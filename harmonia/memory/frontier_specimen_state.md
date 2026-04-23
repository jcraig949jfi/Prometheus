---
name: frontier_specimen_state
purpose: Living per-F-ID state index. Single source-of-truth for tier + last audit + open questions + cross-refs. Replaces the cold-start 4+-location grep (build_landscape_tensor.py FEATURES / signals.specimens / decisions_for_james.md / cartography/docs/audit_*). Mirrors the ANCHOR_PROGRESS_LEDGER pattern (sessionA 1776910494837) at the F-ID layer.
status: v0.1 SKELETON — Harmonia_M2_sessionB 2026-04-22. Exemplar rows filled for actively-touched F-IDs (this session). Killed F-IDs left as stub entries; consolidator or Ergon-tool-build should regenerate from manifest.
regenerator_convention: Follows auditor's audit_results_index.md + sessionA's axis-6 auto-regenerator pattern. A Python regenerator at `harmonia/memory/gen_frontier_specimen_state.py` (TODO) should read `build_landscape_tensor.py` manifest + `cartography/docs/audit_*_results` + `decisions_for_james.md` frontmatter + `stoa/predictions/resolved/*` and emit this artifact idempotently. Until regenerator ships, this file is hand-maintained (with provenance breadcrumbs).
maintenance: living document; each F-ID row is mutable; tier changes route through decisions_for_james.md approval. Rule 3 does NOT apply (this is a mutable sidecar over the immutable tensor manifest, same architectural layer as ANCHOR_PROGRESS_LEDGER).
axis: axis-5 (research frontiers) consolidation #1 per concept_map.md.
---

# Frontier specimen state — living index

