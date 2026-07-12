# Alpha sample write-up (GAR)

**Script:** `run_alpha_sample.py`  
**Desk:** $100k · **1.25%** risk/trade  

## Hypothesis

Fade short-horizon return stretches (z-scored residual) **only** when price is on the same side of a slower trend SMA — mean reversion with a trend gate.

## Why this is here

GAR wants a research loop: idea → code (NumPy-style / pure Python) → metrics → keep or kill.  
This is a **toy alpha** on sample OHLC, not a production market-neutral book.

## Pair with

- `run_backtest.py` — rules/systematic simulation (OB/MS v0) for GAT narrative  
- `../q3_kill_log/` — retirement criteria for dead ideas  
