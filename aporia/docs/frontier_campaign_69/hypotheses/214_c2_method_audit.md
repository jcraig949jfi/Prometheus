# Prompt 214: C2 method audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiWWlnYXJ6NUNMLThfUFVQdWR2QTRRSRIXYllpZ2FyejVDTC04X1BVUHVkdkE0UUk
**Elapsed:** 243s

---

# Methodological Audit: Cost-Matched Comparisons and Budget Standardization in Machine Learning

**Key Points**
*   The research community has established clear methodologies for comparing structurally disparate algorithms, primarily by plotting performance as a function of a unified computational budget rather than reporting isolated cost vectors.
*   Reporting a multidimensional cost vector without equalizing a unified budget axis is a known anti-pattern. It transforms algorithmic comparisons into incomparable apples-to-oranges scenarios, often masking resource-heavy methods as algorithmic breakthroughs.
*   Retrospective audits in fields like Natural Language Processing, Neural Architecture Search, and Deep Reinforcement Learning have repeatedly invalidated published conclusions when unequalized budgets were later corrected.
*   To ensure interpretable results, your research programme must adopt Expected Validation Performance curves and define a scalar exchange rate for disparate cost units (such as joules, dollars, or total floating-point operations).

**Context and Complexity**
Comparing different computational methods is inherently difficult when those methods perform entirely different physical operations to achieve a goal. Research suggests that simply tracking how much of each resource is used—such as counting database retrievals versus counting neural network training steps—leaves the final comparison ambiguous. If one method is cheaper in memory but highly expensive in processing time, determining the "better" method requires a standard metric of exchange. The evidence leans heavily toward standardizing the total resource budget prior to the experiment to ensure fairness.

**The Evolution of Fair Comparison**
Historically, machine learning adopted conventions by habit, evaluating algorithms based on fixed outer iterations or wall-clock time. As methods diverged structurally, these simple metrics failed. Over the past decade, high-scrutiny disciplines realized that without strict budget matching, they were inadvertently measuring which algorithm was allocated the most resources, not which algorithm was mathematically superior. The transition toward rigorous budget matching has caused substantial upheaval, leading to the retraction or invalidation of numerous "state-of-the-art" claims.

## PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO

Several disciplines within machine learning and artificial intelligence have confronted the exact problem of comparing structurally distinct methods. They diverged from the habit of simple wall-clock matching because heterogeneous hardware architectures and disparate inner-loop complexities rendered wall-clock time and iteration counts meaningless [cite: 1, 2]. The fields that faced the most external scrutiny regarding reproducibility—namely Neural Architecture Search, Hyperparameter Optimization, and Deep Reinforcement Learning—have developed specific, named machinery to enforce fair comparisons.

**Neural Architecture Search (NAS)**
The NAS community faced a severe reproducibility crisis when researchers realized that structurally different search strategies (evolutionary algorithms versus reinforcement learning versus gradient-based methods) were being compared without matched budgets. Early papers reported whatever cost vector their specific method incurred.

The field settled on **Tabular Benchmarks** and **Surrogate Benchmarks**. Specifically, the community generated exhaustive datasets like NAS-Bench-101 (arXiv:1902.09635) and NAS-Bench-201 (arXiv:2001.00326). NAS-Bench-101 evaluated "423,624" unique convolutional architectures exhaustively [cite: 3, 4]. By pre-computing the exact accuracy and training time for every possible structural combination, NAS researchers completely separated the cost of evaluating a model from the cost of searching for it.

The established machinery here is the **Budget-Matched Random Search Baseline**. Practitioners map all structurally different costs to a unified metric (usually simulated TPU seconds or total queried models) and plot performance curves across that budget [cite: 3, 5]. When fields disagree, it is usually over whether to use total floating-point operations or hardware-specific latency as the scalar constraint. However, all rigorous NAS literature now demands that comparisons be made at strictly equalized budgets using these standardized search spaces [cite: 6, 7].

