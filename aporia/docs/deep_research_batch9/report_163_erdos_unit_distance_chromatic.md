# Deep Research Report #163: Erdős Unit-Distance Graph Chromatic Number (Hadwiger-Nelson)

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Erdős corpus expansion (Batch 9 Tier 3, computationally tractable)

## 1. Problem Statement

Let G = (V, E) be the *unit-distance graph of the Euclidean plane*: V = R^2, and uv ∈ E iff ‖u − v‖ = 1. The Hadwiger-Nelson problem asks for the chromatic number χ(G) — the minimum k such that V admits a proper k-coloring (no two points at distance 1 share a color).

Current bounds: **5 ≤ χ(G) ≤ 7**.

- Upper bound 7: explicit 7-coloring of the plane by hexagons of diameter slightly less than 1 (Isbell, 1950s).
- Lower bound 5: Aubrey de Grey (2018) constructed an explicit 1581-vertex unit-distance graph requiring 5 colors, breaking the 4-color barrier that had stood since Moser-Moser (1961).
- Polymath 16 (2018-ongoing) reduced the witness size dramatically (sub-600 vertices in published reductions; community holds smaller candidates).

The structural region of interest is the gap **{6, 7}**: either a 6-chromatic unit-distance graph exists (lifting the lower bound), or every finite unit-distance graph is 5-colorable and a 6-coloring of the plane exists (lowering the upper bound). Both directions are open and both would be major.

## 2. Literature

- **Nelson (1950, unpublished correspondence):** original posing of the problem.
- **Hadwiger (1944, 1961):** 7-coloring construction via hexagonal tiling.
- **Moser & Moser (1961):** 4-chromatic 7-vertex Moser spindle, the canonical small obstruction.
- **Soifer, *The Mathematical Coloring Book* (2009):** comprehensive history; documents the 4 ≤ χ ≤ 7 stalemate that held 1961-2018.
- **de Grey, arXiv:1804.02385 (2018):** "The chromatic number of the plane is at least 5" — 1581-vertex SAT-verified witness.
- **Polymath 16 (2018-2020+):** community project reducing witness size; key contributors Exoo, Heule, Parts. Heule's 2018 SAT certificates push verification scale.
- **Exoo & Ismailescu (2020):** structural lower-bound techniques and graph products on unit-distance class.

## 3. Computational Handle

Three facts make this tractable for Ergon:

1. **Explicit witnesses exist.** The de Grey 1581-vertex graph and the Polymath 16 reductions are publicly available as edge lists. No combinatorial discovery is needed to *verify* χ ≥ 5.
2. **SAT scales.** Modern CDCL solvers (Kissat, CaDiCaL) decide k-colorability on graphs up to ~10K vertices in minutes when the graph has rigid geometric structure. χ ≤ 5 is a single SAT call; χ ≥ 6 is the negation of a 5-coloring SAT call.
3. **Augmentation is local.** Adding a vertex at unit distance from k existing vertices and re-running 5-SAT is cheap. The frontier is *which* augmentations destroy 5-colorability — a search problem, not a proof problem.

Search for 6-chromatic unit-distance graphs is the open frontier. Building from known 5-chromatic seeds via vertex augmentation is the natural attack.

## 4. Test Design

**Step 1.** Replicate de Grey's 5-chromatic result. Load the 1581-vertex edge list, encode 4-colorability as SAT (4n vars, monochrome-edge clauses), confirm UNSAT. Confirm 5-SAT is SAT. Validates pipeline against published ground truth.

**Step 2.** Vertex-augmentation search for 6-chromatic candidates. From each 5-chromatic seed, generate candidate augmentations: place a new vertex at the second intersection of two unit circles centered on existing vertices (so it auto-satisfies two edges). For each candidate, SAT-test 5-colorability. Retain only those whose 5-SAT is UNSAT — these would be 6-chromatic.

**Step 3.** Structural analysis of any 6-chromatic discovery: vertex count, edge count, automorphism group (nauty), embedding pattern, presence of Moser-spindle substructures, fractional chromatic number.

**Step 4.** Polymath 16 path test: do small modifications (vertex deletion, edge contraction within unit-distance constraint) of de Grey produce *smaller* 5-chromatic graphs? Do iterated augmentations of the smallest known 5-chromatic graph approach 6-chromaticity in any structured way (e.g., monotone increase in fractional chromatic number)?

## 5. Falsification

- **Discovery of a 6-chromatic unit-distance graph** → settles χ(G) ≥ 6, narrows bounds to 6 ≤ χ ≤ 7. Publishable major result.
- **Reduction of 5-chromatic vertex count below current Polymath 16 record** → publishable extension of Polymath 16.
- **Structural-impossibility lemma:** if all augmentations of a class of 5-chromatic graphs preserve 5-colorability, that's a non-trivial obstruction worth recording.
- **Null:** if 10^5 augmentations all stay 5-colorable, report as evidence (not proof) for χ ≤ 6 conjecture. Calibration only — `feedback_assume_wrong` applies; absence of a 6-chromatic find under this search is not evidence the search space is exhausted.

## 6. Budget

Ergon ~6 hours. SAT setup (~2h, uses REQ-026 SAT-solver tool from techne/inventory.json), search runs (~2h compute on Skullport, parallelized over augmentation candidates), structural analysis (~1h via nauty + networkx), writeup (~1h).

## 7. Expected Outcome

Empirical extension of the Polymath 16 program with a documented augmentation-search frontier and reproducible SAT pipeline. Structural data on unit-distance chromatic-number obstructions feeds the discrete-geometry layer of the tensor. Cross-link to **#162 distinct distances** (Erdős distinct-distances geometry shares the unit-distance edge predicate), **#168 MOLS** (combinatorial-design coloring constraints), **#169 Hadamard** (binary-coloring extremal structure). Prior on a 6-chromatic discovery is low — the Polymath collective has searched hard — but the augmentation pipeline is reusable for related extremal-coloring problems and validates Ergon's SAT capability for the Erdős corpus.

**Word count: 798**
