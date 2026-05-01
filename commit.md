---
name: commit
description: >
  使用 Python 脚本处理确定性 Git 提交流程，必要时再调用 git-commit skill
  生成复杂提交信息。
metadata:
  version: "2.0"
  category: command
  domain: git
  workflow: commit-and-push
  author: Space.Yuan
  license: MIT
  tags:
    - git
    - commit
    - push
    - python
    - multi-remote
    - repo-path
    - conventional-commits
    - chinese-summary
---

# Commit Command

用 Python 脚本执行确定性流程，减少无用模型调用。

## 执行入口

将用户传入的参数原样传给脚本：

```txt
python3 /Users/apple/.config/opencode/commands/scripts/commit.py <args>
```

## 快速帮助

如果用户传入 `-h` 或 `--help`，只运行：

```txt
python3 /Users/apple/.config/opencode/commands/scripts/commit.py --help
```

脚本会直接读取 `@commands/commit-help.md` 并输出，不执行任何 Git 操作。

## 脚本职责

`scripts/commit.py` 负责以下确定性操作：

- 解析参数：`-p`、`--all-remotes`、`-r`、`--repo`、`--auto-add`、`--fast-message`、`--smart-message`、`-h`
- 解析并校验仓库目录
- 检查 `git status --short`
- 检查 `git diff` 与 `git diff --cached`
- 判断是否存在已暂存内容
- 必要时执行 `git add -A`（仅在传入 `--auto-add` 时）
- 校验远程仓库
- 执行 `git commit`
- 按顺序执行一个或多个 `git push`
- 输出中文摘要

## 模型职责

只有当脚本输出 `NEED_SMART_MESSAGE` 时，才调用 `@skills/git-commit/SKILL.md` 生成提交信息。

处理方式：

1. 读取脚本输出中的已暂存文件、diff 统计和 diff 内容
2. 调用 `@skills/git-commit/SKILL.md`
3. 生成 `type(scope): 中文摘要` 格式的提交信息
4. 重新运行同一个脚本，并追加 `--message "<commit message>"`

示例：

```txt
python3 /Users/apple/.config/opencode/commands/scripts/commit.py -p origin ./commands --message "feat(commit): 支持脚本化提交流程"
```

## 参数

- `-p, --push-remotes <list>`：指定推送远程，逗号分隔，默认 `origin`
- `--all-remotes`：推送到当前仓库全部远程（高风险）
- `-r, --repo <path>`：指定仓库目录
- `<repoPath>`：位置参数，作为仓库目录
- `--auto-add`：无已暂存内容时自动 `git add -A`
- `--fast-message`：强制使用本地快速消息生成路径
- `--smart-message`：强制请求模型生成提交信息
- `-h, --help`：显示帮助并退出

## 示例

- `/commit` -> 当前目录，默认推送 `origin`
- `/commit -h` -> 直接输出 `commit-help.md`
- `/commit ./skills` -> 指定目录，默认推送 `origin`
- `/commit --auto-add ./skills` -> 指定目录且无已暂存内容时自动暂存再提交
- `/commit --fast-message ./skills` -> 强制走本地快速消息路径
- `/commit --smart-message ./skills` -> 强制由模型生成提交信息
- `/commit -p origin,upstream ../skills` -> 指定目录并依次推送多个远程
- `/commit -r ../skills -p upstream` -> 显式参数方式
- `/commit --all-remotes ../skills` -> 指定目录并推送全部远程