**Source of truth for per-F-ID state.** Read this first on cold-start if you need to know "what's the current status of F0XX." Any inconsistency between this file and `build_landscape_tensor.py` FEATURES list → the tensor manifest wins for tier, but audit-outcome / open-questions / cross-refs in this file reflect the most recent team work and may lead the manifest by one or two sessions (see consolidation #2 propagation discipline below).

## How to use

1. **Cold-start restore:** start here, then drill into the specific artifacts via cross-refs.
2. **Post-audit update:** when a new audit ships, update the relevant row's `last_audit_outcome` + `cross_refs` columns AND append an audit line to `build_landscape_tensor.py` FEATURES description (per axis-5 consolidation #2 discipline — sessionB 1776911782623).
3. **Tier change:** route through `decisions_for_james.md` approval, then update tier here AND manifest.
4. **Regenerator pattern:** once `gen_frontier_specimen_state.py` ships (Axis 6 Ergon/Techne task candidate), this file becomes auto-generated. Hand edits will be overwritten. Audit-outcome updates route through updating the canonical source (`cartography/docs/audit_*_results`) rather than this file directly.

## Schema (5 columns + provenance)

```
F-ID | tier | last_audit_outcome | open_questions | cross_refs
```

- **tier** ∈ {calibration, calibration_refinement, live_specimen, killed, killed_selection_frame (new per F044), killed_tautology, data_frontier, data_artifact, null_confirmed}
- **last_audit_outcome** — most recent substantive audit verdict + date + auditor instance + agora sync-msg-ID
- **open_questions** — 0–3 open questions blocking promotion / demotion / confirmation
- **cross_refs** — symbol MDs + catalog MDs + Stoa artifacts + cartography audit docs

## Active F-IDs (priority rows — touched this session or at live_specimen tier)

### Live specimens

| F-ID | tier | last_audit_outcome | open_questions | cross_refs |
|---|---|---|---|---|
| **F011** | live_specimen (mixed: LAYER 1 calibration + LAYER 2 frontier) | 2026-04-19 independent-unfolding-audit SURVIVES narrow form; Sage/lcalc external verification deferred | Miller 2009 NLO prediction match to ~23% residual; independent NULL_BSWCD cross-code-path replication | `EPS011@v2`, `Q_EC_R0_D5@v1`, `cartography/docs/wsw_F011_*`, catalogs/hilbert_polya (lens anchor), decisions_for_james 2026-04-18/19 entries |
| **F013** | live_specimen (downstream of F011 excised ensemble) | Pattern 30 PARTIAL Level 1 WEAK_ALGEBRAIC annotation 2026-04-20 (BSD parity couples rank to Katz-Sarnak) | CFKRS rank-2 prediction closes Pattern 5 gate | `LINEAGE_REGISTRY.F013`, catalogs/knot_concordance (lens anchor), null_protocol_v1 composite-verdict running anchor |
| **F014** | live_specimen (Lehmer Salem density + trinomial floor 1.381) | 2026-04-18 Charon structural upgrade: M(x^n−x−1) → 1.381 as n→∞; gap widens with degree | M(A-polynomial) bridge to NF L-values (per knot_nf_lens_mismatch); Salem polynomial enumeration to d=60 | catalogs/lehmer.md (PASS anchor at coordinate_invariant), catalogs/knot_nf_lens_mismatch.md |
| **F015** | live_specimen (sign-uniform durable) | Pattern 30 PARTIAL Level 1 2026-04-19 (log(N) denominator partial algebraic); sign claim durable | Magnitude non-monotonicity (k=4 breaks trend) unexplained | `LINEAGE_REGISTRY.F015`, Pattern 20 anchor |
| **F041a** | live_specimen (nbp ladder rank-2+) | **2026-04-22 AUDITOR Euler-deflation audit (auditor 1776899465123): SIGN_INVERSION_AND_RESHAPE** — deflator flipped (nbp, slope) correlation +0.65 → −0.83; Pattern 30 disposition PARTIAL → SHARED_VARIABLE on original framing; PATTERN-19 flag on auditor-raw-slope ~5× smaller than recorded | Methodology reconciliation before tensor mutation; CFKRS Pattern 5 gate still open (Pattern 30 gate collapsed into same gate) | `cartography/docs/audit_F041a_euler_product_deflation_results.json`, `LINEAGE_REGISTRY.F041a`, `LADDER@v1` |
| **F042** | calibration_refinement (downgraded from live_specimen 2026-04-18) | Gross LNM 776 / Rodriguez-Villegas & Zagier 1993 known-qualitative; 6.66× enrichment is quantitative-precision contribution | Cross-decade replication at other Heegner d values | decisions_for_james 2026-04-18 |
| **F044** | live_specimen (**pending tier change to killed_selection_frame**) | **2026-04-22 AUDITOR frame-based resample + rank-5 audits (1776900048561 + 1776900246480): RETRACTED_AS_SELECTION_ARTIFACT** — at conductor ≥ 10^8, ALL ranks 2-5 are 100% semistable+nbp=1; pattern is LMFDB-sourcing artifact | Conductor approval for tier demotion + cell demotion (P020/P023/P026 +1 → −2); 4th Pattern-4 anchor candidate | `cartography/docs/audit_F044_framebased_resample_results.md`, `cartography/docs/audit_F044_rank4_lmfdb_selection_results.md`, `LINEAGE_REGISTRY.F044` |
| **F045** | live_specimen (nbp-entangled) | **2026-04-22 AUDITOR multiple-testing + independence audit (1776900402211): SURVIVES_MULTIPLE_TESTING_BUT_SHARES_STRUCTURE_WITH_F041A** — 1/25 Bonferroni (p=79); class_size × nbp Spearman +0.455 | Stratified-within-nbp disentanglement from F041a | `cartography/docs/audit_F045_multiple_testing_and_independence_results.json`, `LINEAGE_REGISTRY.F045` |

### Calibration anchors (stable; rare update)

| F-ID | tier | notes |
|---|---|---|
| F001-F005 | calibration | Modularity, Mazur torsion, BSD parity, Hasse bound, High-Sha parity — instrument-health gates. Any 100% → <100% violation IS a bug. |
| F008 | calibration | Scholz reflection |r3(K*) − r3(K)| ≤ 1 across 344K pairs |
| F009 | calibration | Torsion primes ⊆ nonmax primes across 1.39M non-CM EC |

### Killed + data-frontier (stub)

See `build_landscape_tensor.py` FEATURES list for full roster: F010 (NF backbone, killed via block-shuffle), F012 (Möbius H85 killed Pattern-19), F020-F028 (various kills — Megethos, Phoneme, Spectral tail, Faltings-H08, ADE-H10, Artin-H61, Alexander-Mahler, Szpiro-Faltings-H40 tautology), F030 (Delinquent EC data-frontier), F031 (zeros corruption data-artifact), F032 (Knot silence — reframed by knot_nf_lens_mismatch), F033 (rank ≥ 4 coverage cliff data-frontier), F043 (BSD-Sha RETRACTED 2026-04-19 as algebraic identity).

## Cross-axis composition

- **axis-1 (falsification battery, auditor):** audit outputs land here as `last_audit_outcome` column updates. Today's F041a/F044/F045 audits are the handshake instance.
- **axis-2 (mapping, sessionC-Charon):** F-ID tensor rows ARE the content this artifact indexes. Proper axis-5 organization depends on axis-2 tensor-side hygiene.
- **axis-3 (symbolic storage, sessionC):** LINEAGE_REGISTRY (Pattern 30 metadata) cross-refs here; EPS011@v2 is F011's canonical symbol.
- **axis-4 (exploration, sessionA):** New-catalog builds produce new F-IDs that land here at `live_specimen` tier with forward-path provenance.
- **axis-6 (tool building, sessionA):** `gen_frontier_specimen_state.py` regenerator is an axis-6 candidate tool — would auto-sync this file with `build_landscape_tensor.py` + `cartography/docs/audit_*` + `decisions_for_james.md` frontmatter.

## Open items (axis-5 roadmap)

1. **Regenerator (Ergon/Techne task):** `gen_frontier_specimen_state.py` reading manifest + audit docs + decisions + stoa resolved-predictions. Once live, this file becomes auto-generated; manual edits discouraged.
2. **Stoa bi-directional back-refs (consolidation #4):** when a Stoa prediction/discussion resolves against an F-ID, this file's `cross_refs` column should include the Stoa artifact path.
3. **Tier-change approval routing (per decisions_for_james.md convention):** tier changes must be proposed to conductor before update here + in manifest. F044 and F041a both currently have pending tier-change recommendations from auditor's audits this session; no tier mutations applied until approved.

## Version history

- **v0.1** (2026-04-22, sessionB): initial skeleton with 7 live-specimen rows + 3 calibration rows + killed-stub pointer. Drafted as axis-5 consolidation #1. Regenerator + full-roster population deferred to next iteration or Axis 6 tool-build claim.
