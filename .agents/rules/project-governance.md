# Project Governance Rules

These repository-wide rules govern documentation, code hygiene, security, and mathematical formatting across `test_db` and `sirene/`.

## 1. English-Only Living Registers and Engineering Artifacts

- All living governance registers (`PROJECT-CONTEXT.md`, `docs/ACTION_LOGBOOK.md`, `docs/RCA_REGISTER.md`), GitHub issues, pull requests, commit messages, source code comments, docstrings, and structured logs MUST be written strictly in English.
- Zero French prose or diacritical characters are permitted in governance registers or source comments. Official French INSEE SQL table and column identifiers (such as `unites_legales` or `etablissements`) remain ASCII-only.

## 2. Zero Secrets, PII, or Local Host Paths

- Never commit real credentials, API keys, tokens, personal data, or personally identifiable information (PII) anywhere in source files, tests, fixtures, or documentation.
- Local Docker PoC defaults MUST rely on explicit ephemeral environment placeholders such as `${POSTGRES_PASSWORD:-pg_sirene_ephemeral}` documented in `sirene/.env.example`.
- Never embed machine-specific absolute filesystem paths or user home directory prefixes in repository files; always use relative repository paths (e.g., `sirene/sql/01_schema_3nf.sql`).

## 3. LaTeX Math Integrity in Markdown

- Display math blocks (`$$`) MUST start at column 0 on dedicated lines with blank lines before and after, even inside nested lists.
- Never use `\operatorname{...}`; use standard LaTeX macros such as `\arg\max`, `\arg\min`, or `\text{...}`.
- Always preserve underscores (`_`) and asterisks (`*`) inside math spans, keep inline math delimiters tight (`$x$`, never `$ x $`), and escape prose currency symbols (`\$`).

## 4. Living Register Maintenance

- Keep `PROJECT-CONTEXT.md` strictly bounded under 150 words as a single-glance engineering summary.
- Track active work and completed milestones in `docs/ACTION_LOGBOOK.md` and record root causes, implemented mitigations, approved standards, and future backlog items in `docs/RCA_REGISTER.md`.
