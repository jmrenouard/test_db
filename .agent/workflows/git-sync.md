---
description: Git & Release Flow Workflow
---

# Git & Release Flow Workflow

This unified workflow manages the entire lifecycle of local changes, from synchronization to production release.

## When to use this workflow

- When the user types `/git-sync`, `/commit`, or `/release`.

## Phase 1: Local Sync & Development

1. **Pull & Status**:

   ```bash
   git pull --rebase
   git status
   ```

2. **Commit**:
   - Propose a message (Conventional Commits: `feat:`, `fix:`, ...).

   ```bash
   git add .
   git commit -m "[message]"
   ```

## Phase 2: Decision - Sync vs Release

1. **Choice Required**: Ask the USER if they want to perform a **Simple Push** or a **Full Release**.

### Option A: Simple Push

- Execute push only.

  ```bash
  git push
  ```

### Option B: Full Release

1. **Versioning**:
   - Calculate next version according to `CHANGELOG_MANAGEMENT.md`.
   - Update `Changelog` (date, version, bullet points).

2. **Finalize**:
   Comment for tags MUST contains all information related to this tag
   content must be grabbed from Changelog
   If Changelog is not updated with last information, git log information and produce missing information from git log for this specific release
   information for a specific release should go to <Version inforamtion>

   ```bash
   git add Changelog
   git commit -m "chore: release version X.X.Y"
   git tag -a vX.X.Y -m "Release version X.X.Y + <Version information>"
   git push origin main --tags
   ```

## Constraints

- **NO CHATTER**: Response only contains technical steps.
- **TAGGING**: If a tag exists with the same version, confirm deletion before replacing.
- **LOGS**: Maintain YYYY-MM-DD format in Changelog.
