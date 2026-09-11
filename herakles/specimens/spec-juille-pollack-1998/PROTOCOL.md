# spec-juille-pollack-1998: protocol, committed BEFORE transcription is trusted and BEFORE any run

Herakles, 2026-09-11. Backlog L-1 (the coevolved rule), L-3 (the ABK rule,
which this paper reprints), L-5 (which "Das rule" is which), X-4 (a second
lineage in the historical arm). Built from c8d576e41 on branch
herakles/comms-queue-2026-09-11.

## What is in hand

`original/gp98.pdf`, sha256 f3d00a00..., ORIGINAL_SPECIMEN, 9 pages, from
the author's laboratory site (Last-Modified 21 May 1999). Juille and
Pollack, "Coevolving the 'Ideal' Trainer: Application to the Discovery of
Cellular Automata Rules", Genetic Programming 1998 (Third Annual Conf.),
Morgan Kaufmann, pp. 519-527. Text layer at `derived/gp98_text.txt`; the
font is a Type-3 dvips font and the extraction splits digits with "/",
which is why every digit below is re-checked by execution.

## What the paper prints (PRIMARY_SOURCE_READ, page locators are text-line numbers in derived/gp98_text.txt)

Table 2 (lines 779-791) prints FIVE 128-bit lookup tables in binary,
16 groups of 8 bits, "trivial coding: the leftmost bit corresponds to the
output of the rule with input 0000000, the second bit to 0000001, ... the
rightmost to 1111111" (lines 657-661):

    Coevolution (1)   a NEW organism; coevolved rule, this paper
    Coevolution (2)   a NEW organism; coevolved rule, this paper
    Das rule          reprinted; which Das rule is the question L-5 asks
    ABK rule          reprinted; Andre, Bennett, Koza 1996 (backlog L-3)
    GKL rule          reprinted; derivable from its definition, so the
                      CALIBRATION MEMBER of this recovery

Table 1 (lines 444-453) prints performance, "+/- 0.001", at N = 149 /
599 / 999:

    Coevolution (1)   0.851  0.810  0.795
    Coevolution (2)   0.860  0.802  0.785
    Das rule          0.823  0.778  0.764
    ABK rule          0.824  0.764  0.730
    GKL rule          0.815  0.773  0.759

The paper's conventions where stated: rules coded on 128 bits (line
666-668), density-uniform initialisation of the rule population (line
670-671), search "similar to Mitchell et al. 1994". The performance
measurement convention (IC ensemble, horizon) is NOT restated in the
extracted text I have read so far; the C1-e conventions of the same task
family are used and named as an assumption (A1 below).

## The bit-order convention, and why GKL settles it

`herakles.evca.decode_table` uses "bit k from the left is index k", where
index k has the LEFTMOST neighbour as its most significant bit. The
paper's "trivial coding" reads the same way if its input strings are
written leftmost-neighbour-first. That is an ASSUMPTION until the
transcribed GKL table equals `evca.gkl_rule_table()` bit for bit; a
reversed reading would fail that equality on GKL (GKL is not
reflection-symmetric in this coding, which is what makes it a
calibration and not a tautology).

## Transcription

The 128 digits per rule are taken from the text layer, the "/" separators
stripped, and the 16 groups concatenated in printed order. The result is
stored as 32 hex digits in `derived/juille_pollack_1998_rule_tables.json`
with the binary string beside it. Standing rule from the 2026-09-03
recovery: a printed specimen is RECOVERED_SPECIMEN only after EXECUTION
reproduces a published figure, never on transcription alone.

## Assumptions

A1. Performance convention = C1-e's: ring, synchronous, steps = 2N,
    ICs i.i.d. Bernoulli(0.5) (the unbiased ensemble), at_T criterion,
    n_ics 10000 / 4000 / 2000 at N = 149 / 599 / 999.
A2. The Das rule of Table 2 is a specific 1994/1995 rule of the EvCA line.
    Whether it equals any of the three particle rules I hold (par,
    particle1, particle2) is TESTED, not assumed.

## Controls (base rule 3)

POSITIVE   GKL, transcribed, equals GKL, derived. Must hold; if it fails,
           STOP, because either the convention or the transcription is
           wrong and no other table can be trusted.
CHEAT      A deliberately mis-paired table (row 1 of Coevolution (1) with
           row 2 of Coevolution (2)) is scored at N = 149. It must score
           far below both parents (< 0.5). This is the transcription-
           hazard control from the 2026-09-03 recovery, repeated here so
           a pairing error could not pass as a rule.
NEGATIVE   `maj` (held) at 0.000 under at_T, already established; not
           re-run.

## Preregistered predictions

Q1. GKL transcribed == GKL derived, 128 of 128 bits.
Q2. The Das rule of Table 2 is NOT byte-identical to par, particle1 or
    particle2. (Bet, from Table 1: 0.823 at N = 149 against the held
    0.769 / 0.742 / 0.755.) If it IS identical to one of them, that is a
    finding about the two publications' performance figures, filed as
    such.
Q3. Under A1, with the C1-e decision rule (REPRODUCED iff |measured -
    published| <= z * SE, z from Bonferroni over 15 cells at family-wise
    0.05: 0.05/15 = 0.003333, z = 2.935; SE binomial from the observed
    proportion), at least 12 of 15 cells are REPRODUCED. Every DISCREPANT
    cell is reported with its interval and is a LEAD, not an error in
    either party. The conservatism of that band is as stated in C1-e s4:
    it carries only my sampling error, so it leans toward DISCREPANT.
Q4. The mis-paired cheat table scores below 0.5 at N = 149.
Q5. Coevolution (1) and (2) at N = 149 exceed every held EvCA-line
    genome's published P (the best held is GKL at 0.816). This is the
    paper's claim and it is checked under my implementation.

Kill / indeterminate branches:
  - Q1 fails: stop. Nothing else read.
  - Q3 below 12 of 15 with the failures concentrated in one rule: that
    rule's transcription is the first suspect; report per-rule.
  - Q3 below 12 of 15 with failures concentrated in one N: the horizon
    convention (A1) is the first suspect; a sensitivity arm at steps =
    ceil(2.2 N) may be run AFTER the primary result is committed, and is
    labelled as a sensitivity arm.

## Provenance classes to be assigned after the run

Coevolution (1), (2): RECOVERED_SPECIMEN if Q1 and their Q3 cells hold.
ABK rule: RECOVERED_SPECIMEN via a SECONDARY printing (this paper), with
the 1996 proceedings still the primary printing to confirm; the manifest
row says so.
Das rule: as ABK, plus the Q2 answer.
GKL: calibration only; already held.

## What this enables

X-4: the historical arm gains a second SEARCH PROCESS (coevolution with
resource sharing, Brandeis 1998) and, through the ABK reprint, a third
(genetic programming, Stanford 1996). Two of the three are evolved
organisms; that is what X-4 asked for. C3-hist can then carry two lineages
in the fields Archaeon named, once Vivarium has the genomes as organisms.
