---
name: verify-ranking
description: Validate ranking algorithm math with edge cases. Use after modifying ranking_engine.py or factor weights.
allowed-tools: Bash(python *), Bash(cd *)
---

## Verify Ranking Engine

### Step 1: Run ranking-specific tests
```bash
cd C:/claude-projects/investment-project/backend && python -m pytest tests/test_ranking_engine.py -v
```

### Step 2: Edge case smoke test
```bash
cd C:/claude-projects/investment-project/backend && python -c "
from app.services.ranking_engine import normalize_factor, compute_composite, scale_to_0_100, rank_domain

# normalize: std==0 -> all 0.0
assert normalize_factor([5,5,5,5]) == [0.0,0.0,0.0,0.0], 'std==0 failed'

# normalize: fewer than 2 non-None -> all None
assert normalize_factor([1, None]) == [None, None], '<2 non-None failed'

# scale: max==min -> all 50.0
assert scale_to_0_100([3.0,3.0,3.0]) == [50.0,50.0,50.0], 'max==min failed'

# rank_domain: single stock -> score=50, rank=1
result = rank_domain({'AAPL': {'momentum':0.1,'volume_change':0.2,'volatility':0.3,'relative_strength':0.1,'financial_ratio':None}})
assert result['AAPL'].score == 50.0 and result['AAPL'].rank == 1, 'single stock failed'

# rank_domain: empty -> {}
assert rank_domain({}) == {}, 'empty domain failed'

print('All ranking edge cases passed')
"
```
