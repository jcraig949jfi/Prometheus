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
- E-W13 (MAJOR, RELAY physics map; principal P-2, wave2/P-1/decay_plant*.log):
  - C1's relay_flood plant writes S0 only on change, so decay erases it before readout.
  - A 3-line refresh variant (S0 := sign(S0)*256 at each awake tick, then relay_flood) scores EXACTLY
    its no-decay accuracy at decay_shift 3 AND at decay_shift 1, in 3/3 matched A0 cells (random async,
    random sync, ring sync; 16 worlds). In the same worlds relay_flood falls to .60-.68.
  - "Decay kills RELAY plant viability" (A0 17% -> 0-5%) and the SUPPORTED RELAY plant boundary on
    decay_shift therefore measure the plant's design, not physics.
  - Together with E-W8 (economy = budget identity; delta = light-cone near-tautology), none of C1's three
    SUPPORTED RELAY plant boundaries is a physics phase boundary in the intended sense.
- E-W14 (MAJOR, NULL attribution; W2-T, W2-P, W2-U): 111/454 = 24% of C1 evolve NULLs (RELAY 17, MAJ 34,
  XOR 36, FLIP 24) were unwinnable by any program (joint light cone + wake + placement). Only 48-58% are
  admissible for a search-limitation reading. Only 11% (51, all RELAY) have a plant inside the genome
  space. C1 NULL counts must not be read as search failures without this split. 0/113 sampled NULLs
  were broken experiments.
- E-W15 (MAJ INTEGRATION; W2-M): at the physics of 13/19 MAJ SIGNAL rows, the INTEGRATION ruler
  (lo99 > .70) is unattainable by ANY program (ceiling .701). 11/19 MAJ SIGNAL champions are matched by
  a single-sensor transport. INTEGRATION at 4781b0a1 is genuine (a plant matches; single-sensor
  transport cannot).
- E-W16 (A0 dial ranking; W2-U): ceiling-normalised, RELAY plant-viability top-3 = decay, economy,
  topology. "delta"/"d"/"lat_base" effects are 64-79% the light-cone identity. The B-wave delta
  transect (and P1) was selected by that identity. decay survives normalisation but is plant-design
  (E-W13).
- E-W17 (FLIP rulers; W2-L, W2-S): non-inferring "copy" policies attain balanced accuracy B <= .75
  exactly. FLIP_FEEDBACK and the proposed FLIP_CHANGE are both cheatable (a 14-line relay latch .688; 4
  recorded anti-copy champions pass FLIP_CHANGE). Certify FLIP inference only with B lo99 > .75. No
  recorded C1 FLIP reading rests on copy accuracy (all are ~chance).
- E-W18 (rules>1, setrule=0 cells; W2-Q): 5/8 SIGNAL and 6/7 near-SIGNAL cells are a "rule-mosaic
  lottery". Only the actuator's random initial rule matters (one rule works, the other is dead), and
  the best pinned rule is .09-.21 above the reported accuracy. These cells are over-represented among
  the 512-world census corrections (OR 6.5).
- E-W19 (headline counts; W2-AC, W2-G):
  - Pooled all-wave counts (RELAY 50/196, MAJ 19/162, HOLD 97/155) are not rates (effective n 18-60).
  - The 50 RELAY SIGNAL rows are 6 independent lineages (32 rows from one).
  - Quote A1 rates instead: RELAY 4/71 (5.6%, 95% CI 2.2-13.6), MAJ 3/70 (4.3%, 1.5-11.9), HOLD 34/70
    (49%, 37-60), XOR 0/71, FLIP 0/70.
  - "One hop": A1 one-hop 3/32 vs multi-hop 1/39 (p = .32). Multi-hop is rarer, not shown absent.
  - P4 holds (8/352, 99% upper 4.9%), but it counts an alias of SIGNAL.
  - W-O "84% stay CHANCE" is row-weighted; specimen-weighted it is 72% [63, 80].
  - B2 cross-family boundary agreements share 100% of their seeds and one code cause. They are not
    independent reproductions.
- E-W13 SCOPE CORRECTION (W2-W F1, 2026-10-01):
  - E-W13 holds for the A0 MATCHED counterfactual, i.e. viable decay-0 RELAY physics with decay_shift
    raised and nothing else changed. There relay_flood's collapse is plant design.
  - It does NOT transfer to C1's RELAY NULL cells. Over 41 RELAY NULLs with decay > 0 and relay_flood
    <= .60, the refresh plant reaches SIGNAL level in only 6/41. It equals decay-0 relay_flood within
    .01 in 35/41, so other dials bind there (async, cap/aloha, loss).
  - P-1b's "multi-hop rarity tracks plant viability" survives, but via those dials, not decay (refresh
    revives 1/16).
