# Setup receipt -- Epic layer, EP-GLOBAL / EP-PHASE2B / EP-PHASE3 (Achilles, 2026-10-03)

Directive: roles/Achilles/prompts/2026-10-03_epics_phase2b/ (verbatim, MANIFEST). Built from a960a0e81 on
achilles/epics-p2b-2026-10-03 (worktree Prometheus-worktrees/achilles-p2b, ELSA, claude-opus-5-5); one commit,
fast-forwarded to main (the commit carrying this file). Achilles joins neither epic and coordinates neither.

## Delivered (directive s26)
1. Epic primitive: workgraph epics with status ACTIVE/PAUSED/CLOSED, `permanent` + `end_date` (null/NONE),
   scope, exclusions, peers, entry; campaigns carry thread_id + epic_id (checked equal to the thread's);
   tasks resolve their epic through the campaign and may carry it (checked); `priority_class` 1-6.
2-4. ops/epics/EP-GLOBAL (permanent, no end date), EP-PHASE2B, EP-PHASE3 (updated as a peer) -- peers, not
   a tree.
5. ops/threads/TH-GLOBAL-EVIDENCE-REFINERY.md (permanent; Aporia -> Techne -> Nyx -> Harmonia -> Atlas as
   composition of existing charters, each quoted/pointed to, none rewritten).
6. ops/threads/TH-P2B-ENGINE-HARDENING.md (mission, posture, "Entering Phase 2-B", candidate seats, sources).
7. TH-RSO-BUILD kept as the id (no renaming for aesthetics; annotated "also called TH-P3-RSO-BUILD");
   C-004 gains epic_id EP-PHASE3; its metadata key `epic` (label) renamed `label`; no packet touched.
8-9. Seat epic scope: roles/<Seat>/SCOPE.json, enforced by `workgraph ready` and `transition CLAIMED`;
   Palamedes, Pallas, Argus, Cadmus, Eupalamus -> allowed_epics ["EP-PHASE3"]. Seats without SCOPE.json
   (Nestor and every Phase 2-B seat) are unrestricted by epic.
10. ops/templates/P2B-ENGINE-REENTRY/ + `python -m workgraph new-campaign`: next free C-id, owner as
    coordinator, tasks A (ingestion) and B (triage) PROPOSED for the owner to tailor; C-F only from triage.
11. Forensic pointers in the P2B thread: docs/phase3/intake/{sisyphus,tantalus,tityos,ixion}/ (per-seat
    seats/<Seat>.md), ASTRA-6.0 FAILURE_TO_GATE_MAP and crawler audits, PHASE3_CHALLENGES, critical_memories.
12. DISTRIBUTED_WORK.md s10: epic scope; work-conserving shared machines via existing leases with ceilings,
    no preemption of higher-priority active leases, natural expiry; priority classes 1-6.
13. DISTRIBUTED_WORK.md s11: cross-epic findings (committed note under ops/epics/<TO>/findings/ + comms post
    `XEPIC <FROM> -> <TO>`); not a task, not a reassignment.
14. Tests: 12 new workgraph tests (epic schema, permanent epic, thread->epic, campaign->thread and epic match,
    task epic resolution, restricted seat refused (ready and claim), unrestricted Phase 2-B seat claims,
    restricted seat inside scope, campaign closure leaves thread/epic, template instantiation valid,
    repository epics/threads/scopes, C-004 still valid under EP-PHASE3); 1 test amended (campaign epic_id now
    allowed and checked). workgraph + shared-role + base-role + census tests: 82 passed.
    `python -m workgraph validate`: 3 epics, 1 campaign, 1 task, OK.
15. This receipt. Reporting data (s23): `python -m workgraph report --json` gives epic, thread, campaign, task,
    state, class/model, holder, host per active task (leases now record host and epic); the census can read it
    later -- no dashboard built.

## Completion criterion (s27), checked statically
- "You are Nestor ... enter Phase 2-B": README -> ops/epics/EP-PHASE2B/README.md -> TH-P2B-ENGINE-HARDENING
  "Entering Phase 2-B" -> docs/phase3/intake/sisyphus/seats/Nestor.md -> `new-campaign P2B-ENGINE-REENTRY`.
- "You are Palamedes": `workgraph ready Palamedes` shows only EP-PHASE3 work; a Phase 2-B claim is refused
  ("epic scope").

## Not done / for the operator
- EP-PHASE2B and EP-PHASE3 exit conditions not set (recorded as such). No engine campaign launched; no seat woken.
- Nothing was broadcast on comms; seats learn of Phase 2-B when woken with "enter Phase 2-B".
- The census does not yet display epic context (data only, as asked).
