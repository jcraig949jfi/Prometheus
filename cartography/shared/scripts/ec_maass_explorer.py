"""
EC–Maass Coupling Explorer with L-function Bridge Analysis.

Investigates the 2 extra coupling channels found by Megethos-zeroed
TT-Cross sweep (bond=17 vs null=15).

Tasks:
  1. Load L-functions from lfunc_lfunctions.csv into the dissection tensor
  2. Identify the 2 extra EC–maass coupling channels via SVD
  3. Test whether L-functions bridge EC and maass
  4. Explore the EC–maass nearest-neighbor landscape

Machine: M1 (Skullport), RTX 5060 Ti 17GB
"""
import sys
import json
import time
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F_torch
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "cartography/shared/scripts"))

from dissection_tensor import (
    DissectionTensor, DataLoaders, StrategyExtractors, MathObject, DEVICE
)

LFUNC_CSV = Path("F:/lmfdb_local/lfunc_lfunctions.csv")
OUTPUT_PATH = ROOT / "cartography/convergence/data/ec_maass_exploration.json"

# ============================================================
# TASK 1: L-function loader
# ============================================================
def load_lfunctions(max_n=100000):
    """Load L-functions from pipe-delimited CSV into MathObject list."""
    print(f"\n{'='*60}")
    print(f"Loading L-functions from {LFUNC_CSV}")
    print(f"  Reading first {max_n} rows...")

    df = pd.read_csv(
        LFUNC_CSV, sep='|', nrows=max_n,
        usecols=['origin', 'conductor', 'degree', 'motivic_weight',
                 'self_dual', 'types', 'st_group', 'symmetry_type'],
        low_memory=False,
    )
    print(f"  Loaded {len(df)} rows")

    # Clean columns
    df['conductor'] = pd.to_numeric(df['conductor'], errors='coerce')
    df['degree'] = pd.to_numeric(df['degree'], errors='coerce')
    df['motivic_weight'] = pd.to_numeric(df['motivic_weight'], errors='coerce')
    df['self_dual'] = df['self_dual'].map({True: 1, False: 0, 'True': 1, 'False': 0, 't': 1, 'f': 0})

    # Drop rows without conductor
    df = df.dropna(subset=['conductor'])
    df['conductor'] = df['conductor'].astype(int)
    df['degree'] = df['degree'].fillna(0).astype(int)
    df['motivic_weight'] = df['motivic_weight'].fillna(0).astype(int)
    df['self_dual'] = df['self_dual'].fillna(0).astype(int)

    # Parse origin to extract domain category
    def origin_category(origin):
        if pd.isna(origin):
            return "Unknown"
        s = str(origin)
        if s.startswith("EllipticCurve"):
            return "EC_Lfunc"
        elif "Maass" in s or "maass" in s:
            return "Maass_Lfunc"
        elif s.startswith("ModularForm"):
            return "MF_Lfunc"
        elif s.startswith("Artin"):
            return "Artin_Lfunc"
        elif s.startswith("Genus2"):
            return "Genus2_Lfunc"
        elif s.startswith("SymmetricPower"):
            return "SymPow_Lfunc"
        elif s.startswith("NumberField"):
            return "NF_Lfunc"
        else:
            return "Other_Lfunc"

    df['origin_cat'] = df['origin'].apply(origin_category)

    # Report origin distribution
    print(f"\n  Origin categories:")
    for cat, cnt in df['origin_cat'].value_counts().items():
        print(f"    {cat:20s}: {cnt:6d}")

    ext = StrategyExtractors
    objects = []

    for idx, row in df.iterrows():
        cond = int(row['conductor'])
        deg = int(row['degree'])
        mw = int(row['motivic_weight'])
        sd = int(row['self_dual'])

        obj = MathObject(
            obj_id=f"lfunc_{idx}",
            domain="Lfunc",
            label=str(row.get('origin', ''))[:80],
            signatures={},
            raw={
                "conductor": cond,
                "degree": deg,
                "motivic_weight": mw,
                "self_dual": sd,
                "origin": str(row.get('origin', '')),
                "origin_cat": row['origin_cat'],
                "types": str(row.get('types', '')),
                "st_group": str(row.get('st_group', '')),
                "symmetry_type": str(row.get('symmetry_type', '')),
            },
        )

        # s13: conductor as discriminant
        obj.signatures["s13"] = ext.s13_discriminant(cond)

        # s7_cond: p-adic valuation of conductor
        obj.signatures["s7_cond"] = ext.s7_padic(cond)

        # s21_auto: from degree, motivic_weight, self_dual
        # Build a pseudo-automorphic signature
        s21 = np.zeros(8, dtype=np.float32)
        s21[0] = 1.0  # spectral type: L-functions are automorphic by definition
        s21[1] = 1.0 if sd else 0.0  # parity from self_dual
        s21[2] = 0.0  # multiplicativity: unknown without coefficients
        s21[3] = float(sd)  # functional equation: self-dual -> even
        s21[4] = np.log1p(float(cond)) / max(float(mw), 1.0) if mw > 0 else np.log1p(float(cond))
        s21[5] = 1.0 / max(float(deg), 1.0)  # coefficient field degree proxy
        s21[6] = 0.0  # Hecke multiplicativity: unknown
        s21[7] = 0.5  # Satake: neutral
        obj.signatures["s21_auto"] = s21

        # s19_ade: from degree (ADE rank ~ degree)
        obj.signatures["s19_ade"] = ext.s19_ade_classify(
            [deg, mw], method="mckay")

        # s3_ap: mod-p of [conductor, degree, motivic_weight]
        vals = [cond, deg, mw]
        obj.signatures["s3_ap"] = ext.s3_mod_p(vals)

        objects.append(obj)

    print(f"  Built {len(objects)} L-function MathObjects")
    return objects, df


