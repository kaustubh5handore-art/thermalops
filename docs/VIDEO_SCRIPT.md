# ThermalOps — Demo Video Script
**Target length: 3:00 · Format: screen recording + slides, voiceover in Hindi/English mix (Hinglish) or English — your call**

This script is built against the FortyGuard judging rubric so every scene earns points:
Impact & Relevance (40%) · Technical Execution (35%) · Innovation (15%) · Communication (10%)

Recording order: **product site → live dashboard demo → slides (market) → product site close.**
Keep slides in the *middle*, not the intro — open and close on the live product, since judges remember the first and last 15 seconds most.

---

## 0:00–0:20 — Hook (screen: product site, hero section)
**Show:** `product/index.html` hero, scroll slowly into the gauge card.
**Say:**
> "This is a heat index of 46.8 degrees at a loading yard in Dubai, right now. That number isn't weather — it's a decision. Eighteen workers are on that site, and someone has to decide, in real time, whether they keep working. That's the problem ThermalOps solves, on top of FortyGuard's Temperature API."

---

## 0:20–0:55 — Problem, fast (screen: product site, scroll to "Three P&Ls" section)
**Show:** the three pillar cards — Workforce, Logistics, Data Centers.
**Say:**
> "Heat already hits three different budgets. Outdoor crews work through heat stress because supervisors have no site-specific signal. Cold-chain freight gets routed on static seasonal assumptions, so a heat spike becomes a spoilage claim after the fact. And data centers track internal thermal telemetry closely, but treat external heat load as background noise — until cooling capacity is suddenly tight. Three teams, three budgets, one missing layer: real-time, hyperlocal temperature intelligence."

---

## 0:55–1:50 — Live product walkthrough (screen: **http://localhost:5000**, the real backend dashboard — not the static product page)
**Show:** open the running Flask app, point at the "LIVE — FortyGuard API" pill, scroll through the 6 real sites, click "Refresh now" once to show a live re-poll happening on camera.
**Say:**
> "This is ThermalOps actually running — a Flask backend making real calls to FortyGuard's `env_params` endpoint right now, not a mockup. Six sites across three verticals, live. Watch this — I'll hit refresh, and you'll see it re-poll FortyGuard in real time.
>
> Every number here — this solar irradiance reading, this thermal exposure reading — is coming back from FortyGuard's model for this exact location and this exact minute. On top of that, our risk engine scores each site NORMAL, WARNING, or CRITICAL, and when a site crosses a threshold — like Miami and Houston right now — it fires an alert automatically, no manual checking required.
>
> That's the core of ThermalOps: FortyGuard gives you the hyperlocal signal, we turn it into a decision."

*(Recording note: the product/index.html marketing page — with its fuller pricing/market narrative — still works well for the hook at 0:00 and the close at 2:55, since it tells the bigger commercial story. Just make sure THIS section shows the real running app at localhost:5000, since that's the genuine live-API proof.)*

---

## 1:50–2:35 — Market analysis (screen: switch to ThermalOps_MarketAnalysis_Deck.pptx, slides 2–4)
**Show:** Problem slide → Market size (TAM/SAM/SOM) slide → Solution slide.
**Say:**
> "Here's why this is a business, not just a hackathon demo. [Problem slide] Three revenue-adjacent pain points, all traceable to the same missing layer. [Market slide] We're scoping this to heat-exposed enterprise operations — workforce safety, logistics, and facilities software buyers — and going to market first in the Gulf and South Asia, where FortyGuard already has regional coverage and hot-climate demand is highest. [Solution slide] ThermalOps doesn't compete with FortyGuard's API — it's the thin, auditable operations layer enterprises need on top of it: score, alert, prove."

---

## 2:35–2:55 — Architecture + business model (screen: deck slides 6–7, or product site #architecture and #pricing)
**Say:**
> "Technically, it's a five-step pipeline: FortyGuard's API feeds a monitoring agent that polls per site, a risk engine scores it WBGT-style, alert routing fires over WhatsApp, SMS or a TMS webhook, and everything lands in a compliance log. Commercially, it's a per-site subscription — starting at $149 a site for a single-vertical pilot, up to a custom enterprise tier for 200-plus sites."

---

## 2:55–3:00 — Close (screen: product site, CTA band)
**Say:**
> "Heat is already a business risk. ThermalOps just makes it one you can manage. Thanks — links to the live product, the GitHub repo, and the full deck are below."

---

## Production notes
- **Screen recording tool:** OBS Studio (free) or Loom both work well for this length.
- **Cut points:** re-record any segment individually — the script is broken into 5 scenes on purpose, so you don't need one perfect take.
- **On-screen captions:** if recording in Hinglish, consider burning in English captions for judges who are reading fast.
- **File to submit:** export as MP4, upload to YouTube (unlisted) or LinkedIn video, and link it in the GitHub README and hackathon submission form.
- **This script is a guide, not a transcript** — say it in your own words; judges can tell when a script is read verbatim.
