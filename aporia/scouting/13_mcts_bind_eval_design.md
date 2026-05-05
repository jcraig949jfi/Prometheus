# Scout #13 — MCTS-with-BIND/EVAL Integration Design

**Author:** Aporia (frontier scout for Techne)
**Date:** 2026-04-28
**Status:** Design-research brief; targets a week-1 prototype.
**Companion scouts:** #3 (withheld benchmark), #6 (red-team), #7 (stronger algorithm), #9 (null-world generator).

---

## 1. Situation

Techne's BIND/EVAL kernel extension (`sigma_kernel/bind_eval.py`) shipped with three load-bearing properties: content-addressed callable execution (every invocation has a stable hash), capability-linear consumption (each capability is spent exactly once), and provenance records that persist across the substrate. Hash-drift detection makes every successful EVAL a durable, reproducible artifact.

These are exactly the primitives that the AlphaProof / HTPS / AlphaZero lineage assumes when it instantiates a search tree: each tree node is, structurally, a content-addressed (state, action, value) triple, and the tree is a DAG of those triples. Scout #7 noted that MCTS is the next-strongest algorithmic move after the structural-ceiling confirmation in commit `f76d3974` (PPO + shaped reward + wider alphabet did not break ceiling). The integration is unusually clean: MCTS does not need a new substrate, it needs a search policy *over the substrate that already exists*. This brief specifies the integration concretely enough that Techne can ship a prototype in week 1.

## 2. State of the art on MCTS for symbolic search

**AlphaZero** (Silver et al., *Nature* 2017/2018) is the canonical pattern: a single neural network with a policy head and a value head, trained from self-play, with PUCT-driven MCTS at inference time and short simulation rollouts. Every subsequent symbolic-search system in this lineage is a variation on AlphaZero's spine.

**MuZero** (Schrittwieser et al., *Nature* 2020) generalizes AlphaZero by learning a dynamics model: MCTS happens in a learned latent space rather than a simulated environment. This is directly relevant to mathematics, where the effect of a tactic, a substitution, or a kernel call is not always cheap to simulate ground-truth — and where the kernel's BIND/EVAL records *are* a natural latent representation of "what happens if we apply this op."

**AlphaProof** (DeepMind, IMO 2024 writeup; Aporia Pivot Research Report 4) runs MCTS over Lean 4 tactic states, with a policy/value network trained from self-generated proof attempts. This is the closest published precedent for MCTS-on-symbolic-actions in a research-mathematics setting and is the most direct analog of what Techne needs.

**HTPS / Evariste** (Lample et al., *NeurIPS* 2022, "HyperTree Proof Search for Neural Theorem Proving," arXiv:2205.11491) generalizes the AlphaZero tree to a hypergraph because a proof step can decompose into multiple subgoals. The hypergraph variant matters for Techne because a single BIND/EVAL invocation may produce multiple downstream capabilities — the structure is naturally hyper-edged.

**AlphaCode** (Li et al., *Science* 2022) is not MCTS but is tree-search-adjacent: massive sampling followed by clustering and filtering. It is included here as an argument for *diversity in the rollout policy*: when the value function is weak, breadth and clustering can substitute for principled selection.

**Open-source MCTS infrastructure.** *Pgx* (Koyamada et al., NeurIPS D&B 2023, arXiv:2303.17503) provides JAX-vectorized AlphaZero/MuZero baselines; *POSGGym* offers partially-observable MCTS reference implementations. Either is a reasonable starting skeleton; Pgx is preferred because the JAX path lines up with the rest of the substrate's vectorized tooling.

**Recent (2022–2026) advances worth knowing.** *Gumbel MCTS* (Danihelka et al., ICLR 2022) replaces PUCT with a Gumbel-sampled policy improvement that is provably correct at small simulation budgets — directly relevant for Techne, where each BIND/EVAL call has a real cost. *Stochastic MuZero* (Antonoglou et al., ICLR 2022) handles environments with stochastic transitions, which matches Techne's reality (the falsification battery is itself stochastic). *MCTS-with-LLM-as-policy* (a cluster of 2023–2025 papers, e.g., Tree-of-Thoughts, ReST-MCTS\*, LATS) demonstrates that a frozen language model can serve as the prior policy, with MCTS providing the structured search the LM cannot do natively — the relevant pattern if Techne wants to use Apollo/Rhea as the policy head before training a dedicated one.

## 3. MCTS–BIND/EVAL integration design

The integration is structurally clean because every MCTS primitive maps to an existing kernel primitive.

