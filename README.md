# ThermalOps

**Enterprise Temperature Intelligence — for the people, freight, and facilities that heat puts at risk.**
Built on the [FortyGuard Temperature API](https://www.fortyguard.com) for **FortyGuard Hackathon '26 — Building the World's Temperature AI**.

Track: **AI Agents** × **Government & Environmental Applications**

---

## What it is

ThermalOps is a commercial operations layer that sits on top of FortyGuard's hyperlocal (2-meter-resolution) temperature data and turns it into decisions across three verticals:

| Vertical | Who it's for | What it does |
|---|---|---|
| **Workforce Safety** | Construction, delivery, warehouse, field-service crews | Site-level WBGT-style heat risk scoring, auto-triggered work/rest cycles, supervisor alerts over WhatsApp/SMS/Slack, compliance logging |
| **Logistics & Cold Chain** | Fleet operators, last-mile delivery, reefer freight | Route-level thermal exposure scoring before dispatch, cold-chain breach prediction, driver heat-safety alerts |
| **Data Centers & Facilities** | Facilities/uptime teams | External heat-load forecasting layered onto internal thermal telemetry, early cooling-stress warnings |

ThermalOps doesn't compete with FortyGuard's API — it's the thin, auditable layer enterprises need on top of it: **score → alert → prove.**

## What's in this repo

```
thermalops/
├── backend/                  # ← REAL, RUNNABLE app — start here
│   ├── app.py                 # Flask server: live dashboard + REST API
│   ├── fortyguard_client.py   # Real FortyGuard HTTP client (submit → poll → normalize)
│   ├── risk_engine.py         # Per-vertical WBGT-style risk scoring
│   ├── sites.py               # Portfolio registry (real US coordinates, 3 verticals)
│   ├── static/index.html      # Live dashboard — fetches real data, no hardcoded numbers
│   ├── requirements.txt
│   └── .env.example
├── product/
│   └── index.html            # Marketing/pitch product page (static, for the video walkthrough)
├── docs/
│   ├── ThermalOps_MarketAnalysis_Deck.pptx   # Market analysis + product slides (for the demo video)
│   ├── VIDEO_SCRIPT.md       # Scene-by-scene script for the 3-min submission video
│   └── LINKEDIN_POST.md      # Draft LinkedIn post copy for publishing the video
├── scripts/
│   ├── build_deck.js         # Regenerates the .pptx deck (pptxgenjs)
│   └── assets/               # Gradient/glow image assets used by the deck
└── README.md
```

## Running the real app

This is a working Flask backend with a real FortyGuard API client — not a mockup.

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # then paste your FortyGuard hackathon key into .env
python app.py
```

Open **http://localhost:5000**. It works two ways:

- **No `FORTYGUARD_API_KEY` set** → runs in **mock mode**: a labeled, diurnal-curve heat simulation so the app is fully demo-able with zero setup. The dashboard shows a clear "MOCK MODE" pill so this is never mistaken for live data.
- **`FORTYGUARD_API_KEY` set** → runs in **live mode**: every site polls FortyGuard's real `POST /v1/env_params` → `activity_id` → poll `/v1/status/{activity_id}` until `Completed`, and the dashboard shows a "LIVE" pill.

**Verified end-to-end against the real FortyGuard hackathon API** (not just mock mode): submit → poll → parse confirmed working with real credentials, real activity IDs, and real response payloads.

**What's real vs. what's a documented fallback, honestly:**
- **Real, live, FortyGuard-computed:** solar irradiance (`clear_sky.ghi/dni/dhi`) — genuinely varies by exact location and time of day, computed by FortyGuard's model, not us.
- **Real API round-trip, echoed value:** the "heat index" shown is currently FortyGuard's `temperature` field for that location/time. FortyGuard's response schema exposes richer derived metrics (`heat_index_celsius`, `relative_humidity_percent`, `wet_bulb_temperature_celsius`, etc.) as part of its `parameters` object, and the client (`fortyguard_client.py`) already requests them by name — but they came back as empty arrays in every real trial-key call made during this build. That may need a different request shape/endpoint combination than what's publicly documented, or may require a plan tier this trial key doesn't unlock. This is flagged, not hidden.
- **Everything downstream is real, live logic:** risk banding (`risk_engine.py`), alert generation, and the dashboard all run on whatever FortyGuard actually returns — nothing is hardcoded or faked past that point.

**Note on exact FortyGuard paths:** the submit/status endpoint paths (`FORTYGUARD_SUBMIT_PATH`, `FORTYGUARD_STATUS_PATH_TEMPLATE` in `.env.example`) matched `/v1/env_params` and `/v1/status/{activity_id}` for this trial key — confirmed via FortyGuard's own support bot in the hackathon Slack.

## What used to be here (static product page)

`product/index.html` is the earlier marketing/pitch page with illustrative sample data — kept for the video walkthrough's opening/closing shots since it has the fuller commercial narrative (pricing, market sizing teaser, pillar breakdowns). **`backend/static/index.html` is the real, live-data dashboard** — that's the one to demo as "the product."



## Architecture — how it connects to FortyGuard

```
FortyGuard API  →  Monitoring Agent  →  Risk Engine  →  Alert Log  →  Dashboard
(POST /v1/         (background loop,     (WBGT-style      (in-memory,     (Flask, polls
 env_params,         polls every site      scoring per      newest-first)   /api/portfolio
 poll for            every 60s)            vertical)                        every 30s)
 activity_id)
```

- **Data source:** `backend/fortyguard_client.py` — real `requests` calls to FortyGuard's `POST /v1/env_params`, following the documented async job pattern (submit → `activity_id` → poll `GET` until `status: succeeded`).
- **Auth:** `api-key` header, read from `FORTYGUARD_API_KEY` in `.env`. Never touches the frontend.
- **Mock fallback:** if no key is set, `fortyguard_client.py` returns a clearly-labeled diurnal heat simulation (`source: "mock_fallback"`) instead of failing — so the app runs standalone.
- **Risk engine:** `backend/risk_engine.py` — converts `heat_index_c` into `NORMAL` / `WARNING` / `CRITICAL` per vertical, with different thresholds for workforce safety (most conservative) vs. logistics vs. data centers.
- **Alerting today:** in-memory alert log, surfaced via `/api/alerts` and rendered in the dashboard. **Not yet wired to WhatsApp/SMS/Slack** — that's the next build step (see Roadmap), the pricing/product narrative in `product/index.html` describes where this is headed.

## Business model

Per-site subscription, illustrative pilot pricing:

- **Starter** — $149/site/mo — single vertical, up to 5 sites
- **Enterprise** — $399/site/mo — all 3 verticals, 5–200 sites, TMS/WMS/Slack integration
- **Platform** — custom — 200+ sites, government & multi-country, private deployment

Full reasoning in `docs/ThermalOps_MarketAnalysis_Deck.pptx`.

## Demo video

3-minute walkthrough: product site → live dashboard → market analysis (slides) → close.
Script: [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md)
📺 **Video link:** _add after recording & uploading_
💼 **LinkedIn post:** _add after publishing — draft copy in [`docs/LINKEDIN_POST.md`](docs/LINKEDIN_POST.md)_

## Roadmap

1. **Now** — working prototype, portfolio dashboard, WhatsApp alert routing, 3 verticals modeled.
2. **Next 90 days** — first paid pilot per vertical, replace modeled metrics with real ones.
3. **6–12 months** — regional threshold/regulation packs, TMS/WMS integrations, FortyGuard co-sell motion.

## Team / submission

FortyGuard Hackathon '26 · Submission deadline 30 August 2026, 11:59 PM GST.
Built using FortyGuard's Temperature API trial credits.

---

*Figures in the pitch deck and product copy (e.g. "−31% modeled heat-incident rate") are modeled/illustrative for the hackathon submission, clearly labeled as such in the deck — not measured production results.*
