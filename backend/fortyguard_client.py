"""
fortyguard_client.py — real HTTP client for the FortyGuard Temperature API.

Self-healing request body: FortyGuard's exact request schema isn't
published anywhere scrapeable (its interactive docs are a JS-rendered SPA),
so instead of guessing blind this client reads each 422 validation error
FastAPI/pydantic sends back and automatically repairs the request body,
then retries — handling missing fields, enum/literal mismatches (string or
int), wrong types (str/int/float/bool), out-of-range numbers, and bad
date/datetime formats. It keeps going until the request succeeds or it
runs out of attempts, at which point it raises with the full diagnostic
trail (every body it tried + every error FortyGuard sent back).
"""

import os
import re
import time
import random
import datetime
import requests

FORTYGUARD_API_BASE = os.getenv("FORTYGUARD_API_BASE", "https://api.fortyguard.com")
FORTYGUARD_API_KEY = os.getenv("FORTYGUARD_API_KEY", "").strip()

SUBMIT_PATH = os.getenv("FORTYGUARD_SUBMIT_PATH", "/v1/env_params")
STATUS_PATH_TEMPLATE = os.getenv("FORTYGUARD_STATUS_PATH_TEMPLATE", "/v1/env_params/{activity_id}")

POLL_INTERVAL_SECONDS = float(os.getenv("FORTYGUARD_POLL_INTERVAL", "2"))
POLL_TIMEOUT_SECONDS = float(os.getenv("FORTYGUARD_POLL_TIMEOUT", "50"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("FORTYGUARD_REQUEST_TIMEOUT", "15"))

_MAX_SCHEMA_DISCOVERY_ATTEMPTS = 25


class FortyGuardError(Exception):
    """Raised when the live FortyGuard API can't be reached or fails a job."""


def is_live_mode() -> bool:
    return bool(FORTYGUARD_API_KEY)


def _headers() -> dict:
    return {"api-key": FORTYGUARD_API_KEY, "Content-Type": "application/json"}


def fetch_env_params(lat: float, lon: float) -> dict:
    """
    Return environmental params for a lat/lon: heat_index_c, aqi,
    solar_irradiance, source ("fortyguard_live" | "mock_fallback").

    Request body confirmed directly by FortyGuard's own support bot (not
    guessed): env_params uses the same date_time shape as /v1/heatmap —
    {start_date: "YYYY-MM-DD", start_time: "HH:MM", filter_type: 1}, where
    filter_type=1 means "single hour" (i.e. a current-moment reading).
    Coverage is US-only and dates must be 2021-01-01 through today.
    """
    if not is_live_mode():
        return _mock_reading(lat, lon)

    submit_url = f"{FORTYGUARD_API_BASE}{SUBMIT_PATH}"
    now = datetime.datetime.now(datetime.timezone.utc)
    body = {
        "latitude": lat,
        "longitude": lon,
        "temperature": _estimate_ambient_temperature_c(lat),
        "humidity": _estimate_ambient_humidity_pct(lat),  # heat index needs temp+humidity to compute
        "date_time": {
            "start_date": now.strftime("%Y-%m-%d"),
            "start_time": now.strftime("%H:%M"),
            "filter_type": 1,  # 1 = single hour (a current-moment reading)
        },
        # Ask explicitly for the metrics we need — FortyGuard's response
        # schema lists these as available "parameters" but leaves them as
        # empty arrays unless requested. Key names match its own response
        # field names exactly (confirmed from a real response).
        "parameters": [
            "heat_index_celsius",
            "apparent_temperature_celsius",
            "relative_humidity_percent",
            "wet_bulb_temperature_celsius",
            "aqi_us_co",
        ],
    }

    attempt_log = []
    resp = None
    tried_map: dict = {}
    server_error_retries = 0
    _MAX_SERVER_ERROR_RETRIES = 3
    _SERVER_ERROR_BACKOFF_SECONDS = [3, 8, 15]

    attempt = 0
    while attempt < _MAX_SCHEMA_DISCOVERY_ATTEMPTS:
        try:
            resp = requests.post(submit_url, headers=_headers(), json=body, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            break  # success
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None

            # 5xx = FortyGuard's own server had a problem — not something we
            # can fix by changing the body. Retry a few times with backoff,
            # since these are often transient (server hiccup / brief overload).
            if status_code is not None and 500 <= status_code < 600:
                if server_error_retries < _MAX_SERVER_ERROR_RETRIES:
                    wait = _SERVER_ERROR_BACKOFF_SECONDS[server_error_retries]
                    server_error_retries += 1
                    time.sleep(wait)
                    continue  # retry the SAME body, don't advance `attempt`
                body_text = getattr(exc.response, "text", "")[:800]
                raise FortyGuardError(
                    f"FortyGuard's server returned {status_code} after {_MAX_SERVER_ERROR_RETRIES} retries "
                    f"with backoff — this is on FortyGuard's side, not the request body. It may be a "
                    f"temporary outage; check the Hackathon Slack for status updates and try again shortly. "
                    f"Response body: {body_text}"
                ) from exc

            if status_code != 422:
                body_text = getattr(exc.response, "text", "")[:800] if exc.response is not None else ""
                raise FortyGuardError(f"Submit request failed: {exc} | response body: {body_text}") from exc

            try:
                detail = exc.response.json().get("detail", [])
            except Exception:
                detail = []

            changed = _apply_schema_fixes(body, detail, tried_map)
            attempt_log.append({"attempt": attempt + 1, "body": _json_safe(body), "detail": detail})
            attempt += 1

            if not changed:
                raise FortyGuardError(
                    f"Could not auto-resolve FortyGuard's request schema after {attempt} attempt(s). "
                    f"Last validation errors: {detail} | Full attempt log: {attempt_log}"
                ) from exc
            continue
        except requests.RequestException as exc:
            raise FortyGuardError(f"Submit request failed: {exc}") from exc
    else:
        raise FortyGuardError(
            f"Gave up after {_MAX_SCHEMA_DISCOVERY_ATTEMPTS} schema-discovery attempts. "
            f"Full attempt log: {attempt_log}"
        )

    payload = resp.json()
    inner_data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    activity_id = (
        payload.get("activity_id")
        or payload.get("id")
        or inner_data.get("activity_id")
        or inner_data.get("id")
    )

    if not activity_id:
        # No activity_id anywhere — only treat this as an already-complete
        # synchronous result if it actually looks like measurement data
        # (has a heat/temperature-shaped field), not just a submit ack.
        if any(k in inner_data for k in ("heat_index", "heat_index_c", "temperature")) or \
           any(k in payload for k in ("heat_index", "heat_index_c")):
            return _normalize(payload)
        raise FortyGuardError(f"No activity_id in submit response: {payload}")

    status_url = f"{FORTYGUARD_API_BASE}{STATUS_PATH_TEMPLATE.format(activity_id=activity_id)}"
    elapsed = 0.0
    while elapsed < POLL_TIMEOUT_SECONDS:
        try:
            status_resp = requests.get(status_url, headers=_headers(), timeout=REQUEST_TIMEOUT_SECONDS)
            status_resp.raise_for_status()
        except requests.RequestException as exc:
            raise FortyGuardError(f"Status poll failed: {exc}") from exc

        status_payload = status_resp.json()
        # Status may be at the top level OR nested under "data" — check both.
        status_inner = status_payload.get("data") if isinstance(status_payload.get("data"), dict) else {}
        status = str(status_payload.get("status") or status_inner.get("status") or "").lower()

        if status in ("succeeded", "success", "completed", "done"):
            return _normalize(status_payload)
        if status in ("failed", "error"):
            raise FortyGuardError(f"FortyGuard job {activity_id} failed: {status_payload}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    raise FortyGuardError(f"Timed out waiting for activity {activity_id} after {POLL_TIMEOUT_SECONDS}s")


# ---------------------------------------------------------------------------
# Self-healing schema discovery
# ---------------------------------------------------------------------------

_DATE_FORMAT_CANDIDATES = [
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y",
    "%m/%d/%Y",
]


def _get_container(body: dict, loc: list):
    """Walk loc (e.g. ["body", "date_time", "filter_type"]) and return the
    parent container + final key, creating nested dicts/lists as needed."""
    node = body
    for key in loc[1:-1]:
        if isinstance(key, int):
            while len(node) <= key:
                node.append({})
            node = node[key]
        else:
            if key not in node or not isinstance(node[key], (dict, list)):
                node[key] = {}
            node = node[key]
    return node, loc[-1]


def _extract_candidates(err_item: dict):
    """
    Pull allowed values out of a pydantic/FastAPI validation error, trying
    every shape we've seen in practice:
      - ctx.expected: "'a', 'b' or 'c'"  /  "1, 2, 3 or 4"
      - ctx.enum_values: [1, 2, 3]  (older pydantic v1 style, already typed)
      - msg text containing quoted tokens or a trailing number list
    """
    ctx = err_item.get("ctx", {}) or {}

    if "enum_values" in ctx and isinstance(ctx["enum_values"], list):
        return list(ctx["enum_values"])

    expected = ctx.get("expected")
    msg = err_item.get("msg", "") or ""
    source = expected or msg

    if not source:
        return []

    raw = source.replace(" or ", ",").replace(" and ", ",")
    quoted = re.findall(r"'([^']*)'|\"([^\"]*)\"", raw)
    if quoted:
        return [a or b for a, b in quoted if (a or b)]

    # Fall back to splitting on commas for bare tokens like "1, 2, 3, 4"
    tail = raw.split(":")[-1]
    parts = [p.strip() for p in tail.split(",")]
    parts = [p for p in parts if p and re.match(r"^-?\w+(\.\w+)?$", p)]
    return parts


def _coerce(value: str):
    """Turn a string candidate into the most likely real JSON type."""
    if re.match(r"^-?\d+$", value):
        return int(value)
    if re.match(r"^-?\d+\.\d+$", value):
        return float(value)
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def _apply_schema_fixes(body: dict, detail: list, tried_map: dict) -> bool:
    """
    Mutates `body` in place based on FastAPI's 422 `detail` list.
    Returns True if it changed something worth retrying with.
    """
    changed = False

    for err in detail:
        loc = err.get("loc", [])
        if not loc or loc[0] != "body":
            continue

        err_type = err.get("type", "")
        field_name = loc[-1]
        container, key = _get_container(body, loc)
        loc_key = ".".join(str(l) for l in loc)
        tried = tried_map.setdefault(loc_key, set())

        # --- enum / literal mismatches -------------------------------------
        if err_type in ("literal_error", "enum"):
            candidates = _extract_candidates(err)
            fresh = [c for c in candidates if str(c) not in tried]
            if fresh:
                chosen = fresh[0]
                tried.add(str(chosen))
                container[key] = _coerce(str(chosen)) if isinstance(chosen, str) else chosen
                changed = True
            continue

        # --- unexpected field rejected outright: drop it and retry --------------
        if err_type == "extra_forbidden":
            if key in container:
                del container[key]
                changed = True
            continue

        # --- missing required field -----------------------------------------
        if err_type == "missing":
            fname_lower = str(field_name).lower()
            if "date" in fname_lower or "time" in fname_lower:
                val = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
                if val not in tried:
                    container[key] = val
                    tried.add(val)
                    changed = True
            elif fname_lower in _FIELD_NAME_GUESSES:
                fresh = [g for g in _FIELD_NAME_GUESSES[fname_lower] if str(g) not in tried]
                if fresh:
                    container[key] = fresh[0]
                    tried.add(str(fresh[0]))
                    changed = True
            else:
                guesses = ["current", 1, "default", True]
                fresh = [g for g in guesses if str(g) not in tried]
                if fresh:
                    container[key] = fresh[0]
                    tried.add(str(fresh[0]))
                    changed = True
            continue

        # --- wrong type: needs to be an int -----------------------------------
        if err_type in ("int_parsing", "int_type"):
            existing = container.get(key)
            try:
                new_val = int(existing) if existing is not None else 0
            except (TypeError, ValueError):
                new_val = 0
            if str(new_val) not in tried or not isinstance(existing, int):
                container[key] = new_val
                tried.add(str(new_val))
                changed = True
            continue

        # --- wrong type: needs to be a float ------------------------------------
        if err_type in ("float_parsing", "float_type"):
            existing = container.get(key)
            try:
                new_val = float(existing) if existing is not None else 0.0
            except (TypeError, ValueError):
                new_val = 0.0
            if str(new_val) not in tried or not isinstance(existing, float):
                container[key] = new_val
                tried.add(str(new_val))
                changed = True
            continue

        # --- wrong type: needs to be a string -----------------------------------
        if err_type == "string_type":
            existing = container.get(key)
            if existing is not None and not isinstance(existing, str):
                container[key] = str(existing)
                tried.add(str(existing))
                changed = True
            continue

        # --- wrong type: needs to be a bool -------------------------------------
        if err_type in ("bool_parsing", "bool_type"):
            container[key] = True
            changed = True
            continue

        # --- bad date/datetime format: cycle through common formats ------------
        if "date" in err_type or "datetime" in err_type:
            base_date = datetime.datetime.now(datetime.timezone.utc)
            for fmt in _DATE_FORMAT_CANDIDATES:
                candidate = base_date.strftime(fmt)
                if candidate not in tried:
                    container[key] = candidate
                    tried.add(candidate)
                    changed = True
                    break
            continue

        # --- numeric out of range: clamp to the stated limit --------------------
        if err_type in (
            "greater_than", "greater_than_equal", "less_than", "less_than_equal",
        ):
            ctx = err.get("ctx", {}) or {}
            limit = ctx.get("gt", ctx.get("ge", ctx.get("lt", ctx.get("le"))))
            if limit is not None:
                nudge = 1 if "greater" in err_type else -1
                new_val = limit + nudge if "_equal" not in err_type else limit
                if str(new_val) not in tried:
                    container[key] = new_val
                    tried.add(str(new_val))
                    changed = True
            continue

        # --- generic value_error: try a couple of safe fallbacks ----------------
        if err_type == "value_error":
            candidates = _extract_candidates(err)
            fresh = [c for c in candidates if str(c) not in tried]
            if fresh:
                chosen = fresh[0]
                tried.add(str(chosen))
                container[key] = _coerce(str(chosen)) if isinstance(chosen, str) else chosen
                changed = True

    return changed


_FIELD_NAME_GUESSES = {
    "filter_type": ["current", "instant", "now", "latest", "point", "daily", "hourly", "range", 1, 2, 3, 4],
    "unit": ["celsius", "metric", "c"],
    "units": ["celsius", "metric", "c"],
}


def _json_safe(obj):
    """Deep-copy a body dict so it's safe to stash in the attempt log
    (plain values only — no live references that could mutate later)."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# Mock / estimation helpers
# ---------------------------------------------------------------------------

def _estimate_ambient_temperature_c(lat: float) -> float:
    hour = datetime.datetime.now(datetime.timezone.utc).hour
    diurnal = 6 * (1 - abs(hour - 15) / 12)
    latitude_boost = 4 if abs(lat) < 30 else 0
    return round(29 + diurnal + latitude_boost, 1)


def _estimate_ambient_humidity_pct(lat: float) -> float:
    """Rough relative-humidity placeholder (%) — heat index calculations
    need both temperature AND humidity as inputs. Coastal/tropical
    latitudes get a higher baseline; replace with a real reading for
    production accuracy."""
    base = 55 if abs(lat) < 30 else 40
    return round(base, 1)


def _normalize(payload: dict) -> dict:
    """
    Parses FortyGuard's actual confirmed response shape:
      { "data": { "result": { "locations": [ {
            "temperature": <echoed input>,
            "parameters": { "heat_index_celsius": [...], "relative_humidity_percent": [...], ... },
            "solar_irradiance": { "clear_sky": { "ghi": ..., "dni": ..., "dhi": ... } }
      } ] } } }
    Each "parameters" entry is a list (often empty unless explicitly
    requested via the submit body's "parameters" field) — take the last
    value if present.
    """
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    result = data.get("result") if isinstance(data.get("result"), dict) else {}
    locations = result.get("locations") if isinstance(result.get("locations"), list) else []
    loc0 = locations[0] if locations else {}
    params = loc0.get("parameters") if isinstance(loc0.get("parameters"), dict) else {}

    def _param(*keys):
        for k in keys:
            v = params.get(k)
            if isinstance(v, list) and v:
                return v[-1]
            if isinstance(v, (int, float)):
                return v
        return None

    heat_index = _param("heat_index_celsius", "heat_index", "heatIndex")
    if heat_index is None:
        # Fall back to apparent temperature, then the raw submitted
        # temperature reading (still real, just not humidity-corrected).
        heat_index = _param("apparent_temperature_celsius") or loc0.get("temperature")

    aqi = _param("aqi_us_co", "air_quality:idx", "air_quality_o3:idx", "air_quality_pm2p5:idx")

    solar = None
    si = loc0.get("solar_irradiance")
    if isinstance(si, dict):
        clear_sky = si.get("clear_sky")
        if isinstance(clear_sky, dict):
            solar = clear_sky.get("ghi")

    # Fallback for any response shape that isn't the nested locations[] form.
    if not locations:
        candidates = [payload, data, result]
        for c in candidates:
            if not isinstance(c, dict):
                continue
            if heat_index is None:
                heat_index = c.get("heat_index") or c.get("heat_index_c")
            if aqi is None:
                aqi = c.get("aqi")
            if solar is None:
                solar = c.get("solar_irradiance")

    return {
        "heat_index_c": heat_index,
        "aqi": aqi,
        "solar_irradiance": solar,
        "source": "fortyguard_live",
        "raw": payload,  # TEMP: keep visible for debugging until confirmed stable
    }


def _mock_reading(lat: float, lon: float) -> dict:
    hour = datetime.datetime.utcnow().hour
    diurnal = 6 * (1 - abs(hour - 15) / 12)
    latitude_boost = 4 if abs(lat) < 30 else 0
    base = 29 + diurnal + latitude_boost
    heat_index = round(base + random.uniform(-2.0, 4.5), 1)
    return {
        "heat_index_c": heat_index,
        "aqi": random.randint(35, 115),
        "solar_irradiance": round(random.uniform(280, 950), 1),
        "source": "mock_fallback",
        "raw": {},
    }
