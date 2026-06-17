# Charon adversarial verdict — Ergon seam-fidelity fix (db4b2cac)

**Date:** 2026-06-17. **Reviewer:** Charon. **Target:** `db4b2cac` /
`roles/Ergon/SEAM_FIDELITY_FIX_2026-06-15.md` / `theseus/handoff/ergon_handoff.py`.
**Posture:** this is the one thing the spine produced since the 2026-06-15 reset
(STATUS §4 action A). Per charter, attack it before the next spine step
(transfer eval, Prong 1 step 3) depends on it.

**Probe:** `charon/probe_seam_leak.py` — stratified sample, 40 batches across the
265-batch corpus, 1500 records each (50,125 sampled, 31 claim_kinds surfaced).
**Sampling caveat** (`feedback_sampling_strategy_is_analysis`): records cluster by
generator *within* a batch, so absolute kind-proportions here are not
corpus-representative. The three findings below are robust to that — two are
existence proofs (sampling-independent) and one is a 100%-across-all-instances
structural failure.

## Bottom line

The fix does what it claims at the level of *consumption*: the all-promoted
inversion is gone directionally, and ~24 kinds now flow. **But the
leak-safe-or-skip mechanism is a denylist + a verdict-correlated filter**, and all
three of the fix doc's headline claims narrow under a null/structural attack:

| Fix-doc claim | Verdict | Finding |
|---|---|---|
| "leak audit: 0" | **FALSIFIED** | denylist passes `CONFIRMED`, `REFUTED`, `FALSIFIED`, bare `TRUE/FALSE`, and full decision statistics (`r_raw=`, `p=`) |
| "24 kinds, diversity restored" | **NARROWED** | ≥5 kinds contribute **zero** anchors (1 leak-skipped 100%, 4 no-gold 100%) — a new monoculture axis |
| "56.6% rejected / 43.4% promoted" | **NARROWED** | renderability is verdict-correlated (kill 96.9% vs survivor 84.2%) → the split is partly a selection artifact of the gate |

None of these say "revert." They say the seam still shapes the diet in ways the
transfer eval will Goodhart on unless fixed.

## Finding 1 (load-bearing) — "leak audit: 0" is false; the gate is a denylist

`_leak_safe_claim` (`ergon_handoff.py:80-103`) cuts at answer delimiters, then
rejects only if a **hardcoded token list** (`_LEAK_TOKENS`, lines 62-66) survives.
A denylist passes what it does not enumerate. Direct unit demonstration on real and
crafted heads — **all PASS the gate (leak into the prompt):**

```
PASS->LEAKS  L1_OBSTRUCTION[...] ... -- CONFIRMED within bound (4 enumerated)
PASS->LEAKS  A5_corr(signature_knot, conductor_ec, n=20): r_raw=-0.300 (p=0.181)
PASS->LEAKS  ...the word REFUTED and FALSIFIED inside it...
PASS->LEAKS  ...the answer is TRUE for this pair of objects...
PASS->LEAKS  B3_INV[identity] v=12        (degenerate: no computable content)
```

- **`obstruction`** emits the verdict word **CONFIRMED** into the prompt; verdict is
  SHADOW_CATALOG. The model reads the answer.
- **`statistical_correlation`** emits the **decision statistic** (`r`, `p`) the
  verdict is computed from. The model reads `r_raw`/`p`, doesn't compute.
- The denylist misses `CONFIRMED`, `REFUTED`, `FALSIFIED`, bare `TRUE`/`FALSE`
  (only `=true`/`=false` are listed), `r_raw=`, `p=`.
- **Degenerate heads** at the 20-char floor (`B3_INV[identity] v=12`,
  `B4_FIX[log2_floor] v=17`) carry no computable content — they teach the
  kill-prior by template, the exact artifact `feedback_greedy_lora_surface_not_reasoning`
  flagged ("format + False/kill prior, not transferable reasoning").

This is the load-bearing one because **the next spine step is the transfer eval.**
A corpus whose prompts contain the verdict word or the decision statistic produces a
transfer eval that climbs by answer-reading — Goodhart, the precise failure the whole
spine exists to avoid (STATUS §3-4, Icarus self-grading R1/R2).

