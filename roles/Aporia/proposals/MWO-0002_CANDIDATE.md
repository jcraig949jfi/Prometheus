CANDIDATE -- NOT AUTHORITATIVE. This file is a proposal for operator review. It is not the current Master Work
Order. No seat may act on it until an approved text is published at ops/work_orders/CURRENT.md.

PROMETHEUS MASTER WORK ORDER -- MWO-0002

Date: [set at approval] America/New_York
Purpose: One-cycle MIGRATION CENSUS. Measure, from Git, whether each live seat now runs on the single-MWO
operating model established by MWO-0001: Git current MWO -> seat work loop -> Git durable state, with comms as
notification and Fabric/A2A as the execution plane. This is not a new science campaign.

Review snapshot: jcraig949jfi/Prometheus main 5ea4f2dbf07babf8f74be482e2a7c1a5db3b92d8, plus live branch state
that holds seat work state not yet on main, including:

* aphrodite/arc3-2026-09-28 at b57f49ba84
* archaeon/mwo0001-2026-09-28 at b500d307b3

Authored as a candidate by an assigned seat. This order becomes authoritative only after operator approval and
publication by the designated publishing seat (section 2).

----------------------------------------------------------------------------------------------------------------

0. RELATION TO MWO-0001

MWO-0001 (archive ops/work_orders/archive/MWO-0001_2026-09-28.md, sha256
007054adfdb1e6d78157f73c017e653983de9f93f21d835361e74d3f139b88f3, published at 7e4c09f2c) is carried forward in
full, EXCEPT where a section below states a change. In particular these remain in force unchanged:

* section 3, the three planes (GitHub authoritative; Fabric live execution; comms notification);
* section 4, the common work model: Thread -> Campaign -> Experiment -> Task -> Attempt;
* section 5, the A2A policy;
* section 6, the host/package/port policy; promexec remains EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC
  WORKERS;
* section 7, the hard operator gates;
* section 8, the standard seat loop;
* section 9, the WORK_STATE schema v1 (clarified in section 5 below; not replaced);
* section 10, every seat's scientific assignment, blindness rule, custody boundary and restriction, as far as
  it remains open (section 6 below);
* sections 11 and 12, the autonomy and incident rules;
* the Fabric v0.2 freeze (fabric/FREEZE.md, tag fabric-v0.2, commit 54e42c695).

Where this order is silent, MWO-0001 governs.

----------------------------------------------------------------------------------------------------------------

1. WHAT THIS ORDER CHANGES

Exactly three things change. Nothing else in MWO-0001 is amended.

1. Master Work Order custody is generalized: authoring, approval and publication are separated, and publication
   is a function of a designated seat, not of a named seat (section 2).
2. Each live seat files one small machine-readable migration report for this cycle (section 3).
3. The WORK_STATE v1 schema is clarified: required core fields vs permitted extra fields (section 5).

----------------------------------------------------------------------------------------------------------------

2. MASTER WORK ORDER LIFECYCLE: AUTHORING, APPROVAL, PUBLICATION

