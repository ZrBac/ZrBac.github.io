# 资讯

综合热点 + AI/科技 + 文娱 + 体育资讯门户。界面为原生 HTML/CSS/JavaScript；采集与构建仅需 Python 3.11+ 标准库，不依赖旧 Hexo 的运行环境，也不需要模型 API 密钥。

## 本地运行

```sh
python -m unittest discover -s tests -v
python scripts/collect_news.py
git fetch origin master
git worktree add --detach ../zrbac-legacy FETCH_HEAD
python scripts/build_news.py --legacy ../zrbac-legacy
python -m http.server 8080 --directory _site
```

打开 http://localhost:8080 。要在远程服务器预览，优先绑定本机地址并通过 SSH 转发，不要开放开发服务器到公网。

## 内容和界面

- 28 个公开 RSS，详见 `sources.json`。综合来源为中新网、BBC 中文、德国之声中文、法国国际广播电台、香港电台、中央社；科技与 AI 来源为 IT之家、爱范儿、Solidot、GitHub Blog、少数派、极客公园、雷峰网、量子位、Hugging Face、NVIDIA Blog、Google AI、Google DeepMind。文娱频道来源为中新网文娱、中央通訊社·娛樂、Yahoo 娱乐、Variety、Deadline。体育频道来源为中新网体育、中央通訊社·運動、香港电台体育、Yahoo 体育、BBC Sport。
- 支持 RSS 2.0 和 RSS 1.0/RDF。保留来源的原始语言，英文资讯不自动翻译。
- 默认按发布时间倒序，科技和 AI 页签分别展示各自分类，同一条资讯不会同时出现在这两个分类列表中；AI 通过标题关键词和专门来源分类，可能误分类；专门的文娱和体育来源优先归入各自分类。
- 每日速览默认显示北京时间当天的消息，轮流抽取综合/AI/科技/文娱/体育，尽量分散来源，最多 10 条。不是 AI 生成、编辑推荐或热度榜。
- RSS 摘要截取为不超过 90 字符的纯文本，不存储全文、不代理媒体图片。标题和链接保留原始来源。来源可按发布方要求从配置中移除。
- 来源缺少明确带时区的日期、日期过旧/过于超前、无安全 HTTP(S) 链接的条目不发布。
- 收藏将文章快照保存到当前浏览器的 localStorage，不会跨设备同步；浏览器拒绝持久化时会提示。
- 支持分类、来源筛选、关键词搜索、日期筛选、分页加载、深色模式、键盘搜索与 RSS。

## 自动发布

`.github/workflows/news.yml` 在 `hexo` 分支相关文件更新、手动执行以及每小时第 17 分钟运行。GitHub Pages 发布方式使用 GitHub Actions。

构建拉取 `master` 分支的原博客成品，将旧首页放到 `/blog/`，保留历史文章、分页、分类、图片等 URL；旧博客的首页链接改为 `/blog/`。`master` 不会被写入。`source` 下的 Hexo Markdown 也不修改。

采集时读取上次发布的 `/data/news.json`，合并去重，保留最近 30 天、最多 6000 条，历史随运行积累。单来源失败时保留其历史并显示不可用状态；所有来源失败则终止部署，线上保留上一个成功版本。页面分别显示最近检查时间和最新文章发布时间，超过两小时未检查会显示延迟提示。

GitHub 的计划任务不是严格实时调度，可能延迟或被跳过；公共仓库长期无活动时计划任务可能被禁用。可在 Actions 页面手动运行或重新启用。服务器补跑检查配置见 [`ops/README.md`](../ops/README.md)，仍依赖服务器在线、GitHub API 和执行队列可用，不保证严格准点。

每轮抓取的 Actions 日志包含逐来源 `SOURCE_METRIC`，记录检查时间、状态、有效条目数、新收录条目数及耗时；同样的数据写入 `news.json` 的来源状态。`newCount` 是相对于上次归档首次收录的条数，不是来源当天发稿总量。观察一周的日志后再决定是否调整各源频率；暂时仍为每小时抓取全部来源。

## 回滚

原 `master` 分支未被修改。紧急恢复原博客：在 Settings → Pages 将 Source 改回 Deploy from a branch，选择 `master`、`/(root)`，并禁用此资讯工作流，防止再次覆盖。资讯代码回滚使用 Git revert 后重新运行工作流。

## 维护

- 调整来源：编辑 `news/sources.json`。新增源需检查其使用规则及 RSS 格式。
- 修改页面：`news/index.html`、`news/assets/style.css`、`news/assets/app.js`。
- 修改采集：`scripts/collect_news.py`；修改构建：`scripts/build_news.py`。
- 页面展示“资讯来源”中有每轮来源状态；更详细的错误见 GitHub Actions 日志。
- 不要把 GitHub token、API key 或后台凭据写进静态资源。
- 不要运行旧 Hexo 的 `hexo deploy` 来发布此门户，它会覆盖旧成品分支。后续如需重新生成博客，先检查归档与主页的兼容性。
