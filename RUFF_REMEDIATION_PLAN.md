# Ruff Remediation Plan for Pokemon Go MCP Project

**Project:** pokemon-go-mcp
**Analysis Date:** 2026-01-23
**Total Violations:** 5,635 errors across 57 files
**Auto-fixable:** 3,357 (with --fix) + 527 (with --unsafe-fixes)
**Manual Fixes Required:** 1,751
**Files Needing Formatting:** 57

---

## Executive Summary

This plan provides a comprehensive, step-by-step remediation strategy for addressing 5,635 Ruff lint violations and 57 files requiring formatting. The remediation is organized into 6 phases, prioritized by impact and risk level.

### Key Issues Identified

1. **Configuration Issues (CRITICAL)**
   - Deprecated configuration format (top-level `select`/`ignore`)
   - Obsolete rules being ignored (ANN101, ANN102 - removed in Ruff)
   - Formatter conflict (COM812 rule incompatible with formatter)

2. **High-Volume Auto-Fixable Issues (3,357)**
   - 2,065: Q000 - Bad quotes in inline strings (should use double quotes)
   - 716: W293 - Blank lines with whitespace
   - 152: UP006 - Non-PEP585 type annotations
   - 129: COM812 - Missing trailing commas (CONFLICTS WITH FORMATTER)
   - 68: I001 - Unsorted imports
   - 48: RUF010 - Explicit f-string type conversion
   - 39: UP015 - Redundant open modes
   - 30: UP045 - Non-PEP604 optional annotations
   - 23: W292 - Missing newlines at end of file
   - 17: F541 - F-strings missing placeholders
   - 7: FURB105 - Print empty strings

3. **Manual Fix Requirements (1,751)**
   - 351: E501 - Line too long (>88 characters)
   - 298: ANN001 - Missing type annotations for function arguments
   - 226: T201 - Print statements (should use logging)
   - 181: ANN201 - Missing return type annotations (public functions)
   - 130: ANN202 - Missing return type annotations (private functions)
   - 138: ARG002 - Unused method arguments
   - 137: G004 - Logging using f-strings (should use % formatting)
   - 112: BLE001 - Blind except clauses (catching all exceptions)
   - 91: PLC0415 - Imports outside top level
   - 87: F401 - Unused imports
   - 68: PTH123 - builtin-open (should use Path.open)
   - 57: TRY400 - Error instances instead of Exception
   - 55: TRY300 - Try blocks that should have else clauses
   - 46: UP035 - Deprecated imports
   - 28: SLF001 - Private member access
   - 24: W291 - Trailing whitespace
   - Plus 50+ other rule categories

---

## Phase 1: Configuration Fixes (CRITICAL - Do First)

### 1.1 Update pyproject.toml Configuration

**Current Issues:**
- Top-level `select` and `ignore` are deprecated
- Ignoring obsolete rules ANN101, ANN102
- COM812 rule conflicts with formatter

**Actions Required:**

```bash
# Backup current configuration
cp pyproject.toml pyproject.toml.backup
```

**Edit pyproject.toml - Change this:**
```toml
[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "F", "W", "I", "N", "UP", "YTT", "ANN", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "PERF", "FURB", "LOG", "RUF"]
ignore = ["ANN101", "ANN102", "S101", "PLR0913", "PLR0912", "PLR0915"]
```

**To this:**
```toml
[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "YTT", "ANN", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "PERF", "FURB", "LOG", "RUF"]
ignore = [
    "S101",    # Allow assert statements
    "PLR0913", # Allow many arguments (needed for MCP tools)
    "PLR0912", # Allow many branches
    "PLR0915", # Allow many statements
    "COM812",  # Conflicts with formatter
    "ISC001",  # Conflicts with formatter
]
```

**Commands to execute:**
```bash
cd /c/Users/Cope/Documents/GitHub/pokemon-go-mcp
# Edit pyproject.toml as shown above
```

**Verification:**
```bash
python -m ruff check pyproject.toml
# Should no longer show deprecation warnings
```

---

## Phase 2: Safe Auto-Fixes (Low Risk)

These fixes are safe to apply automatically and will resolve ~2,000 violations.

### 2.1 Apply Basic Auto-Fixes

**Command:**
```bash
cd /c/Users/Cope/Documents/GitHub/pokemon-go-mcp
python -m ruff check --fix .
```

