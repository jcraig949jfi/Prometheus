VIVARIUM — EXECUTION ORDER 2026-09-08 (from the operator)

Baseline: archaeon/v0 at 5191c3383 (merged with main). Your requests are in
roles/Vivarium/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md (three sections;
the later ones supersede). Tests and acceptance per package are in
archaeon/docs/expansion/WORK_PACKAGES.md. You are the integrating owner for
every item below; Daedalus, Herakles and Proteus supply libraries and
contracts, not decisions.

DO NOW, IN THIS ORDER
1. START THE CONSUMER on this machine under the existing policy and budget.
   Nothing in the queue has executed since 2026-09-06 11:07. Report the PID,
   the lane it serves, and the first claimed row.
2. WP-0b. Remove the `not kind.stateful` term from degenerate_by_construction
   under state=reset (viv/spec.py:409-412). Tests 0b-a/b/c.
3. WP-0f. Add Kind.result_schema (field -> type; required/optional; vector
   bounds; supported reductions) for noop_v0, evaluate_bitstring,
   random_walk_v0; validate executor OUTPUT against it; `cli kinds` prints it.
   Tests 0f-a/b/c. Archaeon's builder defers to it the moment it exists.
4. Rebase your campaign branch (worktree-vivarium-campaign-e1-e6-e16) onto
   the engine at be65b0efa or later: your SFE copy is the pre-642736763 v7
   and still reads the arm from the spec.

THEN, WHEN THE LIBRARIES LAND (each independent)
5. WP-0c with Daedalus's sfclient.family_member(arm=...): pass the queue
   arm_id through so family_members.arm and the PEW design_hash carry one
   value. Cycle: design binding BEFORE execution -> terminal observation ->
   attestation -> projection; a delayed projection needs no envelope of its
   own and triggers no execution. Tests 0c-a..e. Acceptance: one arm-bound
   round trip with readback and ordering evidence.
6. Wrap Herakles's CA library as kind ca_density_v0(rule_hex, radius,
   n_cells, steps, n_ic, ic_density_set) -> accuracy, misclassified_ic[],
   spacetime_digest. Stateless across executions. Parity fixture vs the
   library (0f-b).
7. Register Daedalus's nk_landscape_v0(bits, length, k) kind + schema when
   A1 lands; parity fixture.
8. Execute the human-issued batches Archaeon issues for A3-acq and C3
   (source_reason='human', no cadence ordinal). They are minutes of work.

NOT ASKED: scheduling intelligence, template admission, any scientific
interpretation, external_backend_v0 (waits on WP-P0, which waits on the
operator's authorisation).

REPORT FORMAT (one packet per item): item ID; source and implementation
revisions; commands run; expected vs observed; fixture hashes; unresolved
limits; next permitted action. Tests not run marked as such.
