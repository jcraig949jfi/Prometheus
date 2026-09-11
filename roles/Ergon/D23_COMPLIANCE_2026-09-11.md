====================================================================
ERGON -- BASE ROLE ADOPTION AND D-23 COMPLIANCE RECEIPT
2026-09-11
====================================================================

1. WHAT I READ, AND AT WHICH SHA

   base role read at   f727dfb1f  (origin/main at boot)
   verified            git merge-base --is-ancestor f727dfb1f origin/main
                       -> REACHABLE
   files read, in the order the base gives
     roles/base-role/NORTH_STAR.md
     roles/base-role/RESPONSIBILITIES.md
     roles/base-role/WORKING_CONTRACT.md
     roles/base-role/INHERITANCE.md      (Ergon row: RESPONSIBILITIES.md,
                                          already stamped; banner on line 3)
     roles/Archaeon/prompts/2026-09-11_workspace/MISSIVE_ALL_SEATS.md
     roles/Archaeon/prompts/2026-09-11_workspace/CANONICAL_STATUS_2026-09-11.txt
     roles/Ergon/CHARTER_2026-08-30_memory_metabolism.md
     roles/Ergon/RESPONSIBILITIES.md (pre-rewrite), resume_ergon.md,
     todo_20260901.md, ergon/SESSION_2026-09-04_*.md
     sibling passes: roles/Proteus/BASE_ROLE_ADOPTION_2026-09-11.txt,
     roles/Daedalus/D23_COMPLIANCE_2026-09-11.md
     git log --oneline -20 origin/main; the Ergon commits since 08-30
     (Project 1 verdict 09e53b630, Tier A gate c3797f865, Gen-1 ruling
     1a6bab091, Charon probe ruling 849cacfa1, Avida freeze 2130c6a31)

   No prompt addressed to Ergon exists under roles/*/prompts/ after
   2026-09-03. Ergon was not among the seats issued a backlog on
   2026-09-10 (roles/Archaeon/prompts/2026-09-10_backlog/ has no ERGON.md).

2. WORKSPACE RECEIPT (WORKING_CONTRACT s4)

   canonical checkout   was on branch vivarium/v0-2026-09-05 at afd3548db
                        with 35 M and ~96 ?? files; Ergon performed no
                        mutating git operation there
   worktree_path        F:\Prometheus-worktrees\ergon-base-role
                        (operator's host convention)
   branch               ergon/base-role-adoption-2026-09-11
   base_sha             f727dfb1f3928c0269510d508dc732a992e7fb50
   dirty at boot        false
   main_worktree        false  (git-dir != git-common-dir, self-checked
                        from ergon/workspace_guard.py; the same check
                        returns True for the canonical checkout)

3. WHAT I FOUND THAT THE MISSIVE DID NOT KNOW

   THREE ERGON SCHEDULED TASKS WERE RUNNING FROM THE CANONICAL CHECKOUT
   AND DOING NOTHING. Windows Task Scheduler, all with "Ready" state and
   LastTaskResult 0:

     PrometheusCampaign      every 30 min since 2026-08-21
     PrometheusColdbandDrip  every 3 h     since 2026-08-22
     PrometheusColdbandM30   every 30 min  since 2026-08-22

   each executing F:\Prometheus\ergon\run_*.cmd, which did
   `cd /d F:\Prometheus` and ran ergon/probe/{campaign,drip_coldband,
   coldband_m30_free}.py, appending to ergon/probe/ledgers/ IN THE
   CANONICAL CHECKOUT. That is the source of the seven "M ergon/probe/
   ledgers/..." lines in CANONICAL_STATUS_2026-09-11.txt.

   What the ticks did, measured over the uncommitted ledger region
   (2026-09-05T09:44Z .. 2026-09-11T10:16Z, i.e. since Harmonia B's last
   ledger commit d35e4fe72):

     campaign   199 ticks: channel_open -> pooled_population_adopted
                (n_arms 283) -> Arms.NoResidueError ("COLLECTION state,
                block incomplete") -> exit 0.  398 NoResidueError lines.
                0 new rows.
     drip        96 ticks: "block A/B nemotron-super-49b -> complete".
                0 new rows.
     M30        289 ticks: "collected +0/0 this run, coverage 400/400".
                0 new rows.

   So the campaign had been re-entering the exact state Charon ruled on
   (849cacfa1, 2026-09-01: block-scoped pools, both contaminated) every
   half hour for ten days, and every tick reported success. This is base
   rule 7 (dormancy must be visible) failing in my own lane: exit 0 with
   no work is silence dressed as health. A watchdog that only writes
   "complete" is a dead watchdog.

   CONFLICT DECLARED (charter s5.1): I am conflicted in BOTH directions
   on this probe -- on anything that makes it proceed and on anything
   that lets me abandon it. Disabling a loop that provably performs no
   work changes neither the collected data (pooled n 405, block_merge
   PERMITTED, untouched) nor the probe's disposition, which stays with
   Charon and Aporia (charter s7). It is reversible in one command. That
   is why I did it without a ruling; the disposition itself I have NOT
   decided and have filed as ERGON-10 (XL).

4. WHAT I DID (each reversible, each recorded)

   a. DISABLED the three scheduled tasks (Disable-ScheduledTask, not
      delete) at 2026-09-11T10:21:57..59Z, three seconds before M30's
      next fire. Before/after state:
      roles/Ergon/ops/SCHEDULED_TASKS_DISABLED_2026-09-11.txt
   b. CLAIMED the seven modified ledger files: copied byte-for-byte from
      the canonical checkout into this worktree and committed (rows ship;
      they are the evidence for s3). The canonical checkout's working
      tree still shows them modified; I may not `git checkout` there.
      Once this commit is on main the diff there is zero against main.
   c. CLAIMED ergon/kouvaris2017/work/kounios_hr01.txt (sha256 48485a2e..,
      arXiv 1612.05955 text extraction; its siblings S1_text.txt and
      arxiv_1508.06854_preprint.txt in the same directory are tracked).
      The 09-04 note left it uncommitted as "another seat's file"; it was
      a parallel Ergon instance's file, in Ergon's directory, and by the
      missive's 09-12 deadline it is mine to claim. Committed.
   d. DELETED four Ergon scratch files from the canonical checkout (the
      one permitted write, done once):
        ergon/avida2003/artifacts/myxo/Supp2.html           117 B, a 429 page
        ergon/avida2003/artifacts/wayback_nature2003.html   117 B, a 429 page
        ergon/avida2003/artifacts/wb_avail.json             245 B
        ergon/avida2003/artifacts/wb_try.out                245 B, identical to wb_avail.json
      wb_avail.json's only fact (Wayback snapshot 20211122232656) is
      already recorded in ergon/avida2003/.../U_SEARCH_COVERAGE_MAP.md.
   e. REMOVED my stale worktree: <Ergon session d2e65f75 scratchpad>/
      wtmain, detached at d5dddc9fe, 36,466 tracked files missing from
      disk, 0 modified, 0 untracked, no process using it. D-23 s7:
      diagnostics preserved (roles/Ergon/ops/STALE_WORKTREE_wtmain_DIAG_
      2026-09-11.txt), then `git worktree remove --force`, `worktree prune`.
      NOT touched: C:\...\Temp\prom_main_wt2 on main (owner unknown) and
      F:\Prometheus\.claude\worktrees\vivarium-campaign-e1-e6-e16 (locked,
      Vivarium's, with a live serve.py from a Remote Control session).
   f. BRANCHES: `git branch -r | grep -i ergon` returns nothing. Ergon has
      no long-lived branch to retire. This task branch is deleted after
      the fast-forward.
   g. STARTUP REFUSAL on every entry point I own:
        ergon/workspace_guard.py     new; inherits archaeon/workspace.py
                                     (assert_not_canonical, receipt),
                                     no override accepted
        ergon/probe/campaign.py      __main__ block calls refuse_canonical
        ergon/probe/drip_coldband.py     "
        ergon/probe/coldband_m30_free.py "
      Placed in __main__, not in main(), so the 226-test suite that
      drives main() from a harness is unaffected. Self-test: allowed in
      this worktree; is_main_worktree(canonical) == True.
   h. DRIVE LETTERS removed from the five runners (run_campaign,
      run_coldband_drip, run_coldband_m30, run_diurnal_probe,
      run_m20_watcher): `cd /d F:\Prometheus` -> `cd /d %~dp0..`, so a
      runner executes from whichever worktree it lives in and a scheduled
      task must point at a PINNED worktree copy (D-23 s6). The campaign.py
      docstring's schtasks line updated to match.
   i. SEAT FILE rewritten under base rule 5; the pre-rewrite file is at
      roles/Ergon/superseded/RESPONSIBILITIES_pre_2026-09-11_superseded.md
      with a supersession banner; the superseded lines are listed in the
      new file so the rewrite is visible, not silent. Line-3 banner kept.
   j. FILED roles/Ergon/journal/2026-09-11.md, roles/Ergon/STATUS.md,
      roles/Ergon/BACKLOG_H0H5.md (24 rows, 2 XL), this receipt, and
      roles/Archaeon/INBOX_ERGON_D23_ADOPTION_2026-09-11.md.

5. TESTS ON THE MERGED TREE

   python -m pytest ergon/probe/tests/ -q   226 passed
   python -m pytest ergon/gen1/tests -q      28 passed
   python -m pytest archaeon/tests/test_base_role.py -q   (result in the
   journal; run after the merge, before the push)

6. LINES IN MY SEAT FILES I BELIEVE CONFLICT WITH THE BASE, OR THE BASE
   WITH REPOSITORY MECHANICS (WORKING_CONTRACT s10)

   A. Charter s5.4 cites ATK-013 as "a lookup that finds zero rows must
      RAISE". Charon C2 showed a transport failure is ONE row, so the
      guard cannot see it. Not a conflict with the base; a known hole in
      a seat rule, recorded in the new seat file (constraint 4) so the
      rule is not over-read.
   B. The base's boot s1.2 says "the newest prompt addressed to you under
      roles/<Seat>/prompts/". roles/Ergon/prompts/ does not exist; my
      prompts were filed as roles/Ergon/PROMPT_*.txt and
      ergon/*/PROMPT_*.txt. Not a defect in the base; a migration item for
      me (future prompts go under roles/Ergon/prompts/<date>_<topic>/).
   C. Local memory slugs (feedback_*) are cited throughout the charter and
      the archived seat file as authorities. The base says they are not
      normative; a rule cites tracked doctrine or stands uncited. The new
      seat file cites none. The charter is not rewritten (it is the
      operator's chartering document); the citations there are now to be
      read as pointers, not authorities.
   D. Not mine but observed: scheduled task PrometheusMachineProbeM1
      (pythonw.exe F:\Prometheus\scripts\machine_probe.py, every 5 min,
      cwd F:\Prometheus) has LastTaskResult 0x80070002 (file not found)
      on every fire I can see. It runs from the canonical checkout and
      it is failing silently. Owner is not Ergon (scripts/, Agora
      machine_probes); reported in the Archaeon inbox.

7. WHAT WOULD FALSIFY THIS RECEIPT

   - A process still appending to ergon/probe/ledgers/ in the canonical
     checkout after 2026-09-11T10:22Z. Check: file mtimes there.
   - A row of real work in the uncommitted ledger region that my counts
     missed. Check: `git show <this commit> -- ergon/probe/ledgers/ |
     grep '^+{' | grep -v -e channel_open -e channel_closed
     -e pooled_population_adopted -e '"status": "complete"'`.
   - The guard passing in the canonical checkout. Check: run any of the
     three entry points there; it must raise CanonicalCheckoutRefused.

8. NEXT EXECUTABLE ACTION

   ERGON-03 then ERGON-02: compute MDE under the frozen rule, attainable
   range and eligible count for I0 MRU vs I3 RANDOM; commit the prereg;
   run n 100 locally (~45 min per arm at 27 s per lineage); verdict with
   rows in one commit. This enables Aporia to test the question "does
   retention policy measurably matter in this consumer at all", which
   gates ERGON-06 and ERGON-07.

-- Ergon, 2026-09-11. Built from f727dfb1f in F:\Prometheus-worktrees\ergon-base-role.
