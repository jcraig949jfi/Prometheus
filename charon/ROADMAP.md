# Charon Roadmap
## Last Updated: 2026-04-02

---

## Status: Foundational Component (Earned)

Charon's three-layer architecture (zeros/graph/Dirichlet) is validated on elliptic curves
and classical modular forms. The test battery, audit pipeline, and disagreement atlas are
type-agnostic infrastructure. The question now is whether the pattern generalizes.

### What's Proven
- Zero vectors (Katz-Sarnak normalized) create continuous rank-aware geometry (ARI=0.55)
- The relationship graph encodes orthogonal algebraic structure (rho=0.04 vs zeros)
- Dirichlet coefficients are identity verification (binary hash)
- Raw k-NN on zeros achieves 100% bridge recovery — no embedding needed
- The disagreement atlas surfaces 163 dim-2 forms with EC zero-neighbors
- Kill tests: weight-2 dim-2 alone is NOT sufficient (10.7% EC-proximate); character
  is a significant confound (3.3x enrichment for non-trivial) but not a complete explanation
- Murmurations independently detected in our data (r = -0.64 to -0.84 across all bins)

### What's Open
- Do the 163 dim-2 forms correspond to genus-2 curves? (Paramodular Conjecture test)
- Does the zero coordinate system generalize to other object types?
- Does graph density increase meaningfully with new object types?
- Does the Charon edge-type vocabulary map onto Noesis primitives?

---

## Expansion Priority (Each Goes Through the Full Loop)

### 1. Genus-2 Curves (NEXT — highest scientific payoff)
- **Why:** Directly tests the 163 finding. If genus-2 curves land near those dim-2 forms in
  zero space, Charon detected Paramodular Conjecture objects computationally.
- **Data:** LMFDB has genus-2 curve data with L-functions and zeros.
- **Pipeline:** Ingest → zero vectors → battery → graph edges → disagreement atlas
- **Cost:** Small dataset, high value, one crossing.
- **Kill condition:** If genus-2 curves are NOT zero-proximate to the 163, the finding
  is a character effect, not a correspondence signal.

### 2. Dirichlet Characters (calibration layer)
- **Why:** Simplest L-functions. If zeros can't distinguish Dirichlet characters by order
  and conductor, the coordinate system is broken on easy inputs.
- **Data:** LMFDB has extensive Dirichlet character data.
- **Pipeline:** Same loop. Serves as unit test for the zero geometry.
- **Cost:** Cheap, well-understood, diagnostic.

### 3. Number Fields (new structure test)
- **Why:** Dedekind zeta functions have zeros. New graph edge types (field extensions,
  Galois group containment). Tests whether zeros encode class number like they encode rank.
- **Data:** LMFDB has number field data.
- **Pipeline:** Same loop + new edge types in graph_edges table.
- **Cost:** Large dataset, significant ingestion time.

### 4. Artin Representations (Langlands-native expansion)
- **Why:** The Galois side of the correspondence. Bridges modular forms to Galois
  representations via the Artin conjecture. Graph gets denser where it's currently sparse.
- **Data:** LMFDB has 798K Artin representations.
- **Pipeline:** Same loop. Cross-layer query: are Artin reps zero-proximate to their
  known modular form partners?
- **Cost:** Highest complexity, highest Langlands payoff.

---

## Why This Is Foundational (Not a Side Experiment)

### Increasing returns
Every new object type makes every previous object type more useful:
- Genus-2 curves make the 163 dim-2 forms testable
- Artin reps make MFs navigable from the Galois side
- Number fields provide a third independent axis
- Each new type potentially bridges disconnected graph components

### Schema supports it
- `objects.object_type` accepts any string — new types add rows, not columns
- `graph_edges.edge_type` accepts any string — new relationships add values, not schema
- Test battery is type-agnostic — tests discrimination, graph correlation, trivial dominance
- The loop (ingest → battery → graph → atlas) is the same for any object type

### Connection to Prometheus
- Three-layer architecture (continuous/discrete/identity) mirrors Noesis multi-lens pattern
- Edge types may map to Noesis primitives (isogeny→MAP, twist→SYMMETRIZE, extension→EXTEND)
- The boundary between Charon and Noesis becomes empirically testable as graph densifies
- The TDD methodology is shared infrastructure across all Prometheus subsystems

---

## Kill Test Results (2026-04-02)

### The 163 Dim-2 Forms
| Test | Result | Implication |
|------|--------|-------------|
| Kill Test 1: Is weight-2 dim-2 sufficient? | **SURVIVED** (10.7% EC-proximate) | The 163 are a real subset, not generic |
| Kill Test 2: Is character the driver? | **PARTIAL KILL** (3.3x enrichment) | Character amplifies signal but doesn't fully explain |
| Dimension gradient | dim-2=10.7%, dim-3=0.8%, dim-4=0.8%, dim-5+=0% | Dim-2 is special; higher dims are not EC-like |

**Verdict:** Character-dependent, partially explained, worth testing against genus-2 data
before claiming anything about paramodular correspondence.

---

## Short-Term Actions

1. **Genus-2 test** — one crossing. Ingest genus-2 curves, check zero proximity to the 163.
   Binary outcome: either they cluster or they don't. This is the next brick.

2. **Document everything** — the kill test results, the murmuration validation, the
   character confound. The receipt pile is the real asset.

3. **Do NOT overclaim.** The 163 are interesting. They are not "functorial wormholes."
   They are dim-2 weight-2 non-trivial-character forms whose zeros resemble EC zeros.
   That's what the data says. Nothing more until genus-2 data speaks.
