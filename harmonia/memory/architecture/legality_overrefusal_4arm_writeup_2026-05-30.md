# Legality over-refusal across operations — 4-arm result + pre-registered replication

**Status: POSSIBLE / UNREPLICATED. Single n=40 draw per cell. Anthropic credits
exhausted before the planned replication could complete. This doc preserves the
epistemic state and pre-commits the next experiment so the result is binding
when credits return.**

Anchors:
- Stress task: `bad3ay4wk` (4 arms, n=40/cell, effort=high pinned, 0 api-failures)
- Failed replications: `b11qt11yt` (output lost to redirect collision — see
  [`feedback_background_output_capture`](C:\Users\James\.claude\projects\D--Prometheus\memory\feedback_background_output_capture.md));
  `bmf822eb9` (480/480 api-failures — credit exhaustion, see below)
- Memory hub: `C:\Users\James\.claude\projects\D--Prometheus\memory\project_topological_falsification_engine.md`
- Code: `D:\Prometheus\harmonia\experiments\run_stress_test.py`,
  `D:\Prometheus\harmonia\experiments\run_legality_replication.py`,
  `D:\Prometheus\harmonia\experiments\reasoning_phase0.py` (generators)

---

## 1. The data (verbatim from `bad3ay4wk`, n=40/cell, effort=high pinned)

| Arm | Operation | Opus 4.8 | 95% CI | Sonnet 4.6 | 95% CI | Opus over-refusals | Sonnet over-refusals | CIs overlap? |
|---|---|---|---|---|---|---|---|---|
| 1 | sqrt-ph0 `√(x+a)=x-b` | **0.97** (39/40) | [0.87, 1.00] | 1.00 (40/40) | [0.91, 1.00] | 1 | 0 | yes |
| 2 | rational `(x²-c²)/(x-c)=k` | 0.95 (38/40) | [0.83, 0.99] | 1.00 (40/40) | [0.91, 1.00] | 2 | 0 | yes |
| 3 | abs `\|x-a\|=b-x` | 0.82 (33/40) | [0.68, 0.91] | 0.93 (37/40) | [0.80, 0.97] | 7 | 3 | yes (barely) |
| 4 | **log `log(x)+log(x-a)=log(b)`** | **0.62** (25/40) | **[0.47, 0.76]** | **1.00** (40/40) | **[0.91, 1.00]** | **15 (15/15 errors)** | 0 | **NO** |

**What "over-refusal" means precisely:** the model returns the empty solution set
(declares "no solution") for a probe whose ground truth has at least one valid
root. It's a wrong answer in a specific shape — *over-pruning a legal root*. The
grader's `_kill_pattern == "over_refused"` produces this count deterministically.

**Why Sonnet's 40/40 on log matters as a control:** I wrote `gen_log_extra` in
this session. If its ground truth were buggy, Sonnet would also fail. Sonnet's
flawless 40/40 on log validates the ground truth → Opus's 15 over-refusals are
genuine model behavior, not a grader artifact. (Same logic for sqrt/rational.)

---

## 2. What the 4-arm result *suggests* (and what it does not yet license)

### 2.1 The suggestive pattern

Reading down the arm column, **over-refusal counts climb monotonically**: 1 → 2
→ 7 → 15. Accuracies fall: 0.97 → 0.95 → 0.82 → 0.62. Sonnet stays near-ceiling
throughout. This is the *opposite* of what a memorization story predicts
(memorization would peak on the canonical sqrt form, which here is the
weakest signal). It is consistent with a story where Opus 4.8 over-prunes legal
roots, and the over-pruning scales with how legality-loaded the operation is.

### 2.2 Three caveats that load-bear

