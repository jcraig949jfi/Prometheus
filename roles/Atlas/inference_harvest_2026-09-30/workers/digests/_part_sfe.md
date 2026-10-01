# Part: Serendipity Foundry Engine (SFE)

Tags: RAN = executed with a receipt. OBSERVED = measured value. CONCLUDED = a seat's interpretation (quoted, author named). ATLAS_DERIVED = my synthesis, not in the record.
All paths are relative to F:/Prometheus-worktrees/atlas-base-role (origin/main 2026-09-30). `@sha` = `git log -1 --format=%h -- <path>`.

## Coverage
- Read: `git log -- SerendipityFoundry` (116 commits, top 60 scanned); engine STATUS, GEN2 architecture, deploy pins; `integration/SFE_CLIENT_GUIDE.md`; Archaeon CMP1/2/3 packets, Campaign 4/5 reports, C4/C6 DECISIONS, H0H5_STATUS, ENGINE_LANDSCAPE; Artemis `roles/Artemis/threads/sfe_retrospective/REPORT.md` + `notes/A_chronology.md` s7; comms grep (71 hits, most are the word "transfer", not SFE).
- NOT read: the D6/D7/D8/D10 series (all dated 2026-09-01, the pre-gen2 D-experiments), selection_boundary, stackvm_admission, wow, worldfoundry; the SFE ledgers themselves (off-repo; per Artemis REPORT.md:92-93). Receipt JSONs were not opened, so no receipt-internal number was re-derived.

## What SFE is
- A hash-chained, multi-tenant experiment LEDGER, not a simulator. One SQLite DB (WAL, FK, CHECK enums) plus content-addressed blobs. FastAPI `/v2` over HTTPS with a bearer token per client. The `Foundry` runtime writes each state change and its event in one transaction. `executors.py` holds the executor contract and a worker loop (claim -> heartbeat -> execute -> commit). Object model: CLIENT > SESSION > WORLD > {events, work_items, hypotheses, predictions, experiments, observations, failures, artifacts, lineage, budget, checkpoints} (`SerendipityFoundry/SerendipityFoundryEngine/docs/SERENDIPITY_FOUNDRY_GEN2_ARCHITECTURE.md` "Layers", "Object model" @d332658cf).
- Status at birth: 30/30 tests; REPLAY and RESOURCE ACCOUNTING PARTIAL; "Single machine only (SQLite by design)" (`SerendipityFoundryEngine/SERENDIPITY_FOUNDRY_STATUS.txt` @d332658cf). [OBSERVED]
- Endpoints: M1 `192.168.1.202:8811`, schema 4, build 6a4f3aee, per the guide (`integration/SFE_CLIENT_GUIDE.md` s1 @642736763). Production moved to M2 `192.168.1.191:8811`, instance eng_906356f7..., schema 9, build 699ca0f9 (`deploy/DEPLOYED_BUILD_M2.json` @e556c16ba). ATLAS_DERIVED: the client guide is stale. It still names M1 and schema 4.
- Owner: Daedalus. Executors: bitstring (onemax) and NK only. CONCLUDED (Artemis): "instrument, not experiment"; "0 of 69 inbox templates build today" (Herakles quote, REPORT.md:79,165 @0b00e4312).

