"""
FindStat Cross-Domain Probes — Map FindStat's position in the landscape.
=========================================================================
10 zero-test pairs. Most probes will be killed. That's the point.

Probe strategy:
  1. Extract numerical fingerprints from FindStat statistics (OEIS refs,
     collection sizes, statistic value distributions)
  2. Extract numerical fingerprints from target datasets
  3. Run falsification battery on every claimed overlap
  4. Report honestly

Usage:
    python findstat_probes.py                   # all probes
    python findstat_probes.py --pair FindStat--OEIS   # single pair
    python findstat_probes.py --dry-run         # show what would run
"""

import argparse
import json
import re
import sys
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent       # layer2/
SHARED_SCRIPTS = SCRIPT_DIR.parents[1]             # shared/scripts
V2_DIR = SCRIPT_DIR.parent                          # v2/
CARTOGRAPHY = SCRIPT_DIR.parents[3]                 # cartography/
ROOT = CARTOGRAPHY.parent                           # Prometheus/

sys.path.insert(0, str(SHARED_SCRIPTS))
sys.path.insert(0, str(V2_DIR))

from falsification_battery import run_battery

# Data paths
FINDSTAT_ENRICHED = CARTOGRAPHY / "findstat" / "data" / "findstat_enriched.json"
FINDSTAT_INDEX = CARTOGRAPHY / "findstat" / "data" / "findstat_index.json"
OEIS_NAMES = CARTOGRAPHY / "oeis" / "data" / "oeis_names.json"
OEIS_STRIPPED = CARTOGRAPHY / "oeis" / "data" / "stripped_new.txt"
KNOTS_JSON = CARTOGRAPHY / "knots" / "data" / "knots.json"
NF_JSON = CARTOGRAPHY / "number_fields" / "data" / "number_fields.json"
GROUPS_DIR = CARTOGRAPHY / "groups" / "data"
CHARON_DB = ROOT / "charon" / "data" / "charon.duckdb"
OUT_FILE = CARTOGRAPHY / "convergence" / "data" / "findstat_probes.jsonl"


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_findstat_enriched():
    """Load enriched FindStat statistics with descriptions and OEIS refs."""
    if not FINDSTAT_ENRICHED.exists():
        print(f"  WARN: {FINDSTAT_ENRICHED} not found")
        return []
    with open(FINDSTAT_ENRICHED, encoding="utf-8") as f:
        data = json.load(f)
    stats = data.get("statistics", [])
    print(f"  FindStat enriched: {len(stats)} statistics loaded")
    return stats


def extract_oeis_refs(stats):
    """Pull OEIS A-numbers referenced by FindStat statistics."""
    refs = {}
    for s in stats:
        ref_text = s.get("references", "")
        matches = re.findall(r"OEIS:A(\d+)", ref_text)
        if matches:
            refs[s["id"]] = [f"A{m.zfill(6)}" for m in matches]
    total = sum(len(v) for v in refs.values())
    unique = len(set(a for v in refs.values() for a in v))
    print(f"  OEIS refs: {total} total, {unique} unique sequences from {len(refs)} statistics")
    return refs


def extract_collection_sizes(stats):
    """Count how many statistics belong to each collection."""
    counts = Counter(s.get("collection", "unknown") for s in stats)
    return dict(counts)


