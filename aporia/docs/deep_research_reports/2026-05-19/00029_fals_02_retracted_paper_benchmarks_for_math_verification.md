# FALS-02: Retracted-paper benchmarks for math verification

**Pythia queue id:** 29
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhU29NYXJlUU1PV0tfdU1QcHZXbWtRdxIXYVNvTWFyZVFNT1dLX3VNUHB2V21rUXc
**Elapsed:** 317s
**Completed at:** 2026-05-19T09:21:43.229944+00:00

---

# The State of ML Benchmarks for Detecting Mathematical Errors in Retracted Literature (2024-2026)

### Key Points
*   **Emerging Evaluation Frameworks:** Between 2024 and 2026, researchers have developed specific benchmarks—most notably the **SPOT** dataset and the **AI Correctness Checker** framework—to evaluate how well Large Language Models (LLMs) can detect mathematical and methodological errors in published and subsequently retracted or corrected literature.
*   **Current Model Limitations:** Evidence suggests that while frontier AI models perform well on standardized math tests, they struggle significantly to locate authentic errors in full-length scientific manuscripts. State-of-the-art models like OpenAI's o3 currently achieve only about 21% recall and 6% precision on complex real-world retraction datasets.
*   **Rising Error Rates:** Large-scale automated analyses indicate that the average number of objective mathematical and formatting mistakes in top-tier AI conference papers has grown steadily, highlighting the urgent need for automated verification tools.
*   **Domain Representation Gaps:** While areas like Combinatorics and Number Theory are heavily represented in current evaluation datasets due to their computational nature, highly abstract fields like Algebraic Topology remain severely underrepresented in automated mathematical verification benchmarks.
*   **Evolving Publishing Policies:** In response to the influx of AI-generated content and potential errors, major preprint servers like arXiv have begun implementing strict penalties, including one-year bans, for authors submitting papers with incontrovertible, unchecked AI-generated mathematical or citation errors.

### Executive Summary for a General Audience
The rapid advancement of artificial intelligence has sparked interest in using AI as an "automated peer reviewer" to help scientists catch mathematical errors before or after publication. Recently, the scientific community has faced a growing number of paper retractions—instances where published research is withdrawn due to critical flaws or misconduct. To determine if AI can assist in cleaning up the scientific record, researchers between 2024 and 2026 created specific tests, or "benchmarks," to see if AI models can spot the exact mathematical mistakes that led to real-world retractions. 

Research suggests that while AI is getting very good at solving textbook math problems, finding a subtle mathematical error hidden inside a 40-page research paper is incredibly difficult. Benchmarks using data from RetractionWatch, the arXiv preprint server, and post-publication forums like PubPeer reveal that current AI systems miss the vast majority of real-world errors and frequently flag correct math as incorrect. Furthermore, there is a significant imbalance in the types of math tested. AI systems are frequently evaluated on "Number Theory" and "Combinatorics" (which often involve concrete numbers and algorithms), but they are rarely tested on highly abstract fields like "Algebraic Topology." As AI becomes more common in research, publishers are actively adapting their policies to manage the risks and benefits of these powerful new tools.

---

## 1. Introduction: The Intersection of Retracted Literature and ML Verification

The scientific publishing ecosystem is currently navigating a period of unprecedented volume and complexity. Between 2024 and 2026, the volume of submissions to major scientific venues has surged; for example, the International Conference on Learning Representations (ICLR) saw submissions rise from roughly 7,000 in 2024 to nearly 20,000 in 2026 [cite: 1]. Consequently, the peer review system is under immense strain, leading to an increase in published papers that contain undetected objective errors [cite: 1, 2]. Substantial human effort is continuously devoted to identifying these mistakes post-publication, relying on the vigilance of independent researchers and platforms like PubPeer and RetractionWatch to document concerns and track retractions [cite: 3].

Simultaneously, the capabilities of Large Language Models (LLMs) and Multimodal Large Language Models (MLLMs) in complex mathematical reasoning have advanced significantly [cite: 4, 5]. This has catalyzed a new research vector: deploying LLMs not just as generative co-authors, but as automated academic verifiers capable of retrospectively auditing published literature for mathematical and methodological flaws [cite: 2, 6]. However, evaluating an ML system's ability to detect errors requires rigorous benchmarks. Standard math benchmarks traditionally measure a model's ability to *solve* a problem to a correct final answer (e.g., GSM8K, MATH-500) rather than its ability to *detect* a logical or mathematical error within a lengthy, human-authored proof [cite: 5, 7]. 

To bridge this gap, the period of 2024–2026 has seen the introduction of specialized benchmarks that leverage retracted papers, arXiv withdrawals, and journal-level errata to test ML error-detection capabilities in real-world contexts [cite: 6, 8]. This report exhaustively details these benchmarks, analyzes the methodologies used to curate retracted mathematical data, and identifies the remaining gaps in domain-specific coverage across Number Theory (NT), Algebraic Geometry (AG), Combinatorics (CO), and Algebraic Topology (AT).

## 2. Dedicated Benchmarks for Error Detection in Published and Retracted Papers

The evaluation of ML systems for mathematical error detection has bifurcated into two primary approaches: identifying objective mistakes in newly published (and historically published) literature at scale, and testing models against carefully curated datasets of known retractions and errata.

### 2.1 The SPOT Benchmark (Scientific Paper Error Detection)
Introduced in May 2025, **SPOT** represents the most direct and comprehensive benchmark addressing the AI-assisted verification of scientific manuscripts based on retracted and corrected literature [cite: 6, 9]. Recognizing that prior benchmarks focused heavily on sentence-level fact checks or noisy peer-review feedback, the creators of SPOT designed a dataset that extends verification to the full complexity of frontier-level scientific research [cite: 6, 8].

