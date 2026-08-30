"""
app.py — ThermalOps backend.

Run:
    pip install -r requirements.txt
    export FORTYGUARD_API_KEY="your-hackathon-key"   # optional — omit for mock mode
    python app.py

Then open http://localhost:5000
"""

import os
import time
import threading
import collections
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()  # must run before fortyguard_client is imported, since it reads env vars at import time

from flask import Flask, jsonify, send_from_directory

import fortyguard_client as fg
import risk_engine
from sites import SITES, VERTICAL_LABELS

app = Flask(__name__, static_folder="static", static_url_path="")

# In-memory state — fine for a hackathon demo; swap for Postgres/Supabase
# before any real customer data touches this.
_portfolio_lock = threading.Lock()
_portfolio_cache = {}          # site_id -> latest reading + score
_alerts = collections.deque(maxlen=50)   # most-recent-first

REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "60"))


def _refresh_site(site: dict):
    try:
        reading = fg.fetch_env_params(site["lat"], site["lon"])
    except fg.FortyGuardError as exc:
        reading = {"heat_index_c": None, "aqi": None, "solar_irradiance": None,
                   "source": "error", "error": str(exc)}

    score = risk_engine.score_site(site["vertical"], reading.get("heat_index_c"))
    now = datetime.now(timezone.utc).isoformat()

    record = {
        **site,
        "heat_index_c": reading.get("heat_index_c"),
        "aqi": reading.get("aqi"),
        "solar_irradiance": reading.get("solar_irradiance"),
        "source": reading.get("source"),
        "error": reading.get("error"),
        "band": score["band"],
        "action": score["action"],
        "updated_at": now,
    }

    with _portfolio_lock:
        previous = _portfolio_cache.get(site["id"])
        _portfolio_cache[site["id"]] = record
        # Log an alert whenever a site newly enters WARNING/CRITICAL,
        # or is freshly read for the first time in a bad band.
        if score["band"] in ("WARNING", "CRITICAL"):
            prev_band = previous["band"] if previous else None
            if prev_band != score["band"]:
                _alerts.appendleft({
                    "site_id": site["id"],
                    "site_name": site["name"],
                    "vertical": site["vertical"],
                    "band": score["band"],
                    "message": score["action"],
                    "heat_index_c": reading.get("heat_index_c"),
                    "timestamp": now,
                })

    return record


def _refresh_loop():
    while True:
        for site in SITES:
            _refresh_site(site)
            time.sleep(1.5)  # be gentle on FortyGuard's API — small gap between sites
        time.sleep(REFRESH_INTERVAL_SECONDS)


def _ensure_initial_data():
    """Populate the cache synchronously on first request/startup so the
    dashboard never shows an empty screen while the background loop warms up."""
    if not _portfolio_cache:
        for site in SITES:
            _refresh_site(site)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "mode": "live" if fg.is_live_mode() else "mock",
        "sites_tracked": len(SITES),
    })


@app.route("/api/portfolio")
def api_portfolio():
    _ensure_initial_data()
    with _portfolio_lock:
        records = list(_portfolio_cache.values())

    by_vertical = {}
    for r in records:
        by_vertical.setdefault(r["vertical"], []).append(r)

    summary = {
        "sites_critical": sum(1 for r in records if r["band"] == "CRITICAL"),
        "sites_warning": sum(1 for r in records if r["band"] == "WARNING"),
        "avg_heat_index": round(
            sum(r["heat_index_c"] for r in records if r["heat_index_c"] is not None)
            / max(1, sum(1 for r in records if r["heat_index_c"] is not None)), 1
        ) if records else None,
        "mode": "live" if fg.is_live_mode() else "mock",
    }

    return jsonify({
        "summary": summary,
        "sites": records,
        "by_vertical": {
            v: {"label": VERTICAL_LABELS.get(v, v), "sites": items}
            for v, items in by_vertical.items()
        },
    })


@app.route("/api/alerts")
def api_alerts():
    _ensure_initial_data()
    with _portfolio_lock:
        return jsonify({"alerts": list(_alerts)})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Manual refresh trigger — handy for a live demo instead of waiting
    for the background loop's next tick."""
    for site in SITES:
        _refresh_site(site)
    return jsonify({"refreshed": len(SITES), "at": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    _ensure_initial_data()
    t = threading.Thread(target=_refresh_loop, daemon=True)
    t.start()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
