---
name: test-and-migrate
description: Run pytest and check Alembic migration state. Use after any backend schema or logic changes.
allowed-tools: Bash(cd *), Bash(python *), Bash(alembic *)
---

## Test and Migrate

Run tests and verify migration state for the investment project backend.

### Step 1: Run tests
```bash
cd C:/claude-projects/investment-project/backend && python -m pytest tests/ -v --tb=short
```

### Step 2: Check migration state
```bash
cd C:/claude-projects/investment-project/backend && alembic current && alembic heads
```

### Step 3: If schema changed, generate + apply migration
```bash
cd C:/claude-projects/investment-project/backend && alembic revision --autogenerate -m "$ARGUMENTS" && alembic upgrade head
```

### Step 4: Verify tests still pass after migration
```bash
cd C:/claude-projects/investment-project/backend && python -m pytest tests/ -v --tb=short
```
