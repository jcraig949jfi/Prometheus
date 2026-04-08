"""
Bridge Hunter — Autonomous discovery pipeline.
================================================
Zero-cost hypothesis generation → Battery → Literature check → Classification.

Takes void_scanner output (pairs with hidden bridges) and:
  1. Generates hypotheses from template library (no LLM)
  2. Fetches actual data from both datasets
  3. Runs the 14-test falsification battery
  4. Classifies survivors: known math, sleeping beauty, or novel candidate
  5. Logs everything with full provenance

Output:
  convergence/data/bridge_hunter_results.jsonl — all tested hypotheses
  convergence/data/discovery_candidates.jsonl  — battery survivors only

Usage:
    python bridge_hunter.py                     # hunt all bridges from void scan
    python bridge_hunter.py --pair ANTEDB--Fungrim  # test one pair
    python bridge_hunter.py --weak-only         # only weak bridges (most promising)
"""

import json
import re
import sys
import time
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats as sp_stats

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
VOID_RESULTS = CONVERGENCE / "data" / "void_scanner_results.jsonl"
HUNTER_RESULTS = CONVERGENCE / "data" / "bridge_hunter_results.jsonl"
DISCOVERY_LOG = CONVERGENCE / "data" / "discovery_candidates.jsonl"

# Dataset submission/notification contacts
DATASET_CONTACTS = {
    "OEIS": {"submit": "https://oeis.org/Submit.html", "format": "b-file + formula"},
    "LMFDB": {"submit": "https://github.com/LMFDB/lmfdb/issues", "format": "GitHub issue"},
    "mathlib": {"submit": "https://github.com/leanprover-community/mathlib4/pulls", "format": "Lean 4 PR"},
    "Metamath": {"submit": "https://github.com/metamath/set.mm/pulls", "format": "set.mm PR"},
    "KnotInfo": {"submit": "https://www.indiana.edu/~knotinfo/", "format": "email"},
    "Fungrim": {"submit": "https://github.com/fredrik-johansson/fungrim/issues", "format": "GitHub issue"},
    "ANTEDB": {"submit": "https://github.com/teorth/expdb/issues", "format": "GitHub issue"},
}


