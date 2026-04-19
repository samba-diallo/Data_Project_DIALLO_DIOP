Continuous Integration and Continuous Deployment (CI/CD)
==========================================================

Overview
--------
This project uses GitHub Actions for automated testing, code quality checks, and validation.
All workflows run automatically on push and pull requests.

Workflows
---------

1. Unit Tests (unit-tests.yml)
   Triggers: push to any branch, pull requests
   Tests: Pytest on Python 3.9, 3.10, 3.11
   Reports: Test results artifacts uploaded
   Scope: tests/ directory
   Success Criteria: All tests pass

2. Code Quality Check (code-quality.yml)
   Triggers: push to any branch, pull requests
   Checks:
     - Flake8 style guide (max line length: 100)
     - Pylint analysis
     - Python syntax validation
   Scope: src/, config.py, main.py
   Note: Errors continue (non-blocking)

3. Dependency Check (dependencies-check.yml)
   Triggers: push to any branch, pull requests
   Validates:
     - requirements.txt existence
     - Package installation
     - Import verification (dash, plotly, pandas, pytest)
     - Project structure integrity
   Scope: Project structure
   Success Criteria: All checks pass

4. PR Validation Gate (pr-validation.yml)
   Triggers: PR to main or dev branches only
   Validates:
     - Target branch (main or dev required)
     - No merge conflict markers
     - Unit tests pass
     - Code quality checks
     - Required files exist
     - PR comment with results
   Scope: PR workflow
   Success Criteria: All validations pass before merge

Branch Rules
------------

By Branch:
- dev1: All workflows run, target should be dev
- dev2: All workflows run, target should be dev
- dev: All workflows run, merge gate enforced
- main: PR validation gate enforced, protected branch

Merge Requirements
------------------

Pull Request to main:
1. Must pass all tests (Python 3.9, 3.10, 3.11)
2. Code quality checks must pass or be reviewed
3. No merge conflict markers
4. All required files present
5. Target branch must be main

Pull Request to dev:
1. Must pass unit tests
2. Good to have: Code quality checks
3. Staging environment for integration

Quick Reference
---------------

Running Tests Locally:
  pytest tests/ -v

Running Flake8 Locally:
  flake8 src/ config.py main.py --max-line-length=100

Running Pylint Locally:
  pylint src/ config.py main.py

Viewing Artifacts:
  Actions → Workflow Run → Artifacts → test-results-X.Y.Z

Troubleshooting
---------------

If tests fail locally but pass in CI:
  Check Python version: python --version
  Check dependencies: pip install -r requirements.txt
  Clear cache: rm -rf __pycache__ .pytest_cache

If CI fails but tests pass locally:
  Check Python version matches CI (3.9/3.10/3.11)
  Check requirements.txt is updated
  Check for OS-specific issues (use ubuntu-latest)