#### Methodology and Curation Pipeline
The SPOT benchmark was constructed using a rigorous five-stage data curation pipeline to ensure the errors were authentic, critical, and free from data contamination:
1.  **Seed Collection:** Researchers sourced manuscripts from two major repositories: **WithdrarXiv** (a large-scale dataset of over 14,000 withdrawn papers from arXiv and their associated retraction comments) and **PubPeer** (an anonymous post-publication peer-review forum) [cite: 8, 10]. The data was filtered to extract entries explicitly annotated as containing factual, methodological, or other critical errors (such as mathematical mistakes and figure duplications) [cite: 6].
2.  **Automated Filtering:** Utilizing GPT-4o (specifically the August 2024 version), the dataset underwent filtering to isolate comment-manuscript pairs that unambiguously pinpointed a specific section, equation, table, or figure. This reduced the pool to 1,855 WithdrarXiv and 25,378 PubPeer samples [cite: 8]. Crucially, to avoid contamination with the parametric knowledge of models trained up to 2024, the dataset was strictly filtered to include only papers published *after* 2024, yielding 58 WithdrarXiv and 215 PubPeer samples [cite: 6, 8].
3.  **Error Validation by Original Authors:** The benchmark prioritized incontrovertible ground truth by retaining only manuscripts where the original authors directly confirmed the error. For PubPeer, this meant requiring an explicit author response acknowledging the mathematical or methodological mistake. For WithdrarXiv, self-retractions were treated as definitive evidence of a critical error [cite: 6].
4.  **Human Sanity Check:** Domain experts conducted manual reviews to verify that the acknowledged error remained visible in the archived PDF, documenting a concise description, extracting the verbatim author acknowledgment, and classifying the error type and severity (proxied by whether it resulted in an erratum or a full retraction) [cite: 6].
5.  **Normalization:** To prevent the conflation of LLM reasoning failures with upstream OCR parsing failures, PDFs were converted into Markdown using Llama-Parse3, capturing high-fidelity screenshots of equations and figures [cite: 11]. 

#### Benchmark Composition and ML Performance
The final SPOT benchmark comprises 83 published manuscripts containing 91 annotated errors. Of these errors, 59 were addressed via errata, while 32 were severe enough to lead to full retractions [cite: 6]. Retractions were found to be highly concentrated in equation and proof cases [cite: 11]. The manuscripts span 10 scientific fields and possess massive multimodal contexts, ranging from 1,000 to 46,000 tokens and including up to 80 figures [cite: 11].

When state-of-the-art LLMs were evaluated on SPOT, the results highlighted a severe deficiency in current ML capabilities regarding error detection. The most capable model, OpenAI's o3, achieved a maximum recall of 21.1% and a precision of just 6.1% [cite: 6]. All other tested models scored near zero [cite: 8]. Furthermore, confidence estimates from the models were uniformly low, and across eight independent runs, the models rarely rediscovered the same errors, severely undermining their reliability as automated mathematical auditors [cite: 9]. Domain experts noted that even the strongest models hallucinated errors that resembled student-level misconceptions rather than genuine mathematical critiques [cite: 9, 12].

### 2.2 The "To Err Is Human" AI Checker Dataset
While SPOT evaluates ML models against a ground-truth dataset of known retractions, a complementary approach introduced in December 2025 by Bianchi, Kwon, et al. utilizes frontier LLMs to proactively audit thousands of peer-reviewed papers for objective mathematical errors [cite: 2, 13].

#### Systematic Quantification of Errors
The researchers developed an "AI Correctness Checker" powered by GPT-5 to systematically identify objective mistakes in 2,500 randomly sampled papers published across top-tier machine learning venues: NeurIPS (2021–2025), ICLR (2018–2025), and TMLR (2022–2025) [cite: 2, 3]. The system focused strictly on objective mistakes with a verifiable ground truth—specifically errors in formulas, mathematical derivations, calculations, and tables—intentionally excluding subjective aspects like novelty or writing quality [cite: 13, 14].

#### Findings on Published Mathematical Errors
The automated audit revealed that published AI papers contain a substantial and growing number of objective mistakes. The average number of mistakes per paper increased significantly over time:
*   **NeurIPS:** Increased from 3.8 mistakes per paper in 2021 to 5.9 in 2025 (a 55.3% increase) [cite: 2].
*   **ICLR:** Rose from 4.1 in 2018 to 5.2 in 2025 (a 27% increase) [cite: 2].
*   **TMLR:** Climbed from 5.0 in 2022-2023 to 5.5 in 2025 [cite: 3].

Overall, 99.2% of the 2,500 papers contained at least one mistake flagged by the AI Checker [cite: 14]. Crucially, the most common issues detected were **mathematical mistakes (54.0%)**, which included incorrect formulas, invalid derivations, and logical flaws in proofs or algorithmic reasoning [cite: 2, 3]. Other error categories included text errors (31.4%), table/figure inconsistencies (9.3%), and cross-reference errors (5.3%) [cite: 2]. Furthermore, a significant portion of these papers (23.8% in ICLR, 30.8% in NeurIPS, and 36.0% in TMLR) contained at least one "potentially substantive mistake" that could alter the interpretation of the findings, invalidate a proof, or impede reproducibility [cite: 2].

#### AI Checker Precision and Recall
To validate the AI Checker as a benchmarking tool itself, human experts manually examined 316 potential mistakes flagged by the system across 60 randomly selected papers. The experts confirmed that 263 were genuine mistakes, yielding a precision of 83.2% for the AI Checker [cite: 2, 14]. In a controlled recall analysis—where 90 mathematical and textual errors were intentionally injected into published papers—the AI Checker achieved an overall recall of 60.0% [cite: 2, 3]. Notably, the model detected Math/Formula mistakes most reliably (66.7% recall), indicating that frontier LLMs are more effective at parsing structured mathematical expressions for errors than identifying mistakes embedded in narrative text (55.9% recall) [cite: 2, 3]. The AI Checker was also able to propose correct fixes for 75.8% of the identified mistakes [cite: 13].

