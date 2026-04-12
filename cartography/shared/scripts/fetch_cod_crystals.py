#!/usr/bin/env python3
"""
Crystallography Open Database (COD) — OPTIMADE API Downloader
==============================================================
Uses the OPTIMADE v1 API (standard, paginated, JSON) to fetch
crystal structure metadata in bulk.

Usage: python fetch_cod_crystals.py [--max N]
Output: cartography/physics/data/cod/cod_structures.json

Default: 10,000 structures. Override with --max.
Estimated time: ~20 min for 10K (100/page, 2s sleep).
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "physics" / "data" / "cod"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "cod_structures.json"
CHECKPOINT_FILE = OUT_DIR / "checkpoint.json"

# OPTIMADE v1 endpoint — standard materials database API
BASE_URL = "https://www.crystallography.net/cod/optimade/v1/structures"

PAGE_SIZE = 100
SLEEP_BETWEEN = 2  # seconds between requests
TIMEOUT = 90


def fetch_page(url):
    """Fetch a single OPTIMADE page. Returns (entries, next_url)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Prometheus/1.0 (mathematical-research)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
    except Exception as e:
        print(f"  ERROR fetching {url[:80]}...: {e}")
        return [], None

    entries = data.get("data", [])
    # OPTIMADE puts next page link in links.next
    links = data.get("links", {})
    next_url = None
    if isinstance(links, dict):
        next_url = links.get("next")
        # Can be a string or {"href": "..."}
        if isinstance(next_url, dict):
            next_url = next_url.get("href")

    return entries, next_url


def extract_metadata(entry):
    """Extract useful fields from an OPTIMADE structure entry."""
    attrs = entry.get("attributes", {})
    result = {
        "id": entry.get("id"),
        "type": entry.get("type"),
        # Chemical
        "chemical_formula_descriptive": attrs.get("chemical_formula_descriptive"),
        "chemical_formula_reduced": attrs.get("chemical_formula_reduced"),
        "chemical_formula_hill": attrs.get("chemical_formula_hill"),
        "elements": attrs.get("elements"),
        "nelements": attrs.get("nelements"),
        "nsites": attrs.get("nsites"),
        # Structural
        "lattice_vectors": attrs.get("lattice_vectors"),
        "dimension_types": attrs.get("dimension_types"),
        "nperiodic_dimensions": attrs.get("nperiodic_dimensions"),
        # Space group
        "space_group_symbol_hall": attrs.get("space_group_symbol_hall"),
        "space_group_symbol_hermann_mauguin": attrs.get("space_group_symbol_hermann_mauguin"),
        "space_group_it_number": attrs.get("space_group_it_number"),
    }

    # Compute cell parameters from lattice vectors if present
    vecs = attrs.get("lattice_vectors")
    if vecs and len(vecs) == 3:
        import math
        a_vec, b_vec, c_vec = vecs
        if a_vec and b_vec and c_vec:
            a = math.sqrt(sum(x**2 for x in a_vec))
            b = math.sqrt(sum(x**2 for x in b_vec))
            c = math.sqrt(sum(x**2 for x in c_vec))
            result["cell_a"] = round(a, 4)
            result["cell_b"] = round(b, 4)
            result["cell_c"] = round(c, 4)
            if a > 0 and b > 0 and c > 0:
                dot_bc = sum(x*y for x, y in zip(b_vec, c_vec))
                dot_ac = sum(x*y for x, y in zip(a_vec, c_vec))
                dot_ab = sum(x*y for x, y in zip(a_vec, b_vec))
                result["cell_alpha"] = round(math.degrees(math.acos(max(-1, min(1, dot_bc/(b*c))))), 2)
                result["cell_beta"] = round(math.degrees(math.acos(max(-1, min(1, dot_ac/(a*c))))), 2)
                result["cell_gamma"] = round(math.degrees(math.acos(max(-1, min(1, dot_ab/(a*b))))), 2)
                result["cell_volume"] = round(a * b * c * math.sqrt(
                    1 - (dot_bc/(b*c))**2 - (dot_ac/(a*c))**2 - (dot_ab/(a*b))**2
                    + 2*(dot_bc/(b*c))*(dot_ac/(a*c))*(dot_ab/(a*b))
                ), 2)

    return result


def load_checkpoint():
    """Load checkpoint if exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"entries": [], "next_url": None, "pages_done": 0}


def save_checkpoint(entries, next_url, pages_done):
    """Save progress."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"next_url": next_url, "pages_done": pages_done, "n_entries": len(entries)}, f)


def main():
    parser = argparse.ArgumentParser(description="Download COD crystal metadata via OPTIMADE API")
    parser.add_argument("--max", type=int, default=10000, help="Max structures to fetch (default: 10000)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()

    max_structures = args.max
    max_pages = (max_structures + PAGE_SIZE - 1) // PAGE_SIZE

    # Load existing data if resuming
    all_entries = []
    start_url = f"{BASE_URL}?page_limit={PAGE_SIZE}"
    pages_done = 0

    if args.resume and OUT_FILE.exists() and CHECKPOINT_FILE.exists():
        with open(OUT_FILE) as f:
            all_entries = json.load(f)
        cp = load_checkpoint()
        start_url = cp.get("next_url") or start_url
        pages_done = cp.get("pages_done", 0)
        print(f"Resuming: {len(all_entries)} entries, page {pages_done}")
    elif OUT_FILE.exists() and not args.resume:
        # Load existing to append
        pass

    print(f"COD OPTIMADE Downloader")
    print(f"Target: {max_structures} structures ({max_pages} pages)")
    print(f"Output: {OUT_FILE}")
    print(f"Sleep: {SLEEP_BETWEEN}s between requests")
    print()

    url = start_url
    consecutive_errors = 0

    for page_num in range(pages_done, max_pages):
        if url is None:
            print("No more pages (next_url is None). Done.")
            break

        print(f"[{page_num+1}/{max_pages}] Fetching... ({len(all_entries)} so far)", end=" ")
        entries, next_url = fetch_page(url)

        if not entries:
            consecutive_errors += 1
            print(f"  Empty page (error #{consecutive_errors})")
            if consecutive_errors >= 3:
                print("  3 consecutive empty pages. Stopping.")
                break
            time.sleep(SLEEP_BETWEEN * 2)
            # Retry same URL
            continue

        consecutive_errors = 0
        extracted = [extract_metadata(e) for e in entries]
        all_entries.extend(extracted)
        print(f"  +{len(extracted)} entries")

        # Save periodically (every 5 pages)
        if (page_num + 1) % 5 == 0:
            with open(OUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_entries, f, indent=1, ensure_ascii=False)
            save_checkpoint(all_entries, next_url, page_num + 1)
            print(f"  [checkpoint: {len(all_entries)} saved]")

        url = next_url
        if len(all_entries) >= max_structures:
            print(f"Reached target ({max_structures}). Stopping.")
            break

        time.sleep(SLEEP_BETWEEN)

    # Final save
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, indent=1, ensure_ascii=False)

    # Clean up checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

    print(f"\nDone: {len(all_entries)} structures saved to {OUT_FILE}")
    print(f"Size: {OUT_FILE.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
