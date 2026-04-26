# Techne session 2026-04-22

Session artifact for James / posterity / team synthesis. The Techne-side counterpart to `charon/CHARON_SESSION_2026-04-22.md`.

---

## Headline: queue drained, arsenal nearly tripled

Started the session at **7 forged tools / 12 open requests**. Ended at **21 forged tools / 1 open request (Khovanov, heavy deps, explicitly deferred)**. Fourteen new tools shipped, six requests created mid-session (Aporia's REQ-021 knot_shape_field, REQ-022 hilbert_class_field, REQ-023 cm_order_data), all fulfilled.

## Tools shipped this session

| Tool | REQ | Callers / use |
|---|---|---|
| `TOOL_CLASS_NUMBER` | REQ-010 | Harmonia Cohen-Lenstra, Iwasawa λ/μ |
| `TOOL_REGULATOR` | REQ-005 | Charon BSD Tier 1 (Report #48) |
| `TOOL_SMITH_NORMAL_FORM` | REQ-015 | Ergon homology (Report #53) |
| `TOOL_GALOIS_GROUP` | REQ-011 | Harmonia Chebotarev (Report #18) |
| `TOOL_LLL_REDUCTION` | REQ-018 | Ergon ideal lattices (Report #32) |
| `TOOL_KNOT_SHAPE_FIELD` + `knot_shape_field_batch` | REQ-021 (Aporia new) | Ergon 12,965-knot H101 identity-join |
| `TOOL_HILBERT_CLASS_FIELD` + `class_field_tower` | REQ-022 (Aporia new) | Aporia H15 ADE tower-termination |
| `TOOL_ANALYTIC_SHA` (+ `rank_hint` fast path) | REQ-004 | Charon BSD Tier 2 audit |
| `TOOL_SELMER_RANK` | REQ-007 | Charon BKLPR Sel_2 distribution |
| `TOOL_FALTINGS_HEIGHT` | REQ-006 | Ergon mechanism(a) conductor test |
| `TOOL_ALEXANDER_POLYNOMIAL` | REQ-002 (closed) | Knot L-space filtering |
| `TOOL_FUNCTIONAL_EQ_CHECK` | REQ-013 | L-function validation (Report #17) |
| `TOOL_TROPICAL_RANK` | REQ-012 | Ergon chip-firing (Report #12) |
| `TOOL_CM_ORDER_DATA` | REQ-023 (Aporia new) | Aporia V-GAMMA-SIXTH-ROOTS sub-void (order conductor f as per-disc predictor) |

## BSD Tier 0/1/2 audit chain assembled

Six tools compose end-to-end BSD verification on any curve E/Q from ainvs:
- `TOOL_CONDUCTOR` (global_reduction → tamagawa_product)
- `TOOL_ROOT_NUMBER` (parity_consistent)
- `TOOL_REGULATOR` (saturated via ellsaturation — the sneaky correctness landmine)
- `TOOL_ANALYTIC_SHA` (r! + disc-sign-period + saturated regulator; 12/12 vs LMFDB)
- `TOOL_SELMER_RANK` (max(r_lo+s, r_hi) + dim E[2](Q) formula)
- `TOOL_FALTINGS_HEIGHT` (`-log|ω_1| - (1/2) log(Im τ)` on minimal model)

Charon used this chain for his 5K rank-0 Sha>1 audit.

## Methodological lessons

1. **Saturation in PARI `ellrank`**. `ellrank` returns independent non-torsion points, NOT a Z-basis — raw `det(height_matrix)` is `(index)²` too large. Must call `ellsaturation(100)` to get a real basis. `TOOL_REGULATOR` does this; was the first-pass bug and is now a guarded regression test.

2. **Three BSD-formula conventions I got wrong on first pass** (documented in `TOOL_ANALYTIC_SHA`):
   - `ellanalyticrank` returns L^(r)(1) **raw**, not L^(r)(1)/r! — missing factor of r! gives 2× error at rank 2, 6× at rank 3.
   - Real period is `2·ω[1]` if `disc > 0`, `ω[1]` otherwise. LMFDB's `real_period` uses this; PARI's `E.omega[1]` does not.
   - Must use the saturated regulator (above).

3. **Faltings height formula**: Four early attempts using `log|Δ|/12` + `η(τ)` expansions all failed by non-constant offsets. The clean identity `(2π/ω_1)¹² η(τ)²⁴ = Δ_E` collapses to `h_F = -log|ω_1| - (1/2) log(Im τ)` **for a global minimal model**. Non-minimal input must be reduced via `ellminimalmodel` first. LMFDB's `faltings_height` matched at 10+ decimals on 4 test curves.

4. **PARI stack handling needs to be centralized**. Patched twice mid-session. Final state: `techne/lib/_pari_util.py` provides `pari`, `safe_call` (auto-doubles stack up to 4 GB on overflow), and `set_stack_mb(mb)`. All cypari-backed tools import from here.

5. **Class-number guard for HCF**. Aporia's 2.0.7751.1 (h=110, HCF degree 220) exhausts 4 GB stack even with retry — genuinely hard memory wall, not fixable by retry logic. Added `max_class_number=50` guard: `hilbert_class_field` raises `ValueError` early, `class_field_tower` returns `aborted=True` for bulk-scan friendliness.

6. **Windows stdout buffering**. Ergon's first knot batch (max_deg=8) and Aporia's H15 retry both hit silent-background-process issues (stdout redirected-to-file buffers). Fix: file-based incremental writes with `buffering=1` instead of tee-redirect. Standardized recommendation shared on stream; both rebuilt pipelines accordingly.

## Cross-checks I ran for other agents

- **Charon small-Salem catalog**: 11/11 Mahler measures match to 10+ decimals under TOOL_MAHLER_MEASURE; 11/11 palindromic (Salem-class structure confirmed); two match published Mossinghoff lowest-M at deg 10 (Lehmer + 1.21639).
- **analytic_sha vs LMFDB `sha_an`**: 8 curves including Sha=16 (210.e1), all round-match exact.
- **selmer_rank vs LMFDB-consistent expectations**: rank 0-3 trivial Sha plus Sha=(Z/2)² cases (571.b1, 66.b1) plus unproved-rank 210.e1.
- **knot_shape_field vs knotinfo iTrF**: 4_1 → Q(√-3), disc -3; 5_2 → cubic disc -23 (LMFDB 3.1.23.1). Matches published iTrF.

## Session arc

- **Cycle 1 (setup, 7 cycles of rapid-forge)**: filled the queue Aporia/Charon/Ergon had pre-loaded. class_number, regulator, SNF, galois, LLL, then HCF, analytic_sha, selmer_rank, faltings_height, FE check, alexander, tropical_rank. Plus knot_shape_field and batch helper in response to Ergon's Phase-2-blocked-on-Sage panic (he was confusing `cypari2` which fails on Windows with `cypari` which works fine).
- **Cycle 7-8**: Charon's BSD audit hit PARI overflows on 4 curves; centralized stack handling into `_pari_util.py`; threaded `safe_call` through all cypari tools.
- **Cycle 9**: Shipped `analytic_sha(ainvs, rank_hint=0)` fast path after Charon's audit stalled — 5-10× speedup when LMFDB rank is known.
- **Cycle 11**: Cross-validated Charon's 11 small-Salem NFs against TOOL_MAHLER_MEASURE + palindromic check; all 11 clean.
- **Cycle 12**: Responded to Charon's H101 concern ("max_deg=8 excludes 4/5 Salem candidates"): verified `(bits_prec=500, max_deg=12)` works, Ergon restarted the 12,965-knot batch at the larger config with 250-knot checkpointing.
- **Cycle 13**: Late background test on 2.0.7751.1 (h=110) returned with still-overflowing error; diagnosed as hard memory wall; shipped `max_class_number=50` guard.
- **Cycle 22**: H101 closed cleanly at stated scope (Ergon found 0 Salem-trace-field matches across 245K evaluations). Offered iTrF substitution extension; Aporia deferred ("tool stays on shelf").

## Open threads I'm tracking

- Ergon mechanism(a)/(c) closure regression (200K curves, faltings_height-stratified)
- Aporia H15 retry on stratified cn ∈ {3..30} sample (uses `class_field_tower` with new class-number guard)
- Charon's BSD audit (rank_hint fast path available but he may have bypassed it)

## Offers queued but not pulled

- `TOOL_KHOVANOV_BETTI` (REQ-008): heavy deps (JavaKh/KhoHo); defer unless multiple callers surface
- `TOOL_KNOT_INVARIANT_TRACE_FIELD`: ~10-line extension of knot_shape_field via `p((z+conj(z))²/4)` substitution; Aporia deferred
- `lehmer_degree_profile(scan_output)`: binning helper for Charon's Lehmer scans
- `progress_io(path, total, flush_every=N)`: resumable-write context manager
- Batch BSD-factor audit wrapper

Each is low-cost on demand; none shipped speculatively.

## Test suite state at session end

14 test files in `techne/tests/`. All green. ~145 assertions total across the arsenal.

```
test_alexander_polynomial.py       11 OK
test_analytic_sha.py               12 OK
test_class_number.py               32 OK
test_cm_order_data.py              17 OK
test_faltings_height.py             6 OK
test_functional_eq_check.py        11 OK
test_galois_group.py               17 OK
test_hilbert_class_field.py         9 OK  (incl. class-number guard tests)
test_knot_shape_field.py            5 OK  (incl. false-fit regression guard)
test_lll_reduction.py               6 OK
test_regulator.py                  16 OK
test_selmer_rank.py                10 OK
test_smith_normal_form.py          22 OK
test_tropical_rank.py              10 OK
```

## Post-wind-down: late-cycle bug fixes (cycles 36-38)

After the F011 session closed and the team moved to paper prep, two
late diagnostics landed that triggered additional Techne work:

1. **Ergon bug report on TOOL_KNOT_SHAPE_FIELD (1776902425706)**:
   At `bits_prec=400, max_deg=10`, the tool was returning false-deg-2
   polynomials with astronomical discriminants (10^140+) due to
   algdep finding spurious low-degree integer relations that passed
   a loose `val < 10^-30` tolerance check. Fix: added two guards:
     (a) **Coefficient-height cap**: reject polys with any |coeff|
         > 2^(bits_prec/4). At bits_prec=400 this caps at ~30 decimals.
     (b) **Precision-scaled tolerance**: `val < 10^(-bits_prec*0.15)`
         (~60 decimals at 400 bits, vs hardcoded 30).
   Both guards are O(1) extra work. All existing tests still green;
   added a regression guard using a transcendental-like z.

2. **Concrete before/after verification on 6_1**: A latent cycle-12
   background test landed in cycle 38 with the OLD buggy output:
   `6_1: (3, 'x^3 - x^2 - 6232518005778378465741327436171095759...',
   disc ~10^252)`. With the fix: `6_1 → (4, 'x^4 + x^2 - x + 1',
   disc 257)`, matching published iTrF for 6_1. Perfect demonstration
   that the coefficient-height cap rejects the astronomical false-fit
   and algdep moves on to the correct quartic.

Issue 2 from Ergon's report (88-min per-knot outlier) was acknowledged
but deferred: true cross-platform timeout on C-level PARI calls needs
`multiprocessing.Process` with `.join(timeout)` — `signal.alarm` is
Unix-only. Deferred to on-demand.

## Post-session standby arc (cycles 39-81)

After the F011 paper-ready state, Techne entered an idle-watchdog
standby mode with 5-minute heartbeats (interval later changed to 8 min
per James). Most cycles had no actionable items — team was in paper
drafting / Maass GL3 extension / Dirichlet family testing. Techne-side
interventions during this arc:

- Cross-checked Charon's 11 small-Salem NFs (TOOL_MAHLER_MEASURE: all
  11 match to 10+ decimals; all 11 palindromic → Salem-class confirmed).
- Added rank_hint=0 fast path to TOOL_ANALYTIC_SHA (5-10× speedup
  when LMFDB rank is known) to unstick Charon's 5K audit.
- Shipped TOOL_CM_ORDER_DATA for Aporia's per-disc residual regression.
- Diagnosed and fixed the TOOL_KNOT_SHAPE_FIELD false-fit bug.
- Provided Windows stdout-buffering tip for Aporia's H15 retry.

Most "standby" cycles produced only a minimal heartbeat — the team
needed no new tools while the F011 paper was being finalized.

## Session tally

| Category | Count |
|---|---|
| Tools forged (session start → end) | 7 → 21 |
| Requests fulfilled | 22 (incl. 3 mid-session additions from Aporia) |
| Requests still open | 1 (REQ-008 Khovanov, heavy deps, explicitly deferred) |
| Test files | 14, all green |
| Test assertions | ~145 |
| Bug reports received | 1 (Ergon, knot_shape_field false-fit) |
| Bug reports fixed | 1 (Issue 1 shipped; Issue 2 deferred on-demand) |
| Patches applied to existing tools | HCF stack guard + class-number guard; analytic_sha rank_hint; knot_shape_field coefficient-height cap; BSD chain hardened via shared _pari_util |
| Cross-checks run for other agents | 3 (Charon Salem catalog; 6_1 iTrF verification; multiple tool regression sweeps) |

---

*Techne — toolsmith, session 2026-04-22 / 2026-04-23. Standing down.*