**Expected Impact:**
- Fixes: Q000, W293, UP006, I001, UP015, UP045, W292, F541, FURB105
- Estimated: 2,000+ violations resolved
- Time: 30-60 seconds

**What gets fixed:**
- Single quotes → double quotes in strings
- Whitespace on blank lines removed
- Type annotations updated to PEP 585 (e.g., `List[str]` → `list[str]`)
- Import sorting
- Redundant file modes removed (e.g., `"r"` → default read mode)
- Optional unions updated (e.g., `Optional[str]` → `str | None`)
- Missing newlines at end of files
- F-strings without placeholders converted to regular strings
- Empty print statements converted to proper form

### 2.2 Apply Unsafe Auto-Fixes (Review Required)

**Command:**
```bash
python -m ruff check --fix --unsafe-fixes .
```

**Expected Impact:**
- Additional 527 fixes
- May change code behavior - requires review
- Time: 30-60 seconds

**What gets fixed (requires manual review):**
- Bookkeeping code (e.g., unused variables)
- Certain type annotation changes
- Import reorganizations that may affect runtime

**Process:**
1. Run command
2. Review git diff: `git diff`
3. Test critical functionality
4. Commit if acceptable, revert and manually fix if not

---

## Phase 3: Format All Files

### 3.1 Apply Ruff Formatter

**Command:**
```bash
cd /c/Users/Cope/Documents/GitHub/pokemon-go-mcp
python -m ruff format .
```

**Expected Impact:**
- 57 files reformatted
- No logical changes
- Improves consistency

**Files affected (57 total):**

**Core MCP Server (11 files):**
- `pogo_mcp/__init__.py`
- `pogo_mcp/api_client.py`
- `pogo_mcp/eggs.py`
- `pogo_mcp/events.py`
- `pogo_mcp/promo_codes.py`
- `pogo_mcp/raids.py`
- `pogo_mcp/research.py`
- `pogo_mcp/rocket_lineups.py`
- `pogo_mcp/server.py`
- `pogo_mcp/types.py`
- `pogo_mcp/utils.py`

**Scraper (11 files):**
- `pogo_scraper/eggs.py`
- `pogo_scraper/events.py`
- `pogo_scraper/promo_codes.py`
- `pogo_scraper/raids.py`
- `pogo_scraper/research.py`
- `pogo_scraper/rocket_lineups.py`
- `pogo_scraper/scraper.py`
- `pogo_scraper/parsers/events/base_event.py`
- `pogo_scraper/parsers/events/comday_details.py`
- `pogo_scraper/parsers/events/generic_event_details.py`
- `pogo_scraper/parsers/events/raid_battle_details.py`
- `pogo_scraper/parsers/events/raid_day_details.py`
- `pogo_scraper/parsers/events/research_breakthrough_details.py`
- `pogo_scraper/parsers/events/spotlight_details.py`
- `pogo_scraper/parsers/events/timed_reseach_code_details.py`
- `pogo_scraper/parsers/rocket_lineups/trainer_data.py`
- `pogo_scraper/parsers/rocket_lineups/weakness_data.py`

**Tests (17 files):**
- `tests/integration/conftest.py`
- `tests/integration/test_cross_cutting_tools.py`
- `tests/integration/test_egg_tools.py`
- `tests/integration/test_event_tools.py`
- `tests/integration/test_mcp_server.py`
- `tests/integration/test_promo_code_tools.py`
- `tests/integration/test_raid_tools.py`
- `tests/integration/test_research_tools.py`
- `tests/integration/test_rocket_tools.py`
- `tests/test_egg_parsing.py`
- `tests/test_events_parsing.py`
- `tests/test_promo_codes_parsing.py`
- `tests/test_raids_parsing.py`
- `tests/test_research_parsing.py`
- `tests/test_rocket_lineups.py`
- `tests/test_timed_research_code_parsing.py`

**Scripts (3 files):**
- `scripts/generate_data_readme.py`
- `scripts/generate_test_data.py`
- `scripts/test_tools.py`

**Skills (15 files):**
- `.claude/skills/claudius-maximus/scripts/claudius_runner.py`
- `.claude/skills/mcp-test-harness/assets/python/conftest.py`
- `.claude/skills/mcp-test-harness/assets/python/test_mcp_template.py`
- `.claude/skills/mypy/scripts/clean_markdown.py`
- `.claude/skills/mypy/scripts/discover_pages.py`
- `.claude/skills/mypy/scripts/scrape_docs.py`
- `.claude/skills/ruff-dev/scripts/bulk_scrape_ruff.py`
- `.claude/skills/ruff-dev/scripts/discover_ruff_docs.py`
- `.claude/skills/ruff-dev/scripts/scrape_ruff_docs.py`
- `.claude/skills/sub-agent-creator/scripts/validate_agent.py`

