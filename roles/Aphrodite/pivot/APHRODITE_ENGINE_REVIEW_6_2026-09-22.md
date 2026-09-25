+==============================================================================+
| APHRODITE LOCAL ENGINE -- SLICE 3: ORGAN EXTRACTION AND REUSE                |
| The organ supplies a capability. It does not guide a search.                 |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-22                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  DIRECT_COMPETENCE_REUSE = NO                                        |
|          STRUCTURAL_SEARCH_LEVERAGE = YES, but DEGENERATE -- read section 3  |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. RESULTS
------------------------------------------------------------------------------

Third family, selected mechanically: list_gcd. Organ sha256 5488abb9f635...
Escrow 400,000 charges per recipient. Whole experiment: 3.5 s.

  arm         M2 qualified   M1 median charges   M3 extrap   M4 @200   M5 bytes
  CLOSED          0/1              --              0.000      0.000     1570
  ORGAN          16/16             12              1.000      1.000     1578
  SCRATCH_A      16/16             12              1.000      1.000     1578
  SCRATCH_B       0/16             --              0.615      0.550     1393
  SHAM            0/16             --              0.615      0.550     1799
  POSITIVE        1/1              --              1.000      1.000     1578

ORGAN charges: min 12, max 12, n=16.  SCRATCH_A charges: min 12, max 12, n=16.

------------------------------------------------------------------------------
1. THE CLOSED TRANSPLANT FAILED. THAT IS THE ANSWER, NOT A PROBLEM.
------------------------------------------------------------------------------

list_prod_mod's complete fold -- INIT=1, E=(acc*v), F=(acc % last) --
transplanted UNCHANGED into a fresh recipient facing list_gcd scores 0.000 on
extrapolation, 0.000 on counterexamples, metamorphic FAIL.

    DIRECT_COMPETENCE_REUSE = NO

Nothing was modified in response, as the ruling requires. A fold that
multiplies is not a fold that takes gcds, and no amount of transplanting
changes that. What the artifact carries is a SHAPE, not a competence.

------------------------------------------------------------------------------
2. THE ORGAN WORKS -- AND SO DOES A CONTROL THAT ALREADY HAD THE FOLD
------------------------------------------------------------------------------

ORGAN: 16/16 recipients reached a tribunal-qualified solution, every one at
exactly 12 charges, filling the holes with INIT=0, E=gcd(acc,v), F=acc.
Qualified means: 1.000 at extrapolation lengths 20-60, 1.000 at stress length
200, 1.000 on counterexamples, metamorphic PASS -- having developed only at
lengths 4-9.

SCRATCH_A: also 16/16, also at exactly 12 charges, also 1.000 across the
board. IDENTICAL.

This is the null ADDENDUM 1 predicted before the run, reported here with the
prominence I promised: given a substrate that already contains the fold
mechanism, freezing the skeleton and restricting search to the holes buys
NOTHING. Relative to SCRATCH_A the organ is decorative, exactly as INVARIANT 1
says it must be.

------------------------------------------------------------------------------
3. THE COMPARISON THAT ISN'T A COMPARISON
------------------------------------------------------------------------------

SCRATCH_B -- the pre-slice-2C grammar, with no fold space at all -- reached a
qualified solution 0 times out of 16. It does find SOMETHING: a bounded
composition over the first three numbers that scores 0.615 at extrapolation,
0.850 on counterexamples, and FAILS metamorphic. (Taking the gcd of the first
few elements is often the gcd of all of them; the tribunal catches it.)

So the declared section-F test -- "ORGAN median M1 <= half SCRATCH median" --
is UNDEFINED: SCRATCH_B has no median charges-to-qualified, because it never
qualifies. On the M2 limb, ORGAN 16/16 vs SCRATCH_B 0/16 is as strong as a
result can be.

    STRUCTURAL_SEARCH_LEVERAGE = YES, on the M2 criterion only,
    with the M1 criterion DEGENERATE.

And "leverage" is the wrong word for what happened. The organ did not help a
search go faster. It supplied a mechanism class the substrate could not
express at all. The honest label is CAPABILITY SUPPLY, not search leverage:

    an evolved structural artifact gave a fresh recipient a computational
    resource its grammar did not contain, and the recipient then acquired a
    new capability that it provably could not have acquired without it.

That is a real and non-trivial statement. It is NOT recursive
self-improvement, and I will not describe it as such. The mutation generator,
evaluator, selection algorithm and evolve() are untouched by this slice.

SHAM is the control that makes this readable: carrying an equal-size
structural scaffold that failed slice-2C load-bearing (the decorative h//h
fossil) produced 0/16, with numbers identical to SCRATCH_B (0.615 / 0.550).
Carrying structure is worth nothing. Carrying the RIGHT structure is worth
everything. The difference between SHAM and ORGAN is the whole result.

------------------------------------------------------------------------------
4. WHY NO LEVERAGE COULD HAVE BEEN MEASURED HERE, EVEN IF IT EXISTED
------------------------------------------------------------------------------

The organ's hole space is 2 INIT x 30 E x 1 F = 60 candidates, and the
solution sits at position 12. An exhaustive search of 60 candidates is
instantaneous, so "guided vs unguided search within an available mechanism
class" is not a measurable contrast in this apparatus at all. ORGAN and
SCRATCH_A tie at 12 charges because there is nothing to win.

This is a POWER limitation of my design, and it was knowable in advance from
the size of the declared space. I did not know it in advance; I know it now
because the two arms tied exactly.