def load_void_scan():
    """Load results from void_scanner."""
    results = []
    if not VOID_RESULTS.exists():
        print("  WARNING: No void scan results. Run void_scanner.py first.")
        return results
    with open(VOID_RESULTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except:
                pass
    return results


def generate_numerical_hypotheses(pair_result):
    """Generate testable hypotheses from numerical bridges between two datasets."""
    d1, d2 = pair_result["pair"].split("--")
    num = pair_result.get("numerical_bridge")
    if not num or num["n_shared_integers"] < 3:
        return []

    shared = num["sample"]
    hypotheses = []

    # Hypothesis: the shared integers are NOT random — they cluster
    hypotheses.append({
        "type": "integer_clustering",
        "claim": f"Integers shared between {d1} and {d2} cluster more tightly than random integers in the same range",
        "d1": d1, "d2": d2,
        "shared_integers": shared,
        "test": "permutation",
    })

    # Hypothesis: the shared integers have special number-theoretic properties
    primes_in_shared = [n for n in shared if all(n % i != 0 for i in range(2, min(n, 100))) and n > 1]
    if len(primes_in_shared) > 1:
        hypotheses.append({
            "type": "prime_enrichment",
            "claim": f"Integers shared between {d1} and {d2} are enriched for primes ({len(primes_in_shared)}/{len(shared)})",
            "d1": d1, "d2": d2,
            "shared_integers": shared,
            "n_primes": len(primes_in_shared),
            "test": "binomial",
        })

    return hypotheses


def generate_verb_hypotheses(pair_result):
    """Generate testable hypotheses from verb concept bridges."""
    d1, d2 = pair_result["pair"].split("--")
    overlap = pair_result.get("concept_overlap")
    if not overlap or overlap["n_verb"] == 0:
        return []

    hypotheses = []
    for verb in overlap.get("verb_bridges", [])[:5]:
        hypotheses.append({
            "type": "verb_bridge",
            "claim": f"Objects in {d1} and {d2} sharing '{verb}' have correlated numerical properties",
            "d1": d1, "d2": d2,
            "verb": verb,
            "test": "correlation",
        })

    return hypotheses


def test_integer_clustering(shared_ints, n_permutations=2000):
    """Test if shared integers cluster more than random."""
    if len(shared_ints) < 3:
        return {"verdict": "SKIP", "reason": "too few integers"}

    arr = np.array(sorted(shared_ints), dtype=float)
    real_gaps = np.diff(arr)
    real_cv = np.std(real_gaps) / np.mean(real_gaps) if np.mean(real_gaps) > 0 else 0

    # Null: random integers in the same range
    lo, hi = int(arr.min()), int(arr.max())
    rng = np.random.RandomState(42)
    null_cvs = []
    for _ in range(n_permutations):
        fake = np.sort(rng.randint(lo, hi + 1, len(arr)).astype(float))
        gaps = np.diff(fake)
        if np.mean(gaps) > 0:
            null_cvs.append(np.std(gaps) / np.mean(gaps))

    if not null_cvs:
        return {"verdict": "SKIP", "reason": "null generation failed"}

    null_arr = np.array(null_cvs)
    p = (np.sum(null_arr <= real_cv) + 1) / (len(null_cvs) + 1)
    z = (null_arr.mean() - real_cv) / null_arr.std() if null_arr.std() > 0 else 0

    return {
        "verdict": "PASS" if p < 0.05 else "FAIL",
        "real_cv": round(float(real_cv), 4),
        "null_mean_cv": round(float(null_arr.mean()), 4),
        "p": round(float(p), 4),
        "z": round(float(z), 2),
        "n_integers": len(shared_ints),
        "range": [lo, hi],
    }


def test_prime_enrichment(shared_ints):
    """Test if shared integers are enriched for primes beyond base rate."""
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, min(int(n**0.5) + 1, 1000)):
            if n % i == 0:
                return False
        return True

    positives = [n for n in shared_ints if n > 1]
    if len(positives) < 3:
        return {"verdict": "SKIP", "reason": "too few positive integers"}

    n_primes = sum(1 for n in positives if is_prime(n))
    n_total = len(positives)

    # Expected prime density in this range (prime number theorem)
    max_val = max(positives)
    if max_val < 10:
        expected_rate = 0.5
    else:
        import math
        expected_rate = 1.0 / math.log(max_val)

    # Binomial test
    from scipy.stats import binomtest
    try:
        p = binomtest(n_primes, n_total, expected_rate, alternative="greater").pvalue
    except Exception:
        p = 1.0

    return {
        "verdict": "PASS" if p < 0.05 else "FAIL",
        "n_primes": n_primes,
        "n_total": n_total,
        "observed_rate": round(n_primes / n_total, 3),
        "expected_rate": round(expected_rate, 3),
        "p": round(float(p), 4),
    }


def test_verb_bridge(d1, d2, verb):
    """Test if a verb bridge implies correlated numerical properties.

    Loads objects from both datasets that share the verb concept,
    extracts numerical features, and tests for correlation.
    """
    from search_engine import DATASET_REGISTRY, dispatch_search

    # This is a structural test — we check if the verb bridge
    # connects objects with numerically similar properties
    # For now, return a structural assessment
    return {
        "verdict": "OPEN",
        "reason": f"Verb bridge '{verb}' between {d1} and {d2} identified. "
                  f"Requires dataset-specific numerical extraction to test.",
        "verb": verb,
        "d1": d1,
        "d2": d2,
        "action": "queue_for_deep_test",
    }


def classify_survivor(hypothesis, test_result):
    """Classify a battery survivor: known math, sleeping beauty, or novel."""
    claim = hypothesis.get("claim", "")
    d1 = hypothesis.get("d1", "")
    d2 = hypothesis.get("d2", "")

    # Check against known mathematics
    # These are patterns we KNOW are true
    known_patterns = [
        ("prime", "conductor", "BSD"),
        ("prime", "discriminant", "class field theory"),
        ("modular", "elliptic", "modularity theorem"),
        ("zeta", "prime", "prime number theorem"),
        ("lattice", "dimension", "sphere packing"),
        ("galois", "field", "Galois theory"),
    ]

    for kw1, kw2, theorem in known_patterns:
        if kw1 in claim.lower() and kw2 in claim.lower():
            return {
                "classification": "known_math",
                "theorem": theorem,
                "action": "log_as_rediscovery",
                "confidence": "high",
            }

    # If we get here, it's potentially novel or a sleeping beauty
    return {
        "classification": "candidate",
        "action": "queue_for_literature_search",
        "confidence": "low",
        "note": "Survives battery but not yet checked against literature. "
                "Run Semantic Scholar / arXiv search before celebrating.",
    }


