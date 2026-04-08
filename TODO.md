# Prometheus — Master TODO List
## Updated: 2026-04-07

*Living document. Each agent session updates its section.*

---

## JAMES — Downloads & Unblocks

### Immediate (blocks progress)
- [x] **MMLKG Download** — 23GB GraphML + 355MB CSVs at `charon/james_downloads/mmlkg/`. 464K theorem refs, 1.8M local refs, 1.5M predicates. Claude needs to ingest CSVs into search engine.
- [x] **GAP System** — INSTALLED at `charon/james_downloads/GAP/`. GAP 4.15.1.
- [x] **Bilbao Crystallographic** — 230 space group JSONs in `cartography/physics/data/bilbao/`. 229/230 have JSON parse errors from GAP script — Claude needs to fix parser.
- [x] **OEIS data** — names.txt (394K names) + stripped copied to `cartography/oeis/data/`. Keyword search restored. Full oeisdata repo (664K sequence files with all metadata) cloned 2026-04-07 at `charon/james_downloads/oeisdata/`. Cross-reference parsing still needed.

### Nice to Have (enrichment)
- [x] **Local Fields DB** — Downloaded 2026-04-07. 10 wildly-ramified data files + 4 PARI/GP code files + docs at `cartography/local_fields/data/`. Primes p=2,3,5, degrees 4-14.
- [x] **polyDB** — Downloaded 2026-04-07. 17/18 collections sampled (SchlaefliFan timeout) at `cartography/polytopes/data/`. f-vector projections for OEIS bridge.
- [x] **Isogeny DB** — Downloaded 2026-04-07. Full Zenodo dump (300MB) at `cartography/isogenies/data/`. 3,240 prime directories, adjacency matrices for isogeny degrees 2-11, primes to 30K.
- [x] **pi-Base** — Cloned 2026-04-07. 220 spaces, 230 properties, 859 theorems at `cartography/topology/data/pi-base/`.
- [x] **Materials Project API key** — Added to keys.py as "MATERIALS" 2026-04-07. Fetch script updated to pull full 150K+ structures (running).
- [ ] ~~**Elicit/Consensus/Scite API keys**~~ — Too expensive. Use free alternatives: Semantic Scholar API + OpenAlex (already in use by Charon).

### Blocked (external, not fixable)
- nLab: Cloudflare 403
- ProofWiki: Cloudflare 403
- House of Graphs: 401 auth
- PDG: API 500
- ATLAS representations: 404

---

## Charon / Cartography

### Data Wiring Sprint — DONE (2026-04-07)
- [x] Parsed genus-2 raw dump: 66,158 curves from g2c-data/ into genus2_curves_full.json
- [x] Fetched 300 Maass forms from LMFDB API (maass_rigor table, level 1, spectral 9.5-142.4)
- [x] Wired genus-2, Maass, lattices (21), FindStat (1993 stats) into search_engine.py
- [x] Wired OpenAlex 10K concepts into concept bridge layer (noun extractor + bridge keywords)
- [x] Rebuilt concept_index.py: 15 noun extractors + 15 verb extractors
- **Result: 20 datasets, 52 search functions, 38,887 concepts, 1.88M links, 4,410 bridges, 59/120 pairs (49%)**

### Shadow Tensor + Exploration Sprint — DONE (2026-04-08)
- [x] Mined 17K hypothesis corpus: scored by dataset pair, word frequency, template extraction
- [x] Built void_scanner.py: maps 80 void/weak pairs, finds hidden concept overlap (3s)
- [x] Built bridge_hunter.py: generates + tests hypotheses from bridges (0.3s, zero cost)
- [x] Built shadow_tensor.py: dark matter map, 190 cells, anomaly scoring, kill signatures
- [x] Built preload_shadow.py: ripped 5,767 cycle logs, extracted 92K test records, 6,240 battery runs
- [x] Built map_elites.py: diversity-driven bin filling, dataset_pair x failure_mode archive
- [x] Built explorer_loop.py: autonomous zero-cost agent, 10s/sweep, BELOW_NORMAL priority
- [x] Added F14 (phase-shift test) to falsification battery (from Gemini session)
- [x] Updated all 8 terminal bat files to cover 5 new datasets + shadow tensor targets
- [x] Updated launcher to include explorer loop (run_charon_8terminals.bat)
- **Result: 92K test records, 140 strong-signal cells, F3 dominant killer (weak truths not noise), 14 cold cells**

