# 更新记录

## 2026-04-28

- 新增 `commands/README.md`
- 新增 `commands/CHANGELOG.md`
- 更新 `commit` 命令流程，接入 `@skills/git-commit/SKILL.md`
- 统一 `commit` 命令为“英文规范 + 中文内容”提交规则（`type/scope` 英文，摘要与 body 中文）
- 更新 `commit` 命令输出为中文摘要（分支、文件、提交信息、hash、push 状态）
- `commit` 命令新增远程参数：默认 `origin`，支持指定单远程、多远程与 `--all-remotes`
- `commit` 命令推送流程升级为逐远程校验与逐远程推送，并汇总各远程状态
- `commit` 命令新增仓库路径参数：支持 `/commit ./skills` 与 `-r, --repo <path>`
- `commit` 命令新增 `-p, --push-remotes <list>` 参数，支持与仓库路径组合使用
- `commit` 命令增加参数优先级、参数冲突处理（`--all-remotes` 与 `-p` 互斥）
