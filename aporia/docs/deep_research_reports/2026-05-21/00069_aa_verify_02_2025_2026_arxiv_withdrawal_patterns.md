# AA-VERIFY-02: 2025-2026 arXiv withdrawal patterns

**Pythia queue id:** 69
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZ1T3NPYXBmcEg3Mm8xTWtQenVMTU9REhZ1T3NPYXBmcEg3Mm8xTWtQenVMTU9R
**Elapsed:** 626s
**Completed at:** 2026-05-21T11:36:11.914927+00:00

---

# Statistical Patterns in arXiv Mathematics Withdrawals (2025-2026): An In-Depth Analysis

**Key Points:**
*   Research suggests that the tracking of arXiv withdrawals has vastly improved with the introduction of comprehensive databases like WithdrarXiv, which cataloged over 14,000 retracted preprints.
*   It appears that specific mathematics sub-fields, particularly Differential Geometry (math.DG) and Combinatorics (math.CO), exhibit higher relative retraction rates compared to massive fields like artificial intelligence, despite having lower absolute withdrawal counts.
*   The evidence leans toward factual and methodological errors—such as calculation mistakes and gaps in mathematical proofs—accounting for the vast majority of preprint withdrawals, eclipsing issues like plagiarism.
*   While an exact, aggregated "average time-to-withdrawal" is not explicitly defined in the current major datasets, researchers note that the lifespan of a withdrawn paper can vary wildly, with extreme cases showing retractions occurring decades after initial submission.

**Understanding Preprint Withdrawals**
In the fast-paced world of scientific research, preprint servers like arXiv allow scientists and mathematicians to share their findings before they undergo formal peer review. Because these papers are shared early, they sometimes contain mistakes. When authors discover a critical error, they can "withdraw" the paper, leaving a note explaining why. Analyzing these withdrawals helps the academic community understand common pitfalls in research and improve the ways we verify complex information. 

**The Shift Toward Automated Tracking**
Recently, researchers have begun systematically tracking these withdrawn papers using large-scale databases. By using advanced artificial intelligence to read the withdrawal notes left by authors, scientists have categorized the most common reasons for failure. This new wave of tracking not only highlights which fields are most prone to specific errors but also opens the door to creating AI tools that might one day catch these errors before a paper is even published.

**The Landscape of Mathematical Errors**
Mathematics is a field built on absolute rigor, yet it is not immune to human error. The recent data reveals that when math papers are withdrawn, it is rarely due to academic misconduct. Instead, authors typically pull their work down because they found a fatal flaw in a proof, realized their calculations were incorrect, or discovered that someone else had already published the same theorem. This transparent self-correction process is a hallmark of the mathematical community's dedication to truth.

***

## Introduction: The Maturation of Preprint Infrastructure and Quality Control

The dissemination of scientific knowledge has undergone a radical transformation over the past three decades, heavily driven by the advent of preprint servers. Since its inception in 1991, arXiv has served as a foundational pillar for the fields of physics, astronomy, computer science, and mathematics [cite: 1, 2]. By the end of 2021, the repository had surpassed two million hosted articles, and as of late 2024, it was accepting approximately 24,000 new submissions per month [cite: 2]. In many sub-disciplines of mathematics, it has become the standard practice for researchers to self-archive their manuscripts on arXiv prior to submitting them to formal peer-reviewed journals [cite: 2]. 

However, the circumvention of traditional, pre-publication peer review inherently shifts the burden of validation from a closed panel of experts to the broader scientific community. Consequently, the platform allows for the versioning and eventual withdrawal of manuscripts when errors, overlaps, or incomplete results are identified post-upload [cite: 3, 4]. A withdrawal on arXiv leaves the prior versions accessible (often marked with a specific version number, such as "v1") but appends a notice—frequently written by the authors themselves—explaining the rationale for the retraction [cite: 3, 5]. 

Historically, systematic studies of these retractions in STEM fields—particularly in mathematics and computer science—have been exceedingly rare compared to the biomedical sciences [cite: 4, 6]. This landscape changed significantly around 2024 and 2025 with the introduction of large-scale, structured datasets aimed at categorizing and analyzing the lifecycle of withdrawn preprints. This report provides an exhaustive academic overview of the statistical patterns surrounding arXiv withdrawals, focusing primarily on the mathematics domain in the 2025-2026 context. It examines the advent of recent withdrawal-trackers, detailed counts and rates per subject category, the temporal dynamics of time-to-withdrawal, and the dominant failure modes that necessitate the retraction of mathematical literature.

