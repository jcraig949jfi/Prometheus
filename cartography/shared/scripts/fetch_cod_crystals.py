#!/usr/bin/env python3
"""
Crystallography Open Database (COD) Downloader
================================================
Downloads crystal structure metadata in batches.
Full CIF files are huge (~10GB) so we fetch metadata only.

Usage: python fetch_cod_crystals.py
Output: cartography/physics/data/cod/

Estimated time: ~4 hours (520K structures, batches of 500, 2s sleep)
"""

import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "physics" / "data" / "cod"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLEEP_BETWEEN = 2  # seconds between batch requests
BATCH_SIZE = 500
MAX_BATCHES = 100  # cap at 50K structures for initial run

# COD search API returns CSV/JSON
BASE_URL = "https://www.crystallography.net/cod/result"


def fetch_batch(offset):
    """Fetch a batch of COD entries."""
    out_file = OUT_DIR / f"batch_{offset:06d}.json"
    if out_file.exists():
        print(f"  Batch {offset}: already downloaded, skipping")
        return True

    params = {
        "format": "json",
        "limit": str(BATCH_SIZE),
        "offset": str(offset),
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Prometheus/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8", errors="replace")

        # Try to parse as JSON
        try:
            entries = json.loads(data)
            if isinstance(entries, list):
                n = len(entries)
            elif isinstance(entries, dict):
                n = len(entries.get("results", entries.get("data", [])))
            else:
                n = 0
        except json.JSONDecodeError:
            # Might be HTML error page
            entries = {"raw": data[:2000], "error": "not JSON"}
            n = 0

        result = {
            "offset": offset,
            "batch_size": BATCH_SIZE,
            "n_entries": n,
            "data": entries if n > 0 else None,
            "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  Batch {offset}: {n} entries")
        return n > 0

    except Exception as e:
        print(f"  Batch {offset}: ERROR - {e}")
        return False


def main():
    print("COD Crystal Structure Downloader")
    print(f"Output: {OUT_DIR}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Max batches: {MAX_BATCHES} ({MAX_BATCHES * BATCH_SIZE} structures)")
    print(f"Sleep: {SLEEP_BETWEEN}s between requests")
    print(f"Estimated time: {MAX_BATCHES * SLEEP_BETWEEN / 60:.0f} minutes")
    print()

    total = 0
    for i in range(MAX_BATCHES):
        offset = i * BATCH_SIZE
        print(f"[{i+1}/{MAX_BATCHES}]", end=" ")
        has_data = fetch_batch(offset)
        total += BATCH_SIZE if has_data else 0
        if not has_data:
            print("  No more data, stopping.")
            break
        time.sleep(SLEEP_BETWEEN)

    print(f"\nDone: ~{total} structures downloaded")


if __name__ == "__main__":
    main()
