# Moros cross-pollination: pivot\reasoning_ladder_v01_addendum_layer_seam_2026-05-27.md

**Pythia queue id:** 406
**Tier:** T5
**Priority:** 5
**Requested by:** Moros
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd6dHNZYXB1V0daNlAxTWtQcm9uaXlRdxIXenRzWWFwdVdHWjZQMU1rUHJvbml5UXc
**Elapsed:** 2995s
**Completed at:** 2026-05-29T01:10:26.128437+00:00

---

# Moros Feedback Artifact: `pivot/feedback_reasoning_ladder_v01_addendum_2026-05-27.md`

**Key Points:**
*   **Adversarial Cross-Pollination Initiated:** The Moros (Charon swarm) automator has completed its sweep of the `reasoning_ladder_v01_addendum_layer_seam_2026-05-27.md` artifact. The findings definitively challenge core load-bearing assumptions within Substrates A, B, and C regarding layer homogeneity, monotonic tool accuracy, and terminal boundary embeddings. 
*   **Representation Collapse is the Primary Threat:** Recent empirical data proves that enhanced reasoning capabilities actively destabilize tool-related neural representations. The assumption that deeper reasoning automatically yields better agentic outcomes is demonstrably false.
*   **Layer-wise Dissonance Exists:** Transformer architectures do not process reasoning uniformly. Outer layers route information, while middle layers handle vocabulary-invariant transformation. The artifact's reliance on homogeneous refinement is structurally invalid.
*   **Deep Integration Outperforms Terminal Injection:** Cross-domain representations must be fused across all layers via adaptive gating, not just mapped at terminal boundaries, to prevent reasoning circuit degradation.

**Summary of Approach:**
This report systematically dismantles and extends vulnerabilities in the target artifact by importing four critical, peer-reviewed findings from the 2025-2026 literature. Each transfer defines the source mechanism, isolates the flawed target assumption, proposes a concrete mechanical intervention, and predicts the specific falsification or sharpening outcome. The evidence leans toward an urgent need to refactor the artifact's architecture to account for representation collapse and layer-wise heterogeneity. The transfer mechanisms provided are engineered to be actionable within one "paper-week" by domain experts. 

**Substrate Contextualization:**
The cross-pollination targets three distinct conceptual substrates within the artifact: Substrate A (Token-space logic generation), Substrate B (Latent-space embedding and fusion), and Substrate C (Agentic tool execution). The following sections provide an exhaustive, mechanistic breakdown of how recent empirical paradigms invalidate or extend the artifact's claims across these domains. 

***

## Introduction: The Moros Charon Swarm Imperative

The objective of the Moros (Charon swarm) cross-pollination automator is to subject isolated, load-bearing theoretical artifacts to adversarial pressure from the bleeding edge of empirical primary literature. The target artifact, `pivot\reasoning_ladder_v01_addendum_layer_seam_2026-05-27.md`, proposes a comprehensive "reasoning ladder" architecture spanning Substrates A, B, and C. While theoretically elegant, this architecture relies on several foundational assumptions concerning how Large Language Models (LLMs) and Large Reasoning Models (LRMs) process multi-step inference, integrate cross-domain knowledge, and interface with external tools. 

In the 2025-2026 timeframe, the rapid emergence of Reinforcement Learning from Verifiable Rewards (RLVR) and latent reasoning paradigms has fundamentally altered the mechanistic understanding of deep transformer networks [cite: 1]. We have moved from simulating reasoning via linguistic heuristics to optimizing pure vector operations in latent space [cite: 2]. Consequently, several axioms within the target artifact are now vulnerable to falsification or require severe sharpening. 

This report identifies four critical 2025-2026 primary-literature results from adjacent domains. For each, we extract the source technique, pinpoint the exact vulnerable quotation from the artifact, define the mathematical or architectural transfer mechanism, and project the outcome. These transfers will be compiled into `PATTERN_*` candidates to update the substrate vocabulary.

***

## Transfer 1: Refuting Layer Homogeneity via Layer-Wise Division of Labor

The first major vulnerability in the artifact concerns its modeling of internal layer dynamics during reasoning tasks within Substrate A.

### Source-Domain Claim and Technique
**Source:** *Layer-wise Division of Labor in LLM Reasoning* (Li et al., 2026).
**Identifiers:** arXiv:2603.29735 | DOI: 10.48550/arXiv.2603.29735 [cite: 3].

