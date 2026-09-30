# HT-974471f045 / W1 -- implementation notes

Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md (control-first
pilot) and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md. Implementer
prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Written BEFORE any code or run exists.

## Spec field -> code

| spec field | code |
|---|---|
| substrate: population 30 | `POP=30` in pilot.py core `evolve()` |
| leaky tanh ESN, N=50, sparse 10%, input dim 1 | `init_individual()`, `run_esn()`; x_t = (1-a) x_{t-1} + a tanh(W x_{t-1} + W_in u_t) |
| ridge readout lambda=1e-4 | `ridge()` (with intercept column, intercept not regularised-exempt: lambda applies to all coefs) |
| 300 steps + 50 washout | `T=300`, `WASH=50` per life |
| 80 generations | gens 0..80 evaluated; task A for g<=40, task B for g>=41; births between generations; measurement after gen-80 evaluation |
| task A: delay-5 recall of u | y_t = u_{t-5} |
| task B: NARMA-5 | y_{t+1} = 0.3 y_t + 0.05 y_t sum_{i=0..4} y_{t-i} + 1.5 u_{t-4} u_t + 0.1 |
| mechanism (sediment, M3): W <- W + eps v w_parent^T, eps=0.05, v random unit input-like, rescale rho | `deposit_sediment()` -- PHASE 2 ONLY, in world.py |
| null twin: W <- W + eps v r^T, r random, ||r||=||w_parent|| | `deposit_null()` in pilot.py |
| control: no deposit, plain Gaussian mutation | `deposit=None` -- PHASE 2 (world.py) |
| positive control: ridge-optimal task A readout (n=2000) deposited at gen 80 | `positive_control()` in pilot.py |
| cheat | `cheat()` in pilot.py: at measurement the few-shot prediction is replaced by the true target (+ tiny noise) -- success injected into the observable |
| observable: few-shot (n=20) task A NRMSE at gen 80, mean over population elites, 10 seeds | `fewshot_A()`; per-seed value = mean over the 5 elites of the mean over R=5 fresh input draws |
| success: sediment mean <= 0.85 x null-twin mean, one-sided MWU p<0.05 over 10 seeds, AND PC reduces NRMSE_A by >= 15% | evaluate.py `meets_success()` |
| failure: ratio > 0.95 or p >= 0.2, or PC fails | evaluate.py |

## Parameters (chosen from the spec or fixed here before any run)

From spec: POP=30, N=50, density 0.10, input dim 1, lambda=1e-4, T=300,
WASH=50, 80 generations (switch after gen 40), eps=0.05, few-shot n=20, PC
readout n=2000, 10 seeds per arm, thresholds 0.85 / p<0.05 / 15% / 0.95 / p>=0.2.

Not in spec, fixed here (standard ESN defaults, not tuned):
- spectral radius rho = 0.9 (every W rescaled to exactly 0.9 after mutation and deposit; "keep rho unchanged" = rho stays 0.9).
- leak a = 0.5.
- W nonzero entries N(0,1) on a fixed random 10% mask, then rescaled; W_in ~ U[-1,1]^N per individual, inherited unchanged.
- input u_t ~ U[0, 0.5] i.i.d. for both tasks (NARMA standard range).
- mutation: every masked entry of W gets N(0, 0.1 * rms(masked entries)); deposits are dense rank-one additions on top.
- selection: rank by lifetime fitness (lower NRMSE better); top 5 kept unchanged (elites, no birth, no deposit); 25 offspring, parent uniform among top 10; each offspring = mutation, then deposit (arm-specific), then rescale to rho.
- lifetime learning: readout trained by ridge on the first 150 post-washout steps; fitness = NRMSE on the last 150. w_parent = the parent's lifetime readout (state part, intercept excluded) from its most recent evaluation.
- v: "random unit input-like vector" = U[-1,1]^N (same law as W_in) normalised to unit length, fresh per birth.
- NRMSE = sqrt(mean((yhat-y)^2) / var(y)).
- elites for the observable = top 5 by fitness at gen 80 (i.e. on task B).
- few-shot: fresh 350-step input, 20 training indices drawn uniformly without replacement from the 300 post-washout steps, ridge lambda=1e-4, test NRMSE on the other 280; repeated R=5 times with fresh inputs; the same measurement inputs (same seed stream) are used for every arm and for pre/post deposit.
- Common random numbers: for a given seed, initial population, per-generation inputs, mutation noise and parent choice come from streams shared across arms; deposit vectors come from a separate stream.
- Seeds 0..9 for every arm.
- Threads: OMP/MKL/OPENBLAS threads = 1; CPU time measured with process_time and appended to cpu_ledger.jsonl.

