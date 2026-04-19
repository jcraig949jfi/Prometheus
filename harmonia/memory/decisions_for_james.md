# Decisions for James — Asynchronous Queue
## Append-only log of items needing James's input
## Owner: Harmonia_M2_sessionA (conductor)
## Started: 2026-04-17

---

## How this works

James is HITL with time offline. I accumulate decisions that need his input here
rather than blocking the work on them. He reads this when he's back.

Each entry:
- Timestamp
- What's the decision
- What I'd recommend (to save his thinking time)
- What's blocked by it (if anything) — usually nothing, because I keep working

Anything truly urgent (calibration anchor failure, destructive-action risk,
data corruption) I flag at the TOP of this document with ⚠️.

Anything I can handle within the charter + standing orders, I handle. This
document is for things outside that envelope.

---

## ⚠️ URGENT (top-pinned)

*None currently.*

---

## Pending decisions

*None blocking. Second map-building milestone 2026-04-19: all 7 delegated roles executed; Geometry 1 FALSIFIED with amendment; F043 durable at z=-348.*

---

### [2026-04-19 ~01:30 UTC] — 7-role map-building wave delivered — milestone, Geometry 1 amended

**Tensor state transition:**
- Before wave: 31 × 25, 82 non-zero, 10.58% density, +2 count=22, +1 count=28
- After wave:  31 × 37, 103 non-zero, 8.98% density, **+2 count=44 (doubled)**, +1 count=7
- 12 new projections added as columns (Gap-filler). 22 cells promoted +1→+2. 5 demotions. 2 downgrades. 4 theorem retentions. 25 new graph edges (Mnemosyne). 246 papers mapped to 197 cells (Aporia).

**Headline finding 1 — Geometry 1 FALSIFIED with amendment (Koios 5f229878):**
SVD on the invariance matrix across three methods (naive, nuclear-norm completion, observed-only agreement) converges on effective rank **12–16**, not the 5 the original hypothesis claimed. Falsified in strong form.

BUT a 3-dimensional core captures 48–74% of variance with clean interpretations: (1) signal/noise, (2) kill/survive, (3) domain connectivity. Amended geometry: **low-rank core in higher-dim residual space**. F011/F013/F015 resolving under P028 is still one core fact with three witnesses; the residual contains real fringe structure we haven't yet named.

Caveat: at 10% density, rank estimates are noisy. Koios projects convergence at ≥30% density. Geometry 1 amendment stays provisional until Gap-filler lifts density across that threshold.

`harmonia/memory/geometries.md` rewritten to reflect this.

**Headline finding 2 — F043 DURABLE at z=-348 (sessionD 9fc25706):**
BSD-Sha anticorrelation corr(log Sha, log A) = -0.4343 survives block-shuffle within conductor decile at z_block = -348.05. Observed vs null 0 ± 0.0012. This is the session's strongest durability result on any specimen. Within-conductor-decile structure is real, not conductor-mediated. F043 promoted P020:+1 → +2, P023:+1 → +2.

**Precision correction — F011:P024 torsion COLLAPSES (sessionD 043ba782):**
F011 × P024 block-shuffle z = 1.37 → demoted +1 → -1. The cross-torsion-class differential is conductor-mediated, not structural. My earlier statements that F011 "resolves under rank, torsion, CM" were accurate for the first two but not the third. F011:P025 CM held (z=5.53). F011 now has 6 durable +2 cells under P028-adjacent axes + 1 collapsed torsion cell.

**Kill candidates from Query-runner (24d17e98):**
F012 Möbius (already tier=killed), F020 Megethos (already killed), F032 Knot silence (still tier=data_frontier). Worth formal review of F032 — the query-runner promoted it to kill-candidate based on structural pattern.

**What Query-runner's Q1/Q2 confirmed:**
- Q1 densest feature: **F011** (11/12 positive cells; every tested projection resolves at +1 or +2 except the now-corrected P024)
- Q2 principal projections: **P020 conductor** and **P023 rank** resolve 9 features each — these are the two empirical axes, consistent with the geometries.md core
- Zero contradictions across the signals.specimens registry

