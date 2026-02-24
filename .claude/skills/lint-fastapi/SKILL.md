---
name: lint-fastapi
description: Check for async/session mixing, pure module violations, and common FastAPI mistakes. Use before committing new routes or DB changes.
allowed-tools: Bash(python *), Bash(cd *), Bash(grep *)
---

## FastAPI Lint Checks

### 1. Session mixing check — sync engine must NOT appear in routers
```bash
grep -r "_sync_engine\|Session(" C:/claude-projects/investment-project/backend/app/routers/ && echo "VIOLATION: sync session in router" || echo "OK: no sync session in routers"
```

### 2. Pure module check — ranking_engine must NOT import I/O deps
```bash
grep -n "import app\|import yfinance\|from app\|from yfinance" C:/claude-projects/investment-project/backend/app/services/ranking_engine.py && echo "VIOLATION: impure import in ranking_engine" || echo "OK: ranking_engine is pure"
```

### 3. ddof check — must use ddof=0 (population std)
```bash
grep -n "ddof=1" C:/claude-projects/investment-project/backend/app/services/ranking_engine.py && echo "VIOLATION: sample std used" || echo "OK: using population std"
```

### 4. Run full test suite
```bash
cd C:/claude-projects/investment-project/backend && python -m pytest tests/ -v --tb=short
```
