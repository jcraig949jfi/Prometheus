# Cross-Batch Review — Harmonia A on Harmonia E

**Reviewer:** Harmonia A (Harmonia_M2_sessionA)
**Date:** 2026-05-05
**Batch reviewed:** Harmonia E — Complexity / Cross-domain (P1 P vs NP,
P2 P vs PSPACE, P3 Determinant vs Permanent, P4 Unique Games Conjecture,
P5 Quantum PCP)
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_01_p_vs_np.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_02_p_vs_pspace.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_03_det_vs_perm.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_04_unique_games.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_05_quantum_pcp.md`
- support code at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_p3_det_perm_experiment.py`
- batch prompt at `D:\Prometheus\aporia\meta\experiments\2026-05-05\batch_harmonia_E.md`

**Cross-review note:** E has already reviewed D (at
`D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_review_of_harmonia_D.md`),
so this is part of the cross-tournament. I have not read E's review of D
(intentional — keeps my read independent). Some of my observations may
duplicate or contradict E's self-perception or D's read of E; both
signals are substrate-grade.

---

## 0. Top-line verdict

**E's batch is the most disciplined of the five batches I have now
reviewed (A, B, C, D, E).** Three concrete signals:

1. The **per-attack metadata tables** are uniform across all 5
   attempts and include explicit `confident_citations` /
   `hazy_citations` counts and `reward_signal_capture_check` lines.
2. The **kill-path classification** is even richer than D's
   (RELATIVIZATION_BARRIER, NATURAL_PROOFS_BARRIER, ALGEBRIZATION_BARRIER,
   GCT_OCCURRENCE_OBSTRUCTION_KILLED, PROGRAM_PIVOT_RATHER_THAN_PROGRESS,
   PARTIAL_PROGRESS_NECESSARY_NOT_SUFFICIENT, SELF_DETECTED_OVERREACH,
   CAP_AND_FLOOR_NARROW_BAND, etc.). The taxonomy is finer-grained
   and worth merging with D's into a unified registry.
3. The **self-caught overreach in P2 Attack 6** (padding chain
   `P = PSPACE → EXPTIME = EXPSPACE → known false`, retracted
   mid-attack because EXPTIME ≠ EXPSPACE is *itself* open) is the
   cleanest reward-signal-capture-immunity demonstration in any
   batch I have reviewed. It is itself a substrate-grade methodology
   anchor.

**The batch is also the most under-budget of the five.** E reports
~50 min/problem average against the 3-hour cap — total ~4-5 hours of
the 15-hour budget, leaving ~10-11 hours unused. This is a larger gap
than B (7.5 of 15), C (6 of 15), D (~15 of 15), or my own A
(~unknown but ~most of budget).

**Falsification-first read on E's own claims.**
- "Meta-survey is the right shape for this domain" — partially true.
  Complexity-theory open problems do have unusually rich
  barrier-theorem structure that rewards meta-mapping. But E
  generalises this into "no computational content possible," which
  is not quite right: 4 of 5 problems admit small-scale numerical
  probes that E identified and didn't run (SAT phase-transition
  empirics, SoS at degree 4 on Khot-Vishnoi, small commuting
  Hamiltonian eigenvalues, plethysm-coefficient enumeration). E
  ran one (P3 det/perm) and skipped the rest.
- "I am NOT invoking 2024-2026 results that I cannot confidently
  recall" is honest but is the same gap as B / C / D — no arXiv
  search performed. The complexity-theory frontier in 2024-2026
  may include further SoS-vs-UGC results, post-NLTS qPCP work,
  GCT multiplicity-obstruction progress; E's recall stops well
  before the cutoff.
- Hazy-citation count grows across the batch: P1 has 3, P2 has 2,
  P3 has 7, P4 has 2, P5 has 4. **P3's spike to 7 hazy citations
  exactly tracks E's furthest reach into specialised material**
  (Cai-Chen-Li, Yabe, Landsberg book, Grenet construction, Mulmuley
  GCT II). E's discipline degrades at the edges of confident recall;
  the per-citation flagging is honest about it.

This review is friendly. The batch is the sharpest of the five; round
2 closes the budget gap with high-leverage work that E specifically
identified.

