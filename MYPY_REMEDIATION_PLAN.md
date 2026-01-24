# Mypy Type Checking Remediation Plan

**Project:** pokemon-go-mcp
**Analysis Date:** 2025-01-23
**Total Errors:** 271 errors across 9 files in `pogo_mcp/`
**Mypy Version:** 1.19.1 (configured in pyproject.toml)

---

## Executive Summary

This plan provides a comprehensive, step-by-step approach to resolving all 271 mypy errors in the `pogo_mcp/` directory. The issues are organized by priority (P0-P3) with specific code fixes, file paths, line numbers, and effort estimates.

### Error Categories

| Category | Count | Priority |
|----------|-------|----------|
| Missing type stubs | 2 | P0 |
| Bare `Dict` without parameters | 9 | P0 |
| `EventExtraData` indexing issues | 12 | P0 |
| Union type attribute access | 225+ | P1 |
| Missing type annotations | 10 | P1 |
| Missing return type annotations | 5 | P2 |
| Untyped decorators/functions | 4 | P2 |

---

## Priority Level Definitions

- **P0 (Critical):** Type system violations that must be fixed for correct type checking
- **P1 (High):** Major issues affecting type safety across the codebase
- **P2 (Medium):** Missing annotations that should be added for completeness
- **P3 (Low):** Optional improvements, nice-to-have refinements

---

## P0: Critical Issues (Foundation)

### Task 1: Install Missing Type Stubs
**Effort:** 5 minutes | **Dependencies:** None | **Files:** `pyproject.toml`

**Problem:**
```
pogo_mcp\utils.py:7: error: Library stubs not installed for "dateutil"  [import-untyped]
pogo_mcp\api_client.py:8: error: Library stubs not installed for "dateutil"  [import-untyped]
```

**Solution:**

Add `types-python-dateutil` to project dependencies:

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pyproject.toml`

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "types-python-dateutil>=2.8.0",  # ADD THIS LINE
]
```

**Verification:**
```bash
pip install types-python-dateutil
python -m mypy pogo_mcp/utils.py pogo_mcp/api_client.py
```

---

### Task 2: Fix Bare `Dict` Type Parameters in `types.py`
**Effort:** 15 minutes | **Dependencies:** None | **Files:** `pogo_mcp/types.py`

**Problem:**
Lines 26, 39-44, 68, 71 use bare `Dict` without type parameters.

**Solution:**

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pogo_mcp\types.py`

```python
# Line 26 - Change:
combat_power: Optional[Dict] = None
# To:
combat_power: Optional[Dict[str, Any]] = None

# Line 39-44 - Change all to:
generic: Optional[Dict[str, Any]] = None
communityday: Optional[Dict[str, Any]] = None
raidbattles: Optional[Dict[str, Any]] = None
raidday: Optional[Dict[str, Any]] = None
spotlight: Optional[Dict[str, Any]] = None
breakthrough: Optional[Dict[str, Any]] = None

# Line 68 - Change:
combat_power: Dict
# To:
combat_power: Dict[str, Any]

# Line 71 - Change:
extra_data: Optional[Dict] = None
# To:
extra_data: Optional[Dict[str, Any]] = None

# Line 102 in ShadowPokemonInfo - Change:
weaknesses: Dict[str, List[str]]
# Already correct, no change needed
```

**Also add `Any` import at top:**
```python
from typing import List, Dict, Optional, Union, Any  # Add Any
```

---

### Task 3: Fix `EventExtraData` Type Definition and Indexing
**Effort:** 20 minutes | **Dependencies:** Task 2 | **Files:** `pogo_mcp/types.py`, `pogo_mcp/utils.py`, `pogo_mcp/api_client.py`, `pogo_mcp/events.py`, `pogo_mcp/server.py`

**Problem:**
`EventExtraData` is a dataclass, but code tries to use it like a dictionary with `in` operator and `[]` indexing.

**Root Cause:**
`EventExtraData` should be a `TypedDict` or union type, not a dataclass.

**Solution:**

**Option A (Recommended):** Change `EventExtraData` to `TypedDict`

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pogo_mcp\types.py`