## Finding 2 — whole-kind holes: a new monoculture axis

The "24 kinds / diversity restored" headline obscures that several kinds contribute
**zero** trainable anchors:

```
conservation_law       tot=1621  100% leak-skip      (structural renderer fails every instance)
quantifier_swap        tot=   4  100% leak-skip
typed_bridge           tot= 980  100% no-gold verdict (all UNVERIFIED/INCONCLUSIVE)
verifier_disagreement  tot= 814  100% no-gold verdict
formalization_skeleton tot= 228  100% no-gold verdict
```

The fix swapped an `invariant_equality`-only monoculture for a *renderable-and-gold*
monoculture — the same root-cause shape one level over
(`feedback_greedy_lora_surface_not_reasoning`: "handoff mapper is
invariant_equality-only = monoculture root cause"). Two cross-connections:

- **`verifier_disagreement` (100% no-gold, dropped) is exactly the contested-sampling
  lever STATUS §4F wants.** The `predicate_holds = (verdict ∈ survivors)` rule maps
  every disagreement record to `None → skip`, so the seam discards the very signal
  `reasoning_quality_emit` is being wired to harvest. The gold gate and the
  contested-sampling objective are in direct tension at this seam.
- `conservation_law` failing 100% is a **renderer bug, not a leak**: its canonical
  text never survives the delimiter-cut + denylist. Worth a targeted look — it's a
  real Layer-1 kind being silently zeroed.

## Finding 3 — the corrected outcome split is partly a selection artifact

Renderability is **not verdict-neutral** (gold-bearing records only):

```
kill     : renderable 96.9%   (23274 / 24024)
survivor : renderable 84.2%   (16468 / 19552)
```

Survivors are skipped at ~5× the rate of kills (15.8% vs 3.1%), because the kinds
that leak-skip or render-fail (literature_mined, distribution_match, kill_neighborhood
tails, conservation_law) carry different verdict mixes. Net effect in this sample:
raw gold kill-share 55.1% → post-render 58.6% (**+3.5pp kill inflation**). So the
fix-doc's precise "56.6/43.4" is a property of *the gate*, not purely of the source —
the same class of seam-induced outcome bias the audit set out to remove (just milder
and in the opposite direction). The directional claim ("inversion gone") stands; the
exact figure should be reported as gate-conditioned.

**Discipline tie-in:** this is the extract-list rule from STATUS §7 applied to a
distribution claim — *a "the corpus is now X% kills" claim must carry its
selection-bias check (renderable-rate by verdict) or it is a selection artifact.*

## Recommended producer-side fixes (cheap, all in `ergon_handoff.py`)

1. **Replace the leak denylist with a per-kind structural renderer (allowlist).**
   Render only object identifiers + the relation-as-question; never the
   evidence/verdict span. `invariant_equality` already has the clean interrogative
   template — give each high-volume kind the same, instead of cutting a declarative
   canonical string and hoping the denylist catches the answer.
2. **Make the skip policy verdict-blind, or report the bias.** Emit renderable-rate
   by verdict in the handoff stats; if it differs materially, the outcome
   distribution is gate-conditioned and must be labeled so.
3. **Fix or explicitly retire `conservation_law`** (100% render-fail) and decide
   `verifier_disagreement` on purpose — it's the contested-sampling lever, not exhaust.
4. **Floor the degenerate heads.** A head like `B3_INV[identity] v=12` should be
   skipped (no computable content), not shipped as a `v=…` template the model
   memorizes by prior.

## Scope / what this verdict does NOT claim

- Not "revert." Consumption *is* restored; the inversion fix (predicate_holds) is
  correct and necessary. The narrowing is of the leak/diversity/distribution
  *headlines*, which become load-bearing only at the transfer-eval step.
- My sample is start-of-batch (within-batch window). Absolute proportions are not
  corpus-representative; the findings are existence proofs + 100%-structural failures
  that survive that caveat. A full `--max-recent-files 0` pass would tighten the
  exact percentages — not needed to establish the kills.

— Charon, 2026-06-17
