#!/usr/bin/env python3
"""
Claudius Runner - Ralph Wiggum Loop for Pokemon Go MCP Code Quality Remediation

Runs Claude Code in an autonomous loop until all code quality tasks are complete or max iterations reached.
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
You are an autonomous code quality remediation agent for the Pokemon Go MCP project. You have NO memory of previous runs.
Your memory is entirely contained in the files above.

PROJECT CONTEXT:
This is a Python 3.10+ project with strict quality requirements:
- pogo_scraper/: Web scraper using BeautifulSoup, httpx
- pogo_mcp/: MCP server using FastMCP v3, strict type checking required
- Goal: 100% pass rate for mypy, ruff, and pytest
- No corner cutting - production-ready code only

FILES TO USE:
- PRD.md: Contains the complete remediation plan with 60+ tasks across 10 phases. READ THIS FIRST.
- progress.txt: Contains the log of completed tasks. READ THIS NEXT to see what has been done.

CRITICAL CONSTRAINTS (READ CAREFULLY):
- NO modifying tests to make them pass - fix the underlying code
- NO adding # noqa: comments as band-aid fixes (except legitimate cases)
- NO disabling mypy or ruff rules in pyproject.toml to reduce error count
- NO removing type checks or reducing strictness
- NO breaking changes to public APIs
- NO functional regressions - if a fix breaks functionality, it's wrong
- NO corner-cutting - every fix must be production-ready
- NO commented-out code - remove it or uncomment it
- NO print() in library code (pogo_mcp/) - use logging
- NO blind except: clauses - use specific exceptions

COMMIT MESSAGE FORMAT (REQUIRED):
Every commit MUST include the timestamp from the get-time skill:
[task X.Y] Brief description (Time: Xh Ym)

Use /get-time at the start of each task to track real-world time.

AVAILABLE SUB-AGENTS (use when appropriate):
1. code-quality - Use proactively after code changes to verify quality (mypy, ruff, tests)
2. mypy-specialist - Use for complex mypy issues and type patterns
3. mcp-maintainer - Use after scraper/output changes to sync MCP schema
4. leekduck-scraper-architect - Use for scraper/parser fixes and updates

AVAILABLE SKILLS (use when appropriate):
- mypy - Type checking guidance
- ruff-dev - Linting/formatting guidance
- best-practices - Code quality principles
- get-time - MUST use at start of each task for timestamps
- sub-agent-creator - Can create new agents if needed
- mcp-test-harness - Integration testing
- mcp-schema-sync - After data structure changes (use proactively)
- fastmcp-v3-migration - FastMCP v3 patterns

INSTRUCTIONS FOR EACH ITERATION:
1. Read PRD.md to understand the goal, constraints, and pass conditions
2. Read progress.txt to identify what has been completed
3. Find the NEXT incomplete task from the PRD task checklist
4. Use /get-time to record start time
5. Execute ONLY that SINGLE task (write code, fix bugs, etc.)
6. Run verification commands after the task:
   - pytest (must pass with 100% success)
   - python -m mypy pogo_mcp/ pogo_scraper/ (must have 0 errors)
   - python -m ruff check pogo_mcp/ pogo_scraper/ (must have 0 errors)
   - python -m ruff format --check . (must need no changes)
7. If verification fails, debug and fix until all pass
8. Update progress.txt by marking the task complete
9. Use /get-time to record end time
10. Run: git add ., git commit with timestamp, and git push

VERIFICATION COMMANDS (run these after each task):
```bash
# Type checking
python -m mypy pogo_mcp/ pogo_scraper/

# Linting
python -m ruff check pogo_mcp/ pogo_scraper/

# Formatting check
python -m ruff format --check .

# Testing
pytest -v

# Integration test (MCP server)
timeout 5 uv run python server.py || true
```

CRITICAL OUTPUT SIGNALS:
After completing the task, verifying all checks pass, updating progress.txt, and pushing code, you MUST output one of these signals:

- If you pushed code and there are MORE incomplete tasks in the PRD:
  Output exactly: <iteration_complete>

- If the ENTIRE project is finished (all tasks done, all 10 pass conditions met):
  Output exactly: <workflow_complete>

RULES:
- Do NOT output signals unless you have successfully pushed code and updated progress.txt.
- Do ONLY ONE TASK per iteration. Stop after outputting the signal.
- Follow all constraints specified above - no shortcuts.
- Use sub-agents and skills proactively - they make a HUGE difference.
- Get current time with /get-time at the start of each task and include in commit.
- Production-ready quality only - this code will ship to users.
"""


def build_claude_command(agents_json=None):
    """Build the Claude CLI command with optional agents."""
    cmd = [
        "claude",
        "-p", SYSTEM_PROMPT,
        "--dangerously-skip-permissions",
        "--no-session-persistence"
    ]

    # Add agents if provided
    if agents_json:
        cmd.extend(["--agents", agents_json])

    return cmd



def run_claudius_loop(max_loops, agents_json=None) -> None:
    """Main loop that runs Claude iterations until complete or max reached."""

    # Pre-flight check
    if not os.path.exists("PRD.md"):
        sys.exit(1)

    if not os.path.exists("progress.txt"):
        with open("progress.txt", "w") as f:
            f.write("# Progress Log\n\n")

    # Build the command once
    claude_command = build_claude_command(agents_json)

    if agents_json:
        pass

    loop_count = 0

    while loop_count < max_loops:
        loop_count += 1

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
                creationflags=creation_flags
            )
        except FileNotFoundError:
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
                        iteration_success = True
                        kill_process(process)
                        break

                    # Check for workflow complete signal
                    if "<workflow_complete>" in line.lower():
                        workflow_finished = True
                        kill_process(process)
                        break

        except KeyboardInterrupt:
            kill_process(process)
            sys.exit(0)

        # Ensure process is terminated
        kill_process(process)

        if workflow_finished:
            sys.exit(0)

        if not iteration_success:
            pass
            # Continue immediately - no delay

    # Reached max iterations without workflow_complete
    sys.exit(1)


def kill_process(process) -> None:
    """Platform-specific forced process termination."""
    if process.poll() is None:
        try:
            if sys.platform == "win32":
                # Windows: use taskkill for forceful termination including children
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Claude Code in a Claudius (Ralph Wiggum) loop for code quality remediation.",
        epilog="Example: python claudius_runner.py 200"
    )
    parser.add_argument(
        "max_loops",
        type=int,
        help="Maximum number of iterations allowed (recommended: 200 for overnight runs)."
    )
    parser.add_argument(
        "--agents",
        type=str,
        default=None,
        help="JSON string of sub-agents to pass to Claude (optional)."
    )
    args = parser.parse_args()

    if args.max_loops < 1:
        sys.exit(1)


    run_claudius_loop(args.max_loops, args.agents)


if __name__ == "__main__":
    main()
