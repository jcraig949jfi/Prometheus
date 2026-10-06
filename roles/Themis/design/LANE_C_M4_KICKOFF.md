# Lane C / M4 -- Commodity Fabric: kickoff (start here after reset)

> **Superseded in part, 2026-10-06.** Lane C is running as campaign C-008 under operator approval
> OP-LC1 (roles/Themis/prompts/2026-10-06_op_lc1/). Its contract is moonshot/epoch/CONTRACT.md:
> semantic identity is independent of git SHAs; a successful CAS is PUBLISHED (not "accepted");
> D3 has twelve cases, not seven; D4 bounds are frozen in ops/campaigns/C-008/prereg/ before any
> baseline. This file is kept as the reset entry point it was.

Owner: Themis. Thread: TH-MOON-M4. Epic: EP-MOONSHOT. Date: 2026-10-06.
Design of record: roles/Themis/design/MOONSHOT_DESIGN_v0.3.md (R-EP, N1, N3, N4, N7, S7, S12,
S17). Full program context: operator auto-memory project_moonshot_rso_lane. This doc is the
concrete entry point for the next working session.

## Why Lane C first

It is the one lane that depends on nothing else. It needs no trustworthy evolutionary substrate
(Lane B / wforge F09), no RSO claim map (Lane A), no organisms, no world science, no S-meter.
It is pure **engine/infrastructure TDD -- layer 1, tests MUST pass** (design S17.1). It de-risks
the distribution layer and tests the operator's standing hypothesis that git compare-and-swap is
an adequate transport at this scale, using the seven-node fleet as the stress rig -- before any
expensive science rides on it. Gated items (evolutionary science, Launchpad population, paid
cloud) are untouched by this lane.

## Scope: SYNTHETIC EPOCHS ONLY

A Lane-C "epoch" does fixed, deterministic CPU busy-work and advances a dummy checkpoint. There
are NO organisms, NO world physics, NO sagacity scoring. The point is to exercise the shard-epoch
commit semantics (R-EP), the workgraph transport, and cross-host canonical-trace identity (N1) in
isolation. Anything science-shaped is explicitly out of scope here.

## Deliverables (each is test-first; a unit is done when its layer-1 tests are green)

- **D1 -- synthetic epoch unit (R-EP).** `immutable checkpoint + epoch spec -> trace + next
  checkpoint`. Semantic epoch identity = sha256(input-checkpoint hash, epoch-spec hash, runtime
  version); execution-attempt IDs/costs kept separate. Output blobs made durable BEFORE a verified
  completion manifest (binding input/spec/trace/output) is atomically exposed.
- **D2 -- CAS successor publication on workgraph.** Exactly one accepted successor per parent
  checkpoint via an explicit compare-and-swap; duplicate equal attempts are idempotent;
  disagreeing outputs are quarantined; a stale worker cannot advance the accepted chain; retry
  costs are charged even when the result is discarded. An ordinary epoch retry must never look
  like an RSO content-reset intervention.
- **D3 -- fault-injection test matrix (all MUST pass).**
  1. duplicate execution: two workers, same parent -> one accepted successor, no double effect.
  2. worker death mid-epoch -> requeue from the input checkpoint, exactly-once successor.
  3. lease expiry -> reclaim without corrupting the accepted chain.
  4. CAS collision: two completions race -> one wins, the other is idempotent or quarantined.
  5. git remote outage -> worker degrades safely; gains NO consumer/promotion authority from a
     push (N3); no partial-claim semantics.
  6. idempotent replay: replaying two chained epochs == uninterrupted execution.
  7. heterogeneous-host canonical trace: the same epoch on different ubu nodes -> identical
     canonical trace (N1 semantic identity; host/perf metadata in a separate receipt).
  Fault-inject before AND after blob durability, completion publication, and lease expiry.
- **D4 -- transport metrics + preregistered reconsider threshold.** Instrument claim latency,
  push/ref contention rate, abandoned-epoch rate, repo/ref growth, and the useful-CPU /
  coordination-CPU ratio. PREREGISTER (before the baseline run) the threshold at which git-CAS
  must be reconsidered -- e.g. coordination-CPU fraction above a stated bound, or push-retry rate
  above a stated bound. Record it; do not tune it after seeing the data (this is a layer-3-style
  precommitment even though the lane is infra). GitHub push rate-limits are a specific early watch
  item, ahead of raw branch contention.
- **D5 -- node auto-join (N7), parallel/stretch.** A fresh e-waste Ubuntu node joins and drains
  synthetic epochs with only Python + git + a push credential; auto-join must NOT auto-authorize
  arbitrary code, and the push grants no scientific authority (N3).

## Acceptance (from design v0.3 R-EP/N1/N4)

One accepted successor and complete evidence under every injected fault; two chained epochs
replay-match uninterrupted execution; renaming/reordering host metadata leaves the canonical
trace unchanged; the reconsider-transport threshold is recorded before the baseline, and the
baseline reports the five metrics against it.

## First steps for the next session

1. Open a bounded campaign under TH-MOON-M4 (ops/campaigns/) or begin in this worktree; write
   the D3 fault matrix as failing tests FIRST (TDD layer 1).
2. Implement D1 + D2 to pass them.
3. Preregister D4's threshold, then baseline on ubu001-006.
4. D5 as a parallel track.

## Out of scope / do not do here

No organisms, world physics, S-meter, RSO evidence, or wforge changes. No evolutionary science,
no Launchpad population, no paid cloud. Lane A (claim map, needs Palamedes) and Lane B (wforge
F09 regression -> Daedalus) proceed separately. Lane C is self-contained and needs no external
coordination to start.
