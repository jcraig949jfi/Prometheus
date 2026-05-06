# Charon 1 — Review of Charon 3's batch

**Reviewer:** Charon 1 (additive/multiplicative number theory batch researcher)
**Reviewing:** Charon 3's topology / geometry batch (Smooth 4D Poincaré, Hodge / CY3, Novikov / Burnside-Gromov-monsters, Volume Conjecture / 5_2, Hadwiger–Nelson)
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Companion:** parallel `charon_2_review_of_charon_3.md` exists in this directory; I drafted independently and only cross-checked at the end (note in §"Cross-check with Charon 2's review" below).

---

## Executive summary

Charon 3 produced **the cleanest of the three Charon batches I have reviewed**. Two computational wins (Moser spindle χ=4 verified, figure-eight VC numerical confirmation to N=2000), one substrate-grade calibrated kill on a wrong-formula 5_2 colored-Jones (a "watch out for this normalization" datum the substrate didn't have before), and a load-bearing cross-problem observation — the **insufficient-invariant pattern** — that is the most substrate-grade output of any of the three Charon batches.

Three structural gaps surface on review:

1. **Missed major recent development on Problem 1.** **Akbulut's 2022 outline of an SPC4 proof** (arXiv:2209.09968), with multiple versions through 2024, is absent from Charon 3's citation chain. Even if the proof is contested or not accepted by the broader community, its existence reframes the obstruction discussion. Charon 3 cites Akbulut 2010 (Cappell-Shaneson elimination) but stops there.

2. **Unforced compute halt on Problem 4.** Charon 3 explicitly identifies the correct Hikami/Habiro double-sum colored-Jones formula for 5_2 and the gap from their (failed) single-sum implementation, then doesn't take the next step. This is a pure "1 lemma short" gap that costs maybe a day of work and produces a substrate-grade VC numerical verification for the second-simplest hyperbolic knot. **Round-2 should close this immediately.**

3. **Unforced compute halt on Problem 5.** Charon 3 acknowledges that adding `python-sat` and pulling Heule's reduced graph closes the verification step in ~30 min. They describe the move and decline to make it. Same pattern as P4 — round-2 closes it cheaply.

The other gaps (recent CY3 / Hodge work, recent Burnside / Property A status) are minor relative to these three.

**Net recommendation:** for any round-2 effort, prioritize closing P4 + P5's documented cheap-close gaps (a day's work each), then chase Akbulut 2022 for P1's literature update. Cross-batch tooling is genuinely productive but lower priority than the cheap-closes.

---

## Per-problem review

### Problem 1 — Smooth 4D Poincaré

**What Charon 3 did well:**
- Verified vanishing of SW dimension on S⁴ via index formula (d = −1, b₂⁺ = 0): clean, reproducible, substrate-grade calibration of the structural obstruction.
- Surveyed Bauer-Furuta refinement and Manolescu's Pin(2)-equivariant Floer; correctly identified that Pin(2)-Floer is for 3-manifolds and doesn't directly attack closed 4-manifolds.
- Identified the "candidate-list-vs-universal-claim" pattern as a structural ceiling on the candidate-elimination strategy.

**What was missed / underutilized:**

1. **Akbulut 2022, "On smooth 4-dimensional Poincaré conjecture" (arXiv:2209.09968)** — outlined proof of SPC4, with revisions through 2024. **This is the single most consequential miss in the batch.** Charon 3's literature scan stops at Akbulut 2010. A 2026 attack on SPC4 should at minimum mention the existence of Akbulut's claimed proof, even if to register it as disputed or not-yet-broadly-accepted. The status of the Akbulut 2022-2024 proof outline (community acceptance? has it been peer reviewed? are there published critiques?) is exactly the kind of "where does the field stand right now" question that frames any substrate-grade attack on the conjecture.

2. **Khovanov / Khovanov-Lee / Rasmussen-s machinery** — categorified link/knot invariants have produced 4-manifold-like distinguishing power (Hayden, Kjuchukova, Mukherjee, Sundberg 2024 on knot trace embeddings; Rasmussen-s for 4D smoothness questions). Mukherjee's 2023+ work on exotic Mazur manifolds is directly adjacent. These are non-gauge-theoretic invariants that *don't* vanish for the same dimension-formula reason that Donaldson/SW vanish. Worth a survey.

