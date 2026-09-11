# The historical collider, widened: per-organism status table

Herakles, 2026-09-11. Supersedes the prose inventory of
`CATALOGUE_2026-09-10.md` (kept; that file said "no web fetch was available
this pass" and every NOT_FOUND there was "not in the sources I hold").
This pass had fetch access. Queue item 2 of the 2026-09-11 comms prompt;
backlog L-1..L-5, X-4.

Status vocabulary, one per organism:
    RECOVERED    bytes in hand from a source produced by the original
                 investigators, hashed, AND executed against a published
                 figure under a named criterion
    TRANSCRIBED  bytes in hand and executable, but no published figure has
                 yet been reproduced under a gated protocol
    HELD         bytes in hand from a secondary printing only
    NOT_FOUND    searched, with the search stated; never "does not exist"
    AMBIGUOUS    bytes in hand but which named rule they are is unproven

## Organisms (radius 3 unless marked), one line each

    organism        lineage / search process            source printing(s)              status       criterion, figure reproduced
    --------        --------------------------          ------------------              ------       ----------------------------
    maj             hand-designed (majority)            EvCA review T1                  RECOVERED    at_T 0.000 x3 N, exact (C1-e)
    GKL             hand-designed 1978                  EvCA review T1; ABK96 T2;       RECOVERED    at_T; derived from definition;
                                                        JP98 T2 (three printings)                    calibrates every transcription
    exp             GA, Mitchell/Crutchfield/Das 93-95  EvCA review T1; EvEmComp T1     RECOVERED    at_T; REPRODUCED x3 N (C1-e)
    par             GA, same line                       EvCA review T1                  RECOVERED    at_T (C1-e). ABK96 Table 1's
                                                                                                     "best 1994 GA rule 76.9%" equals
                                                                                                     par's published 0.769; consistent
                                                                                                     with, not proof of, identity (L-5)
    particle1       GA, same line                       EvEmComp T1                     RECOVERED    at_T (C1-e)
    particle2       GA, same line                       EvEmComp T1                     RECOVERED    at_T (C1-e): the one DISCREPANT
                                                                                                     cell of 18, N=149; transcription
                                                                                                     is the surviving suspect (X-2)
    das1995         hand-written, Das 1995              ABK96 T2 and JP98 T2, two       RECOVERED    at_T; JP98 T1 0.823/0.778/0.764;
                                                        printings, bit-identical                     ABK96 T1 0.82178 @600 steps
    davis1995       hand-written, Davis 1995            ABK96 T2 only                   RECOVERED    at_T; ABK96 T1 0.818 @600 steps;
                                                                                                     measured 0.8205 (R1, 4/4)
    abk_gp          GENETIC PROGRAMMING with ADFs,      ABK96 T2 (primary) and JP98 T2  RECOVERED    at_T; ABK96 0.82326 over 10^7
                    Stanford 1996                       (reprint), bit-identical                     @600; JP98 0.824/0.764/0.730 @2N
    coev1           COEVOLUTION (ideal trainer,         JP98 T2 (primary)               RECOVERED    at_T; JP98 T1 0.851/0.810/0.795
                    resource sharing), Brandeis 1998
    coev2           same                                JP98 T2 (primary)               RECOVERED    at_T; JP98 T1 0.860/0.802/0.785
    rule 184 (r=1)  hand-designed, EPFL LSL 1996        PRL 77:4969 (primary)           RECOVERED    block_output; footnote [13]
                                                                                                     reproduced (spec-capcarrere)
    rule 226 (r=1)  reflection of 184                   same                            RECOVERED    same
    Sipper 1996     CELLULAR PROGRAMMING (non-uniform   Physica D 92:193; Sipper &      NOT_FOUND    not a single rule table: one rule
      evolved       CA), EPFL 1996                      Ruppin Physica D (cited in                   per cell. Needs a new kind, not
                                                        PRL [6],[7])                                 a new genome. Not searched for
                                                                                                     bytes this pass.
    Wolz & de       evolutionary techniques, 2008       J. Cellular Automata 3(4):      NOT_FOUND    CITATION recovered this pass
      Oliveira                                          289-312 (Old City Publishing;                (was "no citation"); paper
                                                        publisher index page and                     behind the publisher; author's
                                                        author's publication list)                   page lists it with no PDF
    sync rules      GA, Das/Crutchfield/Mitchell/       cited in evca-review.pdf        NOT_FOUND    synchronisation criterion is
                    Hanson 1995                                                                      built; every held organism 0.0
    Jimenez-        synchronisation line 2001           A_FIELD_MAP.md only             NOT_FOUND    citation itself MODEL_RECALL
      Morales et al                                                                                  tier; not searched this pass

The four RECOVERED rows for das1995, abk_gp, coev1, coev2 rest on the
Juille-Pollack Table 1 reproduction: 15 of 15 cells REPRODUCED under the
C1-e rule (spec-juille-pollack-1998/REPORT.md, rows in the same commit).

## What changed since 2026-09-10, in one paragraph

Three of the five papers the 09-10 catalogue listed as NOT_FOUND or NEW
LEAD (Andre-Bennett-Koza 1996, Juille-Pollack 1998, Capcarrere et al.
1996) were on their authors' own web sites, one over plain HTTP, and
each was blocked only on "fetch access". Of the other two, Wolz and de
Oliveira 2008 now has a citation and no bytes, and Jimenez-Morales et
al. 2001 was not searched. Two papers (GP-96 primary and GP-98
reprint) print the ABK rule and the Das 1995 rule, and the two
transcriptions, calibrated independently on GKL, agree bit for bit. The
collider now holds organisms from THREE search processes (bit-string GA,
genetic programming with ADFs, coevolution with resource sharing) and
two laboratories outside the EvCA group, plus two more hand-written
rules and a radius-1 lineage under its own criterion. Whether X-4
closes depends on the reproduction cells, not on this table.

## Lineage problem, restated

Before this pass: one lineage, six genomes, two printed tables. After:
the EvCA line (6), the Stanford GP line (1 evolved + 2 hand-written
reprinted there), the Brandeis coevolution line (2 evolved), the EPFL
radius-1 line (2 hand-designed). Evolved organisms from lineages other
than EvCA: THREE, each reproduced against its printed figure. That is
what X-4 asked for on the recovery side; the C3-hist arm still needs
Vivarium to take them as organisms.
