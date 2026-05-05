# Review of Harmonia A — Combinatorics Batch

**Reviewer:** Harmonia B
**Date:** 2026-05-05
**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_01_erdos_faber_lovasz.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_02_frankl_union_closed.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_03_sunflower.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_04_cap_set.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_05_hadamard_matrix.md`
- 5 Python attack scripts at `attempts/_scratch/{efl,frankl,sunflower,capset,hadamard}_attack.py` (571 LOC total)

**Frame:** parallel to my earlier review of Harmonia D (`harmonia_B_review_of_harmonia_D.md`). Same questions: critique, additional research per problem, round-2 candidates, additional solution angles, datasets/tools to build.

---

## Part 1 — Overall critique

### What Harmonia A did well

1. **Real computational artifacts.** Unlike Harmonia D's batch (zero numerical output), A produced 571 lines of Python across 5 attack scripts and meaningful tables of results in each writeup. EFL chromatic numbers verified up to n=6, cap-set bound table at n≤7, sunflower-free family enumeration up to N=8, Sylvester + Paley-I Hadamard constructions verified up to order 84, Frankl empirical worst-case ratios for n≤6 — all of these are *real* substrate-grade numerical kill data.

2. **Sharp identification of structural bottlenecks.**
   - **EFL:** the KKKMO 2021 implicit `N_0` is the explicit gap — and A correctly diagnoses that even after extraction, `N_0` is computationally inaccessible, so closure requires a different argument.
   - **Frankl:** entropy method saturates at `(3-√5)/2 ≈ 0.382`, a factor of `~1.6` short of `0.5`. A re-derives WHY: the auxiliary equation `2p − p² = 1 − p` has root `p = (3-√5)/2`. Concrete, correct, useful.
   - **Sunflower:** spread-lemma optimum at `p ~ log k / k` gives `(C log k)^k`. Pushing `p` smaller worsens it; pushing larger fails the spread bound. The barrier is structural in the current method.
   - **Cap set:** polynomial-method ceiling `2.756^n` is provably tight for the slice-rank technique (Norin/Pebody-style results). A computes the multiplicative gap to known LBs — factor ~3 at n=4, ~5 at n=7 — surfacing that the truth could plausibly sit anywhere in between.
   - **Hadamard:** A enumerates the 27 orders in `[4, 200]` not produced by Sylvester ∪ Paley-I, exhibiting concretely WHERE the toolkit gap lives.

3. **Outstanding computational-honesty discipline.** A repeatedly says "I lack a SAT solver in this environment", "search timed out at 12, honest: 12 is a *lower bound* witnessed by my best-found family, not a proven maximum", "**Honest: I did not produce a Hadamard matrix of order 28 in this session**", "I refuse to invent a number." This is exemplary application of the "no fake partial results" rule. Among all batches I've reviewed, A's discipline on this is the strongest.

4. **"What would unblock" sections are concrete and actionable.** Each problem names a specific lemma, method extension, or structural input that would close the gap. Frankl: "non-product coupling that exploits union-closure as equality constraint." Sunflower: "multi-scale spread lemma allowing non-uniform `p`." Cap set: "non-polynomial-method upper bound or fundamentally new construction." These are good targets, not vague invocations.

5. **Calibrated negatives are precise.** "Random sampling is hopeless: extremal families are highly structured" (Frankl). "DSATUR is loose by 1 at n=5" (EFL). "The Fano plane is *not* sunflower-free" (Sunflower; nice negative result). These rule out specific candidate attacks that a future researcher might otherwise rediscover.

### What Harmonia A did less well

1. **Computational work used naive primitives where modern tools were available.** A's recurring lament — "I lack a SAT solver in this environment" — is partly correct (z3 may not be installed) but:
   - **Python `PuLP` and `OR-tools` are both pip-installable and were available** for ILP. A didn't attempt installation or fallback.
   - **CBC, GLPK** are open-source ILP solvers usable from Python without z3.
   - **`networkx` itself has** experimental SAT-like reductions for chromatic-number that A didn't try.
   - The recurring effect: brute backtracking timed out at n=7 (EFL), N=8 (sunflower), n=4 (cap set, didn't exhaust). With proper ILP encoding all three would have pushed to substantially higher frontiers in the same wall-clock time.

   This is a real ceiling, not a fabrication, but it's a self-imposed one. A 30-minute pip-install + encoding effort would have made attacks 3-5x deeper.

2. **Edel-lift attempt (Cap set Attack 4) and Cambie simulation (Frankl Attack 4) were both abandoned mid-flight**. Honest abandonment per discipline rule, but represents budget-spent-without-payoff. The Edel lift specifically is well within reach — A had already confirmed all the prerequisites (n=6 max-cap of 112 is a known reference value). A focused 30-minute push could have yielded a real 200+ cap at n=7.

3. **No engagement with modern computational tools that exist in 2026**:
   - **Polymath 19's GitHub repo** has experimental cap-set data; not pulled.
   - **Sloane's Hadamard Matrix Catalog** is mentioned and even cited in the prompt; not fetched.
   - **Lean / mathlib** has substantial combinatorics formalizations; cap-set bound has likely been formalized at least partially. Not engaged.
   - **PARI/GP, Sage, GAP** (esp. GAP for Hadamard / design-theory work) are standard for this domain. Not used.
   - **arxiv post-2022 sweeps** for follow-ups to KKKMO, Gilmer, ALWZ, Ellenberg-Gijswijt absent. Each of these papers kicked off a wave that A's citation pool stops short of.

4. **Citation pool is dated, especially for the Frankl wave.** Gilmer 2022 + the Chase-Lovett/Sawin/Cambie sharpenings are cited; everything after 2023 is under-engaged. The Frankl frontier has continued to move — there are post-Cambie refinements that A's pool misses.

5. **Hadamard frontier explicitly NOT refreshed.** A says "I have not refreshed this. Per the batch prompt, the frontier shifts; I refuse to invent a number." This is correct discipline — but a 5-minute arxiv search would have produced a current value. The "refuse to invent" tag is being used where "didn't take 5 minutes" would be more honest.

6. **No cross-problem synthesis.** A's 5 problems share major mathematical themes:
   - **Entropy methods**: Frankl + cap set + sunflower partial. The same `(3-√5)/2`-style barriers appear.
   - **Spread / nibble methods**: EFL (Kahn 1992 used probabilistic; KKKMO extended) + sunflower (ALWZ).
   - **Structured-vs-random divide**: cap set + EFL + sunflower + Hadamard all show "random-search is hopeless; algebraic constructions dominate."
   - **Polynomial-method-vs-not divide**: cap set proven by polynomial method; sunflower partially; EFL not.

   A treats them as silos. **No summary file across the 5 was produced** (whereas Harmonia B has `harmonia_B_summary.md` doing the synthesis explicitly). Same complaint as my D-review.

7. **Frankl Attack 3 ("doubling injection")**: A re-derives the well-known fact that `S → S ∪ {x}` fails outside restricted families. The re-derivation is correct but the time-budget would have been better spent on Attack 4 (Cambie simulation) which got cut off.

8. **Sunflower Attack 3 (Fano plane check)**: A spends 25 minutes verifying that the Fano plane contains 3-sunflowers. This is a 30-second observation (any 3 lines through a common point form a 3-sunflower with that point as core) and the wrong direction anyway — Fano plane is a well-known design with high incidence, NOT a candidate sunflower-free family. Time poorly allocated.

### Verdict-quality calibration

| Problem | A's verdict | My read |
|---|---|---|
| 01 EFL | PARTIAL_RESULT | Justified — small-n verification + lit synthesis. |
| 02 Frankl | INCONCLUSIVE | Justified — entropy-ceiling diagnosis is real but no original advance. |
| 03 Sunflower | PARTIAL_RESULT | Borderline — small-(k,N) brute search is calibration; spread-lemma re-derivation isn't original. **INCONCLUSIVE would be more honest.** |
| 04 Cap set | PARTIAL_RESULT | Justified — n=4 witness + greedy benchmarks + UB-vs-LB ratio are real. |
| 05 Hadamard | PARTIAL_RESULT | Justified — Sylvester + Paley-I + 27-order coverage gap is concrete. |

A's verdicts are slightly more generous than D's. The Sunflower verdict is the one I'd downgrade. Cap set is borderline because the n=4 brute force didn't formally exhaust the space — but the witness for size 20 + the gap calculation are real partial results, so PARTIAL is defensible.

### Comparison to Harmonia D's batch

A's batch is **substantively stronger than D's** along these axes:
- **Computational engagement**: 571 LOC of real Python vs D's 0 LOC. A's diagnosis of bottlenecks is anchored in numerical data; D's is anchored in literature recall.
- **Surface area**: A produced 4-5 attacks per problem with at least one numerical attack each. D's later attacks (4-6 in most files) are bookkeeping confirmations.
- **Concreteness of "what would unblock"**: A names specific technical objects (non-product couplings, multi-scale spread lemmas, Edel lifts). D names programs (Sargsyan-Trang, core-model-for-supercompacts).

D's batch is **substantively stronger than A's** along these axes:
- **Difficulty class diagnosis**: D correctly identifies that all 5 of its problems are independence-flavored (substrate-itself-is-the-obstruction). A's 5 are *non-independence* but A doesn't quite frame the contrast.
- **Citation rigor**: D's paraphrase tags are more conservative; A occasionally cites without flag.

The two batches are **complementary**, not parallel. A's combinatorics problems are ones where progress is made via construction + computation + technical advance; D's logic problems are ones where progress is gated on consistency-strength reductions + new foundational moves. Aporia post-batch synthesis should treat the contrast as a substrate-grade observation: **the kill-morphology depends on the difficulty class, not just the problem domain.**

---

## Part 2 — Per-problem additional research

### Problem 1 (EFL) — additional angles

1. **SAT/ILP encoding of EFL coloring**, pushing brute verification to n=12-15+ (modern SAT solvers handle 28×56-edge graphs in seconds where naive backtracking times out). Use PuLP+CBC if z3 unavailable. Direct deliverable: a verified table of `χ(G_n) = n` for the maximum-overlap EFL graph at n ≤ 15. Possibly higher with symmetry breaking (vertex-orbit canonical-form constraints).

2. **Audit KKKMO 2021 for explicit `N_0`.** A correctly notes this is a paper-reading effort, not a search effort. Even an explicit absurd-large `N_0` (e.g. `2^{2^{40}}`) is substrate-grade information that the field doesn't currently have written down anywhere. The deliverable is a structured journal of the proof's tower-of-lemmas with each `N_i ≥ f(N_{i-1})` extracted.

3. **Lean formalization status of EFL/KKKMO.** Low prior of full formalization, but partial fragments may exist. Audit + propose minimal viable formalization target.

4. **Algebraic-attack-revival on small `n`.** Berge-style structural arguments on linear hypergraphs were largely abandoned post-Kahn 1992. Whether modern algebraic methods (e.g., flag algebras, semi-definite programming bounds à la Razborov) bear is partially explored; deeper push possible.

5. **Computational variants.** Edge-coloring of linear `n`-uniform hypergraphs is the equivalent formulation; SDP relaxations of the corresponding fractional matching polytope might give bounds tight at n vs n+o(n). This is concrete enough for round-2.

### Problem 2 (Frankl) — additional angles

1. **Non-product coupling experiments (numerical).** A's "what would unblock" calls for non-product couplings of `(A, B)` that exploit union-closure as an equality constraint. This is a *computational design* problem: try various couplings (random walks on the family lattice, biased samplers depending on `|A ∩ B|`, etc.) and compute the resulting frequency lower bound. Surface which coupling families improve over `(3-√5)/2` and by how much.

2. **Push computational verification beyond n=11.** Bošnjak-Marković hit n=11 in 2008 by exhaustive computation. With modern SAT/ILP, n=12-13 is plausibly accessible. Each extra `n` is small substrate-grade additional evidence.

3. **arxiv 2023-2026 sweep on Frankl.** The Gilmer-Chase-Lovett-Sawin-Cambie wave is 2022; what's happened since? Likely several incremental refinements I'd want to know about.

4. **Reimer / "smallest set" reduction implementation.** A re-derived this as Attack 3 partially. A focused implementation that automatically applies the small-set reduction to a family and reports either "Frankl follows from Reimer here" or "needs full conjecture" would be a useful substrate tool.

5. **Connection to the Plünnecke-Ruzsa inequality.** Plünnecke-Ruzsa controls sumset sizes; union-closed families have a related but different structure (`A ∪ B ∈ F`). Whether Plünnecke-style arguments transfer is essentially unstudied.

6. **Dual approach: "intersect-closed" Frankl.** The conjecture has a "dual" form for intersection-closed families. Whether the dual is easier (or equivalent) is sometimes useful as a vector for new techniques.

### Problem 3 (Sunflower) — additional angles

1. **SAT/ILP for `f(k, r)` at moderate `(k, r)`.** A's brute force timed out at N=7 with a 12-cap. ILP encoding should reach N=12-15 for `k=3, r=3` cleanly. The witnessed lower bounds become substrate-grade calibration data for testing constructions.

2. **Implement Naslund-Sawin polynomial-method bound on a 3-uniform restricted case.** A noted Naslund-Sawin only handle restricted ground-set structures; a numerical exploration of *which* restrictions yield improvement, at small `k`, would either suggest extensions or rule them out.

3. **Spread-lemma sharpness check.** A's Attack 2 derives the spread-lemma sharp at `p ~ log k / k`. A focused numerical check: build random `p`-spread families at various `p`, see how close `(C/p)^k` is to the actual count. Could surface looseness in the spread bound that the analytic derivation hides.

4. **Connection to the cap-set polynomial-method**. Sunflower and cap set both yielded to polynomial-method-style attacks (CLP, EG, ALWZ uses different machinery but the "find structure in dense families" theme is shared). Whether the slice-rank framework or the spread-decomposition framework can be unified is open territory.

5. **Steiner system + design-theory constructions.** A's Attack 3 dismissed Fano plane and trivial constructions but didn't try larger Steiner systems (S(2, 3, 7), S(2, 3, 9), etc.). A sweep across small designs checking sunflower-freeness might surface unexpected near-extremal candidates.

6. **arxiv 2022-2026 sweep on sunflower / spread methods.** ALWZ 2019, Rao 2020 simplification, and the various 2021-2022 incremental improvements; what's the post-2022 wave?

### Problem 4 (Cap set) — additional angles

1. **SAT/ILP brute force for n=5,6,7.** Known maxima at n=5,6 are 45, 112. ILP can reproduce these in seconds (witnessing the known Hill caps). At n=7 the known LB is 236 (Edel) and UB is `2.756^7 ≈ 1208`; a SAT-based upper bound (showing no 237-cap exists) is currently out of reach but a witness for 236 is straightforward.

2. **Implement Edel's lift from n=6 to n=7.** A acknowledged not budgeting for this; a focused round-2 should. Concrete deliverable: a 236-cap in `F_3^7` constructed end-to-end.

3. **Polynomial-method beyond slice rank.** Norin-Pebody and others showed slice rank cannot improve `2.756^n`. What's the post-2017 post-slice-rank state? Sub-rank, partition rank, geometric rank — multiple candidate generalizations exist; current bounds in this sub-area are paper-tracking.

4. **Lean formalization of Ellenberg-Gijswijt.** Likely partial; status check + completion plan.

5. **Connection to Roth's theorem in [N].** Behrend's construction in [N] gives `r_3([N]) ≥ N · exp(-c√log N)`; the `F_3^n` cap-set construction is a related but different quantity. Whether a tighter transfer between the two settings is possible is at the frontier.

6. **Polymath 19 data ingestion.** Polymath 19 had collaborative computational data; pulling that into substrate as a queryable resource is real value.

### Problem 5 (Hadamard) — additional angles

1. **Implement Williamson at t=7 (order 28).** A noted "Williamson sequences for t=7 are tabulated; closing this would be 30 minutes of careful coding I did not budget." Round-2 should do exactly this. Concrete deliverable: a verified Hadamard matrix of order 28.

2. **Implement Goethals-Seidel array.** This is the workhorse for modern computer search. Implementation + verification + run on a few specific orders.

3. **Sloane's Hadamard Matrix Catalog ingestion.** Pull the actual catalog (or its current online form) into substrate. Mirror locally; query programmatically.

4. **Refresh the smallest-open-`n` frontier.** A explicitly didn't do this. 5-minute task. Per a quick recall (paraphrase, may need verification): smallest open `n` was around 668 or 716 historically; specific values like `668 = 4 × 167` were resolved. Current 2026 frontier I do not know with confidence, but a focused arxiv/literature search would close it.

5. **Computational push at the smallest open order.** Whatever it is, run Williamson + Turyn + Goethals-Seidel searches at it. Even a few hours of substrate compute could plausibly resolve a previously-open order — this is among the most actionable open problems in this batch.

6. **Lean / Coq formalization of Sylvester + Paley constructions.** Low-priority but a clean substrate artifact.

7. **Hadamard-matrix-equivalence database.** Two orders are "equivalent" if related by row/column permutations and sign flips; the equivalence classes are a finite-but-unmapped set for many orders. Building this database for known orders ≤ 100 is concrete computational work.

---

## Part 3 — Round-2 candidates

**Strong round-2 candidates:**

- **Hadamard (Problem 5)** — *the* most actionable round-2 in the batch. A's first-pass implemented Sylvester + Paley-I; a round-2 implementing Williamson + Turyn + Goethals-Seidel + pulling Sloane's catalog would push to substantively new ground. Could plausibly resolve a previously-open order (low probability per single attempt, but the per-attempt expected value is real).

- **Cap set (Problem 4)** — SAT-based brute force for n≤7 + Edel-lift implementation is concrete, bounded, and produces calibration anchors. Lower probability of advancing the asymptotic but high probability of producing usable substrate calibration data.

- **EFL (Problem 1)** — SAT-based brute force pushing to n=15 + KKKMO `N_0` audit. Would close the small-`n` verification gap that A's brute backtracking couldn't reach.

**Weaker round-2 candidates:**

- **Frankl (Problem 2)** — the entropy-ceiling diagnosis is structural; rerunning with better tools would re-confirm rather than advance. The "non-product coupling" exploration is speculative — could yield insight but also could just reproduce `(3-√5)/2`.

- **Sunflower (Problem 3)** — similar to Frankl. Spread-lemma is structural. Round-2 with SAT pushes the brute frontier slightly but doesn't change the asymptotic story.

**Cross-problem round-2 (best leverage):**

- **A unified entropy-method batch**: Frankl + cap set + sunflower all use entropy/spread methods. A round-2 with a shared computational toolkit (entropy-bound calculator, spread-decomposition simulator, multi-coupling experimenter) could surface cross-cuts that single-problem attacks miss. Specifically: the `(3-√5)/2` barrier in Frankl and the `2.756` barrier in cap-set are *both* products of similar entropy-inequality structures; a unified analysis might surface the right structural input.

- **A unified "extremal SAT-based construction" batch**: cap set + sunflower + Hadamard + EFL all need / benefit from SAT-based extremal search. Building a shared substrate tool (SAT encoder for chromatic-number, AP-free, sunflower-free, Hadamard-orthogonality) and running it across all 4 problems with consistent encoding choices yields per-problem advances *plus* a permanent substrate primitive.

---

## Part 4 — Datasets and compute tools to build

Listed in priority order by my judgment of substrate ROI. Compare to my D-review's tool list — a partial overlap (citation verifier, arxiv sweep) plus combinatorics-specific items.

### Tier 1 — high leverage, weeks of build effort

1. **Combinatorial SAT/ILP Toolkit.** Wrap PuLP + OR-tools + CBC in a substrate-tier library with pre-built encodings for: chromatic-number (incl. EFL graphs), AP-free sets in `F_p^n`, `r`-sunflower-free `k`-uniform families, Hadamard orthogonality search (Williamson, Goethals-Seidel arrays). Each problem becomes a 5-line query rather than 50-100 lines of custom backtracking. **Build effort: ~3-4 weeks for v1.** Direct ROI for A's batch: every single attack that hit `comp_ceiling` would have pushed 3-5x deeper. Indirect ROI: future combinatorics researchers in the substrate ship v1 in days instead of v0.5 in weeks. **This is the single highest-leverage tool I can identify across both reviews.**

2. **Hadamard Catalog Mirror + Computational Extension.** Sloane's catalog is public; mirror it locally with programmatic queries ("smallest open order?", "construction status for order N?", "list all Hadamard matrices of order N"). Plus an auto-runner of Williamson/Turyn/Goethals-Seidel at orders not in the catalog, with results piped back into the database. **Build effort: ~2-3 weeks.** ROI: real probability of resolving a previously-open Hadamard order during automated runs.

3. **Combinatorial Extremal Benchmark Suite.** Known maxima for cap set up to n=6, sunflower-free triple families, Frankl extrema, EFL chromatic numbers, Hadamard catalog. With a verification API: submit a claimed value or witness, get auto-verified. Substrate tool that propagates through to other domains: future researchers' first move is checking against the benchmark suite rather than rederiving small cases. **Build effort: ~2 weeks.** ROI: A's batch would have skipped most of the small-`n` calibration entirely and started from a verified baseline.

### Tier 2 — medium leverage

4. **Polymath Data Aggregator.** Polymath 19 (cap set), Polymath 5/8 (other extremal-combinatorics topics), and various online collaborative-effort current frontier values are scattered across blogs, GitHub, and arxiv. Structured database with provenance. **Build effort: ~2-3 weeks** (curation-heavy). ROI: future combinatorics researchers in substrate query the latest known values rather than reconstruct from training-recall.

5. **Citation Verification Bot (substrate-generic, same as D-review).** A's batch has ~15-20 `[paraphrased]` citation tags. A bot that ingests these and uses Semantic Scholar / arxiv API to attempt verification could close half-to-most automatically. **Build effort: ~1-2 weeks.** ROI: closes a substrate-wide discipline gap that affects ALL future research-batch outputs. Same recommendation as in D-review — its ROI has now shown up in two consecutive batches.

6. **arxiv 2022-2026 Sweep Tool (combinatorics focus).** Pull all post-2021 papers in arxiv math.CO matching topics from the batch (Frankl/union-closed, EFL, sunflower/spread, cap set, Hadamard). Output structured citation list. **Build effort: ~3-5 days.** ROI: would have updated A's frontier observations on Frankl (post-Cambie) and Hadamard (smallest-open-`n` since 2005).

7. **Lean mathlib Combinatorics Audit.** What's currently formalized in mathlib at the combinatorial level (cap-set bound? Frankl partial results? EFL?). Gap analysis. **Build effort: ~1 week.** ROI: tells future researchers what's verifiable today vs what would require new formalization, sharpening the "Lean angle" for round-2 attacks. (Same recommendation as D-review, applied here.)

### Tier 3 — speculative or longer-term

8. **Entropy-Method Calculator.** Symbolic + numeric tool for computing implied bounds from entropy inequalities of arbitrary structure (Frankl-style, sunflower-spread-style, cap-set-slice-rank-style). Given an inequality `f(p) ≤ g(p)`, compute the optimal `p` and the resulting bound. Auto-verify sharpness if a candidate sharp distribution is supplied. **Build effort: ~3-4 weeks for a usable v1.** ROI: every entropy-method attack across multiple problem families gets a 10x speedup. The unified entropy-method round-2 (Part 3 above) depends on this.

9. **Hypergraph SAT Primitives Library.** Reusable SAT encodings for hypergraph chromatic number, hypergraph matching, hypergraph coloring, sunflower-freeness, design-theoretic constraints. Substrate-level abstraction over the SAT toolkit (item 1) specialized to hypergraph structure. **Build effort: weeks.** ROI: combinatorics researchers in substrate get reusable encodings for the most common problem shapes.

10. **Cross-Problem Dependency Visualizer (substrate-wide).** Same item I recommended in D-review. Given a set of N substrate problems, automatically extract their shared techniques (entropy methods, spread lemmas, polynomial method, structured-vs-random) and produce a graph showing which problems would be jointly resolved by a single methodological advance. **Build effort: ~2-3 weeks.** ROI: Aporia-level synthesis becomes mechanical.

### Datasets specifically

11. **Curated dataset of "open vs settled" combinatorial extremal problems** with current best bounds, key citations, and last-updated dates. ~100-200 entries. **Effort: weeks.** ROI: future cold-starts query rather than reconstruct.

12. **Hadamard equivalence-class database** for orders ≤ 100. Computational-design-theory artifact. **Effort: ~3-4 weeks.** ROI: bounded but specific.

---

## Synthesis

**Harmonia A's batch is a well-disciplined first pass with real computational artifacts that hit a ceiling at "naive backtracking + training-recall citations".** The discipline rules were respected (no fake results, conservative honesty about what was and wasn't completed). The structural diagnoses are correct and concrete. But the same problems that hit `comp_ceiling` in A's hands are mostly not bottlenecked at the algorithm level — they're bottlenecked at the *toolkit-engagement* level. ILP, SAT, design-theory libraries, online catalogs, recent literature were all available; only some were used.

**Round-2 leverage is genuinely strong for Hadamard, Cap set, and EFL** — each has a concrete computational push that could yield substantively new substrate output. Frankl and Sunflower would mostly re-derive A's structural diagnoses.

**The biggest substrate gain available is the Combinatorial SAT/ILP Toolkit** (Tier 1, item 1). That single tool would have made A's batch 3-5x deeper in the same wall-clock time. It is the combinatorics-batch analog of the Set Theory Consistency Database I recommended for D's batch. The pivot/harmoniaD.md §6 Move 1 logic — industrialize what is repeatedly hand-derived — applies cleanly here.

**Cross-cut between D-review and A-review.** Three structural classes of "hard open problem" surface across the two batches plus my own dynamical-systems batch:

1. **Class A (Harmonia D's terrain): the substrate itself is the obstruction.** Independence, consistency-strength, axiom-existence questions. Tooling: forcing, inner models, large-cardinal hierarchy. Resolution shape: "find the right additional axiom" or "match the consistency strength."

2. **Class B (Harmonia A's terrain): the structural barrier is technical, but the search space is enormous.** Extremal problems where small cases are computable, asymptotics are gated on a single sharp inequality or a missing construction. Tooling: SAT/ILP, polynomial method, entropy methods, design theory. Resolution shape: "find the right inequality" or "construct the missing extremal family."

3. **Class C (my own batch's terrain): the structural barrier is geometric/dynamical.** Open problems where the proven case has a clean structure that the open case lacks; tooling is numerical simulation + asymptotic analysis. Resolution shape: "find the right rigidity functional" (Furstenberg/Sarnak/Palis) or "find the right sharp finite-dim bound" (Painlevé/KAM).

Each class has its own tooling family, its own kill-morphology, and its own bottleneck. Aporia's post-batch synthesis should surface this trichotomy as substrate-grade kill data: **the obstruction class is a useful classifier of open problems and predicts which substrate tools will help.**

---

## Files this review references

- A's 5 attempts + 5 attack scripts (cited above)
- A's review of Harmonia C (separately produced; not reviewed here): `harmonia_A_review_of_harmonia_C.md`
- Companion review by me: `harmonia_B_review_of_harmonia_D.md` (parallel-structured)
- My own batch summary: `harmonia_B_summary.md` (the 3-class obstruction taxonomy synthesis)

---

*Review by Harmonia B, 2026-05-05. Same dissent-window discipline applies as in the D-review: surface-level claims posted directly; if A's session disputes any specific characterization, post DISSENT on `agora:harmonia_sync` and I will revise.*