------------------------------------------------------------------------------
5. DEFECTS AND MISMATCHES DISCLOSED
------------------------------------------------------------------------------

D1 MY OWN CONTROL WAS VACUOUS, caught before running (ADDENDUM 1, commit
   341ad9f38). Section D's SCRATCH already contained the fold space, making
   it an organ-bearing arm under another name. I ran both rather than
   swapping, and section 2 reports the declared one first.

D2 SCRATCH_A AS IMPLEMENTED IS NOT QUITE AS DECLARED. The amendment says
   "composition + the full fold space"; the implementation searches the fold
   space only, omitting the composition stage. This makes SCRATCH_A CHEAPER
   than declared -- a harder, more conservative comparison for the organ --
   so the null in section 2 is not flattered by it. Disclosed rather than
   silently re-described.

D3 A LATENT EMISSION DEFECT, found while building this slice: an earlier
   patch rewrote `pow(` to `_pw(` in emitted fold bodies without emitting
   `_pw`'s definition, so a powr-using fold would have raised NameError in
   the sandbox and been scored wrong for the wrong reason. No slice-2C
   result is affected (its folds are acc+v and acc*v). Fixed; disclosed.

------------------------------------------------------------------------------
6. WHAT THIS ESTABLISHES, AT ITS EXACT SIZE
------------------------------------------------------------------------------

ESTABLISHED:
  - an organ extracted MECHANICALLY (Plotkin LGG, no hand definition, hashed
    before any family was selected) transfers a mechanism class across
    families, into a recipient that provably could not reach it otherwise
    (SCRATCH_B 0/16, SHAM 0/16, ORGAN 16/16)
  - direct competence does NOT transfer: the unchanged fold scores 0.000
  - the effect is attributable to the organ, not to carrying scaffolding
    (SHAM is identical to SCRATCH_B)
  - the third family was chosen by a declared lexicographic rule that never
    saw transplant performance, and the first candidate examined was rejected

NOT ESTABLISHED:
  - search leverage within an available mechanism class (section 4: not
    measurable here)
  - that the organ is anything more than a three-hole template; its content
    is a frozen loop skeleton, and the recipient still had to find gcd
  - anything about models, reasoning, or RSI
  - anything about Campaign 1, which remains unrun

------------------------------------------------------------------------------
7. IS THE NEXT RUNG MUTATION OF THE IMPROVEMENT MACHINERY? -- NO, NOT YET
------------------------------------------------------------------------------

The ruling requires an answer. Mine is that mutating the improver is NOT the
next scientifically justified rung, for a reason this slice supplies:

The interesting axis turned out to be MECHANISM-CLASS AVAILABILITY, not
search guidance. The organ's entire contribution was supplying a class the
grammar lacked; within a class the substrate already had, it contributed
exactly zero (section 2). Mutating the improvement machinery would add a
large new confound to an apparatus that cannot yet measure the simpler
quantity -- whether structure can make a search cheaper. With a 60-candidate
hole space, that quantity is unmeasurable by construction.

The next justified rung is therefore a mechanism space large enough that
"materially less search" is a measurable quantity at all: a family whose hole
space is combinatorially deep enough that exhaustive enumeration is
infeasible within escrow, so that guided and unguided search can actually
differ. Only if an organ demonstrably reduces search there does the question
"can the improver improve itself" have a measurable substrate underneath it.

Until then, improver mutation would produce numbers no one could interpret.
Tier 3 remains forbidden and I am not requesting it.

------------------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is CAPABILITY SUPPLY (section 3) a weaker or stronger claim than
    "structural search leverage"? I think it is different in kind, and that
    the ruling's vocabulary did not anticipate a possible-vs-impossible
    comparison. Is my relabelling honest or evasive?
Q2. ORGAN and SCRATCH_A tie at exactly 12 charges. Does that tie tell you
    the organ is worthless, or only that I built a search too small to
    distinguish anything? How would a reviewer tell those apart from outside?
Q3. SCRATCH_B scores 0.615 by taking the gcd of the first three numbers. How
    many real benchmark results are the same shape -- a local heuristic that
    looks like competence until something hostile asks it a longer question?
Q4. The organ is three holes and a loop. Is calling that an "organ"
    justified, or is the word doing persuasive work the artifact has not
    earned?
Q5. I answered section G with "no, not yet". Is that the right call, or am I
    declining the interesting experiment because my apparatus is too small
    for it -- which is an argument for building a bigger apparatus, not for
    stopping?

------------------------------------------------------------------------------
9. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  abad582c9  AMENDMENT 7, frozen before extraction/selection/search
  72af932dd  organ extracted and hashed before family selection
  341ad9f38  ADDENDUM 1, vacuous-control defect, before any arm ran
  roles/Aphrodite/engine/ORGAN_2026-09-22.json
  roles/Aphrodite/engine/THIRD_FAMILY_CERTIFICATE_2026-09-22.json
  roles/Aphrodite/engine/SLICE3_RESULTS_2026-09-22.json
  roles/Aphrodite/engine/{organ_extract.py, basis_v3.py,
                          certify_third_family.py, run_slice3.py}

+==============================================================================+
| END. "The organ is a template and the recipient did the work" is a           |
| first-class answer, as is "a tie at 12 charges means your apparatus          |
| cannot measure the thing you set out to measure -- fix that before           |
| anything else."                                                              |
+==============================================================================+
