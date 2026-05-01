# /commit 帮助

## 用法

```txt
/commit [options] [repoPath]
```

## 参数

- `-p, --push-remotes <list>`：指定推送远程，逗号分隔，默认 `origin`
- `--all-remotes`：推送到当前仓库全部远程（高风险）
- `-r, --repo <path>`：指定仓库目录
- `--auto-add`：无已暂存内容时自动 `git add -A`
- `--fast-message`：强制使用本地快速消息生成路径
- `--smart-message`：强制交给模型按 `git-commit` skill 生成提交信息
- `-h, --help`：显示帮助并退出

## 示例

```txt
/commit
/commit ./skills
/commit --auto-add ./skills
/commit --fast-message ./skills
/commit --smart-message ./skills
/commit -p origin,upstream ../skills
/commit -r ../skills -p upstream
/commit --all-remotes ../skills
```

## 默认行为

- 默认使用当前目录，默认推送 `origin`
- 默认只提交已暂存内容，推荐先手动 `git add`
- 少量集中变更优先本地快速生成提交信息
- 复杂变更会请求模型按 `git-commit` skill 生成提交信息
- 不执行强制推送