# ============================================================
# TASK 2: Identify the 2 extra coupling channels
# ============================================================
def identify_coupling_channels(dt, results):
    """SVD of the EC-maass coupling matrix to find the extra channels."""
    print(f"\n{'='*60}")
    print(f"TASK 2: Identify the 2 extra EC-maass coupling channels")
    print(f"{'='*60}")

    ec_idx = torch.tensor(dt.domain_indices["EC"], device=DEVICE)
    maass_idx = torch.tensor(dt.domain_indices["maass"], device=DEVICE)

    print(f"  EC objects: {len(ec_idx)}")
    print(f"  maass objects: {len(maass_idx)}")

    # Get all dimensions EXCEPT s13 (Megethos-zeroed)
    s13_start, s13_end = dt._strategy_slices["s13"]
    all_cols = list(range(0, s13_start)) + list(range(s13_end, dt.TOTAL_DIMS))
    col_idx = torch.tensor(all_cols, device=DEVICE)

    # Extract and L2-normalize
    ec_vecs = dt.tensor[ec_idx][:, col_idx]  # [Nec, D']
    ec_mask = dt.mask[ec_idx][:, col_idx]
    maass_vecs = dt.tensor[maass_idx][:, col_idx]  # [Nm, D']
    maass_mask = dt.mask[maass_idx][:, col_idx]

    # Zero where no data
    ec_vecs = ec_vecs * ec_mask.float()
    maass_vecs = maass_vecs * maass_mask.float()

    # L2-normalize each row
    ec_norm = ec_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
    maass_norm = maass_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
    ec_normed = ec_vecs / ec_norm
    maass_normed = maass_vecs / maass_norm

    # Subsample for speed: max 2000 each (SVD is O(n^3))
    max_ec = min(2000, len(ec_idx))
    max_maass = min(2000, len(maass_idx))
    perm_ec = torch.randperm(len(ec_idx), device=DEVICE)[:max_ec]
    perm_maass = torch.randperm(len(maass_idx), device=DEVICE)[:max_maass]
    ec_sub = ec_normed[perm_ec]
    maass_sub = maass_normed[perm_maass]

    # Coupling matrix C[i,j] = cosine_sim(EC_i, maass_j)
    print(f"  Building coupling matrix [{max_ec} x {max_maass}]...")
    C = ec_sub @ maass_sub.T  # [max_ec, max_maass]
    print(f"  Coupling matrix stats: mean={C.mean():.4f}, std={C.std():.4f}, "
          f"min={C.min():.4f}, max={C.max():.4f}")

    # SVD
    print(f"  Computing SVD...")
    U, S, Vh = torch.linalg.svd(C, full_matrices=False)
    print(f"  Top 20 singular values: {S[:20].cpu().numpy().round(3)}")

    # Null model: independently shuffle each column of EC vectors to break
    # cross-domain feature coupling, then recompute C and SVD.
    # Row-permutation of C preserves SVs (it's unitary), so we must break
    # the feature structure itself.
    print(f"  Computing null (30 column-shuffled permutations)...")
    null_svs = []
    for _ in range(30):
        ec_shuffled = ec_sub.clone()
        for d in range(ec_shuffled.shape[1]):
            perm = torch.randperm(ec_shuffled.shape[0], device=DEVICE)
            ec_shuffled[:, d] = ec_shuffled[perm, d]
        # Re-normalize after shuffling
        ec_shuf_norm = ec_shuffled.norm(dim=1, keepdim=True).clamp(min=1e-8)
        ec_shuffled = ec_shuffled / ec_shuf_norm
        C_null = ec_shuffled @ maass_sub.T
        _, S_null, _ = torch.linalg.svd(C_null, full_matrices=False)
        null_svs.append(S_null[:20].cpu().numpy())
    null_svs = np.array(null_svs)
    null_mean = null_svs.mean(axis=0)
    null_std = null_svs.std(axis=0)

    # Which singular values exceed null?
    real_sv = S[:20].cpu().numpy()
    z_scores = (real_sv - null_mean) / np.maximum(null_std, 1e-8)

    print(f"\n  Singular value analysis (top 20):")
    print(f"  {'SV':>3s}  {'Real':>10s}  {'Null mean':>10s}  {'Null std':>10s}  {'z-score':>10s}  {'Exceeds?':>8s}")
    n_exceeding = 0
    for i in range(20):
        exceeds = z_scores[i] > 3.0  # 3-sigma threshold
        if exceeds:
            n_exceeding += 1
        print(f"  {i:3d}  {real_sv[i]:10.3f}  {null_mean[i]:10.3f}  {null_std[i]:10.3f}  "
              f"{z_scores[i]:10.2f}  {'YES' if exceeds else 'no':>8s}")

    print(f"\n  Channels exceeding null: {n_exceeding}")

    # For each exceeding channel: identify which features drive it
    # U[:, k] is the EC-side singular vector, Vh[k, :] is the maass-side
    # Correlate with individual tensor dimensions
    channel_report = []
    strategy_names = list(dt._strategy_slices.keys())

    for k in range(min(n_exceeding, 10)):
        if z_scores[k] <= 3.0:
            break
        print(f"\n  --- Channel {k} (SV={real_sv[k]:.3f}, z={z_scores[k]:.1f}) ---")

        # EC-side: which features load onto U[:, k]?
        u_k = U[:, k].cpu().numpy()  # [max_ec]
        v_k = Vh[k, :].cpu().numpy()  # [max_maass]

        # For each tensor dimension, compute correlation with U[:, k]
        ec_sub_cpu = ec_sub.cpu().numpy()
        maass_sub_cpu = maass_sub.cpu().numpy()

        # EC-side feature loadings
        ec_loadings = []
        for d in range(ec_sub_cpu.shape[1]):
            col = ec_sub_cpu[:, d]
            if np.std(col) < 1e-8:
                ec_loadings.append(0.0)
            else:
                ec_loadings.append(float(np.corrcoef(u_k, col)[0, 1]))
        ec_loadings = np.array(ec_loadings)

        # maass-side feature loadings
        maass_loadings = []
        for d in range(maass_sub_cpu.shape[1]):
            col = maass_sub_cpu[:, d]
            if np.std(col) < 1e-8:
                maass_loadings.append(0.0)
            else:
                maass_loadings.append(float(np.corrcoef(v_k, col)[0, 1]))
        maass_loadings = np.array(maass_loadings)

        # Map column index back to strategy name + dim within strategy
        def col_to_strategy(col_local):
            """Map local column index (s13-excluded) to strategy name + dim."""
            global_col = all_cols[col_local]
            for sname, (start, end) in dt._strategy_slices.items():
                if start <= global_col < end:
                    return sname, global_col - start
            return "unknown", 0

        # Top EC-side features
        top_ec = np.argsort(np.abs(ec_loadings))[-5:][::-1]
        print(f"  EC-side top features:")
        ec_drivers = []
        for ti in top_ec:
            sname, sdim = col_to_strategy(ti)
            r = ec_loadings[ti]
            print(f"    {sname} dim {sdim}: r={r:.3f}")
            ec_drivers.append({"strategy": sname, "dim": int(sdim), "r": float(r)})

        # Top maass-side features
        top_maass = np.argsort(np.abs(maass_loadings))[-5:][::-1]
        print(f"  maass-side top features:")
        maass_drivers = []
        for ti in top_maass:
            sname, sdim = col_to_strategy(ti)
            r = maass_loadings[ti]
            print(f"    {sname} dim {sdim}: r={r:.3f}")
            maass_drivers.append({"strategy": sname, "dim": int(sdim), "r": float(r)})

        channel_report.append({
            "channel": k,
            "singular_value": float(real_sv[k]),
            "z_score": float(z_scores[k]),
            "ec_drivers": ec_drivers,
            "maass_drivers": maass_drivers,
        })

    results["task2_coupling_channels"] = {
        "n_exceeding_null": int(n_exceeding),
        "singular_values": real_sv.tolist(),
        "null_mean": null_mean.tolist(),
        "z_scores": z_scores.tolist(),
        "channels": channel_report,
    }

    # Clean up
    del C, U, S, Vh, ec_sub, maass_sub, ec_normed, maass_normed
    torch.cuda.empty_cache()

    return results


