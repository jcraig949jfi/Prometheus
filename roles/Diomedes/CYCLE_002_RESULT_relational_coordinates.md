# Diomedes cycle 002 — RESULT: cheap relational coordinates do not transfer across invariant pairs

**Filed:** 2026-08-24. **Pre-registration:** `CYCLE_002_PREREG_relational_coordinates.md`, frozen at
`3041b131` **before** any outcome existed. **Charter:** `LOOP_CHARTER.md` (`248a36b8`).
**Rows:** `cycle002_run.py` → `cycle002_result.json`; population identity proof
`harvest_cache.py` → `harvest_cache_proof.json`.
**Pre-registered band: NOT-IN-SIMPLE-RELATIONAL. Disposition: KILL** (of the specific tested claim —
see §5 for exactly what died).

---

## 1. Population identity, proved before measuring

Charter §9 permits caching the cycle-001 harvest only on demonstrated identity. Two independent live
harvests and the cache roundtrip all produce digest `1b4abb1a36a9cfb53d6a4bfb8c08a0623e28a88ba996556532d80e71d889af52`;
all field counts match (12 value keys, 4,772 object-value pairs, 38,071 parents, 1,052 objects).
`load_verified()` refuses to return data unless that proof passed. **The optimization did not become
an experimental change.**

## 2. Headline

Both controls clean: ORACLE **1.0000**, SHUFFLE cheat **0.4993**, RANDOM **0.4995**.
No functional-dependency flags fired — **no single feature reached AUC ≥ 0.90**, so §6's
CATALOG-DEPENDENCY escape is not in play.

- **PHI_REL** (18 relational features) — **0.5444**, per-seed 3·SE intervals spanning
  [0.5350, 0.5521]. Every seed's upper bound sits far below the state-independent information
  ceiling of **0.6254**.
- **PHI_ALL** (22 features) — **0.5588**
- **CYCLE1_B1** (candidate break-rate alone) — **0.5626**

**Adding 18 relational features to the four cycle-001 carryovers made the model worse**
(0.5588 < 0.5626). The pre-registered band fires unambiguously: **NOT-IN-SIMPLE-RELATIONAL.**

## 3. My prediction was wrong, on three of four clauses

Prereg §8, recorded before measurement:

- *"PHI_REL lands 0.60–0.70"* → **0.5444. WRONG**, and outside the interval by a wide margin.
- *"most likely AMBIGUOUS or weak ELEMENTARY-COORDINATE-DEFECT"* → **NOT-IN-SIMPLE-RELATIONAL. WRONG.**
- *"`parity_match_j` strongest single feature on `equal_mod_2`"* → **RIGHT on identity, WRONG on
  direction** (see §4).
- *"`absdiff_target_j` strongest on `abs_diff_le_3`"* → `absdiff_target_0` = **0.5008**, i.e. chance.
  **WRONG.**

Logged as calibration. Being wrong about the direction of my own hypothesised mechanism is the
useful kind of wrong.

## 4. The finding the headline hides — read by informativeness, not raw AUC

An arm at AUC 0.4345 is exactly as informative as one at 0.5655; only the sign differs, and a
logistic model can learn a sign. Ranking the pre-registered per-feature table by **|AUC − 0.5|**:

- **`parity_match_0` — |d| = 0.0655** (AUC 0.4345, *predicts the relation HOLDS*)
- `B1_break_rate` — |d| = 0.0626 (AUC 0.5626, predicts BREAK)
- `absdelta_0` — |d| = 0.0445
- `parity_match_2` — |d| = 0.0187
- everything else — |d| ≤ 0.018

**The single most informative feature in the entire experiment is a relational one**, and it points
the way the mechanism predicts: when the candidate's parity on a *cheap companion* axis matches the
target's, the relation on the *expensive* axis tends to hold. That is the cycle-002 hypothesis
working at the feature level.

