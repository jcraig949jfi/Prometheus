# C1b under attack, and what M2 and M3 actually are

Currency: 2026-09-27. Author: Ananke[m1-7d1e2413]. Evidence: the PTE-C1b
package (cc98596dd) plus the 2026-09-27 spikes (plan 8e081dcb1; log and
outputs in SPIKES_2026-09-27_LOG.md and spikes/out/). The C1 and C1b labels
are NOT changed. This file is the reading.

## 1. Adversarial review of the C1b packet (Block A)

Read as a submitted paper, C1b had one real error, two claims that were
too weak, and one claim that was right for a slightly wrong reason.

R1 ERROR: "the signed payload sum is NOT the encoding" (C1b packet s4,
   repeated in the operator's brief). It was an INSTRUMENT CHOICE, not a
   finding. The C1b census read only payload component 0. The M2
   specimen has P = 2 and carries the code in component 1. On the same
   worlds, the sign of the in-flight component-1 sum decodes the cue at
   1.00 out of sample (p .0005), and swapping ONLY component 1 between
   mirror partners flips the answer (0.13). The census should have
   been run per component, and the carrier-swap test never existed. This
   is ledgered as my error.
R2 TOO WEAK: "M2 in flight, not a pure delay line (routing -0.06)". The
   reset_w drop was DISRUPTION, not storage: swapping w between mirror
   partners has no effect in 4/4 champions. Routing weights are
   infrastructure. In substance M2 is a pure in-flight carrier. The C1b
   label IN_FLIGHT_PLUS_JOINT stays, because it is what the frozen rule
   computes; the reading changes.
R3 TOO WEAK: "SETRULE is configuration (inferred)". It is now shown.
   Rule assignments are identical between mirror partners at every tick
   (0.0%). Every site converges onto rule 0 during trial 0 and never
   changes again. Freezing SETRULE after two trials changes nothing.
   Freezing it from the start leaves sites on random rules, cuts emissions
   4x and kills transport. SETRULE is a one-time population bootstrap.
R4 RIGHT FOR A SLIGHTLY WRONG REASON: "transport must land ON the readout
   tick; timing-locked -> deadline". The decompiled readout
   (S0 := IN0_1 + T3 in rule 0) overwrites S0 on every awake tick with
   that tick's arrivals, and the inbox accumulates only while the site
   sleeps (async p .8). So the real constraint is "arrive after the
   previous wake and by the readout". That is a deadline with a
   STALENESS floor. Latency -1 helps only because the site often sleeps
   at readout.
Alternatives considered and their status after the spikes:
  M2 timing / arrival-lag code .......... RULED OUT (lag decoder chance;
                                          +1 delay tolerated)
  M2 packet count ....................... RULED OUT (count swap no effect;
                                          count decoder chance)
  M2 destination pattern ................ RULED OUT for 3/4 (recipient
                                          roll no effect; 1/4 degraded)
  M2 routing weights .................... RULED OUT as carrier (w swap no
                                          effect)
  M2 hidden transient site state ........ RULED OUT (full site-state swap
                                          incl. inbox, Kp, E, w: no effect)
  M2 order / channel occupancy .......... not separately tested. Payload
                                          content transfer already accounts
                                          for the full flip.
  M3 SETRULE as persistent cue memory ... RULED OUT (partner r identical)
  M3 SETRULE as enabler of transport .... SUPPORTED (emissions 4x down when
                                          frozen from the start)
  M3 hidden state beyond readout r ...... RULED OUT at the site level
                                          (site swap without r: no effect);
                                          the cue is in flight (in-flight
                                          swap FLIPs)
Residual, not closed: the in-flight FLIP accuracy for M3 is 0.33, not
~0.13 as in M2. Part of the M3 answer is not transferable by an in-flight
swap at mid-delta. Candidates: dup copies arriving at ro+1, or the async
inbox. This is the smallest open M3 question (thread T-M3-2).

## 2. Current best explanation of M2 (conclusion: plausible specific carrier identified)

A TUNED TWO-STAGE ECHO ON ONE PAYLOAD COMPONENT.
- Program: every awake site emits every tick. PAY0 := SENSE; PAY1 := the
  component 0 it just received; S0 := IN0_0 + IN0_1. The sensor (which
  is also the actuator in HOLD) pushes the cue out on component 0. The
  neighbours re-emit it on component 1. The returning component-1 wave
  lands back at the actuator 0-2 ticks before the readout (single-cue
  twin profile: cue-bearing arrivals at the actuator only at lags -2..0).
- Carrier: the SIGN of the superposed in-flight value on one payload
  component. Content, not count, not timing, not destination, not
  routing. Intervention-supported: component swap FLIPS, count swap no
  effect.
- Persistence: none beyond one round trip. Accuracy peaks at the trained
  gap (6-8) and is at chance at gap >= 12 in 4/4 champions. This is a
  delay line TUNED to the task's interval, not a memory with a lifetime.
- Fresh seeds: the same code in 3/3 fresh SIGNAL champions. One evolved
  it on the other component (a relabelling symmetry), which is why a
  fixed-component census is the wrong instrument.
- Known name: a two-stage bundled-data pipeline / recirculating delay
  line (Sutherland 1989; mercury delay lines). What is new is only that
  it was EVOLVED under forced superposition, with the payload index
  acting as a hop-stage tag.

## 3. Current best explanation of M3

TRANSPORT WITH A STALENESS-BOUNDED READOUT, ON A POPULATION CONFIGURED
BY A ONE-TIME SETRULE BOOTSTRAP.
- The cue rides in flight (in-flight swap at mid-delta FLIPs to 0.33).
  With delay == delta, it arrives on the readout tick.
- SETRULE: each site's initial rule is random. The rule variants drive
  sites to rule 0 within the first trial, and after that nothing changes.
  Rule state is cue-independent at every tick. Rule 0 is the working
  relay program. Without the bootstrap most sites run junk variants:
  emissions fall 4x and transport fails.
- The "self-modifying, timing-locked" reading from C1 is dead on both
  words: the self-modification is a one-shot configuration, and the
  timing is a deadline with a staleness floor.
- Not reproduced at the fresh-search budget for 0a23398f. f6b623cd's
  descriptive fingerprint recurs.

## 4. Challenges (Block M)

C-1 To the operator's brief and to my own C1b text: "signed payload sum
    is NOT the encoding" was wrong. It is the encoding, on the other
    component.
C-2 To the word "memory" for M2: M2 does not remember. It schedules. A
    tuned echo holds a bit only for the one interval it was evolved for.
    Calling it memory invites the wrong follow-up (lifetime and capacity
    studies). The right follow-up is interval tuning and generalization.
C-3 To "self-modifying" for M3: the rule machinery is used as a
    configuration bootstrap. In PTE, SETRULE's main evolutionary use may
    be ESCAPING random initial rules, an artefact of how r is
    initialized. That would make "rule switching" a less interesting
    channel than the dial suggests (thread T-M3-1).
C-4 To the C1b mechanical labels: absolute thresholds, a fixed payload
    component and cell-id-keyed eligibility each produced a wrong or
    missing reading. The labels are honest to the prereg and weak as
    science. The carrier-swap test (FLIP / NO-EFFECT / CHANCE) is
    stronger than every C1b label and should replace kill/drop readings
    as the primary mechanism instrument (T-INS-1).

## Addendum 2026-09-27 (after W-A, W-B, W-C; these corrections supersede the text above where they differ)
- M2: CONFIRMED and PREDICTED. A strict two-hop echo (W-A); a zero-parameter
  model predicts 46/46 unseen gap curves. Corrections:
  - the specimen's routing write SHAPES the round-trip kernel; it is not
    mere disruption (s1 R2 is too weak);
  - the best gap is 7, not the trained 8 (readout parity);
  - "peak 6-8" came from even-only sweeps.
- M3: bootstrap-only CONFIRMED and sharpened. The zero-register default
  sends every SETRULE to rule 0, and a one-rule law is bit-identical
  (W-B). The "general PTE" SETRULE claim was WRONG: in 29% of 42 cells
  SETRULE is a readout-local per-tick conditional branch (never a memory
  carrier).
- "Channel CONTENT" is a reader-side verdict. Under superposition,
  presence reads as content (W-C). M2 and M3 are genuine content codes
  (twins show no firing difference); several relays are SOURCE-PRESENCE
  codes.
