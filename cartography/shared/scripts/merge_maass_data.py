#!/usr/bin/env python3
"""
Merge Maass form metadata with Fourier coefficients from LMFDB dump.
====================================================================
We already have 14,995 coefficient records from the PostgreSQL dump.
This script joins them with form metadata (spectral parameter, level,
symmetry, etc.) to produce a single analysis-ready file.

Usage: python merge_maass_data.py
Output: cartography/maass/data/maass_with_coefficients.json
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DUMP_DIR = SCRIPT_DIR.parents[1] / "lmfdb_dump"
MAASS_DIR = SCRIPT_DIR.parents[1] / "maass" / "data"

# Input files
COEFFICIENTS_FILE = DUMP_DIR / "maass_newforms_coefficients.json"
NEWFORMS_FILE = DUMP_DIR / "maass_newforms.json"
EXTRAS_FILE = DUMP_DIR / "maass_newforms_extras.json"
LOCAL_FORMS = MAASS_DIR / "maass_forms_full.json"

# Output
OUT_FILE = MAASS_DIR / "maass_with_coefficients.json"


def load_dump(path):
    """Load LMFDB dump file, return records list."""
    if not path.exists():
        print(f"  {path.name}: not found")
        return []
    with open(path) as f:
        data = json.load(f)
    records = data.get("records", [])
    print(f"  {path.name}: {len(records)} records, columns={data.get('columns', '?')}")
    return records


def main():
    print("Merging Maass form data...")
    print()

    # Load coefficient records
    print("Loading coefficients:")
    coeff_records = load_dump(COEFFICIENTS_FILE)

    # Build maass_id -> coefficients map
    coeff_map = {}
    for r in coeff_records:
        mid = r.get("maass_id")
        if mid:
            coeffs = r.get("coefficients", [])
            # Convert string coefficients to float
            if isinstance(coeffs, list) and coeffs:
                try:
                    coeffs = [float(c) if isinstance(c, str) else c for c in coeffs]
                except (ValueError, TypeError):
                    pass
            coeff_map[mid] = coeffs

    print(f"  {len(coeff_map)} forms with coefficients")
    if coeff_map:
        sample_key = list(coeff_map.keys())[0]
        sample_val = coeff_map[sample_key]
        print(f"  Sample: maass_id={sample_key}, {len(sample_val)} coefficients")

    # Load form metadata
    print("\nLoading form metadata:")
    newform_records = load_dump(NEWFORMS_FILE)
    extras_records = load_dump(EXTRAS_FILE)

    # Build metadata maps
    form_map = {}
    for r in newform_records:
        mid = r.get("maass_id") or r.get("label")
        if mid:
            form_map[mid] = r

    extras_map = {}
    for r in extras_records:
        mid = r.get("maass_id") or r.get("label")
        if mid:
            extras_map[mid] = r

    # Also load local forms
    local_forms = []
    if LOCAL_FORMS.exists():
        with open(LOCAL_FORMS) as f:
            local_forms = json.load(f)
        print(f"  local maass_forms_full.json: {len(local_forms)} forms")
        for lf in local_forms:
            mid = lf.get("maass_label")
            if mid and mid not in form_map:
                form_map[mid] = lf

    print(f"\n  Total metadata: {len(form_map)} forms")
    print(f"  Total extras: {len(extras_map)} forms")

    # Merge
    print("\nMerging...")
    merged = []
    coeff_count = 0
    for mid, coeffs in coeff_map.items():
        entry = {
            "maass_id": mid,
            "coefficients": coeffs,
            "n_coefficients": len(coeffs) if isinstance(coeffs, list) else 0,
        }

        # Add metadata
        if mid in form_map:
            meta = form_map[mid]
            for field in ["level", "weight", "spectral_parameter", "symmetry",
                          "conrey_index", "fricke_eigenvalue", "character",
                          "analytic_conductor"]:
                if field in meta:
                    entry[field] = meta[field]

        # Add extras
        if mid in extras_map:
            extra = extras_map[mid]
            for field in ["analytic_conductor", "self_dual", "primitive",
                          "sign_arg", "st_group"]:
                if field in extra and field not in entry:
                    entry[field] = extra[field]

        if entry.get("n_coefficients", 0) > 0:
            coeff_count += 1
        merged.append(entry)

    # Sort by spectral parameter
    merged.sort(key=lambda x: x.get("spectral_parameter", 999999))

    # Save
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=1, ensure_ascii=False)

    print(f"\nDone: {len(merged)} Maass forms merged")
    print(f"  With coefficients: {coeff_count}")
    print(f"  With metadata: {sum(1 for m in merged if 'spectral_parameter' in m)}")
    print(f"  Output: {OUT_FILE}")
    print(f"  Size: {OUT_FILE.stat().st_size / 1024:.0f} KB")

    # Stats
    if merged:
        n_coeffs = [m.get("n_coefficients", 0) for m in merged if m.get("n_coefficients", 0) > 0]
        if n_coeffs:
            print(f"\n  Coefficient count: min={min(n_coeffs)}, max={max(n_coeffs)}, median={sorted(n_coeffs)[len(n_coeffs)//2]}")
        levels = [m.get("level") for m in merged if m.get("level") is not None]
        if levels:
            print(f"  Levels: {len(set(levels))} unique, range [{min(levels)}, {max(levels)}]")
        specs = [float(m["spectral_parameter"]) for m in merged if m.get("spectral_parameter") is not None]
        if specs:
            print(f"  Spectral parameters: range [{min(specs):.3f}, {max(specs):.3f}]")


if __name__ == "__main__":
    main()
