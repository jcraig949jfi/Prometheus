#!/usr/bin/env python3
"""
extract_spectral_config.py
--------------------------
Reads all_elements.json (NIST ASD energy-level data for 99 elements) and
produces nist_spectral_with_config.json: a flat JSON array of records with
normalised field names.

Output fields per record:
    element, Z, ion_stage, configuration, term, J, level_eV, prefix, suffix
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "all_elements.json"
DST = HERE / "nist_spectral_with_config.json"


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    records = []
    n_with_config = 0

    for elem_key, elem_block in data.items():
        element = elem_block["element"]
        Z = elem_block["Z"]

        for ion_stage, ion_block in elem_block["ions"].items():
            for lvl in ion_block["levels"]:
                config = lvl.get("Configuration", "")
                term = lvl.get("Term", "")
                J_val = lvl.get("J", "")
                prefix = lvl.get("Prefix", "")
                suffix = lvl.get("Suffix", "")

                # Parse energy; keep as float (or None when missing/empty)
                raw_eV = lvl.get("Level (eV)", "")
                try:
                    level_eV = float(raw_eV)
                except (ValueError, TypeError):
                    level_eV = None

                rec = {
                    "element": element,
                    "Z": Z,
                    "ion_stage": ion_stage,
                    "configuration": config,
                    "term": term,
                    "J": J_val,
                    "level_eV": level_eV,
                    "prefix": prefix,
                    "suffix": suffix,
                }
                records.append(rec)

                if config:
                    n_with_config += 1

    # Write output
    with open(DST, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1)

    # Summary
    elements = sorted({r["element"] for r in records})
    print(f"Elements:              {len(elements)}")
    print(f"Total records:         {len(records)}")
    print(f"With configuration:    {n_with_config}")
    print(f"Without configuration: {len(records) - n_with_config}")
    print(f"Output written to:     {DST}")


if __name__ == "__main__":
    main()
