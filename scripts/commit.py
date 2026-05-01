#!/usr/bin/env python3
"""Deterministic executor for the OpenCode /commit command."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


COMMANDS_DIR = Path(__file__).resolve().parents[1]
HELP_FILE = COMMANDS_DIR / "commit-help.md"


def run_git(repo: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def print_help() -> int:
    if HELP_FILE.exists():
        print(HELP_FILE.read_text(encoding="utf-8"))
        return 0
    print("未找到帮助文件：commit-help.md")
    return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("repo_path", nargs="?")
    parser.add_argument("-p", "--push-remotes")
    parser.add_argument("--all-remotes", action="store_true")
    parser.add_argument("-r", "--repo")
    parser.add_argument("--auto-add", action="store_true")
    parser.add_argument("--fast-message", action="store_true")
    parser.add_argument("--smart-message", action="store_true")
    parser.add_argument("--message")
    parser.add_argument("--message-file")
    parser.add_argument("-h", "--help", action="store_true")
    return parser.parse_args(argv)


def resolve_repo(args: argparse.Namespace) -> Path | None:
    raw_path = args.repo or args.repo_path or "."
    repo = Path(raw_path).expanduser()
    if not repo.is_absolute():
        repo = (Path.cwd() / repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"仓库目录不存在或不是目录：{repo}")
        return None

    inside = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        print(f"目标目录不是 Git 仓库：{repo}")
        return None

    top = run_git(repo, ["rev-parse", "--show-toplevel"])
    if top.returncode == 0 and top.stdout.strip():
        return Path(top.stdout.strip())
    return repo


def split_remotes(value: str | None) -> list[str]:
    if not value:
        return []
    result: list[str] = []
    for item in value.split(","):
        name = item.strip()
        if name and name not in result:
            result.append(name)
    return result


def resolve_remotes(repo: Path, args: argparse.Namespace) -> tuple[list[str], bool]:
    if args.all_remotes and args.push_remotes:
        print("参数冲突：`--all-remotes` 与 `-p, --push-remotes` 不能同时使用")
        return [], False

    if args.all_remotes:
        remotes = run_git(repo, ["remote"])
        names = [line.strip() for line in remotes.stdout.splitlines() if line.strip()]
        if not names:
            print("当前仓库没有配置任何远程仓库")
            return [], False
        return names, True

    names = split_remotes(args.push_remotes) or ["origin"]
    return names, True


def has_conflicts(repo: Path) -> bool:
    result = run_git(repo, ["diff", "--name-only", "--diff-filter=U"])
    return bool(result.stdout.strip())


def staged_files(repo: Path) -> list[str]:
    result = run_git(repo, ["diff", "--cached", "--name-only"])
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def status_short(repo: Path) -> str:
    return run_git(repo, ["status", "--short"]).stdout


def branch_name(repo: Path) -> str:
    branch = run_git(repo, ["symbolic-ref", "--short", "HEAD"])
    if branch.returncode == 0 and branch.stdout.strip():
        return branch.stdout.strip()
    fallback = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    return fallback.stdout.strip() or "HEAD"


def can_fast_message(files: list[str], diff_text: str) -> bool:
    if len(files) > 5:
        return False
    scopes = {guess_scope(path) for path in files}
    return len(scopes) <= 1 and len(diff_text) < 12000


def guess_scope(path: str) -> str:
    parts = Path(path).parts
    if not parts:
        return "repo"
    if parts[0] in {"README.md", "CHANGELOG.md", "commit.md", "commit-help.md"}:
        return "commit"
    if parts[0] == "scripts":
        return "commit"
    return parts[0].replace("_", "-")


def guess_type(files: list[str], diff_text: str) -> str:
    lowered = diff_text.lower()
    if "fix" in lowered or "修复" in diff_text:
        return "fix"
    if any(Path(path).name in {"commit.md", "commit-help.md"} or path.startswith("scripts/") for path in files):
        return "feat"
    if any(path.endswith((".md", ".mdx")) for path in files) and all(
        path.endswith((".md", ".mdx")) for path in files
    ):
        return "docs"
    if any("test" in path.lower() for path in files):
        return "test"
    if any(Path(path).name in {"package.json", "package-lock.json", "pnpm-lock.yaml", "Dockerfile"} for path in files):
        return "chore"
    return "feat"


def guess_subject(diff_text: str) -> str:
    if "--help" in diff_text or "commit-help" in diff_text:
        return "支持 help 帮助输出"
    if "fast-message" in diff_text:
        return "支持快速消息生成"
    if "auto-add" in diff_text:
        return "支持可选自动暂存"
    if "push-remotes" in diff_text or "all-remotes" in diff_text:
        return "支持多远程推送"
    if "repoPath" in diff_text or "--repo" in diff_text:
        return "支持指定仓库目录"
    return "更新提交命令流程"


def fast_message(repo: Path, files: list[str]) -> str:
    diff_text = run_git(repo, ["diff", "--cached"]).stdout
    commit_type = guess_type(files, diff_text)
    scope = guess_scope(files[0]) if files else "repo"
    subject = guess_subject(diff_text)
    return f"{commit_type}({scope}): {subject}"


def message_from_args(args: argparse.Namespace) -> str | None:
    if args.message_file:
        return Path(args.message_file).read_text(encoding="utf-8").strip()
    if args.message:
        return args.message.strip()
    return None


def print_smart_message_context(repo: Path, files: list[str]) -> int:
    diff_stat = run_git(repo, ["diff", "--cached", "--stat"]).stdout.strip()
    diff_text = run_git(repo, ["diff", "--cached"]).stdout.strip()
    print("NEED_SMART_MESSAGE")
    print("需要模型按 @skills/git-commit/SKILL.md 生成提交信息，然后重新调用脚本并传入 `--message`。")
    print("\n已暂存文件：")
    for path in files:
        print(f"- {path}")
    if diff_stat:
        print("\nDiff 统计：")
        print(diff_stat)
    if diff_text:
        print("\nDiff 内容（截断）：")
        print(diff_text[:12000])
    return 0


def commit(repo: Path, message: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temp:
        temp.write(message.strip() + "\n")
        message_file = temp.name
    result = run_git(repo, ["commit", "-F", message_file])
    Path(message_file).unlink(missing_ok=True)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def push_remotes(repo: Path, remotes: list[str]) -> list[tuple[str, bool, str]]:
    statuses: list[tuple[str, bool, str]] = []
    for remote in remotes:
        remote_url = run_git(repo, ["remote", "get-url", remote])
        if remote_url.returncode != 0:
            statuses.append((remote, False, "远程不存在"))
            continue

        push = run_git(repo, ["push", remote, "HEAD"])
        output = (push.stdout + push.stderr).strip()
        if push.returncode == 0:
            statuses.append((remote, True, "成功"))
            continue

        if "no upstream" in output.lower() or "没有上游" in output:
            upstream = run_git(repo, ["push", "--set-upstream", remote, "HEAD"])
            upstream_output = (upstream.stdout + upstream.stderr).strip()
            statuses.append((remote, upstream.returncode == 0, upstream_output or "已设置 upstream"))
            continue

        statuses.append((remote, False, output or "推送失败"))
    return statuses


def print_summary(repo: Path, branch: str, files: list[str], message: str, push_statuses: list[tuple[str, bool, str]]) -> int:
    short_hash = run_git(repo, ["rev-parse", "--short", "HEAD"]).stdout.strip()
    print(f"✅ 已在仓库: `{repo}`")
    print(f"✅ 已在分支: `{branch}`")
    print("\n📁 已提交文件:")
    for path in files:
        print(f"- `{path}`")
    print("\n📝 提交信息:")
    print("```text")
    print(message.strip())
    print("```")
    print(f"\n🔖 Commit: `{short_hash}`")
    print("\n🚀 远程推送状态:")
    for remote, ok, detail in push_statuses:
        mark = "✓" if ok else "✗"
        print(f"- `{remote}`：{mark} {detail}")
    return 0 if any(ok for _, ok, _ in push_statuses) else 3


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.help:
        return print_help()

    repo = resolve_repo(args)
    if repo is None:
        return 2

    remotes, remotes_ok = resolve_remotes(repo, args)
    if not remotes_ok:
        return 2

    if has_conflicts(repo):
        print("存在 merge conflict，请先解决冲突后再提交")
        return 2

    status = status_short(repo)
    if not status.strip():
        print(f"仓库无任何变更：{repo}")
        return 0

    files = staged_files(repo)
    if not files:
        if args.auto_add:
            add = run_git(repo, ["add", "-A"])
            if add.returncode != 0:
                print((add.stdout + add.stderr).strip())
                return add.returncode
            files = staged_files(repo)
        else:
            print("存在变更但没有已暂存内容，请先手动 git add 或使用 --auto-add")
            return 0

    diff_text = run_git(repo, ["diff", "--cached"]).stdout
    message = message_from_args(args)
    if not message:
        if args.fast_message or (not args.smart_message and can_fast_message(files, diff_text)):
            message = fast_message(repo, files)
        else:
            return print_smart_message_context(repo, files)

    branch = branch_name(repo)
    ok, commit_output = commit(repo, message)
    if not ok:
        print(commit_output)
        return 1

    push_statuses = push_remotes(repo, remotes)
    return print_summary(repo, branch, files, message, push_statuses)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
