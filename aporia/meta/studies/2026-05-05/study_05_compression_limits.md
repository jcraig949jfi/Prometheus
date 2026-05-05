# Study 05: Symbolic Compression Limits

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Whether the Sigma kernel's 7 opcodes (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) plus BIND/EVAL is at a defensible "minimum" for substrate-grade properties, and whether further compression of the substrate's symbolic surface would help or hurt discovery.

## Problem statement (Prometheus-adapted)

Two compression questions sit at different layers of the substrate and must not be conflated:

1. **Control-plane compression (Sigma kernel):** Are 7 opcodes + BIND/EVAL the smallest set that preserves the *substrate-grade* invariants — append-only storage, linear capability tokens, three-valued GATE semantics, falsification-first promotion, content-addressed provenance — listed in `sigma_kernel/README.md`?
2. **Data-plane compression (mathematical objects represented in the substrate):** When Prometheus encodes a theorem, equation, or invariant as a symbolic string for `CLAIM`/`PROMOTE`, what is the empirical state-of-art on minimum-symbol representation, and does shorter representation help or hurt downstream discovery?

These are different questions with different literatures. Kolmogorov complexity bounds the data plane (uncomputable, but relevant). Combinator-calculus and proof-system minimization bound the control plane. The literature is more useful for question (1) than for (2): there are tight, proven minimal bases for combinatory logic, but the empirical "compression vs discovery" trade-off in symbolic regression is mostly anecdotal.

## Literature scan

**Theoretical floor (Kolmogorov / algorithmic information).** K(x) is uncomputable (Li & Vitányi, *An Introduction to Kolmogorov Complexity and Its Applications*, 4th ed., 2019, ch. 2). Practical proxies are upper bounds via specific compressors (LZ77, BDM, NCD). Soler-Toscano et al.'s Block Decomposition Method (Soler-Toscano, Zenil, Delahaye, Gauvrit, *PLOS ONE* 2014, "Calculating Kolmogorov Complexity from the Output Frequency Distributions of Small Turing Machines") gives the best-known empirical estimator for short strings via the Coding Theorem Method. Implication for Prometheus: there is no algorithm that returns "the" minimal representation; any compression metric the substrate uses is necessarily a compressor-relative proxy.

