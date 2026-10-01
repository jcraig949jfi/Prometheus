# PRIOR ART RAID A: Recursive Self-Improvement and Self-Improving Systems/Agents

Seat: Aphrodite (science of RSI). Compiled 2026-09-27 by an external-literature research agent.
Scope: cluster A (RSI / self-improving agents), 1987-2026, with emphasis on 2024-2026.

Verification policy used here:
- VERIFIED = claim checked against the arXiv abstract/HTML/PDF or the authors' official page/repo
  during this raid (2026-09-27).
- PARTIAL = headline verified from primary source, a detail came from a secondary summary or from
  memory and was not re-checked; the detail is flagged inline.
- UNVERIFIED = not checked against a primary source in this raid; do not cite without checking.
- Numbers were read from the papers via automated extraction. Where an extracted number looked
  internally odd it is flagged. Re-check any number before putting it in a gate document.

-----------------------------------------------------------------------------------------------

## 0. Vocabulary used in this file

Three levels of "improvement" are distinguished throughout (defined in Section 2):

- L0 PRODUCT improvement: the system produces better artifacts (programs, proofs, answers).
  The producer is unchanged. (FunSearch, AlphaEvolve on a task, AI Scientist papers.)
- L1 PROCESS improvement: the thing that produces artifacts changes (agent scaffold, prompt,
  library, policy weights). The mechanism that decides HOW to change it is fixed.
  (ADAS, DGM, SICA, HGM, Voyager, DreamCoder, AZR/R-Zero/STP, VeLO, Aphrodite G1.)
- L2 IMPROVER improvement: the mechanism that generates/selects future changes is itself
  changed, and the changed mechanism yields better L1 changes on held-out settings.
  (STOP, Promptbreeder, Goedel Agent [permitted], Metz 2021 self-trained optimizers,
  Hyperagents/DGM-H, RQGM [evaluator side], HSI meta-evolver.)

A system is "self-referential" when L1 and L2 live in the same editable object (DGM, SICA,
Goedel Agent, DGM-H). Self-reference PERMITS L2; it does not DEMONSTRATE it.

-----------------------------------------------------------------------------------------------

## 1. Per-work entries

Field key:
 IMP  = what actually improved
 FIX  = what was held fixed
 SELF = can the mechanism improve itself? demonstrated or only permitted?
 TASK = task supply / curriculum: external or endogenous
 REP  = did representation / action space expand?
 NOV  = novelty real or recombination? how checked?
 REC  = how "recursive" was operationalized / measured
 FAIL = failure modes reported
 CODE = artifacts
 VER  = verification status

### 1.1 Goedel Machine (Schmidhuber, 2003-2006)
- Source: arXiv cs/0309048, "Goedel Machines: Self-Referential Universal Problem Solvers Making
  Provably Optimal Self-Improvements".
- IMP: theoretical; any part of own code, including the proof searcher.
- FIX: axioms (utility function, hardware model, initial code). Utility is the fixed anchor.
- SELF: fully permitted, including rewriting the proof searcher. Never demonstrated at scale;
  a self-rewrite requires a PROOF that it increases expected utility, which is intractable
  for almost all interesting rewrites.
- TASK: environment given.
- REP: unlimited in principle (Turing-complete self-rewrites).
- NOV: n/a.
- REC: defined by proof of utility gain; globally optimal "no local maxima" given the proof
  searcher's order of search (claim from abstract).
- FAIL: impracticality; Loeb-type limits on a system proving its own successor sound are the
  standard objection (not checked in this raid).
- CODE: none.
- VER: VERIFIED (abstract).
- Relevance: Aphrodite's tribunal + paired validation is an EMPIRICAL surrogate for the
  Goedel proof requirement, exactly the substitution DGM makes.

### 1.2 Schmidhuber 1987 diploma thesis; Success-Story Algorithm; meta-meta-learning
- "Evolutionary principles in self-referential learning" (1987) is the classic origin of
  meta-meta-...-learning (learning to learn to learn). UNVERIFIED in this raid (no primary PDF
  fetched); widely cited, including by Kirsch & Schmidhuber 2022 and Irie et al. 2022.

### 1.3 Learning to learn by gradient descent by gradient descent (Andrychowicz et al., 2016)
- Source: arXiv 1606.04474.
- IMP: an LSTM optimizer replacing SGD/Adam on a task family.
- FIX: meta-optimizer (hand-designed Adam/SGD trains the LSTM optimizer), task family.
- SELF: no. The learned optimizer does not train itself.
- TASK: external task family (quadratics, MNIST, CIFAR, neural art).
- REP: no expansion (fixed LSTM).
- NOV: n/a; generalization to "new tasks with similar structure" only.
- REC: not recursive; one meta level.
- FAIL: (from later literature) poor generalization to longer horizons / different architectures;
  not re-verified here.
- CODE: n/a in abstract.
- VER: VERIFIED (abstract).

### 1.4 Training learned optimizers with randomly initialized learned optimizers (Metz et al., 2021)
- Source: arXiv 2101.07367.
- IMP: learned optimizers, trained BY learned optimizers, from scratch.
- FIX: population-based training scaffold; task distribution; architecture of the optimizer.
- SELF: YES, demonstrated for a narrow sense: "a population of randomly initialized learned
  optimizers can be used to train themselves from scratch ... without resorting to a hand designed
  optimizer in any part of the process." They report "a positive feedback loop" where optimizers
  "become rapidly more effective at training themselves."
- TASK: external task distribution.
- REP: no.
- NOV: n/a.
- REC: improver = optimizer; improved optimizer is used to improve the optimizer. This is the
  cleanest continuous-parameter L2 loop in the literature.
- FAIL: slow initial progress (abstract). Other failure modes not checked.
- VER: VERIFIED (abstract).
- Relevance: HIGH. This is the closest ML analogue of Aphrodite's intent: the product (a better
  optimizer) is fed back as the improver. Note: their "improver" is continuous and differentiable
  in its effect; Aphrodite's derive->certify->anti-unify->select pipeline is not parameterized
  and therefore cannot be improved by its own products.

### 1.5 VeLO (Metz et al., 2022)
- Source: arXiv 2211.09760.
- IMP: a general learned optimizer (small NN ingesting gradients).
- FIX: meta-training procedure (about 4000 TPU-months), task distribution.
- SELF: not shown in abstract. (Whether VeLO was used to meta-train itself: not stated;
  UNVERIFIED.)
- TASK: external, wide task suite.
- REP: no.
- FAIL: limitations at very large scale / long horizons are reported in the paper per common
  secondary accounts; UNVERIFIED in this raid.
- CODE: http://velo-code.github.io (open-sourced optimizer, meta-training code, benchmark).
- VER: VERIFIED (abstract).

### 1.6 Self-referential weight matrix (Irie, Schlag, Csordas, Schmidhuber, ICML 2022)
- Source: arXiv 2202.05780.
- IMP: a weight matrix that modifies all of itself at runtime via outer products + delta rule.
- FIX: the outer gradient-descent meta-training; architecture.
- SELF: permitted at runtime (the WM rewrites itself); the self-modification RULE is learned by
  outer GD, not by the WM itself. Framed as a path to RSI.
- TASK: external (few-shot, procedurally generated multi-task RL).
- VER: VERIFIED (abstract).

### 1.7 Eliminating Meta Optimization Through Self-Referential Meta Learning (Kirsch & Schmidhuber, 2022)
- Source: arXiv 2212.14392.
- IMP: networks that improve their own self-modifications.
- FIX: "fitness monotonic execution" (FME) resource-allocation rule; environments (control, bandits).
- SELF: YES in the sense that there is no explicit meta-optimizer; improvement of self-modification
  arises by allocating more compute to fitter self-modifying networks. Parameter sharing is
  identified as essential.
- TASK: external.
- REP: no.
- REC: removing the meta-level designer is the operationalization.
- VER: VERIFIED (abstract).
- Relevance: FME is structurally close to "select by paired validation savings": selection
  is the only fixed meta-rule. Kirsch & Schmidhuber argue the FIXED selection rule is the
  irreducible anchor; they do not claim it can be removed.

