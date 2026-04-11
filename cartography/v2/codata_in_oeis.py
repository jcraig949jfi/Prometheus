#!/usr/bin/env python3
"""
CODATA Physical Constants in OEIS Sequences
============================================
Do dimensionless physical constants appear as terms in OEIS sequences?

Strategy:
1. Load 286 CODATA constants; identify ~93 dimensionless ones (no unit field).
2. For each, extract first 8 significant digits as an integer.
3. Search OEIS stripped data for sequences containing that integer as a term.
4. Also test well-known integer parts and ratios.
5. Control: 286 random 8-digit numbers, same search. Compare hit rates.
"""

import json
import re
import random
import math
import time
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
CODATA_PATH = ROOT / "physics" / "data" / "codata" / "constants.json"
OEIS_PATH = ROOT / "oeis" / "data" / "stripped_new.txt"
OUTPUT_PATH = Path(__file__).resolve().parent / "codata_in_oeis_results.json"

# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_significant_digits(value, n=8):
    """Extract first n significant digits from a float, return as integer."""
    if value == 0:
        return None
    v = abs(value)
    # Normalize to [1, 10^n)
    exp = math.floor(math.log10(v))
    shifted = v / (10 ** (exp - n + 1))
    return int(round(shifted))


def load_oeis_terms(path):
    """Load OEIS stripped file into a dict: term -> set of sequence IDs."""
    print(f"Loading OEIS data from {path}...")
    t0 = time.time()
    term_to_seqs = defaultdict(set)
    seq_count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            # Format: A000001 ,1,2,3,...,
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            terms_str = parts[1].strip().strip(",")
            seq_count += 1
            for t in terms_str.split(","):
                t = t.strip().lstrip("+-")
                if t and t.isdigit():
                    val = int(t)
                    # Only index terms in a reasonable range (skip huge numbers)
                    if 10_000_000 <= val <= 99_999_999:
                        term_to_seqs[val].add(seq_id)
    elapsed = time.time() - t0
    print(f"  Indexed {len(term_to_seqs):,} unique 8-digit terms from {seq_count:,} sequences in {elapsed:.1f}s")
    return term_to_seqs


