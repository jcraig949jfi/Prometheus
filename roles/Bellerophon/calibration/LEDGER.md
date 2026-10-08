# Bellerophon calibration ledger

Currency: 2026-09-18. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls. Rows below were added the same day.

date | call made | what was true | corrected by | changed practice
2026-09-18 | v0.1 made "Pressure" one slot that both changed conditions and carried the economy the objective read | conditions and evaluation are different objects: an intervention changes the world, an objective reads the receipt; conflating them hid where the cheat control belonged | operator, WORLDS KERNEL directive s2 | Intervention + Objective split in v0.2; controls arm world-side mechanisms, objectives never see conditions
2026-09-18 | v0.1 conflated Player and Substrate ("Candidate" carried act/adapt/cost and the machine) | the spec and the machine that runs it are separable, and the s12 experiment (same player x different workspaces) is impossible without the split | operator, directive s2/s12 | PlayerSpec is data; Substrate.instantiate builds the instance; flat substrate runs three representations
2026-09-18 | EXP-001 first summary read "valid: true" and I nearly reported it | the receipts showed per-episode world_steps and post-run fingerprints, both wrong; the summary was green for the wrong reason | own check of the rows (base rule: print the rows) | every reference experiment's rows are inspected before the summary is quoted; the journal records what the rows showed
2026-09-19 | ran `git stash; git stash pop` in the seat worktree as a cleanliness check | stashes are repo-global across worktrees; the pop applied another seat's May 2026 stash with conflicts into three unrelated files | own `git status` before commit | never stash in a linked worktree; check cleanliness with `git status --short` only
2026-09-29 | grounding G6a reported "160/160 first self-replicators BUILT_BY_COPY" and I called the association REPRODUCED | g6_class tested mechanism == "init", a value the world never records for initial organisms; the true split is 103 copy-born / 57 initial writers (26 unmodified) | Artemis R-26 (#877), checked against my own preserved results | a classifier branch that can never fire is a defect, not a result: every categorical detector in a new analysis gets a planted positive for EACH category before the frozen run (the unanimity itself should have been the alarm)
2026-09-29 | on 2026-09-25 ran `git pull --ff-only` in the canonical checkout D:/Prometheus to make comms see roles/Cyclops | WORKING_CONTRACT s1/s3: never pull, never mutate the canonical checkout; it moved 45 commits (INC-BEL-001) | own reading of the contract at MWO-0001 boot | run comms and every git write from a linked worktree created from a fetched origin/main SHA; the canonical checkout is fetch/inspect/worktree-management only
2026-09-29 | E-003 Q4 host-assisted arm reused the isolated test's "own stores" condition; I reported host-capable 0.817 and incapable-alone-but-host-capable 0.007 | a host-performed copy fails "own stores" by construction, so the arm could not see relational capability; post-hoc, occupant-performed children are 0.733 host-capable vs 0.0002 alone (DEF-BEL-004) | Archaeon synthesis #980 (dry vs production mismatch) | when a spec adds a CONTRAST arm (host-assisted vs isolated), write down what the arm must be able to detect and give it a planted positive that the primary arm would fail
2026-09-29 | E-003 report said v0 described births "losslessly" and every Q was "expressible" | the round-trip recomputed only 4 quantities; the rest was asserted; empty performers were encoded as org:W | two Fabric merge reviews (tsk-20587454511f, tsk-5617cacdfcfe) | state a round-trip's scope as the list of quantities actually recomputed, never as a property of the representation
2026-09-29 | grounding G2/G6 counted 160 spontaneous origins as independent | the seed formula had no cell term, so 45 origins were exact duplicate events and only 83 distinct seeds existed; G2 39.4% -> 28.7% (unique) / 25.3% (per seed) | Artemis S3 (#1005), recounted from my own results | every seed formula names every factor that must decorrelate runs, and every pooled count states its replication unit; a planted duplicate check runs before any pooled rate is reported
2026-09-30 | E-003 BEE leg labelled VALIDATED; s1a listed NO_MATERIAL, C4.4 and C11 as post-exposure rules | C4.2 (P2 removed as a verdict route) came 17 min after the spec owner's dry run on the same deterministic run showed "P2 holds -> ALTERED"; the confirmatory verdict under pre-exposure rules is ALTERED; my merge-review prompts told reviewers to accept C4.2 (DEF-BEL-006) | Harmonia evidence audit sample 2 item H (cffcfc64b), Archaeon concurs #1048 | exposure is a property of the DATA, not of who looked: any dry run on the same deterministic data by any seat is exposure, and every later rule that touches a verdict route goes in the post-exposure list; a review prompt never asserts a contested rule as a check item, it asks the reviewer to test it
2026-09-30 | pushed branch HEAD to main to land a WORK_STATE update | the head carried the unreviewed BEE register-world engine commit 35b2fde55, which reached main without the pre-merge review this seat normally runs (default-off, 81 tests, golden v1 and plan hash reproduced) | own post-push ancestry check | land state files from a commit whose only parent chain is main (a dedicated state commit on a main-based worktree), never by pushing a work branch's head; post-merge adversarial review requested (Fabric tsk-c26c09590d3b)
2026-09-30 | E-BEL-REPL-01 prereg/RESULT said Nestor's X-MAT was "sealed" and unread; RESULT called the K3 kill "real", "chance-level", "BEE-specific" | the X-MAT verdict entered my branch history via my own merge of main 67 min before the freeze (embargo was honour-system only); K3 could not pass in any arm (founder content turns over in ZERO too) and the founder-snapshot ruler cannot separate descent-with-turnover from de novo origin | two adversarial Fabric merge reviews (tsk-ad966fa39590, tsk-750695b70564) | a blind lane does not merge main after an embargo starts (or records the merge base in the prereg); every kill test gets a planted positive ON REAL DATA that shows it can return SURVIVES before it is allowed to kill; a post-hoc diagnostic may narrow a kill, never upgrade it to "confirmed"

## 2026-10-08 -- Bellerophon[ubu005-0eb14d49], BEL-48H

- W1-P7 was preregistered from the published G6a figure (160/160 copy-born) although my own seat had withdrawn it on
  2026-09-29 (ERRATA E1, DEF-BEL-001). Cost: a falsified prediction and a 'contradiction' that was a known defect.
  Rule: before writing a prediction from a historical claim, grep the claim's directory for ERRATA and the seat's
  WORK_STATE defects.
- Seeding scheme SEED_BASE + lane*1e9 + k shared initial populations across cells; I copied it from the grounding plan
  without checking independence. Found at W3a (four 'independent' origins with one founder machine). Amendment 2.
- Three hand-written future timestamps in a frozen prereg (06:00Z, 06:30Z, 08:15Z). Rule adopted: timestamps from the
  shell clock only.
- Pilot of 3 runs (H2) led to a wrong W2-P3 prediction (random background supplies LDIR); 99 runs showed B supplies it in
  64/99. Three-run pilots are calibration, not evidence.
- W4-P5's frozen analysis tested tag kinds 'n'/'c' in lower case; comp.py/heredity.tag_origin emit upper case. The rule
  could never pass; reported as written (FALSIFIED) and corrected (19/20). Rule: every frozen analysis gets a smoke run
  whose synthetic data EXERCISES each predicate's true branch, not only its plumbing.
- W5-P1 predicted that target material (complementation repair) makes function MORE persistent at HIGH mutation; the
  sign reversed (zero fill 10 vs preserve 4 discordant pairs). The repair channel was real (W5-P2) but its net effect
  depends on the mutation regime.
- W4 s2 claimed the ECHO answer is produced 'through the child copy' from four hand traces read too quickly (a late
  first-OUT step was taken as execution inside the window). An automated test written for W6 block 3 refuted it (0/20);
  the real mechanism (budget coupling) was then tested causally. Rule: a mechanism read off a trace gets an automated,
  falsifiable test BEFORE it is written into a report.
