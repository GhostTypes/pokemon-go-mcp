# Universal MCP Test Patterns

Language-agnostic patterns for testing MCP servers. Apply these regardless of whether you're using Python, TypeScript, or the Inspector CLI.

## Pattern 1: Tool Discovery Validation

**Purpose**: Verify all expected tools are registered and discoverable.

**What to Test**:
- All expected tools appear in `tools/list` response
- No unexpected tools are present (if strict)
- Each tool has a name and description
- Tool schemas are valid

**Example Assertions**:
```
GIVEN the MCP server is running
WHEN I call tools/list
THEN the response contains tools: ["add", "subtract", "multiply"]
AND each tool has a non-empty description
AND each tool has an inputSchema
```

**Common Issues**:
- Tool not registered (typo in decorator/registration)
- Tool registered but not exported
- Duplicate tool names

---

## Pattern 2: Happy Path Execution

**Purpose**: Verify each tool works correctly with valid inputs.

**What to Test**:
- Tool accepts valid inputs
- Tool returns expected output
- Output format matches specification
- Response time is acceptable

**Example Assertions**:
```
GIVEN the MCP server is running
WHEN I call tool "add" with arguments {a: 5, b: 3}
THEN the response contains content with text "8"
AND isError is false or undefined
```

**Test Data Guidelines**:
- Use realistic, representative inputs
- Include boundary values (min, max, zero)
- Test with different data types if applicable
- Document why specific values were chosen

---

## Pattern 3: Input Validation / Edge Cases

**Purpose**: Verify tools handle edge cases and invalid inputs gracefully.

**What to Test**:
- Empty inputs
- Null/undefined values
- Boundary values (very large, very small, zero)
- Wrong types (string instead of number)
- Missing required parameters
- Extra unexpected parameters

**Example Assertions**:
```
GIVEN the MCP server is running
WHEN I call tool "divide" with arguments {a: 10, b: 0}
THEN the response indicates an error
AND the error message mentions "zero" or "divide"

WHEN I call tool "greet" with arguments {}
THEN the response indicates an error about missing "name" parameter
```

**Error Response Expectations**:
- `isError: true` flag set
- Error message is actionable (tells user what to fix)
- No stack traces in production errors
- Consistent error format across tools

---

## Pattern 4: Error Response Format

**Purpose**: Verify error responses are consistent and actionable.

**What to Test**:
- Errors have consistent structure
- Error messages are human-readable
- Errors include enough context to debug
- Sensitive information is not leaked

**Example Assertions**:
```
GIVEN a tool call that will fail
WHEN the tool returns an error
THEN isError is true
AND content[0].type is "text"
AND content[0].text contains a descriptive error message
AND the message does NOT contain stack traces
AND the message does NOT contain file paths or internal details
```

**Good Error Message**:
```
"Cannot divide by zero. Please provide a non-zero divisor."
```

**Bad Error Message**:
```
"ZeroDivisionError at /home/user/server.py:42"
```

---

## Pattern 5: Concurrent Tool Calls

**Purpose**: Verify the server handles multiple simultaneous requests correctly.

**What to Test**:
- Multiple tool calls don't interfere with each other
- Responses are correctly matched to requests
- No race conditions or data corruption
- Server remains responsive under load

**Example Assertions**:
```
GIVEN the MCP server is running
WHEN I call tool "add" 10 times concurrently with arguments:
  - {a: 0, b: 0}
  - {a: 1, b: 1}
  - {a: 2, b: 2}
  ...
THEN all 10 responses are received
AND response[i] contains text equal to i + i
AND no responses are duplicated or swapped
```

**Implementation Notes**:
- Use async/parallel execution (Promise.all, asyncio.gather)
- Start with 5-10 concurrent calls
- Increase if testing high-load scenarios
- Watch for memory leaks in repeated tests

---

## Pattern 6: Stateful Operations

**Purpose**: Verify tools that maintain state work correctly across calls.

**What to Test**:
- State is properly initialized
- State persists across tool calls
- State isolation (if multiple sessions/users)
- State reset/cleanup works

**Example Assertions**:
```
GIVEN the MCP server is running
WHEN I call tool "set_counter" with {value: 10}
AND then call tool "increment_counter" with {}
THEN get_counter returns 11

GIVEN a fresh server connection
WHEN I call get_counter without setting it first
THEN it returns 0 or an appropriate default/error
```

