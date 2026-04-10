#!/usr/bin/env python3
"""
Moonshine-Hecke Bipartite Graph
================================
Build and analyse a bipartite graph connecting moonshine sequences (Side A)
to Hecke levels from modular forms (Side B).

Edge rule (relaxed from R3-5 exact matching):
  Moonshine sequence S connects to level N if S shares a 6-term coefficient
  window with any weight-2 newform at level N, where "shares" means either
    (a) exact integer match, OR
    (b) congruence mod p for some small prime p in {2,3,5,7,11}

Side A is partitioned into: monstrous, umbral, mock_theta, modular,
  theta, lattice_theta (the last three = Niemeier-adjacent)

The key question: do any Hecke levels serve as "meeting points" connecting
BOTH monstrous and umbral moonshine simultaneously?
"""

import json, sys, os, time, math
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

# Suppress DuckDB progress bar
os.environ["DUCKDB_NO_THREADS"] = "1"

# ── paths ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[4]  # F:/Prometheus
V2 = Path(__file__).resolve().parent
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
MOONSHINE_OEIS = V2 / "moonshine_oeis_results.json"
MOONSHINE_EXPANSION = V2 / "moonshine_expansion_results.json"
OUT_PATH = V2 / "moonshine_hecke_bipartite_results.json"

WINDOW = 6
MOD_PRIMES = [2, 3, 5, 7, 11]

# ── Classification of the 21 core sequences ────────────────────────────
MOONSHINE_PARTITION = {
    "monstrous": ["A000521", "A007191", "A014708", "A007246", "A007267"],
    "umbral": ["A053250"],
    "mock_theta": ["A045488", "A001488"],
    "modular": ["A000594", "A006352", "A004009", "A013973",
                "A008410", "A013974", "A029829"],
    "theta": ["A000118", "A008443", "A000122"],
    "lattice_theta": ["A004011", "A008408", "A004027"],
}

SEQ_TO_FAMILY = {}
for fam, seqs in MOONSHINE_PARTITION.items():
    for s in seqs:
        SEQ_TO_FAMILY[s] = fam

def p(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def load_oeis_sequences(seq_ids):
    """Load coefficient sequences from OEIS stripped file."""
    wanted = set(seq_ids)
    result = {}
    with open(OEIS_STRIPPED, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0]
            if sid in wanted:
                coeffs_str = parts[1].strip().strip(",")
                try:
                    coeffs = [int(x) for x in coeffs_str.split(",") if x.strip()]
                    result[sid] = coeffs
                except ValueError:
                    pass
    return result


def window_entropy(w):
    """Shannon entropy of a window."""
    counts = Counter(w)
    n = len(w)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())