### 2.3 RetractionWatch and OpenAlex Machine Learning Datasets
Beyond detecting the specific mathematical logic flaw within a paper, ML benchmarks have also been developed to predict the *likelihood* of retraction based on bibliometric and metadata features. In June 2025, Fletcher and Stevenson published an open-access dataset combining information from the **RetractionWatch** database and the **OpenAlex** API [cite: 15, 16]. 

#### Retraction Prediction Models
The RetractionWatch database has become a foundational resource for scientific integrity, documenting tens of thousands of retractions and their causes (e.g., mathematical errors, image manipulation, fabricated data) [cite: 17]. Through a collaboration with Crossref, the dataset—comprising over 64,000 articles—was made publicly accessible via an API [cite: 17, 18]. 

Fletcher and Stevenson utilized this data, restricting their analysis to retractions between the years 2000 and 2020 (as the median post-publication time to retraction is roughly 1.8 years, and this period predates the mass proliferation of generative AI) [cite: 16, 19]. Using a case-controlled design, they paired retracted research articles with non-retracted articles published in the same period [cite: 15, 19]. The study trained traditional feature-based classifiers alongside modern contextual language models to predict retractions. 

The results showed that the **Llama 3.2 base model** achieved the highest overall accuracy, reaching a precision of 0.683 for identifying retracted articles [cite: 15, 16]. Traditional feature-based models like the Random Forest classifier achieved a precision of 0.687 for identifying non-retracted articles [cite: 16]. While no single model excelled across all metrics, the benchmark established a foundation for developing automated tools to flag potentially problematic publications for human reviewers, acting as a triage step before deep mathematical auditing is required [cite: 15, 19].

#### Survival Analysis of Retracted Citations
Complementary research utilizing RetractionWatch and OpenAlex data has analyzed the "Time to Correction" for retracted paper citations. Using Accelerated Failure Time (AFT) models, researchers in late 2025 observed that a paper's established scholarly authority (i.e., a higher academic citation count) is paradoxically associated with a *slower* time to correction when the paper is ultimately retracted [cite: 20]. This highlights a critical socio-technical vulnerability in the scientific ecosystem: highly cited mathematical or scientific papers that are later found to contain errors propagate those errors more deeply into the literature, underscoring the need for ML systems that can swiftly detect these flaws prior to massive citation accumulation [cite: 20].

### 2.4 The WithdrarXiv Repository
As established by the creators of SPOT, the **WithdrarXiv** repository serves as a vital dataset for analyzing mathematical and scientific errors [cite: 8]. Containing over 14,000 papers withdrawn from arXiv alongside their associated retraction comments up to September 2024, it provides a comprehensive taxonomy of retraction reasons [cite: 10]. A significant finding from analyzing this dataset is that many papers are withdrawn due to overlapping results; a study of over 14,000 withdrawn preprints found that 2.5% were retracted because the authors' mathematical results had already appeared in prior literature [cite: 21, 22]. The availability of WithdrarXiv has enabled AI researchers to tap into a rich vein of "negative data"—authentic mathematical failures, self-corrections, and retractions—which is essential for training LLMs to recognize flawed reasoning [cite: 8].

## 3. The Value of "Failure Data" in Training ML Reviewers

A critical insight emerging from the 2024-2026 literature is that LLMs are disproportionately trained on "positive" data—successful proofs, published papers, and accepted theorems. This creates a distributional collapse when models are tasked with acting as peer reviewers or error detectors [cite: 1].

Research published in April 2026 articulated this "data crisis." Because frontier models have consumed most available high-quality text, and training predominantly on positive-result literature gives the model a distorted view of science, LLMs lack the structural understanding of how mathematical proofs or scientific experiments *fail* [cite: 1]. The peer review system is straining, with 21% of 75,800 peer reviews at ICLR 2026 flagged as entirely AI-generated [cite: 1]. Furthermore, papers have been found containing hidden prompts designed to manipulate LLM reviewers into giving favorable scores [cite: 1]. 

To combat this, researchers hypothesize that exposure to structured failure data—such as the WithdrarXiv dataset, RetractionWatch, and databases of failed clinical trials—would significantly improve the ability of ML reviewers to detect methodological errors and implausible mathematical claims [cite: 1]. If LLMs are fed only successful mathematical proofs (as found in standard training corpora), they are prone to "conformity bias" or hallucinating correctness when evaluating an inherently flawed proof. Providing access to a corpus of retracted mathematical papers serves not only as a benchmark but as an essential training resource for next-generation automated verification systems [cite: 1, 8].

## 4. Contextualizing Advanced Mathematics Benchmarks

While SPOT and the AI Checker directly analyze published and retracted literature, assessing the exact gaps in ML's mathematical capabilities requires looking at the broader landscape of research-level math benchmarks introduced in 2024–2026. These benchmarks map out the frontier of what ML can solve, which heavily dictates what it can *verify* for errors.

### 4.1 FrontierMath and MathConstruct
**FrontierMath**, introduced in late 2024 and updated through 2026, is a benchmark of 350 original, exceptionally challenging mathematics problems crafted by over 60 expert mathematicians, including Fields Medalists [cite: 23, 24]. The benchmark is divided into four tiers, with Tier 4 representing unsolved or research-level mathematics requiring hours or days for human specialists to solve [cite: 25]. The questions cover most major branches of modern mathematics, from computationally intensive problems in Number Theory to abstract questions in Algebraic Geometry and Category Theory [cite: 23, 26]. 

