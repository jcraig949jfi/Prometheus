# Prompt 02: Diversity and illumination

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaMW1kYW92M0k0UFRfdU1Qb09ueS1RcxIXWjFtZGFvdjNJNFBUX3VNUG9PbnktUXM
**Elapsed:** 273s

---

# Evolutionary Diversity and Illumination Benchmarking

This report outlines the experimental design translation for Quality-Diversity [cite: 1, 2], Novelty Search [cite: 3, 4], Illumination Algorithms [cite: 5], Coevolution [cite: 6, 7], and Minimal-Criterion Coevolution [cite: 8, 9]. Research suggests that the current bench architecture—restricted to single-scalar outcomes and devoid of multi-agent or archival state mechanisms—cannot natively express the core methodologies of these fields without structural expansion. The evidence leans toward the conclusion that entirely new execution kinds are required to faithfully benchmark these paradigms. The requested experimental specifications, along with the precise engineering blockers, are detailed below.

## Experimental Templates and Expansions

BEGIN_TEMPLATE
{
  "template_id": "map.elites.v0",
  "kind": "evaluate_qd_archive.v0",
  "param_space": {"evaluations": {"int_range": "1000 to 5000"},
                  "behavior_dimensions": {"choices": "2, 3, 4"}},
  "origin": {"source": "LITERATURE",
             "field": "Quality-Diversity (MAP-Elites)",
             "reference": "Mouret and Clune 2015 Illuminating search spaces by mapping elites",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "MAP-Elites categorizes solutions into a behavioral grid and retains the highest performing individual per cell. This template measures whether an archive-based search can illuminate the performance landscape across specified behavioral dimensions. The field runs this to understand trade-offs rather than just finding a single optimum. A SURVIVED verdict would indicate successful exploration by exceeding an archive size threshold, but would NOT license the claim that any single solution outperforms an objective-only search, nor would it guarantee that the chosen behavioral dimensions map to a globally continuous phenotype space."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Quality-Diversity (MAP-Elites)
LACKS: A persistent state object that maps multidimensional behavioral coordinates to the best scalar fitness achieved at those coordinates.
WHY: Quality-Diversity and Illumination Algorithms require storing a diverse set of elite solutions across behavioral niches. The current bench only evaluates a single state or carries a one-dimensional walk state, and its single-scalar outcome rule cannot map outcomes across a behavioral grid.
SMALLEST_FORM: An archive_size scalar emitted by a stateful executor that accepts a behavior_dimensions parameter and updates a persistent coordinate store across repeats.
BLOCKS: Quality-Diversity (MAP-Elites), Illumination Algorithms
EVIDENCE: Mouret and Clune 2015 Illuminating search spaces by mapping elites establishes that an archive mapping features to performance is the defining requirement of the method.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "novelty.search.v0",
  "kind": "novelty_search_step.v0",
  "param_space": {"evaluations": {"int_range": "1000 to 5000"},
                  "k_nearest": {"choices": "15, 20, 25"}},
  "origin": {"source": "LITERATURE",
             "field": "Novelty Search",
             "reference": "Lehman and Stanley 2008 Exploiting Open-Endedness to Solve Problems Through the Search for Novelty",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Novelty search abandons the objective function entirely, scoring individuals solely by their behavioral distance to an archive of previous individuals. This measures whether ignoring objectives circumvents deception. A SURVIVED verdict showing high terminal novelty would indicate the search reached unexplored areas, but would NOT license the claim that the algorithm actually solved a specific task, only that it diverged successfully."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Novelty Search
LACKS: A mechanism to compute and record the behavioral distance between the current evaluation and a historical list of prior evaluations.
WHY: Novelty Search abandons the objective function entirely, scoring on distance to past behaviors. The bench's available evaluate_bitstring scores against a static hidden target and carries no history, preventing the required distance calculation.
SMALLEST_FORM: A novelty_score scalar emitted by an executor that maintains a persistent list of past states and computes average distance to the k_nearest historical neighbors.
BLOCKS: Novelty Search
EVIDENCE: Lehman and Stanley 2008 Exploiting Open-Endedness to Solve Problems Through the Search for Novelty explicitly define the method entirely around measuring distance to previously visited behaviors in an archive.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "illumination.grid.v0",
  "kind": "illuminate_space.v0",
  "param_space": {"grid_resolution": {"choices": "10, 20, 50"},
                  "evaluations": {"int_range": "1000 to 10000"}},
  "origin": {"source": "LITERATURE",
             "field": "Illumination Algorithms",
             "reference": "Mouret and Clune 2015 Illuminating search spaces by mapping elites",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Illumination algorithms return a holistic map of high-performing solutions rather than a single optimum. This template tests the ability to fill a discretized behavioral grid of a given resolution. A SURVIVED verdict showing the number of filled bins exceeds a target indicates the landscape is successfully illuminated, but would NOT license the claim that the highest performing individual in the grid is the global optimum, as illumination distributes evaluation budget across niches."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "coevolution.parasites.v0",
  "kind": "coevaluate_populations.v0",
  "param_space": {"host_pop_size": {"choices": "50, 100, 200"},
                  "parasite_pop_size": {"choices": "50, 100, 200"}},
  "origin": {"source": "LITERATURE",
             "field": "Coevolution",
             "reference": "Hillis 1990 Co-evolving parasites improve simulated evolution as an optimization procedure",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Competitive coevolution pits a population of candidate solutions against a population of test cases, where fitness depends on defeating the opposing population. This measures whether an arms race prevents premature convergence on static benchmarks. A SURVIVED verdict showing host improvement over time would indicate a productive arms race, but would NOT license the claim that the final host is robust against all possible tests, only against the final surviving parasites."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Coevolution
LACKS: The ability to maintain two distinct, persisting populations and evaluate individuals from one against individuals from the other.
WHY: Both competitive coevolution and minimal-criterion coevolution depend on evaluating individuals against dynamic opponents rather than a static objective. The bench provides only a single world seed and static hidden target, making adversarial matrices impossible.
SMALLEST_FORM: A host_fitness scalar exposed by an executor that initializes two distinct population arrays from the seed_root and cross-evaluates them across sequential repeats.
BLOCKS: Coevolution, Minimal-Criterion Coevolution
EVIDENCE: Hillis 1990 Co-evolving parasites improve simulated evolution as an optimization procedure demonstrates that co-evaluation of a host population and a parasite test-case population is the foundation of the approach.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "mcc.bipartite.v0",
  "kind": "mcc_step.v0",
  "param_space": {"solvers": {"choices": "50, 100, 250"},
                  "environments": {"choices": "50, 100, 250"}},
  "origin": {"source": "LITERATURE",
             "field": "Minimal-Criterion Coevolution",
             "reference": "Brant and Stanley 2017 Minimal Criterion Coevolution: A New Approach to Open-Ended Search",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Minimal-Criterion Coevolution replaces absolute fitness with a strict survival threshold: a solver must solve at least one environment, and an environment must be solved by at least one solver. This tests whether open-ended divergence can be sustained without objective gradients. A SURVIVED verdict showing sustained population sizes over many repeats would indicate successful open-ended generation, but would NOT license the assumption that the solvers are increasing in general capability, only that they satisfy their specific coupled niches."
}
END_TEMPLATE

**Sources:**
1. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtyx43OLHBA9rMcodryiggho5tNHw8aFWtuXag9LG1Sd0sFgXDngsU1ZkqLVg3m6LL1s476t5K_2WadUP-XddBajJ4FpJFnjG6_L-MSsy1_8sDjlxFpr794j_veAAAPQ==)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4I-7iX4WvoF0VOixBMmigC9wrerMqTqAgcDpHBOcEJu9te3gpiFKS5-QLlkk3jmnF0xxoetNINLGBoLuAa2hxXxIzBlrPo6oAo2EklRGV-0Vry4VmQH58376HwYIj37f_OOMl9l6L-7_ZA4_vuVOm5DFogoH2bDoAYzpfsg414uj-XDRUKf9TE4yJ3gy5WT3MbwOT9DnPcPxem_3t9MKUVatJy2pVWWVFMHjZ_z-R6dnEyaX0YplRV1_S1nmN)
3. [gwern.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc_apeuDm2c64SIsgfvWrAFv2gzP8MIU4NBYyEPgUI-92ngFrPvwOj-kHTimrLvssU14oRqUPOuH9Qoy1OlRp4ubVUkoawemt7J3LR4W1YT0mmpNhGMiufhhNrYoEhy5GRFV0GsWEDNK4kOJeGXemuW602eW-SVjaKdLKwIg==)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq5JU0Xud3xUPZ_l2u4_l_pMXzirc8T7encMCOhxDedf3rVr89Kxtj-Kj0Hu07_sP_7LlMLbDvQL5WwIXLZ5n6C6GPfcxLS-ce8t6E61cvho4LZKfW6eQ7VuOzKp7xnfO29TwPW0JNEEcshEWd3R7wwBCW9pmWz-d6I1DV0ICdoaS0_r3Fpn9VqSpmInwErMRhVZx3edgLzKiaeFOhxjlEN7_SKtgx-vdD0RwbeV0pLUm9Rzo9YJMBr-7xhBvMkEpY7BsSDrwK)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg4rvRUBOUWg7wAkFl-TQjEB3K0-AqYtiz6hh9AzGFsRZDrfClWjEu8_fuHf6OSIidO-QSO4TaWG2vr_1M9moXS8bNI84xpr-mY6mZHKpV96MKE8zv)
6. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7c7OyAtEqtRfjqTdbxz90qlgswahFfCg6EUTBYVBL4rh8_Mp9CkmfvKl7ytHbWmp6fq_eT2J_AEjx-cJ0gHtcFLYzV8Z-O-BpR_63USBRrH4x30CSMJOwtvUFZbGkl1wNWOSpxV0=)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQjLT-o4bF39BxHhYGuwq62eVFsliFHvOHL_olutiDp8TkpjFe7Et78NBTF_j50FChnTkhcAhlBzVKLnAyeVzNcYkBT-N-cr_eMEd2JVLycMglsmgWsf7z11DW8Wh1ZnoowUmxFgY=)
8. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1fm1gj5S3qbFXK8X17IHBCgbb8m2-Rmc-LwwLdXlcC9ExBp1Pxap-iLHiVBcSldKG9yS-iZW6aryaU8lvDIjsiEOkgcdM3g2gSlfv2vIHBnhK9biSIGJOkZYGUjYpL1qCuHSVDmbe74kUDfuQW0mbp-Kv2L0BNyPPEFjOyu-s4zEAH-AloM3Gymsh_2pMRnI96uRKlQGLgyBcdvNeYjI1Sbim_6CKhisCZealiBRmvpx2iDNJzRPeYFEwOTSEEiBhoJ9WHg==)
9. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3v0gB8rquFaEdl7oFtfzsYvUX2hhUzCu5N5IYpo8jpImitR0GsxHijejXcEdLdiAhDQ-IbbwcGVw9HLkqPF2qy32ls5gdq1Sb__TjeRxcEqUVETgnBGIW5o-OwfDxpPw9djyiYLSGJPRPr1YI8RFXpkQLkHHNSWs_Ihhs68x_pt1ChWHV-9G4n3RVblWWsLHP9_UyNg==)

