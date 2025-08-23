# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fauxdantic is a Python library for generating fake Pydantic models for testing and development. It provides two main functions: `faux()` for creating model instances and `faux_dict()` for creating dictionaries of fake data.

## Development Commands

### Dependencies and Environment
```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_core.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality Tools
```bash
# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

### Build and Distribution
```bash
# Build package
poetry build
```

## Architecture

### Core Structure
- **`src/fauxdantic/core.py`**: Main entry point containing `faux()` and `faux_dict()` functions
- **`src/fauxdantic/generators/`**: Data generation modules
  - `strings.py`: Constrained string generation with unique string support
  - `numbers.py`: Constrained number generation
  - `collections.py`: List and dict generation
- **`src/fauxdantic/types/`**: Type handling utilities
  - `constraints.py`: Field constraint extraction from Pydantic models
  - `handlers.py`: Union type prioritization and literal type handling
- **`src/fauxdantic/utils/`**: Utility modules
  - `unique.py`: Unique string generation functionality

### Key Features
- **Unique String Generation**: Supports `<unique>` pattern in strings for generating truly unique identifiers
- **Constraint-Aware Generation**: Respects Pydantic field constraints (max_length, etc.)
- **Union Type Prioritization**: Intelligent handling of Union types with preference order
- **Nested Model Support**: Recursive generation for complex nested structures
- **Builtin Type Support**: Handles standard Python types, UUIDs, datetimes, enums

### Testing Configuration
- Uses pytest with configuration in `pytest.ini`
- Test files follow `test_*.py` pattern
- Tests are located in `tests/` directory
- Includes tests for core functionality, complex models, geographic fields, and builtin types

### Code Style
- Black formatter with 88-character line length
- isort for import sorting with black profile
- MyPy for static type checking with strict settings
- Target Python 3.11+
