# Stage 1 findings: historical Hephaestus / Nous / Coeus artifacts

Surveyed 2026-09-29 at origin/main 9df89d54e. All paths are repository-relative. Nothing
here was inferred from the build prompt; every count comes from reading the files.

## The pipeline (as it actually ran, 2026-03-24 .. 2026-03-31)

    Nous (sample triple -> LLM analysis -> score)  ->  Coeus (causal weights)  ->  Hephaestus (forge code, gates)

## Sources used by the Collider ingestion

| source | path | schema (actual) | size |
|---|---|---|---|
| Concept dictionary | `agents/nous/src/concepts.py` (`CONCEPTS`) | `{name, field, mechanism, short_description}`; mechanism in structure/dynamics/constraint/measure | 95 concepts, 20 fields |
| Nous evaluations | `agents/nous/runs/<run>/responses.jsonl` (12 runs) | `{triple:[i,j,k], concept_names, concept_fields, response_text, score:{ratings{reasoning,metacognition,hypothesis_generation,implementability}, novelty, is_unproductive, composite_score, high_potential}, model, timestamp}` | 5,918 responses, 5,727 unique triples |
| Hephaestus forge ledger | `agents/hephaestus/ledger.jsonl` | `{key ("A + B + C", sorted), concept_names, status forged/scrap, reason, accuracy, calibration, margin_*, timestamp}` | 6,661 outcomes (385 forged, 6,276 scrap) |
| Forge library | `agents/hephaestus/forge*/<a>_x_<b>_x_<c>.py/.json` | tool code + `{concept_names, concept_fields, nous_composite_score, test_accuracy, test_calibration, forged_at}` | forge 366, v2..v9 ~1,140 .py |
| Coeus concept effects | `agents/coeus/graphs/concept_scores.json` | `concept_influence{name:{forge_effect, reasoning_effect}}` | 95 concepts |
| Nous priority triples | `agents/nous/data/priority_triples.json` | `{concepts[3], reason}` | 15 |

## Sources inspected and NOT ingested (and why)

- `agents/hephaestus/humanreadable/*.md` (9,394 files): per-triple reports that are
  *derived* from Nous + ledger + Coeus (header, Nous analysis, Coeus block, forge status,
  code). Ingesting the primaries instead avoids double counting. The report path is kept
  as a provenance pointer where it exists.
- `agents/coeus/enrichments/` (4,031) and per-triple `agents/coeus/graphs/*.json`: prompt
  enrichment blocks for code generation, not concept collisions.
- `forge/candidates/` (605): a later tier-2 forge (2026-04-04), one category plus
  single-field seeds. These are not concept triples.

## Facts worth knowing

- The Nous README says `mechanism_type`; the code says `mechanism`. The code is the
  ground truth.
- The README says 18 fields; the dictionary has 20.
- Model: 5,915 of 5,918 responses are `nvidia/nemotron-3-super-120b-a12b`, and 3 are
  `qwen/qwen3.5-397b-a17b`.
- 299 responses are marked `is_unproductive`. They are kept and flagged, not dropped.
- Topology x Gauge Theory x Evolution IS in the Nous history (composite 0.0).
- Epigenetics x Emergence x Hoare Logic is NOT in the Nous history or the ledger. All three
  concepts exist in the dictionary, so the Collider can build that triple, but only as a
  curated or generated collision, never labelled historical.
- Most Nous analyses begin with a generic "**Algorithm**" header. Some name the mechanism
  ("Probabilistic Abductive Constraint Solver (PACS)", "Evolutionary Analogical Neural
  Oscillator Network (EANON)"). The ingestion extracts a name when one exists; otherwise
  the title stays generic.
- Nous analyses describe answer-scoring *reasoning tools* built from the concepts. They
  are historical LLM output, never validated science. The Collider labels them that way.