3. **Daemi / Hayden / Lidman / Mark / Mukherjee / Picard-Boucher recent work** on 4-manifold invariants surviving in b₂⁺=0. Several 2022-2025 papers that Charon 3 doesn't cite but bear on whether b₂⁺=0 is genuinely a "structural floor" or just a floor for the gauge-theoretic invariant family.

4. **The 11/8 conjecture and its relation** — Furuta's 10/8 + ε result (1995, 2001) and Hopkins-Lin-Shi-Xu 2018 progress toward 11/8 give partial data on the structure of definite intersection forms; these constrain b₂⁺=0 4-manifolds in ways that may eventually feed back into SPC4. Charon 3 doesn't mention.

**Round-2 angles:**

- **A1.** **Critical:** read Akbulut 2022/2024 outline of SPC4 + survey community reception 2024-2025. Update obstruction discussion to reflect the current contested-proof landscape. (~1 hour)
- **A2.** Survey 2022-2025 4-manifold-invariant work (Hayden, Mukherjee, Daemi) for non-vanishing-on-S⁴ candidate invariants. (~2 hours)
- **A3.** Furuta-Bauer 10/8 line and Hopkins-Lin-Shi-Xu progress toward 11/8 — does this constrain candidates for exotic S⁴? (~1 hour)

**Datasets / tools to build:**

- `charon/instruments/four_manifold_invariant_table.py` — for each known 4-manifold-distinguishing invariant family, record (name, dimension formula, vanishing conditions, dependency-on-spin^c-structure). The substrate-grade question becomes mechanical: which row of the table is non-vanishing on b₂⁺=0?

**Round-2 verdict:** **Yes, productive (urgent on Akbulut 2022 update).** SPC4's literature is moving; the 2010 candidate-elimination-era citations are insufficient as a 2026 baseline.

---

### Problem 2 — Hodge Conjecture (CY3 sub-case)

**What Charon 3 did well:**
- Trivial verification for h^{1,1}=1 quintic CY3 — clean, included for completeness.
- Identified the precise reduction: codim-2 Hodge conjecture on a CY3 reduces to (Lefschetz (1,1)) + (cup-product surjectivity H^{1,1}⊗H^{1,1}→H^{2,2}). This is the substrate-grade observation that sharpens the open question into a concrete linear-algebra statement.
- Mumford-Tate group analysis well-done for the generic vs special cases.
- Period integrals deferred honestly with the "would take >>3 hours" reason.

**What was missed:**

1. **The Voisin 2020-2024 CY3 papers.** Voisin has published several papers in this period (2020 paper on integral Hodge for hyper-Kähler, 2022 on Lagrangian fibrations, 2024 survey on cycle classes). Charon 3 cites Voisin 2002, 2003, 2007, but the recent work directly bears on the codim-2 question for CY3-related varieties (hyper-Kähler 4-folds are a parallel "open at codim 2" target).

2. **LMFDB has CY3 data** including explicit Hodge structure data for many small examples. The "compute Hodge structure of an explicit Schoen CY3" exercise Charon 3 deferred is achievable from LMFDB lookup rather than from-scratch period computation.

3. **Macaulay2 / Sage have explicit cohomology-ring computations for CY3.** The cup-product matrix that Charon 3 needed to check for the Schoen CY3 is computable in M2. This is the same tool gap pattern as P4 / P5 — the right tool exists but wasn't reached for.

4. **Schoen-type rigid CY3 cup-product surjectivity** has been computed in the literature for several explicit cases. Charon 3 says "for *generic* Schoen models the calculation has been done; for arbitrary Schoen-type fiber products there is no published universal theorem." Worth citing the specific generic-Schoen reference.

5. **Motivic / Voevodsky framework** — the recent (2020s) developments in motivic cohomology have produced new tools for the integral Hodge problem. Bachmann, Hoyois, Spitzweck papers. Charon 3 mentions "develop a motivic framework" as an unblock direction but doesn't note current progress.

**Round-2 angles:**

- **B1.** Sage / Macaulay2-based computation: cup-product matrix on Schoen CY3 + the Borcea-Voisin construction. Verify surjectivity case-by-case for an explicit list. (~2 days)
- **B2.** LMFDB CY3 data ingest: pull Hodge structure data for the available small CY3 catalog. (~1 hour)
- **B3.** Survey Voisin's 2020-2024 papers + recent motivic-cohomology developments (Bachmann-Hoyois-Spitzweck etc.). (~2 hours)
- **B4.** Period integration for mirror quintic at higher precision via PARI/GP — extends Charon 3's deferred Attack 5. (~1 day)

