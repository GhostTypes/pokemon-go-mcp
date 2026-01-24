# Code Quality Remediation PRD

**Project:** pokemon-go-mcp
**Branch:** code-quality-remediation (based on fastmcp-v3-migration)
**Start Date:** 2026-01-24
**Goal:** Achieve 100% pass rate for mypy, ruff, and pytest with production-ready code quality

---

## Executive Summary

This PRD documents the complete remediation of all code quality issues in the Pokemon Go MCP project. The codebase currently has:

- **1,094 mypy type errors** across 9 files in pogo_mcp/
- **3,103 ruff lint violations** across 57 files
- **28 files need reformatting**
- **~15-20 hours estimated work**

The remediation will be executed in autonomous Claudius loops with 200 maximum iterations, frequent commits with timestamps, and complete validation after each task.

---

## Pass Conditions (ALL Must Be True)

1. ✅ `pytest` passes with 100% of tests succeeding
2. ✅ `python -m mypy pogo_mcp/` passes with 0 errors
3. ✅ `python -m ruff check pogo_mcp/ pogo_scraper/` passes with 0 errors
4. ✅ `python -m ruff format --check .` reports no changes needed
5. ✅ All code follows best practices (SOLID, DRY, KISS, YAGNI)
6. ✅ No regression in functionality - MCP server works, scraper works
7. ✅ No commented-out code, no TODOs without author/issue links
8. ✅ Full type coverage with precise types (no Any unless absolutely necessary)
9. ✅ Proper exception handling (no bare except clauses)
10. ✅ Security issues resolved (timeouts on all HTTP requests)

---

## Constraints (Hard Boundaries - DO NOT VIOLATE)

- **NO modifying tests to make them pass** - fix the underlying code
- **NO adding # noqa: comments** as band-aid fixes (except legitimate cases)
- **NO disabling mypy or ruff rules** in pyproject.toml to reduce error count
- **NO removing type checks or reducing strictness**
- **NO breaking changes to public APIs**
- **NO functional regressions** - if a fix breaks functionality, it's wrong
- **NO corner-cutting** - every fix must be production-ready
- **NO commented-out code** - remove it or uncomment it
- **NO print() in library code** (pogo_mcp/) - use logging
- **NO blind except:** clauses - use specific exceptions
- **NO unused imports, variables, or arguments** (except legitimate cases)
- **Documentation comments must be accurate** - update them if code changes

**Legitimate Exceptions:**
- Test files may use # noqa: for test-specific patterns (unused fixtures, magic values)
- Scraper CLI output may use print() with # noqa: T201
- Interface requirements may use # noqa: ARG002 for unused parameters
- Circular import avoidance may use # noqa: PLC0415

---

## Task Checklist

### Phase 1: Foundation & Configuration (P0 - Critical)

- [ ] **Task 1.1:** Update ruff configuration in pyproject.toml
  - Migrate top-level `select`/`ignore` to `[tool.ruff.lint]` section
  - Remove obsolete rules: ANN101, ANN102
  - Add COM812 and ISC001 to ignore (formatter conflicts)
  - Add per-file ignores for tests and skill scripts
  - **Verification:** `python -m ruff check pyproject.toml` (no deprecation warnings)

- [ ] **Task 1.2:** Install missing type stubs
  - Add `types-python-dateutil` to pyproject.toml dev dependencies
  - Add `types-requests` to pyproject.toml dev dependencies
  - Run `uv sync` to install
  - **Verification:** `python -m mypy pogo_mcp/utils.py pogo_mcp/api_client.py`

- [ ] **Task 1.3:** Fix bare `Dict` type parameters in pogo_mcp/types.py
  - Lines 26, 39-44, 68, 71, 102
  - Replace `Dict` with `Dict[str, Any]` where appropriate
  - Add `Any` to imports if not present
  - **Verification:** `python -m mypy pogo_mcp/types.py` (0 errors)

- [ ] **Task 1.4:** Convert EventExtraData from dataclass to TypedDict
  - Replace dataclass (lines 37-44) with TypedDict definition
  - Add `TypedDict` to imports
  - **Verification:** `python -m mypy pogo_mcp/types.py` (0 errors, EventExtraData indexing works)

- [ ] **Task 1.5:** Apply ruff auto-fixes (safe)
  - Run: `python -m ruff check --fix .`
  - Fixes ~2,000 violations automatically
  - Review changes with `git diff`
  - **Verification:** `pytest` (ensure no regressions)