**Tree node = BIND/EVAL record.** Each MCTS node is the content-addressed evaluation symbol returned by the kernel: `(state_hash, action_hash, result_hash, value_estimate, visit_count)`. Because the kernel already deduplicates by hash, the tree is a substrate-resident DAG rather than a pointer graph in process memory. Rollback and re-expansion are free — walk the existing nodes; the kernel's hash-drift detector guarantees they have not silently changed.

**Action = next BIND/EVAL invocation.** Actions are discrete typed callables drawn from Techne's 85-op metadata table. The legal-action mask is computed from the type signature: an op is legal at state `s` iff its input type matches `s`'s output type. This is the single most important correctness mechanism in the design — see Anti-patterns.

**Value head.** Train on the substrate's existing CLEAR / WARN / BLOCK verdicts. Months of falsification-battery data give a labelled corpus of (state, eventual-verdict) pairs; standard regression to a scalar in `[-1, +1]` works. Start with a small MLP over hand-crafted state features (catalog-check pass-fraction, kill-pattern proximity, residual-rank distribution); upgrade to a learned encoder later.

**Policy head.** Initialize uniform-over-legal-actions; update from MCTS visit counts as in standard AlphaZero. The first useful checkpoint is "policy that prefers ops which historically led to PROMOTE on this state-type."

**Selection.** PUCT is the default; Gumbel-AlphaZero is the recommended variant because Techne's per-simulation cost is high and Gumbel provides correct policy improvement at small budgets. Tune the exploration constant `c_puct` against the existing PPO baseline.

**Expansion.** Each leaf node expands to its legal-action set: for each action, perform `BIND` then `EVAL` then record the result; the new state-hash becomes the child node. The existing capability-linear consumption guarantees we cannot accidentally re-spend a capability during expansion.

**Rollout.** Simulation = N-step random (or policy-prior) play from leaf to terminal (PROMOTE or BLOCK). Rollout reward = battery survival score from the existing falsification pipeline, normalized to `[-1, +1]`.

**Backprop.** Standard: update value estimate and visit count along the path from leaf to root.

