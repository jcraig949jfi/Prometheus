
[claude]

Layer 0: Baseline Sanity (Before Any Embedding)
Test 0.1 — Truncation Collision Rate
Take 10,000 LMFDB elliptic curves. Compute all pairwise Euclidean distances in first-50-prime coefficient space. Count pairs within distance thresholds [0.01, 0.1, 1.0, 5.0]. Compare to the expected collision rate if vectors were drawn uniformly from the observed range. If observed collision rate isn't significantly lower than random baseline at d < 1.0, the representation doesn't discriminate.
Failure condition: collision rate at d < 1.0 is within 2 standard deviations of random baseline.
Test 0.2 — Isogeny Class Coherence
Curves in the same isogeny class have the same L-function by definition. Their coefficient vectors must be identical or within floating-point precision. Any divergence is a data ingest bug, not an interesting result. This test must pass perfectly before anything else proceeds.
Failure condition: any pair of isogenous curves has coefficient distance > 1e-6.
Test 0.3 — Trivial Invariant Dominance
Build a logistic regression predicting "are these two objects isogenous?" using only their coefficient vectors. Then build a second model using only (conductor_A, conductor_B, level_A, level_B). If the trivial invariant model has R² within 5% of the coefficient model, your coefficient vectors are mainly encoding conductor, not deep arithmetic structure. The embedding will cluster by conductor, not by correspondence.
Failure condition: the trivial invariant model explains >90% of the variance the coefficient model explains.

Layer 1: Metric Validity Tests
Test 1.1 — Separability
Known non-corresponding objects with different L-functions must be farther apart than known corresponding objects. Take 100 modularity theorem pairs (distance should be ~0) and 100 provably non-corresponding pairs with similar conductors. The distributions must not overlap. If they do, the metric doesn't separate correspondence from non-correspondence.
Failure condition: distributions overlap at >10% of their mass.
Test 1.2 — The Metric Beats Chance
Randomly shuffle correspondence labels across 1,000 objects. Compute mean distance between shuffled "pairs" vs. true pairs. The true pairs must be significantly closer (p < 0.001, Bonferroni corrected). If shuffled pairs look as close as true pairs, your metric is measuring noise.
Failure condition: Mann-Whitney U test on true vs. shuffled pair distances fails to reject null at p < 0.001.
Test 1.3 — Conductor Conditioning
Within a fixed conductor stratum, is there residual clustering structure? Take all curves with conductor between 100 and 200. Cluster them by coefficient vector. Do the resulting clusters correspond to anything mathematically meaningful beyond "similar conductor"? If clusters dissolve into noise after conditioning on conductor, the metric is a conductor proxy.
Failure condition: no cluster within a conductor stratum has purity > 0.7 by any known invariant.

Layer 2: Embedding Tests
Test 2.1 — The Trivial Baseline
Before building any spectral embedding, run k-NN search directly in the original 50-dimensional coefficient space. Record recovery rate on held-out known modularity pairs. Then run the full spectral embedding pipeline. If embedding recovery rate isn't at least 5 percentage points higher than raw k-NN, the embedding is adding noise, not signal. Spectral embedding that loses information relative to the raw space is strictly worse than the raw space.
Failure condition: spectral embedding recovery rate ≤ raw k-NN recovery rate.
Test 2.2 — Permutation Invariance
Randomly permute the known bridge assignments (shuffle which curve corresponds to which modular form). Re-run the full embedding. If the permuted embedding looks structurally similar to the true embedding (similar cluster count, similar curvature distribution, similar recovery rate on the shuffled labels), then the embedding structure is not coming from the correspondence information — it's coming from the coefficient geometry alone. That means your embedding "works" whether your ground truth is real or fake.
Failure condition: permuted embedding achieves >50% of the recovery rate of the true embedding.
Test 2.3 — Stability Under Perturbation
Add 10% new objects, re-embed. Measure how much existing coordinates shift. If the embedding is globally unstable under 10% data addition, it cannot be the basis of a discovery system — every new data ingestion would invalidate previous candidate discoveries.
Failure condition: mean coordinate shift of existing objects exceeds 20% of the embedding diameter.
Test 2.4 — Dimensionality Saturation
Run the embedding at 2, 5, 10, 20, 50 dimensions. Plot recovery rate vs. dimension. If recovery rate saturates at 2 dimensions, the meaningful structure is extremely low-dimensional. If it never saturates, you don't have a stable embedding. You want a curve that saturates somewhere between 5 and 20 dimensions — that's evidence of real but complex structure.
Failure condition: recovery rate either saturates at ≤2 dimensions or never saturates up to 50.

Layer 3: Discovery Mechanism Tests
Test 3.1 — False Positive Audit
After the embedding stabilizes, extract the top 50 geometrically proximate pairs with no known bridge. Have a domain expert (or cross-check against LMFDB's explicit non-correspondence records) classify each. What fraction are: (a) trivially similar by conductor/level, (b) already known but missing from your database, (c) genuinely interesting candidates? If >80% fall into (a) or (b), the discovery mechanism is finding database gaps and trivial invariants, not Langlands candidates.
Failure condition: <10% of top-50 proximity candidates are genuinely novel after expert review.
Test 3.2 — The Historical Test
Take a Langlands correspondence that was established after 1995 (post-Wiles, so it's in the literature but not ancient). Pretend you don't know it. Does your system rank it as a high-priority candidate? If your system cannot recover recently established bridges as top candidates from proximity alone, it cannot plausibly discover unknown ones.
Failure condition: a held-out post-1995 correspondence does not appear in the top-100 proximity candidates.
Test 3.3 — Trivial Candidate Filter
Every candidate discovery must pass: (a) the pair has different conductors, or (b) if same conductor, they have different Galois groups, or (c) they belong to provably different isogeny classes. If your top candidates are all same-conductor, same-level, same-isogeny-class objects that just happen to be missing a bridge entry in your database, the system is doing data quality control, not mathematical exploration.

Layer 4: The Null Hypothesis Battery
For each core scientific claim, state it, state its null, state the test.
ClaimNull HypothesisKilling TestCoefficient vectors are a meaningful Langlands coordinateClusters reflect conductor/level, not deep structureTest 1.3 — conditioning studyGeometric proximity predicts correspondenceProximity predicts trivial shared invariants onlyTest 3.1 — false positive auditSpectral embedding adds value over raw similarityEmbedding is a lossy compression of the raw signalTest 2.1 — trivial baselineThe landscape is stable enough to support discoveryEmbedding is path-dependent on ingestion orderTest 2.3 — stability under perturbation50 primes is sufficient representationObjects are not discriminated beyond conductor strataTest 0.1 + 0.3 — collision and dominance

The Forcing Principle
Every test here has a binary outcome: it fails or it doesn't. There's no "promising" result, no "worth continuing to investigate." Either the null is rejected at a specified threshold or you return to the design loop before proceeding.
This is what separates TDD from motivated exploration. The tests are written before the code. The thresholds are set before you see the results. You don't get to adjust the threshold after seeing a beautiful embedding.
The truncation collision study is Test 0.1. Run it tomorrow morning before anything else. If it fails, you've saved weeks.