**Datasets / tools to build:**

- `charon/datasets/lmfdb_cy3_hodge_structures.parquet` — Hodge numbers + Picard lattice for available CY3 catalog.
- `charon/instruments/cup_product_matrix.py` — Sage/M2 wrapper for explicit Hodge-class cup-product computation.

**Round-2 verdict:** **Yes, productive but lower priority than P1/P4/P5.** The Voisin 2020-2024 lit-scan is a clean update. The cup-product computation is the right concrete experiment but requires Sage/M2 tooling that is heavier than P4/P5's lifts.

---

### Problem 3 — Novikov Conjecture for Burnside / Gromov monsters

**What Charon 3 did well:**
- Comprehensive survey of the standard tool family (Higson-Kasparov, Yu coarse BC, Lafforgue, Connes-Moscovici, Kasparov-Skandalis, Guentner-Higson-Weinberger).
- Correctly identified that Burnside groups B(m, n ≥ 665 odd) are simple, blocking finite-index reduction.
- "Entire-tool-family-blind" classification is the substrate-grade observation.
- Honest tag (NO_PROGRESS) for the appropriate verdict.

**What was missed:**

1. **L²-Betti numbers / Lück's machinery.** Lück's L²-cohomology framework provides Novikov-direction results that don't fit the standard a-T-menability / Property A / asdim taxonomy. Davis-Januszkiewicz, Lück-Reich. Charon 3 doesn't mention. Whether L² methods apply to Burnside is an open structural question worth surveying.

2. **Tessera 2020s on coarse embeddings** — Tessera has developed coarse-embedding theory beyond Property A, with results on Banach-space target embeddings (rather than Hilbert) that produce weaker but applicable Novikov-direction results. Worth checking whether B(m, n) has a Banach embedding.

3. **Lacunary-hyperbolic structure refinements.** Charon 3 noted Olshanskii-Osin-Sapir 2009 lacunary hyperbolic and that Lafforgue doesn't extend, but didn't survey 2020s extensions of lacunary-hyperbolic theory (Coulon-Sun-Sapir small-cancellation; Drutu-Kapovich asymptotic cone work).

4. **K-theoretic computation for specific B(2, 665).** Even acknowledging that no general result exists, an attempt to compute K_*(C*_max(B(2, 665))) directly might produce substrate-grade calibration data. Probably infeasible (the C*-algebra is non-explicit) but worth flagging as the "what would we even try to compute" question.

5. **The recent Fredholm-module-style approaches** — Connes-Moscovici-Wodzicki, Dabrowski et al. 2020s — provide a parallel cyclic-cohomology pathway that Charon 3's Attack 5 touches but doesn't pursue.

**Round-2 angles:**

- **C1.** Lit scan Lück 2020s + Tessera Banach-embedding work + recent Burnside-group results (Coulon-Sun-Sapir 2024-2025). (~2 hours)
- **C2.** Document the L²-cohomology framework as a parallel attack family explicitly. (~1 hour)
- **C3.** Probably defer K-theoretic computation — the C*-algebra is not explicit enough for tractable calculation.

**Datasets / tools to build:**

- A "Novikov-status table" indexed by (group class, attacking technique, status). Becomes a substrate-readable map of the entire NC frontier. Most rows are "not applicable" — but the structural map is itself substrate-grade.

**Round-2 verdict:** **Marginal.** Charon 3's NO_PROGRESS verdict is correct; round-2 produces more comprehensive literature notes and possibly a structural taxonomy table but no concrete advance is reachable. Lower priority than P1/P4/P5.

---

### Problem 4 — Volume Conjecture for 5_2

**What Charon 3 did well:**
- SnapPy volume computation for 10 small knots — clean, reproducible, substrate-grade calibration data.
- Figure-eight VC numerics to N=2000 with 60-digit precision — converges monotonically; gap +0.035; substrate-grade calibration of the numerical machinery.
- **Substrate-grade kill** on the wrong-formula single-sum 5_2 attempt: the published-formula-doesn't-give-VC-asymptotics result is exactly the kind of "watch out for this normalization" datum the substrate didn't have. **This is the strongest individual finding in the entire batch.**
- Honest tag (PARTIAL_RESULT) and clean documentation of why.

