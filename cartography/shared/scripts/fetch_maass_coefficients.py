#!/usr/bin/env python3
"""
LMFDB Maass Form Fourier Coefficient Fetcher
=============================================
Fetches Fourier coefficients for individual Maass newforms via the LMFDB API.
The bulk export lacks these coefficients — need per-form API queries.

Usage: python fetch_maass_coefficients.py [--max-forms 500] [--coeffs 100]
Output: cartography/maass/data/maass_coefficients.json

Estimated time: ~25 min for 500 forms (3s sleep between requests).
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parents[1] / "maass" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "maass_coefficients.json"
CHECKPOINT_FILE = OUT_DIR / "maass_coeff_checkpoint.json"

# Existing Maass form data
MAASS_DATA = SCRIPT_DIR.parents[1] / "maass" / "data" / "maass_forms.json"

# LMFDB API base
LMFDB_API = "https://www.lmfdb.org/api"
SLEEP_BETWEEN = 3  # be polite
TIMEOUT = 60


def fetch_maass_index(max_forms=500):
    """Get list of Maass form labels from LMFDB API or local data."""
    # Try local data first
    if MAASS_DATA.exists():
        with open(MAASS_DATA) as f:
            data = json.load(f)
        if isinstance(data, list):
            labels = [d.get("label") or d.get("maass_id") or d.get("id") for d in data]
            labels = [l for l in labels if l]
            if labels:
                print(f"Using {len(labels)} labels from local Maass data")
                return labels[:max_forms]

    # Fetch from LMFDB API
    print("Fetching Maass form index from LMFDB API...")
    url = f"{LMFDB_API}/mf.maass.newforms/?_fields=label,spectral_parameter,level,weight,symmetry&_limit={max_forms}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Prometheus/1.0 (mathematical-research)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        records = data.get("data", data.get("results", []))
        labels = [r.get("label") for r in records if r.get("label")]
        print(f"Got {len(labels)} Maass form labels from LMFDB")
        return labels[:max_forms]
    except Exception as e:
        print(f"Error fetching index: {e}")
        return []


def fetch_coefficients_for_form(label, n_coeffs=100):
    """Fetch Fourier coefficients for a single Maass form."""
    # Try the maass_newforms endpoint with coefficients
    url = f"{LMFDB_API}/mf.maass.newforms/?label={urllib.parse.quote(label)}&_fields=label,spectral_parameter,level,weight,symmetry,coefficients"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Prometheus/1.0 (mathematical-research)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        records = data.get("data", data.get("results", []))
        if not records:
            return None

        record = records[0]
        coeffs = record.get("coefficients", [])

        # If coefficients not in main record, try dedicated endpoint
        if not coeffs:
            coeff_url = f"{LMFDB_API}/mf.maass.newform_coeffs/?label={urllib.parse.quote(label)}&_limit={n_coeffs}&_fields=label,coefficients,index"
            req2 = urllib.request.Request(coeff_url, headers={
                "User-Agent": "Prometheus/1.0 (mathematical-research)",
                "Accept": "application/json",
            })
            try:
                with urllib.request.urlopen(req2, timeout=TIMEOUT) as resp2:
                    raw2 = resp2.read().decode("utf-8")
                coeff_data = json.loads(raw2)
                coeff_records = coeff_data.get("data", coeff_data.get("results", []))
                if coeff_records:
                    coeffs = coeff_records
            except Exception:
                pass

        return {
            "label": label,
            "spectral_parameter": record.get("spectral_parameter"),
            "level": record.get("level"),
            "weight": record.get("weight"),
            "symmetry": record.get("symmetry"),
            "n_coefficients": len(coeffs) if isinstance(coeffs, list) else 0,
            "coefficients": coeffs[:n_coeffs] if isinstance(coeffs, list) else coeffs,
        }

    except Exception as e:
        print(f"  Error for {label}: {e}")
        return None


def load_checkpoint():
    """Load progress checkpoint."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"done_labels": [], "results": []}


def save_checkpoint(done_labels, results):
    """Save progress."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"done_labels": done_labels, "n_results": len(results)}, f)


def main():
    parser = argparse.ArgumentParser(description="Fetch Maass form Fourier coefficients from LMFDB")
    parser.add_argument("--max-forms", type=int, default=500, help="Max forms to fetch (default: 500)")
    parser.add_argument("--coeffs", type=int, default=100, help="Coefficients per form (default: 100)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()

    # Get form labels
    labels = fetch_maass_index(args.max_forms)
    if not labels:
        print("No Maass form labels found. Check LMFDB connection or local data.")
        # Try direct spectral parameter range query
        print("Trying spectral parameter range query...")
        url = f"{LMFDB_API}/mf.maass.newforms/?spectral_parameter=1..20&_fields=label&_limit={args.max_forms}"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Prometheus/1.0 (mathematical-research)",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read().decode())
            records = data.get("data", data.get("results", []))
            labels = [r["label"] for r in records if "label" in r]
            print(f"Got {len(labels)} labels from spectral parameter query")
        except Exception as e:
            print(f"Fallback also failed: {e}")
            sys.exit(1)

    # Load existing results if resuming
    results = []
    done_labels = set()
    if args.resume and OUT_FILE.exists():
        with open(OUT_FILE) as f:
            results = json.load(f)
        done_labels = {r["label"] for r in results}
        print(f"Resuming: {len(results)} forms already fetched")

    remaining = [l for l in labels if l not in done_labels]
    print(f"\nFetching coefficients for {len(remaining)} Maass forms...")
    print(f"Coefficients per form: {args.coeffs}")
    print(f"Sleep between requests: {SLEEP_BETWEEN}s")
    print(f"Estimated time: {len(remaining) * SLEEP_BETWEEN / 60:.0f} minutes\n")

    consecutive_errors = 0
    for i, label in enumerate(remaining):
        print(f"[{i+1}/{len(remaining)}] {label}", end=" ")
        result = fetch_coefficients_for_form(label, args.coeffs)

        if result:
            results.append(result)
            done_labels.add(label)
            n_c = result.get("n_coefficients", 0)
            print(f"  -> {n_c} coefficients, R={result.get('spectral_parameter', '?')}")
            consecutive_errors = 0
        else:
            consecutive_errors += 1
            print(f"  -> FAILED (#{consecutive_errors})")
            if consecutive_errors >= 5:
                print("5 consecutive failures. Saving and stopping.")
                break

        # Save every 25 forms
        if (i + 1) % 25 == 0:
            with open(OUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=1, ensure_ascii=False)
            save_checkpoint(list(done_labels), results)
            print(f"  [checkpoint: {len(results)} forms saved]")

        time.sleep(SLEEP_BETWEEN)

    # Final save
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)

    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

    # Summary
    with_coeffs = sum(1 for r in results if r.get("n_coefficients", 0) > 0)
    print(f"\nDone: {len(results)} forms fetched, {with_coeffs} with coefficients")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
