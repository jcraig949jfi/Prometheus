# PEW — FROZEN (V3 closeout, 2026-09-02)

State: PEW_FROZEN_WAITING_FOR_INCUBATOR

## Reopened once, under criterion 1 (2026-09-03): first-integration readiness

A real consumer requirement arrived (Harmonia on M2, first end-to-end run
SFE -> Proteus -> PEW -> Harmonia). Scope was integration defects only:
run identity, read-back, overt failure. No new science, no V4.

    Canonical runbook ..... docs/HARMONIA_FIRST_INTEGRATION_PEW.md
    Evidence contract ..... docs/FIRST_INTEGRATION_EVIDENCE_CONTRACT.md
    Machine-readable ...... GET /api/v1/fossil/contract  (pew.fossil.v1)
    Battery ............... integration/pew_battery.py  (E0-E12, 14 gates)
    Fixture ............... integration/fixture_harmonia_v1.json (namespace test)

PEW returns to the frozen posture after this pass. The same reopen criteria
apply to anything further.

- No V4. No new features, ontology work, tensor machinery, retrieval
  experiments, dashboards, mass ingestion, or synthetic benchmarks.
- The service keeps running (watchdog MnemosyneEvidenceWikiWatchdog, port
  8377); maintenance = keeping it alive and ingesting real Incubator/SFE
  fossils when they arrive.
- The next scientific demand comes from real Incubator operation.
- Incubator Watch posture: preserve raw provenance so weak signals in the
  failure landscape can be reinterpreted later without changing history.
  Candidate bumps stay hypotheses with prospective falsification plans;
  PEW proposes, SFE tests.
- Still open under the freeze (not new work): V1 gap slate sealed until its
  60-day window; cross-host M2-M4 qualification BLOCKED until peers pull
  branch mnemosyne/evidence-wiki-v0; memory-clean session procedure is
  UNQUALIFIED until independently demonstrated.

## Reviewer verdict (2026-09-03)

V3 CLOSEOUT ACCEPTED. The pool-race defect is judged
POOLED_WRITE_PATH_ACCEPTED_WITH_CONTAINMENT_EVIDENCE: a qualification
failure that exposed an implementation bug in the pool lifecycle before it
reached canonical state, NOT a provenance breach. Basis on record: failed
workers returned client-visible 500s (overt, not silent-success), no partial
rows, provenance_failures 0, crash/replay still produced zero duplicate
logical records, 2600 stored / 2600 DISTINCT post-fix. The frozen G21 line
reading false is an instrumentation artifact -- its clean-slate cardinality
assumption was invalidated by append-only accumulation -- not write
corruption. No deeper audit required before maintenance use. V3 is not
reopened and the freeze is not delayed.

## Maintenance invariant (binding)

Any future change to connection-pool ownership, transaction lifecycle,
retry behavior, or connect()/close() semantics AUTOMATICALLY REOPENS the
pooled-write qualification subset BEFORE deployment. That subset is:

    python tests/test_distributed_v3.py     (concurrent ingest, duplicate/
                                             retry injection, crash + full
                                             replay, reads during writes)
    python tests/test_firewall_v3.py        (native surface stays clean)
    idempotent-replay check                 (re-POST an identical batch;
                                             row count must not increase,
                                             stored == DISTINCT)

Read G21 by the invariant (stored == DISTINCT, no duplicate logical
records), not by the frozen harness's absolute 600-row expectation.
This protects the seam that actually failed without reopening engineering.

## Reopen criteria (all other work stays closed)

Reopen PEW only on: a real consumer requirement from Incubator/SFE usage;
a failed invariant; completed cross-host qualification; prospective gap
slate adjudication; or a materially larger empirical corpus. Mnemosyne does
not invent reasons to continue.

## Earned capability ledger (reviewer-attested)

    canonical memory substrate ............ yes
    mechanism-level linkage ............... yes
    bounded evidence-pack semantics ....... yes
    operational ingestion service ......... yes
    ambient-memory contamination barrier .. yes
    memory advantage beyond saturation .... only marginal / instrument-limited
    tensor value .......................... no
    cross-host qualification .............. not yet
    memory-clean isolation ................ not yet

Closeout charter: roles/Mnemosyne/prompts/CHARTER_PEW_V3_CLOSEOUT_2026-09-02.txt
sha256 0af9193d60ef0c0beb061bdfd55cd05b5787ec82b84c2863a7efd3e3378ef893
