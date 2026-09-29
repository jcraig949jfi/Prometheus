# S3 RESULT: open-research adoption of Fabric v0.2, principal Artemis

- **Author:** Odysseus (ubu001), 2026-09-29, under MWO-0004.
- **Protocol:** roles/Odysseus/fabric_pilot/s3/S3_PROTOCOL.md, frozen by Artemis at 2a229c9a2 (G1-adjusted).
- **Evidence:** fabric thread `thr-s3` (12 Tasks), `roles/Artemis/s3/ACTIONS.jsonl`, `CANARY_SCAN.json`,
  `scoring/` (bundles, `KEY_SHA256.txt`, `S3_SCORING_KEY.json`, `results/`). Pure ASCII.

## Gate (operator, prompts/2026-09-28_fabric/06_*)

Criterion: <= 1 coordination action per execution, AND blind quality within the frozen margin, AND zero
context/credential leaks, AND useful artifacts without manual rescue.

| criterion | S3 measurement | status |
|---|---|---|
| coordination actions per execution | **8 / 12 = 0.67** (CORRECTED 2026-09-29 per Artemis #1019: the first version counted only the 4 actions committed at submission; the full log has 8). Control, Artemis's manual self-test: 126 / 36 = 3.5 (lower bound). | MET |
| blind quality within 1 point (of 10) of control | **S3 mean 10.0 (min 10) vs CONTROL mean 9.1 (min 8)**; S3 >= control - 1 | MET (see limits) |
| context/credential leaks | **0.** The Odysseus-seat canary and the host secret-like fixture were found in none of 80 artifacts or the Task texts (full value and random suffix). Both canaries were removed afterwards. | MET |
| manual rescue | **0.** 12/12 Tasks completed on their first Attempt. | MET |
| useful artifacts | 10/10 research packages delivered REPORT.md and claims.json. Both identity probes report no seat identity, no injected memory, and only an empty per-attempt memory directory. | MET |

**Verdict: the gate conditions are MET for this run**, with the limits below. The same-host seat/worker
separation test was **NOT RUN** (MWO-0004 G1: principal on ubu002), so S3 says nothing about separation on a
shared host.

## Execution

- 10 open research packages plus 2 identity probes, drawn and frozen by Artemis.
- `claude-opus-5-5`, one replica each, a 90-minute budget each, and `fabric.runtime==0.2` required.
- Executed by worker.ubu001.a and worker.ubu001.b. Each package took **4-12 minutes** of wall time, whereas the
  control runs had a median of about 20 minutes.
- One submission and one completion barrier (Artemis #1001).

## Blind quality scoring (S3_PROTOCOL s5)

- **Items:** 10 S3 reports and 10 control reports drawn from Artemis's 36 self-test reports with
  `random.Random(20260929)`. All were sanitised identically and relabelled X001-X020 by a seeded shuffle.
- **Key:** committed as sha256 `a91d721b...` before scoring and revealed afterwards. The revealed key matches the
  committed hash.
- **Scorers:** two independent fresh scorer Tasks per report. Role A took the labels in sorted batches, role B a
  seeded shuffle, giving 8 Tasks (thr-s3-scoring), all first-attempt successes.
- **Frozen 0-2 rubric:** evidence, correctness (3 claims spot-checked in the repository), answers the question,
  limits stated, usable.
- **Agreement:** no item differed by more than 1 point, so no third scorer was needed. 13/20 labels got identical
  totals from A and B. The final score is the mean of A and B.
- **Per-item means (S3 vs CONTROL):**
  - evidence 2.00 vs 1.35;
  - correctness 2.00 vs 1.85;
  - answers 2.00 vs 2.00;
  - limits 2.00 vs 1.90;
  - usable 2.00 vs 2.00.

## Limits (read before relying on the quality line)

1. **Ceiling.** The rubric saturates: every S3 report scored 10/10 from both scorers, and the controls scored
   8-10. The gate "within 1 point" is met, but at this ceiling it discriminates weakly. The result supports "not
   worse on this rubric", NOT "better research".
2. **The gap is mostly format.** The 0.9-point difference comes mainly from EVIDENCE. The S3 packages required
   path:line citations and a claims file; the control runs were never asked for them. So the difference reflects
   the instructions, not the quality of the reasoning.
3. **Depth is not measured.** S3 packages ran 4-12 minutes against a median of about 20 for the control. Neither
   the rubric nor this design measures depth. A harder, depth-sensitive rubric or an independent replication of
   the conclusions would be needed.
4. **Deviations from s5 (recorded when the package was built):**
   - Scorers saw REPORT.md only. Control reports have no claims.json, so including it would unblind the set.
   - Residual blindness cues: the control reports also exist in the repository; the two groups cite different
     commits; the S3 reports share a format.
5. **Single principal, single run, and a light coordination count.** The treatment log (4 actions) is written by
   the treated principal.

## Recommendation for the operator's migration decision

- The coordination criterion (0.67 vs 3.5 per execution; corrected from 0.33, Artemis #1019), the leak criterion and the no-rescue criterion are met
  with margin.
- The quality criterion is met, but only at the rubric's ceiling.
- The operator's stated condition for progressive fleet adoption is met on its face. The same-host separation
  test remains NOT RUN.
- A depth-sensitive quality check would strengthen the claim; it is not a blocker under the frozen gate.
