<!-- DEPOSITED VERBATIM by Ananke for worker W-V; sha256(report)=4d537c8ffc524916; delimited; see REPORT.provenance.json -->
W-V (E-ANANKE-W-V, T-INS-18, successor of T-INS-16, thr-8c7342a7d513, MWO-0004)

WHAT I TESTED
- **Question.** For MAJ champion 4781b0a1, whose in-flight traffic to the readout carries the bit, and is the readout a majority over its 5 sensors or a subset rule?
- **Instrument (PLAN.md, frozen before any champion run).**
  - I identify sensor j's packets by exact emitter tagging, not by the twin-world log (a deviation from the brief, stated in PLAN s1).
  - TagWorld re-runs the engine's own _emit with the emission mask restricted to one emitter group, writing into scratch mailboxes. From that it keeps, for each sensor 0..4 plus "rest", the in-flight packets addressed to the readout (sums and counts, all slots).
  - One swap arm exchanges exactly sensor-set J's packets to the readout between mirror partners, after tick t0+o. This is a SINGLE-trial swap with a fork per (trial, offset).
- **Arms per offset (12):**
  - each single sensor s_j;
  - each complement (all but j), c_j;
  - ALL5 (all five sensors), the reference;
  - FLA (W-S flight_a: every in-flight packet to the readout).
- **Champion runs.** M=128 worlds (assays.world_seeds(0x650,128), 64 mirror pairs), trials 1-11, offsets o2, o4, …, o14. Pd is 19 (odd), so every offset covers both update-clock phases q=(t0+o) mod 2.
- **Statistics.**
  - Follow effect e_J is the fraction of eligible pair-trials whose readout follows the partner. Eligible means both partners are normal-correct and the trial is scored.
  - CIs are 99% pair-bootstrap intervals (2000 draws).
  - Primary unit is (offset, phase). A pivotality contrast D_piv tests for majority.
  - Frozen classes are DICTATOR / MAJORITY / SUBSET / DISTRIBUTED-NONMAJ / REDUNDANT-JOINT, applied only at strata where the ALL5 effect E is at least .50.
- **CI widths.** About ±.06 to ±.08 per single-sensor effect per phase stratum (n = 220-246 pair-trials), and about ±.04 pooled (n=466).

RESULTS (4781b0a1, e [99% CI])
- **o2, o4, o6, o8: no effect at all.** E = FLA = 0.00 [0,0], and every arm's raw readout S0 is bit-identical to the normal run.
  - This is not a no-op swap: 80-95% of pairs have mirror-different in-flight traffic to the readout from every sensor at every offset 0-16 (and 0% from non-sensors).
  - The readout ignores that early traffic. Its S0 is computed as IN0_1 - 3 + Kp[7], which depends only on the arrivals in the last wake window before readout.
- **o10: NOT-INFORMATIVE.** E .24 [.20,.27]. Only the distance-3 sensors act: s0 .12 [.09,.16] and s1 .13 [.10,.16]; s2-s4 are .00.
- **o12, q0 and q1: DISTRIBUTED-NONMAJ{0,1,2,3,4}.** E .82 [.77,.86].
  - q0 singles: s0 .17 [.12,.23], s1 .25 [.18,.33], s2 .23 [.17,.28], s3 .27 [.22,.33], s4 .20 [.15,.24].
  - Complements c_j .60-.70. Additivity (sum of singles / E) is 1.37.
  - D_piv .10 [.06,.14]: follow is .31 when the sensor is pivotal and .21 when it is not.
- **o14 q0: DISTRIBUTED-NONMAJ.** E 1.00 [1,1]. Singles .17-.30, complements .70-.82, D_piv .12 [.10,.14].
- **o14 q1: NOT-INFORMATIVE.** E .49 [.45,.53]; singles .09-.18.
- **Verdict (PLAN s3): DISTRIBUTED-NONMAJ.** It holds in 3 of 3 informative strata.
  - Every sensor carries a share of about 1/5 (shares .17-.27).
  - It is not a majority: D_piv is .10-.12 against 1.00 in the majority plant.
  - It is not a subset or a dictator.
- **Predictions.**
  - W1 held (informative strata exist, but only at o12-o14).
  - W2 held (not a majority).
  - W3 held exactly: ALL5 = FLA at every offset, so no non-sensor emitter matters.
- **POST HOC (labelled), how it fails to be a majority (posthoc_sign.py).**
  - Single-sensor follows come almost entirely from the "-" world receiving the partner's "+" traffic. There, follow is .43-.61 at o12 and o14q0, even when the "-" world has 0 positive votes.
  - The "+" world losing one "+" sensor rarely flips (.01-.23, more often when it has fewer "+" votes).
  - So the readout detects rectified positive payload-1 evidence reaching its last window, with a count-dependent strength. It is not a vote count.
- **POST HOC (posthoc_state.py).** The readout's own S1 never differs between mirror partners (0.000 at o0-16, M=128). Every sensor's S1 differs in 100% of pairs.

