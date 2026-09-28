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
R-08 | disposable worker 8 | ubu002 | 2026-09-28T14:28Z | 2026-09-28T14:36Z | REPORT (written via shell heredoc; Write tool blocked) | see audit line
R-09 | disposable worker 9 | ubu002 | 2026-09-28T14:35Z | | running |
R-09 | disposable worker 9 | ubu002 | 2026-09-28T14:35Z | 2026-09-28T14:47Z | REPORT | see audit line
- 2026-09-28T14:48Z note for scoring (A2.6 sanitizer, cohort-blind): reports can carry package-format cues (e.g. 'the harvest's claim' from a raw package, 'work sketch'/'curator' from a sharpened one); the sanitizer will redact these words as well as ids before scorers see reports.
R-10 | disposable worker 10 | ubu002 | 2026-09-28T14:43Z | | running |
R-07 | disposable worker 7 | ubu002 | 2026-09-28T14:20Z | 2026-09-28T14:54Z | REPORT | see audit line
R-11 | disposable worker 11 | ubu002 | 2026-09-28T14:55Z | | running |
R-11 | disposable worker 11 (used 4 parallel reading sub-agents within its budget -- effort asymmetry recorded) | ubu002 | 2026-09-28T14:55Z | 2026-09-28T15:12Z | REPORT (returned in final reply; Write blocked; saved verbatim) | see audit line
R-12 | disposable worker 12 | ubu002 | 2026-09-28T15:12Z | | running |
R-12 | disposable worker 12 | ubu002 | 2026-09-28T15:12Z | 2026-09-28T15:32Z | REPORT (returned in final reply; saved verbatim) | see audit line
R-10 | disposable worker 10 | ubu002 | 2026-09-28T14:43Z | 2026-09-28T15:40Z | REPORT (returned in final reply; saved verbatim) | see audit line
R-13 | disposable worker 13 | ubu002 | 2026-09-28T15:40Z | | running |
R-14 | disposable worker 14 | ubu002 | 2026-09-28T15:40Z | | running |
- 2026-09-28T15:42Z plan (cohort-blind): 'who should know' notifications from ALL run reports are sent to owning seats in one batch after executions end (identical treatment for every run); this is what lets owner decisions (ED) happen before the day-30 re-check.
R-15 | disposable worker 15 | ubu002 | 2026-09-28T15:43Z | | running |
R-14 | disposable worker 14 | ubu002 | 2026-09-28T15:40Z | 2026-09-28T15:49Z | REPORT | see audit line (used only already-spent sealed universes D/E/F)
R-16 | disposable worker 16 | ubu002 | 2026-09-28T15:50Z | | running |
R-13 | disposable worker 13 | ubu002 | 2026-09-28T15:40Z | 2026-09-28T16:10Z | REPORT | clean (3 phrase hits were Archaeon F_FRONTIER.md in a diffstat, not an Artemis file)
R-17 | disposable worker 17 | ubu002 | 2026-09-28T16:11Z | | running |
R-15 | disposable worker 15 | ubu002 | 2026-09-28T15:43Z | 2026-09-28T16:19Z | REPORT | see audit line
R-18 | disposable worker 18 | ubu002 | 2026-09-28T16:17Z | | running |
R-16 | disposable worker 16 | ubu002 | 2026-09-28T15:50Z | 2026-09-28T16:19Z | REPORT | see audit line
- 2026-09-28T16:20Z blind-lane note: R-16's report concerns memory-retention rules adjacent to the Selective Irreversibility program (SI blind lanes, programs/selective_irreversibility/BLIND_LANES.md). It ran on dev fixtures in a scratch copy (no LM01 campaign rows). Containment: its report lives only on the Artemis selftest branch; the end-of-run owner notifications route SI-adjacent findings only to Ensorain / Aporia / Cyclops, never to blind-lane seats (Bellerophon, Nyx, Techne, Aether). The frozen cohort was not changed.
R-19 | disposable worker 19 | ubu002 | 2026-09-28T16:21Z | | running |
R-17 | disposable worker 17 | ubu002 | 2026-09-28T16:11Z | 2026-09-28T16:33Z | REPORT | see audit line
R-20 | disposable worker 20 | ubu002 | 2026-09-28T16:34Z | | running |
R-20 | disposable worker 20 | ubu002 | 2026-09-28T16:34Z | 2026-09-28T16:39Z | REPORT | see audit line
R-21 | disposable worker 21 | ubu002 | 2026-09-28T16:40Z | | running |
R-19 | disposable worker 19 | ubu002 | 2026-09-28T16:21Z | 2026-09-28T17:03Z | REPORT (SI-adjacent: owner notification routed to stewards only) | see audit line
R-22 | disposable worker 22 | ubu002 | 2026-09-28T17:01Z | | running |
R-18 | disposable worker 18 | ubu002 | 2026-09-28T16:17Z | 2026-09-28T17:02Z | REPORT | see audit line
R-23 | disposable worker 23 | ubu002 | 2026-09-28T17:05Z | | running |
R-21 | disposable worker 21 | ubu002 | 2026-09-28T16:40Z | 2026-09-28T17:30Z | REPORT (compiled Avida 2.2 locally with gcc; ~53 CPU-min) | EXPOSED-NAMES: `git grep -l` output listed roles/Artemis/backlog and challenge file NAMES (incl. a thread file name matching its topic -- a weak cue); no Artemis file was opened (no git show of an Artemis path); its 2 phrase hits come from its own package
R-24 | disposable worker 24 | ubu002 | 2026-09-28T17:29Z | | running |
- 2026-09-28T17:32Z template: from R-25 on workers are told to add ':!roles/Artemis' to repository-wide searches (after R-21's grep -l listed Artemis file names). Procedural; identical for all later runs.
R-23 | disposable worker 23 | ubu002 | 2026-09-28T17:05Z | 2026-09-28T17:36Z | REPORT | see audit line
R-25 | disposable worker 25 | ubu002 | 2026-09-28T17:37Z | | running |
R-24 | disposable worker 24 | ubu002 | 2026-09-28T17:29Z | 2026-09-28T17:40Z | REPORT | see audit line
R-26 | disposable worker 26 | ubu002 | 2026-09-28T17:41Z | | running |
R-25 | disposable worker 25 | ubu002 | 2026-09-28T17:37Z | 2026-09-28T17:51Z | REPORT | see audit line
R-27 | disposable worker 27 | ubu002 | 2026-09-28T17:52Z | | running |
R-22 | disposable worker 22 | ubu002 | 2026-09-28T17:01Z | 2026-09-28T17:53Z | REPORT (CPU ~63 min, slightly over the 1 CPU-h cap -- recorded) | see audit line
R-28 | disposable worker 28 | ubu002 | 2026-09-28T17:54Z | | running |
R-27 | disposable worker 27 | ubu002 | 2026-09-28T17:52Z | 2026-09-28T18:08Z | REPORT (used a blind second-coder sub-agent within budget) | EXPOSED-NAMES: its package mentioned a curator file, and it ran `git ls-tree | grep sfe_retro`, listing roles/Artemis/threads/sfe_retrospective and prompts file NAMES; no Artemis file opened (no git show/cat of an Artemis path); its CVT-R hit is from a Nestor commit message, not an Artemis file
R-29 | disposable worker 29 | ubu002 | 2026-09-28T18:09Z | | running |
R-26 | disposable worker 26 | ubu002 | 2026-09-28T17:41Z | 2026-09-28T18:07Z | REPORT | clean (1 phrase hit is from its own package)
R-30 | disposable worker 30 | ubu002 | 2026-09-28T18:10Z | | running |
R-28 | disposable worker 28 | ubu002 | 2026-09-28T17:54Z | 2026-09-28T18:10Z | REPORT | see audit line
R-31 | disposable worker 31 | ubu002 | 2026-09-28T18:11Z | | running |
R-29 | disposable worker 29 | ubu002 | 2026-09-28T18:09Z | 2026-09-28T18:19Z | REPORT (worker notes it did not read a prior-art note because it lives under a forbidden path -- package reference unavailable by design) | EXPOSED-NAMES: a git log listing showed an Artemis commit SUBJECT (4ea12f6a9 "research frontier pass 1 -- ... 19 sharpened ...") while it located a prior-art path its package cited; no Artemis file opened; a weak cue that some questions were curated
R-32 | disposable worker 32 | ubu002 | 2026-09-28T18:20Z | | running |
R-30 | disposable worker 30 | ubu002 | 2026-09-28T18:10Z | 2026-09-28T18:28Z | REPORT | see audit line
R-33 | disposable worker 33 | ubu002 | 2026-09-28T18:29Z | | running |
R-31 | disposable worker 31 | ubu002 | 2026-09-28T18:11Z | 2026-09-28T18:24Z | REPORT (a harness-persisted oversized tool output landed under ~/.claude/projects; worker states it did not open it) | clean (no command accessed ~/.claude/projects; no forbidden names or phrases)
R-34 | disposable worker 34 | ubu002 | 2026-09-28T18:30Z | | running |
R-32 | disposable worker 32 | ubu002 | 2026-09-28T18:20Z | 2026-09-28T18:40Z | REPORT | see audit line
R-35 | disposable worker 35 | ubu002 | 2026-09-28T18:41Z | | running |
R-34 | disposable worker 34 | ubu002 | 2026-09-28T18:30Z | 2026-09-28T18:43Z | REPORT (worker notes the lens-card prototype was unavailable because it lives under the excluded path) | EXPOSED-NAMES: other seats' files it read (Odysseus frontier notes, Aphrodite CROSS_ENGINE_MECHANISMS) cite roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md by path; no Artemis file opened
R-36 | disposable worker 36 | ubu002 | 2026-09-28T18:44Z | | running |
R-35 | disposable worker 35 | ubu002 | 2026-09-28T18:41Z | 2026-09-28T19:10Z | REPORT | see audit line
R-33 | disposable worker 33 | ubu002 | 2026-09-28T18:29Z | 2026-09-28T19:14Z | REPORT | see audit line
R-36 | disposable worker 36 | ubu002 | 2026-09-28T18:44Z | 2026-09-28T19:36Z | REPORT | see audit line
- 2026-09-28T19:40Z executions COMPLETE: 36/36 reports, 0 UNSCORABLE, 0 NOT_EXECUTED. Lease released (comms #866). No comms volunteer for execution or scoring (0 replies to #814/#815) -> all executors were disposable workers; scoring uses fresh disposable scorers (A2.6 fallback).
- 2026-09-28T19:40Z scoring bundles built (build_scoring.py): 36 reports redacted (127 redactions) and relabelled X###; key sha256 d4e7a38273f26ee2 (key held outside the repo; commit-reveal). Residual-cue scan: only two innocuous uses of "prospective". Known limitation: report length/structure and redaction density may still differ by cohort; not correctable.
- 2026-09-28T19:40Z scorer roles: role 1 = labels in sorted order split 18/18; role 2 = seeded (20260928) shuffle split 18/18; 4 fresh disposable scorer sessions; overlap of role1_a and role2_a = 6 labels.
- 2026-09-28T19:25Z scoring roles 1 and 2 complete: consequential agreement 32/36, primary agreement 28/36; 8 disputed labels (X121 X192 X222 X268 X520 X681 X935 X987) sent to a third fresh scorer (role 3) per A2.6. Artemis has not unsealed the mapping.
