# Hestia Audit 1 -- frozen predictions for the designed decisive tests

Currency: 2026-10-07. Committed BEFORE any of these tests has run (none
had, as of origin/main 3fed30ac9). Purpose: calibration of the auditor,
scored in calibration/LEDGER.md as results land (HESTIA-18). These are a
model's subjective probabilities. They are not gates, not verdicts, and
they bind no seat's design. A test whose final design differs materially
from the one named here is scored as "design changed", not as a hit or a
miss.

P = probability the PASS / SEED branch occurs, as worded in REPORT.md.

    #   test (REPORT section)                                   P(pass)
    1   Aether TEST-4, all three conditions pass (3.1)            0.15
    2   Primordial X-TASK-GATE, >= 1/96 certified de novo
        cue-reading lineage with the CT_UA control passing (3.2)  0.05
    3   Odysseus three-factor plasticity beats the frozen
        reservoir by >= 10 pp on >= 6/8 seeds (3.3)               0.30
    4   Ananke FLIP: a new arm >= 6/32, traced to the duplicated
        module (3.4)                                              0.30
        (P(kill: both new arms <= 1/32) = 0.45)
    5   Moonshot pilot: plastic arm >= 8/64, the others <= 2/64,
        and ablation returns it to the null (3.5)                 0.25
    6   sigma_kernel race test finds >= 1 double-spend in 1,000
        trials before the fix (3.6)                               0.75
    7   Cosmos C3 certificate transfers to 3 engines with no
        planted-control misclassification in 5 seeds (3.7)        0.60
    8   Ensorain hidden-state assay: a stateful candidate beats
        the window statistic by >= 0.10 of the gap in >= 2
        families (3.8)                                            0.50
    9   Ludus m-knob: no size-<=8 observation-only rule keeps
        >= 95% at every m >= 1 (i.e. the worlds demand memory) (3.9) 0.80
    10  z80atlas COND_ONE with stepping stone: >= 3/240 (3.10)    0.45
    11  Ares parity: k = 2 in >= 5/10 (3.11)                      0.40
    12  Crius: SMOOTH >= 3/9 with ROUGH 0/9 (3.12)                0.35
    13  SFE typed W2_K2: full-solve lower bound >= 0.25 over
        >= 30 seeds (3.13)                                        0.40
    14  Nyx typed organs separate from random primitives with
        ablation removing the gain (3.14)                         0.25
    15  Aphrodite R8 typed + MDL: gain over pristine (p < 0.05)
        with abstraction depth > 1 in > 10% of seeds (3.15)       0.25
    16  incubation M1/M0 acquisition-cost CI upper bound < 0.5
        with a transform building on another (3.16)               0.30
    17  alien_circuitry table-free invariants recover >= 95% of
        pruning on held-out types (3.17)                          0.20
    18  Theseus planted-structure test: some ruler AUC >= 0.75
        (3.19)                                                    0.45
    19  Tyche parity-k: some arm solves k = 3 in >= 5/10 (3.20)   0.45
    20  Herakles particle elites give >= 1.5x speedup (3.21)      0.30
    21  Forge library learning: >= 1 learned abstraction survives
        knockout after 5 cycles (3.22)                            0.45

Ladder-level (REPORT Part 5), if the ladder is run as specified:
    L1  some substrate reaches R2 at >= 5/32 by ANY escape         0.60
    L2  ... by escape (b) promotion/modularity specifically       0.40
    L3  ... by escape (c) plasticity specifically                 0.35
    L4  some substrate reaches R4 (reuse of a promoted unit)      0.20
    L5  nothing reaches R2 anywhere                               0.40

Bias statement: these are probably too pessimistic for tests that add a
designed mechanism (because designed mechanisms usually work on toy
tasks) and too optimistic for de novo tests. The ledger will show which.
