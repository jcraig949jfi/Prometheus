"""
Within-domain structure test using TT-Cross.

Splits a single domain into two subgroups and tests whether TT-Cross finds
structure between the subgroups that ISN'T explained by the split variable
or Megethos (feature 0).

If split-based bond > random-split bond by > 2 sigma, there's internal
structure in the domain visible through the split variable.

Tests:
  1. EC split by rank (0 vs 1)
  2. EC split by torsion (1 vs 2)
  3. NF split by degree (2 vs 3)
  4. Genus2 split by root_number (+1 vs -1)
"""
import sys
import json
import time
import numpy as np
import torch
import tntorch as tn
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from harmonia.src.domain_index import DomainIndex, _normalize
from harmonia.src.coupling import DistributionalCoupling


# ---------------------------------------------------------------------------
# Data loading with raw split variables preserved
# ---------------------------------------------------------------------------

def load_ec_with_raw():
    """Load elliptic curves returning (DomainIndex, raw_features_dict)."""
    import duckdb
    db_path = Path(__file__).resolve().parents[2] / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql("""
        SELECT lmfdb_label, conductor, rank, analytic_rank, torsion
        FROM elliptic_curves
        WHERE conductor IS NOT NULL
    """).fetchall()
    db.close()

    labels, feats, raw = [], [], []
    for row in rows:
        labels.append(row[0] or str(len(labels)))
        feats.append([
            np.log1p(float(row[1] or 0)),
            float(row[2] or 0),
            float(row[3] or 0),
            float(row[4] or 0),
        ])
        raw.append({
            "conductor": float(row[1] or 0),
            "rank": int(row[2] or 0),
            "torsion": int(row[4] or 0),
        })

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("elliptic_curves", labels, features), raw


def load_nf_with_raw():
    """Load number fields returning (DomainIndex, raw_features_dict)."""
    path = Path(__file__).resolve().parents[2] / "cartography" / "number_fields" / "data" / "number_fields.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats, raw = [], [], []
    for nf in data:
        labels.append(nf["label"])
        feats.append([
            float(nf.get("degree", 0)),
            float(nf.get("disc_sign", 0)),
            np.log1p(abs(float(nf.get("disc_abs", 0)))),
            float(nf.get("class_number", 0)),
            float(nf.get("regulator", 0)),
            float(len(nf.get("class_group", []))),
        ])
        raw.append({
            "degree": int(nf.get("degree", 0)),
        })

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("number_fields", labels, features), raw


def load_genus2_with_raw():
    """Load genus-2 curves returning (DomainIndex, raw_features_dict)."""
    path = Path(__file__).resolve().parents[2] / "cartography" / "genus2" / "data" / "genus2_curves_full.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats, raw = [], [], []
    for curve in data:
        labels.append(curve.get("label", str(len(labels))))
        conductor = curve.get("conductor", 0)
        feats.append([
            np.log1p(abs(float(conductor))),
            float(curve.get("disc_sign", 0)),
            float(curve.get("two_selmer_rank", 0)),
            float(curve.get("has_square_sha", 0)),
            float(curve.get("locally_solvable", 0)),
            float(curve.get("globally_solvable", 0)),
            float(curve.get("root_number", 0)),
        ])
        raw.append({
            "root_number": int(curve.get("root_number", 0)),
        })

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("genus2", labels, features), raw


# ---------------------------------------------------------------------------
# Core: split domain and run TT-Cross
# ---------------------------------------------------------------------------

def split_domain(domain: DomainIndex, raw: list[dict], split_key: str,
                 val_a, val_b, feature_0_idx: int, split_feature_idx: int,
                 subsample: int = 2000):
    """
    Split a domain into two groups by raw[split_key] == val_a / val_b.
    Zero out feature_0_idx (Megethos) and split_feature_idx (the split variable).
    Subsample each group to at most `subsample` objects.

    Returns two DomainIndex objects.
    """
    idx_a = [i for i, r in enumerate(raw) if r[split_key] == val_a]
    idx_b = [i for i, r in enumerate(raw) if r[split_key] == val_b]

    print(f"  Split {split_key}: val={val_a} -> {len(idx_a)}, val={val_b} -> {len(idx_b)}")

    # Subsample
    if len(idx_a) > subsample:
        idx_a = np.random.choice(idx_a, subsample, replace=False).tolist()
    if len(idx_b) > subsample:
        idx_b = np.random.choice(idx_b, subsample, replace=False).tolist()

    # Build subdomains
    def make_sub(indices, name_suffix):
        labs = [domain.labels[i] for i in indices]
        feats = domain.features[indices].clone()
        # Zero out feature 0 (Megethos) and the split variable
        feats[:, feature_0_idx] = 0.0
        if split_feature_idx != feature_0_idx:
            feats[:, split_feature_idx] = 0.0
        return DomainIndex(f"{domain.name}_{name_suffix}", labs, feats)

    dom_a = make_sub(idx_a, f"{split_key}_{val_a}")
    dom_b = make_sub(idx_b, f"{split_key}_{val_b}")
    return dom_a, dom_b


