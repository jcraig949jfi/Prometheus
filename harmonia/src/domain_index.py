"""
Domain Index — Maps mathematical objects to integer indices with feature vectors.

Each domain (knots, number fields, space groups, etc.) becomes one axis
of the tensor. Objects within a domain get integer indices 0..N-1 and
precomputed float feature vectors for fast coupling computation.
"""
import json
import os
import torch
import numpy as np
from pathlib import Path
from typing import Optional

CARTOGRAPHY = Path(os.environ.get(
    "PROMETHEUS_CARTOGRAPHY",
    Path(__file__).resolve().parent.parent.parent / "cartography",
))


def _pg_fire():
    """Get a psycopg2 connection to prometheus_fire (zeros, atlas, objects, bridges)."""
    import psycopg2
    try:
        from prometheus_data.config import get_pg_dsn
        dsn = get_pg_dsn("fire")
    except Exception:
        dsn = dict(host='localhost', port=5432, dbname='prometheus_fire',
                   user='postgres', password='prometheus', connect_timeout=15)
    return psycopg2.connect(**dsn)


def _pg_lmfdb():
    """Get a psycopg2 connection to lmfdb (EC, MF, lfunc — the big tables)."""
    import psycopg2
    try:
        from prometheus_data.config import get_pg_dsn
        dsn = get_pg_dsn("lmfdb")
    except Exception:
        dsn = dict(host='localhost', port=5432, dbname='lmfdb',
                   user='lmfdb', password='lmfdb', connect_timeout=15)
    return psycopg2.connect(**dsn)


class DomainIndex:
    """Index for a single mathematical domain."""

    def __init__(self, name: str, labels: list[str], features: torch.Tensor):
        """
        Args:
            name: Domain name (e.g. 'knots')
            labels: Human-readable label per object
            features: (N, D) float tensor of feature vectors
        """
        self.name = name
        self.labels = labels
        self.features = features  # (N, D) float32
        self.n_objects = len(labels)
        self.n_features = features.shape[1]

    def to(self, device):
        self.features = self.features.to(device)
        return self

    def __len__(self):
        return self.n_objects

    def __repr__(self):
        return f"DomainIndex({self.name!r}, n={self.n_objects}, d={self.n_features})"


def _normalize(t: torch.Tensor) -> torch.Tensor:
    """Z-score normalize each column. Replace NaN with 0."""
    mu = t.mean(dim=0)
    sigma = t.std(dim=0).clamp(min=1e-8)
    out = (t - mu) / sigma
    out[torch.isnan(out)] = 0.0
    return out