- [ ] **Task 1.6:** Apply ruff auto-fixes (unsafe)
  - Run: `python -m ruff check --fix --unsafe-fixes .`
  - Additional ~527 fixes (requires review)
  - Test critical functionality after
  - **Verification:** `pytest` + manual MCP server test

- [ ] **Task 1.7:** Format all files with ruff
  - Run: `python -m ruff format .`
  - Reformat 28 files
  - **Verification:** `python -m ruff format --check .` (no changes)

### Phase 2: Type Safety (P1 - High Priority)

- [ ] **Task 2.1:** Fix union type attribute access in pogo_mcp/server.py (225+ errors)
  - Add type assertions using `isinstance()` checks
  - Create typed helper functions for data extraction
  - Fix lines 54-99, 122-215, 276-361, 364-424
  - **Verification:** `python -m mypy pogo_mcp/server.py` (0 errors)

- [ ] **Task 2.2:** Fix pogo_mcp/api_client.py type annotations
  - Line 26: `_cache` type parameter
  - Line 33: `_load_local_data` return type
  - Line 45: Add type annotation for json.load() result
  - Line 50: `_fetch_data` return type
  - Line 213: Provide default for `type` field
  - Line 375: Add `-> None` to `_clear_cache`
  - **Verification:** `python -m mypy pogo_mcp/api_client.py` (0 errors)

- [ ] **Task 2.3:** Fix pogo_mcp/utils.py type issues
  - Line 21: Add type cast for parse_datetime
  - Lines 280-308: EventExtraData indexing (after TypedDict conversion)
  - All EventExtraData access patterns
  - **Verification:** `python -m mypy pogo_mcp/utils.py` (0 errors)

- [ ] **Task 2.4:** Add variable type annotations
  - pogo_mcp/rocket_lineups.py line 40: `grunts_by_type`
  - pogo_mcp/raids.py lines 36, 119, 276: `tiers`
  - pogo_mcp/eggs.py lines 52, 148, 234, 395: `egg_types`, `distances`
  - pogo_mcp/server.py line 51: `sources`
  - **Verification:** `python -m mypy pogo_mcp/*.py` (0 errors for these files)

- [ ] **Task 2.5:** Add missing return type annotations
  - pogo_mcp/server.py: `register_cross_cutting_tools()`, `main()`
  - pogo_mcp/api_client.py: `_clear_cache()`
  - pogo_mcp/promo_codes.py: `register_promo_code_tools()`
  - **Verification:** `python -m mypy pogo_mcp/*.py` (check ANN201/ANN202 errors resolved)

- [ ] **Task 2.6:** Fix untyped decorators
  - pogo_mcp/promo_codes.py: Add type annotations to decorated functions
  - Ensure all @mcp.tool() functions have proper types
  - **Verification:** `python -m mypy pogo_mcp/promo_codes.py` (0 errors)

### Phase 3: Code Quality - Type Annotations (P1)

- [ ] **Task 3.1:** Add missing function argument type annotations (298 violations)
  - Run: `python -m ruff check --select ANN001 --output-format=text .`
  - Add type annotations to all function arguments
  - Focus on: pogo_mcp/, pogo_scraper/, tests/
  - **Verification:** `python -m ruff check --select ANN001 .` (0 errors)

- [ ] **Task 3.2:** Add missing return type annotations - public functions (181 violations)
  - Run: `python -m ruff check --select ANN201 --output-format=text .`
  - Add `-> ReturnType` to all public functions
  - **Verification:** `python -m ruff check --select ANN201 .` (0 errors)

- [ ] **Task 3.3:** Add missing return type annotations - private functions (130 violations)
  - Run: `python -m ruff check --select ANN202 --output-format=text .`
  - Add `-> ReturnType` to all private functions
  - **Verification:** `python -m ruff check --select ANN202 .` (0 errors)

- [ ] **Task 3.4:** Replace Any with specific types (6 violations)
  - Run: `python -m ruff check --select ANN401 --output-format=text .`
  - Use precise types instead of Any
  - **Verification:** `python -m ruff check --select ANN401 .` (0 errors)

### Phase 4: Code Quality - Exception Handling (P1)

- [ ] **Task 4.1:** Fix blind except clauses (112 violations)
  - Run: `python -m ruff check --select BLE001 --output-format=text .`
  - Replace `except:` with specific exceptions
  - Use multiple except clauses for different exception types
  - **Verification:** `python -m ruff check --select BLE001 .` (0 errors)

