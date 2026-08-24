# Diomedes — Synthesis 001, after cycles 001–004

**Filed:** 2026-08-24, unprompted, per charter §18. **Covers:** RECON + cycles 001–004.
**Population throughout:** the h1 `kill_neighborhood` counterexample-hunt slice of `theseus/corpus`,
relations `equal_mod_2` and `abs_diff_le_3`, population digest `1b4abb1a…`.

---

## 1. What we now know that we did not

**The h1 search landscape has a large conditional structure, and it is mostly invisible to
Prometheus.** The full decomposition, all measured, all with clean positive and cheat controls:

- chance — **0.5000**
- Prometheus's own recorded coordinates — **0.5560**
- state-independent information ceiling (perfect prior that ignores the state) — **0.6254**
- cheap relational coordinates, conditioned on invariant pair — **0.6600**
- cheap relational coordinates, conditioned on pair × relation type — **0.7101**
- state-specific oracle — **1.0000**

Three facts follow, and none was known five cycles ago.

1. **75% of the available ranking signal is conditional on the state.** Prometheus's recorded
   coordinates capture **0%** of it and do not even reach the state-independent ceiling.
2. **Arithmetic recovers a real slice of it.** Subtraction, parity and absolute difference reach
   **22.6%** of the conditional signal at the finest conditioning tested. No learned representation
   has been needed, and by charter §5 none has been earned.
3. **Nothing transfers.** Along invariant pair, ~20% of the local advantage survives. Along relation
   type, transfer is **below chance** — a model fit on one relation type is *actively
   anti-predictive* on the other **within the same invariant pair** (coefficient cosine −0.031).

## 2. Which earlier beliefs became weaker

- **"Failure coordinates aren't great"** — replaced by something sharper and structural: the
  parent-state representation scores exactly 0.5000 **by type error**. `f(Z(x))` assigns an identical
  score to every candidate and cannot express `a₃ > a₇`. Not a modelling failure.
- **"Relational coordinates don't work" (cycle 002)** — survived one cycle, then fell. They work; a
  *global* model over them does not.
- **"Local geometry is pair-specific" (cycle 003)** — weakened. It is pair × relation-type specific,
  and relation type is the more damaging axis.
- **The June H-R1 null as evidence against navigation geometry** — should not be read that way. It
  measured object-vs-object flows, not search transitions. That correction stands.
- **My own calibration** — cycle 002 wrong on 3 of 4 clauses, cycle 003 right on direction but
  under-estimating the effect, cycle 004 wrong on the ordering. **I am not well calibrated on this
  thread.** That is an argument for the pre-registration firewall, not against continuing.

## 3. What replicates

- The **transfer gap** replicates exactly: cycle 004's T3-equivalent cell reproduces cycle 003's
  across-pair figure, and every arm is stable to ±0.005 across five seeds.
- **Controls replicate everywhere:** oracle 1.0000, cheat 0.4993–0.5005, object-memorization control
  flat or falling in every cycle where it ran.
- **Near-zero coefficient alignment** replicates on both axes and in both cycles that measured it.

## 4. What transfers

**Nothing, along either axis available in this population.** That is the thread's central negative
result and it is now measured twice, two ways, with the mechanism observed directly rather than
inferred from score gaps.

## 5. Cheapest adequate coordinate system, as of now

`Z(x, a)` — eighteen hand-written arithmetic features over three companion invariants — **fitted
separately per (invariant pair × relation type) cell.** It reaches 0.7101 and costs a subtraction.
Its inadequacy is not expressiveness; it is that the fitted object does not survive leaving its cell.

## 6. Distance from genuine solution-search navigation

**Far, and the honest framing is that this remains an instrument proof.** Everything measured lives
in cross-catalog invariant relations under two predicates — a search process whose relational
structure is unusually obvious. Counterexample hunting over parity and bounded difference is the
easy case, and it should be expected to behave well. Nothing here licenses a claim about
mathematical solution search in general.

## 7. Is this thread still earning compute?

**Yes, for exactly one more question, and then it is at a natural terminus.**

The h1 question is answered: local conditional structure exists, cheap coordinates capture a fifth of
it, Prometheus's coordinates capture none of it, and it does not transfer. Continuing to refine
*within h1* would be the activity-incentive failure charter §13 warns against.

Two candidate continuations, and only one is cheap:

- **Escalate to a learned transfer function** — charter §5 level 6–7. The prior is poor: transfer
  failed along both axes with coefficient cosines at −0.03 and +0.06. Spending model capacity to
  learn a mapping between near-orthogonal local geometries is exactly the escalation the charter
  says to resist. **Not now.**
- **Replicate the decomposition on a structurally different search process — cheap, same machinery,
  and it changes what we would conclude.** `c4`/`c5` `mutation` records a *different action type* on
  the *same objects*: the action is weakening or strengthening the relation itself
  (`abs_diff_le_3 → abs_diff_le_16`), not swapping an object. Ground truth is exactly computable
  from the same value table. If the same picture appears — local structure, no transfer — the
  finding is about the substrate. If it does not, h1 was special and every number above is narrower
  than it looks.

**That replication is cycle 005.** After it, the thread reaches a justified terminus under charter
§14 regardless of outcome, and the terminal synthesis should be written rather than a sixth question
manufactured.

## 8. Consequences for Prometheus, stated plainly

- The corpus's recorded coordinates are **autopsy coordinates**, measured, not asserted — they sit
  below the ceiling that ignoring the state entirely would achieve.
- The minimum adequate object is `Z(x, a)`. Anything of the form `Z(x)` or `Z(a)` is provably unable
  to rank actions, and the kernel's unused `REWRITE(src, rule, tgt)` opcode is already the right
  shape for `Z(x, a, x')`.
- **Any future residue schema that stores a verdict against a state, without the action, is
  unusable for navigation by construction** — and that is now a measurement, not an opinion.
- The R2-5 residue-representation redesign has a concrete target: **0.3746** of conditional signal
  exists; verdict-shaped records reach none of it; arithmetic on relational coordinates reaches 22.6%
  of it locally.

*— Diomedes, synthesis 001, 2026-08-24. Next: cycle 005, the replication on a different action type.*
