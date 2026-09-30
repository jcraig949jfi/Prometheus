# HT-974471f045 / W3 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...bea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec read: W3, mechanism M7, lenses L2, L7 only.

## Spec field -> code

- hypothesis: "bracketing of distractor channels evolves when readout budget
  is small (k=3) but not when large (k=50)". Tested by evolving masks at
  k=3 and k=50 and comparing the masked distractor fraction.
- mechanism: genome = binary mask m in {0,1}^8 multiplying the 8 input
  channels before a FIXED echo state network (N=50). Channels 0,1 are
  informative (std 1), channels 2..7 are distractors (std 3, "high variance",
  independent of the target). Readout = ridge regression on k fixed taps
  (reservoir units 0..k-1), trained within each fitness evaluation.
- intervention: k in {3, 50}; 60 generations (`world.py: run_evolution`).
- control: CONTROL arm, mask fixed to all-ones, no evolution; NRMSE at each
  k is recorded; masked fraction is 0 by construction.
- positive_control: hand mask [1,1,0,0,0,0,0,0] vs all-ones at k=3; the
  relative NRMSE gain (nrmse_ones - nrmse_hand)/nrmse_ones is computed per
  seed; DETECTED iff the mean over 8 seeds >= 0.10 ("beat by >= 10% NRMSE"
  read as a 10% relative reduction). Also recorded at k=50 (for stupid
  explanation 2), not used for detection.
- null_twin: NULL_TWIN arm, identical to TREATMENT (same k, channels,
  reservoir, data, seed) except that each generation the fitness vector is
  randomly permuted among individuals before selection (lens L7).
- observable: fraction of the 6 distractor bits equal to 0, averaged over
  the elite genomes (top 6 by the fitness used for selection, i.e. permuted
  fitness in the twin) of generation 60; per seed; then mean over 8 seeds.
- success_criterion (applied verbatim): mean_k3 >= 0.8 AND mean_k50 <= 0.4
  AND (mean_k3 - mean_twin_k3) >= 0.3, means over 8 seeds.
- failure_criterion: |mean_k3 - mean_k50| < 0.2 (recorded; per PREREG, NULL
  if treatment fails success OR meets failure).

## Ambiguities and the reading chosen

1. "k taps": which k reservoir units. Reading: fixed, the first k units
   (reservoir is random, so this is an arbitrary fixed subset). k=50 = all.
   Input is not a tap (readout sees reservoir states only) plus a bias term.
2. Task: not given. Chosen a priori: y(t) = 0.6*u0(t-1) + 0.4*u1(t-2),
   linear with short memory so the reservoir is needed. Channels i.i.d.
   Gaussian per step.
3. "elite genomes": the top 6 (20%) of 30 by selection fitness at gen 60.
4. Evolution: elitist truncation. Keep 6 elites; 24 offspring = copy of a
   uniformly chosen elite with each bit flipped with p=1/8 (SYMMETRIC flip,
   no bias to 0). Initial masks Bernoulli(0.5). 60 generations of
   evaluation+selection; observable taken from the gen-60 evaluated pop.
5. Fitness = -NRMSE on a held-out test segment, NRMSE = RMSE/std(y_test).
6. Null twin success reading: the third clause references the twin itself,
   so "null twin meets success criterion" is read as twin_k3 >= 0.8 AND
   twin_k50 <= 0.4 (the two clauses that do not reference the twin).
7. CHEAT: rows whose observable is written directly (k=3 fraction 1.0, k=50
   fraction 0.0) without running evolution; DETECTED iff the success
   criterion evaluated with CHEAT in place of TREATMENT (twin unchanged)
   returns True.

## Parameters (fixed from spec or chosen a priori, not from results)

- population 30, N=50, 8 channels, 60 generations, 8 seeds (spec "size").
- spectral radius 0.9, reservoir density 1 (dense Gaussian), leak 1.0,
  W_in ~ U[-0.2,0.2] (N x 8), bias input 0. Generic ESN defaults.
- informative std 1, distractor std 3.
- T: washout 100, train 600, test 300 steps. ridge lambda 1e-4.
- Data, reservoir and W_in fixed per seed (drawn from seed); evolution RNG
  from seed too; twin uses the same seed and a separate permutation stream.
- Seeds 0..7 for every arm.

## Outcome logic (evaluate.py, from PREREG)

INSTRUMENT_FAIL if not (pc_detected and cheat_detected); else CONFOUNDED if
null twin meets success; else SIGNAL if treatment meets success (and not
failure); else NULL.

## Budget

Estimated well below 10 core-minutes (population batched per step). Measured
with process CPU time and written to rows / OUTCOME.

## Post-run record (appended after attempt 1; nothing above changed)

Attempt 1 ran to completion (1.03 CPU core-minutes, single thread); no
crash, no rerun, no parameter change. Outcome NULL: treatment masked all
distractors at BOTH k=3 and k=50 (mean 1.0 each, 8 seeds), meeting the
failure criterion (difference 0.0 < 0.2). Observed, not interpreted
further: at k=3 the elites kept informative channels only 56% of the time
(elite NRMSE 0.81 vs all-ones 1.00), so k=3 fixed taps barely solve the
task; the hand mask helped far more at k=50 (rel. gain 0.90) than at k=3
(0.11), i.e. the stated alternative explanation (masking selected wherever
distractors add noise) is what these rows show.
