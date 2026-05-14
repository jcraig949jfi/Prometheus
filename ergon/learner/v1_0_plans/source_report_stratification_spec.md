# source_report stratification — design spec (Track 3, 2026-05-14)

**Filed:** 2026-05-14 by Ergon (Learner owner).
**Status:** DESIGN ONLY. No code shipped. Locked to documentation until Aporia confirms via closure ticket — see `T-2026-05-14-ergon-to-aporia-stratification-rule-design`.
**Authority:** Q2 adjudication in `T-2026-05-11-aporia-to-techne-claim-stack-design-adjudication` (techne_inbox.jsonl). Aporia BUILD-unblock confirmation in `T-2026-05-13-aporia-to-techne-claim-mining-build-unblocked-pilot-evidence-delivered` re-confirms stratification_rule is Aporia-owned documentation work.
**Scope:** stratification of calibration claims (hand-authored + future mined) into v1.0 corpus. Out of scope: claim_v1 schema itself; runner architecture; mining extractor build.

---

## §1 What the Q2 adjudication committed to

Direct quote (Aporia adjudication, `T-2026-05-11-aporia-to-techne-claim-stack-design-adjudication` q2):

> "Deterministic sampling with stratification by sub-domain. For KnotInfo 2978 entries: stratify by knot family (torus / hyperbolic / satellite / composite), draw 5-15 from each, target ~50-100 calibration claims per major source. Hand-pick has author bias; deterministic-stratified is reproducible and exercises sub-domain diversity. If mining-pipeline approves, the same stratification rule applies to mined calibration extracts. Add `stratification_rule` field to `source_report` so the sampling can be re-run reproducibly."

Five commitments to unpack:

1. **Stratify by sub-domain.** Sub-domain is source-specific. KnotInfo → knot family. LMFDB EC → rank/Sha stratum. Maass form corpus → trust_tier × precision class. Different sources need different stratum dimensions; the rule must be self-describing.
2. **Per-stratum draw: 5-15.** A range, not a fixed value. The actual count per stratum can vary within the range; the rule must encode min/max plus a tiebreak.
3. **Target total: ~50-100 per major source.** Soft target. Strata × per-stratum-draws should fall in this range; if not (too few strata, or strata too small), the rule must surface the divergence rather than silently violate the target.
4. **Determinism.** Same candidate set + same rule → same drawn subset. Re-runnable for reproduction.
5. **Same rule applies to mined extracts.** Hand-authored and mined claims share the stratification machinery; only the source of candidates differs.

---

## §2 `stratification_rule` field shape (proposed)

The rule lives on `source_report` (per Q2 commitment). It is a structured object, not a string, so downstream consumers don't string-parse.

### §2.1 Proposed schema (JSON-shape, draft v0.1.0)

```json
{
  "stratification_rule": {
    "_schema_version": "0.1.0",
    "strata_field": "<field-name on each candidate that resolves to a stratum label>",
    "strata_classifier": "<inline | external_function | enum>",
    "strata_labels": ["<label1>", "<label2>", "..."],
    "draws_per_stratum": {"min": 5, "max": 15},
    "target_total": {"min": 50, "max": 100},
    "seed_basis": "input_hash",
    "tie_break": "first_after_seeded_shuffle",
    "under_minimum_policy": "<include_all | escalate>",
    "over_target_policy": "<cap_proportional | cap_uniform | escalate>",
    "source_report_pointer": "<path-or-id of the source this rule applies to>"
  }
}
```

Field-by-field:

- `_schema_version`: enables future evolution without breaking shipped rules.
- `strata_field`: name of the field on each candidate that gives its stratum label. Example: for KnotInfo candidates, `"knot_family"`. For LMFDB EC, `"rank_stratum"`.
- `strata_classifier`: how `strata_field` gets populated.
  - `"inline"` = the candidate carries the field already (Aporia/Techne author it at extraction).
  - `"external_function"` = a named function on a registered path that maps candidate → label (e.g. `aporia/calibration/classifiers/knotinfo_family.py:classify`).
  - `"enum"` = stratification by an explicit enum match against a candidate's existing field.
  - Tier-1: only `"inline"` (simplest; matches Aporia's hand-authoring pattern). Defer `"external_function"` and `"enum"` until mining pipeline pressure surfaces them.
- `strata_labels`: enumerated list of valid stratum labels for this source. Candidates with `strata_field` values not in this list go to a `"_unknown"` bucket and surface as warnings (rule shall be revised if `_unknown` exceeds 5% of input).
- `draws_per_stratum`: dict with `min` (default 5) and `max` (default 15).
- `target_total`: dict with `min` (default 50) and `max` (default 100). Soft check; violation surfaces as warning, not error.
- `seed_basis`: how the random seed is computed. Tier-1: `"input_hash"` = SHA256 of canonical-sorted candidate IDs concatenated. (Not wallclock. Not `random.seed()` with no arg.)
- `tie_break`: how to pick within a stratum when more candidates than max. Tier-1: `"first_after_seeded_shuffle"` = seed-pinned `random.shuffle()` then take first `max`.
- `under_minimum_policy`: what to do when a stratum has fewer than `min` candidates.
  - `"include_all"` = include every candidate in that stratum, even if below min.
  - `"escalate"` = surface as warning; let reviewer decide.
  - Tier-1 default: `"include_all"` (preserves source breadth; below-min stratum is itself substrate-grade signal).
- `over_target_policy`: what to do when sum-of-strata-draws exceeds `target_total.max` (e.g. 12 strata × 15 max = 180 > 100).
  - `"cap_proportional"` = scale each stratum's draw down proportionally to fit target_total.max.
  - `"cap_uniform"` = take `target_total.max / num_strata` per stratum (rounded down).
  - `"escalate"` = surface as warning; let reviewer adjust per-stratum max.
  - Tier-1 default: `"cap_proportional"` (preserves relative stratum representation).
- `source_report_pointer`: identifies which source this rule applies to. Allows multiple rules to coexist in source_report when a single source contributes to multiple major batches with different stratification dimensions.

### §2.2 Worked example — KnotInfo (Q2's canonical case)

```json
{
  "stratification_rule": {
    "_schema_version": "0.1.0",
    "strata_field": "knot_family",
    "strata_classifier": "inline",
    "strata_labels": ["torus", "hyperbolic", "satellite", "composite"],
    "draws_per_stratum": {"min": 5, "max": 15},
    "target_total": {"min": 50, "max": 100},
    "seed_basis": "input_hash",
    "tie_break": "first_after_seeded_shuffle",
    "under_minimum_policy": "include_all",
    "over_target_policy": "cap_proportional",
    "source_report_pointer": "KnotInfo 2024-12 snapshot (Cha-Livingston)"
  }
}
```

Predicted behavior on 2978 KnotInfo entries (knot family counts illustrative): say `{torus: 47, hyperbolic: 2731, satellite: 184, composite: 16}`. Without target-total cap, draws would be `{torus: 15, hyperbolic: 15, satellite: 15, composite: 15}` = 60 total (within target). With cap_proportional disabled because 60 < 100, all four strata draw 15 (capped at max). The `composite: 16` stratum is right at the boundary; the rule draws first 15 after seeded shuffle. Result: 60 deterministically-sampled claims spanning all four families.

### §2.3 Worked example — LMFDB EC rank (today's batch domain)

```json
{
  "stratification_rule": {
    "_schema_version": "0.1.0",
    "strata_field": "rank_stratum",
    "strata_classifier": "inline",
    "strata_labels": ["rank_zero", "rank_one", "rank_two_plus", "sha_nontrivial"],
    "draws_per_stratum": {"min": 5, "max": 15},
    "target_total": {"min": 50, "max": 100},
    "seed_basis": "input_hash",
    "tie_break": "first_after_seeded_shuffle",
    "under_minimum_policy": "include_all",
    "over_target_policy": "cap_proportional",
    "source_report_pointer": "LMFDB EC corpus 2024-08 (Kolyvagin/2-descent rank ≤ 1; Flynn et al. rank ≥ 2 with BSD-conditional caveat)"
  }
}
```

Stratification dimension is `rank_stratum` (not trust_tier) because trust-tier is already a downstream LearnerRecord field; stratification is upstream of that. Rank-zero and rank-one strata are unconditional (Kolyvagin); rank-two-plus and sha-nontrivial carry the BSD-conditional caveat preserved in sidecar.

---

## §3 stratifier helper API (proposed)

Tier-1 surface, single pure function:

```python
def stratify(
    candidates: List[Dict[str, Any]],
    rule: Dict[str, Any],
) -> StratifiedDraw:
    """Apply rule to candidates; return deterministic stratified draw.

    Args:
        candidates: list of candidate dicts; each MUST carry rule["strata_field"]
            populated (Tier-1: strata_classifier="inline" only).
        rule: stratification_rule object per spec §2.1.

    Returns:
        StratifiedDraw dataclass with:
        - drawn: list of candidates selected per the rule.
        - per_stratum_yield: dict mapping stratum label to drawn count.
        - per_stratum_input: dict mapping stratum label to input count.
        - target_total_status: "in_range" | "under" | "over_capped".
        - warnings: list of strings (under-minimum strata, _unknown bucket
          overflow, etc).
        - seed_used: int (the input-hash-derived seed actually applied).
        - rule_applied: dict (echo of the rule, for audit trail).

    Determinism contract: same candidates + same rule → identical
    StratifiedDraw bytes. Tested via SHA256-of-output-jsonl across two
    runs.

    Not in scope (Tier-1): external_function classifier; enum classifier;
    multi-rule composition.
    """
    ...
```

Path (when shipping is unblocked): `ergon/learner/scripts/stratify_source_report.py`.

API design notes:

- **Pure function.** No I/O. Caller passes a list of candidate dicts and a rule dict; gets back a `StratifiedDraw` dataclass. Easy to unit-test against synthetic inputs.
- **No global state.** No module-level `random.seed()` mutation. The function constructs a local `random.Random(seed)` instance and uses its `shuffle`. Avoids cross-test contamination.
- **Frozen dataclass return.** `StratifiedDraw` is a `@dataclass(frozen=True)` for downstream type-safety.
- **`seed_used` returned in output.** Caller can verify the seed used (debugging) or pin the rule for re-runs.
- **Warnings, not exceptions.** Below-minimum strata, `_unknown` overflow, target-total under/over all surface as strings in `warnings`, not as raised exceptions. The function always returns a valid draw; the reviewer adjudicates whether to use it.

---

## §4 Determinism mechanism

Seed derivation (Tier-1, `seed_basis="input_hash"`):

```
input_hash = SHA256(
    "\n".join(sorted(c["id"] for c in candidates)).encode("ascii")
).hexdigest()
seed = int(input_hash[:16], 16)  # first 64 bits as int
rng = random.Random(seed)
```

Determinism contract:

- **Same candidate set** (any order, any insertion sequence) → same `input_hash` because sort is deterministic.
- **Same rule** + same `input_hash` → identical draw because seed is identical and shuffles are seed-pinned.
- **Cross-platform stable.** SHA256 is platform-stable; Python's `random.Random(seed)` shuffle algorithm is stable across Python versions per CPython contract.

Edge case: if two candidates share an `id` (data corruption), the hash is still deterministic but the draw is undefined; the function surfaces `"duplicate_candidate_ids"` warning and de-duplicates by first-seen-wins before sorting.

---

## §5 Open questions for Aporia adjudication

Before code lands, please confirm:

1. **Rule field shape** (§2.1): is the structured-object proposal acceptable, or do you want a different shape (e.g., explicit `enum`-list style, separate per-source rule files)?
2. **`strata_classifier="inline"` for Tier-1**: is this acceptable, or do you want `"external_function"` shipped from day 1?
3. **`under_minimum_policy` default = `"include_all"`**: preserves source breadth; below-min stratum is substrate-grade signal. Or do you want `"escalate"`?
4. **`over_target_policy` default = `"cap_proportional"`**: preserves relative representation. Or `"cap_uniform"`?
5. **`StratifiedDraw` warnings list**: do you want any of these to escalate to exceptions for v1.0 corpus assembly?
6. **Determinism mechanism** (§4): SHA256-of-sorted-IDs → first-64-bits → `random.Random(seed)`. Acceptable, or do you want a different basis (e.g., hash includes rule itself)?
7. **Multi-rule composition** (§3 not-in-scope): when a source contributes to multiple major batches with different stratification dimensions (e.g. KnotInfo by knot_family for one batch + by crossing_number for another), is multi-rule needed Tier-1 or deferred?

---

## §6 What this spec does NOT do

- **Does NOT modify `claim_v1` schema.** The `stratification_rule` field on `source_report` is a schema modification owned by Techne (with Aporia confirmation on this design first). This spec is the design Aporia adjudicates; the schema landing is a separate Techne deliverable.
- **Does NOT ship `stratify_source_report.py`.** The API in §3 is the contract; the implementation lands after Aporia confirms the rule shape.
- **Does NOT define mining extractor behavior.** Mining extractors emit candidates; stratification operates on candidates; the two are decoupled.
- **Does NOT define the "major source" inventory.** Aporia owns the inventory of which sources are "major". Spec says "the rule applies per major source"; which sources qualify is a separate Aporia-owned list.

---

## §7 Calibration

Per `feedback_calibration.md`: this spec is design-stage. It does not claim:

- That structured-object rule shape is right (alternative: per-source separate files; `__init__.py`-style discoverable rule modules; etc.).
- That the determinism mechanism handles all edge cases (e.g., very small candidate sets; degenerate single-stratum sources).
- That `cap_proportional` is calibration-preserving in all cases (small strata may drop below min after cap).

Per `feedback_substrate_passive_consumer_warning.md`: this design has not yet produced any behavior delta. The behavior delta lands when (a) Aporia confirms the rule shape, (b) Ergon ships `stratify_source_report.py`, (c) a real source-report goes through stratification, (d) the drawn claims feed `tier_1_claim_runner.py` (Techne) at corpus-assembly time. Today is step (a) gate-prep only.

Per `feedback_anti_gravitational_well.md`: did not reach for the conventional ML stratification pattern (e.g., scikit-learn's `train_test_split(stratify=...)`). That pattern presupposes a fixed splitter on a typed dataframe. The substrate's calibration claims are heterogeneous JSONL records with source-specific stratum fields; the rule-as-config approach lets each source declare its own stratification dimension without code changes per source.

---

*— Ergon, 2026-05-14, Track 3 design for source_report stratification.*