**Verification:**
```bash
python -m ruff format --check .
# Should show "No changes needed"
```

---

## Phase 4: Manual Fixes by Category

After Phases 1-3, approximately 1,751 manual fixes remain. This phase organizes them by category and provides batch-processing strategies.

### 4.1 Type Annotations (Priority: HIGH)

**Violations:**
- 298: ANN001 - Missing type annotations for function arguments
- 181: ANN201 - Missing return type annotations (public functions)
- 130: ANN202 - Missing return type annotations (private functions)
- 10: ANN204 - Missing return type annotations (special methods)
- 6: ANN401 - Any type annotations
- **Total: 625 violations**

**Files requiring most work:**
- All files in `pogo_mcp/` directory
- All files in `pogo_scraper/` directory
- Test files

**Batch Strategy:**

**Step 1: Add missing argument type annotations**
```bash
# Find all functions with missing argument types
python -m ruff check --select ANN001 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
def fetch_data(endpoint):
    pass

# After:
def fetch_data(endpoint: str) -> None:
    pass
```

**Step 2: Add missing return type annotations**
```bash
python -m ruff check --select ANN201,ANN202,ANN204 --output-format=text .
```

**Example fix patterns:**
```python
# Public function:
# Before:
def get_events():
    pass

# After:
def get_events() -> List[EventInfo]:
    pass

# Private function:
# Before:
def _parse_data(data):
    pass

# After:
def _parse_data(data: Dict) -> Dict:
    pass
```

**Step 3: Replace Any with specific types**
```python
# Before:
def process(data: Any) -> Any:
    pass

# After:
def process(data: Dict[str, str]) -> List[str]:
    pass
```

**Priority files for type annotations:**
1. `pogo_mcp/server.py` - Public MCP tool functions
2. `pogo_mcp/api_client.py` - Data access methods
3. `pogo_mcp/utils.py` - Utility functions
4. `pogo_scraper/scraper.py` - Scraper interface

### 4.2 Logging and Print Statements (Priority: MEDIUM)

**Violations:**
- 226: T201 - Print statements (use logging instead)
- 137: G004 - Logging with f-strings (use % formatting)
- **Total: 363 violations**

**Why fix:** Print statements in library code are inappropriate; logging with f-strings has performance implications.

**Batch Strategy:**

**Step 1: Replace print with logging**
```bash
# Find all print statements
python -m ruff check --select T201 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
print("Loading data...")
print(f"Error: {error}", file=sys.stderr)

# After:
logger.info("Loading data...")
logger.error("Error: %s", error)
```

**Files with most print statements:**
- `pogo_scraper/scraper.py`
- `.claude/skills/claudius-maximus/scripts/claudius_runner.py`
- Various scraper parser files

**Step 2: Fix logging f-strings**
```bash
python -m ruff check --select G004 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
logger.info(f"Loaded {len(data)} items")
logger.error(f"Error loading data: {error}")

# After:
logger.info("Loaded %d items", len(data))
logger.error("Error loading data: %s", error)
```

**Important:** Do NOT use lazy interpolation for expensive operations:
```python
# Good:
logger.debug("Data: %s", json.dumps(data))

# Bad (evaluates even if debug disabled):
logger.debug(f"Data: {json.dumps(data)}")
```

**Special case for scraper command-line output:**
Scraper files that are run as scripts may legitimately use `print()` for user-facing output. These can be ignored with inline comments:

```python
# Command-line output - not logging
print(f"Scraped {len(events)} events")  # noqa: T201
```

### 4.3 Path Handling (Priority: MEDIUM)

**Violations:**
- 68: PTH123 - builtin-open (use Path.open)
- 17: PTH118 - os.path.join
- 15: PTH120 - os.path.dirname
- 12: PTH110 - os.path.exists
- 10: PTH109 - os.getcwd
- 9: PTH103 - os.makedirs
- 7: PTH100 - os.path.abspath
- **Total: 138 violations**

**Why fix:** `pathlib.Path` is more modern, cross-platform, and type-safe.

**Batch Strategy:**

