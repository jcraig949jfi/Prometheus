#!/usr/bin/env python3
"""
Download genus-2 curve data from the LMFDB API.

Pages through results using _offset, respects rate limits with 1-second delays,
and saves consolidated data to cartography/genus2/data/genus2_curves.json.

Target: up to 5000 curves. Minimum viable: 1000.

Usage:
    python download_genus2.py
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://www.lmfdb.org/api/g2c_curves/"
FIELDS = "label,cond,abs_disc,num_rat_pts,aut_grp_label,geom_aut_grp_label,analytic_rank,st_group,mw_rank,torsion_order"
PAGE_SIZE = 500          # LMFDB max per request
MAX_CURVES = 5000        # hard cap
DELAY_SECONDS = 1.0      # polite delay between requests
MAX_RETRIES = 5          # retries on 429 / transient errors
INITIAL_BACKOFF = 5.0    # seconds, doubles each retry

# Paths — relative to repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
OUTPUT_DIR = os.path.join(REPO_ROOT, "cartography", "genus2", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "genus2_curves.json")


def fetch_page(offset: int) -> dict:
    """Fetch one page of genus-2 curves from LMFDB."""
    url = (
        f"{BASE_URL}?_format=json"
        f"&_fields={FIELDS}"
        f"&_limit={PAGE_SIZE}"
        f"&_offset={offset}"
    )
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Prometheus-Cartography/1.0 (research; polite)")

    backoff = INITIAL_BACKOFF
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = backoff * (2 ** attempt)
                print(f"  Rate-limited (429). Backing off {wait:.0f}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
            elif e.code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"  Server error ({e.code}). Retrying in {wait:.0f}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
            else:
                raise
        except (urllib.error.URLError, OSError) as e:
            wait = backoff * (2 ** attempt)
            print(f"  Network error: {e}. Retrying in {wait:.0f}s (attempt {attempt+1}/{MAX_RETRIES})")
            time.sleep(wait)
            continue

    raise RuntimeError(f"Failed to fetch offset={offset} after {MAX_RETRIES} retries")


def normalize_record(raw: dict) -> dict:
    """Normalize an LMFDB record into our canonical schema."""
    return {
        "label": raw.get("label"),
        "conductor": raw.get("cond"),
        "discriminant": raw.get("disc"),
        "analytic_rank": raw.get("analytic_rank"),
        "num_rational_points": raw.get("num_rat_pts"),
        "automorphism_group": raw.get("aut_grp_label"),
        "geometric_automorphism_group": raw.get("geom_aut_grp_label"),
        "sato_tate_group": raw.get("st_group"),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_curves = []
    offset = 0

    print(f"Downloading genus-2 curves from LMFDB (max {MAX_CURVES})...")
    print(f"Output: {OUTPUT_FILE}")
    print()

    while offset < MAX_CURVES:
        print(f"Fetching offset={offset} (have {len(all_curves)} curves so far)...")

        data = fetch_page(offset)

        # LMFDB returns {"data": [...], ...} or similar
        # The API returns records under a key — detect it
        records = None
        if isinstance(data, dict):
            # Try common keys
            for key in ("data", "results", "records"):
                if key in data and isinstance(data[key], list):
                    records = data[key]
                    break
            # If none found, check if the dict itself looks like a list wrapper
            if records is None:
                # Some LMFDB endpoints return {next:..., previous:..., data:...}
                # Fall back: look for any list value
                for k, v in data.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        records = v
                        break
        elif isinstance(data, list):
            records = data

        if records is None or len(records) == 0:
            print(f"  No more records at offset={offset}. Done.")
            break

        for rec in records:
            all_curves.append(normalize_record(rec))

        print(f"  Got {len(records)} records (total: {len(all_curves)})")

        if len(records) < PAGE_SIZE:
            print("  Received fewer than page size — reached end of dataset.")
            break

        offset += PAGE_SIZE

        if len(all_curves) >= MAX_CURVES:
            print(f"  Reached max cap of {MAX_CURVES}.")
            break

        # Polite delay
        time.sleep(DELAY_SECONDS)

    # Save
    output = {
        "source": "LMFDB",
        "api_endpoint": BASE_URL,
        "fields": FIELDS.split(","),
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_curves": len(all_curves),
        "curves": all_curves,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Saved {len(all_curves)} genus-2 curves to {OUTPUT_FILE}")

    # Quick stats
    ranks = {}
    st_groups = {}
    for c in all_curves:
        r = c.get("analytic_rank")
        ranks[r] = ranks.get(r, 0) + 1
        sg = c.get("sato_tate_group")
        st_groups[sg] = st_groups.get(sg, 0) + 1

    print(f"\nAnalytic rank distribution:")
    for r in sorted(ranks.keys(), key=lambda x: (x is None, x)):
        print(f"  rank {r}: {ranks[r]}")

    print(f"\nSato-Tate groups ({len(st_groups)} distinct):")
    for sg, count in sorted(st_groups.items(), key=lambda x: -x[1])[:10]:
        print(f"  {sg}: {count}")


if __name__ == "__main__":
    main()