```python
from typing import List, Dict, Optional, Union, Any, TypedDict  # Add TypedDict

# Replace the EventExtraData dataclass (lines 37-44) with:
class EventExtraData(TypedDict, total=False):
    """Additional event-specific data - all fields optional"""
    generic: Optional[Dict[str, Any]]
    communityday: Optional[Dict[str, Any]]
    raidbattles: Optional[Dict[str, Any]]
    raidday: Optional[Dict[str, Any]]
    spotlight: Optional[Dict[str, Any]]
    breakthrough: Optional[Dict[str, Any]]
```

**Note:** TypedDict allows `in` operator and `[]` indexing like a regular dict.

**Option B:** If dataclass must be kept, change all usage patterns to attribute access:
```python
# Instead of: "communityday" in event.extra_data
# Use: event.extra_data.communityday is not None
```

**This option requires extensive changes across multiple files.**

**Recommendation:** Use Option A (TypedDict) for 12+ error fixes in one change.

---

## P1: High Priority Issues (Type Safety)

### Task 4: Fix Union Type Attribute Access in `server.py`
**Effort:** 2 hours | **Dependencies:** Task 3 | **Files:** `pogo_mcp/server.py`

**Problem:**
225+ errors from accessing attributes on unions without proper type narrowing.

**Root Cause:**
The function `get_all_data()` returns a dict with lists of different types, but iteration doesn't narrow types properly.

**Solution:**

**Pattern 1: Type narrowing with `isinstance()`**

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pogo_mcp\server.py`

Lines 54-63 (and similar patterns throughout):

```python
# BEFORE (lines 54-63):
for event in all_data["events"]:
    if event.extra_data and "communityday" in event.extra_data:
        cd_data = event.extra_data["communityday"]
        for shiny in cd_data.get("shinies", []):
            name = shiny.get("name", "")
            if name:
                shiny_pokemon.add(name)
                if name not in sources:
                    sources[name] = []
                sources[name].append(f"Event: {event.name}")

# AFTER:
from typing import cast, Dict, Any

for event in all_data["events"]:
    # Type narrow: we know this is EventInfo from get_all_data()
    assert isinstance(event, EventInfo), f"Expected EventInfo, got {type(event)}"

    if event.extra_data and "communityday" in event.extra_data:
        cd_data = event.extra_data["communityday"]
        if cd_data:  # Add None check
            for shiny in cd_data.get("shinies", []):
                name = shiny.get("name", "")
                if name:
                    shiny_pokemon.add(name)
                    if name not in sources:
                        sources[name] = []
                    sources[name].append(f"Event: {event.name}")
```

**Pattern 2: Use specific iteration variables**

**Lines 50-51:**
```python
# Change:
sources = {}

# To:
sources: Dict[str, List[str]] = {}
```

**Pattern 3: Create typed helper functions**

Add after imports in `server.py`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ApiData

def get_typed_data(data: Dict[str, Any], key: str, expected_type: type) -> list:
    """Safely extract and type-cast data from the unified data dict."""
    items = data.get(key, [])
    if TYPE_CHECKING:
        # Static type checker knows these are the right types
        return cast(list[expected_type], items)
    return items  # Runtime: just return as-is
```

Then use:
```python
events = get_typed_data(all_data, "events", EventInfo)
raids = get_typed_data(all_data, "raids", RaidInfo)
research = get_typed_data(all_data, "research", ResearchTaskInfo)
eggs = get_typed_data(all_data, "eggs", EggInfo)
rocket_lineups = get_typed_data(all_data, "rocket_lineups", RocketTrainerInfo)
promo_codes = get_typed_data(all_data, "promo_codes", PromoCodeInfo)
```

**Specific fixes by line ranges:**

**Lines 63-71 (Raids):**
```python
# Add type assertion
for raid in all_data["raids"]:
    assert isinstance(raid, RaidInfo)
    if raid.can_be_shiny:
        shiny_pokemon.add(raid.name)
        # ... rest of code
```

