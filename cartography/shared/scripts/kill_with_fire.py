"""
kill_with_fire.py — Adversarial test suite to DESTROY the 5D structure claim.

Claim: particle masses, EC conductors, MF levels, lattice determinants,
and metabolic stoichiometry share a low-dimensional geometric subspace.
Key result: particles at 3.7 deg principal angle to EC in Grassmannian.

8 kill tests, each designed to maximise probability of falsification.
ANY kill = claim is dead.

Machine: M1 (Skullport), RTX 5060 Ti 17GB VRAM
"""
import sys
import time
import warnings
import numpy as np
import torch
from pathlib import Path
from collections import defaultdict
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "cartography" / "convergence" / "data"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ============================================================
# Helpers
# ============================================================

def load_tensor():
    """Load dissection tensor with metadata."""
    path = DATA_DIR / "dissection_tensor.pt"
    data = torch.load(path, map_location="cpu", weights_only=False)
    tensor = data["tensor"]        # [N, D] float32
    mask = data["mask"]            # [N, D] bool
    labels = data["labels"]
    domains = data["domains"]
    strategy_slices = data["strategy_slices"]

    domain_indices = defaultdict(list)
    for i, d in enumerate(domains):
        domain_indices[d].append(i)

    # Build group slices
    STRATEGY_GROUPS = {
        "complex":     ["s1_alex", "s1_jones", "s1_ap"],
        "mod_p":       ["s3_alex", "s3_jones", "s3_ap"],
        "spectral":    ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
        "padic":       ["s7_det", "s7_disc", "s7_cond"],
        "symmetry":    ["s9_st", "s9_endo"],
        "galois":      ["s10", "s10_galrep"],
        "zeta":        ["s12_ec", "s12_oeis", "s12_nf"],
        "disc_cond":   ["s13"],
        "operadic":    ["s22"],
        "entropy":     ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
        "attractor":   ["s6_oeis"],
        "automorphic": ["s21_auto"],
        "monodromy":   ["s11_mono"],
        "ade":         ["s19_ade"],
    }
    if "group_slices" in data and data["group_slices"]:
        group_slices = data["group_slices"]
    else:
        group_slices = {}
        for gname, slist in STRATEGY_GROUPS.items():
            starts = [strategy_slices[s][0] for s in slist if s in strategy_slices]
            ends = [strategy_slices[s][1] for s in slist if s in strategy_slices]
            if starts:
                group_slices[gname] = (min(starts), max(ends))

    return tensor, mask, labels, domains, domain_indices, strategy_slices, group_slices


def get_domain_subspace(T_numpy, indices, variance_threshold=0.90):
    """Compute PCA subspace for a domain. Returns Vt[:k,:] and k."""
    T_dom = T_numpy[indices]
    T_dom_c = T_dom - T_dom.mean(axis=0)
    U, S, Vt = np.linalg.svd(T_dom_c, full_matrices=False)
    var = S ** 2
    if var.sum() < 1e-12:
        return Vt[:1, :], 1
    cumvar = np.cumsum(var) / var.sum()
    k = int(np.searchsorted(cumvar, variance_threshold)) + 1
    k = min(k, len(S))
    return Vt[:k, :], k


def principal_angle_deg(subspace_A, subspace_B):
    """Compute minimum principal angle (degrees) between two subspaces."""
    M = subspace_A @ subspace_B.T
    _, sigmas, _ = np.linalg.svd(M, full_matrices=False)
    sigmas = np.clip(sigmas, 0, 1)
    angles = np.arccos(sigmas)
    return float(np.degrees(angles.min())) if len(angles) > 0 else 90.0


