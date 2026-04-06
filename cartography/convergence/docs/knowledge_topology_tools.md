# Knowledge Topology Tools — Integration Assessment
## 2026-04-06

---

## TIER 1: Has API, integrate now

### Connected Papers
**API:** github.com/ConnectedPapers/connectedpapers-js (JS client exists)
**What it does:** Builds semantic similarity graph from a seed paper. Distance = similarity, not citation count.
**Integration:** Feed our surviving battery results as seed papers → get the neighborhood graph → find isolated but similar papers = Sleeping Beauties.
**Cost:** Likely freemium. Check rate limits.

### Consensus
**API:** api.consensus.app/v1/quick_search (documented, curl examples)
**What it does:** Peer-reviewed-only search that extracts claims, not just matches keywords.
**Integration:** For each metabolism-math bridge hypothesis, query Consensus: "Does metabolic network structure encode mathematical constants?" → get evidence-based answers from papers we'd never find by keyword.
**Cost:** API access available.

### Elicit
**API:** support.elicit.com — API keys available, 125M+ papers searchable
**What it does:** Answers research questions by scanning actual paper text. Finds papers using different jargon for the same concept.
**Integration:** The inverse search trick — query "frameworks that resolve non-associativity in algebraic biology" without specifying a field. Forces cross-domain discovery.
**Cost:** API keys, likely paid tier for bulk.

### Scite.ai
**API:** Unofficial CLI exists (OpenDevEd/scite-cli on GitHub)
**What it does:** Smart citations — tells you HOW a paper was cited (supporting, contrasting, mentioning). Papers with many "mentions" but few "supports" = gaps in literature.
**Integration:** For papers near our metabolism finding, check: are they "supported" or "contrasted"? Contrasted papers near our topic = the exact boundary of what's known.

### Sleeping Beauty Algorithm
**Code:** github.com/ranarag/SleepingBeauties (Python implementation exists)
**What it does:** Computes the Beauty Coefficient (B) — how long a paper slept vs how sharply it awakened.
**Integration:** Run on our Semantic Scholar results. Rank papers by Sleeping Beauty potential. High B + relevant to our topic = the paper nobody read that answers our question.
**Cost:** Free (Python, runs on citation data from S2 API)

## TIER 2: Web only, no bulk API

### ResearchRabbit
**Status:** Web-based, no public API for programmatic access
**Workaround:** Manual exploration for high-priority threads
**Value:** "Spotify for papers" — visual network from seed papers

### Litmaps  
**Status:** Web-based, early access, timeline visualization
**Workaround:** Manual for key findings
**Value:** Prior art detection — find forgotten papers from decades ago

### Iris.ai
**Status:** API exists but for their sales platform, not the research tool
**Workaround:** Manual interdisciplinary search
**Value:** Cross-field concept mapping

## INTEGRATION PRIORITY ORDER

1. **Sleeping Beauty algorithm** — FREE, Python, runs on S2 citation data we already fetch daily. Compute B-coefficient for all 25+ papers in each external research feed. Highest-B papers become priority reading.

2. **Consensus API** — For each surviving battery hypothesis, run the inverse query: "What resolves [X] across fields?" Pure evidence-based, no popularity bias.

3. **Connected Papers API** — For the metabolism-math finding specifically: feed the "Topological Environment in Genetic and Metabolic Networks" paper as seed → get the hidden neighborhood.

4. **Scite.ai smart citations** — For papers near our findings: how are they cited? Contrasted = gap. Supported = confirmation. This is the citation topology that reveals where the field disagrees.

5. **Elicit** — The inverse search: "frameworks that resolve non-associativity in biological algebra" — find the paper from the biology journal that has the math workaround.

## THE INVERSE SEARCH TRICK

This is the most powerful technique listed:

> "Search for the inverse of your problem. If stuck on an impossibility
> in Domain A, search for 'theoretical frameworks that resolve [X]'
> without specifying a field."

For our metabolism finding:
- Don't search: "mathematical constants in metabolic networks"
- Search: "algebraic constraints on spectral properties of conservation-law matrices"
- This forces discovery across physics, chemistry, engineering — anywhere conservation laws create algebraic structure.

For the non-associative enzyme question:
- Don't search: "non-associative enzyme kinetics"  
- Search: "energy-dependent ordering effects in sequential algebraic operations"
- This finds the quantum computing paper, the thermodynamics paper, the operations research paper that all describe the same phenomenon in different jargon.

## THE BEAUTY COEFFICIENT

Formula: B = Σ(ct - ct_0) where ct_0 is the citation count at awakening year.

A paper with B > 100 slept for years then exploded. Our target: find papers with high B that are topically adjacent to our metabolism-math finding. These are the papers that got ignored because they crossed domain boundaries — exactly what our tensor train is built to find computationally.

## CONNECTION TO PIPELINE

```
Current pipeline:
  Hypothesis → Search (our databases) → Battery → Verdict

Enhanced pipeline:
  Hypothesis → Search (our databases) → Battery → Verdict
                 ↓
  If SURVIVES → Connected Papers (neighborhood graph)
              → Consensus (evidence-based validation)
              → Scite (citation topology)
              → Sleeping Beauty scan (find the forgotten prior art)
              → Elicit inverse search (cross-domain workarounds)
```

The battery kills false positives. These tools kill false negatives — findings that ARE real but that nobody has connected to existing literature. That's the UPK layer.
