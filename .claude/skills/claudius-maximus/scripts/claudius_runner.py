#!/usr/bin/env python3
"""
Claudius Runner - Ralph Wiggum Loop for Claude Code

Runs Claude Code in an autonomous loop until all tasks are complete or max iterations reached.
Each iteration has no memory - progress is tracked via PRD.md and progress.txt files.

Usage:
    python claudius_runner.py <max_loops>

Requirements:
    - PRD.md and progress.txt must exist in the current directory
    - Claude Code must be installed and authenticated
"""

import argparse
import os
import subprocess
import sys

# --- CONFIGURATION ---

# The system prompt forces the agent to use state files and output specific XML tags.
# @PRD.md and @progress.txt are auto-included by Claude Code.
SYSTEM_PROMPT = """
@PRD.md @progress.txt

ROLE:
You are an autonomous coding agent. You have NO memory of previous runs.
Your memory is entirely contained in the files above.

FILES TO USE:
- PRD.md: Contains the Product Requirements. READ THIS FIRST.
- progress.txt: Contains the log of completed tasks. READ THIS NEXT to see what has been done.

INSTRUCTIONS:
1. Read PRD.md to understand the goal, constraints, and pass conditions.
2. Read progress.txt to identify what has been completed.
3. Find the NEXT incomplete task from the PRD.
4. Execute ONLY that SINGLE task (write code, fix bugs, etc.).
5. Run any verification commands specified in the PRD (tests, lint, typecheck).
6. Update progress.txt by appending what you completed.
7. Run: git add ., git commit -m "descriptive message", and git push.

CRITICAL OUTPUT SIGNALS:
After completing the task and pushing code, you MUST output one of these signals:

- If you pushed code and there are MORE incomplete tasks:
  Output exactly: <iteration_complete>

- If the ENTIRE project is finished (all tasks done, all pass conditions met):
  Output exactly: <workflow_complete>

RULES:
- Do NOT output signals unless you have successfully pushed code and updated progress.txt.
- Do ONLY ONE TASK per iteration. Stop after outputting the signal.
- Do NOT include "Co-Authored-By" lines in commit messages.
- Follow all constraints and boundaries specified in the PRD.
"""

# Base command for Claude Code
# Uses --dangerously-skip-permissions for fully autonomous operation
# Uses --no-session-persistence for clean sessions
# Optional: --agents for passing sub-agents as JSON


def build_claude_command(agents_json=None):
    """Build the Claude CLI command with optional agents."""
    cmd = [
        "claude",
        "-p",
        SYSTEM_PROMPT,
        "--dangerously-skip-permissions",
        "--no-session-persistence",
    ]

    # Add agents if provided
    if agents_json:
        cmd.extend(["--agents", agents_json])

    return cmd


def run_claudius_loop(max_loops, agents_json=None):
    """Main loop that runs Claude iterations until complete or max reached."""

    # Pre-flight check
    if not os.path.exists("PRD.md"):
        print("[Error] Missing required file: PRD.md")
        print("Create a PRD.md file with your requirements before running.")
        sys.exit(1)

    if not os.path.exists("progress.txt"):
        print("[Info] Creating empty progress.txt file...")
        with open("progress.txt", "w") as f:
            f.write("# Progress Log\n\n")

    # Build the command once
    claude_command = build_claude_command(agents_json)

    if agents_json:
        print("[Claudius] Sub-agents loaded from --agents flag")

    loop_count = 0

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n{'=' * 60}")
        print(f"[Claudius] --- Starting Iteration {loop_count}/{max_loops} ---")
        print(f"{'=' * 60}")

        # Launch Claude as a subprocess
        # creationflags for Windows signal handling
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        try:
            process = subprocess.Popen(
                claude_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                encoding="utf-8",
                creationflags=creation_flags,
            )
        except FileNotFoundError:
            print("[Error] Claude Code not found. Install it with:")
            print("  npm i -g @anthropic-ai/claude-code")
            print("Or:")
            print("  curl -fsSL https://claude.ai/install.sh | bash")
            sys.exit(1)

        iteration_success = False
        workflow_finished = False

        try:
            # Monitor output line-by-line for real-time feedback
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    # Print output as it comes
                    sys.stdout.write(line)
                    sys.stdout.flush()

                    # Check for iteration complete signal
                    if "<iteration_complete>" in line.lower():
                        print("\n[Claudius] Signal Detected: ITERATION_COMPLETE")
                        iteration_success = True
                        kill_process(process)
                        break

                    # Check for workflow complete signal
                    if "<workflow_complete>" in line.lower():
                        print("\n[Claudius] Signal Detected: WORKFLOW_COMPLETE")
                        workflow_finished = True
                        kill_process(process)
                        break

        except KeyboardInterrupt:
            print("\n[Claudius] User stopped execution (Ctrl+C).")
            kill_process(process)
            sys.exit(0)

        # Ensure process is terminated
        kill_process(process)

        if workflow_finished:
            print(f"\n{'=' * 60}")
            print(f"[Claudius] PROJECT COMPLETE after {loop_count} iterations!")
            print(f"{'=' * 60}")
            print("\nAll tasks finished. Review your commits and merge when ready.")
            sys.exit(0)

        if not iteration_success:
            print(
                f"\n[Claudius] Warning: Iteration {loop_count} ended without a success signal."
            )
            print("[Claudius] Continuing to next iteration to retry...")
            # Continue immediately - no delay

    # Reached max iterations without workflow_complete
    print(f"\n{'=' * 60}")
    print(f"[Claudius] Reached maximum limit of {max_loops} iterations.")
    print(f"{'=' * 60}")
    print("\nThe workflow did not complete. Check progress.txt to see what was done.")
    print("You can run again with more iterations if needed.")
    sys.exit(1)


def kill_process(process):
    """Platform-specific forced process termination."""
    if process.poll() is None:
        try:
            if sys.platform == "win32":
                # Windows: use taskkill for forceful termination including children
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Unix: terminate then kill
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Run Claude Code in a Claudius (Ralph Wiggum) loop.",
        epilog="Example: python claudius_runner.py 20",
    )
    parser.add_argument(
        "max_loops", type=int, help="Maximum number of iterations allowed."
    )
    parser.add_argument(
        "--agents",
        type=str,
        default=None,
        help="JSON string of sub-agents to pass to Claude (optional).",
    )
    args = parser.parse_args()

    if args.max_loops < 1:
        print("[Error] max_loops must be at least 1")
        sys.exit(1)

    print(f"[Claudius] Starting autonomous loop (max {args.max_loops} iterations)")
    print(f"[Claudius] Working directory: {os.getcwd()}")
    print("[Claudius] PRD file: PRD.md")
    print("[Claudius] Progress file: progress.txt")

    run_claudius_loop(args.max_loops, args.agents)


if __name__ == "__main__":
    main()