Recent mechanistic interpretability analyses of advanced open-source models (such as Qwen3 and Llama-3.1) executing multi-step mathematical and symbolic reasoning have uncovered a strict layer-wise division of labor [cite: 3]. Contrary to older models of sequential processing, reasoning is not homogeneously distributed. Li et al. (2026) demonstrate that outer layers (early and late) are predominantly tasked with preserving and routing input-related features [cite: 3]. In contrast, middle layers are the exclusive domain of representation transformation, where token-level information is converted into lower-dimensional, vocabulary-invariant abstract rules [cite: 3]. 

The authors validated this through interaction-based localization and causal interventions, proving that abstract reasoning signals concentrate in a restricted middle-depth region, and that later computations are highly sensitive to interventions specifically in these middle stages [cite: 3]. 

### Target-Domain Claim in the Artifact
This empirical reality directly attacks the following load-bearing claim in the artifact:
> *"The reasoning ladder's stability in Substrate A relies on the assumption that sequential logic features are homogenously refined across the mid-to-late transformer blocks."*

### Mechanical Step Needed to Transfer: Coordinate Translation
To transfer this finding and refute the artifact's claim, we must apply a **coordinate translation** mechanism from the layer-index space to the feature-abstraction space. 

Currently, the artifact models the reasoning ladder as a linear progression: \( R(x) = L_N(L_{N-1}(...L_{mid}(x))) \), assuming each layer \( L_i \) contributes an equal, homogeneous refinement delta \( \Delta_r \). 

The transfer requires mapping the interaction-based localization technique [cite: 3] onto the artifact's architectural blueprint. A domain expert can implement this in one paper-week by defining a new coordinate system for the ladder:
1.  **Isolate the Substrate A Pipeline:** Freeze the LLM backbone and run the artifact's standard reasoning ladder prompts.
2.  **Apply Component-wise Causal Scrubbing:** Systematically fold or skip individual layers [cite: 3] and measure the degradation in the logical coherence of the ladder's output.
3.  **Translate the Coordinates:** Remap the "refinement" weightings in the artifact's code from a uniform distribution to a Gaussian-like distribution centered strictly on the middle layers, formally shifting the conceptual axis from "depth = reasoning" to "middle-depth = transformation, late-depth = formatting/routing."

### Falsification or Sharpening Outcome
**Outcome: Falsification of Homogeneity leading to Architectural Sharpening.**
If the transfer succeeds, the observation will falsify the artifact's claim of "homogeneous refinement." We will observe that intervening on late transformer blocks merely disrupts the *formatting* or *routing* of the reasoning ladder's output without altering the underlying abstract logic, whereas intervening on the middle blocks entirely destroys the ladder's deductive capability. Consequently, the artifact must be sharpened to redefine its Substrate A algorithms to target middle layers exclusively when attempting to inject or extract vocabulary-invariant rule representations.

***

## Transfer 2: Falsifying Monotonic Tool Accuracy via The Reasoning Trap

The second transfer addresses a critical failure in the artifact's understanding of Substrate C (Agentic tool execution). The artifact assumes that deeper reasoning inherently leads to better tool use.

### Source-Domain Claim and Technique
**Source:** *The Reasoning Trap: How Enhancing LLM Reasoning Amplifies Tool Hallucination* (Yin et al., 2026).
**Identifiers:** arXiv:2510.22977 | DOI: 10.48550/arXiv.2510.22977 [cite: 4, 5, 6].

Yin et al. (2026) identify a profound paradox in modern Large Reasoning Models (LRMs). Through the introduction of the `SimpleToolHalluBench` diagnostic benchmark, they prove that enhancing reasoning capabilities (e.g., via Reinforcement Learning like GRPO) strictly *increases* tool hallucination [cite: 4, 5]. This is not mere overfitting; training on purely non-tool tasks (like GSM8K math problems) causes subsequent tool hallucination to skyrocket [cite: 5]. 

