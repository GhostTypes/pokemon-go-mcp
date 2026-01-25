# Code Quality Issues - TODO List

**Generated:** 2026-01-25
**Total Issues:** 33 Ruff linting violations
**Status:** All tests passing (167/167), code is functional but needs style cleanup

---

## Priority Legend

🔴 **HIGH** - Fix this week (before production)
🟡 **MEDIUM** - Fix next sprint
🟢 **LOW** - Technical debt, fix when convenient

---

## HIGH PRIORITY ISSUES (Fix This Week)

### 1. Line Length Violations (E501) 🔴
**Count:** 9 occurrences
**Impact:** Code readability, may fail strict CI checks

#### Files to Fix:
1. **pogo_mcp/rocket_lineups.py:430** (101 chars)
   ```python
   # BEFORE:
   return f"No type information available for {pokemon_data.get('name', pokemon_name)}."

   # AFTER:
   return (
       f"No type information available for "
       f"{pokemon_data.get('name', pokemon_name)}."
   )
   ```

2. **pogo_scraper/eggs.py:131** (90 chars)
3. **pogo_scraper/eggs.py:139** (89 chars)
4. **pogo_scraper/parsers/events/base_event.py:76** (92 chars)
5. **pogo_mcp/pokemon_types.py:82** (66 chars in logging call)
6. **tests/integration/test_rocket_tools.py:358** (99 chars)
7. **tests/integration/test_rocket_tools.py:385** (92 chars)
8. **tests/integration/test_rocket_tools.py:413** (124 chars)
9. **tests/test_egg_concatenation_fix.py** (multiple lines - see test file cleanup below)

**Fix Strategy:** Use parentheses for implicit line continuation or backslash

---

### 2. Redundant Exception Object (TRY401) 🔴
**File:** pogo_mcp/pokemon_types.py:82
**Issue:** `logger.exception()` automatically includes exception info, passing it explicitly is redundant

```python
# BEFORE:
except httpx.HTTPStatusError as e:
    logger.exception("HTTP error fetching Pokemon data for '%s': %s", pokemon_name, e)
    return None

# AFTER:
except httpx.HTTPStatusError:
    logger.exception("HTTP error fetching Pokemon data for '%s'", pokemon_name)
    return None
```

---

### 3. Import Statement Location (PLC0415) 🔴
**Count:** 2 occurrences
**Issue:** Imports should be at top-level of file, not inside functions

#### File 1: pogo_scraper/parsers/events/base_event.py:74
```python
# BEFORE:
if not dates.get("start") and not dates.get("end"):
    import logging
    logger_debug = logging.getLogger(__name__)
    logger_debug.debug("No dates found for event ID: %s (href: %s)", event_id, href)

# AFTER:
if not dates.get("start") and not dates.get("end"):
    logger.debug("No dates found for event ID: %s (href: %s)", event_id, href)
```

#### File 2: tests/test_egg_concatenation_fix.py (multiple inline imports)
- Move all imports to top of file
- See "Test File Cleanup" section below

---

## MEDIUM PRIORITY ISSUES (Fix Next Sprint)

### 4. Loop Variable Overwrite (PLW2901) 🟡
**File:** pogo_mcp/pokemon_types.py:199-200
**Issue:** Loop variable is immediately overwritten

```python
# BEFORE:
for pokemon_type in types:
    pokemon_type = pokemon_type.lower()

# AFTER:
for ptype in types:
    pokemon_type = ptype.lower()
```

---

### 5. Magic Number Constants (PLR2004) 🟡
**Count:** 7 occurrences
**Issue:** Hard-coded numbers should be named constants

#### Files:
1. **tests/integration/test_api_client_fallback.py:89** - Magic: `3`
2. **tests/test_pokemon_types.py:93** - Magic: `2`
3. **tests/test_egg_concatenation_fix.py:52** - Magic: `4`
4. **tests/test_egg_concatenation_fix.py:111** - Magic: `2`
5. **tests/test_utils.py:28** - Magic: `2026`
6. **tests/test_utils.py:30** - Magic: `24`
7. **tests/test_utils.py:186** - Magic: `2`
8. **tests/test_utils.py:205** - Magic: `3`

**Fix Strategy:**
```python
# At top of test file:
EXPECTED_COUNT = 3
DUAL_TYPE_THRESHOLD = 2
YEAR_2026 = 2026
DAY_24 = 24

# Use in tests:
assert len(result) == EXPECTED_COUNT
assert count >= DUAL_TYPE_THRESHOLD
```

---

## LOW PRIORITY ISSUES (Technical Debt)

### 6. Commented-Out Code (ERA001) 🟢
**File:** tests/test_pokemon_types.py:31
**Issue:** Commented code should be removed

```python
# REMOVE THIS LINE:
# Charizard: Fire/Flying
```

**Note:** This comment serves as documentation, so add `# noqa: ERA001` if keeping it.

---

### 7. Print Statements in Tests (T201) 🟢
**Count:** 5 occurrences
**File:** tests/test_egg_concatenation_fix.py
**Lines:** 58, 95, 103, 118, 125

**Issue:** Tests should use assertions, not print statements

**Options:**
1. Remove print statements (if for debugging)
2. Replace with proper assertions
3. Keep for documentation and add `# noqa: T201`

---

### 8. Test File Cleanup (Multiple Issues) 🟢
**File:** tests/test_egg_concatenation_fix.py
**Issues:** Line length, magic numbers, print statements, inline imports

