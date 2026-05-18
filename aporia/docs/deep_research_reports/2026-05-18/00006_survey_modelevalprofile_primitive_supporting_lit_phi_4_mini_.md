# Survey ModelEvalProfile primitive supporting lit (Phi-4-Mini SambaY + Qwen2.5-Math + Llemma-7B)

**Pythia queue id:** 6
**Tier:** 1
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdablFMYXEzSUhyM04tc0FQbjY3YThBdxIXWm5RTGFxM0lIcjNOLXNBUG42N2E4QXc
**Elapsed:** 185s
**Completed at:** 2026-05-18T20:22:56.123607+00:00

---

# Survey of Model Evaluation Profiles: An Analysis of Phi-4-Mini SambaY, Qwen2.5-Math, and Llemma-7B

**Key Points**
*   **Architectural Diversity in Small Models**: Research suggests that sub-10 billion parameter models are diverging into specialized architectures. The Phi-4-Mini model family successfully explores hybrid state-space/transformer architectures (SambaY) to drastically reduce memory bottlenecks during long-context generation.
*   **Mathematical Reasoning Paradigms**: The evidence strongly leans toward the necessity of specialized training pipelines for mathematical reasoning. Qwen2.5-Math demonstrates that combining Chain-of-Thought (CoT) with Tool-Integrated Reasoning (TIR) and Process Reward Models (PRMs) yields expert-level performance, bridging the gap between open-source models and proprietary systems.
*   **Formal Theorem Proving Capabilities**: It appears highly likely that continued pre-training on specialized corpora, such as the Proof-Pile-2 used by Llemma-7B, effectively adapts code-centric language models into capable formal theorem provers without the need for extensive task-specific fine-tuning.
*   **Evaluation Methodologies**: Model evaluation primitives are shifting from simple zero-shot accuracy metrics toward comprehensive profiling that includes Best-of-N (BoN) sampling, step-by-step process evaluation (ProcessBench), and real-time computational throughput profiling.

**Evolution of Model Assessment**
The evaluation of Large Language Models (LLMs) and Small Language Models (SLMs) has transitioned from monolithic, general-purpose benchmarks to nuanced, capability-specific "profiles." This shift is driven by the realization that aggregated scores often obscure critical deficiencies in specialized domains such as mathematical reasoning, formal logic, and long-context state tracking. Comprehensive model evaluation profiles now encompass architectural efficiency, domain-specific generalization, and tooling integration.

**The Rise of Specialized Small Language Models**
As the computational costs of trillion-parameter models become prohibitive for edge and localized deployment, the AI research community has redirected significant effort toward SLMs. Models typically ranging from 1.5 to 7 billion parameters are being engineered to punch above their weight class through algorithmic innovations. By trading generalist breadth for domain-specific depth, these models achieve state-of-the-art results in rigorous fields like mathematics and logical inference, often matching or outperforming their significantly larger predecessors.

**Scope of the Survey**
This report synthesizes the evaluation profiles of three distinct, state-of-the-art architectures: the hybrid state-space model **Phi-4-Mini SambaY** (specifically the *Phi-4-mini-flash-reasoning* variant), the dense reasoning specialist **Qwen2.5-Math**, and the formal mathematics proof assistant **Llemma-7B**. By analyzing their architectural innovations, training methodologies, and empirical benchmark performance, this survey provides an exhaustive primitive for evaluating modern, specialized language models.

***

## 1. Introduction to Model Evaluation Primitives

In the contemporary landscape of artificial intelligence, a "Model Evaluation Profile" primitive serves as a standardized framework for assessing neural network architectures across multiple orthogonal dimensions. Historically, language models were primarily evaluated on perplexity and generalized zero-shot text completion [cite: 1]. However, as models like **Phi-4-Mini**, **Qwen2.5-Math**, and **Llemma-7B** push the boundaries of domain-specific logic, traditional metrics have proven insufficient [cite: 2]. 

A rigorous model evaluation primitive for mathematical and logical reasoning must encompass several distinct vectors:
1.  **Algorithmic and Hardware Efficiency**: Profiling the time complexity of the pre-filling stage, the memory I/O bottleneck during autoregressive decoding, and the empirical throughput (tokens per second) on standardized hardware [cite: 3, 4].
2.  **Architectural Scalability**: Measuring the "irreducible loss" utilizing power-law scaling across training FLOPs [cite: 5, 6].
3.  **Reasoning Depth and Verifiability**: Utilizing advanced benchmarking such as ProcessBench, which assesses a model's ability to identify errors in intermediate steps (Process Reward Models), rather than merely evaluating the final outcome [cite: 7].
4.  **Extensibility to Formal Verification**: Testing the model's capacity to interface with rigid computational environments, such as Python interpreters or formal theorem provers (e.g., Lean 4, Isabelle) [cite: 8, 9].

