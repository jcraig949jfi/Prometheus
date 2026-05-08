# Tensor Tooling Catalog — Substrate-Grade Fit Assessment

**Author:** Substrate-Tester (M1 instance)
**Date:** 2026-05-08
**Purpose:** Per James's directive 2026-05-08, this catalog is now part of the Substrate-Tester charter. When surfacing capability-gap findings or substrate-design observations, future fires should consider whether one of the tools below would close the gap. This is a living document; updates land via Substrate-Tester fires.

**Hard-rule discipline:** HARD-2 (anti-gravitational-well) applies unconditionally. Tensor tools are useful WHEN they solve substrate-pressure problems; they are NOT a default replacement for substrate-grade primitives. "Use TensorLy" is not the answer to "build the substrate"; it's the answer to "we have an existing array-shaped subspace of the substrate that decomposition would compress."

HARD-3 (tensor-first) makes the unified signature-keyed tensor Priority #1. Tensor *tools* come AFTER the substrate's own tensor *primitive* exists.

---

## The three tensor worlds

Per James's framing 2026-05-08, three distinct ecosystems:

| World | Goal | Substrate fit |
|---|---|---|
| Numerical tensor computation | Fast multidim algebra | Tier 3 — useful once we have a unified tensor |
| Tensor decomposition / geometry | Discover latent structure | Tier 2 — useful for finding operator-axis structure |
| Tensor networks / physics | Compress exponential state | Tier 1 — closest to "informational channels + composition" framing |

---

## Library catalog

### Tier 1 — closest fit to substrate framing

**ITensor** (julitensors.org) — index-aware tensor algebra + diagrammatic programming. Used heavily in quantum many-body / MPS-MPO. **Substrate fit:** thinks in graph topology + contraction geometry, which matches the substrate's "informational channels" + "compositional falsification surfaces" framing better than NumPy's array bookkeeping. Strong fit IF a future substrate evolution adds operator-graph contraction.

**Status:** evaluate when the substrate has a multi-operator joint distribution worth contracting (not yet).

### Tier 2 — useful once unified tensor exists

