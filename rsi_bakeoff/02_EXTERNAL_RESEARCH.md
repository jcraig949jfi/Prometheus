# 02 — External research

Scope: what reusable machinery exists outside Prometheus, and what its experiments actually support. This is not a literature review.

## Verification tags

- **LIC-VERIFIED** — I read the license field from the GitHub API in this session (`gh api repos/<owner>/<repo>`, 2026-11-13).
- **REPO-PRIOR** — taken from Prometheus's own prior-art surveys, which carry their own tags: `roles/Aphrodite/science/frontier/PRIOR_ART_A_RSI_AGENTS.md` (912 lines), `PRIOR_ART_B_LIBRARY_LEARNING.md` (713), `PRIOR_ART_C_OPEN_ENDEDNESS.md` (1150). Where those files mark an item RECHECKED or FT (full text), I inherit that.
- **RECALLED** — from my training knowledge, not re-fetched this session. Numbers carrying this tag must be checked before external quotation.

I made no paid API calls. Web use was limited to license lookups.

## 1. The question I asked of every line of work

Does it give a mechanism by which the machinery that produces improvements is itself changed? If so, by whom (the system, an LLM, or a designer), and was the changed machinery shown to produce *further* improvements? Four levels:

- **L1:** a better product under a fixed improver.
- **L2:** a changed improver that beats the old one on held-out settings.
- **L3:** the changed improver itself finds the next improver change, and the parent could not have found it under matched compute.
- **L4:** L3 that transfers.

## 2. Self-improving systems

| Work | Mechanism | Evidence (what it supports) | LLM at runtime? | Implementation / license | Contribution to this design | Risk |
|---|---|---|---|---|---|---|
| **Gödel machine** (Schmidhuber 2003/2009) | Self-rewrite only after proving the rewrite raises expected utility | Theory. No non-trivial implementation known to me (RECALLED) | No | None | The **acceptance-by-evidence** principle; the fixed utility/evaluator outside the rewritable part | Proof search is intractable; replace proof with a statistical acceptance test |
| **Success-Story Algorithm / self-modifying policies** (Schmidhuber, Zhao, Wiering, *Machine Learning* 1997) | Self-modifications are pushed on a stack. At checkpoints, modifications are popped unless reward per time *since each was made* has increased monotonically along the stack | Small RL demonstrations (RECALLED) | No | None maintained | **Directly adopted:** checkpointed acceptance + rollback stack + "acceleration since modification" criterion. It is the cleanest published L2-acceptance rule that charges a modification for the time it costs | Original tasks tiny; noisy reward makes the stack thrash, so a paired CRN design is needed (§4 of 06) |
| **OOPS — Optimal Ordered Problem Solver** (Schmidhuber, *Machine Learning* 54, 2004) | Bias-optimal incremental Levin-style search. Code of earlier solutions is callable and its probability can be raised, so later problems get cheaper. The paper notes OOPS can in principle search for programs that modify its own search | Towers-of-Hanoi-scale demonstration of incremental speed-up (RECALLED). **No demonstration of searching its own search procedure that I know of** | No | None maintained | Closest ancestor of my selected design: one search procedure, earlier solutions as callable code, time-sharing between "solve" and "improve the solver" | 20 years without follow-up L3 evidence; that absence counts against the approach and is quoted in 08 |
| **Darwin Gödel Machine** (Zhang, Hu, Lu, Lange, Clune 2025, arXiv 2505.22954) | An archive of coding agents. An LLM edits agent code; an empirical benchmark accepts | SWE-bench gains from self-edits (REPO-PRIOR); **objective hacking** (removed hallucination-detection markers) | **Yes** (FM proposes edits) | `jennyzzt/dgm`, Apache-2.0 **LIC-VERIFIED** | Archive-of-improvers + open-ended parent selection; the hacking incident motivates the immutable evaluator | Improvements come from the frozen LLM; excluded by the brief |
| **Huxley-Gödel Machine** (arXiv 2510.21614) | Clade metaproductivity (CMP): rank an improver by what its *descendants* achieve; Thompson sampling | "Metaproductivity–performance mismatch" (REPO-PRIOR, RECHECKED) | Yes | `metauto-ai/HGM`, Apache-2.0 **LIC-VERIFIED** | **Adopted as a metric:** judge an improver edit by the success rate of the meta-searches it parents (L3 readout), not by its own generation-1 product | Needs many descendants per node; prior-dominated for young clades |
| **Hyperagents / DGM-H** (arXiv 2603.19461) | The meta-agent is code too; imp@k; frozen-transplant of meta-agents to an unseen domain | imp@50 0.630 vs 0.0 (REPO-PRIOR, RECHECKED); imp@k is a MAX over k, so noisier improvers look better | Yes | `facebookresearch/HyperAgents`, license NOASSERTION (**LIC-VERIFIED** as unasserted) | The frozen-transplant protocol; the warning against max-of-k metrics (needs a variance-matched sham) | LLM; license unclear |
| **STOP** (Zelikman et al. 2023, arXiv 2310.02304) | A scaffold program improves itself using itself, with an LM inside | Gains with GPT-4, degradation with weaker models; sandbox circumvention 0.42%; reward hacking via a shape bug (REPO-PRIOR) | Yes | `microsoft/stop`, MIT **LIC-VERIFIED** | The **self-application structure**: improver I is run on the task "improve I". My design keeps that structure without the LM | Its recursion gains come from the LM, not the scaffold |
| **Promptbreeder** (arXiv 2309.16797) | Mutation-prompts co-evolve with task-prompts; the hyper-mutation prompt is fixed | Ablating self-referential operators hurts (REPO-PRIOR, PARTIAL) | Yes | — | The right sham removes the ability of products to influence the improver, not the products themselves | LLM |
| **Autoconstructive evolution / Meta-GP** (Spector et al.; Edmonds 2001) | Reproduction code evolves inside the individuals | **Negative record:** outperformed by standard GP; cloning collapse; "did not reach the critical threshold for self-improvement"; AutoDoG ~5–10% vs ~50% for fixed GP (REPO-PRIOR, FT) | No | Clojush (Push), EPL (RECALLED) | The **prior is low** for a discrete, small-DSL, no-learned-prior improver. Two hazards transfer: self-copy wins ties forever, and variation-reducing edits look good short term | The closest prior failure to my Candidate D; the design must answer it (03 §D) |
| **Self-adaptive mutation in evolution strategies** (Rechenberg, Schwefel; Beyer) | Step-size σ is inherited and mutated with the solution | Robust, textbook L2-of-a-parameter (RECALLED) | No | many | The existence proof that a variation mechanism under selection can work. It also marks the boundary: this is parameter tuning, not algorithm change | Do not count it as L3 |