KNOWN-ANSWER CHECKS (plants_wv.py; ns 0x650, M 128; ring 144 r3, dest all, lossless, delays 7/9/11 by sensor distance, sync period 2)
- **KA-MAJ: PASS.** The majority plant PMAJ reads MAJORITY in all informative strata of o2-o6.
  - E 1.00, each single s_j .20-.24 (about 1/5), c_j .76-.80, D_piv 1.00 [1,1].
  - At o8 the distance-1 vote has already landed, and the frozen rule correctly reads DISTRIBUTED-NONMAJ{0-3} with s4 .00.
- **KA-DICT: PASS.** The dictator plant PDICT reads DICTATOR(4) (the distance-1 sensor) in all informative strata of o2-o6: s4 1.00 [1,1], c4 .00.
- **MF1: PASS.** In PDICT, swapping a non-carrying sensor (s0-s3) has no effect: e = .00, CI high .00 (at most .05 required).
- **MF2: PASS.** PDICT never reads MAJORITY.
- **MF3: PASS.** PMAJ with pivot labels permuted across pair-trials gives D_piv -.02 to .01, so the classifier reads DISTRIBUTED-NONMAJ, not MAJORITY.
- **MF4: PASS.** Both plants read NOT-INFORMATIVE at o12 (all packets delivered).
- **Instrument tests (pytest, test_wv.py):**
  - TagWorld is bit-identical to World (digest and trace).
  - The per-group tags sum exactly to the readout's Msum/Mcnt at every tick.
  - An empty-set swap equals the normal run.
  - ALL5 equals FLA in the plants.
  - My per-offset fork's FLA arm equals W-S probe.fork's flight_a.
  - The classifier reads synthetic MAJ / DICT / SUBSET / REDUNDANT / low-E tables correctly.

DISAGREEMENTS
- **Brief framing.** "N is a joint carrier of the readout's site latch S1" is not right in its site reading. The readout's S1 is identical in both mirror partners at every offset. The S1 that carries the bit is the sensors' S1: it differs in 100% of pairs, and site_all swaps it at every site. Two things carry the readout's own bit: its Kp (differs 78-98%) and payload-1 arrivals in the last window.
- **W-P.**
  - W-P says payload-1 Msum is a joint carrier "at every offset". For traffic addressed to the readout, that holds only at o10 and later: at o2-o8, swapping all readout-bound traffic changes nothing, even the raw S0.
  - W-P's early Msum role must therefore be packets addressed to the sensors (sensor-to-sensor relaying via PAY1 = MAX(IN0_1, SENSE)), which the all-sites channel swap includes.
  - Agreement: at o14, channel-follow is 1.00 on even ticks (q0) and weak on odd ticks (E .49), matching W-P's parity split.
- **W-R.** The phase effect replicates at o14 (E 1.00 in q0 vs .49 in q1). It is absent at o12 (.82 vs .82).
- **W-T.** W-T's traffic counts ("about 6 copies from sensor 0, about 25 from the other 4, 0 relays") are consistent with this census: ALL5 = FLA, non-sensor tags are always 0. But the per-sensor causal shares are about equal (sensor 0 is .13-.20, not a minority). Copy counts are not causal weight: most copies land before the readout's final window and have no effect.

PYTEST
- Command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest roles/Ananke/research/workers/W-V/test_wv.py -q -p no:cacheprovider`
- Result: 8 passed, RC=0 (logs/pytest.log).
- The first attempt had 1 failure from a test bug (an assert looked only at the last tick), logged as A4 and fixed.

LEASE
- Fabric lease lse-cfddaaf967a6 on skullport:cpu8, acquired --as Ananke at 07:02Z.
- Released at 07:13Z with --lease --token, which printed RELEASED; `python -m fabric lease status` then returned [].
- PIDs 23392, 24692, 23572, 19856 were logged at launch. Win32_Process then showed 0 W-V python processes, and the monitor task was stopped.

COMPUTE
- About 0.6 core-hours (cap 6): runs 1826 s × 1 thread = 0.51, plus tests, dev and post hoc about 0.07.
- Up to 4 processes × 1 thread, CPU only, no GPU. Wall about 17 minutes.
- No git writes, no edits outside W-V/, no pycache. Outputs 506 KB.

FILES (F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-V/)
- PLAN.md (frozen), LOG.md (A0-A12; A9 and A11 are labelled POST HOC)
- Code: wv.py (TagWorld, fork runner, arms), plants_wv.py (PMAJ, PDICT), ana.py (effects, bootstrap, pivot contrast, frozen classifier, verdict), ka.py, test_wv.py, posthoc_state.py, posthoc_sign.py, launch.sh
- out/raw_{champA,champB,pmaj,pdict}.npz, meta_*.json, summary_*.{json,txt}, summary_pmaj_perm.*, ka.json, posthoc_state.json, posthoc_sign.json
- logs/

PROPOSED FOLLOW-UPS
- The same per-sensor census on sensor-addressed traffic, to locate the early (o2-o9) carrier inside the sensor group: sensor-to-sensor relaying of payload 1 and the sensors' S1 latches.
- A swap of the readout's Kp[7] alone at o10-o14, to test whether Kp is the readout-side half of the joint carrier.
