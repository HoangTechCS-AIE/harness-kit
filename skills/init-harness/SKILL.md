---
name: init-harness
description: Generate a "harness-engineering-grade" CLAUDE.md for a repo, replacing the default /init. Analyzes the codebase to fill in WHAT/WHY/HOW (stack, build/test/run, architecture, conventions), then asks to confirm exactly the 2 things it can't infer — Guardrails (constraints on agent behavior) and Definition of Done (when work counts as finished) — the parts /init omits. Follows HumanLayer's "Writing a good CLAUDE.md" discipline: short (<300 lines, ideally ~60), pointers instead of copies, no style/convention stuffing (leave that to the linter), hand-crafted rather than auto-generated. Use this skill when the user wants to create/standardize a CLAUDE.md, "init harness", or set up a repo for a coding agent. Currently does CLAUDE.md only (Claude Code); AGENTS.md/Codex to be added later.
argument-hint: [repo path, defaults to the current directory]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# init-harness — a harness-engineering-grade CLAUDE.md

Produce a `CLAUDE.md` that is a **durable repo-local instruction** Claude Code reads in *every*
session. It differs from the default `/init`: `/init` only **describes the current state** of the repo
(what it is, how to build it); this skill also **defines agent behavior** (Guardrails + Definition of
Done) and follows the canonical source's context-management discipline.

## Foundational principles (never violate)

From [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md):

- **"LLMs are stateless functions"** — `CLAUDE.md` is the *only* file loaded into *every* session. Every line must earn its place.
- **"Less is more"** — a model can follow ~150–200 instructions; the system prompt already takes ~50. Keep the file **under 300 lines, aim for ~60–120**.
- **"Prefer pointers to copies"** — point to `path/file.ts:42`, do NOT copy code snippets into the file.
- **No style/convention stuffing** — leave that to the linter/formatter. Don't write "use 2 spaces", "name things camelCase".
- **Only universally relevant content** — task-specific info goes elsewhere, link to it when needed (progressive disclosure).
- **Right altitude — don't hardcode rigid rules** — the canonical source warns of TWO EQUAL extremes: too vague *and* too rigid ("overly complex hardcoded logic"). Write stable heuristics/boundaries, do NOT stuff in if-this-then-that chains for every edge case (that makes `CLAUDE.md` brittle, contradictory, hard to maintain). A rule that's only true for one task → push it to a per-task file, don't cram it into `CLAUDE.md`.
- **Craft, don't auto-dump** — the canonical source says it plainly: *don't auto-generate*. This skill analyzes to *propose*, but must distill, not dump raw.
- **Write the NON-obvious** — drop the directory tree (the agent discovers it), drop generic advice ("write clean code").

The two parts that make a "harness" (which `/init` lacks):
- **Guardrails** — what the agent *must not* do, what it *must* do before declaring done, which operations need confirmation.
- **Definition of Done** — concrete evidence (tests pass, build green, lint clean) for the agent to self-verify before claiming completion.

## Procedure

### Step 1 — Identify the repo & scan the current state

- Target repo = `$ARGUMENTS` if given, otherwise the current directory. Confirm it's a git repo (`git rev-parse --show-toplevel`).
- If a `CLAUDE.md` already exists → read it, propose *improvements* rather than blindly overwriting. Ask before overwriting.
- Gather existing sources to consolidate (don't leave them scattered): `README.md`, `.cursorrules` / `.cursor/rules/`, `.github/copilot-instructions.md`, `AGENTS.md` if present.

### Step 2 — Infer WHAT / WHY / HOW (automatic, dense)

Analyze the codebase; do NOT ask for what you can infer:

- **HOW (highest priority — the agent needs it to run the loop):**
  - Build / run / test / lint / typecheck — read from `package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, CI workflows…
  - **The command to run a SINGLE test** — you must find it (e.g. `pytest path::test_x`, `vitest run -t "name"`, `go test -run`). This is the biggest feedback-loop speed-up.
  - Specific tooling: `bun` vs `node`, `uv` vs `pip`, which package manager.
- **WHAT:** tech stack, module boundaries, a "map" of the codebase (especially important for a monorepo). Describe the *big picture you only get from reading many files*, do NOT list every file.
- **WHY:** the project's purpose, the role of each major part — 1–3 sentences.

### Step 3 — Ask to confirm EXACTLY the 2 things you can't infer (in a single round)

Use AskUserQuestion, bundling everything into one round (respect the context budget):

1. **Guardrails** — suggest candidates from the repo, then ask to confirm:
   - Files/dirs that must NOT be edited (generated, already-run migrations, lockfiles, `dist/`, `vendor/`).
   - Operations that need confirmation first (running a migration, deleting data, pushing, editing CI/secrets).
   - Mandatory rules ("always run tests before declaring done", "don't add a new dependency without asking").
2. **Definition of Done** — when does a change count as finished? (e.g. `<test command>` green + `<lint>` clean + `<typecheck>` pass). This is what the agent uses to self-verify.

If the repo is very large / multi-module → ask whether to **layer** it: a lean root `CLAUDE.md` + child files for complex modules (closest-file-wins). Default: root only.

### Step 4 — Write CLAUDE.md to the template

Must begin with:

```md
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

Content template (drop any section that doesn't truly apply — don't invent):

```md
## What this repo is
<WHY + WHAT: 1–3 sentences. The thing you can't get from reading one file.>

## Build / Test / Run
- Build: <command>
- Run all tests: <command>
- Run a SINGLE test: <exact copy-paste command>
- Lint / typecheck: <command>
- Specific tooling: <bun/uv/...>

## Architecture overview
<Big picture you only get from reading many files: the main flow, module boundaries,
where the system's "heart" is. Use pointers path/file.ts:line, don't copy code.>

## Conventions (only the NON-obvious)
<Mandatory patterns the agent can't guess. NO style/format — leave that to the linter.>

## Guardrails
- DON'T edit: <files/dirs>.
- ALWAYS <run tests/lint> before declaring done.
- Require confirmation before: <dangerous operation>.

## Definition of Done
A change is done when: <concrete evidence — tests green, build ok, lint clean>.
```

### Step 5 — Self-check before handing off

Compare the file you wrote against the checklist; fix any violation:

- [ ] Under 300 lines (ideally <120). If long → cut, push task-specific detail to a separate file + link.
- [ ] No directory tree, no generic advice, no surplus style/convention.
- [ ] Uses pointers (`path:line`) instead of copied snippets.
- [ ] Has a single-test command, copy-paste runnable.
- [ ] Has Guardrails and Definition of Done sections (this is what makes it a "harness").
- [ ] Guardrails/conventions are boundary-level heuristics, NOT if-this-then-that chains for each edge case; rules true for only one task are pushed to a per-task file.
- [ ] Every command checked actually exists in the repo (don't invent scripts that aren't there).

### Step 6 — Report

Summarize for the user: which files were created/updated, which sources were consolidated (Cursor/Copilot/README), the line count, and the Guardrails/DoD that were locked in. Note: **AGENTS.md for Codex comes in a later round** (then it's just `ln -s AGENTS.md CLAUDE.md` to share one source).

## Out of scope (for now)

- Doesn't generate `AGENTS.md` / no symlink — saved for a later round on request (focus Claude Code first).
- Doesn't set up hooks/settings.json/MCP — those are other harness pillars, done separately.
