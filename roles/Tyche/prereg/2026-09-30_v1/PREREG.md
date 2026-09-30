# PREREG -- Tyche v1: can a sense evolve from precursors no ruler could value?

Currency: 2026-09-30. Committed BEFORE any v1 arm runs. Directive:
roles/Tyche/prompts/2026-09-30_v1_directive/ (e6884298c). Governs
`python -m tyche.v1.run_v1 --arm {V0,DE,DENR} --seed {1,2}
--out tyche/runs/v1_2026-09-30/<ARM>_s<seed>` at the commit adding this
file (code hashes: CODE_SHA256.txt) and `python -m tyche.v1.report_v1
tyche/runs/v1_2026-09-30`.

## 0. Question

Can a lens lineage acquire a useful sense whose necessary precursor
components have no individually measurable utility? Calibration lane only
(the 122 natural residuals are untouched until gate 6 is shown).

## 1. What v0 showed that this design rests on (from committed v0 rows)

v0 scored a lens by marginal value relative to the CURRENT ecology. It
solved P5 (sign of a product of two delayed gaussians) only at R2, where
one precursor (x4[t]) was already a raw observation: the admitted lens
supplied delay(ch2, 3) alone (ablation needs channel 2 only). P5 at R0
and P1 (both precursors absent) were never solved. Reading: v0 selection
reaches synergy with senses the ecology already holds; it is blind when
two or more precursors are absent. v1 tests that reading directly (C vs Z
worlds) and tests whether preservation + combination removes the blindness.

## 2. Worlds (tyche/v1/worlds_v1.py; hash in each run's CONFIG.json)

13 selection + 5 held out, T = 12100, splits as v0. Ruler R0 ONLY (see
s6). Organisms lin, tree, tab.
  Z (every precursor absent, each exactly zero-marginal): Z1 xor(d4,d11),
    Z2 xor(d3,d7), Z3 parity(d2,d5,d9), Z4 sign(g[t-5] g[t-2]),
    Z5 xor of two delayed 5-window majorities (3-op precursors)
  C (one precursor is a raw observation): C1 xor(raw, d6), C2 sign(raw x d4)
  G gradient control: G1 running count mod 3
  N negatives: TSD twins of Z1, Z2, Z4, Z5; keyed PRF
  held out: Z1 sibling (Markov inputs), Z4 sibling (AR(1) inputs), Z6
    xor(d5,d8), its twin, PRF
Calibration measured before freezing: raw ecology at chance on all Z/C
(0.48-0.52); oracle (answer-key lens) deficit ~0.5 at R0 on Z/C; twins
|deficit| <= 0.02.

## 3. Gate 1 repairs (v0 F1, F2)

Per-world ecology (raw + lenses admitted on that world). tab sees
[candidate, raw] only -- its inputs never depend on ecology order; lin and
tree see [candidate, ecology lenses, raw]. Residual = capability deficit
D(W, o) = acc_o(ecology + oracle) - acc_o(ecology) on calibration worlds;
the oracle is never visible to evolution. err/dis residuals retired.
Check: no organism's ecology baseline may fall > 0.03 below its eco0
value on any world at any epoch (reported as baseline_drops).

## 4. Arms (same worlds; same initial population per seed; budget 6000
evaluation UNITS per world = new lens evaluations + pair evaluations; an
arm runs until its budget is spent, epochs of 10 generations)

  V0   v0 selection (eps-lexicase on individual marginal gains, elites,
       14-slot v0 reserve), single-lens admission only
  DE   V0 selection PLUS a 48-slot utility-free reserve (age protection 5
       gens; output-signature novelty + 0.1 lineage-novelty bonus; 1/3
       random persistence; neutral drift of 12 members per generation)
       PLUS 60 pair evaluations per world per generation, O(L_a, L_b),
       mixed reserve x reserve 50% / reserve x population 30% /
       population x population 20% PLUS fused-sensor admission PLUS
       delayed credit (both precursors of an admitted fused sensor are
       vindicated: protected in the reserve 10 epochs, x3 drift weight)
  DENR preservation ablation: 60 population x population pair evaluations
       per world per generation; no reserve of any kind
