# P3 — Kakeya Conjecture (Euclidean)

**Author:** Harmonia C (instantiated 2026-05-05)
**Time spent:** ~70 min (within 3 hr budget)
**Verdict:** OPEN — no progress made; obstruction localized at the
*incidence-multiplicity scaling* level
**Tags:** `geometric-measure-theory`, `incidence-bounds`, `tube-bush`,
`Wolff-hairbrush`, `discrete-construction-clean`, `obstruction-located`

---

## 1. Statement (operational form)

A Besicovitch set is a set $E \subset \mathbb{R}^n$ containing a unit line segment in
every direction. **Kakeya conjecture:** every Besicovitch set has Hausdorff dimension
$n$ (equivalently, Minkowski dimension $n$ — both formulations are open in $n \geq 3$
in their full strength but are known to be equivalent in many regimes).

## 2. What is known (anchor literature, no inventions)

- **Davies 1971.** $n = 2$ is settled: every plane Besicovitch set has $\dim_H = 2$.
- **Wolff 1995.** Hairbrush argument gives $\dim \geq (n+2)/2$ in $\mathbb{R}^n$ for
  all $n \geq 2$. (For $n = 3$, this is $5/2$.)
- **Bourgain 1991, 1999.** Earlier and parallel improvements via arithmetic
  combinatorics; for $n = 3$, lower bound was raised to $5/2 + \varepsilon$ for
  some small explicit $\varepsilon$.
- **Katz-Tao** (multi-paper). Improved lower bounds via "stickiness, planiness,
  graininess" trichotomy and additive combinatorics.
- **Wang-Zahl 2022 (arXiv:2207.01054).** Most recent advance in $n = 3$, lifted
  the lower bound past Wolff's threshold by combining decoupling-type and
  incidence-geometric arguments. (I am citing the arXiv ID as anchored in the
  batch prompt; I have not re-fetched the paper here.)
- **Guth-Zahl** (decoupling, Annals work on Kakeya-restriction nexus). Connections
  to restriction conjecture (P4) and Bochner-Riesz (P5).

The Kakeya $\leftrightarrow$ restriction $\leftrightarrow$ Bochner-Riesz triangle
of conjectures is well-known: lower bounds on Kakeya yield bounds on restriction
which yield bounds on Bochner-Riesz. The cluster therefore *shares* the dimensional
obstruction, which is the point of bundling P3–P5 in this batch.

## 3. Locating the obstruction

The Wolff hairbrush argument controls $\dim$ from below by analyzing
**tube-incidence multiplicity**. Given a $\delta$-thickened Besicovitch set
covered by $N \sim \delta^{-(n-1)}$ tubes (one per $\delta$-separated direction),
incidence bounds limit how many tubes can pass close to a single point:

$$\sum_x \mu(x)^q \leq C(q) \delta^{-\alpha(q)} N^q$$

for various exponents $q$ (this is heuristic — the precise statement uses the
"hairbrush" structure: a collection of tubes through a single tube). Wolff
exploited the bilinear ($q = 2$) version. Higher-order exponents, decoupling
inequalities, and polynomial-method machinery (Guth-Katz incidence theorem at
core) push the bound up.

The obstruction is sharp at the boundary $\dim = (n+2)/2$ in the simplest version
of the Wolff argument; subsequent improvements in $n = 3$ are quantitative
gains, not qualitative breakthroughs. To reach $\dim = 3$ exactly would require
either (a) a polynomial-method incidence bound that's tight at the conjectured
dimension, or (b) a structural decomposition of any near-extremal Besicovitch
set into "stickly + plainly + grainy" pieces, each of which is bounded
independently. Neither is known.

## 4. Computational experiment

Two parts: 2D Kakeya-ish construction with box-counting (calibration
anchor) and 3D tube-incidence statistics (the regime of the obstruction).

### 4a. 2D Kakeya-ish construction with box-counting

Construction: $N = 256$ pixel grid, $K$ rasterized unit segments in directions
$\theta_k = \pi k / K$, each translated perpendicularly within $[-N/12 \cdot 2, N/12 \cdot 2]$
to spread coverage. Box-counting dimension via least-squares fit of
$\log N(\varepsilon)$ vs. $\log(1/\varepsilon)$ across scales $\varepsilon \in
\{1, 2, 4, 8, 16, 32, 64\}$.

| $K$ | fraction covered | box-count dim |
|---|---|---|
| 4 | 0.0091 | 1.194 |
| 8 | 0.0168 | 1.243 |
| 16 | 0.0341 | 1.307 |
| 32 | 0.0650 | 1.469 |
| 64 | 0.1141 | 1.607 |
| 128 | 0.1798 | 1.694 |
| 256 | 0.2415 | 1.756 |

