ARCHAEON — SEASON 7 ORDER

S6 is closed at ab2d40cef.

Its frozen verdict is CHEAP_REPAIR_WITH_REGRESSION.

Do not reinterpret that verdict.

S6 established that:

* G’s important endgame defect is substantially an objective-units defect: expected targets remaining is not identical to expected probes remaining.
* The frozen exact-tie v2w refinement A_v2w_0 recovered approximately 70% of the available G→O gap at L=9.
* That is approximately the ceiling available from exact-tie intervention.
* A_v2w_0 had zero endgame regressions under the S6 comparison.
* It nevertheless failed the full-universe production safety audit because it remained active outside the endgame and regressed on seven N=30 two-block roots.
* The S6 endgame itself had already been frozen from S5 evidence as:

  5 <= N <= 18

* N is observable before the decision, target-free, deterministic, and requires no learned router.
* The obvious gated composition was NOT preregistered in S6 and therefore was correctly not licensed.

S7 exists to test exactly that missing composition.

THE QUESTION

Does the preregistered observable gate

    5 <= N <= 18

turn the already-frozen S6 exact-tie v2w repair into a production-safe improvement over incumbent G?

This is primarily a LICENSING TRIAL.

It is not a new feature-search season.
It is not another objective-repair season.
It is not a routing-discovery season.
It is not permission to improve v2w.

⸻

1. FREEZE THE CANDIDATE

⸻

The candidate policy is conceptually:

if 5 <= feasible_target_count <= 18:
    use the frozen S6 A_v2w_0 exact-tie refinement
else:
    use incumbent G exactly

Call this candidate, for bookkeeping, GATED_V2W unless repository conventions suggest a better unambiguous name.

The gate bounds come directly from the already-frozen S6 endgame definition.

DO NOT:

* change 5 or 18;
* tune the gate;
* add another coordinate;
* use κ_H;
* learn a router;
* alter the v2w statistic;
* alter the exact-tie definition;
* widen to near-ties;
* add LB2;
* add entropy;
* add coefficients;
* add an exception for N=30;
* inspect failures and then modify the candidate.

Where practical, reuse/freeze the exact S6 implementation of A_v2w_0 rather than rewriting an equivalent algorithm.

Prove or test that the gated implementation invokes precisely the S6 behavior inside the gate and precisely G outside it.

⸻

2. PREREGISTER BEFORE COMPARISON

⸻

Write and commit the S7 preregistration before executing the comparative trial.

Freeze:

* candidate implementation/hash;
* gate;
* eligible universe;
* comparison arms;
* seeds;
* deterministic work accounting;
* leakage controls;
* production bars;
* regression bars;
* verdict rule.

Do not derive a new bar from the S7 outcomes.

S7 should be capable of failing.

⸻

3. PRIMARY SAFETY INVARIANT

⸻

Outside the gate:

    N < 5 or N > 18

GATED_V2W is supposed to BE G, not merely approximate G.

Therefore test a strong implementation invariant:

For every audited decision outside the gate, the candidate must make exactly the same decision as G and incur the same policy outcome, modulo separately accounted gate overhead.

Any behavioral divergence outside the gate is an implementation/instrument failure.

This is stronger than a statistical regression test.

The seven S6 N=30 regression roots are mandatory named canaries.

Under the gated candidate they should reproduce incumbent G exactly.

Do not merely report that their aggregate score improves.

Show that the offending refinement is inactive.

⸻

4. INSIDE-GATE SCIENTIFIC FALSIFIER

⸻

Inside:

    5 <= N <= 18

the candidate receives no immunity merely because S6 looked good.

Repeat the exact comparison against G over the complete eligible census.

The critical question is whether the previously observed zero-regression behavior survives the properly composed policy.

Predefine a production-safety regression bound.

Prefer the strongest mathematically defensible bound.

If exact non-regression is appropriate given the complete census and deterministic policies, use it.

Do not weaken the bound merely because production would otherwise fail.

Report:

* states improved;
* states unchanged;
* states worsened;
* aggregate probe reduction;
* worst regression;
* G→O gap recovered where oracle accounting is available;
* effect by N;
* work units.

⸻

5. GENERALIZATION

⸻

Use the strongest honest confirmation available from the existing experimental history.

L=8 was development territory.

L=9 has prior S5 producer-level exposure and S6 confirmatory exposure and must not be called virgin held-out data.

However, the S7 composition itself was not preregistered or tested in S6.

State the epistemic status precisely.

If an additional untouched construction can be generated without changing the scientific question or creating a new tuning surface, you may preregister it as an additional confirmation.

Do not manufacture a new benchmark merely to obtain the phrase “held out.”

The complete known universe safety audit matters more here than cosmetic novelty.

⸻

6. ORACLE ROLE

⸻

O remains a sealed evaluator.

It is not part of GATED_V2W.

Do not use O to alter the gate or candidate.

Oracle work must continue to be accounted separately under the repaired nested-budget system from S6.

If previously frozen exact O values can be reused without changing the experiment, reuse them and record provenance rather than gratuitously recomputing them.

