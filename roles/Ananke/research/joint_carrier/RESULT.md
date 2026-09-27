# Joint carrier 4781b0a1: RESULT (J1-J5)

Plan: PLAN.md (938d1aa6f) + addendum J5 (committed before J5 ran).
Outputs: out_j_probe.json, out_j5.json. CPU, 2 threads.

## Verdict under the preset rules: UNRESOLVED
None of H-RED / H-SYN / H-HAND / H-ADD met its preset rule:
- S erasure kills fully (not the partial H-ADD needs);
- the flush drop at mid is partial (0.59, hi 0.62 > 0.60, not the
  H-SYN kill);
- both carriers are necessary over an 8-tick overlap (H-HAND needs
  <= 6);
- the J5a actuator prediction failed.
H-ART is EXCLUDED: a joint swap before the cue (t0-1) has no effect (0.78).

## What the data show (descriptive; this reading is new after J5)
SOURCE-LATCHED REGENERATION WITH A DEADLINE HANDOFF.
- Where the necessary site state is: at the 5 SENSOR sites. Erasing S at
  the sensors at mid kills (0.50). Erasing it at the actuator only or at
  all other sites has no effect (0.79 = normal). Kp, w and the inbox are
  irrelevant (erasures and swaps have no effect; the Kp erasure diff is
  exactly 0).
- How long the source matters: erasing S kills through t0+9, recovers
  from t0+10 (0.62) and is harmless by t0+11..14 (0.70-0.79), with a
  small dip at t0+15.
- When the channel matters: flushing kills at t0+1..2, costs ~0.18
  through t0+3..11 (0.60-0.62), costs most at t0+12..13 (0.535 / 0.546),
  and costs least at t0+15 (0.745).
- Reading: the sensors LATCH the cue in S and keep emitting it (program:
  EMIT := MAX(S1, SENSE); the S1 latch is built from SENSE). The readout
  (S0 := IN0_1 - 3 at the actuator) takes what arrives near the readout
  tick. Before ~t0+10 the packets that will matter have not been sent
  yet, so the bit is at the SOURCE. After ~t0+11 the last useful
  emissions are in flight, so the bit is in the CHANNEL. The single-swap
  ~0.5 at mid is a CONFLICT between two stages of the same bit (source
  latch vs copies already in flight), not synergy.
- A present but unused carrier: payload component 0 decodes the cue at
  0.85 out of sample, yet swapping it has no effect. Component 1 is the
  one used (swap -> 0.52). This is the Cosmos P1-vs-P2 distinction
  (present vs used) in a PTE specimen.

## Answer to "where is the information?"
The question is well posed only per TICK and per ROLE. At mid-interval,
the bit is held by the source (a regenerating store) and partly by the
transit channel. Causal responsibility moves from source to channel at
the transmission deadline (~readout minus max delay). "Distributed" here
means the same bit is held at two pipeline stages, not a synergistic
code. This matches Archaeon's WHO/WHERE split: WHO holds it (the sensors'
latch) vs WHERE it rides (the channel, payload component 1). No shared
ontology is claimed.

## Follow-ups (backlog T-JC-1 split)
T-JC-2 A confirmatory sensor-only swap at t0+4 and t0+12: predicted FLIP
       early (bit at the source) and CHANCE late.
T-JC-3 Why does C1's "integration beyond one sensor" work here? Are the
       5 sources' contributions summed in flight (superposition) rather
       than at a site? Carrier: a per-sensor swap.
T-JC-4 A generic "source vs transit" profile instrument: erase-at-role
       curves (sensors / actuator / relays) x erase-channel curves.
