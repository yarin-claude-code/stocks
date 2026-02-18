# /gsd:execute-phase

## Purpose

Execute one mission at a time in a controlled, minimal-token way.

---

## Execution Protocol

1. Restate mission goal in 3 lines max.
2. Confirm with user before starting.
3. Execute step-by-step.
4. After execution:
   - Show diff summary
   - Ask if user wants modifications

---

## Reflection Step (MANDATORY)

After completing mission:

- What was implemented
- What remains
- Possible improvements (short list)
- Ask for approval to commit

---

## Token Efficiency Rules

- Never restate entire phase plan.
- Only reference mission ID.
- No verbose explanation of known concepts.
- Provide only relevant code.
- Avoid unnecessary comments inside code.

---

## GitHub Workflow

For each mission:

- Commit:
  feat(mission-x.y): short description

If mission modifies architecture:

- Use branch

If minor fix:

- fix(mission-x.y): description

Before committing:

- Review changes
- Remove debug logs
- Ensure formatting is clean
