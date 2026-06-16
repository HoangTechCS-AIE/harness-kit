# Harness Engineering for Teams — A Hands-on Tutorial (Claude Code & Codex)

[Tiếng Việt](harness-engineering-tutorial.md) · **English**

> For developers already using an AI coding agent who want to understand *why* an agent is sometimes good, sometimes bad — and *what to do* to make it more reliable.
> This is a condensed, practical guide based on the sources in [Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md). Every section links out for deeper reading.

---

## Table of contents

1. [What harness engineering is — and why you need it](#1-what-harness-engineering-is--and-why-you-need-it)
2. [Mental model: the 6 pillars of a harness](#2-mental-model-the-6-pillars-of-a-harness)
3. [Pillar 1 — Context & Working State](#3-pillar-1--context--working-state)
4. [Pillar 2 — Repo-local instructions & Specs (CLAUDE.md / AGENTS.md)](#4-pillar-2--repo-local-instructions--specs-claudemd--agentsmd)
5. [Pillar 3 — Tools & Environment](#5-pillar-3--tools--environment)
6. [Pillar 4 — Guardrails & Safe Autonomy](#6-pillar-4--guardrails--safe-autonomy)
7. [Pillar 5 — Long-running, Orchestration & Resumability](#7-pillar-5--long-running-orchestration--resumability)
8. [Pillar 6 — Evals & Observability](#8-pillar-6--evals--observability)
9. [Hands-on: write a repo's CLAUDE.md with `/init-harness`](#9-hands-on-write-a-repos-claudemd-with-init-harness)
10. [Team adoption checklist](#10-team-adoption-checklist)
11. [Further reading roadmap](#11-further-reading-roadmap)

---

## 1. What harness engineering is — and why you need it

The easiest analogy: a race car.

- **The model** (Claude, GPT…) = **the engine**. Powerful, but on its own it only produces tokens.
- **The harness** = **everything else in the car**: the chassis, steering, brakes, gauges, fuel system, seatbelts — i.e. everything *around* the model that turns it into an agent that does real work.

> **Harness Engineering** = the craft of designing and operating the environment around an agent (context, tools, constraints, orchestration, measurement) so the agent works **reliably**, especially on long-horizon programming tasks.

The field's core thesis: **when a coding agent produces poor results, it's mostly a harness problem, not a model problem.** Same model, different harness can swing benchmark scores dramatically — LangChain proved this with numbers in [Improving Deep Agents with harness engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/).

**Why should a coding team care?** Because every annoying symptom you hit with Claude Code/Codex is a harness problem:

| Symptom teams hit | This is a harness problem about… |
|---|---|
| Agent "forgets" what it was doing mid-task | Context & working state |
| Each person drives the agent differently, no consistency | Repo-local instructions / specs |
| Agent calls the wrong tool, or lacks a needed tool | Tool design & environment |
| Agent edits recklessly, deletes things, runs dangerous commands | Guardrails & safe autonomy |
| A 30-minute task dies partway and can't resume | Orchestration & resumability |
| Nobody knows whether the agent is doing well or badly | Evals & observability |

Foundational reads:
- [Harness Engineering — Thoughtworks/Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — splits the harness into context engineering, architectural constraints, and "garbage collection" against entropy.
- [The Anatomy of an Agent Harness — LangChain](https://blog.langchain.com/the-anatomy-of-an-agent-harness/) — agent = model + harness (prompts, tools, middleware, orchestration, runtime).
- [Skill Issue: Harness Engineering for Coding Agents — HumanLayer](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) — the "bang the table" piece arguing weak results are usually a harness fault.

---

## 2. Mental model: the 6 pillars of a harness

A more academic decomposition is **CAR — Control / Agency / Runtime** (from a [position paper on the harness layer](https://www.preprints.org/manuscript/202603.1756)): the harness simultaneously *controls* the agent, grants it *agency to act*, and is the *runtime* that runs it.

But to make it usable for a team, we use 6 practical pillars (mirroring the structure of [this repo's README](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md)):

```
                    ┌─────────────────────────────┐
                    │          MODEL              │
                    └─────────────┬───────────────┘
                                  │
   ┌──────────────┬──────────────┼──────────────┬──────────────┐
   │              │              │              │              │
1. Context    2. Specs/      3. Tools &     4. Guardrails  5. Orchestration
   & State        AGENTS.md      Environment    & Safety       & Resumability
   │              │              │              │              │
   └──────────────┴──────────────┴──────┬───────┴──────────────┘
                                         │
                              6. Evals & Observability
                              (measure to improve the 5 above)
```

The first five pillars *build* the harness. Pillar 6 (evals) is the *feedback loop* — without measuring, you can't tell whether a change actually made things better.

---

## 3. Pillar 1 — Context & Working State

**Principle #1:** treat the context window as a **working memory budget**, not a trash can to stuff everything into. Every token you put in context "dilutes" the model's attention. This is the central message of [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

Practical techniques (synthesized from [Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) and [OpenHands](https://openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents)):

- **KV-cache locality:** keep the prompt prefix (system prompt, instructions) *stable, unchanging* between steps → reuse the cache, cheaper and faster. Don't inject random timestamps/IDs at the top of the prompt.
- **Filesystem as external memory:** instead of cramming long files into context, let the agent read/write files (notes, scratchpad, intermediate results). Context holds only *pointers* to information, not all the information.
- **Keep failures in context:** when a command fails, don't hide the error — let the agent see the stack trace so it can self-correct. Hiding errors = the agent repeats the mistake.
- **Context condensation:** for long sessions, compress the conversation history but *preserve* the goal, progress, important files, and currently failing tests.
- **Backpressure:** don't let the agent burn context on noisy/low-value work (see [Context-Efficient Backpressure — HumanLayer](https://www.humanlayer.dev/blog/context-efficient-backpressure)).

**Specifically in Claude Code:**
- Context gets summarized when it grows long (compaction) — so important information *must* live somewhere durable (CLAUDE.md, files in the repo), don't just "say it" in chat.
- Use **subagents** to isolate context-heavy work (e.g. one agent reads 50 files and returns only the conclusion) → the main context doesn't flood.
- `/clear` when switching tasks to reset working state.

Read more: [Advanced Context Engineering for Coding Agents — HumanLayer](https://www.humanlayer.dev/blog/advanced-context-engineering), [Context Engineering for Coding Agents — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html).

---

## 4. Pillar 2 — Repo-local instructions & Specs (CLAUDE.md / AGENTS.md)

This is the **cheapest, highest-leverage** thing for a team — and the first thing to do.

The idea: instead of each dev "teaching" the agent from scratch every time, you write **one instruction file that lives in the repo** which the agent reads automatically. It's the team's "shared, durable memory".

- **Claude Code** reads `CLAUDE.md` (at repo root, and can be layered by subdirectory).
- **Codex** reads [`AGENTS.md`](https://github.com/agentsmd/agents.md) — an open, tool-neutral format (Codex, and many other agents, support it).

> Tip for teams using *both*: write the main content once, then make one file the source of truth and symlink/sync the other. Avoid two files drifting apart.

**What a good instruction file should contain** (per [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)):
- **How to build / test / lint / run** — including the command to run a *single* test.
- **Architecture overview** — the things you can only grasp after reading many files (the big picture), not a file-by-file listing.
- **Project-specific conventions** the agent can't guess (naming, entry format, ordering…).
- **Constraints** ("don't edit generated files", "always run tests before declaring done").
- **Avoid:** generic advice ("write clean code"), directory-tree listings (the agent can discover those).

**Spec-driven development** is the advanced step: for a large feature, write a clear spec *first*, then have the agent execute against the spec. A strong spec → far more consistent results.
- [GitHub Spec Kit](https://github.com/github/spec-kit) — a toolkit for spec-driven dev.
- [Understanding Spec-Driven Development — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html).
- [12 Factor Agents — HumanLayer](https://www.humanlayer.dev/blog/12-factor-agents) — production operating principles for agents: explicit prompts, the agent *owns* its state, clean pause/resume.

---

## 5. Pillar 3 — Tools & Environment

An agent acts through **tools** (read/write files, run commands, call APIs, MCP servers). Tool quality decides whether the agent calls the right thing or the wrong thing.

Principles for good tool design ([Writing effective tools for agents — Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)):
- Fewer, clearer tools > many overlapping ones. Too many tools make the model "fumble".
- Name + description + schema must state clearly *when to use it* and *what it returns*.
- Return concise, distilled information — don't dump raw output that floods context (back to pillar 1).
- Errors returned must be *actionable* (suggest how to fix), because the agent reads errors to self-correct.

**MCP (Model Context Protocol)** — the standard way to plug external tools/data sources into an agent (both Claude Code and Codex support it). Read:
- [Code execution with MCP — Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp) — grant execution rights across an explicit, inspectable tool boundary.
- Benchmarks measuring MCP integration quality: [MCP Bench](https://github.com/modelscope/MCPBench), [MCPMark](https://github.com/eval-sys/mcpmark).

**Environment** = the "world" the agent runs in (shell, filesystem, container, browser). A good harness controls this environment: sandbox it for safety, and provide the right verification tools (test runner, linter, browser to self-verify results).

---

## 6. Pillar 4 — Guardrails & Safe Autonomy

The goal: give the agent **as much autonomy as possible** while staying **safe** — reduce the number of manual "approve" clicks without losing control.

Techniques:
- **Sandboxing & policy:** confine the agent to an isolated environment, define clearly which operations are free / which need confirmation. See [Beyond permission prompts — Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing).
- **Prompt-injection defense:** when the agent reads external content (web, files, issues), that content may contain "hidden instructions" that trick the agent. Defend with confirmation mode, an analyzer, sandbox, hard policy — see [Mitigating Prompt Injection — OpenHands](https://openhands.dev/blog/mitigating-prompt-injection-attacks-in-software-agents).
- **Quality-in-the-loop:** put quality checks *inside the loop* (lint/test/typecheck run automatically) instead of manual review at the very end. [Assessing internal quality — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/ccmenu-quality.html).
- **Anchoring to a reference app:** constrain the agent with a concrete sample to keep output consistent. [Anchoring to a reference application — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/anchoring-to-reference.html).
- **Risk scanning before deploy:** [Lurkr](https://github.com/agentveil-protocol/lurkr) — a static scanner in CI to detect agent-capability risks (credentials leaking into LLM context, `eval`/subprocess inside a `@tool`, unverified MCP endpoints…).

**In Claude Code:** use permission modes, an allowlist in `settings.json`, and **hooks** (run a command automatically before/after a tool call — e.g. auto-format, or block dangerous commands). This is exactly how you "codify" guardrails for the whole team.

Mental model for the human's role: [Humans and Agents in Software Engineering Loops — Thoughtworks](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html) — humans should *reinforce the harness* rather than scrutinize every line of output.

---

## 7. Pillar 5 — Long-running, Orchestration & Resumability

This is the "hard and valuable" part: how an agent runs a long task *across multiple context windows* without getting lost.

Must-read original: [Effective harnesses for long-running agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). The main patterns:
- **Initializer agent:** an agent that sets up the environment/scaffolding before the main agent starts.
- **Feature list / task state:** a durable to-do list (written to a file) as the "source of truth" for progress — the agent ticks items off, and a fresh context window re-reads it to know where it is.
- **`init.sh`:** a script that standardizes environment setup so every run starts from a clean, repeatable state.
- **Self-verification:** the agent verifies its own results (run tests, build) before declaring done.
- **Handoff artifacts:** when context is about to fill up, write a "handoff record" so the next context window continues seamlessly.

See also the follow-up: [Harness design for long-running application development — Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps).

**Orchestration patterns:**
- **Multi-agent:** split roles (planner, coder, reviewer) and coordinate them in a structured way — [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system).
- **Ralph pattern:** a minimal harness `while :; do cat PROMPT.md | claude-code; done` — a single-task loop, deterministic stacked prompts, bounded parallel subagents. A fun-but-deep read: [Ralph Wiggum as a Software Engineer](https://ghuntley.com/ralph/).
- **Framework vs Runtime vs Harness** — draw the line clearly to know what belongs where: [Agent Frameworks, Runtimes, and Harnesses, Oh My! — LangChain](https://blog.langchain.com/agent-frameworks-runtimes-and-harnesses-oh-my/).

**Reference implementations to learn by reading code:**
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) — a research coding agent; harness/prompt/tools/env are all inspectable.
- [deepagents — LangChain](https://github.com/langchain-ai/deepagents) — patterns for long-horizon agents.
- [Citadel](https://github.com/SethGammon/Citadel) — a harness for Claude Code & Codex with isolated worktrees, multi-agent, durable memory.

**In Claude Code:** subagents, plan mode, worktree isolation, and TodoWrite (a durable in-session task list) are the embodiment of these patterns.

---

## 8. Pillar 6 — Evals & Observability

No measurement, no improvement. With agents, "measuring" is harder than regular code because there are *many paths* to success/failure.

**Observability — see what the agent actually does:**
- **Traces:** record every step (tool call, result, decision) for debugging and grading. Standardize with [OpenTelemetry Semantic Conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) so traces are portable across backends.
- Tools: [AgentOps](https://github.com/AgentOps-AI/agentops) (monitoring, session replay, cost tracking), [agenttrace](https://github.com/luoyuctl/agenttrace) (a local-first TUI/CLI to audit coding-agent traces: cost spikes, tool failures, latency gaps, diffs between attempts).

**Evals — grade quality:**
- Turn real traces into repeatable evals (JSONL log + deterministic check): [Testing Agent Skills with Evals — OpenAI](https://developers.openai.com/blog/eval-skills/), [How to Evaluate Agent Skills — OpenHands](https://openhands.dev/blog/evaluating-agent-skills).
- **Trace grading:** grade directly on the trajectory for multi-step tasks — [Trace grading — OpenAI](https://platform.openai.com/docs/guides/trace-grading).
- How to think about "what to measure when there are many trajectories": [Demystifying Evals for AI Agents — Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- An open eval framework: [Inspect AI — UK AISI](https://inspect.aisi.org.uk/) (solver, scorer, sandbox, tool-use, log viewer).

**Important warning:** runtime/infrastructure configuration can swing benchmark scores *more than* the gap between models on a leaderboard — i.e. "infra noise" can easily make you draw the wrong conclusion. Read [Quantifying infrastructure noise in agentic coding evals — Anthropic](https://www.anthropic.com/engineering/infrastructure-noise) before trusting a number.

**Benchmarks** (when you want to compare *harnesses*, not just models): start with [SWE-bench Verified](https://www.swebench.com/) (fix real GitHub issues) and [Terminal-Bench](https://www.tbench.ai/) (terminal-native agents). See also the [Benchmarks section in the README](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md#benchmarks) to pick by task type.

---

## 9. Hands-on: write a repo's CLAUDE.md with `/init-harness`

This is the first exercise to do with a team — the biggest lever, doable in one afternoon. This part focuses on `CLAUDE.md` (Claude Code); `AGENTS.md` for Codex comes later (see the end of the section).

### Don't auto-generate with the default `/init`

The canonical source [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md) says it plainly: ***"don't auto-generate with `/init` — carefully craft its contents"***. Why: `/init` only **describes the current state** of the repo, and still misses the two things that make a "harness" — **Guardrails** (constraints on agent behavior) and **Definition of Done** (evidence for the agent to self-verify).

Our team packaged this discipline into a skill: **`/init-harness`**.

### How to use it (recommended): type `/init-harness`

In Claude Code, in the target repo:

```
/init-harness            # or: /init-harness <repo-path>
```

The skill will: (1) scan the repo to fill in **WHAT/WHY/HOW** (stack, build/test/run, **single-test command**, architecture); (2) ask **one round** of questions to lock down **Guardrails + Definition of Done** — exactly the parts it can't guess; (3) generate the file under the discipline below and self-check.

### What the file it generates looks like

```md
# CLAUDE.md

## What this repo is
<WHY + WHAT: 1–3 sentences. The thing you can't get from reading one file.>

## Build / Test / Run
- Build / Run all tests / Lint / typecheck: <commands>
- Run a SINGLE test: <exact copy-paste command>   ← biggest speed-up to the feedback loop
  (no build/test repo — e.g. an awesome-list — then this becomes the real verification,
   e.g.: check links with `curl -sI <url>` before adding.)

## Architecture overview
<Big picture you only get from reading many files. Use pointers path/file.ts:42, DON'T copy code.>

## Project-specific conventions (only the NON-obvious)
<Mandatory patterns the agent can't guess. NO style/format — leave that to the linter.>

## Guardrails                      ← the default /init does NOT have this
- DON'T edit <generated files/dirs>.
- ALWAYS <run tests/lint> before declaring done.
- Require confirmation before: <dangerous operation>.

## Definition of Done              ← the default /init does NOT have this
A change is done when: <concrete evidence — tests green, build ok, lint clean>.
```

> **Real example (before/after):** [this repo's own CLAUDE.md](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/CLAUDE.md) was generated with `/init-harness`. The repo is an awesome-list with no build/test, so the "HOW" section was adapted into *verify links + lychee CI* — and it has the full `Guardrails` + `Definition of Done` the old `/init` lacked.

### Writing principles (quoting the canonical source)

From [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md):
- **"LLMs are stateless functions"** — `CLAUDE.md` is the *only* file loaded into *every* session. Every line must earn its place.
- **"Less is more"** — a model can follow ~150–200 instructions (the system prompt already takes ~50) → keep the file **<300 lines, aim for ~60–120**.
- **"Prefer pointers to copies"** — point to `path:line`, don't copy snippets.
- **Don't stuff in style/conventions** — leave that to the linter/formatter.
- **Craft, don't auto-dump** — analyze to *propose*, then distill.

### Sharing across Claude Code + Codex (later)

Per [agents.md](https://agents.md): an agent reads **the nearest file up the directory tree — closest-file-wins** (OpenAI's main repo has 88 nested `AGENTS.md` files), so a monorepo uses a root file + per-package overrides (exactly the "layering" `/init-harness` asks about when the repo is large). The standard migration: ***"rename existing files to AGENTS.md and create symbolic links for backward compatibility"***.

→ When the Codex round comes: move the content into `AGENTS.md` as the source of truth, then `ln -s AGENTS.md CLAUDE.md`. One source, two tools, never out of sync.

> Pick a strategy by codebase type: [Greenfield AI, Brownfield AI, and the Vibecode You Just Inherited](https://sawinyh.com/blog/greenfield-vs-brownfield-ai-codebases) — greenfield agent-native, legacy brownfield, and just-vibecoded code; each needs a different playbook (layered CLAUDE.md, progressively tightening pre-commit hooks, baseline lint).

---

## 10. Team adoption checklist

Paste this into your internal wiki. Go top to bottom — each item is a rung on the harness maturity ladder.

**Level 1 — Foundation (do this week)**
- [ ] Every main repo has a `CLAUDE.md` generated with `/init-harness` (see [Section 9](#9-hands-on-write-a-repos-claudemd-with-init-harness)), NOT raw `/init`.
- [ ] The file has full `Guardrails` + `Definition of Done` sections, not just build/test/architecture.
- [ ] There's a single-test command (or real verification method) written in the file.
- [ ] Convention: important info goes into repo files, not "spoken" in chat.

**Level 2 — Context & Tools**
- [ ] Use subagents/worktree for context-heavy work (reading many files, big refactors).
- [ ] `/clear` when switching tasks; condense context for long sessions.
- [ ] Audit configured MCP servers: which are truly needed, which add context noise.

**Level 3 — Guardrails**
- [ ] Configure permission/allowlist in `settings.json` for safe operations.
- [ ] Automated hooks (format, block dangerous commands) for the whole team.
- [ ] Test/lint/typecheck run *in the loop*, not as a final manual review.
- [ ] (If the agent reads external content) have a prompt-injection defense.

**Level 4 — Long-running**
- [ ] Long tasks have a durable feature-list/task-state (file or TodoWrite).
- [ ] The agent self-verifies (runs tests/build) before declaring done.
- [ ] There's an `init.sh`/setup script that's repeatable.

**Level 5 — Evals & Observability**
- [ ] Turn on trace/observability to see what the agent does + cost.
- [ ] At least a few repeatable evals for important tasks (with a "no-harness" baseline).
- [ ] When comparing numbers, control for infra noise before concluding.

---

## 11. Further reading roadmap

Read in this order if starting from zero:

1. **Concepts:** [Thoughtworks — Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) → [LangChain — Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
2. **Two heavy originals:** [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) + [OpenAI — Harness engineering with Codex](https://openai.com/index/harness-engineering/)
3. **Context (pays off most when coding):** [Anthropic — Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) + [Manus — Lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
4. **Apply it:** [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) + [AGENTS.md](https://github.com/agentsmd/agents.md) → then run `/init-harness` to generate the file for your team's repo ([Section 9](#9-hands-on-write-a-repos-claudemd-with-init-harness))
5. **Measure:** [Anthropic — Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

> The full catalog (foundations, context, guardrails, specs, evals, benchmarks, runtimes) lives in [this repo's README](https://github.com/walkinglabs/awesome-harness-engineering/blob/main/README.md) — treat it as the main reference library.
