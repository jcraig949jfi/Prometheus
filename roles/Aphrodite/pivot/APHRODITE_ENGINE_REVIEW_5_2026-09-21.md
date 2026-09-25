+==============================================================================+
| APHRODITE LOCAL ENGINE -- SLICE 2C EXECUTED                                  |
| A load-bearing variable-length accumulation mechanism, discovered            |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-21                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  16/16 QUALIFYING -- and the yield is the LEAST interesting number   |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. HEADLINE, AND THE CLAIM AT ITS EXACT SIZE
------------------------------------------------------------------------------

    discovery_yield                          16/16
    distinct_artifact_hashes                 1/16
    load-bearing in BOTH classes             16/16
    load-bearing in ONE class only           0/16
    total runtime                            22.7 s

THE PERMITTED CLAIM, frozen before the run and not exceeded:

  "Evolution discovered a load-bearing variable-length accumulation mechanism
   that transfers across tasks and survives extrapolation beyond the lengths
   encountered during discovery."

Not RSI. Not reasoning. A computational organ the substrate did not possess.

READ THE YIELD CORRECTLY. 16/16 does not mean the result is strong; it means
THE SEARCH PROBLEM WAS EASY. The declared fold space is 60-480 candidates and
the correct fold is the unique exact fit on two development instances, so
discovery was close to guaranteed once the mechanism space existed. The
scientific content is in the ADJUDICATION, not the yield.

------------------------------------------------------------------------------
1. WHAT WAS DISCOVERED
------------------------------------------------------------------------------

Identical in all 16 lineages, searched not supplied:

    list_sum        acc = 0;  acc = acc + v;   return acc
    list_prod_mod   acc = 1;  acc = acc * v;   return acc % last

    class          base   extrapolation(20-60)  stress(200)  ce    metamorphic
    list_sum       0.00          1.00              1.00      1.00     PASS
    list_prod_mod  0.00          1.00              1.00      1.00     PASS

Development saw ONLY lengths 4-9. The tribunal judged at 20-60 and at 200,
from an artifact of FIXED SIZE (1770 bytes). No bounded unrolling does that.

Surrogate battery, post-freeze, no feedback to search: constants,
identity/passthrough, every single primitive application including over
`last`, and single-iteration control flow. SURVIVORS: ZERO, for both classes,
in all 16 lineages. The mechanism is load-bearing under INVARIANT 1.

Membrane: 16/16 clean. hash_at_extraction == hash_at_load == artifact sha256,
crossed == {artifact_bytes}, donor_reads == [artifact sha256].

------------------------------------------------------------------------------
2. THE REUSE QUESTION, ANSWERED PRECISELY RATHER THAN FLATTERINGLY
------------------------------------------------------------------------------

The frozen question was whether evolution could discover a load-bearing fold
AND REUSE IT across more than one family. The honest answer is narrower than
"16/16 both classes" sounds:

  The artifact contains TWO SEPARATE fold functions, `_fold_list_sum` and
  `_fold_list_prod_mod`, each dispatched to its own family.

So what generalised is the SCHEMA -- accumulate over a variable-length
sequence -- discovered independently for each family. It is NOT one organ
serving two families. That distinction is the whole difference between
"the mechanism class is reachable twice" and "the mechanism is reusable", and
only the transplantation rung can settle it.

------------------------------------------------------------------------------
3. CONVERGENCE (RULING 2: reported, never engineered)
------------------------------------------------------------------------------

    independent launched lineages     16
    distinct extracted hashes          1
    escrow spend range           908 - 15,908

All 16 lineages converged on one artifact while spending between 908 and
15,908 charges -- they took DIFFERENT search paths, with different
development instances and different search orders, to the same destination.
Under RULING 2 that is evidence about the search LANDSCAPE: with a small
declared mechanism space and an exact-match criterion, the correct fold is
effectively the only fixed point. No diversity was engineered and none is
claimed.

------------------------------------------------------------------------------
4. TWO APPARATUS DEFECTS FOUND, BOTH DISCLOSED
------------------------------------------------------------------------------

D1 UNGUARDED EXPONENTIATION (caused a 1.66 GB hang, not a slow run).
   The declared primitive `powr` bounds its exponent to [0, 32]. My fold
   evaluator called raw `eval` on the emitted template and ignored that
   bound, so a candidate of the form pow(v, acc) attempted pow(base, 10^40)
   BEFORE any ceiling check could reject it. The first slice-2C run consumed
   1.66 GB and had to be killed.
   CLASS: conformance defect, same family as the asymmetric enumerator -- the
   implementation was not instantiating the declared grammar.
   REPAIR: the declared bound is now enforced before the operation, in BOTH
   the search evaluator and the emitted artifact source, so search and
   execution agree about what the grammar means.
   EFFECT ON RESULTS: none. The basis-separation certificate was re-run after
   the repair and reproduces IDENTICALLY -- same witnesses, same accuracies,
   collatz still rejected. Runtime fell from a 20-minute hang to 22.7 s.

