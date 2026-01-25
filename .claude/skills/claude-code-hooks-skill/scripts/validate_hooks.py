#!/usr/bin/env python3
"""
Validate Claude Code hook configurations.

This script validates hook JSON to ensure it follows the correct schema
before applying to settings files.

Usage:
    python3 validate_hooks.py hooks.json
    echo '{"hooks":{...}}' | python3 validate_hooks.py -
"""

import argparse
import json
import sys
from typing import Any

VALID_EVENTS = {
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

MATCHER_EVENTS = {"PreToolUse", "PostToolUse", "PermissionRequest"}

COMMON_MATCHERS = {
    "Bash",
    "Write",
    "Edit",
    "Read",
    "Glob",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
    "Notebook.*",
    "*",
}

NOTIFICATION_MATCHERS = {
    "permission_prompt",
    "idle_prompt",
    "auth_success",
    "elicitation_dialog",
}

PROMPT_ONLY_EVENTS = {"Stop", "SubagentStop"}


class ValidationError:
    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


def validate_hook(hook: dict[str, Any], path: str, event: str) -> list[ValidationError]:
    """Validate a single hook entry."""
    errors = []

    # Check type
    hook_type = hook.get("type")
    if not hook_type:
        errors.append(ValidationError(path, "Missing 'type' field"))
    elif hook_type not in ("command", "prompt"):
        errors.append(
            ValidationError(
                path, f"Invalid type '{hook_type}', must be 'command' or 'prompt'"
            )
        )

    # Type-specific validation
    if hook_type == "command":
        if "command" not in hook:
            errors.append(
                ValidationError(path, "Missing 'command' field for type='command'")
            )
        elif not hook["command"]:
            errors.append(ValidationError(path, "Empty command"))

    elif hook_type == "prompt":
        if event not in PROMPT_ONLY_EVENTS:
            errors.append(
                ValidationError(
                    path,
                    f"Prompt hooks only supported for {PROMPT_ONLY_EVENTS}, not '{event}'",
                )
            )
        if "prompt" not in hook:
            errors.append(
                ValidationError(path, "Missing 'prompt' field for type='prompt'")
            )
        elif not hook["prompt"]:
            errors.append(ValidationError(path, "Empty prompt"))

    # Validate timeout if present
    if "timeout" in hook:
        timeout = hook["timeout"]
        if not isinstance(timeout, (int, float)):
            errors.append(
                ValidationError(
                    path, f"Timeout must be a number, got {type(timeout).__name__}"
                )
            )
        elif timeout <= 0:
            errors.append(ValidationError(path, "Timeout must be positive"))
        elif timeout > 300:
            errors.append(
                ValidationError(
                    path,
                    f"Timeout of {timeout}s is very long (>5 min)",
                    severity="warning",
                )
            )

    # Check for unknown fields
    known_fields = {"type", "command", "prompt", "timeout"}
    for field in hook:
        if field not in known_fields:
            errors.append(
                ValidationError(path, f"Unknown field '{field}'", severity="warning")
            )

    return errors


def validate_matcher_group(
    group: dict[str, Any], path: str, event: str
) -> list[ValidationError]:
    """Validate a matcher group."""
    errors = []

    # Validate matcher
    matcher = group.get("matcher", "*")
    if (
        event == "Notification"
        and matcher not in NOTIFICATION_MATCHERS
        and matcher != "*"
        and matcher != ""
    ):
        errors.append(
            ValidationError(
                path,
                f"Unusual notification matcher '{matcher}'. Expected one of {NOTIFICATION_MATCHERS}",
                severity="warning",
            )
        )

    # Validate hooks array
    hooks = group.get("hooks")
    if hooks is None:
        errors.append(ValidationError(path, "Missing 'hooks' array"))
    elif not isinstance(hooks, list):
        errors.append(ValidationError(path, "'hooks' must be an array"))
    elif len(hooks) == 0:
        errors.append(ValidationError(path, "Empty 'hooks' array", severity="warning"))
    else:
        for i, hook in enumerate(hooks):
            hook_path = f"{path}.hooks[{i}]"
            if not isinstance(hook, dict):
                errors.append(ValidationError(hook_path, "Hook must be an object"))
            else:
                errors.extend(validate_hook(hook, hook_path, event))

    # Check for unknown fields in matcher group
    known_fields = {"matcher", "hooks"}
    for field in group:
        if field not in known_fields:
            errors.append(
                ValidationError(path, f"Unknown field '{field}'", severity="warning")
            )

    return errors


def validate_hooks(data: dict[str, Any]) -> list[ValidationError]:
    """Validate complete hooks configuration."""
    errors = []

    # Handle both {hooks:{...}} and {...} formats
    hooks_obj = data.get("hooks", data)

    if not isinstance(hooks_obj, dict):
        errors.append(ValidationError("hooks", "Hooks must be an object"))
        return errors

    for event_name, event_matchers in hooks_obj.items():
        event_path = f"hooks.{event_name}"

        # Validate event name
        if event_name not in VALID_EVENTS:
            errors.append(
                ValidationError(
                    event_path,
                    f"Unknown event '{event_name}'. Valid events: {sorted(VALID_EVENTS)}",
                )
            )
            continue

        # Validate event value is array
        if not isinstance(event_matchers, list):
            errors.append(ValidationError(event_path, "Event value must be an array"))
            continue

        if len(event_matchers) == 0:
            errors.append(
                ValidationError(event_path, "Empty event array", severity="warning")
            )
            continue

        # Validate each matcher group
        for i, matcher_group in enumerate(event_matchers):
            group_path = f"{event_path}[{i}]"

            if not isinstance(matcher_group, dict):
                errors.append(
                    ValidationError(group_path, "Matcher group must be an object")
                )
                continue

            errors.extend(validate_matcher_group(matcher_group, group_path, event_name))

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate Claude Code hook configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hooks.json
  echo '{"hooks":{...}}' | %(prog)s -
  %(prog)s --strict hooks.json
""",
    )

    parser.add_argument("input", help="JSON file to validate (use - for stdin)")

    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output errors, no success message",
    )

    args = parser.parse_args()

    # Load input
    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as f:
                data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    errors = validate_hooks(data)

    # Filter and display
    actual_errors = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity == "warning"]

    if args.strict:
        actual_errors.extend(warnings)
        warnings = []

    # Output
    for error in actual_errors:
        print(error, file=sys.stderr)

    for warning in warnings:
        print(warning, file=sys.stderr)

    # Summary
    if actual_errors:
        print(f"\nValidation FAILED: {len(actual_errors)} error(s)", file=sys.stderr)
        if warnings:
            print(f"Also found {len(warnings)} warning(s)", file=sys.stderr)
        sys.exit(1)
    elif warnings:
        if not args.quiet:
            print(f"Validation PASSED with {len(warnings)} warning(s)", file=sys.stderr)
        sys.exit(0)
    else:
        if not args.quiet:
            print("Validation PASSED", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