**NULL_BSWCD@v2 promoted (9fdf8e93):**
Implementation shipped at `harmonia/nulls/block_shuffle.py::bswcd_null@043ba782`. v2 is backward-compatible additive: stratifier and shuffle_col parameterized, Pattern-26 degeneracy guard wired in programmatically (v1 logged it verbally). All v1 callers get byte-identical defaults under v2.

**What's blocked:** Three deferred audits. F014 × P040 (Lehmer Mahler measure recomputation over 81K polys exceeds tick budget). F045 × P023 (raw per-curve a_p not in Ergon profiles). These need specific data infra.

**My recommendation:** This is the first major data point on whether the map-building strategy compounds. It does — the wave produced more durable structure than any same-duration research-mode wave has produced. The +2 count doubling in a single tick is the measurable signal. Continue map-building mode; another wave at this density + Gap-filler push should take density to ~15–20%, at which point the geometry amendment tightens.

**What's blocked for the next wave:** Gap-filler should prioritize rank-density-lifting cells (those that neighbor existing +2 structure) to get the Koios rank estimate out of the noise regime. Target 30% density as the geometry-closing threshold.

**Urgency:** milestone (no decision needed). All 7 delegated roles delivered.

**Commits:** f566e46c (Charon), ae71bd26/245235bb/d8191b1c (Gap-filler), 74aab3fb/047b754f/f2811662/49f2363f/70e8a344/745fb375 (Mnemosyne edge-weaver), 24d17e98 (Kairos query-runner), 5f229878 (Koios rank-analyst), 646d6ca6 (Aporia literature-mapper), 043ba782/9fc25706/1a18421d (Harmonia re-auditor), 9fdf8e93 (NULL_BSWCD@v2).

---

---

### [2026-04-18 ~21:40 UTC] — Map visualization LIVE — milestone, no pending decision

**Context:** First rendering of the invariance tensor as a live heatmap. Until today the tensor existed only as .npz + .json artifacts and stdout prints. Now at http://localhost:8777/map with auto-refresh from Redis every 5 seconds.

**What's visible:**
- 31 × 25 heatmap with hover metadata, row/col highlighting
- Hot-cell shading on untested cells (neighbor-density predicts structure — subsumes Query-runner Q3 partially)
- Force-directed graphs for feature and projection edges
- Gap banner flagging P028 Katz-Sarnak + 16 other missing projections
- Calibration anchors F001-F009 show green across their tested projections — instrument health visible at a glance
- Killed-feature cluster F020-F028 shows red/orange topology — the shape of known artifacts is now visible as a pattern, not scattered cells

**Three downstream effects:**
1. **Query-runner scope tightens** — Q3 ("predictive gap cells ranked by neighbor density") is partially visible in the viewer already. Q3 becomes "name and enumerate" rather than re-invent.
2. **New shape candidate**: F020-F028 red/orange cluster in the heatmap is structurally recognizable. Candidate shape symbol `KILLED_TOPOLOGY` — not yet drafted.
3. **Gap-filler first task gets concrete**: add 17 missing projections to build_landscape_tensor.py PROJECTIONS list. The cartographer's gap banner is the checklist.

**What's blocked:** Nothing.

**Urgency:** milestone (no decision needed). Charon delivered.

**Commit:** f566e46c Charon cartographer: landscape tensor viewer (31x25, 10.58% density).

---

---

### [2026-04-18 ~14:00 UTC] — Adversarial pass: F011 self-audit citation CORRECTED; 3 weak signals opened — RESOLVED

**Context:** Adversarial read of the research wave (~30 commits since last tick). Goal: refine precision, not just kill.

**Precision correction (F011):**
sessionB recursion-3 (71ff1d47) revealed the F011 rank-0 self-audit z_block=10.46 cited earlier used `class_size` as stratifier — which is DEGENERATE (null_std=0, one value covers 59% of data, produces spurious inflated z). Honest z_block = 4.19 under `torsion_bin` (Mazur 15 balanced). cm_binary gives z=0.63 (only 0.9% CM insufficient). F011 tensor description corrected. Residual still durable, but claim meaningfully less dramatic.