def random_split(domain: DomainIndex, feature_0_idx: int, subsample: int = 2000):
    """
    Random split of a domain into two groups (null model).
    Zero out feature 0 (Megethos) only.

    Returns two DomainIndex objects.
    """
    n = domain.n_objects
    perm = torch.randperm(n)
    half = min(subsample, n // 2)
    idx_a = perm[:half].tolist()
    idx_b = perm[half:half * 2].tolist()

    def make_sub(indices, name_suffix):
        labs = [domain.labels[i] for i in indices]
        feats = domain.features[indices].clone()
        feats[:, feature_0_idx] = 0.0
        return DomainIndex(f"{domain.name}_{name_suffix}", labs, feats)

    return make_sub(idx_a, "random_A"), make_sub(idx_b, "random_B")


def run_tt_bond(dom_a: DomainIndex, dom_b: DomainIndex, max_rank: int = 15,
                eps: float = 1e-3):
    """
    Run TT-Cross between two subdomains and return bond dimension + SVs.
    """
    domains = [dom_a, dom_b]
    scorer = DistributionalCoupling(domains, device="cpu")
    grids = [torch.arange(d.n_objects, dtype=torch.float32) for d in domains]

    def value_fn(*indices):
        return scorer(*[idx.long() for idx in indices])

    tt = tn.cross(function=value_fn, domain=grids, eps=eps, rmax=max_rank, max_iter=50)
    ranks = tt.ranks_tt.tolist()
    bond_dim = ranks[1]  # bond between the two domains

    # Extract SVs from the bond
    core = tt.cores[0]
    unfolded = core.reshape(-1, core.shape[-1])
    try:
        svs = torch.linalg.svdvals(unfolded)
        top_svs = svs[:min(10, len(svs))].tolist()
    except Exception:
        top_svs = []

    return bond_dim, top_svs


# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

TESTS = [
    {
        "name": "EC_rank_0_vs_1",
        "domain": "elliptic_curves",
        "loader": "ec",
        "split_key": "rank",
        "val_a": 0,
        "val_b": 1,
        "feature_0_idx": 0,       # log(conductor) = Megethos
        "split_feature_idx": 1,   # rank
        "description": "EC split by rank: does TT find structure between rank-0 and rank-1 beyond conductor distribution?",
    },
    {
        "name": "EC_torsion_1_vs_2",
        "domain": "elliptic_curves",
        "loader": "ec",
        "split_key": "torsion",
        "val_a": 1,
        "val_b": 2,
        "feature_0_idx": 0,       # log(conductor) = Megethos
        "split_feature_idx": 3,   # torsion
        "description": "EC split by torsion: structure between trivial and Z/2 torsion?",
    },
    {
        "name": "NF_degree_2_vs_3",
        "domain": "number_fields",
        "loader": "nf",
        "split_key": "degree",
        "val_a": 2,
        "val_b": 3,
        "feature_0_idx": 0,       # degree (Note: for NF, feature 0 IS degree)
        "split_feature_idx": 0,   # degree (same as feature 0 here)
        "description": "NF split by degree: structure between quadratic and cubic fields?",
    },
    {
        "name": "Genus2_rootnum_plus1_vs_minus1",
        "domain": "genus2",
        "loader": "genus2",
        "split_key": "root_number",
        "val_a": 1,
        "val_b": -1,
        "feature_0_idx": 0,       # log(conductor) = Megethos
        "split_feature_idx": 6,   # root_number
        "description": "Genus2 split by root_number: structure between even and odd functional equations?",
    },
]


def main():
    np.random.seed(42)
    torch.manual_seed(42)

    # Pre-load all domains
    print("Loading domains...")
    t0 = time.time()
    ec_dom, ec_raw = load_ec_with_raw()
    nf_dom, nf_raw = load_nf_with_raw()
    g2_dom, g2_raw = load_genus2_with_raw()
    print(f"  Loaded in {time.time() - t0:.1f}s")

    domain_map = {
        "ec": (ec_dom, ec_raw),
        "nf": (nf_dom, nf_raw),
        "genus2": (g2_dom, g2_raw),
    }

    N_NULL = 10  # number of random-split null trials per test
    results = []

    print("=" * 80)
    print("WITHIN-DOMAIN STRUCTURE TEST via TT-Cross")
    print("Split a domain in half, test if TT-Cross finds internal structure")
    print("=" * 80)

    for test in TESTS:
        print(f"\n{'-' * 70}")
        print(f"TEST: {test['name']}")
        print(f"  {test['description']}")
        print(f"{'-' * 70}")

        domain, raw = domain_map[test["loader"]]
        t_start = time.time()

        # 1. Run split-based TT-Cross
        print("\n  [1] Split-based TT-Cross:")
        dom_a, dom_b = split_domain(
            domain, raw,
            split_key=test["split_key"],
            val_a=test["val_a"],
            val_b=test["val_b"],
            feature_0_idx=test["feature_0_idx"],
            split_feature_idx=test["split_feature_idx"],
            subsample=2000,
        )
        split_bond, split_svs = run_tt_bond(dom_a, dom_b)
        print(f"  Split bond dimension: {split_bond}")
        print(f"  Top SVs: {[f'{s:.4f}' for s in split_svs[:5]]}")

        # 2. Run null model: random splits (N_NULL trials)
        print(f"\n  [2] Null model ({N_NULL} random splits):")
        null_bonds = []
        null_sv_lists = []
        for trial in range(N_NULL):
            null_a, null_b = random_split(
                domain,
                feature_0_idx=test["feature_0_idx"],
                subsample=2000,
            )
            nb, nsvs = run_tt_bond(null_a, null_b)
            null_bonds.append(nb)
            null_sv_lists.append(nsvs)
            print(f"    Trial {trial+1}: bond={nb}")

        null_mean = np.mean(null_bonds)
        null_std = np.std(null_bonds) if len(null_bonds) > 1 else 1.0
        null_std = max(null_std, 0.5)  # floor to avoid division by near-zero

        # 3. Compute sigma separation
        sigma_sep = (split_bond - null_mean) / null_std

        # 4. Verdict
        if sigma_sep > 2.0:
            verdict = "STRUCTURE_FOUND"
        elif sigma_sep > 1.0:
            verdict = "MARGINAL"
        else:
            verdict = "NO_STRUCTURE"

        wall_time = time.time() - t_start

        print(f"\n  RESULTS:")
        print(f"    Split bond:    {split_bond}")
        print(f"    Null mean:     {null_mean:.2f} +/- {null_std:.2f}")
        print(f"    Sigma sep:     {sigma_sep:.2f}")
        print(f"    Verdict:       {verdict}")
        print(f"    Wall time:     {wall_time:.1f}s")

        result = {
            "test_name": test["name"],
            "domain": test["domain"],
            "split_key": test["split_key"],
            "split_values": [test["val_a"], test["val_b"]],
            "description": test["description"],
            "features_zeroed": {
                "feature_0": test["feature_0_idx"],
                "split_feature": test["split_feature_idx"],
            },
            "group_a_size": dom_a.n_objects,
            "group_b_size": dom_b.n_objects,
            "split_bond_dim": split_bond,
            "split_top_svs": split_svs[:5],
            "null_bonds": null_bonds,
            "null_mean": round(null_mean, 4),
            "null_std": round(null_std, 4),
            "sigma_separation": round(sigma_sep, 4),
            "verdict": verdict,
            "wall_time_seconds": round(wall_time, 2),
        }
        results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for r in results:
        status = ">>>" if r["verdict"] == "STRUCTURE_FOUND" else "   "
        print(f"  {status} {r['test_name']:40s} bond={r['split_bond_dim']:2d}  "
              f"null={r['null_mean']:.1f}+/-{r['null_std']:.1f}  "
              f"sigma={r['sigma_separation']:+.2f}  {r['verdict']}")

    # Save
    output = {
        "experiment": "within_domain_structure",
        "description": (
            "Tests whether TT-Cross finds internal structure within a single domain "
            "when split by a known variable. Feature 0 (Megethos) and the split "
            "variable are zeroed out so we're testing for residual structure. "
            "Compared against random splits of the same domain."
        ),
        "methodology": {
            "scorer": "DistributionalCoupling",
            "max_rank": 15,
            "eps": 1e-3,
            "subsample": 2000,
            "null_trials": N_NULL,
            "significance_threshold": "2 sigma above null mean",
        },
        "tests": results,
    }

    out_path = Path(__file__).resolve().parent.parent / "results" / "within_domain_structure.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