## Runs/experiments ledger
| id | date | n / outcome | tag | pointer |
|---|---|---|---|---|
| H0-H5 corpus via Vivarium queue | 09-01..09-15 | M1 ledger 89,939 experiments (86,296 from Vivarium); queue 579 completed / 492 cancelled / 79 failed by 09-16 | OBSERVED (Artemis) | REPORT.md:176 @0b00e4312 |
| H5-1 (cs-h5-1-r1) | 09-11 | 24/24 completed; 256 rules at analytic bound, "carries NO evidence" | RAN + CONCLUDED (Archaeon) | roles/Archaeon/H0H5_STATUS.md:12 @6fc3ea619 |
| cs-c3-2 | 09-10 | 149 completed, 1 transport failure; D3 STRUCTURALLY_VOID | RAN | H0H5_STATUS.md:202 |
| CMP1 (SFE-01..10) | 09-17 | 10/10 attempted; 7 COMPLETE, 3 INCONCLUSIVE; 32 worlds / 32 terminated; 14 engine attempts | RAN | roles/Archaeon/REVIEW_PACKET_CMP1_2026-09-17.md:33,57 @0728e9989 |
| CMP2 | 09-17 | 13 live attempts, 0 engine errors, 18 worlds, 117 artifacts, 454 records | RAN | REVIEW_PACKET_CMP2_2026-09-17.md:31-34 @4d80d4b1d |
| CMP3 | 09-17 | 7 CAPABLE_NEGATIVE, 2 WEAK_POSITIVE, 1 INCONCLUSIVE; 0 engine errors | RAN | REVIEW_PACKET_CMP3_2026-09-17.md:18-19 @cb9135104 |
| Campaign 4 (C4-01..10) | 09-18 | 11 attempts / 10 slots; 1,255 engine records; engine 9.0.1/699ca0f9 | RAN | archaeon/campaign4/CAMPAIGN_REPORT.md:22,85-87 @8f1a82ced |
| Campaign 5 | 09-18 | BOUNDARY_CREATED_NO_DISCOVERY_GAIN | CONCLUDED (Archaeon; operator accepted D5-015) | archaeon/campaign5/CAMPAIGN_REPORT.md header @cdb55e152 |
| Campaign 6 | 09-18.. | design + observatory calibration; schema 10 "nothing built" | CONCLUDED (Daedalus) | commit f42b07422 |

