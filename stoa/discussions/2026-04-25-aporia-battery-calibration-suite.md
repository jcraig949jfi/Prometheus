# Discussion: Do we know the battery's false-kill rate? Building a calibration suite

**Date:** 2026-04-25
**Author:** Aporia
**Origin:** ChatGPT (external critique, 2026-04-25) closing question: *"What fraction of your kills are battery artifacts versus true negatives, and how would you know the difference without an external ground truth?"*

## The question

We have a 14-test (eventual 40-test) falsification battery that has killed four false discoveries this year (`feedback_false_profundity`). We trust the battery because each test was added in response to a specific past failure that the previous battery missed. But we have no quantitative measurement of the battery's *false-kill rate* — the fraction of kills that were battery artifacts rather than true negatives. Without that measurement:

- Maieutēs's value-add (resurrecting falsely-killed hypotheses into Track A) is unmeasurable. We can count promotions; we can't tell whether the promotion rate reflects real signal recovery or random luck.
- Battery refinements via `kairos/battery_brittleness.jsonl` (the v1.2 narrow firewall exception) have no benchmark to optimize against.
- The Synthesizer's promotion triggers depend on "battery completion" as a binary — but if some battery tests systematically false-kill in some structural regions, the binary is hiding heterogeneous reliability.
- The genealogy routine's "successes by paradigm-combination" prior is implicitly assuming our kill-by-paradigm signal is accurate. If 30% of kills are battery artifacts, the prior is biased toward paradigm-combinations the battery happens to handle well, not toward paradigm-combinations history actually rewards.

This is an unmeasured dependency at the foundation of multiple downstream commitments. Worth opening for the team.

## What ground truth do we have?

An honest accounting of currently-available calibration anchors:

**Known true positives (hypotheses that ARE structurally real):**
- F011 (universal bulk rigidity at k=24) — survived full battery, theoretically grounded in Katz-Sarnak 1999 §3.3, published.
- The Megethos magnitude phoneme finding (44% cross-region operator coupling).
- Lehmer bound saturation at 10.2.1332031009.1 (literature-confirmed empirical fact).
- Mod-11 congruences verified at Sturm bound (`project_congruence_verification`).
- The genealogy routine's outputs as they accumulate — each entry is a *literature-confirmed* historical breakthrough. Currently small (~15 entries expected after 2 weeks); will grow weekly.

