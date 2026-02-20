---
name: verify-frontend
description: Use Playwright MCP to visually verify frontend changes. Use after modifying React components, pages, or styles to confirm the UI renders and behaves correctly.
allowed-tools: mcp__playwright__*, Bash(cd *)
---

## Verify Frontend with Playwright

Use the Playwright MCP browser to visually inspect and interact with the running frontend.

### Prerequisites
Make sure the frontend dev server is running:
```bash
cd C:/claude-projects/investment-project/frontend && npm run dev
```

### Step 1: Navigate to the app
Use `mcp__playwright__browser_navigate` to open `http://localhost:5173`

### Step 2: Take a screenshot to confirm render
Use `mcp__playwright__browser_screenshot` to capture the current state.

### Step 3: Interact and verify the changed feature
- Use `mcp__playwright__browser_click` to click buttons/links related to the change
- Use `mcp__playwright__browser_type` to fill forms if needed
- Use `mcp__playwright__browser_screenshot` after each interaction

### Step 4: Check for console errors
Use `mcp__playwright__browser_console_messages` to surface any JS errors.

### Step 5: Report findings
Summarize: what rendered correctly, what (if anything) is broken, and any console errors.

### Step 6: Cleanup
- If all checks passed: delete any `.png` screenshots from `.playwright-mcp/`
- If something failed: fix the issue directly, then re-verify

### When to run this skill
Only invoke `/verify-frontend` when a React component, page, or style was added or modified. Do not run on backend-only changes.
