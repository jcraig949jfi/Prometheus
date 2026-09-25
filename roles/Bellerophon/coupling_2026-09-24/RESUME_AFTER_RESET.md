# RESUME AFTER RESET -- Bellerophon, written 2026-09-25 ~06:45Z before a machine reboot / context reset

Read this first after boot (after the base-role boot sequence). It is the exact state of the one experiment in
flight, the decisions waiting on the operator, and the recommended next steps.

## 1. Where everything is

| item | location |
|---|---|
| worktree | D:/Prometheus-worktrees/bellerophon-post-campaign-forensics (the worktree dir name is historical) |
| branch | bellerophon/coupling-campaign-2026-09-24 (pushed; NOT merged to main) |
| prior closed work | branch bellerophon/post-campaign-forensics-2026-09-23 @ 3efdacf7e (forensics + grounding, complete, NOT merged) |
| campaign directive (verbatim) | roles/Bellerophon/coupling_2026-09-24/prompts/00_OPERATOR_DIRECTIVE_verbatim.md |
| frozen preregistration | roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_PREREG.md (frozen at c9bed96de) |
| implementation audit | roles/Bellerophon/coupling_2026-09-24/COUPLING_IMPLEMENTATION_AUDIT.md |
| failure ledger | roles/Bellerophon/coupling_2026-09-24/COUPLING_FAILURE_LEDGER.md (F1-F3, pre-freeze) |
| analysis script (frozen) | roles/Bellerophon/coupling_2026-09-24/tools/coupling_analysis.py |
| pinned code the campaign runs | C:/Users/James/z80atlas_coupling_2026-09-24/code (COMMIT.txt = c9bed96de; CRLF bytes) |
| campaign workdir (evidence) | C:/Users/James/z80atlas_coupling_2026-09-24 (results.jsonl, STATUS.json, driver.log, coupling_inputs.json) |
| smoke workdir (disposable) | C:/Users/James/z80atlas_coupling_smoke -- not evidence, may be deleted |
| journal | roles/Bellerophon/journal/2026-09-24.md |

## 2. The experiment in flight: COUPLING CAMPAIGN (physics v3) -- STOPPED, NOT FINISHED

- Question: does a minimal coupling (correct output -> copy resource -> paid offspring construction) create
  heritable evolutionary pressure on computation / reproductive machinery?
- Started 2026-09-24T20:07:31Z. Killed at ~21:23Z by Claude Code's low-memory reaper (not a campaign error).
- State: 959 / 11,372 Phase-1 result lines. Lanes A (600/600) and I (90/90) complete; C 269/1,800; E2, F, G, B-cop,
  B-rand, J not started. 0 voids. No result has been inspected scientifically (only counts/voids).
- Memory cause: my 20 workers grew to ~400 MB each, while another Claude session's dev9.py (20 workers) and
  Archaeon's envgate2 / lineage assays (28 workers) shared the 32 GB machine.
- Resume command (re-executes only runs without a result line; deterministic; safe after reboot):
      cd C:/Users/James/z80atlas_coupling_2026-09-24/code
      python -m prometheus.z80atlas.coupling_campaign --workdir C:/Users/James/z80atlas_coupling_2026-09-24 \
             --inputs C:/Users/James/z80atlas_coupling_2026-09-24/coupling_inputs.json --workers N
  Run it detached so it is not a Claude Code background shell (the reaper kills those), e.g. from a normal
  PowerShell window, or start Claude Code with CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1.
- THE CAPS PROBLEM: the frozen stop rule measures caps from the FIRST start (Phase 1 by 2026-09-25T14:07Z, all by
  18:07Z). The idle time since 21:23Z has consumed the window: ~10,400 runs remain at ~840 runs/h on 20 workers
  (~12.4 h). Relaunching under the frozen caps completes roughly A, I, C, E2, F, G, part of B-cop; B-rand and J
  would be NOT_RUN. The driver will also refuse nothing -- it simply stops at the cap and moves to Phase 2/EXT.