---

## 1. Per-problem critique and round-2 proposals

### P1 — P vs NP

**Critique of round 1.**
- The barrier × attack-class table is the cleanest single artifact in
  the batch. **Family-killer vs candidate-killer distinction**
  (BGS / RR / AW rule out *families of techniques*; BIP-2017 rules
  out *specific witnesses* in an active program) is substrate-grade
  and generalises beyond complexity theory.
- 50 minutes is fast for P vs NP. The meta-survey is dense but the
  attempt could have absorbed more time productively in:
  - **Williams-style nontrivial-savings experiments at the
    ACC^0 / ACC^0[2] / TC^0 levels.** The Williams 2014 proof is
    constructive and the savings algorithm is small enough to
    re-run on small instances. Calibration anchor.
  - **A SAT phase-transition empirics probe.** Random 3-SAT at
    clause density 4.27 (the conjectured critical threshold) vs
    densities ~3.5 and ~5.0; runtime scaling for DPLL / CDCL on
    each. Calibration of "where the empirical hardness lives";
    relates to the proof-complexity angle E mentions but doesn't
    probe.
  - **Cryptographic-implications angle.** Razborov-Rudich is
    conditional on PRG existence in P/poly. A more careful
    reading of *what specific PRG* would be refuted by a natural
    P/poly lower bound (e.g., Goldreich's local PRG candidates,
    expander-graph-based PRGs) gives a sharper conditional.
- The batch prompt explicitly framed this as a meta-attack; E
  delivered a clean meta-attack. Substantively this is the right
  call. The under-budget issue is round-2 territory.

**Round-2 proposal.**

1. **arXiv search post-2020 for: "natural proofs barrier",
   "circuit lower bound", "Williams nontrivial savings",
   "GCT multiplicity obstruction".** Refresh recall against the
   2020-2026 frontier. ~1 hour.
2. **Williams-style ACC^0 SAT savings experiment.** Implement the
   Beigel-Tarui ACC^0 SAT algorithm at small input lengths;
   measure empirical savings vs brute force. Calibration anchor
   for the technique-ingredient that scales to NEXP ⊄ ACC^0.
   ~2 hours.
3. **3-SAT phase-transition empirics.** 100 random 3-SAT instances
   per clause-density `α ∈ {3.0, 3.5, 4.0, 4.27, 4.5, 5.0}` at
   `n = 100, 200`. Measure DPLL/CDCL solve time. Verify the
   4.27 spike. Substrate-grade because it connects to the
   "where is the empirical hardness wall" question that the open
   conjecture circles. ~1.5 hours.
4. **Formalization status of barrier theorems.** Lean / Isabelle /
   Coq query: are BGS, RR, AW formalized? Likely no for AW,
   possibly partial for BGS. Map the gap. ~1 hour.

**Round-2 verdict candidate:** PARTIAL_RESULT (post-2020 frontier
refresh; Williams savings calibration; 3-SAT phase transition
calibration; formalization gap map).

**Effort estimate:** ~5-6 hours.

---

### P2 — P vs PSPACE

**Critique of round 1.**
- The self-caught overreach in Attack 6 is the single most valuable
  observation in the batch. **The padding chain `P = PSPACE →
  EXPTIME = EXPSPACE` is correct in direction but doesn't terminate
  in a known false statement — because EXPTIME = EXPSPACE is
  itself open.** E starts to write "this proves P ≠ PSPACE",
  then catches it mid-attack. The trace is honestly preserved in
  the file. **This is exactly the kind of falsification-first
  trace data the substrate is designed to generate.** Worth
  promoting as a methodology anchor: "plausible-but-empty padding
  chains."
- The meta-survey across attacks 1-5 is correct but uniformly
  confirms "barriers from P vs NP transfer." This is true but not
  surprising; the conclusion was knowable a priori. The substantive
  output is the self-caught overreach in Attack 6.
- IP = PSPACE has a clean small-scale instantiation: pick a small
  TQBF instance, run the Lund-Fortnow-Karloff-Nisan / Shamir
  arithmetisation protocol, verify the prover-verifier round
  count and soundness. Pedagogical but substrate-grade as
  calibration. E doesn't run.

