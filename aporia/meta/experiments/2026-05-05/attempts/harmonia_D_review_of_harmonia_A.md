# Review — Harmonia A (Combinatorics Batch)

**Reviewer:** Harmonia D
**Date:** 2026-05-05
**Scope:** Critique of A's 5 attempt files plus support scripts, with per-problem
recommendations for round-two, additional solution angles, and
datasets/tools that would extend the work.

**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_01_erdos_faber_lovasz.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_02_frankl_union_closed.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_03_sunflower.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_04_cap_set.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_05_hadamard_matrix.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch\` (5 attack scripts: efl, frankl, sunflower, capset, hadamard)

**Existing prior reviews:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_review_of_harmonia_A.md` (Harmonia B, ~265 lines)
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_E_review_of_harmonia_A.md` (Harmonia E, ~675 lines)

This review is independent: I read A's outputs in full, then read both prior reviews, then engaged with B and E in §6 below to be additive rather than redundant. **A is the most-reviewed batch in the experiment** (3 reviewers including me); my marginal value-add is concentrated in: (1) literature currency-check via WebSearch, (2) substrate-internal-tool verification, (3) cross-batch synthesis from D's vantage spanning all four prior reviews.

---

## 0. Top-line judgment

**Quality tier: A− / B+** — alongside E, the strongest of the four Harmonia batches I have reviewed. **The most computationally substantive batch of the four**: 571 LOC of working Python, real numerical tables in every problem, ~12.5h actual time spent (closest to the 15h budget). Discipline is the strongest in the experiment: explicit "I refuse to invent" tags throughout, honest computational ceilings flagged at every problem, one self-caught mid-write error preserved as substrate trace data (Frankl Gilmer-constant correction).

**Three critical findings my WebSearches and substrate-internal verification surfaced** that warrant elevated attention (none in B's or E's reviews):

1. **Hadamard 668 is still the smallest open order as of 2024-2025** ([Wikipedia, verified May 2026](https://en.wikipedia.org/wiki/Hadamard_matrix); [Epoch AI Frontier Math entry](https://epoch.ai/frontiermath/open-problems/hadamard)). A's writeup states "n = 668 resolved 2005 (Kharaghani-Tayfeh-Rezaie)" — which appears wrong. The BATCH_PROMPT itself has an internal contradiction, listing 668 as both "resolved 2005" *and* "the smallest open n where 4n has no known Hadamard matrix is 668". A faithfully reported the prompt without catching the contradiction. The 2024-2025 frontier of small open orders is **{668, 716, 892, 1132, 1244, 1388, 1436, 1676, 1772, 1916, 1948, 1964}** (12 orders ≤ 2000). KTR 2005 most likely resolved a different specific order (commonly cited: 428).

2. **Liu 2023 pushed the Frankl bound past Cambie to ~0.38271** via a conditional IID coupling approach. A's writeup correctly stops at Cambie's `(3-√5)/2 ≈ 0.38197` and identifies the entropy-method ceiling but misses Liu's 2023 push past Cambie. Verified via [arXiv preprint and ResearchGate listing](https://www.researchgate.net/publication/379520332_Improving_the_Lower_Bound_for_the_Union-closed_Sets_Conjecture_via_Conditionally_IID_Coupling). Modest but real.

3. **`techne/lib/sat_solver.py` actually exists** (verified — file is real, functional PySAT + Kissat 4.0.4 / Glucose backends, forged 2026-04-26 per REQ-026). E's review flagged this as a possibility ("If still in tree at `techne/lib/sat_solver.py`, this gives DIMACS-CNF SAT immediately"). I confirmed. **A's recurring complaint "I lack a SAT solver in this environment" was a substrate-discoverability gap, not an actual environmental constraint.** This is the single highest-impact finding in this review for any future round-2 of A's batch — and a substrate-grade observation about the Prometheus toolchain's discoverability.

**On the rest of the batch:** B and E's reviews substantively cover the per-problem critique with strong overlap. Both correctly identify A's environmental compute envelope (no SAT/ILP solver) as the binding constraint that capped Attack 1 short of the informative regime in every problem. Both propose a SAT-toolkit round-2. B's review is heavier on cross-problem synthesis and the 3-class obstruction taxonomy; E's review is heavier on per-problem concrete round-2 plans and tabulated obstruction-class matrices. I largely concur with both.

---

## 1. Per-problem critique (brief; B and E covered this in depth)

### 1.1 — P1 Erdős-Faber-Lovász

B's and E's verdicts: PARTIAL_RESULT justified; small-`n` verification + lit synthesis + KKKMO `N_0` diagnosis. Both note the SAT-encoding ceiling at `n=7`.

**My adds:**
- A correctly identified that even an explicit `N_0` extraction from KKKMO is computationally inaccessible — this is essentially the same epistemic shape as my D batch's "consistency-strength known but actual decision computationally impossible" (e.g., `2^ℵ_ω < ℵ_{ω₄}` Shelah PCF bound; the bound exists but the actual value is undecidable in ZFC).
- The fractional chromatic angle (B and E both mention) is genuinely stronger than what A explored — Faudree, Gyárfás, Schelp proved `χ_f(G) = n` for EFL graphs. The integer-vs-fractional gap is exactly what the LLL/nibble approach controls.
- Bernshteyn 2020+ refinements of LLL via entropy compression are post-A's literature and worth a round-2 read.

### 1.2 — P2 Frankl Union-Closed

B's and E's verdicts: INCONCLUSIVE justified. Both note the entropy-ceiling diagnosis is real but the abandoned Cambie simulation is the round-2 priority.

**My adds (load-bearing currency-check):**
- A's literature scan stops at "Yu 2023 follow-ups" (paraphrased). Actually a substantive 2023-2024 advance happened that A missed: **Liu 2023, "Improving the Lower Bound for the Union-closed Sets Conjecture via Conditionally IID Coupling"** pushed the bound to **~0.38271** ([arXiv 2306.12351 / ResearchGate](https://www.researchgate.net/publication/379520332_Improving_the_Lower_Bound_for_the_Union-closed_Sets_Conjecture_via_Conditionally_IID_Coupling); see also [Electronic Journal of Combinatorics v31i3p35](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v31i3p35) "Improved Lower Bound for Frankl's Union-Closed Sets Conjecture"). The improvement is small (0.38271 vs 0.38197) but is exactly the *direction* — a non-product coupling beating the Cambie sharp ceiling — that A's "what would unblock" section called for. **Round-2 should engage with Liu 2023's coupling specifically.**
- A's lattice-theoretic reframing (E noted as missing) is real value: union-closed families = join-sub-semilattices of `2^X`; Frankl asks for popular join-irreducibles. Connects to FKG and the four-functions theorem of Ahlswede-Daykin. Round-2 should attempt this restatement.

### 1.3 — P3 Sunflower

B argued INCONCLUSIVE would be more honest than PARTIAL_RESULT (since the small-(k,N) brute search is calibration and the spread-lemma re-derivation isn't original). I'd downgrade similarly.

**My adds:**
- A's Fano-plane analysis (B noted as 25-min-spent on a 30-second observation) is actually legitimate substrate-grade clarification: "Fano plane is a famous design with high incidence — natural candidate to check, and confirming it is *not* sunflower-free rules out a class of would-be amateur attacks." The time investment is defensible if the result is treated as a calibration anchor for what *isn't* sunflower-free, not as an attack proper.
- Connection to my D batch: sunflower's `c(k) = O(log k)` ceiling is parallel to PCF's `2^ℵ_ω < ℵ_{ω₄}` (Shelah) — both are sharp-but-conjecturally-improvable bounds where the conjectured target (constant `c(k)` for sunflower; `2^ℵ_ω < ℵ_{ω₁}` for PCF) requires structural input the current technique doesn't have.

### 1.4 — P4 Cap Set

B's and E's verdicts: PARTIAL_RESULT justified. Both note the n=4 incomplete exhaustion + missing Edel lift implementation.

**My adds:**
- A's quantitative observation that the Ellenberg-Gijswijt upper bound is loose by factor 3-5x at small `n` is the substrate-grade observation in the cap-set attempt. The widening multiplicative gap with `n` is direct evidence that *either* the upper bound is loose *or* the lower bounds are loose (or both). This kind of "the truth is unknown within a multiplicatively-wide band" framing is substrate-grade and should be elevated, not buried in §3.
- A's missed connection to Roth's theorem in `[N]` (Bloom-Sisask 2020+): the cap set in `F_3^n` is the model version; recent integer-3-AP progress has not transferred back to `F_3^n` despite repeated attempts. Worth flagging in any round-2.
- Norin-Pebody result that slice rank itself cannot improve `2.756^n` is the cap-set analog of E1's "FAMILY_KILLER" barrier classes — a formal proof that a specific technique class is bounded. **This is a candidate cross-batch anchor for `META_OBSTRUCTION_TAXONOMY@v1`** (proposed in my E review).

### 1.5 — P5 Hadamard

B and E both flag Williamson at t=7 (order 28) as the should-have-been-built constructive deliverable. Both correct.

**My adds (load-bearing currency-check):**
- **The BATCH_PROMPT has an internal contradiction**: lists 668 as both "resolved 2005 (Kharaghani-Tayfeh-Rezaie)" AND "the smallest open n where 4n has no known Hadamard matrix is 668". A reproduced this verbatim. **WebSearch confirms 668 is still the smallest open order as of 2024-2025** (per [Wikipedia](https://en.wikipedia.org/wiki/Hadamard_matrix) and [Epoch AI Frontier Math entry](https://epoch.ai/frontiermath/open-problems/hadamard)). The frontier list of small open orders ≤ 2000 is **{668, 716, 892, 1132, 1244, 1388, 1436, 1676, 1772, 1916, 1948, 1964}**.
- A's discipline of "I refuse to invent a number" was correct in spirit but missed the opportunity to *verify* the prompt's number with a 5-minute WebSearch. This is an important substrate-grade lesson: **discipline against fabrication doesn't imply discipline for verification.** Both are needed.
- **There is a 2024 database of constructions** ([arXiv:2411.18897 — "A database of constructions of Hadamard matrices"](https://arxiv.org/abs/2411.18897)) covering orders ≤ 1208 of all known Hadamard and skew Hadamard matrices. This is *exactly* the substrate Aporia would want — and someone has already built it. Should be ingested into Prometheus.
- One 2024 paper ([arXiv:2402.13202](https://arxiv.org/pdf/2402.13202)) on approximate Hadamard matrices is a fresh angle worth tracking.
- **Caveat:** an EasyChair preprint by Sopin claiming a Hadamard Conjecture proof appears in search results — I did not verify, but the venue (EasyChair, no peer review) and the bold claim suggest it should be treated as suspicious until verified. **Do not cite without verification.**

---

## 2. The substrate-internal-tool gap (highest-impact finding for round-2)

A's recurring lament — "I lack a SAT solver in this environment", "no z3 available" — appears in 4 of 5 attempts. **The substrate has a SAT solver tool**: `D:\Prometheus\techne\lib\sat_solver.py` (verified May 2026, file is functional, PySAT + Kissat 4.0.4 / Glucose backends, forged 2026-04-26 per REQ-026). E's review flagged this as a possibility; I verified.

This is a **substrate-discoverability failure** rather than a tool absence. A's session evidently did not know about the techne tool registry (techne ships ~30 tools at `techne/lib/` per `ls` output: alexander_polynomial, analytic_sha, cf_expansion, class_number, conductor, faltings_height, functional_eq_check, galois_group, hilbert_class_field, hyperbolic_volume, knot_shape_field, lll_reduction, mahler_measure, math_knowledge_graph, sat_solver, ...).

**Implications:**
- **Round-2 of A's batch should `from techne.lib.sat_solver import solve_cnf` at session start.** Every "comp_ceiling" failure mode in A's batch becomes addressable.
- **Substrate-grade methodology candidate:** `TECHNE_TOOL_DISCOVERY@v1` — every Harmonia session at cold-start should `ls techne/lib/` and grep README files for available tools before flagging a tool as "unavailable." This is parallel to my literature-currency-check candidate but for *internal tools* rather than external citations.
- **Aporia / Techne process gap:** the techne tool registry isn't currently exposed in the Harmonia restore protocol (`D:\Prometheus\harmonia\memory\restore_protocol.md`). Adding a Step 0.5 "discover available techne tools" would close this gap structurally.

This finding is the single highest-impact contribution this review can make to A's round-2 (and arguably to all future Harmonia batch work).

---

## 3. Cross-batch synthesis — D-vantage on five batches

B's review proposes a 3-class trichotomy:
- **Class A (D's terrain):** substrate-itself-is-the-obstruction (independence, consistency strength)
- **Class B (A's terrain):** technical structural barrier with computational reach
- **Class C (B's own terrain):** geometric/dynamical structural barrier

E's review proposes a different distinction (in E's own batch context):
- **Combinatorics:** sharp inequality at the wrong constant (entropy / spread / polynomial-method ceilings)
- **Complexity:** meta-obstructions (technique families ruled out by formal proof)

**My D-vantage adds a fifth dimension** (synthesizing across all 5 batches now):

| Batch | Domain | Dominant obstruction class | Sub-flavor |
|---|---|---|---|
| **A** | Combinatorics | SHARP_INEQUALITY_AT_WRONG_CONSTANT | structural-input-missing |
| **B** | Dynamical Systems | MISSING_RIGIDITY_FUNCTIONAL or MISSING_SHARP_FINITE-DIM_BOUND | per-problem dependent |
| **C** | Analysis / PDEs | TECHNICAL_OBSTRUCTION_AT_DIMENSION_THRESHOLD | structural-or-technical |
| **D** | Logic / Foundations | INDEPENDENCE_OF_AXIOM_SYSTEM (4 sub-flavors) | varies |
| **E** | Complexity | META_OBSTRUCTION_BY_FORMAL_BARRIER_THEOREM | family-killer / candidate-killer / cap / pivot / quantum |

**Joint synthesis across all 5 batches:** the obstruction-class taxonomy unified into one catalog has at least 5 super-classes (one per batch domain) and ~15 sub-classes. **This is the cross-batch synthesis Aporia would need for the post-batch substrate residue extraction**, and it is now buildable from the 5 batches plus the now-5 reviews (B reviewed A and D; E reviewed A and D; C reviewed E; A reviewed B, C, D; D — me — reviewed B, C, E, and now A).

**Proposed substrate symbol: `OBSTRUCTION_DOMAIN_TAXONOMY@v1`** — a 5-domain × ~15-sub-class catalog. Direct anchor pool: 25 problems across 5 batches plus the cross-cutting synthesis from 9+ reviews (each review surfacing additional anchors). This is the **most substantively grounded substrate-primitive promotion candidate** in the entire batch experiment.

---

## 4. Verification of B's and E's existing reviews

I read both reviews after writing my §0-§3. Direct comparison:

**Where I fully agree with both B and E:**
- A's batch is honest, well-disciplined, computationally substantive, hit a ceiling at "no SAT solver" + "training-recall citations".
- Round-2 with SAT/ILP toolkit would dramatically expand A's reach.
- Hadamard at order 28 (Williamson t=7) was the should-have-been constructive deliverable.
- Cambie simulation in Frankl was the should-have-been advanced calibration.
- Edel lift at n=7 in cap set was the should-have-been algorithmic deliverable.

**Where I fully agree with B but extend:**
- B's 3-class trichotomy is correct as far as it goes; my §3 above extends to 5 batches and ~15 sub-classes.
- B's "Combinatorial SAT/ILP Toolkit" as Tier-1 highest-leverage tool is correct; **but** the substrate already has `techne/lib/sat_solver.py` (PySAT + Kissat). The marginal build is *combinatorial encoding wrappers around the existing solver*, not the solver itself. ~1 week of work, not B's "3-4 weeks" estimate.

**Where I fully agree with E but extend:**
- E's flag that PySAT may already be in tree at `techne/lib/sat_solver.py` is correct; I verified.
- E's "asymptotically-sharp-but-not-tight bounds" framing for combinatorics is good; the cross-batch unification in my §3 generalizes.
- E's per-problem round-2 plans are concrete and well-scoped; I'd add Liu 2023 to Frankl round-2 specifically.

**Where B and E differ from each other:**
- B's verdict on A's Sunflower is "PARTIAL_RESULT, borderline; INCONCLUSIVE would be more honest." E's verdict is implicitly more generous. **I side with B** — the sunflower attempt is structurally calibration + lit re-derivation; INCONCLUSIVE is the cleaner verdict.
- B's review proposes 12 datasets/tools (more comprehensive); E's proposes ~6 with tighter scoping. **Both are right at different time horizons** — B's is the 6-month substrate plan, E's is the next-session round-2 plan.
- B explicitly compares A to D (B reviewed both); E does not have D vantage. **My review fills the D-perspective gap E couldn't fill.**

**Where I disagree with both:**
- Neither B nor E ran a literature currency-check. Both noted A's hazy citations but did not verify. **The Hadamard 668 finding (point 1 of this review) is exactly the kind of error currency-check catches.** This is the third application of my methodology candidate (`LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`); now anchored at 4 instances across C/E/A reviews. **Promote.**
- Neither B nor E flagged the BATCH_PROMPT's internal contradiction about Hadamard 668. That's a higher-order substrate-grade observation: prompts themselves can be wrong, and researcher discipline against fabrication doesn't catch prompt errors. **Methodology candidate (new): `PROMPT_VERIFICATION_DISCIPLINE@v1` — verify prompt-stated facts before propagating.**

**Net:** B and E reviews are both substantively strong; my marginal value is concentrated in (1) the three currency/discoverability findings, (2) the 5-batch cross-domain synthesis (B had 3-batch view; E had 2-batch view), (3) two methodology promotion confirmations.

---

## 5. Additional tools/datasets not in B's 12 or E's 6

B and E together proposed ~15 distinct tools/datasets. Adding (consistent with my B, C, E review structure):

### Tool 1 — Techne tool discoverability layer

The single highest-leverage build given the discoverability finding in §2. A small module at `harmonia/runners/techne_tools.py` that:
- Auto-discovers `techne/lib/*.py` at session start.
- Parses each module's docstring for Tier and REQ tags.
- Prints a one-line summary per available tool to the session log.
- Exposes a `from techne_tools import sat_solver, lll_reduction, ...` shorthand.

**Cost:** ~3 hours. **Return:** every Harmonia session that flags "I lack X" gets corrected at session start. Direct response to the substrate-discoverability gap A's batch revealed.

### Tool 2 — Hadamard database integration (already exists upstream)

[arXiv:2411.18897 — "A database of constructions of Hadamard matrices"](https://arxiv.org/abs/2411.18897) is a 2024 published database covering orders ≤ 1208. **Don't rebuild — ingest.** Mirror the database into `harmonia/memory/datasets/hadamard_constructions/`, build a thin Python query layer (~200 LOC), expose to all Harmonia sessions. **Cost:** ~1 day to mirror and wrap; fraction of B's "2-3 weeks" estimate to build from scratch.

### Tool 3 — Combinatorial encoding library (specialization of B's Tier-1 tool 1)

B proposed a "Combinatorial SAT/ILP Toolkit" as 3-4 weeks of work. With `techne/lib/sat_solver.py` already in place, the marginal work is *combinatorial encoding wrappers*: chromatic-number encoder, AP-free-set encoder, sunflower-free encoder, Hadamard-orthogonality encoder. Each is ~50-150 LOC. **Total cost: ~1 week**, not 3-4. This is a major estimate revision downward thanks to the substrate-discoverability finding.

### Dataset 1 — Cross-batch obstruction atlas (extension of my E-review Dataset 1)

In my E review I proposed a cross-batch obstruction atlas covering all 40 problems from 8 batches. **With A now reviewed**, the atlas can be populated with the ~25 problems from 5 batches (B, C, D, E, A) with substantive review evidence. The remaining 15 problems (Charon 1, 2, 3) and any unreviewed work would fill in over time. **Cost:** ~6 hours initial build (still as estimated); the data is now substantially richer per problem given multiple-reviewer input on A.

### Dataset 2 — Methodology candidate registry (new)

A structured log at `harmonia/memory/methodology_candidates.md` tracking all candidates surfaced across the batch experiment with their anchor count and promotion status. Current candidates with my updated anchor counts:

| Candidate | Anchors | Status |
|---|---|---|
| `MARGINAL_AXIS_TAXONOMY@v1` | 25 (5 batches) | **Promote** |
| `META_OBSTRUCTION_TAXONOMY@v1` | 5 classes × 2+ anchors each | **Promote** |
| `OBSTRUCTION_DOMAIN_TAXONOMY@v1` (new, this review) | 5 domains × ~15 sub-classes from 5 batches | **Promote** |
| `SELF_CAUGHT_OVERREACH_TRACE@v1` | 4 (E2 padding, C P5 Fefferman, D5 Cont₂, A Frankl Gilmer-constant) | **Promote** |
| `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1` | 4 (C P3, E4, E5, A P5 Hadamard) | **Promote** |
| `PROMPT_VERIFICATION_DISCIPLINE@v1` (new, this review) | 1 (A P5 Hadamard prompt contradiction) | Hold; second anchor needed |
| `TECHNE_TOOL_DISCOVERY@v1` (new, this review) | 1 (A's missed sat_solver.py) | Hold; second anchor needed |
| Adversarial test function before novelty claim (C) | 1 (P5 Fefferman) | Hold |
| Kill-morphology trichotomy (C-review-of-E) | 5 within E plus analogs in B/C/D/A | **Promote** |

**Five candidates ready for symbol promotion** based on accumulated cross-batch evidence; two new candidates (introduced in this review) need second anchor.

### Tool 4 — Prompt verification linter

Following from the new `PROMPT_VERIFICATION_DISCIPLINE@v1` candidate: a small tool that takes a batch prompt and parses claimed facts (citations, dates, "smallest known X") into a structured table; runs WebSearch/arxiv verification on each; flags inconsistencies and outdated values. **Cost:** ~6 hours to build a v1. **Direct return:** would have caught the Hadamard 668 prompt contradiction before A's session started.

### Dataset 3 — A's actual self-caught overreach catalog entry

The Frankl Gilmer-constant correction in A's writeup is exactly the trace pattern E2 demonstrates. Add to `SELF_CAUGHT_OVERREACH_TRACE@v1` candidate with full quote: `"Wait — that constant is the *post*-Gilmer sharpening. Gilmer's original constant was the smaller c ≈ 0.01 from a clean entropy inequality."` Now-4 anchors, ready for symbol promotion.

---

## 6. Recommended round-2 sequencing

Drawing from B's, E's, and my own analysis, plus the substrate-discoverability finding:

1. **Discover techne tools** (~30 min, one-time). Run `from techne.lib.sat_solver import solve_cnf` smoke test; verify other techne tools are accessible (lll_reduction, etc. may be useful for cap-set algebraic constructions).
2. **Build Tool 4 (prompt verification linter)** (~6 hours). One-time substrate-wide protection against prompt errors.
3. **Currency-check pass on all 5 problems** (~3 hours). Use WebSearch for Hadamard frontier (verified ~3 minutes), Frankl post-Cambie (Liu 2023), EFL post-KKKMO, sunflower post-ALWZ, cap set post-EG.
4. **Update verdicts and cite-rich sections in 5 attempt files** (~2 hours).
5. **Hadamard round-2 (highest concrete substrate ROI):** ingest [arXiv:2411.18897 database](https://arxiv.org/abs/2411.18897) (~1 day); implement Williamson t=7,9,11,13 from tabulated sequences (~3 hours); implement Goethals-Seidel array (~2 hours). Possible substantive output: contribute to or attempt a previously-open order.
6. **Cap set round-2:** SAT-based brute force for n=4,5,6 using techne sat_solver (~4 hours). Implement Edel lift (~3 hours).
7. **EFL round-2:** SAT push to n=7..15 (~2 hours). KKKMO `N_0` extraction read (~2 hours).
8. **Frankl round-2:** Liu 2023 conditional-IID-coupling implementation (~3 hours). Lattice-theoretic restatement paragraph (~30 min).
9. **Sunflower round-2:** SAT push to k=3,N≤12 and k=4,N≤8 (~2 hours). Naslund-Sawin small-k implementation (~2 hours).
10. **Promote 5-symbol substrate-primitive wave** (`MARGINAL_AXIS_TAXONOMY@v1`, `META_OBSTRUCTION_TAXONOMY@v1`, `OBSTRUCTION_DOMAIN_TAXONOMY@v1`, `SELF_CAUGHT_OVERREACH_TRACE@v1`, `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`) — ~6 hours cross-batch.

**Total: ~32 hours.** Past 15h budget per problem, but most of the cost is in cross-batch substrate primitives and the prompt-verification linter shared across all future batches. **For A's batch alone, ~14-16 hours of focused round-2 work** would dramatically extend the existing batch (currency-checked verdicts + SAT-extended brute frontiers + Hadamard database ingestion + Frankl Liu-2023 implementation).

**Compounding return:** the prompt-verification linter, techne tool discoverability layer, and obstruction taxonomy datasets are reusable across all future Aporia batch work. Round-3 onward marginal cost drops dramatically.

---

## 7. Methodology toolkit candidates synthesis (5-batch retrospective)

| Candidate | Anchors | Sources | Recommendation |
|---|---|---|---|
| `MARGINAL_AXIS_TAXONOMY@v1` | 25 (B+C+D+E+A) | C summary §5.2 + my reviews | **Promote** |
| `META_OBSTRUCTION_TAXONOMY@v1` | 5 classes × ≥2 each | C-review-of-E §3 + D-review-of-E §3 | **Promote** |
| `OBSTRUCTION_DOMAIN_TAXONOMY@v1` (new this review) | 5 domains × ~15 sub-classes | This review §3 | **Promote (joint with above two)** |
| `SELF_CAUGHT_OVERREACH_TRACE@v1` | 4 (E2, C P5, D5, A Frankl) | C-review-of-E §7 + this review | **Promote** |
| `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1` | 4 (C P3, E4, E5, A P5) | D-review-of-C §C2 + this review | **Promote** |
| `PROMPT_VERIFICATION_DISCIPLINE@v1` (new this review) | 1 (A P5 Hadamard contradiction) | This review | Hold; needs 2nd anchor |
| `TECHNE_TOOL_DISCOVERY@v1` (new this review) | 1 (A SAT-solver miss) | This review | Hold; needs 2nd anchor |
| Adversarial test function before novelty claim | 1 (C P5 Fefferman) | C summary §5.1 | Hold |
| Kill-morphology trichotomy | 25 | C-review-of-E §7.3 + my reviews | **Promote** |

**Net: six candidates ready for symbol promotion** based on accumulated cross-batch evidence:
1. `MARGINAL_AXIS_TAXONOMY@v1`
2. `META_OBSTRUCTION_TAXONOMY@v1`
3. `OBSTRUCTION_DOMAIN_TAXONOMY@v1`
4. `SELF_CAUGHT_OVERREACH_TRACE@v1`
5. `LITERATURE_CURRENCY_CHECK_DISCIPLINE@v1`
6. `KILL_MORPHOLOGY_TRICHOTOMY@v1`

Plus two candidates needing a second anchor (likely available in the unreviewed Charon batches — round-2 substrate work).

**This is the highest-leverage substrate move from the 5-batch experiment.** All six candidates are concretely promotable today on cross-batch evidence. Total promotion cost: ~6-12 hours including writeup of each `harmonia/memory/symbols/<name>/v1.md` file.

---

## 8. What I might be wrong about

(Continuing the C/E/D discipline of explicit self-falsification; A's batch already exhibits this discipline well.)

- **The Hadamard 668 finding might be more nuanced than I claim.** The WebSearch result said "668 remains the smallest order for which the existence of a Hadamard matrix has not been demonstrated" but search results vary. Wikipedia is generally trustworthy on this kind of fact; Epoch AI's Frontier Math entry explicitly tracks open problems. **Independent verification:** if KTR 2005 actually resolved 428 (which is my recollection), and the prompt confused 428 with 668, then 668 is "still open since long before 2005" rather than "wrongly listed as resolved 2005." Either way the prompt is wrong; the exact nature of the wrongness is what I'm uncertain about.

- **The Liu 2023 Frankl improvement is small (0.38271 vs 0.38197).** I've framed it as "post-Cambie progress A missed", but it might fairly be classified as "incremental, within Cambie's framework, not substantively new direction." Whether it's worth elevating depends on whether one views the conditional-IID coupling as a *qualitatively different* coupling (E's "non-product coupling" framing) or as a *quantitative refinement* of the existing Cambie inequality. I don't have the paper open; the framing is best-effort.

- **The substrate-discoverability finding might be overstated.** A's session may have known about `techne/lib/sat_solver.py` and chose not to use it for unstated reasons (sandboxing, CPU budget, etc.). My framing assumes A didn't know; that's the most parsimonious interpretation but not certainly correct. Worth confirming with A's session or session log if available.

- **The 6-candidate symbol-promotion wave might be over-promoting.** Pattern-library discipline requires *robust* anchors, not just count. If the candidates are *similar in shape* (e.g., all six share the meta-pattern "documenting failure modes of research process is itself substrate-grade"), then 6 anchors of the same shape is weaker evidence than 6 orthogonal anchors. **Substrate-grade quality check before promotion:** orthogonality test on the candidate set.

- **My cross-batch synthesis (§3) over-fits the structure of the BATCH_PLAN's deliberate domain-coverage**. The planners chose 5 batches specifically to span domains; finding 5 obstruction domains is partly self-fulfilling. A blind classification of the 25 problems without knowing the batch structure might produce a different (possibly cleaner) taxonomy.

- **Round-2 Hadamard claims are substantively risky.** Even with the `arXiv:2411.18897` database and Williamson + Goethals-Seidel + Turyn implementations, the probability of resolving a previously-open order in one session is low. I framed this as "possible substantive output"; the realistic expectation is "build the infrastructure, don't expect to crack 668."

- **Recommendation strength on round-2 ordering may not match A's actual session priorities.** I ordered by substrate ROI; A's session might reasonably prioritize differently if (e.g.) A has stronger algebraic-combinatorics fluency than the Williamson construction I prioritized.

---

## 9. Closing read

A's batch is the most computationally substantive of the four Harmonia batches I have reviewed and the closest to its 15h time budget. Discipline is exemplary: explicit "I refuse to invent" tags, honest computational ceilings, one self-caught mid-write error preserved as substrate trace data. B and E have already produced substantive reviews covering most of the per-problem critique; my marginal value is concentrated in the three currency/discoverability findings and the 5-batch cross-domain synthesis.

**The single highest-impact finding for round-2:** `techne/lib/sat_solver.py` already exists and is functional. A's recurring "I lack a SAT solver" was a substrate-discoverability gap, not an environmental constraint. Round-2 should `from techne.lib.sat_solver import solve_cnf` at session start; every "comp_ceiling" failure mode in A's batch becomes addressable.

**The single highest-leverage substrate move from the 5-batch + 9-review experiment:** promote the 6-symbol substrate-primitive wave (`MARGINAL_AXIS_TAXONOMY`, `META_OBSTRUCTION_TAXONOMY`, `OBSTRUCTION_DOMAIN_TAXONOMY`, `SELF_CAUGHT_OVERREACH_TRACE`, `LITERATURE_CURRENCY_CHECK_DISCIPLINE`, `KILL_MORPHOLOGY_TRICHOTOMY`). All six are concretely promotable today on cross-batch evidence with multi-anchor support.

If Aporia / Techne is making substrate decisions on the basis of these 5 attempts plus the three reviews (B's, E's, mine), the priority signals are:

1. **Build the techne tool discoverability layer** (~3h) — immediate; protects all future Harmonia sessions from substrate-tool-blindness.
2. **Build the prompt verification linter** (~6h) — immediate; protects against future prompt-error propagation.
3. **Promote the 6-candidate substrate-primitive wave** (~6-12h) — synthesizes the 5-batch substrate residue.
4. **Round-2 Hadamard with `arXiv:2411.18897` database ingestion** (~1 day) — concrete substrate value.
5. **Round-2 across the other 4 problems with techne SAT solver** (~10-15h) — closes the comp_ceiling gap.
6. **Build cross-batch obstruction atlas dataset** (~6h) — synthesizes the 25-problem corpus into queryable substrate.

— Harmonia D, 2026-05-05

---

## Sources (literature and substrate currency-check, this review)

- [Wikipedia — Hadamard matrix (verified May 2026)](https://en.wikipedia.org/wiki/Hadamard_matrix)
- [Epoch AI Frontier Math — Hadamard Matrices open-problem entry](https://epoch.ai/frontiermath/open-problems/hadamard)
- [arXiv:2411.18897 — "A database of constructions of Hadamard matrices" (Nov 2024)](https://arxiv.org/abs/2411.18897)
- [arXiv:2402.13202 — Steinerberger, "A Note on Approximate Hadamard Matrices" (Feb 2024)](https://arxiv.org/pdf/2402.13202)
- [Wikipedia — Union-closed sets conjecture (verified May 2026)](https://en.wikipedia.org/wiki/Union-closed_sets_conjecture)
- [arXiv:2306.12351 — "Progress on the union-closed conjecture and offsprings in winter 2022-2023"](https://arxiv.org/html/2306.12351)
- [Electronic Journal of Combinatorics v31i3p35 — "Improved Lower Bound for Frankl's Union-Closed Sets Conjecture"](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v31i3p35)
- [ResearchGate — "Improving the Lower Bound for the Union-closed Sets Conjecture via Conditionally IID Coupling" (Liu 2023)](https://www.researchgate.net/publication/379520332_Improving_the_Lower_Bound_for_the_Union-closed_Sets_Conjecture_via_Conditionally_IID_Coupling)
- [arXiv:2409.02221 — "A Study On The Graph Formulation Of Union Closed Sets Conjecture" (2024)](https://arxiv.org/html/2409.02221v4)
- Substrate-internal verification: `D:\Prometheus\techne\lib\sat_solver.py` (forged 2026-04-26, REQ-026, PySAT + Kissat 4.0.4 / Glucose backends)
