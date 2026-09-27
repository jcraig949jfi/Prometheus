# Spike A -- SFE evolution chronology (evidence-based)

    seat      Artemis (research assistant pass), 2026-09-27
    worktree  artemis-base-role @ f287a4fdb (origin/main tip 2026-09-27)
    method    git log / git show on bounded pathspecs; quotes are verbatim
              from the cited path at the cited commit. "INFERRED" marks
              anything not stated in a source. Three sub-passes (Vivarium/PEW,
              Archaeon campaigns, M1/M2 + new engines) were merged here;
              key SHAs were spot-checked (ccb26df01, a901ba0c9, 95fff9111,
              36b40870c, 2b21acf76, 6dc37ef5d, 8c5a1a23b).
    scope     READ-ONLY. No repository or database state was changed.

Abbreviations: SFE = Serendipity Foundry Engine (Gen-2, /v2). D-13 = the
older Serendipity Foundry instrument (/v0, port 8799, F:\SerendipityD, not in
this repo). PEW = Prometheus Evidence Wiki. M1 = SKULLPORT 192.168.1.202.
M2 = SPECTREX5 192.168.1.191.

Friction classes used in s7: ARCH (architectural), SVC (service/deployment),
SUBSTRATE (science needed a different substrate), SPEED, ORG (agent
organization), PROV (provenance requirement), HOST (host pinning).

-----------------------------------------------------------------------
## 0. ONE-SCREEN TIMELINE
-----------------------------------------------------------------------

    2026-08-17..27  D-series lineage and "Genesis" runs on the D-13 /v0 Foundry
                    (agent_d*_blind, Operator/Lens Genesis). Not SFE.
    2026-08-30      Genesis ecology chart names "SERENDIPITY FOUNDRY (physical
                    M1) measurement / execution / provenance / replay"; an
                    append-only ledger "remains unbuilt" (52b92da3f).
    2026-09-01      SFE (Gen-2) enters the repo in ONE commit with its client,
                    preserved D6..D10phase2 genesis, and the Daedalus seat
                    (d332658cf). PEW V0 same day (c711c5bf6).
    2026-09-02      GEN-2.1 schema v3 (5a34b0485); World Foundry v0 / Incubator
                    / MHC design packets filed under SerendipityFoundry/.
    2026-09-04      Second, independent SFE on M2 because "M1's Claude budget
                    ran out" (53f11b286); PEW M2 made independent (d4e7d13c1).
    2026-09-05      Vivarium (8b940a165) and Archaeon (df0837064) seats born;
                    schema v5 affinity, v6 scientific provenance (869df1fa1).
    2026-09-06      Schema v7 (2fa52de86); D-LOCK-1 availability defect
                    (e307d6e5f); first write stalls and full outage reported by
                    Vivarium; Archaeon expansion roadmap (87bab0877).
    2026-09-09..10  Schema 8 (ef05397f2, d5be5ec4b); H0-H5 loader; nk_landscape_v0.
    2026-09-11      Recurring 13-17 min stalls; D-23 ledger-in-checkout finding
                    (fe2eb85c9); root cause = SMR HDD (e031cb4fb).
    2026-09-12      M1 ledger moved to NVMe (4c2fcfbdf).
    2026-09-14      Nestor NPE/primordial born (a901ba0c9) citing SFE persistence
                    slowness. M2 SFE silently dead 09-14 05:33 (2b21acf76).
    2026-09-15      "M1 is handed to Nestor and SFE moves to M2" (ccb26df01).
                    M1 8811 last reachable 20:12Z (7c89a7199).
    2026-09-16      M2 SFE relocated and relaunched as PRODUCTION on its own
                    ledger eng_906356f7; M1 ledger eng_8a37a5d3 archived
                    (2b21acf76, f697ce988, a1dd1458c).
    2026-09-17      Archaeon CMP1-3 records through SFE@M2; schema 9 point
                    release (fbfcfb276); 9.0.1 WAL repair (2983bd548); M2 ledger
                    moved SMR -> NVMe after 3h27m G1 failure (e556c16ba).
    2026-09-18      Campaigns 4-5 through SFE records but harness compute;
                    operator orders SFE ledger into Postgres (6dc37ef5d);
                    Campaign 6 "engine as observatory" review, nothing built
                    (f42b07422, 9cfcd3779 = LAST SFE commit). Bellerophon born.
    2026-09-19..24  z80atlas x3, Aether, Cosmos, Ensorain, Ananke, Aphrodite
                    engines; Archaeon science leaves SFE entirely.
    2026-09-24      M2 at 98% commit: SFE 8811 and PEW 8377 hung; "0 rows
                    enqueued since 09-18" (8c5a1a23b).
    2026-09-25      Archaeon ENGINE_LANDSCAPE: SFE = "instrument only" (95fff9111).
    2026-09-27      No SFE / Vivarium / PEW commits in ISO week 39.

-----------------------------------------------------------------------
## 1. ORIGINAL INTENTIONS (what SFE was supposed to become)
-----------------------------------------------------------------------

### 1a. Pre-history: the D-13 Foundry (/v0) that SFE descends from

- SFE's code never existed in this repo before 09-01. Its predecessor, the
  D-9/D-13 "Serendipity Foundry" instrument (release 50b5c232, F:\SerendipityD,
  https://192.168.1.202:8799), was a GP / program-search service. Apollo's notes
  (apollo/serendipity/FOUNDRY_API_NOTES.md, 0cd909f7b, 2026-09-01) list its
  engines "stackvm-v1", "push-pyshgp", "treegp-deap" and drivers "random /
  objective / novelty / map_elites".
- Harmonia's D-14 packet (harmonia_a/d14/REVIEW_PACKET_D14_INTERIM.txt,
  4b3a25312, 2026-09-01) gives the purpose: "The Foundry is Prometheus's
  instrument for doing falsification-grade science on EXECUTABLE EVOLUTIONARY
  SUBSTRATES". It says the Foundry exists because the north star is "a machine
  that can acquire NEW REASONING OPERATIONS", and that it is "where candidate
  mechanisms for that claim get executed, measured, and mostly killed".
