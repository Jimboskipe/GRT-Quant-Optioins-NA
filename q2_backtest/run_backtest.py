"""
Q2 - OB / Market Structure backtest (James Doyle rules v0)

See RULES.md for the human-readable ruleset.
Edit PARAMS below if your live rules differ.

NOT a live-edge claim. Teaching/portfolio implementation of your process.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OHLC = ROOT / "sample_ohlc.csv"
OUT = ROOT / "backtest_summary.txt"

# --- PARAMS (James: change these to match your desk) ---
SWING_L = 3
DISP_ATR = 1.2
ATR_N = 14
STOP_BUF_ATR = 0.1
TARGET_R = 2.0
MAX_DAILY_LOSS_R = -2.0
ACCOUNT_EQUITY = 100_000.0  # backtest account
RISK_PCT = 1.25  # % of equity risked per trade -> $1,250 risk on $100k


@dataclass
class Bar:
    time: str
    open: float
    high: float
    low: float
    close: float


def load_ohlc(path: Path) -> list[Bar]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [
        Bar(
            time=r["time"],
            open=float(r["open"]),
            high=float(r["high"]),
            low=float(r["low"]),
            close=float(r["close"]),
        )
        for r in rows
    ]


def atr(bars: list[Bar], n: int) -> list[float | None]:
    out: list[float | None] = [None] * len(bars)
    trs: list[float] = []
    for i, b in enumerate(bars):
        if i == 0:
            tr = b.high - b.low
        else:
            prev = bars[i - 1].close
            tr = max(b.high - b.low, abs(b.high - prev), abs(b.low - prev))
        trs.append(tr)
        if i >= n - 1:
            out[i] = sum(trs[i - n + 1 : i + 1]) / n
    return out


def swing_points(bars: list[Bar], L: int) -> tuple[list[float | None], list[float | None]]:
    """Pivot high/low: extreme vs L bars on each side."""
    sh: list[float | None] = [None] * len(bars)
    sl: list[float | None] = [None] * len(bars)
    for i in range(L, len(bars) - L):
        window = bars[i - L : i + L + 1]
        if bars[i].high == max(b.high for b in window):
            sh[i] = bars[i].high
        if bars[i].low == min(b.low for b in window):
            sl[i] = bars[i].low
    return sh, sl


@dataclass
class Setup:
    side: str  # long | short
    ob_low: float
    ob_high: float
    stop: float
    created_i: int


def last_opposing_candle(bars: list[Bar], i_disp_start: int, side: str) -> tuple[float, float] | None:
    """Order block proxy: last candle against the displacement before impulse."""
    for j in range(i_disp_start, max(0, i_disp_start - 8), -1):
        b = bars[j]
        if side == "long" and b.close < b.open:  # last bearish before up move
            return b.low, b.high
        if side == "short" and b.close > b.open:  # last bullish before down move
            return b.low, b.high
    return None


def run(bars: list[Bar]) -> dict:
    a = atr(bars, ATR_N)
    sh, sl = swing_points(bars, SWING_L)

    last_swing_high: float | None = None
    last_swing_low: float | None = None
    bias = 0  # 1 bullish structure, -1 bearish

    pending: Setup | None = None
    position = None  # dict with side, entry, stop, target, day
    trades: list[float] = []
    day_r: dict[str, float] = {}
    skipped_chase = 0

    def day_key(t: str) -> str:
        return t[:10]

    def day_ok(d: str) -> bool:
        return day_r.get(d, 0.0) > MAX_DAILY_LOSS_R

    for i in range(len(bars)):
        b = bars[i]
        d = day_key(b.time)
        day_r.setdefault(d, 0.0)

        if sh[i] is not None:
            last_swing_high = sh[i]
            if last_swing_low is not None and b.close > (last_swing_high or b.close):
                bias = 1
        if sl[i] is not None:
            last_swing_low = sl[i]
            if last_swing_high is not None and b.close < (last_swing_low or b.close):
                bias = -1

        # Manage open trade
        if position is not None:
            side = position["side"]
            hit_stop = b.low <= position["stop"] if side == "long" else b.high >= position["stop"]
            hit_tgt = b.high >= position["target"] if side == "long" else b.low <= position["target"]
            if hit_stop or hit_tgt:
                r = -1.0 if hit_stop and not (hit_tgt and not hit_stop) else TARGET_R
                # If both in same bar, conservative: count stop first
                if hit_stop and hit_tgt:
                    r = -1.0
                elif hit_tgt:
                    r = TARGET_R
                else:
                    r = -1.0
                trades.append(r)
                day_r[d] += r
                # no chase: clear pending same side
                if r < 0:
                    pending = None
                position = None
            continue

        if not day_ok(d):
            pending = None
            continue

        if a[i] is None or a[i] <= 0:
            continue

        # Detect sweep + displacement -> form OB setup
        # Long: sweep prior swing low, then displace up
        if (
            last_swing_low is not None
            and bias >= 0
            and b.low < last_swing_low
            and b.close > last_swing_low
            and (b.close - b.open) >= DISP_ATR * a[i]
        ):
            ob = last_opposing_candle(bars, i, "long")
            if ob:
                ob_low, ob_high = ob
                stop = min(b.low, ob_low) - STOP_BUF_ATR * a[i]
                pending = Setup("long", ob_low, ob_high, stop, i)

        # Short: sweep prior swing high, then displace down
        if (
            last_swing_high is not None
            and bias <= 0
            and b.high > last_swing_high
            and b.close < last_swing_high
            and (b.open - b.close) >= DISP_ATR * a[i]
        ):
            ob = last_opposing_candle(bars, i, "short")
            if ob:
                ob_low, ob_high = ob
                stop = max(b.high, ob_high) + STOP_BUF_ATR * a[i]
                pending = Setup("short", ob_low, ob_high, stop, i)

        # Enter on retest of OB
        if pending is not None and i > pending.created_i:
            if pending.side == "long":
                touched = b.low <= pending.ob_high and b.high >= pending.ob_low
                if touched and b.close >= pending.ob_low:
                    entry = b.close
                    risk = entry - pending.stop
                    if risk <= 0:
                        pending = None
                        continue
                    target = entry + TARGET_R * risk
                    position = {
                        "side": "long",
                        "entry": entry,
                        "stop": pending.stop,
                        "target": target,
                        "day": d,
                    }
                    pending = None
            else:
                touched = b.high >= pending.ob_low and b.low <= pending.ob_high
                if touched and b.close <= pending.ob_high:
                    entry = b.close
                    risk = pending.stop - entry
                    if risk <= 0:
                        pending = None
                        continue
                    target = entry - TARGET_R * risk
                    position = {
                        "side": "short",
                        "entry": entry,
                        "stop": pending.stop,
                        "target": target,
                        "day": d,
                    }
                    pending = None

    wins = [t for t in trades if t > 0]
    risk_dollars = ACCOUNT_EQUITY * (RISK_PCT / 100.0)
    total_r = sum(trades) if trades else 0.0
    return {
        "n_trades": len(trades),
        "total_r": total_r,
        "total_pnl_usd": total_r * risk_dollars,
        "risk_dollars": risk_dollars,
        "win_rate": len(wins) / len(trades) if trades else 0.0,
        "expectancy": sum(trades) / len(trades) if trades else 0.0,
        "trades": trades,
        "params": {
            "SWING_L": SWING_L,
            "DISP_ATR": DISP_ATR,
            "TARGET_R": TARGET_R,
            "MAX_DAILY_LOSS_R": MAX_DAILY_LOSS_R,
            "ACCOUNT_EQUITY": ACCOUNT_EQUITY,
            "RISK_PCT": RISK_PCT,
        },
        "skipped_chase": skipped_chase,
    }


def main() -> None:
    bars = load_ohlc(OHLC)
    m = run(bars)
    lines = [
        "=== Q2 OB/MS rules v0 backtest ===",
        "Strategy: liquidity sweep -> displacement -> order-block retest -> 2R target",
        "See RULES.md (confirm parameters with James).",
        f"Bars:       {len(bars)}",
        f"Params:     {m['params']}",
        f"Account:    ${m['params']['ACCOUNT_EQUITY']:,.0f}",
        f"Risk/trade: {m['params']['RISK_PCT']}% (${m['risk_dollars']:,.0f})",
        f"Trades:     {m['n_trades']}",
        f"Win rate:   {m['win_rate']:.1%}",
        f"Expectancy: {m['expectancy']:+.2f} R",
        f"Total R:    {m['total_r']:+.2f}",
        f"Total P&L:  ${m['total_pnl_usd']:+,.2f}",
        "",
        "Limitations:",
        "- Proxy OB/MS on OHLC only (no footprint / true institutional volume).",
        "- Sample CSV may produce few/no trades; use MT5 fetch for real bars.",
        "- No commissions/slippage; stop+target same bar -> stop wins (conservative).",
        "- Markov filters not included in v0.",
        "",
        "Run: python run_backtest.py",
        "MT5: python fetch_mt5_sample.py then re-run.",
    ]
    text = "\n".join(lines)
    print(text)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
