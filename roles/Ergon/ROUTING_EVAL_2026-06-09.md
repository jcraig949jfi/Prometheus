# Routing eval — does mined-failure residue carry navigable routing signal? (preregistration + results)

**Role:** Ergon (the Learner march). **Date:** 2026-06-09. **Status at write-time:** PREREGISTERED, not yet run.

This is the first eval for the Learner's *actual* north-star objective: **route by failure** —
given a problem the base model gets wrong, predict which mined-failure tool ("scrap") solves it.
Every prior Learner result (greedy-LoRA, compute-traces) was on the narrow gold-judgement /
compute-accuracy metric, which the kill (`feedback_greedy_lora_surface_not_reasoning`) showed is
surface. This eval opens a **new measurement axis** aligned with the failure-metabolization
doctrine (`feedback_failure_metabolization_doctrine`, `feedback_residue_must_be_navigable_not_logged`):
is the residue *navigable*, or merely logged?

## Seed artifact (verified in-repo, durable)

`agents/hephaestus/failure_mining_results.json` — 80 scrap records, each:
`{file, concepts(3), scrap_acc, solves_wrong, breaks_right, orthogonality, wrong_probes_solved}`.
`wrong_probes_solved` = the probes (= base-model-wrong "trap" problems) that adding this scrap fixes.

### What is verified vs unverifiable (this gates the design)
- **VERIFIED / durable:** the bipartite **solve matrix** (scrap × probe-index). Probe indices are
  consistent across all 80 scraps (one battery was used for all), so co-occurrence is real even
  without knowing what each probe *is*. Scrap `concepts` (pool 83) and `concept_fields` (pool 20,
  from the sibling `scrap/*.json`, available for 63/80) are durable scrap features.
- **UNVERIFIABLE → excluded from design:** probe *identity/text*. The traps are generic reasoning
  traps (numeric_comparison, modus_tollens, conjunction_fallacy, … 28 categories via
  `trap_generator.generate_trap_battery`), but the current generator yields 64/96/128 traps at
  n_per_category 2/3/4 — **never the 84 implied by the index range**, and the mining *producer is
  not in-repo*. So probe index→text alignment cannot be confirmed. Reconstructing probe features
  would build the eval on an unverifiable assumption (the exact failure mode the doctrine warns
  against). **We therefore make no claim about unseen/new probes** — this is in-distribution routing.

### Matrix description (data, not result)
- 80 scraps × 84 probe-slots; **45 probes active** (39 never solved by any scrap).
- Density 0.118; each scrap solves 7–10 probes — **capped at 10 → top-10 truncation per scrap.**
- Probe popularity severely skewed: median 1, a few probes solved by 36–47 of 80 scraps.

## Hypotheses

- **H_B (structure exists):** the solve matrix has navigable structure beyond per-probe popularity
  — i.e. scraps cluster such that knowing some of a scrap's solves predicts the rest better than
  the popularity prior. (Warm-start matrix completion; feature-free.)
- **H_A (structure is concept-addressable — the north-star one):** a scrap's **fields** predict
  **which** probes it solves, beating popularity, with *no* solves of the query scrap revealed.
  (Cold-start routing by features.) This is the test that says the Learner could route a *tool* to
  *problems* from its concepts alone.

## Design

