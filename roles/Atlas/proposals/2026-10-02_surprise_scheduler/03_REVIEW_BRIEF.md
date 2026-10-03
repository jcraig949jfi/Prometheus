# Review brief for agents asked to review this proposal

Atlas, 2026-10-02.
- You are reviewing a PROPOSAL (01_EXPERIMENT_SERIES.md). Nothing has been executed.
- Please do not execute any part of it, launch anything, or contact other seats on its behalf.
- Write your review as a file and hand it back to the operator.
- If you are a Claude-family model, say so. The proposal treats one-model-family review as a known weakness, and at
  least one review should come from a different model family.

## What to read
1. 00_OPERATOR_NOTE_verbatim.md: the idea as the operator stated it.
2. 01_EXPERIMENT_SERIES.md: the series E0-E6.
3. 02_FURTHER_RESEARCH.md: unverified claims and open design questions.
4. Optional evidence: roles/Atlas/inference_harvest_2026-09-30/ (synthesis, contradictions, buried signals, and the
   verifier tables in workers/).

## Questions (answer the ones in your competence; mark the others "not reviewed")

**Q1. Answer key (E0).**
- Are any listed ARTEFACTS actually unresolved, or any SURVIVORS actually artefacts?
- Check at least 5 items against their primary sources (pointers are given).
- Is the three-tier provenance scheme adequate?

**Q2. Leakage (E1).**
- Is the as-of rule sufficient?
- Can the answer leak through design columns? Example: the mere presence of a "material provenance" column reveals
  that a location-label defect was found.
- Is the leakage audit (trivial classifier AUC <= .60, a canary must fire, text grep) strong enough?

**Q3. Repaired-instrument columns.** Should columns that exist only because a defect was discovered (e.g. CVT-R
results, Bernoulli-ruler re-reads) be in the table?
- If yes: they leak.
- If no: the searcher cannot find what the repair found.

Propose a rule.

**Q4. Arms (E2).**
- Is the comparison fair when all arms share one hypothesis generator?
- Should a bandit baseline (UCB/Thompson) or a pure expected-information-gain (BOED) arm be added?
- Is P4 (null-model prior) well defined?

**Q5. Certification gate (E2).**
- Is "multiplicity-controlled test + beats a zero-parameter baseline + not on the veto list" the right definition of
  a certified finding?
- What would make the gate itself a ruler that cannot fail?
- How should the veto list be built without encoding the key?

**Q6. Endpoints and decision rules.**
- Are certified findings per 100 tests (primary) and false-finding burden (co-primary) the right pair?
- What margin would you pre-register for "P3 beats P2"?

**Q7. Observers (E3).**
- How should the "alien" observer (O8) be constructed so that it is not simply an LLM with an instruction?
- Is the disagreement statistic sound?

**Q8. Null calibration (E4).** Are the synthetic null tables hard enough? They keep the marginals and correlations of
the real table, with outcomes independent of design.

**Q9. Non-stationary surprise (E5).** Is item ordering by claim date valid when many items were claimed and exposed
within the same few days (09-19..09-30)?

**Q10. Model-family dependence.**
- Where else in the design does one model family set the outcome? Consider the hypothesis generator, the interpreter,
  and the adjudication of NEW findings.
- Propose a cheap control for each place you find.

**Q11. Missing experiments.** What would you add or cut? Is there a cheaper experiment that answers the operator's
core question ("does surprise-guided search converge on the anomalies that mattered, or chase artefacts?")?

**Q12. Scope.** Does anything here exceed Atlas's charter? Atlas indexes and analyses; it does not run seats' science
or command seats.

## Format of your review
- One file named REVIEW_<reviewer>_<model>_<date>.md.
- For each question: your answer, the evidence you checked (path:line@sha), and a severity:
  - BLOCKING: the series should not run as designed;
  - MAJOR: change before freeze;
  - MINOR.
- End with a one-paragraph overall verdict.
