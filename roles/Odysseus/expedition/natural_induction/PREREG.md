# Natural induction -- ADVERSARIAL PROGRAM -- PREREGISTRATION

Frozen 2026-09-28 before the main run. It is not edited after the run; any
later change is logged in RESULT.md as a deviation. All results are
EXPLORATORY (small N, 5 training instances per family, toy model).

Author: Odysseus disposable research worker. Directive: 01_OPERATOR_DIRECTIVE
section 9. Base toy: frontier/poi/spikes/S6_natural_induction (toy.py
dynamics, yield and evaluation copied verbatim into ni_adv.py).

Only run before freezing: a timing smoke (`ni_adv.py smoke`) on pilot seed
999 at R=200, MOD family. It printed timings plus one SA energy (-150.0,
against a ground of -152.5). No decision-relevant quantity was inspected.

## 0. What is being attacked

Claim C_L ("learning rule nobody installed"): reset + relax + slow Hebbian
yield gives the system a learned inductive bias. That bias generalises
beyond the specific minima it has experienced.

Rival C_M ("attractor reshaping / memory of visited minima"): the yield only
stores the minima that relaxation visits. Mathematically,
WL = delta * sum_t s(t)s(t)^T is exactly a Hopfield memory of the visited
states. Under C_M the improvement is recall and re-weighting of those states,
and nothing reusable transfers to an instance whose good minima differ.

## 1. Families, instances, seeds

- MOD: N=60, 12 modules x 5 units, intra-module +1, inter-module
  0.05*c_AB (as in S6). Exact ground state by enumerating 2^12 superspins.
  Yield rate delta=3e-4. This is S6's post-hoc rate, which S6 confirmed on
  fresh seeds; it is not re-tuned here.
