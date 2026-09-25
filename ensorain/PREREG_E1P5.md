# ENSORAIN E1.5 "COMPRESSION HEADROOM ASSAY" -- preregistration part 1

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Authority: operator
authorization roles/Ensorain/prompts/2026-09-23_e1p5_authorization/
(verbatim). Committed BEFORE any E1.5 code runs. E1's verdict and rows
are preserved exactly as recorded (27e1f1715); nothing here re-scores
E1. This is the FINAL Ensorain assay unless it passes its hard gate.
Part 2 may set constants (calibrated control constants, tuned
champions) only; no gate, threshold, cap list, arm list, seed set or
verdict clause below may change.

## 0. The question

Did the organism need ~384 floats to REPRESENT what it learned, or only
to FIND it? Operationally: is there a reproducible cap range where TT
beats the strongest matched non-TT memory, and is the learned TT then
compressible (no retraining) toward a size at which a TT TRAINED natively
fails -- or does its advantage come from higher-order structure the
matrix format cannot hold at matched size?

## 1. Unchanged

World, event stream, locks, tolerance (abs tau .15), economy, compute
price and per-life ceiling, scratch S = 128 samples, consolidation
machinery, EFF definition: all exactly E1 (ensorain/e1/, PREREG_E1
part 2). No evolution, no new mechanisms, no GPU work.

## 2. Sweep and arms

Caps: 128, 160, 192, 224, 256, 320, 384, 512 (persistent floats).
Arms (WORLD C): NOMEM, LRU, KNN, CP, LOWRANK, MLP, TT_TUNED, TT_LATENT,
ORACLE. Negative control (WORLD R): same arms at caps 192 and 384, set A.

TUNING (equal budget): CP, LOWRANK, MLP, TT_TUNED each get 32 random
configurations x 4 training worlds per cap (seeds 3000+), same gene
ranges as E1 part 2 except TT ranks 1..8 (to reach 512) and LOWRANK rank
1..cap/128. Objective mean EFF. Champions frozen before confirmatory.

TT_LATENT (positive control) gets ITS OWN constants, calibrated on DEV
seeds (300-305) per cap by a fixed grid lam in {3, 10, 30, 100} x sweeps
in {5, 10, 20}, init 0.5, objective median held-out R^2. Never inherited
from TT_TUNED. Frozen in part 2 before tuning.

## 3. Measurements (per life)

held-out R^2; seen R^2; held-out lock success (L2 and L3h); utility U and
EFF; compute spent learning (consolidation units) and querying;
persistent params; EFFECTIVE TT ranks after the life (numerical ranks of
the learned TT's unfoldings at relative singular-value tol 1e-2);
scratch (fixed 128 samples) and compression workspace (declared below);
final compressed size.

COMPRESSION CURVE (TT_TUNED and TT_LATENT; LOWRANK for comparison), after
the life, NO retraining: the organism rounds ITS OWN memory. For each
target budget b in {384, 320, 256, 224, 192, 160, 128} below the trained
size: TT-SVD of the learned TT's own dense tensor (4096-float transient
workspace, declared) in its own mode order, choosing the rank triple
(each <= its trained ranks) with the smallest reconstruction error TO ITS
OWN MEMORY (the truth is never consulted) among triples fitting b.
LOWRANK: SVD truncation of its learned matrix to rank floor(b/128).
Each compressed memory is scored against the truth by (i) held-out R^2
and (ii) REPLAY: every lock event of the life's stream answered by the
compressed memory, reward counted without energy dynamics; above-chance
replay utility = replay reward - NOMEM replay reward on the same stream.

## 4. Replication

Two disjoint confirmatory instance sets, 40 instances each, organism
seeds 0-1: SET A 30000-30039, SET B 30100-30139. Class 0.

## 5. Hard verdict (operator's, operationalised; any failure -> CLOSE)

PC (positive control): TT_LATENT at C=384 has median held-out R^2 >= 0.5
  AND median L2 success >= 0.5, in both sets. Reported at every cap
  (whether latent-order TT also needs headroom is itself a finding).
T (reproducible transition): there exist two ADJACENT caps in the sweep
  where, in BOTH sets, mean EFF(TT_TUNED) >= 1.10 x mean EFF(X*) with
  paired bootstrap (10,000) 2.5% bound of EFF_TT - 1.10*EFF_X* > 0, X* =
  the non-TT arm (LRU, KNN, CP, LOWRANK, MLP) with the highest mean EFF at
  that cap in that set. Also every other non-TT arm must satisfy the same
  (so "strongest" cannot be dodged by the choice of X*).
C1 (headroom-to-find): for some cap c in T, with trained TT_TUNED size
  s_c, at a compression budget b <= 0.6 s_c (pooled over both sets):
  (a) retention: median compressed held-out R^2 >= 0.9 x median trained
      held-out R^2 AND mean compressed above-chance replay utility >= 0.9
      x trained; AND
  (b) headroom mattered: mean above-chance replay utility of the
      compressed TT exceeds that of TT_TUNED trained NATIVELY at the
      largest sweep cap <= b by > 10%, bootstrap 2.5% bound > 0 (paired
      by instance).
C2 (higher-order structure): for every cap c in T, median TT_TUNED
  held-out R^2 exceeds by >= 0.10 the LOWRANK REPRESENTATIONAL CEILING at
  that cap: the best held-out R^2 over the three 2+2 partitions of the
  truncated SVD (rank floor(c/128)) of the TRUE field's unfolding
  (computed per instance, median). A learner-independent bound: the matrix
  format cannot hold what TT learned at matched size.

  INTRIGUING -- WORTH EXPLORING   iff PC and T and (C1 or C2)
  CLOSE (B)                        otherwise; the scorer prints which
                                   clause failed. PC failing alone is
                                   labelled CLOSE (control), per the
                                   operator: the control must pass
                                   before the sweep is interpreted.

## 6. Seat predictions (losable)

P1 PC passes at 384 with own constants (p .8).
P2 T holds across {320, 384} or {384, 512} in both sets (p .6); fails at
   <= 224 (LOWRANK/under-capacity TT).
P3 C1(a) retention passes (an over-parameterised ALS solution of a
   rank-3 world is near rank-3; p .6); C1(b) passes only if native TT at
   192 stays weak, which E1 says it does (p .45).
P4 C2 FAILS wherever T sits at caps >= 384: the {A,B}|{C,D} unfolding of
   a rank-(3,3,3) chain has matrix rank exactly 3, so the LOWRANK ceiling
   there is R^2 = 1.0 (checked from the construction before commit). C2
   can only pass for caps 256/320 (rank-2 ceiling) or below (p .25).
Net: INTRIGUING p ~ .3 (almost entirely through C1); CLOSE p ~ .7.
