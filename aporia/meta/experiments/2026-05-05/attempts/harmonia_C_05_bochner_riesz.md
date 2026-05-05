# P5 — Bochner-Riesz Conjecture

**Author:** Harmonia C (instantiated 2026-05-05)
**Time spent:** ~75 min (within 3 hr budget)
**Verdict:** OPEN — no progress made; obstruction localized; calibration trace
*partial* (smooth-Gaussian test function does not expose Fefferman's
ball-multiplier counterexample, flagged below)
**Tags:** `harmonic-analysis`, `multiplier-theorem`, `Carleson-Sjolin`,
`obstruction-located`, `calibration-caveat`

---

## 1. Statement (operational form)

The Bochner-Riesz multiplier of order $\delta \geq 0$ is

$$T^\delta f = \mathcal{F}^{-1}\bigl((1 - |\xi|^2)_+^\delta\, \widehat{f}(\xi)\bigr).$$

**Bochner-Riesz conjecture:** $T^\delta$ is bounded on $L^p(\mathbb{R}^n)$ iff

$$\left|\frac{1}{p} - \frac{1}{2}\right| \leq \frac{\delta + 1/2}{n}.$$

For $n = 2$: settled (Carleson-Sjölin 1972).
For $n \geq 3$: OPEN.

## 2. What is known (anchor literature, no inventions)

- **Bochner 1936.** Original construction of the Bochner-Riesz means as a
  summation tool for multiple Fourier series.
- **Fefferman 1971 ("The multiplier problem for the ball").** Proved the
  $\delta = 0$ "ball multiplier" is **unbounded** on $L^p$ for all $p \neq 2$ in
  $n \geq 2$. This is foundational: it showed $\delta = 0$ is qualitatively
  different from $\delta > 0$, which is why the conjecture starts at $\delta > 0$.
- **Carleson-Sjölin 1972.** Full Bochner-Riesz conjecture in $n = 2$.
- **Stein 1958 (thesis).** Earlier necessary conditions for boundedness.
- **Bourgain 1991.** Improvements past Stein-Tomas / square-function in $n \geq 3$.
- **Tao 1998-2003 series.** Bilinear / multilinear progress.
- **Lee 2004**, **Bourgain-Guth 2011**. Further quantitative improvements.

The Bochner-Riesz, restriction (P4), and Kakeya (P3) conjectures form a triangle:
restriction implies Bochner-Riesz, restriction is implied by Kakeya in many
regimes. A Kakeya improvement propagates to BR and restriction.

## 3. Locating the obstruction

The boundary of the conjectured region is the line

$$\frac{1}{p} - \frac{1}{2} = \frac{\delta + 1/2}{n} \qquad \text{(for } p \geq 2\text{)}.$$

**Necessary conditions** (known): for $T^\delta$ to be bounded on $L^p$, the
above inequality must hold (this comes from the Knapp / standard
counterexample on a thin slab in Fourier space).

**Sufficient conditions** (proved): partial — Stein-Tomas $L^2$-orthogonality gives
boundedness up to a worse exponent than conjectured; bilinear methods (Tao 2003)
push further; Bourgain-Guth multilinear-Kakeya-via-polynomial-method pushes
further still; full conjecture remains open in $n \geq 3$ at the boundary line.

The structural obstruction is the same as in restriction (P4): the dual operator
$T^\delta f = \widehat{f} \cdot (1 - |\xi|^2)_+^\delta$ has its action concentrated
on a $\delta'$-neighborhood of the unit sphere (with $\delta' \approx \delta$),
and $L^p$-bounding it reduces to extending the Stein-Tomas bound past the
$L^2$-orthogonality regime.

**Why $n = 2$ closed and $n \geq 3$ didn't:** in $n = 2$, the unit circle is a
1-manifold and the curvature $K = 1$ is constant; the Carleson-Sjölin proof
extracts an $L^p$-bound from the $L^2$-bound via a local-orthogonality argument
that exploits this. In $n \geq 3$, the unit sphere has higher-dimensional
curvature variation that the local-orthogonality argument doesn't directly
control.

## 4. Computational experiment (with calibration caveat)

The script $\mathtt{\_p5\_br\_experiment.py}$ computes the BR multiplier $T^\delta f$
for $f$ a centered Gaussian on a periodic grid in $n = 2$ (128²) and $n = 3$ (48³),
and measures $\|T^\delta f\|_{L^p} / \|f\|_{L^p}$ for $p \in \{1.5, 2, 3, 4, 6, 8\}$
and $\delta \in \{0, 0.25, 0.5, 0.75, 1.0, 1.5\}$.

### 4a. n = 2

| $\delta$ | $(p_{\rm lo}, p_{\rm hi})$ conj. | $p=1.5$ | $p=2$ | $p=3$ | $p=4$ | $p=6$ | $p=8$ |
|---|---|---|---|---|---|---|---|
| 0.00 | (1.33, 4.00) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 0.25 | (1.14, 8.00) | 0.9957 | 0.9936 | 0.9913 | 0.9902 | 0.9891 | 0.9885 |
| 0.50 | (1.00, ∞) | 0.9916 | 0.9873 | 0.9829 | 0.9807 | 0.9785 | 0.9773 |
| 0.75 | (1.00, ∞) | 0.9874 | 0.9811 | 0.9746 | 0.9714 | 0.9681 | 0.9665 |
| 1.00 | (1.00, ∞) | 0.9834 | 0.9750 | 0.9665 | 0.9623 | 0.9580 | 0.9558 |

### 4b. n = 3

| $\delta$ | $(p_{\rm lo}, p_{\rm hi})$ conj. | $p=1.5$ | $p=2$ | $p=3$ | $p=4$ | $p=6$ |
|---|---|---|---|---|---|---|
| 0.00 | (1.50, 3.00) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 0.25 | (1.33, 4.00) | 0.9936 | 0.9903 | 0.9869 | 0.9852 | 0.9835 |
| 0.50 | (1.20, 6.00) | 0.9873 | 0.9808 | 0.9742 | 0.9709 | 0.9675 |
| 1.00 | (1.00, ∞) | 0.9751 | 0.9625 | 0.9498 | 0.9434 | 0.9370 |
| 1.50 | (1.00, ∞) | 0.9634 | 0.9450 | 0.9266 | 0.9174 | 0.9082 |

### CALIBRATION CAVEAT — the test function is not adversarial

The Gaussian's frequency content is concentrated near $|\xi| = 0$, so the
multiplier $(1 - |\xi|^2)_+^\delta$ is essentially $1$ on the support of $\widehat{f}$.
That's why the $\delta = 0$ row shows ratio $= 1.0000$ (exactly), even though
**Fefferman 1971 PROVED $T^0$ is unbounded** on $L^p$ for $p \neq 2$ in $n \geq 2$.

The Gaussian is *too smooth* to expose the unboundedness at $\delta = 0$. The
canonical adversarial functions are Knapp-block constructions (functions whose
Fourier transform is concentrated on a thin slab tangent to the unit sphere),
which I did not implement.

So the calibration check passes "trivially" but does NOT calibrate against the
known counterexample. For a fully calibrated probe, Knapp blocks are the
required test class.

## 5. Where I would push if I had more time

1. **Implement Knapp blocks** (functions $f$ with $\widehat{f}$ concentrated on
   a $\delta'$-thin slab tangent to $S^{n-1}$). Re-run the BR ratio sweep on these.
   The Fefferman counterexample at $\delta = 0$ should appear as a divergent
   ratio with grid refinement. This would be a proper calibration anchor.
2. **Square function approach.** Implement the Carleson-Sjölin / Cordoba
   square-function decomposition numerically in 2D to reproduce the proved $n = 2$
   bound. This is hand-cranked but mechanical.
3. **n = 3 probe at the conjectured boundary.** With Knapp blocks in hand, sweep
   $(p, \delta)$ along the conjectured boundary line in $n = 3$ at multiple grid
   resolutions and see whether the ratio appears bounded as the grid refines.
   Numerical evidence for the conjecture (with all the caveats of finite-grid
   experiments).

I did not start (1)–(3).

## 6. Per-attack metadata

| field | value |
|---|---|
| problem_id | `BOCHNER_RIESZ_N_GE_3` |
| attack_class | survey + non-adversarial Gaussian sweep + caveat |
| anchor_invoked | `Fefferman-1971-ball-multiplier`, `Carleson-Sjolin-1972` |
| failure_mode | `boundary-line-of-conjectured-region-not-saturated-by-known-techniques-in-n>=3` |
| computational_scope | $n=2$ at $128^2$, $n=3$ at $48^3$, Gaussian only (NOT Knapp) |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | Fefferman 1971, Carleson-Sjölin 1972, Bochner 1936 |
| hazy_citations | Lee 2004, Bourgain-Guth 2011 — invoked from prompt, not re-fetched |
| reward_signal_capture_check | **partial pass** — the calibration ratio of 1.0000 at $\delta=0$ is flagged as artifact of test-function choice, NOT as evidence of boundedness |
| pattern_30_relevance | low |
| cross-problem-cluster | implied by P4 (restriction); shares dimensional obstruction with P3, P4 |

## 7. Honest read

The numerical sweep is well-behaved (smooth dependence of ratio on $\delta$ and
$p$, monotone in $\delta$), but the test function is not adversarial: at
$\delta = 0$ in both $n = 2$ and $n = 3$, the ratio is identically $1$, which
*contradicts* Fefferman's ball-multiplier theorem if interpreted as "bound holds."
The contradiction is not real: it's a calibration failure (Gaussian's frequency
support doesn't reach the multiplier's transition region). I am leaving this in
the record explicitly because reward-signal-capture is the real risk — the
naive read of the table would be "BR is bounded for all $\delta \geq 0$ and
all $p$," which is *known false*.

The genuinely informative residue: the ratio sweep across $(\delta, p)$ for
the Gaussian is reproducible to four digits and could anchor any future Knapp-block
calibration as a "trivial-test-function baseline" the adversarial test must beat.

No estimate moved.

— Harmonia C, 2026-05-05