D2 STALE TELEMETRY. `structural_telemetry` looked only for slice-2B `_h_`
   helpers, so it reported contains_loop=False and helper_count=0 for
   artifacts containing TWO `for` loops. Telemetry only -- adjudication is
   done by the surrogate battery, so nothing in section 1 is affected -- but
   THE TELEMETRY FIELDS IN SLICE2C_RESULTS_2026-09-21.json ARE WRONG. The
   corrected reading for the (identical) artifact is: fold_count 2, folds
   [_fold_list_sum, _fold_list_prod_mod], contains_loop true, invoked true.
   The function is repaired; the stale JSON is left as written, with this
   correction attached.

A third process failure, not a code defect: an earlier run reported exit code
0 having been killed on detachment, writing no results. I reported it to the
operator as "still running" when it had already died. That was wrong, and the
later relaunch used a log file that survives detachment.

------------------------------------------------------------------------------
5. A CRITERION MISMATCH I AM DISCLOSING RATHER THAN QUIETLY RENUMBERING
------------------------------------------------------------------------------

AMENDMENT 6 lists Q1-Q8. The implementation records Q1, Q3, Q4, Q5, Q6, Q7,
Q8 -- there is no separately keyed Q2 ("differ causally from the base
image"). Q2 is in substance covered by Q4, which compares against the base
image's tribunal score (0.00 -> 1.00 on both classes), but the criteria
dictionary does not contain a Q2 entry and the frozen amendment says it
should. Recorded as a documentation/implementation mismatch; no artifact's
disposition changes under either reading.

------------------------------------------------------------------------------
6. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

ESTABLISHED:
  - a mechanism the arithmetic basis cannot express was discovered
    endogenously, crossed the qualified membrane, and raised a fresh
    recipient from 0.00 to 1.00 on two independently falsified classes
  - it survives hostile counterexamples and oracle-free metamorphic checks
  - it EXTRAPOLATES from training lengths 4-9 to 20-60 and to 200 at fixed
    artifact size, with the single-iteration surrogate at 0.000
  - zero simpler surrogates reproduce it: load-bearing under INVARIANT 1
  - the basis-separation certificate did its job -- it authorised these two
    families and REJECTED collatz_steps in advance

NOT ESTABLISHED:
  - that discovery is hard, or that the search is powerful (16/16 in 22.7 s
    says the opposite)
  - that one organ is REUSED across families (section 2: two separate folds)
  - anything about models, reasoning, or recursive self-improvement
  - anything about Campaign 1, which remains frozen and unrun

------------------------------------------------------------------------------
7. RECOMMENDED, NOT EXECUTED
------------------------------------------------------------------------------

The next rung, as the operator framed it: excise the fold organ and
transplant it into a fresh recipient facing a THIRD compatible
variable-length family it was never evolved against, and ask whether it
provides reusable leverage there. Section 2 is exactly why that experiment is
now the interesting one rather than a formality -- this slice produced schema
recurrence, and only transplantation distinguishes that from mechanism reuse.

It requires its own authorisation, a third family that passes the
basis-separation certificate in advance, and a decision about whether the
transplanted organ may be adapted (a fold whose E and F are re-searched is
not the same claim as a fold used as-is).

------------------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is a 16/16 yield evidence of anything, or only that I chose a mechanism
    space small enough to be exhaustively searched? What yield would have
    been more informative, and could I have known that in advance?
Q2. Two separate folds versus one reused organ -- is the distinction I draw
    in section 2 the right one, or am I being too hard on a result that did
    generalise a schema across two task types?
Q3. The tribunal judged at lengths 20-200 having trained at 4-9, and the
    artifact held at 1.00. Is length extrapolation a good proxy for
    "genuinely iterative", or is there a mechanism that would pass it
    without being iterative?
Q4. D1 hung the run for twenty minutes because my search ignored a bound its
    own declared primitive specifies. How many published agent-search results
    would survive an audit of whether the implemented grammar equals the
    declared one?
Q5. Should a slice whose defects were found by ITS OWN failure modes (a hang,
    a stale telemetry field) be trusted more or less than one that ran
    cleanly first time?

------------------------------------------------------------------------------
9. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  dfde59cc9  AMENDMENT 6 + slice-2C design, FROZEN PRE-RUN
  roles/Aphrodite/engine/AMENDMENT_6_2026-09-21.md
  roles/Aphrodite/engine/BASIS_SEPARATION_CERTIFICATE_2026-09-21.json
  roles/Aphrodite/engine/SLICE2C_RESULTS_2026-09-21.json  (per-lineage rows;
                                       telemetry fields stale, see section 4)
  roles/Aphrodite/engine/{basis_v2.py, slice2c.py, run_slice2c.py,
                          certify_basis_separation.py}
  roles/Aphrodite/library/METHODOLOGY.md  (INVARIANTS 1-4)
  unpooled predecessors: slice 2B (IMPAIRED, SLICE2B_VALIDITY_SCAR.md),
                         slice 2C gate stop (AMENDMENT_4)

+==============================================================================+
| END. "This proves only that a tiny search finds a tiny program" is a         |
| first-class answer, as is "schema recurrence is not reuse -- do the          |
| transplant or stop claiming organs."                                         |
+==============================================================================+
