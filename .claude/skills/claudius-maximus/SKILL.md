---
name: claudius-maximus
description: "Set up autonomous Claude Code loops (Ralph Wiggum pattern). Use when the user wants to run Claude continuously on a task until complete. Triggered by phrases like: run in a loop, autonomous agent, AFK coding, keep going until done, Ralph Wiggum loop, Claudius loop."
---

# Claudius Maximus

Set up autonomous Claude Code loops based on the Ralph Wiggum pattern - running Claude repeatedly with no memory between sessions until all tasks are complete.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Claudius Loop                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Iteration N:                                              │
│   ├─ Claude starts fresh (no memory)                        │
│   ├─ Reads PRD.md (requirements + tasks)                    │
│   ├─ Reads progress.txt (what's done)                       │
│   ├─ Picks next incomplete task                             │
│   ├─ Implements task                                        │
│   ├─ Runs verification (tests, lint, etc)                   │
│   ├─ Updates progress.txt                                   │
│   ├─ Commits + Pushes                                       │
│   ├─ Outputs: <iteration_complete>                          │
│   └─ Runner kills process                                   │
│       ↓                                                     │
│   Iteration N+1: (fresh session)                            │
│   └─ Repeat until <workflow_complete>                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Each iteration runs in a fresh Claude session. Progress is tracked externally in files. This eliminates context rot - Claude operates at peak intelligence every time.

---

## When Invoked: Full Automation Workflow

When this skill is invoked, your goal is to **fully automate setting up a Claudius loop** in the user's project. This involves:

1. **Proactive Scanning** - Find relevant context before asking questions
2. **Extensive Interview** - Ask MANY questions via AskUserQuestion tool
3. **Generate Artifacts** - Create PRD.md, progress.txt, and customized runner

**CRITICAL: Never be conservative with questions. Missing details leads to bad PRDs.**

---

## Phase 1: Proactive Scanning

Before interviewing the user, scan the project to understand context:

### Agent Documentation

Look for existing agent guidance:

```
CLAUDE.md, GEMINI.md, AGENTS.md, AGENT.md, README.md
.claude/settings.json
docs/*.md, .docs/*.md
```

Extract: code standards, testing requirements, commit conventions, tech stack.

### Existing Sub-Agents

Scan for existing sub-agents (these work in CLI via `--agents` flag):

```
.claude/agents/*.md
~/.claude/agents/*.md
```

For each agent found, extract from its YAML frontmatter:

- `name` - agent identifier
- `description` - what it does
- `tools` - allowed tools list
- `model` - which model to use
- The prompt (content after frontmatter)

### Existing Skills

Scan for skills the agent could use:

```
.claude/skills/*/SKILL.md
```

> **NOTE:** Skills may or may not be fully available in headless mode.
> As a backup, create a "skill shim" in the PRD that lists skills by name + path.
> Skills use progressive disclosure - don't bulk read, start with SKILL.md.

List each skill found with:

- Skill name
- Brief description (from SKILL.md frontmatter)
- Path to SKILL.md
- When it should be invoked

### Build/Test Commands

Look for:

```
package.json (scripts section)
Makefile, Taskfile.yml
pyproject.toml, setup.py
```

Identify: test command, lint command, typecheck command, build command.

### Existing PRD Files

Check if there's already a PRD:

```
PRD.md, prd.md, PLAN.md, TODO.md
```

---

## Phase 2: Interview the User

**ALWAYS use AskUserQuestion tool. Do NOT ask questions in plain text.**

Ask questions in logical groups. Never skip a category.

### Category 1: Project Context

- What is this project? (brief description)
- What tech stack is used?
- What are you trying to accomplish with this Claudius loop?
- Is this a new feature, refactor, test coverage, or something else?

### Category 2: Task Breakdown

- What are the specific tasks that need to be done?
- Should I help break down a large task into smaller pieces?
- What order should tasks be completed in? (dependencies?)
- How would you describe "done" for each task?

### Category 3: Constraints (Fail Conditions)

These are critical. Ask explicitly:

- What files/directories should the agent NOT modify?
- What actions are absolutely forbidden? Examples:
  - Don't deploy to production
  - Don't change database schema
  - Don't add new dependencies
  - Don't modify certain files
- Are there any external services the agent should NOT interact with?

### Category 4: Pass Conditions

- What MUST be true for the entire workflow to be complete?
- What verification commands must pass? (tests, lint, typecheck)
- Is there a coverage threshold?
- Are there specific acceptance criteria?

Present discovered skills:

- "I found these skills: [list]. Which should be available to the loop agent?"
- "When should each skill be invoked?"

### Category 6: Sub-Agents (if any found)

Sub-agents can be passed to Claude via the `--agents` CLI flag.

Present discovered agents:

- "I found these sub-agents: [list with descriptions]. Which should be included in the loop?"
- "For each selected agent, when should the loop agent invoke it?"

Explain that selected agents will be converted to JSON and passed via `--agents` flag.

### Category 7: Git Workflow

- Should I create a new branch for this work? (Recommended: yes)
- What should the branch be named?
- Should commits be pushed after each task? (Recommended: yes)

### Category 8: Iteration Limits

- How many iterations maximum? Recommendations:
  - Small tasks: 5-10
  - Medium features: 20-30  
  - Large complex work: 50-100
- Do you want max-turns per iteration? (safety limit on agentic actions)

### Category 9: Quality Bar

- Is this production code or prototype?
- What level of test coverage is expected?
- Should the agent write tests for new code?
- Any specific coding standards to follow?

---

## Phase 3: Generate Artifacts

After gathering all information, generate these files in the project directory:

### 1. PRD.md

Use the template from `templates/PRD_TEMPLATE.md`. Include:

- Project context
- Task checklist (with `[ ]` checkboxes)
- Constraints (hard boundaries)
- Pass conditions
- Verification commands
- Skill shim (if skills discovered)
- Git workflow notes

### 2. progress.txt

Create an empty progress file:

```
# Progress Log

```

### 3. Agents JSON (if agents selected)

Convert selected sub-agents to JSON for the `--agents` CLI flag:

**From agent .md file:**

```markdown
---
name: code-reviewer
description: Reviews code for quality
tools: Read, Glob, Grep
model: sonnet
---
You are a code reviewer. Analyze code and provide feedback.
```

**To JSON:**

```json
{
  "code-reviewer": {
    "description": "Reviews code for quality",
    "prompt": "You are a code reviewer. Analyze code and provide feedback.",
    "tools": ["Read", "Glob", "Grep"],
    "model": "sonnet"
  }
}
```

### 4. claudius_runner.py (customized)

**CRITICAL: Do NOT generate this file from scratch.** Output capture and signal handling are complex and fragile on different OSs (especially Windows).

1. **COPY** the script from `scripts/claudius_runner.py` in this skill folder to the user's project root.
   - Use `cp` (Linux/Mac) or `copy` (Windows) or `read_file` + `write_to_file`.
2. **MODIFY** the `SYSTEM_PROMPT` constant in the copied file to include:

- Project-specific context
- Custom constraints
- Skill references

---

## Phase 4: Confirm and Launch

Before the user runs the loop:

1. **Confirm the PRD** - Present a summary of what will be done
2. **Verify git state** - Is the repo clean? Is the branch created?
3. **Explain the command**:

   ```
   python claudius_runner.py <max_iterations>
   ```

4. **Set expectations** - Loops can take hours for complex work

---

## Skill Shim Mechanism

Since user skills are NOT available in headless mode, include this in the PRD:

```markdown
## Available Skills (Read When Needed)

> Skills use **progressive disclosure**. Don't bulk-read all files.
> Start with SKILL.md and branch out as needed.

| Skill Name | When to Use | Path |
|------------|-------------|------|
| my-skill | When doing X | `.claude/skills/my-skill/SKILL.md` |
```

The loop agent can then manually read skill files with the Read tool when relevant.

---

## Signal Protocol

The runner script monitors Claude's output for these signals:

| Signal | Meaning | Runner Action |
|--------|---------|---------------|
| `<iteration_complete>` | Single task done, more tasks remain | Kill process, start next iteration |
| `<workflow_complete>` | All tasks done, PRD complete | Kill process, exit loop successfully |

**The agent MUST output exactly one of these after each task.**

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/claudius_runner.py` | Main runner script |
| `templates/PRD_TEMPLATE.md` | Template for generating PRD |
| `templates/SYSTEM_PROMPT.md` | Template for system prompt |
| `references/cli-reference.md` | Claude CLI flags reference |
| `references/getting-started-with-ralph.md` | Original Ralph documentation |
| `references/tips-for-ai-coding-with-ralph-wiggum.md` | Advanced Ralph patterns |

---

## Quick Reference: Claude CLI Flags

```bash
claude -p "prompt" --dangerously-skip-permissions --no-session-persistence
```

| Flag | Purpose |
|------|---------|
| `-p` | Print mode - non-interactive output |
| `--dangerously-skip-permissions` | Auto-approve ALL actions |
| `--no-session-persistence` | Don't save session to disk |
| `--max-turns N` | Optional: limit agentic turns per iteration |

---

## Common Loop Types

| Type | Use Case | Key Prompt Element |
|------|----------|-------------------|
| Feature PRD | Build features from requirements | Task checklist in PRD |
| Test Coverage | Increase coverage to target | Coverage report + threshold |
| Linting | Clean up code quality | `npm run lint` as feedback |
| Refactoring | Extract, restructure code | Specific refactor goals |
| Entropy | Find and fix code smells | "Scan for X, fix one per iteration" |
