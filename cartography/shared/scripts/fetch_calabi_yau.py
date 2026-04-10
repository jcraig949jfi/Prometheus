#!/usr/bin/env python3
"""
Calabi-Yau Database Downloader
===============================
Downloads Hodge number data and polytope lists from the Kreuzer-Skarke database.

Usage: python fetch_calabi_yau.py
Output: cartography/physics/data/calabi_yau/

Estimated time: ~10 minutes (small files)
"""

import json
import os
import time
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "physics" / "data" / "calabi_yau"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLEEP_BETWEEN = 3

# Kreuzer-Skarke data URLs
URLS = {
    "hodge_3d": "http://hep.itp.tuwien.ac.at/~kreuzer/CY/hlist3.gz",
    "hodge_4d": "http://hep.itp.tuwien.ac.at/~kreuzer/CY/hlist4.gz",
    "cicy_list": "http://hep.itp.tuwien.ac.at/~kreuzer/CY/CICYList.txt",
}


def download_file(name, url):
    """Download a single file."""
    ext = url.split(".")[-1]
    out_file = OUT_DIR / f"{name}.{ext}"
    if out_file.exists():
        print(f"  {name}: already downloaded ({out_file.stat().st_size} bytes)")
        return True

    try:
        print(f"  {name}: downloading from {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Prometheus/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()

        with open(out_file, "wb") as f:
            f.write(data)

        print(f"  {name}: saved {len(data)} bytes to {out_file.name}")
        return True

    except Exception as e:
        print(f"  {name}: ERROR - {e}")
        return False


def main():
    print("Calabi-Yau Database Downloader")
    print(f"Output: {OUT_DIR}")
    print()

    for name, url in URLS.items():
        download_file(name, url)
        time.sleep(SLEEP_BETWEEN)

    # Also try to get the main index page for reference
    download_file("index_page", "http://hep.itp.tuwien.ac.at/~kreuzer/CY/CYpalp.html")

    print("\nDone.")


if __name__ == "__main__":
    main()
