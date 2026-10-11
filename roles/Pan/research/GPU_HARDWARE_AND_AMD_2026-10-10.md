# GPU hardware for local models, AMD AI Workbench, and why NVIDIA leads

Filed by Pan on 2026-10-10 at the operator's request ("capture it and file it
away"). Prices are US street prices for NEW cards as seen in early October 2026;
they move week to week -- re-check before any purchase. Searchable with
`python -m pan search "GPU price"` after the next refresh.

## 1. AMD AI Workbench -- verdict: no adoption value for Prometheus today

What it is: the UI layer of AMD's enterprise AI reference stack (v2.2): a
catalog of AMD Inference Microservices (AIMs, OpenAI-compatible inference
containers), GPU workspaces (Jupyter, VS Code), fine-tuning of certified base
models, chat/compare, MLflow, API keys, secrets; standalone or with AMD
Resource Manager (quotas, org hierarchy).

Why it does not fit:
- AMD-only hardware: AIMs run on Instinct MI300X/MI325X/MI350X/MI355X, Radeon
  Pro W7900/R9700 and EPYC 9965 CPUs; NVIDIA is not mentioned. Both program
  GPUs are NVIDIA RTX 5060 Ti 16 GB (M1 Skullport, M2 SPECTREX5; confirmed in
  aporia/docs/germline_infrastructure_2026-08-17.md). Even on the R9700 the
  catalog lists 4 models (3 in preview); the large models are Instinct-only.
- Platform: Kubernetes + Helm (charts as OCI artifacts on Docker Hub), Keycloak
  SSO; the open repo's stack adds Postgres, MinIO, RabbitMQ, Vault; Windows only
  via WSL. Program hosts are Windows; shared Postgres lives on M1 by ruling;
  M2's D: is an SMR disk (no database-style write loads).
- Every feature already exists in the program: Ollama + prometheus_llm
  (OpenAI-compatible) for serving; Fabric leases + MWO-0004 for GPU quotas;
  Pan's executed-test benchmarks (HumanEval+, PAN-34 in-house) instead of
  chat/compare; preregs + git + pan.run/code_bench + Iceberg instead of MLflow;
  seat worktrees instead of workspaces.
- Young: github.com/amd-enterprise-ai/amd-eai-suite had 14 stars and 13 commits
  when read; licence file LICENSE.TXT, name not confirmed.
- Revisit only if the program buys AMD hardware.

## 2. Entry-level cards that run local models (US, early October 2026)

    VRAM   card                            list     street now          notes
    16 GB  AMD RX 9060 XT 16GB             $349     ~$470-550 new       cheapest new 16 GB; ROCm, not CUDA
                                                    ~$450-500 used
    16 GB  NVIDIA RTX 5060 Ti 16GB         $429     ~$790-820 new       the card in M1 and M2; drop-in
    24 GB  Intel Arc Pro B60               --       ~$650               middle step
    32 GB  AMD Radeon AI PRO R9700         $1,299   ~$1,400-1,900       entry 32 GB, ~$42 per GB
    32 GB  NVIDIA RTX 5090                 $1,999   ~$4,800-5,200       faster, CUDA; ~3.5x the R9700
    32 GB  NVIDIA RTX PRO 4500 Blackwell   --       ~$4,200-5,300       workstation card
    32 GB  Intel Arc Pro B70               --       unclear             reports from $949 to $4,999

All 2026 prices sit far above list; trackers attribute it to GDDR memory
shortages and AI demand.

