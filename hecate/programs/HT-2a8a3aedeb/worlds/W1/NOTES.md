# HT-2a8a3aedeb / W1 -- implementation notes

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
2026-09-29_probe_round1/PREREG.md. Written BEFORE any code was run.

## Spec field -> code

| spec field | code |
|---|---|
| state space: 4 factors x 6 levels (1296) | `common.D=4, common.N=6`, tensors shape (6,6,6,6) |
| product passive dynamics | `common.make_world(seed)`: P_i = 0.5*I + 0.5*Dirichlet(1)-rows, one 6x6 per factor, applied axis by axis |
| linear Bellman, finite horizon 20 | `common.solve(q, P, lam)`: log z_H = 0; for t = H-1..0: log z_t = -q/lam + log(P (x) z_{t+1}); done in the LOG domain (per-axis logsumexp) so the solve itself cannot underflow; z = exp(log z_0 - max) |
| V = -lambda log z | `V = -lam * logz0` (the un-normalised value, exact from the log domain) |
| q = sum_i q_i(s_i) + c * sum_{k<=r} rank-1 products | `common.make_q(world, r, c)`: q_i ~ U[0,1] per level; rank-1 term k = outer(u_k1..u_k4), u ~ U[0,1], each term divided by its max (so each coupling term spans [0,1] like one q_i); u_1..u_4 drawn once per seed, first r used (nested) |
| r in {1,2,4}, c in {0.5,2}, lambda in {0.1,0.3,1,3,10}, 10 seeds | `common.R, C, LAMS, SEEDS=range(10)` |
| observable: max TT bond at rel. Frobenius tol 1e-6 (secondary 1e-3) | `common.tt_bonds(A, eps)`: standard TT-SVD (Oseledets), per-cut truncation threshold delta = eps/sqrt(d-1)*||A||_F; bond = smallest rank whose discarded tail norm <= delta; max over the 3 cuts. Max attainable 36 |
| control: tanh(V/sd(V)), rank-preserving quantile map to Gaussian | `common.controls(V)`: tanh((V - mean V)/V.std()) (attempt 1 used no centering; see Log); norm.ppf((rankdata(V)-0.5)/1296) |
| positive_control: c = 0 | arm POSITIVE_CONTROL: q additive only |
| null_twin: entry-shuffled q | arm NULL_TWIN: the coupled q for (seed, r, c) with its 1296 entries permuted (seeded), then solved identically |
| cheat control (round-1 PREREG) | arm CHEAT: z replaced by a planted positive TT-rank-r tensor (sum of r rank-1 products, entries U[0.5,1.5]); V and tanh from the NULL_TWIN solve of the same (seed, r, c). Goes through the same tt_bonds measurement |
| treatment (phase 2) | arm TREATMENT: coupled q, bonds of z and V |
| control (phase 2) | arm CONTROL: tanh and quantile bonds of the TREATMENT V (same q) |

Rows: one JSON line per arm x seed; each row holds a list of all (r, c,
lambda) conditions for that seed with bonds at both tolerances, plus
diagnostics (fraction of normalised z entries < 1e-300 and < 1e-16,
rel. std of z, per-seed P mixing distance ||P_i^20 - stationary||).
Threads pinned to 1 (OMP/MKL/OPENBLAS) so process time = core time.

## Criterion as applied (primary tol 1e-6)

A cell = (r, lambda) at c = 0.5 with lambda in {1, 3, 10}.
- S1: in every cell, #seeds with bond(z) <= bond(V) - 1 is >= 8 (of 10).
- S2: in every cell, #seeds with bond(z) <= bond(tanh) - 1 is >= 7.
- S3: for every lambda in {1,3,10}, Spearman rho between r and bond(z)
  over the 30 (r, seed) points >= 0.6. rho undefined (constant bond) = fail.
- success = S1 and S2 and S3.
- failure (phase 2): in any cell (r, lambda>=1) at ANY c in {0.5, 2}
  (the failure criterion names no c; read literally),
  #seeds with bond(z) >= bond(V) is >= 5, OR #seeds with bond(z) not
  < bond(tanh) is >= 5.

## Ambiguities and chosen readings

1. "in >= 8/10 seeds for every r" -- seed counts are per (r, lambda) cell;
   every lambda >= 1 cell must pass (stricter than pooling over lambda).
2. Spearman "across seeds": computed per lambda over 30 points (3 r x 10
   seeds); required at every lambda >= 1.
3. Positive control (c = 0) cannot vary r (r does not enter q when c=0),
   so S3 is undefined for it. Reading: POSITIVE_CONTROL meets success iff
   (a) its own spec condition holds -- max bond(z) == 1 and max bond(V) == 2
   at tol 1e-6 for every seed and every lambda ("any deviation means the
   pipeline is broken"), AND (b) S1 and S2 hold in each lambda >= 1 cell
   (one cell per lambda). S3 is N/A for this arm; the evaluator's ability
   to see S3 is carried by the CHEAT arm, which varies r.
4. CHEAT detected iff the full success criterion (S1,S2,S3) is met on its
   rows. NULL_TWIN meets success iff S1,S2,S3 are met on its rows (c=0.5).
5. Horizon 20 = 20 backward applications of z <- exp(-q/lam) * P z from
   z_H = 1 (no terminal cost); z_0 is measured.
6. Where the spec gives no value (passive dynamics, cost distributions,
   term scaling, laziness 0.5) the values above were chosen before any
   run and are not changed after.
7. Outcome precedence (phase 2): positive or cheat not detected ->
   INSTRUMENT_FAIL; else null twin meets success -> CONFOUNDED; else
   treatment success and not failure -> SIGNAL; else NULL (round-1: NULL
   includes "meets failure_criterion").

## Seeds

Seed s in 0..9: world rng = numpy default_rng(1000 + s) (P, q_i, u);
shuffle rng = default_rng(5000 + 100*s + 10*r + (c==2)); cheat rng =
default_rng(9000 + 100*s + 10*r + (c==2)).

## Log
- attempt 1 pilot (cpu 6.2 s): FAIL. positive_meets_success=false,
  cheat_detected=false, null_twin_meets_success=false. Cause: the tanh
  control as read (tanh(V/sd(V)), no centering) saturates: V carries a
  large positive offset (~20 steps of cost) with mean/sd >> 1, so tanh(.)
  == 1.0 in float64 for every entry and bond(tanh) = 1 in EVERY arm; S2
  (bond(z) <= bond(tanh) - 1) is then unattainable by construction.
  Positive control own condition held (z rank 1, V rank 2 at 1e-6, all
  seeds, all lambda). S1 and S3 were detected on the cheat. Rows kept as
  pilot_rows_attempt1.jsonl / PILOT_attempt1.json.
- REPAIR (the one allowed, controls only, thresholds unchanged): tanh
  control := tanh((V - mean V) / sd(V)), i.e. the matched monotone
  transform is applied to the centred value so it has dynamic range. No
  other change. No treatment code or statistic existed at this point.
- attempt 2 pilot (cpu 7.8 s): PASS. positive_meets_success=true
  (z rank 1 / V rank 2 exact; S1 10/10, S2 10/10 per lambda>=1 cell),
  cheat_detected=true (S1,S2,S3 all met, rho=1), null_twin_meets_success=
  false (bond z ~36 = bond V; S1 0/10). Phase 2 may start.
- phase 2 (world.py cpu 17.2 s, single attempt, no parameter change):
  outcome NULL (see OUTCOME.json). Total ~0.52 core-minutes.
