# Report 06 — State Representation for Symbolic Substrates

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Topic:** Graph encodings and embeddings for an RL agent acting over a typed symbolic substrate

---

## 1. Situation

Prometheus's substrate is not a flat feature vector; it is a **typed, append-only directed graph** that has accumulated over months of agent activity. Concretely it contains:

- **Symbol nodes** — promoted mathematical objects (zeros, gaps, isogeny classes, OEIS sequences, polytopes, knots), each carrying a content-addressed signature hash.
- **Claim nodes** — null-protocol verdicts (`survives`, `killed`, `conditional`), tagged with the battery tier that produced them and the seed pool used.
- **Tensor cells** — entries in the unified signature-keyed tensor (~86K objects × 145 dims × 11 strategy groups), each a node with sparse activation vectors.
- **Provenance edges** — `derives`, `falsifies`, `supports`, `refutes`, `replicates`, `coarse-grains`, `null-of`, plus operator-application edges from the Σ-kernel TRACE opcode.
- **Calibration anchors** — load-bearing reference nodes (Ramanujan tau, Riemann zeros, LMFDB curves) that ground new claims.
- **Open-question frontier** — Aporia's 322 catalogued aporias, each a node in `open` state with prereq edges.
- **Gate verdicts** — Pronoia / null-battery / battery-FROZEN-v10 outputs attached to each promotion event.

The agent must select an action (NEXT_TEST, COARSEN, BRIDGE, KILL, PROMOTE) over this graph. The state encoder has to preserve **type, locality, and provenance lineage** without serialising the whole substrate every step.

---

## 2. State-of-the-Art in Graph State Representation

**Theorem-proving / proof-state encoders.** HyperTree Proof Search (HTPS, Lample et al. 2022) treats the proof state as a hypergraph of subgoals and uses a Transformer encoder over tactic-state strings, with an AlphaZero-style policy+value head. The lesson is not the architecture per se but that *partial-proof structure was load-bearing* — flat sequence encoding underperformed once the search tree got deep. HOLStep (Kaliszyk et al. 2017) and the Holophrasm/GamePad lines used **graph neural networks over the AST of conjectures and premises**, with edge labels for `is-premise`, `appears-in`, `unifies-with`. AlphaProof (DeepMind 2024) uses a value+policy net that consumes a structured Lean proof state with formal-syntax token embeddings plus a tactic-applicability sub-graph; reported gains over flat-sequence baselines are large at depth >8.

**Program synthesis.** DreamCoder (Ellis et al. 2021) encodes the *library* of learned primitives as a typed lambda-calculus DAG and trains a recognition network that conditions on the task and produces a distribution over library-graph paths. AlphaCode encodes programs as token sequences but augments with a separate AST channel; ablations show the AST channel matters most for problems requiring novel composition.

**Knowledge-graph embeddings.** TransE (Bordes 2013), ComplEx (Trouillon 2016), and RotatE (Sun 2019) treat each edge as `h ⊕ r ≈ t` and learn dense embeddings under a translational/complex/rotational composition rule. These are cheap and good for **link-prediction queries** ("does this symbol couple to that gap?") but bad at preserving long provenance chains. The 2023–2024 trend is **heterogeneous graph transformers**: HGT (Hu et al. 2020) and successors HGNN-AC, SeHGNN (2023), and Simple-HGN++ (2024) parameterise attention per (source-type, edge-type, target-type) triple. Gilmer's message-passing neural network framework (Gilmer 2017) is still the canonical formalism — virtually all modern encoders are MPNN instances differing in the message, update, and readout functions. For sparse, typed graphs the current sweet spot is **R-GCN or HGT with sub-graph sampling (GraphSAINT / NeighborLoader)**.

---

## 3. Encoding Patterns for Prometheus's Substrate

Concrete recommendation, in priority order:

**(a) Typed heterogeneous graph in PyTorch Geometric.** Use `HeteroData` with node types `{claim, symbol, evidence, op_application, calibration_anchor, aporia}` and edge types `{derives, falsifies, supports, refutes, replicates, applies_op, null_of, prereq_of}`. This maps 1:1 to the substrate ontology, and PyG's `HGTConv` / `HeteroConv` layers natively respect typing without flattening. Node features are small per-type vectors (signature-hash embedding + type-specific scalars: claim has `verdict`, `tier`, `seed_pool_size`; symbol has its tensor-cell row; evidence has `provenance_depth`).

**(b) Sub-graph extraction policy.** Do **not** encode the full substrate per step. For each focal claim/aporia under consideration, extract a **k-hop relevance neighborhood** (k=2 or 3) using PyG's `NeighborLoader` with type-aware sampling — bias sampling toward `falsifies`, `null_of`, and `replicates` edges (these are the high-information edges per the kill-rate data) and downsample `supports` (cheap and abundant). Cap at ~512 nodes per observation; this fits comfortably on a single 17 GB card and respects the VRAM ceiling lesson.

**(c) Pretraining strategy.** Before any RL, run **contrastive pretraining** on the existing substrate: positive pairs are (claim, its provenance ancestors) and (claim, its replications); negatives are random sampled cross-tier pairs. Use a GraphCL-style augmentation (edge dropping + node-feature masking). The four documented false-discovery kills plus the killed NF-backbone, the AlignmentCoupling-seed-artifact, and the Quadratic-Mirage cases give natural **hard negatives** — train the encoder to put killed claims far from surviving ones. Freeze the encoder, fine-tune the policy head.

