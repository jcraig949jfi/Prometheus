# Prometheus Pivot Research — Batch 1 Seeds (2026-05-02)

**Drafted by:** Aporia
**Trigger:** James asked for 20 deep research topics informing the Silver-thesis pivot. Companion to `pivot/aporia.md`, `pivot/Charon.md`, `pivot/harmoniaD.md`, `pivot/techne.md`.

**Frame:** Not open math problems — research that informs the *pivot itself*. Substrate engineering, calibration corpus expansion, RL-environment patterns, competitive intelligence, and a few math-content topics that fill load-bearing calibration gaps. Each topic is tractable as a 600-1200 word Claude-subagent or Gemini DR brief.

**Convergence target across pivot files:**
- Substrate as environment (Charon, Techne, harmoniaD)
- BIND/EVAL → Gymnasium env → public spec (Techne)
- Promote, promote, promote — 10 v1 symbols by end of May (Charon)
- Mnemosyne ingest full throttle (Aporia)
- Externalize the substrate (all four)

## Five fronts

1. **Substrate-as-environment engineering** — what other systems do well that Prometheus should adopt
2. **Calibration corpus expansion** — ingest architecture for the load-bearing data sources
3. **Competitive intelligence** — what DeepMind, Ineffable, others are actually shipping
4. **Multi-agent coordination at scale** — patterns for compounding without hiring
5. **High-leverage math content** — calibration anchors in regions the substrate is thin

## 20 topics (numbered, prioritized into 3 tiers)

| # | Topic | Front | Tier |
|---|---|---|---|
| 1 | **Gymnasium env design patterns for symbolic-reasoning RL environments** | Substrate | **1** |
| 2 | **Reward design for partially-verifiable mathematical claims** | Substrate | **1** |
| 3 | **Bloom-Erdős catalog ingestion architecture and paradigm-tagging schema** | Corpus | **1** |
| 4 | **DeepMind AlphaProof — current public state, Lean integration, methodology** | Intel | **1** |
| 5 | **Action space design for typed symbolic actions (Lean tactics, Wolfram, AlphaProof)** | Substrate | 2 |
| 6 | **State representation for symbolic substrates (graph encodings, embeddings)** | Substrate | 2 |
| 7 | **Provenance + cost annotation patterns (Bazel, Nix, IPLD, Datomic, Unison)** | Substrate | 2 |
| 8 | **MathNet ingestion architecture and multi-language paradigm extraction** | Corpus | 2 |
| 9 | **Calibration corpus landscape (LeanDojo, miniF2F, ProofNet, FrontierMath, PutnamBench)** | Corpus | 2 |
| 10 | **Open-source math substrate competitive landscape** | Intel | 2 |
| 11 | **Append-only collaborative substrates (Nix, IPFS, Datomic, Pijul, Unison)** | Coord | 2 |
| 12 | **Maieutēs / weak-signal incubator design — analogous systems in research workflows** | Coord | 2 |
| 13 | **Solution-paradigm tagging methodology at scale (NLP, structured extraction, weak supervision)** | Corpus | 3 |
| 14 | **Linear capability tokens / object capability security best practices and failure modes** | Substrate | 3 |
| 15 | **Verifier-rich math domains catalog — where RL-substrate-eligible structure already exists** | Math | 3 |
| 16 | **Cross-domain operator transport benchmark catalog — known megethos-style transfers** | Math | 3 |
| 17 | **Higher-genus arithmetic geometry computational corpora — gaps beyond LMFDB g=2** | Math | 3 |
| 18 | **Falsification battery design — replication-crisis / multiverse-analysis / preregistration applied to math** | Substrate | 3 |
| 19 | **Tensor decomposition for symbolic substrates (TT, hierarchical Tucker, hypergraph) — what has been tried** | Substrate | 3 |
| 20 | **Ineffable Intelligence + Silver methodology intelligence — track record, prior bets, hiring signals** | Intel | 3 |

## Token budget

20/20 daily token budget for this batch. Fire 3 at a time, 6 waves of 3 + 1 final wave of 2. Sequential firing: Wave 1 = #1, #2, #3 (the load-bearing immediate ones — env design, reward design, Mnemosyne REQ-001 architecture).

## Save-to

Reports save to `aporia/docs/prometheus_pivot_research_batch1/report_NN_slug.md` as they return. Each report is a 600-1200 word brief with: situation summary, current state-of-the-art, concrete actionable patterns Prometheus should adopt, risks/anti-patterns, references.

## Status

Drafted; firing Wave 1 immediately.

---

*Aporia, 2026-05-02. Companion to `pivot/aporia.md`. Each report is meant to inform a specific pivot decision; the batch as a whole is the research substrate for the next 30 days of build work.*
