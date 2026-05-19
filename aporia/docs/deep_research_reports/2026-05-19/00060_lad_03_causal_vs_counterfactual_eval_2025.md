# LAD-03: Causal vs counterfactual eval 2025

**Pythia queue id:** 60
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdYVmNNYXQzOEdyR2I5TW9QeTRQN3FBdxIXWFZjTWF0MzhHckdiOU1vUHk0UDdxQXc
**Elapsed:** 252s
**Completed at:** 2026-05-19T12:32:26.325794+00:00

---

# State-of-the-Art Benchmarks for Evaluating Causal and Counterfactual Reasoning in Large Language Models (2024-2026)

* **Key Points:**
* Research suggests that while large language models (LLMs) excel at identifying patterns and associations in vast amounts of data, their ability to perform genuine cause-and-effect reasoning remains a debated frontier. 
* It seems likely that current top-tier models rely heavily on memorized training data to answer causal questions, often struggling when presented with entirely novel or counterfactual "what if" scenarios.
* The evidence leans toward a significant gap between "seeing" (observational data) and "doing" (interventional actions), though recent experimental frameworks from 2024 to 2026 show promising pathways to bridge this divide.
* Advanced evaluation tools—such as CRASS, CausalGym, and new Pearl-tier intervention probes—are actively being developed to rigorously test whether AI systems can move beyond statistical guessing and truly understand the mechanics of cause and effect.

**The Shift to Causal AI**
Historically, artificial intelligence has been dominated by associative learning—the ability to find correlations within massive datasets. However, researchers are increasingly recognizing that true intelligence requires understanding *why* things happen. This shift has led to the development of causal AI, a field dedicated to teaching machines the rules of cause and effect. Over the past three years (2024-2026), the focus has rapidly shifted from testing basic knowledge to evaluating deep, counterfactual reasoning. 

**Evolution of Benchmarks**
To test these emerging capabilities, scientists have introduced highly sophisticated benchmarks. Early tests often accidentally allowed models to "cheat" by relying on memorized facts. Newer frameworks, such as CausalProbe-2024 and CounterBench, deliberately use fresh news or nonsensical variables to force models to demonstrate raw reasoning skills. Simultaneously, tools like CausalGym look inside the model's "brain" to see how it physically processes these linguistic and causal rules.

**Distinguishing Seeing from Doing**
A central question in modern AI research is whether a model can tell the difference between passively observing a phenomenon and actively intervening to change it. While models like GPT-4 and Gemini 1.5 exhibit impressive associative skills, their ability to navigate the complex mathematics of interventions—known as the *do*-calculus—remains inconsistent. Recent breakthroughs in 2026 suggest that by using the LLM itself as a simulator, AI systems might finally begin to master these higher-level cognitive tasks.

***

## Introduction: The Ladder of Causation in the Era of LLMs

The pursuit of Artificial General Intelligence (AGI) fundamentally requires endowing machines with the ability to reason about cause and effect. The pioneering framework for this endeavor is Judea Pearl's **Ladder of Causation**, which categorizes cognitive reasoning into three distinct, hierarchical rungs: **Association** (seeing), **Intervention** (doing), and **Counterfactuals** (imagining) [cite: 1, 2]. 

At the foundational level, **Association** involves detecting statistical correlations and patterns in observed data (e.g., observing that smoking is associated with adverse health outcomes) [cite: 1]. The vast majority of classical machine learning and pre-trained Large Language Models (LLMs) operate primarily at this level, leveraging massive datasets to predict the next token based on learned probability distributions [cite: 1, 2]. The second rung, **Intervention**, requires predicting the consequences of deliberate actions or changes to a system (e.g., "What happens if we ban smoking?") [cite: 2]. This necessitates modeling the causal relationships among variables, often utilizing directed acyclic graphs (DAGs) and Pearl's *do*-calculus [cite: 1]. The highest rung, **Counterfactuals**, involves reasoning about hypotheticals and alternative realities (e.g., "What would have happened if the patient had not smoked?") [cite: 1, 2]. This level of reasoning requires abduction, intervention, and prediction, forming the core of human-level strategic and scientific thinking [cite: 3].

