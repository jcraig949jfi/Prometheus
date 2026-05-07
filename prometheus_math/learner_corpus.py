"""prometheus_math.learner_corpus — P5 NearMissCorpus interface stub.

Pre-Tier-0 deliverable for joint sprint sync point S1 (see
``pivot/techne_ergon_joint_sprint_2026-05-05.md``). This module is the
*interface stub* — the real triangulated emission lands at Tier 2 (Day 13
of joint sprint) when P4 ExclusionCertificate + P6 TriangulationProtocol
are in place. The stub:

  * Pins the schema (CorpusEmission with three views: pre_falsification,
    post_falsification, provenance) — Ergon's Pipeline-D scaffolds
    against the schema starting Day 1.
  * Implements the loader API with anti-leakage flag enforcement.
  * Provides ``stub_emit_from_legacy_ledger()`` that synthesises a
    minimal CorpusEmission from existing kernel-ledger / promotion-ledger
    records so Pipeline-D has *something* to consume during Days 1-12.
  * Real ``emit_from_substrate()`` is stubbed (raises NotImplementedError
    pointing at Tier 2 P5 work) — this is intentional so Ergon does not
    accidentally train on stub data thinking it is real triangulated
    emission.

Anti-leakage discipline (load-bearing per ChatGPT + Gemini convergence)
----------------------------------------------------------------------
``pre_falsification_view`` and ``post_falsification_view`` write to
*different file paths* and are loaded via *different loader methods*.
The default ``LearnerCorpusLoader.load()`` returns pre-view only;
loading post-view as a predictive feature requires
``allow_post_falsification=True`` AND emits a logged leakage-event row
to the substrate. This is enforcement, not convention. The Day-4 lesson
(modal-class collapse caught by synthetic null on cross-domain envs) is
the precedent; this primitive applies the same discipline at the
training-data interface.

Per-domain raw-invariant feature lists
--------------------------------------
For each cross-domain env, ``pre_falsification_view.raw_invariants`` is
populated from a registered per-domain feature list (see
``RAW_INVARIANTS_PER_DOMAIN``). Lehmer's list comes from Ergon's Q-E2
answer (poly_coefficients, mahler_measure_dps30/60/100, factor
structure, etc.); other domains pin their lists in v1.0 work.

Forward references
------------------
Several fields reference primitives that ship later in v2.3:
  * ``coordinate_chart_id`` — populated only after P0 lands (Day 3-4);
    until then, stub uses ``"provisional:<env_name>"``.
  * ``method_spec`` — populated only after P3 lands (Day 5); until
    then, stub uses a minimal MethodSpec dict shape.
  * ``triangulation_path`` — populated only after P6 lands (Day 8-12);
    until then, stub records ``"untriangulated:stub"``.
  * ``exclusion_certificate_ref`` — populated only after P4 lands; until
    then, stub omits this field.

These deferred fields are documented in each dataclass with a
``# DEFERRED:`` marker. The schema is forward-compatible — when the
real emission lands at Day 13, the same loader API consumes the
upgraded data without Pipeline-D rework.
"""
from __future__ import annotations

import enum
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Schema version + paths
# ---------------------------------------------------------------------------


SCHEMA_VERSION = "v2.3-stub"
"""Version tag emitted into every CorpusEmission so consumers can detect
the stub-vs-real upgrade at Day 13. Real emission bumps to ``v2.3``."""


PRE_VIEW_DIRNAME = "pre_falsification"
POST_VIEW_DIRNAME = "post_falsification"
PROVENANCE_VIEW_DIRNAME = "provenance"
LEAKAGE_LOG_FILENAME = "_post_view_load_events.jsonl"


# ---------------------------------------------------------------------------
# Per-domain raw-invariant feature registry (Q-E2 from Ergon)
# ---------------------------------------------------------------------------


# Lehmer feature list pinned by Ergon's Q-E2 answer (joint sprint S9).
# Other domains' lists are pinned in v1.0 work; for now they default to
# a minimal stub list ("coeffs", "label", "magnitude") that the env's
# observation already exposes.
RAW_INVARIANTS_PER_DOMAIN: Dict[str, Tuple[str, ...]] = {
    "lehmer": (
        "poly_coefficients",
        "mahler_measure_dps30",
        "mahler_measure_dps60",
        "mahler_measure_dps100",
        "height",
        "lead_coefficient",
        "palindromicity_check",
        "n_irreducible_factors",
        "cyclotomic_factor_indices",
        "cyclotomic_factor_powers",
        "non_cyclotomic_factor_present",
        "non_cyclotomic_factor_mahler",
        "reflection_pair_partner_hash",
    ),
    # Cross-domain envs default to a minimal stub list; v1.0 pins them.
    "bsd_rank": ("cremona_label", "conductor", "j_invariant", "torsion_structure", "ap_sequence"),
    "modular_form": ("level", "weight", "character", "q_expansion_prefix"),
    "knot_trace_field": ("pd_code", "crossing_number", "signature", "alexander_coefficients"),
    "genus2": ("igusa_invariants", "conductor", "automorphism_group"),
    "oeis_sleeping": ("oeis_id", "first_n_terms", "oeis_keywords", "conjectured_gf"),
    "mock_theta": ("level", "weight", "shadow_form_ref", "modular_completion_method"),
    # OBSTRUCTION_SHAPE deferred to Charon coordination (joint sprint Q-C1).
    "obstruction_shape": ("__deferred_to_charon__",),
}


