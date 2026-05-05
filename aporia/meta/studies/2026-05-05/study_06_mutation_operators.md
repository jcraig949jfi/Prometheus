# Study 06: Mutation Operators for Mathematical Objects

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Bottled-serendipity thesis, MAP-Elites operator classes, LLM-as-mutator empirical traction.

## Problem statement (Prometheus-adapted)

Prometheus's substrate plans to use LLMs as *mutation operators* over mathematical
objects (polynomials, knots, modular forms, sequences) and filter the output via
falsification. Ergon currently exposes five operator classes — `structural`,
`symbolic`, `anti_prior`, `uniform`, `structured_null` — over a MAP-Elites archive.
The substrate-design questions are:

1. Are there documented mutation classes from the math-AI literature absent from this list?
2. What hit rates (fraction of mutations producing something interesting vs garbage) does the literature actually report?
3. Has anyone formalized "interestingness" beyond intuitive judgment, with a measurable proxy?
4. Does the LLM-as-mutator framing have empirical traction, or is it bottled hype?

The honest summary up front: (1) yes, several documented classes are at least
partially absent, (2) hit rates are reported sparsely and almost never as the
single number Prometheus would want, (3) interestingness has been formalized
multiple times since AM/Eurisko but no consensus proxy has emerged, (4) FunSearch
and ELM are the strongest existence-proofs of LLM-as-mutator, but their published
metrics are dominated by *call counts* rather than *mutation hit rates*.

## Literature scan

**FunSearch (Romera-Paredes et al., Nature 2024).** The canonical LLM-as-mutator
result. The system samples k=2 programs from a database, feeds them to a code LLM
to "merge ideas," scores the output via a fixed evaluator, and admits surviving
programs to an island-structured archive. On the cap-set problem, FunSearch
required ~88,548 LLM calls to reach 75 points below optimal and ~1,732,100 calls
to reach optimum (DeepMind blog / Nature paper). The paper reports performance
*per call budget*, not *per mutation hit rate*. The substrate-relevant inference
is that the per-call yield is small enough that the headline metric is "calls to
discovery" rather than "fraction of useful mutations" — most mutations are
discarded. FunSearch's mutation operator class is closest to Prometheus's
`structural` (program edits respecting program syntax), though the islands
structure plus k=2 program prompting also approximates a crossover operator that
doesn't have a clean Prometheus analog.

**ELM / OpenELM (Lehman et al. 2022, arXiv:2206.08896; CarperAI library).**
Trains a *diff model* — a code LLM trained on Unified Diff edits — and uses it as
the mutation operator inside MAP-Elites. The Sodarace experiment generated
hundreds of thousands of working ambulating-robot programs in a domain absent
from training. The paper's empirical contribution is that learned-diff mutation
out-performs random mutation under a QD metric, but again headline results are
*archive coverage* and *QD-score*, not per-mutation hit rates. The diff-model
formulation is a mutation class Prometheus does not currently expose: *learned*
mutation conditioned on (current_object, target_intent). Prometheus's classes are
all distributionally specified, not learned.

**Eureqa / Schmidt-Lipson Pareto GP.** Eureqa (Schmidt & Lipson 2009;
commercialized by Nutonian) used Pareto optimization over (accuracy, complexity),
plus Age-Fitness Pareto (AFP) to reduce premature convergence and bloat. The key
mutation-operator design choice was the introduction of *age* as an objective —
this is a meta-operator on the population, not on individual objects, and has no
direct Prometheus analog. Eureqa's per-mutation hit rate is not reported in
canonical form; the paper's headline is "rediscovers Hamiltonians from raw
trajectories" rather than mutation statistics.

**Deep Symbolic Regression (Petersen et al. ICLR 2021; Landajuela et al. NeurIPS
2022).** RL-driven generation of expression trees with a recurrent policy network
and risk-seeking policy gradient. Recent extensions (Kamienny et al. ICML 2023,
Generative Symbolic Regression with MCTS) use *learned mutation models*
conditioned on (dataset, current expression). Equality-graph crossover (Aldeia
et al. 2025, arXiv:2501.17848) restricts the second parent to subtrees that
provably yield unvisited expressions — an explicit *novelty-enforcing* mutation
operator. Prometheus's `anti_prior` class is the closest match in spirit but the
e-graph mechanism is a much more disciplined enforcement.

**MAP-Elites foundations (Mouret & Clune 2015; Cully et al. 2015).** Standard
MAP-Elites uses Gaussian mutation, uniform parent sampling, and optional
crossover on similar niches. CMA-ME (Fontaine et al. 2020) replaces Gaussian with
CMA-ES emitters carrying their own covariance state. None of these explicitly
match `anti_prior` or `structured_null` — which appear to be Prometheus-novel
contributions sitting between standard QD operators and adversarial null-model
generation. This is potentially a real innovation worth documenting separately.