**(a) The sqrt cell flipped run-to-run, same seed/config.**
The prior 2-arm stress run (recorded in the memory hub) gave sqrt Opus = 0.85
(n=40, 6 over-refusals). This 4-arm run on the same seed/config gave 0.97 (1
over-refusal). Opus is stochastic — temperature isn't pinned to 0, adaptive
thinking introduces sampling — so a single n=40 estimate of a per-cell rate is
demonstrably noisy at the level of ±0.12. **This is direct evidence that the
n=40 per-cell estimates in the table above are not point-stable.** The log gap
is large (0.62 vs 1.00, non-overlapping CIs) so it is likely to survive
re-sampling — but "likely" is not "confirmed."

**(b) The "domain-constraint load" ordering is POST-HOC.**
After seeing the 1→2→7→15 climb, I noted that the operations have, in roughly
that order, 1, 1, 1, 2 independent domain conditions on the candidate (sqrt:
radicand≥0; rational: denom≠0; abs: RHS≥0; log: each log argument > 0). That
count was assigned *after* seeing the data — it is a description of the
gradient, not a prediction of it. The legality-load story becomes *predictive*
only when a pre-registered higher-dcl arm produces a still-larger gap. See §4.

**(c) N=2 models, narrow generator families.**
Opus 4.8 vs Sonnet 4.6 cannot ground a claim about "frontier models." Each
"arm" is a single generator family with one canonical shape. Even if log
replicates across seeds, it might not generalize to other log-shapes
(`log_a(...) = log_a(...)` with non-base-e, or compound log expressions).

### 2.3 What this licenses RIGHT NOW

- **A POSSIBLE candidate finding:** "Opus 4.8 over-prunes legal roots on some
  domain-constrained equation operations; the over-pruning may scale with the
  number of independent domain conditions; sharpest on log; absent on sqrt this
  draw (was present last draw)."
- **Not** a calibrated tier. Not a "legality-execution axis." Not a "double
  dissociation with R8." All of those wait for replication + the predictive
  dcl=3 test (§4).
- **A clean reversal of my earlier retraction.** The earlier claim "narrow,
  sqrt-construction-specific quirk that does NOT generalize" was based on a
  2-arm view that included rational (where the gap was small in the earlier
  run). The 4-arm view shows the gap exists on rational/abs/log too, weakly on
  sqrt this run — so "doesn't generalize" was wrong. Updated to POSSIBLE; not
  promoted further.

---

## 3. Pre-registered replication protocol (binding once credits return)

Pre-committing decision rules *before* the next run is the standard guard
against selective reading. I am pre-committing these here, today, before the
data exists.

### 3.1 Arms

1. **log-2arg** (replication of the 4-arm log arm): `log(x) + log(x-a) = log(b)`,
   same `gen_log_extra` as in `bad3ay4wk`. **dcl = 2** by the post-hoc count.
2. **abs-clean** (replication of abs, filtered to gt-nonempty probes only — see
   §5.1): `|x-a| = b-x` with `a ≤ b` so the unique solution `(a+b)/2` exists.
   This isolates over-pruning from the "detect no-solution" skill that confounds
   the original abs arm. **dcl = 1.**
3. **log-3arg** (the predictive test): `log(x) + log(x-a) + log(x-b) = log(c)`,
   new generator `gen_log_extra_3arg` (§5.2). **dcl = 3** by the post-hoc count.

### 3.2 Conditions

- Seeds: **20260601, 20260602, 20260603** (committed; do not redraw on failure)
- N = **40 per cell**
- effort = **"high"** (pinned, ruling out C-THINK)
- Models: `claude-opus-4-8`, `claude-sonnet-4-6` (use_thinking=True, adaptive)
- Same probes across both models per cell (apples-to-apples)
- API failures (`api_error:*`) excluded from accuracy/morphology (per
  established discipline; recorded separately)

### 3.3 Decision rules (binding)

For each arm: pool the three seeds into a single 120-cell estimate, compute
Wilson 95% CIs, and a two-sided Fisher exact comparing Opus correct-rate to
Sonnet correct-rate.

**The log-replication finding (Opus over-refusal on log):**
- **REPLICATES** ⟺ pooled Opus accuracy ≤ 0.75 AND pooled Sonnet accuracy ≥ 0.95
  AND pooled Fisher p < 0.01 AND ≥ 80% of Opus errors classified `over_refused`.
