# Git Workflow

## Current setup

- Local repository: `d:\Development\file_compare_codex`
- Main integration branch: `main`
- GitHub remote is the source of truth for `main`
- Task work happens in short-lived branches

## Working model

Use this workflow consistently:

- every new task starts in a new branch
- do not develop directly in local `main`
- do not merge task branches into local `main`
- push task branches to GitHub
- merge into `main` on GitHub via pull request or web merge
- after GitHub merge, sync local `main` from `origin/main`

In practice:

- local `main` is a sync branch
- feature work lives only in `feature/...`, `fix/...`, or `docs/...`
- GitHub `main` is the canonical stable history
- one task equals one dedicated branch with a meaningful name

## Branch naming

Recommended branch names:

- `feature/ui-compact-layout`
- `feature/tc-hotkey-docs`
- `fix/content-diff-scroll`
- `docs/git-workflow`

## Start a new task

Before starting a new task, make sure local `main` is up to date:

```bash
git checkout main
git pull origin main
git checkout -b feature/<short-task-name>
```

Example:

```bash
git checkout main
git pull origin main
git checkout -b feature/tc-button-polish
```

Important rules:

- every new task must start from a new branch
- do not reuse an old task branch for unrelated work
- do not create placeholder branches such as `feature/next-task`
- start a new branch only from updated `main`
- keep the working tree clean before switching branches
- if local `main` has accidental commits, do not continue from it until the situation is resolved

## Daily work

Make small logical commits instead of one large commit.

Useful commands:

```bash
git status
git add <file>
git commit -m "Short clear message"
```

Good commit message examples:

- `Add side-by-side content diff viewer`
- `Tighten compare window layout`
- `Update Total Commander setup docs`

## Before pushing a task branch

Run the minimum project checks:

```bash
python -m pytest tests -q
ruff check file_compare tests
```

If the task also changes packaging or launcher behavior, optionally rebuild:

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

## Publish the branch to GitHub

Push the task branch and set upstream:

```bash
git push -u origin feature/<short-task-name>
```

Example:

```bash
git push -u origin feature/tc-button-polish
```

After push:

- open the branch on GitHub
- create a pull request into `main`
- merge on GitHub, not locally

## After GitHub merge

Once the branch is merged on GitHub:

```bash
git checkout main
git pull origin main
git branch -d feature/<short-task-name>
```

Optional cleanup of the remote branch:

```bash
git push origin --delete feature/<short-task-name>
```

## Rules for `main`

- do not commit directly to `main`
- do not merge task branches into local `main`
- use local `main` only to sync from GitHub and create new task branches

If you need to inspect current stable state locally:

```bash
git checkout main
git pull origin main
```

## What should not be committed

Do not commit generated or local-only files:

- `build/`
- `build_alt*/`
- `dist/`
- `dist_alt*/`
- `.pytest_cache/`
- `.pytest_tmp/`
- `.ruff_cache/`
- `testdata_tmp/`
- `.tmp_testdata/`
- `.agent/`
- `.gemini/`

These are already covered by [`.gitignore`](/d:/Development/file_compare_codex/.gitignore).

## Minimal happy path

Typical task flow:

```bash
git checkout main
git pull origin main
git checkout -b feature/<task>
git status
git add <files>
git commit -m "Short clear message"
python -m pytest tests -q
ruff check file_compare tests
git push -u origin feature/<task>
```

Then:

1. Create PR on GitHub.
2. Merge into `main` on GitHub.
3. Sync local `main`.
4. Delete the finished branch.