**Recommendation:** This file appears to be a temporary debug/test file. Consider:
- **Option A:** Delete if no longer needed (was it for debugging the concatenation fix?)
- **Option B:** Clean up and move to proper test location
- **Option C:** Keep but disable with `.disabled` extension

---

## IMPROVEMENT RECOMMENDATIONS (Not Linting Issues)

### 9. Type System Enhancements 🟢
**File:** pogo_mcp/pokemon_types.py
**Suggestion:** Use TypedDict for better type safety

```python
from typing import TypedDict

class PokemonTypeData(TypedDict):
    name: str
    types: list[str]
    weaknesses: dict[str, list[str]]

async def fetch_pokemon_types(pokemon_name: str) -> PokemonTypeData | None:
    # ... implementation
```

---

### 10. Duplicate Type Chart Code 🟢
**Files:** pogo_mcp/pokemon_types.py and pogo_mcp/utils.py
**Issue:** Type effectiveness chart is duplicated in both files
**Recommendation:** Extract to shared module (pogo_mcp/type_chart.py)

**Priority:** LOW - Duplication is intentional and may need to diverge

---

### 11. Error Handling Enhancement 🟢
**File:** pogo_mcp/pokemon_types.py
**Current:** All errors return `None`
**Suggestion:** Create custom exception types for better error handling

```python
class PokemonTypeError(Exception):
    """Base exception for Pokemon type lookup failures."""

class PokemonNotFound(PokemonTypeError):
    """Pokemon not found in PokeAPI."""

class PokemonAPIError(PokemonTypeError):
    """Error communicating with PokeAPI."""
```

---

### 12. Performance Optimization 🟢
**File:** pogo_mcp/pokemon_types.py
**Current:** Unbounded dict cache
**Suggestion:** Use LRU cache with size limit

```python
from functools import lru_cache

@lru_cache(maxsize=256)
async def fetch_pokemon_types(pokemon_name: str) -> dict[str, Any] | None:
    # ... implementation

def clear_type_cache() -> None:
    fetch_pokemon_types.cache_clear()
```

**Note:** Current implementation is fine for production (~1000 Pokemon max)

---

### 13. Rate Limiting/Retry Logic 🟢
**File:** pogo_mcp/pokemon_types.py
**Issue:** No retry logic for PokeAPI rate limits
**Suggestion:** Add exponential backoff

```python
import asyncio

async def fetch_pokemon_types(pokemon_name: str, max_retries: int = 3) -> dict[str, Any] | None:
    for attempt in range(max_retries):
        try:
            # ... existing code ...
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
    return None
```

---

### 14. Input Validation Enhancement 🟢
**File:** pogo_mcp/pokemon_types.py:36
**Current:** Basic normalization (lowercase, trim, replace spaces/hyphens)
**Suggestion:** Add input sanitization

```python
import re

def normalize_pokemon_name(name: str) -> str:
    """Normalize Pokemon name for API lookup."""
    # Remove special chars except letters, numbers, hyphens
    cleaned = re.sub(r'[^\w\s-]', '', name, flags=re.UNICODE)
    # Convert to lowercase, replace spaces with hyphens
    return cleaned.lower().strip().replace(" ", "-").replace("'", "")
```

---

## QUICK FIX COMMANDS

### Auto-fix What Ruff Can:
```bash
# Fix safe issues automatically
uv run ruff check --fix .

# Fix unsafe issues (review first!)
uv run ruff check --fix --unsafe .
```

### Manual Fix Checklist:
- [ ] Fix 9 line length violations (break long lines)
- [ ] Fix 1 redundant exception object (pokemon_types.py:82)
- [ ] Fix 2 import location issues
- [ ] Fix 1 loop variable overwrite
- [ ] Define constants for 7 magic numbers
- [ ] Remove 1 commented-out code
- [ ] Remove or keep 5 print statements (decision needed)
- [ ] Decide fate of test_egg_concatenation_fix.py

---

## FILES REQUIRING CHANGES

### Modified Files (9 files):
1. pogo_mcp/rocket_lineups.py (line 430)
2. pogo_mcp/pokemon_types.py (lines 82, 199-200)
3. pogo_scraper/eggs.py (lines 131, 139)
4. pogo_scraper/parsers/events/base_event.py (lines 74, 76)
5. tests/integration/test_rocket_tools.py (lines 358, 385, 413)
6. tests/integration/test_api_client_fallback.py (line 89)
7. tests/test_pokemon_types.py (line 31, 93)
8. tests/test_egg_concatenation_fix.py (multiple lines - consider deleting)
9. tests/test_utils.py (lines 28, 30, 186, 205)

### New Files Created:
- pogo_mcp/pokemon_types.py (new module with 8 violations)
- tests/test_pokemon_types.py (new tests with 2 violations)
- tests/test_egg_concatenation_fix.py (temporary debug file with 14 violations)

---

## TESTING AFTER FIXES

After fixing issues, run:

```bash
# 1. Check Ruff (should be 0 violations)
uv run ruff check pogo_mcp/ pogo_scraper/ tests/

# 2. Run tests (should all pass)
uv run pytest

# 3. Type check (if desired)
uv run pyright

# 4. Format check
uv run ruff format --check .
```

---

## SUMMARY

**Total Violations:** 33
**High Priority:** 12 (line length, redundant exception, imports)
**Medium Priority:** 8 (loop variable, magic numbers)
**Low Priority:** 13 (commented code, print statements, improvements)

**Estimated Fix Time:**
- High Priority: 30-60 minutes
- Medium Priority: 30 minutes
- Low Priority: 2-3 hours (optional improvements)

**Production Impact:** NONE - All code is functional. These are style and maintainability improvements only.
