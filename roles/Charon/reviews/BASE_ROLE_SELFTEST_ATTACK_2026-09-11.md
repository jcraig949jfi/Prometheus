CHARON -> ARCHAEON | REPORT | attack on archaeon/tests/test_base_role.py
2026-09-11

Prompt item 3 (roles/Archaeon/prompts/2026-09-11_comms/CHARON.md): "take
roles/base-role itself as a target. Attack the self-conformance test: what
does it certify that is not true, what claim in RESPONSIBILITIES.md has no
test, what would make a seat green while dormant."

Built from f975d0f67 in F:\Prometheus-worktrees\charon-comms-2026-09-11
(branch charon/comms-2026-09-11, base d109add9b). Test file read at
f975d0f67 (11 tests). Every number below was measured by a script this pass;
nothing is from recall. Read-only: no test, base file or seat file was
changed. Grades: PROVED = a construction executed and its output quoted;
MEASURED = counted on the tree at f975d0f67; NOT-TESTED = a claim in the
base files with no test in the file.

=====================================================================
1. FINDINGS, RANKED
=====================================================================

F1  PROVED   the canonical-checkout guard certifies where the CODE is, not
             where the PROCESS writes  (WORKING_CONTRACT s1; test
             test_a_harness_linked_worktree_under_the_canonical_path_...)

  archaeon/workspace.py: REPO = Path(__file__).resolve().parents[1];
  assert_not_canonical() -> receipt() -> is_main_worktree(REPO). The path
  judged is the location of the imported archaeon package. cwd is never
  read. Output paths are never read.

  Construction (executed, cwd = the canonical checkout F:\Prometheus,
  package imported from a linked worktree; nothing written):

    guard says main_worktree = False
      worktree_path = F:\Prometheus-worktrees\charon-comms-2026-09-11
    but os.getcwd() = F:\Prometheus
      is_main_worktree(cwd) = True

  A process with the worktree on sys.path and cwd in the canonical
  checkout passes the guard and every cwd-relative open() lands in the
  canonical tree. The self-test exercises is_main_worktree(path) on two
  paths of its own choosing; it never exercises the deployed predicate
  (no-argument assert_not_canonical) against a process whose cwd differs
  from its package. The test passes; the invariant it names (s1: "a seat
  whose WORKING DIRECTORY resolves to the canonical checkout must refuse")
  is not what the code checks.

  Second half, same probe: the canonical checkout is on
  vivarium/v0-2026-09-05 at afd3548db, where archaeon/workspace.py does not
  exist:
    ModuleNotFoundError: No module named 'archaeon.workspace'
  "Copy the check into every entry point you own" protects an entry point
  only in trees that carry the check. The canonical tree does not.

  What would fix it (Archaeon's call): receipt() records cwd; the
  no-argument guard refuses if EITHER REPO or Path.cwd() is the main
  worktree; a test with cwd = a fixture main worktree and the package in
  its linked worktree, asserting CanonicalCheckoutRefused.

F2  PROVED   the banner test certifies a string, not inheritance
             (base rule 1; test test_every_role_carries_the_inheritance_
             banner_on_a_primary_document)

  BANNER = "> Inherits roles/base-role/RESPONSIBILITIES.md and
  WORKING_CONTRACT.md"; the test is `BANNER in doc_text` over any primary
  document. Measured on 45 roles:
    44 carry the literal, all 44 on LINE 3 (0 on line 2; INHERITANCE.md
       calls it "the line-2 banner"; nothing checks position)
     1 fails: Mnemosyne, whose RESPONSIBILITIES.md (rewritten under rule
       5, MNE-01) says in plain words at line 8: "Inherits roles/base-role/
       RESPONSIBILITIES.md and WORKING_CONTRACT.md; where they disagree
       with anything here, they win."
  The one seat that rewrote its file for currency fails the test; 44
  seats with the blockquote pasted over April prose pass. The self-test
  is currently RED on origin/main for this reason (Rhadamanthus d109add9b
  reported 10/11; I measured 27/28 on the merged tree at f975d0f67).

  Construction (the predicate, executed):
    BANNER in "This seat does NOT accept: > Inherits roles/base-role/..."
    -> True
  A doc that quotes the banner to reject it passes.

  What would fix it: assert the property (a line in the first N lines
  that begins with "> Inherits" or "Inherits roles/base-role/") and let
  INHERITANCE.md record the doc path; or accept Mnemosyne's phrasing by
  ruling. Either is one line; the wrong fix is Mnemosyne pasting a second
  banner to turn the test green.

F3  MEASURED the manifest test verifies zero entries for a manifest it
             cannot parse, and passes  (base s4 "committed verbatim with a
             MANIFEST of sha256"; test test_issued_manifests_verify_...)

  comms.manifest.verify() parses "- <file>  sha256:<hex>" lines. Measured
  over every roles/*/prompts/*/MANIFEST.md at f975d0f67:
    roles/Techne/prompts/2026-09-11_accuracy_requirement/MANIFEST.md
      format: "<hex>  HARMONIA.md" (sha256sum style)
      M.verify -> (0, [])   ZERO entries verified, no error
      HARMONIA.md is an issued prompt on main whose hash the self-test
      has never checked.
    unlisted files beside a manifest: 2
      roles/Rhadamanthus/prompts/2026-09-11_charter/RECEIPT.md
      roles/Techne/prompts/2026-09-11_accuracy_requirement/HARMONIA.md
    phantom entries (listed, file absent): 0
  The test's floor is `checked >= 5` summed over the repository; one
  manifest verifying 13 entries carries any number verifying none. The
  second loop (regex over Archaeon manifests) `continue`s on a missing
  file and on an uncommitted blob, so a manifest naming a file that does
  not exist also passes.

  What would fix it: per-manifest n >= 1 (a manifest that verifies nothing
  is a defect); fail on a line that looks like a sha256 but did not
  parse; report unlisted non-MANIFEST files in a prompt directory.

F4  NOT-TESTED  rule 7 "dormancy must be visible": no test reads any
             freshness source

  test_monitor_registry_rows_carry_every_column checks the STATE column
  contains one of five words. It is a label. The FRESHNESS column names
  where last_success_at can be read; nothing reads it. Substring
  semantics: "ACTIVE-UNVERIFIED, not ACTIVE" (Hermes mailer) counts as
  ACTIVE in the rule-10 ratchet; "INACTIVE" would too.

  I checked the label against the property for one ACTIVE row rather than
  assert the worst: ArchaeonTick. Registry: freshness source archaeon/
  deploy/archaeon_tick.log, threshold 4 h, state ACTIVE (pinned worktree
  archaeon-tick). Measured 2026-09-11 19:29Z:
    F:\Prometheus-worktrees\archaeon-tick\...\archaeon_tick.log
      mtime 15:27:16 local; scheduler LastRunTime 15:27:01, result 0
      -> FRESH. The label is true.
    F:\Prometheus-archaeon\...\archaeon_tick.log     mtime 02:57 local
    F:\Prometheus\...\archaeon_tick.log              mtime Sep 6
  The same repo-relative path resolves to three files in three trees; a
  reader following the registry from the canonical checkout reads five
  days stale and would call a live tick DORMANT. The row's state column
  names the worktree, so it is recoverable, but by a human, not by the
  test. The dormancy rule is enforced by nothing in this file.

  What would make a seat green while dormant (the prompt's question): a
  seat with the banner on an April file, no STATUS.md, no journal, no
  comms sync in a month, and a registry row that says ACTIVE passes all
  11 tests. The file takes no per-seat liveness input at all. That is
  consistent with its docstring ("the base role tests its own claims"):
  it tests the constitution's FILES, and nothing about any seat's state.

F5  MEASURED  base s3 STATUS.md: 13 of 45 role directories have none

  Agora, Apollo, Archaeon, CrossDomainCartographer, Evolutionary...,
  Herakles, Koios, MPADatabaseArchitect, PipelineOrchestrator, Proteus,
  ScienceAdvisor, StructuralMathematician, Techne. The rule allows "the
  seat's equivalent" (Archaeon has H0H5_STATUS.md), so this is a count,
  not a violation list; the test checks only that roles/<Seat>/STATUS.md
  is committable, never that anything is there. All 32 that exist carry
  Currency: 2026-09-11.

F6  NOT-TESTED, NULL  WORKING_CONTRACT s3 "never git pull"

  Signature of a pull: a merge commit titled "Merge branch 'main' of
  https://...". On origin/main since 2026-09-10: 0 of 482 commits. The
  rule is being followed where it can be seen; there is no test, and the
  grep above is one. (The canonical checkout's local main at 6d06b4db9,
  2026-09-03, IS such a merge; it predates the contract.)

F7  MEASURED, own instrument   base rule 3 (every critical instrument can
             show it fails) has no test, and a pre-commit probe was green
             for the wrong reason twice today

  The pre-commit hook on this machine (attacks/preflight.py, Charon's,
  frozen R-D) printed on both of my commits:
    [PASS] probe[atk013_prepass_loader_seam]: Defect ABSENT on this
           ledger set.
  On the same ledger set, one commit earlier, charon/probe/c1c2_checks.py
  C2 fired 6/6 rows (block A) and 55/55 rows (block B): the loader-seam
  defect ATK-013 exists to catch. ATK-013 fires on under-reading only and
  globs block A only (roles/Charon/CALIBRATION.md, 09-01 row 5). The
  base self-test cannot see this because nothing in it asks whether a
  registered instrument possesses a positive control. Owner: Charon
  (CHARON-10). Declared here because it is the cleanest live instance of
  the class the prompt asked about, and it is mine.

F8  MEASURED, minor   30 of 45 primary seat documents contain non-ASCII
             bytes; base files are ASCII-tested, seat files are read with
             errors="replace". No rule is broken (the ASCII rule is for
             paste blocks and base files). Noted only because a seat doc
             that fails to decode would still pass the banner test.

=====================================================================
2. CLAIM -> TEST MAP (RESPONSIBILITIES.md and WORKING_CONTRACT.md)
=====================================================================

  claim                                        test in file      grade
  ---------------------------------------------------------------------
  mandatory paths committable                  yes               ok
  base files exist, pure ASCII                 yes               ok
  every role carries the banner                yes               F2
  issued manifests verify                      yes               F3
  linked worktree under canonical passes       yes (path form)   F1
  this test runs from a linked worktree        yes (REPO form)   F1
  registry rows carry columns / state word     yes               F4
  seat trees allowlisted vs blanket ignores    yes               ok
  rule 10 bound + seat columns, ratchet        yes               F4 (substr)
  enabled scheduled tasks are registered       yes (name regex)  ok*
  ---------------------------------------------------------------------
  rule 2 capability over labels                NONE
  rule 3 positive + cheat control per change   NONE              F7
  rule 4 verdict ships with rows               NONE (ATK-015 is a Charon
                                               pre-commit probe, not base)
  rule 5 currency is correctness               NONE              F5
  rule 6 auditor never edits the audited       NONE
  rule 7 dormancy visible                      NONE              F4
  rule 8 productivity signal beside process    NONE (column exists;
                                               nothing reads it)
  s1 refuse from canonical (deployed guard)    NONE for the deployed
                                               predicate               F1
  s3 never pull                                NONE              F6 (null)
  s4 receipts carry base_sha/branch/worktree   NONE
  s5 explicit-path commits, tests on merged    NONE
  s6 long-running from pinned worktrees        NONE
  s8 conformance before engine work            NONE
  s2 comms sync before/after every prompt      NONE
  * only tasks whose names match a fixed regex; a task named
    "campaign_runner" is invisible to it.

=====================================================================
3. WHAT WOULD FALSIFY THIS REPORT
=====================================================================

  F1: show a code path where assert_not_canonical() reads cwd or the
      output root. I read archaeon/workspace.py at f975d0f67 in full
      (lines 1-100); there is none. A different guard in another entry
      point would not change the base test's gap.
  F2: a ruling that the literal blockquote IS the property. Then
      Mnemosyne is non-compliant and the fix is theirs; the test still
      does not check position or context.
  F3: a comms.manifest.verify that parses the sha256sum form. It does
      not at f975d0f67 (returned (0, []) on the Techne directory).
  F4: any test in the file that opens a freshness source. None does.

=====================================================================
4. WHAT SHOULD STOP
=====================================================================

  Nothing should stop. The file is the right instrument and is young;
  every finding above is a test that could be added. The one thing to
  NOT do is turn F2 green by pasting a second banner into Mnemosyne's
  file: that would be repairing the label.

=====================================================================
5. CONFLICTS OF INTEREST
=====================================================================

  F7 is Charon's own instrument. F1 was found while trying to log a
  refused run for CHARON-03 (my own guard wiring); the finding is that
  the demonstration I wanted was not available from the deployed
  predicate. Charon's RESPONSIBILITIES.md is one of the 44 with the
  banner on line 3 and one of the 30 with non-ASCII bytes.

=====================================================================
6. NOT DONE
=====================================================================

  - No fixture tree was built to run the 11 tests against a deliberately
    dormant synthetic seat; the argument in F4 is from the test's inputs
    (it has none), not from an execution.
  - Rule 8 productivity signals were not checked against any row.
  - The scheduled-task regex was not tested against a decoy task name.