**Step 1: Replace os.path with Path**
```bash
python -m ruff check --select PTH --output-format=text .
```

**Example fix patterns:**
```python
# Before:
import os
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
path = os.path.join("data", "file.json")
dirname = os.path.dirname(path)

# After:
from pathlib import Path
if Path("data.json").exists():
    with open("data.json", "r") as f:  # or Path("data.json").open("r")
        data = json.load(f)
path = Path("data") / "file.json"
dirname = path.parent
```

**Priority files:**
1. `pogo_mcp/api_client.py` - Already uses Path, but may have missed spots
2. `pogo_scraper/scraper.py` - File operations
3. `pogo_scraper/parsers/` - File path handling

### 4.4 Exception Handling (Priority: HIGH)

**Violations:**
- 112: BLE001 - Blind except (catching all exceptions)
- 57: TRY400 - Using Exception instance instead of Exception class
- 55: TRY300 - Try blocks that should have else clauses
- 7: TRY301 - Raise within try (should use else)
- 2: TRY002 - Raise vanilla Exception class
- 1: S110 - Try-except-pass
- **Total: 234 violations**

**Why fix:** Poor exception handling hides bugs and makes debugging difficult.

**Batch Strategy:**

**Step 1: Fix blind except clauses**
```bash
python -m ruff check --select BLE001 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
try:
    data = json.load(f)
except:
    logger.error("Failed to load data")

# After (specific exception):
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    logger.error("Failed to load data: %s", e)
except IOError as e:
    logger.error("Failed to read file: %s", e)
```

**Step 2: Use Exception classes instead of instances**
```bash
python -m ruff check --select TRY400 --output-format-text .
```

**Example fix pattern:**
```python
# Before:
try:
    process()
except Exception as e:
    raise e  # Bad - just re-raises

# After:
try:
    process()
except Exception:
    raise  # Better - preserves stack trace
```

**Step 3: Add else clauses to try blocks**
```bash
python -m ruff check --select TRY300 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
try:
    data = load_data()
    if not data:
        return None
    process(data)
except ValueError:
    logger.error("Invalid data")

# After:
try:
    data = load_data()
    if not data:
        return None
except ValueError:
    logger.error("Invalid data")
else:
    # Only runs if no exception
    process(data)
```

**Priority files:**
1. `pogo_mcp/api_client.py` - Data loading error handling
2. `pogo_scraper/scraper.py` - Network and file error handling
3. All scraper parser files - HTML parsing error handling

### 4.5 Imports and Unused Code (Priority: LOW)

**Violations:**
- 87: F401 - Unused imports
- 91: PLC0415 - Import outside top level
- 46: UP035 - Deprecated imports
- 4: INP001 - Implicit namespace packages
- 1: E402 - Import not at top of file
- **Total: 229 violations**

**Batch Strategy:**

**Step 1: Remove unused imports**
```bash
python -m ruff check --select F401 --fix .
# Most will be auto-fixed, but verify carefully
```

**Step 2: Fix deprecated imports**
```bash
python -m ruff check --select UP035 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
from typing import Dict, List, Optional
from collections.abc import Mapping

# After (Python 3.10+):
from collections.abc import Mapping
# Dict, List, Optional can be replaced with builtin types
```

**Step 3: Move imports to top level**
```bash
python -m ruff check --select PLC0415,E402 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
def lazy_import():
    import json  # Bad - import at top
    return json.dumps({})

# After:
import json  # At module level

def lazy_import():
    return json.dumps({})
```

**Exceptions:** Imports inside functions are sometimes necessary to avoid circular imports. Use inline ignore:

```python
def get_type():
    from .types import MyType  # noqa: PLC0415 - avoid circular import
    return MyType
```

### 4.6 Code Quality and Style (Priority: MEDIUM)

**Violations:**
- 138: ARG002 - Unused method arguments
- 11: ARG001 - Unused function arguments
- 29: PLR2004 - Magic value comparisons
- 8: B007 - Unused loop control variables
- 3: F841 - Unused variables
- 2: RUF059 - Unused unpacked variables
- 9: SIM102 - Collapsible if statements
- 5: SIM103 - Needless bool
- 1: SIM108 - If-else instead of if-exp
- 1: SIM114 - If with same arms
- **Total: ~200 violations**

**Batch Strategy:**

**Step 1: Remove unused arguments**
```bash
python -m ruff check --select ARG --output-format=text .
```

