# 资讯刷新云函数

把手动刷新接口和停更补跑迁到 Cloudflare Workers，抓取与发布仍由 `ZrBac/news` 的 `news.yml` / `hexo` 执行。网页和新闻数据仍由 GitHub Pages 提供。

## 当前状态

代码和测试已准备好。默认两个开关均关闭，网页仍使用原服务器接口；部署 Worker 本身不会切换生产网站。只有完成下面的验证和切换后，才可停用原服务。

## 行为

- POST `/api/news-refresh` 和 GET `/api/news-refresh/status` 与原接口兼容，固定仓库、工作流、分支，不接受任意任务参数。
- 只允许资讯站 Origin；Origin 不是登录认证。每 IP 每分钟最多 60 次请求，真正限制工作流触发次数的是全站持久化冷却。
- SQLite Durable Object 的单个 `news` 实例协调所有手动和自动请求；手动至少间隔 15 分钟，已有任务直接复用。
- Cron 每小时第 07、37 分钟检查 `data/status.json`。停更超过两小时且没有近期/正在运行的任务时补跑；同一次停更滚动 24 小时最多三次，两次至少间隔两小时。
- 预算先持久化再调用 GitHub，超时和失败也消耗预算；新的发布时间重置自动补跑预算，较旧的 CDN 响应不能重置它。
- 查询结果缓存 10 秒；上游异常短暂退避，不盲目补发。GitHub 凭证只存 Worker Secret，不打印上游原始响应或凭证。
- GitHub 自身的每小时计划任务保留。两套调度都不能保证 GitHub 排队和部署准点完成。

## 本地检查

使用 Node.js 22，工具依赖独立于根目录的旧 Hexo：

```sh
cd /root/workspace/zrbac-news/ops/cloudflare
npm ci
npm test
npm run check
```

测试涵盖并发、冷却、重启、失败预算、任务状态、CORS 和请求限制；Miniflare 使用真实 Workers 运行时和 SQLite 存储验证并发及重启持久化，所有 GitHub 请求均为模拟，不会触发线上任务。

## 凭证与首次部署

1. 在可信终端执行 `npx wrangler login`，然后 `npx wrangler whoami` 确认正确账号。远程服务器可使用 SSH 端口转发接收本机浏览器 OAuth 回调，或在本地电脑完成部署。不要把凭证贴进聊天、仓库或网页。
2. 在 GitHub 创建细粒度访问令牌，仅选 `ZrBac/news`，仓库权限 `Actions: Read and write`。设置合适的有效期，并在过期前轮换。
3. 执行 `npm run deploy`，保持 `MANUAL_ENABLED` 和 `WATCHDOG_ENABLED` 为 `false`。首次部署会建立 SQLite Durable Object。
4. 执行 `npx wrangler secret put GITHUB_TOKEN`，在隐藏的输入提示中填入专用令牌。
5. 从部署输出取得真实的 `*.workers.dev` 地址。如果使用 `news-api.zacai.fun`，先确认 Cloudflare 上该域名区域已激活，再添加 Worker 自定义域名；不要修改资讯主站或旅行网站的 DNS 记录。

不要将服务器 `gh` 的广泛权限凭证直接复制到云函数。仓库不保存 account ID、令牌或未经验证的生产接口地址。

## 验证与切换顺序

1. 先发布本站的构建改动，确认 `https://news.zacai.fun/data/status.json` 返回有效 `updatedAt`，且与 `data/news.json` 一致。
2. 用部署得到的真实域名替换以下 `WORKER_HOST`，测试状态接口：

   ```sh
   curl --fail -H 'Origin: https://news.zacai.fun' \
     'https://WORKER_HOST/api/news-refresh/status'
   ```

   应返回 `idle`、`running`、`ready` 或 `failed` 等正常状态，不应返回 503。验证手机和常用网络都能连通该接口。
3. 记录旧服务状态和旧的 GitHub 仓库变量；停止旧 timer，等待其当前检查结束，再停止旧的刷新 API。确认 GitHub 没有正在执行的新闻工作流，且最近一次本机刷新/补跑尝试已过去两小时（包括失败尝试），避免迁移时清空旧预算导致重复触发。

   ```sh
   systemctl disable --now zrbac-news-watchdog.timer
   systemctl is-active zrbac-news-watchdog.service
   systemctl disable --now zrbac-news-refresh.service
   ```

4. 将 `wrangler.jsonc` 的 `MANUAL_ENABLED` 改成 `true`，暂时保持 `WATCHDOG_ENABLED` 为 `false`，重新部署。测试真实 POST → 工作流 → 发布 → 页面新时间。若返回 `fresh` / `cooldown`，等冷却结束后再验证实际触发。
5. 验证成功后，把 `WATCHDOG_ENABLED` 改为 `true`，部署并观察下一次 cron 日志；应有 `watchdog` 事件，不能有持续 503。提交这两个开关的实际状态，避免日后重新部署关闭功能。
6. 设置仓库变量为真实接口地址，再触发 Pages 发布：

   ```sh
   gh variable set NEWS_REFRESH_ENDPOINT --repo ZrBac/news \
     --body 'https://WORKER_HOST/api/news-refresh'
   gh workflow run news.yml --repo ZrBac/news --ref hexo
   ```

7. 等 Pages 部署成功，检查 HTML 的 `news-refresh-endpoint`，在浏览器验证刷新完成、连续点击冷却、接口故障时仍能读取已发布资讯。切换期间和已经打开的旧页面可能需要重新加载才能使用新接口。

只有全部通过才算迁移完成。旧脚本、状态和 nginx 配置保留用于回退；不要停止旅行网站或关闭整台服务器。

## 回退与维护

- 先关闭 Worker 两个开关并重新部署，确认没有在途触发，再恢复原服务器 timer/API，避免双系统同时补跑。
- 删除 `NEWS_REFRESH_ENDPOINT` 仓库变量（或恢复之前的值），重新运行 `news.yml` 发布。未设置变量时构建默认使用原服务器地址。
- `npx wrangler tail` 可检查日志；监控 GitHub 令牌到期、Worker 请求/CPU/存储额度。凭证失效会返回 503，但已发布新闻仍可阅读。
- Worker 代码改动由 `news-worker-check.yml` 自动测试；云端部署使用 `npm run deploy`，不会随着 Pages 构建自动上传。
- 不要删除 Durable Object 命名空间或改动 `idFromName('news')`，否则会丢失冷却和重试预算。