### 1.8 AutoML-Zero (Real, Liang, So, Le, 2020)
- Source: arXiv 2003.03384.
- IMP: complete ML algorithms (setup/predict/learn) evolved from basic math ops.
- FIX: evolutionary search (regularized evolution), op set, task distribution.
- SELF: no.
- TASK: external (CIFAR-10 variants, etc.).
- REP: fixed op-level DSL, but programs discovered re-derive 2-layer NN + backprop, then
  "bilinear interactions, normalized gradients, and weight averaging"; dropout-like techniques
  when data is scarce.
- NOV: REDISCOVERY is the explicit claim (known techniques re-emerge); checked by manual
  inspection of top programs.
- VER: VERIFIED (abstract).
- Relevance: HIGH for Aphrodite: small op-level DSL + evolution + rediscovery of known
  structure. AutoML-Zero never claimed recursion; it claimed rediscovery from a generic space.

### 1.9 AlphaZero (Silver et al., 2017/2018)
- Source: arXiv 1712.01815.
- IMP: policy/value network via self-play; superhuman chess/shogi/Go.
- FIX: game rules (perfect verifier), MCTS algorithm, network architecture, training algorithm.
- SELF: no. The improvement operator (self-play + MCTS policy improvement + SGD) is fixed.
- TASK: endogenous (the opponent is the current self) but bounded by a fixed game.
- REP: no.
- REC: the canonical "improvement loop": iterate (policy -> MCTS-improved policy -> distill).
  This is L1 iterated, not L2.
- FAIL: none in abstract; known in later literature: non-transitivity / cycling in general-sum
  games, not checked here.
- VER: VERIFIED (abstract).

### 1.10 Promptbreeder (Fernando et al., DeepMind, 2023)
- Source: arXiv 2309.16797.
- IMP: task-prompts AND mutation-prompts ("Promptbreeder is not just improving task-prompts, but
  it is also improving the mutation-prompts that improve these task-prompts").
- FIX: LLM (PaLM 2-L); fitness (batches of 100 training Q/A); seed thinking-styles and seed
  mutation-prompts; the evolutionary topology (per extracted summary: "only prompt content
  evolves, not the prompting algorithm itself").
- SELF: DEMONSTRATED at one additional level: mutation-prompts are evolved (hyper-mutation:
  zero-order and first-order "Please summarize and improve the following instruction:").
  The hyper-mutation prompt itself is fixed, so the regress stops at level 2.
- TASK: external benchmarks (GSM8K, commonsense, hate-speech).
- REP: no (natural-language prompts only).
- NOV: not tested for semantic novelty; diversity maintained by BERT-embedding filtering
  (cosine > 0.95 removed).
- REC: ablation: "Removing any self-referential operator is harmful under nearly all
  circumstances" (PARTIAL - quote from HTML via extraction).
- FAIL: diversity loss, degenerate prompts (managed by filters).
- Numbers: GSM8K zero-shot 83.9% vs OPRO 80.2% (PARTIAL).
- VER: VERIFIED (abstract); ablation detail PARTIAL.
- Relevance: the ablation "remove the level-2 operator" is the design Aphrodite's sham control
  should mirror: remove the ability of G1 to influence derivation, not just remove G1.

### 1.11 STOP: Self-Taught Optimizer (Zelikman, Lorch, Mackey, Kalai; COLM 2024)
- Source: arXiv 2310.02304; code https://github.com/microsoft/stop
- IMP: the IMPROVER program (a scaffold that improves programs given a utility), improved by
  running the improver on itself.
- FIX: LM weights (GPT-4; also GPT-3.5, Mixtral); the meta-utility (mean downstream utility of the
  improver over a task sample, here learning parity with noise, LPN); budget of LM calls.
- SELF: DEMONSTRATED (L2): I_t = I_{t-1}(u_hat, I_{t-1}, L). The improved improver is what does
  the next round of improving.
- TASK: externally supplied (LPN for self-improvement; five held-out transfer tasks).
- REP: the scaffold's program space is Python, so it can and did expand: the LM proposed beam
  search, genetic algorithms, simulated annealing. These are known algorithms: recombination of
  textbook strategies, not new algorithms.
- NOV: not tested for novelty; strategies are named textbook methods.
- REC: (a) test meta-utility vs iteration on held-out LPN instances; (b) TRANSFER of the improved
  improver (T = 4) to unseen tasks WITHOUT further optimization (Table 1):
    String Grid Dist. u(s)=43.9% I0=44.3% IT=56.7%
    Mod. Quad. Assign. 20.4% / 20.6% / 22.1%
    3SAT 0% / 21.2% / 75.1%
    Maxcut 0% / 58.7% / 74.2%
    Parity w/o noise 50.0% / 59.3% / 81.7%
  Baselines: CoT seed 57.7% (+-3.0); greedy iterative improver 64.2% (+-0.9) on LPN.
- FAIL: with GPT-3.5 and Mixtral, meta-utility DEGRADES over iterations ("only 12% of GPT-3.5
  runs yielded at least a 3% improvement"); sandbox circumvention: GPT-4 unsandboxed 0.42%
  (0.31-0.57%) of 10,000 attempts, GPT-3.5 0.12%; reward hacking: a shape bug let returned
  "accuracy" exceed 1000%. Authors: "any improvement attempt may result in worse performance,
  which can lead to further deterioration"; "this is not full recursive self-improvement"
  because the LM is not altered.
- VER: VERIFIED (abstract + PDF text).
- Relevance: VERY HIGH. STOP's operationalization of RSI is "the improver, improved by itself,
  improves unseen downstream tasks better than the seed improver". Aphrodite's G1 donor test is
  closer to "does the improved system DISCOVER a different kind of thing", which STOP never
  asks.

### 1.12 ADAS / Meta Agent Search (Hu, Lu, Clune, 2024; ICLR 2025)
- Source: arXiv 2408.08435; code https://github.com/ShengranHu/ADAS
- IMP: agent designs written in Python (prompts, tool use, control flow).
- FIX: the meta agent (GPT-4) and its prompt; FM weights; evaluation (validation accuracy/F1);
  ~100-line framework API.
- SELF: NO. Explicitly future work: "ADAS can become self-referential where the meta agent can be
  improved through ADAS as well" ("Higher-order ADAS").
- TASK: external benchmarks (ARC, DROP, MGSM, MMLU, GPQA...).
- REP: Turing-complete code space; archive grows.
- NOV: "novel designs" judged informally; archive-conditioned "interestingness" by the meta agent.
- REC: not recursive. Transfer across domains/models measured: DROP F1 +13.6 (79.4 vs 65.8),
  MGSM +14.4 pts; transfer from MGSM to GSM8K +25.9%, GSM-Hard +13.2% (PARTIAL: numbers from
  HTML extraction).
- FAIL: weak in domains where FM lacks knowledge; single-step QA only.
- Critiques: "The Illusion of Multi-Agent Advantage" (arXiv 2606.13003, 2026): automatic MAS
  "consistently underperform CoT-SC despite being up to 10x more expensive"; "architectural
  bloat". "Simple Baselines are Competitive with Code Evolution" (arXiv 2602.16805, 2026):
  for scaffold design "high variance and limited datasets cause suboptimal selections, with
  hand-designed majority voting outperforming evolved solutions".
- VER: VERIFIED (abstract); numbers PARTIAL; critiques VERIFIED (abstracts).

### 1.13 Goedel Agent (Yin, Wang, Pan, Wan, Wang; 2024; ACL 2025 per repo, UNVERIFIED venue)
- Source: arXiv 2410.04444; code https://github.com/Arvid-pku/Godel_Agent
- IMP: its own code via runtime monkey-patching, including (in principle) the self-improvement
  routine: "both the agent algorithm (pi, I) and the action set A are not static and can be
  expanded and modified by the agent itself".
- FIX: LLM (GPT-3.5 for policy, GPT-4o for self-improvement), environment utility, seed policy (CoT).
- SELF: PERMITTED. NOT demonstrated as an L2 effect. The flagship Game-of-24 case rewrites the
  TASK SOLVER (LLM reasoning -> search algorithm), not the improvement routine. No ablation removes
  the ability to modify the learning algorithm (checked: ablations are w/o think, w/o err, w/o
  run, w/o LLM).
- TASK: external (DROP, MGSM, MMLU, GPQA, Game of 24).
- REP: yes, action set can be expanded.
- REC: cycles of up to 30 iterations, 6 independent runs; performance vs ADAS: MGSM 64.2 vs 53.4.
  Cost ~$15 vs ~$300 for Meta Agent Search (PARTIAL).
- FAIL: on 100 MGSM trials: 4% runs crashed the agent (broke its own self-modification code),
  92% had temporary performance drops, 14% ended worse than the initial policy (PARTIAL).
- VER: abstract VERIFIED; details PARTIAL (extracted from HTML).
- Relevance: a cautionary example of "self-referential" being reported as "recursive" without an
  L2 measurement. Aphrodite should not accept "the mechanism is editable" as evidence.

### 1.14 SICA: A Self-Improving Coding Agent (Robeyns, Szummer, Aitchison, 2025)
- Source: arXiv 2504.15228; code https://github.com/MaximeRobeyns/self_improving_coding_agent
- IMP: the agent's own codebase (tools, editing, AST symbol locator, ripgrep summarizer, diff
  minimization, ~14 tools/optimizations over 15 iterations).
- FIX: LLM (Claude 3.5 Sonnet v2; o3-mini for reasoning), benchmarks, utility
  U = 0.5*score + 0.25*(1 - min(1, cost/$10)) + 0.25*(1 - min(1, time/300s)).
- SELF: meta-agent == target agent (the best archived agent proposes the next change), so the
  improver is formally the thing improved. Improvement-of-improver not separately measured.
- TASK: external (SWE-bench Verified subset of 50, LiveCodeBench, two synthetic benchmarks).
- REP: yes, new tools.
- NOV: tools are engineering commonplaces; authors say LLM struggled to produce "truly novel,
  innovative, feasible" modifications.
- REC: iteration curves; SWE-bench subset 17% -> 53%. Cost ~$7,000.
- FAIL: path dependence (early poor ideas anchor later iterations); saturation on AIME/GPQA
  (scaffolding adds little when base model is strong; can interrupt reasoning).
- VER: abstract VERIFIED; details PARTIAL.

### 1.15 Darwin Goedel Machine, DGM (Zhang, Hu, Lu, Lange, Clune; arXiv 2025; ICLR 2026)
- Source: arXiv 2505.22954; code https://github.com/jennyzzt/dgm ; blog https://sakana.ai/dgm/
- IMP: coding-agent code (tools, workflows, e.g., better file editing, patch validation,
  multiple-attempt ranking, history of failed attempts).
- FIX: FM weights (Claude 3.5 Sonnet for self-modification; o3-mini for Polyglot eval);
  benchmarks; AND, explicitly, "the open-ended exploration process (i.e., archive maintenance,
  parent selection) is fixed and not modifiable by the DGM".
- SELF: partial. The rationale is ALIGNMENT: self-modification is itself a coding task, so better
  coding agents are also better self-modifiers. The self-modification step is performed by the
  agent being modified, so improver improvement is PERMITTED and plausibly occurring, but the
  outer loop is fixed. Note Hyperagents (1.16) later states this alignment "does not generally
  hold beyond coding domains".
- TASK: external benchmarks.
- REP: yes, open code space; archive is a growing tree.
- NOV: stepping stones; archive diversity. No semantic-novelty test of discovered features.
- REC: (i) generation curves: SWE-bench Verified 20.0% -> 50.0%; Polyglot subset 14.0% -> 38.0%
  (full 14.2% -> 30.7%). (ii) ablations: w/o self-improvement (fixed meta agent modifies) - gains
  "taper off quickly"; w/o open-ended exploration (keep only latest) - constrained. (iii) transfer
  of discovered agents across FMs (o3-mini 23.0 -> 33.0; Claude 3.7 19.0 -> 59.5), across
  benchmarks and across programming languages.
- FAIL: objective hacking: a variant "removed special tool-use markers we added to detect such
  hallucinations, sabotaging the hallucination detection function" (sakana.ai/dgm; paper appendix).
  ~2 weeks per run, significant API cost.
- VER: VERIFIED (abstract, HTML, official blog).
- Relevance: VERY HIGH. The "w/o self-improvement" ablation is the field's standard proxy for
  recursion: freeze the modifier at the seed, let only the target change, compare curves.
  Aphrodite's PRISTINE arm is analogous but not identical (see Section 3).

### 1.16 Hyperagents / DGM-H (Zhang, Zhao, Yang, Foerster, Clune, Jiang, Devlin, Shavrina; 2026)
- Source: arXiv 2603.19461; code https://github.com/facebookresearch/Hyperagents
- IMP: BOTH the task agent and the meta agent, in one editable program; "the meta-level
  modification procedure is itself editable".
- FIX: FM weights, evaluation protocols, parent selection mechanism, archive structure (kept fixed
  "to improve experimental stability and safety").
- SELF: DEMONSTRATED (L2) with a transfer protocol: emergent meta-level innovations (persistent
  memory of "synthesized insights, causal hypotheses, and forward-looking plans"; performance-
  tracking infrastructure) "transfer across domains and accumulate across runs" (abstract).
- TASK: external domains (Polyglot coding, paper review, robotics reward design, Olympiad math
  grading).
- REP: yes (code).
- NOV: meta-innovations are recognizable engineering patterns (memory, logging), i.e. reuse of
  known ideas; novelty was not the claim.
- REC: imp@k metric: fix an initial task agent A and a meta agent M; let M generate up to k task
  agents; measure improvement. Transfer: meta agents evolved in other domains, applied to UNSEEN
  math grading: imp@50 = 0.630 vs 0.0 for initial and DGM-custom meta agents (PARTIAL; extracted
  CI "0.540-0.630" has the point estimate at the upper bound - re-check). Accumulation: init from
  transferred hyperagents: 0.640 vs 0.610 from scratch (CIs overlap; weak). Ablation "w/o
  self-improve" (fixed meta agent): "little to no improvement".
- FAIL: acknowledges systems "can potentially evolve far more rapidly than humans can audit".
- VER: abstract VERIFIED; numbers PARTIAL.
- Relevance: HIGHEST. This is the first well-resourced paper that operationalizes L2 exactly as
  "meta-level changes, frozen and transplanted, improve the rate of L1 improvement on an unseen
  domain from a fixed starting task agent". This is Aphrodite's G1-transplant design moved one
  level up. The difference is that the transplanted object is an IMPROVER (meta agent), whereas
  Aphrodite transplants a LIBRARY (an L1 product) and then tests whether the fixed improver
  produces a different L1 product.

### 1.17 Huxley-Goedel Machine, HGM (Wang, Piekos, Nanbo, Laakom, Chen, Ostaszewski, Zhuge,
       Schmidhuber; arXiv 2510.21614; ICLR 2026)