**Example fix pattern:**
```python
# Before:
def process(data, unused_param):
    return data.upper()

# After:
def process(data):
    return data.upper()

# Or if part of interface:
def process(data, unused_param):  # noqa: ARG002
    return data.upper()
```

**Step 2: Extract magic values**
```bash
python -m ruff check --select PLR2004 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
if tier == "5":
    pass

# After:
MEGA_RAID_TIER = "5"
if tier == MEGA_RAID_TIER:
    pass
```

**Step 3: Simplify conditional logic**
```bash
python -m ruff check --select SIM --output-format=text .
```

**Example fix patterns:**
```python
# SIM102 - Collapsible if:
# Before:
if condition:
    if other_condition:
        do_something()

# After:
if condition and other_condition:
    do_something()

# SIM103 - Needless bool:
# Before:
if is_valid == True:
    pass

# After:
if is_valid:
    pass

# SIM108 - If-else to if-exp:
# Before:
if condition:
    x = 1
else:
    x = 2

# After:
x = 1 if condition else 2
```

### 4.7 Security (Priority: HIGH)

**Violations:**
- 7: S113 - Requests without timeout
- 2: S104 - Hardcoded bind-all-interfaces
- 2: S603 - subprocess without shell=True
- 2: S607 - Start process with partial path
- 2: S110 - Try-except-pass
- **Total: 15 violations**

**Why fix:** Security vulnerabilities can be exploited in production.

**Batch Strategy:**

**Step 1: Add timeouts to requests**
```bash
python -m ruff check --select S113 --output-format=text .
```

**Example fix pattern:**
```python
# Before:
response = requests.get(url)
response = httpx.get(url)

# After:
response = requests.get(url, timeout=30)
response = httpx.get(url, timeout=30)
```

**Step 2: Avoid subprocess without shell=True**
```python
# Before:
subprocess.run(["command", "arg"])

# After:
subprocess.run(["command", "arg"], check=True)
```

**Priority files:**
- `pogo_mcp/api_client.py` - HTTP client
- `pogo_scraper/scraper.py` - HTTP requests

### 4.8 Line Length (Priority: LOW - May Require Design Changes)

**Violations:**
- 351: E501 - Line too long (>88 characters)
- **Total: 351 violations**

**Why fix:** Long lines are hard to read, but fixing them may require refactoring.

**Strategy:**

**Automatic fixes (Ruff will try):**
```bash
python -m ruff check --select E501 --fix .
# Ruff will try to break long lines
```

**Manual fix patterns:**
```python
# Before:
def process(event_data, pokemon_data, raid_data, research_data, egg_data, rocket_data):
    pass

# After:
def process(
    event_data: Dict,
    pokemon_data: Dict,
    raid_data: Dict,
    research_data: Dict,
    egg_data: Dict,
    rocket_data: Dict,
) -> None:
    pass

# Long strings:
# Before:
error_message = "Failed to load data from endpoint " + endpoint + " with status " + status

# After:
error_message = (
    f"Failed to load data from endpoint {endpoint} with status {status}"
)
```

**Note:** Some long lines are acceptable for URLs or data that shouldn't be split. Use inline ignore:

```python
long_url = "https://very-long-url.com/that/cannot/be/reasonably/broken/into/multiple/lines/without/losing/clarity"  # noqa: E501
```

### 4.9 Unused Arguments and Parameters (Priority: MEDIUM)

**Violations:**
- 138: ARG002 - Unused method arguments
- 11: ARG001 - Unused function arguments
- 28: SLF001 - Private member access (external access to _attr)
- **Total: 177 violations**

**Strategy:**

**Step 1: Review unused arguments**
```bash
python -m ruff check --select ARG --output-format=text .
```

**Decision tree for each unused argument:**
1. Is it part of an interface/protocol? → Keep with `# noqa: ARG002`
2. Is it a callback parameter? → Prefix with `_`: `def callback(_unused):`
3. Can it be removed? → Remove it
4. Should it be used? → Implement the missing logic

**Example fixes:**
```python
# Case 1: Interface requirement
def parse(self, data: Dict, _format: str):  # noqa: ARG002
    return self._parse(data)

# Case 2: Callback parameter
def handle_event(_event):
    pass  # Event not needed

# Case 3: Actually use the argument
def process(data, verbose):
    if verbose:
        print(f"Processing: {data}")
    return data.upper()
```

### 4.10 Documentation and TODOs (Priority: LOW)

