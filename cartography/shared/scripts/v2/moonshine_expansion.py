#!/usr/bin/env python3
"""
C09: Moonshine Network Expansion
- Expand coefficient window search across all 394K OEIS sequences
- Cross-match moonshine cores against Hecke eigenvalues from DuckDB
- Find multi-hop bridges via OEIS cross-references
"""

import gzip
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parents[4]  # F:/Prometheus
V2 = Path(__file__).resolve().parent
OEIS_STRIPPED = REPO / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_CROSSREFS = REPO / "cartography" / "oeis" / "data" / "oeis_crossrefs.jsonl"
DUCKDB_PATH = REPO / "charon" / "data" / "charon.duckdb"
EXISTING_RESULTS = V2 / "moonshine_oeis_results.json"
OUTPUT = V2 / "moonshine_expansion_results.json"

MIN_WINDOW = 6
MAX_WINDOW = 10
MIN_RECURSION_ORDER = 3
MIN_ENTROPY = 0.3
MAX_ZERO_FRAC = 0.6

# ── helpers ────────────────────────────────────────────────────────────

def parse_oeis_line(line: str):
    """Parse 'A000001 ,1,2,3,...' -> (seq_id, list_of_ints)"""
    if not line.startswith("A"):
        return None, None
    parts = line.split(" ", 1)
    if len(parts) < 2:
        return None, None
    seq_id = parts[0].strip()
    raw = parts[1].strip().strip(",")
    if not raw:
        return seq_id, []
    try:
        terms = [int(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        return seq_id, []
    return seq_id, terms


def coeff_entropy(window):
    """Shannon entropy of absolute coefficient distribution."""
    vals = [abs(v) for v in window]
    total = sum(vals)
    if total == 0:
        return 0.0
    probs = [v / total for v in vals if v > 0]
    return -sum(p * math.log2(p) for p in probs)


def zero_fraction(window):
    return sum(1 for v in window if v == 0) / len(window)


def is_trivial(window):
    """Reject windows that are all-same, all-zero, or monotone ±1."""
    s = set(window)
    if len(s) <= 1:
        return True
    if s <= {0, 1} or s <= {0, -1} or s <= {1, -1} or s <= {0, 1, -1}:
        return True
    # All same absolute value
    if len(set(abs(v) for v in window)) <= 1:
        return True
    return False


def recursion_order_estimate(window):
    """Estimate minimum linear recursion order via rank of Hankel matrix."""
    n = len(window)
    max_order = n // 2
    for order in range(1, max_order + 1):
        # Build Hankel-like matrix rows
        rows = []
        for i in range(order):
            if i + order < n:
                rows.append(window[i : i + order])
        if len(rows) < order:
            break
        # Check rank via simple Gaussian elimination
        mat = [list(map(float, r)) for r in rows]
        rank = 0
        for col in range(min(len(mat[0]), len(mat))):
            pivot = None
            for row in range(rank, len(mat)):
                if abs(mat[row][col]) > 1e-10:
                    pivot = row
                    break
            if pivot is None:
                continue
            mat[rank], mat[pivot] = mat[pivot], mat[rank]
            for row in range(len(mat)):
                if row != rank and abs(mat[row][col]) > 1e-10:
                    factor = mat[row][col] / mat[rank][col]
                    for c in range(len(mat[0])):
                        mat[row][c] -= factor * mat[rank][c]
            rank += 1
        if rank < order:
            return rank
    return max_order


def passes_quality(window):
    """Apply quality filters."""
    if is_trivial(window):
        return False
    if zero_fraction(window) >= MAX_ZERO_FRAC:
        return False
    if coeff_entropy(window) < MIN_ENTROPY:
        return False
    if recursion_order_estimate(window) < MIN_RECURSION_ORDER:
        return False
    return True


def extract_windows(terms, min_w=MIN_WINDOW, max_w=MAX_WINDOW):
    """Extract all sub-windows of length min_w..max_w from terms."""
    windows = []
    for w in range(min_w, max_w + 1):
        for start in range(len(terms) - w + 1):
            win = tuple(terms[start : start + w])
            windows.append((start, win))
    return windows


# ── Step 1: Load existing results and core sequences ──────────────────

def load_cores():
    print("[1] Loading existing moonshine results...")
    with open(EXISTING_RESULTS) as f:
        existing = json.load(f)

    cores = {}
    for seq_id, info in existing["core_sequences"].items():
        cores[seq_id] = info

    existing_bridges = existing.get("coefficient_bridges", [])
    existing_pairs = set()
    for b in existing_bridges:
        existing_pairs.add((b["core"], b["match"]))

    print(f"    {len(cores)} core sequences, {len(existing_bridges)} existing bridges")
    return cores, existing_bridges, existing_pairs


# ── Step 2: Load ALL OEIS and search for window matches ───────────────

def load_oeis_sequences():
    print("[2] Loading OEIS stripped_full.gz...")
    t0 = time.time()
    oeis = {}
    with gzip.open(OEIS_STRIPPED, "rt") as f:
        for line in f:
            seq_id, terms = parse_oeis_line(line)
            if seq_id and terms and len(terms) >= MIN_WINDOW:
                oeis[seq_id] = terms
    elapsed = time.time() - t0
    print(f"    Loaded {len(oeis)} sequences in {elapsed:.1f}s")
    return oeis


def build_core_windows(cores, oeis):
    """Build lookup of all windows from core sequences."""
    print("    Building core windows...")
    # We need the actual terms for cores from OEIS
    core_windows = {}  # window_tuple -> list of (core_id, offset)
    for seq_id in cores:
        if seq_id not in oeis:
            print(f"    WARNING: core {seq_id} not in OEIS data")
            continue
        terms = oeis[seq_id]
        for offset, win in extract_windows(terms):
            if is_trivial(win):
                continue
            if win not in core_windows:
                core_windows[win] = []
            core_windows[win].append((seq_id, offset))
    print(f"    {len(core_windows)} distinct non-trivial windows from cores")
    return core_windows


def search_oeis(core_windows, cores, oeis, existing_pairs):
    print("    Searching 394K sequences for window matches...")
    t0 = time.time()
    new_bridges = []
    match_count = 0
    checked = 0

    for seq_id, terms in oeis.items():
        if seq_id in cores:
            continue
        checked += 1
        if checked % 50000 == 0:
            print(f"      checked {checked}/{len(oeis)}...")

        for w in range(MIN_WINDOW, min(MAX_WINDOW + 1, len(terms) + 1)):
            for start in range(len(terms) - w + 1):
                win = tuple(terms[start : start + w])
                if win in core_windows:
                    for core_id, core_offset in core_windows[win]:
                        pair = (core_id, seq_id)
                        if pair in existing_pairs:
                            continue
                        # Quality filter on matched window
                        if not passes_quality(list(win)):
                            continue
                        bridge = {
                            "core": core_id,
                            "match": seq_id,
                            "window": list(win),
                            "window_length": len(win),
                            "core_offset": core_offset,
                            "match_offset": start,
                            "entropy": round(coeff_entropy(list(win)), 4),
                            "zero_frac": round(zero_fraction(list(win)), 4),
                            "recursion_order": recursion_order_estimate(list(win)),
                        }
                        new_bridges.append(bridge)
                        existing_pairs.add(pair)
                        match_count += 1

    elapsed = time.time() - t0
    print(f"    Found {match_count} new bridges in {elapsed:.1f}s")
    return new_bridges


# ── Step 3: Hecke eigenvalue cross-match ──────────────────────────────

def hecke_cross_match(core_windows, cores, oeis):
    print("[3] Cross-matching with Hecke eigenvalues from DuckDB...")
    hecke_matches = []

    try:
        import duckdb
    except ImportError:
        print("    DuckDB not available, skipping Hecke match")
        return hecke_matches

    if not DUCKDB_PATH.exists():
        print("    DuckDB file not found, skipping")
        return hecke_matches

    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    # Get modular forms with ap_coeffs
    # ap_coeffs is JSON array of arrays like [[-2], [-1], [1], ...]
    # These are Hecke eigenvalues a_p at successive primes
    print("    Loading Hecke eigenvalue sequences...")
    rows = con.execute("""
        SELECT lmfdb_label, level, weight, ap_coeffs
        FROM modular_forms
        WHERE ap_coeffs IS NOT NULL
    """).fetchall()
    print(f"    {len(rows)} modular forms with ap_coeffs")

    # For each form, flatten ap_coeffs to a sequence of integers
    t0 = time.time()
    checked = 0
    for label, level, weight, ap_json in rows:
        checked += 1
        if checked % 10000 == 0:
            print(f"      checked {checked}/{len(rows)}...")

        try:
            ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
            # Flatten: each entry is [val] for 1-dim forms
            flat = []
            for entry in ap:
                if isinstance(entry, list) and len(entry) == 1:
                    flat.append(int(entry[0]))
                elif isinstance(entry, (int, float)):
                    flat.append(int(entry))
                else:
                    break  # Higher-dim, skip
            if len(flat) < MIN_WINDOW:
                continue
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

        # Search for window matches against core windows
        seen_hecke = set()
        for w in range(MIN_WINDOW, min(MAX_WINDOW + 1, len(flat) + 1)):
            for start in range(len(flat) - w + 1):
                win = tuple(flat[start : start + w])
                if win in core_windows:
                    if is_trivial(win):
                        continue
                    # Extra quality: require entropy >= 1.0 and zero_frac < 0.5 for Hecke
                    wlist = list(win)
                    ent = coeff_entropy(wlist)
                    zf = zero_fraction(wlist)
                    if ent < 1.0 or zf >= 0.5:
                        continue
                    for core_id, core_offset in core_windows[win]:
                        key = (core_id, label, win)
                        if key in seen_hecke:
                            continue
                        seen_hecke.add(key)
                        match_info = {
                            "core": core_id,
                            "core_offset": core_offset,
                            "mf_label": label,
                            "mf_level": level,
                            "mf_weight": weight,
                            "window": wlist,
                            "window_length": len(win),
                            "mf_offset": start,
                            "entropy": round(ent, 4),
                            "zero_frac": round(zf, 4),
                        }
                        hecke_matches.append(match_info)

    con.close()
    elapsed = time.time() - t0
    print(f"    Found {len(hecke_matches)} Hecke eigenvalue matches in {elapsed:.1f}s")
    return hecke_matches


# ── Step 4: Multi-hop bridges via cross-references ────────────────────

def load_crossrefs():
    print("[4] Loading OEIS cross-references...")
    graph = defaultdict(set)
    if not OEIS_CROSSREFS.exists():
        print("    Cross-ref file not found")
        return graph
    t0 = time.time()
    with open(OEIS_CROSSREFS) as f:
        for line in f:
            try:
                rec = json.loads(line)
                src = rec.get("source", "")
                tgt = rec.get("target", "")
                if src and tgt:
                    graph[src].add(tgt)
                    graph[tgt].add(src)
            except json.JSONDecodeError:
                continue
    elapsed = time.time() - t0
    print(f"    Loaded {len(graph)} nodes, {sum(len(v) for v in graph.values())//2} edges in {elapsed:.1f}s")
    return graph


def find_multihop_bridges(cores, new_bridges, existing_bridges, crossref_graph):
    """Find 2-hop paths: core -> OEIS neighbor -> cross-ref target in other datasets."""
    print("    Finding multi-hop bridges...")

    # Collect all 1-hop bridge targets
    bridge_targets = set()
    for b in new_bridges + existing_bridges:
        bridge_targets.add(b["match"])

    # Known dataset sequences (load from various sources if available)
    # We'll check which cross-ref targets are themselves well-connected
    external_keywords = {
        "knot", "polynomial", "braid", "jones", "alexander",
        "conductor", "elliptic", "modular", "hecke", "l-function",
        "gamma", "zeta", "bernoulli", "euler", "riemann",
        "lattice", "root", "weyl", "cartan", "dynkin",
        "partition", "young", "schur", "character",
    }

    multihop = []
    seen = set()
    for target in bridge_targets:
        if target not in crossref_graph:
            continue
        neighbors = crossref_graph[target]
        for hop2 in neighbors:
            if hop2 in cores or hop2 in bridge_targets:
                continue
            key = (target, hop2)
            if key in seen:
                continue
            seen.add(key)
            # Record the 2-hop path
            # Find which cores connect to the bridge target
            source_cores = set()
            for b in new_bridges + existing_bridges:
                if b["match"] == target:
                    source_cores.add(b["core"])

            multihop.append({
                "hop1_target": target,
                "hop2_target": hop2,
                "source_cores": sorted(source_cores),
                "n_source_cores": len(source_cores),
            })

    # Sort by number of source cores (most connected first) and limit
    multihop.sort(key=lambda x: -x["n_source_cores"])
    print(f"    Found {len(multihop)} 2-hop paths")
    return multihop[:500]  # Cap to keep output reasonable


# ── Step 5: Report ────────────────────────────────────────────────────

def build_report(cores, existing_bridges, new_bridges, hecke_matches, multihop):
    print("\n[5] Building report...")

    # Deduplicate new bridges by (core, match) keeping longest window
    best = {}
    for b in new_bridges:
        key = (b["core"], b["match"])
        if key not in best or b["window_length"] > best[key]["window_length"]:
            best[key] = b
    deduped = sorted(best.values(), key=lambda x: (-x["window_length"], -x["entropy"]))

    # Network stats
    core_ids = set(cores.keys())
    all_neighbors = set()
    for b in deduped + existing_bridges:
        all_neighbors.add(b["match"])

    core_degree = defaultdict(int)
    for b in deduped:
        core_degree[b["core"]] += 1

    # Top new bridges by window length and entropy
    top_new = deduped[:50]

    # Hecke stats
    hecke_cores = set(m["core"] for m in hecke_matches)
    hecke_forms = set(m["mf_label"] for m in hecke_matches)

    report = {
        "summary": {
            "n_core_sequences": len(cores),
            "n_existing_bridges": len(existing_bridges),
            "n_new_bridges": len(deduped),
            "n_total_bridges": len(existing_bridges) + len(deduped),
            "n_unique_oeis_neighbors": len(all_neighbors),
            "n_hecke_matches": len(hecke_matches),
            "n_hecke_distinct_cores": len(hecke_cores),
            "n_hecke_distinct_forms": len(hecke_forms),
            "n_multihop_paths": len(multihop),
        },
        "core_degree_new": dict(sorted(core_degree.items(), key=lambda x: -x[1])),
        "top_new_bridges": top_new,
        "hecke_matches": hecke_matches[:100],  # Cap
        "multihop_top50": multihop[:50],
        "window_length_distribution": {},
    }

    # Window length distribution
    wl_dist = defaultdict(int)
    for b in deduped:
        wl_dist[b["window_length"]] += 1
    report["window_length_distribution"] = dict(sorted(wl_dist.items()))

    return report


# ── main ──────────────────────────────────────────────────────────────

def main():
    t_start = time.time()

    # Step 1
    cores, existing_bridges, existing_pairs = load_cores()

    # Step 2
    oeis = load_oeis_sequences()
    core_windows = build_core_windows(cores, oeis)
    new_bridges = search_oeis(core_windows, cores, oeis, existing_pairs)

    # Step 3
    hecke_matches = hecke_cross_match(core_windows, cores, oeis)

    # Step 4
    crossref_graph = load_crossrefs()
    multihop = find_multihop_bridges(cores, new_bridges, existing_bridges, crossref_graph)

    # Step 5
    report = build_report(cores, existing_bridges, new_bridges, hecke_matches, multihop)

    # Save
    with open(OUTPUT, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")

    elapsed = time.time() - t_start
    print(f"Total time: {elapsed:.1f}s")

    # Print summary
    s = report["summary"]
    print(f"\n{'='*60}")
    print(f"MOONSHINE EXPANSION RESULTS")
    print(f"{'='*60}")
    print(f"Core sequences:        {s['n_core_sequences']}")
    print(f"Existing bridges:      {s['n_existing_bridges']}")
    print(f"New bridges found:     {s['n_new_bridges']}")
    print(f"Total bridges:         {s['n_total_bridges']}")
    print(f"Unique OEIS neighbors: {s['n_unique_oeis_neighbors']}")
    print(f"Hecke eigenvalue hits: {s['n_hecke_matches']}")
    print(f"  Distinct cores:      {s['n_hecke_distinct_cores']}")
    print(f"  Distinct MF labels:  {s['n_hecke_distinct_forms']}")
    print(f"Multi-hop paths:       {s['n_multihop_paths']}")
    print(f"{'='*60}")

    if report["hecke_matches"]:
        print("\nHECKE EIGENVALUE MATCHES (extraordinary if non-trivial):")
        for m in report["hecke_matches"][:10]:
            print(f"  {m['core']} <-> {m['mf_label']} (N={m['mf_level']}, w={m['mf_weight']})")
            print(f"    window: {m['window']}")

    if report["top_new_bridges"]:
        print(f"\nTOP NEW BRIDGES (by window length):")
        for b in report["top_new_bridges"][:10]:
            print(f"  {b['core']} <-> {b['match']} (len={b['window_length']}, "
                  f"ent={b['entropy']}, rec={b['recursion_order']})")
            print(f"    window: {b['window'][:8]}{'...' if len(b['window']) > 8 else ''}")


if __name__ == "__main__":
    main()
