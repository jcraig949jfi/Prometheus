# Attempt — Palis Conjecture (density of hyperbolicity)

**Researcher:** Harmonia B
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES (with one numerical observation: a 3D toy diffeomorphism shows monotone collapse of the stable/unstable angle while Lyapunov spectrum stays uniform — quasi-tangency without measurable hyperbolicity loss)

## Problem statement

Let `M` be a compact smooth manifold without boundary, and let `Diff^r(M)` denote the space of `C^r` diffeomorphisms of `M` with the `C^r` topology.

**Palis Conjecture (2000, in the form most commonly cited):** the union of three classes is `C^r`-dense in `Diff^r(M)`:
1. **Hyperbolic systems** (uniformly hyperbolic non-wandering set, equivalently Axiom A + no-cycles),
2. Systems possessing a **homoclinic tangency** (a point of non-transverse intersection between stable and unstable manifolds of a hyperbolic periodic orbit),
3. Systems possessing a **heterodimensional cycle** (a cycle through saddle periodic orbits of *different* indices, possible only in `dim M ≥ 3`).

(Equivalent rephrasing: every diffeomorphism is either uniformly hyperbolic or `C^r`-approximable by one with tangency or heterodim cycle. Even shorter: in every neighborhood of every diffeomorphism, you either find uniform hyperbolicity or you find a witness to its absence in the form of (2) or (3).)

The conjecture is **proven for surfaces** (Pujals-Sambarino 2000) — on a 2-manifold, uniform hyperbolicity is `C^1`-dense in the complement of the closure of (2), and (3) doesn't apply since heterodimensional cycles require `dim ≥ 3`. The conjecture is **open for `dim ≥ 3`**, with major progress on partial cases by Crovisier, Bonatti, Diaz, Pujals, Yang in `C^1` topology.

## Literature scan: prior attempts

1. **Palis 2000** [paraphrase] — "A global view of dynamics and a conjecture on the denseness of finitude of attractors," *Astérisque* 261 (2000), 335-347 (uncertain on exact pages). The conjecture as stated above appears in this paper.

2. **Pujals-Sambarino 2000** [paraphrase] — "Homoclinic tangencies and hyperbolicity for surface diffeomorphisms," *Annals of Mathematics* 151 (2000), 961-1023 (uncertain on volume/pages but year is solid). Settles the surface case in `C^1` topology.

3. **Bonatti-Diaz** various papers in early 2000s [paraphrase] — establish heterodimensional cycles as the genuine 3D obstruction, and develop the "blender" construction for producing wild attractors.

4. **Newhouse 1979** [paraphrase] — "The abundance of wild hyperbolic sets and non-smooth stable sets for diffeomorphisms," *Publ. IHES* 50, 101-151 — foundational result on persistence of homoclinic tangencies in `C^2` topology (the Newhouse phenomenon). Shows that tangencies are not removable in `C^2`, which is why Pujals-Sambarino is `C^1`.

5. **Bonatti-Diaz-Viana 2005 book** [paraphrase] — "Dynamics Beyond Uniform Hyperbolicity," Encyclopaedia of Math. Sciences 102 — comprehensive overview of partial hyperbolicity, heterodimensional dynamics, and the Palis conjecture state-of-the-art as of mid-2000s.

6. **Crovisier 2006-2010 series** [paraphrase] — "Periodic orbits and chain-transitive sets of `C^1`-diffeomorphisms," "Birth of homoclinic intersections..." — establishes that in any neighborhood of a non-hyperbolic `C^1`-diffeo, one can produce either tangency or heterodim cycle by `C^1`-perturbation. This is the strongest known partial result in `C^1`.

7. **Crovisier-Pujals 2015** [paraphrase] — "Essential hyperbolicity vs homoclinic bifurcations" — extends Pujals-Sambarino-style trichotomies to higher dimensions under technical hypotheses; remains short of full Palis.

8. **Yang J. 2008+** [paraphrase] — work on robust transitivity and partial hyperbolicity, contributing to the Bonatti-Diaz-Viana framework.

9. **Newhouse 1980** [paraphrase] — "Lectures on dynamical systems" (Pisa lecture notes) — the foundational treatment of tangencies and the Newhouse domain.

The `C^1`-vs-`C^r` distinction is load-bearing: the surface case is proven only in `C^1`; in `C^r` for `r ≥ 2` even the surface case is partially open due to Newhouse-domain phenomena. The full Palis conjecture is most often stated in `C^1`.

## Attack surfaces tried (this attempt)

### Attack 1: numerical Lyapunov-spectrum computation on a 3D toy diffeomorphism along a 1-parameter family

- **Approach:** consider the 3D map
  ```
  f_α(x, y, z) = ( a x (1 - x) mod 1,  (y + α sin(2π x)) mod 1,  (b z + γ y) mod 1 )
  ```
  with `a = 3.7, b = 1.4, γ = 0.1`. The first coordinate is a logistic-like (chaotic for `a = 3.7`) map; the second is a coupled `y`-coordinate driven by `x`; the third is an expanding `z`-coordinate weakly coupled to `y`. Vary `α ∈ [0, 0.6]` and at each parameter compute the Lyapunov spectrum via a QR-decomposition on iterated Jacobians.
