# Ruff Remediation Quick Start

**For Pokemon Go MCP Project**

Generated: 2026-01-23
Total Violations: 5,635 across 57 files

---

## TL;DR - Fast Track to 60% Reduction

### Step 1: Fix Configuration (5 min)

Edit `pyproject.toml` - Move `select` and `ignore` under `[tool.ruff.lint]`:

```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", ...] # (move existing select here)
ignore = ["S101", "PLR0913", "PLR0912", "PLR0915", "COM812", "ISC001"]
```

### Step 2: Auto-Fix (10 min)

```bash
cd /c/Users/Cope/Documents/GitHub/pokemon-go-mcp
python -m ruff check --fix .
python -m ruff check --fix --unsafe-fixes .
```

**Result:** ~2,500 violations fixed automatically

### Step 3: Format (5 min)

```bash
python -m ruff format .
```

**Result:** All 57 files formatted

### Step 4: Review Remaining Issues

```bash
python -m ruff check --statistics .
```

**Result:** See what's left (mostly type annotations and error handling)

---

## Top 10 Violation Categories

| Count | Rule | Description | Auto-fixable? |
|-------|------|-------------|---------------|
| 2,065 | Q000 | Bad quotes (single → double) | Yes |
| 716 | W293 | Blank lines with whitespace | Yes |
| 351 | E501 | Line too long (>88 chars) | Partial |
| 298 | ANN001 | Missing type annotations | No |
| 226 | T201 | Print statements | No |
| 181 | ANN201 | Missing return types | No |
| 152 | UP006 | Old-style type annotations | Yes |
| 138 | ARG002 | Unused arguments | No |
| 137 | G004 | Logging with f-strings | No |
| 112 | BLE001 | Blind exception catching | No |

---

## Common Fix Patterns

### Type Annotations (625 violations)

```python
# Before:
def fetch_data(endpoint):
    return data

# After:
def fetch_data(endpoint: str) -> Dict[str, Any]:
    return data
```

### Print → Logging (226 violations)

```python
# Before:
print(f"Loading {len(items)} items")

# After:
logger.info("Loading %d items", len(items))
```

### Exception Handling (112 violations)

```python
# Before:
try:
    data = json.load(f)
except:
    logger.error("Failed")

# After:
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    logger.error("Failed: %s", e)
except IOError as e:
    logger.error("IO error: %s", e)
```

### Path Handling (138 violations)

```python
# Before:
import os
if os.path.exists("file.json"):
    with open("file.json") as f:
        pass

# After:
from pathlib import Path
if Path("file.json").exists():
    with open("file.json") as f:
        pass
```

---

## Files Requiring Most Work

### Core Files (Priority 1)

1. **pogo_mcp/server.py** - ~200 violations
   - Type annotations for all MCP tools
   - Print → logging
   - Exception handling

2. **pogo_mcp/api_client.py** - ~150 violations
   - Type annotations
   - Logging f-strings → % formatting
   - Exception handling
   - Add timeouts

3. **pogo_scraper/scraper.py** - ~180 violations
   - Type annotations
   - Print → logging (keep CLI prints)
   - Path handling

### Test Files (Priority 2)

All files in `tests/` - Add per-file ignores for test-specific patterns:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["ARG001", "S101", "PLR2004"]
```

---

## Priority Workflow

### Session 1: Quick Wins (1 hour)
- Phase 1: Config fix
- Phase 2: Auto-fix
- Phase 3: Format
- **Result: 60% reduction**

### Session 2: Type Annotations (3 hours)
- Focus on core files: server.py, api_client.py, utils.py, types.py
- Add type hints to all functions
- **Result: Additional 15% reduction**

### Session 3: Error Handling (2 hours)
- Replace blind except with specific exceptions
- Fix logging f-strings
- Add timeouts
- **Result: Additional 10% reduction**

### Session 4: Code Quality (2 hours)
- Path handling
- Import cleanup
- Remove unused code
- **Result: Additional 10% reduction**

---

## Key Commands Reference

```bash
# Check all
python -m ruff check .

# Auto-fix
python -m ruff check --fix .

# Format
python -m ruff format .

# Statistics
python -m ruff check --statistics .

# Specific rule
python -m ruff check --select ANN001 .

# Specific file
python -m ruff check pogo_mcp/server.py

# Check format
python -m ruff format --check .
```

---

## Recommended Configuration

After fixes, use this in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "ANN", "S", "BLE", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "PERF", "FURB", "LOG", "RUF"]
ignore = ["S101", "PLR0913", "PLR0912", "PLR0915", "COM812", "ISC001"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["ARG001", "S101", "PLR2004"]
"pogo_scraper/**/*.py" = ["T201"]  # Allow print for CLI
".claude/skills/**/*.py" = ["T201"]  # CLI scripts
```

---

## Validation Checklist

After remediation:

```bash
# 1. No Ruff errors
python -m ruff check .
# Goal: 0 errors (or acceptable ignores)

# 2. Formatted correctly
python -m ruff format --check .
# Goal: "No changes needed"

# 3. Type checking
pyright
# Goal: No type errors

# 4. Tests pass
pytest
# Goal: All tests pass
```

---

## Notes

- **Don't fix everything at once** - Use phased approach
- **Commit after each phase** - Easy rollback
- **Focus on core files first** - Maximize impact
- **Tests can have different rules** - Use per-file ignores
- **Some long lines are OK** - Use inline ignore: `# noqa: E501`
- **Print in scraper is OK** - It's a CLI tool

---

**Full Details:** See `RUFF_REMEDIATION_PLAN.md` for comprehensive step-by-step guide.
