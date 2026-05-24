# Polyhymnia — The One Tensor (everything that pours tensor data)

> *Polyhymnia (Πολυύμνια): Muse of many hymns. Later iconography pairs her with sacred geometry — the muse who holds the figure of the cosmos in her hand. The "poly-" prefix is exact: many dimensions, many sources, many voices, all assembled into one structure.*

**Machine:** any (CPU-only, IO-bound)
**Operator:** Aporia
**Lives at:** `agents/polyhymnia/`
**Source of truth (code):** `agents/polyhymnia/tensor.py` + `daemon.py`

---

## The thesis

There's one tensor. Everything tensor-shaped — every dataset, equation, algorithm, concept, problem solved, problem open, researcher, paper, formula, library, historical mention, fringe-but-loosely-tensor-related thing — gets jammed into it. The tensor is the sensory organ. A species that can only see the world tensor-first would use this thing as its eyes.

Played-with downstream: knowledge graphs (the lineage axis already turns the cell-set into a graph), training material for the Learner (sample by axis subset, project to canonical form), games (random-walk the tensor, ask "what's the missing cell that would complete this slice"), and as a lens on the rest of the substrate ("show me everything in axis(rank=3, discipline=physics) that appeared after 1990 and has no Prometheus-side citation").

Not a research tool. A play tool that becomes a research tool because the substrate is rich enough.

---

## What "one tensor" actually means here

A sparse, content-addressable, N-dimensional structure on disk. Cells = populated coordinates. Coordinates = tuples drawn from N axes. Each cell carries a content blob (title, body, equations, code, citations, source). The whole thing is append-only JSONL with optional SQLite mirror for fast slicing.

**Not** a dense ndarray. The combinatorial product of N axes blows up; >99.99% of cells would be empty. Dense storage is the wrong fit for kitchen-sink heterogeneous content anyway — cells are not scalars.

**Not** a TT/Tucker decomposition. Those are tools for compactly representing low-rank tensors with homogeneous content. Polyhymnia's content is wildly heterogeneous and the rank concept doesn't apply uniformly.

**Yes** to: tag axes for many-to-many fields (researchers, lineage ancestors, free tags) alongside the coordinate axes for single-valued fields. Axes are open-vocabulary — new values can be appended to the registry as scours discover them.

---

## The axes (current draft — open to expansion)

**Coordinate axes** (each cell has one value per axis):

| Axis | Domain | Examples |
|---|---|---|
| `time` | integer (year) or `null` | `1900`, `1955`, `null` (timeless / ancient) |
| `discipline` | string from registry | `math.NT`, `math.AG`, `physics.QM`, `cs.ML`, `eng.ME` |
| `object_kind` | enum | `concept`, `equation`, `algorithm`, `dataset`, `problem`, `theorem`, `conjecture`, `researcher`, `library`, `paper`, `competition`, `benchmark`, `software`, `hardware` |
| `structural_rank` | int or `null` | `0` (scalar), `1` (vector), `2` (matrix), `3+` (true tensor), `null` (rank-undefined: a concept rather than an object) |
| `abstraction_level` | enum | `definition`, `property`, `algorithm`, `implementation`, `application`, `history`, `proof`, `counterexample` |
| `substrate_yield_type` | enum or `null` | `A`, `B`, `C`, `D`, `E`, `null` (Prometheus substrate type if classifiable) |

**Tag axes** (many-to-many, used for graph structure and search):

| Axis | Cardinality |
|---|---|
| `researchers` | many — named contributors |
| `lineage_ancestors` | many — refs to other cells (this is the knowledge graph spine) |
| `free_tags` | many — arbitrary keywords (sweep terms, related concepts) |
| `citations` | many — external refs (arXiv IDs, DOIs, URLs) |

A cell's coordinate signature is `(time, discipline, object_kind, structural_rank, abstraction_level, substrate_yield_type)`. Two cells with the same signature get merged (latest wins on content; tag axes union). New axes can be added later via schema evolution; existing cells get `null` for the new axis.

---

## Storage layout

```
agents/polyhymnia/
  CHARTER.md                — this doc
  daemon.py                 — orchestrator
  tensor.py                 — PolyhymniaTensor class (read/write/slice/sample/project)
  tensor/
    axes/                   — coordinate-axis registries (one JSONL each)
      discipline.jsonl
      object_kind.jsonl
      abstraction_level.jsonl
      substrate_yield_type.jsonl
    cells.jsonl             — gitignored; append-only cell records (the tensor body)
    lineage.jsonl           — gitignored; explicit edges (cell_id → ancestor_cell_id)
    _index_cells.sqlite     — gitignored; optional fast-slice index, rebuilt from cells.jsonl
  scours/                   — vacuum-cleaner scripts
    _base.py                — Scour base class
    prometheus_self.py      — first scour: greps the Prometheus repo
    (future: wikipedia.py, arxiv_tensor.py, oeis_tensor.py, mathworld.py,
     wolfram_demo.py, github_topic_tensor.py, semantic_scholar.py, etc.)
  lenses/                   — view / projection / slice scripts
    README.md
  games/                    — fun queries / exploration tools
    README.md
  artifacts/                — gitignored; per-tick / per-scour summary artifacts
  logs/                     — gitignored; daemon + scour logs
  state/                    — gitignored; persisted state across runs
```