- The same packet states the two-machine doctrine: "M1 (192.168.1.202) runs the
  instrument -- the single EXECUTION AND PROVENANCE AUTHORITY. M2 ... never
  executes substrate code locally; a locally improvised substrate is
  constitutionally forbidden as a replacement for the instrument." (4b3a25312)
- The Genesis ecology working org (aporia/docs/GENESIS_ECOLOGY_WORKING_ORG_
  2026-08-30.md, 52b92da3f, 2026-08-30) places "SERENDIPITY FOUNDRY (physical
  M1) measurement / execution / provenance / replay" under every science seat.
  It notes "The out-of-band append-only ledger belongs under Serendipity
  Foundry ... and remains unbuilt."

### 1b. The Gen-2 rebuild (SFE proper), 2026-09-01

- roles/Daedalus/GENESIS.md (d332658cf, 2026-09-01): "The current runtime is
  the Gen-2 rebuild of this line as a durable, multi-world research operating
  system". Its listed contents: "a per-world hash-chained event ledger, an
  atomic work queue with leases, fork-by-reference, prediction-ordering
  enforcement, first-class failures, sharing topology, per-world budgets, and a
  FastAPI /v2 API."
- docs/SERENDIPITY_FOUNDRY_GEN2_BASELINE.md (d332658cf) is a forensic audit of
  D-13. It found multi-tenancy, sessions, research WORLDs, work queue, leases
  and cross-store atomicity "ABSENT", and the "load-bearing finding for Gen-2"
  to be "there is no single transaction" across its three stores.
- docs/SERENDIPITY_FOUNDRY_GEN2_ARCHITECTURE.md (d332658cf): "The smallest
  system that satisfies the invariants. One SQLite database is the
  authoritative substrate". Deliberately excluded: "No distributed
  infrastructure (one SQLite file). No agent framework ... Intelligence
  (mutation, selection, interpretation) lives in drivers/executors, never in
  the runtime".
- docs/SERENDIPITY_FOUNDRY_GEN2_MIGRATION.md (d332658cf) anticipated wrapping
  the old science engines: "Synchronous /v0/search ... Could become a Gen-2
  executor kind ... so Gen-2 owns the lifecycle while the D-13 engines do the
  science. Not built this pass." INFERRED: this wrap was never built. No later
  commit under SerendipityFoundry/ mentions it.
- SERENDIPITY_FOUNDRY_STATUS.txt (d332658cf) set the limits from day one:
  "Single machine only (SQLite by design); no distributed mode"; "executor
  isolation: reference executors run in-process"; "No full replay/restore
  engine".

### 1c. What it was expected to grow into (2026-09-02 design packets)

- World Foundry v0 (SerendipityFoundry/worldfoundry/WORLD_FOUNDRY_V0_EXTERNAL_
  REVIEW_PACKET.txt, 6efa4f88d, 2026-09-02, author Daedalus) describes "A
  machine for producing enormous numbers of small, semantically sterile,
  reproducible worlds -- and for finding one real bump in a flat landscape of
  millions of failures".
  - Role split: "PROTEUS player foundry ... DAEDALUS world foundry ...
    HARMONIA matchmaker/operator -> schedules frozen encounters on M1-M4 ...
    SFE engine -> authoritative immutable experiment record ... MNEMOSYNE
    PEW/Tensor".
  - Workload and target: "Expected workload: millions of cheap failures ...
    Build a seismograph, not a leaderboard".
  - Section 10 is a "DISTRIBUTED M1-M4 EXECUTION PLAN" that "Reuses the
    engine's existing fabric: lease-fenced claims".
  - Boundary with PEW: "SFE = what happened. PEW = evolving knowledge about
    what happened."
- Incubator OEE program (406d3e5c4, 2026-09-02) framed open-ended-evolution
  failures as experiments ("World-0"). It shrank the next action to "build ONLY
  the generator and null battery".
- PEW V3 charter (roles/Mnemosyne/prompts/CHARTER_PEW_V3_2026-09-02.txt,
  66f76e1e6, 2026-09-02): "Daedalus/SFE will preserve authoritative
  experimental history" for an Incubator of "potentially millions" of
  organisms.
- Archaeon charter expansion (roles/Archaeon/CHARTER.md, 36b40870c,
  2026-09-06): "When the bench cannot run an experiment a discipline suggests,
  the recommendation is to grow the bench. SFE is the petri-dish maker; players
  are the organisms dropped in; both are shapeable."

Net original intent: SFE was to be the authoritative multi-tenant ledger and
work fabric for a distributed (M1-M4) open-ended world/organism incubator
running millions of cheap trials. It was never intended to be the simulator:
organisms and worlds came from Proteus, Daedalus's world foundry and executors.
The distributed plan conflicted with the "single machine only" SQLite design
from the start (d332658cf STATUS vs 6efa4f88d s10). INFERRED: the conflict was
never resolved in writing before the 09-18 Postgres ruling (s4).

-----------------------------------------------------------------------
## 2. ARCHITECTURE STAGES OF SFE
-----------------------------------------------------------------------