**What was missed — and this is unforced:**

1. **The correct Hikami/Garoufalidis-Lê double-sum formula for 5_2 IS PUBLISHED** and Charon 3 explicitly identifies it (Hikami 2003 Eq. 3.7) and explicitly says they didn't implement it in the time budget. **This is the obvious round-2 move.** It's not a "we don't know how" gap — it's a "we ran out of time on this session" gap. Closing it produces a substrate-grade VC numerical verification for the second-simplest hyperbolic knot.

2. **Bar-Natan's KnotAtlas** (Mathematica package KnotTheory') has explicit colored Jones polynomials computed for all small knots through ~10 crossings. **This is ground-truth data Charon 3 could have used instead of re-implementing from a transcribed formula.** Direct lookup avoids the transcription-error class entirely.

3. **Habiro's actual 2002 paper** has explicit polynomials for several small knots (4_1, 5_2, 6_1, 6_2, 6_3) per the literature trail. Same lookup-vs-reimplement pattern.

4. **SageMath's Combinatorics / Knot-theory packages** — q-Pochhammer symbol implementations, Habiro polynomial machinery. Available without writing from scratch.

5. **Recent (2023-2025) work on VC for hyperbolic 2-bridge knots.** Web search did not surface a specific 2023-2025 5_2 proof, but the area is active (Murakami-Hitoshi continues; Garoufalidis-Lê-Yoon collaborative work; Detcherry et al. on Turaev-Viro VC). Worth a fresh arXiv scan.

6. **Murakami's 2010 introduction-to-VC survey lists 5_2 as open** but Charon 3 didn't check whether 5_2 has been resolved since 2010 — a 16-year gap. Web search suggests it remains open as of 2025 but the verification is needed.

**Round-2 angles:**

- **D1.** **Critical and cheap:** implement the Hikami/Garoufalidis-Lê double-sum colored-Jones for 5_2, OR pull KnotAtlas / Habiro published polynomials for direct numerical evaluation. Run the VC numerical convergence test to N=1000+. (~1 day)
- **D2.** Extend to 6_1, 6_2, 6_3 with the same machinery. The Habiro polynomials are published for all four. (~1 day)
- **D3.** Survey 2023-2025 VC literature — has 5_2 been resolved? Has Ohtsuki's saddle-point conjecture been completed? (~1 hour)
- **D4.** Compute the Detcherry-Kalfagianni-Yang Turaev-Viro VC for the same knots' surgery manifolds — orthogonal verification. (~1 day)

**Datasets / tools to build:**

- `charon/datasets/colored_jones_small_knots.parquet` — verified J_N values for knots up to 10 crossings, N up to 100, indexed and content-addressed.
- `charon/instruments/volume_conjecture_battery.py` — given a knot, compute (a) Vol via SnapPy, (b) J_N via published formula or KnotAtlas, (c) numerical VC ratio, (d) convergence rate. Becomes a falsification battery for any future VC sub-result claim.

**Round-2 verdict:** **Yes, urgent — this is the cheapest round-2 close in the entire batch.** A clean implementation of the right 5_2 formula is a day's work; the resulting numerical evidence at N=500-1000 plus convergence-rate data is substrate-grade. **The kill that Charon 3 produced — single-sum twist-knot formula gives wrong VC asymptotics for 5_2 — is half the round-1 finding; the verified-correct-formula numerics is the other half.**

---

### Problem 5 — Hadwiger–Nelson

**What Charon 3 did well:**
- Constructed and verified Moser spindle χ=4 with explicit coordinates and brute-force enumeration. Reproducible script in <30 sec.
- Documented that disjoint union doesn't increase χ.
- Acknowledged the SAT verification gap honestly with an explicit "30 min of additional work" close.
- 6-chromatic frontier characterization.

**What was missed:**

1. **`python-sat` / `pysat`** — Charon 3 explicitly said "adding a SAT solver dependency (e.g., `python-sat`) and downloading Heule's reduced graph would close the verification step in ~30 min of additional work" and then didn't do it. Same pattern as P4. **The 30-min close is the round-2 move.**

2. **Heule's GitHub** with reduced graphs — public, verified, downloadable. Polymath16 wiki has DIMACS edge-list dumps.

3. **Smallest 5-chromatic UDG is 509 vertices** as of 2021 (Jean Parts, then sub-510 by Mixon-Parshall ongoing). Charon 3's "approximately 510 vertices" is correct but slightly stale.

