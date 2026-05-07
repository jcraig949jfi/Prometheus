# Substrate-Tester Fire Log

Persistent journal across substrate-tester /loop fires. Each entry is one fire (newest first).

Author: substrate-tester (Charon-aligned), per pivot/substrate_v2_proposal_2026-05-05.md and aporia/meta/pressure_appliers/PRESSURE_PROMPTS_v1.md sections 13-22.

---

## Fire #2 — 2026-05-06 20:35 UTC

**Lanes selected:** 2 (adversarial-CLAIM) + 9 (NearMissCorpus-leak).

**Lane rationale:** Per fire #1 standing recommendation. Avoided lanes 1 + 7 (anti-repeat). Picked orthogonal axes: input-validation discipline (lane 2) vs view-isolation discipline (lane 9). Both have shipped substrate code (`sigma_kernel/coordinate_chart.py`, `prometheus_math/learner_corpus.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_2_harness.py`.
**Results JSON:** `charon/diagnostics/substrate_tester_fire_2_results.json`.

### Lane 2 — adversarial-CLAIM: 4 PASS / 1 FAIL

5 ill-formed probes against `SigmaKernel.CLAIM`, `CoordinateChart`, and `DiscoveryPipeline.process_candidate`:

| Probe | Verdict | Detail |
|---|---|---|
| P1 — `SigmaKernel.CLAIM(precision_metadata="string")` | **PASS** | TypeError: precision_metadata must be a dict or None |
| P2 — `CoordinateChart(domain="")` | **FAIL** | Silently accepted. Validator inconsistency. **→ ticket T-2026-05-06-ST002 (P1-high).** |
| P3 — `CoordinateChart(domain="lehmer:bad")` | **PASS** | ValueError: domain must be colon-free non-empty string |
| P4 — `CoordinateChart(coordinate_system=["x","y"])` | **PASS** | TypeError: coordinate_system must be a tuple |
| P5 — `DiscoveryPipeline.process_candidate(mahler_measure="not_a_number")` | **PASS** | TypeError surfaces at band-check comparison (cleanly typed) |

**Key finding (FAIL P2):** `CoordinateChart.__post_init__` (sigma_kernel/coordinate_chart.py:248-251) checks `isinstance(domain, str)` AND `":" not in domain` but does NOT check non-empty — even though the error message at line 250 reads "must be a colon-free non-empty string" and the sibling `region_key` validator at line 252 DOES enforce non-empty. Validator and contract disagree. Empty-domain charts would produce chart_id like `:region_key` with downstream `_split_chart_id` semantic corruption.

**Substrate verdict:** 4/5 PASS. P2 is a real input-validation gap. **Ticket T-2026-05-06-ST002 filed (P1-high).**

### Lane 9 — NearMissCorpus-leak: 4/4 PASS

| Test | Verdict | Detail |
|---|---|---|
| T1 — `load_post_view(allow_post_falsification=False, ...)` | **PASS** | PostFalsificationLeakageError raised with informative message |
| T2 — `load_post_view(allow_post_falsification=True, caller_id=..., purpose="audit")` | **PASS** | Loaded 3 views; 1 leakage-log entry written for caller |
| T3 — `load_post_view(True, "caller", "purpose")` (positional) | **PASS** | TypeError raised — kw-only enforcement is real, not decorative |
| T4 — `loader.load()` default | **PASS** | 3 pre-views returned; no kill_vector or post-falsification fields leaked |

**Substrate verdict:** PASS. Anti-leakage discipline is enforced at the typing layer; opt-in flag is mandatory; audit log is written; default load is leak-safe.

### Tickets filed this fire

**1 ticket (P1-high):** `T-2026-05-06-ST002` — CoordinateChart accepts empty domain. See `aporia/meta/queue/techne_inbox.jsonl`.

### Standing recommendations for next fire (#3)

1. **Anti-repeat:** avoid lanes 2 + 9. Suggested fire #3: Lane 4 (cross-domain-leak) + Lane 8 (ExclusionCertificate-extension), or Lane 3 (correlated-triangulation).
2. **Stratified in-band sampler still pending.** Will become valuable when fire returns to Lane 1.
3. **Lane 5 (large-scale-enumeration)** still queued. Defer.
4. **Lane 6 (undecidable-canonicalization)** path resolution: code lives at `prometheus_math/canonicalizer_observability.py`. When Lane 6 is selected, treat that as the protocol entry-point.
5. **Watch CoordinateChart fix:** if Techne resolves T-2026-05-06-ST002, future Lane 2 fires should re-probe to confirm the regression is closed.

### Fire-2 stress on substrate health

**Positive:**
- 4/5 lane-2 probes correctly rejected ill-formed input — substrate's typed-primitive discipline is mostly working.
- Lane 9 view-separation enforcement is fully working: kw-only flag, mandatory caller_id + purpose, audit log on every load, leak-safe default.
- `PostFalsificationLeakageError` message is clear and actionable.

**One real flaw:**
- `CoordinateChart` empty-domain validator gap (P1-high; ticket filed).

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward established frameworks observed in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~28 minutes (within 50-minute cap).
- Anti-flooding cap: 1 ticket filed (max 5 allowed).

— substrate-tester, fire #2, 2026-05-06 20:35 UTC

---

## Fire #1 — 2026-05-06 19:28 UTC

**Lanes selected:** 1 (CLAIM-flood) + 7 (precision-gradient).

**Lane rationale:** First fire (no anti-repeat constraint). Avoided lane 5 (large-scale-enumeration — full-cap-only). Picked lanes that exercise orthogonal axes (throughput-correctness vs precision-stability) and have shipped substrate code (`prometheus_math/discovery_pipeline.py`, `prometheus_math/lehmer_path_a.py`).

