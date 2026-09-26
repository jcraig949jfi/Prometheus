# Operator rulings (verbatim, received 2026-09-26 ~14:10Z by Bellerophon[m2-e9845b74] in direct chat)

Three pending decisions are resolved as follows.

1. Cosmos #550 — APPROVED WITH THE EXISTING HOLDOUT REQUIREMENT

Proceed with C3 only after the independent foreign holdout D is produced and sealed by Nestor under the existing reassignment.

D remains mandatory.

Do not weaken the holdout firewall, reuse A/B/C construction material, let Cosmos construct its own D, or substitute an already-seen substrate.

Once Nestor delivers the sealed D artifact and provenance, Cosmos may resume C3 immediately under its frozen protocol. No additional operator approval is required at that point.

2. Bellerophon scoped multi-day campaign — HOLD FOR COUPLING CLOSEOUT

Do not launch NEXT_MULTIDAY_CAMPAIGN.md yet.

The next multi-day campaign is authorized only after the currently frozen coupling campaign has completed execution and analysis and has issued a final readiness classification of either:

* READY_FOR_MULTIDAY, or
* READY_WITH_RESTRICTED_SCOPE.

A campaign design by itself is not the launch gate.

If the coupling result is REPHYSICS_REQUIRED or INSTRUMENT_REPAIR_REQUIRED, do not launch the multi-day campaign; follow the resulting repair/rephysics recommendation instead.

Once the coupling closeout produces one of the two READY classifications, the scoped multi-day campaign may proceed autonomously within the scope supported by that classification without returning for another operator decision.

3. Branch disposition

Merge:

bellerophon/post-campaign-forensics-2026-09-23

The forensic/grounding work is complete and should become durable mainline evidence and infrastructure.

Do not merge the active coupling-campaign branch merely to clean up Git state.

Keep it isolated until the coupling campaign has:

* completed all permitted execution;
* completed preregistered analysis and causal follow-ups;
* written its final report and ledgers;
* issued its readiness classification;
* passed its tests/replay checks;
* committed and pushed the final closeout.

At that point, if the branch is clean and the closeout verifies evidence integrity, merge it to main as part of campaign closure.

These rulings are final for the current sequence; no further HITL is required for the already-defined transitions above.

---

## Execution record (Bellerophon, 2026-09-26)

- Ruling 1: comms #550 closed on Bellerophon's side (ack #737 to Cosmos). Cosmos's INFO_LEDGER already records D as
  reassigned to Nestor (M1) on 2026-09-24 and the Bellerophon request as withdrawn before it was read. Bellerophon
  builds nothing for C3.
- Ruling 3: the coupling closeout met every listed condition before the merge: execution complete (11,657/11,657,
  0 NOT_RUN); preregistered analysis + AUTO follow-ups done; report + ledgers written (6a0b9813e, packet 98a28dd39);
  classification READY_FOR_MULTIDAY; replay 341/341 identical; z80atlas tests 60/60 on the branch AND on the merged
  tree; branch clean and pushed. Merged to main: forensics branch (14a1ea268), then the coupling branch (cc63d7e8a);
  pushed as 874ea23a7 (after merging one concurrent Ensorain commit, no conflicts).
- Ruling 2: the launch condition is MET (READY_FOR_MULTIDAY issued 2026-09-25 by the frozen rule). The scoped
  multi-day campaign proceeds autonomously within the scope set in
  roles/Bellerophon/coupling_2026-09-24/NEXT_MULTIDAY_CAMPAIGN.md (acquisition + protection + long repair; no
  maintenance re-measurement). The design's own prerequisites come before any launch: instrument repairs F6-F11,
  resumable mid-run snapshots, a frozen prereg, an off-plan pilot, a dedicated-host declaration.
