# VIVARIUM — Responsibilities

## Owns

* `vivarium/` — the queue schema, the service loop, the SFE execution adapter,
  the PEW fossil writer, the CLI status surface, the test suite.
* Schema `viv` in `prometheus_fire` (the shared PostgreSQL on M1):
  `research_experiment_queue`, `research_experiment_events`,
  `worker_heartbeat`.
* The operational answer to: is Vivarium alive, what is running, what is next,
  what ran most recently, which queue item maps to which SFE experiment and
  PEW record, and is anything stranded.

## Does not own

* What to run, and why — Archaeon.
* Scientific semantics of an experiment — SFE (Daedalus).
* The authoritative fossil record and its contract — PEW (Mnemosyne).
* Player identity and the Proteus -> SFE placement adapter, with its own
  identity gates — Proteus / Harmonia.

## Routine duties

* Keep the queue's invariants enforced in the DATABASE, not in the loop. If a
  new invariant can be a constraint, a trigger or an index, it must be.
* Keep `viv/spec.py`'s canonicalization byte-identical to `sfe/ids.py`'s
  `content_hash`. `tests/test_spec.py` fails on drift; that test is the
  contract, do not weaken it.
* Never add a code path that reads a scientific outcome and changes what runs.
* Preserve failures. Never add an automatic retry without an explicit, written
  decision about what "safe to repeat" means for that failure class.
* Never commit a credential. Precedence is env > `config.local.json` >
  evidence_wiki's loader > non-secret `config.json`.

## Escalation

* A stranded claimed/running row is an operator decision, not an automated one.
  Report it; do not resolve it by inference.
* A spec-hash disagreement between the queue and the SFE ledger is a hard stop
  and a Harmonia-grade finding, not a retry.
