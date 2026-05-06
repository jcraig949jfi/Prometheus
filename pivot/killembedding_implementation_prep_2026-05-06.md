# KillEmbedding Implementation Prep Checklist

**Date:** 2026-05-06
**Author:** Techne (substrate side)
**Status:** Prep — code-free. Cross-review window open Days 5-12; implementation slot Days 13-17. This doc maps every field in `K(c)` (per `pivot/killembedding_design_seed_2026-05-06.md`) to its substrate source, identifies what needs new accessors, and surfaces the telemetry pipes for the `computational_friction` axis.
**Predecessor:** `pivot/killembedding_design_seed_2026-05-06.md` (Aporia, K(c) v0.1 schema).
**Related ticket:** T-2026-05-06-T002 (this work).

---

## TL;DR

Of K(c)'s 19 fields, **17 are already-public substrate APIs as of v2.3 commit `d17a2ff8`.** Two need lightweight helpers: a margin-array extraction from KillVector (one-liner) and a near-miss boolean derivation (one-liner). One field (`parent_cell_ids`) is sourced from Ergon's `tools/lineage_replay.py`, not from the substrate. The `computational_friction` telemetry is fully populated for A149 and now-instrumented (Pre-Tier-0 0b) for the 6 cross-domain envs.

**No new substrate primitives needed.** No contract changes needed. Implementation can begin Day 13 against the substrate as currently shipped.

---

## §1 — K(c) field → substrate source mapping

| K(c) field | Substrate source | Already public? | Implementation note |
|---|---|---|---|
| `cell_id` | `PreFalsificationView.object_id` (content-addressed sha256) | ✅ | Use `_content_hash(canonical_form, raw_invariants)` from `prometheus_math.learner_corpus`. |
| `domain` | `ObjectFeatures.domain` | ✅ | Per-record; matches `RAW_INVARIANTS_PER_DOMAIN` keys. |
| `coordinate_chart_id` | `ObjectFeatures.coordinate_chart_id`; resolves via `sigma_kernel.coordinate_chart.get_chart()` | ✅ | Provisional ids (`provisional:<domain>`) for the 5 cross-domain envs until Charon-coord lands T11; Lehmer chart registered. |
| `operator_class` | `ProvenanceView.operator_that_generated_candidate` | ✅ | Free-form string; v0.1 K(c) schema's enum `{structural / symbolic / anti_prior / uniform / structured_null}` is documentation, not enforcement. |
| `timestamp` | `ProvenanceView.label_time` | ✅ | Unix epoch seconds. |
| `kill_vector` (20 components) | `PostFalsificationView.kill_vector` (KillVector.to_dict shape) | ✅ | KillVector v2 ships 12 legacy + 8 new (relativizes / naturalizes / local_global_gap / requires_unproven_conjecture / asymptotic_only / small_case_artifact / asymmetric_effort / interpretive_slack). |
| `margin_profile` (np.ndarray shape (20,)) | derived from `KillVector.components[i].margin` | ⚠️ helper | See §2 — one-liner extractor. |
| `method_spec` | `PostFalsificationView.method_spec` (MethodSpec dict) | ✅ | P3 ships engine / strategy / precision_dps / version / parameters / fallback_chain / **independence_class** / drift_channel. |
| `stability_pass` | `KillComponent.stability_pass` (StabilityResult dict; legacy `stability` scalar still readable) | ✅ | Note: schema seed says `StabilityRecord`; substrate ships as `StabilityResult` (rename already noted in Aporia b23851c4). |
| `neighbors_in_chart` | `ObjectFeatures.neighbors_in_chart` (tuple of object_ids) | ✅ | Currently empty for stub; populated by P5 real emission when boundary-layer clustering ships. |
| `terminal_state` | `DiscoveryRecord.terminal_state` (literal `PROMOTED / SHADOW_CATALOG / REJECTED`) | ✅ | Lives in `prometheus_math.discovery_pipeline`. |
| `dominant_kill_pattern` | `KillVector.to_legacy_kill_path()` | ✅ | Legacy compat shim; first-triggered component's pattern. |
| `near_miss` | derived from `KillVector` triggered-count vs floor | ⚠️ helper | See §2 — one-liner derivation. |
| `elapsed_seconds` | `EvidenceField.computational_friction.elapsed_seconds` (or `info["elapsed_seconds"]` in env step) | ✅ | Pre-Tier-0 0b instrumented all 6 cross-domain envs. |
| `oracle_calls` | `EvidenceField.computational_friction.oracle_calls` (or `info["oracle_calls"]`) | ✅ | Same as above. |
| `peak_memory_mb` | DEFERRED (psutil not justified at v0) | ⚠️ NaN | Document as expected-NaN; not a blocker. |
| `triangulation_history` (list[str] in K(c) v0.1) | `PostFalsificationView.triangulation_path` (string); fuller via `ExclusionCertificate.triangulation_history` (list[TriangulationPathRef]) | ✅ | K(c) v0.1 uses path_id strings; v0.2 upgrade-path documented in seed if richer signal needed. |
| `exclusion_certificate_ref` | `PostFalsificationView.exclusion_certificate_ref` | ✅ | Optional certificate_id string. |
| `parent_cell_ids` | NOT in P5 emission; Ergon's `tools/lineage_replay.py` (W2.3) | external | Per Aporia b23851c4: dropped from K(c) v0.1, sourced at training time from Ergon's tool. v0.2 may promote to canonical if cross-review surfaces a need. |

