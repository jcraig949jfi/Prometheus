# Tensor Compute-Fabric Strategy

**Author:** Substrate-Tester (M1 instance)
**Date:** 2026-05-08
**Status:** Living document. Companion to `tensor_tooling_catalog_2026-05-08.md` (which catalogs the TOOLS); this document codifies the **strategic FRAMING** per James's 2026-05-08 directive.

**🔴 SUPERSEDING POSTURE (2026-05-08, late):** Tensor mathematics is now **HARD POSTURE / "near and dear to Prometheus"** per `feedback_tensors_near_and_dear.md`. The **canonical 104-entry catalog at `aporia/mathematics/tensor_open_problems_v1.md`** is the authoritative reference for substrate-grade tensor open problems. Five tensor-specific attack paradigms (P27-P31) are codified in `aporia/docs/attack_angle_taxonomy.md`: slice rank / asymptotic spectrum / border apolarity / tensor network contraction / secant variety geometry.

Substrate-Tester's Lane 12 (representation-pressure) now **pulls capability-gap probes directly from the 104-entry catalog** rather than inventing novel objects. The 5-of-5 capability-gap pattern I surfaced across fires #7-#35 (homotopy / designs / HOMFLY / A∞ / group reps) is independently re-discovered framing of a SUBSET of the territory the catalog formalizes more rigorously. Likely substrate primitives needed (per the canonical reference): `TensorNetwork`, `AsymptoticSpectrumMonotone`, `BorderApolarityWitness`, `MomentPolytope`, `SecantVarietyEquation`.

Tickets queued (filed by Aporia 2026-05-08):
- **`T-2026-05-08-T038`** — Techne: classify all 104 entries by substrate-primitive needs; surface capability gaps.
- **`T-2026-05-08-E009`** — Ergon: for each entry with computational hooks, design probe-shape for v1.0 corpus.
- Substrate-Tester tracks both tickets' progress + amplifies via lane 12 probes.

**The shift:** tensors are not just a tooling option. They are a **compute-fabric strategy** for delaying the local-lab → expensive-cloud-compute transition as substrate complexity grows exponentially. NP-hard problems are coming; brute force is the substrate's current default; tensor methods are mathematically known to compress exponential state spaces into polynomial ones (when the underlying structure is exploitable).

---

## The strategic problem

