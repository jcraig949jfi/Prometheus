# Report T#84 — Optimal Tensor Network Contraction Order

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §X #84
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-8)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND
**Tags:** P30 (Tensor Network Contraction — paradigm exemplar), P22 (auxiliary), P09 (superseded), P28 (adjacency)

---

## Brief summary

T#84 (optimal tensor network contraction order) is the canonical P30 paradigm exemplar and **THE foundational primitive for HARD-3's unified-tensor build**. Verified arc: Markov–Shi 2008 (SIAM J. Comput. 38, 963–981; arXiv:quant-ph/0511069) established NP-hardness via the equivalence "optimal contraction-tree-width(N) = treewidth(line-graph(N))". State-of-practice: Pfeifer–Haegeman–Verstraete 2014 (`netcon`, optimal up to ~30 tensors); Smith–Gray 2018 (`opt_einsum`); Gray–Kourtis 2021 `cotengra` (~10⁴× speedup on Sycamore-class via hypergraph partitioning + CMA-ES hyper-optimization); Meirom et al. RL-TNCO 2022 ICML (Staudt et al. SEA 2024 documents RL underperformance >100 tensors); Liu et al. PRL 131 180601 (2023) subexponential upper bound under entanglement restrictions. T#84 directly anchors `T-2026-05-08-ST-fire39-001` (TensorNetworkGraph + ContractionOrderWitness + RewriteSearchTree gap) — every Tier-A++ TensorNetwork meta-primitive consumes/produces T#84-shaped objects.

## Flagged findings

1. **Two distinct optima — PATTERN_CONDUCTOR_CONFOUND.** "Optimal contraction order" silently means at least two different things: minimum FLOP-count vs minimum peak memory. Different optimization objectives with potentially disjoint optima. `netcon` defaults to FLOPs; cotengra exposes both via cost-modifier hyperparameters. Substrate-grade encoding MUST carry both as separate fields.

2. **Memory cost is the dominant practical constraint — PATTERN_VRAM_TRUNCATION_ARTIFACT.** Textbook FLOP analyses miss that for quantum-circuit and PEPS-class networks, peak intermediate tensor *exceeds available VRAM* long before FLOP budgets are exhausted. cotengra's "slicing" technique is explicit FLOP-for-memory trade. The 17GB-card ceiling is the same architectural reality at substrate scale.

3. **NP-hardness is via treewidth — clean reduction.** Markov–Shi 2008 Theorem: optimal contraction tree-width = treewidth of the *line graph* of the network. Treewidth-d networks contract in T·exp(O(d)) time. Substrate's optimal-contraction-witness primitive is structurally a **tree decomposition of the line graph** with annotated bond dimensions, not a flat permutation.

4. **Heuristic optimality-gap on uniform-random TNs is unmeasured — PATTERN_BASE_RATE_NEGLECT.** Most TN-contraction papers report best-of-K-heuristics on cherry-picked benchmarks; base rate of optimality gap on uniformly random networks is poorly characterized. Substrate-tester opportunity: generate uniform-random TN ensembles, compare cotengra/RL/exhaustive on triple-axis (FLOPs, memory, wall-time).

5. **RL methods underperform classical at scale.** Meirom 2022 RL-TNCO leads at ~50 tensors; Staudt et al. 2024 (SEA 2024) documents RL underperformance at 100+ tensors against hypergraph-partitioning. Substrate-grade response distinguishes regime-of-applicability.

6. **Subexponential structural upper bound (Liu et al. 2023, PRL 131 180601).** For tensor networks corresponding to quantum circuits with restricted entanglement structure, contraction admits subexponential algorithms. Closes a corner; full general-case unconditional subexponential remains open.

7. **Tree-tensor-network special case is polynomial.** SIAM J. Sci. Comput. 23M161286X (Christoffel et al. 2024) — linear contraction order for tree TNs polynomial via reduction to database join ordering. P30 + database-query-optimization cross-pollination.

8. **Substrate gap (foundational):** No current substrate primitive encodes the (V, E, d_e, contraction-tree, FLOP-cost, memory-cost) bundle as a first-class object. `T-ST-fire39-001` flags the gap. Per HARD-3 this is **THE** substrate primitive — every higher-tensor primitive eventually produces or consumes a TensorNetwork instance.

