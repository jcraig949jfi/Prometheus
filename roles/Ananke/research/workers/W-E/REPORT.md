# W-E REPORT  T-RET-1: does PTE have a nontrivial retention regime?

(Saved by Ananke from W-E's final message; the harness refused the
worker's own write. Code, PLAN (with Addendum A before any run and
Addendum B after, labelled exploratory), LOG (attempts 0-5) and out/*.json
are in this directory. Process note: W-E took the cpu8 lease seconds after
starting 3x2-thread CPU processes, not before. A protocol slip,
disclosed.)

Namespace 0x5E9, 64 worlds = 32 single-cue twin pairs, k=3, lags j=0..6, CPU.

VERDICT (preregistered rule): NO. No champion is RETAINS-RECOVERABLE under
the primary single-world decoder (Holm over 112 tests at j >= 2; smallest
adjusted p = 0.149, D_f7e62fe3). The decoder works: all 16 champions decode
cue k at j=0 (p at the floor), and the trial-(k+1) control decodes in 16/16.
The NO is mostly a POWER limit, which the positive control (C-POS) predicted
before any champion ran.

GUARDS (all passed for 16 champions + 2 controls): G1 twins bit-equal
before the cue; G2 no re-divergence after a merge; G3 schedules differ
only at the cue ticks; G5 a full-state swap gives the twin's baseline answer
in every world; G6 noise calibration p < .05 in 5.0% (single) and 3.0%
(paired).

PER CHAMPION
FORGETS (7): D_67ddd858, D_223acaee, D_a8f4ea11, D_023539c4, D_feadc823,
  M2_4ab2ba01, M2_fresh1. Twins are bit-identical 1-11 ticks after the
  readout; decoders are exactly 0.5 afterwards.
DIVERGES-UNRECOVERABLE (5, preregistered label). In 4, the PAIRED
  (twin-difference) decoder is Holm-significant, so the difference is
  cue-signed, not chaos:
  D_f7e62fe3 (w only; paired 1.00 at every lag), D_6a47bd68 (S; 0.89-0.91),
  D_0ad7dc00 (Kp+S; 0.80-0.84), D_e79e72df (Kp+S; 0.61-0.84), D_9e72f9b6
  (Kp+S; 0.72-0.75, Holm p .09 n.s.).
MIXED, slow merge (2): D_5673ea4e (median merge 65 ticks after the readout),
  D_544f3d24 (81-119).
INTERFERES (2): M2_fresh2, M2_fresh3. They diverge chaotically in every
  carrier; later answers change in 9-34% of pairs, with a signed
  interference of ~0 (no consistent direction).

SURPRISES
1 FROZEN SIGNED "SCARS": a write at trial k to a non-decaying plastic store
  is never overwritten (the same value at j=1 and j=6): D_f7e62fe3 4 w
  elements (32/32 pairs signed); M2_fresh3 one w element +-8 (32/32);
  D_0ad7dc00 one Kp element ~216 (22/22); D_6a47bd68 one S element 5-22
  (25/25). NONE changes a later answer (EFFECTIVE = 0 outside fresh2/3).
2 The primary decoder cannot see a trace buried under the other trials'
  cues (C-POS integrator: single 0.59-0.64, paired 1.0; f7e62fe3 the same).
3 EXPLORATORY, post hoc (Addendum B): a single-world decoder that regresses
  out the known other trials' targets recovers cue k from D_f7e62fe3's
  w_sum at 0.97/0.97/0.94/0.89/0.88/0.89 for j=1..6 (Holm p = 0.0056 at
  each lag). No other champion passes at j >= 2. C-POS reaches 0.67-0.80
  with the same decoder. f7e62fe3's routing weights act as an INTEGRATOR
  of the cue history.

WHO RETAINS: the s_ct site/in-flight labels do NOT predict retention.
PHYSICS does. Decay-0 rings with plastic_route=1 retain in w, and with
wimm=1 in Kp; global HOLD cells keep Kp and S residues at floor level;
latch-only and flight-only carriers forget within one trial. The retaining
stores are WRITTEN BUT NEVER READ by the task mechanism.

PROPOSED THREADS: T-RET-2 (a preregistered confirmation with the
history-aware decoder as primary; f7e62fe3 / fresh3 / 0ad7dc00 / 6a47bd68;
k in {2,3,5}); T-SI-SCAR (is the trial-k w-write in f7e62fe3 selectively
irreversible? can later input erase it, i.e. make the twins merge? can a
w-only swap ever make it effective?); T-RET-3 (where the scar elements sit).
Instrument note: sum-sign decoders are weak on accumulating memories; use
paired twin contrasts or regressions on the known cue history.
