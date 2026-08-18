# Report 15 — Verifier-Rich Math Domains Catalog

**Topic:** Where RL-substrate-eligible structure already exists in mathematics
**Date:** 2026-05-02

## 1. Situation

David Silver's "Era of Experience" thesis frames RL self-play as the dominant paradigm for superhuman capability — but only in domains that supply *cheap, decisive verification*. Go has a rule-checker and a terminal win/loss signal; protein folding has structural energy; code has unit tests. Mathematics is, in principle, the canonical verifier-rich domain (proofs are mechanically checkable). In practice, only narrow subdomains today expose verifiers at the throughput, precision, and coverage required to drive an RL loop. Prometheus's substrate-as-environment thesis therefore demands a hard inventory: which mathematical territories already have machine-grade verifiers, what those verifiers verify, and where the substrate must rely on weaker partial verifiers (calibration anchors, replication tests, falsification batteries) until stronger ones materialize. This report catalogs the landscape so substrate ingestion can be sequenced by verifier-density, not by topical interest.

## 2. Catalog of verifier-rich subdomains

### 2.1 Lean / Mathlib (kernel-checked formal proofs)
**Verifier:** the Lean 4 kernel — a small, trusted type-checker that reduces every proof to dependent-type-theory primitives.
**Scale:** Mathlib4 contains ~1.7M lines, ~200K theorems, ~100K definitions (early 2026), spanning undergraduate analysis through algebraic geometry (perfectoid spaces, condensed mathematics).
**Accessibility:** open-source, scripted via `lake`, machine-readable proof terms, well-supported tactic framework (`aesop`, `polyrith`, `nlinarith`). Premise-selection corpora (LeanDojo, ntp-toolkit) expose state/action interfaces directly.
**Calibration potential:** *gold-standard*. Reward = `proof_compiles ∈ {0,1}`. AlphaProof-style RL has demonstrated tractability.

### 2.2 Coq / Isabelle/HOL
**Verifier:** Coq's CIC kernel; Isabelle's Pure logic with HOL extension.
**Scale:** Coq's `coq-community` + `mathcomp` covers ~80K theorems including Feit–Thompson and 4-color theorem; Isabelle's AFP holds ~750 entries, ~250K lemmas, including Gödel's theorems and the CAP theorem.
**Accessibility:** mature; SerAPI / `pycoq` and `Isabelle/PIDE` provide programmatic access.
**Calibration:** comparable to Lean but smaller research-frontier tail; useful as *cross-prover replication* (a lemma proved in two kernels is much stronger than one).

### 2.3 Symbolic computation systems (SymPy / SageMath / PARI-GP / Mathematica)
**Verifier:** algebraic decision procedures (Gröbner bases, cylindrical algebraic decomposition, `is_zero` for polynomial identities, `is_prime` deterministic for sub-2^64).
**Scale:** unbounded — verifies on demand. PARI ships ~1800 number-theoretic routines; Sage glues ~100 backends.
**Accessibility:** Python-native (SymPy), Sage CLI, gp shell. Cheap CPU, no GPU required.
**Calibration:** *high but bounded* — only for decidable fragments (polynomial identities, finite-field arithmetic, exact linear algebra). Floating-point sympy results need precision tracking.

### 2.4 Numerical conjecture verification (LMFDB / Magma / PARI)
**Verifier:** numerical certificates — BSD rank checks via 2-descent, Sato–Tate moments, modular-form coefficient computation, Heegner-point heights.
**Scale:** LMFDB carries ~1.7B objects (elliptic curves to conductor 500K, modular forms to weight 200, number fields to degree 47, L-functions, genus-2 curves). Charon already ingests this.
**Accessibility:** Postgres mirror (devmirror.lmfdb.xyz), REST API, downloadable dumps.
**Calibration:** *partial verifier* — numerical agreement to N digits is strong evidence, not proof. Ideal as RL reward shaping under explicit precision contract.

### 2.5 Constraint solvers (SAT / SMT / MIP)
**Verifier:** Z3, CVC5, MiniSat, Gurobi — produce UNSAT certificates (DRAT proofs) or models.
**Scale:** SAT instances at 10^7+ variables solved daily; the Pythagorean Triples theorem produced a 200 TB proof. SMT-LIB has ~300K instances.
**Accessibility:** standard formats (DIMACS, SMT-LIB), Python bindings (z3-solver, pysat).
**Calibration:** *gold for decidable theories* (QF_LIA, QF_BV, EUF). Higher-order or quantified theories degrade to heuristic.

### 2.6 Combinatorial enumeration (OEIS, KnotInfo, GAP small-groups)
**Verifier:** exact integer matching against canonical databases. OEIS A-numbers; KnotInfo's Khovanov / HOMFLY / signature tables; GAP SmallGroups library covers all groups of order ≤2000 (except 1024).
**Scale:** OEIS ~370K sequences; KnotInfo ~3M knots through 19 crossings (Burton enumeration); GAP ~423M groups of order ≤2000.
**Accessibility:** flat-file + REST + Sage interface.
**Calibration:** *exact-match verifier* — sequence-prefix lookup is fast, decisive, and falsification-rich.

### 2.7 Proof-assistant-adjacent (HOL Light, Mizar, Metamath)
**Verifier:** HOL Light's tiny LCF kernel (~400 lines OCaml); Metamath's set.mm, an axiom-by-axiom textual proof checker; Mizar's MML.
**Scale:** Metamath set.mm ~42K theorems; Mizar MML ~75K; HOL Light covered Flyspeck (Kepler conjecture).
**Accessibility:** all open; Metamath is a single-binary verifier — the cheapest substrate to validate against.
**Calibration:** Metamath's *minimality* makes it the ideal independent referee for cross-prover claims.