What each size buys the program (Pan's measurements on the 16 GB card):
- 16 GB runs everything Pan has tested: gpt-oss:20b (~13 GB), qwen2.5-coder:14b,
  gemma3:12b, qwen3:8b. A second 16 GB NVIDIA card (~$800) = two model jobs in
  parallel with zero software change.
- 32 GB adds ~27-32B models at 4-bit (Qwen3-32B, Gemma-3-27B) and longer
  context. Whether bigger models help the program is UNMEASURED: on the
  program's own code (PAN-34) the best 14B passes 0.415. Running PAN-34 on a
  32B model (CPU offload or rented GPU) is the test to run before buying.
- AMD catch: Ollama/llama.cpp run on the R9700 via ROCm, and AMD's Windows
  PyTorch (ROCm 7.2, 2026-01-21) lists RX 9070/9070 XT, AI PRO R9700, RX 9060 XT,
  RX 7900 XTX -- but Pan's tooling (PyTorch embeddings, Ollama) is tested only
  on NVIDIA. Staying NVIDIA at 32 GB costs ~$4,800+ today.

## 3. Why NVIDIA leads, and where AMD can play

Share (third-party estimates, 2026; methods differ): NVIDIA ~75-86 percent of
AI data-center accelerator revenue, AMD ~5-10 percent; discrete GPUs overall
NVIDIA 90 / AMD 8 percent in Q2 2026 (Jon Peddie Research via Motley Fool).

Why the lead is so large (general knowledge unless a source is given):
1. Software head start. CUDA shipped in 2007; deep learning was born on it
   (AlexNet, 2012, two GeForce GTX 580s). Fifteen-plus years of libraries
   (cuBLAS, cuDNN, NCCL, TensorRT, CUTLASS) and of tuned kernels sit on top.
2. Frameworks and the long tail. PyTorch, JAX and almost every new technique
   (FlashAttention, quantization kernels, new attention variants) land on CUDA
   first; other vendors port later. Each port lags, so the newest work runs
   best on NVIDIA -- which keeps researchers on NVIDIA.
3. One platform from laptop to data center. The same CUDA code runs on a
   gaming card and on an H100, so students and hobbyists learn on hardware
   they own. AMD split consumer (RDNA) and data-center (CDNA) architectures,
   and for years ROCm supported few consumer cards and no Windows; ROCm on
   Windows for Radeon only arrived with 7.2 at CES 2026.
4. Systems, not chips. NVLink/NVSwitch and the Mellanox networking business
   (InfiniBand, acquired 2020) let NVIDIA sell whole racks (e.g. NVL72) that
   train as one machine; training at scale is a networking problem as much
   as a chip problem.
5. Supply and scale. Early, large commitments for TSMC advanced packaging and
   HBM, plus annual product cadence, compound the lead; profits fund the
   largest GPU software organization in the industry.
6. Switching costs. Teams have years of CUDA code, tooling, profilers and
   operational know-how; "works out of the box" beats a cheaper card that
   needs porting and debugging.

Where AMD can and does play:
- Memory per dollar, which is what inference needs: the R9700 gives 32 GB at
  ~$42 per GB vs ~$150 per GB for an RTX 5090; Instinct parts carry very large
  HBM (MI450: 432 GB HBM4, unveiled at Advancing AI 2026).
- Big buyers who want a second source: OpenAI's 6 GW agreement (October 2025,
  first 1 GW of MI450 slated for 2H 2026, warrants for up to 160 M AMD shares)
  and a reported matching 6 GW Meta deal (February 2026). These customers can
  afford to port their own software.
- Narrowing software gap: ROCm 7.x on Linux and now Windows; PyTorch, vLLM,
  SGLang and llama.cpp run on AMD; compilers such as Triton reduce hand-written
  CUDA dependence.
- Still behind on: breadth of consumer-card support, out-of-the-box
  reliability, the long tail of new kernels, and rack-scale networking
  (Helios is AMD's answer, 2026).

For a small lab like this one: AMD makes sense when the job is "serve
open-weight models with as much VRAM per dollar as possible" with
Ollama/llama.cpp; NVIDIA makes sense when the job uses the long tail
(PyTorch training, embedding stacks, new research code) and when nobody has
time to debug drivers.

## 4. What would decide a purchase (measurements, not opinions)

- Does a ~32B model beat the 14B on the program's own code? Run PAN-34 on it.
- Does Pan's stack (Ollama, PyTorch embeddings) run unchanged on ROCm? A one-
  day test on a borrowed or rented AMD card answers it.

## Sources

Workbench / AIMs:
- https://enterprise-ai.docs.amd.com/en/v2.2/workbench/overview.html
- https://enterprise-ai.docs.amd.com/en/v2.2/workbench/getting-started/installation.html
- https://enterprise-ai.docs.amd.com/en/v2.2/aims/overview.html
- https://enterprise-ai.docs.amd.com/en/latest/aims/catalog/models.html
- https://rocm.blogs.amd.com/software-tools-optimization/eai-hw-support/README.html (2026-07-16)
- https://rocm.blogs.amd.com/artificial-intelligence/enterprise-ai-suite/README.html
- https://github.com/amd-enterprise-ai/amd-eai-suite
Prices:
- https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060+Ti+16GB&id=6160
- https://gpuprix.com/us/gpus/geforce-rtx-5060-ti-16gb
- https://gpuprix.com/us/gpus/radeon-rx-9060-xt-16gb
- https://bottleneckpc.com/gpu/rx-9060xt
- https://runaihome.com/blog/amd-radeon-ai-pro-r9700-local-ai-hardware-guide-2026/
- https://pricehistory.app/p/powercolor-amd-radeon-ai-pro-r9700-32gb-BFcRhGIm
- https://localaimaster.com/blog/gpu-price-per-gb-vram
- https://www.compute-market.com/blog/cheapest-32gb-gpu-local-llm-2026
- https://bestvaluegpu.com/history/new-and-used-rtx-5090-price-history-and-specs/
- https://pangoly.com/en/price-trends/vga/rtx-5090
- https://gpuprix.com/us/gpus/rtx-pro-4500-blackwell
Market and AMD position:
- https://commandlinux.com/statistics/ai-gpu-market-share-nvidia-vs-amd-vs-intel/
- https://siliconanalysts.com/ai-accelerator-revenue-forecast/
- https://fool.com/investing/2026/09/15/nvidia-will-still-beat-amd-through-2028-heres-the
- https://insidehpc.com/2025/10/what-the-openai-deal-means-for-amd-in-ai-compute/
- https://www.servethehome.com/?p=90877
- https://www.amd.com/en/resources/support-articles/release-notes/RN-AMDGPU-WINDOWS-PYTORCH-7-2.html
- https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest
