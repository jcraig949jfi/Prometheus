# FALS-05: Claim-graph construction from math literature

**Pythia queue id:** 32
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdxaXNNYXZhcERQaWJfdU1QaTZxcG1BWRIXcWlzTWF2YXBEUGliX3VNUGk2cXBtQVk
**Elapsed:** 244s
**Completed at:** 2026-05-19T09:25:51.348223+00:00

---

# Synthesizing the Mathematical Literature: Claim Graph Extraction, Scalability, and Normalization (2024-2026)

*   **Key Points:**
    *   Research suggests that the extraction of mathematical claim graphs has advanced significantly between 2024 and 2026, transitioning from informal text mining to rigorous, formally verified neuro-symbolic pipelines. 
    *   It seems likely that systems bridging natural language and formal proof environments (such as Lean 4) are establishing a new baseline for claim autoformalization, though performance on deep, graduate-level mathematics remains a significant hurdle.
    *   Current data indicates that scaling claim extraction to million-paper corpora is computationally feasible through topological unfolding and semantic vector databases, although the verifier latency inherent in formal systems continues to pose a bottleneck.
    *   The evidence leans toward claim normalization remaining an open problem, specifically regarding the canonicalization of citation intent, numeric uncertainty, and the mitigation of temporal leakage across diverse scholarly styles.

**The Shift Toward Formalization in Literature**
Historically, mathematical knowledge has been trapped within static documents, requiring immense human effort to verify, trace, and interconnect. In recent years, artificial intelligence has begun to unlock this knowledge by translating informal prose into structured, machine-checkable code. By converting millions of papers into interconnected graphs where every node is a claim, theorem, or premise, researchers can now programmatically map the entire landscape of mathematical literature.

**Bridging Human and Machine Reasoning**
To achieve this, modern tools combine the pattern-matching capabilities of Large Language Models (LLMs) with the absolute logical certainty of formal proof assistants like Lean and HOL Light. Systems can now recursively unpack a complex theorem into all of its foundational definitions, allowing AI to trace the exact dependencies of a concept. However, when these conceptual chains become too long, current AI models frequently lose track of the underlying logic, demonstrating that human-level reasoning across deep mathematical dependencies has yet to be fully realized.

**The Normalization Challenge**
Even when claims are successfully extracted, harmonizing them remains a persistent challenge. Different authors use varying citation styles, terminologies, and contextual assumptions to state similar mathematical truths. Determining whether a new paper supports, extends, or completely refutes a prior claim requires sophisticated relational classification. Normalizing these claims into a universal, canonical format is critical for building trustworthy automated fact-checking systems and preventing AI from drawing false conclusions from fragmented literature.

## 1. Introduction

The translation of mathematical literature from unstructured, natural language prose into formal, structured dependency graphs represents one of the most ambitious frontiers in artificial intelligence and computational linguistics. The period between 2024 and 2026 has witnessed a paradigm shift in how mathematical knowledge is extracted, verified, and interconnected. The impetus for this shift lies in the intrinsic limitations of traditional semantic search and the rigid demands of automated theorem proving (ATP). As the global corpus of mathematical literature expands rapidly, researchers face increasing difficulties in determining whether a specific result already exists, discovering related variants, and identifying historical origins [cite: 1, 2]. 

Historically, large-scale digital libraries relied on keyword indexing, metadata tagging, and basic citation networking to navigate knowledge [cite: 3]. However, the nuances of mathematical claims—where a theorem's validity strictly depends on a complex hierarchy of prior lemmas, definitions, and premises—cannot be adequately captured by standard bibliometric graphs [cite: 4, 5]. To address this, the field has moved toward the extraction of **claim graphs**: directed acyclic graphs (DAGs) where nodes represent individual mathematical statements (e.g., definitions, theorems, lemmas) and edges represent logical or semantic dependencies [cite: 6]. 

This report provides an exhaustive analysis of the state-of-the-art tools and frameworks developed between 2024 and 2026 for extracting claim graphs from primary mathematical literature. We systematically evaluate the integration of formal metadata (e.g., Mathlib4), neuro-symbolic reasoning frameworks (e.g., NLProlog, ProofNet++), and interactive extraction environments (e.g., Lean-Dojo). Furthermore, we analyze the scalability of these architectures when applied to corpora containing millions of papers, examining structural bottlenecks such as verifier latency and topological unfolding. Finally, we explore the open problems in claim normalization across disparate citation styles, focusing on challenges such as contextual dependence, numeric canonicalization, and the semantic disambiguation of scholarly intent.

