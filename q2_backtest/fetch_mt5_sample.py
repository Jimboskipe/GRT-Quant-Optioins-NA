"""
Optional: pull OHLC from MetaTrader 5 into sample_ohlc.csv format.

Requires: MetaTrader 5 terminal running + logged in, and:
  pip install MetaTrader5

Usage:
  python fetch_mt5_sample.py
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "sample_ohlc.csv"


def main() -> None:
    try:
        import MetaTrader5 as mt5
    except ImportError as e:
        raise SystemExit(
            "MetaTrader5 package not installed. pip install MetaTrader5\n"
            "Or keep using the bundled sample_ohlc.csv for the demo."
        ) from e

    if not mt5.initialize():
        raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")

    symbol = "EURUSD"
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 200)
    mt5.shutdown()
    if rates is None:
        raise SystemExit("No rates returned — check symbol and terminal login.")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time", "open", "high", "low", "close", "volume"])
        for r in rates:
            w.writerow(
                [
                    datetime.utcfromtimestamp(int(r["time"])).isoformat(),
                    r["open"],
                    r["high"],
                    r["low"],
                    r["close"],
                    r["tick_volume"],
                ]
            )
    print(f"Wrote {len(rates)} bars to {OUT}")
    print("Next: python run_backtest.py")


if __name__ == "__main__":
    main()
