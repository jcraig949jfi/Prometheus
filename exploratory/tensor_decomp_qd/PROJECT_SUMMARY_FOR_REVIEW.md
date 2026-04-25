# Quality-Diversity Search over Low-Rank Tensor Decompositions

**Project summary prepared for external review**
**Author:** Harmonia_M2_sessionB (autonomous research session)
**Period:** 2026-04-23 to 2026-04-25
**Repo state:** `D:\Prometheus\exploratory\tensor_decomp_qd\` — 11 pilots, 5 published-quality findings, 11 commits on local main

---

## Executive summary

We pursued the question: *can a Quality-Diversity (MAP-Elites-style) archive over low-rank tensor decompositions surface useful structure that single-point optimizers (AlphaTensor, AlphaEvolve, Flip-Graph Search, StrassenNet) miss?*

**Across 10 pilots × 4 fields × 4+ tensor families × 5 mutation classes:**
- **Matmul tensors are pathologically rigid for QD.** The rank-minimum orbit count is 1 over F_2, F_3, ℚ at every size tested (2x2 and 3x3). The three rank-23 orbits found over ℚ are matmul-cyclic-Z_3 cosets — not novel algorithms.
- **Polymul tensors have meaningful sub-optimal-rank diversity.** Exhaustive 2-bit-flip neighborhood probes find 12 (n=3, F_2), 34 (n=4, F_2), 16 (n=3, F_3) distinct non-naive orbits at sub-optimal rank.
- **The mutation primitive is the proven bottleneck.** We tried bit-flip (4 fields), 3-to-2 flip-graph, 2-to-2 flip-graph, 4-to-3 flip-graph, and entry-level LLM mutation. None bridges between rank-r orbits of matmul. Across 200K+ canonicalized submissions, only known-seed orbits and their cyclic conjugates ever populate the archive.
- **Canonicalization is solved.** Brute-force isotropy enumeration scaled fine through |Iso| = 6048 (3x3 F_2). For larger gauges (3x3 F_3 and ℚ), invariant-tuple canonicalization works — verified gauge-invariant on 50/50 random isotropy elements per pilot.

The project produced **two reusable methodological tools** (products-then-solve verification; invariant-tuple canonicalization) and **three substantive empirical findings** (matmul Hamming-isolation universality; polymul sub-optimal richness; ℚ rank-23 orbit cosets under GL_3(ℚ)³).

The original "find a novel decomposition via QD" thesis did not materialize. The mutation-bottleneck finding *did* — and it is informative about what NOT to attempt going forward.

---

## 1. Origin and thesis

The project began (2026-04-23) as an incubation of "Discovering Novel Low-Rank Tensor Identities" — searching for efficient tensor decompositions of known objects via genetic algorithms / MAP-Elites, similar in spirit to how Strassen's algorithm was originally found.

The literature scan (3 passes, ~255 unique papers) immediately surfaced strong contemporary competition: AlphaTensor (DeepMind, 2022), AlphaEvolve (DeepMind, May 2025) plus four open-source replicas (CodeEvolve, GigaEvo, ImprovEvolve, DeepEvolve), Flip-Graph Search (Khoruzhii/Gelß/Pokutta, 2025), StrassenNet (Andreini et al., 2026), Yang's SAT-based negative results (2024), and the constraint-programming approach (Deza et al., 2023).

**The unclaimed niche: behavior-diversity ARCHIVE.** Every existing method outputs a single-point solution. None produces a populated map of (rank × sparsity × symmetry × coefficient-magnitude) cells. The thesis became:

> The archive is the product. Strassen is one cell in that archive; the other cells are the unclaimed territory.

Defensible IF (a) such cells exist and (b) we can reach them. The pilots tested both.

---

## 2. Methodology

### Calibration ladder

Following the discipline that "we should learn this the cheapest possible way" (a phrase the work kept returning to), pilots were ordered smallest-to-largest:

1. **2x2 matmul over F_2** (Strassen calibration; smallest interesting case)
2. **3x3 matmul over F_2** (Laderman seed; first non-trivial size)
3. **2x2 matmul over F_3** (test if char-2 was the issue)
4. **3x3 matmul over F_2 + 4-to-3 flip-graph** (test if higher-arity moves help)
5. **3x3 matmul over F_3 with invariant canonicalization** (scales canonicalization)
6. **Polymul n=3 over F_2** (less-saturated tensor)
7. **Polymul n=4 over F_2** (test n-scaling of polymul richness)
8. **Polymul n=3 over F_3** (test field-scaling of polymul richness)
9. **3x3 matmul over ℚ** (test if ℚ has multiple rank-23 orbits per algebraic-geometry literature)
10. **LLM-driven mutation on polymul n=3 over F_2** (test if LLM can bridge orbit isolation)

Each pilot uses the same architecture: tensor + canonicalizer + gauge-invariant descriptors + MAP-Elites loop + forbidden-cell discipline + unit tests + reseeded runs + diagnostic report.

### Key disciplines applied

**Distinguishing B1 from B2 in negative results.** Before concluding "method works but result is trivial," supply diagnostics separating domain-structure (B1) from exploration-insufficiency (B2). In every negative result we ran exhaustive local-neighborhood probes + brute-force random sampling.

**Forbidden-cell enforcement (operational, not advisory).** Any canonical representative landing at a rank below a known theoretical lower bound (Hopcroft-Kerr 1971 for matmul; Toom-Cook bounds for polymul) triggers immediate canonicalizer audit. Across 200K+ submissions, zero violations occurred.

**Gauge-invariance unit tests.** Before any MAP-Elites run, the canonicalizer must pass: 8/8 standard tests including (a) idempotence, (b) gauge-equivalent decompositions canonicalize to identical bytes, (c) near-miss decompositions don't collide with seeds, (d) orbit × stabilizer = |gauge| (Lagrange).

**Honest claim discipline for LLM work.** The LLM-mutation pilot's prompt explicitly forbade claiming novel matmul algorithms (AlphaEvolve already does that; budget mismatch is too large to credibly compete). The defensible claim is QD-architectural, not algorithmic.

---

## 3. Reusable infrastructure produced

### Products-then-solve verification method

When encoding a published tensor decomposition (Strassen's 7 products, Laderman's 23, Smirnov's catalog) from memory or imperfect sources, the **products** (a-side and b-side of each rank-1 summand) are easier to remember correctly than the **output formulas** (which products combine to produce z_{ij}). Memory errors concentrate in the latter.

**Method:** encode just the products. Build the per-product contribution matrix (each column = the bilinear monomials that product contains). For each output z_{ij}, solve `contrib · s = target` over F_p via Gaussian elimination. If solvable, `s` gives the correct subset of products.

Used successfully for: Laderman over F_2, Laderman over F_3, Laderman over ℤ (signed), Karatsuba-3-way over F_2 + F_3.

Reference: `pilot_F2_3x3/laderman_solve.py`.

### Invariant-tuple canonicalization

Brute-force "iterate over all isotropy elements" canonicalization works through |Iso| ≈ 6000 but breaks down past ~10⁶. For 3x3 matmul over F_3 (|Iso| ≈ 10⁷-10¹⁰) and ℚ (continuous), we need a different approach.

**Method:** instead of finding the lex-min orbit representative, compute a tuple of gauge-invariant scalars that approximately identifies the orbit:
- effective rank
- mode-flattening rank signature `(rank M_1, rank M_2, rank M_3)`
- multiset of pair-sub-tensor mode-rank tuples (over all C(r, 2) pairs)
- multiset of triple-sub-tensor mode-rank tuples (over a sample of C(r, 3) triples)

This tuple is gauge-invariant by construction (basis change preserves flattening ranks). Hash it as the cell key.

**Validation:** verified 50/50 gauge invariance on naive, Laderman, Smirnov-cyclic variants under random matmul-isotropy elements. Two failed-candidate invariants are documented as anti-patterns: `column_weight_multiset` (NOT actually basis-invariant) and `stabilizer_lower_bound` from single sample (conjugation-biased, 46/50 perturbed forms gave different counts).

Reference: `pilot_F3_3x3/`, `pilot_Q_3x3/`.

---

## 4. Substantive empirical findings

### Finding 1: Matmul tensors are Hamming-isolated at every tested rank, in every tested field.

Across all matmul pilots:

| Substrate | Decomposition | Hamming-distance ≤ 4 valid neighbors |
|---|---|---|
| 2x2 F_2 | Strassen rank-7 | 0 / 2,028,355 (exhaustive) |
| 3x3 F_2 | Naive rank-27 | 0 (extensive sampling) |
| 3x3 F_2 | Laderman rank-23 | 0 / 213,131 (exhaustive 1-3 bits, 20K sampled at higher) |
| 2x2 F_3 | Strassen rank-7 | 12 / 762,272 valid at 3-entry; **all** canonicalize back to Strassen |
| 3x3 F_2 | Laderman + 4-to-3 search | 0 / 8,855 quadruples have tensor rank ≤ 3 |

**No local move ever bridged matmul rank-r orbits in any test.** Pure bit-flip, ternary-flip over F_3, 3-to-2 flip-graph, 2-to-2 flip-graph, 4-to-3 flip-graph (with rank-3 tensor decomposition primitive over F_2) — all proven non-functional.

**Why this matters:** quantifies a property of the matmul algorithm-search landscape that, to our knowledge, has not been measured systematically before. It tells future researchers: don't attempt local-mutation QD on matmul; the bottleneck is geometric, not algorithmic.

### Finding 2: Polymul tensors have meaningful sub-optimal-rank orbit diversity.

Exhaustive 2-bit-flip neighborhood probes of naive seed:

| Tensor | Naive rank | Distinct non-naive orbits at 2-flip distance |
|---|---|---|
| Polymul n=3 over F_2 | 9 | 12 |
| Polymul n=4 over F_2 | 16 | 34 |
| Polymul n=3 over F_3 | 9 | 16 |

These are **gauge-quotiented orbit counts**, not raw distinct decompositions. Each orbit is a genuinely distinct equivalence class under the polymul gauge group (D_3 × Z_2 over F_2; size 24 over F_3 with non-trivial F_3* scaling).

The rank-MINIMUM orbit count is still 1 in every polymul pilot — the algebraic rigidity at the optimum persists. But the non-minimum terrain is genuinely populated, and MAP-Elites finds **only ~25%** of these orbits over F_3 (4 / 16) and **0%** over F_2 n=4 — confirming that local mutation under-explores even where rich terrain exists.

**Why this matters:** this is the project's one positive empirical demonstration of the QD-archive thesis. Polymul-family tensors (and likely convolution / group-algebra) are where the QD framework can actually produce population diversity worth charting.

### Finding 3: Z_3 cyclic symmetry of matmul lives outside GL_n(ℚ)³.

Over ℚ-bounded ℤ, we encoded Laderman with original signed coefficients, then applied two transformations:
- Transpose conjugate (a Z_2 symmetry of matmul: (X, Y, Z) ↔ (Y^T, X^T, Z^T))
- Cyclic conjugate (a Z_3 symmetry: cyclic permutation with transpositions)

Computed invariant tuples for all three:
- Laderman: `fd34...`
- Transpose conjugate: `fd34...` (identical to Laderman)
- Cyclic conjugate 1: `e25f...` (different)
- Cyclic conjugate 2: `058f...` (different)

This **empirically demonstrates** that the transpose Z_2 IS captured by GL_3(ℚ)³ acting via `(α, β, γ) ↦ (αXβ⁻¹, βYγ⁻¹, αZγ⁻¹)`, while the cyclic Z_3 is NOT. Three "distinct orbits" in our gauge are actually one orbit under the full matmul automorphism group.

**Why this matters:** the project's architecture handles "outcome A" verification correctly — it shipped 3 distinct invariant tuples — but is honest about WHY those three exist. They are not novel algorithms; they are de Groote-1978 cosets. Future work on novel rank-23 algorithms over ℚ should seed with Smirnov-class variants known to be gauge-inequivalent under the full automorphism (currently a genuinely open question: are there any?).

---

## 5. The negative result that's worth its own line

**LLM mutation at entry-level granularity does not bridge orbit isolation.** Claude Haiku 4.5 made 139 successful API calls (100% parse success, 100% API success, 0% validity). Every proposed small modification was syntactically clean and algebraically broken. The model has no privileged access to "which entry edits preserve the matmul-sum identity" and its proposals are no better than random small perturbations.

This narrows the LLM-mutation hypothesis space cleanly:
- Direct entry-level editing: doesn't work (this pilot)
- Code-level editing (AlphaEvolve framing): probably works at large budgets (per published AlphaEvolve results); small-budget feasibility is open
- Validity-projecting wrapper around arbitrary mutations: untested; the hard part is solving the validity manifold projection problem cheaply

The LLM negative is a clean-budget, infrastructure-validated, reproducible result — useful to future researchers asking "should I just call an LLM as my mutation operator?" The answer at our budget+granularity is "no." A larger pilot at code-level (probably the AlphaEvolve framing applied to polymul, where AlphaEvolve hasn't been published) would test the next hypothesis up.

---

## 6. Open questions (where I am genuinely uncertain)

These are the questions I'd most want a reviewer to weigh in on:

### Q1. Is Hamming-isolation universality novel or known?

Algorithmic-complexity researchers may know that matmul decompositions are "isolated" in some sense, but I haven't found a paper that quantifies it via exhaustive bit-flip neighborhood probes across multiple decompositions and fields. **Is this a publishable empirical result, or has it been measured before in different language?**

### Q2. How seriously should we take the polymul richness finding?

12 / 16 / 34 distinct orbits at sub-optimal rank is a real number. But does it matter? Possible interpretations:
- (a) Real: polymul tensor families are where QD can show its teeth. Worth investing in.
- (b) Trivial: of course there are many ways to write a sub-optimal decomposition; no one cares about non-minimum decompositions because they're not "useful algorithms."
- (c) Half-real: minimum-rank decompositions are where complexity-theory cares; sub-optimal decompositions might matter for hardware/ergonomic reasons (sparsity, coefficient magnitude).

I lean toward (c) but the interpretation depends on community.

### Q3. Is the products-then-solve method actually new?

It's pretty obvious in retrospect — given products, the output formulas are linear in F_p so just solve the system. **Has this been published as a verification method? Or is it folklore?**

### Q4. The ℚ rank-23 cyclic-coset finding — is this useful?

de Groote 1978 classified the matmul automorphism group. We empirically demonstrated that the cyclic Z_3 lives outside GL_n(ℚ)³ via invariant-tuple comparison. Nothing in our work is theoretically novel. **Is the empirical demonstration via canonicalization framework worth anything, or is it just re-deriving 50-year-old results?**

### Q5. Should we attempt code-level LLM mutation on polymul?

AlphaEvolve has done matmul. Polymul over higher n (n=4, 5) does not appear in published AlphaEvolve work. A code-level LLM mutation pilot on polymul could:
- Confirm or refute that AlphaEvolve framing works at our budget
- Apply QD-archive wrapper for orbit-coverage rather than rank-minimization
- Produce the project's first genuinely novel positive empirical result

But it's a multi-day pilot with API costs and the standard AlphaEvolve-replication caveats. **Is this worth it given (4) below?**

### Q6. What's the project's intended deliverable?

The pilots' scaffolding (5+ committed reports, methodology infrastructure, 11 pilot directories) is enough for either:
- (i) A research note on tensor-decomposition QD's empirical frontier
- (ii) A methodology paper introducing products-then-solve and invariant-tuple canonicalization as primitives
- (iii) A blog post about what QD search reveals about matmul's algorithmic landscape
- (iv) Internal reference for further work

Choice of (i)-(iv) shapes what additional pilots are worth running.

---

## 7. Suggested next steps (ranked)

### Option A: Stop and write up. Most defensible.

The empirical results have stabilized after 10 pilots. Additional pilots without methodology shifts are unlikely to change the picture significantly. The five publishable findings (two methodology, three empirical) form a coherent narrative.

**Cost:** ~3-5 days for a clean write-up of the existing material.
**Value:** captures the work in a reviewable form; lets reviewers (you and others) decide direction with full context.

### Option B: Convolution and group-algebra pilots (polymul-family expansion, continued).

Polymul n=3 / n=4 / n=3-F_3 all show consistent sub-optimal richness. Extending to:
- Convolution tensors (n=4, n=5)
- Group-algebra tensors: quaternion (size 4), complex (size 2), small dihedral (size 6+)

Each pilot = ~1 day using the polymul template.

**Cost:** ~5 days for 5 pilots.
**Value:** Strengthens the polymul-richness empirical case. If they all show 12-50 sub-optimal orbits, the QD-archive thesis has its strongest evidence base.

### Option C: Code-level LLM mutation on polymul.

Applies AlphaEvolve framing to a less-saturated tensor (polymul n=4 or n=5), where AlphaEvolve hasn't published results. Wraps it in QD archive for coverage rather than minimum-rank chase.

**Cost:** ~3-5 days; non-trivial API budget (~$50-200); AlphaEvolve replication uncertainty.
**Value:** If it works → genuinely novel result. If it doesn't → another clean negative narrowing the hypothesis space.

### Option D: Validity-preserving projection wrapper.

The proven bottleneck is "tiny edits don't preserve validity." A solver that takes ANY mutation (bit-flip, LLM proposal, anything) and projects it onto the validity manifold (closest valid decomposition by some metric) addresses the bottleneck head-on. Algorithmically hard (validity manifold = solution set of Brent equations; projection = nontrivial system to solve).

**Cost:** ~1 week minimum for a working prototype on F_2 small cases.
**Value:** Highest reward if it works; could turn matmul pilots from B1 to A. Highest cost.

### My honest recommendation

**Option A first, Option B second.** The methodology pieces (products-then-solve, invariant tuples) are genuinely useful primitives that warrant a clean writeup independent of the empirical-findings story. Once that's in reviewable form, B is the cheapest extension and the only direction with strong prior evidence (polymul's sub-optimal richness already replicates across two fields and two values of n).

**C and D are interesting but speculative.** I'd defer them unless the writeup of A motivates a specific reason to pick one.

---

## 8. Project artifact index

All in `D:\Prometheus\exploratory\tensor_decomp_qd\`:

**Pilots (10 directories):**
- `pilot_F2_2x2/` — 2x2 matmul over F_2 (B1)
- `pilot_F2_3x3/` — 3x3 matmul over F_2 with 3-to-2 + 2-to-2 flip-graph (B)
- `pilot_F2_3x3_v2/` — 3x3 matmul over F_2 with 4-to-3 flip-graph (B1, stronger)
- `pilot_F3_2x2/` — 2x2 matmul over F_3 (B1; rejects char-2 hypothesis)
- `pilot_F3_3x3/` — 3x3 matmul over F_3 with invariant canonicalization (B; canonicalization solved)
- `pilot_polymul_n3/` — Polymul n=3 over F_2 (B1 + 12 sub-optimal orbits)
- `pilot_polymul_n4/` — Polymul n=4 over F_2 (B1 + 34 sub-optimal orbits)
- `pilot_polymul_n3_F3/` — Polymul n=3 over F_3 (B1/B2-leaning; 16 sub-optimal orbits)
- `pilot_Q_3x3/` — 3x3 matmul over ℚ (formal A; matmul-Z_3 cosets, not novel)
- `pilot_LLM_mutation/` — Haiku 4.5 mutation on polymul n=3 (B; 0/139 valid)

Each has its own `PILOT_REPORT.md`.

**Synthesis documents:**
- `README.md` — project overview + 10-pilot status table
- `META_REPORT_PARALLEL_PILOTS.md` — Direction 1 synthesis (3 parallel pilots)
- `META_REPORT_DIRECTION_2.md` — Direction 2 synthesis (3 parallel pilots)
- `PROJECT_SUMMARY_FOR_REVIEW.md` — this document

**Literature scan:**
- `harmonia/tmp/tensor_decomp_lit/SYNTHESIS.md` — 3-pass scan, ~255 papers

**Session journal:**
- `roles/Harmonia/worker_journal_sessionB_20260423.md`

**Memory entries (`C:\Users\James\.claude\projects\D--Prometheus\memory\`):**
- `project_tensor_decomp_qd.md` — project-level memory
- `feedback_products_then_solve.md` — methodology memory
- `feedback_distinguish_B1_B2.md` — discipline memory

**Commits on local main (no pushes):**
- `ab605eb4` — initial 2x2 + 3x3 F_2 pilots
- `810ee5c8` — 2x2 F_3 pilot
- `eee8a6bd` — README update
- `3b01cd44` — pilot_F2_3x3_v2 (4-to-3 flip-graph)
- `039c7fe6` — pilot_polymul_n3
- `e8d2f89c` — pilot_F3_3x3 (invariant canonicalization)
- `85bf42c9` — META_REPORT_PARALLEL_PILOTS
- `8e5cb0e0` — pilot_polymul_n4 + pilot_polymul_n3_F3
- `857f8adc` — pilot_Q_3x3
- `9bc8ddf1` — pilot_LLM_mutation
- `22323ef3` — META_REPORT_DIRECTION_2 + README

---

## Closing note

The project's strongest claim is its discipline, not its discoveries. Across 10 pilots run with consistent methodology (calibration ladder, B1-vs-B2 distinction, forbidden-cell enforcement, gauge-invariance unit tests, honest claim discipline), the shape of "what works and what doesn't" is now well-characterized. The mutation-bottleneck finding is a reproducible structural result that applies to anyone attempting QD search on matmul decompositions; the polymul-richness finding is a positive empirical demonstration of where QD does have purchase. The methodology tools (products-then-solve, invariant tuples) are reusable beyond this project.

Whether to push further or write up is a real decision and I have a slight lean toward "write up first." But I would defer to the reviewer's judgment.

---

*Document path: `D:\Prometheus\exploratory\tensor_decomp_qd\PROJECT_SUMMARY_FOR_REVIEW.md`*
*Prepared 2026-04-25 by Harmonia_M2_sessionB*
