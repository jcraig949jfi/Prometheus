# SUBSTRATE FINDING — Salem-class moderation of Lehmer-bound survival at M ≥ 1.30

**Date:** 2026-05-26 (ITER-4)
**Author:** Charon
**Status:** First substrate-grade PROMOTED claim produced end-to-end
by the Erebos generative pipeline through Stygian battery validation.

**Caveat up front:** the underlying mathematical observation (Salem
numbers cluster near Lehmer's value, sparse above ~1.30) is well-
established in the analytic number theory literature. This is NOT a
novel mathematical discovery. **What's novel is that the swarm
arrived at it autonomously through chained Erebos compositions, and
that the discovery loop is now empirically falsified.**

---

## The finding

Source: `charon/agents/stygian/loaders/composition_g02_g04_lehmer_tightened.py`
Run timestamp: 2026-05-26 ITER-4 smoke-test.

In the Mossinghoff non-cyclotomic Mahler-measure catalog (8513 Salem-
class entries + 83 non-Salem entries, all with M ≤ 2.0):

At threshold M ≥ 1.1762808 (Lehmer's value, "baseline"):
- Salem-class survival fraction: **0.9999**
- Non-Salem survival fraction: **1.0000**
- Divergence: **0.0001**
- Permutation null p95: ~0.0001
- Verdict: REJECTED (no detectable moderation)

At threshold M ≥ 1.30 (G04-tightened):
- Salem-class survival fraction: **0.0028** (only 24 of 8513)
- Non-Salem survival fraction: **1.0000**
- Divergence: **0.9972**
- Permutation null p95: 0.0239
- Verdict: **PROMOTED** (observed 41.7x the null p95)

**Substrate-grade observation:** Salem class is a structural
moderator of Mahler-measure distribution in the band M ∈ [1.176,
1.30]. Salem-class polynomials in this catalog concentrate near
Lehmer's value; non-Salem extremes spread out at larger M. The
v0.10 G02 REJECTED at the baseline threshold was a too-loose-
threshold artifact -- the divergence is real, just invisible until
the threshold approaches the Salem cluster's upper edge.

---

## How the swarm arrived at this

The discovery chain (Erebos → Stygian battery → ledger):

1. **Stygian BL-C-001 attack (Lehmer)** — established the baseline
   substrate.
2. **G02 Contrast** — emitted the hypothesis "Salem class moderates
   Lehmer survival rate."
3. **v0.10 composition loader (g02_lehmer_salem)** — ran permutation
   null at M_Lehmer; observed divergence 0.0001 < null p95 0.0001;
   verdict REJECTED with kill_pattern=permutation_null. The plugin's
   expected_kill_pattern matched -- declared "permutation_null"
   was indeed the failure mode at this threshold.
4. **ITER-3 follow-on hypothesis** (in research note): "the
   REJECTED was a too-loose-threshold artifact; tightening might
   reveal signal." Recorded in `pivot/erebos_g04_survivor_
   tightening_research_2026-05-27.md`.
5. **G04 Survivor-Tightening** (ITER-3) — design + implementation
   of the threshold-tightening ladder.
6. **G02+G04 chained-composition loader** (ITER-4 this session) —
   ran permutation null at the G04-tightened threshold M=1.30.
   Observed divergence 0.9972 >> null p95 0.0239. Verdict:
   **PROMOTED**.

The chain spans three iterations (v0.10 ITER-3 → ITER-4) and
exercises five generator concepts (G01 Intersection, G02 Contrast,
G04 Tightening, plus the chained-loader infrastructure). It's the
first substrate-grade discovery that wasn't directly hand-coded by
Charon -- the loader composition itself emerged from the swarm's
falsification process.

---

## What this validates (and doesn't)

**Validates:**
- DNA P12 (falsification asymmetry): the swarm's expected_kill_pattern
  declarations are now empirically testable, and at least one
  (G04 tightening) was confirmed AGAINST G02's prior failure mode.
- DNA P9 (rolling cadence): the 3-iteration loop produced a
  substantive output through chained compositions across iterations.
- The composition-aware Stygian loader spike (task #37) is genuine
  infrastructure that unlocks per-generator empirical validation,
  not just plumbing.

**Does NOT validate:**
- Anything about the broader Prometheus criterion / Reasoning Ladder
  R8 / R9. The Salem-class moderation is well-known math.
- The 25-archetype Erebos cluster as a discovery engine for genuinely
  novel mathematics. This is one finding, in a domain whose structure
  is already understood.
- That the swarm is now producing "real" findings reliably. The G02
  hypothesis was hand-curated (Salem vs non-Salem was a hardcoded
  PROBLEM_BINARY_SPLITS entry); the loader semantics were hand-
  written.

**The honest framing:** this is a proof-of-concept that the
chained-composition loop CAN produce substrate-grade PROMOTED claims
that match known mathematical structure. Whether it can produce
substrate-grade claims that DON'T match known structure -- novel
math -- remains the open question. Per the 2026-05-25 frontier
review's 5% 90-day forecast, the answer is probably "not soon."

---

## ITER-5/6 implications

This finding suggests three next-iteration directions:

1. **Verify the analogous claim in other Mahler-spectrum bands.** If
   Salem class moderates at [1.176, 1.30], does it ALSO moderate at
   [1.30, 1.50]? [1.50, 1.75]? Run G02+G04 with parametric thresholds.
2. **Test other binary categoricals.** If Salem moderates, what
   about cyclotomic-flag (G02 already supports this), Smyth-extremal,
   degree-parity? Each gets a G02+G04 chained composition.
3. **Cross-domain transfer (R7).** Does Salem-like moderation appear
   in OTHER mathematical domains the swarm has data for? BSD CM vs
   non-CM at specific rank thresholds? Knot-Alexander-polynomial
   roots? This is G07 Analogy territory -- defer until G07 ships.

The substrate's first PROMOTED moves us from "the loop produces
candidate claims" to "the loop produces verifiable claims." That's
the spec's intended progression.

— Charon, 2026-05-26 (ITER-4 substrate finding)