**TensorLy** (tensorly.org) — "NumPy for tensor geometry and decomposition." CP, Tucker, TT, PARAFAC2, tensor regression. Multi-backend (PyTorch / JAX / TF). GPU. **Substrate fit:** highest-leverage starting point IF we want to find latent structure in the unified signature-keyed tensor (HARD-3 Priority #1). Until that tensor exists with real content, TensorLy adoption is premature.

**TensorLy-Torch** (tensorly.org/torch) — tensor decompositions as native NN layers (factorized convolutions, tensorized linear layers, low-rank structure learning). **Substrate fit:** "latent geometric structure as a learnable computational primitive." Aligned with symbolic compression + emergent latent channels — but only relevant once the substrate has trainable components (Apollo / Rhea), which the current discipline DEFERS until the unified tensor exists.

**Status:** queue for evaluation when (a) unified tensor populated with substrate-grade content AND (b) Aporia approves a "decompose-and-discover" workstream.

### Tier 3 — raw computational power (mostly tooling layer)

**JAX** (jax.dev) — compiled tensor algebra, differentiable programming, functional tensor rewriting, accelerator compilation. **Substrate fit:** functional + content-addressed style aligns with substrate's content-addressing discipline (hashes, not mutations). Compiler-thinking matches Sigma-kernel's def-blob architecture. **Higher leverage than PyTorch for substrate work** because the substrate's eager-vs-functional mismatch is a real friction.

**PyTorch** (pytorch.org) — flexible research substrate. **Substrate fit:** high-friction with substrate's content-addressing discipline (mutable tensors fight frozen-dataclass hygiene). Useful for prototyping but not for substrate primitives.

**TensorFlow** — production ecosystems. **Substrate fit:** weak — production-ML framing, not substrate research.

**cuTensor / cuTensorNet / TensorRT** (NVIDIA) — high-performance contractions + tensor-network contraction + optimized inference. **Substrate fit:** infrastructure layer; relevant only if contraction-time dominates (it doesn't for the substrate yet; tensor doesn't exist).

**Status:** JAX is the strongest candidate for substrate adoption when differentiable operations land. PyTorch is acceptable for prototypes. TensorFlow + cuTensor + TensorRT are out-of-scope for the current substrate phase.

### Tier 4 — algebraic geometry (tensor problems are secretly variety problems)

**SageMath, Macaulay2, Singular** — algebraic geometry tooling. Tensor problems often hide as: secant variety problems, orbit closure problems, invariant theory problems, singularity problems. **Substrate fit:** indirect but real; relevant for the structured-equivalence-class meta-primitive (the 5-of-5 capability-gap cluster). Sage/Macaulay2 already in the substrate's intellectual ecosystem; no new tooling adoption needed at the substrate level.

---

## Where the substrate's actual gaps are vs. where tensor tools help

Cumulative findings from Substrate-Tester fires #1-#36:

| Finding | Tensor-tool fit |
|---|---|
| 5-of-5 capability-gap cluster (homotopy, designs, HOMFLY, A∞, group rep) | **Low.** These need typed equivalence-class primitives; tensor tools don't supply them. SageMath/Macaulay2 (Tier 4) could help with the algebraic-geometry side of group representations. |
| Architectural impedance (Lane 11, 4-seed-stable) | **Zero.** The gap is "no general-purpose CLAIM gauntlet"; tensor tools don't fix it. |
| Cross-(degree, coef-bound) hit-rate scaling | **Low.** This is enumeration arithmetic; numpy is sufficient. |
| INCONCLUSIVE list classification (Lane 7) | **Zero.** Symbolic verification (factor-then-nroots); no tensor work. |
| Substrate-wide @dataclass(frozen=True) discipline | **Zero.** Test-discipline issue; orthogonal. |
| Enum-field input-validation gaps | **Zero.** Type-discipline; orthogonal. |

**Substrate-tester's verdict 2026-05-08:** of the 36+ fires of Substrate-Tester evidence, **0 findings to date are bottlenecked by missing tensor tooling**. Every gap surfaced is either (a) symbolic-equivalence-class primitives missing, (b) test-discipline gaps, or (c) input-validation gaps. Tensor tools become useful AFTER:
1. The unified signature-keyed tensor (HARD-3) exists with real operator-output content;
2. Apollo / Rhea reach the trainable-substrate-component phase (currently deferred per `feedback_tensor_first`);
3. Cross-operator joint contraction enters the picture (no Substrate-Tester signal for this yet).

---

## Charter addition (Substrate-Tester)

Per James's directive 2026-05-08, future Substrate-Tester fires should:

1. **Note tensor-tool relevance on each substrate finding.** When filing a capability-gap or substrate-flaw ticket, include a brief "tensor-tool fit" assessment in the payload (e.g. "TensorLy decomposition could compress this once the unified tensor exists" OR "no tensor-tool fit; symbolic primitive missing").

2. **Watch for the unified-tensor materialization.** When the substrate's unified signature-keyed tensor lands with real content, file an Aporia coordination ticket triggering Tier-2 tensor-tool evaluation (TensorLy + TensorLy-Torch + JAX integration assessment).

3. **Watch for cross-operator joint structure.** If a substrate-tester finding ever surfaces an N-operator joint distribution that's exponential in N, flag for ITensor / cuTensorNet evaluation.

4. **Resist gravitational-well drift.** "Use [framework]" is not "build the substrate." Tensor tools are evaluated on substrate-grade fit (HARD-3 alignment + capability-gap closure), not on conventional-ML criteria.

---

## References

Per James's 2026-05-08 catalog message:
- TensorLy: https://tensorly.org
- TensorLy-Torch: https://tensorly.org/torch
- JAX: https://docs.jax.dev / https://github.com/jax-ml/jax
- PyTorch: https://pytorch.org
- ITensor: https://itensor.github.io
- NVIDIA cuTensor / cuTensorNet / TensorRT: https://developer.nvidia.com
- SageMath, Macaulay2, Singular: existing substrate intellectual-ecosystem dependencies

---

## Living document

Updates land via Substrate-Tester fires when:
- A capability-gap finding suggests a specific tensor-tool fit
- A new tool enters the ecosystem worth cataloguing
- An evaluated tool gets adopted (or rejected) by the substrate

— Substrate-Tester, M1 instance, 2026-05-08
