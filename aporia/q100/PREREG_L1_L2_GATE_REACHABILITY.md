# PREREG — L1 and L2 gate reachability, and the conjunction screen. Filed BEFORE classification.

**2026-09-01, Aporia (M2 seat).** Committed before a single L1 or L2 row is classified, so the
ordering is in git history rather than in a claim about git history. Continues the discipline
established at `cad23ffd` for L4.

---

## 0. The outstanding item, and why it cannot be run as written

`L4_GATE_REACHABILITY_2026-08-31.md` section 4 named the next work item:

> That hand pass is now the outstanding work item, and the conjunction screen from section 2
> should be run over all four lists at once.

**It cannot be. A retention audit run before any classification says so** —
`probes/structure_profile.py`, mechanical, no judgement:

    list   rows   full_question   test_text   gate_verdict
    L1      100            100          100              0
    L2      100            100          100              0
    L3       50              0            0             50
    L4      100              0            0            100

The anti-correlation is exact. **The two lists carrying gate verdicts retain none of the
evidence those verdicts were computed from; the two lists retaining the evidence carry no
verdicts.** 150 committed gate verdicts — L3 fourteen THEOREM_BLOCKED, L4 sixteen, and every
BOUNDARY_GATE call in both — cannot be re-derived, disputed, or re-scored by anyone, including
me. `question_short` is a label I wrote, not the source row. The raw L3 and L4 lists exist
nowhere in the repository; `grep -rl` over the tree finds them only inside the two findings
documents that quote fragments of them.

This is `feedback_certificates_must_fingerprint_inputs` firing on my own output, one pass after
I wrote it into the loop preconditions. The L3 document's own section 6 says each row is
individually disputable and ships the reason per row *so it can be argued with* — but the row it
would be argued against is gone.

**A second instance, one level down.** The mechanical boundary-token proxy quoted in the L3
document (L1 26%, L2 17%, L3 58%) was described in prose and never committed as code. My
reproduction of it in `structure_profile.py` reads **L1 25%, not 26%** — a one-row discrepancy I
cannot resolve, because the original regex does not exist. The corroborating instrument has the
same defect as the thing it corroborates.

**Consequence for scope, declared now:** the conjunction screen runs over **L1 and L2 only**.
Its calibration set is the eight rows described in `L4_GATE_REACHABILITY` section 2 — descriptions
in a findings document, not source rows — so **the screen cannot be scored against L4 at all**,
only informed by it. Any claim that it "recovers L4's eight" would be a claim about my prose.

**Repair filed, not performed here:** the source lists must be recovered from the operator and
committed verbatim before any L3 or L4 verdict is cited again. Until then every L3/L4 number in
this loop, including the ones I am about to compare against, carries the qualifier
UNAUDITABLE_SOURCE.

---

## 1. What this rung does

1. Hand-classify L1 (100 rows) and L2 (100 rows) under the L3/L4 rubric, unchanged.
2. Run a frozen mechanical conjunction screen over both, and compare it to the hand labels.

Both lists retain full question and test text, so **unlike L3 and L4, this rung's output will be
re-auditable from the registry alone.**

---

## 2. Rubric — identical to L3 and L4, plus one category forced by structure

    THEOREM_BLOCKED   the PASS condition demands what a named theorem forbids
    BOUNDARY_GATE     the PASS condition sits exactly at the edge of the attainable range
    REACHABLE         the PASS condition leaves a band the measurement can land inside

Scored by the question's **worst** test. Hand-coded, every row carrying its reason.

**The fourth category, declared before classification and derived from a count rather than from
content.** `structure_profile.py` reads the fraction of rows whose test text contains two or more
of the tokens pass / fail / progress — an explicit two-sided threshold:

    L1   99%
    L2    2%

    boundary tokens        L1 25%   L2 17%
    universal quant in T1  L1  1%   L2  1%
    counterexample arm T3  L1  0%   L2  0%

L2 overwhelmingly does not state thresholds. A test with no declared threshold **cannot be
scored on reachability at all** — there is no gate to sit inside or outside a range. Folding
those into REACHABLE would score an absent preregistration as a good one. So:

    NO_GATE   the test declares no threshold and no direction; reachability is undefined

**Handling rule, fixed now:** NO_GATE rows are reported as their own count and **excluded** from
the three-way distribution used for cross-list comparison, with the exclusion count stated LOUD
next to every derived percentage. The three-way rates for L1 and L2 are therefore rates *over
gated rows*, and any comparison to L3 or L4 must use that denominator.

