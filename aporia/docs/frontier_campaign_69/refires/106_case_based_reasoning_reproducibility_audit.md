# Prompt 106: Case-Based Reasoning reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3cmVmYXF5YUdjU2ZfdU1QMk95VTJRcxIXd3JlZmFxeWFHY1NmX3VNUDJPeVUyUXM
**Elapsed:** 395s

---

# Reproducibility Audit of a Specific Historical System: Case-Based Reasoning

**Key Points:**
- The classical Case-Based Reasoning cycle (Retrieve, Reuse, Revise, Retain) is embodied by historical expert systems such as PROTOS and CHEF, as well as modern software frameworks like jCOLIBRI.
- Focusing this audit on PROTOS (Bareiss and Porter, 1987), the system is REPRODUCIBLE_WITH_EFFORT. 
- While the original Common Lisp source code (CL-Protos) was distributed via academic FTPs and would require significant porting for modern environments, the exact dataset (Clinical Audiology) survives intact in the UCI Machine Learning Repository.
- The published benchmark to match is highly specific: 92.3 percent classification accuracy on 26 test cases, retaining exactly 120 cases in memory.
- Reimplementation requires addressing the interactive "learning apprentice" nature of PROTOS, either by simulating human teacher feedback computationally or by hardcoding the final mature semantic network.
- The standing critique of PROTOS, led by pioneers of Instance-Based Learning like David Aha, successfully challenged the necessity of PROTOS's labor-intensive, domain-specific knowledge engineering, paving the way for modern statistical classifiers.

**Introduction to the Audit**
The field of Case-Based Reasoning emerged in the 1980s as a cognitive model and computational paradigm that solves new problems by adapting previously successful solutions to similar problems [cite: 1]. Driven by the early memory theories of Roger Schank and Janet Kolodner, Case-Based Reasoning operates on a foundational four-step cycle: Retrieve, Reuse, Revise, and Retain [cite: 2, 3]. Historical systems such as Kristian Hammond's CHEF (a Szechuan recipe planner) and Ray Bareiss and Bruce Porter's PROTOS (a clinical audiology diagnostic tool) served as the primary proofs-of-concept for this paradigm [cite: 1, 4]. Modern iterations of this architecture survive in extensive software ecosystems like the jCOLIBRI framework [cite: 5, 6]. 

This report narrows its focus to answer a single, highly specific question: Can the classical Case-Based Reasoning system, specifically PROTOS, be reproduced today against a published historical result? Because PROTOS possesses a canonical dataset that survived the decay of early internet archives, a well-documented algorithmic structure, and a highly specific published accuracy metric, it serves as the ideal candidate for a strict reproducibility audit. The following sections trace the surviving artefacts, define the exact benchmark, outline the technical hazards of reproduction, and detail the historical critiques that shaped the legacy of the system.

## PART 1. VERDICT, IN THE FIRST LINE

REPRODUCIBLE_WITH_EFFORT

A faithful reimplementation of the PROTOS system can be rebuilt from the published algorithmic descriptions in the literature, coupled with the surviving clinical audiology dataset. The original Common Lisp codebase is a victim of severe software bit-rot and the death of the Lisp machine ecosystem. However, the theoretical model is completely documented. The effort is bounded to approximately two to three months of work for a competent programmer to write a modern implementation in Python or Common Lisp, script the interactive teacher inputs based on the surviving dataset features, and run the evaluation loop to match the historical benchmark.

## PART 2. THE ARTEFACT TRAIL

The survival of the artefacts associated with the classical Case-Based Reasoning systems varies wildly, ranging from lost academic FTP servers to meticulously preserved modern package managers. 

**PROTOS Source Code**
The original source code for PROTOS was written in Common Lisp and was widely known as CL-Protos [cite: 7]. The implementation was developed by E. Ray Bareiss and Bruce W. Porter at the University of Texas at Austin AI Lab, with engineering contributions from Rita Duran, Dan Dvorak, Jim Kroger, Hilel Swerdlin, and Ben Tso [cite: 7]. In the late 1980s and early 1990s, CL-Protos was officially distributed via anonymous FTP at cs.utexas.edu:/pub/porter/ and mirrored at ftp.cc.utexas.edu:/pub/AI_ATTIC/ (also known as bongo.cc.utexas.edu) [cite: 7, 8]. 

