# Tyche v1 report (2026-09-30)

Question (operator v1 directive): can a lens lineage acquire a useful sense
whose necessary precursor components have no individually measurable
utility? PREREG roles/Tyche/prereg/2026-09-30_v1/PREREG.md (282f01c45).
Verdicts computed by tyche/v1/report_v1.py (REPORT_v1.json). Six runs:
arms V0 / DE / DENR x evolutionary seeds 1, 2; equal budget of 6000 units
per world; worlds hash in each CONFIG.json; host M2, clean tree.

## Verdict

GATE 6 = FAIL. All 5 Z worlds were valid in both seeds (initial single
test gain <= 0.018; best of 4560 initial pairs <= 0.061). No Z world had a
DE fused sensor meeting the full predicate while V0 failed.

    Z-world solves (test >= 0.10, replicated), per run:
                 Z1 xor   Z2 xor   Z3 par3  Z4 sign  Z5 wxor   cells
    V0   s1        6        1        0        0        0        2
    V0   s2        0        0        0        1        0        1
    DE   s1        0        0        0        0        0        0
    DE   s2        4        0        0        0        0        1
    DENR s1        1        0        0        0        0        1
    DENR s2        1        0        0        0        0        1
    generations: V0 80/83, DE 36/36, DENR 40/41 (same unit budget)

C and G controls were solved by every arm in both seeds (V0 most often).
Negatives: 0 replicated gains on N worlds in any run; 1 admission at the
conf gate (DENR s1, pair on N1_tsd_Z1, conf z >= 4) killed by Pass D (fresh
seeds +0.011 / -0.007; below its null). Baseline drops > 0.03: 0 in all runs
(the v0 F2 manufactured gap is gone). Capability deficit on negatives
stays 0.00 in every run (the repaired residual has a working negative
control). Z deficits (R0, best organism, test): V0 s1 Z1 0.50 -> 0.00;
DENR s2 Z1 0.50 -> 0.20; DENR s1 Z1 -> 0.30; DE s2 Z1 -> 0.33; Z2 at best
0.33-0.37; Z4 0.46-0.48 throughout.

## Predictions scored (I lost most of them)

    P1 GATE6 PASS on Z1, Z2 in both seeds ........... LOST (FAIL)
    P2 V0 solves C1, C2 both seeds; no Z world ....... C part held; Z part LOST
                                                       (V0 solved 3 Z cells)
    P3 DE solves Z4 both seeds; Z5 <= 1; Z3 none ..... Z4 LOST (0); Z5, Z3 held
    P4 DENR <= half of DE's Z cells .................. LOST (DENR 2, DE 1)
    P5 no N admission; no baseline drop .............. admission LOST (1, killed
                                                       in Pass D); baselines held
    P6 solved Z deficit <= 0.05; N flat .............. held where solved fully
                                                       (V0 s1 Z1 0.00); N held

CORRECTION (2026-09-30, found while designing v2; annotation, original
text kept): the V0 arm was "v0 selection", which INCLUDES v0's 14-slot
dark reserve (2/3 behaviour-signature novelty, 1/3 random, age protection
3). V0 reserve membership was not logged. F1's reading that the Z1 lineage
"survived on noise-level lexicase wins" is therefore an inference from its
best cases being noise-level, not an observation: it may equally have been
carried by the novelty/random reserve. The survival mechanism in v1 is
UNRESOLVED between noisy lexicase and v0's small reserve. v2 separates
them (LEX: lexicase with no reserve; RES: explicit reserve; all
memberships logged).

## Failure shapes

F1 The premise behind the gate did not hold in this implementation: v0-style
   selection did NOT kill zero-utility precursors. Exploratory trace
   (tyche/v1/trace_precursors.py; not preregistered) of V0 s1's best Z1
   solver (L-c4f20eab6d, test +0.281): its first-parent line sat at home
   val gain -0.002..+0.002 from generation 0 to 31, surviving on val
   "gains" of 0.019-0.030 -- mostly on NEGATIVE worlds (N3, N4, N1 twins)
   and Z5, i.e. noise. Epsilon-lexicase over 39 noisy cases is itself a
   random-persistence mechanism: a lens with no real value survives by
   topping some case by chance. At generation 32 a graft brought in a
   lineage valued on C1 (xor with a raw channel, +0.489); at generation 39
   one insertion of delay(ch3, 4) completed the xor (+0.302). Persistence
   by noise plus exaptation from a sibling world, not an explicit reserve.
F2 Soft precursors: a window sum over the missing channel plus the exact
   other delay gave partial joint information (+0.076 on Z1 for an
   ancestor at generation 15). In this chemistry 2-way xor has graded
   footholds; "zero-marginal" holds for exact precursors only.
F3 Explicit preservation + pair evaluation did not beat plain selection at
   equal budget (Z cells: V0 3, DENR 2, DE 1). Pairs cost units, so DE ran
   36 generations against V0's 80.
F4 The directive's mechanism was observed ONCE, below the bar: DE s1 on Z2,
   fused L-07a6707a67 from two lenses whose max individual home val gains
   were 0.004 and 0.006 at every logged evaluation and whose test z alone
   was 2.0 and 1.7 -- replicated (test +0.075, z 5.6; fresh seeds +0.101,
   +0.109; twin z 1.24; pair-null p95 +0.025). It misses the 0.10 test
   threshold, and V0 also solved Z2 in that seed.
F5 "Useful + useless" coalitions are common: a partner with ~0 individual
   value lifted a partial lens from ~0.1 to +0.18-0.21 (DE s2 Z1) and
   completed a full solve (+0.513, DENR s1 Z1).
F6 The real needles: 3-way parity (Z3) and xor of windowed majorities with
   3-op precursors (Z5) were reached by no arm in either seed.

## What this does and does not establish

DOES: the repaired instruments work (no manufactured gaps; deficit flat on
negatives; negatives never replicate); zero-marginal 2-way xor IS reachable
in this chemistry, by several routes; two individually useless lenses can
form a replicated weak sensor (one instance).
DOES NOT: show that explicit preservation is necessary or helpful; show
gate 6. The gate's counterfactual ("precursors would have died under v0
selection") is false for this V0, because noisy many-case lexicase already
preserves useless lineages.

## Successors

S1 Make the counterfactual real: a strictly utility-gated arm (a lens
   survives only with a significant gain on some case, e.g. val z >= 2),
   so "would have died" is true by construction; keep noisy lexicase as
   its own arm (it is an implicit dark ecology worth measuring).
S2 Use the true needles as the gate: parity of order >= 3 (Z3) and deep-
   precursor xor (Z5), with triple coalitions, where F2 ramps are weakest.
S3 Make pair evaluation cheaper (cached lens outputs; organism-free
   screening by mutual-information proxies on the train split) so budget
   parity stops penalising DE.
S4 Quantify F1: fraction of lineage-generations surviving on N-world or
   below-noise cases; this is a measurable "neutral persistence rate".