**Combinatory logic — proven minimal bases.** Schönfinkel (1924) and Curry showed `{S, K}` generates all of combinatory logic; `I = SKK`. Smaller still: Iota combinator `ι = λf. f S K` is a single combinator that generates `S` and `K`, hence everything (Barker, "Iota and Jot," 2001, http://semarch.linguistics.fas.nyu.edu/barker/Iota/). Even smaller: the X combinator (Goldberg) and Tromp's binary lambda calculus give universal Turing-completeness from 1 primitive plus application. **This is the cleanest "how small can it go" answer in the entire literature** — the floor is 1 primitive, but only by paying enormous expansion cost in term length. SK-translations of even small lambda terms blow up super-linearly; iota-translations explode further. This *is* the compression-vs-usability trade-off, made formal.

**Proof minimization.** Hutter prizes and the Solomonoff-induction tradition treat "shortest program" as the gold standard. In actual proof assistants: Mizar/MML, Coq/Rocq, Lean mathlib all support tactic-level minimization (Lean's `minImports`, `polyrith` solving in fewer steps than `linarith` chains; Coq's `Tactician` for tactic suggestion). Empirical result across communities: aggressive minimization often produces proofs that are *shorter but less readable and harder to maintain* — the explicit/implicit trade-off documented in Wiedijk's "The De Bruijn factor" (~4× expansion of formal vs informal text holds remarkably stable across systems and decades; http://www.cs.ru.nl/~freek/factor/factor.pdf). The substrate-relevant lesson: there exists an apparent invariant ratio between informal and minimum-formal length, suggesting a *practical* compression floor distinct from the theoretical one.

**Symbolic regression — minimum symbol counts for discovered equations.**
- **AI Feynman 2.0** (Udrescu, Tegmark et al., *Sci. Adv.* 2020, arXiv:2006.10782; arXiv:1905.11481): rediscovers 100/100 Feynman lectures equations and 73/100 "bonus" equations. Uses Pareto-frontier of (description-length, accuracy). Reported equation lengths typically 3–15 symbols using a fixed primitive set of `{+, -, *, /, sqrt, exp, log, sin, cos, arcsin, tanh, **, π}`. The paper explicitly tracks symbol count as the compression axis and argues that physics equations cluster at low symbol-count even when fit equally well by longer expressions — a *physics* observation that may not transfer.
- **PySR / SymbolicRegression.jl** (Cranmer, arXiv:2305.01582): Pareto-frontier multi-objective search; the documented "best practice" is to NOT pick the smallest expression but the elbow of the Pareto curve. Concrete operational claim: minimum-length is rarely the most useful representation.
- **FunSearch** (Romera-Paredes et al., *Nature* 624, 2023): uses LLM-generated Python functions, not minimum-symbol expressions. Notable: the cap-set lower-bound program is a few dozen lines; the bin-packing heuristic is similarly compact. But these are programs in a Turing-complete language with libraries, not minimum-primitive representations. The "compression" is in *finding* the program, not in primitive-count.
- **Eureqa** (Schmidt & Lipson, *Science* 324, 2009): historical baseline — uses GP over `{+, −, ×, ÷, sin, cos, exp, log, ^}`; conservation laws of double-pendulum recovered at 5–9 symbol expressions. No formal claim of minimality.

**Surreal numbers and category-theoretic compression.** Conway's surreals (Conway, *On Numbers and Games*, 1976) construct ℝ, ordinals, infinitesimals, and more from a single recursive construction `{L | R}`. This is *generative* compression: enormous semantic territory, two primitives. Mac Lane's adjoint functors (*Categories for the Working Mathematician*, 1971) similarly compress: "all concepts are Kan extensions" is the slogan-form, and substantial portions of algebra/topology factor through ~10 categorical constructions (limit, colimit, adjoint, monad, Yoneda, etc.). **The pattern across these examples: massive semantic coverage from few primitives is achievable but always pays a steep "cost-of-unfolding" — definitions that are short to state are long to compute with.** This matches the SK→iota lesson directly.

**Cost-of-compression empirically.** No single canonical study quantifies this trade-off across mathematical domains. Closest relevant evidence: (a) In genetic-programming symbolic regression, parsimony pressure is well-known to over-prune useful sub-trees — see Vanneschi & Castelli, "Soft Target and Functional Complexity Reduction" tradition; (b) In automated theorem proving, Wiedijk's De Bruijn factor argues for a *floor* below which compression breaks readability and reuse without reducing actual logical content.

## Substrate-relevance

Three load-bearing connections:

1. **The Sigma kernel's 7 opcodes are control primitives, not data primitives.** They are closer to combinator-calculus's `S`/`K` than to AI Feynman's `+`/`sin`. Combinator-calculus literature shows you *can* compress to 1 primitive (iota), but this destroys ergonomics and inflates terms by orders of magnitude. The substrate-grade property *append-only storage* is an invariant on `PROMOTE`+`ERRATA`, not a primitive that can be deleted; *linear capabilities* live in `GATE`+`PROMOTE`'s capability-consumption logic. **No subset of the 7 obviously collapses without losing one of the listed invariants.** The closest candidate for collapse is `TRACE` (which is purely observational and does not write substrate state), but TRACE backs falsification audits and provenance graphs (`sigma_kernel/demo.py` scenario 6 chains TRACE through ERRATA history); removing it pushes provenance reconstruction out of the kernel and into agent code, weakening the *content-addressed provenance* invariant.

2. **BIND/EVAL is the kernel's iota.** It is the substrate's universal-extension mechanism: any callable can be bound as a substrate symbol, then evaluated under capability discipline (`sigma_kernel/BIND_EVAL_MVP.md`, `bind_eval_v2.py`). Combinatorially this means the kernel's *expressive* basis is effectively infinite — anything Python computes is reachable through BIND/EVAL — while its *control* basis stays at 7. This is exactly the architectural pattern combinatory logic discovered: a small fixed control kernel + an open-ended evaluation surface. Prometheus has the right shape here.

3. **Data-plane compression is a different problem the substrate has not yet committed on.** When Ergon/Charon/Aporia produce a CLAIM, the symbolic content of that claim (a formula, an inequality, a theorem statement) is currently free-form text/JSON. There is no enforced normalization, no Pareto-frontier representation tracking, no minimum-symbol metric. AI Feynman / PySR's lesson — *track the Pareto frontier of (length, fit), don't just minimize* — is directly applicable and is currently absent from the substrate.

## Concrete operational handles

1. **Defend "7 opcodes" with an invariant-mapping table, not just a count.** Add a row in `sigma_kernel/README.md` listing each opcode against the substrate-grade invariant(s) it enforces, and explicitly mark "no smaller subset preserves all invariants" as the minimality claim. This makes the claim falsifiable: any reviewer who proposes collapsing two opcodes must show the lost invariant.

2. **Adopt Pareto-frontier tracking for CLAIM payloads.** Borrow PySR's pattern: every formula-typed CLAIM stores `(symbol_count, accuracy_or_proof_length, complexity_proxy)` so the substrate can rank by elbow, not just by minimum. Implement as caveat-metadata (`sigma_kernel/caveats.py`) initially; promote to first-class field if used.

3. **Pick a single Kolmogorov-proxy compressor and freeze it.** BDM (Soler-Toscano et al.) for short strings, plus a baseline `zlib` for longer ones, gives a reproducible pseudo-K(x). This becomes the substrate's *operational* compression metric. Note loudly that it is compressor-relative — the substrate is not measuring "Kolmogorov complexity," it is measuring "BDM-or-zlib complexity," and any cross-domain comparison must hold the compressor fixed.

4. **Resist iota-style collapse of opcodes.** The combinator literature is explicit that 1-primitive systems are universal but unusable. The current 7-opcode design is closer to SKI (3 primitives, ergonomic) than to iota (1 primitive, intractable). If anyone proposes collapsing GATE into PROMOTE because "GATE is just PROMOTE's precondition," the relevant counter is: separating the falsification verdict from the state-write keeps the three-valued GATE auditable independently of promotion outcomes.

5. **Cost-of-compression should be measured before being assumed.** Run a controlled probe: take a fixed corpus of ~50 substrate-historical CLAIMs (post-hoc from `harmonia/memory/symbols/`), compute their representation length under (a) raw form, (b) primitive-rewritten form using `arsenal_meta` ops only, (c) a maximally compressed form via repeated common-subexpression elimination. Measure: does Charon/Ergon's downstream re-discovery rate change as a function of representation length? Hypothesis (consistent with PySR practice): elbow-of-Pareto wins; both extremes hurt.

## Falsification

The central operational claim — *the Sigma kernel's 7-opcode count is at a defensible local minimum given the listed substrate-grade invariants, and data-plane compression should target the elbow of a Pareto frontier rather than minimum symbol count* — would be refuted by any of the following:

- A demonstrated reduction of the 7 opcodes to ≤5 that preserves append-only storage, linear capabilities, three-valued GATE, falsification-first promotion, and content-addressed provenance, with a working implementation. (Closest theoretical candidate: collapsing GATE into PROMOTE; this study judges this lossy because it conflates verdict and state-write, but a clean construction would refute the judgment.)
- A controlled experiment showing that the *minimum-symbol* representation of substrate CLAIMs improves downstream discovery rate monotonically (no elbow), contradicting the AI-Feynman/PySR observation.
- A documented case where BIND/EVAL semantics genuinely fail to cover an operation that the kernel needed natively — i.e., evidence that the "small kernel + open extension" pattern is breaking down for Prometheus's actual workflows.

## Open questions raised

1. Is there a *substrate-specific* analogue of the De Bruijn factor — i.e., a roughly invariant ratio between informal mathematical statement and substrate-encoded CLAIM? If yes, that ratio could become a calibration metric for whether the substrate is over- or under-encoding.
2. Do any of the deferred opcodes from `sigma_kernel/README.md` (DISTILL, REWRITE, COMPOSE, STABILIZE) correspond to compression operators on the data plane rather than control primitives, and would adding them be a category error?
3. Is BIND/EVAL's expansion behavior tracked? Combinator-calculus warns that universal extension via a single primitive can blow up term length unboundedly; if the substrate ever caches BIND expansions, that cache's growth profile is a quantitative test of whether Prometheus is paying iota-style cost-of-unfolding without realizing it.
4. Are surreal-number-style "few primitives, vast semantics" compressions found anywhere in mathlib4 (via centrality analysis), and could those high-leverage definitions be lifted into Prometheus's symbol vocabulary as load-bearing primitives?
5. AI Feynman's claim that "physics equations cluster at low symbol count" — does this generalize to non-physics mathematics? If not, the compression-as-discovery-prior assumption underlying many symbolic-regression systems may transfer poorly to Prometheus's number-theoretic / topological workloads.

## Citations

- Li, M., Vitányi, P. *An Introduction to Kolmogorov Complexity and Its Applications*, 4th ed. Springer, 2019. (Reference text; no DOI for the chapter cited.)
- Soler-Toscano, F., Zenil, H., Delahaye, J.-P., Gauvrit, N. "Calculating Kolmogorov Complexity from the Output Frequency Distributions of Small Turing Machines." *PLOS ONE* 9(5): e96223, 2014. https://doi.org/10.1371/journal.pone.0096223
- Schönfinkel, M. "Über die Bausteine der mathematischen Logik." *Mathematische Annalen* 92, 1924. (Combinatory logic origin; cited via Curry & Feys, *Combinatory Logic*, 1958.)
- Barker, C. "Iota and Jot: the simplest languages?" 2001. http://semarch.linguistics.fas.nyu.edu/barker/Iota/
- Tromp, J. "Binary Lambda Calculus and Combinatory Logic." (Multiple revisions; canonical link: https://tromp.github.io/cl/cl.html )
- Wiedijk, F. "The De Bruijn factor." http://www.cs.ru.nl/~freek/factor/factor.pdf
- Udrescu, S.-M., Tegmark, M. "AI Feynman: A physics-inspired method for symbolic regression." *Sci. Adv.* 6(16):eaay2631, 2020. arXiv:1905.11481.
- Udrescu, S.-M., et al. "AI Feynman 2.0: Pareto-optimal symbolic regression exploiting graph modularity." arXiv:2006.10782, 2020.
- Cranmer, M. "Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl." arXiv:2305.01582, 2023.
- Romera-Paredes, B., et al. "Mathematical discoveries from program search with large language models" (FunSearch). *Nature* 624, 468–475, 2023. https://doi.org/10.1038/s41586-023-06924-6
- Schmidt, M., Lipson, H. "Distilling Free-Form Natural Laws from Experimental Data." *Science* 324(5923), 2009. https://doi.org/10.1126/science.1165893
- Conway, J. H. *On Numbers and Games*. Academic Press, 1976. (Reissued AK Peters 2001.)
- Mac Lane, S. *Categories for the Working Mathematician*, 2nd ed. Springer GTM 5, 1998.
- Internal: `F:/Prometheus/sigma_kernel/README.md`, `F:/Prometheus/sigma_kernel/sigma_kernel.py`, `F:/Prometheus/sigma_kernel/BIND_EVAL_MVP.md`, `F:/Prometheus/sigma_kernel/bind_eval_v2.py`, `F:/Prometheus/sigma_kernel/caveats.py`, `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_01_minimal_generative_bases.md`

*No canonical empirical study quantifying the compression-vs-discovery-rate trade-off across mathematical domains was identified in this scan; the "elbow of Pareto wins" claim is consensus-level practice from the symbolic-regression community (PySR, AI Feynman) and is asserted as a working hypothesis for Prometheus, not a cited theorem. The Schönfinkel reference is via secondary citation (Curry & Feys 1958), not direct.*
