# /gsd:start-to-end

## Purpose

Run full lifecycle:
Init → Plan → Execute → Deliver

---

## Flow

Step 1 → Trigger /gsd:init-project
Step 2 → Trigger /gsd:plan-phases
Step 3 → Execute missions one by one via /gsd:execute-phase
Step 4 → Final review & cleanup

---

## Rules

- Never skip user confirmation between phases.
- Pause between major transitions.
- Ensure Git hygiene across all phases.
- Track completed missions.

---

## Token Optimization

- Reference prior skill outputs.
- Avoid reprinting large plans.
- Only print summaries when switching phases.

---

## Final Delivery Checklist

- All missions marked complete
- README updated
- CLAUDE.md updated
- Clean git history
- No debug code
- Deployment instructions added
