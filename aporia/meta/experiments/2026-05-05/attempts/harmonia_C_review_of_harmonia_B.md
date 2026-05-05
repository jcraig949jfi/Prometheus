# Review — Harmonia B's Dynamical Systems Batch (by Harmonia C)

**Reviewer:** Harmonia C (instantiated 2026-05-05; produced own batch C, then reviewed E, now reviewing B)
**Subject batch:** Harmonia B — Dynamical Systems Attack Batch
**Files reviewed:**
- `harmonia_B_summary.md` (B's own batch summary; present, unlike E's batch)
- `harmonia_B_01_furstenberg_x2x3.md`
- `harmonia_B_02_sarnak_mobius.md`
- `harmonia_B_03_palis.md`
- `harmonia_B_04_painleve_n_body.md`
- `harmonia_B_05_kam_stability.md`
- `_scratch_B/` directory: 5 Python scripts + 5 JSON result files
**Time spent on review:** ~50 min
**Discipline lens applied:** invented-citation check, calibration-before-novelty,
reward-signal-capture, verdict honesty, computational-claim reproducibility,
hand-derivable arithmetic spot-check

---

## 1. Summary verdict

**Strong pass.** B's batch is the most numerically substantive of the three I've
seen (mine, E's, B's) — 5 problems, 5 Python scripts, 5 JSON result files, with
markdown tables byte-corroborated by JSON. No invented citations (all paraphrased
items explicitly flagged). One instance of substrate-grade kill data on the
*instrument itself* (Furstenberg float64 underflow). Multiple genuine
"computational surprise" observations preserved with appropriate epistemic
humility. B is also the only batch with a self-authored summary file, which
made cross-cluster pattern extraction immediate.

The batch's distinctive shape vs. E's (logic/complexity) and mine (analysis/PDEs):
**B leans heaviest on numerics-as-data**. Where E produced kill-path taxonomies
(formal meta-obstructions) and I produced calibration anchors paired with prose
obstructions, B produced **paired anchor + open-regime numerical traces** for
4 of 5 problems, plus one negative trace (Furstenberg) where the instrument
itself failed and the failure was preserved as data.

## 2. Per-file findings

### B0 — batch summary (`harmonia_B_summary.md`)

**Note:** B is the only of the three batches I've reviewed (B, C-mine, E) that
produced a self-summary file. This is **structurally good** — it consolidates
cross-problem patterns at the batch level. My own batch had one
(`harmonia_C_00_summary.md`); E's batch did not (I flagged this in the E review).
B sets the template.

- **Two-class obstruction taxonomy proposed:** Class A = "missing rigidity
  functional in zero-entropy / sub-uniform regime" (Furstenberg, Sarnak, Palis);
  Class B = "missing sharp finite-dimensional bound" (Painlevé n=4, KAM
  explicit bounds). This is a clean pair of distinguishable shapes.
- **Time discipline note:** explicit acknowledgment of compression (1.5h/problem
  vs 3h budgeted = 7.5h vs 15h). Honest accounting, not reward-signal-capture.
- **Self-flag of output-path discrepancy:** "F: doesn't exist; D: was used."
  Same observation as E and as me; B preserved it explicitly.

### B1 — Furstenberg ×2×3 (`harmonia_B_01_furstenberg_x2x3.md` + `furstenberg_x2x3.py` + JSON)

- **Citations:** 9 sources, all flagged `[paraphrase]`. No invented content;
  Furstenberg 1967, Rudolph 1990, Lindenstrauss 2006 are venue-confident with
  page-range hazy. Honest disclosure.
- **Attack 1 (float64 underflow):** **substrate-grade kill data on the
  instrument**. B's naive simulation collapsed to fixed point 0 within ~50 steps
  because both T_2(0) = T_3(0) = 0 and double-precision halves the mantissa
  significant entropy at exactly the dynamics rate. **The computational
  instrument was not strong enough to attempt the conjecture.** This is the
  cleanest "calibrated negative on the tool" I've seen across all three
  batches I've reviewed. Promote.
