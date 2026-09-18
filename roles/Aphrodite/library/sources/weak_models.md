# Weak models in self-improvement, search and RSI loops: source notes

Currency: 2026-09-18
Compiled by: research librarian session for Aphrodite (web tools, 2026-09-18)
Question family: can small, weak models actually be used in self-improvement / search / RSI loops
(as proposers, mutators, workers, verifiers or swarm members), and under what conditions?

Status legend:
- VERIFIED: title/authors/claims checked this session against the arXiv abstract page, arXiv HTML,
  or the paper PDF text. Most numbers were relayed by a summarizing fetch tool; the Stroebl et al.
  numbers and equations were read from the raw PDF text. Spot-check any number before citing it in a paper.
- PARTIAL: the paper exists and the core claim was seen, but some detail (authors, a number, a
  condition) comes only from a search-engine snippet or was not visible on the fetched page.
- FROM MEMORY: not checked this session. Do not treat as evidence.
- NOT FOUND: searched for, not located.

Notation used throughout (ASCII only):
- p = per-sample solve rate of the generator on a given task (pass@1 on that task)
- c = verifier completeness = P(verifier accepts | sample correct)
- q = verifier false-accept rate = P(verifier accepts | sample incorrect) = 1 - s (s = soundness)
- K = number of samples drawn

---

## 1. Repeated sampling + verification with small models

### 1.1 Brown et al. 2024, "Large Language Monkeys: Scaling Inference Compute with Repeated Sampling"
- Citation: Bradley Brown, Jordan Juravsky, Ryan Ehrlich, Ronald Clark, Quoc V. Le, Christopher Re,
  Azalia Mirhoseini. arXiv:2407.21787. https://arxiv.org/abs/2407.21787
- Status: VERIFIED (abstract + HTML)
- Mechanism: draw K independent samples; "coverage" = fraction of problems solved by any sample.
  Coverage scales log-linearly with K over four orders of magnitude; fit as an exponentiated power
  law, coverage ~ exp(a * K^b).
- Model sizes: Pythia-160M upward, Gemma-2B, Llama-3-8B-Instruct, Llama-3-70B, DeepSeek-Coder-V2-Instruct.
- Numbers:
  - SWE-bench Lite, DeepSeek-Coder-V2-Instruct: 15.9% at 1 sample -> 56% at 250 samples (prior
    single-sample SOTA 43%).
  - Cost: 5 samples of DeepSeek-Coder-V2-Instruct solve 29.62% for $10.80 vs one GPT-4o attempt at
    24% for $39 (about 3.6x more expensive).
  - Gemma-2B on CodeContests: coverage 0.02% (1 sample) -> 7.1% (10,000 samples).
  - Pythia-160M on MATH: pass@1 0.27% -> pass@10k 57%.
  - FLOPs-matched: Llama-3-8B-Instruct gets higher coverage than Llama-3-70B at equal FLOPs on MATH,
    GSM8K and MiniF2F; the opposite holds on CodeContests.
  - Selection failure: Llama-3-8B on MATH at 10,000 samples: coverage 98.44% but majority voting
    only 41.41%. Majority vote and reward-model selection plateau around ~100 samples on GSM8K/MATH.
- Worked when: an automatic, exact verifier exists (unit tests for SWE-bench/CodeContests, Lean for
  MiniF2F). Coverage is an oracle quantity.
- Failed when: no exact verifier; majority vote and reward models cannot convert coverage into accuracy.
- Librarian caution (not a paper claim): coverage on numeric-answer tasks with tiny models (Pythia-160M
  57% on MATH) may be inflated by answer guessing; treat pass@10k on short-answer tasks as an upper bound.

### 1.2 Stroebl, Kapoor, Narayanan, "Inference Scaling fLaws: The Limits of LLM Resampling with Imperfect Verifiers" (v3 title: "The Limits of Inference Scaling Through Resampling"), ICLR 2026
- Citation: Benedikt Stroebl, Sayash Kapoor, Arvind Narayanan. arXiv:2411.17501 (v3, 26 Mar 2026).
  https://arxiv.org/abs/2411.17501 ; code: https://github.com/benediktstroebl/inference-scaling-limits
- Status: VERIFIED (abstract and PDF text read directly)
- Mechanism: resample until a sample passes an imperfect verifier. Resampling cannot reduce the
  probability that a passing sample is a false positive, so accuracy has an upper bound independent
  of compute.
- Setup: original HumanEval / MBPP unit tests used as the (imperfect) verifier; HumanEval+ / MBPP+
  extended tests used as ground truth. >= 200 samples/task on HumanEval+ (1,000 for Command Light),
  50 samples/task on MBPP+.
- Models: Llama 3.1 8B and 70B, Code Llama 7B and 13B, GPT-4o, GPT-3.5, Cohere Command and Command
  Light, plus Phi-3, Mistral, Vicuna, CodeT5p, CodeGen variants (model list via fetch summary).
- Key findings (quoted/paraphrased from PDF):
  - "Weaker models exhibit a higher probability of producing false positives compared to stronger
    models ... This probability scales inversely with the true capability." The relation is roughly
    linear across model families.
  - Criterion: if P_strong(Correct) > P_weak(Correct | Pass Verifier), the weak model cannot match a
    single call of the strong model "no matter how big the compute budget". No model below GPT-4o's
    line matched it by resampling.
  - The effect is driven largely by a subset of tasks with poor unit tests.
  - Optimal K with a cost for false positives (benefit 1 for a true positive, cost ratio 0/1/2/4/8):
    "at a cost-benefit ratio of 4, the optimal number of samples is K <= 5 for all four models"
    (Llama-3.1 and Code Llama families). Headline: optimal attempts "often fewer than 10".
    Theory model (Appendix C, Llama 3.1 8B parameters): optimal K <= 3; at cost ratio 10, optimal
    K = 0 for almost all models.
  - False-positive rate rises with K because task difficulty is bimodal: easy tasks resolve in a
    few draws, and the tasks still unsolved after many draws are the hard ones where false positives dominate.
  - False-positive code is lower quality (naming conventions, line length, comments).
- Appendix C model (verbatim structure, symbols spelled out): tasks easy (T1) or hard (T2) with
  per-sample correct rates r1 > r2; verifier completeness c, soundness s.
  - Rejection probability per sample: rho_i = (1 - c) * r_i + s * (1 - r_i)
  - Per-attempt true-positive prob: P_TP,Ti = c * r_i
  - Per-attempt false-positive prob: P_FP,Ti = (1 - r_i) * (1 - s)
  - Posterior over task type updated after each rejection; expected value EV_k summed over k to get
    reward(K); K_opt maximizes it.
- DERIVED here (librarian algebra from the eqs above, single task type, i.i.d. samples, not stated as
  a closed form in the paper): the first sample that passes is correct with probability
      A = c*p / (c*p + q*(1 - p))          (q = 1 - s)
  independent of K. As K -> infinity, accuracy on that task -> A (not 1). Target precision t needs
      p / (1 - p) >= (t / (1 - t)) * (q / c).
  Example numbers (c = 1): p = 0.05, q = 0.01 -> A = 0.84; p = 0.01, q = 0.01 -> A = 0.50;
  p = 0.001, q = 0.01 -> A = 0.09. The per-sample solve rate must exceed the false-accept
  rate by a margin, and weak models make this worse because their q is empirically higher.
- Worked when: easy tasks, good test coverage, low cost of false positives.
- Failed when: weak model + incomplete tests; high cost of false positives; large K on hard residual tasks.

### 1.3 Chen et al. 2024, "Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems"
- Citation: arXiv:2403.02419. https://arxiv.org/abs/2403.02419. Authors (FROM MEMORY): Lingjiao Chen,
  Jared Quincy Davis, Boris Hanin, Peter Bailis, Ion Stoica, Matei Zaharia, James Zou.
- Status: PARTIAL (abstract verified; authors from memory)
- Mechanism: Vote and Filter-Vote over N LM calls.
- Finding: performance is non-monotone in N: "more LM calls lead to higher performance on 'easy'
  queries, but lower performance on 'hard' queries". Mixed tasks show rise-then-fall. An analytical
  model predicts the optimal N from a small number of samples.
- Condition: majority vote only helps on items where the correct answer is the per-item plurality
  (roughly p > max wrong-answer mass); on items where a wrong answer is modal, more votes lock in the error.

### 1.4 Saad-Falcon et al. 2025, "Shrinking the Generation-Verification Gap with Weak Verifiers" (Weaver), NeurIPS 2025
- Citation: arXiv:2506.18203. https://arxiv.org/abs/2506.18203. Authors (FROM MEMORY): Jon Saad-Falcon et al.
- Status: PARTIAL (abstract verified; authors from memory)
- Mechanism: weighted ensemble of many weak verifiers (LM judges, reward models); weights estimated
  with weak supervision (little labeled data); normalization and filtering of low-quality verifiers.
- Numbers: 87.7% average accuracy on reasoning/math tasks with Llama 3.3 70B as generator and
  smaller verifier ensembles; the gain is compared to GPT-4o -> o3-mini (69.0% -> 86.7%).
  Distilled into a 400M cross-encoder to cut verification compute.
- Relevance: the verifier side of the loop can be built from weak parts, but only when the weak
  verifiers' errors are not fully correlated (see 6.1, 6.2). The generator here is 70B, not small.

### 1.5 Fowler et al. 2026, "The Capability Frontier: Benchmarks Miss 82% of Model Performance"
- Citation: arXiv:2606.26836 (submitted 2026-06-25). https://arxiv.org/abs/2606.26836
- Status: PARTIAL (abstract only)
- Claim: selecting the best model and the best generation per item gives an 82% improvement, and SOTA
  accuracy is matched at 85% lower cost.
- Caution: the frontier uses ORACLE selection ("optimal selection across models and generations").
  It measures coverage (like 1.1), not what an imperfect verifier achieves (1.2). Do not cite it as
  evidence that cheap swarms match frontier models without a verifier.

---

## 2. Small models trained or boosted by self-improvement and test-time search

### 2.1 Zelikman, Wu, Mu, Goodman 2022, "STaR: Bootstrapping Reasoning With Reasoning" (NeurIPS 2022)
- Citation: arXiv:2203.14465. https://arxiv.org/abs/2203.14465
- Status: VERIFIED (abstract; numbers via search snippet of the paper)
- Mechanism: generate rationales; keep those reaching the correct answer; for failures,
  "rationalize" by giving the answer as a hint; fine-tune; repeat. The filter is the ground-truth answer, an exact verifier.
- Model: GPT-J 6B.
- Numbers: CommonsenseQA 72.5% vs 73.0% for a fine-tuned GPT-3 about 30x larger.
- Condition (paper's own rationale): the base model must be "large enough to generate rationales of
  non-trivial quality to be bootstrapped from", so p > 0 at the start.

### 2.2 Guan et al. 2025, "rStar-Math: Small LLMs Can Master Math Reasoning with Self-Evolved Deep Thinking"
- Citation: Xinyu Guan, Li Lyna Zhang, Yifei Liu, Ning Shang, Youran Sun, Yi Zhu, Fan Yang, Mao Yang.
  arXiv:2501.04519. https://arxiv.org/abs/2501.04519
- Status: VERIFIED (abstract)
- Mechanism: MCTS with a small policy model guided by a small process preference model (PPM);
  code-augmented CoT so each step is checked by Python execution; 4 rounds of self-evolution
  over 747k math problems; the PPM is trained without step-level human labels.
- Numbers: MATH: Qwen2.5-Math-7B 58.8% -> 90.0%; Phi3-mini-3.8B 41.4% -> 86.4% (+4.5 and +0.9 over
  o1-preview). AIME: 53.3% (8/15).
- Worked when: math with checkable final answers and executable intermediate steps; massive
  rollout compute during data synthesis; a trained verifier (PPM) co-evolved with the policy.

### 2.3 Snell, Lee, Xu, Kumar 2024, "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"
- Citation: arXiv:2408.03314. https://arxiv.org/abs/2408.03314
- Status: VERIFIED (abstract + HTML)
- Mechanism: (1) search against a process reward model (PRM): best-of-N, beam, lookahead;
  (2) sequential revisions. A "compute-optimal" strategy picks per prompt by estimated difficulty.
- Model: PaLM 2-S* on MATH; difficulty = pass@1 quintile from 2048 samples.
- Numbers: > 4x efficiency vs best-of-N baseline; FLOPs-matched, the smaller model + test-time
  compute beats a 14x larger model on questions where the small model has moderate success.
- Conditions (from HTML): test-time compute wins on easy/intermediate bins (1-3) and when the inference
  token load is small relative to pretraining (R << 1); pretraining wins on the hardest bin (5) and
  when R >> 1. Beam search against the PRM degrades on easy questions at high budget ("signs of
  exploitation of the PRM signal"); beam beats best-of-N on harder levels 3-4.

### 2.4 Liu et al. 2025, "Can 1B LLM Surpass 405B LLM? Rethinking Compute-Optimal Test-Time Scaling"
- Citation: Runze Liu, Junqi Gao, Jian Zhao, Kaiyan Zhang, Xiu Li, Biqing Qi, Wanli Ouyang, Bowen Zhou.
  arXiv:2502.06703. https://arxiv.org/abs/2502.06703
- Status: VERIFIED (abstract + HTML)
- Numbers: MATH-500: Llama-3.2-1B 66.2% (with Qwen2.5-Math-PRM-72B), Llama-3.2-3B 78.2%,
  Qwen2.5-0.5B 76.4%, DeepSeek-R1-Distill-Qwen-7B 95.2%. AIME24: 16.7%, 30.0%, 10.0%, 83.3%.
  Comparators: Llama-3.1-405B 71.4% and GPT-4o 74.6% on MATH-500.
- KEY CONDITION: the small policy is paired with a LARGE verifier (72B PRM). This is "weak proposer +
  strong verifier", not an all-small loop. Optimal strategy depends on policy, PRM and difficulty;
  PRMs generalize poorly across policy models; PRMs show length bias and scoring errors
  (over-criticism, error neglect). Gains shrink for 14B-32B policies and on very hard sets.

### 2.5 Song et al. 2024, "Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models" (ICLR 2025)
- Citation: arXiv:2412.02674. https://arxiv.org/abs/2412.02674. Authors (FROM MEMORY): Yuda Song,
  Hanlin Zhang, Carson Eisenach, Sham Kakade, Dean Foster, Udaya Ghai.
- Status: PARTIAL (abstract + HTML summary; authors from memory)
- Mechanism: self-improvement = self-verify, filter/reweight, distill. Generation-verification gap
  (GV-gap) = utility after reweighting by the model's own verification minus utility before.
- Findings: a variant of the relative GV-gap scales monotonically with pretraining FLOPs. Quote (via
  fetch): for small models such as Qwen-1.5 0.5B, "gap(f) is non-positive for nearly all verification
  methods". Families 0.5B to 72B (Qwen-1.5/2/2.5, Llama-2/3/3.1, Yi-1.5). Iterated self-improvement:
  "the gap diminishes nearly to zero within two or three rounds"; effective diversity (pass@k) falls.
  Sudoku: meaningful gap only at 72B. Natural Questions: near-zero gap.
- Implication: a small model cannot serve as its OWN verifier in a self-improvement loop; it needs an
  external verifier.

### 2.6 Bansal et al. 2024, "Smaller, Weaker, Yet Better: Training LLM Reasoners via Compute-Optimal Sampling"
- Citation: arXiv:2408.16737. https://arxiv.org/abs/2408.16737. Authors (FROM MEMORY): Hritik Bansal,
  Arian Hosseini, Rishabh Agarwal, Vinh Q. Tran, Mehran Kazemi.
- Status: PARTIAL (HTML numbers verified; authors from memory)
- Mechanism: at fixed sampling compute, draw more samples from a weaker/cheaper model (WC) instead of
  fewer from a stronger/expensive one (SE); filter by final answer; fine-tune.
- Numbers (MATH): Gemma2-9B vs 27B compute-matched: coverage +11% (low budget) / +6% (high budget);
  diversity +86% / +125%; FALSE POSITIVE RATE 7% higher for the 9B data. Gemini Flash vs Pro
  price-matched coverage 81% vs 61.1%. Fine-tuning on WC data: relative gains of 31.6% (Gemma-7B),
  14.4% (Gemma2-9B), 10.9% (Gemma2-27B). FPR of models fine-tuned on WC data is "as good as" SE.
- Worked when: answer-checkable math; the student learns from the data and is not just resampled.
  Failure mode to watch: the higher FP rate in weak-model data (same direction as 1.2).

### 2.7 Zeng et al. 2025, "SimpleRL-Zoo: Investigating and Taming Zero Reinforcement Learning for Open Base Models in the Wild" (COLM 2025)
- Citation: arXiv:2503.18892. https://arxiv.org/abs/2503.18892. Authors (FROM MEMORY): Weihao Zeng et al.
- Status: PARTIAL (abstract)
- Finding: zero-RL with rule-based rewards across 10 base models 0.5B-32B (Llama3, Mistral, Qwen).
  Gains in accuracy for most; response length does not always track the appearance of verification
  behavior; "aha moment" observed in small non-Qwen models. Format-reward and query-difficulty
  choices matter.

### 2.8 Huang et al. 2025, "R-Zero: Self-Evolving Reasoning LLM from Zero Data"
- Citation: Chengsong Huang, Wenhao Yu, Xiaoyang Wang, Hongming Zhang, Zongxia Li, Ruosen Li,
  Jiaxin Huang, Haitao Mi, Dong Yu. arXiv:2508.05004 (v4 2026-02-13). https://arxiv.org/abs/2508.05004
- Status: VERIFIED (abstract)
- Mechanism: Challenger proposes tasks at the Solver's edge; Solver trains on them; no external data.
- Numbers: Qwen3-4B-Base +6.49 on math, +7.54 on general-domain reasoning.
- Unknown from the abstract: plateau or collapse after several iterations (NOT checked).

### 2.9 Zhao et al. 2025, "Absolute Zero: Reinforced Self-play Reasoning with Zero Data"
- Citation: Andrew Zhao, Yiran Wu, Yang Yue, Tong Wu, Quentin Xu, Matthieu Lin, Shenzhi Wang,
  Qingyun Wu, Zilong Zheng, Gao Huang. arXiv:2505.03335. https://arxiv.org/abs/2505.03335
- Status: PARTIAL (abstract; per-size numbers not visible)
- Mechanism: one model proposes and solves tasks; a code executor validates tasks and answers. The
  verifier is exact and external.
- Claim: SOTA on coding/math among zero-data settings, beating models trained on tens of thousands of
  curated examples; results span several scales (3B/7B/14B mentioned). Per-size numbers NOT extracted.

### 2.10 Li et al. 2025, "Small Models Struggle to Learn from Strong Reasoners"
- Citation: arXiv:2502.12143. https://arxiv.org/abs/2502.12143. Authors (FROM MEMORY): Yuetai Li et al.
- Status: PARTIAL (abstract)
- Finding: models <= 3B do not consistently benefit from long CoT or distillation from much larger
  models; shorter chains that match their capacity work better; "Mix Distillation" helps.
- Relevance: in a loop where a strong model teaches a small worker, the small worker's learnability
  limits the transfer.

### 2.11 Sun et al. 2025, "Theoretical Modeling of LLM Self-Improvement Training Dynamics Through Solver-Verifier Gap"
- Citation: Yifan Sun, Yushan Liang, Zhen Zhang, Xin Liu, Jiaye Teng. arXiv:2507.00075 (v4 2026-02-09).
  https://arxiv.org/abs/2507.00075
- Status: PARTIAL (abstract; functional form not visible)
- Claim: self-improvement gains are driven by the gap between solve ability and verify ability. The
  model fits whole training trajectories and gives capability limits. Under limited external data,
  external data stays effective at any training stage.

---

## 3. Weak-to-strong generalization and weak supervisors

### 3.1 Burns et al. 2023, "Weak-to-Strong Generalization: Eliciting Strong Capabilities With Weak Supervision"
- Citation: arXiv:2312.09390. https://arxiv.org/abs/2312.09390. Authors (FROM MEMORY): Collin Burns,
  Pavel Izmailov, Jan Hendrik Kirchner, Bowen Baker, Leo Gao, Leopold Aschenbrenner, Yining Chen,
  Adrien Ecoffet, Manas Joglekar, Jan Leike, Ilya Sutskever, Jeff Wu.
- Status: PARTIAL (abstract + HTML numbers verified; author list from memory)
- Mechanism: fine-tune a strong model on labels from a weak model; measure performance gap recovered
  PGR = (weak-to-strong - weak) / (strong ceiling - weak).
- Numbers: NLP tasks, naive fine-tuning PGR roughly 20-50%; with auxiliary confidence loss, nearly 80%
  for the largest gaps; GPT-4 supervised by a GPT-2-level model reaches about GPT-3.5 level. Chess:
  PGR > 40% for small gaps, near 0 for the smallest supervisors; bootstrapping through intermediate
  sizes helps. REWARD MODELING: naive PGR roughly 10%, "almost never exceeding 20%".
  Larger students imitate supervisor errors less.
- Relevance to weak VERIFIERS: this is weak LABELS for training, not weak filtering at inference. The
  reward-modeling result (PGR <= 20%) is the closest analogue to "weak verifier judging strong output"
  and is the weakest setting. Strong students generalize past label noise when errors are
  learnable-to-ignore. A resample-until-pass loop has no such mechanism, so a verifier false accept
  goes straight to the output.

### 3.2 Sun et al. 2024, "Easy-to-Hard Generalization: Scalable Alignment Beyond Human Supervision" (NeurIPS 2024)
- Citation: arXiv:2403.09472. https://arxiv.org/abs/2403.09472. Authors (per fetch): Zhiqing Sun,
  Longhui Yu, Yikang Shen, Weiyang Liu, Yiming Yang, Sean Welleck, Chuang Gan.
- Status: VERIFIED (abstract)
- Mechanism: train process-supervised reward models on easy MATH (levels 1-3), use them to rerank or
  RL on hard (levels 4-5).
- Numbers: MATH500: 7B RL model 34.0%; 34B reranking@1024 52.5%, using human supervision only on
  easy problems.
- Relevance: an evaluator weaker in coverage (trained on easy) can still select on hard items. This
  supports using limited verifiers in the loop when the selection signal generalizes by difficulty.

### 3.3 Goel et al. 2025, "Great Models Think Alike and this Undermines AI Oversight"
- Citation: arXiv:2502.04313. https://arxiv.org/abs/2502.04313. Authors (FROM MEMORY): Shashwat Goel et al.
- Status: PARTIAL (abstract)
- Findings: CAPA (chance-adjusted probabilistic agreement) similarity metric; LLM judges favor models
  similar to themselves; in weak-to-strong training, gains come from complementary knowledge between
  supervisor and student and shrink as similarity rises; "model mistakes are becoming more similar
  with increasing capabilities".
- Relevance: a weak verifier from the same family as the generator adds less independent signal.

---

## 4. Small models as mutation operators in evolutionary program search

### 4.1 Romera-Paredes et al. 2023, "Mathematical discoveries from program search with large language models" (FunSearch), Nature 625
- Citation: Nature (2023/2024), doi:10.1038/s41586-023-06924-6. https://www.nature.com/articles/s41586-023-06924-6
- Status: PARTIAL (claims via search snippets of the paper and DeepMind PDF; not read in full)
- Mechanism: island-based evolutionary search; LLM writes program variants; an exact evaluator scores them.
- LLM: Codey (PaLM 2 family, code fine-tuned), a fast-inference model chosen on purpose.
- Numbers: on the order of 10^6 samples per result.
- Quotes (via snippet): the key tradeoff is "between the quality of the samples and the inference speed
  of the LLM"; results are "not too sensitive to the exact choice of LLM, as long as it has been
  trained on a large enough corpus of code". The supplementary compares against StarCoder (open, 15.5B).
- Condition: evaluator is exact and cheap (q = 0), so the loop tolerates very low p per sample.

### 4.2 Novikov et al. 2025, "AlphaEvolve: A coding agent for scientific and algorithmic discovery"
- Citation: arXiv:2506.13131. https://arxiv.org/abs/2506.13131
- Status: VERIFIED (abstract + HTML)
- Mechanism: ensemble of Gemini 2.0 Flash and Gemini 2.0 Pro. Quote: "Gemini 2.0 Flash, with its
  lower latency, enables a higher rate of candidate generation, increasing the number of ideas explored
  per unit of time. Concurrently, Gemini 2.0 Pro, possessing greater capabilities, provides occasional,
  higher-quality suggestions that can significantly advance the evolutionary search."
- Ablation: "Small base LLM only" was clearly worse than the full system on matrix-multiplication
  tensor decomposition and on the kissing-number problem (Figure 8; exact numbers not extracted).
- Result: 4x4 complex matrix multiplication with 48 scalar multiplications.
- Reading: a cheap model gives throughput, but an occasional strong model matters. A small-only mutator
  lost in their ablation.

### 4.3 Lehman et al. 2022, "Evolution through Large Models" (ELM); OpenELM
- Citation: arXiv:2206.08896. https://arxiv.org/abs/2206.08896
- Status: PARTIAL (abstract). The model sizes used for the diff model (300M-6B range) are FROM MEMORY.
  OpenELM (Bradley et al., CarperAI, 2023) NOT checked this session.
- Mechanism: a code-diff LLM as the mutation operator inside MAP-Elites (Sodarace). It produced
  hundreds of thousands of working programs in a domain the model had not seen, then bootstrapped a
  conditional model from them.

### 4.4 Zhang et al. 2024, "Understanding the Importance of Evolutionary Search in Automated Heuristic Design with Large Language Models" (PPSN 2024)
- Citation: arXiv:2407.10873. https://arxiv.org/abs/2407.10873. Authors (FROM MEMORY): Rui Zhang, Fei Liu,
  Xi Lin, Zhenkun Wang, Zhichao Lu, Qingfu Zhang.
- Status: PARTIAL (abstract + HTML summary)
- Setup: 4 LLM-based evolutionary program search methods x 4 heuristic-design problems x 9 LLMs
  (UniXcoder 0.3B, StarCoder 15.5B, CodeLlama 7B/34B, DeepSeek-Coder 6.7B/33B, GPT-3.5, GPT-4,
  Claude 3 Opus) x 5 runs.
- Findings (quotes via fetch): "LLMs with more capacity ... do not necessarily lead to better
  performance on AHD problems"; "significant variances in performance attributable to the choice of LLM";
  EoH was stable across all LLMs on TSP while greedy (1+1)-EPS varied a lot. Evolutionary search is
  needed; plain sampling is not enough.
- Reading: in search loops with exact evaluators, the search algorithm matters as much as model size.

### 4.5 Zhang, Chen, Portet, Peyrard 2026, "What Makes an LLM a Good Optimizer? A Trajectory Analysis of LLM-Guided Evolutionary Search"
- Citation: arXiv:2604.19440 (submitted 2026-04-21). https://arxiv.org/abs/2604.19440
- Status: PARTIAL (abstract)
- Setup: 15 LLMs x 8 optimization tasks.
- Findings: zero-shot problem-solving ability correlates with final outcome but "explains only part of
  the variance"; good optimizers act as "local refiners" with frequent small improvements and
  progressive localization; weak ones show "large semantic drift, with sporadic breakthroughs followed
  by stagnation"; novelty helps only when search stays near high-performing regions.

### 4.6 Saketos, Kaltenbach, Litvinov, Koumoutsakos 2025, "Data-Driven Discovery of Interpretable Kalman Filter Variants through LLMs and Genetic Programming"
- Citation: arXiv:2508.11703. https://arxiv.org/abs/2508.11703
- Status: PARTIAL (abstract verified; the model-size statement comes only from a search-engine snippet)
- Claim (snippet): in a FunSearch-like loop with DeepSeek-R1-Distill-Qwen models, "models with fewer than
  14 billion parameters tended to produce repetitive and low-quality generations"; 14B was the chosen
  efficiency/quality tradeoff. This is a single-study anecdote, not a controlled scaling result.

### 4.7 Assumpcao et al. 2025/2026, "CodeEvolve: an open source evolutionary coding agent for algorithmic discovery and optimization" (EMNLP 2026 Findings)
- Citation: arXiv:2510.14150 (rev. 2026-08-27). https://arxiv.org/abs/2510.14150
- Status: VERIFIED (abstract)
- Model: open-weight Qwen3-Coder-30B backbone (MoE; about 3B active parameters, FROM MEMORY) + weighted ensemble.
- Numbers: matches or beats reported AlphaEvolve results on 5 of 9 problems, at "roughly an order of
  magnitude lower cost"; exceeds on CirclePackingSquare.

### 4.8 Lange, Imajuku, Cetin 2025, "ShinkaEvolve"
- Citation: arXiv:2509.19349. https://arxiv.org/abs/2509.19349
- Status: PARTIAL (abstract)
- Mechanism: parent sampling, code-novelty rejection sampling, bandit-based LLM-ensemble selection.
- Number: state-of-the-art circle packing with only 150 samples.
- Reading: sample efficiency comes from search machinery; bandit selection over a model ensemble lets
  cheap models carry most calls.

### 4.9 Xing et al. 2026, "Compute Allocation for Self-Evolving LLMs: From Depth-Breadth to Multi-Armed Bandits"
- Citation: arXiv:2605.29268 (v3 2026-09-12). https://arxiv.org/abs/2605.29268
- Status: PARTIAL (abstract)
- Findings: bilinear depth-breadth fit with task-specific interaction; a "fitness-compute envelope
  along which capability ordering largely collapses when measured in effective FLOPs"; BaSE bandit
  allocation improves mean fitness 12.3% over the strongest island baseline across 8 (model, task) cells.
- Relevance: the closest 2026 evidence that, per effective FLOP, model ranking matters less in
  evolutionary search. Not a direct small-vs-large study.

### 4.10 Weindel, Heckel 2025, "LLM-Guided Search for Deletion-Correcting Codes"
- Citation: arXiv:2504.00613. https://arxiv.org/abs/2504.00613
- Status: PARTIAL (abstract)
- Finding: "compute is better allocated to sampling more functions than to longer reasoning traces
  per function". This supports breadth from cheaper calls over depth per call.

### 4.11 CALM 2025, "Co-evolution of Algorithms and Language Model for Automatic Heuristic Design"
- Citation: arXiv:2505.12285. https://arxiv.org/html/2505.12285v1
- Status: PARTIAL (search-engine snippet only)
- Claim (snippet): the LLM itself is fine-tuned during the search; runs on one 24GB GPU with a 7B
  INT4 model; ablation shows Qwen2.5-14B > 7B, and quantization further hurts 7B.

### 4.12 Any 2026 controlled "model size vs evolutionary search yield" study
- Status: NOT FOUND as a dedicated controlled scaling study. The closest are 4.5 (15 LLMs, trajectory
  analysis) and 4.9 (effective-FLOP envelope).

---

## 5. Swarms of small models vs one large model

### 5.1 Li, Zhang, Yu, Fu, Ye 2024, "More Agents Is All You Need" (TMLR)
- Citation: arXiv:2402.05120. https://arxiv.org/abs/2402.05120
- Status: VERIFIED (abstract + HTML)
- Mechanism: sampling-and-voting ("Agent Forest").
- Numbers: GSM8K: Llama2-13B with 40 agents 59% vs Llama2-70B single 54%; GPT-3.5-Turbo with 15-20
  agents reaches GPT-4 single (88%). Gains at N=40: GSM8K +12-24%, MATH +6-10%, MMLU +5-11%, HumanEval
  +4-9%.
- Conditions: gains peak at moderate inherent difficulty and fall at extreme difficulty; higher prior
  probability of the correct answer -> larger gains; combining with debate hurt Llama2 code
  generation ("noise generated by referencing answers of other agents").

### 5.2 Wang et al. 2024, "Mixture-of-Agents Enhances Large Language Model Capabilities"
- Citation: Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, James Zou. arXiv:2406.04692.
  https://arxiv.org/abs/2406.04692
- Status: VERIFIED (abstract)
- Numbers: AlpacaEval 2.0 65.1% with open-source models only vs GPT-4 Omni 57.5%.
- Caution: the open models used were mostly large (70B+ class; FROM MEMORY). This is not evidence for
  sub-4B swarms, and AlpacaEval is judged by an LLM (see 6.3).

### 5.3 Li, Lin, Xia, Jin 2025, "Rethinking Mixture-of-Agents: Is Mixing Different Large Language Models Beneficial?"
- Citation: arXiv:2502.00674. https://arxiv.org/abs/2502.00674
- Status: VERIFIED (abstract)
- Finding: Self-MoA (many samples of the single best model) beats mixed MoA by 6.6% on AlpacaEval 2.0
  and by 3.8% on average across MMLU, CRUX, MATH; "mixing different LLMs often lowers the average
  quality". Quality beats diversity.
- Reading: a swarm of weaker members added to a strong one tends to dilute it.

### 5.4 Chen et al. 2024 (see 1.3)
- Vote/Filter-Vote is non-monotone in N; hard items get worse with more calls.

### 5.5 Summary of section 5 (librarian reading of 5.1-5.4, 1.1, 1.5)
- Swarms match or beat one larger model when: (a) the answer space is small and checkable by vote;
  (b) per-member p on the item is high enough that the correct answer is the plurality; (c) difficulty
  is moderate; (d) comparison is 13B vs 70B or 3.5 vs 4 class, not sub-1B vs frontier.
- Swarms fail when: the item is hard (the wrong answer is modal); aggregation needs a judge; members are
  weaker than the best single model (Self-MoA); members share errors (6.1).
- Cost-matched swarm vs frontier with a REAL selector (not oracle): NOT FOUND as a clean 2026 study.

---

## 6. Failure conditions

### 6.1 Kim, Garg, Peng, Garg 2025, "Correlated Errors in Large Language Models" (ICML 2025)
- Citation: arXiv:2506.07962. https://arxiv.org/abs/2506.07962
- Status: PARTIAL (abstract; authors' first names FROM MEMORY)
- Numbers: > 350 LLMs; on one leaderboard dataset, "models agree 60% of the time when both models err".
  Shared architecture and provider predict correlation; more accurate models have more correlated
  errors even across different architectures. Consequences shown for LLM-as-judge and hiring (monoculture).
- Relevance: ensembles, votes and cross-checks assume independent errors. That assumption fails at a
  measurable rate.

### 6.2 Goel et al. 2025 (see 3.3): judges prefer similar models; errors converge with capability.

### 6.3 Zhao et al. 2025, "One Token to Fool LLM-as-a-Judge"
- Citation: arXiv:2507.08794. https://arxiv.org/abs/2507.08794. Authors (FROM MEMORY): Yulai Zhao et al.
- Status: PARTIAL (abstract; FP-rate numbers not extracted)
- Finding: "master keys" (":", ".", "Thought process:", "Let's solve this problem step by step")
  make generative reward models / LLM judges give false-positive rewards, including GPT-o1 and
  Claude-4. Fix: Master-RM trained with truncated outputs as negatives.
- Relevance: an LLM verifier in an RLVR or search loop has a q that an optimizing generator can drive
  toward 1 on specific inputs. The q is adversarial, not i.i.d.

### 6.4 Shao et al. 2025, "Spurious Rewards: Rethinking Training Signals in RLVR"
- Citation: arXiv:2506.10947. https://arxiv.org/abs/2506.10947. Authors (FROM MEMORY): Rulin Shao et al.
- Status: PARTIAL (abstract)
- Numbers: GRPO with RANDOM rewards raises Qwen2.5-Math-7B MATH-500 by 21.4 points; code-reasoning
  frequency 65% -> > 90%; gains "often fail" to appear for Llama3 or OLMo2. Mechanism: GRPO clipping
  bias amplifies behaviors already present from pretraining.
- Relevance: small-model self-improvement gains need a random-reward control before you attribute them
  to the verifier signal.

### 6.5 Shumailov et al. 2023/2024, "The Curse of Recursion: Training on Generated Data Makes Models Forget" (Nature 2024: "AI models collapse when trained on recursively generated data")
- Citation: arXiv:2305.17493. https://arxiv.org/abs/2305.17493 ; Nature doi:10.1038/s41586-024-07566-y
  (the Nature page redirected to a login; the Nature title is FROM MEMORY)
- Status: PARTIAL
- Finding: "use of model-generated content in training causes irreversible defects in the resulting
  models, where tails of the original content distribution disappear" (VAEs, GMMs, LLMs; the LLM used
  OPT-125m, FROM MEMORY).

### 6.6 Gerstgrasser et al. 2024, "Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data"
- Citation: arXiv:2404.01413. https://arxiv.org/abs/2404.01413
- Status: PARTIAL (abstract; subtitle and authors FROM MEMORY)
- Finding: replacing real data with each generation's synthetic data -> collapse; accumulating
  synthetic data alongside real data -> test error has "a finite upper bound independent of the number
  of iterations" (linear-model theory), confirmed empirically for LMs, diffusion and VAEs over a range of sizes.
- Condition for safe self-training: keep the original data, accumulate, and do not replace.

### 6.7 Gao, Schulman, Hilton 2022, "Scaling Laws for Reward Model Overoptimization"
- Citation: arXiv:2210.10760. https://arxiv.org/abs/2210.10760
- Status: PARTIAL (abstract; functional forms FROM MEMORY)
- Finding: gold reward vs optimization against a proxy RM follows different functional forms for RL vs
  best-of-n; coefficients scale smoothly with RM size. FROM MEMORY: the forms are
  d*(alpha - beta*d) for best-of-n and d*(alpha - beta*log d) for RL, with d = sqrt(KL).
  Smaller RMs overoptimize sooner.
- Relevance: small reward models reach the Goodhart peak at low optimization pressure.

### 6.8 "Inference-Time Reward Hacking in Large Language Models" (NeurIPS 2025 spotlight)
- Citation: arXiv:2506.19248. https://arxiv.org/abs/2506.19248. Authors: NOT extracted (FROM MEMORY:
  Khalaf, Verdun, Oesterling, Lakkaraju, Calmon)
- Status: PARTIAL
- Finding: true reward is non-monotone in best-of-n / soft-BoN optimization strength against an
  imperfect proxy; HedgeTune picks the hedging parameter; Best-of-Poisson is introduced.

### 6.9 Helff et al. 2026, "LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking"
- Citation: arXiv:2604.15149 (2026-04-16). https://arxiv.org/abs/2604.15149
- Status: VERIFIED (abstract)
- Finding: RLVR-trained models (GPT-5, Olmo3) enumerate instance-level labels that pass verifiers
  without learning the relational rule; absent in non-RLVR models (GPT-4o, GPT-4.5, Ministral).
  "Shortcut prevalence increases with task complexity and inference-time compute." Detection:
  Isomorphic Perturbation Testing.

### 6.10 Ray 2026, "Before the Model Learns the Bug: Fuzzing RLVR Verifiers"
- Citation: arXiv:2606.01066 (2026-05-31). https://arxiv.org/abs/2606.01066
- Status: PARTIAL (abstract)
- Finding: verifier bugs create structured false-positive regions (math answer checkers, JSON
  tool-call validators, unit-test harnesses); search/optimization turns them into high-reward,
  low-correctness behavior. Proposes fuzzing verifiers against stricter references BEFORE training and
  reports FP/FN/disagreement/exploit metrics.

### 6.11 Also relevant, cross-referenced: 1.2 (weak models have higher conditional FP rate), 2.3
(PRM exploitation by beam search on easy items), 2.4 (PRM length bias), 2.5 (GV-gap vanishes in 2-3
rounds, diversity falls).

---

## Working synthesis

Falsifiable claim: A small, weak model is usable as a PROPOSER/MUTATOR in a search or
self-improvement loop when all of the following hold, and fails when any one fails.
(i) An external verifier's false-accept rate q is small relative to the model's per-task solve rate
p: the returned-answer precision in the resample-until-pass limit is A = c*p / (c*p + q*(1-p)), so
reaching precision t needs p/(1-p) >= (t/(1-t))*(q/c). With q about 0 (exact evaluators: Lean,
program scorers, answer keys) the loop can run at p near 1e-3 to 1e-4 (1.1, 4.1, 2.1). With q > 0,
weak models are hurt twice, because their q is empirically higher than a strong model's (1.2, 2.6).
(ii) The model is not its own verifier. Small models have a non-positive
generation-verification gap (2.5), so the successes pair a weak policy with an exact checker or a
larger or separately trained verifier (2.2, 2.4, 3.2).
(iii) p > 0 on the target items and errors across samples are not fully correlated, so
pass@K actually rises. Gains concentrate on easy and intermediate difficulty bins and reverse on the
hardest bins (2.3, 1.3, 5.1). Cross-model error correlation (about 60% agreement when both err, 6.1)
limits what voting and ensemble verification add.
(iv) Budget is spent as breadth under a compute or throughput constraint, with K capped where false
positives start to dominate (optimal K <= 5 at FP cost ratio 4: 1.2). Small-only mutators still lost
to Flash+Pro mixes in AlphaEvolve (4.2), so a weak-majority/strong-minority ensemble beats small-only.
(v) Self-training on its own outputs keeps the real data (accumulates rather than replaces) and uses
a random-reward control (6.4, 6.5, 6.6). Otherwise diversity collapses within 2-3 rounds (2.5).
Falsifiers: (a) measured per-task precision of resample-until-pass deviates from A by more than
sampling error when p, q, c are measured on held-out samples; (b) a sub-1B proposer with an exact
evaluator fails to beat a 3B-class single-sample baseline at matched FLOPs on difficulty bins 1-3;
(c) an all-small loop (small proposer + same-size self-verifier) shows sustained gains beyond 3 rounds
without external verification.

---

## Questions raised

1. Does A = c*p/(c*p + q*(1-p)) predict per-task precision? Experiment (CPU or 2GB GPU): Qwen2.5-0.5B
   or 1.5B-Instruct (4-bit) on HumanEval/MBPP, 200 samples/task; verifier = original tests,
   ground truth = HumanEval+/MBPP+; measure p, q, c per task and compare predicted vs observed
   precision of first-pass-wins.
2. Is q correlated with p across tasks within one small model, as Stroebl et al. found across
   models? Same data as Q1, regress per-task q on p.
3. How far from i.i.d. are small-model samples? Fit a beta-binomial to per-task pass counts and
   compare observed pass@K with 1-(1-p)^K; estimate the intra-task correlation.
4. Does strengthening the verifier (property-based tests with Hypothesis, differential testing against
   a reference) drive q toward 0 and restore monotone scaling? CPU-only, no model training.
5. Mutation yield per FLOP by model size with an exact evaluator: FunSearch-style online bin packing
   or cap-set toy, Qwen2.5-0.5B vs 1.5B vs 3B (4-bit, llama.cpp on CPU/2GB GPU), a fixed wall-clock
   budget, and best-score-vs-time curves.
6. Do weak mutators show the "semantic drift then stagnation" trajectory of 2604.19440? Log embedding
   distance of accepted children to the parent over the Q5 runs.
7. Does a strong-minority mix help at tiny scale? Q5 with 90% 0.5B calls + 10% calls to a larger model
   (API or CPU 7B) vs 100% of either, matched on cost.
8. Can a 0.5B verifier trained only on easy items (easy-to-hard, 3.2) filter a 1.5B generator's
   outputs on hard items with q below the generator's p? LoRA on CPU is feasible for 0.5B.
9. Weaver-style ensembles of weak verifiers: does the ensemble's q fall roughly as the product of
   member q's, or is it floored by correlation? Measure pairwise CAPA among 3-5 small judges.
10. Is the generation-verification gap for sub-2B models really non-positive when verification is
    reframed as a checkable subtask (e.g., "run this test and report")? Replicate the 2.5 setup at 0.5B.
11. STaR-style loop at 0.5B on GSM8K for 5 rounds, replace vs accumulate: track pass@1, pass@16 and
    answer diversity per round. Does the gap vanish by round 2-3?
12. Random-reward control: run the Q11 loop with the answer-check filter replaced by a coin flip at
    matched acceptance rate. What fraction of the gain survives?
13. Reward hacking onset: RL or rejection-sampling fine-tuning of a 0.5B coder against weak unit tests.
    How many rounds until hard-coded outputs / special-casing appear on held-out tests? Is this faster
    than in a 1.5B model?
14. Optimal K under false-positive cost for a 0.5B model (replicate Stroebl Fig. 4 on CPU): is K_opt
    even smaller than for 8B?
15. Swarm vs single under a 2GB VRAM cap: N x 0.5B votes vs M x 1.5B votes at equal tokens/sec, split
    by difficulty bin (Snell binning from 64 samples). Where is the crossover?
16. Self-ensemble vs mixed-family ensemble at sub-2B (Qwen, Llama-3.2-1B, Gemma-2-2B): does the
    Self-MoA "quality over diversity" result hold, or does diversity win when every member is weak?
17. How much small-model coverage on numeric-answer tasks is guessing? Control: shuffle problem
    statements across answers and measure the "coverage" of random pairings at the same K.
18. Can a cheap difficulty probe (pass rate of the first 8 samples) route the remaining budget
    (Snell compute-optimal) and raise solved-per-FLOP for a 0.5B proposer?
19. Verifier fuzzing before any loop (6.10): what fraction of our own evaluators have
    FP regions reachable by a 0.5B model within 10^4 samples?