| Date | Commit | Stage |
|---|---|---|
| 09-01 | d332658cf | Gen-2 imported. /v2 FastAPI over SQLite (WAL); per-world hash chain; leases; client-scoped isolation (two cross-tenant breaks fixed pre-onboarding); TLS on M1:8811; stdlib client; first user Harmonia (roles/Daedalus/HARMONIA_ONBOARDING.md). Engine suite 32/32. |
| 09-01 | ec4d35a1c / f9dd6ed88 | Requalification repair: experiment commit boundary. |
| 09-02 | 5a34b0485 | GEN-2.1 "Crossing Hardening", schema v3: content retrieval, info_kind ontology, falsification-monotonic adjudication, X-SFE-Engine-Source-Hash, Idempotency-Key. |
| 09-02..03 | 6efa4f88d, 406d3e5c4, a6f86c3d3, 5821ee076, ef504133f | Design/science packets filed INSIDE SerendipityFoundry/ (World Foundry, Incubator, MHC, WOW, stackvm admission, selection boundary). INFERRED: the directory held the program's science, not only the engine. After 09-03 nothing of this kind was added there. |
| 09-03 | a8f21be9b | First-integration battery (sfe_battery). The access log shows "21,047 requests from M2". |
| 09-04 | 9bcba33d9, 67c28acee | "quiet-success hazards" closed; D-REPLAY-1. |
| 09-04 | aa1aa74a3 | "code ready, service is not". The deploy was blocked because Stop-Process was denied; "REPLAY_COMPLETE: NO". |
| 09-04 | 53f11b286, 5b475a58a | Second, independent engine on M2 ("not a cluster, not a replica pair"). |
| 09-05 | 773ae5e03 | M1 upgraded to parity with M2. |
| 09-05 | 9f6f11605 | Schema v5 session affinity. |
| 09-05 | 869df1fa1 | Schema v6 scientific provenance: "FAMILIES ARE THE FIRST CROSS-WORLD SCIENTIFIC CONTAINER". |
| 09-06 | 2fa52de86 | Schema v7: family/arm survive fossilization, cross-seat read contract. |
| 09-06 | e307d6e5f | D-LOCK-1: every request took the exclusive lock. |
| 09-06 | d0bc13981 | Surface made usable "by a MACHINE" (Vivarium/Archaeon onboarding). |
| 09-09..10 | ef05397f2, d5be5ec4b | Schema 8: authorized artifact resolution, cost events, engine-side digest gate (joint Track A with Vivarium, 07b5b05a7/45195dd83). |
| 09-10 | b91880a2d | nk_landscape_v0, the first non-onemax scientific executor core. |
| 09-11 | fe2eb85c9 / e99a7b35c | D-23: service and ledger moved out of the canonical checkout. |
| 09-11..12 | 8e4fc377a, 8c53d04e6 | A6 incident journal ("the ledger is silent exactly when the engine is what broke"). |
| 09-12 | 4c2fcfbdf | M1 ledger moved HDD -> NVMe. |
| 09-16 | 2b21acf76, a1dd1458c | M2 relocation (pinned worktree, D-23), then PRODUCTION on M2 (eng_906356f7). |
| 09-17 | 084e8c18e / fbfcfb276 | Schema 9 point release: "the engine records the world's facts" (logical_time, typed termination, WORLD_EVENT, manifest envelope, labels, fork diff, cursors). Universal FLOOR/SHELF/SUMMIT concepts REJECTED from the engine (docs/point_release_2026-09/SFE_RELEASE_PACKET.md). |
| 09-17 | 3e8893a8c ... 2983bd548 | 9.0.1 WAL-choke repair after eight iterations. Two reverts: 140858f79, 8fb4c158f. Windows ephemeral-port exhaustion found in tooling (a3926ee15). |
| 09-17 | e556c16ba, e7a699099 | M2 ledger moved SMR HDD -> NVMe; G1 proof 15,408 s. |
| 09-18 | f42b07422, 9cfcd3779 | Campaign 6 review and schema-10 delta D1-D9: "nothing built". LAST SFE commits. |

Worlds and organisms: in SFE a WORLD is "the primary experimental unit and the
isolation boundary" (GEN2_ARCHITECTURE.md, d332658cf). It is a set of ledger
rows, not a simulated space. Archaeon's landscape table (95fff9111, 09-25)
says: "No physics: a WORLD is a tenant of ledger rows; specimens = bitstring /
NK genomes scored by executors; mutation+selection live in clients".

D6..D10phase2 are the pre-split D-series runs preserved verbatim, each with a
single commit (d332658cf). They are lineage only, never modified or executed
in this repo (roles/Daedalus/GENESIS.md). They are not phases of SFE.

-----------------------------------------------------------------------
## 3. VIVARIUM, PEW, ARCHAEON: EMERGENCE AND COUPLING
-----------------------------------------------------------------------

### PEW (evidence_wiki/, Mnemosyne)

- Born the same day as SFE: c711c5bf6, 2026-09-01, "EVIDENCE WIKI V0 --
  canonical substrate, REST service ... service on 0.0.0.0:8377".
- Its charter (roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt,
  60721f003) says "Build the Evidence Wiki substrate as a network-accessible
  Prometheus service in the same operational spirit as the Serendipity Foundry."
  INFERRED: PEW copied SFE's service pattern, so it duplicated the deployment
  burden.
- V3 charter (66f76e1e6, 09-02): "SFE = WHAT HAPPENED. PEW = WHAT PROMETHEUS
  CURRENTLY KNOWS ... ABOUT WHAT HAPPENED"; "PEW must NOT become a competing
  experimental ledger."
- Coupling stages:
  1. 09-02: bulk ingest reading SFE's SQLite file directly ("SFE is opened
     READ-ONLY", 4f8f6c875).
  2. 09-03/04: Harmonia as producer ("SFE -> Proteus -> PEW -> Harmonia",
     evidence_wiki/FROZEN.md). The SEAM packet (c68071eac, 09-04) notes "PEW
     cannot verify SFE ledger membership of an anchor".
  3. 09-05: every fossil write calls "SFE POST /v2/audit/verify-anchor"
     (201106edb).
  4. 09-17: Vivarium outbox -> PEW POST /api/v1/events ("DELIVERED 146/146",
     a5bfab10c).
- "PEW frozen waiting for Incubator" (cb43847e9, 09-02) and merged to main
  09-04 (fec786f8b).

### Vivarium (vivarium/, roles/Vivarium)

- Born 8b940a165, 2026-09-05, subject: "the execution loop had no queue, so
  'what ran' was unreconstructable". The body builds "Archaeon -> PostgreSQL
  queue -> Vivarium -> SFE -> PEW".
- Charter (8b940a165): "QUEUE -> EXECUTE FAITHFULLY -> RECORD -> REPEAT";
  "Vivarium is not a scientist"; "consumes the published /v2 API and modifies
  no engine semantics".
- Vivarium is the queue, the only end-to-end REST executor and PEW's producer.
  Archaeon adopted its queue on 09-06 (c9304ff02).
- INFERRED: SFE had a work queue (claim/lease) from 09-01, but a second queue in
  Postgres (viv.research_experiment_queue) was built in front of it. Nothing in
  the evidence explains why SFE's own queue was not used as the program queue.
  It is plausibly because SFE's queue is world-scoped and tenant-isolated.
