# PRD Template

## Project Context

[Describe the project, tech stack, and what you're trying to accomplish]

---

## Tasks

Complete each task in order. Mark as done by changing `[ ]` to `[x]`.

- [ ] Task 1: [Description]
- [ ] Task 2: [Description]
- [ ] Task 3: [Description]
- [ ] ...

---

## Constraints (Do NOT Violate)

These are hard boundaries. The agent MUST NOT:

- [e.g., Modify files outside `src/` directory]
- [e.g., Change database schema]
- [e.g., Deploy to production]
- [e.g., Add new dependencies without approval]
- [e.g., Break existing tests]

---

## Pass Conditions (MUST Be True for Completion)

The workflow is complete ONLY when ALL of these are true:

- [ ] All tasks above are marked complete
- [ ] [e.g., All tests pass: `npm test`]
- [ ] [e.g., Zero TypeScript errors: `npm run typecheck`]
- [ ] [e.g., Zero lint errors: `npm run lint`]
- [ ] [e.g., Coverage threshold met: 80%+]

---

## Verification Commands

Run these after each task to validate your work:

```bash
# Tests
npm test

# Type checking
npm run typecheck

# Linting
npm run lint

# Build (if applicable)
npm run build
```

---

## Available Skills (Read When Needed)

> Skills are designed for **progressive disclosure**. Don't bulk-read all skill files.
> Start with the SKILL.md file and branch out based on what you need.

| Skill Name | When to Use | Path |
|------------|-------------|------|
| [skill-name] | [When this skill is relevant] | `.claude/skills/[skill-name]/SKILL.md` |

**How to use skills:**

1. When you encounter a task that matches a skill's "When to Use" criteria
2. Read the skill's SKILL.md file using the Read tool
3. Follow the instructions in that file
4. The skill may reference additional files - read those as needed

---

## Git Workflow

- Branch: `[branch-name]` (create if doesn't exist)
- Commit after each task with descriptive message
- Push after each commit
- Do NOT include "Co-Authored-By" lines in commits
