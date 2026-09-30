# HT-2a8a3aedeb / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Sources read: PREREG, program.json W4, M4, M13, L4. Nothing else.

## World (substrate: tensor, 3 modes x 5 levels = 125 states)

Linearly solvable MDP (Todorov) in first-exit form with a uniform exit.
- Passive dynamics: modes move independently, P = kron(P1,P2,P3), state
  index s = (i1,i2,i3) in C order (matches reshape(5,5,5)). Each P_m is a
  lazy biased walk on 5 levels: stay 0.5, right 0.5*r_m, left
  0.5*(1-r_m), blocked moves at the boundary become stay; r_m ~ U(0.2,0.8)
  per mode per seed. Chosen so dynamics are NOT near-uniform (stupid
  explanation 2); per-mode second eigenvalue is recorded in rows.
- Exit: from every state the passive chain exits with probability
  pe = 0.1 to an absorbing state of terminal cost 0 (desirability 1);
  interior passive kernel is (1-pe) P. pe = 0.1 gives an expected
  horizon of 10 steps, comparable to the grid diameter (12 steps). Spec
  gives no horizon; this is my choice, fixed now.
- Goal = state cost q(s) > 0. Desirability z solves the linear Bellman
  equation  z = exp(-q) * ((1-pe) P z + pe)  i.e.  A z = b with
  A = I - diag(exp(-q))(1-pe)P, b = pe exp(-q).  Exact solve (125x125).

## Goals (in-span / orthogonal)

Per seed and mode m: F_m = 2 random orthonormal vectors orthogonal to the
constant vector (ground-truth shared factors); O_m = orthonormal basis of
the 2-dim complement of span(1, F_m). A goal is
  g = core x1 V1 x2 V2 x3 V3, core ~ N(0,1)^(2x2x2), g /= max|g|,
  q = 1 + 0.9 g   (so q in [0.1, 1.9]).
Training goals (10) and in-span test goals (5) use V = F; orthogonal test
goals (5) use V = O. Each goal has its own random core.
Ambiguity: the spec does not say whether "in-span"/"orthogonal" refers to
cost or desirability factors. Reading chosen: goals are generated in COST
space from shared vs orthogonal per-mode factors; desirability is then the
exact LMDP solution (nonlinear in q), and the HOSVD is on desirabilities
as the spec says. Consequence recorded: orthogonality is by construction
in cost space (see stupid explanation 3).

## Mechanism -> code

- Galerkin restriction: B = kron(U1,U2,U3) (125 x 8, K = 2 per mode,
  columns orthonormal). Solve (B^T A B) c = B^T b, z_hat = B c.
