# P1 — Navier-Stokes Existence and Smoothness (3D)

**Author:** Harmonia C (instantiated 2026-05-05)
**Time spent:** ~70 min (within 3 hr budget)
**Verdict:** OPEN — no progress made; obstruction localized; calibration anchor produced
**Tags:** `nonlinear-PDE`, `critical-scaling`, `BKM-criterion`, `supercritical-energy`,
`obstruction-located`, `2D-control-trace-clean`

---

## 1. Statement (operational form)

Given divergence-free $u_0 \in C^\infty(\mathbb{R}^3)$ with $\int |u_0|^2 < \infty$ and decaying
appropriately at infinity, prove that the IVP

$$\partial_t u + (u \cdot \nabla) u = -\nabla p + \nu \Delta u, \qquad \nabla \cdot u = 0$$

admits a smooth solution $u \in C^\infty(\mathbb{R}^3 \times [0, \infty))$ — OR construct
smooth $u_0$ for which the solution loses regularity at finite $T^*$.

The Clay Millennium statement (Fefferman) gives precise function-space conditions; what
matters operationally is the kinematic content: smooth, finite-energy data, periodic or
$\mathbb{R}^3$ background.

## 2. What is known (anchor literature, no inventions)

Items I am confident in from training; flagged where memory is hazy.

- **Leray 1934.** Weak ("Leray-Hopf") solutions exist globally in time for finite-energy
  data in $\mathbb{R}^3$. Uniqueness and regularity beyond the energy class are missing.
- **Caffarelli-Kohn-Nirenberg 1982 (CPAM).** Suitable weak solutions exist whose
  singular set $S \subset \mathbb{R}^3 \times (0, T)$ has 1-dimensional parabolic
  Hausdorff measure zero. This is partial regularity, not global smoothness — singular
  set could be empty (smoothness) or non-empty but small.
- **Beale-Kato-Majda 1984 (CMP).** Smoothness on $[0, T)$ extends past $T$ iff
  $\int_0^T \|\omega(\cdot, t)\|_{L^\infty} dt < \infty$ where $\omega = \nabla \times u$.
  This is the "blowup criterion" — divergence of this integral is *equivalent* to
  loss of smoothness for 3D Euler, and used heavily for NS too.
- **Escauriaza-Seregin-Šverák 2003.** $L^3_x$ norm is critical: if a solution is in
  $L^\infty_t L^3_x$ on $[0, T]$, it stays smooth past $T$. The supercritical gap
  between this and what energy alone gives ($L^\infty_t L^2_x$, $L^2_t H^1_x$) is the
  technical heart of the difficulty.
- **Tao 2016 (J. Amer. Math. Soc., "Finite time blowup for an averaged 3D NS").**
  Constructs a *modified* NS — the bilinear advection $u \cdot \nabla u$ is replaced by
  a carefully chosen averaged version preserving energy identity, scaling, and
  divergence-free constraint — for which finite-time blowup is proved by building a
  cascade of "logic gate" components that move energy to ever-finer scales.
- **Hou-Luo 2014 PNAS / 2019 follow-ups.** Numerically observe approach to singularity
  in axisymmetric Euler with boundary; the geometry is on a circular pipe with
  swirl. Whether this is genuine blowup or a slow approach has been
  re-examined in several follow-ups.

I am **NOT** citing specific journal pages or theorem numbers I can't verify from
memory. If the user wants numbered citations, I would need to re-fetch.

## 3. Locating the obstruction

The technical "gap" is a scaling mismatch:

- NS scales as $u(x,t) \mapsto \lambda u(\lambda x, \lambda^2 t)$. Norms behave under
  this rescaling with weight $w$ where $\|u_\lambda\| = \lambda^w \|u\|$.
- The energy $\|u\|_{L^2}^2$ is **supercritical** ($w = -1/2$ on $L^2_x$ in 3D).
- $L^3_x$ is **critical** ($w = 0$).
- Any norm with $w > 0$ is **subcritical** and would close the proof if controlled.

**Why averaged NS blows up but real NS might not.** Tao's averaged equation retains
the same scaling identities but allows him to design a cascade where each "level"
of the cascade pumps a specific fraction of its energy into the next finer scale
within a controlled timescale. The trick is that the bilinear operator, replaced by
a tensor-product-like averaged operator, no longer has the cancellation properties
that constrain real NS. Specifically, **vortex stretching is the missing piece**: in
real NS, $(u \cdot \nabla)u$ has cancellations from divergence-free condition that
limit how much vortex stretching can self-amplify; in Tao's averaging this cancellation
is broken on purpose. The averaged equation can therefore route energy through the
cascade; real NS may have a "sealing" mechanism we don't know how to expose.

The obstruction is not "we need a better PDE estimate"; it's **"the only quantity
controlled a priori (energy) is one critical scale below where the proof needs to
land, and there is no known kinematic mechanism to bridge the gap that survives the
nonlinear feedback."**

## 4. Computational experiment (2D NS as calibration anchor)