def get_raw_invariant_keys(domain: str) -> Tuple[str, ...]:
    """Return the registered raw-invariant feature list for a domain.

    Raises ``KeyError`` on unregistered domain. Substrate discipline is
    loud-fail-on-typo, not silent-degradation: a typo
    (``"bsd-rank"`` instead of ``"bsd_rank"``) used to silently return
    ``("__unregistered__",)`` and propagate as all-None ``raw_invariants``
    in downstream emission. The contract was inverted in the
    2026-05-07 contract-change window per T-2026-05-06-ST003 +
    T-2026-05-07-T018 audit.

    Callers who need an Optional-style behavior can wrap with
    ``RAW_INVARIANTS_PER_DOMAIN.get(domain)`` directly (the registry is
    a public module attribute).
    """
    try:
        return RAW_INVARIANTS_PER_DOMAIN[domain]
    except KeyError:
        raise KeyError(
            f"unregistered domain {domain!r}; registered: "
            f"{sorted(RAW_INVARIANTS_PER_DOMAIN)}"
        ) from None


# ---------------------------------------------------------------------------
# View dataclasses (the schema)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObjectFeatures:
    """The mathematical object's features computed BEFORE any falsifier
    touches it. This is what the Learner trains on by default.

    Anti-leakage discipline: anything in this dataclass must be
    derivable from the object's identity / canonical form alone — never
    from kill outcomes, triangulation results, or post-falsification
    margins.
    """

    domain: str
    canonical_form: Any  # JSON-serialisable canonical representation
    raw_invariants: Mapping[str, Any]  # keyed by RAW_INVARIANTS_PER_DOMAIN[domain]
    coordinate_chart_id: str  # "provisional:<env>" until P0 lands Day 3-4
    neighbors_in_chart: Tuple[str, ...] = ()  # same-cluster sibling object_ids


@dataclass(frozen=True)
class PreFalsificationView:
    """Primary Learner training input.

    Contains ONLY object features computed before any falsifier ran.
    Loaded by default via ``LearnerCorpusLoader.load()``.
    """

    object_id: str  # content-addressed hash of canonical_form
    object: ObjectFeatures


@dataclass(frozen=True)
class PostFalsificationView:
    """Gated explanation/calibration view.

    Contains kill outcomes, triangulation paths, method specs, caveats.
    Loaded ONLY via ``LearnerCorpusLoader.load_post_view(allow_post_falsification=True)``;
    every load is logged as a potential leakage event.
    """

    object_id: str  # MUST match the corresponding PreFalsificationView.object_id
    kill_vector: Optional[Mapping[str, Any]] = None  # KillVector.to_dict() shape
    evidence_field: Optional[Mapping[str, Any]] = None  # DEFERRED: P1 EvidenceField (Day 6-7)
    triangulation_path: str = "untriangulated:stub"  # DEFERRED: P6 (Day 8-12)
    method_spec: Optional[Mapping[str, Any]] = None  # DEFERRED: P3 MethodSpec (Day 5)
    caveats: Tuple[str, ...] = ()
    exclusion_certificate_ref: Optional[str] = None  # DEFERRED: P4 (Day 8-12)


@dataclass(frozen=True)
class ProvenanceView:
    """Audit trail for label sourcing, falsifier versions, and known
    artifact flags. Used by Ergon for label-version tracking and
    held-out-time split construction; never used as a predictive input.
    """

    object_id: str
    label_source: str  # e.g. "discovery_pipeline:v1.5", "lehmer_brute_force_path_b"
    label_time: float  # unix epoch when the label was computed
    label_version: str
    label_strength: str = "candidate"  # "candidate" | "robust" | "promoted" | "rejected"
    falsifier_versions: Mapping[str, str] = field(default_factory=dict)
    operator_that_generated_candidate: str = ""
    synthetic_null_family: Optional[str] = None  # set on synthetic-null records
    known_artifact_flags: Tuple[str, ...] = ()
    possible_future_positive_flag: bool = False  # near-miss this iteration; might promote later


# ---------------------------------------------------------------------------
# Triple shapes (both rank-loss and triplet-loss ready, per Q-E1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RankLossTriple:
    """``(positive, near_miss, negative)`` — for rank-loss training where
    near_miss is between positive and negative on a scalar (e.g., KillVector
    margin distance).
    """

    positive_id: str
    near_miss_id: str
    negative_id: str
    near_miss_kind: str  # "boundary" | "method" | "structural" | "random_hard" | "adversarial"


@dataclass(frozen=True)
class TripletLossTriple:
    """``(anchor, positive, hard_negative)`` — for triplet-loss training
    where hard_negative differs from positive on a specific dimension
    (e.g., categorical class boundary).
    """

    anchor_id: str
    positive_id: str
    hard_negative_id: str
    margin_dimension: str  # which dimension separates positive from hard_negative


# ---------------------------------------------------------------------------
# Splits (canonical, leakage-safe defaults)
# ---------------------------------------------------------------------------


class SplitName(str, enum.Enum):
    TRAIN = "train"
    VAL_SAME_REGION = "validation_same_region"
    VAL_HELDOUT_REGION = "validation_heldout_region"
    VAL_HELDOUT_METHOD = "validation_heldout_method"
    VAL_LATER_TIME = "validation_later_time"
    SYNTHETIC_NULL = "synthetic_null"


