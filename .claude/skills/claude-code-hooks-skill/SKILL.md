---
name: claude-code-hooks
description: Interactive skill for setting up Claude Code hooks in any workspace. Use when users want to configure hooks for Claude Code, create automation around tool execution, add notifications, format code automatically, protect files, validate commands, log operations, or customize Claude Code behavior. Triggers include "set up hooks", "create hook", "configure Claude Code", "add PreToolUse hook", "PostToolUse automation", "notification hook", "protect files from editing", or any request to automate Claude Code's behavior through hooks.
---

# Claude Code Hooks Setup Skill

This skill guides you through setting up Claude Code hooks with a thorough interview process to ensure the hook configuration exactly matches user requirements.

## Critical Workflow

**ALWAYS follow this interview-first approach:**

1. **Interview the user** - Never skip this step, even if they provide initial details
2. **Confirm understanding** - Summarize back what you understood
3. **Generate the hook configuration** - Create the JSON structure
4. **Safely apply to settings** - Merge with existing settings or create new

## Step 1: Interview Questions

Ask these questions to fully understand the user's needs. Ask 2-3 at a time max to avoid overwhelming them.

### Essential Questions (Always Ask)

1. **What should the hook do?**
   - "What specific action or behavior do you want to automate?"
   - "Can you describe the problem this hook should solve?"

2. **When should it trigger?**
   - "Which hook event should trigger this?" (Show the list below)
   - "Should it run for all tools or only specific ones?"

3. **What's the desired outcome?**
   - "Should it block operations, modify them, log them, or just observe?"
   - "What should happen when the hook runs successfully vs fails?"

### Hook Event Options (Present to User)

| Event | When It Runs | Common Use Cases |
|-------|--------------|------------------|
| `PreToolUse` | Before any tool executes | Block/allow tools, validate inputs, log commands |
| `PostToolUse` | After tool completes | Auto-format, lint, run tests, notify |
| `PermissionRequest` | When permission dialog shows | Auto-approve safe operations |
| `UserPromptSubmit` | When user submits prompt | Add context, validate prompts |
| `Notification` | When Claude sends notifications | Custom alerts, desktop notifications |
| `Stop` | When Claude finishes responding | Continue work, verify completion |
| `SubagentStop` | When subagent task completes | Validate subagent work |
| `PreCompact` | Before context compaction | Save state, custom summary |
| `SessionStart` | When session begins/resumes | Load context, set env vars |
| `SessionEnd` | When session ends | Cleanup, save logs |

### Matcher Questions (For PreToolUse, PostToolUse, PermissionRequest)

4. **Which tools should this affect?**
   - "Should this apply to all tools (`*`) or specific ones?"
   - Common matchers: `Bash`, `Write`, `Edit`, `Read`, `Glob`, `Grep`, `Task`, `WebFetch`, `WebSearch`
   - "You can combine with regex: `Edit|Write` matches both"

### Implementation Questions

5. **How should the hook be implemented?**
   - `command` type: Run a bash command/script
   - `prompt` type: Use LLM evaluation (only for Stop/SubagentStop)

6. **What should the hook output?**
   - Exit code 0: Success (continues normally)
   - Exit code 2: Block the operation (shows stderr to Claude)
   - JSON output: For advanced control (decisions, modified inputs)

7. **Where should this hook be stored?**
   - User settings (`~/.claude/settings.json`): Applies to all projects
   - Project settings (`.claude/settings.json`): Shared with team
   - Local settings (`.claude/settings.local.json`): Personal, not committed

### Context Questions

8. **Does the hook need project context?**
   - Scripts can use `$CLAUDE_PROJECT_DIR` for project-relative paths
   - Environment variables available to hooks

9. **Should there be a timeout?**
   - Default: 60 seconds
   - Can specify custom timeout per hook

## Step 2: Confirm Understanding

Before proceeding, summarize back:

```
Based on our discussion, here's what I'll set up:

- **Hook Event**: [event name]
- **Matcher**: [pattern or "all tools"]
- **Action**: [what the hook does]
- **Implementation**: [command/prompt and what it does]
- **Output Behavior**: [what happens on success/failure]
- **Storage Location**: [which settings file]

Does this match what you need? Any adjustments?
```

## Step 3: Generate Hook Configuration

### JSON Structure Reference

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### For Events Without Matchers

`UserPromptSubmit`, `Stop`, `SubagentStop`, `Notification`, `SessionStart`, `SessionEnd`, `PreCompact` don't use matchers:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/validator.py"
          }
        ]
      }
    ]
  }
}
```

## Step 4: Safely Apply Configuration

**CRITICAL: Never corrupt existing settings files.**

### Check for Existing Settings

```bash
# Check if settings file exists
if [ -f ".claude/settings.json" ]; then
    echo "Existing settings found"
else
    echo "No existing settings"
fi
```

### Safe Merge Strategy

1. **Read existing file** (if exists)
2. **Parse as JSON** to validate
3. **Merge hooks** - Don't overwrite, append to existing arrays
4. **Write back** with proper formatting

### Helper Script Usage

Use the provided `scripts/apply_hooks.py` script:

```bash
python3 "$SKILL_DIR/scripts/apply_hooks.py" \
    --settings-file ".claude/settings.json" \
    --hook-event "PostToolUse" \
    --matcher "Edit|Write" \
    --command "npx prettier --write \"\$(jq -r '.tool_input.file_path')\"" \
    --timeout 30
```

Or use `scripts/apply_hooks_json.py` for full JSON input:

```bash
echo '{"hooks":{"PostToolUse":[...]}}' | python3 "$SKILL_DIR/scripts/apply_hooks_json.py" --settings-file ".claude/settings.json"
```

## Common Hook Recipes

See `references/hook-recipes.md` for tested, ready-to-use configurations including:
- Code formatting (Prettier, Black, gofmt)
- File protection
- Command logging
- Desktop notifications
- Git safeguards
- Test runners
- Linting

## Hook Input/Output Reference

See `references/hook-io-reference.md` for complete documentation on:
- Input JSON schemas for each event
- Output formats (exit codes vs JSON)
- Decision control options
- Advanced JSON output fields

## Debugging Hooks

If hooks aren't working:

1. **Check registration**: Run `/hooks` in Claude Code
2. **Verify syntax**: Ensure valid JSON in settings
3. **Test commands**: Run hook command manually with sample input
4. **Check permissions**: Ensure scripts are executable
5. **Review logs**: Use `claude --debug` for detailed output
