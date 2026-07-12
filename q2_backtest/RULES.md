# James Doyle — OB / Market Structure Rules (v0)

**Status:** Draft coded for backtest — **confirm or edit**.  
**Source:** Your Ace notes + journal tags (`ob_ms`, sweeps, invalidation, daily loss stop, one A+ after reset).

This is **not** a claim of a proven live edge. It turns your described process into explicit, testable rules.

---

## Setup idea (what you said)

- Trade **order blocks (OB)** and **market structure (MS)**  
- Look for **liquidity sweeps** / “big money” stops then continuation  
- Avoid chasing after **invalidation**  
- **Risk 1.25%** per trade on a **$100k** backtest account ($1,250 / trade)  
- **Max daily loss** → stop trading that day  
- Prefer **A+ setups** only after a reset / loss day  

---

## Coded rules (v0 parameters)

| Step | Rule | Default param (edit in `run_backtest.py`) |
|------|------|-------------------------------------------|
| 1. Swings | Pivot high/low with `L` bars each side | `SWING_L = 3` |
| 2. Sweep | Price runs beyond prior swing, then closes back inside | required for setup |
| 3. Displacement | Next move impulsively away from sweep (≥ `DISP_ATR` × ATR) | `DISP_ATR = 1.2` |
| 4. Order block | Last opposing candle before that displacement | zone = that candle’s range |
| 5. Entry | First return into OB zone in trend direction | touch + close still in direction |
| 6. Stop | Beyond sweep extreme (or OB far side) | + tiny buffer `STOP_BUF_ATR` |
| 7. Target | Fixed R multiple | `TARGET_R = 2.0` |
| 8. Risk | **1.25%** of **$100k** equity per trade ($1,250 = 1R) | `ACCOUNT_EQUITY=100000`, `RISK_PCT=1.25` |
| 9. Daily kill | If day net ≤ `MAX_DAILY_LOSS_R`, no new trades | `-2.0` R |
| 10. No chase | After a stopped trade, skip re-entry same direction until new sweep | on |
| 11. Bias | Trade with structure: long only after bullish BOS context, short after bearish | swing break |

---

## What to send me if this is wrong

Reply with corrections only where needed, for example:

- How you mark an OB (which candle, timeframe)  
- Exact invalidation (close through OB? wick?)  
- Targets (fixed R vs opposite liquidity)  
- Sessions you trade  
- Whether Markov rules are in the live plan yet (v0 does **not** include Markov)

---

## Files

- `run_backtest.py` — implements this v0  
- `RULES.md` — this document  
- `fetch_mt5_sample.py` — optional live OHLC  