@dataclass(frozen=True)
class Splits:
    """Canonical splits per emission. Object_ids per split.

    val_later_time is the temporal split (train on earlier substrate
    records, validate on later) — confirms the Learner does not exploit
    batch artifacts. Per Ergon's Q-E4 confirmation.
    """

    train: Tuple[str, ...] = ()
    validation_same_region: Tuple[str, ...] = ()
    validation_heldout_region: Tuple[str, ...] = ()
    validation_heldout_method: Tuple[str, ...] = ()
    validation_later_time: Tuple[str, ...] = ()
    synthetic_null: Tuple[str, ...] = ()

    def get(self, name: SplitName) -> Tuple[str, ...]:
        return getattr(self, name.value)

    def all_object_ids(self) -> Tuple[str, ...]:
        seen: List[str] = []
        s: set = set()
        for split in (
            self.train,
            self.validation_same_region,
            self.validation_heldout_region,
            self.validation_heldout_method,
            self.validation_later_time,
            self.synthetic_null,
        ):
            for oid in split:
                if oid not in s:
                    s.add(oid)
                    seen.append(oid)
        return tuple(seen)


# ---------------------------------------------------------------------------
# CorpusEmission (the top-level artifact)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CorpusEmission:
    """One emission of the NearMissCorpus.

    The three views are stored as parallel lists keyed on object_id;
    the loader reconstructs (object_id -> view) maps on read.

    Triples + splits reference object_ids; the loader resolves them to
    full views on demand.
    """

    schema_version: str
    emission_id: str  # content-addressed hash of (region_key, label_version, label_time)
    region_key: str
    label_version: str
    emitted_at: float

    pre_views: Tuple[PreFalsificationView, ...]
    post_views: Tuple[PostFalsificationView, ...]
    provenance_views: Tuple[ProvenanceView, ...]

    rank_triples: Tuple[RankLossTriple, ...] = ()
    triplet_triples: Tuple[TripletLossTriple, ...] = ()

    splits: Splits = field(default_factory=Splits)

    @property
    def object_ids(self) -> Tuple[str, ...]:
        return tuple(v.object_id for v in self.pre_views)


# ---------------------------------------------------------------------------
# Emitter — stub from legacy ledger
# ---------------------------------------------------------------------------


def _content_hash(obj: Any) -> str:
    """SHA-256 of canonical JSON serialisation. Used for object_id and
    emission_id."""
    canonical = json.dumps(obj, sort_keys=True, default=repr)
    return hashlib.sha256(canonical.encode()).hexdigest()


def stub_emit_from_legacy_ledger(
    legacy_records: Sequence[Mapping[str, Any]],
    *,
    region_key: str,
    label_version: str,
    domain: str = "lehmer",
    output_root: Optional[Path] = None,
) -> CorpusEmission:
    """Synthesise a minimal CorpusEmission from existing kernel-ledger /
    promotion-ledger records.

    This is the *stub* emitter that lives here during Days 1-12 of the
    joint sprint. Real triangulated emission ships at Day 13 via
    ``emit_from_substrate()`` (currently NotImplementedError).

    The stub:
      * Reads each legacy record
      * Splits each record's content into pre / post / provenance views
      * Generates object_ids by content-hashing the pre-view object
      * Does NOT generate triples (real triple generation requires
        boundary-layer clustering from P5 proper) — emits empty triples
      * Generates a degenerate split: all records in train (Ergon
        overrides this for tire-kick experiments)

    Parameters
    ----------
    legacy_records : sequence of mapping
        Records from a promotion ledger or kernel ledger. Each record
        should contain at least: ``raw_invariants`` (dict) or per-domain
        equivalents; ``kill_vector`` (optional, KillVector.to_dict
        shape); ``operator_class`` (optional); ``timestamp`` (optional).
    region_key : str
        e.g. ``"lehmer:deg14:pm5:palindromic"``.
    label_version : str
        e.g. ``"discovery_pipeline:v1.5"``.
    domain : str, default "lehmer"
        Used to look up ``RAW_INVARIANTS_PER_DOMAIN[domain]``.
    output_root : optional Path
        If provided, the emission is *also* written to disk under
        ``output_root/<emission_id>/`` with subdirs for pre / post /
        provenance views. If None, the emission is returned in-memory
        only (useful for tests).

    Returns
    -------
    CorpusEmission
    """
    raw_invariant_keys = get_raw_invariant_keys(domain)
    chart_id = f"provisional:{domain}"  # P0 chart not yet registered

    pre_views: List[PreFalsificationView] = []
    post_views: List[PostFalsificationView] = []
    provenance_views: List[ProvenanceView] = []

    for rec in legacy_records:
        # Build object features from the record's pre-falsification fields.
        raw_invariants_dict: Dict[str, Any] = {}
        for k in raw_invariant_keys:
            if k in rec:
                raw_invariants_dict[k] = rec[k]
            elif "raw_invariants" in rec and isinstance(rec["raw_invariants"], dict):
                raw_invariants_dict[k] = rec["raw_invariants"].get(k)
            else:
                raw_invariants_dict[k] = None

        canonical = rec.get("canonical_form") or rec.get("coeffs") or rec.get("label")
        obj = ObjectFeatures(
            domain=domain,
            canonical_form=canonical,
            raw_invariants=raw_invariants_dict,
            coordinate_chart_id=chart_id,
            neighbors_in_chart=tuple(rec.get("neighbors_in_chart", ())),
        )

        object_id = _content_hash(
            {"canonical_form": canonical, "raw_invariants": raw_invariants_dict}
        )

        pre_views.append(PreFalsificationView(object_id=object_id, object=obj))

        post_views.append(
            PostFalsificationView(
                object_id=object_id,
                kill_vector=rec.get("kill_vector"),
                caveats=tuple(rec.get("caveats", ())),
                # All other DEFERRED fields stay at default (None / "stub").
            )
        )

        provenance_views.append(
            ProvenanceView(
                object_id=object_id,
                label_source=rec.get("label_source", "stub:legacy_ledger"),
                label_time=float(rec.get("timestamp", time.time())),
                label_version=label_version,
                label_strength=rec.get("label_strength", "candidate"),
                operator_that_generated_candidate=rec.get("operator_class", ""),
            )
        )

    emission_id = _content_hash(
        {"region_key": region_key, "label_version": label_version, "n_records": len(legacy_records)}
    )

    splits = Splits(train=tuple(v.object_id for v in pre_views))

    emission = CorpusEmission(
        schema_version=SCHEMA_VERSION,
        emission_id=emission_id,
        region_key=region_key,
        label_version=label_version,
        emitted_at=time.time(),
        pre_views=tuple(pre_views),
        post_views=tuple(post_views),
        provenance_views=tuple(provenance_views),
        rank_triples=(),  # stub: no triple generation
        triplet_triples=(),  # stub: no triple generation
        splits=splits,
    )

    if output_root is not None:
        write_emission_to_disk(emission, output_root)

    return emission