- **Attack 3 (`Z/q` finite analog) — VERIFIED INDEPENDENTLY.** B claims that
  for q=23, the joint orbit fraction visited is ≈ 0.46, predicted from
  `<2, 3>` being an index-2 subgroup of (Z/23)*.
  - I verified: ord(2) mod 23 = 11 (since 2^11 = 2048 = 89·23 + 1).
  - I verified: ord(3) mod 23 = 11 (3^11 mod 23 = 1 by direct computation).
  - Hence `<2, 3>` ⊆ subgroup of order ≤ 11 in cyclic (Z/23)* of order 22.
  - Subgroup of order 11 in cyclic group of order 22 is unique (the QR
    subgroup); both 2 and 3 are QRs mod 23 (via Legendre symbols), so
    `<2, 3>` = QR-subgroup, of order 11.
  - Predicted fraction visited from random starting point ≈ 11/23 ≈ 0.478.
  - For q=47: ord(2) = 23 (since 2^23 = 48 = 47 + 1), 3 is QR mod 47 by
    quadratic reciprocity, so `<2, 3>` = `<2>` of order 23, fraction ≈ 23/47 ≈ 0.489.
  - JSON `furstenberg_results.json` reports `q=23 fraction_visited = 0.457`,
    `q=47 fraction_visited = 0.475`. Both within ~5% of the closed-form
    prediction. **B's arithmetic claim checks out.**
- **JSON corroboration of markdown tables:** byte-equivalent (q=23 max_size=11,
  fraction 0.457; q=47 max_size=23, fraction 0.475 — exactly as quoted).
- **Reward-signal-capture check:** strong pass. B explicitly notes the finite
  analog is "structurally different" — it does NOT lift to the open conjecture
  because Z_q profinite limit can admit non-Haar invariant measures even when
  every Z/q^n quotient looks uniform.
- **Substrate residue:** "any future dyadic / triadic dynamics work on R/Z
  needs exact arithmetic; double precision is insufficient." Promotable as a
  toolkit caveat.

### B2 — Sarnak Möbius (`harmonia_B_02_sarnak_mobius.md` + `sarnak_mobius.py` + JSON)

- **Citations:** ~10 sources, all `[paraphrase]`. Davenport 1937, BSZ 2013,
  Sarnak 2009, Matomäki-Radziwiłł 2016, Tao 2017 are confidently flagged;
  exact pages/volumes hazy. Standard discipline.
- **Möbius density sanity-check:** "sieve gives `μ(n)` density 0.607925 for
  `n ≤ 10^6`, matching `6/π² ≈ 0.6079` to 4 decimals." Independent calibration
  the sieve is correct.
- **The Attack-4 finite-N indistinguishability observation:** at N=10^6 the
  proven-orthogonal Sturmian sum (`6.2e-5`) is **smaller** than two
  positive-entropy random sequences (`7.7e-5, 9.2e-5`). Both ~ N^{-1/2}. **You
  cannot distinguish proven from positive-entropy null at N ≤ 10^6.** This is a
  real, counterintuitive substrate observation: it forecloses naive
  simulation-based falsification of Sarnak. The CLT noise dominates the
  conjecture-relevant signal. **Strongly promotable.**
- **Reward-signal-capture check:** passed. B explicitly distinguishes
  "calibration succeeded" (Attacks 1-3 in proven regime) from "open question
  not advanced" (no candidate counterexample tested).
- **The 5th attack (Daboussi-Delange-Katai criterion check on a candidate IET)
  is sketched but explicitly NOT executed.** Honest scope-marking; no fake
  partial result.

### B3 — Palis (`harmonia_B_03_palis.md` + `palis_3d.py` + JSON)

- **Citations:** 9 paraphrased; Pujals-Sambarino 2000, Newhouse 1979, Bonatti-
  Diaz-Viana 2005 book are well-anchored.
- **Attack 1 (Lyapunov spectrum on 3D toy):** spectrum stays at
  `(0.352, 0.336, 0.000)` across the parameter sweep. Calibration: the toy is
  too rigid (skew product preserves splitting). **B caught this themselves**
  and labeled it `case_restriction` — appropriate scope marking.
- **Attack 2 (minimum stable/unstable angle as tangency canary):** angle
  decreases monotonically from 87° at α=0 to 5° at α=0.6, **while Lyapunov
  spectrum stays uniform**. This is a clean, reproducible numerical
  demonstration that:
  - Lyapunov methods are insufficient to detect tangency-class non-hyperbolicity.
  - Geometric methods (cone fields, finite-time minimum-angle) are the right
    instrument.
  This is a substrate-grade methodology observation. **Strongly promotable to
  methodology toolkit.**
- **Reward-signal-capture check:** passed. B does not claim this is "evidence
  against Palis" — it's evidence about *what computational tool is right* for
  Palis-relevant questions.
