#!/usr/bin/env python3
"""
Extract the full OEIS cross-reference graph from oeisdata .seq files.

Scans all A### directories, extracts:
  - Cross-reference edges (source -> target A-numbers) from %C, %F, %Y, %o lines
  - Sequence names from %N lines

Outputs:
  - data/oeis_crossrefs.jsonl  — one JSON line per directed edge
  - data/oeis_names.json       — {A-number: name} dict

Optimized for 664K files: pre-compiled regex, os.scandir, buffered writes.
"""

import json
import os
import re
import time
from collections import Counter
from pathlib import Path

# Config
SEQ_ROOT = Path(r"F:\Prometheus\charon\james_downloads\oeisdata\seq")
OUT_DIR = Path(r"F:\Prometheus\cartography\oeis\data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Pre-compile patterns
RE_ANUM = re.compile(r'A\d{6}')
# Lines that carry cross-references: %C (comments), %F (formulas), %Y (xrefs), %o (programs)
RE_XREF_LINE = re.compile(r'^%(C|F|Y|o) ')
RE_NAME_LINE = re.compile(r'^%N ')
# Extract sequence ID from filename
RE_SEQ_ID = re.compile(r'^(A\d{6})\.seq$')


def extract_from_file(filepath: str, filename: str):
    """Parse one .seq file. Returns (seq_id, name, set_of_target_anums)."""
    m = RE_SEQ_ID.match(filename)
    if not m:
        return None, None, None
    seq_id = m.group(1)

    name = None
    targets = set()

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if RE_NAME_LINE.match(line):
                    # %N A000040 The prime numbers.
                    # Strip the "%N A###### " prefix
                    parts = line.split(None, 2)
                    if len(parts) >= 3:
                        name = parts[2].rstrip('\n').strip()
                elif RE_XREF_LINE.match(line):
                    for ref in RE_ANUM.findall(line):
                        if ref != seq_id:
                            targets.add(ref)
    except Exception:
        return seq_id, name, targets

    return seq_id, name, targets


def main():
    t0 = time.time()
    print(f"Scanning {SEQ_ROOT} ...")

    # Collect all subdirectories (A000 .. A394)
    subdirs = []
    for entry in os.scandir(SEQ_ROOT):
        if entry.is_dir() and entry.name.startswith('A'):
            subdirs.append(entry.path)
    subdirs.sort()
    print(f"Found {len(subdirs)} subdirectories")

    names = {}
    total_files = 0
    total_edges = 0
    hub_counter = Counter()  # count outgoing edges per source

    crossrefs_path = OUT_DIR / "oeis_crossrefs.jsonl"
    names_path = OUT_DIR / "oeis_names.json"

    # Buffered JSONL write
    BUFFER_SIZE = 10000
    buffer = []

    with open(crossrefs_path, 'w', encoding='utf-8') as fout:
        for subdir in subdirs:
            for entry in os.scandir(subdir):
                if not entry.name.endswith('.seq') or not entry.is_file():
                    continue

                seq_id, name, targets = extract_from_file(entry.path, entry.name)
                if seq_id is None:
                    continue

                total_files += 1

                if name:
                    names[seq_id] = name

                if targets:
                    n_edges = len(targets)
                    total_edges += n_edges
                    hub_counter[seq_id] = n_edges

                    for t in targets:
                        buffer.append(f'{{"source":"{seq_id}","target":"{t}"}}\n')

                    if len(buffer) >= BUFFER_SIZE:
                        fout.writelines(buffer)
                        buffer.clear()

                if total_files % 50000 == 0:
                    elapsed = time.time() - t0
                    print(f"  {total_files:>7,} files | {total_edges:>10,} edges | {elapsed:.1f}s")

        # Flush remaining buffer
        if buffer:
            fout.writelines(buffer)
            buffer.clear()

    # Write names
    print(f"Writing {len(names):,} sequence names to {names_path} ...")
    with open(names_path, 'w', encoding='utf-8') as f:
        json.dump(names, f, ensure_ascii=False, indent=None, separators=(',', ':'))

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'='*60}")
    print(f"OEIS Cross-Reference Graph Extraction Complete")
    print(f"{'='*60}")
    print(f"Total .seq files processed : {total_files:>10,}")
    print(f"Total directed edges       : {total_edges:>10,}")
    print(f"Sequences with names       : {len(names):>10,}")
    print(f"Time elapsed               : {elapsed:>10.1f}s")
    print(f"\nOutputs:")
    print(f"  Edges : {crossrefs_path}")
    print(f"  Names : {names_path}")

    # Top 20 hub sequences (by outgoing cross-references)
    print(f"\nTop 20 hub sequences (by outgoing cross-ref count):")
    print(f"  {'Rank':>4}  {'A-number':<10}  {'Out-edges':>10}  Name")
    print(f"  {'----':>4}  {'--------':<10}  {'---------':>10}  ----")
    for rank, (seq_id, count) in enumerate(hub_counter.most_common(20), 1):
        sname = names.get(seq_id, '(no name)')
        if len(sname) > 60:
            sname = sname[:57] + '...'
        print(f"  {rank:>4}  {seq_id:<10}  {count:>10,}  {sname}")


if __name__ == '__main__':
    main()