- E-W20 (NULL placement, consolidated; W2-W): of 454 C1 evolve NULLs:
  - 139 (30.6%) are physics-capped by a sound certificate (light cone + exact wake, joint ceiling, LC2,
    or epidemic bound), plus 17 probable caps;
  - 62-65 (13.7-14.3%) are eligible for a search-limitation reading (admissible plus a plant inside the
    row's own genome): RELAY 54, MAJ 5-8, FLIP 3, XOR 0;
  - 250 are open.
  - Per-cell table: harvest/wave2/W2-W/null_placement.csv. This supersedes E-W14's 24% / 11% figures,
    which used narrower certificates and recorded plants only.

## Corrections to the Wave-2 errata (adversarial review W2-X and transect audit W2-Y, 2026-10-01; these supersede wording above)
- E-W1: the topology result is a REFINE, not a KILL. The D-wave collapse is hop count, not lattice
  offsets. Residual graph dependence remains: clustering or redundant short paths for 4 laws (MAJ
  4781b0a1, 8743da7f; RELAY bf82cb29, cd5b6fd6), and per-port latency labels for HOLD 4ab2ba01 (W2-I
  F3). Retention at matched hops: median .78.
- E-W2: "2.5% impossible" refers to A0 MAJ plant worlds. On C1 evolve held worlds it is 0.17%, which is
  immaterial (W2-O/W2-T). Inward placement turns 0/35 MAJ graph champions into SIGNAL (W2-P).
- E-W3: ">= 36/83 by the deterministic light cone (in expectation); 62/83 by LC2 (W2-J)".
- E-W6: XOR claims need XOR_SYM (W2-J), not XOR_PIVOT. FLIP claims need B lo99 > .75 (E-W17);
  FLIP_FEEDBACK is cheatable in-space. The non-parity .75 bound is in expectation; NOR measured .759
  [.73, .79].
- E-W9: 613162a3's packet clause REPLICATES (pooled 2.96 SE, keep .98; W2-K). It is not fragile.
- E-W10: w_any INITIATES the population sensitivity climb and suffices for large persistence. The
  attribution of the MWU/REACH labels to w_any is NOT shown (bonus-only flat runs: MWU 1/40 vs
  37/414). First generation with accuracy variance: median ~4 (IQR 2-9).
- E-W13: "exactly" is replaced by "within one world-pair or exactly". STRENGTHENED by W2-X and W2-Y:
  refresh flattens the decay transect at BOTH SUPPORTED bases on the actual C1 transect rows (RELAY b0
  1.0/1.0/1.0/1.0; b1 .80/.82/.78/.81; FLIP b0 no step).
- E-W14: ".614" is the 50%-power bar, not impossibility. 93/454 have ceiling <= .55. E-W20 supersedes
  both counts. "Plant-backed 51" counts recorded plants only.
- E-W21 (C1 phase boundaries; W2-Y, flood ceiling with random routing, KA 9/9): of the 13 SUPPORTED
  boundaries:
  - delta x2 = transport-time IDENTITY (the flood ceiling steps .685 -> .999);
  - RELAY decay x2 = PLANT-DESIGN (refresh is flat);
  - HOLD decay x4 = non-refreshing-latch artefact [I];
  - emit-vs-rules x3 = program-space;
  - economy x2 = energy, OPEN (the only physics candidate).
  The 3 MAJ topology CANDIDATEs and the evolved RELAY-acc delta CANDIDATE are IDENTITY.
  "No SUPPORTED boundary is established physics beyond the transport bound."
  P1 stays HELD as a label; its content is identity plus plant-design.
  The W2-P/W2-U light cone overstates reach on global/sample topology (random destinations), so
  construction-capped counts there are undercounts.
- E-W22 (multi-hop RELAY SIGNALs; W2-AI): both multi-hop RELAY SIGNAL rows (925caa3a48964717 ring d5;
  882525a9d4a3d073 smallworld d3) FORWARD, but only ONCE PER EPISODE.
  - Each is a receipt-triggered flood latch: the first positive cue fires an irreversible wave, and
    later trials score .500.
  - Accuracy profile 1.00, .70, .59, ... then .50. A latch model predicts 99-99.6% of readouts.
  - 64/64 held worlds are true multi-hop, and the forwarding is certified by vertex-cut ablation
    against equal-size controls.
  - Consequences:
    - (i) "multi-hop competence absent" is false. It is present as one-shot cascades. Per-trial
      (resettable) multi-hop relay is NOT shown.
    - (ii) At 12 trials a one-shot latch clears SIGNAL (ceiling ~.58-.59), so a RELAY SIGNAL near
      .58-.60 does not certify per-trial competence.
    - (iii) REACH_BEYOND_HOP (twin at trial 2) is a false negative for latches: beyond_hop is 1.0 at
      trial 0.
