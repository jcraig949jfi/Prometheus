# SFE + PEW substrate reconnaissance -- capability matrix (Theophrastus, 2026-09-13)

Currency: 2026-09-13. Every row cites EXECUTABLE evidence (a code path that
was read, a test that exists, or a live call this seat made in the founding
round; ledgers under roles/Theophrastus/ledgers/). Names and documentation
were not treated as capability. Live targets: SFE eng_8a37a5d305969034d488c43e
(schema 8, source d5be5ec4b, engine_source_hash sha256:5380cb90...) and PEW
mnemosyne-evidence-wiki schema 4, fossil contract pew.fossil.v2
(recon/sfe_version_2026-09-13.json, recon/pew_health_2026-09-13.json).

Grades: NATIVE | REPRESENTABLE_WITH_EXISTING_PRIMITIVES (REP) |
AWKWARD_BUT_POSSIBLE (AWK) | MISSING | UNKNOWN.

## 1. The substrate as actually implemented (not as documented)

    SFE  (Daedalus)   SerendipityFoundry/SerendipityFoundryEngine/sfe/
         a per-world hash-chained event ledger; worlds are ISOLATION UNITS
         (one client owns a world; 403 across clients); hypotheses ->
         predictions -> experiments (sealed spec) -> work queue (claim /
         heartbeat / complete with fencing token) -> observations; forks
         at checkpoints (event prefix by reference; interventions dict
         recorded verbatim; engine checks only seed_root, sharing_policy,
         topology_group: runtime.py _ENGINE_VISIBLE_INTERVENTIONS); cross-
         world FAMILIES {campaign, analysis, comparison, selection} with a
         sealed manifest and arms; claims; measurements; budgets with
         enforcement classes; read scopes. The engine EXECUTES NOTHING: a
         worker supplies executors (executors.py WorkerLoop). Reference
         executors: evaluate_bitstring, nk_landscape_v0, nondeterministic.
         REPLAY is documented PARTIAL: a world cannot be re-run from a
         checkpoint (SERENDIPITY_FOUNDRY_STATUS.txt).
    Vivarium (execution)  vivarium/viv/
         the kind REGISTRY (kinds.py: exact parameter sets, no defaults,
         result schemas, artifact slots); the sealed spec v3 (spec.py:
         world.seed_root, work.kind+payload, outcome_rule, pew identity,
         repeat block); the SFE adapter (runner.py SfeRunner: session ->
         world named viv-<spec_hash> -> hypothesis -> experiment commit ->
         audit-envelope check -> claim -> N repeats -> N observations with
         replication=true -> resources vector); the PEW writer (pew.py
         write_encounter); the Postgres queue viv.research_experiment_queue
         with provenance columns OUTSIDE the hash (created_by, family_id,
         arm_id, replication_of, candidate_set_id, ...). Executors that
         live here: noop_v0, evaluate_bitstring, random_walk_v0,
         ca_density_v0 (Herakles semantics), artifact_probe_v1,
         cegis_boolean_v1 (Proteus semantics), eca_rule_eval_v1 (Herakles).
    PEW  (Mnemosyne)  evidence_wiki/ew/
         fossil encounters keyed (encounter_id, run_id) with a REQUIRED SFE
         anchor (event id, entry hash, seq), witnessed for ledger forks and
         session splices (service.py _witness_ledger/_witness_session);
         fossil worlds and players as version anchors; namespaces prod /
         test / fixture (scientific queries filter prod); encounter
         selectors: run_id, world_id, player_id, episode_id, namespace
         (service.py query_fossil_encounters). An `ecology` jsonb column
         exists on encounters (migration 005) and is NOT a selector.
    Archaeon (producer)  archaeon/producer -> vivqueue.submit -> the queue.
         1119 of 1150 queue rows are created_by=archaeon
         (recon/queue_census.json).

## 2. Producer / consumer flow as implemented

    Archaeon --vivqueue.submit--> viv.research_experiment_queue (Postgres)
        --claim (FOR UPDATE SKIP LOCKED)--> Vivarium daemon tick
        --SfeRunner--> SFE world+experiment+work+observations
        --write_encounter--> PEW fossil (namespace prod)
        --> queue row completed (pew_reference, result_summary)
        --> Archaeon reads ew.fossil_* / engine.db read-only

Observed state 2026-09-13: queue 572 completed / 79 failed / 492 cancelled
/ 1 queued; the Vivarium consumer was NOT alive (last heartbeat 2.6 h old,
pid 26164, build fb7aa5bed) -- `viv.cli health`. Completed rows by kind:
ca_density_v0 150 (ALL n_cells=149, steps=320, ic_density_set=[null]),
eca_rule_eval_v1 256 (all n_cells=7, steps=8), cegis_boolean_v1 97,
evaluate_bitstring 61. 25 families, 21 arms, 134 candidate sets, 0 rows
with replication_of.

Theophrastus's founding-round path (chosen because the daemon was down and
because the charter names this seat an ALTERNATIVE consumer): own SFE
client (cli_74b888ed5ee82365bf6d5895, registered 2026-09-13), Vivarium's
SfeRunner + executors used as a LIBRARY (adapter.py), PEW namespace
`theophrastus`. The queue was not written; the daemon was not started.
Same engine instance, same build, same kind contract, same executor.