Also: joint α-free decay fit is UNDER-CONSTRAINED (α=0.49±0.52, eps_0=-4.07±56.08). The 31% eps_0 point estimate depends on fixing the decay form; honest range remains 23-36% across three fixed ansatze.

**Weak signals opened as candidate specimens:**
- **F042 — CM disc=-27 L-value depression** (U_C 322ff272). 2.5x depression between cm=-3 (Z[ω] maximal order) and cm=-27 (Z[3ω] non-maximal index 3) at rank-0 decade [1e5,1e6). n=14 — tiny; cross-decade replication queued. Kill/confirm via Rodriguez-Villegas & Zagier 1993 closed-form for non-maximal-order Hecke L-values. Specimen #66.
- **F043 — BSD-Sha anticorrelation with period** (U_D 111d6288). corr(log Sha, log A) = -0.520 at rank 0, A := Ω_real · ∏c_p. Large-Sha curves have systematically small period*Tamagawa product. NOT a conditioning tautology. Mechanistically explains T4's sha depletion in low-L tail. Candidate new empirical BSD relation — not predicted by any standard BSD formula. Replication across ranks queued. Specimen #67.
- **U_E SO(2N) MC k=3,4 divergence** (07a5a738) — pure-RMT Haar-random Monte Carlo at k=3,4 misses empirical moments by 33-100% at both ranks. Registered as F011 audit #68. Supports F011 LAYER 2 interpretation. CAVEAT: 10k MC samples may be under-converged for k=4 heavy tails; CI check task seeded.

**Pattern library discipline:**
sessionB proposed 5 new methodology patterns (25, 26, 28, 29 plus the earlier 23, 24). All are F011-investigation artifacts with 1 anchor each. Promotion criterion for the library is 3+ independent anchors (Pattern 20 had 4, Pattern 21 had 2). Drafts added to `pattern_library.md` as DRAFT section with explicit "do not apply as doctrine yet." Re-evaluate after next 3 specimen investigations.

**F041a Pattern 5 gate harder than it looked:**
U_E showed pure-RMT SO(2N) MC diverges from empirical at k=3,4 even without Euler products or a(k) proxy — 33-100% deviations. The CFKRS closed-form at rank-2 × num_bad_primes needed to close F041a's Pattern 5 gate is in a regime where the RMT side is NOT well-calibrated against existing data. F041a promotion to live_specimen stands but Pattern 5 gate is blocked on a prior calibration task.

**Tasks seeded this tick (5):**
- `audit_F042_cm_m27_rodriguez_villegas_zagier` (-1.0)
- `wsw_F043_bsd_sha_period_corr_replicate` (-1.0)
- `audit_U_E_SO2N_MC_CI_k4` (-0.5)
- `port_dhkms_bessel_integral_python` (-0.5, infra)
- `mine_aporia_literature_scan_for_F_specimens` (-0.5, 246-paper cross-reference against live specimens)

**What's blocked:** Nothing. F042 and F043 are n-limited (F042 n=14; F043 rank-1+ replication needed to promote). The DHKMS Bessel port is the critical-path infra for closing F011 LAYER 2.

**Urgency:** F011 description correction is high-value; other items medium.

---

---

### [2026-04-18 ~10:00 UTC] — F011 REOPENED to live_specimen; mixed tier (excised + rank-0 frontier) — RESOLVED

**Context:** Earlier today I tiered F011 as `calibration_confirmed` based on sessionB's Aporia Report 1 (excised-ensemble tests both passed). Since then Ergon + sessionB + T4 have done decisive followups.

