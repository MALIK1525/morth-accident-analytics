"""Phase 13.4 Government Data Watch — discovery only, never integration.

Sources: OpenCity CKAN (open), data.gov.in (keyed; honest awaiting-key
without DATA_GOV_IN_API_KEY), MoRTH/NCRB publication pages (content-hash
change detection), PIB (manual-check card; no verified machine feed).

Nothing here writes to research/benchmark paths. Review downloads go ONLY
to research_watch/review_queue/. Scan history lives in
research_watch/scan_history.json (runtime state, git-ignored).
"""
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

TIMEOUT_S = 15
SCAN_TTL_S = 6 * 3600
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024

WATCH_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "research_watch")
HISTORY_PATH = os.path.join(WATCH_DIR, "scan_history.json")
REVIEW_DIR = os.path.join(WATCH_DIR, "review_queue")

CKAN_BASE = "https://data.opencity.in/api/3/action"
CKAN_QUERIES = ["road accident", "traffic accidents", "MoRTH", "NCRB ADSI",
                "road safety", "vehicle registration"]

PAGE_WATCHERS = [
    {"id": "morth-reports", "source": "MoRTH",
     "url": "https://morth.nic.in/en/road-accident-in-india",
     "label": "MoRTH Road Accidents in India publications page"},
    {"id": "ncrb-adsi", "source": "NCRB",
     "url": "https://ncrb.gov.in/en/accidental-deaths-suicides-india-adsi",
     "label": "NCRB ADSI publications page"},
]

KEYWORDS_RELEVANT = ["accident", "fatalit", "injur", "morth", "ncrb", "adsi",
                     "road safety", "traffic", "vehicle", "highway",
                     "transport", "road death", "crash"]
KEYWORDS_EXPOSURE = ["vehicle stock", "registration", "registered vehicle",
                     "vahan", "vehicle flow", "permit", "transaction"]
KEYWORDS_FLOW = ["flow", "transaction", "permit", "monthly registration",
                 "vahan"]


def _get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "MoRTH-Data-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        body = resp.read()
        if raw:
            return body
        return json.loads(body.decode("utf-8", errors="replace"))


def detect_vintage(text):
    t = (text or "").lower()
    if "morth" in t or "road transport" in t:
        return "MoRTH"
    if "ncrb" in t or "adsi" in t or "crime records" in t:
        return "NCRB"
    if "imd" in t or "meteorolog" in t:
        return "IMD"
    return "OTHER"


def detect_geography(text):
    t = (text or "").lower()
    out = []
    if "district" in t:
        out.append("District")
    if "city" in t or "million-plus" in t:
        out.append("City")
    if "state" in t or "ut" in t or "state/ut" in t:
        out.append("State/UT")
    if "coordinat" in t or "latitude" in t or "gis" in t:
        out.append("Coordinates")
    if not out and ("india" in t or "national" in t or "all-india" in t):
        out.append("India")
    return out or ["Unspecified"]


def detect_measures(text):
    t = (text or "").lower()
    found = []
    for key in ["accident", "fatalit", "injur", "vehicle", "population",
                "rainfall", "temperature", "traffic", "road condition",
                "registration", "road length"]:
        if key in t:
            found.append(key)
    return found


def classify_relevance(title, description):
    t = f"{title} {description}".lower()
    hits = [k for k in KEYWORDS_RELEVANT if k in t]
    exposure = any(k in t for k in KEYWORDS_EXPOSURE)
    flow_like = any(k in t for k in KEYWORDS_FLOW)
    return {
        "relevant": bool(hits),
        "relevance": "RELEVANT" if hits else "NOT_RELEVANT",
        "exposure_candidate": exposure,
        "stock_or_flow": ("FLOW — must NOT substitute for stock"
                          if flow_like and exposure else
                          ("STOCK?" if exposure else "n/a")),
    }


def compatibility_audit(title, description):
    text = f"{title} {description}"
    vintage = detect_vintage(text)
    return {
        "geography": detect_geography(text),
        "time": (["Month"] if "month" in text.lower() else []) +
                (["Year", "Annual"] if re.search(r"year|annual|20\d\d", text.lower()) else []) or ["Unspecified"],
        "measures": detect_measures(text),
        "vintage": vintage,
        "vintage_warning": ("NCRB VINTAGE — never merge with MoRTH benchmark"
                            if vintage == "NCRB" else None),
        "definition_note": "Metadata-level guess only; verify source definitions before any use.",
    }


def fetch_opencity():
    """Query OpenCity CKAN package_search across keyword queries."""
    seen, items, failed = {}, [], []
    for q in CKAN_QUERIES:
        try:
            url = (f"{CKAN_BASE}/package_search?"
                   + urllib.parse.urlencode({"q": q, "rows": 20}))
            payload = _get(url)
            results = ((payload.get("result") or {}).get("results")) or []
            for ds in results:
                ds_id = ds.get("id")
                if not ds_id or ds_id in seen:
                    continue
                title = ds.get("title") or "Untitled dataset"
                notes = ds.get("notes") or ""
                org = (ds.get("organization") or {}).get("title") or "Unknown"
                rel = classify_relevance(title, notes)
                seen[ds_id] = True
                items.append({
                    "id": f"opencity:{ds_id}",
                    "title": title,
                    "publisher": org,
                    "description": (notes[:500]),
                    "url": f"https://data.opencity.in/dataset/{ds.get('name', ds_id)}",
                    "created": ds.get("metadata_created"),
                    "modified": ds.get("metadata_modified"),
                    "source": "OpenCity",
                    "source_badge": "OPEN DATA — OpenCity",
                    "relevance": rel["relevance"],
                    "exposure_candidate": rel["exposure_candidate"],
                    "stock_or_flow": rel["stock_or_flow"],
                    "compatibility": compatibility_audit(title, notes),
                })
        except Exception:
            failed.append(q)
    return items, failed


