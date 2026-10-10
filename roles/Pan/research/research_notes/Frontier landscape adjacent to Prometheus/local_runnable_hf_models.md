# Open-weight models runnable locally on one RTX 5060 Ti 16 GB (sm_120) + 32 GB RAM, Windows 11, as of 2026-10-09

Method and provenance (read first):
- Gathered 2026-10-09. Every repo id below was resolved live against the Hugging Face Hub API (`GET https://huggingface.co/api/models/{id}?expand[]=createdAt&expand[]=cardData&expand[]=safetensors&expand[]=gguf...`) and returned HTTP 200, unless it is marked UNVERIFIED. Parameter counts are `safetensors.total`. Licenses are `cardData.license`. Context lengths come from the repo's `config.json` (`max_position_embeddings`, or the same key under `text_config`) or from the model card. GGUF sizes come from `GET /api/models/{gguf_repo}/tree/main?recursive=true`.
- "Date" means the HF repo `createdAt` field. That is the repo creation date, which can come before the public release. For example, `mistralai/Ministral-3-14B-Reasoning-2512` has createdAt 2025-10-31 but its name says 2512 (December 2025), and `mistralai/Voxtral-4B-TTS-2603` has createdAt 2025-11-17 ([mistralai listing](https://huggingface.co/api/models?author=mistralai&sort=createdAt&direction=-1&limit=30)). For Mistral, the YYMM suffix is the better estimate of the release month.
- For vision-language repos (Qwen3.5/3.6/3.8, Gemma 4), the parameter count includes the vision tower.
- "Fits 16 GB" verdicts are my inferences. The rule I used: GGUF file size + ~1–2 GB for KV cache and runtime overhead at a modest context. The GGUF file sizes themselves are cited facts.

---

## Q1. Code models usable as mutation operators / program generators in evolutionary search

### Takeaway
The models that fit fully in 16 GB VRAM and have strong code ability are **gpt-oss-20b** (12.1 GB MXFP4 GGUF), **Devstral-Small-2-24B** (IQ4_XS 12.8 GB), **Qwen3.5-9B** (Q4_K_M 5.7 GB), and the small FIM/diffusion coders (Seed-Coder-8B, Mellum, Stable-DiffCoder-8B). **Qwen3-Coder-30B-A3B**, **Qwen3.6-35B-A3B** and **GLM-4.7-Flash** are MoE models with ~3B active parameters. They run at Q4 (17–22 GB) with expert offload to the 32 GB of system RAM. Qwen3-Coder-Next (80B) is only marginally feasible at ≤IQ3 (28.5 GB). For high-throughput mutation, the cheapest useful operators are ~1.5–9B models at Q4–Q6.

### Cited Findings
Code-capable models (dates are HF createdAt):

| Repo id | Date | Params (total / active) | Ctx | License | Quant availability / GGUF size (cited) | Notes |
|---|---|---|---|---|---|---|
| `openai/gpt-oss-20b` | 2025-08-04 | 20.91B / 3.6B active | 131,072 | apache-2.0 | `ggml-org/gpt-oss-20b-GGUF` MXFP4 = 12.1 GB | The card says MXFP4 post-training lets it "run within 16GB of memory". It must be prompted in the harmony format. Ollama: `gpt-oss`. — [HF](https://huggingface.co/openai/gpt-oss-20b); [GGUF tree](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF/tree/main); [Ollama](https://ollama.com/library/gpt-oss) |
| `Qwen/Qwen3-Coder-30B-A3B-Instruct` | 2025-07-31 | 30.53B / 3.3B active | 262,144 native (card: up to 1M with YaRN) | apache-2.0 | Official FP8 repo. `unsloth/...-GGUF`: UD-IQ3_XXS 12.8 GB, IQ4_XS 16.4 GB, Q4_K_M 18.6 GB, Q5_K_M 21.7 GB | The card recommends cutting context to 32,768 on OOM. Ollama: `qwen3-coder`. — [HF](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct); [GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF/tree/main); [Ollama](https://ollama.com/library/qwen3-coder) |
| `Qwen/Qwen3-Coder-Next` | 2026-01-30 | 79.67B (Qwen3Next arch) | 262,144 | apache-2.0 | Official FP8 and `Qwen/Qwen3-Coder-Next-GGUF`. Unsloth: UD-TQ1_0 18.9 GB, UD-IQ3_XXS 28.5 GB, Q4_K_M 48.5 GB | Ollama: `qwen3-coder-next`. — [HF](https://huggingface.co/Qwen/Qwen3-Coder-Next); [GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/tree/main); [Ollama](https://ollama.com/library/qwen3-coder-next) |
| `mistralai/Devstral-Small-2-24B-Instruct-2512` | 2025-11-28 | 24.01B (weights BF16 + F8_E4M3) | 393,216 (config) | apache-2.0 | unsloth: IQ3_XXS 9.4 GB, IQ4_XS 12.8 GB, Q4_K_M 14.3 GB, Q5_K_M 16.8 GB | The card describes an agentic SWE model, "light enough to run on a single RTX 4090 or a Mac with 32GB RAM". Ollama: `devstral-small-2`. — [HF](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512); [GGUF](https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF/tree/main); [Ollama](https://ollama.com/library/devstral-small-2) |
| `mistralai/Devstral-Small-2507` | 2025-07-04 | 23.57B | 131,072 | apache-2.0 | Official `mistralai/Devstral-Small-2507_gguf` | Older Devstral. — [HF](https://huggingface.co/mistralai/Devstral-Small-2507) |
| `Qwen/Qwen3.6-35B-A3B` | 2026-04-15 | 35.95B / 3B active | 262,144 native (card: up to 1,010,000) | apache-2.0 | Official FP8. unsloth: IQ3_XXS 13.2 GB, IQ4_XS 17.7 GB, MXFP4_MOE 21.7 GB, Q4_K_M 22.1 GB | The card stresses "Agentic Coding" and repo-level reasoning. Ollama: `qwen3.6`. — [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B); [GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main); [Ollama](https://ollama.com/library/qwen3.6) |
| `zai-org/GLM-4.7-Flash` | 2026-01-19 | 31.22B MoE | 202,752 | mit | unsloth: IQ3_XXS 12.9 GB, IQ4_XS 16.3 GB, MXFP4_MOE 17.0 GB, Q4_K_M 18.3 GB | Card-reported scores: SWE-bench Verified 59.2 (vs GPT-OSS-20B 34.0), AIME25 91.6, GPQA 75.2. Ollama: `glm-4.7-flash`. — [HF](https://huggingface.co/zai-org/GLM-4.7-Flash); [GGUF](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF/tree/main); [Ollama](https://ollama.com/library/glm-4.7-flash) |
| `microsoft/FrogNano-4B-2609` | 2026-09-17 | 4.66B (Qwen3.5-4B base) | ~131K evaluated | metadata says **mit**; the card text says **Apache 2.0** (conflict) | `bartowski/FrogNano-4B-2609-GGUF` | Repo-level coding agent, RL-trained on ~1,500 synthetic SWE tasks. Card reports Avg@3: 37.6% SWE-bench Pro, 31.1% Terminal-Bench 2.0. — [HF](https://huggingface.co/microsoft/FrogNano-4B-2609) |
| `ByteDance-Seed/Seed-Coder-8B-Instruct` / `-8B-Reasoning` | 2025-04-27 | 8.25B | 32,768 / 65,536 | mit | `unsloth/Seed-Coder-8B-Instruct-GGUF`, `unsloth/Seed-Coder-8B-Reasoning-GGUF` | — [HF](https://huggingface.co/ByteDance-Seed/Seed-Coder-8B-Instruct); [HF](https://huggingface.co/ByteDance-Seed/Seed-Coder-8B-Reasoning) |
| `ByteDance-Seed/Stable-DiffCoder-8B-Instruct` | 2026-01-15 | 8.25B (diffusion LM, `StableDiffcoderForCausalLM`) | 8,192 | mit | mradermacher GGUF exists. llama.cpp support for the arch is unverified | A diffusion code model, a candidate for infill/edit-style mutation. — [HF](https://huggingface.co/ByteDance-Seed/Stable-DiffCoder-8B-Instruct) |
| `apple/DiffuCoder-7B-cpGRPO` | 2025-07-01 | 7.62B (DreamModel diffusion) | 131,072 | apple-amlr | Community GGUFs exist | — [HF](https://huggingface.co/apple/DiffuCoder-7B-cpGRPO) |
| `JetBrains/Mellum-4b-base` | 2025-04-28 | 4.02B | 8,192 | apache-2.0 | Official `JetBrains/Mellum-4b-base-gguf` | A code-completion (FIM) base model. — [HF](https://huggingface.co/JetBrains/Mellum-4b-base) |
| `JetBrains/Mellum2.1-12B-A2.5B-Thinking` | 2026-09-20 | 12.15B / ~2.5B active (MoE) | 131,072 | apache-2.0 | `JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF` (2026-10-07) | New. Trending on HF. — [HF](https://huggingface.co/JetBrains/Mellum2.1-12B-A2.5B-Thinking); [trending query](https://huggingface.co/api/models?pipeline_tag=text-generation&library=gguf&sort=trendingScore&direction=-1&limit=25) |
| `Qwen/Qwen2.5-Coder-14B-Instruct` | 2024-11-06 | 14.77B | 32,768 | apache-2.0 | Official `-GGUF`, `-AWQ`, `-GPTQ-Int4/Int8` | A mature FIM-capable baseline. — [HF](https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct) |
| `nvidia/OpenCodeReasoning-Nemotron-14B` | 2025-04-15 | 14.77B | 32,768 | apache-2.0 | `bartowski/nvidia_OpenCodeReasoning-Nemotron-14B-GGUF` | — [HF](https://huggingface.co/nvidia/OpenCodeReasoning-Nemotron-14B) |
| `agentica-org/DeepCoder-14B-Preview` | 2025-04-07 | 14.77B | 131,072 | mit | `bartowski/agentica-org_DeepCoder-14B-Preview-GGUF` | — [HF](https://huggingface.co/agentica-org/DeepCoder-14B-Preview) |
| `Kwaipilot/KAT-Dev` | 2025-09-15 | 32.76B | 131,072 | apache-2.0 | GGUFs exist (sizes not measured) | Dense 32B. Needs IQ3 or partial offload. — [HF](https://huggingface.co/Kwaipilot/KAT-Dev) |
| `facebook/cwm` (Code World Model) | 2025-08-25 | 32.58B | n/a in API | **fair-noncommercial-research-license**, gated=manual | Community Q4_K_M GGUF (`Volko76/cwm-Q4_K_M-GGUF`) | — [HF](https://huggingface.co/facebook/cwm) |

- Qwen3.5-9B (Q4_K_M 5.7 GB, Q6_K 7.5 GB) and Qwen3.8-27B also target coding. Qwen3.8 is described as delivering "substantial gains across coding, professional work, research, and long-horizon agentic tasks". Details are under Q2. — [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B); [Qwen3.5-9B GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/tree/main)
- `tiiuae/Falcon-H1-Tiny-Coder-90M` (2026-01-13, 91M params) exists with GGUF. — [tiiuae listing](https://huggingface.co/api/models?author=tiiuae&sort=createdAt&direction=-1&limit=15)

### Inferences
- These fit fully on GPU with room for KV cache: gpt-oss-20b (12.1 GB), Devstral-Small-2 at IQ4_XS (12.8 GB, tight at long context), all models ≤14B at Q4_K_M, and Seed-Coder/Mellum/FrogNano at Q8.
- The MoE coders (Qwen3-Coder-30B-A3B, Qwen3.6-35B-A3B, GLM-4.7-Flash, Qwen-AgentWorld) at Q4 (17–22 GB) need llama.cpp/Ollama expert offload to CPU RAM. Because only ~3B parameters are active, throughput should stay usable. 32 GB of system RAM covers the spill-over.
- Qwen3-Coder-Next is not practical. IQ3_XXS (28.5 GB) is ~60% of total memory, Q4 (48.5 GB) exceeds 16+32 GB, and the OS needs its share.
- For evolutionary mutation operators, the most cost-effective tier is probably many cheap samples from 4–9B models (Qwen3.5-9B/4B, Seed-Coder-8B, FrogNano-4B). A 20–35B MoE could be reserved for "repair" or "recombination" steps. Diffusion coders (Stable-DiffCoder, DiffuCoder, DiffusionGemma) suit masked/infill-style edits, but runtime support (llama.cpp/Ollama) for their architectures is unverified.
- Licensing: everything above is permissive except `facebook/cwm` (non-commercial research, gated) and `apple/DiffuCoder` (apple-amlr).

### Gaps
- I did not measure tokens/s on a 5060 Ti for any model.
- I found no Windows-specific benchmark for MoE expert offload.
- llama.cpp/Ollama support for the diffusion code architectures (StableDiffcoder, DreamModel) is unverified.
- The FrogNano license conflict (mit metadata vs Apache 2.0 card text) is unresolved.

---

## Q2. Math and reasoning models that fit (incl. 2026 releases)

### Takeaway
Since mid-2026 the Qwen line has moved on: Qwen3.5 (Feb 2026; 0.8B/2B/4B/9B/27B/35B-A3B), Qwen3.6 (Apr 2026; 27B, 35B-A3B), and **Qwen3.8-27B** (2026-08-05; 17,311 likes, the most-liked model surveyed). Google's **Gemma 4** (Mar–May 2026; E2B/E4B/12B/26B-A4B/31B, Apache-2.0) adds strong small reasoning models. For 16 GB, the sweet spot is Gemma-4-12B (Q4_K_M 7.1 GB), Qwen3.5-9B (5.7 GB), Ministral-3-14B-Reasoning, Phi-4-reasoning-plus (9.1 GB), and the 26–35B MoEs with offload. Qwen3.8-27B squeezes in at UD-IQ4_XS (14.3 GB) or UD-IQ3_XXS (10.9 GB), or in a ternary build (Ternary-Bonsai-2-27B, 5.9–7.2 GB).

### Cited Findings
| Repo id | Date | Params | Ctx | License | GGUF / quant sizes (cited) | Card-reported highlights |
|---|---|---|---|---|---|---|
| `Qwen/Qwen3.8-27B` | 2026-08-05 | 27.78B dense. Hybrid layout "16 × (3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))" | 262,144 native, up to 1M | apache-2.0 | Official `-FP8`. NVIDIA `nvidia/Qwen3.8-27B-NVFP4`. unsloth: UD-IQ3_XXS 10.9 GB, UD-IQ4_XS 14.3 GB, Q4_0 16.1 GB, UD-Q4_K_M 16.5 GB, Q5_K_M 19.8 GB | Thinking mode is on by default and tunable via `reasoning_effort`. Ollama: `qwen3.8`. — [HF](https://huggingface.co/Qwen/Qwen3.8-27B); [GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main); [Ollama](https://ollama.com/library/qwen3.8) |
| `prism-ml/Ternary-Bonsai-2-27B-gguf` | 2026-09-16 | 27B-class ternary built on the Qwen3.8-27B backbone | 262K | apache-2.0 | PTQ1_0 5.95 GB; PQ2_0 7.21 GB | The card claims "98.2% of FP16 intelligence retained" (84.78 avg across 14 thinking-mode benchmarks). It needs "custom ternary hybrid-attention kernels for llama.cpp (CUDA, Metal)". 4.39M downloads. — [HF](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) |
| `Qwen/Qwen3.6-27B` | 2026-04-21 | 27.78B | 262,144 | apache-2.0 | unsloth: IQ3_XXS 12.0 GB, IQ4_XS 15.4 GB, Q4_K_M 16.8 GB | The card advises keeping ≥128K context "to preserve thinking capabilities". — [HF](https://huggingface.co/Qwen/Qwen3.6-27B); [GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/tree/main) |
| `Qwen/Qwen3.6-35B-A3B` | 2026-04-15 | 35.95B / 3B active | 262,144 | apache-2.0 | See Q1 (Q4_K_M 22.1 GB) | — [HF](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) |
| `Qwen/Qwen3.5-9B`, `-4B`, `-2B`, `-0.8B` (+ `-Base`) | 2026-02-27/28 | 9.65B / 4.66B / 2.27B / 0.87B | 262,144 | apache-2.0 | 9B unsloth: IQ3_XXS 4.0 GB, Q4_K_M 5.7 GB, Q6_K 7.5 GB | 9B has 8.39M downloads and 4B has 8.02M. Ollama: `qwen3.5`. — [Qwen3.5 listing](https://huggingface.co/api/models?author=Qwen&search=Qwen3.5&sort=downloads&direction=-1&limit=40); [HF 9B](https://huggingface.co/Qwen/Qwen3.5-9B); [Ollama](https://ollama.com/library/qwen3.5) |
| `Qwen/Qwen3.5-27B`, `Qwen/Qwen3.5-35B-A3B` | 2026-02-24 | 27.78B; 35.95B/3B | 262,144 | apache-2.0 | Official FP8 and GPTQ-Int4 repos (2026-03-03) | — [HF](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) |
| `Qwen/Qwen3-4B-Thinking-2507` | 2025-08-05 | 4.02B | 262,144 | apache-2.0 | unsloth/lmstudio GGUF | AIME25 81.3, HMMT25 55.5, GPQA 65.8. — [HF](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) |
| `Qwen/Qwen3-30B-A3B-Thinking-2507` | 2025-07-29 | 30.53B MoE | 262,144 | apache-2.0 | unsloth/bartowski GGUF | — [HF](https://huggingface.co/Qwen/Qwen3-30B-A3B-Thinking-2507) |
| `Qwen/Qwen3-8B`, `Qwen/Qwen3-14B` | 2025-04-27 | 8.19B; 14.77B | 40,960 (config) | apache-2.0 | Official `Qwen/Qwen3-8B-GGUF`, `Qwen/Qwen3-14B-GGUF` | — [HF](https://huggingface.co/Qwen/Qwen3-8B) |
| `google/gemma-4-12B-it` | 2026-05-23 | 11.96B ("Unified": text/image/audio/video in) | 262,144 | apache-2.0 | Official `google/gemma-4-12B-it-qat-q4_0-gguf`, `-qat-w4a16-ct`. unsloth: IQ4_XS 6.4 GB, Q4_K_M 7.1 GB | Card table (31B / 26B A4B / 12B / E4B / E2B): AIME 2026 no tools 89.2 / 88.3 / 77.5 / 42.5 / 37.5. LiveCodeBench v6 80.0 / 77.1 / 72.0 / 52.0 / 44.0. Ollama: `gemma4`. — [HF](https://huggingface.co/google/gemma-4-12B-it); [GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/tree/main); [Ollama](https://ollama.com/library/gemma4) |
| `google/gemma-4-26B-A4B-it` | 2026-03-11 | 25.81B / ~4B active | 262,144 | apache-2.0 | QAT q4_0 GGUF. unsloth: IQ3_XXS 11.4 GB, IQ4_XS 13.6 GB, MXFP4_MOE 16.6 GB, Q4_K_M 16.9 GB | 12.06M downloads. — [HF](https://huggingface.co/google/gemma-4-26B-A4B-it); [GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/tree/main) |
| `google/gemma-4-31B-it`, `google/gemma-4-E4B-it`, `google/gemma-4-E2B-it` | 2026-03-02/11 | 31.27B; 8.00B; 5.12B | 262,144; 131,072; – | apache-2.0 | QAT q4_0 GGUFs | — [Gemma 4 listing](https://huggingface.co/api/models?author=google&search=gemma-4&sort=downloads&direction=-1&limit=40) |
| `openai/gpt-oss-20b` | 2025-08-04 | 20.91B / 3.6B | 131,072 | apache-2.0 | MXFP4 12.1 GB | See Q1. |
| `microsoft/Phi-4-reasoning-plus` | 2025-04-17 | 14.66B | 32,768 | mit | unsloth: IQ4_XS 8.0 GB, Q4_K_M 9.1 GB, Q6_K 12.0 GB | AIME24 81.3, AIME25 78.0, OmniMath 81.9, GPQA-D 68.9. Ollama: `phi4-reasoning`. — [HF](https://huggingface.co/microsoft/Phi-4-reasoning-plus); [GGUF](https://huggingface.co/unsloth/Phi-4-reasoning-plus-GGUF/tree/main); [Ollama](https://ollama.com/library/phi4-reasoning) |
| `microsoft/Phi-4-mini-reasoning`, `microsoft/Phi-4-mini-flash-reasoning` | 2025-04-29; 2025-06-19 | 3.84B; 3.85B (`Phi4FlashForCausalLM` hybrid) | 131,072; 262,144 | mit | mini-reasoning has GGUF. **No GGUF found for flash-reasoning** | — [HF](https://huggingface.co/microsoft/Phi-4-mini-flash-reasoning) |
| `mistralai/Ministral-3-14B-Reasoning-2512` / `-8B-` / `-3B-` | 2025-10-31 (named 2512) | 13.95B / 8.92B / 3.85B | 262,144 | apache-2.0 | Official `-GGUF` repos | 14B: AIME25 0.850, AIME24 0.898, GPQA-D 0.712, LCB 0.646. 8B: AIME25 0.787. Ollama: `ministral-3`. — [HF](https://huggingface.co/mistralai/Ministral-3-14B-Reasoning-2512); [Ollama](https://ollama.com/library/ministral-3) |
| `mistralai/Magistral-Small-2509` | 2025-09-12 | 24.01B | 131,072 | apache-2.0 | Official GGUF. unsloth: IQ4_XS 12.8 GB, Q4_K_M 14.3 GB | Ollama: `magistral`. — [HF](https://huggingface.co/mistralai/Magistral-Small-2509); [GGUF](https://huggingface.co/unsloth/Magistral-Small-2509-GGUF/tree/main) |
| `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` | 2025-05-29 | 8.19B | 131,072 | mit | unsloth/lmstudio GGUF | Ollama: `deepseek-r1`. — [HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B) |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B` | 2025-01-20 | 14.77B | 131,072 | mit | GGUF widely available | — [HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B) |
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 2025-12-04 | 31.58B hybrid Mamba-2/MoE (`NemotronHForCausalLM`) | 262,144 | other: nvidia-nemotron-open-model-license | Official FP8 and NVFP4 (18.24B packed) | Ollama: `nemotron-3-nano`. — [HF](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16) |
| `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | 2026-08-01 | 31.58B "Mamba-2 + MoE + Attention hybrid" | up to 1M | other: openmdw-1.1 | Official NVFP4. mradermacher GGUF sizes look anomalous (Q2_K 18.7 GB, Q4_K_M 25.4 GB) | Ollama: `nemotron-3.5-lightning`. — [HF](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16); [GGUF](https://huggingface.co/mradermacher/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16-GGUF/tree/main) |
| `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | 2026-03-07 | 3.97B | 262,144 | nvidia-nemotron-open-model-license | Official `-GGUF`, `-FP8` | — [HF](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16) |
| `nvidia/NVIDIA-Nemotron-Nano-9B-v2` | 2025-08-12 | 8.89B | 131,072 | nvidia-open-model-license | bartowski GGUF | — [HF](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2) |
| `nvidia/OpenMath-Nemotron-14B`; `nvidia/AceReason-Nemotron-1.1-7B` | 2025-04-22; 2025-06-16 | 14.77B; 7.62B | 131,072 | cc-by-4.0; nvidia-open-model-license | bartowski GGUF | Math-specialized. — [HF](https://huggingface.co/nvidia/OpenMath-Nemotron-14B); [HF](https://huggingface.co/nvidia/AceReason-Nemotron-1.1-7B) |
| `ibm-granite/granite-4.2-8b`; `ibm-granite/granite-4.2-30b` | 2026-08-07 | 8.79B; 29.28B, dense "(Reasoning)" | 128K native (extension to 512K) | apache-2.0 | Official GGUF, FP8, NVFP4, MXFP4. 30B GGUF: Q3_K_M 14.1 GB, Q4_K_M 17.7 GB | Ollama: `granite4.2`. — [HF](https://huggingface.co/ibm-granite/granite-4.2-8b); [GGUF](https://huggingface.co/ibm-granite/granite-4.2-30b-GGUF/tree/main) |
| `allenai/Olmo-3-7B-Think`; `allenai/Olmo-Hybrid-7B` | 2025-11-18; 2026-01-28 | 7.30B; 7.43B | 65,536 | apache-2.0 | Olmo-3 has GGUF. **No GGUF found for Olmo-Hybrid** | A fully open training stack. Ollama: `olmo-3`. — [HF](https://huggingface.co/allenai/Olmo-3-7B-Think); [HF](https://huggingface.co/allenai/Olmo-Hybrid-7B) |
| `tiiuae/Falcon-H1R-7B` | 2025-10-29 | 7.59B hybrid (FalconH1) | 262,144 | other: falcon-llm-license | Official `tiiuae/Falcon-H1R-7B-GGUF` | — [HF](https://huggingface.co/tiiuae/Falcon-H1R-7B) |
| `WeiboAI/VibeThinker-1.5B` | 2025-11-04 | 1.78B | 131,072 | mit | Community GGUF | AIME24 80.3, AIME25 74.4, HMMT25 50.4, LiveCodeBench v6 51.1. The card recommends it for competition math and algorithm coding. — [HF](https://huggingface.co/WeiboAI/VibeThinker-1.5B) |
| `ServiceNow-AI/Apriel-1.6-15b-Thinker` | 2025-11-28 | 14.86B | 262,400 | mit | bartowski GGUF | — [HF](https://huggingface.co/ServiceNow-AI/Apriel-1.6-15b-Thinker) |
| `openbmb/MiniCPM5-2B` | 2026-09-06 | 2.52B | 131,072 | apache-2.0 | Community GGUF | 1.27M downloads, 1,727 likes. — [HF](https://huggingface.co/openbmb/MiniCPM5-2B) |
| `inclusionAI/Ling-3.0-tiny` | 2026-08-10 | 7.89B MoE (BailingMoeV3) | 131,072 | mit | – | — [HF](https://huggingface.co/inclusionAI/Ling-3.0-tiny) |

- Larger 2026 Qwen/DeepSeek releases do not fit and are listed only for context: `Qwen/Qwen3.8-Flash-Next` (180B), `Qwen/Qwen3.8-2.4T-A95B`, `deepseek-ai/DeepSeek-V4-Flash` (290.94B), `DeepSeek-V4.1-Flash` (763B). — [Qwen listing](https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=30); [deepseek listing](https://huggingface.co/api/models?author=deepseek-ai&sort=createdAt&direction=-1&limit=30)
- No official small Qwen3.8 exists in the Qwen org: the Qwen3.8 search returns only 27B, Flash-Next, and 2.4T. Community distills such as `empero-ai/Qwen3.8-9B-Distill-GGUF` exist. — [Qwen3.8 search](https://huggingface.co/api/models?author=Qwen&search=Qwen3.8&sort=createdAt&direction=-1&limit=40)

### Inferences
- Default fully-on-GPU reasoning models for 16 GB: Gemma-4-12B-it (Q4_K_M 7.1 GB), Qwen3.5-9B (Q6_K 7.5 GB), Ministral-3-14B-Reasoning (Q4–Q5), Phi-4-reasoning-plus (Q4_K_M 9.1 GB), and gpt-oss-20b (12.1 GB).
- The flagship option is Qwen3.8-27B at UD-IQ4_XS (14.3 GB). Its ~75% linear-attention layers should keep KV-cache growth small (the Bonsai card describes the backbone as "~75% linear attention"), so it may hold useful context in the remaining ~1.5 GB. This needs empirical checking.
- Ternary-Bonsai-2-27B (5.9–7.2 GB) would leave >8 GB for KV/batching. It depends on custom llama.cpp kernels, and whether those are upstream or a fork is unverified. The "98.2% retained" figure is a vendor claim.
- Most of these models are thinking-mode by default (Qwen3.6/3.8, Gemma 4 with thinking, Magistral), so output-length budgets dominate wall-clock time in an evolutionary loop.

### Gaps
- I did not extract Qwen3.8-27B or Qwen3.5 benchmark numbers; their cards render benchmarks as HTML.
- I did not independently verify benchmark numbers. All are card claims.
- I did not confirm whether Ternary-Bonsai kernels are merged in upstream llama.cpp or Ollama.
- The Nemotron-3.5-Lightning GGUF sizes look anomalous and are unexplained.

---

## Q3. Small formal theorem provers and Lean tooling

### Takeaway
The best ≤8B Lean 4 provers that run comfortably on 16 GB are **Pythagoras-Prover-4B** (2026-06; 86.07% miniF2F pass@32 claimed; Q4_K_M 2.7 GB) and **Goedel-Prover-V2-8B** (83.0% pass@32; Q4_K_M 5.0 GB; has a compiler-feedback self-correction mode). DeepSeek-Prover-V2-7B, Kimina-Prover-Distill-8B/1.7B/0.6B, and BFS-Prover-V2-7B (step-level, tree search) round out the set. Mistral's **Leanstral** (Mar/Jul 2026) is 119B-A6.5B and does not fit. For tooling, use `leanprover-community/repl`, `kimina-lean-server`, `LeanInteract`, `lean-lsp-mcp`, and `LeanDojo-v2`.

### Cited Findings
| Repo id | Date | Params | Ctx | License | GGUF (cited size) | Card claims |
|---|---|---|---|---|---|---|
| `Pythagoras-LM/Pythagoras-Prover-4B` | 2026-06-07 | 4.41B (Qwen3) | 40,960 | apache-2.0 | `tinyopsec/Pythagoras-Prover-4B-GGUF` (3rd-party): q4_k_m 2.7 GB, q8_0 4.7 GB | "86.07% on MiniF2F-Test at Pass@32". Exceeds DeepSeek-Prover-V2-671B's pass@8192 (88.9%) at pass@2048. Uses Lean 4.9.0-rc1 with a 30K-token generation limit. — [HF](https://huggingface.co/Pythagoras-LM/Pythagoras-Prover-4B); [GGUF](https://huggingface.co/tinyopsec/Pythagoras-Prover-4B-GGUF/tree/main) |
| `Pythagoras-LM/Pythagoras-Prover-32B` | 2026-07-23 | 32.76B | 40,960 | apache-2.0 | mradermacher GGUF | 93.03% MiniF2F-Test. 93/672 PutnamBench. — [HF](https://huggingface.co/Pythagoras-LM/Pythagoras-Prover-32B) |
| `Pythagoras-LM/Pythagoras-Prover-Diffusion-4B` | 2026-06-08 | 4.02B | – | (not checked) | – | Described as "the first diffusion-based theorem prover". — [prover search](https://huggingface.co/api/models?search=Prover&sort=createdAt&direction=-1&limit=30); [card](https://huggingface.co/Pythagoras-LM/Pythagoras-Prover-4B) |
| `Goedel-LM/Goedel-Prover-V2-8B` | 2025-07-15 | 8.19B (Qwen3) | 40,960 | apache-2.0 | mradermacher: Q4_K_M 5.0 GB, Q8_0 8.7 GB | "83.0% on MiniF2F test set at Pass@32". Self-correction mode uses Lean compiler feedback for 2 revision rounds. Uses Lean 4.9 + Mathlib per the DeepSeek-Prover-V1.5 setup. — [HF](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B); [GGUF](https://huggingface.co/mradermacher/Goedel-Prover-V2-8B-GGUF/tree/main) |
| `Goedel-LM/Goedel-Prover-V2-32B` | 2025-07-14 | 32.76B | 40,960 | apache-2.0 | mradermacher i1 GGUF | 88.0% MiniF2F pass@32. — [HF](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-32B) |
| `Goedel-LM/Goedel-Formalizer-V2-8B` | 2025-07-20 | 8.19B | 40,960 | apache-2.0 | mradermacher GGUF | Autoformalizer. — [HF](https://huggingface.co/Goedel-LM/Goedel-Formalizer-V2-8B) |
| `Goedel-LM/Goedel-Code-Prover-8B` | 2026-03-25 | 8.19B | 40,960 | apache-2.0 | `mradermacher/Goedel-Code-Prover-8B-GGUF` | Lean 4 code-verification proof decomposition ("decompose-then-verify"), trained with SFT + GRPO using online Lean rewards. arXiv 2603.19329. — [HF](https://huggingface.co/Goedel-LM/Goedel-Code-Prover-8B) |
| `deepseek-ai/DeepSeek-Prover-V2-7B` | 2025-04-30 | 6.91B | 65,536 (config). The card says "extended context length of up to 32K" | not in metadata (the card has a License section; not read) | unsloth: Q4_K_M 4.2 GB, Q6_K 5.7 GB | The 671B sibling reaches 88.9% miniF2F and 49/658 PutnamBench. The card does not report a 7B figure in the extracted lines. — [HF](https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-7B); [GGUF](https://huggingface.co/unsloth/DeepSeek-Prover-V2-7B-GGUF/tree/main) |
| `AI-MO/Kimina-Prover-Distill-8B`; `-Distill-1.7B`; `-Distill-0.6B`; `-RL-1.7B`; `-RL-0.6B` | 2025-07-04 … 2025-08-12 | 8.19B / 2.03B / 0.75B | 40,960 | apache-2.0 | gabriellarson/mradermacher GGUF | 8B is a distillation of Kimina-Prover-72B. The card says it "achieves 77.86% ac[curacy]…"; I truncated the benchmark name during extraction (see Gaps). — [HF](https://huggingface.co/AI-MO/Kimina-Prover-Distill-8B); [AI-MO listing](https://huggingface.co/api/models?author=AI-MO&sort=createdAt&direction=-1&limit=20) |
| `AI-MO/Kimina-Autoformalizer-7B` | 2025-04-13 | 7.62B | 32,768 | apache-2.0 | mradermacher GGUF | — [HF](https://huggingface.co/AI-MO/Kimina-Autoformalizer-7B) |
| `ByteDance-Seed/BFS-Prover-V2-7B`; `-32B` | 2025-10-06; 2025-09-30 | 7.62B; 32.76B | 4,096 (7B config); 131,072 (32B) | apache-2.0 | mradermacher GGUF | Step-level tactic prover. The system (with planner-enhanced multi-agent tree search) reports 95.08% miniF2F and 41.4% ProofNet. — [HF](https://huggingface.co/ByteDance-Seed/BFS-Prover-V2-7B) |
| `internlm/internlm2_5-step-prover` | 2024-10-21 | – | 8,192 | other | tensorblock GGUF | — [HF](https://huggingface.co/internlm/internlm2_5-step-prover) |
| `mistralai/Leanstral-2603`; `mistralai/Leanstral-1.5-119B-A6B` | 2026-03-11; 2026-07-01 | 119B / 6.5B active | 256K | apache-2.0 | Community GGUFs | "first open-source code agent designed for Lean 4", part of the Mistral Small 4 family. Too large for this machine. — [HF](https://huggingface.co/mistralai/Leanstral-2603); [HF](https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B) |
| `saccha-ai/Sequent-Prover-9B-Preview` | 2026-06-12 | 9.41B (Qwen3.5) | 262,144 | none listed | – | 3 downloads. Low signal. — [HF](https://huggingface.co/saccha-ai/Sequent-Prover-9B-Preview) |
| `anonymous-submission-ICLR2027/Gobble-Prover-1.7B` | 2026-09-18 | 2.03B | – | – | `mradermacher/Gobble-Prover-1.7B-GGUF` | An anonymous ICLR 2027 submission. UNVERIFIED claims. — [prover search](https://huggingface.co/api/models?search=Prover&sort=createdAt&direction=-1&limit=30) |

Lean tooling (GitHub API, 2026-10-09):
- `leanprover-community/repl`: 233 stars, Apache-2.0, last push 2026-10-07. "A simple REPL for Lean 4, returning information about errors and sorries." — [GitHub](https://github.com/leanprover-community/repl)
- `project-numina/kimina-lean-server`: 212 stars, MIT, last push 2026-01-11. Lean server plus client SDK, used for batch verification. — [GitHub](https://github.com/project-numina/kimina-lean-server)
- `augustepoiroux/LeanInteract`: 132 stars, MIT, last push 2026-07-17. Python interface for Lean 4. — [GitHub](https://github.com/augustepoiroux/LeanInteract)
- `oOo0oOo/lean-lsp-mcp`: 525 stars, MIT, last push 2026-09-30. Lean Theorem Prover MCP server. — [GitHub](https://github.com/oOo0oOo/lean-lsp-mcp)
- `lean-dojo/LeanDojo-v2`: 143 stars, Apache-2.0, last push 2026-08-10. "end-to-end framework for training, evaluating, and deploying AI-assisted theorem provers for Lean 4". `lean-dojo/LeanDojo`: 843 stars, MIT, last push 2026-01-18. — [GitHub](https://github.com/lean-dojo/LeanDojo-v2); [GitHub](https://github.com/lean-dojo/LeanDojo)
- `lenianiva/PyPantograph` returned "Moved Permanently" from the GitHub API, so its current location is UNVERIFIED. — [GitHub API](https://api.github.com/repos/lenianiva/PyPantograph)

### Inferences
- Several provers could stay resident together on 16 GB, e.g. Pythagoras-4B Q8 (4.7 GB) + Goedel-V2-8B Q4_K_M (5.0 GB) + DeepSeek-Prover-V2-7B Q4_K_M (4.2 GB) ≈ 14 GB. That enables a prover ensemble with high pass@k sampling while Lean verification runs on CPU.
- The headline numbers are pass@32 or more. Real usefulness depends on sampling budget and Lean verification throughput (CPU-bound), so a fast REPL/server matters more than model size.
- Lean/Mathlib version pinning differs between provers (Lean 4.9 for Goedel/DeepSeek lineage; 4.9.0-rc1 for Pythagoras). A shared verification server must match each prover's expected Mathlib, or prompts and proofs will fail spuriously.

### Gaps
- I did not determine the Kimina-Prover-Distill-8B 77.86% benchmark name.
- I did not read the DeepSeek-Prover-V2-7B license text; the metadata field is empty.
- I did not verify Leanstral GGUF sizes.
- I did not check whether `kimina-lean-server` or the Lean REPL run natively on Windows; WSL2 may be required.

---

## Q4. Embedding and reranker models for semantic search over a technical corpus

### Takeaway
The strongest local options that fit easily:
- **Qwen3-Embedding-0.6B/4B/8B**: 32K context; MRL from 32 up to 1024/2560/4096 dims; 8B was #1 on MTEB multilingual at 70.58 on 2025-06-05. Available in Ollama.
- **jina-embeddings-v5-text-small/nano** (Jan 2026): 71.7 MTEB-Eng-v2 at 677M params, but CC-BY-NC.
- **microsoft/harrier-oss-v1-0.6b** (Mar 2026): MTEB v2 69.0, MIT.
- **nvidia Nemotron-3-Embed-1B/8B** (Jul 2026): 32K context, sliceable dims.
- **google/embeddinggemma-2** (2026-09-14): 740M, multimodal, 768-d MRL, 8K context, Apache-2.0, in Ollama.

BGE-M3 remains the dense+sparse+multivector option. For rerankers: Qwen3-Reranker-0.6B/4B, jina-reranker-v3.5 (NC license), mxbai-rerank-large-v2 (Apache), bge-reranker-v2-m3.

### Cited Findings
| Repo id | Date | Params | Dim (MRL) | Max tokens | License | MTEB / quality (card claims) | Ollama |
|---|---|---|---|---|---|---|---|
| `Qwen/Qwen3-Embedding-0.6B` | 2025-06-03 | 0.60B | up to 1024, user-defined 32–1024 | 32K | apache-2.0 | MTEB multilingual mean(task) 64.33; MTEB Eng v2 70.70 | `qwen3-embedding` ✔ — [HF](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B); [Ollama](https://ollama.com/library/qwen3-embedding) |
| `Qwen/Qwen3-Embedding-4B` | 2025-06-03 | 4.02B | up to 2560 (MRL) | 32K | apache-2.0 | multilingual 69.45; Eng v2 74.60 | ✔ — [HF](https://huggingface.co/Qwen/Qwen3-Embedding-4B) |
| `Qwen/Qwen3-Embedding-8B` | 2025-06-03 | 7.57B | up to 4096, 32–4096 | 32K | apache-2.0 | "No.1 in the MTEB multilingual leaderboard (as of June 5, 2025, score 70.58)". Official GGUF: Q4_K_M 4.7 GB, Q8_0 8.0 GB | ✔ — [HF](https://huggingface.co/Qwen/Qwen3-Embedding-8B); [GGUF](https://huggingface.co/Qwen/Qwen3-Embedding-8B-GGUF/tree/main) |
| `Qwen/Qwen3-VL-Embedding-2B` / `-8B` | 2026-01-07 | 2.13B / 8.14B | – | – | (not checked) | Multimodal | – — [listing](https://huggingface.co/api/models?author=Qwen&search=Embedding&sort=createdAt&direction=-1&limit=25) |
| `google/embeddinggemma-2` | 2026-09-14 | 0.74B | 768 native; MRL 512/256/128 | 8,192 | apache-2.0 (not gated) | MTEB multilingual v2 61.36; Eng v2 68.46; Code v1 78.68 (768d). Near-lossless to 256d. Text, image, video, and audio share one space | `embeddinggemma-2` ✔ — [HF](https://huggingface.co/google/embeddinggemma-2); [GGUF](https://huggingface.co/unsloth/embeddinggemma-2-GGUF/tree/main); [Ollama](https://ollama.com/library/embeddinggemma-2) |
| `google/embeddinggemma-300m` | 2025-07-17 | 0.30B | 768; MRL 512/256/128 | 2,048 | gemma (gated=manual) | – | `embeddinggemma` ✔ — [HF](https://huggingface.co/google/embeddinggemma-300m) |
| `jinaai/jina-embeddings-v5-text-small` | 2026-01-22 | 0.60B (card: 677M) | 1024; MRL 32–1024 | 32,768 | **cc-by-nc-4.0** | 71.7 MTEB English v2; 67.7 MMTEB, "highest among multilingual embedding models under 1B" | ✘ (no `jina-embeddings-v5` page) — [HF](https://huggingface.co/jinaai/jina-embeddings-v5-text-small) |
| `jinaai/jina-embeddings-v5-text-nano` | 2026-01-22 | 0.21B (card: 239M) | 768; MRL 32–768 | 8,192 | cc-by-nc-4.0 | 71.0 MTEB Eng v2; 65.5 MMTEB | ✘. Official `-retrieval-GGUF` exists — [HF](https://huggingface.co/jinaai/jina-embeddings-v5-text-nano) |
| `jinaai/jina-code-embeddings-1.5b` (+ `-0.5b`) | 2025-08-26 | 1.54B | 1536; MRL 128–1536 | 32,768 | cc-by-nc-4.0 | Code retrieval | Official GGUF — [HF](https://huggingface.co/jinaai/jina-code-embeddings-1.5b) |
| `microsoft/harrier-oss-v1-0.6b` (+ `-270m`, `-27b`) | 2026-03-30 | 0.60B (270M / 27B) | 1024 (640 / 5376) | 32,768 | mit | MTEB v2: 69.0 (270m 66.5; 27b 74.3), SOTA on Multilingual MTEB v2 "as of the release date" | ✘ — [HF](https://huggingface.co/microsoft/harrier-oss-v1-0.6b) |
| `nvidia/Nemotron-3-Embed-1B-BF16` | 2026-07-14 | 1.14B (pruned from Ministral-3-3B) | 2048, sliceable (e.g. 1024/512) | 32,768 | other: openmdw-1.1 | – | ✘ — [HF](https://huggingface.co/nvidia/Nemotron-3-Embed-1B-BF16) |
| `nvidia/Nemotron-3-Embed-8B-BF16` | 2026-07-14 | 7.95B | 4096, sliceable | 32,768 | openmdw-1.1 | "state-of-the-art performance on the multilingual RTEB leaderboard as of July 16, 2026" | ✘ — [HF](https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16) |
| `nvidia/llama-embed-nemotron-8b` | 2025-10-07 | 7.50B | – | 131,072 (config) | other: customized-nscl-v1 | – | ✘ — [HF](https://huggingface.co/nvidia/llama-embed-nemotron-8b) |
| `perplexity-ai/pplx-embed-v1-0.6b` / `-4b` (+ `-context-` variants) | 2026-01-14/20 | 0.60B / 4.02B | 1024 / 2560, MRL, INT8/BINARY | 32K | mit | – | ✘ — [HF](https://huggingface.co/perplexity-ai/pplx-embed-v1-0.6b) |
| `BAAI/bge-m3` | 2024-01-27 | ~0.57B (XLM-R) | 1024 | 8,192 | mit | Dense + sparse (lexical weights) + ColBERT multi-vector in one model. Qwen's table lists it at 59.56 multilingual MTEB | `bge-m3` ✔ — [HF](https://huggingface.co/BAAI/bge-m3); [Ollama](https://ollama.com/library/bge-m3) |
| `BAAI/bge-reasoner-embed-qwen3-8b-0923` | 2025-09-22 | 7.57B | – | – | (not checked) | Reasoning-intensive retrieval | – — [BAAI listing](https://huggingface.co/api/models?author=BAAI&pipeline_tag=feature-extraction&sort=createdAt&direction=-1&limit=10) |
| `nomic-ai/nomic-embed-text-v1.5` | 2024-02-10 | 0.14B | 768, Matryoshka (e.g. 512) | 8,192 (tokenizer `model_max_length`) | apache-2.0 | – | `nomic-embed-text` ✔ — [HF](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5); [Ollama](https://ollama.com/library/nomic-embed-text) |
| `nomic-ai/nomic-embed-text-v2-moe` | 2025-02-07 | 0.48B MoE | 768→256 Matryoshka | **512** | apache-2.0 | – | `nomic-embed-text-v2-moe` ✔ — [HF](https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe) |
| `nomic-ai/nomic-embed-code` | 2025-03-24 | 7.07B | – | 32,768 | apache-2.0 | Code retrieval (CoRNStack) | Official GGUF — [HF](https://huggingface.co/nomic-ai/nomic-embed-code) |
| `Snowflake/snowflake-arctic-embed-l-v2.0` / `-m-v2.0` | 2024-11-08 | 0.57B / 0.31B | (MRL; dims not extracted) | 8,194 / 8,192 | apache-2.0 | – | `snowflake-arctic-embed2` ✔ — [HF](https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0); [Ollama](https://ollama.com/library/snowflake-arctic-embed2) |
| `mixedbread-ai/mxbai-embed-large-v1` | 2024-03-07 | 0.34B | (dims not extracted) | 512 | apache-2.0 | – | `mxbai-embed-large` ✔ — [HF](https://huggingface.co/mixedbread-ai/mxbai-embed-large-v1); [Ollama](https://ollama.com/library/mxbai-embed-large) |
| `ibm-granite/granite-embedding-english-r2`; `granite-embedding-311m-multilingual-r2` | 2025-07-17; 2026-04-20 | 0.15B; 0.31B (ModernBERT) | 768 | 8,192; 32,768 | apache-2.0 | Card reports BEIR, MTEB-v2, CoIR (code), MLDR, LongEmbed | `granite-embedding` ✔ — [HF](https://huggingface.co/ibm-granite/granite-embedding-english-r2); [Ollama](https://ollama.com/library/granite-embedding) |
| `LiquidAI/LFM2.5-Embedding-350M` | 2026-05-05 | 0.35B | 1024 (CLS) | 512 (sentence-transformers config) | other: lfm1.0 | – | – — [HF](https://huggingface.co/LiquidAI/LFM2.5-Embedding-350M) |
| `Alibaba-NLP/gte-modernbert-base`; `lightonai/GTE-ModernColBERT-v1` | 2025-01-20; 2025-04-30 | 0.15B | – | 8,192 | apache-2.0 | ColBERT late-interaction variant (PyLate) | – — [HF](https://huggingface.co/lightonai/GTE-ModernColBERT-v1) |

Rerankers:
- `Qwen/Qwen3-Reranker-0.6B` / `-4B` / `-8B` (2025-05/06; 32K; apache-2.0). — [HF](https://huggingface.co/Qwen/Qwen3-Reranker-4B)
- `jinaai/jina-reranker-v3.5` (2026-07-14; 0.6B; listwise; up to 131K tokens; cc-by-nc-4.0; official GGUF). Its card reports BEIR nDCG@10 63.20 vs Qwen3-Reranker-4B 62.28, mxbai-rerank-large-v2 62.45, and Qwen3-Reranker-0.6B 56.94. — [HF](https://huggingface.co/jinaai/jina-reranker-v3.5)
- `mixedbread-ai/mxbai-rerank-large-v2` (1.54B, apache-2.0, 32K). — [HF](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2)
- `BAAI/bge-reranker-v2-m3` (0.57B, apache-2.0, 8,194). — [HF](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- Ollama has no `qwen3-reranker` library page (404); there is a GGUF at `ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF`. — [text-ranking trending](https://huggingface.co/api/models?pipeline_tag=text-ranking&sort=trendingScore&direction=-1&limit=20)
- Trending in Sept–Oct 2026: `Contrastive-LM/CLM-v0.1-8B` (text-ranking, 2026-09-21), `perplexity-ai/pplx-embed-v2-late-0.6b`, and `-v2-late-9b` (late-interaction). I did not vet these. — [feature-extraction trending](https://huggingface.co/api/models?pipeline_tag=feature-extraction&sort=trendingScore&direction=-1&limit=30)

### Inferences
- **Pragmatic default** for a technical/code research corpus, all local and Apache: Qwen3-Embedding-0.6B or -4B via Ollama (MRL lets you store 256–1024 dims) plus Qwen3-Reranker-0.6B/4B via transformers. If code and multimodal matter and storage is tight, embeddinggemma-2 at 256d is the alternative.
- jina v5 has the best quality-per-parameter in this list, but CC-BY-NC may be a problem if outputs are ever commercialized.
- Context-length traps for long technical docs: nomic-embed-text-v2-moe (512), mxbai-embed-large (512), and LFM2.5-Embedding (512 configured) need aggressive chunking. Qwen3, jina-v5-small, harrier, Nemotron-3-Embed, and pplx all take 32K.
- An 8B embedder (Q4_K_M 4.7 GB) can sit alongside a ~9 GB generator on 16 GB.

### Gaps
- I did not fetch the live MTEB leaderboard (it is a Space), so all standings are card claims at their own dates.
- Not extracted: dimensions for mxbai-embed-large and snowflake-arctic-embed-l-v2.0, and MTEB numbers for granite r2 and Nemotron-3-Embed.
- I checked only that Ollama library pages exist, not which tags or quantizations are offered.

---

## Q5. World-model / recursive-reasoning checkpoints (HRM, TRM) and non-transformer models with HF weights

### Takeaway
- **HRM:** official task checkpoints exist (ARC-2, Sudoku-Extreme, Maze-30x30), as does a new 1.18B **HRM-Text-1B** language model (2026-05-17, Apache-2.0, pre-alignment).
- **TRM:** no official HF checkpoint was found. The official repo (7M params; 45% ARC-AGI-1 / 8% ARC-AGI-2) ships code only, and community checkpoints (e.g. `gaoxin492/TinyRecursiveModels-*`) are unvetted.
- **Non-transformer families:** RWKV-7 is active (G1k checkpoints 2026-09-30, up to 13.3B), as is Liquid LFM2/LFM2.5 (to 8B-A1B). Mamba hybrids are now mainstream (Nemotron-H/3, Granite-4.0-H, Falcon-H1/H1R), and Qwen3.5+/3.8 use Gated DeltaNet linear attention.
- **Diffusion LMs:** LLaDA, Dream, DiffusionGemma, Nemotron-Labs-Diffusion.
- **World models:** the most relevant new one is **Qwen-AgentWorld-35B-A3B** (2026-06-22), a language world model simulating 7 agent environments.

### Cited Findings
Recursive / hierarchical reasoning:
- `sapientinc/HRM-checkpoint-ARC-2`, `sapientinc/HRM-checkpoint-sudoku-extreme`, `sapientinc/HRM-checkpoint-maze-30x30-hard`: createdAt 2025-07-21; no license or safetensors metadata in the API. — [HF](https://huggingface.co/sapientinc/HRM-checkpoint-ARC-2); [sapientinc listing](https://huggingface.co/api/models?author=sapientinc&sort=createdAt&direction=-1&limit=20)
- `sapientinc/HRM-Text-1B`: 2026-05-17, 1.18B, `HrmTextForCausalLM`, context 4,096, apache-2.0, 823 likes. "dual-timescale recurrent architecture: two Transformer modules (H… L…) iterate… for H_cycles × (L_cycles + 1) steps". It is a **pre-alignment** PrefixLM checkpoint, not a chat model. A newer `sapientinc/HRM-Text-1B-v3.2` appeared 2026-09-24. A community GGUF exists (`sinimiini/HRM-Text-1B-GGUF`). Not in Ollama. — [HF](https://huggingface.co/sapientinc/HRM-Text-1B); [HRM search](https://huggingface.co/api/models?search=HRM&sort=downloads&direction=-1&limit=20)
- Official code `sapientinc/HRM`: 12,650 stars, Apache-2.0, last push 2026-03-31. — [GitHub](https://github.com/sapientinc/HRM)
- TRM: `SamsungSAILMontreal/TinyRecursiveModels` has 6,556 stars, MIT, last push 2026-04-01. Its README says "achieves amazing scores of 45% on ARC-AGI-1 and 8% on ARC-AGI-2 using a tiny 7M parameters neural network", and the training recipe assumes 4×H100. The README has no HF checkpoint link, and the SamsungSAILMontreal HF org listing shows no TRM checkpoint. — [GitHub](https://github.com/SamsungSAILMontreal/TinyRecursiveModels); [HF org listing](https://huggingface.co/api/models?author=SamsungSAILMontreal&sort=createdAt&direction=-1&limit=10)
- Community TRM checkpoints (provenance UNVERIFIED): `gaoxin492/TinyRecursiveModels-ARC-AGI-1`, `-ARC-AGI-2`, `-Sudoku-Extreme-mlp`, `-Sudoku-Extreme-att`, `gaoxin492/TinyRecursiveModel-Maze-Hard` (2025-10-11/13, apache-2.0, 0 downloads), and `ainz/tiny-recursive-model` (40M). Community HRM: `zbloss/HRM-sudoku-extreme` (27M). — [TinyRecursive search](https://huggingface.co/api/models?search=TinyRecursive&sort=downloads&direction=-1&limit=20); [HF](https://huggingface.co/gaoxin492/TinyRecursiveModels-ARC-AGI-2)

World models:
- `Qwen/Qwen-AgentWorld-35B-A3B`: 2026-06-22, 34.66B / 3B active, 262,144 ctx, apache-2.0. "a native language world model trained for agentic environment simulation… predicting the next environment state given an agent's action and interaction history". It covers MCP, Search, Terminal, SWE, Android, Web, and OS. unsloth GGUF: IQ3_XXS 13.7 GB, IQ4_XS 17.8 GB, Q4_K_M 22.1 GB. Not in Ollama. — [HF](https://huggingface.co/Qwen/Qwen-AgentWorld-35B-A3B); [GGUF](https://huggingface.co/unsloth/Qwen-AgentWorld-35B-A3B-GGUF/tree/main)
- `facebook/cwm` (Code World Model, 32.58B, non-commercial research license, gated). — [HF](https://huggingface.co/facebook/cwm)
- `facebook/vjepa2-vitl-fpc64-256` (V-JEPA 2, 0.33B, MIT, video). — [HF](https://huggingface.co/facebook/vjepa2-vitl-fpc64-256)

RWKV-7:
- `BlinkDL/rwkv7-g1`: raw weights, apache-2.0, created 2025-03-07.
- `RWKV/RWKV7-G1k-{1.5B,2.9B,7.2B,13.3B}-20260930`: HF-transformers `Rwkv7ForCausalLM`, 2026-09-30, apache-2.0.
- `fla-hub/RWKV7-G1j-*-20260831`: flash-linear-attention format, ctx 16,384 in config.
- Not in Ollama (`rwkv7` returns 404).
— [RWKV listing](https://huggingface.co/api/models?author=RWKV&sort=createdAt&direction=-1&limit=12); [fla-hub listing](https://huggingface.co/api/models?author=fla-hub&sort=createdAt&direction=-1&limit=12); [HF](https://huggingface.co/BlinkDL/rwkv7-g1)

Liquid AI (LFM, license `lfm1.0`):
- `LiquidAI/LFM2-8B-A1B` (2025-10-07, 8.34B MoE, 128K).
- `LiquidAI/LFM2.5-8B-A1B` (2026-05-28, 8.47B, 128K, official GGUF).
- `LiquidAI/LFM2.5-2.6B` (2026-07-28, 131,072, official GGUF, 993K GGUF downloads).
- `LiquidAI/LFM2.5-1.2B-Instruct` (2026-01-06).
- `LiquidAI/LFM2.5-230M` / `-350M`.
- `LiquidAI/d1-3B` (2026-10-05, VL, 32,768). Not checked whether this is a diffusion model despite the name.
- DSpark speculative-decoding drafters for LFM2.5 (2026-08-10).
- Ollama: `lfm2`, `lfm2.5` ✔.
— [LiquidAI listing](https://huggingface.co/api/models?author=LiquidAI&search=LFM2&sort=downloads&direction=-1&limit=25); [HF](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B); [Ollama](https://ollama.com/library/lfm2.5)

Mamba / SSM hybrids:
- `state-spaces/mamba2-2.7b` (apache-2.0). — [HF](https://huggingface.co/state-spaces/mamba2-2.7b)
- `tiiuae/falcon-mamba-7b-instruct` (falcon-mamba license). — [HF](https://huggingface.co/tiiuae/falcon-mamba-7b-instruct)
- `mistralai/Mamba-Codestral-7B-v0.1` (pure Mamba-2 code model, apache-2.0). — [HF](https://huggingface.co/mistralai/Mamba-Codestral-7B-v0.1)
- `nvidia/Nemotron-H-8B-Reasoning-128K` (license `nvidia-internal-scientific-research-and-development-model-license`). — [HF](https://huggingface.co/nvidia/Nemotron-H-8B-Reasoning-128K)
- `Zyphra/Zamba2-7B-instruct` (apache-2.0, 4,096). — [HF](https://huggingface.co/Zyphra/Zamba2-7B-instruct)
- `tiiuae/Falcon-H1-7B-Instruct` (262,144). — [HF](https://huggingface.co/tiiuae/Falcon-H1-7B-Instruct)
- `ibm-granite/granite-4.0-h-tiny` (6.94B `GraniteMoeHybrid`, apache-2.0, 131,072). — [HF](https://huggingface.co/ibm-granite/granite-4.0-h-tiny)
- `allenai/Olmo-Hybrid-7B`. — [HF](https://huggingface.co/allenai/Olmo-Hybrid-7B)
- ByteDance "AHN" Mamba2/GatedDeltaNet memory adapters for Qwen2.5 (12–61M params, 2025-10-08), e.g. `ByteDance-Seed/AHN-GDN-for-Qwen-2.5-Instruct-7B`. — [ByteDance-Seed listing](https://huggingface.co/api/models?author=ByteDance-Seed&sort=createdAt&direction=-1&limit=30)

Diffusion LMs:
- `GSAI-ML/LLaDA-8B-Instruct` (mit, 4,096). — [HF](https://huggingface.co/GSAI-ML/LLaDA-8B-Instruct)
- `inclusionAI/LLaDA2.0-mini` (16.26B MoE, apache-2.0, 32,768). — [HF](https://huggingface.co/inclusionAI/LLaDA2.0-mini)
- `Dream-org/Dream-v0-Instruct-7B` (apache-2.0). — [HF](https://huggingface.co/Dream-org/Dream-v0-Instruct-7B)
- `nvidia/Nemotron-Labs-Diffusion-3B` (2026-03-02, nemotron open license, 262,144). — [HF](https://huggingface.co/nvidia/Nemotron-Labs-Diffusion-3B)
- `google/diffusiongemma-26B-A4B-it` (2026-06-09, apache-2.0). Uses block-autoregressive discrete diffusion. The card reports AIME 2026 69.1% vs 88.3% for the autoregressive 26B A4B, and LiveCodeBench v6 69.1% vs 77.1%. unsloth GGUF exists. — [HF](https://huggingface.co/google/diffusiongemma-26B-A4B-it)
- Diffusion coders and provers are listed in Q1/Q3.

Ternary / low-bit:
- `prism-ml/Ternary-Bonsai-2-27B-gguf` (see Q2). — [HF](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf)
- `tiiuae/Falcon3-10B-Base-1.58bit-prequantized` and `tiiuae/Falcon-E-3B-Base-prequantized` (2026-04). — [tiiuae listing](https://huggingface.co/api/models?author=tiiuae&sort=createdAt&direction=-1&limit=15)

### Inferences
- HRM and TRM task checkpoints are tiny (~7–27M params). They run trivially on any GPU but only within their original puzzle task formats. Their value to Prometheus is as mechanism baselines and ablation subjects, not as general reasoners.
- HRM-Text-1B is the only "recursive-depth" LM with a sizeable public checkpoint. Expect it to need few-shot prompting, since it is not instruction-tuned.
- Qwen-AgentWorld could serve as a cheap simulated environment (terminal/SWE/OS) for evaluating evolved agents without real execution, at IQ3_XXS 13.7 GB on GPU or Q4 with offload. Its fidelity is a vendor claim and would need falsification against real environments before any result rests on it.
- Linear-attention hybrids (Qwen3.5/3.6/3.8 Gated DeltaNet, Nemotron-H, Granite-H, LFM2, RWKV-7) grow KV/state much more slowly with context. That suits long evolutionary transcripts on 16 GB.

### Gaps
- I did not verify that the community TRM checkpoints load or reproduce any reported score.
- The license of the HRM task checkpoints is not in metadata.
- llama.cpp/Ollama support for HRM-Text, RWKV7-G1k (HF format), and the diffusion LMs is unverified; RWKV and HRM have no Ollama library page.

---

## Q6. Programmatic discovery: HF Hub API, daily papers API, VRAM-fit metadata, rate limits

### Takeaway
`GET https://huggingface.co/api/models` supports `search`, `author`, `pipeline_tag`, `library`, `filter`, `apps`, `num_parameters=min:X,max:Y`, `sort` (createdAt / downloads / trendingScore were confirmed), `direction`, `limit`, and `expand[]` (30 allowed values, including `safetensors`, `gguf`, `config`, `cardData`, `baseModels`, `trendingScore`). File sizes come from `/api/models/{id}/tree/main?recursive=true`, and papers from `/api/daily_papers` (params `p, limit, date, week, month, submitter, sort=publishedAt|trending`). Anonymous access is limited to 500 API / 3,000 resolver / 100 page requests per 5-minute fixed window per IP. A free token gives 1,000 / 5,000 / 200.

### Cited Findings
- Allowed `expand[]` values, verbatim from the API's validation error on 2026-10-09: author, baseModels, cardData, config, createdAt, disabled, downloads, downloadsAllTime, evalResults, gated, inference, inferenceProviderMapping, lastModified, library_name, likes, mask_token, model-index, pipeline_tag, private, safetensors, sha, siblings, spaces, tags, transformersInfo, trendingScore, widgetData, gguf, resourceGroup, xetEnabled. An invalid `sort` returns "Invalid sort parameter". — [API probe](https://huggingface.co/api/models?limit=1&expand[]=bogus)
- Parameters exercised successfully on 2026-10-09 (HTTP 200 with plausible filtered results):
  - `author=Qwen&sort=createdAt&direction=-1` — [example](https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=30)
  - `search=Prover&sort=downloads`
  - `pipeline_tag=feature-extraction&sort=trendingScore`
  - `pipeline_tag=text-generation&library=gguf&sort=trendingScore` — [example](https://huggingface.co/api/models?pipeline_tag=text-generation&library=gguf&sort=trendingScore&direction=-1&limit=25)
  - `apps=ollama&sort=trendingScore` — [example](https://huggingface.co/api/models?apps=ollama&sort=trendingScore&direction=-1&limit=15)
  - `num_parameters=min:0,max:24B&pipeline_tag=text-generation&sort=trendingScore` — [example](https://huggingface.co/api/models?num_parameters=min:0,max:24B&pipeline_tag=text-generation&sort=trendingScore&direction=-1&limit=30)
  - `filter=gguf&search={name}`, used to find GGUF mirrors.
- Per-model metadata useful for a VRAM-fit classifier (observed responses):
  - `safetensors.total` plus a per-dtype breakdown, e.g. `BF16,F8_E4M3` for Devstral-Small-2 and `BF16,U8` for gpt-oss MXFP4. — [Devstral](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512); [gpt-oss](https://huggingface.co/openai/gpt-oss-20b)
  - `gguf.{total, architecture, context_length, chat_template}` on GGUF repos, e.g. `unsloth/gpt-oss-20b-GGUF` → total 20,914,757,184, architecture gpt-oss, context_length 131072. — [API](https://huggingface.co/api/models/unsloth/gpt-oss-20b-GGUF?expand[]=gguf)
  - `cardData.license` / `license_name`, `gated` (False | "manual"), `pipeline_tag`, `library_name`, `tags`.
  - `config.json` via `/resolve/main/config.json` gives `max_position_embeddings` (or nested `text_config`) and `architectures` (MoE detectable from names like `Qwen3MoeForCausalLM`, `Lfm2MoeForCausalLM`).
- Pitfall: `safetensors.total` on quantized repos counts packed storage, not logical parameters. Examples: `nvidia/Qwen3.8-27B-NVFP4` reports 18.16B for a 27.78B model; `ibm-granite/granite-4.2-8b-nvfp4` reports 5.31B vs 8.79B; `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4` reports 18.24B vs 31.58B. — [nvidia listing](https://huggingface.co/api/models?author=nvidia&sort=createdAt&direction=-1&limit=30); [granite listing](https://huggingface.co/api/models?author=ibm-granite&search=granite-4&sort=createdAt&direction=-1&limit=25)
- File sizes per quantization come from `GET /api/models/{id}/tree/main?recursive=true`, which returns `path` and `size`/`lfs.size`. The OpenAPI spec documents the tree endpoint with params `expand, recursive, limit, cursor`. — [OpenAPI spec](https://huggingface.co/.well-known/openapi.json); [example](https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF/tree/main?recursive=true)
- The Hub API reference moved to an OpenAPI Playground; the spec is at `/.well-known/openapi.json` and in Markdown at `/.well-known/openapi.md`. — [HF docs: Hub API](https://huggingface.co/docs/hub/api)
- Daily papers:
  - `GET /api/daily_papers` takes query params `p, limit, date, week, month, submitter, sort` (sort enum `publishedAt`, `trending`). — [OpenAPI spec](https://huggingface.co/.well-known/openapi.json)
  - Response items (observed) have keys `paper, publishedAt, title, summary, thumbnail, numComments, submittedBy, isAuthorParticipating`. `paper` has `id, authors, publishedAt, submittedOnDailyAt, title, submittedOnDailyBy, summary, upvotes, discussionId, projectPage, githubRepo, githubRepoAddedBy`. — [API](https://huggingface.co/api/daily_papers?limit=2)
  - Related endpoints: `/api/papers` (cursor, limit), `/api/papers/search?q=&limit=`, `/api/papers/{paperId}`, `/api/papers/{paperId}/links`. — [OpenAPI spec](https://huggingface.co/.well-known/openapi.json)
- Rate limits (docs dated "September '25") over 5-minute fixed windows:

  | Plan | API | Resolvers | Pages |
  |---|---|---|---|
  | Anonymous (per IP) | 500 | 3,000 | 100 |
  | Free user | 1,000 | 5,000 | 200 |
  | PRO | 2,500 | 12,000 | 400 |
  | Team | 3,000 | 20,000 | 400 |
  | Enterprise | 6,000 | 50,000 | 600 |

  Exceeding returns 429, with IETF draft headers `RateLimit` and `RateLimit-Policy`. Advice: always pass `HF_TOKEN`, and "replace Hub API calls with Resolver calls, whenever possible". `huggingface_hub` ≥1.2.0 auto-waits on 429 using the header. — [HF docs: rate limits](https://huggingface.co/docs/hub/rate-limits)
- Observed live headers (anonymous): `RateLimit: "api";r=498;t=174` and `RateLimit-Policy: "fixed window";"api";q=500;w=300`, which matches the documented anonymous API quota. — [API](https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=30)
- Trending sorts surface many derivative "Uncensored/Heretic/abliterated" re-uploads. For example, `apps=ollama` trending was dominated by `DavidAU/…`, `HauhauCS/…`, and `orcarouter/…` repos on 2026-10-09. — [apps=ollama trending](https://huggingface.co/api/models?apps=ollama&sort=trendingScore&direction=-1&limit=15)
- Ollama library existence can be checked with `https://ollama.com/library/{name}` (200 vs 404). Checked 2026-10-09:
  - Present: qwen3-embedding, embeddinggemma, embeddinggemma-2, nomic-embed-text, nomic-embed-text-v2-moe, mxbai-embed-large, bge-m3, snowflake-arctic-embed2, granite-embedding, gpt-oss, qwen3.5, qwen3.6, qwen3.8, gemma4, qwen3-coder, qwen3-coder-next, devstral-small-2, magistral, ministral-3, deepseek-r1, phi4-reasoning, phi4-mini-reasoning, nemotron-3-nano, nemotron-3.5-lightning, granite4, granite4.2, lfm2, lfm2.5, olmo-3, glm-4.7-flash.
  - Absent: qwen3-reranker, jina-embeddings-v5, harrier, rwkv7, falcon-h1r, hrm-text, qwen-agentworld.
  — [Ollama library](https://ollama.com/library/qwen3-embedding)

### Inferences
- A VRAM-fit classifier can work in four steps:
  1. Candidate discovery via `api/models?pipeline_tag=…&num_parameters=min:0,max:40B&sort=trendingScore|createdAt&expand[]=safetensors&expand[]=config&expand[]=cardData&expand[]=baseModels&expand[]=gated`.
  2. Filtering out derivative repos with an author allowlist (official orgs plus unsloth/bartowski/ggml-org/lmstudio-community/mradermacher for GGUF), or by requiring `baseModels` to be absent or official.
  3. Finding GGUF mirrors via `filter=gguf&search={name}` and reading exact quant sizes from `/tree/main`.
  4. Computing fit = file_size + KV(ctx), with KV derived from `config.json` (num_layers, num_kv_heads, head_dim, and the share of linear-attention layers). MoE models (detected from `architectures` / `num_experts`) get a second "fits with CPU expert offload (VRAM+RAM)" class.
- Use logical parameter counts from base repos, not NVFP4/FP8 repos.
- Polling budget: with a free token (1,000 API calls / 5 min), a daily sweep of ~40 orgs plus ~200 detail calls fits easily. Detail metadata should prefer resolver calls (`config.json`, `README.md`), which have higher limits.

### Gaps
- The `/api/models` list endpoint does not appear in the OpenAPI spec paths I extracted; only per-repo sub-paths do. The `filter`, `apps`, `num_parameters`, and `library` semantics were confirmed empirically, not from the spec.
- I did not review HF Terms of Service clauses on automated scraping.
- `sort=likes` and `sort=lastModified` were not tested.
- Daily papers pagination semantics (`p`) were not tested.

---

## Q7. Known Blackwell (sm_120) / Windows compatibility issues for local inference stacks (2026)

### Takeaway
On Windows 11 with an RTX 5060 Ti:
- **Ollama and llama.cpp** are the low-friction path. Current releases are Ollama v0.40.2 (2026-10-08) and llama.cpp b11521 (2026-10-09). llama.cpp ships Windows CUDA 12.4 and CUDA 13.4 builds plus Vulkan; there is no 12.8 build.
- **vLLM** has no native Windows support and none is planned. Use WSL2 or the community `SystemPanic/vllm-windows`.
- **FlashAttention** on sm_120 needs a manual `TORCH_CUDA_ARCH_LIST=12.0` build, and FA4 sm_120 support is still a PR.
- **bitsandbytes** ships sm_120 builds for Windows.
- **NVFP4 on consumer Blackwell** is immature: vLLM falls back to Marlin, and llama.cpp declined native SM120 NVFP4 MoE kernels.
- **PyTorch 2.11 is three minor versions behind.** 2.14.x carries sm_120-specific cuDNN fixes, and 2.14.1 notes a CUDA compiler correctness bug "present since CUDA 12.8".

### Cited Findings
- Versions:
  - Ollama v0.40.2 (2026-10-08), v0.40.0 (2026-09-25). — [Ollama releases](https://github.com/ollama/ollama/releases)
  - Ollama v0.30.11 (2026-06-25) "add sm_86 architecture to cuda_v13_windows preset", so a CUDA-13 Windows runner exists. The same release fixed "inverted iGPU/dGPU Vulkan classification on Windows hybrid graphics" and switched to the host Vulkan loader on Windows. — [Ollama releases](https://github.com/ollama/ollama/releases)
  - Ollama v0.34.1 (2026-09-14): "GGUF model creation now requires using llama.cpp tooling for safetensor conversion and quantization." — [Ollama releases](https://github.com/ollama/ollama/releases)
  - Ollama v0.40.1 (2026-10-07) fixed a "clef head reads past 2GiB on windows" bug and avoids symlinks in manifests on Windows. — [Ollama releases](https://github.com/ollama/ollama/releases)
  - llama.cpp b11521 (2026-10-09) Windows assets: `llama-b11521-bin-win-cuda-12.4-x64.zip`, `…-cuda-13.4-x64.zip`, `…-vulkan-x64.zip`, `…-cpu-x64.zip` (also SYCL, ROCm 10.0, OpenVINO). — [llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases)
- PyTorch:
  - 2.14.0 (2026-09-02): "Disable cuDNN convolution engines 58 and 63 on `sm120` to prevent illegal memory accesses (#190112)" and "Update the cuDNN errata filter for `sm120`". — [PyTorch releases](https://github.com/pytorch/pytorch/releases)
  - 2.14.1 (2026-09-30) updated **Linux** CUDA 13.2 binaries to 13.2.2. That resolves a cuBLASLt NVFP4 scaling bug and a compiler bug where "failed thread reconvergence could leave stale or corrupted register values… (present since CUDA 12.8)". — [PyTorch releases](https://github.com/pytorch/pytorch/releases)
  - A 50-series "no kernel image is available" error comes from builds without sm_120. "50XX support started with CUDA 12.8." — [NVIDIA forum](https://forums.developer.nvidia.com/t/rtx-5090-not-working-with-pytorch-and-stable-diffusion-sm-120-unsupported/338015)
- vLLM:
  - Maintainer (2026-06-30): "We do not plan to support Windows natively in tree. You can either use WSL or this community plugin https://github.com/SystemPanic/vllm-windows". — [vLLM #47119](https://github.com/vllm-project/vllm/issues/47119)
  - `SystemPanic/vllm-windows`: 658 stars, Apache-2.0, last push 2026-09-18. — [GitHub](https://github.com/SystemPanic/vllm-windows)
  - sm_120 is in vLLM's supported CMake arch list (maintainer, 2026-05-04). Windows users still report needing `TORCH_CUDA_ARCH_LIST=12.0`, a GPU-preference registry fix on hybrid-graphics laptops, and CUDA DLL PATH ordering fixes. A Linux user listed further issues: torch-nightly downgrade via pin, gcc-14 for CUDA 13, a FlashInfer cu128 wheel problem, and a V1 fork deadlock. — [vLLM #41614](https://github.com/vllm-project/vllm/issues/41614)
  - Open bug (2026-07-06): on RTX 5090 / SM120, a ModelOpt mixed NVFP4 checkpoint "falls back to Marlin W4A16 path and warns no native FP4 support". — [vLLM #47749](https://github.com/vllm-project/vllm/issues/47749)
- CUTLASS: an SM120 NVFP4 MoE grouped GEMM produced garbage output. It was fixed via FlashInfer SM120 patches plus `compute_120f` (CUDA 13.0) and closed as completed 2026-04-14. — [CUTLASS #3096](https://github.com/NVIDIA/cutlass/issues/3096)
- llama.cpp: the feature request for native SM120 NVFP4 MoE kernels was closed **not planned** on 2026-02-06. — [llama.cpp #18250](https://github.com/ggml-org/llama.cpp/issues/18250)
- llama-cpp-python: an issue about building from source for RTX 50 Blackwell has been open since 2025-06-13. Search summaries report an "Unsupported gpu architecture 'compute_120'" error fixed by manual CMake flags. — [llama-cpp-python #2028](https://github.com/abetlen/llama-cpp-python/issues/2028)
- FlashAttention:
  - "FA4 consumer Blackwell (sm_120) integration" PR is open (2026-06-08). — [FA PR #2634](https://github.com/Dao-AILab/flash-attention/pull/2634)
  - "FA4 is consistently slower than FA2 on a 5090" (open, 2026-04-06). — [FA #2440](https://github.com/Dao-AILab/flash-attention/issues/2440)
  - Build failure with CUDA 13.2 + MSVC 2026 + RTX 5090 (2026-03-26). — [FA #2395](https://github.com/Dao-AILab/flash-attention/issues/2395)
  - Windows RTX 5070 Ti notes: set `TORCH_CUDA_ARCH_LIST=12.0` and fix DLL PATH priority. — [FA #2535](https://github.com/Dao-AILab/flash-attention/issues/2535)
  - CuTe on sm_120 bugs (TMA epilogue mis-gating, etc.). — [FA #2386](https://github.com/Dao-AILab/flash-attention/issues/2386)
- bitsandbytes:
  - Maintainer (2026-05-05): "We do compile for sm_120 on both Windows and Linux, and have been since around v0.45.3… These builds should work fine when using a PyTorch build with CUDA 12.8+. We currently do ship CUDA 13.0 binaries". — [bnb #1937](https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1937)
  - Open: NF4 energy-efficiency penalty on Blackwell for small models. — [bnb #1851](https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1851)
- TensorRT-LLM: a report from 4× RTX 5060 Ti was first described in search results as "~6 s fixed per-request latency on sm120… NVFP4 27B". The issue is now titled as a `/metrics` route blocking the serve event loop. So the root cause was a metrics-scrape instrument effect, not sm_120 itself. — [TRT-LLM #19623](https://github.com/NVIDIA/TensorRT-LLM/issues/19623)

### Inferences
- Recommended Windows stack for this machine:
  - Ollama (upgrade from 0.3x to 0.40.x) or llama.cpp's **CUDA 13.4** Windows build for GGUF inference. The 12.4 build predates sm_120 support in CUDA (12.8+). Whether it works via PTX JIT is unverified, and Vulkan is the fallback.
  - PyTorch upgraded to ≥2.14 (cu128 or cu13x wheel) for transformers-based models (embedders, rerankers, HRM/TRM).
  - vLLM only inside WSL2, if batch serving is needed.
- Prefer GGUF K/IQ quants or MXFP4 (gpt-oss) over NVFP4 checkpoints on this card for now. NVFP4 paths on SM120 are partly fallback or buggy in vLLM and absent in llama.cpp.
- The PyTorch 2.14.1 note means CUDA 12.8 toolchains can carry a silent-wrong-result compiler bug. For falsification-grade experiments, pin and record the CUDA runtime and driver alongside model hashes.

### Gaps
- I found no first-hand 2026 report specifically for the RTX 5060 Ti on Windows with Ollama or llama.cpp.
- I did not verify whether llama.cpp's CUDA 12.4 Windows build runs on sm_120.
- The exact Ollama 0.3x versions that first bundled a CUDA-13/sm_120 runner on Windows were not pinned down.
- I did not check whether PyTorch 2.14.1's CUDA 13.2.2 fix applies to Windows wheels; the note says Linux.