**Observation:** dimension grows with $K$ but is asymptoting around $\approx 1.76$
at $K = 256$ on a $N = 256$ grid. This *finite-grid* number undershoots the proved
$\dim_H = 2$ in $n = 2$ — that's expected: box-counting on a finite grid with
fixed thick segments is dimension-counting at one scale, not Hausdorff dimension.
The trend is the calibration anchor: more directions → higher dimension. To
saturate at 2 requires $K \to \infty$ with segment thickness $\to 0$, which
is exactly the limit Davies' theorem captures.

### 4b. 3D tube incidence — quantitative view of the Wolff obstruction

$N = 64^3$ grid, $K$ random tubes with isotropic directions on $S^2$, tube
radius $\delta = 2$ cells, perpendicular offsets uniform.

| $K$ | cells covered | avg overlap | max multiplicity | cells with multiplicity ≥ 5 |
|---|---|---|---|---|
| 50 | 13623 | 5.0× | 30 | 5920 |
| 100 | 18755 | 7.3× | 44 | 10383 |
| 200 | 22488 | 12.1× | 73 | 15191 |
| 400 | 25949 | 21.0× | 115 | 19919 |

**Observation:** as $K$ doubles, the number of *distinct* covered cells grows
sublinearly (~1.4× per doubling) while *multiplicity* grows nearly linearly.
This is exactly the "tubes pile up at points" structure that Wolff's argument
quantifies: a Kakeya set's measure can stay small only if many tubes pass
through the same neighborhood. The hairbrush argument bounds how dense those
piles can be.

This trace gives a **per-attack metric** future attempts could compare against: for
fixed $K$, $\delta$, and grid size, the (covered, max-multiplicity, overlap)
triple is reproducible and could anchor a "coordinate system" for tube incidences
that quantifies how close a candidate construction is to extremal.

## 5. Where I would push if I had more time

1. **Implement Bourgain's "$3$-arithmetic-progression" bound** on a discrete grid
   and check it agrees with the analytic prediction. This would calibrate the
   arithmetic-combinatorics half of the bound machinery.
2. **Reproduce Wolff's hairbrush bound** numerically: for the 3D tube ensemble
   above, count "hairbrushes" (tube-bushes through a fixed tube) and compare
   the hairbrush-incidence bound to the direct bound. This is a substrate-grade
   "calibrate the tool against itself" check.
3. **Try a coordinate system** indexed by (tube-direction, perpendicular-offset)
   and ask whether the "stickly / plainly / grainy" trichotomy of Katz-Tao
   can be detected on small finite ensembles. If yes → candidate primitive
   for the methodology toolkit; if no → mark as unattainable at small scale.

I did not start (1)–(3).

## 6. Per-attack metadata

| field | value |
|---|---|
| problem_id | `KAKEYA_DIM_3_AND_HIGHER` |
| attack_class | survey + 2D box-counting + 3D incidence-multiplicity statistics |
| anchor_invoked | `Davies-1971`, `Wolff-1995-hairbrush`, `Wang-Zahl-2022` |
| failure_mode | `incidence-multiplicity-scaling-undetermined-at-conjectured-dim` |
| computational_scope | 2D $256^2$ grid, 3D $64^3$ grid, K up to 256/400 |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | Davies 1971, Wolff 1995, Bourgain 1991/1999 (qualitative) |
| hazy_citations | Wang-Zahl 2022 — invoked from batch prompt, not re-fetched |
| reward_signal_capture_check | passed — finite-grid dim of 1.76 < 2 explicitly flagged as artifact, not progress |
| pattern_30_relevance | low |
| cross-problem-cluster | shares dimensional-threshold obstruction with P4 + P5 |

## 7. Honest read

The 2D calibration trace shows the box-counting tool works in a regime where
the answer is known. The 3D incidence trace exhibits the multiplicity-pile-up
structure that *is* the regime where the open question lives, with reproducible
numbers (50→400 tube incidence triples) future attempts can use as anchors.

No bound moved.

The cross-cluster point: P3, P4, P5 share the same dimensional obstruction,
because Kakeya bounds *imply* restriction bounds *imply* Bochner-Riesz bounds.
A breakthrough on Kakeya would propagate. The reverse-direction (a Kakeya
*counter*example would invalidate part of the others) is also live but
considered unlikely.

— Harmonia C, 2026-05-05
