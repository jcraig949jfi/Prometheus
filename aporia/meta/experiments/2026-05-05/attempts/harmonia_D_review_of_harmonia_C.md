# Review — Harmonia C (Analysis / PDEs Batch)

**Reviewer:** Harmonia D
**Date:** 2026-05-05
**Scope:** Critique of C's 5 attempt files plus summary, with per-problem
recommendations for round-two, additional solution angles, and
datasets/tools that would extend the work.

**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_00_summary.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_01_navier_stokes.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_02_yang_mills_mass_gap.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_03_kakeya.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_04_restriction.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_C_05_bochner_riesz.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_p{1..5}_*_experiment.py` (5 scripts)

**Existing prior review:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_A_review_of_harmonia_C.md` (Harmonia A, ~600 lines)

This review is independent: I read C's outputs in full before reading A's review, then explicitly engaged with A in §6 below to be additive rather than redundant.

---

## 0. Top-line judgment

**Quality tier: B / B+** for substrate-grade kill data. The batch is honest, has zero invented citations, and produces one load-bearing reward-signal-capture catch (P5 Fefferman miss).

**One critical structural issue** that A's review did not catch and that warrants top placement: **as of February 2025, the Kakeya conjecture in R³ has been proved by Hong Wang and Joshua Zahl** ([arXiv:2502.17655](https://arxiv.org/abs/2502.17655); see Tao's exposition [terrytao.wordpress.com 2025-02-25](https://terrytao.wordpress.com/2025/02/25/the-three-dimensional-kakeya-conjecture-after-wang-and-zahl/) and Quanta coverage [quantamagazine.org 2025-03-14](https://www.quantamagazine.org/once-in-a-century-proof-settles-maths-kakeya-conjecture-20250314/)). C's P3 attempt file uses verdict "OPEN — no progress made" and locates the obstruction at the Wolff-1995 hairbrush level. **This is wrong as of the batch's own date (2026-05-05).** C explicitly flagged Wang-Zahl 2022 as "invoked-from-prompt, not re-fetched"; A's review noted this risk in §6 ("My claim that Wang-Zahl 2022, Hickman-Rogers 2019, Bourgain-Guth 2011 are 'the technical frontier' is from training-data recall and was not re-fetched. If those papers have been superseded by 2026, my framing is dated.") — A's instinct was correct; the surrounding 2024-2025 Wang-Zahl program closed the n=3 case in February 2025. (See §1.3 below for full implications.)

This is **the** highest-priority piece of new information for this review. It changes the framing of P3, partially of P4 (restriction in n=3 may now be substantively closer to closure), and partially of P5 (Bochner-Riesz in n=3 inherits Kakeya-side improvements via the triangle).

**On the rest of the batch:** I largely concur with A's critique. C's batch was under-budget (6h of 15h) and used a uniform recipe (survey + obstruction localization + adjacent-easier calibration). The recipe's safety produced low-variance output without ever bumping against the open frontier in any of the five problems. Round-2 is warranted and feasible.

---

## 1. Per-problem critique

### 1.1 — P1 Navier-Stokes: standard but uninformative

The 2D NS pseudospectral run with BKM integral tracking is well-executed (script `_p1_ns_experiment.py` runs real numerics — verified) but is a textbook calibration. The obstruction-localization in §3 of C's file restates the well-known supercritical-vs-critical scaling story without contributing structural observation.

**Specific issues:**
- C did not run *any* 3D simulation despite §5 listing 3D Taylor-Green and axisymmetric Hou-Luo as "where I would push." Both fit in tens of minutes on a reasonable machine. The under-budget (~80 min instead of 180 min per problem) does not explain the 3D omission.
- Critical-norm tracking via Escauriaza-Seregin-Šverák (`L^3_x` boundedness ⇒ regularity persistence) is the *direct* probe of the regularity criterion at the right critical norm. C did not even mention it as an option until A did.
- The "averaging dial" idea — interpolate between real NS and Tao's averaged NS by a 1-parameter family — is genuinely novel. C did not even sketch it; A proposed it in §1 P1 of A's review, where it remains the most generative round-2 candidate I see for P1.

**Round 2 priority:** medium. The averaging-dial is the high-novelty piece. Critical-norm tracking is the high-discipline piece. Together: ~5-7 hours.

### 1.2 — P2 Yang-Mills: cleanest calibration, weakest ambition

The 2D U(1) Metropolis run reproduces `I_1(β)/I_0(β)` to ~1% — solid. Script verified: real Metropolis with proper plaquette action, real Bessel function call, real string-tension-via-area-law check. **No fabrication.**

**Specific issues:**
- 4D `SU(2)` at small lattice (`L = 6, 8`) is *not* prohibitively expensive — minutes per coupling on a reasonable machine. C dismissed this as "almost certainly null" without trying. Even a null result is calibration.
- Glueball mass extraction via plaquette-plaquette correlator (the *direct* observable for the mass gap) was never attempted.
- The "Balaban block-spin RG flow as coordinate system" idea (C's own §5 item 2) is dismissed as "multi-month work" but a 2-step block-spin on a small lattice with numerical effective-coupling extraction is a session-scale task. This is precisely the kind of "coordinate-system invention" the substrate's north star calls for; C's reflexive dismissal is the kind of reward-signal-capture-resistance that *also* misses real opportunity.
- Gribov region visualization (C's §5 item 3) — also session-scale, also not attempted.

**Round 2 priority:** medium-low for substrate impact, high for completeness. ~7-10 hours absorbs most of C's unused budget.

### 1.3 — P3 Kakeya: structurally outdated; full re-attempt warranted

**Critical update first.** Per WebSearch verification (May 2026):

- **Hong Wang and Joshua Zahl** posted [arXiv:2502.17655](https://arxiv.org/abs/2502.17655) on 2025-02-24, "Volume estimates for unions of convex sets, and the Kakeya set conjecture in three dimensions", **proving the full Kakeya set conjecture in R³**.
- Tao's expository blog post [terrytao.wordpress.com 2025-02-25](https://terrytao.wordpress.com/2025/02/25/the-three-dimensional-kakeya-conjecture-after-wang-and-zahl/) summarizes the proof. Quanta coverage [2025-03-14](https://www.quantamagazine.org/once-in-a-century-proof-settles-maths-kakeya-conjecture-20250314/) characterizes it as "once-in-a-century."
- Larry Guth's outline of the proof: [arXiv:2508.05475](https://arxiv.org/abs/2508.05475).
- Subsequent surveys: Zahl, "A Survey of the Kakeya conjecture, 2000-2025" [arXiv:2512.09397](https://arxiv.org/pdf/2512.09397).
- The proof program: reduce the general case to the *sticky* case, where the sticky case was proven in earlier Wang-Zahl 2022 work building on the Katz-Tao 2014 program.

**Implication for C's P3 attempt file:**

- Verdict "OPEN — no progress made" is **wrong as of 2026-05-05**. The correct verdict is "SETTLED IN n=3 (Wang-Zahl 2025)."
- "Obstruction localized at the *incidence-multiplicity scaling* level" is now historical: Wang-Zahl's reduction to sticky + their resolution of sticky settled the multiplicity-scaling question for n=3.
- The 3D tube-incidence statistics in §4b (50→400 tubes, max multiplicity 30→115) are still informative *as data* but not as an "open-frontier" probe — they are now reproducing structure that is theoretically characterized.
- The remaining genuinely open Kakeya question is **n ≥ 4**. The Wang-Zahl program does not (in current form) extend to n ≥ 4; the obstruction at higher dimensions is now the substrate-grade frontier.

**This miss is C's most important error.** C's discipline rule ("invoked-from-prompt, not re-fetched") permitted shipping an attempt that does not engage with the actual state of the conjecture. The discipline rule should have been: *if the citation matters to the verdict, fetch before shipping.*

**Round 2 priority:** highest urgency in the batch. The right round-2 P3 is:

1. **Re-fetch and read** Wang-Zahl 2025 ([arXiv:2502.17655](https://arxiv.org/abs/2502.17655)) plus Guth's outline ([arXiv:2508.05475](https://arxiv.org/abs/2508.05475)).
2. **Re-frame** the attempt: P3 in n=3 is now SETTLED; pivot to n ≥ 4 where it remains open.
3. **Compute the sticky/non-sticky decomposition** numerically on tube ensembles in n=3 (the key technical reduction in Wang-Zahl). Verify that random tube ensembles look "sticky" by their criterion. Calibration anchor against the new theorem.
4. **Probe n=4** (and n=5) tube-incidence statistics. The n ≥ 4 case is where the substrate-grade open frontier now lives. Wolff's hairbrush bound `(n+2)/2` is `3` in n=4 — the obstruction at higher n is qualitatively similar to the pre-Wang-Zahl obstruction at n=3, and the same multiplicity-statistics methodology applies.
5. **Re-tag** the kill_path: previously "incidence-multiplicity-scaling-undetermined-at-conjectured-dim" is now historical; the new tag for n ≥ 4 is "Wang-Zahl-method-does-not-extend-to-n>=4-via-current-techniques."

**Cascading implication for P4 and P5 in n=3:** since Kakeya ⇒ Restriction ⇒ Bochner-Riesz in many regimes (with quantitative bound transfers, not strict logical entailments), and the Wang-Zahl 2025 result delivered the optimal Kakeya bound in n=3, the Restriction and Bochner-Riesz conjectures in n=3 should be re-checked for whether they are now closed (or substantially improved) downstream. **C and A both treated P4-n=3 and P5-n=3 as fully open; the literature should be re-checked.** I did not run a full literature scan on this; it is a round-2 priority.

### 1.4 — P4 Restriction: cleanly executed, but the test functions don't probe the open regime

The Stein-Tomas calibration on indicator caps in n=2 and n=3 is correct (script `_p4_restriction_experiment.py`). The ratio stays bounded as expected. C's §4 explicitly acknowledges that the data does not probe the open regime.

**Specific issues:**
- Knapp-block test functions (the canonical adversarial functions for restriction at the conjectured boundary) were not implemented. C's §5 item 1 lists this; not done.
- Bilinear extension (Tao-Vargas-Vega 1998) — C's §5 item 2; not done.
- Decoupling on the paraboloid (Bourgain-Demeter, the technical tool Hickman-Rogers chains to) — C's §5 item 3; not done.
- The hazy citations to "Hickman-Rogers 2019" and "Guth 2016" are flagged but never verified. Given the Wang-Zahl 2025 Kakeya advance, the Restriction frontier in n=3 may have shifted; this needs re-fetching.

**Round 2 priority:** high. Knapp blocks are the binding constraint on every honest sweep at the conjectured boundary. ~4-6 hours.

### 1.5 — P5 Bochner-Riesz: the load-bearing catch of the batch

C's reward-signal-capture catch — that the Gaussian test function shows ratio = 1.0000 at δ=0 in violation of Fefferman 1971's known unboundedness, because the Gaussian is too smooth — is the **single most valuable substrate-grade output of the entire C batch**. A's review correctly identifies this. I concur.

**Specific issues (extending A):**
- The table at §4 is uninformative *with* the caveat. C correctly flagged it as artifact rather than reporting "BR is bounded for all δ ≥ 0 and all p" (which would have been a Pattern-30 Level 3 reward-signal-capture failure). The discipline worked.
- Round 2 must replace the Gaussian sweep with Knapp-block sweep. C's §5 item 1; not done. A's round-2 P5 proposal #1 is exactly this and is correct.
- Carleson-Sjölin square-function decomposition in n=2 reproduces the proved bound numerically (C's §5 item 2; A's round-2 P5 proposal #2). Mechanical, ~3 hours, gives a numerical witness of the proof's mechanism.
- Like P4, the n=3 frontier should be re-checked given the post-Wang-Zahl-2025 Kakeya cascade. The Bourgain-Guth 2011 "frontier" citation is hazy; refresh.

**Round 2 priority:** high (the Fefferman miss must be retired with proper Knapp-block calibration). ~5-7 hours.

---

## 2. Cross-cutting issues

The same cross-cutting categories I applied to my B review apply here, with C-specific calibrations:

### C1 — Time discipline (under-budget)

C ran 6h of a 15h budget — 9h unused. A's review correctly identifies this as the most tractable round-2 investment in the batch. I concur. The under-budget was not a weakness of capacity but a feature of the recipe: "survey + obstruction-localize + one calibration trace + stop" is template-friendly and converges. The recipe is *too* safe.

### C2 — Citation discipline: explicit but unverified

C used a clean `[confident]` / `[hazy]` / `[invoked-from-prompt, not re-fetched]` annotation on every citation — better discipline than B's looser `[paraphrase]` tagging. **However**, C did not re-fetch *any* hazy citation despite WebSearch availability, and the P3 Wang-Zahl reference is the case in point: a single arXiv check would have surfaced the 2025 proof and changed the entire P3 attempt. **Methodology candidate (new):** *"Hazy citations on load-bearing claims must be fetched before the verdict line is written."* This is distinct from C's own "adversarial test function before novelty claim" methodology candidate; it addresses a different failure mode (currency rot, not test-function calibration).

### C3 — Numerical precision: appropriate to scope

C's numerical work uses standard double-precision. For the calibration scope (textbook regimes where exact answers are known), this is appropriate; no precision issues observed. Round-2 P1 (3D NS) and P2 (4D lattice gauge) would inherit the same precision sufficiency. P3, P4, P5 round-2 work involving Knapp blocks and decoupling on fine grids may need either careful FFT discipline or higher precision; not yet a binding constraint.

### C4 — Calibration before novelty

C uniformly executed this discipline (every problem has an "adjacent-easier-version" calibration). This is the *strongest* methodology aspect of C's batch and is correctly identified as a candidate for promotion (C's §5 candidate B in summary; A's review more skeptical, see §6 below).

### C5 — Statistical testing: minimal but appropriate

C reported standard errors on Wilson loops via simple `std/√N` per-sample. Adequate for the calibration scope. Round-2 work probing the open regime (Knapp sweeps, decoupling at multiple grids) should add multi-grid extrapolation and bootstrap CIs.

### C6 — No use of methodology toolkit

Same observation as in my B review. The toolkit (KOLMOGOROV_HAT, MDL_SCORER, CHANNEL_CAPACITY, CRITICAL_EXPONENT, etc.) was not deployed. CRITICAL_EXPONENT in particular is *directly applicable* to all 5 problems in C's batch — every one of them is a critical-scaling question. Round-2 should explicitly draw from the toolkit shelf.

### C7 — Cross-batch synthesis missing

C's summary §2 ("does the same dimensional obstruction recur across P3-P5?") is real cross-problem synthesis within the batch. C also identified a 5/5 pattern ("adjacent-but-easier version is solved, gap is dimensional/scaling-marginal, not categorical"). This is genuinely substrate-grade for the analysis cluster. C did *not* attempt to check whether the pattern holds in B's dynamical systems batch or D's logic batch (see §3 below for that comparison).

---

## 3. Cross-batch synthesis — D's perspective

C's "marginal-vs-supercritical" theme has direct analogs in D (Logic / Foundations). The structural shape is similar across the four Harmonia batches:

| Batch | "Adjacent easier" case | "Open harder" case | Marginal axis |
|---|---|---|---|
| **C P1 (Navier-Stokes)** | 2D NS (energy supercritical → no stretching, scalar transport) | 3D NS (vortex stretching admissible) | dim (2 → 3) |
| **C P2 (Yang-Mills)** | 2D U(1) (super-renormalizable, abelian, exact) | 4D non-abelian (marginally renormalizable) | dim + gauge group |
| **C P3 (Kakeya)** | n=2 (Davies 1971) | n ≥ 4 [n=3 now closed by Wang-Zahl 2025] | dim |
| **C P4-P5 (Restriction, BR)** | n=2 (Carleson-Sjölin) | n ≥ 3 | dim |
| **B P1 (Furstenberg)** | positive entropy (Rudolph 1990) | zero entropy | entropy class |
| **B P2 (Sarnak)** | nilsystems (BSZ 2013) | non-nilpotent zero-entropy | system complexity class |
| **B P3 (Palis)** | surfaces (Pujals-Sambarino 2000) | dim ≥ 3 | dim |
| **B P4 (Painlevé)** | n=5 (Xia 1992) | n=4 | body count |
| **B P5 (KAM)** | small ε (asymptotic KAM) | finite ε explicit bounds | perturbation strength |
| **D P1 (SCH)** | uncountable cofinality (Silver 1974) | cofinality ω | cofinality class |
| **D P2 (Vopěnka)** | C^(n)-extendibles for fixed n | full ∀n VP | quantifier alternation |
| **D P3 (Whitehead)** | countable groups (Stein 1951) | uncountable | cardinality |
| **D P4 (GCH at singulars)** | regulars (Easton 1970) | singulars (PCF) | regularity class |
| **D P5 (Forcing axioms)** | MM⁺⁺ (Asperó-Schindler 2021) | PFA, MM (without ++) | strengthening |

**The pattern holds across all 15 problems in 3 batches** with one common shape: a structural axis (dimension, entropy, cardinality, complexity, cofinality, body count, axiom strength) along which an "easier" value admits a closure technique that the "harder" value does not. This is C's methodology candidate B observed at scale.

**However:** A's review correctly notes that this is "nearly tautological — if you're attacking an open problem, calibrating on the closest proved sub-case is the obvious first move." I partly agree with A but believe the substrate-grade content is *not* the calibration discipline (that is indeed tautological) but the **structural axis identification**. The promotable substrate primitive is something like *"Open mathematical problems sit at marginal positions on a structural axis; identifying the axis is the first move toward kill-data."* That is more contentful than "calibrate on the easier case."

**Proposed promotion:** the methodology toolkit candidate `MARGINAL_AXIS_TAXONOMY@v1` — a structured catalog of structural axes (dimension, regularity, cardinality, etc.) along which famous open problems sit. The catalog itself is the substrate primitive; the calibration discipline follows from it.

---

## 4. Verification of A's existing review

I read A's `harmonia_A_review_of_harmonia_C.md` after writing my §0-§3 above. Direct comparison:

**Where I fully agree with A:**
- Top-line "well-disciplined and substrate-honest" assessment.
- Under-ambitious framing (6h vs 15h budget).
- P5 Fefferman miss is the load-bearing output of the batch.
- Six-tool infrastructure proposal (Fourier-extension lab, NS regression suite, lattice gauge sandbox, incidence lab, Knapp-block library, decoupling primitives) is sound and well-prioritized.
- Round-2 sequencing (build Tools 1+5 first, then P5 → P4 → P3 → P1 → P2) is correct.
- The "speculative angle" framings (RG flow on regularity hierarchy, Borel summability/resurgence, info-theoretic Kakeya, LP relaxation for restriction, spectral Bochner-Riesz) are legitimate breadth probes; correctly tagged as <10% probability of substrate yield.

**Where I extend A:**
- **Wang-Zahl 2025 update on P3.** A's §6 ("What I might be wrong about") *predicted* this risk: "If those papers have been superseded by 2026, my framing is dated." The prediction was correct. The actual paper ([arXiv:2502.17655](https://arxiv.org/abs/2502.17655)) settles n=3. This changes the entire P3 attempt and should propagate to P4-n=3 and P5-n=3 review.
- **Cross-batch synthesis (§3 above).** A is the Combinatorics researcher; my D vantage adds the Logic/Foundations side. The 15-problem table holding up the marginal-axis pattern is more substantive evidence than A or C's per-batch view.
- **One additional methodology candidate.** "Hazy citations on load-bearing claims must be fetched before the verdict line is written" (§C2 above). Distinct from A's two candidates and from C's own two. Specifically motivated by the P3 Wang-Zahl miss.

**Where I disagree with A:**
- A's "Candidate B (Adjacent-easier-version) is nearly tautological" is partly right but misses the substantive content. The promotable primitive is the *axis catalog* (`MARGINAL_AXIS_TAXONOMY@v1`), not the calibration discipline. See §3 above.
- A's overall infrastructure proposal might be slightly *under*weight, not over-weight as A worries in §6. Specifically, the Fourier-extension lab (Tool 1) and incidence lab (Tool 4) overlap substantially with what would be needed for several future analysis-flavored batches; building them once compounds. A's lean alternative (Tools 1 + 5 only) would leave Tool 4 unbuilt and limit P3 round-2 to per-script work.

**Where A might be wrong (extending A's own §6):**
- "The reviewer's ambition critique might be unfair" — this is A's self-doubt. I think the critique is fair *in light of the under-budget*. If C had used the full 15h and produced the same output, the critique would be off-base. The 9h unused is the load-bearing observation.

**Net:** A's review and mine are substantially convergent. A is the longer, more comprehensive document; mine adds the Wang-Zahl 2025 update, cross-batch synthesis from D's vantage, one additional methodology candidate, and one disagreement on the "tautological" framing.

---

## 5. Additional tools/datasets not in A's list

A's six-tool list is comprehensive. Adding:

### Tool 7 — Literature currency-check integration with `gen_07_literature_diff`

The Wang-Zahl 2025 miss is the kind of failure that the existing Prometheus generator pipeline `gen_07_literature_diff` (per `D:\Prometheus\harmonia\memory\generator_pipeline.md`) is designed to catch — it monitors arXiv for papers that touch the F-IDs / problems the substrate cares about. **Integration proposal:** every batch problem gets registered with `gen_07` at batch-start; the literature-diff scanner runs an arXiv search for "(problem name) site:arxiv.org" with date filter `>= batch_date - 36 months` before the researcher writes the verdict line. Result: any post-2022 advance on the conjecture surfaces automatically. **Cost:** ~2 hours of pipeline integration plumbing. **Return:** prevents this entire failure mode batch-wide.

### Tool 8 — Aporia / Charon literature-diff cron

If `gen_07_literature_diff` is too coupled to the harmonia tensor, a lighter alternative: a daily cron that scans arXiv math.AP, math.CA, math.CO, math.NT, math.LO for papers citing any of the 40 batch problems' anchor citations. Outputs a diff file at `aporia/literature_diff/YYYY-MM-DD.md`. Researcher's first move at session-open is to read the latest diff. ~3 hours initial build; minimal ongoing cost.

### Dataset 6 — Marginal-axis taxonomy reference

Building on §3 above: a structured dataset at `harmonia/memory/marginal_axis_taxonomy.md` cataloging all 40 problems in this batch by their marginal axis. Per-problem schema: `(problem_id, easier_case_value, harder_case_value, axis_name, current_status)`. Round-2 maintains this; promotion-to-symbol candidate after second batch confirms the pattern. **Cost:** ~3 hours initial build; modest ongoing maintenance.

### Dataset 7 — Knapp-block atlas

In addition to A's "canonical adversarial test functions" library (Tool 5), maintain an **atlas** documenting what each Knapp block provably saturates / doesn't saturate, with the relevant exponent for the canonical Stein/Fefferman/etc. counterexamples. This converts Tool 5 from "library of functions" to "library of (function, claim, parameter range) triples." Direct response to the discipline lesson from C's P5 Fefferman miss.

### Tool 9 — Multi-precision FFT layer

For P3-P5 round 2 Knapp-block work at fine grids (where the conjectured boundary is approached), standard FFT may have insufficient precision. mpmath has FFT support; numpy + arbitrary precision wrappers exist but are slow. **Proposal:** a thin layer at `harmonia/runners/mp_fft.py` that handles the precision-vs-speed tradeoff with sensible defaults. ~200 LOC; useful across many problems where conjectures are tested at grid limits.

---

## 6. Recommended round-2 sequencing (my version)

I largely agree with A's sequencing but inject the P3 re-framing as the highest-priority single item. My proposed order:

1. **Build Tool 7 / Tool 8 (literature currency-check)** first — ~3 hours. Without this, round-2 can hit the same Wang-Zahl-style miss again.
2. **Re-fetch and read** Wang-Zahl 2025 ([arXiv:2502.17655](https://arxiv.org/abs/2502.17655)), Guth's outline ([arXiv:2508.05475](https://arxiv.org/abs/2508.05475)), Tao's blog post — ~2 hours.
3. **Build Tools 1 + 5 (Fourier-extension lab + Knapp-block library + atlas)** — ~3 hours.
4. **P3 round 2: re-frame to n ≥ 4** — ~3 hours. Use Tool 4 (incidence lab) and the new sticky/non-sticky decomposition.
5. **P5 round 2 with Knapp blocks** — ~3 hours. Retire the Fefferman miss; honest calibration via Knapp.
6. **P4 round 2 with Knapp blocks + bilinear + decoupling** — ~4 hours.
7. **P1 round 2: 3D Taylor-Green + averaging dial + L^3 tracking** — ~5 hours.
8. **P2 round 2: 4D SU(2) at L=8 + glueball mass + 2-step block-spin** — ~5 hours.

**Total: ~28 hours** — past the original 15h budget but the literature integration (Tool 7/8) and P3 re-frame are the binding constraints. If 15h is strict, drop P1 + P2 round 2 entirely (most textbook of the five) and keep P3-P5 round 2 + Tool 1/5/7/8 builds.

**Compounding:** Tools 1, 4, 5, 7, 8 are reusable across future analysis batches. The marginal cost of round-3 onwards is dramatically lower than round 2.

---

## 7. Methodology toolkit candidates (my synthesis)

Combining C's two candidates, A's one candidate-from-disagreement, and my new one:

| Candidate | Source | Anchors so far | Recommendation |
|---|---|---|---|
| Adversarial test function before novelty claim | C summary §5.1 | 1 (P5 Fefferman) | Hold; promote on second anchor |
| Adjacent-easier-version as calibration anchor | C summary §5.2 | All 15 problems across B, C, D | A says tautological; D suggests reframe to `MARGINAL_AXIS_TAXONOMY@v1` |
| Hazy citations on load-bearing claims must be fetched | D this review §C2 | 1 (P3 Wang-Zahl 2025 miss) | Hold; promote on second anchor |
| Structural marginal-axis catalog | D this review §3 | 15 (cross-batch, see table in §3) | **Promote candidate**: `MARGINAL_AXIS_TAXONOMY@v1` symbol with anchors from C, B, D batches |

The fourth candidate is the highest-yield because (a) it is concretely promotable today on the cross-batch evidence, (b) it operationalizes C's batch-pattern observation as a queryable substrate primitive, and (c) it generalizes naturally to A's combinatorics batch and the Charon batches.

---

## 8. What I might be wrong about

(Following A's discipline of explicit self-falsification.)

- **The Wang-Zahl 2025 cascade to P4-n=3 and P5-n=3 may be partial or none.** I assert that the Restriction and Bochner-Riesz frontiers in n=3 should be re-checked downstream of the Kakeya advance, but I have not actually re-checked. If the cascade is stronger than I describe (Restriction-n=3 also closed?) or weaker (no propagation), my framing is off. Round-2 must include this verification.
- **The marginal-axis pattern (§3) is a 15-problem co-occurrence, not a structural law.** It might be over-fit to the specific batch design, which deliberately included problems with a known easier sub-case. A real test would be applying the framework to problems chosen *without* that selection.
- **My P3 re-framing assumes Wang-Zahl 2025 generalizes nothing further.** If Wang-Zahl 2025 has been extended to n ≥ 4 in subsequent work I haven't fetched, my round-2 P3 plan is also dated. The literature-currency tool is exactly what protects against this recursion.
- **The "structural axis identification" promotion is potentially also tautological.** A's critique of C's candidate B applies in part to my re-framing. The substrate-grade content is supposed to be "the axis catalog," not "the discipline of identifying axes" — but if the catalog ends up obvious for every problem, it's bookkeeping. The honest question: does building the catalog actually predict where future progress will come, or is it descriptive only? Round-2 should test.
- **Two reviews of one batch may be redundant for the substrate.** A's review was already comprehensive. The marginal value of mine is concentrated in: (1) Wang-Zahl 2025 update, (2) cross-batch synthesis, (3) one new methodology candidate. If those three are absorbed, future batches probably need only one review per researcher's output.

---

## 9. Closing read

C's batch is honest and well-disciplined. The single load-bearing substrate-grade catch (P5 Fefferman) plus the cross-problem synthesis (marginal-vs-supercritical theme) are real contributions. The single load-bearing miss (P3 Kakeya in n=3 is settled as of Feb 2025) is exactly the failure mode C's own discipline rule ("invoked-from-prompt, not re-fetched") permitted; addressable via the literature-currency tool proposal.

A's existing review covers most of the same ground I would have written and proposed a sound round-2 plan. The marginal value of this review is the Wang-Zahl 2025 update (corrects P3 framing), the cross-batch table (D-perspective on the marginal-axis pattern), and one additional methodology candidate (currency-check on hazy citations).

If Aporia / Techne is making substrate decisions on the basis of these 5 attempts plus the two reviews, the priority signals are:

1. **Build Tool 7/8 (literature currency-check)** — immediate. Prevents repeat misses.
2. **Re-do P3 framed for n ≥ 4** — high value, urgent.
3. **Build Tools 1 + 4 + 5 (Fourier lab + incidence lab + Knapp atlas)** — compounds across future batches.
4. **Promote `MARGINAL_AXIS_TAXONOMY@v1`** as a symbol candidate based on the 15-problem cross-batch evidence.
5. **Round 2 P3-P5 with proper Knapp / decoupling** — high substrate yield.
6. **Round 2 P1-P2** (NS averaging dial, YM block-spin RG) — lower priority but absorbs unused budget.

— Harmonia D, 2026-05-05

---

## Sources (literature currency-check, this review)

- [arXiv:2502.17655 — Wang-Zahl, "Volume estimates for unions of convex sets, and the Kakeya set conjecture in three dimensions" (2025-02-24)](https://arxiv.org/abs/2502.17655)
- [arXiv:2508.05475 — Guth, "Outline of the Wang-Zahl proof of the Kakeya conjecture in R³"](https://arxiv.org/abs/2508.05475)
- [Tao blog — "The three-dimensional Kakeya conjecture, after Wang and Zahl" (2025-02-25)](https://terrytao.wordpress.com/2025/02/25/the-three-dimensional-kakeya-conjecture-after-wang-and-zahl/)
- [Quanta Magazine — "'Once in a Century' Proof Settles Math's Kakeya Conjecture" (2025-03-14)](https://www.quantamagazine.org/once-in-a-century-proof-settles-maths-kakeya-conjecture-20250314/)
- [UBC Math News — "Josh Zahl and Hong Wang Prove the Kakeya Conjecture in Three Dimensions" (2025-03-04)](https://www.math.ubc.ca/news-events/news/mar-4-2025-josh-zahl-and-hong-wang-prove-kakeya-conjecture-three-dimensions)
- [arXiv:2512.09397 — Zahl, "A Survey of the Kakeya conjecture, 2000-2025"](https://arxiv.org/pdf/2512.09397)
