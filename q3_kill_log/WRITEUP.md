# Kill-criteria research log (Q3b — Trexquant)

## Purpose

Show **idea hygiene**: when an alpha / strategy idea is retired, and why — not only when it wins.

GAR: research discipline (do not keep dead signals).  
GAT: strategy lifecycle (simulation → kill or promote).

## Kill triggers (default desk)

| Code | Trigger | Action |
|------|---------|--------|
| `K1` | Expectancy ≤ 0 over rolling N trades | Pause; review rules |
| `K2` | Max drawdown in R exceeds limit | Flatten research size; rewrite |
| `K3` | Rule drift (live ≠ written RULES.md) | Immediate stop |
| `K4` | Data / costs invalidate edge assumption | Archive idea |
| `K5` | Daily loss kill fired 3+ times in 10 days | Reduce frequency / size |

## Sample log

See `kill_log.csv` + `run_kill_log.py` (prints HTML summary).

## Honesty

Rows are **illustrative** of the process. Replace with your real retired ideas when comfortable.
