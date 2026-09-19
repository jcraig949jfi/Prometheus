+=====================================================================+
|  CAMPAIGN 6 -- SEGMENT LOOP AND CHECKPOINT CONTRACT v0.1              |
|  Archaeon[m2-49ee5a4d]   2026-09-18   for Vivarium (segment kind),    |
|  Daedalus (engine mapping), Mnemosyne (anchors), Harmonia (receipts) |
|  Code: archaeon/campaign6/segment.py (self-test green: determinism,  |
|  continuity across a boundary, anchor coverage, planted event ->     |
|  freeze; freeze scopes COMPLETE and PARTIAL_FREEZE both exercised)   |
+=====================================================================+

THE CALLABLE
    out = archaeon.campaign6.segment.run_segment(spec, checkpoint_in)
  A pure function: the same (spec, checkpoint_in) yields the same
  out_digest (wall-clock stamps are kept in records but never enter a
  digest). Vivarium wraps it as the segment kind; a worker death mid-
  segment is recovered by re-running the segment from checkpoint_in.

SPEC (archaeon.c6.segment_spec.v1; spec_hash over all fields)
  run_id, provenance (archaeon.c6.provenance.v1: lane in the five, generator
  id+version, seed, params, parent_run, trigger, thresholds_digest),
  world {kind, knobs} (Phase 0: wse.WorldSpec; Axis W worlds register by
  kind), profile ("v0" | "repb_fizzle" | the graph profile when handed
  over), schedule [{from_gen, kind EXOGENOUS_PRESSURE|ENDOGENOUS_PRESSURE,
  label, params}], g0, g1, N, E, archive {dense_until, neighbourhood},
  thresholds (the frozen table by name), spread, seed, probe_worlds,
  planted (Phase-0 fixtures of the operator's kinds: inject_randomized,
  inject_foreign, inject_child_of -- NOT the blind ones), anchor_interval
  = 1000 (R4; not a parameter), log_scores (calibration only).

CHECKPOINT (archaeon.c6.checkpoint.v1; digest)
  run_id, generation (the NEXT generation to evaluate), eval_ordinal
  (run-scoped, monotone), rng_state (SplitMix64 int), population (organism
  records with origins; UNEVALUATED), records (lineage records of the
  population and of the last ANCESTOR_DEPTH+2 generations), lineage_pairs
  (the previous generation's T0 rows by organism id), library (archived
  elites' rows, last 256), prev_anchor_hash, history (manifest + T0 pair
  + parent id + generation for the bounded ancestry freezes need).
  Invariant proven by the self-test: [g0,g1) run as [g0,gm)+[gm,g1) gives
  the same population, eval count and rng state as one segment.

OUT (archaeon.c6.segment_out.v1)
  checkpoint_out; rows (T0 rows: {t0: proteus.behavior_fingerprint.v1,
  ext: archaeon.c6.world_ext.v1}, one per evaluation, in evaluation
  order -- the SIDECAR; never sent to the engine); anchors
  (sfe.t0_anchor.v1 per 1,000 rows AND at segment close AND at every
  escalation; prev_segment_hash chains them; coverage = every evaluation,
  checked); observations (one per ARCHIVED generation: reward min/
  median/max, fingerprint-set digest, population digest, detectors
  fired, elite id, pressure label) -- these are the engine observations;
  events (archaeon.c6.event.v1 per firing organism: verdict vector,
  fired/quiet/unable, disagreement, classifier_failure, interpretation =
  None); freezes (sfe.freeze.v1 per event: subject, parent, ancestors
  (depth 4), siblings, world, pressure window, mutation chain, T1 window
  digest, replay packet {spec_hash, generation, run_id, changed: {}},
  preserved_at, scope COMPLETE | PARTIAL_FREEZE with missing [{member,
  owner, reason, at}] -- R2: never silent, never blocks the firing);
  pressure_history; lineage_delta (child, parents, generation,
  operators); evaluations; out_digest.

ARCHIVE POLICY (in the spec, reported in every observation set)
  every generation to dense_until (default 64), then powers of two, plus
  +-neighbourhood (default 16) around every firing generation.

DETECTORS IN THE LOOP
  The eleven run on every child after its evaluation with the frozen
  thresholds from the spec; UNABLE is a verdict; a FIRE produces an event
  and a freeze in the same generation, before reproduction, before any
  interpretation. The detector table's digest is in the provenance.

REPLAY (T3; the escalation module, next)
  A exact: run_segment(spec, checkpoint_in) again, compare out_digest.
  B lineage / C world-seed / D rollback / E ablation / F transfer / G
  pressure perturbation: a fork of the spec with `changed` naming the
  one key, run from the same checkpoint_in on a scratch engine; outcome
  SAME | DIFFERENT | FAILED | NOT_ATTEMPTED per Daedalus s4.

ENGINE MAPPING (Daedalus s1)
  a experiment = spec; b artifact = checkpoint_in; c PRESSURE_* events =
  pressure_history entries; d observations = observations (batch route);
  e T0_SEGMENT_ANCHOR = anchors; f artifacts = checkpoint_out, rows
  (sidecar file), lineage_delta; FREEZE = freezes (atomic, D5); g commit.

SIZES MEASURED (self-test, N=16, E=8, 20 generations, v0/W0): 320
evaluations in 0.4 s; rows ~1.3 KB each (t0 741 B + ext 581 B); one
anchor per escalation or 1,000 rows; freeze ~10-40 KB.

OPEN (owners): sidecar locator format (Vivarium); the graph profile's
evaluate/descend/answers triple (Proteus); Axis W world kinds (Archaeon,
next); ENDOGENOUS pressure sources (Axis W/P, next).
+=====================================================================+

## Population capture (operator protection, 2026-09-19)

`nominate` accepts `window` (int, default 0) and `population` (bool, default false). When `population` is true, every
generation in `[g - window, g + window]` around each nominated generation is CAPTURED and archived densely: the
population ordering (`population_ids`), the evaluation order actually used (`eval_order`, `eval_order_mode`), and per
evaluation the slot, position, organism id, parent ids, origins, reward, the shared world state BEFORE and AFTER that
evaluation (`shared_before`, `shared_after`: pools, objects, signals as carried), the episode world digest
(action_hist, resources_touched, objects_changed, signals, died_episodes), plus the generation's ENDOGENOUS writes and
pressure label. Output key: `population_captures` (schema `archaeon.c6.population_capture.v1`). The capture changes no
number the segment computes (verified: out_digest identical with and without capture is NOT claimed; determinism of the
captured run is). The primary statistic of a pursuit stays the preregistered one; the capture is what a later reader
needs to reconstruct the event without the primary statistic.
