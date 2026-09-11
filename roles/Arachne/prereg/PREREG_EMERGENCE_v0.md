# Preregistration: WHAT STRUCTURE IN THE JUNE FABRIC WOULD BE SURPRISING UNDER CHEAPER GENERATIVE EXPLANATIONS? (v0, frozen 2026-09-11)

Operator ruling 2026-09-11 s4: the founding falsifiers (partition,
ablation, degree-preserving null) plus stronger nulls the topology
demands. Committed before any statistic is read. The only quantities
read before freezing are the graph facts and eligibility counts below.
Specimen: roles/Arachne/archive/run_2026-06-04/ at its MANIFEST hashes;
both segments; no new crawl data.

## The graph

- 21,209 typed directed edges collapse to G = 16,583 undirected simple
  pairs over 5,621 nodes (110 pairs carry more than one op; the rest of
  the difference is reverse duplicates). No self loops.
- Node landscape = id prefix: oeis 3,043; groups 637; knots 634; mathlib
  612; lmfdb 439; algolib 256. Cross-landscape pairs: 1,887 (rosetta
  shares_concept 1,870 typed edges and computes 57).
- 157 connected components; the giant has 3,829 nodes (68 percent).
- Ops by kind, from the adapters' code (this classification is fixed
  here): EQUIVALENCE relations (two nodes linked iff they share a value):
  shares_prefix (same first 3 terms; 5,850 pairs, 132 classes, largest
  540), same_conductor (1,502; 47; 39), same_determinant (2,324; 71; 15),
  same_order (2,762; 43; 77), same_exponent (142; 20; 18), isogenous
  (255; 115; 6), same_crossing (14; 1), same_n_conjugacy (12; 4).
  RELATIONAL (a real directed structure copied from a source): mathlib
  uses (998 typed), algolib calls (701). LEXICAL: shares_concept (1,870;
  token co-occurrence, homonym-prone). VERIFIED: computes (57).
  TOLERANCE: similar_growth (273; growth within 0.05 and same
  monotonicity; not transitive; treated as relational).
- The table adapters expand with `SELECT ... WHERE col = value LIMIT n`
  and NO ORDER BY (n = 6..8): every expansion inside a class tends to
  return the same physical-first members. This is a generative mechanism
  of the ADAPTER, not of the crawler, and it predicts hubs inside classes.
  Measured before freezing as "hub-8 share" (fraction of an op's class
  edges incident to the 8 highest-degree nodes of the class): isogenous
  1.000, same_crossing 1.000, same_exponent 1.000, same_n_conjugacy
  1.000, same_conductor 0.961, same_determinant 0.961, same_order 0.782,
  shares_prefix 0.432.

## The cheaper generative explanations, ordered from cheapest

E0  The fabric is the union of: sampled subsets of invariant-class
    cliques (equivalence ops), two dependency graphs copied from their
    sources (uses, calls), a lexical token join (shares_concept), and 57
    computation-verified bridges. Nothing in it was produced by
    crawler-crawler interaction.
E1  E0 plus the adapter's LIMIT-n mechanics: within a class, edges
    concentrate on a fixed few members (hubs).
Anything not explained by E0/E1 is candidate crawler-level structure.

## Nulls (each preserves more than the last)

N1  GLOBAL DEGREE-PRESERVING: double-edge swaps over all of G, 5*m
    swaps, 10 seeds. Destroys landscape blocks and classes. The founding
    doc's literal null (s4 c). Expected to be trivially rejected because
    within-landscape edges dominate; reported for the record.
N2  BLOCK-CONSTRAINED: double-edge swaps inside each landscape's induced
    subgraph separately (5*m_L swaps each), and cross-landscape pairs
    rewired among themselves preserving every node's cross-degree and the
    landscape-pair counts. Preserves degrees and the landscape table of
    contents; destroys classes.
N3  CLASS-CONSTRAINED (E0): for each equivalence op, classes = connected
    components of that op's pairs; the op's pairs are re-drawn uniformly
    among distinct pairs inside each class, same count per class; the
    edge keeps its crawler label. Relational, lexical, verified and
    tolerance pairs are kept as observed. Preserves E0 exactly; destroys
    the crawler's and the adapter's specific choices.
N4  ADAPTER-MECHANICS (E1): as N3, but each class's edges are re-drawn
    as a star toward the class's k = min(8, class size) highest-degree
    observed members (each non-hub node draws its observed degree's worth
    of edges toward hubs uniformly; hub-hub pairs allowed). Preserves E0
    plus the LIMIT-n concentration.
10 samples per null (N1 and N2 are the slow ones; 5*m swaps is stated
as the mixing budget). A statistic is SURPRISING under a null when the
observed value lies outside the null samples' [min, max] (an empirical
one-in-ten-or-better event per side); the percentile is reported.

