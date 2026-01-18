# Feature: Refactor Interactive Runner

## Context
The `interactive_runner.py` script is currently a monolithic file containing configuration, execution logic, and HTML report generation. This makes it hard to maintain, test, and extend.

## Objective
Refactor the Python runner into a modular package structure to improve separation of concerns and maintainability.

## Execution Prompt
You are a Senior Python Developer. Your task is to refactor the existing `interactive_runner.py` into a clean, modular Python package.

### Instructions:

1.  **Create Package Structure**:
    - Create a directory `runner/`.
    - Create `runner/__init__.py`.

2.  **Split Responsibilities**:
    - **Configuration (`runner/config.py`)**: Move `STEPS`, `REPORT_FILE`, `HTML_TEMPLATE`, etc., to this file.
    - **Executor (`runner/executor.py`)**: Move the `run_command` function here. Improve error handling if possible.
    - **Reporter (`runner/reporter.py`)**: Move `generate_report` and the HTML template logic here. Use a class or functions that accept results and produce the file.
    - **Main (`runner/main.py`)**: The entry point that orchestrates the execution loop.

3.  **Update Entry Point**:
    - You can either keep `interactive_runner.py` as a thin wrapper that imports from `runner`, or update the `Makefile` to run the module directly (e.g., `python3 -m runner.main`).
    - If you keep `interactive_runner.py`, ensure it's just a few lines calling the main function.

4.  **Requirements**:
    - Ensure the functionality remains *exactly* the same from the user's perspective.
    - The HTML output must remain identical (unless you improve it).
    - **Rules**: Strictly follow the rules in `.agent/rules/*.md`.
    - **Tests**: Verify the refactor by running the runner (dry run if possible) or checking imports.

5.  **Output**:
    - The new `runner/` directory and files.
    - The updated `interactive_runner.py` or `Makefile`.
    - Updated `Changelog`.
