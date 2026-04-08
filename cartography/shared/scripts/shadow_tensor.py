"""
Shadow Tensor — The Dark Matter Map.
======================================
Every hypothesis tested, every battery failure, every near-miss — recorded
in a cell grid indexed by dataset pair. The shadow tensor doesn't track
what we found. It tracks WHERE WE LOOKED, HOW HARD, and HOW IT DIED.

The theory: failure patterns contain information that success patterns don't.
A ring of cells that barely fail (p=0.06) around a void is a gravitational
signature — something is there, pulling the statistics, but we can't see it
directly. A cluster of F13 kills (growth rate) with F14 passes (phase decay)
means the structure is real but masked by polynomial growth.

Cell structure (per dataset pair):
  - n_tested: how many hypotheses tested in this cell
  - n_passed: how many survived battery
  - n_killed: how many the battery murdered
  - kill_profile: {F1: count, F2: count, ...F14: count} — HOW they died
  - p_distribution: list of p-values from F1 (permutation) — the raw signal
  - z_distribution: list of z-scores — effect sizes even on failures
  - effect_sizes: list of Cohen's d values
  - best_p: lowest p-value ever seen (the "closest miss")
  - best_z: highest z-score ever seen
  - verb_bridges: shared verb concepts
  - noun_bridges: shared noun concepts
  - bond_dim: tensor bond dimension (from SVD)
  - top_sv: top singular value
  - exploration_depth: n_tested / possible_hypotheses — how thoroughly searched
  - last_explored: timestamp
  - hypothesis_types: {type: count} — what kinds of hypotheses were tried

The shadow tensor is rebuilt from:
  1. Research memory (17K hypotheses with verdicts)
  2. Bridge hunter results
  3. Genocide results
  4. Void scanner results
  5. Tensor bridge data

Usage:
    python shadow_tensor.py              # build from all sources
    python shadow_tensor.py --show-hot   # show cells with gravitational signatures
    python shadow_tensor.py --show-cold  # show unexplored cells
"""

import json
import math
import re
import sys
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
DATA = CONVERGENCE / "data"

# Input sources
MEMORY_FILE = DATA / "research_memory.jsonl"
HUNTER_RESULTS = DATA / "bridge_hunter_results.jsonl"
VOID_RESULTS = DATA / "void_scanner_results.jsonl"
TENSOR_FILE = DATA / "tensor_bridges.json"
LINKS_FILE = DATA / "concept_links.jsonl"
BRIDGES_FILE = DATA / "bridges.jsonl"

# Genocide results
GENOCIDE_FILES = [
    DATA / f"genocide_r{i}_results.json" for i in range(1, 8)
]

# Output
SHADOW_FILE = DATA / "shadow_tensor.json"


def empty_cell():
    """A fresh unexplored cell."""
    return {
        "n_tested": 0,
        "n_passed": 0,
        "n_killed": 0,
        "n_open": 0,
        "kill_profile": defaultdict(int),  # F-test → kill count
        "p_values": [],          # raw p-values from F1
        "z_scores": [],          # z-scores from tests
        "effect_sizes": [],      # Cohen's d values
        "best_p": 1.0,
        "best_z": 0.0,
        "best_d": 0.0,
        "verb_bridges": [],
        "noun_bridges": [],
        "bond_dim": 0,
        "top_sv": 0.0,
        "hypothesis_types": defaultdict(int),
        "kill_reasons": defaultdict(int),  # kill category → count
        "last_explored": None,
        "sample_hypotheses": [],  # up to 5 representative hypotheses
        "sample_kills": [],       # up to 5 kill diagnoses
    }


def normalize_dataset_name(text):
    """Map hypothesis text mentions to canonical dataset names."""
    mappings = {
        "oeis": "OEIS", "lmfdb": "LMFDB", "knot": "KnotInfo",
        "fungrim": "Fungrim", "antedb": "ANTEDB", "mathlib": "mathlib",
        "metamath": "Metamath", "materials": "Materials", "number field": "NumberFields",
        "isogen": "Isogenies", "local field": "LocalFields", "space group": "SpaceGroups",
        "polytop": "Polytopes", "pi-base": "piBase", "mmlkg": "MMLKG",
        "genus-2": "Genus2", "genus2": "Genus2", "maass": "Maass",
        "lattice": "Lattices", "findstat": "FindStat", "openalex": "OpenAlex",
    }
    text_lower = text.lower()
    found = []
    for keyword, canonical in mappings.items():
        if keyword in text_lower:
            found.append(canonical)
    return found


def pair_key(d1, d2):
    """Canonical pair key (alphabetical order)."""
    return "--".join(sorted([d1, d2]))


