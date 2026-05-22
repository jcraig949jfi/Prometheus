# TSC-05: Active sampling vs uniform enumeration for falsification corpus construction

**Pythia queue id:** 343
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3X01QYXJPMERKMzFqTWNQcEkzQ21RbxIXd19NUGFyTzBESjMxak1jUHBJM0NtUW8
**Elapsed:** 430s
**Completed at:** 2026-05-22T06:19:30.527866+00:00

---

# Techne Self-Claim Verification: Active Sampling and Falsification in Computational Mathematics

**Key Points:**
*   The literature fundamentally supports the spirit of the Techne self-claim, suggesting that without strategic active sampling or curriculum-based data curation, search spaces in complex domains yield an overwhelming majority of uninformative results.
*   Recent breakthroughs by Google DeepMind (AlphaProof, AlphaGeometry) and open-source models (DeepSeek-Prover-V2) explicitly rely on active filtering and test-time reinforcement learning, actively removing trivial or statically unsolvable nodes to maintain an informative training gradient.
*   In computational mathematical falsification (e.g., Birch and Swinnerton-Dyer rank checks, Lehmer attacks), random enumeration consistently fails to generate critical counterexamples, whereas active, guided-search sampling (frequently boosted by surrogate models or gradient methods) accelerates the discovery of mathematically relevant falsifications.
*   There is a formally acknowledged distinction in allied system reliability and RL domains between an "informative kill" (a sample or failure that provides clear actionable gradients or systemic falsification) and a "noise kill" (an in-band, uninformative failure or trivial alert that wastes computational resources). 

**Context and Assessment:**
The assertion that "Without active sampling, 99%+ of records are in-band uninformative kills" touches upon a critical bottleneck in modern machine learning and computational mathematics: sample efficiency. As models scale to tackle Millennium Prize-level problems and robust formal verification, the search space of possible mathematical proofs or system states grows exponentially. The prevailing consensus in the 2024–2026 literature leans heavily toward the necessity of active data curation. While uniform random sampling remains a theoretical baseline due to its unbiased nature, in practice—particularly in sparse-reward environments like Lean 4 theorem proving or finding minimal height points on elliptic curves—uniform sampling is demonstrably inefficient. The evidence strongly suggests that systems must dynamically filter out "noise" to maintain a concentrated curriculum of informative challenges.

***

## 1. Brief Summary
The literature strongly confirms the spirit of the Techne self-claim: in sparse-reward, high-complexity mathematical and computational domains, active sampling and dynamic curriculum strategies are strictly necessary to prevent the training corpus from being flooded by uninformative, in-band "noise kills," which comprise the vast majority of uniform random enumerations.

## 2. Flagged Findings

### 2.1 Current Consensus on Active Data Curation
The current consensus in the 2024–2026 AI and computational mathematics literature is that data curation and active sampling are the "secret sauce" for advancing formal reasoning capabilities [cite: 1]. In reinforcement learning (RL) applied to mathematics, agents operate in environments where the reward function is precisely defined but notoriously sparse [cite: 2, 3]. Standard uniform enumeration or random sampling (passive sampling) typically yields trajectories that either fail trivially or succeed on already mastered tasks, providing no useful gradient for the model. 

DeepMind's AlphaProof and AlphaGeometry models achieved International Mathematical Olympiad (IMO) silver-medal standards not merely through scaling parameters, but via rigorous active sampling and test-time RL [cite: 3, 4]. AlphaProof specifically employs strategic data filtering, purposely excluding problems that are easily solvable via beam search node expansion, thereby concentrating training on harder, highly informative cases [cite: 4]. Similarly, DeepSeek-Prover-V2 utilizes dynamic filtering during RL: problems with consistently high success rates are actively killed (removed) to maintain a challenging curriculum, while persistently intractable problems are broken down [cite: 5]. 

### 2.2 Informative Kill vs. Noise Kill Metrics
While the terminology "informative kill" versus "noise kill" originates across multi-disciplinary boundaries (appearing prominently in both system observability and algorithmic search optimization), its formal abstraction perfectly maps to RL data curation. In observability and reliability engineering, a "noise kill" is an alert or system failure that is heavily in-band, offering no root-cause signal, and is thus actively suppressed (killed) because it reduces system reliability by causing "alert fatigue" [cite: 6, 7]. In the context of mathematical RL and falsification, a "noise kill" is an uninformative sample—a proof path that fails due to trivial syntax errors or basic logical disconnects, or a generated environment state that provides no boundary-testing value. Conversely, an "informative kill" (or a critical scenario discovery) is a guided sample that successfully exposes a boundary condition, falsifies a hypothesis, or yields a high-value negative reward signal [cite: 6, 8]. 