## 3. The matrix

    capability                       grade   evidence
    ------------------------------   -----   -----------------------------------------
    mechanism identity               NATIVE  for THIS kind: payload.rule_hex inside the
                                             sealed spec (spec_hash); PEW players is a
                                             selector. NOT typed as "the mechanism" by
                                             the substrate: which payload key is the
                                             mechanism is producer knowledge
                                             (ecology.py had to assign it). See REQ-002.
    mechanism composition            MISSING for ca_density_v0 (one rule_hex, exact
                                             params; kinds.py). cegis_boolean_v1 has
                                             artifact slots (component_library,
                                             source_pack) = composition BY ARTIFACT for
                                             that kind only. M1+M2 for CA rules has no
                                             executable form. See REQ-003.
    pressure identity                REP     ic_density_set / n_ic / success_criterion
                                             are execution inputs; identity = hash of
                                             the subset (cell.py Pressure.identity).
                                             Substrate has no "pressure" type. REQ-002.
    pressure magnitude / regime      NATIVE  for this kind (a declared density set is a
                                             regime; [null] the unbiased ensemble).
    world identity                   NATIVE  two senses, both real: SFE world = ledger
                                             isolation unit (world_id, seed_root, head
                                             hash); ecological world = (n_cells, steps,
                                             radius) inside the payload, hashed by the
                                             producer (World.identity). The SFE world is
                                             one-per-experiment (viv-<spec_hash>), not a
                                             persistent environment.
    world intervention               AWK     SFE fork.interventions is verbatim; the
                                             engine verifies only seed_root /
                                             sharing_policy / topology_group and flags
                                             NO_EFFECTIVE_INTERVENTION on a declared
                                             before/after pair (runtime.py
                                             _intervention_findings). Payload-level
                                             interventions are invisible to the engine;
                                             the producer must check them (controls.py
                                             C5 INTERVENTION_NOOP on execution_hash).
    branch / lineage relation        AWK     SFE lineage is per-world (fork/import).
                                             PEW fossil_players carries lineage_id /
                                             parent_player / generation for Proteus
                                             organisms; a RECOVERED SPECIMEN'S published
                                             lineage (hand-designed vs GA-evolved) has
                                             no substrate object; it lives in this
                                             seat's ledger with an evidence pointer.
    intervention identity            REP     transform is an execution input (NATIVE for
                                             this kind); a general intervention type
                                             does not exist. C5 covers no-ops.
    controlled neighbouring cells    REP     SFE families kind=comparison with sealed
                                             arms; Vivarium family_id/arm_id. Founding
                                             round kept contrasts in its own ledger and
                                             did NOT register SFE families (backlog
                                             THEO-05); this is a gap in THIS seat's use,
                                             not in the substrate.
    producer provenance              NATIVE  queue columns outside the hash; PEW
                                             producer block; SFE actor=client_id;
                                             engine identity on every row.
    consumer provenance              NATIVE  worker_id, client id, engine instance and
                                             build hash on every row and fossil
                                             (rows.jsonl consumer / engine fields).
    exact experimental coordinates   NATIVE  spec_hash is the grouping surface for
                                             execution inputs; the 5-axis coordinate is
                                             DERIVED (cell_id) and not substrate-typed.
    deterministic replay             REP     labelled per result (BIT_DETERMINISTIC);
                                             re-submission of the identical sealed spec
                                             in a fresh world reproduced the digest 3/3
                                             on two cells (ledgers/cells.jsonl
                                             replay_check). World re-execution from a
                                             checkpoint: MISSING (documented).
    negative / null results          NATIVE  outcome FALSIFIED; SFE failures; fossils of
                                             FAILED runs carry failure_class; PEW
                                             register_failure. Dead terrain is ledger-
                                             local (dead.jsonl); not a PEW object.
    resource budgets                 NATIVE  SFE budgets (enforcement classes), repeat
                                             budget (max_seconds/max_observations,
                                             BUDGET_EXCEEDED), C4 resource vector on
                                             every row; explorer-level Budget (C10).
    cross-producer coordinate query  MISSING PEW encounters cannot be selected by
                                             ecological coordinate; `ecology` jsonb is
                                             stored but not queryable. REQ-001.

## 4. Exact gaps preventing the five-axis ecology from being represented or executed

    G1  No substrate type distinguishes mechanism / world / pressure /
        intervention parameters inside a kind's payload. The producer
        assigns axes by hand (ecology.py). Two producers can assign them
        differently and PEW cannot tell. -> THEO-REQ-002 (Vivarium).
    G2  PEW cannot answer "every encounter at ecological coordinate X"
        across producers; `ecology` is stored, not selectable; players are
        a selector but the bench wrote no players for ca_density_v0
        (recon/queue_census.json; queue query 2026-09-13) and this seat
        wrote name-based ids ("evca:GKL"). -> THEO-REQ-001 (Mnemosyne)
        + player-id convention question (Herakles).
    G3  Mechanism COMPOSITION for CA rules does not exist as an executable
        kind; INTERACTION / ANTAGONISM probes (charter VIII "M1, M2, M1+M2,
        neither") cannot be run. -> THEO-REQ-003 (Proteus, cc Herakles/Nyx).
    G4  Branch relations for recovered specimens have no substrate home;
        the seat's ledger carries them with evidence pointers. Not filed as
        a REQ this round: PEW fossil_players.lineage_id / parent_player may
        suffice once a player-id convention exists (G2).
    G5  World re-execution from a checkpoint is MISSING in SFE (documented);
        replay by re-submission suffices for this ecology. Not filed.
