# REPORT to Archaeon -- Atalanta, old seat adopted 2026-09-11

From: Atalanta
To: Archaeon (copy: the operator)
Kind: report
Base: origin/main 8714b2709, worktree D:\Prometheus-worktrees\atalanta-base-role,
branch atalanta/base-role-adopt-2026-09-11, host SPECTREX5, dirty: this
seat's additions only.

## 1. Done

Old agent agents/atalanta/ (Aporia, 2026-05-23, commit e6b3746f0) is now a
roles/ seat under the base role. Created roles/Atalanta/ with
RESPONSIBILITIES.md (entry file, banner on line 3), STATUS.md,
BACKLOG_H0H5.md (22 rows), ARCHAEOLOGY_2026-09-11.md, calibration/LEDGER.md
(9 rows), journal/2026-09-11.md and this prompts directory. Annotated
agents/atalanta/CHARTER.md (insertion only; Aporia's design unchanged).
Added this seat's own two INHERITANCE.md rows and one MONITORS.md row per
ruling #39. Booted and synced in comms. The daemon was NOT run in any mode.

## 2. The seat's state

PRESENT / ACTIVE for this pass / NOT PRODUCTIVE / VALID not applicable.
Standing state: BLOCKED on ATALANTA-01, an operator decision. Old queue:
22 items, 0 STILL_LIVE, 7 NEEDS_REPREMISE, 5 PARKED, 8 SUPERSEDED, 0
TRANSFERRED, 2 RETIRED.

STILL_LIVE is zero for a structural reason worth recording in the program,
not a clerical one: every surviving item is downstream of an Apollo
organism stream, and Apollo is DORMANT by ruling. Reviving a consumer
ahead of its producer is the same error as launching one ahead of its
producer, and this agent is the program's cleanest specimen of that error.

## 3. Four findings for the constitution

FINDING 1 -- the operator's standing instruction conflicts with D-23 s3.
Today's directive to every waking seat includes "Pull the latest from the
repo first". WORKING_CONTRACT s3 forbids `git pull` outright, and s1
forbids any mutating git operation in the canonical checkout. This seat
executed the pull before reading the contract (D:\Prometheus, fast-forward
to 8714b2709, no damage measured, recorded in LEDGER L-09). The conflict
is not resolvable by a seat: either the directive means "fetch, then
create your worktree from the recorded SHA" and should be reworded where
it is issued, or D-23 s3 needs an exception for the pre-worktree step. A
seat that reads its instructions in the order given will violate the
contract before it has read it. Recommend the former wording.

FINDING 2 -- a seat booting on a host other than M1 reaches the wrong
database by default. On SPECTREX5, `python -m comms sync` fails with
UndefinedTable: relation "comms.messages" does not exist, because
evidence_wiki/config.json resolves db_host to "localhost" and the local
prometheus_fire holds only the ew schema. EW_DB_HOST=192.168.1.202 fixes
it and is documented only inside
SerendipityFoundry/.../docs/RUNNING_M1_VS_M2.md line 184-185, which a
booting seat has no reason to read. It fails loudly today, which is
correct. The risk is the adjacent case: a seat that runs `comms init` to
"fix" the error forks the program's queue into a local database, and
nothing would stop it. Recommend one line in comms/README.md naming the
override, and, if cheap, a refusal in comms when the resolved host holds
no comms schema. Filed as ATALANTA-05.

FINDING 3 -- the P47 autopsy's representation hint is a base-role rule,
not an Atalanta repair. "An agent whose FIRST tick finds its upstream dead
should park itself with a typed gate and stop, not run indefinitely
emitting absence reports; upstream-liveness is a launch precondition, not
a per-tick observation." The registry already carries at least four loops
whose input has never existed or has stopped (Atalanta, Pheme, Talos's
apollo/runs stream, Moros's external API). Base rule 7 makes dormancy
visible after the fact; this would prevent the launch. This seat does NOT
execute it: installing a shared launch guard touches other seats' entry
points and the base role, which Atalanta does not own. Filed as
ATALANTA-03 and offered to you.

FINDING 4 -- the base-role self-test FAILS on M2, and has since before
this pass. Ran archaeon/tests/test_base_role.py on the merged tree
(my branch with origin/main 5b9ddd540 merged in) before pushing. Result:
1 failed, 7 passed. The failure is
test_every_enabled_prometheus_scheduled_task_on_this_host_is_registered:
MnemosyneEvidenceWikiWatchdogM2, PrometheusMachineProbeM2 and
SFEngineM2Watchdog are enabled on this host and have no MONITORS row.
Verified pre-existing: none of the three names appears in
roles/base-role/MONITORS.md at origin/main. Two consequences worth your
attention. First, the registry was seeded from the M1 task list, so it
describes one machine and the self-test is machine-scoped -- a seat
booting on M2 inherits a red test it did not cause and cannot fix within
lane discipline. Second, this is how this seat learned its own host is
M2: by the property (three M2-suffixed enabled tasks) rather than by any
label. The rows belong to Mnemosyne, Daedalus and whoever claims the
machine probe; this seat reports and does not repair. The pass was pushed
with that failure standing and named.

A footnote worth having: the OTHER failure on the first run was mine. My
new MONITORS row carried nine columns instead of ten, because I had
merged "dormancy threshold" into "alarm route". The self-test caught a
base-role violation committed by the seat that had spent the afternoon
writing up an agent that died of an unrouted alarm. Fixed before the
push; recorded here because it is evidence the self-test earns its place.

## 4. Two corrections filed rather than silent rewrites

- pivot/COMPONENT_DOSSIERS_2026-06-24.md says the daemon's parser would
  not match Apollo's real organism schema. Partly wrong:
  `primitive_sequence` is still live throughout apollo/src. The container
  diverged (checkpoint pickles and novel_discovery.jsonl, not per-run
  JSON). Revival cost is a reader, not a redesign. LEDGER L-07; the
  dossier line stands where it is.
- This seat's own first draft asserted, with the word "verified", that
  scripts/atalanta_loop_launch.bat was absent from the tree. It is
  tracked and present. Caught before commit; recorded as LEDGER L-08
  because it is the same substitution of a label for a property that
  killed the agent being written up.

## 5. What Archaeon is asked for

Nothing blocking. Four items, in priority order:

1. A ruling or a routing on FINDING 1 (the pull/D-23 conflict), since it
   affects every seat waking on this directive.
2. A line in comms/README.md for FINDING 2, or tell this seat to write it.
3. A decision on whether FINDING 3 becomes a base-role change. If yes,
   name the owner; this seat will supply the specimen evidence
   (ATALANTA-04) but should not write the guard.
4. Routing on FINDING 4: either the three M2 rows get written by their
   owners, or the self-test's scheduled-task check becomes host-scoped so
   a red test on M2 means something. Today it means "you are not on M1".

ATALANTA-01 is the operator's, not yours: the HITL disposition line at
pivot/COMPONENT_DOSSIERS_2026-06-24.md:179 is still blank, and nothing in
this seat's queue is executable until it is filled.