`cells.jsonl` is the tensor body. `axes/*.jsonl` are the registries of canonical values per coordinate axis. `lineage.jsonl` is the edge list.

Cell record schema (one JSON object per line in `cells.jsonl`):

```json
{
  "cell_id": "<16-char sha256 of canonical content>",
  "coords": {
    "time": 1900,
    "discipline": "math.AG",
    "object_kind": "concept",
    "structural_rank": 3,
    "abstraction_level": "definition",
    "substrate_yield_type": null
  },
  "tags": {
    "researchers": ["Levi-Civita", "Ricci-Curbastro"],
    "lineage_ancestors": [],
    "free_tags": ["differential geometry", "absolute calculus"],
    "citations": ["DOI:10.1007/...", "arXiv:..."]
  },
  "content": {
    "title": "Tensor (mathematical object) — Ricci-Curbastro & Levi-Civita formulation",
    "body": "...",
    "equation_latex": ["T^{ij}_{k}"],
    "code_snippets": []
  },
  "source": {
    "scour": "prometheus_self",
    "scour_run_id": "...",
    "source_path": "prometheus_math/...",
    "extracted_at": "2026-05-24T..."
  },
  "first_seen_at": "2026-05-24T...",
  "last_seen_at": "2026-05-24T..."
}
```

---

## Per-tick contract

Default tick interval: **1800s (30 min)**. The daemon's job is to run the next scour in rotation and integrate its output into the tensor.

Every tick:
1. Acquire single-instance lock (`agents/polyhymnia/polyhymnia.pid`).
2. Heartbeat (`session_telemetry.register_session`, `kind="tool"`, `operator="Aporia"`).
3. Load state: scour rotation cursor, total cells, total lineage edges, anti-silence counter.
4. Pick the next scour in round-robin rotation.
5. Run the scour (it emits a list of candidate cells + lineage edges).
6. Integrate: for each candidate cell, hash its canonical content → check if cell_id exists → merge (union tag axes, update last_seen_at) or append.
7. Append new lineage edges (dedup by `(from, to, relation)`).
8. Emit per-tick artifact at `agents/polyhymnia/artifacts/tick_<ts>.json` with delta.
9. `log_work(stage='polyhymnia_tensor_growth', summary=..., output_path=...)`.
10. If the scour returned nothing → `NULL_TICK` sentinel; increment anti-silence; alarm at 50.
11. If no scours are configured → `UPSTREAM_NOT_FOUND` sentinel.
12. Persist state and release lock.

---

## The scour interface

Each scour subclasses `Scour` and implements:

```python
class Scour:
    name: str               # registry key
    interval_hint_sec: int  # daemon respects this when rotating

    def discover(self, state: dict) -> list[CandidateCell]:
        """Pull from the source, emit candidate cells.
        State persisted between runs (e.g., last-scanned cursor)."""

    def lineage(self, candidates: list) -> list[LineageEdge]:
        """Optional: emit lineage edges derived from candidates."""
```

A `CandidateCell` is a `dict` with the same shape as the on-disk cell record but without `cell_id` (computed by integrator) or `first_seen_at` (set on first append).

The base class handles:
- HTTP timeouts + retries
- Local cache to avoid re-fetching unchanged sources (`scours/_cache/<scour_name>/`)
- Rate-limit politeness (per-source minimum interval)
- Error isolation (one scour's crash doesn't take down the daemon)

---

## Scours we want (priority order)

**Round 1 (Phase 0):**
1. `prometheus_self` — grep this repo for tensor mentions. **SHIPPED** in Phase 0.

**Round 2 (Phase 0.5 — easy local + small APIs):**
2. `wikipedia_tensor` — Wikipedia's tensor portal + linked articles. Public API, no auth.
3. `oeis_tensor` — OEIS sequences tagged with tensor/multilinear/multidimensional. Already-mined source.
4. `arxiv_tensor` — arXiv search for tensor-related papers. Clio's pipeline can be reused.
5. `prometheus_math_lib` — the local `prometheus_math/` Python library, function-by-function.

**Round 3 (Phase 1 — heavier APIs):**
6. `mathworld` — Wolfram MathWorld tensor entries.
7. `semantic_scholar_tensor` — citation graph of tensor papers.
8. `github_topic_tensor` — repos tagged with `tensor`, `tensor-decomposition`, `tensor-network`, etc.
9. `nasalreservation` — NASA technical reports tagged tensor (engineering applications).
10. `wolfram_demonstrations` — interactive tensor demos with code.