**Counts:** 17 already-public + 2 helpers + 1 external (Ergon-side) + 1 deferred = 21 paths covered for the 19-field K(c) v0.1 schema.

---

## §2 — Helpers needed (lightweight, NO contract changes)

Both can live in a new file `prometheus_math/kill_embedding_helpers.py` (within file ownership, no API change to existing modules).

### Helper A — `kill_vector_to_margin_array(kv: KillVector) -> np.ndarray`

```python
def kill_vector_to_margin_array(kv: KillVector) -> np.ndarray:
    """Extract a length-20 margin array (NaN-padded) from a KillVector.

    Order matches ALL_COMPONENT_NAMES (12 legacy + 8 v2 in canonical
    append order). Missing components or None margins → np.nan.
    """
    from prometheus_math.kill_vector import ALL_COMPONENT_NAMES
    by_name = {c.falsifier_name: c for c in kv.components}
    out = np.full(len(ALL_COMPONENT_NAMES), np.nan, dtype=np.float32)
    for i, name in enumerate(ALL_COMPONENT_NAMES):
        c = by_name.get(name)
        if c is not None and c.margin is not None:
            out[i] = float(c.margin)
    return out
```

Length is `len(ALL_COMPONENT_NAMES)` (= 20 in v2.3). NaN propagation is the documented signal for "this falsifier didn't fire / didn't record a margin"; the K(c) schema seed names this convention.

### Helper B — `kill_vector_is_near_miss(kv: KillVector, floor_k: int = ...) -> bool`

```python
def kill_vector_is_near_miss(kv: KillVector, floor_k: int = 3) -> bool:
    """A near-miss cleared >= floor_k falsifiers (i.e. survived k checks
    before being killed). 'Cleared' = component.triggered is False.
    Default floor_k=3 matches the substrate's existing
    coalescing_failure_signature_caveat threshold direction.
    """
    cleared = sum(1 for c in kv.components if not c.triggered)
    return cleared >= floor_k
```

`floor_k` default is open for cross-review tuning — pin during implementation against the existing 314K kill ledger's distribution.

### What about an emission iterator?

Optional v0.2 ergonomic helper: `iterate_k_objects(emission: CorpusEmission) -> Iterator[KillObject]` that walks pre/post/provenance views by object_id and yields fully-assembled K(c) records. Not strictly needed — training-side code can do the join. Defer unless reviewers flag.

---

## §3 — Schema documentation already in place (no new docs needed)

Reviewers can land cleanly without further substrate-side docs:

- `prometheus_math/LEARNER_CORPUS_SPEC.md` — full P5 NearMissCorpus contract (multi-view + triple shapes + splits + anti-leakage)
- `pivot/substrate_v2_proposal_2026-05-05.md` — substrate v2.3 design with §6.2 P3 MethodSpec + §6.2 P2 stability adapters + §6.3 P4/P6/P5 Tier 2
- `sigma_kernel/method_spec.py` docstrings — IndependenceClass enum, DriftChannel, is_independent_of semantics
- `sigma_kernel/coordinate_chart.py` docstrings — CoordinateChart + CanonicalizationProtocol + decidability_status
- `sigma_kernel/exclusion_certificate.py` docstrings — ExclusionCertificate + triangulation_history hard rule
- `sigma_kernel/triangulation_protocol.py` docstrings — clustering-cannot-certify + INDEPENDENCE_TO_METHOD_CLASS
- `prometheus_math/kill_vector.py` docstrings — KillVector v2 (+8) + PRE_FALSIFICATION_DERIVABLE / POST_FALSIFICATION_ONLY classification

This prep checklist is itself the K(c) → substrate mapping doc Aporia listed as preparatory schema documentation.

---

## §4 — Telemetry sources for `computational_friction` axis

### Already shipped (Pre-Tier-0 0b)

All 6 cross-domain envs emit `info["elapsed_seconds"]` + `info["oracle_calls"]` per `step()`. Sources by env:

- `prometheus_math/bsd_rank_env.py` — wraps kernel.BIND + kernel.EVAL inside step(); oracle_calls=2/step
- `prometheus_math/modular_form_env.py` — same
- `prometheus_math/knot_trace_field_env.py` — same
- `prometheus_math/genus2_env.py` — same
- `prometheus_math/oeis_sleeping_env.py` — same
- `prometheus_math/mock_theta_env.py` — same

Each env's existing `tests/test_<env>_env.py::test_step_info_evidence_field_computational_friction_populated` confirms the wiring.

### A149 historical traces

Per Charon's `SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md`: A149 has 314K logged kills with full per-record traces (cost telemetry, kill_vector, method_spec). This is the prototype dataset for the synthetic-null guard pass. **A149 trace records are training-grade as-is — no new instrumentation needed.**