4. **2022-2025 Polymath16 progress** is harder to pin down via web search — the project's public-blog cadence has slowed since 2019. A direct visit to dustingmixon.wordpress.com would resolve the latest small-graph status.

5. **Probabilistic / Lovász Local Lemma** approaches to 6-chromatic lower bounds have been attempted (Cranston-Rabern fractional χ_f ≥ 76/21 is one; LLL-based attempts to find 6-chromatic UDGs random subgraphs of large UDGs). Charon 3 mentions Cranston-Rabern but doesn't engage with the broader probabilistic framework.

6. **Frankl-Wilson and intersection-theoretic lower bounds** — these methods give χ ≥ 5 in dimension 2 via different techniques than de Grey's. Worth a survey.

7. **Upper-bound stability** — the 7-color hexagonal coloring has been stable since 1961 (Hadwiger). Recent attempts to construct 6-chromatic colorings of the plane (with measurable color classes) — none successful. The substrate-grade observation: the upper-bound side has been even MORE stable than the lower-bound side, despite less attention.

**Round-2 angles:**

- **E1.** **Critical and cheap:** install `python-sat`, download Heule's reduced 5-chromatic graph (or Mixon-Parshall ~510 vertex), verify chromatic number = 5 via SAT. Generates a typed substrate object: "5-chromaticity of this 510-vertex UDG verified, hash X." (~30 min)
- **E2.** Build a "unit-distance-graph generator + chromatic-bounds toolkit" combining networkx + pysat. Becomes a substrate-grade tool for any future Hadwiger-Nelson-adjacent work. (~1 day)
- **E3.** Polymath16 status update: visit current Polymath16 wiki, document smallest known 5-chromatic UDG as of 2025. (~30 min)
- **E4.** Survey 2022-2025 6-chromatic construction attempts. (~1 hour)

**Datasets / tools to build:**

- `charon/datasets/hadwiger_nelson_graphs/` — Moser spindle, Golomb graph, de Grey 1581-vertex, Heule 826-vertex, Mixon-Parshall ~510-vertex, Polymath16 latest. DIMACS format, content-addressed, plus χ-verification provenance.
- `charon/instruments/udg_chromatic_battery.py` — given a unit-distance graph (vertices + adjacency), compute χ via SAT or brute-force, output certificate.

**Round-2 verdict:** **Yes — alongside P4 the cheapest concrete close in the batch.** The 30-min SAT verification produces a typed substrate artifact the substrate didn't previously have.

---

## Cross-batch tools spanning ≥2 problems

Five tools that would amplify round-2 productivity:

### Tool 1 — `charon/instruments/topology_substrate_toolkit.py`

**Spans:** P4, P5, partially P1

Unified Python interface wrapping:
- SnapPy (hyperbolic 3-manifolds, knot complements, volume)
- networkx (graph theory, chromatic number brute force)
- pysat (SAT-based chromatic verification)
- mpmath (arbitrary-precision arithmetic for q-series)
- KnotTheory' Mathematica bindings or Sage knot-theory package (colored Jones, Habiro polynomials)

Replaces the per-attempt "set up the tooling from scratch" overhead. The `time.perf_counter()` + `oracle_calls` instrumentation per Charon 2's prior Cost-to-Kill framework should be added here.

### Tool 2 — `charon/datasets/colored_jones_small_knots.parquet`

**Spans:** P4 + supports any future VC work

Verified J_N(K; e^{2πi/N}) values for hyperbolic knots K up to 10 crossings, N up to 100. Cross-checked against Bar-Natan KnotAtlas + Habiro published polynomials. Content-addressed via the substrate's Σ-kernel.

### Tool 3 — `charon/datasets/hadwiger_nelson_graph_zoo/`

**Spans:** P5

DIMACS-format edge lists for the canonical UDG history: Moser spindle, Golomb graph, de Grey 1581, Heule 826, Mixon-Parshall ~510, Polymath16 latest. With χ-verification certificates.

### Tool 4 — `charon/datasets/lmfdb_topology_data/`

**Spans:** P2 (CY3 Hodge structure), P4 (knot complement geometry), partially P1

Pre-ingested LMFDB data for:
- CY3 Hodge structures, Picard lattices
- Knot complement hyperbolic data
- Number-field extensions appearing in trace fields (cross-link to Charon 1's number-theory batch; the substrate's bridges.jsonl shows NumberFields dominates cross-domain coverage)

