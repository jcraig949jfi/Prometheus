# HT-47f4c02be4 / W1 -- implementation notes (written before any code ran)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
2026-09-29_probe_round1/PREREG.md. Read: W1, M1, M2, M10, L1, L2, L3 only.

## Spec field -> code

| spec field | code |
|---|---|
| mechanism (levels = periodic composite predictors; unpredicted integer promoted; cost = c*depth + 1 bit/residual error) | agent.py `run_agent` |
| intervention: c in {0.001,0.003,0.01,0.03,0.1}; cap K in 1..40 | world.py (phase 2): r(K) for K=0..40 from one pass; cost(K,c)=c*K+r(K); K*(c)=argmin_K |
| control: depth frozen at 0 | world.py CONTROL arm = cap K=0 |
| positive_control: explicit OR of periodic sources {2,3,5,7}; depth must stop at 4 with zero residual | pilot.py `pc_stream`, arm POSITIVE_CONTROL |
| null_twin: Cramer stream, n>=3 'prime' w.p. 1/ln n, agent unchanged | pilot.py `twin_stream`, arm NULL_TWIN |
| CHEAT (PREREG round 1: success injected into the observable) | pilot.py arm CHEAT |
| observable: r(K) over n in [2,1e5]; total cost per step; K*(c) | rows: `r_by_K` (K=0..40), `depth_final`, `periods`; cost/K* in phase 2 |
| success: max_{K=1..20} |r(K)-M(K)|/M(K) <= 0.05 on real stream (M(K)=prod_{p<=p_K}(1-1/p)), AND twin r(20)/r(0) >= 0.9 | eval_common.py `clause_A`, `clause_B`, `success` |
| failure: complement | same functions |
| size: N=1e5, K<=40, 5 costs, 10 twin seeds | N=100000, KMAX=40; twin seeds 0..9; PC seeds 0..4; CHEAT seeds 0..4 |

## Ambiguities and chosen readings (fixed before running)

R1 Stream alphabet. Each n in [2,N] carries a label in {composite, prime,
   silent}. Real stream and twin use only {prime, composite}. The PC stream
   ("explicit OR of periodic sources") is ON at every multiple of 2,3,5,7
   (the source integer itself included): n in {2,3,5,7} -> 'prime' (first
   firing of a source), other ON integers -> 'composite', OFF integers ->
   'silent'. Reading: the real stream is the OR of the periodic sources of
   ALL primes, so every n>=2 is an event; the PC is the same construction
   with four sources.

R2 Levels. Level with period p predicts 'composite' at n with p|n and n>p
   (it is born at n=p). Default when no level fires: no prediction.

R3 Residual error at n (the unit of r): the label is non-silent AND either
   (a) no level fires (unpredicted; passed upward; 1 bit), or (b) a level
   fires but the label is not 'composite' (misprediction). Silent integers
   are never residual (default "no event" is correct for them). This is the
   only reading under which the PC's stated "zero residual" and the
   hypothesis's "residual follows the Mertens product" are both expressible.

R4 Promotion. An unpredicted non-silent integer is promoted to a new level
   (period n) if depth < cap. Label value (prime/composite) does not gate
   promotion -- literal mechanism text: "an unpredicted integer is promoted".

R5 Cap K. Depth capped at K; r(K) is the residual count over the whole run
   n=2..N divided by (N-1). Because promotion order does not depend on the
   cap, the cap-K run's levels are the first K levels of the cap-40 run;
   all 41 caps are computed from one streaming pass by recording, per n,
   the minimum index of a firing level. agent.py self-checks this against a
   literal per-cap simulation on a small N.

R6 Control "predict prime-density only": at depth 0 no level fires, so every
   non-silent integer is residual; r(0)=1 on real stream and twin. The
   density prior does not absorb integers under R3.

R7 Twin: n=2 labelled prime (spec starts the Bernoulli at n>=3); n>=3
   prime iff U < 1/ln n, U~Uniform(seed).

R8 Positive control success. The success criterion as written refers to
   "the real stream" and to primes p_K for K up to 20; a four-source stream
   has no p_5..p_20 and its capped residual is not a product law (silent
   integers are excluded). The PC field states its own pass condition, and
   that is the reading used: with cap 40, final depth == 4, periods ==
   [2,3,5,7], and zero residual errors for n > 7 (i.e. after the fourth
   promotion), on every seed. Recorded as an interpretation, not a
   threshold change.

R9 Null twin "meets success". The twin meets success iff clause A (Mertens
   deviation <= 0.05 for all K=1..20, M(K) from the TRUE primes) holds on
   the twin's own r(K). Clause B's ratio r(20)/r(0) is computed from the
   twin rows and reported (it is the twin half of the treatment criterion
   used in phase 2). Chosen aggregation (conservative, makes the pilot
   harder to pass): the twin "meets success" if clause A holds on ANY
   single twin seed or on the seed-mean r(K).

R10 CHEAT. r(K) := M(K)*(1+e_K), e_K ~ U(-0.01,0.01) per seed, for
   K=1..40 (K>20 uses further true primes), r(0)=1, and the twin ratio is
   injected as 1.0. Detected iff the evaluator's `success` returns True on
   every cheat seed.

R11 Aggregation for the treatment (phase 2): the real stream is
   deterministic, so every seed gives the same r(K); success/failure
   evaluated on the (identical) per-seed values; twin ratio for clause B =
   mean over the 10 twin seeds of r(20)/r(0) (chosen before any run).

## Parameters (from the spec)

N = 100000; KMAX = 40; K range for clause A = 1..20; thresholds 0.05 and
0.9; costs {0.001, 0.003, 0.01, 0.03, 0.1}; twin seeds 0..9; PC and CHEAT
seeds 0..4 (PC is deterministic, the five rows are identical by
construction -- recorded, not hidden).

## Budget

Estimated well under 1 CPU core-minute total. Measured core-minutes are
written to PILOT.json / OUTCOME.json.

## Repair log

(none yet)

## Pilot log

Attempt 1: pilot.py ran once. pilot_eval.py crashed on its first call
(numpy bool not JSON serializable) -- a bug in the evaluator, not in the
controls; fixed (bool casts, removed unused prior-attempt CPU logic) and
pilot_eval.py rerun on the same rows. No repair of controls. Result:
PILOT PASS (PC depth 4, periods [2,3,5,7], zero residual after n=7 on 5/5
seeds; CHEAT detected 5/5; twin clause-A max rel dev ~0.65 on 10/10 seeds).

Observation recorded BEFORE any treatment code existed: the twin r(20)/r(0)
is ~0.21 on every seed. Clause B (twin ratio >= 0.9) is part of the
treatment success criterion, so under readings R3/R4 the treatment cannot
meet success whatever r(K) on the real stream is. Parameters and
thresholds are NOT changed in response (PREREG); phase 2 proceeds as
frozen and the evaluator decides.
