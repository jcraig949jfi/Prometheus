---
name: Prometheus Concept Map (living index)
purpose: Single navigable index for the 6 core strategies James named on 2026-04-23. Every sprawling document, scratch artifact, and substrate primitive should be findable from this map within 2 clicks. Cold-start Harmonia / external reviewer / future-James should be able to answer "where do we keep our X?" by scanning here.
status: SKELETON v0.1 — sessionC 2026-04-23 first pass; section-owner recruitment open per agora DIRECTIVE_AND_RECRUITMENT message. Canonical-artifact citations and sprawl-observations to be filled by section owners.
maintenance: living document. Each section owner edits their axis; cross-axis updates need post on agora:harmonia_sync. Index of axis owners maintained at the bottom.
north_star: "getting faster at getting better, leveraging all information"
---

# Prometheus Concept Map

This document is a **structural index** of the project's six core strategies, not a re-statement of any of them. Each section names canonical artifacts (where the concept lives), sprawl observations (where it has leaked or duplicated), and consolidation candidates (deduplication moves). The goal is to make every concept findable in two clicks from this page.

**Important:** the maintenance discipline is *don't add doctrine here*. Each axis section is meta — it points at the canonical artifacts that ARE the doctrine. If you find yourself writing definitions in this map, the definition belongs in the canonical artifact and this map should just reference it.

---

## Foundations (pre-axial — every axis depends on these)

**Rationale** (sessionA 2026-04-23, per axis-4 sprawl observation): SHADOWS_ON_WALL and the landscape charter are not axis-4 concepts even though sessionC's first-pass skeleton listed SHADOWS_ON_WALL in Axis 4. They are pre-axial — Axis 1's pattern library cites them (Pattern 6 = "verdicts are coordinate systems" IS a SHADOWS corollary); Axis 2's tensor measurements are shadows-per-SHADOWS; Axis 3's symbol promotion discipline operationalizes SHADOWS tier levels; Axis 5's frontier-triage rests on the charter's "domains are projections not territories"; Axis 6's tools implement shadow-counting (N lenses = N shadow-tier gates). Every axis owner will reach up into this section. Foundations stay here so no axis "owns" the foundational frame.

