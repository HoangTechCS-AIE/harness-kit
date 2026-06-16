# Long-running — work that spans more than one session (Level 4)

Level 4 keeps the agent working *reliably* on long-horizon work: multi-day refactors, big migrations,
an agent running in the background for hours. Long work dies from 3 things — each file here blocks one.

## 3 files, 3 problems

| File | Which death it blocks |
|------|-----------------------|
| [`setup.sh`](../setup.sh) | Can't get back to a runnable state (a fresh clone/agent doesn't know what to install) |
| [`TASK.md`](./TASK.md) | State lost across sessions / after `/clear` |
| [`new-worktree.sh`](../new-worktree.sh) | Parallel tasks step on each other |

## Install

```bash
cp setup.sh new-worktree.sh .          # into the repo root
chmod +x setup.sh new-worktree.sh
cp long-running/TASK.md .              # when you start a specific long task
```

Then **point `CLAUDE.md`** at them so the agent knows to use them:

```md
## Build / Test / Run
- Set up the environment: ./setup.sh   (idempotent — safe to re-run)

## Long-running
- An in-flight long task is tracked in TASK.md — read it before starting, update it at milestones.
```

## When to use which (this is the discipline part)

The files are just tools — knowing *when* to reach for them is the skill:

- **`setup.sh`** — run it the moment you enter a fresh checkout, and whenever you suspect the
  environment drifted. Keep it **idempotent + fail-fast**: a background agent must be able to rebuild
  it without asking.
- **`TASK.md`** — open it when the work *will span multiple sessions* or you're about to `/clear`.
  Update it at **milestones** (a part done, a decision locked), not every line of code. It's what the
  next agent reads to continue — write it so a "stranger" understands, not as shorthand for yourself.
- **`new-worktree.sh`** — split off a worktree when running **2+ directions in parallel**, or when a
  long task needs isolation from the main branch. One task = one worktree. Done: `git worktree remove <dir>`.

## Running in the background & checking back

Genuinely long work can run in the background while you check back (no babysitting). The principle:
a chunk of work must be **resumable** — if it's cut off mid-way, `TASK.md` + `setup.sh` are enough to
pick up from the latest milestone instead of starting over. That's why those two files exist.