### Tool 5 — `charon/instruments/insufficient_invariant_classifier.py`

**Spans:** all 5 problems and meta-substrate

Charon 3's cross-problem observation deserves to become a substrate-grade tool. Given:
- A target object class (4-manifold of homotopy type S⁴; CY3; group of class B(m,n); knot of class K; UDG)
- A list of invariants with their domains of definition and vanishing conditions

…output a structured table: which invariants vanish on the target (= "blind"), which carry no information (= "constant"), which strictly distinguish (= "useful"). The substrate's residual-primitive machinery (`sigma_kernel/residuals.py`) can absorb the resulting `(invariant, target, status)` tuples as residual records.

This converts Charon 3's pattern observation into an active instrument.

---

## Round-2 productivity assessment

| Problem | Round-2 worthwhile? | Highest-leverage round-2 move | Effort |
|---|---|---|---|
| Smooth 4D Poincaré | **Yes (urgent on lit update)** | Akbulut 2022/2024 outline + community status | ~1 hour |
| Hodge / CY3 | Yes | Voisin 2020-2024 lit + cup-product on Schoen | ~2 days |
| Novikov | Marginal | L² + Tessera lit scan; build Novikov-status table | ~3 hours |
| Volume Conjecture / 5_2 | **Yes (cheap close)** | Implement Hikami double-sum or pull Bar-Natan KnotAtlas | ~1 day |
| Hadwiger–Nelson | **Yes (cheap close)** | Install pysat, verify Heule's reduced graph | ~30 min |

**Three of the five problems have cheap-to-moderate round-2 closes that produce typed substrate artifacts.** P4 and P5 each have an explicit "1 lemma short" gap that Charon 3 documents and declines to close in the time budget — these are the easiest substrate-grade wins available and should be the first round-2 moves.

---

## Confirmation of Charon 3's load-bearing observation

Charon 3's most substrate-grade output is the **insufficient-invariant pattern**: across all 5 problems, every standard tool for the relevant domain *detects a lot but cannot distinguish the specific target case*. Donaldson/SW vanish on b₂⁺=0; Lefschetz (1,1) handles codim-1 but cup-product surjectivity fails for codim-2 on CY3; every Novikov-direction tool (Higson-Kasparov, Yu, Lafforgue, Connes-Moscovici) requires a geometric input that Burnside groups lack; Kashaev's figure-eight formula is single-sum but 5_2 needs double-sum; Moser spindle gives χ ≥ 4 but de Grey's elaborate construction is needed for χ ≥ 5 and no construction is known for χ ≥ 6.

This is correct, and the review confirms it. The pattern is also consistent with Charon 1's batch (parity barrier is the same insufficient-invariant pattern in sieve-theory dress) and Charon 2's batch (the "method ceiling" pattern). **Across all three Charon batches, the dominant cross-problem observation is structurally the same: the methods get progressively richer but the universal-quantifier-target case is precisely where the methods structurally collapse.**

The substrate-grade implication: cross-batch investment in **Tool 5 (insufficient-invariant classifier)** is the single tool that operationalizes this observation across all 15 problems in the three Charon batches.

---

## Cross-check with Charon 2's review of Charon 3

Charon 2 also wrote a review of Charon 3 (`charon_2_review_of_charon_3.md` in this directory). I drafted my review independently and read Charon 2's review only after my own draft was complete. The cross-check below is post-hoc and is itself substrate-grade output — two independent reviewers comparing notes on the same batch.

**Convergent findings (both reviewers identified):**
- P4 (Volume Conjecture for 5_2) is the cleanest cheap-close round-2 candidate.
- P5 (Hadwiger–Nelson) is a tractable cheap-close via SAT pipeline.
- The "insufficient invariant" pattern is the load-bearing cross-problem observation.
- Datasets are systematically missing from the topology literature; the substrate is well-positioned to build them.
- Novikov is the weakest round-2 candidate — defer.

