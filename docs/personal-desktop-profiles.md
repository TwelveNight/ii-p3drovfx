# 本机会话配置选择

Hyprland + II 的配置实体位于 `~/.config/desktop-profiles/hyprland-ii/hypr`。
普通和 UWSM 登录项先调用 desktop-profile，再启动原 compositor 入口。
源码安装器与已安装的 ii-p3drovfx CLI 在写文件前验证 hypr 链接归属。
备份与安装先解析已经验证的配置入口，确保 find 能枚举真实目录内容。
现有 Quickshell、设置和个人键位继续使用各自的路径。

完整维护及回退方式见 `~/.local/lib/desktop-profiles/README.md`。

旧 setup 的首次安装备份也保存 hypr 配置实体，不再只保存活动链接。
现代 CLI 与旧入口都在写入前检查 hyprland-ii 的归属；更新时保留
custom/ 个人目录，Niri 的两个 profile 和共享远程桌面控制器不参与同步。
隔离回归使用 `python3 scripts/test-desktop-profiles.py`。

## 上游与 live 更新

普通 `ii-p3drovfx update` 进入 `desktop-update update hyprland-ii`，
使用 registry 指定的个人源码与 origin/dev，不猜测 origin/night/personal-overlay。
`desktop-update sync all` 先合并并验证三套源码，不更新 live；
`desktop-update deploy all` 再验证、备份、部署。个人提交不 rebase/reset/push。
显式 --local 仍只部署本地源码。完整流程见 iNiR 的
scripts/personal/DESKTOP-UPDATES.md。
维护时只安装配色服务定义，由登录会话负责激活，避免干扰其它桌面。
