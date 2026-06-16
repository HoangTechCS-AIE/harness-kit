# Specs — spec-driven development (the other half of Pillar 2)

Pillar 2 is **"Repo-local instructions & Specs"**. Level 1 (`/init-harness` → `CLAUDE.md`) covers the
**instructions** half: durable rules that hold across *every* task. `FEATURE.md` covers the **specs**
half: defining **one specific feature BEFORE you code it**. A clear spec → the agent strays less; clear
acceptance criteria → you already have what a Level 5 eval grades pass/fail.

## When to use it

- A feature **big enough to get lost in** / multi-step / multi-person → write a spec first.
- A small, one-shot job → **skip it**. Don't turn specs into ritual.

## `FEATURE.md` vs `TASK.md` (don't confuse them — they complement each other)

| | `FEATURE.md` (here) | `TASK.md` (Level 4) |
|---|---|---|
| Purpose | **plan BEFORE coding**: what + pass criteria | **state that survives ACROSS sessions** |
| Lifecycle | written once at the feature's start, changes little | updated continuously at each milestone |
| Answers | "what *is* this feature, when is it done" | "where am I *right now*, what's next" |

A big feature usually uses **both**: `FEATURE.md` fixes the target, `TASK.md` tracks the path.

## Install

```bash
mkdir -p docs/specs
cp FEATURE.md docs/specs/<feature-name>.md
```

## Advanced

Big feature / whole team → use a dedicated framework: **GitHub Spec Kit**, **12-Factor Agents** (links
in `docs/harness-engineering-tutorial.md`). `FEATURE.md` is just a minimal starting point — enough to
have a spec, without forcing you to adopt a whole framework.