The models surveyed in this report represent the vanguard of specialized SLMs. **Phi-4-Mini SambaY** attempts to solve the $O(n^2)$ attention bottleneck for long contexts [cite: 4, 10]. **Qwen2.5-Math** focuses on data synthesis, Tool-Integrated Reasoning (TIR), and complex competition-level math [cite: 11, 12]. **Llemma-7B** bridges the gap between informal natural language mathematics and strictly formalized proof states [cite: 1, 9]. 

## 2. Evaluation Profile: Phi-4-Mini SambaY (Phi4-Mini-Flash-Reasoning)

The **Phi-4-Mini** family, developed by Microsoft, represents a significant advancement in compact language processing systems. While the standard Phi-4-Mini is a 3.8 billion-parameter dense decoder-only transformer employing Grouped-Query Attention (GQA) and fractional Rotary Position Encoding (RoPE) [cite: 13, 14], the most radical architectural evolution within this lineage is the **Phi-4-Mini-Flash-Reasoning** model, which utilizes the **SambaY** architecture [cite: 5, 15, 16].

### 2.1 Architectural Innovations: The SambaY Hybrid Decoder

The fundamental challenge in autoregressive generation for long contexts is the Key-Value (KV) cache memory bottleneck. In traditional transformers, memory and compute scale as $O(n)$ per step, making long generations prohibitively expensive [cite: 4, 10]. Alternatively, State Space Models (SSMs) like Mamba maintain a fixed-size hidden state, enabling $O(1)$ constant-memory autoregressive decoding and linear pre-filling; however, they suffer from degraded retrieval accuracy over extended contexts [cite: 4].

**SambaY** is a "decoder-hybrid-decoder" architecture that synthesizes the strengths of both paradigms [cite: 3, 4]. It eliminates the need for explicit positional encodings (such as RoPE) because the recurrent dynamics of the Samba-based self-decoder naturally encode recency and positional information without performance degradation on sequential tasks [cite: 3, 10]. 

The architecture takes its name from its Y-shaped dual-channel conditioning [cite: 4]. The core components include:
*   **Self-Decoder**: A hybrid stack alternating between Mamba SSM layers and Sliding Window Attention (SWA) [cite: 4]. It processes the input and produces two outputs: the SSM hidden state and a KV cache from the full attention layer [cite: 4].
*   **Gated Memory Unit (GMU)**: The primary novel element introduced in SambaY. The GMU facilitates efficient memory state sharing from the self-decoder to the cross-decoder [cite: 3]. It selectively reweights Samba layer outputs element-wise based on current input context, drastically reducing the memory I/O bottleneck from $O(d_{kv}N)$ to $O(d_h)$ per layer [cite: 10]. 
*   **Cross-Decoder**: By alternating cross-attention layers with GMUs, SambaY achieves up to a 10$\times$ improvement in decoding throughput compared to YOCO baselines, particularly on sequences with 2K-token prompts and 32K-token generation lengths [cite: 3, 10, 17].

Furthermore, **Phi4-Mini-Flash-Reasoning** incorporates **Differential Attention**, a mechanism designed to optimize the retrieval of contextual information while mitigating noise, enhancing the model's performance on reasoning benchmarks [cite: 5, 17, 18].

### 2.2 Training Methodology and Rollout Preference Learning

The standard Phi-4-Mini was trained on approximately 5 trillion tokens with an emphasis on high-quality, reasoning-dense synthetic data [cite: 14, 16]. For the reasoning-specific variants, Microsoft researchers proposed a systematic training recipe consisting of several key stages:

1.  **Distillation as Mid-Training**: The base SLM is trained on a diverse corpus of synthetic Chain-of-Thought (CoT) data generated by larger models (e.g., DeepSeek-R1) [cite: 19]. Only correct answers are retained via rejection sampling, and training utilizes next-token prediction with sequence packing for efficiency [cite: 19].
2.  **Supervised Fine-Tuning (SFT)**: A high-quality subset of the mid-training data, containing mathematics problems up to the college level, is used for fine-tuning in non-packing mode, teaching the model exact stopping criteria [cite: 19].
3.  **Rollout Preference Learning**: To address high variance in response lengths and vanishing gradients under uniform rewards, researchers repurposed incorrect LLM rollouts to construct a preference dataset [cite: 19]. Correct answers are classified as preferred ($y_w$), while incorrect derivations are dis-preferred ($y_l$) [cite: 19]. Direct Preference Optimization (DPO) is applied using the following loss function:

\[
\mathcal{J}_{DPO}(\pi_\theta; \pi_{ref}) = -\mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)} \right) \right]
\]

where $\pi_\theta$ is the trained policy, $\pi_{ref}$ is the reference model, and $\sigma$ is the sigmoid function [cite: 19]. This formulation ensures that the model learns stable reasoning pathways without the complexities of Proximal Policy Optimization (PPO) [cite: 19].

