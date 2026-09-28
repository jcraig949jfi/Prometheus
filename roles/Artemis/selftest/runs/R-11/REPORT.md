# Report: engine-era census of positive controls on silence-bearing gates

## 1. WHAT I SET OUT TO TEST

Many gates, null tests and detectors in the current engines turn a silent outcome ("not detected", NULL, "clean", KILLED-for-absence) into a claim about the world. I set out to count how many of them have actually been shown to fire on a planted positive, and whether that positive was built on the same substrate the gate now judges. For those that do have a positive, I also counted what kind it is: a single plant the analyst knew about, a detection curve over effect size, or a blind injection. The census follows the three-property definitions of the August 2026 verdict-point adequacy census (POS / NEG / FLOOR), so the missing-positive rate can be compared with that census's 54.5%. The decision rule is: under 25% missing with substrate mismatch rare means the August lesson has been absorbed; 50% or more means nothing has changed.

## 2. WHAT I DID

Data: only committed repository content, read with `git show` from a read-only clone (origin/main at 6ff2b2f8a, plus origin/aether/research-block-2026-09-27 and the cosmos/aphrodite/bellerophon/archaeon branches where relevant). I ran no code from the repository and did no computation beyond tabulation.

Frame: one row per verdict point that can return a silence-type outcome, across the engines named in the briefing:
- Aether AETH-03 (15 rows)
- Campaign 6 observatory detectors 1-11 (11)
- MHC v0 and its production ledger (12)
- Ananke C1b (11)
- Cosmos C3 and CWE (10)
- Ensorain LM01 (9)
- Nestor P-11 and the C9/c9x verdicts that use it (7, plus 2 historical context rows excluded)
- Bellerophon/BEE SR criterion, grounding and coupling (8)
- Archaeon causal lens, codeprov, ENVGATE-01/02 and attribution v0 (6)
- Ares cycle 2 (7)
- Aphrodite engine S1-S4 (20, plus 2 pre-engine swarm-toy rows excluded)

Total: 120 rows read, 116 in scope. Of those, 94 are verdict points whose silence is currently read as absence. The other 22 report UNRESOLVED, UNABLE, "blind", or qualification-only outcomes.

Procedure:
- Codebook: `census/CODEBOOK.txt`. POS is one of none / planned / single / curve / blind. Each row also records fired (path@sha of the firing record), pos_rate, same_substrate (y / n / partial), NEG, FLOOR and notes.
- Four parallel hand-readers (sub-agents under my direction) read the preregistrations, reducers, results, reviews and correction files for their engine groups. Each row cites its evidence as path@sha.
- Raw rows: `census/rows_{A,B,C,D}.tsv`, merged into `census/all.tsv`.
- My derived coding (`census/code.py`, output `census/coded.tsv`) adds four columns:
  - absence_read: is the silence read as absence?
  - pos_outcome: fired, fired_partial, failed_on_use_substrate, none, not_run or not_shown.
  - harmonia_POS: was the gate ever shown to fire anywhere? This is the August definition.
  - fired_same_substrate.
- I reclassified one row by hand. The Aether cause probe's only transport positive (fwd) looks like the laws it clears, so I counted it as a failed positive.
- Second reader: I pre-declared 10 rows (`census/second_reader_sample.txt`) and re-read their sources myself: AETH03 E-P1, C6 detector 2, MHC echo base, C1b clause C, Cosmos C3 P1, LM01 E6, the X-PAIR-NORECOMB null, the BEE SR criterion, Ares NEW_CARRIER and ENVGATE-01.

## 3. RESULT

Rate columns: "Absence-read" is the 94 verdict points whose silence is currently read as absence; "All in scope" is all 116 rows.

