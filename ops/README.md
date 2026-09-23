# 新闻更新补跑检查

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