⸻

7. COST

⸻

S7 is not licensed merely because the repair is cheaper than O.

Measure the incremental deterministic work cost of:

GATED_V2W versus G

including the gate and v2w computation when active.

Report at least:

* median work units per decision;
* upper tail / maximum;
* ratio to G;
* fraction of decisions on which v2w is actually invoked;
* total incremental work over the census.

Wall-clock time is descriptive only.

The production ruling must consider whether the recovered probe savings justify the added mechanism and deterministic search work.

⸻

8. LEAKAGE AND PERMUTATION CONTROLS

⸻

Retain the S6 impossible-event controls.

At minimum fail closed on:

* arm below V*;
* oracle exhaustion where oracle evaluation is required;
* candidate decision changing under irrelevant census ordering;
* candidate decision changing under fossil-order permutation where semantics are unchanged;
* census/solver mismatch;
* target information reaching the gate or refinement.

The gate may depend on feasible target count N.

It may not depend on which feasible target is the hidden target.

Repeat the adversarial permutation controls that caught the S5 class of defect.

⸻

9. DO NOT CHASE THE REMAINING GAP

⸻

S6 separated at least three regimes:

exact ties:
    approximately 70% of G→O gap recoverable by v2w
near ties:
    recovery can approach approximately 87%, but the tested
    aggressive repair regressed
beyond the tested 20% window:
    a smaller residual remains for which deeper search may matter

S7 addresses ONLY the first regime.

Do not investigate the extra ~17 percentage points.

Do not invent ARCH-46 science inside this season.

Do not allow an interesting near-tie observation to mutate the licensing candidate.

Record such observations for later work and continue the frozen trial.

⸻

10. VERDICT

⸻

Preregister quantitative criteria, but the verdict structure should distinguish at least:

INSTRUMENT_FAILURE
    The trial cannot establish the candidate's behavior because a
    leakage, implementation, accounting, oracle, census, or other
    preregistered instrument invariant fails.
GATE_FAILS_TO_ISOLATE
    The fixed N gate does not isolate the previously observed safe
    repair region, or meaningful inside-gate regressions remain.
SAFE_BUT_NOT_WORTH_IT
    The gate removes the regressions, but the resulting improvement
    is too small or the deterministic work/mechanism cost too high
    under the preregistered production bar.
LICENSED_ENDGAME_REPAIR
    The fixed gate makes the frozen repair behaviorally identical to
    G outside the gate; the repair satisfies the preregistered
    regression bound inside it; the improvement replicates at the
    required magnitude; leakage and accounting controls pass; and
    deterministic cost satisfies the production bar.

Do not create a softer success category after execution.

⸻

11. PRODUCTION

⸻

Unlike S6, production is an allowed outcome of S7.

It is NOT the default outcome.

If and only if the frozen LICENSED_ENDGAME_REPAIR criteria pass, S7 may license the minimal gated repair for production.

Production means only the mechanism actually tested:

    G outside the frozen gate
    frozen exact-tie v2w refinement inside the frozen gate

Nothing else rides through the gate with it.

No LB2.
No near-tie window.
No W.
No M.
No learned router.
No speculative optimization.

If production is licensed, make the smallest integration possible and preserve an explicit way to identify/count when the repair fires.

If repository governance requires a separate promotion step after scientific licensing, obey that governance rather than bypassing it.

⸻

12. W / M

⸻

W and M remain retirement candidates.

They are irrelevant to the S7 scientific question.

Do not spend compute rerunning them merely for symmetry.

If existing governance permits their retirement to be handled independently without contaminating S7, record the appropriate disposition.

Otherwise leave them alone.

⸻

13. WHAT I WANT BACK

⸻

Return one compact receipt, in this order:

1. S6 verdict preservation.
2. S7 preregistration commit/hash and frozen candidate identity.
3. Proof/test that the candidate is exactly G outside 5 <= N <= 18.
4. Named results on all seven S6 N=30 regression canaries.
5. Complete inside-gate comparison against G.
6. Regression audit.
7. G→O gap recovery, where licensed by existing oracle evidence.
8. Full-universe safety audit.
9. Deterministic work/cost accounting.
10. Leakage and permutation controls.
11. Generalization/confirmation result with honest exposure labels.
12. Frozen-rule verdict.
13. Production ruling.
14. If licensed, exact minimal integration performed; if not, exact falsifier.
15. ARCH-45 disposition and any separately filed future residue.
16. Commits, tests, provenance, and communications receipt.

⸻

THE POINT

Do not make S7 clever.

S4 suggested an ecology.
S5 localized a small advantage for deeper policy.
S6 showed that most of the accessible advantage was a mismatch between the units optimized by G and the units actually paid by the task.

S6 then failed production for a precise reason:

the repair operated where it had not earned the right to operate.

There is now one cheap, observable, target-free boundary already frozen from prior evidence.

Test it.

If the gate works, bank the metabolized residue.

If it fails, preserve the failure and learn why.

Only after this question is closed may Archaeon spend complexity on the remaining near-tie or deep-search frontier.