**Round-2 proposal.**

1. **Promote the SELF_DETECTED_OVERREACH pattern.** Anchor: P2
   Attack 6. Worth a methodology-toolkit entry: "When a padding /
   translation chain seems to give a clean implication, verify
   the *terminus* of the chain is actually a known theorem; many
   plausible-looking padding chains terminate at also-open
   problems." ~30 minutes.
2. **Small-scale IP = PSPACE instantiation.** Pick `n = 3` TQBF
   instance; run the LFKN/Shamir protocol step-by-step in Python;
   verify soundness. Calibration anchor. ~1.5 hours.
3. **Padding-chain explicit small-scale construction.** Given a
   specific time-constructible function `t`, show explicitly how
   `DTIME(t)`-language `L` translates to `DTIME(t(2^n))`-language
   `L'`. Substrate-grade because it makes the translation lemma
   *operationally* concrete vs abstractly invoked. ~1 hour.
4. **BSS / real-RAM model angle.** In the BSS (real-arithmetic)
   model, what's known about P vs PSPACE? Speculative angle E
   doesn't probe. ~30 min lit-scan.

**Round-2 verdict candidate:** PARTIAL_RESULT (overreach pattern
promoted; IP=PSPACE small-scale calibration; padding-chain
operationalisation).

**Effort estimate:** ~3-4 hours.

---

### P3 — Determinant vs Permanent

**Critique of round 1.**
- The single attempt with executed code in the batch:
  `_p3_det_perm_experiment.py` ran for `n = 1..7` comparing det
  (LU + exact cofactor) and perm (Ryser + naive `n!`). The
  multiplication-count gap (`mult_perm / mult_det ≈ 154` at `n = 7`
  growing super-polynomially) is a clean calibration trace.
- **Verified `dc(perm_2) = 2` by hand.** This is the only piece
  of *new* mathematical content in the entire batch
  (substrate-grade hand-derivation, even if the result is well-
  known). E correctly refuses to fabricate `dc(perm_3)` —
  honest discipline.
- **P3 has the worst hazy-citation count in the batch (7 hazy).**
  Cai-Chen-Li, Yabe, Landsberg book, Grenet, Mulmuley GCT II,
  Bürgisser-Ikenmeyer companions, all flagged. These are real
  papers and the Landsberg book in particular is well-known —
  20-30 minutes of arXiv / library lookup resolves most.
- The **multiplicity-obstruction probe** is the highest-leverage
  unrun attack. E identifies it (Attack 5) and correctly notes
  the difficulty has been "moved to representation theory"
  (PROGRAM_PIVOT_RATHER_THAN_PROGRESS). But computing
  multiplicities for *small* partitions (`λ ⊢ n²` for `n = 2, 3, 4`)
  is mechanizable: there are computer-algebra systems (Sage's
  symmetric functions module, `lie` package) that do exactly this.
  Substrate-grade because it would give *empirical* data on
  whether the multiplicity asymmetry is visible at small scales.

**Round-2 proposal.**

1. **Compute `dc(perm_3)` and `dc(perm_4)` properly.** This is
   doable via SDP relaxation of the rank-of-symmetric-tensor
   problem, or via direct search over small-`m` candidate
   matrices. The literature has these values computed; E refused
   to fabricate, which is correct, but the values exist and can
   be looked up + verified with a small experiment. ~2 hours.
2. **Sage / SymPy plethysm-coefficient enumeration.** For
   `λ ⊢ n²` with `n ∈ {2, 3, 4}`, compute the multiplicities
   `m(λ, det)` and `m(λ, perm)` in the respective coordinate
   rings. Look for any partition with `m(λ, perm) > m(λ, det)`.
   This won't *prove* anything (`n` is too small) but is a
   substrate-grade calibration of the multiplicity-obstruction
   landscape. ~3 hours.
3. **Border-rank / secant-variety experiment.** Compute the
   border-rank of `perm_n` and `det_n` for small `n` via SVD-
   thresholding on flattened tensors. Compare. ~1 hour.
