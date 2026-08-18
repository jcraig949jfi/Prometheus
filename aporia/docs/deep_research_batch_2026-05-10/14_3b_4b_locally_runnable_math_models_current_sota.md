# Prompt 14: 3B-4B locally-runnable math models — current SOTA

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJVG9CYXItdE51aThfdU1QbWY3MHFRSRIXSVRvQmFyLXROdWk4X3VNUG1mNzBxUUk
**Elapsed:** 333s

---

# Project Prometheus: Survey of 3B-4B Math-Specialized Language Models (2024-2026)

**Key Points**
*   **VRAM Constraints:** A 17GB VRAM ceiling permits unquantized (FP16) inference of 3B-4B parameter models but forces 4-bit/8-bit quantization for 7B models or supervised fine-tuning workflows. 
*   **Model Availability:** There is a gap in native 3B math-specialized models; the landscape is dominated by 1.5B–2B variants (Qwen2.5-Math-1.5B, DeepSeek-R1-Distill-Qwen-1.5B, Gemma 2 2B) and 7B variants (Mathstral 7B, Llemma-7B), with Microsoft's general-purpose Phi-4-Mini (3.8B) standing in as the optimal dense reasoning model in the precise 3B-4B class.
*   **Activation Tooling:** `TransformerLens` offers robust support for standard Qwen, Llama, and Mistral architectures but struggles natively with architectural deviations like Phi-4-Mini's SambaY hybrid state-space decoder; `nnsight` provides a safer abstraction layer for modifying Hugging Face computational graphs.
*   **Anti-Anchor Reality:** Claims of 80%+ accuracy on the MATH benchmark for sub-4B models heavily rely on Tool-Integrated Reasoning (TIR) via Python interpreters or reinforcement learning-derived over-sampling (e.g., Best-of-N), not pure zero-shot forward passes.

**Context: The 17GB VRAM Challenge**
Project Prometheus requires mathematical reasoning capabilities constrained by consumer-grade hardware (specifically, 17GB VRAM caps typical of high-end consumer GPUs like the RTX 4080 16GB or mobile workstation equivalents). This boundary acts as a strict bottleneck for mechanistic interpretability research and local fine-tuning. 

**Context: The Rise of Distillation and TIR**
Between 2024 and 2026, the paradigm for mathematical language modeling shifted from scaling raw parameter counts to algorithmic data curation and post-training refinement. Knowledge distillation from frontier Mixture-of-Experts (MoE) models (like DeepSeek-R1) and Tool-Integrated Reasoning (TIR) have allowed 1.5B-4B models to match the quantitative reasoning capabilities of previous 70B generation models. 

***

## 1. Top 3B-4B Math Models 2024-2026

The landscape of math-specialized Large Language Models (LLMs) in the 2024-2026 window is bifurcated. Rather than clustering specifically at the 3B-4B parameter scale, research labs have predominantly released highly compressed models (1.5B-2B) intended for edge devices and standard 7B-8B models intended for workstation GPUs [cite: 1, 2]. However, assessing the available ecosystem against the 17GB VRAM ceiling yields specific candidates for Project Prometheus (Apollo/Rhea selection).

**The 7B Math Models (VRAM Ceiling Analysis)**
Models with 7 billion parameters require approximately 14GB of VRAM for pure FP16 (16-bit) inference, leaving a mere 3GB for KV-caching and context windows. Consequently, they are "too big" for unquantized fine-tuning or activation-caching (via TransformerLens) under a 17GB cap, but remain highly viable if quantized to 4-bit or 8-bit [cite: 3, 4].
*   **DeepSeek-Math 7B:** Released in early 2024, this 7B model achieved 51.7% on the MATH benchmark using Group Relative Policy Optimization (GRPO) [cite: 4]. In FP16, it requires ~14GB VRAM, but an INT4 (4-bit) quantized variant consumes only ~5GB VRAM [cite: 3, 4]. It remains an excellent baseline for reproducible reinforcement learning research due to its permissive licensing and clear documentation [cite: 4].
*   **Qwen2.5-Math-7B:** An exceptionally capable 7B model trained on over 1 trillion math tokens. It achieves 83.6% on MATH under Chain-of-Thought (CoT) settings [cite: 5, 6]. Like DeepSeek-Math, it requires 4-bit quantization (e.g., AWQ, GPTQ, or GGUF) to be comfortably manipulated within a 17GB envelope alongside activation tooling.
*   **Llemma-7B:** Initialized from CodeLlama 7B and trained on the Proof-Pile-2 dataset for 200B tokens, Llemma is tailored for formal theorem proving (e.g., Lean, Isabelle) rather than standard conversational mathematics [cite: 7, 8]. Under a 17GB ceiling, 4-bit quantization is mandatory for developmental workflows [cite: 7, 9].
*   **Mathstral 7B:** Mistral AI’s dedicated math model (notably, "Mistral-Math" is the community colloquialism for Mathstral). It relies on the Mistral 7B architecture and achieves 56.6% on MATH [cite: 3, 10]. It fits into ~5GB VRAM using 4-bit quantization (such as IQ4_XS or Q4_K_M formats in GGUF) [cite: 10, 11]. 

