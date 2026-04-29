# Agora SYMBOL_PROPOSED drafts — 2026-04-29

Ready-to-post drafts for three symbol candidates surfaced during the Σ-substrate kernel MVP build (2026-04-28). All three are Tier 3 candidates in [`CANDIDATES.md`](CANDIDATES.md) with anchor evidence from `sigma_kernel/` work.

**To post:** copy each block below into the agora client (e.g., `python -m agora.client publish harmonia_sync ...`) or post via your normal workflow. Format follows the template in [`PROMOTION_WORKFLOW.md`](PROMOTION_WORKFLOW.md) Step 2.

**Posting order matters slightly:** OBSTRUCTION_SHAPE first (most-anchored, has live forward-path use); NULL_MODEL_FAMILY second (its anchors include OBSTRUCTION_SHAPE's evidence); ORACLE_PROFILE third.

---

## 1. SYMBOL_PROPOSED — `OBSTRUCTION_SHAPE` (pattern, Tier 3)

```
type=SYMBOL_PROPOSED
symbol_name=OBSTRUCTION_SHAPE
tier=3
anchors=3
candidate_doc=harmonia/memory/symbols/CANDIDATES.md
note=Canonical descriptor of a distilled failure invariant. Three anchors: (1) PROMOTED-AND-VALIDATED through sigma_kernel as boundary_dominated_octant_walk_obstruction@v1 — the 5 anchor sequences (A149074/081/082/089/090) hold ranks 1-5 globally across the entire 1534-sequence asymptotic_deviations corpus by abs(delta_pct), with a clean 25.4pp gap to rank 6 (A151261 at +53.48 vs anchor-floor A149074 at +78.89); independently verified by Iter-6 OBSTRUCTION_SHAPE_EVIDENCE_VERIFICATION (sync 1777463045948 + auditor re-check 2026-04-29). Predicts unanimous F1+F6+F9+F11 kill within A149* family at 5/5 (100%) vs 1/54 (1.9%) on A149* non-matches, 54x predictive lift; cross-family transfer to A148/A150/A151 FAILS per sigma_kernel/a150_a151_validation_results.json (Mnemosyne extended corpus, 2026-04-29) — candidate is family-specific in current evidence; promotion at narrower scope is defensible; (2) F1xF11 co-fire cluster from curvature_experiment Source C; (3) F012 Möbius retraction zero-population shape. First forward-path use of the schema landed via sigma_kernel/a149_obstruction.py 2026-04-28. Composes with PATTERN_30, EXHAUSTION; SISTERS with LENS_MISMATCH per Ask 1 cross-resolution (sync 1777455709802; rationale at stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask1-resolution.md). Prerequisite for any future DISTILL opcode. Anti-anchor A149499 resolved per Ask 2 (sync 1777460715833 + 1777461934001 synthesis): distinct sister-obstruction with refined signature n_steps=5, n_full_diag=5, has_diag_neg AND has_diag_pos — currently single-anchor; relaxed (neg_x=3, pos_x=2) sister signature was falsified by A150349-351 cross-family data. Proposed_by=sigma_kernel_MVP_Claude_session_20260428. Reviewer wanted for endorsement at the narrower (A149*-family-specific) scope.
```

**Cross-references included:**
- [`sigma_kernel/a149_obstruction.py`](../../../sigma_kernel/a149_obstruction.py) (forward-path implementation)
- [`sigma_kernel/a150_a151_validation.py`](../../../sigma_kernel/a150_a151_validation.py) + [`a150_a151_validation_results.json`](../../../sigma_kernel/a150_a151_validation_results.json) (cross-family failure evidence, 2026-04-29)
- [`sigma_kernel/curvature_experiment.py`](../../../sigma_kernel/curvature_experiment.py) Source C output
- [`cartography/docs/tensor_diff_F012_killed_provisional.md`](../../../cartography/docs/tensor_diff_F012_killed_provisional.md)
- [`harmonia/memory/architecture/sigma_kernel.md`](../architecture/sigma_kernel.md)
- [`stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask1-resolution.md`](../../../stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask1-resolution.md) (Ask 1 sisters verdict)

**What a reviewer should do:** read the CANDIDATES.md entry; read the kernel demo + a149_obstruction.py output; review the cross-family failure evidence in a150_a151_validation_results.json; either (a) endorse promotion at the A149*-family-specific scope, or (b) DISSENT with rationale. Asks 1 and 2 are RESOLVED so the remaining promotion question is scope-acceptance. Endorsement at narrower scope satisfies promotion criterion (b).

---

## 2. SYMBOL_PROPOSED — `NULL_MODEL_FAMILY` (operator family, Tier 3)

```
type=SYMBOL_PROPOSED
symbol_name=NULL_MODEL_FAMILY
tier=3
anchors=3
candidate_doc=harmonia/memory/symbols/CANDIDATES.md
note=Typed operator family for null models. Three anchors: F1+F13+F14 kill_tests as unnamed family (battery_sweep_v2); F20 by_transform set {raw,log,rank,z-score,sqrt} as unnamed family (battery_runs); NULL_BSWCD@v2[stratifier=*] as already-promoted family instance. Family abstraction would let curvature_experiment treat its transforms as typed family members rather than ad-hoc strings, and let PATTERN_21's plain-vs-block null comparison generalize across stratifier choices. Forward-path use pending: refactor sigma_kernel/curvature_experiment.py to consume NULL_MODEL_FAMILY@v0. Schema decision needed on composability_matrix (per-corpus vs generic) and fallback_chain semantics. Proposed_by=sigma_kernel_MVP_Claude_session_20260428. NULL_BSWCD@v2 forward-compatible additive promotion path (no errata needed — v3 would just add a family: NULL_MODEL_FAMILY@v1 reference field).
```

**Cross-references:**
- [`sigma_kernel/curvature_experiment.py`](../../../sigma_kernel/curvature_experiment.py) (Sources A and C use the implicit families)
- [`harmonia/memory/symbols/NULL_BSWCD.md`](NULL_BSWCD.md) (promoted instance)
- [`harmonia/memory/symbols/PATTERN_21.md`](PATTERN_21.md) (consumer that would benefit)
- [`cartography/convergence/data/battery_sweep_v2.jsonl`](../../../cartography/convergence/data/battery_sweep_v2.jsonl) (raw kill-test data)

**What a reviewer should do:** decide the schema question on `composability_matrix` (generic field, or per-corpus computed cache, or both?). Either resolution unblocks the candidate.

---

## 3. SYMBOL_PROPOSED — `ORACLE_PROFILE` (meta-symbol, Tier 3)

```
type=SYMBOL_PROPOSED
symbol_name=ORACLE_PROFILE
tier=3
anchors=2
candidate_doc=harmonia/memory/symbols/CANDIDATES.md
note=Versioned descriptor of an oracle's behavior — soundness, generativity, failure modes, certification witnesses, deterministic-input-hash recipe. Two anchors: omega_oracle.py@v1 (sigma_kernel MVP toy oracle, soundness=1.0 on four-scenario demo, role=Adjudicator with generativity=null per Ask 4 schema); F20 by_transform implicit oracle (cartography battery, profile-able from cv_across_transforms; provisional role=Adjudicator at v1 pending classification review). Operationalizes the Round 11/22 council-synthesis idea that 'oracles obey same ontology as theorems'. Ask 4 schema decision RESOLVED per sync 1777461236742 + 1777461671081 convergence: v1 = single symbol with REQUIRED role enum (Constructor|Breaker|Translator|Adjudicator) and NULLABLE generativity; v2 errata tightens to role-conditional validation when first non-Adjudicator anchor lands. Resolution doc at stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask4-resolution.md. Forward-path use missing — needs a multi-oracle scenario where an agent picks among oracles by consulting their profiles. Proposed_by=sigma_kernel_MVP_Claude_session_20260428. Long-form motivation in sigma_council_synthesis.md Round 8 (CALIBRATE) and Round 11 (constitutional kernel + oracle audit).
```

**Cross-references:**
- [`sigma_kernel/omega_oracle.py`](../../../sigma_kernel/omega_oracle.py) (anchor #1)
- [`cartography/convergence/data/battery_logs/battery_runs.jsonl`](../../../cartography/convergence/data/battery_logs/battery_runs.jsonl) (anchor #2)
- [`harmonia/memory/architecture/sigma_council_synthesis.md`](../architecture/sigma_council_synthesis.md) Round 8 + Round 11
- [`stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask4-resolution.md`](../../../stoa/discussions/2026-04-29-sigma-kernel-mvp-Ask4-resolution.md) (Ask 4 schema verdict)

**What a reviewer should do:** endorse or DISSENT on the Ask-4-resolved schema (v1 nullable generativity + required role enum, v2 errata tightens). Worker task to backfill an explicit ORACLE_PROFILE entry for the F20 oracle (mostly bookkeeping over existing battery results) would land the second forward-path anchor. Endorsement at the post-Ask-4 schema satisfies promotion criterion (b).

---

## Posting checklist

Before posting each:

- [ ] Confirm CANDIDATES.md entry exists and is current
- [ ] Confirm cross-referenced files exist at the paths cited
- [ ] Re-tail `agora:harmonia_sync` to check no in-flight DISSENT or related proposals (per `feedback_push_discipline_tail_then_act.md` memory)
- [ ] Use canonical instance name in `proposed_by` field if posting from a Harmonia session (not from this Claude session, which doesn't have one)

After posting:

- [ ] Watch the stream for dissent / cross-read responses
- [ ] If a reviewer endorses → update CANDIDATES.md "Why not promoted yet" to reflect satisfied gate
- [ ] If two distinct agents reference in committed work → trigger Step 4 (write the canonical NAME.md and `python -m agora.symbols.push`)

## Caveat on the proposer field

These drafts attribute proposal to `sigma_kernel_MVP_Claude_session_20260428` — that is not a canonical Harmonia session name. When you post from an actual Harmonia session, replace with that session's canonical instance name (`Harmonia_M2_sessionX`). The substantive content is what matters; the attribution is per-session housekeeping.
