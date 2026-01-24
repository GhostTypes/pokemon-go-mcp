# https://www.aihero.dev/getting-started-with-ralph

# Getting Started With Ralph

![Matt Pocock](https://res.cloudinary.com/total-typescript/image/upload/c_limit,w_96/f_auto/q_auto/v1728059672/matt-pocock_eyjjli?_a=BAVAZGAQ0)

Matt Pocock

Use with AI

[Ralph](https://ghuntley.com/ralph/) is a technique for running AI coding agents in a loop. You run the same prompt repeatedly. The AI picks its own tasks from a PRD. It commits after each feature. You come back later to working code.

This guide walks you through building your first Ralph loop. We'll use [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Docker Desktop](https://docs.docker.com/desktop/).

I'm assuming Linux, but you can point an AI at this article and have it translate for your OS or AI Coding CLI.

For more tips on getting the most out of Ralph, check out my [11 tips for AI coding with Ralph](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum).

## [1. Install Claude Code](#1-install-claude-code)

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's CLI for agentic coding. Install it with the native binary:

```
curl -fsSL https://claude.ai/install.sh | bash
```

If you get "command not found: claude" after installing, add the install location to your PATH:

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc



source ~/.bashrc
```

Alternatively, install via [npm](https://www.npmjs.com/package/@anthropic-ai/claude-code):

```
npm i -g @anthropic-ai/claude-code
```

Run `claude` to authenticate with your Anthropic account.

## [2. Install Docker Desktop](#2-install-docker-desktop)

[Docker Desktop](https://docs.docker.com/desktop/) lets you run Claude Code in an isolated sandbox. The AI can execute commands, install packages, and modify files without touching your local machine.

Install [Docker Desktop 4.50+](https://docs.docker.com/desktop/install), then run:

```
docker sandbox run claude
```

On first run, you'll authenticate with Anthropic. Your credentials are stored in a Docker volume.

Key benefits of sandboxes:

* Your working directory mounts at the same path inside the container
* Git config is auto-injected for proper commit attribution
* One sandbox per workspace - state persists between runs

See the [Docker Sandboxes docs](https://docs.docker.com/ai/sandboxes/) for more.

## [3. Create your Plan File](#3-create-your-plan-file)

Ralph needs a PRD (Product Requirements Document) to pick tasks from. You could write one manually, but it's faster to use Claude's [plan mode](https://docs.anthropic.com/en/docs/claude-code/plan-mode).

Run Claude:

```
claude
```

And press `shift-tab` to enter plan mode. You'll be able to iterate on a plan until you're happy with it.

When you're happy with the plan, tell Claude to save it to `PRD.md`.

Also create an empty progress file:

```
touch progress.txt
```

The PRD defines the end state. The progress file tracks what's done. Claude reads both on each loop iteration, finds the next unchecked item, implements it, and updates progress.

The PRD can be in any format - markdown checklist, JSON, plain prose. What matters is that the scope is clear and the agent can pull out individual tasks. For more tips on writing good PRDs, see my [11 tips for AI coding with Ralph](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum).

## [4. Create Your `ralph-once.sh` Script](#4-create-your-script)

Before going fully AFK, start with a human-in-the-loop Ralph. You run the script, watch what it does, then run it again. This builds intuition for how the loop works.

Create `ralph-once.sh`:

```
#!/bin/bash



claude --permission-mode acceptEdits "@PRD.md @progress.txt \



1. Read the PRD and progress file. \



2. Find the next incomplete task and implement it. \



3. Commit your changes. \



4. Update progress.txt with what you did. \



ONLY DO ONE TASK AT A TIME."
```

Key elements:

| Element | Purpose |
| --- | --- |
| `--permission-mode acceptEdits` | Auto-accepts file edits so the loop doesn't stall |
| `@PRD.md` | Points Claude at your requirements doc |
| `@progress.txt` | Tracks completed work between runs |
| `ONLY DO ONE TASK` | Forces small, incremental commits |

Make it executable:

```
chmod +x ralph-once.sh
```

Run it with `./ralph-once.sh`. Watch what Claude does. Check the commit. Run it again.

## [5. Create your `afk-ralph.sh` Script](#5-create-your-script)

Once you're comfortable with human-in-the-loop Ralph, wrap it in a loop:

```
#!/bin/bash



set -e



if [ -z "$1" ]; then



echo "Usage: $0 <iterations>"



exit 1



fi



for ((i=1; i<=$1; i++)); do



result=$(docker sandbox run claude --permission-mode acceptEdits -p "@PRD.md @progress.txt \



1. Find the highest-priority task and implement it. \



2. Run your tests and type checks. \



3. Update the PRD with what was done. \



4. Append your progress to progress.txt. \



5. Commit your changes. \



ONLY WORK ON A SINGLE TASK. \



If the PRD is complete, output <promise>COMPLETE</promise>.")



echo "$result"



if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then



echo "PRD complete after $i iterations."



exit 0



fi



done
```

The `-p` flag runs Claude in print mode - non-interactive, outputs to stdout. This lets us capture the result and check for the completion sigil.

```
./afk-ralph.sh 20
```

Go make coffee. Come back to commits.

| Element | Purpose |
| --- | --- |
| `set -e` | Exit on any error |
| `$1` (iterations) | Caps the loop to prevent runaway costs |
| `-p` | Print mode - non-interactive output |
| `<promise>COMPLETE</promise>` | Completion sigil Claude outputs when done |

## [6. Make It Your Own](#6-make-it-your-own)

Ralph is just a loop. That simplicity makes it infinitely customizable.

You can swap the task source. Instead of a local PRD, pull tasks from GitHub Issues, [Linear](https://linear.app), or [beads](https://github.com/steveyegge/beads). The agent still chooses what to work on - you just change where the list lives.

You can change the output. Instead of committing to main, each iteration could create a branch and open a PR. Useful for triaging a backlog of issues.

You can run different loop types entirely:

| Loop Type | What It Does |
| --- | --- |
| Test Coverage | Finds uncovered lines, writes tests until coverage hits target |
| Linting | Fixes lint errors one by one |
| Duplication | Hooks into [jscpd](https://github.com/kucherenko/jscpd), refactors clones into shared utilities |
| Entropy | Scans for code smells, cleans them up |

Any task that fits "look at repo, improve something, commit" works with Ralph.

For deeper guidance on feedback loops, task sizing, prioritization, and more, read my [11 tips for AI coding with Ralph](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum).

Want more on autonomous AI coding? Join my [newsletter](https://aihero.dev/newsletter) to get notified when new articles drop.

![](https://res.cloudinary.com/total-typescript/image/upload/c_limit,w_384/f_auto/q_auto/v1741008166/aihero.dev/assets/textured-logo-mark_2x_ecauns?_a=BAVAZGAQ0)

## Join over 50,000 Developers Becoming AI Heroes

### Subscribe to be the first to learn about AI Hero releases, updates, and special discounts for AI Heroes.

First Name

Email\*

Subscribe

I respect your privacy. Unsubscribe at any time.

**Share**

Copy URL