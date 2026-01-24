# Claude Code Headless/Agent SDK Reference

Official documentation from [code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless).

## Basic Usage

Add the `-p` (or `--print`) flag to any `claude` command to run it non-interactively:

```bash
claude -p "What does the auth module do?"
```

## Key Flags for Claudius Loops

| Flag | Purpose |
| --- | --- |
| `-p`, `--print` | Non-interactive output mode (required for programmatic usage) |
| `--dangerously-skip-permissions` | Skip all permission prompts (use with caution) |
| `--no-session-persistence` | Sessions not saved to disk, cannot be resumed |
| `--allowedTools` | Auto-approve specific tools (e.g., `"Bash,Read,Edit"`) |
| `--output-format` | Control output: `text` (default), `json`, `stream-json` |
| `--json-schema` | Get validated JSON output matching a schema |
| `--continue`, `-c` | Continue most recent conversation |
| `--resume`, `-r` | Resume specific session by ID or name |

## Examples

### Auto-approve tools
```bash
claude -p "Run tests and fix failures" --allowedTools "Bash,Read,Edit"
```

### Git operations with specific tool allowances
```bash
claude -p "Create appropriate commit" \
  --allowedTools "Bash(git diff:*),Bash(git log:*),Bash(git status:*),Bash(git commit:*)"
```

### Append custom instructions
```bash
claude -p "Review code" \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities."
```

### Continue conversations
```bash
# First request
claude -p "Review for performance issues"

# Continue
claude -p "Now focus on database queries" --continue

# Or continue specific session
session_id=$(claude -p "Start review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

### Get structured output
```bash
# JSON output
claude -p "Summarize project" --output-format json

# JSON with schema validation
claude -p "Extract function names" --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

## Correct Command Format for Claudius Loops

```bash
claude --no-session-persistence --dangerously-skip-permissions -p "prompt"
```

**Flag order matters:**
1. `--no-session-persistence` - Disable persistence
2. `--dangerously-skip-permissions` - Auto-approve all actions
3. `-p` - Print mode
4. `prompt` - The actual prompt

## Permission Rule Syntax

The `--allowedTools` flag uses permission rule syntax:

| Pattern | Meaning |
| --- | --- |
| `Bash` | Allows all bash commands |
| `Bash(git:*)` | Allows git commands only (with any args) |
| `Bash(git diff:*)` | Allows only `git diff` with any args |
| `Bash(git commit:*)` | Allows only `git commit` with any args |
| `Read` | Allows file reading |
| `Edit` | Allows file editing |

The `:*` suffix enables prefix matching.