**Compute scaling reality (M1 + M2 evidence):**
- Lehmer brute-force at (deg-14, ±5): 97M polys, ran in past sessions.
- (deg-12, ±5): 8.86M polys, ~7 min wall-clock (fire #6).
- (deg-10, ±5): 805K polys, ~26s (fire #20).
- (deg-10, ±7): 5.3M polys, ~3 min (fire #31).

The pattern is exponential: small parameter changes → order-of-magnitude compute swings. A single jump to (deg-14, ±7) would be ~6× larger than (deg-14, ±5) ≈ 580M polys ≈ ~5 hours sequential. Two parameter steps further and we're in cloud-compute territory.

**The NP-hard surfaces in the substrate (current + emerging):**
1. **Lehmer-style brute-force enumeration** — exponential in `(coef_bound + 1)^(half_degree - 1)`. Already at the local-lab edge.
2. **Cross-operator triangulation independence checks** — currently small N; `N choose K` scaling means it goes combinatorial fast.
3. **Constraint satisfaction in OmegaOracle / verification chains** — hidden, growing.
4. **Search over operator compositions** — currently ad-hoc; may become combinatorial as the operator vocabulary grows.
5. **Orbit / equivalence-class enumeration** — the 5-of-5 capability-gap cluster (homotopy / designs / HOMFLY / A∞ / group reps) all hide orbit-space problems with combinatorial blowup.
6. **Cross-(degree, coef-bound) sweet-spot characterization** — the "tensor-flavored" finding from fire #31; landscape exploration is high-dim.

**The tensor-methods → NP-hard-class mapping:**

| Method | Compresses | Polynomial-rank when | Substrate fit |
|---|---|---|---|
| CP / PARAFAC decomposition | Low-rank tensor approximation | True multilinear rank is low | Latent operator-axis structure in unified signature tensor (HARD-3) |
| Tucker decomposition | Multilinear rank reduction | Each-mode rank is low | Sister to CP; useful for cross-operator joints |
| **Tensor Train (TT)** | 1D-structured exponential state space | Bond dimension stays bounded | **Lehmer brute-force candidate; cross-operator joint** |
| Hierarchical Tucker | Tree-structured high-dim | Hierarchical rank low | Compositional operator search |
| MPS / MPO (matrix product) | Quantum many-body / 1D-area-law | Entanglement bounded by area law | Triangulation chains; certificate composition |
| PEPS / 2D networks | 2D state spaces | Approximate (PEPS contraction is NP-hard) | Cross-domain joint distributions |
| MERA | Multi-scale entanglement | Scale-free / RG-flow systems | Substrate's scale-invariant patterns (cross-degree scaling) |
| DMRG | Exponential ground states | When system is locally interacting | Optimization over verification chains |

**The headline: TT (tensor train) and MPS/MPO are the substrate's most plausible near-term candidates.** Both compress exponential 1D-structured state spaces to polynomial cost when bond dimension stays bounded. Both have mature implementations (TensorLy for TT; ITensor for MPS/MPO).

---

## Walk-before-run roadmap

Three tiers, concrete and ordered:

### Walk-1 (low cost, high information): TT-rank study on Lehmer 8-coef tensor

**Hypothesis:** the deg-14 ±5 palindromic Lehmer brute-force can be cast as a tensor of shape `[11]^8` (each coef ∈ [-5, 5] = 11 values; palindromic constraint reduces full deg-14 to half-vector of 8 values). The tensor-valued function is `M_in_band(coeffs) ∈ {0, 1}` (or M-value for richer signal). **TT decomposition rank study** would reveal whether the in-band region has low-rank structure.

**Why it matters:** if TT bond dimension stays small (say <50), we can ENUMERATE the in-band region via low-rank reconstruction WITHOUT visiting all 97M polys. That's a direct order-of-magnitude compute reduction. If bond dimension blows up, we've learned the in-band region is structurally NOT low-rank — also valuable.

**Tooling:** TensorLy (Python, NumPy/PyTorch backend). 1-2 days of substrate work; prototype only.

**Trigger to start:** Aporia files a coordination ticket OR the substrate's compute pressure on Lehmer-style enumeration becomes blocking.

### Walk-2 (medium cost, high information): TensorLy as a backend for the unified signature-keyed tensor

**Trigger:** the unified tensor (HARD-3 Priority #1) lands with real operator-output content. NOT before.

**Action when triggered:** Aporia coordination ticket → Tier-2 evaluation per `tensor_tooling_catalog_2026-05-08.md`. Run CP / Tucker / TT decompositions on the unified tensor; report rank profiles per operator-axis. The output is "where in operator-space does latent structure exist" — substrate-grade signal for the unified-tensor steering.

**Tooling:** TensorLy + TensorLy-Torch (PyTorch or JAX backend).

**Why it matters:** the unified tensor is the substrate's central artifact (HARD-3). Decomposition is the canonical first analysis once it has content.

### Walk-3 (medium cost, future-direction): MPS / ITensor probe of one cross-operator joint

**Trigger:** an N-operator joint distribution surfaces as exponential-in-N (currently no Substrate-Tester signal; flag for fire-watch).

**Action when triggered:** prototype encoding of the joint as MPS in ITensor (or a Python wrapper if Julia adoption is too heavy). Bond-dimension study + contraction cost. Report whether MPS area-law applies (substrate-style "informational channels" framing predicts it should, for compositionally-structured operators).

**Tooling:** ITensor (Julia preferred; Python wrappers available).

**Why it matters:** ITensor's diagrammatic + index-aware framing is substrate-aligned; MPS area-law is exactly the "compress exponential to polynomial" lever James is pointing at.

### Run (longer-term, requires substrate maturity):

- **JAX-backed substrate primitives** when differentiable substrate operations land (Apollo / Rhea trainable phase).
- **PEPS / 2D-network contraction** for full cross-domain operator joint distributions.
- **DMRG** for optimization over verification chain selection.
- **MERA** if substrate's cross-scale invariants (cross-degree scaling per fire #20) reveal RG-flow structure.

None of these are near-term. They're targets to walk toward.

---

## Walking discipline (HARD-2 vigilance)

The trap: "we should adopt JAX/TensorLy/ITensor/all-of-it." That trap is the gravitational well. The substrate doesn't need a tensor framework wrapper around it; it needs **specific tensor methods applied to specific NP-hard surfaces** to delay compute walls.

**Required for any walk-experiment to start:**
1. **Concrete substrate problem** that's tensor-amenable AND blocking.
2. **Prototype scope** — single experiment, not framework adoption.
3. **Falsifiable rank/cost target** — bond dimension bound, or polynomial-vs-exponential ratio, that determines walk success/failure.
4. **Aporia coordination** — strategic decisions go through Aporia, not through Substrate-Tester unilaterally.

**NOT required (and to avoid):**
- "Let's use [framework] because the README is impressive."
- "Refactor existing substrate primitives to be tensor-typed." (HARD-3 says SUBSTRATE-PRIMITIVE comes before TENSOR-TOOL adoption.)
- "Rewrite the kernel in JAX." Hard NO. The Sigma kernel's content-addressing discipline is more important than JIT-compilation.

---

## The class of problems worth solving in tensor space

Per James's directive: "if there is a class of problems within tensor space to solve, evolving our tools in that direction may make sense sooner than later."

The class is now identified:

> **Exponential-state-space-with-1D-structure problems**, where 1D-structure means there's a natural ordering (degree, coef position, operator chain depth, scale level) along which area-law-style compression is mathematically sound.

Specific instances within the substrate:
1. **Palindromic-polynomial brute-force** → 1D structure: half-coefficient position (Walk-1).
2. **Cross-operator joint** → 1D structure: operator-application order (Walk-3).
3. **Triangulation chain** → 1D structure: path depth (related to Walk-3).
4. **Cross-(degree, coef-bound) sweet-spot landscape** → 2D structure: PEPS-flavored.

Each has area-law-or-similar mathematical structure that justifies tensor-network compression. Each is currently NP-hard or exponential. Each has a measurable rank/cost target.

This is the **substrate-grade rationale** for evolving tensor tools, not a "framework adoption" rationale.

---

## Three framings, not two (per James 2026-05-08 correction to both AI takes)

Both my original framing AND ChatGPT's review framing missed the third axis. The complete picture has THREE framings, each addressing a different strategic question:

| Framing | Strategic question | Method examples |
|---|---|---|
| **Defensive** (my original) | "How do we delay the local-lab → cloud-compute transition?" | TT/Tucker decomposition of pre-existing arrays; MPS compression of computed states |
| **Diagnostic** (ChatGPT's review) | "Does substrate structure collapse onto low-dimensional manifolds?" | Rank study; bond-dimension measurement; correlation-decay analysis |
| **Offensive** (James's correction) | "What can tensors enable us to compute that we COULDN'T otherwise compute at all?" | **TT-cross / cross-approximation; QTT; sparse-grid quadrature; active subspaces** |

The offensive framing is genuinely different. It's not about "we have N-dim brute force; tensor compresses it." It's about **we have N-dim spaces we couldn't enumerate at all; tensor methods let us SEARCH them**.

### Offensive method catalog

**TT-cross / TT-completion** (Oseledets, Goreinov, et al.) — adaptive cross-approximation algorithms that build a low-rank tensor train from a small number of function evaluations. Polynomial time in dimension when the underlying function has bounded TT-rank. Used for:
- High-dim Bayesian optimization (search complex landscapes)
- Function approximation on `[N]^d` where naive grid search is infeasible
- Combinatorial optimization where the full landscape is exponential but structure permits sampling

**QTT (Quantics Tensor Train)** — represents continuous functions via binary-encoded TT, achieving polynomial cost on continuum problems that classical methods make exponential. Used for:
- High-dim PDE solving on local hardware
- Continuum integration over `[0, 1]^d` for very large d

**Sparse-grid quadrature (Smolyak)** — combines low-dim quadratures into high-dim integrals with cost polynomial-in-d instead of exponential. Used for:
- Multi-dim integration with bounded mixed regularity
- Reduces high-dim integration to a substrate-feasible budget

**Active subspaces** — discovers a low-dim subspace where the function actually varies, then operates only in that subspace. Used for:
- Sensitivity analysis on high-dim parameter spaces
- Reduced-order models when the effective dimensionality << ambient dimension

### Offensive substrate use cases (concrete)

Where the substrate could **enable computations that don't currently exist as feasible options**:

1. **deg-16+ Lehmer enumeration via TT-cross adaptive search**. Currently capped at deg-14 ±5 (~97M states; brute force feasible). deg-16 ±5 ≈ 2.4B states — infeasible on local hardware. **TT-cross** with the in-band-indicator function would adaptively sample only where in-band density is high. If the in-band region has low-rank structure (Walk-1's diagnostic answer), TT-cross enables a domain (deg-16) that's currently closed to us entirely.

2. **Operator composition search**. Search the space of N-step operator compositions for "interesting" combinations (high information yield, near-misses, novel intersections). Naive: combinatorial explosion in N. **TT-cross on the operator-composition tensor** with an "interesting score" function: polynomial time IF the score landscape has low-rank structure. Enables compositional discovery the substrate currently can't do.

3. **Counterexample search in high-dim conjecture spaces**. For a conjecture "∀ params ∈ `[low, high]^N`, property P holds," **TT-cross with the property-violation indicator** can search for counterexamples in spaces too large for grid search. This is a candidate Aporia tool — flip "exhaustive verification infeasible" to "adaptive search for failure cases feasible."

4. **High-dim Bayesian optimization over substrate-tester probe parameters**. The N-dim space of (lane-1-thru-18 × probe configurations × seed/threshold tunings × stratification choices) is too large for grid search; **TT-cross BO** could find probe configurations with high yield-per-fire that we'd never reach by hand.

5. **Cross-(degree, coef-bound, palindromic-class, ...) sweet-spot characterization**. Fire #31 surfaced the deg-10 sweet-spot finding (±5 yields hits; ±3 and ±7 don't). The full landscape across (degree, coef-bound, palindromic-class, etc.) is high-dim. **Sparse-grid quadrature or TT-cross** would map the whole sweet-spot manifold without exhaustive enumeration.

### The shift this represents

The offensive framing changes Walk-1's purpose. The original Walk-1 framing answered the diagnostic question ("can we compress this?"). The upgraded framing answers BOTH questions simultaneously:

| Question | Walk-1 measurement |
|---|---|
| **Diagnostic:** does the in-band region have low-rank structure? | Bond-dimension profile across rank-truncation levels |
| **Offensive:** could TT-cross adaptively SEARCH this lattice? | Same bond-dimension measurement IS the answer — bounded bond dim → TT-cross is feasible |

Walk-1 outcome interpretations:
- Bond dim < 50 → **both** "structure compressible" (diagnostic-pass) AND "TT-cross adaptive search viable" (offensive-pass). Unlocks deg-16 enumeration as a candidate domain.
- Bond dim ~50-200 → ambiguous; further structural analysis needed.
- Bond dim >> 200 → both diagnostic-fail AND offensive-fail. Lehmer in-band region is genuinely incompressible / non-low-rank; tensor methods don't help here. Other compression geometries (categorical, evolutionary, sparse symbolic) become the candidates.

**The strategic upgrade:** the substrate's tensor-tool roadmap now has TWO independent leverage points:
- **Compress what we already compute** (defensive framing; modest gains)
- **Compute what we currently can't** (offensive framing; potentially transformative)

Walk-1 result determines which leverage is available for the Lehmer surface; future walk-experiments determine the same for cross-operator joints, conjecture counterexample spaces, etc.

---

## Strategic upgrade (per ChatGPT 2026-05-08 review)

ChatGPT's review of this doc and the related charter sharpened several framings worth codifying:

### Upgrade 1: the discriminator is **compressible locality under an ordering**, not "1D-ness"

My original framing — "exponential-state-space-with-1D-structure" — was correct in shape but loose in property. The sharper framing:

> Tensor methods become leverage **when there exists an ordering under which information density obeys compressible locality**.

A 2D-structured space CAN be compressible (PEPS, MERA hierarchies). A 1D-structured space CAN be incompressible (random-SAT instances). The discriminator is locality + correlation decay, not dimensionality. Walk-1 (Lehmer TT-rank study) tests this property directly — bond dimension growth IS the locality measurement.

### Upgrade 2: "Tensors as camouflage for brute force" is a real failure mode

When bond dimension explodes during a walk-experiment, the substrate is *worse off* than before — false epistemic comfort. The tooling looks sophisticated; the underlying problem is unchanged; agents downstream may treat the tensor encoding as "solved" when it's just brute force in a wig.

**Detection rule for walk-experiments:** unbounded bond-dimension growth must be reported as a **failure**, not as "still working on it." A failed walk-experiment that produces a clear NEGATIVE result ("this region is incompressible") is more valuable than a partial-success that hides cost. **Falsifiable benchmark with informative-failure semantics** is non-negotiable.

### Upgrade 3: Tensor-Admissibility Criteria (the gating predicate)

Before any subsystem becomes tensorized, require ALL seven:

| Criterion | Measurable signal |
|---|---|
| 1. Stable ordering exists | named axis (coef position, operator-chain depth, etc.) |
| 2. Locality hypothesis exists | nearby-position interactions dominate |
| 3. Empirical correlation decay | measurable from sample data |
| 4. Compressibility measurable | TT-rank / bond-dimension can be bounded |
| 5. Bond growth polynomial | not exponential as system size grows |
| 6. Falsifiable benchmark exists | compression-threshold target set in advance |
| 7. Failure informative | negative result reveals structural property, not just "didn't work" |

Walk-1 (Lehmer TT-rank study) satisfies #1, #2, #4, #6, #7 by design. Criterion #3 (correlation decay) is the open question the experiment will answer. Criterion #5 is the falsifiable target.

### Upgrade 4: tensors are a **probe**, not the goal

The strategic question is NOT "should we use tensors?" It is:

> **Does substrate structure naturally collapse onto low-dimensional manifolds?**

Tensors are one probe for that question. Other probes for the same question include:
- **Probabilistic programs** (over latent generative models)
- **Categorical rewrites** (the 5-of-5 capability-gap cluster's natural geometry — closer to topos theory than tensor decomposition)
- **Graph grammars** (operator composition algebra)
- **Sparse symbolic operators** (when most entries are zero / canonical form)
- **Homotopy structures** (closely related to ST-fire1-002 + ST-fire21-002 capability gaps)
- **Evolutionary search** (when no analytical compression geometry exists)

The substrate may eventually need DIFFERENT compression geometries for different surfaces. The 5-of-5 capability-gap cluster (homotopy, combinatorial design, HOMFLY, A∞-algebra, group representation) likely wants **categorical rewrites** more than tensor decomposition — these are structural/symbolic compression, not numerical. Tensor methods are RIGHT for the substrate's enumeration / search / joint-distribution surfaces; they are NOT obviously right for the equivalence-class surfaces.

**Charter rule (added):** when surfacing a substrate-pressure problem, evaluate compressibility candidates across MULTIPLE geometries (tensor, categorical, graph, probabilistic, etc.), not just tensor. Filing a Walk-1 candidacy is contingent on the problem being clearly tensor-shaped (Tensor-Admissibility Criteria #1-#7), not just "high-dimensional."

### Upgrade 5: developmental-order vindication (and the trap to keep avoiding)

ChatGPT named the developmental order Prometheus is following: ontology → invariants → compression-geometry → asymptotic scaling. Most teams jump to compute (GPUs, distributed systems, JAX migrations) before having canonical primitives or trustworthy invariants — they create *faster chaos*. The substrate's deliberate ordering (ontology + falsification first, compression-geometry only when topology suggests it) is the high-leverage discipline.

**The trap to keep avoiding:** premature collapse onto one computational religion. Every ambitious system has a moment where one framing (ML / probabilistic / categorical / tensor) starts to feel like THE answer. That feeling is the warning sign, not the green light. Keeping multiple compression-geometry candidates open is a discipline, not indecision.

---

## Charter additions (Substrate-Tester, codified)

1. **On every capability-gap or substrate-flaw ticket:** include "tensor-tool fit" assessment in payload (existing). UPGRADED: when a substrate-pressure problem with exponential-state-space-with-1D-structure structure surfaces, file an Aporia coordination ticket flagging Walk-1/2/3 candidacy.

2. **Quarterly compute-pressure check (informal cadence):** when substrate-tester observes a fire whose wall-clock is >20% of the 50-min cap on enumeration / search / verification, flag whether the NP-hard surface has tensor-amenable structure.

3. **Trigger conditions for walk-experiments are now codified** (in this document + memory). Substrate-Tester or another agent identifying a trigger fire files an Aporia coordination ticket; Aporia decides walk authorization.

4. **HARD-2 vigilance maintained:** "use [framework]" is not "build the substrate." Tensor tools evaluated on substrate-grade fit + NP-hard-surface compression target, not on convention.

---

## References

- James's tensor-ecosystem catalog message 2026-05-08 (TensorLy, TensorLy-Torch, JAX, PyTorch, ITensor, cuTensor*, Sage/Macaulay2/Singular).
- `charon/diagnostics/tensor_tooling_catalog_2026-05-08.md` — companion catalog of TOOLS (this doc covers STRATEGY).
- `feedback_tensor_first.md` (auto-memory) — HARD-3 priority: substrate's own unified tensor primitive comes BEFORE tensor-tool adoption.
- `feedback_anti_gravitational_well.md` (auto-memory) — HARD-2: don't drift toward conventional framework adoption.
- `feedback_tensor_tooling_charter.md` (auto-memory) — Substrate-Tester charter addition (initial; this doc upgrades it).

---

## Living document

Updates land via Substrate-Tester fires when:
- A walk-experiment trigger fires
- A new substrate-pressure problem surfaces with tensor-amenable structure
- A walk-experiment completes (success or rank-blowup; either is informational)
- A new tensor method enters the ecosystem worth evaluating

— Substrate-Tester, M1 instance, 2026-05-08
