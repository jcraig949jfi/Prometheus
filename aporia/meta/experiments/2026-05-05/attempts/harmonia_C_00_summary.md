# Harmonia C — Batch Summary (Analysis / PDEs Cluster)

**Author:** Harmonia C (instantiated 2026-05-05)
**Total time:** ~6 hours wall-clock for 5 attempts (well under 15 hr budget)
**Output files (all in `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\`):**
- `harmonia_C_01_navier_stokes.md`
- `harmonia_C_02_yang_mills_mass_gap.md`
- `harmonia_C_03_kakeya.md`
- `harmonia_C_04_restriction.md`
- `harmonia_C_05_bochner_riesz.md`
- support scripts: `_p1_ns_experiment.py`, `_p2_ym_experiment.py`,
  `_p3_kakeya_experiment.py`, `_p4_restriction_experiment.py`,
  `_p5_br_experiment.py`

**Path note:** the batch prompt specified `F:/Prometheus/...` for output. F: drive
does not exist on this host (verified via `Test-Path`); D: is the project drive.
All artifacts are at the D: equivalent. Flagging in case the batch coordinator
expected F: explicitly.

---

## 1. Verdicts

All 5 problems: OPEN. No theorem moved. No claim of progress.

| # | Problem | Verdict | Calibration anchor produced | Caveat |
|---|---|---|---|---|
| 1 | Navier-Stokes 3D regularity | OPEN | 2D BKM-integral trace clean | none |
| 2 | Yang-Mills 4D mass gap | OPEN | 2D U(1) Wilson lattice matches $I_1/I_0$ to ~1% | none |
| 3 | Kakeya $n \geq 3$ | OPEN | 2D box-counting + 3D incidence-multiplicity stats | finite-grid dim < 2 expected |
| 4 | Stein restriction $n \geq 3$ | OPEN | Tomas-Stein ratio bounded in $n=2,3$ on indicator caps | did not test Knapp examples |
| 5 | Bochner-Riesz $n \geq 3$ | OPEN | $T^\delta$ Gaussian sweep across $(\delta, p)$ | **smooth Gaussian doesn't expose Fefferman 1971 counterexample at $\delta=0$ — calibration partial** |

## 2. Does the same dimensional obstruction recur across P3–P5?

**Yes**, qualitatively, and the literature is explicit about this. The three
conjectures form an implication triangle:

$$\text{Kakeya} \Rightarrow \text{Restriction} \Rightarrow \text{Bochner-Riesz}$$

(in many regimes; the implications are not strict logical entailments but
quantitative bound-transfers). The shared structural obstruction across P3–P5 is
**incidence geometry of tubes / caps / multipliers near a $(n-1)$-dimensional
manifold (sphere or cone) in $\mathbb{R}^n$**. All three reduce to bounding
sums of "tube incidences" past what $L^2$-orthogonality and bilinear arguments
give. The proof methods that closed them in $n = 2$ exploit features of
1-dimensional curves (constant curvature, or Carleson-Sjölin local orthogonality
on a 1-manifold) that don't generalize cleanly to higher-dimensional manifolds.

Concretely from the experiments:
- P3 (Kakeya): tube multiplicity grows ~linearly with $K$ at fixed grid $N^3$.
- P4 (Restriction): Tomas-Stein ratio bounded in both $n=2$ and $n=3$ on
  indicator-of-cap test functions, decreasing with cap size.
- P5 (Bochner-Riesz): $T^\delta$ ratio bounded by 1 on smooth test functions
  (uninformative at the boundary of the conjectured region).

**Whether the same obstruction recurs at P1 and P2:** less directly. P1 (NS) is
about supercritical scaling of $L^2$-energy vs. $L^3$-criticality, which is a
different category of obstruction (PDE energy vs. harmonic-analysis incidence).
P2 (YM) is about constructive QFT and continuum limits, also different. But
**all 5 share a "marginal-vs-supercritical" theme**: the controlled quantity
(energy in P1, lattice approximation in P2, $L^2$ orthogonality in P3-P5) sits
*one degree below* what the open problem requires.

This may be a candidate substrate observation for the methodology toolkit:
across this batch, **5/5 problems share the structural pattern that an
*adjacent-but-easier* version is solved, and the gap is dimensional/scaling-marginal,
not categorical**.

## 3. Computational surprises

1. **P5 reward-signal-capture flag.** The Gaussian-test-function sweep showed
   $\|T^0 f\|/\|f\| = 1.0000$ exactly across all $p$ in $n = 2, 3$. Naively, this
   "confirms" boundedness at $\delta = 0$ — which is **known false** by
   Fefferman 1971. The miss is because the Gaussian's frequency support doesn't
   intersect the multiplier's transition region. I flagged this in the P5
   attempt file rather than report a false confirmation. Adversarial test
   functions (Knapp blocks) are required for proper calibration.
2. **P3 multiplicity scaling.** Tube incidence in 3D scales: each doubling of $K$
   (number of directions) increases covered cells by ~1.4× but max multiplicity
   by ~1.5×. The "pile-up at points" structure that Wolff's argument quantifies
   is visible in the raw numbers — the avg-overlap column grows from 5× to 21×.
   This was expected qualitatively but reproducible quantitatively in ~2 minutes
   of CPU.
3. **P2 lattice MC matched analytics to ~1%** within 6000 sweeps on a 16² lattice
   at $\beta = 2$. This is fast enough that lattice-toolchain-checking is
   essentially free; future Yang-Mills batch attempts could use this as a
   regression baseline.

## 4. Time-discipline notes

- Per-problem time budget was 3 hr; actual was ~70 min average. Under-budget
  because the "attack" recipe converged: (1) survey from training-data citations
  flagged confident vs hazy, (2) localize obstruction, (3) one small-scale
  numerical experiment as calibration anchor, (4) attempt-metadata block with
  reward-signal-capture check. Each problem fit this template cleanly.
- The reward-signal-capture check at the metadata block was load-bearing in P5
  (caught the Fefferman gap). This is a substrate-level check worth keeping in
  any future batch template.
- I did NOT invent citations. Where memory was hazy (Wang-Zahl 2022 specifics,
  Hickman-Rogers 2019, Bourgain-Guth 2011) I marked the citation as invoked-from-prompt
  rather than verified-from-memory.
- I did NOT pursue the open part of any conjecture computationally. Each
  experiment is a calibration trace, not a probe of the open regime.

## 5. Substrate-level residue

Two candidates for promotion to methodology toolkit / pattern library:

1. **"Adversarial test function before novelty claim"** — generalizes the P5
   Fefferman miss. Before claiming a numerical bound is consistent with a
   theorem, verify the test function actually exercises the regime where the
   theorem could fail. Smooth Schwartz functions often miss known
   counterexamples that live on Knapp slabs, thin caps, or sharp cutoffs.
2. **"Adjacent-easier-version is the calibration anchor"** — for any open
   conjecture, the lower-dimensional / abelian / Euclidean / smooth-data
   analog where the result IS known is the calibration target. Run the
   tool on the analog first, verify it produces the known answer, then
   document the gap to the open problem. All 5 attempts in this batch
   followed this pattern; the discipline is generalizable.

Both are candidate primitives for `harmonia/memory/methodology_toolkit.md`.

## 6. What I did NOT do

- Did not implement Knapp examples (would calibrate P5 properly).
- Did not run any 3D NS, 4D non-abelian YM, or higher-dimensional Kakeya
  simulation at scale where the open problem could in principle surface.
- Did not re-fetch any cited paper; relied on training-data anchors and the
  batch prompt's references.
- Did not attempt cross-problem coordinate-system invention.
- Did not push back on the batch prompt's framing (e.g., "are these really
  the right 5 problems for this cluster?").

## 7. Closing

Five attempt files produced, each with verdict + calibration trace + attack
metadata + honest read. Substrate-grade kill data: yes, in the sense that the
attempt-shape itself is reproducible. Surface area: covered. Time discipline:
under budget. No reward-signal capture (one near-miss flagged in P5).

The substrate is, marginally, sharper than it was at session start: the
"adversarial-test-function-before-novelty-claim" and "adjacent-easier-version-as-
calibration-anchor" patterns are concretely anchored across 5 problems and
ready for promotion if a second batch confirms them.

— Harmonia C, 2026-05-05
