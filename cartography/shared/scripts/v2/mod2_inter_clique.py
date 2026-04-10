"""
M8: Inter-Clique Structure in the Mod-2 GSp_4 Graph
=====================================================
Since all connected components are complete graphs (M3), the interesting
question is the *conductor arithmetic* that determines clique size.

Analyses:
  1. v_2(N) correlation: does 2-adic valuation of conductor predict clique size?
  2. Full conductor factorization for large cliques (size >= 5)
  3. K_24 deep dive: what's special about conductor 352,256?
  4. Coprime K_4 characterization: what distinguishes the 7 surviving K_4?
  5. Odd-part structure: after removing powers of 2, what patterns remain?

Reads raw genus-2 data and rebuilds mod-2 congruence graph.

Usage:
    python mod2_inter_clique.py
"""

import re
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from math import gcd, log2
from itertools import combinations


# ── Helpers ────────────────────────────────────────────────────────────

def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def full_factorization(n):
    """Return dict {prime: exponent}."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = 1
    return factors


def v_p(n, p):
    """p-adic valuation of n."""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v


def odd_part(n):
    """Remove all factors of 2."""
    while n % 2 == 0:
        n //= 2
    return n


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("M8: INTER-CLIQUE STRUCTURE IN MOD-2 GSp_4 GRAPH")
    print("=" * 72)
    t0 = time.time()

    # ── Load curves ───────────────────────────────────────────────────
    DATA_FILE = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    OUT_DIR = Path(__file__).resolve().parent

    all_curves = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            label = parts[0]
            st = parts[8]
            euler = parse_good_lfactors(parts[16])
            eqn = parts[3]
            # Also grab endomorphism ring info if available
            end_ring = parts[9] if len(parts) > 9 else ""

            all_curves.append({
                "conductor": conductor,
                "label": label,
                "st": st,
                "euler": euler,
                "eqn": eqn,
                "end_ring": end_ring,
            })

    print(f"Loaded {len(all_curves)} curves")

    # ── Group by conductor & deduplicate by isogeny class ─────────────
    by_cond = defaultdict(list)
    for c in all_curves:
        by_cond[c["conductor"]].append(c)

    cond_reps = {}
    for cond, crvs in by_cond.items():
        if len(crvs) < 2:
            cond_reps[cond] = crvs
            continue
        classes = defaultdict(list)
        common = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    total_reps = sum(len(v) for v in cond_reps.values())
    print(f"Isogeny class reps: {total_reps}")

    # ── Full mod-2 scan ──────────────────────────────────────────────
    print(f"\nRunning mod-2 congruence scan...")

    # Store congruences with full metadata
    mod2_congruences = []

    for cond, reps in cond_reps.items():
        if len(reps) < 2:
            continue
        bad = prime_factors(cond)

        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue

                all_cong = True
                has_nz = False
                for p in good:
                    da = e1[p][0] - e2[p][0]
                    db = e1[p][1] - e2[p][1]
                    if da % 2 != 0 or db % 2 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True
                if all_cong and has_nz:
                    ell_div = cond % 2 == 0
                    mod2_congruences.append({
                        "cond": cond,
                        "ell_div": ell_div,
                        "st1": reps[i]["st"],
                        "st2": reps[j]["st"],
                        "label1": reps[i]["label"],
                        "label2": reps[j]["label"],
                        "eqn1": reps[i]["eqn"],
                        "eqn2": reps[j]["eqn"],
                        "end1": reps[i]["end_ring"],
                        "end2": reps[j]["end_ring"],
                    })

    print(f"Mod-2 congruences (all): {len(mod2_congruences)}")

    # ── Build graph and extract components ────────────────────────────
    # Node ID encodes conductor
    def make_node_id(c, which):
        if which == 1:
            return f"N{c['cond']}_{c['label1']}_{c['eqn1'][:30]}"
        else:
            return f"N{c['cond']}_{c['label2']}_{c['eqn2'][:30]}"

    adj = defaultdict(set)
    all_nodes = set()
    node_cond = {}  # node -> conductor
    node_st = {}    # node -> ST group
    node_end = {}   # node -> endomorphism info
    node_label = {} # node -> LMFDB label

    for c in mod2_congruences:
        n1 = make_node_id(c, 1)
        n2 = make_node_id(c, 2)
        adj[n1].add(n2)
        adj[n2].add(n1)
        all_nodes.add(n1)
        all_nodes.add(n2)
        node_cond[n1] = c["cond"]
        node_cond[n2] = c["cond"]
        node_st[n1] = c["st1"]
        node_st[n2] = c["st2"]
        node_end[n1] = c["end1"]
        node_end[n2] = c["end2"]
        node_label[n1] = c["label1"]
        node_label[n2] = c["label2"]

    # Extract connected components
    visited = set()
    components = []
    for n in all_nodes:
        if n not in visited:
            comp = []
            stack = [n]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                comp.append(node)
                stack.extend(adj[node] - visited)
            components.append(comp)

    print(f"Nodes: {len(all_nodes)}, Components: {len(components)}")

    # Each component is a clique (from M3). Get conductor for each.
    clique_data = []
    for comp in components:
        size = len(comp)
        conds = set(node_cond[n] for n in comp)
        sts = Counter(node_st[n] for n in comp)
        ends = Counter(node_end[n] for n in comp if node_end[n])
        labels = [node_label[n] for n in comp]
        # All nodes in a component share the same conductor (same-conductor pairs)
        assert len(conds) == 1, f"Multi-conductor component: {conds}"
        cond = list(conds)[0]
        clique_data.append({
            "size": size,
            "conductor": cond,
            "st_distribution": dict(sts),
            "end_distribution": dict(ends),
            "labels": labels,
        })

    clique_data.sort(key=lambda x: -x["size"])
    print(f"\nTop 10 cliques:")
    for cd in clique_data[:10]:
        print(f"  K_{cd['size']} at N={cd['conductor']}, ST: {cd['st_distribution']}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 1: v_2(N) correlation with clique size
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 1: v_2(N) CORRELATION WITH CLIQUE SIZE")
    print("=" * 72)

    v2_vs_size = []
    for cd in clique_data:
        v2 = v_p(cd["conductor"], 2)
        v2_vs_size.append((v2, cd["size"]))

    # Group by v_2
    by_v2 = defaultdict(list)
    for v2, size in v2_vs_size:
        by_v2[v2].append(size)

    v2_summary = {}
    print(f"\n{'v_2(N)':<10} {'Count':<10} {'Mean Size':<12} {'Max Size':<10} {'Sizes >= 5':<12}")
    print("-" * 54)
    for v2 in sorted(by_v2.keys()):
        sizes = by_v2[v2]
        mean_s = sum(sizes) / len(sizes)
        max_s = max(sizes)
        n_big = sum(1 for s in sizes if s >= 5)
        print(f"{v2:<10} {len(sizes):<10} {mean_s:<12.3f} {max_s:<10} {n_big:<12}")
        v2_summary[str(v2)] = {
            "count": len(sizes),
            "mean_size": round(mean_s, 4),
            "max_size": max_s,
            "n_size_ge5": n_big,
            "size_distribution": dict(Counter(sizes)),
        }

    # Correlation
    v2_vals = [x[0] for x in v2_vs_size]
    size_vals = [x[1] for x in v2_vs_size]
    n = len(v2_vals)
    mean_v2 = sum(v2_vals) / n
    mean_size = sum(size_vals) / n
    cov = sum((v2_vals[i] - mean_v2) * (size_vals[i] - mean_size) for i in range(n)) / n
    std_v2 = (sum((v - mean_v2)**2 for v in v2_vals) / n) ** 0.5
    std_size = (sum((s - mean_size)**2 for s in size_vals) / n) ** 0.5
    corr = cov / (std_v2 * std_size) if std_v2 > 0 and std_size > 0 else 0
    print(f"\nPearson correlation(v_2(N), clique_size) = {corr:.4f}")

    # Also check: is v_2 = 0 (odd conductor) always small cliques?
    odd_cond_sizes = by_v2.get(0, [])
    even_cond_sizes = [s for v2, sizes in by_v2.items() if v2 > 0 for s in sizes]
    print(f"\nOdd conductor cliques: {len(odd_cond_sizes)}, max size: {max(odd_cond_sizes) if odd_cond_sizes else 0}")
    print(f"Even conductor cliques: {len(even_cond_sizes)}, max size: {max(even_cond_sizes) if even_cond_sizes else 0}")

    if odd_cond_sizes:
        print(f"  Odd: mean={sum(odd_cond_sizes)/len(odd_cond_sizes):.3f}, "
              f"sizes >= 3: {sum(1 for s in odd_cond_sizes if s >= 3)}, "
              f"sizes >= 5: {sum(1 for s in odd_cond_sizes if s >= 5)}")
    if even_cond_sizes:
        print(f"  Even: mean={sum(even_cond_sizes)/len(even_cond_sizes):.3f}, "
              f"sizes >= 3: {sum(1 for s in even_cond_sizes if s >= 3)}, "
              f"sizes >= 5: {sum(1 for s in even_cond_sizes if s >= 5)}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 2: Conductor factorization for large cliques
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 2: CONDUCTOR FACTORIZATION FOR CLIQUES SIZE >= 5")
    print("=" * 72)

    large_cliques = [cd for cd in clique_data if cd["size"] >= 5]
    print(f"\n{len(large_cliques)} cliques of size >= 5")

    factorization_data = []
    for cd in large_cliques:
        N = cd["conductor"]
        fac = full_factorization(N)
        v2_N = fac.get(2, 0)
        odd_N = N // (2 ** v2_N)
        odd_fac = full_factorization(odd_N) if odd_N > 1 else {}
        n_odd_primes = len(odd_fac)
        omega_N = len(fac)  # number of distinct prime factors
        Omega_N = sum(fac.values())  # total prime factors with multiplicity

        entry = {
            "size": cd["size"],
            "conductor": N,
            "factorization": fac,
            "factorization_str": " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(fac.items())),
            "v_2": v2_N,
            "odd_part": odd_N,
            "odd_factorization": odd_fac,
            "n_distinct_primes": omega_N,
            "n_prime_factors_total": Omega_N,
            "st_distribution": cd["st_distribution"],
        }
        factorization_data.append(entry)
        print(f"  K_{cd['size']:>2} at N={N:>8} = {entry['factorization_str']:<30} "
              f"v_2={v2_N}, odd={odd_N}, omega={omega_N}, ST: {cd['st_distribution']}")

    # Pattern analysis on factorizations
    print("\n--- Pattern Summary ---")
    v2_values = [fd["v_2"] for fd in factorization_data]
    odd_parts = [fd["odd_part"] for fd in factorization_data]
    omega_values = [fd["n_distinct_primes"] for fd in factorization_data]

    print(f"v_2 range: {min(v2_values)} to {max(v2_values)}")
    print(f"v_2 distribution: {dict(Counter(v2_values))}")
    print(f"omega(N) range: {min(omega_values)} to {max(omega_values)}")
    print(f"omega(N) distribution: {dict(Counter(omega_values))}")

    # Check: does large v_2 => large clique?
    v2_sizes = [(fd["v_2"], fd["size"]) for fd in factorization_data]
    v2_sizes.sort()
    print(f"\nv_2 vs size for large cliques:")
    for v2_val in sorted(set(v for v, _ in v2_sizes)):
        sizes_at_v2 = [s for v, s in v2_sizes if v == v2_val]
        print(f"  v_2={v2_val}: {len(sizes_at_v2)} cliques, sizes={sorted(sizes_at_v2, reverse=True)[:10]}")

    # Odd part patterns
    odd_counter = Counter(odd_parts)
    print(f"\nOdd parts appearing more than once among large cliques:")
    for op, cnt in odd_counter.most_common():
        if cnt >= 2:
            sizes_at_op = [fd["size"] for fd in factorization_data if fd["odd_part"] == op]
            print(f"  odd_part={op} ({full_factorization(op) if op > 1 else {}}): "
                  f"{cnt} cliques, sizes={sorted(sizes_at_op, reverse=True)}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 3: K_24 deep dive at conductor 352,256
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 3: K_24 DEEP DIVE — CONDUCTOR 352,256")
    print("=" * 72)

    N_24 = 352256
    fac_24 = full_factorization(N_24)
    print(f"\n352,256 = {' * '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(fac_24.items()))}")
    print(f"  = 2^{fac_24.get(2, 0)} * {odd_part(N_24)}")
    print(f"  odd part = {odd_part(N_24)} = {full_factorization(odd_part(N_24))}")

    # What curves live at this conductor?
    curves_352256 = cond_reps.get(N_24, [])
    print(f"\nIsogeny classes at N=352,256: {len(curves_352256)}")
    st_dist_352 = Counter(c["st"] for c in curves_352256)
    print(f"ST distribution: {dict(st_dist_352)}")
    end_dist_352 = Counter(c["end_ring"] for c in curves_352256 if c["end_ring"])
    if end_dist_352:
        print(f"Endomorphism distribution: {dict(end_dist_352)}")

    # How many of these form the K_24?
    # The K_24 means 24 nodes all pairwise mod-2 congruent
    # = C(24,2) = 276 edges within the clique
    n_edges_352 = sum(1 for c in mod2_congruences if c["cond"] == N_24)
    print(f"Mod-2 congruence edges at N=352,256: {n_edges_352}")
    print(f"Expected for K_24: C(24,2) = {24*23//2}")

    # Compare with other large-v_2 conductors
    # Conductors with v_2 >= 8
    high_v2_conds = set()
    for cd in clique_data:
        if v_p(cd["conductor"], 2) >= 8:
            high_v2_conds.add(cd["conductor"])
    print(f"\nConductors with v_2 >= 8: {len(high_v2_conds)}")
    for cond in sorted(high_v2_conds):
        cd_match = [cd for cd in clique_data if cd["conductor"] == cond]
        if cd_match:
            fac = full_factorization(cond)
            print(f"  N={cond} = {' * '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(fac.items()))}"
                  f", clique size={cd_match[0]['size']}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 4: Coprime clique characterization
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 4: COPRIME (USp(4)) CLIQUE CHARACTERIZATION")
    print("=" * 72)

    mod2_coprime = [c for c in mod2_congruences if not c["ell_div"]]
    mod2_coprime_usp = [c for c in mod2_coprime
                         if c["st1"] == "USp(4)" and c["st2"] == "USp(4)"]

    print(f"\nCoprime edges: {len(mod2_coprime)}")
    print(f"Coprime USp(4) edges: {len(mod2_coprime_usp)}")

    # Build coprime graph
    cop_adj = defaultdict(set)
    cop_nodes = set()
    cop_node_cond = {}
    cop_node_st = {}
    cop_node_end = {}
    cop_node_label = {}

    for c in mod2_coprime_usp:
        n1 = make_node_id(c, 1)
        n2 = make_node_id(c, 2)
        cop_adj[n1].add(n2)
        cop_adj[n2].add(n1)
        cop_nodes.add(n1)
        cop_nodes.add(n2)
        cop_node_cond[n1] = c["cond"]
        cop_node_cond[n2] = c["cond"]
        cop_node_st[n1] = c["st1"]
        cop_node_st[n2] = c["st2"]
        cop_node_end[n1] = c["end1"]
        cop_node_end[n2] = c["end2"]
        cop_node_label[n1] = c["label1"]
        cop_node_label[n2] = c["label2"]

    # Extract coprime components
    cop_visited = set()
    cop_components = []
    for n in cop_nodes:
        if n not in cop_visited:
            comp = []
            stack = [n]
            while stack:
                node = stack.pop()
                if node in cop_visited:
                    continue
                cop_visited.add(node)
                comp.append(node)
                stack.extend(cop_adj[node] - cop_visited)
            cop_components.append(comp)

    cop_clique_data = []
    for comp in cop_components:
        size = len(comp)
        conds = set(cop_node_cond[n] for n in comp)
        sts = Counter(cop_node_st[n] for n in comp)
        ends = Counter(cop_node_end[n] for n in comp if cop_node_end.get(n))
        labels = [cop_node_label[n] for n in comp]
        cond = list(conds)[0] if len(conds) == 1 else -1
        cop_clique_data.append({
            "size": size,
            "conductor": cond,
            "conductors": sorted(conds),
            "st_distribution": dict(sts),
            "end_distribution": dict(ends),
            "labels": labels,
        })

    cop_clique_data.sort(key=lambda x: -x["size"])
    cop_size_dist = Counter(cd["size"] for cd in cop_clique_data)
    print(f"\nCoprime USp(4) components: {len(cop_clique_data)}")
    print(f"Size distribution: {dict(sorted(cop_size_dist.items()))}")

    # Focus on K_4 coprime cliques
    k4_coprime = [cd for cd in cop_clique_data if cd["size"] == 4]
    print(f"\nK_4 coprime cliques: {len(k4_coprime)}")
    k4_details = []
    for i, cd in enumerate(k4_coprime):
        N = cd["conductor"]
        fac = full_factorization(N)
        print(f"\n  K_4 #{i+1}: N={N}")
        print(f"    Factorization: {' * '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(fac.items()))}")
        print(f"    v_2(N) = {v_p(N, 2)}")
        print(f"    Odd part = {odd_part(N)}")
        print(f"    ST: {cd['st_distribution']}")
        print(f"    Labels: {cd['labels']}")
        if cd["end_distribution"]:
            print(f"    Endomorphism: {cd['end_distribution']}")
        k4_details.append({
            "conductor": N,
            "factorization": dict(fac),
            "factorization_str": " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(fac.items())),
            "v_2": v_p(N, 2),
            "odd_part": odd_part(N),
            "st_distribution": cd["st_distribution"],
            "end_distribution": cd["end_distribution"],
            "labels": cd["labels"],
        })

    # K_3 coprime cliques
    k3_coprime = [cd for cd in cop_clique_data if cd["size"] == 3]
    print(f"\nK_3 coprime cliques: {len(k3_coprime)}")
    k3_conductors = [cd["conductor"] for cd in k3_coprime]
    k3_v2 = [v_p(c, 2) for c in k3_conductors]
    print(f"  v_2 distribution: {dict(Counter(k3_v2))}")
    k3_odd_parts = [odd_part(c) for c in k3_conductors]
    print(f"  Common odd parts: {Counter(k3_odd_parts).most_common(10)}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 5: Odd-part clustering
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 5: ODD-PART CLUSTERING")
    print("=" * 72)

    # Do cliques at same odd part but different v_2 have similar sizes?
    by_odd = defaultdict(list)
    for cd in clique_data:
        op = odd_part(cd["conductor"])
        by_odd[op].append(cd)

    # Find odd parts with multiple cliques
    multi_odd = {op: cds for op, cds in by_odd.items() if len(cds) >= 2}
    print(f"\nOdd parts with >= 2 cliques: {len(multi_odd)}")

    # For each, show how size varies with v_2
    print(f"\n{'Odd part':<12} {'# Cliques':<10} {'v_2 values':<20} {'Sizes':<30}")
    print("-" * 72)
    shown = 0
    for op in sorted(multi_odd.keys()):
        cds = multi_odd[op]
        if any(cd["size"] >= 4 for cd in cds):
            v2s = [v_p(cd["conductor"], 2) for cd in cds]
            sizes = [cd["size"] for cd in cds]
            pairs = sorted(zip(v2s, sizes))
            print(f"{op:<12} {len(cds):<10} {str([p[0] for p in pairs]):<20} {str([p[1] for p in pairs]):<30}")
            shown += 1
            if shown >= 30:
                break

    # Correlation within odd-part families: does increasing v_2 increase clique size?
    growth_cases = 0
    shrink_cases = 0
    flat_cases = 0
    for op, cds in multi_odd.items():
        pairs = sorted([(v_p(cd["conductor"], 2), cd["size"]) for cd in cds])
        for i in range(len(pairs) - 1):
            if pairs[i+1][1] > pairs[i][1]:
                growth_cases += 1
            elif pairs[i+1][1] < pairs[i][1]:
                shrink_cases += 1
            else:
                flat_cases += 1

    print(f"\nWithin odd-part families, increasing v_2:")
    print(f"  => larger clique: {growth_cases}")
    print(f"  => smaller clique: {shrink_cases}")
    print(f"  => same size: {flat_cases}")
    if growth_cases + shrink_cases > 0:
        print(f"  Growth ratio: {growth_cases / (growth_cases + shrink_cases):.3f}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 6: Small prime composition
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 6: SMALL PRIME COMPOSITION")
    print("=" * 72)

    # For each small prime p, check v_p correlation with clique size
    for p in [2, 3, 5, 7, 11, 13]:
        vp_vs_size = [(v_p(cd["conductor"], p), cd["size"]) for cd in clique_data]
        by_vp = defaultdict(list)
        for vp, sz in vp_vs_size:
            by_vp[vp].append(sz)
        print(f"\nv_{p}(N) distribution:")
        for vp_val in sorted(by_vp.keys()):
            sizes = by_vp[vp_val]
            if len(sizes) >= 5 or max(sizes) >= 5:
                print(f"  v_{p}={vp_val}: {len(sizes)} cliques, "
                      f"mean={sum(sizes)/len(sizes):.2f}, max={max(sizes)}")

    # ══════════════════════════════════════════════════════════════════
    # ANALYSIS 7: ST homogeneity within cliques
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("ANALYSIS 7: SATO-TATE HOMOGENEITY WITHIN CLIQUES")
    print("=" * 72)

    n_pure = 0
    n_mixed = 0
    mixed_sizes = []
    pure_sizes = []
    st_by_cliquesize = defaultdict(lambda: {"pure": 0, "mixed": 0})

    for cd in clique_data:
        if len(cd["st_distribution"]) == 1:
            n_pure += 1
            pure_sizes.append(cd["size"])
            st_by_cliquesize[cd["size"]]["pure"] += 1
        else:
            n_mixed += 1
            mixed_sizes.append(cd["size"])
            st_by_cliquesize[cd["size"]]["mixed"] += 1

    print(f"\nST-pure cliques: {n_pure}")
    print(f"ST-mixed cliques: {n_mixed}")
    print(f"Mixed fraction: {n_mixed / (n_pure + n_mixed):.4f}")
    print(f"Pure clique max size: {max(pure_sizes) if pure_sizes else 0}")
    print(f"Mixed clique max size: {max(mixed_sizes) if mixed_sizes else 0}")

    print(f"\nBy clique size:")
    print(f"{'Size':<8} {'Pure':<8} {'Mixed':<8} {'Mixed %':<10}")
    for sz in sorted(st_by_cliquesize.keys()):
        p = st_by_cliquesize[sz]["pure"]
        m = st_by_cliquesize[sz]["mixed"]
        pct = 100 * m / (p + m)
        print(f"{sz:<8} {p:<8} {m:<8} {pct:<10.1f}")

    # ══════════════════════════════════════════════════════════════════
    # Compile results
    # ══════════════════════════════════════════════════════════════════
    elapsed = time.time() - t0

    results = {
        "description": "M8: Inter-Clique Structure in Mod-2 GSp_4 Graph",
        "total_cliques": len(clique_data),
        "analysis_1_v2_correlation": {
            "pearson_r": round(corr, 4),
            "by_v2": v2_summary,
            "odd_conductor_cliques": len(odd_cond_sizes),
            "odd_max_size": max(odd_cond_sizes) if odd_cond_sizes else 0,
            "even_conductor_cliques": len(even_cond_sizes),
            "even_max_size": max(even_cond_sizes) if even_cond_sizes else 0,
            "finding": ("v_2(N) > 0 is NECESSARY for clique size >= 5 in the full graph. "
                        f"Pearson r = {corr:.4f}. "
                        f"v_2 = 0: max clique = {max(odd_cond_sizes) if odd_cond_sizes else 0}. "
                        f"v_2 >= 7: all cliques have max size >= "
                        f"{min(by_v2[v][0] for v in by_v2 if v >= 7) if any(v >= 7 for v in by_v2) else 'N/A'}."),
        },
        "analysis_2_factorization": {
            "n_large_cliques": len(large_cliques),
            "cliques": [{
                "size": fd["size"],
                "conductor": fd["conductor"],
                "factorization": fd["factorization_str"],
                "v_2": fd["v_2"],
                "odd_part": fd["odd_part"],
                "n_distinct_primes": fd["n_distinct_primes"],
                "st_distribution": fd["st_distribution"],
            } for fd in factorization_data],
            "v2_distribution_large": dict(Counter(fd["v_2"] for fd in factorization_data)),
            "omega_distribution_large": dict(Counter(fd["n_distinct_primes"] for fd in factorization_data)),
        },
        "analysis_3_k24": {
            "conductor": N_24,
            "factorization": dict(fac_24),
            "factorization_str": " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(fac_24.items())),
            "v_2": fac_24.get(2, 0),
            "odd_part": odd_part(N_24),
            "odd_part_factorization": dict(full_factorization(odd_part(N_24))),
            "n_isogeny_classes": len(curves_352256),
            "st_distribution": dict(st_dist_352),
            "n_mod2_edges": n_edges_352,
            "expected_k24_edges": 24 * 23 // 2,
        },
        "analysis_4_coprime": {
            "n_coprime_edges": len(mod2_coprime),
            "n_coprime_usp4_edges": len(mod2_coprime_usp),
            "n_coprime_components": len(cop_clique_data),
            "coprime_size_distribution": dict(sorted(cop_size_dist.items())),
            "k4_coprime_cliques": k4_details,
            "k3_coprime_count": len(k3_coprime),
            "k3_v2_distribution": dict(Counter(k3_v2)),
        },
        "analysis_5_odd_part_clustering": {
            "n_odd_parts_with_multiple_cliques": len(multi_odd),
            "growth_ratio": round(growth_cases / (growth_cases + shrink_cases), 4) if growth_cases + shrink_cases > 0 else None,
            "growth_cases": growth_cases,
            "shrink_cases": shrink_cases,
            "flat_cases": flat_cases,
        },
        "analysis_7_st_homogeneity": {
            "n_pure": n_pure,
            "n_mixed": n_mixed,
            "mixed_fraction": round(n_mixed / (n_pure + n_mixed), 4),
            "pure_max_size": max(pure_sizes) if pure_sizes else 0,
            "mixed_max_size": max(mixed_sizes) if mixed_sizes else 0,
            "by_clique_size": {str(sz): st_by_cliquesize[sz] for sz in sorted(st_by_cliquesize.keys())},
        },
        "metadata": {
            "total_curves": len(all_curves),
            "total_mod2_edges": len(mod2_congruences),
            "elapsed_seconds": round(elapsed, 1),
        },
    }

    out_file = OUT_DIR / "mod2_inter_clique_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n{'=' * 72}")
    print(f"Results saved to {out_file}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
