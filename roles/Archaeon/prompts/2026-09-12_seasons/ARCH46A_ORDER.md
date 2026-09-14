ARCHAEON — ARCH-46A: EXACT MEANS EXACT

S7 is accepted exactly as ruled:

GATE_FAILS_TO_ISOLATE

Do not amend that verdict.

The single preregistered regression has been localized to a representation defect:

mathematically equal v2w values were compared as binary floating
values, creating an artificial ~2e-15 ordering inside an exact
tie and bypassing G's deterministic tie rule.

ARCH-46A gets ONE scientific change:

represent/compare v2w exactly so mathematically equal partition
values remain tied and resolve through the existing G tie rule.

Nothing else.

Do not:

* change the N gate;
* change GATED_V2W semantics;
* tune thresholds;
* change seeds;
* change worlds;
* change budgets;
* change the objective;
* change the continuation;
* widen the candidate pool;
* add another routing statistic;
* revisit W or M;
* integrate into production;
* forgive the S7 regression retrospectively.

Before rerunning the candidate:

1. Implement the smallest exact representation warranted by the
    mathematics, preferably an exact rational/integer form derived
    directly from the partition counts.
2. Add a regression test for evs:914ee3e416304d0d proving that the five
    {6,4,2} probes are exactly tied under v2w and therefore fall through
    to G’s existing tie rule.
3. Add adversarial exact-tie tests sufficient to show this is a semantic
    repair rather than a patch for one state.
4. Demonstrate that non-tied v2w orderings are unchanged.
5. Freeze and commit a NEW preregistration before running the comparative
    trial.

Then repeat the S7 trial as identically as possible.

The primary question is now:

DOES THE N-GATED COMPOSITION PASS THE ORIGINAL S7 BARS WHEN THE
REFINEMENT'S IMPLEMENTATION MATCHES ITS INTENDED EXACT SEMANTICS?

Preserve L8 as development/exposed, L9 as previously exposed, and L10 as
the strongest existing generalization set. Do not manufacture a new
holdout merely because L10 has now been observed.

Report exact deltas from S7, not merely fresh aggregate tables.

In particular report whether:

* the sole L8 regression disappears;
* every previously unchanged state remains unchanged unless the exact
    tie repair mathematically requires otherwise;
* every S7 improvement survives;
* L9 recovery survives;
* L10’s 17 improvements / 0 regressions survive;
* outside-gate identity remains exact;
* N=30 canaries remain G at the root;
* work accounting changes materially;
* any NEW regression appears.

If exact arithmetic changes decisions beyond cases attributable to
previous floating-point ordering, investigate before interpreting the
trial.

Verdict under the NEW frozen rule.

If every S7 substantive bar survives and the exact-tie regression
disappears, you may rule ARCH-46A accordingly.

Do NOT automatically license production.

If ARCH-46A passes, return separately with the evidence needed to decide
whether the gated composition has earned a production canary. That is a
new decision, not part of this repair experiment.

ARCH-46(b), the near-tie/deep-search frontier, remains parked.

Commit all code, preregistration, tests, results, readout, and receipt to
the Prometheus repository and ensure the final commits are pushed and
verified as ancestors of main. Post the appropriate Archaeon comms
receipt.

One repair.
One preregistration.
One rerun.
No moving the bar.