### 2.3 Evaluation Profile: Scaling Laws and Empirical Performance

Extensive scaling experiments demonstrate the theoretical and practical superiority of the SambaY architecture. Researchers fitted power laws against training FLOPs to measure the **irreducible loss** ($C$) [cite: 5, 6]. 

Under the $\mu P++$ parameterization (a novel combination of maximal update parameterization and Depth-$\mu P$), SambaY exhibits the lowest irreducible loss ($C = 0.58$) for FLOPs scaling compared to strong YOCO baselines [cite: 5, 18]. All tested hybrid architectures shared the same compute efficiency exponent ($b = 0.07$) [cite: 18].

#### Long-Context Retrieval and Reasoning Benchmarks
The **Phi4-Mini-Flash-Reasoning** model was rigorously evaluated on both retrieval and complex mathematical reasoning tasks. 

*   **Long-Context Retrieval**: Evaluated on RULER, Needle-in-a-Haystack, and the challenging Phonebook benchmark (PB-32K) [cite: 5, 18]. SambaY achieved superior performance, demonstrating advanced length extrapolation capabilities even with a modest SWA size of 256 [cite: 5, 18]. Ablation studies revealed a clear hierarchy: `SambaY > SambaY-MLP > SambaY-A > SambaY-AA`, indicating that the natural recency bias of SSMs is superior for retrieving contiguous local information compared to alternative memory sources [cite: 6, 18, 20].
*   **Reasoning Benchmarks**: Despite lacking specific reinforcement learning fine-tuning compared to traditional reasoning models, Phi4-Mini-Flash-Reasoning outperformed the baseline Phi-4-Mini-Reasoning on complex exams [cite: 4, 5]. Evaluated with a maximum generation length of 32K tokens, the model consistently won on 7 out of 8 benchmarks [cite: 6].
*   **Throughput Profile**: Under the vLLM inference framework, utilizing a single NVIDIA A100-80GB GPU, Phi4-Mini-Flash-Reasoning achieved up to 10$\times$ higher decoding throughput and 2–3$\times$ lower latency than standard transformers on 2K-prompt/32K-generation workloads [cite: 6, 15, 17, 21].

***

## 3. Evaluation Profile: Qwen2.5-Math

Developed by the Qwen Team at Alibaba Group, **Qwen2.5-Math** represents a highly specialized series of dense decoder-only large language models focused exclusively on advanced mathematics and symbolic reasoning [cite: 11, 12]. Unlike the generalist approach of Phi-4, the Qwen2.5-Math series (available in 1.5B, 7B, and 72B parameter scales) relies on massive, domain-specific pre-training and an intricate self-improvement loop [cite: 11, 12, 22].

### 3.1 Data Ecosystem and the Self-Improvement Pipeline

The foundation of Qwen2.5-Math is the **Qwen Math Corpus v2**, which increased the total pre-training token count from 700 billion (in v1) to over 1 trillion tokens of high-quality mathematical text [cite: 12, 22, 23].

The core innovation of the Qwen2.5-Math series is the integration of a **self-improvement philosophy** spanning pre-training, post-training, and inference [cite: 11]. The pipeline operates as follows:
1.  **Data Generation**: The previous generation, Qwen2-Math-Instruct, is used to generate large-scale, high-quality mathematical derivation data [cite: 11].
2.  **Reward Model (RM) Training**: Massive sampling from Qwen2-Math-Instruct creates a dataset used to train a Reward Model [cite: 11].
3.  **Iterative SFT and RL**: The RM guides the iterative evolution of Supervised Fine-Tuning (SFT) data. As the SFT model improves, the RM is iteratively updated to provide better guidance. The ultimate RM is then utilized for reinforcement learning, yielding the final instruction-tuned models [cite: 11].
4.  **Inference-Time Optimization**: During deployment, the RM is used to guide sampling (e.g., Best-of-N or RM@8), drastically optimizing the model's final output [cite: 11].

### 3.2 Reasoning Modalities: Chain-of-Thought (CoT) and Tool-Integrated Reasoning (TIR)

A major limitation of the predecessor Qwen2-Math was its restriction to English-only Chain-of-Thought (CoT) reasoning [cite: 23, 24]. Qwen2.5-Math overcomes this by natively supporting both **CoT** and **Tool-Integrated Reasoning (TIR)** in both English and Chinese [cite: 24]. 

In TIR mode, the model functions as an agent capable of generating Python code, executing it via an interpreter, and utilizing the computational output to inform subsequent reasoning turns [cite: 23, 25]. This is particularly critical for solving equations, verifying algebraic identities, and executing symbolic logic [cite: 12]. Researchers developed "SimpleTIR," a method that unifies high-level planning and low-level token execution within a single policy $\pi_\theta(a_t|s_t)$, avoiding catastrophic gradient norm explosions observed in prior multi-turn training approaches by utilizing specialized masking and terminal reward assignments [cite: 25].