def emit_from_substrate(
    typed_records: Sequence[Mapping[str, Any]],
    *,
    region_key: str,
    label_version: str,
    domain: str,
    coordinate_chart_id: Optional[str] = None,
    output_root: Optional[Path] = None,
    n_synthetic_null_per_record: int = 1,
    triple_neighborhood_size: int = 3,
    split_seed: int = 0,
    holdout_method_independence_class: Optional[str] = None,
) -> CorpusEmission:
    """Real triangulated P5 emission (replaces the Day 1-2 stub).

    Schema version bumps to ``v2.3`` (no longer stub). Consumes typed
    records that carry the full upstream substrate primitives:

      * KillVector v2 (+8 components per Aporia Study 02)
      * MethodSpec (P3, structured engine/strategy/independence_class/drift_channel)
      * EvidenceField (P1, 6 factual axes; PolicyField is separate)
      * Optional ExclusionCertificate ref (P4, only complete/bounded_complete feed exclusion_distance axis)
      * Optional TriangulationPath info (P6, INCONCLUSIVE upgrades require ≥1 proof-bearing path)

    The stub continues to exist for Days 1-12 callers; this function
    is the upgrade path for Day 13+.

    Parameters
    ----------
    typed_records : sequence of mapping
        Each record contains:
          - object features (raw_invariants per RAW_INVARIANTS_PER_DOMAIN[domain])
          - canonical_form
          - kill_vector (KillVector dict from KillVector v2)
          - evidence_field (EvidenceField dict — already built by caller, OR
            the function builds one from kill_vector + telemetry)
          - method_spec (MethodSpec dict from P3)
          - triangulation_path (P6 path id or path summary string)
          - exclusion_certificate_ref (P4 certificate_id; optional)
          - caveats (list[str])
          - operator_class
          - timestamp
          - label_strength (candidate / robust / promoted / rejected)
          - region_key (per-record; may differ from emission-level region_key
            for cross-region emissions)
    region_key : str
        Top-level region key for the emission (e.g., "lehmer:deg14:pm5:palindromic").
        Per-record region_key in typed_records may be a sub-region.
    label_version : str
        E.g. "discovery_pipeline:v2.3".
    domain : str
        Domain identifier; used to look up RAW_INVARIANTS_PER_DOMAIN[domain].
    coordinate_chart_id : optional str
        Default chart_id for records whose own chart_id is not specified.
        Pass the registered Lehmer chart id (or another P0 chart). For
        domains without registered charts, pass None and records get
        ``"provisional:<domain>"``.
    n_synthetic_null_per_record : int, default 1
        How many synthetic-null records to emit per real record. The
        nulls have shuffled labels (label_strength swapped randomly)
        and are flagged with ``synthetic_null_family``.
    triple_neighborhood_size : int, default 3
        How many same-neighborhood records to pull as triple candidates
        per anchor. Anti-trivial-separability per Gemini.
    split_seed : int, default 0
        Deterministic seed for canonical-split assignment. Same seed +
        same records → same splits.
    holdout_method_independence_class : optional str
        If set, records using a method with this independence_class are
        held out (val_heldout_method split). Otherwise the heldout-method
        split is empty.

    Returns
    -------
    CorpusEmission with schema_version='v2.3' (NOT stub).
    """
    import random

    if not typed_records:
        raise ValueError("typed_records cannot be empty for emit_from_substrate")

    raw_invariant_keys = get_raw_invariant_keys(domain)
    default_chart_id = coordinate_chart_id or f"provisional:{domain}"

    pre_views: List[PreFalsificationView] = []
    post_views: List[PostFalsificationView] = []
    provenance_views: List[ProvenanceView] = []
    record_metadata: List[Dict[str, Any]] = []  # for split + triple computation

    for rec in typed_records:
        # ---- Pre-falsification view (object features only) ----
        raw_invariants_dict: Dict[str, Any] = {}
        for k in raw_invariant_keys:
            if k in rec:
                raw_invariants_dict[k] = rec[k]
            elif "raw_invariants" in rec and isinstance(rec["raw_invariants"], dict):
                raw_invariants_dict[k] = rec["raw_invariants"].get(k)
            else:
                raw_invariants_dict[k] = None

        canonical = rec.get("canonical_form") or rec.get("coeffs") or rec.get("label")
        rec_chart = rec.get("coordinate_chart_id", default_chart_id)
        obj = ObjectFeatures(
            domain=domain,
            canonical_form=canonical,
            raw_invariants=raw_invariants_dict,
            coordinate_chart_id=rec_chart,
            neighbors_in_chart=tuple(rec.get("neighbors_in_chart", ())),
        )
        object_id = _content_hash(
            {"canonical_form": canonical, "raw_invariants": raw_invariants_dict}
        )
        pre_views.append(PreFalsificationView(object_id=object_id, object=obj))

        # ---- Post-falsification view (gated; uses ALL upstream primitives) ----
        kv = rec.get("kill_vector")
        ef = rec.get("evidence_field")
        ms = rec.get("method_spec")
        tp = rec.get("triangulation_path", "untriangulated")
        ec_ref = rec.get("exclusion_certificate_ref")
        post_views.append(
            PostFalsificationView(
                object_id=object_id,
                kill_vector=kv,
                evidence_field=ef,
                triangulation_path=tp,
                method_spec=ms,
                caveats=tuple(rec.get("caveats", ())),
                exclusion_certificate_ref=ec_ref,
            )
        )

        # ---- Provenance view (audit trail) ----
        provenance_views.append(
            ProvenanceView(
                object_id=object_id,
                label_source=rec.get("label_source", "substrate:emit_from_substrate"),
                label_time=float(rec.get("timestamp", time.time())),
                label_version=label_version,
                label_strength=rec.get("label_strength", "candidate"),
                falsifier_versions=dict(rec.get("falsifier_versions", {})),
                operator_that_generated_candidate=rec.get("operator_class", ""),
                synthetic_null_family=None,  # real records; nulls injected separately below
                known_artifact_flags=tuple(rec.get("known_artifact_flags", ())),
                possible_future_positive_flag=bool(rec.get("possible_future_positive_flag", False)),
            )
        )

        # ---- Track per-record metadata for split + triple computation ----
        record_metadata.append({
            "object_id": object_id,
            "region_key": rec.get("region_key", region_key),
            "method_independence_class": (ms or {}).get("independence_class") if isinstance(ms, dict) else None,
            "label_strength": rec.get("label_strength", "candidate"),
            "timestamp": float(rec.get("timestamp", time.time())),
            "neighbors_in_chart": tuple(rec.get("neighbors_in_chart", ())),
        })

    # ---- Synthetic-null pack (label-shuffled records) ----
    rng = random.Random(split_seed)
    synthetic_null_ids: List[str] = []
    if n_synthetic_null_per_record > 0:
        for src_meta, src_pre, src_post, src_prov in zip(
            list(record_metadata), list(pre_views), list(post_views), list(provenance_views)
        ):
            for k in range(n_synthetic_null_per_record):
                # Shuffle labels by drawing a random label_strength different from the source's.
                source_label = src_meta["label_strength"]
                shuffled_label = rng.choice(
                    [s for s in ("candidate", "robust", "promoted", "rejected") if s != source_label]
                )
                # Synthesize null object_id by hashing (source_id, k, shuffled_label).
                null_object_id = _content_hash({
                    "source": src_pre.object_id,
                    "synthetic_null_index": k,
                    "shuffled_label": shuffled_label,
                })
                # Pre-view re-uses the source's object features (the shuffle is on the LABEL, not the features).
                pre_views.append(PreFalsificationView(
                    object_id=null_object_id,
                    object=src_pre.object,
                ))
                # Post-view inherits but flagged.
                post_views.append(PostFalsificationView(
                    object_id=null_object_id,
                    kill_vector=src_post.kill_vector,
                    evidence_field=src_post.evidence_field,
                    triangulation_path=src_post.triangulation_path,
                    method_spec=src_post.method_spec,
                    caveats=tuple(list(src_post.caveats) + ["synthetic_null"]),
                    exclusion_certificate_ref=src_post.exclusion_certificate_ref,
                ))
                provenance_views.append(ProvenanceView(
                    object_id=null_object_id,
                    label_source="substrate:synthetic_null_shuffle",
                    label_time=src_prov.label_time,
                    label_version=label_version,
                    label_strength=shuffled_label,  # the shuffled (false) label
                    falsifier_versions=src_prov.falsifier_versions,
                    operator_that_generated_candidate=src_prov.operator_that_generated_candidate,
                    synthetic_null_family="label_shuffle_v1",
                    known_artifact_flags=tuple(list(src_prov.known_artifact_flags) + ["shuffled_label"]),
                    possible_future_positive_flag=False,
                ))
                synthetic_null_ids.append(null_object_id)

    # ---- Triple generation (anti-trivial-separability per Gemini) ----
    rank_triples, triplet_triples = _generate_triples(
        record_metadata=record_metadata,
        triple_neighborhood_size=triple_neighborhood_size,
        rng=rng,
    )

    # ---- Canonical splits ----
    splits = _build_canonical_splits(
        record_metadata=record_metadata,
        synthetic_null_ids=tuple(synthetic_null_ids),
        holdout_method_independence_class=holdout_method_independence_class,
        split_seed=split_seed,
        region_key=region_key,
    )

    emission_id = _content_hash({
        "region_key": region_key,
        "label_version": label_version,
        "n_records": len(typed_records),
        "n_synthetic_null": len(synthetic_null_ids),
        "schema": "v2.3",
    })

    emission = CorpusEmission(
        schema_version="v2.3",  # NO LONGER STUB
        emission_id=emission_id,
        region_key=region_key,
        label_version=label_version,
        emitted_at=time.time(),
        pre_views=tuple(pre_views),
        post_views=tuple(post_views),
        provenance_views=tuple(provenance_views),
        rank_triples=rank_triples,
        triplet_triples=triplet_triples,
        splits=splits,
    )

    if output_root is not None:
        write_emission_to_disk(emission, output_root)

    return emission


