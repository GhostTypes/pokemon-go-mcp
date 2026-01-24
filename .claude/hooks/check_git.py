import sys
import json
import subprocess
import os


def main():
    try:
        # Read JSON from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract tool name and command
        tool = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool == "Bash":
            command = tool_input.get("command", "")

            # Check if command is a commit or push (operations that finalize work)
            if "git" in command and any(cmd in command for cmd in ["commit", "push"]):
                # Get current time
                time_script = ".claude/skills/get-time/scripts/get_time.py"
                if os.environ.get("CLAUDE_PROJECT_DIR"):
                    time_script = os.path.join(
                        os.environ["CLAUDE_PROJECT_DIR"], time_script
                    )

                result = subprocess.run(
                    ["python", time_script, "datetime", "America/New_York"],
                    capture_output=True,
                    text=True,
                    shell=False,
                )

                if result.stdout.strip():
                    current_time = result.stdout.strip()
                    print(f"\n{'=' * 60}")
                    print(f"[TIME TRACKING REMINDER]")
                    print(f"Current time: {current_time}")
                    print(
                        f"Before committing: Calculate elapsed time from your start time"
                    )
                    print(f"Include duration in commit message (e.g., 'Time: ~2h 15m')")
                    print(f"Update progress.txt with time tracking data")
                    print(f"{'=' * 60}\n")

    except Exception as e:
        # Silently fail - don't break the workflow
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