def load_oeis_terms_flexible(path, targets):
    """Search OEIS for arbitrary integer targets (any size). Returns target -> set of seq IDs."""
    print(f"Searching OEIS for {len(targets)} specific integer targets...")
    t0 = time.time()
    target_set = set(targets)
    # Convert to strings for fast matching
    target_strs = {str(t): t for t in target_set}
    results = defaultdict(set)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            terms_str = parts[1].strip().strip(",")
            for t in terms_str.split(","):
                t = t.strip()
                # Handle negative terms
                t_abs = t.lstrip("+-")
                if t_abs in target_strs:
                    results[target_strs[t_abs]].add(seq_id)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s, found hits for {len(results)} targets")
    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Load CODATA
    with open(CODATA_PATH, "r", encoding="utf-8") as f:
        constants = json.load(f)
    print(f"Loaded {len(constants)} CODATA constants")

    dimensionless = [c for c in constants if "unit" not in c]
    with_units = [c for c in constants if "unit" in c]
    print(f"  Dimensionless: {len(dimensionless)}")
    print(f"  With units: {len(with_units)}")

    # ── Phase 1: 8 significant digits of dimensionless constants ─────────
    print("\n=== Phase 1: 8-digit signatures of dimensionless constants ===")

    digit_map = {}  # 8-digit int -> list of constant names
    for c in dimensionless:
        v = c["value"]
        sig = extract_significant_digits(v, 8)
        if sig is not None and 10_000_000 <= sig <= 99_999_999:
            if sig not in digit_map:
                digit_map[sig] = []
            digit_map[sig].append(c["name"])

    print(f"  Unique 8-digit signatures: {len(digit_map)}")

    # Load OEIS index (8-digit terms only)
    oeis_8digit = load_oeis_terms(OEIS_PATH)

    # Search
    phase1_hits = {}
    for sig, names in digit_map.items():
        if sig in oeis_8digit:
            seqs = sorted(oeis_8digit[sig])
            phase1_hits[sig] = {"constants": names, "sequences": seqs, "count": len(seqs)}
            for name in names:
                print(f"  HIT: {name} -> {sig} found in {len(seqs)} sequences: {seqs[:5]}")

    print(f"\n  Phase 1 results: {len(phase1_hits)} hits out of {len(digit_map)} searched")

    # ── Phase 2: Well-known integer values and ratios ────────────────────
    print("\n=== Phase 2: Well-known integer parts and ratios ===")

    special_targets = {}
    # Integer parts of mass ratios, coupling constants, etc.
    for c in dimensionless:
        v = c["value"]
        int_part = int(abs(v))
        if int_part >= 2:  # Skip 0 and 1 (trivially common)
            special_targets[int_part] = special_targets.get(int_part, [])
            special_targets[int_part].append(f"{c['name']} (int part = {int_part})")

    # Key derived ratios
    key_ratios = {
        137: "1/alpha (fine structure constant inverse, ~137.036)",
        1836: "proton/electron mass ratio (integer part)",
        2127: "1/(electron g-factor anomaly) ~ 1/0.00116 ~ 862 [corrected]",
        207: "muon/electron mass ratio (integer part)",
        1777: "tau mass in MeV (integer part)",
        938: "proton mass in MeV (integer part)",
        106: "muon mass in MeV (integer part)",
        274: "proton/muon mass ratio * 30 ... skip, just proton-muon ratio int = 8",
    }
    # Recompute some from data
    proton_electron = None
    for c in constants:
        if c["name"] == "proton-electron mass ratio":
            proton_electron = c["value"]
        if c["name"] == "fine-structure constant":
            alpha = c["value"]

    if alpha:
        inv_alpha = int(1.0 / alpha)  # 137
        key_ratios[inv_alpha] = f"1/alpha = {1.0/alpha:.6f} -> int part {inv_alpha}"
    if proton_electron:
        key_ratios[int(proton_electron)] = f"proton/electron mass ratio = {proton_electron:.3f} -> int part {int(proton_electron)}"

    # Clean up key_ratios: only keep reasonable ones
    clean_ratios = {k: v for k, v in key_ratios.items() if 2 <= k <= 99_999_999}

    all_special = set()
    for k in special_targets:
        if 2 <= k <= 99_999_999:
            all_special.add(k)
    for k in clean_ratios:
        all_special.add(k)

    print(f"  Special integer targets: {len(all_special)}")

    # Search for these
    special_results = load_oeis_terms_flexible(OEIS_PATH, all_special)

    phase2_hits = {}
    for target, seqs in sorted(special_results.items(), key=lambda x: -len(x[1])):
        sources = []
        if target in special_targets:
            sources.extend(special_targets[target])
        if target in clean_ratios:
            sources.append(clean_ratios[target])
        # Small integers appear in many sequences - only report if < 50 hits or notable
        if len(seqs) <= 200 or target in clean_ratios:
            phase2_hits[target] = {
                "sources": sources,
                "sequence_count": len(seqs),
                "sample_sequences": sorted(seqs)[:10],
            }
            if target in clean_ratios or len(seqs) <= 20:
                print(f"  {target}: {len(seqs)} sequences — {sources[0] if sources else '?'}")

    # ── Phase 3: Control — random 8-digit numbers ───────────────────────
    print("\n=== Phase 3: Random control (286 random 8-digit numbers) ===")
    random.seed(42)
    random_targets = [random.randint(10_000_000, 99_999_999) for _ in range(286)]

    control_hits = 0
    control_details = []
    for rt in random_targets:
        if rt in oeis_8digit:
            control_hits += 1
            control_details.append({"number": rt, "sequences": sorted(oeis_8digit[rt])[:5], "count": len(oeis_8digit[rt])})

    print(f"  Control hits: {control_hits} / 286 = {control_hits/286*100:.1f}%")
    print(f"  CODATA 8-digit hits: {len(phase1_hits)} / {len(digit_map)} = {len(phase1_hits)/max(len(digit_map),1)*100:.1f}%")

    # ── Phase 4: Also search digit signatures for ALL constants (with units) ──
    print("\n=== Phase 4: All constants (including with units) — 8-digit signatures ===")
    all_digit_map = {}
    for c in constants:
        v = c["value"]
        sig = extract_significant_digits(v, 8)
        if sig is not None and 10_000_000 <= sig <= 99_999_999:
            if sig not in all_digit_map:
                all_digit_map[sig] = []
            all_digit_map[sig].append(c["name"])

    phase4_hits = {}
    for sig, names in all_digit_map.items():
        if sig in oeis_8digit:
            seqs = sorted(oeis_8digit[sig])
            phase4_hits[sig] = {"constants": names, "sequences": seqs[:10], "count": len(seqs)}
            print(f"  HIT: {names[0][:50]:50s} -> {sig} in {len(seqs)} seqs: {seqs[:3]}")

    print(f"\n  All-constants 8-digit hits: {len(phase4_hits)} / {len(all_digit_map)} = {len(phase4_hits)/max(len(all_digit_map),1)*100:.1f}%")

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Dimensionless 8-digit hits: {len(phase1_hits)} / {len(digit_map)} ({len(phase1_hits)/max(len(digit_map),1)*100:.1f}%)")
    print(f"All constants 8-digit hits:  {len(phase4_hits)} / {len(all_digit_map)} ({len(phase4_hits)/max(len(all_digit_map),1)*100:.1f}%)")
    print(f"Random control 8-digit hits: {control_hits} / 286 ({control_hits/286*100:.1f}%)")
    print(f"OEIS 8-digit term coverage:  {len(oeis_8digit):,} unique values indexed")

    # Estimate: how many 8-digit integers exist in OEIS?
    total_8digit = 90_000_000  # 10M to 99M
    coverage_pct = len(oeis_8digit) / total_8digit * 100
    print(f"OEIS covers {coverage_pct:.2f}% of all 8-digit integers")
    print(f"Expected random hit rate: ~{coverage_pct:.2f}%")

    # ── Save results ─────────────────────────────────────────────────────
    results = {
        "metadata": {
            "total_constants": len(constants),
            "dimensionless_constants": len(dimensionless),
            "with_units_constants": len(with_units),
            "oeis_sequences_searched": "~394K",
            "oeis_8digit_terms_indexed": len(oeis_8digit),
            "total_8digit_space": total_8digit,
            "oeis_coverage_pct": round(coverage_pct, 4),
        },
        "phase1_dimensionless_8digit": {
            "searched": len(digit_map),
            "hits": len(phase1_hits),
            "hit_rate_pct": round(len(phase1_hits) / max(len(digit_map), 1) * 100, 2),
            "details": {str(k): v for k, v in phase1_hits.items()},
        },
        "phase2_integer_parts": {
            "searched": len(all_special),
            "hits_reported": len(phase2_hits),
            "notable": {str(k): v for k, v in phase2_hits.items() if v["sequence_count"] <= 50 or k in clean_ratios},
        },
        "phase3_control": {
            "searched": 286,
            "hits": control_hits,
            "hit_rate_pct": round(control_hits / 286 * 100, 2),
            "details": control_details[:20],
        },
        "phase4_all_constants_8digit": {
            "searched": len(all_digit_map),
            "hits": len(phase4_hits),
            "hit_rate_pct": round(len(phase4_hits) / max(len(all_digit_map), 1) * 100, 2),
            "details": {str(k): v for k, v in phase4_hits.items()},
        },
        "conclusion": "",  # filled below
    }

    # Build conclusion
    if len(phase1_hits) == 0 and control_hits == 0:
        conclusion = (
            "Neither CODATA dimensionless constants nor random 8-digit numbers appear as OEIS terms. "
            f"OEIS covers only {coverage_pct:.2f}% of 8-digit integer space, so null result is expected. "
            "Physical constants do NOT have a privileged presence in integer sequences."
        )
    elif len(phase1_hits) <= control_hits:
        conclusion = (
            f"CODATA hit rate ({len(phase1_hits)}/{len(digit_map)}) is at or below random baseline "
            f"({control_hits}/286). No evidence that physical constants appear preferentially in OEIS."
        )
    else:
        conclusion = (
            f"CODATA hit rate ({len(phase1_hits)}/{len(digit_map)} = {len(phase1_hits)/max(len(digit_map),1)*100:.1f}%) "
            f"exceeds random baseline ({control_hits}/286 = {control_hits/286*100:.1f}%). "
            "Investigate whether matches are coincidental or meaningful."
        )

    results["conclusion"] = conclusion
    print(f"\nCONCLUSION: {conclusion}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