**Violations:**
- 10: ERA001 - Commented out code
- 5: FIX002 - TODO comments without author
- 5: TD002 - TODO missing author
- 5: TD003 - TODO missing link
- **Total: 25 violations**

**Strategy:**

**Step 1: Remove or fix commented code**
```bash
python -m ruff check --select ERA001 --output-format=text .
```

**Action:** Either uncomment the code or remove it. Don't leave dead code.

**Step 2: Fix TODO comments**
```python
# Before:
# TODO: Implement caching
# TODO: Fix this bug

# After:
# TODO(ghosttypes): Implement caching
# TODO(ghosttypes): Fix this bug - https://github.com/user/repo/issues/123
```

---

## Phase 5: File-Specific Manual Remediation

Some files require individual attention due to specific patterns or high violation counts.

### 5.1 High-Priority Files (Core Functionality)

**Files to address first:**

1. **`pogo_mcp/server.py`** (~200 violations)
   - Add type annotations to all MCP tool functions
   - Replace print with logging
   - Fix exception handling
   - Remove unused arguments

2. **`pogo_mcp/api_client.py`** (~150 violations)
   - Add type annotations to all methods
   - Fix logging f-strings
   - Improve exception handling (specific exceptions)
   - Add timeouts to file operations

3. **`pogo_mcp/utils.py`** (~100 violations)
   - Type annotations for utility functions
   - Exception handling improvements

4. **`pogo_scraper/scraper.py`** (~180 violations)
   - Type annotations
   - Print → logging (but keep CLI output prints)
   - Path handling improvements
   - Exception handling

5. **`pogo_mcp/types.py`** (~50 violations)
   - Dataclass field type annotations
   - Remove unused imports

### 5.2 Test Files (Medium Priority)

**Strategy for test files:**
- Some violations are acceptable in tests (e.g., unused arguments in test fixtures)
- Add per-file ignores in pyproject.toml for test-specific rules:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ARG001",  # Unused arguments in test fixtures
    "S101",    # Assert statements in tests
    "PLR2004", # Magic values in tests
]
```

**Test files to address:**
- All `tests/integration/test_*.py` files
- All `tests/test_*.py` files

### 5.3 Skill Scripts (Low Priority)

**Files:** `.claude/skills/*/scripts/*.py`

**Strategy:**
- These are standalone scripts
- May have different requirements than library code
- Consider adding per-file ignores for script-specific patterns

```toml
[tool.ruff.lint.per-file-ignores]
".claude/skills/**/*.py" = [
    "T201",    # Print statements in CLI scripts
]
```

---

## Phase 6: Final Validation

### 6.1 Run Complete Quality Checks

After completing all phases, run this validation suite:

```bash
cd /c/Users/Cope/Documents/GitHub/pokemon-go-mcp

# 1. Check for remaining Ruff violations
python -m ruff check .
# Goal: 0 errors (or only acceptable ignores)

# 2. Verify formatting
python -m ruff format --check .
# Goal: "No changes needed"

# 3. Run MyPy type checking
pyright
# Goal: No type errors

# 4. Run tests
pytest
# Goal: All tests pass

# 5. Check for remaining issues
python -m ruff check --statistics .
# Review any remaining violations by category
```

### 6.2 Create Pre-Commit Hook

**File:** `.git/hooks/pre-commit` (or use pre-commit framework)

```bash
#!/bin/bash
# Pre-commit hook for Pokemon Go MCP

echo "Running Ruff linter..."
python -m ruff check .
if [ $? -ne 0 ]; then
    echo "Ruff linting failed. Please fix issues before committing."
    exit 1
fi

echo "Running Ruff formatter check..."
python -m ruff format --check .
if [ $? -ne 0 ]; then
    echo "Code needs formatting. Run: ruff format ."
    exit 1
fi

echo "Running MyPy type checker..."
pyright
if [ $? -ne 0 ]; then
    echo "Type checking failed. Please fix type errors."
    exit 1
fi

echo "Running tests..."
pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix failing tests."
    exit 1
fi