# ============================================================
# TASK 3: Do L-functions bridge EC and maass?
# ============================================================
def test_lfunc_bridge(dt, results):
    """Test whether L-functions serve as a bridge between EC and maass."""
    print(f"\n{'='*60}")
    print(f"TASK 3: Do L-functions bridge EC and maass?")
    print(f"{'='*60}")

    # Megethos-zeroed: exclude s13
    s13_start, s13_end = dt._strategy_slices["s13"]
    all_cols = list(range(0, s13_start)) + list(range(s13_end, dt.TOTAL_DIMS))
    col_idx = torch.tensor(all_cols, device=DEVICE)

    def get_domain_vecs(domain, max_n=5000):
        """Get L2-normalized vectors for a domain, s13-zeroed."""
        idx = dt.domain_indices[domain]
        if not idx:
            return None, None
        idx_t = torch.tensor(idx[:max_n], device=DEVICE)
        vecs = dt.tensor[idx_t][:, col_idx]
        mask = dt.mask[idx_t][:, col_idx]
        vecs = vecs * mask.float()
        norms = vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
        return vecs / norms, idx_t

    def compute_bond_dimension(vecs_a, vecs_b, name_a, name_b, n_null=20):
        """Compute effective bond dimension between two domain sets.
        Uses SVD of coupling matrix; bond dim = # singular values > null."""
        max_a = min(2000, len(vecs_a))
        max_b = min(2000, len(vecs_b))
        perm_a = torch.randperm(len(vecs_a), device=DEVICE)[:max_a]
        perm_b = torch.randperm(len(vecs_b), device=DEVICE)[:max_b]
        a_sub = vecs_a[perm_a]
        b_sub = vecs_b[perm_b]

        C = a_sub @ b_sub.T
        _, S, _ = torch.linalg.svd(C, full_matrices=False)
        real_sv = S[:30].cpu().numpy()

        # Null: column-shuffle domain A to break feature coupling
        null_svs = []
        for _ in range(n_null):
            a_shuf = a_sub.clone()
            for d in range(a_shuf.shape[1]):
                perm = torch.randperm(a_shuf.shape[0], device=DEVICE)
                a_shuf[:, d] = a_shuf[perm, d]
            a_shuf_norm = a_shuf.norm(dim=1, keepdim=True).clamp(min=1e-8)
            a_shuf = a_shuf / a_shuf_norm
            C_null = a_shuf @ b_sub.T
            _, S_null, _ = torch.linalg.svd(C_null, full_matrices=False)
            null_svs.append(S_null[:30].cpu().numpy())
        null_svs = np.array(null_svs)
        null_mean = null_svs.mean(axis=0)
        null_std = null_svs.std(axis=0)
        z_scores = (real_sv - null_mean) / np.maximum(null_std, 1e-8)

        bond_dim = int(np.sum(z_scores > 3.0))
        null_bond = int(np.median([np.sum((s - null_mean) / np.maximum(null_std, 1e-8) > 3.0)
                                    for s in null_svs]))

        print(f"  {name_a} <-> {name_b}: bond_dim={bond_dim}, null~{null_bond}, "
              f"top SV={real_sv[0]:.3f}, top z={z_scores[0]:.1f}")

        del C, S
        torch.cuda.empty_cache()

        return {
            "bond_dim": bond_dim,
            "null_bond": null_bond,
            "exceeds_null": bond_dim > null_bond,
            "top_sv": float(real_sv[0]),
            "top_z": float(z_scores[0]),
            "singular_values": real_sv[:10].tolist(),
            "z_scores": z_scores[:10].tolist(),
        }

    # Get vectors for each domain
    ec_vecs, _ = get_domain_vecs("EC")
    maass_vecs, _ = get_domain_vecs("maass")
    lfunc_vecs, _ = get_domain_vecs("Lfunc")

    if ec_vecs is None or maass_vecs is None or lfunc_vecs is None:
        print("  ERROR: Missing domain data")
        return results

    # 1. EC-maass bond (baseline)
    print(f"\n  Bond dimension analysis:")
    ec_maass = compute_bond_dimension(ec_vecs, maass_vecs, "EC", "maass")

    # 2. EC-Lfunc bond
    ec_lfunc = compute_bond_dimension(ec_vecs, lfunc_vecs, "EC", "Lfunc")

    # 3. maass-Lfunc bond
    maass_lfunc = compute_bond_dimension(maass_vecs, lfunc_vecs, "maass", "Lfunc")

    # 4. Check if L-functions from EC origin couple to maass domain
    # and L-functions from Maass origin couple to EC domain
    lfunc_objs = [o for o in dt.objects if o.domain == "Lfunc"]

    # Split L-functions by origin category
    ec_origin_idx = [i for i, o in enumerate(dt.objects)
                     if o.domain == "Lfunc" and o.raw.get("origin_cat") == "EC_Lfunc"]
    maass_origin_idx = [i for i, o in enumerate(dt.objects)
                        if o.domain == "Lfunc" and o.raw.get("origin_cat") == "Maass_Lfunc"]
    mf_origin_idx = [i for i, o in enumerate(dt.objects)
                     if o.domain == "Lfunc" and o.raw.get("origin_cat") == "MF_Lfunc"]

    print(f"\n  L-function origin breakdown:")
    print(f"    EC_Lfunc: {len(ec_origin_idx)}")
    print(f"    Maass_Lfunc: {len(maass_origin_idx)}")
    print(f"    MF_Lfunc: {len(mf_origin_idx)}")

    cross_coupling = {}

    # EC-origin L-funcs -> maass domain (cross-coupling test)
    if ec_origin_idx and len(ec_origin_idx) > 10:
        ec_origin_t = torch.tensor(ec_origin_idx[:3000], device=DEVICE)
        ec_lf_vecs = dt.tensor[ec_origin_t][:, col_idx]
        ec_lf_vecs = ec_lf_vecs * dt.mask[ec_origin_t][:, col_idx].float()
        ec_lf_norms = ec_lf_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
        ec_lf_normed = ec_lf_vecs / ec_lf_norms

        cc_ec_to_maass = compute_bond_dimension(ec_lf_normed, maass_vecs, "EC_Lfunc", "maass")
        cross_coupling["EC_Lfunc_to_maass"] = cc_ec_to_maass
        del ec_lf_vecs, ec_lf_normed
        torch.cuda.empty_cache()

    # Maass-origin L-funcs -> EC domain
    if maass_origin_idx and len(maass_origin_idx) > 10:
        maass_origin_t = torch.tensor(maass_origin_idx[:3000], device=DEVICE)
        maass_lf_vecs = dt.tensor[maass_origin_t][:, col_idx]
        maass_lf_vecs = maass_lf_vecs * dt.mask[maass_origin_t][:, col_idx].float()
        maass_lf_norms = maass_lf_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
        maass_lf_normed = maass_lf_vecs / maass_lf_norms

        cc_maass_to_ec = compute_bond_dimension(maass_lf_normed, ec_vecs, "Maass_Lfunc", "EC")
        cross_coupling["Maass_Lfunc_to_EC"] = cc_maass_to_ec
        del maass_lf_vecs, maass_lf_normed
        torch.cuda.empty_cache()

    # MF-origin L-funcs -> both (modularity check)
    if mf_origin_idx and len(mf_origin_idx) > 10:
        mf_origin_t = torch.tensor(mf_origin_idx[:3000], device=DEVICE)
        mf_lf_vecs = dt.tensor[mf_origin_t][:, col_idx]
        mf_lf_vecs = mf_lf_vecs * dt.mask[mf_origin_t][:, col_idx].float()
        mf_lf_norms = mf_lf_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
        mf_lf_normed = mf_lf_vecs / mf_lf_norms

        cc_mf_to_ec = compute_bond_dimension(mf_lf_normed, ec_vecs, "MF_Lfunc", "EC")
        cc_mf_to_maass = compute_bond_dimension(mf_lf_normed, maass_vecs, "MF_Lfunc", "maass")
        cross_coupling["MF_Lfunc_to_EC"] = cc_mf_to_ec
        cross_coupling["MF_Lfunc_to_maass"] = cc_mf_to_maass
        del mf_lf_vecs, mf_lf_normed
        torch.cuda.empty_cache()

    # Interpretation
    bridge = ec_lfunc.get("exceeds_null", False) and maass_lfunc.get("exceeds_null", False)
    print(f"\n  VERDICT: L-functions {'ARE' if bridge else 'are NOT'} a bridge")
    if bridge:
        print(f"    EC-Lfunc bond exceeds null ({ec_lfunc['bond_dim']} > {ec_lfunc['null_bond']})")
        print(f"    maass-Lfunc bond exceeds null ({maass_lfunc['bond_dim']} > {maass_lfunc['null_bond']})")
    else:
        print(f"    EC-Lfunc: bond={ec_lfunc['bond_dim']}, null={ec_lfunc['null_bond']}")
        print(f"    maass-Lfunc: bond={maass_lfunc['bond_dim']}, null={maass_lfunc['null_bond']}")

    results["task3_lfunc_bridge"] = {
        "EC_maass": ec_maass,
        "EC_Lfunc": ec_lfunc,
        "maass_Lfunc": maass_lfunc,
        "cross_coupling": cross_coupling,
        "is_bridge": bridge,
    }

    del ec_vecs, maass_vecs, lfunc_vecs
    torch.cuda.empty_cache()

    return results


