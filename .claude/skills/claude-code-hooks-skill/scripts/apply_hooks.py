#!/usr/bin/env python3
"""
Apply Claude Code hooks to settings files safely.

This script safely merges hook configurations into existing settings files,
never overwriting or corrupting existing data.

Usage:
    python3 apply_hooks.py --settings-file .claude/settings.json \
        --hook-event PostToolUse \
        --matcher "Edit|Write" \
        --command "prettier --write"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_settings(filepath: Path) -> dict[str, Any]:
    """Load existing settings or return empty dict."""
    if not filepath.exists():
        return {}

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        print("Please fix the JSON syntax before adding hooks.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def save_settings(filepath: Path, settings: dict[str, Any]) -> None:
    """Save settings with proper formatting."""
    # Create parent directories if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if file exists
    if filepath.exists():
        backup_path = filepath.with_suffix(".json.backup")
        try:
            with open(filepath) as src, open(backup_path, "w") as dst:
                dst.write(src.read())
            print(f"Created backup at {backup_path}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}", file=sys.stderr)

    # Write new settings
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")  # Trailing newline

    print(f"Successfully updated {filepath}", file=sys.stderr)


def add_hook(
    settings: dict[str, Any],
    hook_event: str,
    hook_type: str,
    command: str | None = None,
    prompt: str | None = None,
    matcher: str | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    """Add a hook to settings, merging with existing hooks."""

    # Ensure hooks dict exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Ensure event array exists
    if hook_event not in settings["hooks"]:
        settings["hooks"][hook_event] = []

    # Build the hook entry
    hook_entry: dict[str, Any] = {"type": hook_type}

    if hook_type == "command" and command:
        hook_entry["command"] = command
    elif hook_type == "prompt" and prompt:
        hook_entry["prompt"] = prompt

    if timeout:
        hook_entry["timeout"] = timeout

    # Events that use matchers
    matcher_events = {"PreToolUse", "PostToolUse", "PermissionRequest"}

    if hook_event in matcher_events:
        # Find or create matcher group
        matcher_value = matcher or "*"
        matcher_group = None

        for group in settings["hooks"][hook_event]:
            existing_matcher = group.get("matcher", "*")
            if existing_matcher == matcher_value:
                matcher_group = group
                break

        if matcher_group is None:
            # Create new matcher group
            matcher_group = {"matcher": matcher_value, "hooks": []}
            settings["hooks"][hook_event].append(matcher_group)

        # Check for duplicate hooks
        for existing_hook in matcher_group.get("hooks", []):
            if (
                existing_hook.get("command") == command
                and existing_hook.get("prompt") == prompt
            ):
                print(
                    f"Hook already exists for {hook_event} with matcher '{matcher_value}'",
                    file=sys.stderr,
                )
                return settings

        # Add the hook
        if "hooks" not in matcher_group:
            matcher_group["hooks"] = []
        matcher_group["hooks"].append(hook_entry)

    else:
        # Events without matchers (UserPromptSubmit, Stop, etc.)
        # Find or create the hooks container
        hooks_container = None

        for container in settings["hooks"][hook_event]:
            if "hooks" in container:
                hooks_container = container
                break

        if hooks_container is None:
            hooks_container = {"hooks": []}
            settings["hooks"][hook_event].append(hooks_container)

        # Check for duplicate hooks
        for existing_hook in hooks_container.get("hooks", []):
            if (
                existing_hook.get("command") == command
                and existing_hook.get("prompt") == prompt
            ):
                print(f"Hook already exists for {hook_event}", file=sys.stderr)
                return settings

        hooks_container["hooks"].append(hook_entry)

    return settings


def main():
    parser = argparse.ArgumentParser(
        description="Add Claude Code hooks to settings files safely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a PostToolUse hook for formatting
  %(prog)s --settings-file .claude/settings.json \\
      --hook-event PostToolUse \\
      --matcher "Edit|Write" \\
      --command "prettier --write"

  # Add a UserPromptSubmit hook (no matcher)
  %(prog)s --settings-file .claude/settings.json \\
      --hook-event UserPromptSubmit \\
      --command "/path/to/validator.py"

  # Add a prompt-based Stop hook
  %(prog)s --settings-file .claude/settings.json \\
      --hook-event Stop \\
      --hook-type prompt \\
      --prompt "Check if all tasks complete"
""",
    )

    parser.add_argument(
        "--settings-file",
        "-f",
        required=True,
        help="Path to settings file (e.g., .claude/settings.json)",
    )

    parser.add_argument(
        "--hook-event",
        "-e",
        required=True,
        choices=[
            "PreToolUse",
            "PostToolUse",
            "PermissionRequest",
            "UserPromptSubmit",
            "Notification",
            "Stop",
            "SubagentStop",
            "PreCompact",
            "SessionStart",
            "SessionEnd",
        ],
        help="Hook event to trigger on",
    )

    parser.add_argument(
        "--hook-type",
        "-t",
        default="command",
        choices=["command", "prompt"],
        help="Hook type (default: command)",
    )

    parser.add_argument("--command", "-c", help="Command to execute (for type=command)")

    parser.add_argument(
        "--prompt",
        "-p",
        help="Prompt for LLM evaluation (for type=prompt, Stop/SubagentStop only)",
    )

    parser.add_argument(
        "--matcher",
        "-m",
        help="Tool matcher pattern (for PreToolUse, PostToolUse, PermissionRequest)",
    )

    parser.add_argument("--timeout", type=int, help="Timeout in seconds")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.hook_type == "command" and not args.command:
        parser.error("--command is required for hook-type=command")

    if args.hook_type == "prompt" and not args.prompt:
        parser.error("--prompt is required for hook-type=prompt")

    if args.hook_type == "prompt" and args.hook_event not in ("Stop", "SubagentStop"):
        parser.error("prompt hooks are only supported for Stop and SubagentStop events")

    filepath = Path(args.settings_file)

    # Load existing settings
    settings = load_settings(filepath)

    # Add the hook
    settings = add_hook(
        settings=settings,
        hook_event=args.hook_event,
        hook_type=args.hook_type,
        command=args.command,
        prompt=args.prompt,
        matcher=args.matcher,
        timeout=args.timeout,
    )

    if args.dry_run:
        print("Dry run - would write:", file=sys.stderr)
        print(json.dumps(settings, indent=2))
    else:
        save_settings(filepath, settings)
        print(f"Added {args.hook_event} hook successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
