# Evals & Observability — measure whether the agent does the right thing (Level 5)

Levels 1–4 *build* the harness. Level 5 is the **feedback loop**: how do you know whether changing
CLAUDE.md / settings / a skill made the agent **better or worse**? Without Level 5, every harness
change is a guess.

## Two halves

| Half | Answers | File |
|------|---------|------|
| **Evals** | "Does the agent produce the *right* result?" (measurable pass/fail) | [`cases/`](./cases/) |
| **Observability** | "What did the agent *do*, and why did it fail?" | [`observability.md`](./observability.md) |

Evals tell you **right/wrong**. Observability tells you **why** — and often reveals a problem at a
lower level (re-reading files endlessly = dirty context → Level 2; constant permission prompts → fix
`allow` at Level 3).

## The loop (this is the core, not the files)

```
define  →  run  →  read  →  fix  →  (re-run)
golden     the       the      the
task       agent     trace    harness
                     /result  (CLAUDE.md,
                              settings, skill)
```

The real lever: the golden-task set is a **regression net for the harness itself**. After you change
CLAUDE.md, re-run the set — a case that used to pass and now fails → almost certainly your change
(confirm by re-running a few times to rule out noise), not a guess.

## The truth: Level 5 is the least file-able

A *real* eval is **domain-specific** — no kit ships "is your agent correct yet" out of the box. This
kit only gives you the **scaffold + discipline**:

- **File:** the folder structure + a golden-task template + an observability guide.
- **Discipline (most of it):** *define* what "correct" means for your task, build the case set, read
  traces, **close the loop** (eval finds a regression → fix the harness → re-run).

The kit deliberately ships **no** runner code — a runner is repo-specific, and faking a generic one
would just be junk.

## Getting started

1. Copy `cases/example-task.md` into a real case and fill in *objective* done-criteria.
2. Gather 3–5 **representative** tasks (what the agent does most often) — you don't need many, you need the right ones.
3. **Take a "no-harness" baseline FIRST.** Run the set once with the harness not yet applied (empty
   CLAUDE.md / before installing Levels 1–4) and record the score. This is what **quantifies the
   harness's ROI**: re-run after applying the harness and compare the delta — exactly the field's
   opening thesis (changing the harness moves the score; see `docs/harness-engineering-tutorial.md`).
   This is *different* from the regression check below.
4. After that, before/after **each change** to the harness, re-run the set and compare (run it a few
   times to rule out noise before concluding cause).
5. When a case fails, open [`observability.md`](./observability.md) to trace *why*.