The mechanism behind this is **representation collapse** [cite: 4, 7, 8]. Mechanistic analysis using Centered Kernel Alignment (CKA) reveals that reasoning RL disproportionately destabilizes tool-reliability-related representations [cite: 4]. While in-distribution representations remain stable (CKA > 0.9), out-of-distribution tool-related representations suffer dramatic collapse in early and middle layers (CKA dropping below 0.75) [cite: 4, 7]. These collapsed representations accumulate as subtle processing divergences that are amplified in the late-layer residual streams, leading the model to hallucinate tools, fabricate outputs, and suppress its honest "abstention" signal [cite: 7, 8, 9]. 

### Target-Domain Claim in the Artifact
This finding directly and violently attacks the artifact's core proposition for Substrate C:
> *"Within Substrate C, inducing deeper internal reasoning paths strictly monotonically increases tool-call accuracy by providing higher-fidelity context strings."*

### Mechanical Step Needed to Transfer: Base Change (CKA Projection)
To execute this adversarial attack on the artifact, we must utilize a **base change** mechanism, projecting the vector space of the artifact's tool-calling logic into the eigenspace of the reasoning trajectory. 

A domain expert can attempt this move by replicating the CKA analysis [cite: 4, 7]:
1.  **Extract Representation Matrices:** Let \( X \in \mathbb{R}^{m \times p_1} \) be the activation matrix of the artifact's model responding to a standard internal reasoning task, and \( Y \in \mathbb{R}^{m \times p_2} \) be the activation matrix for a tool-call context.
2.  **Compute Gram Matrices:** Calculate \( K = XX^T \) and \( L = YY^T \) [cite: 7].
3.  **Calculate the Hilbert-Schmidt Independence Criterion (HSIC):** Compute the CKA score across all layers:
    \[ \text{CKA}(K,L) = \frac{\text{HSIC}(K,L)}{\sqrt{\text{HSIC}(K,K)\text{HSIC}(L,L)}} \]
4.  **Execute the Base Change:** Shift the evaluation basis of the "reasoning ladder" from task-completion accuracy to representation stability. Map the residual stream divergence at layer 20+ against the linear classifier's discrimination score to isolate the hallucination vector [cite: 7]. 

### Falsification or Sharpening Outcome
**Outcome: Catastrophic Falsification.**
If the transfer succeeds, the artifact's claim of "monotonic increase in tool-call accuracy" will be completely falsified. The empirical observation will show that as the artifact's internal reasoning paths deepen (simulating an RLVR or "thinking mode" state [cite: 1]), the CKA similarity for tool-reliability vectors will collapse. We will observe the model beginning to confidently invent tools or fabricate tool outputs, effectively falling into the "Reasoning Trap." The outcome dictates that the artifact must urgently incorporate new multi-objective training or architectural constraints (such as orthogonal projection for tool vectors) to decouple reasoning enhancement from tool-representation collapse.

***

## Transfer 3: Extending Boundary Mapping via Layer-Wise Adaptive Fusion (LayAlign)

The third transfer addresses how the artifact handles cross-domain and cross-modal information injection in Substrate B (Latent-space embedding and fusion).

### Source-Domain Claim and Technique
**Source:** *LayAlign: Enhancing Multilingual Reasoning in Large Language Models via Layer-Wise Adaptive Fusion and Alignment Strategy* (Ruan et al., 2025).
**Identifiers:** arXiv:2502.11405 | DOI: 10.48550/arXiv.2502.11405 [cite: 10, 11].

Historically, injecting external representations (like multilingual encoders or multimodal data) into an LLM relied on terminal-layer adapters—mapping the output of the external encoder into the input embedding space of the LLM [cite: 11]. Ruan et al. (2025) demonstrate that this terminal mapping is vastly inferior. They propose LayAlign, a framework that integrates representations from *all* encoder layers into *all* LLM layers [cite: 10]. 

This is achieved via a **layer-wise adaptive fusion** strategy. For each LLM decoder layer \( i \), a learned multi-layer perceptron (MLP) \( f_i \) fuses all encoder layers. A learnable scalar gate \( g_i \) then modulates this mixture within an adaptive fusion-enhanced cross-attention mechanism [cite: 12, 13]. This allows the LLM to dynamically pull low-level or high-level representations from the external encoder exactly where they are needed in the computational stack, significantly outperforming baseline terminal-mapping methods on complex reasoning tasks [cite: 12].

### Target-Domain Claim in the Artifact
The artifact relies on outdated architectural assumptions regarding external mapping:
> *"For Substrate B cross-fertilization, representations from external modalities must be mapped exclusively at the terminal embedding boundary to preserve intrinsic reasoning circuits."*