Similarly, **MathConstruct** challenges LLM reasoning with constructive proofs, evaluating advanced theorem generation and procedural mathematics [cite: 26, 27]. The performance of ML models on these datasets is illuminating. Initially, leading models solved less than 2% of FrontierMath problems, highlighting a massive gap in complex mathematical reasoning [cite: 23, 26]. By mid-2026, state-of-the-art models like GPT-5.4 advanced to a score of 47.6% across the dataset [cite: 28]. However, this evaluation relies on the model generating a final, verifiably correct answer (often via an embedded Python execution environment) [cite: 29]. Generating a correct answer from scratch is computationally distinct from identifying a subtle logical flaw in a 20-page human-authored topology paper, explaining why models might score 47% on FrontierMath but only 6% precision on the SPOT retraction benchmark [cite: 6, 28].

### 4.2 RealMath
**RealMath**, introduced in May 2025, derives its benchmark directly from research papers (arXiv) and mathematical forums (Math StackExchange) [cite: 30, 31]. It automatically extracts verifiable mathematical statements and theorems from real research environments [cite: 30]. RealMath addresses data contamination by serving as a continually refreshable data collection pipeline [cite: 30]. Interestingly, frontier models demonstrated surprisingly strong capabilities on RealMath, achieving accuracy rates of 43–49% on `Math.arXiv` papers and up to 70% on `Math.StackExchange` questions [cite: 30, 31]. 

However, fine-tuning models on RealMath samples did not lead to subsequent improvements in accuracy, suggesting that the difficulty stems from a genuine lack of specialized mathematical knowledge rather than the format of the questions [cite: 32, 33]. RealMath's extensive categorization of theorems also provides a highly detailed map of which mathematical domains are heavily tested and which remain neglected [cite: 32].

### 4.3 Student Error Detection Benchmarks (ErrorRadar and MathAgent)
It is also worth noting that error detection benchmarks exist at the K-12 and undergraduate levels. **ErrorRadar** (2024/2025) and **MathAgent** (2025) focus on multimodal mathematical error detection in student solutions [cite: 34, 35]. These frameworks require the ML system to perform "error step identification" and "error categorization" [cite: 35]. For instance, MathAgent utilizes a Mixture-of-Math-Agent framework with specialized agents (image-text consistency validator, visual semantic interpreter, and integrative error analyzer) to identify exactly where a student's reasoning went wrong [cite: 35]. 

While highly effective in educational settings (achieving near 90% student satisfaction by replacing manual error detection), these benchmarks focus on elementary algebra and geometry [cite: 35, 36]. The meta-reasoning required to spot a procedural slip in a high school algebra problem differs exponentially from identifying a false assumption in an advanced asymptotic methods paper (such as those featured in the **HARDMATH** benchmark for graduate-level applied mathematics) [cite: 37, 38]. Research confirms that even when provided with the correct reference solution, LLMs struggle with "meta-reasoning"—the active evaluation of another entity's logic to find the first error step [cite: 39].

## 5. Coverage Gaps by Mathematical Domain (NT, AG, CO, AT)

A critical component of evaluating ML systems is understanding the distribution of the data they are tested on. An exhaustive analysis of 9.2 million mathematical theorems extracted from arXiv in 2026, combined with the domain breakdowns of datasets like RealMath, provides a precise map of coverage and gaps across four specific mathematical domains: Number Theory (NT), Algebraic Geometry (AG), Combinatorics (CO), and Algebraic Topology (AT) [cite: 21, 40].

### 5.1 Combinatorics (math.CO)
**Coverage:** Highly Represented.
Combinatorics is exceptionally well-covered in current ML mathematical benchmarks. In the 9.2 million theorem dataset parsed from arXiv, `math.CO` accounts for **727,514 theorems** (the third highest of any mathematical discipline) across 46,929 primary papers [cite: 21, 22]. 
**Analysis:** In the RealMath dataset, Combinatorics comprises more than 20% of the entire dataset size [cite: 27, 32]. The heavy representation of Combinatorics in benchmarks like MathConstruct, FrontierMath, and RealMath stems from the nature of the field: combinatorial problems frequently involve discrete structures, constructive proofs, and algorithmic derivations that often result in a fixed, verifiable numerical or symbolic answer [cite: 23, 32]. Because these answers can be objectively validated via scripts or programmatic execution (e.g., Python environments used by LLMs), ML models can be efficiently benchmarked on combinatorial error detection [cite: 29].

### 5.2 Number Theory (math.NT)
**Coverage:** Highly Represented.
Number Theory is similarly ubiquitous in ML benchmarks. The arXiv extraction dataset identified **550,466 theorems** in `math.NT` across 32,235 primary papers [cite: 21, 22].
**Analysis:** Like Combinatorics, Number Theory constitutes more than 20% of the RealMath benchmark dataset [cite: 27, 32]. Computational number theory is heavily featured in FrontierMath [cite: 23]. ML performance in this domain is generally robust; for instance, the AI Correctness Checker evaluating RealMath achieved over 60% accuracy in Number Theory [cite: 31]. The high volume of papers, the dense concentration of theorems per paper, and the fact that many number theory theorems are constructive and computational make it an ideal domain for current automated error detection frameworks [cite: 32].

### 5.3 Algebraic Geometry (math.AG)
**Coverage:** Moderately to Highly Represented in raw data, but challenging for verification.
Algebraic Geometry boasts the highest raw volume of theorems among the queried domains. The arXiv dataset mapped **761,230 theorems** in `math.AG` across 36,350 primary papers [cite: 21, 22]. 
**Analysis:** Despite the massive corpus of available literature, Algebraic Geometry presents unique challenges for ML error detection. While it is featured in FrontierMath [cite: 23], the field is highly abstract, dealing with schemes, sheaves, and cohomological constructs that do not easily reduce to computationally verifiable strings or Python-executable code [cite: 41]. Consequently, while there is no shortage of published (or retracted) papers in AG, formatting these papers into a benchmark that allows an LLM to reliably pinpoint a non-computational, conceptual error remains an ongoing challenge for dataset curators [cite: 23].