def ingest_research_memory(cells):
    """Ingest 17K hypotheses from research memory."""
    if not MEMORY_FILE.exists():
        return 0
    count = 0
    with open(MEMORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                h = json.loads(line)
            except:
                continue

            hyp_text = h.get("hypothesis", "")
            status = h.get("status", "open")
            datasets = normalize_dataset_name(hyp_text)

            if len(datasets) < 2:
                continue

            # Use first two mentioned datasets as the cell
            pk = pair_key(datasets[0], datasets[1])
            cell = cells[pk]

            cell["n_tested"] += 1
            if status == "falsified":
                cell["n_killed"] += 1
            elif status == "open":
                cell["n_open"] += 1
            else:
                cell["n_passed"] += 1

            ts = h.get("last_seen")
            if ts and (cell["last_explored"] is None or ts > cell["last_explored"]):
                cell["last_explored"] = ts

            if len(cell["sample_hypotheses"]) < 5:
                cell["sample_hypotheses"].append(hyp_text[:200])

            count += 1
    return count


def ingest_hunter_results(cells):
    """Ingest bridge hunter test results with battery details."""
    if not HUNTER_RESULTS.exists():
        return 0
    count = 0
    with open(HUNTER_RESULTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except:
                continue

            hyp = r.get("hypothesis", {})
            result = r.get("test_result", {})
            d1 = hyp.get("d1", "")
            d2 = hyp.get("d2", "")
            if not d1 or not d2:
                continue

            pk = pair_key(d1, d2)
            cell = cells[pk]

            verdict = result.get("verdict", "SKIP")
            if verdict == "PASS":
                cell["n_passed"] += 1
            elif verdict == "FAIL":
                cell["n_killed"] += 1

            # Record p-value and z-score if available
            p = result.get("p")
            if p is not None:
                cell["p_values"].append(float(p))
                if float(p) < cell["best_p"]:
                    cell["best_p"] = float(p)

            z = result.get("z")
            if z is not None:
                cell["z_scores"].append(float(z))
                if abs(float(z)) > abs(cell["best_z"]):
                    cell["best_z"] = float(z)

            cell["hypothesis_types"][hyp.get("type", "unknown")] += 1
            cell["n_tested"] += 1

            ts = r.get("timestamp")
            if ts and (cell["last_explored"] is None or ts > cell["last_explored"]):
                cell["last_explored"] = ts

            count += 1
    return count


def ingest_genocide_results(cells):
    """Ingest genocide round results."""
    count = 0
    for gf in GENOCIDE_FILES:
        if not gf.exists():
            continue
        try:
            data = json.loads(gf.read_text(encoding="utf-8"))
        except:
            continue

        tests = data if isinstance(data, list) else data.get("tests", [])
        for t in tests:
            hyp_text = t.get("hypothesis", t.get("name", ""))
            datasets = normalize_dataset_name(hyp_text)
            if len(datasets) < 2:
                continue

            pk = pair_key(datasets[0], datasets[1])
            cell = cells[pk]

            verdict = t.get("verdict", t.get("tag", ""))
            if "KILL" in verdict.upper() or "SAVAGE" in verdict.upper():
                cell["n_killed"] += 1
            elif "PASS" in verdict.upper() or "SURVIV" in verdict.upper() or "VALIDAT" in verdict.upper():
                cell["n_passed"] += 1

            p = t.get("p", t.get("p_value"))
            if p is not None:
                cell["p_values"].append(float(p))
                if float(p) < cell["best_p"]:
                    cell["best_p"] = float(p)

            z = t.get("z", t.get("z_score"))
            if z is not None:
                cell["z_scores"].append(float(z))
                if abs(float(z)) > abs(cell["best_z"]):
                    cell["best_z"] = float(z)

            cell["n_tested"] += 1
            count += 1
    return count


def ingest_void_scan(cells):
    """Ingest void scanner concept/numerical bridge data."""
    if not VOID_RESULTS.exists():
        return 0
    count = 0
    with open(VOID_RESULTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except:
                continue

            pk = r.get("pair", "")
            if "--" not in pk:
                continue

            cell = cells[pk]

            overlap = r.get("concept_overlap")
            if overlap:
                cell["verb_bridges"] = overlap.get("verb_bridges", [])
                cell["noun_bridges"] = overlap.get("noun_bridges", [])

            num = r.get("numerical_bridge")
            if num:
                cell["numerical_jaccard"] = num.get("jaccard", 0)

            cell["bond_dim"] = r.get("bond_dim", 0)
            cell["top_sv"] = r.get("top_sv", 0)
            count += 1
    return count


def ingest_tensor_bonds(cells):
    """Overlay SVD bond dimensions from tensor bridge analysis."""
    if not TENSOR_FILE.exists():
        return 0
    tensor = json.loads(TENSOR_FILE.read_text(encoding="utf-8"))
    count = 0
    for pk, data in tensor.get("svd_bond_dimensions", {}).items():
        cell = cells[pk]
        cell["bond_dim"] = data.get("bond_dim", 0)
        svs = data.get("top_singular_values", [])
        cell["top_sv"] = svs[0] if svs else 0
        count += 1
    return count


def compute_signatures(cells):
    """Compute derived metrics: gravitational signatures, anomaly scores."""
    for pk, cell in cells.items():
        n = cell["n_tested"]
        if n == 0:
            cell["exploration_depth"] = 0
            cell["kill_rate"] = None
            cell["anomaly_score"] = 0
            continue

        cell["exploration_depth"] = n
        cell["kill_rate"] = cell["n_killed"] / n if n > 0 else 0

        # Gravitational signature: high near-miss rate
        # If many hypotheses ALMOST pass (p in 0.01-0.10), something is pulling
        near_misses = [p for p in cell["p_values"] if 0.01 < p < 0.10]
        cell["near_miss_count"] = len(near_misses)
        cell["near_miss_rate"] = len(near_misses) / n if n > 0 else 0

        # Anomaly score: combines multiple signals
        #  - High near-miss rate (something is there)
        #  - Low best_p (closest we got)
        #  - Non-zero verb bridges (structural connection exists)
        #  - Moderate exploration depth (we've looked, not just 1 test)
        score = 0.0

        # Near-miss gravity
        if cell["near_miss_rate"] > 0.1 and n >= 5:
            score += cell["near_miss_rate"] * 30

        # Best p gravity (log scale, lower = stronger pull)
        if cell["best_p"] < 0.5 and cell["best_p"] > 0:
            score += max(0, -math.log10(cell["best_p"])) * 5

        # Best z gravity
        if abs(cell["best_z"]) > 1.5:
            score += abs(cell["best_z"]) * 2

        # Verb bridge bonus (structural connection the tensor can't see)
        score += len(cell.get("verb_bridges", [])) * 10

        # Exploration bonus (well-explored cells with anomalies are more reliable)
        if n >= 10:
            score *= 1.5
        elif n >= 5:
            score *= 1.2

        # Bond dimension penalty (if tensor already sees it, less interesting)
        if cell["bond_dim"] > 2:
            score *= 0.5

        cell["anomaly_score"] = round(score, 2)

    # Convert defaultdicts for JSON serialization
    for pk, cell in cells.items():
        cell["kill_profile"] = dict(cell["kill_profile"])
        cell["hypothesis_types"] = dict(cell["hypothesis_types"])
        cell["kill_reasons"] = dict(cell["kill_reasons"])


def build_shadow_tensor():
    """Build the complete shadow tensor from all sources."""
    print("=" * 70)
    print("  SHADOW TENSOR — Building the Dark Matter Map")
    print("  Every failure is data. Every near-miss is gravity.")
    print("=" * 70)

    t0 = time.time()
    cells = defaultdict(empty_cell)

    # Ingest all sources
    print("\n  Ingesting sources...")
    n = ingest_research_memory(cells)
    print(f"    Research memory: {n} hypothesis-pair records")

    n = ingest_hunter_results(cells)
    print(f"    Bridge hunter: {n} test records")

    n = ingest_genocide_results(cells)
    print(f"    Genocide rounds: {n} test records")

    n = ingest_void_scan(cells)
    print(f"    Void scan: {n} pair records")

    n = ingest_tensor_bonds(cells)
    print(f"    Tensor bonds: {n} pair records")

    # Compute derived metrics
    print("\n  Computing signatures...")
    compute_signatures(cells)

    # Get all known datasets
    all_datasets = set()
    for pk in cells:
        parts = pk.split("--")
        all_datasets.update(parts)

    # Ensure all possible pairs have cells (even unexplored ones)
    for d1, d2 in combinations(sorted(all_datasets), 2):
        pk = pair_key(d1, d2)
        if pk not in cells:
            cells[pk] = empty_cell()
            cells[pk]["exploration_depth"] = 0
            cells[pk]["anomaly_score"] = 0
            cells[pk]["kill_rate"] = None

    # Summary stats
    n_cells = len(cells)
    n_explored = sum(1 for c in cells.values() if c["n_tested"] > 0)
    n_unexplored = n_cells - n_explored
    n_hot = sum(1 for c in cells.values() if c.get("anomaly_score", 0) > 20)
    total_tests = sum(c["n_tested"] for c in cells.values())
    total_kills = sum(c["n_killed"] for c in cells.values())
    total_passes = sum(c["n_passed"] for c in cells.values())

    # Save
    output = {
        "meta": {
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_cells": n_cells,
            "n_explored": n_explored,
            "n_unexplored": n_unexplored,
            "n_hot_cells": n_hot,
            "total_tests": total_tests,
            "total_kills": total_kills,
            "total_passes": total_passes,
            "datasets": sorted(all_datasets),
        },
        "cells": {pk: cell for pk, cell in sorted(cells.items())},
    }

    with open(SHADOW_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    elapsed = time.time() - t0

    print(f"\n  Shadow tensor built in {elapsed:.1f}s")
    print(f"  Cells: {n_cells} ({n_explored} explored, {n_unexplored} unexplored)")
    print(f"  Total tests: {total_tests} ({total_kills} killed, {total_passes} passed)")
    print(f"  Hot cells (anomaly > 20): {n_hot}")
    print(f"  Saved to {SHADOW_FILE}")

    return output


def show_hot_cells(shadow=None):
    """Display cells with gravitational signatures — something is pulling."""
    if shadow is None:
        shadow = json.loads(SHADOW_FILE.read_text(encoding="utf-8"))

    cells = shadow["cells"]
    hot = [(pk, c) for pk, c in cells.items() if c.get("anomaly_score", 0) > 0]
    hot.sort(key=lambda x: -x[1]["anomaly_score"])

    print(f"\n  HOT CELLS — Gravitational Signatures (anomaly > 0)")
    print(f"  {'Pair':40s} score  tested  killed  best_p  best_z  verbs  bd  near_miss")
    print(f"  {'-'*120}")

    for pk, c in hot[:30]:
        print(f"  {pk:40s} {c['anomaly_score']:5.1f}  "
              f"{c['n_tested']:6d}  {c['n_killed']:6d}  "
              f"{c['best_p']:6.4f}  {c['best_z']:6.1f}  "
              f"{len(c.get('verb_bridges',[])):5d}  "
              f"{c.get('bond_dim',0):2d}  "
              f"{c.get('near_miss_count',0):3d}")


def show_cold_cells(shadow=None):
    """Display unexplored or under-explored cells."""
    if shadow is None:
        shadow = json.loads(SHADOW_FILE.read_text(encoding="utf-8"))

    cells = shadow["cells"]
    cold = [(pk, c) for pk, c in cells.items() if c["n_tested"] < 3]
    cold.sort(key=lambda x: x[1]["n_tested"])

    print(f"\n  COLD CELLS — Unexplored Territory ({len(cold)} cells)")
    print(f"  {'Pair':40s} tested  verbs  bd  sv")
    print(f"  {'-'*80}")

    for pk, c in cold[:30]:
        print(f"  {pk:40s} {c['n_tested']:6d}  "
              f"{len(c.get('verb_bridges',[])):5d}  "
              f"{c.get('bond_dim',0):2d}  "
              f"{c.get('top_sv',0):8.1f}")


def show_kill_signatures(shadow=None):
    """Analyze kill patterns across cells — what failure modes cluster together?"""
    if shadow is None:
        shadow = json.loads(SHADOW_FILE.read_text(encoding="utf-8"))

    cells = shadow["cells"]
    explored = {pk: c for pk, c in cells.items() if c["n_tested"] >= 5}

    print(f"\n  KILL SIGNATURES — How Things Die ({len(explored)} well-explored cells)")

    # Group by dominant kill mode
    # For cells with p_values, categorize the failure pattern
    patterns = defaultdict(list)
    for pk, c in explored.items():
        if not c["p_values"]:
            continue

        p_arr = c["p_values"]
        median_p = sorted(p_arr)[len(p_arr) // 2]

        if median_p < 0.01:
            pattern = "strong_signal"
        elif median_p < 0.05:
            pattern = "borderline"
        elif median_p < 0.10:
            pattern = "near_miss"
        elif c["kill_rate"] and c["kill_rate"] > 0.8:
            pattern = "hard_kill"
        else:
            pattern = "mixed"

        patterns[pattern].append((pk, c))

    for pattern, pairs in sorted(patterns.items()):
        print(f"\n  --- {pattern.upper()} ({len(pairs)} cells) ---")
        for pk, c in sorted(pairs, key=lambda x: -x[1].get("anomaly_score", 0))[:5]:
            print(f"    {pk:40s} anomaly={c['anomaly_score']:5.1f} "
                  f"best_p={c['best_p']:.4f} n={c['n_tested']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Shadow Tensor - Dark Matter Map")
    parser.add_argument("--show-hot", action="store_true", help="Show hot cells")
    parser.add_argument("--show-cold", action="store_true", help="Show unexplored cells")
    parser.add_argument("--show-kills", action="store_true", help="Show kill pattern analysis")
    args = parser.parse_args()

    shadow = build_shadow_tensor()

    if args.show_hot:
        show_hot_cells(shadow)
    if args.show_cold:
        show_cold_cells(shadow)
    if args.show_kills:
        show_kill_signatures(shadow)

    if not any([args.show_hot, args.show_cold, args.show_kills]):
        show_hot_cells(shadow)
        show_cold_cells(shadow)
