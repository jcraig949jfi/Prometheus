# G01 Intersection — v2 design

**Date:** 2026-05-27
**Status:** v2 design proposal, informed by DR `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/01_g01_intersection_v2_design_audit.md`
**Predecessor:** v1 at `charon/agents/erebos/generators/g01_intersection.py`; composition loader = NONE (emissions short-circuit to `erebos_g01_intersection_pending`).

## 1. v1 state — what we have

- **Plugin tier:** R3 (DNA P10: abstraction / MDL compression of two claims).
- **Cognitive move:** Extract the subject of a Stygian-substantive claim A and impose the Pollux-PROMOTED subset constraint of claim B; surface Hecate cross-gen patterns as ambient context. Output: "Pattern X from A holds when restricted to Subset Y from B."
- **Expected kill_pattern:** `base_rate_failure` (the pattern holds no better inside subset Y than in the global population).
- **Composition loader status:** none. Every G01 emission short-circuits with `stygian_erebos_composed_loader_pending` / `erebos_g01_intersection_pending`. No verdicts have been written through G01.
- **Live substrate finding (if any):** none yet — no loader to fire. The plugin has emitted composed claims but the substrate has never observed their battery result.

## 2. DR-surfaced critical objections (top 3)

The DR (deep-research-pro-preview-12-2025, interaction `v1_ChdkNElXYXQzc0k0dkQtc0FQaTh2QTJRcxIXZDRJV2F0M3NJNHZELXNBUGk4dkEyUXM`, elapsed 273s) raises the following load-bearing critiques. Each is anchored to the DR's primary-source citations.

- **Objection 1 — Naïve Boolean intersection collapses to tautology (semantic aliasing / meet-irreducibility collapse).** v1 builds the composed claim by literal string-restriction ("the Stygian pattern, restricted to the Pollux subset") without ever testing whether the intersection survives in a non-trivial way. The DR's lattice-theoretic analysis predicts that absent semi-distributivity, the meet of two complex claims plunges to ⊥ (universe baseline like "object exists").
  - Source: Cambrian / alt-Tamari lattice factorizations, **arXiv:2605.13770** (DR cite 1); S-Noetherian lattices, **arXiv:2604.26058** (DR cite 2). DR §1.1.
  - Failure mode it predicts: Composed claim is structurally indistinguishable from "both observations involve integers." The downstream battery (when wired) will keep promoting compositions that are tautological aliases of one parent.

- **Objection 2 — No permutation null or codimension test means we cannot distinguish "structural intersection" from "happens to overlap in this finite sample."** The DR's *Triviality Detector* section is explicit: any survivor cohort under a composed predicate must be tested against (a) a codimension-drop test (k₁+k₂ vs max(k₁,k₂)), (b) a permutation-invariant subgroup test (S_n on coefficients), and (c) a cross-fibration nullification against a trivially-defined base space. v1 has none of these.
  - Source: TxGraffiti / The Optimist `dominance_pruned` kill mechanism, **arXiv:2411.09158, arXiv:2507.17780** (DR cites 8, 9); MTDL `pharmacological_orthogonality_failure`, **arXiv:2507.18926** (DR cite 16). DR §2.1, §2.3, §3.
  - Failure mode it predicts: Composed claim survives because its parent constraints are correlated with degree, parity, or some other trivial fibration, not because the intersection isolates a load-bearing core.

- **Objection 3 — Boolean snapshot is blind to dynamical / limit-sequence relationships between the two parent claims.** DR §6 calls this out directly: the load-bearing relationship between two empirical observations is often *transformational* — A morphs into B as degree → ∞, or A ∪ B produces an emergent feature absent from A ∩ B. The Mossinghoff/Salem/cyclotomic example (DR §6) shows the intersection literally cannot represent the relationship that matters.
  - Source: Mossinghoff catalog + Lehmer 1.17628 limit context throughout DR §4; sheaf-theoretic gluing for distributed claim merge, **arXiv:2605.01879, arXiv:2509.25236** (DR cites 3, 4). DR §1.2, §6.
  - Failure mode it predicts: G01 will systematically miss the most interesting Mahler-context structure (Salem-class limit behaviors) because it only ever takes a static slice. This is a class-level blind-spot, not a tuning issue.

## 3. v2 architectural changes