### Microscope + Term Factory Sprint — DONE (2026-04-08 afternoon)
- [x] Constant telescope: 68K sleepers scanned, 861 hits, 39 constants (Feigenbaum/Mills/Apery/Brun)
- [x] A148763 Feigenbaum KILLED by computing 16 new terms (parity artifact at 29 terms)
- [x] GAP smallgroups parsed + wired: 21 datasets, 56 searches, sv=5797 NF--SmallGroups
- [x] FindStat enriched: 250 statistics with descriptions, 17 collections
- [x] Polytopes near-misses KILLED: small-integer artifact
- [x] NF--SmallGroups distributional identity KILLED: z-normalization artifact (probe patched)
- [x] OEIS term factory: **1,422 sequences extended, 22,338 new verified terms**
- [x] Growth constant scanner: no false positives at 1e-4 with 40+ terms
- [x] Geometric survey: 13 probes × 12 arrays × 66 pairs
- [x] Microscope built: 3-layer decontamination (prime detrend + small int filter + scale normalization)
- **Key finding: 96-100% of gap structure = prime factorization. Real bridges at 3-4 decimal precision in residuals.**

### Queued
- [ ] Run microscope with fixed matched-object comparison (not sorted-rank)
- [ ] Build Isolatus metric as first-class search function (high entropy / low centrality)
- [ ] Submit 22K OEIS terms (batch b-file submission)
- [ ] Extend remaining ~2,100 walk sequences (A148/149/150/151 remainder)
- [ ] Build commutativity score (Gemini Q6) and steering vectors (Q7)
- [ ] More data: Materials Project full 150K

### Pipeline v3 Status (2026-04-07 night)
- [x] v3 tensor bridge architecture (0 cost, 0.8s/cycle)
- [x] ALL 15 verb extractors (all 20 datasets have verbs), 1.88M links, 59/120 pairs connected (49%)
- [x] Bridge-specific searches, diversity gate, enrichment-before-validation
- [x] Research memory + dedup + tautology detection
- [x] Integer-aware battery nulls
- [x] Known truth battery: **180/180 verified (100%)** across 6 layers
- [x] Falsification battery: **14 tests** (F12: partial correlation, F13: growth rate, F14: phase shift)
- [x] Genocide R1-R6: 37+ rediscoveries including Eichler-Deuring, modularity, BSD, Heegner
- [x] Tensor validation sweep: 4 genuine connections, 6 confounds classified
- [x] OEIS cross-reference graph: 1.59M edges, 335K sources
- [x] **20/20 datasets, 52 search functions**, --tag for parallel terminals
- [x] Gemini spatial math test: 10/10 questions answered computationally
- [x] Sleeping Beauty analysis: 68,770 high-structure low-connectivity sequences identified
- [x] 10,129 wakeup candidates (sleepers referencing hubs)
- [x] **New datasets wired**: Genus-2 (66K), Maass (300), Lattices (21), FindStat (1993), OpenAlex (10K)

### Findings Status
- **Metabolism z=3.8** — Survives constrained null (p=0.005). Modest but real. NOT z=32.
- **R6 deep dive** — 4/6 "potentially genuine" survivors killed by partial correlation (just scale with p). 1 Eichler-Deuring rediscovery. 1 known math (CN=1).
- **Sleeping beauties** — 33% more structured than hubs, 48% fewer famous integers. They speak in quadratic forms, not Fibonacci.
- **Tensor validation** — Genuine bridges are verb-driven (Fungrim-mathlib=17 dims). Confound bridges are integer-driven (KnotInfo-LMFDB=shared primes).
- **Known math rediscoveries** — 37+ across 6 genocide rounds. Validates pipeline at 100%.

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
python genocide_r5_expansion.py # Round 5: 16 tests (7 new datasets)
python known_truth_battery.py   # Calibration: 39 known truths

# Data tools
python concept_index.py     # Rebuild 38K concepts + verb bridges (15 datasets)
python tensor_bridge.py     # Tensor bridge detection (38s, 22/66 pairs connected)
python tensor_review.py     # Dataset quality audit (3 seconds)
python constant_matcher.py 1.618  # Identify mathematical constants

# Overnight runner
run_charon_overnight.bat    # Loops indefinitely (~$0.01/hr with DeepSeek)

# Parallel research terminals (run 4 at once, non-overlapping dataset focus)
# Each terminal gets a --tag so logs/reports never collide.
# All 15 datasets are in the random pool; topics steer the LLM toward different corners.