**Harness:** `charon/diagnostics/substrate_tester_fire_1_harness.py` (reproducible).

**Results JSON:** `charon/diagnostics/substrate_tester_fire_1_results.json`.

### Lane 1 — CLAIM-flood: PASS

- 100 probes generated: 70 random degree-10 palindromes + 25 perturbed-near-band (from real INCONCLUSIVE deg-14 ±5 half-coeffs) + 5 structural (Lehmer, Phi_3, Phi_5, x⁴-1, dummy).
- Submitted via `DiscoveryPipeline.process_candidate(coeffs, mahler_measure)` against fresh `SigmaKernel + BindEvalExtension`.
- 100/100 completed; 0 errors; wall clock 5.93 s.
- Throughput: **16.87 claims/sec** (above 10/sec P2 threshold).
- Terminal-state distribution: `{REJECTED: 100}` (no PROMOTE; no SHADOW_CATALOG explicitly counted).
- Kill-pattern root distribution: `{out_of_band: 99, known_in_catalog: 1}`.
- The single `known_in_catalog` hit is consistent with Lehmer's polynomial (M ≈ 1.176) correctly routed to the catalog cross-check.

**Substrate verdict:** PASS. Substrate correctly routed every probe; out-of-band candidates were Phase-0 killed before issuing a CLAIM, in-band catalog match was correctly identified.

**Probe-design note (NOT a substrate flaw):** the kill-pattern skew (99% `out_of_band`) is a probe-design artifact — my "near-band perturbed" probes didn't preserve in-band M after perturbation. Future CLAIM-flood fires should use a stratified in-band sampler (rejection-sampling on M ∈ (1.001, 1.18)) so the F1/F6/F9/F11 falsifier panel actually gets exercised. Filing this as a fire-log calibration note rather than a ticket because it is probe-construction, not substrate behavior.

### Lane 7 — precision-gradient: PASS

- Borderline INCONCLUSIVE entry from deg-14 ±5 brute-force results (entry #1 of 17): coeffs_ascending = [1, -4, 5, 0, -5, 4, -1, 0, -1, 4, -5, 0, 5, -4, 1]; M_numpy ≈ 1.00314; M_mpmath = NaN; has_cyclotomic_factor = True.
- Submitted via `lehmer_path_a.high_precision_M_via_factor` at dps ∈ {10, 30, 60, 100, 200}.
- All 5 dps values returned **M = 1.0 exactly**, status=ok, no exceptions.
- Precision_digits **recorded at every level** (10, 30, 60, 100, 200 propagated correctly into the output dict).
- M_spread = 0.0; band_status = `out_of_band` at every dps (M = 1.0 < 1.001).
- No verdict oscillation across precision levels.
- No precision-aware caveat needed (verdict is stable; substrate doesn't need to fire `precision_below_expected` because verdict converges already at dps=10).

**Substrate verdict:** PASS. Verdicts converge as precision increases (constant at 1.0); precision is recorded; no oscillation; no critical bugs.

**Substantive observation (substrate-grade, not a flaw):** the original `M_numpy ≈ 1.00314` reading was numerical noise. Under `mpmath.factor_first` at any dps ≥ 10, the polynomial decomposes as a *pure cyclotomic product* with M = 1.0 — fully classified, no Lehmer-band hit. This validates Path B's day-5 finding: at the boundary, **strategy** (factor-first vs direct) is the discriminating axis, not **precision**. Substrate is correctly handling the cross-method asymmetry.

### Tickets filed this fire

**0 tickets.** Both lanes PASS. The lane-1 kill-distribution skew is probe-design, not substrate. Documented in fire log per discipline note "File tickets only for ACTUAL failures, not subjective preferences."

### Standing recommendations for next fire

1. **Stratified in-band sampler for CLAIM-flood probes.** Future Lane 1 fires need a generator that actually produces in-band candidates. Rejection-sampling on M ∈ (1.001, 1.18) is the cheapest correct approach; better: walk the Mossinghoff catalog and perturb known small-M polynomials by single-coefficient flips, accepting only perturbations that stay in band.
2. **Avoid Lane 1 + Lane 7 again immediately.** Anti-repeat protocol. Suggested fire #2: Lane 2 (adversarial-CLAIM) + Lane 9 (NearMissCorpus-leak), or Lane 4 (cross-domain-leak).
3. **Lane 5 (large-scale-enumeration)** is queued but takes the full cap. Defer to a fire that has nothing else queued.
4. **Lane 6 (undecidable-canonicalization)** path expectation is wrong: spec says `sigma_kernel/canonicalization_protocol.py`, but the code lives at `prometheus_math/canonicalizer_observability.py`. Will file an ENGINEERING_FAIL ticket if Lane 6 gets selected and the protocol entry-point is genuinely missing.

### Fire-1 stress on substrate health (positive observations)

- All key v2 primitive code IS shipped: `sigma_kernel/{coordinate_chart,exclusion_certificate,method_spec,triangulation_protocol}.py` + `prometheus_math/learner_corpus.py`.
- `DiscoveryPipeline + SigmaKernel + BindEvalExtension` compose cleanly; no import or wiring failures.
- Phase-0 band check fires correctly (out_of_band kill_pattern emitted with full kill_vector).
- High-precision factor-first method records precision_digits as documented.

### Discipline notes

- No paper/publication mentions in this fire (per `feedback_exploration_not_papers.md` HARD RULE 2026-05-06).
- No drift toward "let's refactor to use [established library]" detected in the substrate code I read this fire (per `feedback_anti_gravitational_well.md` HARD RULE 2026-05-06).
- Time used: ~32 minutes (within 50-minute cap).

— substrate-tester, fire #1, 2026-05-06 19:28 UTC