**Canonical artifacts (minimal; add sparingly):**
- `docs/landscape_charter.md` — project reframe: domains are projections, open problems are shortcut requests, terrain is the product not the answer. Pre-axial for every axis.
- `harmonia/memory/symbols/SHADOWS_ON_WALL.md` — foundational frame: every measurement is a shadow; tiers {shadow, surviving_candidate, coordinate_invariant, durable, map_of_disagreement}; silent single-lens claims forbidden. All promoted patterns compose under it.
- `harmonia/memory/pattern_library.md` §Pattern 6 — verdicts are coordinate systems (SHADOWS's earliest specific-form in the pattern library).
- `user_prometheus_north_star.md` (memory) — compressing coordinate systems of legibility, not laws. Novelty is the reward; watch for reward-signal capture.
- `docs/long_term_architecture.md` — 5-layer substrate architecture (Data / Measurement / Discipline / Symbolic / Replication). Every axis inhabits some layer of this architecture.
- `harmonia/memory/restore_protocol.md` (v4.3) — operating-disposition section that frames all work (rigorous + novelty-seeking + compression-seeking posture).

**Discipline:** Foundations section is NOT itself an axis — it has no separate section-owner, no sprawl audit, no consolidation candidates. Foundations artifacts are read-only for concept_map purposes; edits to them happen in their home files. This section exists purely to avoid the Pattern-17 failure mode where a foundational frame gets incorrectly scoped as one axis's concept.

---

## Axis 1 — Falsification battery

**One-line:** All findings assumed false until every kill path exhausted; pattern library + null protocols + retraction discipline are the substrate's antibodies against false positives.

**Canonical artifacts:**
- `harmonia/memory/pattern_library.md` — Patterns 1-30 (recognition rules, anchor cases, graded severity)
- `harmonia/memory/symbols/PATTERN_30.md` — algebraic-identity coupling (graded 0-4)
- `harmonia/memory/symbols/PATTERN_20.md` — pooled-vs-stratified projection
- `harmonia/memory/symbols/PATTERN_21.md` — null-model selection
- `harmonia/memory/symbols/protocols/null_protocol_v1.md` — 5 claim classes + stratifier prescriptions
- `harmonia/memory/symbols/NULL_BSWCD.md` (+ `NULL_PLAIN`, `NULL_BOOT`, `NULL_FRAME`, `NULL_MODEL`) — null operator family
- `harmonia/memory/protocols/block_shuffle.md` — block-shuffle protocol
- `harmonia/sweeps/` — automated sweep modules (pattern_30.py, pattern_20.py, pattern_19.py, runner.py, retrospective.py)
- `harmonia/sweeps/OVERRIDE_PROTOCOL.md` — graded override discipline
- `feedback_falsification_first.md` (memory) — north-star epistemology
- `feedback_battery_calibration.md` (memory) — battery as living instrument
- `feedback_ensemble_invariance.md` (memory) — 3-tier hierarchy

**Sprawl observations** *(Harmonia_M2_auditor first-pass, 2026-04-23):*

1. **Pattern library mixes promoted vs draft tiers in one file.** `pattern_library.md` has Patterns 1-30, but only ~10 are formally promoted (full-pattern). Drafts (e.g., DRAFT Patterns 23-29 around line 832, Pattern 30 itself which is "DRAFT promoted to strong advisory") sit inline with promoted patterns. Cold-start Harmonia cannot distinguish doctrine from heuristic at a glance — has to read each pattern's status block. Pattern-17 (language/organization) symptom.

2. **null_protocol_v1.md amendments stack inline.** v1.1 PATTERN_STRATIFIER_INVARIANCE amendment (sessionD reaudit_10) AND the auditor F013:P020 anchor block AND the v1.1 PATTERN_BSD_TAUTOLOGY amendment all live as appended sections in the same MD as v1.0. The frontmatter version is "1.1" but content is multi-amendment-deep. Future amendments would compound the drift. VERSIONING.md Rule 3 (immutability of promoted versions) is not being applied to protocols MDs — possibly intentional (protocols ≠ symbols) but worth surfacing.

3. **Audit results scattered across `cartography/docs/` with no index.** My 5 audits this session (audit_F041a_euler_product_deflation_results.json, audit_F042_..., audit_F044_framebased_resample_results.md, audit_F044_rank4_lmfdb_selection_results.md, audit_F045_multiple_testing_and_independence_results.json) live alongside dozens of older audit artifacts with no navigation page. "Which F-IDs have been audited and when, what was the verdict, what was the tensor-mutation recommendation?" requires `glob + grep` not a single read. Pattern-17 sprawl.

4. **`decisions_for_james.md` mixes falsification entries with non-falsification.** F044 retraction, F042 OBSOLETE close, F045 PARTIAL_CONFOUND, F041a SIGN_INVERSION are all in there alongside non-audit decisions (T4 materialization, F011 tier changes, etc.). A falsification-specific filtered view does not exist — auditor or future James must scan-for-keyword.

5. **LINEAGE_REGISTRY (Pattern 30 metadata) lives in Python code.** `harmonia/sweeps/retrospective.py::LINEAGE_REGISTRY` is the source-of-truth for per-F-ID `algebraic_lineage` declarations (F011 non_correlational, F013 algebraic WARN, etc.). Discoverability gap — future Harmonia looking for "what's F045's lineage classification" has to grep Python. sessionA's substrate-debt-closure entry (decisions_for_james 2026-04-22) names this but the registry itself isn't surfaced in concept_map readable form.

6. **Override events have no aggregated log.** `OVERRIDE_PROTOCOL.md` defines the 4 legitimate override reasons + audit discipline; each sweep emits a sync event when an override fires; but no central log shows "across the substrate's history, what was overridden, when, why, by whom". Substrate-debt for any future audit of override patterns.

7. **Self-dissent events not formally logged.** `feedback_self_dissent.md` (memory) defines the discipline. This session demonstrated it 4-5 times (sessionA twice on Y_IDENTITY framing; auditor once on Y_IDENTITY endorsement; sessionB once on 2-seed convergence claim; possibly more). No central log; events live in sync stream + decisions_for_james entries. A self-dissent ledger would be a useful substrate-discipline metric (high self-dissent rate = healthy; low rate = either calibrated already or hiding errors).

8. **Track D replication status not indexed by symbol.** Zaremba achieved cross-implementation Track D byte-equivalence this session (sessionC re-implementation of sessionB's measurement). EPS011@v2 has `independent_unfolding_audit: SURVIVES` annotation per its own MD. F011 has Track D as a deferred task. No central "Track D status by promoted symbol" page; individual symbol MDs are the source-of-truth which makes cross-symbol queries hard.

**Consolidation candidates** *(Harmonia_M2_auditor first-pass, 2026-04-23):*

1. **`harmonia/memory/audit_results_index.md`** — **SHIPPED 2026-04-23** (Harmonia_M2_auditor; sync `1776912005761-0`). Auto-generated table via `harmonia/runners/regen_audit_results_index.py`. 41 audit-like artifacts indexed (audit_*, reaudit_*, wsw_*, *_investigation_*, pattern_*_audit). Cross-F-ID chronological view; complementary to sessionB axis-5 #2 inline annotations in `build_landscape_tensor.py` (sync `1776911782623-0`). **Closes sprawl #3.**

2. **Pattern library tier separation.** **SHIPPED 2026-04-23 (lightweight variant)** (Harmonia_M2_auditor). Auto-generated tier-index table inserted near top of `pattern_library.md` via `harmonia/runners/regen_pattern_library_tier_index.py`. 29 patterns classified into FULL (3) / ADVISORY (1) / MATURE (15) / DRAFT (7) / META (3) per `**Status:**` markers + heuristic fallback. Cold-start Harmonia can read the table first, drill into specific patterns by tier. Heavier per-pattern frontmatter still TBD (would close sprawl #1 fully); this is the v1 navigation aid. **Partially closes sprawl #1.**

3. **`harmonia/memory/lineage_registry_view.md`** — **SHIPPED 2026-04-23** (Harmonia_M2_auditor; sync `1776911475791-0`). 19 F-IDs surfaced from `LINEAGE_REGISTRY` in `retrospective.py` with type distribution + per-type sub-tables + pending-audit pointers. Source-of-truth discipline preserved (NEVER edit MD; edit Python + regenerate). **Closes sprawl #5.**

4. **Self-dissent ledger sidecar** — **DESIGN + SEED SHIPPED 2026-04-23** (Harmonia_M2_auditor; sync `1776912454676-0` style). Design + seed at `harmonia/memory/dissent_ledger_design.md` with schema (project-wide HASH at `agora:dissent_ledger`, mirrors sessionA's `ANCHOR_PROGRESS_LEDGER` API style), 6-event seed from this session's v2-thread self-dissents (4 agents), composition map, implementation path. Module implementation deferred — sessionA owns the sidecar architecture (`agora/symbols/anchor_progress.py`); cleanest path is either a parallel module or extension. **Partially closes sprawl #7** (design-shipped; module pending).

5. **null_protocol versioning discipline.** **DESIGN SHIPPED 2026-04-23** (Harmonia_M2_auditor; sync `1776915476473-0` style). Design at `harmonia/memory/symbols/protocols/PROTOCOL_VERSIONING.md` proposing forward-only convention: cap inline amendments at v1.1; next amendment creates `_v2.md` mirroring `FRAME_INCOMPATIBILITY_TEST@v1 → @v2` precedent; downstream symbol references decided at next symbol-version bump. 5 open questions for team review (Q1-Q5). Backward-compatible: no retroactive repair needed. **Closes sprawl #2 as DESIGN; enforcement awaits team concurrence + next-amendment trigger.**

6. **Falsification-only filter on `decisions_for_james.md`** — **SHIPPED 2026-04-23** (Harmonia_M2_auditor; sync `1776912908730-0` style). Auto-generated tagged index at `harmonia/memory/decisions_for_james_index.md` via `harmonia/runners/regen_decisions_index.py`. 32 entries classified into 7 tags (falsification 24 / methodology 9 / milestone 7 / promotion 7 / external_review 6 / infrastructure 4 / other 5; multi-tag entries normal). Falsification-filter section first, full tagged index second, tag-counts summary. **Closes sprawl #4.**

7. **Track D status sidecar** — adapt ANCHOR_PROGRESS_LEDGER schema for tracking cross-implementation byte-equivalence per promoted symbol. Schema: `symbol@version, dimension (per long_term_architecture §Layer 5), status, replicating_agent, byte_match_at_resolution`. Closes sprawl #8. Composes naturally with sessionA's prototype.

8. **Override-events log** — Redis stream at `agora:override_log` mirroring sweep override events. Aggregator script generates `override_log_view.md`. Closes sprawl #6.

**Cross-axis ties:** consolidation #4 (self-dissent ledger) overlaps with axis 6 (tool building); consolidation #1 (audit results index) overlaps with axis 5 (research frontiers — audit results are frontier-state evidence); consolidation #7 (Track D sidecar) overlaps with axis 3 (symbolic storage). All three are sidecar-pattern instances per ANCHOR_PROGRESS_LEDGER.

**Proposed owner:** Harmonia_M2_auditor — **CLAIMED** 2026-04-23 per agora `1776910xxx-x` CLAIM (this iteration).

---

## Axis 2 — Mapping (tensor + coordinate systems)

**One-line:** The product is the map; F-IDs × P-IDs build a tensor whose invariance pattern IS the substrate's compression of mathematics. Cells encode verdicts; rows encode features; columns encode coordinate systems.

**Canonical artifacts:**
- `harmonia/memory/build_landscape_tensor.py` — tensor source of truth (FEATURES, PROJECTIONS, INVARIANCE, edges)
- `harmonia/memory/TENSOR_REDIS.md` — Redis mirror protocol
- `harmonia/memory/coordinate_system_catalog.md` — P-ID roster with tautology profiles (42 projections)
- `harmonia/memory/axis_class_tags.md` — AXIS_CLASS@v1 first-pass tagging (sessionB 2026-04-22, complete v1.0)
- `harmonia/memory/symbols/AXIS_CLASS.md` — controlled vocabulary
- `cartography/viewer/` — Cartographer HTML viewer + Redis poll (server.py + index.html + **README.md** with features/launch/API/requirements; Charon 2026-04-18)
- `cartography/docs/` — per-cell metadata, wsw_*.json result schemas
- `harmonia/memory/symbols/Q_EC_R0_D5.md` — canonical dataset symbol (rank-0 EC slice)
- `harmonia/memory/NAMESPACE.md` — P-ID allocation
- `agora/tensor/` — Python helpers for tensor read/write/mirror
- `harmonia/memory/abandon_log.md` — abandoned tensor-mapping experiments (e.g., Geometry 1 retraction); historical context for current shape decisions
- `harmonia/memory/TENSOR_VIEWS.md` — three-view comparison (git source / Redis mirror / Cartographer viewer); navigation doc (sessionC 2026-04-23)
- `feedback_tensor_admission_test.md` (memory) — 5-gate admission test
- `feedback_mpa_is_construction.md` (memory) — MPA is coordinate construction not law discovery

**Sprawl observations (sessionC 2026-04-23, axis-2 strawman owner per partition with sessionA):**

*Duplication:*
- **P-ID metadata lives in 3+ places.** `coordinate_system_catalog.md` (rich prose per-P-ID with tautology profiles), `axis_class_tags.md` (sessionB v1.0 — class tags), `build_landscape_tensor.py` PROJECTIONS list (canonical names + SQL/code reference), per-P-ID frontmatter in MD where applicable. No single canonical P-ID page; cold-start needs to glob across 3 files to know "what is P028?"
- **Tensor state lives in Python source + Redis mirror + cartography viewer.** `build_landscape_tensor.py` is git-source-of-truth; `agora.tensor` mirrors to Redis (sub-ms reads); `cartography/viewer/` polls Redis every 5s. Source-of-truth is git (per OVERVIEW.md), but viewer is the human-facing artifact, and Redis is the agent-facing artifact. Three views, one truth — but no document explains which one to read for what question.
- **Catalog-vs-coordinate_system distinction.** `harmonia/memory/catalogs/` = problem-lens catalogs (Axis 4 substrate). `harmonia/memory/coordinate_system_catalog.md` = P-ID roster. Both called "catalog" — semantic collision. Cold-start may conflate.

*Drift:*
- **AXIS_CLASS tagging coverage is partial.** `axis_class_tags.md` v1.0 covers 42 P-IDs (36 CONFIDENT + 3 explicitly-null infrastructure + 3 CONFIDENT compound after my 2026-04-23 second-pass). But P-IDs added since the tagging pass (e.g., any new P101+ entries) won't have tags. No automated invariant that "every promoted P-ID has an AXIS_CLASS tag in axis_class_tags.md."
- **F-ID ↔ tensor cell ↔ catalog cross-references partial.** Tensor cell (F, P) → verdict +2/+1/0/-1/-2 lives in `build_landscape_tensor.py` INVARIANCE dict. Catalog frontmatter (e.g., zaremba.md) has `cnd_frame_status` etc. F-ID prose lives in tensor builder FEATURES list. Cross-reference walking is manual per artifact.
- **Cartography viewer feature set vs README discoverability.** Viewer at `cartography/viewer/server.py` includes features (hover metadata, force-directed graphs, hot-cell shading, gap banner) discoverable only via running it. No README for the viewer that lists features + their entry points + their data dependencies.

*Orphan:*
- **Reverse-references in tensor (F-ID → which papers cite it) live in `cartography/docs/edges_*.json` from gen_07 lit-diff but not surfaced from a single artifact.** Future consumer of "which lit-diff entries touch F011" greps the JSON.
- **TENSOR_REDIS.md describes the mirror protocol but doesn't document the per-key TTL / eviction discipline.** If Redis evicts a tensor key, what's the recovery? Procedure isn't explicit.
- **`harmonia/memory/abandon_log.md` references abandoned tensor-mapping experiments** (e.g., earlier rank-completion attempts before Geometry 1 retraction). Not in the canonical Axis-2 list above, but it's mapping-axis history that shapes current decisions. Should be cross-referenced.

**Consolidation candidates (sessionC 2026-04-23):**

1. **Per-P-ID single canonical artifact.** Either: (a) split `coordinate_system_catalog.md` into per-P-ID MDs at `harmonia/memory/coordinate_systems/P0NN.md` with frontmatter `axis_class`, `tautology_profile`, `tensor_cells`, `linked_F_IDs`; OR (b) keep monolithic catalog but add a strict per-section frontmatter convention so structured-extraction works. Either resolves "where do I find what P028 is" sprawl. Prefer (b) for first pass — lower migration cost.

2. **Tensor view-of-truth doc.** Single MD `harmonia/memory/TENSOR_VIEWS.md` answering "what is git-source vs Redis-mirror vs viewer-rendered, and when do you use which?" Compose with TENSOR_REDIS.md (mirror protocol) and viewer README (features). Resolves the three-views-one-truth navigation gap.

3. **Rename `coordinate_system_catalog.md` → `projection_catalog.md`** to disambiguate from `harmonia/memory/catalogs/` (problem-lens catalogs). Cheap rename + sed fixes references. Pattern-17 fix.

4. **AXIS_CLASS tagging invariant + automation.** Either a sweep script `harmonia/sweeps/axis_class_coverage.py` that flags un-tagged promoted P-IDs, OR a frontmatter-validator that fires at PROBE_PROPOSED for any new P-ID. Closes the "what gets tagged when" drift.

5. **Tensor cell change-log.** Cell (F, P) verdicts evolve (e.g., F011 P024 +1 → -1 demotion). Currently tracked in agora messages + decisions_for_james.md, not in a single tensor-history artifact. A `harmonia/memory/tensor_changelog.md` or `agora.tensor.history` Redis stream would surface the evolution. Composes with sessionA Axis 4's ANCHOR_PROGRESS_LEDGER pattern (cells are the tensor-level analog of anchor-tier evolution).

6. **Cartography viewer README.** ~~Listing features / data deps / startup.~~ **ALREADY SHIPPED 2026-04-18 by Charon.** sessionC strawman missed it; verified. Cancel candidate.

7. **Cross-reference abandon_log.md from this section.** Add `abandon_log.md` to canonical artifacts above + brief one-liner. Mapping-axis history matters for understanding why current shape is what it is (Geometry 1 retraction example).

**Cross-axis hooks:**
- **Axis 1 (Falsification):** consolidation #5 (tensor cell change-log) is also a falsification-axis tool — auditor's tier-demotion records would naturally land there.
- **Axis 3 (Symbolic storage):** consolidation #4 (AXIS_CLASS coverage automation) is the same shape as my Axis 3 #7 (auto-render reverse-reference index from Redis sets) — both are "auto-derive metadata index from canonical store." Joint tooling.
- **Axis 6 (Tool building):** consolidations #2, #4, #5, #6 are all tool-building moves. Heavy overlap; sessionA's Axis 6 owner-pass should reference these.

**Proposed owner:** Charon (cartographer + tensor builder) — IDLE; **strawman drafted by sessionC 2026-04-23 iter-40** per recruitment-commitment fallback. If Charon arrives, accept as proper owner; sessionC's strawman is editable.

---

## Axis 3 — Symbolic storage (registry + immutability)

**One-line:** Compound primitives become first-class symbols with strict versioning + Redis mirror; immutability + provenance + content-addressing buys cross-session reproducibility and cross-instance equivalence checking. The discipline scales the substrate from "well-organized prose" to "queryable knowledge graph."

**Canonical artifacts:**
- `harmonia/memory/symbols/OVERVIEW.md` — executive rationale
- `harmonia/memory/symbols/VERSIONING.md` — five mandatory rules + lifecycle status (T2) + session manifest (T1)
- `harmonia/memory/symbols/INDEX.md` — promoted-symbol registry (currently 22 symbols; FRAME_INCOMPATIBILITY_TEST@v2 latest)
- `harmonia/memory/symbols/CANDIDATES.md` — Tier 1-4 candidate staging
- `harmonia/memory/symbols/<NAME>.md` — per-symbol canonical MDs (LADDER, NULL_BSWCD, CND_FRAME, FRAME_INCOMPATIBILITY_TEST, SHADOWS_ON_WALL, MULTI_PERSPECTIVE_ATTACK, PATTERN_*, etc.)
- `harmonia/memory/symbols/protocols/` — per-protocol symbols (null_protocol_v1, dataset_snapshot_v1)
- `harmonia/memory/symbols/external/` — external-standards artifacts (IUCr, OpenQASM, ngspice, CODATA)
- `agora/symbols/` — Python helpers (push, resolve, manifest, lifecycle, versioning)
- `harmonia/memory/architecture/definition_dag.md` — substrate-primitive spec (gen_11 prerequisite)
- `docs/long_term_architecture.md` §2.1 — idempotence + purity constraints (computation symbols)

**Sprawl observations (sessionC 2026-04-23, axis-3 owner):**

*Duplication:*
- **Three-layer overlap CANDIDATES.md ↔ INDEX.md ↔ per-symbol MDs.** CANDIDATES.md has full proposals; INDEX.md has one-liners; per-symbol MDs have canonical content. Promoted-symbol-stub-in-CANDIDATES (with MD link, per OVERVIEW.md convention) is the workaround. Convention applied for VACUUM/EXHAUSTION/SUBFAMILY/CND_FRAME/FRAME_INCOMPATIBILITY_TEST. Older promoted symbols may lack stubs. Cold-start landing on CANDIDATES.md may not realize a candidate has shipped if stub is missing.
- **VERSIONING.md amendment-stacking** — same pattern auditor flagged in Axis 1 for `null_protocol_v1.md`. VERSIONING.md content stacks v1 (initial discipline) → v2 (lifecycle status, T2) → v3 (session manifest, T1) inline. File-frontmatter version is unstable; future amendments compound the drift. Rule 3 immutability is for promoted-symbol `:def` blobs, not for protocols/discipline MDs — clarification gap.
- **OVERVIEW.md vs INDEX.md** at symbols/ root cover overlapping purposes — OVERVIEW is rationale + executive summary + tier-1 schema; INDEX is the registry table. Both describe symbol lifecycle in their own words. Drift risk if either gets edited without the other.

*Drift:*
- **Reverse-reference index in INDEX.md is partial.** "By reference" section has 11-12 entries; not every promoted symbol has reverse rows. CND_FRAME's references (SHADOWS_ON_WALL, PROBLEM_LENS_CATALOG, MULTI_PERSPECTIVE_ATTACK, PATTERN_20, PATTERN_30) were added at promotion; FRAME_INCOMPATIBILITY_TEST@v2 references not yet indexed. Stale-by-default unless promotion-author proactively backfills.
- **Promotion workflow is informal procedural knowledge.** Steps (draft MD → SYMBOL_PROPOSED on agora → second-reference accumulation → push to Redis → INDEX.md update → CANDIDATES.md stub → reverse-references) are discoverable only via OVERVIEW.md fragments + analogy with prior promotions + reading my CND_FRAME promotion sequence on agora. No single procedural artifact. Future authors may diverge.
- **Pattern symbols vs Pattern library entries — split criterion opaque.** PATTERN_20, PATTERN_21, PATTERN_30 are promoted symbols with MDs. Patterns 1-19, 22-29 live only in `pattern_library.md`. Why 20/21/30 got symbolized but Patterns 6 (verdicts are coordinate systems — foundational), 17 (language/organization — referenced 5+ times this session), 18 (uniform visibility — operationalized as VACUUM but Pattern itself unsymbolized), 19 (stale entries) didn't is unclear. Symbolization criterion belongs in OVERVIEW.md or pattern_library.md preamble.

*Orphan:*
- **External symbols** (IUCr CIF, OpenQASM, ngspice, CODATA at `harmonia/memory/symbols/external/`) are pinned by hash but not in INDEX.md "By type" tables. `long_term_architecture.md` describes them as "present but not yet integrated into the measurement layer." Either-or limbo: not promoted, not retired. Cold-start may discover the directory and not know how to use them.
- **agora.symbols Python module function index missing.** `agora/symbols/` ships push.py, resolve.py, manifest.py, lifecycle.py, etc. OVERVIEW.md mentions some helpers; CND_FRAME promotion required `python -m agora.symbols.push <path>` (memorized from my prior promotions). No `agora/symbols/__init__.py`-equivalent function index for "what helpers exist with what signatures."
- **SIGNATURE v1→v2 migration narrative scattered.** INDEX.md notes both versions promoted; specific migration story (what changed, why v2, how legacy v1 references compose) lives in MD Version history sections + agora messages. No bump-narrative artifact for tracking how each symbol's version number tells what story.
- **Methodology cluster has no graph view** (cross-axis with sessionA Axis 4 #2). CND_FRAME + FRAME_INCOMPATIBILITY_TEST + CONSENSUS_CATALOG + Y_IDENTITY_DISPUTE-enum + ANCHOR_PROGRESS_LEDGER + ANCHOR_AUTHOR_DIVERSITY (6 inter-referenced symbols/candidates) — each MD references the others; no single artifact maps cluster as a graph. Symptom of the same gap from Axis-3 (storage) and Axis-4 (exploration) perspectives.

**Consolidation candidates (sessionC 2026-04-23):**

1. **Create `harmonia/memory/symbols/PROMOTION_WORKFLOW.md`.** Single procedural artifact: 7-step workflow (draft → SYMBOL_PROPOSED → wait/iterate → push → INDEX update → CANDIDATES stub → reverse-references) + canonical examples (link to VACUUM as the prototypical promotion). Eliminates the "informal-procedural-knowledge" sprawl.

2. **Add `concept_axis: <N>` frontmatter field to every promoted symbol** (joint with sessionA Axis 4 #7). Enables grep-level axis queries (`rg "concept_axis: 3"` returns Axis-3 corpus). Cheap to backfill.

3. **Render methodology cluster graph as `cluster_methodology_cnd_fit_consensus.md`** (joint with sessionA Axis 4 #2). Cross-axis Axis 3 + Axis 4 candidate. Single MD with ASCII DAG + per-symbol one-liner + "what question does this answer?" Preserves individual MDs; cluster doc is purely navigational.

4. **Decide pattern-symbol promotion criterion explicitly.** Either (a) symbolize remaining FULL patterns (1, 6, 13, 14, 15, 16, 17, 18, 19) per parity with 20/21/30, OR (b) write explicit criterion in OVERVIEW.md naming what gets symbolized vs stays library-only. Current pattern (some symbolized, some not, no rule) is the failure mode.

5. **Bump VERSIONING.md to a new file (`VERSIONING_v3.md`) when next amendment lands**, OR adopt formal amendment-section convention (header `## v<N>.<M> AMENDMENT — <subject> (<date>)`) and stop bumping. Decision needed; current drift is unsustainable past v4-v5.

6. **External-symbols decision.** Either promote {IUCr, OpenQASM, ngspice, CODATA} as `external_symbol` type with INDEX.md row, OR explicitly mark `status: deferred_phase_2_external_integration` and link from OVERVIEW.md. Removes the limbo state.

7. **Auto-render reverse-reference index from Redis sets.** `symbols:refs:<id>` keys exist per OVERVIEW.md schema. A `agora/symbols/render_refs.py` script could generate the complete reverse-index MD on demand (cron-able, or run pre-promotion). Keeps INDEX.md "By reference" as a curated highlight; full index lives in queryable form. Pattern-17 fix.

8. **ANCHOR_PROGRESS_LEDGER deployment for symbol-side tracking** (joint with Axis 1 — substrate-debt about post-promotion anchor-tier evolution). The sessionA prototype (1776910494837 PROTOTYPE_COMPLETE) addresses this; reference from this section once landed in Redis.

**Cross-axis hooks:**
- **Axis 1 (Falsification):** Pattern-symbol-vs-library-entry decision (#4 above) is also a falsification-axis question (which patterns are gating discipline vs heuristic).
- **Axis 4 (Exploration):** consolidation #2 (axis-tagging frontmatter) and #3 (methodology cluster graph) are joint with sessionA's Axis 4 candidates #7 and #2 respectively.
- **Axis 6 (Tools):** consolidation #1 (PROMOTION_WORKFLOW.md) and #7 (render_refs.py) are tool-building moves that also serve Axis 6.

**Proposed owner:** sessionC (this session — recently shipped CND_FRAME@v1 + co-authored FRAME_INCOMPATIBILITY_TEST@v2 + ANCHOR_PROGRESS_LEDGER attestation) — **CLAIMED 2026-04-23 iter-39**. Sprawl + consolidation above.

---

## Axis 4 — Exploration techniques

**One-line:** Multi-perspective attack on open problems with committed-stance discipline + cross-disciplinary lens shelf + lens catalogs per problem; the methodology generates the FAIL-ANCHOR / PASS-ANCHOR / coordinate-invariant verdicts that drive substrate growth.

**Canonical artifacts:**
- `harmonia/memory/symbols/SHADOWS_ON_WALL.md` — foundational frame (every measurement is a shadow)
- `harmonia/memory/symbols/MULTI_PERSPECTIVE_ATTACK.md` — N-thread committed-stance methodology
- `harmonia/memory/symbols/PROBLEM_LENS_CATALOG.md` — per-problem catalog schema
- `harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md` (v2) — teeth test classifier
- `harmonia/memory/symbols/CND_FRAME.md` — convergent-on-measurement-divergent-on-framing FAIL anchor type
- `harmonia/memory/methodology_multi_perspective_attack.md` — procedure document with anchor cases (Lehmer, Collatz)
- `harmonia/memory/methodology_toolkit.md` — cross-disciplinary projection shelf (KOLMOGOROV_HAT, CRITICAL_EXPONENT, CHANNEL_CAPACITY, MDL, RG_FLOW, FREE_ENERGY)
- `harmonia/memory/catalogs/` — 11 per-problem lens catalogs (lehmer, collatz, brauer_siegel, knot_concordance, ulam_spiral, hilbert_polya, zaremba, p_vs_np, drum_shape, irrationality_paradox, knot_nf_lens_mismatch)
- `harmonia/memory/catalogs/README.md` — catalog index with teeth-test verdicts + cnd_frame_status
- `harmonia/memory/symbols/VACUUM.md` + `EXHAUSTION.md` — Pattern 18 / Pattern 13 made queryable
- `feedback_mpa_is_construction.md` + `feedback_falsification_first.md` (memory) — frame docs
- `feedback_api_probe_methodology.md` (memory) — single-seed-vs-multi-seed LLM probe discipline
- `cartography/docs/probe_*_results.md` — external-LLM probe outputs
- `harmonia/memory/probes_register.md` — probes index (sessionA 2026-04-23, closes axis-4 drift observation)
- `harmonia/memory/cluster_methodology_cnd_fit.md` — methodology cluster graph (sessionA + sessionC joint 2026-04-23, closes axis-4 sprawl observation on methodology cluster)
- `harmonia/memory/provocations.md` — sessionE calibration-provocations living log

**Sprawl observations (sessionA 2026-04-23, axis-4 owner):**

*Duplication:*
- **Two docs for MPA.** `MULTI_PERSPECTIVE_ATTACK.md` (v1 promoted symbol, immutable under Rule 3) is the canonical definition; `methodology_multi_perspective_attack.md` is the procedure-and-anchor-cases doc (mutable). Symbol references procedure; procedure references symbol. Content overlap ~30% (both state forbidden-moves discipline; both describe anchor cases Lehmer/Collatz). Low-risk drift so far but real duplication.
- **Cross-disciplinary lenses live in 3 places.** `methodology_toolkit.md` holds the 6-tool shelf (KOLMOGOROV_HAT, CRITICAL_EXPONENT, CHANNEL_CAPACITY, MDL_SCORER, RG_FLOW, FREE_ENERGY). `docs/prompts/gen_09_cross_disciplinary_transplants.md` specs gen_09 which consumes the first 3. `CANDIDATES.md` has individual tool-candidate entries for each. The SAME lens is described 3 times.
- **Two catalog indexes.** `harmonia/memory/catalogs/README.md` (mutable index with per-catalog one-liners + teeth-test verdicts) + `PROBLEM_LENS_CATALOG.md` (v1 promoted symbol with schema + promotion-time anchors frozen at 3). Since v1 promotion, 8 more catalogs landed (11 total); the immutable-def anchor list does NOT reflect current state; README does. Well-defined split but a reader needs to know to prefer README for current state.

*Drift:*
- **External-LLM probe outputs are scattered.** 5+ probe result files live under `cartography/docs/probe_*_results.md`. No index; no cross-reference from the API-probe methodology memory. Hard to answer "what probes have run, on what symbols, with what model, with what outcome?"
- **Methodology cluster has no graph.** CND_FRAME + FRAME_INCOMPATIBILITY_TEST + CONSENSUS_CATALOG + Y_IDENTITY_DISPUTE (enum within FIT v2) + ANCHOR_PROGRESS_LEDGER + ANCHOR_AUTHOR_DIVERSITY are six inter-referenced symbols/candidates. Each MD cross-references the others, but no artifact renders the cluster as a readable map. A future Harmonia encountering any one of these has to traverse references to build the graph in their head.

*Orphan:*
- **SHADOWS_ON_WALL is claimed by Axis 4 but IS the project's foundational frame.** The restore protocol's Operating Disposition section treats it as pre-axial. Other axes' canonical artifacts depend on it (Pattern 6 in Axis 1 is literally "verdicts are coordinate systems" which is SHADOWS). Splitting it into one axis is a Pattern-17 organization smell.
- **`provocations.md` not listed anywhere.** `harmonia/memory/provocations.md` (sessionE 2026-04-20 living log) is an exploration-techniques artifact but doesn't appear in the canonical list. Scope: session-specific calibration provocations.
- **Stoa discussions/predictions** (`stoa/discussions/*.md`, `stoa/predictions/open/*.md`, `stoa/feedback/*.md`) host a lot of cross-session methodology debate (teeth-test resolution, MPA-v2 refactor premise, convergent-number-divergent-frame debate). Not referenced in the canonical list; lives in a parallel artifact tree.

**Consolidation candidates (sessionA 2026-04-23):**

1. **Create `harmonia/memory/probes_register.md`.** Index of every external-LLM probe (model, prompt path, result path, replication status per `feedback_api_probe_methodology.md`). Format: table with columns {date, probe_id, model, prompt_summary, result_path, replication_tally, outcome_landed_at_symbol}. Would unblock "what have we probed? on what? with what convergence?" queries in one scan.

2. **Render methodology cluster as `cluster_methodology_cnd_fit_consensus.md`.** A single MD with a dependency diagram (plain ASCII DAG is fine) showing: SHADOWS_ON_WALL → PROBLEM_LENS_CATALOG → FRAME_INCOMPATIBILITY_TEST → {CND_FRAME, CONSENSUS_CATALOG, Y_IDENTITY_DISPUTE enum} + supporting {ANCHOR_AUTHOR_DIVERSITY, ANCHOR_PROGRESS_LEDGER}. Per-symbol one-liner + "which question does this answer?" Preserves individual MDs as canonical; cluster is navigational.

3. **Reference SHADOWS_ON_WALL from every axis section in this map.** Pattern-17 fix. SHADOWS is foundational for all axes; not axis-4-exclusive. Propose adding a top-level "## Foundations" section before Axis 1 that names SHADOWS_ON_WALL + Pattern-6 + the landscape_charter as pre-axial frame documents every axis depends on.

4. **Clarify `MULTI_PERSPECTIVE_ATTACK.md` vs `methodology_multi_perspective_attack.md` split.** One candidate: symbol MD stays thin (schema + canonical anchors); procedure doc stays rich (step-by-step + anchor walkthrough + forbidden-moves rationale). Explicit header in each: "this doc = definitional schema; see procedure at X" and vice versa. No content merge; just clearer delegation.

5. **Create `harmonia/memory/stoa_index.md`.** Surface the Stoa artifact tree (discussions / predictions / feedback / ideas) from this concept_map. Axis 4 should reference it; axis 5 (frontiers) also benefits because open predictions are frontier-tracking material.

6. **Add provocations.md to canonical list + reference from axis 4.** Small fix. Was missed in sessionC's first-pass; my axis-4 ownership catches it.

7. **Tag all methodology-toolkit entries + methodology_multi_perspective_attack.md with explicit axis-4 membership in frontmatter** (e.g., `concept_axis: 4`). Cheap to add; enables grep-level axis queries (`rg "concept_axis: 4"` returns the axis-4 corpus). Parallel convention for axes 1-3, 5-6.

**Proposed owner:** sessionA (MULTI_PERSPECTIVE_ATTACK + methodology_toolkit author + recent V2_STRUCTURE_PROPOSAL coordinator) — **CLAIMED 2026-04-23 iter-38**. Sprawl + consolidation above.

---

## Axis 5 — Research frontiers (live specimens + open problems)

**One-line:** F-IDs (live, killed, calibration, data-frontier) + open-problem catalogs are the project's outward-facing surface; tracking what's contested vs settled vs unmapped is what tells us where to look next.

**Canonical artifacts:**
- `harmonia/memory/decisions_for_james.md` — running log of judgment calls + retractions + standing limits
- `harmonia/memory/build_landscape_tensor.py` (FEATURES list) — F-ID roster (calibration / live_specimen / killed / data_frontier tiers)
- `harmonia/memory/catalogs/` — per-open-problem lens catalogs (see Axis 4)
- `harmonia/memory/geometries.md` — three named shape hypotheses (1 retracted; 2 + 3 intact)
- `signals.specimens` Postgres table — measurement registry with provenance
- `prometheus_fire.zeros.object_zeros` Postgres table — 2M EC L-function zeros (F011 substrate)
- `aporia/mathematics/lesser_known_open_problems.md` + `silent_islands_analysis.md` — frontier triage
- `aporia/mathematics/fingerprints_report.md` — irrationality_paradox origin
- `roles/Harmonia/worker_journal_*.md` — full conductor journals
- `feedback_finding_hierarchy.md` (memory) — 3 conditional laws / 2 constraints / 1 identity / 0 universal laws

**Sprawl observations** *(sessionB first-pass, 2026-04-22):*

1. **F-ID state fragmented across 4+ locations.** `build_landscape_tensor.py` FEATURES list has tier + prose description; `signals.specimens` Postgres has measurement registry; `decisions_for_james.md` has retractions + standing limits; `cartography/docs/audit_*` has specific audit outputs. No single canonical F-ID state page a cold-start can grep.

2. **Today's audits orphaned from F-ID entries.** Auditor's 2026-04-22 F041a SIGN_INVERSION_AND_RESHAPE (1776899465123), F044 RETRACTED_AS_SELECTION_ARTIFACT (1776900048561 + 1776900246480), F045 SURVIVES_MULTIPLE_TESTING_BUT_SHARES_STRUCTURE_WITH_F041A (1776900402211) all produced substantive findings but haven't propagated back to the F-ID descriptions in `build_landscape_tensor.py`. Cold-start after next restart will see stale F-ID prose.

3. **Catalog README.md index has 11 catalogs without living-tier status.** 3 at coordinate_invariant (Zaremba, drum_shape, knot_nf_lens_mismatch), 6 at surviving_candidate, 2 not-yet-teeth-tested. Tier state lives in individual catalog frontmatter but the index header doesn't mirror it — readers must open each catalog to know its status.

4. **Stoa → catalog back-refs one-directional.** Catalog MDs point at Stoa predictions they resolved against (e.g., knot_nf_lens_mismatch → sessionD teeth-test stringency prediction), but Stoa predictions/discussions don't back-link to the catalog MDs they now anchor. Harder to trace a Stoa artifact forward into active substrate.

5. **F011 Layer 2 rank-0 residual state sprawl.** EPS011@v2 symbol declares 22.90 ± 0.78 (1/log N), but the 3-ansatz comparison (22.90 / 31.08 / 35.83) + under-constrained joint fit caveat + independent-unfolding audit result + Sage/lcalc deferral + DHKMS rule-out + T4 sub-family observation are spread across `build_landscape_tensor.py` F011 description (long paragraph), EPS011@v2 MD, `decisions_for_james.md` 2026-04-18/19 entries, and worker-journal archives. No single F011-state-of-the-union doc.

6. **Aporia provenance chain intermittently grounded.** `fingerprints_report.md §II.4` → irrationality_paradox catalog anchor; `silent_islands_analysis.md Island 1` → knot_nf_lens_mismatch anchor; `deep_research_batch1.md Report 3` → A-polynomial diagnosis. These provenance pointers exist inside individual catalog MDs but there's no cross-ref table from the Aporia artifacts forward to which Prometheus catalog / F-ID they seeded. Aporia authors may not know what Harmonia built on their reports.

**Consolidation candidates** *(sessionB first-pass, 2026-04-22):*

1. **`harmonia/memory/frontier_specimen_state.md` (new living artifact).** Per-F-ID living state page: current tier, active audits, pending cross-resolvers, open questions, cross-refs to substrate measurements + symbol MDs + catalog MDs + Stoa artifacts. Would replace the need to re-derive state from 4+ locations. Schema: `F0XX | tier | last_audit_outcome | open_questions | cross_refs`. Rebuild from `build_landscape_tensor.py` manifest every tick; ANCHOR_PROGRESS_LEDGER-style mutable sidecar.

2. **Audit-result → F-ID description propagation pass.** For each of today's auditor audit docs (F041a / F044 / F045 / and any prior), edit `build_landscape_tensor.py` F-ID description to include: (a) 1-sentence outcome summary; (b) path pointer to `cartography/docs/audit_*_results`; (c) tier-change recommendation if one exists. This sprawl item is the HIGHEST-LEVERAGE single fix on axis 5 — the tensor cells are the public face and must reflect audit outcomes.

3. **Catalog README.md living-tier header.** Add top-level table: `catalog | problem_id | cnd_frame_status | teeth_test_verdict | tier | last_resolver | last_cross_resolver`. Mirrors the ANCHOR_PROGRESS_LEDGER pattern (sessionA 1776910494837) at the catalog layer. Mutable index over immutable catalog bodies; Rule-3-compliant.

4. **Stoa → catalog bi-directional back-refs.** For each resolved Stoa prediction/discussion, add `resolved_catalogs: [list]` in frontmatter; for each catalog with a Stoa anchor, add `anchors_stoa: [list]` in frontmatter. Cross-linked graph queryable from either direction.

5. **F011 residual state consolidation into EPS011 MD.** Promote EPS011@v2 to single source-of-truth: embed 3-ansatz comparison table + under-constrained-fit caveat + unfolding audit outcome + DHKMS / T4 observations + Sage/lcalc deferral status. `build_landscape_tensor.py` F011 description and `decisions_for_james.md` entries then link to EPS011@v2 rather than duplicate. This closes a 2026-04-18/19 sprawl that has been accreting.

6. **Teeth-test wave consolidation in `decisions_for_james.md`.** The 8/8 + 3 forward-path teeth-test resolution is fragmented across ~10 entries (2026-04-22 through 2026-04-23) in decisions_for_james.md. One consolidated "2026-04-22 teeth-test wave" entry with links replaces the per-verdict entries; per-verdict entries remain as historical commits in the file's append-only log but are marked `superseded_by: teeth-test-wave-2026-04-22`. Preserves audit trail, reduces duplicate-index surface.

**Priority ordering (axis 5 recommendation):**
- P0 — consolidation #2 (audit → F-ID propagation). Audit findings from today will become stale fastest.
- P1 — consolidation #1 (frontier_specimen_state.md). Highest leverage for cold-start restore-time reduction.
- P1 — consolidation #3 (catalog README tier header). Cheap + high visibility.
- P2 — consolidations #4, #5, #6. Useful but not urgent.

**Cross-axis hooks:**
- Axis 1 (auditor, falsification battery): audit outputs land HERE as F-ID-description updates. Consolidation #2 is the handshake between axis 1 and axis 5.
- Axis 2 (Charon, mapping): F-ID tensor rows ARE the axis-5 data. Proper axis-5 organization is the content axis 2 organizes.
- Axis 3 (sessionC, symbolic storage): EPS011@v2 consolidation (#5) is an axis-3 symbol-MD work item with axis-5 content.
- Axis 4 (sessionA, exploration techniques): MPA-driven new catalog builds (K41, drum_shape, etc.) feed axis 5 as new frontier anchors.
- Axis 6 (Ergon/Techne, tool building): `frontier_specimen_state.md` generator + Stoa bi-directional-link auto-maintenance are axis-6 tool candidates.

**Proposed owner:** Harmonia_M2_sessionB (CLAIMED 2026-04-22 per sync 1776910772657).

---

## Axis 6 — Tool building for efficiency

**One-line:** Generators that spawn N tasks per application + helpers that compress restore cost + sweeps that automate epistemic discipline; the substrate is increasingly self-growing because each generator IS a primitive that compounds.

**Canonical artifacts:**
- `harmonia/memory/generator_pipeline.md` (v1.1) — 11-generator DAG (Tier 0 + Tier 1 executed; gen_11 axis-space producer DRAFT)
- `harmonia/runners/` — reusable executors for first-pass generator work (gen_03, gen_05, gen_07, gen_log_builder)
- `harmonia/sweeps/` — automated epistemic discipline modules (pattern_30, pattern_20, pattern_19, runner, retrospective, OVERRIDE_PROTOCOL)
- `agora/helpers.py` — substrate-health, queue_preview, tail_sync, seed_task, canonical_instance_name
- `agora/work_queue.py` + `agora/symbols/*` + `agora/tensor/*` + `agora/datasets/*` — agora client library
- `harmonia/memory/restore_protocol.md` (v4.3) — cold-start protocol; minimum viable path ~12 files / ~30 minutes
- `docs/prompts/gen_NN_*.md` — generator specs (force-added through .gitignore)
- `docs/prompts/track_*.md` — track-level work prompts
- `harmonia/memory/architecture/definition_dag.md` — substrate primitive (manual seed Phase 0 pending)
- `cartography/viewer/server.py` — heatmap server (port 8777; auto-refresh from Redis)
- `feedback_4min_cron_collaboration.md` (memory) — collaborative-day cron discipline
- `feedback_track_d_replication_discipline.md` (memory) — Track D byte-equivalence tuple
- `feedback_partial_push_recovery.md` (memory) — Rule 3 immutability vs failed-mid-write recovery

**Sprawl observations (sessionA 2026-04-23, axis-6 strawman-drafter per sessionC partition proposal 1776911869855-0):**

*Duplication:*
1. **Generator specs live in `docs/prompts/*.md` which is `.gitignore`-excluded.** Requires `git add -f` per gotcha #2 in restore_protocol.md. Cold-start Harmonia who clones the repo fresh won't see generator specs unless they know about the force-add convention. Duplicates the risk pattern the `harmonia/tmp/` convention already accepts — but generator specs are MORE canonical than tmp.
2. **Generator status in two places.** `generator_pipeline.md` (v1.1) has a Tier/status table as its single source-of-truth. `decisions_for_james.md` has individual milestone entries per generator ship (gen_06, gen_02, gen_10 etc.). Cold-start Harmonia reading one may miss updates in the other. Source-of-truth should be the pipeline doc; decisions_for_james entries should link-only.
3. **`harmonia/tmp/` → `harmonia/runners/` promotion is ad-hoc.** tmp scripts (probe_*, init_*) live gitignored for one-shot use; some graduate to runners/ when reused. No formal criterion for when a script becomes a runner. This session alone: `init_anchor_progress_FIT.py` + 5 probe scripts sit in tmp/, of which anchor_progress is importable from `agora.symbols.anchor_progress` (already promoted the module but not the init script).

*Drift:*
4. **`agora/` package has no function index.** `agora/helpers.py` + `agora/work_queue.py` + `agora/symbols/{push,resolve,manifest,lifecycle,anchor_progress}.py` + `agora/tensor/*` + `agora/datasets/*` — a new Harmonia discovering `from agora import X` has to `grep -r '^def '` to find helpers. No top-level `agora/README.md` listing signatures. Echoes sessionC axis-3 orphan #2 (agora.symbols specifically); applies at the whole-package level for axis-6.
5. **`restore_protocol.md` is monolithic.** v4.3 ~530 lines, one-file-reads-all. If `concept_map.md` becomes the navigational outline (per sessionC cross-axis observation line 372), restore_protocol could split into per-axis restore procedures OR become a deep-dive companion to concept_map rather than the primary cold-start path.
6. **Sweep events emit to sync stream only.** `harmonia/sweeps/runner.py` posts override events + PATTERN_30_BLOCK to `agora:harmonia_sync`; no dedicated log stream (`agora:override_log` per auditor axis-1 #8). Aggregation over time requires re-scanning the main sync stream. Same concern from axis-1 perspective; axis-6 adds the tool-building angle (a dedicated log stream is infra a tool-builder should ship).

*Orphan:*
7. **Cron-discipline not formally documented.** `feedback_4min_cron_collaboration.md` (memory) names the pattern but procedural how-to (CronCreate with `*/N * * * *`, CronDelete `<id>` on wind-down, interval rounding for non-clean divisors of 60) is tribal knowledge in session transcripts. No `harmonia/memory/cron_discipline.md`.
8. **Partial-push recovery is memory-entry-only.** `feedback_partial_push_recovery.md` captures the sessionB discipline (cleanup orphan :def / :meta / :latest / :versions keys before retry). No corresponding helper function in `agora/symbols/push.py` — the cleanup is manual.
9. **`tests/` directory exists but is unlisted in axis-6 canonical artifacts.** `agora/symbols/test_manifest.py` (21 tests green) + `harmonia/sweeps/test_sweeps.py` (14 tests green) + a `tests/` tree mentioned in git status earlier. No test-coverage-index-at-a-glance; which substrate components have tests vs don't is unknown without scanning.
10. **`substrate_health()` is the cold-start diagnostic but lacks convention-level visibility.** `from agora.helpers import substrate_health; substrate_health()` is the Step 0 check in restore_protocol; there's no `python -m agora.healthcheck` CLI convention that cold-start Harmonia might try first.

**Consolidation candidates (sessionA 2026-04-23, axis-6 strawman):**

1. **`agora/README.md` — package function index.** Auto-generated (or manually curated) listing of every public function in `agora.*` with signature + one-liner. Parallel to auditor's `lineage_registry_view.md` pattern (auto-regenerable from Python source via `ast` walk). Closes sprawl #4. **Cheap win.**

2. **`harmonia/memory/cron_discipline.md` — cron-discipline doc.** Factor out of session transcripts: cadence choice (collaborative 4m / sustained 8-10m / self-pace), interval rounding for non-clean divisors, CronDelete on wind-down, migration between cadences. Closes sprawl #7. **1 tick of work.**

3. **`python -m agora.healthcheck` CLI entrypoint.** Wrap `substrate_health()` in a `__main__.py` that prints + exits with non-zero on anomaly (stale tensor version, symbol count regression, queue stuck). Discoverable via standard Python convention. Closes sprawl #10. Would make CI-gating the substrate feasible.

4. **`docs/prompts/README.md` — generator spec index.** Single navigation page for the force-added docs/prompts/ tree. Closes sprawl #1 (cold-start discoverability of force-added files). Cross-reference from `generator_pipeline.md`.

5. **`harmonia/memory/automation_index.md` — runners + sweeps table.** One-page table: module path, purpose, sync events emitted, last-run (if cron-triggered), owner axis. Closes sprawl-overlap between axis-1 (sweeps as discipline) and axis-6 (sweeps as automation). Joint with auditor's `audit_results_index.md` pattern — this is `automation_produced_indexes.md`.

6. **`harmonia/tmp/` → `harmonia/runners/` promotion criterion (written rule).** Formal: if a tmp script is (a) imported by another file, OR (b) executed > 2 times, OR (c) produces a tensor/symbol mutation, it is promoted by its author to `runners/` with a header block naming its intended reuse pattern. Closes sprawl #3. Lightweight; no code change needed beyond the discipline doc.

7. **`agora.symbols.push.cleanup_partial_push(name, version)` helper.** Codifies sessionB's manual cleanup discipline per `feedback_partial_push_recovery.md`. Inputs: symbol name + version; outputs: audit log of keys cleaned. Closes sprawl #8. **Medium effort but saves future recovery time.**

8. **`restore_protocol.md` axis-keyed split.** Transform v4.3 into v5 = navigation wrapper + six `restore_protocol_axis_N.md` deep-dives (Axis 1-6 per concept_map partition). Cold-start Harmonia who needs axis-specific restore (e.g. returning after working on falsification) reads axis-1 deep-dive in 5 min instead of 30 min. Joint with sessionC cross-axis observation (line 372). Closes sprawl #5. **Medium effort; high cold-start cost reduction.**

9. **`tests/` coverage index.** `harmonia/memory/test_coverage.md` — table: module under test, test file, test count, last-run-status, owner. Closes sprawl #9. Auto-regenerable via pytest --collect-only. Joint with axis-3 (tests are symbolic-infrastructure).

10. **Dedicated log streams per automation class.** `agora:override_log` (sweep overrides), `agora:promotion_log` (symbol promotions), `agora:probe_log` (external LLM probes per probes_register.md). Each is a capped Redis stream parallel to `agora:harmonia_sync` but filtered by event class. Closes sprawl #6 + cross-axis with auditor axis-1 consolidation #8. Longer-term infra; ship only if cross-stream aggregation becomes operationally needed.

**Priority ordering (axis-6 recommendation):**
- P0 — #2 (cron discipline doc), #4 (generator spec README), #1 (agora README). Cheap 1-tick wins.
- P1 — #3 (healthcheck CLI), #5 (automation index), #6 (tmp→runners promotion rule). Medium effort.
- P2 — #7 (cleanup helper), #8 (restore protocol split), #9 (tests coverage), #10 (log streams). Higher effort; schedule when consolidation ROI justifies.

**Cross-axis hooks:**
- **Axis 1 (auditor, falsification):** consolidations #5 (automation index) and #10 (log streams) overlap with auditor's #4 (self-dissent ledger) and #8 (override events log). Joint sidecar-pattern instances per ANCHOR_PROGRESS_LEDGER.
- **Axis 3 (sessionC, symbolic storage):** consolidations #1 (agora README) and #9 (test coverage) overlap with sessionC's axis-3 orphan #2 (agora.symbols helper index). Joint.
- **Axis 5 (sessionB, frontiers):** consolidation #8 (restore protocol split) addresses sessionB axis-5 cold-start restore-time concern implicitly.
- **Axis 2 (mapping):** TBD once sessionC's axis-2 strawman lands — tensor-tool consolidations may emerge there.

**Proposed owner:** sessionA (axis-6 strawman-drafter, per sessionC partition proposal 1776911869855-0) — **STRAWMAN 2026-04-23 iter-51**. Sprawl + consolidation above. Happy to step aside if Ergon / Techne / Koios claims by next-tick; strawman preserves state until genuine claim.

---

## Cross-axis observations (sessionC first-pass, 2026-04-23)

**Concepts spanning multiple axes:**
- `MULTI_PERSPECTIVE_ATTACK@v1` lives across Axis 4 (exploration) and Axis 1 (falsification — committed-stance discipline IS a kill discipline at the framing level).
- `gen_06 sweeps` (PATTERN_30/20/19) live across Axis 1 (falsification) and Axis 6 (tools — they're automated discipline).
- `FRAME_INCOMPATIBILITY_TEST@v2` lives across Axis 3 (symbolic storage — its own MD), Axis 4 (the test classifier), and Axis 5 (per-catalog teeth-test verdicts).
- `methodology_toolkit.md` lives across Axis 4 (cross-disciplinary lens shelf) and Axis 6 (a tool for finding new lenses) and Axis 5 (gen_09 transplant pathway).

**Recurring sprawl pattern:** The methodology cluster (CND_FRAME / FRAME_INCOMPATIBILITY_TEST / CONSENSUS_CATALOG / ANCHOR_AUTHOR_DIVERSITY / ANCHOR_PROGRESS_LEDGER) accumulated 5 inter-related symbols this work-day (2026-04-23). Each symbol cross-references the others. The connections are documented in each symbol's MD but no single artifact maps the cluster as a graph. Candidate consolidation: one diagram or table per methodology cluster, indexed from this concept_map.

**Recurring drift pattern:** Memory entries (33 entries as of 2026-04-23) and feedback memories (~17 entries) overlap at the boundary. Some lessons (`feedback_battery_calibration`, `feedback_ensemble_invariance`) are about the falsification axis; some (`feedback_mpa_is_construction`) are about exploration. No current axis-tagging on memory entries. Candidate consolidation: tag each memory entry with primary axis (1-6) for queryability.

**Cold-start cost compression observation:** Restore protocol is currently ~30 minutes (12 files) per restore_protocol.md v4.3. With a navigable concept_map, future cold-starts could read concept_map.md FIRST as an outline + pull canonical artifacts on-demand. Candidate substrate primitive: the concept_map IS the cold-start outline; restore_protocol becomes the deep-dive procedure for when an axis-specific restore is needed.

---

## Section owners (current; updated as claims land)

| Axis | Owner | Status |
|---|---|---|
| 1 — Falsification battery | Harmonia_M2_auditor | CLAIMED 2026-04-23, first-pass sprawl + consolidation candidates filled |
| 2 — Mapping | (proposed: Charon, fallback Koios) | UNCLAIMED |
| 3 — Symbolic storage | (proposed: Harmonia_M2_sessionC) | UNCLAIMED (sessionC will draft strawman by iter-3 if no other claim) |
| 4 — Exploration techniques | Harmonia_M2_sessionA | CLAIMED 2026-04-23 — sprawl + consolidation filled |
| 5 — Research frontiers | (proposed: Harmonia_M2_sessionB or Aporia) | UNCLAIMED |
| 6 — Tool building for efficiency | Harmonia_M2_sessionA (strawman) | STRAWMAN 2026-04-23 per sessionC partition proposal — sprawl + consolidation filled; will step aside if Ergon/Techne/Koios claims |

Coordination: claim via agora:harmonia_sync `CLAIM` message naming the axis. Drop section in this file as you fill it in.

---

## Version history

- **v0.1** (2026-04-23, sessionC) — initial skeleton per James's 2026-04-23 directive ("organize big concepts across Harmonias + Charon + Ergon + Aporia + Techne; rally around 6 core strategies; getting faster at getting better"). All 6 axes have canonical-artifact lists; sprawl + consolidation observations placeholder pending section-owner fill. Cross-axis + recurring-drift + cold-start-compression observations from sessionC's first-pass scan.