**The Specialized Sub-4B Variants**
To operate natively in FP16/BF16 without the degradation inherent to weight quantization, Project Prometheus must look at the 1.5B to 3.8B tier. These models fit seamlessly into 17GB VRAM, allowing sufficient overhead for the memory-intensive caching required by TransformerLens-style mechanistic interpretability hooks.
*   **DeepSeek-R1-Distill-Qwen-1.5B (DeepSeek-Math-Lite equivalent):** DeepSeek's smallest 2026 release. It is a dense model distilled via supervised fine-tuning from the frontier DeepSeek-R1 MoE reasoning model [cite: 12, 13]. Built on the Qwen2.5 architecture, it demonstrates remarkable chain-of-thought preservation. A community fine-tune, DeepScaleR-1.5B, pushed its performance even further using reinforcement learning [cite: 14]. 
*   **Qwen2.5-Math-1.5B:** Alibaba’s native math-specialist edge model. Note that there is no "Qwen2.5-Math-3B"; the Qwen2.5 family jumps from 1.5B directly to 7B in its math-specific lineage [cite: 15, 16]. The 1.5B model relies heavily on Tool-Integrated Reasoning (TIR) to execute Python code for calculations, pushing its theoretical MATH score to ~80% [cite: 5, 6].
*   **Phi-4-Mini (3.8B):** Released in early 2025 by Microsoft, this model perfectly fits the 3B-4B parameter target requested. While not explicitly named "Phi-4-Math", it was trained extensively on synthetic mathematical and logical textbook data [cite: 17, 18]. It contains 3.8 billion parameters and employs a dense decoder-only structure with Grouped-Query Attention (GQA) [cite: 18, 19]. 
*   **Gemma 2 2B:** Google's 2.6B parameter model. While not exclusively a math model, its pre-training corpus heavily weights mathematics and code, allowing it to serve as a robust baseline for circuit discovery and algorithmic reverse-engineering [cite: 20, 21].

## 2. Per-Model Technical Profiles

The following data outlines the architectural, empirical, and deployment profiles for the primary models under consideration. All inference speeds assume operation on modern consumer silicon (e.g., NVIDIA RTX 40-series).

### DeepSeek-R1-Distill-Qwen-1.5B
*   **Parameter Count:** 1.5 Billion.
*   **Base Model:** Qwen2.5-Math-1.5B [cite: 13, 22].
*   **Training Corpus:** 800,000 high-quality reasoning traces distilled from DeepSeek-R1, featuring strict `<think>` and `<answer>` formatting blocks [cite: 13]. 
*   **Eval Scores:** MATH-500: 82.8% to 83.9% [cite: 14, 23]; AIME 2024: 28.8% to 28.9% [cite: 14, 23]; GSM8K: ~94.1% [cite: 24]. MiniF2F formal evaluation metrics are generally low due to lack of formal theorem-proving alignment unless further fine-tuned (e.g., LEGO-Prover frameworks) [cite: 25].
*   **License:** MIT License [cite: 26, 27].
*   **Quantization:** Available in standard 4-bit, 8-bit, and AWQ/GPTQ. However, at 1.5B, FP16 inference uses only ~3GB VRAM, negating the necessity for quantization under a 17GB cap [cite: 28].
*   **Inference Speed:** Exceptionally fast; constrained only by memory bandwidth. Easily achieves >100 tokens/second on consumer GPUs.

### Qwen2.5-Math-1.5B
*   **Parameter Count:** 1.5 Billion.
*   **Base Model:** Qwen2.5 1.5B (Language Base) [cite: 15, 16].
*   **Training Corpus:** Over 1 Trillion high-quality mathematical tokens (Qwen Math Corpus v2), encompassing both English and Chinese synthetic data [cite: 15].
*   **Eval Scores:** MATH: 49.8% (Base CoT) / 79.7% (TIR) [cite: 5, 29]; GSM8K: 76.8% (Base) / 94.1% (TIR) [cite: 5].
*   **License:** Apache 2.0 [cite: 30, 31].
*   **Quantization:** AWQ, GPTQ, GGUF 4-bit and 8-bit supported natively [cite: 30].
*   **Inference Speed:** Real-time generation suitable for agentic workflows on local edge hardware.

### Phi-4-Mini (3.8B)
*   **Parameter Count:** 3.8 Billion (Dense) [cite: 19, 32].
*   **Base Model:** Custom Microsoft Phi-4 architecture [cite: 19].
*   **Training Corpus:** 5 Trillion tokens of synthetic, "textbook-like" reasoning data and filtered web documents [cite: 17, 18].
*   **Eval Scores:** MATH: 64.0% (0-shot CoT) [cite: 17, 32]; GSM8K: 88.6% (8-shot CoT) [cite: 17, 32]. MiniF2F formal scores are not natively optimized but logic extraction is highly rated [cite: 18].
*   **License:** MIT License [cite: 19, 33].
*   **Quantization:** FP16 requires ~7.6GB VRAM. INT8 requires ~5GB, and INT4 requires ~3GB [cite: 19]. Fits well within the 17GB ceiling in unquantized 16-bit format.
*   **Inference Speed:** High-speed token generation aided by tied input/output embeddings and a massive 200,064 token vocabulary, optimizing sequence length generation [cite: 18, 34].

### Gemma 2 2B
*   **Parameter Count:** 2.6 Billion (effective) [cite: 20].
*   **Base Model:** Gemma 2 architecture (Google) [cite: 21].
*   **Training Corpus:** 2 Trillion tokens, heavy emphasis on code and mathematics [cite: 2, 21].
*   **Eval Scores:** MATH: 42.3% (4-shot) [cite: 21, 35]; GSM8K: 74.0% (5-shot) [cite: 21]. 
*   **License:** Gemma License (Open weights, commercial use permitted with restrictions) [cite: 2].
*   **Quantization:** Standard bitsandbytes 4-bit/8-bit compatible.
*   **Inference Speed:** Highly optimized for edge CPUs and GPUs [cite: 2]. 