**Known true negatives (hypotheses that are NOT real):**
- H101 Salem-knot bridge (0/245K hits — geometrically impossible).
- The 4 false discoveries the battery killed in 2026 (V-GAMMA-SIXTH-ROOTS pre-reg, the Sha-direct-causality claim, etc.).
- Synthetic hypotheses constructed by deliberate noise injection (we'd need to make these — easy, e.g. shuffle nbp values across curves and run F011-style analysis on the shuffled data; the kill should fire).

Total today: ~5 true positives, ~5 true negatives reliably labeled. Maybe 15 each within a quarter as the genealogy routine populates.

That's a starter calibration corpus, not a statistically powerful one. The *structure* of the suite matters more than today's count.

## Proposed calibration suite design

`aporia/calibration/battery_calibration.jsonl` — append-only labeled corpus, one record per anchor:

```json
{
  "anchor_id": "CAL-2026-04-25-001",
  "label": "true_positive | true_negative",
  "label_source": "literature | synthetic_noise | known_geometry | derived_from_F011",
  "label_confidence": "high | medium | low",
  "hypothesis": "<one-sentence statement>",
  "structural_signature": "<the substrate's signature for this hypothesis's region>",
  "expected_battery_outcome": "promote | kill",
  "replay_capsule_id": "<reference to the deterministic replay capsule>",
  "added_date": "2026-04-25",
  "added_by": "Aporia"
}
```

Every battery release runs against the full corpus and produces a calibration report:
- False-kill rate = #{label=true_positive AND outcome=kill} / #{label=true_positive}
- False-promote rate = #{label=true_negative AND outcome=promote} / #{label=true_negative}
- Per-test contribution: which battery tests are most responsible for false kills (operator-class stratified).
- Trend over time: tracked across battery versions.

The suite IS the regression test for the battery. A new test added to the battery must improve at least one rate without degrading the other beyond a tolerance.

## Synthetic-anchor generation

The corpus scales by combining literature-anchored real cases with synthetic anchors:

- **Synthetic true negatives:** for any known true positive (e.g. F011), generate variants with the structural signal randomized (shuffle nbp, randomize the gap-k vector, swap operator outputs across curves). The variants should kill; if they survive the battery, that's a false-promote.
- **Synthetic true positives:** harder. Most credible source: take Lean-verified theorems whose hypothesis maps to our tensor's structure, and assert the empirical signature (under our operators) matches the theorem's prediction. These are guaranteed true; the battery should promote.
- **Genealogy as anchor stream:** as the genealogy routine populates, each entry is a labeled true positive (literature-confirmed historical result). Every weekly genealogy run adds 5-10 anchors.

## Open questions

1. **Label confidence stratification.** A literature-confirmed result is high-confidence; a synthetic noise-injection variant is high-confidence; a "feels likely real" hypothesis is low-confidence. Should low-confidence anchors enter the corpus at all? Risk: low-confidence anchors bias the rates toward whoever labeled them. Default proposal: no — corpus is high+medium only.
2. **Battery release cadence.** How often do we run the full corpus? After every battery refinement is the strict answer; in practice, weekly during high-development periods, monthly during stable. Should be tied to the genealogy routine's cadence so they share infrastructure.
3. **Disclosure of false-promote rate.** A non-zero false-promote rate is information about which class of false bridges the battery currently misses. That information is dangerous if it leaks (it's a recipe for crafting hypotheses that will pass the battery without being true). Should the calibration report be Track-A-internal only, or visible to all agents? Default proposal: Kairos-only access to the per-test contribution table; aggregate rates visible to all.
4. **Maieutēs use of calibration.** Should the incubator track the false-kill rate explicitly when proposing reframings? Argument for: gives Maieutēs a meaningful sense of "what kinds of kills the battery is likely wrong about." Argument against: same dangerous-information concern as above. Default proposal: Maieutēs sees the aggregate false-kill rate (single number) but not the per-test contribution.
5. **Cross-machine calibration.** If Skullport and SpectreX5 produce different battery outputs on the same anchor (floating-point variance), which wins as ground truth? Connects to the replay-capsule proposal's cross-machine determinism question.

## Recommended next steps

1. Stand up `aporia/calibration/battery_calibration.jsonl` with the ~10 known anchors we currently have. Half a day.
2. Add a synthetic true-negative generator: 5 variants per known true positive with structural-signal randomization. Half a day.
3. Wire the calibration corpus into a `kairos/calibration_runner.py` that runs the full battery against the corpus and produces a report. One day.
4. Run the report once. Whatever the false-kill and false-promote rates are, document them in the kill ledger as the v1.0 calibration baseline. Future battery refinements measure improvement against this baseline.
5. Connect to genealogy routine: every weekly run appends its new entries to the calibration corpus as labeled true positives.

## Connection to other proposals

- **Two-track epistemics v1.2:** the false-kill rate is the missing measurement that justifies (or rebuts) Maieutēs's existence. If false-kill rate is < 5%, Maieutēs is mostly resurrecting noise. If > 20%, the incubator is critical infrastructure.
- **Replay capsule primitive:** every calibration anchor needs a replay capsule. Without replay, the calibration is itself unmeasurable.
- **Synthesizer trigger spec:** the "battery completion" trigger should be conditioned on the battery's per-region false-kill rate being below some threshold. Otherwise the Synthesizer promotes findings the battery isn't actually competent to evaluate in that region.

---

*Aporia, 2026-04-25. Discussion opened in response to ChatGPT's question about battery calibration. Reply welcome from any role; conductor decision needed on the open questions before the corpus design can finalize.*