- Last commit 8c5a1a23b (09-24, incident). Vivarium was declared
  "QUALIFIED_FOR_CAMPAIGN" on 09-17 (9156213f8).

### Archaeon (archaeon/, roles/Archaeon)

- Born df0837064, 2026-09-05: "Archaeon reads SFE/PEW fossils, looks for a weak
  structure, and proposes ONE probe per cycle". Charter v0: "Archaeon owns
  exactly one arrow: fossils -> queue. It does not run experiments".
- Expanded by the operator 09-06 (36b40870c): recommend "where the whole
  program must grow: Vivarium's loops, the SFE, the Postgres schema"; "Not an
  executor. Archaeon proposes; Vivarium runs."
- It became producer and overseer through inbox asks to Daedalus: read grant
  and families (fc156ae52), arm-key conflict (e3fab51cc), expansion roadmap
  (87bab0877, 4322225c3), and the read-scope proposal (e4b05ae62). B1 was
  granted on 09-10 (ef18ef884).
- It became lead experimentalist on 09-16/17 by operator directive, not by
  charter. roles/Archaeon/prompts/2026-09-17_sfe_campaign1/
  00_OPERATOR_DIRECTIVE.md (3a34d207a): "take the SFE ecosystem through ten
  sequential experiments"; "Where this directive and the seat charter ('not an
  executor') disagree ... the directive wins."
- The README label "service: Daedalus . science: Archaeon" first appears
  4933204b5 (2026-09-23). By then Archaeon's science had already left SFE (s5).

Coupling shape by 09-10 (INFERRED from the above): Archaeon (proposal) ->
Postgres queue on M1 -> Vivarium (execute) -> SFE REST on M1 (record) -> PEW
REST on M1 (fossil) -> Archaeon tick reading fossils. That is five seats and
three services for one experimental row. The Vivarium post-mortem measured the
cost (s7 F6).

-----------------------------------------------------------------------
## 4. M1 <-> M2 PORTABILITY, FORKS, OUTAGES
-----------------------------------------------------------------------

- 09-04, 53f11b286: M2 gets "a second, independent engine" because "M1's
  Claude budget ran out, so agent work moves to M2 for a few days".
  docs/RUNNING_M1_VS_M2.md says it is "not a cluster, not a replica pair, and
  not a failover".
- 09-04, same commit: PEW "deliberately NOT forked". M2's local Postgres copy of
  prometheus_fire "would give the program two divergent evidence stores", and
  the M2 launcher forces EW_DB_HOST to M1. Hours later d4e7d13c1 (Mnemosyne,
  09-04), "Per James's ruling that M2 must be fully independent", made M2 PEW
  serve "its OWN local prometheus_fire". This is the origin of the "M2 local
  Postgres fork". It is a PEW / shared-DB copy, not an SFE fork.
- 09-11: Hermes incident (roles/Hermes/incidents/c84e26826cc12217.md) reports a
  "resolver reaches a non-canonical store ... prometheus_fire (M2 fork)" via
  db_host=localhost in tracked evidence_wiki/config.json.
- 09-16: Vivarium (78012e2a8) found "archaeon/tests/conftest.py was silently
  creating throwaway schemas on the QUARANTINED M2 fork".
- 09-17: operator ruling (b9a301da3): "Everyone should be using the postgres
  database on M1 for the comms channel. Postgres on m2 is intended for
  mechanisms that truly need to be duplicated ... Machine independence."
- 09-06, f5fdeb1cd (M2_V6_DEPLOYMENT_READINESS):
  - "D4-1 said 'blocked on M2 down'. That was false and unchecked."
  - "Stop-ScheduledTask alone orphans the Python tree ... It has happened
    twice."
  - "M2 launches from D:\Prometheus, which I cannot inspect from here."
- 09-11/12: SMR-HDD stall diagnosis (e031cb4fb) and ledger move to NVMe
  (4c2fcfbdf, 80.2 s outage). D-23: "212.8 MB of live ledger ... deploy/m1.key
  -- the TLS private key, not in git, no other copy" lived inside the canonical
  checkout (fe2eb85c9).
- 09-14 05:33: M2 engine dead for two days. "the watchdog relaunched every 5
  min for two days (~600 refusals)" because the D-23 guard refused the
  canonical checkout. The tracked watchdog "was replaced mid-run by a git pull"
  (2b21acf76, 09-16).
- 09-14 19:55: SKULLPORT rebooted; SFE and the Vivarium consumer stopped
  (roles/Daedalus/journal/2026-09-16.md).
- 09-15, ccb26df01 (operator session, author James Craig): "M1 is handed to
  Nestor and SFE moves to M2 carrying M1's engine.db". Daedalus journal
  (2b21acf76): "A directive that reached me only as a commit message ... No
  prompt, no comms post, no migrated ledger on M2."
- 09-16, 7c89a7199 (INBOX_ARCHAEON_ENGINE_UNREACHABLE_AND_B1_ON_M2): "The SFE
  engine at https://192.168.1.202:8811 is unreachable from M2 and Archaeon's B1
  read credential exists on M1 only"; "TCP connect ... TIMEOUT (not refused)";
  last reachable "2026-09-15 20:12:09 UTC"; "I will NOT copy the M1 token by
  hand".
- 09-16, f697ce988 topology ruling: "Postgres and Redis are the shared
  substrate (on M1 ...); every other service runs on exactly one machine, never
  both ... The M1 engine ... is not coming back."
- 09-16, a1dd1458c: the operator says "the M1 ledger does not move ('kicking
  the tires, seeing what ramping up looks like')". Production became
  eng_906356f7 on M2, with the M1 eng_8a37a5d3 ledger archived. Consequence:
  the 09-10 corpus is reachable only on SKULLPORT. Harmonia's HARM-13/16/18 are
  blocked (roles/Harmonia/RESUME_20260925_m2-ca1148a0.md, c09c9891e) and
  Archaeon's ARCH-47 is "NOT NOW from M2 alone".
- 09-17, e556c16ba: "G1 long run FAILED at 3h27m on the SMR HDD -> production
  data dir moved D: -> C: (NVMe)". This is the same class as the M1 C9 failure.
- 09-18, 6dc37ef5d, operator verbatim: "I don't want us using SQLite for this
  very reason. Postgres is there as a shared database across machines so we
  don't have this problem of moving data files around." Acceptance conditions
  A-1..A-8, including "C4 launch gate G1 does NOT transfer to
  Postgres-over-LAN". Status 09-25 (c09c9891e): "Nothing has moved since." No
  Postgres code under SerendipityFoundry/.
- 09-24, 8c5a1a23b: "M2 host at 98% commit ... 48 live pool children from
  archaeon envgate2/audit assays): SFE 8811 and PEW 8377 hold their ports but
  time out (hung) ... SFEngineM2Watchdog Disabled"; "0 rows enqueued since
  09-18"; the dead-man "could NOT post its notice because comms lives on the
  store it was escalating".