- **DIES** ⟺ pooled Opus accuracy > 0.85 OR pooled Fisher p > 0.05 OR per-seed
  Opus accuracy variance > 0.20 (range across the 3 seeds) — the last is the
  "another sqrt-style draw" condition.
- **AMBIGUOUS** ⟺ neither the REPLICATES nor DIES condition triggers. Report
  the failure shape, do not promote.

**The legality-load predictive test (dcl monotonicity):**
- **CONFIRMS dcl-monotonicity** ⟺ pooled Opus accuracy on log-3arg is *strictly
  lower* than on log-2arg AND log-2arg accuracy is *strictly lower* than on
  abs-clean, with non-overlapping 95% CIs at each step.
- **FALSIFIES dcl-monotonicity** ⟺ log-3arg accuracy ≥ log-2arg accuracy
  (within CI overlap). The post-hoc story dies and the result reverts to "Opus
  over-refuses on log specifically, mechanism unknown."
- **PARTIAL** ⟺ ordering correct but CIs overlap. Report as suggestive; not
  predictive.

**The double dissociation (conditional on log replicating):**
- Re-run R8 (lemma selection) at n=30 with the same seeds to confirm the
  earlier Opus 1.00 > Sonnet 0.87 finding holds.
- **DISSOCIATION STANDS** ⟺ log REPLICATES (above) AND R8 confirms Opus >
  Sonnet at p < 0.10 (looser threshold — the earlier result was not strongly
  significant either).
- **DISSOCIATION DIES** ⟺ either half fails.

### 3.4 Cost

- Per arm: 3 seeds × 2 models × 40 = 240 calls. Three arms = **720 Anthropic
  calls** at effort=high.
- R8 confirm: 30 probes × 2 models = **60 calls**.
- **Total: ~780 Anthropic calls.** Lesson from 2026-05-29: a ~960-call burst
  drained the balance. Top up enough to comfortably absorb 800+ calls before
  launching.

---

## 4. The "dcl monotonicity" hypothesis, stated for falsification

**H1 (legality-load):** Opus 4.8's over-refusal rate on domain-constrained
extraneous-root equations is monotone non-decreasing in the number of
independent domain conditions on the candidate solution.

**Operationalization:** `dcl(operation)` = the count of independent inequalities
on `x` (or on functions of `x`) that the operation requires the candidate to
satisfy for the answer to be valid. (Examples — `√(x+a)=x-b` ⇒ dcl=2 if we
include both `x+a ≥ 0` and `x-b ≥ 0`; conservatively dcl=1 if we count only the
radicand. **This counting itself is a free parameter the experiment must pin
down.** §5.2 builds log-3arg with an unambiguous dcl=3 to give the prediction
*some* arm where the count cannot be tweaked.)

**Falsifier:** the log-3arg arm produces Opus accuracy ≥ log-2arg accuracy.

