# P4 — Restriction Conjecture (Stein)

**Author:** Harmonia C (instantiated 2026-05-05)
**Time spent:** ~70 min (within 3 hr budget)
**Verdict:** OPEN — no progress made; Tomas-Stein machinery calibrated;
obstruction localized at gap from $L^2$-restriction to full $L^p$-restriction
**Tags:** `Fourier-restriction`, `extension-operator`, `Tomas-Stein`,
`q-endpoint-gap`, `obstruction-located`, `2D-control-trace-clean`

---

## 1. Statement (operational form)

For $n \geq 2$, the extension operator $E: L^p(S^{n-1}) \to L^q(\mathbb{R}^n)$,

$$E(g)(x) = \int_{S^{n-1}} g(\xi)\, e^{2\pi i x \cdot \xi}\, d\sigma(\xi),$$

is bounded iff $q > 2n/(n-1)$ and (for the $L^p \to L^q$ Stein endpoints)
the exponents satisfy a specific affine relation depending on $n$. In its
strongest form (the "extension conjecture"): for $q > 2n/(n-1)$,
$E: L^q(S^{n-1}) \to L^q(\mathbb{R}^n)$ is bounded.

For $n = 2$: settled (Carleson-Sjölin / Fefferman 1970-era).
For $n \geq 3$: OPEN at the full conjectured endpoint.

## 2. What is known (anchor literature, no inventions)

- **Stein 1979 conjecture.** Restriction conjecture in its modern form.
- **Tomas 1975** (and **Stein**, independently 1970s): the
  **Stein-Tomas endpoint** $(p, q) = (2, 2(n+1)/(n-1))$, i.e. $L^2 \to L^{2(n+1)/(n-1)}$.
  - In $n = 2$: Stein-Tomas endpoint is $(2, 6)$.
  - In $n = 3$: Stein-Tomas endpoint is $(2, 4)$.
  - In $n = 4$: $(2, 10/3)$, etc.
- **Carleson-Sjölin / Fefferman 1970.** Full restriction in $n = 2$ at
  the conjecture endpoint (i.e. all $q > 4$).
- **Bourgain 1991** and follow-ups. Improvements past Stein-Tomas in $n \geq 3$.
- **Tao-Vargas-Vega 1998.** Bilinear restriction estimates.
- **Guth 2016 (Annals).** Major polynomial-method advance on restriction in $n = 3$.
- **Hickman-Rogers 2019** and **Wang 2022.** Most recent decoupling-based
  improvements; full conjecture remains open in $n \geq 3$.

The conjecture is *equivalent* (in many regimes) to the Kakeya conjecture (P3) and
implies the Bochner-Riesz conjecture (P5). The triangle is well-known.

## 3. Locating the obstruction

The Stein-Tomas $L^2 \to L^{2(n+1)/(n-1)}$ estimate is proved by orthogonality
($T^* T$ is convolution with $\widehat{d\sigma}$, which has $L^q$ decay
$|\widehat{d\sigma}(x)| \lesssim |x|^{-(n-1)/2}$). This $L^2$ approach reaches
$q = 2(n+1)/(n-1)$ but cannot push to the conjectured $q > 2n/(n-1)$.

The gap between $2(n+1)/(n-1)$ and $2n/(n-1)$ shrinks with $n$:
- $n = 2$: $6$ vs $4$ — gap of $2$. Fefferman closed it.
- $n = 3$: $4$ vs $3$ — gap of $1$. Open.
- $n = 4$: $10/3$ vs $8/3$ — gap of $2/3$. Open.
- $n = 5$: $3$ vs $5/2$ — gap of $1/2$. Open.

The "easy" $L^2$ orthogonality argument is structurally limited; pushing past
it requires bilinear / multilinear arguments (Tao-Vargas-Vega, Bennett-Carbery-Tao
2006), polynomial method (Guth), or decoupling (Bourgain-Demeter 2015, Guth-Maldague,
Hickman-Rogers). Each closes part of the gap but not all of it. The remaining gap
is a *quantitative* obstruction inside a well-understood structural framework, not
a new structural obstacle. That makes the open problem "small" in some sense and
also makes progress slow.

## 4. Computational experiment

The script $\mathtt{\_p4\_restriction\_experiment.py}$ computes the extension of
indicator-of-arc / indicator-of-cap functions on $S^{n-1}$ and measures
$\|E(g)\|_{L^q(B_R)} / \|g\|_{L^p(S^{n-1})}$ to verify the Stein-Tomas
ratio is bounded by an absolute constant (calibration).

### 4a. n = 2 (calibration anchor, theory complete)

$g = \mathbf{1}_{|\theta| < \delta/2}$ on $S^1$. Grid: $200 \times 200$ on
$[-40, 40]^2$. Stein-Tomas endpoint $(p, q) = (2, 6)$.

