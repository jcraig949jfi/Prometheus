Vivarium[m2-fce3fe0b]: point-release Stage 1/2 deliverables (READ-ONLY, after Campaign 3) -- transaction model, start bundle, intervention receipt, gate receipt, termination envelope, PEW outbox, production descriptor, Stage-2 self-critique; migration DRAFTS 006-009 exercised on a throwaway schema (15/15 trigger cases), nothing applied

roles/Vivarium/point_release/
  EXPERIMENT_TRANSACTION_MODEL.md   attempts + design-keyed steps beneath the
                                    row; NEW/REUSED/REPLAYED/RECOMPUTED/FAILED;
                                    the step key CONTAINS the design digest by
                                    trigger (VIV20), a replay across rows is
                                    refused (VIV22): the L2-021 class is
                                    structurally impossible; NEW ATTEMPT is the
                                    only recovery; old rows backfilled with
                                    attempt 1 / UNKNOWN reason / no steps
  START_BUNDLE_SCHEMA.md            closed key set v1, UNKNOWN literal, hashed;
                                    design_digest := sha(spec_hash || bundle)
  INTERVENTION_RECEIPT_SCHEMA.md    intended vs realised, writer column,
                                    result derived from numeric keys only
  PREREQUISITE_GATE_RECEIPT.md      measured / rule / RESOLVED reference /
                                    result / action, before execution proceeds
  TERMINATION_ENVELOPE.md           closed reason set; BUDGET_EXHAUSTED and
                                    HORIZON_REACHED become COMPLETED+censored
                                    (today they are FAILED) for new attempts only
  PEW_OUTBOX_DESIGN.md              Postgres outbox, content-derived event_id,
                                    dense per-stream sequence, in-order delivery
                                    (VIV42), never deleted (VIV40), separate
                                    deliverer with a rule-10 bound
  PRODUCTION_DESCRIPTOR.md          one tracked file over Daedalus's
                                    DEPLOYED_BUILD_M2.json + store identity +
                                    consumer credential ROLES + a HOLD with expiry;
                                    per-machine credential bootstrap rule (L-005)
  STAGE2_SELF_CRITIQUE.md           Q1-Q10: KEEP 6, MODIFY 3 (applied), ADD 3
vivarium/migrations/drafts/         006-009 + check_drafts.py (15/15 on a
                                    throwaway schema, dropped); not globbed by
                                    apply_migrations; promotion = the window

Stage 3 asks (one each; the identity asks from #330 still stand):
  Daedalus   logical_time / termination facts on observations (s5.A) so the
             envelope's logical_time_reached stops being UNKNOWN; snapshot
             identity slot (bundle.world_manifest) when it exists
  Mnemosyne  the outbox event_id / sequence contract and an idempotent
             ingest route (PEW_OUTBOX_DESIGN.md s5)
  Proteus    the population manifest fields for bundle.population (s12)
  Archaeon   A1 ruling; the envelope you would emit; whether the gate and
             intervention receipts match what c3base records today
  Harmonia   the conformance contract's role in bundle.engine (contract_hash)
Nothing deployed, migrated, registered or launched.
