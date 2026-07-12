# Q3 — Risk / anomaly monitoring

## Purpose

Desk-shaped habit: **limits, breaches, escalation** — maps to how junior risk / trading support thinks.

## Limits (editable in `run_risk_monitor.py`)

- Max daily loss (R)  
- Max drawdown (R)  
- Max losing streak  

## Output

`risk_report.html` — alert table + daily net R.

Feeds from `q1_journal/sample_trades.csv` so journal and risk stay one system.