### Mathstral 7B & Llemma 7B (Constraint Note)
*   **Parameter Count:** 7 Billion (requires ~14.5GB VRAM in FP16) [cite: 11].
*   **Licenses:** Apache 2.0 (Mathstral) [cite: 3, 36], MIT-style open weights (Llemma) [cite: 8].
*   **Eval Scores:** Mathstral achieves 56.6% on MATH [cite: 10]. Llemma achieves 26.5% on MiniF2F using search heuristics [cite: 37].
*   **VRAM Feasibility:** To operate under 17GB with any KV-cache or activation hooking, these models *must* utilize 4-bit quantization (e.g., AWQ, Q4_K_M GGUF, reducing footprint to ~4-5GB) [cite: 3, 11]. 

## 3. Activation-Tooling Compatibility

For mechanistic interpretability research (Project Prometheus), the ability to cache internal activations, apply causal tracing, and perform activation patching is paramount. The primary tools in this space are `TransformerLens` and `nnsight` (often used in conjunction with `SAE-Lens` for Sparse Autoencoder feature extraction).

### TransformerLens Architecture Support
`TransformerLens` relies on a unified internal implementation of the transformer block. Rather than wrapping Hugging Face code directly, it reconstructs the computational graph using `HookedTransformer`, allowing uniform hook points (e.g., `blocks.0.attn.hook_z`) [cite: 38, 39]. This approach is highly performant for exploratory analysis but introduces significant friction when models deviate from the standard Llama/GPT-2 template [cite: 39].

*   **Qwen2.5-Math (1.5B/7B):** Fully supported. TransformerLens recently stabilized `qwen2` and `qwen2.5` architecture adapters [cite: 38, 40, 41]. The Grouped-Query Attention (GQA) used by Qwen is natively handled by the library's aliasing systems [cite: 42, 43].
*   **Gemma 2 2B:** Supported. Gemma-2 introduced structural anomalies (like Softmax attention variants and sliding window attention), but the TransformerLens community explicitly added Gemma 2 bridges in recent updates (v2.16+) [cite: 42, 43]. Note that mechanistic analysis of sliding window layers requires specialized slicing considerations during attention pattern retrieval [cite: 39].
*   **Mathstral / Mistral-Math (7B):** Fully supported via the standard Mistral adapter. Mistral's sliding window attention is maturely handled within the ecosystem [cite: 40, 42].
*   **Phi-4-Mini (3.8B):** **High friction expected.** Phi-4-Mini utilizes a "SambaY" decoder, which is a hybrid architecture blending state-space models (Mamba) for memory with sliding window attention for recent tokens [cite: 18, 44]. While TransformerLens has experimental `ssm2_mixer` and `ssm_block` modules [cite: 38], mapping a hybrid state-space/attention model into the standard `HookedTransformer` pipeline requires custom architecture adaptation. Out-of-the-box support for Phi-4-Mini's specific tied embeddings and SambaY blocks is likely to fail or require significant downstream patching [cite: 34, 45].
*   **MoE Architectures:** While models like Mixtral are supported via sparse-MoE adapters [cite: 40], debugging routing logits and expert selection gradients remains highly complex in TransformerLens [cite: 39]. Fortunately, the 1.5B-4B models recommended above (Qwen, Phi-4, Gemma) are dense models, avoiding the MoE tooling bottleneck altogether [cite: 16, 19, 32].

### nnsight as the Alternative Abstraction
Because `TransformerLens` requires manual reimplementation of architectures, it is prone to numerical mismatch and update lag when novel models drop [cite: 39]. If Project Prometheus selects Phi-4-Mini, the team must pivot to `nnsight`. `Nnsight` operates directly on the native Hugging Face model graph [cite: 39]. It does not require standardization; instead, researchers access layers via the model's native syntax (e.g., `model.model.layers.self_attn`). This preserves exact model behavior, prevents GQA/SWA/Mamba compatibility failures, and allows seamless integration with SAE-Lens for feature extraction [cite: 39].

## 4. Fine-Tuning Toolchains and Memory Budget

Fine-tuning LLMs on a strict 17GB VRAM hardware profile requires careful orchestration of Optimizer States, Gradients, and Activations. Standard full-parameter Supervised Fine-Tuning (SFT) is mathematically impossible for a 3B+ model in this environment, necessitating Parameter-Efficient Fine-Tuning (PEFT) techniques like LoRA or QLoRA [cite: 46, 47].

### Memory Budget Walk-Through (Example: 3.8B Parameter Model in FP16)
To fine-tune a model like Phi-4-Mini (3.8B) or Qwen2.5-Math-3B (base) under 17GB VRAM, we calculate the footprint:
1.  **Model Weights (Base):** 3.8 billion parameters * 2 bytes (FP16/BF16) = **7.6 GB** [cite: 19].
2.  **LoRA Adapters:** Targeting `r=16` on attention matrices (`q_proj`, `v_proj`) yields roughly ~10 million trainable parameters = **~20 MB** [cite: 47].
3.  **Gradients:** Gradients are stored only for the trainable LoRA parameters = **~20 MB**.
4.  **Optimizer States (AdamW 8-bit):** Traditional AdamW stores 2 moments per parameter (4 bytes each). With bitsandbytes 8-bit AdamW applied *only* to the LoRA parameters, the optimizer footprint is negligible (**~20 MB**) [cite: 47]. (If full parameter tuning were attempted, the optimizer alone would consume ~15.2 GB, immediately OOMing the 17GB GPU).
5.  **Activations:** During the forward pass, activations must be stored for backpropagation. For a batch size of 2 and a sequence length of 2048, activations can consume 4GB - 6GB depending on hidden dimensions [cite: 19, 47]. 

