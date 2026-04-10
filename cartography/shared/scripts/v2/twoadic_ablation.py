"""
OSC-4: Ablate the 2-Adic Camouflage
=====================================
Remove all even-conductor forms from the congruence graph and measure
whether the mod-2 camouflage evaporates or persists.

Key questions:
  - How much of the mod-2 neighborhood is just even-conductor forms?
  - Does the altitude gradient change shape after ablation?
  - Is this effect specific to 15.2.a.a or universal?
  - Is mod-2 camouflage a property of the FORM or of EVEN CONDUCTORS?
"""
import json, time, math, random
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "twoadic_ablation_results.json"

ELLS = [2, 3, 5, 7, 11, 13]
MIN_GOOD_PRIMES = 8
N_CONTROLS = 5


def sieve(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]


def prime_factors(n):
    f = set(); d = 2
    while d*d <= n:
        while n % d == 0: f.add(d); n //= d
        d += 1
    if n > 1: f.add(n)
    return f


def v2(n):
    """2-adic valuation of n."""
    if n == 0: return float('inf')
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def mod_ell_fingerprint(ap_int, ap_primes, bad_primes, ell, max_primes=20):
    """Compute mod-ell fingerprint: tuple of (a_p mod ell) at good primes."""
    fp = []
    for i, p in enumerate(ap_primes[:max_primes]):
        if i >= len(ap_int): break
        if p in bad_primes or p == ell: continue
        fp.append(ap_int[i] % ell)
    return tuple(fp)


def compute_clusters(forms_subset, ap_primes, ell):
    """Compute fingerprint clusters for a subset of forms."""
    clusters = defaultdict(list)
    fps = {}
    for label, fdata in forms_subset.items():
        fp = mod_ell_fingerprint(fdata["ap_int"], ap_primes, fdata["bad"], ell)
        if len(fp) >= MIN_GOOD_PRIMES:
            fps[label] = fp
            clusters[fp].append(label)
    return fps, clusters


def neighborhood_size(label, fps, clusters):
    """Count neighbors sharing the same fingerprint (excluding self)."""
    if label not in fps:
        return -1
    fp = fps[label]
    return len(clusters.get(fp, [])) - 1


def cluster_stats(clusters):
    """Summary statistics for a cluster map."""
    sizes = sorted([len(v) for v in clusters.values()], reverse=True)
    if not sizes:
        return {"n_clusters": 0, "max": 0, "singletons": 0, "singleton_frac": 0}
    return {
        "n_clusters": len(sizes),
        "max": sizes[0],
        "top_5": sizes[:5],
        "singletons": sum(1 for s in sizes if s == 1),
        "singleton_frac": round(sum(1 for s in sizes if s == 1) / len(sizes), 4),
    }