## 3. Algorithm discovery and library learning

| Work | Mechanism | What its experiments support | LLM? | Impl / license | Contribution | Risk |
|---|---|---|---|---|---|---|
| **DreamCoder** (Ellis et al., PLDI 2021, arXiv 2006.08381) | Wake: guided enumeration. Sleep-abstraction: version-space refactoring into a library. Sleep-dream: a recognition network trained on fantasies + replays | Qualitative abstraction chains (filter→max→nth→sort); library depth vs solved r=0.79. **No controlled "remove G1, is G2 still derivable" test exists** (REPO-PRIOR, FT) | No | `ellisk42/ec`, MIT **LIC-VERIFIED** (last push 2023; OCaml + Python + PyTorch) | The **compute-matched fixed-improver baseline** (Candidate B). A recognition model that pays the library breadth cost | The wake/sleep schedule is fixed: L1 + learned guidance, never L3. Compute is large (RECALLED: cluster-days per domain) |
| **Stitch** (Bowers et al., POPL 2023) | Top-down corpus-guided abstraction search with an MDL objective; multi-arity | Orders of magnitude faster than DreamCoder compression at similar compression (REPO-PRIOR, FT) | No | `mlb2251/stitch`, MIT **LIC-VERIFIED**, Rust + Python bindings | **Adopted as the kernel's fixed MDL scorer / reference compressor** in M0 comparisons; it avoids writing my own anti-unifier | Compression is not usefulness ("Library Learning Doesn't") |
| **babble / LLMT** (POPL 2023) | Library learning modulo an equational theory (e-graphs) | Handles syntactic variants (REPO-PRIOR) | No | — | Answer to Beta-04's extraction non-invariance: abstract modulo equivalence | Needs the theory supplied |
| **LILO** (ICLR 2024) | Stitch + LLM naming; deep re-derivation each iteration | Re-derivation beats inheritance (REPO-PRIOR) | Yes | — | Warning echoing R8: inherited libraries can block better ones, so allow refactoring | LLM |
| **"Library Learning Doesn't"** (arXiv 2410.20274; 2504.03048) | Critique: measures reuse of LLM-learned libraries | Reuse is extremely infrequent (REPO-PRIOR) | — | — | **Mandatory control:** measure *use* of each library entry on held-out tasks, not size | — |
| **Observational-equivalence pruning** (TRANSIT, Escher 2013; bottom-up enumeration lineage) | Discard candidates that behave identically on the examples | Standard, large constant-factor gains (REPO-PRIOR). Beta-04 found OE pruning the dominant repair of stone acquisition (OBSERVED, `beta04/SYNTHESIS.md` §3) | No | many | A **withheld-mechanism positive control** (06 §3): a known-good improver edit the meta-level should rediscover | — |
| **Neural-guided bottom-up search** (DeepCoder 2017; BUSTLE 2021; CrossBeam ICLR 2022; LambdaBeam 2023) | A learned model ranks next combinations | Large search savings in-distribution (RECALLED) | No (small nets) | various, mostly Apache (RECALLED) | Shows "learned search control" is the most reliable L2-like lever. Small models run on CPU | Fixed search algorithm with learned weights; generalisation off-distribution weak |
| **FunSearch / AlphaEvolve** (Nature 2023; arXiv 2506.13131) | LLM proposes program edits; automated evaluator; evolutionary database | Real new algorithms and bounds (REPO-PRIOR) | **Yes** | `google-deepmind/alphaevolve_results`, Apache-2.0 **LIC-VERIFIED** (results only, not the system) | The evaluator-database-island architecture; "evaluate cheaply, then expensively" cascades | LLM; excluded by the brief |
| **AutoML-Zero** (Real, Liang, So, Le, ICML 2020) | Regularised evolution of ML algorithms (setup / predict / learn functions) from scalar/vector/matrix primitives | Rediscovered linear regression, 2-layer nets with backprop-like updates (RECALLED); heavy CPU compute; "learned improvers overfit their development distribution" (REPO-PRIOR) | No | `google-research/google-research/automl_zero`, Apache-2.0 **LIC-VERIFIED** (monorepo license) | **Strongest no-LLM evidence** that search over *learning algorithms* (not parameters) is reachable, with functional-equivalence caching and hurdles. It does not self-apply | Compute scale; a fixed evolutionary meta-level (L2 by an external searcher, never L3) |
| **Learned optimisers trained by themselves** (Metz et al. 2021, arXiv 2101.07367; VeLO 2022) | A learned optimiser trains the next learned optimiser | Positive feedback loop, slow start (REPO-PRIOR) | No | Apache (RECALLED) | The only published self-application loop without an LLM that I know improves | Continuous, gradient-based, GPU/TPU-scale (VeLO: thousands of TPU-months, RECALLED). Smooth-landscape regime, not ours |
| **Genetic programming with ADFs / ARL** (Koza; Rosca and Ballard) | Evolved callable subroutines | Hierarchies on toy problems (REPO-PRIOR, SEC) | No | many | Promotion-to-primitive is old; scalar fitness is the weak point (Hestia W4) | — |