echo "All quality checks passed!"
```

**Install:**
```bash
chmod +x .git/hooks/pre-commit
```

---

## Execution Timeline

### Estimated Time Commitment

- **Phase 1 (Config):** 15 minutes
- **Phase 2 (Auto-fix):** 30 minutes (including review)
- **Phase 3 (Format):** 10 minutes
- **Phase 4 (Manual fixes):** 8-12 hours (spread over multiple sessions)
  - 4.1 Type annotations: 3-4 hours
  - 4.2 Logging/Prints: 2 hours
  - 4.3 Path handling: 1 hour
  - 4.4 Exceptions: 1-2 hours
  - 4.5 Imports: 1 hour
  - 4.6 Code quality: 1-2 hours
  - 4.7 Security: 30 minutes
  - 4.8 Line length: 1 hour
  - 4.9 Unused args: 30 minutes
  - 4.10 Documentation: 30 minutes
- **Phase 5 (File-specific):** 2-3 hours
- **Phase 6 (Validation):** 30 minutes

**Total:** 11-16 hours of focused work

### Recommended Execution Order

**Session 1 (Configuration & Auto-fixes - 1 hour):**
1. Phase 1: Update configuration
2. Phase 2: Apply auto-fixes
3. Phase 3: Format all files
4. Quick validation

**Session 2 (Type Annotations - 3 hours):**
1. Phase 4.1: Add type annotations to core files
2. Focus on: server.py, api_client.py, utils.py, types.py

**Session 3 (Error Handling & Logging - 2 hours):**
1. Phase 4.2: Fix print statements
2. Phase 4.4: Improve exception handling
3. Phase 4.7: Add timeouts

**Session 4 (Code Quality - 2 hours):**
1. Phase 4.3: Path handling
2. Phase 4.5: Imports
3. Phase 4.6: Code quality improvements

**Session 5 (Final Cleanup - 2 hours):**
1. Phase 4.8: Line length
2. Phase 4.9: Unused code
3. Phase 4.10: Documentation
4. Phase 5: File-specific fixes

**Session 6 (Validation - 30 minutes):**
1. Phase 6: Complete validation suite
2. Set up pre-commit hook

---

## Common Fix Patterns Reference

### Type Annotation Patterns

```python
# Function with no return
def process(data: str) -> None:
    pass

# Function returning value
def get_name() -> str:
    return "pokemon"

# Function with multiple returns
def get_pokemon(name: str) -> Optional[PokemonInfo]:
    return db.get(name)

# Async function
async def fetch_data(url: str) -> Dict[str, Any]:
    pass

# Method
class Client:
    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
```

### Exception Handling Patterns

```python
# Specific exception
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON: %s", e)
    return None

# Multiple specific exceptions
try:
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
except httpx.TimeoutError:
    logger.error("Request timed out")
except httpx.HTTPStatusError as e:
    logger.error("HTTP error: %s", e.response.status_code)

# Exception with else
try:
    data = load_data()
    if not data:
        raise ValueError("Empty data")
except ValueError as e:
    logger.error("Validation failed: %s", e)
else:
    process(data)  # Only runs if no exception
```

### Logging Patterns

```python
# Good logging
logger.info("Processing %d items", len(items))
logger.error("Failed to connect: %s", error)
logger.debug("Data: %s", json.dumps(data))

# Bad (don't use f-strings in logging)
logger.info(f"Processing {len(items)} items")  # Bad
logger.error(f"Failed: {error}")  # Bad
```

### Path Handling Patterns

```python
from pathlib import Path

# Reading files
data_path = Path("data") / "events.json"
if data_path.exists():
    with data_path.open("r") as f:
        data = json.load(f)

# Writing files
output_path = Path("output") / "results.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(results))

# Path operations
file_path = Path("/path/to/file.json")
parent = file_path.parent
name = file_path.stem
ext = file_path.suffix
```

---

## Appendix A: Quick Reference Commands

```bash
# Check all violations
python -m ruff check .

# Check specific rules
python -m ruff check --select ANN001,ANN201 .

# Check specific file
python -m ruff check pogo_mcp/server.py

# Auto-fix
python -m ruff check --fix .

# Unsafe fixes
python -m ruff check --fix --unsafe-fixes .

# Format
python -m ruff format .

# Check format without changes
python -m ruff format --check .

# Statistics
python -m ruff check --statistics .

# Per-rule breakdown
python -m ruff check --output-format=json . | \
  python -c "import sys,json; data=json.load(sys.stdin); \
  from collections import Counter; \
  counts=Counter(item['code'] for item in data); \
  [print(f'{code}: {count}') for code,count in counts.most_common()]"
