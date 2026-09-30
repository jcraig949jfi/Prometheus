# Ruler-quality audit, 2026-09-30 (Harmonia CWO item promoted from NEXT)

Harmonia[m2-475d761f], under the operator CWO 2026-09-30 (HARMONIA: "Ruler quality: saturated, gameable, unreachable or
non-discriminating rulers") and MWO-0004.

**Scope:** verdict-bearing clauses in recent frozen preregistrations whose outcomes were not yet reported at selection
time:
- Tyche dark-ecology v0 (075e5fc21 + amendment 1 e9442d5c0);
- Hecate novelty autopsy (d6d4b9533);
- Hecate alien-lawful validation rule (1fed85d95).

**Method:** two read-only audit agents computed attainability, null-pass probability, power, ceiling and gameability
(exact binomials or small simulations; scripts in Harmonia's scratchpad). **Every MAJOR/BLOCKING item was re-verified
by Harmonia** (marked HV). Severity:
- BLOCKING: the verdict is predetermined or unreachable;
- MAJOR: the ruler cannot discriminate, or licenses a claim it does not test;
- MINOR: hygiene or sanity-only.

**Timing note:** by the time of verification, Tyche's rerun had completed (rows at d5b25e4e0) and Hecate's autopsy had
run (e4a05ba3b). Amendment before exposure is therefore no longer possible for these. The findings bear on **how the
verdicts must be labelled**.

## 1. Tyche dark-ecology v0

| Rule (roles/Tyche/prereg/2026-09-30_v0/PREREG.md) | Finding | Severity |
|---|---|---|
| **H1** planted positive control: "VOID ... if the best initial lens's test gain >= 0.03 ... PASS if >= 4 valid worlds and >= 4 SOLVED" | **PASS is unreachable (HV).** The fixed initial population (master seed 20260930) gives best-initial test gains P3 0.227, P4 0.109, P6 0.141, so all three are VOID. Only P1, P2 and P5 are valid, and 3 < 4. Source: `tyche/runs/v0_2026-09-30_ABORTED/PASS_A_BASELINE.json` `initial_population_best`, reproduced independently by a replay from committed code. The prereg predicted P3 and P4 SOLVED. | **BLOCKING** |
| **H6** end to end: "PASS iff H1, H2 and H5 PASS ..." | Inherits the H1 impossibility. **PASS is unreachable.** | **BLOCKING** |
| **H3** residual shift: negative-world arm "on >= 80% of selection negative worlds it moves by <= 0.03" | Agent simulation: ecology growth alone (random 16-48-lens ecologies) moves the err fraction 0.04-0.13 on most negative worlds. The arm passed in 0/20 simulated ecologies at 16-48 lenses. The arm measures ecology size, not a planted effect. **Not re-run by Harmonia (agent simulation only).** | **MAJOR** |
| H4 redundancy | FAIL is nearly unattainable (K1/K2 baselines are 1.0, K3 lin 0.989). Sanity check, not a hypothesis. | MINOR |
| H5 instrument | FAIL is unattainable by construction (all ops causal). Sanity gate. | MINOR |
| H2 false gradients; admission gate (z >= 4, gain >= 0.01); replicated/beats_null | Null-pass about 1e-8 per lens x world; a constant-lens cheat reaches max z 2.75. **Sound.** | OK |
| Twin z < 3 check | Up to about 10% spurious NOT_SOLVED across 6 cases. | MINOR |
| Amendment 1 | No threshold changed (recorded). The compute guard adds a stopping rule that can shorten epochs (it affects H3/H6 end points). No `interventions_unseen` field (STANDING_RULES A1 form). The rerun is a near-replay of the aborted run (same seeds), so blinding rests on the author not reading the aborted rows. | MINOR |

**Required labelling (Harmonia CHARTER s1: "report 'nothing could fire' as its own label"):**
- H1 and H6 must not be reported as scientific FAIL/INDETERMINATE of lens evolution. They are **UNREACHABLE_BY_DESIGN
  (NOTHING_COULD_FIRE for PASS)**, and the report should show the valid-world count (3) beside the rule.
- H3's negative-world arm should be read beside a random-lens-ecology drift baseline, or labelled
  NON_DISCRIMINATING.
- What remains informative in v0: H2 and the admission gate (sound), plus per-world SOLVED status on P1, P2 and P5
  as descriptive results.

## 2. Hecate alien-lawful validation rule (hecate/alien PREREG.md:144-148)

| Clause | Finding | Severity |
|---|---|---|
| T1 AUC >= 0.80 with CI-low >= 0.65 (n 32 vs 30) | Saturated for the LLM (pilot 0.98, CI-low 0.95, while 19/30 noise systems were labelled RULE: the score is confidence). The CI clause never binds at this n. Null-pass 0.000 at true AUC 0.5. | MAJOR (non-discriminating in practice) |
| Pair accuracy >= 0.80 (n = 30; 24/30 needed) | Null-pass 0.0007 at 0.5; power 0.85 at a true 0.85. But 8/30 pairs are adversarial-vs-SEDUCTIVE, a class the prereg itself flags as possibly unsolvable (PREREG.md:157-158). A detector perfect on the other 22 but at chance on those 8 passes only about 0.96/0.57/0.37 at true 1.0/0.9/0.85. | MAJOR (structural ceiling) |
| **Construct: the conjunction is named NOVELTY_DETECTOR_VALIDATED** | **Gameable by a non-novelty baseline (HV).** Applying the frozen rule with the committed scorer (`score.auc`, `score.boot_diff`) to `data/BASELINES.json`: the lookup-table baseline passes, `localtab_t2_comp` (AUC 0.844, lo 0.721, pair 0.800) and `localtab_eval_exact` (0.852, 0.747, 0.817), as does affine on its 12 pairs. The rule validates **lawful-vs-noise discrimination, not novelty**. | **MAJOR** (construct validity). Not BLOCKING, because no current verdict is wrong: the pilot is NOT_VALIDATED. A future VALIDATED must not license "novelty" or "no unfamiliar mechanisms" claims. |
| Pair n counts successful calls only; no minimum n | A failed call silently shrinks n. | MINOR |
| Phase 2 visual (9edcb1169) | No decision clause; n = 5 pairs (even 5/5 has null p = 0.031); `key.json` sits beside `sets.json`. | MINOR |

## 3. Hecate novelty autopsy (d6d4b9533; run at e4a05ba3b)

| Clause | Finding | Severity |
|---|---|---|
| R1: UNFAMILIAR rate on ALIEN <= 0.10 (<= 3/32) | The arithmetic is sound (P(R1) = 0.093 at a true rate of 0.20). But the detector has **no UNFAMILIAR positive control**: `hecate/gravity/calibration_v1.json` contains 0 unfamiliar items (HV, same as evidence audit B). R1 therefore shows "this detector did not call these 32 UNFAMILIAR", **not** "UNFAMILIAR is unreachable". The autopsy's formalism reading is plausible but not a preregistered discrimination. | MAJOR |
| R2: ALIEN >= 0.50 and KNOWN <= 0.10 | Low power near the thresholds (0.53 at 0.5/0.05). The DESTROY class is collected but ungated. | MINOR |
| Part A flow accounting | **No defined null** for "more or less often than chance" (no test, alpha or permutation). Any skew claim from it is post hoc. | MAJOR (for skew claims) |

## 4. Cross-cutting ruler rules (proposed for STANDING_RULES; Harmonia's own lane)

- **R-A (reachability first):** before any run, compute the attainable outcome set for every gated verdict at the actual
  design. The VOID/eligibility rules plus fixed seeds can decide a PASS before a single generation (Tyche H1). This
  applies CHARTER s1 to design time.
- **R-B (absence needs a positive control):** a detector's "zero X" requires a calibration item on which it outputs X.
- **R-C (construct name = what a shortcut cannot pass):** run the frozen rule on every committed baseline. If a
  non-construct baseline passes, the verdict's name must be narrowed.
- **R-D (ceiling):** a non-inferiority or accuracy clause whose control sits within one margin of the maximum is a sanity
  check, not a test (see evidence audit D).

## Routing

- **Tyche:** H1/H6 UNREACHABLE_BY_DESIGN labelling, before its v0 report.
- **Hecate:** construct narrowing; the R1 reading; the flow null.
- No infrastructure defect for Builders.
- No operator escalation: no CWO s4 class applies, and no frozen decision rule is changed. The findings are about
  labelling and future design.

## CORRECTION C-1 (2026-09-30, after Tyche #1047): the H4 rating was wrong. SUPERSEDED as written above.

- **Section 1 said:** H4 FAIL is "nearly unattainable (K1/K2 baselines are 1.0, K3 lin 0.989). Sanity check, not a
  hypothesis."
- **That judged reachability from the epoch-0 baselines only.** The baseline is a function of the evolving ecology. The
  tab organism's feature budget is filled newest-lens-first, so as the ecology grows it can push the raw channels out.
- **Verified by Harmonia from `tyche/runs/v0_2026-09-30/RESIDUALS.jsonl`:** K1_ident `R0|tab|val` at
  - passA/epoch0: 1.000 (ecology size 0);
  - epoch1: 0.995 (11);
  - epoch2: **0.547** (21);
  - epoch3: 0.998 (32);
  - final: **0.518** (44).
- A lens restoring the channel was admitted (Tyche reports a conf gain of +0.49). **H4 FAIL was attainable, and it was
  attained.** H4 is a real test of redundancy under an evolving baseline, not a sanity check.
- **The error was Harmonia's.** Tyche's counterpoint is accepted in full, and F1 is amended accordingly (STANDING_RULES
  F1).
- The other section-1 findings stand: H1/H6 UNREACHABLE_BY_DESIGN (the VOID status is fixed by the initial population
  and does not evolve), and H3 negative arm NON_DISCRIMINATING. Tyche applied both labels (bdeba9865).
