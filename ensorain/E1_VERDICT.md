# ENSORAIN E1 "KNIFE FIGHT" -- verdict

> ANNOTATION 2026-09-23 (E1.5, ensorain/E1P5_VERDICT.md s4). Verdict below
> preserved exactly. E1.5 shows E1's gate failure at 128/192 was B2: the TT
> arms used the observed order or a missed random search (2 sweeps). With
> the latent order found and 10 sweeps, TT beats LOWRANK 4x per parameter
> at 192 in two replicate sets. The s4 "384 signal" was constants + order
> search, not headroom.

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Rows ship in this
commit: ensorain/runs/e1_confirm_C1..C4.jsonl (10,081 lives, instances
20000-20039), e1_tune.jsonl + e1_champions.json (frozen e494757b2 before
any confirmatory row), e1_score.json, e1_score_stdout.txt. Scorer
ensorain/e1/score.py frozen at 04b6feec8. Preregistration PREREG_E1.md
(acf899366) + part 2 (8071e4163).

## 1. Verdict under the frozen rule

    INDETERMINATE (controls)

POSITIVE CONTROL FAILED at C=192: TT_LATENT (latent order, true ranks,
TT_TUNED@192's constants) median L2 success 0.284 (gate >= 0.5), median
held-out R^2 0.477 (gate >= 0.5). Cause, identified before the run and
recorded in the tuning commit: the rule ties TT_LATENT to TT_TUNED's
champion constants, and TT_TUNED@192's 24-draw random search landed on
2 sweeps / a poor rank profile (training EFF 0.02). Dev round 2 had shown
20 sweeps were needed at this cap.

Other controls PASS: smuggler refused by the audit; TT_INJECT = 1.00 x
ORACLE reward at 192; in WORLD R no arm's L2 success exceeds NOMEM's
(largest difference +0.0001).

## 2. The governing gate fails regardless

G (R5) at the preregistered severe-pressure caps, EFF = (U - U_NOMEM) /
persistent params, 40 instances, paired bootstrap:

    cap   best TT        EFF    LOWRANK EFF   G vs LOWRANK
    128   TT_OBS         0.717  1.656         FAIL (lo -1.45)
    192   TT_OBS         1.131  2.634         FAIL (lo -2.23)

A rank-1 (128-float) matrix unfolding on partition {A,B}|{C,D} beats every
TT per parameter AND in raw utility at 192 (U 1,493 vs 1,373). TT beats
LRU, KNN, CP and MLP at both caps (CI lo > 0). G also fails at kappa x0
and x4 (C4). Under the operator's rule -- any non-TT within 10% at
matched memory and compute -> B -- B stands at the question that was
asked.

## 3. Recommendation

    B: CLOSE THE BRANCH AS PREREGISTERED.

The claim asked for -- under SEVERE memory pressure, TT gives materially
more transferable competence per parameter and per unit compute -- did
not happen. Both readings of the failure end the same way: either the
TT learner cannot exploit exact-capacity TT memory within a life (B2,
which is what the positive control says), or LOWRANK is simply the
better bounded memory here (G). Neither is a reason to scale.

## 4. The one strong signal, NOT preregistered as the claim

At C = 384 (2x the true TT's 192 parameters; run and reported, not
gated) the picture inverts:

    arm        EFF    lock success L1/L2   held-out R^2   comp energy
    TT_TUNED   5.71   0.75 / 0.70          0.97           110
    TT_LATENT  10.01  0.67 / 0.64          0.98            55
    LOWRANK    2.53   0.50 / 0.45          0.63           152
    TT_OBS     1.33   0.36 / 0.33          0.50            22
    CP, MLP    <=0.16
TT_TUNED beats every non-TT arm there with CI lo > 0 (vs LOWRANK lo
+2.61), and its held-out (never co-observed A,C pairs) success is 0.70 vs
NOMEM 0.25: real factor transfer. TT_TUNED's tuned order (1,0,2,3)
differs from the observed order and TT_OBS in the observed order gets
1.33 -- the order mattered here.

[SUPERSEDED by E1.5 s3/S1-S2: the reading below is FALSE; exact capacity
learns with the right order and enough sweeps.] Reading: an OVER-parameterised TT (ranks 5-6 against a true rank 3)
learns the world from correlated 128-sample batches; an exactly-sized TT
does not. That is a known property of ALS completion (slack rank helps),
not evidence about bounded organisms under severe pressure. It is the
strongest positive signal in either campaign, it is post hoc, and by the
seat's own doctrine it is a hypothesis, not a result. If the operator
wants it tested it needs its own preregistration (cap sweep 256-768,
positive control with its OWN tuned constants, same G rule), and the
seat's prior on it surviving is moderate at best.

## 5. Transplant (R7) -- fails for every structural arm

Carried vs fresh memory, first 400 events after an undisclosed
relabeling (L1+L2 success): TT_OBS 0.205 vs 0.248, TT_TUNED 0.232 vs
0.247, TT_LATENT 0.217 vs 0.248, LOWRANK 0.225 vs 0.244, CP 0.193 vs
0.233 (all carried < fresh). MLP 0.255 vs 0.170 is the only "pass":
fresh MLP is below NOMEM (0.25) while carried MLP sits at NOMEM -- a
calibration artifact, not transfer. Nothing learned survives a relabeling;
every memory here is bound to its coordinate frame.

## 6. Failure shapes

F1 (E0) is fixed by design: locally-ranked guessing now earns nothing
    (NOMEM L2 0.25 is the heavy-tail chance floor, removed by EFF; no arm
    beats it in WORLD R).
F7  [SUPERSEDED by E1.5: exact capacity learns (R^2 0.96-0.98 at 192)
    with the right order and 10-20 sweeps; the numbers below reflect
    inherited constants and a missed order search.] Exact capacity does not learn. At C=192 the TT that CAN represent the
    world exactly reaches R^2 0.48 (latent order) / 0.19 (observed); at
    C=384 R^2 0.97-0.98.
F8  Per-parameter efficiency favours the smallest adequate model:
    LOWRANK rank 1 (128 floats) wins the ratio at 128 and 192 even where
    its raw utility is close to TT's.
F9  The positive-control coupling (TT_LATENT inherits TT_TUNED's
    constants) turned a random-search miss into INDETERMINATE. It was the
    rule, it was flagged before the run, and it is not re-litigated here.
F10 Nothing transplants.

## 7. Seat predictions scored

    P1 positive control passes        WRONG (0.28 / 0.48)
    P2 G fails; verdict B p ~ .6      G FAILED (right, via LOWRANK, not CP)
    P3 transplant fails for all       RIGHT (MLP pass is an artifact)