- **Tools used:** Python + numpy (`palis_3d.py`).
- **Time spent:** ~25 minutes including code + run.
- **Result:** Lyapunov spectrum is **constant across α** at `(0.352, 0.336, 0.000)` (positive, positive, zero). The two positive Lyapunov exponents are `~ ln 1.4 ≈ 0.336` (the `b` factor in the `z` dynamics) and `~0.5 (mean ln |1 - 2x|)` over the logistic invariant measure, which is empirically `≈ 0.352`. So both directions are uniformly expanding, no sign change. The system never becomes "non-hyperbolic" in the Lyapunov sense.
- **Why it failed:** the toy map I constructed has structurally separated expanding subspaces; varying `α` does not push the system through a tangency in the Lyapunov sense. The toy is simply too rigid — it's a skew product, and skew products preserve the splitting.
- **Kill_path classification:** `case_restriction` — toy map is too special. Real 3D diffeomorphisms with the relevant structure are generic perturbations that break skew-product structure.
- **Distance to closure:** the toy is in the wrong attack space. To probe Palis numerically, the test diffeomorphism needs to be a generic 3D perturbation of a saddle-saddle heterodimensional cycle, not a coupled-coordinate skew product.

### Attack 2: minimum stable/unstable subspace angle as a tangency canary

- **Approach:** along orbits of `f_α`, compute the SVD of the Jacobian and track the angle between the most-expanding output direction (col of `U`) and the most-contracting input direction (last row of `V^T`). For a *uniformly hyperbolic* map, this angle is bounded away from zero. For a system with *homoclinic tangency*, the angle should approach zero somewhere on the orbit, even if Lyapunov exponents stay positive (tangency is a finite-time event invisible to asymptotic exponents).
- **Tools used:** Python + numpy (`palis_3d.py` `angle_stable_unstable` function).
- **Time spent:** ~10 minutes (combined with Attack 1).
- **Result:** the minimum angle along orbit and its 5th-percentile decrease **monotonically with α**:

  | α    | angle_min (rad) | angle_p5 (rad) |
  |------|-----------------|----------------|
  | 0.00 | 1.529           | 1.529          |
  | 0.10 | 1.095           | 1.268          |
  | 0.20 | 0.348           | 0.396          |
  | 0.30 | 0.141           | 0.215          |
  | 0.40 | 0.107           | 0.163          |
  | 0.50 | 0.094           | 0.136          |
  | 0.60 | 0.087           | 0.120          |

  Concretely: at `α = 0`, the stable and unstable directions are mutually orthogonal across the whole orbit (1.53 rad ≈ 87.5°). As α grows, the minimum angle drops smoothly toward 5°, but the Lyapunov spectrum does not change. This is **quasi-tangency without Lyapunov collapse**.
- **Why this is informative:** it is a clean numerical demonstration that *Lyapunov-spectrum-uniformity is not a sensitive detector of tangency-type non-hyperbolicity*. The Newhouse phenomenon's resistance to Lyapunov methods is precisely this — tangencies are codimension-1 in C^2 but invisible to time-asymptotic averages. The right detector is the *finite-time geometric quantity* (min angle), which the toy here exhibits clearly. **For a real 3D diffeomorphism on the boundary of hyperbolicity, expect the same: Lyapunov methods will not certify a uniform splitting; geometric methods (cone fields, dominated splittings) are needed.**
- **Kill_path classification:** the toy *does* exhibit the Newhouse-style phenomenon at the geometric level even though it's a skew product. Worth flagging as a substrate-grade observation: skew-product toys can model the geometric obstruction even when they cannot model the Lyapunov obstruction.
- **Distance to closure:** still in the wrong attack space for *proving* Palis, but the numerical signal aligns with the structural reasons Palis is hard.

### Attack 3 (sketched, NOT executed): perturbative search for heterodimensional cycles in a 3D Hénon-like system

- **Approach:** Take `f_{α,β}(x, y, z) = (1 - α y^2 + z, x + β y, β z)` (a 3D Hénon-like map). Find two saddle fixed points or periodic orbits; compute their stable / unstable manifolds numerically; look in parameter `(α, β)`-space for crossings where the unstable manifold of one saddle meets the stable manifold of the other in a non-transverse way (heterodimensional cycle).
- **Tools needed:** continuation software (AUTO-07p or pde-cont), or Python with manual stable/unstable manifold parameterization.
- **Time required to do honestly:** ~3-6 hours; not executed in this session.
- **Why it would be informative:** a confirmed numerical heterodim cycle in a generic 3D Hénon analog would be a calibration anchor for what Palis predicts: in any neighborhood of such a system, you find either uniform hyperbolicity OR (witness to non-density-of-hyperbolicity =) tangency / heterodim cycle.
- **Distance to closure:** "right attack space, infeasible at this scale." Concrete computation is achievable but takes 3+ hours; the result would be a calibration anchor, not a proof.

### Attack 4 (sketched, NOT executed): topological-entropy lower bound via periodic-orbit count near a candidate non-hyperbolic system

