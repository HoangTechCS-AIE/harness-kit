# Guardrails — permission baseline (Level 3)

Level 3 controls **what the agent is allowed to do** — the safety boundary. Unlike Level 2 (a *clean*
context), Level 3 is about *safe* actions: block destructive commands, ask before risky ones, let
safe ones run straight through.

## Install

Copy `settings.json` into the repo's `.claude/`:

```bash
mkdir -p .claude
cp settings.json .claude/settings.json
```

**Why `.claude/settings.json` (not `settings.local.json`):** this file is **checked into the repo**,
so everyone who clones it **inherits the same guardrails automatically**. `settings.local.json` is a
personal override (gitignored) — use it for machine-specific tweaks, not to impose on the team.

> **The FIRST thing to do after copying — add test/lint/build commands to `allow`.** The baseline
> deliberately only allows read-only git. Without your repo's feedback loop, Claude asks permission
> *every time* it runs tests → you fall into the "click yes to get it over with" habit the *Insight*
> section below calls the real danger. Open `.claude/settings.json` and add your stack's commands to `allow`:
>
> - **Node:** `"Bash(npm run test:*)"`, `"Bash(npm run lint:*)"`, `"Bash(npm run build:*)"`
> - **Python:** `"Bash(pytest:*)"`, `"Bash(ruff:*)"`, `"Bash(mypy:*)"`
> - **Go:** `"Bash(go test:*)"`, `"Bash(go build:*)"`, `"Bash(go vet:*)"`
>
> This is **mandatory, not optional** — a fast feedback loop is the thread running through the whole kit.

## The 3-bucket model

Every action (run bash, read/edit a file) falls into one of 3 buckets:

| Bucket | Meaning | Examples in the baseline |
|--------|---------|--------------------------|
| **deny** | absolutely forbidden, the agent can't call it | `rm -rf`, read `.env`/`secrets/**`, read `*.pem` keys |
| **ask** | stop and ask you first | `git push`, `git reset --hard`, `git clean`, `rm` |
| **allow** | run straight through, no prompt | `git status`, `git diff`, `git log`, `git branch` |

Rule syntax: `Tool(specifier)`.
- Bash matches by **prefix**: `Bash(npm run test:*)` matches any command starting with `npm run test`.
- Files match **gitignore-style**: `Read(./secrets/**)`, `Edit(./dist/**)`.

## Extend it for your repo

The baseline is deliberately **minimal and universal**. Add what's specific to your repo:

- **Into `allow`** — safe, daily commands so you aren't asked constantly:
  `Bash(npm run test:*)`, `Bash(npm run lint:*)`, `Bash(pytest:*)`, `Bash(make:*)`.
- **Into `ask`** — repo-specific actions with *big consequences*:
  running a migration (`Bash(npm run migrate:*)`), deploys, `Bash(docker compose down:*)`.
- **Into `deny`** — paths that must never be edited/read:
  `Edit(./dist/**)`, `Edit(./vendor/**)`, `Read(./**/*.key)`.

> Tip: don't over-stuff `allow`. Every time Claude asks is a chance for you to *review* — over-stuffing
> `allow` throws away your own review checkpoint.

## Insight: deny ≠ airtight security

A deny-list **doesn't** stop an adversary (an agent can route around it: write `rm` via a script,
base64…). It's a **safety net + friction reducer**:
- `deny`/`ask` block **accidents** (deleting/pushing by mistake) — they guard against *errors*, not *attacks*.
- `allow` lets safe commands run straight through → you avoid the "click yes to get it over with"
  habit (that habit is the real danger).

**Real safety** is still **reviewing diffs + plan mode** before letting the agent act — that's runtime
discipline, not something you can package into a file.

## External content & prompt injection

The `deny`/`ask` rules above block *accidents*; they **don't** stop prompt injection. Content the agent
reads from the web, issues, PRs, logs… is **data — not commands**, but an attacker can hide instructions
in it to steer the agent. This is **runtime discipline** (so the kit ships no pre-baked hook/CI-scan), a
few practical guards:

- Read external content (web/issue/PR) in **plan mode** — the agent *proposes* before it *acts*.
- DON'T let the agent auto-run a command / `curl` pulled out of content it just fetched.
- Untrusted input → split into a **separate session**; don't mix it into a high-privilege session.

Automated CI scanning and deeper background: see `docs/harness-engineering-tutorial.md` (the **Lurkr**
link for CI-scan, **OpenHands — mitigating prompt injection** for the background).

## Advanced (optional): Hooks

When you need *logic* beyond static allow/deny — e.g. "block every edit to a protected path", "auto-run
lint after each edit" — use a **hook**: a script that runs *before/after* every tool call. Declare it in
`settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": ".claude/hooks/guard.sh" }] }
    ]
  }
}
```

The script reads the tool-call JSON from stdin; **exit code 2 = block**, with a message on stderr.
Because a blocking hook is repo-specific, the kit **ships none** — it just points the way. Write one
when you genuinely have a recurring rule that static allow/deny can't express.

**Audit-log (`PostToolUse`)** — record *every* tool call to review later. This is what
`evals/observability.md` (Level 5) points to; this hook is **generic, not repo-specific**:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "*", "hooks": [{ "type": "command", "command": ".claude/hooks/audit-log.sh" }] }
    ]
  }
}
```

`audit-log.sh` just appends the stdin payload to a file — one JSON tool-call per line:

```bash
#!/usr/bin/env bash
cat >> .claude/audit.log
```