### 3.3 Evaluation Profile: Benchmarks and Process Verification

The base models (Qwen2.5-Math-1.5B/7B/72B) were evaluated on English benchmarks (GSM8K, MATH, MMLU-STEM) and Chinese benchmarks (CMATH, GaoKao Math Cloze, GaoKao Math QA) using few-shot CoT prompting [cite: 22, 23, 24]. The 1.5B model alone saw a 5.4-point improvement on MATH and a 19.8-point improvement on GaoKao Math QA compared to its Qwen2 equivalent [cite: 22, 23].

#### Instruction-Tuned Benchmark Performance
The flagship model, **Qwen2.5-Math-72B-Instruct**, established itself as a state-of-the-art open-source mathematical model, significantly outperforming closed-source models like GPT-4o and Gemini Math-Specialized 1.5 Pro on multiple fronts [cite: 11, 22, 24]. 

**Table 1: Qwen2.5-Math Series Benchmark Performance Overview**
| Model | Parameter Size | GSM8K (CoT) | MATH (CoT) | MATH (TIR / RM@8) | AIME 2024 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Qwen2.5-Math-1.5B (Base) | 1.5B | Outperforms baselines | ~80 (with Python tool) | N/A | N/A |
| Qwen2.5-Math-7B (Base) | 7B | 91.6 [cite: 11] | 55.4 [cite: 11] | N/A | N/A |
| Qwen2.5-Math-7B-Instruct | 7B | High 70s-80s [cite: 12] | 83.6 [cite: 23] | 85.3 [cite: 12, 23] | N/A |
| Qwen2.5-Math-72B (Base) | 72B | N/A | 66.8 [cite: 11] | N/A | N/A |
| Qwen2.5-Math-72B-Instruct| 72B | N/A | Close to 90 [cite: 11] | 92.9 [cite: 12, 24] | Solves 9-12/30 [cite: 12] |

Notably, on the notoriously difficult AIME 2024 benchmark, where generalist models like Claude 3 Opus and GPT-4 Turbo manage to solve only 1 or 2 out of 30 questions, Qwen2.5-Math-72B-Instruct solved 9 questions in standard settings and up to 12 questions utilizing TIR [cite: 12, 23, 24]. Even the ultra-compact 1.5B-Instruct model, utilizing RM@256 in CoT mode, successfully solved 29 out of 40 problems on AMC 2023 [cite: 23, 24].

#### ProcessBench and Process Reward Models (PRMs)
Moving beyond the outcome-based metrics, Alibaba evaluated Qwen2.5-Math utilizing **ProcessBench**, an evaluation framework requiring models to identify the earliest step containing an error in a mathematical derivation [cite: 7]. 

The researchers released **Qwen2.5-Math-PRM-7B** and **PRM-72B**, trained explicitly as critic models. In **Best-of-N (BoN)** evaluations (where N=8 candidate responses are generated and scored step-by-step), the PRM-7B model demonstrated superior performance, outperforming standard majority voting (maj@8) across 7 different tasks (including Minerva Math and OlympiadBench) with an average improvement of 1.4% [cite: 7]. On ProcessBench, the 7B PRM outperformed all open-source LLM-as-judge models and even outperformed GPT-4o-0806 in error identification capabilities, establishing step-level verification as a critical evaluation primitive [cite: 7].

***

## 4. Evaluation Profile: Llemma-7B

Developed by EleutherAI, **Llemma-7B** is a specialized language model explicitly designed for mathematical research, code-based mathematical computation, and formal theorem proving [cite: 1, 8, 26]. Unlike Phi-4-Mini, which builds upon a heavily modified hybrid architecture, or Qwen2.5-Math, which utilizes synthetic distillation, Llemma relies on massive-scale continued pre-training on natural and formalized mathematical corpora [cite: 1, 9, 26].

### 4.1 Architectural Initialization and The Proof-Pile-2

Llemma-7B is initialized from the weights of **Code Llama 7B**, which itself is an adaptation of Meta's Llama 2 fine-tuned on code datasets [cite: 8, 26, 27]. The hypothesis driving Llemma is that the syntactic rigor learned through code pre-training provides a superior inductive bias for mathematics [cite: 26, 27].

The model underwent continued pre-training using a standard autoregressive language modeling objective on a highly curated, 55 billion-token dataset known as the **Proof-Pile-2** [cite: 1, 8, 9, 26]. The dataset composition includes:
*   **Web Data (OpenWebMath)**: A 15 billion-token subset of high-quality web pages heavily filtered for mathematical content [cite: 1, 9].
*   **Scientific Papers**: A 29 billion-token subset derived from the RedPajama arXiv scrape [cite: 1, 9].
*   **Code (AlgebraicStack)**: An 11 billion-token dataset containing source code spanning 17 languages relevant to numerical, symbolic, and formal math. Crucially, this includes over 1.5 billion tokens of proof states extracted from formal theorem provers like Lean and Isabelle [cite: 1, 9, 27].

