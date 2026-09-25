+======================================================================+
| AGE / AETH-01 -- C1 SINGLE-DEFECT CLEANUP COVERAGE REPAIR              |
| Author: Augment Agent; Windows workstation                            |
| Date: 2026-09-22; For: HITL and external reviewers                    |
| Status: C1_REPAIRED; AGE remains BOUNDED_REPAIR_BEFORE_B3 otherwise   |
| Self-contained result; repository needed only to rerun the tests     |
+======================================================================+

----- 0. Scope -----

This is the single, explicitly authorized repair of Review 04's C1 blocker
(Aether/AETH-01/INDEPENDENT_CLOSURE_REVIEW_04.md), and nothing else. No
general cleanup architecture was reopened, no B3 operational proof, no R1
admission, no RunPod launch, no provider calls, no image build. Provider
spend: $0. Repository: jcraig949jfi/Prometheus. Branch:
aether/base-role-adopt-2026-09-19. Repaired against reviewed HEAD
abe63ef42476b140283fd8e52869b929b86a7dc0 (Review 04 remained unmodified there).

----- 1. C1 recap -----

Review 04 found that cleanup_evidence.aggregate() could return
OPERATIONAL_CLEANUP_CONFIRMED even though a controller-known, exact-owned
pod ID never occurred in the independent reaper's report at all -- the
reaper's empty LIST-only horizon was accepted as sufficient even for an ID
the reaper never learned about and therefore never issued the falsifying
GET against. Appendix A's reproduction: local confirms pod_1 (terminated),
the reaper's LIST stays stale/empty for 61 rounds (zero GET, zero DELETE
calls, report["owned_ids"] == []), yet the direct GET pod_1 result is
RUNNING. The pre-repair combiner nonetheless sealed
OPERATIONAL_CLEANUP_CONFIRMED, authoritative_local_state=true, exit_code=0.

----- 2. Minimum repair implemented -----

Aether/runpod/aeth01_canary/cleanup_evidence.py aggregate(): every ID present
in the local (controller) report's owned pods must also occur in the
reaper's report before known_owned_cleanup_status can be CONFIRMED. An ID
the reaper alone discovers (present only in the reaper's report) remains a
legitimate independent discovery and is NOT required to be locally known --
the requirement is asymmetric, matching the model's "union all known IDs;
do not lose IDs by trusting only one source" and the review's "never waive
this for locally confirmed IDs."

    coverage_ok = set(local_pods) <= set(reaper_pods)
    known_ok = not ambiguous and coverage_ok and all(
        pods[pid]["cleanup_confidence"] == "CONFIRMED"
        for pid in owned_ids for pods in (local_pods, reaper_pods) if pid in pods)

No new handoff file, CLI flag, or reaper-side seeding mechanism was added.
combine_operational_cleanup() already reconstructs the local outcome from
authoritative durable state.json under RunLock (existing equality check at
age_controller.py) before ever calling aggregate(), so this pure per-ID
coverage check is sufficient: a forged/omitted local owned_ids list is
already caught by that pre-existing reconstruction, independent of this fix
(see C1-J below). This is the "at minimum" repair the review authorized,
deliberately not the wider proactive known-ID handoff/seeding option.

----- 3. Regression tests added -----

Aether/test/test_aeth01_age_controller.py:
* test_c1_controller_known_id_omitted_from_reaper_probe_set_stays_unresolved
  -- reproduces Appendix A exactly (stale/empty LIST, live GET at t=1800,
  zero GET/DELETE calls, report["owned_ids"] == []) and asserts the FIXED
  outcome: KNOWN_OWNED_CLEANUP_UNRESOLVED, OPERATIONAL_CLEANUP_UNRESOLVED,
  exit_code == 2. Verified to fail against the pre-repair aggregate() (see
  section 5) and pass against the repaired one.
* test_c1_forged_local_report_omitting_owned_id_is_caught_by_fresh_state
  (C1-J) -- a caller-supplied local report with owned_ids/pod_evidence
  forged empty is refused with INVALID_CLEANUP_EVIDENCE by the existing
  fresh-state reconstruction, before aggregate() is ever reached with a
  trusted forged report.

The pre-existing test_n1_empty_list_get_reappearance_at_1800_never_confirms
_and_retries_delete in test_aeth01_independent_reaper.py already exercises
Review 04's counterfactual control (the SAME ID seeded into the reaper's own
owned set first): 61 GETs, 31 DELETE attempts, KNOWN_OWNED_CLEANUP_UNRESOLVED.
It required no change and continues to pass.

