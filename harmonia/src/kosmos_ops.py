"""
Kosmos Operations — Arithmetic and geometry of mathematical objects in the Kosmos.

The Kosmos is an 11.4-dimensional measured coordinate system discovered by PCA
over all mathematical domains.  Every mathematical object maps to a point in
this space (after padding raw features to 28 and projecting through a shared
SVD rotation).

This module implements five operations on those points:

  1. Distance   — L2 distance between any two objects
  2. Nearest    — k-nearest neighbors across domains
  3. Addition   — vector sum in Kosmos space; search for real objects at the tip
  4. Projection — extract a single Kosmos axis ("phoneme") from an object
  5. Analogy    — a - b + c = ?  (Word2Vec-style analogical reasoning)

All operations recompute the PCA rotation from scratch: load all requested
domains, subsample to 3000, pad to 28, SVD.  The first 15 PCs are kept
(capturing > 99 % of variance); the effective dimensionality is ~11.4.
"""

import torch
import numpy as np
import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from harmonia.src.domain_index import (
    DomainIndex, load_domains, DOMAIN_LOADERS, _normalize,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MAX_FEATURES = 28          # pad every domain to this width
N_PCS        = 15          # number of principal components to keep
SUBSAMPLE    = 3000        # per-domain subsample for computing the rotation


def _pad_features(features: torch.Tensor, width: int = MAX_FEATURES) -> torch.Tensor:
    """Pad (or truncate) feature columns to *width*."""
    n, d = features.shape
    if d >= width:
        return features[:, :width]
    return torch.cat([features, torch.zeros(n, width - d)], dim=1)


def _build_pca(domains: dict[str, DomainIndex],
               subsample: int = SUBSAMPLE,
               n_pcs: int = N_PCS):
    """
    Compute the PCA rotation matrix from a pooled, subsampled set of all
    domain features.

    Returns
    -------
    mean   : (28,)  column means used for centering
    Vt     : (n_pcs, 28)  right-singular vectors (rotation matrix)
    S      : (n_pcs,) singular values
    """
    blocks = []
    for dom in domains.values():
        padded = _pad_features(dom.features)
        if padded.shape[0] > subsample:
            idx = torch.randperm(padded.shape[0])[:subsample]
            padded = padded[idx]
        blocks.append(padded)

    pooled = torch.cat(blocks, dim=0)          # (N_total, 28)
    mean = pooled.mean(dim=0)                   # (28,)
    centered = pooled - mean

    # Economy SVD — we only need the top n_pcs components
    U, S, Vt = torch.linalg.svd(centered, full_matrices=False)
    Vt = Vt[:n_pcs]                             # (n_pcs, 28)
    S  = S[:n_pcs]
    return mean, Vt, S


def _project(features: torch.Tensor,
             mean: torch.Tensor,
             Vt: torch.Tensor) -> torch.Tensor:
    """Project raw (padded) features into PCA space.  Returns (N, n_pcs)."""
    padded = _pad_features(features)
    centered = padded - mean
    return centered @ Vt.T                      # (N, n_pcs)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class KosmosSpace:
    """Container holding the PCA rotation and projected coordinates for
    every loaded domain."""
    domains: dict                # name -> DomainIndex
    mean: torch.Tensor           # (28,)
    Vt: torch.Tensor             # (n_pcs, 28)
    S: torch.Tensor              # (n_pcs,)
    coords: dict                 # name -> (N, n_pcs)  projected coords
    labels: dict                 # name -> list[str]

    # --- raw feature lookup helpers used by conductor/level extraction ---
    _raw_features: dict = field(default_factory=dict, repr=False)


def build_kosmos(*domain_names: str, subsample: int = SUBSAMPLE) -> KosmosSpace:
    """
    Load domains, compute PCA, project everything.

    >>> ks = build_kosmos("elliptic_curves", "modular_forms")
    """
    domains = load_domains(*domain_names)
    mean, Vt, S = _build_pca(domains, subsample=subsample)

    coords, labels_map, raw_map = {}, {}, {}
    for name, dom in domains.items():
        coords[name] = _project(dom.features, mean, Vt)
        labels_map[name] = dom.labels
        raw_map[name] = dom.features.clone()

    return KosmosSpace(
        domains=domains,
        mean=mean,
        Vt=Vt,
        S=S,
        coords=coords,
        labels=labels_map,
        _raw_features=raw_map,
    )


# ── 1. Distance ──────────────────────────────────────────────────────────

def kosmos_distance(ks: KosmosSpace,
                    domain_a: str, idx_a: int,
                    domain_b: str, idx_b: int) -> float:
    """L2 distance between two objects in Kosmos PCA space."""
    va = ks.coords[domain_a][idx_a]
    vb = ks.coords[domain_b][idx_b]
    return float(torch.norm(va - vb).item())


def kosmos_distance_by_label(ks: KosmosSpace,
                             domain_a: str, label_a: str,
                             domain_b: str, label_b: str) -> float:
    """Distance lookup by human-readable labels."""
    idx_a = ks.labels[domain_a].index(label_a)
    idx_b = ks.labels[domain_b].index(label_b)
    return kosmos_distance(ks, domain_a, idx_a, domain_b, idx_b)


# ── 2. Nearest neighbor ─────────────────────────────────────────────────

def nearest_neighbors(ks: KosmosSpace,
                      source_domain: str, source_idx: int,
                      target_domain: str,
                      k: int = 5) -> list[tuple[str, float]]:
    """
    Return the *k* closest objects in *target_domain* to the given source
    object.  Returns list of (label, distance).
    """
    v = ks.coords[source_domain][source_idx]          # (n_pcs,)
    targets = ks.coords[target_domain]                 # (M, n_pcs)
    dists = torch.norm(targets - v.unsqueeze(0), dim=1)
    topk = torch.topk(dists, k=min(k, len(dists)), largest=False)
    results = []
    for i, d in zip(topk.indices.tolist(), topk.values.tolist()):
        results.append((ks.labels[target_domain][i], d))
    return results


def nearest_neighbors_by_label(ks: KosmosSpace,
                               source_domain: str, source_label: str,
                               target_domain: str,
                               k: int = 5) -> list[tuple[str, float]]:
    idx = ks.labels[source_domain].index(source_label)
    return nearest_neighbors(ks, source_domain, idx, target_domain, k=k)


# ── 3. Addition ──────────────────────────────────────────────────────────

def kosmos_add(ks: KosmosSpace,
               domain_a: str, idx_a: int,
               domain_b: str, idx_b: int,
               search_domain: str,
               k: int = 5) -> tuple[torch.Tensor, list[tuple[str, float]]]:
    """
    Vector-add two objects in Kosmos space and find the nearest real objects
    in *search_domain*.

    Returns (sum_vector, nearest_neighbors_list).
    """
    va = ks.coords[domain_a][idx_a]
    vb = ks.coords[domain_b][idx_b]
    v_sum = va + vb

    targets = ks.coords[search_domain]
    dists = torch.norm(targets - v_sum.unsqueeze(0), dim=1)
    topk = torch.topk(dists, k=min(k, len(dists)), largest=False)
    results = []
    for i, d in zip(topk.indices.tolist(), topk.values.tolist()):
        results.append((ks.labels[search_domain][i], d))
    return v_sum, results


# ── 4. Projection ───────────────────────────────────────────────────────

def kosmos_project(ks: KosmosSpace,
                   domain: str, idx: int,
                   axis: int = 0) -> float:
    """
    Project an object onto a single Kosmos axis (PC).

    axis=0 → PC1 ≈ Megethos (size / complexity).
    """
    return float(ks.coords[domain][idx][axis].item())


# ── 5. Analogy ──────────────────────────────────────────────────────────

def kosmos_analogy(ks: KosmosSpace,
                   d_a: str, idx_a: int,
                   d_b: str, idx_b: int,
                   d_c: str, idx_c: int,
                   search_domain: str,
                   k: int = 5) -> tuple[torch.Tensor, list[tuple[str, float]]]:
    """
    a - b + c = ?

    "EC(conductor 11) - MF(level 11) + MF(level 37) = ?"
    Should land near EC(conductor 37) if the Kosmos preserves analogy.
    """
    va = ks.coords[d_a][idx_a]
    vb = ks.coords[d_b][idx_b]
    vc = ks.coords[d_c][idx_c]
    v_result = va - vb + vc

    targets = ks.coords[search_domain]
    dists = torch.norm(targets - v_result.unsqueeze(0), dim=1)
    topk = torch.topk(dists, k=min(k, len(dists)), largest=False)
    results = []
    for i, d in zip(topk.indices.tolist(), topk.values.tolist()):
        results.append((ks.labels[search_domain][i], d))
    return v_result, results


# ---------------------------------------------------------------------------
#  Helper: extract conductor / level from raw features
# ---------------------------------------------------------------------------

def _extract_conductor_from_label(label: str) -> Optional[int]:
    """Parse conductor from EC label like '11.a1' or MF label like '11.2.a.a'."""
    try:
        return int(label.split(".")[0])
    except (ValueError, IndexError):
        return None


# =====================================================================
#  TESTS
# =====================================================================

def run_tests():
    """Run all five operation tests and print results."""

    results_out = {}
    np.random.seed(42)
    torch.manual_seed(42)

    print("=" * 72)
    print("  KOSMOS OPERATIONS — Test Suite")
    print("=" * 72)

    t0 = time.time()
    print("\nLoading domains and computing PCA rotation ...")
    ks = build_kosmos(
        "elliptic_curves", "modular_forms",
        "knots", "number_fields", "lattices",
    )
    load_time = time.time() - t0
    print(f"  Loaded in {load_time:.1f}s")
    print(f"  PCA singular values (top 15): "
          f"{[f'{s:.2f}' for s in ks.S.tolist()]}")
    variance_explained = (ks.S ** 2).cumsum(0) / (ks.S ** 2).sum()
    print(f"  Cumulative variance: "
          f"{[f'{v:.3f}' for v in variance_explained.tolist()]}")

    # ------------------------------------------------------------------
    # TEST 1 — Distance: EC 11.a1 vs MF 11.2.a.a should be close
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 1: Distance  (are related objects close?)")
    print("-" * 72)

    try:
        d_related = kosmos_distance_by_label(
            ks, "elliptic_curves", "11.a1",
            "modular_forms", "11.2.a.a",
        )
        print(f"  d(EC 11.a1, MF 11.2.a.a) = {d_related:.4f}")

        # Compare with random pairs
        n_random = 200
        random_dists = []
        ec_n = len(ks.labels["elliptic_curves"])
        mf_n = len(ks.labels["modular_forms"])
        for _ in range(n_random):
            i = np.random.randint(ec_n)
            j = np.random.randint(mf_n)
            random_dists.append(kosmos_distance(ks, "elliptic_curves", i,
                                                "modular_forms", j))
        mean_random = np.mean(random_dists)
        std_random  = np.std(random_dists)
        z_score = (d_related - mean_random) / max(std_random, 1e-8)
        # percentile: fraction of random pairs that are CLOSER than d_related
        percentile = np.mean([d_related >= d for d in random_dists]) * 100

        print(f"  Random baseline: mean={mean_random:.4f}, std={std_random:.4f}")
        print(f"  z-score = {z_score:.2f}  (negative = closer than random)")
        print(f"  Percentile among random = {percentile:.1f}%  (lower = closer)")

        test1_pass = percentile < 25  # related pair in bottom quartile
        verdict1 = "PASS" if test1_pass else "FAIL"
        print(f"  Verdict: {verdict1}")
        results_out["distance"] = {
            "d_related": d_related, "mean_random": mean_random,
            "z_score": z_score, "percentile": percentile,
            "verdict": verdict1,
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        results_out["distance"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 2 — Nearest neighbor: does EC(N) -> nearest MF have level N?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 2: Nearest Neighbor  (cross-domain modularity)")
    print("-" * 72)

    try:
        # Pick ECs with small conductors where we expect MF matches
        test_conductors = [11, 14, 15, 17, 19, 20, 21, 24, 26, 27, 30, 32,
                           33, 34, 35, 36, 37, 38, 39, 40]
        ec_labels = ks.labels["elliptic_curves"]
        matches = 0
        total = 0

        print(f"  Testing {len(test_conductors)} conductors ...")
        for N in test_conductors:
            # Find an EC with this conductor
            target_label = None
            for lbl in ec_labels:
                if _extract_conductor_from_label(lbl) == N:
                    target_label = lbl
                    break
            if target_label is None:
                continue

            nns = nearest_neighbors_by_label(
                ks, "elliptic_curves", target_label,
                "modular_forms", k=5,
            )
            total += 1
            # Check if any of top-5 MFs have level == N
            found = False
            for mf_label, dist in nns:
                mf_level = _extract_conductor_from_label(mf_label)
                if mf_level == N:
                    found = True
                    break

            if found:
                matches += 1
            print(f"    EC {target_label:>8s} (N={N:>3d}) -> top MF: "
                  f"{nns[0][0]:>12s} (d={nns[0][1]:.3f})  "
                  f"{'MATCH' if found else 'miss'}")

        hit_rate = matches / max(total, 1)
        # Random baseline: prob of level N in top-5 among 50K MFs
        # is very low (~5/50000 * 5 = 0.05%), so even 10% hit rate is signal
        test2_pass = hit_rate > 0.10
        verdict2 = "PASS" if test2_pass else "FAIL"
        print(f"  Hit rate: {matches}/{total} = {hit_rate:.1%}")
        print(f"  Verdict: {verdict2}")
        results_out["nearest_neighbor"] = {
            "matches": matches, "total": total,
            "hit_rate": hit_rate, "verdict": verdict2,
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        results_out["nearest_neighbor"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 3 — Addition: EC_a + EC_b near EC_{a*b}?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 3: Addition  (does vector sum -> conductor product?)")
    print("-" * 72)

    try:
        # Test: EC(11) + EC(14) should land near EC(154=11*14)?
        # More generally try several pairs
        addition_tests = [
            ("11.a1", "14.a1", 154),
            ("11.a1", "17.a1", 187),
            ("14.a1", "15.a1", 210),
            ("11.a1", "37.a1", 407),
        ]

        ec_labels = ks.labels["elliptic_curves"]
        add_hits = 0
        add_total = 0

        for label_a, label_b, expected_N in addition_tests:
            if label_a not in ec_labels or label_b not in ec_labels:
                continue
            idx_a = ec_labels.index(label_a)
            idx_b = ec_labels.index(label_b)
            v_sum, nns = kosmos_add(
                ks, "elliptic_curves", idx_a,
                "elliptic_curves", idx_b,
                "elliptic_curves", k=10,
            )
            add_total += 1

            # Check if any top-10 result has conductor == expected_N
            found = False
            nearest_conductors = []
            for lbl, dist in nns:
                c = _extract_conductor_from_label(lbl)
                nearest_conductors.append(c)
                if c == expected_N:
                    found = True

            if found:
                add_hits += 1
            print(f"    {label_a} + {label_b} -> expected N={expected_N}")
            print(f"      Top conductors: {nearest_conductors[:5]}")
            print(f"      Nearest: {nns[0][0]} (d={nns[0][1]:.3f})  "
                  f"{'HIT' if found else 'miss'}")

        add_rate = add_hits / max(add_total, 1)
        verdict3 = "PASS" if add_rate > 0.25 else "FAIL"
        print(f"  Hit rate: {add_hits}/{add_total} = {add_rate:.1%}")
        print(f"  Verdict: {verdict3}")
        results_out["addition"] = {
            "hits": add_hits, "total": add_total,
            "hit_rate": add_rate, "verdict": verdict3,
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        results_out["addition"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 4 — Projection: PC1 ≈ Megethos (complexity / size)
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 4: Projection  (PC1 ~ Megethos / complexity)")
    print("-" * 72)

    try:
        # For ECs, log_conductor is feature 0 (after z-scoring).
        # PC1 projection should correlate with it.
        ec_features = ks._raw_features["elliptic_curves"]
        log_cond = ec_features[:, 0]  # already z-scored log(1+conductor)
        pc1_vals = ks.coords["elliptic_curves"][:, 0]

        corr = float(torch.corrcoef(
            torch.stack([log_cond, pc1_vals])
        )[0, 1].item())
        abs_corr = abs(corr)

        print(f"  Correlation(PC1, log_conductor) for ECs = {corr:.4f}")

        # Also check for MFs (feature 0 = log_level)
        mf_features = ks._raw_features["modular_forms"]
        mf_log_level = mf_features[:, 0]
        mf_pc1 = ks.coords["modular_forms"][:, 0]
        corr_mf = float(torch.corrcoef(
            torch.stack([mf_log_level, mf_pc1])
        )[0, 1].item())

        print(f"  Correlation(PC1, log_level) for MFs = {corr_mf:.4f}")

        # Also check knots (feature 0 = crossing_number)
        kn_features = ks._raw_features["knots"]
        kn_cross = kn_features[:, 0]
        kn_pc1 = ks.coords["knots"][:, 0]
        corr_kn = float(torch.corrcoef(
            torch.stack([kn_cross, kn_pc1])
        )[0, 1].item())
        print(f"  Correlation(PC1, crossing_number) for knots = {corr_kn:.4f}")

        mean_abs_corr = np.mean([abs(corr), abs(corr_mf), abs(corr_kn)])
        test4_pass = mean_abs_corr > 0.3
        verdict4 = "PASS" if test4_pass else "FAIL"
        print(f"  Mean |correlation| = {mean_abs_corr:.4f}")
        print(f"  Verdict: {verdict4}")
        results_out["projection"] = {
            "corr_ec": corr, "corr_mf": corr_mf, "corr_knots": corr_kn,
            "mean_abs_corr": mean_abs_corr, "verdict": verdict4,
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        results_out["projection"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 5 — Analogy: EC(11) - MF(11) + MF(37) ≈ EC(37)?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 5: Analogy  (EC(11) - MF(11) + MF(37) = EC(37)?)")
    print("-" * 72)

    try:
        analogy_tests = [
            ("11.a1", "11.2.a.a", "37.2.a.a", 37),
            ("11.a1", "11.2.a.a", "14.2.a.a", 14),
            ("37.a1", "37.2.a.a", "11.2.a.a", 11),
        ]

        ec_labels = ks.labels["elliptic_curves"]
        mf_labels = ks.labels["modular_forms"]
        analogy_hits = 0
        analogy_total = 0

        for ec_lbl, mf_from, mf_to, expected_cond in analogy_tests:
            if ec_lbl not in ec_labels:
                print(f"    SKIP: {ec_lbl} not found")
                continue
            if mf_from not in mf_labels:
                print(f"    SKIP: {mf_from} not found")
                continue
            if mf_to not in mf_labels:
                print(f"    SKIP: {mf_to} not found")
                continue

            ec_idx = ec_labels.index(ec_lbl)
            mf_from_idx = mf_labels.index(mf_from)
            mf_to_idx = mf_labels.index(mf_to)

            v_result, nns = kosmos_analogy(
                ks,
                "elliptic_curves", ec_idx,
                "modular_forms", mf_from_idx,
                "modular_forms", mf_to_idx,
                "elliptic_curves", k=10,
            )
            analogy_total += 1

            nearest_conds = []
            found = False
            for lbl, dist in nns:
                c = _extract_conductor_from_label(lbl)
                nearest_conds.append(c)
                if c == expected_cond:
                    found = True

            if found:
                analogy_hits += 1

            cond_a = _extract_conductor_from_label(ec_lbl)
            print(f"    EC({cond_a}) - MF({mf_from.split('.')[0]}) "
                  f"+ MF({mf_to.split('.')[0]}) -> expected EC(N={expected_cond})")
            print(f"      Top conductors: {nearest_conds[:5]}")
            print(f"      Nearest: {nns[0][0]} (d={nns[0][1]:.3f})  "
                  f"{'HIT' if found else 'miss'}")

        analogy_rate = analogy_hits / max(analogy_total, 1)
        verdict5 = "PASS" if analogy_rate > 0.25 else "FAIL"
        print(f"  Hit rate: {analogy_hits}/{analogy_total} = {analogy_rate:.1%}")
        print(f"  Verdict: {verdict5}")
        results_out["analogy"] = {
            "hits": analogy_hits, "total": analogy_total,
            "hit_rate": analogy_rate, "verdict": verdict5,
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        results_out["analogy"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    for op, res in results_out.items():
        v = res.get("verdict", "?")
        print(f"  {op:20s}  {v}")
    total_time = time.time() - t0
    print(f"\n  Total time: {total_time:.1f}s")

    # Save results
    out_path = Path(__file__).resolve().parent.parent / "results" / "kosmos_ops_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results_out, f, indent=2, default=str)
    print(f"  Results saved to {out_path}")

    return results_out


# =====================================================================
#  LOG-SPACE (PHONEME) OPERATIONS
#  ──────────────────────────────
#  The raw PCA addition FAILED because Megethos = log(conductor).
#  In phoneme space (5D, rotated), addition ↔ conductor multiplication,
#  subtraction ↔ conductor division, scalar multiply ↔ conductor power.
# =====================================================================

@dataclass
class LogKosmosSpace:
    """
    Container holding the 5D rotated phoneme-space coordinates, with axis 0
    calibrated to actual log(conductor).

    Unlike KosmosSpace (28D raw PCA), this operates in the 5D space
    discovered by PhonemeProjector, further rotated by kosmos_rotation.pt
    so that axis 0 = Megethos = log(conductor).

    Critical detail: PhonemeProjector z-scores its output, so the raw rotated
    coordinates are in z-score units, not log-conductor units.  We recalibrate
    axis 0 by regressing it against known log(conductor) values so that
    addition in this space genuinely equals conductor multiplication.
    """
    domains: dict                    # name -> DomainIndex
    rotation: torch.Tensor           # (5, 5) rotation matrix
    coords: dict                     # name -> (N, 5) rotated phoneme coords
    labels: dict                     # name -> list[str]
    conductors: dict                 # name -> list[Optional[int]]  (parsed from labels)
    megethos_scale: float            # scale factor applied to axis 0
    megethos_offset: float           # offset applied to axis 0


def build_log_kosmos(*domain_names: str) -> LogKosmosSpace:
    """
    Load domains, project to 5D phoneme space, rotate via kosmos_rotation.pt,
    then recalibrate axis 0 to actual log(conductor) units.

    >>> lks = build_log_kosmos("elliptic_curves", "modular_forms")
    """
    from harmonia.src.phonemes import PhonemeProjector

    domains = load_domains(*domain_names)
    dom_list = list(domains.values())

    projector = PhonemeProjector(dom_list)

    rotation_path = Path(__file__).resolve().parent.parent / "data" / "kosmos_rotation.pt"
    rotation = torch.load(rotation_path, weights_only=True)

    coords, labels_map, conductors_map = {}, {}, {}
    for d_idx, (name, dom) in enumerate(domains.items()):
        all_idx = torch.arange(dom.n_objects)
        raw_phoneme = projector.get_phonemes(d_idx, all_idx)    # (N, 5)
        rotated = raw_phoneme @ rotation.T                       # (N, 5)
        coords[name] = rotated
        labels_map[name] = dom.labels
        conductors_map[name] = [
            _extract_conductor_from_label(lbl) for lbl in dom.labels
        ]

    # ── Recalibrate axis 0 to actual log(conductor) ──────────────────
    # Use EC domain as calibration source (conductor is known and clean).
    # Fit: log(conductor) = scale * rotated_axis0 + offset
    # Then apply this transform to ALL domains so the space is consistent.
    scale, offset = 1.0, 0.0
    if "elliptic_curves" in coords:
        ec_coords_0 = coords["elliptic_curves"][:, 0]
        ec_conds = conductors_map["elliptic_curves"]
        # Build mask for valid conductors
        valid_mask = torch.tensor([c is not None and c > 0 for c in ec_conds])
        log_conds = torch.tensor([
            np.log(c) if (c is not None and c > 0) else 0.0
            for c in ec_conds
        ], dtype=torch.float32)

        if valid_mask.sum() > 10:
            x = ec_coords_0[valid_mask]
            y = log_conds[valid_mask]
            # Linear regression: y = scale * x + offset
            x_mean = x.mean()
            y_mean = y.mean()
            scale = float(((x - x_mean) * (y - y_mean)).sum() / ((x - x_mean) ** 2).sum())
            offset = float(y_mean - scale * x_mean)

    # Apply calibration to axis 0 for all domains
    for name in coords:
        c = coords[name].clone()
        c[:, 0] = c[:, 0] * scale + offset
        coords[name] = c

    return LogKosmosSpace(
        domains=domains,
        rotation=rotation,
        coords=coords,
        labels=labels_map,
        conductors=conductors_map,
        megethos_scale=scale,
        megethos_offset=offset,
    )


def _find_by_conductor(lks: LogKosmosSpace, domain: str, conductor: int) -> Optional[int]:
    """Find the first object index in *domain* whose conductor == *conductor*."""
    for i, c in enumerate(lks.conductors[domain]):
        if c == conductor:
            return i
    return None


def _nearest_in_domain(lks: LogKosmosSpace, vec: torch.Tensor,
                       domain: str, k: int = 10) -> list[tuple[str, float, Optional[int]]]:
    """Find the k nearest objects to *vec* in *domain*. Returns (label, dist, conductor)."""
    targets = lks.coords[domain]
    dists = torch.norm(targets - vec.unsqueeze(0), dim=1)
    topk = torch.topk(dists, k=min(k, len(dists)), largest=False)
    results = []
    for i, d in zip(topk.indices.tolist(), topk.values.tolist()):
        results.append((
            lks.labels[domain][i],
            d,
            lks.conductors[domain][i],
        ))
    return results


# ── 1. Log-Addition (conductor multiplication) ─────────────────────────

def log_addition(lks: LogKosmosSpace,
                 domain_a: str, idx_a: int,
                 domain_b: str, idx_b: int,
                 search_domain: str,
                 k: int = 10) -> tuple[torch.Tensor, list]:
    """
    Add two objects in rotated phoneme space.

    Because Megethos (axis 0) = log(conductor), we ADD along axis 0
    (conductor multiplication) and AVERAGE the shape axes (1-4),
    since the product object inherits a blend of both parents' structure.
    """
    va = lks.coords[domain_a][idx_a]
    vb = lks.coords[domain_b][idx_b]
    v_result = torch.zeros_like(va)
    v_result[0] = va[0] + vb[0]              # Megethos: log(N1) + log(N2)
    v_result[1:] = (va[1:] + vb[1:]) / 2.0   # Shape: average
    return v_result, _nearest_in_domain(lks, v_result, search_domain, k=k)


# ── 2. Log-Subtraction (conductor division) ────────────────────────────

def log_subtraction(lks: LogKosmosSpace,
                    domain_a: str, idx_a: int,
                    domain_b: str, idx_b: int,
                    search_domain: str,
                    k: int = 10) -> tuple[torch.Tensor, list]:
    """
    Subtract obj_b from obj_a in rotated phoneme space.

    Axis 0 (Megethos): log(N1) - log(N2) = log(N1/N2).
    Shape axes (1-4): use obj_a's shape (the 'remainder' keeps the
    dividend's structure).
    """
    va = lks.coords[domain_a][idx_a]
    vb = lks.coords[domain_b][idx_b]
    v_result = va.clone()
    v_result[0] = va[0] - vb[0]              # Megethos: log(N1) - log(N2)
    # Shape axes: keep obj_a's shape (quotient inherits dividend's structure)
    return v_result, _nearest_in_domain(lks, v_result, search_domain, k=k)


# ── 3. Scalar Multiply (conductor exponentiation) ──────────────────────

def scalar_multiply(lks: LogKosmosSpace,
                    domain: str, idx: int,
                    k_scalar: float,
                    search_domain: str,
                    k: int = 10) -> tuple[torch.Tensor, list]:
    """
    Scale Megethos by *k_scalar* (= raise conductor to k-th power).

    Axis 0: k * log(N) = log(N^k).
    Shape axes (1-4): kept unchanged (the powered object has the same
    structural character).
    """
    v = lks.coords[domain][idx]
    v_result = v.clone()
    v_result[0] = k_scalar * v[0]            # Megethos: k * log(N)
    # Shape axes: unchanged
    return v_result, _nearest_in_domain(lks, v_result, search_domain, k=k)


# ── 4. Inner Product (alignment measure) ───────────────────────────────

def inner_product(lks: LogKosmosSpace,
                  domain_a: str, idx_a: int,
                  domain_b: str, idx_b: int) -> float:
    """
    Dot product of two objects in rotated phoneme space.

    Measures 'how aligned are two objects?' — positive means they share
    structural features; large magnitude means both are 'loud' in
    phoneme space.
    """
    va = lks.coords[domain_a][idx_a]
    vb = lks.coords[domain_b][idx_b]
    return float(torch.dot(va, vb).item())


def cosine_similarity(lks: LogKosmosSpace,
                      domain_a: str, idx_a: int,
                      domain_b: str, idx_b: int) -> float:
    """Normalized inner product (cosine similarity) in phoneme space."""
    va = lks.coords[domain_a][idx_a]
    vb = lks.coords[domain_b][idx_b]
    return float(torch.nn.functional.cosine_similarity(
        va.unsqueeze(0), vb.unsqueeze(0)
    ).item())


# =====================================================================
#  LOG-SPACE TESTS
# =====================================================================

def run_log_tests():
    """Test all four log-space operations and save results."""

    results_out = {}
    np.random.seed(42)
    torch.manual_seed(42)

    print("=" * 72)
    print("  LOG-SPACE (PHONEME) OPERATIONS — Test Suite")
    print("=" * 72)

    t0 = time.time()
    print("\nLoading domains and building phoneme-space rotation ...")
    lks = build_log_kosmos("elliptic_curves", "modular_forms")
    load_time = time.time() - t0
    print(f"  Loaded in {load_time:.1f}s")
    print(f"  Rotation matrix shape: {lks.rotation.shape}")
    print(f"  EC objects: {len(lks.labels['elliptic_curves'])}")
    print(f"  MF objects: {len(lks.labels['modular_forms'])}")

    ec_dom = "elliptic_curves"
    mf_dom = "modular_forms"

    # ------------------------------------------------------------------
    # TEST 1 — Log-Addition: log_add(EC_N1, EC_N2) ~ EC(N1*N2)?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 1: Log-Addition  (add in phoneme space = multiply conductors)")
    print("-" * 72)

    try:
        addition_tests = [
            (11, 14, 154),    # 11 * 14 = 154
            (11, 17, 187),    # 11 * 17 = 187
            (14, 15, 210),    # 14 * 15 = 210
            (11, 30, 330),    # 11 * 30 = 330
        ]

        add_hits = 0
        add_total = 0
        add_details = []

        for N1, N2, expected_N in addition_tests:
            idx_a = _find_by_conductor(lks, ec_dom, N1)
            idx_b = _find_by_conductor(lks, ec_dom, N2)
            if idx_a is None or idx_b is None:
                print(f"    SKIP: conductor {N1} or {N2} not found")
                continue

            v_sum, nns = log_addition(lks, ec_dom, idx_a, ec_dom, idx_b, ec_dom, k=20)
            add_total += 1

            nearest_conds = [c for _, _, c in nns]
            # Check if expected conductor is in top 20
            found = expected_N in nearest_conds
            # Also check ratio: nearest conductor / expected conductor
            if nearest_conds[0] is not None:
                ratio = nearest_conds[0] / expected_N if expected_N > 0 else float('inf')
            else:
                ratio = float('inf')

            if found:
                add_hits += 1

            detail = {
                "N1": N1, "N2": N2, "expected": expected_N,
                "nearest_conductors": nearest_conds[:10],
                "nearest_label": nns[0][0], "nearest_dist": nns[0][1],
                "ratio_nearest_to_expected": round(ratio, 3),
                "hit": found,
            }
            add_details.append(detail)
            print(f"    EC({N1}) + EC({N2}) -> expected N={expected_N}")
            print(f"      Top conductors: {nearest_conds[:10]}")
            print(f"      Nearest: {nns[0][0]} (d={nns[0][1]:.4f}, cond={nearest_conds[0]})")
            print(f"      Ratio nearest/expected: {ratio:.3f}  {'HIT' if found else 'miss'}")

        add_rate = add_hits / max(add_total, 1)
        verdict1 = "PASS" if add_rate > 0.25 else "FAIL"
        print(f"\n  Hit rate: {add_hits}/{add_total} = {add_rate:.1%}")
        print(f"  Verdict: {verdict1}")
        results_out["log_addition"] = {
            "hits": add_hits, "total": add_total, "hit_rate": add_rate,
            "verdict": verdict1, "details": add_details,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        results_out["log_addition"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 2 — Log-Subtraction: EC(30) - EC(6) ~ EC(5)?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 2: Log-Subtraction  (subtract in phoneme space = divide conductors)")
    print("-" * 72)

    try:
        subtraction_tests = [
            (330, 11, 30),    # 330 / 11 = 30
            (330, 30, 11),    # 330 / 30 = 11
            (154, 11, 14),    # 154 / 11 = 14
            (154, 14, 11),    # 154 / 14 = 11
            (210, 14, 15),    # 210 / 14 = 15
            (210, 15, 14),    # 210 / 15 = 14
        ]

        sub_hits = 0
        sub_total = 0
        sub_details = []

        for N1, N2, expected_N in subtraction_tests:
            idx_a = _find_by_conductor(lks, ec_dom, N1)
            idx_b = _find_by_conductor(lks, ec_dom, N2)
            if idx_a is None or idx_b is None:
                print(f"    SKIP: conductor {N1} or {N2} not found")
                continue

            v_diff, nns = log_subtraction(lks, ec_dom, idx_a, ec_dom, idx_b, ec_dom, k=20)
            sub_total += 1

            nearest_conds = [c for _, _, c in nns]
            found = expected_N in nearest_conds

            if nearest_conds[0] is not None:
                ratio = nearest_conds[0] / expected_N if expected_N > 0 else float('inf')
            else:
                ratio = float('inf')

            if found:
                sub_hits += 1

            detail = {
                "N1": N1, "N2": N2, "expected": expected_N,
                "nearest_conductors": nearest_conds[:10],
                "nearest_label": nns[0][0], "nearest_dist": nns[0][1],
                "ratio_nearest_to_expected": round(ratio, 3),
                "hit": found,
            }
            sub_details.append(detail)
            print(f"    EC({N1}) - EC({N2}) -> expected N={expected_N}")
            print(f"      Top conductors: {nearest_conds[:10]}")
            print(f"      Nearest: {nns[0][0]} (d={nns[0][1]:.4f}, cond={nearest_conds[0]})")
            print(f"      Ratio nearest/expected: {ratio:.3f}  {'HIT' if found else 'miss'}")

        sub_rate = sub_hits / max(sub_total, 1)
        verdict2 = "PASS" if sub_rate > 0.25 else "FAIL"
        print(f"\n  Hit rate: {sub_hits}/{sub_total} = {sub_rate:.1%}")
        print(f"  Verdict: {verdict2}")
        results_out["log_subtraction"] = {
            "hits": sub_hits, "total": sub_total, "hit_rate": sub_rate,
            "verdict": verdict2, "details": sub_details,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        results_out["log_subtraction"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 3 — Scalar Multiply: 2 * EC(11) ~ EC(121)?
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 3: Scalar Multiply  (scale phoneme vec = conductor power)")
    print("-" * 72)

    try:
        scalar_tests = [
            (11, 2, 121),     # 11^2 = 121
            (14, 2, 196),     # 14^2 = 196
            (5, 3, 125),      # 5^3  = 125
            (6, 2, 36),       # 6^2  = 36
        ]

        sc_hits = 0
        sc_total = 0
        sc_details = []

        for N, k_val, expected_N in scalar_tests:
            idx = _find_by_conductor(lks, ec_dom, N)
            if idx is None:
                print(f"    SKIP: conductor {N} not found")
                continue

            v_scaled, nns = scalar_multiply(lks, ec_dom, idx, k_val, ec_dom, k=20)
            sc_total += 1

            nearest_conds = [c for _, _, c in nns]
            found = expected_N in nearest_conds

            if nearest_conds[0] is not None:
                ratio = nearest_conds[0] / expected_N if expected_N > 0 else float('inf')
            else:
                ratio = float('inf')

            if found:
                sc_hits += 1

            detail = {
                "N": N, "k": k_val, "expected": expected_N,
                "nearest_conductors": nearest_conds[:10],
                "nearest_label": nns[0][0], "nearest_dist": nns[0][1],
                "ratio_nearest_to_expected": round(ratio, 3),
                "hit": found,
            }
            sc_details.append(detail)
            print(f"    {k_val} * EC({N}) -> expected N={expected_N}")
            print(f"      Top conductors: {nearest_conds[:10]}")
            print(f"      Nearest: {nns[0][0]} (d={nns[0][1]:.4f}, cond={nearest_conds[0]})")
            print(f"      Ratio nearest/expected: {ratio:.3f}  {'HIT' if found else 'miss'}")

        sc_rate = sc_hits / max(sc_total, 1)
        verdict3 = "PASS" if sc_rate > 0.25 else "FAIL"
        print(f"\n  Hit rate: {sc_hits}/{sc_total} = {sc_rate:.1%}")
        print(f"  Verdict: {verdict3}")
        results_out["scalar_multiply"] = {
            "hits": sc_hits, "total": sc_total, "hit_rate": sc_rate,
            "verdict": verdict3, "details": sc_details,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        results_out["scalar_multiply"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # TEST 4 — Inner Product: EC(N) . MF(N) should be high (aligned)
    # ------------------------------------------------------------------
    print("\n" + "-" * 72)
    print("TEST 4: Inner Product  (EC and corresponding MF should be aligned)")
    print("-" * 72)

    try:
        test_levels = [11, 14, 15, 17, 19, 20, 21, 24, 26, 27, 30, 32,
                       33, 34, 35, 36, 37, 38, 39, 40]

        matched_ips = []
        random_ips = []

        ec_labels = lks.labels[ec_dom]
        mf_labels = lks.labels[mf_dom]

        for N in test_levels:
            ec_idx = _find_by_conductor(lks, ec_dom, N)
            mf_idx = _find_by_conductor(lks, mf_dom, N)
            if ec_idx is None or mf_idx is None:
                continue

            ip = inner_product(lks, ec_dom, ec_idx, mf_dom, mf_idx)
            cs = cosine_similarity(lks, ec_dom, ec_idx, mf_dom, mf_idx)
            matched_ips.append({"N": N, "inner_product": ip, "cosine_sim": cs})

        # Random baseline
        n_ec = len(ec_labels)
        n_mf = len(mf_labels)
        for _ in range(200):
            i = np.random.randint(n_ec)
            j = np.random.randint(n_mf)
            ip = inner_product(lks, ec_dom, i, mf_dom, j)
            random_ips.append(ip)

        matched_mean = np.mean([m["inner_product"] for m in matched_ips])
        matched_cos_mean = np.mean([m["cosine_sim"] for m in matched_ips])
        random_mean = np.mean(random_ips)
        random_std = np.std(random_ips)

        # z-score: how many SDs above random is the matched mean?
        z_score = (matched_mean - random_mean) / max(random_std, 1e-8)

        print(f"  Matched pairs (EC(N) . MF(N)):")
        for m in matched_ips[:8]:
            print(f"    N={m['N']:>3d}: inner_product={m['inner_product']:.4f}, "
                  f"cosine_sim={m['cosine_sim']:.4f}")
        if len(matched_ips) > 8:
            print(f"    ... ({len(matched_ips)} total)")

        print(f"\n  Matched mean inner product:  {matched_mean:.4f}")
        print(f"  Matched mean cosine sim:     {matched_cos_mean:.4f}")
        print(f"  Random mean inner product:   {random_mean:.4f} +/- {random_std:.4f}")
        print(f"  z-score (matched vs random): {z_score:.2f}")

        # Pass if matched cosine similarity is notably higher than random,
        # or z-score > 1.5
        verdict4 = "PASS" if (z_score > 1.5 or matched_cos_mean > 0.5) else "FAIL"
        print(f"  Verdict: {verdict4}")

        results_out["inner_product"] = {
            "n_matched_pairs": len(matched_ips),
            "matched_mean_ip": matched_mean,
            "matched_mean_cosine": matched_cos_mean,
            "random_mean_ip": random_mean,
            "random_std_ip": random_std,
            "z_score": z_score,
            "verdict": verdict4,
            "matched_details": matched_ips[:10],
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        results_out["inner_product"] = {"verdict": "ERROR", "error": str(e)}

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("  LOG-SPACE SUMMARY")
    print("=" * 72)
    for op, res in results_out.items():
        v = res.get("verdict", "?")
        print(f"  {op:20s}  {v}")
    total_time = time.time() - t0
    print(f"\n  Total time: {total_time:.1f}s")

    # Save results
    out_path = Path(__file__).resolve().parent.parent / "results" / "log_ops_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results_out, f, indent=2, default=str)
    print(f"  Results saved to {out_path}")

    return results_out


if __name__ == "__main__":
    import sys
    if "--log" in sys.argv:
        run_log_tests()
    else:
        run_tests()