def load_knots(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "knots" / "data" / "knots.json"
    with open(path) as f:
        data = json.load(f)
    knots = data["knots"]

    labels, feats = [], []
    for k in knots:
        labels.append(k["name"])
        alex_coeffs = (k.get("alexander") or {}).get("coefficients", [])
        jones_coeffs = (k.get("jones") or {}).get("coefficients", [])
        conway_coeffs = (k.get("conway") or {}).get("coefficients", [])

        # Pad/truncate coefficient lists to fixed lengths
        def pad(seq, n):
            seq = list(seq)[:n]
            return seq + [0.0] * (n - len(seq))

        feat = [
            float(k.get("crossing_number") or 0),
            float(k.get("determinant") or 0),
            float(len(alex_coeffs)),
            float(len(jones_coeffs)),
            float(len(conway_coeffs)),
        ] + pad(alex_coeffs, 7) + pad(jones_coeffs, 12) + pad(conway_coeffs, 4)
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("knots", labels, features)


def load_number_fields(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "number_fields" / "data" / "number_fields.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for nf in data:
        labels.append(nf["label"])
        feat = [
            float(nf.get("degree", 0)),
            float(nf.get("disc_sign", 0)),
            np.log1p(abs(float(nf.get("disc_abs", 0)))),
            float(nf.get("class_number", 0)),
            float(nf.get("regulator", 0)),
            float(len(nf.get("class_group", []))),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("number_fields", labels, features)


def load_space_groups(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "spacegroups" / "data" / "space_groups.json"
    with open(path) as f:
        data = json.load(f)

    # Encode crystal system and lattice type as integers
    crystal_systems = sorted(set(sg["crystal_system"] for sg in data))
    lattice_types = sorted(set(sg["lattice_type"] for sg in data))
    cs_map = {s: i for i, s in enumerate(crystal_systems)}
    lt_map = {s: i for i, s in enumerate(lattice_types)}

    labels, feats = [], []
    for sg in data:
        labels.append(f"SG{sg['number']}_{sg['symbol']}")
        feat = [
            float(sg["number"]),
            float(sg["point_group_order"]),
            float(sg["is_symmorphic"]),
            float(cs_map[sg["crystal_system"]]),
            float(lt_map[sg["lattice_type"]]),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("space_groups", labels, features)


def load_genus2(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "genus2" / "data" / "genus2_curves_full.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for curve in data:
        labels.append(curve.get("label", str(len(labels))))
        conductor = curve.get("conductor", 0)
        feat = [
            np.log1p(abs(float(conductor))),
            float(curve.get("disc_sign", 0)),
            float(curve.get("two_selmer_rank", 0)),
            float(curve.get("has_square_sha", 0)),
            float(curve.get("locally_solvable", 0)),
            float(curve.get("globally_solvable", 0)),
            float(curve.get("root_number", 0)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("genus2", labels, features)


def load_maass(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "maass" / "data" / "maass_with_coefficients.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for form in data:
        labels.append(form.get("maass_id", str(len(labels))))
        coeffs = form.get("coefficients", [])[:20]  # First 20 coefficients
        coeffs_padded = (list(coeffs) + [0.0] * 20)[:20]
        feat = [
            float(form.get("level", 0)),
            float(form.get("weight", 0)),
            float(form.get("spectral_parameter", 0)),
            float(form.get("symmetry", 0)),
            float(form.get("fricke_eigenvalue", 0)),
        ] + [float(c) for c in coeffs_padded]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("maass", labels, features)


def load_lattices(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "lattices" / "data" / "lattices_full.json"
    with open(path) as f:
        raw = json.load(f)
    data = raw["records"] if isinstance(raw, dict) and "records" in raw else raw

    labels, feats = [], []
    for lat in data:
        labels.append(lat.get("label", str(len(labels))))
        feat = [
            float(lat.get("dimension", 0)),
            np.log1p(abs(float(lat.get("determinant", 0)))),
            np.log1p(float(lat.get("level", 0))),
            float(lat.get("class_number", 0)),
            float(lat.get("minimal_vector") or 0),
            np.log1p(float(lat.get("aut_group_order") or 0)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("lattices", labels, features)


def load_polytopes(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "polytopes" / "data" / "polytopes.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for i, p in enumerate(data):
        labels.append(f"poly_{i}")
        f_vec = p.get("f_vector", [])
        feat = [
            float(p.get("dimension") or 0),
            float(p.get("n_vertices") or 0),
            float(p.get("n_edges") or 0),
            float(p.get("n_facets") or 0),
            float(len(f_vec)),
            float(sum(f_vec)) if f_vec else 0.0,
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("polytopes", labels, features)


def load_materials(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "physics" / "data" / "materials_project_10k.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for mat in data:
        labels.append(mat.get("material_id", str(len(labels))))
        feat = [
            float(mat.get("band_gap", 0)),
            float(mat.get("formation_energy_per_atom", 0)),
            float(mat.get("spacegroup_number", 0)),
            float(mat.get("density", 0)),
            np.log1p(float(mat.get("volume", 0))),
            float(mat.get("nsites", 0)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("materials", labels, features)


def load_fungrim(path: Optional[Path] = None) -> DomainIndex:
    path = path or CARTOGRAPHY / "fungrim" / "data" / "fungrim_formulas.json"
    with open(path) as f:
        data = json.load(f)

    # Encode type and module as integers
    types = sorted(set(f.get("type", "") for f in data))
    modules = sorted(set(f.get("module", "") for f in data))
    type_map = {t: i for i, t in enumerate(types)}
    mod_map = {m: i for i, m in enumerate(modules)}

    labels, feats = [], []
    for formula in data:
        labels.append(formula.get("id", str(len(labels))))
        feat = [
            float(type_map.get(formula.get("type", ""), 0)),
            float(len(formula.get("symbols", []))),
            float(mod_map.get(formula.get("module", ""), 0)),
            float(len(formula.get("formula_text", ""))),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("fungrim", labels, features)


def load_elliptic_curves(db_path: Optional[Path] = None) -> DomainIndex:
    """Load elliptic curves from Postgres (lmfdb.ec_curvedata, 3.8M rows)."""
    conn = _pg_lmfdb()
    cur = conn.cursor()
    cur.execute("""
        SELECT lmfdb_label, conductor::bigint, rank::int, analytic_rank::int, torsion::int
        FROM ec_curvedata
        WHERE conductor IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        labels.append(row[0] or str(len(labels)))
        feat = [
            np.log1p(float(row[1] or 0)),  # conductor
            float(row[2] or 0),              # rank
            float(row[3] or 0),              # analytic_rank
            float(row[4] or 0),              # torsion
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("elliptic_curves", labels, features)


def load_modular_forms(db_path: Optional[Path] = None) -> DomainIndex:
    """Load modular forms from Postgres (lmfdb.mf_newforms, 1.1M rows)."""
    conn = _pg_lmfdb()
    cur = conn.cursor()
    cur.execute("""
        SELECT label, level::int, weight::int, dim::int, char_order::int, char_parity::int
        FROM mf_newforms
        WHERE level IS NOT NULL
        LIMIT 100000
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        labels.append(row[0] or str(len(labels)))
        feat = [
            np.log1p(float(row[1] or 0)),  # level
            float(row[2] or 0),              # weight
            float(row[3] or 0),              # dim
            float(row[4] or 0),              # char_order
            float(row[5] or 0),              # char_parity
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("modular_forms", labels, features)


def load_dirichlet_zeros(db_path: Optional[Path] = None) -> DomainIndex:
    """Load Dirichlet zeros from Postgres (prometheus_fire.zeros.dirichlet_zeros, 185K rows)."""
    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute("""
        SELECT lmfdb_url, conductor, degree, 0 AS rank, n_zeros_stored, motivic_weight
        FROM zeros.dirichlet_zeros
        WHERE conductor IS NOT NULL
        LIMIT 100000
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        labels.append(row[0] or str(len(labels)))
        feat = [
            np.log1p(float(row[1] or 0)),  # conductor
            float(row[2] or 0),              # degree
            float(row[3] or 0),              # rank
            float(row[4] or 0),              # n_zeros_stored
            float(row[5] or 0),              # motivic_weight
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("dirichlet_zeros", labels, features)


def load_ec_zeros(db_path: Optional[Path] = None, limit: int = 20000) -> DomainIndex:
    """
    Load elliptic curves with high-precision L-function zero statistics.

    12 features per object: standard EC invariants + zero locations,
    spacings, spacing ratios, and GUE statistics. The spectral features
    (first zero, mean spacing, spacing variance) have 6-digit precision
    from LMFDB data.

    Data sources: prometheus_fire.zeros.object_zeros + lmfdb.ec_curvedata
    (joined via xref.object_registry.source_key = ec_curvedata.lmfdb_label)
    """
    # Get zeros + EC label from prometheus_fire
    fire = _pg_fire()
    fire_cur = fire.cursor()
    fire_cur.execute(f"""
        SELECT r.source_key, oz.zeros_vector, oz.root_number, oz.analytic_rank
        FROM zeros.object_zeros oz
        JOIN xref.object_registry r ON r.object_id = oz.object_id
        WHERE r.object_type = 'elliptic_curve'
              AND oz.zeros_vector IS NOT NULL
              AND array_length(oz.zeros_vector, 1) >= 5
        LIMIT {limit}
    """)
    zero_rows = {row[0]: row[1:] for row in fire_cur.fetchall()}
    fire.close()

    # Get EC invariants from lmfdb
    lmfdb = _pg_lmfdb()
    lmfdb_cur = lmfdb.cursor()
    labels_list = list(zero_rows.keys())
    # Batch query in chunks to avoid oversized IN clause
    rows = []
    chunk_size = 5000
    for i in range(0, len(labels_list), chunk_size):
        chunk = labels_list[i:i+chunk_size]
        lmfdb_cur.execute("""
            SELECT lmfdb_label, conductor::bigint, rank::int, torsion::int
            FROM ec_curvedata
            WHERE lmfdb_label = ANY(%s) AND conductor IS NOT NULL
        """, (chunk,))
        for ec_row in lmfdb_cur.fetchall():
            label, conductor, rank, torsion = ec_row
            zvec, root_num, ana_rank = zero_rows[label]
            rows.append((label, conductor, rank, torsion, zvec, len(zvec) if zvec else 0, root_num, ana_rank))
    lmfdb.close()

    labels, feats = [], []
    for row in rows:
        label, conductor, rank, torsion, zeros_vec, n_zeros, root_num, ana_rank = row
        zeros = sorted([z for z in (zeros_vec or []) if z is not None and z > 0])
        if len(zeros) < 3:
            continue
        spacings = [zeros[i + 1] - zeros[i] for i in range(len(zeros) - 1)]

        labels.append(label or str(len(labels)))
        feats.append([
            np.log1p(float(conductor or 0)),
            float(rank or 0),
            float(ana_rank or 0),
            float(torsion or 0),
            float(root_num or 0),
            zeros[0],                                  # first zero
            np.mean(spacings),                         # mean zero spacing
            np.std(spacings) if len(spacings) > 1 else 0,
            spacings[0] / spacings[1] if len(spacings) > 1 else 1,
            float(len(zeros)),
            np.mean(zeros[:3]),                        # low zero average
            np.mean(zeros[-3:]),                       # high zero average
        ])

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("ec_zeros", labels, features)


def load_raw_zeros(db_path: Optional[Path] = None, n_zeros: int = 10) -> DomainIndex:
    """
    Load raw L-function zero positions as features.

    No summary statistics. No engineering. Just the actual locations where
    L-functions vanish on the critical line, at 8-10 digit precision computed
    by professional number theorists. These are theorems, not features.

    Each object gets n_zeros features: the first n_zeros positive zeros
    of its L-function, in ascending order.

    Data source: prometheus_fire.zeros.object_zeros + xref.object_registry
    """
    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT r.source_key, oz.zeros_vector
        FROM zeros.object_zeros oz
        JOIN xref.object_registry r ON r.object_id = oz.object_id
        WHERE r.object_type = 'elliptic_curve'
              AND oz.zeros_vector IS NOT NULL
              AND array_length(oz.zeros_vector, 1) >= {n_zeros}
        ORDER BY array_length(oz.zeros_vector, 1) DESC
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        zeros = sorted([z for z in (row[1] or []) if z is not None and z > 0])
        if len(zeros) < n_zeros:
            continue
        labels.append(row[0] or str(len(labels)))
        feats.append(zeros[:n_zeros])

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("raw_zeros", labels, features)


def load_zeros_anchored(db_path: Optional[Path] = None, n_zeros: int = 10) -> DomainIndex:
    """
    Raw zero positions + log(conductor) for Megethos anchoring.

    Feature 0: log(conductor) — the Megethos coordinate.
    Features 1-N: raw zero positions — the Phasma coordinates at maximum precision.
    This domain bridges the two axes through ground-truth data.

    Data sources: prometheus_fire.zeros.object_zeros + lmfdb.ec_curvedata
    """
    # Get zeros + labels from prometheus_fire
    fire = _pg_fire()
    fire_cur = fire.cursor()
    fire_cur.execute(f"""
        SELECT r.source_key, oz.zeros_vector
        FROM zeros.object_zeros oz
        JOIN xref.object_registry r ON r.object_id = oz.object_id
        WHERE r.object_type = 'elliptic_curve'
              AND oz.zeros_vector IS NOT NULL
              AND array_length(oz.zeros_vector, 1) >= {n_zeros}
        ORDER BY array_length(oz.zeros_vector, 1) DESC
    """)
    zero_map = {row[0]: row[1] for row in fire_cur.fetchall()}
    fire.close()

    # Get conductors from lmfdb
    lmfdb = _pg_lmfdb()
    lmfdb_cur = lmfdb.cursor()
    labels_list = list(zero_map.keys())
    rows = []
    chunk_size = 5000
    for i in range(0, len(labels_list), chunk_size):
        chunk = labels_list[i:i+chunk_size]
        lmfdb_cur.execute("""
            SELECT lmfdb_label, conductor::bigint
            FROM ec_curvedata
            WHERE lmfdb_label = ANY(%s) AND conductor IS NOT NULL
        """, (chunk,))
        for label, conductor in lmfdb_cur.fetchall():
            rows.append((label, conductor, zero_map[label]))
    lmfdb.close()

    labels, feats = [], []
    for row in rows:
        zeros = sorted([z for z in (row[2] or []) if z is not None and z > 0])
        if len(zeros) < n_zeros:
            continue
        labels.append(row[0] or str(len(labels)))
        feats.append([np.log1p(float(row[1] or 0))] + zeros[:n_zeros])

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("zeros_anchored", labels, features)


def load_rmt_ensemble(db_path: Optional[Path] = None, limit: int = 30000) -> DomainIndex:
    """
    Load GUE/random-matrix-theory spectral statistics from L-function zeros.

    PURE spectral features only -- no conductor, rank, or arithmetic invariants.
    These capture the quantum-chaos / RMT connection: the statistical fingerprint
    of how zero spacings conform to (or deviate from) GUE universality.

    14 features per object:
      Normalized spacing moments (4): mean, var, skew, kurtosis of s_i / mean(s)
      Nearest-neighbor spacing ratio stats (3): mean(r), var(r), min(r)
      Number variance Sigma^2(L) for L = 1, 2, 4 (3)
      Spectral rigidity Delta_3(L) approx for L = 1, 2 (2)
      Unfolded level statistics (2): mean unfolded spacing, unfolded spacing var
    """
    from scipy import stats as sp_stats

    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT r.source_key, oz.zeros_vector, array_length(oz.zeros_vector, 1)
        FROM zeros.object_zeros oz
        JOIN xref.object_registry r ON r.object_id = oz.object_id
        WHERE r.object_type = 'elliptic_curve'
              AND oz.zeros_vector IS NOT NULL
              AND array_length(oz.zeros_vector, 1) >= 8
        ORDER BY array_length(oz.zeros_vector, 1) DESC
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        label, zeros_vec, n_zeros = row
        zeros = sorted([z for z in (zeros_vec or [])[:n_zeros] if z is not None and z > 0])
        if len(zeros) < 8:
            continue

        spacings = np.array([zeros[i + 1] - zeros[i] for i in range(len(zeros) - 1)])
        mean_sp = spacings.mean()
        if mean_sp < 1e-12:
            continue
        s_norm = spacings / mean_sp

        # Feature 0-3: Normalized spacing distribution moments
        sp_mean = float(s_norm.mean())
        sp_var = float(s_norm.var())
        sp_skew = float(sp_stats.skew(s_norm))
        sp_kurt = float(sp_stats.kurtosis(s_norm))

        # Feature 4-6: Nearest-neighbor spacing ratios
        ratios = []
        for i in range(len(spacings) - 1):
            lo = min(spacings[i], spacings[i + 1])
            hi = max(spacings[i], spacings[i + 1])
            ratios.append(lo / hi if hi > 1e-15 else 0.0)
        ratios = np.array(ratios) if ratios else np.array([0.0])
        r_mean = float(ratios.mean())
        r_var = float(ratios.var())
        r_min = float(ratios.min())

        # Feature 7-9: Number variance Sigma^2(L)
        def number_variance(zeros_arr, L_val):
            n = len(zeros_arr)
            counts = []
            for start_idx in range(n):
                start = zeros_arr[start_idx]
                end = start + L_val
                cnt = np.searchsorted(zeros_arr, end) - start_idx
                counts.append(cnt)
                if start + L_val > zeros_arr[-1]:
                    break
            if len(counts) < 2:
                return 0.0
            return float(np.var(counts))

        zeros_arr = np.array(zeros)
        sigma2_1 = number_variance(zeros_arr, 1.0 * mean_sp)
        sigma2_2 = number_variance(zeros_arr, 2.0 * mean_sp)
        sigma2_4 = number_variance(zeros_arr, 4.0 * mean_sp)

        # Feature 10-11: Spectral rigidity Delta_3(L) approximation
        def delta3_approx(zeros_arr, L_val):
            n = len(zeros_arr)
            residuals = []
            L_actual = L_val * mean_sp
            for start_idx in range(0, max(1, n - 3)):
                start = zeros_arr[start_idx]
                end = start + L_actual
                mask = (zeros_arr >= start) & (zeros_arr <= end)
                local_z = zeros_arr[mask]
                if len(local_z) < 3:
                    continue
                x = local_z - start
                y = np.arange(1, len(local_z) + 1, dtype=float)
                A_mat = np.vstack([x, np.ones(len(x))]).T
                try:
                    result = np.linalg.lstsq(A_mat, y, rcond=None)
                    resid = result[1]
                    if len(resid) > 0:
                        residuals.append(resid[0] / L_actual)
                    else:
                        fitted = A_mat @ result[0]
                        residuals.append(float(np.mean((y - fitted) ** 2)) / L_actual)
                except np.linalg.LinAlgError:
                    continue
                if len(residuals) >= 20:
                    break
            return float(np.mean(residuals)) if residuals else 0.0

        d3_1 = delta3_approx(zeros_arr, 1.0)
        d3_2 = delta3_approx(zeros_arr, 2.0)

        # Feature 12-13: Unfolded level statistics
        def unfold(z):
            z = np.array(z)
            z_safe = np.maximum(z, 0.1)
            n_smooth = (z_safe / (2 * np.pi)) * np.log(z_safe / (2 * np.pi * np.e) + 1)
            return n_smooth

        unfolded = unfold(zeros)
        unf_spacings = np.diff(unfolded)
        unf_spacings = unf_spacings[unf_spacings > 1e-15]
        if len(unf_spacings) > 0:
            unf_mean_sp = float(unf_spacings.mean())
            unf_var_sp = float(unf_spacings.var())
        else:
            unf_mean_sp = 0.0
            unf_var_sp = 0.0

        labels.append(label or str(len(labels)))
        feats.append([
            sp_mean, sp_var, sp_skew, sp_kurt,
            r_mean, r_var, r_min,
            sigma2_1, sigma2_2, sigma2_4,
            d3_1, d3_2,
            unf_mean_sp, unf_var_sp,
        ])

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("rmt", labels, features)


def load_battery() -> DomainIndex:
    """
    Load battery test results as a dimension.

    Each object = one hypothesis that was tested. Features encode
    the test outcome (z-score, p-value, verdict) and which domains
    were involved. This lets the tensor discover which domain combinations
    produce surviving vs killed hypotheses.
    """
    data_dir = CARTOGRAPHY / "convergence" / "data"

    # Collect all genocide round results + battery logs
    all_tests = []

    # Genocide rounds
    for r in range(1, 8):
        fname = "genocide_results.json" if r == 1 else f"genocide_r{r}_results.json"
        path = data_dir / fname
        if path.exists():
            try:
                with open(path) as f:
                    raw = json.load(f)
                for t in raw.get("tests", []):
                    t["source_round"] = r
                    all_tests.append(t)
            except (json.JSONDecodeError, KeyError):
                pass

    # Battery log entries (full F15-F24b results)
    blog = data_dir / "battery_logs" / "battery_runs.jsonl"
    if blog.exists():
        with open(blog) as f:
            for line in f:
                entry = json.loads(line)
                tests_run = entry.get("tests_run", {})
                # Each test within is a sub-observation
                for test_name, result in tests_run.items():
                    all_tests.append({
                        "name": f"{entry.get('finding_id', '')}_{test_name}",
                        "tag": result.get("verdict", "UNKNOWN"),
                        "p": 0.0,  # Not always present
                        "z": result.get("observed", 0),
                        "source_round": 0,  # battery log
                    })

    # Encode domain mentions in test names as features
    domain_keywords = {
        "knot": 0, "jones": 0, "alexander": 0, "crossing": 0, "conway": 0,
        "field": 1, "degree": 1, "discriminant": 1, "class": 1, "galois": 1,
        "space": 2, "crystal": 2, "symmetr": 2, "sg": 2,
        "genus": 3, "curve": 3, "conductor": 3, "sato": 3, "selmer": 3,
        "maass": 4, "spectral": 4, "fricke": 4, "level": 4,
        "lattice": 5, "det": 5,
        "polytope": 6, "vertex": 6, "facet": 6,
        "material": 7, "band": 7, "density": 7,
        "fungrim": 8, "formula": 8, "symbol": 8,
        "elliptic": 9, "rank": 9, "torsion": 9,
        "modular": 10, "hecke": 10, "weight": 10,
        "isogen": 11, "prime": 11,
    }

    labels, feats = [], []
    for t in all_tests:
        name = t.get("name", "")
        labels.append(name[:60])

        # Domain involvement vector (12 dims)
        domain_vec = [0.0] * 12
        name_lower = name.lower()
        for kw, idx in domain_keywords.items():
            if kw in name_lower:
                domain_vec[idx] = 1.0

        verdict_score = 1.0 if t.get("tag") == "SURVIVES" else -1.0 if t.get("tag") == "KILLED" else 0.0
        p_val = float(t.get("p") or 0.5)
        z_score = float(t.get("z") or 0)
        real_val = float(t.get("real", 0) or 0)
        null_mean = float(t.get("null_mean", 0) or 0)
        source_round = float(t.get("source_round", 0))

        feat = [
            verdict_score,
            -np.log10(max(p_val, 1e-20)),  # log p-value (higher = more significant)
            z_score,
            real_val,
            null_mean,
            source_round,
        ] + domain_vec

        feats.append(feat)

    if not feats:
        # Return minimal if no data
        return DomainIndex("battery", ["empty"], torch.zeros(1, 18))

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("battery", labels, features)


def load_bianchi_forms(path: Optional[Path] = None, limit: int = 100000) -> DomainIndex:
    """Load Bianchi modular forms — automorphic forms over imaginary quadratic fields."""
    path = path or CARTOGRAPHY / "convergence" / "data" / "bianchi_forms.json"
    with open(path) as f:
        raw = json.load(f)
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    labels, feats = [], []
    for form in data[:limit]:
        labels.append(form.get("label", str(len(labels))))
        # Parse level "N.M" into two numbers
        level_parts = str(form.get("level", "0.0")).split(".")
        level_norm = float(level_parts[0]) if level_parts[0].isdigit() else 0
        level_idx = float(level_parts[1]) if len(level_parts) > 1 and level_parts[1].isdigit() else 0
        feat = [
            np.log1p(level_norm),
            level_idx,
            float(form.get("sign", 0)),
            float(form.get("cm", 0)),
            float(form.get("base_change") not in (None, "-1", "0")),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("bianchi", labels, features)


def load_groups(path: Optional[Path] = None, limit: int = 100000) -> DomainIndex:
    """Load abstract groups from GAP SmallGrp library."""
    path = path or CARTOGRAPHY / "groups" / "data" / "abstract_groups.json"
    with open(path) as f:
        raw = json.load(f)
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    labels, feats = [], []
    for g in data[:limit]:
        labels.append(g.get("label", str(len(labels))))
        feat = [
            np.log1p(float(g.get("order", 0))),
            np.log1p(float(g.get("exponent", 0))),
            float(g.get("num_conjugacy_classes", 0)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("groups", labels, features)


def load_belyi(path: Optional[Path] = None) -> DomainIndex:
    """Load Belyi maps — dessins d'enfants connecting algebra, geometry, topology."""
    path = path or CARTOGRAPHY / "convergence" / "data" / "belyi_maps.json"
    with open(path) as f:
        raw = json.load(f)
    data = raw.get("records", raw) if isinstance(raw, dict) else raw

    labels, feats = [], []
    for b in data:
        labels.append(b.get("label", str(len(labels))))
        feat = [
            float(b.get("degree", 0)),
            float(b.get("genus", 0)),
            float(b.get("orbit_size", 0)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("belyi", labels, features)


def load_oeis(path: Optional[Path] = None, limit: int = 100000) -> DomainIndex:
    """
    Load OEIS sequences with statistical features computed from terms.
    Each sequence becomes an object with features: growth rate, entropy,
    periodicity, term statistics.
    """
    import gzip
    path = path or CARTOGRAPHY / "oeis" / "data" / "stripped_full.gz"

    labels, feats = [], []
    with gzip.open(path, "rt") as f:
        for line in f:
            if not line.startswith("A") or "," not in line:
                continue
            parts = line.strip().split(",")
            seq_id = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t and t.lstrip("-").isdigit():
                    terms.append(int(t))
            if len(terms) < 5:
                continue

            labels.append(seq_id)
            abs_terms = [abs(t) for t in terms if t != 0]

            # Statistical features of the sequence
            mean_val = float(np.mean(abs_terms)) if abs_terms else 0.0
            max_val = float(max(abs_terms)) if abs_terms else 0.0
            n_zeros = sum(1 for t in terms if t == 0)
            n_neg = sum(1 for t in terms if t < 0)
            # Growth rate: ratio of last to first nonzero
            growth = float(np.log1p(max_val) - np.log1p(float(abs_terms[0]))) if abs_terms else 0.0
            # Monotonicity: fraction of increasing consecutive pairs
            mono = sum(1 for i in range(len(terms) - 1) if terms[i + 1] >= terms[i]) / max(len(terms) - 1, 1)

            feat = [
                np.log1p(mean_val),
                np.log1p(max_val),
                growth,
                mono,
                float(n_zeros) / len(terms),
                float(n_neg) / len(terms),
                float(len(terms)),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("oeis", labels, features)


def load_charon_landscape(db_path: Optional[Path] = None, limit: int = 100000) -> DomainIndex:
    """
    Load the Charon embedding landscape — 119K objects with 16D coordinates,
    local curvature, and cluster assignments. This is a pre-computed
    embedding of the entire LMFDB object space.

    Data source: Redis landscape:* hashes (migrated from DuckDB 2026-04-16).
    Falls back to Redis scan since landscape data is stored as hashes.
    """
    import redis as _redis
    import json as _json
    try:
        from prometheus_data.config import get_redis_config
        r = _redis.Redis(**get_redis_config(), decode_responses=True)
    except Exception:
        r = _redis.Redis(host='localhost', port=6379, password='prometheus', decode_responses=True)

    rows = []
    count = 0
    for key in r.scan_iter("landscape:*", count=5000):
        if key == "landscape:by_curvature" or key.startswith("landscape:by_cluster"):
            continue
        obj_id = key.split(":")[-1]
        data = r.hgetall(key)
        coords = _json.loads(data.get("coordinates", "[]"))
        curvature = float(data.get("curvature", 0))
        cluster = int(data.get("cluster_id", 0))
        rows.append((obj_id, coords, curvature, cluster))
        count += 1
        if count >= limit:
            break

    labels, feats = [], []
    for row in rows:
        obj_id, coords, curvature, cluster = row
        if not isinstance(coords, list) or len(coords) < 5:
            continue
        labels.append(str(obj_id))
        # Use first 8 embedding dimensions + curvature + cluster
        coord_feats = [float(c) for c in coords[:8]]
        feat = coord_feats + [float(curvature or 0), float(cluster or 0)]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("charon_landscape", labels, features)


def load_dissection_strategies() -> DomainIndex:
    """
    Load equation dissection strategies (S1-S34) as a dimension.

    Each object = one analytical lens. Features encode the strategy's
    properties: priority, tractability, GPU-ability, execution cost,
    and which domains it applies to. This lets the tensor discover
    which analytical methods are entangled with which mathematical domains.
    """
    # Strategies with their metadata from the doc
    strategies = [
        {"id": "S01", "name": "Complex plane extension", "priority": 9, "tract": 3, "gpu": 1, "time_min": 120, "domains": [8, 4]},
        {"id": "S02", "name": "Fractional derivative", "priority": 7, "tract": 3, "gpu": 1, "time_min": 30, "domains": []},
        {"id": "S03", "name": "Modular arithmetic projection", "priority": 10, "tract": 5, "gpu": 1, "time_min": 10, "domains": [9, 10, 1]},
        {"id": "S04", "name": "Topological signatures", "priority": 8, "tract": 3, "gpu": 1, "time_min": 60, "domains": [3, 0, 7]},
        {"id": "S05", "name": "Fourier spectral decomposition", "priority": 8, "tract": 5, "gpu": 1, "time_min": 5, "domains": [4, 8]},
        {"id": "S06", "name": "Phase space attractors", "priority": 7, "tract": 3, "gpu": 1, "time_min": 30, "domains": []},
        {"id": "S07", "name": "p-adic evaluation", "priority": 9, "tract": 3, "gpu": 0.5, "time_min": 20, "domains": [9, 1, 11]},
        {"id": "S08", "name": "Level set topology Morse", "priority": 7, "tract": 3, "gpu": 1, "time_min": 120, "domains": []},
        {"id": "S09", "name": "Symmetry group detection", "priority": 8, "tract": 2, "gpu": 0, "time_min": 60, "domains": [3, 7, 2]},
        {"id": "S10", "name": "Galois group of roots", "priority": 9, "tract": 3, "gpu": 0, "time_min": 30, "domains": [1, 0]},
        {"id": "S11", "name": "Monodromy representation", "priority": 7, "tract": 2, "gpu": 0, "time_min": 120, "domains": []},
        {"id": "S12", "name": "Zeta function of variety", "priority": 10, "tract": 3, "gpu": 1, "time_min": 15, "domains": [9, 3, 11]},
        {"id": "S13", "name": "Discriminant and resultant", "priority": 8, "tract": 5, "gpu": 0, "time_min": 5, "domains": [1, 0]},
        {"id": "S14", "name": "Newton polytope", "priority": 7, "tract": 5, "gpu": 0, "time_min": 5, "domains": [6]},
        {"id": "S15", "name": "Grobner basis signature", "priority": 6, "tract": 1, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S16", "name": "Hodge diamond", "priority": 6, "tract": 1, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S17", "name": "Motivic integration", "priority": 3, "tract": 0, "gpu": 0, "time_min": 999, "domains": []},
        {"id": "S18", "name": "Tropical geometry skeleton", "priority": 8, "tract": 3, "gpu": 0, "time_min": 30, "domains": []},
        {"id": "S19", "name": "Singularity classification ADE", "priority": 9, "tract": 2, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S20", "name": "Differential Galois group", "priority": 7, "tract": 2, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S21", "name": "Automorphic form association", "priority": 10, "tract": 2, "gpu": 0, "time_min": 120, "domains": [9, 10]},
        {"id": "S22", "name": "Operadic structure", "priority": 8, "tract": 3, "gpu": 0, "time_min": 10, "domains": [8]},
        {"id": "S23", "name": "Convexity profile Hessian", "priority": 7, "tract": 5, "gpu": 0, "time_min": 10, "domains": []},
        {"id": "S24", "name": "Information theoretic", "priority": 6, "tract": 5, "gpu": 0, "time_min": 5, "domains": []},
        {"id": "S25", "name": "Renormalization group flow", "priority": 7, "tract": 2, "gpu": 0, "time_min": 30, "domains": []},
        {"id": "S26", "name": "Spectral curve", "priority": 8, "tract": 2, "gpu": 0, "time_min": 60, "domains": [4, 11]},
        {"id": "S27", "name": "Arithmetic dynamics orbits", "priority": 7, "tract": 3, "gpu": 0, "time_min": 20, "domains": []},
        {"id": "S28", "name": "Resurgence Borel summation", "priority": 6, "tract": 2, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S29", "name": "Differential Galois Picard-Vessiot", "priority": 8, "tract": 2, "gpu": 0, "time_min": 60, "domains": []},
        {"id": "S30", "name": "Tropicalization skeleton", "priority": 8, "tract": 3, "gpu": 0, "time_min": 30, "domains": []},
        {"id": "S31", "name": "Functional equation symmetry", "priority": 9, "tract": 2, "gpu": 0, "time_min": 60, "domains": [9, 10]},
        {"id": "S32", "name": "Coefficient field", "priority": 8, "tract": 3, "gpu": 0, "time_min": 10, "domains": [1]},
        {"id": "S33", "name": "Recursion operator extraction", "priority": 9, "tract": 3, "gpu": 0, "time_min": 20, "domains": []},
        {"id": "S34", "name": "Categorical equivalence functoriality", "priority": 9, "tract": 3, "gpu": 0, "time_min": 30, "domains": []},
    ]

    # Domain index: 0=knots, 1=NF, 2=SG, 3=genus2, 4=maass, 5=lattices,
    #               6=polytopes, 7=materials, 8=fungrim, 9=EC, 10=MF, 11=isogenies

    labels, feats = [], []
    for s in strategies:
        labels.append(f"{s['id']}_{s['name'][:30]}")

        # Domain applicability vector (12 dims)
        domain_vec = [0.0] * 12
        for d in s["domains"]:
            if d < 12:
                domain_vec[d] = 1.0

        feat = [
            float(s["priority"]),
            float(s["tract"]),
            float(s["gpu"]),
            np.log1p(float(s["time_min"])),
            float(len(s["domains"])),  # domain coverage
        ] + domain_vec

        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("dissection", labels, features)


def load_dynamics(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load arithmetic dynamics signatures — Lyapunov exponents, orbit
    classifications, phase portrait statistics for OEIS sequences treated
    as discrete dynamical systems.

    10 features per object:
      lyapunov, orbit_type (encoded), period, n_returns, n_terms,
      correlation, n_diagonal, unique_pairs, phase_density,
      log_n_terms
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "arithmetic_dynamics_signatures.jsonl"

    # Encode orbit types as integers
    orbit_type_map = {
        "fixed_point": 0, "periodic": 1, "quasiperiodic": 2,
        "chaotic": 3, "divergent": 4, "constant": 5,
    }

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("seq_id", str(len(labels))))

            lyap = rec.get("lyapunov")
            period = rec.get("period")
            ps = rec.get("phase_portrait_stats", {})

            feat = [
                float(lyap) if lyap is not None else 0.0,
                float(orbit_type_map.get(rec.get("orbit_type", ""), -1)),
                float(period) if period is not None else 0.0,
                float(rec.get("n_returns", 0)),
                float(rec.get("n_terms", 0)),
                float(ps.get("correlation", 0)),
                float(ps.get("n_diagonal", 0)),
                float(ps.get("unique_pairs", 0)),
                float(ps.get("phase_density", 0)),
                np.log1p(float(rec.get("n_terms", 0))),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("dynamics", labels, features)


def load_phase_space(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load phase space signatures — autocorrelation lags, mutual information,
    Lyapunov exponents, and fixed-point counts for OEIS sequences.

    10 features per object:
      n_terms, autocorr_1, autocorr_2, autocorr_3, mutual_info,
      lyapunov, orbit_type (encoded), n_fixed_points, period,
      log_n_terms
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "phase_space_signatures.jsonl"

    orbit_type_map = {
        "fixed_point": 0, "periodic": 1, "quasiperiodic": 2,
        "chaotic": 3, "divergent": 4, "constant": 5,
    }

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("seq_id", str(len(labels))))

            lyap = rec.get("lyapunov")
            period = rec.get("period")

            feat = [
                float(rec.get("n_terms", 0)),
                float(rec.get("autocorr_1", 0)),
                float(rec.get("autocorr_2", 0)),
                float(rec.get("autocorr_3", 0)),
                float(rec.get("mutual_info", 0)),
                float(lyap) if lyap is not None else 0.0,
                float(orbit_type_map.get(rec.get("orbit_type", ""), -1)),
                float(rec.get("n_fixed_points", 0)),
                float(period) if period is not None else 0.0,
                np.log1p(float(rec.get("n_terms", 0))),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("phase_space", labels, features)


def load_spectral_sigs(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load FFT power spectra of mathematical formulas (spectral_signatures.jsonl).

    Features capture the frequency-domain decomposition of formula structure:
    centroid, bandwidth, entropy, rolloff, and top 10 FFT magnitudes.
    These are the calculus/trig fingerprints — spectral decomposition of formulas.
    Phoneme: Phasma (spectral essence).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "spectral_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("id", str(len(labels))))

            top_mags = rec.get("top_magnitudes", [])[:10]
            top_mags_padded = (list(top_mags) + [0.0] * 10)[:10]

            feat = [
                float(rec.get("centroid", 0)),
                float(rec.get("bandwidth", 0)),
                float(rec.get("entropy", 0)),
                float(rec.get("rolloff", 0)),
            ] + [float(m) for m in top_mags_padded]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("spectral_sigs", labels, features)


def load_operadic_sigs(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load operadic (compositional skeleton) signatures of formulas.

    Features capture the algebraic composition tree structure:
    n_ops, is_symmetric, arity profile length, and depth profile statistics
    (number of distinct operators, mean/max depth, depth spread).
    These encode the compositional DNA of mathematical formulas.
    Phoneme: Taxis (order/structure).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "operadic_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("hash", str(len(labels))))

            # Parse arity_profile string to get length
            arity_str = rec.get("arity_profile", "")
            arity_entries = [e for e in arity_str.split(",") if e.strip()] if arity_str else []

            # Parse depth_profile "op:lo-hi|op:lo-hi" to get stats
            depth_str = rec.get("depth_profile", "")
            depth_entries = [e for e in depth_str.split("|") if e.strip()] if depth_str else []
            depths_lo, depths_hi = [], []
            for entry in depth_entries:
                parts = entry.split(":")
                if len(parts) == 2:
                    range_parts = parts[1].split("-")
                    if len(range_parts) == 2:
                        try:
                            depths_lo.append(int(range_parts[0]))
                            depths_hi.append(int(range_parts[1]))
                        except ValueError:
                            pass

            n_distinct_ops = len(depth_entries)
            mean_depth = float(np.mean(depths_hi)) if depths_hi else 0.0
            max_depth = float(max(depths_hi)) if depths_hi else 0.0
            depth_spread = float(np.mean([h - l for l, h in zip(depths_lo, depths_hi)])) if depths_lo else 0.0

            feat = [
                float(rec.get("n_ops", 0)),
                float(rec.get("is_symmetric", False)),
                float(len(arity_entries)),
                float(n_distinct_ops),
                mean_depth,
                max_depth,
                depth_spread,
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("operadic_sigs", labels, features)


def load_metabolism(data_dir: Optional[Path] = None) -> DomainIndex:
    """
    Load metabolic network models (BiGG/COBRA format) as a domain.

    Each object is a genome-scale metabolic model. 113 files exist but
    we skip non-model JSON files. Features capture network topology,
    stoichiometric structure, and biological organization:

    11 features per object:
      n_reactions, n_metabolites, n_genes,
      mean_stoich_participants, max_stoich_participants,
      frac_reversible, n_compartments, n_subsystems,
      connectivity_ratio (met/rxn), gene_coverage,
      log_n_reactions
    """
    data_dir = data_dir or CARTOGRAPHY / "metabolism" / "data"

    labels, feats = [], []
    for fname in sorted(os.listdir(data_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = data_dir / fname
        try:
            with open(fpath) as f:
                d = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        # Skip non-model files (need reactions, metabolites, genes)
        if not isinstance(d, dict) or "reactions" not in d:
            continue

        rxns = d["reactions"]
        mets = d.get("metabolites", [])
        genes = d.get("genes", [])
        n_rxn = len(rxns)
        n_met = len(mets)
        n_gen = len(genes)

        if n_rxn < 10:
            continue

        # Stoichiometric participation counts per reaction
        stoich_counts = []
        reversible = 0
        gene_reactions = 0
        subsystems = set()
        for r in rxns:
            met_dict = r.get("metabolites", {})
            stoich_counts.append(len(met_dict))
            if r.get("lower_bound", 0) < 0:
                reversible += 1
            if r.get("gene_reaction_rule", "").strip():
                gene_reactions += 1
            ss = r.get("subsystem", "")
            if ss:
                subsystems.add(ss)

        mean_stoich = float(np.mean(stoich_counts)) if stoich_counts else 0.0
        max_stoich = float(max(stoich_counts)) if stoich_counts else 0.0

        model_id = d.get("id", fname.replace(".json", ""))
        labels.append(model_id)
        feat = [
            float(n_rxn),
            float(n_met),
            float(n_gen),
            mean_stoich,
            max_stoich,
            reversible / max(n_rxn, 1),
            float(len(d.get("compartments", {}))),
            float(len(subsystems)),
            n_met / max(n_rxn, 1),
            gene_reactions / max(n_rxn, 1),
            np.log1p(float(n_rxn)),
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("metabolism", labels, features)


def load_chemistry(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load QM9 molecular property dataset as a domain.

    133K small organic molecules with quantum-chemical properties
    computed at B3LYP/6-31G(2df,p) level of theory.

    12 features per object:
      A, B, C (rotational constants),
      mu (dipole moment), alpha (isotropic polarizability),
      homo, lumo, gap (orbital energies),
      r2 (electronic spatial extent), zpve (zero-point vibrational energy),
      cv (heat capacity at 298.15K),
      u0 (internal energy at 0K)
    """
    import csv
    path = path or CARTOGRAPHY / "chemistry" / "data" / "qm9.csv"

    labels, feats = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row.get("mol_id", str(len(labels))))
            feat = [
                float(row.get("A", 0)),
                float(row.get("B", 0)),
                float(row.get("C", 0)),
                float(row.get("mu", 0)),
                float(row.get("alpha", 0)),
                float(row.get("homo", 0)),
                float(row.get("lumo", 0)),
                float(row.get("gap", 0)),
                float(row.get("r2", 0)),
                float(row.get("zpve", 0)),
                float(row.get("cv", 0)),
                float(row.get("u0", 0)),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("chemistry", labels, features)


def load_codata(path: Optional[Path] = None) -> DomainIndex:
    """
    Load CODATA physical constants (286 constants).

    10 native features per constant — derived from value, uncertainty,
    unit, and name metadata. No proxy features from formula dissection.

    Features:
      0: log_abs_value        — log10(|value|), the magnitude scale
      1: sign                 — sign of value (+1 or -1)
      2: log_uncertainty      — log10(uncertainty), measurement precision
      3: log_relative_unc     — log10(uncertainty/|value|), relative precision
      4: order_of_magnitude   — floor(log10(|value|))
      5: is_dimensionless     — 1.0 if no unit, 0.0 otherwise
      6: unit_category        — integer encoding of unit type
      7: is_ratio             — 1.0 if name contains 'ratio'
      8: is_mass_related      — 1.0 if name contains 'mass'
      9: is_magnetic          — 1.0 if name contains 'mag.' or 'moment'
    """
    import math
    path = path or CARTOGRAPHY / "physics" / "data" / "codata" / "constants.json"
    with open(path) as f:
        data = json.load(f)

    # Build unit category map
    all_units = sorted(set(c.get("unit", "") for c in data))
    unit_map = {u: i for i, u in enumerate(all_units)}

    labels, feats = [], []
    for c in data:
        name = c.get("name", "")
        labels.append(name[:60])

        value = float(c.get("value", 0))
        unc = float(c.get("uncertainty", 0) or 0)
        unit = c.get("unit", "")

        abs_val = abs(value) if value != 0 else 1e-300
        sign = 1.0 if value >= 0 else -1.0
        log_abs = math.log10(abs_val) if abs_val > 0 else -300.0
        log_unc = math.log10(unc) if unc > 0 else -30.0
        log_rel = math.log10(unc / abs_val) if unc > 0 and abs_val > 0 else -30.0
        oom = math.floor(log_abs) if abs_val > 0 else 0
        is_dimless = 1.0 if not unit else 0.0
        unit_cat = float(unit_map.get(unit, 0))
        name_lower = name.lower()
        is_ratio = 1.0 if "ratio" in name_lower else 0.0
        is_mass = 1.0 if "mass" in name_lower else 0.0
        is_mag = 1.0 if ("mag." in name_lower or "moment" in name_lower) else 0.0

        feat = [
            log_abs,
            sign,
            log_unc,
            log_rel,
            float(oom),
            is_dimless,
            unit_cat,
            is_ratio,
            is_mass,
            is_mag,
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("codata", labels, features)


def load_pdg_particles(path: Optional[Path] = None) -> DomainIndex:
    """
    Load PDG particle data (226 particles).

    11 native features per particle — mass, width, error structure, and
    quantum numbers decoded from the Monte Carlo ID (PDG numbering scheme).

    WARNING from M1: 225 particles in 13/182 active dimensions created
    geometric illusions (6/8 kills). These native features avoid that trap
    by staying in the particle domain's own coordinate system rather than
    projecting through the full tensor at high dimension.

    Features:
      0: log_mass             — log10(mass_GeV), energy scale
      1: log_width            — log10(width_GeV), inverse lifetime
      2: relative_mass_err    — log10(err_plus/mass), measurement precision
      3: mass_err_asymmetry   — (err_plus + err_minus) / max(err_plus - err_minus, eps)
      4: is_stable            — 1.0 if width == 0 (stable particle)
      5: spin_2j_plus_1       — 2J+1 from MC ID last digit
      6: nq1                  — quark content digit 1 from MC ID
      7: nq2                  — quark content digit 2 from MC ID
      8: nq3                  — quark content digit 3 from MC ID
      9: n_radial             — radial excitation quantum number from MC ID
     10: is_hadron            — 1.0 if has quark content (mc_id >= 100)
    """
    import math
    path = path or CARTOGRAPHY / "physics" / "data" / "pdg" / "particles.json"
    with open(path) as f:
        data = json.load(f)

    labels, feats = [], []
    for p in data:
        name = p.get("name", "")
        mc_id = p.get("mc_ids", [0])[0]
        mass = float(p.get("mass_GeV", 0) or 0)
        width = float(p.get("width_GeV", 0) or 0)
        err_plus = float(p.get("mass_err_plus", 0) or 0)
        err_minus = float(p.get("mass_err_minus", 0) or 0)

        # Label: use mc_id + name snippet
        labels.append(f"PDG{mc_id}_{name.strip()[:30]}")

        # Derived features
        log_mass = math.log10(mass) if mass > 0 else -30.0
        log_width = math.log10(width) if width > 0 else -30.0
        rel_err = math.log10(abs(err_plus) / mass) if mass > 0 and err_plus != 0 else -30.0
        # Asymmetry: (|err+| - |err-|) / max(|err+| + |err-|, eps) — 0 if symmetric
        sum_err = abs(err_plus) + abs(err_minus)
        diff_err = abs(err_plus) - abs(err_minus)
        asym = diff_err / max(sum_err, 1e-30)
        is_stable = 1.0 if width == 0 else 0.0

        # Decode quantum numbers from PDG MC ID
        aid = abs(mc_id)
        nj = aid % 10                  # 2J+1
        nq3 = (aid // 10) % 10         # quark 3
        nq2 = (aid // 100) % 10        # quark 2
        nq1 = (aid // 1000) % 10       # quark 1
        nr = (aid // 100000) % 10      # radial excitation
        is_hadron = 1.0 if aid >= 100 else 0.0

        feat = [
            log_mass,
            log_width,
            rel_err,
            asym,
            is_stable,
            float(nj),
            float(nq1),
            float(nq2),
            float(nq3),
            float(nr),
            is_hadron,
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("pdg_particles", labels, features)


def load_padic_sigs(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load p-adic valuation signatures — Newton polygon features for primes 2,3,5,7,11.

    Features capture the p-adic landscape of mathematical objects:
    n_segments, min/max valuation, total_width for each prime.
    Phoneme: Topos (place/locality).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "padic_signatures.jsonl"

    primes = ["2", "3", "5", "7", "11"]
    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("id", str(len(labels))))

            padic = rec.get("padic", {})
            feat = []
            for p in primes:
                pd = padic.get(p, {})
                feat.append(float(pd.get("n_segments") or 0))
                feat.append(float(pd.get("min_valuation") or 0))
                feat.append(float(pd.get("max_valuation") or 0))
                feat.append(float(pd.get("total_width") or 0))
            # 20 features from 5 primes x 4 stats -- trim to 10 most informative
            # Keep: n_segments and max_valuation for each prime (2 per prime = 10)
            feat_trimmed = []
            for i, p in enumerate(primes):
                feat_trimmed.append(feat[i * 4 + 0])  # n_segments
                feat_trimmed.append(feat[i * 4 + 2])  # max_valuation
            feats.append(feat_trimmed)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("padic_sigs", labels, features)


def load_info_theoretic(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load information-theoretic signatures — Shannon entropy, compression ratios,
    LZ complexity for OEIS sequences.

    Phoneme: Auxesis (growth).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "info_theoretic_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("id", str(len(labels))))

            feat = [
                float(rec.get("entropy", 0)),
                float(rec.get("compression_ratio", 0)),
                float(rec.get("lz_complexity", 0)),
                float(rec.get("diff_entropy", 0)),
                float(rec.get("n_terms", 0)),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("info_theoretic", labels, features)


def load_fractional_deriv(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load fractional derivative signatures — fractional calculus invariants
    evaluated at multiple fractional orders and evaluation points.

    Features: 9 entries of the signature_vector (fractional derivatives at
    3 alpha values x 3 evaluation points).
    Phoneme: Phasma (spectral).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "fractional_derivative_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("id", str(len(labels))))

            sig_vec = rec.get("signature_vector", [])
            # Pad/truncate to 9 entries
            sig_padded = (list(sig_vec) + [0.0] * 9)[:9]
            feat = [float(v) if v is not None else 0.0 for v in sig_padded]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("fractional_deriv", labels, features)


def load_functional_eq(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load functional equation classification signatures — reflection, shift,
    scaling, multiplicative, and duplication symmetry detection.

    Phoneme: Symmetria.
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "functional_equation_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("hash", str(len(labels))))

            feat = [
                float(rec.get("has_reflection", False)),
                float(rec.get("has_shift", False)),
                float(rec.get("has_scaling", False)),
                float(rec.get("has_multiplicative", False)),
                float(rec.get("has_duplication", False)),
                float(rec.get("n_reflections", 0)),
                float(rec.get("n_shifts", 0)),
                float(rec.get("n_scalings", 0)),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("functional_eq", labels, features)


def load_resurgence(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load resurgence / Borel summability signatures — radius of convergence,
    Gevrey order, divergence rate, growth rate from OEIS sequences.

    Phoneme: Phasma (spectral).
    """
    path = path or CARTOGRAPHY / "convergence" / "data" / "resurgence_signatures.jsonl"

    labels, feats = [], []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            labels.append(rec.get("id", str(len(labels))))

            sig = rec.get("signature", rec)  # data is nested under "signature" key
            feat = [
                float(sig.get("radius_of_convergence") or 0),
                float(sig.get("radius_root_test") or 0),
                float(sig.get("radius_ratio_test") or 0),
                float(sig.get("gevrey_order") or 0),
                float(sig.get("gevrey_fit_r2") or 0),
                float(sig.get("is_borel_summable") or 0),
                float(sig.get("divergence_rate") or 0),
                float(sig.get("growth_rate_tail") or 0),
                float(sig.get("n_terms") or 0),
            ]
            feats.append(feat)

            if len(feats) >= limit:
                break

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("resurgence", labels, features)


def load_disagreement(db_path: Optional[Path] = None) -> DomainIndex:
    """Load disagreement atlas from Postgres (prometheus_fire.analysis.disagreement_atlas, 119K rows).

    Objects where different analysis methods disagreed. Features capture
    the nature and extent of disagreement: conductor, rank, torsion, CM flag,
    jaccard similarity, precision, recall, zero coherence, graph degree,
    component size, neighbor counts, and overlap.
    """
    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute("""
        SELECT label, conductor, rank, torsion, cm,
               jaccard, precision_score, recall_score, zero_coherence,
               graph_degree, component_size, n_zero_nn, n_graph_nn, n_overlap,
               disagreement_type
        FROM analysis.disagreement_atlas
        WHERE label IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    # Encode disagreement_type as numeric
    type_map = {"A": 0.0, "B": 1.0, "C": 2.0, "D": 3.0}

    labels, feats = [], []
    for row in rows:
        labels.append(row[0])
        feat = [
            np.log1p(float(row[1] or 0)),    # log_conductor
            float(row[2] or 0),               # rank
            float(row[3] or 0),               # torsion
            float(row[4] or 0),               # cm flag
            float(row[5] or 0),               # jaccard
            float(row[6] or 0),               # precision_score
            float(row[7] or 0),               # recall_score
            float(row[8] or 0),               # zero_coherence
            float(row[9] or 0),               # graph_degree
            float(row[10] or 0),              # component_size
            float(row[11] or 0),              # n_zero_nn
            float(row[12] or 0),              # n_graph_nn
            float(row[13] or 0),              # n_overlap
            type_map.get(row[14], 0.0),       # disagreement_type encoded
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("disagreement", labels, features)


def load_knowledge_graph(db_path: Optional[Path] = None) -> DomainIndex:
    """Load knowledge graph summary statistics per object from Redis.

    Computes per-object features from Redis graph:neighbors:* adjacency sets.
    Graph edges were migrated from DuckDB to Redis on 2026-04-16.
    Note: Redis stores adjacency only (no weight/type), so we use degree only.
    """
    import redis as _redis
    try:
        from prometheus_data.config import get_redis_config
        r = _redis.Redis(**get_redis_config(), decode_responses=True)
    except Exception:
        r = _redis.Redis(host='localhost', port=6379, password='prometheus', decode_responses=True)

    rows = []
    for key in r.scan_iter("graph:neighbors:*", count=5000):
        obj_id = key.split(":")[-1]
        degree = r.scard(key)
        rows.append((obj_id, degree))

    labels, feats = [], []
    for row in rows:
        labels.append(str(row[0]))
        degree = float(row[1] or 0)
        feat = [
            np.log1p(degree),                  # log_degree
            degree,                            # raw_degree
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("knowledge_graph", labels, features)


def load_bridges(db_path: Optional[Path] = None) -> DomainIndex:
    """Load known cross-domain bridges from Postgres (prometheus_fire.xref.bridges, 17K rows).

    Features per source object: number of bridges, whether verified,
    and bridge type encoding.
    """
    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.source_key AS source_label,
            COUNT(*) AS n_bridges,
            SUM(CASE WHEN b.evidence_grade = 'verified' THEN 1 ELSE 0 END) AS n_verified,
            SUM(CASE WHEN b.bridge_type = 'modularity' THEN 1 ELSE 0 END) AS n_modularity
        FROM xref.bridges b
        JOIN xref.object_registry r ON r.object_id = b.source_object_id
        WHERE r.source_key IS NOT NULL
        GROUP BY r.source_key
    """)
    rows = cur.fetchall()
    conn.close()

    labels, feats = [], []
    for row in rows:
        labels.append(row[0])
        n_bridges = float(row[1] or 0)
        n_verified = float(row[2] or 0)
        n_modularity = float(row[3] or 0)
        feat = [
            np.log1p(n_bridges),               # log_n_bridges
            n_verified / max(n_bridges, 1.0),   # verified_fraction
            n_modularity / max(n_bridges, 1.0), # modularity_fraction
            n_bridges,                          # raw bridge count
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("bridges", labels, features)


def load_lmfdb_objects(db_path: Optional[Path] = None) -> DomainIndex:
    """Load LMFDB objects with invariant vectors from Postgres (prometheus_fire.xref.object_registry, 134K rows).

    The invariant_vector is a 50-dimensional float vector capturing deep
    arithmetic invariants. We also extract conductor and completeness scores.
    """
    conn = _pg_fire()
    cur = conn.cursor()
    cur.execute("""
        SELECT source_key, conductor, invariant_vector,
               coefficient_completeness, 0.0 AS zeros_completeness, object_type
        FROM xref.object_registry
        WHERE invariant_vector IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    # Encode object_type
    type_map = {"elliptic_curve": 0.0, "modular_form": 1.0, "genus2_curve": 2.0}

    labels, feats = [], []
    for row in rows:
        label = row[0] or str(len(labels))
        conductor = float(row[1] or 0)
        inv_vec = row[2]  # list of 50 floats
        coeff_comp = float(row[3] or 0)
        zeros_comp = float(row[4] or 0)
        obj_type = type_map.get(row[5], -1.0)

        # Build feature vector: log_conductor + invariant_vector(50) +
        # completeness(2) + object_type(1) = 54 features
        feat = [np.log1p(conductor)] + [float(v or 0) for v in inv_vec] + [
            coeff_comp,
            zeros_comp,
            obj_type,
        ]
        labels.append(label)
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("lmfdb_objects", labels, features)


def _ec_rich_from_postgres(host: str, limit: int) -> list:
    """Try loading EC data from a Postgres instance."""
    import psycopg2
    conn = psycopg2.connect(
        host=host, port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=15,
    )
    cur = conn.cursor()
    cur.execute(f'''
        SELECT lmfdb_label, conductor, rank, analytic_rank, torsion,
               regulator, cm, num_bad_primes, class_size, class_deg,
               degree, sha, num_int_pts, faltings_height, abc_quality,
               szpiro_ratio, semistable
        FROM ec_curvedata
        WHERE conductor IS NOT NULL AND rank IS NOT NULL
        ORDER BY conductor LIMIT {limit}
    ''')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def _ec_rich_from_csv(limit: int) -> list:
    """Load EC data from local CSV fallback."""
    import csv
    csv_paths = [
        Path("F:/lmfdb_local/ec_curvedata.csv"),
        Path("C:/prometheus_share/lmfdb_local/ec_curvedata.csv"),
    ]
    for csv_path in csv_paths:
        if csv_path.exists():
            rows = []
            cols = ['lmfdb_label', 'conductor', 'rank', 'analytic_rank', 'torsion',
                    'regulator', 'cm', 'num_bad_primes', 'class_size', 'class_deg',
                    'degree', 'sha', 'num_int_pts', 'faltings_height', 'abc_quality',
                    'szpiro_ratio', 'semistable']
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    rows.append(tuple(row.get(c, '') for c in cols))
            return rows
    raise FileNotFoundError("No EC CSV found at F:/lmfdb_local/ or C:/prometheus_share/lmfdb_local/")


def load_ec_rich(limit: int = 100000) -> DomainIndex:
    """
    Load rich elliptic curve data (16 features) from Postgres or CSV fallback.

    Fallback chain: local Postgres -> CSV -> remote LMFDB mirror.

    Features: log_conductor, rank, analytic_rank, torsion, regulator, CM,
    num_bad_primes, class_size, class_deg, degree, sha, num_int_pts,
    faltings_height, abc_quality, szpiro_ratio, semistable.
    """
    rows = None
    # Try local Postgres first
    for host in ['localhost', 'devmirror.lmfdb.xyz']:
        try:
            rows = _ec_rich_from_postgres(host, limit)
            if rows:
                break
        except Exception:
            continue
    # CSV fallback
    if not rows:
        try:
            rows = _ec_rich_from_csv(limit)
        except FileNotFoundError:
            raise RuntimeError(
                "load_ec_rich: no data source available. "
                "Need local Postgres, CSV at F:/lmfdb_local/, or devmirror.lmfdb.xyz"
            )

    def _safe_float(val):
        if val is None or val == '':
            return 0.0
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        if isinstance(val, str) and val.lower() in ('true', 'false'):
            return 1.0 if val.lower() == 'true' else 0.0
        return float(val)

    labels, feats = [], []
    for row in rows:
        labels.append(str(row[0] or len(labels)))
        feat = [
            np.log1p(_safe_float(row[1])),    # log_conductor
            _safe_float(row[2]),               # rank
            _safe_float(row[3]),               # analytic_rank
            _safe_float(row[4]),               # torsion
            _safe_float(row[5]),               # regulator
            _safe_float(row[6]),               # CM discriminant (0 = no CM)
            _safe_float(row[7]),               # num_bad_primes
            _safe_float(row[8]),               # class_size
            _safe_float(row[9]),               # class_deg
            _safe_float(row[10]),              # degree
            _safe_float(row[11]),              # sha (analytic)
            _safe_float(row[12]),              # num_int_pts
            _safe_float(row[13]),              # faltings_height
            _safe_float(row[14]),              # abc_quality
            _safe_float(row[15]),              # szpiro_ratio
            _safe_float(row[16]),              # semistable (bool -> 0/1)
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("ec_rich", labels, features)


def _artin_from_postgres(host: str, limit: int) -> list:
    """Try loading Artin rep data from a Postgres instance."""
    import psycopg2
    conn = psycopg2.connect(
        host=host, port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=15,
    )
    cur = conn.cursor()
    cur.execute(f'''
        SELECT "Baselabel", "Dim", "Conductor", "Galn", "Galt", "Indicator"
        FROM artin_reps
        WHERE "Conductor" IS NOT NULL
        ORDER BY "Conductor" LIMIT {limit}
    ''')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def _artin_from_csv(limit: int) -> list:
    """Load Artin rep data from local CSV fallback."""
    import csv
    csv_paths = [
        Path("F:/lmfdb_local/artin_reps.csv"),
        Path("C:/prometheus_share/lmfdb_local/artin_reps.csv"),
    ]
    for csv_path in csv_paths:
        if csv_path.exists():
            rows = []
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    rows.append((
                        row.get('Baselabel', ''),
                        row.get('Dim', '0'),
                        row.get('Conductor', '0'),
                        row.get('Galn', '0'),
                        row.get('Galt', '0'),
                        row.get('Indicator', '0'),
                    ))
            return rows
    raise FileNotFoundError("No Artin CSV found at F:/lmfdb_local/ or C:/prometheus_share/lmfdb_local/")


def load_artin(limit: int = 100000) -> DomainIndex:
    """
    Load Artin representations from Postgres or CSV fallback.

    Fallback chain: local Postgres -> CSV -> remote LMFDB mirror.

    Features: log_conductor, dimension, Galois_n (order), Galois_t (transitive number),
    indicator (Frobenius-Schur).
    """
    rows = None
    for host in ['localhost', 'devmirror.lmfdb.xyz']:
        try:
            rows = _artin_from_postgres(host, limit)
            if rows:
                break
        except Exception:
            continue
    if not rows:
        try:
            rows = _artin_from_csv(limit)
        except FileNotFoundError:
            raise RuntimeError(
                "load_artin: no data source available. "
                "Need local Postgres, CSV at F:/lmfdb_local/, or devmirror.lmfdb.xyz"
            )

    labels, feats = [], []
    for row in rows:
        labels.append(str(row[0] or len(labels)))
        conductor = row[2]
        # Conductor may be a string or numeric; handle both
        try:
            cond_val = float(conductor)
        except (TypeError, ValueError):
            cond_val = 0.0
        feat = [
            np.log1p(cond_val),               # log_conductor
            float(row[1] or 0),               # dimension
            float(row[3] or 0),               # Galn (Galois group order)
            float(row[4] or 0),               # Galt (transitive number)
            float(row[5] or 0),               # indicator (Frobenius-Schur)
        ]
        feats.append(feat)

    features = _normalize(torch.tensor(feats, dtype=torch.float32))
    return DomainIndex("artin", labels, features)


# Registry of all loaders
DOMAIN_LOADERS = {
    "knots": load_knots,
    "number_fields": load_number_fields,
    "space_groups": load_space_groups,
    "genus2": load_genus2,
    "maass": load_maass,
    "lattices": load_lattices,
    "polytopes": load_polytopes,
    "materials": load_materials,
    "fungrim": load_fungrim,
    "elliptic_curves": load_elliptic_curves,
    "modular_forms": load_modular_forms,
    "dirichlet_zeros": load_dirichlet_zeros,
    "ec_zeros": load_ec_zeros,
    "rmt": load_rmt_ensemble,
    "raw_zeros": load_raw_zeros,
    "zeros_anchored": load_zeros_anchored,
    "bianchi": load_bianchi_forms,
    "groups": load_groups,
    "belyi": load_belyi,
    "oeis": load_oeis,
    "charon_landscape": load_charon_landscape,
    "battery": load_battery,
    "dissection": load_dissection_strategies,
    "dynamics": load_dynamics,
    "phase_space": load_phase_space,
    "spectral_sigs": load_spectral_sigs,
    "operadic_sigs": load_operadic_sigs,
    "metabolism": load_metabolism,
    "chemistry": load_chemistry,
    "codata": load_codata,
    "pdg_particles": load_pdg_particles,
    "padic_sigs": load_padic_sigs,
    "info_theoretic": load_info_theoretic,
    "fractional_deriv": load_fractional_deriv,
    "functional_eq": load_functional_eq,
    "resurgence": load_resurgence,
    "disagreement": load_disagreement,
    "knowledge_graph": load_knowledge_graph,
    "bridges": load_bridges,
    "lmfdb_objects": load_lmfdb_objects,
    "ec_rich": load_ec_rich,
    "artin": load_artin,
}


def load_domains(*names: str, device: str = "cpu") -> dict[str, DomainIndex]:
    """Load multiple domains by name."""
    result = {}
    for name in names:
        if name not in DOMAIN_LOADERS:
            raise ValueError(f"Unknown domain: {name}. Available: {list(DOMAIN_LOADERS.keys())}")
        result[name] = DOMAIN_LOADERS[name]().to(device)
    return result