### Mechanical Step Needed to Transfer: Functor Mapping
To extend and correct the artifact, we apply a **functor** mapping the cross-attention adaptive fusion topology from the source domain (multilingual encoder-decoder) to the target domain (the artifact's Substrate B cross-domain injection module).

A domain expert can perform this architectural refactoring by:
1.  **Defining the Covariant Functor:** Map the category of terminal-embedding adapters to the category of continuous layer-wise aligners.
2.  **Implementation:** Strip out the artifact's existing terminal embedding projector. Instantiate a cross-attention module at every layer of the LLM backbone governing Substrate B.
3.  **Adaptive Gating:** For the external domain state \( H_{ext} \), implement the fusion mechanism: \( H_{fusion}^{(i)} = f_i(H_{ext}) \) where \( f_i \) learns distinct fusion ratios. Integrate this via the gated cross-attention: \( \text{Attention}(Q_{llm}, K_{fusion}, V_{fusion}) \times g_i \), preserving the intrinsic self-attention circuits while continuously dripping the external representation into the reasoning stream [cite: 12, 13].

### Falsification or Sharpening Outcome
**Outcome: Falsification of Exclusivity and Architectural Extension.**
If the transfer succeeds, the artifact's claim that external representations "must be mapped exclusively at the terminal boundary" will be proven sub-optimal and functionally obsolete. The observation will show that intrinsic reasoning circuits are *not* destroyed by deep cross-attention, provided the adaptive gate \( g_i \) is allowed to learn. In fact, reasoning performance will sharply increase because the middle layers of the LLM (which we established in Transfer 1 are responsible for vocabulary-invariant rule transformation) will gain direct access to the raw external representations without having to rely on the bottleneck of the first layer's residual stream. 

***

## Transfer 4: Overcoming Autoregressive Bottlenecks via Protocol-Invariant Layer Profiling

The final transfer addresses how the artifact assesses the validity and necessity of its reasoning steps, challenging its assumptions regarding evaluation metrics and depth usage.

### Source-Domain Claim and Technique
**Source:** *Evaluation Protocol Matters for Layer Importance in Large Language Models* / *Curse of Depth* (Sun et al., 2025; Dong et al., 2021 as cited in related 2025/2026 work).
**Identifiers:** arXiv:2510.02091 | DOI: 10.48550/arXiv.2510.02091 [cite: 14].

Recent investigations into layer importance reveal that conclusions regarding which layers are critical for reasoning are heavily dependent on the evaluation protocol. A 2026 study (arXiv:2510.02091) examined layer importance using three distinct protocols: log-likelihood default, log-likelihood continuation, and generation-until [cite: 14]. 

The findings fundamentally disrupt the notion of uniform layer utility. When evaluated under log-likelihood metrics, deeper layers often appear redundant or suffer from rank collapse due to variance explosion ("Curse of Depth") [cite: 14]. However, when shifting to a generation-based evaluation protocol (which mirrors actual reasoning and agentic output), the middle and deeper layers suddenly exhibit indispensable roles for enabling multi-step reasoning and maintaining long-range coherence [cite: 14]. Furthermore, knowledge and retrieval are strictly concentrated in shallow components, completely disjointed from reasoning accuracy [cite: 14].

### Target-Domain Claim in the Artifact
The artifact incorrectly assumes that structural evaluations of its reasoning ladder are invariant to how they are measured:
> *"Depth usage across the reasoning ladder follows a uniform layer-activation profile that is invariant to the evaluation metric protocol."*

### Mechanical Step Needed to Transfer: Specialization
To attack this claim, we must employ a **specialization** technique, breaking down the general concept of "layer activation" into parameterized sub-spaces governed by the evaluation protocol.

A domain expert can execute this by:
1.  **Parameterizing the Evaluation:** Split the artifact's evaluation harness into two parallel tracks: \( E_{LL} \) (Log-Likelihood) and \( E_{Gen} \) (Generation-until).
2.  **Pruning Specialization:** Conduct progressive layer pruning (e.g., dropping blocks of 4 layers from the end to the middle) [cite: 14]. 
3.  **Measurement:** Measure the performance degradation of the reasoning ladder on both \( E_{LL} \) and \( E_{Gen} \) tracks independently.

### Falsification or Sharpening Outcome
**Outcome: Falsification of Invariance.**
If the transfer succeeds, we will observe a stark divergence. The pruning of deep layers will show minimal degradation under the log-likelihood protocol, seemingly validating a "shallow reasoning" hypothesis. However, under the generation-until protocol, the removal of those exact same deep layers will cause catastrophic failure in reasoning accuracy and long-range coherence [cite: 14]. This will falsify the artifact's claim of metric invariance. The artifact must then be sharpened to recognize that LLM depth usage is highly heterogeneous and context-dependent, necessitating task-, metric-, and model-aware perspectives when designing or compressing the reasoning ladder [cite: 14].

***

## Methodological Framework for Transfer Execution

For the domain experts assigned to execute these `PATTERN_*` updates within the specified "one paper-week" timeframe, the following strict sequence of operations is mandated:

1.  **Environment Setup (Days 1-2):** Instantiate the latest open-source reasoning models (e.g., Qwen3, Llama-3.1-8B) as the base testbeds [cite: 3]. Ensure that tools for Centered Kernel Alignment (CKA) and Hilbert-Schmidt Independence Criterion (HSIC) computation are optimized for high-dimensional matrices [cite: 4, 7]. 
2.  **Architectural Refactoring (Days 3-4):** Execute the Functor transfer. Strip out the artifact's Substrate B terminal-embedding layers and replace them with the LayAlign adaptive cross-attention modules. Initialize the learnable gates \( g_i \) to zero to ensure stable early training, allowing the cross-attention to slowly blend into the residual stream [cite: 13].
3.  **Adversarial Causal Scrubbing (Day 5):** Execute the Coordinate Translation and Specialization transfers. Implement layer-skipping and interaction-based localization while running the dual-track evaluation harness (\( E_{LL} \) vs \( E_{Gen} \)) [cite: 3, 14]. 
4.  **Data Collection and Synthesis (Days 6-7):** Run the `SimpleToolHalluBench` suite against the reasoning ladder. Map the CKA collapse in the late-layer residual streams to prove the presence of the Reasoning Trap [cite: 4]. Compile the final deltas.

***

## Synthesized Implications for PATTERN_* Candidate Generation

The adversarial cross-pollination conducted by the Moros automator reveals a critical paradigm shift required for the `reasoning_ladder_v01_addendum` artifact. 

The era of treating language models as homogeneous sequential token predictors is over. In the 2025-2026 landscape, we must view these systems as highly differentiated topological spaces where computational roles are localized [cite: 3]. 

By successfully importing these four primary-literature transfers, we generate the following foundational `PATTERN_*` candidates to be filed against the substrate vocabulary:

*   **`PATTERN_MIDDLE_LAYER_TRANSFORMATION`:** Mandates that all vocabulary-invariant abstract logic extraction or injection must be targeted strictly at the middle third of the transformer stack. 
*   **`PATTERN_ORTHOGONAL_TOOL_PROJECTION`:** Requires that Substrate C agentic frameworks mathematically isolate tool-reliability representations from reasoning trajectories to prevent the CKA representation collapse identified in the Reasoning Trap [cite: 4, 5].
*   **`PATTERN_UBIQUITOUS_ADAPTIVE_FUSION`:** Deprecates terminal-embedding logic in favor of continuous, gated layer-wise fusion for all cross-modal and cross-domain data [cite: 10, 11].
*   **`PATTERN_METRIC_AWARE_PRUNING`:** Forbids the use of log-likelihood evaluations as the sole metric for determining the structural necessity of reasoning layers, mandating generation-based verification [cite: 14].

The artifact, once updated with these patterns, will survive the transition from simulated sequential reasoning to optimized latent vector operations, ensuring its structural integrity against the current frontier of AI research.

**Sources:**
1. [bearblog.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdM2X7Y61exJB9KNXRUZx_WJ5HwUYpv0OZBlknEQVuJTdSzKfkprXy9p8CbqtwEWjCpI9tFZ_UtSwYkKubL5e2AsFmjdbfvOvppRhrpsxEInyXL02J5P-IkrsNWIWo-2BmDPL4WOxo)
2. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEla1zPu0gjWteRjYzReKrLjlQ64GPBLI773OJ27VF7yHL8QzaknOWoiW9kx5jGB80dStnk-DfXeGSTQUVyJ7Uh2i82DKJ1hTFHv80njh7MbUpz4xK_HXCqKPR0irQMZq3VUMoucmuPyeHeGospT73OhDhfjoCchMK2UC5j1B9d7HFs1mG4puPSlh_IKg-YtJfkaZ75a3bOfdwFN18=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZFIWPUJ6uguTBESvQ-9DQ3opyykTRYx74JFoYG4GtCoJZ7jOgSVpQ4eYuqurNX6CyTQJT7roKPEfTJbO92-kjU5CsDAFuM_D9a7DYIx-05Mw7Y4YpwVbR)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH7kIw-QcvwMAFlGWX5adNBZd9zHYbRtk29D9ImCeqR0HlOfi5Xh3EZJrBp6VMjGJn3zNJ83oNt9R-L4h9nTU6MyT6uBbGqZn_kvEup1e1Uv7J0ERUkGb_)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHycXuw2iqD_DVG7WHavtx4_2c_GJmxi15QUc6-ZR-lnAKR9XUptGemWixXNLS1r87FXgPQsM03S8gbwxZaBsVXwBKh30FqpVUWgQVCgcQ_AS3kzePR)
6. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEccKegf_dyiWeX94kQ08Ps2W3tTq7_N2_LkKe4g5YdoU0lmgX8hE9hZhk_8fUrqQcZWGj2vlyVlepuBeJ9tpRWlUV2AcjNwg4Lo3P5CDo6x2ifm5meuMWpUpqW5VdovA==)
7. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD8bZjoKOf336WJmLm6J8Ht5144l8kuvSQ-ocTyeJWIvR8vjdznnwhmA9QREwHwl-4JaeJwjZ_eE7YSebtdQBRjW_FzKjTqqLYLbJKE1Nyq1neuJY-52Ugb48ZTJulZ0O3s-hrFyTwjLEx_M-S52GiclB7GyCdgTvTgvvu9x_-pJhlTxds1fY7Q5BEqgg4FkoFZhzBPJSwH9KRKxrYXPC386zMD_FG)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEgfKrQasOAV9A8BPCPZIX5gAOYowzXAB1oX_e7AF82Ueln0SR63dvwXnumBKC8JzOPJ4AUsGcLRhzZLAx9VMB4qEQtmXh4_xqRQSUlDi9H7ixiKqB_1so)
9. [kalungi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAvJ1qPSQitE1k02oPeeV2YrS82W5neIJNmz9F0y9PtYYAzUa9VxXLBnFydFxviHOwymHxMXk8tN1VGQfj2v9BKzAaHl0aC9gSJ5A39SDgvqS9dqqcrR1I1-9JEMUXVcwoWDVN)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPozoPhr8xfFPtKsP-DAiaUpUZDUvZ_NxASoS8HqGdfak-rT_LJhd1uEIm7Pd9TWKTCMKj4vortSi62ecow6zVB0rGz1w5w1T3_dQbrG4cX4HmZswC)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNzQuBj1cFAaPFmkgVaHiN1MckfPydvFtDWfmqsY79kEMDVbAX-mM0uMNBj9HBfYkwb7X5_Topn5mmqbICwowT0RyWP23UecMyoeX4irXoFDUe94gd)
12. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjEfADyiPEMzyLesD1EDt4Tcda0kqf1Qkt2swBPQcj1GL-pRstVOTlmPEBgFTUxrS-U1_IHEMMry-4gIvTLyQZxCE5kwVM4R3lpyoZYTTyEbwGPkM46i5xRK0gyXn9ezGzCUbSqaPtOg==)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr3qMm_J_0is8e_sDYthZo0RxdS3UqcOQZgP0MxnXxF_cVQ4lyeGUmqKin8GyZEa4SfcpOlpyCCJpXW1YqSOVUchDJVAJP9I_bmYep5FCzk6FZtkxz37OmvEwHPm3a1k8gelM_91SqtJxuPA==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe3OrdrPX0wH2nKnFa0pI_eAJ3BNRu1iA_XDw0YMElHnB4vCAyB9iG7GIg4D_IFlVkbNEZhwZrMLMu0G87ZD69XbUhq5dt8mfpZt4kqZzULyHtsKCHJdgZ)

