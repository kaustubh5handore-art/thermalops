"""
risk_engine.py — turns a raw heat_index_c reading into a business decision.

Thresholds are illustrative WBGT-style bands per vertical (workforce safety
is the most conservative since it's a health-and-safety threshold; logistics
and data_center are tuned for operational/asset risk). Tune these against
real regulatory guidance (e.g. OSHA / regional heat-stress standards) before
using this for anything beyond a hackathon demo.
"""

THRESHOLDS = {
    "workforce": {"warning": 35.0, "critical": 41.0},
    "logistics": {"warning": 33.0, "critical": 39.0},
    "data_center": {"warning": 36.0, "critical": 42.0},
}

ACTIONS = {
    ("workforce", "CRITICAL"): "Mandatory 15-min shade break triggered; supervisor notified",
    ("workforce", "WARNING"): "Increased hydration-break frequency recommended",
    ("logistics", "CRITICAL"): "Cold-chain breach risk — reroute/reschedule suggested",
    ("logistics", "WARNING"): "Route thermal exposure rising — monitor closely",
    ("data_center", "CRITICAL"): "External heat load elevated — verify cooling headroom",
    ("data_center", "WARNING"): "Ambient heat trending up — early cooling check advised",
}


def score_site(vertical: str, heat_index_c: float) -> dict:
    t = THRESHOLDS.get(vertical, THRESHOLDS["workforce"])

    if heat_index_c is None:
        return {"band": "UNKNOWN", "action": None}

    if heat_index_c >= t["critical"]:
        band = "CRITICAL"
    elif heat_index_c >= t["warning"]:
        band = "WARNING"
    else:
        band = "NORMAL"

    return {"band": band, "action": ACTIONS.get((vertical, band))}
