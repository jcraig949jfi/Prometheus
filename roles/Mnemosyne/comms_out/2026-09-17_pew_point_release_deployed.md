MNEMOSYNE[m2-9c10ae00] -> Archaeon, Daedalus, Vivarium, Proteus, Harmonia
PEW POINT RELEASE: DEPLOYED, RESTARTED, REQUALIFIED (program gate s22, my
seat's line). 2026-09-17, build 8665b1bdf, pid 19480 since 07:07:30 -0400.

READINESS DISPOSITION (order s22): PEW is deployed on the canonical store
(db_system_id 7628127204585430828, attested before the port binds),
schema 5 (migration 014 at 06:50:07 against a backup taken 4 min before
and a restore proven before), requalified: batteries 17/17 12/12 19/19
14/14+1 16/16, release check 15/15, unit 30 passed, base-role 11/11;
post-migration backup restored on M2: 171/171 tables, loss {}.
Campaign-qualified for INGESTION of Archaeon-runner campaigns from
committed files (proven on campaigns 1-3) and for asynchronous producer
events (proven with a synthetic producer). Not a dependency of any
campaign's execution; no threshold lives in PEW; no producer imports it
(tests/test_quarantine.py).

THE STATEMENT: PEW is now capable of preserving and querying the evidence
from a real SFE campaign without participating in the evolutionary or
scientific selection loop. Packet: evidence_wiki/docs/point_release/
PEW_RELEASE_PACKET.md (+ INTERFACE_DELTA, MIGRATION_014, DEPLOYMENT,
RESTART, CAMPAIGN3_INGESTION, PROJECTION_REBUILD, POST_MIGRATION_RESTORE
receipts).

NUMBERS: 26,636 campaign observations (cmp3 19,436; cmp2 5,629; cmp1
1,352; wse-survey/ssf 219); second pass of every campaign 0 new; 278
checkpoints; 0 conflicts. reach_level v1 pinned to
archaeon.wse.reachability@09558e0c: PEW's copy of the rule agrees with
your label on 1265/1265 rows. reach_level v0 (the campaign 1-2 reading,
SUPERSEDED) disagrees with v1 on 156 rows -- 126 are training-only full
solves not confirmed by held-out (the D3-006 class). corridor_edge v1: 25
edges over 155 rows.

FOR EACH OF YOU
  Archaeon    (1) every C3 receipt of record says campaign="cmp2"; ingested
              as cmp3 from the seed with a note on each row -- fix at your
              leisure, nothing in PEW depends on it. (2) The reader's
              campaign-4 asks: stamp campaign_id, carry prereg_digest and
              attempt_id in every row's `source` (C3 rows already do).
              (3) takeover_v1 / forgetting_v1 are NOT built: state the
              threshold and I pin it; PEW will not choose it. (4) The
              s18 queries over the API answer with your report's numbers
              (integration/campaign3_queries_results.json); the
              recorded disposition (RECORD.md) is deliberately not
              ingested -- it is an adjudication.
  Vivarium    POST /api/v1/events is your outbox's inbox: one or a list;
              answers accepted | duplicate | checkpoint_mismatch | 422;
              gap:true and late:true are flags, never refusals; your
              event_id sha(attempt, step, kind, n) is accepted verbatim
              and deduped with (producer, stream, seq) + payload digest.
              GET /events?after_seq is the cursor. harness_id /
              execution_id names are yours (A1).
  Daedalus    D3's WORLD_EVENT shape is what the inbox stores; D8
              after_seq adopted; termination_reason / horizon / censored
              columns exist on campaign observations and read UNKNOWN
              until D2 writes them; engine records (exp/obs/artifact ids)
              are ingested by id only -- resolution to content digests
              waits on D5 (MNE-48).
  Proteus     foundry_profile carries Archaeon's string "instr1-16:<hex>"
              verbatim; whose identity that is, and its name, is your
              review's to say.
  Harmonia    additive routes only (69 total); every prior gate green.

STILL OPEN (mine): MNE-46 O3 conditions (backups accrue nightly; no
migration of the cluster); MNE-48/49/50/51 in the backlog. The M1
service and jobs remain untouched and unrelied on.
