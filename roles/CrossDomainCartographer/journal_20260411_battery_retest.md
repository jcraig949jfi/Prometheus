# Journal — 2026-04-11 (Battery Retest Session)
## The Audit Becomes the Discovery

### What happened

Picked up from the Battery Session (2026-04-12 journal). Built unified battery infrastructure (F1-F23), applied three micro-refinements, then ran the full battery on every Probable and Possible finding. Two kills. One confirmation. Two need more data.

### Infrastructure built

1. **battery_logger.py** — Structured JSONL logging. Every finding gets a timestamped record with all test verdicts, parameters, and metadata. Audit trail in `cartography/convergence/data/battery_logs/battery_runs.jsonl`.

2. **battery_unified.py** — Single interface wrapping F1-F14 (falsification_battery.py) + F15-F23 (battery_v2.py). Two modes: `test_distribution()` for moment/value claims, `test_correlation()` for paired data. Auto-classifies by tier.

3. **Micro-refinements applied:**
   - **F19**: Variance ratio check — if synthetic_std / |real_stat| > 10, verdict = MODEL_MISSPECIFIED
   - **F22**: Complexity penalty — transforms that destroy ordering get penalized in the combined score
   - **F23**: Multi-method agreement — k-means + hierarchical + GMM must agree (gate 5). LATENT_CONFOUND now requires 4/4 validation gates.

### The kills

**P4/S8: Galois enrichment on class number — KILLED by F17**
- Previous claim: Galois group enrichment 3.68x-5.12x on class number. Degree enrichment 2.56x-3.00x. "Enrichment is MAX not multiplicative."
- F17 result: sensitivity = 0.66 (CONFOUND_DOMINATED). Conditional on degree strata, enrichment drops from 3.94x to 1.34x.
- Within-degree verification: Degree 3 → 1.16x, Degree 4 → 0.40x (anti-enrichment!).
- **The Galois "enrichment" was entirely a degree artifact.** Different Galois groups cluster at different degrees, and different degrees have different class number distributions. Control for degree, and Galois adds nothing.
- This kills the "MAX not multiplicative" claim (P4) too — the "nesting" was just degree → Galois → class number, a chain of confounds.
- **Lesson: F17 confound sweep should be MANDATORY for any enrichment claim.** Before this session, we only had corrected enrichment values (via F17), but hadn't actually killed any finding with it.

**Isogeny diameter — KILLED by F23 (nuanced)**
- Previous claim: diameter ~ 1.80·log(n), R²=0.92, Ramanujan expander.
- F1-F14: ALL PASS. z=101, cross-validated, phase-decay confirmed, growth-rate robust. F21: ROBUST.
- F23 result: LATENT_CONFOUND at k=4, delta_r=0.23, all 5 gates pass (stability 0.998, silhouette 0.587, 3/3 methods agree).
- Investigation: Slopes vary 0.71-1.94 across size regimes. Small primes (n<100) have steep slope ~1.94, large primes (n>1000) have flatter slope ~0.71.
- **Correct framing:** The relationship is real — diameter does scale with log(n). But a single slope is wrong. The coefficient drifts: c(n) → {1.94 small, 1.12 medium, 0.71 large}. This is the "finite-size effect" the previous journal already flagged.
- **Not a full kill — a refinement.** The claim should be: "diameter = O(log n) confirmed, but coefficient is size-dependent."

### The survivors

**P2: Space group predicts Tc — PROBABLE (confirmed)**
- Eta² = 0.4551, exactly matching the previous claim.
- Band gap eta² = 0.0953 — much weaker, confirming selectivity.
- F17: CONFOUND_ROBUST (sensitivity 0.20). F18: STABLE.
- This is the cleanest survivor. Space group specifically predicts superconducting Tc and nothing else.

**P1: G2 conductor M4/M2^2 = 2.939 — POSSIBLE**
- 63,107 USp(4) conductors tested. M4/M2^2 = 2.9391 [2.917, 2.962].
- F15: DEVIATES_FROM_LOGNORMAL. F16: EQUIVALENT to 3.0 (inside ±10% bounds). F18: STABLE (CV ratio 0.43).
- F20: REPRESENTATION_DEPENDENT (CV across transforms = 0.32).
- Classified POSSIBLE not PROBABLE because no Tier B test ran (no confound data available for distribution-only test). Need to provide paired data or group labels to trigger F17/F21/F23.
- The value is real and stable. It's 2.939, not 3.000. Needs investigation of what determines it.

**K1: Knot determinant M4/M2^2 = 2.156 — POSSIBLE (kill holds)**
- 2,977 determinants. M4/M2^2 = 2.1555.
- F16: INCONCLUSIVE on SU(2)=2.0. The 90% CI [2.10, 2.21] barely touches 2.0 at the lower edge.
- F20: WEAKLY_DEPENDENT (CV across transforms = 0.28).
- The original kill of "knot det = SU(2)" holds. It's close but not exact.

### What this means

**Before this session:** 4 Probable, 8 Possible, 8 Killed.
**After this session:** 1 Probable, 4 Possible (2 from Probable), 2 new Kills.

The battery does what it's supposed to: it kills things that looked real. The P4/S8 kill is clean — a finding we had at "Probable" tier for days was entirely a degree confound. F17 caught it in one test.

The honest count is now:
- **Validated:** Euler relation, S_n character formula (exact identities)
- **Probable:** P2 (SG→Tc) — the only finding that survives the full F1-F23 battery with Tier B confirmation
- **Possible:** P1 (G2 conductor 2.939), K1 (knot det 2.156), Isogeny (log-diameter with drifting coefficient), and ~30 untested conjectures from previous session
- **Killed:** P4/S8 (Galois enrichment = degree confound), Isogeny single-slope, plus all previous kills

### The philosophical update

The battery now has **23 tests + 5 gates + structured logging**. It caught a finding that survived for 4 days as "Probable." The correct response to this is not dismay — it's calibration. Every kill makes the surviving findings stronger.

The question we should be asking about P2 (the only Probable survivor) is: **why does space group predict Tc but not band gap?** That's the genuine mystery. Eta²=0.45 for one property and 0.095 for another in the same dataset, using the same grouping variable. The answer is in the physics of superconductivity — crystal symmetry constrains Cooper pair formation differently than it constrains electronic structure.

---

*5 findings retested. 2 killed. 1 confirmed. 3 new scripts. 3 micro-refinements.*
*The battery is 23 tests + 5 gates + multi-method agreement.*
*The honest number of Probable findings: 1.*
*April 11, 2026*
