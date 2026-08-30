"""
sites.py — the portfolio ThermalOps monitors.

FortyGuard's hackathon API coverage is scoped to the US, so these are real
US coordinates so live calls actually resolve. Swap/add entries freely —
each just needs a unique id, a vertical, and a lat/lon.
"""

SITES = [
    # ---- Workforce Safety ----
    {"id": "wf-phx-01", "vertical": "workforce", "name": "Construction Site — Phoenix, AZ",
     "lat": 33.4484, "lon": -112.0740},
    {"id": "wf-hou-01", "vertical": "workforce", "name": "Warehouse Loading Yard — Houston, TX",
     "lat": 29.7604, "lon": -95.3698},

    # ---- Logistics & Cold Chain ----
    {"id": "lg-mia-01", "vertical": "logistics", "name": "Last-Mile Hub — Miami, FL",
     "lat": 25.7617, "lon": -80.1918},
    {"id": "lg-dal-01", "vertical": "logistics", "name": "Reefer Corridor — Dallas, TX",
     "lat": 32.7767, "lon": -96.7970},

    # ---- Data Centers & Facilities ----
    {"id": "dc-ash-01", "vertical": "data_center", "name": "DC-02 Cooling Zone — Ashburn, VA",
     "lat": 39.0438, "lon": -77.4874},
    {"id": "dc-chd-01", "vertical": "data_center", "name": "West Campus — Chandler, AZ",
     "lat": 33.3062, "lon": -111.8413},
]

VERTICAL_LABELS = {
    "workforce": "Workforce Safety",
    "logistics": "Logistics & Cold Chain",
    "data_center": "Data Centers & Facilities",
}