### 5.4 Algebraic Topology (math.AT)
**Coverage:** Severe Gap.
Algebraic Topology is significantly underrepresented in mathematical ML benchmarks. In the arXiv theorem dataset, `math.AT` accounts for only **200,267 theorems** across 8,886 primary papers [cite: 21, 40]. 
**Analysis:** This represents a volume roughly one-third to one-fourth the size of Combinatorics or Algebraic Geometry [cite: 22]. The gap in coverage is not merely a product of lower publication volume; it is a structural limitation of current ML benchmarking methodologies. Algebraic Topology involves advanced generalized cohomology theories, higher category theory, homotopy groups, and spectral sequences [cite: 41]. Proofs in this domain are deeply functorial and diagrammatic, relying heavily on commutative diagrams and qualitative abstract reasoning that are notoriously difficult to serialize into Markdown or LaTeX for LLM parsing without loss of semantic meaning. Because benchmarks prioritize "objective mistakes" with a clearly verifiable ground truth (such as an incorrect formula or miscalculated table) [cite: 2, 13], the deeply conceptual errors that might lead to a retraction in a `math.AT` paper fall outside the scope of current automated correctness checkers. As a result, Algebraic Topology remains a major gap in the coverage of ML error-detection capabilities.

### Domain Summary Table
Based on the 2026 semantic search analysis of 9.2 million mathematical theorems from arXiv [cite: 21, 22]:

| arXiv Tag | Subject Area | Total Theorems (All cross-lists) | Total Papers (Primary) | Benchmark Coverage Status |
| :--- | :--- | :--- | :--- | :--- |
| `math.AG` | Algebraic Geometry | 1,097,654 | 36,350 | High volume, but high abstraction limits verifiable benchmarking. |
| `math.CO` | Combinatorics | 1,107,979 | 46,929 | Highly covered (>20% of standard datasets); very suitable for ML. |
| `math.NT` | Number Theory | 752,812 | 32,235 | Highly covered (>20% of standard datasets); high model accuracy. |
| `math.AT` | Algebraic Topology| 348,076 | 8,886 | **Major Gap**; low volume and extremely difficult to evaluate automatically. |

*(Note: "Total Theorems" includes papers where the domain is cross-listed, while "Total Papers" denotes the count where the domain is the primary tag [cite: 21, 22].)*

## 6. Systemic Consequences and Publishing Policy Interventions (2026)

The development of benchmarks to detect errors is occurring against a backdrop of increasing anxiety regarding AI's role in scientific publishing. The very tools being developed to *detect* errors are also being used to *generate* them [cite: 1, 42].

### Real-World Retractions Due to Mathematical Errors
Historical and contemporary examples demonstrate that basic mathematical errors frequently slip through human peer review. For example, in 2016, a physics paper critiquing Bell's theorem was quietly removed by an Elsevier journal after experts pointed out "elementary mathematical errors" and self-contradictions that the peer reviewers had missed [cite: 43]. Similarly, in the social sciences, prominent criminology papers were retracted after inquiries found routine but highly consequential mathematical and coding errors in the binary standard deviations of the datasets [cite: 44]. In an era of AI-generated content, the rate of these "routine" mathematical errors being injected into the literature is accelerating [cite: 2].

### The arXiv One-Year Ban Policy (May 2026)
In response to the proliferation of LLM-generated errors, preprint servers are taking aggressive regulatory steps. On May 15, 2026, Thomas G. Dietterich (head of the Computer Science section at arXiv) announced a strict new policy regarding AI generation [cite: 42]. The policy states that authors take full responsibility for all contents of their submission, irrespective of how the contents were generated [cite: 45]. 

Crucially, if a submission contains "incontrovertible evidence that the authors did not check the results of LLM generation"—such as hallucinated mathematical results, fabricated references, or meta-comments left in the text (e.g., *"Here is a 200 word summary, would you like me to make any changes?"* or *"This table is illustrative, fill it in with the real numbers"*), the authors will face severe penalties [cite: 42, 45]. The penalty is a **1-year ban from submitting to arXiv**, followed by a requirement that any subsequent submissions must first be accepted at a reputable peer-reviewed venue [cite: 45]. This policy underscores the urgency of developing highly reliable, automated ML verifiers that can flag these errors before they pollute the preprint ecosystem and trigger punitive actions against researchers [cite: 42].

## 7. Conclusion

Between 2024 and 2026, the scientific community has made significant strides in defining and benchmarking the ability of ML systems to detect mathematical errors in published and retracted literature. The introduction of benchmarks like **SPOT** and the **AI Correctness Checker** reveals a dual reality: while frontier models are highly adept at solving isolated, computational math problems (as seen in FrontierMath and RealMath), they remain fundamentally unreliable at auditing lengthy, complex, multimodal research papers for genuine errors [cite: 2, 6, 23]. With state-of-the-art recall hovering around 21% on actual retraction datasets, human peer review remains indispensable [cite: 6, 8].

Furthermore, the landscape of automated error detection is highly uneven. Computational fields like Combinatorics and Number Theory dominate the benchmark datasets, providing an inflated sense of ML capabilities, while deeply abstract fields like Algebraic Topology are left in a blind spot [cite: 21, 32]. 

