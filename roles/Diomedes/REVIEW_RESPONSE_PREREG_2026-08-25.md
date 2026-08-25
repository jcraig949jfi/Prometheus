# Diomedes — review-response audit: PRE-REGISTRATION, filed before measurement

**Filed:** 2026-08-25, **after** an external review of `HITL_REVIEW_2026-08-25_cycle005_terminal.md`
and **before** any of the three audits below were run. **Charter §17:** external reviews are
hypotheses, not authority — *"resolve disagreement experimentally where possible."* That is what this
does. It is **not** a sixth research cycle: no new hypothesis is introduced, and the scope is fixed at
three audits that discriminate between interpretations already listed in §10 of the packet.

**Reviewer's substantive objections, recorded as received:**

1. **The relation axis is not a coordinate axis — it changes the reward function.** `y_r(x,a) =
   1[a breaks r]`. Changing `r` changes what counts as a successful action, so it is closer to
   changing `R` than to transforming `S`. Strata B (same pair, different relation) and D (both) are
   objective changes; only **C (different pair, same relation)** is a clean coordinate-transport
   experiment. The aggregate mixes them.
2. **Semantic proxy leakage.** A companion invariant `w(a)` may predict the withheld tested invariant
   `v_tested(a)`. A per-cell map `ĥ_c` plus the known parent value and relation reconstructs the
   oracle without any navigational content.
3. **The SE is on the wrong unit.** 552 ordered transfers are massively dependent; the reported SE is
   across 5 seeds only.
4. **Pooled-with-cell-identity is not decisive** (a flexible model with cell indicators can contain 24
   local models). **Leave-one-cell-out with the relation held fixed** is the right discriminator.
5. **CORAL should not be retro-admitted** to the frozen arm; preregister `T_independent` vs `T_unsup`
   for any successor.

**Accepted without contest:** 1, 3, 4, 5. **To be tested here:** 2, plus the stratified restatement of
1 and the correct uncertainty for 3, plus the LOCO design of 4.

**One factual correction to the review, established before these audits and not by them:** the
reviewer read the packet's "+0.083" for stratum C as an absolute AUC gain and derived ≈41% recovery.
It was already a **recovery fraction** computed against stratum C's own denominator. C's absolute
movement is 0.5549 → 0.5702; C's own local relearning is 0.7391; headroom 0.1841; **recovery 8.28%**.
The stratum does **not** cross into the 25–50% MIXED band. The reviewer's raw figure of 0.5349 was
cycle 004's one-draw sample; Arm B enumerates all 264 same-relation ordered pairs and gets 0.5549.
**The ambiguous unit labelling in the packet is my defect**, and the stratified table is now primary.

---

## A1 — Proxy reconstruction audit (tests Interpretation 2). Rung 5, but with an exact predicate.

**Question:** can the candidate's **companion** invariants predict the candidate's **tested**
invariant well enough that applying the *exact* relation predicate to the prediction reproduces the
local ranking performance?

**Method, per cell `c`, per seed:**
- Features: the candidate's raw companion invariant values `w_0(a), w_1(a), w_2(a)` **only**. No
  relational features, no target, no parent.
- Fit `ĥ_c` on the cell's **training** states (ridge regression, integer-free, no tuning), predicting
  the candidate's **tested** invariant value `v_tested(a)`.
- On the cell's **held-out** states, score each candidate by applying the **exact** relation predicate
  to the prediction: `ŷ = NOT r(v_tested(parent), ĥ_c(a))` — i.e. predicted-to-break.
- Report AUC against the true break label, on the same held-out rows the Arm B numbers use.

**The tested invariant is used here legitimately:** this is a diagnostic auditing where the
predictive information came from, not a ranking arm competing under the admissibility rule. Stated
explicitly so it is not later mistaken for a leak.

**Reported alongside:** (i) a continuous variant scoring `|ĥ_c(a) − target|` for `abs_diff_le_3` and
predicted-parity mismatch for `equal_mod_2`, because a binary predicate produces heavy ties;
(ii) the regression quality of `ĥ_c` (Spearman ρ between `ĥ_c(a)` and `v_tested(a)`), so a weak proxy
cannot be confused with a strong one; (iii) the same pipeline with **permuted** companion values, as
a null.