Active sampling methods, such as Global Optimization via Inverse Distance Weighting and Surrogate Radial Basis Functions (GLIS), explicitly seek informative kills. In comparative studies within falsification frameworks, active sampling identified vastly more critical scenarios (informative kills) compared to passive random sampling (e.g., Halton sequences), which primarily yielded non-critical, in-band results [cite: 8]. 

### 2.3 Where the Consensus Might Be Wrong
The literature cautions against the complete abandonment of uniform random baselines due to the risk of biasing the model or over-constraining the search space. Some pessimistic formulations of active learning demonstrate that poorly calibrated active sampling strategies can actually perform worse than uniform random sampling if the underlying assumptions about the data distribution are flawed [cite: 9]. Recent advancements propose "robust active inference," which optimally interpolates between uniform and active sampling to guarantee that the resulting estimator is never mathematically worse than a uniform baseline [cite: 10].

## 3. Problem Statement
The precise object of interrogation is the comparative efficiency of active-sampling (and curriculum-based data curation) versus uniform random enumeration in building informative training corpora for computational mathematics, specifically in domains where falsification is the primary substrate. 

In these domains—such as searching for counterexamples in Lehmer's conjecture regarding the canonical heights of non-torsion points on elliptic curves [cite: 11, 12], verifying modularity, or checking the Birch and Swinnerton-Dyer (BSD) rank conjectures [cite: 13, 14]—the search space is vast and often infinite. The goal of a computational agent (whether an RL-driven prover like HunyuanProver [cite: 15] or a statistical sampling algorithm) is to find highly specific mathematical states: a formal proof path, a topological invariant, or a numerical counterexample. The problem is evaluating whether random enumeration can practically cover these spaces, or if the distribution of the space dictates that over 99% of random samples will be uninformative (noise kills), thereby necessitating active, guided sampling (such as BOOST classifiers or active-learner protocols) to identify informative falsification instances.

## 4. Status & Bounds

### 4.1 Last Known Status of Math-RL Curricula
The state-of-the-art in automated theorem proving (ATP) relies on coupling pre-trained Large Language Models (LLMs) with formal systems like Lean 4, Coq, or Isabelle/HOL, driven by active data synthesis and test-time RL [cite: 1, 4]. 
*   **AlphaProof (DeepMind 2024-2025)** utilizes a 3B-parameter proof network pre-trained on 300B tokens, fine-tuned on 300k state-tactic pairs, and trained via RL on 80 million autoformalized statements [cite: 16]. It achieves deep, problem-specific adaptation through a specialized inference-time curriculum (Test-Time RL), fundamentally acting as an active sampler over the solution space [cite: 4, 16].
*   **HunyuanProver (2024)** addresses data sparsity through a scalable, iterative data synthesis framework paired with guided tree search to enable "system 2" thinking, achieving 68.4% pass rates on miniF2F-test [cite: 15, 17].
*   **DeepSeek-Prover-V2 and InternLM2.5-StepProver** rely heavily on dynamic prompt set curation, where the active removal of uninformative problems (both trivially solved and absolutely intractable) creates a bounded, informative training curriculum [cite: 4, 5].

### 4.2 Current Best Bounds in Active Sampling
Theoretical analyses of active sampling bounds in computational geometry and regression provide a formal backbone for the Techne self-claim.
*   **Active Learning and \(\ell_p\) Regression**: Recent works establish tight bounds for active sampling in \(\ell_p\) regression. The sample complexity for upper bounds requires reading a nearly optimal number of entries up to polylogarithmic factors, with established lower bounds of \(\Omega(d/\epsilon^2)\) for \(p \in (0,1)\) based on distinguishing biased coin flips [cite: 18]. 
*   **Robust Active Inference**: By casting active sampling as a minimax optimization problem over a probability simplex, algorithms can guarantee an estimator that is no worse than uniform random sampling. Under robust active inference, if the tuning parameter \(\rho^*\) is optimally estimated, the variance \(\sigma_{\rho^*}^2\) is bounded by \(\min\{\sigma_0^2, \sigma_1^2\}\), ensuring the active sampling process strictly outperforms uniform random enumeration when uncertainty scores are reliable [cite: 10].
*   **Bayesian Umbrella Quadrature (BUQ)**: In active sampling for probabilistic models, BUQ actively selects gradient samples that maximally reduce the posterior integral variance based on a noise-tolerant Gaussian Process. This active approach converges orders of magnitude faster in wall-clock time compared to naive Markov chain Monte Carlo (MCMC) [cite: 19].

