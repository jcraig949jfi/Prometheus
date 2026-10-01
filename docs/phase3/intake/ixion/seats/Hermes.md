# Seat dossier: Hermes

Crawler label: memory (Ixion sub-crawler)
Date: 2026-10-01 (date -u: Thu Oct 1 09:47 UTC 2026)
Base SHA read: bed05507a (origin/main, worktree F:\Prometheus-worktrees\ixion-phase3)
Host: M1 / SKULLPORT. Read-only Postgres queries on agora.intelligence_outputs and comms (counts, stages,
timestamps; recipient addresses redacted in the query, never printed).

Fully read: roles/Hermes/RESPONSIBILITIES.md, STATUS.md, ARCHAEOLOGY_2026-09-11.md,
pivot/hermes_deprecation_2026-05-17.md (first 50 lines), agents/hermes/README.md header,
roles/base-role/MONITORS.md rows 37, 38, 41, 46, 85.
Sampled: agents/hermes/src/hermes.py (docstring, function list, SMTP path), scripts/send_brief_email.py (function
list, main(), send/emit path, Achilles diff a797beabd), scripts/intelligence_loop.py (schedule lines),
scripts/metis_portfolio.py (header, LLM cascade lines), CONVERGENCE_PROBE (first 60 lines), hermes32/RESULT.md
(first 40), incidents/c84e26826cc12217.md (head + occurrence count), calibration/CALIBRATION.md (rows 1-2),
REPORT_M2_UNREGISTERED_LOOPS.md (head), BACKLOG_H0H5.md (rows 01, 04, 16, 25, 26, 32), 2 digests.
NOT read: hermes.py collector bodies, journal/2026-09-11*.md bodies, convergence/*.json data, the 05-19 cleanup
commit diff, agents/hermes/config.json / agents/eos/.env (credential files; prohibited), the M4 host where the
mailer runs (not reachable; every M4 runtime fact below comes from agora rows or git).

## 1 Charter and role history

- 2026-03-23 agents/hermes added as "The Messenger": the last stage of the Pronoia scan chain (Eos -> Aletheia ->
  Skopos -> Metis -> Clymene -> Hermes -> Audit) [IMPL] (eb17886fa; agents/hermes/src/hermes.py:1-15).
- 2026-03-23..04-01 ran; 42 digest files tracked under agents/hermes/digests/ (git ls-files) [IMPL]. [CORR] the
  README annotation and ARCHAEOLOGY say "60 digests" (agents/hermes/README.md:6-7; ARCHAEOLOGY A); git tracks 42
  and no digest deletions appear in git log --diff-filter=D.
- 2026-04-23 pronoia.py (the orchestrator calling Hermes) removed from the tree and gitignored [HIST]
  (MONITORS.md row 46, 3b3c74bc0).
- 2026-05-15..05-23 the replacement reporting layer was built "under Hermes's credentials and namespace":
  scripts/send_brief_email.py (74c4c5834), docs/ dashboard on GitHub Pages (36c0f4be3), 4-hour
  scripts/intelligence_loop.py (ab55ea85e), orchestration_logging.py (edefec3cf), Pythia DR surfacing
  (4556b2ac4, 96ea9322e), "brutal cleanup" incl. stripping Metis chain-of-thought (52b844afa) [IMPL].
- 2026-05-17 deprecation of agents/hermes by Aletheia "after architecture clarification from James": the agent
  was bound to one pipeline on one machine [IMPL doc] (pivot/hermes_deprecation_2026-05-17.md:3-12).
- 2026-06-23/24 two disposition documents proposed DELETE / RETIRE-after-HITL, "needs James confirm", never
  confirmed [HIST] (ARCHAEOLOGY A, citing pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md row 43,
  pivot/PROCESS_TABLE_2026-06-24.md).
- 2026-09-11 operator seated Hermes as a base-role seat on M2 (SPECTREX5): "the last hop to the operator, and the
  accounting of that hop" [IMPL] (da5d6880e; RESPONSIBILITIES.md:1, 27-35). Same day: identity guard
  (88337a141), comms wiring (f7d7c2eac), convergence probe (84cc58224), HERMES-32 (8094151be preregistration,
  283687393 result) [IMPL].
- After 2026-09-11: no Hermes-authored commit (git log -- roles/Hermes shows only merges and other seats'
  incident-occurrence lines on 09-16) [IMPL]. comms.agents: Hermes boot_count 1, last_active and last_sync
  2026-09-11 14:08 -04 [IMPL]. Census state DORMANT (docs/fleet/fleet_state.json, 2026-10-01T04:35Z) [IMPL].

## 2 Systems maintained

1. agents/hermes/src/hermes.py (820 lines): filesystem collector + content-hash dedup + Gmail SMTPS digest
   [IMPL]. Retired; not imported by any code (git grep for hermes imports outside agents/hermes found only a
   docstring example in agents/shared/structured_log.py:8 and a process-name entry in
   scripts/check_intelligence_pipeline.py:56) [IMPL].
2. scripts/send_brief_email.py (682 lines): the live mailer, HERMES_* env namespace, claimed by Hermes 09-11
   pending HERMES-XL-1 (never ruled in the record found) [IMPL code; HIST claim].
3. Seat science, 09-11: store-identity guard (moved to comms/identity.py + comms/environments.json, wired into
   comms/api.connect and later ew/db.py) [IMPL]; failure-convergence probe (roles/Hermes/science/convergence/,
   signature.py, probe.py, tests) [IMPL]; HERMES-32 experiment (science/hermes32/) [IMPL]; incident file
   mechanism (one file per failure signature) [IMPL].
Not Hermes's: scripts/intelligence_loop.py (claimed by Pronoia, MONITORS.md:41), scripts/metis_portfolio.py
(owner-less by ruling, MONITORS row 85), comms (Archaeon) [IMPL doc].

## 3 Actual implementation paths

agents/hermes/{src/hermes.py, README.md, digests/ (42), logs/hermes_2026-03-31.jsonl (12 lines),
logs/hermes_2026-04-01.jsonl (6 lines), docs/SampleEmailsWithDuplicates.txt}; scripts/send_brief_email.py;
scripts/orchestration_logging.py; scripts/intelligence_loop.py; scripts/metis_portfolio.py;
scripts/portfolio_monitor.py; comms/identity.py; comms/environments.json; comms/tests/test_identity.py;
roles/Hermes/science/{convergence/*, hermes32/*}; roles/Hermes/incidents/c84e26826cc12217.md [IMPL].

## 4 Architecture

March agent [IMPL hermes.py:42-55, 134-200, 384-410, 658-700]: read today's files from agents/eos/reports,
agents/aletheia/data, agents/metis/briefs, Clymene; per-section sha256[:16] hash vs data/sent_state.json; send
only if some section changed (a real unchanged-payload check); save digests/YYYY-MM-DD_HHMM_digest.md; SMTP_SSL
smtp.gmail.com:465.
Current pipeline (M4) [IMPL code, scripts/intelligence_loop.py:9-11, 443-545]:
  portfolio_monitor.py --once -> docs/state.json (from agora tables + git)
  metis_portfolio.py -> docs/portfolio_brief.md; an LLM cascade "NVIDIA -> Cerebras -> Groq" exists behind
    METIS_LLM=1, with a deterministic fallback when the output is flagged as scratchpad leak (metis_portfolio.py:6-7, 49-60, 454,
    525-556, 777)
  send_brief_email.py -> multipart Gmail (brief + agora intelligence_outputs + AGENT_REFS/STATIC_REFS catalog +
    since 09-30 the Achilles fleet census block, which is the only part with a staleness guard,
    send_brief_email.py:447-480)
  git auto-commit "auto: portfolio update <ts>" to main -> GitHub Pages.
Every stage emits an event row into agora.intelligence_outputs via orchestration_logging.emit_event, attributed
agent='Pronoia' (send_brief_email.py:653-676) [IMPL].

## 5 Data stores

- agora.intelligence_outputs (columns id, cycle_id, stage, success, output_path, output_summary, error,
  started_at, finished_at, duration_sec, agent, error_class, retryable, run_id) [IMPL]. Stage counts relevant
  to Hermes: email_dispatched 485 success (2026-05-23 .. 2026-10-01 04:15 -04); pronoia_email_dispatched 335
  success + 1 fail; 'hermes' 1 row (2026-05-17, the deprecation marker) [IMPL SQL]. All 821 mailer rows carry
  agent='Pronoia' [IMPL].
- git: docs/portfolio_brief.md and docs/state.json auto-commits, cadence ~6/day from 2026-05-17 to 2026-10-01,
  gaps 05-31..06-09, 09-09..09-10, 09-12..09-17 [IMPL] (git log --grep counted per day).
- agents/hermes/data/sent_state.json (March dedup state) [INFER: path in code; not tracked].
- roles/Hermes/science/*.json result files [IMPL].

## 6 APIs/interfaces

CLI only: hermes.py --once/--collect/--force/--test-email; send_brief_email.py (flags incl. --brief, dry run);
env vars HERMES_GMAIL_ADDRESS, HERMES_GMAIL_APP_PASSWORD, HERMES_RECIPIENT, HERMES_ENABLED
(send_brief_email.py:10-14, 567-576) [IMPL]. Output interface: one email per cycle, a GitHub Pages site, and an
agora event row. Input contract from Achilles: docs/fleet/email_census.json (generated_at_utc, markdown, html)
[IMPL a797beabd].

## 7 Scheduling model

- March: hand-run Pronoia serial scan; no scheduled task ever existed [HIST] (MONITORS row 46).
- Current: intelligence_loop.py is a long-running loop on M4 (hourly monitor + brief, email at cycle end; the
  observed cadence is 4-hourly) [IMPL code + agora rows]. Not on M1 (schtasks query 2026-10-01 found no task
  matching hermes/brief/portfolio/intelligence/pronoia/metis) [IMPL]; not on M2 per Hermes 09-11 [HIST].

## 8 State machine

March: per-section hash state -> send/no-send [IMPL]. Current mailer: none -- HERMES_ENABLED flag, then send,
then success/auth-fail(exit 2)/send-fail(exit 3) event [IMPL send_brief_email.py:567, 661-676]. The proposed
delivery ledger (last_input_at, last_success_at, payload sha256, no-op reason; HERMES-01) does not exist:
roles/Hermes/ops/ is absent from git ls-files [IMPL]. Lifecycle classification vocabulary from base role:
STILL_LIVE / NEEDS_REPREMISE / PARKED / SUPERSEDED / TRANSFERRED / RETIRED (ARCHAEOLOGY B-C) [INTENT].

## 9 Communication channels

To operator: Gmail email (the lane itself) [IMPL]. To seats: comms -- Hermes sent 14 messages (#61..#118, all
2026-09-11); received 8, 5 with no Hermes receipt, newest #1224 (Achilles, 2026-09-30, "Fleet census section
added to scripts/send_brief_email.py") [IMPL SQL]. Prompts packaged as files under roles/Hermes/prompts/ with
MANIFEST [IMPL].

## 10 Failure recovery

None in the mailer beyond exit codes and an event row [IMPL]. Historical silent death: a consumer built ahead of
its producer "shipped a TypeError that killed every send for days" (cce4505ed, 2026-05-23) [HIST]
(ARCHAEOLOGY C9). Producer death 09-09 was found 61 h later only because a seat went looking [HIST]
(MONITORS row 38). The census block added 09-30 is the first loud-staleness path in the mailer [IMPL].

## 11 Persistence

Emails (operator inbox; unreadable by seats), agora event rows (readable from any host with DB access), git
auto-commits (brief/state), 42 March digests in git [IMPL].

## 12 Provenance

March digest hashed sections [IMPL]. Current mailer records subject, body length, duration, census tag in
output_summary; no payload hash, no input timestamp, no producer identity beyond agent='Pronoia' [IMPL
send_brief_email.py:649-660]. Example row 2026-10-01 08:15Z: "body=27766/36899 md/html chars | 2.3s |
census=2026-10-01T04:35:00Z rows=59 age_h=3.7" [IMPL SQL, recipient redacted].

## 13 Resource usage

~1.5-2.3 s per send (agora duration rows) [IMPL]. Brief generation runs ~6/day; the free-tier LLM cascade is
only reached with METIS_LLM=1 (see CORR in s14).

## 14 Model/inference dependency

- March hermes.py: inference-free (collection + hashing + SMTP) [IMPL].
- Current brief content: INFERENCE_FREE by code default (deterministic brief); LLM cascade only with METIS_LLM=1.
  [CORR -- Ixion verification 2026-10-01] The cascade is NOT the default: metis_portfolio.py:452-460 returns _deterministic_brief() unless env METIS_LLM=1 (since af9b4d9c9, 2026-08-18), and the brief committed at e9cf5ee16 (2026-10-01T08:14Z) carries 'Deterministic brief (primary mode) -- no LLM in the loop'. Whether M4 sets METIS_LLM=1 is [UNK] but the committed output says it does not. The mailer itself is inference-free [IMPL].
- The 09-11 seat work (archaeology, guard, probe) was done by a Claude Opus 5 session (comms boot model
  claude-opus-5[1m], STATUS.md) [HIST].

## 15 Human dependency

The operator is the sole consumer ("reads on a phone and relays by hand", RESPONSIBILITIES.md:29-31) [INTENT].
Three XL decisions (mailer ownership, producer ownership, host) await the operator; no ruling found in
roles/Hermes or MONITORS [IMPL absence, searched roles/Hermes + MONITORS.md].

## 16 Major outputs

- 42 March digests (agents/hermes/digests/) [IMPL].
- ~820 dispatched emails May-Oct (agora rows) [IMPL].
- comms/identity.py store-identity guard, now used by comms and ew/db.py (identity before structural check)
  [IMPL] (05_MOVED_2026-09-11.md; ew/db.py:39-55).
- Incident-per-signature file c84e26826cc12217 with 14 dated occurrence lines from multiple seats [IMPL grep].
- Convergence probe: 2 of 5 historical failure cases converge deterministically under a sha256 signature over
  only what the observer had at failure time; 2 RELATED-NOT-SAME, 1 UNSIGNABLE [REPORTED]
  (CONVERGENCE_PROBE_2026-09-11.md:20-33).
- HERMES-32: one silent class converted UNSIGNABLE -> EXACT with ablation; ruling "BOUND MORE NARROWLY" -- works
  only when the exposed fact is at the same scope as the rule [REPORTED] (hermes32/RESULT.md:12-30).
- REPORT_M2_UNREGISTERED_LOOPS: base-role self-test found 3 enabled M2 tasks with no MONITORS row [IMPL doc].
- ARCHAEOLOGY + CALIBRATION ledger of the seat's own wrong calls [IMPL doc].

## 17 Known failures

- 2026-05-23 TypeError silent send death [HIST] (cce4505ed).
- Producer (brief) dead 09-09..09-10 [IMPL: no auto-commit, no email rows those days].
- The "Agora is not fed" assertion, corrected the same day by Pronoia #91 (agora.intelligence_outputs 15,503
  rows, live) [CORR] (ARCHAEOLOGY B.2 bracket; b026db8cc).
- [CORR, new in this crawl] MONITORS row 37 (Hermes, 09-11) states the mailer's record is "NONE. The email
  itself is the only record". At that time agora.intelligence_outputs held 369 email_dispatched rows (last
  2026-08-20 03:45 -04) plus daily pronoia_email_dispatched rows 2026-09-01..09-08 (6/day), written by the
  mailer itself via emit_event since edefec3cf (2026-05-23), readable from M2 [IMPL SQL]. The freshness record
  existed; it was attributed to Pronoia and was not looked for.
- [CORR] MONITORS row 38 still reads "DORMANT since 2026-09-09" for the brief producer; auto-commits resumed
  2026-09-18 and ran 6/day through 2026-10-01 (e9cf5ee16) [IMPL].
- STATUS.md "60 digests" vs 42 tracked [CORR].
- Disposition proposals to delete the seat never ruled [HIST].
- Brief LLM cascade "repeatedly leaked scratchpad (2026-08-17/18 emails)" [HIST] (metis_portfolio.py:454).
- metis_portfolio infra alarm reads a key state.json stopped emitting 2026-09-01, so the degraded branch cannot
  fire [HIST] (MONITORS row 85).

## 18 Pivots

Digest agent (Mar) -> deprecated, function moved to pipeline-agnostic mailer under the same namespace (May) ->
proposed retirement (Jun) -> re-seated as an accountability instrument for the last hop (Sep 11) -> one day of
substrate-identity and failure-convergence science -> dormant seat; mailer keeps running under Pronoia
attribution and gains an Achilles census block (Sep 30) [IMPL/HIST].

## 19 Journals/TODOs/backlogs

BACKLOG_H0H5.md: 44 HERMES rows, last edited 283687393 (09-11); HERMES-01 (delivery ledger), HERMES-04 (three
controls incl. timestamp-only cheat), HERMES-16 (dormancy alarm) unbuilt; HERMES-26 CLOSED; HERMES-25
SUPERSEDED (duplicate) [IMPL]. Journals: journal/2026-09-11.md, 2026-09-11b.md [IMPL].

## 20 Historical relevance to current Prometheus

- The mailer is the only running program-to-operator channel and is now the carrier for the Achilles census
  [IMPL a797beabd; agora rows with census= tag, 2 so far].
- comms/identity.py (Hermes origin) is in the connect path of comms, atlas, fabric and PEW [IMPL].
- The incident-signature mechanism is a working deterministic dedup design that needs no judge [REPORTED +
  IMPL code].

## 21 Inference-dependency classification

| function | class | evidence |
|---|---|---|
| Email transport + event row | INFERENCE_FREE | send_brief_email.py:643-676 |
| Unchanged-payload suppression (March) | INFERENCE_FREE | hermes.py:134-200 |
| Census staleness flag in email | INFERENCE_FREE | send_brief_email.py:447-480 |
| State snapshot (portfolio_monitor) | INFERENCE_FREE | intelligence_loop.py:443 |
| Brief prose (metis_portfolio) | MODEL_MEDIATED (fallback is deterministic) | metis_portfolio.py:6-7, 525-556 |
| "Smart" reference routing by name grep | ASSISTED_PLAUSIBLY_DETERMINISTIC (rotted) | send_brief_email.py:57-110; ARCHAEOLOGY C8 |
| Failure signature + incident convergence | INFERENCE_FREE | roles/Hermes/science/convergence/signature.py |
| Store identity guard | INFERENCE_FREE | comms/identity.py |
| Archaeology / classification of old queues | OCCASIONAL_JUDGMENT | ARCHAEOLOGY_2026-09-11.md |

## 22 False-negative / false-positive watch

False negatives:
- hermes.py was deprecated for being single-host, yet it had the one property the successor lacks: hash-based
  suppression of unchanged payloads (hermes.py:134-200). The successor dropped dedup and Hermes re-proposed it
  as HERMES-01/04, unbuilt [IMPL]. The idea died of a deployment-scope defect, not a design defect [INFER].
- Convergence probe's 3 non-converging cases are classed by mechanism (RELATED-NOT-SAME, UNSIGNABLE), and
  HERMES-32 showed one UNSIGNABLE class becomes EXACT once instrumented at the right scope -- "signature coverage
  is downstream of instrument coverage" was tested on one specimen only [REPORTED].
False positives:
- MONITORS labels: row 37 "ACTIVE-UNVERIFIED ... no record" and row 38 "DORMANT" are both wrong today; the
  registry is not refreshed by any automated reader [IMPL].
- email_dispatched success=True means SMTP accepted; it does not mean the payload was new or fresh (no hash, no
  input age) [IMPL].
