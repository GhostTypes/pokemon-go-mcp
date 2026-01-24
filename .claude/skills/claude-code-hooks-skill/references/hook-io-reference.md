# Hook Input/Output Reference

Complete reference for Claude Code hook inputs and outputs.

## Common Input Fields (All Events)

Every hook receives JSON via stdin containing:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/conversation.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default|plan|acceptEdits|bypassPermissions",
  "hook_event_name": "EventName"
}
```

## Event-Specific Inputs

### PreToolUse Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

**Tool Input Schemas by Tool:**

| Tool | Key Fields |
|------|------------|
| `Bash` | `command`, `description` |
| `Write` | `file_path`, `content` |
| `Edit` | `file_path`, `old_string`, `new_string` |
| `Read` | `file_path`, `start_line`, `end_line` |
| `Glob` | `pattern`, `path` |
| `Grep` | `pattern`, `path`, `include` |
| `Task` | `task`, `allowed_tools` |

### PostToolUse Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

### Notification Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "Notification",
  "message": "Claude needs your permission to use Bash",
  "notification_type": "permission_prompt|idle_prompt|auth_success|elicitation_dialog"
}
```

### UserPromptSubmit Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "User's submitted prompt text"
}
```

### Stop / SubagentStop Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

**Important:** `stop_hook_active` is `true` when Claude is already continuing due to a previous stop hook. Check this to prevent infinite loops!

### PreCompact Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "PreCompact",
  "trigger": "manual|auto",
  "custom_instructions": ""
}
```

### SessionStart Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "SessionStart",
  "source": "startup|resume|clear|compact"
}
```

**Special:** SessionStart has access to `$CLAUDE_ENV_FILE` for persisting environment variables.

### SessionEnd Input

```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/project/path",
  "permission_mode": "default",
  "hook_event_name": "SessionEnd",
  "reason": "clear|logout|prompt_input_exit|other"
}
```

---

## Output Methods

### Method 1: Exit Codes (Simple)

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| `0` | Success | Continues normally; stdout shown in verbose mode |
| `2` | Block | Blocks operation; stderr fed back to Claude |
| Other | Non-blocking error | Continues; stderr shown in verbose mode |

**Exit Code 2 Behavior by Event:**

| Event | Exit Code 2 Effect |
|-------|-------------------|
| PreToolUse | Blocks tool call, shows stderr to Claude |
| PermissionRequest | Denies permission, shows stderr to Claude |
| PostToolUse | Shows stderr to Claude (tool already ran) |
| UserPromptSubmit | Blocks prompt, erases it, shows stderr to user |
| Stop/SubagentStop | Blocks stopping, shows stderr to Claude |
| Notification/PreCompact/SessionStart/SessionEnd | Shows stderr to user only |

### Method 2: JSON Output (Advanced)

JSON output is only processed with exit code 0. For exit code 2, only stderr is used.

#### Common JSON Fields

```json
{
  "continue": true,
  "stopReason": "Message when continue is false",
  "suppressOutput": false,
  "systemMessage": "Warning shown to user"
}
```

- `continue: false` stops Claude entirely (takes precedence over other decisions)
- `stopReason` accompanies `continue: false`
- `suppressOutput: true` hides stdout from transcript
- `systemMessage` shows a warning to the user

#### PreToolUse Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Explanation",
    "updatedInput": {
      "field_to_modify": "new value"
    }
  }
}
```

- `allow`: Bypasses permission system
- `deny`: Blocks the tool call
- `ask`: Shows permission dialog to user
- `updatedInput`: Modifies tool inputs before execution

#### PermissionRequest Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow|deny",
      "updatedInput": { },
      "message": "Denial reason",
      "interrupt": false
    }
  }
}
```

#### PostToolUse Decision Control

```json
{
  "decision": "block",
  "reason": "Why blocking",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Extra info for Claude"
  }
}
```

#### UserPromptSubmit Decision Control

```json
{
  "decision": "block",
  "reason": "Why blocking (shown to user)",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Context added to conversation"
  }
}
```

**Note:** Plain text stdout with exit 0 also adds context to the conversation.

#### Stop/SubagentStop Decision Control

```json
{
  "decision": "block",
  "reason": "Why Claude must continue working"
}
```

#### SessionStart Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Context loaded at session start"
  }
}
```

---

## MCP Tool Matching

MCP tools follow the pattern `mcp__<server>__<tool>`:

- `mcp__memory__create_entities`
- `mcp__filesystem__read_file`
- `mcp__github__search_repositories`

Matcher examples:
- `mcp__memory__.*` - All memory server tools
- `mcp__.*__write.*` - Any write tool from any server

---

## Environment Variables

Available in hook commands:

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Absolute path to project root |
| `CLAUDE_CODE_REMOTE` | `"true"` if web environment, empty if local |
| `CLAUDE_ENV_FILE` | (SessionStart only) Path to persist env vars |

---

## Prompt-Based Hooks

For Stop/SubagentStop events, use LLM evaluation instead of bash:

```json
{
  "type": "prompt",
  "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks complete.",
  "timeout": 30
}
```

The LLM responds with:

```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "continue": false,
  "stopReason": "Custom stop message",
  "systemMessage": "Warning to user"
}
```
