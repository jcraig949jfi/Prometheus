# SAGACITY_FOUNDATION_MAP

Owner of this document: Pan (data infrastructure). Status: v1, 2026-10-11.
Directive: roles/Pan/prompts/2026-10-11_sagacity_foundation (operator, verbatim).
Every population below was measured read-only on the M1 cluster on 2026-10-11 between
09:53Z and 10:10Z (Atlas's last harvest pass: harvest_id 364, finished 2026-10-10T12:30:46Z).
Nothing in this document populates Atlas's or Hades's tables. Schema text marked PROPOSAL
is a proposal to the owning seat, not an applied change.

## 0. One-paragraph answer

The program has an information plane and almost no knowledge plane.

- **Information plane (exists).**
  - Pan: 421,366 catalogued artifacts; 408,916 text chunks with full-text and
    vector indexes (pgvector HNSW); 62,575 document vectors; 46,554 citation links.
  - Atlas: 41,784 facts, each with an evidence pointer; 2,270 experiments; 13,995
    sources; 5,693 lineage edges.
- **Knowledge plane (embryonic).**
  - 10 propositions, of which 6 are already of kind `distinction`.
  - 7 proposition-evidence links; 7 blind spots.
  - 0 CONTRADICTS edges; 1 EXPLAINS edge.
  - No mechanism-equivalence relation with an intervention witness.
  - No program-wide failure-boundary object.

The work is not a new platform. It is three additions:
1. a scoped `distinction` extension and a sparse `boundary` table, both owned by
   Atlas and Hades;
2. provenance-sensitive access classes in the retrieval pipeline, owned by Pan;
3. a calibrated distinctness instrument (NEGATIVE_SPACE_EVALUATION.md) before
   any claim that negative knowledge redirects search.

## 1. What exists: measured populations

### 1.1 Atlas (schema `atlas`, M1 database prometheus_fire; owner: Atlas)

| table | rows | what it is | relevance |
|---|---:|---|---|
| fact | 41,784 | one stated value about a subject. `layer` is RAN, OBSERVED or CONCLUDED; status REPORTED/UNKNOWN/CONTRADICTORY/...; author/method = harvester | the observation layer |
| fact_evidence | 41,785 | fact -> source locator | every fact points at bytes |
| source | 13,995 | a file, row range or ledger slice. Has sha256, commit, and `visibility` = LOCATION (GIT_REMOTE, PG:M1, FS:M2, EXPECTED:...) | provenance anchor. Note: Atlas's "visibility" means WHERE, not WHO MAY READ |
| source_link | 14,246 | source -> entity, with a role | |
| experiment | 2,270 | one experiment, with digests (prereg/design/config), `atlas_class`, `validity_state` | 736 POSITIVE, 121 FAILED, 43 NEGATIVE, 26 NULL, 49 INCONCLUSIVE, 369 PLANNED, 905 UNKNOWN |
| attempt / segment | 2,377 / 3,582 | executions of an experiment | |
| campaign / idea | 70 / 54 | grouping; proposed ideas | |
| conclusion | 600 | verbatim dispositions with source locator; supersession chain | PASS 69; failure-like: CAPABLE_NEGATIVE 36, NULL 26, FAIL 25, KILL 18, INDETERMINATE 24, INCONCLUSIVE 13, UNDERPOWERED 12 |
| defect | 221 | engine/campaign defects by category and severity | SCIENCE_DEFECT 25 (11 critical); instrument failures live here |
| edge | 5,693 | typed lineage, with relation, lineage_kind, basis, confidence and source | DEFORMATION_OF 2,370; COORD_PRESERVING 529; TESTS 570; CONTROL_OF 300; ANALOGUE_OF 124; TRANSPLANT_OF 24; CONTRADICTS 0; EXPLAINS 1 |
| signal | 195 | rule-derived flags | CALIBRATION_SPECIMEN 40, NULL_WITH_TELEMETRY 33, CROSS_ENGINE_LINEAGE 21, INSTRUMENT_FAILURE_CLUSTER 18, CONCLUSION_CHANGED 18 |
| **proposition** | **10** | statement, kind, scope, confidence (+basis), known_confounds, mechanisms[], untested_predictions[], supersedes, status, review cadence | kinds: 6 `distinction`, 2 `constraint`, 1 `assumption`, 1 `mechanism_claim`; all OPEN |
| **proposition_evidence** | **7** | proposition -> entity, relation, weight, verbatim, source locator, method | relations in use: SUPPORTS 5, SHARPENS 1, SCOPES 1 |
| **blind_spot** | **7** | assumption, engines_checked[], engines_holding[], counterexamples[], detection_basis, anti_experiment, status | 5 COMMISSIONED, 2 OPEN. This is the "assumption repeated across engines" object |
| primitive | 20 | named computational primitives (definition, operationalisations, measured_by, detection_status) | 6 are UNMEASURED (error_correction, partial_heredity, reproductive_closure, temporal_gating, write_authority, ...); "Needs ATLAS-39" |
| primitive_use | 4,249 | primitive x entity | all 4,249 rows are state PRESENT; absence is never recorded |
| combination | 190 | primitive sets with verdict | TESTED 89, UNEXPLORED 85, SUGGESTED_BY_EVIDENCE 16; BARREN and FALSIFIED_INDIRECTLY defined but unused |
| experiment_score | 92 | policy-weighted score; components include novelty, causal_discriminability, prior_failure_density, orthogonality | an existing search-direction policy (policy_version 2 rows) |
| ecosystem / ecosystem_reference | 365 / 870 | external systems catalogue | |
| vocab | 140 | controlled vocabularies (fact_kind, edge_relation, evidence_relation, proposition_confidence, validity, combination_verdict, signal_kind, ...) | reuse these terms; do not invent parallel ones |

Views: v_theory_frontier (proposition x evidence counts), v_manifest, v_measurement_names,
v_shape_inventory, v_edge_dangling, v_coverage, v_writers, v_local_only.

Failure-bearing experiments by engine:
- vivarium 96 of 1,242
- npe 70 of 276
- sfe 20 of 57
- theseus 3 of 97
- aether 1 of 18
- archaeon.frontier 0 of 422
- workgraph 0 of 102
- cosmos 0 of 10. Cosmos's EXP-01/02 negatives are not yet harvested as failures.

### 1.2 Pan (schema `pan`; owner: Pan)

| object | population | retrieval interface |
|---|---:|---|
| artifact | 421,366 (fs 341,502, git 77,721, comms 2,109, moonshot 34) | `python -m pan search/similar/pivot/refs/cochange` |
| chunk + tsvector | 408,916 | full-text (`--mode fts`) |
| embedding (bge-small, 384) | 408,916, HNSW (m=32, ef_construction=200) | vector; M2 exact, other hosts pgvector (recall@10 0.94 at ef 200 on real queries) |
| doc_embedding (Qwen3-Embedding-0.6B, 512) | 62,575, HNSW | document neighbours, pivot NEAREST HERE |
| link | 46,554 | `refs PATH` (who cites / what is cited) |
| commit + commit_file | 13,627 / 148,917 | `cochange PATH`, lineage |
| frontier_item / hf_model | 8,827 / 1,580 | `frontier search/like/models` |
| Iceberg pan_atlas.* | 35 tables, 143,139 rows (harvest_id 1..364) | analytical copy of the Atlas record, time-travel per harvest pass |
| run | 193 | provenance of every Pan job |

Measured limits that matter here:
- hybrid retrieval recall@10 is 0.765 on 200 independent queries (bar 0.80);
- a retrieved hit is a POINTER, never evidence (pan-search skill, s1).

### 1.3 Hades (CHIASMA; owner: Hades)

- Hades's positive/shadow representation lives inside an engine. A CHIASMA organism carries
  K = (P, N, U, L) inside synthetic Paradigm Worlds; there is no program-wide store.
- State as of 2026-10-10:
  - E1's primary claim failed.
  - Dev-only evidence (not results): a compressed failure shadow beats raw, counterfeit
    and no failure memory on PW-D, 8-10/10 seeds.
  - Hades recommends KILL for O4 and keeping D1 (factored geometry) and D2
    (compressed shadow) for fresh preregistrations.
- The usable connection points are CHIASMA's conventions, not its data:
  - matched controls: same bytes, compute, observations and query workload;
  - the counterfeit-shadow control (O3R, random masks of the same size);
  - WT-0 known-answer gating;
  - RSO receipts: canonical JSON without floats, an append-only ledger, and
    three-field verdicts (EXECUTION / AUTHORITY / OUTCOME).

## 2. Gaps (each tied to a measurement above)

| # | gap | evidence | consequence |
|---|---|---|---|
| G1 | Abstraction rate | 41,784 facts vs 10 propositions; 7 evidence links | the record cannot answer "what do we know" |
| G2 | No contradiction structure | 0 CONTRADICTS edges, 1 EXPLAINS; every proposition OPEN | competing interpretations cannot be represented as competing |
| G3 | No equivalence with witness | equivalence-like edges are naming/transform relations (COORD_PRESERVING 529, SAME_MEASUREMENT_AS); none says "A and B behave the same under intervention suite S" | "is this mechanism new?" has no store and no instrument |
| G4 | Absence never recorded | primitive_use: 4,249 PRESENT, 0 ABSENT/NEGATIVE | negative space over primitives is invisible; UNEXPLORED combinations are computed from silence |
| G5 | Negative results under-harvested | Cosmos 0 failures of 10; archaeon.frontier 0 of 422 | the cross-engine recurrence question (directive s1) is unanswerable from the current index |
| G6 | Access is unenforced | every program session connects as `postgres` (superuser; bypasses RLS); 0 tables with RLS; Pan's index holds 271 artifacts (796 chunks) with sealed/holdout-looking paths | blindness rests on convention; search amplifies any exposure |
| G7 | Instrument for distinctness absent | no calibrated evaluator exists | any "redirects search" claim would rest on an uncalibrated judge |

## 3. COMPUTATIONAL_DISTINCTION: proposal (Atlas owns; Pan proposes)

**Finding.** Atlas already has the object.
- `atlas.proposition` with `kind = 'distinction'`: 6 rows, e.g.
  - P-copy-not-heredity;
  - P-persistence-not-self-maintenance;
  - P-task-competence-not-mechanism;
  - P-selection-not-search.
- Three of the directive's s7 examples correspond to these rows.

A competing table would split one concept in two. The proposal is therefore an EXTENSION
keyed by `proposition_id` that holds the fields a distinction needs beyond a proposition.

PROPOSAL file: `roles/Pan/docs/sagacity/proposals/atlas_distinction_detail.sql` (not applied).

Field mapping (directive field -> where it lives):

| directive field | existing column | new column (atlas.distinction_detail) |
|---|---|---|
| distinction identifier | proposition.proposition_id (kind='distinction') | -- |
| computational property A / B | -- | property_a, property_b (text; each optionally a primitive_id) |
| observed discriminating behavior | -- | discriminating_behavior |
| experimental conditions | proposition.scope (free text) | conditions (jsonb: world family, intervention protocol, budget) |
| supporting / contradicting evidence | proposition_evidence (relation SUPPORTS / CONTRADICTS / SCOPES / SHARPENS / CONFOUNDS) | -- (reuse) |
| mechanism or substrate scope | proposition.scope, proposition.mechanisms[] | substrate_scope[] (engine_ids / world families tested) |
| known confounds | proposition.known_confounds | -- |
| uncertainty | proposition.confidence (+ confidence_basis), vocab includes CONTESTED | uncertainty_note; generalization ('UNKNOWN' default) |
| minimal witness | -- | witness_ref (entity or source locator), witness_sha256 |
| proposed discriminating experiment | proposition.untested_predictions[] | discriminating_experiment (text + optional idea_key) |
| evidence lineage hashes | proposition_evidence.source_id -> source.file_sha256/commit_sha | lineage_digest (sha256 over the sorted evidence source hashes, recomputable) |
| visibility classification | -- | access_class (Pan's classes, s6) |

Rules the proposal encodes:
- A row may exist with zero SUPPORTS links. It is then `confidence = UNTESTED`, which
  is honest.
- `lineage_digest` is recomputed by a query. A mismatch means the evidence set changed
  under the claim.
- Promotion to a universal proposition is a separate act: a new proposition row with
  `supersedes`, never an in-place edit.

## 4. FAILURE-BOUNDARY representation: proposal (Hades and Atlas own; Pan proposes)

Mapping the directive's six kinds onto what exists:

| kind | exists today as | missing |
|---|---|---|
| OBSERVED_FAILURE | conclusion (FAIL / KILL / NULL / CAPABLE_NEGATIVE / UNDERPOWERED); experiment.atlas_class FAILED / NEGATIVE / NULL; defect SCIENCE_DEFECT; fact layer OBSERVED | a link from the failure to the ASSUMPTION it implicates |
| PROPOSED_FAILURE_MECHANISM | proposition kind `constraint` (P-accessibility-cliffs, P-heredity-bootstrap-barrier); blind_spot.assumption | explicit mechanism -> failure links with status |
| SUPPORTED_EQUIVALENCE_CLASS | nothing (see G3) | class membership with an intervention-suite witness |
| KNOWN_BOUNDARY | proposition_evidence relation SCOPES (1 row); proposition.scope text | the condition where support ends, as data |
| UNRESOLVED_SIMILARITY | signal CROSS_ENGINE_LINEAGE / REPEATED_WEAK_EFFECT; identity_collision (names, not mechanisms) | "these two may be the same; here is the experiment that would tell" |
| UNTESTED_REGION | combination verdict UNEXPLORED (85); signals RARELY_CROSSED / VISITED_ONCE | reachability: unexplored vs inaccessible |

PROPOSAL file: `roles/Pan/docs/sagacity/proposals/boundary.sql` (not applied).

It defines one sparse table `boundary` (kind in the six), plus `boundary_member` and
`boundary_evidence`. Every non-UNTESTED row must cite an experiment, attempt, conclusion
or source.

The schema itself enforces "Do not infer causal equivalence from embedding similarity":
- `basis` must be one of DECLARED / INTERVENTION_WITNESS / ATLAS_DERIVED;
- `SUPPORTED_EQUIVALENCE_CLASS` requires `basis = INTERVENTION_WITNESS` and a
  `witness_ref`;
- a similarity score may populate only UNRESOLVED_SIMILARITY, never a supported class.

Placement: in schema `atlas` if Atlas adopts it. Hades's CHIASMA shadow is an engine-internal
representation. Hades decides whether CHIASMA reads (consumes) boundaries; it never writes
them into Atlas on Atlas's behalf.

**Cross-engine recurrence (the directive's addition).** The question "which computational
assumptions have repeatedly produced the same failures across otherwise unrelated engines"
becomes a query once two links exist:
- failure -> assumption (boundary_member, kind PROPOSED_FAILURE_MECHANISM, entity =
  blind_spot or proposition);
- assumption -> engines holding it (blind_spot.engines_holding).

The proposal includes the view `v_assumption_failure_recurrence`. Per assumption it gives:
- the count of distinct engines with an OBSERVED_FAILURE linked to it;
- of those, the count in engines that do NOT share its world family. Unrelatedness is
  approximated by world_family, a stated proxy that can be overturned.

Today the view would return almost nothing, because of G5 (failures under-harvested) and
G1 (no links). That emptiness is itself the measurement.

## 5. Retrieval interfaces across the fleet

| need | interface today | after this work |
|---|---|---|
| find documents and passages | `pan search` (hybrid), `similar`, `frontier like` | same, with an access-class filter by caller clearance (s6) |
| one screen around an artifact | `pan pivot` | same; pgvector path works from any host |
| lineage / citations | `pan refs`, `cochange`; atlas.edge | same |
| structured facts | SQL on atlas.*; Iceberg pan_atlas.* | MCP `atlas_facts` (read-only, filtered, provenance-carrying; MCP_INTERFACE_PROTOTYPE.md) |
| distinctions / boundaries | atlas.proposition (+ proposal tables) | read via MCP once Atlas adopts the proposals |

## 6. Security and blindness design (Pan owns the mechanism; the operator owns grants)

### 6.1 Classes

Classes are separate from Atlas's location-"visibility". The column is `access_class`.

| class | meaning | example |
|---|---|---|
| PROGRAM | readable by every seat (anything on main is already this) | most artifacts |
| BURNED_HOLDOUT | was meant to be blind, is now exposed; readable, but excluded from GENERATOR retrieval so search does not amplify it | prometheus/cosmos/holdout/sealed_spec*.json, c3_holdout_D/sealed_spec_D.json (declared EXPOSED by the D2 firewall) |
| EMBARGOED_OUTCOME | results withheld from authors until a reveal | receipts of a running blind evaluation |
| PRIVILEGED_CRITIQUE | reviews not to be shown to the reviewed author before adjudication | adjudication drafts |
| SEALED | must never enter Pan at all. Index-time refusal, not a filter | holdout plaintext, keys, salts (D2 keeps these on M1 outside git) |

### 6.2 Inheritance rule (the directive's rule, made mechanical)

A derived object's effective class is the MOST RESTRICTIVE class among its inputs.
Declassification happens only through a recorded decision: who, when, why, review
reference, and the before and after classes.

Applies to:
- chunks, embeddings and document vectors (inherit from their artifact);
- links (most restrictive of the two endpoints);
- Iceberg snapshots and cached results (most restrictive of their rows);
- summaries (most restrictive of the sources they cite);
- query logs (most restrictive of the results they returned).

### 6.3 Roles and enforcement

- **Roles (design; no grant made).**
  - `pan_generator`: PROGRAM only.
  - `pan_evaluator`: PROGRAM plus EMBARGOED_OUTCOME of evaluations it runs.
  - `pan_adjudicator`: adds PRIVILEGED_CRITIQUE.
  - `pan_holdout_custodian`: the only role that may see holdout material; its keys
    stay outside Pan.
  - `pan_infrastructure`: Pan's own maintenance, with no retrieval surface.
- **Enforcement layers.**
  1. Index-time refusal of SEALED, by path rules and content markers.
  2. Postgres RLS on the artifact table, with child tables (chunk, embedding,
     link) using `EXISTS` on the parent's class. Inheritance is then a join, not a
     copied column that can drift.
  3. Non-superuser login roles. RLS is void while every session is `postgres`.
  4. Outside Postgres (lake files, Iceberg data files, caches): physical separation by
     class directory plus filesystem ACLs; the MCP server never reads the lake.
- **Pan's retrieval code now takes a `clearance` parameter** (PAN-42, migration 014).
  Until RLS is granted, this is defence in depth and honest about its limit: a caller
  holding `postgres` can bypass it, and the design says so.
- **Proof of mechanism, done.** RLS with inheritance-by-EXISTS was demonstrated in a
  throwaway database using the existing non-superuser role prometheus_read. No new roles
  were created: roles are cluster-global, and the directive grants no authorization
  change. Controls `roles/Pan/reports/controls/ACCESS_20261011T100600Z.json`, PASS 12/12:
  - generator clearance: full-text, vector (pg and local backends, querying with a burned
    chunk's OWN vector), pivot and refs never return the 4 BURNED_HOLDOUT files;
  - evaluator clearance: the same queries do return them, so the check is not vacuous;
  - the 119 refused credential-shaped files hold 0 chunks;
  - an unknown role fails closed;
  - under RLS a hidden artifact's chunk is invisible directly and through a join;
  - the superuser bypasses RLS.

### 6.4 Applied in Pan on 2026-10-11 (migration 014, Pan's own schema only)

- `pan.access_class`, `pan.clearance`, `pan.access_rule` and `pan.declassification`;
  `pan.artifact.access_class` and `access_rule`.
- Rules:
  - `C-cosmos-burned-holdout` classified 4 files;
  - `R-credential-file` refused 119 artifacts (108 filesystem entries whose contents
    were never read, plus 11 committed files) and purged 11 chunks and 7 document
    vectors.
- Retrieval clearance comes from `PAN_CLEARANCE` or the MCP server; the default is
  `generator`, the most restrictive.
- Schema proposals verified in a throwaway database:
  `roles/Pan/reports/controls/PROPOSALS_20261011T100108Z.json`, PASS 15/15.

## 7. Ownership (as directed) and the boundary of each

| seat | owns | reads |
|---|---|---|
| Pan | catalog, indexes, retrieval, provenance, transport, access-class mechanism, MCP read surface | everything it is cleared for |
| Atlas | facts, propositions, distinctions (adoption of s3), primitives, combinations, boundary adoption (s4) | Pan retrieval |
| Hades | failure boundaries' experimental validation; CHIASMA dual mesh | boundaries (consumer) |
| Cosmos | first test environment for NEGATIVE_SPACE_EVALUATION | MCP read surface (generator clearance) |
| Nyx | attacks on distinctions and equivalence claims | evaluator clearance |
| Harmonia | adjudication of promoted claims | adjudicator clearance |

## 8. What this map does not establish

- That any distinction in Atlas is true. The populations measure bookkeeping, not
  science.
- That the six-kind boundary table is the right decomposition. It is a proposal for
  Atlas and Hades to accept, change or reject.
- That access classes are enforced. Until non-superuser roles and RLS are granted, the
  filter is cooperative.