- [ ] **Task 4.2:** Fix Exception instance misuse (57 violations)
  - Run: `python -m ruff check --select TRY400 --output-format=text .`
  - Change `raise e` to `raise` (preserves stack trace)
  - **Verification:** `python -m ruff check --select TRY400 .` (0 errors)

- [ ] **Task 4.3:** Add else clauses to try blocks (55 violations)
  - Run: `python -m ruff check --select TRY300 --output-format=text .`
  - Refactor to use else clauses for post-try logic
  - **Verification:** `python -m ruff check --select TRY300 .` (0 errors)

- [ ] **Task 4.4:** Fix raise within try blocks (7 violations)
  - Run: `python -m ruff check --select TRY301 --output-format=text .`
  - Move raises to else clauses
  - **Verification:** `python -m ruff check --select TRY301 .` (0 errors)

### Phase 5: Code Quality - Logging & Security (P1)

- [ ] **Task 5.1:** Replace print() with logging in pogo_mcp/ (226 violations)
  - Run: `python -m ruff check --select T201 --output-format=text pogo_mcp/`
  - Replace print statements with logger calls
  - Set up proper logger in each module
  - **Verification:** `python -m ruff check --select T201 pogo_mcp/` (0 errors)

- [ ] **Task 5.2:** Fix logging f-strings (137 violations)
  - Run: `python -m ruff check --select G004 --output-format=text .`
  - Change `logger.info(f"...")` to `logger.info("...", var)`
  - Use % formatting for lazy interpolation
  - **Verification:** `python -m ruff check --select G004 .` (0 errors)

- [ ] **Task 5.3:** Add timeouts to HTTP requests (7 violations)
  - Run: `python -m ruff check --select S113 --output-format=text .`
  - Add `timeout=30` to all httpx/requests calls
  - **Verification:** `python -m ruff check --select S113 .` (0 errors)

### Phase 6: Code Quality - Paths & Imports (P2)

- [ ] **Task 6.1:** Replace os.path with pathlib (138 violations)
  - Run: `python -m ruff check --select PTH --output-format=text .`
  - Replace os.path operations with Path objects
  - **Verification:** `python -m ruff check --select PTH .` (0 errors)

- [ ] **Task 6.2:** Remove unused imports (87 violations)
  - Run: `python -m ruff check --select F401 --output-format=text .`
  - Remove all unused imports
  - **Verification:** `python -m ruff check --select F401 .` (0 errors)

- [ ] **Task 6.3:** Fix deprecated imports (46 violations)
  - Run: `python -m ruff check --select UP035 --output-format=text .`
  - Replace typing.Dict/List with builtin dict/list (Python 3.10+)
  - **Verification:** `python -m ruff check --select UP035 .` (0 errors)

- [ ] **Task 6.4:** Move imports to top level (91 violations)
  - Run: `python -m ruff check --select PLC0415 --output-format=text .`
  - Move imports to module level (unless circular import)
  - Use # noqa: PLC0415 for legitimate mid-file imports
  - **Verification:** `python -m ruff check --select PLC0415 .` (0 errors)

### Phase 7: Code Quality - Style & Cleanup (P2)

- [ ] **Task 7.1:** Remove unused arguments (149 violations)
  - Run: `python -m ruff check --select ARG --output-format=text .`
  - Remove truly unused arguments
  - Use `_` prefix for intentionally unused callback params
  - Use # noqa: ARG002 for interface requirements
  - **Verification:** `python -m ruff check --select ARG .` (0 errors, except legitimate ignores)

- [ ] **Task 7.2:** Extract magic values to constants (29 violations)
  - Run: `python -m ruff check --select PLR2004 --output-format=text .`
  - Create named constants for magic numbers/strings
  - **Verification:** `python -m ruff check --select PLR2004 .` (0 errors in library code)

- [ ] **Task 7.3:** Simplify conditional logic (10+ violations)
  - Run: `python -m ruff check --select SIM --output-format=text .`
  - Apply SIM102, SIM103, SIM108 refactorings
  - **Verification:** `python -m ruff check --select SIM .` (0 errors)

- [ ] **Task 7.4:** Remove commented-out code (10 violations)
  - Run: `python -m ruff check --select ERA001 --output-format=text .`
  - Delete all dead code
  - **Verification:** `python -m ruff check --select ERA001 .` (0 errors)