Today, these bare university FTP servers are largely decommissioned or locked behind modern security protocols. The direct, live download of the original CL-Protos tarball from these URLs is UNCONFIRMED without accessing specialized internet antiquarian archives. A search of modern repositories reveals a GitHub project named "cl-protos" (located within https://github.com/smartcontractkit/cre-sdk-go), but an inspection of the commit history indicates this is a naming collision referring to "Chainlink Protobufs" rather than the 1987 Case-Based Reasoning system [cite: 9, 10]. While the literal 1987 code is practically inaccessible to the casual modern programmer, the complete logic, memory architecture, and heuristic weighting formulas were published in exhausting detail in Bareiss's 1989 text and Aha's 1990 dissertation.

**CHEF Source Code**
Kristian Hammond's CHEF (1986) was a pioneering case-based planner [cite: 11, 12]. An instructional, stripped-down version of the code, known as Micro-CHEF, was authored by Hammond and published as a code appendix and companion software to the seminal textbook "Inside Case-Based Reasoning" by Christopher Riesbeck and Roger Schank (1989) [cite: 7, 13, 14]. The Lisp source code for Micro-CHEF was historically hosted at cs.umd.edu:/pub/schank/icbr/ [cite: 7, 8]. Like the Texas FTPs, the Maryland FTP server is no longer a reliable live endpoint, but the physical print copies of "Inside Case-Based Reasoning" preserve the logic. 

**jCOLIBRI Source Code**
In contrast to the historical Lisp systems, the jCOLIBRI framework is actively preserved. Developed by the Group of Artificial Intelligence Applications (GAIA) at Universidad Complutense de Madrid, jCOLIBRI is an object-oriented Java framework for building Case-Based Reasoning systems [cite: 5, 15, 16]. The artefact trail here is flawless: version 3.2 is currently available via Maven Central under the identifier es.ucm.fdi.gaia:jCOLIBRI [cite: 5, 17]. Its dependencies and POM files are intact, and its source directory is mirrored on GitHub at https://github.com/jCoderZ/public.maven.repository/master, with the official project homepage historically maintained at http://gaia.fdi.ucm.es/projects/jcolibri/ [cite: 5, 15, 18]. 

**The Dataset**
The most critical artefact for reproducing PROTOS is the clinical audiology dataset, which survives perfectly. The dataset was originally provided by Professor James Jerger of the Baylor College of Medicine [cite: 19, 20]. It consists of complex patient-reported symptoms, patient history, and routine audiological test results [cite: 19, 21]. This exact dataset was standardized into Boolean attributes and uploaded to the UCI Machine Learning Repository, where it remains available today at https://archive.ics.uci.edu/ml/datasets/audiology [cite: 20, 22]. The preservation of this specific dataset is the sole reason a rigorous quantitative reproduction of PROTOS is possible today.

## PART 3. THE PUBLISHED RESULT TO CHECK AGAINST

To audit a system's reproducibility, there must be a highly specific, quantitative claim in the original literature that a modern replication can be checked against. For PROTOS, this benchmark is explicitly documented in the foundational literature, specifically in Bareiss, Porter, and Wier's 1987 paper "Protos: An Exemplar-Based Learning Apprentice" (Proceedings of the 4th International Workshop on Machine Learning, 12-23) [cite: 20, 23], and it was subsequently verified by independent researchers in the early 1990s [cite: 24].

The specific claims that a reproduction must match are as follows:

1. **The Dataset Split:** The reproduction must use the exact split of 200 training instances and 26 test instances, spread across 24 diagnostic categories of clinical audiology (such as otitis media and malleus fixation) [cite: 1, 24]. The instances must be parsed into an average of 10 Boolean attributes per case [cite: 24].
2. **The Retention Metric:** During the training phase, the Case-Based Reasoning memory model must aggressively prune redundant or subsumed cases. A faithful reproduction of the PROTOS retention heuristic will result in exactly 120 cases retained in the final case library [cite: 24].
3. **The Accuracy Metric:** On the first attempt to classify the 26 unseen test instances, the reproduction must achieve exactly 92.3 percent accuracy. This equates to correctly classifying 24 out of the 26 test instances [cite: 24, 25]. 
4. **The Secondary Attempt Metric:** When the system is directed to attempt a second classification (using the heuristic fallback mechanisms innate to PROTOS), it must correctly classify all 26 test instances, achieving 100 percent accuracy, even without any additional domain knowledge being provided between the first and second attempts [cite: 24].

If a competent programmer builds a category-exemplar semantic network, trains it on the UCI audiology training set, and achieves exactly 24 out of 26 correct on the first pass and 120 retained cases, the historical system has been successfully and faithfully reproduced.

## PART 4. WHAT WOULD BREAK A REPRODUCTION

Re-running the literal 1987 bytes of CL-Protos is virtually impossible without specialized digital archaeology, but even a faithful reimplementation faces severe conceptual and technical hazards that could easily break a reproduction.

**Interactive Human Input (The Learning Apprentice Bottleneck)**
The most significant barrier to reproducing PROTOS is that it was never designed as a passive, batch-processing classifier. PROTOS was a "learning apprentice," meaning it was designed to acquire knowledge by interacting with a human expert during the normal course of problem-solving [cite: 19, 24, 26]. When PROTOS failed to classify a training instance correctly, or when it retrieved an exemplar that did not match the ground truth, the system would halt execution. It would then ask the human teacher to explain the failure [cite: 19, 26]. 

The human expert would provide domain-specific "difference links." For example, if PROTOS confused a case of otitis media with a case of malleus fixation, the human would manually install a heuristic link noting how the two cases functionally differed, or conversely, explain why two seemingly different symptoms provided evidence for the same functional feature [cite: 19]. A modern reproduction running an automated test script would immediately break at this step, waiting for standard input that will never arrive. To reproduce the 92.3 percent accuracy today, the programmer must either simulate the human teacher by writing an oracle script that automatically generates difference links based on the known ground-truth labels in the UCI dataset, or they must bypass the training phase entirely by hardcoding the mature, final semantic network that the original authors extracted. 

**Lisp Machine Primitives and Environment Decay**
If an ambitious archivist managed to extract the original CL-Protos source from a surviving magnetic tape, the code itself would likely break a modern reproduction attempt. CL-Protos was written in early Common Lisp and specifically optimized for the hardware of the era, including Sun3, TI Explorer, HP 9000, and Symbolics Lisp machines [cite: 7]. It was notoriously resource-heavy, described in historical FAQs as a program that "gobbles a huge amount of memory" [cite: 7]. Furthermore, 1980s Lisp implementations frequently relied on proprietary windowing systems, pre-CLOS object orientations, and specialized macros. Running this legacy code on a modern compiler like SBCL would result in a cascade of fatal syntax and primitive-dependency errors.

**The Small Disjuncts Evaluation Rule**
A reproduction could easily fail to match the 120-case retention metric if the programmer does not rigorously follow the original authors' evaluation rules regarding edge cases. In subsequent audits of PROTOS, researchers noted that the system generated many highly specific concept definitions based on incredibly sparse data. Specifically, 21 of the 26 definitions created by PROTOS in the audiology domain were based on 10 or fewer training examples [cite: 27, 28]. These "small disjuncts" are highly sensitive to noise. If a modern reproducer implements standard cross-validation or prunes the dataset using modern statistical outlier detection, they will destroy the fragile heuristic network PROTOS relied on, resulting in a wildly different accuracy metric than the published 92.3 percent.

## PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT

The results published by Bareiss and Porter in 1987 were intensely scrutinized during a pivotal transitional era in Artificial Intelligence. In the late 1980s and early 1990s, the field was shifting away from "knowledge engineering" (where human experts hand-coded rules and semantic networks) toward statistical machine learning (where algorithms computed patterns from raw data without domain-specific semantic understanding). PROTOS became a central battleground for this epistemological debate.

**The Instance-Based Learning Challenge**
The most decisive critique of PROTOS came from David Aha and Dennis Kibler. In their 1987 and 1991 research on Instance-Based Learning, Aha and Kibler directly challenged the core philosophy of PROTOS [cite: 29, 30]. PROTOS relied on an "exemplar-based" approach, which required massive amounts of domain-specific knowledge to compute similarity [cite: 29, 31]. PROTOS explicitly encoded typicality information, featural importances, and causal rules derived from human explanations of category membership [cite: 29, 31]. 

Aha and Kibler argued that this approach suffered from a severe knowledge-acquisition bottleneck. To prove their point, they deployed early versions of Instance-Based Learning algorithms (the precursors to modern k-Nearest Neighbors) against the exact same clinical audiology dataset used by PROTOS. Aha demonstrated that knowledge-lean algorithms, which merely computed statistical distance rather than relying on encoded semantic meaning, could achieve highly competitive accuracy [cite: 24, 29]. By bypassing the need for a human teacher to hold the system's hand and explain the domain, Aha proved that statistical learning was vastly more scalable than classical Case-Based Reasoning for classification tasks.

**The Problem of Small Disjuncts**
Further critique came from Robert Holte, L. Acker, and Bruce Porter (the latter being the co-creator of PROTOS) in their 1989 paper "Concept Learning and the Problem of Small Disjuncts" [cite: 27, 28]. Holte analyzed the rules generated by PROTOS and found that the system had a strong tendency to create "small disjuncts" concept definitions that covered a very small number of training examples [cite: 27]. 

The critique highlighted a vulnerability in the PROTOS methodology: because PROTOS relied on a human teacher to resolve failures, it was prone to overfitting. The system would dutifully retain noisy, irrelevant, or highly idiosyncratic exemplars simply because the teacher forced a difference link to resolve a temporary classification error [cite: 27, 30]. While PROTOS achieved high accuracy on the audiology dataset, it did so by memorizing a highly fragmented rule space.

**Resolution of the Challenge**
The challenge resolved into a field-wide consensus that fundamentally altered the trajectory of AI. PROTOS was historically vindicated as a highly accurate, brilliantly engineered system. Its reliance on domain-specific knowledge made it exceptionally good at explaining its reasoning, which remains a highly desirable trait in medical domains like clinical audiology [cite: 23, 32]. However, the critiques by Aha, Kibler, and Holte were overwhelmingly accepted by the broader community. The necessity of hand-holding an algorithm through difference links was deemed too expensive for general applications [cite: 30]. Consequently, Case-Based Reasoning evolved into niche, high-value domains (like legal reasoning and industrial maintenance), while statistical and Instance-Based methods conquered the broader classification landscape [cite: 32, 33, 34]. 

## PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING

Because PART 1 issued a verdict of REPRODUCIBLE_WITH_EFFORT, this section provides the exact reproduction recipe required to rebuild the classical Case-Based Reasoning cycle of PROTOS and match the published result.

**Reproduction Recipe for PROTOS**

**Target Result to Match:** 
92.3 percent accuracy (24 correct out of 26 test cases) on the first classification attempt, with exactly 120 cases retained in the final memory structure [cite: 24].

**Dataset Preparation:**
1. Download the Standardized Audiology Database from the UCI Machine Learning Repository at https://archive.ics.uci.edu/ml/datasets/audiology [cite: 20].
2. Isolate the two critical files: `audiology.standardized.data` (which contains the 200 training instances) and `audiology.standardized.test` (which contains the 26 test instances) [cite: 20, 24].
3. Parse the data according to the standardized rules published by UCI: convert properties like `age_gt_60` to Boolean attributes (true/false). Crucially, treat missing values (marked as `?` in the dataset) as negative Boolean features, as each Boolean attribute is assumed to be false unless explicitly noted as true [cite: 20, 24].

**Software Architecture (The Python Reimplementation):**
Instead of attempting to compile the 1987 CL-Protos Lisp code, the modern reproducer must write a Python script implementing the "Category-Exemplar" memory model described by Bareiss (1989) [cite: 24, 35]. The script must implement the three core data structures of the PROTOS memory network:
1. **Feature-to-Category Links:** Pointers that connect a specific problem descriptor (e.g., a symptom) to a broad diagnostic category.
2. **Feature-to-Exemplar Links:** Pointers connecting specific symptoms to individual historical cases.
3. **Difference Links:** Explicit relational pointers between two exemplars that note how they differ functionally [cite: 1, 19].

**Simulating the Learning Apprentice:**
To faithfully reproduce the training phase without requiring a human to sit at the terminal, the reproducer must write an automated "Oracle" loop. 
1. The Python PROTOS will process the 200 training cases sequentially.
2. If the system misclassifies a case or retrieves an exemplar that does not match the known ground-truth category in the UCI dataset, the execution pauses.
3. The Oracle script intercepts the pause, compares the attributes of the misclassified target case against the retrieved case, and automatically injects a "difference link" into the semantic network based on the mismatched Boolean features [cite: 19]. 
4. The case is then retained. If a case is classified correctly with high confidence and introduces no novel features, it is pruned to maintain the 120-case retention metric [cite: 24].

**Compute Cost and Parameters:**
The computational cost of this reproduction is entirely trivial on modern hardware. While the original Lisp implementation strained 1980s workstations, a Python reimplementation processing 226 total cases will execute in less than one second on a standard commercial laptop. There are no hyperparameters to tune in the modern statistical sense; rather, the reproducer must strictly enforce the Boolean matching logic and the Oracle's difference-link injection rules as defined in the historical literature. Reproducing this system today acts as a masterclass in the mechanics of classical AI, demonstrating how symbolic logic and human expertise were once synthesized before the statistical revolution.

**Sources:**
1. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoxkX2_DidpCOxv9nK7K1xFLkXWO8S2Fq3XHLqZTLVvALaRX381afurR2bTYKXdhhZ5FnqiNvSjhuF1HgZgESVTSxJHQ7S-8Ew_h9xcXIjSEX2tdsA4RCDpMsAi0N2hxB-7PEHwxqyx6FkIoL80I0ojbCm8POYH8dbGsxZPzqkiScGtw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyV7Y2x67-9bp-S06iOw67loAy4oaTne8FOWvq2Sg4tYXAp_JqUQhkOyqGHmdSZYQdjoX2a6_UCI8BjcDuGbCaoblttyp6JvDo4Ipwucm5topZgHg=)
3. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6zVOoyK9uPmEjnpEBQigfbdLHyWAexo4BpR7CVlUrb4rjckfLYV6d3zGeyWOC7Vhh-BPm1MhNy9HhrjttlLxi9_VDL6yF-cyr2mxJd-vlYakFjQdUHx7e6xPFqGSHT5_EoEConI3Z7TNus5XRzQQmPBMorIvKYu8_WhhtMjSz1lX3Wdk1P7yIQIYM5g2S0ahCFn8=)
4. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc3tSAKqXZboumTxparDQU4e2EI10s5rQ7JhqkQ58HV123LiGsTLHYheXwjCXWfOTdQwSkGWqaQjPdSzLgnbeghOvCS2s-sKfvw0Pyv2mJlp1SnUAayGguCSpX3pld3o3QP80=)
5. [sonatype.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0pbYK2K--vLVxYz3VrJcUpQCXRiUkdaNPmApRhAiDFr6fHtRon4vyv1WyNR3jSJ11VRYas5lM6nEbsJzVkTR3cq4wfuD5bVWp6k_RVEqKVx-_EjTa4bJ2L7rbuQHUxsDzacM1saWOO2lV1xgFe4p2BMDU)
6. [bibbase.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKIJWHZzBf6HWMH-mYfi6MwhUqEt7WRbZvrGWDfA7TmaX0uoRYbeRszR2WzbDPRREO9RC6BVd2120dsQ2H4MtWcNhew36w5a0EOrDLl6Nk5Z1vWLVc9HGnCFV9-a1SLLILB6m_rktziccN51EDCeB_7eid8HYm1M_Icnq7ZuqmoN4X-q5B3j8df4xyoeU_eZIwxKpOU5uw3bDlCjJ-VM6HTGvwX_nw389WMgdvNe1NSSB-B9MI_9XzGZrxZg==)
7. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnkASBpf4NL5ohh1-Uq-jYL_hZr09-mFoJPrdDH0DTKCiWbrKhGuTaEh-CNRo5gq81-Cd1Mb93FRpGjxvzkEB27pnit1ZiZQwdPwXxN2o8GvyQUZxt2QXIRNNjSqjRjLwJA50PcJobZbCLLHAcNTKJeBe0nvP6vzPWSAcc2rk=)
8. [uniba.sk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5tpCCRJ7khR6ym_r08YhqlFnmSSWJPHfCOKC6-dg4vqA4DWq8C8AnIzzNyc0wYbAu4FtTH4VT8ByPwxjPszTQiH8LhMoyReVY4njxVyzU3f6xE_OrFqYry8UB9q50u5mdmDWX-v53RJE=)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5ap2Hpqi7CnyYvw4Pg1z4w5CtHFcqEPWnUAS711VTrN_W8j7vSTcYdJx5hzZjCoowi13QT46JHo4vdmBqlx5VZgnBjzBai0yv9o2UTdE55YkbGuoh8ZQkWLkEpxkfPozbJPQE2XfDI0pqPV4=)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM6N5uGLcosOiLKIIdUADP6f7C3VblLpZdwBTD9FNej-Z00W_DIeMtAao7vkIamdMkYo5BWrgcxurtQzTD6Nr9UOSsfh3Ln-fQwc2d3gSwvJXBwPwYnDF_M0Ex9EVIH-a3aJPhnKZc3hYa3d0Bmt5PG4PSudI=)
11. [csic.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbYtAZSLyTz336eOVzOUUVCkZW46-6UJ6x_RIIKbX2dBec_ZLaZao91D1sW6gVR0Jz3Sqt_RhNhhBCPwkvEfYFdLvlcnPl_xYTOFvfwbHPh9O_rz3yYbs4UXVsYUdoGLBNnQGsmHwa0jXCnqwgLJrV33_wq4f8MOI=)
12. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsse9t8W-G1069zjx87smn9cAUecTM7ywMaGF9E6dRMyJ5zWj0jYmYk6eMnCvTlqkdoLz10LRK8_xb1UFqbnzvxNlrH_COZIiiRM75tcR8rJgjJjQoAvJrUhIUSF3meJObSxZd6uUDsYhBcBL-ipG2Smlv)
13. [emse.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL3kc2V4BqCrrbyD0d9VMWG6tae73gQ9pGyqWUHNnxh_90x6Wo2dUtOaCc-JqlytFMqBSgENmZdlhaoIL-dlbkMcfq5Ij-kq2EPstweZY-B32_IhKgBmJZwSRWPQtYraZ-eTNm-pce1ukVi246TYqNHVyvQA==)
14. [vitalsource.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZjs8IZvUl3gpbdrGX7FYUmyP4jmL112vO845HFgDhVmWXfzPwia4Xs83Mt-yk1YQpKAOhQvXvIQ8JHDh10CfxK--sYPXbvNOGnR3eAmp2DT4q9bilnWrD_ep5TnuhL1v9020f3ZZqhChi8TZtk8YG80nArwnVecjlF1tjk2EsMFLut7GH4TRZCgvQYg6cELOyPw1e3wH09MKX1w==)
15. [mvnrepository.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeIS2GmscURdODiM0jBmunBeQWSgLF6kUjrzmJRzTgJMSVL4sQy4Yw5yCDBiz2QLB_WvmzBet5NY_mdsphpDplJ5Bgascx_5xrk4j6AE3WJ4KhdJJ6pja-FT1sQ8GipGSgFjpw2GOmRCKRb-3OONwjg7ARoQ==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8-iAKIVpazHQfMztzB4tNFWP5tlEZcKJWhwtT2D5L3fYVY_FYL7DNHBuLsKyPbttr5CB__Dibd3KfI474yJ0ZUJ9GXy8S_cJKpEST_4HIQvrLovVZtbGddVzaZO_OyXVlZD7Ymna606VNvzE5Z8tOJf-NqzftMjJzJS6BiZMKfZNKQEjKj8ZIs0BF-fb7FC68Txwe_LFsqcEMhXP-5aTI8Bmi1Yjpdf2iCRy-Z1wKjgcXDKLytNkr4rUtgQ==)
17. [mvnrepository.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7q78fP0cWQKiWBjjzgP2NB2m9Md9HQc6j3afqMqVd1kAeGvxXF-XVsmvM1bVojL9l67G31JfYZCCMz0berUTyE7NKKI587EcOe3kCe588J9s9kNn7UprkkTF798nNB4h7JRcXP8rRsMx5-spoQbhB)
18. [ekstrandom.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZhqXdK2wPeCcGpTRs45FhWPOTAnr3U513pnRbKI9UDTBBSgOWu3t1MpFrcvlgnLeWVF9UXScbE4VHQ6-0YhuS8Dmejzez_21a16PuomcXR5ZXWl40YlJLtQ2KL4oSzw==)
19. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENL2ZZncZbpLTsJsWphddCyUfxA7vGy_CsH3Km2Z9CSIiKLfNXDg4obTXeSggB1ZXVfwPGhTjbYRh5aOePB-7PrFTNOn0U9vWQ_dpn-DKecuobAXBITGeqfUm6d0frUcMdiVSAg5XYeMPj3WFKUw53_X6pQxX48MGa)
20. [openml.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqlANkG0DO4cRSpTbGJHdEvNqZv93dFcnn5O34UuaJ4qyFehq7YPYjLkVsxbYmZ2rEgHg-CdHiLkX4fJAdwCFKmoUMcHSanTB7gUrZt3hkXCTrMUlkDfLHWFefJ9K0btQI)
21. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvivpmSGmFZQlmFCbkDu6VVvukFvDlILyreESIbzABvLPe_Lkc3lYT-A6aM-RlQeyVi8DsBMCEWDt2yCtH6qG61EuVi9JSGK6POY1sYTJu8ADQc5SagbBp_xKCu2kuTrO9V47qFJc=)
22. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6Cjrd0OccK0QSjpyqEqgJUItssAMwKDEDAXBPlSYKAvHCB0-PyE1TwHHdd7DoNY0xY0ff2lvpeDLdNteurKHLCZFFmo86k1Q7HnguwIUDB_i4GLCrK2IcPWYS5oKz0BVKhd0rTm_hH9aoMa9JZMwo)
23. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHni-bPOZzi-u4lzvPl4mGakWbgZTPqfvcMkjRT0obbETe2uQGNqB0qKA_A37oB015RXNwAc_loFi8-HhWoCY3Cqg1NMr1ijfxKbmsZnz3GmwNSAvw3rRLwAZDIPg==)
24. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEo0t5Fi8ch_BH2_rFrcjK2MyfTRgMTNLWAOyJJbCqFyeiENbhWPZEgvbXP-RGX-X1Exc5EJOB8uOUbwjx7xI0tjRsDK2piCmq5jYjxx0mildZV370gme4XQjGnqiB7F2Uk6LBF0X6CUtxHAzWuGPoJajRxN_BBDlvdAp1s1olDw9jSxgP0Q45Hu18b08CJ3UloXBSO6pzQkzI=)
25. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3gOgExD9tdcO9q3snQondTdr0ZNwnWwXzDGODcPTGJmN5ntJyD0NlJV4hle7CyYS34w0uNb-E5bwXfcwZSOzNWYhZwWbajaHSZlxmKsuy4IbY1HYYaorSJxHfGDzxeH6yqT34Lkf3cYob)
26. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgmV1Ac3f7zWjt9sTu1N106q_kD98FW8uFdfqirH0QSEv15IoiNKdseknrs8RTjvtr34S1zKag6H7BkXL2UxLLawbSiwryrt1TBD0L5YiZpYs4nW0X6Vtqhmx-HoJoxFOfG3CsKL3_L2cFCzOe02eBSmUkpfc5)
27. [ualberta.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3qAv-1hCLVwl7cf0mHASvY-lF_oxl1cv3JDdY9_wPoC-fZmsP2kBhG_6m70rVwJdgg8M6nYRM10Vyif0ap0KRYgD5c73KGqLyhJgLPrc9ZGlyccvm9bOa2kCBazsYeenXRmMilYf-W1F4zRhReix6X9C2L7HM-AuMaVE=)
28. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOBCi_8un8AliwzACVsCLK_nGMKiLd9rYzI9cAuNURu7c5GSsazN_IdrBFQkrh7YXIQ1WUNgaor8G_m8tzoHqtS_gM4Q2cMCh6Deob8KE0AlQuELF1YGjD56eplR66futsEFpPBibw1thO2dMkfAksvA==)
29. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq3Tlor47-GAtRHbQPPVljUeMMMWquq5Ir2CIPikmOGwZnoDfwv4BteZ6FGW4rnDVojw2Vl88dA1av5fOk1oRXZzdw-6nZTfvj4x7bQ5nKleaRNTNjFkH-8WAy12BVnDGfjCS0K6Y3RLTFi9Zlvlrn5Kz28kUggooHSk4=)
30. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKkwrhdzH6isAj_Y7V1ayeZFf80NJ56462_0tvVzmfMUofSlLMxBxRZABTXurOjPmfGzG8sh37rf8GjjY8_fP9WfSBkaJY-vwlLCTQ6yjUEVF7KLNmDn5tq16GiIdlS19KrtXAaLc7VFFu)
31. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkD2utXvvC9_rK2Rebeds1RyA3-r1_-UQx8rNxlivK7jVNuOpmADp8xJ3EiXv4JtN0EzmjM5jVbTgkqnOYQuGqGZ6y7wupLmpL79TkhiEWORsfPN1BFTU61QokLv4F2JeggJUcwGdAaWKkjO_oWB8=)
32. [pitt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnyUTEEt_FAdm0hv8DllA_zwBKEbzPxQus9VqV4zSEZtxZ2-obuFouT4EWFfc_IHGIFNTxdy9MaQAThQ8YAstuIVcHMyqS5e_gTeRcfJwpfuIT_4D0yabxvW6aV-JrwmxkrrbQLR03WKrpvhy6idEqqOP8jP7QY54=)
33. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKWNwFn_atQvV6h1EiZ_tItYWxJwsLTcVM49A4f-8S7OU6yvB9uLO8NChc1b33QoAd1bhUchRfIj2FWxAddw0og0rqBSGHYSmqKglHVXFqW2mRLVVtOEWSmks1AbjRu2fsKeiNbrLIA2R3cg49X3b6Sg==)
34. [ntnu.no](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVmQGJBzLXnHvjO3b1lXJrnw1RdMZQAh24BTMtQFKdzZqflQsCoQ4I_sLTTkK-QB2qXO5EKuX8XY5wi0F9WzObzUW1WYq6WnRqRPVhbxadPDsyS1a3-pGL2JcYOpx-aV5RqNBH0EycKQj_awXVMWjkBw==)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExUqNKMED0WOGWsExOqNdpYjt7SdTRx2zD62ZM-T1JUoLjhbBT4gcPbBb_arSLsdLED9n4hNHrf7Dv1F8Yq3wrIDxRhSSlb1haq85Wd7PYWDi8xAeb_hc3guee20_QbqXyLBRMX3q4sU310vsMmDh75p_Q3e-gFpzb7HdpSrDTfXBUAYDCVFMjxf2YzuTQ1_lgHDVg1qh7BIILTauR0V3GVxXo_zMaH0hXB5gYpNA8P4XL36IfY0-aKQBJn_h7KGp7)

