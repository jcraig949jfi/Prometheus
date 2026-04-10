"""
OSC-2: Altitude Camouflage — Entropy Decay Gradient for 15.2.a.a Twist Orbit
==============================================================================
Maps how the mod-ell neighborhood shrinks as ell increases, measuring:
  - N(ell): neighborhood size at each prime altitude
  - H(ell): Shannon entropy of mod-ell cluster distribution
  - ell_c: critical prime where form becomes effectively isolated
  - Twist orbit invariance of the phase transition
  - Background comparison against 100 random forms
"""
import json, time, math, random
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
DB = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT = V2 / "altitude_camouflage_results.json"

ELLS = [2, 3, 5, 7, 11, 13]
N_BACKGROUND = 100
MIN_GOOD_PRIMES = 8  # require at least this many good primes for a valid fingerprint


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


def kronecker(d, n):
    """Kronecker symbol (d/n)."""
    if n == 0: return 0
    if n == 1: return 1
    result = 1
    if n < 0:
        n = -n
        result = -1 if d < 0 else 1
    while n % 2 == 0:
        n //= 2
        if d % 2 != 0:
            r = d % 8
            if r == 3 or r == 5: result = -result
    while n > 1:
        if n % 2 == 0: n //= 2; continue
        if d % n == 0: return 0
        result *= 1 if pow(d, (n-1)//2, n) <= 1 else -1
        d, n = n, d % n
    return result


def mod_ell_fingerprint(ap_int, ap_primes, bad_primes, ell, max_primes=20):
    """Compute mod-ell fingerprint: tuple of (a_p mod ell) at good primes."""
    fp = []
    for i, p in enumerate(ap_primes[:max_primes]):
        if i >= len(ap_int): break
        if p in bad_primes or p == ell: continue
        fp.append(ap_int[i] % ell)
    return tuple(fp)


def compute_neighborhood(target_fp, all_fps):
    """Count how many forms share the same fingerprint."""
    return sum(1 for fp in all_fps if fp == target_fp)


def shannon_entropy(cluster_sizes, total):
    """H = -sum(p_i * log(p_i)) where p_i = cluster_size / total."""
    h = 0.0
    for s in cluster_sizes:
        if s > 0:
            p = s / total
            h -= p * math.log2(p)
    return h


def find_ell_c(neighborhood_curve, ells):
    """Find critical prime where form becomes effectively isolated.
    ell_c = first ell where N(ell) <= 1 (singleton), or where the
    largest drop occurs if never fully isolated.
    """
    for i, ell in enumerate(ells):
        if neighborhood_curve[i] <= 1:
            return ell
    # Never isolated: find largest relative drop
    max_drop = 0
    ell_c = ells[-1]
    for i in range(1, len(ells)):
        if neighborhood_curve[i-1] > 0:
            drop = (neighborhood_curve[i-1] - neighborhood_curve[i]) / neighborhood_curve[i-1]
            if drop > max_drop:
                max_drop = drop
                ell_c = ells[i]
    return ell_c


def main():
    t0 = time.time()
    print("=== OSC-2: Altitude Camouflage — Entropy Decay Gradient ===\n")

    con = duckdb.connect(str(DB), read_only=True)

    # Load all forms
    print("[0] Loading database...")
    all_rows = con.execute("""
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms WHERE weight = 2 AND dim = 1 AND char_order = 1
    """).fetchall()
    con.close()
    print(f"  Loaded {len(all_rows)} forms")

    ap_primes = sieve(200)

    # Parse all forms into usable structures
    print("[0.1] Parsing a_p data...")
    forms = {}
    for label, level, ap_json, is_cm in all_rows:
        ap = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        ap_int = [int(x[0]) if isinstance(x, list) else int(x) for x in ap]
        bad = prime_factors(level)
        forms[label] = {
            "level": level, "ap_int": ap_int, "bad": bad, "is_cm": bool(is_cm)
        }
    print(f"  Parsed {len(forms)} forms")

    # ------------------------------------------------------------------
    # STEP 1: Identify 15.2.a.a and its twist orbit
    # ------------------------------------------------------------------
    TARGET = "15.2.a.a"
    if TARGET not in forms:
        print(f"  ERROR: {TARGET} not found!")
        return

    target = forms[TARGET]
    print(f"\n[1] Target: {TARGET} (level={target['level']}, CM={target['is_cm']})")
    print(f"  Bad primes: {sorted(target['bad'])}")
    print(f"  a_p first 10: {target['ap_int'][:10]}")

    # ------------------------------------------------------------------
    # STEP 2: Find twist partners
    # ------------------------------------------------------------------
    print("\n[2] Finding twist orbit...")
    TWIST_DISCS = [-3, -4, -7, -8, -11, -15, -19, -20, -24, 5, 8, 12, 13, 17, 21, 24]
    twist_orbit = {TARGET: {"disc": 1, "label": TARGET}}  # identity twist

    # Also include known twists from CT4 results
    known_twists = {
        "45.2.a.a": -3, "75.2.a.b": 5, "240.2.a.d": -4,
    }

    for d in TWIST_DISCS:
        # Compute twisted a_p (only at primes good for the target)
        twisted_ap = {}
        for i, p in enumerate(ap_primes[:25]):
            if i >= len(target["ap_int"]): break
            twisted_ap[i] = target["ap_int"][i] * kronecker(d, p)

        # Search for matching form
        best_match = None
        best_score = 0
        best_compared = 0
        for label, fdata in forms.items():
            if label == TARGET: continue
            score = 0
            compared = 0
            for i in range(min(25, len(fdata["ap_int"]))):
                if i not in twisted_ap: continue
                p = ap_primes[i]
                # Skip primes that are bad for EITHER form, or equal to disc
                if p in target["bad"] or p in fdata["bad"]: continue
                if abs(d) == p: continue
                compared += 1
                if twisted_ap[i] == fdata["ap_int"][i]:
                    score += 1
            if compared >= 6 and score >= compared - 1 and score > best_score:
                best_score = score
                best_compared = compared
                best_match = label

        if best_match and best_score >= 6:
            # Deduplicate: same form can appear via different discriminants
            existing = [v["label"] for v in twist_orbit.values()]
            if best_match not in existing:
                twist_orbit[f"chi_{d}"] = {"disc": d, "label": best_match}
                print(f"  chi_{d}: {best_match} (score={best_score}/{best_compared})")
            else:
                print(f"  chi_{d}: {best_match} (duplicate, skipping)")

    # Add known twists from CT4 that may have been missed
    for label, d in known_twists.items():
        if label in forms and label not in [v["label"] for v in twist_orbit.values()]:
            twist_orbit[f"ct4_chi_{d}"] = {"disc": d, "label": label}
            print(f"  ct4_chi_{d}: {label} (from CT4 data)")

    twist_labels = [v["label"] for v in twist_orbit.values()]
    print(f"\n  Twist orbit: {len(twist_labels)} distinct forms")
    for k, v in twist_orbit.items():
        print(f"    {k}: {v['label']} (level={forms[v['label']]['level']})")

    # ------------------------------------------------------------------
    # STEP 3: Precompute all mod-ell fingerprints
    # ------------------------------------------------------------------
    print("\n[3] Computing mod-ell fingerprints for all forms...")
    all_fingerprints = {}  # ell -> {label: fingerprint}
    cluster_maps = {}  # ell -> {fingerprint: [labels]}

    for ell in ELLS:
        fps = {}
        clusters = defaultdict(list)
        for label, fdata in forms.items():
            fp = mod_ell_fingerprint(fdata["ap_int"], ap_primes, fdata["bad"], ell)
            if len(fp) >= MIN_GOOD_PRIMES:
                fps[label] = fp
                clusters[fp].append(label)
        all_fingerprints[ell] = fps
        cluster_maps[ell] = clusters
        n_clusters = len(clusters)
        sizes = [len(v) for v in clusters.values()]
        max_size = max(sizes) if sizes else 0
        singletons = sum(1 for s in sizes if s == 1)
        print(f"  ell={ell}: {len(fps)} forms fingerprinted, "
              f"{n_clusters} clusters, max_size={max_size}, singletons={singletons}")

    # ------------------------------------------------------------------
    # STEP 4: Neighborhood curves N(ell) for twist orbit
    # ------------------------------------------------------------------
    print("\n[4] Neighborhood decay curves N(ell)...")
    neighborhood_curves = {}

    for tw_key, tw_info in twist_orbit.items():
        label = tw_info["label"]
        curve = []
        for ell in ELLS:
            if label in all_fingerprints[ell]:
                fp = all_fingerprints[ell][label]
                n_neighbors = len(cluster_maps[ell].get(fp, [])) - 1  # exclude self
                curve.append(n_neighbors)
            else:
                curve.append(-1)  # not enough data
        neighborhood_curves[label] = curve
        print(f"  {label}: N(ell) = {dict(zip(ELLS, curve))}")

    # ------------------------------------------------------------------
    # STEP 5: Entropy H(ell) at each altitude
    # ------------------------------------------------------------------
    print("\n[5] Entropy decay curves H(ell)...")
    global_entropy = {}
    for ell in ELLS:
        clusters = cluster_maps[ell]
        sizes = [len(v) for v in clusters.values()]
        total = sum(sizes)
        h = shannon_entropy(sizes, total)
        global_entropy[ell] = round(h, 4)
        print(f"  ell={ell}: H={h:.4f} bits ({len(sizes)} clusters, {total} forms)")

    # Per-form entropy: entropy of the cluster the form belongs to, relative to total
    # More informative: what fraction of total entropy does this form's cluster represent?
    form_entropy = {}
    for tw_key, tw_info in twist_orbit.items():
        label = tw_info["label"]
        h_curve = []
        for ell in ELLS:
            if label in all_fingerprints[ell]:
                fp = all_fingerprints[ell][label]
                cluster_size = len(cluster_maps[ell].get(fp, []))
                total = sum(len(v) for v in cluster_maps[ell].values())
                # Local contribution: -p*log(p) for this form's cluster
                p = cluster_size / total
                local_h = -p * math.log2(p) if p > 0 else 0
                h_curve.append(round(local_h, 6))
            else:
                h_curve.append(None)
        form_entropy[label] = h_curve

    print("\n  Form-level entropy contribution (bits):")
    for label, h_curve in form_entropy.items():
        print(f"  {label}: {dict(zip(ELLS, h_curve))}")

    # ------------------------------------------------------------------
    # STEP 6: Critical prime ell_c
    # ------------------------------------------------------------------
    print("\n[6] Critical prime ell_c (isolation point)...")
    ell_c_map = {}
    for tw_key, tw_info in twist_orbit.items():
        label = tw_info["label"]
        curve = neighborhood_curves[label]
        # Filter out -1 entries
        valid = [(ELLS[i], curve[i]) for i in range(len(ELLS)) if curve[i] >= 0]
        if valid:
            valid_ells = [v[0] for v in valid]
            valid_ns = [v[1] for v in valid]
            ec = find_ell_c(valid_ns, valid_ells)
            ell_c_map[label] = ec
            print(f"  {label}: ell_c = {ec} (curve: {dict(zip(valid_ells, valid_ns))})")

    # Invariance check
    ell_c_values = list(ell_c_map.values())
    all_same = len(set(ell_c_values)) == 1 if ell_c_values else False
    print(f"\n  ell_c values: {ell_c_map}")
    print(f"  Twist orbit invariant? {'YES' if all_same else 'NO'}")
    if not all_same and ell_c_values:
        print(f"  Distinct ell_c: {sorted(set(ell_c_values))}")

    # ------------------------------------------------------------------
    # STEP 7: Background comparison — 100 random forms
    # ------------------------------------------------------------------
    print("\n[7] Background comparison (100 random forms)...")
    random.seed(42)
    all_labels = [l for l in forms.keys() if l not in twist_labels]
    bg_labels = random.sample(all_labels, min(N_BACKGROUND, len(all_labels)))

    bg_curves = []
    bg_ell_c = []
    for label in bg_labels:
        curve = []
        for ell in ELLS:
            if label in all_fingerprints[ell]:
                fp = all_fingerprints[ell][label]
                n = len(cluster_maps[ell].get(fp, [])) - 1
                curve.append(n)
            else:
                curve.append(-1)
        bg_curves.append(curve)
        valid = [(ELLS[i], curve[i]) for i in range(len(ELLS)) if curve[i] >= 0]
        if valid:
            valid_ells = [v[0] for v in valid]
            valid_ns = [v[1] for v in valid]
            bg_ell_c.append(find_ell_c(valid_ns, valid_ells))

    # Compute background statistics
    bg_array = np.array(bg_curves, dtype=float)
    bg_array[bg_array < 0] = np.nan
    bg_means = np.nanmean(bg_array, axis=0)
    bg_medians = np.nanmedian(bg_array, axis=0)
    bg_stds = np.nanstd(bg_array, axis=0)
    bg_p90 = np.nanpercentile(bg_array, 90, axis=0)
    bg_p99 = np.nanpercentile(bg_array, 99, axis=0)

    print(f"  Background N(ell) statistics:")
    for i, ell in enumerate(ELLS):
        print(f"    ell={ell}: mean={bg_means[i]:.1f}, median={bg_medians[i]:.0f}, "
              f"std={bg_stds[i]:.1f}, p90={bg_p90[i]:.0f}, p99={bg_p99[i]:.0f}")

    # Target vs background
    target_curve = neighborhood_curves[TARGET]
    print(f"\n  Target {TARGET} vs background:")
    for i, ell in enumerate(ELLS):
        tc = target_curve[i]
        if tc >= 0 and bg_stds[i] > 0:
            z = (tc - bg_means[i]) / bg_stds[i]
            pctile = np.nansum(bg_array[:, i] <= tc) / np.nansum(~np.isnan(bg_array[:, i])) * 100
            print(f"    ell={ell}: target={tc}, z-score={z:.2f}, percentile={pctile:.1f}%")
        else:
            print(f"    ell={ell}: target={tc}, background mean={bg_means[i]:.1f}")

    # Background ell_c distribution
    bg_ell_c_counter = Counter(bg_ell_c)
    print(f"\n  Background ell_c distribution:")
    for ec, cnt in sorted(bg_ell_c_counter.items()):
        print(f"    ell_c={ec}: {cnt} forms ({cnt/len(bg_ell_c)*100:.1f}%)")

    # ------------------------------------------------------------------
    # STEP 8: Decay shape analysis
    # ------------------------------------------------------------------
    print("\n[8] Decay shape analysis...")
    # For each form in twist orbit, fit log(N(ell)) vs ell
    # Exponential decay: log(N) = a - b*ell
    # Phase transition: sudden drop (look for max gap in log-space)
    decay_analysis = {}
    for tw_key, tw_info in twist_orbit.items():
        label = tw_info["label"]
        curve = neighborhood_curves[label]
        valid = [(ELLS[i], curve[i]) for i in range(len(ELLS)) if curve[i] > 0]
        if len(valid) >= 2:
            x = np.array([v[0] for v in valid], dtype=float)
            y = np.array([math.log2(v[1]) for v in valid], dtype=float)
            # Linear fit in log-space
            if len(x) >= 2:
                slope, intercept = np.polyfit(x, y, 1)
                residuals = y - (slope * x + intercept)
                max_residual_idx = np.argmax(np.abs(residuals))
                decay_analysis[label] = {
                    "slope": round(float(slope), 4),
                    "intercept": round(float(intercept), 4),
                    "residual_max": round(float(np.max(np.abs(residuals))), 4),
                    "residual_at": int(x[max_residual_idx]),
                    "r_squared": round(float(1 - np.var(residuals)/np.var(y)), 4) if np.var(y) > 0 else 0,
                    "n_points": len(valid),
                    "log2_N": dict(zip([int(v[0]) for v in valid],
                                       [round(float(math.log2(v[1])), 2) for v in valid]))
                }
                print(f"  {label}: slope={slope:.4f}/prime, R²={decay_analysis[label]['r_squared']:.4f}")

    # Check if decay is smooth (R² > 0.95) or has phase transition (R² < 0.8)
    smooth_count = sum(1 for d in decay_analysis.values() if d["r_squared"] > 0.95)
    jump_count = sum(1 for d in decay_analysis.values() if d["r_squared"] < 0.8)
    print(f"\n  Smooth exponential decay: {smooth_count}/{len(decay_analysis)}")
    print(f"  Phase transition (poor fit): {jump_count}/{len(decay_analysis)}")

    # ------------------------------------------------------------------
    # STEP 9: Cluster size distributions at each ell
    # ------------------------------------------------------------------
    print("\n[9] Cluster size distributions...")
    cluster_distributions = {}
    for ell in ELLS:
        sizes = sorted([len(v) for v in cluster_maps[ell].values()], reverse=True)
        dist = Counter(sizes)
        cluster_distributions[ell] = {
            "n_clusters": len(sizes),
            "max": sizes[0] if sizes else 0,
            "top_5": sizes[:5],
            "singletons": dist.get(1, 0),
            "singleton_fraction": round(dist.get(1, 0) / len(sizes), 4) if sizes else 0,
        }
        print(f"  ell={ell}: {len(sizes)} clusters, max={sizes[0] if sizes else 0}, "
              f"singletons={dist.get(1, 0)} ({cluster_distributions[ell]['singleton_fraction']*100:.1f}%)")

    # ------------------------------------------------------------------
    # BUILD RESULTS
    # ------------------------------------------------------------------
    elapsed = time.time() - t0
    print(f"\n=== Completed in {elapsed:.1f}s ===")

    results = {
        "challenge": "OSC-2",
        "title": "Altitude Camouflage: Entropy Decay Gradient for 15.2.a.a Twist Orbit",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "target": TARGET,
        "twist_orbit": {k: v for k, v in twist_orbit.items()},
        "ells": ELLS,
        "neighborhood_curves": {
            label: dict(zip([str(e) for e in ELLS], curve))
            for label, curve in neighborhood_curves.items()
        },
        "global_entropy": {str(k): v for k, v in global_entropy.items()},
        "form_entropy": {
            label: dict(zip([str(e) for e in ELLS], h))
            for label, h in form_entropy.items()
        },
        "critical_prime": {
            "ell_c_per_form": ell_c_map,
            "twist_invariant": all_same,
            "distinct_values": sorted(set(ell_c_values)) if ell_c_values else [],
        },
        "decay_analysis": decay_analysis,
        "background": {
            "n_forms": len(bg_labels),
            "mean_N": {str(ELLS[i]): round(float(bg_means[i]), 2) for i in range(len(ELLS))},
            "median_N": {str(ELLS[i]): round(float(bg_medians[i]), 1) for i in range(len(ELLS))},
            "std_N": {str(ELLS[i]): round(float(bg_stds[i]), 2) for i in range(len(ELLS))},
            "p90_N": {str(ELLS[i]): round(float(bg_p90[i]), 1) for i in range(len(ELLS))},
            "p99_N": {str(ELLS[i]): round(float(bg_p99[i]), 1) for i in range(len(ELLS))},
            "target_z_score": {
                str(ELLS[i]): round(float((target_curve[i] - bg_means[i]) / bg_stds[i]), 2)
                if target_curve[i] >= 0 and bg_stds[i] > 0 else None
                for i in range(len(ELLS))
            },
            "ell_c_distribution": {str(k): v for k, v in sorted(bg_ell_c_counter.items())},
        },
        "cluster_distributions": {
            str(ell): dist for ell, dist in cluster_distributions.items()
        },
        "assessment": None,
    }

    # Build assessment
    parts = []
    parts.append(f"Twist orbit: {len(twist_labels)} distinct forms")

    # Neighborhood summary
    tc = neighborhood_curves[TARGET]
    parts.append(f"15.2.a.a: N(2)={tc[0]}, N(3)={tc[1]}, N(5)={tc[2]}, "
                 f"N(7)={tc[3]}, N(11)={tc[4]}, N(13)={tc[5]}")

    # Phase transition
    if all_same:
        parts.append(f"ell_c={ell_c_values[0]} is INVARIANT across twist orbit")
    else:
        parts.append(f"ell_c varies: {sorted(set(ell_c_values))} — twisting shifts camouflage altitude")

    # Decay shape
    if smooth_count > jump_count:
        parts.append("Decay is predominantly smooth (exponential)")
    else:
        parts.append("Decay shows discrete phase transitions")

    # Background comparison
    z2 = results["background"]["target_z_score"].get("2")
    if z2 is not None:
        parts.append(f"Mod-2 neighborhood z-score vs background: {z2}")

    results["assessment"] = ". ".join(parts)
    print(f"\nASSESSMENT: {results['assessment']}")

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