### Tier 3 envs still emitting `provisional:<domain>` chart_id

The 5 cross-domain envs (BSD / MF / knots / g2c / OEIS / mock theta) emit telemetry correctly but their `coordinate_chart_id` is `provisional:<domain>` until Charon coord lands T11. KillEmbedding training across these envs gates on Charon coordinating chart registration. **A149 prototype path is unaffected by this gate** — A149 has its own chart pending T11 coord but has standalone training value via the synthetic-null guard.

### `peak_memory_mb` (DEFERRED)

Documented in `EvidenceField.computational_friction` as `Optional[float]`; populated as `None` on all current sources. psutil dependency was deferred at Tier 3 ship. Document for reviewers as expected-NaN; revisit when there's a measurement need.

---

## §5 — Substrate side risk inventory for the implementation slot

For Day 13-17 implementation, surface these risks in advance:

1. **K(c) v0.1 `triangulation_history` is `list[str]` of path_ids.** ExclusionCertificate's underlying `triangulation_history` is `list[TriangulationPathRef]` (richer struct: path_id + method_spec + verdict + timestamp + summary). v0.1 deliberately strips to path_id strings. If embedding training shows the path_id alone is uninformative, v0.2 must restore the structured object. Open question for cross-review.
2. **`independence_class` is on MethodSpec, not on KillComponent.** Charon's Q-C2 (in cross-review) asks: if KillEmbedding training treats methods as features without preserving independence_class distinctions, does the embedding silently encode methodological correlations as failure-shape similarities? The substrate exposes the data correctly (MethodSpec.independence_class is queryable per-component); the implementation must explicitly honor it as a feature dimension. Document this in the encoder spec.
3. **`stability_pass` may be `None` for many components** if the falsifier didn't run a stability adapter. K(c) seed says weight-down by 0.5 in loss; the substrate has no objection but flags that the policy choice should be ablated against weight=0 (drop) and weight=1 (full inclusion) to detect whether stability information is actually load-bearing for the geometry.
4. **`neighbors_in_chart` is empty in stub emission**, populated only when real boundary-layer clustering ships. Until then, K(c) training on the A149 prototype must source neighbors from Ergon's W2.3 `tools/lineage_replay.py` or compute on-the-fly via the registered Lehmer CoordinateChart's metric. Document the source clearly so cross-domain training (post-T11) inherits the right pattern.
5. **K(c) v0.1 names DANN-style domain-adversarial mitigation** for cross-domain training. The substrate has no opinion — implementation choice. Surface the question for Q-F1 review (frontier models): does DANN actually generalize cross-mathematical-domain, or is it a tooling import without empirical justification on heterogeneous-corpus settings?

---

## §6 — Sister-project coordination already in place

- **S5/T4 P0 Lehmer chart registered** — KillEmbedding's chart_id resolution works for A149-adjacent reasoning out of the box (Lehmer chart is the prototype for chart-aware substrate queries).
- **S6/T7 P3 MethodSpec shipped** — `independence_class` queryable per method; `drift_channel` available for triangulation independence checks.
- **S7/T8 KillVector v2 (+8) shipped** — 20 components total; `PRE_FALSIFICATION_DERIVABLE` set classifies which components belong in pre vs post view.
- **S8/T10 P5 NearMissCorpus full emission shipped** — `emit_from_substrate()` returns CorpusEmission with all DEFERRED fields populated; KillEmbedding training feeds directly off this.

No further substrate-side blocks for the implementation slot. Cross-review window unblocked from Techne side.

---

## §7 — Open questions for the implementer

1. **Where does `kill_embedding_helpers.py` live?** Proposal: `prometheus_math/kill_embedding_helpers.py` (within file ownership). Alternative: inside the eventual `prometheus_math/kill_embedding.py` module.
2. **Should `kill_vector_is_near_miss` floor_k be a substrate constant or training-side hyperparameter?** Default-3 is reasonable; pin against actual distribution at implementation time.
3. **Does the optional `iterate_k_objects` emission helper belong in `learner_corpus.py` or a new module?** v0.2 question; defer.
4. **For the synthetic-null guard's "structural metrics," does the substrate need to expose any new computation primitives** (silhouette score, kNN consistency, PROMOTE-distance distribution computers)? Tentative answer: NO — these are training-side analysis tools, not substrate primitives. Confirm during implementation.

---

## §8 — What this prep checklist does NOT cover

- The encoder architecture (training-side; per K(c) seed, 2-layer MLP with skip)
- The training loop itself (training-side)
- The synthetic-null guard's actual structure-metric computations (training-side / Charon adjacent)
- Hyperparameter pins (embedding dim d, hard-negative mining strategy, stability weight)
- Cross-domain DANN-style training (waits for T11 + cross-review feedback)
- The KILL_EMBEDDING_VALIDITY_REPORT.md and KILL_EMBEDDING_RESULTS.md deliverables (Days 13-17 implementation outputs)

---

*Substrate side is fully prepped for Day 13-17 implementation. Cross-review (Charon + Ergon + frontier models) is the only remaining gate. — Techne, 2026-05-06 (Fire #1)*