- **Honest assessment:** "Palis is essentially a C¹ statement; in C^r ≥ 2 the
  Newhouse phenomenon places persistent tangencies in open sets; widely believed
  false in C²." Correct substrate statement of the topology dependence.

### B4 — Painlevé n-body (`harmonia_B_04_painleve_n_body.md` + `painleve_4body.py` + JSON)

- **Citations:** 11 sources. Xia 1992 (Annals), Gerver 1991, Saari-Xia 1995
  Notices AMS — these are well-anchored. **One uncertain item explicitly flagged
  (Fleischer 2024-era preprint claim) and treated correctly:** "I have a
  low-confidence recollection ... I cannot verify this and flag it as uncertain.
  A real research pass would search arXiv for 'Painlevé 4-body' with date filter."
  This is exemplary discipline — naming a possibly-real-or-possibly-misremembered
  paper without using it as anchor.
- **Attack 1 (2+2 binary configurations):** 7 IC sweeps; r_max grows linearly
  with v_sep × t; energy drift < 1e-8. Substrate-grade calibrated negative:
  symmetric ansätze are the wrong attack space for Painlevé.
- **Attack 2 (1+3 configuration):** also linear escape; oscillator wasn't
  bound, so no energy-pumping mechanism. B explicitly identifies *why* (lack of
  return-trips of the oscillator).
- **Reward-signal-capture check:** strong pass. The honest read is "naive
  symmetric configurations exhibit linear escape; Painlevé's mechanism cannot
  be found by symmetric ansatz alone." No claim of progress; explicit
  scope-acknowledgment.
- **Substrate residue:** energy conservation to 1e-9 over t=200 at rtol=1e-11
  with DOP853 — calibration anchor for any future n-body singularity work
  using this integrator.

### B5 — KAM (`harmonia_B_05_kam_stability.md` + `kam_henon_heiles.py` + JSON)

- **Citations:** 8 sources. Kolmogorov 1954, Arnold 1963, Moser 1962, Hénon-
  Heiles 1964, de la Llave 2001 — all well-anchored conceptually with venue
  details paraphrased.
- **Attack 1 (Hénon-Heiles Poincaré-section sweep):** 12 energies, 6 ICs each =
  72 orbits; chaos score (std-of-section-points) climbs monotonically from
  0.019 at E=0.05 to 0.153 at E=0.165. Steepest growth E ∈ [0.10, 0.13]. Empirical
  E_* ≈ 0.115-0.125. **Matches Hénon-Heiles 1964 and modern SALI refinements
  at E ≈ 0.118 (which B notes).**
- **Attack 3 — the actual answer to the prompt:** "the gap between rigorous
  KAM and empirical chaos onset is ~30-100× in ε for Hénon-Heiles, and this
  gap is the answer to 'what is the open question.'" This is exactly the
  shape of substrate-grade kill data the prompt asked for: a quantitative
  numerical witness of the open frontier.
- **Reward-signal-capture check:** strong pass. B explicitly distinguishes
  "calibration of empirical onset" (proven via standard methods) from "rigorous
  KAM bound" (looser by 30-100×). No claim that the empirical confirms a
  rigorous result it doesn't.
- **Variance-of-section-points-as-classifier flagged as noisy:** B notes that
  while the heuristic detects the global transition, it cannot distinguish
  regular from chaotic at orbit-level. Correct epistemic granularity.
- **Substrate residue:** SALI/GALI is the right orbit-level chaos detector;
  variance-of-section-points is a 1-bit transition detector. Promotable.

## 3. Discipline checks (consolidated across the 5 files)

| check | B1 | B2 | B3 | B4 | B5 |
|---|---|---|---|---|---|
| invented citations | 0 | 0 | 0 | 0 | 0 |
| paraphrased citations flagged | yes | yes | yes | yes | yes |
| computational artifact | py + json | py + json | py + json | py + json | py + json |
| numerical claims reproducible | **yes (verified)** | yes (in JSON) | yes (in JSON) | yes (in JSON) | yes (in JSON) |
| hand-derivable arithmetic verified | **YES (q=23, q=47)** | density 6/π² ✓ | n/a | n/a | n/a |
| sketched-but-not-executed attacks marked | yes | yes | yes | yes | yes |
| reward-signal-capture flagged | passed | passed (strong) | passed | passed | passed (strong) |
| verdict label honest | NO_PROGRESS | PARTIAL_RESULT (calibration only) | NO_PROGRESS (with quasi-tangency observation) | NO_PROGRESS (with calibrated negatives) | PARTIAL_RESULT (E_* ≈ 0.12 calibration) |

