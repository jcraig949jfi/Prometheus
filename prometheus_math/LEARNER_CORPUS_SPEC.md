# P5 NearMissCorpus — Spec (v2.3-stub)

**Module:** `prometheus_math/learner_corpus.py`
**Status:** Pre-Tier-0 interface stub. Real triangulated emission ships at Day 13 of joint sprint.
**Authors:** Techne (substrate side) — pinned per Ergon's Q-E1 / Q-E2 / Q-E3 / Q-E4 / Q-E5 answers.
**Anti-leakage discipline:** load-bearing per ChatGPT + Gemini convergent critique on substrate v2.

---

## What this is

The contract between Techne's substrate and Ergon's Learner. Defines:

- The schema for a `CorpusEmission` (multi-view: pre / post / provenance).
- The two triple shapes (rank-loss + triplet-loss).
- Canonical splits (train / val_same_region / val_heldout_region / val_heldout_method / val_later_time / synthetic_null).
- The loader API with anti-leakage flag enforcement.
- Per-domain raw-invariant feature lists.

Ergon's Pipeline-D scaffolds against this schema starting Day 1 of the joint sprint. The stub emitter (`stub_emit_from_legacy_ledger`) lets Pipeline-D consume *something* during Days 1-12; real emission swaps in at Day 13 via the same loader API. Same code path, upstream emitter changes.

---

## Anti-leakage discipline (load-bearing)

Per ChatGPT's 8 contrastive-corpus failure modes + Gemini's trivial-separability warning + Aporia's closed-loop concern:

1. **Pre and post views write to different file paths.** `<emission>/pre_falsification/` and `<emission>/post_falsification/` are separate subdirectories.
2. **Loader requires explicit opt-in to load post-view as predictive features.** `LearnerCorpusLoader.load_post_view(allow_post_falsification=True, caller_id=..., purpose=...)` — keyword-only flag, all three params required. Default `load()` returns pre-view only.
3. **Every post-view load is logged.** Append-only `_post_view_load_events.jsonl` in the emission root captures `(timestamp, caller_id, purpose, emission_id)`. The substrate's leakage-audit tooling reads this file.
4. **`emit_from_substrate()` is intentionally `NotImplementedError` until Day 13.** Prevents accidental training on stub data.

The discipline is enforcement, not convention. Bypass requires editing the loader; any such edit is visible in code review.

---

## Schema

### CorpusEmission (top-level)

```python
@dataclass(frozen=True)
class CorpusEmission:
    schema_version: str           # "v2.3-stub" or "v2.3"
    emission_id: str              # content-addressed
    region_key: str               # e.g. "lehmer:deg14:pm5:palindromic"
    label_version: str            # e.g. "discovery_pipeline:v1.5"
    emitted_at: float

    pre_views: Tuple[PreFalsificationView, ...]
    post_views: Tuple[PostFalsificationView, ...]
    provenance_views: Tuple[ProvenanceView, ...]

    rank_triples: Tuple[RankLossTriple, ...]
    triplet_triples: Tuple[TripletLossTriple, ...]

    splits: Splits
```

### PreFalsificationView (Learner training input — default)

```python
@dataclass(frozen=True)
class PreFalsificationView:
    object_id: str        # content-addressed hash
    object: ObjectFeatures

@dataclass(frozen=True)
class ObjectFeatures:
    domain: str
    canonical_form: Any                  # JSON-serialisable
    raw_invariants: Mapping[str, Any]    # keyed by RAW_INVARIANTS_PER_DOMAIN[domain]
    coordinate_chart_id: str             # "provisional:<env>" until P0 Day 3-4
    neighbors_in_chart: Tuple[str, ...]  # same-cluster siblings (anti-trivial-separability)
```

**Hard rule:** anything in `ObjectFeatures` must be derivable from the object's identity / canonical form alone — never from kill outcomes, triangulation results, or post-falsification margins.

### PostFalsificationView (gated; explanation/calibration only)

```python
@dataclass(frozen=True)
class PostFalsificationView:
    object_id: str                          # MUST match a pre-view's object_id
    kill_vector: Optional[Mapping[str, Any]] = None
    evidence_field: Optional[Mapping[str, Any]] = None      # DEFERRED: P1 Day 6-7
    triangulation_path: str = "untriangulated:stub"          # DEFERRED: P6 Day 8-12
    method_spec: Optional[Mapping[str, Any]] = None          # DEFERRED: P3 Day 5
    caveats: Tuple[str, ...] = ()
    exclusion_certificate_ref: Optional[str] = None          # DEFERRED: P4 Day 8-12
```

