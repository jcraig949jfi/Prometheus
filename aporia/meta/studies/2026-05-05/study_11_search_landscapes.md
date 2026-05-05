# Study 11: Search Landscapes of Open Problems

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** MAP-Elites archive design; descriptor axis derivation
from proof-search literature; landscape-structure-by-domain.

## Problem statement (Prometheus-adapted)

The substrate just produced a Case A finding: its RL search agent collapsed
to modal-class predictions because the search landscape it was asked to
traverse was, from its perspective, *flat*. The architectural consequence is
that any MAP-Elites-style archive needs descriptor axes that actually carve
the search space into bins where local quality varies, otherwise the archive
degenerates into a multi-bucket histogram of the same finding.

This study asks: does the proof-search literature (Lean tactic search, Coq
automation, AlphaProof, GPT-f, DeepSeek-Prover, FunSearch as a contrast
case) give Prometheus *predictive* structure for landscape design? More
specifically:

1. What does empirical evidence say about local-vs-global structure in proof
   search?
2. Should Ergon's 5-axis descriptor (canonicalizer subclass / DAG entropy /
   output type / magnitude bucket / canonical-form distance) be reorganised
   based on proof-search analogs?
3. What is the actual difference between *proof-space landscape* (the
   theorem-proving literature) and *candidate-object landscape* (what
   Prometheus operates on), and is the metaphor transferable?
4. Does landscape *structure* differ by mathematical domain in a documented,
   load-bearing way?

Headline summary up front: (a) proof-search landscapes have *measurable*
funnel/multi-funnel structure in adjacent search problems (SAT, GP, QAP) and
strong qualitative evidence of similar structure in tactic search, but (b)
no published study cleanly characterises the proof-space landscape with
autocorrelation length, local-optima-network statistics, or basin diameter
in the way fitness-landscape analysis does for combinatorial optimisation;
(c) the proof-space-vs-object-space distinction is real and the substrate
operates almost entirely on the *object* side, which means the proof-search
literature is *analogically suggestive*, not directly transferable; (d)
domain-by-domain landscape structure is anecdotal in the literature, not
quantified.

## Literature scan

