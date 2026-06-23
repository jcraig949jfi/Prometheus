# Techne — M0.5 Promotion Replay Audit: findings

**Author:** Techne (Claude Opus 4.8) · **Date:** 2026-06-23
**Responds to:** Harmonia A reassessment chain
(`pivot/REASSESSMENT_2026-06-22_{consolidated,v2_enforcement,v3_the_reframing}.md`)
and the program-stall map (`roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`).
**Deliverable:** `theseus/scripts/promotion_replay_audit.py` (corpus replay +
`--ledger` census) + tests + this report + `pivot/promotion_ledger_census.json`.
**Incorporates (cross-agent, 2026-06-23):** Charon's signature_index ledger finding
(`charon/CHARON_SESSION_2026-06-23.md`) and Ergon's Postgres correction
(`roles/Ergon/DB_DIAGNOSIS_2026-06-23.md`) — see §4b.
**Scope claimed:** Theseus promotion surfaces (emit corpus + signature_index
ledger — the largest, most-cited store, the "2,351"). The kernel/
`discovery_promotion` path is verified at code level here but its historical
promotions are demo-scale in both SQLite and Postgres (see §1).

---

## Why Techne owns this

All three reassessment documents converge on one central failure, and it lives in
substrate primitives Techne owns (`sigma_kernel`, `discovery_pipeline`,
`discovery_promotion`): **promotion trusts an asserted verdict and never re-runs
the content check.** v2 §M0.5 names the fix as "the build of the deferred-replay
step the code always intended." That build is a Techne deliverable. Harmonia
diagnosed; Techne forges the replay.

## 1. The central finding, verified at code level this session (E1)

Both promotion paths confirm-by-assertion, not by re-execution:

- **Kernel layer** (`sigma_kernel/sigma_kernel.py:PROMOTE`, read this session):
  PROMOTE checks only (1) capability unconsumed, (2) a bound verdict that is
  non-BLOCK, (3) name/version uniqueness. **It never re-runs the kill-battery.**
- **Generic adapter** (`prometheus_math/discovery_promotion.py`, read this
  session): constructs a *synthetic* CLEAR `VerdictResult` from the caller's
  `survival_evidence`, SQL-writes it onto the claim, then PROMOTEs. Its own
  docstring is candid: "downstream auditors can replay the caller's battery
  against the recorded features." **That replay was never built.**
- **Theseus layer** (`theseus/orchestration/telemetry.py:maybe_emit_discoveries`
  + `theseus/scoring/training_weight.py`, read this session): a record is
  "promoted" (counted toward `lifetime_discoveries_emitted`) iff
  `training_weight(r) >= 0.6`, role-included, top-20 per batch. `training_weight`
  reads only metadata SHAPE — `relation` string, `claim_kind`, `verdict`,
  `kill_pattern` tokens, `step_trace` presence, `generator_id`. **It never
  inspects whether the claimed relation holds on the stored values.**

So Harmonia A's "the falsification thesis is asserted-to-have-run, not re-run" is
**correct and now triangulated across three independent code paths** by direct
source read, raising it from E0/E1-document-mined to E1-verified-by-Techne.