def load_oeis_terms(a_numbers, max_terms=64):
    """Load first N terms for given OEIS sequences from stripped_new.txt."""
    if not OEIS_STRIPPED.exists():
        print(f"  WARN: {OEIS_STRIPPED} not found")
        return {}
    target = set(a_numbers)
    result = {}
    with open(OEIS_STRIPPED, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            if seq_id in target:
                terms_str = parts[1].strip().strip(",")
                try:
                    terms = [int(x) for x in terms_str.split(",") if x.strip()]
                    result[seq_id] = terms[:max_terms]
                except ValueError:
                    pass
    print(f"  OEIS terms loaded: {len(result)}/{len(target)} sequences")
    return result


def load_number_fields():
    """Load number field data (class numbers, discriminants)."""
    if not NF_JSON.exists():
        print(f"  WARN: {NF_JSON} not found")
        return []
    with open(NF_JSON, encoding="utf-8") as f:
        data = json.load(f)
    print(f"  Number fields: {len(data)} loaded")
    return data


def load_knot_invariants():
    """Load knot determinants and polynomial data."""
    if not KNOTS_JSON.exists():
        print(f"  WARN: {KNOTS_JSON} not found")
        return []
    with open(KNOTS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    knots = data.get("knots", [])
    print(f"  Knots: {len(knots)} loaded")
    return knots


def load_oeis_group_counts():
    """A000001 = number of groups of order n. Load from stripped_new.txt."""
    terms = load_oeis_terms(["A000001"], max_terms=512)
    if "A000001" in terms:
        return terms["A000001"]
    return []


# ---------------------------------------------------------------------------
# Probe functions — each returns list of probe results
# ---------------------------------------------------------------------------

def probe_findstat_oeis(stats):
    """FindStat--OEIS: do OEIS sequences referenced by FindStat statistics
    show distributional similarity to collection size distributions?"""
    probes = []
    oeis_refs = extract_oeis_refs(stats)
    if not oeis_refs:
        return [_skip_result("FindStat--OEIS", "No OEIS refs found in FindStat data")]

    all_a_numbers = list(set(a for v in oeis_refs.values() for a in v))
    oeis_terms = load_oeis_terms(all_a_numbers)

    if not oeis_terms:
        return [_skip_result("FindStat--OEIS", "Could not load OEIS terms")]

    # Probe 1: Distribution of OEIS-referenced sequence initial terms vs
    # distribution of FindStat statistic ID numbers (as integers).
    # Rationale: if FindStat preferentially references OEIS sequences whose
    # terms match combinatorial sizes, we'd see distributional overlap.
    oeis_first_terms = []
    for seq_id, terms in oeis_terms.items():
        oeis_first_terms.extend(terms[:16])
    oeis_first_terms = np.array([t for t in oeis_first_terms if 0 <= t <= 10000], dtype=float)

    # FindStat stat IDs as integers (St000001 -> 1)
    stat_ids = np.array([int(s["id"][2:]) for s in stats], dtype=float)

    if len(oeis_first_terms) >= 20 and len(stat_ids) >= 20:
        claim = "OEIS sequences referenced by FindStat have terms correlated with FindStat statistic IDs"
        verdict, results = run_battery(oeis_first_terms, stat_ids, claim=claim)
        probes.append(_probe_result("FindStat--OEIS", "oeis_ref_terms_vs_stat_ids",
                                    claim, len(oeis_first_terms), len(stat_ids),
                                    verdict, results))

    # Probe 2: Per-collection count of OEIS refs — does any collection
    # disproportionately reference OEIS?
    coll_ref_counts = Counter()
    for s in stats:
        sid = s["id"]
        if sid in oeis_refs:
            coll_ref_counts[s.get("collection", "unknown")] += len(oeis_refs[sid])

    coll_sizes = extract_collection_sizes(stats)
    # Compute ref density per collection
    if len(coll_ref_counts) >= 3:
        collections_both = [c for c in coll_sizes if c in coll_ref_counts]
        sizes = np.array([coll_sizes[c] for c in collections_both], dtype=float)
        ref_counts = np.array([coll_ref_counts[c] for c in collections_both], dtype=float)

        if len(sizes) >= 5:
            claim2 = "FindStat collection size predicts OEIS reference count"
            verdict2, results2 = run_battery(sizes, ref_counts, claim=claim2)
            probes.append(_probe_result("FindStat--OEIS", "collection_size_vs_oeis_refs",
                                        claim2, len(sizes), len(ref_counts),
                                        verdict2, results2))

    return probes if probes else [_skip_result("FindStat--OEIS", "Insufficient data for probes")]


def probe_findstat_numberfields(stats):
    """FindStat--NumberFields: do partition statistics produce values
    matching class numbers or discriminant magnitudes?"""
    probes = []
    nf_data = load_number_fields()
    if not nf_data:
        return [_skip_result("FindStat--NumberFields", "No number field data")]

    # Extract class numbers and discriminants
    class_numbers = np.array([int(nf["class_number"]) for nf in nf_data
                              if nf.get("class_number")], dtype=float)
    disc_abs = np.array([int(nf["disc_abs"]) for nf in nf_data
                         if nf.get("disc_abs")], dtype=float)

    # FindStat: partition statistics often produce small integers.
    # Extract collection distribution as proxy for "typical statistic values"
    partition_stats = [s for s in stats if s.get("collection") == "Integer partitions"]
    perm_stats = [s for s in stats if s.get("collection") == "Permutations"]

    # Statistic ID numbers for partition stats
    partition_ids = np.array([int(s["id"][2:]) for s in partition_stats], dtype=float)
    perm_ids = np.array([int(s["id"][2:]) for s in perm_stats], dtype=float)

    # Probe: class number distribution vs partition statistic ID distribution
    if len(class_numbers) >= 20 and len(partition_ids) >= 10:
        claim = "Number field class numbers overlap with FindStat partition statistic ID distribution"
        verdict, results = run_battery(class_numbers, partition_ids, claim=claim)
        probes.append(_probe_result("FindStat--NumberFields", "class_numbers_vs_partition_stat_ids",
                                    claim, len(class_numbers), len(partition_ids),
                                    verdict, results))

    # Probe: log-discriminants vs permutation stat IDs
    if len(disc_abs) >= 20 and len(perm_ids) >= 10:
        log_disc = np.log1p(disc_abs)
        claim2 = "Number field log-discriminants correlate with FindStat permutation statistic IDs"
        verdict2, results2 = run_battery(log_disc, perm_ids, claim=claim2)
        probes.append(_probe_result("FindStat--NumberFields", "log_disc_vs_perm_stat_ids",
                                    claim2, len(log_disc), len(perm_ids),
                                    verdict2, results2))

    # Probe: class number value distribution vs collection size distribution
    coll_sizes = extract_collection_sizes(stats)
    coll_arr = np.array(sorted(coll_sizes.values()), dtype=float)
    if len(class_numbers) >= 20 and len(coll_arr) >= 5:
        claim3 = "Number field class number distribution matches FindStat collection size distribution"
        verdict3, results3 = run_battery(class_numbers[:len(coll_arr)], coll_arr, claim=claim3)
        probes.append(_probe_result("FindStat--NumberFields", "class_num_vs_coll_sizes",
                                    claim3, len(class_numbers[:len(coll_arr)]), len(coll_arr),
                                    verdict3, results3))

    return probes if probes else [_skip_result("FindStat--NumberFields", "Insufficient data")]


def probe_findstat_knotinfo(stats):
    """FindStat--KnotInfo: permutation stats <-> knot invariants.
    The theoretical link: permutations -> braids -> knots."""
    probes = []
    knots = load_knot_invariants()
    if not knots:
        return [_skip_result("FindStat--KnotInfo", "No knot data")]

    # Knot determinants
    dets = np.array([k["determinant"] for k in knots if k.get("determinant")], dtype=float)
    # Crossing numbers
    crossings = np.array([k["crossing_number"] for k in knots if k.get("crossing_number")], dtype=float)

    # FindStat permutation statistics (IDs as proxy for coverage density)
    perm_stats = [s for s in stats if s.get("collection") == "Permutations"]
    perm_ids = np.array([int(s["id"][2:]) for s in perm_stats], dtype=float)

    # Alexander polynomial degree distribution
    alex_degrees = []
    for k in knots:
        alex = k.get("alexander", {})
        if alex and alex.get("max_power") is not None and alex.get("min_power") is not None:
            alex_degrees.append(alex["max_power"] - alex["min_power"])
    alex_degrees = np.array(alex_degrees, dtype=float) if alex_degrees else np.array([])

    # Probe: knot determinant distribution vs permutation stat ID distribution
    if len(dets) >= 20 and len(perm_ids) >= 10:
        claim = "Knot determinants share distributional structure with FindStat permutation statistic IDs"
        verdict, results = run_battery(dets, perm_ids, claim=claim)
        probes.append(_probe_result("FindStat--KnotInfo", "knot_det_vs_perm_stat_ids",
                                    claim, len(dets), len(perm_ids),
                                    verdict, results))

    # Probe: Alexander polynomial degree vs crossing number
    # (not directly FindStat, but tests the braid link)
    if len(alex_degrees) >= 20 and len(crossings) >= 20:
        claim2 = "Alexander polynomial degrees correlate with crossing numbers (braid-permutation link)"
        verdict2, results2 = run_battery(alex_degrees, crossings[:len(alex_degrees)], claim=claim2)
        probes.append(_probe_result("FindStat--KnotInfo", "alex_degree_vs_crossing",
                                    claim2, len(alex_degrees), len(crossings),
                                    verdict2, results2))

    # Probe: knot determinant log-distribution vs FindStat collection sizes
    coll_sizes = extract_collection_sizes(stats)
    coll_arr = np.array(sorted(coll_sizes.values()), dtype=float)
    if len(dets) >= 20 and len(coll_arr) >= 5:
        log_dets = np.log1p(dets)
        claim3 = "Log knot determinants match FindStat collection size distribution"
        verdict3, results3 = run_battery(log_dets[:len(coll_arr)], coll_arr, claim=claim3)
        probes.append(_probe_result("FindStat--KnotInfo", "log_det_vs_coll_sizes",
                                    claim3, len(log_dets[:len(coll_arr)]), len(coll_arr),
                                    verdict3, results3))

    return probes if probes else [_skip_result("FindStat--KnotInfo", "Insufficient data")]


def probe_findstat_smallgroups(stats):
    """FindStat--SmallGroups: do group counts (A000001) match
    any FindStat distributional fingerprint?"""
    probes = []
    group_counts = load_oeis_group_counts()
    if not group_counts or len(group_counts) < 20:
        return [_skip_result("FindStat--SmallGroups", "Could not load A000001 (group counts)")]

    gc = np.array(group_counts, dtype=float)

    # FindStat collection sizes
    coll_sizes = extract_collection_sizes(stats)
    coll_arr = np.array(sorted(coll_sizes.values()), dtype=float)

    # Probe: group count distribution vs collection sizes
    if len(coll_arr) >= 5:
        n = min(len(gc), len(coll_arr))
        claim = "Group count sequence (A000001) correlates with FindStat collection sizes"
        verdict, results = run_battery(gc[:n], coll_arr[:n], claim=claim)
        probes.append(_probe_result("FindStat--SmallGroups", "group_counts_vs_coll_sizes",
                                    claim, n, n, verdict, results))

    # Probe: group counts at small orders vs statistic ID density
    # How many FindStat stats per "decade" of IDs?
    id_bins = np.bincount(np.array([int(s["id"][2:]) // 100 for s in stats]))
    id_bins = id_bins[id_bins > 0].astype(float)
    n2 = min(len(gc), len(id_bins))
    if n2 >= 10:
        claim2 = "Group counts at order n match FindStat statistic density per century"
        verdict2, results2 = run_battery(gc[:n2], id_bins[:n2], claim=claim2)
        probes.append(_probe_result("FindStat--SmallGroups", "group_counts_vs_stat_density",
                                    claim2, n2, n2, verdict2, results2))

    # Probe: group count sequence growth vs permutation stat count growth
    perm_stats = [s for s in stats if s.get("collection") == "Permutations"]
    perm_ids = sorted(int(s["id"][2:]) for s in perm_stats)
    if len(perm_ids) >= 20:
        # Gaps between consecutive permutation stat IDs
        perm_gaps = np.diff(perm_ids).astype(float)
        n3 = min(len(gc), len(perm_gaps))
        if n3 >= 10:
            claim3 = "Group count growth matches gaps between FindStat permutation statistic IDs"
            verdict3, results3 = run_battery(gc[:n3], perm_gaps[:n3], claim=claim3)
            probes.append(_probe_result("FindStat--SmallGroups", "group_counts_vs_perm_gaps",
                                        claim3, n3, n3, verdict3, results3))

    return probes if probes else [_skip_result("FindStat--SmallGroups", "Insufficient data")]


def probe_findstat_generic(stats, pair_name, description):
    """Generic probe for pairs without specific target data.
    Uses collection size distribution and statistic ID distribution
    as the FindStat fingerprint, and tests against simple baselines."""
    probes = []

    coll_sizes = extract_collection_sizes(stats)
    coll_arr = np.array(sorted(coll_sizes.values()), dtype=float)
    stat_ids = np.array(sorted(int(s["id"][2:]) for s in stats), dtype=float)

    # Self-consistency: are collection sizes uniformly distributed?
    # (baseline for later cross-comparisons)
    if len(coll_arr) >= 5:
        uniform = np.linspace(coll_arr.min(), coll_arr.max(), len(coll_arr))
        claim = f"{pair_name}: FindStat collection sizes differ from uniform baseline ({description})"
        verdict, results = run_battery(coll_arr, uniform, claim=claim)
        probes.append(_probe_result(pair_name, "coll_sizes_vs_uniform",
                                    claim, len(coll_arr), len(uniform),
                                    verdict, results))

    # Statistic ID gaps — are they regular or clustered?
    if len(stat_ids) >= 50:
        gaps = np.diff(stat_ids)
        random_gaps = np.random.RandomState(42).exponential(scale=gaps.mean(), size=len(gaps))
        claim2 = f"{pair_name}: FindStat stat ID gaps differ from exponential null ({description})"
        verdict2, results2 = run_battery(gaps, random_gaps, claim=claim2)
        probes.append(_probe_result(pair_name, "stat_gaps_vs_exponential",
                                    claim2, len(gaps), len(random_gaps),
                                    verdict2, results2))

    return probes if probes else [_skip_result(pair_name, f"Insufficient data for {description}")]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _probe_result(pair, probe_name, claim, n_a, n_b, verdict, battery_results):
    passes = [r["test"] for r in battery_results if r.get("verdict") == "PASS"]
    kills = [r["test"] for r in battery_results if r.get("verdict") == "FAIL"]
    skips = [r["test"] for r in battery_results if r.get("verdict") == "SKIP"]
    return {
        "pair": pair,
        "probe": probe_name,
        "claim": claim,
        "data_sizes": {"a": n_a, "b": n_b},
        "verdict": verdict,
        "pass_tests": passes,
        "kill_tests": kills,
        "skip_tests": skips,
        "n_pass": len(passes),
        "n_kill": len(kills),
        "n_skip": len(skips),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _skip_result(pair, reason):
    return {
        "pair": pair,
        "probe": "SKIPPED",
        "claim": reason,
        "data_sizes": {"a": 0, "b": 0},
        "verdict": "SKIPPED",
        "pass_tests": [],
        "kill_tests": [],
        "skip_tests": [],
        "n_pass": 0,
        "n_kill": 0,
        "n_skip": 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


# ---------------------------------------------------------------------------
# All pairs registry
# ---------------------------------------------------------------------------

COLD_PAIRS = [
    "FindStat--OEIS",
    "FindStat--NumberFields",
    "FindStat--KnotInfo",
    "FindStat--SmallGroups",
    "FindStat--Genus2",
    "FindStat--LocalFields",
    "FindStat--Maass",
    "FindStat--Materials",
    "FindStat--Metamath",
    "FindStat--OpenAlex",
]


def run_all_probes(stats, pairs=None):
    """Run probes for specified pairs (or all cold pairs)."""
    pairs = pairs or COLD_PAIRS
    all_probes = []

    for pair in pairs:
        print(f"\n{'='*60}")
        print(f"  PROBE: {pair}")
        print(f"{'='*60}")
        t0 = time.time()

        try:
            if pair == "FindStat--OEIS":
                results = probe_findstat_oeis(stats)
            elif pair == "FindStat--NumberFields":
                results = probe_findstat_numberfields(stats)
            elif pair == "FindStat--KnotInfo":
                results = probe_findstat_knotinfo(stats)
            elif pair == "FindStat--SmallGroups":
                results = probe_findstat_smallgroups(stats)
            elif pair == "FindStat--Genus2":
                results = probe_findstat_generic(stats, pair, "genus-2 curves")
            elif pair == "FindStat--LocalFields":
                results = probe_findstat_generic(stats, pair, "local fields")
            elif pair == "FindStat--Maass":
                results = probe_findstat_generic(stats, pair, "Maass forms")
            elif pair == "FindStat--Materials":
                results = probe_findstat_generic(stats, pair, "materials science")
            elif pair == "FindStat--Metamath":
                results = probe_findstat_generic(stats, pair, "formal proofs")
            elif pair == "FindStat--OpenAlex":
                results = probe_findstat_generic(stats, pair, "academic citations")
            else:
                results = [_skip_result(pair, f"Unknown pair: {pair}")]
        except Exception as e:
            print(f"  ERROR: {e}")
            results = [_skip_result(pair, f"Exception: {e}")]

        elapsed = time.time() - t0
        for r in results:
            r["elapsed_s"] = round(elapsed / max(len(results), 1), 2)
        all_probes.extend(results)

        for r in results:
            v = r["verdict"]
            tag = "KILLED" if v == "KILLED" else ("SURVIVES" if v == "SURVIVES" else v)
            print(f"  -> {r['probe']}: {tag}  (pass={r['n_pass']} kill={r['n_kill']} skip={r['n_skip']})")

    return all_probes


def save_results(probes, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for p in probes:
            f.write(json.dumps(p, cls=_NumpyEncoder) + "\n")
    print(f"\nResults written to {path}")


def print_summary(probes):
    print(f"\n{'='*60}")
    print("  FINDSTAT PROBE SUMMARY")
    print(f"{'='*60}")
    total = len(probes)
    survived = sum(1 for p in probes if p["verdict"] == "SURVIVES")
    killed = sum(1 for p in probes if p["verdict"] == "KILLED")
    skipped = sum(1 for p in probes if p["verdict"] == "SKIPPED")
    print(f"  Total probes: {total}")
    print(f"  SURVIVES:     {survived}")
    print(f"  KILLED:       {killed}")
    print(f"  SKIPPED:      {skipped}")

    if survived > 0:
        print(f"\n  Survivors:")
        for p in probes:
            if p["verdict"] == "SURVIVES":
                print(f"    {p['pair']} / {p['probe']}")
                print(f"      {p['claim']}")

    pairs_seen = set(p["pair"] for p in probes)
    print(f"\n  Pairs probed: {len(pairs_seen)}/{len(COLD_PAIRS)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="FindStat cross-domain probes")
    parser.add_argument("--pair", type=str, default=None,
                        help="Run single pair (e.g. FindStat--OEIS)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would run without executing")
    parser.add_argument("--out", type=str, default=str(OUT_FILE),
                        help="Output JSONL path")
    args = parser.parse_args()

    pairs = [args.pair] if args.pair else COLD_PAIRS

    if args.dry_run:
        print("DRY RUN — would probe:")
        for p in pairs:
            print(f"  {p}")
        return

    print("Loading FindStat data...")
    stats = load_findstat_enriched()
    if not stats:
        print("FATAL: No FindStat data. Exiting.")
        sys.exit(1)

    warnings.filterwarnings("ignore", category=RuntimeWarning)
    probes = run_all_probes(stats, pairs)
    save_results(probes, Path(args.out))
    print_summary(probes)


if __name__ == "__main__":
    main()
