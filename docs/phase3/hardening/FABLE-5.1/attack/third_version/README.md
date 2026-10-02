# Reference harness v0 (FABLE-5.1 version of the Phase 3 hardening spec)

A conformance skeleton. It shows that each gate of
`../03_TEST_HARNESS_SPEC_FABLE.md` returns its registered answer on sound
cases and on cases broken on purpose. It runs on toy fixtures and on four
receipts that already existed. It qualifies no science.

    python -B -m unittest discover -v     103 tests, under a minute
    python -B run_harness.py              rewrites RECEIPT_harness_v0.json
    python -B mutation_probe.py           about ten minutes; rewrites
                                          RECEIPT_mutation_probe.json

Standard library only. Deterministic.

## Layout

    rso_harness/verdict.py        G0   five verdicts and how they combine
    rso_harness/stats.py          G2   exact binomial tails; preflight; the
                                       five places a score can stand
    rso_harness/registration.py   G1   registered cell; receipt belongs to it
    rso_harness/retain1.py        the W0 world RETAIN-1; four positives, four
                                  impostors, a weak positive, baselines,
                                  runtimes and worlds broken on purpose
    rso_harness/rulers.py         G3, G4, G5   three rulers; exclusion; entry;
                                               neutrality
    rso_harness/torture.py        G6, G8   observer, reset, restart; demand
                                           closure against a baseline list
    rso_harness/search.py         G7   exact and sampled reach on 8-bit
                                       landscapes; reports are replayed
    rso_harness/audits.py         G9, G10   arms, clauses, sham, setting,
                                            contrast; the kit registry
    rso_harness/claims.py         G11, G12   custody; claims as functions of
                                             facets
    rso_harness/ladder.py         EXPLORATORY: two key worlds (a second nested
                                  boundary; an unseen pair). Not gates
    rso_harness/meta.py           GM   every gate against its sound cases and
                                       mutants; the known escapes
    tests/test_harness.py         the tests
    run_harness.py                writes the receipt
    mutation_probe.py             changes the gates' logic one line at a time
                                  and asks whether the tests notice

## What the receipts say

21 gates. Each passes its registered sound cases (48) and rejects its
registered mutants (215) with the verdict registered for each: 108 FAIL, 78
BLOCKED, 22 UNQUALIFIED, 7 INDETERMINATE.

24 faults are known NOT to be caught, at least one in every gate. Each is run
and pinned by a test, so a passing harness is not read as covering it. The
list is not complete.

Mutation probe: 167 one-line changes to the gates' logic, in five sets. 165
could be carried over to this version; the tests notice 159. The 6 they do
not notice alter no verdict. This figure was taken after the tests were
extended to those changes, so it says only that those holes are closed.

## What it is worth

Three versions, three reads. Each version passed every case it held when it
was handed to a reader.

    version   sound   broken   what readers then found
    -------   -----   ------   ---------------------------------------------
    one         34       62    65 of the reader's 71 broken cases got
                               through; 22 of 25 logic changes unnoticed
    two         44      148    an unlisted passing fault in every gate;
                               34 of 44, 20 of 32, 26 of 36 unnoticed
    three       48      215    FINAL_READ_PLACEHOLDER

The honest measure of the tests is the first-sight figure, and it has been
bad every time it was taken.

## Limits

One author for the gates. Three reads by readers of the author's model
family. Four toy physics, one world, no noise. See section 12 of the
specification.
