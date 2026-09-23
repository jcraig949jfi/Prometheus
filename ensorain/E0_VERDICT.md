# ENSORAIN E0 "CHOO CHOO" -- verdict

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Rows ship in this
commit: ensorain/runs/confirm_M1..M4.jsonl (15,760 lives), genome_c0_cap
{96,168}.json, evolve_*.jsonl, score_E0.json, score_E0_stdout.txt.
Scorer: ensorain/e0/score.py, frozen at 33055de3d before any
confirmatory row. Preregistration: PREREG_E0.md (20a4bab5c), part 2
+ A6 (60b8cb1d1, 33055de3d).

## 1. Verdict under the frozen rule

    INDETERMINATE (controls)

The positive control failed: the planted TT (true mode order, true ranks,
TT_TUNED learning constants) reached median R^2 on unvisited cells of
0.007 at C=168 (gate >= 0.5). All three permitted learner-engineering
rounds were used on dev seeds before the freeze. By the part 1 rule this
is B2 -- the online learner cannot build the representation within a
lifetime -- not a verdict on the world.

## 2. The seat's recommendation (a reading, not the rule's output)

    B -- "fun, but not a great use of tokens/compute" -- FOR E0 AS BUILT.

Every gate that could be evaluated points the same way, and the failure
shape explains why rather than merely that:

H1 (premise)       FAIL. C=96: TT_TUNED 7,605 vs best non-TT (LRU)
                   3,235, margin +135%, CI lo > 0, interaction CI lo > 0
                   (PASS there, because LOWRANK is NA below 128 floats).
                   C=168: LOWRANK 8,719 beats TT_TUNED 7,058 (margin
                   -19%). H1 needs both caps (A1).
H2 (selection)     FAIL on the cross-class clause. Harvest: TT_EVOLVED
                   beats TT_TUNED at C=168 by +33.5% (CI lo +1,028);
                   +13.1% at 96 (CI lo < 0). Order recovery: evolved
                   orders need 568 / 1,464 TT params for the true field
                   vs random-order median 1,568 (latent order: 168) --
                   better than chance, far from the physics. Cross-class:
                   the class-0 genome gains AS MUCH on class 1 (2,639 vs
                   2,365 at C=168; 585 vs 1,000 at 96). The gain is
                   generic tuning, not discovered physics.
H3 (dose)          TT_TUNED's advantage over the best non-TT arm is
                   NEGATIVE at every lambda (-1,660 .. -2,621). Spearman
                   rho = -9/10 EXACTLY (ranks 4,5,3,2,1); the scorer's
                   float gave -0.8999999 and printed FAIL. Annotated,
                   not re-scored: the verdict is decided by the controls
                   either way, and a "monotone decline" of an advantage
                   that is never positive is vacuous.

## 3. Failure shapes (what the rows say, with the numbers)

F1. The task rewards COARSE structure, not a faithful representation.
    Harvest comes from a local argmax over 4 exits. Every surviving
    learner has R^2 on unvisited cells ~0 (TT_TUNED -0.00, TT_EVOLVED
    -0.01 at 168) yet harvests ~2x NOMEM. Evolution drove ranks to 1-2
    at both caps (champions (1,1,1,2,2) and (1,2,1,2,1)). A rank-1 TT is
    order-invariant, so selection had almost no reason to find the order.
    This is the directive's "trivial low-rank fitting", measured.
F2. Bounded structure DOES beat unbounded caching -- weakly, and not
    TT-specifically. DICT_UNCAP (every visited cell, no cap): 6,244.
    TT_TUNED at 96 floats: 7,605; TT_EVOLVED at 168: 9,423; LOWRANK at
    384: 14,112. The premise "I cannot remember this universe, I must
    learn its structure" holds; the tensor-train form is not what makes it
    hold (a 64x64 matrix factorisation does it better at 384).
F3. Online learning under the cap is ~10x less sample-efficient than the
    literature. Batch ALS: R^2 0.997 from 800 samples (latent order).
    Online TT: ~0.8-0.94 after 8,000. ALS needs ~1,600 stored floats --
    above every gated cap. The cap forbids the good algorithm; the
    organisms are left with SGD.
F4. The compute proxy decides the baseline ranking. kappa=0 (M4, not
    gated): KNN 172 -> 6,133; TT_TUNED 7,058 -> 11,492; TT_PLANTED
    6,970 -> 11,626; LOWRANK unchanged (8,719 -> 8,756, it is cheap).
    Any E1 claim must survive a compute-proxy sensitivity sweep.
F5. Memory can be a trap: LRU (3,030 at 168) < NOMEM (3,759) in C;
    remembering good cells leads back to depleted ones.
F6. At cap 4096 every TT and LOWRANK arm dies of compute in <60 steps
    (the "generous control" is killed by kappa, not by memory).

## 4. Controls (literal part-1 reading and governing A6 reading)

    clause                         literal   governing
    NEG r2 in R                    FAIL      PASS (median R^2 <= .05)
    NEG harvest in R               PASS(LRU) PASS (NOMEM)
    POS ORACLE top                 FAIL*     PASS  (*TT_SVD_INJECT 17,446
                                                   > ORACLE 16,546 at 168)
    POS planted R^2_unv >= .5      FAIL (0.007)
    CHEAT smuggler refused         PASS (mid-life audit: "secret: dict")
    CHEAT inject >= .9 ORACLE      PASS (1.054 at 168, 1.052 at 384)

The measurement channel works (cheat controls pass, R separates). The
positive control fails for the learner, not the instrument.

## 5. Seat predictions scored (calibration ledger)

    predicted                         outcome
    H1 FAIL                           FAIL (correct)
    H2 harvest FAIL                   PASS at 168 (wrong)
    H2 order recovery PASS            PASS, weakly (correct, but the
                                      recovery is far from the physics)
    H3 PASS                           boundary / vacuous (not informative)
    net B-MUNDANE most likely         INDETERMINATE by rule; B in reading

## 6. What would change this recommendation (E1 kill-test, not started)

One cheap experiment could flip B to A, and it should be run only if the
operator wants E1: a world whose DECISIONS need fine structure (payoff
depends on exact values or on delayed, cross-region relevance P7), and
where the organism may trade cap for an amortised batch step (charged
ALS on a small buffer). Kill condition, stated now: if in that world
LOWRANK or any non-TT arm at matched cap and matched compute still
matches the best TT arm within 10%, the tensor-train form is not what
matters and B stands without appeal.

## 7. What was NOT done

s12 of the directive is truncated; the INTERIM efficiency measure
(R^2 on unvisited cells) is reported, not gated. P4/P5/P7 puzzle families
were not built (E0 scope). No GPU was used (tiny per-organism tensors
are faster on CPU; recorded). No cloud spend.
