# Research Brief: Gymnasium Env Design Patterns for Symbolic-Reasoning RL

**Date:** 2026-05-02
**Author:** Claude (research subagent)

---

## 1. Situation

Project Prometheus is a multi-agent mathematical research substrate consisting of a signature-keyed tensor over ~86K mathematical objects, an arsenal of ~2800 typed callables (Techne's toolsmith inventory), a falsification battery (Charon's regime-change/mirror tests), and adversarial agents (Agora, Aporia). Techne's pivot proposes wrapping this substrate as a Gymnasium-compatible environment so that David Silver-class RL learners (future internal Apollo/Rhea evolutions, or external agents) can plug in without bespoke glue. Observations are the current substrate state (claim graph + tensor slices + open frontier), actions are `(op_id, args)` over the typed arsenal, rewards come from falsification-battery survival, and episodes terminate on PROMOTE (claim survives) or BLOCK (kill). This brief surveys SOTA symbolic-reasoning RL envs to inform that scaffold while the frontier-LLM window is still open (per `feedback_frontier_models_window`).

## 2. State-of-the-Art

**LeanDojo / Lean-Gym (Yang et al., NeurIPS 2023; Polu & Sutskever 2020).** Observation: serialized proof state (goals + hypotheses) as text. Action: tactic string from a fixed-vocabulary or LLM-generated. Reward: sparse terminal (proof closes). Worked: enabled retrieval-augmented tactic selection (ReProver). Didn't work: pure RL without retrieval got stuck on long proofs; tactic-string action space is unbounded and forced LM-as-policy.

**AlphaProof (DeepMind, 2024).** Observation: Lean 4 proof state. Action: tactic generation conditioned on AlphaZero-style search. Reward: shaped via auto-formalized problem difficulty + proof-completion. Episode: tree-structured, not linear. Worked: AlphaZero-style MCTS over tactic policies achieved IMO silver. Key insight: self-play via problem generation (Test-Time RL) compensates for sparse reward.

**AlphaGeometry (Trinh et al., Nature 2024).** Action: symbolic deduction step OR auxiliary-construction proposal. Hybrid neuro-symbolic: symbolic engine handles deduction, LM proposes constructions. Reward: terminal proof closure. Worked: separating "deterministic deduction" from "creative construction" massively reduced action-space explosion.

**DreamCoder (Ellis et al., PLDI 2021).** Observation: program sketch + I/O examples. Action: production rule from evolving DSL. Reward: program correctness + description-length prior. Episode: wake-sleep cycle compresses successful programs into new primitives — directly relevant to Techne's tier-promotion pattern.

**Code Contests / APPS / HumanEval-RL (Hendrycks et al. 2021; Li et al. 2022).** Observation: problem statement. Action: token sequence. Reward: pass-rate on hidden tests. Worked at scale (AlphaCode); failed for fine-grained credit assignment — terminal-only reward is brittle.

**HTPS / Evariste (Lample et al., NeurIPS 2022).** HyperTree Proof Search over Metamath/Lean: tree-search with learned policy + value. Confirmed that **tree-structured episodes outperform linear MDPs** for proof search.

## 3. Patterns Prometheus Should Adopt

1. **Discrete typed `op_id` action space, not free-form strings.** AlphaProof and HTPS both gain sample efficiency from a finite tactic vocabulary. Techne's ~2800 callables already have type signatures — use them as a typed action mask conditioned on observation. Avoids LeanDojo's unbounded-string failure mode.

2. **Two-level action: `(op_family, args)` factorization.** AlphaGeometry's deduce-vs-construct split shows huge wins from factoring action space. For Prometheus: top-level chooses op-family (FALSIFY / EXTEND / BIND / EVAL / PROMOTE), bottom-level chooses concrete callable + args. Cuts effective branching factor.

3. **Graph observation, not flat vector.** Substrate state is inherently a provenance graph (claims, evidence, ops). Use a typed heterogeneous graph (PyG-style) with node types {claim, tensor-slice, evidence, op-application} and edge types {derives, falsifies, supports}. Flat vectorization loses the load-bearing topology — `feedback_verbs_over_nouns` warns exactly against object-label flattening.

4. **Shaped reward via intermediate falsification gates.** Charon's battery has tiers. Award partial credit per surviving tier rather than terminal-only PROMOTE/BLOCK. AlphaProof shapes via difficulty estimates; HumanEval-RL's terminal-only reward demonstrably cripples credit assignment. Use the existing 25-test/4-tier battery as a natural reward curriculum.

5. **MCTS-compatible API surface.** Both AlphaProof and HTPS rely on tree search at inference. Expose `env.clone()` and `env.set_state()` to permit search-based policies — many top-performing symbolic-RL agents are search+policy, not pure policy-gradient.