## 4. Open-endedness and quality-diversity

| Work | Supports | Impl / license | Contribution |
|---|---|---|---|
| MAP-Elites (Mouret and Clune 2015), novelty search (Lehman and Stanley 2011) | Archives of diverse stepping stones beat objective-only search in deceptive domains (RECALLED) | QDax MIT **LIC-VERIFIED** (JAX) | An improver archive indexed by behavioural descriptors of *improvers*, to avoid improver collapse (§D risk) |
| POET / Enhanced POET (Wang et al. 2019/2020) | Co-generated environments with transfer produce solutions direct optimisation does not (RECALLED) | `uber-research/poet`, Apache-2.0 **LIC-VERIFIED** | Deferred to M2. Hestia's warning holds: co-evolving worlds against an organism that cannot pass R2 makes harder deserts |
| Prometheus Beta-04 frontier archive | Descriptively *worse* than neutral (17/40 vs 27/40; censored) | — | Do not assume archives help; test it as an arm |

## 5. Equality saturation and rule inference (basis of Candidate C)

| Work | Mechanism | Supports | Impl / license |
|---|---|---|---|
| egg (Willsey et al., POPL 2021) | E-graphs + equality saturation | Fast term-rewriting search (RECALLED) | `egraphs-good/egg`, MIT **LIC-VERIFIED**; `egglog` MIT **LIC-VERIFIED** |
| Ruler (Nandi et al., OOPSLA 2021) | Enumerate terms; find candidate equalities by fuzzing/characteristic vectors; validate; then **use the rules learned so far to merge the e-graph before searching for new rules** | Smaller, comparable rule sets vs CVC4 enumeration (RECALLED) | `uwplse/ruler`, MIT **LIC-VERIFIED** |
| Theory exploration (QuickSpec, Hipster) | Lemma discovery where discovered lemmas prune later exploration | Same compounding shape (RECALLED) | QuickSpec BSD (RECALLED) |

