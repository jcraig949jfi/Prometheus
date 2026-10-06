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
- (none yet) First work is specified in roles/Themis/design/LANE_C_M4_KICKOFF.md (the reset
  entry point, 2026-10-06): synthetic epochs only; D1 R-EP epoch unit, D2 CAS one-accepted-
  successor, D3 seven-case fault-injection matrix (tests first), D4 transport metrics + a
  preregistered reconsider-transport threshold, D5 node auto-join. Pure layer-1 must-pass TDD;
  no evolutionary substrate, no science, no external coordination needed. Open a bounded
  campaign here and begin.
