# MCP hygiene — a checklist for pruning surplus tools (Level 2)

Every MCP server you plug in **injects all of its tool definitions into context on EVERY turn** —
even turns that don't use it. Five rarely-used servers can eat thousands of tokens per turn and
make the model "fumble" when choosing a tool. This is a **permanent context tax**, not a safety
issue (safety is Level 3).

## See what's plugged in

```bash
claude mcp list        # list the configured MCP servers
```

## For EACH server, ask 3 questions

- [ ] **Did you actually call its tools in the past month?** No → remove it.
- [ ] **How many tools does it add per turn when you only use 1–2?** Lots of surplus → remove it or find a leaner build.
- [ ] **Can an existing CLI replace it?** (e.g. `gh` instead of a GitHub MCP for simple things) → prefer the CLI, drop the MCP.

## Principle

> **Few clear tools > many overlapping ones.** Keep exactly what you use weekly.
> Add more only when you *genuinely* need a new source/capability, not "just in case".

Plugging in an MCP "just in case" is the most common Level 2 trap: it quietly makes every session
more expensive and less accurate, without anyone noticing.