# ---------------------------------------------------------------------------
# Triple generation (anti-trivial-separability)
# ---------------------------------------------------------------------------


def _generate_triples(
    *,
    record_metadata: Sequence[Mapping[str, Any]],
    triple_neighborhood_size: int,
    rng: Any,
) -> Tuple[Tuple[RankLossTriple, ...], Tuple[TripletLossTriple, ...]]:
    """Generate anti-trivial-separability triples.

    For each anchor record:
      1. Find same-region "neighborhood" records (same region_key).
      2. Within neighborhood: pick a positive (different label_strength == "promoted" or "robust")
         and a negative (label_strength == "rejected") if available.
      3. If neighborhood is too small or lacks contrasts, skip this anchor's triple.

    Per Gemini's anti-trivial-separability rule: triples MUST be drawn
    from same coordinate-chart neighborhood. We use region_key as the
    proxy until ChartRegistry-aware neighbor lookup ships in v3.0.
    """
    rank_out: List[RankLossTriple] = []
    triplet_out: List[TripletLossTriple] = []

    # Group by region_key
    by_region: Dict[str, List[Mapping[str, Any]]] = {}
    for r in record_metadata:
        by_region.setdefault(r["region_key"], []).append(r)

    for region, records in by_region.items():
        if len(records) < 3:
            continue
        # For each anchor, find positive + negative within the same region.
        promoted = [r for r in records if r["label_strength"] in ("promoted", "robust")]
        rejected = [r for r in records if r["label_strength"] == "rejected"]
        candidates = [r for r in records if r["label_strength"] == "candidate"]
        if not promoted or not rejected:
            # Cannot form contrastive triples without polarised labels in this region.
            continue
        # Pair up anchors with positives and hard-negatives from candidates (near-misses).
        for anchor in promoted[:triple_neighborhood_size]:
            pos = rng.choice(promoted)
            neg = rng.choice(rejected)
            near_miss = rng.choice(candidates) if candidates else None
            if anchor["object_id"] == pos["object_id"]:
                continue
            triplet_out.append(TripletLossTriple(
                anchor_id=anchor["object_id"],
                positive_id=pos["object_id"],
                hard_negative_id=neg["object_id"],
                margin_dimension="label_strength",
            ))
            if near_miss is not None:
                rank_out.append(RankLossTriple(
                    positive_id=pos["object_id"],
                    near_miss_id=near_miss["object_id"],
                    negative_id=neg["object_id"],
                    near_miss_kind="structural",  # same region, candidate label
                ))
    return tuple(rank_out), tuple(triplet_out)


