#!/usr/bin/env python3
"""
Tensor Builder v2: Precompute all domain×feature data into a single numpy tensor.

Uses Harmonia's DomainIndex loaders instead of hand-rolled loading.
Each loader returns z-scored (N, D) feature matrices — we stack them into
one big tensor with domain boundaries and feature column indices.

v2 changes (2026-04-16):
  - Switched from 7 hand-rolled domains to 31 Harmonia loaders
  - From 58K objects to 5M+ objects
  - Features are z-scored by Harmonia (consistent with coupling scorers)
  - Backward compatible: TensorData.save/load format unchanged
  - Old gene_schema ACTIVE_DOMAINS/ACTIVE_FEATURES still work as subset

Output: .npz file with:
  - data: (n_objects_total, n_features_total) float32 matrix
  - domain_boundaries: dict of {domain: (start_row, end_row)}
  - feature_indices: dict of {(domain, feature_name): column_index}
  - metadata: domain sizes, feature counts, build timestamp
"""
import sys
import json
import time
import numpy as np
from pathlib import Path
from collections import OrderedDict

_root = Path(__file__).resolve().parent.parent  # Prometheus/
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from harmonia.src.domain_index import DOMAIN_LOADERS


# ============================================================
# Domain configuration
# ============================================================

# Domains to include in the tensor, ordered by priority.
# "core" = mathematical objects with known cross-domain structure
# "extended" = additional mathematical/physical domains
# "derived" = computed features from other analyses
#
# Excluded: battery, dissection, disagreement, knowledge_graph, bridges,
#           charon_landscape, lmfdb_objects (meta-domains, not raw objects)

CORE_DOMAINS = [
    "elliptic_curves",   # 3.8M objects, 4 features (from local Postgres)
    "modular_forms",     # 100K, 5 features
    "number_fields",     # 9K, 6 features
    "genus2",            # 66K, 7 features
    "artin",             # 100K, 5 features (NEW)
    "ec_rich",           # 100K, 16 features (NEW — rich EC from Postgres)
    "knots",             # 13K, 28 features
    "maass",             # 15K, 25 features
]

EXTENDED_DOMAINS = [
    "lattices",          # 39K, 6 features
    "polytopes",         # 1K, 6 features
    "materials",         # 10K, 6 features
    "space_groups",      # 230, 5 features
    "belyi",             # 1K, 3 features (NEW)
    "bianchi",           # 100K, 5 features (NEW)
    "groups",            # 100K, 3 features (NEW)
    "oeis",              # 100K, 7 features (NEW)
    "codata",            # 286, 10 features (NEW — physical constants)
    "pdg_particles",     # 226, 11 features (NEW — particle physics)
    "chemistry",         # 50K, 12 features (NEW — QM9 molecules)
    "metabolism",        # 108, 11 features (NEW)
    # Fingerprint domains (Aporia E-FP tests)
    "nf_cf",             # ~2K, 10 features (NF + continued fraction features)
    "artin_ade",         # 100K, 11 features (Artin + ADE/Dynkin classification)
]

DERIVED_DOMAINS = [
    "dynamics",          # 50K, 10 features
    "phase_space",       # 50K, 10 features
    "spectral_sigs",     # 50K, 14 features
    "operadic_sigs",     # 50K, 7 features
    "padic_sigs",        # 50K, 10 features
    "info_theoretic",    # 50K, 5 features
    "fractional_deriv",  # 50K, 9 features
    "functional_eq",     # 50K, 8 features
    "resurgence",        # 50K, 9 features
]

ALL_DOMAINS = CORE_DOMAINS + EXTENDED_DOMAINS + DERIVED_DOMAINS

# For backward compatibility with forge/v3 gene_schema
try:
    _forge_v3 = str(_root / "forge/v3")
    if _forge_v3 not in sys.path:
        sys.path.insert(0, _forge_v3)
    from gene_schema import ACTIVE_DOMAINS as LEGACY_DOMAINS, ACTIVE_FEATURES as LEGACY_FEATURES
except ImportError:
    LEGACY_DOMAINS = None
    LEGACY_FEATURES = None


# ============================================================
# Tensor Builder
# ============================================================

class TensorData:
    """Precomputed tensor with index metadata for fast hypothesis execution."""

    def __init__(self):
        self.data = None                    # (n_total_objects, n_total_features) float32
        self.domain_boundaries = {}         # domain -> (start_row, end_row)
        self.feature_col = {}               # (domain, feature_name) -> col_index
        self.domain_sizes = {}              # domain -> n_objects
        self.feature_names = []             # ordered list of (domain, feature) tuples
        self.n_objects = 0
        self.n_features = 0
        self.build_time = 0.0

    def get_slice(self, domain, feature):
        """Get the 1D array for a (domain, feature) pair. Returns None if unavailable."""
        col = self.feature_col.get((domain, feature))
        if col is None:
            return None
        start, end = self.domain_boundaries[domain]
        return self.data[start:end, col]

    def save(self, path):
        """Save tensor and metadata to .npz."""
        np.savez_compressed(
            path,
            data=self.data,
            domain_boundaries=json.dumps(self.domain_boundaries),
            feature_col=json.dumps({f"{d}|{f}": int(c) for (d, f), c in self.feature_col.items()}),
            domain_sizes=json.dumps(self.domain_sizes),
            feature_names=json.dumps(self.feature_names),
            n_objects=self.n_objects,
            n_features=self.n_features,
            build_time=self.build_time,
        )

    @classmethod
    def load(cls, path):
        """Load tensor from .npz."""
        npz = np.load(path, allow_pickle=False)
        td = cls()
        td.data = npz["data"]
        td.domain_boundaries = {k: tuple(v) for k, v in json.loads(str(npz["domain_boundaries"])).items()}
        raw_fc = json.loads(str(npz["feature_col"]))
        td.feature_col = {tuple(k.split("|", 1)): v for k, v in raw_fc.items()}
        td.domain_sizes = json.loads(str(npz["domain_sizes"]))
        td.feature_names = [tuple(x) for x in json.loads(str(npz["feature_names"]))]
        td.n_objects = int(npz["n_objects"])
        td.n_features = int(npz["n_features"])
        td.build_time = float(npz["build_time"])
        return td