### 4.3 Conditional Qualifiers and Calibration Constraints
When interrogating mathematical structures like the BSD conjecture using machine learning, specific data artifacts can severely skew the active sampling process:
*   **`PATTERN_RANK_PARITY_LEAK`**: In predicting the root numbers or analytic ranks of L-functions from their Dirichlet coefficients, machine learning models (including active samplers) can suffer from rank parity leaks. If a model accurately infers root numbers merely by detecting shallow parity correlations rather than deep algebraic geometry (like murmurations), the "informative" kills it generates may actually be trivial artifacts of the parity, offering no generalizable proof insight [cite: 14].
*   **`PATTERN_CONDUCTOR_CONFOUND`**: When averaging Dirichlet coefficients over specific conductor intervals to map murmurations, the variance inherent in specific conductor ranges can confound the statistical output. Active samplers must be calibrated to recognize this confound to avoid aggressively sampling noise that mimics arithmetic structure [cite: 20]. 

## 5. Literature (Primary Sources)
The following primary sources drive the current consensus on mathematical RL, active data curation, and falsification:

*   **arXiv:2507.13158** (DeepMind / Google Research, 2025): Details RL in mathematical reasoning, highlighting AlphaProof, AlphaGeometry, and the critical challenge of moving beyond static active sampling to account for preference diversity in reward modeling [cite: 2, 3].
*   **arXiv:2601.13209** (2026): Outlines the architecture of AlphaProof, emphasizing its test-time RL and specialized curriculum construction dynamically adapted to problem structure [cite: 16].
*   **arXiv:2412.20735** (Li et al., Dec 2024): *HunyuanProver: A Scalable Data Synthesis Framework and Guided Tree Search for Automated Theorem Proving*. Demonstrates SOTA performances using guided active tree search over formal environments [cite: 15, 17, 21].
*   **arXiv:2510.08871** (Cats et al., Oct 2025): *Experimental investigations on Lehmer's conjecture for elliptic curves*. Describes a computed database of 17,834 elliptic curves searching for minimal canonical heights over fixed degree fields, a prime example of large-scale computational falsification search [cite: 11, 12, 22].
*   **arXiv:1911.02008 / Nature / J. Symb. Comput.** (Alessandretti, Baronchelli, He, 2019/2020): *Machine Learning meets Number Theory: The Data Science of Birch-Swinnerton-Dyer*. Discusses using gradient boosted trees (BOOST) and machine learning on 2.5 million elliptic curves to evaluate BSD quantities [cite: 13, 23, 24].
*   **arXiv:2403.14631** (2024): Analyzes machine learning predictions of Dirichlet coefficients, root numbers, and analytic ranks, focusing on murmurations and the limitations of standard ML against complex arithmetic data [cite: 14].
*   **arXiv:2511.08991** (2025): Discusses robust active inference, demonstrating how optimal interpolating paths between uniform and active sampling can theoretically and empirically beat baseline random sampling [cite: 10].

## 6. Attack Vectors

### 6.1 Live Techniques
*   **Test-Time Reinforcement Learning (TTRL)**: Used by AlphaProof and other SOTA provers, TTRL generates problem variants during inference to enable deep, problem-specific adaptation. It actively samples local proof trees to synthesize a highly informative, temporary curriculum [cite: 4, 16].
*   **Dynamic Prompt Set Curation / Strategic Data Filtering**: Applied during RL pre-training. Algorithms intentionally exclude problems solvable by simple beam search (noise kills) and decompose hyper-difficult problems into sub-goals. This actively limits the training corpus to the precise frontier of the model's capabilities [cite: 4, 5].
*   **Active Guided-Search Falsification (e.g., GLIS)**: In simulation and contract falsification, passive (random) sampling strategies like Halton sequences are replaced by active global optimization frameworks (like GLIS) that use surrogate radial basis functions to target parameter regions most likely to violate mathematical or physical constraints (informative kills) [cite: 8]. 
*   **Gradient Boosting for Active Sampling**: Using Gradient Boost classifiers as meta-classifiers to identify boundaries of uncertainty. By training a model \(h(X)\) based on the performance of a base estimator without prior knowledge of region boundaries, the system aggressively curates samples where the model is least confident [cite: 10].