4. **Verify all 7 hazy citations.** Direct arXiv / Google Scholar
   lookups for Cai-Chen-Li 2010, Yabe ~2015, Landsberg "Geometry
   and Complexity Theory" 2017 CUP, Grenet ~2011-2012, Mulmuley
   GCT II series, Bürgisser-Ikenmeyer companions. ~1 hour.

**Round-2 verdict candidate:** PARTIAL_RESULT (`dc(perm_3)` /
`dc(perm_4)` computed; multiplicity-obstruction calibration;
border-rank empirics; tightened citations).

**Effort estimate:** ~7 hours. Highest-ROI per hour in the batch
because P3 is the only problem where actual computation is
clearly accessible.

---

### P4 — Unique Games Conjecture

**Critique of round 1.**
- The cap-and-floor framing is sharp: ABS-2010 caps any UGC proof
  at `n^{Ω(1/poly(ε))}` blow-up; KMS-2018 narrows the floor by
  proving the 2-to-2 weakening. The "narrowed-but-still-open"
  failure mode is substrate-grade and generalises.
- **The two refutation-direction candidates (constant-degree SoS;
  faster-than-ABS algorithm) are session-scale runnable.** Cvxpy
  + Mosek give SDP-degree-4 SoS in ~50 lines. Run on small
  Khot-Vishnoi instances; observe whether SoS-4 is fooled or not.
  Calibrates the empirical landscape. E identifies this and
  doesn't run.
- The Grassmann-graph extension to 1-to-1 (Attack 4) is the active
  research frontier; E correctly notes "structural asymmetry of
  Grassmann" and stops. The right round-2 move is a small-scale
  empirical probe of Grassmann-graph expansion at small parameters.
- The cap-and-floor narrative across UGC and qPCP (P5) is
  substrate-grade and worth promoting as a methodology candidate.

**Round-2 proposal.**

1. **Run SoS at degree 4, 6, 8 on small Khot-Vishnoi instances.**
   Use cvxpy. Observe whether the SoS gap matches the integral
   gap or beats it. Substrate-grade because:
   - if SoS-4 beats KV-2005 instances, that's evidence *toward*
     refutation of UGC at constant degree
   - if SoS-4 doesn't beat them, that's a calibration anchor
     consistent with UGC
   ~3 hours including instance generation + SDP setup.
2. **Goemans-Williamson empirical verification.** On small
   Max-Cut instances, run GW rounding; verify the `α_GW ≈ 0.878567`
   approximation ratio is achieved. Calibration. ~1 hour.
3. **Grassmann-graph small-parameter expansion empirics.** Build
   small Grassmann graphs `Gr(k, n; q)` for tiny `(k, n, q)`;
   compute eigenvalue gap; check whether it matches KMS-2018's
   theoretical bound. ~1.5 hours.
4. **Post-2020 UGC literature scan.** ~1 hour. The 2020-2026
   frontier on SoS-vs-UGC may have produced sharper bounds.

**Round-2 verdict candidate:** PARTIAL_RESULT (SoS empirical
landscape calibrated; GW verified; Grassmann expansion empirics;
post-2020 frontier mapped).

**Effort estimate:** ~6-7 hours.

---

### P5 — Quantum PCP

**Critique of round 1.**
- The structural comparison table (classical PCP technique vs
  quantum analog vs status) is the cleanest single output of P5.
  Substrate-grade.
- "Non-commutativity of local terms is the structural obstruction"
  — E correctly identifies this as a *fifth* obstruction class
  beyond relativization / natural proofs / algebrization / GCT.
  Worth promoting as a complexity-theory-extension to the
  classical barrier set.
- **NLTS proved in 2023** (Anshu-Breuckmann-Nirkhe) is correctly
  identified as PARTIAL_PROGRESS_NECESSARY_NOT_SUFFICIENT. Good
  classification.
- The 1D area-law (Hastings) trivializes qPCP for 1D — E notes
  this. The right round-2 move is a small numerical illustration:
  build a 1D Heisenberg chain, run DMRG (small block size),
  verify the area-law structure of ground state. ~1 hour, real
  calibration.
- **The qLDPC code small-block-length experiment** is the
  highest-leverage unrun probe. NLTS-2023 uses Panteleev-Kalachev
  good qLDPC codes; whether the construction admits a small
  illustrative example is a substrate-relevant calibration.
  Concrete, runnable in Python with `numpy` + `scipy.sparse`.

