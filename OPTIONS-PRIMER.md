# Options primer (learner memo) — for GRT junior path

**Author:** James Mitchell Doyle  
**Honesty:** Self-study + markets practice. Not an institutional OTC options seat. Goal: speak Greeks/vol clearly and learn the book under seniors.

---

## 1. Why options exist here

GRT prices **vanilla and structured OTC options** on tokens that often have **no listed options market**. The desk needs a view of value (model + assumptions), a two-way quote, and a plan to **warehouse and hedge** risk.

---

## 2. Greeks (intuition)

| Greek | Plain meaning | Desk use |
|-------|---------------|----------|
| **Delta** | Directional sensitivity to spot | Hedge with spot/perps; inventory |
| **Gamma** | How fast delta changes | Stress when spot jumps; hedge frequency |
| **Vega** | Sensitivity to implied vol | Core P&L driver on OTC vol |
| **Theta** | Time decay | Carry of short vol / long vol |
| **Rho** | Rates (secondary in crypto often) | Note, usually smaller vs vol/spot |

Black–Scholes intuition: price is a function of spot, strike, time, rates, and **volatility**. On illiquid underlyings, **vol + skew + term structure assumptions** matter as much as the closed form.

---

## 3. Implied vol, skew, term structure

- **IV surface:** implied vol by strike and expiry  
- **Skew:** OTM puts vs calls often priced differently (crash / pump demand)  
- **Term structure:** near-dated vs longer-dated vol  
- OTC practice: refine assumptions with **backtests, paper trading, scenarios, walk-forward** (per GRT JD)

---

## 4. Structures you will see early

| Structure | Idea |
|-----------|------|
| **Covered call** | Long spot + short call — income, capped upside |
| **Cash-secured put** | Short put with cash to buy spot if assigned — entry / yield |
| **Bespoke payoffs** | Client hedges (project tokens, miners, funds) — model + hedge plan |

Junior work: help price, monitor Greeks, improve tooling — not “own the firm’s capital from day one without supervision.”

---

## 5. What I already practice (adjacent)

- Rules, journaling, fixed risk ($100k · 1.25%/trade framing in sims)  
- Python research / backtest / risk monitors / kill criteria  
- Crypto market structure curiosity (CEX, perps, liquidity) without inventing OTC tenure  

---

## 6. What I want at GRT

Direct exposure to live OTC options **under senior traders**: models, IV surfaces, automated hedging, Python dashboards for risk and P&L attribution — junior / high-ownership seat, remote NA (and APAC hours if applied).
