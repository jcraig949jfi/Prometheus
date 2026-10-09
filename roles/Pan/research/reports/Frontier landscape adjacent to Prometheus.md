# Refinement loops, not architectures, now drive the frontier

Every field next to Prometheus settled on the same motif in 2025–2026. A proposer emits candidates, a machine-checkable evaluator scores them, and an archive decides what survives. The proposer is usually an LLM, though sometimes it is a 7M-parameter recursive network. **AlphaEvolve** (arXiv 2506.13131, 2025-06-16; generally available on Google Cloud 2026-07-09) set the template. Apache-2.0 clones (OpenEvolve, ShinkaEvolve) now reproduce its headline results on a workstation. The ARC Prize 2025 technical report (2601.10904, 2026-01-15) calls the **"refinement loop"** the defining theme of the year, and self-modifying agent archives (Darwin Gödel Machine, Huxley-Gödel Machine, Hyperagents) run the same loop on an agent's own code. The more consequential finding for Prometheus is that the field's own 2026 audits keep deflating the advertised mechanisms. Simple baselines match code-evolution pipelines (2602.16805). HRM's hierarchy matters less than its outer loop. Pairwise interaction is not what makes self-replicators emerge (2607.01483). AI-scientist agents revise after refutation in only 26% of traces (2604.18805). Nearly everything worth absorbing is open and fits on one 16 GB GPU: 4–9B code models as mutation operators, ≤8B Lean provers at 2.7–5 GB, and 0.6–8B embedders. The polling spine has to be arXiv (1 request per 3 s), Hugging Face (500 calls per 5 min anonymous), GitHub (5,000 per hour with a token), Crossref and OpenAlex. As of 2026-10-09, OpenReview, DBLP, the ACM Digital Library and MIT Press Direct all block scripted clients.

## Seven lineages now run one propose–evaluate–archive loop

### LLM-guided program evolution became an open commodity within a year

AlphaEvolve has an LLM propose direct code edits, scores them with automated evaluators inside an evolutionary database, and evolves whole files. Its predecessor FunSearch evolved single Python functions. Its best-known result is a 4x4 complex matrix multiplication with **48 scalar multiplications**, against Strassen's 49 ([arXiv](https://arxiv.org/abs/2506.13131.pdf)). Google opened enterprise preview on 2025-12-09 and made it **generally available on 2026-07-09**. The deployment results Google reports, such as -20% Spanner write amplification and quantum circuits with 10x lower error, are vendor figures with no independent replication ([Google blog](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/); [Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone)). The most useful public stress test is **Georgiev, Gómez-Serrano, Tao and Wagner** (2511.02864, v1 2025-11-03), who ran AlphaEvolve on **67 problems**. It rediscovered most best-known constructions and improved several. The authors concede some gains "could likely also have been matched by more traditional" methods ([arXiv](https://arxiv.org/abs/2511.02864)).

The open ecosystem caught up fast:

- **OpenEvolve** (Apache-2.0, ~7.5k stars) has a MAP-Elites grid, island migration, cascade evaluation and seeded reproducibility ([GitHub](https://github.com/algorithmicsuperintelligence/openevolve)).
- **ShinkaEvolve** (2509.19349; ICLR 2026; Apache-2.0; PyPI `shinka-evolve` since March 2026) uses novelty rejection sampling and a UCB bandit over an LLM ensemble. It matched a 26-circle packing result with about **150 samples** ([GitHub](https://github.com/SakanaAI/ShinkaEvolve); [arXiv](https://arxiv.org/pdf/2509.19349)).
- **CodeEvolve** (2510.14150) claims open-weight models match closed baselines ([arXiv](https://arxiv.org/pdf/2510.14150)).
- **GigaEvo** (2511.17592, 2025-11-17) adds DAG evaluation pipelines and lineage tracking ([arXiv](https://arxiv.org/abs/2511.17592v1)).
- **DeepEvolve** (2510.06056) adds retrieval because pure evolution "quickly plateaus" ([arXiv](https://arxiv.org/html/2510.06056v1)).
- **LEVI** (2605.09764, 2026-05-10) argues that a stronger search architecture can substitute for a larger LLM ([arXiv](https://arxiv.org/abs/2605.09764)).

These systems differ mainly in parent selection, the diversity archive, novelty filtering, model routing and the evaluator cascade. That makes them ready-made **reference arms** rather than competitors.

The substantive 2025–2026 shift is from a frozen mutation operator to one that **learns during the run**:

- **ThetaEvolve** (2511.23473, 2025-11-28; ICML 2026) adds test-time RL. It is the first small open model (DeepSeek-R1-0528-Qwen3-8B) to set new best-known bounds on circle packing and an autocorrelation inequality ([arXiv](https://arxiv.org/abs/2511.23473v1)).
- **TTT-Discover** (2601.16175, January 2026; ICML 2026 spotlight) runs RL on the single test problem with gpt-oss-120b through the Tinker API at "a few hundred dollars per problem" ([arXiv](https://arxiv.org/abs/2601.16175v1)).
- **SOAR** (2507.14172; ICML 2025) fine-tunes its own LLM on hindsight-relabelled search traces and solves **52% of ARC-AGI-1 public test** ([arXiv](https://arxiv.org/abs/2507.14172v1)).
- **GEPA** (2507.19457; ICLR 2026 Oral) evolves prompts over a per-instance Pareto front. Its v2 reports +6% over GRPO, down from +10% in v1 ([arXiv](https://arxiv.org/abs/2507.19457)).

Meta's **AIRA-dojo** (2507.02554) found that **operator quality is the primary bottleneck** in MLE-bench agents ([arXiv](https://arxiv.org/html/2507.02554v2)). LEVI claims the opposite: archive structure can substitute for operator strength. That disagreement is an open, testable question.

The pre-2025 lineage is still worth indexing but not adopting. It includes FunSearch (Apache-2.0, unmaintained) ([Wikipedia](https://en.wikipedia.org/wiki/FunSearch)), OpenELM (MIT, last release 2023-03-08) ([GitHub](https://github.com/CarperAI/OpenELM)), and EoH, ReEvo and LLaMEA, which LLM4AD bundles ([arXiv](https://arxiv.org/abs/2412.17287)).

### Program induction moved from static grids to interactive skill acquisition

ARC Prize 2025 ran from 2025-03-26 to 2025-11-03 and drew **1,455 teams and 15,154 entries**:

- **Kaggle winner:** NVARC scored **24.03%** on private ARC-AGI-2 at $0.20 per task. The 85% grand prize went unclaimed ([arXiv](https://arxiv.org/html/2601.10904)).
- **Paper awards:** **TRM** (2510.04871, a ~7M-parameter recursive net), **SOAR**, and **CompressARC** (2512.06104, ~76K parameters, minimizing description length on each puzzle with no pretraining) ([arXiv](https://arxiv.org/html/2512.06104v1)).
- **Commercial harness:** Poetiq's generate–critique–refine–verify harness on Gemini 3 Pro reached **54% on semi-private ARC-AGI-2 at ~$30 per task** ([bdtechtalks](https://bdtechtalks.com/2025/12/09/poetiq-arc-agi-2-solution/)).

The live frontier is now **ARC-AGI-3** (2603.24621), launched **2026-03-25**:

- **Format:** hundreds of handcrafted, instruction-free, turn-based environments, scored on action efficiency against human baselines.
- **Baseline scores:** humans score 100%. Frontier AI scored under 1% at launch; sources give 0.26% to 0.51% ([ARC Prize](https://arcprize.org/blog/arc-agi-3-launch); [arXiv](https://arxiv.org/abs/2603.24621)).
- **Prize:** the ARC-AGI-3 track carries **$850K**. Final deadline is **2026-11-02**, and open-sourcing is required ([ARC Prize](https://arcprize.org/competitions/2026/arc-agi-3)).
- **Milestone #1 (winners posted 2026-07-06):** all winners used **local open models inside Kaggle**. Tufa Labs ran Qwen 3.6 27B FP8 writing Python in a REPL; others used Gemma-4-31B ([ARC Prize](https://arcprize.org/blog/arc-prize-2026-milestone-1)).

Library learning had a quieter 2025–26. The LEGO-Prover case study (2504.03048) reports that LLM library learning fails ([arXiv](https://arxiv.org/pdf/2504.03048)). RLAD (2510.02263) trains an abstraction generator against a solver ([arXiv](https://arxiv.org/html/2510.02263v1)). EvoLib (2605.14477, May 2026) evolves a test-time abstraction library for black-box LLMs ([arXiv](https://arxiv.org/html/2605.14477v1)). DreamCoder, Stitch (2211.16605) and LILO (2310.19791) remain the reference designs. The notes confirmed no new 2025–26 arXiv IDs from the Ellis or Tenenbaum/Andreas groups.

### Small open Lean provers now beat last year's 671B model

**DeepSeek-Prover-V2** (2504.21801, 2025-04-30) reached **88.9% on miniF2F-test and 49/658 PutnamBench** with a 671B model ([arXiv](https://arxiv.org/abs/2504.21801v1)). Within three months, **Goedel-Prover-V2** (2508.03613; ICLR 2026) showed an **8B model at 84.6% pass@32 beating the 671B**, using Lean-compiler-guided self-correction ([arXiv](https://arxiv.org/pdf/2508.03613)). By June 2026 the model cards claim more: **Pythagoras-Prover-4B** (HF 2026-06-07) reports 86.07% pass@32, and its 32B sibling reports 93.03% and 93/672 PutnamBench ([HF](https://huggingface.co/Pythagoras-LM/Pythagoras-Prover-4B); [HF](https://huggingface.co/Pythagoras-LM/Pythagoras-Prover-32B)).

The closed frontier sits a level higher:

- **AlphaGeometry2** (2502.03544) solves 84% of IMO geometry problems ([arXiv](https://arxiv.org/abs/2502.03544)).
- **AlphaProof** appeared in *Nature* in November 2025 ([Nature Asia](https://www.natureasia.com/en/info/press-releases/detail/9147)).
- **Seed Prover 1.5** (2512.17260) produced Lean proofs for IMO 2025 P1–P5 in 16.5 h ([ByteDance Seed](https://seed.bytedance.com/en/blog/seed-prover-1-5-advanced-mathematical-reasoning-through-a-novel-agentic-architecture)).
- **Aristotle** (2510.01346) formally verified 5/6 IMO 2025 problems ([alphaXiv](https://alphaxiv.org/abs/2510.01346v1)).

miniF2F is saturated, and the frontier has moved to PutnamBench and open problems. **Erdős #728** was resolved on 2026-01-04/06 by a GPT-5.2 Pro argument that Aristotle formalized in Lean (2601.07421) ([arXiv](https://arxiv.org/pdf/2601.07421)). Epoch AI's **FrontierMath: Erdős** (August 2026) formalizes **68 open problems** in Lean ([Epoch](https://epoch.ai/latest/announcing-frontiermath-erdos)).

### Automated-science agents multiplied faster than their capacity to refute

The 2025 science-agent wave includes:

- **Google's co-scientist** (2502.18864, February 2025) runs a generate–debate–evolve loop with an Elo tournament; access is limited ([arXiv](https://export.arxiv.org/pdf/2502.18864)).
- **The AI Scientist-v2** (2504.08066, 2025-04-10) uses agentic tree search, and the *Nature* paper on The AI Scientist appeared on 2026-03-26 ([arXiv](https://arxiv.org/abs/2504.08066v1); [coverage](https://noqta.tn/en/news/sakana-ai-scientist-nature-automated-research-2026)).
- **Agent Laboratory** (2501.04227, MIT license) ([GitHub](https://github.com/SamuelSchmidgall/AgentLaboratory)).
- **Robin** (2505.13400) proposed ripasudil for dry AMD ([arXiv](https://arxiv.org/pdf/2505.13400)).
- **Kosmos** (2511.02824, launched 2025-11-05) is a commercial platform ([Edison](https://edisonscientific.com/articles/announcing-kosmos)).
- **Ai2's AutoDiscovery** (NeurIPS 2025) rewards Bayesian surprise and shipped in AstaLabs on 2026-02-12 ([Ai2](https://allenai.org/blog/autodiscovery)).

The one design built for refutation is **POPPER** (2502.09858; ICML 2025, Stanford SNAP with Candès and Leskovec). LLM agents design falsification experiments on a hypothesis's measurable implications inside a **sequential test with strict Type-I error control** ([arXiv](https://arxiv.org/abs/2502.09858)). **Fisher-R1** (2608.07437, August 2026) follows that direction by training agents with RL on a verified statistical reward ([arXiv](https://arxiv.org/abs/2608.07437)).

### Open-endedness made foundation models its novelty oracle and agents its substrate

Self-modification is the fastest-moving cluster:

- **Darwin Gödel Machine** (2505.22954, v1 2025-05-29; ICLR 2026) edits its own repository and keeps an archive of agents. It raised SWE-bench from **20.0% to 50.0%** ([arXiv](https://arxiv.org/abs/2505.22954)).
- **Huxley-Gödel Machine** (2510.21614, 2025-10-24; ICLR 2026 oral) names the **"Metaproductivity–Performance Mismatch"**: an agent's own score poorly predicts its descendants' value. It selects on **Clade-Metaproductivity** instead ([arXiv](https://arxiv.org/abs/2510.21614); [ICLR](https://www.iclr.cc/virtual/2026/oral/10009360)).
- **Hyperagents** (2603.19461, 2026-03-19; UBC, Vector and Meta) makes the meta-agent itself editable. It reports meta-level improvements that transfer across domains. It is a single-lab preprint, and a third-party page lists its code license as CC BY-NC-SA 4.0 ([arXiv](https://arxiv.org/abs/2603.19461); [docs](https://www.mintlify.com/facebookresearch/HyperAgents/introduction)).
- **Autopoiesis** work is formal and early. "The Minary Primitive" (2601.04501) proposes a provable self-maintenance primitive and leaves self-replication open ([arXiv](https://arxiv.org/abs/2601.04501)).

ALife search now treats a vision-language model as its interestingness oracle:

- **ASAL** (2412.17799, v2 2025-05-16) ([arXiv](https://arxiv.org/abs/2412.17799)) and its VLM-guided descendant (2509.22447, ALIFE 2025) ([arXiv](https://arxiv.org/abs/2509.22447)).
- A **Picbreeder replication with VLMs** (2605.23908), the only best-paper nominee in GECCO 2026's Complex Systems track ([arXiv](https://arxiv.org/abs/2605.23908); [GECCO](https://gecco-2026.sigevo.org/Best-Paper-Nominations)).
- The **Fractured Entangled Representation hypothesis** (2505.11581) argues that open-ended search yields factored representations where SGD yields fractured ones ([arXiv](https://arxiv.org/abs/2505.11581)).

Substrates are becoming ecologies:

- Sakana's **Petri Dish NCA** ([Sakana](https://sakana.ai/pd-nca/)).
- **PBT-NCA** (2604.11248), which fixes PD-NCA's collapse to frozen or monoculture states ([arXiv](https://arxiv.org/abs/2604.11248)).
- **Universal NCA** (2505.13058) ([arXiv](https://arxiv.org/abs/2505.13058)).
- **Reasoning with NCA** (2609.36126, 2026-09-28) ([arXiv](https://arxiv.org/abs/2609.36126)).
- A **Z80 primordial soup** in which self-replication and polynomial evaluation co-evolve from random 32-byte programs (2607.09211, 2026-07-10) ([arXiv](https://arxiv.org/abs/2607.09211)).

Quality-diversity work is incremental but useful:

- **Dominated Novelty Search** (2502.00593, GECCO 2025) replaces the MAP-Elites grid with a fitness transformation and supports unbounded, variable-dimensional descriptors ([arXiv](https://arxiv.org/abs/2502.00593)).
- Sakana's **Task-Capability Coevolution** (2604.14969; ICLR 2026) adopts it for exactly that reason ([arXiv](https://arxiv.org/abs/2604.14969)).
- QD has been recast as multi-objective optimization (2602.00478) ([arXiv](https://arxiv.org/abs/2602.00478)).

POET-style environment generation has moved into two places: unsupervised environment design (UED), and LLM-written environments:

- **UED:** TRACED (2506.19997; ICLR 2026) ([arXiv](https://arxiv.org/abs/2506.19997)), the NCC optimization framework (2505.20659; RLC 2025) ([arXiv](https://arxiv.org/abs/2505.20659)) and PACE (2605.01358) ([arXiv](https://arxiv.org/abs/2605.01358)).
- **LLM-written environments:** OMNI-EPIC (2405.15568; ICLR 2025) ([arXiv](https://arxiv.org/abs/2405.15568)), GenEnv (2512.19682) ([arXiv](https://arxiv.org/abs/2512.19682)) and Environment Evolution for Terminal Agents (2609.04128, 2026-09-03) ([arXiv](https://arxiv.org/abs/2609.04128)).
- Uber's original POET repo has been dormant since 2022-03-23 ([GitHub](https://github.com/uber-research/poet)).

Two areas stayed thin: genuine **major-transitions models** and a **standardized open-endedness benchmark**.

### World models and non-LLM architectures iterate in latent space

The JEPA line is the most Prometheus-shaped substrate:

- **V-JEPA 2** (2506.09985, 2025-06-11). Its action-conditioned variant, post-trained on under 62 h of robot video, drove Franka arms zero-shot ([HF Papers](https://huggingface.co/papers/2506.09985)).
- **LeJEPA** (2511.08544, 2025-11-11) replaces heuristics with a single regularizer (SIGReg) ([arXiv](https://arxiv.org/abs/2511.08544)).
- **LeWorldModel** (2603.19312, 2026-03-24) is a **~15M-parameter** end-to-end JEPA that trains "on a single GPU in a few hours" and plans up to 48x faster than foundation-model world models. Its code is MIT ([arXiv](https://arxiv.org/html/2603.19312)).
- **2605.26379** (2026-05-25) proves when LeJEPA latents are linearly identifiable ([Emergent Mind](https://www.emergentmind.com/papers/2605.26379)).
- LeCun's **AMI Labs** raised **$1.03B**, announced 2026-03-09 ([TechCrunch](https://techcrunch.com/2026/03/09/yann-lecuns-ami-labs-raises-1-03-billion-to-build-world-models/)). Its own code-release policy is unverified.

Generative world models split between closed and large:

- **Genie 3** (2025-08-05) is a closed preview with no paper ([TechCrunch](https://techcrunch.com/2025/08/05/deepmind-reveals-genie-3-a-world-model-that-could-be-the-key-to-reaching-agi)).
- **Cosmos-Predict2.5** (2511.00062) comes in 2B and 14B under the NVIDIA Open Model License ([NVIDIA](https://research.nvidia.com/labs/cosmos-lab/cosmos-predict2.5)).
- **Matrix-Game 3.0** (2604.08995) is a 5B model ([arXiv](https://arxiv.org/pdf/2604.08995)).
- **Dreamer 4** (2509.24527, 2025-09-29) collected Minecraft diamonds from offline data alone. It has no official code ([arXiv](https://arxiv.org/pdf/2509.24527)).

Latent-iteration reasoners include:

- **HRM** (2506.21734; 27M parameters) ([README](https://cdn.jsdelivr.net/gh/sapientinc/HRM@main/README.md)).
- **TRM** (7M parameters; 44.6% ARC-AGI-1). Its repo is now **archived** ([README](https://cdn.jsdelivr.net/gh/samsungsailmontreal/tinyrecursivemodels@main/README.md)).
- **Continuous Thought Machines** (2505.05522) ([HF](https://huggingface.co/SakanaAI/ctm-imagenet)).
- The looped LMs **Huginn** (2502.05171) and **Ouro** (2510.25741) ([HF](https://huggingface.co/ByteDance/Ouro-1.4B)).
- **Energy-Based Transformers** (2507.02092; ICLR 2026 oral), where the energy acts as a built-in verifier ([ICLR](https://iclr.cc/virtual/2026/oral/10008833)).

The non-LLM cognitive architectures keep shipping code without competitive shared-benchmark results:

- **Active inference:** VERSES' **AXIOM** (2505.24784). Its repo has been frozen since 2025-06-02, and its DreamerV3 comparison is company-run ([arXiv](https://arxiv.org/html/2505.24784v1)). A verified open **renormalising generative model** implementation followed (2608.09512, August 2026) ([arXiv](https://arxiv.org/pdf/2608.09512)). **pymdp 1.0** now runs on JAX ([announcement](https://lists.cnsorg.org/hyperkitty/list/comp-neuro@lists.cnsorg.org/thread/RAHKDE4SCCA4FSFCN44MYOEJKUBREAMI/)).
- **Thousand Brains:** **Monty** merged 197 PRs in Q1 2026 ([TBP](https://thousandbrains.discourse.group/t/2026-04-q2-roadmap-and-q1-review/1066)).
- **OpenCog Hyperon** is "active pre-alpha" (PyPI 0.2.10, 2026-02-11) ([PyPI](https://pypi.org/project/hyperon/)).

Several "beyond-LLM" entries are LLM-shaped underneath, including LFM2.5, Ouro, Huginn and SpikingBrain. Watch-lists should tag *architecturally novel* separately from *efficiency-novel*.

The following table tiers the open code by how easily Prometheus can absorb it on its own hardware.

| Tier | Systems | Why |
|---|---|---|
| Absorbable local infrastructure | OpenEvolve, ShinkaEvolve, LLM4AD, pyribs, evosax/EvoX, CAX, Kinetix, Craftax, ARC-AGI-3 toolkit, Lean REPL plus ≤8B provers, LeWorldModel, HRM/TRM, pymdp | Pure Python/JAX, permissive licenses, run against local OpenAI-compatible servers |
| Local harness plus API reference arm | DGM, HGM, AI Scientist-v2, Agent Laboratory, POPPER, Poetiq | DGM/HGM need Docker and SWE-bench (x86_64, ≥120 GB disk) ([PyPI](https://pypi.org/project/swebench)); others call metered APIs |
| Cloud-only reference points | AlphaEvolve, Kosmos, co-scientist, TTT-Discover RL, AlphaProof, Seed-Prover, Aristotle, Genie 3 | Managed services or closed weights |

## The field's 2026 audits deflate most mechanism claims

The most valuable thing Prometheus can take from the frontier is a set of **discriminating controls**, which the field built against its own results, rather than any single new system. The same pattern recurs in every sub-area. The sophisticated mechanism in a paper's title is not what moved the number. A simpler outer loop, a tuned baseline, the harness, or the base model did. Each of the audits below doubles as a ready-made control for Prometheus's falsification-first instruments.

| Audit (date) | Finding | Control Prometheus can copy |
|---|---|---|
| Gideoni, Risi, Gal, 2602.16805 (2026-02-18; ICLR 2026) | Simple baselines **match or exceed** code-evolution pipelines on math bounds, scaffold design and ML competitions; search space and prompt knowledge set the ceiling ([arXiv](https://www.arxiv.org/abs/2602.16805)) | Simple-baseline arm on every evolutionary claim |
| Pelleriti et al., EvoTrace, 2605.20086 (2026-05-19) | One best score conflates new structure, re-tuning, recombination and evaluator overfitting; dataset spans 4 frameworks x 16 tasks with replay environments ([arXiv](https://arxiv.org/html/2605.20086v1)) | Lineage, diff and replay logging; re-tune-only ablation |
| ARC Prize HRM analysis (2025-08-15) | The hierarchy had minimal impact against a same-size transformer; the outer refinement loop drove the performance ([ARC Prize](https://newhotness.arcprize.org/blog/hrm-analysis)); an independent replication found the same at matched compute ([SOTAVerified](https://sotaverified.org/blog/hierarchy-flat-loop)) | Matched-compute flat-loop control |
| Knierim et al., 2607.01483 (2026-07-01) and Papadopoulos et al., ALIFE 2026 (2026-08-17) | Tuned mutation matches pairwise interaction; coupling governs replicator *takeover*, not *emergence*; the two groups converged independently ([arXiv](https://arxiv.org/abs/2607.01483); [ALIFE program](https://2026.alife.org/wp-content/uploads/sites/2/2026/06/ALIFE2026-Program-Ver-2026-06-30.pdf)) | Mutation-only twin; measure emergence and takeover separately |
| Huxley-Gödel Machine, 2510.21614 (2025-10-24) | An agent's own benchmark score poorly predicts its lineage's productivity ([arXiv](https://arxiv.org/abs/2510.21614)) | Clade-level selection signal |
| "AI scientists produce results without reasoning scientifically," 2604.18805 (April 2026) | Agents ignore evidence in **68%** of traces and revise after refutation in only **26%**; the base model, not the scaffold, explains most variance ([Pith](https://pith.science/paper/2604.18805)) | Score revision-on-refutation, not output quality |
| "Failing to Falsify," 2604.02485 (April 2026) | On a Wason-style task, verify-only agents underperform agents that also seek disconfirming evidence ([arXiv](https://arxiv.org/html/2604.02485v1)) | Disconfirmation-seeking as a measured behavior |
| de Pinho and Sinapayen, 2603.01701 (2026-03-02) | Total evolutionary activity is unbounded, but normalized activity is bounded and new activity is null, so the system is not open-ended ([arXiv](https://arxiv.org/abs/2603.01701)) | Multi-statistic Bedau test, not total activity alone |
| MSPD, 2606.17091 (2026-06-12) | Static, Brownian and single-blob systems must score near zero ([arXiv](https://arxiv.org/abs/2606.17091)) | Explicit negative controls for any complexity metric |
| Open-Endedness Bench, 2610.02588 (2026-10-01) | Per a search summary, only 16–29% of research agents' claimed improvements hold against logged results ([arXiv](https://arxiv.org/abs/2610.02588)) | Log-grounded claim verification |
| ARC-AGI-3 technical report (2026) | On one environment variant, Opus 4.6 scored **0.0% with no harness and 97.1% with a custom harness** ([DataCamp](https://www.datacamp.com/blog/arc-agi-3)); the CNN+RL preview leader fell from 12.58% to 0.25% on the full set ([MindStudio](https://www.mindstudio.ai/blog/arc-agi-3-results-frontier-models-score-zero)) | Hold the harness fixed or ablate it |
| Physics-IQ Verified, 2606.18943 (2026) | Model rankings change significantly under audit ([Emergent Mind](https://www.emergentmind.com/papers/2606.18943)) | Store benchmark version and audit papers with every score |

Two benchmark findings work as **negative anchors** against overclaiming. AlgoTune (NeurIPS 2025) found that models "fail to discover algorithmic innovations" and prefer surface-level optimizations ([NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9a648e8e1014c2427156dcb5465cd488-Abstract-Datasets_and_Benchmarks_Track.html)). FrontierCO found that classical solvers still win on hard combinatorial instances ([ICLR slides](https://iclr.cc/media/iclr-2026/Slides/10010940.pdf)). In latent reasoning, "Do Latent Tokens Think?" (2512.21711) found Coconut's continuous thoughts insensitive to steering and exploiting dataset shortcuts ([arXiv](https://arxiv.org/abs/2512.21711v1)).

Two caveats keep this from becoming a blanket dismissal. First, several audits are themselves single studies or come through secondary summaries: the OEB figure is a snippet, and the 2604.18805 numbers come via a referee summary. They should enter the corpus at "probable," not "validated." Second, the audits do not show that the loops fail. They show that **credit assignment inside the loop is usually wrong**. That is precisely the question an evolutionary ecology with its own primitives is positioned to answer, for example by settling whether operator quality (AIRA-dojo) or archive structure (LEVI) dominates.

## Where the work is emitted: categories, labs, venues and benchmarks

### arXiv categories and the labs behind them

The preprint stream concentrates in **cs.NE** (18,441 total results on 2026-10-09) ([arXiv API](https://export.arxiv.org/api/query?search_query=cat:cs.NE&sortBy=submittedDate&sortOrder=descending&start=0&max_results=2)), **cs.AI**, **cs.LG**, **cs.PL** and **cs.LO** for program synthesis and provers, and **cs.MA** for LLM ecologies such as TerraLingua. ALife work also lands in **nlin.AO** (adaptation and self-organizing systems), **nlin.CG**, **q-bio.PE** and occasionally **math.DS**. The OAI-PMH sets `cs:cs:NE`, `cs:cs:AI`, `physics:nlin:AO` and `physics:nlin:CG` exist for incremental harvesting ([ListSets](https://oaipmh.arxiv.org/oai?verb=ListSets)).

Output is concentrated in a small number of labs:

- **Google DeepMind** keeps the core closed (AlphaEvolve, AlphaProof, Genie 3).
- **Sakana AI** is the most prolific open emitter across sub-areas: ShinkaEvolve, the AI Scientist line, ASAL, NCA ecologies, CTM and Digital Red Queen ([GitHub](https://github.com/SakanaAI/ShinkaEvolve)).
- **Jeff Clune's lab** at UBC and Vector does self-improvement work: DGM, Hyperagents with Meta FAIR, Automated Capability Discovery, and Foundation Model Self-Play.
- Other active groups:
  - KAUST/Schmidhuber (HGM)
  - Imperial's Adaptive and Intelligent Robotics lab (QDax, DNS, CAX)
  - Oxford FLAIR (Kinetix, Craftax, UED)
  - Google Paradigms of Intelligence (BFF soups)
  - the Levin lab
  - INRIA Flowers (SOAR, Lenia agency)
  - the ARC Prize Foundation
  - FutureHouse/Edison
  - Stanford SNAP (POPPER)
  - Ai2 (AutoDiscovery)
- **World models and alternative architectures:** Meta FAIR, Balestriero's galilai-group, Sapient, Samsung SAIL Montréal, VERSES, the Thousand Brains Project, TrueAGI and Liquid AI.
- **Lean provers:** DeepSeek, Moonshot/Numina, the Goedel-LM team, ByteDance Seed and Harmonic.

**Author-based polling catches more than org-based polling.** Researchers who bridge labs include Risi (Sakana and ITU), Kumar (MIT, Sakana and Clune collaborations), Foerster (FLAIR, Meta, Hyperagents) and Etcheverry (the Flowers lineage, now co-authoring Google's soup and NCA-reasoning papers). Much of their code lives under personal GitHub accounts. **Hugging Face is not where the ALife community publishes.** Only Sakana has a meaningful HF org, and no FLAIR or UCL DARK org exists ([HF](https://huggingface.co/SakanaAI)). HF matters for models, not for evolutionary or ALife code.

The single highest-value curated watch-list is **jennyzzt/awesome-open-ended** (475 stars, last push 2026-09-19) ([GitHub](https://github.com/jennyzzt/awesome-open-ended)). The **ARC Prize blog** is the best aggregator for non-LLM reasoning results, and **Terence Tao's blog** is a primary venue for AlphaEvolve and Erdős commentary.

### Conferences and workshops, with machine paths

There has been no dedicated open-endedness workshop at a major ML venue since ALOE at NeurIPS 2023 ([NeurIPS](https://neurips.cc/virtual/2023/workshop/66527)). The topic now appears in agent and self-improvement workshops, while ALIFE and GECCO remain the core evolutionary venues.

| Venue | 2025 edition | 2026 edition | Next | Machine path |
|---|---|---|---|---|
| ALIFE | Kyoto plus online, 6–10 Oct 2025 ([site](https://2025.alife.org/)) | Waterloo, 17–21 Aug 2026; proceedings at direct.mit.edu/isal/isal2026/volume/38 ([Complex Systems Digest](https://comdig.cssociety.org/2026/09/06/alife-2026-proceedings-of-the-2026-artificial-life-conference/)) | ALIFE 2027 likely Prague (unverified) | Crossref prefix 10.1162; MIT Press Direct is Cloudflare-gated |
| GECCO | Málaga, 14–18 Jul 2025 | Costa Rica, 13–17 Jul 2026, hybrid ([site](https://gecco-2026.sigevo.org/)); workshops on LLMs for and with EC, Program Synthesis, ECADA, BENCH and Evolving Self-Organisation ([workshops](https://gecco-2026.sigevo.org/Workshops)) | GECCO 2027 CfP live | Crossref prefix 10.1145 plus exact title/ISBN; the ACM DL is gated and dblp is walled |
| EvoStar | — | Toulouse, 8–10 Apr 2026 | Mainz, 31 Mar–2 Apr 2027; **deadline 1 Nov 2026** ([evostar.org](https://evostar.org)) | Site poll |
| PPSN | — | Trento; Risi keynote 31 Aug 2026 ([booklet](https://ppsn2026.disi.unitn.it/docs/PPSN_booklet.pdf)) | — | Site poll |
| ICLR | Venue for OMNI-EPIC and Kinetix | Workshops 26–27 Apr 2026: Lifelong Agents (LLA), Recursive Self-Improvement (RSI), MemAgent, AIWILD ([OpenReview](https://api2.openreview.net/groups?prefix=ICLR.cc/2026/Workshop/)) | ICLR.cc/2027/Conference group exists | OpenReview `/groups` |
| NeurIPS | Scaling Environments for Agents (SEA), 7 Dec 2025 ([NeurIPS](https://neurips.cc/virtual/2025/events/workshop)) | NeurIPS.cc/2026/Conference (`public_submissions` false) | — | OpenReview `/groups` |
| ICML | POPPER, SOAR, LLM-SRBench (oral) | Workshops SCALE and AI4Research ([OpenReview](https://api2.openreview.net/groups?prefix=ICML.cc/2026/Workshop/)) | — | OpenReview `/groups` |
| ARC Prize | 2025-03-26 to 2025-11-03 | ARC-AGI-3 track final deadline 2026-11-02; 2026 is the last year of the ARC-AGI-2 track ([ARC Prize](https://arcprize.org/competitions/2026/arc-agi-3)) | — | arcprize.org/blog, Kaggle |

### Benchmarks and datasets worth ingesting

The benchmarks split by what grounds their scores. Prometheus should prefer **machine-checkable** ground truth and treat LLM-judged metrics, such as AutoDiscovery's "surprise" or AI Scientist review scores, as uncalibrated.

| Benchmark | Identifier and date | Ground truth | Access |
|---|---|---|---|
| ARC-AGI-2 | 2505.11831 (2025-05-17) ([arXiv](https://arxiv.org/abs/2505.11831)) | Exact match | Public eval; private set on Kaggle |
| ARC-AGI-3 | 2603.24621 (launched 2026-03-25) | Action efficiency against human baselines | `pip install arc-agi` for local play; private games are Kaggle-only ([docs](https://docs.arcprize.org/toolkit/overview)) |
| AlphaEvolve/Tao problem set | 2511.02864 (67 problems) | Numeric bounds | Repo name truncated in sources (unverified) |
| ALE-Bench | 2506.09050 (NeurIPS 2025) ([arXiv](https://arxiv.org/pdf/2506.09050)) | AtCoder heuristic scores | — |
| LLM-SRBench | 2504.10415 (ICML 2025 oral; 239 problems) ([arXiv](https://arxiv.org/pdf/2504.10415)) | Symbolic accuracy | — |
| BLADE | 2504.20183 ([arXiv](https://arxiv.org/abs/2504.20183)) | Black-box optimizer performance | — |
| EvoTrace | 2605.20086 (2026-05-19) | Search traces with replay | Dataset location not captured |
| miniF2F, PutnamBench, FrontierMath: Erdős | 658–672 Putnam problems; 68 open Erdős problems (Aug 2026) | Lean kernel | Downloadable |
| MLE-bench | 2410.07095 ([GitHub](https://github.com/openai/mle-bench)) | Kaggle medals | Kaggle API, Git-LFS, ~2 days of preparation |
| Craftax, Kinetix, XLand-MiniGrid | 2402.16801, 2410.23208, 2312.12044 | RL return over open-ended task spaces | JAX repos; Kinetix v3.0.2 on 2026-09-24 ([GitHub](https://github.com/FLAIROx/Kinetix)) |
| Open-Endedness Bench | 2610.02588 (2026-10-01) | Log-verified research-agent claims | HF dataset `AgentNativeResearchLab/oeb-scored-runs` |
| COGITAO | 2509.05249 (ICML 2026) ([ICML](https://icml.cc/virtual/2026/69281)) | Compositional generalization on ARC-style grids | — |
| IntPhys 2, CausalVQA, MVPBench, Physics-IQ | 2506.09849, 2506.09943, 2501.09038 | Physical reasoning | Shared leaderboard ([HF Space](https://facebook-physical-reasoning-leaderboard.hf.space/)) |

No public, versioned dataset of long-running ALife or open-ended evolution runs (logged lineages or activity statistics) was found. That gap is one Prometheus could fill.

## One 16 GB GPU hosts operators, provers and embedders

The target machine is an **RTX 5060 Ti 16 GB (sm_120) with 32 GB RAM on Windows 11**. The fit verdicts below are GGUF file sizes, all cited, plus an inferred 1–2 GB for KV cache and runtime. Repo dates are Hugging Face `createdAt` values, which can precede public release. Benchmark figures are model-card claims.

| Role | Repo id (HF createdAt) | Cited size | Fit | License |
|---|---|---|---|---|
| Cheap mutation operator | `Qwen/Qwen3.5-9B` (2026-02-27/28) | Q4_K_M 5.7 GB; Q6_K 7.5 GB ([GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Agentic small coder | `microsoft/FrogNano-4B-2609` (2026-09-17) | 4.66B; bartowski GGUF ([HF](https://huggingface.co/microsoft/FrogNano-4B-2609)) | Full GPU | mit in metadata, Apache 2.0 in card (conflict) |
| Strong operator | `openai/gpt-oss-20b` (2025-08-04) | MXFP4 12.1 GB ([GGUF](https://huggingface.co/ggml-org/gpt-oss-20b-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Repair / recombination | `mistralai/Devstral-Small-2-24B-Instruct-2512` (2025-11-28) | IQ4_XS 12.8 GB ([GGUF](https://huggingface.co/unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF/tree/main)) | Tight | apache-2.0 |
| MoE coder | `Qwen/Qwen3-Coder-30B-A3B-Instruct` (2025-07-31) | Q4_K_M 18.6 GB ([GGUF](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF/tree/main)) | Expert offload to RAM | apache-2.0 |
| MoE coder/reasoner | `zai-org/GLM-4.7-Flash` (2026-01-19) | Q4_K_M 18.3 GB; card SWE-bench Verified 59.2 ([GGUF](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF/tree/main)) | Expert offload | mit |
| Flagship reasoner | `Qwen/Qwen3.8-27B` (2026-08-05) | UD-IQ4_XS 14.3 GB; UD-IQ3_XXS 10.9 GB ([GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main)) | Tight | apache-2.0 |
| Small reasoner | `google/gemma-4-12B-it` (2026-05-23) | Q4_K_M 7.1 GB ([GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Math reasoner | `microsoft/Phi-4-reasoning-plus` (2025-04-17) | Q4_K_M 9.1 GB ([GGUF](https://huggingface.co/unsloth/Phi-4-reasoning-plus-GGUF/tree/main)) | Full GPU | mit |
| ThetaEvolve reproduction arm | `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` (2025-05-29) | GGUF available ([HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B)) | Full GPU | mit |
| Lean prover | `Pythagoras-LM/Pythagoras-Prover-4B` (2026-06-07) | q4_k_m 2.7 GB; q8_0 4.7 GB ([GGUF](https://huggingface.co/tinyopsec/Pythagoras-Prover-4B-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Lean prover with self-correction | `Goedel-LM/Goedel-Prover-V2-8B` (2025-07-15) | Q4_K_M 5.0 GB ([GGUF](https://huggingface.co/mradermacher/Goedel-Prover-V2-8B-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Lean prover | `deepseek-ai/DeepSeek-Prover-V2-7B` (2025-04-30) | Q4_K_M 4.2 GB ([GGUF](https://huggingface.co/unsloth/DeepSeek-Prover-V2-7B-GGUF/tree/main)) | Full GPU | Not in metadata |
| Embedder | `Qwen/Qwen3-Embedding-8B` (2025-06-03) | Q4_K_M 4.7 GB; 32K context ([GGUF](https://huggingface.co/Qwen/Qwen3-Embedding-8B-GGUF/tree/main)) | Full GPU | apache-2.0 |
| Multimodal embedder | `google/embeddinggemma-2` (2026-09-14) | 0.74B; 768-d with MRL down to 128; 8K context ([HF](https://huggingface.co/google/embeddinggemma-2)) | Full GPU | apache-2.0 |
| Small embedder | `microsoft/harrier-oss-v1-0.6b` (2026-03-30) | 0.60B; MTEB v2 69.0 ([HF](https://huggingface.co/microsoft/harrier-oss-v1-0.6b)) | Full GPU | mit |
| Reranker | `Qwen/Qwen3-Reranker-4B` | 32K context ([HF](https://huggingface.co/Qwen/Qwen3-Reranker-4B)) | Full GPU | apache-2.0 |
| Simulated agent environment | `Qwen/Qwen-AgentWorld-35B-A3B` (2026-06-22) | IQ3_XXS 13.7 GB ([GGUF](https://huggingface.co/unsloth/Qwen-AgentWorld-35B-A3B-GGUF/tree/main)) | Tight or offload | apache-2.0 |
| Recursive-depth LM | `sapientinc/HRM-Text-1B` (2026-05-17) | 1.18B, pre-alignment ([HF](https://huggingface.co/sapientinc/HRM-Text-1B)) | Full GPU | apache-2.0 |

Three operating patterns follow from these sizes:

- **Mutation tier:** many cheap samples from 4–9B models, with a 20–35B MoE reserved for repair and recombination steps.
- **Prover ensemble:** Pythagoras-4B Q8 plus Goedel-8B plus DeepSeek-Prover-7B at Q4 is about 14 GB and can stay resident while Lean verification runs on CPU. Each prover expects a different Lean/Mathlib version (Lean 4.9 for the Goedel/DeepSeek lineage, 4.9.0-rc1 for Pythagoras), so a shared server must be pinned per prover.
- **Retrieval pair:** Qwen3-Embedding-0.6B or 4B plus Qwen3-Reranker, all Apache-licensed.

Lean tooling that pairs with the provers:

- `leanprover-community/repl` (last push 2026-10-07) ([GitHub](https://github.com/leanprover-community/repl))
- `project-numina/kimina-lean-server` ([GitHub](https://github.com/project-numina/kimina-lean-server))
- `oOo0oOo/lean-lsp-mcp` ([GitHub](https://github.com/oOo0oOo/lean-lsp-mcp))
- `lean-dojo/LeanDojo-v2` ([GitHub](https://github.com/lean-dojo/LeanDojo-v2))

Several items do **not** fit:

- Qwen3-Coder-Next (80B; Q4_K_M 48.5 GB) ([GGUF](https://huggingface.co/unsloth/Qwen3-Coder-Next-GGUF/tree/main)).
- Mistral's Leanstral (119B with 6.5B active) ([HF](https://huggingface.co/mistralai/Leanstral-2603)).
- Cosmos 2B models, which NVIDIA sizes at ~26–33 GB ([NVIDIA](https://docs.nvidia.com/cosmos/latest/predict2/model_matrix.html)).
- TRM training at ARC scale (4 H100 for about 3 days). Note also that no official TRM checkpoint exists on HF ([HF listing](https://huggingface.co/api/models?author=SamsungSAILMontreal&sort=createdAt&direction=-1&limit=10)).

**LeWorldModel** (~15M parameters) and **HRM's Sudoku demo**, which trains on a single RTX 4070 laptop GPU in about 10 h ([README](https://cdn.jsdelivr.net/gh/sapientinc/HRM@main/README.md)), are cheap enough to run many variants per day, which is what evolutionary pressure needs.

Watch the license traps:

- `facebook/cwm` is non-commercial and gated ([HF](https://huggingface.co/facebook/cwm)).
- The jina v5 embedders and jina-reranker-v3.5 are CC-BY-NC ([HF](https://huggingface.co/jinaai/jina-embeddings-v5-text-small)).
- NVIDIA and Liquid models use custom licenses.

The Blackwell-on-Windows stack is workable but has sharp edges:

- **Inference:** use Ollama v0.40.2 (2026-10-08) or llama.cpp b11521 (2026-10-09). llama.cpp ships a **CUDA 13.4** Windows build, and its CUDA 12.4 build predates sm_120 support ([Ollama](https://github.com/ollama/ollama/releases); [llama.cpp](https://github.com/ggml-org/llama.cpp/releases)).
- **vLLM:** no native Windows support is planned (maintainer, 2026-06-30). Use WSL2 or the community `SystemPanic/vllm-windows` ([vLLM #47119](https://github.com/vllm-project/vllm/issues/47119)).
- **NVFP4:** it falls back to Marlin in vLLM, and llama.cpp declined native SM120 NVFP4 MoE kernels ([llama.cpp #18250](https://github.com/ggml-org/llama.cpp/issues/18250)). Prefer GGUF K/IQ quants or MXFP4.
- **PyTorch:** 2.14.0 disables two cuDNN engines on sm_120 to prevent illegal memory accesses. The 2.14.1 notes document a CUDA compiler correctness bug "present since CUDA 12.8" ([PyTorch](https://github.com/pytorch/pytorch/releases)). For falsification-grade experiments, record the CUDA runtime and driver alongside model hashes.
- **OpenEvolve on Windows:** evolution calls must be wrapped in an `if __name__ == '__main__':` guard because Windows uses `spawn` multiprocessing ([GitHub](https://github.com/algorithmicsuperintelligence/openevolve)).

## Polling must route around four closed doors

Four sources that once served scripts no longer do, as of probes on 2026-10-09:

- **OpenReview** returns `403 ChallengeRequiredError` on anonymous `/notes` queries ([probe](https://api2.openreview.net/notes?content.venueid=ICLR.cc/2026/Conference&limit=1)).
- **DBLP** serves an Anubis proof-of-work page instead of JSON ([probe](https://dblp.org/search/publ/api?q=quality%20diversity&format=json&h=2)).
- **The ACM Digital Library** (GECCO) returns Cloudflare challenges ([probe](https://dl.acm.org/conference/gecco)).
- **MIT Press Direct** (ALIFE proceedings and the *Artificial Life* journal) also returns Cloudflare challenges ([probe](https://direct.mit.edu/isal)).

Papers with Code is gone and redirects to Hugging Face trending papers ([probe](https://paperswithcode.com/api/v1/papers/?q=evolution)). The durable spine is arXiv, Hugging Face, GitHub, Crossref and OpenAlex, with Semantic Scholar for enrichment under a key.

| Service | Endpoint | Verified limit | Verified | Storage terms |
|---|---|---|---|---|
| arXiv API, RSS, OAI-PMH | `export.arxiv.org/api/query`; `rss.arxiv.org`; `oaipmh.arxiv.org/oai` | **1 request per 3 s, one connection, across all your machines**; search slices ≤2,000, total ≤30,000 ([ToU](https://info.arxiv.org/help/api/tou.html); [manual](https://info.arxiv.org/help/api/user-manual.html)) | Probed 2026-10-09; no rate-limit headers returned | Metadata CC0; full text may be stored for research but not served |
| Hugging Face Hub | `/api/models`, `/api/daily_papers`, `/api/papers/*` | 500 API / 3,000 resolver / 100 page requests per 5 min anonymous; 1,000 / 5,000 / 200 with a free token; paper search has a separate **50 per 5 min** anonymous bucket ([docs](https://huggingface.co/docs/hub/rate-limits); [probe](https://huggingface.co/api/papers/search?q=open-endedness)) | Docs "September '25"; headers observed 2026-10-09 | Card text is user content under each repo's license |
| GitHub REST | `/search/repositories`, `/repos/*`, `releases.atom` | Core 60/h unauthenticated, 5,000/h with a PAT; search 10/min unauthenticated, 30/min authenticated; 1,000 results per search; GraphQL 0 without auth ([docs](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api); [probe](https://api.github.com/rate_limit)) | Observed 2026-10-09 | Per-repo license |
| Semantic Scholar | `/graph/v1/paper/search/bulk`, `/paper/batch` | 1 RPS with a key; anonymous shared pool gave 429 on 3 of 4 calls ([product page](https://www.semanticscholar.org/product/api)) | Observed 2026-10-09 | Internal non-commercial use only; attribution required; no redistribution ([license](https://api.semanticscholar.org/license/)) |
| OpenAlex | `api.openalex.org/works` | $0.10/day (~1,000 credits) keyless; 10x with a free key; 100 req/s cap; singleton lookups free, list $0.0001, search $0.001 ([help](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)) | Help page updated 2026-08-19; observed 2026-10-09 | CC0 |
| Crossref | `api.crossref.org/works` | List queries 1 rps public, 3 rps with `mailto`; single records 5 and 10 rps ([Crossref](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137)) | Post dated 2026-07-21; observed 2026-10-09 | Open metadata; abstracts are publisher-supplied |
| OpenReview | `api2.openreview.net/groups` | `/groups` anonymous at 20/min; `/notes` needs authentication ([probe](https://api2.openreview.net/groups?id=ICLR.cc/2026/Conference)) | Observed 2026-10-09 | Terms unverified |

The cheapest correct arXiv design has three parts:

- **Daily feed fetch:** one RSS/Atom fetch per category set per day, after 04:00–05:00 UTC, because feeds rebuild at midnight US Eastern ([RSS help](https://info.arxiv.org/help/rss.html)).
- **Authoritative incremental harvest:** OAI-PMH `ListRecords` with `metadataPrefix=arXivRaw`, which carries version history and per-paper license. Persist `from` datestamps rather than resumption tokens, which **expire daily** since the March 2025 move to `oaipmh.arxiv.org` ([OAI help](https://info.arxiv.org/help/oa/index.html)).
- **Backfills only:** use the search API for targeted backfills, because results do not change within a day.

arXiv's documentation conflicts with itself. The bulk-data page suggests bursts of 4 requests per second, while the Terms of Use say one request per 3 s ([bulk](https://info.arxiv.org/help/bulk_data.html)). Follow the stricter Terms of Use. The 2026-10-01 "rate limit" change covered **submissions**, not access ([arXiv blog](https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/)).

Hugging Face and GitHub usage:

- **Hugging Face:** a free token doubles the budget. Use `expand[]` to pull `safetensors`, `gguf` and `cardData` in one listing call. Prefer `daily_papers?date=` over search fan-out, given the 50-call search bucket.
- **GitHub:** per-repo `releases.atom` feeds are the cheapest release tracker. Compute star velocity internally rather than scraping `/trending`.

Recovering GECCO and ALIFE camera-ready versions without the gated publisher sites:

- **ALIFE and *Artificial Life*:** Crossref with prefix `10.1162` works; a 2026 query returned 150 *Artificial Life* items ([probe](https://api.crossref.org/works?filter=prefix:10.1162,from-pub-date:2026-01-01&query.container-title=Artificial+Life&rows=2&select=DOI,title,container-title,published)).
- **GECCO:** Crossref's fuzzy container-title match returns Springer's book series instead of GECCO ([probe](https://api.crossref.org/works?query.container-title=Genetic+and+Evolutionary+Computation+Conference&filter=from-pub-date:2026-01-01&rows=2&select=DOI,title,container-title,published)). Filter by prefix `10.1145` plus the exact proceedings title or ISBN.

Several of these terms changed in 2025–2026:

- arXiv OAI-PMH moved in March 2025.
- Hugging Face set new rate-limit tiers in September 2025.
- Crossref changed limits in December 2025 and again in July 2026.
- OpenAlex introduced metered budgets in 2026.

The pipeline should therefore carry `terms_version_seen` and `checked_at` per source and store S2-derived fields in a separately tagged, internal-only table.

## Conclusion

The adjacent frontier has largely converged on the loop Prometheus already runs. The scarce resource is no longer another propose–evaluate–archive system. It is **correct credit assignment inside the loop**. The 2026 audits — simple baselines, flat-loop controls, mutation-only twins, clade-level scoring and harness ablation — read like a specification for falsification instruments. The field built them reactively, one embarrassment at a time. That argues for an intake pipeline that ranks audit papers, negative results and trace datasets (EvoTrace, Open-Endedness Bench) at least as high as new systems. A new loop paper without a null arm is weak evidence. A new null arm is reusable infrastructure.

The second implication concerns what "growing reasoning mechanisms" means externally. The live edge has moved from frozen LLMs used as mutation operators to operators that learn within the run (ThetaEvolve, TTT-Discover, SOAR), and from artifact-level to lineage-level selection (HGM, Hyperagents). Both moves can be tested on a single 16 GB card with 4–9B open models. The unresolved AIRA-dojo versus LEVI question — whether operator quality or archive structure dominates — is one Prometheus can settle with its own primitives. Meanwhile the scholarly web is closing to scripts. Building the polling spine on arXiv, Crossref, OpenAlex, GitHub and Hugging Face now, with terms recorded per source, is cheaper than retrofitting after the next door shuts.

## Appendix: machine-readable seed lists

All identifiers are copied from the research notes compiled on 2026-10-09. Tags used throughout:

- `VERIFIED-LIVE`: probed on 2026-10-09.
- `DERIVED`: built from a documented URL pattern but not individually probed.
- `UNVERIFIED`: the notes could not confirm the item.

### (a) arXiv category codes and boolean query strings

```text
# === arXiv category codes (from notes) ===
cs.NE        # primary: evolutionary computation, ALife, QD (18,441 results in API on 2026-10-09)
cs.AI
cs.LG
cs.PL        # program synthesis / induction
cs.LO        # Lean / formal theorem proving
cs.MA        # multi-agent LLM ecologies (e.g. TerraLingua 2603.16910)
nlin.AO      # adaptation and self-organizing systems (ALife)
nlin.CG      # cellular automata and lattice gases
q-bio.PE     # populations and evolution (ToLSim 2603.01701, Training Ecosystems 2605.30109)
q-bio.NC     # neurons and cognition (appears in arXiv RSS help example)
math.DS      # dynamical systems (Minary autopoiesis 2601.04501)

# === OAI-PMH set specs (VERIFIED-LIVE via ListSets 2026-10-09) ===
cs:cs:NE
cs:cs:AI
physics:nlin:AO
physics:nlin:CG

# === search_query strings for https://export.arxiv.org/api/query ===
# Syntax per arXiv API manual: prefixes ti/au/abs/cat/all; AND, OR, ANDNOT; parentheses %28 %29;
# phrases in %22...%22 (shown unencoded below for readability); spaces -> '+'.
# Append &sortBy=submittedDate&sortOrder=descending&max_results=200 ; sleep 3 s between calls.
# Date window template: AND submittedDate:[YYYYMMDDTTTT TO YYYYMMDDTTTT]   (GMT)

Q_LLM_EVOLUTION = (cat:cs.NE OR cat:cs.AI OR cat:cs.LG) AND (abs:"AlphaEvolve" OR abs:"FunSearch" OR abs:"evolutionary coding agent" OR abs:"program evolution" OR abs:"code evolution" OR abs:"LLM-guided evolution" OR abs:"evolution through large models")
Q_PROGRAM_SYNTHESIS = (cat:cs.AI OR cat:cs.LG OR cat:cs.PL) AND (abs:"ARC-AGI" OR abs:"refinement loop" OR abs:"library learning" OR abs:"program synthesis" OR abs:"program induction")
Q_LEAN_PROVERS = (cat:cs.LO OR cat:cs.AI OR cat:cs.LG) AND (abs:"Lean 4" OR abs:"theorem prover" OR abs:"miniF2F" OR abs:"PutnamBench" OR abs:"autoformalization")
Q_FALSIFICATION_AGENTS = (cat:cs.AI OR cat:cs.LG OR cat:cs.MA) AND (abs:"falsification" OR abs:"hypothesis validation" OR abs:"hypothesis testing" OR abs:"AI scientist" OR abs:"automated scientific discovery" OR abs:"confirmation bias")
Q_OPEN_ENDEDNESS = (cat:cs.NE OR cat:cs.AI OR cat:nlin.AO OR cat:q-bio.PE) AND (abs:"open-endedness" OR abs:"open-ended evolution" OR abs:"open-ended learning" OR abs:"artificial life")
Q_SELF_REPLICATION_ALIFE = (cat:cs.NE OR cat:nlin.AO OR cat:nlin.CG OR cat:q-bio.PE) AND (abs:"self-replicator" OR abs:"self-replicating" OR abs:"primordial soup" OR abs:"artificial chemistry" OR abs:"evolvability")
Q_NCA_LENIA = (cat:cs.NE OR cat:nlin.CG OR cat:nlin.AO OR cat:cs.LG) AND (abs:"neural cellular automata" OR abs:"Lenia" OR abs:"cellular automata")
Q_QUALITY_DIVERSITY = (cat:cs.NE OR cat:cs.LG OR cat:cs.AI) AND (abs:"quality-diversity" OR abs:"MAP-Elites" OR abs:"novelty search" OR abs:"dominated novelty search")
Q_ENV_GENERATION_UED = (cat:cs.LG OR cat:cs.AI OR cat:cs.NE) AND (abs:"unsupervised environment design" OR abs:"environment generation" OR abs:"POET" OR abs:"open-ended environment")
Q_SELF_MODIFYING = (cat:cs.AI OR cat:cs.LG OR cat:cs.NE OR cat:math.DS) AND (abs:"Godel Machine" OR abs:"Gödel Machine" OR abs:"self-improving agent" OR abs:"self-referential" OR abs:"autopoiesis" OR abs:"autopoietic")
Q_WORLD_MODELS = (cat:cs.LG OR cat:cs.AI) AND (abs:"JEPA" OR abs:"world model" OR abs:"Dreamer")
Q_LATENT_RECURSIVE = (cat:cs.LG OR cat:cs.AI) AND (abs:"recursive reasoning" OR abs:"Hierarchical Reasoning Model" OR abs:"Tiny Recursive" OR abs:"looped language model" OR abs:"latent reasoning" OR abs:"energy-based transformer" OR abs:"Continuous Thought Machine")
Q_COGNITIVE_ARCH = (cat:cs.AI OR cat:q-bio.NC OR cat:cs.LG) AND (abs:"active inference" OR abs:"Thousand Brains" OR abs:"OpenCog" OR abs:"Hyperon" OR abs:"MeTTa" OR abs:"NARS" OR abs:"cognitive architecture")

# === Author queries (names from notes; surname-only au: may need cat: filter to disambiguate) ===
AU_CLUNE_LAB   = au:Clune
AU_SAKANA      = au:Risi OR au:Lange OR au:Darlow
AU_IMPERIAL    = au:Cully OR au:Faldor
AU_FLAIR       = au:Foerster
AU_FLOWERS     = au:Oudeyer OR au:Etcheverry OR au:Plantec OR au:Pourcel
AU_GOOGLE_POI  = au:Mordvintsev OR au:Randazzo OR au:Niklasson
AU_LEVIN       = au:Levin AND (cat:q-bio.PE OR cat:cs.NE OR cat:nlin.AO)
AU_JEPA        = au:LeCun OR au:Balestriero
AU_DREAMER     = au:Hafner
AU_RECURSIVE   = au:Jolicoeur-Martineau
AU_ACTIVE_INF  = au:Friston
AU_TBP         = au:Leadholm OR au:Hawkins
AU_ARC         = au:Chollet
AU_SCHMIDHUBER = au:Schmidhuber
AU_SSM         = (au:Gu OR au:Dao) AND cat:cs.LG
AU_SAYAMA      = au:Sayama
```

### (b) Hugging Face org/author ids and repo ids worth polling

```text
# === Model-publishing orgs/authors (author= filter on /api/models) ===
SakanaAI
Goedel-LM
deepseek-ai
julien31                 # SOAR program-synthesis models
AI-MO                    # Kimina-Prover distills
Pythagoras-LM
Qwen
google
mistralai
openai
nvidia
microsoft
ByteDance-Seed
ByteDance
sapientinc
facebook
LiquidAI
RWKV
BlinkDL
fla-hub
tiiuae
ibm-granite
allenai
JetBrains
zai-org
jinaai
BAAI
nomic-ai
Snowflake
mixedbread-ai
perplexity-ai
Alibaba-NLP
lightonai
Skywork
tomg-group-umd
prism-ml
openbmb
WeiboAI
ServiceNow-AI
agentica-org
Kwaipilot
inclusionAI
internlm
GSAI-ML
Dream-org
Zyphra
state-spaces
apple
SamsungSAILMontreal      # org exists; no TRM checkpoint found 2026-10-09
# GGUF mirror allowlist (from notes)
unsloth
bartowski
ggml-org
lmstudio-community
mradermacher
# No HF org found for: FLAIR (FLAIROx), ucl-dark, AMI Labs

# === Datasets ===
AgentNativeResearchLab/oeb-scored-runs      # Open-Endedness Bench (2610.02588)
paperswithcode/paperswithcode-data          # last Papers with Code snapshot (secondary sources)

# === Spaces ===
facebook-physical-reasoning-leaderboard     # https://facebook-physical-reasoning-leaderboard.hf.space/

# === Collections ===
# None named in notes; enumerate via GET https://huggingface.co/api/collections (documented in openapi.json)

# === Tag filters ===
evolutionary-algorithms                     # /api/models?filter=evolutionary-algorithms (returned julien31/Soar-qwen-7b)

# === Model repo ids: code / mutation operators ===
openai/gpt-oss-20b
ggml-org/gpt-oss-20b-GGUF
Qwen/Qwen3-Coder-30B-A3B-Instruct
unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF
Qwen/Qwen3-Coder-Next
mistralai/Devstral-Small-2-24B-Instruct-2512
unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF
mistralai/Devstral-Small-2507
Qwen/Qwen3.6-35B-A3B
unsloth/Qwen3.6-35B-A3B-GGUF
zai-org/GLM-4.7-Flash
unsloth/GLM-4.7-Flash-GGUF
microsoft/FrogNano-4B-2609
bartowski/FrogNano-4B-2609-GGUF
ByteDance-Seed/Seed-Coder-8B-Instruct
ByteDance-Seed/Seed-Coder-8B-Reasoning
ByteDance-Seed/Stable-DiffCoder-8B-Instruct
apple/DiffuCoder-7B-cpGRPO
JetBrains/Mellum-4b-base
JetBrains/Mellum2.1-12B-A2.5B-Thinking
JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF
Qwen/Qwen2.5-Coder-14B-Instruct
nvidia/OpenCodeReasoning-Nemotron-14B
agentica-org/DeepCoder-14B-Preview
Kwaipilot/KAT-Dev
facebook/cwm                                # non-commercial, gated
tiiuae/Falcon-H1-Tiny-Coder-90M
julien31/Soar-qwen-7b
julien31/Soar-qwen-32b
julien31/Soar-mistral-123b   # EXPANDED from notes shorthand; resolve before use

# === Model repo ids: math / reasoning ===
Qwen/Qwen3.8-27B
unsloth/Qwen3.8-27B-GGUF
nvidia/Qwen3.8-27B-NVFP4
prism-ml/Ternary-Bonsai-2-27B-gguf
Qwen/Qwen3.6-27B
unsloth/Qwen3.6-27B-GGUF
Qwen/Qwen3.5-9B
unsloth/Qwen3.5-9B-GGUF
Qwen/Qwen3.5-27B
Qwen/Qwen3.5-35B-A3B
Qwen/Qwen3-4B-Thinking-2507
Qwen/Qwen3-30B-A3B-Thinking-2507
Qwen/Qwen3-8B
Qwen/Qwen3-14B
google/gemma-4-12B-it
unsloth/gemma-4-12b-it-GGUF
google/gemma-4-26B-A4B-it
unsloth/gemma-4-26B-A4B-it-GGUF
google/gemma-4-31B-it
google/gemma-4-E4B-it
google/gemma-4-E2B-it
microsoft/Phi-4-reasoning-plus
unsloth/Phi-4-reasoning-plus-GGUF
microsoft/Phi-4-mini-reasoning
microsoft/Phi-4-mini-flash-reasoning
mistralai/Ministral-3-14B-Reasoning-2512
mistralai/Magistral-Small-2509
unsloth/Magistral-Small-2509-GGUF
deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16
nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16
nvidia/NVIDIA-Nemotron-Nano-9B-v2
nvidia/OpenMath-Nemotron-14B
nvidia/AceReason-Nemotron-1.1-7B
ibm-granite/granite-4.2-8b
ibm-granite/granite-4.2-30b
ibm-granite/granite-4.2-30b-GGUF
allenai/Olmo-3-7B-Think
allenai/Olmo-Hybrid-7B
tiiuae/Falcon-H1R-7B
WeiboAI/VibeThinker-1.5B
ServiceNow-AI/Apriel-1.6-15b-Thinker
openbmb/MiniCPM5-2B
inclusionAI/Ling-3.0-tiny

# === Model repo ids: Lean provers / formalizers ===
Pythagoras-LM/Pythagoras-Prover-4B
tinyopsec/Pythagoras-Prover-4B-GGUF
Pythagoras-LM/Pythagoras-Prover-32B
Pythagoras-LM/Pythagoras-Prover-Diffusion-4B
Goedel-LM/Goedel-Prover-V2-8B
mradermacher/Goedel-Prover-V2-8B-GGUF
Goedel-LM/Goedel-Prover-V2-32B
Goedel-LM/Goedel-Formalizer-V2-8B
Goedel-LM/Goedel-Code-Prover-8B
mradermacher/Goedel-Code-Prover-8B-GGUF
deepseek-ai/DeepSeek-Prover-V2-7B
unsloth/DeepSeek-Prover-V2-7B-GGUF
AI-MO/Kimina-Prover-Distill-8B
AI-MO/Kimina-Prover-Distill-1.7B   # EXPANDED from notes shorthand; resolve before use
AI-MO/Kimina-Prover-Distill-0.6B   # EXPANDED from notes shorthand; resolve before use
AI-MO/Kimina-Prover-RL-1.7B   # EXPANDED from notes shorthand; resolve before use
AI-MO/Kimina-Prover-RL-0.6B   # EXPANDED from notes shorthand; resolve before use
AI-MO/Kimina-Autoformalizer-7B
ByteDance-Seed/BFS-Prover-V2-7B
ByteDance-Seed/BFS-Prover-V2-32B   # EXPANDED from notes shorthand; resolve before use
internlm/internlm2_5-step-prover
mistralai/Leanstral-2603                    # 119B-A6.5B, does not fit 16 GB
mistralai/Leanstral-1.5-119B-A6B
saccha-ai/Sequent-Prover-9B-Preview         # low signal
anonymous-submission-ICLR2027/Gobble-Prover-1.7B   # UNVERIFIED claims

# === Model repo ids: embeddings / rerankers ===
Qwen/Qwen3-Embedding-0.6B
Qwen/Qwen3-Embedding-4B
Qwen/Qwen3-Embedding-8B
Qwen/Qwen3-Embedding-8B-GGUF
Qwen/Qwen3-VL-Embedding-2B
Qwen/Qwen3-VL-Embedding-8B   # EXPANDED from notes shorthand; resolve before use
google/embeddinggemma-2
unsloth/embeddinggemma-2-GGUF
google/embeddinggemma-300m
jinaai/jina-embeddings-v5-text-small        # cc-by-nc-4.0
jinaai/jina-embeddings-v5-text-nano         # cc-by-nc-4.0
jinaai/jina-code-embeddings-1.5b            # cc-by-nc-4.0
microsoft/harrier-oss-v1-0.6b
nvidia/Nemotron-3-Embed-1B-BF16
nvidia/Nemotron-3-Embed-8B-BF16
nvidia/llama-embed-nemotron-8b
perplexity-ai/pplx-embed-v1-0.6b
BAAI/bge-m3
BAAI/bge-reasoner-embed-qwen3-8b-0923
nomic-ai/nomic-embed-text-v1.5
nomic-ai/nomic-embed-text-v2-moe
nomic-ai/nomic-embed-code
Snowflake/snowflake-arctic-embed-l-v2.0
mixedbread-ai/mxbai-embed-large-v1
ibm-granite/granite-embedding-english-r2
LiquidAI/LFM2.5-Embedding-350M
Alibaba-NLP/gte-modernbert-base
lightonai/GTE-ModernColBERT-v1
Qwen/Qwen3-Reranker-0.6B
Qwen/Qwen3-Reranker-4B
Qwen/Qwen3-Reranker-8B   # EXPANDED from notes shorthand; resolve before use
ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF
jinaai/jina-reranker-v3.5                   # cc-by-nc-4.0
mixedbread-ai/mxbai-rerank-large-v2
BAAI/bge-reranker-v2-m3

# === Model repo ids: world models, recursive/latent, non-transformer ===
Qwen/Qwen-AgentWorld-35B-A3B
unsloth/Qwen-AgentWorld-35B-A3B-GGUF
facebook/vjepa2-vitl-fpc64-256              # family prefix facebook/vjepa2-*
Skywork/Matrix-Game-2.0
nvidia/Cosmos-Predict2.5-14B
sapientinc/HRM-Text-1B
sapientinc/HRM-Text-1B-v3.2
sapientinc/HRM-checkpoint-ARC-2
sapientinc/HRM-checkpoint-sudoku-extreme
sapientinc/HRM-checkpoint-maze-30x30-hard
gaoxin492/TinyRecursiveModels-ARC-AGI-2     # community, provenance UNVERIFIED
SakanaAI/ctm-imagenet
SakanaAI/EvoVLM-JP-v1-7B
tomg-group-umd/huginn-0125
ByteDance/Ouro-1.4B                         # research-only
ByteDance/Ouro-2.6B
RWKV/RWKV7-G1k-13.3B-20260930   # EXPANDED from notes shorthand; resolve before use
BlinkDL/rwkv7-g1
LiquidAI/LFM2.5-8B-A1B
LiquidAI/LFM2.5-2.6B
LiquidAI/LFM2.5-1.2B-Instruct
LiquidAI/LFM2-8B-A1B
state-spaces/mamba2-2.7b
mistralai/Mamba-Codestral-7B-v0.1
nvidia/Nemotron-H-8B-Reasoning-128K
Zyphra/Zamba2-7B-instruct
tiiuae/Falcon-H1-7B-Instruct
ibm-granite/granite-4.0-h-tiny
GSAI-ML/LLaDA-8B-Instruct
inclusionAI/LLaDA2.0-mini
Dream-org/Dream-v0-Instruct-7B
nvidia/Nemotron-Labs-Diffusion-3B
google/diffusiongemma-26B-A4B-it

# === API query templates (VERIFIED-LIVE parameter forms, 2026-10-09) ===
https://huggingface.co/api/models?author=<org>&sort=createdAt&direction=-1&limit=30&expand[]=createdAt&expand[]=cardData&expand[]=safetensors&expand[]=gguf
https://huggingface.co/api/models?num_parameters=min:0,max:24B&pipeline_tag=text-generation&sort=trendingScore&direction=-1&limit=30
https://huggingface.co/api/models?pipeline_tag=feature-extraction&sort=trendingScore&direction=-1&limit=30
https://huggingface.co/api/models?filter=gguf&search=<name>
https://huggingface.co/api/models/<repo_id>/tree/main?recursive=true
https://huggingface.co/api/daily_papers?date=<YYYY-MM-DD>&limit=100
https://huggingface.co/api/papers/<arxiv_id>
```

### (c) RSS/Atom feed URLs

```text
# === arXiv (VERIFIED-LIVE 2026-10-09) ===
https://rss.arxiv.org/rss/cs.NE
https://rss.arxiv.org/atom/cs.NE+cs.AI
https://export.arxiv.org/rss/cs.NE                     # legacy, identical content
# DERIVED from documented pattern rss.arxiv.org/{rss|atom}/<cat>[+<cat>] (multi-category limit 2000 items):
https://rss.arxiv.org/atom/cs.LG
https://rss.arxiv.org/atom/cs.PL+cs.LO
https://rss.arxiv.org/atom/nlin.AO+nlin.CG
https://rss.arxiv.org/atom/q-bio.PE+q-bio.NC
https://rss.arxiv.org/atom/cs.MA
# OAI-PMH incremental harvest (pattern; base URL VERIFIED-LIVE):
https://oaipmh.arxiv.org/oai?verb=ListRecords&metadataPrefix=arXivRaw&set=cs:cs:NE&from=<YYYY-MM-DD>

# === Lab blogs (VERIFIED-LIVE 2026-10-09) ===
https://deepmind.google/blog/rss.xml                   # atom:link self-ref wrongly says example.com
https://openai.com/news/rss.xml
https://sakana.ai/feed.xml                             # mixed Japanese/English entries
https://research.google/blog/rss/
https://blog.google/technology/ai/rss/                 # 301 -> https://blog.google/innovation-and-ai/technology/ai/rss/
https://bair.berkeley.edu/blog/feed.xml
https://www.microsoft.com/en-us/research/feed/
https://blogs.nvidia.com/feed/
https://huggingface.co/blog/feed.xml                   # counts against HF "pages" bucket (100/5 min anon)
https://lilianweng.github.io/index.xml

# === Newsletters (VERIFIED-LIVE 2026-10-09) ===
https://jack-clark.net/feed/
https://importai.substack.com/feed
https://www.interconnects.ai/feed
https://www.latent.space/feed
https://magazine.sebastianraschka.com/feed
https://lastweekin.ai/feed
https://thegradient.pub/rss/
https://www.alignmentforum.org/feed.xml

# === Societies (VERIFIED-LIVE 2026-10-09) ===
https://alife.org/feed/                                # ISAL news/announcements

# === No feed found (404) -> fallback ===
# Anthropic: https://www.anthropic.com/sitemap.xml (diff <lastmod>)
# Meta AI: https://ai.meta.com/blog/rss/ (404) -> HTML index poll
# The Batch: https://www.deeplearning.ai/the-batch/feed/ (404)

# === HTML-only sources named in notes (no feed URL verified; poll index pages) ===
# https://arcprize.org/blog
# https://epoch.ai/latest
# https://allenai.org/blog
# https://edisonscientific.com
# https://pub.sakana.ai
# https://www.drmichaellevin.org/publications
# https://www.verses.ai/research-blog
# https://www.liquid.ai/blog
# https://thousandbrains.discourse.group
# https://comdig.cssociety.org
# terrytao.wordpress.com

# === GitHub releases Atom ===
https://github.com/SakanaAI/AI-Scientist/releases.atom   # VERIFIED-LIVE
# DERIVED from pattern https://github.com/<owner>/<repo>/releases.atom (repos that tag releases per notes):
https://github.com/SakanaAI/ShinkaEvolve/releases.atom
https://github.com/adaptive-intelligent-robotics/QDax/releases.atom
https://github.com/icaros-usc/pyribs/releases.atom
https://github.com/RobertTLange/evosax/releases.atom
https://github.com/nnaisense/evotorch/releases.atom
https://github.com/EMI-Group/evox/releases.atom
https://github.com/maxencefaldor/cax/releases.atom
https://github.com/MichaelTMatthews/Craftax/releases.atom
https://github.com/FLAIROx/Kinetix/releases.atom
https://github.com/dunnolab/xland-minigrid/releases.atom
https://github.com/chrxh/alien/releases.atom
https://github.com/opennars/OpenNARS-for-Applications/releases.atom
https://github.com/ollama/ollama/releases.atom
https://github.com/ggml-org/llama.cpp/releases.atom
https://github.com/pytorch/pytorch/releases.atom
```

### (d) GitHub owner/repo ids

```text
# === Orgs / owners to sweep (pushed_at + new repos) ===
google-deepmind
SakanaAI
facebookresearch
arcprize
flowersteam                 # UNVERIFIED via API (rate-limited); SOAR repo cited under it
snap-stanford
future-house
allenai
deepseek-ai
MoonshotAI
Optima-CityU
gepa-ai
adaptive-intelligent-robotics
FLAIROx
ucl-dark
paradigms-of-intelligence
google-research
galilai-group
thousandbrainsproject
trueagi-io
sapientinc
nvidia-cosmos
SkyworkAI
infer-actively
metauto-ai
EMI-Group
algorithmicsuperintelligence
VersesTech
Liquid4All

# === LLM-guided evolution / program synthesis ===
algorithmicsuperintelligence/openevolve
SakanaAI/ShinkaEvolve
inter-co/science-codeevolve
AIRI-Institute/gigaevo-core          # UNVERIFIED which of these two is current
FusionBrainLab/gigaevo-core
liugangcode/deepevolve
ttanv/levi
gepa-ai/gepa
google-deepmind/funsearch
CarperAI/OpenELM                     # stale (2023)
beeevita/EvoPrompt
FeiLiu36/EoH
ai4co/LLM-as-HH
Optima-CityU/LLM4AD
Google-Cloud-AI/alphaevolve-on-googlecloud   # UNVERIFIED (named by third-party tutorial)

# === Self-improving / self-modifying agents ===
jennyzzt/dgm
metauto-ai/HGM
facebookresearch/HyperAgents
SakanaAI/drq

# === Automated science / falsification ===
snap-stanford/POPPER
SakanaAI/AI-Scientist-v2
SakanaAI/AI-Scientist
SamuelSchmidgall/AgentLaboratory
future-house/aviary
Future-House/paper-qa
openai/mle-bench
ARA-Labs/oeb

# === ARC / program induction / library learning ===
fchollet/ARC-AGI
arcprize/ARC-AGI-3-Agents
flowersteam/SOAR
SamsungSAILMontreal/TinyRecursiveModels   # archived
if-ai/TinyRecursiveModels                 # fork with uv setup
sapientinc/HRM
poetiq-ai/poetiq-arc-agi-solver
jerber/arc-lang-public
ijoffe/ARC-VSA-2025
CoreThink-AI/Research-publications
mlb2251/stitch
MoonshotAI/Kimina-Prover-Preview

# === Lean tooling ===
leanprover-community/repl
project-numina/kimina-lean-server
augustepoiroux/LeanInteract
oOo0oOo/lean-lsp-mcp
lean-dojo/LeanDojo-v2
lean-dojo/LeanDojo
lenianiva/PyPantograph                    # moved; current location UNVERIFIED

# === QD / evolutionary computation libraries ===
adaptive-intelligent-robotics/QDax
adaptive-intelligent-robotics/Dominated-Novelty-Search
icaros-usc/pyribs
RobertTLange/evosax
nnaisense/evotorch
EMI-Group/evox
EMI-Group/tensorneat
google/evojax                             # archived

# === ALife substrates ===
maxencefaldor/cax
SakanaAI/asal
SakanaAI/petri-dish-nca
arberzela/pbt-nca
paradigms-of-intelligence/cubff
google-research/self-organising-systems
Chakazul/Lenia                            # dormant
erwanplantec/FlowLenia
maxencefaldor/Leniabreeder
chrxh/alien
devosoft/avida
ChakshuGupta13/lab
jennyzzt/awesome-open-ended               # curated watch-list

# === Environment generation / UED / open-ended RL ===
MichaelTMatthews/Craftax
FLAIROx/Kinetix
dunnolab/xland-minigrid
DramaCow/jaxued
facebookresearch/minimax                  # stale
facebookresearch/dcd                      # archived
luchris429/JaxLife                        # stale
EvolutionGym/evogym
maxencefaldor/omni-epic
uber-research/poet                        # dormant since 2022-03-23
Gen-Verse/GenEnv

# === World models / latent reasoning / cognitive architectures ===
facebookresearch/vjepa2
facebookresearch/jepa-wms
facebookresearch/nwm
facebookresearch/coconut
facebookresearch/jepa
galilai-group/lejepa
galilai-group/stable-worldmodel
galilai-group/stable-pretraining
lucas-maes/le-wm
nvidia-cosmos/cosmos-predict2.5
nvidia-cosmos/cosmos-reason1
SkyworkAI/Matrix-Game
eloialonso/diamond
danijar/dreamerv3
nicklashansen/dreamer4                    # unofficial
lucidrains/dreamer4                       # unofficial
SakanaAI/continuous-thought-machines
seal-rg/recurrent-pretraining
alexiglad/EBT
VersesTech/axiom                          # frozen since 2025-06-02
infer-actively/pymdp
ReactiveBayes/RxInfer.jl
thousandbrainsproject/tbp.monty
trueagi-io/hyperon-experimental
trueagi-io/MORK
trueagi-io/PeTTa
trueagi-io/metta-wam
opencog/atomspace
opennars/OpenNARS-for-Applications
SoarGroup/Soar
Liquid4All/cookbook
Liquid4All/liquid-audio
raminmh/CfC
jxiw/M1
state-spaces/mamba
BICLab/SpikingBrain-7B
fangwei123456/spikingjelly
synsense/rockpool
lava-nc/lava                              # archived
google-deepmind/physics-IQ-benchmark

# === Local inference stack (Windows / sm_120) ===
ollama/ollama
ggml-org/llama.cpp
SystemPanic/vllm-windows
vllm-project/vllm
Dao-AILab/flash-attention
bitsandbytes-foundation/bitsandbytes
abetlen/llama-cpp-python
pytorch/pytorch

# === Search queries (GET /search/repositories, sort=updated, add pushed:>=<last_run>) ===
topic:open-endedness
topic:evolutionary-algorithms
topic:artificial-life
topic:quality-diversity
"arxiv.org/abs/2610" in:readme
```

### (e) External APIs, verified rate limits and verification dates

```text
# service | endpoint | limit | auth | verified | source / notes
arXiv API | https://export.arxiv.org/api/query | 1 req / 3 s; 1 connection; applies across all machines you control; slices <=2000, total <=30000 (HTTP 400 above) | none | ToU page undated; live probe 2026-10-09 (no rate-limit headers) | https://info.arxiv.org/help/api/tou.html ; https://info.arxiv.org/help/api/user-manual.html
arXiv RSS/Atom | https://rss.arxiv.org/{rss|atom}/<cat> | same 1 req / 3 s legacy-API limit; feeds rebuild daily at midnight US Eastern; multi-category limit 2000 items | none | live probe 2026-10-09 | https://info.arxiv.org/help/rss.html
arXiv OAI-PMH | https://oaipmh.arxiv.org/oai | same 1 req / 3 s; resumptionToken expires daily; earliestDatestamp 2005-09-16 | none | base moved March 2025; live probe 2026-10-09 | https://info.arxiv.org/help/oa/index.html
arXiv bulk | S3 / Kaggle | CONFLICT: bulk page suggests bursts of 4 req/s with 1 s sleep vs ToU 1 req / 3 s -> use ToU | none | 2026-10-09 | https://info.arxiv.org/help/bulk_data.html
arXiv submissions (not access) | n/a | 2 submissions per calendar month; 3 active max | account | announced 2026-10-01 | https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/
Hugging Face Hub API | https://huggingface.co/api/* | 5-min fixed windows. Anonymous: 500 api / 3000 resolvers / 100 pages per IP. Free: 1000/5000/200. PRO: 2500/12000/400. Team: 3000/20000/400. Enterprise: 6000/50000/600. Enterprise Plus: 10000/100000/1000. Academia Hub: 3000/20000/400 | optional HF_TOKEN | docs "September '25"; headers observed 2026-10-09 (q=500;w=300) | https://huggingface.co/docs/hub/rate-limits
Hugging Face paper search | https://huggingface.co/api/papers/search | separate "search" bucket: 50 / 300 s anonymous (undocumented); token quota UNVERIFIED | optional | observed 2026-10-09 | https://huggingface.co/api/papers/search?q=open-endedness
Hugging Face openapi spec | https://huggingface.co/.well-known/openapi.json | "media" bucket 10000 / 300 s | none | observed 2026-10-09 | live
GitHub REST core | https://api.github.com | 60/h unauthenticated per IP; 5000/h PAT; App installs 5000 scaling to 12500 (15000 Enterprise Cloud); GITHUB_TOKEN 1000/h per repo | PAT recommended | docs (X-GitHub-Api-Version 2026-03-10); /rate_limit probe 2026-10-09 | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
GitHub REST search | https://api.github.com/search/* | 10/min unauthenticated; 30/min authenticated; code search needs auth, 10/min per docs (/rate_limit reported code_search 60 unauthenticated); 1000 results max per search; per_page <=100; query <=256 chars, <=5 operators | PAT | probe 2026-10-09 | https://docs.github.com/en/rest/search/search
GitHub secondary limits | all REST | <=100 concurrent; <=900 points/min (GET=1); <=90 s CPU per 60 s; on 403/429 wait for x-ratelimit-reset / retry-after, else >=1 min exponential backoff | - | docs 2026-10-09 | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
GitHub GraphQL | https://api.github.com/graphql | limit 0 without auth | PAT required | probe 2026-10-09 | https://api.github.com/rate_limit
Semantic Scholar Graph | https://api.semanticscholar.org/graph/v1 | key: 1 RPS on all endpoints; unauthenticated: shared 1000 RPS pool, throttled (3 of 4 anonymous calls -> 429 on 2026-10-09); /paper/batch <=500 ids; /paper/search/bulk <=1000 per call, <=10,000,000 total | API key | product page + probe 2026-10-09 | https://www.semanticscholar.org/product/api ; license https://api.semanticscholar.org/license/ (internal non-commercial; attribution; no redistribution)
Semantic Scholar Datasets | https://api.semanticscholar.org/datasets/v1/release/ | downloads require API key (401 without); latest release 2026-09-29 | API key | probe 2026-10-09 | live
OpenAlex | https://api.openalex.org | keyless $0.10/day (~1000 credits); free key 10x ($1/day); cap 100 req/s; singleton free, list/filter $0.0001, search $0.001; per-page max 100 | api_key optional | help page "Last updated August 19, 2026"; headers observed 2026-10-09 | https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication (data CC0)
Crossref REST | https://api.crossref.org | single record: 5 rps public / 10 rps polite; list queries: 1 rps public / 3 rps polite; concurrency 1 public / 3 polite (via search summary); polite pool selected by real mailto | mailto | post dated 2026-07-21; observed x-rate-limit-limit 1, interval 1s, 2026-10-09 | https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137
OpenReview API v2 | https://api2.openreview.net | /groups anonymous OK, ratelimit-policy 20;w=60; /notes ratelimit-policy 180;w=60 but anonymous -> 403 ChallengeRequiredError | account token (MFA risk) | observed 2026-10-09 | https://api2.openreview.net/groups?id=ICLR.cc/2026/Conference
DBLP search API | https://dblp.org/search/publ/api | BLOCKED for scripts: Anubis proof-of-work page; follow-ups got TCP resets | n/a | observed 2026-10-09 | https://dblp.org/search/publ/api?q=quality%20diversity&format=json&h=2
Papers with Code API | https://paperswithcode.com/api/v1/ | DEAD: redirects to https://huggingface.co/papers/trending (sunset ~2025-07-24/25) | n/a | observed 2026-10-09 | https://paperswithcode.com/api/v1/papers/?q=evolution
ACM Digital Library | https://dl.acm.org | BLOCKED: 403 cf-mitigated challenge; use Crossref prefix 10.1145 | n/a | observed 2026-10-09 | https://dl.acm.org/conference/gecco
MIT Press Direct | https://direct.mit.edu/isal ; /artl | BLOCKED: 403 cf-mitigated challenge; use Crossref prefix 10.1162 | n/a | observed 2026-10-09 | https://direct.mit.edu/isal
alphaXiv | https://api.alphaxiv.org/mcp/v1 | 401; requires auth; no official public REST reference (UNVERIFIED) | key | observed 2026-10-09 | https://www.alphaxiv.org/
ar5iv / arXiv HTML | https://arxiv.org/html/<id> ; https://ar5iv.labs.arxiv.org/html/<id> | live 200; covered by arXiv ToU | none | observed 2026-10-09 | https://arxiv.org/html/2408.06292
Ollama library existence | https://ollama.com/library/<name> | 200 vs 404 check; no limit documented | none | checked 2026-10-09 | https://ollama.com/library/qwen3-embedding
```

### (f) Key arXiv ids from the notes

```text
# id | short label | note
# --- LLM-guided evolution / program evolution ---
2506.13131 | AlphaEvolve white paper (2025-06-16)
2511.02864 | Georgiev, Gomez-Serrano, Tao, Wagner: AlphaEvolve on 67 problems
2509.19349 | ShinkaEvolve (ICLR 2026)
2510.14150 | CodeEvolve
2511.17592 | GigaEvo
2510.06056 | DeepEvolve
2511.23473 | ThetaEvolve (ICML 2026)
2601.16175 | TTT-Discover (ICML 2026 spotlight)
2605.09764 | LEVI
2602.10233 | ImprovEvolve
2604.18607 | TurboEvolve
2602.23413 | EvoX meta-evolution | UNVERIFIED (citation only)
2604.19440 | What Makes an LLM a Good Optimizer? | UNVERIFIED (citation only)
2604.24372 | SeaEvo | title only
2602.16805 | Simple Baselines are Competitive with Code Evolution (ICLR 2026)
2605.20086 | What Do Evolutionary Coding Agents Evolve? (EvoTrace/EvoReplay)
2507.19457 | GEPA (ICLR 2026 Oral)
2507.02554 | AIRA-dojo (MLE-bench agents)
2309.08532 | EvoPrompt | background
2401.02051 | EoH | background
2402.01145 | ReEvo | background
2405.20132 | LLaMEA | background
2412.17287 | LLM4AD | background
2206.08896 | ELM (Lehman et al.) | UNVERIFIED, background
# --- Self-improving / self-modifying / autopoiesis ---
2505.22954 | Darwin Godel Machine (ICLR 2026)
2510.21614 | Huxley-Godel Machine (ICLR 2026 oral)
2603.19461 | Hyperagents
2408.08435 | ADAS | background
2602.07755 | Meta-learning agentic memory designs
2502.07577 | Automated Capability Discovery
2507.06466 | Foundation Model Self-Play (RLC 2025)
2601.04501 | Minary primitive of computational autopoiesis
2311.10761 | Autopoietic vesicles in particle system | background
# --- Program synthesis / ARC / library learning ---
2601.10904 | ARC Prize 2025 Technical Report
2505.11831 | ARC-AGI-2
2603.24621 | ARC-AGI-3
2412.04604 | ARC Prize 2024 report | background
2507.14172 | SOAR (ICML 2025)
2510.04871 | TRM: Less is More, Recursive Reasoning with Tiny Networks
2506.21734 | HRM
2512.06104 | CompressARC
2603.13372 | ARC of Progress living survey | title only
2504.03048 | LLM Library Learning Fails: LEGO-Prover case study
2510.02263 | RLAD
2510.15863 | PolySkill
2605.14477 | EvoLib
2603.23244 | Online library learning in human visual puzzle solving
2211.16605 | Stitch | background
2310.19791 | LILO | background
2401.16467 | ReGAL | background
2411.02272 | Induction + transduction for ARC | UNVERIFIED id
2509.05249 | COGITAO (ICML 2026)
# --- Theorem proving / neuro-symbolic ---
2502.03544 | AlphaGeometry2
2504.21801 | DeepSeek-Prover-V2
2504.11354 | Kimina-Prover Preview
2508.03613 | Goedel-Prover-V2 (ICLR 2026)
2507.23726 | Seed-Prover
2512.17260 | Seed Prover 1.5
2510.01346 | Aristotle (Harmonic)
2601.07421 | Erdos #728 writeup
2606.12594 | Pythagoras-Prover-32B paper | UNVERIFIED (secondary)
2606.05400 | LeanMarathon | title only
2603.19329 | Goedel-Code-Prover
# --- Automated science / falsification ---
2502.18864 | AI co-scientist
2502.09858 | POPPER (ICML 2025)
2504.08066 | AI Scientist-v2
2408.06292 | AI Scientist v1 | UNVERIFIED in evolution note; used as live probe id
2501.04227 | Agent Laboratory
2503.18102 | AgentRxiv
2505.13400 | Robin
2511.02824 | Kosmos
2503.22708 | Ai2 CodeScientist | UNVERIFIED
2604.02485 | Failing to Falsify
2604.18805 | AI scientists produce results without reasoning scientifically
2604.22080 | Sound Agentic Science Requires Adversarial Experiments
2608.07437 | Fisher-R1
2608.22948 | What Proves You Wrong (falsifiable ideation benchmark) | title only
2608.12345 | Research-integrity diagnostic for co-scientists | title only
2609.28850 | RECLAIM | title only
2609.18598 | Hypothesis-driven autonomous materials synthesis | title only
# --- Benchmarks (program/optimization/agents) ---
2410.07095 | MLE-bench | background
2506.09050 | ALE-Bench
2504.20183 | BLADE
2504.10415 | LLM-SRBench (ICML 2025 oral)
2610.02588 | Open-Endedness Bench
# --- Open-endedness theory / measurement ---
2406.04268 | Open-Endedness is Essential for ASI | background
2502.04512 | Safety Must Precede Deployment of Open-Ended AI (ICML 2026)
2505.11581 | Fractured Entangled Representation hypothesis
2605.23908 | Replicating Picbreeder with VLMs (GECCO 2026)
2606.08369 | Information-theoretic definition of open-ended learning
2607.09560 | Vocabulary and Verifier Gaps in Open-Ended AI
2603.01701 | ToLSim speciation simulation, OEE tests
2606.17091 | Multi-Scale Path Divergence (MSPD)
2603.16910 | TerraLingua
2604.19761 | EvoForest
2601.03335 | Digital Red Queen
2604.01658 | CORAL
2606.13710 | HOTE | snippet, not API-checked
2105.03216 | OEE measurement review | background
# --- Computational life / soups ---
2406.19108 | Computational Life (BFF) | background
2607.01483 | BFF: Simple explanations for complex phenomena
2607.09211 | Coevolution of self-replication and function (Z80 soup)
# --- ALife substrates / NCA / Lenia ---
2412.17799 | ASAL
2509.22447 | Guiding ALife evolution with VLMs (ALIFE 2025)
2604.11248 | PBT-NCA
2505.13058 | Path to Universal NCA
2609.36126 | Reasoning with NCA
2402.10236 | Sensorimotor agency in CA (Science Advances 2025-10-31)
2607.27402 | Continuous Game of Life
2609.01348 | Collision-based logic in Lenia
2605.30708 | Agnosiophobia in Lenia
2604.01932 | BraiNCA
2406.04235 | Leniabreeder | background
2212.07906 | Flow-Lenia | background
2410.02651 | CAX
2506.15746 | NCA for ARC-AGI (ALIFE 2025)
2505.08778 | ARC-NCA
2506.04912 | Differentiable Logic Cellular Automata
2603.10055 | Training LMs via NCA
# --- Evolvability / Levin lab ---
2605.30109 | Training Ecosystems
2605.06746 | Causally Emergent Alignment Hypothesis
2605.16321 | Language Game (Levin lab)
2604.08749 | A Little Rank Goes a Long Way | snippet
2401.05375 | Sorting algorithms as morphogenesis | background
# --- Quality-Diversity ---
2502.00593 | Dominated Novelty Search
2504.08057 | Vector Quantized-Elites
2504.03715 | Multi-Objective QD in unstructured spaces
2602.00478 | QD as Multi-Objective Optimization
2604.14969 | Task-Capability Coevolution (ICLR 2026)
2410.14735 | CycleQD | background
2605.27130 | DEI: Diversity in Evolutionary Inference
2607.22375 | IDEAgent | snippet, not API-checked
2308.03665 | QDax | background
2303.00191 | pyribs | background
2212.04180 | evosax | background
2302.12600 | EvoTorch | background
2301.12457 | EvoX library | background
# --- Environment generation / UED ---
2405.15568 | OMNI-EPIC
2410.23208 | Kinetix
2505.20659 | Optimisation framework for UED (NCC)
2506.19997 | TRACED (ICLR 2026)
2511.12706 | UED for task-level pairs (AAAI 2026)
2602.09813 | Efficient UED via hierarchical policy representation
2605.01358 | PACE
2512.19682 | GenEnv
2605.09423 | SimWorld Studio
2609.04128 | Environment Evolution for Terminal Agents
2608.10299 | Co-Evolution in Agentic Systems (survey)
2406.04663 | LLM-POET | background
2402.16801 | Craftax | background
2312.12044 | XLand-MiniGrid | background
2403.13091 | JaxUED | background
2409.00853 | JaxLife | background
2311.12716 | minimax | background
# --- World models ---
2506.09985 | V-JEPA 2
2603.14482 | V-JEPA 2.1
2512.10942 | VL-JEPA
2511.08544 | LeJEPA
2512.24497 | What drives success in JEPA world-model planning
2603.19312 | LeWorldModel
2605.26379 | When Does LeJEPA Learn a World Model?
2512.04797 | SIMA 2
2511.00062 | Cosmos-Predict2.5 / Transfer2.5
2508.13009 | Matrix-Game 2.0
2604.08995 | Matrix-Game 3.0
2301.04104 | DreamerV3 preprint | background
2509.24527 | Dreamer 4
2507.03298 | Dyn-O
# --- Latent / recursive / energy-based reasoning ---
2605.20613 | HRM-Text | UNVERIFIED (secondary link only)
2605.19943 | Probabilistic TRM
2602.12078 | Tiny recursive reasoning with Mamba-2 hybrid
2608.24136 | Steering recurrent reasoners with readout feedback
2607.16051 | Loop the Loopies! (catalogue)
2505.05522 | Continuous Thought Machines
2502.05171 | Huginn recurrent-depth LM
2510.25741 | Ouro looped LMs
2412.06769 | Coconut | background
2512.21711 | Do Latent Tokens Think?
2507.06203 | Survey on latent reasoning
2505.16782 | Latent CoT survey
2507.02092 | Energy-Based Transformers (ICLR 2026 oral)
2504.10449 | M1 Mamba reasoning (NeurIPS 2025)
# --- Active inference / Thousand Brains / neurosymbolic ---
2505.24784 | AXIOM
2407.20292 | Scale-free active inference (RGMs) | background
2608.09512 | RGMs for active inference: verified implementation
2603.20927 | Active inference for physical AI agents
2307.14145 | RxInfer reference | background
2412.18354 | Thousand Brains Project white paper | background
2507.04494 | Thousand-Brains Systems (Monty)
2310.18318 | OpenCog Hyperon framework | background
2510.09355 | NL2GenSym (LLM + Soar)
2512.24113 | CogRec
2506.07807 | Common Model of Cognition + metacognition
# --- Efficient / spiking ---
2511.23404 | LFM2 Technical Report
2509.05276 | SpikingBrain
# --- Physical reasoning benchmarks ---
2506.09849 | IntPhys 2
2506.09943 | CausalVQA
2501.09038 | Physics-IQ
2606.18943 | Physics-IQ Verified
```