The `# DEFERRED` markers indicate fields that the stub leaves at default and the real emission populates.

### ProvenanceView (audit trail; never a predictive input)

```python
@dataclass(frozen=True)
class ProvenanceView:
    object_id: str
    label_source: str
    label_time: float
    label_version: str
    label_strength: str = "candidate"  # candidate | robust | promoted | rejected
    falsifier_versions: Mapping[str, str] = {}
    operator_that_generated_candidate: str = ""
    synthetic_null_family: Optional[str] = None
    known_artifact_flags: Tuple[str, ...] = ()
    possible_future_positive_flag: bool = False
```

---

## Triple shapes (Q-E1: both useful, not redundant)

Per Ergon's confirmation: emit BOTH shapes; consumer picks via API.

### RankLossTriple

```python
@dataclass(frozen=True)
class RankLossTriple:
    positive_id: str
    near_miss_id: str       # between positive and negative on a scalar
    negative_id: str
    near_miss_kind: str     # boundary | method | structural | random_hard | adversarial
```

For rank-loss / ordinal training where near-miss is between positive and negative on a scalar (e.g., KillVector margin distance).

### TripletLossTriple

```python
@dataclass(frozen=True)
class TripletLossTriple:
    anchor_id: str
    positive_id: str
    hard_negative_id: str
    margin_dimension: str   # which dimension separates positive from hard_negative
```

For triplet-loss with margin where hard-negative differs from positive on a specific dimension (e.g., categorical class boundary).

### Anti-trivial-separability rule (Gemini)

All three members of a triple MUST share a coordinate-chart neighborhood (same boundary-layer cluster, same region cell). The Learner is forced to learn structural geometry, not magnitude variance.

The stub emitter does NOT generate triples — that requires P5 proper + boundary-layer clustering. Consumers see `rank_triples == ()` and `triplet_triples == ()` until Day 13.

---

## Splits (Q-E4: temporal ordering matters)

```python
class SplitName(str, enum.Enum):
    TRAIN = "train"
    VAL_SAME_REGION = "validation_same_region"
    VAL_HELDOUT_REGION = "validation_heldout_region"
    VAL_HELDOUT_METHOD = "validation_heldout_method"
    VAL_LATER_TIME = "validation_later_time"
    SYNTHETIC_NULL = "synthetic_null"
```

`val_later_time` is the temporal split: train on earlier substrate records, validate on later records. Confirms the Learner does not exploit batch artifacts. Per Ergon's Q-E4 confirmation (her iter28 → iter31 → iter39 ordering is the canonical example).

The stub emitter puts everything in `train` by default; Ergon overrides for tire-kick experiments.

---

## Per-domain raw-invariant feature registry (Q-E2)

```python
RAW_INVARIANTS_PER_DOMAIN: Dict[str, Tuple[str, ...]] = {
    "lehmer":           (13 keys; pinned by Ergon's Q-E2 answer)
    "bsd_rank":         (5 keys; v1.0 pinning)
    "modular_form":     (4 keys; v1.0 pinning)
    "knot_trace_field": (4 keys; v1.0 pinning)
    "genus2":           (3 keys; v1.0 pinning)
    "oeis_sleeping":    (4 keys; v1.0 pinning)
    "mock_theta":       (4 keys; v1.0 pinning)
    "obstruction_shape": ("__deferred_to_charon__",)
}
```

Lehmer's 13-key list (Ergon Q-E2):
```
poly_coefficients, mahler_measure_dps30, mahler_measure_dps60, mahler_measure_dps100,
height, lead_coefficient, palindromicity_check, n_irreducible_factors,
cyclotomic_factor_indices, cyclotomic_factor_powers,
non_cyclotomic_factor_present, non_cyclotomic_factor_mahler,
reflection_pair_partner_hash
```

`obstruction_shape` defers to Charon coordination per joint sprint Q-C1.

---

## Disk layout

```
<output_root>/<emission_id>/
    metadata.json
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
    _post_view_load_events.jsonl    # appended by loader on each post-view load
```