9. **New P30 sub-tactics flagged for taxonomy update:**
   - **HyperOpt-over-heuristic** — meta-search (CMA-ES / Bayesian / RL) over heuristic *families* and their hyperparameters
   - **Memory-FLOP-Pareto navigation** — explicit slicing trade-off characterization rather than single-objective optimization
   - **Treewidth-as-line-graph-invariant** — only known *clean* hardness reduction; substrate's TensorNetworkGraph primitive should expose treewidth(line-graph) as a derived invariant

10. **Recommend filing `T-ST-T84-001 TensorNetwork + ContractionOrderWitness primitive specification`** for next contract-change window with this report as design-spec input.

## Verified arXiv IDs / DOIs

`quant-ph/0511069` (Markov–Shi, SIAM J. Comput. 38, 963–981, 2008); `1304.6112` (Pfeifer–Haegeman–Verstraete, PRE 90, 033315, 2014); `2002.01935` (Gray–Kourtis, Quantum 5, 410, 2021); JOSS 10.21105/joss.00753 (Smith–Gray opt_einsum, 2018); `2204.09052` (Meirom-Maron-Medini-Chechik, ICML 2022); LIPIcs.SEA.2024.27 (Staudt et al., 2024); `1807.04599` (Dumitrescu, treewidth benchmarking, 2018); `2001.08063` (Schindler–Jermyn, 2020); s43588-021-00119-7 (Huang et al., Nature Comp. Sci. 2021); `2507.20667` (simulated annealing TN partitioning, 2025); PRL 131 180601 (Liu et al. 2023); SIAM J. Sci. Comput. 23M161286X (tree TN, 2024).

---

## 1. Problem Statement

A **tensor network** N = (V, E, d) consists of: vertex set V (tensors); multi-hyperedge set E ⊆ 2^V (each edge labels a contracted index); bond-dimension d : E → ℤ_{≥1}.

A **contraction sequence** is a binary tree T with leaves V; each internal node represents the pairwise contraction of its children's results. Costs:
- **FLOP cost:** C_flop(T) = Σ_{internal v} (size of intermediate produced at v).
- **Memory cost:** C_mem(T) = max_{internal v} (entry count of intermediate at v).

**T#84:** given (V, E, d), find T* minimizing C_flop (and/or C_mem). NP-hard in general; approximation algorithms with sharp worst-case guarantees remain open.

**Equivalent formulations:** treewidth equivalence (Markov–Shi); carving-width / branch-decomposition for memory variant; database-join-order reformulation for tree TNs; hypergraph cut sequence for hyperedge networks (cotengra).

| Variant | Hardness | Best practical solver | Optimal up to |
|---|---|---|---|
| FLOP-min, general | NP-hard | cotengra | ~30 tensors (`netcon`) |
| Memory-min, general | NP-hard | cotengra w/ slicing | ~30 tensors |
| Tree TN linear order | P (poly-time) | join-order DP | unbounded |
| Bounded treewidth d | exp(O(d)) | tree-decomposition + DP | unbounded |
| Random circuit (Sycamore-class) | NP-hard | cotengra + slicing | ~10⁴× speedup over naive |

## 2. Status & Bounds

| Result | Authors | Year |
|---|---|---|
| NP-hardness of optimal FLOP-min order | Markov–Shi (SIAM J. Comput. 38 963) | 2008 |
| Treewidth(line-graph) = optimal contraction-tree-width | Markov–Shi | 2008 |
| Exhaustive optimal solver via pruning (~30 tensor ceiling) | Pfeifer–Haegeman–Verstraete (`netcon`) | 2014 |
| DP + greedy heuristic library | Smith–Gray (`opt_einsum`, JOSS 3 753) | 2018 |
| Hyper-optimized hypergraph partitioning + CMA-ES driver | Gray–Kourtis (`cotengra`, Quantum 5 410) | 2021 |
| Sycamore-circuit ~10⁴× speedup vs prior expectation | Gray–Kourtis | 2021 |
| Parallel KaHyPar + CMA-ES at HPC scale | Huang et al. (Nat. Comp. Sci.) | 2021 |
| RL-GNN approach (small-scale leader) | Meirom et al. (ICML; RL-TNCO) | 2022 |
| RL-vs-classical regime crossover at ~100 tensors | Staudt et al. (SEA 2024.27) | 2024 |
| Subexponential upper bound under entanglement-restriction | Liu et al. (PRL 131 180601) | 2023 |
| Tree-TN linear contraction in P (DB-join reduction) | Christoffel et al. (SIAM JSC) | 2024 |
| Simulated-annealing partitioning at HPC scale | arXiv:2507.20667 | 2025 |