# ============================================================
# TASK 4: Explore the EC-maass neighborhood
# ============================================================
def explore_neighborhood(dt, results):
    """Find nearest EC-maass pairs and analyze their arithmetic properties."""
    print(f"\n{'='*60}")
    print(f"TASK 4: EC-maass neighborhood exploration")
    print(f"{'='*60}")

    ec_indices = dt.domain_indices["EC"]
    maass_indices = dt.domain_indices["maass"]

    # Megethos-zeroed columns
    s13_start, s13_end = dt._strategy_slices["s13"]
    all_cols = list(range(0, s13_start)) + list(range(s13_end, dt.TOTAL_DIMS))
    col_idx = torch.tensor(all_cols, device=DEVICE)

    # Get all EC and maass vectors
    ec_idx_t = torch.tensor(ec_indices, device=DEVICE)
    maass_idx_t = torch.tensor(maass_indices, device=DEVICE)

    ec_vecs = dt.tensor[ec_idx_t][:, col_idx] * dt.mask[ec_idx_t][:, col_idx].float()
    maass_vecs = dt.tensor[maass_idx_t][:, col_idx] * dt.mask[maass_idx_t][:, col_idx].float()

    # L2-normalize
    ec_norms = ec_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
    maass_norms = maass_vecs.norm(dim=1, keepdim=True).clamp(min=1e-8)
    ec_normed = ec_vecs / ec_norms
    maass_normed = maass_vecs / maass_norms

    Nec = len(ec_indices)
    Nm = len(maass_indices)
    print(f"  EC: {Nec}, maass: {Nm}")

    # For each EC, find nearest maass neighbor
    # Process in batches to avoid OOM
    batch_size = 2000
    best_sim = torch.full((Nec,), -float('inf'), device=DEVICE)
    best_maass_idx = torch.zeros(Nec, device=DEVICE, dtype=torch.long)

    print(f"  Finding nearest maass neighbor for each EC...")
    for start in range(0, Nec, batch_size):
        end = min(start + batch_size, Nec)
        chunk = ec_normed[start:end]  # [chunk, D']
        sims = chunk @ maass_normed.T  # [chunk, Nm]
        max_sims, max_idx = sims.max(dim=1)
        best_sim[start:end] = max_sims
        best_maass_idx[start:end] = max_idx
        del sims
        torch.cuda.empty_cache()

    best_sim_np = best_sim.cpu().numpy()
    best_maass_idx_np = best_maass_idx.cpu().numpy()

    # Get top 100 closest pairs
    top100 = np.argsort(best_sim_np)[-100:][::-1]

    print(f"\n  Top 100 closest EC-maass pairs:")
    print(f"  {'Rank':>4s}  {'Sim':>7s}  {'EC_ID':>30s}  {'EC_cond':>8s}  {'Maass_ID':>30s}  {'Maass_level':>11s}  {'Match?':>6s}")

    pairs = []
    conductor_match = 0
    conductor_no_match = 0

    for rank_i, ec_local in enumerate(top100):
        ec_global = ec_indices[ec_local]
        maass_local = int(best_maass_idx_np[ec_local])
        maass_global = maass_indices[maass_local]

        ec_obj = dt.objects[ec_global]
        maass_obj = dt.objects[maass_global]

        ec_cond = ec_obj.raw.get("conductor", "?")
        maass_level = maass_obj.raw.get("level", "?")
        sim = float(best_sim_np[ec_local])

        match = str(ec_cond) == str(maass_level)
        if match:
            conductor_match += 1
        else:
            conductor_no_match += 1

        pair_info = {
            "rank": rank_i + 1,
            "similarity": sim,
            "ec_id": ec_obj.obj_id,
            "ec_conductor": int(ec_cond) if ec_cond != "?" else None,
            "ec_rank": ec_obj.raw.get("rank"),
            "ec_torsion": ec_obj.raw.get("torsion"),
            "maass_id": maass_obj.obj_id,
            "maass_level": int(maass_level) if maass_level != "?" else None,
            "maass_spectral_parameter": maass_obj.raw.get("spectral_parameter"),
            "maass_symmetry": maass_obj.raw.get("symmetry"),
            "conductor_level_match": match,
        }
        pairs.append(pair_info)

        if rank_i < 20:
            print(f"  {rank_i+1:4d}  {sim:7.4f}  {ec_obj.obj_id:>30s}  {str(ec_cond):>8s}  "
                  f"{maass_obj.obj_id:>30s}  {str(maass_level):>11s}  {'YES' if match else 'no':>6s}")

    print(f"\n  Conductor/level matches: {conductor_match}/100")
    print(f"  Non-matching close pairs: {conductor_no_match}/100")

    # Analyze the non-matching pairs more carefully
    non_matching = [p for p in pairs if not p["conductor_level_match"]]
    if non_matching:
        print(f"\n  Non-matching pairs — shared arithmetic properties:")
        cond_levels = [(p["ec_conductor"], p["maass_level"]) for p in non_matching
                       if p["ec_conductor"] is not None and p["maass_level"] is not None]

        if cond_levels:
            # Check GCD patterns
            from math import gcd
            gcd_vals = [gcd(c, l) for c, l in cond_levels]
            ratio_vals = [c / l if l > 0 else float('inf') for c, l in cond_levels]

            print(f"    GCD distribution: mean={np.mean(gcd_vals):.1f}, "
                  f"median={np.median(gcd_vals):.1f}, max={max(gcd_vals)}")
            print(f"    Conductor/level ratio: mean={np.mean([r for r in ratio_vals if r < 1e6]):.2f}, "
                  f"median={np.median([r for r in ratio_vals if r < 1e6]):.2f}")

            # Factor analysis: do they share prime factors?
            def prime_factors(n):
                n = abs(int(n))
                factors = set()
                d = 2
                while d * d <= n and d < 1000:
                    while n % d == 0:
                        factors.add(d)
                        n //= d
                    d += 1
                if n > 1:
                    factors.add(n)
                return factors

            shared_primes_count = 0
            for c, l in cond_levels[:50]:
                pf_c = prime_factors(c)
                pf_l = prime_factors(l)
                if pf_c & pf_l:
                    shared_primes_count += 1

            print(f"    Pairs sharing prime factors: {shared_primes_count}/{min(len(cond_levels), 50)}")

    # Overall similarity distribution
    print(f"\n  Overall similarity distribution:")
    print(f"    Mean: {np.mean(best_sim_np):.4f}")
    print(f"    Median: {np.median(best_sim_np):.4f}")
    print(f"    Std: {np.std(best_sim_np):.4f}")
    print(f"    Max: {np.max(best_sim_np):.4f}")
    print(f"    Min: {np.min(best_sim_np):.4f}")

    results["task4_neighborhood"] = {
        "top_100_pairs": pairs,
        "conductor_level_matches": conductor_match,
        "non_matching_count": conductor_no_match,
        "similarity_stats": {
            "mean": float(np.mean(best_sim_np)),
            "median": float(np.median(best_sim_np)),
            "std": float(np.std(best_sim_np)),
            "max": float(np.max(best_sim_np)),
            "min": float(np.min(best_sim_np)),
        },
    }

    del ec_vecs, maass_vecs, ec_normed, maass_normed, best_sim, best_maass_idx
    torch.cuda.empty_cache()

    return results


