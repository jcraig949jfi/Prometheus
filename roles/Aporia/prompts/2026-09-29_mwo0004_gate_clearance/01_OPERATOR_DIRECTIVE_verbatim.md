Aporia: you are the author and designated publisher of **MWO-0004** for this publication only.

Authoring/publishing confers no steward, coordinator, scheduling, portfolio-management, or scientific-adjudication authority.

Draft MWO-0004 from the rulings below, run the normal publication checks, and publish it without returning for another approval unless you discover a genuinely new custody, blindness, or safety conflict.

Do not return merely because a scientific choice is imperfect, evidence is incomplete, or a previous process expected an operator decision. The purpose of this order is to remove those routine stalls.

Before drafting:

- verify the current MWO/publication state from `origin/main`;
- if the previously approved MWO-0003 publication is incomplete, finish that already-authorized publication first;
- inspect current WORK_STATE files so obviously obsolete pending items are not carried forward as gates.

Publication checks:

- ASCII-safe control text where practical;
- strict valid JSON where JSON is shown;
- no blind-lane scientific terms in fleet-global text;
- prefer neutral IDs over hypothesis names;
- no branch protection or branch-locking changes;
- no paid compute;
- no privileged host changes;
- no invented operator confirmations.

Publish through the established two-commit protocol:

**P:** `CURRENT.md` + immutable archive only, push and verify identical committed blobs/hash.

Then broadcast the normal fleet pointer.

**R:** `PUBLICATIONS.md` row + Aporia WORK_STATE/publication receipt, push and verify.

MWO-0001 through MWO-0003 remain in force except where MWO-0004 explicitly changes them.

# PURPOSE

Clear routine pending decisions and eliminate open-ended waiting.

Prometheus should prefer **small, bounded, reversible execution now** over waiting for an unscheduled review.

We are testing concepts. Scientific cleanup, consolidation, and retrospective review can happen later.

No seat should stop useful unrelated work because one item is blocked.

# PART 1 — STANDING AUTONOMY RULES

## R1 — IMMEDIATE DEFAULT FOR NON-HARD DECISIONS

A pending item that is **not** an MWO-0001 §7 hard gate does not wait for operator review.

On the next normal loop, the seat executes:

1. an explicit default stated in the governing MWO/contract; otherwise
2. the smallest reversible action that:
   - stays inside current scientific meaning;
   - stays inside the standing resource envelope;
   - does not reveal sealed/blind material;
   - does not create external side effects;
   - does not require privilege;
   - does not expand a campaign materially.

There is **no 24-hour or 48-hour waiting period**.

If no safe reversible default exists, HOLD that item and continue other eligible work. Do not turn it into a fleet-wide coordination stop.

`operator_decisions_required` should contain actual hard gates only.

Routine choices, reviewer availability, preferred host, optional follow-up work, ordinary repairs, identifier cleanup, and implementation details are not operator gates.

## R2 — STANDING LOCAL COMPUTE ENVELOPE

No separate authorization is required for work satisfying all of:

- local/unpaid compute only;
- canonical Fabric lease for substantial resource use;
- <= 16 CPU core-hours per item;
- <= 48 CPU core-hours per seat per rolling 24 hours;
- <= 4 GPU-hours per seat per rolling 24 hours on already-available local GPU resources;
- no new packages requiring machine-wide or privileged installation;
- no changed scientific meaning or preregistration.

Inside this envelope, a statement such as "needs N core-hours" is not an operator gate.

Seats may voluntarily use less.

## R3 — NATIVE FALLBACK

If an otherwise-authorized task cannot run on Fabric because no currently eligible worker can host it — including host-affine Windows/SKULLPORT work, unavailable runtime capability, or custody-local evidence — run it natively on the required host.

Requirements:

- use the canonical Fabric lease when the resource claim is substantial;
- record why Fabric could not host the work;
- preserve the same scientific/evidence contract;
- do not install new privileged/system dependencies merely to make Fabric usable.

Absence of an eligible Fabric worker is not a gate.

## R4 — COLD-BOOT REPAIR

The MWO-0002 census and MWO-0003 cold-start probe identified a common bootstrap defect: fresh seats may not discover the current MWO from the base-role entry path.

After the relevant FP-001 cold-start result is durably in Git, Aporia is authorized to make exactly one shared bootstrap repair:

Add to the first boot step in:

`roles/base-role/RESPONSIBILITIES.md`

the instruction:

`Before anything else: read origin/main:ops/work_orders/CURRENT.md, then roles/<Seat>/WORK_STATE.json.`

No other base-role policy change is authorized by this item.

Make this as a separate ordinary implementation commit after publication R, then record the commit in Aporia WORK_STATE and return to HOLD.

Do not wait for another MWO to make this one-line repair.

## R5 — NO DEFERRAL TO NOWHERE

The following is not a valid blocker:

`wait for future MWO review`

or equivalent wording.

A blocked item must instead have one of:

- an executable default under R1;
- a named hard gate;
- a concrete dependency that can actually become true;
- an explicit HOLD decision.

Seats continue other eligible work while any one item is blocked.

# PART 2 — D2: END THE REPAIR/AUDIT HAMSTER WHEEL

MWO-0003's D2 pause is modified as follows.

## D2-1 — RESOLVE #925 WITHOUT OPERATOR SESSION WORK

MWO-0004 itself resolves D2 issue #925.

No additional direct operator statement in Nestor, comms, or another seat is required.

No branch protection is required.

No branch lockdown is authorized.

The D2 protocol-record root of trust is:

**published Git object identity + immutable blob hashes + an append-only out-of-repository anchor on M1.**

For each protocol record participating in D2, confirmation records:

- repository path;
- blob SHA-256;
- commit SHA.

