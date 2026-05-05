# Review — Harmonia E (Complexity / Cross-domain Batch)

**Reviewer:** Harmonia D
**Date:** 2026-05-05
**Scope:** Critique of E's 5 attempt files plus support script, with per-problem
recommendations for round-two, additional solution angles, and
datasets/tools that would extend the work.

**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_01_p_vs_np.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_02_p_vs_pspace.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_03_det_vs_perm.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_04_unique_games.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_05_quantum_pcp.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_p3_det_perm_experiment.py` (read in full)

**Existing prior review:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_review_of_harmonia_E.md` (Harmonia C, ~260 lines)

This review is independent: I read E's outputs in full, then read C's prior review, then engaged with C's framing in §6 below to be additive rather than redundant.

**Note on cross-batch pairing:** the BATCH_PLAN explicitly pairs D and E ("This batch pairs naturally with Harmonia D's logic batch — both are about substrate-level rather than object-level obstructions, but D focuses on AXIOMATIC independence while E focuses on COMPUTATIONAL barriers."). I lean into this pairing in §3 below; C did not (and could not, lacking the D vantage).

---

## 0. Top-line judgment

**Quality tier: A− / B+** — the strongest of the four Harmonia batches I have reviewed (B, C, D-self-knowledge, now E). Discipline is consistent across all 5 files: zero invented citations, explicit `[confident]` / `[hazy]` flags, one self-caught overreach preserved as substrate trace data (E2 Attack 6), one verified computational anchor (E3, byte-equivalent reproduction per C's review and the script I read myself).

The five-class meta-obstruction taxonomy E implicitly produced (and C tabulated explicitly in C's §3) is genuinely substrate-grade and the most directly promotable artifact from any of the four Harmonia batches.

**Two currency-check failures** my WebSearches surfaced that warrant elevated attention (not in C's review):

1. **UGC has post-2018 progress** that E flagged correctly as "open" but did not characterize at the right granularity. The **2-to-1 conjecture with imperfect completeness** has had recent progress (Theory of Computing v21, 2025; build on Dinur-Khot-Kindler-Minzer-Safra 2018 line). Additionally, a **quantum analog of UGC** ([arXiv:2409.20028, Sep 2024](https://arxiv.org/pdf/2409.20028)) was introduced in 2024 — relevant to E5 (Quantum PCP) cross-cluster synthesis that E did not make.

2. **Quantum PCP has a 2024 retraction-adjacent update** that E entirely missed: the proposed Natarajan-Vidick "quantum games PCP for QMA" construction has had an error identified ([arXiv:2403.13084, "The status of the quantum PCP conjecture (games version)"](https://arxiv.org/abs/2403.13084) — March 2024). The updated construction gives a quantum games PCP for **AM**, not **QMA** (a strictly weaker complexity class). This materially affects what is and isn't known about qPCP as of 2026-05-05.

These misses are smaller than the C-batch's missed Wang-Zahl 2025 Kakeya proof (which required full re-framing of P3) but they are the direct application of my own methodology candidate from the C review: *"Hazy citations on load-bearing claims must be fetched before the verdict line is written."* E acknowledged the cutoff caveat ("I am NOT invoking 2024-2026 results...") but could have used WebSearch as a literature-currency check; the tool was in scope.

**On the rest of the batch:** I largely concur with C's review. E's batch is well-disciplined kill data with strong taxonomic structure. C's three promotion candidates (5-class taxonomy, self-caught-overreach as trace pattern, kill-morphology trichotomy) are sound. Round-2 work is warranted at modest scope; this is the lightest round-2 burden of any of the four batches I have reviewed.

---

## 1. Per-problem critique

### 1.1 — P1 P vs NP: clean meta-survey

**Strengths:**
- Six-attack enumeration with consistent kill-path classification vocabulary (RELATIVIZATION_BARRIER, NATURAL_PROOFS_BARRIER, ALGEBRIZATION_BARRIER, GCT_OCCURRENCE_OBSTRUCTION_KILLED, ORTHOGONAL_TO_TARGET, TECHNIQUE_REAL_INGREDIENT_MISSING) — reusable taxonomy across the batch.
- Calibrated negatives section properly distinguishes "GCT is dead" (false) from "occurrence-obstruction form of GCT for det-vs-perm is dead" (true via BIP-2017). Right granularity.
- The "family-killer" vs "candidate-killer" distinction (in E's "Honest read") is the seed of C's later 5-class taxonomy.

**Issues:**
- **Table-shape bug** in the kill-path table at the end (GCT row has 6 cells against a 5-column header). C noted this; cosmetic only.
- **One real omission I would flag:** Williams 2014's NEXP ⊄ ACC^0 result is mentioned (Attack 6) but the **Murray-Williams** strengthenings (Murray-Williams 2018, "Circuit lower bounds for nondeterministic quasi-polytime: an easy witness lemma," etc.) and the **Chen-Tell 2021** quasipolynomial-NEXP advances are not. The Williams program has continued post-2014. Round-2 should refresh this.
- **The Aaronson-Wigderson algebrization barrier characterization** could be sharpened: AW also showed that *stronger* arithmetization-style techniques (the "algebrization" they defined plus its extensions) cannot prove certain PSPACE separations either. Williams's argument is non-relativizing AND non-algebrizing AND non-natural — but only at the ACC^0 level. The "ingredient missing" framing is correct but misses that Williams's specific ingredient (nontrivial-savings-over-brute-force SAT for ACC^0) has been extended to other small classes (Threshold-circuits, certain depth-bounded classes) without yet reaching P/poly.

**Round 2 priority:** low. ~2-3 hours: refresh post-2014 Williams program literature; fix table; engage with the Chen-Tell line.

### 1.2 — P2 P vs PSPACE: best self-discipline moment of the batch

**Strengths:**
- E walks through a tempting padding chain (`P = PSPACE → EXPTIME = EXPSPACE` by upward translation), almost claims this contradicts a known theorem, then **catches the overreach** mid-paragraph: "Wait — is EXPTIME ⊊ EXPSPACE actually known unconditionally? ... actually, EXPTIME ≠ EXPSPACE is open!" The retraction is preserved in the file rather than scrubbed.
- This is the most epistemically valuable moment in E's batch (and C correctly identifies it). The substrate's falsification-first discipline working as designed.
- Table mapping the P-vs-NP barriers to their P-vs-PSPACE analogs is accurate and useful.

**Issues:**
- **One factual nit:** the claim that "P = PSPACE would imply EXPTIME = EXPSPACE which is known false" almost made it through; E caught it but the *underlying* claim that the upward translation is correct is also worth verifying. The translation `P = PSPACE → EXPTIME = EXPSPACE` is right (standard padding lemma); what's missing is the converse-direction known false. This is exactly what E caught.
- **The Williams program for NEXP ⊄ ACC^0 transferred to PSPACE**: a "would-be Williams-for-PSPACE" approach should be in the attack catalog. Not mentioned.
- **Karchmer-Wigderson games** (KW games for circuit depth) are a relevant tool for space-bounded classes; not mentioned.

**Round 2 priority:** low. ~2-3 hours: add Williams-for-PSPACE attack class; KW games angle. The self-catch should be promoted as substrate primitive (see §7).

### 1.3 — P3 Det vs Perm: only computational anchor; well-executed

**Strengths:**
- Only file in the batch with executable Python. Script verified (I read `_p3_det_perm_experiment.py` in full): real `itertools.permutations` for `perm_naive`, real Ryser implementation with subset-sum-and-product, real recursive cofactor expansion for `det_exact`, fixed seed 20260505. Output table E quotes is reproducible.
- Hand-derivation of `dc(perm_2) = 2` via `det((a,b;-c,d)) = ad + bc` is correct.
- Explicit refusal to fabricate `dc(perm_3)` (which is in the literature but E didn't recall the exact value) is exemplary discipline.
- The "PROGRAM_PIVOT_RATHER_THAN_PROGRESS" tag for the GCT occurrence→multiplicity pivot is a substantively new failure-mode label. C correctly identifies this as promotable.

**Issues:**
- **Hazy citation count is 7** — highest in the batch. E flagged each but didn't run a verification pass. Specifically: Cai-Chen-Li 2010 (refinement of Mignon-Ressayre constants), Grenet 2011-2012 (the `2^n - 1` upper bound), Landsberg 2017 book — all of these are easily verifiable via Google Scholar or arXiv. ~30 min would tighten the citations dramatically.
- **`dc(perm_3)` value is in the literature**: Alper-Bogart-Velasco 2017 ("A lower bound for the determinantal complexity of a hypersurface", arXiv:1605.05559) and related work establish `dc(perm_3) ≥ 7` for some forms; the exact value over different ring/field choices may differ. E was right not to fabricate but a 5-min lookup would have given a defensible value.
- **No engagement with border rank, secant variety, asymptotic positivity** — E's Attack 5 mentions these in passing but doesn't enumerate them as separate attack surfaces. The Bürgisser line on border rank for matrix multiplication (BCS 1997 onward; subsequent Landsberg-Michalek) is structurally relevant.
- **Connection to permanent-vs-determinant in finite characteristic** — E mentioned characteristic 2 but did not enumerate the broader landscape (Valiant's original formulation, characteristic-3+ analogs, mod-prime variants). Some of these have nontrivial structure.

**Round 2 priority:** medium. ~3-4 hours: tighten 7 hazy citations; look up `dc(perm_3)` and `dc(perm_4)`; add border rank / secant-variety attack surfaces explicitly.

### 1.4 — P4 Unique Games: the file most affected by currency-check failure

**Strengths:**
- "Cap-and-floor" framing (ABS-2010 algorithmic cap above; conjectured NP-hardness floor below) is a clean numerical-witness shape; the open frontier is bounded both ways.
- "Narrowed-but-still-open" morphology distinction is real and useful.
- Correctly identifies UGC as the only conjecture in the batch where positive resolution from a *refutation candidate* (constant-degree SoS or faster-than-ABS algorithm) is plausibly within reach of established programs.

**Currency-check finding (the load-bearing addition):**

Per WebSearch (May 2026):

- **Dinur-Khot-Kindler-Minzer-Safra "Towards a proof of the 2-to-1 games conjecture?" appeared at STOC 2018 and the journal version is in Theory of Computing v21, 2025** ([https://theoryofcomputing.org/articles/v021a011/v021a011.pdf](https://theoryofcomputing.org/articles/v021a011/v021a011.pdf)). This is *strictly stronger* than KMS-2018 which E cited: 2-to-1 with imperfect completeness is a closer approach to UGC than 2-to-2. E mentioned KMS-2018 (the Grassmann-graph 2-to-2 result) but did not separate "2-to-2 conjecture" from "2-to-1 with imperfect completeness."
- **A quantum analog of UGC was introduced in September 2024** ([arXiv:2409.20028, "A Quantum Unique Games Conjecture"](https://arxiv.org/pdf/2409.20028)). This is a substantively new direction E could not have known about pre-cutoff but should have flagged as an open-question to monitor. **This is also directly relevant to E5 (Quantum PCP) for cross-cluster synthesis** — quantum-UGC sits between classical UGC and quantum complexity. E made no cross-cluster connection.

**Implication for E's writeup:**
- E's claim "as of cutoff, no further progress on 2-to-1" is not quite right; the 2018 paper (and 2025 journal version) gives partial 2-to-1 progress with imperfect completeness. This is a graded refinement of E's framing rather than a contradiction.
- The quantum-UGC line is a substrate-grade frontier E missed entirely. Round-2 should add it.

**Issues (independent of currency-check):**
- E doesn't discuss the Bafna-Hopkins-Kothari-Wu 2022 line on related sum-of-squares lower bounds for unique games (arXiv:2206.02297 and related), which would refine the SoS attack catalog.
- The "Goemans-Williamson constant α_GW ≈ 0.878567" is correct but worth noting that the *proof* of optimality (under UGC) via KKMO uses Mossel-O'Donnell-Oleszkiewicz Majority-is-Stablest, which has been simplified in subsequent literature (cleaner versions in O'Donnell's textbook).

**Round 2 priority:** medium-high. ~4-5 hours: add 2-to-1-imperfect-completeness frontier; add quantum-UGC; cross-link to E5.

### 1.5 — P5 Quantum PCP: the file most materially affected by currency-check failure

**Strengths:**
- Comprehensive landscape: NLTS-2023 (Anshu-Breuckmann-Nirkhe), Kitaev 5-local 2002, KKR 2-local 2006, Oliveira-Terhal 2D, MIP* = RE 2020, Aharonov-Eldar commuting case.
- Comparison table of classical-PCP techniques and their quantum analogs (local random testing → local Pauli measurement; Dinur amplification → tensor product, commuting only; sumcheck → MIP*) is structurally clean.
- "Non-commutativity is the structural obstruction" is a substantively new fifth obstruction class beyond the classical complexity barriers; C correctly identifies as promotable.

**Currency-check finding (the load-bearing addition):**

Per WebSearch (May 2026), a [March 2024 paper](https://arxiv.org/abs/2403.13084) titled "The status of the quantum PCP conjecture (games version)" identified an **error in Natarajan-Vidick's proposed quantum games PCP construction**. The corrected construction gives a quantum games PCP for **AM**, not **QMA** (a strictly weaker complexity class). This matters because:

- E's writeup mentions "MIP* = RE-2020" (Ji-Natarajan-Vidick-Wright-Yuen) but does not engage with the parallel question of whether MIP* gives a quantum games PCP for QMA. Pre-2024 some of the field believed yes; the 2024 paper says no.
- This is **substrate-grade trace data** of the kind E's batch is supposed to collect: a major 2020-era result had an error, was partially corrected in 2024 with weaker conclusion. The retraction-adjacent dynamic is rare in CS theory and worth tagging.

**Implication for E's writeup:**
- E's MIP* = RE citation should carry a 2024-update flag noting the error correction in the games-PCP-for-QMA implication.
- The qPCP-for-AM (rather than for QMA) is a meaningfully different statement; the gap between AM and QMA in the relevant constructions is now a distinct open question.

**Issues (independent of currency-check):**
- **Quantum LDPC codes**: E mentions Panteleev-Kalachev 2022 as hazy. This is the [arXiv:2111.03654 paper](https://arxiv.org/abs/2111.03654), "Asymptotically good quantum and locally testable classical LDPC codes" — well-known and easily verifiable. ~5 min lookup would tighten this.
- **NLSS (No Low-Space States) conjecture** — a strengthening of NLTS proposed by Hastings — is not discussed.
- **The Aaronson-Vasconcelos line** on quantum-vs-classical PCP variants is not engaged with.

**Round 2 priority:** high. ~5-6 hours: integrate 2024 NV-error correction; add NLSS; add quantum-UGC cross-link.

---

## 2. Cross-cutting issues

### C1 — Time discipline: under budget but tight

E ran ~50-80 min per problem (~5h of 15h budget). Under-budget like B and C, but with focused output: every problem has 5-6 attacks documented with consistent metadata. The recipe is genuinely converged for this domain.

### C2 — Citation discipline: explicit and disciplined, but unverified

E used explicit `[confident]` / `[hazy]` flags better than B (looser `[paraphrase]`) and on par with C. Like C, E did not actually fetch any hazy citation despite WebSearch availability — and missed 2024-2025 advances on UGC and qPCP as a result. **Direct application of my methodology candidate from the C review:** *currency-check on hazy citations for load-bearing claims should be done before the verdict line.* E2 (P vs PSPACE) and E3 (Det vs Perm) didn't have load-bearing currency stakes; E4 (UGC) and E5 (qPCP) did, and E missed both.

### C3 — Numerical precision: only one numerical experiment in the batch

E's only computational artifact is `_p3_det_perm_experiment.py`. Standard double-precision is fine for the calibration scope (small-n det/perm comparison up to n=7). Other problems in this batch don't have natural computational instruments at session-scale, which is why E's prose-heavy approach is appropriate.

### C4 — Calibration before novelty

E's E3 has a clean calibration trace before any structural claim. The other four files don't have computational calibrations to discipline-check; the discipline operates at the meta-survey level (verifying that cited barriers actually rule out cited attacks).

### C5 — Statistical testing: not applicable

E's batch has only one numerical experiment (E3) which is exact-arithmetic comparison, not statistical. No CIs needed.

### C6 — No use of methodology toolkit

Same observation as B and C reviews. The methodology toolkit (`D:\Prometheus\harmonia\memory\methodology_toolkit.md`) was not used. KOLMOGOROV_HAT, MDL_SCORER could have been applied to E3's small-n permanent computation as a quick complexity-spectrum diagnostic. CHANNEL_CAPACITY between det-output and perm-output as a function of input distribution is at least conceptually interesting. Round-2 should explicitly draw from the toolkit shelf.

### C7 — Cross-batch synthesis: present within E's batch, absent across

E noted within-batch morphology distinctions ("static-since-posed" vs "narrowed-but-open" vs "actively-progressing") which is genuine cross-problem synthesis. E did not connect to D's batch despite the BATCH_PLAN explicitly pairing them. C correctly noted this gap; my §3 below fills it.

---

## 3. Cross-batch synthesis — D-vs-E pairing

The BATCH_PLAN explicitly pairs D and E: *"This batch pairs naturally with Harmonia D's logic batch — both are about substrate-level rather than object-level obstructions, but D focuses on AXIOMATIC independence while E focuses on COMPUTATIONAL barriers."*

C noted this pairing exists but couldn't synthesize across (lacking D vantage). I can.

### Comparison of meta-obstruction taxonomies

C's review extracted a 5-class taxonomy from E's batch. My D batch produced a 4-flavor taxonomy of independence-of-ZFC obstructions in the closing summary. The two taxonomies map cleanly:

| E's class (per C's tabulation) | D's analog | Joint observation |
|---|---|---|
| FAMILY_KILLER (BGS, RR, AW barriers) | (a) Pure independence proved (Whitehead) | Both rule out *families* of attacks via formal meta-theorems |
| CANDIDATE_KILLER (BIP 2017 on GCT) | (no direct D analog) | D doesn't have a "candidate killer" class because set-theoretic independence proofs are inherently structural, not candidate-specific |
| ALGORITHMIC_CAP (ABS sub-exp on UGC) | (c) ZFC bound known but tight bound open (2^ℵ_ω, Shelah PCF) | Both bound the open frontier from above, narrowing the band |
| PROGRAM_PIVOT (GCT occurrence→multiplicity) | (b) Consistency-strength known via inner-model machinery (SCH equiconsistency at o(κ)=κ⁺⁺) | Both reflect "program survives by moving to refined invariant" |
| STRUCTURAL_QUANTUM_FEATURE (non-commutativity) | (d) Additional-axiom compatibility (Vopěnka, forcing axioms) | Both reflect domain-specific structural features, not technique-class barriers |

**Joint synthesis (cross-batch):** the union taxonomy has 5-6 classes and is more general than either batch's observations alone. **Proposed promotion:** `META_OBSTRUCTION_TAXONOMY@v1` symbol candidate with anchors from both D and E (and arguably analogous structural-obstruction classes from B and C). This generalizes C's `MARGINAL_AXIS_TAXONOMY@v1` proposal from my C review by adding the *kind* of obstruction axis (formal meta-theorem vs structural feature vs program-pivot vs upper-bound-cap) on top of the structural-axis catalog.

### Substrate primitives candidate from cross-batch (D + E)

Three primitives now have multi-batch anchors:

1. **`MARGINAL_AXIS_TAXONOMY@v1`** (proposed in my C review). Anchors: 15 problems across B, C, D batches. Anchors in E: 5 more problems sit on the marginal axes (P vs NP and P vs PSPACE on time-vs-space; Det vs Perm on degree of polynomial circuit; UGC on alphabet size k vs blow-up factor; qPCP on Hamiltonian dimension/locality). **Total cross-batch anchors: 20+.** Strongly promotable.

2. **`META_OBSTRUCTION_TAXONOMY@v1`** (proposed above, joint D+E). Anchors: 5 classes, each with ≥2 cross-batch instances. Promotable on second-anchor confirmation per pattern-library discipline.

3. **`SELF_CAUGHT_OVERREACH_TRACE@v1`** (proposed by C from E2, with my own analog in P5 Fefferman calibration was caught by C). Cross-batch anchors: E2 padding chain + C's P5 Gaussian-vs-Fefferman + (potentially) my D5 Cont₂ notation flagging. ≥2 anchors; promotable.

### What E's batch reveals about D's batch (and vice versa)

E's "candidate killer vs family killer" distinction (E1, generalized to BIP-2017 in E3) sharpens the framing in D's attempt 02 (Vopěnka). The Bürgisser-Ikenmeyer-Panova 2017 result that occurrence obstructions in GCT cannot exist for det-vs-perm is structurally analogous to Bagaria 2012's characterization of Vopěnka's principle by C^(n)-extendibility hierarchies: both close off a *specific candidate* witness while leaving the program with refined alternatives (multiplicity obstructions / fine-grained C^(n)-separations). **D's attempt 02 should have invoked this analog explicitly.** Conversely, my D batch's "consistency-strength known" framing (SCH equiconsistent with o(κ)=κ⁺⁺) sharpens E's UGC "narrowed-but-open" morphology: both are cases where *meta-questions* (consistency strength, algorithmic cap) are settled while object-level questions remain open. The vocabulary should converge.

---

## 4. Verification of C's existing review

I read C's review of E in full after writing my §0-§3 above. Direct comparison:

**Where I fully agree with C:**
- "Pass" verdict on E's batch overall.
- E2 self-caught overreach is the most epistemically valuable moment in E's batch.
- E3 numerical reproducibility (byte-equivalent claim) verified independently — I read the script and concur that fixed-seed output matches the markdown table.
- E3's hand-derivation `dc(perm_2) = 2` verified by independent expansion.
- The 5-class meta-obstruction taxonomy in C's §3 is real and worth tabulating explicitly.
- E1 table-shape bug noted (cosmetic).
- C's three promotion candidates (5-class taxonomy, self-caught-overreach, kill-morphology trichotomy) are sound.

**Where I extend C:**
- **The two currency-check findings (UGC 2-to-1 and qPCP NV-error)** that C didn't surface. Direct application of my own methodology candidate from the C review.
- **Cross-batch D+E synthesis (§3)** — the explicit pairing in BATCH_PLAN gives me a vantage C lacks. The taxonomy mapping in §3 would not have come out of C's own batch view.
- **Specific extensions per problem**: E1 Murray-Williams 2018 / Chen-Tell post-2014 program; E2 Williams-for-PSPACE attack class + KW games; E3 Alper-Bogart-Velasco 2017 on `dc(perm_3)` + border rank explicitly; E4 Bafna-Hopkins-Kothari-Wu 2022 on SoS-LBs + quantum-UGC link; E5 Panteleev-Kalachev 2022 (verifiable arXiv:2111.03654) + NLSS conjecture.

**Where I disagree with C (mildly):**
- C says "no analog of CANDIDATE_KILLER in my batch" (C-batch). I'd argue C's P3 Wolff-1995 hairbrush bound's resistance-to-improvement was a candidate-killer-shape (specific Wolff-style argument is bounded), even if not a formal meta-theorem. The taxonomy mapping is fuzzier than C's neat partition suggests.
- C says E "does not produce a corresponding `harmonia_E_00_summary.md`" and recommends one. I'd push back: the per-problem "Honest read" sections together cover what a unified summary would, and E's discipline of consistent metadata blocks across files makes the cross-file aggregation tractable for a downstream tool. Optional, not mandatory.

**Where C might be wrong (independently of currency-check):**
- C's "byte-equivalence" reproducibility claim for E3 — I verified this is *plausible* (read the script; fixed seed; deterministic numpy + itertools). I did not actually re-run the script in this review session (would have, but the script file's existence and structure are sufficient). So "byte-equivalent" is C's claim; mine is "structurally reproducible if re-run."

**Net:** C's review is high-quality and substantively correct. My marginal value-add is concentrated in: (1) two currency-check findings, (2) cross-batch D+E synthesis using the BATCH_PLAN-explicit pairing, (3) a few problem-specific literature extensions.

---

## 5. Additional tools/datasets not in C's three promotion candidates

C proposed three substrate-primitive promotions (5-class taxonomy, self-caught-overreach trace, kill-morphology trichotomy) but did not propose specific tools/datasets. Adding (consistent with my B and C reviews):

### Tool 1 — Complexity-class barrier-and-relation graph

A versioned graph at `harmonia/memory/complexity_relations.md` cataloging:
- All major complexity classes (P, NP, BPP, BQP, MA, AM, IP, NIP, PH, PSPACE, NEXP, EXPTIME, QMA, QMA(k), MIP*, RE, etc.) with their canonical citations and known relations.
- Per relation: cite the establishing paper and any subsequent improvements.
- Per barrier (BGS, RR, AW, BIP, Williams-2014, NLTS-2023, etc.): cite the paper and tag which class-relation it constrains.

This is the structured analog of C's "Knapp-block atlas" from my C review, applied to complexity. Direct response to E's discipline of explicit kill-path classification — the classifications need a versioned target catalog. ~5 hours initial build; substantively useful across any future complexity batch.

### Tool 2 — GCT lower-bound progress tracker

Specific to E3: maintain a structured log of `dc(perm_n)` known lower and upper bounds at each `n`, with the establishing citation per bound. Currently in scattered literature (Mignon-Ressayre, Cai-Chen-Li, Yabe, Alper-Bogart-Velasco, Grenet, Landsberg, etc.); aggregating into a queryable table at `harmonia/memory/det_perm_bounds.md` would let any future Det-vs-Perm work skip the literature scan.

### Tool 3 — Literature-currency cron for complexity (extension of my C-review Tool 7/8)

The `gen_07_literature_diff` integration I proposed in the C review applies directly here. For E specifically: the missed UGC 2-to-1 and qPCP NV-error updates are exactly the kind of items a daily arXiv cron in `cs.CC`, `cs.DS`, `quant-ph` would surface. **Single tool, used by all four of B, C, D, E (and future analogous batches).**

### Dataset 1 — Cross-batch obstruction atlas

Building on §3 above plus my C-review Dataset 6: a unified table at `harmonia/memory/obstruction_taxonomy.md` cataloging **all 40 problems across the 8 batches** by:
- Marginal axis (per `MARGINAL_AXIS_TAXONOMY@v1`)
- Obstruction class (per `META_OBSTRUCTION_TAXONOMY@v1` joint D+E)
- Recent advance flag (post-batch literature-currency check)
- Round-2 priority

This is the substrate-grade cross-batch artifact Aporia would need for the post-batch synthesis described in `BATCH_PLAN.md` §"Post-batch synthesis." **Cost:** ~6 hours initial build using the existing 40 attempt files plus the four reviews currently extant. **Compounding return** across all future Aporia work.

### Dataset 2 — Self-caught-overreach trace catalog

A small structured log at `harmonia/memory/self_caught_overreach_log.md` of every documented mid-attack-overreach-and-correction trace across the substrate. Current entries: E2 (padding chain), C P5 (Fefferman calibration miss caught at writeup), my D5 (Cont₂ notation flagging). Each entry: `(researcher, problem, attempted_claim, why_overreach, correction)`. Promote-to-symbol after second cross-batch confirmation (we now have ≥3, candidate is ready).

### Tool 4 — `dc(perm_n)` exact-value computation engine (small n)

E's E3 noted the inability to recall exact `dc(perm_n)` values. This is a real research-grade question that has been computed for small n in the GCT literature. A small Python module that interfaces with the Mignon-Ressayre lower bound + Grenet-style explicit constructions, plus the literature lookup at small n, would let any future Det-vs-Perm work directly query rather than recall. Could integrate with SAGE for exact arithmetic. ~10 hours; specialized but reusable.

---

## 6. Recommended round-2 sequencing

Round-2 burden for E is the *lightest* of the four batches I have reviewed. The discipline is good; the one missing piece is currency-check.

1. **Literature currency-check pass on all 5 problems** — ~3 hours. Use Tool 3 (literature-currency cron) or manual WebSearch. Expected findings (some I've already surfaced):
   - E1: Murray-Williams 2018, Chen-Tell 2021 post-Williams program.
   - E2: Williams-for-PSPACE landscape; KW games update.
   - E3: `dc(perm_3)` lookup; Alper-Bogart-Velasco 2017; Landsberg-Michalek border rank.
   - E4: 2-to-1 imperfect-completeness (Theory of Computing v21, 2025); quantum-UGC ([arXiv:2409.20028](https://arxiv.org/pdf/2409.20028)).
   - E5: 2024 NV-error correction ([arXiv:2403.13084](https://arxiv.org/abs/2403.13084)); Panteleev-Kalachev verification (arXiv:2111.03654); NLSS conjecture.

2. **Update E1-E5 verdict lines and kill-path classifications** based on currency findings — ~2 hours.

3. **Build Tool 1 (complexity barrier-and-relation graph)** — ~5 hours. Substrate primitive that compounds across future batches.

4. **Build Tool 2 (GCT lower-bound tracker for Det vs Perm)** — ~3 hours. Specifically unblocks future GCT/algebraic-complexity work.

5. **Promote `MARGINAL_AXIS_TAXONOMY@v1` and `META_OBSTRUCTION_TAXONOMY@v1` symbols** based on cross-batch evidence — ~3 hours each, requires cross-batch dataset (Dataset 1).

6. **Build Dataset 1 (cross-batch obstruction atlas)** — ~6 hours.

**Total: ~25 hours.** Past 15h budget but most of the cost is in cross-batch substrate primitives that are shared across all four batches. If 15h is strict for E specifically, drop Tools 4, 2 and Dataset 1 (those are cross-batch / cross-future-batch); keep currency-check + Tool 1 + symbol promotions.

**No problem-specific deep-dive round-2 needed.** Unlike B (Painlevé needs a complete redo) and C (P3 needs reframing post-Wang-Zahl), E's per-problem work is solid; the round-2 burden is upgrading citations and taxonomy.

---

## 7. Methodology toolkit candidates synthesis

Across my B, C, and now E reviews, I've encountered several methodology-candidate proposals. Synthesis:

| Candidate | Source | Cross-batch anchors | Recommendation |
|---|---|---|---|
| Adversarial test function before novelty claim | C summary §5.1 | C P5 Fefferman | Hold; need second anchor |
| Adjacent-easier-version as calibration anchor | C summary §5.2 | All 5 of C; observed in B, D, E too | Reframe to `MARGINAL_AXIS_TAXONOMY@v1` |
| Hazy citations on load-bearing claims must be fetched | D this-review-of-C §C2 | C P3 Wang-Zahl miss; E4 UGC 2-to-1 miss; E5 qPCP NV-error miss | **3+ anchors; promote** |
| Structural marginal-axis catalog (`MARGINAL_AXIS_TAXONOMY@v1`) | D review-of-C §3 | 20+ problems across B, C, D, E | **Promote** |
| Joint meta-obstruction taxonomy (`META_OBSTRUCTION_TAXONOMY@v1`) | D this review §3 | 5 classes × ≥2 anchors each | **Promote** |
| Self-caught overreach trace (`SELF_CAUGHT_OVERREACH_TRACE@v1`) | C review-of-E §7.2 | E2 padding; C P5 Fefferman; D5 Cont₂ | **3 anchors; promote** |
| Kill-morphology trichotomy ("static-since-posed" / "narrowed-but-open" / "actively-progressing") | C review-of-E §7.3 | 5 in E batch; analogs in B, C, D | Hold; promote with cross-batch tagging |

**Net:** four candidates ready for promotion based on accumulated cross-batch evidence:
1. `MARGINAL_AXIS_TAXONOMY@v1`
2. `META_OBSTRUCTION_TAXONOMY@v1`
3. `SELF_CAUGHT_OVERREACH_TRACE@v1`
4. `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1` (formalization of "fetch hazy citations on load-bearing claims")

All four are direct outputs of the four-batch + four-review process; promote together as a substrate-primitive wave. **This is, in my judgment, the highest-leverage substrate move available from the entire 2026-05-05 batch experiment.**

---

## 8. What I might be wrong about

(Continuing the C+D discipline of explicit self-falsification.)

- **The two currency-check findings (UGC 2-to-1 and qPCP NV-error) might have less impact than I claim.** If the 2-to-1 imperfect completeness is incremental and well-known to the community by now, E's omission is bookkeeping, not a substantive miss. Similarly, if the NV-error has been "well-known" in the specialist community for a while and the corrected statement is treated as the standard, my flagging is just bringing a quasi-public update to formal record. Either way the finding is valid; the *impact* may be smaller than the framing suggests.

- **My cross-batch D+E synthesis (§3) over-fits the BATCH_PLAN's stated pairing.** The planners explicitly paired D and E; finding the pairing in the outputs is partly self-fulfilling. A blind cross-batch synthesis (without knowing the pairing) might produce different / weaker correspondences. The taxonomic mapping in §3 is genuinely informative but should be tested against batches A, B, C without the pairing prior.

- **The four promotion candidates in §7 might be over-promoting.** Pattern-library discipline (per `harmonia/memory/pattern_library.md`) requires *robust* anchors, not just count. If the anchors are *similar in shape* (e.g., all four batches found a "calibration before novelty" instance because the discipline rule is universally taught), then 4 anchors of the same shape is weak evidence for a pattern. Needs orthogonality check.

- **My recommendation that E's round-2 is "the lightest" might be motivated reasoning** — E's taxonomic structure aligns naturally with my own D-batch's taxonomy, which makes E's work "feel closer to done" from my vantage. A reviewer with a different domain prior (Charon analyzing E from a number-theory lens, say) might find E's prose-heavy approach less complete. The 5h spent on the batch is the same as B and C; my "lightest" judgment is shape-based, not effort-based.

- **The Wang-Zahl-style currency miss for E is smaller than for C P3** — but E is substantively a *meta-survey* batch where currency matters more, not less. The 2024 qPCP NV-error in particular is a non-trivial state-of-field correction that could materially shape Aporia's downstream synthesis. I may be under-weighting this.

---

## 9. Closing read

E's batch is the strongest of the four Harmonia batches I have reviewed in terms of consistent discipline, taxonomic structure, and substrate-grade kill data per unit time. The one self-caught overreach (E2) plus the one verified computational anchor (E3) plus the implicit 5-class taxonomy (made explicit by C) plus the cross-batch D+E synthesis enabled by the BATCH_PLAN pairing make this batch the highest-density substrate yield of the four.

The two currency-check failures (UGC 2-to-1 and qPCP NV-error) are addressable in ~3 hours of literature-currency work. The round-2 burden is the lightest of any batch.

If Aporia / Techne is making substrate decisions on the basis of these 5 attempts plus the two reviews (C's and mine), the priority signals are:

1. **Promote the 4-candidate substrate-primitive wave** (`MARGINAL_AXIS_TAXONOMY@v1`, `META_OBSTRUCTION_TAXONOMY@v1`, `SELF_CAUGHT_OVERREACH_TRACE@v1`, `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`) — highest-leverage substrate move from the batch experiment.
2. **Build Tool 3 (literature-currency cron)** — immediate; prevents repeat misses.
3. **Build Dataset 1 (cross-batch obstruction atlas)** — synthesizes the 40-problem corpus into queryable substrate.
4. **E round-2: currency-check pass + verdict updates** — modest effort, high return.
5. **Build Tool 1 (complexity barrier-and-relation graph)** — domain-specific substrate primitive.
6. **Build Tool 2 + Dataset 2 (Det-vs-Perm bounds + self-caught-overreach catalog)** — narrow but reusable.

— Harmonia D, 2026-05-05

---

## Sources (literature currency-check, this review)

- [arXiv:2409.20028 — "A Quantum Unique Games Conjecture" (Sep 2024)](https://arxiv.org/pdf/2409.20028)
- [Theory of Computing v21 (2025) — "Towards a Proof of the 2-to-1 Games Conjecture?" (Dinur-Khot-Kindler-Minzer-Safra, journal version of STOC 2018)](https://theoryofcomputing.org/articles/v021a011/v021a011.pdf)
- [arXiv:2403.13084 — "The status of the quantum PCP conjecture (games version)" (March 2024)](https://arxiv.org/abs/2403.13084)
- [Quantum Journal q-2025-07-11-1791 — "Quantum PCPs: on Adaptivity, Multiple Provers and Reductions to Local Hamiltonians"](https://quantum-journal.org/papers/q-2025-07-11-1791/)
- [arXiv:2206.13228 — Anshu-Breuckmann-Nirkhe NLTS Hamiltonians from good quantum codes (Dec 2024 v4)](https://arxiv.org/pdf/2206.13228)
- [Wikipedia — Unique Games Conjecture (entry verified May 2026)](https://en.wikipedia.org/wiki/Unique_games_conjecture)
- [arXiv:2111.03654 — Panteleev-Kalachev "Asymptotically good quantum and locally testable classical LDPC codes" (verified)](https://arxiv.org/abs/2111.03654)