## The Advent of Modern Withdrawal Trackers: WithdrarXiv

To understand the statistical patterns of arXiv withdrawals, researchers in 2024 and 2025 have relied heavily on a pioneering dataset known as **WithdrarXiv** [cite: 1, 4]. Developed by a collaborative team including Delip Rao, Jonathan Young, Thomas Dietterich, and Chris Callison-Burch, WithdrarXiv represents the first comprehensive, large-scale dataset of withdrawn papers from the arXiv repository [cite: 4, 7]. The database aggregates over 14,000 papers and their associated retraction comments, covering the entire history of arXiv up through September 2024 [cite: 4, 6]. 

### Methodology of the Tracker
The creation of the WithdrarXiv tracker involved several sophisticated data harvesting and cleaning techniques. The researchers worked directly with arXiv.org to compile a list of 16,460 withdrawn article IDs [cite: 4, 6]. Because arXiv allows for multiple versions of a paper, approximately 11% of these identifiers represented different versions of the same core manuscript [cite: 4]. 

To protect author privacy and adhere to ethical data release practices, the developers utilized natural language processing (NLP) techniques to scrub personally identifiable information (PII) from the retraction comments. Specifically, they employed a Python package named `scrubadubdub` to replace sensitive data with generic placeholders such as `[RETRACTED_NAME]` and `[RETRACTED_EMAIL]` [cite: 4, 6]. 

### Taxonomy and Categorization
A core contribution of the WithdrarXiv tracker is its structured taxonomy of retraction reasons. By utilizing a text embedding model and K-means clustering, the researchers mapped the free-form natural language withdrawal comments into 10 distinct categories [cite: 6]. Following this, they utilized a zero-shot categorization prompt with the GPT-4 large language model (LLM) to classify the comments, achieving a highly accurate weighted average F1-score of roughly 0.96 [cite: 4, 6]. 

Furthermore, the developers released an enriched subset of the data called **WithdrarXiv-SciFy** [cite: 7, 8]. This subset includes scripts designed to parse full-text PDFs specifically to facilitate ongoing research into automated scientific claim verification, theorem proving, and structural error detection [cite: 6, 8]. The availability of WithdrarXiv-SciFy has directly fueled subsequent research in 2025 and 2026, wherein teams have benchmarked AI systems on their ability to autonomously detect the very errors that led to these historical withdrawals [cite: 9, 10].

## Statistical Patterns: Counts and Rates per Subject Category in Mathematics

When analyzing the distribution of withdrawn preprints, absolute counts can be misleading due to the vastly different submission volumes across scientific disciplines. Computer Science fields, particularly those related to Artificial Intelligence such as Computer Vision (`cs.CV`), Machine Learning (`cs.LG`), and Computation and Language (`cs.CL`), dominate arXiv in terms of sheer submission numbers [cite: 4, 7]. Consequently, they also exhibit the highest absolute counts of withdrawn papers [cite: 4, 7]. 

However, when normalizing these absolute counts by the total number of submissions within a given category, a distinct and critical pattern emerges regarding the field of mathematics. The WithdrarXiv analysis explicitly identified that while AI-related fields experience more retractions in absolute terms, certain mathematics sub-fields face notably higher *relative frequencies* (rates) of retraction [cite: 4].

### High-Risk Mathematical Sub-fields
The analysis of the WithdrarXiv dataset highlights that multiple mathematical categories are present in the top 10 arXiv subject categories for highest retraction counts [cite: 4]. The categories specifically flagged for their systematic challenges in research validation include:
*   **math.DG** (Differential Geometry)
*   **math.CO** (Combinatorics)
*   **math.AP** (Analysis of PDEs)
*   **math.NT** (Number Theory)
*   **math.AG** (Algebraic Geometry) [cite: 4]

The discrepancies in withdrawal *rates* are particularly striking. For instance, the AI categories `cs.CV` and `cs.LG` demonstrated retraction rates of 1.5% and 1.3%, respectively [cite: 4, 7]. In stark contrast, mathematical sub-fields exhibited much higher percentages:
*   **math.DG (Differential Geometry)** showed a remarkably high retraction rate of **8.0%** [cite: 4, 7].
*   **math.CO (Combinatorics)** exhibited a retraction rate of **4.7%** [cite: 4, 7].

