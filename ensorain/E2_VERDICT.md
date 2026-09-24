# ENSORAIN E2 "STRUCTURE DISCOVERY" -- verdict

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Rows ship in this
commit: ensorain/runs/e2_confirm.jsonl (4,800 lives: 4 families x 10 arms
x 60 instances x 2 organism seeds, sets A and B), e2_score.json,
e2_score_stdout.txt. Scorer ensorain/e2/score.py frozen at 0ab17639c.
Preregistration PREREG_E2.md (efbf950af) + part 2 (edb67bd12, OUTER
0ab17639c).

## 1. Verdict under the frozen rule

    INDETERMINATE (controls)

The failing control is CHT's chance band: BLIND1 identified the correct
structure in 33/360 structured lives (0.092) vs the band [0.034, 0.084]
around 1/17. PC passed (ORACLE_H held-out R^2 0.91-0.997 in every family
and set), NEG passed (no arm above NOMEM in W_NONE), the smuggler was
refused. Post-verdict diagnostic (ensorain/e2/blind_sim.py, NOT a gate):
the identical draw procedure on 1,200 fresh seeds gives 0.060 (TT 0.080,
MAT 0.055, CP 0.045) vs 0.0588 -- the confirmatory excess (TT 15/120,
~3 SE) was a chance fluctuation, not information reaching a blind arm.
The rule is not re-read; the verdict stays INDETERMINATE.

## 2. The substantive gates fail regardless -- decisively

G_ID (SD correct-structure rate; gate >= 0.70 per structured family,
>= 0.50 NONE; sets A / B):
    TT    0.20 / 0.15      MAT   0.52 / 0.43
    CP    0.27 / 0.38      NONE  0.93 / 0.98  (the only pass)
G_EFF (SD vs best blind, >10% with CI): passes in 1 of 6 cells (B_CP).
In W_MAT the fixed OUTER partition (a coin flip that is right 1/3 of the
time) beats SD in both sets (EFF 4.72 / 5.45 vs 2.27 / -1.32).

Recommendation: CLOSE (B) the structure-discovery claim at this scale.
The answer to "can an organism discover how its world wants to be
factorized, from experience, within this bounded economy?" is NO for
cross-family and mode-order discovery, and it is no for every in-life
mechanism tried, not only SD.

## 3. Failure shapes (what was measured)

S1. Mode order is not discoverable from the discovery budget. Best TT
    identification by any in-life arm: MI 0.32 / 0.27 (a cheap heuristic,
    no model fits) > EXHAUSTIVE 0.27 / 0.25 > SD 0.20 / 0.15 > GREEDY
    0.10 / 0.02. RANDPERM 0.05 / 0.05 (chance 1/12 within TT).
S2. Family confusion TT <-> CP. In CP worlds SD committed to TT 73/120
    times (CP 39/120): a TT(3,3,3) approximates a CP-4 field about as well
    as the CP model does on 384 samples, so validation cannot separate
    them. In TT worlds SD chose TT 58/120, LR 28, NONE 21, CP 13.
S3. Within-family selection DOES work. LRSEL (3 matrix partitions) picks
    the right partition 0.75 / 0.67 in W_MAT and earns EFF 14.7 / 14.4
    (ORACLE_H 20.3 / 22.0). The difficulty scales with the hypothesis
    space: 3-way works, 17-way does not at this data budget.
S4. "No structure" IS detected: SD picks NONE 0.93 / 0.98 in W_NONE,
    GREEDY 1.00, EXHAUSTIVE 0.98 -- but paying ~5-8M discovery units to
    learn that costs more energy than it saves (EFF -22 / -38 vs NOMEM 0).
S5. "Increasingly useful" holds only partway: SD's median validation MSE
    falls round by round (TT 0.83 -> 0.65 over rounds 0-4; CP 0.72 ->
    0.32) and then RISES at the last doubling (TT 0.75, CP 0.58) -- the
    light-ridge from-scratch fit overfits 384 samples at high sweeps, so
    the final survivor is chosen on an overfit score.
S6. The discovery budget, not only the mechanism, binds: even the
    CORRECT hypothesis fitted from scratch on the 512-sample buffer reaches
    held-out R^2 of only 0.90 (TT), 0.79 (MAT), 0.44 (CP) (part 2 s2).
    Selecting among 17 models whose best member is that uncertain is
    unreliable by construction. A larger buffer is the one obvious lever;
    it is the same move as E1.5's "give it more memory", and it would not
    obviously resolve S2.

## 4. Qualifier and the TEXTBOOK finding

QUALIFIER = TEXTBOOK: SD beats no simple in-life search in any cell. The
best simple search per family is MI (TT), LRSEL (MAT), MI/EXHAUSTIVE (CP).
Successive halving -- the "temporarily test alternative decompositions"
organism -- adds nothing over exhaustive or heuristic selection here, and
is worse than a no-fit MI heuristic at ordering TT modes.

## 5. Seat predictions scored

    P1 PC passes; CP the risk           RIGHT on PC; CP passed (0.91/0.94)
    P2 SD G_ID: TT .6 MAT .7 CP .4      WRONG direction on TT/MAT (0.15-0.52)
       NONE >= .5 (p .5)                RIGHT (0.93 / 0.98)
    P3 G_EFF passes where G_ID does     VACUOUS (G_ID failed)
    P4 TEXTBOOK (p .75)                 RIGHT
    Net CLOSE p ~ .5                    CLOSE in substance; INDETERMINATE
                                        by the chance-band control
