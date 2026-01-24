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

            # Check if command contains "git"
            if "git" in command:
                # Get current time - use project dir if available
                time_script = ".claude/skills/get-time/scripts/get_time.py"
                if os.environ.get("CLAUDE_PROJECT_DIR"):
                    time_script = os.path.join(os.environ["CLAUDE_PROJECT_DIR"], time_script)

                result = subprocess.run(
                    ["python", time_script, "datetime", "America/New_York"],
                    capture_output=True,
                    text=True,
                    shell=False
                )

                if result.stdout.strip():
                    print(f"[Git Command] Current time: {result.stdout.strip()}")

    except Exception as e:
        # Silently fail - don't break the workflow
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
