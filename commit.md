---
name: commit
description: >
  分析当前分支变更，按 Conventional Commits 英文规范生成中文提交信息，
  执行 git commit 与 git push，并输出中文摘要。
metadata:
  version: "1.3"
  category: command
  domain: git
  workflow: commit-and-push
  author: Space.Yuan
  license: MIT
  tags:
    - git
    - commit
    - push
    - multi-remote
    - repo-path
    - conventional-commits
    - chinese-summary
---

分析当前仓库中的所有 Git 变更，并按以下流程执行提交：

参数约定：

- `-p, --push-remotes <list>`（可选）：指定推送远程，逗号分隔（如 `origin,upstream`）
- `--all-remotes`（可选）：推送到当前仓库全部远程（高风险，必须显式传入）
- `-r, --repo <path>`（可选）：指定仓库目录
- `<repoPath>`（可选）：位置参数，作为仓库目录（如 `./skills`、`../skills`）
- `--auto-add`（可选）：当无已暂存内容时自动执行 `git add -A`

仓库目录选择优先级：

1. `-r, --repo <path>`
2. `<repoPath>` 位置参数
3. 当前目录

远程选择优先级：

1. `--all-remotes`
2. `-p, --push-remotes <list>`
3. 默认 `origin`

1. 按“仓库目录选择优先级”解析目标仓库，并校验为 Git 仓库
2. 运行 `git status --short` 查看所有变更文件
3. 运行 `git diff` 和 `git diff --cached` 理解实际改动内容
4. 检查是否存在已暂存内容：
   - 默认仅提交已暂存内容（推荐手动 `git add` 精准控制）
   - 如果无已暂存内容且传入 `--auto-add`，运行 `git add -A` 暂存全部改动
   - 如果无已暂存内容且未传入 `--auto-add`，提示“请先手动 git add 或使用 --auto-add”并结束
5. 先调用 `@skills/git-commit/SKILL.md`，并按该 skill 生成提交信息：
   - 使用 Conventional Commits 英文规范：`<type>(<scope>): <subject>`
   - `type` / `scope` 保持英文（如 `feat`, `fix`, `auth`, `invoices`）
   - `subject` 使用中文，整体格式为：`type(scope): 中文摘要` 或 `type: 中文摘要`
   - 如存在多个重要变更，可补充中文项目符号正文（建议不超过 5 条）
6. 使用 `git commit` 执行提交
7. 根据“远程选择优先级”解析目标远程列表，并去重后按顺序逐个推送：
   - 先校验远程是否存在：`git remote get-url <remote>`
   - 远程不存在：标记该远程失败并继续处理下一个远程
   - 远程存在：执行 `git push <remote> HEAD`
   - 若因没有 upstream 失败，执行 `git push --set-upstream <remote> HEAD`
   - 若仍失败或因其他原因失败（如远端分支已分叉），清晰报告错误且不要强制推送
8. 用中文输出结果摘要：仓库目录、分支名、已提交文件、提交信息、commit hash、远程列表与各远程 push 状态

参数冲突处理：

- `--all-remotes` 与 `-p, --push-remotes` 互斥，同时传入时直接报错并结束

边界处理：

- 如果没有任何变更，直接告知并结束
- 如果存在变更但没有已暂存内容，且未传入 `--auto-add`，直接告知并结束
- 如果存在 merge conflict，提示风险并中止提交
- 如果目标远程全部推送失败，命令整体返回失败状态

示例：

- `/commit` -> 当前目录，默认推送 `origin`
- `/commit ./skills` -> 指定目录，默认推送 `origin`
- `/commit --auto-add ./skills` -> 指定目录且无已暂存内容时自动暂存再提交
- `/commit -p origin,upstream ../skills` -> 指定目录并依次推送多个远程
- `/commit -r ../skills -p upstream` -> 显式参数方式
- `/commit --all-remotes ../skills` -> 指定目录并推送全部远程
