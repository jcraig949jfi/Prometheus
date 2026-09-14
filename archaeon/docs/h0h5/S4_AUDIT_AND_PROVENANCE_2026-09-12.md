# S4 -- four-loop audit and thousand-H provenance (written while the batch runs; independent of its outcome)

## Four-loop audit of every component S4 touched

    component                              loop   crossings (source -> destination)                         declared?
    ------------------------------------   -----  ---------------------------------------------------------  ---------
    evaluate_bitstring executor (scores)   1      none in S4: the synthetic harness scores a probe against    n/a (LOOP 1 is
                                                  the hidden target exactly as the executor would; no          untouched)
                                                  producer alters a running organism's moves
    archaeon/producer/fossil_inference.py  2      evidence IN: fossils (bits, score) -> feasible set           yes (contract)
    archaeon/producer/acquisition.py       2      evidence IN: feasible set + probe -> partition, ER           yes
    archaeon/producer/s4_producers.py      2      evidence IN (G, W, M only): the arm's own fossils;           yes: Proposal.
                                                  proposal OUT: probe + provenance -> LOOP 4                     evidence_policy,
                                                  U: NO evidence in (signature has no fossils)                   snapshot_id, ancestry
    S4_RUNNER_2026-09-12.py (harness)      4      holds the hidden target; executes the proposal; returns       yes: the only place
                                                  the exact score; keeps one evidence list PER ARM              the target exists
                                                  (no cross-arm sharing)
    S4_PREREG_2026-09-12.json              3      Keeper-set question, thresholds, budgets, regimes -> LOOP 2   yes: preregistered,
                                                  (as rules), verdict -> LOOP 3 (as a report)                    committed before rows
    B1 read grant (fossils_b1.py)          2<-4   production fossils -> Archaeon (not used by S4's synthetic   yes: grant, scope,
                                                  batch; used only by the eligibility census)                   tick record
    comms posts                            2->3   reports and delegations to seats / operator                   yes

    VIOLATIONS: 0 found.
    - no producer reads hidden organism/target state: enforced by signature
      (test_cheat_no_producer_can_receive_the_hidden_target) and by a spy
      on the partition function in the S3 oracle tests (inputs are fossils
      and probes only).
    - no ecological selector controls an organism's internal trajectory:
      a proposal is a whole probe; the executor's scoring of it is not
      steered mid-run; there is no channel from the producer into the
      executor except the sealed probe.
    - no runner silently chooses which hypothesis deserves continuation:
      the harness executes exactly the probe it is handed, in the arm's
      order, for the preregistered budget; it selects nothing.
    - no Keeper-derived answer appears as experimental evidence: the
      thresholds and budgets are rules on the record; the verdict is
      computed from rows; no operator statement is a fossil.
    - the arms' evidence states are separate Python lists built from the
      same initial evidence; a fossil returned to one arm is never
      appended to another (the counterfactual analysis evaluates OTHER
      producers' proposals on G's state explicitly and labels them so).

## External channel (Phase 7)

The contract's EXTERNAL slot is preserved and recorded, not built:
archaeon.producer.s4_producers.external_channel(). Harmonia already acts
as an external producer in production: 979 of the 1,029 rows in the
raw tenancy corpus on 2026-09-12 were harmonia-m2 client worlds (names
of the form t2-A4-K0-i0-k1), issued without consuming Archaeon's
fossils. A Harmonia-issued spec satisfies the contract with producer_id
harmonia, evidence_policy EXTERNAL, evidence_snapshot_id None, probe =
its sealed spec, ancestry = its own preregistration reference. What is
NOT on those worlds today is that reference as a durable field: the
ledger carries the client identity, not the preregistration path
(searched roles/Harmonia for the world-name pattern: no match). That is
the one field an external producer would have to add to be reconstructible
by id -- Harmonia's to place, and no change to its contract is needed to
participate. Harmonia was not woken for this season; U is the PEW-blind
control.

## Thousand-H readiness: the minimum provenance the evidence actually required

Derived from what the S1 ancestry join, the S1/S3/S4 readouts and the
producer contract NEEDED, not from what would be tidy:

    field                       required by                              already on production rows?
    -------------------------   --------------------------------------   ---------------------------
    producer_id                 telling U/G/W/M (and harmonia) apart     yes (created_by + policy_version)
    producer_version            re-deriving a proposal after code moves  partly (policy_version@TICK_VERSION;
                                                                          no source hash) -> add
    evidence_policy             PEW_BLIND vs PEW_CONSUMING vs EXTERNAL    partly (selection_basis) -> name it
    evidence_snapshot_id        "same probe, different history" events   NO on tick rows (corpus hash is a
                                                                          moving window) -> the fossil ID LIST
                                                                          or window bounds; S1 rows carry both
    probe / spec_hash           identity of what ran                     yes (spec_hash, queue + engine)
    seed_inputs                 determinism                              yes (policy.seed_inputs)
    objective + tie_class       why THIS probe and not its equals        NO on tick rows -> add (S4 has it)
    ancestry (fossil ids)       the E1 edge of the loop                  yes on the canary/S1 (chosen_region,
                                                                          source_fossil ids); no on tick rows
    preregistration ref         the rule that licensed the row           yes on campaign rows; no on tick rows
    pair / campaign / arm       matched comparison identity              yes (campaign_set, family_id, arm_id)

    Invariants the evidence proved necessary:
    1. a hash of a moving window is not an evidence identity; an id list
       (or window bounds on an existing sequence field) is;
    2. producer identity must include the code version, or a re-derived
       proposal cannot be checked;
    3. two rows with equal probes and different evidence snapshots are
       different events and must stay distinguishable;
    4. ties must be recorded as classes, or a later reader will treat a
       tie-break as a preference.
    Nothing else is claimed necessary; no schema change is proposed now
    (base rule: keep season labels in season evidence until a consumer
    demands promotion).