| arc width $\delta$ | $\|g\|_{L^2}$ | $\|E g\|_{L^2}$ | $\|E g\|_{L^4}$ | $\|E g\|_{L^6}$ | $\|E g\|_{L^8}$ | TS ratio $\|E g\|_{L^6} / \|g\|_{L^2}$ |
|---|---|---|---|---|---|---|
| $\pi$ | 1.7725 | 41.82 | 6.086 | 4.135 | 3.679 | **2.333** |
| $\pi/2$ | 1.2533 | 29.24 | 4.517 | 2.786 | 2.299 | **2.222** |
| $\pi/4$ | 0.8862 | 19.82 | 3.274 | 1.900 | 1.470 | **2.144** |
| $\pi/8$ | 0.6267 | 13.74 | 2.105 | 1.161 | 0.868 | **1.853** |
| $\pi/16$ | 0.4431 | 9.444 | 1.259 | 0.656 | 0.477 | **1.481** |

The Stein-Tomas ratio at $q = 6$ stays below $\approx 2.4$ across the sweep
and *decreases* as $\delta$ shrinks. Calibration confirms boundedness.

### 4b. n = 3 (open regime)

$g = \mathbf{1}_{\text{cap of polar angle } \delta}$ on $S^2$. Grid: $60^3$ on
$[-15, 15]^3$. Stein-Tomas endpoint $(p, q) = (2, 4)$.

| cap radius $\delta$ | $\|g\|_{L^2}$ | $\|E g\|_{L^2}$ | $\|E g\|_{L^3}$ | $\|E g\|_{L^4}$ | TS ratio $\|E g\|_{L^4} / \|g\|_{L^2}$ |
|---|---|---|---|---|---|
| 1.000 | 1.700 | 61.67 | 15.11 | 8.449 | **4.971** |
| 0.500 | 0.877 | 29.02 | 7.254 | 3.807 | **4.341** |
| 0.250 | 0.442 | 13.79 | 2.964 | 1.406 | **3.182** |
| 0.125 | 0.221 | 6.065 | 1.128 | 0.490 | **2.214** |

The Stein-Tomas ratio at $q = 4$ stays bounded ($\sim 5$ at large cap, $\sim 2$ at
small) and *decreases* as $\delta$ shrinks. This is calibration for what's proved.

### What the data does NOT show

It does not probe the open part of the conjecture. To get there I'd need to test
$E: L^p(S^{n-1}) \to L^q(\mathbb{R}^n)$ at the **conjectured** endpoint
$(p, q) \to (q^*, q^*)$ with $q^* > 2n/(n-1)$, where the bound is unproven.
Doing this empirically requires sweeping $p$ together with $q$ along the
conjectured line. I sketched this but did not execute — the indicator-of-arc
test function's $L^p$ norm scales as $\delta^{1/p}$, so the conjectured ratio
would behave like $\delta^{1/p - 1/q}$, which is bounded as $\delta \to 0$ for
$p \geq q$. To probe the **upper** boundary of the bound, one wants
$p \to q^{+}$ with $q^*$ slightly past Stein-Tomas; the test functions need to be
chosen more cleverly (e.g. Knapp examples — narrow caps with specific concentration).

## 5. Where I would push if I had more time

1. **Knapp example sweep.** Run the experiment with the canonical "Knapp examples"
   (test functions concentrated on a $\delta$-cap that saturate the conjectured
   bound). Verify the ratio approaches the conjectured constant from below.
2. **Bilinear extension.** Implement Tao-Vargas-Vega bilinear estimate
   numerically for two angularly-separated caps in $S^2$. Compare to the linear
   bound — bilinear should be strictly better.
3. **Decoupling on the paraboloid.** Sample the paraboloid $\{(x, |x|^2): x \in
   \mathbb{R}^{n-1}\}$ and verify the Bourgain-Demeter $\ell^2$-decoupling bound
   on a Schwartz test function in $n = 3$.

I did not start (1)–(3).

## 6. Per-attack metadata

| field | value |
|---|---|
| problem_id | `STEIN_RESTRICTION_N_GE_3` |
| attack_class | survey + Stein-Tomas calibration on indicator caps in $n = 2, 3$ |
| anchor_invoked | `Tomas-1975`, `Stein-1979`, `Carleson-Sjolin-Fefferman-1970` |
| failure_mode | `q-endpoint-gap-from-2(n+1)/(n-1)-to-2n/(n-1)` |
| computational_scope | $n=2$ at $200^2$, $n=3$ at $60^3$ — both bounded ratios confirmed |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | Tomas 1975, Stein 1979, Carleson-Sjölin, Bourgain 1991 |
| hazy_citations | Hickman-Rogers 2019, Guth 2016 — invoked from prompt, not re-fetched |
| reward_signal_capture_check | passed — calibration ratio stays bounded as expected; no novel claim |
| pattern_30_relevance | low |
| cross-problem-cluster | direct dual-link with P3 (Kakeya) and implies P5 (Bochner-Riesz) |

## 7. Honest read

The Stein-Tomas ratio $\|E g\|_{L^q} / \|g\|_{L^2}$ stays bounded (and in fact
decreases) for indicator-of-arc / indicator-of-cap test functions across a
factor-of-16 sweep in cap size, in both $n = 2$ and $n = 3$. This calibrates the
extension-operator machinery for both proved ($n = 2$) and partially proved
($n = 3$ at $L^2 \to L^4$) regimes.

The computational experiment did not probe the open part of the conjecture
(p along the conjectured line past Stein-Tomas in $n = 3$). To do that,
Knapp-example test functions and a separate sweep design are needed.

No estimate moved.

— Harmonia C, 2026-05-05
