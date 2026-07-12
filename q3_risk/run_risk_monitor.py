"""
Q3 — Risk monitoring mini-dashboard from journal CSV.
Flags: daily loss limit, streak risk, drawdown breach.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOURNAL = ROOT.parent / "q1_journal" / "sample_trades.csv"
OUT = ROOT / "risk_report.html"

MAX_DAILY_LOSS_R = -2.0
MAX_DD_R = -4.0
MAX_LOSING_STREAK = 3


def load(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def analyze(trades: list[dict]) -> dict:
    by_day: dict[str, float] = defaultdict(float)
    for t in trades:
        by_day[t["date"]] += float(t["r_multiple"])

    alerts = []
    for d, net in sorted(by_day.items()):
        if net <= MAX_DAILY_LOSS_R:
            alerts.append(
                {
                    "level": "HIGH",
                    "code": "DAILY_LOSS_LIMIT",
                    "detail": f"{d}: {net:+.2f} R <= {MAX_DAILY_LOSS_R} R",
                }
            )

    rs = [float(t["r_multiple"]) for t in trades]
    streak = 0
    max_streak = 0
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rs:
        streak = streak + 1 if r <= 0 else 0
        max_streak = max(max_streak, streak)
        cum += r
        peak = max(peak, cum)
        max_dd = min(max_dd, cum - peak)

    if max_streak >= MAX_LOSING_STREAK:
        alerts.append(
            {
                "level": "MED",
                "code": "LOSING_STREAK",
                "detail": f"Max losing streak {max_streak} (limit {MAX_LOSING_STREAK})",
            }
        )
    if max_dd <= MAX_DD_R:
        alerts.append(
            {
                "level": "HIGH",
                "code": "DRAWDOWN_LIMIT",
                "detail": f"Max DD {max_dd:.2f} R <= {MAX_DD_R} R",
            }
        )

    if not alerts:
        alerts.append(
            {
                "level": "OK",
                "code": "WITHIN_LIMITS",
                "detail": "No limit breaches on this sample window",
            }
        )

    return {
        "by_day": dict(sorted(by_day.items())),
        "max_dd": max_dd,
        "max_streak": max_streak,
        "ending_r": cum,
        "alerts": alerts,
    }


def write_html(m: dict, path: Path) -> None:
    alert_rows = "".join(
        f"<tr><td>{a['level']}</td><td>{a['code']}</td><td>{a['detail']}</td></tr>"
        for a in m["alerts"]
    )
    day_rows = "".join(
        f"<tr><td>{d}</td><td>{v:+.2f}</td></tr>" for d, v in m["by_day"].items()
    )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>Risk monitor — James Doyle</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;background:#0b0f14;color:#e8eef5}}
.card{{background:#151b24;padding:1rem 1.2rem;border-radius:10px;margin:1rem 0}}
table{{width:100%;border-collapse:collapse}}
td,th{{padding:0.45rem;border-bottom:1px solid #2a3340;text-align:left}}
</style></head><body>
<h1>Risk monitoring</h1>
<p>Limits: daily loss {MAX_DAILY_LOSS_R} R · max DD {MAX_DD_R} R · losing streak {MAX_LOSING_STREAK}</p>
<div class="card">
  <strong>Ending R:</strong> {m['ending_r']:+.2f} ·
  <strong>Max DD:</strong> {m['max_dd']:.2f} R ·
  <strong>Max losing streak:</strong> {m['max_streak']}
</div>
<h2>Alerts</h2>
<table><thead><tr><th>Level</th><th>Code</th><th>Detail</th></tr></thead>
<tbody>{alert_rows}</tbody></table>
<h2>Daily net R</h2>
<table><thead><tr><th>Date</th><th>Net R</th></tr></thead>
<tbody>{day_rows}</tbody></table>
</body></html>"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    trades = load(JOURNAL)
    m = analyze(trades)
    print("=== Q3 Risk monitor ===")
    for a in m["alerts"]:
        print(f"[{a['level']}] {a['code']}: {a['detail']}")
    write_html(m, OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