# ---------------------------------------------------------------------------
# Canonical splits
# ---------------------------------------------------------------------------


def _build_canonical_splits(
    *,
    record_metadata: Sequence[Mapping[str, Any]],
    synthetic_null_ids: Tuple[str, ...],
    holdout_method_independence_class: Optional[str],
    split_seed: int,
    region_key: str,
) -> Splits:
    """Deterministic canonical splits.

    Strategy:
      - synthetic_null: all the shuffled-label records
      - val_heldout_method: records whose method's independence_class == holdout (if set)
      - val_later_time: top 10% latest records (by timestamp) — temporal split
      - val_heldout_region: records with region_key != emission's region_key
      - val_same_region: 15% of remaining records, deterministically selected
      - train: the rest

    All sets are mutually exclusive; assignment cascades in the order above.
    """
    import hashlib

    def _det_bucket(object_id: str) -> int:
        """Deterministic bucket 0-99 from object_id."""
        h = hashlib.sha256((str(split_seed) + object_id).encode()).hexdigest()
        return int(h[:8], 16) % 100

    train: List[str] = []
    val_same_region: List[str] = []
    val_heldout_region: List[str] = []
    val_heldout_method: List[str] = []
    val_later_time: List[str] = []

    # Sort by timestamp to identify the temporal-holdout (latest 10%).
    sorted_records = sorted(record_metadata, key=lambda r: r["timestamp"])
    n_total = len(sorted_records)
    later_time_cutoff_idx = max(int(n_total * 0.9), n_total - 1) if n_total > 0 else 0
    later_time_ids = {r["object_id"] for r in sorted_records[later_time_cutoff_idx:]}

    for r in record_metadata:
        oid = r["object_id"]
        if oid in later_time_ids:
            val_later_time.append(oid)
            continue
        if (
            holdout_method_independence_class is not None
            and r.get("method_independence_class") == holdout_method_independence_class
        ):
            val_heldout_method.append(oid)
            continue
        if r["region_key"] != region_key:
            val_heldout_region.append(oid)
            continue
        bucket = _det_bucket(oid)
        if bucket < 15:  # ~15% to val_same_region
            val_same_region.append(oid)
        else:
            train.append(oid)

    return Splits(
        train=tuple(train),
        validation_same_region=tuple(val_same_region),
        validation_heldout_region=tuple(val_heldout_region),
        validation_heldout_method=tuple(val_heldout_method),
        validation_later_time=tuple(val_later_time),
        synthetic_null=tuple(synthetic_null_ids),
    )


