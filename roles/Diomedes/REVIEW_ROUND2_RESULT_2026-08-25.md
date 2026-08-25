# Diomedes — round-2 audit RESULT: nonlinearity adds nothing, the parity relation was carrying nothing, and one of my own gates was underpowered

**Filed:** 2026-08-25. **Pre-registration:** `REVIEW_ROUND2_PREREG_2026-08-25.md`, committed at
`ed859c7e` **before** either calculation ran. **Rows:** `review_round2_run.py` →
`review_round2_result.json`. **Corrections context:** `REVIEW_ROUND2_CORRECTIONS_2026-08-25.md`.

**The corpus KILL is unchanged and was never contingent on these.** Both calculations audit claims
already made. Per the reviewer's instruction, this is the end of work on the dead corpus.

**Language constraint C1 applies throughout:** every percentage below is *the fraction of the local
above-chance AUC span that an independent proxy mechanism reproduces*. **None of it is a
decomposition of the local model's performance**, and none of it is written as one.

---

## 1. A1-NL — nonlinear, cross-fitted proxy reconstruction. **BAND: PARTIAL.**

Gradient boosting, folds assigned by **candidate object identity** (5 folds), so no candidate's
tested invariant ever influences its own prediction. Hyperparameters frozen in the prereg; nothing
selected using the action-ranking result. Local `Z(x,a)` reference **0.7392**; permuted-companion
null **0.5000** exactly.

Pre-registered statistic — best of the four variants:

- literal binary **0.5546** · literal continuous **0.6065**
- full-18 binary **0.5501** · **full-18 continuous 0.6075** ← best
- proxy regression quality ρ **0.4431**

**0.6075 is inside the 0.55–0.65 PARTIAL band. It is reported as partial, with no rounding.**

**The headline finding of this audit is a negative one about my own hypothesis.** I predicted 0.62–0.70
and pre-committed to withdrawing the navigational reading outright if it cleared 0.65. **It did not.**
Against ridge's 0.5979, gradient boosting bought **+0.0096**. The proxy route is **not limited by
model class** — a learner that recovers generic tabular nonlinear relationships extracts essentially
nothing beyond what a linear map already extracted. The reviewer nominated this as the attack most
likely to overturn the disposition; it did not land, and that is worth more than my having argued
against it in advance.

Also notable: **full-18 ≈ literal** (0.6075 vs 0.6065). The entire admissible feature family adds
~0.001 over the three raw companion values. Whatever the proxy captures is already in `w(a)`.

## 2. A1-NL per relation — the reviewer's suspicion was correct

The concern was that a generic Euclidean margin might be smuggled into a modulo-2 oracle, inflating
the aggregate continuous score. **Split by relation, full-18:**

- **`abs_diff_le_3`** — binary **0.5634**, **continuous 0.6636**
- **`equal_mod_2`** — binary **0.5367**, **continuous 0.5515**

**The aggregate continuous number was carried almost entirely by the bounded-difference relation.**
On parity — which demands *exact* integer recovery, where 101 and 103 are equivalent against an odd
parent — the proxy sits near chance and the continuous score buys only 0.015 over binary.

This is the correct behaviour, not an artifact: the parity continuous score is **distance to the
nearest even integer**, not distance to the parent, so it cannot smuggle Euclidean structure into a
mod-2 predicate. The exact definitions are published in the prereg §1 and implemented in
`cont_score()`. That the two relations separate this sharply is evidence the construction is
relation-native.

**What it means.** For a bounded-difference oracle, an independent non-navigational proxy reproduces
performance equivalent to roughly two thirds of the local above-chance span. For a congruence oracle
it reproduces very little. **The proxy explanation is strong exactly where the oracle is a
coarse-grained numerical predicate, and weak where it demands exact arithmetic recovery.**

**I am not re-banding on the per-relation number.** 0.6636 would sit above the 0.65 gate, but the
pre-registered statistic is the best *aggregate* variant, and switching to a subgroup after seeing
where it landed is exactly the post-hoc branch selection I was corrected for in C3. The band is
PARTIAL. The per-relation split is reported because it was requested and because it is informative,
**not** as a route to a different verdict.

## 3. A1-NL-CORR — the band fired, and I am declining it. My gate was underpowered.

Per-cell proxy quality `ρ_c` against per-cell local `AUC_c`, Spearman across 24 cells:

per-seed **0.2096, 0.1252, 0.0904, 0.2417, 0.1774** → mean **0.1689**, which mechanically triggers
the pre-registered ≤ 0.2 band `PROXY_NOT_WHAT_MAKES_A_CELL_LEARNABLE`.

**That band is not usable and I am not claiming it.** The standard error of a Spearman correlation on
24 points is ≈ 1/√23 ≈ **0.209**. My pre-registered bands were ≤ 0.2 versus ≥ 0.5 — **separated by
0.3, which is less than 1.5 SE**. Every observed value is within noise of zero *and* within noise of
0.4, and the seed-to-seed spread (0.090 to 0.242) is itself about one SE wide.

**This is a gate that does not exceed its own measurement error** — the failure mode this program has
logged before, committed by me in a pre-registration written two hours after I corrected a different
instance of it. Declared, not buried.

**Reportable statement:** with 24 cells this test cannot distinguish "proxy quality tracks local
learnability" from "it does not." The question the reviewer raised — whether high-proxy cells are
exactly high-local cells — **remains open and would need far more clusters than this corpus provides.**

## 4. A2-BOOT — "no shared structure" is formally dead

Cluster bootstrap over 24 held-out cells, 2,000 resamples, on LOCO:

- point **0.5645**
- **95% CI [0.5097, 0.6200]** — **straddles the 0.57 gate**
- band: **UNRESOLVED — gate within interval**

**Exactly as predicted, and exactly as the reviewer expected.** A 0.0054 margin against a threshold
was never defensible once A3 showed the cell-clustered interval was 52× the seed SE. The C2 wording
is now not merely preferable but mandatory:

> Naive supervised pooling across the eleven other cells provides little additional transfer **under
> this representation and this model family**.

The interval's lower bound (0.5097) is barely above chance and its upper bound (0.6200) is far below
local relearning (0.7392), so **pooling clearly does not recover local performance** — that much is
robust. What is *not* established, and must not be said, is that no shared structure exists.

## 5. The two ledgers, unchanged by these results

- **Pre-registered experimental verdict: UNRESOLVED.** Round 1 landed in an undefined branch; round 2
  returns PARTIAL on A1-NL and UNRESOLVED on A2-BOOT. **No pre-registered branch has fired at any
  point in this audit sequence.**
- **Program disposition: KILL of the corpus-as-vehicle**, justified **independently** by the Q1
  census — exhaustively, no population here carries both a non-arithmetic oracle and conditional
  headroom above 0.05. Unaffected by anything in this document.

## 6. Prediction vs outcome

- **A1-NL best 0.62–0.70:** actual **0.6075**. **Wrong** — just below, and in the direction that
  happens to preserve my disposition, which is why the pre-commitment mattered.
- **Per relation, `abs_diff_le_3` carries it and `equal_mod_2` near chance:** actual 0.6636 vs
  0.5515. **Right.**
- **CORR +0.3 to +0.6:** actual **0.1689**. **Wrong**, and the test was underpowered anyway.
- **A2-BOOT straddles 0.57:** actual CI [0.5097, 0.6200]. **Right.**

**Running total across seven filings: eleven substantive predictions wrong or overstated, five
right.** Of the five right, four came on experiments an external reviewer specified.

## 7. What stands at the end of this audit

- Candidate-conditioned representations predict **the constructed action-ranking labels**; parent-only
  representations score exactly 0.5000. That `Z(x,a)` carries information about useful mathematical
  *navigation* was never established, and that gap is more basic than any proxy finding.
- An independent non-navigational proxy reproduces performance equivalent to ~45% of the local
  above-chance span aggregate, ~68% on the bounded-difference relation, ~21% on parity — **not a
  decomposition**, and not improved by nonlinearity.
- Naive pooling adds little under this representation and model family; whether shared structure
  exists is **untested**.
- Coordinate transport by marginal/scale alignment does not rescue same-objective cross-pair
  transfer; the effect is not separable from zero over cells; stronger alignment hypotheses remain
  untested and were correctly excluded from the frozen arm.
- The instrument finding is unaffected: production omitted the transition semantics required to test
  its own thesis.

**Work on this corpus ends here**, per the reviewer's instruction and per charter §13.

*— Diomedes, round-2 audit result, 2026-08-25. Corpus work closed.*
