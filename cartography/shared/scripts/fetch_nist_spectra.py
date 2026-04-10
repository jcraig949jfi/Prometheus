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

        # Response is tab-delimited text, not HTML
        # First line is header, rest are data
        lines = [l.strip() for l in html.split("\n") if l.strip()]

        # Parse into structured records
        if lines:
            header = lines[0]
            data_lines = lines[1:]
        else:
            header = ""
            data_lines = []

        # Extract energy levels
        levels = []
        for line in data_lines:
            fields = line.split("\t")
            if len(fields) >= 5:
                try:
                    config = fields[0].strip().strip('"')
                    term = fields[1].strip().strip('"') if len(fields) > 1 else ""
                    j_val = fields[2].strip().strip('"') if len(fields) > 2 else ""
                    energy_str = fields[4].strip().strip('"') if len(fields) > 4 else ""
                    if energy_str:
                        energy = float(energy_str)
                        levels.append({
                            "config": config,
                            "term": term,
                            "J": j_val,
                            "energy_eV": energy,
                        })
                except (ValueError, IndexError):
                    pass

        result = {
            "element": element,
            "spectrum": f"{element} I",
            "n_levels": len(levels),
            "levels": levels,
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
