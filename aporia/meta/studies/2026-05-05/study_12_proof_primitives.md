# Study 12: Primitive Operations Underlying Proofs

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** Sigma kernel opcodes vs proof-primitive opcodes; BIND/EVAL extension surface for proof tactics; arsenal_meta augmentation question.

## Problem statement (Prometheus-adapted)

Two superficially similar questions must be kept distinct:

1. **Substrate-control primitives (Sigma kernel, 7 opcodes):** Operations on substrate state — RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE. These touch append-only storage, capability tokens, and provenance graphs. They are *not* proof steps.
2. **Proof-construction primitives (Lean/Coq tactics, sequent rules, natural-deduction inferences):** Operations that *build a derivation*. These rewrite goals, instantiate hypotheses, invoke induction schemata, discharge contradictions. They are object-level constructions inside whatever logic Prometheus consumes (mathlib4 statements, Hecke claims, BSD-style invariants).

The Prometheus-relevant question is whether (2) belongs *inside* the Sigma kernel as new opcodes, or *outside* the kernel as bound callables exposed via BIND/EVAL. The 7-opcode kernel currently treats every CLAIM payload as opaque text/JSON; there is no native notion of "this CLAIM was derived by induction on n" or "this PROMOTE consumed a `rewrite`+`linarith` chain." Augmenting `arsenal_meta` (currently 85 callables in `prometheus_math/arsenal_meta.py`, math-operation-centric) with proof-step primitives would be a category extension, not a category change — provided we know what the proof primitives actually *are* empirically.

That last word matters: Study 01 flagged that **no published top-N centrality ranking of mathlib4 tactics exists** as a peer-reviewed artifact. This study tries to close (or honestly characterize) that gap.

## Literature scan

**Natural deduction vs sequent calculus vs Hilbert systems.** Hilbert systems achieve minimal *axiomatic* footprint (Łukasiewicz's three axioms + modus ponens) at the cost of grotesque proof length; natural deduction (Gentzen 1935) trades axiom count for ~10–14 introduction/elimination rules and is uniformly cheaper to use; sequent calculus (LK/LJ) is the cleanest object for cut-elimination but at similar primitive count. Every modern proof assistant builds on natural-deduction-style elaboration (Coq's CIC, Lean's dependent type theory, Mizar's Jaśkowski variant, Isabelle/Pure). Minimum-primitive: Hilbert. Minimum-friction: natural deduction. Same SKI-vs-iota trade-off Study 05 surfaced.

**Empirical mathlib tactic distribution.** This is the most important and most under-cited part of the literature.