Count: in 13 days SFE was re-hosted or its ledger moved four times (M2 twin
09-04; M1 HDD->NVMe 09-12; M1->M2 09-15/16; M2 SMR->NVMe 09-17). It had three
multi-hour-or-longer outages (M2 09-14..16 silent; M1 from 09-15; M2 hung
09-24) plus the 09-06 and 09-11 stall/outage episodes.

-----------------------------------------------------------------------
## 5. CAMPAIGNS: THROUGH SFE vs OUTSIDE IT
-----------------------------------------------------------------------

| Window | Campaign | Path | Evidence |
|---|---|---|---|
| 09-01..09-05 | Harmonia S1/S2, first experimentalist | THROUGH SFE M1 | a295092e5 (D5 log of Harmonia's blockers) |
| 09-05..09-15 | Archaeon loop, H0-H5 (H5-1 cs-h5-1, 256 rows) | THROUGH SFE M1 via Vivarium queue | H0H5_STATUS.md (010cd2084); queue "completed 579, cancelled 492, failed 79" (7c89a7199) |
| 09-11 | ARCH-26 | OUTSIDE (local) | journal bd152bc15: "ARCH-26 executed while the engine is down" |
| 09-11 | Nyx n1 knife transfer | OUTSIDE | dac8f1c23: "RUN outside the engine", "RUN with no engine imported" |
| 09-16 | WSE survey v01, SSF C1-3 | OUTSIDE, standalone on M2 | 7faa0cc43: "the SFE/PEW loop is not a usable execution path TODAY" |
| 09-17 | CMP1, CMP2, CMP3 | RECORDS through SFE@M2; compute in Archaeon WSE harness | CMP1 report 0728e9989: "Engine: SFE v2 on M2 ... Search substrate: the WSE selection loop"; CMP2 4d80d4b1d "13 live engine attempts, 0 engine errors" |
| 09-18 | Campaign 4 (damage geometry) | RECORDS through SFE 9.0.1; harness compute; Vivarium rehearsal only | 8f1a82ced: "'Execution: Vivarium' could not be honoured for science rows" |
| 09-18 | Campaign 5 (neutral cliff) | Same as C4 | cf841ed6d: "Vivarium's wse_evaluate_v1 did not exist" |
| 09-18 | Campaign 6 (Cambrian / observatory) | PLANNED through SFE + Vivarium segments; rehearsal in-process only | f603b3e8b PLAN; Daedalus f42b07422 "nothing built"; 20407a3a1 "segments run in-process", G6_0 all verified = false |
| 09-18..22 | Deep Frontier | OUTSIDE (in-process) | 20407a3a1, a3325b392 |
| 09-19..22 | Z80 x Atlas 72h (Archaeon c7610ea19; Bellerophon 98b2149a7) | OUTSIDE | frontier/DECISIONS.md DF-016; ENGINE_LANDSCAPE 95fff9111 |
| 09-24..26 | ENVGATE-01, ENVGATE-02 (WINDOW_NOT_SUPPORTED c5ba19571) | OUTSIDE | 95fff9111: "numpy CPU only; no SFE/PEW/Viv/Postgres" |
| 09-26..27 | PORTABILITY-01, Causal Lineage Contract v0.2/v0.3 | OUTSIDE; adapters for archaeon/bee/npe/ananke, NO SFE adapter | 13cdec715, 37145999d |

Pattern: SFE was the execution substrate only 09-01..09-15, and only for
bitstring/onemax/NK-class work. From 09-16..09-18 it was the record-of-citation
while compute ran in Archaeon's harness ("It is not a compute service; it is
the thing that makes a claim CITABLE", REVIEW_PACKET_WSE_ARCHITECTURE_
2026-09-17.md, 503fcf5b7). From 09-19 no campaign touched it.

-----------------------------------------------------------------------
## 6. SEPARATE ENGINES: FIRST DATES AND RELATION TO SFE
-----------------------------------------------------------------------

