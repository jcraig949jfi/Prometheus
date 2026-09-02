# PEW V3 Architecture (delta over V0-V2)

Charter sha 0d24ff4fb5e6b9e3d31b10d9219c8ecac617020c43ee20ebaaa3481469fde031.

## Trust boundaries (charter s3, s10)

    SFE (SQLite, hash-chained ledger; AUTHORITATIVE; PEW opens mode=ro ONLY)
        |            events.entry_hash / artifacts.artifact_id (content hashes)
        v
    PEW substrate (Postgres schema ew; append-only; derived, references only)
        |-- fossil_{worlds,players,encounters,edges}   [SFE-hash anchored]
        |-- interpretations (versioned; supersedes-chains; never mutate subjects)
        |-- candidate_bumps (PEW proposes; SFE adjudicates)
        |-- memory_artifacts + memory_influences        [s6 chain]
        |
        |---> HUMAN WIKI  (prose permitted; badges; /wiki)
        |---> EVIDENCE PACKS (frozen, content-hashed; V2-promoted interface)
        '---> PEW-NATIVE  (/api/v1/native/*: ids/hashes/numbers ONLY;
                           firewall scanner-verified against live prose)

## What V3 added
- Migration 005: fossil record, interpretations, candidate bumps, explicit
  memory chain, LEGACY_AMBIENT_MEMORY provenance class.
- Real metabolization: 11,731 rows referencing live SFE history (D6-D8 era:
  242 worlds, 6,006 candidate organisms, 5,452 ledger-anchored encounters).
- Fossil mining module (ew/fossil.py): family x failure matrix, KL-anomaly
  worlds, discrimination-per-cost, SVD exercise, fork-lineage survival —
  all <=7ms at current scale; sparse/relational implementation justified in
  code comments (representation can migrate; query contract stays).
- Batch ingest endpoint (the Incubator path): 712 ev/s vs 7 ev/s
  single-event; direct bulk 8,191 rows/s.
- Native surface + scanner-based semantic firewall (negative-controlled).
- Explicit memory: packs registered by content hash; every experimental
  consumer logged in ew.memory_influences with decision/execution/result.

## What V3 deliberately did NOT build (charter s24)
No player-access native interface; no speculative abstraction engine; no
embedding of wiki prose anywhere near the native surface; no cross-host
deployment scripts beyond what peers can run by pulling the branch; no
compression machinery (only its invariant).

## Known bottlenecks for the Incubator (measured)
1. Per-event REST path (7/s) — use batch. 2. Connection-per-request server
pattern — pool before sustained multi-thousand ev/s. 3. SFE phenotype
coverage (2/6006 candidates carry scores in meta) — upstream requirement.
4. Cross-host operation unqualified until M2-M4 pull the branch.