- SK: N=50, +/-1. delta=1e-4 (S6's preregistered rate).
- Training instances A: seeds 11-15 per family. These are fresh; S6 used 1-10.
- Transfer targets per A:
  - MOD:
    - B0..B3: same family and same module partition (same unit labels),
      with fresh inter-module signs c_AB. A's ground-state pattern is
      therefore uninformative about B's, but the decomposition is shared.
    - Xperm: MOD with a randomly permuted partition (different structure).
    - Xsk60: a +/-1 SK instance with N=60 (different family).
  - SK:
    - B0..B3: fresh SK instances (same family, no shared structure).
    - P10 and P30: A with 10% or 30% of coupling signs flipped. These are
      related instances, where C_M predicts transfer.

## 2. Systems (all trained on A only)

- NI: reset/relax/yield as in S6 (T=10 sweeps per reset, yield after every
  sweep, idle credit at convergence), R=1000, rate delta.
- NI2: identical to NI but with a different reset/order RNG stream (a
  different history).
- NIslow: delta/3, R=3000 (same yield budget, a different history
  timescale).
- H<eps> (material memory, sign-blind): same reset/relax schedule. After each
  sweep, every bond (i,j) whose two endpoints both flipped in that sweep
  softens multiplicatively: W_ij *= (1-eps). This is history-dependent
  but carries no s_i*s_j sign information. eps in {1e-3, 1e-2, 1e-1}; the best
  on A is used in decisions. Its history-dependence is measured as
  ||W_hist1 - W_hist2||_F / ||W0||_F.
- MEM_x<k> (open-loop "plain parameter adaptation toward visited minima",
  i.e. explicit Hebbian storage): sum of s s^T over the 1000 minima reached
  by plain relaxation on W0_A (visit-frequency weighted, no energy
  weighting, no feedback). Scaled to k * ||WL_NI||_F, with
  k in {0.25, 0.5, 1, 2, 4}.
- SAMEM_x<k> (the "directly optimised couplings" endpoint): Hebbian storage
  of the single state found by simulated annealing on W0_A (Metropolis,
  2000 sweeps, T from 3.0 to 0.05 geometric, then polish). Same scale grid.
- BESTMEM_x<k>: storage of the best-known A state. For MOD this is the exact
  ground state; for SK it is the best of 1000 plain restarts. Same scale
  grid.
- NIblock / NIinter (MOD only, decomposition, descriptive): NI's WL
  restricted to A-partition intra-module entries, or to inter-module
  entries.
- noyield: WL = 0.

For a memory model, the scale "chosen on A" is the k with the lowest M on A
(ties go to the k closest to 1). This choice uses A data only, never B.

## 3. Evaluation (as in S6)

- Freeze the couplings. The 100 random starts are fixed per target and
  shared by all systems (a paired design).
- For each start: relax on W0_target + WL (up to 50 sweeps), then polish on
  W0_target (up to 50 sweeps).
- M = mean E0_target over the 100 polished minima. Lower is better.
- SD0 = SD of the noyield energies on that target (floor 1e-9 -> 1).
- Transfer score of system X on target t:
  z_X(t) = (M_noyield(t) - M_X(t)) / SD0(t). Positive means X helps.

B-experience runs (MOD and SK, all 20 (A,B) pairs):
- scratch: NI on B from WL=0, with checkpoints at R_B = 100, 300 and 1000.
- warm: NI on B starting from WL_A (NI), with checkpoints at R_B = 100 and
  300.
- Both use the same RNG stream and the same eval starts.

## 4. Tests and decision rules

A test is "positive" over the 20 (A,B) same-family pairs if median z >= 0.5
and z > 0 in >= 14/20 pairs. It is "negative" if median z <= -0.5 and z < 0 in
>= 14/20 pairs. Anything else is "none". For the 5-pair cross-family targets
the rule is median >= 0.5 with >= 4/5 (and the mirror for negative).

T1 TRANSFER (per family):
- T1a zero-shot: z_NI(B) over 20 pairs. Label: positive / none / negative.
- T1b limited B experience: d(R_B) = (M_scratch(R_B) - M_warm(R_B)) / SD0(B)
  at R_B = 100 and 300. The label follows the same rule (positive means warm
  start beats scratch). Also reported: the cost in B-resets that the warm
  start saves (descriptive).
- T1c cross-family / other structure: MOD targets Xperm and Xsk60 (5 each).
  SK targets P10 and P30 (5 each; these are related instances).
- T1d comparators on B: the same z statistics for noyield (0 by
  definition), SAMEM, BESTMEM and MEM at the scales chosen on A, plus NI2,
  NIslow and H.

T2 IDENTICAL ENDPOINT, DIFFERENT HISTORY (per family):
- Candidate pairs per A: (NI, NI2), (NI, NIslow), (NI, MEM_x*),
  (NI, SAMEM_x*), (NI, BESTMEM_x*).
- For the memory models, "x*" here is the k whose M_A is closest to NI's
  M_A.
- A pair is endpoint-matched if |M_A(X) - M_A(Y)| <= 0.25 * SD0(A).
- For matched pairs, the history effect on B is
  h = (M_X(B) - M_Y(B)) / SD0(B) over that A's 4 B targets.
- "History matters" for a pair type if median |h| over its matched
  (A,B) pairs >= 0.5. The sign is reported.
- Also reported: the identity of the endpoint. That is the Hamming overlap
  |q| of the modal A-eval minimum between NI and NI2, and between NI and
  NIslow (path dependence of WHICH minimum, at matched quality).

T3 ALTERNATIVES (explicit models; the discriminating statistic for each):
- Annealing (on states, the original energy). Annealing leaves the future
  dynamics unchanged, so after it a fresh start behaves like noyield
  (z = 0 by construction). Statistic: z_NI(A) > 0 with frozen WL and fresh
  starts means "not merely annealing". Also reported: SA's endpoint E
  against NI's eval min and mean.
- Hysteresis / material memory without Hebbian direction (H). Statistic:
  z_H(A) at the best eps, together with its history distance.
  - If H is history-dependent (distance > 0.01) but z_H(A) < 0.5, then
    history-dependence per se does not produce the effect.
- Plain parameter adaptation toward visited minima, open loop (MEM).
  Statistic: ratio rho = median_A z_MEM*(A) / median_A z_NI(A), with the
  scale chosen on A.
  - rho >= 0.75: open-loop memory suffices on A.
  - rho < 0.75: the closed loop (learning shaping which minima are visited
    next) adds something.
- Path dependence: the T2 overlap statistic.
- Attractor reshaping / memory of the best minimum (BESTMEM, SAMEM): the
  same rho statistic.

T4 KILL TEST (single, preregistered; headline family MOD, SK reported):
"learning rule nobody installed" SURVIVES only if BOTH hold on the 20 MOD
(A,B) same-family pairs:
- K1: NI zero-shot transfer is positive. That is, median z_NI(B) >= 0.5 and
  z_NI(B) > 0 in >= 14/20 pairs.
- K2: NI's transfer exceeds that of every memory-of-minima model at its
  A-chosen scale. That is, median over pairs of
  [z_NI(B) - max(z_MEM*(B), z_SAMEM*(B), z_BESTMEM*(B))] >= 0.25.

If K1 or K2 fails, the thread is RETIRED in favour of "attractor reshaping /
memory of visited minima". Rationale: in MOD-B, A's minima carry no
information about B's minima; only the shared decomposition could transfer.
If NI extracted a reusable bias beyond storing minima, it must show it here
and must beat plain storage of A's minima.

## 5. Budget

- Stdlib Python, 4 workers, target under 45 min wall. The machine is shared
  (load ~27 at freeze).
- If a stage overruns, the fallback is to drop A seed 15 (4 A instances,
  16 pairs, with the thresholds scaled to 11/16). Any use of the fallback is
  reported.