- Sanity check before relaunch: `python -m prometheus.z80atlas.coupling_campaign --workdir <that> --status`
  (from the pinned code dir) and confirm results.jsonl still has 959 lines and plan_sha256 a3bc8c8e... in STATUS.json.

## 3. Questions for the operator (blocking the relaunch)

Q1. Relaunch under the FROZEN caps (partial Phase 1, B-rand and J reported NOT_RUN), or authorise a dated
    AMENDMENT to COUPLING_CAMPAIGN_PREREG.md that re-bases the caps on the relaunch time (18 h / 22 h from relaunch)
    because the interruption was external? The amendment changes only the stop rule, no threshold, test or unit.
    My recommendation: the amendment, recorded before relaunch, so every lane runs.
Q2. May Bellerophon have the whole machine for ~14-15 h (no other 20+ worker jobs)? If not: relaunch with
    --workers 12 (roughly +60% wall time).
Q3. Memory mitigation: may I add worker recycling (multiprocessing maxtasksperchild, e.g. 25) to the driver as a
    scheduling-only amendment? It cannot change any result (runs are pure functions of their spec) but it needs a
    new pinned copy and a recorded amendment; the plan hash is unaffected.
Q4. Merge policy: two finished/ongoing branches are pushed but not merged (post-campaign-forensics-2026-09-23,
    coupling-campaign-2026-09-24). Merge the forensics branch now, or hold both until the coupling campaign closes?

## 4. What to do next (in order)

1. Boot per the base role; `python -m comms sync Bellerophon` (EW_DB_HOST=192.168.1.202); read this file.
2. Check for operator answers to Q1-Q4. Do not relaunch without the go-ahead (the harness rule that stopped the
   run said: restart only when asked).
3. On go-ahead: if Q1 = amendment, append a dated "Amendment 1" section to COUPLING_CAMPAIGN_PREREG.md (reason:
   external harness kill at 21:23Z; new caps from relaunch time; nothing else changed), and a matching one-line edit
   of PHASE1_CAP_H/TOTAL_CAP_H handling in the driver ONLY if the operator authorises (the driver reads caps from
   code constants and STATUS first_start_ts -- a re-base needs either a new first_start_ts field or a code change;
   prefer a recorded STATUS field "cap_base_ts" read by a patched driver, committed + pinned anew). If Q3 = yes, add
   maxtasksperchild in the same pinned copy. Commit, push, re-pin, relaunch detached.
4. After the stop: run tools/coupling_analysis.py (--code <pinned> --inputs <pinned inputs> --replay 0.03), then
   write COUPLING_CAMPAIGN_REPORT.md, append post-launch failures to COUPLING_FAILURE_LEDGER.md (F4 = the harness
   kill), publish the causal/origin ledgers, NEXT_MULTIDAY_CAMPAIGN.md only if the frozen readiness rule says
   READY_FOR_MULTIDAY, update STATUS.md, journal, and give the operator the final report in the directive's format.

## 5. What the pre-freeze pilot suggested (EXPLORATORY, off-plan seeds, NOT results)

On 3 pilot seeds per arm: coupling ON kept worlds alive with 138-218 competent organisms of ~255; OFF, YOKED (same
resource supply, no contingency) and RANDOM_REWARD mostly went extinct and never kept competence. If the campaign
confirms this, the effect is "earning", not "more resource". Do not quote these as findings; the campaign decides.

## 6. Longer-term suggestions (after the coupling campaign)

- If READY: a multi-day run targeting reproduction/computation co-adaptation (preservation of task code under
  copying, modular separation, task-funded reproductive machinery), from seeded competent copiers plus a fixed
  fresh-origin lane; keep YOKED and RANDOM_REWARD controls throughout.
- Whatever the verdict: fix worker memory growth (per-run caches; maxtasksperchild) before any long run, and run long
  campaigns outside Claude Code background shells.