# ---------------------------------------------------------------------------
# Disk layout + writer
# ---------------------------------------------------------------------------


def write_emission_to_disk(emission: CorpusEmission, output_root: Path) -> Path:
    """Write a CorpusEmission to disk under
    ``output_root / emission_id /``.

    Disk layout (anti-leakage by file separation):
        <emission_id>/
            metadata.json                  # schema_version, region_key, label_version, ...
            pre_falsification/
                <object_id>.json
                ...
            post_falsification/
                <object_id>.json
                ...
            provenance/
                <object_id>.json
                ...
            rank_triples.jsonl
            triplet_triples.jsonl
            splits.json
            _post_view_load_events.jsonl   # appended by loader on each post-view load
    """
    root = Path(output_root) / emission.emission_id
    (root / PRE_VIEW_DIRNAME).mkdir(parents=True, exist_ok=True)
    (root / POST_VIEW_DIRNAME).mkdir(parents=True, exist_ok=True)
    (root / PROVENANCE_VIEW_DIRNAME).mkdir(parents=True, exist_ok=True)

    meta = {
        "schema_version": emission.schema_version,
        "emission_id": emission.emission_id,
        "region_key": emission.region_key,
        "label_version": emission.label_version,
        "emitted_at": emission.emitted_at,
        "n_records": len(emission.pre_views),
    }
    (root / "metadata.json").write_text(json.dumps(meta, indent=2))

    for v in emission.pre_views:
        (root / PRE_VIEW_DIRNAME / f"{v.object_id}.json").write_text(
            json.dumps(asdict(v), indent=2, default=repr)
        )
    for v in emission.post_views:
        (root / POST_VIEW_DIRNAME / f"{v.object_id}.json").write_text(
            json.dumps(asdict(v), indent=2, default=repr)
        )
    for v in emission.provenance_views:
        (root / PROVENANCE_VIEW_DIRNAME / f"{v.object_id}.json").write_text(
            json.dumps(asdict(v), indent=2, default=repr)
        )

    rank_path = root / "rank_triples.jsonl"
    rank_path.write_text("\n".join(json.dumps(asdict(t)) for t in emission.rank_triples))
    triplet_path = root / "triplet_triples.jsonl"
    triplet_path.write_text("\n".join(json.dumps(asdict(t)) for t in emission.triplet_triples))

    (root / "splits.json").write_text(
        json.dumps(
            {
                "train": list(emission.splits.train),
                "validation_same_region": list(emission.splits.validation_same_region),
                "validation_heldout_region": list(emission.splits.validation_heldout_region),
                "validation_heldout_method": list(emission.splits.validation_heldout_method),
                "validation_later_time": list(emission.splits.validation_later_time),
                "synthetic_null": list(emission.splits.synthetic_null),
            },
            indent=2,
        )
    )

    return root


# ---------------------------------------------------------------------------
# Loader — anti-leakage flag enforcement
# ---------------------------------------------------------------------------


class PostFalsificationLeakageError(RuntimeError):
    """Raised when a caller tries to load post-falsification view as a
    predictive feature without explicit ``allow_post_falsification=True``.
    """


