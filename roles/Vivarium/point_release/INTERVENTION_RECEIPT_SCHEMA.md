# Intervention receipt schema -- intended vs realised (point release, MUST SHIP)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s5; Amendment 1 s6.G).

## 0. Why (Campaigns 1-3)

    C1 L-007  a residue channel was INERT (tabu_hits 0 in 9/9 rows) and nothing flagged an intervention that never applied
    C3-SFE-07 the opcode-neighbourhood intervention DID apply (567-573 rewrites per treated run) -- that number is what let
              the CAPABLE_NEGATIVE stand
    C3-SFE-10 takeover is mechanics: dose 1 of 200 suffices; the offspring cap is the only lever; realised origin share
              per generation is what separated "small perturbation" from "half the population replaced"
    L3-016    (blocks future runs) "cap or declare replacement"

The producer chooses the intervention. The world/engine or the kind applies
it. Vivarium records the pair -- intended and realised -- as a fact beside the
attempt, so "applied 0 of 4" is a column, not an inference from trace shape.

## 1. The receipt (one per intervention per attempt; viv.intervention_receipt)

    receipt_id              uuid PK
    attempt_id              uuid FK -> execution_attempt
    step_id                 uuid NULL FK -> execution_step          the step during which it was applied
    intervention_id         text NOT NULL                           producer's id (from the bundle's interventions_declared); UNIQUE
                                                                    (attempt_id, intervention_id)
    intervention_kind       text NOT NULL                           open vocabulary, producer-declared; known values today:
                                                                    import | substitution | lesion | schedule_change | artifact_injection |
                                                                    opcode_rewrite | reset | cap
    intended                jsonb NOT NULL                          {"count"|"dose"|"value"|"share"|"cap": ..., ...} verbatim from the bundle
    realised                jsonb NOT NULL                          the same keys as measured by the applier; a key intended but not
                                                                    measurable is the literal "UNKNOWN" (never omitted)
    logical_time            jsonb NULL                              {"generation": n} | {"tick": n} | {"step": n} | "UNKNOWN"
    target                  jsonb NOT NULL                          {"world_id", "population_ref" | "UNKNOWN"}
    supplied                jsonb NOT NULL DEFAULT '[]'              entities/artifacts supplied: [{"digest"|"organism_id"|"lineage_id", ...}]
    source_ids              jsonb NOT NULL DEFAULT '[]'              where they came from (source world/artifact/attempt), verbatim
    result                  text NOT NULL                            APPLIED | PARTIAL | NOT_APPLIED | REJECTED | UNKNOWN
    reason                  text NULL                               drop/rejection reason as the applier gave it (engine 403, cap hit,
                                                                    entity missing, ...)
    post_ref                jsonb NULL                              reference to the post-application observation/receipt (obs id, artifact
                                                                    digest, trace row ref) -- a POINTER, never a copy of the trace
    recorded_at             timestamptz NOT NULL DEFAULT now()

`result` is DERIVED mechanically and only from the two numbers, never from
science: APPLIED iff every intended numeric key equals its realised key;
PARTIAL iff some realised < intended and > 0; NOT_APPLIED iff all realised
== 0; REJECTED iff the applier refused; UNKNOWN iff any realised key is
UNKNOWN. The derivation applies to NUMERIC keys only (Stage-2 Q3): a
receipt with no numeric key (a schedule change) is APPLIED iff the applier
reported success, else UNKNOWN. A world designer who wants "applied at half
dose is fine" reads PARTIAL and decides above.

## 2. Who writes it

    kind-internal interventions (the executor applies them inside run())  -> the executor returns an `_interventions` channel beside
                                                                            `_truncated`; executors.run pops it and Vivarium writes the
                                                                            receipts; a kind that declares interventions in its contract
                                                                            MUST return the channel (validator refuses otherwise, same
                                                                            pattern as truncation declaration, THEO-REQ-004)
    engine-side interventions (imports via /v2/.../import)                -> Vivarium's preflight/import step writes the receipt from the
                                                                            engine's answer (import_artifact_id, origin, 403 reason)
    producer-side (Archaeon's harness applies it in-process)              -> the harness posts the receipt through the same table via the
                                                                            envelope (a qualification-run requirement, s16); Vivarium
                                                                            stores it verbatim and marks writer = producer

`writer` column: executor | engine | producer. A receipt written by the
producer about its own intervention is provenance, not verification; the
column says so.

## 3. Standard summary in the attempt receipt (SHOULD, s18)

    interventions: {"declared": n, "applied": a, "partial": p, "not_applied": z, "rejected": r, "unknown": u}

so the "4 intended, 0 applied" case is one line on the receipt and one
predicate an analyst can grep for.

## 4. What this is not

Not a dose chooser, not a takeover detector, not a lineage-share computer:
`realised.share` is a SUPPLIED measurement (C3 group F computes origin
share per generation in the trace; the applier reports the value at
application time). Vivarium stores it. FLOOR/SHELF/SUMMIT, "takeover",
"replacement vs transfer" are projections above.

## 5. Generality check (Stage 2, "survives future worlds?")

The schema names no organism, no genome, no generation as a type: logical
time is a tagged object, targets and supplied entities are id lists with
producer-owned key names, kinds are strings. A world with message loss
(intervention_kind = "drop", intended {"share": 0.1}, realised {"share":
0.097}) fits without a schema change.