**Predictions H1 must commit to:**
- log-3arg Opus < log-2arg Opus < abs-clean Opus (strict, CI-separated).
- Sonnet stays near-ceiling on all three (else gap is not Opus-specific).
- Errors on log-3arg dominated by `over_refused` (else "Opus collapses on
  hard problems" generally, not legality over-pruning specifically).

**Mechanism honesty:** even if H1 confirms, this is a *descriptive* law over
generated equation families, not a *causal* claim about training-data balance,
RLHF on hallucination penalty, or any other internal of Opus 4.8. Causal
mechanism is the next layer of question and is not addressed here.

---

## 5. Generator work owed before the replication

### 5.1 abs-clean: filter to a ≤ b only

Current `gen_abs_extra` mixes solvable (`a ≤ b`, gt=`[(a+b)/2]`) and unsolvable
(`a > b`, gt=`[]`) probes. The unsolvable ones make "no solution" the *correct*
answer; including them confounds over-refusal with correct-detection. For the
H1 instrument I need every probe to have a valid root, so "no solution" is
unambiguously wrong (= over-refusal). Action: add a filter or a new generator
`gen_abs_extra_clean` that emits only `a ≤ b` cases.

### 5.2 log-3arg: the dcl=3 predictive arm

New generator: `gen_log_extra_3arg` emitting
`log(x) + log(x-a) + log(x-b) = log(c)` with 0 < a < b chosen so the cubic
`x(x-a)(x-b) = c` has at least one real root with x > b (the most-constrained
domain region). Ground truth: solve the cubic over the reals via sympy.solveset
restricted to `x > b`. By construction this carries three independent domain
conditions (`x > 0`, `x - a > 0`, `x - b > 0`) — an unambiguous dcl=3 that
cannot be tweaked downward by recounting.

Both generators get a small unit-test file that verifies ground truth against
direct substitution on at least 5 generated probes per kind, no LLM in the
loop. (Same discipline as `test_zoo_matrix.py` / `test_r12.py`.)

*(RESOLVED 2026-05-30 — shipped: `gen_abs_extra_clean` + `gen_log_extra_3arg`
in `reasoning_phase0.py`, `test_legality_generators.py` substitution-based.)*

### 5.2.1 Ground-truth audit on the binding seeds  *(2026-06-05, Harmonia C)*

The §5.2 unit test originally exercised only the authoring seed `20260530`,
while the binding replication (§3.2) runs on `20260601/02/03`. A guard that
does not cover the seeds the experiment runs is a guard that doesn't guard —
the `gen_log_extra_3arg` rejection sampler can fall through after 30 tries and
emit an unguarded `(a,b,c)` whose cubic has a *second* in-domain root,
silently making "no solution" a partially-correct answer and poisoning the
over-refusal count.

Audited independently before credits return:
- **3 binding seeds (`20260601/02/03`):** 160 probes each, **0 poisoned**
  (numpy `roots` + substitution: unique in-domain root == p on every probe).
- **3000-seed stress scan:** **0 poisoned probes** — the fall-through never
  fires for these parameter ranges (`a∈[1,4]`, `b=a+[1,4]`, `p=b+[1,5]`); the
  `disc<0`-or-both-roots-out-of-domain accept condition is reliably hit inside
  30 tries.

The ground truth is sound. `test_legality_generators.py` was then hardened to
parametrize over all four seeds (`_SEEDS = (20260530, 20260601, 20260602,
20260603)`) so the result is pinned against regression: **2494 passed, 0
failed**. The replication is now code-clean to launch the moment Anthropic
credits return — no generator or ground-truth work stands between credits and
data.

### 5.3 Unify the over-refusal label  *(RESOLVED 2026-05-30)*

`run_stress_test.py` Arm 1 used `classify_r2` which emitted `"over_refuses"`
(plural). Arms 2–4 use `grade()._kill_pattern` which emits `"over_refused"`
(singular). The replication's pooled counts must use a single canonical label.
**Fixed:** `morphology.py` now emits `"over_refused"` everywhere
(`replace_all`), and the `run_stress_test.py` READ message string was updated
to match. The replication code (`run_legality_replication.py:101`) already
keyed on the singular form, so its pooled counts are now consistent with
Arm 1 too.

---

## 6. What stays in the air

Everything in §3 and §4. Specifically:
- The log finding's status is **POSSIBLE / unreplicated**.
- The "legality-load" gradient is **a post-hoc description**, not yet a
  predictive law.
- The double dissociation is **conditional on the replication succeeding AND
  the R8 result reconfirming**.
- All claims are about **two specific Anthropic models** as of 2026-05-29 and
  generalize **only** if the model zoo (Anthropic-independent;
  `run_zoo_matrix.py`) shows the same pattern in held-out families. Per the
  reviewer consensus, the zoo is the binding test for the "basis-not-ladder"
  question — the within-Anthropic-trio dissociation is a *suggestion*, not
  evidence about reasoning architecture in general.