Pre / post / provenance views live in different subdirectories. This is the file-system layer of the anti-leakage discipline. A consumer that wants to grep for `kill_vector` data must explicitly cd into `post_falsification/` — no accidental contamination from `pre_falsification/`.

---

## Loader API (anti-leakage gate)

```python
class LearnerCorpusLoader:
    def __init__(self, emission_root: Path): ...
    def load(self) -> Iterator[PreFalsificationView]: ...               # safe; default
    def load_provenance(self) -> Iterator[ProvenanceView]: ...          # safe; audit
    def load_post_view(
        self,
        *,
        allow_post_falsification: bool,    # MUST be True
        caller_id: str,                    # required; logged
        purpose: str,                      # required; logged
    ) -> Iterator[PostFalsificationView]: ...
    def load_splits(self) -> Splits: ...
    def load_rank_triples(self) -> List[RankLossTriple]: ...
    def load_triplet_triples(self) -> List[TripletLossTriple]: ...
    def post_view_load_events(self) -> List[Dict[str, Any]]: ...        # leakage audit trail
```

`load_post_view`'s three keyword-only parameters cannot be omitted — Python raises `TypeError` if any is missing. Passing `allow_post_falsification=False` raises `PostFalsificationLeakageError` with the explanation. Passing `allow_post_falsification=True` succeeds AND appends a row to `_post_view_load_events.jsonl`.

---

## Stub vs real emission

### `stub_emit_from_legacy_ledger(records, *, region_key, label_version, domain, output_root=None)`

The Day 1-12 stub. Reads legacy promotion-ledger records and emits a multi-view CorpusEmission. Limitations vs real emission:

- No triple generation (requires boundary-layer clustering)
- No triangulation_path (requires P6 Day 8-12)
- No method_spec (requires P3 Day 5)
- No evidence_field (requires P1 Day 6-7)
- No exclusion_certificate_ref (requires P4 Day 8-12)
- No synthetic_null pack
- Default split is all-train

These are documented as DEFERRED fields. The schema is forward-compatible — the real emission populates them without breaking the stub-shaped consumers.

### `emit_from_substrate(...)`

Raises `NotImplementedError` with message *"Real P5 emission ships at Day 13 of joint sprint (Tier 2). Use stub_emit_from_legacy_ledger() during Days 1-12."*

Intentional — prevents Ergon from accidentally training on stub data thinking it is real triangulated emission.

---

## Sister-project commitments tied to this spec

From `pivot/techne_ergon_joint_sprint_2026-05-05.md`:

- **T1** (Techne Day 1-2): P5 interface stub published. ✅ This module.
- **T8** (Techne Day 6-7): KillVector v2 (+8 components) ships; auto-populated for the 3 v0.5-relevant components. → upgrades `PostFalsificationView.kill_vector` content.
- **T10** (Techne Day 8-12): P4 ExclusionCertificate + P6 TriangulationProtocol + P5 full emission. → upgrades all DEFERRED fields; `emit_from_substrate()` becomes implemented.
- **E4** (Ergon Day 1-7): Pipeline-D scaffolds against P5 interface (not against legacy promotion_ledger). → consumes this stub.
- **E5** (Ergon Day 14+): Train on `pre_falsification_view` only; explicit `--allow-post-falsification` flag for opt-in. → uses `LearnerCorpusLoader.load()` by default; `load_post_view(allow_post_falsification=True, ...)` only with logged caller intent.
- **S12** (Day 13-14): Stub-to-real migration validation — same loader API consumes both shapes; consumer code path unchanged.

---

## What this spec does NOT cover

- Real triangulation logic (P6, Day 8-12).
- ExclusionCertificate semantics (P4, Day 8-12).
- EvidenceField axes (P1, Day 6-7).
- MethodSpec drift_channel (P3, Day 5).
- CoordinateChart registration (P0, Day 3-4).
- Synthetic-null pack generation (real P5, Day 13).
- Boundary-layer clustering for triple sourcing (real P5, Day 13).

All of these are scheduled in later substrate-sprint deliverables. This spec freezes the *interface contract* — content under each field is upgraded as upstream primitives ship.

---

*One contract, two forges. Pre-view is what the Learner trains on. Post-view is what the substrate explains itself with. They live in different paths because they answer different questions. — Techne, 2026-05-05*