- Policy: u(s'|s) prop. to (1-pe)P(s'|s) z_hat(s') for interior s',
  u(exit|s) prop. to pe * 1. Ambiguity: z_hat may be <= 0. Reading:
  z_hat is floored at 1e-12 * max(z_hat); if max(z_hat) <= 0 the passive
  policy is used. Count of floored entries recorded per rule.
- Observable: policy cost v solves v = q + KL(u(.|s)||p(.|s)) +
  sum_{s' interior} u(s'|s) v(s') (exact linear solve). J = mean of v
  over a uniform start distribution; J* = mean(-log z*). Relative regret
  = (J - J*)/J*. Sanity: evaluating the exact optimal policy must give J*
  (checked; mismatch recorded as anomaly).

## Intervention (subspace rules), K = 2 per mode

(a) HOSVD: stack training desirabilities into T (10 x 5 x 5 x 5); for
    state mode m, U_m = top-2 left singular vectors of the mode-m
    unfolding. No centering (plain HOSVD).
(b) Prediction: U_m = right eigenvectors of P_m with the 2 largest
    eigenvalues (functions on levels, the space z lives in; P_m is a
    birth-death chain so eigenvalues are real), orthonormalised by QR.
(c) Random: U_m = QR of a 5x2 Gaussian matrix, one draw per seed.

## Arms (each row = one (arm, seed); all arms share the seed's world)

Every row carries regrets of rules a, b, c on all test goals. The arm
defines which "candidate" subspace is compared with (b) in the criterion:
- TREATMENT: candidate = (a).
- CONTROL: candidate = (c) random (spec: "rule (c) random subspace of
  same K"). Reading: the control is the criterion applied with (c) in
  place of (a).
- NULL_TWIN: candidate = HOSVD of training desirabilities where, per
  goal and per mode, the level index is permuted by an independent random
  permutation (keeps each goal's mode spectra; destroys shared factors).
- POSITIVE_CONTROL: test goals = 5 of the training goals (goals 0..4);
  rule (a) regret recorded. Spec threshold: relative regret < 1e-3.
- CHEAT: the TREATMENT observables with success written directly into
  them: regret_a := regret_b / 10 on in-span goals and
  regret_a := regret_b * 10 on orthogonal goals (bypasses the mechanism).

## Criteria as applied (thresholds unchanged)

Per seed, with med = median over the 5 goals of the group:
  in_ratio  = med(regret_b, in-span) / med(regret_cand, in-span)
  off_ratio = med(regret_cand, orth) / med(regret_b, orth)
Ambiguity: "median regret (b)/(a)" read as ratio of medians (not median
of per-goal ratios); median of per-goal ratios is also reported, not
used.
- seed success: in_ratio >= 2 AND off_ratio >= 1.2.
- SUCCESS (arm): seed success in >= 7 of 10 seeds.
- FAILURE: in_ratio < 2 in >= 5/10 seeds, OR "no reversal" in >= 5/10
  seeds, where no reversal is read as off_ratio <= 1 (candidate not worse
  than (b) off-span).
- Positive control detected: rule-(a) median regret over the 5 training
  goals < 1e-3 in >= 7/10 seeds (mirrors the success count rule; spec
  gives no count).
- Cheat detected: CHEAT rows meet SUCCESS.
- Null twin meets success: NULL_TWIN rows meet SUCCESS.
Outcome (PREREG classes, in this order): INSTRUMENT_FAIL if PC or cheat
not detected; else CONFOUNDED if null twin meets success; else SIGNAL if
treatment meets success; else NULL.

## Seeds, compute

Seeds 0..9 (spec: 10 seeds); numpy default_rng(seed) for the world,
separate child streams per component. Compute measured with
time.process_time in world.py and recorded in every row; budget 10 CPU
core-minutes; expected well under 1.

## Stupid explanations, as this run can address them

1. "orthogonal goals chosen to be hard for everyone": regrets of a, b, c
   are reported in-span and off-span; relative regret normalises by J*.
2. "prediction subspace poor due to near-uniform dynamics": dynamics
   are biased lazy walks; per-mode 2nd eigenvalue and bias recorded.
3. "crossover is built into the construction": NOT addressable here:
   orthogonal goals are orthogonal to the training factors by design.

## Attempt log and the one instrument repair (appended after attempt 1)

Attempt 1 (world run once, RC 0). evaluate.py first crashed on a Python
syntax error (keyword argument named `n_seeds_below_1e-3`); renamed to
`n_seeds_below_threshold`, no logic change, evaluator re-run on the same
rows. Result: INSTRUMENT_FAIL -- POSITIVE_CONTROL not detected (rule-(a)
median regret on training goals 2.9e-3 .. 7.3e-3 per seed, 0/10 below
1e-3); CHEAT detected (10/10). The TREATMENT numbers were visible to me
at this point (median in_ratio 1.05, off_ratio 1.03); this is disclosed.
The 5733 floored z_hat entries were all in rule (c) (random), none in
a/b/null.

Diagnosis (instrument defect, not a parameter choice): I built the shared
factors F_m orthogonal to the constant vector, yet every goal cost has a
constant offset (q = 1 + 0.9 g). Each goal's cost therefore spans THREE
per-mode directions (constant + 2 shared) while the spec fixes K = 2, so
no K = 2 subspace can hold even a training goal, and the spec's
positive control (training goal, rule (a) regret < 1e-3) could not pass
by construction. That contradicts the spec's premise that the training
goals share K = 2 factors per mode.

Repair (the ONE allowed): per mode, the shared factor set is
F_m = [constant/sqrt(5), one random unit vector orthogonal to it]
(2 dims = K), and O_m = 2 orthonormal directions from the 3-dim
complement of span(F_m). Goal costs unchanged in form
(q = 1 + 0.9 g, g = core x V, V = F or O), so the offset now lies inside
the shared span and orthogonal goals differ from shared ones only in
their non-constant factors. Every other parameter, seed, threshold,
criterion reading and arm definition is unchanged. Attempt 2 reruns all
arms once; its outcome stands whatever it is (a second INSTRUMENT_FAIL
-> NOT_BUILT per PREREG).
