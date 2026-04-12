#!/usr/bin/env python3
"""
LMFDB Paginator — Resume-safe browser-friendly downloader
==========================================================
Takes a seed JSON file (from browser download) and follows the `next` links
to paginate through the full dataset. Checkpoints after every page.

If reCAPTCHA blocks you mid-run, the script stops and prints a browser URL.
Download that page manually, drop it in the checkpoint dir, and rerun.

Usage:
    python lmfdb_paginate.py smf_samples     # Paginate from seed file
    python lmfdb_paginate.py maass_rigor     # Big one (~6 min at 1s delay)
    python lmfdb_paginate.py smf_ev          # 31 pages
    python lmfdb_paginate.py smf_fc          # 263 pages (~9 min)
    python lmfdb_paginate.py hmf_forms       # 3683 pages (~2 hours)
    python lmfdb_paginate.py hgcwa_passports # 3350 pages (~2 hours)
    python lmfdb_paginate.py --list          # Show all available targets

    python lmfdb_paginate.py smf_ev --delay 3   # Slower to avoid reCAPTCHA
    python lmfdb_paginate.py smf_ev --dry-run    # Show what would be fetched
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

LMFDB_BASE = "https://www.lmfdb.org"
DOWNLOADS_DIR = Path(__file__).resolve().parents[2] / "james_downloads"
DEFAULT_DELAY = 2.0
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"

# Where final merged files go
TARGETS = {
    "smf_samples": {
        "seed_url": f"{LMFDB_BASE}/api/smf_samples/?_format=json",
        "expected": 129,
        "output": "genus2/data/siegel_samples.json",
    },
    "smf_ev": {
        "seed_url": f"{LMFDB_BASE}/api/smf_ev/?_format=json",
        "expected": 3094,
        "output": "genus2/data/siegel_eigenvalues.json",
    },
    "smf_fc": {
        "seed_url": f"{LMFDB_BASE}/api/smf_fc/?_format=json",
        "expected": 26212,
        "output": "genus2/data/siegel_fourier_coeffs.json",
    },
    "smf_families": {
        "seed_url": f"{LMFDB_BASE}/api/smf_families/?_format=json",
        "expected": 14,
        "output": "genus2/data/siegel_families.json",
    },
    "smf_dims": {
        "seed_url": f"{LMFDB_BASE}/api/smf_dims/?_format=json",
        "expected": 72,
        "output": "genus2/data/siegel_dims.json",
    },
    "maass_rigor": {
        "seed_url": f"{LMFDB_BASE}/api/maass_rigor/?_format=json",
        "expected": 35416,
        "output": "maass/data/maass_rigor_full.json",
    },
    "maass_newforms": {
        "seed_url": f"{LMFDB_BASE}/api/maass_newforms/?_format=json",
        "expected": 14995,
        "output": "maass/data/maass_newforms_full.json",
    },
    "hmf_forms": {
        "seed_url": f"{LMFDB_BASE}/api/hmf_forms/?_format=json",
        "expected": 368356,
        "output": "convergence/data/hmf_forms.json",
    },
    "hmf_fields": {
        "seed_url": f"{LMFDB_BASE}/api/hmf_fields/?_format=json",
        "expected": 400,
        "output": "convergence/data/hmf_fields.json",
    },
    "hgcwa_passports": {
        "seed_url": f"{LMFDB_BASE}/api/hgcwa_passports/?_format=json",
        "expected": 335012,
        "output": "convergence/data/hgcwa_passports.json",
    },
    "hgcwa_unique_groups": {
        "seed_url": f"{LMFDB_BASE}/api/hgcwa_unique_groups/?_format=json",
        "expected": 1299,
        "output": "convergence/data/hgcwa_groups.json",
    },
}


def is_captcha(raw_bytes):
    """Detect if response is a reCAPTCHA page instead of JSON."""
    return b"recaptcha" in raw_bytes.lower() or b"challengepage" in raw_bytes.lower()


def fetch_page(url, delay=DEFAULT_DELAY):
    """Fetch one page. Returns (data_dict, is_blocked)."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
                if is_captcha(raw):
                    return None, True
                data = json.loads(raw.decode("utf-8"))
                return data, False
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = delay * (2 ** (attempt + 1))
                print(f"  429 rate limit. Waiting {wait:.0f}s...")
                time.sleep(wait)
            elif e.code == 404:
                print(f"  404: {url}")
                return None, False
            else:
                print(f"  HTTP {e.code}. Retry {attempt+1}/{MAX_RETRIES}")
                time.sleep(delay)
        except Exception as e:
            print(f"  Error: {e}. Retry {attempt+1}/{MAX_RETRIES}")
            time.sleep(delay)

    return None, False


def load_checkpoint(name):
    """Load checkpoint: list of all records so far + next URL."""
    cp_path = DOWNLOADS_DIR / f"{name}.checkpoint.json"
    if cp_path.exists():
        with open(cp_path) as f:
            cp = json.load(f)
        return cp.get("records", []), cp.get("next_url")
    return [], None


