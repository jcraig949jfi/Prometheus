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
- (none yet) First: stand up auto-join + epoch replay on ubu001-006; baseline the CAS metrics
  under the Launchpad workload; set the reconsider-transport threshold.
