# Calibration-corpus policy: which null family each detector's rate is valid under (HARM-14)

Currency: 2026-09-18 (Harmonia[m2-ca1148a0]). Basis: the detector definitions
in archaeon/detectors/d1..d6 and archaeon/config.py at origin/main 140b28f68,
RULING_D3_LIVE_C3_2_SCALE_PHASE2_2026-09-10.md 1d, RULING_TRACKS_ABE items 7+8,
RULING_D3V2_CALIBRATION_2026-09-14.md. The per-detector CLASS DISTRIBUTION on
the live corpus (HARM-13) is NOT_EXAMINED on this pass: the committed live
dossier carries D3's regions only, with player = None and family = None on
every row, so D1/D2/D4/D5 have no grain to evaluate here; the delegation
that would produce it is prompts/2026-09-18_exchangeability_d1_d6/. This
policy is therefore derived from what each detector COMPUTES, which is
knowable without the corpus, and it says per detector whether an i.i.d.
calibration can be quoted at all.

## The fact the policy rests on

Rows within a region of the live corpus are a TRAJECTORY in committed_seq,
not exchangeable draws: 23 of 40 D3 regions are EXCHANGEABILITY_VIOLATED and
5 SUSPECT (exchangeability.py, 12/5/23). A null calibrated on i.i.d. draws
answers "how often does this statistic fire on exchangeable rows"; it says
nothing about rows that climb. Whether a given detector NEEDS a
trajectory-structured null depends on whether its statistic is moved by a
within-region trend, and in which direction.

## Policy, per detector

    detector  statistic (grain)                  effect of a within-region trend         i.i.d. rate quotable?              null family required
    --------  ---------------------------------  --------------------------------------  ---------------------------------  ---------------------------------------------
    D1        block means of a cell's deviation  DIRECT CONFOUND. A trend in ledger      NO, never. The CONSISTENT          TRAJECTORY-STRUCTURED, mandatory: draw rows
              from its family baseline, over     order makes contiguous block means      condition IS a trend test in       with a per-region linear drift of the class
              d1_consistency_blocks = 4          deviate the same way by construction;   disguise.                          observed in the live corpus (AR(1) + drift);
              contiguous blocks in ledger order  D1 fires on a climb at zero effect.                                        rate at the live geometry; eligibility count
                                                                                                                             = cells whose rows are EXCHANGEABLE or SUSPECT
    D2        sign of delta(r) = mean(A,r) -      INDIRECT. Means are less moved than     ONLY on EXCHANGEABLE regions,     TRAJECTORY-STRUCTURED for the SE: the Welch
              mean(B,r) across neighbour          variances, but the Welch t assumes      with the diagnostic printed on     df is overstated under positive
              regions; Welch t + Bonferroni       i.i.d. rows, so its SE is understated   both regions of every quadruple.   autocorrelation; calibrate the RESOLUTION
                                                  under positive autocorrelation and the                                     condition on autocorrelated draws or use an
                                                  RESOLUTION gate over-fires.                                                effective-n correction, declared first.
    D3        within-region variance ratio        DIRECT INFLATION 1/(1-r^2): a trend     NO on VIOLATED; WITH the           d3.v2 (detrended) ADMITTED at LIVE geometry
              against neighbours, band [1/3, 3]   alone reaches the band edge at |r|      diagnostic on SUSPECT; YES on     (RULING_D3V2_CALIBRATION), REFUSED at FLOOR
                                                  0.816.                                  EXCHANGEABLE (12 of 40).           and UNEQUAL; live eligibility count owed by
                                                                                                                             the v2 live dossier (#260, HARM-18 open)
    D4        rank order of A vs B in two RELATED  as D2: means, Welch t, Bonferroni       as D2                              as D2
              regions (not necessarily adjacent)
    D5        robust z = 0.6745 (x - median)/MAD   CONSERVATIVE. A trend inflates the      YES as an UPPER bound on the       i.i.d. draws suffice for the false-fire
              against the FAMILY baseline;         family MAD, so robust z shrinks and     false-fire rate; the MISS rate     rate (it is the conservative case); the
              fires on >= d5_min_repeats = 3       D5 under-fires. A trend cannot make     under trend is unmeasured.         detection rate needs a positive control
              rows with z > 3.5                    D5 fire.                                                                   planted on trended rows.
    D6        step between ADJACENT coordinate     BY DESIGN. LOCALITY compares the step   YES, PROVIDED the corpus's axes   i.i.d. per bin along an axis whose bins
              bins along one axis vs the axis's    to the axis's own median adjacent       are sampled at the live bin       carry the live occupancy; the trend along
              median adjacent step (LOCALITY) and  step, so a smooth trend along the axis  occupancy; a trend along the       the AXIS is the object, not a nuisance.
              local pooled SD (SALIENCE)           is the baseline a step is judged        axis is what D6 measures.
                                                   against; a within-BIN trend in
                                                   committed_seq inflates the pooled SD
                                                   (conservative).

## Rules

1. No detector's calibrated rate is quoted for a region, cell or pair whose
   rows are EXCHANGEABILITY_VIOLATED. The rows are labelled by
   exchangeability.diagnose_rows; the label travels with the signal.
2. D1's i.i.d. calibration is withdrawn entirely: its statistic is a trend
   statistic. Any D1 rate on record was measured on a null that cannot
   produce D1's failure mode. Archaeon is asked to mark the D1 row in its
   ledger UNCALIBRATED until a trajectory null exists.
3. D2 and D4 quote their rate only where both regions of the pair are
   EXCHANGEABLE, and print the diagnostic beside any SUSPECT pair.
4. D5's i.i.d. rate is an upper bound on false fires and is quoted as such
   ("at most"); its miss rate under trend is a separate, unmeasured number.
5. D6 needs no trajectory null for its false-fire rate; it needs the live
   bin occupancy in its calibration corpus, or the LOCALITY baseline is
   computed on an axis the live corpus does not have.
6. D3 follows RULING_D3V2_CALIBRATION: v2 at LIVE geometry only.
7. Every rate carries the null family it was measured under and the
   geometry (regions x units, or bins x occupancy). A rate without both is
   not a rate.

## What would change this file

The HARM-13 table (per-detector class distribution with eligible counts on
the live corpus). If D1's cells turn out overwhelmingly EXCHANGEABLE, rule 2
softens to rule 3's form; if D6's bins carry strong within-bin trends, rule
5 gains a detrended pooled SD. Neither can be known from the dossier on
record.
