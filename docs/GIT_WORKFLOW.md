# Git Workflow

## Current setup

- Local git repository initialized in `d:\Development\file_compare_codex`
- Default branch: `main`
- Current baseline commit:
  `Initial import: file_compare Total Commander tool`
- Remote repository is not configured yet

## Branch model

Use a simple workflow:

- `main` contains the latest stable local state
- each task is done in a separate short-lived branch

Recommended branch names:

- `feature/ui-compact-layout`
- `feature/tc-hotkey-docs`
- `fix/content-diff-scroll`
- `docs/git-workflow`

## Start a new task

Create a branch from `main`:

```bash
git checkout main
git checkout -b feature/<short-task-name>
```

Example:

```bash
git checkout main
git checkout -b feature/tc-button-polish
```

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

## Before merging back to main

Run the minimum project checks:

```bash
python -m pytest tests -q
ruff check file_compare tests
```

If the task also changes packaging or launcher behavior, optionally rebuild:

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

## Merge completed work

If the branch is ready and `main` has not moved:

```bash
git checkout main
git merge --ff-only feature/<short-task-name>
```

If `main` has moved and fast-forward is not possible:

```bash
git checkout main
git merge --no-ff feature/<short-task-name>
```

After merge:

```bash
git branch -d feature/<short-task-name>
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

## Suggested next step for remote setup

When you decide to publish the repo later:

1. Create an empty repository in GitHub or GitLab.
2. Add remote:
   `git remote add origin <repo-url>`
3. Push `main` first:
   `git push -u origin main`

Until then, keep the repo local and continue using the branch workflow above.
