# Reasoning-Quality Emit Spec v0.1 — persist the per-evaluator vector

**Filed:** 2026-06-08
**Author:** Aporia (in-session, with James)
**Status:** Spec / preregistration. The minimal substrate change that lets the
*validated* relational H-R1 instrument finally test the reasoning claim on real data.
**Parents:** `reasoning_steering_protocol_v0.3_relational_correction.md` (the
instrument), `stage0b_emit_schema_freeze.md` (the Stage-0b emit discipline),
`feedback_no_naive_score_combination` (the failure this explains/fixes),
`feedback_anticorrelation_is_not_noncyclicity` (the screen), `feedback_substrate_passive_consumer_warning`
(every doc → a behavior delta).

---

## 0. The problem (root cause, now precise)

Five times this session the substrate had a real finding-in-memory but the underlying
multi-evaluator data was not on disk (Mahler done; kill ledgers thin; learner corpus
categorical; quality dims unpopulated; **Walk-Z/PRM head scores never persisted**). The
common root cause: **the substrate computes per-head reasoning scores, COMBINES them into
one scalar (or one verdict), and persists only the combined value.** The per-evaluator
vector — the only thing the relational H-R1 instrument and the curl diagnostic can read —
is discarded at write time.

Consequence: the *reasoning* claim of H-R1 ("is reasoning-difficulty non-scalar?") and the
*reward* diagnostic from path B ("is a combined reward < best-single because of curl?")
are both **untestable on real data** — not for lack of an instrument (it is validated:
Efron dice → 0.99 curl, planted n=30 cycle → BEATS_NULL p=0.005), but for lack of emitted
data.

---

## 1. The minimal change (one sentence)

**Wherever ≥2 heads / judges / scorers evaluate the same reasoning candidate, persist the
per-evaluator score VECTOR — before any combination — alongside whatever combined value is
produced.** Nothing else changes; the combine step stays. We just stop throwing the
vector away.

---

## 2. The record (append-only JSONL, relational-pipeline-ready)

One line per (candidate, evaluation):
```
{
  "candidate_id":  "<sha1 of the reasoning state / step / solution>",
  "task_id":       "<problem / episode id>",
  "evaluator_scores": { "<evaluator_id>": <float>, ... },   // >= 2 keys; THE vector
  "combined":      <float|null>,        // whatever the substrate already computes
  "outcome":       "<correct|wrong|...>|null",   // ground truth if available
  "contested":     <bool>,              // did the evaluators split? (Section 4)
  "provenance":    { "scorer_versions": {...}, "born_at": "<iso>" },
  "emitter_version": "<code hash>"
}
```
`evaluator_scores` feeds the relational pipeline directly as `margins`. `evaluator_id`
must be a STABLE name per head/judge so the emitter-family-holdout null and the screen's
per-evaluator diagnostics work. Evaluators must be GENUINELY INDEPENDENT in provenance
(different bases / objectives / prompts) — re-prompts of one model correlate and reproduce
the g2c NULL with extra steps.

---

## 3. Integration points

Any existing site that already produces ≥2 reasoning scores per candidate, e.g.:
- reward modelling / PRM + auxiliary heads (the Walk-Z site — exactly where the data was
  discarded);
- multi-judge eval harnesses (several judges scoring one answer);
- the agent-verdict path (if ≥3 agents ever score shared candidates — currently only 2).
Instrument at the point *just before* combination. This is a logging change, not a
modelling change.

---

## 4. Contested-state sampling (the P(signal) lever)

Per the validated levers, curl is concentrated on **contested** candidates — where
evaluators split. Emit ALL contested candidates and a sample of the rest; set
`contested = true` when the evaluators do not agree on the top candidate (or pairwise
disagree). Uniform sampling dilutes contestedness and buries whatever curl exists (g2c's
mostly-uncontested draw is the cautionary tale). This is importance-sampling toward
disagreement.

---

## 5. The gate and the payoff (behavior delta)

On the emitted data, run `prescreen.signal_screen` (cheap), then the full relational H-R1
on PASS:
- **NULL** → reasoning-quality on this task family IS scalar-reducible; a single
  (best-aligned) head is sufficient; combining is fine.
- **BEATS_NULL** → the heads measure **non-weightable** dimensions; **scalar / linear reward
  combination is provably lossy** (path B: combined crashes below the best single head and
  below random). The substrate should then use a **vector-valued reward** (or select the
  best-aligned head), NOT average — and normalization will not save it.
Either way it is a falsifiable answer that changes how the substrate rewards reasoning —
the behavior delta. (Re-run of the path-B diagnostic, now on real data.)

---

## 6. What it unblocks

This is the precondition for H-R1 arms A (independent judges) and D (the actual heads) on
REAL reasoning data — the only place the non-conservativity thesis can still live (math
objects came up scalar on two fair tests). It is no-inference to SPECIFY and to LOG; the
heads already run. The first genuine chance to find curl where it might actually be.

---

## 7. Anti-patterns (each already cost us a NULL or a dead end)

- **Pre-combine and discard the vector.** The root cause. Persist the vector.
- **Uniform sampling.** Dilutes contestedness → buries curl.
- **Correlated evaluators** (one model re-prompted, theorem-coupled invariants). Use
  genuinely independent provenance; `feedback_anticorrelation_is_not_noncyclicity` —
  and remember anti-correlation alone is NOT enough; only the curl screen decides.
- **Normalize-and-hope.** If the cause is curl, no rescaling fixes it (path B).
- **Trusting absolute non_gradient_mass.** It carries a saturation floor; gate on BEATS-NULL
  / the screen, never on `> 0`.

— Aporia, 2026-06-08 (reasoning-quality emit spec v0.1)