**Round 4 (Phase 1+ — fringe + history):**
11. `historical_papers_archive_org` — pre-1950 tensor-mention papers from archive.org scans.
12. `quantum_info_tensor_networks` — quantum information tensor-network corpus.
13. `psychology_tensor` — yes, fringe: psychometric tensor models. The "even loosely related" promise.
14. `economics_tensor` — multi-way models in econometrics.
15. `linguistics_tensor` — vector space semantics, tensor word models.
16. `biology_tensor` — neural manifolds, single-cell tensor decompositions.
17. `meteorology_tensor` — atmospheric tensor fields.
18. `art_history_tensor` — yes, fringe: where "tensor" appears in any non-mathematical sense (Latin etymology, etc.).

The rule from James: **leave no stone unturned**. Fringe is the point.

---

## Lenses

A lens = a slice + projection + display script. Lives in `lenses/`. Examples to ship in Phase 0.5:

- `lenses/by_decade.py` — group cells by `time // 10`; show count + sample
- `lenses/discipline_x_kind.py` — 2D table: rows=discipline, cols=object_kind, values=count
- `lenses/researcher_lineage.py` — given a researcher, show all cells + their ancestor chain
- `lenses/rank_n.py` — given a structural_rank N, show every cell at that rank across disciplines
- `lenses/missing.py` — for a given slice, show the empty cells (Mendeleev-gap-style: what's not there but probably should be)

---

## Games

Live in `games/`. Examples to ship later:

- `games/random_walk.py` — start at a random cell, walk N steps following lineage edges, narrate the journey
- `games/connect_two.py` — pick two cells from very different axes (e.g., `(physics.QM, equation)` and `(cs.ML, dataset)`); find the shortest lineage path between them
- `games/complete_the_slice.py` — show a slice with one cell removed; ask the LLM (or a human) to predict it
- `games/twenty_questions.py` — pick a hidden cell; player asks yes/no questions about coordinates to narrow it down
- `games/mendeleev.py` — find the most "anomalous gap" in the current tensor — the empty cell whose neighbors are richest

These also become Learner training material: each game = a (prompt, expected response) generator.

---

## Structured logging

Same three-stream pattern as Hypatia / Atalanta / Pheme / Talos:

- **Text log** at `agents/polyhymnia/logs/polyhymnia.log`
- **Events JSONL** at `agents/polyhymnia/events.jsonl`
- **State file** at `agents/polyhymnia/state/state.json` — `{scour_rotation_cursor, total_cells, total_lineage_edges, per_scour_cells_contributed, anti_silence_counter, total_ticks_lifetime, total_null_ticks_lifetime}`
- **Heartbeat** with rich `status_json` (current tensor size, cells per axis, latest scour)
- **Work events**: `polyhymnia_tensor_growth`, `polyhymnia_null_tick`, `polyhymnia_upstream_not_found`, `polyhymnia_self_audit_null`, `polyhymnia_startup`, `polyhymnia_shutdown`, `polyhymnia_scour_<name>_run`
- **Per-tick artifact** + **per-scour-run artifact** in `agents/polyhymnia/artifacts/`

---

## Operational

**Single-instance lock:** `agents/polyhymnia/polyhymnia.pid`.

**Detached launch:** `scripts/polyhymnia_loop_launch.bat`.

**CLI:**
- `python -m agents.polyhymnia.daemon --once`
- `python -m agents.polyhymnia.daemon --loop --interval 1800`
- `python -m agents.polyhymnia.daemon status` — print tensor size + per-axis cardinality
- `python -m agents.polyhymnia.daemon lens <lens_name> [args]` — run a lens
- `python -m agents.polyhymnia.daemon scour <scour_name>` — run a specific scour now

**Hard stops:**
- Never delete cells. Append-only. If a cell becomes wrong, append a corrected version with the same coord signature — the integrator merges (latest wins on content).
- Never auto-classify into `substrate_yield_type` without an explicit basis. The default is `null` (unknown / unclassified); explicit type-tagging requires either a rule the scour author named or human input.
- Never silently drop content. If a scour can't classify into the current axes, it should still emit the cell with `null` coordinates AND an `extras` field containing the unstructured content. The axes will grow to absorb it.

**Anti-gravitational-well vigilance:** the conventional move would be to require taxonomic cleanliness — refuse to ingest anything that doesn't fit cleanly. Polyhymnia's discipline is the opposite: **ingest first, classify later**. Loosely related content gets in. The axes grow to fit. The fringe is the point. A scour that's rejecting >50% of its candidates because they don't fit the current axes is the failure mode — flag and re-orient (probably the axes need expansion).

— Aporia, 2026-05-24