**Open frontier:** Sharp APX-hardness vs PTAS classification; Memory-FLOP Pareto frontier characterization; Provable speedup of RL/learning at large scale; Distributed / MPI-aware contraction-order optimization; Tensor-decision-diagram (TDD) integration.

## 3. Literature

**Foundational:** Markov–Shi 2008 (NP-hardness; treewidth equivalence). Aji–McEliece 2000 (early tree-decomposition / generalized distributive law). Arnborg–Corneil–Proskurowski 1987 (treewidth NP-hardness, the upstream reduction).

**Exhaustive / branch-and-bound:** Pfeifer–Haegeman–Verstraete PRE 90, 033315 (2014, `netcon`).

**Greedy / DP heuristic libraries:** Smith–Gray JOSS 3, 753 (2018, `opt_einsum`).

**Hyper-optimized + hypergraph partitioning:** Gray–Kourtis Quantum 5, 410 (2021, `cotengra`); Huang et al. Nat. Comp. Sci. 2021 (parallel TN contraction with index slicing); Schindler–Jermyn 2020; Dumitrescu et al. 2018.

**RL approaches:** Meirom-Maron-Medini-Chechik ICML 2022 (RL-TNCO); Staudt et al. SEA 2024 (cut-strategy refinement).

**Theoretical upper bounds:** Liu–Pan–Zhang–Wang–Yang PRL 131, 180601 (2023, subexponential); Christoffel et al. SIAM JSC 23M161286X (2024, tree-TN P-time).

**Tools:** `netcon` (Matlab), `opt_einsum` (Python), `cotengra` (Python), `TensorNetwork` (Google), ITensor (Julia/C++), TenPy (Python), TensorAlgebra.jl, ITensors.jl, cuQuantum / cuTensorNet (NVIDIA), KaHyPar (Schlag et al.), TT-Toolbox, T3F.

## 4. Attack Vectors

T#84 is the canonical **P30 (Tensor Network Contraction)** paradigm exemplar.

**P30 — active sub-tactics:**
- Treewidth-based contraction (Markov–Shi 2008; Dumitrescu 2018)
- Hypergraph partitioning (cotengra; Huang et al.)
- Index slicing (cotengra) — Memory-FLOP Pareto navigation
- Branch-and-bound with pruning (Pfeifer `netcon`)
- Dynamic programming on subset lattices (opt_einsum "optimal" / "dp")
- Genetic / simulated annealing (Sayed et al. 2025)
- RL on contraction-step MDP (Meirom 2022)
- Variational / Bayesian hyper-search over heuristics (Gray–Kourtis 2021)
- Tree-TN linear contraction via join-order DP (Christoffel 2024)
- Tensor-decision-diagrams (Springer J. Supercomp. 2024)

**P22 (auxiliary):** Treewidth lower bounds via Cauchy-interlacing-style spectral arguments on line-graph structure.

**P09 (superseded):** `netcon` and opt_einsum "optimal" are P09-shape but explicitly fail at large scale. Their ROLE is as ground-truth oracles for benchmarking heuristics.

**P28 (adjacency):** Asymptotic-rank-of-contraction question is a P28-shaped reformulation of T#84's approximation-algorithm question.

**Sub-tactics flagged for taxonomy update (P30 internal):**
1. **HyperOpt-over-heuristic** — outer meta-search over heuristic families. Recurs in compiler scheduling, NAS, query optimization.
2. **Memory-FLOP-Pareto navigation** — explicit slicing trade-off characterization.
3. **Treewidth-as-line-graph-invariant** — substrate's TensorNetworkGraph primitive should expose treewidth(line-graph) as a derived invariant.

## 5. Substrate Encoding