**AM / Eurisko (Lenat 1976, 1983; Ritchie & Hanna 1984; Lenat & Brown "Why AM
and Eurisko Appear to Work" 1984).** AM proposed concepts and conjectures using
~250 hand-coded interestingness heuristics. Eurisko added the ability to mutate
the heuristics themselves. The *retrospective verdict* (Ritchie/Hanna; Lenat's
own 1984 self-critique) is that AM's apparent productivity was largely an
artifact of (a) Lisp's property of making syntactic mutations frequently produce
semantically meaningful expressions, (b) hand-tuned heuristics matching the
specific domain, and (c) generous human interpretation of results. This is
*directly relevant* to Prometheus's bottled-serendipity thesis and is the
strongest historical *cautionary* evidence that LLM-as-mutator productivity may
be inflated by similar interpretive slack.

**Interestingness measures (Colton, Bundy, Walsh 2000; "On the notion of
interestingness in automated mathematical discovery").** Surveys ~10 systems
(AM, GT, Graffiti, HR, MCS, etc.) and identifies recurrent dimensions:
*novelty* (not previously generated), *surprisingness* (deviates from
expectation), *complexity* (description length of statement), *applicability*
(how often the concept is invoked elsewhere), *utility* (used in further
discovery). No single proxy is canonical; the consensus is that interestingness
is a *vector*, not a scalar. Graffiti (Fajtlowicz, 1980s+) is the strongest
positive existence-proof — it generated conjectures in graph theory using a
"Dalmatian heuristic" (a conjecture is interesting if it dominates known bounds
on at least one example) and several were proved by humans. The Dalmatian
heuristic is an interestingness proxy with operational teeth and is missing from
Prometheus's current vocabulary.

**MDL / Solomonoff-Kolmogorov frame.** MDL (Rissanen, Grünwald) gives a
principled compression-based proxy for "interesting structure" — shorter
description = more interesting pattern. This has been deployed in concept
analysis (Galbrun, Miettinen, Vreeken on FCA + MDL) but rarely in mathematical
conjecture generation directly. The Sleeping Beauties / Sigma kernel work
already in Prometheus is MDL-shaped at the meta level (the substrate prefers
short Sigma programs), so this connection is partly already made.

**OEIS variants.** OEIS (390K+ sequences as of late 2025) has an explicit
"variant" relation in cross-references but does not expose a canonical
"mutation operator" vocabulary. SuperSeeker runs many algorithms to find
related sequences but the relation graph is curator-built, not algorithmic.
There are documented cases where small variations on known sequences led to
new structure (the happy-numbers variant A351327; numerous Catalan-variant
sequences), but no systematic study of *which mutations on OEIS sequences
preserve mathematical interest* appears in the literature; this scan did not
identify one. This is a candidate Prometheus side-project: a mutation-class
audit on OEIS using the existing substrate.

**Isogeny graphs as mutation operators.** Isogeny is a documented
*structure-preserving* mutation on elliptic curves: an isogeny class shares
L-function, conductor, rank, and BSD invariants up to controlled scaling. The
isogeny graph is finite and well-studied (LMFDB exposes it directly). This is a
*proven* class of mathematical-object mutations that preserves a specific
collection of invariants — exactly the structure Prometheus's MAP-Elites would
want. Prometheus does not currently expose isogeny-as-mutation as a named
operator class. Other examples in the same family: Hecke operators on modular
forms, Reidemeister moves on knots, base-change on number fields, twist on
elliptic curves. These are not "mutation operators" in the GP sense — they are
*equivalence-preserving moves* — but for the substrate's purposes (generate
neighbors of a known object that share known structure), they are the
mathematically-grounded analog of the LLM-as-mutator workflow.

## Substrate-relevance

1. **Prometheus's five-class taxonomy is at least one or two classes short.**
   The literature consistently uses some combination of: random/Gaussian,
   crossover, learned (diff-model), structure-preserving (isogeny-like),
   novelty-enforcing (e-graph or archive-checked), and adversarial (anti-prior /
   null). Prometheus has the random/uniform end, the structural end, the
   adversarial pair (`anti_prior`, `structured_null`), and `symbolic`. Likely
   gaps: **(a) crossover** as a first-class operator (Prometheus appears to be
   single-parent), **(b) learned-mutation** (diff-model conditioned on intent),
   **(c) structure-preserving / equivalence-class** (isogeny, Reidemeister,
   Hecke).

2. **Hit-rate metrics are not standard.** No paper this scan reviewed reports a
   single "fraction of mutations that produce something interesting" number that
   Prometheus could anchor against. FunSearch reports calls-to-discovery, ELM
   reports QD-score, Eureqa reports Pareto fronts, DSR reports recovery rate on
   benchmark equation sets. Prometheus would be ahead of the literature merely
   by *measuring and publishing* per-class hit rates against a falsification
   battery. The Ergon promotion-ledger architecture is well-suited to this.

3. **Interestingness as a vector, not a scalar.** Colton-Bundy-Walsh's
   conclusion — interestingness is multi-dimensional — directly supports
   Prometheus's existing kill_vector primitive (per-component margins replacing
   categorical kill_path). The substrate should resist any pull to compress
   interestingness to a single score; the multi-component shape is correct on
   independent grounds.