- [ ] **Task 7.5:** Fix TODO comments (15 violations)
  - Run: `python -m ruff check --select TD --output-format=text .`
  - Add author and issue links to TODOs
  - Or implement the TODO and remove comment
  - **Verification:** `python -m ruff check --select TD .` (0 errors)

- [ ] **Task 7.6:** Fix line length issues (351 violations)
  - Run: `python -m ruff check --select E501 --output-format=text .`
  - Break long lines appropriately
  - Use # noqa: E501 for unbreakable URLs
  - **Verification:** `python -m ruff check --select E501 .` (0 errors, except legitimate ignores)

### Phase 8: Test File Remediation (P2)

- [ ] **Task 8.1:** Add type annotations to test functions
  - Run: `python -m ruff check --select ANN --output-format=text tests/`
  - Add type hints to all test functions
  - **Verification:** `python -m ruff check --select ANN tests/` (0 errors)

- [ ] **Task 8.2:** Fix test-specific code quality issues
  - Remove unused test variables
  - Fix exception handling in tests
  - Add proper assertions
  - **Verification:** `pytest` (all tests pass)

- [ ] **Task 8.3:** Improve test coverage (if needed)
  - Run: `pytest --cov=pogo_mcp --cov-report=term-missing`
  - Add tests for uncovered code paths
  - **Verification:** Coverage report shows adequate coverage

### Phase 9: File-Specific Deep Cleans (P2)

- [ ] **Task 9.1:** pogo_mcp/server.py (~200 violations)
  - Add all type annotations
  - Replace print with logging
  - Fix exception handling
  - Remove unused code
  - **Verification:** `python -m mypy pogo_mcp/server.py && python -m ruff check pogo_mcp/server.py` (0 errors)

- [ ] **Task 9.2:** pogo_mcp/api_client.py (~150 violations)
  - Add all type annotations
  - Fix logging patterns
  - Improve exception handling
  - Add timeouts
  - **Verification:** `python -m mypy pogo_mcp/api_client.py && python -m ruff check pogo_mcp/api_client.py` (0 errors)

- [ ] **Task 9.3:** pogo_mcp/utils.py (~100 violations)
  - Add all type annotations
  - Fix exception handling
  - Improve code quality
  - **Verification:** `python -m mypy pogo_mcp/utils.py && python -m ruff check pogo_mcp/utils.py` (0 errors)

- [ ] **Task 9.4:** pogo_scraper/scraper.py (~180 violations)
  - Add all type annotations
  - Keep CLI print() with # noqa: T201
  - Fix exception handling
  - Improve path handling
  - **Verification:** `python -m mypy pogo_scraper/scraper.py && python -m ruff check pogo_scraper/scraper.py` (0 errors)

- [ ] **Task 9.5:** pogo_mcp/types.py (~50 violations)
  - Ensure all dataclass fields have types
  - Remove unused imports
  - **Verification:** `python -m mypy pogo_mcp/types.py && python -m ruff check pogo_mcp/types.py` (0 errors)

### Phase 10: Final Validation (P0)

- [ ] **Task 10.1:** Complete mypy validation
  - Run: `python -m mypy pogo_mcp/ pogo_scraper/`
  - **Goal:** 0 errors
  - If errors remain, fix them

- [ ] **Task 10.2:** Complete ruff lint validation
  - Run: `python -m ruff check pogo_mcp/ pogo_scraper/`
  - **Goal:** 0 errors
  - If errors remain, fix them

- [ ] **Task 10.3:** Complete ruff format validation
  - Run: `python -m ruff format --check .`
  - **Goal:** "No changes needed"
  - If changes needed, run formatter

- [ ] **Task 10.4:** Complete test suite validation
  - Run: `pytest -v`
  - **Goal:** 100% tests pass
  - If failures, debug and fix (DO NOT modify tests to hide bugs)

- [ ] **Task 10.5:** Integration testing
  - Test MCP server: `uv run python server.py`
  - Test scraper: `python pogo_scraper/scraper.py --all --output-dir data --cache-duration 0`
  - **Goal:** Both work correctly

- [ ] **Task 10.6:** Final code quality review
  - Review git diff for all changes
  - Ensure no regressions
  - Ensure all changes are production-ready
  - **Goal:** Clean, professional codebase

---

## Verification Commands (Run After Each Task)

```bash
# Type checking
python -m mypy pogo_mcp/ pogo_scraper/

# Linting
python -m ruff check pogo_mcp/ pogo_scraper/

# Formatting check
python -m ruff format --check .

# Testing
pytest -v

# Integration test (MCP server)
timeout 5 uv run python server.py || true

# Count errors
python -m mypy pogo_mcp/ 2>&1 | grep -c "error:" || echo "0"
python -m ruff check pogo_mcp/ pogo_scraper/ 2>&1 | grep -c "^pogo" || echo "0"
```

