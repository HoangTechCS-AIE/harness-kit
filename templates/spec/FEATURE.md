<!--
FEATURE.md — spec one feature BEFORE writing code (spec-driven development).

This is the "Specs" half of the "Repo-local instructions & Specs" pillar: CLAUDE.md (Level 1) covers
durable rules across EVERY task; FEATURE.md defines ONE specific feature before you start. A clear spec
→ the agent runs in the right direction; clear acceptance criteria → something a Level 5 eval can grade.

How to use: copy it per significant feature (e.g. docs/specs/<feature>.md). Skip small jobs — don't
ritualize it. Fill in the sections, delete this comment when you use it for real.
-->

# Feature: <short name>

## Problem / why
<What it solves and for whom. 1–3 sentences. If you can't state the "why", don't code yet.>

## Scope

### In scope
- 

### OUT of scope (important — blocks scope creep)
- 

## Constraints
<Technical/business musts: API must stay stable, no new dependencies, performance limits…>
- 

## Acceptance criteria (measurable — clear pass/fail)
<What MUST be true for the feature to count as done. This also feeds the Level 5 golden task.>
- [ ] 
- [ ] 

## Test hooks
<Which tests / commands will check it. Prefer things that can be automated.>
- 

## Design notes & decisions locked
<Approach + a short why. So the next person (and the agent) don't re-litigate from scratch.>
- 
