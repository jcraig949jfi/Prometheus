# S6 natural induction -- PREREGISTRATION (frozen before any run; not edited after)

Date: 2026-09-27. Odysseus spike worker. Source: NEWLENS.md L2; raw/E5 PART 3 L7.
Target result: Watson, Buckley, Mills 2011 (Complexity 16(5)) "Optimization in
self-modelling complex adaptive systems": a Hopfield-like network that is
repeatedly reset and relaxed, with slow Hebbian change of its couplings, comes to
reach lower-energy minima of its ORIGINAL couplings. Protocol reconstructed from
memory of the paper (no web check at prereg time): N units s_i in {-1,+1},
original couplings W0 (the "constraints"), learned couplings WL (start 0), state
dynamics on W0+WL, Hebbian dWL_ij = delta*s_i*s_j, random reset every tau steps,
energy scored on W0 only. Paper used a modular W0 (strong intra-module, weak
inter-module) so that single-flip relaxation cannot reorganise modules.

## Problem families (instances generated from fixed seeds)
F_SK : N=50, W0_ij = +/-1 (p=1/2) symmetric, zero diagonal.
F_MOD: N=60 = 12 modules x 5 units. Intra-module W0_ij = +1. Inter-module
       W0_ij = 0.05 * c_AB with c_AB = +/-1 per module pair (a 12-"superspin"
       SK problem). Ground state E0 computed exactly by enumerating the 2^12
       module-consistent configurations (and checked: no mixed state is lower,
       since each broken intra bond costs 1 > max inter gain; recorded as an
       assumption with a numeric check in toy.py).
Energy E0(s) = -sum_{i<j} W0_ij s_i s_j.
Main seeds: 5 instances per family (seeds 1..5). Pilot seed: 999 (not in main).

## Dynamics (one "reset")
Random s. Up to T=10 asynchronous sweeps (random order, fresh per sweep),
s_i <- sign(h_i), h_i = sum_j (W0+WL)_ij s_j, tie keeps s_i. After EVERY
sweep (including sweeps after convergence -- a converged state is cheaply
"idled" for the remaining sweeps), yield: WL_ij += delta * y_i y_j (i != j),
where y is the yield input (y = s for natural induction). No clipping.
R = 1000 resets per learning run; checkpoints at R = 100, 300, 1000.

## Evaluation (primary metric, identical inits across conditions: paired)
Freeze WL. 100 random inits (eval seed fixed per instance). Each: relax on
W0+WL to convergence (max 50 sweeps), then POLISH: relax on W0 alone to
convergence (max 50 sweeps), so every scored state is a true single-flip local
minimum of the original problem. M = mean E0 over the 100 polished states.
Secondary: mean E0 before polish; fraction of evals reaching the ground state
(F_MOD, exact) or the best-known E0 (F_SK: min over everything run on that
instance); SD_noyield = SD of E0 over the 100 no-yield evals.

## Conditions
NI         : y = s (own visited states), delta in grid {1e-4, 3e-4, 1e-3, 3e-3}.
C_noyield  : delta = 0 (evaluation = plain relaxation on W0).
C_anti     : dWL = -delta * s_i s_j (sign reversed), own states.
C_shuf_oth : yield on the state sequence visited by the primary-delta NI run
             on a DIFFERENT instance (instance k uses instance k+1 mod 5);
             the system's own dynamics still run on W0+WL, but WL is driven by
             the foreign states.
C_shuf_perm: y = pi(s), unit labels permuted by a fresh random permutation
             each reset (own states, same activity statistics, correlation
             with W0 destroyed).
A_fast     : timescale separation removed: delta = 0.1 (one reset's yield
             T*delta = 1 = |W0| scale), R = 1000.
A_noreset  : repeated reset removed: one random init, then R*T sweeps of
             relaxation+yield with no reset (same total yield budget).
A_nodiss   : dissipation/relaxation removed: every sweep the state is a fresh
             random vector (no relaxation), yield on it (same budget).
Reference  : best-of-1000 plain relaxations on W0 (equal-count baseline),
             reported only, not in decision rules.
Controls and ablations run at the primary delta (except A_fast), R=1000.

## Primary delta selection (the only tuning)
Pilot on seed 999 per family: NI at each grid delta, R=1000; primary delta =
the one with lowest M (ties -> smaller). Chosen before main runs; recorded.

## Decision rules (per family, primary delta, R=1000, 5 main seeds)
D1: M_NI < M_noyield in >= 4/5 seeds AND median over seeds of
    (M_noyield - M_NI)/SD_noyield >= 0.5.
D2: M_NI < M_anti in >= 4/5 seeds.
D3: M_NI < M_shuf_oth AND M_NI < M_shuf_perm in >= 4/5 seeds.
REPRODUCED = D1 & D2 & D3. PARTIAL = D1 but not (D2 & D3). NOT REPRODUCED = not D1.
The headline verdict is F_MOD (the paper's setting); F_SK is reported alongside.

Ablations: with G = median over seeds of (M_noyield - M_NI) and
G_x = median of (M_noyield - M_x): ingredient x "carries" the effect if
G_x <= 0.25*G; "partially needed" if 0.25*G < G_x <= 0.75*G; "not needed"
if G_x > 0.75*G. (Only interpreted if D1 holds.)
Sensitivity (delta x R grid): reported as a table, no decision rule.

## Budget
Stdlib Python, multiprocessing (4 workers), target < 20 min wall.
If over budget, reduce R to 600 and report it; no other changes.