**Lines 74-80 (Research):**
```python
for task in all_data["research"]:
    assert isinstance(task, ResearchTaskInfo)
    for reward in task.rewards:
        # ... rest of code
```

**Lines 82-88 (Eggs):**
```python
for egg in all_data["eggs"]:
    assert isinstance(egg, EggInfo)
    if egg.can_be_shiny:
        shiny_pokemon.add(egg.name)
        # ... rest of code
```

**Lines 90-99 (Rocket):**
```python
for trainer in all_data.get("rocket_lineups", []):
    assert isinstance(trainer, RocketTrainerInfo)
    for slot in trainer.lineups:
        # ... rest of code
```

**Repeat pattern for all functions:**
- `search_pokemon_everywhere()` (lines 122-215)
- `get_daily_priorities()` (lines 276-361)
- `get_event_details()` (lines 364-424)

---

### Task 5: Fix `api_client.py` Type Annotations
**Effort:** 30 minutes | **Dependencies:** None | **Files:** `pogo_mcp/api_client.py`

**Problem:**
Lines 26, 33, 45, 213, 269, 271, 375

**Solution:**

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pogo_mcp\api_client.py`

**Line 26:**
```python
# Change:
self._cache: Dict[str, List[Dict]] = {}
# To:
self._cache: Dict[str, List[Dict[str, Any]]] = {}
```

**Line 33:**
```python
# Change:
def _load_local_data(self, endpoint: str) -> List[Dict]:
# To:
def _load_local_data(self, endpoint: str) -> List[Dict[str, Any]]:
```

**Line 45:**
```python
# The function returns data from json.load(), add type annotation
# Change line 33 return type and line 45
def _load_local_data(self, endpoint: str) -> List[Dict[str, Any]]:
    # ... existing code ...
    with open(local_file, 'r', encoding='utf-8') as f:
        data: List[Dict[str, Any]] = json.load(f)
        return data
```

**Line 50:**
```python
# Change:
async def _fetch_data(self, endpoint: str) -> List[Dict]:
# To:
async def _fetch_data(self, endpoint: str) -> List[Dict[str, Any]]:
```

**Line 213:**
```python
# Find the line creating RocketTrainerInfo with type field
# Change:
type=trainer_data.get("type"),
# To:
type=trainer_data.get("type", "unknown"),  # Provide default
```

**Lines 269, 271:**
```python
# Similar to Task 3, ensure EventExtraData is TypedDict
# Or use attribute access if kept as dataclass
```

**Line 375:**
```python
# Find: def _clear_cache(self):
# Change to:
def _clear_cache(self) -> None:
    self._cache.clear()
    self._cache_timestamp.clear()
```

---

### Task 6: Fix `utils.py` Type Issues
**Effort:** 20 minutes | **Dependencies:** Task 3 | **Files:** `pogo_mcp/utils.py`

**Problem:**
Lines 21, 282, 285, 297, 300

**Solution:**

**File:** `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\pogo_mcp\utils.py`

**Line 21:**
```python
# Find the function returning datetime
# Add explicit type cast:
from dateutil import parser as dateutil_parser
from typing import cast

def parse_datetime(date_str: str) -> Optional[datetime]:
    try:
        return cast(datetime, dateutil_parser.parse(date_str))
    except (ValueError, TypeError):
        return None
```

**Lines 280-292 (extract_community_day_info):**
```python
def extract_community_day_info(event: EventInfo) -> Optional[Dict[str, Any]]:
    """Extract Community Day specific information from an event."""
    if not event.extra_data:
        return None

    # After Task 3, EventExtraData is TypedDict, so this works:
    if "communityday" not in event.extra_data:
        return None

    cd_data = event.extra_data["communityday"]
    if cd_data is None:
        return None

    return {
        "featured_pokemon": [spawn.get("name") for spawn in cd_data.get("spawns", [])],
        "bonuses": [bonus.get("text") for bonus in cd_data.get("bonuses", [])],
        "shiny_available": [shiny.get("name") for shiny in cd_data.get("shinies", [])],
        "special_research": cd_data.get("specialresearch", [])
    }
