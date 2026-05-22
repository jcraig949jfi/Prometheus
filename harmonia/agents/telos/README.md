# Telos

> Stalled-specimen reviver — the negative-space patroller.

## What Telos does for Prometheus

Every live finding in Prometheus has a clock: the longer it sits at `live_specimen` tier without a fresh audit, the more likely the discipline standard has moved past it and the verdict is silently wrong. Telos is the agent whose entire purpose is to refuse to let stalled findings rot.

Each tick he reads `D:\Prometheus\harmonia\memory\frontier_specimen_state.md` for the per-F-ID state, computes stall age (days since `last_audit_outcome`), picks the most-stalled specimen past threshold (default 14 days), enumerates which lenses have not been applied yet (the gap between the F-ID's `cross_refs` and the current promoted-symbols-plus-methodology-toolkit pool), and files a *revive task* artifact proposing the next 3 audit actions.

When every live specimen is within threshold, Telos rotates into killed-F-ID patrol: he picks the lexicographically smallest never-revisited killed F-ID and asks "would current tooling un-kill this?" Retractions are not always permanent — F010 NF-backbone killed under one null model might survive under a different stratifier; F012 Möbius killed via Pattern-19 might re-emerge under the gen_06 sweep that landed after.

When both pools exhaust, Telos files a `NEGATIVE_SPACE_MAPPED@v1` candidate artifact rather than going silent. *Silence is forbidden* — validating that a specimen is dead by not asking is the reward-capture failure mode generalized to attention.

Telos's value is in counter-bias: he asks the questions the conductor stopped having time to ask.

## Where Telos sits in the pipeline

```
frontier_specimen_state.md  ┐
methodology_toolkit.md      ├──► Telos ──► revive_<FID>_*.md (live stalled)
substrate_health symbols    │             killed_revisit_<FID>_*.md (killed patrol)
retraction_registry.md      ┘             negative_space_mapped_*.md (full coverage)
```

Telos's backlog is roughly (stalled F-IDs × unapplied-lens deltas × revisit-cadence). The native backlog is large but bounded by the size of `frontier_specimen_state.md` (~50 F-IDs counting killed entries). The pool-cycle pattern (each F-ID has a finite per-FID lens pool that resets when exhausted) gives Telos unbounded *cycle* depth even when *F-ID* depth is finite.

## Output

Each tick writes one artifact to `D:\Prometheus\harmonia\agents\telos\artifacts\`:

- `revive_<FID>_<utc>.md` — for the most-stalled live specimen above threshold. Contains: F-ID + tier + stall-age-days, quoted `last_audit_outcome`, list of lenses not yet applied with full paths to their toolkit entries, list of new symbols since last audit, list of retractions in adjacent F-IDs (cross-referenced from `retraction_registry.md`), proposed next 3 audit actions with priority scores, and a seedable Agora queue task spec
- `killed_revisit_<FID>_<utc>.md` — when no live specimen is stalled past threshold. Contains: F-ID's prior kill mechanism, what was available then vs now (lens delta), verdict sketch (likely-still-killed / worth-revisit / ambiguous)
- `negative_space_mapped_<utc>.md` — when both live and killed pools exhaust. Names what's been exhaustively patrolled and proposes the gap as a substrate-primitive candidate

State persists in `state/proposed_history.json` (per-F-ID lens-proposal history with anti-duplicate dedup) and `state/last_picked.json` (anti-greedy: don't pick the same F-ID two ticks in a row, when alternatives exist).

## Pool-exhaust mechanics

For each F-ID, Telos tracks every lens he has proposed. When `candidates_after_dedup` empties (all unapplied lenses have been proposed at least once across prior ticks), the pool exhausts: `proposal_pool_exhausted=True` fires in stats, the proposed-history for that F-ID resets to `[]`, and the next tick starts a fresh rotation. This is the designed long-cycle behavior — it keeps Telos generating distinct artifacts indefinitely even on a small F-ID set.

## Current state

Telos has produced **440 artifacts** across ~54 hours of operation. He has logged **14 pool-exhausts** in the last 24-hour rolling window, predominantly alternating F011 (stall 30d) and F014 (stall 32d) under the anti-greedy rotation.

Per-F-ID proposal histories at last check: **F011 = 15 lenses**, **F014 = 12 lenses** (mid-cycle on both). The pool-exhaust → reset → restart loop is the designed behavior and has been observed firing cleanly in production multiple times.

## How to use Telos's output

- **As an auditor**: pick the newest `revive_*.md` for the F-ID you care about. The "proposed next 3 audit actions" are paste-ready Agora task specs.
- **As a retraction-skeptic**: read `killed_revisit_*.md` to find killed findings worth reconsidering under current tooling.
- **As coverage cartographer**: `state/proposed_history.json` tells you exactly which lenses Telos has surfaced as gaps per F-ID. The unioned set is the running negative-space map.

## Roadmap (short)

- **F-ID coverage breadth is the biggest gap.** Today Telos picks the top-stalled by `last_audit_outcome` date and anti-greedy rotates between F011 and F014. The other live stalled specimens (F013, F041a, F045) almost never get picked because their stall-age is lower. A round-robin-across-top-N selection (not just top-1-with-anti-greedy-veto) would distribute attention more evenly.
- **Per-cell granularity.** Currently Telos works at the F-ID level. The tensor has F-ID × P-ID cells; each cell is a candidate revive target with its own stall age. Lifting Telos to per-cell granularity multiplies his addressable backlog by ~30 (the projection axis).
- **Consumer-side: nobody actually runs Telos's proposed audits.** Revive tasks accumulate in `artifacts/`; no downstream agent picks them up. The natural improvement is a consolidator (Techne or Charon) that, when an audit IS run, posts the result back so Telos can update the F-ID's `last_audit_outcome` and reset that F-ID's proposed-history for a fresh cycle.
- **Killed-F-ID revisit is rarely triggered.** Telos only patrols killed when no live specimen is above threshold; that's almost never the case in practice. A small modification — patrol killed in proportion (e.g., 1 in 5 ticks deterministically) — would surface retraction-reconsideration candidates without waiting for a quiet period.
- **DR enqueue is unimplemented.** Unlike Phylax and Argos, Telos doesn't enqueue Pythia DRs. The natural integration: when a revive task names a lens with no known primary-literature precedent, fire a doctrine-compliant DR asking "has anyone applied <lens> to <specimen-family> since 2024?" Substrate type C (paradigm refinement) would fit cleanly.

See `D:\Prometheus\harmonia\agents\ROADMAP.md` for the cross-swarm picture.
