# Observability — see what the agent did (Level 5)

When an eval fails — or the agent "does something weird" — you need to *see* what it did, not guess.
Here's where to look, cheapest to deepest.

## Where to look

1. **The session transcript** — a record of *every* tool call the agent made (which files it read,
   which commands it ran, what it edited). This is the number-one source of truth for "why did it do
   that". Claude Code stores a per-session transcript under the project folder in `~/.claude/`.
2. **`/cost`** — the session's tokens & cost. An unusual spike = a sign of context bloat (re-reading
   surplus files, MCP tool stuffing) → pull it back to Level 2.
3. **Telemetry (for a whole team / background runs)** — Claude Code can export metrics/logs via
   OpenTelemetry: enable it with the `CLAUDE_CODE_ENABLE_TELEMETRY` env var, then point an OTLP
   exporter at your backend (Grafana, Honeycomb, Datadog…). Use it when you need to watch many
   sessions/agents, not just one. → Find the exact config in the Claude Code docs under *monitoring / telemetry*.
4. **A log hook (proactive audit)** — attach a `PostToolUse` hook that writes each tool call to a file
   (see [guardrails/README.md](../guardrails/README.md), the Hooks section). Handy for background runs you want to review later.

## Symptoms & which level they point to

Observability isn't just for debugging one session — it **surfaces harness gaps**:

| What you see in the trace | Problem | Fix at level |
|---------------------------|---------|--------------|
| Re-reading the same files; tokens climbing | dirty context | **Level 2** (subagent / `/clear` / prune MCP) |
| Constant permission prompts for safe commands | missing allowlist | **Level 3** (add to `allow`) |
| Nearly ran a destructive command | missing guard | **Level 3** (add to `deny`/`ask`) |
| Loses context mid-long-session, starts over | no checkpoint | **Level 4** (`TASK.md`) |
| Does it wrong and nobody notices until late | missing eval | **Level 5** (add a golden task) |
| Vague about "how do build/test run" | missing guidance | **Level 1** (CLAUDE.md) |
| Repeats the same mistake across sessions | rule never written down | **Level 1** (add one line to CLAUDE.md) |

**Closing the loop back to Level 1 — `CLAUDE.md` is a living document.** When the trace shows the agent
**repeating** a mistake Z (e.g. forgetting to run a migration, editing a generated file), don't just
fix it by hand this time: add **one line** of guardrail/convention to `CLAUDE.md` to prevent it next
time, then **re-run the golden task** to confirm the regression is gone. That's how `CLAUDE.md` grows
*from real mistakes*, instead of bloating on speculation.

## Principle

> Don't improve the harness on vibes. **Read the trace, let it point to the exact level to fix**, fix
> it, then re-run the golden task to confirm it actually got better. That's the whole Level 5 loop.