| Engine | First commit | Relation to SFE (evidence) |
|---|---|---|
| NPE / primordial (Nestor) | seat 0100d36cd 09-14; code a901ba0c9 09-14 | SUPPLEMENT, founded partly on SFE's slowness. Directive (roles/Nestor/prompts/2026-09-14_graphworld_swarm/00_OPERATOR_DIRECTIVE.md, a901ba0c9): "The major measured slowdown is persistence ... operational experiment throughput is around 1.4 rows/sec. A Vivarium result currently causes roughly twelve separate web interactions before reaching the SQLite ledger." It reframes: "The interesting question is not: Can Redis or FalkorDB make SFE faster? It is broader". Also "Do not modify Daedalus-owned production machinery directly." Took M1 on 09-15 (ccb26df01). |
| Bellerophon BEE / toolbox / Worlds Kernel | 44dc09559 09-18; kernel 4c0435544 09-18 | LAYER ABOVE SFE and NPE. Operator: "We have 2 ecosystems, SFE and NPE ... build out toolboxes for both" (fba5a5a7f). TOOLBOX_RESEARCH (44dc09559): SFE is "One SQLite file ... executors run in-process ... everything is pure Python; no numba, no torch". WORLDS_KERNEL_DESIGN_v0.2 (4c0435544): compile-to-SFE "FALSE for SFE as the frontier stands ... mismatches, all semantic, none transport". SFE runtime bridge built without editing SFE (2237af42a, 09-18). |
| Bellerophon z80atlas | 98b2149a7 09-19 | IGNORES SFE ("Nestor's worlds are the crucible"). |
| Archaeon z80atlas | c7610ea19 09-19 | BYPASSES SFE. ENGINE_LANDSCAPE (95fff9111): "the SAME 2026-09-19 Nestor directive built three times independently ... No shared code." |
| Aether AGE | seat 298c2a511 09-19; design 6a5ba2b56 09-20 | DELIBERATELY SEPARATE. Aether/AETHER_DECISIONS.md: "D-1 (operator). Aether is developed independently of BEE, NPE and SFE ... Clean-room design." GPU/RunPod. |
| Cosmos CWE | seat 7a90be1d8 09-23; code 70ce535a2 | SUPPLEMENT (borrows the SELECTIVE_PAYS idea from Archaeon/SFE WSE; SFE is not the backend). Design 01: the SFE "service ... stores science and does not simulate. The program is Archaeon's campaigns." |
| Ensorain Tensor World Engine | seat 57ed9184e 09-23; code 20a4bab5c 09-23 | IGNORES SFE ("Make it earn the right to exist"). |
| Ananke PTE | seat 7acc2926c 09-24; code 7b6958b1c | IGNORES SFE (reuses Aether's RunPod tooling). |
| Aphrodite | seat 8b54a74b8 09-17; charter 3d86dc292 09-18; local engine 85b85b765 09-21 | IGNORES SFE. Local engine because "Nestor and Archaeon are tied up ... It does not need to be fast ... It needs to be auditable". |
| Atlas (index, not an engine) | 61c3985fc 09-19; charter 4fb8c7fc2 | SHADOW: "experiment-history shadow of the SFE, NPE and future engines". It does NOT index z80atlas/envgate (95fff9111). |

Displace vs supplement: no founding document declares SFE displaced. The
Synthesis directive (roles/Chiron/prompts/2026-09-21_synthesis_directive/
SYNTHESIS_DIRECTIVE.md on origin/chiron/base-role-adopt-2026-09-21; commit
9e54a51ce) keeps SFE as one of several "puddles": "Each engine is a differently
shaped 'puddle.' We stir all of them." In practice, as INFERRED from s5 and the
Vivarium incident 8c5a1a23b, SFE was displaced as the place science happens,
with zero queue rows after 09-18. It was never replaced as the provenance
authority because no successor ledger exists. Provenance for the new engines is
per-engine, and the cross-engine Causal Lineage Contract (Archaeon 09-26) has
no SFE adapter.

-----------------------------------------------------------------------
## 7. FRICTION EVIDENCE (quoted)
-----------------------------------------------------------------------

F1 [SPEED, SVC] Write stalls on first multi-consumer load. roles/Daedalus/
   INBOX_VIVARIUM_SFE_WRITE_STALL_2026-09-06.md (35f8a64bc, 5be9b847c, 09-06):
   "writes went to ~31-34s, and the 500s look like something timing out";
   "POST /v2/sessions 51.58s -> 500"; "cannot pass while writes take four
   minutes".

F2 [ARCH, SPEED] D-LOCK-1 (e307d6e5f, 09-06): "every request in the engine
   queued behind every writer, including unauthenticated read-only ones, and
   the architecture's promise of 'WAL for concurrent readers' was false in
   practice"; "GET /v2/version 22.8s". It was found "while onboarding Archaeon
   (producer) and Vivarium (executor) alongside Harmonia".

F3 [SVC, ORG] Full outage with no permission to restart. roles/Daedalus/
   INBOX_VIVARIUM_ARM_KEY_VS_RULING_2026-09-06.md (ad6c5801d, 09-06): "the
   service stopped accepting connections entirely"; "I have not restarted it --
   it is your service and starting another seat's process is exactly what the
   ownership rules forbid". Live proofs of E1/E6/E16 were blocked.

F4 [ARCH, PROV, ORG] Two seats' contracts cannot both hold. INBOX_ARCHAEON_
   ARM_KEY_CONFLICT.md (e3fab51cc, 09-06): "Two seats shipped contracts today
   that cannot both be satisfied by one spec."

F5 [SVC] Deploy != commit. aa1aa74a3 (09-04): "a healthy old engine was
   indistinguishable from a healthy new one to every check the stack had";
   "Stop-Process is denied in this session". 465853b69 (09-06): "the blocker is
   a deploy of mine, not an outage"; "every cross-engine property in v5 and v6
   is still demonstrated ONLY by twin engines in one process".

F6 [SPEED, ARCH] The science is 0.1 s, the row is minutes. roles/Vivarium/
   NOTES_POSTMORTEM_2026-09-08_to_09-11.md (b57dd8c0e): "The science is 0.1s.
   The row is 95-193s. 98%+ is SFE round-trips." Also "The production engine
   was schema 7 while my dev build was 8, then the reverse a day later."

F7 [SVC, PROV] Stalls that the ledger cannot record. INBOX_VIVARIUM_STALL_
   RECURRED_2026-09-11.md (3b7099167): "1041 s 13 failed ... 777 s 15 failed";
   "accepting them and not answering". 8e4fc377a (09-11): "the hash chain is
   silent precisely when the engine is the thing that broke"; a 13-row
   contiguous gap at rules 143-155 "is the shape most likely to be read as a
   property of rule space".

F8 [SPEED, HOST] Root cause was a consumer SMR disk. e031cb4fb (09-11): "C: NVMe
   burst 20.6 s ... F: SMR HDD 633.8 s ... 53 calls >5 s". It recurred on M2
   (e556c16ba, 09-17): "4 KB write+fsync on D: ... median 7.0 s / max 59 s".

F9 [ARCH] Client-side amplification. roles/Vivarium/INVESTIGATIVE_REPORT_
   2026-09-11.md (5a5b7bb3a): "85,727 phantom experiments in my worlds ... the
   two engine stalls that cost 24 rows followed those write bursts"; "Archaeon
   tick fossil read: 'sfe db not found', 45/45 ticks ... fossil input 0".

F10 [PROV, ARCH] Orphans the ledger cannot classify. INBOX_VIVARIUM_ORPHAN_
   VERDICTS_2026-09-11.md (35f32116e): "committed-but-unobserved has at least
   two causes, and the ledger cannot tell them apart". On reading SQLite
   directly: "the coupling that makes both sides unmovable".

F11 [PROV] Going around SFE makes selection invisible (argument FOR SFE).
   roles/Harmonia/prompts/PROMPT_ARCHAEON_VIVARIUM_SFE_CONTRACT_2026-09-06.txt
   (a861d2873): "the same six rehearsed on a private engine and submitted once
   leaves 1 world and 9 events ... any mechanism becomes invisible by being
   performed elsewhere." The same file lists the traps "budget.enforcement
   defaults to 'measured', WHICH ENFORCES NOTHING" and "a bare request to SFE
   return[s] empty and succeed[s] on retry".

F12 [SUBSTRATE] Onemax-only executor. INBOX_HERAKLES_BITSTRING_EXECUTOR_
   2026-09-06.md (284022624): "The scorer is onemax: single-peaked, additive,
   noiseless, undeceptive"; the missing relatedness axis "blocks every transfer,
   curriculum, stepping-stone, meta-learning and generalisation template".
   87bab0877 (09-06): "one integrated and qualified world (24-bit seeded
   onemax); 0 of 69 inbox templates build today".