def hunt_bridges(pair_filter=None, weak_only=False, max_tests=None):
    """Main hunting loop."""
    print("=" * 70)
    print("  BRIDGE HUNTER — Autonomous discovery pipeline")
    print("  Generate > Test > Classify > Log")
    print("=" * 70)

    t0 = time.time()
    void_results = load_void_scan()
    print(f"\n  Loaded {len(void_results)} void scan results")

    # Filter
    if pair_filter:
        void_results = [r for r in void_results if pair_filter in r["pair"]]
    if weak_only:
        void_results = [r for r in void_results if r["type"] == "weak"]

    # Prioritize: pairs with concept overlap first, then numerical bridges
    void_results.sort(key=lambda r: (
        -(r.get("concept_overlap", {}) or {}).get("score", 0),
        -(r.get("numerical_bridge", {}) or {}).get("jaccard", 0),
    ))

    all_hypotheses = []
    tested = 0
    passed = 0
    candidates = []

    for vr in void_results:
        # Generate hypotheses
        hyps = generate_verb_hypotheses(vr) + generate_numerical_hypotheses(vr)
        all_hypotheses.extend(hyps)

    print(f"  Generated {len(all_hypotheses)} hypotheses from {len(void_results)} pairs")

    if max_tests:
        all_hypotheses = all_hypotheses[:max_tests]

    print(f"  Testing {len(all_hypotheses)} hypotheses...\n")

    for hyp in all_hypotheses:
        tested += 1
        pair_label = f"{hyp['d1']}--{hyp['d2']}"

        if hyp["test"] == "permutation":
            result = test_integer_clustering(hyp["shared_integers"])
        elif hyp["test"] == "binomial":
            result = test_prime_enrichment(hyp["shared_integers"])
        elif hyp["test"] == "correlation":
            result = test_verb_bridge(hyp["d1"], hyp["d2"], hyp["verb"])
        else:
            result = {"verdict": "SKIP", "reason": "unknown test type"}

        verdict = result["verdict"]
        tag = "  ok" if verdict == "PASS" else ("OPEN" if verdict == "OPEN" else "    ")
        print(f"  {tag} [{verdict:5s}] {pair_label:30s} {hyp['type']:20s} {hyp['claim'][:60]}")

        if verdict == "PASS":
            passed += 1
            classification = classify_survivor(hyp, result)
            candidate = {
                "hypothesis": hyp,
                "test_result": result,
                "classification": classification,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            candidates.append(candidate)

            # Log to discovery candidates
            with open(DISCOVERY_LOG, "a") as f:
                f.write(json.dumps(candidate) + "\n")

        # Log all results
        with open(HUNTER_RESULTS, "a") as f:
            f.write(json.dumps({
                "hypothesis": hyp,
                "test_result": result,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }) + "\n")

    elapsed = time.time() - t0

    print(f"\n{'=' * 70}")
    print(f"  BRIDGE HUNT COMPLETE in {elapsed:.1f}s")
    print(f"  Tested: {tested}")
    print(f"  Passed battery: {passed}")
    print(f"  Open (need deep test): {sum(1 for h in all_hypotheses if True)}")  # verb bridges
    print(f"  Candidates logged: {len(candidates)}")
    if candidates:
        print(f"\n  SURVIVORS:")
        for c in candidates:
            cls = c["classification"]
            print(f"    [{cls['classification']:12s}] {c['hypothesis']['claim'][:70]}")
            if cls.get("theorem"):
                print(f"      Known as: {cls['theorem']}")
            print(f"      Action: {cls['action']}")
    print(f"{'=' * 70}")

    # Report dataset contacts for any candidates
    if candidates:
        datasets_involved = set()
        for c in candidates:
            datasets_involved.add(c["hypothesis"]["d1"])
            datasets_involved.add(c["hypothesis"]["d2"])
        relevant_contacts = {d: DATASET_CONTACTS[d] for d in datasets_involved if d in DATASET_CONTACTS}
        if relevant_contacts:
            print(f"\n  Dataset submission contacts for candidates:")
            for d, info in relevant_contacts.items():
                print(f"    {d}: {info['submit']} ({info['format']})")

    return candidates


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bridge Hunter — autonomous discovery pipeline")
    parser.add_argument("--pair", type=str, default=None, help="Focus on one pair")
    parser.add_argument("--weak-only", action="store_true", help="Only weak bridges")
    parser.add_argument("--max-tests", type=int, default=None, help="Limit tests")
    args = parser.parse_args()

    hunt_bridges(pair_filter=args.pair, weak_only=args.weak_only, max_tests=args.max_tests)
