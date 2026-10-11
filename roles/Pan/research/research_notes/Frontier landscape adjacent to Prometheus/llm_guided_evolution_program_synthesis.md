# LLM-guided evolutionary search, program synthesis/induction, neuro-symbolic & automated-science/falsification agents: frontier 2025 to Oct 2026

Compiled 2026-10-09. Scope: LLM-as-mutation-operator program evolution, library learning / program induction / ARC, open neuro-symbolic theorem proving, and automated-science / hypothesis-falsification agents. Out of scope (other researchers): general open-endedness/ALife/QD, world models/cognitive architectures, general local-LLM lists.

Conventions used below:
- [BG] = background (pre-2025), included only as lineage/baseline.
- UNVERIFIED = seen only in a secondary/aggregator source, or an identifier recalled but not confirmed this session.
- "Date" = first arXiv submission unless stated otherwise; later revisions noted where seen.
- Licenses are only stated where a primary page (repo or official listing) was seen; otherwise marked UNVERIFIED.

---

## Q1. What are the most important works (2025 to Oct 2026) in each sub-field, with authors/org, date, ID, contribution, code and license?

### Takeaway
The field consolidated around one loop: an LLM proposes program/code edits, an automated evaluator scores them, and an archive/islands/MAP-Elites database selects parents (AlphaEvolve, 2025-06; GA on Google Cloud 2026-07-09). The open ecosystem (OpenEvolve, ShinkaEvolve, CodeEvolve, GigaEvo, LEVI) now reproduces AlphaEvolve-class results on headline problems, and 2025-26 added test-time RL inside the loop (ThetaEvolve, TTT-Discover). Two 2026 papers show that simple baselines often match these pipelines and that headline scores hide what was actually evolved; any Prometheus comparison needs a null arm. On ARC, the 2025 theme was the "refinement loop" (per-task iterative program/model optimization under a feedback signal). ARC-AGI-3 (interactive, launched 2026-03-25) is the live frontier. Lean provers saturated miniF2F and moved to PutnamBench and Erdős problems. The automated-science line is now judged by whether its agents actually falsify, and 2026 audits say mostly they do not.

### Cited Findings

#### A. LLM-guided evolution of programs / algorithms (core loop, frameworks, critiques)

