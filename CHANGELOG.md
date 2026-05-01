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
- `commit` 命令默认改为“仅提交已暂存内容”，不再自动全量 `git add -A`
- `commit` 命令新增 `--auto-add` 参数：无已暂存内容时可选择自动 `git add -A`
- `commit` 命令新增快速消息路径：小改动默认优先快速生成，复杂变更再调用 `git-commit` skill
- `commit` 命令新增 `--fast-message` 参数：可强制跳过 skill，加快提交速度
- `commit` 命令新增 `-h, --help` 参数：展示命令帮助并立即退出，不执行 Git 操作
- 新增 `commit-help.md`：独立维护 `/commit` 帮助内容
- 新增 `scripts/commit.py`：由 Python 处理参数解析、仓库校验、提交与推送等确定性流程
- `commit` 命令升级为脚本驱动：只有复杂提交信息生成才调用远程模型与 `git-commit` skill
- `commit` 命令新增 `--smart-message` 参数：强制调用模型生成提交信息