**Total Footprint for 3.8B Model LoRA (FP16 Base):** ~7.6GB (Weights) + ~5GB (Activations) + ~0.1GB (PEFT/Optim) = **~12.7 GB**. This fits comfortably within the 17GB ceiling.

**If utilizing a 7B model (Mathstral / Llemma):**
Base weights alone are 14GB. Adding activations will breach 17GB. **QLoRA** (4-bit base weights) is mandatory. The base weights compress to ~4GB, and the LoRA adapters remain in FP16/FP32, keeping total memory under 10GB using optimized backends like Unsloth [cite: 46, 47, 48].

### Alignment: DPO, GRPO, and RLHF
Preference optimization (Direct Preference Optimization [DPO] or Group Relative Policy Optimization [GRPO]) requires loading both a *Policy Model* (trainable) and a *Reference Model* (frozen) into memory simultaneously [cite: 48, 49].
*   For a 1.5B model (Qwen2.5), two FP16 copies consume 6GB VRAM. DPO is trivial within 17GB.
*   For a 3.8B model, two FP16 copies consume 15.2GB VRAM. Adding optimizer states and activations guarantees an Out-Of-Memory (OOM) error. 
*   **Solution for Prometheus:** To run DPO/GRPO on a 3-4B model, use `Unsloth` to instantiate the Reference and Policy models sharing the same underlying 4-bit quantized base weights, differentiating them only via decoupled LoRA adapters. Unsloth's optimized triton kernels allow 4-bit DPO training on consumer GPUs precisely for this scenario [cite: 48].

## 5. Checkpoint Availability

For local deployment and internal modification, API-only models (like GPT-4o or Gemini) are non-starters. Project Prometheus requires open-weight architectures hosted on accessible repositories. All recommended 3B-4B models are readily available on Hugging Face Model Hub, providing both native `safetensors` frameworks and quantized distributions.

*   **Qwen2.5-Math Ecosystem:** Alibaba hosts the entire Qwen2.5-Math suite natively on Hugging Face (e.g., `Qwen/Qwen2.5-Math-1.5B-Instruct`) under the permissive Apache 2.0 license [cite: 16, 29, 30]. Safetensors are standard.
*   **DeepSeek-R1 Distillations:** The 1.5B Qwen-based distillation is available explicitly on Hugging Face (`deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`) under the MIT license, encouraging uninhibited commercial and research usage [cite: 26, 50]. Community variants enhanced with extra RL, such as `deepscaler:1.5b-preview`, are also accessible [cite: 14].
*   **Phi-4-Mini:** Hosted via Microsoft’s Hugging Face portal (`microsoft/Phi-4-mini-instruct`). Crucially, Microsoft uses the MIT license for this release, ensuring complete downstream freedom for derivative weights and circuit extraction [cite: 19, 51].
*   **Mathstral and Gemma:** Available via `mistralai/mathstral-7B-v0.1` (Apache 2.0) [cite: 3, 11] and `google/gemma-2-2b` (Gemma License) [cite: 21]. The Gemma license requires adherence to Google's prohibited use guidelines but otherwise acts as open-weight [cite: 2].

## 6. Inference Frameworks

Executing inference optimally on a Windows 11 platform with a consumer NVIDIA GPU (e.g., RTX 4080) requires matching the model structure to the backend compiler.

*   **vLLM:** The industry standard for high-throughput inference using PagedAttention. It supports Windows natively (though WSL2 integration is often smoother for compilation dependencies). vLLM excels with unquantized (FP16) or AWQ/GPTQ quantized 3B-4B models. It supports Grouped-Query Attention natively, ensuring Phi-4, Qwen, and Gemma operate efficiently [cite: 28]. 
*   **llama.cpp & Ollama:** Ideal for running GGUF-quantized models. If Project Prometheus experiments with 7B math models (Mathstral, Llemma), `llama.cpp` using the CUDA (`cuBLAS`) backend allows arbitrary bit-depths (e.g., IQ4_XS at 3.9GB) [cite: 10]. Ollama provides a wrapper to deploy these local APIs instantly on Windows 11 without containerization overhead [cite: 14, 48].
*   **MLX:** *Explicitly incompatible.* MLX is an array framework developed by Apple machine learning research specifically designed to exploit Unified Memory Architecture on Apple Silicon (M-series chips) [cite: 52]. The Prometheus team must strictly avoid MLX tooling on Win11/NVIDIA hardware to prevent engineering deadlock.

## 7. Anti-Anchor Flags & Benchmark Verification

The 2024-2026 landscape of small language models is rife with benchmark hacking, data contamination, and heavily caveated evaluation metrics. Project Prometheus must aggressively scrutinize "hero claims" made by model providers.

**The MATH Benchmark Illusion (>80% accuracy for <4B models)**
*   **Claim:** Small models like Qwen2.5-Math-1.5B and DeepSeek-R1-Distill claim MATH benchmark scores of ~80% or higher, ostensibly rivaling GPT-4 [cite: 5, 14].
*   **Verification Flag:** These claims almost exclusively rely on **Tool-Integrated Reasoning (TIR)** or extreme over-sampling. Qwen2.5-Math-1.5B achieves ~80% *only* when allowed to write, compile, and execute Python code in a sandbox to calculate eigenvalues or complex arithmetic, rather than reasoning through natural language alone [cite: 5, 6, 29, 49]. In standard 0-shot Chain-of-Thought, its score is closer to 49.8% [cite: 5]. Similarly, DeepSeek-R1 distillations rely on massive context lengths utilizing the `<think>` protocol, which extends inference time exponentially [cite: 12, 13].

