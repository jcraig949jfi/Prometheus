# D15A_TRACKB1_FREEZE — construct the missing middle

Harmonia A · 2026-09-02 · Frozen BEFORE any Z_8xZ_8 world is generated.
R-A approved: six-rung ladder retained; substrate enlarged; NOTHING
else moves. E1/E2/E3, probe semantics, firewall, policies, warrant
endpoint, engine pin (5274ddbe), depth-1 forks, A3 replay: all frozen
as in D15A_REPAIR_EQUIVALENCE_V2.md and the Phase-0 record. Cost stays
OUT of E2 (capability+soundness only); cost distinctions remain E3.

## Substrate order (frozen)
1. Z_8 x Z_8 (64 states). 2. Z_6^3 (216) ONLY if Z_8x8 fails robustly.
Stop at the smallest working substrate. No escalation for prettier
geometry. The operator family is the same op-shape set lifted
mechanically to mod-8 (shifts k=1..3, swap, reflections, diagonal
shears, + pairwise compositions to ~26 distinct permutations), the
only change dimensional lifting requires.

## I2 criterion (frozen BEFORE generation)
A world is I2 iff, under the SAME frozen greedy min-probe cost
estimator used for every rung (identical code, identical accounting,
probe cap 8):
    finite(C_passive)  [probe pool = N, navigation-reachable]
    finite(C_active)   [probe pool = O, any observable]
    C_active < C_passive
Rung membership comes from this exact oracle-side structure, never
from any learned policy's performance. Retention bands:
    n(I2) >= 40 retained worlds; population-level advantage
    median(dC) >= 1 with dC = C_passive - C_active reported as the
    complete paired distribution (C_p, C_a, dC per world).

## Gradient requirement (anti-"magic probe", frozen)
Per I2 world measure: |V0|, H0 = log2|V0|, C_passive, C_active, best
single-probe class-collapse gain, median legal-probe gain, number of
discriminating probes. MAGIC_PROBE flag: best single probe already
collapses |V0| -> 1. Honesty band: if MAGIC_PROBE fraction > 0.5 of
retained I2 worlds, I2 must be reported as "I1 in softer clothing"
and D15A_TRACKB1_I2 = NOT_READY regardless of the cost criterion.
Gradient band: fraction of I2 worlds with >= 3 discriminating probes
of unequal gain >= 0.5.

## Probe orthogonality (frozen)
Per probe s in O, measured at V0: dH_repair = log2|V0| - log2|V({s})|
and goal_progress bit (s in N AND s on a shortest-T-path frontier
toward G, unchanged semantics). Factorial cells:
    INFORMATION_ONLY dH>0, goal=0 | GOAL_ONLY dH=0, goal=1
    MIXED            dH>0, goal=1 | NULL      dH=0, goal=0
READY band: across retained I2+I3+I4 worlds, INFORMATION_ONLY cell
populated in >= 50% of worlds AND GOAL_ONLY cell populated in >= 50%;
report full per-rung cell counts. If either cell cannot be populated,
D15A_TRACKB1_ORTHOGONALITY = NOT_READY.

## Matched-difficulty qualification (frozen)
Difficulty features per world: baseline_search_cost = shortest-path
length x0->G under T u {h} (post-repair solve cost); reach_frac =
|N|/|S|; solver_density = |U|/|R|; target_burden = |G|. Common-support
matching: worlds w_A (rung A), w_B (rung B) MATCH iff
|reach_frac diff| <= 0.10 AND |baseline_search_cost diff| <= 1 AND
|solver_density diff| <= 0.15 AND same target_burden. READY band:
>= 30 matched cross-rung pairs for EACH key contrast
(I0 vs I5, I2 vs I3, I1 vs I3), demonstrating "similarly difficult to
navigate, materially different in what can be learned."

## Substrate-size confound attack (frozen)
(a) Same estimator, same accounting on both substrates; Z_6^2 numbers
from Track B stand as comparator. (b) For each retained I2 world,
record WHERE the active advantage comes from: the first greedy active
probe's membership in O\N, and the count of discriminating probes
inside vs outside N. INFORMATION-advantage band: >= 80% of retained
I2 worlds must draw their first active probe from O\N while passive
identification remains finite via in-N discriminators — i.e. the gap
is access to discriminating observations, not compute. (c) Anchor
drift check: I3's C_active == C_passive equality must persist on
Z_8x8 (the graded gap must NOT appear in the rung defined not to have
it).

## Anchor retention (frozen)
Re-census I0/I1/I3/I4/I5 on Z_8x8 with unchanged acceptance filters:
I0 zero-info retained (full-observable probing shrinks nothing);
I1 passive=infinite/active-finite retained; I5 |V0|=1 with E1/E2 >= 3
retained; all-rung E1/E2 median >= 3; master-key <= 0.15. Any anchor
broken by enlargement = redesign FAILS (report, do not rescue).

## Return gate (frozen)
Five separate verdicts, each READY/NOT_READY, no collapsing:
D15A_TRACKB1_I2 · D15A_TRACKB1_ORTHOGONALITY ·
D15A_TRACKB1_DIFFICULTY_MATCH · D15A_TRACKB1_FULL_GENERATOR ·
D15A_TRACKB1_INSTRUMENT. Confirmatory science stays forbidden unless
ALL are READY. A robust negative (no honest I2 without breaking
anchors or importing a difficulty confound) is a RESULT to return,
not a failure to rescue.

## Topology-2 (per brief §10)
Marked ABANDONED_PARTIAL_RUN_ENGINE_DISCONTINUITY. The 6/90-cell
partial run under pin e367e791 is permanently non-resumable across
the release boundary; artifacts preserved as historical evidence at
genesis/harmonia_a/sfe_gen2/results/. No restart during Track B.1.