**Findings that reopen F011:**
- **Ergon DHKMS closed-form (2572d7dd):** The 31% rank-0 residual is NOT a finite-N correction. DHKMS predicts the WRONG DIRECTION. Would need 25% mean unfolding bias to explain — implausible. Not a reference error (Gaudin baseline confirmed).
- **sessionB three-ansatz decay fit (a87ea026):** power-law eps_0=31.08±6.19, 1/log(N) eps_0=22.90±0.78 (z=29σ from 0), 1/log(N)² eps_0=35.83±0.36. Residual robust 23-36% across ansatze.
- **sessionB self-audit under P104 block-shuffle (within class_size, 100 perms):** null mean -9.42±3.87, observed 31.08, **z_block=10.46 DURABLE**. F011 rank-0 residual survives its own instrument (Pattern 24).
- **Ergon zero-projections (37158e4f):** The deficit varies with arithmetic complexity. Isogeny class size 1→8: var/Gaudin drops 1.37→0.97. Sha order 1→36: var/Gaudin drops 1.30→1.00. NOT uniform — rules out generic unfolding error, points to genuine structure.
- **T4 low-tail sub-family (cbe7b623):** rank-0 Pr[L/M_1<0.25] enriched for CM (1.73x, cm=-27: 6.66x), class_size=3 (1.78x), nbp=2 (1.52x); sha>1 depleted. Residual concentrated in arithmetically structured sub-populations.

**New tier:** F011 tier → `live_specimen` (mixed). Description rewrites LAYER 1 = excised calibration (confirmed) + LAYER 2 = rank-0 residual (genuine frontier). n=2,009,089. Specimen #63 registered.

**Tensor implication:** P020:+2 retained (conductor IS resolving axis for LAYER 1). P028:+2 retained (downstream of LAYER 1 but durable). P104:+1 (self-audit survival).

**What blocked:** Nothing. 4 decisive tests queued for next cohort: DHKMS closed-form magnitude match; independent-unfolding via non-LMFDB zeros; cross-family comparison vs Dirichlet L-functions; Miller 2009 NLO prediction (P106 draft) match to ~23% residual.

**My recommendation:** this is the session's strongest frontier. Connects to Hilbert-Pólya lineage per Ergon Thread A. The rank-0 residual is the single most interesting number we have. Worth prioritizing P106 merge + Miller 2009 comparison over any new catalog work.

**Urgency:** medium-high. Not blocking, but the four residual-frontier tests should run on next worker cohort.

---

### [2026-04-18 ~10:00 UTC] — F041a PROMOTED, supersedes F041 — RESOLVED

**Context:** F041 (rank-dependent Keating-Snaith convergence) was demoted earlier today — sessionC showed it's first-moment drift. The REAL signal is F041a: at rank ≥ 2, moment slope is strictly monotone in `num_bad_primes`. Ergon drafted the catalog entry; 5 Harmonia workers stress-tested it.

**Kill tests survived:**

| Test | Worker | Result |
|---|---|---|
| Cross-nbp block-shuffle-within-(rank,decade) | W2 | amp 27.6x, corr(nbp,slope)=0.97, null spread 0.046 vs obs 1.32 |
| Conductor-control joint OLS | U_A | b_nbp z=3.37 (≥3 threshold); narrow 0.1-decade bins corr=0.965 |
| P039 Galois-image alternative axis | W3 | P021 range 1.316 vs best P039 marginal 0.305 — not a proxy |
| P026 semistable vs additive split | T3 | Ladder lives in SEMISTABLE half (counterintuitive, points to multiplicative-ramification) |
| Specific-prime joint stratification | T5 | No single Mazur-Kenku prime dominates; count matters + mild {2,3} lift |

**Tier:** F041a `live_specimen`. INVARIANCE: P023:+2, P020:+1, P021:+2, P026:+1, P039:-1, P104:+2. n=222,288 (rank-2 joined). Specimen #62 registered.

**Residual hurdle:** Pattern 5 CFKRS gate. Compute CFKRS rank-2 SO(even) theoretical slopes-in-nbp prediction. If CFKRS predicts the monotone ladder: demote to calibration. If not: fully frontier.

**What's blocked:** CFKRS theoretical formula at rank 2+ stratified by nbp is non-trivial (sessionC W1 had to flag k=3,k=4 rank-0 as FRONTIER). The computation is the work.

**My recommendation:** ACCEPTED as live_specimen pending Pattern 5. This is the session's second-strongest finding, behind F011 rank-0 residual. F041a + F011 together suggest "rank-mediated arithmetic sensitivity" as a shape worth naming.

