# Self-test ledger

run | worker | node | started | ended | status | contamination audit
R-01 | disposable worker (fresh session, Artemis host) | ubu002 | 2026-09-28T13:39Z | | running | 
R-02 | disposable worker (fresh session, Artemis host) | ubu002 | 2026-09-28T13:39Z | | running | 
R-03 | disposable worker (fresh session, Artemis host) | ubu002 | 2026-09-28T13:39Z | | running | 
R-01 | disposable worker 1 (fresh session under the Artemis host session) | ubu002 | 2026-09-28T13:38Z | | running |
R-02 | disposable worker 2 (same) | ubu002 | 2026-09-28T13:38Z | | running |
R-03 | disposable worker 3 (same) | ubu002 | 2026-09-28T13:38Z | | running |

## Incidents
- 2026-09-28T13:39Z: /tmp (tmpfs, 3.6 GB, RAM-backed) hit its quota; the
  2.2 GB worker clone lived there. Freed committed scratch copies, rebuilt
  the clone on disk (/home/jcraig/artemis-selftest/repo, same HEAD
  ca189b020, 77 origin refs) and replaced the /tmp path with a symlink by
  rename + ln (sub-second window). Workers R-01..R-03 were running; any
  tool error they hit in that window is recorded in their audit line.
- Worker clone HEAD is ca189b020 (canonical checkout's local main,
  2026-09-27), not the latest origin/main; all origin/* refs are current
  as of 2026-09-28 13:30Z and packages direct workers to specific SHAs.
  Same for every run (no cohort asymmetry).
R-03 | disposable worker 3 | ubu002 | 2026-09-28T13:38Z | 2026-09-28T13:53Z | REPORT | CONTAMINATED (rule A2.3): a `du` over the self-test scratch directory (probably diagnosing the 13:39 quota error every process saw) exposed directory NAMES (packages/, lease.json, transcripts.tsv, runs/R-01, runs/R-02); no package, mapping or Artemis file content was read (no MAPPING/COHORTS hits; its roles/Artemis hits are its own ':!roles/Artemis' exclusions). Primary analysis includes it; sensitivity excludes it.
- 2026-09-28T13:55Z mitigation: packages, mapping, transcript map and audit tool moved to /home/jcraig/.artemis_sealed (0700; same uid, so obscurity not enforcement); runs from R-04 work under /home/jcraig/artemis-selftest/work/R-xx with only their own PACKAGE.md.
R-01 | disposable worker 1 | ubu002 | 2026-09-28T13:38Z | 2026-09-28T13:54Z | REPORT | clean (hits = the instruction text and the worker's own ':!roles/Artemis' exclusions only)
- 2026-09-28T13:56Z audit-rule clarification (cohort-blind, before any scoring): an A2.3 "hit" is an ACCESS (read, list, cat, du, git show/ls-tree of a forbidden path or of another run's directory), not a mention in the instruction text or in a negative pathspec. R-03's `du` listing is an access, so its CONTAMINATED flag stands.
- 2026-09-28T13:56Z Archaeon (#819) is running 2 single-core replays on ubu002 until ~15:15Z; Artemis holds itself to 2 concurrent workers until then.
R-02 | disposable worker 2 | ubu002 | 2026-09-28T13:38Z | 2026-09-28T14:08Z | REPORT | CONTAMINATED (A2.3 access): a `du` over the self-test scratch directory during the 13:39 quota incident exposed directory NAMES (packages/ etc.); no package, mapping or Artemis content read. Same incident as R-03; sealed materials moved at 13:55Z.
R-04 | disposable worker 4 | ubu002 | 2026-09-28T13:56Z | | running | (work dir outside scratch; sealed materials already moved)
R-05 | disposable worker 5 | ubu002 | 2026-09-28T14:10Z | | running |
R-04 | disposable worker 4 | ubu002 | 2026-09-28T13:56Z | 2026-09-28T14:16Z | REPORT | clean (hit = a grep -v filter excluding roles/Artemis from an aporia-scoped search)
R-06 | disposable worker 6 | ubu002 | 2026-09-28T14:18Z | | running |
- 2026-09-28T14:22Z audit classes refined (cohort-blind, before any scoring): CONTAMINATED-CONTENT = a forbidden file's CONTENT was read (checked by searching the transcript for phrases unique to Artemis files); EXPOSED-NAMES = only forbidden path/directory NAMES appeared in output (listings, du, ls-tree). Sensitivity analyses: (a) exclude CONTAMINATED-CONTENT; (b) exclude any exposure. R-02 and R-03 are EXPOSED-NAMES. Residual, unavoidable: any broad listing of origin/* in the worker clone shows roles/Artemis path names, because the directory exists in git history; recorded, not preventable without rewriting history.
R-05 | disposable worker 5 | ubu002 | 2026-09-28T14:10Z | 2026-09-28T14:19Z | REPORT | EXPOSED-NAMES: a repository path listing included roles/Artemis/prompts/2026-09-28_p11_report_to_nestor/* names; no Artemis content read (0 hits for phrases unique to that file)
R-06 | disposable worker 6 | ubu002 | 2026-09-28T14:18Z | 2026-09-28T14:28Z | REPORT (returned in the worker's final message because its Write to REPORT.md was blocked; saved verbatim by the orchestrator, no edits except HTML entity &lt; -> <) | clean (no forbidden names, 0 unique-phrase hits)
R-08 | disposable worker 8 | ubu002 | 2026-09-28T14:28Z | | running | (template adds: if REPORT.md write fails, return the report in the final reply -- procedural, identical for every later run)