**The AIME and MiniF2F Vulnerabilities**
*   **Claim:** RL-tuned models like DeepScaleR-1.5B achieve 43.1% on AIME 2024, beating OpenAI's O1-Preview [cite: 14].
*   **Verification Flag:** AIME benchmarks are highly sensitive to sampling protocols (e.g., `Pass@1` vs `Cons@64` [Consensus over 64 generated paths]) [cite: 23, 27]. While impressive, 1.5B models suffer from severe "discriminator vs. generator" disparities; they can recognize correct logic but often hallucinate syntax in deep logic trees unless brute-forced via multi-sampling [cite: 12]. 
*   **MiniF2F Caveat:** The MiniF2F benchmark evaluates formal theorem-proving in code-like languages (Lean, Isabelle) [cite: 37, 53]. Models initialized on natural language (Phi-4, Gemma) perform poorly here compared to Code-initialized models (Llemma) [cite: 7, 8]. If Prometheus requires rigorous symbolic proofs rather than algebraic problem-solving, general "math" models will fail, and Llemma-7B (quantized) becomes the mandatory choice [cite: 9].

**GSM8K Contamination**
GSM8K is functionally solved, with models as small as 1.5B achieving over 90% [cite: 5]. However, rigorous systemic testing reveals that much of this is due to n-gram contamination in the pre-training corpus [cite: 13, 54]. For internal Apollo/Rhea decision-making, GSM8K scores should be discarded entirely in favor of AIME 2024/2025 or proprietary internal logic evaluations.

