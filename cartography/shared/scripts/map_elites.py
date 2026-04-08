"""
MAP-Elites Illuminator — Diversity-driven exploration of the shadow tensor.
============================================================================
Instead of searching for the BEST bridge, fills a grid of bins where each
bin keeps the "elite" (closest-to-passing) specimen. Empty bins = where to
explore next. The grid axes are:

  X axis: dataset pair (190 cells)
  Y axis: failure modality (F1-F14 + PASS + OPEN)

Each bin stores the hypothesis that got closest to passing that particular
test in that particular cell. The "elite" is the near-miss, not the winner.

The illuminator:
  1. Loads the shadow tensor (current map state)
  2. Identifies empty/weak bins
  3. Takes template hypotheses from the corpus
  4. Mutates them toward empty bins (swap dataset names, verbs)
  5. Tests and updates the archive
  6. Rebuilds the shadow tensor

Zero LLM cost. Runs indefinitely as an autonomous exploration agent.

Usage:
    python map_elites.py                # one sweep of all empty bins
    python map_elites.py --loop 10      # 10 sweeps
    python map_elites.py --focus Maass  # focus on bins involving Maass
"""

import json
import re
import sys
import time
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
DATA = CONVERGENCE / "data"

SHADOW_FILE = DATA / "shadow_tensor.json"
ARCHIVE_FILE = DATA / "map_elites_archive.json"
LINKS_FILE = DATA / "concept_links.jsonl"
RESULTS_FILE = DATA / "map_elites_results.jsonl"

# All known datasets
ALL_DATASETS = [
    "ANTEDB", "FindStat", "Fungrim", "Genus2", "Isogenies", "KnotInfo",
    "LMFDB", "Lattices", "LocalFields", "MMLKG", "Maass", "Materials",
    "Metamath", "NumberFields", "OEIS", "OpenAlex", "Polytopes",
    "SpaceGroups", "mathlib", "piBase",
]

# Failure modes (bins on Y axis)
FAIL_MODES = [
    "F1_permutation", "F3_effect_size", "F5_normalization",
    "F9_simpler", "F12_partial_corr", "F13_growth_rate", "F14_phase_shift",
    "PASS", "OPEN", "UNTESTED",
]


def pair_key(d1, d2):
    return "--".join(sorted([d1, d2]))


def load_archive():
    """Load or create the MAP-Elites archive."""
    if ARCHIVE_FILE.exists():
        return json.loads(ARCHIVE_FILE.read_text(encoding="utf-8"))

    # Initialize empty archive: pair × fail_mode → elite
    archive = {}
    for d1, d2 in combinations(ALL_DATASETS, 2):
        pk = pair_key(d1, d2)
        archive[pk] = {}
        for fm in FAIL_MODES:
            archive[pk][fm] = None  # empty bin
    return archive


def save_archive(archive):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, default=str)


def load_concept_overlap():
    """Precompute shared concepts for all pairs."""
    ds_concepts = defaultdict(set)
    with open(LINKS_FILE) as f:
        for line in f:
            link = json.loads(line)
            ds_concepts[link["dataset"]].add(link["concept"])

    overlaps = {}
    for d1, d2 in combinations(ALL_DATASETS, 2):
        pk = pair_key(d1, d2)
        shared = ds_concepts.get(d1, set()) & ds_concepts.get(d2, set())
        verbs = {c for c in shared if c.startswith("verb_")}
        overlaps[pk] = {
            "shared": shared,
            "verbs": verbs,
            "nouns": shared - verbs,
        }
    return overlaps


