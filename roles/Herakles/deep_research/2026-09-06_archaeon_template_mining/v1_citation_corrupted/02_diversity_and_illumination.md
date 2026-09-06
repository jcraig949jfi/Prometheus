# Prompt 02: Diversity and illumination

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctVS1kYXNMdEw3eUYtOFlQMXFTTThBTRIXLVUtZGFzTHRMN3lGLThZUDFxU004QU0
**Elapsed:** 365s

---

# Computational Research Bench Experiment Templates: Diversity, Illumination, and Coevolution

**Leading Paragraph:** 
This report synthesizes experimental templates and infrastructural expansion requests for implementing diversity-driven and coevolutionary algorithms on the current computational research bench. 
*   **Quality-Diversity and Illumination Algorithms** fundamentally seek to map the performance of solutions across a low-dimensional feature space, generating an archive of high-performing, phenotypically diverse elites rather than a single global optimum [cite: 1]. Implementing these on the bench is blocked because they inherently require evaluating a candidate's features against a persistent historical archive [cite: 2], a statefulness the bench currently restricts solely to deterministic random walks. 
*   **Novelty Search** drives open-ended search by entirely abandoning traditional objective gradients, instead rewarding behavioral novelty calculated via distance to previously encountered behaviors in an archive [cite: 3]. This similarly demands inter-evaluation state persistence [cite: 4, 5]. 
*   **Coevolution** relies on an evolutionary "arms race" (e.g., host-parasite dynamics) to continuously adapt the fitness landscape, preventing stagnation at local optima [cite: 6, 7]. 
*   **Minimal-Criterion Coevolution (MCC)** demonstrates that bounded open-endedness can be achieved without objective gradients by enforcing a simple survival constraint (e.g., an agent solving at least one maze) between two interacting populations [cite: 8, 9]. Both coevolutionary paradigms are blocked by the bench's reliance on evaluating a single static payload against a seed-derived hidden target [cite: 10, 11], lacking the bipartite evaluation necessary for dynamic entities to compete. 

Because the field's smallest honest experiments fundamentally require archives and pairwise interactions, they cannot be expressed by the stateless `noop_v0`, the statically evaluated `evaluate_bitstring`, or the deterministic `random_walk_v0`. Thus, all templates below declare new executor kinds, serving simultaneously as precise expansion requests to unblock these research disciplines.

## Quality-Diversity (MAP-Elites)

