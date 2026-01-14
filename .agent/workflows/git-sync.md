---
description: git-flow
---

# Git & Release Flow Workflow

This unified workflow manages the entire lifecycle of local changes, from synchronization to production release.

## When to use this workflow

- When the user types `/git-sync`, `/commit`, or `/release`.

## Phase 1: Local Sync & Development

1. **Pull & Status**: Ensure the local environment is up-to-date.

   ```bash
   git pull --rebase
   git status
   ```

2. **Stage & Commit**:
   - Use **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `chore:`).
   - If multiple features are added, list them in the commit body (not just the subject).

   ```bash
   git add .
   git commit -m "[subject]" -m "[bullet point 1]" -m "[bullet point 2]" ...
   ```

## Phase 2: Decision - Sync vs Release

Ask the USER if they want to perform a **Simple Push** or a **Full Release**.

### Option A: Simple Push

Use this for regular development updates without a version bump.

```bash
git push
```

### Option B: Full Release

1. **Versioning & Documentation**:
   - Determine the next version (Semantic Versioning).
   - Update `Changelog`: Add the version, current date (YYYY-MM-DD), and all relevant bullet points.

2. **Release Execution (Commit & Tag)**:
   - **CRITICAL**: Both the commit message and the tag annotation MUST contain the full list of changes (bullet points) for that version.
   - If the `Changelog` is already updated, use that content. Otherwise, derive it from `git log`.
   - The message format for both should be: `vX.X.Y: [Short Summary]\n\n[Bullet Points]`.

   ```bash
   # 1. Commit the version bump
   git add Changelog
   git commit -m "chore: release version X.X.Y" -m "[Change 1]" -m "[Change 2]" ...

   # 2. Handle existing tag (if necessary)
   git tag -d vX.X.Y || true
   git push origin :refs/tags/vX.X.Y || true

   # 3. Create and push new annotated tag
   git tag -a vX.X.Y -m "Release version X.X.Y" -m "[Change 1]" -m "[Change 2]" ...
   git push origin master --tags
   ```

## Constraints

- **NO CHATTER**: Direct technical output only.
- **PARITY**: The commit message for the release and the annotated tag description must be identical in content (listing all changes).
- **REMOTE SYNC**: Always delete the remote tag before re-pushing if a correction is needed for a specific version.
- **FORMAT**: Always use YYYY-MM-DD for dates in the `Changelog`.
