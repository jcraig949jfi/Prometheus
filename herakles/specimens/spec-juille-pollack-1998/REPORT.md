# spec-juille-pollack-1998: Table 1 reproduced, 15 of 15 cells; four organisms RECOVERED

Herakles, 2026-09-11. Rows: `derived/reproduction_results.json` (same
commit). Runner: `derived/run_reproduction.py`. Protocol 7379a5634,
committed before transcription. Tables: `derived/juille_pollack_1998_
rule_tables.json` (transcribe.py, commit 7901a1e03). Built from c8d576e41
in the herakles-comms-queue worktree, branch herakles/comms-queue-2026-09-11.
Runtime 597 s.

Conventions (assumption A1 = C1-e's): ring, synchronous, steps = 2N, ICs
i.i.d. Bernoulli(0.5), at_T, n_ics 10000 / 4000 / 2000, one seed per
cell derived from 20260911. Decision: REPRODUCED iff |measured -
published| <= 2.935 SE (Bonferroni, 15 cells, family-wise 0.05); the
band carries my sampling error only, so it leans toward DISCREPANT.

## The fifteen cells

    rule     N   n_ics  published  measured    diff   |diff|/SE  decision
    coev1  149  10000     0.851     0.8548  +0.0038    1.08     REPRODUCED
    coev2  149  10000     0.860     0.8574  -0.0026    0.74     REPRODUCED
    das    149  10000     0.823     0.8281  +0.0051    1.35     REPRODUCED
    abk    149  10000     0.824     0.8232  -0.0008    0.21     REPRODUCED
    gkl    149  10000     0.815     0.8190  +0.0040    1.04     REPRODUCED
    coev1  599   4000     0.810     0.7925  -0.0175    2.73     REPRODUCED
    coev2  599   4000     0.802     0.8045  +0.0025    0.40     REPRODUCED
    das    599   4000     0.778     0.7808  +0.0028    0.42     REPRODUCED
    abk    599   4000     0.764     0.7712  +0.0072    1.09     REPRODUCED
    gkl    599   4000     0.773     0.7692  -0.0038    0.56     REPRODUCED
    coev1  999   2000     0.795     0.7915  -0.0035    0.39     REPRODUCED
    coev2  999   2000     0.785     0.7785  -0.0065    0.70     REPRODUCED
    das    999   2000     0.764     0.7505  -0.0135    1.40     REPRODUCED
    abk    999   2000     0.730     0.7400  +0.0100    1.02     REPRODUCED
    gkl    999   2000     0.759     0.7715  +0.0125    1.33     REPRODUCED

## Predictions, as the predicates returned them

    Q1  HOLDS   GKL transcribed == GKL derived, 128/128 (transcribe.py).
    Q2  HOLDS   the Das rule equals none of par, particle1, particle2.
    Q3  HOLDS   15 of 15 REPRODUCED (prediction was >= 12).
    Q4  HOLDS   the mis-paired cheat table (coev1 bits 0-63 + coev2 bits
                64-127) scores 0.440 at N = 149, below both parents
                (0.855, 0.857) and below the 0.5 bar.
    Q5  HOLDS   coev1 0.8548 and coev2 0.8574 at N = 149 exceed the best
                held EvCA-line published P (GKL 0.816).

The one cell worth a sentence: coev1 at N = 599 sits 2.73 SE below its
published 0.810, inside the band but the largest deviation of the
fifteen. Under the C1-e rule that is REPRODUCED and nothing more is
read; it is recorded so that a second seed at N = 599, if ever run, has
a number to compare against.

## Provenance classes assigned

    coev1, coev2   RECOVERED_SPECIMEN. Original printing, one
                   transcription, GKL-calibrated, three cells each
                   reproduced.
    abk            RECOVERED_SPECIMEN. Two printings (1996 primary, this
                   reprint), two independent transcriptions, bit-identical;
                   three cells reproduced here under the 2N convention and
                   the ABK-convention run is in spec-andre-bennett-koza-1996.
    das1995        RECOVERED_SPECIMEN, two printings likewise. It is the
                   1995 HAND-WRITTEN Das rule (ABK 1996 Table 1 says so),
                   which advances L-5: the "Das rule" other papers reprint
                   is not the 1994 GA rule.
    gkl            held already; calibration member only.

## What this enables

X-4 is now answerable in the affirmative on the recovery side: the
historical arm holds EVOLVED organisms from three search processes
(bit-string GA 1993-95, genetic programming with ADFs 1996, coevolution
with resource sharing 1998), each reproduced against its own printed
figure. The C3-hist arm with a second lineage needs Vivarium to take
these four genomes as organisms of the ca_density kind; that is a
handover, not a run, and it is the next executable action on X-4.

## What would falsify this

- A second seed at N = 599 for coev1 landing again more than 2.7 SE
  below 0.810 would make that cell a lead about the convention (the
  paper's horizon is not restated in its text; A1 is an assumption).
- The 1998 proceedings printing differing from the author-site PDF.
  The author-site file is dated 1999-05-21 and is the only copy held.

## What should stop

No further compute on these five rules under the 2N convention. The
band clause of the Bonferroni rule was never near firing (largest
|diff|/SE 2.73 against 2.935), so a tighter replication buys nothing
the next question needs.
