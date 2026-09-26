# 资讯

综合热点 + AI/科技 + 文娱 + 体育资讯门户。界面为原生 HTML/CSS/JavaScript；采集与构建仅需 Python 3.11+ 标准库，不需要模型 API 密钥。

## 本地运行

```sh
python -m unittest discover -s tests -v
python scripts/collect_news.py
python scripts/build_news.py
python -m http.server 8080 --directory _site
```

打开 http://localhost:8080 。要在远程服务器预览，优先绑定本机地址并通过 SSH 转发，不要开放开发服务器到公网。

## 内容和界面

- 34 个公开 RSS，详见 `sources.json`。综合来源为中新网、BBC 中文、德国之声中文、法国国际广播电台、香港电台、中央社；科技与 AI 来源为 IT之家、爱范儿、Solidot、GitHub Blog、少数派、极客公园、雷峰网、量子位、Hugging Face、NVIDIA Blog、Google AI、Google DeepMind。文娱频道来源为中新网文娱、中央通訊社·娛樂、Yahoo 娱乐、Variety、Deadline、Google 新闻·中文娱乐、明周娱乐、镜周刊·娱乐、KSD 韩星网、The Hollywood Reporter、Billboard。体育频道来源为中新网体育、中央通訊社·運動、香港电台体育、Yahoo 体育、BBC Sport。
- 支持 RSS 2.0 和 RSS 1.0/RDF。保留来源的原始语言，英文资讯不自动翻译。
- 默认按发布时间倒序，科技和 AI 页签分别展示各自分类，同一条资讯不会同时出现在这两个分类列表中；AI 通过标题关键词和专门来源分类，可能误分类；专门的文娱和体育来源优先归入各自分类。
- 每日速览默认显示北京时间当天的消息，轮流抽取综合/AI/科技/文娱/体育，尽量分散来源，最多 10 条。不是 AI 生成、编辑推荐或热度榜。
- RSS 摘要截取为不超过 90 字符的纯文本，不存储全文、不代理媒体图片。标题和链接保留原始来源。来源可按发布方要求从配置中移除。
- 来源缺少明确带时区的日期、日期过旧/过于超前、无安全 HTTP(S) 链接的条目不发布。
- 收藏将文章快照保存到当前浏览器的 localStorage，不会跨设备同步；浏览器拒绝持久化时会提示。
- 支持分类、来源筛选、关键词搜索、日期筛选、分页加载、深色模式、键盘搜索与 RSS。
- 读取新闻超时放宽到 30 秒，失败自动重试一次；兼容不支持 `AbortSignal.timeout` 的浏览器。请求仍失败时，可显示本浏览器最近一次成功读取的数据，并明确标记缓存状态。浏览器存储不可用时不影响正常在线读取。
- “刷新资讯”通过 Cloudflare Worker 请求抓取和发布，完成后重新读取数据并保留当前筛选。全站共享至少 15 分钟触发间隔，已运行的任务会被复用；接口不可用时仍尝试读取 GitHub Pages 上已发布的数据。

## 安装与离线阅读（PWA）

页脚“安装到桌面”在浏览器允许时唤起原生安装窗口，否则展示对应平台操作。Chrome / Edge 可从地址栏或菜单安装，iPhone / iPad 可通过 Safari 分享菜单添加到主屏幕；支持的 Mac Safari 版本可添加到程序坞。安装需要 HTTPS（本地开发允许 localhost）；安装后的名称为“资讯”，以独立窗口打开。

- `/manifest.webmanifest` 提供名称、图标、启动路径和每日速览/收藏快捷入口。PNG 图标直接由现有 SVG 站点图标导出。
- `/sw.js` 只缓存新闻首页及其静态资源，首次联网加载并完成缓存后才能离线重新打开。文章、搜索和收藏使用本浏览器已保存的数据；不缓存或代理原文网站。
- 新闻 JSON 与刷新 API 不进入 Service Worker 缓存，联网时始终请求当前发布版本。请求失败才显示明确标记的上次数据；离线时不触发抓取，恢复联网会重新读取资讯。
- 首页使用有超时的网络优先策略，失败时返回与已缓存脚本配套的首页。安装阶段验证资源与 HTML 属于同一版本；不会将不存在的页面替换成新闻首页。
- 程序版本由 HTML、静态资源和 Service Worker 内容计算。只更新新闻不会更换程序缓存；程序改动安装完成后显示“更新页面”，用户点击后切换并清理本站旧缓存，保留收藏和其他应用缓存。
- 离线数据保存在本机，清除浏览器存储或浏览器回收空间后可能丢失；新闻更新和原文链接需要联网。PWA 本身不需要常驻服务器，也没有额外的后台抓取任务。

完成本地构建后，可用独立安装的 Playwright 运行完整安装/离线/更新检查：

```sh
PLAYWRIGHT_MODULE=/path/to/playwright NEWS_TEST_SITE=_site node tests/pwa-browser.cjs
```

## 自动发布

`.github/workflows/news.yml` 在 `hexo` 分支相关文件更新、手动执行以及每小时第 17 分钟运行。GitHub Pages 发布方式使用 GitHub Actions。

构建从空目录生成资讯站，只发布资讯页面、数据、RSS、站点地图和 PWA 资源。博客归档、历史文章和旧博客资源已下线，不再拉取旧博客快照；历史源码仍可从 Git 仓库中查阅。

采集时读取上次发布的 `/data/news.json`，合并去重，保留最近 30 天、最多 6000 条，历史随运行积累。单来源失败时保留其历史并显示不可用状态；所有来源失败则终止部署，线上保留上一个成功版本。页面分别显示最近检查时间和最新文章发布时间，超过两小时未检查会显示延迟提示。

GitHub 的计划任务不是严格实时调度，可能延迟或被跳过；公共仓库长期无活动时计划任务可能被禁用。可在 Actions 页面手动运行或重新启用。Cloudflare 每半小时检查一次停更并按条件补跑，配置见 [`ops/cloudflare/README.md`](../ops/cloudflare/README.md)；仍依赖 GitHub API 和执行队列可用，不保证严格准点。

每轮抓取的 Actions 日志包含逐来源 `SOURCE_METRIC`，记录检查时间、状态、有效条目数、新收录条目数及耗时；同样的数据写入 `news.json` 的来源状态。`newCount` 是相对于上次归档首次收录的条数，不是来源当天发稿总量。观察一周的日志后再决定是否调整各源频率；暂时仍为每小时抓取全部来源。

## 回滚

资讯代码回滚使用 Git revert 后重新运行工作流。仓库现为 `ZrBac/news`，站点为 `https://news.zacai.fun`；不要回滚到依赖已删除的 `master` 分支或旧域名读取归档的配置。

## 维护

- 调整来源：编辑 `news/sources.json`。新增源需检查其使用规则及 RSS 格式。
- 修改页面：`news/index.html`、`news/assets/style.css`、`news/assets/app.js`。
- 修改采集：`scripts/collect_news.py`；修改构建：`scripts/build_news.py`。
- 页面展示“资讯来源”中有每轮来源状态；更详细的错误见 GitHub Actions 日志。
- 不要把 GitHub token、API key 或后台凭据写进静态资源。
- 通过上述 GitHub Actions 工作流发布，不要运行旧 Hexo 的 `hexo deploy`。
