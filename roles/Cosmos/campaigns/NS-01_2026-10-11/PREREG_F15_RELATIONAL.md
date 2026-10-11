# NS-01 / F15 test -- is "readout decodes the cue better than the full-state decoder" a new failure? (prereg
# 2026-10-11T08:35Z, before any of the tests below has been run on any mechanism)

Observation (deep investigation, 8407a30bd + ns01_deep): B01 rf 1.00 / full .84; B05 rf .87-1.00 / full .91 -> .40;
B08 rf 1.00 / full .29 (all k; fresh seed and 4 disguises reproduce). full[k] = random-feature ridge decoder on the
standardised declared full_state. If the cue is in the state yet invisible to that decoder, every instrument that
reads "information present" off full_state (C3 P1 decodability; this campaign's DEGENERATE and M-UNREACHABLE rules)
has a false-negative region.

Mechanisms: B01, B05, B08 (unmodified originals) and W-REL, a minimal witness written by Cosmos from the causal account
(M share pairs (A, B) in Z4; cue sets B - A = c with a uniform key; every later step adds a common uniform shift r_m to
both shares; readout = histogram of (B - A) mod 4; no noise). k in {1, 4, 16}; seeds fixed.

Measurements: rf (readout, as in the signature); T0 full_lin = LINEAR ridge decoder on full_state; T1 full_onehot = rf
decoder on a per-coordinate one-hot re-encoding of full_state (coordinates rounded to integers, values clipped to the
observed range; continuous-state mechanisms get T1 = n/a); T3 (B08 and W-REL only) interventions at t = 1 on the
state dict: GAUGE (add one common uniform shift per pair to A and B) and DESYNC (add an independent uniform shift to B
only); readout decoded with the unperturbed decoder.

Classification per mechanism (first match; gap = rf - x, averaged over k):
- DECODER_CLASS_ARTIFACT (known: decoder-class dependence of "usable", archive XorCue / E08 shared-failure matrix):
  gap(full_lin) <= .10.
- REPRESENTATION_DEPENDENT (known, tier P8 / E12, narrowed): gap(full_onehot) <= .10.
- RELATIONAL (candidate F15): gap(full_lin) >= .20 AND gap(full_onehot) >= .20 AND (where run) GAUGE keeps the readout
  excess >= .9 x baseline AND DESYNC drops it below FLOOR .10.
- otherwise UNRESOLVED.
NOVEL_FAILURE_CANDIDATE iff B08 is RELATIONAL. NOVEL_FAILURE_SUPPORTED iff, in addition, W-REL (written by Cosmos from
the account, not from B08's code) is RELATIONAL. Either way the unmodified originals are preserved and nothing is
repaired; the class enters the archive only for NS-02.