**Urgency:** medium (specimen is live, frontier is Pattern 5 gate).

---

### [2026-04-18 ~10:00 UTC] — F008 Scholz reflection = NEW CALIBRATION ANCHOR — RESOLVED

**Context:** sessionD's Report 18c identified p=3 BST convergence exponent as distinctly slower (α_3 ≈ 0.16 vs α_{p≥5} ≈ 0.23-0.28). Matches Davenport-Heilbronn + Scholz reflection prediction. I seeded a direct Scholz test as audit_scholz_reflection_p3_BST. Ergon executed.

**Finding (Ergon scholz_reflection.py in 2572d7dd):** Zero violations of |r3(K*) - r3(K)| ≤ 1 across 344,130 imaginary-real quadratic pairs. 71.5% equality (r3 matches), 28.5% differ by exactly 1. Never >1. sessionD independently confirmed in 12e93a0f.

**Added as F008** calibration tier anchor. INVARIANCE: P024:+2. Theorem lineage: Scholz 1932 reflection + Davenport-Heilbronn 1971. n=344,130. Specimen #64 registered.

**What this gives us:** Any NF computation that produces |r3(K*) - r3(K)| > 1 has a bug. Instrument-health check complement to F003 (BSD parity) and F009 (Serre+Mazur).

**Calibration tier now:** F001-F005 + **F008** + F009 = **8 anchors** (up from 7).

**What's blocked:** Nothing.

**Urgency:** resolved.

---

---

### [2026-04-18 ~09:00 UTC] — F011 tier change: live_specimen → calibration_confirmed — RESOLVED

**Context:** Aporia's deep-research Report 1 hypothesized that F011's ~38% GUE first-gap variance deficit is the Duenez-Huynh-Keating-Miller-Snaith (2011) excised ensemble — a known finite-conductor central-zero-forcing effect, not a novel anomaly. sessionB executed both decisive tests on n=2,009,089 EC.

**Results (sessionB wsw_F011_excised_ensemble):**

| Test | Prediction (excised) | Prediction (anomaly) | Observed | Verdict |
|---|---|---|---|---|
| Conductor-window scaling | Deficit shrinks with conductor | Flat | Slope -7.17 per log-decade, z=-54.2; 45.37% → 35.34% across 10 bins | EXCISED |
| Edge vs bulk (gap1 vs gap2) | gap1 >> gap2 (central zero repels only adjacent) | Similar | gap1 38.17% vs gap2 29.07%, z=96.97 | EXCISED |

**Both tests pass excised-ensemble prediction at z > 54.** F011 is Duenez-HKMS, not new physics.

**Tier change:** F011 `live_specimen` → `calibration_confirmed`. Joins F001-F005 + F009 as calibration anchor (6 → 7). Specimen #46 already registered with `status=calibration_confirmed` by sessionB.

**Downstream: F013 interpretation.** F013's P028 split (z=13.68, block-shuffle z_block=15.31) is now understood as a downstream consequence of the same central-zero-forcing — not independent novelty. F013 stays `live_specimen` because the rank-slope sign flip is still structurally informative beyond F011's first-gap story, but interest downgraded. Pattern 5 (known bridge) gate closed retrospectively on both F011 and F013 P028 findings.

**What was learned:** The instrument correctly detected a known RMT effect. F011's block-shuffle verification (z_block=111.78) was durable because the effect IS real — just not novel. This is calibration success, not failure. The "session's strongest durably-resolved specimen" claim from 2026-04-17 is revised to "session's strongest durably-resolved calibration case."

**Residual frontier on F011:** (a) magnitude comparison vs Duenez-HKMS closed-form prediction — if our observed 38% matches the theoretical constant to ~1%, the calibration is exact. (b) rank-3 deficit (37.2%) > rank-2 deficit (32.0%) inversion is NOT predicted by naive central-zero count — candidate higher-order effect, worth a separate probe.

**James input at the time:** "If F011 turns out to be excised-ensemble, I'd write the tier-change decision." — sessionA is writing it per this instruction.