As LLMs have scaled in parameters and capabilities between 2024 and 2026, the academic community has critically examined whether these models genuinely climb this ladder or merely simulate higher-order reasoning through advanced associative lookup—often termed "level-1" behavior [cite: 4, 5]. To rigorously separate genuine causal inference from "causal parrots" relying on parametric memory, researchers have introduced an array of sophisticated benchmarks and interventional probes [cite: 6]. This report exhaustively details the latest advancements in LLM causal evaluation, focusing on benchmarks like **CRASS** and **CausalGym**, the emergence of **Pearl-tier intervention probes**, and the empirical capacity of contemporary models to distinguish observational from interventional distributions.

## Observational vs. Interventional Reasoning: Can LLMs Distinguish "Seeing" from "Doing"?

The distinction between observational and interventional distributions lies at the heart of causal inference. Within a **Structural Causal Model (SCM)**, an observational distribution, denoted as \(P(Y|X=x)\), reflects the probability of \(Y\) given that we passively observe \(X=x\). Conversely, an interventional distribution, denoted using the **do-operator** as \(P(Y|do(X=x))\), reflects the probability of \(Y\) if we actively set \(X\) to \(x\), thereby severing all incoming causal influences (backdoor paths) to \(X\) [cite: 7, 8, 9].

### Theoretical Distinctions in LLM Processing
For an LLM to engage in genuine causal reasoning, it must recognize that intervening is not merely conditioning. When an intervention occurs, the state of the intervened variable provides no diagnostic evidence regarding its actual causes, which remain at their base rates [cite: 7]. In a common cause structure \(A \rightarrow B\) and \(A \rightarrow C\), observing \(B\) updates the probability of \(A\), which in turn updates the probability of \(C\). However, intervening on \(B\) (\(do(B)\)) severs the \(A \rightarrow B\) link; thus, \(B\) no longer provides information about \(A\), and the probability of \(C\) remains unchanged [cite: 7, 8]. 

### Empirical Performance on Intervention Effects
Recent empirical studies have sought to determine whether LLMs can accurately update their knowledge of a data-generating process in response to an intervention [cite: 10, 11]. Binz and Schulz (2023) adapted human psychology studies for LLMs, feeding models prompts that describe observational and post-interventional findings. They discovered that earlier models like GPT-3 performed poorly compared to human subjects, failing to understand the implications of interventions [cite: 12, 13].

More recent frameworks evaluate "intervention effects" via binary classification tasks that test which causal relations in a graph are modified by an observed intervention [cite: 12, 13]. Under specific prompt conditions, advanced models like GPT-4 exhibit "promising accuracy" in predicting how causal relationships shift under interventions [cite: 10, 11]. However, this capability is highly fragile. Researchers found that LLMs are acutely sensitive to the choice of variable names; when prompts utilize real-world variable names that trigger memorized associations (commonsense causal facts), performance can drop or skew, indicating that the models often rely on associative shortcuts rather than formal *do*-calculus [cite: 11]. 

Ultimately, while models like GPT-4 demonstrate moderate success on associational queries, their accuracy drops significantly when performing backdoor adjustments or identifying collider bias—tasks that strictly require the formal application of interventional logic [cite: 14].

## CRASS: Counterfactual Reasoning Assessment Benchmark

As researchers pushed models toward the third rung of Pearl's ladder, the **CRASS (Counterfactual Reasoning Assessment)** benchmark emerged as a foundational tool. Originally introduced by Frohberg and Binder, CRASS evaluates the ability of LLMs to answer counterfactual conditional questions, specifically focusing on "what if" scenarios that deviate from actual reality [cite: 14, 15, 16].

### Methodology and Dataset Structure
CRASS utilizes "questionized counterfactual conditionals" framed as premise-counterfactual tuples (PCTs) [cite: 14, 15]. The dataset contains 274 meticulously designed PCTs, each comprising a base premise, a counterfactual antecedent, and three possible consequents: one correct outcome and two distractors [cite: 14]. For example, a scenario might read: *"A woman sees a fire. What would have happened if the woman had fed the fire with dry leaves?"* [cite: 16]. 

The benchmark evaluates whether the model can maintain temporal and causal consistency in alternative realities, functioning independently of the actual timeline's causality [cite: 14, 16]. This makes CRASS highly relevant for AI applications requiring strategic planning, decision-making, and scenario analysis [cite: 17].

### Model Performance and Evolution
Initial evaluations on the CRASS benchmark revealed stark differences across model generations:
*   **T0pp** and early **GPT-3** models struggled, with GPT-3 achieving an accuracy of only 58.39% to 71.3% [cite: 18].
*   Subsequent iterations, such as **text-davinci-003**, improved to 83.94% [cite: 18].
*   **GPT-4** established a new state-of-the-art on CRASS, achieving an accuracy of 88.6%, indicating a robust capacity to adapt to few-shot demonstrations and generalize counterfactual arguments to novel scenarios [cite: 14, 18]. 

