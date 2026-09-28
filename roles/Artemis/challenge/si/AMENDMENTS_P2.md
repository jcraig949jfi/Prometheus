# AMENDMENTS to MODEL_AND_PREREG.md (frozen at 1b573ac95) -- Phase 2

Artemis, 2026-09-28. Pure ASCII.

This file was written BEFORE any preregistered grid cell was run. The only executions before it were:
- toy-size smoke tests of the code (A0);
- the Phase-1 scratch arithmetic.

Each item gives the change, why it is needed, and the direction it could cut.

## A0. Pre-amendment exposure (disclosure)

Code was smoke-tested at NON-grid sizes (T = 200-300, one seed per family, F4 at depth d = 5). Those
results are discarded and appear in no reading. Two facts were seen:
- The naive F4 backtracking search is exponential at W = 1. At d = 5 it excluded n <= 6 in 20 s, then
  hit its cap; the T4a bound at d = 5 is n >= 8.
- At W = 2, d = 5 it FOUND a 3-state permutation tracker.

The second fact is relevant to C1 at W >= 2 (see A9). It was seen before this file was written and
before any grid cell ran.

## A1. HK (hybrid checkpointer) dropped

The prereg gives HK no clearing rule for its checkpoints. For exact tracking, a checkpoint copy of S_j
can only be cleared by recomputing S_j, and that needs a synchronising word inside the window: the
same condition RG-W already tests. So under the prereg's own recoverability rule a checkpoint only
MOVES garbage; it cannot lower the unrecoverable-merge rate. HK is therefore not run.

Direction: neutral. HK could not beat RG-W on the quantity the readings use.

## A2. FX1 clause for I

The prereg says "For every I run: ERASE > 0 and the backward run fails". I erases only a merged
predecessor (and, at W = 0, the input register). On co-unifilar sources at W >= 1 it has nothing to
erase, which is exactly T2. So the I-clause applies to I runs at W = 0 and to I runs on merging sources.
On co-unifilar sources at W >= 1, ERASE = 0 is the EXPECTED value and is reported.

Direction: without this, FX1 would fail on the prereg's own theorem T2 and block every reading.

## A3. SLOPE_CHECK eligibility (power)

A cell is eligible iff the expected number of unrecoverable merges per seed in the second half of the
run, r'(W) * T/2, is >= 10.
- Below that, the per-seed slope is dominated by Poisson noise, and a check against a ratio band of
  [0.5, 1.5] has no power.
- Ineligible cells are reported as NOT_ELIGIBLE.
- The fraction computed under the ORIGINAL rule (all finite-W merging cells) is also reported beside
  it, and it does not decide.
- SLOPE_CHECK is applied to uncapped RG-W, the unbounded construction.

Direction: removes a tilt toward U that comes from low power, not from the model.

## A4. Budget (the prereg is internally inconsistent)

The prereg sets a hard budget of 1 CPU-hour, but also lists F4 as "at most 60 min, capped at 10 min per
cell" on 9 cells. The F4 caps alone (90 min) exceed the budget, so the 10% projection would trigger
every reduction whatever F1-F3 cost. The preregistered scale-down order is therefore applied IN FULL
before any run:
1. F3 seeds 4 -> 2;
2. F1 T 8192 -> 4096;
3. F4 depth 12 dropped (cells W in {1,2,3} x d in {8,10}).

F1-F3 and LMT then run under the 10% projection as preregistered. F4 runs last with per-cell cap =
min(600 s, (3600 s - CPU already spent - 60 s) / 6). A capped F4 cell reads as the prereg says.
The F2 T stays at 8192.

## A5. Implementation choices (not in the prereg text)

- a. RECOVERABILITY TEST. S_{t-1} counts as recoverable iff the retained symbols x_{t-W+1..t-1}
     contain a synchronising word (the image of all states under it is a singleton, allowed
     transitions only), or the window reaches back to time 0 (anchor s0). The test does not
     condition on S_t, so it can only OVERstate unrecoverable garbage relative to r(W). For RP this
     makes no difference, because S_t = 0 after R. Analytic r'(W) uses the same test.
- b. RG and RQ recompute ABSTRACTLY: one charged op of cost D, justified by the verified
     synchronisation. RU-W/B recomputes EXPLICITLY with a Bennett chain of registers, computed then
     uncomputed. RU-W/LMT runs a real Euler tour and verifies its reverse tour. The harness chooses
     the chain's start state as the true state before the synchronising word. The result does not
     depend on that choice, because the word synchronises; the harness only supplies an allowed
     start.
- c. SCAN COST. Locating the synchronising word costs D*|S| ops, charged twice (scan and unscan). An
     unsuccessful search costs the searched window length * |S|. The prereg's T3 accounting omitted
     this cost. The S1(i) C_step ratio uses the MEASURED total, scan included. This cuts AGAINST K.
- d. CERTIFICATE. Trace entries store op names, operand names and env positions, never written
     values, so every inverse is recomputed. Control flow in the backward run follows the recorded
     op sequence; branch conditions are not independently re-derived.