**My recommendation:** ACCEPTED. This is the cleanest falsification outcome possible: Pattern 5 gate worked, instrument calibrated against known theory, and the methodology (block-shuffle protocol from F010) didn't save a finding from reinterpretation. Falsification-first doing its job.

**What's blocked:** Nothing. Residual-frontier tests (closed-form magnitude, rank-3 inversion) seeded-able when the worker cohort is re-spun.

**Urgency:** resolved (historical record).

---

### [2026-04-18 ~08:40 UTC] — F041 Keating-Snaith moment convergence added as candidate

**Context:** sessionC executed Aporia Report 4 post-loop. Moment ratios R_k(X) = M_k(X)/(log X)^{k(k-1)/2} on 2M EC leading_term values, stratified by (analytic_rank, conductor-decade). Pattern 20 discipline reflexive: no pooled statistic reported; 13 cells at n≥100 per stratum.

**Finding:** convergence rate (slope of R_k vs log-conductor) is STRONGLY rank-dependent at k=1:
- rank=0: +0.164 ± 0.020
- rank=1: +0.922 ± 0.040 (5.6x larger)
- rank=2: +1.929 ± 0.025 (12x larger)

Higher-k columns (k=3, k=4) show approx-zero slopes for rank 0 — RMT prediction already satisfied at small conductor for rank 0.

**Interpretation:** convergence rate IS a candidate phoneme. Different rank cohorts approach RMT asymptotics at different speeds, consistent with SO_even vs SO_odd excised-ensemble story (i.e., this is likely ANOTHER downstream consequence of the same central-zero-forcing effect, connected to F011).

**Added as F041** `live_specimen`, n=2,009,089, interest=0.7, specimen #48 registered.

**NOT yet block-shuffle verified** — must happen before promotion or upgrade. Pattern 21 discipline.

**What's blocked:** Nothing. Seed-able: `wsw_F041_moment_convergence_block_shuffle`, `keating_snaith_arithmetic_factor` (decontaminate a_E(k)), `katz_sarnak_vs_rank_check`.

**Urgency:** medium (fresh specimen; block-shuffle verification is the next gate).

---

### [2026-04-18 ~08:59 UTC] — Cohen-Lenstra NOT F-anchor but calibration-consistent

**Context:** sessionD executed Aporia Report 18. Prob(p|h) across 25 (degree × galois_label) strata × 5 primes {3,5,7,11,13} on 21.8M NF.

**Verdict:** `NOT_F_ANCHOR_BUT_CONSISTENT_WITH_ASYMPTOTIC_CL`. Imaginary quadratic 3-8% below asymptote, real quadratic 13-25% below (slower convergence matches classical regulator-growth intuition). All strata |z| = 11-66 below theory. Deviation is known finite-disc convergence bias (Bhargava-Shankar-Tsimerman), NOT an instrument failure.

**Decision:** do NOT add as calibration anchor. Would pollute the F-tier with a specimen that deviates from its own prediction by known finite-disc bias. Specimen #47 registered for audit trail.

**What's blocked:** Nothing. If future work obtains larger-disc bounds (Bhargava-Shankar-Tsimerman rate), F_Cohen_Lenstra could be revisited as an asymptotic anchor.

**Urgency:** resolved.

---

---

### [2026-04-17 ~12:45 UTC] — 3 SPECIMENS VERIFIED under block-shuffle; P028 is a real cross-specimen resolver — MAJOR FINDING

**Context:** Following the F010 block-shuffle kill this morning, sessionB and sessionC ran the protocol on F011, F013, and F015. Results:

| Specimen | Finding | Block-shuffle verdict | z_block |
|---|---|---|---|
| F010 NF backbone | decon ρ=0.27 via P052 | **KILLED** | -0.86 |
| F011 GUE first-gap deficit | P028 spread 7.63% | **DURABLE** | 111.78 |
| F013 zero-spacing vs rank | P028 slope diff 13.68 | **DURABLE** | 15.31 |
| F015 Szpiro sign-uniform | per-k slope -0.3 to -0.7 | **DURABLE** | -3.48 to -24.03 |