---

## Git Workflow

**Commit Strategy:** After every completed task

**Commit Message Format:**
```
[task X.Y] Brief description (Time: Xh Ym)

- File1.py: Fixed specific issue
- File2.py: Added type annotations

Tests: pytest pass
Mypy: 0 errors
Ruff: 0 errors
```

**Push Strategy:** Push after every commit

**Branch:** code-quality-remediation (based on fastmcp-v3-migration)

**Pull Request:** After all tasks complete, PR to main branch

---

## Available Skills (Read When Needed)

Skills use progressive disclosure. Start with SKILL.md and branch out as needed.

| Skill Name | When to Use | Path |
|------------|-------------|------|
| mypy | Type checking tasks | `.claude/skills/mypy/SKILL.md` |
| ruff-dev | Linting/formatting tasks | `.claude/skills/ruff-dev/SKILL.md` |
| best-practices | Code quality/architecture | `.claude/skills/best-practices/SKILL.md` |
| get-time | Add timestamp to commit messages | `.claude/skills/get-time/SKILL.md` |
| sub-agent-creator | Create new agents if needed | `.claude/skills/sub-agent-creator/SKILL.md` |
| mcp-test-harness | Integration testing | `.claude/skills/mcp-test-harness/SKILL.md` |
| mcp-schema-sync | After data structure changes | `.claude/skills/mcp-schema-sync/SKILL.md` (use proactively) |
| fastmcp-v3-migration | FastMCP v3 patterns | `.claude/skills/fastmcp-v3-migration/SKILL.md` |

---

## Sub-Agents Available

These agents will be passed via --agents CLI flag:

1. **code-quality** - Use proactively after code changes to verify quality
2. **mypy-specialist** - Use for complex mypy issues and type patterns
3. **mcp-maintainer** - Use after scraper/output changes to sync MCP schema
4. **leekduck-scraper-architect** - Use for scraper/parser fixes and updates

---

## Project Context

### Architecture

- **pogo_scraper/** - Web scraper using BeautifulSoup, httpx, requests
  - Fetches HTML from LeekDuck.com
  - Parses event data, raid bosses, research tasks, eggs, rocket lineups
  - Outputs JSON files to data/

- **pogo_mcp/** - MCP server using FastMCP v3
  - Reads JSON data from data/
  - Exposes tools via Model Context Protocol
  - Caching, validation, formatting utilities

### Tech Stack

- Python 3.10+
- FastMCP 3.0.0b1 (newly migrated)
- httpx for HTTP client
- BeautifulSoup for HTML parsing
- pytest for testing
- mypy for type checking (strict mode)
- ruff for linting and formatting

### Quality Bar

- **Production code** - not a prototype
- **Strict type checking** - no Any unless absolutely necessary
- **Zero tolerance** for regressions
- **No shortcuts** - every fix must be proper and permanent
- **Test coverage** - all changes must be tested

---

## Common Patterns Reference

### Type Annotation Pattern

```python
from typing import Optional, Dict, List, Any

def process_data(data: Dict[str, Any]) -> List[str]:
    """Process data and return results."""
    results: List[str] = []
    for item in data.get("items", []):
        if isinstance(item, str):
            results.append(item.upper())
    return results
```

### Exception Handling Pattern

```python
import logging

logger = logging.getLogger(__name__)

try:
    data = json.load(f)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON: %s", e)
    return None
except IOError as e:
    logger.error("Failed to read file: %s", e)
    return None
```

### Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("Processing %d items", len(items))
logger.error("Failed: %s", error)

# Bad
logger.info(f"Processing {len(items)} items")  # Don't do this
```

### Type Narrowing Pattern

```python
from typing import Union

class A:
    a_field: str

class B:
    b_field: int

def process(item: Union[A, B]) -> str:
    if isinstance(item, A):
        # Type narrowed to A
        return item.a_field
    else:
        # Type narrowed to B
        return str(item.b_field)
```

---

## End of PRD

**Total Tasks:** 60+ tasks across 10 phases
**Estimated Effort:** 15-20 hours
**Maximum Iterations:** 200
**Success Criteria:** All 10 pass conditions met

**Next Step:** Start executing tasks in order, marking complete as you go.
