# Seat dossier: Cyclops

Crawler label: coord (Ixion Phase 3 sub-crawler; seats Aporia, Cyclops, Agora)
Date: 2026-10-01 (date -u at start: Thu Oct 1 09:36:13 UTC 2026)
Base SHA read: bed05507a

Fully read: roles/Cyclops/RESPONSIBILITIES.md, STATUS.md (all three eras), WORK_STATE.json, WAKE.md (head),
audits/2026-09-30_observability.md, calibration/LEDGER.md (head), prompts/2026-09-25_creation verbatim,
prompts/2026-09-25_selective_irreversibility verbatim (first 3 KB of 19,552 bytes), git log of
roles/Cyclops (31 commits, all subjects with timestamps), ops/work_orders/PUBLICATIONS.md, MWO-0001 s1-s2.
Sampled: programs/selective_irreversibility/ (README, RULINGS, prepost_check.py head).
NOT read: journal/2026-09-25.md and 2026-09-30.md bodies, TODO.md, BACKLOG_H0H5.md, the 23 prompt
directories other than creation/charter, audits/2026-09-30_observability_probe.py body, SI memo M2 sections.
Comms: read-only SELECTs on schema comms.

## 1 Charter and role history

    2026-09-25 15:24Z  created on M2 (SPECTREX5) by one-line operator prompt; base role adopted,
                       "charter PENDING"                                            [IMPL] f4202098d; prompts/2026-09-25_creation
    2026-09-25 16:25Z  charter = Selective Irreversibility Stewardship Directive (to Aporia AND
                       Cyclops, peers, "Neither is subordinate"); Cyclops received it first,
                       so the shared directive lives under roles/Cyclops/prompts/        [IMPL] 608b672d5, sha256 f0dd0599...
    2026-09-25..26     steward loop, 20-30 min self-paced ticks; 28 commits 11:24-02:26 -04 [IMPL] git log roles/Cyclops
    2026-09-26 06:26Z  PARKED by operator ("Consider yourself parked for now"); loop stopped [IMPL] 8083cdc1b; STATUS.md 3rd narrative
    2026-09-28 21:48-04 unparked as MWO-0001 REGISTRAR: sole custodian of ops/work_orders/;
                       published MWO-0001                                             [IMPL] 7e4c09f2c, bd48fac9b; MWO-0001 s2
    2026-09-29         custody moved to Aporia by explicit operator ruling for MWO-0002+ [IMPL] mwo0002_revision s1
    2026-09-30 10:27Z  adopted MWO-0004 + CWO; ran one bounded observability audit; PARKED again
                       ("not a fleet coordinator; not a steward ... Do not recreate the previous
                       coordination layer")                                            [IMPL] 4c361044d, 029dd5555, WORK_STATE.json role_note

Cyclops is therefore a 6-day-old seat that has held three coordination roles (peer steward, registrar,
auditor) and has been PARKED twice [IMPL].

## 2 Systems maintained

- programs/selective_irreversibility/ M2 rows (EXPERIMENTS, RESOURCE_CONFLICTS, PORTFOLIO_MAP,
  BLIND_LANES, DEPENDENCIES, ANOMALIES) and memo M2 sections [IMPL] RESPONSIBILITIES.md s2; 23 commits
  with "Cyclops[" prefix touch the SI dir [IMPL; git log --format=%s -- programs/selective_irreversibility].
- DO_NOT_BRIEF.txt + probes/prepost_check.py (6 controls incl. the real #585 body) [IMPL] add51a9a4.
- blind_probe_v1.py with raw outputs from M2 and M3 [IMPL] programs/selective_irreversibility/probes/.
- ops/work_orders/CURRENT.md + archive + PUBLICATIONS.md for MWO-0001 only [IMPL].
- roles/Cyclops/audits/2026-09-30_observability_probe.py [IMPL] 029dd5555.

## 3 Actual implementation paths

All steward work is session prose + comms posts + git commits. Executable pieces: prepost_check.py
(refusal predicate), blind_probe_v1.py (registry probe), observability_probe.py (git + comms-who text
parse; "the lease and process checks were run by hand") [IMPL] audits/2026-09-30_observability.md header.

## 4 Architecture

Peer-steward pair over comms with one shared append-only record; entries under "### <UTC> Seat[tag]"
headers; disagreements to DISAGREEMENTS.md; only cost/contamination/interpretation decisions to the
operator (directive s14) [IMPL] programs/selective_irreversibility/README.md; RESPONSIBILITIES.md s1.
Cyclops "never" launches/stops/amends another seat's experiment; it "asks the owner" [INTENT] s3.

## 5 Data stores

Git (roles/Cyclops, programs/selective_irreversibility, ops/work_orders). comms rows: 35 sent, 123
received [IMPL; comms query]. No database of its own.

## 6 APIs/interfaces

prepost_check.py CLI (exit 0 clear, 2 REFUSED) [IMPL]. WORK_STATE.json (prometheus.work_state.v1)
[IMPL]. WAKE.md paste block for boot [IMPL].

## 7 Scheduling model

loop-in-session: "self-paced loop at intervals of 20-30 minutes ... at or under the 60-90 minute
heartbeat cadence the engine seats use" [INTENT] RESPONSIBILITIES.md s4. Measured: 28 commits between
2026-09-25 11:24 and 2026-09-26 02:26 (-04:00), i.e. one per ~32 min [IMPL; git log timestamps].
"The steward loop is a session loop, not a registered monitor" [IMPL] STATUS.md steward-era narrative.

## 8 State machine

Seat: ACTIVE (steward) -> PARKED -> REGISTRAR/HOLD -> PARKED [IMPL] STATUS.md narratives. Tick protocol:
comms sync -> act on steward traffic -> one concrete step -> journal -> commit/push/verify -> sync;
a tick that advances nothing "is recorded as a no-op" [INTENT] RESPONSIBILITIES.md s4. Whether no-op
ticks were recorded was NOT verified (journal not read) [UNK].

## 9 Communication channels

comms (M1 Postgres; M2 sets EW_DB_HOST to M1) [IMPL] WAKE.md. Sent by day: 09-25 19 (5 rulings,
3 prompts, 2 delegations, 8 reports, 1 question), 09-26 13 (9 rulings, 4 reports), 09-29 1 broadcast
(#914), 09-30 2 reports [IMPL; comms query]. Received 116 messages on 09-25/26 [IMPL]. Prompts to
other seats committed under roles/Cyclops/prompts/<date>_<topic>/01_TO_<SEAT>.md + MANIFEST [IMPL]
(25 prompt directories 09-25..09-26, incl. creation and charter).

## 10 Failure recovery

PARK is the operator's recovery tool. WORK_STATE repair on reboot (MWO-0001/HOLD -> MWO-0004) [IMPL]
4c361044d. No watchdog.

## 11 Persistence

Git + comms. Steward-era narratives retained below the current STATUS ("kept per base role s2") [IMPL].

## 12 Provenance

Verbatim + MANIFEST discipline for every inbound and outbound prompt [IMPL]. Observability audit states
its evidence window, reference SHAs, and splits "reported" vs "actual" per finding [IMPL] audit header.

## 13 Resource usage

"no compute, GPU or spend held; read-only audit" [IMPL] WORK_STATE.json. Steward era: ENVGATE-02 and
coupling campaigns on M2 were other seats' runs it gated/observed [HIST] STATUS.md steward narrative.

## 14 Model/inference dependency

Steward rulings, concurrences, memo drafting: MODEL_MEDIATED. Registrar publication: deterministic
protocol executed by a model session. Observability audit: mostly deterministic checks executed by hand
[IMPL] audit text.

## 15 Human dependency

Created, chartered, parked, unparked and re-parked by operator chat [IMPL]. Directive s14 routes cost/
contamination/interpretation decisions to operator; Q1-Q5 operator questions were outstanding at park
time [IMPL] STATUS.md steward narrative; RULINGS.md 13:05Z handover list.

## 16 Major outputs

- SI joint portfolio memo co-signed (d50103524) [IMPL].
- WTP-LM01 design concurrences (D1-D7, P1-P4, strata, R-c) [HIST] commit subjects 5552e55d0..07111827d.
- Blind-lane registry probe + DO_NOT_BRIEF + pre-post check [IMPL].
- MWO-0001 publication [IMPL] 7e4c09f2c; note: archive path was gitignored by a blanket "archive/" rule,
  fixed in the same commit [IMPL] PUBLICATIONS.md note.
- Observability audit F1-F7 [IMPL] audits/2026-09-30_observability.md.

## 17 Known failures

- INCIDENT #585: Cyclops addressed Archaeon AND Bellerophon citing the directive path and calling
  Bellerophon's lane "theory-blind" -- "exposed the fleet's only blind seat to the program by name"
  [IMPL] calibration/LEDGER.md row 3; 3de747dd8. The DO_NOT_BRIEF/prepost machinery was built in response
  [IMPL] add51a9a4.
- #616 body pointed at the wrong file (duplicated #615) [IMPL] LEDGER.md row 2.
- #627 "direct readout of ... selectivity" -- a relevance-blind merge also produces the gap [IMPL] LEDGER.md row 4; [CORR] c981be1dd.
- Memo R1.3 FIFO control wrongly called relevance-blind [IMPL] LEDGER.md row 1.
- Own WORK_STATE updated_at in the future (corrected) [IMPL] audit F3.

## 18 Pivots

Steward -> parked (operator, ~14 h after charter) -> registrar (MWO-0001, ~2.6 days later) -> custody
removed next day (MWO-0002 rev.) -> auditor + parked (CWO 09-30) [IMPL]. MWO-0001 had made Cyclops
"the registrar and distributor ... not a strategic steward, science adjudicator, scheduler" and "Only
Cyclops writes the canonical ops/work_orders/ files unless a later MWO explicitly changes custody"
[IMPL] MWO-0001:25-27,58; custody was changed ~5 h after publication [IMPL] 7e4c09f2c 21:48 -04 -> 89512068f 02:56 -04.

## 19 Journals/TODOs/backlogs

journal/2026-09-25.md, 2026-09-30.md; TODO.md; BACKLOG_H0H5.md; calibration/LEDGER.md; superseded/
pre-charter RESPONSIBILITIES [IMPL] listing.

## 20 Historical relevance to current Prometheus

Cyclops is PARKED and routable "for a bounded task from Aporia" [IMPL] WORK_STATE.json. Its two durable
contributions to fleet machinery are the blind-lane pre-post refusal pattern and the observability
audit's five proposed predicates (FUTURE_UPDATE, RUNNING_UNDECLARED, PRESENCE_VS_COMMIT, roster-based
enumeration, lease cross-check) [IMPL] audit "Suggested BUILDER-OBSERVABILITY checks". None of the five
is implemented in ops/fleet/fleet_status.py at bed05507a (flags are only STALE_MWO, STALE_UPDATE,
NO_QUEUE, IDLE_HOLD, IDLE_WORKERS; file last changed 6a7a84569, before the audit) [IMPL] fleet_status.py:6-10.

## 21 Inference-dependency classification

    function                                  | class                            | evidence
    steward rulings / concurrences            | MODEL_MEDIATED                   | 14 ruling-kind msgs 09-25/26
    blind-lane exposure guard                 | INFERENCE_FREE                   | prepost_check.py
    blind-lane exposure measurement           | ASSISTED_PLAUSIBLY_DETERMINISTIC | blind_probe_v1.py + raw outputs
    MWO registrar publication                 | ASSISTED_PLAUSIBLY_DETERMINISTIC | MWO-0001 s2 steps 1-7
    observability audit (state vs reality)    | ASSISTED_PLAUSIBLY_DETERMINISTIC | F1-F5 each reduce to a join of git/comms/fabric/process data
    resource-conflict arbitration (M2-1/M2-2) | OCCASIONAL_JUDGMENT              | 373b99bb6, 5f9aa3a0f

## 22 False-negative / false-positive watch

- FN: the peer-steward experiment was parked after ~15 h and frozen fleet-wide after ~21.5 h. Its record
  contains real instrument catches (#627 readout defect found by fixture; FIFO control; the blind-lane
  exposure became an executable guard). The freeze ruling gives no reason beyond "I will be providing
  direction" [IMPL] steward_freeze verbatim. Whether stewardship failed on value, on cost (operator relay
  load), or on latency is not recorded [UNK].
- FP watch: STATUS steward narrative "PRODUCTIVE (steward record, rulings, routed requests)" is a
  self-assessment by activity count [IMPL] STATUS.md; the base role itself warns activity is not
  productivity (rule 8, 58fe2fc57).
