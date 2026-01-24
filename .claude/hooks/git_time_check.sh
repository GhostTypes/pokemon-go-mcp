#!/bin/bash
# PreToolUse hook for git commands - shows time before git operations
# Reads JSON from stdin, checks if Bash command contains "git"

# Read the input JSON
INPUT=$(cat)

# Extract tool name and command
TOOL=$(echo "$INPUT" | grep -o '"tool_name":"[^"]*"' | cut -d'"' -f4)

if [ "$TOOL" = "Bash" ]; then
    # Extract the command from tool_input
    COMMAND=$(echo "$INPUT" | grep -o '"command":"[^"]*"' | head -1 | cut -d'"' -f4)

    # Check if command contains "git"
    if echo "$COMMAND" | grep -q "git"; then
        # Run the time reminder
        CONTEXT="Git Command"
        python "$CLAUDE_PROJECT_DIR/.claude/skills/get-time/scripts/get_time.py" "datetime" "America/New_York" 2>/dev/null | sed "s/^/🕐 [$CONTEXT] Current time: /"
    fi
fi

exit 0