def build_tensor(domains=None, max_per_domain=None, verbose=True):
    """Build the precomputed tensor from Harmonia domain loaders.

    Args:
        domains: list of domain names (default: ALL_DOMAINS)
        max_per_domain: cap objects per domain (None = no cap, use for testing)
        verbose: print progress

    Returns:
        TensorData object with everything in RAM
    """
    if domains is None:
        domains = ALL_DOMAINS

    t0 = time.time()
    td = TensorData()

    # Phase 1: Load all domains via Harmonia loaders
    domain_data = OrderedDict()  # name -> DomainIndex
    for name in domains:
        loader = DOMAIN_LOADERS.get(name)
        if loader is None:
            if verbose:
                print(f"  {name}: no loader (skipped)")
            continue

        if verbose:
            print(f"  Loading {name}...", end="", flush=True)

        try:
            dom = loader()
            if dom.n_objects == 0:
                if verbose:
                    print(" EMPTY (skipped)")
                continue

            # Optional cap
            if max_per_domain and dom.n_objects > max_per_domain:
                # Subsample deterministically
                np.random.seed(hash(name) % 2**31)
                idx = np.random.choice(dom.n_objects, max_per_domain, replace=False)
                idx.sort()
                import torch
                dom.features = dom.features[idx]
                dom.labels = [dom.labels[i] for i in idx]
                dom.n_objects = max_per_domain

            domain_data[name] = dom
            td.domain_sizes[name] = dom.n_objects
            if verbose:
                print(f" {dom.n_objects:,} objects x {dom.n_features} features")

        except Exception as e:
            if verbose:
                print(f" FAILED: {str(e)[:60]}")
            continue

    if not domain_data:
        raise RuntimeError("No domains loaded successfully")

    # Phase 2: Build column index
    # Each domain gets its own feature columns (features are domain-specific)
    col_idx = 0
    feature_name_map = {}  # domain -> list of feature names
    for name, dom in domain_data.items():
        feat_names = [f"f{i}" for i in range(dom.n_features)]
        feature_name_map[name] = feat_names
        for fname in feat_names:
            td.feature_col[(name, fname)] = col_idx
            td.feature_names.append((name, fname))
            col_idx += 1

    td.n_features = col_idx

    # Phase 3: Compute row boundaries
    row_offset = 0
    for name, dom in domain_data.items():
        td.domain_boundaries[name] = (row_offset, row_offset + dom.n_objects)
        row_offset += dom.n_objects

    td.n_objects = row_offset

    if verbose:
        print(f"\n  Tensor shape: ({td.n_objects:,}, {td.n_features})")
        mem_mb = td.n_objects * td.n_features * 4 / (1024 * 1024)
        print(f"  Memory: {mem_mb:.1f} MB")

    # Phase 4: Allocate and fill
    td.data = np.full((td.n_objects, td.n_features), np.nan, dtype=np.float32)

    for name, dom in domain_data.items():
        start, end = td.domain_boundaries[name]
        features_np = dom.features.numpy() if hasattr(dom.features, 'numpy') else np.array(dom.features)

        for fi in range(dom.n_features):
            col = td.feature_col[(name, f"f{fi}")]
            td.data[start:end, col] = features_np[:, fi]

    td.build_time = time.time() - t0
    if verbose:
        n_valid = int(np.sum(np.isfinite(td.data)))
        n_total = td.n_objects * td.n_features
        print(f"\n  Build time: {td.build_time:.1f}s")
        print(f"  Valid cells: {n_valid:,}/{n_total:,} ({n_valid/max(n_total,1):.1%})")
        print(f"  Domains: {len(domain_data)}")

    return td


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build Ergon tensor from Harmonia domain loaders")
    parser.add_argument("--domains", choices=["core", "extended", "all", "legacy"], default="core",
                        help="Which domain set to build (default: core)")
    parser.add_argument("--max-per-domain", type=int, default=None,
                        help="Cap objects per domain (for testing)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path (default: ergon/tensor.npz)")
    args = parser.parse_args()

    domain_map = {
        "core": CORE_DOMAINS,
        "extended": CORE_DOMAINS + EXTENDED_DOMAINS,
        "all": ALL_DOMAINS,
        "legacy": LEGACY_DOMAINS if LEGACY_DOMAINS else CORE_DOMAINS,
    }
    domains = domain_map[args.domains]

    print("=" * 70)
    print(f"TENSOR BUILDER v2 — {args.domains} domains ({len(domains)} requested)")
    print("=" * 70)

    td = build_tensor(domains=domains, max_per_domain=args.max_per_domain)

    out_path = Path(args.output) if args.output else Path(__file__).parent / "tensor.npz"
    td.save(out_path)
    print(f"\n  Saved: {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")

    # Verification
    td2 = TensorData.load(out_path)
    print(f"  Reload check: ({td2.n_objects:,}, {td2.n_features}), {len(td2.domain_boundaries)} domains")
    for name, (start, end) in sorted(td2.domain_boundaries.items()):
        print(f"    {name}: {end - start:,} objects")
