---
description: git-flow
---

# Git Flow Workflow

This workflow automates the common git operations: pulling updates, checking status, and committing changes.

## When to use this workflow

- When the user types `/git-sync` or `/commit`.
- Before starting work (pull).
- After completing a task (commit).

## Task

1. Pull latest changes from the repository.

   ```bash
   git pull --rebase
   ```

2. Show current git status.

   ```bash
   git status
   ```

3. Ask the user for a commit message or suggest one based on `git diff`.

4. Add all changes and commit.

   ```bash
   git add .
   git commit -m "[message]"
   ```

## Constraints

- Use **Conventional Commits** (feat:, fix:, chore:, docs:) as required by `WORKFLOW.md`.
- Never force push.
- If conflicts occur during pull, stop and notify the user.
