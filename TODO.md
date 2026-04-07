# Prometheus — Master TODO List
## Updated: 2026-04-07

*Living document. Each agent session updates its section.*

---

## JAMES — Downloads & Unblocks

### Immediate (blocks progress)
- [x] **MMLKG Download** — 23GB GraphML + 355MB CSVs at `charon/james_downloads/mmlkg/`. 464K theorem refs, 1.8M local refs, 1.5M predicates. Claude needs to ingest CSVs into search engine.
- [x] **GAP System** — INSTALLED at `charon/james_downloads/GAP/`. GAP 4.15.1.
- [x] **Bilbao Crystallographic** — 230 space group JSONs in `cartography/physics/data/bilbao/`. 229/230 have JSON parse errors from GAP script — Claude needs to fix parser.
- [x] **OEIS data** — names.txt (394K names) + stripped copied to `cartography/oeis/data/`. Keyword search restored. oeisdata repo at `charon/james_downloads/oeisdata/` still needs cross-reference parsing.

### Nice to Have (enrichment)
- [ ] **Local Fields DB** — https://math.la.asu.edu/~jj/localfields/ → `cartography/local_fields/data/`. Ramification data, connects to Charon spectral findings.
- [ ] **polyDB** — https://polydb.org/ → `cartography/polytopes/data/`. Polytope f-vectors bridge to OEIS.
- [ ] **Isogeny DB** — https://isogenies.enricflorit.com/ → supplements LMFDB graph.
- [ ] **pi-Base** — https://topology.pi-base.org → `cartography/topology/data/`. Topological spaces, bridges mathlib Topology namespace.
- [ ] **Materials Project API key** — Add to keys.py as "MATERIALS" to replace synthetic data with real 150K+ structures.
- [ ] **Elicit/Consensus/Scite API keys** — For literature grounding layer (Sleeping Beauty detection).

### Blocked (external, not fixable)
- nLab: Cloudflare 403
- ProofWiki: Cloudflare 403
- House of Graphs: 401 auth
- PDG: API 500
- ATLAS representations: 404

---

## Charon / Cartography

### Active (in progress)
- [ ] Wire OpenAlex 65K concepts into concept bridge layer (just downloaded)
- [ ] Wire Number Fields 9.1K into concept extraction (just downloaded)
- [ ] Rebuild tensor with new datasets + verb concepts
- [ ] Run genocides on new data combinations

### Pipeline v3 Status
- [x] v3 tensor bridge architecture (0 cost, 0.8s/cycle)
- [x] Verb concept extraction (26K concepts, 855K links, 7/10 pairs connected)
- [x] Bridge-specific searches
- [x] Research memory + dedup + tautology detection
- [x] Integer-aware battery nulls
- [x] Known truth battery: 38/39 validated (97.4%)
- [x] Genocide: 33/54 survive (61%), all known math rediscoveries
- [x] Modularity theorem independently rediscovered (z=72)
- [x] Heegner numbers independently found from Number Fields data
- [x] BSD small-prime signature found (div by 2,3,5 predicts rank)
- [x] OEIS keyword search restored (James download)
- [x] Number Fields downloaded (9,116 fields)
- [x] OpenAlex downloaded (65K concepts)
- [x] Materials expanded (10K, crystal_system fixed)

### Findings Status
- **Metabolism z=3.8** — Survives constrained null (p=0.005). Modest but real. NOT z=32.
- **Cross-domain discoveries** — Zero novel bridges survive proper testing yet.
- **Known math rediscoveries** — 33 across 4 genocide rounds. Validates pipeline.

---

## Ignis (Reasoning Circuit Discovery)

- [ ] Analyze multi-layer Ignis run results (L14/L18/L21 at 1.5B)
- [ ] 7B Qwen2.5 cloud run (~$25-40)
- [ ] Install SAELens, train SAE on Qwen 2.5-3B
- [ ] Reframe RPH paper around bypass finding

---

## Eos / Dawn (Horizon Scanner)

- [ ] Groq as fallback LLM
- [ ] Cerebras for deep analysis
- [ ] Alert mechanism for critical findings

---

## Quick Reference

```bash
# Charon v3 research cycle (0 cost for bridge hypotheses)
cd cartography/shared/scripts
python research_cycle.py --provider deepseek --hypotheses 3 --loop 20 \
  --tensor-review-every 10 --topic "your question"

# Genocide (rapid hypothesis testing, no LLM)
python genocide.py          # Round 1: 12 tests
python genocide_r2.py       # Round 2: 12 tests
python genocide_r3_wild.py  # Round 3: wild cross-domain
python genocide_r4_massacre.py  # Round 4: 18 tests
python known_truth_battery.py   # Calibration: 39 known truths

# Data tools
python concept_index.py     # Rebuild 26K concepts + verb bridges
python tensor_bridge.py     # Tensor bridge detection (4 seconds)
python tensor_review.py     # Dataset quality audit (3 seconds)
python constant_matcher.py 1.618  # Identify mathematical constants

# Overnight runner
run_charon_overnight.bat    # Loops indefinitely (~$0.01/hr with DeepSeek)

# Parallel research terminals (run 3 at once, different topics)
# Terminal 1:
python research_cycle.py --provider deepseek --hypotheses 3 --loop 20 --tensor-review-every 10 --topic "Find bridges between knot polynomial coefficients, number field class numbers, and OEIS sequences. Test the unpopular sequences."

# Terminal 2:
python research_cycle.py --provider deepseek --hypotheses 3 --loop 20 --tensor-review-every 10 --topic "Find bridges between LMFDB modular form levels, Fungrim formula symbol patterns, and ANTEDB zero-density exponent bounds. Focus on structural relationships not integer coincidences."

# Terminal 3:
python research_cycle.py --provider deepseek --hypotheses 3 --loop 20 --tensor-review-every 10 --topic "Test irregular primes, Heegner numbers, and class number 1 discriminants against knot determinants and metabolic eigenvalue ratios. Explore the sleeping beauties."
```