### Interpreting the Mathematical Retraction Rates
The presence of multiple pure and applied mathematics categories among the most highly retracted fields points to the unique difficulties inherent in validating mathematical research. Unlike empirical sciences, where a faulty experimental setup might be masked by stochastic data, mathematics relies on deterministic logic. A single flaw in a lemma or a missed boundary condition can instantly invalidate an entire theorem. 

The high rate of withdrawals in `math.DG` and `math.CO` suggests that the peer review process—whether informal via community scrutiny on arXiv, or formal prior to journal publication—remains highly effective at eventually identifying fatal flaws [cite: 4, 7]. The mathematical community's culture of rigorous proof-checking leads authors to rapidly utilize arXiv's withdrawal feature once an error is pointed out by colleagues, contributing to the higher relative rates of retraction observed in the data.

## The Temporal Dimension: Average Time-to-Withdrawal

A critical dimension of retraction studies is understanding the temporal dynamics: how long does a flawed paper persist in the academic ecosystem before it is identified and withdrawn? 

### Limitations in Aggregate Temporal Data
Currently, explicit statistical aggregates regarding the "average time-to-withdrawal" (e.g., a specific mean or median number of days or years across the 14,000+ papers) are marked as strictly unavailable in the primary WithdrarXiv dataset analyses published thus far [cite: 4]. The foundational paper by Rao et al. (2024) establishing the WithdrarXiv database explicitly consigns the study of "Temporal Analysis"—investigating how withdrawal patterns and durations have evolved over time—to future work [cite: 4]. Similarly, while there are models predicting time-to-withdrawal in other contexts (such as patient dropouts in clinical trials or student attrition in education), comprehensive macro-level temporal metrics for arXiv mathematics preprints have not been definitively aggregated [cite: 11, 12].

### Case Studies and Variance
Despite the lack of an aggregated average, qualitative evidence and notable case studies indicate that the time-to-withdrawal for mathematical preprints is characterized by extreme variance. While some papers are withdrawn within days or weeks of upload—often when an eagle-eyed reader spots an immediate error in a proof—others can persist for decades.

A high-profile example illustrating this extreme variance occurred in late 2022. Boris Shoikhet, a mathematician affiliated with the University of Antwerp, formally withdrew a manuscript titled "Lifting formulas, Moyal product, and Feigin spectral sequence" from the arXiv repository [cite: 5]. The paper had been originally submitted to arXiv's `math.QA` (Quantum Algebra) category on October 28, 1998 [cite: 5]. It was withdrawn exactly 24 years later, with Shoikhet citing "a crucial mistake in the arguments" [cite: 5]. 

This 24-year gap, while highly unusual, underscores a vital characteristic of the arXiv ecosystem: the repository serves as a permanent, living archive. An arXiv withdrawal functions similarly to a formal journal retraction in that it alerts readers to fundamental issues, yet all prior versions remain securely online and timestamped without the platform itself actively policing the validity of aging, un-published preprints [cite: 5]. Because preprints are essentially immortalized, errors discovered years later during subsequent research can and do prompt delayed withdrawals.

## Common Failure Modes in Mathematics Preprints

The taxonomy developed by the WithdrarXiv creators provides unprecedented clarity into *why* authors retract their preprints. A comparative analysis shows that arXiv withdrawal patterns differ fundamentally from traditional journal retractions. In traditional biomedical journals, issues related to academic misconduct—such as plagiarism, data falsification, or image manipulation—frequently drive retractions [cite: 4, 13]. On arXiv, however, retractions due to plagiarism (136 cases) and policy violations (134 cases) are exceedingly rare, accounting for less than 1% of the database each [cite: 4, 7]. 

Instead, the vast majority of arXiv withdrawals stem from honest mistakes, premature uploads, or conflicts with prior art. The taxonomy highlights three dominant failure modes.

### 1. Factual, Methodological, and Critical Errors (~40%)
The single largest category of preprint withdrawals is defined as "factual/methodological/other critical errors in manuscript." This category accounts for **6,018 cases**, representing roughly 37% to 40% of all categorized withdrawals in the dataset [cite: 4, 6, 7]. 