# ============================================================
# Main
# ============================================================
def main():
    t0 = time.time()
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

    # ---- Load EC and maass ----
    print(f"{'='*60}")
    print(f"Loading EC and maass data...")
    print(f"{'='*60}")
    ec_objects = DataLoaders.load_ec()
    maass_objects = DataLoaders.load_maass_forms(max_n=15000)
    print(f"  EC: {len(ec_objects)}, maass: {len(maass_objects)}")

    results["counts"] = {
        "EC": len(ec_objects),
        "maass": len(maass_objects),
    }

    # ---- Load L-functions ----
    lfunc_objects, lfunc_df = load_lfunctions(max_n=100000)
    results["counts"]["Lfunc"] = len(lfunc_objects)

    # ---- Build tensor ----
    print(f"\n{'='*60}")
    print(f"Building DissectionTensor with 3 domains...")
    print(f"{'='*60}")
    dt = DissectionTensor()
    dt.add_objects(ec_objects)
    dt.add_objects(maass_objects)
    dt.add_objects(lfunc_objects)
    dt.build()

    # ---- Megethos-zeroed normalization ----
    print(f"\nApplying Megethos-zeroed normalization...")
    dt.normalize(n_bins=10)

    # ---- Task 2: Coupling channels ----
    results = identify_coupling_channels(dt, results)

    # ---- Task 3: L-function bridge ----
    results = test_lfunc_bridge(dt, results)

    # ---- Task 4: Neighborhood exploration ----
    results = explore_neighborhood(dt, results)

    # ---- Save results ----
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_PATH}")

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
    print(f"{'='*60}")
    print(f"DONE")


if __name__ == "__main__":
    main()