4. **The LLM-as-mutator thesis has *thin* but real empirical traction.**
   FunSearch (cap set, online bin packing) and ELM (Sodarace) are existence
   proofs. The cautionary tale is AM/Eurisko: apparent productivity often
   reflects *interpretive slack*, not real discovery. Prometheus's calibration
   discipline (kill-everything, null protocol, base 10 is human artifact) is the
   correct prophylactic; the substrate should *expect* most LLM mutations to be
   garbage and design throughput accordingly.

## Concrete operational handles

1. **Add three named mutation classes to the Ergon taxonomy** (proposed names):
   `crossover` (two-parent recombination), `learned_diff` (LLM/diff-model edit
   conditioned on intent), `equivalence_preserving` (isogeny / Reidemeister /
   Hecke / twist — mathematically-defined moves that preserve named
   invariants). The third class is the most undervalued: it grounds the
   substrate in real mathematics rather than syntactic perturbation, and gives
   Charon and Agora a vocabulary for *targeted* mutations that respect known
   structure.

2. **Instrument per-class hit-rate measurement in Ergon's promotion ledger.**
   For each mutation, record: operator class, parent(s), child, kill_vector
   components, and whether the child cleared a falsification threshold.
   Aggregate to per-class hit rates. The literature does not report this number;
   Prometheus would be in a position to publish it. Recommend a frozen
   benchmark task set (analogous to the deg-14 ±5 palindromic subspace work) so
   the rate is comparable across substrate iterations.

3. **Adopt a Dalmatian-style novelty proxy** for the `anti_prior` class:
   a mutation is interesting iff it *dominates* a known bound or *falsifies*
   a known regularity on at least one tested example. This is the operational
   form Graffiti used, and it is much sharper than "is in a previously empty
   archive bin." Suggest combining: (Dalmatian dominance) AND (archive
   novelty) AND (passes one falsification gate) before promotion.

4. **Tag the existing Sigma kernel opcodes with a Bourbaki-axis label** (cf.
   Study 01 recommendation) so the `equivalence_preserving` class can be
   organized by what kind of structure each operator preserves (algebraic /
   order / topological / mixed). This makes the operator class searchable for
   Charon's bridge-discovery workflow.

5. **Treat AM/Eurisko as the cautionary-tale baseline.** Add a kill_vector
   component "interpretive slack" — a discount applied when a "discovery" is
   ratified only by LLM-generated narrative rather than by independent
   falsification. This is a direct application of feedback_ai_to_ai_inflation
   (two AIs amplify narrative instead of falsifying) and feedback_assume_wrong.

## Falsification

The central operational claim — *Prometheus's five-class taxonomy is missing
at least crossover, learned-diff, and equivalence-preserving classes, and these
are mathematically meaningful additions* — would be refuted by:

- A published benchmark showing that adding crossover, diff-model, or
  equivalence-preserving mutation to a MAP-Elites mathematical-discovery
  pipeline does not improve QD-score, archive coverage, or discovery rate
  beyond the existing Prometheus operator set.
- A demonstration that one of the existing Prometheus classes already
  *implements* the proposed missing class under a different name (in which
  case the recommendation collapses to a relabeling, not an addition).
- An ablation in Ergon showing that hit rate is independent of operator class
  on a representative task set — which would mean the class taxonomy is
  decorative and the substrate has been doing something else load-bearing.

The bottled-serendipity thesis itself is harder to falsify cleanly. The
strongest negative test would be: run a Prometheus task with LLM-as-mutator
*disabled* (only `structural` + `uniform` + `structured_null`) versus enabled
(all five), and measure per-call discovery rate. If LLM-as-mutator does not
beat the random/structural baseline at fixed compute, the thesis is in
trouble.

## Open questions raised

1. Are `anti_prior` and `structured_null` Prometheus-novel contributions, or
   are they renamings of existing QD literature ideas? If novel, they are worth
   a separate writeup.
