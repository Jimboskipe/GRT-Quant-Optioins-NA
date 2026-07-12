"""
Q2b — Simple alpha research sample (GAR-oriented)

Signal: 20-day mean reversion on excess return vs prior close,
filtered by 50-day trend (only fade stretches with the higher-TF trend).

Account framing: $100k equity, 1.25% risk per trade (desk defaults).
NOT a live-edge claim. Teaching research loop: hypothesis -> code -> metrics -> kill/keep.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OHLC = ROOT / "sample_ohlc.csv"
OUT = ROOT / "alpha_summary.txt"

ACCOUNT = 100_000.0
RISK_PCT = 1.25
LOOKBACK = 20
TREND = 50
ENTRY_Z = 1.25  # enter when residual stretch exceeds this (approx)
TARGET_R = 1.5
STOP_R = 1.0


def load(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sma(xs: list[float], n: int, i: int) -> float | None:
    if i + 1 < n:
        return None
    return sum(xs[i - n + 1 : i + 1]) / n


def stdev(xs: list[float], n: int, i: int) -> float | None:
    m = sma(xs, n, i)
    if m is None:
        return None
    window = xs[i - n + 1 : i + 1]
    var = sum((x - m) ** 2 for x in window) / n
    return math.sqrt(var)


def run(rows: list[dict]) -> dict:
    closes = [float(r["close"]) for r in rows]
    rets = [0.0] + [(closes[i] / closes[i - 1] - 1.0) for i in range(1, len(closes))]
    trades: list[float] = []
    i = max(LOOKBACK, TREND)
    while i < len(closes) - 2:
        mu = sma(rets, LOOKBACK, i)
        sd = stdev(rets, LOOKBACK, i)
        trend = sma(closes, TREND, i)
        if mu is None or sd is None or trend is None or sd == 0:
            i += 1
            continue
        z = (rets[i] - mu) / sd
        # Long mean-reversion only in uptrend after down-stretch
        side = None
        if closes[i] > trend and z <= -ENTRY_Z:
            side = "long"
        elif closes[i] < trend and z >= ENTRY_Z:
            side = "short"
        if side is None:
            i += 1
            continue
        entry = closes[i + 1]  # next bar open approx = next close for sample CSV simplicity
        # Fixed fractional R using ATR proxy = sd * price
        atr_proxy = max(sd * closes[i], closes[i] * 0.001)
        if side == "long":
            stop = entry - STOP_R * atr_proxy
            target = entry + TARGET_R * atr_proxy
            # path next few bars
            r_mult = 0.0
            for j in range(i + 1, min(i + 10, len(closes))):
                if closes[j] <= stop:
                    r_mult = -STOP_R
                    break
                if closes[j] >= target:
                    r_mult = TARGET_R
                    break
                r_mult = (closes[j] - entry) / atr_proxy
            trades.append(r_mult)
        else:
            stop = entry + STOP_R * atr_proxy
            target = entry - TARGET_R * atr_proxy
            r_mult = 0.0
            for j in range(i + 1, min(i + 10, len(closes))):
                if closes[j] >= stop:
                    r_mult = -STOP_R
                    break
                if closes[j] <= target:
                    r_mult = TARGET_R
                    break
                r_mult = (entry - closes[j]) / atr_proxy
            trades.append(r_mult)
        i += 5  # cool-down

    risk_cash = ACCOUNT * (RISK_PCT / 100.0)
    wins = [t for t in trades if t > 0]
    total_r = sum(trades) if trades else 0.0
    return {
        "n": len(trades),
        "win_rate": len(wins) / len(trades) if trades else 0.0,
        "expectancy_r": total_r / len(trades) if trades else 0.0,
        "total_r": total_r,
        "pnl_usd": total_r * risk_cash,
        "risk_cash": risk_cash,
        "params": {
            "LOOKBACK": LOOKBACK,
            "TREND": TREND,
            "ENTRY_Z": ENTRY_Z,
            "ACCOUNT": ACCOUNT,
            "RISK_PCT": RISK_PCT,
        },
    }


def main() -> None:
    m = run(load(OHLC))
    lines = [
        "=== Q2b GAR alpha sample (mean-reversion + trend filter) ===",
        "Hypothesis: fade stretched returns only with the 50-bar trend.",
        f"Params:     {m['params']}",
        f"Risk/trade: {RISK_PCT}% (${m['risk_cash']:,.0f}) on ${ACCOUNT:,.0f}",
        f"Trades:     {m['n']}",
        f"Win rate:   {m['win_rate']:.1%}",
        f"Expectancy: {m['expectancy_r']:+.2f} R",
        f"Total R:    {m['total_r']:+.2f}",
        f"Total P&L:  ${m['pnl_usd']:+,.2f}",
        "",
        "Limitations: sample OHLC; no costs/slippage; not walk-forward; not a live edge.",
        "Kill path: see ../q3_kill_log/ if expectancy or DD fails.",
    ]
    text = "\n".join(lines)
    print(text)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
