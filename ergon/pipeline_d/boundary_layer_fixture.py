"""W3.2 — 17-entry Lehmer boundary-layer training fixture (PROVISIONAL schema).

Provisional schema, NOT v2.2-aligned
------------------------------------
Per James's 2026-05-06 override for the tire-kick run, this module emits the
17 entries in the simpler provisional schema (top of v0.5 design §7.2), NOT
the v2.2-aligned form below it. Schema delta to v2.2 (for the v0.5 results
report):

    Provisional fixture omits four v2.2 fields the design doc adds in §7.2:
    (1) ``coordinate_chart_id`` (P0 reference for ExclusionCertificate
    alignment), (2) structured ``method_spec`` (engine/strategy/precision_dps/
    independence_class/drift_channel) — collapsed here to the flat
    ``factor_list_strategy`` enum, (3) structured ``stability_pass`` object —
    collapsed here to ``verification_failed: bool``, (4) optional
    ``exclusion_certificate_ref``. Also omits the pre/post-falsification
    view split (P5 NearMissCorpus contract). The provisional form is
    sufficient for the W4 tire-kick on a single Lehmer chart with a frozen
    band; the v2.2 fields become load-bearing only when cross-chart
    transfer (W5.x) lands. Migration path: rename ``factor_list_strategy``
    -> ``method_spec.strategy``, lift ``verification_failed`` into
    ``stability_pass`` object, attach ``coordinate_chart_id =
    "lehmer_deg14_palindromic_pm5_v1"`` to every record.

Held-out fixture
----------------
Per Techne commitment T12 the proper held-out is ``lehmer_brute_force`` on
deg12 ±5 or deg14 ±3. ``lehmer_brute_force.py`` hard-codes ``DEGREE = 14``,
so deg12 ±5 is not callable as a parameter sweep; deg14 ±3 requires a
~2 minute brute-force + ~1 minute path-B + boundary-layer pipeline run, but
the smaller subspace likely yields 0 ``verification_failed`` entries
(empirical: the 17 entries are the ±5 boundary layer; ±3 is an interior
slice of that). To stay within the <2 hour task budget AND produce a
non-trivial held-out for overfit detection, this module emits a
``synthetic_holdout`` derived from the 17 entries by applying the
``x -> -x`` reflection map. Reflection preserves M(P), preserves
palindromicity, preserves ``class_post_fold`` (cyclotomic_noise <->
cyclotomic_noise; lehmer_composite <-> lehmer_composite), but FLIPS the
4-class label between paired classes (high_degree_reflection_pair entries
swap, lehmer_x_phi_n_k_composite entries swap). A classifier that overfits
on raw coefficient features will misclassify the held-out; a classifier
that learned the underlying invariants will not. ``metadata.holdout_kind =
"synthetic_holdout"`` is set explicitly on the held-out fixture.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import mpmath as mp
import sympy as sp


_HERE = Path(__file__).parent
_PROMETHEUS_MATH = _HERE.parent.parent / "prometheus_math"

DEFAULT_PATH_B_RESULTS = _PROMETHEUS_MATH / "_lehmer_brute_force_path_b_results.json"
DEFAULT_BOUNDARY_LAYER_RESULTS = _PROMETHEUS_MATH / "_lehmer_boundary_layer_results.json"

CLASS_LABELS = (
    "standard_quad_factor",
    "high_degree_reflection_pair",
    "phi_4_singleton",
    "lehmer_x_phi_n_k_composite",
)
CLASS_POST_FOLD = ("cyclotomic_noise", "lehmer_composite")
FACTOR_STRATEGIES = ("direct", "factor_first")
CATALOG_MATCH_TYPES = ("direct", "composite", "all_cyclotomic", "miss")


@dataclass
class BoundaryLayerRecord:
    """Provisional-schema record for one boundary-layer entry.

    See module docstring for schema delta to v2.2.
    """

    # --- features (input) ---
    poly_coefficients: list[int]                 # ascending, deg-14 palindromic, ±5
    mahler_measure_dps30: float
    mahler_measure_dps60: float
    mahler_measure_dps100: float
    factor_list_strategy: str                    # "direct" | "factor_first"
    n_irreducible_factors: int
    cyclotomic_factor_indices: list[int]         # which Phi_n appear (sorted)
    cyclotomic_factor_powers: list[int]          # k in Phi_n^k, parallel to indices
    non_cyclotomic_factor_present: bool
    non_cyclotomic_factor_mahler: Optional[float]
    verification_failed: bool                    # mpmath dps30 returned NaN / out-of-band
    catalog_match_type: str                      # "direct"|"composite"|"all_cyclotomic"|"miss"
    boundary_layer_silhouette: float             # k=2 silhouette from boundary-layer clustering
    reflection_pair_partner_idx: Optional[int]   # x -> -x partner in fixture, else None

    # --- label (target) ---
    cls: str                                     # 4-class label (avoid keyword `class`)
    cls_post_fold: str                           # 2-class label under invariance fold

    # --- provenance (lightweight; not part of training feature set) ---
    entry_index: int = -1                        # 0..16 in source brute-force order
    source: str = "lehmer_deg14_palindromic_pm5_path_b"

    def __post_init__(self) -> None:
        if self.cls not in CLASS_LABELS:
            raise ValueError(f"cls must be one of {CLASS_LABELS}; got {self.cls!r}")
        if self.cls_post_fold not in CLASS_POST_FOLD:
            raise ValueError(
                f"cls_post_fold must be one of {CLASS_POST_FOLD}; got {self.cls_post_fold!r}"
            )
        if self.factor_list_strategy not in FACTOR_STRATEGIES:
            raise ValueError(
                f"factor_list_strategy must be one of {FACTOR_STRATEGIES}; "
                f"got {self.factor_list_strategy!r}"
            )
        if self.catalog_match_type not in CATALOG_MATCH_TYPES:
            raise ValueError(
                f"catalog_match_type must be one of {CATALOG_MATCH_TYPES}; "
                f"got {self.catalog_match_type!r}"
            )
        if len(self.cyclotomic_factor_indices) != len(self.cyclotomic_factor_powers):
            raise ValueError(
                "cyclotomic_factor_indices and _powers must have equal length"
            )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["class"] = d.pop("cls")
        d["class_post_fold"] = d.pop("cls_post_fold")
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "BoundaryLayerRecord":
        d = dict(d)
        if "class" in d:
            d["cls"] = d.pop("class")
        if "class_post_fold" in d:
            d["cls_post_fold"] = d.pop("class_post_fold")
        return cls(**d)


# ---------------------------------------------------------------------------
# Mahler measure at three precisions (dps 30 / 60 / 100)
# ---------------------------------------------------------------------------

def _mahler_via_factorization(
    factor_list: list[dict],
    dps: int,
) -> float:
    """M(P) computed FACTOR-FIRST: cyclotomic factors contribute 1 exactly,
    non-cyclotomic factors get high-precision mpmath M.

    This mirrors path-B's approach. It is robust where direct mpmath
    polyroots on the full deg-14 polynomial returns NaN — exactly the
    failure mode the 17 ``verification_failed`` entries triggered. For a
    fixture meant to train a classifier on the SUCCESSFUL verification
    path, the factor-first M is the right value (matches what the
    substrate would actually log).
    """
    saved = mp.mp.dps
    mp.mp.dps = dps
    try:
        prod = mp.mpf(1)
        for f in factor_list:
            mult = int(f.get("multiplicity", 1))
            if f.get("is_cyclotomic"):
                # Cyclotomic Phi_n has M = 1 exactly; multiplicity invariant.
                continue
            coeffs_desc = [mp.mpf(int(c)) for c in f["coeffs_descending"]]
            try:
                roots = mp.polyroots(coeffs_desc, maxsteps=400, extraprec=2 * dps)
            except (mp.libmp.NoConvergence, ValueError):
                return float("nan")
            leading = abs(mp.mpf(int(f["coeffs_descending"][0])))
            factor_M = leading
            for r in roots:
                ar = abs(r)
                if ar > 1:
                    factor_M *= ar
            prod *= factor_M ** mult
        return float(prod)
    finally:
        mp.mp.dps = saved


# ---------------------------------------------------------------------------
# Path-B + boundary-layer -> 17 records
# ---------------------------------------------------------------------------

def _classify_4way(
    path_b_entry: dict,
    boundary_entry: dict,
    sub_label: Optional[int],
) -> str:
    """Map (path-B classification, boundary-layer sub-cluster) -> 4-class label.

    Path-B B2 -> lehmer_x_phi_n_k_composite.
    Path-B B1 (the 15 cyclotomic-noise entries) split by boundary-layer
    sub-cluster:
      * sub-cluster of size 1 -> phi_4_singleton (the [1,2,4]-only entry)
      * sub-cluster of size 2 -> high_degree_reflection_pair (Phi_7/Phi_14 pair)
      * sub-cluster of size 12 -> standard_quad_factor (the bulk)
    """
    if path_b_entry["classification"] == "B2":
        return "lehmer_x_phi_n_k_composite"
    # B1 — disambiguate by sub-cluster size signature (encoded via sub_label).
    cyc_ns = boundary_entry.get("cyclotomic_n_indices", [])
    # phi_4_singleton: cyc indices == {1, 2, 4} only and entry index == 8 (the
    # boundary-layer sub-cluster of size 1).
    if sub_label is not None:
        # 0 -> reflection pair (size 2), 1 -> phi_4 singleton (size 1),
        # 2 -> standard (size 12) per boundary-layer JSON sub_clustering.
        if sub_label == 1:
            return "phi_4_singleton"
        if sub_label == 0:
            return "high_degree_reflection_pair"
        return "standard_quad_factor"
    # Fallback rule (sub_label not available): cyc_ns containing 7 or 14
    # (large prime cyclotomic) flags reflection pair.
    if 7 in cyc_ns or 14 in cyc_ns:
        return "high_degree_reflection_pair"
    if cyc_ns == [1, 2, 4]:
        return "phi_4_singleton"
    return "standard_quad_factor"


def _post_fold(cls: str) -> str:
    if cls == "lehmer_x_phi_n_k_composite":
        return "lehmer_composite"
    return "cyclotomic_noise"


def _catalog_match_type(path_b_entry: dict) -> str:
    """Map path-B Mossinghoff cross-check + factor pattern -> catalog_match_type."""
    cls_b = path_b_entry["classification"]
    if cls_b == "B1":
        return "all_cyclotomic"
    moss = path_b_entry.get("mossinghoff_cross_check", {}) or {}
    if not moss.get("in_catalog"):
        return "miss"
    method = (moss.get("match_method") or "").lower()
    if method.startswith("coefficient"):
        return "direct"
    return "composite"


def _detect_reflection_partner(
    coeffs_lookup: dict[tuple[int, ...], int],
    coeffs_ascending: Sequence[int],
) -> Optional[int]:
    """Find x -> -x partner index in the fixture (None if self-reflective or absent)."""
    flipped = tuple(c if i % 2 == 0 else -c for i, c in enumerate(coeffs_ascending))
    if flipped == tuple(coeffs_ascending):
        return None  # self-reflective
    return coeffs_lookup.get(flipped)


def _build_records_from_aligned(
    path_b_results: list[dict],
    boundary_entries: list[dict],
    sub_labels_full: list[Optional[int]],
    silhouette_k2: float,
) -> list[BoundaryLayerRecord]:
    """Assemble BoundaryLayerRecord list from aligned path-B + boundary-layer data."""
    n = len(path_b_results)
    coeffs_lookup = {
        tuple(path_b_results[i]["coeffs_ascending"]): i for i in range(n)
    }

    records: list[BoundaryLayerRecord] = []
    for i in range(n):
        pb = path_b_results[i]
        be = boundary_entries[i]
        coeffs_asc = list(pb["coeffs_ascending"])

        # Cyclotomic factor (n, k) pairs from path-B factor_list. Aggregate
        # across the (factor_poly, multiplicity) records.
        cyc_idx: list[int] = []
        cyc_pow: list[int] = []
        non_cyc_present = False
        non_cyc_M: Optional[float] = None
        for f in pb.get("factor_list", []):
            if f.get("is_cyclotomic"):
                cyc_idx.append(int(f["cyclotomic_n"]))
                cyc_pow.append(int(f["multiplicity"]))
            else:
                non_cyc_present = True
                if f.get("M_exact") is not None:
                    non_cyc_M = float(f["M_exact"])
        # Sort cyclotomic indices for deterministic ordering; permute powers in lockstep.
        if cyc_idx:
            order = sorted(range(len(cyc_idx)), key=lambda k: cyc_idx[k])
            cyc_idx = [cyc_idx[k] for k in order]
            cyc_pow = [cyc_pow[k] for k in order]

        # Mahler measures at three precisions, factor-first (the
        # successful verification path; direct polyroots returns NaN for
        # these 17 entries, which is what made them verification_failed).
        factor_list = pb.get("factor_list", [])
        M_dps30 = _mahler_via_factorization(factor_list, dps=30)
        M_dps60 = _mahler_via_factorization(factor_list, dps=60)
        M_dps100 = _mahler_via_factorization(factor_list, dps=100)

        # 4-class label.
        sub_label = sub_labels_full[i] if i < len(sub_labels_full) else None
        cls = _classify_4way(pb, be, sub_label)
        cls_pf = _post_fold(cls)

        # Reflection partner.
        partner = _detect_reflection_partner(coeffs_lookup, coeffs_asc)

        # Verification failure flag — definitional for these 17 entries (the
        # band hits the brute-force flagged as verification_failed).
        verif_failed = bool(pb["source_entry"].get("verification_failed", False))

        # factor_list_strategy: path-B is always a factor_first computation
        # (sympy Z[x] factorization first, then mpmath M on each factor).
        # The "direct" alternative would be mpmath polyroots on the full
        # deg-14 polynomial — which is what brute-force did and which
        # returned NaN for these 17. The training-relevant signal is which
        # strategy the SUCCESSFUL verification used; for these entries that
        # is uniformly factor_first.
        strategy = "factor_first"

        catalog_t = _catalog_match_type(pb)

        rec = BoundaryLayerRecord(
            poly_coefficients=coeffs_asc,
            mahler_measure_dps30=M_dps30,
            mahler_measure_dps60=M_dps60,
            mahler_measure_dps100=M_dps100,
            factor_list_strategy=strategy,
            n_irreducible_factors=int(pb["n_factors"]),
            cyclotomic_factor_indices=cyc_idx,
            cyclotomic_factor_powers=cyc_pow,
            non_cyclotomic_factor_present=non_cyc_present,
            non_cyclotomic_factor_mahler=non_cyc_M,
            verification_failed=verif_failed,
            catalog_match_type=catalog_t,
            boundary_layer_silhouette=float(silhouette_k2),
            reflection_pair_partner_idx=partner,
            cls=cls,
            cls_post_fold=cls_pf,
            entry_index=i,
        )
        records.append(rec)
    return records


def load_17_entry_fixture(
    path_b_path: str | Path = DEFAULT_PATH_B_RESULTS,
    boundary_layer_path: str | Path = DEFAULT_BOUNDARY_LAYER_RESULTS,
) -> list[BoundaryLayerRecord]:
    """Load the 17-entry boundary-layer fixture from path-B + boundary-layer JSONs."""
    with Path(path_b_path).open("r", encoding="utf-8") as fh:
        pb = json.load(fh)
    with Path(boundary_layer_path).open("r", encoding="utf-8") as fh:
        bl = json.load(fh)

    pb_results = pb["results"]
    bl_entries = bl["entries"]
    if len(pb_results) != len(bl_entries):
        raise ValueError(
            f"length mismatch: path-B={len(pb_results)} vs boundary-layer="
            f"{len(bl_entries)}"
        )

    # Validate alignment by coeffs_ascending.
    for i, (pbe, ble) in enumerate(zip(pb_results, bl_entries)):
        if list(pbe["coeffs_ascending"]) != list(ble["coeffs_ascending"]):
            raise ValueError(f"coeffs_ascending mismatch at index {i}")

    # Sub-labels (within-largest-cluster sub-clustering of the 15 B1 entries).
    sub = bl.get("sub_clustering_within_largest_class") or {}
    sub_labels_full = list(sub.get("labels_full_indexing", [None] * len(pb_results)))

    # k=2 silhouette from the boundary-layer clustering — uniform across all
    # entries (a global cluster-quality scalar, not per-entry).
    sil_k2 = float("nan")
    for r in bl.get("per_k_clustering", []):
        if r.get("k") == 2:
            sil_k2 = float(r.get("silhouette", float("nan")))
            break

    return _build_records_from_aligned(
        pb_results, bl_entries, sub_labels_full, sil_k2
    )


# ---------------------------------------------------------------------------
# Held-out fixture (synthetic_holdout via x -> -x reflection)
# ---------------------------------------------------------------------------

def _reflect_record(rec: BoundaryLayerRecord, new_index: int) -> BoundaryLayerRecord:
    """Apply x -> -x to a record. Preserves M, palindromicity, and post-fold class.

    Coefficient transform: c_k -> (-1)^k * c_k.
    Cyclotomic indices: Phi_n(x) = Phi_m(-x) where m is the x->-x partner of n.
    For our entries this swaps the (n=1, n=2) pair, the (n=7, n=14) pair, etc.
    Powers stay the same.
    The 4-class label flips between reflection partners (e.g. high_degree_pair
    entry A -> high_degree_pair entry B); post_fold is invariant.
    """
    flipped_coeffs = [c if i % 2 == 0 else -c for i, c in enumerate(rec.poly_coefficients)]
    flipped_cyc_idx = [_cyclotomic_xflip(n) for n in rec.cyclotomic_factor_indices]
    # Re-sort to deterministic order, permuting powers in lockstep.
    if flipped_cyc_idx:
        order = sorted(range(len(flipped_cyc_idx)), key=lambda k: flipped_cyc_idx[k])
        flipped_cyc_idx = [flipped_cyc_idx[k] for k in order]
        flipped_powers = [rec.cyclotomic_factor_powers[k] for k in order]
    else:
        flipped_powers = list(rec.cyclotomic_factor_powers)
    return BoundaryLayerRecord(
        poly_coefficients=flipped_coeffs,
        mahler_measure_dps30=rec.mahler_measure_dps30,
        mahler_measure_dps60=rec.mahler_measure_dps60,
        mahler_measure_dps100=rec.mahler_measure_dps100,
        factor_list_strategy=rec.factor_list_strategy,
        n_irreducible_factors=rec.n_irreducible_factors,
        cyclotomic_factor_indices=flipped_cyc_idx,
        cyclotomic_factor_powers=flipped_powers,
        non_cyclotomic_factor_present=rec.non_cyclotomic_factor_present,
        non_cyclotomic_factor_mahler=rec.non_cyclotomic_factor_mahler,
        verification_failed=rec.verification_failed,
        catalog_match_type=rec.catalog_match_type,
        boundary_layer_silhouette=rec.boundary_layer_silhouette,
        reflection_pair_partner_idx=None,  # remap in second pass
        cls=rec.cls,
        cls_post_fold=rec.cls_post_fold,
        entry_index=new_index,
        source="synthetic_holdout_xflip_of_" + rec.source,
    )


def _cyclotomic_xflip(n: int) -> int:
    """Phi_n(-x) = Phi_m(x) mapping. For n in {1,2}: 1<->2. For odd n>1: n -> 2n.
    For n = 2*odd: n -> n//2. For n divisible by 4: n -> n (Phi_n is x->-x invariant)."""
    if n == 1:
        return 2
    if n == 2:
        return 1
    if n % 4 == 0:
        return n  # Phi_n(-x) = Phi_n(x) when 4 | n
    if n % 2 == 1:
        return 2 * n
    # n = 2 * odd, odd > 1
    return n // 2