**Natural Language Processing (NLP)**
In NLP, models differ drastically in structural parameters, parameter sharing, and pre-training data volumes. The practice of merely reporting a cost vector (e.g., parameter count, inference latency, and FLOPs) was found to obscure massive discrepancies in the computation spent to find the best hyperparameters.

The field settled on **Expected Validation Performance** curves as a function of computation budget. Formally proposed by Dodge et al. in arXiv:1909.03004, this machinery calculates the expected maximum validation score an algorithm will achieve given a specific budget constraint (measured in GPU hours or hyperparameter trials) [cite: 8, 9]. The NLP community diverged from simple point-estimate reporting because they realized that comparing the best result of Method A against the best result of Method B is invalid if Method A was allowed to search for its best configuration for two weeks, while Method B was only searched for two hours [cite: 8, 10]. Under external scrutiny, top NLP conferences integrated this requirement into their standard review checklists [cite: 11].

**Hyperparameter Optimization (HPO)**
The HPO community exists specifically to evaluate structurally different search arms (e.g., Bayesian optimization versus successive halving versus evolutionary search). They settled on **Multi-Fidelity Budget Matching**. Machinery such as HPOBench (arXiv:2109.06716) provides standardized containers where disparate methods are constrained by an absolute, unified evaluation budget [cite: 12, 13]. Practitioners disagree slightly on whether budget should be measured in function evaluations or exact runtime, but they universally reject the idea of simply reporting post-hoc cost vectors. They require plotting the anytime performance (performance as a monotonic function of budget consumed).

**Deep Reinforcement Learning (DRL)**
The DRL field experienced a reckoning when it was discovered that structural and extrinsic factors were routinely conflated. The established machinery is **Intrinsic vs. Extrinsic Variance Control**. Henderson et al. (arXiv:1709.06560) demonstrated that disparate methods must be compared across identical budgets of environment interactions (oracle calls) and identical hyperparameter tuning budgets [cite: 14, 15]. The field rejected post-hoc cost vector reporting because the variance introduced by unconstrained hyperparameter tuning swamped the actual algorithmic contributions.

## PART 3. THE FAILURE CASES, WITH RECEIPTS

The history of machine learning over the past several years is littered with documented cases where a failure to match budgets—and the subsequent reliance on unconstrained cost reporting—invalidated published results. The following are specific, documented cases where corrections changed the conclusions of the literature.

**Failure Case 1: ENAS and Complex NAS vs. Random Search**
*   **The Claim:** Highly complex algorithms like Efficient Neural Architecture Search (ENAS) and DARTS were published claiming state-of-the-art performance, utilizing structurally distinct weight-sharing mechanisms and reinforcement learning controllers.
*   **The Receipt:** Li and Talwalkar (arXiv:1902.07638) re-ran the literature using matched evaluation budgets.
*   **The Correction:** They proved that when the computational budget and search space were strictly equalized, these complex, structurally different methods performed no better than a simple Random Search baseline with early stopping [cite: 6, 16]. The original conclusions were invalidated because the prior authors failed to control for the total evaluation budget, allowing their preferred methods to implicitly consume more resources. The SOTA results were an artifact of budget discrepancies, not algorithmic superiority [cite: 17, 18].

**Failure Case 2: NLP Model Superiority claims invalidated by Computational Budget**
*   **The Claim:** Numerous NLP papers claimed new neural network architectures were structurally superior based on test-set performance scores, reporting various training costs as isolated vectors.
*   **The Receipt:** Dodge et al. (arXiv:1909.03004) audited multiple recent model comparisons in the NLP literature using their Expected Validation Performance machinery.
*   **The Correction:** They documented multiple cases where authors would have reached a different conclusion about which model was superior if they had used more (or less) computation [cite: 8, 9]. Applying their budget-matching framework to recently published results revealed massive, hidden variations across papers, with computational investments ranging from hours to weeks [cite: 8, 19]. The failure to plot performance over a matched budget curve directly invalidated the static superiority claims of the original papers.