Concrete code-level changes. Each change references (a) what v1 module changes, (b) what new module is added, (c) what tests are updated or added.

### 3.1 Ship the missing composition loader: `composition_g01_mahler_intersection.py`

The single largest gap. v1 has literally no loader; all emissions short-circuit. v2 ships a Mahler-context loader following the pattern of `composition_g11_*` and `composition_g02_*`.

- **What changes:** nothing in `g01_intersection.py` for this change (plugin stays as-is for emission). New loader is the focus.
- **New module:** `charon/agents/stygian/loaders/composition_g01_mahler_intersection.py`
- **Behavior:**
  - `applicable(composed_id, ...)`: matches `composed_id.startswith("EREBOS-G01-")` AND both parent rows resolve to Mahler-context predicates (i.e., at least one parent is bound to a Mossinghoff/Salem/cyclotomic feature). Otherwise REJECT-NOT-APPLICABLE.
  - `build_battery_input`: from each parent row's `claim_payload`, derive an indicator function `pred_i(entry) → bool` over `load_non_cyclotomic_mahler_entries()`; the intersection set is `P_cap = {e : pred_1(e) AND pred_2(e)}`. Union set `P_cup = {e : pred_1(e) OR pred_2(e)}`.
  - `verdict`: applies the three-tier kill protocol from DR §4.4 (see §3.2 below) plus the three triviality detectors from DR §3.1–§3.3 (see §3.3 below).
