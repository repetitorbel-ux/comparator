# AGENTS.md

## Git Workflow Guardrail (Mandatory)

Source of truth for git process: `docs/GIT_WORKFLOW.md`.

When there is any conflict between instructions, follow `docs/GIT_WORKFLOW.md` for all git operations.

Не нарушай `docs/GIT_WORKFLOW.md`: для задач не работай напрямую в `main`.

### Required Rules

1. Do not develop directly on local `main`.
2. Start each task from updated `main` in a dedicated branch:
   - `feature/...`
   - `fix/...`
   - `docs/...`
3. Do not merge task branches into local `main`.
4. Push task branches to GitHub and merge into `main` on GitHub via PR.
5. After PR merge, sync local `main` from `origin/main`.

### Mandatory Flow

`main sync -> new feature/fix/docs branch -> checks -> push branch -> PR merge on GitHub -> sync main`

### Session Protocol

Before any git action, run a quick preflight:

- `git status --short --branch`
- `git branch --show-current`

Before closing a task, enforce this order:

1. Commit task changes in task branch.
2. Run checks:
   - `python -m pytest tests -q`
   - `ruff check file_compare tests`
3. Push task branch.
4. Create/merge PR to `main` on GitHub.
5. Sync local `main` with `origin/main`.