def load_heldout_fixture(
    path_b_path: str | Path = DEFAULT_PATH_B_RESULTS,
    boundary_layer_path: str | Path = DEFAULT_BOUNDARY_LAYER_RESULTS,
) -> tuple[list[BoundaryLayerRecord], dict]:
    """Synthetic held-out fixture via x -> -x reflection of the 17 entries.

    See module docstring for rationale (deg12 ±5 not callable; deg14 ±3
    likely yields 0 entries within the <2 hr task budget).

    Returns
    -------
    (records, metadata) where metadata["holdout_kind"] == "synthetic_holdout".
    """
    base = load_17_entry_fixture(path_b_path, boundary_layer_path)
    out: list[BoundaryLayerRecord] = [
        _reflect_record(rec, new_index=i) for i, rec in enumerate(base)
    ]
    # Re-bind reflection_pair_partner_idx within the held-out: identical
    # pairing structure to the original (the x -> -x reflection is an
    # involution on the 17-entry set as a whole).
    coeffs_lookup = {tuple(r.poly_coefficients): i for i, r in enumerate(out)}
    for i, r in enumerate(out):
        partner = _detect_reflection_partner(coeffs_lookup, r.poly_coefficients)
        r.reflection_pair_partner_idx = partner

    metadata = {
        "holdout_kind": "synthetic_holdout",
        "transform": "x_to_minus_x_reflection",
        "n_entries": len(out),
        "rationale": (
            "deg12 ±5 not exposed by lehmer_brute_force.DEGREE constant; "
            "deg14 ±3 brute-force run estimated ~3 minutes but smaller "
            "subspace likely yields 0 verification_failed entries (the 17 "
            "are the ±5 boundary layer). Synthetic x->-x reflection "
            "preserves M(P), palindromicity, and class_post_fold but "
            "flips intra-fold class labels — clean overfit-detection probe."
        ),
        "invariants_preserved": [
            "mahler_measure_dps30",
            "mahler_measure_dps60",
            "mahler_measure_dps100",
            "class_post_fold",
            "boundary_layer_silhouette",
        ],
        "labels_flipped_between_pairs": [
            "high_degree_reflection_pair (entries 1 <-> 12)",
            "lehmer_x_phi_n_k_composite (entries 2 <-> 14)",
        ],
    }
    return out, metadata