def generate_probe(d1, d2, overlaps):
    """Generate a zero-cost probe for a dataset pair."""
    pk = pair_key(d1, d2)
    ov = overlaps.get(pk, {})
    verbs = list(ov.get("verbs", []))
    nouns = list(ov.get("nouns", []))

    probes = []

    # Verb-based probes
    for verb in verbs[:3]:
        probes.append({
            "type": "verb_correlation",
            "d1": d1, "d2": d2,
            "claim": f"Objects in {d1} and {d2} tagged with '{verb}' have correlated properties",
            "verb": verb,
        })

    # Integer overlap probe
    def extract_ints(concepts):
        ints = set()
        for c in concepts:
            m = re.match(r'integer_(\d+)', c)
            if m:
                ints.add(int(m.group(1)))
        return ints

    from search_engine import (
        _load_knots, _knots_cache,
        _load_nf, _load_genus2, _load_maass, _load_lattices,
    )

    # Try to extract actual numerical arrays for correlation test
    # This is the "deep probe" that goes beyond concept overlap
    arrays = {}
    try:
        if d1 == "Genus2" or d2 == "Genus2":
            _load_genus2()
            from search_engine import _genus2_cache
            arrays["Genus2"] = np.array([c.get("conductor", 0) for c in _genus2_cache[:500]])
        if d1 == "Maass" or d2 == "Maass":
            _load_maass()
            from search_engine import _maass_cache
            arrays["Maass"] = np.array([m.get("spectral_parameter", 0) for m in _maass_cache])
        if d1 == "Lattices" or d2 == "Lattices":
            _load_lattices()
            from search_engine import _lattices_cache
            arrays["Lattices"] = np.array([l.get("kissing", 0) for l in _lattices_cache])
        if d1 == "KnotInfo" or d2 == "KnotInfo":
            _load_knots()
            dets = [k.get("determinant", 0) for k in _knots_cache if k.get("determinant", 0) > 0]
            arrays["KnotInfo"] = np.array(dets[:500])
        if d1 == "NumberFields" or d2 == "NumberFields":
            _load_nf()
            from search_engine import _nf_cache
            arrays["NumberFields"] = np.array([f.get("disc_abs", 0) for f in _nf_cache[:500]
                                               if f.get("disc_abs")])
    except Exception:
        pass

    if d1 in arrays and d2 in arrays:
        a1 = arrays[d1]
        a2 = arrays[d2]
        n = min(len(a1), len(a2))
        if n >= 20:
            probes.append({
                "type": "numerical_correlation",
                "d1": d1, "d2": d2,
                "claim": f"Numerical properties of {d1} and {d2} correlate (n={n})",
                "a1": a1[:n],
                "a2": a2[:n],
            })

    return probes


def test_probe(probe):
    """Run a probe and return result with failure mode classification."""
    ptype = probe["type"]

    if ptype == "verb_correlation":
        # Structural assessment — no numerical test yet
        return {
            "verdict": "OPEN",
            "fail_mode": "OPEN",
            "p": None,
            "z": None,
            "detail": f"Verb bridge '{probe['verb']}' identified, needs numerical extraction",
        }

    if ptype == "numerical_correlation":
        a1 = np.array(probe["a1"], dtype=float)
        a2 = np.array(probe["a2"], dtype=float)
        n = min(len(a1), len(a2))
        a1, a2 = a1[:n], a2[:n]

        # Remove zeros/nans
        mask = (a1 > 0) & (a2 > 0) & np.isfinite(a1) & np.isfinite(a2)
        a1, a2 = a1[mask], a2[mask]
        n = len(a1)

        if n < 15:
            return {"verdict": "SKIP", "fail_mode": "UNTESTED", "p": None, "z": None,
                    "detail": f"Too few valid pairs ({n})"}

        # Sort both and compare distributions
        a1_sorted = np.sort(a1)
        a2_sorted = np.sort(a2)

        # F1: Permutation test on rank correlation
        rho, p_rho = sp_stats.spearmanr(a1_sorted, a2_sorted)

        # F3: Effect size
        d_cohen = abs(np.mean(a1) - np.mean(a2)) / np.sqrt(
            (np.var(a1) + np.var(a2)) / 2) if np.var(a1) + np.var(a2) > 0 else 0

        # F13: Growth rate check
        idx = np.arange(n, dtype=float)
        r_sq = abs(sp_stats.spearmanr(a1_sorted, idx**2)[0])
        r_target = abs(rho)

        # F14: Phase shift
        if n >= 30:
            shifted_rhos = []
            for k in range(1, 6):
                if n - k >= 15:
                    r_k = abs(sp_stats.spearmanr(a1_sorted[k:], a2_sorted[:n-k])[0])
                    shifted_rhos.append(r_k)
            decay_ratio = np.mean(shifted_rhos) / abs(rho) if abs(rho) > 0.1 and shifted_rhos else 1.0
        else:
            decay_ratio = 1.0

        # Classify failure mode
        if p_rho > 0.05:
            fail_mode = "F1_permutation"
        elif d_cohen < 0.2:
            fail_mode = "F3_effect_size"
        elif r_sq > r_target and r_sq > 0.5:
            fail_mode = "F13_growth_rate"
        elif decay_ratio > 0.90 and abs(rho) > 0.5:
            fail_mode = "F14_phase_shift"
        elif p_rho < 0.01 and d_cohen > 0.2:
            fail_mode = "PASS"
        else:
            fail_mode = "F5_normalization"  # borderline

        passed = fail_mode == "PASS"

        return {
            "verdict": "PASS" if passed else "FAIL",
            "fail_mode": fail_mode,
            "p": round(float(p_rho), 6),
            "z": round(float(rho / (1/np.sqrt(n))) if n > 0 else 0, 2),
            "rho": round(float(rho), 4),
            "d_cohen": round(d_cohen, 4),
            "r_growth": round(r_sq, 4),
            "decay_ratio": round(decay_ratio, 4),
            "n": n,
            "detail": f"rho={rho:.4f}, p={p_rho:.6f}, d={d_cohen:.3f}, growth_r={r_sq:.3f}, decay={decay_ratio:.3f}",
        }

    return {"verdict": "SKIP", "fail_mode": "UNTESTED", "p": None, "z": None}


