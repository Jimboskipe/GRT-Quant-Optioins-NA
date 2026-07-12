# Q2 — OB / Market Structure backtest (your rules v0)

## Purpose

Code **your** process (order block + market structure + sweep + risk limits) as an explicit, runnable backtest — not an SMA toy and not a claimed live edge.

## Read first

**[RULES.md](RULES.md)** — full v0 ruleset. Confirm or edit parameters in `run_backtest.py`.

## Flow

1. Detect swing highs/lows (market structure)  
2. Liquidity sweep of prior swing + displacement  
3. Mark order block (last opposing candle)  
4. Enter on OB retest  
5. Stop beyond sweep/OB; target `TARGET_R` (default 2R)  
6. Daily loss kill switch  

## Files

| File | Role |
|------|------|
| `RULES.md` | Human rules |
| `run_backtest.py` | Implementation |
| `sample_ohlc.csv` | Demo bars (may be thin for OB setups) |
| `fetch_mt5_sample.py` | Pull real MT5 OHLC |
| `backtest_summary.txt` | Last run output |

## Honesty

v0 is a **structured proxy** of how you described trading. If your live markers differ, change PARAMS or tell me the exact invalidation / OB definition and I’ll update the code.
