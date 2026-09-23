# ENSORAIN E1.5 "COMPRESSION HEADROOM ASSAY" -- verdict

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Rows ship in this
commit: ensorain/runs/e1p5_confirm.jsonl (12,960 lives: sets A and B x 8
caps x 9 arms x 80, plus WORLD R), e1p5_calibrate.jsonl,
e1p5_latent_constants.json, e1p5_tune.jsonl, e1p5_champions.json,
e1p5_score.json, e1p5_score_stdout.txt. Scorer ensorain/e1p5/score.py
frozen at a532562e2. Preregistration PREREG_E1P5.md (bde3f4237), part 2
(630f45f6f; confound addendum aae4dd71e).

## 1. Verdict under the frozen rule

    CLOSE (B): failed "C1 or C2"

    PC  PASS  TT_LATENT@384 (own constants): held-out R^2 0.979 / 0.979,
              L2 success 0.69 / 0.71 (sets A / B).
    T   PASS  TT_TUNED beats EVERY non-TT arm by >10% (CI lo > 0) in BOTH
              sets at caps 160, 192, 224 (adjacent pairs {160,192},
              {192,224}). At 192: EFF 8.63 / 8.60 vs LOWRANK 2.03 / 1.76.
    C1  FAIL  unreachable by construction and failing in substance: T sits
              at s_c <= 192, so "b <= 0.6 s_c" needs b <= 115, below the
              smallest budget (128). In substance, rounding the 192-float
              TT to 160 keeps R^2 0.87 but 66% of utility; to 128, R^2 0.77
              and 40% of utility.
    C2  FAIL  "for every cap in T": at 160 TT R^2 0.29 < ceiling 0.56 +
              0.10. At 192 (0.96) and 224 (0.74) TT DOES exceed the
              rank-1 matrix ceiling (0.56) by more than 0.10.

## 2. The operationalisation choice that decides it -- stated, not used

The operator's clause reads "a reproducible transition ... across at least
two adjacent caps ... and either (1) or (2)". The seat's preregistration
took T as the UNION of all passing adjacent pairs and required C2 at
EVERY cap in that union. Under the other natural reading -- some adjacent
pair that satisfies T also satisfies C2 -- the pair {192, 224} passes
(PC, T and C2 all hold there) and the verdict would be INTRIGUING. The
frozen rule is not re-read after the data; the verdict stays CLOSE. The
operator owns the clause and may rule on which reading was meant.

## 3. The seat's recommendation: CLOSE, for reasons that do not depend on s2

S1. THE HEADROOM HYPOTHESIS IS FALSIFIED. The organism did NOT need 384
    floats to find the structure. With the latent order known and its own
    constants (lam 30, 20 sweeps), a TT at EXACTLY 192 floats reaches
    held-out R^2 0.98 (flat from 192 to 512: the architecture is the same
    true-rank TT). TT_TUNED at 192 with a good order: 0.96. Rounding below
    192 loses competence steeply (s1). It needed 192 to REPRESENT, and
    192 was enough to FIND.
S2. E1's "384 signal" decomposes into two artifacts, both now measured:
    (i) TT_LATENT in E1 used the same 192-float architecture at both caps
    and differed only by inherited constants (10 vs 2 sweeps); (ii)
    TT_TUNED's random order search hits or misses by cap -- in E1.5 it
    found the latent-matching order (1,0,2,3) at 160/192/224 and missed it
    at 256-512 (training EFF 10.1 at 224, -0.05 at 384). The "transition"
    in T is where the order search succeeded, not a capacity phase
    transition (EFF 8.6 at 192, 0.10 at 256 -- non-monotone in memory).
S3. C2's pass at 192/224 is the tautology declared in PREREG_E1 s0: the
    world IS a rank-(3,3,3) tensor train, so the TT format holds it in 192
    floats while the matrix format needs 384 (rank-3 unfolding). "The
    matrix baseline cannot represent it efficiently" is true by
    construction in a TT-generated world; it is a statement about the
    generator, not a discovered property of bounded organisms.
S4. What remains is standard tensor completion: with the right mode order
    and enough ALS sweeps, a TT with matched inductive bias beats generic
    memories at matched size. The hard part is the ORDER, and nothing in
    E0, E1 or E1.5 discovered order by learning -- E0's evolution drove
    ranks to 1-2 instead, and E1.5's order came from random search.

## 4. Annotation on E1 (E1's verdict preserved exactly; nothing re-scored)

E1's governing-gate failure at 128/192 (LOWRANK beat TT) is now explained:
the TT arms there used either the observed order (TT_OBS) or a missed
random search (TT_TUNED@192, 2 sweeps). In E1.5 at 192 with a found order
and 10 sweeps, TT beats LOWRANK 4x per parameter in both sets. E1's
failure was B2 (search/constants), not B1. It does not change E1's
recorded verdict, and it does not rescue the premise either (s3, s4).

## 5. Controls

Negative (WORLD R, set A, caps 192/384): no arm's L2 success exceeds
NOMEM's (max +0.00). Positive: PASS (s1). Cheat controls were not re-run
(E1.5 changed no machinery; E1's smuggler/inject controls stand).

## 6. Seat predictions scored

    P1 PC passes at 384 (p .8)            RIGHT
    P2 T at {320,384} or {384,512}        WRONG: T at 160-224 (order-
                                          search luck; 384 failed T)
    P3 C1(a) retention passes              NOT SCORABLE (unreachable);
                                          in substance WRONG (40% at 128)
    P4 C2 fails where T sits >= 384       VACUOUS (T not there); C2
                                          passes at 192/224, fails at 160
    Net CLOSE p ~ .7                      CLOSE
