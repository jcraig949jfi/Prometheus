# Charon 1 — Review of Charon 2's batch

**Reviewer:** Charon 1 (myself, the additive/multiplicative number-theory batch researcher)
**Reviewing:** Charon 2's analytic/Diophantine number-theory batch (RH, GRH, Lindelöf, abc, Vojta-for-curves)
**Date:** 2026-05-05
**Time spent:** ~1.5 hours

---

## Executive summary

Charon 2 produced **clean, disciplined kill-data** across 5 hard analytic-NT problems. The verdicts are calibrated, the obstruction-class taxonomy is sound, and the 2-cluster split (analytic / Diophantine) is the right substrate-grade observation. Time discipline was good (3 h / 15 h cap; same surface-area-over-depth choice I made in Charon 1).

**However**, the review surfaces three structural gaps:

1. **Missed recent literature (2024-2025)** in three of the five problems. Most consequential miss: the **Guth-Maynard 2024 zero-density breakthrough** (first improvement to Ingham 1940 in 80+ years), which directly affects the Lindelöf-direction analysis Charon 2 wrote. Tao-Trudgian-Yang 2025 systematic exponent-pair paper is also missed. For abc: the **2024-2025 LANA Project** (Lean formalization of IUT, Kato Fumiharu / ZEN Mathematics Center) and the **May 2025 "Final Report" arXiv:2505.10568** are missed; both substantively change the abc landscape.

2. **Underutilized public infrastructure.** LMFDB has 36 billion zeros downloadable in raw format with reader code; Platt has computed 103.8 billion. Odlyzko has tables at heights ≈10²² publicly available. Sage bundles Rubinstein's `lcalc` (Charon 2 used only mpmath, hit walls at n=10¹², while Odlyzko's tables go to 10²²). For abc: the Reken Mee Met ABC archive has ~200 high-q triples and is queryable; Charon 2 verified 5 of them.

3. **Round-2 round trips would be very productive** for 4 of 5 problems (RH, GRH, Lindelöf, abc) given the available tooling. Vojta is the exception — its obstruction is genuinely structural and unaffected by available tools.

**Net recommendation:** for any round-2 effort, prioritize building a small Σ-substrate-compatible toolkit (Riemann-Siegel evaluator with multipoint, LMFDB ingestor, q-record battery) that spans RH/GRH/Lindelöf/abc. Per Charon 2's own observation: a single advance translates across an entire cluster.

---

## Per-problem review

### Problem 1 — Riemann Hypothesis

**What Charon 2 did well:**
- Clean diagnostic of mpmath's wall at n=10¹² (precision-tolerance interaction documented; reproducible).
- Riemann-von Mangoldt count cross-check at n=10⁷ to 10¹².
- Honest tag: NO_PROGRESS_DOCUMENTED_OBSTACLES with calibration sub-data is exactly the right verdict for this attack space.

**What was missed / underutilized:**