```

**Lines 295-308 (extract_raid_day_info):**
```python
def extract_raid_day_info(event: EventInfo) -> Optional[Dict[str, Any]]:
    """Extract Raid Day specific information from an event."""
    if not event.extra_data:
        return None

    if "raidday" not in event.extra_data:
        return None

    rd_data = event.extra_data["raidday"]
    if rd_data is None:
        return None

    return {
        "raid_bosses": [boss.get("name") for boss in rd_data.get("bosses", [])],
        "bonuses": [bonus.get("text") for bonus in rd_data.get("bonuses", [])],
        "ticket_bonuses": [bonus.get("text") for bonus in rd_data.get("ticketBonuses", [])],
        "research": rd_data.get("research", []),
        "shiny_available": [shiny.get("name") for shiny in rd_data.get("shinies", [])]
    }
```

---

### Task 7: Fix Variable Type Annotations
**Effort:** 15 minutes | **Dependencies:** None | **Files:** Multiple

**Problem:**
Variables need explicit type annotations.

**Solution:**

**File:** `pogo_mcp/rocket_lineups.py` line 40:
```python
# Change:
grunts_by_type = {}
# To:
grunts_by_type: dict[str, list[RocketTrainerInfo]] = {}
```

**File:** `pogo_mcp/raids.py` lines 36, 119, 276:
```python
# Change all instances of:
tiers = {}
# To:
tiers: dict[str, list[RaidInfo]] = {}
```

**File:** `pogo_mcp/eggs.py` lines 52, 148, 234:
```python
# Change:
egg_types = {}
# To:
egg_types: dict[str, list[EggInfo]] = {}
```

**File:** `pogo_mcp/eggs.py` line 395:
```python
# Change:
distances = {}
# To:
distances: dict[str, list[EggInfo]] = {}
```

**File:** `pogo_mcp/server.py` line 51:
```python
# Change:
sources = {}
# To:
sources: dict[str, list[str]] = {}
```

---

## P2: Medium Priority Issues (Completeness)

### Task 8: Add Missing Return Type Annotations
**Effort:** 15 minutes | **Dependencies:** None | **Files:** `pogo_mcp/server.py`, `pogo_mcp/api_client.py`, `pogo_mcp/promo_codes.py`

**Solution:**

**File:** `pogo_mcp/server.py`

**Line 36:**
```python
# Change:
def register_cross_cutting_tools():
# To:
def register_cross_cutting_tools() -> None:
```

**Line 493:**
```python
# Find the function and add -> None
```

**File:** `pogo_mcp/api_client.py`

**Line 375:**
```python
# Change:
def _clear_cache(self):
# To:
def _clear_cache(self) -> None:
```

**File:** `pogo_mcp/promo_codes.py`

**Line 14:**
```python
# Find the function and add return type
def register_promo_code_tools(mcp: FastMCP) -> None:
```

---

### Task 9: Fix Untyped Functions and Decorators
**Effort:** 20 minutes | **Dependencies:** Task 8 | **Files:** `pogo_mcp/promo_codes.py`, `pogo_mcp/server.py`

**Problem:**
Untyped decorator makes functions untyped.

**Solution:**

**File:** `pogo_mcp/promo_codes.py`

```python
from typing import Any
from fastmcp import FastMCP

def register_promo_code_tools(mcp: FastMCP) -> None:
    """Register promo code related tools."""

    @mcp.tool()
    async def get_active_promo_codes() -> str:
        """Get all currently active Pokemon Go promo codes.

        Returns the latest promo codes with their rewards and expiration dates.
        """
        # ... existing code ...
```

**File:** `pogo_mcp/server.py`

**Line 503-505:**
```python
# Ensure all register functions have proper type annotations
def register_promo_code_tools(mcp: FastMCP) -> None:
    # ... existing code ...