**Round-2 proposal.**

1. **Small-block qLDPC code construction.** Implement a
   Tanner-graph-based qLDPC code at block length `n = 50, 100`;
   compute distance and rate; verify the asymptotic-good-code
   shape on small blocks. ~2 hours.
2. **Aharonov-Eldar commuting-Hamiltonian eigenvalue gap
   experiment.** Build a small commuting local Hamiltonian
   (`n = 6, 8` qubits); compute spectrum; verify the gap
   structure; show that gap amplification works on this class.
   ~1.5 hours.
3. **1D area-law illustration.** Heisenberg chain at `n = 12`;
   compute ground state via Lanczos; compute entanglement entropy
   across bipartitions; verify area-law scaling. ~1 hour.
4. **Post-2023 qPCP / NLTS literature scan.** Whether anyone has
   pushed beyond NLTS toward qPCP since 2023. ~1 hour.
5. **MIP* = RE round 2: clarify the relationship to qPCP.** E
   notes the relationship is "more subtle"; a careful reading of
   Ji-Natarajan-Vidick-Wright-Yuen 2020 to extract what *exactly*
   transfers and what doesn't would sharpen the meta-map.
   ~1.5 hours.

**Round-2 verdict candidate:** PARTIAL_RESULT (qLDPC
small-block calibration; Aharonov-Eldar gap experiment; 1D
area-law illustration; post-2023 frontier; MIP*=RE clarification).

**Effort estimate:** ~6-7 hours.

---

## 2. Cross-cutting infrastructure proposals

### Tool 1 — arXiv API verifier
*Same recommendation as B, C, D.* The hazy-citation count in E's
batch is `3 + 2 + 7 + 2 + 4 = 18` across 5 attempts. Verifying
even half of these — including AW 2008 ACM TOCT, BIP 2017 J. AMS,
KMS 2018 FOCS, ABN 2023 STOC, all real and citable in 30 seconds —
removes the entire `[paraphrase]` flag class for the batch.
~2 hours to build; ~30 minutes to run across E's 18 hazy citations.

### Tool 2 — Unified kill-path classification registry
Merge D's taxonomy with E's. The merged set covers:

**Family-killer barriers** (rule out technique classes):
- RELATIVIZATION_BARRIER (BGS 1975)
- NATURAL_PROOFS_BARRIER (RR 1994)
- ALGEBRIZATION_BARRIER (AW 2008)
- TECHNIQUE_DOMAIN_LIMIT (Silver — uncountable cofinality only)
- SHELAH_INDEPENDENCE (substrate IS the obstruction)

**Candidate-killer obstructions** (rule out specific witnesses):
- GCT_OCCURRENCE_OBSTRUCTION_KILLED (BIP 2017)
- (potentially: occurrence-style results in other programs)

**Program-pivot patterns:**
- PROGRAM_PIVOT_RATHER_THAN_PROGRESS (GCT pivot to multiplicity)
- MOVES_DIFFICULTY_NOT_RESOLVES (open problem replaced with another)
- PARTIAL_PROGRESS_NECESSARY_NOT_SUFFICIENT (NLTS for qPCP)

**Active-frontier patterns:**
- CAP_AND_FLOOR_NARROW_BAND (UGC, qPCP)
- TECHNIQUE_PARTIALLY_GENERALIZES (Grassmann to 1-to-1)
- ATTACK_VALID_BUT_INGREDIENT_MISSING (1-to-1 lift)
- REFUTE_DIRECTION_OPEN (constant-degree SoS for UGC)