## 2. Existing Tools for Claim Graph Extraction (2024-2026)

The ecosystem for extracting mathematical claims has bifurcated into two synergistic approaches: (1) extracting and formalizing knowledge from unstructured text using large language models, and (2) mining structured metadata from formal proof assistants to train better retrieval and verification agents. The following frameworks define the state-of-the-art in this domain.

### 2.1 Mathlib4 Metadata and Matlas 

Mathlib4 is the foundational mathematical library for the Lean 4 interactive theorem prover, acting as a collaborative repository where established results are continuously formalized by a global community [cite: 1, 7]. Because it eliminates the need to repeatedly formalize established results, it serves as the ultimate ground truth for mathematical claim graphs. However, extracting actionable knowledge from Mathlib4 requires overcoming the semantic gap between its rigid formal naming conventions and the informal queries utilized by researchers [cite: 7]. For instance, "Cauchy's Mean Value Theorem" is formally codified as `exists_ratio_deriv_eq_ratio_slope`, making exact-match string searches virtually useless [cite: 7].

To bridge this gap, extraction pipelines mine Mathlib4 metadata—including theorem names, formal statements, documentation strings, and hyperlinked related definitions [cite: 7]. This metadata is frequently processed through LLMs (such as GPT-3.5 or GPT-4) to auto-generate informal natural language statements, which are then paired with their formal counterparts to build parallel corpora [cite: 7].

Building upon this paradigm is **Matlas** (2026), a semantic search engine designed specifically to construct and navigate massive mathematical claim graphs [cite: 2, 8]. The core innovation of Matlas lies in its graph-theoretic approach to statement unfolding:
1.  **Extraction**: Matlas extracts mathematical statements from published papers and textbooks.
2.  **Graph Construction**: It constructs a document-level directed dependency graph where node $B$ is connected to node $A$ if $B$ logically depends on $A$ [cite: 1].
3.  **Topological Unfolding**: The system processes the graph in a layer-wise topological order. By recursively expanding statements starting from layer 0 (nodes with zero in-degree), the system generates "self-contained" representations of highly complex theorems [cite: 1, 2].

This process results in stable, statement-centered vector embeddings (utilizing models like Qwen3-Embedding-8B) that retain their deep mathematical dependencies without suffering from context-loss at arbitrary batch boundaries [cite: 1, 2]. 

### 2.2 Lean-Dojo and Premise Mining

While Matlas focuses on extracting claims from natural language literature, **Lean-Dojo** serves as the critical infrastructure for extracting and interacting with formal mathematical graphs directly from Lean repositories [cite: 9, 10]. Lean-Dojo converts the Lean proof assistant into an interactive, gym-like environment, enabling programmatic extraction of Abstract Syntax Trees (ASTs), file dependencies, proof states, tactics, and premises [cite: 9, 11].

A primary bottleneck in theorem proving is **premise selection**—the task of identifying which previously established theorems or definitions are required to prove a new claim [cite: 11, 12]. Lean-Dojo solves this by mining fine-grained premise annotations directly from the Lean codebase, generating a precise relational graph between a claim and its logical ancestors [cite: 9, 11]. 

Using this extracted graph data, the Lean-Dojo framework powers **ReProver** (Retrieval-Augmented Prover), an LLM-based agent. Given a current proof state, ReProver retrieves accessible premises from the Mathlib network to generate the next tactic [cite: 9, 11]. ReProver leverages Lean-Dojo's programmatic analysis to separate genuinely accessible premises from hard negative examples, fundamentally relying on the structural integrity of the extracted claim graph [cite: 11]. The accompanying LeanDojo Benchmark (e.g., LeanDojo Benchmark 4) scales to over 122,000 theorems and proofs, providing a robust dataset for graph-based AI training [cite: 9].

### 2.3 ProofNet and ProofNet++: Neuro-Symbolic Verification

Autoformalization—the process of transforming natural language math into formal code—requires rigorous evaluation. **ProofNet** (2023) was established as a benchmark for statement autoformalization, containing hundreds of undergraduate mathematical exercises [cite: 13, 14]. However, purely generative LLMs suffer from "hallucinated logical steps and unverifiable reasoning" when attempting to navigate these benchmarks [cite: 15, 16].