**(d) Sparse-aware encoders.** The substrate is sparse: median node degree is low single digits, with a long tail at calibration anchors and primes (the prime-atmosphere problem). Use `torch_sparse` SpMM kernels and avoid any dense adjacency materialisation. Consider GraphSAGE-style mean-aggregation as a baseline before HGT, since HGT's per-relation attention is expensive and may not pay off until the substrate exceeds ~10⁶ nodes.

---

## 4. Composition with the Σ-Kernel

The Σ-kernel already does most of the encoding work; the RL state encoder should ride on it rather than parallel it.

- **TRACE produces a provenance graph natively.** Each kernel TRACE record is `(input_hash, op, output_hash, witness)`. These records *are* `op_application` nodes and `derives` edges. The encoder ingests the TRACE log directly with no transformation.
- **Content-addressed hashes are natural node IDs.** The kernel's hash invariant (same content → same hash) means the encoder gets **automatic node de-duplication** and **referential transparency** across sessions. Two agents that independently derive the same symbol contribute to the same node.
- **Append-only invariant enables incremental encoding.** Because nothing is mutated, the encoder maintains a **persistent embedding table keyed by hash**. On each PROMOTE only the new sub-graph (typically <50 new nodes) is embedded; the rest of the table is frozen and reused. Large wall-clock win versus re-embedding the substrate every step.
- **Gate verdicts attach to op_application nodes.** Pronoia's kill/survive verdicts become node attributes, so the policy can learn to route around historically failure-prone operator chains without explicit feature engineering.
- **Calibration anchors get pinned embeddings.** Anchor nodes (Ramanujan, Riemann, LMFDB) get fixed, possibly-pretrained embeddings the encoder is forbidden to update — they are the substrate's coordinate frame.

---

## 5. Concrete `observation_space` Recommendation

Use a Gymnasium `Dict` space wrapping a PyG `HeteroData` mini-batch (PyG ships `pyg.data.lightning.LightningDataset` integration that already handles Gymnasium-compatible serialisation).

```python
from gymnasium import spaces
import numpy as np

observation_space = spaces.Dict({
    "node_features": spaces.Dict({
        "claim":              spaces.Box(-np.inf, np.inf, (512, 32),  np.float32),
        "symbol":             spaces.Box(-np.inf, np.inf, (512, 145), np.float32),
        "evidence":           spaces.Box(-np.inf, np.inf, (512, 16),  np.float32),
        "op_application":     spaces.Box(-np.inf, np.inf, (512, 24),  np.float32),
        "calibration_anchor": spaces.Box(-np.inf, np.inf, (32,  64),  np.float32),
        "aporia":             spaces.Box(-np.inf, np.inf, (256, 32),  np.float32),
    }),
    "edge_index": spaces.Dict({
        et: spaces.Box(0, 2**31 - 1, (2, 4096), np.int64)
        for et in ("derives", "falsifies", "supports", "refutes",
                   "replicates", "applies_op", "null_of", "prereq_of")
    }),
    "focal_node_id": spaces.Box(0, 2**31 - 1, (1,), np.int64),
    "node_hashes":   spaces.Box(0, 2**63 - 1, (2432,), np.int64),
})
```

The 512-per-type cap implements the relevance-radius policy from §3(b); `focal_node_id` tells the policy head which claim is under consideration; `node_hashes` lets the replay buffer recognise repeats and reuse cached embeddings.

---

## 6. References

1. Lample, G. et al. (2022). *HyperTree Proof Search for Neural Theorem Proving*. NeurIPS 2022.
2. Gilmer, J. et al. (2017). *Neural Message Passing for Quantum Chemistry*. ICML 2017.
3. Kaliszyk, C., Chollet, F., Szegedy, C. (2017). *HOLStep: A Machine Learning Dataset for Higher-Order Logic Theorem Proving*. ICLR 2017.
4. DeepMind (2024). *AI achieves silver-medal standard solving IMO problems* (AlphaProof technical note).
5. Ellis, K. et al. (2021). *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*. PLDI 2021.
6. Bordes, A. et al. (2013). *Translating Embeddings for Modeling Multi-relational Data* (TransE). NeurIPS 2013.
7. Trouillon, T. et al. (2016). *Complex Embeddings for Simple Link Prediction* (ComplEx). ICML 2016.
8. Sun, Z. et al. (2019). *RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space*. ICLR 2019.
9. Hu, Z. et al. (2020). *Heterogeneous Graph Transformer* (HGT). WWW 2020.
10. Yang, X. et al. (2023). *Simple and Efficient Heterogeneous Graph Neural Network* (SeHGNN). AAAI 2023.
11. Hamilton, W., Ying, R., Leskovec, J. (2017). *Inductive Representation Learning on Large Graphs* (GraphSAGE). NeurIPS 2017.
12. Zeng, H. et al. (2020). *GraphSAINT: Graph Sampling Based Inductive Learning Method*. ICLR 2020.
13. You, Y. et al. (2020). *Graph Contrastive Learning with Augmentations* (GraphCL). NeurIPS 2020.
14. Fey, M., Lenssen, J.E. (2019). *Fast Graph Representation Learning with PyTorch Geometric*. ICLR Workshop 2019.

Word count ≈ 1150
