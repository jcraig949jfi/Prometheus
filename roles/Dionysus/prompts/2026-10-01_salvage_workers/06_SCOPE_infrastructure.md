# Scope 6: execution, provenance and institutional infrastructure

Slots to fill: the KERNEL's runner, single queue and lease mechanism,
single ledger and receipt schema, sealed-world broker, derived index and
dashboard, operator digest, token and energy meters (RSE_ARCHITECTURE.md
sections 4 and 10).

Requirement areas to read: section 1; PROV-01 to PROV-10; REPR-01 to
REPR-07; COMP-02, COMP-04, COMP-05; INF-01 to INF-07; ENRG-01; HUM-01 to
HUM-05; MEAS-06, MEAS-11; ANTI-01.
Also read docs/phase3/intake/ixion/REPORT.md sections 5, 6, 7, A, C, D, E
and docs/phase3/intake/ixion/inference_dependency_map.md.

Components:

1. Agent Fabric v0.2 (fabric/): store, worker, script executor, leases,
   events, lease_compat, the claude executor sandbox, promexec. Dossier:
   ixion/seats/Odysseus.md.
2. SFE (SerendipityFoundry/SerendipityFoundryEngine/): the hash-chained
   ledger, prediction-before-observation, executors, verify_deploy.py.
   Dossier: sisyphus/seats/Daedalus.md.
3. Vivarium's data plane: the Postgres experiment queue, blind executor,
   sealed spec, quarantine-by-listing, attempt replay, ordered outbox.
   Dossier: sisyphus/seats/Vivarium.md.
4. prometheus/toolbox receipts and admission (only the provenance side;
   worlds belong to scope 3). Dossier: sisyphus/seats/Bellerophon.md.
5. primordial RowWriter (primordial/fabric/rows.py) and the primordial
   lease and CPU-token mechanisms. Dossier: sisyphus/seats/Nestor.md.
   Do NOT open nestor_secrets.
6. comms/ (messages, receipts, task queue, manifest.py, identity.py) and
   evidence_wiki/ew (store gates, db.py identity-attested connector,
   campaign reader, projections, search). Dossiers: ixion/seats/
   Mnemosyne.md, Aporia.md. Do not open evidence_wiki/config.json or any
   file holding credentials.
7. atlas/ (schema, migrations, harvesters, comb rules, report) and
   achilles/census (rules, registry, render, run receipts). Dossiers:
   ixion/seats/Atlas.md, Achilles.md.
8. The reporting loop: scripts/intelligence_loop.py, portfolio_monitor.py,
   metis_portfolio.py (deterministic brief), send_brief_email.py.
   Dossiers: ixion/seats/Pronoia.md, Hermes.md, Metis.md.
9. Small deterministic instruments: archaeon/workspace.py (the canonical-
   checkout guard), Alethelia (agents/alethelia/), productive_liveness.py,
   null_bound.py, Metis compose.py (cheapest partitioning discriminator),
   Cyclops's prepost_check.py, Cosmos's holdout broker (code only; do NOT
   open holdout directories), prometheus_llm (the single model-call choke
   point). Dossiers: ixion/seats/Alethelia.md, Pronoia.md, Atalanta.md,
   Metis.md, Cyclops.md; tantalus/seats/Cosmos.md.

For each, answer from the source:

- what it guarantees, and by what mechanism (database constraint, hash
  chain, process boundary, convention);
- what it depends on that is not in the repository (a Postgres instance on
  one host, a scheduled task on one laptop, credentials on one machine);
- whether it runs today, on which host, and when it last did;
- whether a campaign runner could use it without a model session in the
  loop;
- its receipt or row schema (list the fields), and whether those fields
  cover: code commit, configuration hash, seeds, component versions, host,
  row hashes, verdict with ruler hash, cost meters;
- whether anything anywhere records token use, model identity per call, or
  energy. If prometheus_llm is the single choke point, say exactly what it
  logs per call.

Also answer for the whole scope:

A. Hosts. List every machine the program has used, with what the tree
   records about its hardware and role (M1, M2, M3, M4, ELSA, ubu001,
   ubu002, BUCKKEEP, GANDALF, DESKTOP-RUAPVAI, rented GPUs). Quote the
   file that records each fact.
B. Which ONE queue, ONE ledger and ONE lease mechanism would be the least
   work to make canonical for deterministic campaigns on M1, and what
   each of the others would cost to retire.
C. What exists that could generate a weekly operator digest from receipts
   with no model call.

The decision Dionysus has to make: which infrastructure is kept as the
kernel's base, which is extracted, and which institutional machinery has no
Phase 3 role.