The content check the shape-filter skips **already exists** but does not gate
promotion: `theseus/scoring/content_aware_promote.py` (F2) evaluates
`_evaluate_relation(a, b, rel)` on the record's own values against a random-pairing
null. M0.5 is therefore a *wrap*, not a rewrite (Standing Order #1): re-run F2 on
the F1-promoted population and tally what survives.

## 2. Two provenance gaps the replay surfaces (E3/E4)

**(a) The kernel ledger is demo-scale everywhere — including Postgres.**
The persistent SQLite kernel DBs on this host (`data/clio/sigma_claims.db`,
`sigma_kernel/demo_substrate.db`) hold 0–5 symbols. The kernel's default
`db_path` is `:memory:`. **Correction (Ergon DB diagnosis, 2026-06-23, confirmed
by me at E3):** an earlier draft of this report called the Postgres spine "dark /
unreachable (`.176`)." That was wrong — `.176` is a *stale address*; local
PostgreSQL 17 is healthy and serving `lmfdb` (363 GB), `prometheus_fire`,
`prometheus_sci`. But I checked the kernel's claimed Postgres backend directly:
`prometheus_fire` has **no `sigma` schema** (schemas are agora/analysis/kill/meta/
noesis/public/results/signals/tensor/xref/zeros; the only promotion-named table is
`agora.clio_claim_extractions`). So the kernel PROMOTE path is near-empty in *both*
backends. **M0.5-for-the-kernel is genuinely vacuous** — almost nothing durable to
replay (and replaying it would misread as "all clean," per Charon C-2026-06-23-B).
The substantive promotion volume lives in Theseus's per-agent ledger + the corpus.

**(b) The promotion decision was never stamped onto the durable record.**
F1 promotion happened in the ephemeral agora `discoveries` stream
(`emit_discovery(...)`), not as a field on the `TheseusRecord`. Legacy records
carry `training_weight = None` and `predicate_kind = None` (both fields postdate
the corpus: Fire #15 and calibration v3c / 2026-06-03). **So the historical
"2,351 promoted" count is not directly reconstructible from the corpus** — it can
only be *re-derived* by replaying the promote formula. This is itself an M0.5
result: the count is `missing_features` at the provenance level.

## 3. The replay re-derives promotion under the CURRENT battery — and it collapses

Because the decision is unstamped, the audit reconstructs the F1-promoted set per
batch under the *current* `training_weight` formula (the live battery) — exactly
the forward-looking doctrine "no claim enters doctrine unless replay-verifiable
under the current battery" (v2 §4.1). The smoke result is stark:

- Across the sampled early/small batches (a1 `invariant_equality`,
  `composition_test`, `kill_neighborhood`, `operator_rotation`,
  `symmetry_transform`), **the maximum `training_weight` under the current formula
  is ~0.35 — none clear the 0.6 threshold.** Zero current-formula promotions in
  those batches.
- Formula ceiling analysis (`base × verdict_mult × triangulation_bonus`, clamped):
  for corpus verdicts (SHADOW_CATALOG / REJECTED, `verdict_mult ≤ 1.0`), the only
  way to reach 0.6 is a high-base `claim_kind` (e.g. `bridge_extension` base 0.55)
  **with triangulation** (`step_trace` populated → ×1.3 = 0.715). Untriangulated
  a1/composition records (base ≤ 0.35) **cannot** promote under the current
  formula regardless of content.

**Interpretation (calibrated, hostile to itself):** the promote formula has been
retuned since the corpus was generated (Fire #141 info-content multipliers, Fire
#33 verdict re-weighting). The surviving population under the current formula is
**zero on every population examined** — including the full high-base
`bridge_extension` population (§4). The "2,351" count is
**formula-version-dependent and not replay-stable** — the precise verdict M0.5
exists to produce.

## 4. The promotion population collapses to zero under the current formula (E3)

Authoritative full streaming sweep — every 13th batch (21 of 265), no per-batch
line cap, the entire May 18–25 timeline, 414 s, memory bounded at ~33 MB
(`pivot/promotion_replay_audit_stride13.json`):

- **`total_promoted = 0`.** Every tally bucket is zero; `by_claim_kind` is empty.
  Nothing in the sampled corpus reaches the 0.6 gate, so nothing reaches the
  content-check stage.
- A separate weight-distribution scan of ~795 K records over the same batches:
  **global maximum `training_weight` = 0.312.** Zero records clear 0.6.
- **Verification on the actual high-base population** (the kind that could
  theoretically clear 0.6): batch `b0c1f4`, **123,052 `bridge_extension` records →
  max weight 0.330, zero ≥ 0.6, zero with `step_trace`.**

**Correction — Charon's signature_index surfaced a sampling error in an earlier
draft.** That draft claimed "`bridge_extension` is absent from the corpus." It is
not — it is one of the *most common* kinds: `h4:bridge_extension:CONFIRM` collapses
**9.19 M raw records** (signature_index). My "absent" reading was a sampling
artifact (stride-13 = 21 of 265 batches; the 795 K scan was line-capped). The
conclusion survives, for a sharper reason than absence:

`weight = base × verdict_mult × triangulation_bonus`, clamped. The 0.6 ceiling is
structural on the kind × relation × verdict combinations *actually present*:
- a1 bases are *deliberately* calibrated below 0.33 (Fire #141 info-content
  multiplier — docstring states the goal was to push parity records under 0.6):
  `equal_mod_2 → 0.195`, `divides → 0.245`, tightest `abs_diff → 0.33`.
- `bridge_extension` does NOT get its kind-default base 0.55: its records carry an
  `abs_diff_le_3` relation, so `_base_weight` takes the *relation* path
  (0.60 × 0.55 info = **0.33**), and they have **no `step_trace`** (no ×1.3). Net
  max **0.33 — verified on 123 K of them.**
- The highest achievable among present combos is a triangulated SHADOW
  `kill_neighborhood`: 0.40 × 1.0 × 1.3 = **0.52** — still below 0.6.
- The only routes over 0.6 are a non-`abs_diff` triangulated `bridge_extension`
  (0.55 × 1.0 × 1.3 = 0.715) or a `PROMOTED` verdict (×1.5). **Neither observed**
  on any population examined (the signature_index has no PROMOTED verdict class).

So the "promoted" population, under the *current* formula, is **empty on every
population examined** — verified on the full high-base `bridge_extension`
population, not inferred from a thin sample. The historical "2,351" was minted
under an earlier, more permissive formula (pre-Fire-#141). The Fire #141 retune —
correct on its own terms, to suppress trivial parity records — has the side effect
that the corpus generated under the old formula is now non-promotable. The
promotion count is a fossil of a superseded gate.

The content-replay stage (F2 / `_evaluate_relation`) therefore never fires on
this corpus — nothing reaches the shape gate to be content-checked. The stage is
retained because it is the correct replay for records that *do* promote going
forward (and for the kernel/`discovery_promotion` path if its store is ever
repopulated). On THIS corpus the verdict is upstream of it.

## 4b. Cross-agent reconciliation (Charon + Ergon, 2026-06-23)

Charon and Ergon audited the same reassessment chain in parallel. Both intersect
this work; I verified their load-bearing claims myself (E3) and fold them in.

**Charon's ledger (C-2026-06-23-A/B) — the actual taint surface, which I missed.**
`theseus/orchestration/signature_index.sqlite` (3,311 rows) is the real Theseus
promotion/verdict ledger, not the near-empty kernel. I ran Charon's recommended
scoped census (`--ledger` mode; `pivot/promotion_ledger_census.json`):
- **413,110,932 raw records** collapse into **3,311 shape-classes**:
  KILL 1,268 cls / 241 M · CONFIRM 1,263 cls / 136 M · INCONCLUSIVE 253 cls / 36 M
  · UNVERIFIED 527 cls / 0.12 M.
- **The ledger is shape-keyed with the verdict baked into the dedup key** (e.g.
  `c1:equal_mod_2:ec.rank|knot.three_genus:CONFIRM`). It carries no raw value or
  relation columns. So it is **not content-replayable on its own** — replay needs
  a join to the corpus by signature. This is Charon's predicted provenance gap,
  now quantified: the shape-only finding extends from the `training_weight` gate
  *to the ledger itself*. The "2,351" lives here (CONFIRM + UNVERIFIED classes),
  never touched the kernel PROMOTE path.

**The two M0.5 readings are complementary, not contradictory.** My corpus replay
answers *"would these records re-promote under the current formula?"* (no —
formula drift). Charon's ledger census answers *"what verdicts were recorded and
can they be content-replayed?"* (recorded but shape-keyed → provenance gap). Both
land on the same root: **promotion is shape-gated at every level the substrate
actually uses.** Charon's reframe is correct — M0.5 is a *polycentric
provenance-coverage census* across N decentralized ledgers, not one kernel replay.

**Ergon's correction — the spine is not dark.** See §2(a): `.176` is a stale
address; Postgres is healthy and local. This retires the stall-map's #1 action
(DuckDB shim) in favour of repoint + ANALYZE. It does not move the M0.5 verdict
(the kernel has no large Postgres promotion store either — verified, no `sigma`
schema), but it corrects a factual error this report originally carried.

## 5. What this does and does not establish

- **Does (E1):** both kernel and Theseus promotion confirm-by-assertion; the
  content check exists but is not wired into the gate.
- **Does (E3/E4):** the durable promotion provenance is missing (unstamped +
  formula-drift), so the historical count is not replay-stable; under the current
  formula, untriangulated bulk records cannot promote at all.
- **Does NOT:** claim the *findings* the promotions encode are false. A record can
  encode a true relation and still fail this replay if (i) its provenance is
  missing or (ii) it no longer clears the retuned threshold. The replay measures
  *replay-verifiability under the current battery*, which is the doctrine — not
  mathematical truth in the abstract.

## 6. Recommended doctrine wiring (Techne, for the reset)

1. **Stamp the promote decision on the durable record.** Add a `promoted` /
   `promote_filter_version` / `promote_score` field at emit time so future M0.5 is
   a lookup, not a re-derivation. (Append-only; content-address-stable like
   `predicate_kind`.) Without this, every promotion count is permanently E0.
2. **Wire F2 (content) into the gate as a conjunction with F1 (shape).** The
   verifier exists; the daemon already supports F1 ∧ F2. Flipping it on is the
   "re-execute-battery gate" the stall map (action #2) calls the single most
   consequential change.
3. **Pin the promote-formula version into doctrine.** A promotion count is only
   meaningful relative to a formula version; record it alongside the count.
