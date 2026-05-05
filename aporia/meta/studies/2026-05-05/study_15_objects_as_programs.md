# Study 15: Mathematical Objects as Programs

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** BIND/EVAL semantics; CLAIM payload computational requirements; hash-drift detection vs observational equivalence.

## Problem statement (Prometheus-adapted)

Prometheus's BIND/EVAL extension to the Sigma kernel commits, in code, to a specific stance: a `binding` symbol's `def_blob` carries a Python callable's content-hash plus cost model, postconditions, and authority refs; EVAL re-hashes source and refuses to run if the hash drifted (`sigma_kernel/bind_eval.py:622`). In prose this is "math objects as bound callables." The question is whether this stance is supported by the PL-theory and proof-theory literature on *math-as-programs*, or is a Prometheus-local convenience.

Four sub-questions, each tied to one operational handle:

1. Is "math objects as executable bound callables" mainstream, minority, or Prometheus-specific?
2. Which PL properties (termination, totality, type safety, side-effect freedom) become first-class when math objects are EVAL'd?
3. Should CLAIM payloads be required to carry computational content?
4. Does hash-drift detection correspond to a known computational-semantics concept?

Headline: (a) proofs-as-programs is load-bearing in Coq/Lean/Agda/HoTT but lives at *proof* level, not *object* level; (b) the object-level reading exists (computable analysis, synthetic topology, Edalat domain theory, Type Two effectivity) but in narrow communities; (c) BIND/EVAL is closest in spirit to *realizability* and *Type Two Effectivity*, not Curry-Howard at proof level; (d) hash-drift is *intensional*, not what observational equivalence means — the analog is *content-addressed term identity* (Unison, Nix), not denotational semantics.

## Literature scan

**Curry-Howard correspondence (proofs as programs).** Textbook: Sørensen and Urzyczyn, *Lectures on the Curry-Howard Isomorphism* (Elsevier 2006). The triple — Curry, Howard 1969/1980, de Bruijn's Automath — fixes the correspondence: intuitionistic proofs of `A` are closed terms of type `A`; cut-elimination is beta reduction. This is the canonical *proof-level* reading. CIC (Coquand & Huet 1988; Coquand & Paulin-Mohring 1990) extends to dependent types (Coq); Lean 4 uses a related dependent type theory; Agda uses Martin-Löf type theory. In all of these, a *proof* is literally a program and the type-checker is the proof-checker.

