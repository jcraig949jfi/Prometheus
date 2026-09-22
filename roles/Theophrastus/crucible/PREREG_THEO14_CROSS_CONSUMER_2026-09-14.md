# THEO-14 -- cross-consumer re-derivation of Vivarium bench fossils (PREREGISTERED)

Currency: 2026-09-14. Committed BEFORE any bench fossil is re-derived.
Only a structure probe has been run (one row's key names; the counts
150/150 rows carry repeats + seed + accuracy_at_T + mask_digest_at_T).
No accuracy, digest or per-IC value of a bench row has been read.

## Question

Does THEO-SPEC-001's per-IC phenotype instrument (theophrastus/dissect.py),
validated only on fossils THIS seat's consumer produced, re-derive fossils
produced by a DIFFERENT consumer (the Vivarium daemon, builds before
2026-09-12) of a DIFFERENT producer's specs (Archaeon C3-2) bit-exactly?
This is the founding PREREG s8 cross-consumer question, answered from the
existing record instead of from a new queue row.

## Population

viv.research_experiment_queue, kind ca_density_v0, status completed:
150 rows (census 2026-09-14). Read-only. Rows with transform != "none" are
re-derived through the same wrapper transform path (vivarium/viv/
ca_density.apply_transform) so they are in scope, not excluded.

## Frozen predictions

P1  150/150 rows: recomputed accuracy_at_T and correct-mask digest equal
    the fossil's on EVERY repeat (instrument transports across consumers).
P2  CHEAT: seed + 7 on one bench row breaks the match.
P3  At n_cells=149, steps=320, [null] ensemble, NONE transform, the bench's
    per-IC success at fixed margin m agrees with this seat's founding
    curve for every genome present in BOTH (maj, GKL, exp, par): no
    0.01-m bin with |z| >= 3 (same test as round-2 H1).

## Outcome meanings

P1 pass            instrument transports; SPEC-001 TRANSPORT EVIDENCE gains
                   "another consumer's fossils, 150 rows"
P1 fail on k rows  preserve the rows and the first differing repeat; the
                   class of difference (seed derivation, wrapper version,
                   transform path) is the finding; SPEC-001's instrument
                   claim is narrowed to this seat's consumer
P2 not caught      the instrument is not validating; halt
P3 fail            bench and seat disagree on a phenotype at identical
                   coordinates: an engine/wrapper-version effect, reported
                   to Vivarium, never averaged away

## OUTCOMES (2026-09-14, after execution; the text above is unchanged)

Artifacts: crucible/theo14/THEO14_RESULT.json, per_ic_bench.jsonl (60,000
records), P2_CHEAT_CENSUS.json. (The run console crucible/theo14_console.log
is gitignored by the repo *.log rule and is local-only; the JSON is the row
record.)

P1  PASS as frozen: 150/150 bench rows, every repeat, accuracy_at_T and
    correct-mask digest equal (132 none, 6 x reflect / complement /
    reflect_complement). ELIGIBILITY ANNOTATION: 126 of 150 rows score
    exactly 0.0 on every repeat (all 120 C3-acq rows -- already reported
    in archaeon/docs/h0h5/C3_2_READOUT.md, not a new fact -- plus maj and
    6 others). On those rows an all-false mask matches for ANY seed, so
    they cannot discriminate. The informative count is 24 rows (9 none,
    15 transformed: 5 per symmetry; genomes exp, par, particle1,
    particle2, GKL x4 each + two constant rules x2).
P2  NOT CAUGHT as frozen. The frozen cheat row 81b3882e (C3-hist, maj,
    accuracies 0,0,0,0) is one of the 126 degenerate rows: "nothing could
    have fired". Per the outcome rule the run halted and the instrument
    was checked before any reading: the same seed+7 cheat on all 150 rows
    is caught on 24/24 non-degenerate rows and on 0/126 degenerate rows.
    DISPOSITION: the prereg defect is this seat's (no eligibility check
    on the cheat row; calibration ledger 2026-09-14). The instrument
    validates wherever validation is possible.
P3  PASS: GKL, exp, maj, par at N=149/320/[null]/none: no 0.01-m bin with
    |z| >= 3 (max |z| 1.66, 2.45, 0.0, 1.53; 400 bench ICs vs 1600 seat
    ICs per genome).