**Pre-registered interpretation, fixed now:**
- **Proxy AUC ≥ 0.65** (i.e. recovering ≥ ~65% of the 0.5→0.7392 local span) ⇒ **Interpretation 2 is
  substantially supported**; the cycle-001–005 decomposition is substantially surrogate measurement
  of the withheld variable, and the navigational reading of `I(A*; Z_a | Z_x)` must be withdrawn.
- **Proxy AUC ≤ 0.55** with local `Z(x,a)` still ≈ 0.7392 ⇒ Interpretation 2 is **not** the
  explanation of the local signal; something cell-specific remains unexplained.
- **Between 0.55 and 0.65** ⇒ partial; report as partial and do not round either way.

## A2 — Leave-one-cell-out, relation held fixed (tests Interpretation 4, in the reviewer's stronger form)

**Method:** for each relation `r` and each invariant pair `k`, train the frozen 18-feature model on
**all other invariant pairs carrying `r`**, pooled, with **no cell-identity feature of any kind**, and
evaluate on pair `k` under `r` — a pair entirely unseen in training. Compare against: local
relearning (0.7392), single-cell raw transfer within stratum C (0.5549).

**Pre-registered interpretation, fixed now:**
- **LOCO ≥ 0.68** ⇒ shared cross-cell structure exists and the "locality" reading is an artifact of
  training on one cell at a time. **Finding 3 would be withdrawn, not merely left provisional.**
- **LOCO ≤ 0.57** ⇒ no shared structure recoverable by this family; the locality reading survives this
  particular attack.
- **Between** ⇒ partial, reported as such.

## A3 — Uncertainty on the correct unit

Replace the seed-level SE with a **cluster bootstrap resampling target cells** (and, reported
separately, source cells), 2,000 resamples, within stratum C. The reported interval is over cells,
not over seeds and not over rows. **The claim "127 SE below the gate" is withdrawn in advance of this
computation**, independent of what the bootstrap returns.

## Predictions, recorded so they can be wrong

- **A1:** I expect the proxy to land **between 0.60 and 0.70** — materially above chance, below local.
  My reasoning is that conductor/discriminant-type invariants are strongly co-monotone with each
  other, so a coarse proxy should exist, but `abs_diff_le_3` demands near-exact recovery of an
  integer, which a 3-feature regression should struggle to deliver.
- **A2:** I expect LOCO **near 0.55–0.62** — above single-cell raw transfer, below local.
- **A3:** I expect the cell-clustered interval on stratum C to be **several times wider** than the
  seed SE and to remain below 0.25.

**Discount all three.** My record on this thread: eight substantive predictions wrong or overstated
across five cycles; most recently I predicted the sign flip would be the largest transport mover and
it was the worst, having quoted a ceiling computed on one subset as a property of all 552 pairs — the
same aggregation error the reviewer has now caught in the headline itself. **If A1 lands ≥ 0.65 the
honest consequence is that the thread's central quantity was mismeasured, and I have pre-committed to
saying so.**

## Disposition consequence, fixed before measurement

The reviewer argues for **KILL** of *"use the current cross-catalog substitution corpus to determine
whether mathematical navigation structure is transferable"* — while explicitly retaining the parent
claim. Charter §3 requires that a KILL name exactly what died.

- **If A1 ≥ 0.65** ⇒ **KILL**, and the named casualty is broader than the reviewer's: not merely the
  corpus as a vehicle, but the interpretation of the cycle-001 decomposition as navigational
  information.
- **If A1 ≤ 0.55 and A2 ≤ 0.57** ⇒ **KILL** of the corpus-as-vehicle exactly as the reviewer frames
  it, with the local signal recorded as real but unexplained and unexportable.
- **If A2 ≥ 0.68** ⇒ **REDESIGN**: shared structure exists, and the accumulation unit is a pooled
  cross-cell model rather than a local one.

**PARK is withdrawn as the disposition in every branch above.** The Q1 census established that no
population in this corpus can supply the missing identifying assumption, and PARK implies a
discriminability that the census says does not exist.

*— Diomedes, review-response pre-registration, 2026-08-25. Frozen before measurement.*
