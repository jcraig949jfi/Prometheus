# The Tier B adjudicator is the least-tested verdict code in the program

**Date:** 2026-08-23 · **Measured by:** Hephaestus (M3), full enumeration, no cap
**Command (reproduce exactly):**
`python attacks/mutation_harness.py ergon/probe/analysis.py ergon/probe/tests/test_probe_analysis.py`

```
analysis.py  killed=74  survived=133  score=35.7%  [FULL of 207 sites]  (672s)
```

An independent scout measured the same module at **35.7%** against this suite and **52.7%**
union across both suites that touch it (`test_probe_analysis.py` + `test_bc_clearance.py`) —
coverage is split, and the harness's one-source/one-test model cannot express that. Take 52.7%
as the fair union figure and 35.7% as what its own named test file achieves. **Either is far
below the ladder circuits**, and this is the module that computes Δ_carry and assigns the §6.3
verdict classes for the program's one priced experiment.

**Conflict declaration:** I am the probe's declared-conflicted, non-signing residue supplier.
I am reporting a defect in the code that would score my own residue, and the repair is **not
mine to make** — it belongs to Ergon (driver). This measurement is mechanical and reproducible
precisely so that my conflict does not have to be trusted.

---

## The survivors that matter

**1. All five §2 decomposition terms invert (lines 446–450, `Sub → Add`, every test green).**
`residue_existence`, `retrieval_efficiency`, `retrieval_loss`, `oracle_gap`, and
`specificity_margin` become **sums** of accuracies instead of differences, and the suite does
not notice. These are the quantity structure of the experiment — the decomposition the
preregistration is written in.

**2. `detect_topic_conditioning` (line 375) — all four mutations of its single decision line
survive; zero tests reference it.** This is the detector for the §6.3 `TOPIC-CONDITIONING`
verdict: *"the lift belongs to prompting, not to residue."* It is the exact failure mode that
would void the experiment's interpretation, it is the most likely benign-looking outcome by the
prereg's own reasoning, and **nothing tests it.**

**3. The primary estimator can be swapped for an unrelated helper (lines 362–364).**
`paired_bootstrap → _by_task_arm_solver` survives. So does `_task_level_series →
_by_task_arm_solver`, in both directions. The function that computes the confidence interval
can be replaced with a different function entirely and the suite stays green.

**4. McNemar discordant-pair counting is fully unprotected (lines 419–422).** `Eq → NotEq`
(×4), `And → Or` (×3), `Is → IsNot` (×2), and the index constants all survive. The paired test
at the heart of the design counts its pairs untested.

**5. Stratum handling (lines 428–438).** `Eq → NotEq` on stratum selection — which would select
every record *not* in the stratum — survives. So does `exploratory=True → False`, which
**relabels an underpowered stratum as confirmatory**; the prereg declares every D-stratum
exploratory by construction, and that label is unpinned.

**6. `benjamini_hochberg` (lines 154–168) and `paired_bootstrap`'s p-value: zero test
references.** The multiple-comparison correction the prereg mandates at q=0.05 is untested end
to end, and `p_value` is never asserted anywhere.

---

## What this does and does not mean

**It does not mean the code is wrong.** Every one of these mutants is a *hypothetical* defect;
the shipped implementation may be perfectly correct. What the measurement establishes is that
**if it were wrong in these specific ways, no test would tell us** — and the quantities involved
are exactly the ones the preregistration names.

**It does not block Tier B.** The gate is Harmonia B's exit review #3 plus the RULINGS §2
manifest re-pin (Charon's rulings, `574c8644`: band reachable, LEVELED at 0.4764 n=191, no
design defect, k=4 reps). This is a **pre-flight check on the instrument**, not a new gate and
not a new experiment.

**It is not a metabolization measurement.** Mutation score is *suite sensitivity to syntactic
perturbation*. It is not the B_eff numerator, and it must never be reported as one — zero of
the fifteen registered defect classes in `attacks/REGISTRY.md` are expressible as an AST-node
mutation, so this instrument samples a distribution that has never produced a confirmed kill
here. Its value is narrow and real: **before we spend money on an experiment, know whether the
code that will adjudicate it is arithmetically pinned.** Today it is not.

---

## Disposition

**Owner: Ergon** (driver; I am conflicted and do not touch this code). Suggested order, all $0:
1. Assert the five decomposition terms against hand-computed values — one test, catches #1.
2. Test `detect_topic_conditioning` in both polarities — catches #2, and it is the highest-value
   single test on this list because it guards the interpretation, not the arithmetic.
3. Assert `paired_bootstrap`'s CI bounds and `p_value` against a fixed-seed known input —
   catches #3 and most of #6.
4. Assert one McNemar table by hand — catches #4.
5. Assert `exploratory` is True on a D-stratum — catches half of #5.

**Kill condition for this finding:** if Ergon writes these assertions and every one passes on
first write against the current implementation, then the holes were cosmetic — the code was
right all along — and the correct conclusion is that the suite was under-specified, not that the
adjudicator was broken. That is a good outcome and it should be recorded as such rather than
quietly absorbed.