- **mathlib4-all-tactics** (Enomoto, https://github.com/haruhisa-enomoto/mathlib4-all-tactics): catalogues all tactics defined or used in mathlib4 — several hundred entries — but is a registry, not a frequency study.
- **LeanDojo** (Yang et al., NeurIPS 2023, arXiv:2306.15626): extracts ~98,000 theorems and ~130,000 tactic invocations from mathlib4. Largest publicly available substrate for tactic-frequency analysis. The paper's headline focus is retrieval-augmented proof generation; tactic frequency is a dataset side-product, not the stated contribution. Informal re-analyses (Lean Zulip, gists) show Pareto-style distribution: `simp`, `rw`, `exact`, `apply`, `intro`, `refine`, `cases`, `induction`, `ring`/`linarith`, `omega` dominate. **No peer-reviewed paper whose stated contribution is "empirical Pareto distribution of mathlib4 tactic usage" identified.** Data exists; canonical citation does not.
- **CoqGym** (Yang & Deng, ICML 2019, arXiv:1905.09381): ~71,000 Coq proofs, ~123 tactic types. Dominant tactics: `apply`, `rewrite`, `intro`, `auto`, `simpl`, `destruct`, `induction`, `exact`, `unfold`, `assumption` — ~10 tactics dominate.
- **ML4PG** (Komendantskaya et al., arXiv:1212.3618, 2012): ~10 dominant tactics out of ~100 in Coq; SSReflect <10. Cited in Study 01.
- **Tactician** (Blaauwbroek et al., arXiv:2008.00120, ITP 2020); **HOList / HolStep** (Bansal et al., arXiv:1904.03241; Kaliszyk et al., arXiv:1703.00426): same heavy-tail pattern in Coq and HOL Light.

**Cross-system convergence on the dominant kernel.** Aggregating across the above sources, the empirically-observed top tactics across Lean 4 mathlib, Coq, HOL Light, and Mizar substantially overlap in *function* even when they differ in name:

| Function | Lean 4 mathlib | Coq | HOL Light | Mizar |
|---|---|---|---|---|
| Goal substitution | `rw`, `simp` | `rewrite`, `simpl` | `REWRITE_TAC`, `SIMP_TAC` | by *Th* |
| Hypothesis introduction | `intro` | `intro`, `intros` | `GEN_TAC`, `DISCH_TAC` | `let`, `assume` |
| Hypothesis use | `exact`, `apply`, `refine` | `exact`, `apply` | `MATCH_MP_TAC` | `by` |
| Case-split | `cases`, `rcases` | `destruct`, `case` | `DISJ_CASES_TAC` | `per cases` |
| Induction | `induction` | `induction` | `INDUCT_TAC` | scheme `Ind_Step` |
| Decide closed-form | `decide`, `omega`, `linarith`, `nlinarith` | `lia`, `lra`, `nia` | `ARITH_TAC` | `requires` |
| Equational closure | `ring`, `field_simp` | `ring`, `field` | `REAL_ARITH` | (limited) |
| Extensionality | `ext`, `funext` | `extensionality` | `ABS_TAC`, `MK_COMB_TAC` | (limited) |
| Contradiction | `contradiction`, `exfalso` | `contradiction`, `exfalso` | `CONTR_TAC` | `thus contradiction` |

Roughly **8–10 functional categories** cover the dominant usage across systems. This *functional* alignment is the closest thing the literature has to an "empirical instruction set for proof," and it is consistent across decades and across very different logical foundations (CIC vs HOL vs first-order set theory).

**Theoretical-minimum proof primitive sets.** First-order logic with equality: Hilbert systems with modus ponens + 3–5 axiom schemata (Łukasiewicz, Frege) suffice; natural deduction needs ~14 intro/elim rules; sequent calculus needs structural rules + identity + per-connective left/right rules. All three are minimal in their styles, and all share the SKI-vs-iota trade-off: shorter primitive lists, combinatorially longer proofs.

**Proof compression / minimal-tactic literature.** Proof terms underlying tactic scripts are typically 5–50× the byte size of the script (Coq's `Show Proof`); tactics are a compression layer over proof terms — matches Study 05's De Bruijn factor. HoTT/UF (HoTT book 2013) compresses algebraic-topological proofs by 2–10× on specific theorems via path induction + univalence. Tactic minimizers (Lean `polyrith`, Coq `Tactician`, Isabelle `sledgehammer`+`try0`) reduce script length but rarely below the readability floor.

**Has anyone built an empirical "instruction set for proof"?** Closest artifacts: LeanDojo's dataset (instruction set implicit, not enumerated); TacticToe (Gauthier et al., arXiv:1804.00596, 2018) for HOL4 ranks tactics by *search utility*, not raw frequency; Tactician corpus statistics buried in Blaauwbroek et al.'s appendix. No paper of the form "Top-50 mathlib4 tactics by call frequency with Pareto-fit α and 95% CIs" identified. **Same gap Study 01 named for definition centrality, restated for tactics.** Closeable in ~1 day on the LeanDojo dump.

## Substrate-relevance

Three load-bearing connections to current Prometheus architecture:

1. **The Sigma kernel's 7 opcodes are *substrate-control* operations, not proof-construction operations.** They are about *who is allowed to write what to substrate state, with what provenance, under what falsification regime*. They are orthogonal to proof construction in the same way that a database's transaction primitives (BEGIN, COMMIT, ROLLBACK, GRANT) are orthogonal to SQL's query operations. Conflating them would be a category error: PROMOTE is not "QED," and GATE is not "decide". The 7 opcodes' minimality argument (Study 05) is independent of whatever proof-primitive vocabulary CLAIM payloads happen to use.

2. **Proof primitives belong on the BIND/EVAL extension surface, not as new kernel opcodes.** This is the cleanest architectural fit: bind a Lean-style tactic (`rewrite`, `induction`, `cases`) as a substrate symbol, EVAL it under capability discipline, let the resulting term become the data side of a CLAIM. This mirrors what `bind_eval_v2.py` already does for arithmetic callables and matches the small-kernel-plus-open-extension pattern the substrate has already committed to. **No kernel opcode change is required to enable proof-primitive workflows.**

3. **`arsenal_meta` (85 callables in `prometheus_math/arsenal_meta.py`) is currently object-construction-centric, not proof-step-centric.** Its categories (AI, CAS, COMB, DB, NT, NUM, OPT, SAT, TOP per `ARSENAL.md`) are mathematical-operation domains, not deductive moves. There is currently no `arsenal_meta` callable named `induct_on`, `case_split`, `extensionality`, `contradiction`, `well_founded_recursion`, or `congruence`. This is fine if Prometheus's intended workflow is *evidence-collection then claim-emission* (which is what Charon, Ergon, Aporia mostly do today); it is a real gap if the workflow shifts toward *proof-construction with substrate-grade audit*.

## Concrete operational handles

1. **Run the missing empirical analysis.** Pull LeanDojo (arXiv:2306.15626; HuggingFace `kaiyuy/leandojo-lean4-benchmark` or `leandojo-lean4-mathlib4`) and produce a 1-page artifact: top-100 mathlib4 tactics by raw call-frequency, with category aggregation matching the 8-row functional table above. This closes the gap Study 01 named for tactics. Time cost: ~1 day. Output: a citable internal artifact (`aporia/meta/studies/2026-05-05/derived/mathlib4_tactic_frequencies.json`) that downstream studies and Aporia challenges can reference instead of "no canonical source identified."

2. **Do not add proof-primitive opcodes to the Sigma kernel.** The 7 opcodes are control-plane; proof primitives are data-plane derivation moves. Augment the kernel only if a substrate-grade *invariant* (append-only, linear cap, three-valued GATE, falsification-first, content-addressed provenance) requires native support — which proof primitives do not.

3. **Augment `arsenal_meta` with a proof-primitive sub-namespace** *if and only if* downstream agents start producing CLAIMs whose payloads are proof terms rather than computational results. Suggested initial set, derived from the cross-system functional table above and bounded to ~10 entries to match the empirical Pareto: `rewrite`, `simp_normalize`, `intro`, `apply`, `case_split`, `induct_on`, `decide_arith` (linarith/omega-style), `ring_normalize`, `extensionality`, `contradiction`. Implement as bound callables (BIND/EVAL), not as new kernel opcodes.

4. **Add a CLAIM-payload typing field for proof-derived claims.** When a CLAIM carries a proof term (vs a computational fact), tag it with `derivation_kind: {computational, tactic_chain, formal_proof}` and record the tactic sequence. This enables downstream analysis of which proof primitives Prometheus actually exercises — feeding back into the empirical-Pareto loop and preventing the "85 callables but we don't know which fire" issue Study 01 named.

5. **Track the De Bruijn factor on substrate CLAIMs.** Wiedijk's empirical ~4× ratio between informal and formal-text length is one of the most robust cross-system invariants in the literature (Study 05). If Prometheus's CLAIM payloads diverge sharply from this — too compressed or too verbose — that is a calibration signal that the substrate's encoding is mis-tuned.

## Falsification

The central operational claim — *Sigma kernel opcodes (control-plane) are orthogonal to proof primitives (data-plane); proof primitives belong on BIND/EVAL and as an `arsenal_meta` sub-namespace; no peer-reviewed top-N empirical Pareto for mathlib4 tactics currently exists* — would be refuted by:

- A demonstration that some substrate-grade invariant cannot be enforced over proof-term CLAIMs without a native proof-primitive opcode. Plausible candidate: cut-elimination as a substrate-level ERRATA operation, if proof-term ERRATA needs to preserve cut-elimination natively.
- A peer-reviewed post-2024 publication reporting the mathlib4 tactic-frequency Pareto with counts and CIs.
- Evidence from `arsenal_meta` augmentation that the proposed factorization is wrong — e.g., `simp_normalize` and `ring_normalize` collapse, or `case_split` consistently decomposes into `intro`+`apply`.

## Open questions raised

1. Does the LeanDojo dataset contain enough metadata to compute *conditional* tactic frequencies — e.g., "given that the goal is an arithmetic equality, P(simp) vs P(ring) vs P(linarith)" — and if so, does the distribution become flatter or sharper than the unconditional Pareto?
2. What fraction of mathlib4 proofs are dominated (≥90% of tactic invocations) by the same top-10 tactics observed in CoqGym / ML4PG? If the fraction is >80%, the cross-system "10 dominant primitives" generalization is empirically locked. If it is <50%, there is mathlib-specific structure (e.g., `simp` lemma-base dominance, type-class elaboration) that breaks the cross-system pattern.
3. Are there proof-primitive operations that are *frequent in informal mathematics but rare in formal proof assistants*? Candidates: "without loss of generality," "by symmetry," "by induction on the complexity of the formula," "diagram chase." If yes, these are the missing primitives whose absence accounts for part of the De Bruijn factor — and they are the most Prometheus-relevant ones, since Prometheus mostly produces informal-style CLAIMs today.
4. Does the BIND/EVAL surface's expansion behavior (Study 05's open question 3) compose with proof-tactic binding in a way that preserves auditability? Specifically: if `induct_on` is bound as a callable that internally invokes `rewrite` + `case_split`, can TRACE recover the inner tactic chain, or does it see only the outer call? If only the outer call, proof-primitive binding silently degrades content-addressed provenance.
5. Should `FALSIFY` opcodes be allowed to consume proof primitives (e.g., FALSIFY by exhibiting a counterexample-construction tactic chain)? Currently FALSIFY is treated as a verdict event, not a derivation. Coupling it to proof-primitive provenance would make falsification audits structurally symmetric with promotion audits.

## Citations

- Gentzen, G. "Untersuchungen über das logische Schließen." *Mathematische Zeitschrift* 39, 1935. (Natural deduction / sequent calculus origin; cited via Szabo's translation, *The Collected Papers of Gerhard Gentzen*, North-Holland, 1969.)
- Łukasiewicz, J. "Elementy logiki matematycznej." Warsaw, 1929. (Three-axiom Hilbert system; cited via Borkowski's English edition, *Selected Works*, 1970.)
- Yang, K., Swope, A., Gu, A., Chalamala, R., Song, P., Zhang, S., Prenger, R., Anandkumar, A. "LeanDojo: Theorem Proving with Retrieval-Augmented Language Models." *NeurIPS* 2023. arXiv:2306.15626.
- Yang, K., Deng, J. "Learning to Prove Theorems via Interacting with Proof Assistants." *ICML* 2019. arXiv:1905.09381. (CoqGym.)
- Komendantskaya, E., Heras, J., Grov, G. "Machine Learning in Proof General: Interfacing Interfaces." arXiv:1212.3618, 2012. (ML4PG.)
- Blaauwbroek, L., Urban, J., Geuvers, H. "The Tactician: A Seamless, Interactive Tactic Learner and Prover for Coq." arXiv:2008.00120; ITP 2020.
- Bansal, K., Loos, S., Rabe, M., Szegedy, C., Wilcox, S. "HOList: An Environment for Machine Learning of Higher Order Logic Theorem Proving." arXiv:1904.03241, 2019.
- Kaliszyk, C., Chollet, F., Szegedy, C. "HolStep: A Machine Learning Dataset for Higher-Order Logic Theorem Proving." arXiv:1703.00426, 2017.
- Gauthier, T., Kaliszyk, C., Urban, J., Kumar, R., Norrish, M. "TacticToe: Learning to Reason with HOL4 Tactics." arXiv:1804.00596, 2018; LPAR 2017.
- Wiedijk, F. "The De Bruijn factor." http://www.cs.ru.nl/~freek/factor/factor.pdf
- Wiedijk, F. (ed.) *The Seventeen Provers of the World*. Springer LNAI 3600, 2006.
- Univalent Foundations Program. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, 2013. https://homotopytypetheory.org/book/
- Enomoto, H. mathlib4-all-tactics. https://github.com/haruhisa-enomoto/mathlib4-all-tactics
- Internal: `F:/Prometheus/sigma_kernel/README.md`, `F:/Prometheus/sigma_kernel/sigma_kernel.py`, `F:/Prometheus/sigma_kernel/BIND_EVAL_MVP.md`, `F:/Prometheus/sigma_kernel/bind_eval_v2.py`, `F:/Prometheus/prometheus_math/arsenal_meta.py`, `F:/Prometheus/prometheus_math/ARSENAL.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_01_minimal_generative_bases.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/study_05_compression_limits.md`, `F:/Prometheus/aporia/meta/studies/2026-05-05/BATCH_PLAN.md`

*Calibrated negative finding: as of this scan, no peer-reviewed paper reports the empirical Pareto distribution of mathlib4 tactic usage with frequency counts and confidence intervals — the same gap Study 01 named for definition centrality, restated here for tactics. The LeanDojo dataset (arXiv:2306.15626) contains the underlying invocation traces; computing the distribution is a ~1-day analysis but the canonical citation does not yet exist. The cross-system "8–10 dominant tactic categories" pattern is consensus-level community knowledge supported by ML4PG, CoqGym, TacticToe, and HOList, asserted as a working hypothesis for Prometheus rather than a single citable theorem. The Schönfinkel-Bernays "single combinator" claim for first-order logic is referenced via standard combinatory-logic textbook tradition rather than a directly-cited primary source in this scan.*
