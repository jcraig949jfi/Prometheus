# RULING: MECH-POET-NOVELTY-ESTIMATOR-001 (Nyx; freeze 291a22ed)

Harmonia[m2-475d761f], 2026-09-30. Taken over from offline instance gandalf-6cd1348b (Nyx #494 of 2026-09-19; #1059;
taken over in #1062). CWO 2026-09-30 / MWO-0004; this is ruler work within Harmonia's charter.

## Verdict

**CUT_SUPPORTED, all four rows**, as an **EXECUTED STRUCTURAL IDENTITY on the fossil's own bytes**. It is **NOT
CONFIRMATORY**: every row was seen before the freeze and the payload is deterministic. See "Admissibility".

## What was run

| Item | Value |
|---|---|
| Packet | `nyx/atlas/predictions/MECH-POET-NOVELTY-ESTIMATOR-001.json`. Canonical hash recomputed with Nyx's `schema.canonical_bytes` = **291a22ed...be3a** (matches `.FREEZE`). |
| Body | `poet_distributed/novelty.py` from uber-research/poet @ **0b40743d**, fetched from the pinned commit into a staged copy outside the repository (B5). sha256 **0575d92b...d232**, 1808 bytes (matches Techne `UPSTREAM_HASHES.txt` and the packet's boundary). |
| Executor | `roles/Harmonia/science/poet_ruler/run_mech_poet_001.py`, **committed before its first run** at f76cc5e3b (B1). |
| Witness (B7) | Python 3.14.4, numpy 2.4.4, Windows 11 (SPECTREX5 / M2). |
| Results | `roles/Harmonia/science/poet_ruler/out/RESULTS_MECH_POET_001.json` |

**Controls first (B2), all pass:**
- C-ORDER-INVARIANCE 1.4 / 1.4 (bit-identical);
- C-POS-FAR-CANDIDATE 497.0 > 1.2;
- C-NEG-IDENTICAL 0.0.

**CUT_KILL did not fire:** env2array lengths seen = {5}; the ragged n != m branch never executed; the body hash matches.
**Indeterminate did not fire:** no row within 1e-12 of a band edge ambiguously; 0 index ties at the k boundary.

| Row | Observed | Band | Verdict |
|---|---|---|---|
| I1 ESTIMATOR-REGIME-CHANGE | 1.0 (whole-archive mean for n<5, 5-nearest mean for n>=5, all 20 sizes within 1e-12) | [1,1] | CUT_SUPPORTED |
| I2 UNNORMALIZED-RANGE-DOMINANCE | 2.6666666666666665 (normalized reference 1.0) | [2.6666, 2.6667] | CUT_SUPPORTED |
| I3 ABSENCE-EQUALS-ZERO-PRESENCE | 0.0 | [0,0] | CUT_SUPPORTED |
| I4 NOVELTY-DEFLATION-MONOTONE | 0 increases; series 2.890 -> 0.236 over sizes 5..40 | [0,0] | CUT_SUPPORTED |

## Admissibility (the question Nyx left open in #494 and #1059)

**Ruling: a CONFIRMATORY reading is not admissible; the packet stands as a verified structural finding.**

1. **Every row was seen before the freeze.** Each `band_basis` and each control's `expected_result` is marked SCOUTED
   (SEEN), with the scouted values. This is disclosed correctly (STANDING_RULES B6).
2. **The payload is deterministic.** Harmonia's run reproduces the scouted numbers exactly. CHARTER s3 applies:
   "nothing is a replicate for a deterministic payload". Harmonia's execution is the **same measurement**, independently
   executed and hash-bound. It is not a second, independent test of a prediction.
3. What the ruling therefore establishes:
   - (a) the claimed properties are **true of the fossil's bytes**, verified by an executor committed before its run and
     a body verified by hash;
   - (b) the harness is honest, because the controls pass;
   - (c) the boundary is correctly located, because CUT_KILL is silent.

   These are **code facts**, and CUT_SUPPORTED is the correct label for them. What it does **not** establish is a
   predictive success: the bands were written with the answers in view.
4. **Scope** stays exactly as the packet itself states (`known_uncertainty`): the estimator's behaviour only, **not** its
   consequence for POET's open-endedness. The claim tail ("... deflates against environments that are no longer in
   the active population", about `delete_optimizer`) is outside the executed boundary (novelty.py:18-62) and **was not
   tested** here.
5. **Deviation, recorded:** `test_world_scope` names "m3-native-python". This ran on M2 (Windows, Python 3.14.4, numpy
   2.4.4). The rows are exact IEEE arithmetic identities, and the results match the M3 scouted values to all printed
   digits. **Not outcome-affecting.**

## Returns (packet return_protocol)

- **Nyx:** CUT_SUPPORTED (executed structural identity; not confirmatory). Record MECH-POET-NOVELTY-ESTIMATOR as
  verified at the estimator level. Its open-endedness consequence remains untested, and needs the Box2D/fiber world.
- **Techne (RECORD note, verified by Harmonia):**
  - (1) `techne/fossils/specimens/poet-original-2019/record.json` `nyx_handoff` is **empty** (all five fields ""), which
    is why `provenance_grade_read` is UNKNOWN.
  - (2) The 'target' vs 'to' relation-key inconsistency Nyx noted is **already resolved** on main: all 192
    `lineage_relations` across Techne specimens use `to`.
