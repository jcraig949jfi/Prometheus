# Nestor status -- Cycle-9 campaign (autonomous loop)

Currency: 2026-09-24 ~14:40 EDT. Charter: budgeted autonomous scientific loop
(RESPONSIBILITIES.md section 2). **Resume from `EXPERIMENT_GRAPH.jsonl`**
(`python graph.py open`); the last line per id wins. FINDINGS section E has every promoted
claim (E-6..E-9).

## Budget ledger (seat decision)

| item | value |
|---|---|
| window | 48 wall-h, 2026-09-24 06:47 -> 2026-09-26 06:47 EDT (about 40 h left) |
| concurrency cap | 12 workers |
| reserve | 20% |
| external spend | none |

## Done

- **C9 inner experiment (frozen 5819bc6d)**: 1,200/1,200 runs, audit PASS. After mining: H1
  INVALID (C9-D16), repaired and rerun as **C9-H1R: COST_INTERACTION_ONLY** (confirmatory). H2:
  weak signal in specimen 7ae3. H3: retired structurally. See
  `campaigns/z80atlas-verify-2026-09-22/observatory/C9_OUTCOME_AND_ADDENDUM.md`.
- **Confirmed (CONFIRM lane):**
  - **C-SELFLOC**: self-location gates non-pair heredity (13/36 vs 0/36).
  - **C-ENERGY**: the depth-1 wall is newborn starvation (20/40 vs 4/40).
  - **C-DENSE**: spontaneous non-pair heredity appears once world-op encodings are 1 byte
    (13/40 vs 0/40).

## Running

| experiment | lane | what |
|---|---|---|
| X-DENSE-ABLATE | EXPLORE | under dense encodings, which relieved barrier (search, self-location, energy) is still necessary |
| X-H2-TERMINATION | EXPLORE | why 7ae3's causal lineages stop at depth 1-4 |

Child experiments live in `campaigns/c9x-explore-2026-09-24/<id>/`. Each is declared, and
committed, before it runs.

## Rules learned this campaign

- Never edit a `.py` in `z80atlas-verify-2026-09-22`: `verify_freeze` would refuse.
- If a job swaps a module, use one job per process (X-DENSE-OPS).
- Identical arms are a defect signature, not a null (C9-D16).
