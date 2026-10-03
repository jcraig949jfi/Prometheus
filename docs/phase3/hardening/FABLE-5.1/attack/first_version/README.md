# Reference harness v0 (FABLE-5.1 version of the Phase 3 hardening spec)

A conformance skeleton. It shows that each gate of
`../03_TEST_HARNESS_SPEC_FABLE.md` can return its registered answer on a
clean case and on a case broken on purpose. It runs on toy fixtures and on
four receipts that already existed. It qualifies no science.

    python -B -m unittest discover -v     31 tests
    python -B run_harness.py              rewrites RECEIPT_harness_v0.json

Standard library only. Deterministic. A few seconds.

## Layout

    rso_harness/verdict.py        G0   five verdicts and how they combine
    rso_harness/registration.py   G1   registered cell; receipt belongs to it
    rso_harness/stats.py          G2, G3   exact binomial: preflight, class exclusion,
                                       zero-hit bound
    rso_harness/retain1.py        the W0 world RETAIN-1; four positives, four impostors,
                                  four policies that need no retention, three broken runtimes
    rso_harness/rulers.py         G3, G4, G5   three rulers; entry; neutrality
    rso_harness/torture.py        G6, G8   observer, reset, restart; demand closure
    rso_harness/search.py         G7   exact and sampled reach on 8-bit landscapes; report labels
    rso_harness/audits.py         G9, G10   arms, clauses, sham, setting, contrast; the kit registry
    rso_harness/claims.py         G11, G12   custody; claims as functions of facets
    rso_harness/meta.py           GM   every gate against its clean cases and mutants
    tests/test_harness.py         the tests
    run_harness.py                writes the receipt

## What the receipt says

21 gates, each qualified: 34 clean cases pass and 62 mutants are rejected with
the verdict registered for them (34 FAIL, 14 BLOCKED, 13 UNQUALIFIED, 1
INDETERMINATE). Two known escapes are listed and pinned by tests.

The audits read `../../../review/FABLE-5.1/counterfeit/RECEIPT_gauntlet2.json`
and `RECEIPT_gauntlet3.json` and return, as verdicts, the faults three
reviewers found in those runs by hand.

## Limits

One author, one sitting. Four toy physics, one world, no noise. The mutants
were written by the author of the gates. See section 13 of the specification.