---

## Pattern 7: Resource Testing

**Purpose**: Verify resources are properly exposed and readable.

**What to Test**:
- All expected resources appear in `resources/list`
- Resource URIs follow expected format
- Resources can be read successfully
- Resource content matches expectations

**Example Assertions**:
```
GIVEN the MCP server exposes file resources
WHEN I call resources/list
THEN the response contains resource with uri "file://config.json"

WHEN I call resources/read with uri "file://config.json"
THEN the content contains valid JSON
AND the JSON has expected keys ["version", "settings"]
```

---

## Pattern 8: Prompt Testing

**Purpose**: Verify prompts are properly exposed and can be retrieved.

**What to Test**:
- All expected prompts appear in `prompts/list`
- Prompts have proper names and descriptions
- Prompts with arguments work correctly
- Prompt content is valid

**Example Assertions**:
```
GIVEN the MCP server exposes prompts
WHEN I call prompts/list
THEN the response contains prompt named "summarize"

WHEN I call prompts/get with name "summarize" and arguments {style: "brief"}
THEN the response contains messages array
AND messages[0].role is "user" or "assistant"
AND messages[0].content is non-empty
```

---

## Test Organization Best Practices

### Group Tests Logically

```
tests/
├── test_discovery.py      # Pattern 1: Tool/Resource/Prompt discovery
├── test_tools.py          # Pattern 2-4: Individual tool tests
├── test_resources.py      # Pattern 7: Resource tests
├── test_prompts.py        # Pattern 8: Prompt tests
├── test_concurrency.py    # Pattern 5: Concurrent operations
└── test_integration.py    # Multi-step workflows
```

### Name Tests Descriptively

```python
# Good
def test_add_returns_sum_of_two_positive_integers():
def test_divide_by_zero_returns_error_message():

# Bad
def test_add():
def test_error():
```

### Use Parametrized Tests for Variations

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, "3"),
    (-1, 1, "0"),
    (0, 0, "0"),
    (100, 200, "300"),
])
def test_add(client, a, b, expected):
    result = await client.call_tool("add", {"a": a, "b": b})
    assert result.content[0].text == expected
```

### Document Test Rationale

```python
def test_handles_unicode_input():
    """
    Verify the greet tool handles Unicode names correctly.
    
    Regression test for issue #42 where Japanese characters
    caused encoding errors.
    """
    result = await client.call_tool("greet", {"name": "田中"})
    assert "田中" in result.content[0].text
```

---

## Test Data Management

### Principles

1. **Use Realistic Data**: Test with data similar to production
2. **Make Data Self-Contained**: Tests shouldn't depend on external state
3. **Document Data Assumptions**: Explain why specific values were chosen
4. **Keep Sensitive Data Out**: Use environment variables for API keys

### Fixture Pattern

```python
@pytest.fixture
def sample_users():
    """Provide sample user data for testing."""
    return [
        {"id": "user-1", "name": "Alice", "email": "alice@example.com"},
        {"id": "user-2", "name": "Bob", "email": "bob@example.com"},
    ]

async def test_lookup_user(client, sample_users):
    for user in sample_users:
        result = await client.call_tool("get_user", {"id": user["id"]})
        assert user["name"] in result.content[0].text
```

### Environment-Based Configuration

```python
import os

@pytest.fixture
def api_config():
    """Load API configuration from environment."""
    return {
        "api_key": os.environ.get("TEST_API_KEY", "test-key"),
        "base_url": os.environ.get("TEST_API_URL", "https://api.test.com"),
    }
```

---

## Assertion Guidelines

### Be Specific

```python
# Too vague - will pass for any truthy value
assert result

# Better - checks structure
assert result.content is not None
assert len(result.content) > 0

# Best - validates actual data
assert result.content[0].text == "8"
```

### Check Error Conditions Properly

```python
# Check for error indication
assert result.is_error or "error" in result.content[0].text.lower()

# Check specific error message
assert "cannot divide by zero" in result.content[0].text.lower()
```

### Use Appropriate Matchers

```python
# Exact match
assert text == "Hello, World!"

# Contains
assert "Hello" in text

# Pattern match
import re
assert re.match(r"User \d+ created", text)

# Numeric tolerance
assert abs(result - expected) < 0.001
```