# Terminal 1 — ARITHMETIC: knots + number fields + OEIS + isogenies
python research_cycle.py --tag T1 --provider deepseek --hypotheses 8 --loop 70 --tensor-review-every 25 --topic "Bridge knot polynomial invariants (Alexander, Jones, determinants) with number field class numbers, discriminants, and regulators. Do isogeny graph node counts at prime p predict anything about knots with determinant p? Search OEIS for the unpopular sequences — sleeping beauties nobody checks. Test across bases, not just base 10."

# Terminal 2 — ANALYTIC: LMFDB + Fungrim + ANTEDB + local fields
python research_cycle.py --tag T2 --provider deepseek --hypotheses 8 --loop 70 --tensor-review-every 25 --topic "Find structural bridges between LMFDB modular form levels, Fungrim formula symbol patterns, and ANTEDB zero-density exponent bounds. Do wildly ramified local field extensions at p=2,3,5 encode information about L-function zeros or exponent pairs? Focus on transformations (verbs) not labels (nouns). No integer coincidences."

# Terminal 3 — GEOMETRIC: space groups + polytopes + pi-Base + materials
python research_cycle.py --tag T3 --provider deepseek --hypotheses 8 --loop 70 --tensor-review-every 25 --topic "Cross the geometric divide. Do crystallographic space group Wyckoff positions correlate with polytope f-vectors or vertex counts? Do pi-Base topological properties (compactness, metrizability, connectedness) predict which Mizar articles are hubs? Test crystal system symmetry orders against number field Galois group orders. Bridge the continuous (topology) with the discrete (combinatorics)."

# Terminal 4 — STRUCTURAL: MMLKG + mathlib + Metamath + cross-everything
python research_cycle.py --tag T4 --provider deepseek --hypotheses 8 --loop 70 --tensor-review-every 25 --topic "Map the proof graph. Do Mizar hub articles reference the same concepts as mathlib's most-imported namespaces? Do Metamath theorem density patterns predict ANTEDB bound improvements? Test the structural skeleton: which proof dependencies bridge to which empirical datasets (LMFDB conductors, knot determinants, OEIS terms)? Find the verbs that connect formal proofs to computed objects. Explore the forgotten corners."

# Terminal 5 — SLEEPING BEAUTIES: hunt the dark matter
python research_cycle.py --tag T5 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Hunt sleeping beauties. Use oeis_sleeping_beauties to find high-entropy low-connectivity sequences. Do they share growth patterns with known hubs? Can you rotate a sleeping beauty (apply diff, ratio, log, or modular transform) into alignment with primes, Fibonacci, or Catalan? Test quadratic form representation counts (x^2+ky^2) against LMFDB conductors and number field discriminants. The sleepers speak in quadratic forms, not famous integers."

# Terminal 6 — DISCONNECTED PAIRS: bridge the 36 gaps
python research_cycle.py --tag T6 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Bridge the disconnected. 36 out of 66 dataset pairs have zero tensor bond dimension. Find verb concepts that connect: Polytopes to ANTEDB (f-vectors to exponent bounds), piBase to KnotInfo (topological properties to knot invariants), MMLKG to Isogenies (theorem structure to graph structure), Materials to NumberFields (crystal properties to field discriminants). Every new connection the tensor can't see is a potential discovery."

# Terminal 7 — L-FUNCTIONS: the Langlands corridor
python research_cycle.py --tag T7 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Walk the Langlands corridor. LMFDB has L-functions for elliptic curves and modular forms. Fungrim has Dirichlet L-function formulas. ANTEDB has zero-density bounds. Number Fields have regulators and class numbers. Isogenies encode supersingular structure. Find the verb bridges between these — the transformations that connect analytic, algebraic, and geometric number theory. What operations do they share?"

# Terminal 8 — CROSS-REFERENCE ARCHAEOLOGY: dig into OEIS xref graph
python research_cycle.py --tag T8 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Explore the OEIS cross-reference graph. 1.6M edges connect 335K sequences. Which cross-reference PATHS connect sleeping beauties to hubs through intermediate sequences? Do sequences with exponential growth cross-reference polynomial sequences at a different rate than sub-linear? Use oeis_crossrefs and oeis_xref_hubs to map the citation topology. Find the one-way bridges — sleepers that reference hubs but are never referenced back."
```
