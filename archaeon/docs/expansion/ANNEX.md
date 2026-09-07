# Diversity and expansion — annex index

Supporting material for `archaeon/docs/ROADMAP.md` §Diversity and expansion
(2026-09-07). The roadmap is the readable, maintained document; this
directory holds the evidence and the detail it points to.

## Starting point (revisions behind the assessment)

| What | Where | Revision |
|---|---|---|
| Archaeon (charter, registry, producer, tests) | `archaeon/`, `roles/Archaeon/` | `archaeon/v0` at `073091863`, merged with `origin/main` → `325cf497e` |
| SFE engine | `SerendipityFoundry/SerendipityFoundryEngine/sfe/` | `be65b0efa` (v7 LIVE on M1; schema_version 7 confirmed by `readback_probe` 2026-09-07) |
| Vivarium | `F:\Prometheus\vivarium` on `vivarium/v0-2026-09-05` | `19e13e5b1`; campaign branch `worktree-vivarium-campaign-e1-e6-e16` at `621bdfeb9` (E1 design_hash, E6 selection families, E16 aggregate) |
| PEW | `evidence_wiki/` | `ec49be22d`, schema 4, `pew.fossil.v2` |
| Harmonia ruling | `roles/Harmonia/rulings/RULING_ARM_LEVELS_D3_MSIGNAL_2026-09-06.md` | `5759518f0` |
| Daedalus arm binding + read scopes | `sfe/` | `642736763` |
| Herakles mining + expansion pass | `roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/` | `19ad79d2e` (69 PROPOSED), `284022624` / `19e13e5b1` (matrix, capabilities, portfolio) |
| Live release-condition probe | `python -m archaeon.producer.readback_probe` | 2026-09-07: v7 live; granted readback **false** (200, 0 rows — no scope granted to `cli_1029e9255a074157a1b3ba1e`); arm-bound round trip **false** |

The 2026-09-06 reports are historical inputs; every claim in the roadmap was
re-checked against the revisions above.

## Files

- `CROSSWALK.md` / `crosswalk.json` — all 69 proposals by stable ID: question,
  competing explanations, representation/dynamics/actions/observations,
  dependencies, must-survive / can-change / proxy-would-lose, faithful route
  vs bench proxy and the difference in claims, destroyed parameters and
  entailed repairs, Herakles's reference grade (not re-graded), adjacent
  Prometheus home, branch.
- `ASSETS.md` — reuse audit of existing machinery at four maturity levels with
  the command or document behind each level.
- `SOURCES.md` — capability inventory of SFE, Vivarium and PEW with file:line
  citations; what the record can hold today.
- `CHARTERS_SURVEY.md` — Harmonia's current rulings and every seat's
  owns / must-not / top-TODO / inbox status, used to route requests.
- `BRANCHES.md` — the branch designs: worlds, organisms, interfaces,
  nulls, controls, first experiments, what each branch cannot do.
- `INFRASTRUCTURE.md` — what stays common, what stays family-specific, how
  raw material is preserved, C-0…C-6 reassessed, concrete contract changes,
  what would need a different architecture.
- `SELECTION_RULES.md` — R1–R8: reserve allocation, retention, coverage
  without a universal score, label-vs-behaviour, matched nulls, transfer
  through declared mappings, research leads, LLM boundaries.
- `GRAPH.md` — dependency graph (mermaid + text).
- `WORK_PACKAGES.md` — the compact table and per-package notes.
- `DECISIONS.md` — D-1…D-12 with options and recommendations.

## Counting rules kept separate (per the assignment)

Parameter completeness (`check().drawable`), executor availability
(`check().runnable`), scientific design completeness (crosswalk
`must_survive` / `faithful_route`), semantic fidelity (crosswalk
`claim_difference`), reference verification (crosswalk
`reference_grade_herakles`, Herakles's own, unfetched for most), measurement
qualification (Harmonia's rulings only; today D3 for region discrimination on
a frozen corpus, and nothing else).

## Owner requests filed from this work

- `roles/Herakles/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
- `roles/Vivarium/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
- `roles/Daedalus/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
- `roles/Harmonia/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
- `roles/Mnemosyne/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
- `roles/Proteus/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
