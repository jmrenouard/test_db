---
description: release
---

# Release Workflow

This workflow automates the versioning process, including updating the Changelog and tagging the repository.

## When to use this workflow

- When the user types `/release`.
- When a set of features is ready for a new version.

## Task

1. Read the current version from the `Changelog`.
2. Determine the next version (following `CHANGELOG_MANAGEMENT.md` rules).
3. Update `Changelog` with the new version, date, and changes summary.
4. Commit the Changelog update.

   ```bash
   git add Changelog
   git commit -m "chore: release version X.X.Y"
   ```

5. Create a git tag for the new version.

   ```bash
   git tag -a vX.X.Y -m "Release version X.X.Y"
   ```

6. Push changes and tags.

   ```bash
   git push origin main && git push origin --tags
   ```

## Constraints

- Date format must be `YYYY-MM-DD`.
- Follow the entry format: `Version Date` followed by indented bullet points.
- Ensure all tests pass (`/run-tests`) before performing a release.
