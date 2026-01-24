# Claude Code CLI Reference

Official documentation from [code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference).

## CLI Commands

| Command | Description | Example |
| --- | --- | --- |
| `claude` | Start interactive REPL | `claude` |
| `claude "query"` | Start REPL with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Query via SDK, then exit | `claude -p "explain this function"` |
| `cat file | claude -p "query"` | Process piped content | `cat logs.txt | claude -p "explain"` |
| `claude -c` | Continue most recent conversation in current directory | `claude -c` |
| `claude -c -p "query"` | Continue via SDK | `claude -c -p "Check for type errors"` |
| `claude -r "<session>" "query"` | Resume session by ID or name | `claude -r "auth-refactor" "Finish this PR"` |
| `claude update` | Update to latest version | `claude update` |

## CLI Flags

### Core Flags for Claudius Loops

| Flag | Purpose |
| --- | --- |
| `--dangerously-skip-permissions` | Skip all permission prompts (use with caution) |
| `--no-session-persistence` | Disable session persistence - sessions not saved to disk |
| `--print`, `-p` | Print response without interactive mode |
| `--continue`, `-c` | Load the most recent conversation in current directory |
| `--resume`, `-r` | Resume a specific session by ID or name |

### Tool Permission Flags

| Flag | Purpose |
| --- | --- |
| `--allowedTools` | Tools that execute without prompting (e.g., `"Bash(git log:*)" "Read" "Edit"`) |
| `--disallowedTools` | Tools removed from model's context and cannot be used |
| `--tools` | Restrict which built-in tools Claude can use (e.g., `"Bash,Edit,Read"`) |

### Output Control Flags

| Flag | Purpose |
| --- | --- |
| `--output-format` | Specify output format: `text` (default), `json`, `stream-json` |
| `--json-schema` | Get validated JSON output matching a JSON Schema |
| `--max-turns` | Limit number of agentic turns before error exit |

### System Prompt Flags

| Flag | Behavior | Modes |
| --- | --- | --- |
| `--system-prompt` | Replaces entire default prompt | Interactive + Print |
| `--system-prompt-file` | Replaces with file contents | Print only |
| `--append-system-prompt` | Appends to default prompt | Interactive + Print |
| `--append-system-prompt-file` | Appends file contents to default prompt | Print only |

## Flag Order

Correct order for autonomous loops:
```bash
claude --no-session-persistence --dangerously-skip-permissions -p "prompt"
```

**Important:** Flag order matters. `--no-session-persistence` comes before `--dangerously-skip-permissions`.
