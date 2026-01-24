#!/bin/bash
# Time reminder hook - prints current time in formatted way
# Usage: time_reminder.sh [context]

CONTEXT="${1:-Session}"
TIME_OUTPUT=$(python "$CLAUDE_PROJECT_DIR/.claude/skills/get-time/scripts/get_time.py" "datetime" "America/New_York" 2>/dev/null)

if [ -n "$TIME_OUTPUT" ]; then
    echo "🕐 [$CONTEXT] Current time: $TIME_OUTPUT"
fi

exit 0