class LearnerCorpusLoader:
    """Load CorpusEmission from disk with anti-leakage discipline.

    Default behaviour: ``load()`` returns pre_falsification views only.
    To load post_falsification views, the caller MUST pass
    ``allow_post_falsification=True`` to ``load_post_view()``; every
    such load is logged as a potential leakage event.
    """

    def __init__(self, emission_root: Path):
        self.root = Path(emission_root)
        if not self.root.exists():
            raise FileNotFoundError(f"emission root not found: {self.root}")
        meta_path = self.root / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"metadata.json not found at {self.root}")
        self.metadata: Dict[str, Any] = json.loads(meta_path.read_text())
        self.schema_version: str = self.metadata.get("schema_version", "unknown")

    # -- pre-view (default, safe) ------------------------------------------

    def load(self) -> Iterator[PreFalsificationView]:
        """Default loader: yields pre_falsification views only.

        This is the safe path. Use this for primary Learner training.
        """
        pre_dir = self.root / PRE_VIEW_DIRNAME
        for path in sorted(pre_dir.glob("*.json")):
            d = json.loads(path.read_text())
            obj = d["object"]
            yield PreFalsificationView(
                object_id=d["object_id"],
                object=ObjectFeatures(
                    domain=obj["domain"],
                    canonical_form=obj["canonical_form"],
                    raw_invariants=obj["raw_invariants"],
                    coordinate_chart_id=obj["coordinate_chart_id"],
                    neighbors_in_chart=tuple(obj.get("neighbors_in_chart", ())),
                ),
            )

    # -- provenance view (audit trail; not a predictive input) -------------

    def load_provenance(self) -> Iterator[ProvenanceView]:
        """Load provenance views (audit trail). Never used as predictive
        features; useful for split construction, label-version tracking,
        synthetic-null filtering."""
        prov_dir = self.root / PROVENANCE_VIEW_DIRNAME
        for path in sorted(prov_dir.glob("*.json")):
            d = json.loads(path.read_text())
            yield ProvenanceView(
                object_id=d["object_id"],
                label_source=d["label_source"],
                label_time=float(d["label_time"]),
                label_version=d["label_version"],
                label_strength=d.get("label_strength", "candidate"),
                falsifier_versions=d.get("falsifier_versions", {}),
                operator_that_generated_candidate=d.get(
                    "operator_that_generated_candidate", ""
                ),
                synthetic_null_family=d.get("synthetic_null_family"),
                known_artifact_flags=tuple(d.get("known_artifact_flags", ())),
                possible_future_positive_flag=bool(
                    d.get("possible_future_positive_flag", False)
                ),
            )

    # -- post-view (gated; logs leakage event) ------------------------------

    def load_post_view(
        self,
        *,
        allow_post_falsification: bool,
        caller_id: str,
        purpose: str,
    ) -> Iterator[PostFalsificationView]:
        """Load post_falsification views.

        REQUIRES explicit opt-in via ``allow_post_falsification=True``.
        Without it, raises ``PostFalsificationLeakageError``.

        Every load is logged to ``_post_view_load_events.jsonl`` in the
        emission root; the substrate's leakage-audit tooling reads
        this file to detect predictive use of post-falsification
        features.

        Parameters
        ----------
        allow_post_falsification : bool
            MUST be True. The keyword is required to be explicit so
            callers cannot accidentally pass it.
        caller_id : str
            Identifier of the calling code (e.g.
            ``"ergon.learner.tire_kick.W4_2"``). Logged.
        purpose : str
            Why this post-view load is happening. Acceptable purposes:
            ``"explanation"`` (post-hoc analysis of model outputs),
            ``"calibration"`` (using post-view to calibrate confidence
            scores), ``"audit"`` (leakage audit itself). Any other
            purpose is logged and accepted but flagged in the audit
            trail.
        """
        if not allow_post_falsification:
            raise PostFalsificationLeakageError(
                "Loading post_falsification view requires "
                "allow_post_falsification=True. This view contains kill "
                "outcomes from the same falsifiers that compute training "
                "labels — using it as a predictive feature creates label "
                "leakage. See substrate v2.3 §6.3 NearMissCorpus contract."
            )

        # Log the load event regardless of purpose. The leakage-audit
        # tooling reads this file.
        log_event = {
            "ts": time.time(),
            "caller_id": caller_id,
            "purpose": purpose,
            "emission_id": self.metadata["emission_id"],
        }
        log_path = self.root / LEAKAGE_LOG_FILENAME
        with open(log_path, "a") as f:
            f.write(json.dumps(log_event) + "\n")

        post_dir = self.root / POST_VIEW_DIRNAME
        for path in sorted(post_dir.glob("*.json")):
            d = json.loads(path.read_text())
            yield PostFalsificationView(
                object_id=d["object_id"],
                kill_vector=d.get("kill_vector"),
                evidence_field=d.get("evidence_field"),
                triangulation_path=d.get("triangulation_path", "untriangulated:stub"),
                method_spec=d.get("method_spec"),
                caveats=tuple(d.get("caveats", ())),
                exclusion_certificate_ref=d.get("exclusion_certificate_ref"),
            )

    # -- splits + triples (safe; reference object_ids only) ----------------

    def load_splits(self) -> Splits:
        d = json.loads((self.root / "splits.json").read_text())
        return Splits(
            train=tuple(d.get("train", ())),
            validation_same_region=tuple(d.get("validation_same_region", ())),
            validation_heldout_region=tuple(d.get("validation_heldout_region", ())),
            validation_heldout_method=tuple(d.get("validation_heldout_method", ())),
            validation_later_time=tuple(d.get("validation_later_time", ())),
            synthetic_null=tuple(d.get("synthetic_null", ())),
        )

    def load_rank_triples(self) -> List[RankLossTriple]:
        path = self.root / "rank_triples.jsonl"
        if not path.exists() or path.stat().st_size == 0:
            return []
        return [
            RankLossTriple(**json.loads(line))
            for line in path.read_text().splitlines()
            if line.strip()
        ]

    def load_triplet_triples(self) -> List[TripletLossTriple]:
        path = self.root / "triplet_triples.jsonl"
        if not path.exists() or path.stat().st_size == 0:
            return []
        return [
            TripletLossTriple(**json.loads(line))
            for line in path.read_text().splitlines()
            if line.strip()
        ]

    # -- audit ---------------------------------------------------------------

    def post_view_load_events(self) -> List[Dict[str, Any]]:
        """Return all logged post-view load events from this emission's
        leakage audit trail. Used by the substrate's leakage-detection
        tooling to flag callers that read post-view as predictive
        features."""
        path = self.root / LEAKAGE_LOG_FILENAME
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    "SCHEMA_VERSION",
    "RAW_INVARIANTS_PER_DOMAIN",
    "get_raw_invariant_keys",
    "ObjectFeatures",
    "PreFalsificationView",
    "PostFalsificationView",
    "ProvenanceView",
    "RankLossTriple",
    "TripletLossTriple",
    "SplitName",
    "Splits",
    "CorpusEmission",
    "stub_emit_from_legacy_ledger",
    "emit_from_substrate",
    "write_emission_to_disk",
    "LearnerCorpusLoader",
    "PostFalsificationLeakageError",
]