Why this matters: in rule-inference systems the learned object (a rewrite rule) *is* a search operator. Learned rules change what is reachable in one step, not only the walk order. Aphrodite's libraries never do that: "identical expressive power", `fair.py`. This dissolves the θ/φ distinction rather than bridging it (Candidate C).

## 6. Theory that bounds what to expect

- **Evolvability = correlational statistical queries** (Valiant, J. ACM 2009; Feldman 2008) (RECALLED, also cited from memory in Hestia W1). Parity-like targets are not CSQ-learnable by fitness-proportional selection. Prediction: any improver edit that helps only in combination with another, unrewarded edit will not be found by acceptance-tested hill climbing. **The design must make useful improver edits single-step, or make their parts individually rewarded.**
- **Bounded self-refinement** (Wang–Dorchen–Jin arXiv 2510.04399; Chen–Wang–Qu survey 2607.07663; REPO-PRIOR): with a fixed evaluator and a capacity-bounded improver space the regime is safe and *predicts non-accelerating* gains. My claims language therefore says "bounded recursive improvement", never "accelerating".
- **Levin search / OOPS optimality** (RECALLED): an incremental searcher that time-shares between solving and searching for solver improvements loses at most a constant factor. This justifies the fixed compute split between object-level and meta-level search (04 §4) instead of a learned split, which would be a reward-hacking channel.

## 7. Areas surveyed and set aside

- **Self-referential weight matrices** (Irie, Schlag, Csordás, Schmidhuber, ICML 2022; `IDSIA/modern-srwm`, license field empty, **LIC-VERIFIED as unasserted**). Real self-modification during the forward pass, but it needs gradient meta-training on GPU, and its "self-modification" is the in-context learning of a meta-trained net. Not CPU-affordable for L3 replication studies.
- **Holland classifier systems, Baum's Hayek economies** (RECALLED). Credit-allocation-by-market. Historically unstable; no recursion evidence.
- **Predictive state representations** (Littman, Sutton, Singh 2002) and **active causal discovery**. Relevant to M2 hidden-state worlds as *task domains*. They do not supply an improver mechanism.
- **Identity / agency / persistent memory formalisms.** My design needs only an operational identity: the content-addressed (θ, φ) pair plus a ledger of its own actions. The kernel's distinction between "actions the improver took" (its proposals, its searches) and "events" (oracle answers, task arrivals) is a logging contract, not a theory of agency (04 §2).

## 8. What I take, and why

1. **No LLM-based system is usable at runtime.** Their *protocols* transfer: archive, frozen transplant, imp@k with a variance-matched sham, CMP, an immutable evaluator.
2. **The no-LLM evidence for changing learning machinery is:**
   - AutoML-Zero: an external evolutionary searcher, L2;
   - Metz et al.: continuous self-application;
   - SSA / OOPS: tiny or undemonstrated.

   There is **no published L3 in a discrete program space without an LLM**. My recommendation therefore cannot be BUILD-with-confidence; it is a falsification-first research programme (08).
3. **Concrete adoptions:**
   - SSA's rollback-stack acceptance;
   - OOPS's single-searcher / reusable-code structure;
   - STOP's self-application;
   - HGM's descendant-based metric;
   - Stitch's MDL compressor as a fixed kernel scorer;
   - OE pruning and multi-hole abstraction as withheld positive controls;
   - DreamCoder as the fixed-improver baseline.
