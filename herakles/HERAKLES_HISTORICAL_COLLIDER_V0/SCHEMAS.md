# HERAKLES_HISTORICAL_COLLIDER_V0 — Record schemas
## Version 0, 2026-09-02. All registries are JSONL (one record per line) or Markdown where prose dominates. Field names below are normative.

Common fields on EVERY record:
- `id` — stable slug (`fam-…`, `spec-…`, `det-…`, `anom-…`, `part-…`, `edge-…`, `gen-…`, `cal-…`, `neg-…`, `art-…`)
- `evidence_source` — one of `ARTIFACT_IN_HAND | PRIMARY_SOURCE_READ | SECONDARY_SUMMARY | MODEL_RECALL_UNVERIFIED`
- `locators` — list of `{type, ref}`; type ∈ `doi|url|archive_url|file|thesis|repo|commit|page|figure|line`
- `written` — ISO date; `promoted` — list of `{date, from, to, locator}` promotions of `evidence_source`
- `kill_observation` — the single observation that would end interest (mandatory for spec/anom/part/composition records)
- `notes` — free text

---

## A. Field map — `A_FIELD_MAP.md` (prose table; one row per family)
`fam_id | tradition | system/experiment | years | investigators | artifact_status (belief) | lens (why it matters to §1) | evidence_source`

## B. Specimen registry — `B_SPECIMEN_REGISTRY.jsonl`
```
spec_id, fam_id, name, years, investigators,
physics_size: {genome_bits|genome_len, population, generations, world_dims, step_cost_est},
phenomenon_of_interest: [candidate signals from directive §1],
artifacts: {paper, supplement, source, data, dumps, logs, configs, seeds, thesis} each ∈ KNOWN_LOCATED|REPORTED|UNKNOWN|LOST,
provenance_class_attainable: ORIGINAL_SPECIMEN|RECOVERED_SPECIMEN|REIMPLEMENTATION|APPROXIMATE_RECONSTRUCTION|CONCEPTUAL_REPRODUCTION,
original_detector_ref: det_id,
rank_criteria: {microdynamics, artifacts, reconstructability, evolvability_relevance, blindness, replication_leverage, counterfactuals, composability, simplicity, info_gain}  (each 0-3 or null),
sfe_feasibility: TRIVIAL|CHEAP|MODERATE|EXPENSIVE|INFEASIBLE,
parts_contained: [part_id], composes_with: [part_id],
kill_observation, evidence_source, locators, written, notes
```

## C. Detector archaeology registry — `C_DETECTOR_ARCHAEOLOGY_REGISTRY.jsonl`
```
det_id, spec_id|fam_id,
wanted_to_measure, could_measure, threw_away, compute_prevented, anomalies_mentioned_not_pursued,
questionnaire: { every §2-B item -> YES|NO|PARTIAL|UNKNOWN with locator },
vesuvius: {orig_compute, orig_storage, orig_replication, orig_resolution,
           modern_compute, modern_storage, modern_replication, sfe_resolution}  (order-of-magnitude strings, labelled EST),
at_10000x: {anomaly_frequency, treatment_null_diff, seed_dependence, lineage_dependence, precursor_frequency, env_dependence, cond_prob_later_innovation, false_positive_rate}  (what would be estimable),
sfe_would_record_that_original_did_not: [..],
counterfactual_impossible_then: [..],
evidence_source, locators, written
```

## D. Failure / anomaly registry — `D_FAILURE_ANOMALY_REGISTRY.jsonl`
```
anom_id, spec_id|fam_id, quoted_language (verbatim if PRIMARY_SOURCE_READ), where (page/fig/file),
class: TRANSIENT|NEUTRAL|DELETERIOUS|DISCARDED|EXCLUDED_RUN|FAILED_REPLICATION|SEED_DEPENDENT|PLATEAU|COLLAPSE|CYCLING|OUTLIER|UNEXPLAINED|EXPLOIT,
mundane_explanations: [..], status: LEAD|REPLICATED|EXPLAINED|KILLED,
kill_observation, evidence_source, locators, written
```

## E. Synthetic reasoning parts registry — `E_PARTS_REGISTRY.jsonl` (fields verbatim from directive Mission C)
```
part_id, historical_terminology: [..], source_experiments: [spec_id],
causal_computational_description, required_preconditions, transformation, observable_consequence, downstream_effect,
evidence_strength: observed_association|historical_sequence|perturbation|ablation|replication|mechanistic_proof,
replication_status, known_failure_modes, substrate_dependence,
candidate_equivalent_mechanisms: [part_id], candidate_complementary_mechanisms: [part_id], possible_compositions: [[part_id,..]],
sfe_reproduction_feasibility, minimum_reconstruction_needed, confidence: 0-1,
status: CANDIDATE_PART|PART, kill_observation, evidence_source, locators, written
```

## F. Part composition graph — `F_PART_COMPOSITION_GRAPH.jsonl` (edges)
```
edge_id, from: part_id, to: part_id|capability_region, relation: enables|protects|combines_with|opens|suppresses|substitutes,
evidence_class: observed_association|historical_sequence|perturbation|ablation|replication|mechanistic_proof,
historical_cooccurrence: [spec_id] (systems containing both ends), measured_jointly: bool, effect_shape: additive|superadditive|subadditive|unknown,
evidence_source, locators, written
```

## G. Circuit-genealogy candidates — `G_CIRCUIT_GENEALOGY_CANDIDATES.md`
Prose per candidate: sequence X → Y → Z; per link the §11 questions (required? useful when it appeared? altered accessible mutations? duplication mattered? could later arise without it? useful only after Y? environment Z converted it?) each answered with evidence class.

## H. Calibration particle set — `H_CALIBRATION_PARTICLES.md`
`cal_id | phenomenon | system | established causal structure (how) | what a detector must recover blind | detector(s) to test | status`

## I. Negative control set — `I_NEGATIVE_CONTROLS.md`
`neg_id | system | why it looks like a precursor | why it is not (or is not yet shown to be) | what a detector must NOT report | status`

## J. Recovered artifact manifest — `J_RECOVERED_ARTIFACT_MANIFEST.jsonl`
```
art_id, spec_id, kind: source|binary|genome|population_dump|log|config|seed|dataset|thesis|website|archive,
sha256, bytes, path (repo or Z:\), retrieved_from, retrieved_at, archive_snapshot, provenance_class, derived_from: art_id|null, custody_notes
```

## K. Reconstruction queue — `K_RECONSTRUCTION_QUEUE.md`
Ranked table: `rank | spec_id | rubric score (10 criteria) | provenance class attainable | first question to SFE | est. cost | blocking unknowns`

## L. Compute-leverage table — `L_COMPUTE_LEVERAGE_TABLE.md`
`spec_id | original runs | original compute (EST) | modern cost per run (EST) | runs affordable now | question that becomes answerable | question that stays unanswerable`

## M. Blind-spot matrix — `M_BLIND_SPOT_MATRIX.md`
Rows = phenomena (directive §1 list); columns per family = `observable? recorded? preserved? reconstructable? SFE-detectable? causal test? modern replication? info gain`.

## N/O/P. TOP lists — `N_TOP20_BUMPS.md`, `O_TOP20_PARTS.md`, `P_TOP10_UNTESTED_COMPOSITIONS.md`
Entry requires `evidence_source ∈ {ARTIFACT_IN_HAND, PRIMARY_SOURCE_READ}` and the sixteen §25 answers. Until then the files hold a labelled CANDIDATE POOL only.
