# MWO-0002 candidate -- author note

Author: Aporia[m1-cb5a6069], on operator assignment (verbatim at
roles/Aporia/prompts/2026-09-29_mwo0002_authoring/). Authoring only. Aporia is not restored as a steward and
this note carries no authority. Candidate: roles/Aporia/proposals/MWO-0002_CANDIDATE.md.

## 1. Git state reviewed

- origin/main 5ea4f2dbf07babf8f74be482e2a7c1a5db3b92d8 (2026-09-29T02:10-04:00), fetched at the start of drafting.
  Worktree F:/Prometheus-worktrees/aporia-2026-09-29, branch aporia/mwo-0002-candidate-2026-09-29, cut from it.
- MWO-0001: CURRENT.md is byte-identical to archive/MWO-0001_2026-09-28.md; committed-blob sha256
  007054adfdb1e6d7...f3 matches PUBLICATIONS.md (publication 7e4c09f2c, broadcast comms #914 to *).
- Read in full: ops/work_orders/{CURRENT,PUBLICATIONS}.md, the MWO-0001 archive, fabric/{README,PROTOCOL,FREEZE}.md,
  ops/README.md, ops/tools/thread_check.py, ops/threads/TH-015.md (sample).
- WORK_STATE: every roles/*/WORK_STATE.json on all 21 origin branches updated since 2026-09-28. Twelve seats
  have one naming MWO-0001 (Aether, Ananke, Aphrodite, Archaeon, Artemis, Bellerophon, Cosmos, Cyclops, Ensorain,
  Harmonia, Nestor, Odysseus). Aphrodite's is only on aphrodite/arc3-2026-09-28 (b57f49ba84), and Archaeon's
  only on archaeon/mwo0001-2026-09-28 (b500d307b3). Every one records mwo_commit 7e4c09f2c.
- Adoption records: roles/Artemis/journal/2026-09-29.md and roles/Harmonia/journal/2026-09-29_m2-475d761f.md.
- ops/tools/thread_check.py on main: threads=17, migrated=17, failures=0.
- Not reviewed: Fabric store contents (tasks/attempts/leases) directly; seat branches older than 2026-09-28; comms
  beyond #914.

## 2. Principal design choices

1. The census is a FILE, not a message. Each seat pushes one small JSON (MIGRATION_REPORT_MWO-0002.json) plus a
   WORK_STATE update to its OWN branch. Central coordination finds reports by scanning origin branches, the
   same way this note found the WORK_STATEs. No comms report, no ACK, no merge to main.
2. The roster is a RULE derived from Git (a WORK_STATE naming MWO-0001 after its publication, or live during the
   cycle), not a list. No dormant seat is woken; a seat that stays dormant is NOT_LIVE, not a failure.
3. Seats report CLAIMS WITH POINTERS. A YES with no evidence pointer reads as UNVERIFIED. Classification
   (MIGRATED / MIGRATED_AT_GATE / PARTIAL / NOT_MIGRATED / NOT_LIVE) is done by central coordination, never by
   the seat about itself, and not by any new seat.
4. The measured quantity is explicit: how_mwo_0001_was_found / how_mwo_0002_was_found. At least one MWO-0001
   adoption (Harmonia) began with a per-seat operator boot prompt, so "needed a bespoke prompt" is the thing the
   census counts. It is not framed as a fault.
5. Gates vs routine (C9) is operationalised: a stop counts as a hard gate only if it cites an MWO-0001 s7 clause or
   a frozen contract path. Waiting on a sign-off that no frozen contract requires is routine coordination.
6. Custody is generalized in the smallest way that satisfies the portability ruling. Publication is a
   step-by-step REGISTRAR FUNCTION of whichever seat the approval designates, and it ends at step 7. No seat is
   named in the protocol. The one publisher slot is "[DESIGNATED AT APPROVAL]".
7. Carry-forward by reference. MWO-0001 s10 assignments continue "as far as they remain open per the seat's own
   pushed WORK_STATE". This avoids rewriting eleven seat sections from a snapshot that would be stale on
   publication. The easy-to-lose restrictions (LM01 not launched, D2 custody, no third Nestor run, no RunPod, no
   promexec, blind lanes) are restated explicitly.

## 3. Ambiguities and policy conflicts found

- CUSTODY: MWO-0001 s2 says "Only Cyclops writes the canonical ops/work_orders/ files unless a later MWO explicitly
  changes custody". Publishing MWO-0002 by any seat other than Cyclops is only valid if the operator's approval of
  MWO-0002 is itself that explicit change. The candidate states this.
- ops/README.md (2026-09-27, Harmonia) still says the Thread/Campaign model is a pilot, and tells agents not to
  create ops/campaigns/ or adopt it on their own initiative. MWO-0001 later mandated the model fleet-wide. The
  candidate says the MWO governs, but does not edit Harmonia's file.
- MWO-0001 s7 says an approved MWO satisfies a prior "operator direct chat" requirement. Ensorain's FROZEN LM01
  launch gate rejects an MWO archive file as a carrier (DEF-ENS-001). The general rule and the frozen
  implementation disagree. It fails closed, so it is safe, but a launch MWO needs a carrier decision first.
- Fabric vs custody: workers check out base_sha from origin, so a Fabric Task cannot read custody-withheld files
  without publishing them (Cosmos). "Use Fabric where appropriate" therefore has a principled exception that
  MWO-0001 does not state.
- Fabric vs host-local evidence: no Windows workers, so SKULLPORT-local work cannot be a Fabric Task (Archaeon
  tsk-c4317a3656d0 unclaimable). The census criterion C6 treats this as a blocker, not a seat failure.
- Identifier drift: WORK_STATEs cite ids not in the registry, for example thr-bel-*, thr-ens-*, thr-s3,
  C-BEL-*, C-ENS-ARC3, C-ANANKE-*, and TH-018..020 / C-003 only on Aphrodite's branch. MWO-0001 s4 names canonical
  forms but no registration step. The candidate MEASURES this (identifier_check) and does not mandate repair.
- WORK_STATE schema drift: seats added mwo_sha256, state_reason, leases, incidents, comms_cursor, head_sha_note, and
  others. Threads appear as strings in some files and objects in others. The candidate clarifies core vs extra
  fields and does not create a v2.
- Hash-verification pitfall: a CRLF working-tree copy of CURRENT.md hashes differently (Harmonia). The candidate
  fixes the method: hash the committed blob.

## 4. Intentional changes from MWO-0001

Only three (candidate s1):
1. MWO custody and publication generalized (replaces the "Cyclops publication" step in s1 and the custody
   sentence in s2).
2. The census report duty, for one cycle.
3. The WORK_STATE v1 clarification (core vs permitted fields; no new schema).
Everything else is carried forward by reference, including every scientific assignment, gate, freeze and
restriction. Not changed on purpose: seat assignments, gates, the Fabric freeze, the A2A and host policies,
promexec status, and the Atlas and parked-seat treatment.

## 5. Needs operator decision BEFORE publication

1. PUBLISHER for MWO-0002. If it is Cyclops, MWO-0001 custody is satisfied as written. If it is another seat,
   state in the approval that it is the custody change.
2. Whether the census applies only to the Git-derived roster (as drafted), or also requires a report from any
   specific seat by name.
3. Whether to accept "carry forward by reference" for s10 assignments, or to have central coordination refresh
   the per-seat sections before publication. The snapshot here is a few hours old and several WORK_STATEs change
   daily.
4. ops/README.md banner: leave it (the MWO governs, as drafted), or direct its owner to update it.
5. The SI freeze requests #603 and #608, held in Harmonia's queue: renew or cancel. They were sent by the two
   stewards before the 2026-09-26 steward freeze. The author has a conflict of interest here (it co-issued them)
   and makes no recommendation.
6. No other decision is needed to publish. Section 8 of the candidate lists pending science and custody decisions
   only as a record; none of them blocks the census.