Llemma-7B was trained for 200 billion tokens (multiple epochs over the dataset) utilizing bfloat16 mixed precision [cite: 8, 9, 26]. To facilitate long-context fine-tuning in future iterations, the Rotary Position Encoding (RoPE) base period of the initial Code Llama architecture was contracted from $\theta = 1,000,000$ to $\theta = 10,000$ before training [cite: 9]. 

### 4.2 Chain-of-Thought and Informal Mathematics Performance

Despite lacking instruction-tuning or Reinforcement Learning from Human Feedback (RLHF), Llemma-7B performs exceptionally well on standard zero-shot and few-shot Chain-of-Thought benchmarks [cite: 9, 26, 27]. 

Evaluations were conducted using a fork of the Language Model Evaluation Harness [cite: 1]. On an equi-parameter basis, Llemma models significantly outperformed both Llama-2 and Code Llama, and matched or exceeded the performance of Google's proprietary Minerva models [cite: 1, 8, 27].

**Table 2: Llemma-7B Informal Mathematics Benchmark Comparison** [cite: 8, 28]
| Model | Size | GSM8K | MATH | OCW | MMLU-STEM | SAT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Llama 2 | 7B | 11.8% | 3.2% | 3.7% | 29.9% | 25.0% |
| Code Llama | 7B | 10.5% | 4.5% | 4.4% | 25.1% | 9.4% |
| **Llemma** | **7B** | **36.4%** | **-** | **-** | **-** | **-** |

*Note: The performance of Code Llama on MMLU and SAT was noted to be worse than random guessing largely due to the model failing to conclude its chain of thought with a valid answer format, a deficit completely resolved by Llemma's continued pre-training* [cite: 1]. Llemma-7B improved over Code Llama by 20 percentage points on GSM8K and 13 points on MATH, conclusively demonstrating that continued pre-training on Proof-Pile-2 effectively induces mathematical problem-solving capabilities without task-specific fine-tuning [cite: 1, 26].

### 4.3 Evaluation Profile: Formal Theorem Proving

What uniquely separates Llemma's evaluation profile from Qwen2.5 and Phi-4 is its demonstrated capability in **formal-to-formal** and **informal-to-formal** theorem proving. Computational tools like Lean 4 and Isabelle require absolute syntactic perfection and strict logical state tracking [cite: 1, 8, 9]. 

Llemma-7B was evaluated on its ability to generate formal proof steps interactively:
*   **Informal-to-Formal Proving (Isabelle)**: Given a formal statement, an informal LaTeX statement, and an informal LaTeX proof, the model must generate the formal proof script [cite: 1]. Llemma-7B closed 22.1% of theorems in Isabelle, surpassing its Code Llama initialization and the built-in Sledgehammer prover automation [cite: 1, 9]. Notably, Llemma generated proofs complementary to Sledgehammer; combining both resulted in 26 new validation proofs and 17 new test proofs [cite: 1, 9].
*   **Formal-to-Formal Proving (Lean 4)**: The model predicts the next formal tactic required to advance a proof state. Llemma-7B performed similarly to ReProver (a model explicitly fine-tuned for tactic prediction) without requiring any task-specific fine-tuning [cite: 1, 9]. This represents a milestone as the first demonstration of few-shot tactic prediction for theorem proving achieved by an open-weight model, a capability previously restricted to proprietary systems like Codex [cite: 1, 9]. 

***

## 5. Comparative Analysis and Synthesis

The convergence of these three models outlines the diverse strategies currently employed to maximize the capability of compact networks. By analyzing their profiles side-by-side, several distinct conclusions regarding SLM evaluation emerge.

### 5.1 Architectural Trade-Offs: Hybrids vs. Dense Transformers
**Phi-4-Mini-Flash-Reasoning** represents a profound structural deviation from standard transformers. By integrating SSMs (Mamba) with the **Gated Memory Unit (GMU)**, it fundamentally targets the physical constraints of GPU memory bandwidth [cite: 4, 5, 10]. The model achieves 10$\times$ the throughput of standard dense models in long-context scenarios (e.g., 32K token generation) by dropping the $O(n)$ cache scaling requirement to a constant state size [cite: 4, 10, 21]. 