- **AlphaEvolve: A coding agent for scientific and algorithmic discovery.** Novikov, Vũ, Eisenberger et al. (18 authors incl. Kohli, Balog), Google DeepMind. arXiv **2506.13131**, submitted **2025-06-16** (white paper; the blog launch was May 2025). An LLM proposes direct code edits and evaluators score them inside an evolutionary loop; the successor to FunSearch, which only evolved single small Python functions. Reported 4x4 complex matrix multiplication with 48 scalar multiplications (vs Strassen's 49), plus deployed Google infrastructure gains. Code: none (closed). — [arXiv](https://arxiv.org/abs/2506.13131.pdf); [summary](https://notesbylex.com/alphaevolve-a-coding-agent-for-scientific-and-algorithmic-discovery)
- **AlphaEvolve commercial availability.** Academic Early Access from May 2025, enterprise private preview from **2025-12-09**, and **general availability to all Google Cloud customers on 2026-07-09** ("Gemini Enterprise Agent Platform"). The user supplies a baseline program plus a scoring function and runs candidates in their own evaluation environment. Reported internal results include TPU circuit layout, Spanner compaction heuristics (-20% write amplification), ~9% storage reduction via compiler optimizations, and quantum circuits with 10x lower error on Willow. Customer claims include BASF, Klarna and Schrödinger; these are vendor figures. — [Google blog](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/); [Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone); [ITBrief](https://itbrief.com.au/story/google-cloud-makes-alphaevolve-generally-available); codelab/example repo `Google-Cloud-AI/alphaevolve-on-googlecloud` named only by a third-party tutorial (UNVERIFIED) — [codelab](https://codelabs.developers.google.com/alphaevolve-on-google-cloud-1)
- **Mathematical exploration and discovery at scale.** Georgiev, Gómez-Serrano, **Tao**, Wagner. arXiv **2511.02864**, v1 **2025-11-03**, v3 2025-12-22 (81 pp). AlphaEvolve was applied to **67 problems** in analysis, combinatorics, geometry and number theory. It rediscovered the best-known solutions in most cases and improved several. It did not match prior results in all cases, and some improvements "could likely also have been matched by more traditional" methods. For Sidorenko, Sendov and Crouzeix it generally relocated the known candidates. Prompts and outputs are on GitHub under google-deepmind (the exact repo name was truncated in the source, UNVERIFIED). — [arXiv abs](https://arxiv.org/abs/2511.02864); [search/Tao blog summary](https://tagteam.harvard.edu/hub_feeds/3899/feed_items/16691196)
- **ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution.** Robert Tjarko Lange, Yuki Imajuku, Edoardo Cetin (Sakana AI). arXiv **2509.19349** (Sept 2025), accepted **ICLR 2026** (Jan 2026). Its mechanisms are adaptive parent sampling, novelty rejection sampling (embeddings plus LLM-as-judge), and bandit (UCB) selection over an LLM ensemble. It reported a new 26-circle packing result with about 150 samples, and was also run on AIME scaffold design, ALE-Bench, and an MoE load-balancing loss. It helped Team Unagi win ICFP Contest 2025 (Oct 2025). **Code: github.com/SakanaAI/ShinkaEvolve, Apache-2.0**; on PyPI as `shinka-evolve` (Mar 2026). Updates: agent skills for Claude Code/Codex (Feb 2026), unified runner (Mar 2026), docs site (Apr 2026), headless CLI-backed mutation models (May 2026). — [arXiv](https://arxiv.org/pdf/2509.19349); [GitHub](https://github.com/SakanaAI/ShinkaEvolve); [Sakana blog](https://sakana.ai/shinka-evolve/)
- **OpenEvolve.** Asankhaya Sharma (codelion), now hosted under the `algorithmicsuperintelligence` GitHub org; first released 2025 (post-May 2025). An open reimplementation of AlphaEvolve with MAP-Elites grid, island populations with migration, cascade evaluation, artifact feedback to the LLM, LLM ensembles with fallback, and seeded reproducibility (default seed 42). It evolves whole files. Its circle packing n=26 run "matches published benchmarks" (self-claim). **License Apache-2.0**; ~7.5k stars at time of fetch. — [GitHub](https://github.com/algorithmicsuperintelligence/openevolve); [HF blog](https://huggingface.co/blog/codelion/openevolve)
- **CodeEvolve: an open source evolutionary coding agent for algorithmic discovery and optimization.** arXiv **2510.14150** (Oct 2025; v4 ~Mar 2026). An islands GA with modular LLM orchestration, evaluated on the AlphaEvolve benchmarks; the authors claim open-weight models often match or exceed closed baselines at lower cost. Code: github.com/inter-co/science-codeevolve (license UNVERIFIED). — [arXiv](https://arxiv.org/pdf/2510.14150); [alphaXiv](https://www.alphaxiv.org/abs/2510.14150v4)
- **GigaEvo: An Open Source Optimization Framework Powered by LLMs and Evolution Algorithms.** AIRI / Sber. arXiv **2511.17592**, **2025-11-17**. It combines MAP-Elites, asynchronous DAG-based evaluation pipelines, LLM mutation with "insight generation" and bidirectional lineage tracking, and multi-island strategies. Reproducibility was checked on Heilbronn triangles, circle packing and kissing numbers. The repo link differs between versions: AIRI-Institute/gigaevo-core vs FusionBrainLab/gigaevo-core (UNVERIFIED which is current). — [arXiv](https://arxiv.org/abs/2511.17592v1)
- **DeepEvolve: Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research.** Gang Liu, Yihan Zhu, Jie Chen, Meng Jiang (Notre Dame / IBM). arXiv **2510.06056** (Oct 2025). Adds external retrieval ("deep research"), cross-file editing and debugging to the evolve loop, arguing that pure evolution "quickly plateaus." Tested on 9 benchmarks (chemistry, math, biology, materials, patents). Code: github.com/liugangcode/deepevolve (license UNVERIFIED). — [arXiv](https://arxiv.org/html/2510.06056v1)
- **ThetaEvolve: Test-time Learning on Open Problems.** Yiping Wang et al. (UW, Microsoft). arXiv **2511.23473**, **2025-11-28**; **ICML 2026**. A single LLM with a large program database, plus in-context learning **and test-time RL**, batch sampling, and lazy penalties. It claims the first small open model (DeepSeek-R1-0528-Qwen3-8B) to reach new best-known bounds (circle packing, first autocorrelation inequality). The authors say code is released (repo URL not captured; UNVERIFIED). — [arXiv](https://arxiv.org/abs/2511.23473v1); [ICML](https://icml.cc/virtual/2026/poster/63428)
- **Learning to Discover at Test Time (TTT-Discover).** Mert Yuksekgonul, Daniel Koceja et al. arXiv **2601.16175** (Jan 2026); **ICML 2026 spotlight**. Runs RL on the single test problem, aiming for one great solution rather than good average performance. Reports SOTA on Erdős minimum overlap, an autocorrelation inequality, a GPUMode kernel (up to 2x), past AtCoder contests, and single-cell denoising. Uses open **gpt-oss-120b** via Thinking Machines' **Tinker** API, at "a few hundred dollars per problem," with public code. Claims gains over ThetaEvolve at equal model and compute. — [arXiv](https://arxiv.org/abs/2601.16175v1); [ICML](https://icml.cc/virtual/2026/spotlight/84891)
- **LEVI: Stronger Search Architectures Can Substitute for Larger LLMs in Evolutionary Search.** arXiv **2605.09764**, **2026-05-10**. Components: a diversity-preserving database, a mutation router splitting work between large and small LLMs, and a rank-preserving proxy benchmark. Code: github.com/ttanv/levi (license UNVERIFIED). — [arXiv](https://arxiv.org/abs/2605.09764)
- **ImprovEvolve: Basin-Hopping Meets LLM-Guided Evolutionary Search.** arXiv **2602.10233** (Feb 2026); applied to AlphaEvolve-style math constructions. Code not confirmed. — [arXiv](https://arxiv.org/abs/2602.10233)
- **TurboEvolve: Towards Fast and Robust LLM-Driven Program Evolution.** arXiv **2604.18607** (Apr 2026). Compares against ShinkaEvolve and CodeEvolve, and cites TTT-Discover, ThetaEvolve and LoongFlow (planner-executor-memory). — [arXiv](https://arxiv.org/pdf/2604.18607)
- **EvoX (meta-evolution for automated discovery)** arXiv 2602.23413 and **"What Makes an LLM a Good Optimizer?"** arXiv 2604.19440: seen only as citations (UNVERIFIED). **SeaEvo: Advancing Algorithm Discovery with Strategy Space Evolution**, arXiv 2604.24372: title only. — [search listing](https://arxiv.org/pdf/2604.24372)
- **Simple Baselines are Competitive with Code Evolution.** Yonatan Gideoni, Sebastian Risi, Yarin Gal. arXiv **2602.16805**, **2026-02-18**; ICLR 2026. Across math bounds, agentic-scaffold design and ML competitions, simple baselines **match or exceed** sophisticated code-evolution pipelines. For bounds, the search space and domain knowledge in the prompt set the ceiling, and the evolution pipeline is "secondary." — [arXiv](https://www.arxiv.org/abs/2602.16805); [ICLR](https://www.iclr.cc/virtual/2026/10018694)
- **What Do Evolutionary Coding Agents Evolve?** Nico Pelleriti et al. (ZIB / TU Berlin / HKBU / RIKEN). arXiv **2605.20086**, **2026-05-19**. Releases **EvoTrace**, a dataset of search traces (programs, lineage, diffs, prompts, generator models, evaluator outputs, replay environments) across **4 frameworks x 16 tasks**, plus **EvoReplay** for controlled interventions. It argues that a single best score conflates new structure, re-tuning, recombination of known ideas, and evaluator overfitting. Reported finding: post-hoc hyperparameter tuning often recaptures late-stage gains (secondary summary). Its related work lists OpenEvolve, GEPA, ShinkaEvolve, GigaEvo, CodeEvolve, FM Agent and AIDE. — [arXiv html](https://arxiv.org/html/2605.20086v1); [EmergentMind](https://www.emergentmind.com/papers/2605.20086)
- **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning.** Lakshya A. Agrawal + 16 (Berkeley, Stanford, et al.). arXiv **2507.19457**, v1 Jul 2025, v2 Feb 2026; **ICLR 2026 Oral**. Genetic-Pareto prompt evolution with natural-language reflection and a per-instance Pareto front. v2 reports +6% average over GRPO (v1 said +10%), up to 35x fewer rollouts, and >10% over MIPROv2. Code: github.com/gepa-ai/gepa (used in ARC 2025 entries; license UNVERIFIED). — [arXiv](https://arxiv.org/abs/2507.19457); [ARC 2025 tech report](https://arxiv.org/html/2601.10904)
- **Darwin Gödel Machine (DGM): Open-Ended Evolution of Self-Improving Agents.** Jenny Zhang, Shengran Hu, Cong Lu, Robert Lange, Jeff Clune (UBC / Sakana). arXiv **2505.22954**, v1 **2025-05-29**, v2 2025-09-26; **ICLR 2026**. The agent edits its own code repository, with each change validated empirically on benchmarks, and keeps an archive/tree of agents for open-ended parent selection. SWE-bench rose from 20.0% to 50.0% and Polyglot from 14.2% to 30.7% with frozen FMs. Code: github.com/jennyzzt/dgm (license UNVERIFIED). — [arXiv](https://arxiv.org/html/2505.22954v2); [SourcePulse](https://www.sourcepulse.org/projects/3752776)
- **Huxley-Gödel Machine (HGM).** KAUST (incl. Schmidhuber). arXiv **2510.21614**, 2025-10-24 (v2 10-28); ICLR 2026. Introduces CMP, which scores an agent by its descendants' benchmark performance as a proxy for self-improvement potential. Beats DGM-style methods on SWE-bench Verified and Polyglot with fewer CPU-hours. Code: github.com/metauto-ai/HGM. — [arXiv](https://arxiv.org/pdf/2510.21614v2); [ICLR](https://iclr.cc/virtual/2026/poster/10009359)
- **AI Research Agents for Machine Learning: Search, Exploration, and Generalization in MLE-bench (AIRA-dojo).** Meta FAIR / UCL / Örebro. arXiv **2507.02554** (Jul 2025). Separates search policy from code-modification operators and finds **operator quality is the primary bottleneck**. MLE-bench Lite medal rate 47.7% (v1), rising to 55% after rerun (v2). Also reports a validation/test generalization gap that leads to overfitting. Code: Meta `aira-dojo` repo. — [arXiv v2](https://arxiv.org/html/2507.02554v2)
- [BG] **FunSearch.** Romera-Paredes et al., "Mathematical discoveries from program search with large language models," *Nature*, Dec 2023. Code: github.com/google-deepmind/funsearch, **Apache-2.0 (code) / CC-BY-4.0 (other materials)**; not actively maintained. — [Wikipedia](https://en.wikipedia.org/wiki/FunSearch)
- [BG] **OpenELM** (CarperAI). A replication of "Evolution Through Large Models" with MAP-Elites, CVT-MAP-Elites, Deep Grid MAP-Elites and a GA baseline. `pip install openelm`, **MIT**. Not Apple's OpenELM LM. — [GitHub](https://github.com/CarperAI/OpenELM)
- [BG] **EvoPrompt.** Qingyan Guo et al. (Tsinghua / MSR / Northeastern). arXiv **2309.08532**, v1 2023-09-15, v3 **2025-05-01** (31 datasets incl. BBH). Code: github.com/beeevita/EvoPrompt. — [arXiv](https://arxiv.org/abs/2309.08532v3)
- [BG] **EoH (Evolution of Heuristics)**, Liu et al., ICML 2024, arXiv 2401.02051, code github.com/FeiLiu36/EoH. **ReEvo**, Ye et al., NeurIPS 2024, arXiv 2402.01145, code github.com/ai4co/LLM-as-HH ("reflections as verbal gradients"). **LLaMEA**, arXiv 2405.20132, (1+1) LLM-EA for metaheuristics, PyPI `llamea`. **LLM4AD platform**, CityU HK / SUSTech, arXiv 2412.17287, code github.com/Optima-CityU/LLM4AD (bundles EoH, FunSearch, hill climbing, adapted LLaMEA; local or remote LLM; v1.0.0 2024-11-05). — [EoH](https://arxiv.org/abs/2401.02051v3); [ReEvo](https://arxiv.org/abs/2402.01145v3); [LLaMEA](https://arxiv.org/pdf/2405.20132); [LLM4AD](https://arxiv.org/abs/2412.17287); [LLM4AD docs](https://llm4ad-doc.readthedocs.io)

#### B. Program synthesis / induction, library learning, ARC-AGI methods

- **ARC Prize 2025: Technical Report.** Chollet, Knoop, Kamradt, Landers (ARC Prize Foundation). arXiv **2601.10904**, **2026-01-15**. The competition ran 2025-03-26 to 2025-11-03: 1,455 teams, 15,154 entries, 90 papers (47 in 2024). Top private ARC-AGI-2 score was 24% at $0.20/task, and the Grand Prize (85%) went unclaimed. The defining 2025 theme is the **"refinement loop: a per-task iterative program optimization loop guided by a feedback signal."** — [arXiv html](https://arxiv.org/html/2601.10904); [ARC Prize 2025 archive](https://arcprize.org/competitions/2025/archive)
  - Kaggle (ARC-AGI-2 private):
    - 1st **NVARC**, 24.03%. Ivan Sorokin & Jean-François Puget (NVIDIA KGMoN). Builds on the 2024 ARChitects TTT entry with heavy synthetic data and a fine-tuned ~4B model. A post-competition 29.72% is UNVERIFIED.
    - 2nd **the ARChitects**, 16.53%. 2D-aware masked-diffusion LM with recursive self-refinement and perspective-based scoring.
    - 3rd **MindsAI**, 12.64%. Test-time fine-tuning, augmentation ensembles, tokenizer dropout.
    - 4th Lonnie, 6.67%; 5th G. Barbadillo, 6.53%.
    - Sources: [tech report](https://arxiv.org/html/2601.10904); [ARC Prize 2025](https://arcprize.org/competitions/2025); [bdtechtalks](https://bdtechtalks.com/2025/12/09/poetiq-arc-agi-2-solution/)
  - Paper awards:
    - 1st: **TRM**, Jolicoeur-Martineau.
    - 2nd: **SOAR**, Pourcel, Colas, Oudeyer.
    - 3rd: **"ARC-AGI Without Pretraining" (CompressARC)**, I. Liao & A. Gu.
    - Runners-up: VSA for ARC (Joffe & Eliasmith; github.com/ijoffe/ARC-VSA-2025); Berman, "From Parrots to Von Neumanns: evolutionary test-time compute" (github.com/jerber/arc-lang-public; evolves NL programs); E. Pang, "Efficient Evolutionary Program Synthesis" (Python plus a dynamically built abstraction library); ARC-NCA (Guichard et al.).
    - Other open writeups: [ARChitects](https://lambdalabsml.github.io/ARC2025_Solution_by_the_ARChitects/), [Barbadillo](https://ironbar.github.io/arc25/05_Solution_Summary/), [Pang](https://open.substack.com/pub/ctpang/p/arc-agi-2-sota-efficient-evolutionary), CoreThink neuro-symbolic (github.com/CoreThink-AI/Research-publications). — [tech report](https://arxiv.org/html/2601.10904)
  - Frontier/commercial: the **Poetiq** harness on Gemini 3 Pro went from 31% at $0.81/task to **54% at ~$30-31/task** on ARC-AGI-2 semi-private. Its loop is generate > critique > refine > verify over off-the-shelf models with no retraining. Claude Opus 4.5 with the same approach reportedly rivals it at ~$60/task. Code: github.com/poetiq-ai/poetiq-arc-agi-solver (MIT per a mirror; README states none; UNVERIFIED). — [tech report](https://arxiv.org/html/2601.10904); [bdtechtalks](https://bdtechtalks.com/2025/12/09/poetiq-arc-agi-2-solution/); [SourcePulse](https://www.sourcepulse.org/projects/20182084)
- **Self-Improving Language Models for Evolutionary Program Synthesis: A Case Study on ARC-AGI (SOAR).** Julien Pourcel, Cédric Colas, Pierre-Yves Oudeyer (Inria Flowers). arXiv **2507.14172**, v1 **2025-07-10**, v2 2026-03-16; **ICML 2025** (PMLR 267). An LLM drives evolutionary search (sample + refine), then **hindsight learning** turns search traces into training pairs that fine-tune the same LLM, in an iterative loop. Solves 52% of the ARC-AGI-1 public test with test-time adaptation. Code: github.com/flowersteam/SOAR. Models: HF `julien31/Soar-qwen-7b`, `Soar-qwen-32b`, `Soar-mistral-123b`. Paper CC BY 4.0; code license UNVERIFIED. — [arXiv](https://arxiv.org/abs/2507.14172v1); [PMLR](https://proceedings.mlr.press/v267/pourcel25a.html); [HF](https://huggingface.co/julien31/Soar-qwen-7b)
- **Less is More: Recursive Reasoning with Tiny Networks (TRM).** Alexia Jolicoeur-Martineau (Samsung SAIL Montréal). arXiv **2510.04871** (Oct 2025). A single 2-layer, **~5-7M-parameter** recursive network. ARC-AGI-1 rises from 40% to 45%, ARC-AGI-2 from 5% to 8%, Sudoku-Extreme from 55% to 87%, Maze-Hard from 75% to 85%, versus the 27M HRM. Code: github.com/SamsungSAILMontreal/TinyRecursiveModels, archived/read-only per README. — [arXiv](https://arxiv.org/pdf/2510.04871); [README](https://cdn.jsdelivr.net/gh/samsungsailmontreal/tinyrecursivemodels@main/README.md)
- **HRM (Hierarchical Reasoning Model)**, arXiv **2506.21734** (Jun 2025): TRM's predecessor. — [cited in tech report](https://arxiv.org/html/2601.10904)
- **The ARC of Progress towards AGI: A Living Survey of Abstraction and Reasoning**, arXiv **2603.13372** (Mar 2026). Title only seen. — [arXiv](https://arxiv.org/pdf/2603.13372)
- Library learning, 2025-26:
  - **"LLM Library Learning Fails: A LEGO-Prover Case Study"**, arXiv **2504.03048** (Apr 2025): a negative result on LLM library learning (abstract not retrieved). — [arXiv](https://arxiv.org/pdf/2504.03048)
  - **RLAD: Training LLMs to Discover Abstractions for Solving Reasoning Problems**, arXiv **2510.02263** (Oct 2025): RL with two players, an abstraction generator and a solver. — [arXiv](https://arxiv.org/html/2510.02263v1)
  - **PolySkill**, arXiv **2510.15863** (Oct 2025): polymorphic skill abstraction for web agents. — [arXiv](https://arxiv.org/html/2510.15863v1)
  - **EvoLib: Test-Time Learning with an Evolving Library**, arXiv **2605.14477** (May 2026): black-box LLMs induce, reuse and consolidate abstractions in an evolving library at test time. — [arXiv](https://arxiv.org/html/2605.14477v1)
  - **Online library learning in human visual puzzle solving**, arXiv **2603.23244** (Mar 2026): cognitive-science framing, where libraries bias future search. — [arXiv](https://arxiv.org/pdf/2603.23244)
- [BG] **DreamCoder**: Ellis et al., PLDI 2021; wake-sleep library learning plus neural search policy. — [PLDI](https://pldi21.sigplan.org/details/pldi-2021-papers/55/DreamCoder-Bootstrapping-Inductive-Program-Synthesis-with-Wake-Sleep-Library-Learnin)
- [BG] **Stitch**: Bowers et al., "Top-Down Synthesis for Library Learning," arXiv 2211.16605 (POPL 2023). Reported 3-4 orders of magnitude faster and 2 orders less memory than DreamCoder's compressor. Rust code at github.com/mlb2251/stitch. — [arXiv](https://arxiv.org/pdf/2211.16605)
- [BG] **LILO**: Grand, Wong, Bowers, Olausson, Liu, Tenenbaum, Andreas, ICLR 2024, arXiv 2310.19791. LLM-guided synthesis plus Stitch compression plus LLM auto-documentation. — [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/819cebb05f993840e8a52d7564c5c282-Abstract-Conference.html)
- [BG] **ReGAL**, arXiv 2401.16467: refactoring to discover generalizable abstractions. — [arXiv](https://arxiv.org/pdf/2401.16467)
- [BG/2025] **Combining Induction and Transduction for Abstract Reasoning**: Wen-Ding Li, Keya Hu, ..., Kevin Ellis (Cornell); ICLR 2025; ARC Prize 2024 paper award 1st. Induction (program synthesis) and transduction (direct prediction) solve different ARC tasks, and ensembling helps. — [Ellis alphaXiv](https://www.alphaxiv.org/@kevin-ellis); [ARC Prize 2024 report](https://arxiv.org/pdf/2412.04604)

#### C. Neuro-symbolic reasoning & open automated theorem proving

- **AlphaGeometry2: Gold-medalist Performance in Solving Olympiad Geometry.** Google DeepMind. arXiv **2502.03544**, v1 **2025-02-05**, v3 2025-12-08. Extended language (moving objects, linear equations of angles/ratios/distances). IMO 2000-2024 coverage rose from 66% to 88%, and the solve rate from 54% to 84%. — [arXiv](https://arxiv.org/abs/2502.03544)
- **AlphaProof: "Olympiad-level formal mathematical reasoning with reinforcement learning."** Hubert, Mehta, Sartran et al. (GDM), *Nature*, **Nov 2025**, DOI 10.1038/s41586-025-09833-y. AlphaZero-style RL in Lean, trained on ~80M auto-formalized statements. IMO 2024 silver (with AlphaGeometry). No open weights seen. — [Nature Asia press release](https://www.natureasia.com/en/info/press-releases/detail/9147)
- **DeepSeek-Prover-V2.** DeepSeek. arXiv **2504.21801**, **2025-04-30** (v2 2025-07-18). Lean 4, RL for subgoal decomposition. The 671B model reaches **88.9% miniF2F-test** and **49/658 PutnamBench**; a 7B variant also exists. License: code MIT plus DeepSeek Model License for weights per aggregator (UNVERIFIED). — [arXiv](https://arxiv.org/abs/2504.21801v1)
- **Kimina-Prover Preview.** Numina + Kimi (Moonshot). arXiv **2504.11354**, **2025-04-15**. RL from Qwen2.5-72B; 80.7% miniF2F at pass@8192. Distilled **1.5B and 7B** released at github.com/MoonshotAI/Kimina-Prover-Preview; model license UNVERIFIED. Later 8B/70B variants reach 84.0% @32 and 87.7% @1024 per the Goedel-V2 comparison. — [arXiv](https://arxiv.org/abs/2504.11354v1); [Goedel-V2 paper](https://arxiv.org/pdf/2508.03613)
- **Goedel-Prover-V2.** Goedel-LM team (HF org `Goedel-LM`; the Princeton affiliation is from prior knowledge and the author list was not captured, so UNVERIFIED). arXiv **2508.03613** (Aug 2025); **ICLR 2026**. Uses scaffolded data synthesis, Lean-compiler-guided self-correction and checkpoint averaging. The 32B model gets 88.1% miniF2F @32 (90.4% with self-correction); the **8B gets 84.6% @32, beating DeepSeek-Prover-V2-671B**. PutnamBench: 86 solved @184 (paper) vs 64 @64 (model card), a discrepancy to reconcile. Weights on HF `Goedel-LM/Goedel-Prover-V2-8B` / `-32B`. — [arXiv](https://arxiv.org/pdf/2508.03613); [HF](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B); [ICLR](https://proceedings.iclr.cc/paper_files/paper/2026/hash/13e8be77982beb73d7ed0bbf122f9f3c-Abstract-Conference.html)
- **Seed-Prover: Deep and Broad Reasoning for Automated Theorem Proving.** ByteDance Seed. arXiv **2507.23726**, **2025-07-31**. Lemma-style whole-proof reasoning refined with Lean feedback, plus Seed-Geometry. Proves 78.1% of formalized past IMO problems, saturates miniF2F, and exceeds 50% on PutnamBench. IMO 2025 count conflicts: the paper says 5/6, while the ByteDance blog says 4/6 plus a partial (official silver). **Seed Prover 1.5**, arXiv **2512.17260** (Dec 2025), produced Lean proofs for IMO 2025 P1-P5 in 16.5 h. Closed weights (as far as seen). — [alphaXiv](https://www.alphaxiv.org/abs/2507.23726v2); [Seed blog](https://seed.bytedance.com/en/blog/seed-prover-1-5-advanced-mathematical-reasoning-through-a-novel-agentic-architecture)
- **Aristotle: IMO-level Automated Theorem Proving.** Harmonic. arXiv **2510.01346**, **2025-10-01** (v2 10-10). Lean proof search combined with informal lemma generation and formalization and a geometry solver; formally verified 5/6 IMO 2025. Product/API, not open weights. — [alphaXiv](https://alphaxiv.org/abs/2510.01346v1)
- **Erdős problems, 2026.** Erdős #728 was resolved via a GPT-5.2 Pro informal argument formalized by Aristotle in Lean (Jan 4-6, 2026), with a writeup at arXiv **2601.07421**, described as the first Erdős problem regarded as fully resolved autonomously by AI. #397 was disproved via GPT-5.2 plus Aristotle (secondary). Epoch AI's **FrontierMath: Erdős** benchmark has 68 open Erdős problems formalized in Lean (Aug 2026), and Epoch estimates 3-5 problems "of this caliber" solved by AI as of Aug 2026. — [arXiv 2601.07421](https://arxiv.org/pdf/2601.07421); [Epoch](https://epoch.ai/latest/announcing-frontiermath-erdos); [The Neuron](https://www.theneuron.ai/explainer-articles/from-erdos-to-axiom-the-open-problems-ai-has-actually-solved/)
- **Pythagoras-Prover-32B**: 93.0% miniF2F-test and 93/672 PutnamBench (June 2026 paper, UNVERIFIED secondary). — [papers.cool](https://papers.cool/arxiv/2606.12594). **LeanMarathon** (long-horizon Lean autoformalization), arXiv **2606.05400**: title only. — [arXiv](https://arxiv.org/pdf/2606.05400)
- Neuro-symbolic ARC entries in 2025: Vector Symbolic Algebras (Joffe & Eliasmith) and CoreThink (Das et al.). — [ARC 2025 tech report](https://arxiv.org/html/2601.10904)

#### D. Automated scientific discovery & hypothesis-falsification agents

- **Towards an AI co-scientist.** Juraj Gottweis, Vivek Natarajan et al. (Google). arXiv **2502.18864** (Feb 2025). Gemini 2.0 multi-agent system with a **generate-debate-evolve** loop: generation, reflection, evolution and ranking (Elo tournament) agents, scaling with test-time compute. Applied to drug repurposing, target discovery and AMR mechanisms. Limited-access program, no code. — [arXiv](https://export.arxiv.org/pdf/2502.18864); [DeepLearning.AI](https://www.deeplearning.ai/the-batch/ai-co-scientist-an-agent-that-generates-research-hypotheses-aiding-drug-discovery)
- **POPPER: Automated Hypothesis Validation with Agentic Sequential Falsifications.** Kexin Huang, Ying Jin, Ryan Li, Michael Li, **Emmanuel Candès**, **Jure Leskovec** (Stanford). arXiv **2502.09858** (Feb 2025); **ICML 2025**. LLM agents design and execute **falsification experiments** on a hypothesis's measurable implications, inside a **sequential testing framework with strict Type-I error control**. Covers 6 domains (biology, economics, sociology...), comparable to human scientists at about 10x less time. Code: github.com/snap-stanford/POPPER (last push ~2025-05-14 per aggregator; license UNVERIFIED). — [arXiv](https://arxiv.org/abs/2502.09858); [PMLR](https://proceedings.mlr.press/v267/huang25n.html); [gittrend](https://gittrend.io/repo/snap-stanford/POPPER)
- **The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search.** Yamada, Lange, Lu et al. (Sakana / UBC / Oxford). arXiv **2504.08066**, **2025-04-10**. Drops human code templates in favor of progressive agentic tree search run by an experiment-manager agent. 1 of 3 fully autonomous papers exceeded the average acceptance threshold at an ICLR 2025 workshop (score 6.33; withdrawn by prior agreement). **Nature paper describing The AI Scientist published 2026-03-26** (open access). License reportedly changed in **Dec 2025** to a custom "AI Scientist Source Code License" (Responsible-AI derivative; UNVERIFIED, so check LICENSE). Code: github.com/SakanaAI/AI-Scientist-v2 (v1: SakanaAI/AI-Scientist). — [arXiv](https://arxiv.org/abs/2504.08066v1); [Nature coverage](https://noqta.tn/en/news/sakana-ai-scientist-nature-automated-research-2026); [license note](https://rywalker.com/research/ai-scientist)
- **Agent Laboratory: Using LLM Agents as Research Assistants.** Samuel Schmidgall et al. (AMD / JHU). arXiv **2501.04227**, 2025-01-08 (v2 2025-06-17). Literature review, then experimentation, then report, with optional human feedback at each stage; reports an 84% cost reduction vs prior autonomous methods. Code: github.com/SamuelSchmidgall/AgentLaboratory, **MIT** (per fork mirror). Follow-up **AgentRxiv**, arXiv 2503.18102. — [arXiv](https://arxiv.org/abs/2501.04227v1); [GitHub](https://github.com/SamuelSchmidgall/AgentLaboratory)
- **Robin: A multi-agent system for automating scientific discovery.** Ghareeb, Chang et al. (FutureHouse / Oxford). arXiv **2505.13400** (May 2025). Orchestrates Crow, Falcon and Finch (literature and data-analysis agents) across hypothesis, experiment, analysis and revision. Proposed **ripasudil** for dry AMD, with ABCA1 upregulation as the mechanism. FutureHouse says the code is on GitHub. A claim that it was later published in Nature with an AI-vs-human reanalysis discrepancy (7.5x vs 1.75x) is UNVERIFIED. — [arXiv](https://arxiv.org/pdf/2505.13400); [FutureHouse](https://futurehouse.org/research-announcements/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system); [Pebblous (unverified claim)](https://blog.pebblous.ai/blog/robin-multi-agent-drug-discovery/en/)
- **Kosmos: An AI Scientist for Autonomous Discovery.** Edison Scientific (FutureHouse spinout). arXiv **2511.02824**, launched **2025-11-05**. Each cycle runs parallel data-analysis and literature-search agents over many cycles toward an open objective plus dataset, ending in a cited report. Vendor figures from May 2026: "6 months of research in a day," 80% reproducibility, ~1,500 papers read per run. Commercial platform, not open source. **Edison Advances** launched 2026-07-23 with open weights for MarkushGlyph/OCSRGlyph (chemistry OCR). — [arXiv](https://arxiv.org/pdf/2511.02824); [Edison](https://edisonscientific.com/articles/announcing-kosmos); [runtimewire](https://runtimewire.com/article/edison-scientific-advances-glyph-open-models)
- **AutoDiscovery (formerly AutoDS): Open-ended Scientific Discovery via Bayesian Surprise.** Ai2. **NeurIPS 2025**. MCTS with progressive widening, using **Bayesian surprise** (the LLM's prior-to-posterior belief shift) as reward. Produces 5-29% more "surprising" discoveries on 21 datasets, and two-thirds were surprising to experts. Released in **AstaLabs 2026-02-12**; the original AutoDS codebase is open source. — [Ai2 blog](https://allenai.org/blog/autodiscovery); [NeurIPS](https://neurips.cc/virtual/2025/poster/116398); [SiliconANGLE](https://siliconangle.com/2026/02/12/ai2-introduces-autodiscovery-automated-scientific-discovery-ai-system/)
- **2026 audits of whether agents falsify** (directly relevant to Prometheus's falsification instruments):
  - **"Failing to Falsify: Evaluating and Mitigating Confirmation Bias in Language Models"**, arXiv **2604.02485** (Apr 2026). Uses a Wason-style 2-4-6 rule-discovery task and shows agents that only verify perform worse than those that also seek disconfirming evidence. — [arXiv](https://arxiv.org/html/2604.02485v1)
  - **"AI scientists produce results without reasoning scientifically"**, arXiv **2604.18805** (Apr 2026). Agents ignore evidence in 68% of traces and show refutation-driven revision in only 26%, and the **base model, not the scaffold, explains most variance** (via a Pith referee summary). — [Pith](https://pith.science/paper/2604.18805)
  - **"Sound Agentic Science Requires Adversarial Experiments"**, arXiv **2604.22080** (ICLR 2026 workshop, position paper). — [arXiv](https://arxiv.org/pdf/2604.22080)
  - **Fisher-R1: Training LLM Agents for Reliable Hypothesis Testing**, arXiv **2608.07437** (Aug 2026). RL with a verified statistical reward improves hypothesis-testing reliability. — [arXiv](https://arxiv.org/abs/2608.07437)
  - Title-only, Aug-Sep 2026: "What Proves You Wrong: Benchmarking LMs on Falsifiable Research Ideation" ([2608.22948](https://arxiv.org/pdf/2608.22948)); "Diagnostic Foundation for Evaluating LLMs' Research Integrity as Co-Scientists" ([2608.12345](https://arxiv.org/pdf/2608.12345)); "RECLAIM: Can Agents Reproduce the Claims of ML Papers?" ([2609.28850](https://arxiv.org/html/2609.28850v1)); "Hypothesis-Driven Autonomous Materials Synthesis with Multimodal LLM Agents" with verify/falsify modes ([2609.18598](https://arxiv.org/pdf/2609.18598)).

### Inferences
- The loop is converging. AlphaEvolve, OpenEvolve, ShinkaEvolve, GigaEvo, CodeEvolve and LEVI differ mainly in parent selection, diversity archive, novelty filtering, model routing and evaluator cascade. That makes them **reference arms** Prometheus can run side by side on its own evaluators. OpenEvolve and ShinkaEvolve (both Apache-2.0, local-LLM capable) are the most absorbable.
- Gideoni/Risi/Gal (2602.16805) and Pelleriti et al. (2605.20086, EvoTrace/EvoReplay) are the field's own **falsification instruments** for this loop. They line up with Prometheus's "constant twin / simple baseline" and "what was actually evolved" discipline. EvoTrace's trace schema (lineage, diffs, prompts, evaluator outputs, replay env) is a plausible interchange format for Prometheus's own lineage logs.
- AIRA-dojo's "operator quality is the bottleneck" and LEVI's "archive diversity substitutes for model size" pull in opposite directions on whether mutation quality or selection structure matters more. That is a testable question for an evolutionary ecology that supplies its own primitives.
- Test-time RL inside the loop (ThetaEvolve, TTT-Discover) and self-training on search traces (SOAR) are the 2025-26 move from "frozen LLM as mutation operator" to "operator that learns within the run." That is the closest external analogue to growing reasoning mechanisms.
- **Calibration anchors** with known answers include circle packing n=26, autocorrelation inequalities, Heilbronn and kissing numbers (AlphaEvolve and Tao's 67-problem set), ARC-AGI-1/2 public eval, miniF2F/PutnamBench (Lean-checkable), and LLM-SRBench. These give falsifiable, machine-checkable ground truth.
- The 2026 audits (2604.18805, 2604.02485) suggest that "automated scientist" systems are weak on refutation-driven revision. POPPER's sequential e-value/Type-I-controlled design is the strongest open template for a falsification instrument.

### Gaps
- Exact repo name for the Tao et al. / AlphaEvolve math artifacts is truncated in sources ("github.com/google-deepmind/alp..."). The likely candidates `google-deepmind/alphaevolve_repository_of_problems` and `google-deepmind/alphaevolve_results` are UNVERIFIED.
- No 2026 DeepMind AlphaEvolve research paper was found. "AlphaProof Nexus" (claimed 9 Erdős problems) appeared only in a secondary video summary and is UNVERIFIED.
- Not re-verified this session (identifiers from prior knowledge; treat as UNVERIFIED):
  - AI Scientist v1, arXiv 2408.06292 (Aug 2024)
  - ELM (Lehman et al.), arXiv 2206.08896
  - AlphaDev (*Nature* 2023, sorting)
  - Ai2 CodeScientist (arXiv 2503.22708)
  - Induction/Transduction paper arXiv ID 2411.02272
  - LILO GitHub (gabegrand/lilo)
  - DreamCoder GitHub (ellisk42/ec)
- ARC Prize 2025 3rd-place-and-beyond Kaggle code repos: only writeups were captured, and NVARC's GitHub URL and license were not found.
- Licenses UNVERIFIED for DGM, CodeEvolve, GigaEvo, DeepEvolve, LEVI, GEPA, POPPER, SOAR, Kimina, Poetiq, AI Scientist (changed Dec 2025), Robin and Aviary.
- No independent replication was found of AlphaEvolve's matrix-multiplication or infrastructure claims, or of Kosmos's vendor figures.

---

## Q2. Which have open-source implementations that run on a single workstation (RTX-class 16 GB GPU, 32 GB RAM; Windows host plus Linux laptops)? Hardware needs?

### Takeaway
Most open evolutionary-search frameworks are thin Python orchestrators whose compute cost is (a) LLM calls and (b) your evaluator. They run on a workstation if you point them at a local OpenAI-compatible server (Ollama/vLLM/LM Studio) or a metered/subscription API. Workstation-friendly: OpenEvolve, ShinkaEvolve, LLM4AD/EoH/ReEvo, OpenELM, GEPA, the ARC-AGI-3 toolkit, TRM (7M), SOAR-7B inference, and small Lean provers (Goedel-Prover-V2-8B, Kimina distilled 1.5B/7B, DeepSeek-Prover-V2-7B). Docker/Linux-dependent: DGM/HGM (SWE-bench harness) and AI Scientist. Not workstation-runnable: AlphaEvolve (GCP service), Kosmos (Edison platform), co-scientist (limited access), TTT-Discover's RL (gpt-oss-120b via Tinker), and AlphaProof/Seed-Prover/Aristotle (closed).

### Cited Findings
- **OpenEvolve:**
  - Python 3.10+; Docker optional.
  - "Any OpenAI-compatible API," with a documented **local Ollama/vLLM** config; the FAQ also lists LM Studio and text-generation-webui.
  - **Windows/macOS use `spawn` multiprocessing, so evolution calls must be wrapped in `if __name__ == '__main__':`**.
  - No hardware spec given. Apache-2.0.
  - [GitHub](https://github.com/algorithmicsuperintelligence/openevolve)
- **ShinkaEvolve:**
  - Python >=3.10.
  - `job_type` can be local, slurm_docker or slurm_conda, and evaluations parallelize locally.
  - Has a local-models docs guide and local OpenAI-compatible embedding servers (`local/<model>@http://host:port/v1`).
  - Dev install shows a Windows venv path.
  - Slurm defaults: 1 CPU, 1 GPU, 8 GB.
  - Includes a `max_api_costs` budget cap. Apache-2.0.
  - [GitHub](https://github.com/SakanaAI/ShinkaEvolve)
- **LLM4AD** (EoH, FunSearch, hill climbing, LLaMEA adapted): local or remote LLM through a unified interface, multiprocessing evaluation with timeouts, W&B/TensorBoard. — [arXiv](https://arxiv.org/html/2412.17287v2); [docs](https://llm4ad-doc.readthedocs.io)
- **OpenELM** (CarperAI): `pip install openelm`; the Sodarace env needs swig. MIT. — [GitHub](https://github.com/CarperAI/OpenELM)
- **LEVI** explicitly targets substituting search architecture for model size by routing mutations between large and small LLMs, making it the most "small-local-model" oriented framework found. — [arXiv](https://arxiv.org/abs/2605.09764)
- **CodeEvolve** claims open-weight models match closed baselines at a fraction of the cost. — [arXiv](https://arxiv.org/pdf/2510.14150)
- **ThetaEvolve** uses an **8B** open model (DeepSeek-R1-0528-Qwen3-8B) with test-time RL. — [arXiv](https://arxiv.org/abs/2511.23473v1)
- **TTT-Discover** uses gpt-oss-120b via the Tinker API at "a few hundred dollars per problem"; it is cloud RL, not local. — [arXiv](https://arxiv.org/abs/2601.16175v1)
- **Darwin Gödel Machine:**
  - Requires **Docker** (README hello-world check, docker group), `requirements.txt`, a cloned SWE-bench, and **OpenAI and Anthropic API keys exported in ~/.bashrc** (Linux-style setup).
  - Warns that it runs untrusted model-generated code. — [SourcePulse](https://www.sourcepulse.org/projects/3752776)
  - The SWE-bench harness recommends **x86_64, >=120 GB free disk, 16 GB RAM, 8 cores**. — [PyPI swebench](https://pypi.org/project/swebench)
- **AI Scientist / v2:** executes LLM-written code autonomously and "requires sandboxing." — [Nature coverage](https://noqta.tn/en/news/sakana-ai-scientist-nature-automated-research-2026); [SourcePulse](https://www.sourcepulse.org/projects/2165187)
- **Agent Laboratory:** supports OpenAI o1/o1-preview/o1-mini/gpt-4o/o3-mini and DeepSeek-v3 via API; pure Python, MIT. — [GitHub](https://github.com/SamuelSchmidgall/AgentLaboratory)
- **Poetiq ARC solver:** Python 3.11+ venv with API keys in `.env`; reproduces ARC-AGI-1/2 submissions over Gemini/OpenAI APIs. — [SourcePulse](https://www.sourcepulse.org/projects/20182084)
- **TRM:** a ~7M-parameter model. The author's estimate (via Gigazine) is training in 2 days on **4x H100 for under $500**. The repo is archived/read-only, and the fork if-ai/TinyRecursiveModels adds a uv setup. — [Gigazine](https://gigazine.net/gsc_news/en/20251010-tiny-recursion-model-trm); [README](https://cdn.jsdelivr.net/gh/samsungsailmontreal/tinyrecursivemodels@main/README.md)
- **SOAR** released 7B/32B/123B fine-tuned program-synthesis models on HF. — [HF 7B](https://huggingface.co/julien31/Soar-qwen-7b)
- **ARC-AGI-3 Toolkit:** `pip install arc-agi`; supports **local environment execution without the API** (ARCEngine). ARC-AGI-3-Agents v0.9.3 (2026-01-29) added local env execution and runs via `uv run main.py --agent=random --game=ls20`. — [docs](https://docs.arcprize.org/toolkit/overview); [GitHub](https://github.com/arcprize/ARC-AGI-3-Agents)
- **ARC Prize 2026 Milestone #1 winners** (2026-07-06) ran **local open models inside Kaggle**: Tufa Labs "The Duck" used **Qwen 3.6 27B FP8** writing Python in a live REPL; Reki and "forge" used **Gemma-4-31B** with JSON actions. Code is in Kaggle notebooks. — [ARC Prize blog](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **Lean provers (open weights):**
  - Goedel-Prover-V2-8B and -32B on HF. — [HF](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B)
  - Kimina-Prover distilled 1.5B/7B. — [arXiv](https://arxiv.org/abs/2504.11354v1)
  - DeepSeek-Prover-V2 7B and 671B. — [Goedel-V2 comparison](https://arxiv.org/pdf/2508.03613)
- **MLE-bench:** dataset prep through the Kaggle API takes about 2 days, with Git-LFS data. — [GitHub/summary](https://github.com/openai/mle-bench)
- **AlphaEvolve** is a managed Google Cloud service (GA 2026-07-09). — [Google blog](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/alphaevolve-on-cloud/)
- **Kosmos** is an Edison platform product. — [Edison docs](https://docs.edisonscientific.com/)

### Inferences
These are hardware estimates from model sizes, not measured.
- **16 GB VRAM** comfortably serves a 7-8B model in 8-bit or 4-bit (SOAR-qwen-7b, Goedel-Prover-V2-8B, Kimina-7B, DeepSeek-Prover-V2-7B) as a local mutation operator or prover. 27-32B models (Qwen 3.6 27B, Gemma-4-31B, Goedel-32B, SOAR-32B) need ~4-bit quantization plus CPU offload with 32 GB RAM, and will be slow. 70B+ is impractical.
- **Windows host:** OpenEvolve and ShinkaEvolve are pure Python and should run, with OpenEvolve's `spawn` guard noted. Docker-heavy harnesses (DGM/HGM via SWE-bench, MLE-bench grading, AI Scientist sandboxes) are better placed on the Linux laptops. SWE-bench's 120 GB disk need makes DGM marginal on a laptop.
- **Fine-tuning/RL** on the workstation (SOAR-style hindsight fine-tuning, ThetaEvolve-style test-time RL) is feasible only with LoRA/QLoRA on ≤8B models. That is an inference, and the papers do not report 16 GB configurations.
- TRM training is small enough in parameters (7M) that a single 16 GB GPU should work if slower than 4xH100. The cost would be time, not memory (inference only).
- Proposed tiering for Prometheus:
  - (1) **absorbable local infrastructure:** OpenEvolve, ShinkaEvolve, LLM4AD, ARC-AGI-3 toolkit, Lean plus small provers, EvoTrace format
  - (2) **local harness + API reference arms:** DGM, AI Scientist-v2, Agent Lab, POPPER, Poetiq
  - (3) **cloud-only reference points:** AlphaEvolve GCP, Kosmos, co-scientist, TTT-Discover/Tinker

### Gaps
- No source gave measured VRAM/RAM figures for any evolutionary framework, or for running SOAR/Goedel/Kimina at specific quantization levels on 16 GB.
- AI Scientist-v2's OS/GPU requirements (Linux + NVIDIA GPU + CUDA, as recalled) are UNVERIFIED this session.
- POPPER's runtime requirements (data dependencies, which LLM APIs) were not retrieved.
- Windows compatibility of ShinkaEvolve, GigaEvo, CodeEvolve, LEVI and the ARC-AGI-3 toolkit is not stated in their docs.

---

## Q3. Which labs/orgs emit this work? GitHub orgs, blogs, HF orgs

### Takeaway
Output is concentrated in Google DeepMind (closed core: AlphaEvolve, AlphaProof, AlphaGeometry2, co-scientist; open only FunSearch-era code and math artifacts) and Sakana AI (the most prolific open emitter: ShinkaEvolve, AI Scientist v1/v2, DGM co-authorship). Other hubs are the ARC Prize Foundation (benchmarks plus open-sourced winning solutions), FutureHouse/Edison (science agents, partly open), Stanford SNAP (POPPER), Ai2 (AutoDiscovery/Asta), Inria Flowers (SOAR), Cornell/Ellis and MIT/Tenenbaum-Andreas (library learning), and Chinese labs for Lean provers (DeepSeek, Moonshot/Numina, ByteDance Seed) plus the Goedel-LM team. Community frameworks (OpenEvolve/codelion, LLM4AD/CityU) fill the open-infrastructure gap.

### Cited Findings
- **Google DeepMind:** AlphaEvolve (2506.13131), AlphaProof (Nature Nov 2025), AlphaGeometry2 (2502.03544), co-scientist (2502.18864, Google Research). GitHub: `google-deepmind` (e.g., funsearch, Apache-2.0); AlphaEvolve math artifacts under google-deepmind (exact repo UNVERIFIED). Commercial: Google Cloud AlphaEvolve. — [AlphaEvolve](https://arxiv.org/abs/2506.13131.pdf); [FunSearch](https://en.wikipedia.org/wiki/FunSearch); [Cloud](https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone)
- **Sakana AI (Tokyo):** ShinkaEvolve, AI Scientist v1/v2 and the Nature 2026 paper, DGM (with UBC/Clune). GitHub `SakanaAI`; blog sakana.ai. — [Sakana ShinkaEvolve](https://sakana.ai/shinka-evolve/); [GitHub](https://github.com/SakanaAI/ShinkaEvolve)
- **Jeff Clune lab (UBC / Vector):** DGM, with code at `jennyzzt/dgm`. — [arXiv](https://arxiv.org/html/2505.22954v2)
- **KAUST / Schmidhuber:** HGM, `metauto-ai/HGM`. — [ICLR](https://iclr.cc/virtual/2026/poster/10009359)
- **ARC Prize Foundation** (Chollet, Knoop, Kamradt, Landers, Pinkard): ARC-AGI-1/2/3, tech reports. GitHub `fchollet/ARC-AGI` and `arcprize` (ARC-AGI-3-Agents); docs.arcprize.org; blog arcprize.org/blog with 2026 posts:
  - 2026-03-25 Announcing ARC-AGI-3
  - 2026-04-14 Measuring Human Performance on ARC-AGI-3
  - 2026-05-01 Analyzing GPT-5.5 & Opus 4.7 with ARC-AGI-3
  - 2026-07-06 Milestone #1
  - 2026-09-03 "OpenAI's GPT-6 Astra on ARC-AGI-3"
  - Sources: [ARC blog index](https://arcprize.org/blog); [tech report](https://arxiv.org/html/2601.10904); [ARC-AGI-3-Agents](https://github.com/arcprize/ARC-AGI-3-Agents)
- **ARC competitors/labs:**
  - NVIDIA KGMoN (NVARC)
  - the ARChitects (Lambda-hosted writeup)
  - MindsAI
  - Poetiq (`poetiq-ai`)
  - Tufa Labs
  - Samsung SAIL Montréal (`SamsungSAILMontreal/TinyRecursiveModels`)
  - Jeremy Berman (`jerber`)
  - Sources: [ARC 2025](https://arcprize.org/competitions/2025); [Milestone 1](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **Inria Flowers (Oudeyer, Colas):** SOAR, GitHub `flowersteam`, HF `julien31`. — [HF](https://huggingface.co/julien31/Soar-qwen-32b)
- **Cornell / Kevin Ellis group:** DreamCoder lineage, induction+transduction (ICLR 2025), WorldCoder, VisualPredicator. — [alphaXiv profile](https://www.alphaxiv.org/@kevin-ellis)
- **MIT (Tenenbaum, Andreas, Solar-Lezama):** LILO, Stitch (`mlb2251/stitch`). — [Stitch](https://arxiv.org/pdf/2211.16605); [LILO](https://proceedings.iclr.cc/paper_files/paper/2024/hash/819cebb05f993840e8a52d7564c5c282-Abstract-Conference.html)
- **FutureHouse / Edison Scientific:** Robin, Kosmos, PaperQA, Aviary. GitHub `Future-House` / `future-house` (aviary; paper-qa listed Apache-2.0 by aggregator). Docs at docs.edisonscientific.com; Edison Advances (open weights) from 2026-07-23. — [aviary](https://github.com/future-house/aviary); [paper-qa](https://ossinsight.io/analyze/Future-House/paper-qa); [Edison docs](https://docs.edisonscientific.com/)
- **Stanford SNAP (Leskovec) + Candès:** POPPER, `snap-stanford/POPPER`. — [arXiv](https://arxiv.org/abs/2502.09858)
- **Allen Institute for AI (Ai2):** AutoDiscovery/AutoDS (NeurIPS 2025) inside the Asta / AstaLabs ecosystem; blog allenai.org/blog. GitHub org `allenai`; AutoDS repo name UNVERIFIED. — [Ai2](https://allenai.org/blog/autodiscovery)
- **Meta FAIR:** AIRA-dojo (MLE-bench agents). — [arXiv](https://arxiv.org/html/2507.02554v2)
- **OpenAI:** MLE-bench (`openai/mle-bench`); gpt-oss-120b used by TTT-Discover. — [MLE-bench](https://github.com/openai/mle-bench)
- **Lean prover orgs:**
  - DeepSeek (`deepseek-ai`)
  - Moonshot/Numina (`MoonshotAI/Kimina-Prover-Preview`)
  - Goedel-LM (HF `Goedel-LM`; Princeton affiliation UNVERIFIED)
  - ByteDance Seed (seed.bytedance.com)
  - Harmonic (Aristotle)
  - Epoch AI (FrontierMath: Erdős)
  - Sources: [Kimina](https://arxiv.org/abs/2504.11354v1); [Goedel HF](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B); [Seed](https://seed.bytedance.com/en/blog/seed-prover-1-5-advanced-mathematical-reasoning-through-a-novel-agentic-architecture); [Epoch](https://epoch.ai/latest/announcing-frontiermath-erdos)
- **Open-framework maintainers:**
  - `algorithmicsuperintelligence` / codelion (OpenEvolve)
  - `Optima-CityU` (LLM4AD)
  - `FeiLiu36` (EoH)
  - `ai4co` (ReEvo)
  - `CarperAI` (OpenELM)
  - `inter-co` (CodeEvolve)
  - AIRI-Institute / FusionBrainLab (GigaEvo)
  - `liugangcode` (DeepEvolve)
  - `ttanv` (LEVI)
  - `gepa-ai` (GEPA)
  - Sources: [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve); [LLM4AD](https://arxiv.org/abs/2412.17287); [EoH](https://arxiv.org/abs/2401.02051v3); [ReEvo](https://arxiv.org/abs/2402.01145v3)
- **Terence Tao's blog** (terrytao.wordpress.com): a primary venue for AlphaEvolve/Erdős math commentary. — [mirror of post](https://tagteam.harvard.edu/hub_feeds/3899/feed_items/16691196)
- **Microsoft Research / UW:** ThetaEvolve. — [MSR](https://www.microsoft.com/en-us/research/?p=1173254)
- **Zuse Institute Berlin (Pokutta group per affiliation; UNVERIFIED group attribution):** EvoTrace (2605.20086). — [arXiv](https://arxiv.org/html/2605.20086v1)

### Inferences
Suggested watch-list for polling:
- **arXiv:** cs.NE, cs.AI, cs.LG, cs.PL, cs.LO, with keyword filters "AlphaEvolve | evolutionary coding agent | program evolution | refinement loop | ARC-AGI | library learning | Lean prover | falsification | hypothesis validation"
- **GitHub orgs and repos:** releases/commits from google-deepmind, SakanaAI, algorithmicsuperintelligence/openevolve, arcprize, flowersteam, snap-stanford, future-house, allenai, Goedel-LM, deepseek-ai, MoonshotAI, Optima-CityU, gepa-ai
- **Blogs:** arcprize.org/blog, sakana.ai, deepmind.google/blog, edisonscientific.com, allenai.org/blog, Tao's blog, epoch.ai/latest
- **Leaderboards:** Kaggle ARC Prize 2026 (both tracks)
- **HF orgs:** SakanaAI, Goedel-LM, deepseek-ai, julien31, AI-MO (UNVERIFIED for Kimina weights)

### Gaps
- No official HF org was confirmed for Kimina-Prover weights, Ai2 AutoDS, or Edison Advances models.
- Tenenbaum/Andreas 2025-26 program-induction papers specific to this scope were not surfaced (searches returned only the 2024 LILO and earlier work).
- Kevin Ellis group 2025-26 arXiv IDs were not confirmed.

---

## Q4. Which benchmarks matter (dates, URLs, download access)?

### Takeaway
Use benchmarks in three tiers:
- **Few-shot program induction:** ARC-AGI-1/2, plus ARC-AGI-3 for interactive skill acquisition.
- **Open-ended optimization with machine-checkable scores:** AlphaEvolve/Tao problem sets, ALE-Bench, AlgoTune, FrontierCO, BLADE, LLM-SRBench.
- **Formal verification and agentic science/ML engineering:** miniF2F, PutnamBench, FrontierMath: Erdős, MLE-bench, SWE-bench/Polyglot for self-improving coders.

All the ARC sets, MLE-bench, LLM-SRBench and the Lean benchmarks are downloadable. ARC-AGI-3 has a local toolkit, but private evaluation is Kaggle-only.

### Cited Findings
- **ARC-AGI-1** (2019): repo github.com/fchollet/ARC-AGI. — [ARC 2025 tech report](https://arxiv.org/html/2601.10904)
- **ARC-AGI-2:** Chollet, Knoop, Kamradt, Landers, Pinkard. arXiv **2505.11831**, v1 **2025-05-17**, v2 2026-01-15. Same input-output grid format; a more granular signal at higher fluid intelligence; extensive human testing. Top scores:
  - Kaggle private: 24.03% (NVARC, 2025)
  - Semi-private: 54% (Poetiq + Gemini 3 Pro, ~$30/task)
  - **2026 is the final year of the ARC-AGI-2 track**, with a grand prize guaranteed to the best open-source solution.
  - Sources: [arXiv](https://arxiv.org/abs/2505.11831); [tech report](https://arxiv.org/html/2601.10904); [ARC-AGI-3 competition page](https://arcprize.org/competitions/2026/arc-agi-3)
- **ARC-AGI-3:** "ARC-AGI-3: A New Challenge for Frontier Agentic Intelligence," arXiv **2603.24621**, v1 2026-03-24, v2 2026-04-17. **Launched 2026-03-25** as an interactive turn-based benchmark of hundreds of handcrafted environments with no instructions.
  - **Efficiency-based scoring against human action baselines.** Humans score 100%; frontier AI was <1% at launch (0.26% official, other outlets cite 0.37-0.51%).
  - Access: `pip install arc-agi` toolkit (local play, game editing) and the ARC-AGI-3-Agents repo (v0.9.3, 2026-01-29).
  - **ARC Prize 2026 ARC-AGI-3 track: $850K.** Grand Prize $700K for 100%; open-sourcing required; no internet during evaluation; Kaggle submission.
  - Milestone #1 closed 2026-06-30 (winners posted 2026-07-06); milestone #2 closed 2026-09-30.
  - Final deadline **2026-11-02**, with winners **2026-12-04** (per secondary search summary).
  - Sources: [launch](https://arcprize.org/blog/arc-agi-3-launch); [arXiv](https://arxiv.org/abs/2603.24621); [competition](https://arcprize.org/competitions/2026/arc-agi-3); [Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3); [toolkit](https://docs.arcprize.org/toolkit/overview); [Milestone 1](https://arcprize.org/blog/arc-prize-2026-milestone-1)
- **MLE-bench:** OpenAI. arXiv **2410.07095** (Oct 2024; ICLR 2025) [BG]. 75 Kaggle competitions; best at release was o1-preview+AIDE with ≥bronze in 16.9%. Code and data at github.com/openai/mle-bench (Kaggle API credentials, Git-LFS, ~2 days prep). A community fork recommends ≥3 seeds and mean ± SEM. 2025 SOTA on **MLE-bench Lite**: AIRA-dojo 47.7% to 55%. — [arXiv](https://arxiv.org/pdf/2410.07095); [GitHub](https://github.com/openai/mle-bench); [AIRA](https://arxiv.org/html/2507.02554v2)
- **ALE-Bench:** Sakana et al. arXiv **2506.09050** (Jun 2025), NeurIPS 2025. Built from AtCoder Heuristic Contests: score-based, long-horizon iterative refinement, 22 models evaluated, with a human gap in consistency and long-horizon work. — [arXiv](https://arxiv.org/pdf/2506.09050)
- **AlgoTune:** NeurIPS 2025 Datasets & Benchmarks. Speeding up numerical programs vs SciPy/sklearn/CVXPY references. 120 tasks (another version cites 154); AlgoTuner averages 1.58x. Models "fail to discover algorithmic innovations," preferring surface-level optimizations. — [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9a648e8e1014c2427156dcb5465cd488-Abstract-Datasets_and_Benchmarks_Track.html)
- **FrontierCO** (ICLR 2026 submission): 8 combinatorial-optimization problems across 5 domains (TSPLib, DIMACS instances), 23 approaches including FunSearch and ReEvo, and a normalized gap to best-known. Classical solvers remain strongest on hard instances (slides only). — [ICLR slides](https://iclr.cc/media/iclr-2026/Slides/10010940.pdf)
- **BLADE:** arXiv **2504.20183** (Apr 2025). Benchmark suite for LLM-driven automated design of continuous black-box optimizers (MA-BBOB, SBOX-COST, instance generators). — [arXiv](https://arxiv.org/abs/2504.20183)
- **LLM-SRBench:** Shojaee et al. arXiv **2504.10415** (Apr 2025); **ICML 2025 oral**. 239 equation-discovery problems (111 LSR-Transform + 128 LSR-Synth, designed against memorization); best system reaches 31.5% symbolic accuracy. Accepts programs as hypotheses. — [arXiv](https://arxiv.org/pdf/2504.10415); [ICML](https://icml.cc/virtual/2025/oral/47220)
- **AlphaEvolve / Tao problem set:** 67 problems (analysis, combinatorics, geometry, number theory) with best-known values, plus the AlphaEvolve white-paper problems (circle packing n=26, Heilbronn, kissing numbers, autocorrelation inequalities, Erdős minimum overlap). These are reused as reproducibility checks by GigaEvo, ShinkaEvolve, OpenEvolve, ThetaEvolve and TTT-Discover. — [arXiv 2511.02864](https://arxiv.org/abs/2511.02864); [GigaEvo](https://arxiv.org/abs/2511.17592v1); [TTT-Discover](https://arxiv.org/abs/2601.16175v1)
- **EvoTrace** (May 2026): a dataset of evolutionary-coding-agent search traces (4 frameworks x 16 tasks) with replay environments, a meta-benchmark for analyzing search itself. — [arXiv](https://arxiv.org/html/2605.20086v1)
- **Lean benchmarks:**
  - **miniF2F**: saturated; 88-93% at modest pass@k, and Seed-Prover "saturates".
  - **PutnamBench**: 658 problems in DeepSeek-V2's count, 672 in a 2026 count. Records: DeepSeek-V2 49; Goedel-V2 86 @184; Seed-Prover >50%.
  - **FrontierMath: Erdős** (Epoch AI, Aug 2026): 68 open problems in Lean.
  - Sources: [DeepSeek-Prover-V2](https://arxiv.org/abs/2504.21801v1); [Goedel-V2](https://arxiv.org/pdf/2508.03613); [Seed-Prover](https://www.alphaxiv.org/abs/2507.23726v2); [Epoch](https://epoch.ai/latest/announcing-frontiermath-erdos)
- **SWE-bench (Verified) & Polyglot:** the self-improvement yardsticks for DGM (20% to 50% SWE-bench; 14.2% to 30.7% Polyglot) and HGM. SWE-bench needs Docker, x86_64 and ≥120 GB disk. — [DGM](https://arxiv.org/html/2505.22954v2); [swebench](https://pypi.org/project/swebench)
- **Science-agent evaluation sets:**
  - POPPER: 6 domains with Type-I error control. — [arXiv](https://arxiv.org/abs/2502.09858)
  - AutoDiscovery: 21 real datasets, LLM-judged surprise plus expert check. — [NeurIPS](https://neurips.cc/virtual/2025/poster/116398)
  - Title-only, Aug-Sep 2026: "What Proves You Wrong" falsifiable-ideation benchmark ([2608.22948](https://arxiv.org/pdf/2608.22948)); RECLAIM, reproducing ML paper claims ([2609.28850](https://arxiv.org/html/2609.28850v1)).

### Inferences
- For Prometheus as a **calibration-anchor** set, prefer benchmarks with machine-checkable ground truth and known optima: AlphaEvolve/Tao constructions (numeric bound verifiable), ARC-AGI-1/2 public eval (exact-match), Lean benchmarks (kernel-checked), and LLM-SRBench (symbolic accuracy). Treat LLM-judged metrics (AutoDiscovery "surprise," AI Scientist review scores) as uncalibrated.
- ARC-AGI-3's efficiency-vs-human-actions metric is the most direct external test of "skill acquisition," as opposed to competence at a fixed task. Its local toolkit makes it absorbable as an environment, but leaderboard scores depend on Kaggle-only private games. Milestone #1 organizers noted local public-game checks were "not a reliable proxy" for leaderboard performance.
- AlgoTune's finding (surface-level optimizations, not algorithmic innovation) and FrontierCO's (classical solvers still win on hard instances) are useful **negative anchors** against overclaiming from evolutionary code search.

### Gaps
- ARC-AGI-2 data repo URL (likely `arcprize/ARC-AGI-2`) was not confirmed.
- Exact ARC-AGI-3 environment counts and scoring formula were not in the abstract.
- Verified frontier scores on ARC-AGI-3 are not captured. The GPT-6 Astra post (2026-09-03) returned 404 to the fetcher. A tracking-site claim of Claude Opus 5 at 30.16% on the 25-environment public demo (Jul 2026) and a Reddit "Seed IQ 100%" claim are UNVERIFIED.
- ARC-AGI-3 Milestone #2 winners appeared only in a secondary search summary, and no Milestone #2 post was visible on the blog index at fetch time: Daniel Franzen 27.9%, "Lord Han Solo" 23.8%, Lohit Siriki 22.5%. UNVERIFIED.
- Milestone #1 prize split conflicts: Kaggle says $25K/$7.5K/$5K, the ARC page says $25K/$10K/$2.5K. Milestone #1 scores were not published in the fetched post.
- No 2026 MLE-bench (full) leaderboard was found. AIRA₂ claims (Kaggle gold, 81.5% mean percentile) come from one secondary source and are UNVERIFIED.
- Download/licensing terms for ALE-Bench, AlgoTune, FrontierCO and LLM-SRBench datasets were not retrieved (repos not captured).