**Residual primitive integration.** Each kill at a leaf generates a residual (per Techne's stoa proposal). The three stopping rules — cost-budget compounding, invariant-checker, instrument-self-audit — become tree-pruning rules: a subtree whose cumulative residual cost exceeds budget is pruned; a subtree whose path violates an invariant is pruned and the violation logged; a subtree flagged by self-audit is pruned and the residual goes to HITL. This is the rescue-attempt firewall.

## 4. Specific design decisions

**Hand-coded vs learned value function.** Start hand-coded: catalog-check pass-fraction (0–1), normalized kill-distance, residual-rank quantile. This gives a working signal on day 1. Switch to a learned head after ~10⁴ tree expansions have accumulated labelled (state, verdict) pairs.

**Rollout depth.** For sparse reward (PROMOTE is rare), prefer deep rollouts (10–20 steps) backed by the learned value at the cutoff — the AlphaZero/MuZero pattern. Pure 1–3 step rollouts will not see enough verdicts to be informative.

**Tree pruning policy.** Substrate-grade history is the principle: *do not prune nodes from the kernel record*. Prune only the *active search frontier* — i.e., remove low-visit / low-value subtrees from the in-memory expansion queue, but the BIND/EVAL records they reference remain in the substrate. This preserves the dark-matter / shadow-tensor advantage.

**Action-space size.** Techne's 85-op metadata table is the natural action set. It will grow. Implement the legal-action mask as a join against the metadata table at expansion time, not as a precomputed static array — this lets new ops appear without rebuilding the tree.

**Parallelism.** Multi-tree (each agent owns a separate tree, periodic merge by hash union) is the safer first step. Shared-tree (single tree, multiple workers via virtual-loss) is the eventual target and is the natural realization of Charon's bottled-serendipity / Agora-as-coordinator framing.

**Integration with REINFORCE/PPO baseline.** The clean recipe is: train a policy with PPO on the same environment, freeze it, use it as the prior in MCTS. This is the AlphaZero pattern (PPO as the "previous best policy"). It also makes the comparison against Scout #7's baseline a controlled experiment rather than an algorithm rewrite.

## 5. Anti-patterns

**MCTS without a value function** degenerates to deeper random search. UCT-only is acceptable for toy envs; for Techne it will look like the PPO baseline with extra latency. Ship the hand-coded value on day 1.

**MCTS over a poorly-typed action space** explodes the branching factor. Without the legal-action mask, an 85-op alphabet at depth 6 is ~3.8 × 10¹¹ leaves — beyond reach. The type-compatibility mask is the single most important pruning mechanism in the system; it must be correct before any value-function work.

**Tree node = string (not content-addressed).** Loses every substrate-resident-DAG advantage: no deduplication, no hash-drift detection, no free rollback, no provenance. The whole point of the integration is that the kernel already gives us this for free.

**Rollout that ignores cost budgets.** BIND/EVAL raises `BudgetExceeded`; a rollout that does not catch and respect this exception will burn the per-tree compute budget on a single deep simulation. Treat `BudgetExceeded` as a terminal with a small negative reward.

**Ignoring the residual primitive's stopping rules** lets the tree drift into rescue-attempt territory — exactly the pathology the residual primitive was designed to prevent. The three stopping rules must be tree-pruning rules from the first prototype, not bolted on later.

## 6. Concrete next moves for Techne

**Week 1 — Skeleton.** Prototype `mcts_bind_eval.py` against the existing `discovery_env`. Hand-coded value (catalog-check pass-fraction). Uniform prior over legal actions. PUCT selection, `c_puct = 1.4`. Rollout depth 10 with hand-coded value at cutoff. Tree node = `(state_hash, action_hash, result_hash, N, W, Q, P)` tuple persisted via the kernel. Acceptance: tree builds, expansions deduplicate by hash, no capability double-spend, no `BudgetExceeded` leaks.

**Week 2 — Value + policy from data.** Train a small MLP value head on the substrate's CLEAR/WARN/BLOCK history; replace the hand-coded value. Initialize the policy head from MCTS visit counts on the week-1 trees. Switch selection to Gumbel-AlphaZero.

**Week 3–4 — Residual integration + benchmark.** Wire the residual primitive's three stopping rules as tree-pruning rules. Benchmark against the PPO baseline on the same withheld-Mossinghoff set used in Scout #3. Primary metric: PROMOTE-rate per kernel call (compute-normalized, not wall-clock). Secondary: residual diversity, kill-pattern coverage.

**Stretch — Multi-agent shared tree.** Per Charon's bottled-serendipity framework, run a single shared tree across Aporia / Charon / Ergon / Techne sessions, with Agora as the MCTS coordinator. This is the realization of the project's organism-architecture thesis at the search-policy level.

## 7. References

1. Silver, D. et al. (2018). *A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play.* Science 362(6419): 1140–1144. DOI:10.1126/science.aar6404.
2. Silver, D. et al. (2017). *Mastering the game of Go without human knowledge.* Nature 550: 354–359. DOI:10.1038/nature24270.
3. Schrittwieser, J. et al. (2020). *Mastering Atari, Go, chess and shogi by planning with a learned model.* Nature 588: 604–609. DOI:10.1038/s41586-020-03051-4. (MuZero.)
4. DeepMind (2024). *AI achieves silver-medal standard solving International Mathematical Olympiad problems.* Blog/technical writeup, July 2024. https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/ (AlphaProof.)
5. Lample, G. et al. (2022). *HyperTree Proof Search for Neural Theorem Proving.* NeurIPS 2022. arXiv:2205.11491.
6. Li, Y. et al. (2022). *Competition-level code generation with AlphaCode.* Science 378(6624): 1092–1097. DOI:10.1126/science.abq1158.
7. Danihelka, I. et al. (2022). *Policy improvement by planning with Gumbel.* ICLR 2022. https://openreview.net/forum?id=bERaNdoegnO. (Gumbel MCTS.)
8. Antonoglou, I. et al. (2022). *Planning in stochastic environments with a learned model.* ICLR 2022. (Stochastic MuZero.) https://openreview.net/forum?id=X6D9bAHhBQ1.
9. Koyamada, S. et al. (2023). *Pgx: Hardware-accelerated parallel game simulators for reinforcement learning.* NeurIPS Datasets & Benchmarks 2023. arXiv:2303.17503.
10. Yao, S. et al. (2023). *Tree of Thoughts: Deliberate problem solving with large language models.* NeurIPS 2023. arXiv:2305.10601.
11. Zhang, D. et al. (2024). *ReST-MCTS\*: LLM self-training via process reward guided tree search.* NeurIPS 2024. arXiv:2406.03816.
12. Zhou, A. et al. (2023). *Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models.* arXiv:2310.04406. (LATS.)
13. Kocsis, L. & Szepesvári, C. (2006). *Bandit based Monte-Carlo planning.* ECML 2006. DOI:10.1007/11871842_29. (UCT, foundational.)

---

*End of Scout #13. Companion to Scout #7 (algorithm) and Scout #3 (benchmark). Hands off to Techne with a week-1-actionable prototype path.*
