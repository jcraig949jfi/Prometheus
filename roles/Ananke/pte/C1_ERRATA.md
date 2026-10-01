# PTE-C1 errata (C1 labels are NOT changed; these are reading notes)

Currency: 2026-09-26. Source: PTE-C1b (roles/Ananke/pte/c1b/, rows sha256
8019247c19cdf2f0) and the pre-run code inspection (comms #639/#640, #661,
#683).

E1 D-A PACKET-ABLATION WINDOW. C1's packet_ablation dropped arrivals over
   [t0, readout) and never at the readout tick. For the two M3 cells
   (0a23398f, f6b623cd; delay == delta == 4) this made the C1 null
   VACUOUS BY CONSTRUCTION: no arrival carrying the trial's cue could fall
   inside the window. C1b confirmed it on the specimens: C1 window
   0.697 / 0.686 (no effect), readout-tick-only 0.511 / 0.500, corrected
   window 0.501 / 0.500. The recheck of all 12 D-wave cells shows no other
   verdict affected (RELAY corrected 0.50 in 4/4; HOLD latches 1.00).
E2 FROZEN ROUTING VACUOUS under dest_mode "all" (both M3 cells). w is never
   read there, so "frozen routing: no effect" could not have been otherwise.
   The C1 reading "SETRULE carries it" rested partly on that null. C1b:
   SETRULE is required (freeze_rule -> 0.52), but the readout site's rule
   index carries no cue (constant 0).
E3 C1's MEMORY ABLATION reset only S. M2's "not in any site" was
   under-identified. C1b per-carrier resets: S, inbox no effect; w -0.066;
   the joint non-packet reset -0.062; flushing in flight -> 0.497.

## Errata from the inference-harvest code audit (2026-09-30, harvest/H-IMPL/REPORT.md)
- E-H1 (MAJOR, labels): on MAJ and XOR the twin assay negates EVERY sensor column but measures reach
  from sensor 0 only (assays.py twin_assay). A program that never emits scores beyond_hop 1.00 (MAJ
  reach 6, XOR reach 3). The stored REACH_BEYOND_HOP labels for MAJ (114/162, 59 with comm_delta < .02)
  and XOR (48/83, 46 with comm_delta < .02) are UNINTERPRETABLE. No C1_REPORT headline uses them.
  From 2026-09-30 twin_assay also reports reach_nearest / beyond_hop_nearest (distance to the nearest
  perturbed sensor); legacy keys are unchanged.
- E-H2 (label): on global topology every env distance is <= 1, so REACH_BEYOND_HOP can never fire
  (0/213 global evolve rows). "No distal reach" on global is structural, not measured.
- E-H5 (wording): wave E scales ONE RELAY law (bbef66a1). C1_REPORT s1's "frozen RELAY laws ...
  SIZE-FREE" rests on that single law, and bbef66a1 failed its fresh-seed reproduction (reps .572 /
  .506). The reproduced RELAY cells were never scaled.
- E-H2b (interpretation, principal-verified with H-SCI): zero_comm is exactly .500 in 213/213 RELAY,
  174/174 MAJ and 95/95 XOR rows. It is forced by construction: mirror pairs share all physics draws,
  and the actuator is never the sensor. COMM_DEPENDENT therefore equals SIGNAL in these families, and
  zero_comm cannot count as causal evidence there.

## Errata from the Wave-2 inference saturation (2026-10-01; harvest/wave2/, reports deposited verbatim)
C1 labels are NOT changed. Each item names its source report; [P] marks those re-checked by the principal.
- E-W1 (MAJOR, reading of F2 / "topology-bound"; W2-G F1 [P code]): the D-wave topology->random
  transplant keeps env d. On random graphs, env distance is BFS hops, so a 1-hop ring task becomes a
  3-hop task. At d=1 on the same random graph all 4 RELAY laws stay above chance (lo99 .57-.81). The
  collapse measures hop count, not lattice geometry.
- E-W2 (MAJOR, MAJ geometry; W2-A2 F3, W2-A1 F1):
  - MAJ "d" is not distance d. On rings d=1 and d=2 give identical placements, and 3 of 5 sensors are
    off d.
  - On directed graphs sensors are placed by out-distance from the actuator (envs.py:212), while
    packets travel sensor -> actuator. Only 18% of sensors sit at transport distance d; 2.5% of random
    worlds are impossible.
  - 2 of the 3 MAJ topology boundary CANDIDATEs are placement artefacts; the third is confounded with
    the dest_mode alias.
  - All 19 MAJ SIGNALs are one-hop placements.