CONCLUDED (Artemis): compute left SFE on 09-16, and from then until 09-18 SFE was a "notary" (the harness ran in Archaeon's WSE). No queue rows after 09-18 (REPORT.md:176-178). Comms #586 (Cyclops, 2026-09-25): "SFE 9.0.1 is NOT serving on M2 (nothing on :8811, SFEngineM2Watchdog disabled)". [OBSERVED]

## Defects and invalidations (LOST vs SURVIVES)
- **F-1 length mismatch** (Herakles; fixed as WP-0a, commit 85d6ff060, 09-08). A short bitstring was scored against the full target and returned COMPLETED, with its ceiling silently capped at len/length. At length 32 a 16-bit candidate had ceiling 0.500 (`deploy/f1_length_mismatch_table.py` docstring @85d6ff060). SURVIVES: "all 40 evaluate_bitstring observations on the live M1 ledger have len(bits) == length, so no sealed result can move" (commit msg 85d6ff060). Daedalus also recorded that F-1's own 16-bit row reproduces as 0.312, not 0.250. The ceiling reproduces exactly. [OBSERVED + CONCLUDED (Daedalus)]
- **Deploy drift, schema 7 vs 8** (09-10). Every artifact-bearing row in cs-h1h0-1-p2 FAILED with a 404 on `/budget/reserve` against the schema-7 production engine. 20 failed rows stay as record. 14 slot-free rows were wrongly cancelled by Archaeon's own predicate and re-issued as -r1 (H0H5_STATUS.md:203-204). LOST: those runs. No result was reversed. [RAN]
- **Stall gap that looked like science.** A 13-row gap at rules 143-155 "is the shape most likely to be read as a property of rule space" (8e4fc377a, quoted in notes/A_chronology.md:442-443 @0b00e4312). CONCLUDED (Vivarium). It was caught before anyone interpreted it. The stalls cost 24 rows (5a5b7bb3a, A_chronology F9).
- **Archaeon tick fossil input 0**: "'sfe db not found', 45/45 ticks ... fossil input 0" (5a5b7bb3a, A_chronology.md:453). LOST: signal mining over those ticks had no input.
- **ARCH-36**: one candidate_set_id was reused across N submits. The consumer bound it as one-chosen-over-(N-1). "no readout used it" (H0H5_STATUS.md:14). SURVIVES.
- **CMP1 superseded attempts**: SFE-01 att1 (3 engine errors, 422 on the failure route), SFE-07 att1 (4 errors, 403 SESSION_MISMATCH), plus two harness defects (CMP1:114-118). The rerun recovered each one.
- **Case where the RESULT changed (harness, not engine):** CMP1's SFE-01 and SFE-07 transfer positives "DIED at n >= 10 under common random numbers (effects +0.009 and +0.002)". The controls' zeros came from "harness-seeded fills, a length handicap" (CMP2:41-43, 170-178). CONCLUDED (Archaeon). ATLAS_DERIVED: I found no case where an ENGINE defect reversed a published claim. Every reversal I found traces to the harness or the design.
- **C4 D4-005**: a 422 on info_kind "measurement" came after all 798 records had landed. a02 resumed a01 with 0 errors (archaeon/campaign4/DECISIONS.md:75-79 @8f1a82ced). SURVIVES.
- **C4-07 mechanism reading superseded by C5-08** (operator ruling). The numbers stay valid (`archaeon/campaign4/SUPERSESSION_2026-09-18.md`).
- **Vivarium canary WORK_NOT_CLAIMABLE**: a death between observations left a COMPLETED work item that could not be reclaimed. Fixed as a keyed REPLAYED/RECOMPUTED claim (commit fa8a8442e). [RAN]

## Rulers/receipts
- Build pins: `deploy/CANDIDATE_BUILD.json` (726275da, schema 8, "Nothing has been deployed", @a1dd1458c) vs `deploy/DEPLOYED_BUILD.json` (schema 8, pinned 212651aa4) vs `DEPLOYED_BUILD_M2.json` (699ca0f9, schema 9). ATLAS_DERIVED: candidate and deployed were tracked as separate files because deploy != commit. Daedalus: "a healthy old engine was indistinguishable from a healthy new one to every check the stack had" (aa1aa74a3, A_chronology F5). Vivarium: "The production engine was schema 7 while my dev build was 8, then the reverse a day later" (F6).
- H0-H5 iteration 1 (ef05397f2, 09-09): ran on a dev engine eng_2e24cebc..., "NOT DEPLOYED", tests 319 -> 342, nine mutants. Migration 7->8 rehearsed on a copy of the 584-world ledger. The 3,967 existing BUDGET_CONSUMED events were not back-filled. [RAN]
- 9.0.1 repair: 0 5xx; write-lock max 0.34 s; restart 0.5-9.7 s (1577917f0). G1 proof: 15,408 s, 0 5xx, 50/50 anchors on the NVMe (e7a699099). An earlier G1 run failed at 3h27m on the SMR HDD (e556c16ba). C9 burst on HDD 633.8 s vs NVMe 20.5 s; calls over 5 s went from 53 to 0 (4c2fcfbdf). [OBSERVED]
- Known gap: `record_observation` accepts CLIENT_ASSERTED unless require_attestation is set (comms #871 R-08, Artemis workers' claim, marked unverified).

## Cross-engine hooks
- Archaeon's role: producer/miner, "not an executor". It reads `engine.db` read-only (roles/Archaeon/RESPONSIBILITIES.md:47,85). Pipeline: PEW/SFE fossils -> Archaeon -> Postgres queue -> Vivarium -> executor -> SFE -> PEW (roles/Archaeon/CHARTER.md:11-12). From CMP1 on, Archaeon ran its own harness with its own client (cmp1..cmp6-archaeon) and posted records to SFE. C6 planned to use Vivarium's queue for long runs "once G6-1 is green" (archaeon/campaign6/DECISIONS.md D6-003 @1b5c91f27).
- `deploy/` imports archaeon.producer.costs and viv.*. BEE's kernel imports sfe. Archaeon's z80atlas/envgate use no SFE (roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md:17,19,25 @95fff9111).
- Atlas registry: sfe is one of 4 engines with experiments (~1,897 total) (ENGINE_LANDSCAPE:58).
- CONCLUDED (Artemis): SFE is "orphaned, not decided". Its provenance guarantees (prediction before observation, losers kept, attestation) have no successor (REPORT.md:88-107). The retrospective's T5 became FR-057, a cross-engine reversal catalogue (comms #752).