Conversely, **Qwen2.5-Math** and **Llemma-7B** maintain classical dense decoder-only architectures [cite: 14, 22, 26]. Qwen relies heavily on **Grouped-Query Attention (GQA)** to mitigate the KV cache bloat, but inherently cannot escape the quadratic scaling costs during extremely long generations, making it computationally heavier for extended tool-use interactions [cite: 14, 22, 29]. The trade-off is that pure transformers provide exact token-level recall [cite: 4]. While SambaY mitigates SSM memory loss through alternating Cross-Attention and GMUs, empirical evidence suggests dense transformers still slightly edge out hybrids in absolutely rigid formal-syntax tasks (like Llemma's Lean 4 proofs) where precise character-level historical recall is paramount.

### 5.2 Training Paradigms: Distillation vs. Continued Pre-Training
The evaluation profiles highlight two highly successful, yet divergent, approaches to instilling mathematical logic:
*   **Synthetic Distillation and Reinforcement (Qwen & Phi-4)**: Qwen2.5-Math and Phi-4-Mini rely extensively on massive sets of synthetic data generated by larger teacher models (e.g., DeepSeek-R1, GPT-4) [cite: 11, 19]. Both utilize Preference Learning: Phi-4 utilizes DPO on rollouts [cite: 19], while Qwen2.5 utilizes an iterative Reward Model pipeline [cite: 11]. This results in extremely high performance on standardized, natural-language math benchmarks (GSM8K, MATH, AIME) [cite: 5, 11].
*   **Domain-Specific Continued Pre-Training (Llemma)**: Llemma bypasses preference tuning entirely, relying solely on next-token prediction over the highly curated Proof-Pile-2 dataset [cite: 9, 26]. While its zero-shot GSM8K and MATH scores (e.g., 36.4% on GSM8K) [cite: 8] appear vastly inferior to Qwen2.5-Math's instruction-tuned metrics (e.g., 91.6% on GSM8K) [cite: 11], Llemma's raw capacity for structured formal mathematics (Lean, Isabelle) demonstrates that base models can internalize deep symbolic logic without the potential mode-collapse introduced by RLHF. 

### 5.3 The Primacy of Tool-Integrated Reasoning (TIR)
A core evolution in evaluation primitives is the integration of external tools. **Qwen2.5-Math**'s leap to a 92.9% accuracy on the MATH dataset is heavily attributed to its TIR mode coupled with RM@8 (Reward Model Best-of-8) [cite: 12, 24]. Permitting the model to halt generation, execute a Python script to perform numeric calculation, and resume generation drastically minimizes arithmetic hallucination [cite: 12, 23]. Similarly, **Llemma-7B** implicitly evaluates this through interactive formal prover environments [cite: 8]. Future evaluations of math-focused SLMs must consider TIR an essential baseline, as raw CoT generation is demonstrably sub-optimal for complex symbolic manipulation.

## 6. Conclusion

Evaluating small language models in domains requiring rigorous reasoning necessitates a multi-faceted approach. The profiles of **Phi-4-Mini SambaY**, **Qwen2.5-Math**, and **Llemma-7B** dictate that researchers can no longer rely on single-number aggregate benchmarks. 

*   **Phi-4-Mini-Flash-Reasoning** establishes that architectural evaluations must quantify long-context memory throughput, demonstrating that hybrid SSM-Transformer structures like SambaY, enhanced with Gated Memory Units, offer unprecedented hardware efficiency while maintaining mathematical prowess [cite: 4, 5, 10].
*   **Qwen2.5-Math** proves that evaluation must probe the step-by-step logic of the model. The use of ProcessBench and Process Reward Models (PRMs) highlights the necessity of models understanding *where* they fail, scaling verifiable logic to the heights of the AIME exams [cite: 7, 12].
*   **Llemma-7B** introduces formal verifiability as a core evaluation primitive. By mastering formal-to-formal tactic prediction in Lean 4 and Isabelle via the Proof-Pile-2 dataset, it shows that open-source models can serve as legitimate tools for advanced mathematical research [cite: 1, 9, 26].

Collectively, these models chart the immediate future of artificial intelligence: localized, radically efficient, and deeply specialized reasoning engines constrained by formal logic and optimized for computational autonomy.

**Sources:**
1. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHldkw634BmZJK2nKWOiric5QaQd9COao4PvLgVTV_nFJikeQ27j9_Kbcjcc7Z0eWjhHTJB0Pjqe9myL2V_mlHypJaSyI285YaFk0Ihscm6pxc6gEHFiCeCvMJOz5swo_A=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw6HYi7q-qm8jqyl1mPl2lNiA-3iwtsdaIjFHqySqxEPw24wVPFCammfTTzMfpH9T48MbqIQ08RcVB-YZbLItMXodTQrzZnFzhVbpDl0_E7Ik5kNd3cI90ppa2HPJyePwCtLG6qDWZzwD0fOC2ZEH5ndKw9JHyFFhQvPd5WFzePX3Y7tCp5rAwrTiX45lT639pJottmyDRYfxid3SoNYPmDqNsiCLJSAsvDKDC5NBFqg==)
3. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWRlXrcB6ea44UFC_DX9_SGG0JuqTQXRZFvIaJGBwvnelQW7K_f-RQIosjLkqBWyk12Gu9Z6q4ZdGFcFKrugS3n64ZLV3Kz4LE6at3Ehy981op-qH3H-uur2Ax6RrIZ8XuMoGhDrIenrF3f6_1)
4. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPpCcnzIXMoOwaIT8F4YVDCu3gzXRtsGKt7nfbSlcImKeulluI32X496znxxcPjmXKpGBzmznDuZClxsPwkGGevr0jQU738peRiSliWFUYazy-yZ7b_DyHemcDpkZ3D3pRrh0DrnaZwZju2N3Fjl6H)
5. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO7ncY9wEqYp8o5ARPqI9Wqa9NgymJZMb46s8JHndejOJ-HwgXyEZsRY2by0OP4wyZ3s5DR4bpM6vKzkkMWvjpYJvZaU_wE6AuSyfyJOAjXcfem9vTvGMbCOjQVqbfHu0=)
6. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh_ZK4DiuyXqRNOe6A0QcEmpNQjYMybNxeev9EKDJvg4F0MjHohZihlwUINhU-3rjKvJly4DA8DR09Y5sUlDX8lRltDkCEGaCqPUBPjSm5xwzvMlPT3ABquQoB6ZTiNqPHino=)
7. [qwen.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf7mcWEYPU7zDX1ozGwuiW0gROv1lqI3LFH5UXvNHvNq4tMaXlmBdwtMJRyqJulvLYaOCBsX32vY3nKcM_TvUg29S0bBNhkX23m-b6cRAApcrwni4-V-EhGnKYlTLk)
8. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeTffmP-oUEfD9P2twA3Pfc0wTtPjJd7t9fG8Glyj2bFwhGEdThHwsovfP2-Q9zDNGbQ4InRwIKr5WYEYNAy9dVf8uV667acz-VvMARZ2jQh69TMXy85-DBUZy2R_y48pH)
9. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj7BVM-spXhEmCPVV5ghZsOCFrmF8J_V1blSw7DTpgQ0TFtUMYx5QW7fVrcEikEteW1Dz-EQbUb_msmsDfIlM1OES1XzqkDjo7T7rSXIDctZ5f8xjr_YmmIKVo5ZESPQwiKJhDn6Mz1WS1QGFbcsuBuVtL80LpSPXg)
10. [xugj520.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNQgRWV0vAZZ-CpLzgeBQme0FkeHvB8SkJFgkeEYCZWh_Ruygkzxc4H8RkerePYqJXWWF8NhEwpDRz_sxUnej1q4LvJu3_SEP0AVRJC0ERu4CyDShN9fXAV3cwys86Gak2RlFHDwW5r-z_5VC_9bQ5cZYsNvccKeffWMZAPTmPdG8=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnkHbqa_WuEHsTRoqziNkq59o9kA4VgmQwKiHubujKkPxPFN7j_dIrGvKWwQJovOM9zG4MV-HKVhXzomJOcVtanWC0MaS3e47HXpiA2F2n-_DszBzu0_qYNQ==)
12. [qwen-ai.chat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmJzQJIP07BQorjcmSLrCrWqAEBODcEyYKa25w3TKM43en2vLVNvs6TIy2TO-PdN8iuq0Rv0mJNfKaJgbuGgj7250nwiZtoPw6o-jMJyEfd_vLD9xmnKWCnY2_pi3C)
13. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKO1-rmIX6VcEJZWGjTHd0ewc8TxdbHJl7h7wHZVIjlVabyxl4xSqten92aTheMF5b7LvsMCVsREPM6_INWwxwcKX-GVT5zVfeDHA4cqMpyYhZfKQrRU8uqjYFsIuFQ0J0iMuFEzqTPpCrpEdfXD7D8PgwpIESwMO7ExGR7p9UlM1-grbBKD2BODhzHR1PGgRyBMZVcnTbGWfnBBgOiUQPhl0MubvVelmz-LKKHOkK_pklp_vPm-K8kw3_7Yg=)
14. [azure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwUIWT078-arATbkL5leEQRtUCURU2eMWE9IL9IeztHgO38kCX98PXbpwSxkGPAwamHKuNZyRctr_UkfHOfUfDlmgQKqxcQzGPXr_jcAQI1PYQbpr4VheTiHV4_5p7YH99NVS4emK_CUKjwwJT)
15. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErxv1889HajEu9VhFoZoaZfq6rh0bnO8oxXt_xtRoPZWhJqxw-wCZm0PPqnCqKlRy-nLGOrpZffnsoPUXP5Yf22IhIk0sEsQTpCIgIqIjXm7iAm03VlKAJqVsC6MJFZABNHkmOssKoqD9BG4MAJK0kKg==)
16. [azinsider.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8iK1NRt6badpofDUJB_1db22f3PyXvXX_U5lRwmYLQ8koul9KdWiF15pZL6WnY-pg2VzkgOOUgdJCZgi0hpUITkjlpsGPQvc4iOrCgdSGstHh3qqDKiXhvSKNp9MREg==)
17. [modelscope.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXaJx-gLK4qAD7gFw3eM5G5f-GEQQbIa854xEj5U2ZPbjruUEFjXH0j3-xjBqh0uABLC2kyY_fQswqw7eGtTSdTacpbBhYV2gS03JGCWhrkuCspYaDp9Ul5D7pz6azhHZJAhiEJRtBWX1xGFgtAslOdppafklHAxFlqQ==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG37w55cUI1j-4SStpJb5u_yOFNOysZ_GplrGw-pyt5pVm_6D1fvAgRcsFauMDlX_nWm9W0zYVyYLVxRd41OBJsBLZ2RstGMeUVhoI7qNBfz8KXwJxJvhgFOQ==)
19. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ6V4oJbXoQNYzD4rOptK1K8kbRbpPfjJVn-JQ-MCxWIEC-h4hR0553J85j_zb_Ix5C_gz5Pne-QWbj5klylFTdfeyzBv2uGYAoaIGmIoU28ZjHAhcK0dt5wG1Kt3kcj_tA9SQ1kMiyckpRuGup2dUutLQ8r5NRI-Xs2QCXsJfSR-FaH5cMKakK7X1oYs6Ich8gj0-aLZcxQ7I8lsrgI-t5rwqIWyNaS4lwmvwRCMjVQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0TS5X1vRnXi49UdLJwLGnCM3bsPZnXlxk9HqBk4KpLxiU9Uc4MCJtMnTOX7fM5WcoQMdHrH2rCzf_XYyNM5az44IzpscFWLFWQA-4-ujiZgLhOBW6nKWVZg==)
21. [smythos.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWPMzZGEoavAHRiyWOp47vMREdOSJrRqf8mbryptT1OOdVjOjukFeodJQj9eVLiQywrkbrX0eEuqD6hKtBV_cHu6Ne1_I161DUt4vkI27LeUEjb6qNYKfXWWl15PgjJSjtx9cvllWsJ-krfgBxvMueKkkgEdmJ0WEf_RfMeHhWMwxNWZVC5S8ztsv5nHz9peOOSR58SGDHUDx4XZcxfKfViDKOoKM1Rw==)
22. [analyticsvidhya.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTB7RbTBQlJpxlMf1zzKX3sJ0AY5JpYYSXAUivsLnZ2FVhsNuEZg3IrcS0zxqfPXAW_qumZlziYNle54VJmz1y9gd9jVu0NAzZYkwqxPiTOG2r_yNgc-KujFfZMRW7Z8E7YtWHvNqry3mVwhnsUEHP)
23. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrjDm-7QUo6mrrZqA75ZuNuApuv9zoLKc4Ivfq8ezpWlILScmcfDusJCIJtyt6XVoneUlEhgbgk_JXVHIzB6z-vthcoe79JSvVCvamgEtmaxeDWVGlPaUIG4xnhHXmyfWb)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnKFpm5r3osWlyOhNUP1S35CYTJm2cjqDP-2tYfCE4T2k2_IyW9tbzeZfxJIHbg6UpAm4unRZEXJnQLxJYnq8wtf2tmZy3snDYYdL5DpqTBzahccSkH6HUk7pPjA==)
25. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2-6hQBJZR5DNivkfAFOF-aYGAogWMOV99Xhh8yQmF8CrUtr89JeqPwOVU7geIeQQOShdwGQcpeNwe1s2_R2VonJkmPbxkrkWgyy4XRkLisW3zKFd61wqHjb_C52eH)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPKNyys-Pt3mvrQQymY1V4bjji4iU5GS6wpC2HvgVJmyFgeSNLQKMykA2V4l8H1EZrgKvuR5-7a6BFPo6hGb0eTbMEIPMuHcQCeUXUFIMQULAC0ZVaqA==)
27. [venturebeat.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZV90BB4cpB5rLxu3iKK3KxgF4NvhfQbvbvU9ezSrV3W4UU4Z8-e_qVymKv1puiGbhZYO9gtWwqyDFCEso587ntY8srO69ZUN6PDA5F3qV8EOCzRw9gy7lWoDU2H61gzp51x9A1NnLOgyeeYwXVwo5Wqr88nPv0WlQRzDzZi8AQE3c3g7ombGEY8O4COaIkr-j7aJ7)
28. [ollama.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3oMDHvt3_ArQW0h0RDmKP9sI3j5MMdP9ibILI3CImWBZhyxPxYsGDmsH3Lu2mzmr4iNiFYThqsvOBCj29Dzl96XrJB7aV4i4OP6l3I-XR4oyvRKpJAP_SHA==)
29. [apxml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLE3gbO2aqSdKixUR0hEiWcZ19oS-td9wgGyaJ6YG-F5DlDLA2O7Z2QOW--mbkgtC1TUNcuGMf6jieX_j7E8aRqnIBUweCF9YkPFETIiRETJveIztrkSfDHw==)