T#84 directly anchors the **Tier-A++ TensorNetwork meta-primitive** (per HARD-3 closed-loop-condition #1). It is THE foundational substrate primitive — every other tensor primitive eventually consumes or produces TensorNetwork instances.

```python
class ContractionCostKind(str, Enum):
    FLOP_MIN = "flop_minimizing"
    MEMORY_MIN = "peak_memory_minimizing"
    PARETO = "pareto_frontier"
    UNKNOWN = "unknown"

class ContractionTreewidthClass(str, Enum):
    TREE_TN = "tree_tn"
    BOUNDED_TW = "bounded_treewidth"
    GENERAL = "general_np_hard"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class TensorNetwork:
    network_id: "NetworkID"
    node_set: tuple["TensorNodeID", ...]
    edge_set: tuple["LabeledHyperedge", ...]
    # LabeledHyperedge: (incident_nodes, bond_dimension, index_label)
    treewidth_line_graph: Optional[int] = None
    treewidth_class: ContractionTreewidthClass = ContractionTreewidthClass.UNKNOWN
    domain_docstring: dict = field(default_factory=dict)

@dataclass(frozen=True)
class ContractionOrderWitness:
    network: "TensorNetwork"
    contraction_tree: "BinaryTreeOnNodeSet"
    cost_kind: ContractionCostKind
    flop_cost: int
    memory_cost: int
    slicing_indices: tuple[str, ...] = ()
    discovery_method: "MethodSpec"  # netcon | opt_einsum | cotengra | RL-TNCO | hand
    optimality_status: "OptimalityStatus" = OptimalityStatus.HEURISTIC
    optimality_certificate: Optional["ExclusionCertificate"] = None
```

**How this answers `T-2026-05-08-ST-fire39-001`:** the three missing primitives flagged by Substrate-Tester fire #39 (TensorNetworkGraph, ContractionOrderWitness, RewriteSearchTree) are jointly addressed by the (TensorNetwork, ContractionOrderWitness) pair. RewriteSearchTree is the *implementation detail* of how a ContractionOrderWitness is *discovered*; substrate's MethodSpec already covers that layer.

