<!-- Markdown linting -->

Markdown files must be linted by `prettier`. Verify this by running
`prettier -w $filepath1 $filepath2 ...` on all modified markdown files.

<!-- YAML linting -->

YAML files must be linted by `yamlfix`. Verify this by running
`yamlfix $filepath1` on all modified YAML files.

<!-- Python linting -->

When running shell commands, always pass filepaths relative to the repo root.

Python code must be formatted by `ruff`. Verify this by running
`ruff format $filepath1 $filepath2 ...` on all modified files.

Python code must be linted by `ruff`. Verify this by running
`ruff check $filepath1 $filepath2 ...` on all modified files.

Python code must be type checked by `mypy`. Verify this by running `mypy` with
no arguments after making changes.

<!-- Python testing -->

Tests must always pass after every change. Run the test suite with `pytest`.

Unit tests live in `tests/unit/`. They should be structured into classes with
one class per function/class being tested.

Don't use `unittest.mock.patch` in unit tests. Use `unittest.mock.patch.object`
instead.

Functional tests live in `tests/functional/`. Functional tests use the `runner`
Pytest fixture to run the Click command being tested.

When creating `mock.Mock` instances, always pass a `spec` argument.

<!-- General Python -->

Don't inline imports in Python files.

Prefer to have only one statement in a `try..except` block.

Don't leave any trailing whitespace.

<!-- Application structure -->

This repo is a Click application. Commands are registered in
`src/chow/__main__.py`.

Each command should make a single call of a use case function from
`src/chow/usecases/`.