This section replaces MWO-0001 section 1's publication step ("Cyclops publication") and section 2's custody
sentence ("Only Cyclops writes the canonical ops/work_orders/ files unless a later MWO explicitly changes
custody"). It does not change any other part of those sections.

AUTHORING

* Any capable seat may draft a candidate MWO when assigned to do so by the operator.
* A candidate lives under roles/<AuthorSeat>/proposals/ and begins with the line
  "CANDIDATE -- NOT AUTHORITATIVE".
* Authoring confers no authority. Writing a candidate does not make it current, does not assign work, and does
  not make the author a coordinator or steward.
* Seats must not act on any file under roles/*/proposals/ as if it were a work order.

APPROVAL

* The operator, with central ChatGPT coordination, accepts, revises or rejects a candidate.
* Only the approved text is authoritative. The approved text may differ from the candidate. When it does, the
  approved text governs and the candidate is kept only as history.
* The approval names the publishing seat for that MWO.

PUBLICATION

The designated publishing seat performs the REGISTRAR FUNCTION for that one publication only. The registrar
function is not a standing role. It confers no authority beyond these steps, and it ends when step 7 is done.

1. Commit the approved text verbatim to ops/work_orders/CURRENT.md and to
   ops/work_orders/archive/<MWO-ID>_<date>.md, byte-identical, LF line endings.
2. Compute the sha256 of the COMMITTED BLOB (git show origin/main:<path> | sha256sum), never of a working-tree
   file. A CRLF checkout hashes differently.
3. Append one row to ops/work_orders/PUBLICATIONS.md: MWO ID, archive path, sha256, publication commit, UTC time,
   broadcast id, and the publishing seat.
4. Push to origin/main.
5. Verify from origin/main that CURRENT.md and the archive copy hash identically to the recorded sha256.
6. Send one comms message to all seats: MWO ID, commit SHA, archive path, sha256, and the line
   "fetch origin/main:ops/work_orders/CURRENT.md and adopt".
7. Record the publication in the publishing seat's WORK_STATE, then return to that seat's own work or HOLD.

The registrar must not rewrite, summarize, expand, reinterpret or reprioritize the approved text, and must not
require ACK messages. Only the designated publishing seat writes ops/work_orders/ for that publication.
PUBLICATIONS.md remains append-only; its header line naming a maintainer is read as "maintained by the
publishing seat of each row".

PUBLISHER FOR MWO-0002: [DESIGNATED AT APPROVAL]. If the operator designates Cyclops, this publication also
satisfies MWO-0001's custody sentence as written. If the operator designates another seat, the operator's
approval of this text is the explicit custody change that MWO-0001 section 2 requires.

----------------------------------------------------------------------------------------------------------------

3. THE MIGRATION CENSUS

THE QUESTION

For each live seat: if the unique bootstrap prompt that pointed this seat to MWO-0001 were never sent again,
could the seat now continue routine Prometheus work by fetching the current MWO, checking comms and Fabric, and
reading Git state?

A true hard gate (MWO-0001 section 7, or a frozen scientific or custody contract) is NOT a migration failure. A
seat that is correctly stopped at a real gate, and knows which gate, has migrated.

WHO REPORTS (the census roster)

The roster is derived from Git, not from a list in this order:

* every seat that has a roles/<Seat>/WORK_STATE.json naming MWO-0001 on any branch pushed to origin after the
  MWO-0001 publication commit (7e4c09f2c); and
* any other seat that becomes live, for its own reasons, while MWO-0002 is current.

At the review snapshot, the first rule gives: Aether, Ananke, Aphrodite, Archaeon, Artemis, Bellerophon, Cosmos,
Cyclops, Ensorain, Harmonia, Nestor, Odysseus. That list is informative; the rule governs.

No dormant or parked seat is woken to file a census report. A seat that stays dormant for the whole cycle is
recorded by central coordination as NOT_LIVE, which is not a migration failure.

WHAT EACH ROSTER SEAT DOES (once, inside its normal loop)

1. Adopt MWO-0002 per MWO-0001 section 8: fetch, verify the committed blob's sha256 against PUBLICATIONS.md, and
   read this order.
2. Write roles/<Seat>/MIGRATION_REPORT_MWO-0002.json (schema in section 4).
3. Update roles/<Seat>/WORK_STATE.json: set mwo_id to MWO-0002 and mwo_commit to the MWO-0002 publication commit,
   and add "migration_report": "roles/<Seat>/MIGRATION_REPORT_MWO-0002.json".
4. Commit both files and push them to the seat's own working branch. A merge to main is NOT required to report.
5. Continue its carried-forward work (section 6).

That is all. No comms report is required. A seat may send at most one short comms line pointing to the pushed
commit; it is not necessary, because central coordination finds reports by scanning Git.

HOW CENTRAL COORDINATION FINDS AND READS THE REPORTS

* Discovery: every roles/*/MIGRATION_REPORT_MWO-0002.json on every origin branch pushed after the MWO-0002
  publication commit, newest per seat.
* A report is a set of CLAIMS by the seat about itself. Every YES must carry at least one verifiable pointer:
  a path at a commit SHA, a Fabric tsk-/att-/lse- id, a comms message id, or a command with its recorded
  output. A YES without a pointer is read as UNVERIFIED.
* Central coordination may cross-check any report against Git, comms and Fabric, and may dispatch a read-only
  Fabric review Task (repo-readonly, independent replicas) for that purpose under MWO-0001 section 5. No seat
  reviews another seat's census report as a standing duty.

CLASSIFICATION (made by central coordination from the reports and Git; no seat classifies itself)

* MIGRATED: the answer to THE QUESTION is YES with evidence; any stop is a named hard gate.
* MIGRATED_AT_GATE: MIGRATED, and currently stopped at a real hard gate. Counted as migrated.
* PARTIAL: the seat operates the loop but depends on some non-MWO mechanism for routine work. That includes
  bespoke per-seat prompts, a legacy lease or queue convention, and steward-era sign-offs.
* NOT_MIGRATED: the seat cannot identify its current authorized work from the MWO and Git alone.
* NOT_LIVE: the seat did not run during the cycle.

A NO or PARTIAL answer is useful data, not a fault. The census measures the operating model, not the seats.

----------------------------------------------------------------------------------------------------------------

4. MIGRATION REPORT SCHEMA (prometheus.migration_report.v1)

Keep it short: one small JSON file, pointers not prose. Each criterion has status YES | PARTIAL | NO |
NOT_APPLICABLE, "evidence" (a list of pointers), and "note" (one or two sentences at most).

{
  "schema": "prometheus.migration_report.v1",
  "seat": "<Seat>",
  "mwo_id": "MWO-0002",
  "mwo_commit": "<MWO-0002 publication commit>",
  "reported_at_utc": "<ISO-8601>",
  "branch": "<branch>",
  "head_sha": "<pushed head>",

  "bootstrap_independence": {
    "answer": "YES|CONDITIONAL|NO",
    "conditions": [],
    "how_mwo_0001_was_found": "comms_broadcast|operator_prompt|own_loop_fetch|other",
    "how_mwo_0002_was_found": "comms_broadcast|operator_prompt|own_loop_fetch|other",
    "evidence": [], "note": ""
  },

  "criteria": {
    "C1_adopted_mwo_0001":            {"status": "", "evidence": [], "note": ""},
    "C2_discovers_next_mwo_unprompted":{"status": "", "evidence": [], "note": ""},
    "C3_work_state_useful":           {"status": "", "evidence": [], "note": ""},
    "C4_identifies_authorized_work":  {"status": "", "evidence": [], "note": ""},
    "C5_checks_comms_correctly":      {"status": "", "evidence": [], "note": ""},
    "C6_uses_fabric_where_appropriate":{"status": "", "evidence": [], "note": ""},
    "C7_uses_common_hierarchy":       {"status": "", "evidence": [], "note": ""},
    "C8_uses_canonical_leases":       {"status": "", "evidence": [], "note": ""},
    "C9_distinguishes_gates_from_routine":{"status": "", "evidence": [], "note": ""}
  },

  "hard_gates_current": [
    {"gate": "<MWO-0001 s7 clause number, or frozen contract path>", "item": "", "evidence": []}
  ],
  "migration_blockers": [
    {"what": "", "kind": "fabric|host|custody|identifier|tooling|policy|other", "evidence": []}
  ],
  "legacy_conventions_still_used": [
    {"convention": "", "why": "", "retire_plan": "none|seat|needs_operator"}
  ],
  "identifier_check": {
    "thread_ids_unresolved": [],
    "campaign_ids_unresolved": [],
    "note": ""
  }
}

Criterion meanings (answer for the seat's own practice during this cycle):

* C1: WORK_STATE names MWO-0001 at its publication commit, and the seat verified the committed blob's hash.
* C2: the seat learned of MWO-0002 by its own loop (fetch, or the one publication broadcast), not by a bespoke
  per-seat prompt. If a per-seat prompt was used, say so. That is the measured quantity.
* C3: WORK_STATE has the v1 core fields filled (section 5) and is current at the pushed head.
* C4: the seat can point to its current authorized work: an MWO section plus a Thread, Campaign or Experiment id,
  or HOLD with the reason.
* C5: the seat checks comms from its recorded cursor at loop points, does not broadcast idle heartbeats, and does
  not treat comms as the durable record or as an approval channel.
* C6: execution that another seat or a replica could do was expressed as a Fabric Task, where Fabric can host it.
  NOT_APPLICABLE when the seat had no portable execution. PARTIAL with a blocker when Fabric could not host it
  (see section 7).
* C7: reports and WORK_STATE keep Attempt -> Task -> Experiment -> Campaign -> Thread distinct, using registry
  identifiers where they exist.
* C8: new substantial resource claims used the canonical Fabric lease row. NOT_APPLICABLE if none were made.
* C9: every current stop in hard_gates_current names a real MWO-0001 section 7 clause or a frozen contract.
  Waiting for another seat's sign-off, a steward's concurrence, or a comms "go" that no frozen contract requires
  is routine coordination, not a gate, and belongs in migration_blockers or legacy_conventions_still_used.

identifier_check: list any thr-/TH- or C- identifier that the seat's WORK_STATE uses but that does not resolve to
a file under ops/threads/ or ops/campaigns/ on origin/main or on the seat's pushed branch. Record the ones that
don't resolve; do not repair them for the census. Thread identity is checked with ops/tools/thread_check.py.

----------------------------------------------------------------------------------------------------------------

5. WORK_STATE v1: CLARIFICATION (not a new schema)

The v1 schema in MWO-0001 section 9 stands. For comparability:

* Required core fields: schema, seat, mwo_id, mwo_commit, updated_at_utc, state, branch, head_sha, threads,
  campaigns, experiments, fabric_tasks, running, blocked_on, next_actions, operator_decisions_required,
  latest_reports.
* Additional fields are permitted (for example mwo_sha256, state_reason, leases, incidents, comms_cursor,
  migration_report). Tools must ignore unknown fields.
* Within threads, campaigns and experiments, prefer objects with "id" (canonical where one exists) and "alias".
  Plain strings remain valid.
* head_sha is the pushed head of "branch". If the seat's work spans several branches, name the one holding the
  newest WORK_STATE and list the others in a permitted extra field.

----------------------------------------------------------------------------------------------------------------

6. CURRENT SEAT INSTRUCTIONS

Every seat's MWO-0001 section 10 assignment continues, as far as it remains open according to the seat's own
pushed WORK_STATE. This order does not re-issue, extend, close or reprioritize any scientific assignment. The only
addition for roster seats is the census (section 3).

Carried forward explicitly, because they are easy to lose in a cutover:

* LM01 (Ensorain) remains FROZEN AND NOT LAUNCHED at ee8cbe0c8cb1ef131e6bc8181c8272656eaa5a6e. This order does
  not contain the launch phrase.
* D2 (Cosmos / Harmonia / Nestor / Odysseus): custody, blindness and the seal -> audit -> commitment ->
  designation -> reveal sequence are unchanged. Nothing here authorizes spending, revealing, designating or
  inspecting D2.
* Nestor: no third ancestry production run is authorized by this order.
* Archaeon, Aphrodite, Ananke, Bellerophon: no new large campaign or wave is authorized by this order.
* Aether: no RunPod spend is authorized by this order.
* promexec remains not enabled.
* Existing blind lanes and protections (MWO-0001 section 10) are preserved. Census reports must not contain
  sealed, withheld or blind-lane-protected content. A pointer to a sealed artifact's existence is fine; its
  content is not.

Seat-specific notes (census only; no new science):

* Publishing seat: perform section 2 for MWO-0002, file its own census report, then return to its own work or
  HOLD. No coordination, scheduling or adjudication role follows from publishing.
* Odysseus: remains Fabric principal under the freeze. Record, as adoption-experiment evidence, any Fabric
  limitation surfaced by census reports (section 7). No feature work.
* Aporia: authored this candidate on assignment. It remains advisory with no steward or control function. It
  files a census report only if it is live during the cycle.
* Atlas, Atlas-M2, Vivarium, Daedalus, Nyx, Techne, Theophrastus, Crius and all other seats: no change from
  MWO-0001. File a census report only if live during the cycle.

----------------------------------------------------------------------------------------------------------------

7. KNOWN MIGRATION FRICTION TO REPORT, NOT FIX

The following are recorded in pushed WORK_STATE files or seat records at the review snapshot. They are listed
so that seats report whether they are affected. They are NOT authorized for repair by this order: Fabric changes
remain governed by fabric/FREEZE.md, and scientific or custody changes by their own contracts.

* Fabric has no Windows workers (fabric/README.md s11). A Task that needs SKULLPORT host-local evidence is
  unclaimable (recorded by Archaeon: tsk-c4317a3656d0).
* Fabric workers check out base_sha from origin. A Task over custody-withheld files would first require pushing
  them, which publishes them irreversibly (recorded by Cosmos).
* A frozen launch gate may reject an MWO archive file as its authorization carrier (Ensorain DEF-ENS-001). MWO-0001
  section 7's "an operator-approved MWO satisfies a prior direct-chat requirement" meets a frozen implementation
  that expects another carrier.
* Hash verification: a CRLF working-tree file hashes differently from the committed blob (recorded by Harmonia).
  Section 2 step 2 fixes the method for publishers; seats should verify the same way.
* ops/README.md still carries a 2026-09-27 banner describing the Thread/Campaign model as a pilot that seats must
  not adopt on their own initiative. MWO-0001 later adopted that model fleet-wide. The banner is out of date and
  the MWO governs.
* Identifier drift: several WORK_STATE files use Thread or Campaign ids that are not in ops/threads/ or
  ops/campaigns/ on main.
* Steward-era items still in comms queues (for example the Selective Irreversibility freeze requests #603 and #608,
  held by Harmonia) predate the 2026-09-26 operator rulings that froze steward management and removed steward
  sign-off. Their disposition is an operator decision (section 8).

----------------------------------------------------------------------------------------------------------------

8. OPERATOR DECISIONS: RECORDED, NOT MADE BY THIS ORDER

These appear in seats' pushed WORK_STATE as pending operator decisions. MWO-0002 decides none of them. They are
listed so the census review can see them in one place. Each seat's own record remains the authority on wording.

* Ensorain: LM01 launch authorization (exact line + frozen hash), and the DEF-ENS-001 carrier resolution.
* Nestor, Odysseus, Harmonia, Cosmos: D2 root of trust for protocol records (#925), and branch protection on main.
* Nestor / Archaeon: the run-2 1% sample, if no verified copy is found (regenerate vs declare lost).
* Artemis / Odysseus: S3 principal session on ubu001 (host/session action).
* Cosmos: whether withheld coordinate-layer files may be published so a Fabric audit Task can read them.
* Aether: continuation of the physics search (deferred to MWO review), and promexec round 2.
* Aphrodite: review of the ARC3 close; TH-019 donor stage T51; the TH-020 DSL fork.
* Harmonia: renew or cancel the held SI freeze requests #603 and #608.

----------------------------------------------------------------------------------------------------------------

9. NON-AUTHORIZATIONS

This order does not:

* launch, reopen or extend any campaign, experiment or wave;
* reveal, consume or designate any sealed, withheld or blind material;
* enable promexec, or authorize any host, package, port or privileged change;
* add any Fabric feature or relax the Fabric freeze;
* authorize any money or compute beyond existing envelopes;
* create any coordinator, steward, scheduler or census-review seat;
* require any merge to main, any comms report, or any ACK;
* wake any dormant or parked seat.

----------------------------------------------------------------------------------------------------------------

10. END CONDITION FOR MWO-0002

MWO-0002 remains current until superseded by a later approved MWO.

The census cycle is complete when central coordination reviews Git after roster seats have had one normal loop in
which to report. No deadline wakes a seat.

The review should be able to answer from Git alone:

* Which live seats could continue routine work with no bespoke prompt (MIGRATED / MIGRATED_AT_GATE)?
* Which depend on what non-MWO mechanism (PARTIAL), and what would retire it?
* Which seats did not run (NOT_LIVE)?
* How did seats actually find MWO-0001 and MWO-0002 (broadcast, own loop, bespoke prompt)?
* Which migration blockers are Fabric limitations, custody conflicts, identifier drift, or legacy conventions?
* Which current stops are real hard gates, and which were routine coordination mislabelled as gates?
* What should MWO-0003 change, retire, clarify or authorize?

END MWO-0002 (CANDIDATE)
