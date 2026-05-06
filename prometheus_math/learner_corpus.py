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

    Falls back to ``("__unregistered__",)`` for unknown domains so the
    emission shape is always well-defined; consumers can detect
    unregistered domains via this sentinel.
    """
    return RAW_INVARIANTS_PER_DOMAIN.get(domain, ("__unregistered__",))


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


def emit_from_substrate(*args: Any, **kwargs: Any) -> CorpusEmission:
    """Real triangulated emission. NOT IMPLEMENTED — ships at Day 13 of
    joint sprint when P4 ExclusionCertificate + P6 TriangulationProtocol
    are in place. Until then, use ``stub_emit_from_legacy_ledger()``.

    Raising NotImplementedError is *intentional* — it prevents Ergon
    from accidentally training on stub data while believing it is real
    triangulated emission.
    """
    raise NotImplementedError(
        "Real P5 emission ships at Day 13 of joint sprint (Tier 2). "
        "Use stub_emit_from_legacy_ledger() during Days 1-12."
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
