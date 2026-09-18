# Preregistration: swarm damage-boundary toys S1-S4 (Aphrodite, 2026-09-18)

Committed BEFORE any S1-S4 code was written. Directive:
roles/Aphrodite/prompts/2026-09-18_rsi_library/OPERATOR_DIRECTIVE.md
("build additional toys to find the damage boundaries of swarms, model
it"; "can small weak models actually be used?").

## What these are

A DAMAGE BOUNDARY is the parameter surface on which adding agents,
samples, readers or generations stops helping and starts hurting. Each
toy pairs an ANALYTIC MODEL, stated here before code, with a stdlib-only
stochastic simulation that measures where the boundary actually lies.
The model is the prediction; the simulation is the test. Where a model
is solved numerically (S2b, S3 persistence, S4 herding), the numerical
method is fixed here and implemented in a separate models.py that never
reads simulation output.

Honesty clause, as in E1-E4: these are near-analytic toys. A match shows
our models and instruments agree; it is calibration for the questions in
library/QUESTIONS.md, not evidence about any real swarm. The value is a
set of boundary formulas with stated preconditions that a real swarm
experiment can later falsify.

Common rules: fixed seeds; rows to ledgers/; verdicts from rows by a
committed analysis step; a 95% CI straddling a gate -> INDETERMINATE
(bootstrap seed 12345, 2000 resamples, or the exact binomial SE where
stated). Positive, negative and cheat controls per toy as pytest tests,
passing before results are read. Eligibility is stated per hypothesis
(the seat's calibration row of 2026-09-17).

## S1 -- Contagion of a false claim through a trust network

Model. N agents; each agent's output is read by d others chosen
uniformly at random (out-degree d, in-degree ~ Poisson(d)). A reader
that receives a false claim adopts it with probability tau (trust)
unless its own verifier catches it (probability v). Per-edge
transmission p = tau (1 - v); R0 = d p. One initial false agent.
  Outbreak probability (branching process, Binomial(d, p) offspring):
    1 - s, where s is the smallest root of s = (1 - p + p s)^d.
  Final contaminated fraction, given a major outbreak:
    z solving z = 1 - exp(-R0 z).
  Damage boundary: R0 = 1, i.e. required verification
    v* = 1 - 1/(d tau). Every extra reader raises v*.
Grid: N = 2000; d in {2, 4, 8}; tau in {0.25, 0.5, 0.75, 1.0}; v in
{0.00, 0.05, ..., 1.00}; 400 runs per cell. "Major" = final size > 5%
of N.
H-S1a: for every cell with R0 <= 0.8, P(major) <= 0.05.
H-S1b: for every cell with R0 >= 1.2, |P(major) - (1 - s)| <= 0.07.
H-S1c: for every cell with R0 >= 1.2, |mean final fraction given
       major - z| <= 0.05.
Eligibility: 400 runs give SE(P(major)) <= 0.025, so 0.07 is ~2.8 SE.
Cells with R0 in (0.8, 1.2) are the finite-size window and
carry no gate; reported only. Cells with R0 = 0 excluded from H-S1a
counting as trivially satisfied (reported).

## S2 -- Can small weak models be used? Generate-and-verify precision

S2a (binary verifier). A weak proposer's sample is correct with
probability p. The verifier accepts a correct sample with probability t
and a wrong one with probability q (false accept). The swarm samples
until the first acceptance, budget k.
  Precision of an accepted answer: P = p t / (p t + (1 - p) q),
    INDEPENDENT of k.
  Damage boundary: P < 0.5 iff p < q / (t + q). A weak model is usable
    in this loop only while its solve rate exceeds roughly the
    verifier's false-accept rate; more samples never fix precision.
Grid: p in {0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4}; q in {0, 0.005,
0.01, 0.02, 0.05, 0.1}; t in {1.0, 0.8}; k in {1, 10, 100, 5000};
4000 trials per cell.
H-S2a1: in every cell with >= 400 accepted trials, |precision - P| <=
        max(0.03, 3 SE), SE = sqrt(P (1 - P) / accepted).
H-S2a2: for each (p, q, t), any two k values with >= 400 accepted trials
        differ in precision by <= max(0.04, 3 SE_diff), SE_diff the
        root-sum-square of the two binomial SEs at P.
Eligibility (computed before freezing): at ~400 accepted trials and
P = 0.5 one SE is 0.025, so a fixed 0.03 would be ~1.2 SE; hence 3 SE.

S2b (scored best-of-k with an exploitable tail). Sample k answers; pick
the highest-scoring. Scores: correct ~ N(1, 1); ordinary wrong ~ N(0,
1); a fraction h of wrong answers are "hacks" scoring ~ N(3, 1). p = 0.1.
  Model: accuracy(k) = k * integral p phi(s - 1) F(s)^(k-1) ds with
    F(s) = p Phi(s - 1) + (1 - p)(1 - h) Phi(s) + (1 - p) h Phi(s - 3),
    evaluated by trapezoid rule on [-8, 12], step 0.001.
Grid: h in {0, 0.001, 0.01, 0.05}; k in {1, 2, 4, ..., 1024}; 4000
trials per cell.
H-S2b1: |simulated accuracy - model| <= 0.025 in every cell.
H-S2b2: h = 0: simulated accuracy never falls by more than 0.03 from
        one k to the next (non-decreasing within noise; one step's SE of
        the difference is <= 0.011, so 0.03 is ~2.7 SE).
H-S2b3: h in {0.01, 0.05}: the model's argmax k* < 1024 and simulated
        accuracy at k = 1024 is below simulated accuracy at k* by >= 0.1.
        (Damage boundary: past k*, more samples of a weak model make the
        swarm worse.)

## S3 -- Exploiters in a self-improving population, and persistence

Model. Population M; honest improvers have true fitness 1. An evaluator
hole gives exploiters reported fitness 1 + g; an auditor inspects each
individual per generation with probability a, and an inspected exploiter
reports 0. Fitness-proportional Wright-Fisher selection; one-way mutation
honest -> exploiter at rate mu = 0.005.
  Invasion iff (1 - a)(1 + g) > 1, i.e. boundary a* = g / (1 + g).
Grid: M = 200; g in {0.1, 0.25, 0.5}; a in {0.00, 0.02, ..., 0.60};
T = 300 generations; 100 runs per cell.
H-S3a: for each g, the audit rate at which the mean final exploiter
       fraction (averaged over runs) first falls below 0.5, scanning a
       upward, lies within +-0.04 of a*.
Persistence arm ("contamination persisting through clean evolution").
200 generations at a = 0, g = 0.5 (exploiters dominate); then the hole
is fixed: g = 0, and exploiters carry a true cost c in {0, 0.02, 0.1}
(reported fitness 1 - c); mutation continues. 300 more generations, 100
runs per c.
  Model: deterministic recursion. Selection x_s = x (1 - c) / (1 - c x),
    then mutation x' = x_s + mu (1 - x_s). Iterated from the measured
    mean fraction at the fix.
H-S3b: c = 0: exploiter fraction at the end is >= 0.8 in >= 90% of runs
       (the exploit PERSISTS when it carries no true cost).
H-S3c: c = 0.1: the median generation at which a run first falls to
       half its fraction at the fix is within +-25% of the model's.
H-S3d: c = 0.02: reported against the model's equilibrium (roughly
       mu / c = 0.25), no gate: the balance point is near "half", so a
       half-life is ill-defined there.

## S4 -- Correlated voting and herding: when do more agents hurt?

Model A (independent with a common shock). n agents vote on a binary
question; with probability rho all copy one shared signal (correct w.p.
p), otherwise each votes independently correct w.p. p. Majority (n odd).
  A(n) = rho p + (1 - rho) Cond(n, p), Cond = P(Binomial(n, p) > n/2).
  Damage boundary: for p < 0.5, A(n) DECREASES with n (more agents
  hurt); for p > 0.5 it rises to the cap rho p + (1 - rho).
Model B (herding: agents act in sequence and see all earlier actions;
each has a private signal correct w.p. p; Bayesian with the tie rule
"follow your own signal"; a cascade starts when the action difference
reaches 2). Exact Markov chain on the action difference computes the
probability the last of n agents is correct.
Grid: p in {0.4, 0.45, 0.55, 0.6, 0.7}; n in {1, 3, 9, 27, 81}; rho in
{0, 0.2, 0.5}; 20000 trials per cell.
H-S4a: model A vs simulation: |diff| <= 0.015 in every cell.
H-S4b: for p in {0.4, 0.45}, simulated A(81) < A(1) - 0.05 for rho = 0
       (more agents hurt).
H-S4c: herding (p in {0.55, 0.6, 0.7} only: below 0.5 a Bayesian agent
       would invert its signal, so the model does not apply): simulated
       accuracy of agent n = 81 within 0.015 of the Markov chain; and for p = 0.7, herding accuracy at
       n = 81 is below independent (rho = 0) majority accuracy at n = 81
       by >= 0.1. Visibility converts a Condorcet gain into a cap.
Not a gate: whether the closed form p(p+1) / (2(1 - p + p^2)) equals the
chain's limit (a check of the seat's recall, reported either way).

## What would falsify the seat's reading

"Swarm damage is governed by a few ratios -- transmission R0 against
verification, solve rate against false-accept rate, exploit gain
against audit rate, and signal quality against visibility/correlation"
is falsified by any toy whose simulated boundary misses its model's by
more than its stated tolerance with the controls green. In that case the
model, not the swarm, is the thing that was wrong, and it is reported so.
