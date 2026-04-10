#!/usr/bin/env python3
"""
NIST Atomic Spectra Database Scraper
=====================================
Downloads energy levels and spectral lines for all elements.
Sleeps between requests to avoid rate limiting.

Usage: python fetch_nist_spectra.py
Output: cartography/physics/data/nist_spectra/

Estimated time: ~2 hours (92 elements × 2 queries × 3s sleep)
"""

import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "physics" / "data" / "nist_spectra"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# All elements
ELEMENTS = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U",
]

SLEEP_BETWEEN = 3  # seconds between requests

BASE_URL = "https://physics.nist.gov/cgi-bin/ASD/energy1.pl"


def fetch_energy_levels(element):
    """Fetch energy levels for a single element (neutral atom, first ion)."""
    out_file = OUT_DIR / f"{element}_levels.json"
    if out_file.exists():
        print(f"  {element}: already downloaded, skipping")
        return True

    params = {
        "spectrum": f"{element} I",  # neutral atom
        "units": "1",  # cm^-1
        "format": "3",  # tab-delimited
        "output": "0",  # all data
        "page_size": "15",
        "multiplet_ordered": "0",
        "conf_out": "on",
        "term_out": "on",
        "level_out": "on",
        "unc_out": "on",
        "j_out": "on",
        "lande_out": "on",
        "submit": "Retrieve Data",
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Prometheus/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Parse the HTML table (rough extraction)
        lines = []
        in_pre = False
        for line in html.split("\n"):
            if "<pre>" in line.lower():
                in_pre = True
                continue
            if "</pre>" in line.lower():
                in_pre = False
                continue
            if in_pre and line.strip():
                lines.append(line)

        result = {
            "element": element,
            "spectrum": f"{element} I",
            "n_lines": len(lines),
            "raw_lines": lines[:500],  # cap to avoid huge files
            "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        with open(out_file, "w") as f:
            json.dump(result, f, indent=2)

        print(f"  {element}: {len(lines)} lines saved")
        return True

    except Exception as e:
        print(f"  {element}: ERROR - {e}")
        return False


def main():
    print(f"NIST Atomic Spectra Scraper")
    print(f"Output: {OUT_DIR}")
    print(f"Elements: {len(ELEMENTS)}")
    print(f"Sleep: {SLEEP_BETWEEN}s between requests")
    print(f"Estimated time: {len(ELEMENTS) * SLEEP_BETWEEN / 60:.0f} minutes")
    print()

    success = 0
    for i, elem in enumerate(ELEMENTS):
        print(f"[{i+1}/{len(ELEMENTS)}] Fetching {elem}...")
        if fetch_energy_levels(elem):
            success += 1
        time.sleep(SLEEP_BETWEEN)

    print(f"\nDone: {success}/{len(ELEMENTS)} elements downloaded")


if __name__ == "__main__":
    main()
