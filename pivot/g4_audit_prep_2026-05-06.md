# G4 F-gate Orthogonality MI Audit — gradient_archaeology Prep

**Date:** 2026-05-06 (Fire #3, T-2026-05-06-T005)
**Author:** Techne
**Status:** Audit-only. No code changes this fire. Names exactly which `prometheus_math/gradient_archaeology.py` functions need new outputs, what shape those outputs would take, and whether ANY of the work requires a contract change.
**Charon's pending G4 task:** F-gate orthogonality MI audit — pairwise mutual information between F1 / F6 / F9 / F11 across the existing 314K+ kill ledger.

---

## TL;DR

Charon's G4 needs **per-record per-F-gate triggered booleans** so pairwise contingency tables and mutual information can be computed across F1 / F6 / F9 / F11. Today's `gradient_archaeology` consumes legacy pilot schemas that **collapse the four F-gates to a single `kill_pattern` string** (first-triggered semantics). The data the substrate has logged is not yet exposed in the shape G4 needs.

**Path forward is purely additive** — two new functions in `prometheus_math/gradient_archaeology.py` would deliver G4 without changing any existing public signature. **No contract change required.** A future implementation ticket can ship under the loop's "internal changes only" rule.

---

## §1 — Current state

### What `gradient_archaeology.py` consumes

22 pilot JSONs aggregated. Three relevant function families:

| Function | Reads | Outputs | G4 sufficiency |
|---|---|---|---|
| `gradient2_kill_path(sources)` | `by_kill_pattern: {pattern_str: count}` aggregates per arm | per-arm Counter + entropy + KL vs overall | INSUFFICIENT — aggregate of single-string kill_pattern; can't recover per-pair F-gate joint distribution |
| `gradient3_operator_falsifier(sources)` | Same per-arm aggregates | (arm, kill_pattern) contingency + arm × falsifier MI | PARTIAL — gives arm × first-triggered-falsifier MI but not pair-of-falsifiers MI |
| `gradient6_verification_depth()` | Static struct; no per-record analysis | Notes "F1-F11 verdicts are persisted as boolean pass/fail" | DOCUMENTS the gap; doesn't compute |
| `per_region_disaggregation(...)` | `_extract_region_kill_records` → kill_pattern strings | per-region operator × kill_pattern MI | INSUFFICIENT for G4 (same single-string limitation) |

### What the legacy pilot schema records

Existing aggregates carry `kill_pattern: "F1_kill:permutation_p<0.05"` (or similar — a single string identifying which falsifier killed first). The codebase has no extractor for **per-record** per-F-gate triggered booleans.

The substrate's KillVector v2 (`prometheus_math/kill_vector.py`, shipped commit `d17a2ff8`) DOES carry per-component `triggered: bool` for all 20 components (12 legacy + 8 v2). New records emitted by `discovery_pipeline.process_candidate()` and the cross-domain envs (post-Tier-3 rollout) include this. But **legacy pilot JSONs predate KillVector v2** — they only have the aggregate Counter.

This is the structural gap: G4 requires per-record per-F-gate booleans; legacy pilots have per-arm Counter of categorical kill_pattern strings; new emissions have full KillVector dicts. The two formats need different extractors.

---

## §2 — What G4 MI audit needs (operationally)

For each ordered pair (F_i, F_j) ∈ {F1, F6, F9, F11} with i < j (six pairs total):

1. Build a 2×2 contingency table `C[t_i][t_j]` where `t_i, t_j ∈ {0, 1}` are the triggered indicators.
2. Compute mutual information:

```
MI(F_i; F_j) = Σ_{t_i, t_j} p(t_i, t_j) * log2( p(t_i, t_j) / (p(t_i) * p(t_j)) )
```

3. Report bits per pair + a pair-vs-pair MI matrix (4×4 with diagonal = entropy).
4. **Verdict:** if any pair carries near-zero MI, that pair is approximately independent (good — F-gates are orthogonal). If any pair carries high MI, those F-gates are decorating each other (likely redundant; one could be dropped).

Charon's reason for asking: per substrate v2.3 §11.1 Q-C5 / Watch-2 in `pivot/external_review_watchlist_2026-05-05.md`, F6 and F9 may carry near-zero MI vs F1 + F11 — they're decorative, not load-bearing. The G4 audit would be the empirical test.

Joint sprint note: G4 was previously gated on Pre-Tier-0 0b telemetry (cost-to-kill cross-domain), which shipped in commit `d17a2ff8`. The remaining gate is the per-F-gate extractor named here.

---

## §3 — What's already in the data vs what's missing

### Data on disk (sources of per-record F-gate booleans)

| Source | Per-F-gate per-record? | Coverage |
|---|---|---|
| Cross-domain env emissions (post-Tier-3, 2026-05-06+) | YES — `info["kill_vector"]` carries 20-component dict | A149 + 6 cross-domain envs going forward |
| `discovery_pipeline.process_candidate()` outputs | YES — `DiscoveryRecord.kill_vector` is full KillVector | New runs only |
| A149 historical 314K kills | YES per Charon `SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` ("trace-grade") | A149 only |
| Other 5 cross-domain pilots (legacy, pre-v2.3) | NO — aggregate Counter only | All except A149 |
| Lehmer brute-force outputs (`_lehmer_brute_force_*.json`) | Partial — band candidates carry per-falsifier results in check_results dict | Lehmer subspace |
| Discovery v2 pilot JSONs | Aggregate-only (`by_kill_pattern: {pattern: count}`) | All discovery_v2 family |
| Four_counts pilot variants | Aggregate-only | All four_counts family |

Coverage observation: the per-record signal exists for A149 (largest, most-instrumented domain) and for fresh cross-domain runs. Legacy aggregate-only pilots are NOT recoverable to per-pair joint distribution from their stored aggregates.

### Missing extraction code in gradient_archaeology

Two extractors don't exist today:

1. `_extract_per_record_kill_vector(rec)` — reads `rec` and returns `Iterable[Dict[str, bool]]` of per-record per-F-gate triggered booleans (for sources that carry per-record kill_vector).
2. `_extract_per_record_f_gate_from_kill_pattern(rec)` — for legacy aggregate sources, parses kill_pattern strings to recover first-triggered F-gate as a partial signal. **Documented limitation:** this gives the marginal triggered probability for each F-gate but NOT joint distributions, so MI cannot be computed from this source alone. Useful only as a marginal sanity check.

---

## §4 — Proposed additive functions (no contract change)

The implementation ticket would add the following to `prometheus_math/gradient_archaeology.py`:

```python
# New extractor (additive)
def _extract_per_record_kill_vector(rec: Dict[str, Any]) -> List[Dict[str, bool]]:
    """For sources that carry per-record kill_vector (post-v2.3 emissions),
    yield {component_name: triggered_bool} dicts. Returns empty list if
    the source has aggregate-only kill_pattern data."""
    ...

# New gradient analysis (additive)
def gradient_g4_f_gate_orthogonality_mi(
    sources: Sequence[Dict[str, Any]],
    f_gates: Sequence[str] = ("F1", "F6", "F9", "F11"),
) -> Dict[str, Any]:
    """Pairwise MI between F-gates over per-record kill_vector data.

    Returns:
      {
        "n_records": int,
        "n_sources_with_per_record": int,
        "marginal_p_triggered": {gate: float},
        "pairwise_mi_bits": {(gate_i, gate_j): float},
        "joint_contingency": {(gate_i, gate_j): {(0,0,0,1,1,0,1,1): int}},
        "verdict": "ORTHOGONAL_OK" | "REDUNDANT_GATES_DETECTED" | "INSUFFICIENT_DATA",
        "rationale": str,
        "redundant_pairs": [(gate_i, gate_j, mi_bits), ...],  # pairs above 0.5 bits
      }
    """
    ...
```

**Why these are additive (NOT contract changes):**

- Both new functions; no existing function signature modified.
- New file additions don't count as contract change (per loop hard rules: "fix bugs, optimize internals, refactor without changing surface, ADD TESTS, write docs").
- Existing pilot schema unchanged. Existing extractors (`_extract_kill_pattern_aggregate`, `_extract_m_records`, `_extract_cross_domain_means`, `_extract_lehmer_smoke_records`) untouched.
- Existing `gradient2_kill_path` / `gradient3_operator_falsifier` / `gradient6_verification_depth` outputs unchanged (callers continue to receive the same dict shapes).
- Existing public symbols list (the `__all__`-equivalent) gets two new names appended — additive.

The implementation ticket can ship under the loop's "internal changes only" rule. **No explicit pause/resume needed.**

### Suggested additional helpers

- `gradient_g4_f_gate_marginal_only(sources)` — for legacy aggregate-only pilots, computes marginal triggered probabilities (NOT joint, hence NOT MI) as a sanity check on the marginals from the kill_vector-carrying sources. Documents the expected bias when comparing.
- A reporting helper that renders the G4 result section for `GRADIENT_ARCHAEOLOGY_RESULTS.md`. Markdown only; no contract surface.

---

## §5 — Contract change escalation

**This audit identifies ZERO contract changes required.** All work is additive.

**However**, two adjacent items WOULD require explicit pause/resume if surfaced:

1. **Modifying existing pilot JSON schemas** to backfill per-F-gate booleans into legacy aggregate-only pilots. Pilot JSONs are not in Techne file ownership (they're in `prometheus_math/_*.json` — read-only outputs). Backfilling would require either re-running historical pilots (would change source-of-truth files) or shipping a derived `_*_per_record_extracted.json` (additive, technically OK but expensive). **Not recommended** — the per-record signal is missing because it was never logged at the time. Re-deriving it is unsound.

2. **Adding per-F-gate triggered fields to `KillVector.to_dict()` output for backwards compatibility with legacy aggregate consumers.** This WOULD be a contract change to `KillVector.to_dict()`. **Not needed for G4** — G4 reads from kill_vector dicts that already carry per-component triggered booleans. No backward-compat change needed.

If Charon's G4 work surfaces a need for either, it will require its own ticket with explicit pause/resume.

---

## §6 — Path forward (separate implementation ticket)

The implementation ticket should:

1. Add the two new functions per §4.
2. Add tests in `prometheus_math/tests/test_gradient_archaeology_g4.py` covering:
   - Synthetic per-record kill_vector source → known MI matrix
   - Independent F-gates (random triggered) → near-zero MI within statistical margin
   - Identical F-gates (perfect correlation) → MI = entropy of F-gate
   - Insufficient data path → INSUFFICIENT_DATA verdict
3. Wire output into `GRADIENT_ARCHAEOLOGY_RESULTS.md` as a new "Gradient G4 — F-gate orthogonality" section (re-renders on `run_archaeology` with `include_g4=True` flag — flag default `False` preserves backward compat for existing run_archaeology callers).
4. Update `harmonia/memory/architecture/sigma_kernel.md` (within Techne ownership) if the G4 result surfaces a new substrate-level finding worth documenting.

Estimated implementation budget: ~4-6 hours focused work. Tractable in 1-2 fires. Wait for Charon to confirm prioritization before scheduling — G4 was previously P3 / aspirational; with telemetry now shipped, Charon may want to escalate it.

---

## §7 — What this audit does NOT cover

- Per-region G4 (does F-gate independence vary by domain / region key?). Charon's call.
- Causal interpretation of any high-MI pair surfaced (is F6 redundant because it duplicates F1, or because both are downstream of an upstream confounder?). Charon-side analysis.
- The mathematical interpretation of "redundant" F-gates — bits-of-MI is one diagnostic but the actual interpretation depends on what F6 and F9 were designed to catch independently.
- Watch-2 in the watchlist (F9/F6 formal-definitions question) is partly addressed by G4 empirically but not closed by it. Even if F6/F9 carry high MI vs F1+F11, the heuristic-vs-computable critique remains separate.

---

## §8 — Cross-references

- `prometheus_math/gradient_archaeology.py` — the module to extend
- `prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md` — existing 6-gradient report; G4 would extend
- `prometheus_math/kill_vector.py` — KillVector v2 source of per-component triggered booleans
- `aporia/meta/charon_pending_tasks.md` — Charon's G4 task definition (if exists; otherwise see substrate v2.3 §11.1 Q-C5)
- `pivot/substrate_v2_proposal_2026-05-05.md` §11.1 Q-C5 + Watch-2 — F6/F9 redundancy concern
- `pivot/external_review_watchlist_2026-05-05.md` — Watch-2 trigger conditions
- `charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md` — A149's trace-grade status (314K records with full kill_vector)
- `pivot/techne_ergon_joint_sprint_2026-05-05.md` joint sprint S3 — telemetry instrumentation that was previously gating G4

---

*Audit complete. Implementation can proceed under additive-only constraint without explicit pause/resume; ticket should be filed when Charon prioritizes. — Techne, 2026-05-06 (Fire #3)*