----- 4. Existing tests updated for the new (intended) semantics -----

Aether/test/test_aeth01_cleanup_evidence.py:
* test_union_retains_local_only_reaper_only_and_multiple_exact_owned_ids ->
  renamed test_union_retains_reaper_only_ids_but_requires_reaper_coverage_
  of_local_ids. A local-only ID is no longer trusted; the test now seeds it
  into the reaper's report too, and adds an explicit assertion that removing
  it from the reaper's report alone (leaving it in local, still confirmed)
  drives KNOWN_OWNED_CLEANUP_UNRESOLVED. The reaper-only-ID and late-duplicate
  behavior is unchanged.
* test_window_must_strictly_follow_latest_local_event_even_after_wall_rollback
  -- added matching reaper-side pod evidence so the (unrelated) window-
  ordering assertion under test is not itself blocked by the new coverage
  requirement.

Aether/test/test_aeth01_age_controller.py structured_reports fixture: the
reaper report now includes pod_1 (TERMINATED, observed strictly before the
independent window's start, i.e. a prior OWNED_SEEN-style reset), matching
what a real reaper report covering a controller-known ID looks like. All
eight dependent tests (combine/N2 seal, forged-evidence, missing-facts,
pure-evaluation-label, CLI) were re-verified with no behavioral changes
beyond restoring the coverage precondition.

----- 5. Falsification of the fix itself -----

Stashed only cleanup_evidence.py (reverting to the pre-repair aggregate())
and reran the new C1 regression test in isolation: it fails, reproducing
exactly the bug (KNOWN_OWNED_CLEANUP_CONFIRMED instead of _UNRESOLVED).
Restoring the fix makes it pass again. This confirms the test is coupled to
the actual defect, not a vacuous assertion.

----- 6. Executed validation -----

python -B -m pytest Aether/test/test_aeth01_cleanup_evidence.py
Aether/test/test_aeth01_age_controller.py Aether/test/test_aeth01_independent_reaper.py
Aether/test/test_aeth01_cleanup_oracle.py Aether/test/test_aeth01_runpod_api.py
Aether/test/test_aeth01_terminology_audit.py -q -p no:cacheprovider (one command).
Result: 651 passed, 74 subtests passed, exit 0 (Review 04's unmodified
baseline was 646 passed / 74 subtests; +5 net new/renamed assertions from
this repair). Terminology audit passed after one wording fix (a comment used
"reproduction", a disallowed deprecated-metaphor term; reworded to "repro").

----- 7. What remains unresolved -----

This repair only closes the missing-known-ID coverage gap. It does not
implement a proactive controller-to-reaper known-ID handoff/seeding
mechanism -- a genuinely already-deleted local-only ID that the reaper never
independently lists or GETs will now correctly stay UNRESOLVED forever
rather than falsely confirm; achieving eventual convergence for that case is
explicitly out of scope for this bounded round (see CLEANUP_EVIDENCE_MODEL.md
"Supply authenticated/trusted, run-bound known IDs..." as the larger,
unauthorized option). All other Review 04 findings (N1/N2 dual-endpoint and
authoritative-seal behavior, oracle ceiling, crash boundaries, clock/freshness
attacks) are unchanged by this commit. AGE remains BOUNDED_REPAIR_BEFORE_B3
for every other reason already on record; only C1 is closed by this packet.

+=========================== END OF PACKET =============================+
Retirement or "not worth continuing" remains an available human decision.