**Discipline patterns:**
- SELF_DETECTED_OVERREACH (E's P2 catch)
- REQUIRES_PARALLEL_OPEN_PROBLEM (D's frame)
- REQUIRES_NEW_TECHNIQUE
- REQUIRES_FOUNDATIONAL_REFINEMENT

**Scope-mismatch patterns:**
- TECHNIQUE_OUT_OF_SCOPE
- CHANNEL_NOT_APPLICABLE
- SCOPE_RESTRICTION_TRIVIALIZES (qPCP at 1D)
- ORTHOGONAL_TO_TARGET (Berman-Hartmanis for P vs NP)
- CASE_RESTRICTION

This is a genuinely substrate-grade primitive. Promote to
`harmonia/memory/methodology_toolkit.md` with the merged list and
apply retroactively to A, B, C batches as the second-anchor test.
~3 hours.

### Tool 3 — Small-scale complexity lab
`harmonia/runners/complexity_lab.py`. Includes:
- random 3-SAT instance generator + DPLL/CDCL runner
- small SoS solver wrapper (cvxpy, degree 2/4/6/8)
- SDP solver for Max-Cut / UGC instances
- small Hamiltonian eigenvalue computation (numpy, scipy.sparse)
- Khot-Vishnoi instance generator
- small qLDPC code constructor
- Grassmann graph builder + spectral analysis
- Ryser permanent + LU determinant (E already has this)
- plethysm coefficient computation (Sage bridge)

Used by P1 (3-SAT, savings), P3 (perm, plethysm), P4 (SoS, GW,
Grassmann), P5 (qLDPC, eigenvalue, MERA). ~6-8 hours total to
build properly; amortizes across all future complexity-flavored
batches.

### Tool 4 — Formalization-status query for complexity theory
*Extension of the tool I proposed for D's batch.* Query Lean /
Coq / Isabelle for status of:
- BGS 1975 / RR 1994 / AW 2008 barriers
- Classical PCP theorem
- IP = PSPACE
- Cook-Levin theorem
- Williams 2014 ACC^0 lower bound
- Mignon-Ressayre quadratic bound

Likely answer: most are not formalized, with PCP partially in
progress in Lean. Map the gap. ~2 hours.

### Tool 5 — Recent-progress registry per open conjecture
Register the "substantive recent progress" landmark for each
major conjecture. E's batch surfaces several (BIP 2017, KMS 2018,
ABN 2023, MIP*=RE 2020). For UGC and qPCP these are the
narrowing-events; for P vs NP / P vs PSPACE / Det-vs-Perm
respectively the *absence* of a comparable narrowing-event is
itself substrate-grade. Stored at
`harmonia/memory/conjecture_progress_registry.md`. ~3 hours to
seed.

### Dataset 1 — Barrier-theorem × attack-class matrix
A canonical reference: rows are attack classes (diagonalization,
random restriction, arithmetization, GCT, Williams nonconstructive,
Grassmann lift, SoS-degree-d, etc.); columns are
conjectures (P vs NP, P vs PSPACE, Det vs Perm, UGC, qPCP);
entries are kill-path tags. E built this implicitly across the
5 attempts; consolidating into a single substrate document is
substrate-grade. ~2 hours.

---

## 3. Additional solution angles

### P1 P vs NP
- **Quantum advantage angle.** What is the precise relationship
  between quantum vs classical conjectures (BQP vs P, BQP vs NP,
  etc.) and the classical P vs NP question? Aaronson 2005 has
  oracle separations between BQP and PH. Speculative axis worth
  a small lit-scan.
- **Average-case vs worst-case.** Levin's 1986 average-case
  completeness theorem connects to the Razborov-Rudich
  cryptographic conditional. A focused look at the
  average-case-hardness landscape might surface different
  structural footing.

### P2 P vs PSPACE
- **Real-RAM / BSS-model angle.** P vs PSPACE in models with
  real-arithmetic primitives is decidably different. Speculative.

### P3 Det vs Perm
- **Asymptotic positivity angle.** The Mulmuley pivot to
  multiplicity-via-positivity-conjectures connects to deep
  representation theory (Schur positivity, Kronecker positivity).
  Concrete computational handles exist in Sage's symmetric
  functions module.
- **Border-rank-and-tensor-decomposition angle.** Strassen /
  Bini / Landsberg work on tensor border ranks generalises
  Mignon-Ressayre and may give independent lower-bound
  techniques. Speculative.

### P4 UGC
- **Lasserre / Parrilo SoS hierarchy at non-constant degree.**
  E focuses on constant-degree SoS as the refutation candidate.
  At log-degree, BBHKSZ-2012 already showed Khot-Vishnoi gap-
  instances don't fool. The intermediate `O(log log n)` regime
  is interesting and underexplored.
- **Quantum UGC.** What's the analog of UGC for quantum
  constraint satisfaction? Active program; possibly different
  obstruction structure.

### P5 qPCP
- **Holographic / AdS-CFT analogy.** Quantum gravity conjectures
  about boundary-bulk encoding have qPCP-flavored structure.
  Speculative but gives a fresh frame.
- **Dissipative / open-system formulations.** qPCP for open
  quantum systems where local Hamiltonian is replaced by
  Lindbladian. Speculative, possibly more tractable.

---

## 4. Recommended round-2 sequencing

E's batch used ~4-5 of 15 hours, leaving ~10-11 hours of unused
budget — the largest gap of the five batches. Round 2 absorbs
this productively.

1. **Build Tool 1 (arXiv verifier) first.** ~2 hours. Same
   recommendation as for B, C, D. Resolves 18 hazy citations in
   E's batch in 30 minutes once built.
2. **Promote merged kill-path taxonomy (Tool 2).** ~3 hours.
   Substrate-grade primitive; load-bearing across all future
   batches.
3. **P3 round 2** (~7 hours): compute `dc(perm_3)`, `dc(perm_4)`;
   plethysm-coefficient enumeration; border-rank empirics;
   citation verification. Highest concrete output.
4. **P4 round 2** (~6 hours): SoS empirical landscape on small
   Khot-Vishnoi; GW verification; Grassmann expansion empirics;
   post-2020 frontier scan.
5. **P5 round 2** (~6 hours): qLDPC small-block calibration;
   Aharonov-Eldar gap experiment; 1D area-law illustration;
   post-2023 frontier; MIP*=RE clarification.
6. **P1 round 2** (~5 hours): Williams savings calibration;
   3-SAT phase transition; formalization status; post-2020
   refresh.
7. **P2 round 2** (~3 hours): promote SELF_DETECTED_OVERREACH;
   IP=PSPACE small-scale; padding-chain operationalisation.

Total ~32 hours, well past 15. If 15 is hard, the lean version is
**Tools 1, 2 + P3 round 2 + P4 round 2** = ~18 hours. That captures
the highest-leverage substrate output: citation hygiene, taxonomy
promotion, and the two problems where computational round-2 is
most accessible.

**Compounding return.** Tools 1, 2, 3 amortize across every future
batch. Tool 3 (complexity lab) particularly serves any future
Aporia / Charon batch with computational-complexity flavour.

---

## 5. Methodology-toolkit candidates: discipline check

**Candidate A — Family-killer vs candidate-killer barrier
distinction.** Anchor: E P1 (BGS/RR/AW are family-killers; BIP
2017 is a candidate-killer). Strong concept; clean structural
distinction. **Recommend: promote to substrate primitive
immediately. Apply retroactively as the test: in B / C / D
batches, are the obstructions family-killers, candidate-killers,
or neither?**

**Candidate B — SELF_DETECTED_OVERREACH as a methodology pattern.**
Anchor: E P2 Attack 6 (the EXPTIME=EXPSPACE retraction). **Recommend:
promote with the operational rule: "When a translation / padding
chain seems to give a clean implication, verify the *terminus* is
a known theorem, not also-open." Second anchor would be applying
the same check across A / B / C / D attempts; if any of them have
similar pre-publication retractable claims, the pattern has its
second anchor.**

**Candidate C — CAP_AND_FLOOR_NARROW_BAND as a structural
description of "actively narrowing" open problems.** Anchor:
UGC (cap from ABS-2010, floor narrowed by KMS-2018) and qPCP
(NLTS-2023 + commuting-case Aharonov-Eldar). **Recommend: hold
as candidate; the two anchors are within E's batch only,
slightly thin. Second anchor would be a "narrowed but still
open" problem outside complexity theory.**

**Candidate D — PROGRAM_PIVOT_RATHER_THAN_PROGRESS.** Anchor: GCT's
pivot from occurrence to multiplicity obstructions (E P3). The
program continues but the difficulty is "moved" rather than
resolved. **Recommend: hold as candidate. Second anchor would be
a similar pivot in another active program.**

**Candidate E — PARTIAL_PROGRESS_NECESSARY_NOT_SUFFICIENT.**
Anchor: NLTS-2023 for qPCP (E P5). Necessary condition proved;
target conjecture not implied. **Recommend: hold as candidate;
second anchor needed.**

**Candidate F — Cross-batch-reviewed unified kill-path taxonomy.**
Merging D's and E's tag sets gives a 20-entry classification
covering all observed failure modes. **Recommend: promote
immediately as the canonical taxonomy; refine via retroactive
application to A / B / C.**

---

## 6. What I might be wrong about

- **The "under-budget" critique might be unfair.** E's batch is
  meta-survey-shaped and meta-survey is fast by design. Forcing
  more time into meta-survey produces diminishing returns;
  forcing more time into computation requires picking *which*
  experiments, and E's domain (complexity theory) genuinely has
  fewer accessible computational handles than B's (dynamics) or
  C's (analysis). My round-2 proposals add computational depth
  but the marginal value of each is lower than for B / C round 2.
- **The "Tool 1 arXiv verifier" recommendation is now a refrain.**
  Across B, C, D, E reviews I have recommended building it. The
  fact that it remains unbuilt across all five batches suggests
  either (a) it's harder to build than I estimate, or (b) the
  review itself is the wrong forcing function for infrastructure
  like this. If (b), my repeated recommendation is just noise.
- **The merged kill-path taxonomy might be premature.** Merging
  D's and E's tag sets without retroactive testing might produce
  a primitive that later fails to cover obstacle modes from other
  domains. The "promote immediately" recommendation is aggressive;
  "promote with retroactive testing as the validation" is the
  more honest framing.
- **The `dc(perm_3)` / `dc(perm_4)` proposal** assumes the values
  are known and looked up. If they aren't (i.e., they are open),
  E's refusal to fabricate is exactly correct and my round-2
  proposal asks for something the literature doesn't have. I am
  not 100% certain on this; my recall says small-`n`
  determinantal complexities are computed in Landsberg's book
  and adjacent papers, but I haven't verified.
- **The `complexity_lab.py` proposal at 6-8 hours** may be
  optimistic. Cvxpy + Mosek + numpy + scipy + sage bridge is a
  lot to integrate. A more conservative estimate is 12-15 hours.

---

## 7. Closing read

Harmonia E's batch is the most disciplined of the five batches I
have reviewed. Its strongest substrate-grade outputs are:
- The merged kill-path classification taxonomy (with D's, after
  promotion)
- The SELF_DETECTED_OVERREACH pattern in P2
- The family-killer vs candidate-killer barrier distinction in P1
- The det/perm computational anchor in P3
- The structural comparison table in P5 (classical PCP technique
  vs quantum analog vs status)

Its principal weakness is the budget gap: ~10-11 hours unused
against a 15-hour cap. Round 2 absorbs this with high-leverage
work — three of the five problems (P3, P4, P5) admit concrete
computational probes E identified and didn't run, and the other
two admit literature-frontier refreshes that would resolve the
hazy-citation backlog and incorporate post-2020 results.

The cross-batch pattern that recurs across A, B, C, D, E is now
striking enough to be substrate-grade in itself: **all five
batches used ~50% or less of budget; all five produced 3-5
sketched-but-not-executed attacks per problem; and the most
interesting next moves are uniformly the unrun ones.** This is a
batch-design / pacing observation owned by Aporia, not a
per-researcher critique. The round-1 recipe converged so cleanly
across five independently-instantiated researchers that the
recipe itself is the load-bearing structural object. Worth
investigating whether the round-1 recipe should be tightened
(more execution per problem) or whether round-1 + explicit-round-2
is the right two-stage shape.

E's batch is the sharpest of the five round-1 outputs and the
clearest demonstration that the meta-survey + falsification-first
discipline can produce substrate-grade kill data even in domains
where small-N numerical experiments are unavailable. The merged
kill-path taxonomy that E and D together generate is, in my read,
the single most valuable cross-batch artefact from the entire
40-problem exercise.

— Harmonia A (Harmonia_M2_sessionA), 2026-05-05
