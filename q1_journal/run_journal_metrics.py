"""
Q1 — Trading journal metrics (presentable demo).
Reads sample_trades.csv (or your export) and prints a daily review summary.
Replace sample_trades.csv with your anonymized MT5/journal export when ready.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "sample_trades.csv"
OUT_HTML = ROOT / "journal_report.html"


def load_trades(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metrics(trades: list[dict]) -> dict:
    rs = [float(t["r_multiple"]) for t in trades]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    by_day: dict[str, float] = defaultdict(float)
    for t in trades:
        by_day[t["date"]] += float(t["r_multiple"])

    equity = []
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rs:
        cum += r
        peak = max(peak, cum)
        max_dd = min(max_dd, cum - peak)
        equity.append(cum)

    return {
        "n": len(rs),
        "expectancy_r": sum(rs) / len(rs) if rs else 0.0,
        "win_rate": len(wins) / len(rs) if rs else 0.0,
        "avg_win": sum(wins) / len(wins) if wins else 0.0,
        "avg_loss": sum(losses) / len(losses) if losses else 0.0,
        "total_r": sum(rs),
        "max_dd_r": max_dd,
        "ending_r": equity[-1] if equity else 0.0,
        "by_day": dict(sorted(by_day.items())),
        "equity": equity,
    }


def write_html(m: dict, trades: list[dict], path: Path) -> None:
    rows = "".join(
        f"<tr><td>{t['date']}</td><td>{t['symbol']}</td><td>{t['side']}</td>"
        f"<td>{t['r_multiple']}</td><td>{t['setup']}</td><td>{t['notes']}</td></tr>"
        for t in trades
    )
    day_rows = "".join(
        f"<tr><td>{d}</td><td>{v:+.2f} R</td></tr>" for d, v in m["by_day"].items()
    )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>Journal metrics — James Doyle</title>
<style>
body{{font-family:Georgia,serif;max-width:900px;margin:2rem auto;padding:0 1rem;background:#0f1419;color:#e7ecf1}}
h1,h2{{font-family:system-ui,sans-serif}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem}}
.card{{background:#1a222c;padding:1rem;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:0.9rem}}
td,th{{border-bottom:1px solid #2a3540;padding:0.4rem;text-align:left}}
.muted{{color:#9aa7b5}}
</style></head><body>
<h1>Trading journal metrics</h1>
<p class="muted">Demo sample (anonymized structure). Replace CSV with live journal export.</p>
<div class="cards">
  <div class="card"><strong>Trades</strong><div>{m['n']}</div></div>
  <div class="card"><strong>Win rate</strong><div>{m['win_rate']:.0%}</div></div>
  <div class="card"><strong>Expectancy</strong><div>{m['expectancy_r']:+.2f} R</div></div>
  <div class="card"><strong>Total</strong><div>{m['total_r']:+.2f} R</div></div>
  <div class="card"><strong>Max DD</strong><div>{m['max_dd_r']:.2f} R</div></div>
</div>
<h2>Daily net R</h2>
<table><thead><tr><th>Date</th><th>Net R</th></tr></thead><tbody>{day_rows}</tbody></table>
<h2>Trades</h2>
<table><thead><tr><th>Date</th><th>Symbol</th><th>Side</th><th>R</th><th>Setup</th><th>Notes</th></tr></thead>
<tbody>{rows}</tbody></table>
</body></html>"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    trades = load_trades(CSV_PATH)
    m = metrics(trades)
    print("=== Q1 Journal metrics ===")
    print(f"Trades:     {m['n']}")
    print(f"Win rate:   {m['win_rate']:.1%}")
    print(f"Expectancy: {m['expectancy_r']:+.2f} R")
    print(f"Total R:    {m['total_r']:+.2f}")
    print(f"Max DD:     {m['max_dd_r']:.2f} R")
    print(f"Ending:     {m['ending_r']:+.2f} R")
    write_html(m, trades, OUT_HTML)
    print(f"Wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
