# harness-kit

[Tiếng Việt](README.md) · **English**

> Set up a repo for a coding agent (Claude Code) across the **5 maturity levels** of harness
> engineering — in one command.

**Harness** = everything *around* the model (context, instructions, tools, safety constraints,
orchestration, measurement) that makes an agent reliable. This kit packages it into installable
**artifacts** plus a **tutorial** that teaches *when* to use each. The kit ships files; the tutorial
teaches the discipline.

## Quick install

```bash
npx harness-kit              # pick levels interactively, then install
npx harness-kit --all        # install all 5 levels
npx harness-kit --levels=1,3 # specific levels only
```

Requires **Node ≥18**. The command drops artifacts in the right places (`.claude/`, repo root,
`~/.claude/skills/`) and saves all docs into `docs/harness/` so your team keeps them. **Idempotent**
— safe to re-run (`--force` to overwrite). Prefer installing by hand to understand each level? See
the `cp` commands per level below — the installer just automates exactly those.

## What's in the kit — each level prevents a failure mode

| Level | Without it | Artifact |
|-------|------------|----------|
| **1 — Foundation** | the agent has no durable repo guidance | `/init-harness` skill → generates `CLAUDE.md` |
| **2 — Clean context** | context floods, the agent's attention dilutes | sample subagent + MCP audit checklist |
| **3 — Guardrails** | agent deletes/pushes by mistake, asks permission nonstop | `settings.json` (deny/ask/allow) |
| **4 — Long-running** | long tasks break mid-way, can't resume | `setup.sh`, `new-worktree.sh`, `TASK.md` |
| **5 — Evals & Obs** | no idea whether the agent does well or badly | golden-task template + observability guide |

## The 5 levels (detail + manual install)

### Level 1 — Foundation · `CLAUDE.md` &nbsp;`[do this first]`
```bash
cp -r skills/init-harness ~/.claude/skills/   # then run /init-harness in the target repo
```

### Level 2 — Clean context
```bash
mkdir -p .claude/agents && cp templates/agents/repo-explorer.md .claude/agents/
```
Read `templates/agents/README.md` + `templates/mcp-audit.md`.

### Level 3 — Guardrails &nbsp;`[points into CLAUDE.md]`
```bash
mkdir -p .claude && cp templates/settings.json .claude/settings.json
```
**First thing to do:** add your repo's test/lint commands to `allow` (see `templates/guardrails/README.md`).

### Level 4 — Long-running &nbsp;`[points into CLAUDE.md]`
```bash
cp templates/setup.sh templates/new-worktree.sh . && chmod +x setup.sh new-worktree.sh
cp templates/long-running/TASK.md .            # when starting a long task
```

### Level 5 — Evals & Observability &nbsp;`[needs ≥1 level applied to have something to measure]`
```bash
mkdir -p evals/cases && cp templates/evals/cases/example-task.md evals/cases/
```
Read `templates/evals/README.md` (includes a **no-harness baseline** step) + `observability.md`.

### + Specs (the other half of Pillar 2)
```bash
mkdir -p docs/specs && cp templates/spec/FEATURE.md docs/specs/<feature>.md
```

## Level dependencies

- **Level 1 first** — it's the backbone; later levels reference `CLAUDE.md`.
- **Levels 3 & 4** both "point `CLAUDE.md` to" their artifacts → require Level 1 done.
- **Level 5** needs at least one level applied to have a change to measure.

## Docs

`docs/harness-engineering-tutorial.md` (after install: `docs/harness/tutorial.md`) — the why + *when*
to use each piece. Note: the tutorial prose is in Vietnamese. Full industry-wide source catalog:
[Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering).

## License

[MIT](LICENSE).