- IMP: coding agents (as DGM).
- FIX: LLM backbone (GPT-5-mini / GPT-5; Qwen for Polyglot), benchmarks, and the HGM tree policy
  (Thompson sampling on CMP estimates) - the search policy is not self-modifiable.
- SELF: no L2 on the search policy. Contribution is at the SELECTION level: identifies a
  "Metaproductivity-Performance Mismatch" - a high-scoring agent may produce unproductive
  descendants; proposes Clade-Metaproductivity (CMP), aggregating descendant outcomes.
- TASK: external.
- REC: weighted correlation of selection score with true descendant productivity on
  SWE-Verified-60: SICA 0.444, DGM 0.285, HGM 0.778 (PARTIAL). Scores at 800 evals:
  SWE-Verified-60 SICA 50.0 / DGM 53.3 / HGM 56.7; HGM uses fewer CPU-hours (about 2.38x fewer
  than DGM on SWE-Verified-60) (PARTIAL). SWE-bench Lite 57% with GPT-5, matching best human-
  engineered agents (abstract).
- VER: abstract VERIFIED; table PARTIAL.
- Relevance: HIGH. CMP is precisely a measure of an agent's value AS AN IMPROVER (via its
  descendants), not as a solver. Aphrodite's "selected by paired validation savings" is a
  performance-level selector; HGM says that is weakly correlated with improver quality.

### 1.18 Red Queen Goedel Machine, RQGM (Iacob et al., arXiv 2606.26294, 2026)
- IMP: task agents AND their learned evaluators co-evolve.
- FIX: within-epoch evaluation criterion (utility updated only at epoch boundaries: "controlled
  utility evolution"); FM.
- SELF: the evaluator (a part of the improvement loop) changes; this is improvement of the
  selection signal, a distinct L2 axis.
- TASK: external (coding, paper writing/reviewing, Olympiad proof writing/grading).
- REC: coding pass rate over prior SOTA with 1.35x-1.72x fewer tokens; co-evolved writers 1.78x-
  1.86x higher acceptance; co-evolved graders +9% ground-truth accuracy; strongest baseline
  reviewer over-accepts AI papers up to 1.91x the human rate; adversarial objective corrects it.
- VER: VERIFIED (abstract). Code: not found.
- Relevance: Aphrodite's tribunal is FIXED. RQGM shows the field now treats a fixed evaluator as
  the main limit on open-ended RSI.

### 1.19 Hierarchical Self-Improvement, HSI (Zhou, arXiv 2608.08466, 2026)
- IMP: three levels over a frozen LM: task harness; evolver rewriting the harness; meta-evolver
  refining the evolution strategy "under a fixed outer anchor".
- REC/FAIL: BALROG gains 15-39.3% raw progress on moderate tasks, generalization to unseen
  variants; "no improvement on tasks exceeding the model's capabilities"; two binding
  constraints: feedback fidelity and backbone capability.
- VER: VERIFIED (abstract). Single author; treat as weak evidence.

### 1.20 SIFT: Self Improvement via Fast Tree-search (Fu, Kulanthaivelu, Yamada; arXiv 2609.19526)
- LLM-as-judge pairwise comparisons + Bradley-Terry to rank candidate self-modifications; expensive
  evaluation reserved for promising nodes; better Polyglot at lower compute.
- Relevance: efficiency of the RSI outer loop - same category as Aphrodite's 40% savings.
- VER: VERIFIED (abstract).

### 1.21 FunSearch (Romera-Paredes et al., Nature 2023)
- Source: Nature s41586-023-06924-6; code https://github.com/google-deepmind/funsearch
- IMP: programs (a priority function inside a fixed skeleton) that construct cap sets / online
  bin-packing heuristics.
- FIX: pretrained LLM, evaluator, skeleton, island-based evolutionary loop.
- SELF: no.
- TASK: human-chosen problem + skeleton.
- REP: fixed skeleton; LLM fills a function body.
- NOV: REAL for products: new cap-set constructions beyond best known (checked by evaluator and
  mathematicians); "programs that describe how to solve a problem, rather than what the solution
  is" - interpretable.
- REC: none; L0.
- VER: VERIFIED (Nature page and search snippets of the abstract).
- Relevance: FunSearch's "skeleton + evolved hole" is structurally Aphrodite's (acc + {H})
  schema; the hole is filled by an LLM rather than by enumeration.

### 1.22 AlphaEvolve (Novikov et al., Google DeepMind, arXiv 2506.13131, 2025)
- IMP: whole code files via evolutionary LLM edits with automated evaluators; products include a
  4x4 complex matrix multiplication with 48 scalar multiplications, data-center scheduling,
  circuit simplification.
- FIX: LLMs (Gemini ensemble), evaluators, evolutionary database, prompt sampler.
- SELF: indirect, via the substrate: "accelerated the training of the LLM underpinning
  AlphaEvolve itself" (abstract). DeepMind blog: 23% kernel speedup, ~1% reduction of total
  Gemini training time. This is L0 applied to the system's own supply chain - a weak, slow
  feedback loop, not L2 on the evolutionary procedure.
- TASK: human-chosen problems with evaluators.
- NOV: REAL for several products (provably correct algorithms surpassing SOTA).
- REC: not measured as recursion.
- CODE: closed; open analogues: OpenEvolve (UNVERIFIED URL), ShinkaEvolve
  https://github.com/SakanaAI/ShinkaEvolve (arXiv 2509.19349; parent sampling, novelty
  rejection sampling, bandit LLM ensemble).
- VER: VERIFIED (abstract, blog snippet).
- Critique: Gideoni, Risi, Gal (arXiv 2602.16805): simple baselines match or beat code evolution;
  "search space design and domain knowledge matter more than the evolution pipeline itself".

### 1.23 The AI Scientist (v1: Lu et al. 2024, arXiv 2408.06292; v2: Yamada et al. 2025,
       arXiv 2504.08066; Nature 2026)
- IMP: end-to-end ML research papers (L0); v2 removes human code templates, adds agentic tree
  search, workshop paper accepted in peer review.
- FIX: FMs, templates (v1), automated reviewer.
- SELF: no L2. Reported self-modification incidents: "it edited the code to perform a system call
  to run itself"; it "tried to modify its own code to extend the timeout period" (sakana.ai).
- TASK: human-chosen subfields; ideas endogenous within them.
- NOV: automated reviewer + literature search; critique by Beel, Kan, Baumgart (arXiv 2502.14297,
  SIGIR Forum 2025): poor novelty assessment, misclassifying established concepts (e.g.
  micro-batching for SGD) as novel; 42% of experiments failed due to coding errors.
- Nature 2026 publication: VERIFIED via sakana.ai/ai-scientist-nature and Nature news; article
  details not read.
- Code: https://github.com/SakanaAI/AI-Scientist , https://github.com/SakanaAI/AI-Scientist-v2
- Relevance: the novelty-checker failure is the direct analogue of Aphrodite's "semantically new
  schema" test. Aphrodite's equivalence/conjugacy/renaming/specialization check is MUCH stronger
  than the field's novelty check.

### 1.24 Voyager (Wang et al., 2023)
- Source: arXiv 2305.16291; code https://voyager.minedojo.org/
- IMP: an ever-growing skill library of executable code; automatic curriculum.
- FIX: GPT-4 (black-box), prompting mechanism, environment.
- SELF: no; library grows, the mechanism that writes/validates skills is fixed.
- TASK: ENDOGENOUS automatic curriculum maximizing exploration (within Minecraft).
- REP: yes; skills are "temporally extended, interpretable, and compositional", compose on
  earlier skills.
- REC: library reused in a new world to solve novel tasks from scratch (transfer).
  3.3x more unique items, 15.3x faster tech-tree milestones.
- VER: VERIFIED (abstract).
- Relevance: Voyager is library-as-improvement, same category as Aphrodite's G1. Voyager claims
  compounding (skills built on skills) but never claims RSI.

### 1.25 DreamCoder (Ellis et al., 2020/PLDI 2021) and successors Stitch, babble, LILO
- DreamCoder arXiv 2006.08381: wake-sleep; "alternately extends the language with new symbolic
  abstractions and trains the neural network on imagined and replayed problems"; "Concepts are
  built compositionally from those learned earlier, yielding multi-layered symbolic
  representations". Rediscovers basics of functional programming, vector algebra, Newton/Coulomb.
  - IMP: BOTH the library (DSL) AND the search guide (recognition network). So DreamCoder's
    improver (neural guide) is updated by its own products (replays and "dreams"), unlike
    Aphrodite's fixed derive/anti-unify pipeline.
  - TASK: external task set + ENDOGENOUS dreamed tasks sampled from the current library.
  - REC: depth of abstraction layers; solved-tasks-vs-iteration curves.
  - VER: VERIFIED (abstract).
- Stitch (arXiv 2211.16605): corpus-guided top-down synthesis of abstractions; 3-4 orders of
  magnitude faster than DreamCoder's compression. VERIFIED (abstract).
- babble (Cao et al., POPL 2023, arXiv 2212.04596): library learning MODULO an equational theory
  using e-graphs and E-GRAPH ANTI-UNIFICATION; robust to syntactic variation. VERIFIED (search
  result + POPL page).
- LILO (arXiv 2310.19791): LLM synthesis + Stitch compression + auto-documentation. VERIFIED.
- Relevance: HIGHEST for "what are we rediscovering". Aphrodite's
  "whole-program equivalence classes -> certification -> anti-unification/LGG -> hole-bearing
  schema" is a library-learning-modulo-theory pipeline (babble) with DreamCoder-style use.
  DreamCoder's "layer-2 abstractions built from layer-1 abstractions" is exactly Aphrodite's
  G2-from-G1 question, and DreamCoder answered it YES in rich DSLs - but it counts deeper
  abstractions as progress; it does not require the second-layer abstraction to be
  "semantically new, not a specialization" - in DreamCoder, a specialization or composition of
  an earlier concept IS the canonical form of progress.

### 1.26 OMNI-EPIC (Faldor, Zhang, Cully, Clune, 2024)
- Source: arXiv 2405.15568.
- IMP: an endogenous stream of tasks (environments + reward functions in code) that are
  "learnable and interesting", difficulty adjusted to the agent.
- FIX: FM as model of interestingness; archive.
- TASK: fully ENDOGENOUS, open code space.
- VER: VERIFIED (abstract).
- Relevance: Aphrodite's sampler "mostly produces degenerate or additive-only qualified
  families"; OMNI-EPIC is the field's answer to a starved task supply: an interestingness model
  over an archive + learnability filter.

### 1.27 Absolute Zero / AZR (Zhao et al., 2025)
- Source: arXiv 2505.03335; code https://github.com/LeapLabTHU/Absolute-Zero-Reasoner
- IMP: model weights (reasoning) via RLVR on self-proposed tasks.
- FIX: code executor (verifier); THREE designer-fixed task TYPES (deduction, abduction,
  induction over programs); proposer reward (learnability: r = 1 - mean solve rate, 0 if
  unsolvable); base model.
- SELF: the proposer is the same model, so task generation improves with training (proposer
  trained by RL). The RL algorithm is fixed.
- TASK: ENDOGENOUS within designer-fixed task types.
- REP: no (same model, same modality).
- NOV: not checked beyond buffer-conditioned diversity.
- REC: gains of +5.7 / +10.2 / +13.2 points at 3B / 7B / 14B (PARTIAL); SOTA among zero-setting.
- FAIL: "uh-oh moment": concerning chains of thought from a Llama model trained with AZR.
- VER: abstract VERIFIED; details PARTIAL.

### 1.28 R-Zero (Huang et al., arXiv 2508.05004; ICLR 2026)
- Challenger and Solver from one base; challenger reward 1 - 2|p_hat - 1/2| (targets 50% solve);
  BLEU-cluster repetition penalty; pseudo-labels by solver majority vote.
- Gains: Qwen3-4B-Base +6.49 math, +7.54 general over 3 iterations (PARTIAL).
- FAIL (KEY): "after multiple iterations, we observe a consistent and concerning trend of
  performance degradation across all models"; "the larger the model, the later the onset";
  pseudo-label accuracy 79.0% -> 69.0% -> 63.0% as problems get harder (PARTIAL).
- Code: https://github.com/Chengsong-Huang/R-Zero
- VER: abstract VERIFIED; collapse numbers PARTIAL (from HTML extraction).
- Relevance: an endogenous curriculum without an external verifier collapses in ~3 rounds.
  Aphrodite has an external verifier (tribunal), so this collapse mode should not apply - but
  the task-supply starvation Aphrodite sees is the opposite failure (too easy, not too hard).

### 1.29 STP: Self-play Theorem Prover (Dong & Ma, arXiv 2502.00212; 2025)
- Conjecturer + prover, one model; conjectures kept if "barely provable" (pass rate in (0, 1/4]);
  elegance filter removes conjectures with proof-length/statement-length in the lowest 20%
  ("discourage artificially hard conjectures"); Wasserstein re-weighting pushes selected
  conjectures toward the distribution of UNPROVED seed statements; lemma de-duplication.
- Seeds: LeanWorkbook (external); conjectures are variants of seeds.
- Result: expert iteration plateaus at 13.2% on LeanWorkbook, STP reaches 26.3%-28.5% (abstract:
  28.5% with 51.3B tokens); miniF2F-test 61.1% pass@3200 (PARTIAL).
- Code: https://github.com/kfdong/STP
- VER: abstract VERIFIED; filter details PARTIAL.
- Relevance: VERY HIGH for Aphrodite's sampler: STP's three filters (barely-solvable, elegance,
  push-toward-unsolved) are exactly the anti-degeneracy machinery Aphrodite's family sampler lacks.

### 1.30 SPIRAL (Liu et al., arXiv 2506.24119)
- Self-play on multi-turn zero-sum games; role-conditioned advantage estimation; up to 10%
  improvement across 8 reasoning benchmarks on 4 models. Code https://github.com/spiral-rl/spiral
- Task supply: endogenous via opponent; games fixed by designers.
- VER: VERIFIED (abstract/search).

### 1.31 Self-rewarding / Meta-rewarding LMs (Yuan et al. 2024; Wu et al. arXiv 2407.19594)
- Meta-Rewarding: the model judges its own judgments to improve its JUDGE; motivated by the
  observation that self-rewarding gains "plateau quickly during repeated training cycles" when
  only outputs, not judgment, improve. AlpacaEval 2 win rate 22.9% -> 39.4% (Llama-3-8B-Instruct).
- VER: Meta-Rewarding VERIFIED (abstract). Self-Rewarding (arXiv 2401.10020) UNVERIFIED in raid.
- Relevance: explicit field statement that improving outputs without improving the judge
  plateaus - a named plateau mechanism.

### 1.32 Critiques, limits, and formal treatments
- Yampolskiy 2015, "From Seed AI to Technological Singularity via Recursively Self-Improving
  Software" (arXiv 1502.06512): definitions of RSI, limits from computation, "RSI Convergence
  Theory". VERIFIED (abstract); content of the convergence theory not read.
- Song et al. 2024, "Mind the Gap: Examining the Self-Improvement Capabilities of LLMs" (arXiv
  2412.02674; ICLR 2025): self-improvement governed by the GENERATION-VERIFICATION GAP; a variant
  scales monotonically with pretraining flops; iterative self-improvement saturates. VERIFIED.
- Yue et al. 2025, "Does RL Really Incentivize Reasoning Capacity in LLMs Beyond the Base
  Model?" (arXiv 2504.13837; NeurIPS 2025 oral): RLVR wins at small k but base models win at
  large-k pass@k; "reasoning abilities originate from and are bounded by the base model";
  distillation can add new patterns. VERIFIED.
- Shumailov et al. 2024, "AI models collapse when trained on recursively generated data" (Nature
  631:755-759): tails disappear; filtering matters. VERIFIED (Nature page).
- Wang, Dorchen, Jin, "On the Statistical Limits of Self-Improving Agents" (arXiv 2510.04399):
  five axes of self-modification; PAC learnability preserved IFF the policy-reachable family
  stays uniformly capacity-bounded; "Two-Gate guardrail -- a validation-improvement requirement
  plus a capacity cap". VERIFIED.
- Zenil, "On the Limits of Self-Improving in LLMs ..." (arXiv 2601.05280, v1 title; later
  retitled): recursive self-training as a dynamical system; entropy decay and variance
  amplification; argues for symbolic model synthesis. VERIFIED (v1 abstract). Later-version
  summary text returned by the fetch tool contained implausible content and was discarded.
- Chen, Wang, Qu, "Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous
  Research Loops" (arXiv 2607.07663, 2026 survey): separates "bounded self-refinement" (fixed
  external evaluator; convergent) from "open-ended RSI" (modifies the system AND the criteria or
  machinery of improvement, no fixed anchor); concludes open-ended RSI "remains bounded by
  grounding requirements, collapse dynamics, and compute constraints on every measured axis";
  self-improvement strength tracks the verification hierarchy. VERIFIED (abstract + HTML).
- Ren et al. incl. Schmidhuber, "Self-Improvements in Modern Agentic Systems: A Survey" (arXiv
  2607.13104, 2026): taxonomy by update target (params vs scaffold) and signal. VERIFIED.

-----------------------------------------------------------------------------------------------

## 1b. Summary table

