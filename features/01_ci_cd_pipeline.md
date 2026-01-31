# Feature: CI/CD Pipeline Integration

## Context
The project currently relies on manual execution of tests via the `Makefile`. To ensure code quality and prevent regressions, an automated CI/CD pipeline is needed to run the test suite on every code change.

## Objective
Implement a GitHub Actions workflow that automatically sets up the environment and runs the full test suite on every push and pull request to the `main` branch.

## Execution Prompt
You are an expert DevOps engineer. Your task is to create a GitHub Actions workflow for this project.

### Instructions:

1.  **Create Workflow File**:
    - Create a new file `.github/workflows/ci.yml`.

2.  **Workflow Configuration**:
    - Trigger the workflow on `push` to `main` and `pull_request` to `main`.
    - Use `ubuntu-latest` as the runner image.

3.  **Steps Implementation**:
    - **Checkout**: Use `actions/checkout@v4`.
    - **Setup Python**: Use `actions/setup-python@v5` (required for reporting scripts).
    - **Start Environment**: Run `make start`. Ensure you wait for the database to be ready (you might need to implement a wait loop or use `sleep` as a simple fallback, or better, use a `mysqladmin ping` check).
    - **Inject Data**: Run `make inject`.
    - **Run Tests**: Run `make test-all`.

4.  **Requirements**:
    - The workflow must pass only if `make test-all` succeeds.
    - Ensure all steps are clearly named.
    - **Constraints**: Do not modify the `Makefile` or existing scripts unless absolutely necessary to make them CI-compatible (e.g., removing interactive prompts).
    - **Rules**: Strictly follow the rules in `.agent/rules/*.md`.

5.  **Output**:
    - The content of `.github/workflows/ci.yml`.
    - Updates to `README.md` adding a "CI Status" badge if possible (or instructions to add it).
    - Updates to `Changelog` (following `.agent/rules/CHANGELOG_MANAGEMENT.md`).
