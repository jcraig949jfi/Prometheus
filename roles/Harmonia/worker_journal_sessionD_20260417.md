# Worker Journal — Harmonia_M2_sessionD — 2026-04-17

*Per TRACKING MANDATE 1776424004299-0. Append-only. Terse.*

## Tick 0 @ ~10:25 UTC — bootstrap
- Read: charter, Harmonia CHARTER, tensor builder, pattern_library, coordinate_system_catalog, sync_protocol, parallel_expectations, worker_protocol.
- Posted PING 1776421540232-0. Answered CALIBRATION_CHALLENGE `calib_hitl` at 5/8 (passed 60% threshold). QUALIFICATION_GRANTED received.
- Notes: auto-reclaim loop on F012 (HITL-blocked) — abandoned cleanly twice before filtering by task_type.

## Tick 1 @ ~10:30 UTC — catalog_mf_weight
- Claimed: `catalog_mf_weight`
- Executed: Drafted P029 entry (MF weight stratification). Flagged F001 modularity as weight=2-only anchor; `weight=2` 91% dominance as Pattern 4 trap; small-n coverage (14/249 weights at n≥1000).
- Result: SUCCESS.
- Output: `cartography/docs/catalog_mf_weight_draft.md`.
- Committed: none (no git push authority).
- Posted: WORK_COMPLETE 1776421841179-0; TENSOR_DIFF 1776421821703-0.
- Notes: originally drafted as P028, renumbered to P029 at sessionA REVISION_REQUEST 1776421986497-1 (sessionB's Katz-Sarnak took P028 first).

## Tick 2 @ ~10:45 UTC — wsw_F013 + tensor_update_F011_deficit
- Claimed: `wsw_F013` (then `tensor_update_F011_deficit`)
- Executed (F013): 4000-curve balanced rank sample (1000/rank for 0..3); pooled + 4 stratifications + P042 perm-null + P051 unfolded fit.
- Result (F013): REAL BUT DENSITY-MEDIATED. P042 z=-14.165 (object-level real); P051 collapses slope -0.00467→-0.00121 (~74% reduction); not mediated by conductor/bad-prime/torsion.
- Output (F013): `cartography/docs/wsw_F013_results.json`.
- Executed (F011 update): Pattern 8 updated in-place with 38% + 7-projection uniform visibility + F013 parallel. tensor py edits applied then reverted externally mid-task.
- Result (F011 update): SUCCESS_PARTIAL. TENSOR_DIFF posted (1776423299295-0); sessionA applied diff this tick (per CONDUCTOR_TICK 1776423568212-0).
- Posted: WORK_COMPLETE 1776423047971-0 (F013); WORK_COMPLETE 1776423327471-0 (F011 update).
- Notes: `build_landscape_tensor.py` in-place edit was reverted mid-task; learned to rely on TENSOR_DIFF-only for future tensor updates.

## Tick 3 @ ~10:50 UTC — tensor_update_F012_killed
- Claimed: `tensor_update_F012_killed`
- Executed: Drafted provisional markdown diff for F012 kill (tier → `killed_provisional` pending Liouville side-check). INVARIANCE `{P022:-1, P040:-2, P043:-1}`. Added shared_ledger_axis_exhausted edge F012→F011, may_inform edge F012→F028.
- Result: SUCCESS_PROVISIONAL.
- Output: `cartography/docs/tensor_diff_F012_killed_provisional.md`.
- Posted: WORK_COMPLETE 1776423480750-0; TENSOR_DIFF 1776423467073-0.
- Notes: Pattern 19 authorship held for sessionA per their CONDUCTOR_TICK. Liouville rescued? No — sessionB's side-check confirmed kill (1776423440503-0). sessionA TENSOR_UPDATE_FINAL 1776423774297-1 promoted Pattern 19 and applied the diff non-provisionally.

## Tick 4 @ ~11:00 UTC — catalog_artin_indicator
- Claimed: `catalog_artin_indicator`
- Executed: Drafted **P031** Frobenius-Schur Indicator entry. Flagged tautology triad: asymmetric with Is_Even (ν=-1 ⇒ Is_Even=True), asymmetric with Dim (ν=-1 only at even Dim), near-redundant with P028 on Artin slice (ν + Is_Even determines Katz-Sarnak type exactly). Applied n≥100 discipline per sessionB Liouville lesson (ν=-1 has only 785 rows).
- Result: SUCCESS.
- Output: `cartography/docs/catalog_artin_indicator_draft.md`.
- Posted: WORK_COMPLETE 1776423694972-0; TENSOR_DIFF 1776423675246-0 (inadvertently sent as type=stratification due to duplicate-key typo; content valid).
- Notes: ID collision with sessionB's character_parity resolved at sessionA's ID_ASSIGNMENT 1776424150490-0 in favor of sessionD at P031 (APPROVED as drafted).

## Tick 5 @ ~11:05 UTC — wsw_F015 + CORRECTION
- Claimed: `wsw_F015` (Szpiro monotone at fixed bad-prime count).
- Executed: 30000-row balanced sample by num_bad_primes (5000 per k in 1..6). Pooled + P021 within-k + P020 within-conductor-bin + P042 perm-null + P052 decontamination.
- Result: REPRODUCE_REAL_AT_OBJECT_LEVEL / MONOTONE_CLAIM_NOT_LITERAL. All within-k slopes negative (✓ sign), but k=4 breaks monotonicity. P042 per-stratum z = −6.9 to −22.7 (p=0 all). P052: 88% of pooled slope is k-mediated; 12% residual. P020 within-conductor: szpiro vs k is positive (+0.44 to +0.61) — coherent with negative slope vs logN at fixed k.
- Output: `cartography/docs/wsw_F015_results.json`.
- Posted: WORK_COMPLETE 1776423978085-0; CORRECTION 1776423778036-0 (message-type typo flag + P030 collision flag).
- Notes: third pattern case (F011 uniform / F013 density-mediated / F015 k-confounded) — pooled views hide structure; stratification reveals it. Seeded Pattern 20 candidate.

## Tick 6 @ ~11:10 UTC — harvest_ec_complexity_projections + P031→P032 rename
- Claimed: `harvest_ec_complexity_projections`.
- Executed: Single Claude Opus 4.7 API call with literal task brief (246 in / 1479 out tokens, 23s). Parsed 50 projection rows; heuristic match against 52-column `ec_curvedata` schema gave 23 direct column hits, 27 derivable/sibling-table.
- Result: SUCCESS.
- Output: `cartography/docs/harvest_ec_projections.md` + `cartography/docs/harvest_ec_projections_raw.txt` (provenance).
- Posted: WORK_COMPLETE 1776424203479-0.
- Notes: Side-action: renamed my Frobenius-Schur draft P031→P032 after sessionA REVISION_REQUEST to sessionB (1776423774297-0). Posted revised TENSOR_DIFF 1776424063510-0. Flagged three collisions this session → +1'd sessionB's `reserve_id()` infra proposal.

## Tick 7 @ ~11:15 UTC — mandate ack + P032→P031 restore + tensor_update_F015
- Claimed: `tensor_update_F015_sign_not_magnitude`.
- Executed:
  - Reverted Frobenius-Schur draft P032→P031 per sessionA ID_ASSIGNMENT 1776424150490-0 (my entry APPROVED as drafted at P031; sessionB char parity now P032).
  - Started this journal and backfilled ticks 0-6.
  - Backfilled `signals.specimens` rows for 7 prior completions (specimen_ids 2-8). All from `Harmonia_M2_sessionD`.
  - Drafted F015 tensor diff: FEATURES label/description rewrite, INVARIANCE `{P021:+2, P020:+1, P042:+2, P051:0, P052:-1, P001:-1}`, two new edges F015→F011 and F015→F013 under `stratification_reveals_pooled_artifact`. Pattern 20 skeleton proposed but authorship held for the dedicated task.
- Result: SUCCESS (TENSOR_DIFF only; no in-place edits).
- Output: `cartography/docs/tensor_diff_F015_sign_not_magnitude.md`.
- Posted: TENSOR_DIFF (this tick); WORK_COMPLETE forthcoming.
- signals.specimens: specimen_id=9 inserted (status=`refined`, interest=0.55).
- Notes: Mandate overhead consumed half the tick; task was chosen deliberately light. F011 Katz-Sarnak test (prio −4) left for a tick when I have full 4 min of compute.

## Tick 8 @ ~11:20 UTC — ID contradiction flag + absorb_ec_harvest
- Claimed: `absorb_ec_harvest`.
- Executed:
  - Posted QUESTION to sessionA flagging ID contradiction: ID_ASSIGNMENT 1776424150490-0 (11:09) said sessionD at P031; REVIEW_APPROVE 1776424352382-0 (11:12) approved sessionD at P032. Holding Frobenius-Schur draft at current state (P031) pending a single definitive ruling. No more rename thrash until sessionA picks one.
  - Triage of my 50-row harvest output: marked already-catalogued rows, nominated **top 10 uncatalogued projections** (Sha, root number, modular degree, Kodaira, Faltings, Sato-Tate group, isogeny-class size, regulator, Galois-image mod-ℓ, Iwasawa λ/μ) with proposed IDs P035–P048 (skipping the null-model reserved block P040–P043).
  - Flagged 5 new tautology pairs for Section 8 of the catalog (BSD leading term, Goldfeld-Szpiro, Bloch-Kato, Heegner/Kolyvagin, congruence number / modular degree).
  - Raised a CRITICAL namespace-collision flag: my P035+ run into reserved null-model P040–P043; recommending section-prefixed reserve_id() (preferred) or explicit skip.
- Result: SUCCESS.
- Output: `cartography/docs/ec_harvest_triage.md`.
- Posted: TENSOR_DIFF (this tick) + QUESTION for P-ID ambiguity.
- signals.specimens: specimen_id=10 inserted via `agora.register_specimen.register_from_task_result` helper (first use of the tracking helper sessionA shipped).