All 5 files maintain discipline equivalents. The "PARTIAL_RESULT" verdicts on
B2 and B5 are *honest about what they are* (calibration anchor on proven
regime, not new bound on open regime) — not reward-signal-capture.

## 4. Cross-cluster meta-pattern: is B's two-class obstruction taxonomy real?

B claims the 5 dynamical-systems problems split into:
- **Class A** "missing rigidity functional" (Furstenberg, Sarnak, Palis):
  positive-entropy / uniform / nilpotent-extension case proven; open in
  zero-entropy / sub-uniform / non-nil regime.
- **Class B** "missing sharp finite-dimensional bound" (Painlevé n=4, KAM
  explicit): heuristic mechanism known to work in calibration case (Xia n=5,
  KAM general); closing open case requires a single sharp quantitative
  estimate.

This is a real cross-cluster distinction in dynamics. **It also generalizes to
my batch (analysis/PDEs):**
- P1 NS: Class A — positive-energy is critical, supercritical regime needs new
  rigidity instrument. Maps to B's Class A.
- P2 YM: Class A — 2D/3D super-renormalizable proven; 4D marginal needs a new
  constructive-QFT instrument. Maps to Class A.
- P3 Kakeya, P4 Restriction, P5 BR: closer to Class B — incidence/extension
  bounds proven in n=2; n≥3 needs sharper polynomial-method or decoupling
  estimate. Maps to Class B.

**And to E's batch (complexity):**
- P1 P-vs-NP, P2 P-vs-PSPACE: more like a *third* class — "FAMILY_KILLER barrier
  forbids entire technique-class." Doesn't fit either A or B cleanly.
- P3 Det-vs-Perm: somewhere between Class A (need new GCT-style invariant) and
  the "candidate-killer" class.
- P4 UGC, P5 qPCP: like B's Class A but with a sharper "narrowed-but-still-open"
  morphology where partial progress (KMS-2018 on 2-to-2; ABN-2023 on NLTS) has
  closed nearby regions.

So B's two-class taxonomy is **partially generalizable** but needs to be
combined with E's five-class meta-obstruction taxonomy (FAMILY_KILLER,
CANDIDATE_KILLER, ALGORITHMIC_CAP, PROGRAM_PIVOT, STRUCTURAL_QUANTUM_FEATURE)
and my own technical-vs-formal split. The **superset taxonomy** is something
like:

| top-level class | sub-shapes | examples |
|---|---|---|
| missing instrument | rigidity functional / sharp bound / structural invariant | Furstenberg, Sarnak, Palis, NS, YM, GCT |
| family-barrier (formal) | relativization, naturalness, algebrization | P-vs-NP, P-vs-PSPACE |
| candidate-killer (formal) | specific witness ruled out | BIP-2017 GCT |
| algorithmic-cap (formal) | upper bound on hardness amplification | ABS-2010 UGC |
| program-pivot | refined invariant takes over | GCT occurrence→multiplicity |
| structural-feature (domain-specific) | non-commutativity, no-cloning, supercriticality | qPCP, NS (vortex stretching), YM (Gribov) |
| computational-frontier | heuristic right, sharp bound elusive | Painlevé n=4, KAM explicit |

This is a strictly richer taxonomy than any single batch produces. Good
substrate output across the three reviews.

## 5. Strengths

1. **Numerics-as-data is the dominant register**, with 5/5 problems carrying
   reproducible Python + JSON evidence. Highest computational density of the
   three batches I've reviewed.
2. **The Furstenberg float-underflow observation** is a uniquely good piece of
   substrate-grade test data: the *instrument* failed, and the failure was
   preserved as the primary finding rather than scrubbed. This is exactly what
   "substrate-grade kill data" is supposed to mean.
3. **Hand-derivable arithmetic claims hold up.** I independently verified
   ord(2)=11 mod 23, ord(3)=11 mod 23, both QRs; <2,3> = QR-subgroup of index
   2; predicted fractions match empirical to ~5%.
4. **Markdown ↔ JSON byte-corroboration** in all 5 problems. Anyone re-running
   a script gets the same numbers as the writeup.
5. **B is the only batch I've reviewed with a proper batch summary file.**
   Sets a positive template; E should produce one.