BEGIN_TEMPLATE
{
  "template_id": "qd.map_elites.v0",
  "kind": "evaluate_qd_archive.v0",
  "param_space": {"evaluations": {"int_range": },
                  "dimensions": {"int_range": [cite: 12, 13]},
                  "bins_per_dim": {"int_range": [cite: 14]},
                  "fitness_target": {"int_range": [cite: 6]}},
  "origin": {"source": "LITERATURE",
             "field": "Quality-Diversity (MAP-Elites)",
             "reference": "Mouret and Clune (2015) Illuminating search spaces by mapping elites [cite: 1]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a multi-dimensional archive of phenotypic elites can successfully illuminate a search space by discovering high-performing solutions across defined behavioral bins [cite: 1, 2]. The field runs this to understand performance trade-offs across phenotypic dimensions rather than simply finding one global optimum [cite: 15, 16]. A SURVIVED verdict (e.g., the archive reaching a specific coverage percentage of bins) would license the claim that the algorithm successfully maps phenotypic diversity; it would NOT license the claim that MAP-Elites evaluates individual genomes faster than a pure objective search, nor would it guarantee the true global peak of the landscape was found."
}
END_TEMPLATE

## Novelty Search

BEGIN_TEMPLATE
{
  "template_id": "novelty.search.v0",
  "kind": "evaluate_novelty.v0",
  "param_space": {"evaluations": {"int_range": },
                  "k_nearest": {"int_range": [cite: 17, 18]},
                  "novelty_threshold": {"int_range": [cite: 6]}},
  "origin": {"source": "LITERATURE",
             "field": "Novelty Search",
             "reference": "Lehman and Stanley (2011) Abandoning Objectives: Evolution through the Search for Novelty Alone [cite: 3]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether completely abandoning the objective function and searching solely for behavioral novelty can circumvent deceptive local optima in a search space [cite: 4, 5]. The field runs this to demonstrate open-ended search capabilities in environments where traditional objective gradients actively misdirect search [cite: 18, 19]. A SURVIVED verdict (e.g., discovering the hidden target strictly by maximizing distance to past behaviors) would license the claim that the underlying landscape is deceptive and traversable via behavioral divergence; it would NOT license the claim that novelty search is universally superior, as it typically underperforms on straightforward, non-deceptive convex optimization tasks."
}
END_TEMPLATE

## Illumination Algorithms

BEGIN_TEMPLATE
{
  "template_id": "illumination.coverage.v0",
  "kind": "evaluate_illumination.v0",
  "param_space": {"eval_budget": {"int_range": },
                  "feature_resolution": {"int_range": [cite: 14]}},
  "origin": {"source": "LITERATURE",
             "field": "Illumination Algorithms",
             "reference": "Mouret and Clune (2015) Illuminating search spaces by mapping elites [cite: 1, 16]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This explicitly maps the fitness potential of an entire feature space to return a set of high-performing, diverse solutions [cite: 1, 2]. The field runs this to generate a holistic view of the search space's capacity, evaluating how interesting attributes combine to affect performance positively or negatively [cite: 16, 20]. A SURVIVED verdict licenses the claim that the algorithm can maintain diverse, high-performing niches simultaneously; it does NOT license the conclusion that the manually chosen feature dimensions are the most optimal or relevant phenotypic descriptors for the underlying problem space."
}
END_TEMPLATE

## Coevolution

BEGIN_TEMPLATE
{
  "template_id": "coevolution.host_parasite.v0",
  "kind": "evaluate_coevolution.v0",
  "param_space": {"host_pop_size": {"int_range": [cite: 14]},
                  "parasite_pop_size": {"int_range": [cite: 14]},
                  "generations": {"int_range": [cite: 14]}},
  "origin": {"source": "LITERATURE",
             "field": "Coevolution",
             "reference": "Hillis (1990) Co-evolving parasites improve simulated evolution as an optimization procedure [cite: 6, 7]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether simulated evolution improves as an optimization procedure when opposed by co-evolving parasites (e.g., host sorting networks evaluated against a dynamic, co-evolving pool of parasite test cases) [cite: 10, 12]. The field runs this to prevent evolutionary search from settling for mediocre solutions that only beat weak, static opponents [cite: 21, 22]. A SURVIVED verdict licenses the claim that co-evolutionary pressure successfully prevents the host population from stagnating at a static local optimum; it does NOT license the claim that the co-evolutionary dynamic is perpetually stable, as the verdict alone cannot rule out the occurrence of cyclic 'Red Queen' dynamics where populations change without making true progressive improvements."
}
END_TEMPLATE

## Minimal-Criterion Coevolution

BEGIN_TEMPLATE
{
  "template_id": "mcc.maze_nav.v0",
  "kind": "evaluate_mcc.v0",
  "param_space": {"agent_pop": {"int_range": },
                  "maze_pop": {"int_range": },
                  "generations": {"int_range": [cite: 14]}},
  "origin": {"source": "LITERATURE",
             "field": "Minimal-Criterion Coevolution",
             "reference": "Brant and Stanley (2017) Minimal criterion coevolution: a new approach to open-ended search [cite: 8, 9]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether two interacting populations can achieve open-ended complexity strictly by satisfying a minimal survival criterion (e.g., mazes must be solved by at least one agent, agents must solve at least one maze) without explicit competitive fitness gradients [cite: 11, 23]. The field runs this to model natural, unbounded open-endedness where reproduction relies solely on viability rather than optimality [cite: 24, 25]. A SURVIVED verdict licenses the claim that simple minimal criteria alone are sufficient to drive phenotypic divergence and structural complexity; it would NOT license the claim that the resulting maze solvers are globally optimized or efficient for any specific, explicitly targeted downstream task."
}
END_TEMPLATE

## Expansions Required for Field Capability

BEGIN_EXPANSION
FIELD: Quality-Diversity (MAP-Elites)
LACKS: A persistent state object that retains user-defined behavioral descriptors of evaluated payloads across sequentially executed repeats.
WHY: Quality-Diversity, Novelty Search, and Illumination algorithms fundamentally rely on computing a new candidate's uniqueness relative to a continually updated historical archive of previously evaluated behaviors [cite: 1, 2, 3]. Because the bench currently restricts state persistence solely to the deterministic `random_walk_v0` executor and destroys all evaluation state between independent spec runs, there is no structural workaround to maintain a historical archive to calculate diversity or novelty scores [cite: 1, 4].
SMALLEST_FORM: A `persist_archive` state discipline for repeat blocks that stores a bounded list of arbitrary payload outputs from previous repeats and injects them as an `archive_history` array parameter into the subsequent repeat's payload execution.
BLOCKS: Quality-Diversity (MAP-Elites), Novelty Search, Illumination Algorithms
EVIDENCE: Mouret and Clune's MAP-Elites [cite: 1] and Lehman and Stanley's Novelty Search [cite: 3], both of which mathematically require calculating fitness/novelty explicitly against a historical, maintained archive of prior evaluations.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Coevolution
LACKS: The ability to execute a bipartite pairwise evaluation that scores two distinct genome payloads against one another.
WHY: Coevolution and Minimal-Criterion Coevolution fundamentally rely on an "arms race" dynamic where the fitness of one candidate (e.g., a host or solver) is strictly determined by its performance against a concurrent, dynamic adversary (e.g., a parasite or maze) [cite: 7, 9]. The current bench derives its evaluation target purely from hashing `seed_root` with the genome length, meaning the environment is perfectly static per seed and mathematically cannot represent an adaptive, co-evolving opponent [cite: 10, 11].
SMALLEST_FORM: A new executor `evaluate_pairwise.v0` that takes two distinct bitstrings (`bits_a`, `bits_b`) and their lengths as its payload, evaluating their relative interaction and outputting a single scalar `win_margin` field compatible with the existing outcome rule.
BLOCKS: Coevolution, Minimal-Criterion Coevolution
EVIDENCE: Hillis (1990) sorting networks co-evolved against parasite test cases [cite: 6, 7] and Brant & Stanley (2017) maze solvers co-evolved against dynamic, generated mazes [cite: 8, 9].
END_EXPANSION

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQdkHSZi11Vu8dzS_B8976BaHwYUD94niLxxxipT8sjW3maTLCHdRhjCa06KobVsIMwN-_hn6iWQlPEQwtAignNM-ky-Hc_HmCMuy7A1bHBR9lYpLUw==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxgMdKFagsLfiXi6Ssn9MvOSDnVokPYq7yDJiXQQr_FJZP5qcVkUZycc__SmvEfj3_xgpibQ6Ca1LviJsnJsRyoHnFcpWR0gGkrbCPiOhSsaUzimLEhOQy6V2Cw5qI5R1rL4LTms-THr8qZreTLmCf-b0vnzhwOUC8opOl6Xh0zzIozZvg609HfuaTr6hdAbbC13oiqA==)
3. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBL2QoCDzCPyXrcWF68-jVRF8Py5u_8M9lhJP2tiDe0prZL3ECgOGkyWeFVmodWqUeXhk0JG0GlVdRcQM54Hz3qAKk3w6QQhUHoFSvRyW2GwfQool_tO8gctmqUeyVfQ==)
4. [gwern.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEn754C2Z-gwtWxdqgNLfbwBfpYn8iNNzg781rWD8rF1r5E7DBSIABeLRrEAA0e_VOMNePXqfdFyckAfKSWYavXqULZ2LmuRUmaxNV_HONB_zJ-S4dhvM3sCBnM_cAR9dd0QzoSJaFQIHkWR2Qy5ttiyKUshFV1tHkysE1UIgY=)
5. [ucf.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfcJvhMpRRWf37CBnt-5LISAnuBK4xexOH9A-G4wB76ZgDDVjKqf8JiHdie7sO3sbA81jv1jwrpz-RuxgDIEhv4mkg1brDD8clQaFqeP69wfoVO2IDX0Z6rlWtJDvFuD2XNv70L-AYHDXKpe44JvifBnEQfS6IIB4vcexN53ks4MN16_Y9_nFeOZ9j)
6. [scilit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMMp8LWoWaCCdkFq9LtYh1Tdrh-ojxux4deGJpOE_2_sBzG04Q_iMpXQpe5R-ER-HJD7SipT_4hLQ8WNmzp2UvKcCROTVUevJuAfOOCgNG8QqFRqqNVQCLgNNcDu0so-opnVvgVCEky-_qq87BKExallz7Ha0H31Conw==)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVZ3yQbDWfgCzY-qS_byI05ydh9eUu_ws86t8mlcqqftDoJaihX3zSb6XUj-tnO-wivlxMJcehZcMqU_jcssughbIufAsNHoeY04KQiYXLbyy93eXGGXyOVfXWUDR8OqAbJ3eHgiGm)
8. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFJsXLS3DWZApTVvJ2vjnao2hOWnpvU_codPT1vKnYZnjR2dT1dGywGknLQWRPt3zE85TtZUJSXK3shJqj0VxCpz9W1anKK0eacofH0vHWh7BkTsCGbh93PR5PqcOR8ZbyU7-JUPVvhAph3L3AyJXvjG66BUMijdA2RCmWkfhKnFFC_q1bvTgyZJ2PEyrSPzRIOaxxrlLAGwyb0lflraEdWCJXDrHfR6FyK60yH2FGXQbkmRzR5femMqEE-VZ2rIL_mPVRtDY=)
9. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzAVcumRGw6Cz8sdXeHJxq93VGknVpWNOKns3tYjTsaFdxySwYUIkdrdKFPjOxrPWyn32L1f4SbVQZDXZUvfb9hEK8vTLF5_4zRVvMj8J9Sf4X0RxA4Uzyi5Wu8G_eMtikljdnkgEJXdz62TFeHMZQuVdi8zT4TYrC7I73MjevzYNJBIo92jx0J4UELDzExSPiaHevbF8NVj_fTdRsBUDurDm7YkrB0ewOCdUfHcW_)
10. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW_hlsAsuMkqNMg2ADsUFXebIusCbrsTJiZuaaIkBOSgoO29jxLA7oNw-JDQJdorUHegKh_aFSUv2q4izQVPR2_Wg_LbXE-nc_tsqMhhRn77bsVxxUScF5HtO5b5Y=)
11. [ucf.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjvY48A-J60Dj8MNMXjFUo05sldXil0lp5c7_hUNX2lmh2V2J1YWeXJSCvrAqXUVmQrBzwFBogYgKHwk1T5-Dtm5ji8ZojMlcqbJQJRQyANc8MzohNekaEF-O2m9SsCZ-bfF61)
12. [ametsoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM-SHPWfkeCbPG7t72d4c1xRwtup4m1rtv8QfQjS2b4TaIw4f_kBizOaoNLZImvQmQ2mJamEFlONmi5OUlS2tmG-Qd_L5-t-lPZVdw-Gj-zIZYsC5Q3EO3E4SLfEFmoFTGbavdkbmZqq5xVB1BQO9Z7pNn2pR2vKQTfj8PSFoQXA==)
13. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe8bpdOtRYJG46UIe_wHXOtHpgAbSMSIRP9q9lG8cwJd3mFEpNnrS5wji2dhNSLlaEwz-Ac0Qv5j_CMADbu5KxJnloMEN6GXfuERYaPs1T0ekWh93SMIAoQleAx9aSAkt6IHhISgHdWOe7-3Nk1LCa2WamgyU7zgZgAONzp9q7X9JKDjVKfuf8DmbWlkxcivsng_dXDKjX3dhJopCgVg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEun7Fv7kEfhtuNVHrvnAW-AYCvtjgEGsoMrniqgocFYw-rplvVGxMA41XGb16t6-wqfdN1P7iDrh6fU5MKz2daoOZXgDDPGY2AF6XyyxGLfM_xsakmgRWOfhC5hbvfV8GGB8da4RQECJHvA3cwzrJbZCfATAmOJeMfaYQ9WL4DFwze)
15. [evotorch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGaiWNuRMs1xHr21ycyTk3it1hofcmiSCXb0fpaxu66HSW0jko9eDInxTwqvdBYTNZ_R5xUk10gTXTO-AAABN85ORiJzDpw3KnkzrTOixlVDiWJ-7NLIXd1hWOW7pPVkucF8qs5bw0ZgwAedpBOo6nTh4GSzQXy3BhGrK40qtF2FNB7L_oRN6wgrktYkjUF8LTNZ8=)
16. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqRtx2D5yhJCeSVx5GI68IN8bR39pxSoBf5FKhZ3gTsIwtM3sSOj9_3b5ga0wrKG_DY_5-J_WJUi5vMrDyy5hYpqYEZajKglejBKyQgst7nxMc2jIBjxtblkG97IfYTcruDon8msqJH9BYoeMk4fmc-CZnSDOilQ0r_fewSkCUr0zpbOcZ7kzKUPnIVjYu_smpaJhxf8t0BeofYfnQblvt5Wk6dgVwCobNtfDapeFUc9S55Tcdi6EkHZyaJJIKYg==)
17. [ndl.go.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETxa9fCyjxBhd4Pa7S3wH4VmuVLcGIW9pcGJ71g4y6c-OR-KoavHVkFXx8XmIaXA11-BonTnkMBMiCeXGJkjy3VA8xKXQfuZiaNba1F4hfQ96OycFII6YeNqMTQHKMp5G1d-RSsMdA7XhPlk7vjUqyWnvkItIN3g==)
18. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXJjfuOal0xZ2KqzELFA49tv46d70EKwsJGkDwH4BvPlh0l_z3fh3WEsrMGVUTv6KKuOutOnsSQyZ4yC-tg1IzjE1zYMrtFGrCxVX-nwU84Dn-u2aXcBWE120WOQ0TpQx6x8K0G5tyNWe_AxQBC6X_rewWT4sSFoX-43FpSMeI5YDICGxcgBDUSB__Sjm3y2-tgjof0nyTUdf9jZfiwdq2RbikRSdu4wXwdRg0LKxa9cxT9I7RtGRUqFqdhB_Ns4wId4JMEtvaCXW9)
19. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHztUrj38FKuTtfs4ekJfff4AC-0ebQf2gR5KYzHDFJrkV82_hUByFhijDATgVVWw7ptJkKwErHqWG9gcikvm2DysenBI4Dc4wi-5aLf-BQtj0CvWCLWaU_wRY3vCPGEM1hWTWlnlfuz0=)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcZ8155xbSayp3xwNP83s7ta-NEMoEmZSQo-9qOXtNAFYPUuo2ycTr1DGpMUC7khnUaf0fXZsWCwGdVngmtgw9C63Uj152S2yheyM-FzMekNm7x0tI5hxCUCQfFYm5bHo=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6Y70U1OuIgJgRbmPA6v6-SGFw28QpWo7wlIOB4LiO6rs89hLzD2hBN4zF8wX0MHd9HwwqNIVjRHIdWS0wyKD0SoDnJq4Jx1sokPKWLWKKtxBpJ_tok_egnw==)
22. [slc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxhwVQvL65W6bXfraCod--50ofJM5FZvrdx23uL4__49CYF62XrdcKa2IEji_ud1HdNlNVzPmnH2PXR5pl8ypcV2KCm46nwlNTKfQTfztJosV0eWlGPnN49h1rZitdJXNhklS60RM1vU6bgY6-p6hZYxd9H00W2C9n9pznPg==)
23. [ieee-cog.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhVjn3MLX7Txf_3wJ56HdieV9gyNpVdFYzXFvn3IueVOaJv50WrGHnillOK2ARKo2vCyrOjOp4C-W27nPi4YvjjzgLkaut6pgs5zzZlUYIovfdHcsMJrNqImgsVdjgtl_tTldKyxhud_G7)
24. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEll9xGvrhCG_7Dsx_lMbSq19HyKhIpbhPYzRgUJ6Zl8cwEYCCbjm2Wai76CiAq1TR3hkKTUW1B3tkkdlQ1clrVDsUO_GTRZYgrZD2fxFu8i1xniDNbURp9A_dG5cazZLPt9fzSUL9Gigc0arC0gUd5RRE=)
25. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwW4wKcl1UoBvoUnd14o9jQz_qp0pwp4_HqzH3ucXVwRbmBKHweZriDyWL3w3ZKWh4jyk358Itmxi7o_iQcLmwiy5mVs5PMzTZb3i3XQ4UQMwcljxYOcYigbkEsunYdipVNd-Y0MFnRI929kaHBKOatPkI6M47oWEEYZuxyHHDbDjC0XRd8Vk5BA==)

