<!-- DEPOSITED VERBATIM by Ananke for worker W-J; sha256(report)=463daf2bd1ca706c; delimited; see REPORT.provenance.json -->
# W-J REPORT: do receiver semantics shape which mechanisms emerge?

Worker W-J, namespace 0x5EF. Directory: roles/Ananke/research/workers/W-J/ (PLAN.md, LOG.md A0-A21, NOTES.md, QUEUE.md, arb.py, test_arb.py, e1-e6b scripts, out/).

I wrote PLAN.md before any run and appended a frozen addendum before each later experiment.

Context contamination: I read W-C's NOTES.md and X4_RESULT.md before writing PLAN, because the brief listed them as raw evidence. I read the principal's files only after PLAN.

I used two GPU leases, both released (comms 777/781 and 782/783). Aether was read only, via `git show origin/main`, and was never run, modified or contacted.

## Answer in one paragraph
Yes, but only conditionally, and much less than the cross-engine framing implies. The receiver operator decides which functions a single tick can compute (table below; the table's one-shot numbers were checked with designed plants). Whether evolution uses that difference depends on the task's aggregation gain: the value of combining several simultaneous arrivals over one sample.
- At the PTE physics where the matched C1 block lives (loss 0.3, asynchronous wake), the gain is about 0.02. Across 32 fresh searches, 29 champions converged on sparse "only the sensor fires" presence codes. Their accuracy is identical to 3 decimals under SUM, SAT and a hash-arbitration variant (ARB). These codes sit in the operators' null space: at most about one arrival per decision.
- In a lossless variant the gain is about 0.13. There, one SUM champion (0.801) evolved a count-threshold majority code: only positive-cue sensors fire, and the actuator is positive iff at least 3 packets of 52 superpose. That code scores exactly 0.500 under saturation, erasure (ALOHA) and arbitration.
- The operator matters only through the reader's invariances. A sign reader cannot tell SUM from SAT; a count reader can.

## Formal statement (details in NOTES s2)
Setting: X is the multiset of arrivals at one receiver, channel and tick; k is its size; K is the total over all channels. Senders are anonymous and homogeneous.
- **SUM (PTE, collision none).** The receiver sees clamp(Σx) and k. One tick computes exactly the nomographic family ψ(Σφ(x_i), k), with φ chosen by the sender program and ψ by the receiver program. Cheap: count, sum, mean, majority, threshold votes. Impossible: sender identity or order. Exact max, min or OR of multi-bit values are impossible except over small ranges, because of the clamp.
- **SAT (PTE saturate).** Divisive normalisation by K: above the cap the receiver sees cap × mean. Cheap: sign and anything scale-free. Impossible above the cap: count and total.
- **ALOHA (PTE aloha).** A collision channel with erasure and no collision detection: silence and collision both read as CNT = 0. Aggregating more than cap senders requires spreading them over time (schedules, protocol sequences).
- **ARB-replace (Aether).** One content-blind, timing-blind hash-lottery sample per contest; no count. Majority needs receiver memory (sequential sampling). Without that memory the medium is a voter or copying process. Such a process does not compute majority (fixation probability equals the initial fraction). The only differences that persist are genealogical ("whose byte is here"), which matches Aether's measured "who fired" and "different writer won".
- **Message-writable code.** In Aether the sender picks the field, so a message is an operator on the receiver (overwrite destruction). PTE code changes are receiver-gated: SETRULE or WIMM take IN or CNT operands only if the receiver's own code chooses them. The E6 champion does exactly this (r := CNT0 mod 4). The known regime for sender-addressed writes is Core War and coreworld; Tierra added exclusive write privileges (a "membrane") to stop it.

One-shot table:

| function | SUM | SAT | ALOHA | ARB-replace |
|:--|:-:|:-:|:-:|:-:|
| presence | C | C | C if k ≤ cap | C |
| count | C | C only up to cap | C only up to cap | X (T by sampling) |
| sum or vote | C | mean only | C only up to cap | T with memory; a voter copy cannot |
| identity | X | X | X | X |

C = cheap in one tick, T = only across ticks, X = impossible from the delivered observation.

## What I tested and what happened (all verdicts against frozen rules)
- **E1 (C1 evolved cells by operator, descriptive).** MAJ "communicating competent" share: SUM 0.041, SAT 0.217, ALOHA 0.000.
  - P1 fails on its threshold (SUM − ALOHA gap 0.041 &lt; 0.05). P2 and P3 hold weakly.
  - The SAT lead sits entirely in targeted waves. The randomized wave A has zero competent communicators under any operator.
- **E3 (18 matched C1 champions, each evaluated under all 4 operators).**
  - P1 fails: SAT-evolved champions do not lose under SUM (−0.007).
  - P2 fails: not every class drops under ARB (SUM −0.021, SAT −0.053).
  - P3 holds: ALOHA champions are unchanged under SUM.
  - P4 NOT_VERIFIED: the inbox swap was arm-identical in every competent champion.
  - ALOHA destroys the dense content codes (0.717 → 0.539).
- **E4 (randomized census, generation 0).** No SAT or ALOHA head start; both predictions fail. The data sit at a floor, so this only rules out a large effect.
- **E2 (32 fresh searches, 4 operators × MAJ and RELAY, f6b6 physics).**
  - Fail: P1 (narrowly, 0.051), P2, P4, P6 (0 of 4 arms show an own-operator advantage above 0.03) and P8 (SAT champions are not dense).
  - P3 is vacuous and P9 is not testable.
  - P5 holds only trivially (+0.014). P7 holds only mechanically (both drops are about 0).
- **E5/E5b (designed aggregation plant).**
  - Lossy physics: SUM 0.695 = SAT; ARB 0.674; ALOHA 0.562.
  - Lossless physics: SUM 0.823 = SAT; ARB 0.727; ALOHA 0.500. Theory predicts 0.837 / 0.700 / erased.
  - The gap threshold of ≥ 0.10 fails narrowly (0.096); all other E5b clauses hold.
- **E6 (lossless physics, 12 searches).**
  - Fail: P1 (median SUM − ARB = 0.027) and P4.
  - Hold: P2 (a SUM champion at 0.801) and P3 (that champion is 0.500 under every other operator).
  - Own-operator advantage is SUM +0.104, ALOHA +0.030, ARB +0.017, against ≤ 0.014 in E2.
  - An ALOHA champion falls below chance without erasure (0.614 → 0.467).
- **E6b (the decompiled vote logic as a hand-built plant).** SUM 0.878 [0.833, 0.917]; SAT, ALOHA and ARB exactly 0.500. The ±0.03 band around 0.837 fails on the point estimate, although the CI contains 0.837.

## Observability artefacts (NOTES s4)
- **O1.** A PTE payload-vs-count swap names the reader's register, not the physical code.
- **O2.** Aether's XOR content signature labels additive transport as "altered". Under `add` or `rcv_add`, a flip of ±2^b carries into higher bits, so "content does not travel" cannot be measured for combining commits.
- **O3.** Aether measures propagation; PTE measures use by a selected reader. These are different quantities.
- **O4.** Aether has no selection and no task, so "which mechanisms emerge" across the two engines confounds operator × selection × task × instrument. Only varying the operator inside one engine is clean; that is what E2 and E6 do.
- **O5.** C1's operator dial was not randomised in the evolved waves.
- **O6.** A one-bit origin (Aether) and a whole-trial cue negation (PTE) differ by orders of magnitude in perturbation size.

## DISAGREEMENTS
- **D1.** The PTE engine card says "messages can never rewrite the program". That is false as stated. SETRULE and WIMM accept IN and CNT operands, and the E6 champion selects its rule from an arrival count. The true contrast is sender-addressed versus receiver-gated code modification.
- **D2.** The synthesis and engine card say "PTE ADDS arrivals". The operator is a dial (none / aloha / saturate). The C1 competent communicators concentrate under saturation (normalisation), and ALOHA is a native collision channel. PTE lacks only content-blind winner selection and sender-addressed code writes.
- **D3.** The synthesis says "the real axis is the receiver operator". This is too strong on the PTE evidence. Across 44 fresh champions the operator is behaviourally irrelevant except where the physics makes aggregation pay. Receiver operator × aggregation gain is the axis, and it is filtered by the reader's invariances.
- **D4.** The Aether-side reading "content differences are overwritten" is right for replacement, but it is partly an instrument statement (O2) for the combining laws (`add`, `rcv_add`).

## Surprises
- SAT-evolved dense codes do not need SAT at evaluation, because SAT is a positive rescaling.
- The SAT ↔ dense-code association in C1 did not replicate in fresh searches (0 of 4).
- The only dense MAJ champion in E2 arose under ARB.
- One ALOHA champion's code requires collisions to be erased.
- The first pure superposition-count majority code seen in PTE: presence vote plus threshold 3 of 5.

## Discriminating designs (runnable here) and Aether proposals (for its owner; nothing run)
- **PTE, done:** E2, E6 and E6b. arb.py is a known-answer-tested ARB receiver (CUDA graph == eager).
- **PTE, next:** E6 at ≥ 8 seeds per arm, adding SAT and a RELAY control, plus a sweep of loss from 0 to 0.3 (~25 min GPU). Prediction: own-operator advantage rises monotonically with plant-measured aggregation gain.
- **A-J1 `sup`.** Commit old + Σ of all simultaneous proposals, compared with `add` (old + winner). This isolates the operator. Predictions: the "different writer won" share falls to about 0; preserved content rises (scored with A-J2).
- **A-J2.** Additive (mod 256) content signature, with an `add` relay-chain fixture; re-score `rcv_add` with it.
- **A-J3.** Receiver-gated code writes (a membrane). Predictions: less overwrite destruction, less reach.
- **A-J4.** Voter-genealogy test: the recorded winner graph should predict ≥ 95% of payload differences in v1 with perturbation off.

## Predictions that could fail (open)
1. Own-operator advantage scales with aggregation gain across a loss sweep.
2. Under SUM, count-threshold codes appear only when single-sample accuracy is well below k-vote accuracy.
3. `sup` removes Aether's writer-identity differences.
4. The additive signature raises `rcv_add`'s preserved-content share.
5. The receiver-gated membrane cuts overwrite destruction.
6. v1 payload differences follow the winner genealogy (≥ 95%).

## Proposed Threads
- **T-WJ-1:** aggregation-gain sweep (above).
- **T-WJ-2:** reader-invariance classes as a lens function: evaluate any champion under all 4 operators (a 4-number fingerprint).
- **T-WJ-3:** Aether A-J1 to A-J4.
- **T-WJ-4:** correct the engine card's "messages never rewrite the program" to "receiver-gated".

## Literature (full list and URLs in NOTES s5)
Massey &amp; Mathys 1985 (collision channel); Goldenbaum, Boche &amp; Stanczak (nomographic over-the-air computation); Nazer &amp; Gastpar 2011 (compute-and-forward); Zhang, Liew &amp; Lam 2006 (physical-layer network coding); Carandini &amp; Heeger 2012 (normalisation); Maass 2000 (winner-take-all); Chaney &amp; Molnar 1973 (arbiters); Shapiro et al. 2011 (CRDTs / last-writer-wins); Aspnes &amp; Ruppert (population protocols); Holley &amp; Liggett (voter model); Land &amp; Belew 1995 (density classification); Cornejo &amp; Kuhn 2010 (beeps); Rasmussen et al. 1990 (coreworld); Ray 1991 (Tierra write privileges, quote verified); Theraulaz &amp; Bonabeau 1999 (stigmergy).