**Interpretation:** The Katz-Sarnak symmetry-type axis (P028) is now the **first cross-specimen resolver** this session. F011 and F013 both resolve via it at z_block >> 10. F015 resolves via a different axis (P021 bad-prime) but also block-verified. F010 failed — and it was the only specimen whose "survival" came through a post-hoc decontamination rather than a native stratification.

**What was learned:** (1) The block-shuffle protocol discriminates rather than blanket-rejects — it correctly separates durable from artifact. (2) Plain permutation nulls can over-reject OR under-reject depending on which stratum structure they preserve. F010 plain null over-rejected (z=2.38 looked real, was artifact); F011 plain null didn't over-reject (z=7.63 was real). The protocol IS the check. (3) P028 Katz-Sarnak is a genuinely load-bearing resolving axis for EC and NF-adjacent specimens.

**What needs deciding:** Nothing. All three specimens' tensor entries updated with block-shuffle verification. P028 is now the "canonical resolver" to test against new specimens before any other axis.

**My recommendation:** This is the session's strongest POSITIVE finding. Combined with the F010 kill, we have a clean methodology pair:
- Kill case (F010): post-hoc decontamination can look durable but isn't
- Survival case (F011/F013/F015): native stratification via P028 OR P021 is durable

Both are needed to calibrate the instrument. The session is complete, durable, and leaves a working methodology plus a working resolver.

**What's blocked:** Nothing. Worth future work: test P028 on F014 (only live specimen without a block-verified resolver).