## Statistics (frozen)

S1  Louvain modularity (resolution 1, seed 0) of G.
S2  NMI and ARI of the Louvain partition vs landscape labels (founding
    condition a at the landscape level). Attainable [0,1].
S3  Within-landscape: for each landscape with an equivalence op, NMI of
    the Louvain partition of that landscape's subgraph vs the class labels
    of its dominant equivalence op (nodes with no class: their own
    singleton). Founding condition (a) at the invariant level: organization
    that cuts ACROSS classes reads as NMI < 0.5; recovering the classes
    reads as NMI >= 0.5.
S4  Transitivity and average clustering of G.
S5  Giant component fraction and component count.
S6  Bridge redundancy (the June holdout judge re-implemented on the frozen
    graph, all 57 computes edges, 8 random same-landscape comparators per
    bridge, seed 12345, BFS bound 8): fraction of bridges whose true
    endpoint is closer than the median comparator with the bridge removed.
    The June value was 0.088 on a 60-bridge sample.
S7  Cross-landscape concentration: over pairs of Louvain communities
    (A, B) in different landscapes, the maximum and the Gini of the
    number of cross pairs between them.
S8  n = 2 EMERGENCE (founding doc s4: "two crawlers producing structure
    neither produces alone"): the number of triangles in G whose three
    edges carry at least two distinct crawler labels (mixed triangles)
    and the fraction of all triangles that are mixed.
S9  Hub-8 share per equivalence op (the E1 signature), observed vs N3.

Which nulls each statistic is read against: S1, S2, S4, S5 vs N1, N2, N3,
N4; S3 vs N3, N4; S6 vs N2, N3; S7 vs N2 (cross-edge rewiring); S8 vs N3,
N4; S9 vs N3 (by construction N4 reproduces it).

## Ablation (founding condition b)

Eligible: the 73 crawlers with >= 50 typed edges (of 101 crawler ids;
rosetta and operational are weavers, ablated separately as two extra
units). For each unit: remove its pairs (a pair whose every op belongs
to the unit is removed; a pair shared with another crawler stays),
recompute Louvain (seed 0) on the remainder, and measure ARI between
the full partition and the ablated partition on the nodes that remain
with degree >= 1. Null for each unit: 10 random removals of the same
number of pairs drawn from the same landscape mix. A unit is
LOAD-BEARING if its ARI is below every one of its 10 null draws.
Founding condition (b) "stable under ablation of any single crawler" is
read as: number of load-bearing units = 0 -> STABLE; otherwise the units
are listed and (b) reads NOT_STABLE, with the caveat that the largest
crawler (oeis-0-4, 3,666 typed edges, 17 percent) removes a sixth of the
graph.

## Readings (frozen ladder)

(a) PARTITION: TABLE_OF_CONTENTS if S2 NMI >= 0.5 AND every S3 NMI >= 0.5;
    CROSS_CUTTING if S2 NMI < 0.5 OR any S3 NMI < 0.5 (named);
    INDETERMINATE if fewer than 3 landscapes have an equivalence op with
    >= 20 classes (they do: 5 do).
(b) ABLATION: STABLE / NOT_STABLE as above.
(c) NULLS: for each statistic, the list of nulls under which it is
    surprising. The reading: NOTHING_BEYOND_E0 if no statistic among
    S1, S3, S4, S6, S7, S8 is surprising under N3; NOTHING_BEYOND_E1 if
    some are surprising under N3 but none under N4; CANDIDATE_STRUCTURE
    if any of S1, S3, S4, S6, S7, S8 is surprising under N4 (named, with
    the direction).
EMERGENCE (founding doc s4, all three): earns the word only if (a) reads
CROSS_CUTTING AND (b) reads STABLE AND (c) reads CANDIDATE_STRUCTURE.
Any other combination: the specific reading is reported and the word is
not used.

## Positive and cheat controls for the instruments (run first)

- Partition instrument: a planted 2-block graph (positive) must give
  NMI vs blocks > 0.9; the same graph with block labels shuffled
  (negative) must give NMI < 0.1; a planted community injected into a
  copy of the real G (cheat: 60 fresh nodes as a clique attached by one
  edge) must be recovered as one community.
- Null instrument: every null sample must preserve what it claims
  (degree sequence for N1/N2; class edge counts for N3/N4; cross-degree
  and landscape-pair counts for N2) -- asserted on every sample.
- Ablation instrument: removing a unit that owns no pairs must give ARI
  = 1 (negative); removing a planted clique's owner must reduce ARI
  (positive).
Statistics are not read until the controls pass; the control results
ship with the readout.
