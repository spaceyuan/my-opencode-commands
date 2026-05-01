# Commands 索引

本目录用于存放 OpenCode 自定义 commands。

## 当前可用

- `commit` - 分析变更并执行提交与推送（英文规范 + 中文提交内容）

## 使用说明

- 每个 command 一个 Markdown 文件
- 文件头部采用统一元数据格式：`name`、`description`、`metadata`
- 可在 command 中引用 skill（如 `@skills/git-commit/SKILL.md`）

## 目录结构

- `commands/commit.md`
- `commands/commit-help.md`
- `commands/scripts/commit.py`

## 使用示例

### commit

用法：

```txt
/commit
/commit --help
/commit ./skills
/commit --auto-add ./skills
/commit --fast-message ./skills
/commit --smart-message ./skills
/commit -p origin,upstream ../skills
/commit -r ../skills -p upstream
/commit --all-remotes ../skills
```

示例说明：

- `/commit`：使用当前目录，默认推送 `origin`
- `/commit --help`：展示命令帮助，不执行任何 Git 操作
- `/commit ./skills`：指定目录，默认推送 `origin`
- `/commit --auto-add ./skills`：指定目录；若无已暂存内容则自动 `git add -A`
- `/commit --fast-message ./skills`：强制使用快速消息生成路径，不调用 skill
- `/commit --smart-message ./skills`：强制调用 `git-commit` skill 生成提交信息
- `/commit -p origin,upstream ../skills`：指定目录并按顺序推送多个远程
- `/commit -r ../skills -p upstream`：显式参数方式，指定目录并推送单远程
- `/commit --all-remotes ../skills`：指定目录并推送当前仓库全部远程（高风险，谨慎使用）

作用：

- 运行 `git status --short`、`git diff`、`git diff --cached`
- 默认仅提交已暂存内容（推荐先手动 `git add` 选择文件）
- 传入 `--auto-add` 时，无已暂存内容会自动执行 `git add -A`
- Python 脚本负责参数解析、仓库校验、暂存检查、提交、推送和中文摘要
- 小改动默认优先走本地快速消息生成；复杂变更才调用 `@skills/git-commit/SKILL.md`
- 传入 `--fast-message` 时，强制使用本地快速消息生成路径
- 传入 `--smart-message` 时，强制调用模型与 `git-commit` skill 生成提交信息
- 执行 `git commit`，随后执行 `git push`
- 无 upstream 时自动 `git push --set-upstream <remote> HEAD`
- 支持指定仓库目录：`/commit <repoPath>` 或 `-r, --repo <path>`
- 支持指定远程：`-p, --push-remotes <list>` 或 `--all-remotes`
- 支持帮助参数：`-h, --help`
- 输出中文摘要（仓库目录、分支、文件、提交信息、hash、远程与 push 状态）

帮助输出：

```txt
/commit --help
/commit -h
```

用于查看命令用途、参数说明、仓库目录规则、远程推送规则与示例。

实现方式：

- `/commit` 入口调用 `commands/scripts/commit.py`
- `/commit -h` 与 `/commit --help` 直接读取 `commands/commit-help.md`
- 只有复杂提交信息生成才调用远程模型与 `git-commit` skill
# test speed
