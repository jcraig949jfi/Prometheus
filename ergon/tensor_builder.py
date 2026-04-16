#!/usr/bin/env python3
"""
Tensor Builder: Precompute all domain×feature data into a single numpy tensor.

Loads all active domains, extracts all active features, stacks into one matrix.
The tensor executor then maps hypothesis (domain_a, feature_a, domain_b, feature_b)
to tensor slice indices — microseconds instead of disk I/O per hypothesis.

Output: .npz file with:
  - data: (n_objects_total, n_features_total) float32 matrix
  - domain_boundaries: dict of {domain: (start_row, end_row)}
  - feature_indices: dict of {(domain, feature_name): column_index}
  - metadata: domain sizes, feature counts, build timestamp
"""
import sys
import json
import math
import time
import numpy as np
from pathlib import Path
from collections import OrderedDict

_root = Path(__file__).resolve().parent.parent  # Prometheus/
_forge_v3 = str(_root / "forge/v3")
if _forge_v3 not in sys.path:
    sys.path.insert(0, _forge_v3)

from gene_schema import ACTIVE_DOMAINS, ACTIVE_FEATURES

_scripts = str(_root / "cartography/shared/scripts")
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

# ============================================================
# Data Loading (identical to executor.py — single source of truth)
# ============================================================

def _load_domain(domain):
    """Load domain data. Returns list of dicts with raw fields."""
    data_root = _root / "cartography"

    objects = []

    if domain == "elliptic_curves":
        import psycopg2
        try:
            from prometheus_data.config import get_pg_dsn
            con = psycopg2.connect(**get_pg_dsn("lmfdb"))
        except Exception:
            con = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
        cur = con.cursor()
        cur.execute("""
            SELECT conductor::bigint, rank::int, torsion::int, cm::int
            FROM ec_curvedata WHERE conductor::bigint > 0 LIMIT 10000
        """)
        rows = cur.fetchall()
        con.close()
        for cond, rank, tors, cm in rows:
            objects.append({"conductor": cond, "rank": rank or 0, "torsion": tors or 1,
                           "cm": cm or 0, "ap": []})

    elif domain == "modular_forms":
        import psycopg2
        try:
            from prometheus_data.config import get_pg_dsn
            con = psycopg2.connect(**get_pg_dsn("lmfdb"))
        except Exception:
            con = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
        cur = con.cursor()
        cur.execute("""
            SELECT level::int, weight::int, dim::int FROM mf_newforms WHERE level::int > 0 LIMIT 10000
        """)
        rows = cur.fetchall()
        con.close()
        for level, weight, dim in rows:
            objects.append({"level": level, "weight": weight, "dim": dim or 1})

    elif domain == "number_fields":
        nf_path = data_root / "number_fields/data/number_fields.json"
        if nf_path.exists():
            raw = json.load(open(nf_path, encoding="utf-8"))
            for f in raw[:10000]:
                try:
                    objects.append({
                        "discriminant": float(f.get("disc_abs", 0)),
                        "class_number": float(f.get("class_number", 0)),
                        "regulator": float(f.get("regulator", 0)),
                        "degree": int(float(f.get("degree", 0))),
                    })
                except:
                    pass

    elif domain == "genus2_curves":
        import ast
        g2_path = data_root / "genus2/data/genus2_curves_full.json"
        if g2_path.exists():
            raw = json.load(open(g2_path, encoding="utf-8"))
            for c in raw[:10000]:
                if c.get("conductor", 0) > 0:
                    t = c.get("torsion", [])
                    if isinstance(t, str):
                        try:
                            t = ast.literal_eval(t)
                        except:
                            t = []
                    order = 1
                    if isinstance(t, list):
                        for x in t:
                            order *= x
                    objects.append({
                        "conductor": c["conductor"],
                        "discriminant": abs(c.get("discriminant", 0)),
                        "torsion": order,
                        "st_group": c.get("st_group", ""),
                        "root_number": c.get("root_number", 0),
                    })

    elif domain == "maass_forms":
        maass_path = data_root / "maass/data/maass_with_coefficients.json"
        if maass_path.exists():
            raw = json.load(open(maass_path, encoding="utf-8"))
            for m in raw[:5000]:
                coeffs = m.get("coefficients", [])
                objects.append({
                    "level": m.get("level", 0),
                    "spectral_parameter": m.get("spectral_parameter", 0),
                    "coefficients": coeffs[:25] if isinstance(coeffs, list) else [],
                })

    elif domain == "knots":
        knot_path = data_root / "knots/data/knots.json"
        if knot_path.exists():
            raw = json.load(open(knot_path, encoding="utf-8"))
            for k in raw.get("knots", raw if isinstance(raw, list) else [])[:10000]:
                objects.append({
                    "crossing_number": k.get("crossing_number", 0),
                    "determinant": k.get("determinant", 0),
                    "alex_coeffs": k.get("alex_coeffs", []),
                    "jones_coeffs": k.get("jones_coeffs", []),
                })

    elif domain == "superconductors":
        import csv
        import io
        csv_path = data_root / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
        if csv_path.exists():
            with open(csv_path) as f:
                lines = [l for l in f if not l.startswith("#")]
            for row in csv.DictReader(io.StringIO("".join(lines))):
                try:
                    tc = float(row.get("tc", ""))
                    sg = row.get("spacegroup_2", "").strip()
                    sc_class = row.get("sc_class", "").strip()
                    if tc > 0 and sg:
                        objects.append({"tc": tc, "sg": sg, "sc_class": sc_class})
                except:
                    pass

    return objects


