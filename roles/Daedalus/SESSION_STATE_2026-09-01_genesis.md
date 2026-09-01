# Daedalus — Session State — Genesis
## Date: 2026-09-01

The session in which the Daedalus role was created and the Serendipity Foundry
Engine was stood up for multi-experimenter use, with Harmonia (M2) as first user.

## What exists now

- **Engine live**: `https://192.168.1.202:8811` (`/v2`, TLS), always-on via the
  `SFEngine` scheduled task. `GET /v2/version` → `{"api":"v2","schema_version":1,
  "runtime":"serendipity-foundry-sfe"}`. DB at `SerendipityFoundryEngine/var/engine.db`.
- **Client** complete: stdlib `sfclient`, `config/` (profile + public cert),
  `examples/` (`run_sample.py`, `run_worker.py`), docs (README/CONNECTING/API),
  and two live test harnesses.
- **Role** created at `F:\Prometheus\roles\Daedalus`: CHARTER, RESPONSIBILITIES,
  GENESIS, RUNBOOK, this state file, and HARMONIA_ONBOARDING.
- **Genesis preserved**: D6/D6A/D7/D8/D10/D10phase2 kept as-is under
  `SerendipityFoundry/` (see GENESIS.md). `gen2/` removed from `F:\SerendipityD`
  (commit `ba879da`); its history is preserved at `dd006cb`.

## Isolation: audited, fixed, tested (the headline of this session)

Before onboarding a second experimenter, isolation was verified two ways.

**Adversarial code audit** (6 independent auditors, one per surface). Verdicts:
event-ledger and SQLite-transaction integrity **sound** (per-world hash chain;
`BEGIN IMMEDIATE`; no double-claim, no torn write). Two **critical live breaks**
found, plus defense-in-depth gaps and two low-severity existence oracles.

**Fixes applied** (all in `sfe/`, all outside the D-13 allowlist — pin unmoved):

1. **Work-queue cross-claim (CRITICAL → fixed).** An unscoped `POST /v2/work/claim`
   (`world_id=None`) had no owner filter and could hand experimenter B a work
   item from A's world (payload disclosure + lease/queue starvation). Fix:
   `claim_work` now takes `client_id` and filters `d.client_id=?`; the API always
   passes the caller's id. Regression: `test_work_claim_is_client_scoped`.

2. **Artifact import exfiltration (CRITICAL → fixed).** `import_artifact` checked
   only the destination policy (B-controlled) and read the source world by id with
   no source consent — B could pull A's artifact bytes knowing the ids. Fix:
   cross-client import now requires an **explicit bilateral topology share** (both
   worlds in the same non-null `topology_group` AND the source policy emits the
   kind); otherwise a uniform `AccessDenied` is raised **before** the artifact is
   looked up, so no id existence oracle remains. Regression:
   `test_import_artifact_is_cross_client_isolated`.

3. **Defense-in-depth (HIGH → fixed).** `complete_work` / `fail_work` /
   `heartbeat` now enforce world ownership at the runtime layer (via `client_id`),
   not only in the API wrapper — the check now lives where the ledger write
   happens.

**Accepted + documented (not fixed):** a `404`-vs-`403` world-existence oracle on
`/v2/worlds/{id}/*`. For cooperating colleagues on a trusted LAN with opaque
random ids, this reveals only existence (never data) and does not enable
stomping; keeping `403` gives an honest "that's another experimenter's world"
signal. Revisit if the threat model ever becomes adversarial tenants.

## Verification results (live, this session)

- Engine suite: **32/32** pass (incl. the two new isolation regressions).
- Client capability harness: **12/12** pass (live).
- Two-experimenter isolation (concurrent, live): **7/7** pass —
  `test_harness/isolation_two_experimenters.py`.
- D-13 pin: `source_tree_hash 50b5c232…` **unchanged**; D-13 service on 8799 up
  and untouched.
- Firewall: `SFEngine (LAN)` admits `192.168.1.0/24` on 8811; Engine exe not
  shadowed by any Block rule → M2 (192.168.1.191) reachable.

## What's next

- Hand Harmonia the onboarding prompt (`HARMONIA_ONBOARDING.md`); confirm her
  first `GET /v2/version` and world round-trip from M2.
- Re-run the standing verification battery after any Engine change or before any
  new experimenter joins.
- If/when experimenters need to *share* results, use the bilateral topology-group
  mechanism (both opt in) rather than loosening the default ISOLATED.

*Daedalus, 2026-09-01*
