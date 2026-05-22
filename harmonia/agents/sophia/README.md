# Sophia

> Coordinate-system scout — generates new axes for measuring the substrate.

## What Sophia does for Prometheus

Sophia is the swarm's offensive layer for the project's north-star directive: *compressing coordinate systems of legibility, not laws*. The unit of discovery in Prometheus is "invariant under a specific projection" (Pattern 6), not "universal law" — and what makes that work is having more projections available than humans have named. Sophia generates those projections continuously.

Each tick she draws one operator from the methodology toolkit (`D:\Prometheus\harmonia\memory\methodology_toolkit.md` — K̂ compressibility, critical exponent, MDL, channel capacity, RG flow, free energy, Gini coefficient, TT-approximation, etc.) and pairs it with one specimen from the current frontier set (live calibration anchors F001–F009 plus stalled live specimens F011, F013, F014, F041a, F042, F044, F045). The pair becomes a *proposal artifact*: a paste-ready spec for how the operator could be applied to the specimen, with a calibration-anchor sanity gate as the explicit anti-reward-capture safeguard.

The discipline is: every proposed composition MUST include at least one calibration anchor for sanity-checking. An operator that finds a "novel axis" but fails its own instrument's basic check is artifact, not discovery (the F043 failure mode, generalized). Sophia hard-encodes this rule — no proposal lands without a calibration anchor in the gate slot.

Sophia produces *proposals*, not measurements. She never executes the scorers. Her value is measured in (operator × specimen) pairs that, when actually executed by Techne or Charon downstream, produce calibrated and non-tautological scoring functions.

## Where Sophia sits in the pipeline

```
methodology_toolkit.md ──┐
frontier_specimen_state ─┴──► Sophia ──► proposal_<OP>_x_<FID>_*.md
                              │
                              └──► [if grid exhausted]
                                    └──► meta_expand_toolkit_*.md
```

Sophia's backlog is the cartesian product (operators × specimens). With the default toolkit shelf (10 operators) × current live frontier (~14 specimens), that's a 140-pair grid. She burns one pair per tick at ~7.5-minute cadence, lexicographically smallest untried first.

## Output

Each tick writes one artifact to `D:\Prometheus\harmonia\agents\sophia\artifacts\`:

- `proposal_<OP>_x_<FID>_<utc>.md` — full proposal with operator frame, specimen tier, proposed scoring procedure, calibration-anchor sanity gate, 5-gate tensor-admission stub (null-calibrated / representation-stable / not-marginals / non-tautological / domain-agnostic — left UNFILLED for the executor to complete), and a seedable Agora queue task spec
- `meta_expand_toolkit_<utc>.md` — when the grid exhausts, propose-only artifact suggesting new operators to add to the toolkit (DeepSeek-drafted when available)

State persists in `state/tried_pairs.json` (lifetime list of "OP@vN×F0XX" strings). To reset: `state/reset_requested.json`.

## Current state

Sophia has produced **438 artifacts** as of 2026-05-22 morning. She **exhausted her original 140-pair grid** at 2026-05-20 05:46 UTC and has been in meta-task fallback mode since — currently producing one `meta_expand_toolkit` artifact per tick proposing operator-shelf expansion candidates.

The grid exhaustion was the first time any swarm agent fell through to its self-generated backlog path in production. The transition was clean — the next tick correctly emitted a meta-task, and the loop has been stable since.

She has touched 10 toolkit operator rows across the run:
`CHANNEL_CAPACITY → CONJECTURE_GENERATOR → CONTROLLABILITY_RANK → CRITICAL_EXPONENT → FREE_ENERGY → GINI_COEFFICIENT → KOLMOGOROV_HAT → MDL_SCORER → RG_FLOW → TT_APPROX_MAP`

## How to use Sophia's output

- **As a methodology architect**: read newest `proposal_*.md` and pick the ones with calibration-anchor gates you'd actually want to run. Each artifact has a "next step" line that's a seedable Agora task spec.
- **As Techne / Charon**: a proposal that survives reviewer attention is a candidate for scorer implementation. The 5-gate stub is the contract Techne would fulfill when materializing the scorer.
- **As a curriculum**: the cross-product traversal pattern is itself useful pedagogy — seeing K̂ applied to every active specimen surfaces which operators *can't* be applied where (e.g., toolkit operators with no canonical fingerprint for a given specimen tier).

## Roadmap (short)

- **Backlog expansion is the most urgent need.** With the toolkit shelf at 10 operators, the grid (140 pairs) was always going to exhaust within ~17 hours of continuous ticking. Three obvious expansion axes:
  1. **Promoted symbols as operators** — 24 promoted symbols (AXIS_CLASS, NULL_*, PATTERN_*, CND_FRAME, etc.) added to the operator pool → 34 operators × 14 specimens = 476 pairs (~57 hours of runway)
  2. **k=2 operator compositions** — 34² operators → 16,184 pairs (~80 days)
  3. **Cross-disciplinary operator transplants** — physics, info-theory, complexity-class invariants pulled in via Pythia DR (Sophia could enqueue DRs asking "what coordinate systems exist in field X that we haven't named")
- **Consumer-side: nobody runs Sophia's proposals.** They sit in `artifacts/` as paste-ready specs but no downstream actor turns them into actual scorers. The 5-gate tensor-admission stub is a contract waiting for a counterparty. The natural next step is a Techne or Charon agent that picks the top-ranked Sophia proposal each day and implements it. Until then Sophia's yield is measured in proposals filed, not scorers shipped.
- **Calibration-anchor pairing is currently lexicographic.** F001 gets paired with everything (F001-then-everything-else-against-F001). A smarter pairing would diversify anchor coverage so every operator gets gated against multiple anchors, not just the lowest-numbered one.
- **`meta_expand_toolkit` artifacts are propose-only.** They have no concrete consumer — they accumulate while no one actually grows the toolkit. A consolidator that batches these into a single weekly "toolkit expansion proposal" doc would be more actionable than a stream of identical files.

See `D:\Prometheus\harmonia\agents\ROADMAP.md` for the cross-swarm picture and the shared scoring-primitive thesis.