| Measure | Absence-read (n=94) | All in scope (n=116) |
|---|---|---|
| Never shown to fire (August POS definition) | 37 (39.4%) | 49 (42.2%) |
| Same, also counting positives that failed on the substrate in use | 42 (44.7%) | - |
| Missing NEG (no should-fail or fooled-by case shown) | 48 (51.1%) | 64 (55.2%) |
| Missing FLOOR (no chance or null rate) | 58 (61.7%) | 71 (61.2%) |
| Failing at least one property | 74 (78.7%) | 91 (78.4%) |
| Fired on a planted positive on the SAME substrate | 12 (12.8%) | 13 (11.2%) |
| Same, excluding 2 whose "positive" arm is identical to the treatment (Aphrodite S4 and S4/S7) | 10 (10.6%) | - |
| Fired on a partly matching substrate | 28 more | 30 more |
| Not shown to fire on a same or partly matching substrate | 53 (56.4%) | - |

How the positives were calibrated, among the 57 absence-read gates that have any demonstrated positive:

| Kind of positive | Gates |
|---|---|
| Single analyst-known plant, or a few fixed plants | 56 |
| Graded detection curve | 1 |
| Blind injection | 0 |

Across all 116 rows there are only 4 curves (three MHC power curves and the Ensorain selectivity instrument) and no blind injection. Substrate of those 57 positives: 13 same, 28 partial, 16 different.

**Positives that exist but failed on the substrate the gate judges (11 rows):**
- Aether: E-P1. fwd, which forwards bytes by construction, preserves content to generation 5 or later in 3.1% of origins (bar 5%), but 21/21 on the clean relay. The cause probe that clears rcv, rcv_add and rcv_str is also counted here.
- Campaign 6 detectors 1 and 2 at their frozen population thresholds: 3/12 and 0/12. The 744/744 figure for detector 2 is at the single-edit threshold, and all these positives are on v0 genomes.
- MHC: memoryful base (admit 0-0.05 at every effect size, the same as the null), solo-sealed holdout 0/12, trend test 2/12, structure lens 1/15.
- Ananke C1b: the echo, sham and delay-line plants at specimen physics. By C1b's own rule, the clauses these plants guard went _UNRESOLVED.

**Per engine** (absence-read rows; missing POS / fired on same substrate):

| Engine | Missing POS | Fired on same substrate |
|---|---|---|
| Aphrodite | 13/20 | 4 |
| Cosmos | 6/10 | 0 |
| Aether | 6/14 | 2 |
| Nestor | 3/7 | 1 |
| Ares | 2/6 | 1 |
| Bellerophon | 2/6 | 1 |
| MHC/SFE | 2/5 | 2 |
| Archaeon | 2/11 | 1 |
| Ananke | 1/9 | 0 |
| Ensorain | 0/6 | 0 |

Without Aphrodite, missing POS is 24/74 (32.4%).

**Second reader.** My reading agreed on 47 of 50 axis judgements (94%). I agreed on POS for all 10 sampled rows, though for C1b clause C only after finding the dev fixture record; the prereg alone did not show it. The disagreements were NEG for Ares NEW_CARRIER, FLOOR for LM01 E6, and a substrate code on a POS=none row. Limitation: I had already seen the first readers' labels, so this is not a blind re-read.

**Plain conclusion.** In the engines, the share of absence-bearing gates never shown to fire is about 39-45%. The August figure was 54.5%, and that was a keyword-proxy lower bound. So the engines have improved, but they sit in the middle band of the decision rule: neither under 25% nor at or above 50%. The stronger finding is on the other two axes:
- Only about 1 in 10 absence-reading gates has fired on an independent planted positive on the substrate it now judges.
- Substrate mismatch is the norm, not rare: 44 of 57 positives are partial or different.
- Essentially every positive that exists is a single plant known to the analyst: 1 curve and 0 blind among absence-reading gates.

Where the engines have absorbed the lesson (Ananke C1b, Ensorain LM01, Bellerophon coupling, MHC), the good mechanism is the rule that an absence reading counts only where its plant fired, and otherwise reads UNRESOLVED. Where it has not, the gates are mostly leakage, metering, conformance and "no counterexample" checks (Aphrodite S1-S4, Cosmos CWE/C3 audit, MHC leak and storm), plus exploratory CLEAN_NULLs (Nestor, BEE G4/G5).