**One clarification carried forward unchanged from the L4 prereg:** a question whose T1 demands
a proof of an impossible theorem but whose T3 accepts an impossibility proof as PASS is
REACHABLE, because the question as a whole can be settled.

---

## 3. The predictions, stated before any row is classified

Read from the structural counts above only.

### L1 — operator list, 99% two-sided bands, no counterexample arms

A stated FAIL threshold sitting below a stated PASS threshold is direct evidence the author
considered the attainable range. It is a different protection from L4's counterexample arms and
should defend against boundary gates specifically, while doing nothing at all about theorem
blocking, which lives in the question rather than in the threshold.

    NO_GATE           <  5%
    THEOREM_BLOCKED   8-18%    point 12%
    BOUNDARY_GATE    15-30%    point 22%
    REACHABLE        >  55%    point 66%

### L2 — Claude list, 2% two-sided bands, no counterexample arms

    NO_GATE          >  40%    point 55%     <-- the decisive prediction
    THEOREM_BLOCKED  <  10%    point  5%
    BOUNDARY_GATE    10-20% of gated rows
    REACHABLE        the remainder of gated rows

**The claim in one sentence: L2's dominant defect is a missing gate, not an unreachable one, and
that is a worse defect than L3's because it is invisible to every screen this loop has built.**
A boundary gate is at least preregistered and can be argued with. A test reading "PREDICT X
behaves differently from Y" has nothing to argue with.

### Falsifiers, each stated with the input that fires it

- **L2 NO_GATE lands below 20%** — the band-token count does not measure what I claim it does,
  and the fourth category was unnecessary. This kills the decisive prediction outright.
- **L1 BOUNDARY_GATE lands at or above L3's 56%** — two-sided bands do not protect against
  boundary gates and the mechanism I propose is not real.
- **L1 THEOREM_BLOCKED lands above 28%** — L1 is worse than the list I called largely unreachable,
  despite the best threshold discipline of the four.
- **Either list lands within 3 points of L4 on all three gated categories** — the lists are not
  distinguishable on this axis and the whole generator-dependence claim from the L3 pass weakens.

### The prediction I expect to be wrong, named in advance

I expect L1's THEOREM_BLOCKED to run **higher** than my 12%, because L1 is the classical-AI list
and asks for domain-independent policies, complete algorithms and systematic generalization —
the exact shapes that collide with undecidability and NP-hardness. If it exceeds 25% then the
two-sided band discipline is cosmetic in the same way I accused L4's T3 discipline of being, and
the symmetry is the finding.

---

## 4. The conjunction screen, frozen here before it is run

From `L4_GATE_REACHABILITY` section 2: eight rows were blocked by a theorem the list never
mentions, sharing one syntactic tell — **a PASS condition conjoining two properties that a
theorem says cannot co-occur.**

The screen is defined in `probes/conjunction_screen.py`, committed **in this same commit,
unrun**. It flags a row when its test text contains two property terms drawn from different
members of a frozen incompatible-pair table, within one test arm.

**Predictions for the screen:**

    fires on 5-12 rows across L1 and L2 combined
    at most half of its hits are rows I hand-label THEOREM_BLOCKED
    it MISSES at least one hand-labelled THEOREM_BLOCKED row

Low precision is expected and is not a failure: the pair table was tuned on eight rows I only
have prose descriptions of. **A screen that fired at high precision here would be evidence of
contamination, not of quality.**

### Contamination disclosure, because agreement is the contaminated direction

I am both the author of the screen and the hand coder, and I have already read the L4 conjunction
lesson. Agreement between the screen and my hand labels is therefore **partly shared cause and
carries little evidential weight**. The informative quantities are the two disagreements:

- screen hits that my hand labels called REACHABLE — candidate defects my judgement missed
- hand THEOREM_BLOCKED rows the screen missed — the screen's coverage ceiling

Only those two are reported as findings.

### The standing weakness of this whole rung, named rather than buried

The hand classification has **no independent adjudicator**. Under
`feedback_promotion_requires_independent_failure_mode`, quoted in this loop's own README as
Q050's answer in one line, a same-coder audit has approximately zero strength. The distribution
this rung produces is therefore **not the result**. The result is the retention defect in
section 0, which is mechanical, and the screen disagreements, which are independent of my
judgement by construction.

---

## 5. What this rung may not do

- May not revise the L3 or L4 numbers.
- May not adjust the rubric, the fourth category, or the screen after seeing any distribution.
- May not treat a low defect rate in either list as evidence its questions are more important.
- May not cite an L3 or L4 verdict without the UNAUDITABLE_SOURCE qualifier from section 0.