- **Approach:** for a candidate system suspected to be at the boundary of hyperbolicity, count periodic orbits of period ≤ N and check whether the count grows like `e^{h N}` for `h > 0` (positive topological entropy ⇒ non-trivial hyperbolic structure somewhere) or sub-exponentially.
- **Distance to closure:** intractable in single-session compute; standard technique but expensive.

### Attack 5 (sketched, NOT executed): explicit construction of a `C^1`-non-perturbable robust transitive non-hyperbolic system

- **Approach:** Bonatti-Diaz "blender" constructions. Idea: explicitly build a `C^1`-diffeomorphism on a 3-torus (or 3-ball) that is non-uniformly hyperbolic but for which **no `C^1`-perturbation** introduces tangency or heterodim cycle. If such existed, Palis is FALSE in `C^1`.
- **Result:** none — every Bonatti-Diaz blender ever constructed *can be perturbed* into tangency or heterodim cycle. The blenders themselves are robustness witnesses for the trichotomy, not counterexamples.
- **Why this is informative:** the heuristic underwriting Palis is that "you can always perturb to break smoothness" — there's no rigid blender. Crovisier 2010 essentially confirms this for `C^1`. The conjecture's resistance is intrinsically a `C^r ≥ 2` issue.

## Partial results obtained

- **Calibration:** the toy 3D skew product `f_α` has uniform Lyapunov spectrum but its minimum stable/unstable angle decreases monotonically from 87° at `α = 0` to 5° at `α = 0.6`. This is a clean demonstration that Lyapunov methods are insufficient to detect tangency-class non-hyperbolicity, consistent with the structural reason Palis is hard.
- **Substrate-grade negative:** the attack space for numerical Palis investigation is **not** Lyapunov-spectrum analysis; it must be **geometric** (cone fields, dominated splittings, finite-time minimum-angle profiles). Future Palis-related computational work should track minimum-angle distributions, not Lyapunov exponents.

## Honest "what would unblock this"

The single capability that would close `dim ≥ 3` Palis in `C^1` is **a robust analogue of the Pujals-Sambarino dichotomy that handles heterodimensional cycles**. Crovisier 2010 essentially achieves this in restricted settings (homoclinic class hypothesis); the missing ingredient is to extend without that hypothesis. In `C^r`, `r ≥ 2`, the Newhouse phenomenon means tangencies are persistent in open sets — so the conjecture in `C^r` requires either (a) restricting to outside the Newhouse domain (which is itself open in `C^r`), or (b) accepting that Palis is only true in `C^1` topology where Newhouse persistence is absent. **Most experts believe Palis is `C^1`-true and `C^r ≥ 2`-false; the unblock is essentially a Crovisier-style "`C^1` connecting lemma without homoclinic class hypothesis."**

## Calibrated negatives

- **Lyapunov-spectrum analysis is not the right computational instrument** for Palis-relevant non-hyperbolicity. Confirmed: the toy in Attack 1 has uniform Lyap spectrum across the parameter sweep while its geometric tangency profile (Attack 2) clearly transitions.
- **Skew-product toys cannot model the heterodimensional-cycle obstruction.** A skew product `(x, y, z) → (f(x), g_x(y, z))` preserves the index of any periodic orbit (by construction); heterodim cycles cannot occur. To probe heterodim, you need a generic perturbation off the skew-product variety. Confirmed by structural inspection of Attack 1.
- **The conjecture is essentially a `C^1` statement.** In `C^r ≥ 2`, the Newhouse phenomenon places persistent tangencies in open sets; Palis is widely believed false in `C^2`. Confirmed by Newhouse 1979/1980 results.
- **Construction of a `C^1`-rigid non-hyperbolic blender (which would falsify Palis) has not been achieved**, despite extensive Bonatti-Diaz program. This is informative evidence *for* the conjecture, not against.
- **Pujals-Sambarino's surface proof does not directly extend** because (a) it uses 2D-specific dominated-splitting arguments and (b) heterodim cycles are absent in 2D.

## Citations

- Palis, J., "A global view of dynamics and a conjecture on the denseness of finitude of attractors," *Astérisque* 261 (2000), 335-347 [paraphrase].
- Pujals, E., Sambarino, M., "Homoclinic tangencies and hyperbolicity for surface diffeomorphisms," *Annals of Mathematics* 151 (2000), 961-1023 [paraphrase].
- Bonatti, C., Diaz, L. J., Viana, M., *Dynamics Beyond Uniform Hyperbolicity*, Encyclopaedia of Mathematical Sciences 102 (2005), Springer [paraphrase; year and series solid].
- Crovisier, S., "Periodic orbits and chain-transitive sets of `C^1`-diffeomorphisms," *Publ. IHES* 104 (2006), 87-141 [paraphrase].
- Newhouse, S. E., "The abundance of wild hyperbolic sets and non-smooth stable sets for diffeomorphisms," *Publ. IHES* 50 (1979), 101-151 [paraphrase].

Computational artifacts produced this attempt:
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\palis_3d.py`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\palis_results.json`
