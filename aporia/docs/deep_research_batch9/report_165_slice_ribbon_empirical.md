# Deep Research Report #165: Slice-Ribbon Conjecture — Empirical Scan over 13K Knots

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Knot silent island (Batch 9 Tier 1)
**Predecessor:** Batch 1 #3 (knot-silence void, broad framing)

## 1. Problem Statement

The **slice-ribbon conjecture** (Fox 1962, refined by Fox-Milnor 1966): every smoothly slice knot K in S^3 — i.e., one bounding a smooth properly embedded disk D ⊂ B^4 — bounds a *ribbon* disk, a smooth disk in B^4 whose radial Morse function has only index-0 and index-1 critical points (no local maxima with respect to the radius). Equivalently, every slice knot is the boundary of an immersed disk in S^3 with only ribbon self-intersections.

Status: open in general; resolved for several families. Lisca (2007) settled all 2-bridge slice knots are ribbon via lattice obstructions; Greene-Jabuka (2010) extended to 3-stranded pretzel and many alternating cases; Aceto-Castro-Cervantes-McCoy-Park (2020+) cover further families up through 12 crossings.

The specific empirical question this brief targets: **over the 12,965-knot HFK census at `F:\Prometheus\ergon\results\hfk_features.json`, identify the slice subset, determine which members are not yet known to be ribbon, and structurally cluster the residual.** This directly probes the knot structural region per `project_silent_islands` and uses the verb-first framing of `feedback_domains_are_docstrings`: the operation under test is *bounds-a-ribbon-disk*, not the noun *ribbon knot*.

## 2. Literature

- **Fox-Milnor (1962, 1966):** original conjecture and the Alexander-polynomial necessary condition Δ_K(t) = f(t)f(t^{-1}).
- **Casson-Gordon (1978, 1986):** signature-defect obstructions to sliceness; many knots with vanishing Δ killed.
- **Lisca (2007):** 2-bridge slice ⇒ ribbon, via Donaldson diagonalization on double covers.
- **Greene-Jabuka (2010):** pretzel and alternating cases via Heegaard-Floer d-invariants.
- **Ozsváth-Szabó (2003):** τ from HFK is a smooth concordance invariant; τ(K) = 0 is necessary for sliceness.
- **Rasmussen (2010):** s-invariant from Khovanov; independent obstruction.
- **Aceto-Castro-Cervantes-McCoy-Park (2020-2023):** systematic resolution at 11-12 crossings.

## 3. Computational Handle

Sliceness *detection* (necessary conditions, all fast on existing data):
- τ(K) = 0 — already in `f2_tau` field of the HFK census.
- Alexander polynomial Fox-Milnor factorization — derivable from `f4_total_rank` plus polynomial reconstruction.
- Casson-Gordon signature jumps — computable from Seifert form via SnapPy.
- Rasmussen s = 0 — Khovanov via KnotJob (already installed per Ergon inventory).

Ribbon-ness *verification* is harder and asymmetric: a positive ribbon disk is exhibited by explicit band moves; absence is not provable by these tools alone, only "not found by current search budget." KnotJob's automated band-presentation search and Sage's `sage.knots` ribbon-construction routines are the workhorses.

The 12,965-row HFK census makes Step-1 filtering near-instantaneous; the ribbon search is the budget-dominant step.

## 4. Test Design

**Step 1.** Filter `hfk_features.json` for τ = 0 candidates. Expected ~2,000-3,000 rows. Cross-filter against Khovanov s = 0 from KnotJob, then Fox-Milnor factor check on the Alexander polynomial. Expected slice candidate set: ~150-400 knots.

**Step 2.** Cross-reference to KnotInfo's known-slice and known-ribbon columns. Partition the slice set into (a) known-ribbon, (b) known-slice-not-yet-ribbon (the target set), (c) status-unknown sliceness.

**Step 3.** For each member of (b), run automated ribbon search: Sage `Knot.is_ribbon()` heuristic, KnotJob band-search, genus-filtration descent. Time-budget each at 2 minutes wall-clock.

**Step 4.** Structural-region clustering: feed the (b) set's HFK signature vector (f1_seifert_genus, f4_total_rank, f7_rank_width, f9_max_betti, plus τ=0, s=0 fixed) into a k-means / DBSCAN cluster against the broader census. Test whether resistant cases cluster with hyperbolic vs torus knots, with high-genus vs low-genus, or with specific 2-bridge factor structure.

## 5. Falsification

- **(a) Confirmation:** all (b)-set members admit a ribbon disk under Step-3 search → empirical slice-ribbon validation at 13K-knot scale; report ribbon-disk catalog.
- **(b) Hard residual:** ≥1 slice knot resists all ribbon attempts at 2-min budget AND at extended 30-min budget → flagged as tooling-or-conjecture frontier case. Almost certainly a search failure, but worth explicit follow-up via `project_techne` for a stronger ribbon-construction tool.
- **(c) Structural signature:** the resistant set clusters non-randomly in HFK feature space (silhouette > 0.4, permutation-null p < 0.01 over 1000 shuffles) → publishable signal: "harder-to-prove-ribbon" has measurable structure in Heegaard-Floer coordinates. Feeds directly into the unified tensor's knot region per `feedback_tensor_first`.
- **Null sanity:** apply identical clustering to a random τ=0 subset of equal size; resistant-set cluster quality must exceed null by ≥2σ to count as signal.

## 6. Budget

Ergon ~6 hours total. HFK / Khovanov / Fox-Milnor filter on existing 13K-knot data ~1h (single Python pass over `hfk_features.json` + KnotJob batch). Ribbon-construction attempts via Sage + KnotJob ~3h (worst case 400 knots × 2 min, parallelizable across 6 cores). Structural-region clustering + permutation null ~1h. Writeup + jsonl emission to `ergon/results/slice_ribbon_scan.jsonl` ~1h. SnapPy + sage.knots + KnotJob already installed per Ergon inventory; no new tooling.

## 7. Expected Outcome

Prior: confirmation outcome (a) is most likely — every slice knot in the census admits a ribbon disk under reasonable search budget, replicating the 11-crossing prior literature at the 13K scale and extending it. The *valuable* secondary outcome is (c): structural signature for resistant cases gives the knot region of the tensor its first internal stratification beyond crossing number and genus. Per `project_silent_islands`, the knot front is currently isolated — knot invariants do not couple measurably to NF, genus-2, or modular-form regions. A well-defined "ribbon-hardness" coordinate is a candidate first bridge: it is a property the knot shares with its Khovanov / HFK environment, and Khovanov has known links to category O and Soergel bimodules that *do* couple. Direct contribution to closing the knot silent island.

**Word count: 798**
