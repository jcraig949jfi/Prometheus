# spec-andre-bennett-koza-1996: what was done before this file, and the protocol for what follows

Herakles, 2026-09-11. Backlog L-3. Built from c8d576e41 on branch
herakles/comms-queue-2026-09-11.

## Order of events, stated because it is not the ideal order

The Juille-Pollack protocol (spec-juille-pollack-1998/PROTOCOL.md, commit
7379a5634) was committed first and covers the ABK rule as a REPRINT. The
1996 primary printing was then found on the author's site, downloaded,
and its Table 2 transcribed and cross-checked BEFORE this file was
committed. The transcription and cross-check are not a gated measurement
(no threshold, no number read against a prediction other than the
already-preregistered GKL calibration), so nothing was chosen after
seeing a result. But the honest order is: specimen, transcription,
cross-check, then this protocol. The gated run below has NOT started.

## What is in hand

`original/gp1996gkl.pdf`, sha256 23a07b06..., ORIGINAL_SPECIMEN, 11
pages, from genetic-programming.com (Last-Modified 18 Nov 2006). Andre,
Bennett, Koza, "Discovery by Genetic Programming of a Cellular Automata
Rule that is Better than any Known Rule for the Majority Classification
Problem", GP-96 (First Annual Conf.), MIT Press, pp. 3-11. Text layer at
`derived/gp1996gkl_text.txt`.

## What the paper prints (PRIMARY_SOURCE_READ; line numbers in the text layer)

Table 2 (lines 312-328), "in truth table order from 0000000 to 1111111",
four 128-bit tables in binary: GKL 1978, Davis 1995 (human-written),
Das (1995) (human-written), and the GP rule of this paper.

Table 1 (lines 93-106), out-of-sample accuracy at N = 149:
    Das/Mitchell/Crutchfield 1994 best GA rule   76.9%    10^6 cases
    GKL 1978                                     81.6%    10^6
    Davis 1995                                   81.8%    10^6
    Das 1995                                     82.178%  10^7
    GP rule (this paper)                         82.326%  10^7

Conventions (lines 343-350): ICs "created randomly, with no bias (0 and 1
each have an independent 50% probability)", so i.i.d. Bernoulli(0.5);
correct iff "the system relaxes to the correct configuration after 600
time steps". Horizon 600 at N = 149, NOT 2N = 298. This is the third
horizon convention now recorded in this family (EvCA line "about 2N",
Capcarrere ceil(N/2), ABK 600).

## Done before this file: transcription and cross-check (derived/transcribe.py)

- GKL transcribed from ABK Table 2 == GKL derived from its definition,
  128 of 128 bits. The 1996 printing's bit order is therefore the same
  as `evca.decode_table`'s.
- ABK GP rule (1996 printing) == "ABK rule" (Juille-Pollack 1998
  reprint), 128 of 128 bits. Two printings, two independent
  transcriptions, each calibrated on GKL, agree.
- Das (1995) (1996 printing) == "Das rule" (1998 reprint), 128 of 128.
- Davis 1995 appears in the 1996 printing only.
- None of Davis 1995, Das 1995, ABK GP equals any held genome.

## Preregistered predictions for the gated run (NOT yet run)

Configuration: N = 149, ICs i.i.d. Bernoulli(0.5), n = 10000, seed
20260911 + 2000 + rule index, horizon 600 (the paper's), at_T criterion.
Four rules: gkl, davis1995, das1995, abk_gp. Decision rule as C1-e:
REPRODUCED iff |measured - published| <= z * SE, Bonferroni over 4 cells
at family-wise 0.05: z = 2.498. Published figures carry their own
sampling error (SE 0.0004 at 10^6, 0.0001 at 10^7), negligible next to
mine (0.0038 at n = 10000), so the band is essentially mine alone.

R1. At least 3 of 4 cells REPRODUCED at horizon 600.
R2. The ranking abk_gp > das1995 > davis1995 > gkl of Table 1 is NOT
    resolvable at n = 10000 (the gaps are 0.0015 to 0.003, below one
    SE), so it is NOT tested; stating this in advance so that an
    observed ordering is not read as confirmation or refutation.
R3. Sensitivity: the same four rules at horizon 298 (2N). Prediction:
    every rule's accuracy at 298 is within 0.01 of its accuracy at 600
    (these rules relax fast). If a rule differs by more than 0.01, the
    horizon convention matters for that rule and the C1-e-convention
    cells in spec-juille-pollack-1998 carry that caveat.

Kill branches: R1 fails with the failing cell being davis1995 only:
first suspect is the Davis transcription, which has no cross-printing;
report and hold the Davis rule at TRANSCRIBED, not RECOVERED. R1 fails
on abk_gp or das1995: those have two agreeing printings, so the suspect
is the convention, and the sensitivity arm is read for it.

## Provenance classes after the run

abk_gp: RECOVERED_SPECIMEN from the ORIGINAL printing, cross-confirmed.
das1995: RECOVERED_SPECIMEN, two printings; and L-5 is advanced: the
"Das rule" of both 1996 and 1998 is the 1995 HAND-WRITTEN Das rule, not
a GA-evolved one; and ABK Table 1's 76.9% for the 1994 GA rule matches
the held `par`'s published 0.769, which is consistent with `par` being
that rule and is NOT proof of it (a figure is not a table).
davis1995: RECOVERED_SPECIMEN only if R1 holds on it; else TRANSCRIBED.
