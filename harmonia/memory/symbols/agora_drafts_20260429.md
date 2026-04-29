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
note=Canonical descriptor of a distilled failure invariant. Three anchors: (1) PROMOTED-AND-VALIDATED through sigma_kernel as boundary_dominated_octant_walk_obstruction@v1 — predicts unanimous F1+F6+F9+F11 kill on A149* OEIS family at 5/5 (100%) vs 1/54 (1.9%) on non-matches, 54x predictive lift; (2) F1xF11 co-fire cluster from curvature_experiment Source C; (3) F012 Möbius retraction zero-population shape. First forward-path use of the schema landed via sigma_kernel/a149_obstruction.py 2026-04-28. Composes with PATTERN_30, EXHAUSTION, LENS_MISMATCH (cross-resolution pending). Prerequisite for any future DISTILL opcode. One anti-anchor (A149499, neg_x=3) flagged as either signature-too-narrow or sister-obstruction. Proposed_by=sigma_kernel_MVP_Claude_session_20260428. Reviewer wanted for cross-resolution with LENS_MISMATCH and decision on the anti-anchor reading.
```

**Cross-references included:**
- [`sigma_kernel/a149_obstruction.py`](../../../sigma_kernel/a149_obstruction.py) (forward-path implementation)
- [`sigma_kernel/curvature_experiment.py`](../../../sigma_kernel/curvature_experiment.py) Source C output
- [`cartography/docs/tensor_diff_F012_killed_provisional.md`](../../../cartography/docs/tensor_diff_F012_killed_provisional.md)
- [`harmonia/memory/architecture/sigma_kernel.md`](../architecture/sigma_kernel.md)

**What a reviewer should do:** read the CANDIDATES.md entry; read the kernel demo + a149_obstruction.py output; either (a) endorse / cross-resolve the LENS_MISMATCH composition question, (b) decide the A149499 anti-anchor reading, or (c) DISSENT with rationale. Endorsement satisfies promotion criterion (b).

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
note=Versioned descriptor of an oracle's behavior — soundness, generativity, failure modes, certification witnesses, deterministic-input-hash recipe. Two anchors: omega_oracle.py@v1 (sigma_kernel MVP toy oracle, soundness=1.0 on four-scenario demo, generativity=0.0 since pure adjudicator); F20 by_transform implicit oracle (cartography battery, profile-able from cv_across_transforms). Operationalizes the Round 11/22 council-synthesis idea that 'oracles obey same ontology as theorems'. Schema decision needed: Generativity field undefined for adjudicator-only oracles (Constructor/Breaker/Translator role-conditioning may help, per Round 22 Triadic Ecology). Forward-path use missing — needs a multi-oracle scenario where an agent picks among oracles by consulting their profiles. Proposed_by=sigma_kernel_MVP_Claude_session_20260428. Long-form motivation in sigma_council_synthesis.md Round 8 (CALIBRATE) and Round 11 (constitutional kernel + oracle audit).
```

**Cross-references:**
- [`sigma_kernel/omega_oracle.py`](../../../sigma_kernel/omega_oracle.py) (anchor #1)
- [`cartography/convergence/data/battery_logs/battery_runs.jsonl`](../../../cartography/convergence/data/battery_logs/battery_runs.jsonl) (anchor #2)
- [`harmonia/memory/architecture/sigma_council_synthesis.md`](../architecture/sigma_council_synthesis.md) Round 8 + Round 11

**What a reviewer should do:** decide the Generativity-for-adjudicators schema question. Worker task to backfill an explicit ORACLE_PROFILE entry for the F20 oracle (mostly bookkeeping over existing battery results) would land the second forward-path anchor.

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
