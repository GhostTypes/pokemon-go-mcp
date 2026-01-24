# Hook Recipes

Ready-to-use hook configurations for common use cases.

## Code Formatting

### Auto-Format TypeScript with Prettier

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -qE '\\.tsx?$'; then npx prettier --write \"$file_path\" 2>/dev/null; fi; }"
          }
        ]
      }
    ]
  }
}
```

### Auto-Format Python with Black

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -q '\\.py$'; then black \"$file_path\" 2>/dev/null; fi; }"
          }
        ]
      }
    ]
  }
}
```

### Auto-Format Go with gofmt

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -q '\\.go$'; then gofmt -w \"$file_path\"; fi; }"
          }
        ]
      }
    ]
  }
}
```

### Auto-Format Rust with rustfmt

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read file_path; if echo \"$file_path\" | grep -q '\\.rs$'; then rustfmt \"$file_path\" 2>/dev/null; fi; }"
          }
        ]
      }
    ]
  }
}
```

---

## Linting

### ESLint After JavaScript/TypeScript Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read fp; if echo \"$fp\" | grep -qE '\\.[jt]sx?$'; then npx eslint --fix \"$fp\" 2>&1 || true; fi; }"
          }
        ]
      }
    ]
  }
}
```

### Ruff for Python

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read fp; if echo \"$fp\" | grep -q '\\.py$'; then ruff check --fix \"$fp\" 2>&1 || true; fi; }"
          }
        ]
      }
    ]
  }
}
```

---

## File Protection

### Block Edits to Sensitive Files

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json,sys; d=json.load(sys.stdin); p=d.get('tool_input',{}).get('file_path',''); sys.exit(2 if any(x in p for x in ['.env','.git/','secrets/','package-lock.json','yarn.lock']) else 0)\" 2>&1 || echo 'Protected file - modification blocked' >&2"
          }
        ]
      }
    ]
  }
}
```

### Block Production Config Edits

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -qE '(prod|production)' && { echo 'Cannot modify production files' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

---

## Command Logging

### Log All Bash Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"[\\(now | strftime(\"%Y-%m-%d %H:%M:%S\"))] \\(.tool_input.command)\"' >> ~/.claude/command-log.txt"
          }
        ]
      }
    ]
  }
}
```

### Log File Modifications

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"[\\(now | strftime(\"%Y-%m-%d %H:%M:%S\"))] Modified: \\(.tool_input.file_path)\"' >> ~/.claude/file-changes.txt"
          }
        ]
      }
    ]
  }
}
```

---

## Notifications

### Desktop Notification on Permission Request (Linux)

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.message' | xargs -I{} notify-send 'Claude Code' '{}'"
          }
        ]
      }
    ]
  }
}
```

### Desktop Notification (macOS)

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.message' | xargs -I{} osascript -e 'display notification \"{}\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### Slack Webhook Notification

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.message' | xargs -I{} curl -sX POST -H 'Content-type: application/json' --data '{\"text\":\"{}\"}' $SLACK_WEBHOOK_URL"
          }
        ]
      }
    ]
  }
}
```

---

## Command Validation

### Block Dangerous Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE '(rm\\s+-rf\\s+/|:(){:|dd\\s+if=|mkfs|format\\s+c:|>\\s*/dev/sd)' && { echo 'Dangerous command blocked' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

### Suggest Modern Alternatives

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | { read cmd; echo \"$cmd\" | grep -q '\\bgrep\\b' && ! echo \"$cmd\" | grep -q '|' && { echo 'Consider using rg (ripgrep) instead of grep for better performance' >&2; exit 2; }; exit 0; }"
          }
        ]
      }
    ]
  }
}
```

---

## Git Safety

### Prevent Force Push

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE 'git\\s+push.*(-f|--force)' && { echo 'Force push blocked - use --force-with-lease if necessary' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

### Prevent Commits to Main/Master

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | grep -qE 'git\\s+commit' && git branch --show-current | grep -qE '^(main|master)$' && { echo 'Cannot commit directly to main/master branch' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

---

## Testing

### Auto-Run Tests After Code Changes

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read fp; if echo \"$fp\" | grep -qE '\\.(ts|js|py)$' && ! echo \"$fp\" | grep -qE '(test|spec)\\.'; then echo 'Consider running tests for changed file'; fi; }",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## Session Management

### Load Environment on Session Start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "if [ -f .env ] && [ -n \"$CLAUDE_ENV_FILE\" ]; then grep -v '^#' .env | grep '=' >> \"$CLAUDE_ENV_FILE\"; fi"
          }
        ]
      }
    ]
  }
}
```

### Add Project Context on Session Start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"Project: '$(basename $PWD)'. Git branch: '$(git branch --show-current 2>/dev/null || echo 'none')'.\"}}'"
          }
        ]
      }
    ]
  }
}
```

---

## Prompt Validation

### Block Sensitive Information in Prompts

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.prompt' | grep -qiE '(password|secret|api.?key|token)\\s*[:=]' && { echo '{\"decision\":\"block\",\"reason\":\"Prompt appears to contain sensitive information. Please remove credentials.\"}'; } || echo '{}'"
          }
        ]
      }
    ]
  }
}
```

### Add Timestamp Context to Prompts

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Current time: $(date '+%Y-%m-%d %H:%M:%S %Z')\""
          }
        ]
      }
    ]
  }
}
```

---

## Stop Hooks (Intelligent Continuation)

### Verify All Tests Pass Before Stopping

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the session transcript. If any code was written or modified, verify that tests were run and passed. If tests failed or weren't run for new code, respond with {\"decision\":\"block\",\"reason\":\"Please run tests to verify the changes work correctly\"}. Otherwise respond with {\"decision\":\"approve\",\"reason\":\"Work complete\"}."
          }
        ]
      }
    ]
  }
}
```

### Check for Incomplete TODOs

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.stop_hook_active' | { read active; if [ \"$active\" = \"true\" ]; then exit 0; fi; grep -r 'TODO' --include='*.ts' --include='*.py' --include='*.js' . 2>/dev/null | head -5 | { read todos; if [ -n \"$todos\" ]; then echo '{\"decision\":\"block\",\"reason\":\"Found TODOs that may need addressing\"}'; else echo '{}'; fi; }; }"
          }
        ]
      }
    ]
  }
}
```