```

---

## Appendix B: Configuration Reference

**Final pyproject.toml configuration:**

```toml
[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "W",    # pycodestyle warnings
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "YTT",  # flake8-2020
    "ANN",  # flake8-annotations
    "S",    # flake8-bandit (security)
    "BLE",  # flake8-blind-except
    "FBT",  # flake8-boolean-trap
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "COM",  # flake8-commas
    "C4",   # flake8-comprehensions
    "DTZ",  # flake8-datetimez
    "T10",  # flake8-debugger
    "EM",   # flake8-errmsg
    "EXE",  # flake8-executable
    "FA",   # flake8-future-annotations
    "ISC",  # flake8-implicit-str-concat
    "ICN",  # flake8-import-conventions
    "G",    # flake8-logging-format
    "INP",  # flake8-no-pep420
    "PIE",  # flake8-pie
    "T20",  # flake8-print
    "PYI",  # flake8-pyi
    "PT",   # flake8-pytest-style
    "Q",    # flake8-quotes
    "RSE",  # flake8-raise
    "RET",  # flake8-return
    "SLF",  # flake8-self
    "SLOT", # flake8-slots
    "SIM",  # flake8-simplify
    "TID",  # flake8-tidy-imports
    "TCH",  # flake8-type-checking
    "INT",  # flake8-gettext
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
    "TD",   # flake8-todos
    "FIX",  # flake8-fixme
    "ERA",  # eradicate (commented-out code)
    "PD",   # pandas-vet
    "PGH",  # pygrep-hooks
    "PL",   # pylint
    "TRY",  # tryceratops
    "FLY",  # flynt
    "NPY",  # numpy
    "PERF", # perflint
    "FURB", # refurb
    "LOG",  # flake8-logging
    "RUF",  # ruff-specific rules
]

ignore = [
    "S101",    # Allow assert statements
    "PLR0913", # Allow many arguments (MCP tools need them)
    "PLR0912", # Allow many branches
    "PLR0915", # Allow many statements
    "COM812",  # Conflicts with formatter
    "ISC001",  # Conflicts with formatter
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ARG001",  # Unused arguments in test fixtures
    "S101",    # Assert statements in tests
    "PLR2004", # Magic values in tests
]

".claude/skills/**/*.py" = [
    "T201",    # Print statements in CLI scripts
]

# Allow print statements in scraper (CLI tool)
"pogo_scraper/**/*.py" = [
    "T201",    # Print for user feedback
]
```

---

## Appendix C: Risk Assessment

### Low-Risk Auto-Fixes (Safe to Apply)
- Q000 - Quote style (cosmetic)
- W293 - Blank line whitespace (cosmetic)
- UP006 - Type annotation modernization (compatible)
- I001 - Import sorting (cosmetic)
- UP015 - Redundant modes (cosmetic)
- W292 - Missing newlines (cosmetic)
- Formatting changes (cosmetic)

### Medium-Risk Auto-Fixes (Review Required)
- UP045 - Optional union changes (verify behavior)
- RUF010 - F-string type conversion (verify behavior)
- F541 - F-string removal (verify not dynamic)
- FURB105 - Print empty string (verify intent)
- --unsafe-fixes flag changes

### Manual Fixes (High Risk if Not Tested)
- Type annotations (may reveal bugs)
- Exception handling (may change control flow)
- Logging changes (may affect debugging)
- Import changes (may affect runtime)
- Path handling (may break on Windows)

### Testing Recommendations

After each major fix category:
1. Run unit tests: `pytest`
2. Run integration tests: `pytest tests/integration/`
3. Test MCP server manually: `python server.py`
4. Test scraper: `python pogo_scraper/scraper.py --all`

---

## Conclusion

This remediation plan provides a structured approach to resolving 5,635 Ruff violations across 57 files. By following the phased approach, you can:

1. **Quickly reduce violations by 60%** with auto-fixes (Phases 1-3)
2. **Systematically address manual fixes** by category (Phase 4)
3. **Focus on critical files first** (Phase 5)
4. **Validate quality throughout** (Phase 6)

The estimated 11-16 hours of work will result in:
- Cleaner, more maintainable code
- Better type safety
- Improved error handling
- Consistent code style
- Security improvements

**Next Steps:**
1. Review this plan
2. Adjust priorities based on project needs
3. Begin with Phase 1 (configuration)
4. Progress through phases incrementally
5. Commit changes after each phase for easy rollback

**Remember:** You don't have to fix everything at once. Even completing Phases 1-3 will eliminate ~60% of violations and significantly improve code quality.