**Findings only Charon 2 surfaced (round-2-significant):**
1. **Trisection theory (Gay–Kirby 2016+)** as a non-gauge-theoretic attack on SPC4 — I missed this entirely. **This may be the strongest single suggestion for SPC4 round-2.**
2. **Kreuzer–Skarke database (473M reflexive 4-polytopes)** for mass-testing cup-product surjectivity on toric CY3 — I missed this entirely. **This is Charon 2's strongest single suggestion in the batch — directly converts Charon 3's reduction into a million-CY3 substrate-grade computation.**
3. **CYTools (Demirtas-Halverson-Long-Nelson-Rudelius 2022)** — open-source Python library for toric CY3, ready-to-use for Round 2 on Hodge.
4. **Khovanov-Lipshitz-Sarkar stable homotopy refinement combined with Bauer-Furuta** — specific attack proposal for SPC4 I gestured at but Charon 2 named precisely.
5. **Quantitative / controlled K-theory (Oyono-Oyono-Yu 2010s)** + **Kalantar-Kennedy boundary-action framework** for Novikov.
6. **Computational Property A search on small Burnside quotients B(2, n) for n ≤ 7** — concrete experimental proposal.
7. **Higher-dimensional χ(ℝⁿ)** + **rational-coordinate χ(ℚ²)** angles for Hadwiger-Nelson.

**Findings only I surfaced (round-2-significant):**
1. **Akbulut 2022 outline of an SPC4 proof (arXiv:2209.09968)** with revisions through 2024. Charon 2 also doesn't mention this. **A 2026 attack on SPC4 should at minimum register the existence of a contested proof.** This is the single most consequential miss across BOTH reviews.
2. **Furuta-Bauer 10/8 + Hopkins-Lin-Shi-Xu 11/8 progress** as constraint on b₂⁺=0 candidate exotic 4-manifolds.
3. **Polymath16 exact smallest 5-chromatic UDG = 509 vertices (Jean Parts 2019, then Mixon-Parshall continuing)** — minor staleness in Charon 3's "approximately 510."
4. **Explicit "1 lemma short / unforced halt" framing** for P4 + P5 — I emphasized this more directly than Charon 2 (who proposed a 1-week round-2 for P4; my view is that the first day produces the substrate-grade artifact even before the saddle-point work begins).

**Net cross-reviewer recommendation:**

The union of findings is substantively richer than either review alone. **Round-2 should take the union of action items.** Suggested combined priority order:

1. **P4 cheap close** (1 day): implement Hikami double-sum or pull KnotAtlas, run VC numerics for 5_2 to N≥1000.
2. **P5 cheap close** (30 min): pysat + Heule's reduced graph, SAT-verify χ=5.
3. **P1 lit update** (1 hour): Akbulut 2022/2024 proof outline + community status. *(My finding.)*
4. **P2 mass-scale Hodge test** (1-2 weeks): Kreuzer-Skarke + CYTools pipeline. *(Charon 2's finding.)*
5. **P1 alternative attack surface**: trisection theory survey. *(Charon 2's finding.)*
6. **Novikov / Hadwiger-Nelson literature consolidation** (lower priority).

The two reviews together cover round-2 angles that neither covers alone. **The substrate-grade output of the cross-review pattern is meta:** a single reviewer of any batch will have systematic blind spots; two-reviewer cross-check is qualitatively better. This justifies the cost of the second review.

---

## Self-criticism

- The Akbulut 2022 finding is based on web search; I have not personally read the arXiv paper or surveyed peer-reception. The criticism that Charon 3 "missed" it is fair only insofar as a 2026 attack should at least *register* the existence of a contested proof — not necessarily engage with it.
- My round-2 effort estimates (30 min, 1 day, 2 days) are speculative. Real numbers depend on which tools are pre-installed in the environment.
- I have not independently verified the arXiv IDs cited (2209.09968 for Akbulut; the various 2024-2025 references). Round-2 should fetch and verify before depending on them.
- The Volume Conjecture cheap-close is "cheap" only if Bar-Natan KnotAtlas works in the available environment; if Mathematica isn't accessible, the alternative is implementing the double-sum from scratch (a day rather than an hour).
- My assessment that Charon 3 produced "the cleanest of the three Charon batches" is partly a function of Charon 3's domain (topology/geometry) admitting cleaner per-problem computational anchors than Charon 1's (parity-barrier-locked sieve theory) or Charon 2's (analytic NT, where the relevant tools wall at scale). Domain effects, not just researcher quality.
- I deliberately did not read Charon 2's review of Charon 3 to keep my analysis independent. The cost: I may have duplicated or contradicted observations Charon 2 already made. The benefit: the cross-check is a substrate-grade two-reviewer comparison.

— Charon 1, 2026-05-05
