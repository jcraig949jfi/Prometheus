# Review of Harmonia E — Complexity / Cross-domain Batch

**Reviewer:** Harmonia B
**Date:** 2026-05-05
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_01_p_vs_np.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_02_p_vs_pspace.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_03_det_vs_perm.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_04_unique_games.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_05_quantum_pcp.md`
- 1 Python script: `attempts/_p3_det_perm_experiment.py` (~160 LOC)
- For perspective: `harmonia_E_review_of_harmonia_D.md` and `harmonia_E_review_of_harmonia_A.md` (E's own cross-reviews)

**Frame:** parallel to my prior reviews of Harmonia D (`harmonia_B_review_of_harmonia_D.md`) and Harmonia A (`harmonia_B_review_of_harmonia_A.md`). Same questions: critique, additional research per problem, round-2 candidates, additional solution angles, datasets/tools to build.

---

## Part 1 — Overall critique

### What Harmonia E did well

1. **The most sophisticated meta-obstruction taxonomy across the four batches I have data for.** E explicitly distinguishes:
   - **Family-killer barriers** (Baker-Gill-Solovay 1975, Razborov-Rudich 1994, Aaronson-Wigderson 2008): rule out entire technique families.
   - **Candidate-killer results** (Bürgisser-Ikenmeyer-Panova 2017): rule out specific witness within active program.
   - **Self-detected overreach**: P-vs-PSPACE Attack 6 caught a plausible-but-empty padding chain mid-attempt.
   - **Stepping-stone-proved-but-target-open**: NLTS for qPCP.
   - **Narrowed-but-still-open**: UGC and qPCP both have substantial weakenings proven (KMS-2018; NLTS-2023).
   - **Non-commutativity-as-quantum-specific obstruction**: qPCP's break of Dinur-style amplification.
   
   This taxonomy is finer-grained than D's "independence-shape" classification and is the most reusable single output across the entire 8-batch experiment.

2. **Self-caught error mid-attempt is exemplary discipline.** P-vs-PSPACE Attack 6 nearly concluded `P=PSPACE → EXPTIME=EXPSPACE → known false → P≠PSPACE`, then E caught that EXPTIME ≠ EXPSPACE is itself open, and documented the *entire chain of attempted reasoning including the error*. This is precisely the substrate-grade trace data the brief asks for. The kill-path classification `SELF_DETECTED_OVERREACH (caught mid-attempt)` is novel terminology I haven't seen in A or D.

3. **Per-attack metadata tables.** Unique to E's batch. Standardized fields per attack including `invented_citation_count: 0`, `confident_citations`, `hazy_citations`, `reward_signal_capture_check`, `pattern_30_relevance`, `code_artifact`. This is the structured-output Aporia would want for automated cross-batch synthesis. Worth promoting as a substrate-wide standard for future attempt files.

4. **Citation discipline is the cleanest of the three batches I've reviewed.** Confident vs hazy distinctions are explicit per citation, with totals per file. Across 5 attempts: 47 confident citations vs 18 hazy. E flagged "I am NOT invoking 2024-2026 results that I cannot confidently recall" in every attempt — exemplary about the knowledge-cutoff boundary.

5. **Cross-batch awareness throughout.** E repeatedly tags observations "for Aporia's cross-batch synthesis" — surfacing how the structural distinctions in this batch could feed pattern-mining across other batches. This is more proactive than A or D.

6. **Refutation-direction attention.** E uniquely identifies "would refute UGC if it works" attacks (constant-degree SoS, sub-exponential algorithms beyond ABS) and "would refute qPCP if it works" attacks (efficient classical witness). Bidirectional thinking — investigating *what would close the conjecture in either direction* — is largely absent from D's batch and partially absent from A's. Substrate-grade.

7. **Frontier-aware and progress-aware.** E correctly identifies which problems have actually moved (KMS-2018 narrowing UGC's frontier; NLTS-2023 closing one qPCP objection) versus which have remained essentially static (P vs NP, P vs PSPACE, Det vs Perm). E names this "narrowed-but-still-open" as a kill-morphology distinct from "frozen-frontier".

8. **Frame-honesty about the meta-attack format.** All 5 attempts open with "the brief explicitly says solving is not the goal. I treat this as a meta-attack." This is the right framing for problems where individual research-grade attacks are out of reach in 3 hours and the substrate value is in the obstruction map.

### What Harmonia E did less well

1. **Time spent is significantly under the 3-hour-per-problem cap.** Self-reported times per problem: ~50 min (P vs NP), ~40 min (P vs PSPACE), ~80 min (Det vs Perm), ~45 min (UGC), ~50 min (qPCP). Total ≈ 4.4 hours against a 15-hour budget. E says "within 3 hr cap" but used ~30% of it. Honest disclosure but the brief's "surface area over depth" rule was applied to the *batch* rather than to the individual problems — each individual problem could have had more depth in the same total budget. (Compare: A averaged ~2.5h/problem; D averaged ~3h/problem; my own dynamics batch averaged ~1.5h compressed but produced denser numerics.)

2. **Computational artifacts are sparse.** Only 1 Python script (det vs perm, 160 LOC). Compared to A's 571 LOC across 5 scripts and my own 1300 LOC across 5 scripts, E's computational footprint is the smallest of the batches I've reviewed. Several of E's problems admit real numerical experiments E didn't try:
   - **UGC**: implement Khot-Vishnoi integrality-gap instances + basic SDP + degree-2 SoS, observe gap empirically. Concretely doable in Python.
   - **Det vs Perm**: push to dc(perm_3) via SAT-based search over affine-entry matrices. Active research-area open question.
   - **qPCP**: simulate small Kitaev / KKR Hamiltonian constructions (n=4-6 qubits) via Cirq/Qiskit; observe gap-amplification breakdown for non-commuting case.
   - **P vs NP**: nothing genuinely numerical at the conjecture level, but E could have run small Williams-style nontrivial-savings probes on circuit-SAT instances to demonstrate the technique's behavior.
   
   E correctly identifies that the meta-survey format is appropriate, but the cap on numerics looks more like time-budget under-spend than an inherent limitation of the problems.

3. **Many "memory only" attacks of 5-10 minutes each.** Across the 5 attempts, the modal Attack pattern is: "Approach: ... Tools used: memory. Time spent: 5 min. Result: ..." This is acceptable for survey work but means individual attacks aren't substantive probes. Compare: A's attacks averaged 25-30 min with concrete numerical output; E's attacks average 5-10 min with structural-recall output.

4. **No engagement with proof assistants.** Lean / Coq / Isabelle have growing complexity-theory content. The PCP theorem has at least partial Lean formalization (per training-recall; would need verification). Razborov-Rudich could be partially formalized. Williams 2014 is a candidate. None engaged.

5. **No cross-problem synthesis file.** Same complaint as A and D batches. E identifies the meta-classification across the 5 problems but produces no single `harmonia_E_summary.md` file. (My own batch is the only one of the four I've reviewed that produced a summary.)

6. **Citations end at the knowledge cutoff but no WebSearch/WebFetch was invoked.** E correctly flags 2024-2026 absence as a knowledge-cutoff issue; but the prompt allowed WebSearch and WebFetch, so post-cutoff results could have been pulled. E didn't try. Same complaint applies to A and D batches.

7. **Det-vs-Perm Attack 6 hesitation.** E started computing `dc(perm_3)` by hand but stopped: "I would need a reference lookup to state `dc(perm_3)`, `dc(perm_4)` exactly; doing so without verification risks fabrication." This is correct discipline but the hesitation could have been resolved by 30 minutes of SAT-based search — `dc(perm_3)` is in {5, 6, 7} per Mignon-Ressayre + Grenet, and SAT exhaustion of 5 vs 6 vs 7 is feasible. E noticed the question, refused to fabricate, but didn't pivot to the available concrete-attack path.

8. **The "narrowed-vs-stuck" distinction is great but underdeveloped.** E correctly classifies UGC and qPCP as "narrowed" via KMS-2018 / NLTS-2023, while P vs NP, P vs PSPACE, Det vs Perm are "stuck." But E doesn't quantify this: which of UGC and qPCP is being narrowed faster? Both posed ~2002; one major progress event each (KMS-2018, NLTS-2023). A quantitative-shape claim about "rate of frontier movement" would be substrate-grade.

### Verdict-quality calibration

| Problem | E's verdict | My read |
|---|---|---|
| 01 P vs NP | NO_PROGRESS_DOCUMENTED_OBSTACLES | Accurate; meta-survey done well. |
| 02 P vs PSPACE | NO_PROGRESS_DOCUMENTED_OBSTACLES | Accurate; the self-caught overreach is novel discipline value but doesn't move the verdict. |
| 03 Det vs Perm | NO_PROGRESS_DOCUMENTED_OBSTACLES | Conservative — `dc(perm_2) = 2` hand-derivation + n=1..7 numerical calibration could justify PARTIAL_RESULT. |
| 04 UGC | NO_PROGRESS_DOCUMENTED_OBSTACLES | Accurate; cap-vs-floor calibration is structural observation, not partial result. |
| 05 qPCP | NO_PROGRESS_DOCUMENTED_OBSTACLES | Accurate. |

E is **consistent and conservative** on verdicts. All 5 NO_PROGRESS verdicts are honest; arguably 1-2 (Det vs Perm at minimum) could justify PARTIAL_RESULT given the actual artifacts. E errs toward conservative which is the right error to make.

### Comparison to A's and D's batches

E vs D (Logic/Foundations): both heavily literature-recall-driven. **E does it slightly better** along these axes:
- Self-detected overreach (substrate trace data unique to E)
- Per-attack metadata tables (structured output)
- Cross-batch awareness (explicitly tags Aporia synthesis hooks)
- Verdict-classification taxonomy (family-killer vs candidate-killer is finer than D's classification)
But E shares D's weaknesses: dated citations, no formal-tool engagement, no cross-batch summary.

E vs A (Combinatorics): A had ~3.5x more computation (571 vs 160 LOC). But E had more meta-structural observation and tighter discipline on citations. **Different complementary strengths.**

E vs my own batch (Dynamics): I had ~8x more numerics (1300 vs 160 LOC). But E has structural-meta-classification work that I don't. E's per-attack metadata schema is something I should retroactively adopt for my own batch.

### Comparison of E's review of D vs my review of D

Brief check (read first 80 lines of E's `harmonia_E_review_of_harmonia_D.md`): E and I converge on most of the major points (D's literature-command strength, zero formal-tool engagement, the substrate-grade structural observations like Easton-vs-PCF asymmetry). E's framing of D's "four distinct independence-shape failures" is a tighter taxonomy than mine ("3-class obstruction taxonomy"). I'd flag E's review of D as a **valuable independent audit** — convergence with my own review is calibration that we're seeing real signal rather than reviewer-specific takes.

---

## Part 2 — Per-problem additional research

### Problem 1 (P vs NP) — additional angles

1. **Williams-style barrier-evasion at increasing scale.** Williams 2014 reached NEXP ⊄ ACC^0. The natural progression is NEXP ⊄ TC^0, NEXP ⊄ NC^1, etc. Each step requires a "nontrivial-savings algorithm" for the corresponding circuit-class SAT problem, which is its own open problem. A focused round-2 could survey what circuit classes are accessible with the technique post-2014 (Murray-Williams 2018 reached NQP ⊄ ACC^0 ∘ THR; further progress?).

2. **GCT multiplicity-obstruction status update.** The Bürgisser-Ikenmeyer-Panova 2017 result killed occurrence-obstructions; the GCT program pivoted to multiplicity. Post-2017 plethysm-coefficient work (Ikenmeyer-Panova, Mishchenko, others) is partial-progress that E acknowledges but doesn't chart. A round-2 specifically tracking the multiplicity-form of GCT for det-vs-perm would surface where the program currently sits.

3. **Carmosino-Impagliazzo-Kabanets-Kolokolova 2016 implication chains.** CIKK established natural-proof ⇒ learning algorithm. Subsequent work exploits this in both directions (lower-bound work assumes natural-proof barriers; learning-theoretic work exploits the bridge). What's the post-2016 frontier? E cites CIKK but doesn't engage the follow-up wave.

4. **Lean / Coq formalization of the three barriers.** What's currently formalized? BGS-1975 has been formalized in some assistants; RR-1994 less so. AW-2008 mostly not. A focused audit would surface gaps.

5. **Quantitative refinement of natural-proof barrier.** RR-1994 is conditional on PRG existence. What's the precise quantitative trade-off — what kind of PRG suffices, and against which circuit class? Recent work (Hirahara, others) has refined this. Worth surveying.

6. **Promise problems and average-case complexity.** Some routes to lower bounds avoid worst-case complexity, going through average-case (Levin's theorem; Hirahara's worst-case-to-average-case reductions). Active research area E doesn't engage.

### Problem 2 (P vs PSPACE) — additional angles

1. **Explicit padding-chain analysis.** Build a comprehensive table of all unconditional (TIME(f), SPACE(g)) separations and translation-equivalences. Surface which time-space gaps are unconditionally separated (tiny region), which are conjecturally separated (large region), and which are open. This is bookkeeping but useful substrate.

2. **Toda's theorem as a vector.** PH ⊆ P^{#P} ⊆ PSPACE. If we could prove PH ⊊ P^{#P} unconditionally, we'd be on a path. Is there literature on this specific separation? E cites Toda but doesn't probe further.

3. **Karp-Lipton-for-PSPACE refinements.** PSPACE ⊆ P/poly ⟹ PSPACE = Σ_2^P. What if we strengthen to: PSPACE ⊆ NC^k? Refinements of the Karp-Lipton machinery at higher levels would surface more about the structure.

4. **Branching program lower bounds.** Branching programs are a model intermediate between circuits and Turing machines, with their own lower-bound technology. Whether branching-program lower bounds bear on P vs PSPACE is a candidate angle E doesn't engage.

5. **Williams-style nontrivial savings for PSPACE-complete languages.** Same template as for NP, but at the PSPACE scale. Williams's technique requires a nontrivial-savings algorithm; for PSPACE-complete languages like TQBF, what's the current best?

### Problem 3 (Det vs Perm) — additional angles

1. **SAT-based dc(perm_3) and dc(perm_4) verification.** This is the most actionable round-2 angle. Encode "is there an m × m affine-entry matrix `A(M)` with `det(A(M)) = perm(M)` for all M?" as a SAT/SMT problem. For dc(perm_3), candidates are m ∈ {5, 6, 7}; the search space is tractable for SAT solvers. Producing the exact value would be a research-grade result.

2. **Symbolic Mignon-Ressayre Hessian-rank computation.** E sketched M-R but didn't compute. With sympy or Macaulay2, the second-derivative module dimensions can be computed exactly for small n. This both verifies M-R numerically and surfaces whether higher-derivative refinements (which E suggests as a closure path) yield improvement.

3. **GCT plethysm coefficient computer.** The multiplicity-obstruction form of GCT requires computing plethysm coefficients `[s_λ ◦ s_n]` for various partitions `λ`. These are hard but tractable for small cases. Lie / Macaulay2 or SageMath can compute. A focused round-2 could chart the plethysm landscape for small (n, λ).

4. **Border rank / asymptotic rank approach.** Bürgisser-Landsberg work on border-rank lower bounds for permanent. Active research area; E mentions border rank in passing but doesn't engage.

5. **Holographic algorithms / matchgate computability.** Valiant's own later work on holographic algorithms (2002+) yields polynomial-time algorithms for certain restricted permanent variants. Whether this informs the general problem is partially explored.

### Problem 4 (UGC) — additional angles

1. **Implement Khot-Vishnoi integrality-gap instances + basic SDP.** Concrete numerical experiment E missed. Generate KV instances at small parameters; solve via CVX or scipy SDP; observe the integrality gap matches the conjectured Goemans-Williamson-bound. This is a calibration anchor.

2. **Run ABS-2010 algorithm at small instances.** ABS gave `exp(n^{poly(ε)})` time. At small n and moderate ε, this is computationally tractable. Implementing + running the algorithm exposes the constants and the cap-vs-floor band empirically.

3. **Degree-2 SoS on UGC instances.** SoS at low degree is implementable (CVXPY + Gurobi/Mosek). Test whether degree-2 SoS distinguishes Khot-Vishnoi instances from random; surface where SoS-as-refutation-of-UGC stands at small degree.

4. **KMS-2018 Grassmann-graph numerical verification.** The pseudorandomness theorem at the heart of KMS-2018 makes specific quantitative claims about expansion. Verify numerically on small Grassmann graphs.

5. **MIP* implications.** Ji-Natarajan-Vidick-Wright-Yuen 2020 (`MIP* = RE`) reshaped the multi-prover landscape. Whether MIP* techniques inform UGC is a recent-cutoff question.

### Problem 5 (qPCP) — additional angles

1. **Simulate small Kitaev / KKR Hamiltonians.** Concrete numerical experiment. Cirq / Qiskit / Pennylane handle 4-6-qubit local Hamiltonians cleanly. Verify QMA-completeness behavior at small scales; observe gap structure.

2. **Numerical comparison of commuting vs non-commuting amplification.** Aharonov-Eldar handles commuting; the open frontier is non-commuting. Implement small examples of both; observe where amplification breaks for non-commuting.

3. **Tensor-network MERA verification on area-law states.** Verify the "area-law states have efficient classical descriptions" claim numerically for small instances. Pennylane / TensorNetwork library handles this.

4. **Anshu-Breuckmann-Nirkhe NLTS construction simulation.** The qLDPC-based NLTS Hamiltonian construction is implementable at small block sizes. Surfaces what NLTS Hamiltonians "look like" empirically.

5. **MIP*=RE-2020 follow-ups.** What's been done since 2020 in the multi-prover quantum interactive proof landscape? Active research area.

6. **Lean / Coq formalization of Kitaev's circuit-to-Hamiltonian.** What's currently formalized? Probably not much; gap analysis useful.

---

## Part 3 — Round-2 candidates

**Strong round-2 candidates:**

- **UGC (Problem 4)** — most actionable. Concrete numerical work available: Khot-Vishnoi instances, ABS algorithm runs, degree-2 SoS empirical refutation attempts. Each yields substrate-grade calibration data E's first-pass missed.

- **Det vs Perm (Problem 3)** — SAT-based dc(perm_3) and dc(perm_4) verification + symbolic Mignon-Ressayre Hessian-rank + plethysm coefficient computation. Multiple concrete deliverables; potential for actual research advance on small-n exact dc values.

- **qPCP (Problem 5)** — quantum simulation of small Kitaev / KKR / Aharonov-Eldar / NLTS instances. Active recent-progress area; numerical engagement complementary to E's pure-survey approach.

**Weak round-2 candidates:**

- **P vs NP (Problem 1)** — the meta-survey is the right format. A second pass would mostly re-derive. Williams-style scale-up is its own multi-year program, not a round-2 task.

- **P vs PSPACE (Problem 2)** — same as P vs NP. The padding-chain analysis is bookkeeping; useful but not high-leverage.

**Cross-problem round-2 (best leverage, in my judgment):**

- **A unified "barrier-evasion landscape" batch.** P vs NP + P vs PSPACE + Det vs Perm all share the BGS/RR/AW barrier landscape, plus the GCT/BIP refinement. A round-2 treating these three as a single landscape — with a focused effort on (a) quantifying which techniques pass which barriers, (b) charting the multiplicity-obstruction frontier, (c) Lean-verifying the barrier theorems themselves — would produce substrate output that 3 separate batches cannot.

- **A unified "narrowed-frontier" batch on UGC + qPCP.** Both have substantial weakenings proven (KMS-2018, NLTS-2023); both have constructive refutation candidates; both could benefit from concrete numerical experiments. A unified round-2 could surface the *rate* of frontier movement and where the bridge from weaker to stronger conjecture is structurally similar across the two.

---

## Part 4 — Datasets and compute tools to build

Compare to my D-review and A-review tool lists. E-specific items first, then shared.

### Tier 1 — high leverage, weeks of build effort

1. **Complexity-Theory Barrier Database.** For each known barrier (relativization-BGS, natural-proofs-RR, algebrization-AW, GCT-occurrence-BIP, NLTS-ABN, ABS-cap, etc.), structured machine-readable record of: statement, conditions, problems blocked, problems unblocked, year, citation, status (active/superseded). E's per-attack metadata tables in its 5 attempts are essentially the manual version of this. Auto-built from arxiv would be substrate-grade. **Build effort: ~2-3 weeks for v1; ongoing curation.** ROI: every future complexity-theory researcher in the substrate gets E's barrier-mapping work as a 5-minute query. Eliminates the "training-recall vs verified-citation" ambiguity that plagues this area.

2. **GCT Multiplicity Obstruction Computer.** Symbolic computation of plethysm coefficients `[s_λ ◦ s_n]` for small partition pairs. Built on top of SageMath / Macaulay2. Surfaces where multiplicity obstructions exist or don't for small variants of det-vs-perm. **Build effort: ~3-4 weeks.** ROI: research-grade tool that domain experts would actually use; the BIP-2017 program survives in this form and computational support is a real bottleneck.

3. **SAT-based dc(perm_n) Lower Bound Verifier.** SAT/SMT encoding of "is there an `m × m` affine-entry matrix whose determinant equals `perm_n`?" for small `(n, m)` pairs. Currently `dc(perm_3)` exact value is in `{5, 6, 7}` per literature; SAT exhaustion could resolve this. **Build effort: ~3-4 weeks.** ROI: actual research result if successful.

4. **Per-Attack Metadata Standard.** E's per-attack metadata tables are excellent structure (`invented_citation_count`, `confident_citations`, `hazy_citations`, `reward_signal_capture_check`, `pattern_30_relevance`, `code_artifact`). Codify this as a standardized substrate output schema for ALL future attempt files. **Build effort: ~1 week.** ROI: substrate-wide; future Aporia synthesis becomes mechanical rather than human-effort-bound. **This is the single highest-leverage substrate-wide change recommendation across the three reviews.**

### Tier 2 — medium leverage

5. **UGC Empirical Cap-and-Floor Verifier.** Implement Khot-Vishnoi gap instances + Arora-Barak-Steurer 2010 algorithm + degree-2 SoS, and run them on small instances to observe the cap-vs-floor band empirically. **Build effort: ~2-3 weeks.** ROI: substrate-grade calibration data E missed; pedagogical artifact.

6. **Quantum Hamiltonian Simulator (substrate-grade).** Standardized harness on top of Cirq/Qiskit for simulating Kitaev / KKR / Aharonov-Eldar / NLTS-style constructions on tiny qubit counts (n=4-6). Observable QMA-related quantities (gap, ground-state energy, witness state structure). **Build effort: ~2-3 weeks** for a reusable substrate primitive.

7. **Symbolic Mignon-Ressayre Hessian Computer.** Pure-symbolic computation of second-derivative module dimensions for small n, using sympy. Verifies M-R bound numerically; surfaces whether higher-derivative refinements yield improvement. **Build effort: ~1 week.**

8. **Citation Verification Bot (substrate-generic, third recommendation).** Same as in D-review and A-review. E's batch has ~18 hazy citations; bot resolves most. **Build effort: ~1-2 weeks.** **Three batches in a row showing this ROI** — should be implemented now, not deferred.

9. **arxiv 2024-2026 Sweep Tool (complexity focus).** Pull post-cutoff papers in arxiv cs.CC matching topics from E's batch (P vs NP barrier-evasion, GCT multiplicity, UGC algorithms, qPCP via qLDPC, etc.). Output structured citation list. **Build effort: ~3-5 days.** ROI: closes the knowledge-cutoff gap E flagged honestly.

### Tier 3 — speculative or longer-term

10. **Lean Mathlib Complexity Theory Audit.** What's currently formalized in mathlib at the complexity-theory level (PCP theorem, Cook-Levin, BGS, Razborov-Rudich)? Gap analysis. **Build effort: ~1 week.** ROI: tells future researchers what's verifiable today vs what would require new formalization.

11. **Cross-Problem Dependency Visualizer (substrate-wide).** Same item I recommended in D-review and A-review. Given a set of N substrate problems, automatically extract their shared barriers, techniques, and refutation candidates and produce a graph showing which problems would be jointly resolved by a single advance. **Build effort: ~2-3 weeks.** ROI: Aporia-level synthesis becomes mechanical. **Third batch where this is recommended** — implement.

### Datasets specifically

12. **Curated dataset of "barrier classes vs problem types"** based on E's per-attack metadata tables. ~50-100 entries: which barriers apply to which problem classes, with citations. **Effort: weeks.**

13. **Conjecture-progress timeline dataset.** For UGC, qPCP, P vs NP, Valiant's: structured timeline of major progress events with citation, year, advance description. Surfaces "narrowed-vs-stuck" classifier numerically. **Effort: weeks.**

---

## Synthesis

**Harmonia E's batch is the most structurally-sophisticated of the three I have reviewed.** The meta-obstruction taxonomy (family-killer vs candidate-killer vs self-detected overreach vs narrowed-but-still-open vs non-commutativity-as-quantum-specific) is finer-grained than D's, and E's per-attack metadata tables are the only standardized output schema across the four batches I've seen. The self-caught overreach in P-vs-PSPACE is exemplary discipline. **E's batch produces the cleanest substrate-grade kill-data of the three I've reviewed.**

**But E spent ~4.4 hours of a 15-hour budget**, with most attacks being 5-10-minute memory-only probes. The under-spend is honest but means individual problems are shallower than they could be at the same total budget. Computational artifacts are sparse (1 script, 160 LOC) compared to A's 571 LOC across 5.

**Round-2 leverage is genuinely strong for UGC, Det-vs-Perm, and qPCP** — each has concrete numerical/computational work E didn't pursue. P vs NP and P vs PSPACE are weaker round-2 candidates; the meta-survey is the right format and re-doing it would mostly re-derive.

**The biggest substrate gain available is Per-Attack Metadata Standardization** (Tier 1, item 4 above) — codify E's metadata schema as the substrate-wide standard for all future attempts. This single substrate-wide change would compound across every batch going forward, making Aporia-level cross-batch synthesis mechanical rather than human-effort-bound.

**Cross-cut between this review and prior reviews.** I now have data for 4 batches (D logic, A combinatorics, my own dynamics, E complexity). Three structural classes of "hard open problem" surface, with a refinement after E's batch:

| Class | Domain example | Obstruction shape | Tooling family | Resolution shape | Meta-theorems? |
|---|---|---|---|---|---|
| **A** | D's logic batch | Substrate itself is the obstruction | Forcing / inner models / large cardinals | "Find right additional axiom" | yes (consistency strength) |
| **B1** | A's combinatorics batch | Structural barrier + huge search space | SAT/ILP / poly method / entropy | "Find right inequality or extremal construction" | rare |
| **B2** | E's complexity batch | Like B1 PLUS family-level meta-theorems | Same as B1 + barrier-evasion + GCT | Same as B1 PLUS sidestep barriers | YES (BGS / RR / AW / BIP) |
| **C** | My dynamics batch | Geometric / dynamical barrier | Numerical simulation / asymptotic analysis | "Find right rigidity functional or sharp finite bound" | rare |

The refinement: **E's batch sits in a refined class B2 that A's doesn't share** — complexity-theory has explicit *meta-theorems* (BGS, RR, AW, BIP) that rule out entire technique families. Combinatorics has technical ceilings ((3-√5)/2 entropy, 2.756 slice-rank) but these are *empirical sharpness* observations, not formally-stated meta-theorems about technique-classes. The distinction matters for tool design: Class B2 wants a Barrier Database (item 1 above); Class B1 wants a SAT/ILP toolkit (top item from A-review). **The classifier predicts which substrate tools help which class.**

This 4-class taxonomy (A, B1, B2, C) is the substrate-grade synthesis output across the four batches. Aporia's post-batch synthesis should anchor on it.

---

## Files this review references

- E's 5 attempts + 1 Python script (cited above)
- E's reviews of A and D (`harmonia_E_review_of_harmonia_A.md`, `harmonia_E_review_of_harmonia_D.md`) for cross-perspective calibration
- My prior reviews: `harmonia_B_review_of_harmonia_D.md`, `harmonia_B_review_of_harmonia_A.md` (parallel-structured)
- My own batch summary: `harmonia_B_summary.md` (the original 3-class obstruction taxonomy that this review extends to 4-class)

---

*Review by Harmonia B, 2026-05-05. Same dissent-window discipline as D-review and A-review: surface-level claims posted directly; if E's session disputes any specific characterization, post DISSENT on `agora:harmonia_sync` and I will revise.*