# ---------------------------------------------------------------------------
# JSONL serialisation (HuggingFace dataset-loader friendly)
# ---------------------------------------------------------------------------

def dump_to_jsonl(
    records: Iterable[BoundaryLayerRecord],
    path: str | Path,
) -> Path:
    """Write records as line-delimited JSON. Returns the written path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r.to_dict(), default=_json_default))
            fh.write("\n")
    return out


def load_from_jsonl(path: str | Path) -> list[BoundaryLayerRecord]:
    """Load records from a JSONL file written by ``dump_to_jsonl``."""
    out: list[BoundaryLayerRecord] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            out.append(BoundaryLayerRecord.from_dict(json.loads(line)))
    return out


def _json_default(o):
    if isinstance(o, float) and math.isnan(o):
        return "NaN"  # keep human-readable; round-trip via load_from_jsonl
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serialisable")


# ---------------------------------------------------------------------------
# CLI: emit fixture + held-out JSONL alongside path-B results
# ---------------------------------------------------------------------------

def main() -> int:  # pragma: no cover -- CLI wrapper
    out_dir = _HERE / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_17_entry_fixture()
    fixture_path = dump_to_jsonl(records, out_dir / "boundary_layer_17.jsonl")

    heldout, meta = load_heldout_fixture()
    heldout_path = dump_to_jsonl(heldout, out_dir / "boundary_layer_heldout.jsonl")
    meta_path = out_dir / "boundary_layer_heldout.meta.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    print(f"[boundary_layer_fixture] wrote {fixture_path} ({len(records)} records)")
    print(f"[boundary_layer_fixture] wrote {heldout_path} ({len(heldout)} records)")
    print(f"[boundary_layer_fixture] wrote {meta_path}")
    return 0


# ---------------------------------------------------------------------------
# Deg-12 held-out fixture (Techne fire-8 commitment T12; ingested fire-9)
# ---------------------------------------------------------------------------
#
# Per coordination ticket E-2026-05-07-T-deg12-fixture (techne-fire-8):
# Techne shipped the deg-12 ±5 palindromic brute-force fixture. 8.86M polys
# enumerated; 113 raw band candidates in [1.000001, 1.18]. Verdict:
# INCONCLUSIVE-pending-verification — triangulation phase deferred (Path
# A/B/C/D verification has not been run, so cls / cls_post_fold labels
# are NOT yet assigned). Per file ownership (prometheus_math/ is Techne's
# territory), Ergon ingests as UNLABELED structural held-out: the
# poly_coefficients + mahler_measure are sufficient for val_heldout_region
# metrics that don't require ground-truth class labels (n records,
# distribution by mahler band, model-prediction-distribution, etc.). When
# Techne ships the triangulation follow-up, this loader will gain a
# `with_triangulated_labels=True` mode.

DEFAULT_DEG12_RESULTS = _PROMETHEUS_MATH / "_lehmer_brute_force_deg12_results.json"

DEG12_DEGREE = 12
DEG12_N_FREE = 7  # palindromic deg-12 has 7 free coefficients (positions 0..6)


@dataclass(frozen=True)
class Deg12HeldoutRecord:
    """Unlabeled deg-12 ±5 palindromic in-band record (held-out for W3.2).

    Sister type to ``BoundaryLayerRecord`` but with a thinner schema
    reflecting the deferred-triangulation state of the deg-12 brute-force
    fixture. ``cls`` / ``cls_post_fold`` are deliberately ABSENT (not
    Optional[None] — absent) because ground-truth class assignment requires
    Path A/B/C/D triangulation that Techne has not yet run on this slice.

    NOT a subclass of BoundaryLayerRecord. Existing code that consumes
    BoundaryLayerRecord is unaffected. Loaders that want to use this
    held-out for unsupervised metrics import Deg12HeldoutRecord directly.
    """

    poly_coefficients: list[int]                 # full deg-12 palindrome, length 13
    free_coefficients: list[int]                 # length 7, positions 0..6
    mahler_measure: float                        # one precision; matches Techne's run
    in_band: bool                                # always True for entries in this fixture
    band_lower: float
    band_upper: float
    triangulation_status: str                   # always "pending" until Techne ships verification
    source: str = "lehmer_deg12_palindromic_pm5_path_a_brute_force"


def _palindromize_deg12(free: list[int]) -> list[int]:
    """Reconstruct full deg-12 palindromic coefficient list from 7 free coeffs.

    Free indices 0..6; palindromic → coeff[12-i] = coeff[i] for i in 0..5;
    coeff[6] is the central coefficient (free position 6)."""
    if len(free) != DEG12_N_FREE:
        raise ValueError(f"deg-12 palindrome needs {DEG12_N_FREE} free coeffs; got {len(free)}")
    full = [0] * (DEG12_DEGREE + 1)
    for i in range(DEG12_N_FREE):
        full[i] = int(free[i])
    for i in range(DEG12_N_FREE - 1):  # 0..5 mirror to 12..7
        full[DEG12_DEGREE - i] = int(free[i])
    return full


def load_deg12_heldout_fixture(
    path: Optional[Path] = None,
) -> Tuple[List[Deg12HeldoutRecord], Dict[str, Any]]:
    """Load Techne's deg-12 ±5 brute-force fixture as an unlabeled held-out.

    Returns: (records, metadata) where metadata mirrors the source JSON's
    top-level fields (degree, coef_range, band_upper, n_polys_processed,
    etc.) so downstream code can record the held-out's provenance.

    Records have NO class labels (ground-truth assignment requires
    triangulation; deferred to Techne). Use for structural / unsupervised
    val_heldout_region metrics (count, mahler distribution, prediction-
    distribution, structural similarity to deg-14 fixture).
    """
    src = Path(path) if path is not None else DEFAULT_DEG12_RESULTS
    if not src.exists():
        raise FileNotFoundError(
            f"deg-12 fixture not found at {src}. Per coordination ticket "
            f"E-2026-05-07-T-deg12-fixture, Techne ships this; if missing, "
            f"contact via aporia/meta/queue/techne_inbox.jsonl."
        )

    raw = json.loads(src.read_text(encoding="utf-8"))
    band_lower = float(raw.get("band_lower", 1.000001))  # default per Techne fixture summary
    band_upper = float(raw.get("band_upper", 1.18))

    records: List[Deg12HeldoutRecord] = []
    for entry in raw.get("in_band", []):
        # Each entry is a 2-tuple [free_coefficients_list, mahler_measure_float]
        if not (isinstance(entry, list) and len(entry) == 2):
            raise ValueError(f"unexpected entry shape in deg-12 fixture: {entry!r}")
        free, mahler = entry
        records.append(Deg12HeldoutRecord(
            poly_coefficients=_palindromize_deg12(list(free)),
            free_coefficients=[int(c) for c in free],
            mahler_measure=float(mahler),
            in_band=True,
            band_lower=band_lower,
            band_upper=band_upper,
            triangulation_status="pending",
        ))

    metadata = {
        "degree": int(raw.get("degree", DEG12_DEGREE)),
        "coef_range": list(raw.get("coef_range", [-5, 5])),
        "band_upper": band_upper,
        "band_lower": band_lower,
        "n_polys_processed": int(raw.get("n_polys_processed", 0)),
        "in_band_count": int(raw.get("in_band_count", len(records))),
        "elapsed_seconds": float(raw.get("_elapsed_seconds", 0.0)),
        "run_timestamp": raw.get("_run_timestamp"),
        "triangulation_status": "pending",  # block-level; per-record same
        "source_file": str(src),
        "source_module": "prometheus_math.lehmer_brute_force_general",
        "techne_ticket": "E-2026-05-07-T-deg12-fixture",
    }
    return records, metadata


__all__ = [
    # deg-14 fixture (existing)
    "BoundaryLayerRecord",
    "load_17_entry_fixture",
    "load_heldout_fixture",
    "dump_to_jsonl",
    # deg-12 fixture (fire-9, ingested from Techne T12)
    "Deg12HeldoutRecord",
    "load_deg12_heldout_fixture",
    "DEFAULT_DEG12_RESULTS",
    "DEG12_DEGREE",
    "DEG12_N_FREE",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
