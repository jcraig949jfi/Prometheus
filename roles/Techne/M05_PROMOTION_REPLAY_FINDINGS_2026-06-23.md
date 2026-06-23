# Techne — M0.5 Promotion Replay Audit: findings

**Author:** Techne (Claude Opus 4.8) · **Date:** 2026-06-23
**Responds to:** Harmonia A reassessment chain
(`pivot/REASSESSMENT_2026-06-22_{consolidated,v2_enforcement,v3_the_reframing}.md`)
and the program-stall map (`roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`).
**Deliverable:** `theseus/scripts/promotion_replay_audit.py` + this report.
**Scope claimed:** Theseus emit corpus only (the largest, most-cited promotion
store — the "2,351"). The kernel/`discovery_promotion` path is verified at code
level here but its historical promotions are demo-scale locally (see §1).

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

**(a) The kernel ledger is demo-scale locally; the real store is the corpus.**
The persistent SQLite kernel DBs on this host (`data/clio/sigma_claims.db`,
`sigma_kernel/demo_substrate.db`) hold 0–5 symbols. The kernel's default
`db_path` is `:memory:`. The substantive promotions live in the 346 GB Theseus
emit corpus (265 batches, all from the May 18–25 2026 generation run), not in a
queryable kernel ledger. **M0.5-for-the-kernel is mostly vacuous on this host** —
there is almost nothing durable to replay; the dark Postgres (`.176`) may hold
more but is unreachable.

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
#33 verdict re-weighting). The initial reading was "sparse and concentrated in
triangulated high-base records"; the cross-timeline sweep (§4) sharpens it to the
stronger result — the surviving population is **zero**, because the one kind that
could clear the retuned bar (`bridge_extension`) is absent from the corpus. The
"2,351" count is **formula-version-dependent and not replay-stable** — the precise
verdict M0.5 exists to produce.

## 4. The promotion population collapses to zero under the current formula (E3)

Authoritative full streaming sweep — every 13th batch (21 of 265), no per-batch
line cap, the entire May 18–25 timeline, 414 s, memory bounded at ~33 MB
(`pivot/promotion_replay_audit_stride13.json`):

- **`total_promoted = 0`.** Every tally bucket is zero; `by_claim_kind` is empty.
  Nothing in the sampled corpus reaches the 0.6 gate, so nothing reaches the
  content-check stage.
- A separate weight-distribution scan of ~795 K records over the same batches:
  **global maximum `training_weight` = 0.312.** Zero records clear 0.6.
- The argmax (0.312) is a triangulated `kill_neighborhood` / REJECTED record —
  exactly `base 0.40 × verdict_mult 0.6 (generic kill) × triangulation 1.3`.
- **Zero `bridge_extension` records** found in the sample.

**This is robust on formula-ceiling grounds, independent of sampling.**
`weight = base × verdict_mult × triangulation_bonus`, clamped. For corpus
verdicts (SHADOW/REJECTED, `verdict_mult ≤ 1.0`):
- a1 bases are *deliberately* calibrated below 0.33 (Fire #141 info-content
  multiplier — the docstring states the goal was to push parity records under
  0.6): `equal_mod_2 → 0.195`, `divides → 0.245`, tightest `abs_diff → 0.33`.
- The max base among *kinds present in the corpus* is `kill_neighborhood` 0.40 →
  with a specific-kill pattern (×1.0) and triangulation (×1.3) = **0.52**, still
  below 0.6.
- The only routes over 0.6 are `bridge_extension` (base 0.55 × 1.0 × 1.3 = 0.715)
  or a `PROMOTED` verdict (×1.5) — **both absent from the corpus.**

So the "promoted" population is not merely shape-gated rather than content-gated;
under the *current* formula it is **empty**. The historical "2,351" was minted
under an earlier, more permissive formula (pre-Fire-#141). The Fire #141 retune —
correct on its own terms, to suppress trivial parity records — has the side
effect that the entire May corpus, generated under the old formula, is now
**non-promotable**. The promotion count is a fossil of a superseded gate.

The content-replay stage (F2 / `_evaluate_relation`) therefore never fires on
this corpus — nothing reaches the shape gate to be content-checked. The stage is
retained because it is the correct replay for records that *do* promote going
forward (and for the kernel/`discovery_promotion` path if its store is ever
repopulated). On THIS corpus the verdict is upstream of it.

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
