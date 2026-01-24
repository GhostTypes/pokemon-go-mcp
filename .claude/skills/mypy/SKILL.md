---
name: mypy
description: "Professional static type checking for Python with mypy (v1.19.1). Use when working with Python type hints, type annotations, or integrating mypy into codebases for: (1) Adding type annotations to Python code, (2) Configuring mypy (mypy.ini, pyproject.toml, setup.cfg), (3) Resolving mypy errors and type checking issues, (4) Using advanced type patterns (Generics, Protocols, TypedDict), (5) Running mypy in CI/CD or development workflows, (6) Creating or working with stub files, (7) Migrating existing codebases to typed Python, or (8) Any mypy-related development task."
---

# Mypy - Professional Static Type Checking

Mypy is a static type checker for Python that finds bugs without running code. This skill provides comprehensive guidance for professional mypy integration and usage.

## Quick Start

### Installation and Basic Usage

```bash
# Install mypy
python3 -m pip install mypy

# Check a file
mypy program.py

# Check with strict mode
mypy --strict program.py
```

### Basic Type Annotations

```python
def greeting(name: str) -> str:
    return 'Hello ' + name

# Type checking catches errors
greeting(3)  # Error: Argument has incompatible type "int"; expected "str"
```

## Configuration

Mypy supports multiple configuration formats (discovery order):

1. `mypy.ini`
2. `.mypy.ini`
3. `pyproject.toml` (with `[tool.mypy]` section)
4. `setup.cfg` (with `[mypy]` section)

### Essential Configuration Options

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

# Per-module configuration
[mypy-module_name.*]
ignore_missing_imports = True
```

See `references/config_file.md` for complete configuration reference.

## Core Workflows

### Adding Types to Existing Code

1. Start with `--check-untyped-defs` for gradual typing
2. Use `# type: ignore` comments sparingly for temporary exceptions
3. Add type annotations incrementally, module by module
4. Enable stricter checks progressively

See `references/existing_code.md` for migration strategies.

### Resolving Type Errors

When mypy reports errors:

1. Check the error code (e.g., `[attr-defined]`)
2. Consult error code documentation:
   - `references/error_code_list.md` - Default errors
   - `references/error_code_list2.md` - Optional checks
3. Use type narrowing techniques when needed
4. Consider `reveal_type()` for debugging type inference

See `references/common_issues.md` for troubleshooting.

### Working with Advanced Types

**Generics**: `references/generics.md`
- TypeVar, Generic classes, bounded type variables
- Variance (covariant, contravariant, invariant)

**Protocols**: `references/protocols.md`
- Structural subtyping, runtime checkable protocols
- Protocol composition

**TypedDict**: `references/typed_dict.md`
- Required vs optional keys, inheritance
- Total vs non-total TypedDicts

**Literal Types**: `references/literal_types.md`
- String/int/bool/Enum literals
- Exhaustiveness checking

See `references/kinds_of_types.md` for type system overview.

## Command Line Reference

```bash
# Strict mode (recommended for new projects)
mypy --strict module.py

# Check specific paths
mypy src/ tests/

# Generate HTML coverage report
mypy --html-report ./mypy-report src/

# Use mypy daemon for faster checking
dmypy run -- src/

# Generate stubs from existing code
stubgen -p mypackage -o stubs/
```

See `references/command_line.md` for all CLI options.

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy --install-types --non-interactive
    mypy src/
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Reference Documentation

The `references/` directory contains complete mypy 1.19.1 documentation:

### Getting Started
- `getting_started.md` - Installation, basic concepts
- `cheat_sheet_py3.md` - Quick reference guide

### Type System
- `builtin_types.md` - Python built-in types
- `type_inference_and_annotations.md` - Annotations guide
- `kinds_of_types.md` - Type system overview
- `class_basics.md` - Class typing fundamentals
- `protocols.md` - Structural subtyping
- `generics.md` - Generic types and TypeVars
- `typed_dict.md` - TypedDict patterns
- `literal_types.md` - Literal types and Enums
- `final_attrs.md` - Final declarations
- `more_types.md` - Additional type patterns
- `type_narrowing.md` - Type narrowing techniques
- `duck_type_compatibility.md` - Duck typing rules

### Configuration & Running
- `config_file.md` - Complete configuration reference
- `command_line.md` - CLI options and flags
- `running_mypy.md` - Running mypy guide
- `inline_config.md` - Inline type comments
- `mypy_daemon.md` - Daemon mode for speed
- `installed_packages.md` - Package type stubs

### Advanced Topics
- `stubs.md` - Stub files guide
- `stubgen.md` - Automatic stub generation
- `stubtest.md` - Stub testing tool
- `extending_mypy.md` - Plugins and extensions
- `metaclasses.md` - Metaclass typing
- `runtime_troubles.md` - Runtime annotation issues
- `dynamic_typing.md` - Dynamic typing patterns

### Troubleshooting
- `error_codes.md` - Error code system
- `error_code_list.md` - Default error codes
- `error_code_list2.md` - Optional error codes
- `common_issues.md` - Solutions to common issues
- `faq.md` - Frequently asked questions

### Project Info
- `additional_features.md` - Advanced features
- `supported_python_features.md` - Python version support
- `existing_code.md` - Migration strategies
- `changelog.md` - Version history

## Updating Documentation

The `scripts/` directory contains tools to refresh documentation from mypy.readthedocs.io:

```bash
# Discover all documentation pages
python scripts/discover_pages.py > mypy_pages.txt

# Bulk scrape and clean documentation
python scripts/scrape_docs.py

# Clean individual markdown files
python scripts/clean_markdown.py input.md output.md
```

These scripts use cloudscraper for Cloudflare bypass and automatically clean navigation/footer content.

## Best Practices

1. **Start gradually** - Use `--check-untyped-defs` initially
2. **Configure per-module** - Different strictness for different parts of codebase
3. **Use error codes** - Specific `# type: ignore[code]` instead of blanket ignores
4. **Leverage inference** - Let mypy infer types when obvious
5. **Run in CI** - Catch type errors before merge
6. **Update regularly** - Stay current with mypy releases for better type checking

## Common Patterns

### Optional Values
```python
from typing import Optional

def find_user(id: int) -> Optional[User]:
    # May return None
    return user_db.get(id)
```

### Union Types
```python
from typing import Union

def process(value: Union[int, str]) -> str:
    if isinstance(value, int):
        return str(value)
    return value
```

### Generic Functions
```python
from typing import TypeVar, Sequence

T = TypeVar('T')

def first(seq: Sequence[T]) -> T:
    return seq[0]
```

### Protocol (Structural Typing)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()  # Any object with draw() works
```

## Version Information

This skill is based on mypy 1.19.1 (stable) documentation. Use the scraping scripts to update to newer versions as they are released.
