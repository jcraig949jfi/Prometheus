# Primitives Atlas cannot yet represent (Ananke 72h push)

Atlas's PRIMITIVES.jsonl (20 rows at export) is organised around heredity, replication and organism representation. The
72h push measured seven quantities that Atlas cannot record. Their rows are in PRIMITIVES.jsonl here.

| primitive | why Atlas lacks it | Ananke operationalisation |
|---|---|---|
| search_reachability | Atlas records whether a phenomenon occurred, not whether a search could reach a permitted, representable competence after physics, ruler and selection causes are excluded. | P/R/V admission, BASE rate, budget scaling (C2A-C2C, C3R, C4, C5T) |
| mirror_pair_counterfactual_carrier | No causal-carrier primitive: Atlas cannot say which state component causally carries a bit. | swap_v2 (FLIP/PARTIAL/NO_EFFECT/EMPTY_SWAP) |
| lineage_reconstruction | Heredity primitives track parent-child copying, not whether a function was rebuilt within a planted lineage or arose in the background. | line provenance tags, share >= .5 |
| module_reuse | No composition family: insertion of solved machinery with provenance, integrity and causal ablation. | OPDL, MODULE_PRESENT/LIVE/CAUSAL/INTEGRITY |
| graded_partial_function_retention | Atlas cannot separate "lineage kept" from "function kept". | C3S classes A/B/C/D |
| channel_state | Atlas cannot place information in the communication medium rather than in an organism. | Msum swap, zero_comm |
| module_binding (proposed) | It does not exist in PTE either. It is the primitive the C4 results point to. | to be designed: typed ports or a wiring field |

**Suggested Atlas schema change:** add a `composition` family (module_reuse, module_binding) and a `causal_assay` family
(mirror_pair_counterfactual_carrier, channel_state). Without those families, Ananke's composition results can only be
filed as "not observed", which loses the distinction between "not reachable" and "not representable".