def build_bipartite_graph():
    """Main pipeline."""
    p("=" * 70)
    p("MOONSHINE-HECKE BIPARTITE GRAPH")
    p("=" * 70)

    # ── 1. Load moonshine core data ────────────────────────────────────
    with open(MOONSHINE_OEIS) as f:
        oeis_data = json.load(f)
    with open(MOONSHINE_EXPANSION) as f:
        expansion_data = json.load(f)

    core_ids = list(oeis_data["core_sequences"].keys())
    p(f"\nCore moonshine sequences: {len(core_ids)}")

    # Collect bridge target IDs
    bridge_targets = set()
    for b in expansion_data.get("top_new_bridges", []):
        bridge_targets.add(b["match"])
    for m in expansion_data.get("multihop_top50", []):
        if "path" in m:
            for node in m["path"]:
                if node.startswith("A") and node not in core_ids:
                    bridge_targets.add(node)

    all_seq_ids = set(core_ids) | bridge_targets
    p(f"Bridge target sequences: {len(bridge_targets)}")
    p(f"Total Side-A candidates: {len(all_seq_ids)}")

    # ── 2. Load OEIS coefficient data ──────────────────────────────────
    p("\nLoading OEIS sequences...")
    oeis_coeffs = load_oeis_sequences(all_seq_ids)
    p(f"Loaded {len(oeis_coeffs)} sequences with coefficients")

    # ── 3. Build window hash tables for moonshine sequences ────────────
    p("Building window hash index...")
    # exact_index: frozenset-free, just tuple -> [(seq_id, offset)]
    exact_index = defaultdict(list)
    mod_index = {pp: defaultdict(list) for pp in MOD_PRIMES}

    n_windows = 0
    for sid in oeis_coeffs:
        coeffs = oeis_coeffs[sid]
        max_win = min(len(coeffs) - WINDOW + 1, 100 if sid in core_ids else 50)
        for i in range(max(0, max_win)):
            w = tuple(coeffs[i:i+WINDOW])
            if len(set(w)) <= 1:
                continue
            ent = window_entropy(w)
            if ent < 1.0:
                continue
            exact_index[w].append((sid, i))
            for pp in MOD_PRIMES:
                wm = tuple(x % pp for x in w)
                mod_index[pp][wm].append((sid, i))
            n_windows += 1

    p(f"Indexed {n_windows} windows")
    p(f"Unique exact windows: {len(exact_index)}")
    for pp in MOD_PRIMES:
        p(f"  Unique mod-{pp} windows: {len(mod_index[pp])}")

    # ── 4. Load modular forms in batches ───────────────────────────────
    p("\nLoading modular forms from DuckDB...")
    import duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Get total count
    total = con.execute("SELECT COUNT(*) FROM modular_forms WHERE traces IS NOT NULL").fetchone()[0]
    p(f"Total forms with traces: {total}")

    # Process in chunks to limit memory
    BATCH = 10000
    TRACE_CAP = 150  # only check first 150 coefficients per form

    edges_raw = defaultdict(lambda: defaultdict(list))
    edge_count = 0
    forms_scanned = 0
    t0 = time.time()

    for offset in range(0, total, BATCH):
        rows = con.execute(
            f"SELECT lmfdb_label, level, traces FROM modular_forms "
            f"WHERE traces IS NOT NULL "
            f"ORDER BY object_id LIMIT {BATCH} OFFSET {offset}"
        ).fetchall()

        for label, level, traces in rows:
            if traces is None or len(traces) < WINDOW:
                continue
            forms_scanned += 1

            # Integer traces, capped
            int_tr = [int(round(t)) for t in traces[:TRACE_CAP]]
            n_tr = len(int_tr)

            for j in range(n_tr - WINDOW + 1):
                fw = tuple(int_tr[j:j+WINDOW])
                if len(set(fw)) <= 1:
                    continue

                # Exact match
                if fw in exact_index:
                    for (sid, s_off) in exact_index[fw]:
                        edges_raw[sid][level].append({
                            "mt": "exact", "p": 0,
                            "label": label, "fo": j, "so": s_off,
                            "w": list(fw), "ent": round(window_entropy(fw), 4)
                        })
                        edge_count += 1

                # Mod-p matches
                for pp in MOD_PRIMES:
                    fwm = tuple(x % pp for x in fw)
                    if fwm in mod_index[pp]:
                        for (sid, s_off) in mod_index[pp][fwm]:
                            # skip if also exact
                            orig = tuple(oeis_coeffs[sid][s_off:s_off+WINDOW])
                            if orig == fw:
                                continue
                            edges_raw[sid][level].append({
                                "mt": f"mod-{pp}", "p": pp,
                                "label": label, "fo": j, "so": s_off,
                                "w": list(fw), "ent": round(window_entropy(fw), 4)
                            })
                            edge_count += 1

        elapsed = time.time() - t0
        p(f"  Batch {offset//BATCH + 1}: scanned {forms_scanned} forms, "
          f"{edge_count} raw edges ({elapsed:.1f}s)")

    con.close()
    p(f"\nScan complete: {edge_count} raw edges from {forms_scanned} forms "
      f"in {time.time()-t0:.1f}s")

    # ── 5. Deduplicate: one edge per (seq, level) pair ─────────────────
    bipartite_edges = []
    seq_level_pairs = set()
    for sid in edges_raw:
        for level in edges_raw[sid]:
            matches = edges_raw[sid][level]
            matches.sort(key=lambda m: (0 if m["mt"] == "exact" else 1, -m["ent"]))
            best = matches[0]
            pair_key = (sid, level)
            if pair_key not in seq_level_pairs:
                seq_level_pairs.add(pair_key)
                bipartite_edges.append({
                    "seq_id": sid,
                    "level": level,
                    "match_type": best["mt"],
                    "prime": best["p"],
                    "form_label": best["label"],
                    "entropy": best["ent"],
                    "window": best["w"],
                    "n_raw_matches": len(matches)
                })

    p(f"\nDeduplicated bipartite edges: {len(bipartite_edges)}")
    p(f"Unique sequences with edges: {len(set(e['seq_id'] for e in bipartite_edges))}")
    p(f"Unique levels with edges: {len(set(e['level'] for e in bipartite_edges))}")

    # ── 6. Family assignment ───────────────────────────────────────────
    bridge_family = {}
    for b in expansion_data.get("top_new_bridges", []):
        core, target = b["core"], b["match"]
        if core in SEQ_TO_FAMILY and target not in bridge_family:
            bridge_family[target] = SEQ_TO_FAMILY[core]

    def get_family(sid):
        if sid in SEQ_TO_FAMILY:
            return SEQ_TO_FAMILY[sid]
        return bridge_family.get(sid, "unknown")

    # ── 7. Monstrous-umbral meeting points ─────────────────────────────
    p("\n" + "=" * 70)
    p("MONSTROUS-UMBRAL MEETING POINTS")
    p("=" * 70)

    level_families = defaultdict(lambda: defaultdict(set))
    for e in bipartite_edges:
        fam = get_family(e["seq_id"])
        level_families[e["level"]][fam].add(e["seq_id"])

    meeting_points = []
    for level in sorted(level_families.keys()):
        fams = level_families[level]
        if "monstrous" in fams and "umbral" in fams:
            meeting_points.append({
                "level": level,
                "monstrous_seqs": sorted(fams["monstrous"]),
                "umbral_seqs": sorted(fams["umbral"]),
                "all_families": {k: sorted(v) for k, v in fams.items()},
                "n_families": len(fams)
            })

    p(f"\nLevels connecting BOTH monstrous and umbral: {len(meeting_points)}")
    for mp in meeting_points[:25]:
        p(f"  Level {mp['level']}: monstrous={mp['monstrous_seqs']}, "
          f"umbral={mp['umbral_seqs']}, families={list(mp['all_families'].keys())}")

    multi_family_levels = []
    for level in sorted(level_families.keys()):
        fams = level_families[level]
        if len(fams) >= 3:
            multi_family_levels.append({
                "level": level,
                "n_families": len(fams),
                "families": {k: sorted(v) for k, v in fams.items()}
            })
    multi_family_levels.sort(key=lambda x: (-x["n_families"], x["level"]))

    p(f"\nLevels spanning 3+ families: {len(multi_family_levels)}")
    for mf in multi_family_levels[:20]:
        p(f"  Level {mf['level']}: {mf['n_families']} families = "
          f"{list(mf['families'].keys())}")

    # ── 8. Graph statistics ────────────────────────────────────────────
    p("\n" + "=" * 70)
    p("GRAPH STATISTICS")
    p("=" * 70)

    seq_to_levels = defaultdict(set)
    level_to_seqs = defaultdict(set)
    for e in bipartite_edges:
        seq_to_levels[e["seq_id"]].add(e["level"])
        level_to_seqs[e["level"]].add(e["seq_id"])

    seq_degrees = {s: len(lvls) for s, lvls in seq_to_levels.items()}
    level_degrees = {l: len(seqs) for l, seqs in level_to_seqs.items()}

    n_side_a = len(seq_degrees)
    n_side_b = len(level_degrees)
    n_edges = len(bipartite_edges)

    density = n_edges / (n_side_a * n_side_b) if (n_side_a > 0 and n_side_b > 0) else 0

    p(f"\n|Side A| (moonshine sequences): {n_side_a}")
    p(f"|Side B| (Hecke levels): {n_side_b}")
    p(f"|Edges|: {n_edges}")
    p(f"Density: {density:.6f}")

    seq_deg_values = sorted(seq_degrees.values(), reverse=True) if seq_degrees else []
    level_deg_values = sorted(level_degrees.values(), reverse=True) if level_degrees else []

    if seq_deg_values:
        p(f"Mean degree Side A: {np.mean(seq_deg_values):.2f}")
        p(f"Mean degree Side B: {np.mean(level_deg_values):.2f}")

    # Hub sequences
    p("\nTop Hub Moonshine Sequences (highest degree):")
    for sid, deg in sorted(seq_degrees.items(), key=lambda x: -x[1])[:20]:
        fam = get_family(sid)
        p(f"  {sid} ({fam}): degree={deg}")

    # Hub levels
    p("\nTop Hub Hecke Levels (highest degree):")
    for lvl, deg in sorted(level_degrees.items(), key=lambda x: -x[1])[:20]:
        fams_at_level = sorted({get_family(s) for s in level_to_seqs[lvl]})
        p(f"  Level {lvl}: degree={deg}, families={fams_at_level}")

    # Degree distributions
    p(f"\nSide A degree distribution:")
    if seq_deg_values:
        p(f"  min={min(seq_deg_values)}, max={max(seq_deg_values)}, "
          f"median={np.median(seq_deg_values):.0f}, "
          f"mean={np.mean(seq_deg_values):.1f}, std={np.std(seq_deg_values):.1f}")
    p(f"Side B degree distribution:")
    if level_deg_values:
        p(f"  min={min(level_deg_values)}, max={max(level_deg_values)}, "
          f"median={np.median(level_deg_values):.0f}, "
          f"mean={np.mean(level_deg_values):.1f}, std={np.std(level_deg_values):.1f}")

    # ── 9. Bipartite clustering coefficient ────────────────────────────
    p("\nComputing bipartite clustering (Latapy)...")
    # For each Side-A node u: fraction of neighbor-pair co-adjacencies
    cc_values = []
    for sid in seq_to_levels:
        nbrs = list(seq_to_levels[sid])
        if len(nbrs) < 2:
            cc_values.append(0.0)
            continue
        # Sample if too many neighbors
        if len(nbrs) > 200:
            nbrs = list(np.random.choice(nbrs, 200, replace=False))
        total_pairs = 0
        shared_pairs = 0
        for i in range(len(nbrs)):
            for j in range(i+1, min(i+50, len(nbrs))):
                total_pairs += 1
                # Two levels share a neighbor if some sequence connects to both
                if level_to_seqs[nbrs[i]] & level_to_seqs[nbrs[j]]:
                    shared_pairs += 1
        cc_values.append(shared_pairs / total_pairs if total_pairs > 0 else 0)

    avg_cc = float(np.mean(cc_values)) if cc_values else 0
    p(f"Average bipartite clustering (Side A): {avg_cc:.4f}")

    # ── 10. Random comparison ──────────────────────────────────────────
    p("\n" + "=" * 70)
    p("RANDOM COMPARISON")
    p("=" * 70)

    n_mc = 500
    np.random.seed(42)
    all_levels_arr = np.array(sorted(level_to_seqs.keys()))
    all_seqs_sorted = sorted(seq_to_levels.keys())
    seq_deg_arr = np.array([len(seq_to_levels[s]) for s in all_seqs_sorted])
    seq_fam_arr = [get_family(s) for s in all_seqs_sorted]

    mc_meetings = []
    for trial in range(n_mc):
        rand_level_fams = defaultdict(set)
        for idx, sid in enumerate(all_seqs_sorted):
            n_lvl = min(seq_deg_arr[idx], len(all_levels_arr))
            chosen = np.random.choice(all_levels_arr, size=n_lvl, replace=False)
            fam = seq_fam_arr[idx]
            for rl in chosen:
                rand_level_fams[rl].add(fam)
        n_meet = sum(1 for fams in rand_level_fams.values()
                     if "monstrous" in fams and "umbral" in fams)
        mc_meetings.append(n_meet)

    mc_mean = float(np.mean(mc_meetings))
    mc_std = float(np.std(mc_meetings))
    actual_meetings = len(meeting_points)
    z_score = (actual_meetings - mc_mean) / mc_std if mc_std > 0 else 0

    p(f"\nMeeting points (monstrous-umbral):")
    p(f"  Actual: {actual_meetings}")
    p(f"  Random null ({n_mc} MC): mean={mc_mean:.1f}, std={mc_std:.1f}")
    p(f"  Z-score: {z_score:.2f}")
    verdict = "ENRICHED" if z_score > 2 else "DEPLETED" if z_score < -2 else "CONSISTENT WITH RANDOM"
    p(f"  Verdict: {verdict}")

    # Also compare degree variance
    if n_side_a > 0 and n_side_b > 0:
        p_rand = n_edges / (n_side_a * n_side_b)
        expected_var_a = n_side_b * p_rand * (1 - p_rand)
        expected_var_b = n_side_a * p_rand * (1 - p_rand)
        actual_var_a = float(np.var(list(seq_degrees.values())))
        actual_var_b = float(np.var(list(level_degrees.values())))

        p(f"\nDegree variance comparison (actual / ER-expected):")
        if expected_var_a > 0:
            p(f"  Side A: {actual_var_a:.1f} / {expected_var_a:.1f} = {actual_var_a/expected_var_a:.1f}x")
        if expected_var_b > 0:
            p(f"  Side B: {actual_var_b:.1f} / {expected_var_b:.1f} = {actual_var_b/expected_var_b:.1f}x")

    # ── 11. Match type breakdown ───────────────────────────────────────
    p("\n" + "=" * 70)
    p("MATCH TYPE BREAKDOWN")
    p("=" * 70)

    match_type_counts = Counter(e["match_type"] for e in bipartite_edges)
    for mt, cnt in match_type_counts.most_common():
        p(f"  {mt}: {cnt} edges ({100*cnt/n_edges:.1f}%)" if n_edges > 0 else f"  {mt}: {cnt}")

    # Exact-only sub-graph stats
    exact_edges = [e for e in bipartite_edges if e["match_type"] == "exact"]
    p(f"\nExact-match sub-graph:")
    exact_seqs = set(e["seq_id"] for e in exact_edges)
    exact_levels = set(e["level"] for e in exact_edges)
    p(f"  |Edges|={len(exact_edges)}, |Seqs|={len(exact_seqs)}, |Levels|={len(exact_levels)}")

    # Exact meeting points
    exact_level_fams = defaultdict(lambda: defaultdict(set))
    for e in exact_edges:
        fam = get_family(e["seq_id"])
        exact_level_fams[e["level"]][fam].add(e["seq_id"])
    exact_meetings = [lvl for lvl in exact_level_fams
                      if "monstrous" in exact_level_fams[lvl]
                      and "umbral" in exact_level_fams[lvl]]
    p(f"  Monstrous-umbral meetings (exact only): {len(exact_meetings)}")
    for lvl in sorted(exact_meetings)[:10]:
        p(f"    Level {lvl}: monstrous={sorted(exact_level_fams[lvl].get('monstrous',set()))}, "
          f"umbral={sorted(exact_level_fams[lvl].get('umbral',set()))}")

    # ── 12. Compile results ────────────────────────────────────────────
    results = {
        "summary": {
            "n_side_a_sequences": n_side_a,
            "n_side_b_levels": n_side_b,
            "n_edges": n_edges,
            "n_exact_edges": len(exact_edges),
            "density": round(density, 6),
            "n_meeting_points_monstrous_umbral": len(meeting_points),
            "n_exact_meeting_points": len(exact_meetings),
            "n_multi_family_levels": len(multi_family_levels),
            "avg_bipartite_clustering_a": round(avg_cc, 4),
            "match_type_breakdown": dict(match_type_counts),
            "random_comparison": {
                "mc_trials": n_mc,
                "mc_mean_meetings": round(mc_mean, 2),
                "mc_std_meetings": round(mc_std, 2),
                "actual_meetings": actual_meetings,
                "z_score": round(z_score, 2),
                "verdict": verdict,
            },
        },
        "meeting_points_monstrous_umbral": meeting_points[:50],
        "exact_meeting_points": sorted(exact_meetings)[:50],
        "multi_family_hub_levels": multi_family_levels[:30],
        "hub_sequences": [
            {"seq_id": sid, "family": get_family(sid), "degree": deg}
            for sid, deg in sorted(seq_degrees.items(), key=lambda x: -x[1])[:30]
        ],
        "hub_levels": [
            {"level": lvl, "degree": deg,
             "families": sorted({get_family(s) for s in level_to_seqs[lvl]})}
            for lvl, deg in sorted(level_degrees.items(), key=lambda x: -x[1])[:30]
        ],
        "degree_distribution_side_a": {
            "min": int(min(seq_deg_values)) if seq_deg_values else 0,
            "max": int(max(seq_deg_values)) if seq_deg_values else 0,
            "median": float(np.median(seq_deg_values)) if seq_deg_values else 0,
            "mean": round(float(np.mean(seq_deg_values)), 2) if seq_deg_values else 0,
            "std": round(float(np.std(seq_deg_values)), 2) if seq_deg_values else 0,
        },
        "degree_distribution_side_b": {
            "min": int(min(level_deg_values)) if level_deg_values else 0,
            "max": int(max(level_deg_values)) if level_deg_values else 0,
            "median": float(np.median(level_deg_values)) if level_deg_values else 0,
            "mean": round(float(np.mean(level_deg_values)), 2) if level_deg_values else 0,
            "std": round(float(np.std(level_deg_values)), 2) if level_deg_values else 0,
        },
        "family_partition": {k: v for k, v in MOONSHINE_PARTITION.items()},
        "all_edges_sample": sorted(bipartite_edges,
                                    key=lambda e: (0 if e["match_type"]=="exact" else 1,
                                                   -e["entropy"], e["level"]))[:200],
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    p(f"\nResults saved to {OUT_PATH}")
    p(f"Total time: {time.time()-t0:.1f}s")

    return results


if __name__ == "__main__":
    build_bipartite_graph()
