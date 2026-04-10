#!/usr/bin/env python3
"""
DLMF Formula Scraper
=====================
Downloads mathematical formulas from the Digital Library of Mathematical Functions.
Parses MathML/LaTeX from each chapter page.

Usage: python fetch_dlmf_formulas.py
Output: cartography/physics/data/dlmf/

Estimated time: ~30 minutes (36 chapters × 5s sleep)
"""

import json
import os
import re
import time
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[2] / "physics" / "data" / "dlmf"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLEEP_BETWEEN = 5  # seconds between chapter fetches

# DLMF has 36 chapters
CHAPTERS = list(range(1, 37))

BASE_URL = "https://dlmf.nist.gov"


def fetch_chapter(chapter_num):
    """Fetch formulas from a single DLMF chapter."""
    out_file = OUT_DIR / f"chapter_{chapter_num:02d}.json"
    if out_file.exists():
        print(f"  Chapter {chapter_num}: already downloaded, skipping")
        return True

    url = f"{BASE_URL}/{chapter_num}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Prometheus/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract chapter title
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        title = title_match.group(1) if title_match else f"Chapter {chapter_num}"

        # Extract all LaTeX formulas (inside math elements or \( \) or $$ $$)
        # DLMF uses data-math attribute for LaTeX
        latex_formulas = re.findall(r'data-math="([^"]*)"', html)

        # Also try to find equation numbers
        eq_numbers = re.findall(r'id="((?:E|S)\d+\.\w+\.\w+)"', html)

        # Extract section links for deeper crawling
        section_links = re.findall(rf'href="/{chapter_num}\.(\d+)"', html)
        sections = sorted(set(section_links))

        result = {
            "chapter": chapter_num,
            "title": title.strip(),
            "n_formulas_page": len(latex_formulas),
            "n_equations": len(eq_numbers),
            "n_sections": len(sections),
            "sections": sections,
            "formulas_sample": latex_formulas[:50],  # first 50 from main page
            "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  Chapter {chapter_num} ({title[:40]}): {len(latex_formulas)} formulas, {len(sections)} sections")
        return True

    except Exception as e:
        print(f"  Chapter {chapter_num}: ERROR - {e}")
        return False


def fetch_section(chapter_num, section_num):
    """Fetch formulas from a specific section."""
    out_file = OUT_DIR / f"section_{chapter_num:02d}_{section_num:02d}.json"
    if out_file.exists():
        return True

    url = f"{BASE_URL}/{chapter_num}.{section_num}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Prometheus/1.0 (research)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        latex_formulas = re.findall(r'data-math="([^"]*)"', html)
        eq_ids = re.findall(r'id="((?:E|S)\d+\.\d+\.\w+)"', html)

        result = {
            "chapter": chapter_num,
            "section": section_num,
            "n_formulas": len(latex_formulas),
            "n_equations": len(eq_ids),
            "equation_ids": eq_ids,
            "formulas": latex_formulas,
            "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"  Section {chapter_num}.{section_num}: ERROR - {e}")
        return False


def main():
    print("DLMF Formula Scraper")
    print(f"Output: {OUT_DIR}")
    print(f"Chapters: {len(CHAPTERS)}")
    print(f"Sleep: {SLEEP_BETWEEN}s between requests")
    print()

    # Phase 1: fetch chapter index pages
    print("Phase 1: Chapter index pages")
    for ch in CHAPTERS:
        print(f"[{ch}/{len(CHAPTERS)}]", end=" ")
        fetch_chapter(ch)
        time.sleep(SLEEP_BETWEEN)

    # Phase 2: fetch individual sections
    print("\nPhase 2: Section pages (deep crawl)")
    total_sections = 0
    for ch in CHAPTERS:
        ch_file = OUT_DIR / f"chapter_{ch:02d}.json"
        if not ch_file.exists():
            continue
        with open(ch_file) as f:
            ch_data = json.load(f)
        sections = ch_data.get("sections", [])
        for sec in sections:
            try:
                sec_num = int(sec)
            except ValueError:
                continue
            print(f"  [{ch}.{sec_num}]", end=" ", flush=True)
            fetch_section(ch, sec_num)
            total_sections += 1
            time.sleep(SLEEP_BETWEEN)
        print()

    # Summary
    all_formulas = 0
    for f in OUT_DIR.glob("section_*.json"):
        with open(f) as fh:
            d = json.load(fh)
            all_formulas += d.get("n_formulas", 0)

    print(f"\nDone: {len(CHAPTERS)} chapters, {total_sections} sections, {all_formulas} formulas")


if __name__ == "__main__":
    main()