Before each D2 gated step, verify:

1. the recorded commit still exists;
2. it is an ancestor of the currently fetched `origin/main`;
3. the record at that commit still has the confirmed blob hash;
4. those values agree with an append-only M1 anchor created when first confirmed.

A mismatch fails closed.

The anchor must not contain sealed scientific content; only identifiers/hashes necessary for integrity checking.

This is the accepted residual model for D2. The residual risk of repository history mutation is accepted only insofar as this mechanism detects it and stops execution.

Do not add GitHub branch rules or force-push lockdowns.

## D2-2 — ONE BOUNDED COMPLETION ATTEMPT

The MWO-0003 D2 pause lifts only for:

1. implementing D2-1;
2. one repair pass if needed to conform existing records;
3. one independent re-audit.

If that audit passes, continue under the existing D2 protocol.

If it fails on an ordinary implementation defect, allow **one final bounded repair and one final re-audit**.

After that:

- PASS → proceed under existing custody/reveal rules.
- FAIL → record the remaining defect and HOLD D2.
- Do not begin audit round 10, 11, 12, etc.
- Do not request an operator decision unless the remaining issue is genuinely a new hard gate.
- Continue other fleet work.

All existing D2 custody, blindness, and evidence rules remain unchanged.

Nothing sealed is released merely because #925 is resolved.

D2 work remains separate from FP-001.

# PART 3 — CURRENT SEAT ITEMS

These are decisions, not questions.

## G1 — ARTEMIS / ODYSSEUS S3 PRINCIPAL

Use the existing Artemis instance on **ubu002** as the S3 principal.

The previously desired same-host/separate-session placement on ubu001 is dropped for this run.

Record that separation test as **NOT RUN**, not as passed.

Proceed with the bounded S3 work without starting another operator-managed session.

## G2 — ARCHAEON / NESTOR 1% SAMPLE

Run the frozen sample verifier natively on SKULLPORT under R3.

If all available run-1 copies fail the frozen verification:

- declare the 1% sample **LOST / NOT VERIFIED**;
- do not regenerate it;
- do not run a third ancestry production run;
- preserve the failure as evidence and move on.

No operator decision is required.

## G3 — ENSORAIN LM01

LM01 at frozen commit:

`ee8cbe0c8cb1ef131e6bc8181c8272656eaa5a6e`

remains **HOLD / NOT LAUNCHED** under MWO-0004.

This is a decision, not a pending operator gate.

Do not keep an `operator_decisions_required` entry merely asking whether LM01 should launch.

The frozen campaign may be explicitly launched by a later order when we actually want that larger experiment.

DEF-ENS-001 therefore does not block current Ensorain work; it only matters at a future launch.

Continue other bounded eligible Ensorain work.

## G4 — AETHER

Continue the narrow existing `rcv_add` / `rcv_str` line within R2.

No RunPod or other paid compute.

Do not enable promexec.

`promexec` remains EXPERIMENTAL / NOT ENABLED.

Do not wait for a general "physics-search continuation" ruling; the narrow bounded continuation above is the ruling.

## G5 — APHRODITE ARC3

Accept the existing ARC3 close as reported.

Authorize TH-019 stage T51 within R2.

Keep TH-020 parked under its existing seat default.

No additional ARC3 close review is required before T51.

## G6 — ARCHAEON NEW BEE / NPE DESIGNS

No new large BEE/NPE design campaign is requested by MWO-0004.

This is not a blocker.

Continue existing authorized bounded Archaeon work and fleet micro-probes.

## G7 — COSMOS WITHHELD COORDINATE-LAYER FILES

Do not publish the withheld files merely to make Fabric able to consume them.

Keep them withheld.

Use native/custody-local execution where otherwise authorized under R3.

Revisit portability after D2 completes.

This is a decision, not an operator wait.

## G8 — HARMONIA ADDENDUM E

The current Addendum E position stands.

No additional review is required merely because it was previously listed as pending.

## G9 — LEASE CUTOVER

Canonical Fabric lease authority applies immediately to new substantial work.

Do not require Nestor or Archaeon to merge all of `origin/main`, rebase branches, or perform branch-management work merely to satisfy this item.

If a local branch lacks the canonical lease implementation needed for new work, incorporate the minimum relevant lease-cutover change at the next safe point.

Legacy lease detection may remain temporarily for compatibility but must not be used as authority for a new claim.

Branch housekeeping is not a gate.

# PART 4 — HARD GATES

This order intentionally resolves many items that were previously waiting for operator attention.

It does **not** abolish genuine hard gates.

Still hard:

- sealed/blind-data release;
- crossing a frozen launch gate unless this MWO explicitly launches it;
- paid/external spend beyond an explicit envelope;
- privileged host/system changes;
- changing frozen experiment meaning, endpoints, thresholds, or preregistration after exposure;
- genuinely new custody/safety conflicts.

When one occurs:

- HOLD that item;
- record the gate precisely;
- continue all unrelated eligible work;
- do not generate repeated repair/review cycles around the unresolved gate.

# PART 5 — AFTER PUBLICATION

Aporia:

1. publish MWO-0004 by P/R;
2. perform the single R4 boot-line implementation when its prerequisite FP-001 result is present;
3. record the implementation commit in WORK_STATE;
4. return to HOLD/advisory.

Do not start:

- another migration census;
- another general review;
- another cleanup campaign;
- a steward loop;
- a branch-lockdown project.

Seats discover and execute MWO-0004 through their normal loop.

No ACKs required.

No bespoke prompts should be necessary merely to activate these decisions.

The desired fleet behavior is:

**make a bounded decision, execute, record evidence, and keep moving.**

Only true hard gates should stop the affected item.

END DIRECTIVE
