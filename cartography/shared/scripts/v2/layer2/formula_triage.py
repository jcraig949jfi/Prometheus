"""
Formula Triage — Select the formulas worth dissecting.
========================================================
27M formulas × 30 strategies = 810M computations. Don't dissect everything.
Dissect the ones that MATTER: near shadow tensor boundaries, connected to
calibration targets, referenced by open problems.

Builds 4 priority sets:
  A: OEIS-Fungrim bridges (16,774 formulas)
  B: Expected bridge targets (EC, MF, knots, number fields)
  C: Shadow tensor hot spots (high surprise regions)
  D: Erdos problem formulas

Output: formula_triage.jsonl — hashes + priority set membership

Usage:
    python formula_triage.py
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "cartography" / "convergence" / "data"
FORMULAS_FILE = DATA / "openwebmath_formulas.jsonl"
TREES_FILE = DATA / "formula_trees.jsonl"
TRIAGE_FILE = DATA / "formula_triage.jsonl"

# Fungrim bridge concepts (mathematical functions that bridge OEIS and Fungrim)
BRIDGE_FUNCTIONS = {
    "zeta", "Zeta", "gamma", "Gamma", "eta", "Eta",
    "theta", "Theta", "dirichlet", "Dirichlet",
    "bernoulli", "Bernoulli", "euler", "Euler",
    "riemann", "Riemann", "modular", "hecke", "Hecke",
    "eisenstein", "Eisenstein", "dedekind", "Dedekind",
}

# Keywords for expected bridge targets
EC_KEYWORDS = {"elliptic", "weierstrass", "conductor", "rank", "torsion", "discriminant"}
MF_KEYWORDS = {"modular", "form", "hecke", "eigenvalue", "cusp", "weight", "level"}
KNOT_KEYWORDS = {"alexander", "jones", "knot", "braid", "crossing", "polynomial"}
NF_KEYWORDS = {"galois", "field", "extension", "discriminant", "class", "regulator"}
LATTICE_KEYWORDS = {"lattice", "sphere", "packing", "kissing", "leech", "root"}


def load_formula_domains():
    """Load hash -> (domain, operators, latex_snippet) from formulas file."""
    print("  Loading formula metadata...")
    meta = {}
    if not FORMULAS_FILE.exists():
        print(f"    WARNING: {FORMULAS_FILE} not found")
        return meta

    with open(FORMULAS_FILE) as f:
        for i, line in enumerate(f):
            try:
                d = json.loads(line)
                h = d.get("hash", "")
                meta[h] = {
                    "domains": d.get("domains", []),
                    "operators": d.get("operators", []),
                    "latex": d.get("latex", "")[:200],
                    "n_operators": d.get("n_operators", 0),
                }
            except Exception:
                pass
            if (i + 1) % 2000000 == 0:
                print(f"    {(i+1)//1000000}M...")

    print(f"    {len(meta)} formulas loaded")
    return meta


def classify_formula(meta_entry):
    """Classify a formula into priority sets based on its content."""
    sets = set()
    latex = meta_entry.get("latex", "").lower()
    ops = set(meta_entry.get("operators", []))
    domains = meta_entry.get("domains", [])

    # Set A: OEIS-Fungrim bridges (formulas with bridge function operators)
    if ops & BRIDGE_FUNCTIONS or any(bf in latex for bf in BRIDGE_FUNCTIONS):
        sets.add("A")

    # Set B: Expected bridge targets
    all_kw = latex + " " + " ".join(ops)
    if any(kw in all_kw for kw in EC_KEYWORDS):
        sets.add("B_EC")
    if any(kw in all_kw for kw in MF_KEYWORDS):
        sets.add("B_MF")
    if any(kw in all_kw for kw in KNOT_KEYWORDS):
        sets.add("B_knot")
    if any(kw in all_kw for kw in NF_KEYWORDS):
        sets.add("B_NF")
    if any(kw in all_kw for kw in LATTICE_KEYWORDS):
        sets.add("B_lattice")

    # Set C: Complex/interesting formulas (high operator count, multi-domain)
    if meta_entry.get("n_operators", 0) >= 5:
        sets.add("C_complex")
    if len(domains) >= 2 and "unclassified" not in domains:
        sets.add("C_multidomain")

    return sets


def main():
    print("=" * 70)
    print("  FORMULA TRIAGE — Select what's worth dissecting")
    print("=" * 70)

    t0 = time.time()
    meta = load_formula_domains()

    # Load Erdos OEIS refs for Set D
    erdos_file = ROOT / "cartography" / "open_problems" / "data" / "erdos_enriched.jsonl"
    erdos_oeis = set()
    if erdos_file.exists():
        with open(erdos_file) as f:
            for line in f:
                try:
                    d = json.loads(line)
                    for c in d.get("oeis_info", {}).get("oeis_connections", []):
                        erdos_oeis.add(c.get("sequence", "").lower())
                except Exception:
                    pass
    print(f"  Erdos OEIS refs: {len(erdos_oeis)}")

    # Classify all formulas
    print("  Classifying formulas...")
    set_counts = defaultdict(int)
    triaged = []

    for h, m in meta.items():
        sets = classify_formula(m)

        # Set D: check if latex mentions any Erdos OEIS sequence
        latex_lower = m.get("latex", "").lower()
        for seq in erdos_oeis:
            if seq in latex_lower:
                sets.add("D_erdos")
                break

        if sets:
            entry = {
                "hash": h,
                "sets": sorted(sets),
                "n_sets": len(sets),
                "domains": m.get("domains", []),
                "n_operators": m.get("n_operators", 0),
            }
            triaged.append(entry)
            for s in sets:
                set_counts[s] += 1

    # Sort by priority (more sets = higher priority)
    triaged.sort(key=lambda x: -x["n_sets"])

    # Save
    with open(TRIAGE_FILE, "w") as f:
        for t in triaged:
            f.write(json.dumps(t) + "\n")

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  TRIAGE COMPLETE — {elapsed:.1f}s")
    print(f"  Total formulas: {len(meta)}")
    print(f"  Triaged (in any set): {len(triaged)} ({100*len(triaged)/max(len(meta),1):.1f}%)")
    print(f"  Untriaged (skip): {len(meta) - len(triaged)}")
    print(f"\n  Set breakdown:")
    for s, count in sorted(set_counts.items(), key=lambda x: -x[1]):
        print(f"    {s:20s} {count:>8,}")
    print(f"\n  Multi-set formulas (highest priority):")
    multi = [t for t in triaged if t["n_sets"] >= 3]
    print(f"    {len(multi)} formulas in 3+ sets")
    for t in multi[:10]:
        print(f"      {t['hash']} sets={t['sets']}")
    print(f"\n  Output: {TRIAGE_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