2. Is there a publishable per-class hit-rate measurement using Ergon's
   promotion ledger on a frozen benchmark? The literature appears not to have
   this number.
3. Could the Sigma kernel's BIND / EVAL pair be used to express
   equivalence-preserving mutations as first-class kernel ops (e.g.,
   `BIND isogeny EVAL`)? This would unify the proposed `equivalence_preserving`
   class with the existing kernel rather than adding it as a side-channel.
4. Does the Dalmatian heuristic survive when applied to the substrate's actual
   open questions (Aporia's 322), or is it too easily satisfied by trivial
   counterexamples?
5. What fraction of FunSearch's 1.7M calls produced syntactically valid but
   uninteresting outputs vs syntactically invalid outputs vs interesting
   outputs? The published paper does not break this down; if the breakdown
   exists in supplementary material, it would directly calibrate Prometheus's
   own throughput expectations.

## Citations

- Romera-Paredes, B., et al. "Mathematical discoveries from program search with large language models." *Nature* 625, 468–475 (2024). https://www.nature.com/articles/s41586-023-06924-6
- DeepMind blog: FunSearch. https://deepmind.google/discover/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/
- google-deepmind/funsearch (code). https://github.com/google-deepmind/funsearch
- Lehman, J., et al. "Evolution Through Large Models." arXiv:2206.08896 (2022). https://arxiv.org/abs/2206.08896
- CarperAI. OpenELM library. https://github.com/CarperAI/OpenELM
- Schmidt, M., Lipson, H. "Distilling Free-Form Natural Laws from Experimental Data." *Science* 324, 81–85 (2009). (Eureqa basis; AFP method.)
- Petersen, B. K., et al. "Deep Symbolic Regression: Recovering mathematical expressions from data via risk-seeking policy gradients." ICLR 2021. https://openreview.net/forum?id=m5Qsh0kBQG
- Kamienny, P.-A., et al. "Deep Generative Symbolic Regression with Monte-Carlo-Tree-Search." ICML 2023. https://proceedings.mlr.press/v202/kamienny23a.html
- Aldeia, G. S. I., et al. "Improving Genetic Programming for Symbolic Regression with Equality Graphs." arXiv:2501.17848 (2025). https://arxiv.org/abs/2501.17848
- Mouret, J.-B., Clune, J. "Illuminating search spaces by mapping elites." arXiv:1504.04909 (2015). https://arxiv.org/abs/1504.04909
- Cully, A., et al. "Robots that can adapt like animals." *Nature* 521, 503–507 (2015).
- Fontaine, M. C., et al. "Covariance Matrix Adaptation for the Rapid Illumination of Behavior Space" (CMA-ME). GECCO 2020. arXiv:1912.02400.
- Lenat, D. B., Brown, J. S. "Why AM and EURISKO appear to work." *Artificial Intelligence* 23(3), 269–294 (1984). https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=37ab31f586cdc1efc3bf0dcc9ba52f644077e466
- Lenat, D. B. "Theory Formation by Heuristic Search." *Artificial Intelligence* 21, 31–59 (1983). https://users.cs.northwestern.edu/~mek802/papers/not-mine/Lenat_1983_theory_formation_by_heuristic_search.pdf
- Colton, S., Bundy, A., Walsh, T. "On the notion of interestingness in automated mathematical discovery." *International Journal of Human-Computer Studies* 53(3), 351–375 (2000). https://cgi.cse.unsw.edu.au/~tw/IJHCS00.pdf
- Fajtlowicz, S. "On conjectures of Graffiti." Multiple papers, 1986+. (Dalmatian heuristic.)
- Grünwald, P. "Minimum Description Length Principle." MIT Press (2007). https://en.wikipedia.org/wiki/Minimum_description_length
- LMFDB. "Isogeny graph of an isogeny class of elliptic curves." https://www.lmfdb.org/knowledge/show/ec.isogeny_graph
- OEIS. https://oeis.org/ ; A351327 (happy-numbers variant). https://oeis.org/A351327
- Internal: `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`; `F:/Prometheus/ergon/learner/promotion_ledger.py`; `F:/Prometheus/prometheus_math/KILL_VECTOR_SPEC.md`; feedback files `feedback_ai_to_ai_inflation.md`, `feedback_assume_wrong.md`, `feedback_replicate_seeds.md`, `feedback_calibration.md`.

*This scan did not identify a published per-class mutation hit-rate benchmark
for symbolic-discovery pipelines. If one exists, this report under-cites it.
The claim that `anti_prior` and `structured_null` are Prometheus-novel is
based on absence of a clean match in the QD literature reviewed here, not on
exhaustive search; treat as a hypothesis for separate verification.*