def fetch_datagovin():
    """data.gov.in watcher. Honest awaiting-key without DATA_GOV_IN_API_KEY."""
    if not os.environ.get("DATA_GOV_IN_API_KEY"):
        return {"status": "awaiting_key",
                "message": "data.gov.in: Awaiting API key (set DATA_GOV_IN_API_KEY)."}
    try:
        url = ("https://api.data.gov.in/catalogs?"
               + urllib.parse.urlencode(
                   {"ministry": "Ministry of Road Transport and Highways",
                    "api-key": os.environ["DATA_GOV_IN_API_KEY"],
                    "format": "json", "limit": 20}))
        payload = _get(url)
        return {"status": "success", "raw": payload}
    except Exception:
        return {"status": "error", "message": "data.gov.in temporarily unavailable"}


def fetch_page_snapshot(watcher):
    body = _get(watcher["url"], raw=True)
    digest = hashlib.sha256(body).hexdigest()
    return {"id": watcher["id"], "source": watcher["source"],
            "url": watcher["url"], "label": watcher["label"],
            "hash": digest, "size": len(body)}


def _load_history():
    try:
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_history(hist):
    os.makedirs(WATCH_DIR, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=1)


_scan_cache = {"at": 0.0, "data": None}
SCAN_CACHE_TTL = 600


def scan(force=False):
    now = time.time()
    if not force and _scan_cache["data"] is not None and (now - _scan_cache["at"]) < SCAN_CACHE_TTL:
        out = dict(_scan_cache["data"])
        out["cached"] = True
        return out
    detected_at = time.strftime("%Y-%m-%d %H:%M IST", time.localtime(now))
    hist = _load_history()
    items, errors = [], []

    oc_items, oc_failed = fetch_opencity()
    if oc_failed:
        errors.append({"source": "OpenCity",
                       "message": f"{len(oc_failed)} quer(ies) failed; partial results"})
    for it in oc_items:
        key = it["id"]
        prev = hist.get(key)
        mod = it.get("modified")
        if prev is None:
            it["status"] = "NEW"
        elif mod and prev.get("modified") and mod != prev["modified"]:
            it["status"] = "UPDATED"
        else:
            it["status"] = "KNOWN"
        it["detected_at"] = prev.get("detected_at", detected_at) if prev else detected_at
        it["first_seen"] = prev.get("first_seen", detected_at) if prev else detected_at
        hist[key] = {"title": it["title"], "modified": mod,
                     "first_seen": it["first_seen"], "last_seen": detected_at}
        items.append(it)

    pages = []
    for w in PAGE_WATCHERS:
        try:
            snap = fetch_page_snapshot(w)
            prev = hist.get("page:" + w["id"])
            snap["status"] = ("KNOWN" if prev and prev.get("hash") == snap["hash"]
                              else ("UPDATED" if prev else "NEW"))
            snap["detected_at"] = detected_at
            snap["title"] = w["label"]
            snap["source_badge"] = f"OFFICIAL — {w['source']}"
            snap["relevance"] = "RELEVANT"
            snap["compatibility"] = {"vintage": w["source"], "note": "Page-change detection only; content review required."}
            hist["page:" + w["id"]] = {"hash": snap["hash"], "last_seen": detected_at}
            pages.append(snap)
        except Exception:
            pages.append({"id": w["id"], "source": w["source"], "url": w["url"],
                          "title": w["label"], "status": "SOURCE_UNAVAILABLE",
                          "source_badge": f"OFFICIAL — {w['source']}",
                          "detected_at": detected_at,
                          "relevance": "MANUAL_REVIEW"})

    dg = fetch_datagovin()

    try:
        _save_history(hist)
    except OSError:
        errors.append({"source": "history", "message": "Could not persist scan history"})

    data = {"status": "success", "scanned_at": detected_at,
            "datasets": items, "pages": pages,
            "datagovin": dg,
            "pib": {"status": "manual_check",
                    "message": "PIB has no verified machine feed; check PIB MoRTH releases manually.",
                    "url": "https://pib.gov.in/"},
            "counts": {"new": sum(1 for i in items + pages if i.get("status") == "NEW"),
                       "updated": sum(1 for i in items + pages if i.get("status") == "UPDATED"),
                       "total": len(items) + len(pages)},
            "errors": errors}
    _scan_cache.update(at=now, data=data)
    out = dict(data)
    out["cached"] = False
    return out


def queue_download(url):
    """Fetch a candidate file into the review queue ONLY. Returns saved path."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http/https URLs allowed.")
    req = urllib.request.Request(url, headers={"User-Agent": "MoRTH-Data-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read(MAX_DOWNLOAD_BYTES + 1)
    if len(body) > MAX_DOWNLOAD_BYTES:
        raise ValueError("File exceeds 32 MB review limit.")
    os.makedirs(REVIEW_DIR, exist_ok=True)
    name = os.path.basename(parsed.path) or "download"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:80] or "download"
    dest = os.path.join(REVIEW_DIR, f"{int(time.time())}_{name}")
    if not os.path.abspath(dest).startswith(os.path.abspath(REVIEW_DIR)):
        raise ValueError("Unsafe path rejected.")
    with open(dest, "wb") as f:
        f.write(body)
    return dest


def clear_cache():
    _scan_cache.update(at=0.0, data=None)
