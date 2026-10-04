# Operator Directive — Aporia

Proceed with the routing, with the modifications below, and then make your primary job for the next several hours **M1 quiescence and Phase 2-B reseating preparation**.

Phase 3 is already running. Do not pull Phase 3 builders into this work.

## 1. Clear the current routing backlog

### Cosmos / Theseus C4

Re-ping Theseus with the existing assignment and require an explicit acknowledgment.

Do **not** reassign this work to Achilles. Achilles is fleet/control-plane infrastructure and is not to become a science seat.

If Theseus does not acknowledge within the next normal heartbeat window, mark the C4 dependency subtree:

`HOLD_REHOME`

Record:

- Cosmos blocked;
- Ananke blocked;
- Bellerophon blocked;
- original assignment;
- last attempted contact;
- exact dependencies.

Do not launch another scientific seat merely to clear this before the M1 reset.

This becomes a Phase 2-B re-entry item and can be assigned cleanly after the seats are redistributed.

### Epimetheus defects

Route now, but classify them by program scope.

Treat these as **GLOBAL / MEDIUM** control-plane defect reports:

- `comms/manifest.py` short-binary hash collision;
- `comms/identity.py` registry record lacking database identity;
- `archaeon/workspace.py` fail-open behavior on git errors.

Route them to the appropriate existing owner; Archaeon may receive the bounded reports if that remains the established repair lane.

Do not require an M1 seat to begin a substantial repair while it is being drained. The defect packet survives the reseat.

Route these as **Phase 2-B / LOW** owner-verification items:

- Proteus VM tick counter;
- Harmonia t-test degrees-of-freedom rounding.

They should become part of those seats' Phase 2-B hardening intake rather than emergency repairs.

### Nestor X-TASK-GATE

Acknowledge and record:

`DO_NOT_DISPATCH_AS_FROZEN`

The stage-0 preregistration cannot exercise the ruler required for stage 1.

No execution occurred.

Carry the required amendment into Nestor's Phase 2-B intake.

### Nyx ASAL replication

Acknowledge only.

Harmonia owns adjudication.

No duplicate routing.

### Hecate C1-C8

Do not ask the operator to resolve these during the machine reset.

Record them as pending scientific rulings and route them to **Harmonia for Phase 2-B adjudication** when Harmonia is relaunched.

Hecate should preserve its revised/red-teamed question set unchanged.

### Dionysus custody exposure

Record the incident durably.

The one-line holdout exposure was redacted and Dionysus is requesting no immediate action.

Route the eventual custody ruling to Harmonia / the appropriate evidence owner after Phase 2-B seating.

Do not wake Mnemosyne solely for this.

## 2. Adopt Achilles census

Yes.

Stop maintaining the hand-built `ops/fleet/CENSUS.json` as an independent live census.

Adopt Achilles's generated census/provenance system as the canonical fleet census.

Preserve the old file as historical material if required by repository archaeology; do not maintain two competing truths.

---

# 3. Begin M1 DRAIN

Issue a machine-scoped control order:

**M1-DRAIN-2026-10-03**

Its purpose is to slowly quiesce every named seat and agent currently operating on Machine 1.

This is not an emergency shutdown.

The machine remains usable while seats finish bounded closure work.

From receipt of the drain order, M1 seats must:

- claim no new scientific Campaigns;
- claim no new long-running Tasks;
- begin no new experiment that cannot finish during drain;
- finish their current smallest safe unit of work;
- preserve all uncommitted state;
- reconcile their Git state;
- emit a drain receipt;
- stop.

A seat may finish a short atomic operation needed to make its state durable.

It may not interpret "finish in place" as permission to start another campaign.

---

# 4. Use Achilles census to generate the M1 inventory

Do not reconstruct the seat list manually.

Generate the M1 drain roster from current Achilles census plus repository/worktree/process observations.

For every seat/process on M1 record at least:

- seat;
- current state;
- PID/session/tmux identity if applicable;
- checkout/worktree;
- local branch;
- HEAD SHA;
- upstream;
- dirty state;
- untracked state;
- unpushed commits;
- divergence from `origin/main`;
- current Task/Campaign;
- active experiment/process;
- expected safe stop point;
- branch disposition;
- drain status.

Keep this as a machine drain ledger under an appropriate `ops/` or Achilles/Aporia operational path.

---

# 5. Branch disposition

Every branch encountered on M1 must end in one of three explicit states.

## MERGE

Use when the branch contains completed work intended for main and its relevant acceptance conditions pass.

Process through the repository's normal merge path.

Record merge SHA.

## ARCHIVE

Use when work is historically/scientifically valuable but should not be merged into current main.

Before deleting the branch:

- commit all meaningful state;
- push it;
- create a durable archive reference/tag or equivalent immutable reference;
- record tip SHA;
- record why it was not merged;
- record what future seat/Campaign owns reconsideration.

Then the working branch may be deleted.

## DISCARD

Use only when a seat explicitly establishes that the material is disposable generated/scratch state.

Record that decision and enough identity to prove what was discarded.

Do not silently delete unknown work.

The desired outcome is not:

> every branch becomes main.

The desired outcome is:

> every branch has an intentional, recoverable disposition.

---

# 6. No work stranded locally

Before a seat is considered drained:

- meaningful modifications are committed;
- commits exist on a remote or durable archive ref;
- HEAD SHA is recorded;
- relevant receipts exist;
- no unique scientific artifact exists only on M1;
- no active experiment is silently killed;
- no untracked meaningful data is abandoned.