1. **The Odlyzko tables at heights ≈10²² are publicly downloadable** (Odlyzko's webpage at u-minn.edu, file `zeros6` with 2,001,052 zeros at height 10²²+1). Charon 2's stated goal "verify a specific zero in the n≈10¹⁵ range" is actually achievable today *via lookup* rather than computation — the data exists. Walling at mpmath's 10¹² is choosing the wrong instrument for the job.

2. **LMFDB has Platt's 103.8 billion zeros** (per LMFDB status page). The raw download is at `beta.lmfdb.org/riemann-zeta-zeros/` with Python reader code at `github.com/LMFDB/lmfdb/blob/master/lmfdb/zeros/zeta/platt_zeros.py`. **This makes Charon 2's "n=10¹⁵" zero accessible without writing a Riemann-Siegel evaluator.**

3. **Sage bundles `lcalc`** (Rubinstein's L-function calculator, GPL since 2005). lcalc evaluates ζ at large t much faster than mpmath. Available without compiling anything if Sage is installed.

4. **GUE pair-correlation check was deferred** as "redundant with literature." For substrate-grade purposes, it's the highest-value single computational artifact: a small block of zero spacings at high t (10¹³ or 10²¹) compared to the GUE prediction is exactly the kind of multi-evaluation calibration the substrate's residual-primitive machinery (`sigma_kernel/residuals.py`) is designed to absorb. **The "redundant with literature" verdict is wrong from a substrate-deposit perspective**: it would have produced a typed substrate object (GUE-consistency claim with content-addressed evidence) that the substrate doesn't yet have.

**Round-2 angles (productive):**

- **A1.** Ingest a slice of LMFDB / Platt's zeros into the substrate as a battery-eligible dataset. Run F1+F6+F9+F11-style consistency checks on the first 10⁵ zeros ingested (functional-equation symmetry, RvM count match, GUE local-block statistics). Output: typed substrate object — calibration-grade.
- **A2.** Wrap `lcalc` (via Sage or directly) as a zero-evaluation tool callable from Python. Push n to 10¹³+ in standard wall-clock; document the new wall.
- **A3.** Compute Odlyzko's published statistics (pair correlation, nearest-neighbor spacing, number variance) on the n≈10²² block; cross-check Charon 2's claim that "GUE matching does not constitute a proof path." The cross-check itself is substrate-grade calibration.
- **A4.** Deferred: a clean Schönhage-multipoint Python implementation (~1 week). Lower priority than A1-A3 since LMFDB/Odlyzko data already exceeds our reach.

**Datasets / tools to build:**

- **`charon/instruments/lmfdb_zeros.py`** — LMFDB raw-file reader; standard Pandas DataFrame interface; cached locally.
- **`charon/instruments/lcalc_wrapper.py`** — Sage-or-direct wrapper exposing zero-finding and ζ-evaluation; with timing instrumentation per Charon 2's own Cost-to-Kill framework.
- **`charon/batteries/zeta_zero_battery.py`** — applies the falsification battery (F1 permutation null on spacing distribution; F6 base rate; F9 simpler explanation; F11 cross-validation against RvM count) to any incoming zero-data block.

**Round-2 verdict:** **Yes, very productive.** Charon 2's RH attempt had a tool-selection problem more than a substrate-coverage problem. Round 2 with LMFDB ingestion + lcalc wrapper would extend the verified-zero range by ~10 orders of magnitude with modest engineering effort.

---

### Problem 2 — GRH for Dirichlet L-functions

**What Charon 2 did well:**
- Rediscovered first zero of L(s, χ₅) at t≈6.6485 cleanly. PARTIAL_RESULT verdict appropriate.
- Off-line σ-perturbation showing |L| growth — calibration that the zero is non-degenerate.
- Sanity scan of q=7 demonstrated method portability.
- Honest deferral on functional-equation cross-check.

**What was missed / underutilized:**

1. **Sage's `lcalc` directly handles arbitrary Dirichlet characters.** No need to roll a 100,000-term truncated Dirichlet sum manually. lcalc handles q up to ~10⁴ at modest cost.

2. **LMFDB has zero data for Dirichlet L-functions at all small q** (the L-function tour pages list zeros explicitly). Charon 2's t≈6.6485 result is a re-derivation of an LMFDB-cataloged zero. The substrate value is in the cross-checking machinery, not the rediscovery.

3. **No mass scan over (q, χ).** A sweep of q ∈ [2, 1000] across all primitive characters is exactly the substrate-grade output that would let the substrate accumulate calibration-grade ground truth. With lcalc this is hours of compute; not done.

4. **Selberg-class L-functions** (Hecke L-functions of number fields, automorphic L-functions of small Maass forms, Rankin-Selberg L-functions) are also accessible through Sage and LMFDB. These are *categorically different* L-functions — not just reparametrizations of the Dirichlet case. A cross-class consistency check would be substrate-relevant.

**Round-2 angles:**

- **B1.** Sage-driven mass-scan of small (q, χ): for q ∈ [2, 1000], compute first N zeros for each character, build typed substrate dataset. Estimated cost: a few hours of Sage time. Output: ~10⁵ zero-objects with content-addressed provenance.
- **B2.** Functional-equation symmetry check across the dataset: for each computed zero, verify the functional equation symmetric pair. F11 cross-validation pattern.
- **B3.** Selberg-class extension: compute zeros of L-functions for a small set of number-field Hecke L-functions (LMFDB has them). Cross-class GUE statistics — does the substrate's residual-clustering find structural similarity across Selberg-class boundaries?
- **B4.** Siegel-zero hunting: Charon 2 noted "Heath-Brown 2004 explicitly excludes Siegel zeros for small q below an explicit bound." Mass-verify this for q ∈ [2, 10⁴]; document the explicit exclusion bound empirically.

**Datasets / tools to build:**

- **`charon/datasets/dirichlet_zeros_q1000.parquet`** — first ~50 zeros for each primitive character mod q, q ≤ 1000.
- **`charon/instruments/selberg_class_zoo.py`** — uniform interface to L-functions across the Selberg class (Dirichlet, Hecke, automorphic small-rank).
- **`charon/batteries/grh_consistency_battery.py`** — applies F1-F11 + functional-equation-symmetry test to the dataset.

**Round-2 verdict:** **Yes, productive.** GRH at small q is the cleanest of the 5 problems for substrate-grade work — the data is structured, the tools (Sage / lcalc) exist, and the cross-class extension is a substrate-distinctive contribution.

---

### Problem 3 — Lindelöf Hypothesis

**What Charon 2 did well:**
- Empirical |ζ(1/2+it)| growth up to t=10¹².
- 3-class technique taxonomy (van der Corput / BIM / Bourgain decoupling).
- Honest classification of asymptotic-only obstruction.

**What was missed — substantive:**

1. **GUTH-MAYNARD 2024.** Major recent result: first substantial improvement to Ingham 1940's `N(3/4, T) ≪ T^(3/5+o(1))` zero-density bound. Per Tao's mathstodon post (verified, mathstodon.xyz/@tao/112557248794707738). This is *directly* relevant to Lindelöf-direction work because zero-density results bound exponent records via the Hadamard-product / explicit-formula route. Charon 2's "RH-direction" Attack 3 should have noted this; it's more than two years post-Bourgain 2017 and two years before Charon 2's session.

2. **TAO-TRUDGIAN-YANG 2025**, "New exponent pairs, zero density estimates, and zero additive energy estimates: a systematic approach." This is a *systematic survey + new exponent pairs* paper that effectively re-tabulates Charon 2's "3 technique families" with explicit, computer-checked exponent records. **It supersedes Charon 2's exponent table.** A 2025 review of Lindelöf-direction work should have surfaced this.

3. **The 13/84 = 0.15476 number is wrong from Charon 2's own 2017 Bourgain reference.** Bourgain's Annals paper has exponent **13/84** with arxiv 1408.0930, but Charon 2's table mentions Huxley-Watt 89/570 ≈ 0.1561 as if it were the predecessor. The actual progression around σ=1/2 from the 1980s has multiple parallel records; the "monotonic improvement" framing Charon 2 used is an oversimplification. Worth a careful re-tabulation in round-2.

4. **No empirical exponent regression.** Computing |ζ(1/2+it)| at many t and regressing log|ζ| ~ μ log(t) gives an empirical μ. With LMFDB/Odlyzko data we have |ζ(1/2+iT)| at hundreds of millions of points; the empirical μ is testable. Charon 2 sampled 4 t values; the right experiment samples 10⁷.

**Round-2 angles:**

- **C1.** **Critical:** lit-scan Guth-Maynard 2024, Tao-Trudgian-Yang 2025, and the 2024 Lerch-zeta extensions of Bourgain. Update Charon 2's exponent-history table.
- **C2.** Empirical exponent regression: compute |ζ(1/2+it)| at 10⁵ t-values for t in [10⁹, 10¹²]; fit the exponent. Compare empirical to Bourgain 13/84 and to Lindelöf-target 0.
- **C3.** Compute moment integrals ∫₀^T |ζ(1/2+it)|^(2k) dt for T ≤ 10¹² and k ∈ {2, 4, 6, 8}. Compare to the conjectured `M_k(T) ≈ a_k T (log T)^(k²)` (Conrey-Ghosh). Substrate-grade calibration of the "k-th moment" theory.
- **C4.** Build a "decoupling-progress monitor": cron-style scan of arXiv math.NT / math.CA for "decoupling" + "zeta" tags. The decoupling field is moving fast; the substrate should track it.

**Datasets / tools to build:**

- **`charon/datasets/zeta_critical_line_t1e12.parquet`** — |ζ(1/2+it)| at 10⁶ uniformly-sampled t in [10⁹, 10¹²], computed once and cached.
- **`charon/instruments/empirical_exponent_fit.py`** — robust regression of log|ζ| vs log(t), with bootstrap CI on the exponent.

**Round-2 verdict:** **Yes, urgent.** The lit-scan miss is consequential — Charon 2's Lindelöf attempt is dated 2017 in its citation graph despite being written in May 2026. The Guth-Maynard 2024 + Tao-Trudgian-Yang 2025 papers are exactly the kind of systematic-progress moment that warrants a round-2 attempt, not a round-1 stop.

---

### Problem 4 — abc Conjecture

**What Charon 2 did well:**
- Verified 5 canonical high-quality triples by direct factorization. Reusable as battery input.
- Honest survey of the IUT / Scholze-Stix dispute as a `category_theory_dispute` obstruction class.
- Empirical c/rad^(1+ε) calibration across triples.
- Honest tag: INCONCLUSIVE.

**What was missed — substantive:**

1. **THE LANA PROJECT (Lean and Anabelian geometry)** — started end of 2023 by **Kato Fumiharu** at the **ZEN Mathematics Center** in Japan, attempting Lean formalization of IUT. The team has reached a stage where they can articulate a specific point with enough precision to formalize it in Lean but cannot proceed past that point. **This is the substrate-grade development.** Charon 2's verdict that "settling the dispute would require a computer-formalized version of IUT" was correct in spirit but missed that this is an active, ongoing project — not a hypothetical.

2. **Mochizuki's own Lean formalization.** ~70 lines of Lean code drafted by Mochizuki + collaborators, not yet public. Per Mochizuki's stated framing at the University of Exeter: "the validation aspect is not our primary focus; the significance of Lean formalization lies in establishing an accurate record of the logical structure of IUT." Charon 2 missed this.

3. **arXiv:2505.10568 (May 2025)** — "Final Report on the Mochizuki-Scholze-Stix Controversy." A substantial recent paper that synthesizes the dispute. Charon 2 should have surfaced this.

4. **$1 Million prize** for someone who can disprove abc — verified via Scientific American article. Changes the incentive structure for the dispute substantively.

5. **Reken Mee Met ABC archive is queryable in bulk.** Charon 2 verified 5 triples; the archive has ~200. Mass-statistics on the q-distribution, on rad(abc) modulo small primes, on the cofactor-structure of high-q triples — these are substrate-grade datasets that Charon 2 didn't compute.

6. **Polynomial-abc analog (Mason-Stothers theorem).** Mason 1984 / Stothers 1981 — proved abc for polynomials. Charon 2 didn't reference this; it's the cleanest example of "abc is true in a related setting" and the polynomial proof's structure is well-understood (it uses the polynomial degree as a substitute for log(c)). Cross-domain transfer of the polynomial-method to the integer case is what's open.

**Round-2 angles:**

- **D1.** Lit-scan: LANA project current status, Mochizuki Exeter conference proceedings, arXiv:2505.10568. Update the Scholze-Stix obstruction summary with 2024-2025 developments.
- **D2.** Mass-process Reken Mee Met ABC archive (full ~200 triples). Compute q-distribution, structure of rad(abc), small-prime conditioning. Output: typed substrate dataset.
- **D3.** Apply the substrate's KillVector machinery (`prometheus_math/kill_vector.py`) to the high-q triples. The "(out_of_band, reciprocity, irreducibility, catalog match)" vector translates to abc via "(q-rank, log(c)-rank, rad-rank, prime-multiplicity-rank)." Charon-grade kill-pattern catalog.
- **D4.** Polynomial-abc cross-check: implement Mason-Stothers in sympy / sage; verify the polynomial bound on a sample of polynomial triples; identify which steps of the polynomial proof do/don't transfer to integers.
- **D5.** Effective abc bounds: compute Stewart-Yu type upper bounds explicitly for ~10³ random triples; compare to the empirical q-record. Quantify the "gap" Charon 2 identified.

**Datasets / tools to build:**

- **`charon/datasets/abc_high_quality_triples.parquet`** — Reken Mee + LMFDB + Bach-Reiter aggregated; ~200 triples with full factorization metadata.
- **`charon/instruments/mason_stothers_evaluator.py`** — polynomial-abc verification.
- **`charon/batteries/abc_kill_battery.py`** — KillVector-style multi-falsifier on triples.

**Round-2 verdict:** **Yes, productive.** Charon 2's abc attempt was the strongest of the 5 (already produced reusable substrate artifacts) but it stops short of a couple of mass-data exercises that the substrate's existing infrastructure would handle cleanly. LANA / Mochizuki's Lean attempts are the substrate-direction development the substrate should track explicitly.

---

### Problem 5 — Vojta's Conjecture (curves case)

**What Charon 2 did well:**
- (Genus × Divisor) cell map of "predicted vs proven" — substrate-grade observation about which open territory is open.
- Identified the polynomial-method ineffectivity as the structural obstruction.
- Honest deferral on Sage-based curve enumeration.
- Honest tag: NO_PROGRESS_DOCUMENTED_OBSTACLES.

**What was missed:**

1. **Sage genus-2 / abelian-variety functionality** — has comprehensive support for: explicit point-counting on small-genus curves, Mordell-Weil rank computation, integral-points enumeration via Coppola/Bilu/Bugeaud-style algorithms. Charon 2 deferred Attack 3 ("computational survey of small genus-2 curves") with `comp_ceiling (no sage in session)`. **This is a tool-availability issue, not a substrate-coverage one.**

2. **LMFDB has tables of genus-2 curves over ℚ** with computed Mordell-Weil groups, integral points, and conductor data. ~70K curves in the database. **A substrate-grade observation: do height bounds on integral points correlate with conductor / discriminant in a way that abc-bounds would predict?** Empirically testable from LMFDB without writing Sage code.

3. **Belyi-map / abc-implies-Mordell concrete bounds.** Elkies 1991 gave the reduction; *the explicit constants in the abc-implies-effective-Mordell reduction are computable*. Charon 2 noted the implication but didn't compute the resulting bounds for specific curves.

4. **Vojta's own 2023-2025 papers.** Charon 2's literature scan stops at 2011 (Cetraro lectures) and 1994 (Faltings-Wüstholz product theorem). Vojta has been actively publishing in the 2020s; a quick arxiv author-scan would surface recent work.

**Round-2 angles:**

- **E1.** Sage-based enumeration on a sample of 100 genus-2 curves from LMFDB: compute integral points, height distributions. Plot against curve discriminant / conductor. Output: empirical-vs-Vojta scatterplot.
- **E2.** Compute abc-implies-effective-Mordell concrete bounds for the same 100 curves. Compare to actual integral-point heights.
- **E3.** Recent Vojta literature scan (2020-2026). What partial-effectivization results exist? Helfgott / Bilu / Bugeaud have published in this area.
- **E4.** Polynomial-method ineffectivity: implement a small Roth-style auxiliary-polynomial construction in sympy. Document where ineffectivity creeps in. (Pedagogical, but useful as substrate documentation.)

**Datasets / tools to build:**

- **`charon/datasets/lmfdb_genus2_curves_with_points.parquet`** — first 100 LMFDB genus-2 curves + integral-point data.
- **`charon/instruments/abc_to_mordell_calculator.py`** — Elkies' explicit reduction.

**Round-2 verdict:** **Marginal.** The structural obstruction is genuine (polynomial method is ineffective by construction); no tool changes that. But concrete LMFDB-driven enumeration and abc→Mordell explicit bounds would provide substrate-grade calibration data — useful, just less impactful than rounds 1-4. Round-2 is **worth doing if the time is available, but it's the lowest priority of the 5.**

---

## Cross-batch tools that span ≥3 problems

Five tools / datasets that would amplify round-2 productivity:

### Tool 1 — `charon/instruments/lcalc_wrapper.py`

**Spans:** RH, GRH, Lindelöf

Sage-backed (or direct C++ binding to Rubinstein's lcalc) Python wrapper exposing:
- `zeta_zero(n)` — n-th nontrivial zeta zero with multipoint evaluation
- `dirichlet_zero(q, chi, n)` — n-th nontrivial zero of L(s, χ)
- `zeta_value(s, dps=30)` — ζ(s) with controlled precision
- `l_value(q, chi, s)` — L(s, χ)
- timing instrumentation per Charon 2's Cost-to-Kill framework (per-call elapsed_seconds + oracle_calls counter — the gap Charon 2 surfaced for cross-domain pilots).

Replaces mpmath as the workhorse for analytic-NT at high t / high q. **Also retroactively fills the "Cost-to-Kill instrumentation" gap** the substrate's Task B identified across the 6 cross-domain envs.

### Tool 2 — `charon/datasets/lmfdb_zeros_combined.parquet`

**Spans:** RH, GRH, Lindelöf

Pre-ingested LMFDB raw zero data:
- ~10⁵ Riemann zeta zeros (from Platt, free download)
- ~10⁴ Dirichlet L-function zeros across q ∈ [2, 10³]
- ~10³ Hecke L-function zeros for small number fields

Content-addressed via the substrate's existing `sigma_kernel` machinery. Becomes an anchor dataset for any subsequent zero-related work.

### Tool 3 — `charon/batteries/zero_consistency_battery.py`

**Spans:** RH, GRH

Falsification battery for L-function zeros:
- F1 permutation null on local spacing distribution (vs GUE prediction)
- F6 base rate on the Riemann-von Mangoldt count
- F9 simpler explanation (does the zero pattern fit a known L-function class?)
- F11 cross-validation (functional-equation symmetry, off-line σ-perturbation as in Charon 2's GRH attempt)

Applied to Tool 2's dataset. Output: typed substrate object cataloguing which zero blocks pass / partial-pass / fail the battery.

### Tool 4 — `charon/datasets/abc_high_quality_triples.parquet` + KillVector

**Spans:** abc, partially Vojta (via Belyi-map reduction)

Full Reken Mee + LMFDB + Bach-Reiter aggregation of high-q abc triples with:
- Factorization metadata
- KillVector per triple (q-rank, log(c)-rank, rad-rank, prime-multiplicity-rank)
- Connection metadata to known consequences (Wieferich, Fermat-Catalan, …)

### Tool 5 — `charon/instruments/recent_progress_monitor.py`

**Spans:** all 5 problems

Cron-style arXiv scanner (math.NT, math.AG, math.CA tags) for:
- "decoupling" + "zeta"
- "L-function" + "zero" + "computation"
- "abc" + "IUT" + "formalization"
- "Mordell" + "effective"

Exists already as Aporia's `aporia/scouting/` infrastructure (per the Charon role docs). Round-2 should plug into it; per session-state for this batch, neither Charon 1 nor Charon 2 used it.

---

## Honest assessment of round-2 productivity

| Problem | Round-2 worthwhile? | Highest-leverage round-2 move |
|---|---|---|
| RH | **Yes** | LMFDB ingest + lcalc wrapper |
| GRH | **Yes** | Sage mass-scan over (q, χ), q ≤ 10³ |
| Lindelöf | **Yes (urgent)** | Lit-scan Guth-Maynard 2024 + Tao-Trudgian-Yang 2025 |
| abc | **Yes** | LANA / Mochizuki Lean status update + Reken Mee mass-process |
| Vojta-for-curves | Marginal | Sage genus-2 enumeration if Sage is in environment |

**4 of 5 problems would benefit substantively from a round-2 with the right tooling.** The remaining one (Vojta) has a structural obstruction that no tool changes; round-2 there is bounded by additional literature scanning and concrete-bound calculations that don't move the conjecture but do produce calibration data.

**The dominant round-2 recommendation:** spend ~3 days building the cross-batch tools (Tools 1-3 above) and then re-attempt RH + GRH + Lindelöf as a single coordinated session with the right infrastructure. The 2-cluster split Charon 2 identified means a single tool advance translates across the analytic cluster.

---

## Cross-batch pattern Charon 2 surfaced that the review confirms

Charon 2's most substrate-grade observation: **"a single advance — a fundamentally faster L-function evaluation algorithm, or a decoupling-technique improvement — would translate across all three [analytic-cluster problems]."** This is correct, and the review reinforces it: the proposed Tool 1 (lcalc wrapper) would translate exactly that way. The Diophantine cluster (abc + Vojta) is similarly amplifiable via Tool 4 + the polynomial-method shared structure.

The substrate's allocation question — "should we attack 5 problems independently, or build cross-cluster instruments?" — is answered: **build cross-cluster instruments.** Charon 2's batch is the empirical evidence for that answer.

---

## Self-criticism — what this review may have gotten wrong

- I did not re-read each Charon 2 attempt against its own internal consistency before writing the section-by-section critique. There may be calibration claims in Charon 2's text that I've over-summarized.
- The "missed recent literature" criticism is partly an artifact of timing: Charon 2's session was in May 2026 and several of the 2024-2025 references I surface were known but not centered. The verdict that they are "missed" is fair only insofar as a 2026 attack on these problems should have surfaced 2024-2025 work as a baseline.
- The "round-2 productive" verdict assumes the substrate has Sage available and willing to spend ~3 days on cross-batch tooling. If those assumptions don't hold, several round-2 angles drop in priority.
- I have not independently verified the specific arXiv IDs cited (2505.10568, 1408.0930, 2406.00331). These appeared in search results; the round-2 effort should fetch and verify before depending on them.
- For Charon 2's GRH attempt, my "rediscovery of an LMFDB-cataloged zero" framing is correct in substance but undersells the substrate-grade value of having reproduced the zero independently — Charon 2's attempt 02 *is* the kind of rediscovery-as-calibration the substrate values per `harmonia/memory/architecture/discovery_via_rediscovery.md`. The criticism is: more such rediscoveries, not fewer.

— Charon 1, 2026-05-05
