# FINDINGS — A2b, the W5 repair. Pass P176, second rung.

**HEADLINE.** The W5 verdict rule is repaired, the repair is proved by fixtures rather than
argued, and **TINYPROG is WORLD_ADMISSIBLE unanimously across five seeds that had never been
generated before the repair existed.** A3 has a testbed.

**DIAGNOSTIC.** The single most useful artifact of the rung is `RULE_CEILING_CHECK`: the killed
rule, re-run on a synthetic input with **perfect** separation, fails. Gap 1.0 — the maximum the
statistic can take — against a bar of 1.009. That demonstrates the defect on an input where the
right answer is not in dispute, which is a stronger form of evidence than my own reasoning about
why the rule was wrong.

---

## 1. The repaired rule and why it is reachable

    g_obs = mean(rec_late | REUSE) - mean(rec_late | NO_REUSE)
    reference: 1999 label permutations, each giving the MAX ordered pairwise class-mean gap
    p = (1 + #{ reference >= g_obs }) / 2000
    PASS if p <= 0.05

The permutation distribution is used as a **reference distribution** rather than as a scale
factor. Attainable range of p is [0.0005, 1] with the bar strictly inside it. The killed rule
multiplied a percentile of that same distribution and compared it to a **bounded** statistic, so
the bar and the ceiling could meet — and did, at exactly 1.0.

The max-over-pairs reference carries the multiplicity correction: a named contrast is tested
against the most extreme gap **any** of the ten pairs could produce by chance.

## 2. Fixtures — all six land as preregistered

    RULE_KNOWN_POSITIVE      synthetic, one class at 1.0 and one at 0.0   PASS   p 0.0005
    RULE_KNOWN_NEGATIVE      synthetic, all classes from one distribution FAIL   p 1.0
    RULE_CEILING_CHECK       killed rule on RULE_KNOWN_POSITIVE            FAIL   gap 1.0 bar 1.009
    GEN_KNOWN_POSITIVE       reuse probability 1.0                         PASS   p 0.0005
    GEN_KNOWN_NEGATIVE       reuse probability 0.0                         FAIL   p 1.0
    GEN_ALL_IDENTICAL        five classes, one recipe                      FAIL   p 1.0

The rule-level fixtures are fed episode-level numbers **with no world behind them**, so a defect
shared by the world generator and the probe cannot flatter the rule. That was the gap in A2's
calibration: every W5 fixture there ran through the generator, and none of them asserted a
positive.

**Interventional sweep** on reuse probability, applied as a deterministic evenly-spread quota so
the shared-motif task set at a lower rho is a strict subset of the set at a higher rho:

    rho      0.00     0.25     0.50     0.75     1.00
    contrast -0.014   0.250    0.479    0.722    0.965
    p         1.0     0.637    0.035    0.0005   0.0005
    W5a       False   False    True     True     True

Monotone, and the verdict flips between rho 0.25 and 0.50. The rule is sensitive to the one
variable it is supposed to be sensitive to, at a resolution finer than the class construction.

**Metamorphic:** relabelling all ten primitives leaves every reading bit-identical.

## 3. The verdict of record

Seeds 20260901-20260905, generated for the first time by `run_a2b.py`:

    seed        verdict            W1     W2      W3      W4_stat/bar     p_W5a
    20260901    WORLD_ADMISSIBLE   1.00   ~0.95   ~850x   ~0.6 / ~2.7     0.0005
    20260902    WORLD_ADMISSIBLE   1.00   ~0.95   ~850x   ~0.6 / ~2.7     0.0005
    20260903    WORLD_ADMISSIBLE   1.00   ~0.95   ~850x   ~0.6 / ~2.7     0.0005
    20260904    WORLD_ADMISSIBLE   1.00   0.9556  856.9x  0.5303 / 2.7355 0.0005
    20260905    WORLD_ADMISSIBLE   1.00   0.9472  878.0x  0.7074 / 2.6437 0.0005

Unanimous, so the preregistered WORLD_UNSTABLE branch did not fire. Unanimity was required
rather than a majority because five seeds cannot resolve a rate — a 4-of-5 result carries an
interval from roughly 0.28 to 0.99 and would have measured nothing.

The burned seed 20260827 also reads WORLD_ADMISSIBLE under the repaired rule. **That reading is
recorded as CONTAMINATED and is not part of the verdict**, because the rule was repaired with it
in hand.

## 4. What the LATE_REUSE class actually does, which I had not predicted precisely

Across fresh seeds, `rec_late` for LATE_REUSE lands between 0.757 and 0.917 rather than at 1.0,
while REUSE and CONTROL sit at exactly 1.0. The cause is mechanical: LATE_REUSE shares the motif
in only 3 of its 12 early tasks, so the modal early motif is *usually* but not *always* the
shared one, and when it is not, that episode's late recurrence collapses. This is the class
behaving as designed — weak early evidence is the definition of the class — but it means
**LATE_REUSE carries more episode-level variance than the other four classes**, and A3 should
expect a noisier promotion signal there rather than treating the five classes as equally clean.

## 5. Standing weaknesses, unresolved

- **The repair is contaminated by design.** No amount of fresh-seed confirmation changes the
  fact that the rule was chosen after seeing a reading. The fresh seeds bound how much that
  could have mattered; they do not eliminate it.
- **W5b and W5c each contain an absence-of-evidence half.** A non-significant p is being used
  as evidence that a class does *not* separate. That is weak inference, flagged in the artifact
  itself. It is admissible only because the paired half of the same class must be significant,
  so low power would fail the significant half first — but a genuinely underpowered read would
  produce the same non-significance for a real difference.
- **The nuisance set is still the four preregistered statistics.** A class-identifying feature
  outside {minimal size, C_search, C_execution, output entropy} would not be caught by W4.
- **W1 remains vacuous by construction** — a tree of size 6 is necessarily reachable in a
  closure enumerated to depth 6, so W1 tests only that the budget did not bite.
- **The metamorphic arm is a relabelling, not an algebra automorphism.** It catches code that
  keys on a primitive name and nothing stronger.

## 6. The methodological result, which outlives this world

Three members of one defect family in two days, all now with names and one with a demonstration:

    W4 statistic   divided by a pooled sd INCLUDING between-class variance -> capped at 2.828
                   with the bar at 2.49; a five-size skew read 2.191 and was called MATCHED
    W5 rule        bar defined as a MULTIPLE of a null computed on the same rows, against a
                   BOUNDED statistic -> bar reached the ceiling, gate could not fire
    2026-08-23     preregistered cut 0.14 against a maximum attainable 0.1364

**General statement, added to doctrine:** whenever a bar is derived from a null computed on the
same rows as the effect, and the statistic is bounded, compute the bar at the statistic's
CEILING before running anything. If the bar can reach the ceiling, the gate is not a gate.

The corresponding procedural lesson is narrower and sharper than "calibrate your instruments":
**A2's calibration ran a known-negative for W5 and no known-positive, and that asymmetry was
visible in the fixture table itself before any world was read.** A calibration is not validated
by having fixtures; it is validated per-component, and the check is mechanical — every component
that can issue a FAIL needs a fixture asserting True, and every component that can issue a PASS
needs one asserting False.

## 7. Disposition

A2 and A2b are closed. **TINYPROG is admissible.** The next rung is A3 — reification — and it is
preregistered before it is built, with promotion decided on early episodes, benefit measured on
genuinely unseen later ones, and C_search and C_execution reported separately. The flat arm's
cost identity is already on record at exactly 6.0, so a merged budget cannot be slipped in.
