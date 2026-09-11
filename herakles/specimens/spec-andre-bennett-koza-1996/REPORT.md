# spec-andre-bennett-koza-1996: Table 1 reproduced 4 of 4 under the paper's own convention; the horizon does not matter for these rules

Herakles, 2026-09-11. Rows: `derived/reproduction_results.json` (same
commit). Runner: `derived/run_reproduction.py`. Protocol in PROTOCOL.md
(commit 7901a1e03; the order-of-events note there stands). Built from
c8d576e41 in the herakles-comms-queue worktree. Runtime 83 s.

Convention: the paper's. N = 149, ICs i.i.d. Bernoulli(0.5), n = 10000,
horizon 600, at_T. z = 2.498 (Bonferroni over 4 cells). Sensitivity arm
at horizon 298 on the SAME ICs.

    rule       published   cases   measured@600  |diff|/SE  decision    measured@298  delta
    gkl        0.81600     10^6    0.8145        0.39       REPRODUCED  0.8144        -0.0001
    davis1995  0.81800     10^6    0.8205        0.65       REPRODUCED  0.8205        +0.0000
    das1995    0.82178     10^7    0.8235        0.45       REPRODUCED  0.8235        +0.0000
    abk_gp     0.82326     10^7    0.8243        0.27       REPRODUCED  0.8243        +0.0000

    R1  HOLDS   4 of 4 (prediction >= 3).
    R2  not tested, as preregistered: the printed gaps (0.0015 to 0.003)
                are below one SE at n = 10000. Observed order at 600:
                abk_gp > das1995 > davis1995 > gkl, which happens to be
                the paper's; it is NOT evidence for it at this n.
    R3  HOLDS   every rule within 0.01 between horizons 298 and 600; in
                fact within 0.0001. These four rules have relaxed by 2N.
                The horizon-convention caveat on the 2N cells in
                spec-juille-pollack-1998 is therefore lifted for gkl,
                das1995 and abk_gp (the only ones that appear in both).

## Provenance classes assigned

    abk_gp      RECOVERED_SPECIMEN from the ORIGINAL printing, cross-
                confirmed by the 1998 reprint, reproduced under both the
                paper's convention (this file) and the 2N convention
                (spec-juille-pollack-1998): 0.8243 against 82.326%.
    das1995     RECOVERED_SPECIMEN, two printings, reproduced under both
                conventions.
    davis1995   RECOVERED_SPECIMEN: one printing, but its cell reproduces
                (0.8205 against 81.8%) and it shares the GKL-calibrated
                transcription of the same table, so the kill branch for
                a Davis-only failure did not fire.

## What this enables

The historical arm now holds nine radius-3 organisms with published
figures reproduced (maj, GKL, exp, par, particle1, particle2, das1995,
davis1995, abk_gp) plus two coevolved ones from the 1998 paper, and
CRITERIA.md records three horizon conventions (2N, 600, ceil(N/2)),
with a measurement that the first two coincide for the rules that were
compared under both.

## What would falsify this

An independent transcription of the 1996 Table 2 (for Davis 1995, the
only single-printing rule) that differs in any bit; a Davis cell at a
second seed outside the band.

## What should stop

No further compute on these four. The remaining value in this paper is
archival: it names a Davis 1995 rule whose source is not cited in the
extracted text and which I have not seen printed anywhere else, and
it lists the 1994 GA rule at 76.9% without printing its table (L-5).
