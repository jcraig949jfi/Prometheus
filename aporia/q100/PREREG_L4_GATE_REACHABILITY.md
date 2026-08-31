# PREREG — L4 (DeepSeek) gate reachability. Filed BEFORE classification.

**2026-08-31, Aporia.** Committed before a single L4 row is classified, so the ordering is in
git history rather than in a claim about git history.

## 0. Correction to the record, first

**L3 is GEMINI, not DeepSeek.** `REGISTRY_L3.jsonl` and
`L3_GATE_REACHABILITY_2026-08-31.md` were committed at `b087f4cc` with the wrong attribution.
Corrected in the same commit as this preregistration. The measurements in that document are
unaffected — only the generator's name was wrong — but provenance is part of the evidence, and a
mis-attributed source in a committed record is exactly the kind of defect this loop exists to
catch. L4 is DeepSeek, 100 rows, complete.

## 1. Why this rung exists

The L3 analysis disclosed that its classification was **not a fired prediction** — I saw the list
before classifying it. The criterion (`feedback_gate_must_be_shown_reachable`) predated the data,
but the application did not. This preregistration fixes that for L4.

## 2. The prediction, stated before measurement

Reading L4's *structure* only — not classifying its content — one feature is visible and is the
basis of the prediction:

**L4's T3 arms are systematically counterexample hunts rather than additional demands.** The
recurring shape is: T1 give the algorithm and prove the theorem; T2 an empirical benchmark with a
numeric band; **T3 "show a case where it fails; fail if found."** That is a negative control, and
it is the arm L3 almost never had.

Second visible feature: **L4 converts known hardness results into PASS conditions rather than
demanding their violation.** Q5's T3 passes if a reduction from Petri-net reachability
establishes undecidability. Q9's T3 uses a #P-hardness reduction as the falsifier. Q79's
why-column names Gibbard-Satterthwaite and says general solutions are impossible.

**Therefore I predict, before classifying:**

    L4 THEOREM_BLOCKED   < 10%     (L3 measured 28%)
    L4 REACHABLE         > 50%     (L3 measured 16%)
    L4 UNREACHABLE       < 50%     (L3 measured 84%)

**Falsification:** if L4's theorem-blocked rate lands at or above L3's 28%, the structural
features above do not protect against unreachable gates and my reading of the T3 pattern is
wrong. If L4's reachable rate lands below 30%, the prediction fails outright.

**A prediction I expect to be wrong somewhere, named in advance:** L4 asks for exact/polynomial
solutions to several problems whose why-columns concede NP-hardness or undecidability (Q17
planning, Q26 latent-confounder structure learning, Q78 multi-agent POMDPs at NEXP). Those may
be theorem-blocked despite the good T3 discipline, because the *question* is impossible even when
the *falsifier* is well-formed. My guess is that this affects fewer than ten rows; if it affects
more than twenty, the T3 discipline is cosmetic.

## 3. Rubric — identical to L3, unchanged, so the comparison is valid

    THEOREM_BLOCKED   the PASS condition demands what a named theorem forbids
    BOUNDARY_GATE     the PASS condition sits exactly at the edge of the attainable range
    REACHABLE         the PASS condition leaves a band the measurement can land inside

Scored by the question's **worst** test. Hand-coded, every row carrying its reason, individually
disputable. The same mechanical boundary-token regex is run alongside as a reproducible
corroborator.

**One rubric clarification, fixed now rather than after seeing results:** a question whose T1
demands a proof of an impossible theorem but whose T3 accepts an impossibility proof as PASS is
**REACHABLE**, because the question as a whole can be settled. That distinction is what
separates "asks for the impossible" from "asks whether it is possible", and L3 largely lacked it.

## 4. What this rung may not do

- May not revise the L3 numbers to make the comparison cleaner.
- May not adjust the rubric after seeing L4's distribution.
- May not treat a low L4 defect rate as evidence L4's questions are more *important* — only that
  its tests are better posed.
