# Seat dossier: Atlas-M2

- Seat: Atlas-M2 (sibling seat on M2 / SPECTREX5; "brother of Atlas", NOT an Atlas instance)
- Crawler label: atlas (Ixion sub-crawler)
- Date: 2026-10-01 (date -u: Thu Oct 1 09:35:45 UTC 2026)
- Base SHA read: bed05507a (origin/main), worktree F:/Prometheus-worktrees/ixion-phase3
- Fully read: roles/Atlas-M2/{STATUS,RESPONSIBILITIES,TODO_2026-09-25}.md, calibration/LEDGER.md, both operator
  prompts (bootstrap + ongoing directive, verbatim files), atlas/harvest/frontier_runs_m2.py header (s1-30).
- Sampled: journal/2026-09-19.md (headings + tick lines), journal/2026-09-25.md (first 50 lines), RESUME.md (via
  STATUS/TODO cross-refs only), reports/REPORT_2026-09-19_M2.txt (not opened beyond ls).
- Live M1 Postgres: harvest_run rows with seat='Atlas-M2'; source visibility FS:M2 counts.
- NOT read / not reachable: M2 itself (host-local runs/, SFE ledger, M2 Postgres) -- this crawler runs on M1;
  everything M2-local is NOT_VERIFIED. BACKLOG_H0H5.md (25 lines) and prompts/*TO_ATLAS* bodies not opened.

---------------------------------------------------------------------------------------------------------

## 1 Charter and role history

- 2026-09-19 operator bootstrap prompt (verbatim): "You're Atlas-M2 a new entity ... You have a brother session called
  Atlas, running on Machine 1 ... Bootstrap yourself as an instance here on M2 ... but recognize that you are not an
  instance of Atlas ... Wait for them." [INTENT] roles/Atlas-M2/prompts/2026-09-19_bootstrap/OPERATOR_PROMPT_verbatim.md.
- Same day ongoing directive: own seat "to minimize collisions in github, comms channels"; loop on comms; "not
  urgent"; "do not interfer with the science. Just gather what the emerging science benches emit" [INTENT]
  prompts/2026-09-19_ongoing_directive/OPERATOR_DIRECTIVE_verbatim.md.
- Seat created 094d0558c (2026-09-19 06:16 -0400) [IMPL]. Identity collision with Atlas's INSTANCES.md (Atlas had
  read the operator as one seat / two instances) stated to Atlas in #499; Atlas replaced INSTANCES.md with
  SIBLINGS.md three minutes later (b8b6f8e59) [IMPL] git log; [HIST] journals.
- 4 loop ticks 2026-09-19 10:57-12:50Z, then PARKED under the operator's instruction relayed in #512 (442867f72) [IMPL]
  commit; [HIST] journal.
- 2026-09-25 pre-reboot save (RESUME.md, TODO_2026-09-25.md; 53e071604); no harvest by decision [IMPL]+[HIST].
- Nothing since 2026-09-25 [IMPL] git log -- roles/Atlas-M2; no harvest_run after 2026-09-19 [IMPL].

## 2 Systems maintained

- No system of its own beyond one harvester module: atlas/harvest/frontier_runs_m2.py (225 lines; first 3d1fa6f91,
  last 2f4db08eb) [IMPL]. It writes into Atlas's schema on M1 through Atlas's db.py/common.py [IMPL] module header.
- Host-M2 rows of atlas/registry.json "local_roots" [INTENT] RESPONSIBILITIES.md s2; [HIST] journal tick 1 "8 host-M2
  local_roots rows".
- Its own seat files under roles/Atlas-M2/ [IMPL].

## 3 Actual implementation paths

- atlas/harvest/frontier_runs_m2.py: reads git-ignored archaeon/frontier/runs/<family>/<spec>/RECEIPT.json (+chunk
  files) on M2; flips EXPECTED:M2 pointers to FS:M2; enriches attempts (started/finished/config_digest/budget) and
  segments on the SAME keys; never mints an attempt key from a receipt time (8 of 42 receipts differ from the RUN-event
  time by one second); /2 handles chunk-only dirs without minting [IMPL] frontier_runs_m2.py:1-30.
- Test: atlas/tests/test_frontier_runs_m2.py (116 lines) [IMPL] wc.
- Shared CLI and local_files collector are Atlas's [IMPL].

## 4 Architecture

M2 benches (SFE at C:\Prometheus-data\sfe, Vivarium consumer, Archaeon frontier runs/ inside another seat's worktree,
logs) -> stat/small reads on M2 -> writes over the LAN to schema atlas on M1 (EW_DB_HOST=192.168.1.202) [INTENT]
RESPONSIBILITIES.md s1. Explicitly NOT the M2 local Postgres ("a quarantined fork and a rehearsal store") [INTENT]
RESPONSIBILITIES.md s1 end. Coordination with Atlas via SIBLINGS.md rules 1-8 (same keys, host-scoped roots, announced
shared-code changes, claimed migration numbers, harvester_hosts, harvest_run.seat, advisory locks) [IMPL] SIBLINGS.md;
db.py:46-53.

## 5 Data stores

None owned. Its contribution in atlas.* on M1: harvest_run rows seat='Atlas-M2': reference 1, local_files 2,
frontier_runs_m2 2, comb 3 = 8 rows, all 2026-09-19 06:58-08:10 (-0400) [IMPL] live query. Sources with visibility
FS:M2 now 244 [IMPL]. Reported effect: FS:M2 0 -> 137, +2,378 facts, 167/167 frontier runs/ pointers FS:M2, 42 attempts
enriched, 107 segments enriched, 0 keys minted [HIST] STATUS.md "index writes".

## 6 APIs/interfaces

`python -m atlas harvest local_files|frontier_runs_m2|reference`, `comb`, `report`, pytest, with ATLAS_SEAT=Atlas-M2
[HIST] RESUME/STATUS; env read at db.py:46-50 [IMPL]. Comms identity Atlas-M2 (could not be addressed from M1 until
roles/Atlas-M2 reached main) [HIST] roles/Atlas/journal/2026-09-19.md.

## 7 Scheduling model

Session wakeup (Claude Code ScheduleWakeup ~30 min), bound 16 non-productive ticks, accountable seat Atlas; "NOT a
scheduled task" [IMPL] roles/base-role/MONITORS.md:87. Ran 4 ticks on 2026-09-19 only [HIST]. No schtasks entry on M1
(this crawl); M2 scheduler not inspected [UNK].

## 8 State machine

Loop: running -> PARKED/DISABLED (operator) [IMPL] MONITORS.md:87. Seat assertions PRESENT / NOT ACTIVE as loop /
PRODUCTIVE through 09-19 / VALID for tests [HIST] STATUS.md. Attempt-pointer states in its harvester: EXPECTED:M2 ->
FS:M2 (present=true) [IMPL] module header.

## 9 Communication channels

comms on M1: #499 (identity), #500/#501 (SIBLINGS acks), #502-#509 tick reports, #512 park, #513, later FYIs
#517/#523/#531/#556 from Atlas [HIST] journals. Outgoing bodies committed under prompts/2026-09-19_ongoing_directive/
TO_ATLAS_*.md and a 2026-09-25 TO_ANANKE monitors-row note [IMPL] ls.

## 10 Failure recovery

RESUME.md (post-reboot entry: state, env vars, five commands, waiting work, written prediction) [HIST] 53e071604.
Risk recorded: the frontier receipts live in ANOTHER seat's git-ignored worktree (archaeon-wse-2026-09-16); if that
worktree is destroyed, the only record outside the index disappears [HIST] journal/2026-09-25.md.

## 11 Persistence

Index rows on M1 (persist); M2 evidence itself is host-local and git-ignored [HIST]. Seat files in git [IMPL].

## 12 Provenance

Every row it wrote carries harvest_run host_id=M2, seat=Atlas-M2, instance m2-8f915f3d [IMPL] live harvest_run.
Identity rule: no attempt key derived from receipt time; identity only via pointers Atlas already linked [IMPL]
frontier_runs_m2.py:15-24.

## 13 Resource usage

Harvest flushes <= 0.4 s each [IMPL] harvest_run durations. No compute lease [INFER].

## 14 Model/inference dependency

Collector code deterministic [IMPL]. Seat operation (ticks, comms, decisions to ingest or not) was session-driven by a
Claude instance [HIST].

## 15 Human dependency

Exists only on the operator's word; parked by operator; resume on operator's word only [INTENT] RESPONSIBILITIES.md s4;
STATUS.md "blockers: none. The loop resumes on the operator's word only."

## 16 Major outputs

frontier_runs_m2.py (+test); 8 harvest passes; REPORT_2026-09-19_M2.txt (235 lines); RESUME/TODO with measured
backlog [IMPL] files.

## 17 Known failures

Calibration ledger: "(none yet; the seat has made no measured call)" [IMPL] calibration/LEDGER.md. No FAILED
harvest_run for seat Atlas-M2 [IMPL]. Structural: Atlas-M2 was unreachable by comms from M1 until its directory was on
main [HIST].

## 18 Pivots

Bootstrap as "instance" (operator text says "Bootstrap yourself as an instance") vs "not an instance of Atlas" in the
same prompt -> resolved as separate seat [IMPL] prompt text; SIBLINGS.md. BOOT_M2.md (Atlas's prompt for an M2 Atlas
instance) treated as "a suggestion whose facts are used, not an instruction" [IMPL] RESPONSIBILITIES.md s3, s5.

## 19 Journals/TODOs/backlogs

journal/2026-09-19.md (298 lines), journal/2026-09-25.md (83); TODO_2026-09-25.md items: (1) ingest 71 new receipts
(runs/ 230 -> 540 files, newest 2026-09-22T19:07:50Z) with a prediction on record that most land unmatched until Atlas
re-harvests git; (2) ask Ensorain/Ares/unknown owner before indexing new M2 run trees and C:/Prometheus-data/evidence
(envgate01, z80atlas_campaign_2026-09-19); (3) adopt Atlas's ATLAS-28/29/30; (4) 5,950 EXPECTED:M2 pointers are
ledger:// records inside the live SFE ledger, "not a gap" [IMPL] TODO_2026-09-25.md.

## 20 Historical relevance to current Prometheus

The only seat that has put M2-local experiment evidence into the shared index; its single pass (09-19) is the M2 truth
the index holds. Since then M2 evidence has grown (129 receipts vs 58 seen) unindexed [HIST]. Shows a working
two-host, one-index pattern (machine-independent keys, host-scoped prune, advisory locks) that was exercised once [IMPL].

## 21 Inference-dependency classification of this seat's functions

| function | class | evidence |
|---|---|---|
| stat/hash of M2 roots (local_files) | INFERENCE_FREE | local_files.py header |
| receipt -> attempt/segment enrichment | INFERENCE_FREE | frontier_runs_m2.py:1-30 |
| deciding new gather targets / de-duplication across worktrees | OCCASIONAL_JUDGMENT | TODO item 2 |
| comms loop, park/resume, coordination with Atlas | MODEL_MEDIATED (session) | MONITORS.md:87; journals |
| registry root curation (which M2 paths, live vs idle, no_hash) | OCCASIONAL_JUDGMENT | journal tick 1; #507 storage_root rule |

## 22 False-negative / false-positive watch

- False negative: frontier runs completed after 2026-09-19 (71 receipts) are absent from attempt enrichment; any
  Atlas query of frontier attempt timings / budgets is truncated at 09-19, not because runs stopped [HIST] STATUS.md;
  [IMPL] harvest_run dates.
- False positive risk low: harvester mints nothing on uncertainty (cheat control in /2) [IMPL] header s/2.
- The 5,950 EXPECTED:M2 ledger:// pointers could be read as "missing M2 evidence"; Atlas-M2 says they are records
  inside the live SFE ledger, deliberately not opened [HIST]; R12 still fires a DATA_GAP signal for 6,101 [IMPL].

## Relation to Atlas

Brother seat, not instance; Atlas owns schema, model, comb, reports; Atlas-M2 owns one M2-only harvester and the M2
registry rows; both write the same rows by key; neither directs the other [IMPL] SIBLINGS.md; RESPONSIBILITIES.md s0-s2.
Whether it "did anything": yes, measurably, on one day (8 harvest_runs, 244 FS:M2 sources today) [IMPL]; nothing after.
