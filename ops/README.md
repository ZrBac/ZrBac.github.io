# 新闻更新补跑检查

2026-09-24 已切换到 [Cloudflare Workers](cloudflare/README.md)。本页的服务器 timer/API 已停用；以下安装说明保留用于回退。旧 API 地址通过 nginx 转发到 Worker，新页面直接调用云函数。

当前仓库为 `ZrBac/news`，补跑脚本直接使用该名称。

服务器上的 systemd timer 在每小时第 07、37 分钟检查 `https://news.zacai.fun/data/news.json`。保留 GitHub 原有每小时第 17 分钟的计划任务。

补跑条件：

- 已发布的 `updatedAt` 距今超过 2 小时。
- 没有正在排队、运行或等待的 `news.yml` 任务。
- 最近 2 小时没有该工作流的新运行，也没有本机补跑尝试。
- 同一个停更期间，滚动 24 小时内最多尝试 3 次。新的发布时间会重置此预算；失败和请求超时也消耗预算。

网页请求失败、数据格式异常或 GitHub API 查询失败时，记录错误并退出，下一次定时检查再试，不盲目补发任务。本机文件锁防止并发检查，状态先落盘再请求 GitHub，避免请求超时导致连续补发。已有 GitHub workflow concurrency 配置保证发布任务串行。

## 安装和凭据

本部署使用服务器现有 root 用户的 `gh` 登录配置，只在服务器本地读取；不把凭据复制进仓库、静态网站或 systemd unit。需要该账号具有此仓库 Actions workflow dispatch 权限。撤销登录或凭据过期后，补跑会失败并记录日志。

在仓库根目录执行（需要 systemd 和管理员权限）：

```sh
install -d -m 0755 /opt/zrbac-news-watchdog
install -m 0755 scripts/check_news_update.py /opt/zrbac-news-watchdog/check_news_update.py
install -m 0644 ops/zrbac-news-watchdog.service /etc/systemd/system/
install -m 0644 ops/zrbac-news-watchdog.timer /etc/systemd/system/
systemd-analyze verify /etc/systemd/system/zrbac-news-watchdog.service /etc/systemd/system/zrbac-news-watchdog.timer
systemctl daemon-reload
systemctl enable --now zrbac-news-watchdog.timer
systemctl start zrbac-news-watchdog.service
```

代码更新后需要重新安装脚本；GitHub Pages 发布不会修改服务器上的副本。

## 检查与停用

```sh
systemctl list-timers zrbac-news-watchdog.timer
journalctl -u zrbac-news-watchdog.service --since '7 days ago' --no-pager
python3 /opt/zrbac-news-watchdog/check_news_update.py --dry-run
systemctl disable --now zrbac-news-watchdog.timer
```

`--dry-run` 只检查和报告，不触发 GitHub，也不修改补跑预算。状态存储在 `/var/lib/zrbac-news-watchdog/state.json`。日志由 systemd journal 管理；`retry_limit` 表示停更仍未恢复、需要排查；`check_failed` 表示网页、凭据、API 或本地状态检查异常。这里没有配置邮件或消息通知。

服务器重启后 timer 自动启动，`Persistent=true` 会补做一次错过的检查。若服务器离线或 GitHub API/执行队列不可用，这套补跑检查也不能保证每小时更新。

## 网页上的手动刷新

`scripts/news_refresh_api.py` 提供一个固定用途的公开接口，只能触发 `ZrBac/news` 的 `news.yml` / `hexo`，不接受仓库名、分支名或命令参数。它通过 `https://zacai.fun/api/news-refresh` 提供服务，监听本机 `127.0.0.1:8001`，由 nginx 转发。网站仍由 GitHub Pages 托管；浏览和读取已发布的新闻不依赖该接口。

- POST `/api/news-refresh`：需要网站 Origin 和 `X-News-Refresh: 1` 请求头，无需登录，不使用旅行网站会话。
- GET `/api/news-refresh/status`：查看共享任务状态，GitHub 查询结果缓存 10 秒。
- 全站共享至少 15 分钟触发间隔，预算先落盘后触发，请求失败也计入间隔。已有任务直接复用；与自动补跑共享文件锁。
- Origin 检查用于避免浏览器跨站误触发，不作为身份认证。公开接口的资源限制依靠固定任务、全站冷却、nginx 每 IP 限流及进程资源限制。
- GitHub 凭据仍只读取服务器本地 root 的 `gh` 配置，不出现在静态网页和接口响应中。

安装：

```sh
install -d -m 0755 /opt/zrbac-news-refresh
install -m 0755 scripts/news_refresh_api.py scripts/check_news_update.py /opt/zrbac-news-refresh/
install -m 0644 ops/zrbac-news-refresh.service /etc/systemd/system/
install -m 0644 ops/news-refresh-limit.conf /etc/nginx/conf.d/news-refresh-limit.conf
install -m 0644 ops/news-refresh-location.conf /etc/nginx/news-refresh-location.conf
# 在 /etc/nginx/conf.d/zacai.fun.conf 的 HTTPS server 块内添加：
# include /etc/nginx/news-refresh-location.conf;
systemctl daemon-reload
systemctl enable --now zrbac-news-refresh.service
nginx -t
systemctl reload nginx
```

状态文件位于 `/var/lib/zrbac-news-refresh/request.json`。用 `journalctl -u zrbac-news-refresh.service` 排查接口错误。代码更新后须重新安装两个 Python 文件并重启服务。停用时移除 nginx 的 include，验证并 reload nginx，然后 `systemctl disable --now zrbac-news-refresh.service`；已发布网站仍可访问。