If a branch cannot be understood safely during the drain, classify it `ARCHIVE / NEEDS_REVIEW`, preserve it, and continue.

Do not burn model inference reconstructing months of history merely to make the branch aesthetically clean.

---

# 7. Sync after seat drain

Once all users of a checkout/worktree are quiescent:

- fetch current origin;
- verify ancestry;
- remove obsolete worktrees according to the working contract;
- delete resolved local branches;
- delete resolved remote working branches after their merge/archive disposition is durably recorded;
- leave the canonical repository in the repository-approved synchronized state corresponding to `origin/main`.

Do **not** use casual `git pull` in the canonical checkout.

Use the current working-contract synchronization procedure.

---

# 8. Process/session cleanup

Branch cleanup alone is insufficient.

For each M1 seat, verify that after closure there are no unintended:

- agent sessions;
- tmux sessions;
- long-running experiment processes;
- watchdogs specific to the retired session;
- stale worktree leases;
- stale task leases;
- machine-local scratch workers.

Do not disable legitimate machine-global infrastructure merely because a seat used it.

Record anything intentionally left running.

---

# 9. Produce a Phase 2-B re-entry manifest

While seats drain, create a **re-entry manifest**, not new science.

For every non-parked engine/scientific seat, capture:

- seat;
- native engine/charter;
- last meaningful Campaign;
- current scientific status;
- known deep-dive defects/feedback;
- unresolved historical experiments;
- reruns warranted;
- open bugs;
- blocked dependencies;
- recommended first Phase 2-B Campaign;
- machine/runtime requirements;
- GPU requirement if any;
- preferred model/capability;
- whether it must remain a named seat;
- whether execution can later be delegated to PrometheusWorkers.

Use the current census and Phase 3 forensic material rather than memory alone.

Do not assign machines yet unless the operator has already specified them.

---

# 10. Phase 2-B seat selection

Do not interpret "restart Phase 2-B" as "restart every historical seat."

Classify each historical scientific seat:

- `P2B_RESTART`
- `P2B_SUPPORT_ON_DEMAND`
- `PARKED`
- `NEEDS_OPERATOR_RULING`

All engines/seats that were not scientifically parked and still have justified backlog should normally become `P2B_RESTART`.

Include Aether, Aphrodite, and the other surviving engine seats found by the census/forensic record.

Do not hard-code the list if repository state supplies a better answer.

---

# 11. Do not reseat them all on M1

M1 is being cleaned specifically so historical placement is no longer destiny.

After drain, produce a proposed placement matrix for the operator.

Distribute Phase 2-B seats across available machines based on:

- model availability;
- CPU/GPU requirement;
- engine locality constraints;
- local data that cannot economically move;
- collision with Phase 3;
- machine load;
- reliability.

No seat owns a machine merely because it historically lived there.

M1 should become one member of the fleet, not the default home for old science.

---

# 12. Keep Phase 3 isolated

The RSO builder seats remain:

- Palamedes
- Argus
- Cadmus
- Eupalamus
- Pallas

They continue EP-PHASE3 work.

Do not give them M1 cleanup work.

Do not give them Phase 2-B work.

Do not preempt them for branch archaeology.

Their only interaction with this operation is normal resource priority if they need shared compute.

---

# 13. Prepare for the new contracts

When a Phase 2-B named seat is later restarted, it should start as a **fresh session from current `origin/main`**, not resume an old session carrying pre-Phase-2B assumptions.

The old seat's durable science/history remains in Git.

The new session should bootstrap:

- current base role;
- current A2A/distributed-work amendments;
- Epic hierarchy;
- Phase 2-B contract/CWO;
- its native charter;
- its Phase 2-B re-entry Campaign.

That fresh-session boundary is intentional.

---

# 14. Preserve the distinction between named seats and generic workers

Do not use named seats to consume generic execution tasks during cleanup.

When PrometheusWorker infrastructure becomes available, generic execution can migrate there.

M1 drain work itself belongs to the seat that owns the branch/state, plus deterministic fleet tooling where safe.

Scientific ownership stays with named seats.

---

# 15. Reporting cadence during drain

Do not send the operator dozens of seat-level messages.

Maintain one evolving M1 drain report.

Surface only:

- ambiguous branch disposition requiring operator judgment;
- unpushable/unrecoverable state;
- experiment that cannot safely stop;
- material merge conflict;
- unexpected process/resource risk;
- proposed Phase 2-B seat placement once ready.

Everything else should close mechanically.

---

# 16. End state for Machine 1

M1 is considered drained when:

- all historical named sessions are stopped or explicitly exempted;
- no meaningful dirty worktrees remain;
- every branch has MERGE / ARCHIVE / DISCARD disposition;
- mergeable work is on main;
- archival work has durable refs;
- resolved branches/worktrees are removed;
- repository state is synchronized appropriately to current origin/main;
- stale leases/processes are gone;
- the Phase 2-B re-entry manifest exists.

At that point report:

**M1 QUIESCENT / READY FOR RESEATING**

Do not automatically repopulate it.

Wait for operator placement decisions.

---

# 17. Deliverables to the operator

When enough of the drain is complete, give James a compact table containing:

| Seat | Drain | Git disposition | Phase 2-B status | Suggested machine | First re-entry work |
|---|---|---|---|---|---|

Also report:

- unresolved M1 branches;
- archived branch refs;
- merges made;
- processes still running;
- total seats drained;
- Phase 2-B seats recommended for restart;
- available machines/capabilities.

That table should be sufficient for James to spend the next few hours launching fresh Phase 2-B sessions across the fleet.

Proceed.