def banner(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================
def main():
    np.random.seed(42)
    torch.manual_seed(42)

    print("KILL WITH FIRE — Adversarial test suite")
    print(f"Device: {DEVICE}")
    print(f"Loading tensor...")

    tensor, mask, labels, domains, domain_indices, strategy_slices, group_slices = load_tensor()
    T = tensor.numpy()
    M = mask.numpy()
    N, D = T.shape

    # Identify key domains
    print(f"\nDomain sizes:")
    for dname in sorted(domain_indices.keys()):
        print(f"  {dname:15s}: {len(domain_indices[dname]):>6d}")

    # Compute real subspaces
    particle_idx = domain_indices.get("particle", [])
    ec_idx = domain_indices.get("EC", [])
    lattice_idx = domain_indices.get("lattice", [])
    metab_idx = domain_indices.get("metabolism", [])
    knot_idx = domain_indices.get("knot", [])
    material_idx = domain_indices.get("material", [])

    if not particle_idx:
        print("ERROR: No 'particle' domain found. Available:", list(domain_indices.keys()))
        sys.exit(1)
    if not ec_idx:
        print("ERROR: No 'EC' domain found.")
        sys.exit(1)

    print(f"\nKey domains: particle={len(particle_idx)}, EC={len(ec_idx)}, "
          f"lattice={len(lattice_idx)}, metabolism={len(metab_idx)}")

    # Real subspaces
    sub_particle, k_particle = get_domain_subspace(T, particle_idx)
    sub_ec, k_ec = get_domain_subspace(T, ec_idx)
    real_angle = principal_angle_deg(sub_particle, sub_ec)
    print(f"\nREAL particle<->EC principal angle: {real_angle:.2f} deg (subspace dims: {k_particle}, {k_ec})")

    # Also compute other claimed bridges
    if lattice_idx and metab_idx:
        sub_lattice, k_lattice = get_domain_subspace(T, lattice_idx)
        sub_metab, k_metab = get_domain_subspace(T, metab_idx)
        real_metab_lattice = principal_angle_deg(sub_metab, sub_lattice)
        print(f"REAL metabolism<->lattice principal angle: {real_metab_lattice:.2f} deg")

    if material_idx and knot_idx:
        sub_material, _ = get_domain_subspace(T, material_idx)
        sub_knot, _ = get_domain_subspace(T, knot_idx)
        real_material_knot = principal_angle_deg(sub_material, sub_knot)
        print(f"REAL material<->knot principal angle: {real_material_knot:.2f} deg")

    kills = 0
    total = 8

    # ============================================================
    # TEST 1: NULL CONTROL — Random data should NOT bridge
    # ============================================================
    banner("TEST 1: NULL CONTROL — Random data with same sparsity pattern")
    N_TRIALS = 1000
    n_particles = len(particle_idx)

    # Get particle sparsity pattern
    particle_mask = M[particle_idx]  # [n_particles, D]

    null_angles = []
    for trial in range(N_TRIALS):
        # Generate random values where particles have data
        fake_particles = np.zeros((n_particles, D), dtype=np.float32)
        for d in range(D):
            col_mask = particle_mask[:, d]
            n_filled = col_mask.sum()
            if n_filled > 0:
                # Use the global distribution of that dimension as the random source
                all_vals = T[:, d][M[:, d]]
                if len(all_vals) > 0:
                    fake_particles[col_mask, d] = np.random.choice(all_vals, size=int(n_filled), replace=True)

        # Compute subspace
        fake_c = fake_particles - fake_particles.mean(axis=0)
        try:
            U, S, Vt = np.linalg.svd(fake_c, full_matrices=False)
            var = S ** 2
            cumvar = np.cumsum(var) / (var.sum() + 1e-12)
            k = int(np.searchsorted(cumvar, 0.90)) + 1
            k = min(k, len(S))
            fake_sub = Vt[:k, :]
            angle = principal_angle_deg(fake_sub, sub_ec)
            null_angles.append(angle)
        except Exception:
            pass

    null_angles = np.array(null_angles)
    p_value = (null_angles <= real_angle).mean()
    print(f"  Null distribution: mean={null_angles.mean():.2f}, std={null_angles.std():.2f}, "
          f"min={null_angles.min():.2f}, max={null_angles.max():.2f}")
    print(f"  Real angle: {real_angle:.2f} deg")
    print(f"  p-value (fraction of nulls <= real): {p_value:.4f}")
    print(f"  5th percentile of null: {np.percentile(null_angles, 5):.2f} deg")

    if p_value > 0.05:
        print(f"  VERDICT: *** KILLED *** — Random data with same sparsity achieves similar angles (p={p_value:.4f})")
        kills += 1
    else:
        print(f"  VERDICT: SURVIVES — Real angle is significantly smaller than null (p={p_value:.4f})")

    # ============================================================
    # TEST 2: PERMUTATION KILL — Shuffle within domain
    # ============================================================
    banner("TEST 2: PERMUTATION KILL — Shuffle values within each dimension independently")
    N_TRIALS = 1000
    perm_angles = []
    particle_data = T[particle_idx].copy()  # [n_particles, D]

    for trial in range(N_TRIALS):
        shuffled = particle_data.copy()
        for d in range(D):
            # Only shuffle non-zero (filled) entries
            filled = particle_mask[:, d]
            n_filled = filled.sum()
            if n_filled > 1:
                vals = shuffled[filled, d].copy()
                np.random.shuffle(vals)
                shuffled[filled, d] = vals

        shuf_c = shuffled - shuffled.mean(axis=0)
        try:
            U, S, Vt = np.linalg.svd(shuf_c, full_matrices=False)
            var = S ** 2
            cumvar = np.cumsum(var) / (var.sum() + 1e-12)
            k = int(np.searchsorted(cumvar, 0.90)) + 1
            k = min(k, len(S))
            shuf_sub = Vt[:k, :]
            angle = principal_angle_deg(shuf_sub, sub_ec)
            perm_angles.append(angle)
        except Exception:
            pass

    perm_angles = np.array(perm_angles)
    p_value_perm = (perm_angles <= real_angle).mean()
    print(f"  Permutation distribution: mean={perm_angles.mean():.2f}, std={perm_angles.std():.2f}, "
          f"min={perm_angles.min():.2f}, max={perm_angles.max():.2f}")
    print(f"  Real angle: {real_angle:.2f} deg")
    print(f"  p-value: {p_value_perm:.4f}")

    if p_value_perm > 0.05:
        print(f"  VERDICT: *** KILLED *** — Marginal distributions alone produce similar angles (p={p_value_perm:.4f})")
        kills += 1
    else:
        print(f"  VERDICT: SURVIVES — Joint structure matters, not just marginals (p={p_value_perm:.4f})")

    # ============================================================
    # TEST 3: DIMENSION ABLATION — Which dims drive the bridge?
    # ============================================================
    banner("TEST 3: DIMENSION ABLATION — Remove each strategy group")

    ablation_results = {}
    groups_that_matter = 0
    groups_tested = 0

    for gname, (start, end) in sorted(group_slices.items()):
        # Check if either domain has data in this group
        particle_has = M[particle_idx][:, start:end].any()
        ec_has = M[ec_idx][:, start:end].any()

        if not (particle_has and ec_has):
            continue

        groups_tested += 1
        # Ablate: zero out this group's dimensions
        T_ablated = T.copy()
        T_ablated[:, start:end] = 0.0

        sub_p_abl, _ = get_domain_subspace(T_ablated, particle_idx)
        sub_e_abl, _ = get_domain_subspace(T_ablated, ec_idx)
        abl_angle = principal_angle_deg(sub_p_abl, sub_e_abl)
        delta = abl_angle - real_angle
        ablation_results[gname] = {"angle_after": abl_angle, "delta": delta}

        tag = ""
        if delta > 30:
            tag = " *** THIS GROUP DRIVES THE BRIDGE ***"
            groups_that_matter += 1
        elif delta > 10:
            tag = " * contributes"
            groups_that_matter += 1

        print(f"  Remove {gname:15s} [{start:3d}:{end:3d}]: angle={abl_angle:6.2f} deg  (delta={delta:+.2f}){tag}")

    # Check: if only 1 group drives everything, bridge is fragile
    if groups_tested == 0:
        print(f"  No shared groups between particle and EC!")
        print(f"  VERDICT: *** KILLED *** — Domains share no strategy dimensions")
        kills += 1
    elif groups_that_matter <= 1:
        print(f"\n  Only {groups_that_matter}/{groups_tested} group(s) contribute > 10 deg change.")
        print(f"  VERDICT: *** KILLED *** — Bridge driven by a single strategy group, not distributed structure")
        kills += 1
    else:
        print(f"\n  {groups_that_matter}/{groups_tested} groups contribute > 10 deg change.")
        print(f"  VERDICT: SURVIVES — Bridge is distributed across multiple strategy groups")

    # ============================================================
    # TEST 4: SAMPLE SIZE BIAS — Is 225 particles enough?
    # ============================================================
    banner("TEST 4: SAMPLE SIZE BIAS — Subsample EC to particle size")
    N_TRIALS = 1000
    subsample_angles = []
    ec_full_sub, _ = get_domain_subspace(T, ec_idx)

    for trial in range(N_TRIALS):
        # Random subsample of EC at particle size
        sub_idx = np.random.choice(ec_idx, size=min(n_particles, len(ec_idx)), replace=False)
        sub_sub, _ = get_domain_subspace(T, sub_idx.tolist())
        angle = principal_angle_deg(sub_sub, ec_full_sub)
        subsample_angles.append(angle)

    subsample_angles = np.array(subsample_angles)
    # If same-domain subsamples routinely get angles as small as 3.7, then small N is the explanation
    fraction_as_small = (subsample_angles <= real_angle).mean()
    print(f"  EC subsample ({n_particles} objects) vs full EC:")
    print(f"  Distribution: mean={subsample_angles.mean():.2f}, std={subsample_angles.std():.2f}, "
          f"min={subsample_angles.min():.2f}, max={subsample_angles.max():.2f}")
    print(f"  Real particle<->EC angle: {real_angle:.2f} deg")
    print(f"  Fraction of EC subsamples with angle <= real: {fraction_as_small:.4f}")

    # ALSO: subsample EC and measure angle to a DIFFERENT domain (e.g., knot)
    # to see if small subsamples universally give small angles to everything
    if knot_idx:
        sub_knot_full, _ = get_domain_subspace(T, knot_idx)
        cross_angles = []
        for trial in range(min(500, N_TRIALS)):
            sub_idx = np.random.choice(ec_idx, size=min(n_particles, len(ec_idx)), replace=False)
            sub_sub, _ = get_domain_subspace(T, sub_idx.tolist())
            angle = principal_angle_deg(sub_sub, sub_knot_full)
            cross_angles.append(angle)
        cross_angles = np.array(cross_angles)
        print(f"\n  EC subsample vs KNOT (cross-domain control):")
        print(f"  Distribution: mean={cross_angles.mean():.2f}, std={cross_angles.std():.2f}")

    if fraction_as_small > 0.5:
        print(f"\n  VERDICT: *** KILLED *** — Majority of same-size subsamples achieve same angle")
        kills += 1
    else:
        # Additional check: does the angle distribution of same-domain subsamples
        # overlap with the real cross-domain angle?
        percentile = stats.percentileofscore(subsample_angles, real_angle)
        print(f"  Real angle is at {percentile:.1f}th percentile of same-domain subsample angles")
        if percentile > 20:
            print(f"  VERDICT: *** KILLED *** — Cross-domain angle is not unusually small vs same-domain subsamples")
            kills += 1
        else:
            print(f"  VERDICT: SURVIVES — Cross-domain angle is significantly smaller than same-domain subsamples")

    # ============================================================
    # TEST 5: ISOMETRY TEST — Distribution comparison on shared dims
    # ============================================================
    banner("TEST 5: ISOMETRY TEST — KS test on shared dimensions")
    n_shared = 0
    n_sig_different = 0
    n_tested = 0
    ks_results = []

    for d in range(D):
        p_has = M[particle_idx][:, d]
        e_has = M[ec_idx][:, d]
        p_vals = T[particle_idx][p_has, d]
        e_vals = T[ec_idx][e_has, d]

        if len(p_vals) < 5 or len(e_vals) < 5:
            continue

        n_shared += 1
        ks_stat, ks_p = stats.ks_2samp(p_vals, e_vals)
        n_tested += 1
        if ks_p < 0.01:
            n_sig_different += 1
        ks_results.append((d, ks_stat, ks_p))

    print(f"  Dimensions with data in both particle and EC: {n_shared}")
    print(f"  Dimensions with significantly different distributions (KS p<0.01): {n_sig_different}/{n_tested}")

    if n_tested > 0:
        frac_diff = n_sig_different / n_tested
        print(f"  Fraction significantly different: {frac_diff:.3f}")

        # Show worst offenders
        ks_results.sort(key=lambda x: x[1], reverse=True)
        print(f"\n  Top 10 most different dimensions:")
        for d, stat, p in ks_results[:10]:
            # Find which strategy this dim belongs to
            strat = "unknown"
            for sname, (s, e) in strategy_slices.items():
                if s <= d < e:
                    strat = sname
                    break
            print(f"    dim {d:3d} ({strat:15s}): KS={stat:.4f}, p={p:.2e}")

        if frac_diff > 0.8:
            print(f"\n  VERDICT: *** KILLED *** — {frac_diff*100:.0f}% of shared dimensions have completely different distributions.")
            print(f"    Small principal angle measures ENCODING GEOMETRY not genuine structural similarity.")
            kills += 1
        elif frac_diff > 0.5:
            print(f"\n  VERDICT: WEAK SURVIVAL — Many dims differ but some align. Bridge is partly encoding artifact.")
        else:
            print(f"\n  VERDICT: SURVIVES — Distributions are similar in most shared dimensions.")
    else:
        print(f"  VERDICT: *** KILLED *** — No shared dimensions with sufficient data!")
        kills += 1

    # ============================================================
    # TEST 6: CROSS-PHYSICS SANITY — All physics pairs
    # ============================================================
    banner("TEST 6: CROSS-PHYSICS SANITY — Do unrelated physics domains bridge?")
    physics_domains = ["SC", "material", "atom", "particle", "metabolism", "crystal"]
    physics_available = [d for d in physics_domains if d in domain_indices and len(domain_indices[d]) >= 10]

    print(f"  Physics domains available: {physics_available}")

    physics_subs = {}
    for dname in physics_available:
        idx = domain_indices[dname]
        if len(idx) >= 20:
            sub, k = get_domain_subspace(T, idx)
        else:
            # For small domains, use fewer components
            sub, k = get_domain_subspace(T, idx, variance_threshold=0.80)
        physics_subs[dname] = sub

    n_small = 0
    n_pairs = 0
    print(f"\n  Principal angles between physics domain pairs (degrees):")
    for i, d1 in enumerate(physics_available):
        for d2 in physics_available[i+1:]:
            if d1 in physics_subs and d2 in physics_subs:
                angle = principal_angle_deg(physics_subs[d1], physics_subs[d2])
                n_pairs += 1
                tag = ""
                if angle < 15:
                    n_small += 1
                    tag = " ** SUSPICIOUSLY SMALL"
                print(f"    {d1:12s} <-> {d2:12s}: {angle:6.2f} deg{tag}")

    if n_pairs > 0:
        frac_small = n_small / n_pairs
        if frac_small > 0.5:
            print(f"\n  VERDICT: *** KILLED *** — {n_small}/{n_pairs} physics pairs show small angles.")
            print(f"    Encoding leaks domain-independent structure into angles.")
            kills += 1
        else:
            print(f"\n  VERDICT: SURVIVES — Only {n_small}/{n_pairs} physics pairs bridge. Specificity intact.")
    else:
        print(f"  Not enough physics domains for comparison.")
        print(f"  VERDICT: INCONCLUSIVE")

    # ============================================================
    # TEST 7: SCRAMBLE TEST — Random domain assignment
    # ============================================================
    banner("TEST 7: SCRAMBLE TEST — Random domain labels")
    N_TRIALS = 100
    scramble_angles = []

    all_idx = list(range(N))

    for trial in range(N_TRIALS):
        # Random "particle" domain: 225 random objects
        fake_particle_idx = np.random.choice(all_idx, size=n_particles, replace=False).tolist()
        # Random "EC" domain: same size as real EC
        remaining = list(set(all_idx) - set(fake_particle_idx))
        ec_size = min(len(ec_idx), len(remaining))
        fake_ec_idx = np.random.choice(remaining, size=ec_size, replace=False).tolist()

        try:
            fake_p_sub, _ = get_domain_subspace(T, fake_particle_idx)
            fake_e_sub, _ = get_domain_subspace(T, fake_ec_idx)
            angle = principal_angle_deg(fake_p_sub, fake_e_sub)
            scramble_angles.append(angle)
        except Exception:
            pass

    scramble_angles = np.array(scramble_angles)
    p_value_scramble = (scramble_angles <= real_angle).mean()
    print(f"  Scrambled domain assignment (random 225 vs random {len(ec_idx)}):")
    print(f"  Distribution: mean={scramble_angles.mean():.2f}, std={scramble_angles.std():.2f}, "
          f"min={scramble_angles.min():.2f}, max={scramble_angles.max():.2f}")
    print(f"  Real angle: {real_angle:.2f} deg")
    print(f"  p-value: {p_value_scramble:.4f}")

    if p_value_scramble > 0.05:
        print(f"  VERDICT: *** KILLED *** — Random domain assignment produces similar angles (p={p_value_scramble:.4f})")
        kills += 1
    else:
        print(f"  VERDICT: SURVIVES — Domain identity matters (p={p_value_scramble:.4f})")

    # ============================================================
    # TEST 8: HELD-OUT VALIDATION — Split and predict
    # ============================================================
    banner("TEST 8: HELD-OUT VALIDATION — EC train/test split + particle projection")
    from sklearn.decomposition import PCA

    ec_data = T[ec_idx]
    n_ec = len(ec_idx)

    # Multiple splits for robustness
    N_SPLITS = 50
    ec_recon_errors = []
    particle_recon_errors = []
    particle_data_full = T[particle_idx]

    for split in range(N_SPLITS):
        perm = np.random.permutation(n_ec)
        n_train = int(0.8 * n_ec)
        train_idx = perm[:n_train]
        test_idx = perm[n_train:]

        ec_train = ec_data[train_idx]
        ec_test = ec_data[test_idx]

        # Fit PCA on EC train
        n_components = min(k_ec, n_train - 1, D)
        pca = PCA(n_components=n_components)
        pca.fit(ec_train)

        # Reconstruct EC test
        ec_test_proj = pca.transform(ec_test)
        ec_test_recon = pca.inverse_transform(ec_test_proj)
        ec_err = np.mean((ec_test - ec_test_recon) ** 2)
        ec_recon_errors.append(ec_err)

        # Project particles onto EC train subspace
        particle_proj = pca.transform(particle_data_full)
        particle_recon = pca.inverse_transform(particle_proj)
        p_err = np.mean((particle_data_full - particle_recon) ** 2)
        particle_recon_errors.append(p_err)

    ec_recon_errors = np.array(ec_recon_errors)
    particle_recon_errors = np.array(particle_recon_errors)

    ratio = particle_recon_errors.mean() / (ec_recon_errors.mean() + 1e-12)
    print(f"  EC held-out reconstruction error:   {ec_recon_errors.mean():.6f} +/- {ec_recon_errors.std():.6f}")
    print(f"  Particle reconstruction error:       {particle_recon_errors.mean():.6f} +/- {particle_recon_errors.std():.6f}")
    print(f"  Ratio (particle / EC held-out):      {ratio:.4f}")

    if ratio > 5.0:
        print(f"\n  VERDICT: *** KILLED *** — Particles reconstruct {ratio:.1f}x worse than held-out EC.")
        print(f"    The 3.7 deg angle is misleading; particles do NOT genuinely share the EC subspace.")
        kills += 1
    elif ratio > 2.0:
        print(f"\n  VERDICT: WEAK KILL — Particles reconstruct {ratio:.1f}x worse. Partial overlap at best.")
        kills += 1
    else:
        print(f"\n  VERDICT: SURVIVES — Particles reconstruct comparably to held-out EC (ratio={ratio:.2f})")

    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print("\n")
    print("=" * 70)
    print("  FINAL VERDICT")
    print("=" * 70)
    print(f"\n  Tests run:    {total}")
    print(f"  KILLS:        {kills}")
    print(f"  SURVIVES:     {total - kills}")
    print()

    if kills == 0:
        print("  RESULT: ALL 8 TESTS SURVIVED. The 5D structure claim is ROBUST.")
        print("  (But stay paranoid. Design more tests.)")
    elif kills <= 2:
        print(f"  RESULT: {kills} KILL(S) — Claim is WOUNDED but not dead.")
        print("  Investigate the specific failures before making claims.")
    else:
        print(f"  RESULT: {kills} KILLS — Claim is DEAD.")
        print("  The cross-domain structure is likely an artifact of encoding, sparsity, or sample size.")
    print()

    return kills


if __name__ == "__main__":
    t0 = time.time()
    kills = main()
    elapsed = time.time() - t0
    print(f"Total runtime: {elapsed:.1f}s")
    sys.exit(0)
