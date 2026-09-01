# Genesis of the Serendipity Foundry Engine

*Preserved lineage. Daedalus does not delete where the machine came from.*

The Serendipity Foundry Engine did not spring into being as a `/v2` REST service.
It is the current form of a line of work — the **D-series** Serendipity Foundry
runs — that was carried into `F:\Prometheus\SerendipityFoundry` and preserved
here, some of it pre-dating the split into a separate Client and backend Engine.
That is fine and intentional: the pre-split material is the record of how the
ideas took shape. This file is the map of that lineage.

## The preserved runs (under `F:\Prometheus\SerendipityFoundry`)

Each directory is kept **as it arrived** — Daedalus does not modify the genesis.
Read each one's own index/report for its detail; the pointers below are a table
of contents, not a re-interpretation.

| Directory | Entry points | Role in the lineage |
|---|---|---|
| `D6/` | `PREREG_D6A.md`, `REPORT_D6A.md`, `VERDICT.json` | An early pre-registered run with a recorded verdict. |
| `D6A/` | `REPORT_D6A.md`, `prereg/`, `runs/`, `src/` | The D6A line with its own source, prereg, and run artifacts. |
| `D7/` | `README.md`, `code/`, `audit/`, `reports/` | A run carrying its own code, audit trail, and reports. |
| `D8/` | `SESSION.md`, `REVIEW_PACKET.txt`, `agent_d8/` | A session-documented run with an external review packet. |
| `D10/` | `D10_INDEX.md`, `README.md`, `PHASE1_REPORT.md`, `REVIEW_PACKET_PHASE1.txt`, `lib/ preflight/ prereg/ review/ tests/` | Phase-1 run: preflight, prereg, library, tests, and a review packet. |
| `D10phase2/` | `D10_INDEX.md`, `PHASE2_REPORT.md`, `README.md`, `REVIEW_PACKET_PHASE2.txt`, `lib/ phase2/ repair/ tests/` | The Phase-2 continuation, including a repair pass. |

## The split into Engine + Client

The current runtime is the **Gen-2** rebuild of this line as a durable,
multi-world research operating system, then divided into two shipping pieces:

- **`SerendipityFoundryEngine/`** — the backend. Built under `F:\SerendipityD\gen2\`
  during the Gen-2 mandate (package `gen2`), then relocated here with the package
  renamed `gen2 → sfe`. It is a durable runtime: SQLite (WAL, foreign_keys=ON) as
  the authoritative substrate, a per-world hash-chained event ledger, an atomic
  work queue with leases, fork-by-reference, prediction-ordering enforcement,
  first-class failures, sharing topology, per-world budgets, and a FastAPI `/v2`
  API. The original `gen2/` was removed from `F:\SerendipityD` on 2026-09-01
  (commit `ba879da`) with a breadcrumb; its full genesis remains in that repo's
  history at commit `dd006cb`.

- **`SerendipityFoundryClient/`** — configuration, documentation, a stdlib-only
  client library, runnable examples, and the test harnesses. This is what a
  client machine (M1/SKULLPORT, M2, …) uses to connect to and drive the Engine.

## Relationship to the D-9 / D-13 instrument (`F:\SerendipityD`)

The Engine is the **backend descended from the D-9 / D-13 Serendipity Foundry
instrument** that still lives and runs at `F:\SerendipityD` (the live D-13 REST
service on `192.168.1.202:8799`). The two are independent by design:

- The Engine was built **entirely outside** the D-13 release allowlist
  (`foundry/`, `tests/`, `third_party/`, `scripts/`), so the D-13
  `source_tree_hash` stays **`50b5c232…`** and M2's release pin is never
  disturbed by Engine work.
- They run side by side on M1: D-13 on `8799`, Engine on `8811`. Daedalus keeps
  them separate and does not fold Engine code into the D-13 instrument.

## Why preserve all of it

A maintainer who deletes the lineage loses the ability to explain why the machine
is shaped the way it is — why the ledger is hash-chained, why failures are
first-class, why isolation is the load-bearing property. The answers are in these
runs. Keep them.

*Daedalus, 2026-09-01*