However, CRASS has structural limitations. While it excellently targets template-based counterfactual scenarios, it does not explicitly address deep cause identification, effect prediction, or multi-step causal chain tracing [cite: 14]. Furthermore, despite high accuracy scores by GPT-4, critics argue that because CRASS scenarios often overlap with common sense, models might still be leveraging highly advanced pattern matching rather than algorithmic counterfactual inference [cite: 14]. 

## CausalGym and Mechanistic Interpretability

To truly understand whether LLMs are reasoning causally or acting as "causal parrots," researchers have turned to mechanistic interpretability. In 2024, Arora, Jurafsky, and Potts introduced **CausalGym**, a benchmark designed not just to evaluate model outputs, but to assess the *causal mechanisms* shaping the internal behavior of the language models themselves [cite: 19, 20, 21].

### Benchmarking Causal Efficacy
CausalGym adapts and expands the SyntaxGym suite of tasks to benchmark the ability of interpretability methods to causally affect model behavior [cite: 19, 21]. The pipeline involves taking an input minimal pair exhibiting a linguistic alternation, intervening on the base forward pass using a predefined intervention function, and measuring how this intervention affects next-token prediction probabilities [cite: 22].

In a comprehensive study of the **Pythia** model family (ranging from 14M to 6.9B parameters), CausalGym was used to evaluate various interpretability methods, contrasting traditional linear probing with **Distributed Alignment Search (DAS)** [cite: 19, 21]. The study found that DAS significantly outperformed other methods in causally steering model behavior. Using DAS, the researchers mapped the learning trajectories of complex linguistic phenomena, such as negative polarity item licensing and filler-gap dependencies, discovering that the mechanisms implementing these tasks are learned by the LLM in discrete stages rather than gradually [cite: 19, 21].

### Advancements Beyond CausalGym: HDMI
By May 2026, the methodologies surrounding causal interpretability saw further refinement with the introduction of **Hidden-state Driven Margin Intervention (HDMI)** [cite: 23]. HDMI addresses the limitations of DAS and other methods that rely on auxiliary probe classifiers. It is a probe-free, gradient-based technique that directly steers the hidden states of an LLM using a margin objective [cite: 23]. 

Evaluated on metrics of completeness and selectivity, HDMI consistently demonstrated higher reliability than prior methods on the CausalGym benchmark across models like Meta-Llama-3-8B-Instruct and Pythia-70M [cite: 23, 24]. This proved that the internal representations of LLMs can be causally steered without external classifiers, providing deeper insights into how parametric memory translates into sequential causal predictions [cite: 23].

## The Vanguard of 2026: Pearl-Tier Intervention Probes and the ICP

The most profound paradigm shift in evaluating LLM causal reasoning occurred in mid-2026 with the formal operationalization of Pearl's conditioning-intervention dichotomy directly within LLM architectures [cite: 25]. Researchers recognized a fundamental limitation in earlier approaches (such as static causal graphs or standard prompt engineering): they could not distinguish whether a concept truly contributed causally to a correct answer, or whether the observed association was a spurious correlation driven by confounding variables, such as problem difficulty (\(D\)) [cite: 25].

### The Interventional Capability Probe (ICP)
To resolve this, researchers introduced the **Interventional Capability Probe (ICP)** within a framework known as **CIKA (Causal Intervention for Knowledge Activation)** [cite: 25]. The core innovation of CIKA is utilizing the LLM itself as a *do*-operator simulator [cite: 25]. 

The ICP is mathematically formalized to diagnose whether an LLM can *use* a given concept, which is distinct from merely possessing the knowledge [cite: 25, 26]. The causal effect \(\hat{e}_{c_i \to p}\) functions as a probe. By executing a *do*-calculus-based prompt intervention (e.g., \(do(c_i = 1)\), setting the concept state to "mastered"), the probe severs all incoming causal pathways to the concept, including the confounding arrow from problem difficulty (\(D\)) [cite: 26]. 

This achieves the **backdoor criterion** [cite: 25, 26]. Because the intervention exogenously sets the concept state independently of problem difficulty, the ICP isolates the true causal effect of the concept on the downstream problem-solving outcome, eliminating the confounding bias that plagues purely observational metrics [cite: 25, 26]. 