Admission (all arms, epoch end, CONF split, per-world ecology): candidates
are the top 5 single lenses and (DE, DENR) the top 5 pairs per world with
val gain >= 0.02; tested in val order; the first with conf z >= 4 and
gain >= 0.01 is admitted (at most 1 per world per epoch); a pair is
admitted as fuse(a, b), whose output is exactly [L_a(X), L_b(X)].
Evolutionary seeds 1 and 2 (6 runs).

Pass D per admitted lens: test split, fresh seeds 101/102, matched random
null (64; for a fused sensor 64 fused pairs of random lenses of the
components' sizes), causality audit, twin gain, transfer to all other
worlds (raw best case; descriptive), channel ablation, and for fused
sensors each component's max individual val gain on its home world over
every logged evaluation and its test gain alone.

## 5. Gates, verdict code (tyche/v1/report_v1.py) and my predictions

GATE 6 (primary): per Z world and seed, de_ok = DE admitted a fused
sensor with test gain >= 0.10, replicated (z >= 4; both fresh seeds
z >= 3), above the matched pair-null p95, causal, twin z < 3, whose two
components each had max individual home val gain < 0.01 at EVERY logged
evaluation and test z < 3 alone; v0_fail = V0 admitted nothing on that
world with test gain >= 0.10 and replicated. PASS if some Z world has
de_ok and v0_fail in both seeds; PARTIAL if in one; FAIL if none;
NOTHING_COULD_FIRE if no Z world is valid. Tests: a synthetic qualifying
row PASSes; a precursor with val gain 0.05, a V0 solve, or a live twin
each FAIL (tyche/tests/test_v1.py).
Reachability (measured before freezing, PASS_A_s1/s2): every Z world is
valid in both seeds -- best initial single test gain <= 0.018; best of
all 4560 initial pairs (val joint) <= 0.061 (void threshold 0.10).

Predictions (I can lose these):
  P1 GATE6 = PASS, on Z1 and Z2 in both seeds.
  P2 V0 solves C1 and C2 in both seeds (one-step synergy with raw) and
     no Z world in either seed.
  P3 DE solves Z4 in both seeds; Z5 (3-op precursors) in at most one
     seed; Z3 (needs a triple; no triple search) in neither.
  P4 DENR solves Z worlds in at most half as many (world, seed) cells as
     DE -- preservation, not pairing alone, carries the effect.
  P5 No admission on any N world in any arm; no baseline drop > 0.03.
  P6 On solved Z worlds the R0 deficit falls from ~0.5 to <= 0.05; on N
     worlds it stays within 0.03 of 0.
If P4 fails (DENR ~ DE), the reading is "pair evaluation suffices in this
chemistry; preservation was not needed" -- a legitimate negative about the
reserve. If GATE6 FAILS with pairs evaluated, the reading is that O(La,Lb)
with this budget does not find zero-marginal pairs, and v2 must change the
generator of precursors, not the ruler.

## 6. Disclosures (seen before freezing)

- Design-time reachability at first included R2: a single initial lens
  reached test +0.497 on Z4 at R2 (seed 1) and the Z1 initial-pair floor
  was 0.370 at R2 -- R2 shifts every delay by 2 and turns Z4 into a
  one-precursor-present world. R2 was removed from v1 before any
  evolution; the floors above are the R0 recomputation.
- Smoke runs of all three arms (tiny budget) were executed for bugs; their
  admission counts were visible (DE 2 then 1; V0 about 1 per epoch;
  DENR 2 then 0), not which worlds.
- Tests: tyche/tests 30 passed (v0 14, catalogue 7, v1 9).

## 7. Compute

Estimated ~2 core-hours for 6 runs on M2 (13 workers each, <= 2 runs at
once), inside MWO-0004 R2; no lease claimed. Budget in units bounds work.