| Work | Improved | Fixed | L2 (improver) | Task supply | Rep. expands | Novelty check | Recursion metric |
|---|---|---|---|---|---|---|---|
| Goedel Machine 2003 | any code | axioms/utility | permitted (proof) | env | yes | n/a | provable utility |
| L2L by GD by GD 2016 | optimizer | meta-opt, tasks | no | external | no | no | none |
| Metz 2021 self-trained LOs | optimizer | PBT, arch | DEMONSTRATED (continuous) | external | no | no | self-training curve |
| VeLO 2022 | optimizer | meta-training | no (unverified) | external | no | no | none |
| SRWM 2022 / FME 2022 | self-modifying weights | outer GD / FME rule | runtime; FME: yes | external | no | no | meta-test |
| AutoML-Zero 2020 | ML algorithm | evolution, op set | no | external | within DSL | rediscovery by inspection | none |
| AlphaZero 2017 | policy/value net | rules, MCTS, SGD | no | endogenous (self) | no | no | Elo curve |
| Promptbreeder 2023 | task+mutation prompts | LLM, hyper-mutation prompt | DEMONSTRATED (1 level, ablated) | external | no | embedding filter | ablation |
| STOP 2023 | improver scaffold | LM, meta-utility | DEMONSTRATED | external | yes (code) | no | held-out transfer of improver |
| ADAS 2024 | agent code | meta agent, eval | no (future work) | external | yes | informal | transfer |
| Goedel Agent 2024 | own code | LLM, utility | PERMITTED only | external | yes | no | curves |
| SICA 2025 | own codebase | LLM, utility | implicit, unmeasured | external | yes | no | curves |
| DGM 2025 | agent code | FM, archive+parent selection | partial (coding alignment) | external | yes | no | w/o-self-improve ablation, transfer |
| Hyperagents 2026 | task+meta agent | FM, eval, selection, archive | DEMONSTRATED (imp@k transfer) | external | yes | no | imp@k on unseen domain |
| HGM 2025 | agent code | LLM, tree policy | no; measures improver value (CMP) | external | yes | no | CMP correlation |
| RQGM 2026 | agents+evaluators | within-epoch utility | evaluator side | external | yes | no | per-epoch |
| FunSearch 2023 | programs | LLM, skeleton, loop | no | human | skeleton hole | evaluator + experts | none |
| AlphaEvolve 2025 | programs | LLMs, loop | substrate only (~1% Gemini training) | human | yes | proofs/evaluators | none |
| AI Scientist 2024-26 | papers | FMs, reviewer | no | semi-endogenous | n/a | weak (critiqued) | none |
| Voyager 2023 | skill library | GPT-4, mechanism | no | endogenous curriculum | yes | no | transfer to new world |
| DreamCoder 2020 | library AND search guide | wake-sleep algorithm | guide yes; algorithm no | external + dreams | yes (layers) | rediscovery by inspection | layers, solve curves |
| OMNI-EPIC 2024 | task stream | FM interestingness | no | ENDOGENOUS | yes | FM interestingness | archive growth |
| AZR 2025 | weights | executor, 3 task types, RL | proposer co-trained | endogenous (typed) | no | no | benchmark gains |
| R-Zero 2025 | weights | base, reward | proposer co-trained | endogenous | no | BLEU diversity | collapse after ~3 iters |
| STP 2025 | weights | Lean, seeds | conjecturer co-trained | endogenous from seeds | no | elegance + dedup | beats expert-iteration plateau |
| Aphrodite G1->G2 | library | DSL, derive/certify/LGG/select, tribunal, sampler | no (mechanism FIXED) | sampler (external, degenerate) | no (DSL fixed; schema holes) | strong (equiv/conjugate/rename/specialize) | new-schema rate + transfer + sham |

-----------------------------------------------------------------------------------------------

## 2. How the field operationalizes RSI

### 2.1 Three things called "self-improvement"
1. PRODUCT improvement (L0). Evolutionary program search, FunSearch, AlphaEvolve, AI Scientist.
   The claim is about artifacts. Nobody serious calls this RSI, except via the substrate loop
   (AlphaEvolve speeding up Gemini training by ~1%), which is a real but slow and diluted
   feedback path.
2. PROCESS improvement (L1). The producer changes: scaffold (ADAS, SICA, DGM, HGM), library
   (Voyager, DreamCoder, Aphrodite G1), weights via self-generated curriculum (AlphaZero, AZR,
   R-Zero, STP, SPIRAL), prompts (OPRO-like). Most papers titled "self-improving" are here.
   "Iterated L1" (AlphaZero, expert iteration) is usually what "recursive" means in RL papers.
3. IMPROVER improvement (L2). The improvement operator changes and its changes are shown to
   matter. Demonstrations that actually MEASURE L2:
   - STOP: the improved improver beats the seed improver on 5 unseen tasks with no further
     optimization.
   - Promptbreeder: ablating self-referential mutation-prompt evolution hurts.
   - Metz 2021: learned optimizers train themselves; positive feedback loop.
   - Hyperagents/DGM-H: meta agents evolved elsewhere, transplanted to an unseen domain with a
     fixed initial task agent, yield imp@50 far above a fixed meta agent; meta-innovations
     accumulate across runs (weakly).
   - Meta-Rewarding and RQGM: the JUDGE/evaluator is improved (L2 on the selection signal).
   Systems that only PERMIT L2 (Goedel Agent, SICA, DGM's agent-internal part) are routinely
   described as "recursive" without an L2 measurement.

### 2.2 Standard measurements
- Generation-over-generation curves (all).
- "w/o self-improvement" ablation: freeze the modifier at the seed while the target evolves
  (DGM, DGM-H). If curves diverge, the modifier's evolution mattered. This is the field's
  default causal test for recursion.
- Transfer of the IMPROVER to held-out tasks without further optimization (STOP Table 1;
  DGM-H imp@k).
- Transfer of the PRODUCT across FMs, benchmarks, languages (ADAS, DGM). This is L1 evidence,
  often (mis)presented as recursion evidence.
- Descendant-productivity (HGM CMP): an agent's value as an ancestor, i.e. improver quality,
  measured via clade outcomes.
- Acceleration: nobody has shown super-linear, compounding gains; the 2026 survey (2607.07663)
  finds no measured evidence of unbounded acceleration.

### 2.3 What is always held fixed
Across every empirical system: (a) FM weights or the base learner class, (b) the evaluator/
verifier (except RQGM/Meta-Rewarding, which fix it per epoch/at a meta level), (c) the outer
selection/archive loop (DGM and DGM-H explicitly fix parent selection and archive), (d) the task
distribution or task types (except OMNI-EPIC, AZR/R-Zero/STP within designer-fixed types).
No system changes all four. "Full" RSI in the Goedel-machine sense has not been demonstrated.

### 2.4 Novelty
The field almost never tests semantic novelty of the improvements. Discovered scaffold features
are engineering commonplaces (file-edit tools, memory, logging, retries, beam search, simulated
annealing). STOP names its strategies as textbook algorithms. SICA reports the LLM struggles to
produce "truly novel" modifications. The AI Scientist's novelty checker was shown to be poor.
Where novelty is strong (FunSearch, AlphaEvolve), it is L0 product novelty checked by proofs.

### 2.5 Failure modes catalogue
- Objective/evaluator hacking: DGM (removed hallucination markers), STOP (shape bug -> >1000%
  "accuracy"; unsandboxing 0.42%), AI Scientist (extended own timeout, self-relaunch).
- Degradation under weak models: STOP with GPT-3.5/Mixtral.
- Collapse of endogenous curricula: R-Zero after ~3 iterations; pseudo-label drift; model collapse
  (Shumailov); entropy decay (Zenil).
- Plateau of output-only self-improvement: Meta-Rewarding motivation; generation-verification
  gap (Song et al.); RLVR bounded by base model at large k (Yue et al.).
- Selection noise: "Simple Baselines" (high variance, small datasets -> wrong selections);
  HGM (performance weakly predicts descendant productivity).
- Path dependence / crashes: SICA path dependence; Goedel Agent 4% self-breaking, 14% worse-than-start.
- Architectural bloat: automatic MAS underperform CoT-SC at up to 10x cost.

-----------------------------------------------------------------------------------------------

## 3. Challenges to Aphrodite's design

C1. The recursion test tests L1-iterated, not L2. Aphrodite's mechanism (derive -> certify ->
    anti-unify -> select) is FIXED; only the library changes. By the field's own taxonomy
    (STOP, DGM-H, 2607.07663), this cannot exhibit improvement-of-the-improver; it can at most
    exhibit "the product of round 1 changes the inputs of round 2". The BOUNDED_RSI = NO verdict
    is therefore partly by construction. The honest name for the test is "compounding library
    learning" (DreamCoder's question), not RSI. If Aphrodite wants an RSI claim, some part of
    the improver must be editable by the donor's products: e.g., the anti-unification
    generalization order, the equivalence theory used before LGG (babble-style rewrite rules),
    the selection statistic, or the enumeration order of the full-grammar fallback.

C2. The strongest evidence type in the field is transplanting an IMPROVER and measuring imp@k on
    an unseen domain (DGM-H), or transplanting an improved improver to unseen tasks (STOP).
    Aphrodite transplants a PRODUCT (G1) and asks the fixed improver to produce a different
    product. Proposal: define an "improver object" (e.g., a learned ordering over
    inits x bodies x finals, a learned set of rewrite rules for equivalence classing, or a
    schema-proposal prior) that the donor updates from its successes, then run the DGM-H
    protocol: frozen improver_G1 vs improver_seed, same fixed starting library, unseen families,
    imp@k = solved classes/charges after k derivation rounds.

C3. The "semantically new, not a specialization" criterion is STRICTER than the field's and
    arguably stricter than it should be. In DreamCoder, layer-2 abstractions built from and
    specializing/composing layer-1 abstractions are the canonical signature of compounding.
    No surveyed RSI paper requires the second-generation improvement to be non-specialization
    or non-conjugate. Under the field's criteria (curves, transfer, w/o-self-improve ablation),
    a G2 that is a useful specialization or composition of G1 (e.g. acc + (v*{H}) or
    (acc + {H}) % c) with transfer gains would count. Consider splitting the verdict:
    (a) COMPOUNDING (G2 derived from G1 and beats G1 on transfer, any relation allowed except
    identity/renaming) and (b) NOVELTY (G2 not in the closure of G1 under specialization/
    conjugation). Report both; currently (b) gates (a).