- **New constants** (calibrated empirically against existing Mahler corpus; values chosen to match the DR's threshold guidance and existing loader conventions):
  - `MIN_INTERSECTION_SIZE = 3` (DR §4.4 over-constraint threshold).
  - `PERMUTATION_NULL_P_THRESHOLD = 0.01` (DR §4.4 null-hypothesis threshold).
  - `N_PERMUTATIONS = 2000` (matches `_mahler_composition_helpers` convention).
  - `CODIMENSION_DROP_TOLERANCE = 0.20` (max fraction by which observed codimension may fall short of k₁+k₂ before triggering `kill_codimension_drop`).
  - `FIBRATION_TVD_THRESHOLD = 0.05` (total-variation distance between intersection's parity/degree-mod-k distribution and background; below this is `kill_cross_fibration_null`).
- **Test updates:**
  - New file `tests/charon/stygian/loaders/test_composition_g01_intersection.py` with at minimum: (i) trivial-containment synthetic (P_cap ≡ P_1) → must emit `kill_intersection_trivial_containment`; (ii) permutation-null synthetic where two predicates correlate with degree but the intersection is just a degree-restriction artifact → must emit `kill_permutation_null_failure`; (iii) genuine non-trivial intersection synthetic (Salem-class ∩ palindromic-coefficient) → must PROMOTE; (iv) over-constrained synthetic (|P_cap| < 3) → must emit `kill_intersection_over_constrained`.

### 3.2 Add the three-tier intersection-quality verdict gate

Implement the DR §4.4 protocol verbatim, inside the new loader.

- **What changes:** new function `_intersection_quality_verdict(pred_1, pred_2, entries) → KillVector | PromoteVector` inside the new loader module.
- **Logic:**
  1. Compute `P_cap`, `P_1`, `P_2`. If `|P_cap| < MIN_INTERSECTION_SIZE` → `kill_intersection_over_constrained`.
  2. If `P_cap == P_1` (as multiset) OR `P_cap == P_2` → `kill_intersection_trivial_containment`.
  3. Compute Mahler-measure infimum shift: `inf(M(P_cap)) - inf(M(P_cup))`. Run `N_PERMUTATIONS` L1-norm-preserving coefficient permutations on catalog entries, recompute predicates, recompute infimum-shift on permuted ensemble; `p_value = fraction of permutations with shift ≤ observed`. If `p_value > PERMUTATION_NULL_P_THRESHOLD` → `kill_permutation_null_failure`.
  4. Else proceed to §3.3 triviality detectors.
- **New constants:** see §3.1.
- **Test updates:** synthetic tests above directly exercise each branch.

### 3.3 Triviality detector battery (codimension drop + permutation invariance + cross-fibration null)

Implement DR §3.1–§3.3 as a single composite detector that runs *after* the §3.2 gate.

- **What changes:** new function `_triviality_detector(pred_1, pred_2, entries) → kill_pattern | None` inside the new loader.
- **Logic:**
  - **Codimension drop:** for each predicate, estimate codimension by `k_i ≈ -log_2(|P_i| / |universe|)`. If `k_cap < (k_1 + k_2) * (1 - CODIMENSION_DROP_TOLERANCE)` → `kill_codimension_drop` (one predicate is a near-alias of the other within the moduli space).
  - **Permutation-invariant subgroup:** apply `pred_cap` to entries whose coefficient tuples are random permutations of an original entry's coefficients. If `pred_cap` survives on ≥ 95% of those permutations (i.e., is essentially S_n-invariant) → `kill_permutation_invariant_intersection`.
  - **Cross-fibration null:** project `P_cap` onto `degree mod 2` (Mahler-context-appropriate trivial base). Compute total-variation distance between the projection distribution and the background catalog's `degree mod 2` distribution. If `TVD < FIBRATION_TVD_THRESHOLD` → `kill_cross_fibration_null`.
- **Test updates:** dedicated synthetic per detector (degree-aliased pair for codim-drop; symmetric-function pair for S_n; parity-uncorrelated pair for fibration null).

### 3.4 Plugin-side: emit predicate handles, not just text

v1 packs the composition as English text. v2 requires the plugin to additionally emit machine-evaluable predicate handles so the loader has a concrete `pred_i(entry) → bool` to work with.

- **What changes:** `g01_intersection.py::_build_claim` extended to populate `composition_payload["pred_handles"] = {"parent_1": <handle>, "parent_2": <handle>}` where each handle is a `{"kind": "salem_class" | "is_smyth_extremal" | "degree_eq" | "mahler_lt" | "palindromic" | ..., "args": {...}}` dict, drawn from a registry shared with Mahler helpers.
- **New module:** small `charon/agents/erebos/generators/_predicate_handles.py` (mirrors `_predicate_lattice.py`) that knows how to map a Stygian or Pollux row's claim_payload onto one of N supported predicate kinds, and raises `UnsupportedPredicate` otherwise. When `UnsupportedPredicate` is raised, the plugin still emits the composed claim but tags it `pred_resolution = "unresolved"`; the loader's `applicable()` will then return False (we won't try to verdict a claim whose predicates we can't evaluate).
- **Test updates:**
  - Extend `tests/charon/erebos/generators/test_g01_intersection.py` (or add) with two cases: predicate-resolvable (full payload present) → handles populated; predicate-unresolvable → `pred_resolution == "unresolved"` and downstream loader REJECT-NOT-APPLICABLE path is exercised.

## 4. New kill_patterns introduced

| kill_pattern | When it fires | Substrate-grade meaning |
|---|---|---|
| `kill_intersection_over_constrained` | `\|P_cap\| < MIN_INTERSECTION_SIZE` (=3) | The two parent claims, conjoined, isolate fewer than 3 objects in the Mahler catalog. The intersection is degenerate — it describes an identity, not a *class*. Substrate learns: this pair of parents lives in incompatible micro-regions of the moduli space. |
| `kill_intersection_trivial_containment` | `P_cap ≡ P_1` or `P_cap ≡ P_2` (set-equal) | One parent is a strict generalization of the other within the catalog. The composed claim is a relabel of the more-specific parent. Substrate learns: a Pollux-PROMOTED predicate dominates a Stygian-substantive predicate (or vice versa); flag the pair to the cross-plugin redundancy ledger. |
| `kill_permutation_null_failure` | Mahler-infimum-shift `p_value > 0.01` under coefficient permutation null | The intersection's apparent ability to isolate low-Mahler-measure entries is indistinguishable from chance. Substrate learns: this composition's "structure" is a sampling artifact; the parent verdicts were independent. (Refines the v1 `base_rate_failure` into a properly-nulled version.) |
| `kill_codimension_drop` | `k_cap < (k_1 + k_2) * 0.80` | Observed intersection retains too few independent constraints — one predicate's information is largely subsumed by the other. Substrate learns: these two parents are not orthogonal observations; mark them as a single composite direction in the predicate lattice. |
| `kill_permutation_invariant_intersection` | `pred_cap` true on ≥95% of S_n-permuted coefficient tuples | The intersection is invariant under full symmetric-group action on coefficients — i.e., it's a zero-information property of the coefficient multiset (sum, product, parity-of-degree, etc.). Substrate learns: composed claim is a *property of the multiset* not the *polynomial*; do not promote. |
| `kill_cross_fibration_null` | TVD(P_cap-projected-onto-base, background-on-base) `< 0.05` | The intersection set is statistically indistinguishable from background when projected to a trivially-defined base (parity / low-degree-mod-k). Substrate learns: no mutual information with Mahler-context dynamics; the "structure" is in the labels, not the polynomials. |

`base_rate_failure` (the v1 expected kill_pattern) is retained as the catch-all if the verdict survives all six gates but still shows no statistical lift; it now means "intersection is structurally non-trivial yet predictively flat," which is a different and rarer substrate signal than the old umbrella-meaning of "no lift, reason unknown."

## 5. Cross-plugin interactions

How v2 changes G01's relationship with neighboring plugins.

- **vs G22 Subgraph/Clique (both multi-row pattern detection):** G22 finds dense subgraphs in the *kill-pattern co-occurrence graph* across the ledger — its inputs are kill_pattern labels and its substrate is the ledger meta-structure. G01 v2 finds non-trivial *predicate intersections in object-space* (Mossinghoff catalog) and its substrate is the catalog itself. Concretely: G22 says "kills A and B tend to co-fire on the same problem_ids"; G01 v2 says "predicates P and Q jointly isolate a load-bearing low-M sub-region of polynomials." After v2, G22 SHOULD treat any sustained `kill_intersection_trivial_containment` cluster across G01 emissions as a candidate clique — that's exactly the predicate-redundancy structure G22 was built to find. Add a downstream Hecate cross-gen rule: `G01.kill_intersection_trivial_containment ⇒ flag pair to G22 candidate-edge set`.

- **vs G12 Invariant-Substitution (substitution-like):** G12 substitutes an *invariant transformation* (e.g., x ↦ -x, x ↦ 1/x, palindromic flip) onto a Stygian claim and asks whether the claim survives. G01 v2 conjoins *two predicates from two separate parents* and asks whether the conjunction is non-trivial. The DR §6 blind-spot — "transformational equivalences as degree → ∞" — is structurally G12's territory, not G01's; G01 v2 explicitly does NOT try to absorb that and instead routes such patterns out via a new emission tag `composition_payload["suggests_g12_handoff"] = True` when both predicates can be expressed as invariants of a common substitution. This is the cross-plugin specialization fix: G01 v2 says "static intersection" and G12 says "transformational equivalence," and an emitted G01 claim that smells transformational gets handed off rather than mis-verdicted.

## 6. Refinement loop trigger

Conditions under which v2 should become v3:

- **Trigger A:** Across the first 100 verdicted G01 emissions, ≥ 80 % terminate in `kill_permutation_null_failure`. That would indicate the loader's permutation null is doing all the work and the upstream G01 plugin is generating overwhelmingly noise-equivalent compositions. v3 should move the null check *upstream* into the plugin's `applicable()` gate (cheaper pre-filtering) and add a smarter parent-pair scoring heuristic.
- **Trigger B:** A frontier review identifies a substrate-grade alternative formulation (e.g., sheaf-theoretic pullback per DR §5.2, or symmetric-difference composer per DR §5.1) that is *not* expressible as a kill_pattern within v2's verdict gate. That means v2's verdict space is the wrong shape and v3 must restructure the composition target itself.
- **Trigger C:** Any single PROMOTE survives v2 but is later killed by a downstream Stygian re-verification at higher precision — proves v2's thresholds were too permissive and the calibration must be tightened.

## 7. Falsification route specification

The exact battery shape an Erebos v2 G01 emission flows through:

```
queue_payload  →  loader.applicable()  →  loader.build_battery_input()  →  verdict
```

- **`applicable(composed_id, claim_payload, ...)`:**
  - Return True iff ALL of:
    - `composed_id.startswith("EREBOS-G01-")`
    - `claim_payload["composition_payload"]["pred_handles"]` exists and both `parent_1` and `parent_2` resolve via `_predicate_handles.RESOLVERS[handle["kind"]]` (no `UnsupportedPredicate`).
    - `claim_payload.get("pred_resolution") != "unresolved"`.
    - At least one of the two predicates is in the Mahler-context family (`{"salem_class", "is_smyth_extremal", "degree_eq", "mahler_lt", "palindromic", "cyclotomic_factor", "degree_mod_k"}`).
  - Otherwise REJECT-NOT-APPLICABLE; G01 emission is logged with `loader_decision = "not_applicable"` and never promoted/killed (distinct from a kill).

- **`build_battery_input()`:**
  - `entries = load_non_cyclotomic_mahler_entries()`  (shared helper, already used by 9 sibling loaders).
  - `pred_1 = _predicate_handles.resolve(handle_1)`; `pred_2 = _predicate_handles.resolve(handle_2)`  (both are pure `entry → bool`).
  - `P_1 = [e for e in entries if pred_1(e)]`; `P_2 = [e for e in entries if pred_2(e)]`; `P_cap = [e for e in entries if pred_1(e) and pred_2(e)]`; `P_cup = [e for e in entries if pred_1(e) or pred_2(e)]`.
  - Return `BatteryInput(entries=entries, pred_1=pred_1, pred_2=pred_2, P_1=P_1, P_2=P_2, P_cap=P_cap, P_cup=P_cup)`.

- **`verdict(battery_input) → Verdict`:** (decision order matters — each gate short-circuits)
  1. If `len(P_cap) < MIN_INTERSECTION_SIZE` → KILL `kill_intersection_over_constrained`.
  2. If `set(P_cap) == set(P_1)` or `set(P_cap) == set(P_2)` → KILL `kill_intersection_trivial_containment`.
  3. Compute Mahler-infimum-shift `obs = inf(M(P_cap)) - inf(M(P_cup))`. Run permutation null (N=2000, L1-preserving coefficient permutation, recompute `P_cap_perm` per draw, recompute `inf(M(P_cap_perm)) - inf(M(P_cup))`). `p = (#{perm : shift_perm ≤ obs}) / N`. If `p > 0.01` → KILL `kill_permutation_null_failure`.
  4. Compute codimension estimates `k_i = -log_2(len(P_i) / len(entries))`; if `k_cap < 0.80 * (k_1 + k_2)` → KILL `kill_codimension_drop`.
  5. Compute S_n-permutation invariance fraction `f_inv`; if `f_inv ≥ 0.95` → KILL `kill_permutation_invariant_intersection`.
  6. Compute `TVD(P_cap_on_parity, background_on_parity)`; if `TVD < 0.05` → KILL `kill_cross_fibration_null`.
  7. If Mahler-infimum-shift is statistically significant (`p ≤ 0.01`) AND none of the above fire → PROMOTE with `kill_vector = {"infimum_shift": obs, "p_value": p, "P_cap_size": len(P_cap), "codim_observed": k_cap, "codim_expected": k_1+k_2}`.
  8. If the verdict reaches here without a PROMOTE (i.e., shift was significant but degenerate in some other way), default to KILL `base_rate_failure` (v1 catch-all, retained).

## 8. Anti-gravitational-well check

The DR — even while flagging the v1 problems — exhibits several conventional gradients. v2 explicitly rejects:

- **Conventional framing 1: "Use sheaf-theoretic pullback / topos-theoretic gluing as the v2 intersection operator" (DR §1.2, §5.2).** This is the LLM-default Tier-1-prestige route: lift the engineering problem into category theory and let the formalism do the work. *Substrate alternative taken:* keep v2 strictly in numerical-empirical territory — Mahler-infimum permutation null + codimension + symmetric-group invariance + fibration TVD. All four are computationally cheap, falsifiable per-emission, and produce specific kill_patterns the substrate can aggregate. Sheaf pullback is parked as a *plugin re-formulation* (a possible future G_X), not as the v2 verdict gate. This honors `feedback_anti_gravitational_well`: traditional mathematics is exhausted; build the substrate's own coordinate system instead of importing one.

- **Conventional framing 2: "Define a Causal-Abstraction-Network-style multi-agent worldview merge" (DR §1.2, citing arXiv:2509.25236).** The DR repeatedly nudges toward distributed-agent causal-model merging. *Substrate alternative taken:* G01's role is *not* worldview merging; it is "do these two empirical observations isolate a non-trivial joint sub-region of object-space?" v2 keeps the question local to a single catalog (Mahler), single tick, two parent rows, no agent-coordination layer. Multi-agent merging is a category error for G01 — it belongs in Hecate's cross-gen layer, not in a composition plugin. The narrative-resistance discipline (`feedback_narrative_resistance`) says: test the simplest mechanism first; the simplest mechanism is "do the predicates jointly carry information against a permutation null."

## 9. Open questions for frontier review

3–5 specific questions where v2 leaves a design choice ambiguous and frontier critique would be load-bearing.

- **Q1.** The Mahler-infimum shift is one of many possible statistics for "non-trivial intersection." Should v2 *also* test (i) median shift, (ii) tail-quantile shift (e.g., 5th percentile), (iii) Kolmogorov-Smirnov against the union distribution? The DR only commits to infimum. Frontier review should identify which statistic is most discriminating for the *known* Salem-cluster structure that ITER-10 already mapped, so v2 calibrates against an empirical anchor rather than a theoretically-motivated guess.

- **Q2.** `MIN_INTERSECTION_SIZE = 3` and `PERMUTATION_NULL_P_THRESHOLD = 0.01` are chosen by analogy to existing loaders. For the Mahler catalog specifically, where many natural intersections will land in the 3–10 object range, is `p < 0.01` over-conservative (kills real structure as noise) or under-conservative (lets sampling artifacts through)? A multi-threshold sweep similar to ITER-18's G17 work should be on v2's near-term roadmap; frontier review should advise whether to ship v2 with the single threshold and revisit, or to ship with a sweep built-in.

- **Q3.** The `_predicate_handles.py` registry defines a finite set of predicate kinds. For any parent row whose `claim_payload` doesn't map onto that registry, the loader REJECT-NOT-APPLICABLEs. What fraction of historical G01 emissions would land in REJECT-NOT-APPLICABLE under a candidate registry of 8 kinds (salem_class, is_smyth_extremal, degree_eq, degree_mod_k, mahler_lt, palindromic, cyclotomic_factor, lehmer_neighborhood)? If > 50 %, the registry is the v2 bottleneck and we need a more aggressive predicate extractor — possibly LLM-mediated parsing of `canonical_claim_text`. Frontier review should advise whether deterministic registry + REJECT is healthier than LLM-mediated parse + best-effort.

- **Q4.** The G01-vs-G12 handoff (§5): how should the substrate detect that a G01 composition is "really" a transformational equivalence in disguise? Naively, "if both predicates are invariants of some substitution s, hand off to G12." But identifying the substitution non-trivially requires symbolic reasoning the substrate doesn't yet have. Should v2 ship the handoff as a *flag only* (G12 picks it up if it independently constructs the same pair) or as an *active routing edge* (G01 emits to G12's input queue directly)?

- **Q5.** v2 keeps G01's plugin-level behavior almost unchanged and concentrates effort in the new loader. Is the right v2 architecture instead a *split*: G01_static (current Boolean intersection, fully nulled) + G01_dynamic (sequence-of-degrees limit composer, DR §6) as two sibling plugins under a shared G01 spec? Frontier review should call this out if v2-as-monoplugin will systematically leave the DR §6 blind-spot uncovered.

## 10. Implementation budget

Rough estimate in iterations (matching the substrate's existing iteration scale; ~1 iteration ≈ one Erebos working cycle).

- v2 plugin update (predicate-handles registry + payload emission tweak in `g01_intersection.py`, plus `_predicate_handles.py` shared module): **1 iteration**.
- v2 loader implementation (`composition_g01_mahler_intersection.py` with all six verdict gates and the three triviality detectors): **2 iterations** (one to scaffold + wire, one to calibrate thresholds against existing Mahler corpus).
- Synthetic-control tests (six tests, one per kill_pattern, plus one PROMOTE-positive synthetic, plus REJECT-NOT-APPLICABLE smoke): **1 iteration**.
- Substrate finding doc (if v2 surfaces any non-trivial PROMOTE within first ~100 verdicted emissions): **1 iteration**, deferred until after first live run.
- Cross-plugin wiring (G22 candidate-edge feed; G12 handoff flag; `kill_pattern` registry updates): **0.5 iteration**, folded into loader iteration.

**Total: 4–5 iterations** to ship v2 to substrate-live and verdicted. Substrate finding doc adds 1 more iteration *if and only if* v2 produces a non-trivial PROMOTE; otherwise the loader's accumulated kill_pattern distribution itself is the finding (and a v3 refinement-loop trigger evaluation per §6).
