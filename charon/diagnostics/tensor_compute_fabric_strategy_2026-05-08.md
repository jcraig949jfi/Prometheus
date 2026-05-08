# Tensor Compute-Fabric Strategy

**Author:** Substrate-Tester (M1 instance)
**Date:** 2026-05-08
**Status:** Living document. Companion to `tensor_tooling_catalog_2026-05-08.md` (which catalogs the TOOLS); this document codifies the **strategic FRAMING** per James's 2026-05-08 directive.

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
