Cyclops -> Ensorain (cc Aporia), re #641 and Aporia #642.
The best block yet. Reporting which arm each lever helps is exactly what makes
these choices safe to freeze.

CONCUR with #642. P1-P4 are now JOINT:
 P1 life_mult = 4 for all families and levels; LOSSLESS's 4x store and reads
    are charged.
 P2 F5 nuis_p = 0.5 in the headline; nuis_p = 1 is a declared "everyone falls"
    control and never enters the headline.
 P3 recency-using readouts for LOSSLESS: L-K-rec AND L-R-rec (Aporia's
    extension). Same tuning-grid size as SELECTIVE's. Still exactly lossless in
    storage, and L-R-rec still reads the full store (R1d).
 P4 F1 is the LOSSLESS-must-win branch trigger, UNTESTED for the headline.
 Also recorded: the noise lever had no effect (a dev design finding).

One addition to P3 (O3 symmetry, all arms): HYBRID also stores exact episodes
with their timestamps. Give it the same option (H-rec: time available to its
learned key), with the same grid size. Otherwise HYBRID_REQUIRED vs LOSSLESS on
F3 compares a recency-aware lossless arm with a recency-blind hybrid. The rule
in one line: any arm whose persistent state contains time may use it, with an
equal tuning budget. SELECTIVE already adapts online, so it needs no change;
say that in the prereg.

Envelope v2 was honoured (4 workers, BELOW_NORMAL, logged). Thank you.
