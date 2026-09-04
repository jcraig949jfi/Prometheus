# GATE-1 STATUS — 2026-09-03 — OPEN FOR `spec-evca-density`, WITH SCOPE

**Gate text** (ruling authorisation 5, charter GATE-1): *no evolutionary compute runs until at least one specimen reaches `ARTIFACT_IN_HAND`, or a reconstruction is proven sufficiently exact.*

**Status: BOTH conditions are now met for this one specimen.** The gate opens for `spec-evca-density` and remains closed for every other specimen.

---

## Condition 1: ARTIFACT_IN_HAND — met

`J_RECOVERED_ARTIFACT_MANIFEST.jsonl` is no longer empty. Fourteen rows: thirteen `ORIGINAL_SPECIMEN` papers, hashed and stored under `herakles/specimens/spec-evca-density/original/`, and one `RECOVERED_SPECIMEN`, which is the artifact that actually matters.

**The recovered specimen is six evolved and hand-designed genomes from 1993 to 1995**, preserved only as printed hexadecimal in published tables. Four were produced by the genetic algorithm on different runs. **Two of the six appear in no other publication**, so they were one printed table away from being lost.

## Condition 2: reconstruction proven sufficiently exact — met, for the CA half only

This is the part that needs stating precisely, because the two halves of the physics are in different states.

**The cellular-automaton half is proven exact by execution.** The seat re-derived two of the six rules from their mathematical definitions and matched the published hexadecimal in all thirty-two digits: the simple majority rule, and the hand-designed Gacs-Kurdyumov-Levin rule. Those two act as calibration for the other four. All six then reproduce published performance under our implementation:

| Rule | Published at N=149 | Measured | Difference |
|---|---|---|---|
| maj | 0.000 | 0.000 | 0.000 |
| exp | 0.652 | 0.664 | +0.012 |
| par | 0.769 | 0.765 | -0.004 |
| particle1 | 0.742 | 0.733 | -0.009 |
| particle2 | 0.755 | 0.742 | -0.013 |
| GKL | 0.816 | 0.820 | +0.004 |

Measurement standard error at ten thousand initial conditions is about 0.004 to 0.005, and the paper's own reported standard deviation is 0.004. Five of six sit within about two standard errors; the largest gap is plausibly a maximum-relaxation-steps convention difference, since the exact stopping rule for the reporting measure is not fully specified in print.

**The genetic-algorithm half is specified but not yet validated.** Every parameter is in print and confirmed, but no artifact has yet checked our implementation of selection, crossover and mutation.

---

## The circularity problem, and why it does not bite

There was a real risk here. If the only validation target for the genetic algorithm were the 7/300 transition rate, then Stage 1 would be simultaneously the validation and the measurement, and a failure would be uninterpretable: bad reconstruction, or a phenomenon that does not reproduce, with no way to tell them apart.

The recovered artifacts supply **validation targets that are independent of the rare transition**:

1. **The four-epoch fitness signature.** Forty-six of fifty runs in the Physica D configuration show it. That is a high-frequency, cheap-to-hit target.
2. **Four of fifty runs never exceeding fitness 0.5.**
3. **Thirty-seven of fifty stuck at 0.5 when crossover is disabled**, which is a strong differential signal specifically about the recombination operator.
4. **Fitness of the recovered rules under the biased density-uniform measure**, computable directly from the genomes now in hand.

So the genetic-algorithm implementation can be validated on targets 1 through 4 **before** the transition rate is ever measured. If it passes those and then misses 7/300, that is evidence about the phenomenon. If it fails those, that is evidence about our code. The pre-registered `RECONSTRUCTION_FAILS` outcome is now diagnosable rather than merely declarable.

**This is a genuine improvement in the experiment that only became possible because the artifacts were recovered.** It was not visible when the plan was written.

---

## Two anomalies found during recovery

### A confirmed error in a published specimen

The 1995 PNAS table prints the majority rule as `...0117177701171777...` where the mathematics requires `...0117177f0117177f...`. Hex positions 15 and 23 differ.

**Confirmed independently by the seat**, not merely reported. Those two positions cover neighbourhood indices 60 to 63 and 92 to 95. Every one of those eight neighbourhoods has a population count of at least four out of seven, so a majority rule must output 1 for all of them, which requires the nibble `f`. Neighbourhood 0111100 alone settles it: four ones out of seven is a majority.

The EvCA review paper prints it correctly. The consequence is small, because the majority rule scores zero either way, but a reconstruction that took its baseline from the PNAS table would have been running something that is not the majority rule while calling it one. That is the class of defect that silently corrupts a reconstruction, and it is a fair example of why execution beats transcription.

### A reported anomaly that did NOT reproduce

The recovering agent reported that one rule, `particle2`, showed performance *rising* with lattice size, which would be backwards for a particle-based strategy and would cast doubt on its digits.

**The seat could not reproduce that.** Independent measurement gives 0.750, 0.695, 0.694 across N of 149, 599 and 999: normal monotone degradation. The anomaly is attributed to the agent's own scoring rather than to the rule or the transcription, and the rule is retained at high confidence.

This is recorded because it is the seat verifying its own subagent. An agent's reported anomaly is a lead, exactly like a historical paper's reported anomaly, and it gets the same treatment.

---

## What did not survive, documented rather than asserted

**The simulation source code was not found.** The project site has directory indexing enabled and was fully enumerated: every file is HTML, PDF or PostScript, with no archive or source extension anywhere. Software, code, data, rules, download and source paths all return 404. The Santa Fe FTP host is DNS-dead. Code search returns only modern third-party reimplementations. First-party corroboration: Hordijk's own retrospective describes the surviving site as carrying the papers only.

**One channel remains genuinely unchecked.** The Internet Archive CDX and replay interface returned rate-limit errors on every attempt across roughly fourteen retries, while the lightweight availability interface confirms that snapshots exist for both the pre-migration Santa Fe project site and the later site. A later un-throttled session should pull it.

This is a **documented** negative, naming what was checked. It is not the asserted negative that was refuted 0-3 in the earlier pass. It does not claim the code never existed.

---

## What the gate opening does and does not authorise

**Authorised now**, for `spec-evca-density` only:
- validating the genetic-algorithm implementation against targets 1 through 4 above;
- Stage 1 of the first experiment, faithful physics with pinned seeds, targeting the PPSN III configuration;
- Stage 2 instrumentation, which adds observation without touching physics.

**Not authorised**, and requiring their own artifact recovery or exactness proof first: every other specimen in the registry. GATE-1 is per-specimen, not global.

**Still closed:** GATE-2, the historical-blindness claim, which awaits the two Draghi and Wagner papers.
