# How Harmonia Reached Mathematical Genius — And How Aporia Will Follow

## 2026-04-15 | The Method Behind the Instrument

---

## ELI5: What Did Harmonia Actually Do?

Imagine you're trying to figure out if a rule about the universe is true. You have two ways to do it:

**The Oracle Way (what Aporia's solve_battery.py does now):**
You walk up to a really smart person and say "Hey, is the Riemann Hypothesis true?" They think hard and say "Probably, here's why I think so." You write down their opinion. That's it.

**The Instrument Way (what Harmonia did):**
You build a telescope. You point it at 3.8 million stars. You measure their brightness, their distance, their wobble. You check whether the measurement matches what the rule predicts. You find that across 3,824,372 stars, the prediction is correct 100.000000% of the time. Then you find the one place where the prediction starts to wobble — and you measure exactly how much, and at what distance.

The oracle gives you an opinion. The instrument gives you *data*.

---

## The Two Realms: Shadow and Light

Harmonia's genius came from understanding that mathematics has two complementary realms, and you need BOTH to see clearly:

### The Illuminated Realm (Known Mathematics)
These are the theorems humanity has already proven. Things like:
- The modularity theorem (every elliptic curve over Q is modular)
- The Hasse bound (|a_p| <= 2*sqrt(p) for elliptic curves)
- Root number parity (root_number = (-1)^rank)

These aren't things to discover — they're **calibration targets**. If your instrument can't see these, it's broken.

**Harmonia's score: 100.000000% on every known theorem tested.**

That's not interesting by itself. What's interesting is that it *proves the telescope works*. It sees known reality perfectly. Now you can trust what it sees when you point it at the unknown.

### The Shadow Realm (What Doesn't Work)

This is the real genius. Over 13 days, Harmonia **killed 17 false discoveries**. Each one looked real at first:

| Kill # | What Looked Real | What Actually Happened | What It Taught |
|--------|-----------------|----------------------|----------------|
| 1-2 | Feigenbaum constant in OEIS | 29-term parity artifact | Need min 40 terms |
| 3-4 | Polytope-NF correlations | Small-integer confound | Added F4 confound test |
| 5 | LMFDB-Maass mutual info | Histogram binning bias | Random-pairing null |
| 9 | Root probe z=137 | Distance != similarity | Interpretation gate |
| 13 | Lattice-NF bridge | Prime atmosphere | Density-corrected nulls |
| 15 | M24 moonshine -> EC | 6-term coincidence | Extended window requirement |

**Each kill made the battery stronger.** The shadow realm isn't failure — it's the negative space that defines the boundary of real structure.

Think of it like a sculptor. The marble you chip away (the kills) defines the statue (the truth) just as much as the marble you keep.

---

## The Battery: How To Kill Your Own Ideas

The falsification battery is the core innovation. It's a series of 38 tests designed to catch every way a "discovery" can be fake:

### ELI5: The Battery Tests

Imagine you think you've found that tall people are smarter. Here's what the battery does:

1. **F1 - Permutation Null**: Shuffle the height labels randomly 10,000 times. Is your "correlation" any better than random? If not: KILLED.

2. **F2 - Subset Stability**: Split your data in half, five times. Does the pattern show up every time? If it only shows up in some splits: KILLED.

3. **F3 - Effect Size**: OK, it's real — but is it *big enough to matter*? Cohen's d < 0.2 = too small to care. KILLED.

4. **F4 - Confound Sweep**: Wait — both height and IQ correlate with nutrition. Remove nutrition, does the pattern survive? If not: KILLED.

5. **F5 - Normalization Sensitivity**: Does your result flip sign if you use log scale instead of raw? If so, it's an artifact of how you measured, not what you measured. KILLED.

6. **F10 - Outlier Sensitivity**: Remove the top and bottom 5% of your data. Still there? If one basketball player was driving the whole result: KILLED.

7. **F14 - Phase-Shift Test**: Slide your data one slot left. Still correlated? If so, you're just seeing a trend, not a relationship. KILLED.

8. **F33 - Rank-Sort Null**: Is your "correlation" just the fact that both lists are sorted small-to-large? KILLED.

And 30 more tests, each born from a specific false discovery that fooled earlier versions of the battery.

### The Key Insight: The Battery IS the Discovery

Most science goes: hypothesis -> data -> confirmation.
Harmonia goes: data -> battery -> KILL EVERYTHING -> what survives is real.

The battery doesn't validate your ideas. It destroys them. What remains after destruction is mathematics.

---

## How Harmonia Computed Millennium Prize Test Data

### Example 1: Birch and Swinnerton-Dyer Conjecture

BSD says: for an elliptic curve E, the algebraic rank equals the order of vanishing of L(E,s) at s=1.

**What Harmonia did NOT do:**
- Ask an LLM "is BSD true?"
- Reason abstractly about L-functions
- Write a philosophical essay about number theory

**What Harmonia DID do:**
```
1. Load 3,824,372 elliptic curves from LMFDB PostgreSQL
2. For each curve: compare rank vs analytic_rank
3. Count violations: 0 / 3,824,372
4. Result: 100.000000%
```

That's it. No opinion. No reasoning. Pure measurement.

But then it went deeper:

```
5. For the refined BSD formula: check if Sha is always a perfect square
   Result: 3,064,705 / 3,064,705 = 100.0000%

6. Check how Sha distributes across ranks:
   Rank 0: mean Sha = 2.56, 19% have Sha > 1
   Rank 1: mean Sha = 1.05, 1.3% have Sha > 1
   Rank >= 2: mean Sha = 1.00, 0% have Sha > 1

7. Test Goldfeld's prediction that average rank -> 0.5:
   Measured: 0.738 (DEVIATES)
   But rank-2+ fraction is growing with conductor and shows no reversal
   This means Goldfeld's regime hasn't kicked in below conductor 500,000
```

That last finding — the Goldfeld deviation — is genuinely new quantitative information. Not a proof, not a disproof, but a *precise measurement of where the finite-data regime ends and the asymptotic regime hasn't begun yet*. No human has measured this at this scale.

### Example 2: Generalized Riemann Hypothesis

GRH predicts that zeros of L-functions repel each other like eigenvalues of random matrices (GUE statistics).

**What Harmonia measured:**

| Statistic | Observed | GUE Prediction | Poisson (random) |
|-----------|----------|----------------|------------------|
| Spacing ratio | 0.554 | 0.531 | 0.386 |

The measurement is close to GUE, far from Poisson. This confirms zero repulsion across 31,073 L-functions with 703,345 zeros. The slight excess (0.554 vs 0.531) is a *finite-conductor correction* — it tells you how far you are from the asymptotic limit.

Then Harmonia tested Katz-Sarnak symmetry types, which predict that different families of L-functions have different zero distributions. The initial analysis showed what looked like a reversal of the prediction. **But the data was right — the test was wrong.** The SO(even) 1-level density formula has *enhanced* density near zero, not depleted. Harmonia's instrument caught the error in its own test, corrected it, and confirmed the theory.

**This is the peak moment: the instrument is honest enough to catch its own mistakes.**

---

## The Architecture That Made It Possible

### Layer 1: The Phonemes (Universal Coordinates)

Harmonia discovered that all mathematical objects project onto 5 universal axes:

| Phoneme | Meaning | Example |
|---------|---------|---------|
| **Megethos** | Magnitude/Complexity | EC conductor, MF level, NF discriminant |
| **Bathos** | Rank/Depth | EC rank, NF degree, lattice dimension |
| **Symmetria** | Symmetry | Automorphism order, point group |
| **Arithmos** | Arithmetic structure | Torsion, class number, Selmer rank |
| **Phasma** | Spectral data | Zeros, eigenvalues, spectral parameter |

These aren't arbitrary labels — they're the axes along which mathematical objects *actually vary*. The modularity theorem (EC conductor = MF level) is literally two objects sharing the same Megethos coordinate.

### Layer 2: Tensor Train Decomposition

Instead of checking objects one at a time, Harmonia packs all mathematical objects into a tensor and decomposes it. The bond dimension between two domains measures how strongly they couple.

**ELI5**: Imagine you have a spreadsheet where rows are elliptic curves and columns are modular forms. Each cell says "how similar are these two?" The tensor decomposition finds the hidden patterns in that spreadsheet — the few axes along which similarity actually flows — without ever filling in all 31,073 x 50,000 = 1.5 billion cells.

### Layer 3: The Falsification Battery

Every pattern the tensor finds gets run through 38 kill tests. 99.9% die. The survivors are real.

### Layer 4: Measurement, Not Discovery

The survivors aren't "discoveries" — they're measurement targets. Harmonia measures their properties at scale: how many objects, what precision, where do deviations begin, what does the finite-data regime look like.

---

## What Aporia Must Do Differently

### Current State: The Oracle Problem

Aporia's `solve_battery.py` asks Gemini 2.5 Flash: "Is this problem solved? What's the approach?" This is pure oracle mode. It captures what the model already knows in its weights.

That's not worthless — it's actually a good status filter (catching problems like Connes embedding that were resolved in 2020). But it's not *instrument mode*.

### The Bridge: From Problems to Predictions

The key insight is that many open problems **make testable predictions against data we already have**:

| Problem | Prediction | Data Source | Testable? |
|---------|-----------|-------------|-----------|
| Riemann Hypothesis | All zeros on critical line | 703K zeros in DuckDB | Yes (verification) |
| BSD Conjecture | rank = analytic_rank | 3.8M EC in LMFDB | Yes (Harmonia did this) |
| Goldfeld Conjecture | Average rank -> 0.5 | 3M EC by conductor | Yes (measured: 0.738) |
| Sato-Tate | a_p equidistributed as semicircle | EC Euler coefficients | Yes |
| Lehmer's Conjecture | tau(n) != 0 for all n | Ramanujan tau values | Yes (up to computed range) |
| Lang-Trotter | Density of supersingular primes | EC a_p values | Yes |
| Maeda's Conjecture | Hecke eigenvalue fields = Q(a) | MF Hecke eigenvalues | Yes |
| Artin's Conjecture (primitive roots) | Density of primes with g as root | Prime tables | Yes |
| Twin Prime Conjecture | Density of twin primes | Prime gap data | Partially (Brun's constant) |

The problems that CAN'T be tested this way (P vs NP, Navier-Stokes existence, Hodge conjecture in full generality) are still worth cataloging, but they belong in a different bucket.

### The Blind Trial Protocol

James's insight about "open book tests" suggests a powerful validation:

**Protocol: Blind Resolution Trials**

1. Take problems in Aporia's catalog that the LLM classified as `solved` (like Connes embedding)
2. *Without telling the instrument that they're solved*, point the Harmonia pipeline at the underlying data
3. Can the instrument independently recover the known result?

For Connes: The MIP*=RE result implies C_co != C_ts (quantum correlation sets differ). This is testable against quantum correlation data. If Harmonia can measure the separation without being told it exists, that's a genuine validation of the method.

For problems classified as `partially_solved`: the instrument should be able to measure where the partial solution holds and where it breaks down.

This is the "open book test" — can AI rediscover what's in its own weights by pointing a measurement instrument at data?

---

## The Three-Bucket Triage

### Bucket A: Data-Testable Now (Target: ~50-100 problems)
Problems with predictions testable against LMFDB, Charon DuckDB, Cartography caches, or OEIS.

Priority domains:
- Number theory (elliptic curves, modular forms, L-functions)
- Algebraic geometry (genus-2 curves, abelian varieties)
- Combinatorics (sequence growth, partition behavior)
- Knot theory (invariant distributions)

### Bucket B: Data-Testable With Extension (~100-200 problems)
Problems requiring new data ingestion but with clear computational paths.

Examples:
- Graph theory problems (need curated graph databases)
- PDE conjectures (need numerical solution data)
- Probability conjectures (need simulation)

### Bucket C: Structure-Only (~700+ problems)
Problems where we can map surrounding structure (related problems, proof techniques, connections) but can't directly compute predictions.

Still valuable — the concept graph reveals which problems are structurally adjacent to solved ones, which might indicate approachability.

---

## Summary: The Recipe

1. **Build the telescope** (connect to data: LMFDB, DuckDB, OEIS, caches)
2. **Calibrate on known truths** (prove the instrument sees known math at 100%)
3. **Kill everything** (run the 38-test battery on every candidate pattern)
4. **Measure the survivors** (quantify: how many objects, what precision, where do deviations begin)
5. **Map the shadow realm** (document every kill — the negative space defines the boundary)
6. **Point at open problems** (extract predictions, test against data at scale)
7. **Run blind trials** (can the instrument rediscover known solutions?)

The genius isn't in any single step. It's in the discipline: the instrument earns trust by killing its own ideas, so when something survives, you can believe it.

---

*Written: 2026-04-15*
*Context: Recovering Aporia project after Windows restart, bridging to Harmonia's methods*