6. **DreamCoder-style primitive promotion loop.** Successful op-compositions get crystallized as new tier-2/3 primitives in Techne's arsenal — directly mirrors `project_tiered_forge.md`. Make this loop a first-class env hook (`env.promote_skill(trace)`).

7. **Permutation-null reward sanity check baked into reward function.** Per `feedback_permutation_null` and `feedback_false_profundity`: every reward emission should optionally compute a permutation-null score. Refuses to reward agents for finding structure indistinguishable from chance — kills RL hacking before it starts.

## 4. Anti-Patterns

- **Token-level action spaces for symbolic tasks** (early code-synthesis RL): explodes branching factor, learns syntax not semantics. Mitigated by AlphaCode only via massive scale + filtering.
- **Terminal-only sparse reward** (HumanEval-RL, naive Lean-Gym): credit-assignment collapses on long episodes. AlphaProof needed shaped rewards even with MCTS.
- **Continuous parameterization of inherently discrete ops** (some early neural-theorem-prover attempts): no gradient signal that's meaningful for symbolic equality.
- **Single monolithic observation tensor** (some MathRL papers): hides the proof-graph structure that the policy actually needs.
- **Reward functions that don't penalize narrative inflation** — see `feedback_ai_to_ai_inflation`. Without permutation/null baselines, agents learn to produce *plausible-looking* claims, not true ones. Direct analog: reward hacking in code-synthesis envs that pass-by-overfit.
- **Locking the action vocabulary** — DreamCoder's wake-sleep proves the arsenal must evolve; freezing 2800 callables forever caps the achievable policy.

## 5. Concrete Next Steps for Techne's Pivot

Build `prometheus_gym/` with:

- `PrometheusEnv(gym.Env)` exposing `observation_space = Dict({claim_graph: GraphSpace, frontier: Sequence(ClaimID), arsenal_mask: MultiBinary(2800)})` and `action_space = Tuple(Discrete(5_op_families), Discrete(2800), Dict(args))`.
- `BIND` op resolves arsenal callable + type-checks args against substrate signatures; `EVAL` runs the bound op and yields a falsification trace.
- Reward = `sum(tier_weights * tiers_survived) - permutation_null_score - cost_penalty(wall_clock)`.
- `env.clone()` + `env.set_state()` for MCTS compatibility.
- `env.promote_skill()` hook writes successful op-traces to Techne's tier-2 inventory.
- Headless mode for Agora multi-agent rollouts; Redis-backed trace logging via existing Agora infrastructure.
- First milestone: replicate Charon's known PROMOTE on C11 scaling-law claim using a random policy as smoke test, then a tiny PPO baseline (3B-class model per `feedback_vram_ceiling`).

## 6. References

1. Yang, K. et al. (2023). *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models.* NeurIPS 2023. arXiv:2306.15626
2. Polu, S. & Sutskever, I. (2020). *Generative Language Modeling for Automated Theorem Proving.* arXiv:2009.03393
3. DeepMind (2024). *AI achieves silver-medal standard at IMO* (AlphaProof + AlphaGeometry 2). https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
4. Trinh, T. H. et al. (2024). *Solving olympiad geometry without human demonstrations.* Nature 625. DOI:10.1038/s41586-023-06747-5
5. Ellis, K. et al. (2021). *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning.* PLDI 2021. arXiv:2006.08381
6. Lample, G. et al. (2022). *HyperTree Proof Search for Neural Theorem Proving.* NeurIPS 2022. arXiv:2205.11491
7. Hendrycks, D. et al. (2021). *Measuring Coding Challenge Competence with APPS.* NeurIPS Datasets 2021. arXiv:2105.09938
8. Li, Y. et al. (2022). *Competition-level code generation with AlphaCode.* Science 378. DOI:10.1126/science.abq1158
9. Han, J. M. et al. (2022). *Proof Artifact Co-training for Theorem Proving with Language Models* (PACT). ICLR 2022. arXiv:2102.06203
10. Wu, Y. et al. (2022). *Autoformalization with Large Language Models.* NeurIPS 2022. arXiv:2205.12615
11. Towers, M. et al. (2023). *Gymnasium: A Standard API for Reinforcement Learning Environments.* https://gymnasium.farama.org/
12. Fey, M. & Lenssen, J. E. (2019). *Fast Graph Representation Learning with PyTorch Geometric.* ICLR Workshop. arXiv:1903.02428
13. Schrittwieser, J. et al. (2020). *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model* (MuZero — for `env.clone()` MCTS pattern). Nature 588. arXiv:1911.08265

---

Word count ~1150