**Object-level computational interpretations.** Less mainstream but real:
- *Computable analysis* (Weihrauch, Springer 2000): real numbers, continuous functions, and operators as programs over Type Two functionals. Mathematical objects are identified with their realizers. Closest published analog to Prometheus's "math object as callable" stance.
- *Synthetic topology / synthetic computability* (Escardó ENTCS 2004; Bauer 2006): an "open set" *is* a semi-decidable predicate — a program of type `X -> Sigma`. Topology becomes a function space.
- *Domain theory and effective topology* (Edalat, BSL 1997; Plotkin's LCF). Mathematical objects sit in a Scott-continuous domain; "hash drift on the source" comes closest here to a real semantic meaning, namely change of effective representation of the same entity.
- *Realizability* (Hyland's effective topos 1982; van Oosten 2008): every proposition is interpreted by the set of programs that realize it. The closest theoretical underpinning for BIND/EVAL at scale.
- *Cubical type theory* (Cohen, Coquand, Huber, Mörtberg 2018) and HoTT (UF 2013): give equality itself computational content via path induction. Univalence makes "equivalent structures are equal" executable. Directly relevant to sub-question 4.
- *Joyal's arithmetic universes* (ca. 1973; reconstructed in Maietti, TAC 2010): a categorical vantage on arithmetic objects; link to substrate work is loose.

**On Bell.** John L. Bell's smooth infinitesimal analysis (*A Primer of Infinitesimal Analysis*, CUP 2008) is more accurately a *non-classical-logic* interpretation than a PL-theoretic one. Listed for honesty.

**PL properties relevant to math.** Pierce, *Types and Programming Languages* (MIT 2002): termination, type safety (progress + preservation), strong normalisation, confluence, referential transparency, side-effect freedom, totality. The load-bearing axis for math is *totality*: Coq and Agda enforce strong normalisation; Lean 4 admits partial functions but stratifies them; Idris distinguishes total from partial at type level. *If a mathematical object is a program, the program had better halt*; otherwise its claims carry a totality side-condition.

**Content-addressed code as a programming model.** Unison (Chiusano & Bjarnason, https://www.unison-lang.org/) addresses functions by content hash, with the motivation that "renaming a function should not break callers; changing its source should." Nix derivations (Dolstra 2006) content-address build artifacts; IPFS/Merkle-DAG generalise. **Prometheus's hash-drift detection is structurally identical to Unison's stale-binding semantics — not to a denotational-semantics concept.**

**Observational equivalence (contextual equivalence).** Morris 1968; Plotkin 1977 for PCF; Pitts 2002. Two programs are observationally equivalent iff no context distinguishes them by observable behaviour. This is *extensional* — opposite of hash-drift, which is *intensional* and fires precisely when implementation changes even if behaviour is preserved. Conflating them is a category error.

## Substrate-relevance

Three load-bearing connections:

1. **BIND/EVAL is realizability-flavoured, not Curry-Howard.** What `def_blob` stores is a *realizer* (a Python callable computing the object) plus content hash plus cost model. The mathematical object is identified with this realizer up to source-text equality. This matches the realizability tradition (van Oosten 2008): an object is what its realizers do. It does *not* match Curry-Howard at proof level, because no CLAIM today is a typed proof term. The framing is *literature-supported but minority*: the PL-theory-applied-to-math mainstream runs through Coq/Lean/Agda at proof level; the substrate has taken the parallel object-level track.

2. **Hash-drift is content-addressed-code semantics, not observational equivalence.** The Unison/Nix analogy is exact: the binding is stale iff source changed, regardless of whether the new source computes the same function. Right behaviour for a *provenance* and *audit* system; *not* what "observational equivalence" denotes. A coherent extension: add a *separate*, *coarser* equivalence channel ("does the new callable extensionally match the old on a battery of probe inputs?") that flags hash-drifts as *intensional-only* vs *behaviour-changing*. Cheap; would let the substrate distinguish "renamed a variable" from "changed the algorithm."

3. **Termination/totality is operational (budget), not static (types).** EVAL enforces `max_seconds`, `max_memory_mb`, `max_oracle_calls`, raising `BudgetExceeded` on overshoot. This is *operational* totality: EVAL terminates in bounded time, but the substrate does not check that the underlying math operation is total over its declared input type. For PROMOTE-on-computed-witnesses, the gap matters — a partial function that happened not to diverge in-budget is still partial, and its postconditions are conditional on inputs lying in its domain.

## Concrete operational handles

1. **Add an `extensional_equivalence_probe` on hash drift.** When EVAL detects `live_hash != stored_callable_hash`, do not immediately raise; first run the new callable on a small battery of cached `(args, output)` records from prior evaluations of the old callable, and report `intensional_drift` (hash differs, behaviour matches on probes) vs `behavioural_drift` (both differ). Current binary kill is correct default but coarse; refined report lets Aporia/Charon treat cosmetic refactors differently from algorithmic changes. Cost: one dataclass field, one EVAL extension, ~50 LOC.

2. **Add a CLAIM-payload typing field `derivation_kind: {assertion, computational_witness, refuted, deferred}`.** Mirrors Study 12 and answers sub-question 3: do *not* require every CLAIM to carry computational content (most Charon/Ergon CLAIMs are statistical observations with no natural program form); tag those that *do* carry a witnessing computation, and route them through BIND/EVAL re-execution audits. Substrate becomes hybrid: propositional where appropriate, computational where the math admits it.

3. **Add a `totality_status` field to `arsenal_meta` callables.** Three values: `total_on_declared_input_type`, `partial_with_known_domain`, `partial_with_unknown_domain`. Default pessimistic; let registrants narrow. Without it, every postcondition silently inherits the partial-function ambiguity.

4. **Do not adopt Curry-Howard at the kernel level.** Declaring CLAIMs to be typed terms in some dependent type theory would force commitment to a specific foundation. Honest alternative: leave the kernel logic-agnostic; let bound callables optionally invoke external provers (Lean/Coq) and store proof terms as opaque CLAIM payloads tagged `derivation_kind=computational_witness` with `prover=lean4`. Matches Study 12's "proof primitives on BIND/EVAL, not in the kernel."

5. **Document BIND/EVAL as a realizability stance.** The architectural choice is defensible (realizability is a respectable interpretation tradition) and should be named; calling it "math objects as programs" without that grounding invites overclaim. One paragraph in `BIND_EVAL_MVP.md` saying "this is realizability-flavoured, not Curry-Howard-flavoured" prevents downstream agents from importing wrong intuitions.

## Falsification

The central claim — *BIND/EVAL is realizability-flavoured rather than Curry-Howard-flavoured; hash-drift is content-addressed-code semantics, not observational equivalence; termination is operational (budget), not logical (totality typing); CLAIM payloads should not be required to be programs* — would be refuted by:

- A published PL/type-theory framework in which "binding-symbol whose def_blob holds a callable's content hash plus a cost model" is identified with a denotational-semantics notion of object equality. None found in this scan.
- A demonstration that the Unison content-addressing analogy fails because Prometheus's `def_blob` extras (cost model, postconditions, authority refs) change semantics rather than just metadata. Extras are metadata; analogy survives.
- Empirical evidence that requiring CLAIMs to carry computational content materially improves PROMOTE/FALSIFY rates over opaque propositional CLAIMs on Prometheus's actual workload. None observed; most PROMOTEs are statistical, not witness-based.
- A case where a hash-drift kill was correct on a behaviour-changing edit *and* extensional-probe refinement would have been wrong (false safe). Plausible but not seen.

## Open questions raised

1. Does Study 11's open question — does the proof/object distinction collapse for Sigma-kernel programs? — collapse *one-directionally*? Object-level CLAIMs admit a programmatic realizer (BIND/EVAL handles this), but proof-level CLAIMs lack a kernel-level type for "this CLAIM is itself a proof term in system X." Asymmetric closure (add `derivation_kind=formal_proof_term`) is cheaper than full Curry-Howard.
2. Should PROMOTE require *behavioural reproducibility* (same callable, same args, same output across N runs) before firing? Cheap gate. Would catch nondeterministic callables that silently pass today.
3. Is there a productive partial cubical-TT analog — *paths* between bindings rather than binary hash-equal vs hash-drift? A graded channel (intensional / probe-extensional / formally-proved-equivalent) could be its operational shadow without requiring full type theory.
4. For partial functions in `arsenal_meta`, should the postcondition language admit *domain conditions* (`requires x > 0`)? Postconditions are output-side; domain conditions are input-side and complementary. Would let EVAL refuse out-of-domain inputs before oracle cost.
5. Does the cost model commit a category error by mixing *operational* cost (seconds, memory) with *oracle* cost (PARI/SymPy/external calls)? Operational cost is intrinsic to the realizer; oracle cost is a *trust*-boundary cost. May warrant separate axes for RL reward shaping.

## Citations

- Sørensen, M. H., Urzyczyn, P. *Lectures on the Curry-Howard Isomorphism*. Studies in Logic and the Foundations of Mathematics 149, Elsevier, 2006.
- Howard, W. A. "The formulae-as-types notion of construction." In *To H. B. Curry: Essays on Combinatory Logic, Lambda Calculus and Formalism*, Academic Press, 1980 (manuscript circulated 1969).
- de Bruijn, N. G. "AUTOMATH, a language for mathematics." Technological University Eindhoven Report 68-WSK-05, 1968.
- Coquand, T., Huet, G. "The Calculus of Constructions." *Information and Computation* 76, 1988.
- Coquand, T., Paulin-Mohring, C. "Inductively defined types." *COLOG-88*, LNCS 417, 1990.
- Martin-Löf, P. *Intuitionistic Type Theory*. Bibliopolis, 1984.
- Univalent Foundations Program. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, 2013. https://homotopytypetheory.org/book/
- Cohen, C., Coquand, T., Huber, S., Mörtberg, A. "Cubical Type Theory: a constructive interpretation of the univalence axiom." *Journal of Functional Programming* 28, 2018.
- Weihrauch, K. *Computable Analysis: An Introduction*. Texts in Theoretical Computer Science, Springer, 2000.
- Escardó, M. "Synthetic Topology of Data Types and Classical Spaces." *Electronic Notes in Theoretical Computer Science* 87, 2004.
- Bauer, A. "First Steps in Synthetic Computability Theory." *Electronic Notes in Theoretical Computer Science* 155, 2006.
- Edalat, A. "Domains for computation in mathematics, physics and exact real arithmetic." *Bulletin of Symbolic Logic* 3(4), 1997.
- Hyland, J. M. E. "The effective topos." In *The L. E. J. Brouwer Centenary Symposium*, North-Holland, 1982.
- van Oosten, J. *Realizability: An Introduction to its Categorical Side*. Studies in Logic and the Foundations of Mathematics 152, Elsevier, 2008.
- Joyal, A. "Arithmetic universes." Unpublished talk, ca. 1973. Reconstruction: Maietti, M. E. "Joyal's arithmetic universe as list-arithmetic pretopos." *Theory and Applications of Categories* 24, 2010.
- Bell, J. L. *A Primer of Infinitesimal Analysis*, 2nd ed. Cambridge University Press, 2008.
- Pierce, B. C. *Types and Programming Languages*. MIT Press, 2002.
- Pitts, A. M. "Operational Semantics and Program Equivalence." In *Applied Semantics*, LNCS 2395, Springer, 2002.
- Plotkin, G. D. "LCF considered as a programming language." *Theoretical Computer Science* 5(3), 1977.
- Morris, J. H. *Lambda-calculus models of programming languages*. PhD thesis, MIT, 1968.
- Dolstra, E. *The Purely Functional Software Deployment Model*. PhD thesis, Utrecht University, 2006. (Nix derivations.)
- Unison Computing. *Unison: a content-addressed programming language*. https://www.unison-lang.org/
- Lean 4 reference manual. https://lean-lang.org/lean4/doc/
- Internal: `F:/Prometheus/sigma_kernel/bind_eval.py`, `F:/Prometheus/sigma_kernel/BIND_EVAL_MVP.md`, `F:/Prometheus/sigma_kernel/sigma_kernel.py`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_11_search_landscapes.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_12_proof_primitives.md`.

*Calibrated negative finding: the prompt's framing "math objects as programs" is supported by literature, but the support runs through realizability theory, computable analysis, and synthetic topology — not through the Curry-Howard correspondence (which lives at proof level, not object level). The substrate's specific BIND/EVAL implementation is closest in spirit to Unison's content-addressed code model, *not* to observational equivalence. The hash-drift mechanism is an intensional check; observational equivalence is extensional. Calling the two the same would be a category error. Prometheus's stance is defensible as realizability-flavoured object semantics with content-addressed provenance, and that is the framing recommended for any future writeup.*