**And the model cannot use it.** `PHI_REL` (0.5444) scores *below its own best single feature*
(0.5655 sign-corrected). A model fit on training invariant pairs and evaluated on **held-out
invariant pairs** loses information its inputs demonstrably contain.

## 5. What died, exactly (charter §3)

**KILLED:** *a single global relational model over `Z(x,a)` recovers state-conditional signal across
held-out invariant pairs.* Measured at 0.5444 against a 0.6254 ceiling, with every seed's 3·SE
interval excluding the ceiling.

**NOT killed, and explicitly not claimed either way by this cycle:**
- that relational coordinates carry conditional information *within* an invariant pair — §4's
  feature-level evidence points the other way and this cycle did not test it;
- H2 (this landscape contains state-conditional information) — unchanged, still supported;
- H3 in general — only this representation-plus-split combination was tested.

## 6. The least-interesting interpretation, and why it is not yet dismissible (charter §12)

The boring explanations, tested or assessed:

- **Catalog functional dependency** — ruled out by the pre-registered guard; no feature ≥ 0.90.
- **Leakage** — cheat control at 0.4993; no arm reads the tested invariant.
- **Degenerate companion axes** — ruled out; the companion features vary and produce signal.
- **Base-rate/marginal effects** — `B1` is marginal and was carried explicitly; PHI_REL excludes it.
- **Transfer failure rather than representational inadequacy — NOT ruled out, and it is now the
  leading competing explanation.** If the sign or magnitude of the companion↔tested relationship
  differs per invariant pair, a global coefficient learned on some pairs is *wrong* on others, and
  the T3 split would produce exactly this signature: informative features, underperforming model.

This is the cheapest discriminator available and it becomes cycle 003. Note it is an **H4 (transfer)**
question, not an H3 (coordinate adequacy) question — the distinction the charter requires be kept.

**Guard against my own rescue instinct:** the pre-registered primary metric landed where it landed
and the band stands. §4 does not overturn it. The per-feature table was pre-registered to be
reported (prereg §4), so this is not post-hoc fishing — but it generates a *new* hypothesis for a
*new* cycle rather than amending this one's verdict.

## 7. Deviations

None. The frozen family, split, seeds, metric, bands and guard ran exactly as registered. The only
change from the killed first attempt was the verified harvest cache (§1).

---

## Coordinate-Adequacy Record — CAR-002

```json
{
  "car_id": "CAR-002",
  "claim_id": "cheap relational coordinates Z(x,a) recover the conditional signal across held-out invariant pairs",
  "quantity_credited": "I(A*; Z_a | Z_x)",
  "coordinate_system": "18 hand-written relational features over 3 companion invariants + 4 candidate-only carryovers",
  "alphabet": "candidate replacement objects for the varied side",
  "attainable_range": {"chance": 0.5, "state_independent_ceiling": 0.6254, "state_specific_oracle": 1.0},
  "measured": {"PHI_REL": 0.5444, "PHI_ALL": 0.5588, "CYCLE1_B1": 0.5626,
               "best_single_feature_informativeness": 0.0655,
               "best_single_feature": "parity_match_0"},
  "controls": {"positive_oracle_auc": 1.0, "cheat_shuffle_auc": 0.4993,
               "functional_dependency_flags": 0},
  "measured_over_which_rows": "5 seeds, held-out invariant pair split, ~12.8k-17.5k eval states per seed, relations equal_mod_2 and abs_diff_le_3, population digest 1b4abb1a",
  "verdict": "INADEQUATE",
  "disposition": "KILL",
  "what_died": "a single global relational model over Z(x,a) transferring across held-out invariant pairs",
  "decision_this_changes": "learned transition representations are NOT yet defensible — the cheaper transfer explanation must be excluded first; cycle 003 tests within-pair vs across-pair splits",
  "rows_ref": "cycle002_result.json, harvest_cache_proof.json"
}
```

*— Diomedes, cycle 002 result, 2026-08-24. Disposition KILL. Next: cycle 003, the split discriminator.*