**Sources:**
1. [premai.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEJzKDLnuXfbCrqh_xF2ov-dunLIKTuXlXphQd34cDMAw5i8KgXHzCZevXzJMro23iedRj35sNyaYe508IwOCBq1kDDZbGHbHdp4jasI7hiy5itNXggdhjV0ENckyq0fHc_p7xzBvh5Nkpc9o0vVy3DteqmXoreZvRTE0O)
2. [deeplearning.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQwmq0Bw2BnsUmUrkkz-GzilwmIRdILzINyamWyOgfFDMtDbJKFz6GJPJPvlANaeWDL7UjQJX6iHvg6aQtVa-4-JE-oS-pc4U1EIRhijvgGqyxNgcgWlrjCJALW8-xtxsBBPbAb_WRB6l4856GisUTGVGKC2bhO9s-fKQYjw==)
3. [hyperion-consulting.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwI1VwzIQ0YzpkHVqXbdeTB7EiShv4TzSjd88KzIfZQDb5w-7c78Wk5FILZODjIVhURqs5qr_e4TS5cNQrKO80iHsxcHbCZpadjOLPsi5wY1V4tfMGlhgrzK2XQBR0Mjk_wbv5C1TfoSTDuGsjuwrj15ttuv8keg-Sq09_5lZ5)
4. [deepseekai.guide](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoKAOnzNyMRG7EbhP-Q_b4SDWAV6z2zl-lDT_UpPz4Pt_iAXVzBE0iAQuJBwuxG393PUveInfEVN5MKR0-Gbfsn7Oyq8T2aWaqiZCGmuVQrI3C6kEb_AWxyCCszUtflqpPUrV3)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl0A1tdOGeg7lPCcsUy90jF41r3S3Ochv_vN_s4eoWJbM6JdWR2HoDYH9vv7zBIOon8wbg4mZa1iBZQl_0c8HLI0gf5VGFCqbGrFlAwJKLj4gO4NyYXFlSJg==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNbMmTCnj_rTKzT5QkoHiMBYjuslWzKeBnhdGcZtdmIg5MzFa4dsZ2X_yohGB5Ya5sFsfbw7fR39Yz__Wt9qpK_VXMX4J9FnqTmzukBu49tHH3rrUhbDfbrO1h6hsgc3n_)
7. [pricepertoken.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmRKlgCpEf2GzHml2sCm09_NBUc3VTR_aKDvWclldkH3XcJm6HGDcQllzMJoUCcYJd3YNBE38rThcqZ1lAI8KsNHc_lM2vVEPn8aVHYB7HDRrbwElf6BUko8Fy7fEsRqNcSAb2nsjBfWepWQ==)
8. [evalry.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVDPAJxgS75fnjXygMP6Q1muIhoXatFSW_M0opL-NrM6A2PCyPtYGEIzJ3Xj9dvAIoJWNPgTIkoMgvOQSqm3k4wZHGoG_ksMjUYQEpkOFs)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL7rqPeg10-ptr1OFZ4RfLge8OT46VxvPtp9IUyVlk0lbrcdYCfXmGtx0p73XtBOOsNXAxJdWLUdEIl-tUeo_wp5qXsdnZYKFNWs-DYW9XtrBQRe7MRg==)
10. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjJgCPP0AX85IQR6DWIyueUBpTiBt5tq6LcJ0DpyONm6wkxqxpl7kpuKBSXcpxjOdTzST-7T3BVzRhnv7-ijARZ-8NvBNrypxQjdkoOjX4rRZaq1i6Pz9qBuuwpWLRxIpUVQ2AjN678y8KwVRJ_CZ6Wi7Euzs8)
11. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmRgpbYHWhPue_jb8uYJlDF54J3py4KMBeIQtZfiEmzp-iJmLYuYamZN4iAHPAZ1dWblkaIaPlJ0jtNuEWuzgcpk_doD-URB3_e1sRiN5H68TkO0ibMIuBZ9IiG6BzsFoI6zFfGBRskQ8o1pab)
12. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9qymOPkevOnMyXOVKSBcM4JvOXkVx9bymSN6ONhk4O177hO74Nx3fc6LV0Y7XJ_YfuWz0wTzPo50OaRvLj8kohJDXgcY_OKnZrwu9cvP-_UdgK5LU3XXNJtvokurZL5Y0ulUdhagKGhwd7wDdKOgPp0KnETC2)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwgb6DZ3Uiqb3ShfUXAn6AR8yP8M4kh_H7-EF_u-wLDh5HLzsN5IP72KCl5Bm0gkb50Tk9_5t7MmgQyU5TlY0yPnpMS-xKej-aKGSLBb5T5pquZGBDWakPTOAZKw_rd81y7k3ox8t4RqOf5V--OB4xgEpVSVP2Pw==)
14. [ollama.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF7suSxs73jeKtwRgBpC-Dt2c0G3SZ1t7peunVCmwui74sI9zaj0B-aFFlzkPK7-G4iw0VZwIzck1YXYKvVLiuOiIKMRPf5hxMxbqZHJvVhe_2-dbZjBCrrxnaqPxi8vctKBykPwD6xOQtmyOn)
15. [analyticsvidhya.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwKhTf1xb6P-zfEn4DjlB3tArOSfD8b131hR5ASqTF6Z7wvplsy8qPIAb-wf2OqoNjzFEBtPELXJhoK5eFlJSniulf471tGblR0wgTKzS4zh7AgIn5ETwDkbQvWMgkWoSUM0HW3Eh6xOjq7ZtojsXK)
16. [alibabacloud.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGqs0859f2LwHEvlDQd6r3Jl2GiwrlvPi1cCps2QdFGXnQzO3XFjEmmIRUuS0nf3GsFr-rLBl6r2A3P9xO5THd3SAvGP36hMl6DuTXDbBeJ_zlIRbgYSdJAjcnNpn-ZZ_01jolB9iCB5aIIFcFErALcfXXW7LvjWnDu4jRMaMlrrT2GQ==)
17. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5zrYEeSe8vwvprBbKhAwF7-Zlay3dORahHHs5du9HkU7prssN4VPyy0MmN5zLv0u9gK-bBvP_Px1PQrzZn8dx4lWAzx-tdYTQ7gouTWKjaVMr82DrbJmsxXwZ-HxIlfhnszaG6L4RKuja71RX8NvehXHWj7AO)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFbqmDyCOHdDQ4NQUIIbKHgX9IKcsCXovzGnb1LX_Ag6wkCHlXHO87sLIXQg1fxBsBqci2BxLNfTO7VnKwURlpfmJmFIqfX2eEMnv-Uk1Gz0gSBOra-0ahxQ==)
19. [apxml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEXwTHKqqTqvEckQV5t_fc_yK8Tdo_2ac7AtduuoZ1fL9aCfCLxtsaOkAYJZaNDV6RzIkEydqTgKTc6GxD20ZOcg92hFOxUTOH7FtsEZsMiWfHWJWegNF6Zg==)
20. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH01FGtqBbev3cX1fBA-3ufQ7p93C8klRfotNzCdY1smAE6EzR3jt62YUhoZVaptMisH1pKBdlUXG-0qAGH_NQbixrF2DIMveRNKtu8RvjRa2CxYzd-iS8bJpALVbYBcgw75D05na9JWQ==)
21. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1sZLcsojexIwdahl9Poep0SAafio6qespOr3Te5iPnNBlS7NIWHXkcJXoVHj5UgCFyZ7EXluReZVc85pxC9fny8laYlNTOzh---5Ujfjmo_y4mEK4PWINYyRVo2z6)
22. [bentoml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELXurRFCZN6bwFvtdxXP_SnJWEH0yahXgv4KDI0d9YGVVAXPIl0f05w2oEPexOr9q2pD3bCfnNC9zqAjHhOvQK_I23AVA7PpZi4Td6clOih9Fcvtd49PmJ_0LK-Jq3tOqJ2b9EYeGb5jpCXmHeZa_MblQXzdW3xKAykVwURw-JIOlt7QDHJduma8Xc0IiOtAaK)
23. [openrouter.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQIaszpMisYJN3kcNAwdi_EUTgGZBXqUq9KtrfdKIgvtUrOzCSoPrxXlS6GsOexkwRWkbCrTji44pUxZVyQYPYNUde8T39Py_UtrufysImhSeZuZF01I83V5nlzPiEbzTbE3R4plHwuJfoVMcCXa8J3HE=)
24. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1Po3N3-FdrwiUiiFQ-_V55UWTklu-MecsBRZVz-eFecOFZT56CvqNSipN_LyWHa3oKZfhziH2qBilg1cq-EL4YFkJhi7ApCUlYbJmMnWDxpAMFyfQ3FXmX2lkMIBGJ0a7QVfXAGKNWymGCcUYWnQzQA==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0b8PcCmcg9T3hBDK0Ibxof7ZH86RbmPWaQsfweQMIjQ6otMg8QrzLQajZmc1swiR2eFecP_hmQ6smxa4Z8JA3XtEoIPRiQGMGcZdKkFNhVgrj5Ro9kQ==)
26. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhLcuwPdxdYgc0sqQ2_GyLvbArpL_WswX94i0hFUUOsvbJg10bU6ZWsUNqs07o9lLj-ScSJ6iL-1Sibs8-IrIebREoZZYMg11gICXcgxZ0zbMUoPpMTVOOWWRALhOBx1QEwo9Oan1oY_WuAmv9uE7Hhj-7N5Yomp82C0So46T7_FZn-IBczr5isYpVLK_wMqBRuI3cYb7V)
27. [llm-stats.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3_ACxTFYfdz3ITLy6PpdbNDl0Cts6YIMuNKrEEOGs4wVcURwfaidG-eB6ZjWsr8n_2ymSDH1FtCrRd6zLKkUOo1Xujr2t1SrYAV5alynnsRCVRL-TWHoqyZARrxDgbiOYrePyHcBP_NucpuCpU4KL)
28. [redhat.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKNp9VZBbFh4IvofcW10ecCCNYIAkLS9O1FtLWHwEiTITSIPEI7ePJUcOl68t3fCuXRzwaA_X_9UTkNxUFndWsf2MBKK-SDhp6l8mc4xKcOFkXHtQw1MnHMf7x9Ce4WuzfRlK6TvCoLV26rvjAK5UQmOex9epWZF7mHcZnkDImEoHDkkfY2S1DYPwjBC0-MFuj40hOdJqyV1bR3Ne7nKc=)
29. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENJBEtnt-Sr3hyOWgRNmwbJw4NT2013-JSijMC4FuicnQ_yFxC9imkbLdV6uAwUNmFvaepYi0E_n2XEbHZrqLihIQ8DnN_1XybLiupZSCFonrSDqYf5IYZCgk7awBXKKMFuAg=)
30. [intuz.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOhL6O_3pKyQtHtxFbNpgjjeSNu5vk2SKV8P1zOS4zcxkPbcLUVXZN2oLj86g1mV_6Uw8e7DQKbv5WLGI8uyyXJZqq4MCZSlOmwbV0XiZMb1yedgkxa9QLf0J3fcAOCGxTHMGuw6KRoWPRgQ==)
31. [sourceforge.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUGj7YZwrH2_Xxb1mXClKzbdyf8KilUGvGSzjTD-jRIx6puh_8O95WiYOPN_7U5QMDBhhSKYVI6ViWUVOLXsEo5kC4us3oE8z2QHWxsekpoC3VucdFnc1eg9k3qvoVEBzDeZ-1CkI3Yy1IDA==)
32. [azure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUhfz-EqNyT1TSmvlSD8KHOPIDBBk_dYt6fPg5xeUmYH_pp-YxDdsQOmsrPla4rWGU0qZonzAMD34uHj8f8OeIXSjPCVlhETiH9Vjfqeaa-NGRmDJIiGGArxpGepwYg6JDvNNM037w5f9GR536)
33. [llm-stats.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMLKwct6OtiNojIUSm6UYuMDktcQu0ONlhHHeUd6EuL8ljZ7DFymEOGlcG_KnqkFXwPlyrmZ0cdme2MXsVpBZ6YwG4UjQh8hHdRzdaxruXalbNGTKOgUf6e30fJfI=)
34. [debuggercafe.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCDz6Msuhxk5E2eQoE-V8ZypAqx2M2x8ByW7l-p5HNPsTC1VsXoNUn2PoupIrzwef3fjqmE-f2Pd9O2t1tmM_ljwKJxfu9o7P-1fG1balmyHA68J3IEIQ73bI=)
35. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWHbm6JLo0MIA0lDn1AbAZ-0hMwSXjFy4Mq6A4Z6UbDG13ra3P8Zy39D6bfFT-FAVFJGFW7sXYGdzoAJz_TPzP-6B8u9aB-hUcxKFvflQ_pqMMy8iqDmZA7lGh6q_-S-uHgngPAJ57E0G2aF7PcJNrvPOG-Q==)
36. [latitude.so](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA-8mNZrZ8k_JMIpXs-Ozp7WTK2LXvhoJgwBKkHxckLgwjQb9usOzioRKTKtBNdxYn6_Fx0v739ZERIeLGFjA5aN2UNCFYeZjRss74xzV4baNt8ZVNzMKOajRyxPOFPvWpMk4EPbfO-jyKR-yHnOhqnTKmm27QCxZQa6wuGxHkpKJi)
37. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECYPWU3tMAV7YFwrPQekjQKDeRs5TRm-tUKqpfn2p31AFatqipZZGYmTMmMghAkQETNFWd8yhyJl7WLYKue9z4t_PNwIetM6vEVsn80WZy59E9SaLofARxwPxRFtHZF8pckkXgToKQNte8gaCN64Q0zhJRysWP1raJ_HLt3Bw2Pw==)
38. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuL5bMwbbO4GE-5-zDzeL3ju-f_z6xZ14I8n5LguJl9jsqkiEW3lWN6FgLCb8p90QRx7XtysswLda3PqY7CGMXUn8odXFuYyJ_MB4LskX2r4T5eV8CFn8gRRN091C3A7eKYlI1RrmdaYKWHbUFPaZpiVrv45bVl55846B06cIhjt8GrVGc1lU=)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoXyB28RHKGBmlax8wgEDUXk9R0HJCwVwIMYBgWG7ups0KAdJ5UO3ucKGCfiMO0tW0lrOzKgWjqFsyLWLY6zw29dIQI4rw95TqLuVkAY5LqpaPcHWSoPzgKA==)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6KD4WnKSi_nzFCFCCKnAqDoqiOcmJS_2QVRhykjXAS5E7R6B1EOwD7CO_yFg-8x_jSn5G8PekXmffFnW3ZQpIsFpJdHzS57Mh2eZwnEFsg0BFfqebBKZ-SA==)
41. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAxhQzAVSiFS5orirY_B_udkcFw5vpjSjj4zlNbVTVflbzej4Hy36auOUKAzMXoyqWM42W3EnsorZz-FBWPpSw_vYDkTYL43zAEIoE7DfxTPWmjf0Rorm-LC_6rhC2XbT7jhwHNrayB4OIkQ==)
42. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9EgPbKim7f9Bxcjc5ExWIlkTESQcjGsgpwNYP2Hwo4tXGsY4WJgQPSttRcp2Dg7F-ViynZR7twaWdTztXPmxVadg7eqPqUPZYeTp37vAUMIvsFcI-mZ3nr1ke7o7oOmrJEFs31P7Y0nUwuMB4eA==)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu9dd54_jaiEFiAPfOb082xta94P0Y0pE9FA_oec8YCnPf7y6v1pRY25AgDJPl5X1kRXlAQVBgZn0jMTPTNBt8IkLl7mRSf5J2ANvjEdc6SWXEnhLF6NpQKg==)
44. [smythos.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv-6jrrZHIYj_eP6T42pf62Md48qImNypOGKyXCofIBVTX0tdofNNS5ypOAuOjBIuUJWmDL0w-nBG_PkH3Qx9EJCCr6WE61BBZXueoiw-DPa50wlhFL7bBFnanWeUQwJ2KEtEN_Uz8imiEXsZGrpZ0Gr3E76b3jo9-o5hIRgjqyGtLiD0ON_H4qkHJcDwAErqacneX6xT2_yExTcpGGPh32i6k1MVTPA==)
45. [learnmechinterp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj4bd2CxNgEF8E7z8x2wQBMVMbVvXGm6Atcd21gCRdl1jdlPDswoek4BvE779HzbNyS1kNGwji4YRV_RVeA3c35NasiAljRiMwLGTg_CpwsMxYl3ByFrwNS-xYD23dUHdlfEX7-O7Paro=)
46. [aimodels.fyi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3hAW2aymUex2c_2dmy8FAtpvDYMQ5IwkmeeuqpWg2f_XqAR2cd-W6Ocz4emL6YT3jIrOCkYKNPWRZiWztxcudddBw23nBiZP7Trkk69OL7q_1L3kOFAQH5r8lmyXe2e0M-9WRppmdrGXEmVoRKTHMKXI=)
47. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfGAtC49Pz_Xuf-sZ-rpNrCSvcTiTMynbmY7MTBmpvjWfWPLz9Uqt5x71qGlaPXPL9NEHuNazf-6vtUYTVKOci9AEjAgnq7Wx42fFlc59zHa2SR6n5lDZIMY8CEldZAz0_1Ls8VbcFXk1FT98v_hLFdQo_k7Deb7uSPMoEP43AXxaZAuQS5kcQ_ECoTTPghMXpLpM4eo63SWaqFZwfkq3cfieXWpF7WPU=)
48. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWBvS9Ts-p-FzQ906_PjSDrlP24u2moy-ymTjDdbcbLu7d-cmUBpHA57rzaGbza5q32HFx-qU_XuFtEpJJWZ8YNj9TlO5mp83INWuNugKL3nxsv7Gqxzkv8pdQIF2bgZ-Phw==)
49. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcINleo-7B4SlGZ7iy6JEW4eRSR1Ux2Z4syM-ZTlNDeSXcuhrlpaVdqF8pKoSlU4e6Y0ovSEDpToe_tFdhfFVcS_9tXcjFxaLL5zjzIdS_JBHrWVUS-wq4LayeKar2Uu_MDk6uZYRvq6vQYA==)
50. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMLlu20vEJIJnKvVRKurVG9wDbj4eUkQpjv01dAkWfmLGMaTyrBvxusbo8XYNJCWNoxjw8AwBUjDJn9K3_sHGTuiV6TVwa7TRF1IlpcBqIifPSdzTLfPoxsCNxK83WcDqS4rIiDPTbLNmyzDZ0iiIhPDt-mUWR)
51. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB5TAS0YxHtx3286tzF_QBWK8rr3ruNkml3wXw2yI4O7oAd8AgRW6gu_S73Mlr6vY4ECTP-ycz_jgCp8sRZ1DjJosxDHS39fU-CZO5ROpQX6dYeB4td6U095RBh5DQa_1zBOm7gQZJ6Mpm)
52. [smol.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo2Eb_ecok0hL3idZfjzXWi3PNlGd4XkXcujTrnlYWec6h7ORNMJVPy5SHqGVZK43jrRJPGyx9K3HjBZN4KinIJnLc9xULqrcuEC0VDPmxTuKoaQhjgqGEbn_nE691gwZm4bwg)
53. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVx2FTpUDRsUx-wLQiDIroggt8-Oc5oSgmtO3dMQhyyBV4w6gzklKf9JZEgTveqyrbXGPiSABm1zbHOTzQiVsCo_qjj5kkRWPRKIInap5_dImx1sDwIA==)
54. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA5_loB7zCIvzimDV18QkFij7h9h_CsD99l_v_gpCB-YUdQ1uuvnEUTfweG_yLIvY_Bj09-4_v7G0jVnM5jsawc4iqeDyENuPCmDvJspWMvO8xvc8YnGmlaQ==)