**Failure Case 3: Deep RL Baselines and "State-of-the-Art"**
*   **The Claim:** Novel policy gradient algorithms in Deep Reinforcement Learning frequently claimed superiority over baselines like TRPO and DDPG.
*   **The Receipt:** Henderson et al. (arXiv:1709.06560) re-evaluated these claims under strict external scrutiny.
*   **The Correction:** They found that fine details of experimental procedure, specifically the unconstrained and unmatched hyperparameter search budgets and network architectures, were responsible for the reported improvements [cite: 14, 20]. When the baseline algorithms (TRPO/DDPG) were given the exact same tuning budget and structural parameters as the novel methods, the novel methods' advantages vanished. The published conclusions were artifacts of unequal resource allocation [cite: 14, 21].

**Failure Case 4: The Efficiency Misnomer**
*   **The Claim:** Models were frequently reported as "more efficient" by highlighting favorable dimensions of a cost vector (e.g., lower parameter counts or fewer FLOPs) while ignoring other dimensions.
*   **The Receipt:** Dehghani et al. (arXiv:2110.12894) documented how this practice systematically misrepresents true experimental costs.
*   **The Correction:** They showed that a model with lower FLOPs or fewer parameters can actually be slower and more computationally expensive in practice due to memory access costs and lack of hardware parallelism [cite: 22]. They concluded that reporting isolated or incomplete vectors leads to partial and unfair conclusions regarding model comparisons [cite: 1, 23]. Relying on a descriptive cost vector without mapping it to a holistic, matched constraint results in scientific literature that cannot be accurately interpreted.

## PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN

The proposal under audit states: "charge every one of those costs to the arm that incurs them and report a full cost vector before any comparison, rather than equalising an outer wall clock or a count of outer iterations."

**What It Gets Wrong (Mechanically)**

1.  **The Incomparability of Vector Spaces (Lack of Scalarization):**
    By reporting a full cost vector before comparison, the proposal leaves the comparison itself mathematically undefined. If Arm A yields an accuracy of "0.90" with a cost vector of (retrieval=100, decoder=10, oracle=0), and Arm B yields an accuracy of "0.92" with a cost vector of (retrieval=0, decoder=500, oracle=50), there is no mechanical way to determine which arm is superior. You cannot compare vectors across different structural dimensions without defining an exchange rate. The proposal completely leaves open how the actual conclusion will be drawn when the vectors cross over each other.

2.  **Budget Confounding and Implicit Bias:**
    By refusing to equalize a budget constraint prior to the experiment, the proposal permits unbounded resource consumption. If researchers favor Arm B, they might inadvertently allow it to run longer, incur more oracle calls, or tune its decoder for more epochs until it achieves a positive result. Because the proposal only *reports* the cost post-hoc, it fails to *constrain* the cost. A post-hoc vector justifies why Arm B took longer, but it does not tell you if Arm A would have reached an accuracy of "0.95" had it been given the equivalent amount of total resources.

3.  **Static Point Evaluation vs. Dynamic Scaling:**
    The proposal mechanically assumes that an experiment yields a single point of accuracy and a single cost vector. In reality, machine learning performance scales logarithmically with compute. By not forcing a budget constraint, the proposal evaluates structurally different methods at arbitrary, isolated points on their respective scaling curves. This is the exact mechanical failure identified by Dodge et al. in NLP [cite: 8].

**Where It Is Sound and The Boundary of Soundness**
The proposal is entirely sound as an **accounting mechanism**. Tracking every structural cost precisely and avoiding the over-simplification of "outer loop iterations" (which vary wildly in true cost) is excellent engineering discipline.

**The Boundary:** The soundness stops the moment you attempt to use those reported vectors to declare one method superior to another. It stops being sound at the point of *evaluation*. Accounting vectors are prerequisites for fair comparison, but they are not the comparison mechanism itself. To cross the boundary into sound scientific evaluation, those vectors must be mapped to a unified constraint axis.

## PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE

To ensure the research programme yields interpretable results that survive external scrutiny, it must adopt a strict budget-matching discipline. Below is the minimal set of rules, ranked by how much interpretability each buys, distinguishing the necessary from the best practice.

**Rule 1: Define a Unified Currency for the Cost Vector (NECESSARY)**
*   **What it is:** You must establish a mathematical exchange rate between retrieval costs, decoder training, and oracle calls. This usually takes the form of total hardware time (e.g., GPU-hours on identical standardized hardware), financial cost (e.g., cloud compute dollars), or energy (joules).
*   **What it buys:** It collapses the multidimensional cost vector into a single scalar value, allowing disparate structural methods to be measured against a common denominator. Without this, no comparison is possible.

**Rule 2: Enforce Equalized Global Budgets (NECESSARY)**
*   **What it is:** Before running the science, set a strict, globally unified budget boundary based on the currency established in Rule 1. If the budget is "$100 of compute", Arm A can spend it all on retrieval, and Arm B can spend it all on oracle calls, but both must halt when the budget is exhausted.
*   **What it buys:** This completely eliminates the confounding variable of unequal resource allocation. It proves that a positive result is due to structural efficiency, not just spending more total resources.

**Rule 3: Plot Expected Performance as a Function of Budget (NECESSARY)**
*   **What it is:** Instead of running each arm once and reporting a single point, run the arms across a range of predefined fractional budgets (e.g., "10 percent", "50 percent", "100 percent"). Plot the performance curve.
*   **What it buys:** It reveals the Pareto frontier of the methods. As Dodge et al. demonstrated, Method A might be superior at low budgets, but Method B might overtake it at high budgets [cite: 8]. This protects the programme from publishing a positive result that is entirely dependent on an arbitrary stopping point.

**Rule 4: Implement a Random Search / Naive Baseline (BEST PRACTICE)**
*   **What it is:** Introduce a control arm that utilizes the exact same unified budget but allocates it randomly or naively (e.g., random network topology, or uniform random retrieval).
*   **What it buys:** As shown by Li and Talwalkar in NAS, it protects against the embarrassment of publishing a complex, structurally sophisticated method that performs no better than random guessing when budgets are strictly matched [cite: 6, 24].

**Rule 5: Report the Raw Vectors as Metadata (BEST PRACTICE)**
*   **What it is:** Continue with the original proposal to track the exact multidimensional cost vector (retrieval, decoder, oracle), but relegate this data to the appendix as diagnostic metadata.
*   **What it buys:** Transparency. It allows future researchers with different exchange rates (e.g., if retrieval becomes radically cheaper in five years) to recalculate the unified budget and reinterpret the results.

## PART 6. TOOLS AND CHECKS

The following resources implement the necessary machinery to enforce fair, budget-matched comparisons. 

**Show Your Work Codebase**
*   **URL:** github.com/allenai/show-your-work (UNCONFIRMED exact repo, but derived from Dodge et al. arXiv:1909.03004) [cite: 8, 25].
*   **Maturity Note:** Established in the NLP community. Provides scripts to calculate Expected Validation Performance curves based on hyperparameter search budgets. Highly recommended for converting point-estimates into budget-aware curves.

**HPOBench**
*   **URL:** github.com/automl/HPOBench
*   **Maturity Note:** Very mature and actively maintained [cite: 26, 27]. It is a library providing multi-fidelity benchmark problems for hyperparameter optimization, specifically designed to ensure reproducibility and fair comparison under matched budgets across structurally different tools [cite: 12, 13].

**NAS-Bench-201 / NATS-Bench API**
*   **URL:** github.com/D-X-Y/NAS-Bench-201
*   **Maturity Note:** Extremely mature standard in the NAS community [cite: 28, 29]. Provides a unified benchmark and API to query exact costs (parameters, FLOPs, latency) and accuracies for "15,625" architectures [cite: 30, 31]. Useful as a structural template for how to separate evaluation cost from search cost.