### Empirical Triumphs of CIKA
The distinction between "knowing" and "being able to use" represents the first true operationalization of Pearl's intervention layer for LLM knowledge diagnosis [cite: 25, 26]. Empirical results from 2026 demonstrate the massive efficacy of this approach:
*   On discrimination tests, the ICP successfully distinguished causally relevant concepts from irrelevant ones with high statistical significance (\(p < 10^{-6}\), Cohen's \(d = 0.86\)) [cite: 25, 26].
*   When applied to a frozen **7B-parameter LLM**, the CIKA framework achieved a remarkable **69.7%** on the contamination-free Omni-MATH-Rule benchmark, and **64.0%** overall [cite: 25, 27]. 
*   This performance effectively surpassed much larger or highly specialized models, including **o1-mini**, which scored 60.5% in the same conditions [cite: 25, 27, 28]. 
*   Crucially, the Causal Knowledge Activation component of CIKA contributed 33.8% of correct answers on problems where the base model initially failed, proving that the LLM possessed the requisite knowledge but lacked the causal activation to utilize it observationally [cite: 25, 27].

## Novel Benchmarks of 2024-2026: Pushing the Boundaries

Alongside theoretical probe developments, the benchmark ecosystem expanded dramatically between 2024 and 2026, shifting focus from static text to dynamic, multi-domain, and algorithmically rigorous causal assessments.

### CounterBench: Algorithmic Counterfactuals
Introduced in early 2026, **CounterBench** addresses the critical gap in evaluating formal, algorithmic counterfactual reasoning, moving away from the commonsense-heavy prompts of CRASS [cite: 29, 30]. 

*   **Design:** CounterBench comprises 1,200 counterfactual reasoning queries built upon deterministic Structural Causal Models (SCMs) [cite: 29, 30]. It features balanced distributions (50% "Yes", 50% "No") across diverse causal graph structures, varying difficulty levels, and nonsensical variable names to entirely neutralize pre-training memorization [cite: 31, 32].
*   **Findings:** Standard LLMs performed abysmally. When forced to rely purely on formal rules rather than prior knowledge, models like GPT-4o and DeepSeek-V3 performed at levels comparable to random guessing [cite: 30, 31]. Gemini-1.5-Flash achieved the highest baseline at 68.0% [cite: 30, 32]. Even advanced prompting strategies like CausalCoT failed to yield significant improvements, with GPT-4o reaching only 75.8% [cite: 30, 32].
*   **The CoIn Solution:** To solve this, researchers proposed the **CoIn** reasoning paradigm. CoIn forces the LLM to execute Pearl's three-step counterfactual process explicitly: abduction (inferring latent variables), action/intervention, and iterative prediction with backtracking validation [cite: 30, 32]. CoIn dramatically improved model accuracy, achieving nearly 90% on several state-of-the-art LLMs, representing a 20% absolute improvement over previous baselines [cite: 29, 32].

| Model | Baseline Accuracy | with CausalCoT | with CoIn Paradigm |
| :--- | :--- | :--- | :--- |
| **Gemini-1.5-Flash** | 68.0% | N/A | **Significant Gain** |
| **GPT-4o** | Near Random | 75.8% | **~90.0%** |
| **DeepSeek-V3** | Near Random | Marginal Gain | **Significant Gain** |
*Table 1: Approximate performance metrics on the CounterBench framework showcasing the necessity of explicit algorithmic guidance (CoIn) for counterfactual logic [cite: 30, 32].*

### InterveneBench: Real-World Social Systems
While CounterBench tests abstract, formal logic, **InterveneBench** (March 2026) grounds causal evaluation in messy, real-world scenarios. It specifically evaluates intervention-centered, end-to-end causal study design derived from empirical social science [cite: 33, 34].

*   **Design:** InterveneBench comprises 744 peer-reviewed studies across diverse policy domains [cite: 34, 35]. Crucially, it operates in a *structure-agnostic* setting; models must reason about policy interventions and identification assumptions *without* access to predefined causal graphs or structural equations [cite: 34, 36].
*   **Findings:** State-of-the-art models struggled immensely with this real-world complexity. GPT-5.1 achieved an aggregate score of only 0.578 and a 49.3% accuracy on model selection [cite: 34]. 
*   **The STRIDES Framework:** To bridge this gap, researchers introduced STRIDES (Social Theory-guided Research for Intervention Design, Estimation, and Scrutiny), a multi-agent system [cite: 34]. By decomposing the workflow into specialized roles (a Paper Interpreter, a Causal Designer, and a Critic agent), STRIDES simulates expert collaboration, improving LLM performance on InterveneBench by up to 25.1% [cite: 34, 35].

### CausalProbe-2024 and CausalBench
Addressing the pervasive issue of data contamination (where models memorize benchmarks during pre-training), **CausalProbe-2024** (July 2025) extracts its question corpora from highly authoritative, fresh news media (e.g., BBC, The Guardian) published strictly after the training cutoff dates of models like LLaMA 3, GPT-3.5, and Claude 3 Opus [cite: 4]. 
*   The results confirmed that when faced with genuinely novel scenarios, LLM performance drops significantly, proving they largely rely on "Level-1" associative retrieval [cite: 4, 5]. To compensate, the **G²-Reasoner** was introduced, merging retrieval-augmented generation (RAG) with goal-driven prompts to push models toward "Level-2" flexibility [cite: 4, 5]. 

Similarly, **CausalBench** (NeurIPS 2024) introduced a multi-dimensional evaluation spanning text, mathematics, and coding, rigorously testing cause-to-effect, effect-to-cause, and interventional directions to ensure models exhibit genuine structural understanding rather than statistical guessing [cite: 37].

## Synthesis: Which Models Distinguish Observational from Interventional?

The collective data from 2024 to 2026 provides a nuanced answer to whether contemporary LLMs can distinguish observational distributions (seeing) from interventional distributions (doing).

1.  **Out-of-the-Box LLMs (GPT-4o, Claude 3.5, Gemini 1.5, DeepSeek-V3):** When evaluated on benchmarks lacking explicit causal guidance (like the baseline CounterBench or unprompted InterveneBench), these models largely **fail** to consistently distinguish observational from interventional distributions [cite: 30, 34]. They are susceptible to collider bias, struggle with backdoor path identification, and heavily conflate \(P(Y|X)\) with \(P(Y|do(X))\) when variables are stripped of commonsense context [cite: 14, 31].
2.  **Prompt-Augmented LLMs (CausalCoT, G²-Reasoner):** Implementing chain-of-thought tailored for causality provides marginal to moderate improvements. Models begin to recognize interventions, but remain fragile and sensitive to prompt phrasing and variable naming [cite: 5, 11, 30].
3.  **Algorithmic and Multi-Agent Frameworks (CoIn, STRIDES):** When LLMs are embedded in explicit scaffolding that forces them to act as causal agents—separating abduction, intervention, and prediction (CoIn), or dividing tasks among specialized agents (STRIDES)—they successfully distinguish seeing from doing, reaching near-expert accuracies on complex benchmarks [cite: 32, 34].
4.  **Mechanistically Probed LLMs (HDMI, CIKA/ICP):** The most definitive ability to distinguish observational from interventional states comes not from standard model prompting, but from internal architectural probing. The **Interventional Capability Probe** proves that LLMs *do* possess the latent capacity to separate confounding variables via the backdoor criterion. When a frozen 7B model is utilized as its own interventional simulator via CIKA, it objectively separates observational correlations from interventional causations, outperforming massively larger standard models like o1-mini [cite: 25, 26, 27].

## Future Directions and the Path to AGI

The trajectory of research from CRASS and CausalGym in 2024 to CounterBench, InterveneBench, and Pearl-tier probes in 2026 highlights a definitive maturation in artificial intelligence evaluation. The AI community has realized that maximizing parameters and relying on next-token prediction is insufficient for reaching the pinnacle of Pearl's hierarchy [cite: 1, 25]. 

Future research is heavily indexing on multi-agent systems and algorithmic wrappers (like CoIn) to explicitly structure the latent reasoning power of LLMs [cite: 32, 34]. Furthermore, mechanistic techniques like HDMI and ICP suggest that future models might natively integrate *do*-calculus into their attention mechanisms, effectively building a causal simulator directly into the neural architecture [cite: 23, 25]. Until then, benchmarks like CounterBench and InterveneBench will serve as the rigorous gatekeepers, ensuring that the transition from statistical parrots to genuine causal reasoning agents is measured, verified, and fundamentally rooted in the laws of causality.

**Sources:**
1. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjh-UpI-Ffm42aSd9i5jHKEisn3EUApRg4ng-tkDCh-3UZ0DTJT-p53xP1gruf3DRXD_c_MvsHqcX4gJ1T1gsaDo5wjXrZ7DF54U0JRCwDjfbm6Gj8OjeySYl6UXYM5s6cUD50NOyizGhMvDUAyRmE0DFKBWACEMudQ-o2CTTwmC_-7Ozmhs5cDRIwkQ==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl4rprFuRsTMrlzy6P3FDLRUcfhOVenGx51I2tcdwLXXvwRRiR7WjWaT48NTvvGryPyyrd7e_cErdriPiE3vGDWJrd0azr40v9HWKHMHIZBU6CE8KmbP1LjA==)
3. [note.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2s0sdlEmYfI_CRqpibetv0v8eoiSi6X9DimvOI_5b0Gu8Jit51-ZpJlN3hnNROW-aisqFUDjIKzWl7RRhC-bYqE_ZDVM4paM8el48WPuFsn1o-jhS74vbQqK8YAcPCv3BC0s=)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYd1d12KLZ5vDzVqzuK4GqSuNl9-dgPBlwD4eiA6Uxp-eyXABAKywtV1Mvns6aQQthakd6TIbuGQSMvXvHLu_Ppl1aW2AGbLqE4v69LwnImJp8W8ToasMwaT5ohwOgG0i556kpMxfYuA60)
5. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESi-xGeiMbzH82p7lpX7AAB3R0dt658F7PTi71I2eVdpyjq2aplYulswVxe5PgWb3f6RBkc1y28UDuBVxyYyjFyGxjryR31TKnSI1xAzyExssmcdpUB57eAui_QT1fJzkPOR0mNkO9vzPm5sOwQZXG3pwPpiRSnM9oL3SHH2CJniJUaCz2wKQaqIB5BKqoQOVcc9FAVdmX093qBSwah2zzAcNB_6SAtCg=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEk2fv1boGu6BytK5mRpSF6BlxEPXvB9uE-_lev6lvQnTLuqLk4VEif66YsCaVdHWik5BOSmK9iG7sT7DqlwIiAgFtxJQmS76H0fjQ9Q_dC-wl0fcWULSEqzA==)
7. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHnTuUXzyxVpUM_ODfkoET01XjGWJQfJDNPdkPGSAFy4_tE-9pAwtyU57eouOdxooDz9qhGdiL33gXtx1VoWC79TQdtmxrqMKA-vYcXb3RWtfPoGwcQM2Pt4MkXzcjBaIGDiLAJSB0hDT3euRe)
8. [fabiandablander.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6cD5bkVnANTTPvpeKzqjTkEYmOYkMKCV6bdkMmmOIcvoEmTQBjzMl8odDZj9coTRu-3dUEZiRTet9Y-lUdEVAhqLy9GvLgHFuPnDScjSzq6W6IF31aJczQ9CctD2mDnIK9sCqDGCP_mY=)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3DO-YAo2_ciOzFto-3nhxZD8HQ0xQbhCXbyOIVCtj6N4EzGz46KKmO52Td1sxkbxq04MSMk3BOtLLZHNV3J5ogfEXlhVbZDP15qPe5Z4EqPAsn9vyVfh2JVXdtylQPWunC8qy9-5H8M1neLj1GZKfm36DvIwMzWWIszVDRf1Aqw34F1s_EV1xHqE=)
10. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFW73MOb6J1LEg4TwkSkuTMSUEpPHCJQOqGTCiR2BeXM6F5jJUI7nwi_hzUI8iM3r1iLBKzWde5IcyUTnlLAPqBOr0C5W84wAwiF5_oxQENrPemGjVYxkzJXPbqAA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLD0fdDKptoeloONxqY5pQh46OT_bN2cFUGC5IdwfnMpWEX0ajCmgi7Qq8bZncFQf8cBzudaL3uM4HllEnDMKhxRx3lghLNAwl7IeE9h-X7hempBzDXqN7FQ==)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXb8HXI-cB-8OurpJSG9zs6qwvOjbJdPTf37JIhGegi4LISYnwogMJ7c0H9eHL-fCA_087Ydf4GbulUaTRHjdRBfaYjUYBEwI4vqfAqLRO5RzwNwsupoiAXoL9zZ8M)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ8uiMZbaetZNOr06b6_5Q-IQeYvtQApiPD99zPD8s3Zl-iGToETrhsLjPuGN4O0jnwqeN-SjZsiq5DPTnvpHeZ7zz4ULXBOw1zS22FwhFTehSQniI7BONqQ==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZYU6iMZu1SwBIFgF1vjhiz3XKOnI-ar2fF62kDnCjauX8kFHCPxBaHH6KODnKkU7LRj6wEGMQ0W6Ha1sqlSNzlIV8xTFzUIcS8JmJ-bLdy093TzuQBarJ42IHKdG1mgI3hrxRzGhV3bx7T-AAkAwL3AM8Xw2Np5dopcPG-rNmAsrCFm4wJfdtdc5OUzqyj7CcLLjobzftaaNfyMCDGs3hEWOpBLnPBOdQPSEj866EWacFVjDy_h7I--PuAW8Pc9GvVx77-aFHFQ==)
15. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMQ8vUiOg-HFmspayaUYzuL6lkhWhplRmKc4TnM28SmF326UzV2S7WIKQGaBN46IE_qehA0sIm_n_cQg3ZhvzOcr3PrzUbQYjPEUDzaF5JV1dYWLCct3T3kyvpjPtIOjjfLHwrCJUR3NwLsLfI3_vaoPR9RWvyl8_Z4zxW1J7EQupibdRgLbPf8OQa-4CkvSq0Wr2sWiwGCTfu6BtoxAFvu8L54WX5mZLTGAMO5EQ7dSBfgjA-aDnccRyObyuNzeBA0qUuXZTQAQ==)
16. [arize.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd3DFvxmhUiaUv8bOXbY0MP8n0xKzSC1H5aVhzGb6uLlq0cTGH8vjNVf2mCEwrhO83MWSg7wm4asFalYnAhilCcfUzR3tUCdoy0BOn3922LU0mxP3QLcvo-Q_hLKZwQrsX7EUpEi6WF9PRiKSKwFM0)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxp3gWzYnwnM9JTD7Qgm_ZldgEvMOBtgMcKa69Ut8bSPJA1iiWnNr9uDwDzB684UELdFTnei7a2bR6vLeSgmaST7X85rYVjL1InuLw5iUOJadPDFnv5GF7EsBmr6FS9h4M)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZQT83BH5kJIFUUvvrxXBpCLCIIZana9IVbgyOzwqPhqiTg8FochIR1zQGzokbGtVFyoqDetvzk3lBPwhNJgzvo1QVXNciLlAZOZhL2YzM98gXPeQEhw==)
19. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmyC_i0ANCszBWoflPlnggHZhIDsZf5qxenhbTE8Q2B8Z8ntRry2yEK6TKId6wjNd-I9QwvuTsyE2rHMFLJwUCOx6od4PfEpkGomDafcY8FrLRENwbSU5vglQYnkIuvjIK)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBalaTg1a_WQvYMrbS8481RR_dUKpPvstx89jiRwhlvFwAt16gnDet7tWmxo8XFccLzv9ltTuTebkKJcPCTH6E70e140l4_wM8IuRPzEkuxM70M5XeHQ==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGufcUEFGNgm0FabPtoQNv9QGSXjCffuod5YlYbFvUQ1S0pCj1M1kIHQr0GSRQAY4wVIbA1sGMV6Spk9ft-VoES4XoPWNZHpboHyzmQZH-LcfglUGer-FAzIQ==)
22. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvcnawPStNFYkZtnkO2BZ5loKO7Yuqx_pWzSBL0vCJLfg8o7NvoCmQ3H9TWxTGl-ppveDqIaWtdTPvywz5BAqSe1XEcvyLqY2SqyQcVRgCoN5Oek3Art-4yyEgpK2CygVA11be)
23. [aissential.tech](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwXDHKjETiGIGR3q6WjowYdYnjG5S-Ewv0MjXRPFagSBFOXQq-HG1NXPIdTIJBSjFQEI8GLYIA-fGet77yKXZPSD5Dhxo9jUKn55k0wDnwxzELza-x4xgdaYP_qTpStpuPgo8SCgh2T5nuNf8nkT6AD-THd3tH0TdgVbc=)
24. [arxiv-troller.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPkrEbhZ2NDATBX5K323F8N8TcypJDVahvMJK7Nw_ikmjXKGotYmmfeYrjVbwLo7aeKsGS0DZRiLJezFRryOcv1ICoN5Ykhb9Ctp6LYUcWlzPQEEzSBX_6PhBWokgD0iNIK-UI)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLVQrDiXUIMEbo80JDl-GDlAln5BQOwgtdZemK0ZV7AU48XTPUd-cLLaHXUUl-q8WMn3lU0iddS55q96kLzNPsAqc-3tFU-LpbF2M9tFKH5wb3pQ99TTpHJA==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg9RZ2VHsmqWW8ofSJMplxElOvKycVGPoxtpRiDTDxQatjtGwujNFgp25fJ0qWpNvXVt8bWkf57PC7heVgaWfoTUYQKWTTJ-eWlYj2ylWzMQ5yA1EB0Q==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3VbI9x-rzW-kQpIbEkm8zKDpeZW11JUvCrzmVD53faX5-vhdC0lLp5zJvN_8-mjSoESY8BoEUlBTWOsRJQ4YZz2XC-PkuBkCTo51T5BGV6kEyrjqsCw==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwlAptNSQSGn5y01bLx7zxhknwPbH53lr0cA81mFfDiSGnNERv2Abd_u8dFqY4GR9JNOVyO0bTCDPm9qa6g0HGWHI6SOBOcrNqQwnCW26FeDaIHFjZjNHwWe55qug4yufRZGt1P6SqAU1PTbzjOZN9wK_EV3xHst80FGalheQTqELbnGo0U7KBYQs99VGc3C04WwqBTu4ogKIH9JtNkO0bfZ3z0eEXnXbvCxk4rFBrdO27eyr1W9pjuAWlMMKuKfd_)
29. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLQFpJP6O-JyEmAknrxeIGKgiqXTcuHCZnQTtN4qbNajmDgJwZe7CByEzOCbXuh6rY_HhBxf7YT6TtOxlH5o2AqKMJxNeJjVRC2lpID_PjVSzRUB1jlCfXi2nbH9hv507RDUzcQq8=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0tmBAa1dL2of5lDNz4AgInZFMaAk8CWeL_wjyDSZbLS0FUie_Sab_HmmnLjyozvvd7Dls7pZYQdj34PYzpv5Mf31X_kTtzDZTkRUa0hsw7blUtUgZn-j7jw==)
31. [takara.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbDooc_HavOavdz4zwoezUiPgpewfwDlAsBkZWA-jHBT4LNTP3KwNBqZ5vx0SKU8gFUjatIH9xbFAyfU7lF1KjndTKGY9Yu3OIaNNqtilDgd9urBXoesJf2w==)
32. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVugFUK8Ac9SPNJJoaZhsBlGiA5moAphXGPeBguNwqps241FE744pzwpTKAevKzSo8-z9TvnTyQMHmlhBCSmxol6Wp3j5OCBNLsaKEBILFSMut5KhioQ5MvZFMU-FNJ5wLYG1AU5OaFKf4wJpAtjiL7oU=)
33. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhkdbSXrHlJTovp3WEuhDd3acEhOFY0_5eJBWdPPZyeheUgbctp96uFDl-6QUslUxkJU0-jYS132YHxZ3J3vRCacXG4sRohkVrUdfjsOUAmsm3u8nFaLrmAf38zl3jgXoDLFmjNixrGyYebX87n-nKqyGOycEdNTO2vDnRUORTFtRK1ARr8Y4fqYNOyPWPa3zJYxwyapx_OMxRKXab6YlQDR2TYlbsOckNVSsgqjeq-gtCFfvB9mdmxIWFW6cCKQqWOA==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl4J__aEjyhdpMxEzjeLWS9CpBG4heZpjJXRoeHnIxjGocKGwHJJUpgGsjCcaDZoIXPXAvyRuJYdU9sysuI8n5MJgbp-qPMHl_lNuQYmY3zN0t64ZiB0GZ7w==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGz2UYOwxEaL5p_p6WU4NUs2Zqs3Qy1y8QhbhMujGeSsqf5Rr6V2VSMzROV7pvsqR_Z6FoIpogmWsdG5u9QT6vUSTuU3TUqgfxNnPSeYz91KL0DFzQnvg==)
36. [catalyzex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJCfzLP5fqfTXRXW4acJTMDxaBttPmJNWNxAgeSzv9U_akMqCXDZS6fYR2mok8DTbPvEVa-YjvsduiF8CL7d6g3crgQCD2xco4HhYvwDedZ4K2xBAgbxSraAtiAaN4GG5AxlHq)
37. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrfttssyVQbA0LT489jby3glp239QqYls12pYFeRecqBc-wKpe4xxJbCzO1QERmFQell6iLMR26rhNSe1FuX3uCv6Yp6Tps7WarY3W_c3MaLY8jcq7S0e3QDWG)