**Urgency:** Low (FYI — the session's high-order positive finding)

---

---

### [2026-04-17 ~12:33 UTC] — F010 KILLED under block-shuffle null — FINAL KILL

**Context:** F010 (NF backbone via Galois-label) was the session's emerging "strongest specimen" candidate at 5/5 projection survival. Multiple falsification layers peeled back:
1. Pooled ρ=0.40 killed at bigsample → 0.109 (Pattern 20 artifact)
2. Decontaminated ρ=0.27 via P052 prime-detrend (z=2.38 weak-null) was the proposed durable signal
3. P028 Is_Even split z_diff=5.38 attenuated to z_diff=1.95 at bigsample (P028 weak)
4. **Block-shuffle-within-degree null (sessionC wsw_F010_alternative_null, this tick)**: the decontaminated ρ=0.173 (n=51) sits BELOW null mean 0.205, z=-0.86. **Zero within-degree coupling.**

**Interpretation:** The NF↔Artin coupling is degree-marginal only — "low-degree NFs pair with low-dim Artin reps" is trivial and doesn't survive preserving per-degree structure. F010 joins F022 (its feature-distribution twin, previously killed).

**What was learned:** The plain label-permute null (used in sessionC's bigsample) OVER-REJECTED because it didn't preserve per-degree marginal. This is a *null-model selection* lesson — choice of null matters as much as choice of projection. Three-layer artifact demonstrated: Pattern 20 (pooled level) + Pattern 19 (stale 0.40 claim) + null-model-mismatch (plain permute doesn't catch degree-marginal signal).

**What needs deciding:** Nothing — F010 tier changed to `killed`. INVARIANCE updated: P052: +1 → -2, P010: +2 → -1. The null-model lesson is the session's strongest methodology finding.

**My recommendation:** ACCEPTED. This is a GREAT result even though it looks like a negative. The methodology caught what would have been a tempting false-positive. No new calibration anchor, but a strong PATTERN calibration: when a signal survives 5 projections, run it through a null that preserves the most obvious stratum structure (degree, conductor, etc.) before promotion.

**What's blocked:** Nothing. The remaining live specimens (F011, F013, F014, F015) have NOT been through block-shuffle nulls. Worth seeding bigsample+block-null tests for each — now a standard protocol.

**Urgency:** medium-high (paradigm for other specimens)

---

---

## Resolved (recent — keep for audit)

### [2026-04-17 ~11:33 UTC] — F010 did NOT graduate: pooled ρ was Pattern-20 artifact — RESOLVED

**Original question:** Would F010 graduate from `live_specimen` to `robust_specimen` if the large-n rerun pushed z>3.5?

**Resolution:** sessionC wsw_F010_bigsample (per_degree=5000, n_shared=75) completed. Raw pooled ρ **collapsed** from 0.404 (n=71) to 0.109 (n=75, z=0.88) — classic Pattern-20 sample-frame artifact. Durable signal is decontaminated ρ=0.270 (P052 prime-detrend, stable across sample sizes, retention_ratio=2.47). But z=2.38 is still borderline. F010 stays `live_specimen`, not promoted.

**Downstream updates:**
- F010 became the 4th Pattern 20 anchor case (pattern_library.md updated).
- F010 joined F012/F014/F011 as Pattern 19 anchors (the claimed 0.40 was stale).
- Tensor F010 description rewritten: durable ρ=0.27 via P052, pooled was artifact.
- F010 INVARIANCE: P052:+1 added, P040 demoted -1→-2 (pooled is not durable here).

**What's blocked:** Nothing. F010 may still firm up with an alternative null (block-shuffle within degree-class). Seeding `wsw_F010_alternative_null` followup.

**James approval:** 2026-04-17 "agreed on the F010 NF - let it play out" — outcome now known.

---

### [2026-04-17 ~11:00 UTC] — F012 H85 kill provisional pending Liouville — RESOLVED

**Original question:** Was the F012 |z|=6.15 a definitional artifact (Möbius vs Liouville) that Liouville side-check would rescue?

**Resolution:** Liouville side-check completed (sessionB). Max|z|=0.52 under Liouville, 0.39 under Möbius. Both firmly in noise (p=0.60/0.68). **F012 kill is definitional-independent** — the original |z|=6.15 was never reproducible. F012 moved to `tier=killed`. Pattern 19 promoted from draft to full pattern.

**James approval:** 2026-04-17 "All sounds good. You can archive them."

---

### [2026-04-17 ~11:00 UTC] — F013 density/structural 74%/26% split — ACKNOWLEDGED

**Original question:** Recording the quantitative characterization of F013 as 74% density-mediated, 26% structural residual.

**Resolution:** Recorded in tensor (F013→F011 parallel_density_regime edge, F013 INVARIANCE updated per sessionC draft). Clean finding, good science. No further action required.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — Pattern 19 (Stale/Irreproducible Tensor Entry) promotion — APPROVED

**Original question:** Should Pattern 19 (sessionB's proposed pattern from F012 WORK_COMPLETE) become an official pattern?

**Resolution:** Promoted to full pattern with Liouville confirmation. Anchor cases F012/F014/F011 documented. In pattern_library.md.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — F014 Lehmer 4.4% gap FALSIFIED — ACKNOWLEDGED

**Original question:** SessionB found Salem polynomial at M=1.216 inside the claimed 4.4% Lehmer gap. F014 needed refinement.

**Resolution:** F014 description updated in tensor to reflect the Salem density in (1.176, 1.228). sessionB further refined with num_ram=1 monotone trend. Kept tier=live_specimen (structure remains interesting, claim refined).

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — F010 NF backbone reproduced at 4/5 projections — ACKNOWLEDGED

**Original question:** SessionC confirmed F010 at ρ=0.404, survives conductor/bad-prime/feature-perm, P052 deferred.

**Resolution:** Recorded. Followup task `wsw_F010_P052` queued to close out the fifth projection.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — Worker commits push authorization — APPROVED

**Original question:** Should I push worker output commits on their behalf?

**Resolution:** James's ongoing approval mode during this session covers pushes of worker output files (`cartography/docs/wsw_*.json|.py`) and tensor memory files when they correspond to approved TENSOR_DIFFs. I've been pushing these as I approve them.

**James approval:** 2026-04-17 "All sounds good."

---

*Template for new entries:*

```
### [YYYY-MM-DD HH:MM UTC] — <short title>

**Context:** one paragraph
**What needs deciding:** one sentence
**My recommendation:** one paragraph with reasoning
**What's blocked:** (nothing | specific worker | specific task) — usually nothing
**Urgency:** low / medium / high / URGENT

---
```
