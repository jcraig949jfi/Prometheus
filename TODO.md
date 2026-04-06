# Prometheus — Master TODO List
## Updated: 2026-04-06

*Living document. Each agent session updates its section.*

---

## JAMES — Human-in-the-Loop Action Items

### Immediate
- [ ] **OEIS Full Dump** — Register at oeis.org, download full dump with cross-references → `cartography/oeis/data/`. Blocks keyword search (names.gz corrupted).
- [ ] **Review Suggestions Queue** — 19 pending items. Run: `cd cartography/shared/scripts && python suggestions.py`. Top: OEIS names (HIGH), Materials fields (HIGH), NLI check (HIGH).
- [ ] **Review 4 Battery Survivors** — 4 hypotheses survived 11-test battery, need sign-off before "confirmed". See `cartography/convergence/data/active_threads.json`.
- [ ] **Review External Research Roadmap** — `cartography/convergence/reports/external_research_roadmap_20260406.md`. 25 papers triaged into 5 priority buckets.

### When Available
- [ ] **GAP System Install** — `conda install -c conda-forge gap-system`. Unblocks SmallGroups character tables.
- [ ] **Bilbao Crystallographic** — SSL error from Python, works in browser. Download space groups from https://www.cryst.ehu.es/ → `cartography/physics/data/bilbao/`
- [ ] **Materials Project Expansion** — 1K crystals ingested, 150K+ available. crystal_system/spacegroup fields 0% populated.
- [ ] **Google Billing** — Check billing status, confirm free tier limits for Gemini in Eos
- [ ] **Archive Old Repos** — bitfrost-mech, ArcanumInfinity → read-only

### Blocked (external)
- nLab: Cloudflare 403
- ProofWiki: Cloudflare 403
- House of Graphs: 401 auth
- PDG: API 500
- ATLAS representations: 404

---

## Charon / Cartography (Cross-Domain Research Pipeline)

### Next Session
- [ ] Fuzzy-match 2,166 Wikidata labels → 12K extracted concepts (ground the concept layer)
- [ ] Generate hypotheses FROM bridges instead of LLM creativity (Phase 3)
- [ ] Download MMLKG (2.2GB Mizar math proof graph — figshare)
- [ ] Download OpenAlex concept taxonomy (65K concepts, maps papers → our data)
- [ ] Track per-function success rates + branch outcome tracking

### Pipeline Improvements (from process analysis)
- [ ] Fix LLM hallucinating search function names — ongoing, validation gate catches most
- [ ] Add more battery extraction strategies as new datasets are added
- [ ] Add OEIS cross-reference graph when full dump available
- [ ] Deeper Fungrim symbol → mathlib namespace bridge extraction

### Data Expansion (from dataset candidates doc)
- [ ] Lattice Catalogue (Sloane/Nebe) — theta series = modular forms bridge
- [ ] Number Fields DB — 100K+ fields, LMFDB bridge
- [ ] Local Fields DB — ramification data, Charon spectral bridge
- [ ] polyDB — polytope f-vectors → OEIS
- [ ] Isogeny DB — LMFDB supplement
- [ ] pi-Base — topology, mathlib bridge

### Completed (2026-04-06)
- [x] Autonomous research cycle pipeline (10 files, ~5K lines)
- [x] 8 datasets ingested (OEIS, LMFDB, mathlib, Metamath, Materials, KnotInfo, Fungrim, ANTEDB)
- [x] 11-test falsification battery with 5-category kill diagnosis
- [x] NLI relevance gate (Chen et al. pattern)
- [x] Concept bridge layer (12K concepts, 359K links, 165 bridges)
- [x] External research feed (Semantic Scholar + arXiv + Tavily)
- [x] Council review + tensor review (periodic)
- [x] Suggestions ledger (HITL-gated)
- [x] Search plan enrichment (fixes placeholder string problem)
- [x] Wikidata math concepts (2,166 downloaded)
- [x] External research roadmap triaged

---

## Ignis (Reasoning Circuit Discovery)

### Precipitation Hunt
- [x] Compute delta_proj at 1.5B
- [x] Expand RPH eval to 53 pairs
- [x] Build reasoning subspaces at layers 14, 18, 21
- [x] Compute delta_proj across all 4 scales
- [ ] Analyze multi-layer Ignis run results (L14/L18/L21 at 1.5B)
- [ ] If mid-layer shows different bypass/native ratio → design follow-up

**Key finding:** 0.5B/1.5B/3B produce ZERO self-corrections. Only Qwen3-4B self-corrects (3/8 traps).

### Scale Gradient
- [ ] 7B Qwen2.5 cloud run (Lambda/RunPod A100, ~$25-40)
- [ ] Update scale gradient table with 7B results

### SAE Decomposition
- [ ] Install SAELens, train SAE on Qwen 2.5-3B residual stream
- [ ] Decode best_genome.pt vectors through SAE
- [ ] Get human-readable feature decomposition

### RPH Paper
- [ ] Integrate delta_proj results
- [ ] Reframe around bypass finding
- [ ] Add 7B results when available

---

## Eos / Dawn (Horizon Scanner)

### To Wire
- [ ] Groq as fallback LLM (14.4K RPD free)
- [ ] Cerebras for deep analysis (Qwen 3-235B free)
- [ ] Serper for targeted web searches (2500 lifetime budget)

### Infrastructure
- [x] Paper dedup across cycles
- [x] Persistent paper/repo index
- [ ] Add log file output alongside console
- [ ] Alert mechanism for critical findings

---

## Pronoia (Agent Orchestrator)

- [x] Built pronoia.py with scan/eos/metis/status/review commands
- [x] --every and --publish flags
- [ ] Add `ignis` command
- [ ] Add `all` command: Eos → Metis → review in one pass
- [ ] Process health monitoring

---

## Arcanum (Waste Stream Novelty Mining)

- [ ] Smoke-test from F:\Prometheus\arcanum\
- [ ] Review current 1.5B screening results
- [ ] Plan 3B screening run

---

## Quick Reference — Running Things

```bash
# Charon research cycle
cd cartography/shared/scripts
python research_cycle.py --provider openai --hypotheses 3 --loop 5 \
  --tensor-review-every 5 --external-research \
  --topic "your research question"

# Individual Charon components
python concept_index.py          # 12K concepts, 165 bridges
python tensor_review.py          # Dataset quality audit (free)
python external_research.py      # Daily paper + web feed
python suggestions.py            # View pending suggestions

# Eos horizon scan
cd agents/eos && python -m src.eos_daemon

# Pronoia orchestration
cd agents/pronoia && python pronoia.py scan --every 3600 --publish
```