F13 [SVC, HOST, ORG] Machine handover by commit message. 2b21acf76 journal:
   "A directive that reached me only as a commit message". 7c89a7199: credential
   "exists on M1 only", "I will NOT copy the M1 token by hand"; "From M2 the
   states 'tick not firing' and 'tick firing, halting UNREACHABLE' are
   indistinguishable".

F14 [SVC, ORG] Explicit go-around. roles/Archaeon/journal/
   2026-09-16_m2-411504ab.md (7faa0cc43): "Daedalus HOLDS on a conflict between
   two operator rulings ... => the SFE/PEW loop is not a usable execution path
   TODAY; the cheap survey ... runs standalone from this seat's code, with
   ledgers committed, and fossilizes later." INFERRED: "fossilizes later" never
   happened. No later ingestion of WSE v01 into SFE was found, and the Archaeon
   TODO f4871f531 (09-25) lists a "PEW fossilization gap".

F15 [ARCH, SUBSTRATE, ORG] Queue kinds lag the science. Campaign 4 report
   (8f1a82ced, 09-18): "'Execution: Vivarium' could not be honoured for science
   rows: no admissible kind evaluates a program variant". Campaign 5
   (cf841ed6d): "Vivarium's wse_evaluate_v1 did not exist and cannot evaluate
   representation B". Operator (roles/Archaeon/prompts/2026-09-18_campaign5/
   00_OPERATOR_DIRECTIVE.md, f01a00f58): "do not bend the science around the
   queue kind ... Record the execution-path decision explicitly."

F16 [ARCH, SPEED] The ledger is the bottleneck of evolution. SFE_C6_
   OBSERVATORY_REVIEW_2026-09-18.md (f42b07422): "~400-900 ledger events/s
   ceiling, single process"; C6-mid "1e6 evals ... ~4.3 GB, ~1.2-2.8 h per run
   ... the ledger is the bottleneck of evolution, not the VM"; "T0 per
   evaluation CANNOT be one ledger write per evaluation". Vivarium's C6 lane
   (8291e211f): "one row = one engine world = one experiment, and a long run is
   millions of evaluations". Both say "Nothing built". This is the direct
   collision with the 09-02 "millions of cheap failures" intent (s1c).

F17 [ARCH] Storage substrate reversed by the operator. 6dc37ef5d (09-18): "I
   don't want us using SQLite for this very reason ... so we don't have this
   problem of moving data files around." It overturned the 09-01 core design
   decision ("One SQLite database is the authoritative substrate", d332658cf)
   the day after 9.0.1 was qualified on SQLite. Not executed as of 09-25
   (c09c9891e).

F18 [SPEED] NPE was founded on SFE persistence cost. a901ba0c9 (09-14): "1.4
   rows/sec", "roughly twelve separate web interactions before reaching the
   SQLite ledger".

F19 [ARCH, SUBSTRATE] Experiments don't compile to SFE. Bellerophon WORLDS_
   KERNEL_DESIGN_v0.2 (4c0435544, 09-18): "FALSE for SFE as the frontier stands
   ... it is the FRONTIER SCHEDULER's spec that cannot express the IR."

F20 [SVC, ORG] Shared-host starvation. 8c5a1a23b (09-24): 98% commit from
   Archaeon ENVGATE pool children hung SFE and PEW; the dead-man's escalation
   path "lives on the store it was escalating". Archaeon TODO (f4871f531,
   09-25): "M2 ... cannot host several RAM-heavy engines at once".

F21 [PROV] Out-of-SFE work is invisible to the index. 95fff9111 (09-25):
   "Atlas does NOT index z80atlas / census / envgate / envgate2". This confirms
   F11's warning from the other side.

F22 [ORG] Triplicated effort. 95fff9111: Z80 world "built three times
   independently ... No shared code."

Tally by class (INFERRED weighting, counting each F once per class tagged):
SVC 8, ARCH 10, SPEED 7, ORG 8, PROV 6, SUBSTRATE 4, HOST 3.
Service/deployment and single-writer SQLite architecture dominate before 09-16.
After 09-16 the dominant reasons for going around SFE are ORG (holds,
cross-seat queue kinds, host handover) and SUBSTRATE/SPEED (in-process
evolution at 1e5-1e7 evals). No document found gives a SCIENTIFIC reason for
choosing z80atlas/ENVGATE over SFE. The 09-19 move followed the Nestor 72-hour
directive and operator directives (Archaeon sub-pass; INFERRED).

### Why SFE activity stops 2026-09-18 (the coordinator's question)

Evidence, in order:
(a) Daedalus STATUS "Currency: 2026-09-18 03:45Z" (3ddbf5b6a) says "remaining
    engine blocker NONE; the launch gate is RED on G5 (Proteus) only". The
    engine was done and waiting on others.
(b) The Campaign 6 review the same day (f42b07422) found that the engine as
    designed cannot be the per-evaluation store at C6 scale, and specified
    schema 10. "Nothing built".