Two evals, leave-one-scrap-out, on the active-probe set (45 probes). Primary metric **ROC-AUC**
(rank a held-out scrap's solved vs unsolved probes); secondary **Average Precision** and **Recall@10**.

- **Eval A — cold-start feature routing (tests H_A).** Held-out scrap q, *zero* of its solves
  revealed. Score probe p by field-weighted neighbour vote:
  `score_A(p) = Σ_{train s} sim(fields_q, fields_s) · solves(s,p)`, sim = Jaccard on fields.
  Baseline **POP**: `score_POP(p) = Σ_{train s} solves(s,p)` (sim≡1; field-blind popularity).
  FEATURE beats POP ⟺ field-weighting adds routing signal. Runs on the 63 field-joined scraps.
- **Eval B — warm-start collaborative completion (tests H_B).** Reveal a random half of q's solved
  set R_q; predict the held-out half among unrevealed probes. neighbour sim = Jaccard(R_q, R_s) on
  revealed probes; `score_B(p) = Σ_s sim·solves(s,p)`. Baseline POP on the held-out half. Feature-free.

### Instrument validation (run BEFORE trusting real-data verdict)
- **Positive control:** synthetic matrix where field *determines* solves (each field → a fixed probe
  block). Require FEATURE ≫ POP (AUC →~1.0). Confirms the harness can detect routing when present.
- **Negative control:** real solve matrix with fields **shuffled** across scraps. Require
  FEATURE ≈ POP (ΔAUC ≈ 0). Confirms FEATURE has no mechanical advantage absent real field→solve link.
- **Floor check:** POP-vs-itself / random predictor ⇒ AUC ≈ 0.5.

### Statistics
5 fold-split seeds; report mean ± sd AUC. Paired FEATURE−POP per held-out scrap, Wilcoxon signed-rank.

### Kill / verdict conditions (preregistered)
- **H_A NULL** if Eval-A FEATURE AUC ≤ POP AUC (ΔAUC ≤ 0 or Wilcoxon p > 0.05). Verdict: *this
  failure-mining artifact does not carry routing signal navigable by the concept/field handle.*
- **H_B NULL** if Eval-B COLLAB ≤ POP. Verdict: *no navigable low-rank structure beyond popularity.*
- A clean NULL is a real north-star result (per `feedback_assume_wrong`, kills are the output): it
  says the Learner cannot route from this artifact, and points to what a router-grade artifact needs
  (probe features + no top-10 truncation + denser tail).

### Preregistered caveats
1. **Top-10 truncation** inflates POP and under-observes the tail → biases *against* finding routing
   signal (conservative; surviving signal is trustworthy, a NULL is partly truncation-limited).
2. **No probe identity** → no unseen-probe generalization claim; in-distribution only.
3. **Small N** (80 scraps; 63 with fields; 45 active probes) → modest power; report effect size not
   just significance.

---

## RESULTS (run 2026-06-09; `ergon/learner/eval/routing_eval.py`, deterministic, 5 seeds)

Data: 80 scraps × 45 active probes (84 slots); fields on 63/80.

**Instrument validation — PASSED (verdicts trustworthy):**
- Positive control (field ⇒ solves): FEATURE AUC 0.956±0.072 vs POP 0.618±0.174 — harness
  detects routing when present.
- Negative control (fields shuffled): FEATURE 0.743 ≈ POP 0.753, ΔAUC −0.010 — no mechanical
  advantage absent a real field→solve link.
- Floor: AUC≈0.5 for random (by construction of the metric).

**H_A — cold-start feature routing: NULL.**
- FEATURE AUC 0.744±0.151 vs POP 0.753±0.157; ΔAUC = **−0.009**, bootstrap P(Δ≤0)=0.93.
- Recall@10: FEATURE 0.437 vs POP 0.420 (n.s.).
- **Decisive:** real fields (0.744) ≈ *shuffled* fields (0.743). The concept/field metadata
  carries **no routing signal over popularity**. You cannot route a tool to problems from its
  concept labels.

**H_B — warm-start collaborative completion: SUPPORTED, and robust.**
- COLLAB AUC 0.829±0.162 vs POP 0.754±0.153; ΔAUC = **+0.075**, bootstrap P(Δ≤0)<0.0001.
- **Adversarial tail check** (drop top-8 popular probes from candidates): COLLAB 0.829 vs POP
  0.746, ΔAUC **+0.082**, P<0.0001 — structure **SURVIVES** in the tail. Not a popularity/head
  artifact: it is genuine scrap-clustering.

## VERDICT & directional pointer (per `feedback_failure_signal_vector_field`)

The mined-failure residue **is navigable — but the navigable handle is BEHAVIORAL, not SEMANTIC.**
- Navigable structure beyond popularity exists (H_B): tools that co-solve some problems co-solve
  others, robustly into the tail. Routing-by-failure is possible *in principle*.
- That structure is **not** addressable by the human concept/field labels (H_A NULL): metadata
  routing is dead — real fields are no better than random fields.

**Implication for the Learner / north star:** a Learner can route by failure **only with behavioral
observations of tools (warm-start)** — what a tool actually fixes — not from its concept metadata
(cold-start). The true objective (route a *new problem* → tool) remains untestable here because the
artifact lacks **probe/problem features** and is **top-10 truncated**. Those two gaps are now the
precise spec for a router-grade artifact: (1) emit *full* per-scrap solve sets (no top-N cap);
(2) persist probe/problem features (text/concepts) so cold-start problem→tool routing becomes
measurable. This NULL+POSITIVE split is the first behavior-delta on the Learner's real objective
and points at exactly what to instrument next, rather than more surface-metric LoRA runs.

— Ergon, 2026-06-09
