# Evidence Wiki — V1 Architecture Delta

Status: V1 qualification campaign, 2026-09-02. Baseline: `ARCHITECTURE_V0.md`
(unchanged, frozen). Charter:
`roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V1_2026-09-02.txt`
(sha256 52d4a256490cff6c1d51b15f8d89b9623fa6f09deefaa323f7d775a00ddc8a54).
Preregistration: `PREREGISTRATION_V1.md` (frozen at commit a2898d196 BEFORE
any campaign agent launched).

V1 changes NOTHING about the epistemic core (append-only, content-addressed,
provenance-required, derived-quarantined). It adds qualification machinery
and governance:

## 1. Ontology v2 + mechanism governance (charter s4)
- `ew.ontology_versions` row 2; new relation types: FAILS_TO_REPLICATE,
  EXTENDS, TESTS, FALSIFIES (metabolization vocabulary, s8).
- `ew.mechanism_registry`: versioned, append-only mechanism records — label,
  definition, inclusion criteria, exclusion criteria (hand-written for the
  17 confusable sibling pairs; TBD-marked elsewhere, to be refined from
  V1-A disagreement data), examples, supersedes, deprecation, rationale.
  Refinement = insert (term_id, version+1) with `supersedes`; old versions
  are never rewritten; historical assignments keep their ontology_version.

## 2. Fixture namespace (charter s15, gate G13)
- `ew.object_namespace`: append-only classification (fixture/test), never
  deletion. Production views `ew.claims_prod`/`evidence_prod`/
  `relations_prod` exclude namespaced rows; search, coordinates, telemetry,
  contradictions and consumer stats read only production views. Raw tables
  remain for audit. V0 demo/smoke rows were namespaced on migration.

## 3. Operational hardening (charter s16)
Per-machine tokens binding claimed machine identity (legacy shared token
accepted, attributed as legacy); watchdog + Task Scheduler autostart with
verified kill/restart (G15); rotation procedure + failure logging in
`OPERATIONS_V1.md`.

## 4. Observability (charter s18)
`GET /api/v1/telemetry`: reads/writes by agent+endpoint, negative-evidence
reuse/orphan rates (reuse = OBSERVED reuse-typed relation, citation does not
count), cross-agent reuse counts, freshness. Every V1-B wiki-arm
consultation is captured in `ew.read_log` (G18 traceability).

## 5. Qualification campaigns (results in benchmarks/ + docs/)
- V1-A independent ontology qualification: held-out corpus (sources disjoint
  from all 38 V0 source files), 6 isolated annotators in conditions A/B/C +
  a post-hoc normalizer; agreement, disagreement matrix, forced-fit and
  growth rates; G3 retrieval with annotator-only labels (Mnemosyne excluded
  from both prediction and adjudication). `ONTOLOGY_QUALIFICATION_V1.md`.
- V1-B metabolization: 8 frozen tasks x {control, wiki}, 16 isolated
  agents; deterministic trap/reuse/falsifier checklists frozen in prereg.
  `METABOLIZATION_EXPERIMENT_V1.md`.
- V1-C prospective gaps: 15 blinded MISSING_CELL hypotheses (marginal /
  uniform-random / freq-weighted-random slates, method sealed by hash);
  adjudication PENDING_PROSPECTIVE per prereg. `GAP_SURFACING_V1.md`.
- Tensor policy: learning-curve milestones only (`tensor_learning_curve.json`);
  no rescue; G6 reopens at >=1000 real coordinates.

## 6. Known V1 structural limitations (declared up front)
- "Independent" annotators and designers are isolated Claude contexts, not
  different model families; shared priors may inflate agreement. Recorded in
  every V1 verdict as a scope ceiling.
- Mnemosyne authors the deterministic scoring of V1-B against frozen
  checklists; mitigation: checklists frozen pre-run, mandatory quotes,
  scoring sheet shipped for human audit.
- Control arms may (and do) find prior evidence via ordinary repo search;
  that is the intended comparator, not a confound.
