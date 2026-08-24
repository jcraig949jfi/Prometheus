# Library Learning — Neighbour Study

**Opened:** 2026-08-24 · **Closed:** 2026-08-24, 8 passes
**Status:** COMPLETE. Loop stopped. Ownership passes to the **Lexis** seat (`roles/Lexis/ROLE.md`).
**Constraint:** study only. No Apollo, Hephaestus or forge code or plans were changed.

---

## Why this exists

Aporia's literature cross-reference surfaced `arXiv:2006.08381` (DreamCoder) and, through it, four
active research families that have independently built systems whose *shape* resembles the
Prometheus forge → library → reuse loop. This directory is a **study of the neighbours**, not a
change proposal.

**Operator constraint (2026-08-24):** do not hand this to Apollo or Hephaestus, and do not adjust
their code or plans on the strength of it.

## Read these first

| Document | What it is |
|---|---|
| [`SIDE_BY_SIDE.md`](SIDE_BY_SIDE.md) | **The deliverable.** Consolidated comparison, component by component. |
| [`RETROSPECTIVE.md`](RETROSPECTIVE.md) | Step-by-step second pass over all eight iterations, with the corrections ledger and what each pass missed. |
| [`SOURCES.md`](SOURCES.md) | Complete bibliography, every source graded primary / secondary. |
| `../ROLE.md` | The seat that now owns this slice, with pre-committed gates G0–G4. |

Published reference page: <https://claude.ai/code/artifact/651a056a-3c93-4d31-b59e-e94bbdbb7d2d>

## The four families

    A · MIT library learning      DreamCoder → LAPS → Stitch → LILO
    B · UW e-graphs               egg → Ruler → babble → Enumo · ShapeCoder
    C · Chalmers theory expl.     QuickSpec → Hipster → Lemmanaid → Twitch
    D · LLM tool/skill libraries  LATM · Voyager · TroVE(+refutation) · ReGAL · DreamProver

Twitch (2026) is the **junction** of A/B and C, not a descendant of either.

## Working record

| Pass | Subject | File |
|---|---|---|
| 1 | Lineage map, primary sources, first technical model, Prometheus-side reality check | `notes/PASS_01_lineage_map.md` |
| 2 | Apollo crossmap — O1's measured expressivity ceiling vs library growth | `notes/PASS_02_apollo_crossmap.md` |
| 3 | Admission-criterion taxonomy; the field's own compute-matched kill; DreamProver | `notes/PASS_03_admission_criteria_and_the_open_frontier.md` |
| 4 | Gene extractor read in full; O1 substrate resolved; babble's e-graph fit | `notes/PASS_04_gene_extractor_and_the_e_graph_fit.md` |
| 5 | Static audit — 0/26 undeclared writes; 39 of 45 pairs commute | `notes/PASS_05_commutation_audit.md` |
| 6 | Consolidated side-by-side; AutoDoc and crossover-vs-decomposition | [`SIDE_BY_SIDE.md`](SIDE_BY_SIDE.md) |
| 7 | The forge half — the ratchet exists, and was measured at 0% primitive usage | `notes/PASS_07_the_forge_half.md` |
| 8 | Wider survey — four families; criterion 5 was never ours | `notes/PASS_08_wider_tool_survey.md` |

## What survived eight passes

- **0.833 is an expressivity ceiling of Apollo's blackboard substrate, measured by exhaustive
  enumeration.** 16.7% of its battery is unreachable in that vocabulary regardless of search.
- **39 of 45 operator pairs in O1's ceiling pipeline commute; zero undeclared writes across 26
  operators.** The bug that voided two O1 runs was statically derivable from existing metadata.
- **The forge has a tiered ratchet whose promoted primitives were measured at 0% usage** — and
  compressivity would have prevented that by construction, while novelty-gating invites it.
- **Cross-domain transfer of learned primitives is unreported across all four families**, and is the
  stated cloud-spend precondition. The field's frontier and ours are the same line.
- **The distinctive asset is the corpus, not the method.** Eight passes of attempted falsification;
  every methodological-novelty claim collapsed. Diomedes said this on day one.

## Standing cautions

- Eight claims were made and withdrawn during this study. They are listed in `RETROSPECTIVE.md` §9,
  not quietly patched. Six of the eight share one cause: **interpreting before reading** — our code
  or theirs.
- Much of pass 8 is graded `[S]` (secondary). Nothing marked secondary in `SOURCES.md` should be
  quoted as measured.
- A tool-fit result is not progress toward the goal. This study produced one, and it is seductive:
  a better abstraction tool over a substrate capped at 0.833 by construction still cannot exceed
  0.833.
