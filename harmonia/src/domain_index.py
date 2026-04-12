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
    """Load elliptic curves from Charon DuckDB."""
    import duckdb
    db_path = db_path or Path(CARTOGRAPHY).parent / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql("""
        SELECT lmfdb_label, conductor, rank, analytic_rank, torsion
        FROM elliptic_curves
        WHERE conductor IS NOT NULL
    """).fetchall()
    db.close()

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
    """Load modular forms from Charon DuckDB."""
    import duckdb
    db_path = db_path or Path(CARTOGRAPHY).parent / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql("""
        SELECT lmfdb_label, level, weight, dim, char_order, char_parity
        FROM modular_forms
        WHERE level IS NOT NULL
        LIMIT 50000
    """).fetchall()
    db.close()

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
    """Load Dirichlet zeros from Charon DuckDB."""
    import duckdb
    db_path = db_path or Path(CARTOGRAPHY).parent / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql("""
        SELECT lmfdb_url, conductor, degree, rank, n_zeros_stored, motivic_weight
        FROM dirichlet_zeros
        WHERE conductor IS NOT NULL
        LIMIT 50000
    """).fetchall()
    db.close()

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
    """
    import duckdb
    db_path = db_path or Path(CARTOGRAPHY).parent / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql(f"""
        SELECT ec.lmfdb_label, ec.conductor, ec.rank, ec.torsion,
               oz.zeros_vector, oz.n_zeros_stored, oz.root_number, oz.analytic_rank
        FROM object_zeros oz
        JOIN elliptic_curves ec ON oz.object_id = ec.object_id
        WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
              AND ec.conductor IS NOT NULL
        LIMIT {limit}
    """).fetchall()
    db.close()

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


def load_bianchi_forms(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
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


def load_groups(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
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


def load_oeis(path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
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


def load_charon_landscape(db_path: Optional[Path] = None, limit: int = 50000) -> DomainIndex:
    """
    Load the Charon embedding landscape — 119K objects with 16D coordinates,
    local curvature, and cluster assignments. This is a pre-computed
    embedding of the entire LMFDB object space.
    """
    import duckdb
    db_path = db_path or Path(CARTOGRAPHY).parent / "charon" / "data" / "charon.duckdb"
    db = duckdb.connect(str(db_path), read_only=True)
    rows = db.sql(f"""
        SELECT object_id, coordinates, local_curvature, cluster_id
        FROM landscape
        WHERE coordinates IS NOT NULL
        LIMIT {limit}
    """).fetchall()
    db.close()

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
    "bianchi": load_bianchi_forms,
    "groups": load_groups,
    "belyi": load_belyi,
    "oeis": load_oeis,
    "charon_landscape": load_charon_landscape,
    "battery": load_battery,
    "dissection": load_dissection_strategies,
}


def load_domains(*names: str, device: str = "cpu") -> dict[str, DomainIndex]:
    """Load multiple domains by name."""
    result = {}
    for name in names:
        if name not in DOMAIN_LOADERS:
            raise ValueError(f"Unknown domain: {name}. Available: {list(DOMAIN_LOADERS.keys())}")
        result[name] = DOMAIN_LOADERS[name]().to(device)
    return result
