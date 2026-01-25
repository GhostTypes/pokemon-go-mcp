#!/usr/bin/env python3
"""
Apply Claude Code hooks from JSON input to settings files safely.

This script accepts a complete hooks JSON structure via stdin and safely
merges it into existing settings files, never overwriting or corrupting
existing data.

Usage:
    echo '{"hooks":{"PostToolUse":[...]}}' | python3 apply_hooks_json.py --settings-file .claude/settings.json

    cat hooks.json | python3 apply_hooks_json.py --settings-file .claude/settings.json
"""

import argparse
import json
import sys
from copy import deepcopy
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


def hooks_are_equal(hook1: dict[str, Any], hook2: dict[str, Any]) -> bool:
    """Check if two hooks are effectively the same."""
    # Compare type
    if hook1.get("type") != hook2.get("type"):
        return False

    # Compare command or prompt
    if hook1.get("command") != hook2.get("command"):
        return False
    if hook1.get("prompt") != hook2.get("prompt"):
        return False

    return True


def merge_hooks(existing: dict[str, Any], new_hooks: dict[str, Any]) -> dict[str, Any]:
    """
    Merge new hooks into existing settings without overwriting.

    Strategy:
    - For each event in new_hooks, merge with existing event array
    - For matcher-based events, merge hooks within matching matcher groups
    - Never remove existing hooks, only add new ones
    - Deduplicate based on command/prompt content
    """
    result = deepcopy(existing)

    if "hooks" not in result:
        result["hooks"] = {}

    input_hooks = new_hooks.get(
        "hooks", new_hooks
    )  # Accept both {hooks:{...}} and {...}

    if not isinstance(input_hooks, dict):
        print("ERROR: Invalid hooks structure", file=sys.stderr)
        sys.exit(1)

    # Events that use matchers
    matcher_events = {"PreToolUse", "PostToolUse", "PermissionRequest"}

    for event_name, event_matchers in input_hooks.items():
        if not isinstance(event_matchers, list):
            print(
                f"ERROR: Event '{event_name}' should have array value", file=sys.stderr
            )
            sys.exit(1)

        # Ensure event array exists
        if event_name not in result["hooks"]:
            result["hooks"][event_name] = []

        existing_event = result["hooks"][event_name]

        for new_matcher_group in event_matchers:
            if event_name in matcher_events:
                # Handle matcher-based events
                new_matcher = new_matcher_group.get("matcher", "*")
                new_hooks_list = new_matcher_group.get("hooks", [])

                # Find existing matcher group
                existing_matcher_group = None
                for group in existing_event:
                    if group.get("matcher", "*") == new_matcher:
                        existing_matcher_group = group
                        break

                if existing_matcher_group is None:
                    # Add new matcher group
                    existing_event.append(deepcopy(new_matcher_group))
                    print(
                        f"Added new matcher group '{new_matcher}' for {event_name}",
                        file=sys.stderr,
                    )
                else:
                    # Merge hooks into existing matcher group
                    if "hooks" not in existing_matcher_group:
                        existing_matcher_group["hooks"] = []

                    for new_hook in new_hooks_list:
                        # Check for duplicates
                        is_duplicate = False
                        for existing_hook in existing_matcher_group["hooks"]:
                            if hooks_are_equal(existing_hook, new_hook):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            existing_matcher_group["hooks"].append(deepcopy(new_hook))
                            print(
                                f"Added hook to {event_name} (matcher: {new_matcher})",
                                file=sys.stderr,
                            )
                        else:
                            print(
                                f"Skipped duplicate hook for {event_name} (matcher: {new_matcher})",
                                file=sys.stderr,
                            )
            else:
                # Handle non-matcher events
                new_hooks_list = new_matcher_group.get("hooks", [])

                # Find existing hooks container
                existing_container = None
                for container in existing_event:
                    if "hooks" in container:
                        existing_container = container
                        break

                if existing_container is None:
                    # Add new container
                    existing_event.append(deepcopy(new_matcher_group))
                    print(
                        f"Added new hooks container for {event_name}", file=sys.stderr
                    )
                else:
                    # Merge hooks
                    for new_hook in new_hooks_list:
                        # Check for duplicates
                        is_duplicate = False
                        for existing_hook in existing_container["hooks"]:
                            if hooks_are_equal(existing_hook, new_hook):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            existing_container["hooks"].append(deepcopy(new_hook))
                            print(f"Added hook to {event_name}", file=sys.stderr)
                        else:
                            print(
                                f"Skipped duplicate hook for {event_name}",
                                file=sys.stderr,
                            )

    return result


def validate_hooks_structure(hooks: dict[str, Any]) -> bool:
    """Validate the hooks structure."""
    valid_events = {
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
    }

    hooks_data = hooks.get("hooks", hooks)

    for event_name in hooks_data:
        if event_name not in valid_events:
            print(f"WARNING: Unknown hook event '{event_name}'", file=sys.stderr)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Merge Claude Code hooks from JSON into settings files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply hooks from stdin
  echo '{"hooks":{"PostToolUse":[{"matcher":"*","hooks":[{"type":"command","command":"echo done"}]}]}}' | \\
      %(prog)s --settings-file .claude/settings.json

  # Apply hooks from file
  cat my-hooks.json | %(prog)s --settings-file .claude/settings.json

  # Dry run to see what would change
  cat my-hooks.json | %(prog)s --settings-file .claude/settings.json --dry-run
""",
    )

    parser.add_argument(
        "--settings-file",
        "-f",
        required=True,
        help="Path to settings file (e.g., .claude/settings.json)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Read JSON from stdin
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print("ERROR: No JSON input provided via stdin", file=sys.stderr)
            sys.exit(1)

        new_hooks = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate structure
    validate_hooks_structure(new_hooks)

    filepath = Path(args.settings_file)

    # Load existing settings
    existing_settings = load_settings(filepath)

    # Merge hooks
    merged_settings = merge_hooks(existing_settings, new_hooks)

    if args.dry_run:
        print("Dry run - would write:", file=sys.stderr)
        print(json.dumps(merged_settings, indent=2))
    else:
        save_settings(filepath, merged_settings)
        print("Hooks merged successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