In 2025, **ProofNet++** emerged as a neuro-symbolic framework designed to explicitly combat these hallucinations by coupling LLMs with formal proof verification and self-correction modules [cite: 15, 17]. ProofNet++ represents a critical advancement in the reliability of extracted mathematical claims:
*   **Symbolic Proof Tree Supervision**: The system trains on normalized, annotated proof trees derived from corpora like Lean's Mathlib and HOL Light, representing approximately 120,000 proofs [cite: 15, 16].
*   **Verifier-Guided Reinforcement Learning**: ProofNet++ uses the formal verifier (the proof assistant's kernel) as a reward function. Only valid proof steps in the claim graph receive positive reinforcement, heavily penalizing hallucinated transitions [cite: 15, 16].
*   **Iterative Self-Correction**: When a proof state fails, an automated module diagnoses the logical or syntactic error, proposing repair candidates that are re-validated by the kernel [cite: 15].

Empirically, ProofNet++ achieved a 74.9% Final Proof Success Rate (FPSR) on the `mathlib-extract` dataset, demonstrating high efficacy in generating sound mathematical subgraphs [cite: 16].

### 2.4 NLProlog: Reasoning over Unstructured Text

While systems like Lean and HOL Light operate strictly within formal syntax, real-world primary literature is written in ambiguous natural language. **NLProlog** provides a bridge by implementing Neural Probabilistic Logic Programming, which blends deep learning with the logical inference rules of Prolog [cite: 18, 19].

NLProlog allows for reasoning over natural language claims by using a technique called **weak unification** [cite: 18, 20]. In traditional logic, symbols must match exactly (e.g., `theorem(A)` and `theorem(B)` do not unify). In NLProlog, natural language phrases are embedded into vector spaces, and unification occurs based on semantic similarity rather than exact symbolic matching [cite: 19, 20]. 

For claim graph extraction, this means that NLProlog can parse a scientific document, extract open information (OpenIE) triples, and logically infer connections even if the terminology varies [cite: 20]. The system combines a knowledge base of extracted facts with logical rules (e.g., transitivity, inheritance) allowing the model to trace arguments through a paper deductively while remaining differentiable and trainable via gradient descent [cite: 19]. Though less absolute than Lean, NLProlog is vital for mapping the vast majority of mathematical literature that has not yet been formalized.

### 2.5 The MathAtlas Benchmark

The frontier of claim graph extraction was formalized in May 2026 with the release of **MathAtlas**, a large-scale autoformalization benchmark for graduate-level mathematics "in the wild" [cite: 6]. MathAtlas highlights the extreme difficulties of extracting deep dependency graphs from advanced textbooks. 

The benchmark contains roughly 52,000 theorems, definitions, and proofs extracted from 103 textbooks, explicitly annotated with a mathematical dependency graph of ~178,000 relations [cite: 6, 21]. Constructing MathAtlas required running entity extraction on multimodal mathematical documents (MMDs), followed by reference extraction to identify dependencies, and relation extraction to build the final DAG [cite: 6].

Evaluations on MathAtlas revealed a stark reality regarding current AI capabilities: state-of-the-art models achieved at most a 9.8% correctness rate on formalizing theorem statements [cite: 6, 21]. More critically, performance is inversely correlated with the depth of the claim graph. On the "MA-Hard" subset—consisting of 700 entities with the deepest dependency trees—accuracy plummeted to just 2.6% [cite: 6, 21]. This demonstrates that while shallow extraction (e.g., basic definitions) is solvable, traversing deep conceptual hierarchies remains a major open problem [cite: 22]. 

## 3. Scalability per Million-Paper Corpora

Scaling claim graph extraction to million-paper corpora presents unique computational and architectural challenges. The transition from processing isolated PDFs to maintaining a continuously updating, semantically unified graph requires algorithmic breakthroughs in dependency resolution, subgraph routing, and verification efficiency.

### 3.1 Real-World Scale: The Matlas Implementation

The Matlas search engine represents one of the most successful empirical demonstrations of scalability to date. It was constructed upon a corpus of **8.07 million mathematical statements** extracted from **435,000 peer-reviewed papers** (spanning 1826 to 2025) and 1,900 textbooks [cite: 1, 2]. This approaches the million-paper scale and requires sophisticated data engineering.

To achieve this, the corpus was derived from 180 curated journals selected via an ICM citation-based criterion [cite: 1, 2]. The fundamental bottleneck at this scale is resolving dependencies across documents. Matlas addresses this through its document-level dependency graphs and recursive topological unfolding [cite: 2]. By ensuring that each statement is recursively expanded into a self-contained unit utilizing its graph ancestry, the system eliminates the need for expensive multi-hop retrieval at inference time, at the cost of massive computational overhead during the preprocessing and embedding phases [cite: 1, 2]. 

### 3.2 Verifier Latency and Computational Bottlenecks

While extracting informal claims scales reasonably well using distributed LLM inference, scaling *formal* claim verification (as seen in ProofNet++) is severely bottlenecked by the proof assistants themselves [cite: 23]. 

In neuro-symbolic reinforcement learning loops, every proposed edge in the claim graph must be evaluated by an external verifier (e.g., the Lean 4 kernel). In ProofNet++ experiments, flawed proofs involving topological errors (representing 24% of the flawed dataset) triggered an 18.2% increase in verifier latency [cite: 15]. The average verification time was 176 ms for `mathlib-extract` and up to 214 ms for HOL Light (which averaged longer proofs of 14.3 steps) [cite: 23]. At a million-paper scale—where trillions of potential tactic steps must be evaluated—this latency translates into thousands of GPU-years. 

To mitigate these scaling issues, researchers are developing test-time scaling (TTS) workflows, adaptive heuristics, and hierarchical sampling to selectively route only the most promising subgraph trajectories to the formal verifier [cite: 13, 14, 24].

### 3.3 Graph Coordination and Cascade Growth Models

When multi-agent LLM systems are deployed to extract and verify claims at scale, their interactions generate complex coordination topologies. Recent studies (April 2026) have modeled this behavior over 1.5 million coordination events [cite: 25]. 

In these systems, coordination propagates through "claim-rooted cascades" over the global claim graph $\mathcal{G} = (\mathcal{C}, \mathcal{E}_c)$, where each selected claim can generate new claims via delegation, revision, or synthesis [cite: 25]. Under reinforced routing algorithms, the selection of claims follows a preferential attachment model:

\[ \beta(N) = \frac{d\log R(x,N)}{d\log x} \]

Where $R(x,N)$ is the routing ratio for claims with activity $x$ in a system of size $N$ [cite: 25]. However, because LLM multi-agent systems are bounded by context limits and finite agent populations, they do not produce unbounded scale-free networks. Instead, the cascade sizes follow a truncated power-law distribution:

\[ P(X=x) \propto x^{-\alpha}e^{-x/x_c} \]

where $x_c$ denotes the characteristic cutoff imposed by systemic constraints [cite: 25]. Understanding these graph dynamics is critical for designing scalable infrastructure that prevents infinite reasoning loops while ensuring thorough coverage of the mathematical literature.

### 3.4 Distance-Generalized Core Decomposition

To process million-paper corpora, backend graph databases must employ scalable analytics. Identifying the most highly interconnected sub-theories within a massive claim graph relies on algorithms like distance-generalized core decomposition [cite: 26]. A distance-generalized core, or $(k, h)$-core, is a maximal subgraph where every node has at least $k$ other nodes within a distance of $h$ hops [cite: 26]. 

Advanced peeling techniques utilizing elegant bitmap implementations and node sampling strategies (e.g., Lite Graph Transformers parsing in $O(N \log N)$ time) have yielded up to 100x speedups over state-of-the-art exact algorithms [cite: 26]. These algorithmic improvements are strictly necessary to query and maintain mathematical dependency DAGs spanning tens of millions of interconnected claims.

## 4. Open Problems in Claim Normalization Across Citation Styles

Extracting a claim graph is only the first step; making that graph logically coherent requires **claim normalization**. The primary mathematical literature is highly heterogeneous. Different authors employ varying nomenclatures, notation conventions, levels of rigor, and citation styles to refer to identical mathematical truths. Normalizing these disparate representations into a canonical form is currently fraught with open research problems.

### 4.1 Citation Intent vs. Claim Evolution (ClaimFlow)

Standard bibliometric graphs treat a citation as a binary edge (Paper A cites Paper B) [cite: 5, 27]. However, this fails to capture the semantic interaction between the claims. The **ClaimFlow** framework (March 2026) highlights the critical open problem of mapping how scientific claims evolve across decades of literature [cite: 5, 27].

ClaimFlow introduces the task of *Claim Relation Classification*. Rather than merely parsing a citation marker, an AI model must ingest a cited claim, a citing claim, and the citation context, and infer the scientific stance [cite: 27]. ClaimFlow taxonomizes these relations into five categories based on argumentation theory:
1.  **Supports**: The citing paper reinforces the cited claim [cite: 5].
2.  **Extends**: The citing paper applies the claim to a new domain or dataset while preserving its core assertion [cite: 5].
3.  **Qualifies**: The citing paper restricts the validity or scope of the cited claim without rejecting it [cite: 5].
4.  **Refutes**: The citing paper contradicts or proves the cited claim false [cite: 5].
5.  **Background**: The cited claim is mentioned purely for context without evaluation [cite: 5].

In an analysis of ~13,000 NLP papers, ClaimFlow revealed that only 11.1% of claims are ever challenged, and widely propagated claims are much more frequently *reshaped* (qualified or extended) than directly confirmed [cite: 5, 28]. 

The open problem lies in normalizing these shifting claims. When a theorem is heavily "qualified" over twenty years, its modern canonical statement may differ drastically from its original publication. Automated systems struggle to align these historical versions into a single unified node within the claim graph, as language models currently achieve only a baseline 0.78 macro-F1 score on this relation classification task [cite: 27, 28].

### 4.2 Numeric Claim Normalization and Uncertainty

Many applied mathematical claims and statistical proofs involve numeric estimations, bounds, and confidence intervals. Normalizing these numeric assertions across varying formatting styles is a highly complex open problem [cite: 29].

Recent theoretical frameworks (e.g., February 2026) attempt to define operators for Canonicalization. For an interventional estimand $\epsilon$, and a numeric claim $c = (\theta, CI)$ (where $\theta$ is the point estimate and $CI$ is the confidence interval), a canonicalization operator $N$ maps this to a normal form:
\[ N(\epsilon, c) \mapsto (\epsilon_{canon}, c_{canon}, \alpha) \]
where $\alpha$ records any required conditions [cite: 29]. 

This operator must satisfy determinism, idempotence ($N(N(\epsilon, c)) = N(\epsilon, c)$), and semantic preservation [cite: 29]. However, parsing missing or partially specified uncertainty—especially when extracted from older literature utilizing outdated statistical reporting standards—often results in systemic errors during automated fact-checking and quantitative claim alignment [cite: 29]. When scaling to complex numerical claims, standard LLMs suffer from "reasoning drift," requiring adaptive test-time scaling strategies (like predicting claim complexity via layer-wise latent representations) to preserve accuracy [cite: 24].

### 4.3 Contextual Dependence and Temporal Leakage

Automated verification of claims using retrieved literature frequently encounters issues of **contextual dependence** and **evidence insufficiency** [cite: 30, 31, 32]. A mathematical lemma stated in a 1980s paper may rely on unstated assumptions standard to that era's specific sub-field. When an AI extracts this lemma into a global graph, it is stripped of its implicit context, rendering it potentially invalid when combined with modern axioms.

Furthermore, **temporal leakage** occurs when a model uses future knowledge to evaluate a past claim, or when a historically accurate claim is falsely flagged as incorrect because the terminology (or underlying classification) has since evolved [cite: 30, 31]. Recent datasets (e.g., AVerImaTeC) attempt to mitigate this via strict claim normalization, temporally constrained evidence annotation, and two-stage sufficiency checks, achieving inter-annotator agreements of $\kappa = 0.742$ [cite: 30, 31]. Nevertheless, enforcing these temporal and contextual constraints universally across millions of mathematical papers with highly variable citation styles (e.g., inline numbers, author-date, footnotes) remains largely unsolved [cite: 30, 32]. 

## 5. Conclusion and Future Trajectories

The period from 2024 to 2026 has definitively proven that the extraction of claim graphs from mathematical literature is computationally feasible, yet bounded by steep logical and semantic hurdles. Tools like **Lean-Dojo** and **Mathlib4** metadata extraction have successfully turned formal repositories into massive datasets of actionable premise graphs, establishing the gold standard for logical correctness [cite: 7, 9, 11]. Concurrently, frameworks like **NLProlog** and the integration of vector databases in **Matlas** have enabled the scaling of these extraction pipelines to millions of natural language papers [cite: 2, 20]. 

The introduction of neuro-symbolic systems such as **ProofNet++** demonstrates a promising pathway to bridging the generative flexibility of LLMs with the absolute rigor of formal verifiers via self-correcting reinforcement loops [cite: 15, 16]. However, as the **MathAtlas** benchmark starkly revealed, when AI systems attempt to formalize graduate-level mathematics containing deep dependency chains, performance collapses dramatically [cite: 6, 21]. 

Achieving a truly unified, million-paper mathematical claim graph will require solving deep open problems in **claim normalization**. Systems must be developed that can accurately trace the evolution of claims through complex citation networks (as proposed by **ClaimFlow**) and reliably normalize numeric uncertainty, contextual dependence, and disparate citation styles [cite: 27, 29]. 

As the digital infrastructure of mathematics continues to shift from static PDFs to interactive, machine-readable DAGs, the synergy between informal semantic extraction and formal proof verification will dictate the pace of automated scientific discovery. The eventual realization of an automated, self-correcting global mathematical library relies not merely on scaling LLM parameter counts, but on advancing the fundamental graph-theoretic and neuro-symbolic algorithms that parse the intricate tapestry of human reasoning.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRXW4V65MfFEnIgNN0X3AZFwoRzB0zkcXHuwqDDbqzy3gC0ei66FeP21YTWw2pd40tXTyCkPTgbB2SrGOsFYe6QD17xsnGmhulVVjbpEPOdHsHiyXiZ8HxbQ6vPal3Cg8pzcASwg6ZW5MLvvWWTloHnNIFNaJ9JwXv1bv7KC2SpWY1JpKuomYjp9SFwGN-U77jcG2mRLtjFjLkYoKHZAWMIw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOcCcgPUOpyMG_8f78DojN8EzLzqx7IbiPh4BzHaKOYQa2_LDS8WtDxGiPcNv3GQdmaicBi5g8G7bvEzbeLf2YbIQSg9vgPpoT0b0nxr5QWTVjJiCwTg==)
3. [mathunion.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAnGv1VJMotLACwMf9KequRDm3ONuAslkWD5S8WGQoKsRDn8mSyGrj9npDUQN2cGQuMiEZ8tu2K45fB2BIHQHHZ-8bpoRQku_NS1VxQ54pfrJz7UtuMcYQSuqRmhhkeCTCAwBOQ4nq6_xO0dgDTslc3te8LqXByuMWkQbXO4CmRBvtI8sGk--BNaP3NXNR1kXU)
4. [nationalacademies.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF40EKnVTiQxd7pOGmwHr6bXXhdQQHZBoQmvNR9Z-n_sPcEioPvn1BQaIC5UXX_Dc5N1kazvaLaqvn9gl2wGrNM2fjz8ZI6geNJjhoKUy7YEenzHTC2EBbcQyNCt5oRj1d0Sc0iXWw2UA3x38=)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpiPent1YbLHrUqzgs-U-dtLLWq8WFVhZ4PmRKzhxdpRpf7AvxXq09A2IIpnLAfCb38-AnFG57m4ujGYpGHSq5V4Qb6AAUwr2BdrTeDw3kXfXqQInm-BKUKkMuXLDRhrmU6wzmzaqvBEqdh9J_k12eYgOW_UbdoQmxXa3e-jFz6abBuebtaYxJSFKv6vi1sy-40fO2idqIZ1lir5AyNUoutuHdIg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENBZmCBFfmRswp8TleBOBRYRbkEkzwUrY_g5FaKIb3WQaAQHDwf_dEg0LbybYh9OTuVMIHYwBHurnQRn39VbSmOGP6obWAFKvulptPzWU93cltXmScaMnK_g==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHizAceu0dKziNlxgIHsTwipbn2KWubt2_3JTWpgOvQe1kppGrpN37Vnlwc4RldaSGne93ATaJqyCv9GkKNviRnZaOmUL7vYaQzdkv_vOzLSCFpx1LytJB7ug==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5_hUq9TeEV9M3VtBSuW-KVqbqyZ1-UTSNergEJiTsbpcC5XSbly4E-nCwkT4nYWoR3yaZVbxzZozGkE1lF1gdZpCE6FuCfgSP_ZI2IrVST5zPPfy8pg==)
9. [leandojo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbLM-AcH2EuksOVCHrugn-utdJsx4I_sWKbNEZMPV5ABADUQH2MW8-bVqZGJ9cD8qchszbix7bKeO9xHi5myP04HTEMRwrOA3v349iv2rkdg640PFipOGZ)
10. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9DSk_-c6y8GmmkXDxfnX4mM5a68Y6GFalQHpS2xU8KuWqEgV5u4XxY9XsLv7DF64UDIMF0WC-TUUgdW5z4nuQmoJYt5T5liwMo8mUESGzN3DYyRM79ioMEy0=)
11. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9tb1vkO19NVrhVi_RkhK50BpbU2rJGuVgy8vBsjaEMsg3wLyCh2jjU0sQ1-Y1GMdnf3K6Dvfs3xVW3E3IcAXOCqUqTvo1ZYtCXSHc8nWNOgRbxSyfDz7QXjq2KAiCIxzy-jjTVUBY-wk7o27kyMhN0I2tj2aZ5a_n9PyDKNa0iY9ywys-x7VVrq_SuyNFtorPRR6cwH3PlcH7Qflu_A87c3Oh_3qH7IXxMh5d0kijEKNF7Q==)
12. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjMta9iPKHSdoUaOaq2Is0hsBgVtDXPzvzpPkF4FTCLQwpkl6IsWNnHbwrGjZj-VW_thk0F2GySYiNHeVMMib4JtV0sPFDS1zyO6C99BmU6QFeDAmxUR4CAiixtFQEc2wLIos26Q3sh5ekwWjIrTIcvKsMMm1lh3QLitfVAwKgXMlSCIgQX-g128wj5T5GOF63s3yMHk6vPs65W1o3xgS6Ae15WKbMulJg3c2xJ68lgGtb0Q==)
13. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz86IgY3EtDzWvLrOYBv5ZmVdgH5WyHjUMSKwLpisVscwtl8Orl927soYck3py2qQebqcQHukVhiKQNIiSpgzSddMf931NIRkNuiPjSpQFvMbBe4TbrCL_xQDIVhuoFN8D7ga1aLw=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE236PqdE4Hu376xQO-FsWPthP4KMJLffRaln6Mz0kGDMuQBybPAq5FzMZl0H0XUG8rXNAmskMEL7y39FVym4X0PLyoUPeJpxudCHMmx-0vspbu-mq5CUVPft6uoCNj-YBOycRKgy93i2poQ7CetMJCpS_4b6QLx7uskJEtODPaZNLh-FyplsNE2BpK5Ucw35pCAi_35MZ0KIdFWAfv6oKulcwHcQTlBaE2Lgyaf7Hhk6oisIh1abz95eUi8I5C)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU7act14mZATEBdNpPCP0tYYtcA2oispWf7kCUiPqKm2batWbtF2DmEqgKAjk0nJd-GvN8bkrxg054X6wUgxAmCpSjBslirSzPB1EjJaNDVj1ZVdl464Pdfw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENKQEREze5FVbK9dOSxh8ECHG0RmuXKkoAdh3BFMVGzpCAadNGRwVSCxuYX0zv06FxuOJOg2gvt5z-_98rnoCRJuINv0ZbOnwjrSEaye12eCtExVrQC5M=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVdogDisMYM1hZK7NwZTm63POYgwBTM848n6XfmXZU_0OZTe-NJzD8WWbPyrOyQqcdkOYKXBsY3ArG7N8WgqrNL8Q5Y2J7bahqNBcBZltcuYFd8ZGGyQ==)
18. [eurecom.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNRYZHPJSqwTSdJzEBxIAOqAqXbswOShZduti0uNnKdlqQxsozfRAiYubhhxNl5w3z5nMQubKnRFn5tIMwkcUk61xWbDJrKkgy8lqUw8O_NE2aoOGZ8IrjVyALlPrq9l7yxIeXI0QSCH7qpCkoVaNZp8izLg_jcnIA8w==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_yEhAm5FmlpHchTjPJ3z1cEma2FZE30JRQl2sLC07Z5P5Ay11KPzU29UqS-YOb6SgEzC_pT5UMIp6wkhpxq3-K8R9fqGgRCYiSC3mEaHSKFDGK0KjSFPgNHSYLPsJFuAVjIml4whbygUsyju0npr5YXojhIR8BoUoaD3jcTacSgmHlcRMjm1xXsjk-2622SRKEWkZD6327vQUZg==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcBhQuHQqhI_7xzWAvYDZZ0x99gHjDa3Woe6gonJWqR981y5NkH-YpNg-c-oIizXPuW4l-MdSjwlDy3Rja4-GDJmruLK2v-AsMLLN30Ttqcsv-f1LSbBRo-Q==)
21. [awesomeagents.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-vtnLkHhfzbgEEKKXTyPdFsfRMruC-EA5_NB846K1r748JbhKWWckOV2iiXRKypJF2WH96mSBtItsCsjK4WmJKcYbv29nMpxgj5McwbAbcUD2wXcDFq6rF1ZDfSweh19P13j2kv1GGcet7qKVD3zlNf1ezZ-IhtQo3OzYXkC_fQJarjc=)
22. [hypexio.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYdF3l-_bDEY1ICYtzTuskKpTe_WMMn-ZuuX8Lo_zh8PQbINck-RyoEpTdldLrDXaKpVCRhGKhUqih5DW8l1-tGn69IMWSzPdwuKTskgeM2CbI5jFOFJpyFLa6fyPaJc7fT-BYoOW2oxIydrtgIUfzAgdodnYUNxwAEEdwwz6H)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHElOluQDLLbNV2oz1lLP8539Qg_k4dBkBsmjsTlyFFRUika5MMN3_Znt2vN7nhWwAD05miDAL-ZbsMv697tsD4DfDly1dGRlxSeOwRwKJn06pZ20LT_WuiUiEkINZF8fo0i05Zi9F68duQVkAHncfmsmkuNKlTZLv1iFTi7oKWjfHZCGS5-hUM1v4T1H1FYOhxjiRfx6bevAHb07TB4vvbgNlwMm3_KRu1Xr4BAWixQ1gMLOjWLfeVUA9Kog4=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbayKDgIlFqVwNgkYIGnTljipQafc5FmxcISxJyucBDLv_Xajy_yfNDwHbvEWB4BsWF6G56tMAt3YQGHBXb652yfZO69M2kAhnF-YvrRbG-_HPo5dTd9sm5A==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFUFvWG9-9dVlCvylacPpu4VseyjCUGeq4P0kW1JSEFUoOlLcam1j1AbVGdiSDmnlnO8a3omFdwjRD1FPWhD1fjPZxIe_ccc6ElM6ehjQTe9MW4BLJtG4k0g==)
26. [sigweb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-N6PnFDwTb2Te-I0jLEHA4cwZRpbbEGcGr5a327n437tXYji10VlLypqtpx2QznoKCN-wykkQ4iw2w-QZjAycBw1h55z5hGToA3DzclILVWsJyGfo_m5AA03-9w==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh1Hb5z9_IV9ZP1vnQGfT4HNFG4XglpG_ThXn2LraQxXskJ8DYD7Bcp35BQPCipmlQNFoxxqLhR5imRzGy6sqdALoWmsEiEXvM09w34l26UV_MnrbNGzHX7g==)
28. [catalyzex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtiq-HoAnvZqqRU8aZZSiCF_ICavkWoHh_--i3E4Zt-LQc50w7JdVuhcERZcQ6PGYG3iH87zH0d7bCUyA9DzQRdZk_K2VV84b8HC9Ng36VkxoOy2uMxLLncUNvrwyniGZwVsMXTkPS)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfzUbVSzVsfKRTmgxfcsnH2I6Z5IaGvKDBgNdqGI0-QM7FfFJldhxFRdAK4dGwvlntJHiiGjdn6K4u4uNBUgALUPc7ceQGnDWVrkSkKsDG6v_OPGa1ot0OMA==)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9X_Z2MItBilBcGpPZrAiMaIXzZaffc0R9HnlWsKJLpnSCiNb2GC072SUw4F0c2osjAYcdl5qORRJ2Tpiwau6Ipk9s3URHYpgmZeyUxx1NgQNAxWQWSWEWUl3FlQ==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoqv2UgFF6tBxw7dz46zdnzhstFTi8aXooqgNtvrfLyBXC4j42lclILb-ukUyoLusp4JIBsGq0ZwXPWu3tQUiGOHDLzY6qeX043smB5u3ZJgR8LOHR8-EePA==)
32. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGfPrwMQQrvpLThItnEwk-AYRq9wyvDi5V2YFiTcFh_7WfcrGxQi-5MQ7QQMAiU6liA97On36-z3pDK59Sew5Ryeh0zjqiGU7Mv-cHfDnljCblhBkb_kcNfLBKalcRXUhxkZbaaQegv0-nP-1WXMu_nA1UHg==)

