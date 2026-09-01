# D6-A FINAL REPORT — BLIND ENDOGENOUS METRIC GENESIS
2026-08-27. All evidence frozen per prereg/PREREG_D6A.md (+ amendments 1–3, all logged
before any Z/M1 evidence). No within-generation rescue was performed after evidence froze.

## MACHINE VERDICT (per preregistered §9 gates, §23 vocabulary)

    ENDOGENOUS_SIGNAL_FOUND

and explicitly **NOT** CAUSAL_FINDABILITY_SIGNAL, NOT FROZEN_SIGNAL_TRANSFER.
Also earned: the battery is valid (V1–V5 pass) and the sparse-feedback wall exists (T-P1).

The central hypothesis — that relational executable history can construct a derived signal
that causally increases exact-solver findability on held-out tasks beyond the artifact
hoard — was **not confirmed** in this generation. The result is a clean preregistered null
with an identified mechanistic bottleneck (see §Interpretation).

## Claim ladder outcomes

| claim | status | evidence |
|---|---|---|
| P0 solvers exist | ✓ | 104/104 constructive witnesses, exact on all 64 rows (runs/battery.json) |
| P1 sparse wall | ✓ | M0: CONF 0.007, tier3 0.000 (0/576 seed-runs), gates V2–V4 pass (runs/m0.log) |
| P2 signals constructed | ✓ | z\* = genome (−1,−1,+1,0 · id · mean · +len) over relational tables; absent initially, exact executable semantics, no human labels; used throughout development |
| P3 causal findability | ✗ | H3−H1 on CONF: +0.010, CI95 [−0.010,+0.042], p=0.49 (needed ≥ +0.20, p<0.01) |
| P4 beyond-hoard | ✗ (moot) | H3−H2 = 0.000; H3−RANDZ = −0.000; no effect to explain |
| P5 frozen transfer | ✗ | ALIEN zero-shot 0/144 both arms |
| P6 geometry changed | ✓ (weakly) | see Geometry below |
| P7 revision capacity | ✓ (mechanism) | phase-D revision rule executed (kept zB on merit); NEG arms: H3−H1 = +0.010 (no harm, no help) |

## Preregistered tests (runs/stats.log)

    T-P3  H3−H1  (CONF)   +0.010  [−0.010,+0.042]  p=0.4875  FAIL
    T-P4  H3−H2  (CONF)   +0.000  [−0.021,+0.021]  p=0.7444  FAIL
    T-P5  H3−H1  (ALIEN)  +0.000                    p=1.0000  FAIL
    T-CTRL H3−H1 (STRUCT) −0.014  |d|≤0.10                    PASS (no spurious effect)
    Holm over primaries: FAIL

Arm solve rates on CONF (24 tasks × 12 seeds × 200k oracle calls, all frozen):
H1 0.003 · H2 0.014 · H3 0.014 · RANDZ 0.014 · Z0ARM 0.010. M0 (H0) was 0.007.
Note H1 ≈ H0: the hoard itself conferred no held-out advantage either.

## What DID happen (all preregistered/metered)

1. **Development worked in-distribution.** DEV tier2 with the endogenous z: 43/144 = 0.30
   solve rate vs M0's 0.007 — a ~40× in-development improvement. DEV tier3 stayed at
   0/144: the deep wall held everywhere.
2. **Z1 beat Z0 at selection time.** Same grammar, same budgets: best relational genome
   solved 6/12 discovery episodes; best hoard-intrinsic genome 3/12. On CONF the
   difference vanished (+0.003).
3. **Geometry moved; solve rate didn't** (runs/geometry.log, analysis-only):
   - on-manifold submission rate (privileged classification): H3 4.2% vs H1 0.4%
   - module-pair submissions: H3 2.5e-4 vs H1 0.0
   - first-passage of the rare CONF solves: H3 median 65k calls vs H1 200k
   - Spearman(z, −oracle distance) over random programs: +0.126
4. **The interface ceiling was measured before the null.** Step-8 validation: even a
   designer-side truth-seeded z (perfect module knowledge the learner never had) moved
   dev-tier2 solves only 5/24 → 9/24 at the best config, and a matched random-table z
   solved 0/24 (content mattered, mechanics didn't). The mechanistic probe
   (runs/mech_probe.json) showed candidate-level score ranking actively collapses
   module-pair submissions (score-accreting blobs win), and draw-level tournaments peak
   at k=32 with pair rate 8.5e-4 — roughly one direct exact hit per budget at best.

## Interpretation (human-side; no machine claims)

The null is informative. The preregistered selection interface — tournament-k reordering
of draws from frozen proposal physics — has a low transmission ceiling: converting
"which artifacts matter" into "which exact composition to submit" requires selecting BOTH
correct operands AND the correct operator out of ~1551² × 8 combinations, and rank-only
pressure delivers at most ~10× concentration per slot before diversity collapse
(k=64 regressed). Perfect knowledge under this interface yields ≲2× findability; the
endogenous signal achieved measurable geometric concentration (10× on-manifold) but that
sits far below what exact-solution acquisition needed at 200k calls. The bottleneck is
the ordering-only coupling, not the history: relational tables demonstrably identified
the latent modules (Z1 > Z0 at selection; truth-like concentration in geometry probes).

A successor generation would need a preregistered interface whose expressive locus is
constructive (e.g. z-conditioned composition proposals) rather than purely selective —
that is a different experiment (closer to the sibling "graph alteration" design of §16),
and under §24 it cannot be retrofitted into this one.

## Budgets (metered oracle calls)

- M0 battery: 249.6M (1248 runs × 200k)
- Development A/C/E: 61.2M; meta-search B/D: 171.2M (reported, learner-side)
- Evaluation arms: 2592 runs × 200k cap = 512M nominal
- Step-8/mech probes (designer-side): ~29M + 220k proposal rounds

## Integrity

- Anti-cheat probes: ALL PASS (runs/anticheat.log), including provenance of every z-table
  key (0 orphans; 1 behavior coincides with an eval-family target — it is a solved DEV
  target shared by construction with alien_2, reported as data).
- DEV/CONF disjoint; z\*, hoard, history, k frozen before first CONF/ALIEN exposure;
  identical genotype inventory across H1/H2/H3; oracle hard-stops at budget.
- Calibration defects fixed pre-evidence and logged: composite-target rarity filter,
  global target dedup. Phase-A seeds were not hash-stable (PYTHONHASHSEED unset);
  all later phases ran with PYTHONHASHSEED=0. Outcomes are recorded, not re-derived.

## Answer to the final question

Under this frozen physics, grammar, and selection interface: **no** — accumulated
relational history built a signal that visibly bent search geometry toward the hidden
structure, but experience could not manufacture a coordinate strong enough to make the
flat problem navigable to exact solutions, and even a perfect coordinate could not have
done so through this interface. The wall, the signal, and the ceiling are all measured.