def register_cross_cutting_tools() -> None:
    # ... existing code ...

# Then the calls are fine:
register_promo_code_tools(mcp)
register_cross_cutting_tools()
```

**Line 526:**
```python
# The main() function needs return type
def main() -> None:
    # ... existing code ...
```

---

## P3: Low Priority Improvements

### Task 10: Add Type Stub for FastMCP (Optional)
**Effort:** 30 minutes | **Dependencies:** None

**Problem:**
FastMCP may not have complete type stubs.

**Solution:**
Create a stub file or check if newer version has types.

**File:** `pogo_mcp/stubs/fastmcp.pyi` (if needed)

---

## Execution Order

Execute tasks in this order:

1. **Task 1** - Install type stubs (5 min)
2. **Task 2** - Fix bare Dict in types.py (15 min)
3. **Task 3** - Fix EventExtraData to TypedDict (20 min)
4. **Task 5** - Fix api_client.py types (30 min)
5. **Task 6** - Fix utils.py types (20 min)
6. **Task 7** - Add variable type annotations (15 min)
7. **Task 4** - Fix union type access in server.py (2 hours)
8. **Task 8** - Add missing return types (15 min)
9. **Task 9** - Fix untyped functions (20 min)
10. **Task 10** - Optional FastMCP stubs (30 min)

**Total Estimated Time:** ~4 hours

---

## Verification Commands

After each task, run:

```bash
# Check specific file
python -m mypy pogo_mcp/<file>.py

# Check entire directory
python -m mypy pogo_mcp/

# Count remaining errors
python -m mypy pogo_mcp/ 2>&1 | grep "error:" | wc -l
```

Final verification:
```bash
# Should pass with no errors
python -m mypy pogo_mcp/ --strict
```

---

## Testing Strategy

After fixing types:

1. **Run existing tests:**
   ```bash
   pytest tests/
   ```

2. **Test MCP server functionality:**
   ```bash
   uv run python server.py
   ```

3. **Test with MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector python pogo_mcp/server.py
   ```

---

## Common Patterns Reference

### Pattern 1: TypedDict for Dictionary-like Objects

```python
from typing import TypedDict, NotRequired

class MyData(TypedDict, total=False):
    field1: str
    field2: NotRequired[int]

# Usage:
data: MyData = {"field1": "value"}
if "field2" in data:
    value = data["field2"]  # Type: int
```

### Pattern 2: Type Narrowing with Assertions

```python
from typing import Union

def process(item: Union[A, B]) -> str:
    if isinstance(item, A):
        # Type narrowed to A
        return item.a_specific_field
    else:
        # Type narrowed to B
        return item.b_specific_field
```

### Pattern 3: Explicit Type Casting

```python
from typing import cast, Any

def unsafe_function() -> Any:
    return {"key": "value"}

result: Dict[str, str] = cast(Dict[str, str], unsafe_function())
```

---

## Notes

- All file paths are absolute paths from repository root: `C:\Users\Cope\Documents\GitHub\pokemon-go-mcp\`
- The `pogo_scraper/` directory was not analyzed due to import issues mentioned
- Focus is on `pogo_mcp/` directory which contains the MCP server
- Some changes may require runtime testing after type fixes
- Consider running `mypy --install-types` to auto-install missing stubs

---

## Appendix: Quick Reference

### Type Parameters for Common Types

| Bare Type | Parameterized Type | Usage |
|-----------|-------------------|-------|
| `Dict` | `Dict[K, V]` | `Dict[str, int]` |
| `List` | `List[T]` | `List[str]` |
| `Optional` | `Optional[T]` | `Optional[str]` (alias for `Union[T, None]`) |
| `Union` | `Union[A, B, ...]` | `Union[int, str]` |
| `Any` | `Any` | Use sparingly! |

### mypy Configuration in pyproject.toml

Current config is very strict:
```toml
[tool.mypy]
strict = true
disallow_untyped_defs = true
disallow_untyped_decorators = true
```

This is good for new code but requires complete type coverage.

---

**End of Remediation Plan**
