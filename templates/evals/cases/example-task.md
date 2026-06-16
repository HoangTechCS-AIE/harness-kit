<!--
A "golden task" = one representative job + OBJECTIVE pass criteria, so it can be re-run after every
harness change. Copy this file per case. Name it after the job: add-endpoint.md, fix-flaky-test.md...

Principle: done-criteria must be MACHINE-checkable where possible (a command that returns pass/fail);
fall back to human grading only when unavoidable. "Looks right" is NOT a criterion.
Delete this comment when you use it for real.
-->

# Case: <the job — e.g. "add endpoint GET /users/:id">

## Task (give this verbatim to the agent)
<The exact prompt you'd type to the agent. The closer to reality, the better.>

## Setup (what state the repo must be in before running)
<Base branch/commit, seed data, env vars. So the case repeats identically every time.>
- Base: <commit/branch>
- 

## Done-criteria (OBJECTIVE — clear pass/fail)
<What MUST be true after the agent finishes. Prefer commands that return pass/fail.>
- [ ] `<test command>` green
- [ ] `<lint / typecheck command>` clean
- [ ] <a concrete change exists — e.g. "new route returns 200 for a valid id, 404 otherwise">
- [ ] Did NOT touch <out-of-scope file/path>

## How to grade
<If automatable, write the exact command. If it must be manual, write a short rubric; don't leave it "implied".>
- Automated: `<command that returns an exit code>`
- Manual (if needed): <1–2 sentence rubric>

## Reference (optional)
<A "correct" commit/PR to compare against, if any. Helps see where the agent diverged.>