def main():
    t0 = time.time()
    print("=== OSC-4: Ablate the 2-Adic Camouflage ===\n")

    con = duckdb.connect(str(DB), read_only=True)
    all_rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms WHERE weight = 2 AND dim = 1 AND char_order = 1
    """).fetchall()
    con.close()
    print(f"[0] Loaded {len(all_rows)} forms from database")

    ap_primes = sieve(200)

    # Parse all forms
    forms = {}
    for label, level, ap_json, is_cm in all_rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_int = [int(x[0]) if isinstance(x, list) else int(x) for x in ap]
        bad = prime_factors(level)
        forms[label] = {
            "level": level, "ap_int": ap_int, "bad": bad,
            "is_cm": bool(is_cm), "v2_level": v2(level),
        }

    # =====================================================================
    # STEP 1: Separate by 2-adic valuation of conductor
    # =====================================================================
    print("\n[1] Separating by v_2(N)...")
    odd_forms = {l: f for l, f in forms.items() if f["v2_level"] == 0}
    even_forms = {l: f for l, f in forms.items() if f["v2_level"] >= 1}

    # Finer breakdown
    v2_distribution = Counter(f["v2_level"] for f in forms.values())

    print(f"  Total forms:          {len(forms)}")
    print(f"  Odd-conductor  (v2=0): {len(odd_forms)} ({100*len(odd_forms)/len(forms):.1f}%)")
    print(f"  Even-conductor (v2>=1): {len(even_forms)} ({100*len(even_forms)/len(forms):.1f}%)")
    print(f"  v_2(N) distribution:")
    for v, cnt in sorted(v2_distribution.items()):
        print(f"    v_2={v}: {cnt} forms ({100*cnt/len(forms):.1f}%)")

    # =====================================================================
    # STEP 2: Compute mod-ell neighborhoods in full vs ablated populations
    # =====================================================================
    TARGET = "15.2.a.a"
    if TARGET not in forms:
        print(f"ERROR: {TARGET} not found!")
        return

    target_v2 = forms[TARGET]["v2_level"]
    print(f"\n[2] Target: {TARGET} (level={forms[TARGET]['level']}, v2={target_v2})")

    # Full population clusters
    print("\n[2a] Full population neighborhoods...")
    full_neighborhoods = {}
    for ell in ELLS:
        fps, clusters = compute_clusters(forms, ap_primes, ell)
        n = neighborhood_size(TARGET, fps, clusters)
        full_neighborhoods[ell] = n
        stats = cluster_stats(clusters)
        print(f"  ell={ell}: N={n}, clusters={stats['n_clusters']}, "
              f"max={stats['max']}, singletons={stats['singletons']}")

    # Odd-conductor-only clusters
    print("\n[2b] Odd-conductor-only neighborhoods...")
    odd_neighborhoods = {}
    odd_cluster_data = {}
    for ell in ELLS:
        fps, clusters = compute_clusters(odd_forms, ap_primes, ell)
        n = neighborhood_size(TARGET, fps, clusters)
        odd_neighborhoods[ell] = n
        odd_cluster_data[ell] = {"fps": fps, "clusters": clusters}
        stats = cluster_stats(clusters)
        print(f"  ell={ell}: N={n}, clusters={stats['n_clusters']}, "
              f"max={stats['max']}, singletons={stats['singletons']}")

    # Even-conductor-only clusters
    print("\n[2c] Even-conductor-only neighborhoods...")
    even_neighborhoods = {}
    for ell in ELLS:
        fps_even, clusters_even = compute_clusters(even_forms, ap_primes, ell)
        # Check how many even-conductor forms share 15.2.a.a's fingerprint
        # 15.2.a.a is odd-conductor, so compute its fingerprint and check against even forms
        target_fp = mod_ell_fingerprint(
            forms[TARGET]["ap_int"], ap_primes, forms[TARGET]["bad"], ell
        )
        n_even_matches = sum(1 for l, fp in fps_even.items() if fp == target_fp)
        even_neighborhoods[ell] = n_even_matches
        print(f"  ell={ell}: {n_even_matches} even-conductor forms share 15.2.a.a's fingerprint")

    # =====================================================================
    # STEP 3: Camouflage decomposition
    # =====================================================================
    print("\n[3] Camouflage decomposition...")
    print(f"  {'ell':>4} | {'Full N':>8} | {'Odd-only N':>10} | {'Even matches':>12} | {'Even %':>8} | {'Evaporates?':>12}")
    print(f"  {'----':>4}-+-{'--------':>8}-+-{'----------':>10}-+-{'------------':>12}-+-{'--------':>8}-+-{'------------':>12}")

    decomposition = {}
    for ell in ELLS:
        full_n = full_neighborhoods[ell]
        odd_n = odd_neighborhoods[ell]
        even_n = even_neighborhoods[ell]
        even_pct = 100 * even_n / full_n if full_n > 0 else 0
        # "Evaporates" if odd-only N is dramatically smaller
        if full_n > 0 and odd_n >= 0:
            reduction = 100 * (1 - odd_n / full_n) if full_n > 0 else 0
            evaporates = "YES" if reduction > 80 else ("PARTIAL" if reduction > 50 else "NO")
        else:
            reduction = 0
            evaporates = "N/A"

        decomposition[str(ell)] = {
            "full_N": full_n,
            "odd_only_N": odd_n,
            "even_matches": even_n,
            "even_pct": round(even_pct, 1),
            "reduction_pct": round(reduction, 1),
            "evaporates": evaporates,
        }
        print(f"  {ell:>4} | {full_n:>8} | {odd_n:>10} | {even_n:>12} | {even_pct:>7.1f}% | {evaporates:>12}")

    # Verify: odd_n + even_n should equal full_n (or close, since fingerprints
    # can differ due to different bad primes)
    print(f"\n  Consistency check: odd_N + even_matches vs full_N")
    for ell in ELLS:
        s = odd_neighborhoods[ell] + even_neighborhoods[ell]
        f = full_neighborhoods[ell]
        print(f"    ell={ell}: {odd_neighborhoods[ell]} + {even_neighborhoods[ell]} = {s} vs {f} (diff={f - s})")

    # =====================================================================
    # STEP 4: Ablated altitude gradient for odd-conductor forms
    # =====================================================================
    print("\n[4] Altitude gradient comparison...")
    # Compute gradient shape: log2(N(ell)) vs ell
    print(f"  {'ell':>4} | {'log2(Full)':>10} | {'log2(Odd)':>10} | {'Ratio':>8}")
    print(f"  {'----':>4}-+-{'----------':>10}-+-{'----------':>10}-+-{'--------':>8}")
    gradient = {}
    for ell in ELLS:
        fn = full_neighborhoods[ell]
        on = odd_neighborhoods[ell]
        log_f = math.log2(fn) if fn > 0 else 0
        log_o = math.log2(on) if on > 0 else 0
        ratio = on / fn if fn > 0 and on >= 0 else 0
        gradient[str(ell)] = {
            "log2_full": round(log_f, 3),
            "log2_odd": round(log_o, 3),
            "ratio": round(ratio, 4),
        }
        print(f"  {ell:>4} | {log_f:>10.3f} | {log_o:>10.3f} | {ratio:>8.4f}")

    # =====================================================================
    # STEP 5: M8 connection — clique structure at odd conductors
    # =====================================================================
    print("\n[5] Mod-2 cluster structure: odd vs even conductors...")

    # Odd-conductor mod-2 cluster sizes
    _, odd_cl2 = compute_clusters(odd_forms, ap_primes, 2)
    _, even_cl2 = compute_clusters(even_forms, ap_primes, 2)
    _, full_cl2 = compute_clusters(forms, ap_primes, 2)

    odd_sizes = sorted([len(v) for v in odd_cl2.values()], reverse=True)
    even_sizes = sorted([len(v) for v in even_cl2.values()], reverse=True)
    full_sizes = sorted([len(v) for v in full_cl2.values()], reverse=True)

    clique_comparison = {
        "full": {
            "n_clusters": len(full_sizes),
            "max": full_sizes[0] if full_sizes else 0,
            "top_10": full_sizes[:10],
            "mean_size": round(float(np.mean(full_sizes)), 2) if full_sizes else 0,
            "ge5": sum(1 for s in full_sizes if s >= 5),
        },
        "odd_only": {
            "n_clusters": len(odd_sizes),
            "max": odd_sizes[0] if odd_sizes else 0,
            "top_10": odd_sizes[:10],
            "mean_size": round(float(np.mean(odd_sizes)), 2) if odd_sizes else 0,
            "ge5": sum(1 for s in odd_sizes if s >= 5),
        },
        "even_only": {
            "n_clusters": len(even_sizes),
            "max": even_sizes[0] if even_sizes else 0,
            "top_10": even_sizes[:10],
            "mean_size": round(float(np.mean(even_sizes)), 2) if even_sizes else 0,
            "ge5": sum(1 for s in even_sizes if s >= 5),
        },
    }

    print(f"  Full population mod-2: {len(full_sizes)} clusters, max={full_sizes[0] if full_sizes else 0}, "
          f"clusters>=5: {clique_comparison['full']['ge5']}")
    print(f"  Odd-conductor mod-2:   {len(odd_sizes)} clusters, max={odd_sizes[0] if odd_sizes else 0}, "
          f"clusters>=5: {clique_comparison['odd_only']['ge5']}")
    print(f"  Even-conductor mod-2:  {len(even_sizes)} clusters, max={even_sizes[0] if even_sizes else 0}, "
          f"clusters>=5: {clique_comparison['even_only']['ge5']}")
    print(f"\n  Top 10 cluster sizes (full):      {full_sizes[:10]}")
    print(f"  Top 10 cluster sizes (odd-only):  {odd_sizes[:10]}")
    print(f"  Top 10 cluster sizes (even-only): {even_sizes[:10]}")

    # Density comparison: what fraction of forms are in large (>=5) clusters?
    full_in_large = sum(s for s in full_sizes if s >= 5) / sum(full_sizes) if full_sizes else 0
    odd_in_large = sum(s for s in odd_sizes if s >= 5) / sum(odd_sizes) if odd_sizes else 0
    even_in_large = sum(s for s in even_sizes if s >= 5) / sum(even_sizes) if even_sizes else 0
    print(f"\n  Fraction in clusters>=5: full={full_in_large:.3f}, odd={odd_in_large:.3f}, even={even_in_large:.3f}")

    clique_comparison["density_in_large"] = {
        "full": round(full_in_large, 4),
        "odd": round(odd_in_large, 4),
        "even": round(even_in_large, 4),
    }

    # =====================================================================
    # STEP 6: Control — 5 random forms, same ablation
    # =====================================================================
    print("\n[6] Control: 5 random forms, same ablation...")
    random.seed(42)
    # Pick controls: mix of odd and even conductor
    odd_labels = list(odd_forms.keys())
    even_labels = list(even_forms.keys())
    # 3 odd-conductor, 2 even-conductor controls
    control_odd = random.sample([l for l in odd_labels if l != TARGET], 3)
    control_even = random.sample(even_labels, 2)
    controls = control_odd + control_even

    control_results = {}
    for ctrl in controls:
        ctrl_v2 = forms[ctrl]["v2_level"]
        ctrl_full = {}
        ctrl_odd = {}
        ctrl_even_match = {}
        for ell in ELLS:
            # Full population
            fps_full, cl_full = compute_clusters(forms, ap_primes, ell)
            n_full = neighborhood_size(ctrl, fps_full, cl_full)
            ctrl_full[ell] = n_full

            # Odd-only
            fps_odd, cl_odd = compute_clusters(odd_forms, ap_primes, ell)
            n_odd = neighborhood_size(ctrl, fps_odd, cl_odd) if ctrl in odd_forms else -1
            ctrl_odd[ell] = n_odd

            # Even matches for this control's fingerprint
            ctrl_fp = mod_ell_fingerprint(
                forms[ctrl]["ap_int"], ap_primes, forms[ctrl]["bad"], ell
            )
            fps_even, _ = compute_clusters(even_forms, ap_primes, ell)
            n_even = sum(1 for l, fp in fps_even.items() if fp == ctrl_fp and l != ctrl)
            ctrl_even_match[ell] = n_even

        # Mod-2 reduction
        f2 = ctrl_full[2]
        o2 = ctrl_odd[2] if ctrl_odd[2] >= 0 else 0
        reduction = 100 * (1 - o2 / f2) if f2 > 0 else 0

        control_results[ctrl] = {
            "level": forms[ctrl]["level"],
            "v2_level": ctrl_v2,
            "is_odd_conductor": ctrl_v2 == 0,
            "full_N": {str(e): ctrl_full[e] for e in ELLS},
            "odd_only_N": {str(e): ctrl_odd[e] for e in ELLS},
            "even_matches": {str(e): ctrl_even_match[e] for e in ELLS},
            "mod2_reduction_pct": round(reduction, 1),
        }
        parity_tag = "ODD" if ctrl_v2 == 0 else "EVEN"
        print(f"  {ctrl} (v2={ctrl_v2}, {parity_tag}): full_N(2)={f2}, odd_N(2)={o2}, "
              f"reduction={reduction:.1f}%")

    # =====================================================================
    # STEP 7: The honest answer — proportional vs structural
    # =====================================================================
    print("\n[7] Proportional vs structural analysis...")

    n_odd = len(odd_forms)
    n_total = len(forms)
    odd_fraction = n_odd / n_total

    # If camouflage is purely proportional, ablated N should be ~odd_fraction * full_N
    # If structural, the ratio should differ from odd_fraction
    print(f"  Odd-conductor fraction of database: {odd_fraction:.4f} ({n_odd}/{n_total})")
    print(f"  If camouflage is proportional, odd-only N(2) ~ {odd_fraction:.4f} * {full_neighborhoods[2]} = {odd_fraction * full_neighborhoods[2]:.0f}")
    print(f"  Actual odd-only N(2) = {odd_neighborhoods[2]}")

    proportional_analysis = {}
    for ell in ELLS:
        fn = full_neighborhoods[ell]
        on = odd_neighborhoods[ell]
        expected = odd_fraction * fn if fn > 0 else 0
        ratio = on / expected if expected > 0 and on >= 0 else 0
        proportional_analysis[str(ell)] = {
            "expected_proportional": round(expected, 1),
            "actual": on,
            "ratio_to_expected": round(ratio, 3),
            "interpretation": (
                "STRUCTURAL" if ratio > 1.5 or ratio < 0.5
                else "PROPORTIONAL" if 0.7 < ratio < 1.3
                else "MIXED"
            ),
        }
        tag = proportional_analysis[str(ell)]["interpretation"]
        print(f"  ell={ell}: expected={expected:.1f}, actual={on}, ratio={ratio:.3f} [{tag}]")

    # Same analysis for controls
    print(f"\n  Control proportional ratios at ell=2:")
    control_proportional = {}
    for ctrl, cdata in control_results.items():
        fn = cdata["full_N"]["2"]
        on = cdata["odd_only_N"]["2"]
        if on < 0:
            on = 0
        expected = odd_fraction * fn if fn > 0 else 0
        ratio = on / expected if expected > 0 else 0
        control_proportional[ctrl] = round(ratio, 3)
        print(f"    {ctrl}: full={fn}, odd={on}, expected={expected:.1f}, ratio={ratio:.3f}")

    # =====================================================================
    # STEP 8: v2 stratification — how does neighborhood scale with v2?
    # =====================================================================
    print("\n[8] v_2 stratification: neighborhood by conductor 2-adic valuation...")

    # For each v2 stratum, compute 15.2.a.a's neighborhood within that stratum
    v2_strata = defaultdict(dict)
    for v2_val in sorted(v2_distribution.keys()):
        stratum = {l: f for l, f in forms.items() if f["v2_level"] == v2_val}
        if len(stratum) < 2:
            continue
        for ell in [2, 3, 5]:
            fps, clusters = compute_clusters(stratum, ap_primes, ell)
            target_fp = mod_ell_fingerprint(
                forms[TARGET]["ap_int"], ap_primes, forms[TARGET]["bad"], ell
            )
            n_matches = sum(1 for l, fp in fps.items() if fp == target_fp and l != TARGET)
            v2_strata[v2_val][str(ell)] = {
                "stratum_size": len(stratum),
                "matches": n_matches,
                "density": round(n_matches / len(stratum), 6) if len(stratum) > 0 else 0,
            }

    print(f"  {'v2':>3} | {'#forms':>6} | {'N(2)':>6} | {'d(2)':>8} | {'N(3)':>6} | {'d(3)':>8} | {'N(5)':>6} | {'d(5)':>8}")
    for v2_val in sorted(v2_strata.keys()):
        s = v2_strata[v2_val]
        sz = s["2"]["stratum_size"]
        n2 = s["2"]["matches"]
        d2 = s["2"]["density"]
        n3 = s.get("3", {}).get("matches", "-")
        d3 = s.get("3", {}).get("density", "-")
        n5 = s.get("5", {}).get("matches", "-")
        d5 = s.get("5", {}).get("density", "-")
        print(f"  {v2_val:>3} | {sz:>6} | {n2:>6} | {d2:>8.6f} | {n3:>6} | {d3:>8} | {n5:>6} | {d5:>8}")

    # =====================================================================
    # BUILD RESULTS
    # =====================================================================
    elapsed = time.time() - t0
    print(f"\n=== Completed in {elapsed:.1f}s ===")

    # Build assessment
    mod2_reduction = decomposition["2"]["reduction_pct"]
    odd_n2 = odd_neighborhoods[2]
    full_n2 = full_neighborhoods[2]
    prop_ratio_2 = proportional_analysis["2"]["ratio_to_expected"]
    prop_interp_2 = proportional_analysis["2"]["interpretation"]

    # Control comparison
    ctrl_reductions = [c["mod2_reduction_pct"] for c in control_results.values()]
    target_specific = abs(mod2_reduction - np.mean(ctrl_reductions)) > 2 * np.std(ctrl_reductions) if ctrl_reductions else False

    assessment_parts = []
    assessment_parts.append(
        f"Odd-conductor forms: {len(odd_forms)}/{len(forms)} ({100*len(odd_forms)/len(forms):.1f}%)"
    )
    assessment_parts.append(
        f"Mod-2 ablation: full N={full_n2}, odd-only N={odd_n2}, "
        f"reduction={mod2_reduction:.1f}%"
    )
    if mod2_reduction > 80:
        assessment_parts.append("Camouflage EVAPORATES after removing even conductors")
    elif mod2_reduction > 50:
        assessment_parts.append("Camouflage PARTIALLY evaporates after removing even conductors")
    else:
        assessment_parts.append("Camouflage PERSISTS even after removing even conductors")

    assessment_parts.append(
        f"Proportional test at ell=2: ratio={prop_ratio_2:.3f} [{prop_interp_2}]"
    )
    if prop_interp_2 == "PROPORTIONAL":
        assessment_parts.append(
            "Camouflage is proportional — it is a property of DATABASE COMPOSITION, not the form"
        )
    elif prop_interp_2 == "STRUCTURAL":
        assessment_parts.append(
            "Camouflage is structural — odd-conductor forms have genuinely different mod-2 behavior"
        )
    else:
        assessment_parts.append(
            "Camouflage is mixed -- partly database composition, partly structural"
        )

    if not target_specific:
        assessment_parts.append(
            "Effect is UNIVERSAL (controls show similar reduction), not specific to 15.2.a.a"
        )
    else:
        assessment_parts.append(
            "Effect is SPECIFIC to 15.2.a.a (controls differ significantly)"
        )

    assessment = ". ".join(assessment_parts)
    print(f"\nASSESSMENT: {assessment}")

    results = {
        "challenge": "OSC-4",
        "title": "Ablate the 2-Adic Camouflage",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "target": TARGET,
        "target_level": forms[TARGET]["level"],
        "target_v2": target_v2,
        "population": {
            "total": len(forms),
            "odd_conductor": len(odd_forms),
            "even_conductor": len(even_forms),
            "odd_fraction": round(len(odd_forms) / len(forms), 4),
            "v2_distribution": {str(k): v for k, v in sorted(v2_distribution.items())},
        },
        "full_neighborhoods": {str(e): full_neighborhoods[e] for e in ELLS},
        "odd_only_neighborhoods": {str(e): odd_neighborhoods[e] for e in ELLS},
        "even_matches": {str(e): even_neighborhoods[e] for e in ELLS},
        "decomposition": decomposition,
        "gradient_comparison": gradient,
        "clique_comparison_mod2": clique_comparison,
        "proportional_analysis": proportional_analysis,
        "control_results": control_results,
        "control_proportional_ratios_ell2": control_proportional,
        "v2_stratification": {str(k): v for k, v in sorted(v2_strata.items())},
        "assessment": assessment,
    }

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