- E-W3 (MAJOR, P3 / XOR NULL; H-PLANT, W2-G F3 [P]): 36/83 = 43% of XOR evolve rows (FLIP 24/82,
  RELAY 16/196) are light-cone-capped below .60 for ANY program. The XOR actuator has no upper distance
  bound, so ring rows are dead by construction.
- E-W4 (interpretation, C1_REPORT "one hop"; W2-G F5, P-1b [P]):
  - 150/196 RELAY evolve rows only demand one hop.
  - The 50 RELAY SIGNAL rows are 17 distinct conditions.
  - Among light-cone-reachable rows, 21/30 multi-hop rows are relay_flood-dead.
  - Conditional on a working plant, search succeeds 40/99 one-hop vs 2/9 multi-hop (n.s.).
- E-W5 (controls; W2-B P1/P5/F4, W2-A1 F3):
  - COMM_DEPENDENT is an exact alias of SIGNAL in RELAY/XOR/MAJ, and LOCAL_ONLY is unreachable there.
  - env_permutation cannot fail (E = .5 for any program).
  - max_loss is the same run as zero_comm (12/12 pair vectors).
  - CAUSAL_SUPPORT in comm families rests on the packet_ablation clause alone.
  - shuffle_dest on global topology is a re-draw of routing noise. 613162a3's "shuffle .72 > normal
    .688" is routing variance.
- E-W6 (rulers; W2-B P2/P3, F1/F2): XOR SIGNAL is cheatable as a parity claim: every non-parity readout
  scores <= .75, and NOR of the flags scores .759. FLIP SIGNAL is cheatable as a feedback claim: a block
  clock reading the first teacher scores 1.000 (28 lines; not shown within 16). No C1 XOR/FLIP SIGNAL
  exists, so no label changes. Future claims need XOR_PIVOT / FLIP_FEEDBACK.
- E-W7 (refines E-H1; W2-B P4/F6): legacy REACH_BEYOND_HOP on XOR/MAJ is fired by any one-hop emitter
  even when d <= hop (silent programs fire it only when sensor spacing > hop).
- E-W8 (wording, P1/P5/P7; principal P-4, W2-B P11-P12):
  - P1 held on delta, where a relay plant improving with later readout is near-tautological.
  - P5 held on ONE comm-family source.
  - P7 (size-free HOLD) and the wave-E size test are forced for local laws.
  - 8/104 transects (2 levels) could never yield a boundary.
  - The SUPPORTED economy boundary is a budget identity (relay_flood is mute by tick ~11; W2-A1 F5).
- E-W9 (statistics; W2-H F2/F3/F4): the held CI (percentile bootstrap, P=32) undercovers. Under BOOTT
  2 SIGNAL calls flip (884a64df, 8ccf6c72); under t, 3 flip. No prediction changes. BH q=.01 keeps
  210/216 SIGNAL calls. 613162a3 CAUSAL_SUPPORT is fragile (keep probability ~.88).
- E-W10 (selection; W2-A2 F1, principal P-3 [P]):
  - In NULL runs every genome scores acc exactly .5 until gen ~5 (40 runs: all 36 generations), yet
    population sens_any rises 19-70x under the .02*sens_any bonus.
  - MEMORY_WITHOUT_USE (46 rows) and REACH_BEYOND_HOP/persist on NULL champions are, at onset,
    products of the w_any term.
  - NULL champions sit ~80x above random genomes on persist.
- E-W11 (provenance; W2-A2 F4, W2-G F4, W2-D F1): classify stamps transfer rows with
  REACH_BEYOND_HOP=False although no twin ran, and the prereg NULL-with-eligibility label is not
  implemented. Transfers fac4aaa2, ef77ef2e and 1b26026f were cited in H-PLANT as search NULLs. d9cc
  has ONE FLIP search and ZERO multi-hop RELAY searches.
- E-W12 (bookkeeping; W2-A2 F6, W2-A1 F2): summary.json counts 23 TRANSFER_SUPPORT; the effective count
  is 1 (22 HOLD variants rerun the same condition). A report key TRANSFER_SUPPORT_EFFECTIVE was added
  2026-10-01. summary.json describes 5/12 D cells as "dest_mode all"; they ran "sample".
