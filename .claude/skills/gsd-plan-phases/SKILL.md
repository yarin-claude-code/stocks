# /gsd:plan-phases

## Purpose

Create a complete GSD execution roadmap.

---

## Planning Method

Follow this order:

1. Define Architecture Layer
2. Define Major Phases
3. Break Phases into Milestones
4. Break Milestones into Small Missions (atomic tasks)
5. Define success criteria for each mission

---

## Must Follow Best Practices

- Each mission must:
  - Be completable in 1 focused session
  - Have measurable output
  - Be independently testable
- Avoid vague tasks.
- Avoid combining frontend + backend in same mission unless necessary.

---

## Output Structure

PHASE 1: Foundation

- Mission 1.1
- Mission 1.2

PHASE 2: Core Features

- Mission 2.1

Each mission must include:

- Goal
- Technical Steps
- Files Impacted
- Definition of Done

---

## Token Efficiency Rules

- Do not repeat project description.
- Use compact structured formatting.
- No motivational text.
- No filler explanations.
- No example code unless required.

---

## GitHub Workflow

For major phases:

- Create branch:
  feature/phase-x-name

For planning updates:

- chore(plan): refine roadmap structure

Never commit planning drafts without cleanup.
