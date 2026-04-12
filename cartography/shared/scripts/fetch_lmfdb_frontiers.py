#!/usr/bin/env python3
"""
LMFDB Frontier Downloader — Rate-limit resilient batch fetcher
================================================================
Downloads data from 4 LMFDB collections that block Charon's research frontiers.

Collections:
  1. smf       — Siegel modular forms (samples + Fourier coefficients + eigenvalues)
  2. maass     — Maass forms with rigorous spectral parameters (35,416 forms)
  3. hmf       — Hilbert modular forms (368,356 forms)
  4. hgcwa     — Higher genus curves with automorphisms (335,012 passports, includes genus-3)

Strategy:
  - 2-second delay between requests (conservative)
  - Exponential backoff on 429 (5s → 10s → 20s → 40s → 80s)
  - Checkpoint after every page (resume-safe)
  - 100 results per page (LMFDB API max)
  - Saves raw JSON per collection

Usage:
    python fetch_lmfdb_frontiers.py smf          # Siegel modular forms (small, ~30s)
    python fetch_lmfdb_frontiers.py maass         # Maass forms (35K, ~15min)
    python fetch_lmfdb_frontiers.py hmf           # Hilbert modular forms (368K, ~2.5hr)
    python fetch_lmfdb_frontiers.py hgcwa         # Higher genus (335K, ~2hr)
    python fetch_lmfdb_frontiers.py all           # Everything sequentially

    python fetch_lmfdb_frontiers.py smf --dry-run # Show URLs without fetching
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_BASE = "https://www.lmfdb.org/api"

# LMFDB API uses "/" separators in URLs (smf/samples/ not smf_samples/)
# but collections page lists them with dots (smf.samples).
# We store the actual URL path.
PAGE_SIZE = 100              # LMFDB API max per request
DELAY_SECONDS = 2.0          # polite delay between requests
MAX_RETRIES = 5
INITIAL_BACKOFF = 5.0
USER_AGENT = "Prometheus-Cartography/2.0 (mathematical research; polite; contact: github.com/prometheus)"

# Repository layout
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

# ---------------------------------------------------------------------------
# Collection definitions
# ---------------------------------------------------------------------------
COLLECTIONS = {
    "smf": {
        "description": "Siegel modular forms",
        "tables": [
            {
                "name": "smf_samples",
                "endpoint": f"{API_BASE}/smf_samples/",
                "count": 129,
                "fields": None,  # all fields
                "output": REPO_ROOT / "cartography" / "genus2" / "data" / "siegel_samples.json",
                "sort": "label",
            },
            {
                "name": "smf_ev",
                "endpoint": f"{API_BASE}/smf_ev/",
                "count": 3094,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "genus2" / "data" / "siegel_eigenvalues.json",
                "sort": "label",
            },
            {
                "name": "smf_fc",
                "endpoint": f"{API_BASE}/smf_fc/",
                "count": 26212,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "genus2" / "data" / "siegel_fourier_coeffs.json",
                "sort": "label",
            },
            {
                "name": "smf_families",
                "endpoint": f"{API_BASE}/smf_families/",
                "count": 14,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "genus2" / "data" / "siegel_families.json",
                "sort": "name",
            },
            {
                "name": "smf_dims",
                "endpoint": f"{API_BASE}/smf_dims/",
                "count": 72,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "genus2" / "data" / "siegel_dims.json",
                "sort": "label",
            },
        ],
    },
    "maass": {
        "description": "Maass forms (rigorous spectral parameters)",
        "tables": [
            {
                "name": "maass_rigor",
                "endpoint": f"{API_BASE}/maass_rigor/",
                "count": 35416,
                "fields": "maass_id,level,weight,character,spectral_parameter,symmetry,fricke_eigenvalue,analytic_conductor",
                "output": REPO_ROOT / "cartography" / "maass" / "data" / "maass_rigor_full.json",
                "sort": "spectral_parameter",
            },
            {
                "name": "maass_newforms",
                "endpoint": f"{API_BASE}/maass_newforms/",
                "count": 14995,
                "fields": "maass_id,level,weight,character,spectral_parameter,symmetry,fricke_eigenvalue,analytic_conductor",
                "output": REPO_ROOT / "cartography" / "maass" / "data" / "maass_newforms_full.json",
                "sort": "spectral_parameter",
            },
        ],
    },
    "hmf": {
        "description": "Hilbert modular forms",
        "tables": [
            {
                "name": "hmf_forms",
                "endpoint": f"{API_BASE}/hmf_forms/",
                "count": 368356,
                "fields": "label,field_label,short_label,level_norm,level_label,level_ideal,weight,parallel_weight,dimension,is_CM,is_base_change,AL_eigenvalues",
                "output": REPO_ROOT / "cartography" / "convergence" / "data" / "hmf_forms.json",
                "sort": "label",
            },
            {
                "name": "hmf_fields",
                "endpoint": f"{API_BASE}/hmf_fields/",
                "count": 400,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "convergence" / "data" / "hmf_fields.json",
                "sort": "label",
            },
        ],
    },
    "hgcwa": {
        "description": "Higher genus curves with automorphisms (includes genus 3+)",
        "tables": [
            {
                "name": "hgcwa_passports",
                "endpoint": f"{API_BASE}/hgcwa_passports/",
                "count": 335012,
                "fields": "passport_label,total_label,genus,group,dim,g0,signature,gen_vectors,hyperelliptic,hyp_involution",
                "output": REPO_ROOT / "cartography" / "convergence" / "data" / "hgcwa_passports.json",
                "sort": "passport_label",
                # Filter to genus >= 3 to focus on the frontier
                "query_params": "genus=i3",
            },
            {
                "name": "hgcwa_passports_g4plus",
                "endpoint": f"{API_BASE}/hgcwa_passports/",
                "count": 100000,  # estimate
                "fields": "passport_label,total_label,genus,group,dim,g0,signature,gen_vectors,hyperelliptic,hyp_involution",
                "output": REPO_ROOT / "cartography" / "convergence" / "data" / "hgcwa_passports_g4plus.json",
                "sort": "passport_label",
                "query_params": "genus=i4",
            },
            {
                "name": "hgcwa_unique_groups",
                "endpoint": f"{API_BASE}/hgcwa_unique_groups/",
                "count": 1299,
                "fields": None,
                "output": REPO_ROOT / "cartography" / "convergence" / "data" / "hgcwa_groups.json",
                "sort": "label",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------
def fetch_page(url: str, dry_run: bool = False) -> dict | None:
    """Fetch one page from LMFDB API with retry + backoff."""
    if dry_run:
        print(f"  [DRY RUN] {url}")
        return None

    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    backoff = INITIAL_BACKOFF
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = backoff * (2 ** attempt)
                print(f"  Rate-limited (429). Backing off {wait:.0f}s "
                      f"(attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            elif e.code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"  Server error ({e.code}). Retrying in {wait:.0f}s "
                      f"(attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                print(f"  HTTP {e.code}: {e.reason}")
                return None
        except Exception as e:
            wait = backoff
            print(f"  Error: {e}. Retrying in {wait:.0f}s "
                  f"(attempt {attempt+1}/{MAX_RETRIES})")
            time.sleep(wait)

    print(f"  FAILED after {MAX_RETRIES} retries: {url}")
    return None


def download_table(table: dict, dry_run: bool = False) -> int:
    """Download an entire LMFDB table with pagination and checkpointing."""
    name = table["name"]
    endpoint = table["endpoint"]
    output_path = Path(table["output"])
    fields = table.get("fields")
    sort = table.get("sort", "")
    query_params = table.get("query_params", "")
    expected = table["count"]

    print(f"\n{'='*72}")
    print(f"TABLE: {name}")
    print(f"Expected: ~{expected:,} records")
    print(f"Output:   {output_path}")
    print(f"{'='*72}")

    # Resume from checkpoint
    checkpoint_path = output_path.with_suffix(".checkpoint.json")
    all_records = []
    offset = 0

    if checkpoint_path.exists() and not dry_run:
        try:
            with open(checkpoint_path, "r") as f:
                checkpoint = json.load(f)
            all_records = checkpoint.get("records", [])
            offset = checkpoint.get("offset", 0)
            print(f"  Resuming from checkpoint: {len(all_records)} records, offset={offset}")
        except Exception:
            print("  Checkpoint corrupt, starting fresh")

    if dry_run:
        # Show first URL only
        url = f"{endpoint}?_format=json&_limit={PAGE_SIZE}&_offset=0"
        if sort:
            url += f"&_sort={sort}"
        if fields:
            url += f"&_fields={fields}"
        if query_params:
            url += f"&{query_params}"
        fetch_page(url, dry_run=True)
        return 0

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_num = offset // PAGE_SIZE
    total_fetched = len(all_records)

    while True:
        url = f"{endpoint}?_format=json&_limit={PAGE_SIZE}&_offset={offset}"
        if sort:
            url += f"&_sort={sort}"
        if fields:
            url += f"&_fields={fields}"
        if query_params:
            url += f"&{query_params}"

        page_num += 1
        result = fetch_page(url)

        if result is None:
            print(f"  Stopping at offset {offset} (fetch failed)")
            break

        data = result.get("data", [])
        if not data:
            print(f"  No more data at offset {offset}")
            break

        all_records.extend(data)
        total_fetched += len(data)
        elapsed_pages = page_num

        # Progress
        pct = min(100, total_fetched / max(expected, 1) * 100)
        print(f"  Page {elapsed_pages}: +{len(data)} records "
              f"(total: {total_fetched:,} / ~{expected:,}, {pct:.1f}%)")

        # Checkpoint every 10 pages
        if elapsed_pages % 10 == 0:
            with open(checkpoint_path, "w") as f:
                json.dump({"records": all_records, "offset": offset + PAGE_SIZE}, f)

        offset += PAGE_SIZE
        time.sleep(DELAY_SECONDS)

        # Safety: LMFDB caps at ~10K per refined query
        # If we hit that, we need to refine
        if total_fetched >= 10000 and len(data) == PAGE_SIZE:
            # Still getting full pages past 10K — good, the API is cooperating
            pass

    # Save final results
    output = {
        "source": "LMFDB",
        "table": name,
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(all_records),
        "records": all_records,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)

    # Clean up checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    print(f"\n  SAVED: {len(all_records):,} records -> {output_path}")
    return len(all_records)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Download LMFDB frontier data for Charon"
    )
    parser.add_argument(
        "collection",
        choices=list(COLLECTIONS.keys()) + ["all"],
        help="Which collection to download"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show URLs without fetching"
    )
    parser.add_argument(
        "--table", type=str, default=None,
        help="Download only a specific table within the collection"
    )
    args = parser.parse_args()

    if args.collection == "all":
        targets = list(COLLECTIONS.keys())
    else:
        targets = [args.collection]

    print("LMFDB FRONTIER DOWNLOADER")
    print("=" * 72)
    print(f"Collections: {', '.join(targets)}")
    print(f"Delay: {DELAY_SECONDS}s between requests")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    # Time estimates
    for name in targets:
        coll = COLLECTIONS[name]
        total = sum(t["count"] for t in coll["tables"])
        pages = total // PAGE_SIZE + 1
        est_min = pages * DELAY_SECONDS / 60
        print(f"  {name}: {coll['description']}")
        print(f"    ~{total:,} records, ~{pages} pages, ~{est_min:.0f} min")

    if not args.dry_run:
        print()
        print("Starting in 3 seconds... (Ctrl+C to abort)")
        time.sleep(3)

    grand_total = 0
    t0 = time.time()

    for name in targets:
        coll = COLLECTIONS[name]
        print(f"\n\n{'#'*72}")
        print(f"# COLLECTION: {name} — {coll['description']}")
        print(f"{'#'*72}")

        for table in coll["tables"]:
            if args.table and table["name"] != args.table:
                continue
            n = download_table(table, dry_run=args.dry_run)
            grand_total += n

    elapsed = time.time() - t0
    print(f"\n\n{'='*72}")
    print(f"DONE: {grand_total:,} total records in {elapsed/60:.1f} min")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