## Ambiguities and chosen readings

1. "Positive control ... at gen 80 directly": the PC needs a gen-80 population.
   Reading: take the gen-80 elites of the NULL_TWIN evolutionary run (same
   seed), compute w_A* (ridge, n=2000 samples, lambda=1e-4, delay-5 target) on
   each elite's own reservoir, deposit once W <- W + eps v w_A*^T (eps=0.05, v
   input-like unit, rescale to rho), measure few-shot NRMSE_A. "Reduces
   NRMSE_A by >= 15%" = per-arm mean reduction relative to the same elites
   before the deposit (= the NULL_TWIN arm value, identical by construction):
   1 - mean(post)/mean(pre) >= 0.15.
2. "Positive control meets the spec's success criterion" (pilot): PC arm
   mean <= 0.85 x NULL_TWIN arm mean AND one-sided MWU (PC < NULL_TWIN)
   p < 0.05 over 10 seeds AND reduction >= 15%.
3. "Null twin does NOT meet it" (pilot): the success criterion is relative to
   the null twin, so the null twin cannot be scored against itself, and the
   no-deposit CONTROL arm is phase-2 code. Pilot reading: the content-destroyed
   twin of the PC -- at gen 80 the same elites receive a deposit
   W <- W + eps v r^T with r random, ||r|| = ||w_A*||, same eps/v-law/rescale --
   is scored exactly like the PC (ratio vs NULL_TWIN mean, MWU, >= 15%). It must
   NOT meet the criterion. Stats also report NULL_TWIN gen-80 vs gen-0 elites
   (information only). In phase 2 `null_twin_meets_success` in OUTCOME.json is
   the proper reading: NULL_TWIN arm vs CONTROL arm (ratio <= 0.85 and MWU p < 0.05).
4. Cheat detected iff the CHEAT arm meets ratio <= 0.85 and p < 0.05 vs the
   NULL_TWIN arm.
5. Outcome in phase 2 (round-1 classes, decided in code): PC or cheat not
   detected -> INSTRUMENT_FAIL; else null twin meets success vs control ->
   CONFOUNDED; else sediment meets success -> SIGNAL; else NULL (failure
   criterion or the grey zone 0.85 < ratio <= 0.95 / 0.05 <= p < 0.2 both
   count as "treatment fails the criterion").
6. Few-shot n=20 with 51 coefficients and lambda=1e-4 is a near min-norm
   interpolation; values > 1 are possible and are kept (no clipping). MWU is
   rank-based.
7. NARMA-5 divergence: if a generated target is non-finite or |y| > 10, the
   input is redrawn from the same stream (counted in rows as `narma_redraws`).

## Pilot log

Attempt 1 (pilot_rows.jsonl, 39.5 CPU s): FAIL. Positive control as literally
specified (delay-5 ridge readout, n=2000, deposited once at gen 80) reduced
NRMSE_A by only 2.5% (ratio 0.975 vs NULL_TWIN, MWU p=0.137); needs >= 15%.
Cheat detected (ratio 0.007, p=1e-4). PC's content-free twin not meeting
(ratio 1.013). Info: NULL_TWIN gen-80 elites vs gen-0 elites ratio 0.92, p=0.011.

REPAIR (the one allowed; controls only, thresholds unchanged; no treatment
code or statistic exists): the deposit term eps v w^T acts through the
recurrent step, so what it injects into x_{t+1} is w^T x_t -- the readout's
value ONE STEP LATE. A delay-5 readout therefore deposits u_{t-6} into x_t,
which is not task-A content for the recall target u_{t-5} (u is i.i.d.). The
repaired positive control fits the ridge-optimal (n=2000, lambda=1e-4) readout
of u_{t-4} on x_t, so the deposited feedback carries exactly u_{(t+1)-5}, the
task-A target, through the channel. Everything else (eps, v law, rescale,
elites, instrument, seeds, the content-free twin matched to ||w_A*||) is
unchanged. Note for the reading: the spec's sediment operator deposits the
parent's lifetime readout unshifted, i.e. the same one-step lag applies to the
treatment; this is recorded as a property of the spec, not repaired in the
treatment (which must follow the spec as written).

Attempt 2 (pilot_rows_attempt2.jsonl, 38.9 CPU s): FAIL. Repaired PC reduction
1.6% (ratio 0.984, p=0.37). Cheat detected; content-free twin not meeting.
Second pilot failure -> OUTCOME.json outcome SPEC_UNATTAINABLE. Stopped; no
phase-2 code written.