**Asymmetric-existential resolution (Tier-B convergence with fires #38/#40/#41):** ContractionOrderWitness is a positive existential ("contraction tree T achieves cost ≤ B") with an associated ExclusionCertificate ("no T achieves cost < B"). Together they form the Tier-B ConstructiveExistenceWitness shape. RankDecompositionWitness + ContractionOrderWitness + IsomorphismCertificate + LimitWitness all share this asymmetric-existential pattern.

**Why this primitive is THE foundational tensor object (HARD-3):**
1. Every Section-X catalog entry (#75–83) consumes a tensor network as input.
2. The unified-tensor build requires a "signature-keyed tensor" — TensorNetwork with treewidth + cost annotations IS a signature.
3. Cotengra/opt_einsum/cuTensorNet integration: substrate primitive directly maps to library inputs, no wrapper layer.
4. Operator-derived structural partitions (HARD-3, HARD-5): treewidth(line-graph), bond-dimension distribution, hypergraph-cut-weight statistics are operator-derived structural fields.
5. Cross-tier composition: TensorPCA threshold (T#73, fire #43) and random-tensor ensembles compose cleanly when TensorNetwork carries `bond_dimension_distribution` as a Tier-D ProbabilityMeasure on edges.

**Migration path for next contract-change window:**
1. Ship `TensorNetwork` + `ContractionOrderWitness` as Tier-A++ primitives.
2. Wire to cotengra / opt_einsum as backend MethodSpecs.
3. Expose `treewidth_line_graph` as derived field via networkx / kahypar.
4. Add `slicing_indices` + memory-cost as first-class to defeat PATTERN_VRAM_TRUNCATION_ARTIFACT.
5. Add lower-bound-only ExclusionCertificate route for proofs-of-optimality.

## 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "T#84 is NP-hard via Markov–Shi 2008 reduction to minimum-treewidth of the line graph; netcon is exhaustive optimal up to ~30 tensors; cotengra is the production-grade hypergraph-partitioning + hyper-optimization heuristic family; RL-TNCO leads at ≤50 tensors but is overtaken by cotengra at 100+ tensors per Staudt et al. SEA 2024."
- *Substrate-grade:* "Two cost objectives — FLOP-min and memory-min — generally have *different* optima; cotengra exposes both via slicing."
- *Textbook-trivial:* "Optimal contraction order is NP-hard." (Bare statement without treewidth reduction or library landscape is anecdote not anchor.)
- *Trap (PATTERN_BASE_RATE_NEGLECT):* "Method X achieves Y× speedup over baseline" without specifying baseline, network ensemble, and cost axis.
- *Trap (PATTERN_VRAM_TRUNCATION_ARTIFACT):* reporting only FLOP cost when memory is the binding constraint.
- *Trap (PATTERN_CONDUCTOR_CONFOUND):* conflating "optimal" across cost axes; conflating contraction *order* with contraction *tree*; conflating treewidth of network graph with treewidth of line graph.

**Canonical authors at varying canonicality:**
- **Markov, Shi** — NP-hardness + treewidth reduction founders.
- **Pfeifer, Haegeman, Verstraete** — `netcon` line.
- **Gray, Kourtis** — cotengra; most-cited recent.
- **Smith, Gray** — opt_einsum.
- **Meirom, Maron, Medini, Chechik** — NVIDIA RL-TNCO line.
- **Liu, Pan, Zhang** — subexponential bound.
- **Schlag** (KaHyPar) — graph-partitioning canonical.

**Fabrication risks:**
1. Mis-stating Markov–Shi (correct: 2008 SIAM J. Comput. 38 963; arXiv quant-ph/0511069).
2. Inventing constant-factor approximation algorithm with sharp guarantees.
3. Conflating treewidth-of-network with treewidth-of-line-graph.
4. Inventing speedup factors for RL-TNCO at scales beyond ~50 tensors.
5. Treating "memory cost = FLOP cost." False.
6. Per HARD-5: T#84 NOT exclusively quantum-simulation. Same shape arises in factor graphs, DB join orders, PGM, weighted-model-counting, TT numerical linear algebra.

## 7. Cross-References

**Within `tensor_open_problems_v1.md`:**
- **#75 Area law** — area-law states admit efficient TN representation; T#84 is the cost question.
- **#76 PEPS contraction** — #P-hard; routes through T#84-style optimization with bond-dim truncation.
- **#77 TN expressibility** — dual question.
- **#82 TN manifold geometry** — variational TN optimization presupposes contraction.
- **#83 TN with signs** — sign-problem networks complicate cost optimization.
- **#49 TT-rank determination** — sister problem.
- **#50 Tucker compression** — same accuracy/storage tradeoff family.
- Adjacent: #51, #4, #58.

**Within `attack_angle_taxonomy.md`:**
- **P30** — paradigm-defining problem. **Recommend adding sub-tactics:** HyperOpt-over-heuristic; Memory-FLOP-Pareto navigation; Treewidth-as-line-graph-invariant.
- P22, P09, P28.

**Within `aporia/docs/deep_research_batch_tensor_priority_2026-05-09/`:**
- `report_T1_matrix_multiplication_exponent.md` — ω is asymptotic contraction cost of M_n network family.
- `report_T28_asymptotic_spectrum.md` — asymptotic spectrum subsumes both ω and contraction-cost asymptotics.
- `report_T79_slocc_entanglement.md` — SLOCC orbits live on TN-represented states.
- `report_T56_symmetric_rank_nphard.md` — sister NP-hardness.
- `report_T43_best_rank_r_existence.md` — orbit-closure non-closure couples to TN ill-conditioning.
- `report_T34_borderrank_membership.md` — sister Tier-B.

**Capability-gap tickets:**
- **`T-2026-05-08-ST-fire39-001`** — direct anchor. Resolution shape supplied in §5.
- `T-2026-05-08-ST-fire38-001`, `T-ST-fire40-001`, `T-ST-fire41-001` — sibling fires.
- `T-2026-05-08-T038` — Techne classification: T#84 is **TIER A++ FOUNDATIONAL / SUBSTRATE-CRITICAL**; resolution unblocks all of §X (entries 75–84) and most of HARD-3 unified-tensor build infrastructure.
- **New candidate ticket `T-ST-T84-001 TensorNetwork + ContractionOrderWitness primitive specification`** — recommend filing for next contract-change window.

---

*Aporia, 2026-05-09*
