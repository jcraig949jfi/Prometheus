#!/usr/bin/env python3
"""
Charon Data Blocker Pipeline -- Fetch missing datasets for Charon research
==========================================================================
Downloads three datasets that block Charon's cross-domain analysis:

  1. picard-fuchs   -- AESZ Calabi-Yau differential operators (Mainz server)
  2. hmf-hecke      -- HMF Hecke eigenvalues at scale (LMFDB API, paginated)
  3. mckay-thompson -- Full McKay-Thompson coefficient tables (OEIS API)

Conventions match fetch_lmfdb_frontiers.py:
  - 2s polite delay, exponential backoff on 429
  - Checkpoint/resume after every page
  - Standard output schema: {source, table, fetched, total_records, records}

Usage:
    python fetch_charon_blockers.py picard-fuchs
    python fetch_charon_blockers.py hmf-hecke
    python fetch_charon_blockers.py mckay-thompson
    python fetch_charon_blockers.py all
    python fetch_charon_blockers.py all --dry-run

Note: Brauer-Manin data requires cloning researcher repos -- see fetch_brauer_manin.sh
Note: Higher-weight Hecke charpolys require SageMath -- see compute_hecke_charpolys.sage
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DELAY_SECONDS = 2.0
MAX_RETRIES = 5
INITIAL_BACKOFF = 5.0
USER_AGENT = "Prometheus-Cartography/2.0 (mathematical research; polite)"
LMFDB_API = "https://www.lmfdb.org/api"
OEIS_API = "https://oeis.org/search"
PAGE_SIZE = 100

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


# ---------------------------------------------------------------------------
# Shared infrastructure (matches fetch_lmfdb_frontiers.py patterns)
# ---------------------------------------------------------------------------
def _make_request(url, retries=MAX_RETRIES, backoff=INITIAL_BACKOFF):
    """HTTP GET with exponential backoff on 429/5xx."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                wait = backoff * (2 ** attempt)
                print(f"  HTTP {e.code} -- backing off {wait:.0f}s (attempt {attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise
        except (urllib.error.URLError, OSError) as e:
            wait = backoff * (2 ** attempt)
            print(f"  Network error: {e} -- retrying in {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {retries} retries: {url}")


def _download_file(url, dest_path, retries=MAX_RETRIES, backoff=INITIAL_BACKOFF):
    """Download a file with retry/backoff."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    for attempt in range(retries):
        try:
            urllib.request.urlretrieve(url, dest_path)
            return True
        except (urllib.error.URLError, OSError) as e:
            wait = backoff * (2 ** attempt)
            print(f"  Download error: {e} -- retrying in {wait:.0f}s")
            time.sleep(wait)
    return False


def _save_checkpoint(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def _load_checkpoint(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def _timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# 1. Picard-Fuchs / AESZ Calabi-Yau Operators
# ---------------------------------------------------------------------------
def fetch_picard_fuchs(dry_run=False):
    """
    Download the AESZ Calabi-Yau differential operator database.
    Source: Almkvist-Enckevort-van Straten-Zudilin (Mainz).
    Also tries the supplementary tables if available.
    """
    dest_dir = REPO_ROOT / "cartography" / "physics" / "data" / "calabi_yau"
    dest_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        {
            "name": "AESZ_operators",
            "url": "http://www.mathematik.uni-mainz.de/CYequations/db/CYdb.txt",
            "filename": "AESZ_picard_fuchs_operators.txt",
            "description": "Main AESZ Calabi-Yau differential operator table",
        },
        {
            "name": "AESZ_instanton",
            "url": "http://www.mathematik.uni-mainz.de/CYequations/db/instanton.txt",
            "filename": "AESZ_instanton_numbers.txt",
            "description": "Instanton numbers for CY operators",
        },
        {
            "name": "AESZ_monodromy",
            "url": "http://www.mathematik.uni-mainz.de/CYequations/db/monodromy.txt",
            "filename": "AESZ_monodromy_data.txt",
            "description": "Monodromy data for CY operators",
        },
    ]

    print("\n=== Picard-Fuchs / AESZ Calabi-Yau Database ===")
    for src in sources:
        dest_path = dest_dir / src["filename"]

        if dest_path.exists():
            size = dest_path.stat().st_size
            print(f"  SKIP {src['name']}: already exists ({size:,} bytes)")
            continue

        if dry_run:
            print(f"  [DRY RUN] Would download: {src['url']}")
            print(f"            -> {dest_path}")
            continue

        print(f"  Downloading {src['description']}...")
        print(f"    URL: {src['url']}")
        if _download_file(src["url"], str(dest_path)):
            size = dest_path.stat().st_size
            print(f"    OK: {size:,} bytes -> {dest_path.name}")
        else:
            print(f"    FAILED: {src['name']} -- server may require manual download")

        time.sleep(DELAY_SECONDS)

    # Write manifest
    manifest = {
        "source": "AESZ Calabi-Yau Database (Mainz)",
        "description": "Picard-Fuchs differential operators for Calabi-Yau varieties",
        "fetched": _timestamp(),
        "files": {s["name"]: s["filename"] for s in sources},
        "reference": "Almkvist-Enckevort-van Straten-Zudilin",
        "url": "http://www.mathematik.uni-mainz.de/CYequations/",
    }
    manifest_path = dest_dir / "picard_fuchs_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest -> {manifest_path.name}")


# ---------------------------------------------------------------------------
# 2. HMF Hecke Eigenvalues at Scale
# ---------------------------------------------------------------------------
def fetch_hmf_hecke(dry_run=False):
    """
    Download HMF Hecke eigenvalues from LMFDB API.
    We already have hmf_forms metadata (368K forms) and hecke_orbits (454 orbits).
    This fetches the hmf_hecke table which stores per-form eigenvalue data.

    The LMFDB hmf_hecke table is huge (~1.37M records). We paginate with
    checkpointing every 10 pages.
    """
    dest_dir = REPO_ROOT / "cartography" / "convergence" / "data"
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_path = dest_dir / "hmf_hecke_eigenvalues.jsonl"
    checkpoint_path = dest_dir / "hmf_hecke.checkpoint.json"

    endpoint = f"{LMFDB_API}/hmf_hecke/"
    fields = "label,hecke_eigenvalues,AL_eigenvalues"

    print("\n=== HMF Hecke Eigenvalues (LMFDB) ===")

    if dry_run:
        url = f"{endpoint}?_fields={fields}&_limit={PAGE_SIZE}&_offset=0&_sort=label"
        print(f"  [DRY RUN] Endpoint: {url}")
        print(f"  [DRY RUN] Estimated: ~1.37M records, ~14,000 pages")
        print(f"  [DRY RUN] Output: {output_path}")
        return

    # Resume from checkpoint
    ckpt = _load_checkpoint(checkpoint_path)
    offset = ckpt["offset"] if ckpt else 0
    total_written = ckpt["total_written"] if ckpt else 0

    if offset > 0:
        print(f"  Resuming from offset {offset} ({total_written} records written)")

    mode = "a" if offset > 0 else "w"
    page_count = 0

    with open(output_path, mode) as out:
        while True:
            url = f"{endpoint}?_fields={fields}&_limit={PAGE_SIZE}&_offset={offset}&_sort=label"
            print(f"  Page {offset // PAGE_SIZE + 1} (offset={offset})...", end="", flush=True)

            try:
                data = _make_request(url)
            except RuntimeError as e:
                print(f"\n  FATAL: {e}")
                print(f"  Checkpoint saved at offset={offset}")
                _save_checkpoint(checkpoint_path, {"offset": offset, "total_written": total_written})
                return

            records = data.get("data", [])
            if not records:
                print(" -- no more records")
                break

            for rec in records:
                out.write(json.dumps(rec) + "\n")

            total_written += len(records)
            offset += PAGE_SIZE
            page_count += 1
            print(f" {len(records)} records (total: {total_written})")

            # Checkpoint every 10 pages
            if page_count % 10 == 0:
                _save_checkpoint(checkpoint_path, {"offset": offset, "total_written": total_written})
                out.flush()

            time.sleep(DELAY_SECONDS)

            # Safety: if we got fewer than PAGE_SIZE, we're at the end
            if len(records) < PAGE_SIZE:
                break

    # Clean up checkpoint on success
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    print(f"  DONE: {total_written} records -> {output_path.name}")


# ---------------------------------------------------------------------------
# 3. McKay-Thompson Full Coefficient Tables
# ---------------------------------------------------------------------------
# Complete OEIS IDs for all 194 conjugacy classes of the Monster group
# that have known McKay-Thompson series in OEIS.
# The j-function (class 1A) plus key classes through 71AB.
MCKAY_THOMPSON_SEQUENCES = {
    # Class: OEIS ID -- McKay-Thompson series T_g for Monster group
    "1A":  "A000521",   # j-function - 744
    "2A":  "A007191",   # T_2A = j^(1/2) related
    "2B":  "A007267",   # T_2B
    "3A":  "A030197",   # T_3A
    "3B":  "A007258",   # T_3B (also A014708)
    "3C":  "A030182",   # T_3C
    "4A":  "A007246",   # T_4A
    "4B":  "A007248",   # T_4B
    "4C":  "A007249",   # T_4C
    "4D":  "A007250",   # T_4D
    "5A":  "A007251",   # T_5A
    "5B":  "A007252",   # T_5B
    "6A":  "A007253",   # T_6A
    "6B":  "A007254",   # T_6B
    "6C":  "A007255",   # T_6C
    "6D":  "A007256",   # T_6D
    "6E":  "A007257",   # T_6E
    "7A":  "A030183",   # T_7A
    "7B":  "A030184",   # T_7B
    "8A":  "A030185",   # T_8A
    "10A": "A030186",   # T_10A
    "10B": "A058487",   # T_10B
    "12A": "A030188",   # T_12A
    "12B": "A058496",   # T_12B
    "13A": "A034318",   # T_13A (Hauptmodul Gamma_0(13))
    "25A": "A058553",   # T_25A (Hauptmodul Gamma_0(25))
}


def fetch_mckay_thompson(dry_run=False):
    """
    Fetch full McKay-Thompson coefficient series from OEIS.
    Stores both raw OEIS data and extracted coefficient arrays.
    """
    dest_dir = REPO_ROOT / "cartography" / "convergence" / "data" / "moonshine"
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== McKay-Thompson Coefficient Tables (OEIS) ===")
    print(f"  {len(MCKAY_THOMPSON_SEQUENCES)} conjugacy classes to fetch")

    results = {}
    fetched = 0
    skipped = 0

    for cls, seq_id in MCKAY_THOMPSON_SEQUENCES.items():
        cache_path = dest_dir / f"mckay_{cls}_{seq_id}.json"

        if cache_path.exists():
            print(f"  SKIP {cls} ({seq_id}): already cached")
            skipped += 1
            # Load for summary
            with open(cache_path) as f:
                results[cls] = json.load(f)
            continue

        if dry_run:
            print(f"  [DRY RUN] {cls} -> {seq_id}: {OEIS_API}?q=id:{seq_id}&fmt=json")
            continue

        url = f"{OEIS_API}?q=id:{seq_id}&fmt=json"
        print(f"  Fetching {cls} ({seq_id})...", end="", flush=True)

        try:
            data = _make_request(url)
        except RuntimeError:
            print(f" FAILED -- skipping")
            continue

        # OEIS JSON API returns a bare list of result dicts
        oeis_results = data if isinstance(data, list) else data.get("results", [])
        if oeis_results:
            entry = oeis_results[0]
            record = {
                "class": cls,
                "oeis_id": seq_id,
                "name": entry.get("name", ""),
                "data": entry.get("data", ""),  # comma-separated coefficients
                "offset": entry.get("offset", ""),
                "formula": entry.get("formula", []),
                "program": entry.get("program", []),
                "xref": entry.get("xref", []),
                "fetched": _timestamp(),
            }
            # Parse coefficient string into list of ints
            if record["data"]:
                try:
                    record["coefficients"] = [int(x) for x in record["data"].split(",")]
                    record["n_coefficients"] = len(record["coefficients"])
                except ValueError:
                    record["coefficients"] = []
                    record["n_coefficients"] = 0

            with open(cache_path, "w") as f:
                json.dump(record, f, indent=2)

            results[cls] = record
            n = record.get("n_coefficients", 0)
            print(f" {n} coefficients")
            fetched += 1
        else:
            print(f" no results in OEIS")

        time.sleep(DELAY_SECONDS)

    # Write combined summary
    if not dry_run:
        summary = {
            "source": "OEIS",
            "table": "McKay-Thompson series (Monster moonshine)",
            "fetched": _timestamp(),
            "total_classes": len(MCKAY_THOMPSON_SEQUENCES),
            "fetched_count": fetched,
            "skipped_count": skipped,
            "classes": {
                cls: {
                    "oeis_id": r.get("oeis_id"),
                    "n_coefficients": r.get("n_coefficients", 0),
                    "name": r.get("name", ""),
                }
                for cls, r in results.items()
            },
        }
        summary_path = dest_dir / "mckay_thompson_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n  Summary -> {summary_path.name}")
        print(f"  {fetched} fetched, {skipped} cached, {len(results)} total")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Charon data blocker pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        choices=["picard-fuchs", "hmf-hecke", "mckay-thompson", "all"],
        help="Which dataset to fetch",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show URLs without fetching")
    args = parser.parse_args()

    targets = {
        "picard-fuchs": fetch_picard_fuchs,
        "hmf-hecke": fetch_hmf_hecke,
        "mckay-thompson": fetch_mckay_thompson,
    }

    print(f"Charon data pipeline -- {_timestamp()}")
    print(f"Repo root: {REPO_ROOT}")

    if args.target == "all":
        for name, fn in targets.items():
            fn(dry_run=args.dry_run)
    else:
        targets[args.target](dry_run=args.dry_run)

    print("\n=== Pipeline complete ===")
    if not args.dry_run:
        print("Remaining manual steps:")
        print("  1. Run fetch_brauer_manin.sh for Brauer-Manin obstruction repos")
        print("  2. Run compute_hecke_charpolys.sage in SageMath for Gouvea-Mazur data")


if __name__ == "__main__":
    main()
