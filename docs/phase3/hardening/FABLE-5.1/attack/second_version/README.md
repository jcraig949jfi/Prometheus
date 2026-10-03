# Reference harness v0 (FABLE-5.1 version of the Phase 3 hardening spec)

A conformance skeleton. It shows that each gate of
`../03_TEST_HARNESS_SPEC_FABLE.md` returns its registered answer on sound
cases and on cases broken on purpose. It runs on toy fixtures and on four
receipts that already existed. It qualifies no science.

    python -B -m unittest discover -v     59 tests, about 10 seconds
    python -B run_harness.py              rewrites RECEIPT_harness_v0.json
    python -B mutation_probe.py           about 3 minutes; rewrites
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

21 gates. Each passes its registered sound cases (44) and rejects its
registered mutants (148) with the verdict registered for each: 82 FAIL, 41
BLOCKED, 19 UNQUALIFIED, 6 INDETERMINATE.

Eleven gates have a fault they are known NOT to catch. Each such fault is run
and pinned by a test, so a passing harness is not read as covering it.

Mutation probe: 55 one-line changes to the gates' logic; the tests notice 54.
The one they do not notice changes a reason text and no verdict.

## What happened to the first version

The first version held 21 gates, 34 sound cases and 62 mutants, all written
by the author of the gates, and passed all of them. An adversarial reader
then wrote its own cases. Replayed from `../attack/` on a copy of the first
version:

    the reader's broken cases that passed (escapes) ........ 65 of 71
    the reader's sound cases that were rejected ............ 12 of 12
    the reader's one-line logic changes not noticed ........ 22 of 25

Most of the reader's cases are now registered here beside the author's. The
faults it showed that the gates still cannot catch are the known escapes.

## Limits

One author for the gates, one adversarial reader, one revision. Four toy
physics, one world, no noise. A second reader would find more. See section
13 of the specification.