## 4. DID IT RESOLVE THE QUESTION

**Partly.**

Resolved:
- The counts asked for: missing positive, single versus curve versus blind, and same-substrate firing, for the engines listed.
- Answer: missing POS is about 40%, blind positives 0, curves 1, and same-substrate firing about 11-13%.

Not fully resolved:
- The frame follows the briefing's engine list, so it is still a chosen sample. Aphrodite contributes 20 of 94 rows and pulls the rate up.
- Row splitting is a judgement call, and a different granularity would move the rates by a few points.
- The second-reader check was not blind.
- The comparison with August is only approximate, for two reasons.
  - August used a keyword proxy with 72% agreement against hand labels, and it scoped a different set of files.
  - Here most rows were read by agent readers against a written codebook, with me as the second reader.
- The rates straddle the decision thresholds depending on the denominator (39-45%). So the verdict is "middle band", not a clean absorbed or unchanged.

## 5. CONSEQUENCES

**False or stale premises in the briefing:**
- The August 54.5% was a keyword proxy, not a hand census.
- Campaign 6 detector 2's "744/744" holds only at the single-edit threshold. At its frozen population threshold it fires 0/12 on planted jumps, and detector 1 fires 3/12. Both "admitted" rulers are therefore effectively blind at the thresholds they would use.
- The "null ladder" belongs to Ensorain WTP03, not LM01.
- Cosmos C3's planted 6-system gate is a set of analyst-built plants, not blind. The foreign holdout D has never been certified and was later declared exposed.

**Harness and instrument defects surfaced by the reading** (owning seats should check):
- Aphrodite `run_s3s4.py` hard-codes S4 conditions 4 and 8 to True (L391, L420). S4 condition 7 was decided with an empty class-certificate list. The S4 "positive control" arm is content-identical to the treatment.
- Nestor: X-PAIR-NORECOMB retired a line as CLEAN_NULL with no positive arm. It ran at tier M, while P-11 had only ever fired at tier L. P-11 zeros are also cell-conditional: the same founder genome scores 0.955 in some cells and 0.0 in ten others.
- The BEE SR criterion is location-based (pc < L), so it cannot see replication from self-copied window code. The recount is still open.
- Cosmos CWE G7 was fooled by pooling opposite-signed family residuals.
- The Aether content-transport metric failed its own positive control in the soup, yet it still clears three laws of content transport.

**Recommendation:**
- Make POS a machine-checked field at freeze time with two parts: the firing record's path@sha, and a same-substrate yes/no.
- Adopt ecology-wide the rule that an absence counts only where its plant fired, else UNRESOLVED. Ananke and Ensorain already have it.
- No gate has a blind positive. A third-seat plant-and-seal service would be new.
- Three silence-bearing gates with the weakest positives, for a dose-curve follow-up by their owning seats:
  1. the Aether content-transport signature, in the rich soup;
  2. Campaign 6 detectors 1-2, at the frozen thresholds on graph populations;
  3. P-11 as used in the CLEAN_NULL verdicts, with an in-regime implant dose series.

**Who should know:** the meter-integrity seat (Harmonia), Nemesis (census), and the owning seats named above (Aphrodite, Nestor, Bellerophon, Cosmos, Aether, Archaeon).

Overall this is a partial reproduction of the known result (the missing-positive defect is still common), with a sharper new finding: substrate mismatch and the single-plant form dominate.

## 6. COST

- Time: about 1.25 hours wall-clock of my own work, plus four parallel reading agents of about 6-9 minutes each.
- CPU: well under 1 CPU-minute of computation (text tabulation only). No repository code was run, and no database was queried.
- Not done:
  - a fully blind second read;
  - a census of the Nestor non-pair CLEAN_NULLs and of the WTP03 null ladder;
  - the dose-curve injections themselves, which are seat work and outside this budget.
