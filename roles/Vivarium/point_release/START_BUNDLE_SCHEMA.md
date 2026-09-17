# Start bundle schema -- content-addressed start conditions (point release, MUST SHIP)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s4; Amendment 1
s6.C). Design only.

## 0. Why (Campaign 3)

Every C3 result turned on a start condition that today lives in prose or in
harness code: fresh vs preserved-shelf population (C3-SFE-01), partial-credit
vs all-or-nothing evaluator (C3-SFE-08), mature source vs permuted control
(C3-SFE-04/10), injection dose and offspring cap (C3-SFE-10), foundry profile
(L2-017), rung schedule and hold rule (C3-SFE-03, L3-011), retention schedule
(C3-SFE-05). The reachability table's own run identity is (cell, bits, N, G,
E, regime, foundry, campaign_seed, rng_label, seed) -- ten fields, three of
which Vivarium cannot name today. A start bundle is the executed half of
Archaeon's preregistration, hashed, so "same design" is a byte equality and
"one thing changed" is a diff.

## 1. Relation to what exists

    sealed spec (spec_hash)     WHAT is executed: kind + payload + world.seed_root + repeat + outcome_rule + pew.
                                Unchanged. Still the world name, still the design half the executor sees.
    start bundle (bundle_hash)  UNDER WHAT CONDITIONS: everything the executed spec assumes but does not carry --
                                engine, executor version, profiles, population manifest, initial artifacts, budgets,
                                interventions declared, external dependencies. Carried on the attempt (bundle_hash) and
                                stored once per hash (viv.start_bundle).
    design_digest               == spec_hash today. The operator's rule "a changed bundle produces a NEW DESIGN DIGEST"
                                is honoured by DEFINING design_digest := sha256(spec_hash || bundle_hash) in the
                                attempt table once bundles exist (migration 006 stores both; the composite is a
                                generated column). Pre-release attempts have bundle_hash NULL and design_digest ==
                                spec_hash, which is what they meant.

## 2. The bundle (canonical JSON, sorted keys, no floats-as-strings; sha256 -> "sha256:<hex>")

    {
      "bundle_version":   "viv.start_bundle.v1",
      "spec_hash":        "sha256:...",                          the sealed spec it conditions
      "engine":           {"engine_instance_id", "engine_source_hash", "schema_version", "contract_hash"},
                                                                 from the conformance stamp; never from config
      "executor":         {"kind", "kind_contract_digest", "viv_version", "viv_base_sha"},
                                                                 kind_contract_digest = sha over the registry entry (params, result
                                                                 schema, value_checker name, axes) so a contract change is visible
      "world_manifest":   {"manifest_schema", "manifest_hash"} | "UNKNOWN",
                                                                 Daedalus s5.B envelope once it exists; UNKNOWN until then
      "evaluator":        {"profile_id", "reward_mode", ...} | "UNKNOWN",
                                                                 producer-declared; C3-SFE-08's reward_mode is the first known value
      "schedule":         {"schedule_id", "kind", "parameters"} | "UNKNOWN",
                                                                 pressure/rung/retention schedule identity (producer-declared)
      "population":       {"manifest_hash", "manifest_ref", "count", "foundry_profile", "lineage_composition",
                           "gen0_provenance", "selection_criteria", "selection_evidence_ref"} | "UNKNOWN",
                                                                 Proteus's manifest contract (s12) once defined; until then the producer
                                                                 may supply {"manifest_hash": ..., "manifest_ref": ...} only
      "foundry_profile":  "<Proteus profile id>" | "UNKNOWN",
      "initial_artifacts":[{"slot", "digest", "artifact_type", "schema_version", "source_world", "source_artifact"}],
                                                                 the spec's artifact slots + the locators, so the bundle names WHERE the
                                                                 bytes came from as well as what they hash to
      "interventions_declared": [{"intervention_id", "kind", "intended", "timing", "source_ids"}],
                                                                 intended only; realised goes in the receipt (INTERVENTION_RECEIPT_SCHEMA.md)
      "rng":              {"seed_root", "seed_derivation", "campaign_seed", "rng_label"} ,
                                                                 the first two from the spec (verbatim), the last two producer-supplied
                                                                 or "UNKNOWN"; Archaeon's CRN regime becomes reconstructable
      "budget":           {"max_seconds", "max_observations", "generations", "evaluations", "cost_envelope"},
                                                                 repeat.budget verbatim + producer-declared logical budgets
      "external":         [{"kind", "descriptor", "digest"}],   Redis/world-service/GPU descriptors for the future second executor
                                                                 class; [] today
      "factors":          {...}                                  the stratum labels (s11), verbatim, VALUES SCALAR ONLY (string /
                                                                 number / bool; Stage-2 Q2); included in the hash so a relabelled
                                                                 design is a different design
    }

Rules

    R1  every top-level key is present; a value the producer cannot know is the literal "UNKNOWN" (a string), never omitted
        and never null; two bundles that differ only by UNKNOWN-vs-value are different bundles (that is the truth)
    R2  nothing in the bundle is interpreted by Vivarium; the only fields Vivarium FILLS are engine, executor, initial_artifacts
        (from preflight) and rng.seed_root/seed_derivation (from the spec); everything else is copied verbatim from the enqueue
    R3  the bundle is sealed at ENQUEUE (producer-supplied part) and COMPLETED at CLAIM (engine/executor part); both hashes are
        stored: bundle_hash_declared (enqueue) and bundle_hash (claim). A difference between them is exactly "the environment
        differed from what the producer expected" and is visible on the attempt
    R4  a changed bundle -> a new design_digest -> a new row is REQUIRED (the producer enqueues again); Vivarium never
        mutates a bundle in place

## 3. Comparisons the bundle makes mechanical (Vivarium provides the diff, science decides the meaning)

    exact replay                          same spec_hash, same bundle_hash, new attempt (parent = the replayed attempt)
    same organisms, different pressure    diff == {schedule}
    same world, different evaluator       diff == {evaluator}
    same source population, different cap diff == {interventions_declared[i].intended.cap}
    same design, different seed           diff == {rng.seed_root} (and hence spec_hash: a different row by construction)
    matched structure, unmatched capability
                                          diff == {population.selection_criteria, population.selection_evidence_ref}
                                          with population.manifest_hash's structural summary equal (Proteus supplies it)

`viv.cli bundle-diff <attempt_a> <attempt_b>` prints the key paths that differ and
nothing else. It never says which difference matters.

## 4. Storage

    viv.start_bundle (bundle_hash text PK, bundle jsonb, first_seen timestamptz, declared_by text)
    execution_attempt.bundle_hash / bundle_hash_declared (FK)
    research_experiment_queue.bundle_declared jsonb NULL   (the enqueue-time producer part; unhashed column, hashed content)

## 5. Stage-2 self-critique hooks (answered in STAGE2_SELF_CRITIQUE.md)

    "untyped junk drawer"  -> the key set is CLOSED per bundle_version; unknown keys are refused at enqueue; extension is a
                              new bundle_version, never a free field
    "Campaign 3 vocabulary" -> evaluator.reward_mode and schedule.kind are producer strings; Vivarium validates presence and
                              type, never the value
