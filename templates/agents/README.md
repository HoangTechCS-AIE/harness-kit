# Subagents — how to write a good one (Level 2)

A subagent is **Level 2's main lever**: push heavy work (reading many files, big refactors,
repeated test runs) into a **separate context**, so the main context receives only *conclusions* —
it doesn't flood.

## Install

Each subagent is a `.md` file in `.claude/agents/` (repo-level) or `~/.claude/agents/` (user-level).
Copy the sample file there and Claude Code picks it up automatically:

```bash
mkdir -p .claude/agents
cp repo-explorer.md .claude/agents/
```

## File structure

```md
---
name: <kebab-case>
description: <WHEN to use it — Claude reads this line to decide whether to call this agent>
tools: Read, Grep, Glob        # (optional) give it only the tools it NEEDS, to keep it focused
---
<system prompt: role + how to work + ESPECIALLY how to RETURN>
```

## 4 rules you can't forget

1. **Write `description` as "when to use", not "what it is".** This is what the main agent reads
   to decide whether to delegate. Vague → it never gets called.
2. **A subagent must return a *distilled conclusion*, not a log.** The whole reason a subagent
   exists is so the main context does NOT have to swallow what it read. A raw dump defeats the purpose.
3. **`tools` lists only what's truly needed.** This is NOT a safety guardrail (that's Level 3) —
   it keeps the agent lean and focused. A comprehension agent only needs `Read, Grep, Glob`.
4. **One subagent = one clear job.** Don't merge "read + edit + test" into one agent. Different
   heavy jobs → different separate contexts.

## When you DON'T need a new subagent

Claude Code already ships `Explore` (read-only sweeps), `Plan` (design), and `general-purpose`.
They cover most context-isolation needs already. **Only write your own subagent when** you have a
recurring, domain-specific job the built-ins don't handle — don't spawn a redundant generic copy,
because surplus tools are exactly the context noise Level 2 teaches you to avoid.