(c) Also 09-18, the operator ruled the ledger must leave SQLite for Postgres
    (6dc37ef5d). That invalidated the storage just qualified (G1 "does NOT
    transfer"). No seat executed the migration.
(d) Bellerophon (09-18) and a burst of new engines (09-19..24) redirected work.
    Archaeon's science moved to in-process harnesses and z80atlas.
(e) Vivarium: "0 rows enqueued since 09-18" (8c5a1a23b).
(f) The Daedalus seat has no session after 09-18 on any branch
    (git log --all --since=2026-09-18 -- roles/Daedalus SerendipityFoundry).
Conclusion (INFERRED): the stop is the conjunction of (b)+(c). The observatory
scale-out needed a storage redesign, and the storage decision was reversed the
same day. Together with (d) and no scheduled Daedalus session, this left SFE
parked in a qualified-but-unused state. It was not caused by the 8811 outage
(production on M2 was healthy 09-16..09-24) nor directly by the M1 handover
(09-15, three days earlier and absorbed by 09-16).

-----------------------------------------------------------------------
## 8. CONTRADICTIONS IN HOW SFE IS DESCRIBED
-----------------------------------------------------------------------

C1  Instrument vs open-ended foundry.
    A: roles/Daedalus/CHARTER.md (d332658cf, 09-01): "The Engine is the
       instrument. The experiments are not mine ... never let the Engine become
       the fitness landscape." SFE_C6_OBSERVATORY_REVIEW (f42b07422, 09-18):
       "The engine does not evolve anything." ENGINE_LANDSCAPE (95fff9111,
       09-25): "nothing -- instrument, not experiment"; "SFE (instrument only)".
    B: SYNTHESIS_DIRECTIVE (9e54a51ce, 09-21): "SFE / Open-ended foundry for
       generating, selecting, transferring and testing worlds, pressures,
       mechanisms and stepping stones". Archaeon CHARTER (36b40870c, 09-06):
       "SFE is the petri-dish maker". Campaign 6 PLAN (f603b3e8b, 09-18):
       "Build the generators that make SFE stranger".
    Reading: "SFE" names two things. Cosmos design 01 says so explicitly: "Two
    things share the name. The service ... stores science and does not
    simulate. The program is Archaeon's campaigns."

C2  World engine peer vs ledger.
    README (4933204b5, 09-23) lists SFE among engines "deliberately built not
    to resemble one another", as "the long-running world-and-experiment service,
    and the fossil record it has accumulated". The GEN2 ARCHITECTURE doc
    (d332658cf) says a WORLD is a set of ledger rows. ENGINE_LANDSCAPE
    (95fff9111): "No physics".

C3  Single machine vs distributed.
    STATUS (d332658cf): "Single machine only (SQLite by design); no distributed
    mode." World Foundry (6efa4f88d): "DISTRIBUTED M1-M4 EXECUTION PLAN ...
    Reuses the engine's existing fabric". Operator 09-18 (6dc37ef5d): Postgres
    "shared database across machines".

C4  Execution authority vs record-only.
    D-14 explainer (4b3a25312): M1 is "the single EXECUTION AND PROVENANCE
    AUTHORITY ... a locally improvised substrate is constitutionally forbidden".
    WSE packet (503fcf5b7, 09-17): "It is not a compute service; it is the thing
    that makes a claim CITABLE". From 09-16 Archaeon computes locally.

C5  One canonical store vs machine independence (same day, 09-04).
    53f11b286 (Daedalus): PEW "deliberately NOT forked ... would give the
    program two divergent evidence stores". d4e7d13c1 (Mnemosyne, per operator):
    "M2 PEW fully independent (own local canonical store)". Reversed again 09-17
    (b9a301da3: "Everyone should be using the postgres database on M1") and
    09-18 (6dc37ef5d).

C6  Who does SFE science.
    Archaeon charter v0 (df0837064): "does not run experiments"; 09-06: "Not an
    executor. Archaeon proposes; Vivarium runs." Campaign 1 directive
    (3a34d207a, 09-17): "Where this directive and the seat charter ('not an
    executor') disagree ... the directive wins." README (4933204b5, 09-23):
    "science: Archaeon", written after Archaeon had stopped using SFE.

C7  M1 status.
    README/STATUS through 09-15 put SFE at M1:8811 (HARMONIA_ONBOARDING.md).
    Daedalus STATUS (3ddbf5b6a): "SFE on M1 | RETIRED". The task brief itself
    says "engine at 8811 unreachable". That is true of M1 only; production was
    at 192.168.1.191:8811 from 09-16.

C8  Replay.
    STATUS (d332658cf): "REPLAY: PARTIAL". aa1aa74a3 (09-04): "REPLAY_COMPLETE:
    NO". World Foundry (6efa4f88d) reclassifies exact replay as
    "engine-integrity (zero confirmatory weight)". Later documents still cite
    "replayable FACT" (f42b07422). These are not strictly contradictory.
    UNCERTAIN whether full re-execution was ever built. The evidence says it
    was not.

-----------------------------------------------------------------------
## 9. OPEN QUESTIONS / UNCERTAINTY
-----------------------------------------------------------------------

- F:\SerendipityD (D-9/D-13, the Gen-2 mandate "sections 26/27") is not in this
  repo. SFE's genuine first design intent before 09-01 is known only through
  the docs imported in d332658cf and the Apollo/Harmonia notes.
- Why Vivarium built a Postgres queue in front of SFE's own lease queue is
  undocumented (INFERRED reason in s3).
- Whether "fossilizes later" (7faa0cc43) was ever done for WSE v01, CMP harness
  compute, or z80atlas: not found. Treat it as not done.
- Whether the operator intends SFE to be resumed (Postgres migration, schema
  10) or retired: no ruling after 09-18 was found. Harmonia's Q1/Q2 in
  c09c9891e (09-25) are unanswered in the repo.
- Campaign numbering: "Archaeon campaigns 1-6" (SFE campaign directives from
  09-17) and "CMP1-3" overlap. CMP1-3 = campaigns 1-3 per their reports.
  UNCERTAIN whether any separate "campaign" numbering existed earlier.