## 3. Verifier-poor subdomains (where RL self-play breaks down)

Several mathematical territories actively resist substrate-grade verification today:

- **Research-frontier algebraic geometry / arithmetic geometry.** Perfectoid spaces, condensed mathematics, derived categories — proofs are essay-length, rely on shared intuition about commuting diagrams, and Lean formalization lags by years. Scholze's *Liquid Tensor Experiment* showed it's possible but heroic.
- **Open conjectures with no decidable approximation.** Riemann hypothesis, P vs NP, abc conjecture (the Mochizuki dispute illustrates the pathology). No partial verifier short of the full proof.
- **Mathematical physics with measurement-collapse interpretation.** Path integrals, renormalization, AdS/CFT — symbolic results often depend on physicist conventions (regularization choice, normalization) that are not theorems but modeling decisions. The *math* is extractable; the *physics interpretation* is not RL-verifiable.
- **Foundations / philosophy of math.** Choice-of-axiom debates (large cardinals, univalence, predicativity) have no verifier — they are meta-theoretic preferences.
- **Pedagogical and historical exposition.** Textbook proofs, naming conventions, attribution — not verifiable, only conventional.
- **Conjectural patterns from numerical data without theoretical backing.** OEIS-style "this looks like that" without a proof sketch — partially verifiable via extended computation, but exposed to false-discovery.

In these zones, RL self-play silently rewards plausibility-modeling rather than truth-modeling — the well-documented hallucination failure mode.

## 4. Implications for Prometheus's substrate scope

The substrate should be populated in *verifier-density order*, not *topic-popularity order*. Concretely:

1. **Tier-1 (gold verifier, ingest first):** Lean/Mathlib, Metamath set.mm, OEIS, GAP small-groups, KnotInfo, SAT/SMT instance libraries, LMFDB exact-arithmetic columns. Every node carries a `verifier_id` and a re-check cost.
2. **Tier-2 (partial verifier, ingest with calibration anchor):** LMFDB numerical conjecture checks, Sato–Tate moments, BSD ranks, modular-form q-expansions to N coefficients. These attach a *precision contract* — the substrate stores the agreement digits and the assumed-but-unproved hypotheses (GRH, BSD).
3. **Tier-3 (verifier-adjacent, exploration only, firewalled from training corpus):** essay-style proofs, physics-derived conjectures, philosophical commitments. Exposed to MAP-Elites exploration but blocked from RL reward signal — consistent with the two-track-epistemics rule (`feedback_weak_signals_are_threads.md`).

This sequencing means the substrate compounds *verifier coverage* before it compounds *topic coverage*. The Tensor's signature-keyed index should expose `verifier_density` as a first-class field so Apollo/Rhea routing prefers verifier-rich neighborhoods for any RL update, while Aporia and Charon retain access to verifier-poor exploration zones.

## 5. Concrete next steps

1. **Mathlib4 ingestion at theorem-statement granularity** — extends Lean kernel into substrate as Tier-1 verifier.
2. **Metamath set.mm ingestion** — small, decisive, cross-prover replicator.
3. **LMFDB numerical-evidence columns tagged with precision contract** — Charon already touches this; formalize the contract.
4. **OEIS exact-prefix verifier wrapper** — partially in Aporia stack; expose as substrate primitive.
5. **SAT/SMT instance corpus from SAT competition + SMT-LIB** — closest analog to Go-grade verifier-richness.
6. **Defer:** condensed-math, AdS/CFT, foundations debates — keep in Aporia exploration tier only.

## 6. References

1. Silver, D. & Sutton, R. (2025). *Welcome to the Era of Experience.* DeepMind position paper.
2. Mathlib Community. (2020/ongoing). *The Lean Mathematical Library.* CPP'20; mathlib4 repo.
3. Yang, K. et al. (2023). *LeanDojo: Theorem Proving with Retrieval-Augmented LLMs.* NeurIPS.
4. AlphaProof team, DeepMind. (2024). *AI Achieves Silver-Medal Standard at IMO.* Blog + technical note.
5. Gonthier, G. et al. (2013). *A Machine-Checked Proof of the Odd Order Theorem.* ITP.
6. Wenzel, M. (2018). *Isabelle/Isar — A Generic Framework for Human-Readable Proof Documents.* From Insight to Proof.
7. The Sage Developers. (2026). *SageMath, the Sage Mathematics Software System (Version 10.x).*
8. PARI Group. (2026). *PARI/GP, Version 2.17.* Université de Bordeaux.
9. The LMFDB Collaboration. (2026). *The L-functions and Modular Forms Database.* lmfdb.org.
10. de Moura, L. & Bjørner, N. (2008). *Z3: An Efficient SMT Solver.* TACAS.
11. Heule, M. et al. (2016). *Solving and Verifying the Boolean Pythagorean Triples Problem via Cube-and-Conquer.* SAT.
12. OEIS Foundation. (2026). *The On-Line Encyclopedia of Integer Sequences.* oeis.org.
13. Livingston, C. & Moore, A. (2026). *KnotInfo: Table of Knot Invariants.* knotinfo.math.indiana.edu.
14. The GAP Group. (2024). *GAP — Groups, Algorithms, and Programming, Version 4.13.*
15. Megill, N. & Wheeler, D. (2019). *Metamath: A Computer Language for Mathematical Proofs.*
16. Hales, T. et al. (2017). *A Formal Proof of the Kepler Conjecture.* Forum of Mathematics, Pi.
17. Castelvecchi, D. (2021). *Mathematicians welcome computer-assisted proof in 'grand unification' theory.* Nature (Liquid Tensor Experiment coverage).
18. Buzzard, K. (2022). *What is the point of computers? A question for pure mathematicians.* ICM proceedings.

Word count ~1150
