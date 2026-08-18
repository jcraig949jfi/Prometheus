# Domain Map: Datasets and Tensor Networks
## Separate tensors until bridges emerge

---

## Architecture Principle

Each domain gets its own tensor with its native metric. No forcing
cross-domain distance functions. Bridges are discovered empirically
and live in a separate bridge layer (literally a functor map).

Hubs that appear in multiple domain tensors are alignment points --
they trigger bridge search between those specific domains.

---

## Current Tensors (Data In Hand)

| Domain | Dataset | Objects | Internal Metric | Status |
|--------|---------|---------|----------------|--------|
| **L-functions** | LMFDB + Charon DuckDB | 336K | Coefficient cosine / zero gaps | Explored (Day 1-5) |
| **Integer sequences** | OEIS stripped | 392K | Log-term cosine / property vector | Explored (Day 5) |
| **Formal proofs** | Lean mathlib | 216K decls | Import graph / namespace Jaccard | Explored (Day 5) |
| **Finite groups** | GAP SmallGroups | 97MB raw | TBD (character table similarity) | Cloned, needs extraction |
| **Crystals** | COD sample | 500 | Unit cell ratios | Pilot (silhouette 0.52) |
| **Atomic spectra** | NIST ASD (H) | 1,308 | Energy gaps / quantum numbers | Pilot (needs unfolding) |
| **Relationships** | LMFDB graph | 396K edges | Graph distance | Explored (Day 5) |

## Known Cross-Tensor Bridges

| Bridge | Type | Strength | Finding |
|--------|------|----------|---------|
| OEIS ↔ mathlib | Topological | 5.1x enrichment | Shared sequences predict imports |
| OEIS ↔ mathlib | Geometric | NONE (rho=-0.13) | Distances don't correlate |
| OEIS ↔ properties | Geometric | rho=0.56 | Terms predict mathematical character |
| Operations ↔ imports | Geometric | r=0.27 | Shared methodology predicts proofs |
| LMFDB ↔ OEIS | Exact match | 72 ECs | Coefficient sequences in OEIS |
| LMFDB isogeny ↔ OEIS | Consistent | 17/17 | Isogeny classes match same OEIS |
| Groups ↔ OEIS | Fingerprint | 34 sequences | Group-counting pattern in OEIS |
| Zeros ↔ OEIS | Direct | Floor/ceiling | Zeta zeros are OEIS entries |

## Datasets To Ingest (Priority Order)

### Tier 1: High value, known bridge potential
1. **FindStat** — combinatorial statistics with explicit maps. Pre-digested for bridges.
2. **KnotInfo** — knot invariants. Davies et al. found ML connections. Number theory bridge.
3. **Bilbao Crystallographic Server** — space groups. Connects to group theory tensor.
4. **zbMATH MSC taxonomy** — crawl frontier. Coverage tracker for all of mathematics.
5. **Wikidata math KG** — broad index of mathematical knowledge. Messy but machine-readable.

### Tier 2: Rich structure, moderate effort
6. **House of Graphs** — graph invariants. Intersection of many domains.
7. **ATLAS finite groups** — character tables for simple groups. Landmark points.
8. **CODATA constants** — physical constants with algebraic structure.
9. **DLMF / Wolfram Functions** — special function identities as bridges.
10. **PDG particles** — symmetry groups, quantum numbers. Small but dense.
11. **Algebraic NT archives** — class groups, discriminants. Adjacent to LMFDB.
12. **nLab link structure** — category-theoretic cross-references.
13. **OpenAlex math citations** — citation graph between mathematical fields.
14. **ProofWiki / Metamath** — alternative formalized theorem databases.
15. **NIST ASD** (full) — 100K spectral lines across many elements.
16. **Materials Project** — 150K crystals with computed properties (needs API key).

### Tier 3: Wild bets, high novelty potential
17. **Error-correcting codes** — lattices, groups, combinatorics connections.
18. **BiGG/KEGG reaction networks** — biochemistry as graph/algebra.
19. **Music/tuning databases** — cyclic group decomposition in intervals.
20. **Open problem lists** — cross-reference against structural holes.

## The Self-Directing Loop

```
Ingest structured knowledge
    ↓
Build domain tensor (native metric)
    ↓
Run internal analysis (clusters, holes, topology)
    ↓
Check for hub alignment across tensors
    ↓
Search for bridges at alignment points
    ↓
Verify candidates (TDD pipeline + adversarial agent)
    ↓
Use verified bridges to steer next ingestion
    ↓
(loop)
```

Step 5 (hub alignment) is the attention mechanism: with N tensors,
we have N(N-1)/2 pairwise comparisons. Hubs that appear in multiple
tensors trigger focused bridge search between those specific domains.

Step 7 (adversarial verification) is the immune system: a second
agent whose job is specifically to attack candidate bridges before
they enter the verified tier. The Charon sprint showed why this
matters -- the mean-spacing test killed narratives that 16 mechanism
strips didn't touch.

## What Triggers Bridge Search?

Three signals that two tensors should be compared:
1. **Shared hub structure** — same structural pattern is central in both
2. **Shared vocabulary** — same operation words appear (the r=0.27 finding)
3. **Shared numerical shadow** — same OEIS sequences appear in both domains

The hubs are the alignment points. FORCED_SYMMETRY_BREAK (or its
equivalent) appearing as central in two different domain tensors
means those domains share a structural bottleneck worth investigating.

## What We DON'T Do

- Force cross-domain distance functions
- Merge tensors before bridges are verified
- Assume connections exist because domains are "related"
- Build narratives before measurements
- Skip mean-spacing / normalization checks on any new domain