**AlphaProof (Nature 2025; DeepMind).** Olympiad-level proofs in Lean via a
proof network producing (top-N tactic candidates, value estimate) feeding a
tree search. The relevant landscape detail: AlphaProof uses *minimum* return
across independent subgoals rather than sum, which means the value landscape
is shaped by the *worst* unfinished subgoal — analogous to defining fitness
as the bottleneck dimension of a multi-objective problem rather than its
average. This is a *deliberate landscape-shaping* choice; it makes the proof
landscape less rugged at the cost of conservatism, because partial progress
on easy subgoals is not rewarded until the hardest is also closed
[https://www.nature.com/articles/s41586-025-09833-y].

**GPT-f (Polu & Sutskever 2020, arXiv:2009.03393).** Best-first proof tree
search over Metamath, expanding goals by cumulative tactic log-probability.
Reports new short proofs accepted into the Metamath library — the first
deep-learning system to contribute to a formal library. The implicit
landscape model is *log-prob priority as heuristic value*; no published
fitness-landscape analysis (autocorrelation, local-optima network) was
performed, but the system's success implies the LM-induced ordering on
tactics is informative — i.e., the landscape is non-flat under that
heuristic.

**DeepSeek-Prover-V1.5 (arXiv:2408.08152).** Combines whole-proof generation
with MCTS, introducing RMaxTS — an *intrinsic-reward-driven* exploration
strategy explicitly motivated by *reward sparsity*. The truncate-and-resume
mechanism is a landscape-aware design: when a proof segment fails, truncate
at the first error and resume, treating the prefix as a partial elite. This
is functionally a *single-axis MAP-Elites* on prefix-length. It implies the
designers believe the landscape has dense partial-credit structure even
though terminal credit is sparse [https://arxiv.org/abs/2408.08152].

**BFS-Prover and LeanTree (2025).** BFS-Prover (arXiv:2502.03438) reports
that scalable best-first tree search over LLM-generated tactics is
competitive with MCTS while being simpler — implying the proof landscape is
not so deceptive that exploration heuristics dominate. LeanTree (arXiv:
2507.14722) factorises proof state into independent subgoals to prune
redundant search; the empirical claim is that subgoal independence is the
dominant feature, again pointing at *structured* (not maximally rugged)
landscape geometry.

**FunSearch (Romera-Paredes et al., Nature 2024).** Not a proof-search
system but the closest published QD analog to what Prometheus does. Uses
island-structured archive with k=2 program prompting, ~1.7M LLM calls to
reach optimum on cap set. Already analysed in Study 06; relevant here as a
contrast — FunSearch operates on *candidate object space* (programs), not
*proof space*.

**Fitness-landscape analysis literature (Stadler, Verel, Ochoa, Tomassini).**
A mature quantitative framework for combinatorial landscapes: autocorrelation
length (Weinberger 1990), local optima networks (LONs; Ochoa et al. 2008,
2014), funnel decomposition (Ochoa & Veerapen 2018), neutrality measures.
Applied extensively to TSP, QAP, SAT, NK landscapes. The single most
transferable empirical finding: *easy instances feature a single dominant
funnel; hard instances feature many sub-optimal funnels that trap local
search* [https://link.springer.com/chapter/10.1007/978-3-030-58115-2_9;
https://hal.science/hal-04029576/file/ppsn2020-tuto-fitness-landscapes.pdf].

**SAT phase transition / proof complexity.** Random k-SAT proof landscapes
have been studied across the satisfiability phase transition. The number,
size, and connectivity of local/global optima change sharply at the
transition; tree-resolution proofs are short on structured (real-world)
instances and long on random instances at threshold density. This is the
single most precise documented case of *landscape structure varying by
problem class*, and it is in a domain (SAT) not mathematics-of-research.

**Heavy-tailed runtimes.** Gomes, Selman, Crato (1997) showed backtracking
ATP runtimes follow heavy-tailed distributions; Luby's restart strategy
gives O(T(τ*) log T(τ*)) expected runtime under a known optimum. This is a
*landscape-implication* finding — heavy tails imply most starting points
lead to long fruitless walks but a small fraction reach the goal quickly.
Operationally: the proof landscape has *narrow basins of attraction to
short proofs* surrounded by very large basins of attraction to dead ends.

**Cellucci / Blanchette-style analysis ("On the difficulty of discovering
mathematical proofs," Synthese 2023).** Philosophical/qualitative argument
that proof discovery has three scaffolded difficulty types: (Type 1)
formulating the problem precisely; (Type 2) lacking a plausible proof
outline; (Type 3) carrying technical details through a known outline. Not
empirical landscape analysis but a useful taxonomy: Prometheus's substrate
operates almost entirely in Type 3 + a sliver of Type 2; AlphaProof
operates in Type 3 only.

**MAP-Elites descriptor literature.** Descriptor design is consistently
called the load-bearing decision in QD (Cully et al. 2015; Mouret & Clune
2015; Fontaine et al. 2020 CMA-ME; Faldor & Cully 2023 DCG-MAP-Elites
arXiv:2303.03832). The community standard is: (i) descriptors should be
behaviourally meaningful, (ii) low-dimensional (3-6 axes), (iii) ideally
*causally upstream* of the fitness rather than redundant with it. No
proof-search system this scan reviewed uses a multi-axis descriptor in the
MAP-Elites sense — they all use single-axis priority queues or MCTS
visit-count heuristics.

## Substrate-relevance

1. **The proof-space-vs-object-space distinction is load-bearing.** Lean,
   GPT-f, DeepSeek-Prover all search *over proof states* (sequences of
   tactic applications), where the landscape's vertical axis is "distance
   to QED" and the horizontal axes are tactic-state features. Prometheus's
   Ergon archive searches *over candidate objects* (genomes evaluating to
   polynomials, sequences, modular forms), where the vertical axis is a
   kill_vector / falsification margin and horizontal axes are
   canonicalizer-subclass / DAG entropy / etc. *These are different
   problems.* Importing proof-search heuristics into the substrate
   wholesale is a category error. What *can* be imported is the
   methodological apparatus of fitness-landscape analysis (autocorrelation,
   LONs, funnel decomposition).

2. **The Case A finding is consistent with multi-funnel landscape
   pathology.** When a search agent collapses to modal predictions, the
   diagnosis from fitness-landscape analysis would be one of: (a) the
   landscape has a single very wide flat basin (low autocorrelation across
   any direction the agent samples), (b) the agent's mutation operator
   distribution is concentrated at the modal class so it cannot escape, or
   (c) the descriptor axes are correlated with the modal output and so the
   "diversity" the agent thinks it is producing is actually one cell in
   five projections. These are *testable* with the fitness-landscape
   toolkit. The fill-rate audit Ergon already implements
   (`compute_fill_rates` in `ergon/learner/descriptor.py`) is a partial
   instance of this — the |corr|>0.7 axis-pair flag is exactly the
   redundancy check the QD literature recommends.

3. **Ergon's 5-axis descriptor is *not* derivable from proof-search
   literature.** It is derivable from canonicalisation theory and category
   theory of mathematical objects (which is what `arsenal_meta` is built
   on). The proof-search literature does not have an analog of "output
   canonicalizer subclass" because it doesn't deal in objects, only in
   proof terms. So the substrate cannot crib axes from proof search; it
   has to design them from object-space considerations, which Ergon
   already does. What proof search *does* offer: the *meta-level* lesson
   that single-axis priority (GPT-f) and intrinsic-reward exploration
   (DeepSeek RMaxTS) both work because they are designed against an
   independently-validated landscape structure. Ergon's analog would be
   to validate its 5-axis descriptor against measured landscape geometry
   *before* further axis additions.

4. **Domain-by-domain landscape structure is anecdotal.** The literature
   does not provide a clean comparison of landscape ruggedness in number
   theory vs topology vs combinatorics for proof search. mathlib coverage
   is uneven (heavy in algebra, light in topology and analytic NT;
   FormalMATH benchmark notes heavy domain bias in prover performance) but
   this is *coverage* bias, not *landscape* bias. The claim that "topology
   has long inferential chains, NT has short surprising leaps,
   combinatorics has rugged dense plateaus" is folklore. Treating it as
   measured fact would be inflating the literature.

## Concrete operational handles

1. **Adopt fitness-landscape-analysis instrumentation as a new Ergon
   audit class.** Specifically: (a) measure descriptor-axis autocorrelation
   along random walks in the archive (Weinberger autocorrelation length per
   axis); (b) build a Local Optima Network of the archive's elite set,
   where edges are operator-class-induced transitions, and report the
   number of funnels; (c) report neutrality (fraction of mutations
   producing identical kill_vector) per operator class. This generalises
   the existing `compute_fill_rates` audit. The first paper-quality result
   would be a measured autocorrelation length per axis on a frozen task
   set — the literature does not have this number for math-discovery QD
   pipelines.

2. **Treat the Case A flat-landscape finding as a landscape-measurement
   call to action, not just an RL-architecture indictment.** Run the
   Weinberger autocorrelation test on the same trajectories that produced
   the modal-collapse finding. If autocorrelation length on the kill_vector
   axis is short (rugged) but the agent is still collapsing, the agent is
   miscalibrated. If autocorrelation is long (flat), the descriptor and
   reward shaping are at fault, not the agent. This bisects the diagnosis.

3. **Borrow DeepSeek-Prover's intrinsic-reward / curiosity exploration
   under the right framing.** RMaxTS adds intrinsic reward when terminal
   reward is sparse. Ergon's `kill_vector` is a *vector* margin precisely
   so it is dense; intrinsic reward as a curiosity bonus would be a
   second-order signal for exploration, not a replacement. Suggest a
   per-cell visit-count-discounted bonus when selecting parents from the
   archive — this is a small, well-scoped addition.

4. **Resist landscape-metaphor over-claiming.** "Mathematical research has
   landscape structure" is defensible *for the substrate's specific
   choice of object space and falsification metric*. It is *not*
   defensible as a general claim about open mathematical problems, because
   the literature does not yet support such a claim with measured
   autocorrelation, LON statistics, or basin counts. The substrate should
   document its own landscape *as it measures it*, and avoid retrofitting
   theorem-proving's loose landscape vocabulary onto it.

## Falsification

The central operational claim — *fitness-landscape-analysis instrumentation
(autocorrelation length, LONs, funnel count) on Ergon's archive will produce
substrate-relevant signal that the existing fill-rate audit does not* —
would be refuted by:

- A measurement showing that on a frozen Ergon task set, descriptor-axis
  autocorrelation length is uniform across operator classes and is not
  predictive of which operator class produces interesting children. (Then
  the FLA toolkit gives no useful signal for Prometheus-scale archives.)
- A demonstration that the existing kill_vector + fill_rate audit already
  captures the same information that LON statistics would, in which case
  LONs are redundant.
- An ablation showing that adding an intrinsic-curiosity bonus to Ergon's
  parent selection does not improve discovery rate beyond the existing
  selection rules — refuting the DeepSeek-style transfer.

The narrative claim — *proof-space landscape structure transfers to
object-space landscape structure for mathematical discovery* — would be
refuted by any direct attempt that fails: e.g., porting GPT-f's tactic-
log-prob priority to Ergon's operator selection and getting no lift. The
prediction here is that it would not transfer cleanly, because the two
search problems are structurally different.

## Open questions raised

1. Is there a published autocorrelation-length measurement for *any*
   mathematical-discovery search landscape? This scan did not find one. If
   none exists, Prometheus could publish the first.
2. Does the Case A modal-collapse finding survive a re-run with
   higher-resolution descriptor axes (e.g., split magnitude_bucket from
   bounded ranges into log-uniform fine-grained buckets)? If yes, the
   problem is not descriptor resolution.
3. Could AlphaProof's "minimum return over independent subgoals" landscape
   shaping be ported to Ergon's kill_vector aggregation? Currently
   kill_vector aggregates by margin sum / mean; using min would be a
   one-line change with potentially large landscape effects.
4. Is the proof-space-vs-object-space distinction itself a category error?
   For domains where the object *is* a proof (e.g., Sigma-kernel programs
   in Prometheus), the two collapse. This is worth examining as part of
   the BIND/EVAL semantics work in Study 15.
5. Does the substrate's existing `arsenal_meta` taxonomy implicitly encode
   a landscape geometry that nobody has read off explicitly? The
   `canonicalizer_subclass` axis suggests yes; an explicit reading would
   be a small project.

## Citations

- AlphaProof team (Google DeepMind). "Olympiad-level formal mathematical reasoning with reinforcement learning." *Nature* (2025). https://www.nature.com/articles/s41586-025-09833-y
- Polu, S., Sutskever, I. "Generative Language Modeling for Automated Theorem Proving." arXiv:2009.03393 (2020). https://arxiv.org/abs/2009.03393
- Xin, H., et al. "DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search." arXiv:2408.08152 (2024). https://arxiv.org/abs/2408.08152
- Xin, R., et al. "BFS-Prover: Scalable Best-First Tree Search for LLM-based Automatic Theorem Proving." arXiv:2502.03438 (2025). https://arxiv.org/html/2502.03438
- "LeanTree: Accelerating White-Box Proof Search with Factorized States in Lean 4." arXiv:2507.14722 (2025). https://arxiv.org/html/2507.14722v1
- Romera-Paredes, B., et al. "Mathematical discoveries from program search with large language models." *Nature* 625, 468–475 (2024). https://www.nature.com/articles/s41586-023-06924-6
- Mouret, J.-B., Clune, J. "Illuminating search spaces by mapping elites." arXiv:1504.04909 (2015). https://arxiv.org/abs/1504.04909
- Cully, A., et al. "Robots that can adapt like animals." *Nature* 521, 503–507 (2015).
- Faldor, M., Cully, A. "MAP-Elites with Descriptor-Conditioned Gradients and Archive Distillation into a Single Policy." arXiv:2303.03832 (2023). https://arxiv.org/abs/2303.03832
- Weinberger, E. D. "Correlated and uncorrelated fitness landscapes and how to tell the difference." *Biological Cybernetics* 63, 325–336 (1990). https://link.springer.com/article/10.1007/BF00202749
- Stadler, P. F. "Fitness Landscapes." (preprint compendium). https://www.bioinf.uni-leipzig.de/~studla/Publications/PREPRINTS/01-pfs-004.pdf
- Verel, S. "Tutorial on Fitness landscape analysis." PPSN 2020. https://hal.science/hal-04029576/file/ppsn2020-tuto-fitness-landscapes.pdf
- Ochoa, G., Veerapen, N. "Mapping the global structure of TSP fitness landscapes." *Journal of Heuristics* 24, 265–294 (2018).
- Ochoa, G., Tomassini, M., Vérel, S., Darabos, C. "A Study of NK Landscapes' Basins and Local Optima Networks." Tomassini-Ochoa LON literature. https://link.springer.com/chapter/10.1007/978-3-642-41888-4_9
- Pérez Cáceres, L., Pavelka, T., et al. "Global Landscape Structure and the Random MAX-SAT Phase Transition." (2020). https://link.springer.com/chapter/10.1007/978-3-030-58115-2_9
- Gomes, C. P., Selman, B., Kautz, H. "Boosting Combinatorial Search Through Randomization." AAAI 1998. (Heavy-tailed runtimes.) Cited via https://timvieira.github.io/blog/post/2019/09/06/the-restart-acceleration-trick-a-cure-for-the-heavy-tail-of-wasted-time/
- Luby, M., Sinclair, A., Zuckerman, D. "Optimal speedup of Las Vegas algorithms." *Information Processing Letters* 47, 173–180 (1993).
- Cellucci, C. "On the difficulty of discovering mathematical proofs." *Synthese* 202 (2023). https://link.springer.com/article/10.1007/s11229-023-04184-5
- "FormalMATH: Benchmarking Formal Mathematical Reasoning." arXiv:2505.02735. https://arxiv.org/pdf/2505.02735
- Internal: `F:/Prometheus/ergon/learner/descriptor.py` (5-axis CellCoordinate, compute_fill_rates audit); `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`; `F:/Prometheus/aporia/meta/studies/2026-05-05/study_06_mutation_operators.md` (FunSearch / ELM context); feedback files `feedback_assume_wrong.md`, `feedback_calibration.md`, `feedback_narrative_resistance.md`, `feedback_ai_to_ai_inflation.md`.

*This scan did not identify any published fitness-landscape analysis
(autocorrelation length, local optima network, funnel decomposition) on a
mathematical-discovery search problem at Prometheus's level of abstraction.
The claim that none exists is based on absence in this scan, not exhaustive
search; treat as a hypothesis worth a literature follow-up. The transfer
from proof-search to object-search is treated here as analogically
suggestive at best, not as direct portability.*