In the realm of mathematics and closely aligned theoretical fields, this broad category manifests in several highly specific failure modes:
*   **Gaps in Mathematical Arguments / Errors in Proofs:** This is perhaps the most quintessential mathematical failure mode. Authors routinely withdraw papers after a peer (or the authors themselves) discovers a logical gap that cannot be easily bridged, rendering a theorem or lemma invalid [cite: 4, 7]. The withdrawal notes in these cases are often characterized by transparent admissions of failure, with one cited example stating, "This paper is withdrawn due to a fatal mistake… I am ashamed to have written this paper" [cite: 3].
*   **Computation and Numerical Errors:** In fields relying on applied mathematics, physics, and computer science, researchers often discover miscalculations in specific equations, constants, or algorithmic implementations that fundamentally alter the concluding results [cite: 4].
*   **Conceptual Misconceptions:** These occur when researchers misunderstand theoretical foundations, misinterpret a primary source, or base their proofs on unverified assumptions [cite: 4].

### 2. Incomplete Exposition and Work in Progress (~19%)
The second most frequent reason for withdrawal relates to the premature dissemination of research. The WithdrarXiv dataset flags **3,143 cases** (approximately 19%) where a paper was withdrawn because it was "incomplete exposition or more work in progress" [cite: 4, 7]. 

In mathematics, researchers may upload a preprint claiming a major result (such as a proof for a famous conjecture) before all corollaries are fully written out or verified. If the mathematical community demands rigorous clarification that the authors are not immediately prepared to provide, the authors may withdraw the "v1" manuscript to avoid disseminating unfinished or potentially misleading claims, intending to resubmit once the work is finalized [cite: 1, 4].

### 3. Prior Art and Subsumption by Other Publications
The issue of novelty and overlapping literature is a major driver of withdrawals. This failure mode takes two primary forms:
*   **Subsumption:** The dataset categorizes **2,843 cases** where a preprint was withdrawn because it was "subsumed by another publication" [cite: 4, 7]. Often, authors will merge an arXiv preprint into a broader, more comprehensive study, and withdraw the original preprint to avoid self-plagiarism or to consolidate the academic record [cite: 1, 4].
*   **Discovery of Prior Art:** A significant, albeit slightly smaller, portion of papers are withdrawn because the authors independently arrived at a result, only to discover that the theorem had already been proven. A study of withdrawn arXiv preprints noted that approximately 2.5% were retracted specifically because the main results already appeared in prior literature [cite: 14]. For example, mathematical papers by Popescu-Pampu (2007), Zhang (2012), and Shahryari (2020) were all historically withdrawn after the authors were made aware that their main theorems had been previously established by others [cite: 14]. Authors generally self-identify these preprints as "not novel" upon learning of the prior art [cite: 4].

## The Role of Large Language Models in Error Detection (2025-2026)

The release of the WithdrarXiv database and its PDF-enriched counterpart, WithdrarXiv-SciFy, has catalyzed an entirely new sub-field in AI research during 2025 and 2026: the use of Large Language Models (LLMs) for automated peer review and mathematical error detection. 

