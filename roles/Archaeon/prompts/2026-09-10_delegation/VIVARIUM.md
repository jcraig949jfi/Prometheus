VIVARIUM -- PUBLISH THE PHASE-2 ARTIFACTS, THROUGHPUT, TWO KINDS, BRANCH
(operator 2026-09-10, via Archaeon; see 00_COMMON.md for authority)

State: cs-c3-2 is at 86/150 on your consumer (PID 29884), 0 failed; the
per-row time went from ~1.5 min to ~4 min after 10:00. cs-h1h0-1-p1 is
complete (24/24). Archaeon's phase-2 packs are built and unissued:
archaeon/docs/h0h5/H1H0_PHASE2_PUBLISH_RECEIPT_2026-09-10.json (11
artifacts: 10 failure_input_set packs + 1 component_library instrument
control; canonical bytes and slot digests inside).

DELIVER
1. PUBLISH the 11 artifacts into a PRODUCER world on the production engine
   (the same path your h1_h0_alpha_demo used: create_session, create_world
   with sharing_policy EXPLICIT_IMPORT_ONLY, client.artifact(world, type,
   canonical bytes, expected_blob_hash=slot.digest)). Commit
   archaeon/docs/h0h5/H1H0_PHASE2_LOCATORS_2026-09-10.json as
   {digest: {"source_world": ..., "source_artifact": ...}} for all 11, plus
   the producer world id and the engine instance. Archaeon then issues
   phase 2 (72 rows) on the operator's standing word -- no further ask.
2. THROUGHPUT: say what slowed cs-c3-2 after 10:00 (engine, PEW, host
   contention, lease renewals) with the numbers from your logs, and the
   expected completion time. No change to the consumer unless it is
   failing.
3. eca_rule_eval_v1: register Herakles's kind (herakles/eca, class map
   fixture 8bf7bc9036...) as a Vivarium kind with result_schema, following
   the ca_density_v0 pattern (wrapper decides nothing; the library owns
   conventions). If Herakles has not handed a kind spec, say so and name
   the missing piece. This unblocks H5's templates (Track C).
4. success_criterion with an ATTAINABLE RANGE for random rules: 40 of 40
   random tables in cs-c3-2 score 0.0 under both `stable` and `at_T`
   (100/100 ICs incorrect). Expose, as a THIRD declared criterion value
   only (existing values untouched), a per-cell measure Herakles defines
   (see his prompt item 5), so a future corpus can be issued on a scale
   where random rules are not all zero. Do not change cs-c3-2.
5. BRANCH: origin/vivarium/v0-2026-09-05 has commits not on main (last
   2026-09-09). Merge what belongs, then delete it, or state why it stays.

REPORT: SHA on main and path per item; exact commands; the locator file
first.
