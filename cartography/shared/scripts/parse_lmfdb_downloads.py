#!/usr/bin/env python3
"""
Parse LMFDB text downloads into clean JSON files.
Reads tab-separated text files from james_downloads/, outputs JSON to cartography/.
"""

import json
import re
import time
from pathlib import Path

DOWNLOADS = Path(__file__).resolve().parents[2] / "james_downloads"
CART = Path(__file__).resolve().parents[2]

# Map: input filename pattern -> (column_names, output_path)
FILES = {
    "lmfdb_maass_rigor": {
        "columns": ["label", "level", "weight", "character", "spectral_parameter", "symmetry", "fricke"],
        "types":   [str, int, int, str, str, int, int],
        "output": CART / "maass" / "data" / "maass_rigor_full.json",
    },
    "lmfdb_hmf_forms": {
        "columns": ["label", "base_field", "level", "dimension"],
        "types":   [str, str, str, int],
        "output": CART / "convergence" / "data" / "hmf_forms_full.json",
    },
    "lmfdb_hgcwa_passports": {
        "columns": ["passport_label", "genus", "group", "group_order", "dimension", "signature"],
        "types":   [str, int, str, int, int, str],
        "output": CART / "convergence" / "data" / "hgcwa_passports_full.json",
    },
    "lmfdb_lat_lattices": {
        "columns": ["label", "dimension", "determinant", "level", "class_number", "minimal_vector", "aut_group_order"],
        "types":   [str, int, int, int, int, int, int],
        "output": CART / "lattices" / "data" / "lattices_full.json",
    },
    "lmfdb_gps_st": {
        "columns": ["label", "weight", "degree", "real_dim", "identity_component", "name",
                     "component_group", "prob_t0", "mean_a1_sq", "mean_a1_4th", "mean_a2"],
        "types":   [str, int, int, int, str, str, str, str, str, str, str],
        "output": CART / "convergence" / "data" / "sato_tate_groups.json",
    },
    "lmfdb_belyi_galmaps": {
        "columns": ["label", "degree", "group", "abc", "ramification_type", "genus", "orbit_size", "base_field"],
        "types":   [str, int, str, str, str, int, int, str],
        "output": CART / "convergence" / "data" / "belyi_maps.json",
    },
    "lmfdb_bmf_forms": {
        "columns": ["base_field", "level", "label", "sign", "base_change", "cm"],
        "types":   [str, str, str, str, str, str],
        "output": CART / "convergence" / "data" / "bianchi_forms.json",
    },
    "lmfdb_g2c_curves": {
        "columns": ["label", "class", "conductor", "rank", "torsion", "endomorphism_ring", "equation"],
        "types":   [str, str, int, str, str, str, str],
        "output": CART / "genus2" / "data" / "genus2_curves_lmfdb.json",
    },
    "lmfdb_hgm_motives": {
        "columns": ["label", "A", "B", "degree", "weight", "hodge"],
        "types":   [str, str, str, int, int, str],
        "output": CART / "convergence" / "data" / "hgm_motives.json",
    },
    "lmfdb_gps_groups": {
        "columns": ["label", "name", "order", "exponent", "num_conjugacy_classes", "center", "type_length"],
        "types":   [str, str, int, int, int, str, str],
        "output": CART / "groups" / "data" / "abstract_groups.json",
    },
}


def parse_value(val, typ):
    """Parse a tab-separated value into the target type."""
    val = val.strip().strip('"')
    if typ == int:
        try:
            return int(val)
        except ValueError:
            return val  # keep as string if not parseable (e.g. "2?")
    return val


def parse_file(path, config):
    """Parse one LMFDB text file into records."""
    columns = config["columns"]
    types = config["types"]
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # Skip comments, blanks, definition lines
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < len(columns):
                continue

            record = {}
            for i, (col, typ) in enumerate(zip(columns, types)):
                if i < len(parts):
                    record[col] = parse_value(parts[i], typ)
                else:
                    record[col] = None
            records.append(record)

    return records


def main():
    print("LMFDB Text Download Parser")
    print("=" * 60)

    # Find all matching files
    all_files = sorted(DOWNLOADS.glob("lmfdb_*.txt"))
    print(f"Found {len(all_files)} text files in {DOWNLOADS}\n")

    total = 0
    for path in all_files:
        name = path.stem
        # Skip duplicates
        if name.endswith("_B"):
            print(f"  SKIP (duplicate): {path.name}")
            continue

        # Find matching config
        config = None
        for prefix, cfg in FILES.items():
            if name.startswith(prefix):
                config = cfg
                break

        if not config:
            print(f"  SKIP (no config): {path.name}")
            continue

        records = parse_file(path, config)
        if not records:
            print(f"  SKIP (empty): {path.name}")
            continue

        # Save
        out_path = config["output"]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        output = {
            "source": "LMFDB (text download)",
            "source_file": path.name,
            "table": name.split("_0409")[0].replace("lmfdb_", ""),
            "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_records": len(records),
            "records": records,
        }

        with open(out_path, "w") as f:
            json.dump(output, f, indent=1)

        sz = out_path.stat().st_size
        print(f"  {path.name:50s} -> {len(records):>8,} records  ({sz:>12,} bytes)  {out_path.relative_to(CART)}")
        total += len(records)

    print(f"\nTotal: {total:,} records parsed")


if __name__ == "__main__":
    main()