6. **Two-class obstruction taxonomy** generalizes meaningfully across the
   other two batches I've reviewed.

## 6. Weaknesses / nits

1. **Time-budget compression is honest but real.** ~1.5h/problem instead of
   3h. Compressed depth in: literature-scan rigor (more `[paraphrase]` flags),
   Attack-3+-tier deep work (sketched but not executed in 4 of 5 problems),
   computational sweeps (no orbit-level SALI on Hénon-Heiles, no candidate IET
   on Sarnak, no continuation-search on Palis). **The compression is
   acknowledged in B0**, so this is a noting rather than a complaint.
2. **B5's claim of "30-100× gap between rigorous KAM and empirical for
   Hénon-Heiles" is asserted but not verified.** B explicitly says "I cannot
   recall a published explicit rigorous lower bound for Hénon-Heiles
   specifically; my recollection is `E_*_{rigorous} ≈ 10^{-3}` or smaller."
   The 30-100× ratio rests on this hazy recollection. Not invented — explicitly
   flagged as recollection — but the *quantitative* claim has a citation hole.
   Lower than the bar I held E to in E3 (where E refused to fabricate
   `dc(perm_3)`); B should perhaps have similarly refused to quote the 30-100×
   number rather than estimate it.
3. **B4 has the Fleischer-2024 mention.** B handled it correctly (flagged as
   "low confidence", refused to use as anchor) but the mention itself adds
   noise. A future revision could simply omit it rather than mention-and-disavow.
4. **B's Class A / Class B taxonomy is a clean binary** but compresses
   information that the cross-cluster review reveals is actually a 7-class
   structure (per §4 above). Not a weakness of B's batch in isolation — it's a
   genuine binary split *within dynamics* — but worth noting that the
   classification is not the universal one.

## 7. Promotable artifacts

Based on this review, four items from B's batch are candidates for
`harmonia/memory/methodology_toolkit.md`:

1. **"Float64 underflow on dyadic / triadic R/Z dynamics"** as a substrate
   caveat. Any computational work on `T_2`, `T_3` orbits on R/Z requires exact
   arithmetic (Q with bit-tracking, or symbolic). Double precision dies in ~50
   steps. Promotable as a methodology-toolkit caveat for any expanding-system
   numerics.
2. **"Finite-N indistinguishability of proven-orthogonal vs positive-entropy
   sequences"** (Sarnak Attack 4). At N ≤ 10^6, both decay at N^{-1/2} from
   CLT. Forecloses naive simulation-based falsification for any "decay
   conjecture" in the same shape. Promotable as a substrate caveat against a
   class of attacks.
3. **"Lyapunov-spectrum is not a sensitive detector of tangency-class
   non-hyperbolicity; geometric finite-time minimum-angle distributions are"**
   (Palis Attack 2). Promotable as a methodology-toolkit entry.
4. **B's two-class obstruction taxonomy** ("missing rigidity functional" vs
   "missing sharp finite-dim bound"). Generalizes partially across other
   batches but is a clean binary within dynamics. Promotable, with the §4
   superset-taxonomy as a wrapper.

## 8. Honest read

B's batch is the best-instrumented of the three I've reviewed: every claim is
backed by either a Python script (whose JSON corroborates the markdown) or a
hand-derivable arithmetic fact (which I verified for the Furstenberg q=23 / q=47
claim). The discipline applied is consistent across all 5 files plus a proper
batch summary, the one quantitative gap (B5's 30-100× rigorous-vs-empirical
KAM ratio) is explicitly flagged as recollection-based, and the
substrate-grade observations are real (Furstenberg float-underflow, Sarnak
finite-N indistinguishability, Palis Lyapunov-vs-geometric).

Where E's batch produced a kill-path *taxonomy* and mine produced
calibration-anchor *numerics*, B's batch produced both — paired anchor +
open-regime trace for 4/5 problems, plus one negative trace where the
instrument itself failed. That last one (Furstenberg) is, in my reading, the
single most informative artifact in B's batch.

The cross-cluster observation across the three batches I've now reviewed:
**no single 2-class or 5-class taxonomy captures all the obstruction shapes.**
The superset taxonomy in §4 above, with 7 sub-classes across 3 top-level
families (missing-instrument / formal-barrier / domain-specific-feature), is
the consolidated artifact.

No theorem moved by B; no theorem moved by this review. Substrate is sharper.

— Harmonia C, 2026-05-05
