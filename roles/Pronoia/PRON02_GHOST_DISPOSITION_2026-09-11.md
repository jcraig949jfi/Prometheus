# PRON-02 -- disposition of the Era 1 ghost actuator on M2

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Built from 213873bc1 in
Prometheus-worktrees/pronoia-base-role, host M2 (SPECTREX5).
Operator authority: the PRON-02 mission directive of 2026-09-11
("neutralize the executable hazard if and only if your evidence shows it
is not a live dependency ... do not destroy the only evidentiary copy
before recording what it is").

This file is the record made BEFORE the neutralisation. The deletion
receipt is section 6, appended after the act.

## 1. The specimen, identified exactly

    path (M2)        <canonical checkout root>/pronoia.py
    size             32,165 bytes on disk
    mode             -rwxr-xr-x
    mtime            2026-04-11 11:26:01.874057300 -0400
    line endings     CRLF present
    sha256 (on-disk, raw bytes)
                     a823ecc8325c2f5d6eed0c8edc4ffaa5a0344453ede51aa518f0f0ba8311a460
    sha256 (LF-normalised, 31,293 bytes -- the repository-artifact hash)
                     4d37633a6181ec5b2ebdd3ed50c11fa86b9998418e5296045558ea9a15114350
    git blob id      96f674b29be55c816a923613fe5798dd48304a0a
    tracked          no  (git ls-files --error-unmatch -> no match)
    ignored          yes (.gitignore:174:/pronoia.py)
    on origin/main   no  ("exists on disk, but not in origin/main")

## 2. Provenance: exact, and fully recoverable from git

`git hash-object pronoia.py` returns 96f674b29be55c816a923613fe5798dd48304a0a,
which IS the blob at `3b3c74bc0^:pronoia.py`. A content diff of the
on-disk copy (CR stripped) against `git show 3b3c74bc0^:pronoia.py`
produces ZERO lines.

So the on-disk file is a CRLF working copy of a blob that git still
holds. Its history:

    eb17886fa  2026-03-23  added  ("agents: add Aletheia, Clymene,
                                    Hermes, Pronoia + wire full pipeline")
    9e189d683  2026-04-01  last content modification
                                   ("Pipeline health, backoff fixes,
                                    and documentation")
    3b3c74bc0  2026-04-23  deleted from the tree, with 24 other
                                   root-level scripts
                                   ("Clean up repo for external visibility")
    .gitignore:174                 /pronoia.py added, so it can never be
                                   re-added by accident

THIS IS THE DECIDING EVIDENTIARY FACT. The file is NOT a unique
artifact. Anyone can recover it byte-for-byte at any time with:

    git show 3b3c74bc0^:pronoia.py
    git cat-file -p 96f674b29be55c816a923613fe5798dd48304a0a

Deleting the disk copy therefore destroys no evidence. What the disk
copy uniquely carried -- its path, mode, mtime and CRLF state -- is
recorded in section 1 above and is the only thing that dies with it.

## 3. The hazard, stated mechanically

pronoia.py:69 publish_reports() does, in order, with cwd set to
PROMETHEUS_ROOT (the directory the script lives in):

    for p in 11 paths:  git add <p>
    git diff --cached --quiet          (proceed only if something staged)
    git commit -m "pronoia: auto-publish reports <timestamp>"
    git push                           (no remote, no refspec: current
                                        branch to its upstream)

all with capture_output=True, so every git error is swallowed and never
printed.

On M2 the script sits in the CANONICAL CHECKOUT, whose HEAD is `main`
tracking `origin/main`. Running it there breaches D-23 four ways:

  s1  a mutating git operation (add/commit/push) in the canonical
      checkout, which no seat may perform
  s2  no worktree, no task branch, no recorded base SHA
  s5  `git commit` with NO pathspec and NO message file: it commits
      EVERYTHING staged in the canonical index, which is precisely the
      "pathspec-less commit that sweeps another seat's staged work" the
      contract names. With many seats sharing this host, the index is
      not reliably empty.
  s5  `git push` straight to main with no ancestor check and no tests

It also stages `agents/aletheia/data/` (a SQLite database) and
`docs/TODO.md` (deleted from the tree in the same 2026-04-23 commit).

### 3.1 The triggers -- the hazard is not one file

pronoia.py is the ACTUATOR. On M2 there are three double-clickable
TRIGGERS, all of them root-level .bat files that are ALSO on disk,
untracked, and ignored by a blanket rule (.gitignore:159:/*.bat) rather
than by name:

    run_intelligence_pipeline.bat
        cd /d "%~dp0"                       (= the canonical checkout)
        "once" branch:  python pronoia.py scan --publish
        default branch: opens a Windows Terminal tab running
                        python pronoia.py scan --every 2 --publish
                        (hardcoded `cd /d F:\Prometheus`, an M1 path
                         that does not resolve on M2 -- this branch
                         fails here; the "once" branch does not)

    run_all.bat:41
        start ... cmd /k "cd /d %~dp0 && python pronoia.py scan --every 2 --publish"

    run_all.bat:57  (the :intel_only label)
        the same command again

run_all.bat:41 is the worst case: an UNBOUNDED two-hourly loop that
publishes to main from the canonical checkout, started by
double-clicking one file.

All three were deleted from the tree in the same commit as pronoia.py
(3b3c74bc0) and all three survive on disk, for the same reason.

## 4. Dependency search -- the "if and only if" test

The question is whether anything currently depends on THIS EXACT COPY.
Every check below was read-only. pronoia.py was NEVER EXECUTED, and its
publish path was never exercised against any repository.

    CHECK                                        RESULT
    ------------------------------------------   ---------------------------
    running process with pronoia in its command   NONE. The only matches on
      line (Get-CimInstance Win32_Process)        M2 are this seat's own
                                                  claude.exe session and its
                                                  own grep/bash helpers.
    scheduled task referencing pronoia            NONE (schtasks /query /v)
    python module import (import/from pronoia)    NONE anywhere on
                                                  origin/main. The two
                                                  regex hits are prose in
                                                  a YAML comment and a
                                                  pivot document.
    tracked launcher (.bat/.ps1/.sh/.cmd/.xml)    NONE on origin/main
    tracked references to the string pronoia.py   28 files, ALL prose:
                                                  READMEs, pivot dossiers,
                                                  pipeline YAML specs, a
                                                  docs/index.html hyperlink,
                                                  and .gitignore:174 itself.
                                                  No invocation among them.
    untracked launchers on disk                   THREE, listed in 3.1.
                                                  They are triggers FOR the
                                                  actuator, not dependents
                                                  ON it: each invokes it by
                                                  filename. With the
                                                  actuator gone they fail
                                                  closed with "python: can't
                                                  open file 'pronoia.py'".

One documentation defect found and NOT repaired (out of lane, recorded
for whoever owns docs/): docs/index.html:94 links "Pronoia" to
https://github.com/jcraig949jfi/Prometheus/blob/main/pronoia.py, which
has 404'd since 2026-04-23.

### 4.1 The limit of this finding, stated

This evidence covers M2 (SPECTREX5) only. This seat cannot read M1's,
M3's or M4's filesystem and did not try. run_intelligence_pipeline.bat
hardcodes `F:\Prometheus`, which is M1's canonical path, so a
similar untracked copy may exist there. Nothing in this file asserts
anything about hosts other than M2, and the neutralisation below changes
nothing on them. Registered as the open remainder in section 7.

## 5. Disposition

CONDITION MET. The operator's test was "neutralize if and only if your
evidence shows it is not a live dependency". Section 4 shows no process,
no scheduler, no import, no tracked launcher and no live caller depends
on this copy; section 2 shows the content is recoverable byte-for-byte
from git, so the deletion destroys no evidence.

ACTION: delete the actuator, `pronoia.py`, from the M2 canonical
checkout root.

SCOPE DELIBERATELY NOT WIDENED: the three .bat triggers are NOT deleted.
Two reasons. (a) With the actuator gone they are inert and fail closed.
(b) run_all.bat also launches the forge pipeline and other lanes; it is
not this seat's file to remove, and removing a launcher another lane may
rely on to trade a latent hazard for a broken workflow is not an
improvement. They are reported instead, in section 7 and to their
owners.

The single permitted write in the canonical checkout under D-23 s1 is
"the once-only deletion of your OWN untracked scratch during a declared
clean-up, reported afterwards". pronoia.py is this seat's own untracked
artifact; this is that declared clean-up; section 6 is the report.

## 6. Deletion receipt

    APPENDED AFTER THE ACT -- see below.

## 7. What remains open after this disposition

  PRON-02a  The three untracked .bat triggers on M2 remain on disk,
            ignored by a blanket .gitignore:159:/*.bat rule. They are
            inert now, and they are still double-clickable files that
            name a publish-to-main workflow. Reported to the operator;
            not this seat's to delete.

  PRON-02b  Two OTHER root-level untracked .bat files on M2 contain
            `git push` or `git commit` of their own:
            run_all_pending_tasks.bat and run_overnight_gap_closing.bat.
            They are outside PRON-02 and were not read beyond that grep.
            This is the evidence that turns PRON-09 from a hypothesis
            into a measurement: the class "deleted-from-the-tree,
            blanket-ignored, still-runnable, git-mutating root script"
            has at least three members on this host.

  PRON-02c  M1/M3/M4 unknown (section 4.1). A copy may exist on M1,
            whose path the M2 launcher still hardcodes.

  PRON-02d  docs/index.html:94 links to a file that has not existed on
            main since 2026-04-23.
