# 2026-10-10 OP-NF2 -- native execution fabric (supersedes the Git-CAS runtime plan)

Operator amendment given in chat on SPECTREX5 (session 0e9b1ed2-f51f-49c9-a2ea-5c93be2dfb1c), after the C-008
review packet. 01_OPERATOR_OP-NF2_verbatim.md is the authority; this file only indexes it.

What it changes (summary; 01 governs):
- Git-CAS runtime coordination is replaced by PostgreSQL on the existing canonical cluster. No SQLite.
  No second generic task queue: the existing Fabric service is the starting point.
- Responsibilities: FABRIC (Odysseus) -- submission, claims, worker identity/capabilities, resource
  leases, heartbeats, attempt state, generic retry. MOONSHOT (Themis) -- canonical epoch identity,
  checkpoint lineage, atomic epoch publication, duplicate/disagreement classification, replay/validation
  state, contest/taint resolution. PAN (Pan) -- dataset catalogs, Parquet, Iceberg history, searchable
  evidence metadata.
- Deliverables: (1) a reviewed Fabric/Moonshot/Pan interface contract; (2) a minimal PostgreSQL
  epoch-publication implementation in a versioned Moonshot schema; (3) transactional and adversarial
  fault-injection evidence; (4) a working two-node demonstration with racing workers (identical and
  conflicting); (5) a preregistered fleet benchmark if the two-node controls qualify; (6) a
  Parquet/Iceberg evidence-materialization design or bounded demonstration; (7) a concise engineering
  review of what is ready for native science.
- Boundaries: coordinate with Odysseus and Pan before proposing interface changes; do not modify their
  schemas without review and authorization; use Fabric's canonical leases (no competing lease
  authority); promexec stays EXPERIMENTAL (not production-qualified); approved bounded deterministic
  executors only; no unrestricted command execution or privileged DB credentials for fleet workers;
  authentication, authorization and isolation are acceptance criteria; the authoritative publication
  must not depend on an Iceberg snapshot update; no M2-local lake assumptions for the Ubuntu nodes;
  no Git remote in claiming, executing or publishing these epochs; MWO-0004 limits; local only.
- Preserve C-008 as historical engineering evidence; record any unexecuted Git benchmark as such.
- Keep Moonshot's science moving: native-world repair (Daedalus) and RSO claim mapping (Palamedes)
  continue with their owners; no evolutionary survival search against the wforge affordability defect.