As the volume of scientific publications continues to grow—compounded by the ease of LLM-assisted drafting—the pressure on the peer-review system will only intensify. Ensuring the integrity of the scientific record will require not just better generative models, but dedicated efforts to train ML reviewers on diverse, domain-spanning "failure datasets" composed of retractions, withdrawals, and known mathematical errors [cite: 1]. Until then, as evidenced by recent arXiv policy changes, the ultimate responsibility for mathematical correctness remains firmly with the human author [cite: 45].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm9bOI25XuVN8DJlXZWZ4aBh4dxKUJvunRbRas-_q3Dg6roDKiXZvIjhu98SKaOJ4M2FLtX5zXN5QkqDvWOQORraJcg-uOOVvBaURmlhe5j4k6WhecyUUaWg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5OSDx1j7oJiZq1xPW_tdyPEpOceJEq9kVM_lWahQ-csmz8qnx9U1eTHPcRq0V6_1XcX86hGgvS2P2er-mkNeb5z14-oKBEqYOIA8IjP53ck_11AcDDM1kJA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE70rNwLyRnR6-4OKra5sVTi2ztKWf1meEIQsY3Ns1JXMqMhUnPJFD1djDw4Uxd09A7y514DIFFlaHgB5zhHu11SncM98MbhGtOcsaSDfeG12lwhba6kQ==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHN29eqUsXn2znrO6Tqg8u7kk8F_XVuzxazdwL3KmEo-pMSKZqz0-3Z0NWXvs6eZ4nEMtRg8gW9q7a9rjYv2_e0JES8g7-hyueQv86F2aHQeGs8Ayyd8ckew==)
5. [artificialanalysis.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4LeTioXbai6e6IJdmSdD-SZm4zN5S7rCb6eXvczS5_rxL7vObSlt5HtMKEIe5TZVnsYfWWCwHa_OZCYWA0uS-p-QBwKYr90r5D4LWGVgOzB1q4AdjazhyBFafmfRdk4H8Bl6PDkCK3w==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXD9nxun6iv8eOVahSffKhEXdhz_WtVUj9QuU0xL1nRTh9kL7ZLh8EU3BNNxAbdWpkQ6JC57ccwGYTFD0ZKK0WO8Haea-RgO0BUjoshAkyvzj0JAuhRg==)
7. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKWmilVFud6HaD2WLgumEkq_0W1cxy6-VocVL0btb33QOQ7fPHgA81ALaUHDwLVYXtvkAgZfS0ODl5skYYXEd1oBbq-ZckVOCvEss1nAw4C7UT2py0rmcB-yYkKUfrEe0XFKjdCwrfuCSG6Ipkx7nZ7gK5MWc2Yu4DjxWaY5SNVDcpIRIiaxf4_MSr7JCalwr0pPX2mXHDOX7BSbMApZQ0pzyX3gHknByqwgD0yPeSQvDiWdk2f9HRgxo=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0eYDWF8dZTv8YW8DiAtATl5J1D5imdaq3wM6qGJNxrye_YNQMFkztkjPFKH75cxC7tuZ9bfEaa_EF7AQK80gZhpn9a0YnXI_3aXd5P5yj4fpghnmn7A-zkQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi9ditRbsOt-n0ZEMzSu3hufPq6kuHERjw99jVgFVt1ppwRtLaq7XudU_1yI6nR4oJ5Y_u7YZ2ZY2zR8mCO9X5Ti2a4ywiDs4I81G1NZlPwMaN44dpuw==)
10. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1rVi7Konwhxis_hvXWl9FLW-FiOio3BWIQnoI3F26eZlI6AwBfMMLiapXW338Wdl8cOXulqphHxbtIYYpb77r44u7M5VQaXZRQjNSpWPn1SnWh00kYS_sRVUo10p53LL3aF-hGLWaErxvG9GhD18ITuQtPg3jvdz4NPDhySMObSMfp0lMP5ZqrelL9_F8I6wmgjyLQIalcG0lvEoaMccyR0NX2eaR-_oddZtFwmnGGAZ4Q7xr7xx2wt-lj1ejJs6RcLP9)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsq-1O07TwrzZ0a5N1GTpvZun8wwIbv3cZ_rCpjl1BKM74BMzQcaXOsDvSobD8M6ByXdW7WDJ7bP7sc-UWdTmtItDrz6G-kQm8BFrzdCv48NKDkF6aGtH3dk_XUgCy)
12. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAiv7EB4wzUrac4TxTP7FPh1b2FJYqNrO7B65u2LPiLvAa4uIhHac0u_dTe8OcT96HZ5sMv0Ga4f-h6sOMP3zMrVvSzwebhqbNAAeLNL8LgCoXU8BxUeiU6uJNFSQ=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnwhb_q7CmUIlhvzNm29y4qLGVbwFD_Esgl4JsuZUtKNLCSfIAWgCqMfsr3RvROSvbPqwzRATG2SWPglVR-5e1lIeS00L0Uv_yIkOcVYPMXEDcpSczwg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY02ScMp3F5G2VAZj7H8tip_nkNDqBZrCBjH3YKqqck0Qd7u6qhQ-IYwcwnoSykEm4SHgb1aafV_FYGxR9Ixp2NNWQ2rinHdAAZqu2eu-cVm1AtSB-uuQ6_DJYMDKPY7xCb4EVJBxGe79dN1xVcrGH7aoPC5CgqTevo80PmDWu7Mi8THF4F5aXl-E0eVjJptCv7pGb91FVyKgfuguR9lPLYMAIlohghFLU7fOwSbybmJ8_yqFx36d-nGzrjznQkImIaT6qvg==)
15. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCNdhwS870WlO67BeqLva_4R7o-n2eDMI64rbhk__kN0H-zKU2Dj1iRuC7gnapKpbEMtFta64ozKdYZ6-R78wW2wO5e_1ARp1UbHuH-nZUkvthQjcb-_Z5OAawGL0CxA==)
16. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFW-HLAuaTwxrLSc-Ea0AQuOpOqy7l8sM2ByaQtNS3a1Q-PB4AqywFedCr-5dOKbBO_C4AZBVTnWKEN-v6yVs4EFSWaqkY3_Rl7vQYWLFXR9GOzJriFfjv6Dw6SwUbgGwDRFYKXGhHk6A==)
17. [hkust.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMUek5dQ4wStzFsdsumGz9B2bZH4x-h3uNfUbFUa2ECT9xWwYpVM3TV_jyQC9lxZBDbV_A8mQS6IGWN5ZoLIjcFXUTVvJNj7vH5vknUXuIXJAnEfCih2rXx4woKTQ7SH1zISHoLag6vAdtGoJHzr1wf98C7S5l6oat55jwhQ9jGbi3wpyLRhsDqMkT2HNFwvMNOl8Iz8UUgXTnTB_kAe0d2qlNX_wqPLY6QQ==)
18. [peerreviewcongress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG977fBoBh62yluMJMbrmeuBUmG_s_rRKiXleDEAvRFFEfaqnRM98R1D3PBeJwbbFOE-rXM3sCCcbSqT2dG0LvAQCthlG-OjKIkL6g6jDpxZU7Mgg4PGyApNcdOJiJ-LlMusXXHnWcvshW9aTdzp0BLj6Y2cwf2KQMN4JGtivMwLfmFnzHXF2vonFJ0zc0JtVoZDEr-a0=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjbeceNZsjUjqSyn5bDQI9of7Ar2MYBlNqI8lt9xN6rJa1BXpvLPTdy5ZI7RiDd7TdD8Dshp9Ck4RITNuZFii4QbmgC1TvJeq-jyHy1HJ9O1ZO3upIrKQqH4g8dyFOCRzuZ01Ih0UhkVgTvWJfuX3_06W8gsKLqiJvUh99qF3WgHt3eq2SG8_lEHrUSlo_u07DT0eHF5XC-94sIiWdaBWwH32AEjaneMeX35QZDP-lRA==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH01cVSS4o9x6AB5Bx6G22GsBcLtWLQ0pvO_JtYQ3ZGirUl-So4i9tM-50L-2HSNvCFNNuw940BMnNScstkmT7Sws6RT_dOdD543ST2jqcoPix2zq4PydSBdw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjcjwEj4SCHe8QXjatA6DSA2BQXyrtMOkeByWEtqN0UhSpgfyOflNv1YC_Xgd7hlYt9MeAZ7MwvdfXj07GPSWhESqQmAPma8psX4O1sQvN527E8KQZcKo-PA==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH90wmjhCDzlRWQc6g6t1v_T_J80fUeeC3FtAyHsZl2HslR47PDN164Arm5cb8cyU4qXoAUZHWDhVHvFkS7nHtv0EeFRsZ0I1Vy8vAn5gPVj0785270MunmuA==)
23. [lesswrong.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEv1lVtCBYIZbpVQ_-qDaReuR_on9zKzFB9WCDjV8LWI2gks7M-OeCW_uKkdD4uSYhjrWGuPFTagQuV1ansfGKISKZnQPKGXJzNB9nJgQsNn-e5N7TeW_Hb0zpWBBgUXeyj6FEATtFalgnaIArDyznfz2emPnKML-sbs9inI8kiHXh2nhKXXNWKHHDtBLEFk6QS0exf8O_Ckw==)
24. [epoch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERhC6Z2Dd3CNuE1tipPSW8is3pmG0nAbq0YizITherDvQnGFh6_PloSPB9EtGIcSm-V-UH63hBnhFUfv8KxfjLQOZfKexyrVleBESdRqUJqAxokMa-umUFgddDrGQNTrginB26Fg==)
25. [epoch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFp59spbG3Gb-aSrEyj2WmBYtA6cLHALT7nND0d7KhxHCo7OgTpGuTi8hkWgMJo51pHzCgg2eA366T1S9uhGVZJ_AhzYWjjvSa3sfh0g42kcwl__w==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1uG47zpS04XuV2Z9JXLpw_dh0qQC2D1yjGQ2ZJCRFvlyV8KOGogpBMkxe687pOLDTBLjOCF5uVcIX9qdPp54Qg5HtLqOaPCwKCuESRH89NHCdnR2ATAsIOO2DJM9ZVTjZ5xInrTe7JiNjAmmsed1dKb8B-6nnmZkAdzJQDeyIYstUua_GgcfoU8TICXcEJPBrB0jCmboIalx2fA8ZHXMzjtstGQ==)
27. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTazD2P-mPTGq0PHvfGqpyp0Xw2sP_GqpYfFwkInlNOkBKYUzWp092hb2vXRKuf20vq9fCx6TMHtyVegRRcsZ50pIUGCS7SdXAazqHJNH4RFdbBZsZDWwF8r7bJOZr)
28. [llm-stats.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDzZRmdspt9BVFdwZDlG301-MLz1SwKmd9q6Sl-uD3Kk5mHIKhVp1uLDGHHUznsAMGqerT6jyiKxG0vw-SuG_wM0_hY_lzc8AL7IJo6dvThym4brwWEMRE9pcRkE7WKfOPdMs=)
29. [ourworldindata.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEow37TC1Vifk6tRW-p4JOEFLT3eitmlpPeg6WWW1trI1WpGM8xpdYra0mLZZks0FK8dJ26Fyqp_KCxEqibI-wWIrjxnUQ3Tybvd-04L7K78tjAzTmVGks-QNhek3IQUier6U9uZZ8cRi4oC2d2-XtsYc=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpZ5MiJ_5QKqh0N29vnz3GIAfZYPeL5VCTJ4DUfAc4qBuZAxmcZXkFR9WCx5eU-BciuFBGZjMB6u9eaeIOcg1uc1PVnXkYHFW4Z2kxlf2pytUkel05WmDEVw==)
31. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ4ESMAJZoqdogN3g3Jt3Sh5fX0iJk6mb4JGSRCoO5m8SXH3JoXjhVn92_xlBd7ZsrXU0dLssRlw03di2aqnAPsVVAf7p4zbF4KE_0Im5X8h_x9mOnjMd4OukAlWDXGRARJGU=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3TdB0YHMfQeguzoTFCZrPPGCrBrfWGNgy4GaSoP8Byll968bokBclsnPbx2Aye7MIK-dk2_Izg-ceGV1C-AZPrIs0glhuWsh4-c_CYRW-38ltKS6XvtoJgg==)
33. [csdn.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqp3jmMmXms5iqmLkeV7_b6-K0j2s3dEUwqs72cCIxtf1BOJ894qtnVDlnzxjisTvR70VOlWvxSPRiFJ1qoq1maUTKwfQPw4pYyNmuVTyP8U9qqqpyk6bLNZeZFAURyBqYCil9kLVfIuyEkmfq3QQ=)
34. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnsz2BSVbK7nk0aMsf2ZwqonaoYa3_MSGgm26va12em2BdB3S52Ur2FqgMqP-bVVuuAtoIVLVV-w0-zBfAcuxTwBBvQwEktN_oeTUs9Ece8vnw_Xwui-KwvbDGz3DrD8Y=)
35. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo7DDytFRsiE4dDtFQNQVU9y2j_NorqHdFX_JCB-IQIoCwpa1Lk74zbf-Ekin6EVRYSDzrSEpos-f2pA_0B4Td1q2-UmKpeCy_yAgQzzwn0gFrPQ-XHAF_8sAXtubC5nFaWePF71w=)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYWmpe7Gin4G0UGwBPwDX64b9CLvCNrbCP42ykGYA0GhEQ_e1bhTn1zbHNy4ixEK82WSi9_mpQNOSAWZ8tRUs6kRWnMuCHPjt35cDQlCgv5ykfIPTOw_73ug==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyMk2IsPqGp7FgRj2_R_ynkKoJ3yh1F7_hGmRzSiaRyCvIMEnY6fYR8ohk_vXAcdx096Gs9DYL93L8GQ2yUJ9zceOHMsbc1R5I2Py1yioVTQPbfH7pBA==)
38. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7AqwNEZypLx_ZmyFJN1Z3dTKKT2h5QzQw8yQSBwG24nosIwvpHpIp9tNAUOpwjK_P6YmURzU8Yr0rb1IifXlolj_hNUCWCf0QAkkZZEYazsssTLwAbLxHDSrlgMdqPla6WeQnzQv1B9F9IZ_ootGQIMJr3Qse13zepV-D76xkVcnPJ-OyjgRTsMnq0VVUeiR5qRo0IvSE2BdUegTcepkTKAfQ88WaQLw-ngbwDWEMeUvzqfJXNbLLvaaXCw==)
39. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_ocRYS9P8z_K0ZSb3dV4he4115UAH9KDET84rdIrlmatPOFiSQsiwJleF-MazN5pKMnuYlK7gr1XidpVqe7BV1mefI_1ZyP5q3qVAPazTsnz2iaM4U_Vy5534Xt__YkQ5RHuDCBI=)
40. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtnxKT9rJhUZwMb3PVHFtjDepMGimpms8A-YiE68rrmvPZcNpRmMuBnbAhteN_FqOFa_Q19zHJ5kwAA6N-CUQqSyzx7CTv9aqJoz1GTq82zhFXaU020dfmO9ISk1A72IkZyTPC_zVQWA4hhjGeRbnumsmsZ6iSKu1cIa_FgtZMWVLJImXYBYU6pWAFDTpI3Hbpb4sq1cqJIMCbdqeV)
41. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpMtYfE_I_SftG-_N79gQPJN4cdY-fr7re3qy3ZE0wdOIG3cgA0CGDJqIUgdPGcM4NGbb6pHrOi_vNVeGHmxPUazBzskSiaWx2ThejpqW-FX7zHybYu8i0HBJ3uZvhIFVY4Fv58R2LkLHriOY_ObUIJVAjwjrdMiv9-_qXe0zUfVo=)
42. [gigazine.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM1fBpfbZvmhGsuaaxvPCMXCEaUA5DEpGcGoGrX4aKJGOHDUVs50viI4BPQrKmnjqrUrMvNU7wTdRVmTrAabmvguCDAnlYvdX-OFepuaWESFkk3Id5vQwP20iaDlwBoGnWZcRtk-CywTKPgPuGRbzRgzoKB2P4)
43. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRAKbwxQnVRpQkz61jt6KW607edIBE7oZyEdyTsBjTE4B9YvqWBmMWRquijpaALNrfj_RpWNxMIzikKhxNV9JjwqDY74JZuhnBvmZJagWgijBBt6sHXOdinYmZRib2VqFy7aXvam6KCq35rAUzKkQkDmFoaFPLNnLBEm28r3KQbNTQlJSKIDNPYfLbkwbQZLKeeGB74ruGxjwnMA-6bl0K3ojeMBi8hQ==)
44. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgzSjFXw72rWzExLqhKeD0q5jzE3YGlgRoL-aVTcxfzM0MhDhQWDWqAeUmYKCoVzbLy9cI3khRfartiEUrgNNJLdK5hsoRlj2CNXcEuv90mIzQ0yg3DE9vo32blVQLKWxRwuB7HC_AGuCCHe5r_Hfhky74BSpT_-DNrZSW8hHawjDlhUglBb6kRBcS5bdOsGggXgWYvT0_WGInJFenPV4vuU8CNXf3sMKV)
45. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ4QrKuX6QnwI47zDttMTrc-hftUvjoOxv8969SdJUTcUSaAEnlaaEZSy_20lq0qE-6ysPvYhEQarx7_iMlcF20x__BC7dlMA8JjKHIHwVFlpcDd_No1wZCUeqrpLh4qnHSonidJhuiR3gq-zoGeRYaYwQ2QnK3Ctk-GsvzbisGrwCd3pEltIDcTgcVi_cWQsLzv8NnYo=)

