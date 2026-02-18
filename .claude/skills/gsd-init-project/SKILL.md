# /gsd:init-project

## Purpose

Understand the project deeply before planning or coding.
Create a structured project foundation and Claude environment.

---

## Execution Rules

1. Ask structured questions grouped by:
   - Product Vision
   - Target Users
   - Core Problem
   - Tech Stack
   - Infrastructure
   - UI/UX preferences
   - Constraints (budget, hosting, time)
   - Non-functional requirements (security, performance, scalability)

2. Avoid asking redundant questions.
3. Use bullet format.
4. Do not provide implementation suggestions unless asked.
5. Summarize understanding before proceeding.

---

## UI/UX Sub-Skill (Embedded Behavior)

- Ask about:
  - Design inspiration (Dribbble, 21st.dev, etc.)
  - Branding tone
  - Accessibility requirements
  - Device priority
- Suggest optional UI direction only after user answers.

---

## Output Requirements

After answers:

1. Generate:
   - PROJECT_OVERVIEW.md
   - CLAUDE.md (environment instructions)
   - TECH_STACK.md
   - PRODUCT_REQUIREMENTS.md

2. Keep files concise and structured.
3. Avoid verbose explanation.

---

## CLAUDE.md Must Include

- Project goal
- Stack
- Code style rules
- Folder structure conventions
- Git branching rules
- Token efficiency guidelines
- Response style (concise, no fluff)

---

## Token Saving Rules

- Never restate the entire project in each reply.
- Use reference shorthand after initial summary.
- Avoid long explanations.
- Ask batch questions instead of sequential ones.
- Use structured markdown instead of paragraphs.

---

## GitHub Instructions

- If new project → create new repo.
- Commit with:
  feat(init): project foundation and environment setup
- Clean commit messages.
- No meaningless commits.
- Branching:
  - For setup phase → main is acceptable.
  - For changes after initialization → create branch:
    feature/project-setup-enhancements
