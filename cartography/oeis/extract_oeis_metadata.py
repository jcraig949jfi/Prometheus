"""
Extract OEIS metadata from oeisdata repo .seq files.
=====================================================
Parses keyword (%K), formula (%F), and program (%o) lines from .seq files.

Outputs:
  - cartography/oeis/data/oeis_keywords.json   (seq_id -> list of keywords)
  - cartography/oeis/data/oeis_formulas.jsonl   (seq_id, formula_text lines)
  - cartography/oeis/data/oeis_programs.jsonl   (seq_id, language, program_text lines)

Processes the first 100K sequences (A000000-A099999) by default.
Run standalone:  python extract_oeis_metadata.py [--max N] [--all]
"""

import json
import os
import sys
import time
from pathlib import Path

# Paths
REPO = Path(__file__).resolve().parents[2]
OEISDATA_SEQ = REPO / "charon" / "james_downloads" / "oeisdata" / "seq"
OUT_DIR = Path(__file__).resolve().parent / "data"

OUT_KEYWORDS = OUT_DIR / "oeis_keywords.json"
OUT_FORMULAS = OUT_DIR / "oeis_formulas.jsonl"
OUT_PROGRAMS = OUT_DIR / "oeis_programs.jsonl"


def parse_seq_file(filepath: Path) -> dict:
    """Parse a single .seq file, extracting %K, %F, and %o lines.

    Returns dict with keys: seq_id, keywords, formulas, programs.
    """
    seq_id = filepath.stem.upper()  # e.g. A000001
    keywords = []
    formula_lines = []
    program_lines = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue

                # %K lines: keywords (comma-separated)
                if line.startswith("%K "):
                    # Format: %K A000001 nonn,core,nice,hard
                    parts = line.split(None, 2)
                    if len(parts) >= 3:
                        kws = [k.strip() for k in parts[2].split(",") if k.strip()]
                        keywords.extend(kws)

                # %F lines: formulas
                elif line.startswith("%F "):
                    parts = line.split(None, 2)
                    if len(parts) >= 3:
                        formula_lines.append(parts[2])

                # %o lines: programs (Maple, Mathematica, PARI, Python, etc.)
                elif line.startswith("%o "):
                    parts = line.split(None, 2)
                    if len(parts) >= 3:
                        program_lines.append(parts[2])

    except Exception as e:
        print(f"  WARNING: Could not read {filepath}: {e}", file=sys.stderr)

    return {
        "seq_id": seq_id,
        "keywords": keywords,
        "formulas": formula_lines,
        "programs": program_lines,
    }


def detect_language(program_text: str) -> str:
    """Heuristic to detect programming language from %o line."""
    text = program_text.strip()
    if text.startswith("("):
        # Format: (PARI) code... or (Python) code...
        paren_end = text.find(")")
        if paren_end > 1:
            return text[1:paren_end].strip()
    return "unknown"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract OEIS metadata from oeisdata .seq files")
    parser.add_argument("--max", type=int, default=100_000,
                        help="Maximum number of sequences to process (default: 100000)")
    parser.add_argument("--all", action="store_true",
                        help="Process all sequences (overrides --max)")
    args = parser.parse_args()

    max_seqs = None if args.all else args.max

    if not OEISDATA_SEQ.exists():
        print(f"ERROR: oeisdata seq directory not found at {OEISDATA_SEQ}")
        print("Clone the oeisdata repo to charon/james_downloads/oeisdata/")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect .seq file paths in sorted order
    print(f"Scanning {OEISDATA_SEQ} for .seq files...")
    seq_dirs = sorted(OEISDATA_SEQ.iterdir())
    seq_files = []
    for d in seq_dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix == ".seq":
                seq_files.append(f)
                if max_seqs and len(seq_files) >= max_seqs:
                    break
        if max_seqs and len(seq_files) >= max_seqs:
            break

    total = len(seq_files)
    print(f"Found {total:,} .seq files to process")

    # Process files
    t0 = time.time()
    all_keywords = {}  # seq_id -> [keywords]
    n_formulas = 0
    n_programs = 0
    keyword_counts = {}  # keyword -> count

    f_formulas = open(OUT_FORMULAS, "w", encoding="utf-8")
    f_programs = open(OUT_PROGRAMS, "w", encoding="utf-8")

    try:
        for i, fpath in enumerate(seq_files):
            parsed = parse_seq_file(fpath)
            sid = parsed["seq_id"]

            # Keywords
            if parsed["keywords"]:
                all_keywords[sid] = parsed["keywords"]
                for kw in parsed["keywords"]:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

            # Formulas
            for formula in parsed["formulas"]:
                f_formulas.write(json.dumps({"seq_id": sid, "formula": formula},
                                            ensure_ascii=False) + "\n")
                n_formulas += 1

            # Programs
            for prog in parsed["programs"]:
                lang = detect_language(prog)
                f_programs.write(json.dumps({"seq_id": sid, "language": lang, "program": prog},
                                            ensure_ascii=False) + "\n")
                n_programs += 1

            if (i + 1) % 10000 == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed
                print(f"  Processed {i+1:,}/{total:,} sequences "
                      f"({elapsed:.1f}s, {rate:.0f} seq/s)")

    finally:
        f_formulas.close()
        f_programs.close()

    # Save keywords
    with open(OUT_KEYWORDS, "w", encoding="utf-8") as f:
        json.dump(all_keywords, f, ensure_ascii=False)

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'='*60}")
    print(f"OEIS Metadata Extraction Complete")
    print(f"{'='*60}")
    print(f"  Sequences processed: {total:,}")
    print(f"  Time:                {elapsed:.1f}s")
    print(f"  Keywords file:       {OUT_KEYWORDS}")
    print(f"    Sequences with keywords: {len(all_keywords):,}")
    print(f"  Formulas file:       {OUT_FORMULAS}")
    print(f"    Total formula lines:     {n_formulas:,}")
    print(f"  Programs file:       {OUT_PROGRAMS}")
    print(f"    Total program lines:     {n_programs:,}")

    print(f"\n  Keyword distribution (top 20):")
    for kw, count in sorted(keyword_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"    {kw:20s} {count:>7,}")

    # Key tags for Prometheus
    nice_count = keyword_counts.get("nice", 0)
    core_count = keyword_counts.get("core", 0)
    total_with_kw = len(all_keywords)
    sleepers = total_with_kw - len([s for s, kws in all_keywords.items()
                                     if "nice" in kws or "core" in kws])
    print(f"\n  Prometheus-relevant:")
    print(f"    'nice' sequences:  {nice_count:,}")
    print(f"    'core' sequences:  {core_count:,}")
    print(f"    Sleeper candidates (have keywords but NOT nice/core): {sleepers:,}")


if __name__ == "__main__":
    main()
