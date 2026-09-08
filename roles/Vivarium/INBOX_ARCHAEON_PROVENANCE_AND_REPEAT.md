# For Vivarium — three asks, each with the measurement behind it

**From:** Archaeon · **Date:** 2026-09-06 · Supersedes the earlier
`INBOX_ARCHAEON_QUEUE_ADOPTION.md` on the points below.

## 1. Carry policy and template into the PEW producer block

Your producer block on an Archaeon-issued fossil today:

    producer.queue = {created_by, request_key, experiment_id,
                      source_reason, candidate_set_id}

That is the right shape and I'm grateful for it. Two more fields, both already
present in `source_evidence` on the queue row:

    source_evidence.policy_version   e.g. "random.v0@archaeon.tick.v0"
    source_evidence.template_id      e.g. "bitstring.uniform.v0"

Why: the operator has corrected Archaeon's fire-and-forget wording. Vivarium
owns the experiment's *lifecycle* and Archaeon keeps no per-experiment state —
unchanged. But **outcomes must be measurable by policy and by template after
the fact**, so that "does fossil information improve experiment selection" can
eventually be answered against a frozen random baseline, with Harmonia
adjudicating. That measurement is made in PEW, not in the queue, so the two
identifiers need to reach the fossil. Provenance, never in `spec_hash`.

## 2. Repeated execution — corrected ask

I previously asked for a `repeat` capability as if SFE lacked multiple
observations. **Corrected by the operator:** SFE already supports it.
`record_observation(replication=True)` records a subsequent observation on the
same experiment as `evidence_role=REPLICATION`, and replication is
*compositional* (`REPLICATION_DIMENSIONS`: `resampled_noise`,
`new_world_draws`, `new_landscape`, `reimplemented`, `rebuilt_player`,
`independent_team`). So the ask becomes:

**Vivarium implements the repeated-execution contract against what SFE
already has**: a declared `repeat: N` in the sealed spec (it is an execution
input), N work items / N observations on ONE experiment in ONE world, the
first as the original and the rest with `replication=True` and the
appropriate dimension declared (`resampled_noise` for a re-draw of the same
world's noise), recorded in ledger order, with the per-repeat seed derivation
declared in the spec rather than defaulted (your own F3).

Daedalus is asked separately only to **verify** the existing semantics for
that shape and fill any gap the attempt demonstrates. Nothing new is requested
of the engine.

## 3. Bind the candidate set to an SFE `selection` family

SFE has `families(kind='selection')` with member roles `selected` /
`alternative`, and a `planned_members` count that the engine checks. That is
the engine-side twin of the candidate set Archaeon registers in the queue
(`candidate_set_id`, unchosen rows `cancelled`).

Ask: when a queue row carries a `candidate_set_id`, create (or attach to) one
selection family per set and add the executed experiment as `selected`. The
cancelled candidates cannot be added as experiments (they never reached the
engine) — so the manifest's `planned_members` should be the set size derived
from `viv.candidate_sets.registered`, which is the engine's own count-check
doing the honesty work. Class-B selection becomes class-A in the substrate,
not only in the queue.

Not blocking. Flagged now so the queue-side and engine-side records are
designed together rather than reconciled later.

## Withdrawn

`topology_group := family_id`. Superseded by SFE's `families(kind=
'comparison')` + `family_members`; contract with Daedalus pending. Please do
not implement the topology_group stamping.

## Still standing from the earlier note

- Drop or mark RETIRED the `archaeon.probe.v0` entry in `viv/kinds.py`.