def _extract_feature_value(obj, feature_name):
    """Extract a single numeric value from one object for one feature."""
    val = None

    # Direct field match
    if feature_name in obj:
        try:
            val = float(obj[feature_name])
        except (TypeError, ValueError):
            pass

    # Computed features
    if val is None:
        if feature_name == "log_conductor" and "conductor" in obj:
            val = math.log(max(obj["conductor"], 1))
        elif feature_name == "log_discriminant" and "discriminant" in obj:
            val = math.log(max(obj["discriminant"], 1))
        elif feature_name == "n_bad_primes" and "conductor" in obj:
            c = int(obj["conductor"])
            count = 0
            for p in [2, 3, 5, 7, 11, 13]:
                if c % p == 0:
                    count += 1
            val = float(count)
        elif feature_name == "ap_kurtosis" and "ap" in obj and len(obj.get("ap", [])) >= 5:
            arr = np.array(obj["ap"], dtype=float)
            if np.std(arr) > 0:
                val = float(np.mean(((arr - np.mean(arr)) / np.std(arr)) ** 4))
        elif feature_name == "coefficient_entropy" and "coefficients" in obj and len(obj.get("coefficients", [])) >= 5:
            arr = np.abs(np.array(obj["coefficients"][:20], dtype=float))
            total = np.sum(arr)
            if total > 0:
                p = arr / total
                p = p[p > 0]
                val = float(-np.sum(p * np.log2(p)))
        elif feature_name == "alexander_degree" and "alex_coeffs" in obj:
            val = float(len(obj.get("alex_coeffs", [])))
        elif feature_name == "jones_degree" and "jones_coeffs" in obj:
            val = float(len(obj.get("jones_coeffs", [])))
        elif feature_name == "ap_compression_lz" and "ap" in obj and len(obj.get("ap", [])) >= 5:
            import zlib
            s = ",".join(str(x) for x in obj["ap"])
            val = float(len(zlib.compress(s.encode())) / len(s.encode()))

    if val is not None and np.isfinite(val):
        return val
    return float("nan")


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
        """Get the 1D array for a (domain, feature) pair. Returns NaN array if unavailable."""
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


def build_tensor(domains=None, features_map=None, verbose=True):
    """Build the precomputed tensor from all active domains and features.

    Args:
        domains: list of domain names (default: ACTIVE_DOMAINS)
        features_map: dict of {domain: [feature_names]} (default: ACTIVE_FEATURES)
        verbose: print progress

    Returns:
        TensorData object with everything in RAM
    """
    if domains is None:
        domains = ACTIVE_DOMAINS
    if features_map is None:
        features_map = ACTIVE_FEATURES

    t0 = time.time()
    td = TensorData()

    # Phase 1: Load all domain data
    domain_objects = OrderedDict()
    for domain in domains:
        if verbose:
            print(f"  Loading {domain}...", end="", flush=True)
        objects = _load_domain(domain)
        if not objects or objects[0].get("_empty"):
            if verbose:
                print(" EMPTY (skipped)")
            continue
        domain_objects[domain] = objects
        td.domain_sizes[domain] = len(objects)
        if verbose:
            print(f" {len(objects)} objects")

    # Phase 2: Build column index — one column per (domain, feature) pair
    col_idx = 0
    for domain in domain_objects:
        for feature in features_map.get(domain, []):
            td.feature_col[(domain, feature)] = col_idx
            td.feature_names.append((domain, feature))
            col_idx += 1

    td.n_features = col_idx

    # Phase 3: Compute row boundaries
    row_offset = 0
    for domain, objects in domain_objects.items():
        n = len(objects)
        td.domain_boundaries[domain] = (row_offset, row_offset + n)
        row_offset += n

    td.n_objects = row_offset

    if verbose:
        print(f"\n  Tensor shape: ({td.n_objects}, {td.n_features})")
        mem_mb = td.n_objects * td.n_features * 4 / (1024 * 1024)
        print(f"  Memory: {mem_mb:.2f} MB")

    # Phase 4: Allocate and fill the tensor
    td.data = np.full((td.n_objects, td.n_features), np.nan, dtype=np.float32)

    for domain, objects in domain_objects.items():
        start, end = td.domain_boundaries[domain]
        features = features_map.get(domain, [])
        if verbose:
            print(f"  Extracting {domain}: {len(features)} features × {len(objects)} objects...", end="", flush=True)

        for feature in features:
            col = td.feature_col[(domain, feature)]
            for i, obj in enumerate(objects):
                td.data[start + i, col] = _extract_feature_value(obj, feature)

        # Report valid counts
        if verbose:
            valid_counts = []
            for feature in features:
                col = td.feature_col[(domain, feature)]
                n_valid = int(np.sum(np.isfinite(td.data[start:end, col])))
                valid_counts.append(f"{feature}={n_valid}")
            print(f" [{', '.join(valid_counts)}]")

    td.build_time = time.time() - t0
    if verbose:
        print(f"\n  Build time: {td.build_time:.2f}s")
        print(f"  Total valid cells: {int(np.sum(np.isfinite(td.data)))}/{td.n_objects * td.n_features}")

    return td


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TENSOR BUILDER — Precomputing feature tensor for forge v3")
    print("=" * 70)

    td = build_tensor()

    out_path = Path(__file__).parent / "tensor.npz"
    td.save(out_path)
    print(f"\n  Saved: {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")

    # Verification: reload and spot-check
    td2 = TensorData.load(out_path)
    print(f"  Reload check: shape=({td2.n_objects}, {td2.n_features}), domains={list(td2.domain_boundaries.keys())}")

    # Spot check: EC conductors should be positive
    ec_cond = td2.get_slice("elliptic_curves", "conductor")
    if ec_cond is not None:
        valid = ec_cond[np.isfinite(ec_cond)]
        print(f"  EC conductors: n={len(valid)}, min={valid.min():.0f}, max={valid.max():.0f}, median={np.median(valid):.0f}")