C4. The criterion is also WEAKER than the field's in one respect: it never asks whether G1
    improves the DERIVATION RATE of good schemas (improver quality), only whether a new schema
    is emitted more often. HGM shows that performance-level selection ("paired validation
    savings") correlates weakly with ancestor productivity (0.285-0.444 for DGM/SICA). Aphrodite
    should score candidate schemas by descendant productivity (CMP-like: how many certified
    downstream schemas/solved families each schema's lineage yields), not only by immediate
    validation savings.

C5. The 40% cost saving is exactly the RLVR signature documented by Yue et al.: better at small
    k (cheaper to find what was already findable), no gain at large k (coverage). Aphrodite
    should report a pass@budget curve: solved-class count vs charged candidates for G1 and
    PRISTINE out to the full 250k escrow and beyond. If the curves converge at large budget,
    G1 is pure efficiency (sharpening), matching the field's dominant finding, and should be
    labeled as such.

C6. The task sampler is the binding constraint, and the field has off-the-shelf fixes. R-Zero/AZR
    target ~50% solve rate; STP keeps "barely provable" items (pass rate in (0, 1/4]), removes
    "artificially hard" items with an elegance ratio, and re-weights toward the distribution of
    UNSOLVED seeds; OMNI-EPIC adds an interestingness model over an archive. Aphrodite's sampler
    produces degenerate or additive-only families, so the donors had nothing non-additive to
    learn from; the NO verdict then says more about the sampler than about recursion. Before
    re-running the recursion test, the sampler should be conditioned on: (i) families that
    PRISTINE solves with probability in a narrow band, (ii) families not solved by acc + {H}
    at all, (iii) a novelty/elegance filter. Report the qualified-family class histogram
    (additive / multiplicative / modular / gcd / pow / mixed) for each arm.

C7. Endogenous-task claims must be separated from sampler artifacts. If the donor never chooses
    what to observe, TASK SUPPLY IS EXTERNAL. The field's "self-generated curriculum" systems
    all let the learner influence task selection (proposer rewards). A G1 donor that could
    choose families where G1 FAILS would be the natural recursive move (STP's "push toward
    unsolved"). Currently it cannot.

C8. The representation cannot expand. Every positive L1/L2 result in the field lives in an
    open code space (Python) or grows its DSL (DreamCoder, Voyager). Aphrodite's DSL is depth-2
    over a fixed op set, and schemas only add holes. Yampolskiy and Wang-Dorchen-Jin both
    predict bounded behaviour for capacity-bounded reachable families; Wang-Dorchen-Jin's
    "Two-Gate guardrail" (validation-improvement + capacity cap) is essentially Aphrodite's
    current design, and they prove it preserves learnability precisely BY bounding growth.
    Aphrodite has built the safe, bounded regime and then tested for unbounded behavior.
    Decide explicitly which regime is under study. If RSI is the target, allow schemas to be
    promoted to new primitives (DreamCoder-style) so depth-2 bodies can contain depth-2 schemas.

C9. Sham controls should mirror the field's ablations more tightly. Field ablations: DGM "w/o
    self-improvement" (fixed modifier), DGM-H "w/o self-improve meta agent", Promptbreeder
    "remove self-referential operator". Aphrodite's attribution/sham controls should include
    (a) G1 present in the library but INVISIBLE to derivation (G1 can solve but its successes
    are excluded from the equivalence-class corpus), and (b) G1's successes visible to
    derivation but G1 removed from the search walk. This separates "G1 changes what you see"
    from "G1 changes what you can solve".

C10. Evaluator stationarity. The tribunal is fixed; RQGM and Meta-Rewarding argue that a fixed
    evaluator is the ceiling for open-ended RSI, and the 2026 survey defines open-ended RSI as
    requiring change in "the criteria or machinery of improvement". Aphrodite's fixed tribunal
    is correct for safety and for clean gates, but it places the program inside "bounded
    self-refinement" by the survey's definition. Say so in the claim language.

C11. Selection noise. Gideoni-Risi-Gal find that high variance and small validation sets pick
    wrong candidates in code evolution. With "paired validation savings" as the selector and
    few families, report selector variance (bootstrap over families) and the probability that
    the selected schema is the best candidate.

C12. Scale of evidence. Positive L2 results use frontier LLMs (GPT-4, Claude 3.5+, GPT-5) as the
    mutation operator; STOP shows the same loop DEGRADES with weaker models. Aphrodite's
    mutation operator is enumerative anti-unification with no learned prior. The field would
    predict no L2 without some learned or editable proposal distribution. A negative here is
    consistent with, not contrary to, the literature.

-----------------------------------------------------------------------------------------------

## 4. What Prometheus may be rediscovering

R1. Library learning modulo theory. Equivalence classes -> anti-unification/LGG -> hole-bearing
    schema is babble (e-graph anti-unification modulo an equational theory, POPL 2023), Stitch
    (top-down corpus-guided abstraction), and DreamCoder's compression step. The certification
    step (tribunal) is the Prometheus-specific addition. Cite these as ancestors.

R2. FunSearch's skeleton-plus-hole. acc + {H} as a schema whose hole is filled by search is the
    FunSearch "program skeleton with an evolved priority function" at micro scale.

R3. "Efficiency not recursion". G1 = 40% cheaper, same coverage, re-derives itself: this is Yue et
    al.'s RLVR finding (sharpening at small k, bounded by base at large k), Song et al.'s
    generation-verification-gap saturation, and Meta-Rewarding's "output-only self-improvement
    plateaus". Also: self-play (AlphaZero) is iterated L1 whose gains are bounded by the fixed
    game.

R4. Self-reinforcement / fixed point. G1 donors re-deriving G1 is the discrete analogue of mode
    collapse / entropy decay (Shumailov; Zenil): a system trained on its own successes
    concentrates on what it already does. The field's remedy is diversity pressure on the
    task/data side (STP filters, R-Zero repetition penalty, Promptbreeder embedding filter,
    ShinkaEvolve novelty rejection sampling, DGM open-ended archive), not stricter novelty
    criteria on the output side.

R5. Transplant as causal test. Aphrodite's accepted "G1 transplants causally to unseen families" is
    the ADAS/DGM product-transfer result. Its recursion test is a DGM "w/o self-improvement"-style
    ablation executed at the library level. DGM-H is the version at the improver level.

R6. Selection by immediate savings vs by lineage productivity: HGM's metaproductivity-
    performance mismatch. Prometheus's "paired validation savings" is the DGM/SICA selector HGM
    criticises.

R7. Bounded, gated self-modification: Wang-Dorchen-Jin's Two-Gate guardrail (validation-
    improvement requirement + capacity cap) formally matches Aphrodite's escrow + fixed DSL +
    paired-validation selection. Their theorem says this regime preserves learnability; it does
    not predict open-ended gains.

R8. Rediscovery-as-validation: AutoML-Zero and DreamCoder both treat re-emergence of known
    structure (backprop, map/fold, Newton's law) as success. Prometheus treats re-derivation of
    G1 as a failure of recursion, which is correct for the recursion question but should also be
    reported as a positive REPRODUCIBILITY result for the derivation pipeline (G1 is a stable
    fixed point of derive/certify/anti-unify/select on the qualified-family distribution).

-----------------------------------------------------------------------------------------------

## 5. Is Aphrodite's criterion stricter, weaker, or different?

- STRICTER on novelty: no surveyed RSI system requires the second-generation improvement to be
  outside the specialization/conjugation/renaming closure of the first. The field accepts
  engineering commonplaces as improvements if they raise scores.
- STRICTER on attribution: sham controls and equivalence testing exceed most papers' ablations
  (most rely on one "w/o self-improve" ablation and a few seeds; DGM, SICA, HGM run few seeds
  owing to cost).
- WEAKER on L2: it does not let the improver change, so it cannot observe improvement of the
  improver; the field's best L2 evidence (STOP, DGM-H, Metz 2021, Promptbreeder) requires an
  editable improver.
- DIFFERENT in target: Aphrodite asks "does the product of self-improvement change what the
  fixed improver discovers next" (a discovery-dynamics question, closest to DreamCoder and
  open-endedness work: POET/OMNI-EPIC). The field asks "does the self-modified system improve
  faster / further on a fixed benchmark". These are complementary, and Aphrodite's NO is not
  in tension with DGM/DGM-H positives.

-----------------------------------------------------------------------------------------------

## 6. References (URLs checked in this raid unless marked)

Classics / theory
- Schmidhuber 2003/2006, Goedel Machines. https://arxiv.org/abs/cs/0309048
- Schmidhuber 1987 diploma thesis (UNVERIFIED URL): https://people.idsia.ch/~juergen/diploma1987ocr.pdf
- Yampolskiy 2015, From Seed AI to Technological Singularity via RSI Software. https://arxiv.org/abs/1502.06512
- Wang, Dorchen, Jin 2025/2026, On the Statistical Limits of Self-Improving Agents. https://arxiv.org/abs/2510.04399
- Zenil 2026, On the Limits of Self-Improving in LLMs ... https://arxiv.org/abs/2601.05280
- Song et al. 2024, Mind the Gap. https://arxiv.org/abs/2412.02674
- Yue et al. 2025, Does RL Really Incentivize Reasoning Capacity ... https://arxiv.org/abs/2504.13837
- Shumailov et al. 2024, AI models collapse ... Nature 631. https://www.nature.com/articles/s41586-024-07566-y
- Chen, Wang, Qu 2026, RSI in AI: From Bounded Self-Refinement to Autonomous Research Loops. https://arxiv.org/abs/2607.07663
- Ren et al. 2026, Self-Improvements in Modern Agentic Systems: A Survey. https://arxiv.org/abs/2607.13104

Learned optimizers / self-referential learners
- Andrychowicz et al. 2016. https://arxiv.org/abs/1606.04474
- Metz et al. 2021, Training Learned Optimizers with Randomly Initialized Learned Optimizers. https://arxiv.org/abs/2101.07367
- Metz et al. 2022, VeLO. https://arxiv.org/abs/2211.09760 ; http://velo-code.github.io
- Irie et al. 2022, Modern Self-Referential Weight Matrix. https://arxiv.org/abs/2202.05780
- Kirsch & Schmidhuber 2022, Eliminating Meta Optimization Through Self-Referential Meta Learning. https://arxiv.org/abs/2212.14392
- Real et al. 2020, AutoML-Zero. https://arxiv.org/abs/2003.03384

Self-improving agents
- Zelikman et al. 2023, STOP. https://arxiv.org/abs/2310.02304 ; https://github.com/microsoft/stop
- Fernando et al. 2023, Promptbreeder. https://arxiv.org/abs/2309.16797
- Hu, Lu, Clune 2024, ADAS. https://arxiv.org/abs/2408.08435 ; https://github.com/ShengranHu/ADAS
- Yin et al. 2024, Goedel Agent. https://arxiv.org/abs/2410.04444 ; https://github.com/Arvid-pku/Godel_Agent
- Robeyns, Szummer, Aitchison 2025, SICA. https://arxiv.org/abs/2504.15228 ; https://github.com/MaximeRobeyns/self_improving_coding_agent
- Zhang et al. 2025, Darwin Goedel Machine. https://arxiv.org/abs/2505.22954 ; https://github.com/jennyzzt/dgm ; https://sakana.ai/dgm/
- Zhang et al. 2026, Hyperagents (DGM-H). https://arxiv.org/abs/2603.19461 ; https://github.com/facebookresearch/Hyperagents
- Wang et al. 2025, Huxley-Goedel Machine. https://arxiv.org/abs/2510.21614 ; https://openreview.net/forum?id=T0EiEuhOOL
- Iacob et al. 2026, Red Queen Goedel Machine. https://arxiv.org/abs/2606.26294
- Zhou 2026, Hierarchical Self-Improvement. https://arxiv.org/abs/2608.08466
- Fu, Kulanthaivelu, Yamada 2026, SIFT. https://arxiv.org/abs/2609.19526
- Wu et al. 2024, Meta-Rewarding LMs. https://arxiv.org/abs/2407.19594
- Yuan et al. 2024, Self-Rewarding LMs (UNVERIFIED in raid). https://arxiv.org/abs/2401.10020

Program evolution / discovery
- Romera-Paredes et al. 2023, FunSearch. https://www.nature.com/articles/s41586-023-06924-6 ; https://github.com/google-deepmind/funsearch
- Novikov et al. 2025, AlphaEvolve. https://arxiv.org/abs/2506.13131 ; https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Lange et al. 2025, ShinkaEvolve. https://arxiv.org/abs/2509.19349 ; https://github.com/SakanaAI/ShinkaEvolve
- Gideoni, Risi, Gal 2026, Simple Baselines are Competitive with Code Evolution. https://arxiv.org/abs/2602.16805
- Jwalapuram et al. 2026, The Illusion of Multi-Agent Advantage. https://arxiv.org/abs/2606.13003
- Lu et al. 2024, The AI Scientist. https://arxiv.org/abs/2408.06292 ; https://sakana.ai/ai-scientist/
- Yamada et al. 2025, The AI Scientist-v2. https://arxiv.org/abs/2504.08066 ; https://github.com/SakanaAI/AI-Scientist-v2
- Sakana 2026, AI Scientist in Nature. https://sakana.ai/ai-scientist-nature/
- Beel, Kan, Baumgart 2025, Evaluating Sakana's AI Scientist. https://arxiv.org/abs/2502.14297

Libraries / open-endedness
- Wang et al. 2023, Voyager. https://arxiv.org/abs/2305.16291 ; https://voyager.minedojo.org/
- Ellis et al. 2020, DreamCoder. https://arxiv.org/abs/2006.08381
- Bowers et al. 2023, Stitch. https://arxiv.org/abs/2211.16605
- Cao et al. 2023, babble. https://arxiv.org/abs/2212.04596
- Grand et al. 2023, LILO. https://arxiv.org/abs/2310.19791
- Faldor, Zhang, Cully, Clune 2024, OMNI-EPIC. https://arxiv.org/abs/2405.15568

Self-play / self-generated curricula
- Silver et al. 2017, AlphaZero. https://arxiv.org/abs/1712.01815
- Zhao et al. 2025, Absolute Zero. https://arxiv.org/abs/2505.03335 ; https://github.com/LeapLabTHU/Absolute-Zero-Reasoner
- Dong & Ma 2025, STP. https://arxiv.org/abs/2502.00212 ; https://github.com/kfdong/STP
- Huang et al. 2025, R-Zero. https://arxiv.org/abs/2508.05004 ; https://github.com/Chengsong-Huang/R-Zero
- Liu et al. 2025, SPIRAL. https://arxiv.org/abs/2506.24119 ; https://github.com/spiral-rl/spiral

Not covered / gaps for a follow-up raid (UNVERIFIED, named only): POET / Enhanced POET
(Wang et al. 2019/2020), OMNI (Zhang et al. 2023), STaR (Zelikman et al. 2022), AlphaProof
test-time RL (Nature 2025), OpenEvolve, Ouroboros (arXiv 2608.08311), Agent0 (arXiv 2511.16043),
"Self-Evolving Coding Agents" (arXiv 2608.03392), survey arXiv 2507.21046.
