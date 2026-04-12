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
}


def load_domains(*names: str, device: str = "cpu") -> dict[str, DomainIndex]:
    """Load multiple domains by name."""
    result = {}
    for name in names:
        if name not in DOMAIN_LOADERS:
            raise ValueError(f"Unknown domain: {name}. Available: {list(DOMAIN_LOADERS.keys())}")
        result[name] = DOMAIN_LOADERS[name]().to(device)
    return result