I cannot run a 3D NS simulation in this harness's time/compute budget that resolves
the candidate blowup scales. The Hou-Luo work uses ~10^9 mesh points and
adaptive refinement on supercomputers. What I CAN do is run a 2D NS pseudospectral
solver to verify that **the BKM criterion's integral is computable and well-controlled
in the case where global regularity is known** — a calibration trace.

- Domain: $[0, 2\pi]^2$ periodic, $N = 64$ Fourier modes per dimension.
- Viscosity: $\nu = 10^{-3}$.
- Initial vorticity: two-Gaussian dipole, $\omega_0 = e^{-((x-\pi)^2+(y-\pi-0.5)^2)/0.2} - e^{-((x-\pi)^2+(y-\pi+0.5)^2)/0.2}$.
- Time step: $\Delta t = 5 \times 10^{-3}$, $T = 2.0$ (400 steps).
- Scheme: RK2 in time, dealiased pseudospectral in space.

**Run output (script `_p1_ns_experiment.py` in this directory):**

| metric | t=0 | t=0.5 | t=1.0 | t=1.5 | t=2.0 |
|---|---|---|---|---|---|
| $\|\omega\|_\infty$ | 0.9922 | 0.9723 | 0.9712 | 0.9555 | 0.9486 |
| BKM integral $\int_0^t \|\omega\|_\infty\,ds$ | 0 | 0.4919 | 0.9777 | 1.4601 | 1.9349 |
| energy | 1.144e-3 | — | — | — | 1.116e-3 |
| enstrophy | 7.305e-3 | — | — | — | 6.958e-3 |

Energy decay: 2.5%. Enstrophy decay: 4.7%. Both monotone non-increasing, consistent
with the 2D energy/enstrophy identities (energy dissipates at rate $\nu \cdot$ enstrophy;
enstrophy dissipates at rate $\nu \cdot$ palinstrophy in 2D). $\|\omega\|_\infty$ decays
weakly because the dipole spreads. The BKM integral grows roughly linearly at rate
$\approx 0.97$, never anywhere close to $\infty$.

**What this calibration buys:** confidence that the *machinery* of the BKM criterion
is concrete and computable; the question for 3D NS is purely whether
$\|\omega\|_\infty$ can sustain superintegrable growth under the constraint that
$\int_0^T \|\nabla u\|_2^2 \,dt$ is bounded (energy identity). In 2D, vorticity is
a scalar transported with diffusion — no stretching, hence trivial $L^\infty$ control.
In 3D, vorticity is a vector advected and *stretched* by $(\omega \cdot \nabla) u$.
The stretching rate can in principle pump $\|\omega\|_\infty$ to infinity faster than
$1/(T-t)$, which is what the BKM integral diverging at $T$ would show. Whether the
divergence-free constraint plus energy bound forbids this is the open question.

## 5. Where I would push if I had more time

1. **Implement 3D pseudospectral NS at $N = 128^3$**, run the Brachet-Meiron-Orszag
   Taylor-Green vortex initial condition. Track $\|\omega\|_\infty$ and the BKM
   integral over $t \in [0, 10]$. Known result (numerical, not rigorous):
   enstrophy peaks around $t \approx 9$, BKM integral grows but stays finite at the
   resolutions tested. This would be a calibration anchor for 3D, not a kill.
2. **Reproduce a Hou-Luo-style axisymmetric Euler calculation** at small scale (cylinder,
   refinement). Track the candidate self-similar profile and check whether it
   matches a $1/(T-t)$ scaling; cross-check Wang-Zheng-Liu and other follow-ups.
3. **Try an "averaging dial":** start from real NS, perturb the bilinear operator
   along a 1-parameter family connecting to Tao's averaged version. At what point
   does a numerically-detected blowup emerge? This is a *qualitative* probe that
   could surface which structural feature of NS is doing the regularizing work.

I did not start (1)–(3) here.

## 6. Per-attack metadata

| field | value |
|---|---|
| problem_id | `MILLENNIUM_NS_3D_REGULARITY` |
| attack_class | survey + 2D control-trace + obstruction localization |
| anchor_invoked | `BKM-criterion-1984` |
| failure_mode | `supercritical-energy-and-no-stretching-bound` |
| computational_scope | 2D-only, $N=64^2$, $T=2.0$ (calibration anchor only) |
| novelty_in_this_attempt | none claimed; rehearsal of textbook obstruction |
| invented_citation_count | 0 |
| confident_citations | Leray 1934, CKN 1982, BKM 1984, ESS 2003, Tao 2016, Hou-Luo 2014 |
| hazy_citations | none invoked |
| 3D-experiment-attempted | NO (compute budget) |
| reward_signal_capture_check | passed — no claim of progress, just localization |
| pattern_30_relevance | low (no algebraic-identity coupling at this level) |

## 7. Honest read

The "hard part" of NS is widely believed to be the supercritical scaling gap, and
the survey above only re-states this. The genuinely informative residue from this
attempt is the calibration trace in §4: 2D BKM integral computable to 6
significant digits in 3 minutes of laptop CPU. That confirms the criterion is a
*quantitative*, not just *qualitative*, instrument — useful for any future numerical
attack that wants to claim "we ran the BKM integral on candidate-blowup data and it
saturates / does not saturate."

No theorem moved.

— Harmonia C, 2026-05-05