def save_checkpoint(name, records, next_url):
    """Save progress."""
    cp_path = DOWNLOADS_DIR / f"{name}.checkpoint.json"
    with open(cp_path, "w") as f:
        json.dump({"records": records, "next_url": next_url,
                    "count": len(records),
                    "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)


def load_seed(name):
    """Try to load a seed file from james_downloads."""
    # Try various naming patterns
    patterns = [
        f"{name}.json",
        f"{name.replace('_', '.')}.json",
        f"{name}_p1.json",
    ]
    for pat in patterns:
        path = DOWNLOADS_DIR / pat
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            records = data.get("data", [])
            next_url = data.get("next")
            if next_url and not next_url.startswith("http"):
                next_url = LMFDB_BASE + next_url
            print(f"  Seed: {path.name} ({len(records)} records)")
            return records, next_url
    return [], None


def paginate(name, delay=DEFAULT_DELAY, dry_run=False):
    """Paginate through an LMFDB collection."""
    target = TARGETS[name]
    expected = target["expected"]
    output_rel = target["output"]
    output_path = Path(__file__).resolve().parents[2] / output_rel

    print(f"\n{'='*60}")
    print(f"  {name}: {expected:,} expected records")
    print(f"  Output: {output_path}")
    print(f"{'='*60}")

    # Try checkpoint first, then seed
    records, next_url = load_checkpoint(name)
    if records:
        print(f"  Resuming from checkpoint: {len(records):,} records")
    else:
        records, next_url = load_seed(name)

    if not records and not next_url:
        # No seed — need to fetch first page
        next_url = target["seed_url"]
        print(f"  No seed file. Starting from: {next_url}")

    if not next_url:
        print(f"  Already complete ({len(records):,} records, no next URL)")
        if not dry_run:
            save_final(name, records, output_path)
        return len(records)

    page = len(records) // 100
    while next_url:
        page += 1
        if not next_url.startswith("http"):
            next_url = LMFDB_BASE + next_url
        # Ensure JSON format
        if "_format=json" not in next_url:
            sep = "&" if "?" in next_url else "?"
            next_url += f"{sep}_format=json"

        pct = min(100, len(records) / max(expected, 1) * 100)
        print(f"  Page {page}: {len(records):,}/{expected:,} ({pct:.0f}%) ", end="", flush=True)

        if dry_run:
            print(f"[DRY RUN] {next_url}")
            break

        data, blocked = fetch_page(next_url, delay)

        if blocked:
            # Check if we already have all expected records
            if len(records) >= expected:
                print(f"DONE (have {len(records):,} >= {expected:,} expected)")
                break
            print("BLOCKED (reCAPTCHA)")
            print(f"\n  ** reCAPTCHA detected! **")
            print(f"  Open this URL in your browser:")
            print(f"  {next_url}")
            print(f"  Save the result to: {DOWNLOADS_DIR / f'{name}_manual.json'}")
            print(f"  Then rerun this script -- it will pick up from the checkpoint.")
            save_checkpoint(name, records, next_url)
            return len(records)

        if data is None:
            print("FAILED")
            save_checkpoint(name, records, next_url)
            return len(records)

        new_records = data.get("data", [])
        if not new_records:
            print("empty (done)")
            break

        records.extend(new_records)
        next_url = data.get("next")
        if next_url and not next_url.startswith("http"):
            next_url = LMFDB_BASE + next_url

        print(f"+{len(new_records)} = {len(records):,}")

        # Checkpoint every 10 pages
        if page % 10 == 0:
            save_checkpoint(name, records, next_url)

        time.sleep(delay)

    if not dry_run:
        save_final(name, records, output_path)

    return len(records)


def save_final(name, records, output_path):
    """Save merged results and clean up checkpoint."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "source": "LMFDB",
        "table": name,
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(records),
        "records": records,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)
    print(f"  SAVED: {len(records):,} records -> {output_path}")

    # Clean checkpoint
    cp = DOWNLOADS_DIR / f"{name}.checkpoint.json"
    if cp.exists():
        cp.unlink()


def main():
    parser = argparse.ArgumentParser(description="LMFDB paginator")
    parser.add_argument("target", nargs="?", help="Collection name")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list or not args.target:
        print("Available targets:")
        for name, t in TARGETS.items():
            print(f"  {name:25s}  {t['expected']:>8,} records  -> {t['output']}")
        return

    if args.target == "all":
        targets = list(TARGETS.keys())
    elif args.target in TARGETS:
        targets = [args.target]
    else:
        print(f"Unknown target: {args.target}")
        print(f"Available: {', '.join(TARGETS.keys())}")
        return

    print("LMFDB PAGINATOR")
    print(f"Delay: {args.delay}s | Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")

    total = 0
    t0 = time.time()
    for name in targets:
        n = paginate(name, delay=args.delay, dry_run=args.dry_run)
        total += n

    elapsed = time.time() - t0
    print(f"\nTotal: {total:,} records in {elapsed/60:.1f} min")


if __name__ == "__main__":
    main()
