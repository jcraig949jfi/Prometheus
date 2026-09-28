REPORT -- one memory certificate applied to another engine's specimen

1. WHAT I SET OUT TO TEST

The program has three instruments that each claim to certify "history is kept and causally used". They are Cosmos's public P1/P2 certificate, Ensorain's LM01 and Ananke's SI01. I asked two things. First, do they return compatible verdicts on the same specimen? Second, which committed specimens could all three be run on? Only one of the three can actually be run today, so I did the cheapest discriminating part. I applied the Cosmos P1/P2 v3 certificate, unchanged, to Ananke's evolved M2 specimen. M2 is a HOLD memory which Ananke's own tests place "in packets in flight, not in site state". I ran it under two declared system boundaries: B1 declares site state + inbox + in-flight packets, and B2 declares site state only. The question was whether the certificate agrees with Ananke's own tests, and whether the verdict is set by the boundary the adapter author declares.

2. WHAT I DID

Code and data were exported with git archive into /home/jcraig/artemis-selftest/work/R-10/src. Nothing was run against the clone.
- Cosmos certificate: prometheus/cosmos/c3/{certify,system,task,probe,calib}.py @940b486f2, unchanged. Rule v3: 49 permutations, p <= 0.02, P2 = 3 bootstrap SE, 2000 training and 3000 test episodes.
- Ananke engine: prometheus/ananke/*.py @cc98596dd. This is identical to main except for lens.py.
- The M2 specimen is cell 4ab2ba014aac967e. Its champion genome, physics and environment come from roles/Ananke/pte/c1_rows/cells.jsonl.gz @b91f522ae.
- The physics is a ring of 144 sites with synchronous wake every 2 ticks, and the in-flight mailbox ring has length 8. The environment is HOLD with cue_len 2 and gap 8.
- New code, all in /home/jcraig/artemis-selftest/work/R-10:
  - adapter.py: a Cosmos System around the Ananke engine.
  - run_cert.py: the certification driver.
  - ka_check.py and ka_adapter.py: known-answer checks.

How the adapter maps a Cosmos episode (V=2, k=8) onto one HOLD trial run from a fresh world:
- The cue takes 2 engine ticks at +/-256 on the actuator site.
- Each distractor takes 1 tick at +/-64.
- The query takes 1 silent tick, which is the HOLD readout tick.
- The readout features are a one-hot of sign(S0) at the actuator, which is Ananke's own readout.
- The engine's counter-based RNG gets a fresh world seed per step from the harness's noise(), so the two rows of a P2 pair share every random draw.
- The C3 harness swaps every array in the state dict at t=k. Carriers outside the declared boundary are therefore kept outside the dict: they are neither swapped nor probed.
- full_state is the declared arrays, with sites re-indexed relative to the actuator (the ring is translation-symmetric). Columns that are constant within a batch are dropped, which loses nothing for a linear probe.
- "phase" is the engine tick parity at which the episode starts. Phase 0 reproduces trial 0 of Ananke's episodes.

Runs:
- ka_check.py: Ananke's own evaluate() on the 64 held worlds for the normal, flush_inflight, flush_inflight_late, reset_S, reset_all_nonpacket and zero_comm arms.
- ka_adapter.py: the same arms re-created through the adapter (flush after step 5 = mid-delay, flush after step 8 = the tick before readout, zero_comm), at phases 0 and 1, 2000 episodes each.
- run_cert.py PV|NZ seeds 6-10: the Cosmos planted sanity systems on the same V=2, k=8 task.
- run_cert.py B1 seeds 6,7,8 (phase 0) and B2 seeds 6-10 (phase 0).
- run_cert.py B2 seeds 6,7 at phase 1.
- Outputs are in out/*.json and out/log_*.txt.

3. RESULT

Known answers:
- Ananke's own run reproduces the committed held accuracy exactly: 0.8828. flush_inflight gives 0.497, zero_comm 0.500, reset_S 0.883 (unchanged), reset_all_nonpacket 0.863, and flush_inflight_late 0.845.
- Accuracy per trial alternates with the tick parity at which the trial starts: about 0.72-0.84 on even starts and 0.92-1.0 on odd starts. The trial period is 13 ticks and sites wake every 2 ticks.
- Through the adapter:
  - Phase 0: normal J = 0.736 (matches trial 0 = 0.72), flush mid-delay 0.50, flush just before readout 0.68, zero_comm 0.50.
  - Phase 1: normal 0.959, flush mid-delay 0.51, flush just before readout 0.959 (no effect), zero_comm 0.50.
- The adapter therefore reproduces Ananke's known answers.

Certificate, unchanged v3 rule:

| System | Seeds | Class | P1 D (bits) | P1 p | P2 effect (+/- SE) | Notes |
|---|---|---|---|---|---|---|
| M2, B1, phase 0 | 6, 7, 8 | FUNCTIONAL 3/3 | 0.80-0.81 | 0.02 | 0.45-0.47 +/- 0.009 | J 0.73 -> 0.27 |
| M2, B2, phase 0 | 6-10 | PASSIVE 5/5 | 0.83-0.85 | 0.02 | exactly 0.0000 | J_ablated = J_intact |
| M2, B2, phase 1 | 6, 7 | FUNCTIONAL 2/2 | 0.98 | 0.02 | 0.92 +/- 0.005 | |
| PV | 6-10 | PASSIVE 5/5 | | | | sanity as expected |
| NZ | 6-10 | 3 FUNCTIONAL, 1 INDETERMINATE (p=0.04), 1 INCOHERENT (p=0.30) | | | about 0.04 in all 5 | P1 gets weak at k=8 |

Plain conclusion:
- On this specimen the Cosmos certificate agrees with Ananke's tests once the boundary is declared. B1 is FUNCTIONAL and B2 is PASSIVE at phase 0, which is the pre-stated "agree" outcome. No INCOHERENT result occurred on M2: the linear P1 probe decodes the cue from the declared state.
- Two qualifications change how that should be read.
  - (a) The verdict is set not only by the declared boundary but also by the moment of the swap relative to the engine's wake cycle. With B2 fixed, starting the episode one tick later flips the verdict from PASSIVE to FUNCTIONAL. At phase 1 the cue has been written back into site state by the tick before readout, which is consistent with Ananke's own flush_inflight_late being harmless there. So "the memory is in packets, not site state" is true at mid-delay but not at every tick. The certificate's fixed swap time t=k samples only one tick.
  - (b) P1 held under both boundaries, including B2 where the cue's carrier is excluded. P1 probes at t=k+1, after the readout tick, so the state that holds the system's answer already contains the cue. On this task P1 does not locate where the memory is carried; only P2 discriminates.
- The second part of the question (which committed specimens all three instruments could be applied to) has the answer "none today". LM01 is frozen but not launched, and its world is tensor completion with no cue-delay-query episode. SI01 has a directive but no prereg and no code. Only the Cosmos certificate exists as runnable code, so no three-way comparison is possible.

4. DID IT RESOLVE THE QUESTION

Partly.
- The cheapest discriminator is resolved for the Cosmos-on-Ananke pair. The dependence on the boundary was confirmed, and a second hidden degree of freedom was found (the wake phase at the swap time).
- The three-way compatibility question cannot be resolved with committed inputs: two of the three instruments have no runnable implementation.
- B1 was run on 3 of the 5 planned seeds because of the CPU budget. All 3 agree, with P2 z around 50, so the missing seeds are very unlikely to change the class.

5. CONSEQUENCES

- Positive result / reproduction: the adapter reproduces Ananke's known answers, and the certificate agrees with them under a declared boundary. The adapter (/home/jcraig/artemis-selftest/work/R-10/adapter.py) is a reusable tool for putting Ananke specimens under the Cosmos certificate.
- Instrument caveat (for Cosmos, and for anyone proposing this as the common ruler):
  - A verdict must name the boundary AND the swap tick, since the carrier can move between packets and site state within a trial.
  - A single fixed swap at t=k is not enough for engines with periodic update. Sweeping the swap over the delay would be the natural amendment.
  - P1 at t=k+1 cannot localize memory, because any system that answers correctly meets it trivially.
- Calibration note (for Cosmos): the v3 gate was passed at V=4, k=6. At the V=2, k=8 shape needed here, the weak planted system NZ is not 5/5 FUNCTIONAL (3/5; one INCOHERENT from a P1 miss). The gate's guarantees do not carry over to other task shapes without being re-run there.
- For Ananke: the statement "memory in packets in flight, not site state" should be qualified. It holds at mid-delay, but at the tick before readout on odd-phase trials the cue is already in site state.
- For the thread steward: LM01 and SI01 need runnable code and a cue-query episode before any cross-instrument comparison. Adding an E class to Cosmos was not attempted.
- Governance: I ran this as a neutral worker using only the public certificate code and the committed specimen row. I did not contact Cosmos or Ananke (the channel is frozen), so they should be told.

6. COST

- About 2 hours of my own time.
- About 47 CPU-minutes (roughly 2,800 CPU-seconds), single-threaded, at most one heavy process at a time, peak about 1.6 GB RSS.
- Not done:
  - B1 seeds 9 and 10.
  - B1 at phase 1.
  - A packets-only boundary (B3; implemented in the adapter but not run).
  - A sweep of the swap tick.
  - Any LM01 or SI01 application, since there is nothing runnable.
