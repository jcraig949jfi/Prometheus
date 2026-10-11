# TH-MOON-M4 -- Commodity Fabric

epic: EP-MOONSHOT

Status: OPEN. Type: INFRASTRUCTURE/EXPERIMENT. Opened 2026-10-05 by the operator (verbatim:
roles/Themis/prompts/2026-10-05_epic_approval_and_review/). Owner: Themis. Supports: H1-infra.

## Question / capability
Turn the seven-node Linux fleet into a working wide-tier substrate AND treat the distribution
transport as an experiment, not a solved problem. Deliverables: node auto-join (N7); the
shard-epoch durable unit (immutable checkpoint + epoch spec -> trace + next checkpoint, atomic
publish, design doc R-EP) so node death has no semantic effect; and an instrumented study of
the git compare-and-swap work plane -- claim latency, push/ref contention, abandoned-epoch rate,
repo/ref growth, and the useful-CPU/coordination-CPU ratio -- with a PREREGISTERED threshold at
which the transport must be reconsidered (GitHub push rate-limits are a specific early watch
item). Seven e-waste boxes are the stress rig to find that threshold before 100-1,000 workers.

## Campaigns
- C-008 (OPEN 2026-10-06, operator OP-LC1; ops/campaigns/C-008/): Lane C on synthetic epochs --
  T001 D1+D2 under the twelve-case D3 matrix (test-first), T002 D4 preregistration (bounds frozen
  before any baseline), T003 D4 local-network baseline (single-ref vs per-chain, disposable LAN
  bare remote), T004 one bounded GitHub WAN-semantics arm (<=2 workers, <=250 write attempts),
  T005 D5 node auto-join without auto-authorization. Contract: moonshot/epoch/CONTRACT.md (git SHA
  = transport identity; successful CAS = PUBLISHED, validation separate). Entry point was
  roles/Themis/design/LANE_C_M4_KICKOFF.md.
- C-012 (OPEN 2026-10-10, operator OP-NF2; ops/campaigns/C-012/): native execution fabric -- Moonshot epochs on
  the program's PostgreSQL via Fabric v0.2 (as-is) with a versioned Moonshot publication schema and Pan's lake for
  derived evidence. Supersedes C-008's Git-CAS runtime plan; C-008 T003/T004 SUPERSEDED unexecuted (no verdict).
