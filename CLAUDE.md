# Obsidian Project Manager - Development Guidelines

## Build Commands
- Build: `hatch build`
- Run: `obsidian_project_manager`

## Lint and Test Commands
- Install dev dependencies: `pip install -e ".[dev]"`
- Lint: `ruff check .`
- Type check: `mypy src`
- Run tests: `pytest`
- Run single test: `pytest path/to/test_file.py::test_function_name`

## Code Style Guidelines
- Follow PEP 8 guidelines
- Use type hints for function arguments and return values
- Use snake_case for functions and variables, PascalCase for classes
- Group imports: stdlib, third-party, local
- Use f-strings for string formatting
- Handle exceptions with specific error types
- Use docstrings for modules, classes, and functions
- Keep functions small and focused on a single task
- Use meaningful variable and function names

## Error Handling
- Use try/except blocks for expected exceptions
- Raise custom exceptions when appropriate
- Log errors for debugging purposes

Remember to update this file as the project evolves and new conventions are established.