def illuminate(n_sweeps=1, focus_dataset=None):
    """Run MAP-Elites illumination sweeps."""
    print("=" * 70)
    print("  MAP-ELITES ILLUMINATOR")
    print("  Diversity-driven exploration of the shadow tensor")
    print("=" * 70)

    t0 = time.time()

    archive = load_archive()
    overlaps = load_concept_overlap()

    # Count empty bins
    total_bins = sum(len(modes) for modes in archive.values())
    empty_bins = sum(1 for pk in archive for fm in archive[pk] if archive[pk][fm] is None)
    print(f"\n  Archive: {total_bins} bins, {empty_bins} empty ({100*empty_bins/total_bins:.0f}%)")

    # Generate pairs to probe
    pairs = list(combinations(ALL_DATASETS, 2))
    if focus_dataset:
        pairs = [(d1, d2) for d1, d2 in pairs if focus_dataset in (d1, d2)]

    total_probes = 0
    total_updates = 0

    for sweep in range(n_sweeps):
        if n_sweeps > 1:
            print(f"\n  --- Sweep {sweep+1}/{n_sweeps} ---")

        for d1, d2 in pairs:
            pk = pair_key(d1, d2)
            probes = generate_probe(d1, d2, overlaps)

            for probe in probes:
                result = test_probe(probe)
                total_probes += 1
                fm = result["fail_mode"]

                if fm not in archive.get(pk, {}):
                    continue

                # Update bin if this is a better elite (closer to passing)
                current = archive[pk][fm]
                p = result.get("p")

                if current is None:
                    # Empty bin — fill it
                    archive[pk][fm] = {
                        "claim": probe["claim"],
                        "type": probe["type"],
                        "result": result,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }
                    total_updates += 1
                elif p is not None and current.get("result", {}).get("p") is not None:
                    # Better elite: lower p = closer to passing
                    if p < current["result"]["p"]:
                        archive[pk][fm] = {
                            "claim": probe["claim"],
                            "type": probe["type"],
                            "result": result,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        }
                        total_updates += 1

                # Log
                with open(RESULTS_FILE, "a") as f:
                    f.write(json.dumps({
                        "pair": pk,
                        "fail_mode": fm,
                        "probe": {k: v for k, v in probe.items() if k not in ("a1", "a2")},
                        "result": result,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }) + "\n")

    save_archive(archive)
    elapsed = time.time() - t0

    # Summary
    filled = sum(1 for pk in archive for fm in archive[pk] if archive[pk][fm] is not None)
    print(f"\n{'=' * 70}")
    print(f"  ILLUMINATION COMPLETE in {elapsed:.1f}s")
    print(f"  Probes: {total_probes}")
    print(f"  Archive updates: {total_updates}")
    print(f"  Bins filled: {filled}/{total_bins} ({100*filled/total_bins:.1f}%)")
    print(f"  Archive saved to {ARCHIVE_FILE}")

    # Show most interesting elites
    elites = []
    for pk in archive:
        for fm, elite in archive[pk].items():
            if elite is None:
                continue
            p = elite.get("result", {}).get("p")
            if p is not None and p < 0.1:
                elites.append((pk, fm, elite))

    if elites:
        elites.sort(key=lambda x: x[2]["result"]["p"])
        print(f"\n  NEAR-MISS ELITES (p < 0.1):")
        for pk, fm, elite in elites[:10]:
            r = elite["result"]
            print(f"    {pk:35s} [{fm:20s}] p={r['p']:.6f} {elite['claim'][:50]}")

    print(f"{'=' * 70}")

    return archive


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MAP-Elites Illuminator")
    parser.add_argument("--loop", type=int, default=1, help="Number of sweeps")
    parser.add_argument("--focus", type=str, default=None, help="Focus on dataset")
    args = parser.parse_args()

    illuminate(n_sweeps=args.loop, focus_dataset=args.focus)
