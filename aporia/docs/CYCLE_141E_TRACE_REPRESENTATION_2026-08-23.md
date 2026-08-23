# CYCLE 141-E — TERMINAL: KILL (pass 1 of 3)

**Question:** CYCLE 140-D killed the operator vocabulary on elliptic-curve *counting* sequences and
its preregistered consequence required changing the **representation**, not the operator family.
So: does the vocabulary produce any non-trivial exact relation between the **Frobenius trace
sequences** of two non-isogenous elliptic curves over Q?

**Answer: no.** H = 0 over **294,909,843** reachable admissible triples, with the instrument
verified four independent ways.

## Why a_p is the right next representation

A counting sequence is a fact about the *catalogue* — how many curves happen to sit at each
conductor. The trace sequence `a_p = p + 1 - #E(F_p)` is a fact about the *object*: it is the
arithmetic content of the curve, it determines the L-function, and by Faltings/Tate it determines
the isogeny class. If the vocabulary reaches elliptic curves at all, this is where it must show.

`lfunc_lfunctions` was checked first and rejected: for degree-2 motivic-weight-1 rows
`dirichlet_coefficients` is NULL and `euler_factors` are stored as floating-point analytic
normalizations. A 20-term exactness bar cannot run on floats, so the coefficients were recomputed
exactly from `ainvs` by point counting over F_p.

**Disclosed judgment call:** computing a_p is ~15 lines implementing the definition of the object,
not an instrument build and not a modification of anything owned by another agent. Operators and
the `nondeg` guard were reused verbatim from `campaign_v_widen.py`. The judgment is disclosed
rather than buried, and it is guarded by four controls any one of which would expose a bad count.

## The instrument was verified before any null was read

    curves (conductor <= 2000):  11,308, each x 40 good primes
    C1 isogeny-identity : 5,454 same-class pairs, 0 mismatches      PASS
    C2 Hasse bound      : 0 violations of |a_p| <= 2*sqrt(p)        PASS
    C3 known values     : 11.a1 -> a_2=-2, a_3=-1, a_5=1, a_7=-2    PASS
    C4 independent algo : 1,811 brute-force O(p^2) checks, 0 disagreements  PASS

C1 is the strongest of these: isogenous curves must have identical trace sequences, and 5,454
pairs agree on all 40 terms with zero exceptions. C4 is a genuinely *different algorithm*, not a
restatement — the first draft of C4 compared `pr[2]*pr[3]` against `ap(...,2)*ap(...,3)`, which are
the same quantity and could not fail. That tautological safeguard was caught and replaced before
the run. It is exactly the unfalsifiable-safeguard failure the external reviews flagged.

## Reachability was made a term in the branch, not a note beside it

140-D's pass 1 computed attainability, printed it, and still routed a forced zero to KILL because
the vacuity branch tested only the controls. That was the second reachability defect caught at
adjudication in two passes. Here `attainable >= 1` is a **conjunct of every non-vacuous branch**.

Reachability was also computed **per operator**, which produced a finding of its own:

    target band: every target obeys |a_p| <= 27 (Hasse over the window)
      diff              10,071 / 11,092 sources reachable
      partsum            3,365 / 11,092
      binomial               0 / 11,092   STRUCTURALLY INCAPABLE
      moebius           10,675 / 11,092
      inverse_binomial       0 / 11,092   STRUCTURALLY INCAPABLE
      second_diff        1,978 / 11,092
      stirling2              0 / 11,092   STRUCTURALLY INCAPABLE

**Three of the seven non-trivial operators cannot fire on this representation at all.** Their
images escape the Hasse band for every one of 11,092 sources. This is not a null — it is a
structural statement about the vocabulary: `binomial`, `inverse_binomial` and `stirling2` are
calibrated for sequences with growth, and trace sequences are bounded by construction. Counting
their triples in the denominator would have inflated the attainable range by roughly 40% and
reported a gate as reachable when for those operators it never was.

So the honest denominator is the **reachable** one: 294,909,843 triples across the four operators
that could in principle fire.

## Result and verdict

    NON-TRIVIAL exact relations (headline): H = 0
    TRIVIAL-class relations:                 0
    BRANCHES: {B1_VACUOUS: False, B2_ADVANCE: False, B3_KILL: True}  (exactly one fired)

**CYCLE 141-E: KILL** at pass 1 of a permitted 3.

## What the two nulls together mean, and what they do not

Two independent representations of the *same objects* — counting sequences at 140-D, trace
sequences here — have both returned zero. That pair is the finding; neither alone would carry it.
The recorded pre-run risk said exactly this, so the write-up cannot now inflate a single expected
null into more than it is.

Per the preregistered consequence, the next cycle must change the **object class** or abandon the
vocabulary. It must **not** try a third representation of elliptic curves.

Explicitly not killed: the verbs thesis, and the 220 verified OEIS relations.

## Self-identified weaknesses

- A null here is close to the *expected* outcome. Trace sequences are Sato-Tate distributed and
  behave randomly; that two random-like integer sequences are not exact operator images of one
  another is unsurprising. The value is in it being the second representation, not in the null.
- Only 4 of 7 operators were capable of firing. The test of the "vocabulary" is really a test of
  `diff`, `partsum`, `moebius` and `second_diff` — and the operators native to L-functions
  (Dirichlet convolution, twisting, Euler-product manipulation) are **not in the vocabulary at
  all**. It is possible the vocabulary simply lacks the right verbs for this object rather than
  that no verbs exist, and this pass cannot distinguish those.
- Conductor <= 2000 and 40 good primes were chosen for compute. A relation appearing only at
  larger conductor or deeper into the prime sequence would be missed.
- The guard removed 216 of 11,308 sequences; small, and reported here beside the verdict.
- One object class, and a_p is one representation of it among several.

## Falsifier

A non-trivial exact operator relation between the trace sequences of two non-isogenous curves at
any conductor bound or prime depth; a curve pair whose a_p agree over 20 primes without being
isogenous (which would also contradict Faltings/Tate as implemented here); or the same sweep with
an operator set extended by Dirichlet convolution producing hits, which would locate the null in
the *vocabulary's* missing verbs rather than in the objects.

## Terminal

**CYCLE 141-E: KILL.** Elliptic curves are closed to this operator vocabulary in both
representations tested. The next attempt changes the object class or the vocabulary.