- e. LOSS. The probability floor is 1e-12 when a desynchronised learner assigns 0 to the realised
     symbol. An exact learner's loss is set to exactly 0 when its state equals S_t, so "bitwise
     D = 0" means every step exact.
- f. GM and EVEN use p = 1/2. Random machines: Dirichlet(1) emissions (all transitions allowed);
     rejection-sampled for strong connectivity, synchronisation (pair graph) and minimality (Moore).
- g. FX2 SE: batch-means SE (16 batches per run, pooled over seeds), because per-step losses are
     autocorrelated.
- h. RU is run uncapped only. In a capped cell it FAILS if its garbage stack exceeds the cap. RG runs
     at caps 8, 64 and inf (F1). On overflow a capped RG enters the declared non-merging mode.
- i. APPLICABILITY:
     - IW-k, IH, RH, RX: W = 0 in F1.
     - RQ at W = 0: an agent-held store plus a transient recompute (as the prereg says).
     - IH also at W = 1 in F3.
     - R-min only on co-unifilar sources.
     - F2 W = 0 cells: I and RQ only.
- j. MEMORY-BOUNDED (used by S1): the median over seeds of the second-half slope of M_agent is
     <= 1e-3 bits/step, and the garbage stack is empty at the end in every seed. A learner "succeeds"
     in a cell iff it is exact in every seed and memory-bounded (unbounded budget), or its garbage
     stack is <= cap in every seed (capped cell).
- k. S1(i) is judged on RU/B, or on R-min for co-unifilar sources. These are the explicit
     constructions. RG and RQ are reported beside them.
- l. F3 analytic r'(W): exact DP over (state, image set). Where the DP exceeds 2e5 pairs, an MC
     estimate from an independent 20000-step sequence is used and flagged "mc".
- m. The prediction readout is the harness reading the state register (not an op); the same holds
     for every learner.

## A6. IH definition

IH is an 8-bit state h.
- Each step: h <- P_x(h), with fixed random permutations P_x.
- At exactly the steps where I merges: one random bit of h is erased (a fixed random schedule), so the
  merge-time curve is matched to I.
- The predictive table P(x_{t+1} | h) is calibrated on an independent 65536-step sequence with Laplace
  counts.

## A7. S2(i) eligibility at finite lifetime

Because of A4, F1 has T = 4096. RP(q = .01) at W = 1 expects about 41 unrecoverable merges, fewer
than a 64-bit cap. By T4(b) a reversible agent SURVIVES such a cell for the whole lifetime: that is
T4's finite-premium escape, not evidence against T4a.
- A capped cell is eligible for the S2(i) REV_GAP requirement iff the expected unrecoverable merges
  over the run satisfy r'(1) * T >= 1.5 * cap / ceil(log2|S|).
- Ineligible cells are reported, with the observed survival, as FINITE_LIFETIME_ESCAPE.

## A8. S2(iii) at W = 1 and the U rule

The prereg's S3 makes a capped F4 cell read U only for W >= 2. For W = 1 it is silent. Decision:
- VERIFIED if every n < Fib(d) is excluded.
- CONSISTENT (T4a stands on its proof) if the probe is capped with no tracker found at n <= the last
  excluded n.
- CONTRADICTED if a tracker with n < Fib(d) is FOUND. That would mean a bug or a wrong proof: STOP and
  report.

A W = 1 CONSISTENT reading does not by itself make CLAIM-NARROW U.

## A9. C1 at W >= 2 with d = 12 dropped

The prereg's "bounded n for all d up to 12 (n_min constant over the last 2 depths)" becomes: FOUND at
both d = 8 and d = 10 with equal n_min -> C1 FALSIFIED at that W, and N* narrows to the W values where
it is not falsified. A0 disclosed that a 3-state tracker exists at W = 2, d = 5.

## A10. S4 (B3) flip rule

A cell's reading is re-computed with M_env added:
- finite W: W * ceil(log2|X|) bits, constant;
- W = inf: the retained past, t * ceil(log2|X|), which grows.

A REV_MATCH flips under B3 iff its B3 memory is unbounded.

END

## A11. POST-DATA fixture-check correction (2026-09-28, after the campaign ran; S0 procedure)

FX4 failed on the first analysis pass. The cause was the CHECK, not the instrument. analyze.py v1
required M_peak == M_end, but M_peak includes the transient input register that R-min reads during
the step (1 bit for EVEN, 2 bits for RP), and M_end is the end-of-step persistent width. The rows
show R-min exactly as preregistered in all 16 FX4 runs:
- ERASE = 0; exact (D = 0);
- M_end = 1 bit (the state register);
- M_peak = 1 + width of the input register;
- slope of order 1e-18 (float noise).

Fix: "constant M_agent" is read as |slope| < 1e-9, M_end = ceil(log2|S|), and M_peak =
ceil(log2|S|) + ceil(log2|X|). No learner, row or other rule changed. The fixtures were re-run on the
same rows.

The same pass cached r'(W) to disk so the re-run did not redo the MC estimates.

Disclosure: this correction was made AFTER all readings of the first pass had been seen. Those
readings were:
- CLAIM-BROAD not K;
- CLAIM-NARROW U.

The correction can only change the S0 gate. It cannot change any S1-S4 reading.