Given the high volume of mathematical and scientific output, relying solely on human peer review has led to a widely acknowledged "peer review crisis" characterized by delayed publication times and overburdened reviewers [cite: 9, 15]. Consequently, computer scientists have begun benchmarking the ability of advanced AI models (such as GPT-4o, Claude 3.5, and OpenAI's o3) to identify the fatal errors that led to historical arXiv withdrawals.

### Methodological Benchmarks: The "LLM-as-Judge"
In early 2026, researchers like Zhang and Abernethy, as well as a concurrent study by Son et al., utilized the WithdrarXiv dataset to evaluate whether LLMs could reliably spot critical flaws in scientific manuscripts [cite: 9, 10, 16]. These studies typically operate by feeding the full text (or LaTeX source code) of a known, withdrawn paper into an LLM and asking it to identify methodological or mathematical errors. The model's output is then compared against the actual retraction reason provided by the original human authors [cite: 16, 17].

The findings of these 2025-2026 studies reveal both the promise and the severe limitations of current AI in mathematical verification:
*   **Performance Ceilings:** While LLMs excel at processing text, they struggle significantly with complex mathematical reasoning. Son et al. (2025/2026) evaluated LLMs on a highly curated subset of papers paired with confirmed scientific errors. They found that even the most advanced reasoning model (OpenAI o3) identified only 21.1% of the fatal errors, and did so with an abysmal precision rate of just 6.1% [cite: 10]. 
*   **The Problem of Nuance:** Zhang and Abernethy noted that retraction notes on arXiv can sometimes be ambiguous (e.g., stating "withdrawn due to a crucial error in Lemma 2" without explaining the exact nature of the mathematical failure) [cite: 16]. This ambiguity makes it difficult to train AI models to recognize deeply embedded structural flaws in mathematical logic.
*   **Information Loss:** Attempts to parse mathematical papers into formats readable by LLMs often result in information loss. Researchers observed that when converting PDFs to Markdown or analyzing raw LaTeX, models occasionally missed context that a human mathematician would grasp intuitively. Interestingly, the performance of models like Gemini decreased when forced to read raw LaTeX compared to natural language, likely due to tokenization issues with mathematical syntax [cite: 9].

Ultimately, these 2025-2026 studies conclude that while LLMs can serve as preliminary "quality checkers" to surface potential issues, they cannot replace the domain expertise of human mathematicians [cite: 9, 10]. The task of tracing a subtle gap in a complex combinatorial proof or spotting a minor but fatal error in a differential geometry equation remains, for now, an "irreducibly human" endeavor [cite: 10].

## Conclusion

The statistical landscape of arXiv mathematics withdrawals from 2025-2026 provides a profound window into the self-correcting mechanisms of the scientific method. The advent of sophisticated withdrawal-trackers like WithdrarXiv has quantified what many in the mathematical community have long understood qualitatively: that mathematics is highly vulnerable to subtle, fatal errors, necessitating a vigilant and responsive culture of retraction.

The data unequivocally shows that fields like Differential Geometry (`math.DG`) and Combinatorics (`math.CO`) experience disproportionately high withdrawal rates (8.0% and 4.7%, respectively) compared to the massive submission volumes seen in computer science [cite: 4, 7]. The vast majority of these retractions (approximately 40%) are born not of malice or misconduct, but of factual, methodological, and computational errors—gaps in proofs and flawed logic that are caught by peers or the authors themselves [cite: 4, 13]. 

While the precise aggregate time-to-withdrawal remains an area for future temporal analysis [cite: 4], the historical record proves that mathematical validation is a continuous, open-ended process, with some errors remaining hidden for decades before being corrected [cite: 5]. As the academic community continues to grapple with increasing publication volumes, the integration of AI and LLM-based verification tools holds promise. Yet, as recent studies using the WithdrarXiv dataset demonstrate, the ultimate responsibility for ensuring the absolute rigor of mathematical proofs relies entirely on human expertise and the transparent, open-access infrastructure of preprint servers.

**Sources:**
1. [fapesp.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBvzWZBy_qX4OQ-qMmYzOAXmjyXSZ-m_UoEWfQGH4Cp5BbgBy745TGBcfIkh_XHDfyyJTGosMXCd3XlUjTKmldAcn4TZgyMWdSLcuLR1dWzaMNbbEM5Zp6qsoJjFUK73DMANU_ki6VgNbSsQc=)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFrvHpxH5SXaSgeEO0D-XQV3ePeOpIZ04928KIEeakM98OA2Y7VrLaiNeF7I9EA50f93gA2DHTyZcnu61iNQdo-uy7RqxByYZ_MtBOhli6z3-tdej1MDRn)
3. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLa2uUpaVrypOYclcXYHZeUissWejjCogFMIBRq8wTOet70pte78Y77zkior00cYsz0glKvzECejcCQWSwe10xI9AWnkO8Y6CvO2-1DxiOWkujLrtY_Q6UL3GsQ0JUodwlY6GX0N_MyCq_1bQFzHh7D7FyiJM=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAnWfJdUd9W8VfpSu5SQtDhyvcUbY9pM-Vf88vUAT-PeMmYKaNbkA53w4R74ndZFiXK5fcEfn07EKAGNepKC7TqD8bLrBtFKGwEGkfX4A5IExFop7unBfS)
5. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnzAYwuKqLDYsBRy7oI6TyRMdeN2FsEC8Eyo_YoVTPIrQ5D0GeyzIPnJ60D2PgmFyQh_XhJRMBMx78FJoXvDQyZz4BNSO20-NAuEL3nQsS3kQyj5XqeSepLTf6v-c1vcP-5yJ11FdVaje4y2ZINo68u9CQCC3gVoaj-v-t-U6SmSFIvwmJ6PwxtEcom2Es1tQB-bz9h5i9Wr1EpaOFq8w=)
6. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEZf_ohh0cL5nipfXKWIyubeIkSWY3jQb21Pr6MQhVbpYfPAvSvdxxquROvy0ff7j3eWr402azm3h-qV2GpInFLT_26ubdzZO9VGgL5uKtJQBW_qJfIMYUvUzZh4UxDn_m2iZ8m7aiqGwv-_ylYMwepG6OsyWtY2t5pXpMHriQzq9Nsje19arnrFzwr7aEQDuA)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaj0YISX5AVnKSFGLE1NIW_s_Ne5N1yFVKzVAap0DzcOtJxN_rbtGQeJOdL3JY34MY0xU98n2AMoFWpcdM9TOGa5zqHuHW8hTYxpEX9byq-yZQKiu7)
8. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRez_hiUKXKrBSX1Y9Mqlz8v3L0xVU45UwKSoapWpNN16ecQ0WHhfVRC5EdQJjZcGCy8dRzegqkSmTxwOTrnOb9Dcs5D3gV3-xyUVM2Df4-3VDZrO6eCywZ-QUk6v-Why1FVABpK5OIVlG)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHXAUfnwGvn5JL8YfM16QuqJURZqTq77JW7PocXzs_LE5QRvdjgiMc6E6kSkqcCC29HGwnkeQ93wjzL_Tutf5rwHTZXT9Ct43ptnIx7eXV52rnOhD8eWg_)
10. [netlify.app](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0tf2Lu8-epyr9s-dWvcyM_3mrJZ20pV3sS4IxdyGwqgIdpVmL1Z1CehJkXN3rKlZh0DLwXu6nB5XOQDU2P2hS7AUjsxAyF0gBuJevH7QvD7qYSCNfUweszDgUhLlq)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHknGi-eD9Axs8fzRvd1zZl__xDU6fwpg9x08svRigEI5_dAcUa65023Sdz5OOFSXmUsSQ4VJ6rqoAHdqDguc6Nj5M0laEBmURDPRVNf04G9bZ_f9o-xhW6LuOInz5fwMyOtST5jhc8s59gpNM9FcWVv7rNdtYYdjBtmaNDHQ8UDd-z5IYNQ6t8HekdGTC9StmfviavBqQEv0RPZeof5eBWO7NdyG6ro8VI3bSZ25OT2OwCiZX5bvjcHrLVPytesVkFx4qLe9xdgjsd0XeEpbxzoD7YAUlzlPnxQUsG52onKCFsgCZKc1tdut5pX7_h9_MT7qWrMQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw2rkReRPmIwQlZhf4uxQebIh_HnIkVJvjLvI3HrQtBh15TjpZxe6eqYTU1KoUE0-UnGJj44411oi_sexAT-cvdoA0mnc6izbPBpEUbfcSA9O-HMtYzWCt)
13. [nrf.re.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEINgvF-GDfJko7G5QRD7n-DwhZ5_TiCwPPiqpuyr6KgVMrk5P47hj0yEhEHHQvbvuqAmSjtcrtZ1kkwVO_D98P8pTIpX5gqJlsQ7A7Jk80BRAn_c2CBikMn3NzHAWdYEY6_omJoQq0b4kv94=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrM-Zd41RFTPdKz3QIZJi0MFTH5e_I4uKmq3x-v18KuCFjduQI2uiY1J_UNKHA8KOPuybT9Z-MM7DiAfUp8zFmnkl18iOsvQ88ZeyLMouuCdAY2Jyd_u5U)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-fAqG569rrLzW9UyoNSZeNEQOMqD7mPfuTQv8D0-FXgyU4kA-gYgfYKJtB6vg_Kpw4O2lGPRdzfBlEVUxorYbvyVCvJaporVXjNg0bY-e2KerXA6extp4)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl_8odXXQLCUELSLb2dj6SOQ48QY-bcoAuvyBHrbXxMcG8ktE3sQbE856gHZYFv3uw_itiQGEeq0FH0BeSGR_HwJUAJzuTKOjwyRkZjroqh6TQR1AXCCca)
17. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKZqRe57Qr1BZj1EwpSQDwLeLbzykl1XT9s1F1ElCTJtEaNyLwvvHO53Czg9BJ1_1-z3qc_2aQVXiJ__T0oouv2W125SjRcJI8sZW3BLoJ7TRjbCN1Yd_69CnyHEo=)

