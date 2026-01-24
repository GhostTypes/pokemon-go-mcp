import subprocess
import sys


def main():
    try:
        result = subprocess.run(
            [
                "python",
                ".claude/skills/get-time/scripts/get_time.py",
                "datetime",
                "America/New_York",
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            print(f"[Session Start] Current time: {result.stdout.strip()}")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