**NASBench-101 API**
*   **URL:** github.com/google-research/nasbench
*   **Maturity Note:** Highly mature dataset mapping "423,624" unique architectures to their trained performance [cite: 3, 32]. Backed by Google Research. Essential reference for how to exhaustively evaluate a search space to permit algorithmic comparisons on a level playing field [cite: 3, 4].

**Responsible NLP Research Checklist**
*   **URL:** aclrollingreview.org/responsibleNLPresearch
*   **Maturity Note:** Adopted as a mandatory standard by the Association for Computational Linguistics (ACL) and top conferences like EMNLP [cite: 11]. It explicitly mandates reporting total computational budgets (e.g., GPU hours) and computing infrastructure to preempt incomparable point-estimates [cite: 11, 33].

**(End of Audit)**

**Sources:**
1. [takara.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIsQcvnqUqest9eq9FOiaslWF2nxT9lUzR9wW7eiUDcWu5Lx2ELKAtdYXKZ9v74XM7JvIr37_9PcnPOMehMD3erptyaWBs0oinZXI2U5aElyXBQLiw0UhVgA==)
2. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH7J6VDy976eSQw5BY0PmcxsQJS3WUU37uoTuBs21htiAR63l9d80pSa2FIA9WhYy597T7DKs7SVvuADyj24mBwlRBULtaVP-GU8KMnaN75Jlsmv-URV8JbeLkV8iqN4Q9DyNtkDTVwqE=)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtz6kHhM0Hwk83nDbHmlcTl9oM61HUiJfBu4pizWSb_mWsDgnMexncicvophhUWaCGjuJqxT9p7FyjMdftcmRAU0l6PJ8N6QxJ0sg3aBkz3WFWhkqncAkhRaoXjzrYCd9IjHMzCnbaEVWj)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLdVg9TqEWFhK5hhg5-KZHKsNfkt3q2iFfQbl9OdBS4Z8CAlo4SvOUknMH3xDV5jzkBGCa5XYX5oCq7K2WQT8rflDaGt4yEOhkwqp8AVoX9S7Ycd4I6A==)
5. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlIpYjPTOHmzUBk-cxqhbDv63u9uvzkJ2y5wNhL0W3uFOLyVlEjLh7Zw0urOLTstkbuogUX3PNIsjaGO18IdsqqqD-6jk2EqYVuDhuzlEfaXsv-dip7jeW3T4NsWj0EF-1N0cpNVTM5UwaG-Stls-lP_TODHVleoUoZgQ=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQUfRPsqdsg2_wrTs-mKbTeqQ-Iv5Is1SvB8JIkH06TOAy9NQKYsllb5IWUG9qIIkyJUpqAKU_D_d_WdvUNOSFk9pA3HBq2du3OdnHbw4cOhjGTmdMhw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc3fJ3oatkl_8er9Dkcar-Aj-xzg4XopqIo1yq-8qJ3qvr5NkwZiIHlAEsdEnYXYUdhqNVT1wpGScnjrXVVH77NvcltmTQoN4MI-Kmsuq5rxsoTFsLXTUozw==)
8. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7LYib0eT8dWrEhI57JSv7kLYvZspGbLhfNWsKMor3m6ApuCoBGPGgERkRUvrVPK2vRlHhJlw0ebtXs290F6HKher-hUEzQQIvclab1OepJgwESuLwgS_g)
9. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB6M-F3u76FU_d4ZXhDMNpE0tkmTBnwo19bixOvt7V9X65eJBuAWOKf_O5dBbEpl0vV-rO-oNomsk-YgfFXmOXMlz36miCPSU39y11ESkUuvhqooLDr1nq2qcH)
10. [liner.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlYtlgxa9tv1EShf4w_mssCOyaoQdxWsGZ0bJcg0-2qp0CoRAFhGIAx_ij14rZzEPcl4fhRY25joNS0pScJep0PXq6S9pM0h-U_JAtcX6dYyieCS7KGnjcPMGMlG1m7xVKsem9-519yBFmAaLcemcC7twJExj1JtKgzi_9tkDz2iA7DIoC)
11. [aclrollingreview.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJY_-d2AYaMvZEaMMzubIviySuQ_gLTLVzWPy9TyCK1N5H4KC78_4qqGYSBszNc8LyFHN_Ok6ixBOKaCNxdsPkjQ0HtbkZdTFMA6ezJh8kfaj3l935RDxIzT9ty20l-bvbKfC8vyB0b8-4)
12. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyoESGwrzTEQ1uUjqHypbsgxmrazNWsRMmgc4mpSwDvKL8I0AOlK2Q1My-EFJQ8p-CXBqCJreMimTm9rqebgrdbXCDojfSlJYr-allwuPEEPTGXKyCAFvnw_p1e82zJQ==)
13. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN1xEbz1N9iKpTHl2UedHOM29lXBuOUzSx1UJxOsx5WmaJsnHQL8HnsXRBGH0m1O53SL4I73nMlw9QYDTXniSKr6w2qvRwzbvpQJNIzt5YXxJFJq0QwbUoms-q)
14. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj2GaOo8-KP_v01STxMLG52ghKxYJ_PWqNrE3QSXlIFhvS6rwO-htEw59nqkRDE4_5xiDFl7gtyC5z5q2CdJnz0tyF6wTbDgtbOn4dDmVRLItOoAKWtFEwoydPKUQ=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYRWy1Lj6JNrPjVoB2uxSso-hc-SXPF1Kboobn_JZFXtwEpUn_CA_acuzlIOjjX_L1ROWC4huW191xP6oNd74ELKS4fkFGiLSxCuag-gxpDcttLIXXRLBx4TJff5RaJmKpkVf9pisg6XrEeojAfOQzCMeaSXo65ElUaedGNnDudf7aRRtjtYz7Bka1V3yAsl_e)
16. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ68S-8gX2x-0kPn_Thf1LabyMupn8dthIs8O6eDfAdH4osSmx8ToAwG7d9_ZqFAc0pyRIS2L4SYFxm8RkQP_ByLw2kpJJvBQHT3PqxEbFEb6JYmsuE1AR_mLF3c29HyIPjO8XzQLmUOwfbrnS_B9X)
17. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8TItlzDbmyMLMs5PsbrV8aISZpk02F4VFz6FNLaaDpaw8XyM7-G7AxFLcON2MUweZ4ZQ2lDnrKO4nYBLn_dVUYf0yvhAzJXt0HtOd971NAvEubhjdjfM6eI-MJgqRrK8ldxRmGg==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpQtuXtMNI-3sK5o9WNY_RS8uCRBb5kwnWd7V2tPBEfFdfeCXdigjFSMAHzcZSDNAhjVTVOxyL7YkdI8uMIpnS1l5d1JuEDprNWuzrnkmxq00dMnQCr5A8uw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgv1GMAugmIV-prYJjG7ynLqDFzPzklOc4ZtIaA0vY7YqRf5CpzJiKDYorKJGDATzszeAES4OuGFUvhnoeR8XDeVRpWjqaLXYYIZ6GWKoDoMJDv0AoQQ==)
20. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzCQDySPorwr3oiSGqAiWuVppbkiDjPG_s4FZA4Xm-LbhB-FsiEMym7Z9fsPRfeIMVR6yYEXlCgRliRz8v7GUZR2W76dnLAoR7qzgx772Jc_ey0VgI-8HA0frY7-oqJsCSCadsvjn8vTloN7c5N6nxWkcETu7fE1mT-5yDT1eaSoiOZuhQ_g==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY08VgCEd-o9hJI6FVlMP88jifmZgjdchFDASknXL17Akn5vzBFE_qc0Z1-_EeAEXkn5thMMvf6UuLdGpmaenvaJaNMN2HoBb58bFC4DIlxMDa-KEWIg==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR85r1ewpVomW7RFfLibYICahYiUIhQhQMgB6Rtclm2THTvk8MUX8ig3mRi4ns8t9VT7BEikP-XUES-vLRBVoBds_Mp0tA8kSmGavb4IxXIXX4T1aV-w==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjdb3QHn-vvoBuDHAAhCsf1m_t2Q7tp5_ztLs9qNGUpVX9FyHMs-2M-qtVQ5g4oHBWRuxz7SirastL_hilvkVH4Dk6u4x0XTtC8GmF6jzhAqVlQ2EB-A==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIFFimwrvzOVrve4Ld1BKj_4OcFFhu1lCcLn8RAzo3N9Pq1IIH7tmmfi9CVhZmqjtkn_BwDHHUckYBif3OjGLupaQe0atCd9H3aWp3QzXoTiXidxtMGK9lDuOYHd6bJh4RGTvE25-70KzzPIrqIlC5jfr-GhbmxuWELRqG3Kk812YMJ6FQLpKVMPUKs58WU1kuZhSxIN1eRce8eF9z9eK9o37Iu-GXhdh9)
25. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7FVovntkMV7SnydFo14zwmLq6L6LCRls_2A2FlCOLk_3U1OoHDGSL1rekfpMrby5j4U0LvBAyBG26hLg2vz9OHlReyVA-zohWkdk_A-yQjFzVmKYEP8cW3MU5iUd81o1HhCk=)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzomUd0iVX0-GCMa12QVyqJ1erwNM0MTVskqI-2d5_q53DgE30Wc0qySp9RtMZdbGaB3KMjehK4UL3WJt3zRAw6q0NV10N2Jgj2LVgn5RSYtyb5-iR5iby)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7kGQRulKeWsS1kjDsNLrbqeH6r4ApQd7thShmntneUCBOLhQcpWhYXFTWEeDRLewlZOx7J8w2M3KUYiCkzjAPuiXSfe1MPKIfCGeA3WfFQzeyOEAyz1UoJpcCPTwo4tI14F9NTql0FkUi8xz8)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF17NcyP1XIXggwE-uofNUx8k94WZlAL1siWBCA9Xjsz1tIz9K8tEMyyQ6AkD7DyJHwrPBll6FrTW6gUx3h-1eSVcsEBeliQfTixVOBaDRhij7nXs8VyhplLUYZA==)
29. [optuna.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHnXRnTqVL1eXCasG02Z77wOA9QBP6poA2JGlAa62Ak_6h9r3ajZTCz-Ph0-7i6qXONPd7T67kph02aEVcPhDIQ8yDQkbOGVnEZyGz_bQ2PJRvHBvd5lmoNpD-su76MkXTIXrA)
30. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxMT9ilrwP0Vi0S24M7pTxezNH1CMPJUQwqmj8At-VAGa7HQupKo60KdH7NDnOhynvgvuHFeDHRCSYa7heLZjjVxKBFbYC-tokelv_r_IEoBIhQFl3B4IBczToCDh9)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7st8xCODIXOtEmKgMpQ18h4z9flvqc9iTr09mKDLNq8n3a2jBqpqLhv_zS1zo4OGfoIiaYJ8nEJ7Ol4wkeJ8BaEB6WN-Rf4z6q5sLU3_mwkbqw81vKA==)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ36iEZ_H17Ym8vFse2yB89Fl7L9DHrFOK8c6qhgnefPedhrlW62a-AePFH64QmWMzteOXh-iB2IZGBvcHyxQiuVp2saZ4EYBJSLt_Wm4EY4U8zCqUkJHT761NQjL4_5z7)
33. [tib-op.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQzgaqIlaGfcGt_KGqredL1J61R8QgRg0kGWwJtXOm6CsgHh1z6yoCPPmJxRne6JcQSTbirY4MPVMoSf_yLsLxJwaNMyRHFTaEGTSSl1Po53CN04L0YkZyloBEFK1QumIB5Zu9YaPAig-tHCfAw3qRTQ==)