### 6.2 Exhausted Approaches
*   **Uniform Random Enumeration in Infinite Spaces**: Blind Monte Carlo generation of mathematical statements or proof tactics. Due to the strict syntactic requirements of Lean 4 and the vastness of uninformative algebraic combinations, uniform random sampling results almost entirely in type-check failures or trivial logic loops, severely starving the RL algorithm of positive rewards [cite: 2, 9, 19].
*   **Passive Falsification Checkers**: Methodologies relying solely on random generation of edge-cases for mathematical conjectures (like Lehmer's or BSD). While historically used, without active heuristic filtering (like Mestre-Nagao type heuristics for elliptic curves), random generation is computationally intractable against the required bounds [cite: 14].

## 7. Cross-References

*   **Murmurations and the Sato-Tate Conjecture**: The application of active ML techniques led to the discovery of "murmurations"—a phenomenon linking the average Frobenius traces of elliptic curves to their ranks (BSD conjecture) [cite: 14, 20]. This open area heavily relies on actively curating datasets of L-functions and avoiding the `PATTERN_CONDUCTOR_CONFOUND` [cite: 20].
*   **Neuro-Symbolic Concept Learners (NSCL) & Logical Neural Networks (LNN)**: To overcome verification and modularity issues in pure ML, neuro-symbolic AI utilizes active rule-based systems to constrain the neural search space, effectively guaranteeing that the sampled outputs follow strict logical frameworks [cite: 25, 26]. This modularity verification is critical for pushing AI toward reliable artificial general intelligence [cite: 27].
*   **Anti-Anchors**: A common anti-anchor in active learning is the assumption that *any* uncertainty-based sampling is superior to random sampling. As documented, heuristic-heavy active samplers can fail catastrophically if they overly fixate on noisy regions of the data distribution, hence the necessity for "robust" active methods that mathematically bind their worst-case performance to the random baseline [cite: 9, 10].

***
**Verdict:** The literature formally and extensively **confirms** the spirit of the Techne self-claim. In computational mathematical domains governed by falsification and sparse rewards, uniform random sampling yields an overwhelming majority of in-band, uninformative "noise kills." Active sampling, dynamic data curation, and test-time reinforcement learning are strictly required to unearth "informative kills" and provide valid training gradients.

**Sources:**
1. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9rwDTTbUThAMWl_IFEOO_WCgkUHSV_USInuCS2TcssAkj0JgvOwfT-_xtwW2attnGsF6QJNjooWo9XdCLAZKr6qOiz2t08kn0YbKr4Y45e2srdKKM616geHJpXHQ5YA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy9AhQuwdpgR4e0BhYT2ldG30R-HbpwUCs2RO0Nvpjxlp9Kx2VT0mWPcRHVwY3VJ5XK_6y6WbBwchTtHi-tKxOKQKgXKN3qST-3qCZCDPG8uS9TDnnMA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4afjleN3BVhhiQhaqsR-DUNdO7z0xLn88_85c9jWgyOKMXDoBPO17fjIrrvCRBkMzy3tgSz_iPQUL1KLxCbT4g6v-P9-Yb6lqWWXyBAGG27dcSdDQTrkSWQ==)
4. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbehxu-MAXJnyPDWDd-zqCSNbHaH0bw6lIsr6qX4zzZ4h8V8zl-oUhRAc-lM7zXRZkgqpg6G5ZwNW3LfNHqj0Y85hWm-8L9WyC0H46hvd3nS6P0NFzwMcStoS061VD0zR03HKZED3S5q-0Fwy9RDJjj6WqRiG6zV41SSAhI1jQXdkFkHEwyOAJostI0-lb2mMFPqxeNUhqLkLlk0KrMceaLvcd7R4anWIjdVcfbTNfupeBxw4rqklPsY4o1ii2JFHRd7jd1_b1)
5. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZl5DktyebMgLAfAxVNbr4HgVtMQoxran78mK_uFg-7kyvs_vd9LxJj5_rZS73lQ_IOu8dGd5Qsb6HZiNk4Niovp5TLGMJWYoSMLY5Xulol8MAM3syP7oLcc9dGOJ_k9jZMXWGWQ==)
6. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU06KFk01vG97ieItPBBYWh_-IuFG36snx1A5z_8KDzGC3vhGPNvwzDKQsHs7-M2v-gBEqkS6-tlZsk3EVcId7GaDo4jhyEutfKsACRs_743MrH_J0exmav1VHhTVWajqOK5wsJRod4S1KWU-u-dQKOA0k4Fk24UTGTr7jVI4dP7oNlCaiZ1IklbFFWhT1F02fyHIx2pME8jeMEor6c4cSniiQ4mc=)
7. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsw5UNziDcbAGSLeqpzfrRnXr9y9FVKMpOlvkdQgHRWwEo42h8jKv4U2HTwNyRs4jKVmIlo9XGqxVjZMPgeIFvAD4n9e9HjgcHXdefVPW6QJxvAc9AT5a05wEgaLxYA6scNZFXC53ol2vHMhNS6lUXqrG791t_AW2VKa3yKfjYMiSErfGlL61I_4QJP9IaWvfPH5FBqH4v)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWBm1eS3nU7abHqT8ydPGpvJ9g2rkGR7orNROPEiyQgWoxLsMOUvca9hAaxkuVnzv6cnoLPLypGcicVvc4wuRi2Jz3FbtIv9om6QX3jxwft5RXDhPdwg==)
9. [ru.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAEZ-dBFunPOhTeeJQVAq0-FXW8XgoSPEFWx8wTvoXU9TIaHsTiv_K2kNX-PTXk5Lb9sU2acqFaxfJGEEvdBk0S7V1dlc6Seqqr7OS0KzvBhJ33phpPtyHCeQBqkscctD6YGehE7r2KSrKohOP0JfNJOrFJhk7v5G1EeG3mL-Q7nGnQSqp9G9RZ9N7Z_1Ud-7XxE0VFh9We7drJH6Zat3yglqZ5qYr55dbWOGhU4OZlA4C5H2FREJVh1m8wfeaTf0jESVhOQfbmjNTteN6glfPzA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6nwmOzRmIMBhNT5lQMCmKWfWkAN1bH0cHJVyGZtjC8z-pNhS-Ls2zD3LDg_9oEiLDrv6TxHKdJ8NWI-MhZ2Ob-JuppMfJph496QoJluVj1yCU_XOGivqj_w==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRQCXuSYqNvNzqcT1zIKcqLbS6aQtD-UtowArVMWJ1XGRQxb3JReQyX1hsDOE4Gzc2YY_0zJVToCTuSboJoVkXaw5nwjnZaHIibpUIb7xYqZJLOHkBc9fn3A==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBbV4P_xpRPjuDdOl9uRf8aoj-H6EIaozq7M6XaCFQsTwsGvE2cGenZvX2s4zvjuy4E-ReKV0ZZzDzQajq6AN_ZdnT5B17biGlSqzMjalW3XbYOGPSOw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4DgryHsaeBllRHmcFq-y7cutUWgzXqKYD1f5jCdqcMKi5TkSfExCw5iAgmXmyLr1QRf5CU7zozU5qs97-QQqwWIrsc0MIMMCbXj7Ha354_2FerboSmQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGti4VyTYW9nGoWUxiHiJP1Nq7fcePsRfWaBpnFiWptIs3J4iNCJZ2TRakSnAhP6m3hQWpYZeWZGowyeJFo-LH8trXHt8Ivtfwq2rz40IWw5ft6qR3Cw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFePRH43qUy58bJlv2o0coXO9-UI-pacWHbBf-TqqOdkNCou8IpqgUeWLZx_VH6Bo9aIDn7nJc8kYM3zaGsuSb8I_CmyVmq7-dSBKMZI9hthesSp6_Liw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3qzbyPMg7EuNXVIxUa2HnZ4U-i_yxlCY1-z0QHbY_iFbXqC5WRNsVOR3EzEJvq_GE6nwJdS4-mtPLGoTv5Odmwfwcg9MvjnxOQAPCFmD792exZDE-YzRarg==)
17. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE79R7WgNrchaJV-dY_eK-__etTiQdmhZpPxvAO865hHDbEOkqbGyJx-wDD-tTmxtJNP9jlgX0dncqkpxdie22mMnWwUKMRQhLklrSFFp_dHGe6JC43SiLPcdys1sMB)
18. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHc36PATB4hlWHQ-jzu2FPZrOmMUyVg0RIVfwR3ozaAVlq37BHmtgYHPCF7zHqanTG8XMNV-0WqDQLLoBkMBwmnIOeuAKh_uW7vHna_Ow3PJOQLD1LBRhVKxJ_KHPy6zPyQ8RKX17QqRCCP2biwdlfHk0wBzuZzA==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgU2HW3FHkvD6cD1TQatzWK5WCbwXjYO46b1PVsOFz4a3-0p6GTnmQssTAYKf8YXhPK3QulqQZ-I0VKSML85XHaGvdS5w6c7vm36wwQI3bSKs3sLgODkFnyLvGJ_CpuR_hAo1Gan_ETFc1zkGmmBLIPjrkS2rdkvmP058rhnL1VUP6NcSl_glcdiG4b3Rigopfbn7eeIdj70KxopyP34ZNawVf4jCbfVU-NWsbBkzSuVVbKq2R)
20. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfDZSflYikq2pbYlpbdA2T7hUKLWyKNL6o3R1775wZflDfUEXdQsXSy46DoqAKLPDoHknwBJe-jKg3wDjr4c4WSK6EYxmqYmTje6SqaMmk9SXLk2LhL2SqsoeCeyIM895k)
21. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3qbynRmHtpBTVfMxSr1JlOS5rfad_DgSfe5EljlTgk9P-UCjn7EOPaIzX_n0W9RZh2t52wcpluBpeiUYYOSJQE3t2eoFnKxLC5R8qxZcp7Jy6wemKKC4K_Ml1vzMb7JUjamc=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGan-6UdSHUyxQOH6rU6gI3qJuq47Z1ilWAxmVknbGdZxeOSwHojWzqQnBDIpa0O8VVmWhA9eBNPYPK3FYktKh_sH_K56UM9ShbGNF7opZuz3VGr5h9jA==)
23. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRSK7f34r5OH13OiKHoJ77Gn7cIjTUczm256AZu2y_DNy7GCVKsGq9k1uascn2AKadwiKX_eeWP1PI4tWeA8zGOrG6_fUDdtbG9U_L5gGaYC71wmNkS56Oru2JG3ky8YIaZHSnuyYXbRpyhGQVDM0-N3z943NQvCHOabt2sEwPac0PugodQcUhw_PB71hQIA6Zb5WG20HYCajeniZ56spbxFjm9Kw41DQWaLdGb549Hz5V19PIv0ngcURQg8UJOq-iQIlmV-nN-FPPx-6f_QRyh1ti)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqGSpluDFjNOCkslbfla0q85kyUxjT5ZXr5eXunFkq2Aa1NkR15gBp5S4J1YjmcHCNVrQniB03XBKSTfd15gk5kJHLwd6GFYeoYrtDJiPvFO-072s-GJDazC1skvbfwMgneWnCmibxRxEYBhpMa8G8CEjWJ-79bPoSyeKeBmmmSgBpPyZtLbor-m88JUP_H9hP3XhdZ1CUZ7AmnM-50zGa4NCbLZSYIrY06EBdmJekiFTXmhqxzlkl)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSb9NrfejY7xsp0pPRxMoa0mGGSQummULIInxvkpbqx9IgxB5d2SMqqsP_IVVi8j9tLw6VccK3Jy1esI-e5jp5ue_GT25P32PqZ_DSriGJvte83yS5AU2-H2CwHY-P6R4kfMTnrxgI1dFF4usG4zWAiWdTkoQPpI149NZDnLG_dumm7A==)
26. [deepgroup.do](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJgzPsXRpj9MKS8ths2Y9ZFYBmV_SUYAoHQTc1e8BfopJxVL69-ZyuqJmeTnFmRdWc8fXvWqv7sdNiAyZ7cfuTkcFpXpB-VoIa0I8PAt72LQTCvj8vaDpa9y-E3mNahsa9aAjA9_5qyQuDQArBE5Mj1a2DGL8=)
27. [cdf.am](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKcLa8TvVfLyunqexPPnc2SlT2C1qVoShap0_8eXDmi7ZKh9fT14Tc5SXG3uq6D12OLipO_UgmOmC_Ue1WJwimYx8OoPGfIRF3ImHFyWmXRKUU_RnEG6jgIzXaLIJX1ktfwU8NPimmjFtPeA1Z7zxCMPHt_OpyVWEBkCc=)

