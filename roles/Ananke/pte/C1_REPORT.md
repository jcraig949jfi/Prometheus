# PTE-C1 -- final report (Ananke, 2026-09-25)

Currency: 2026-09-25T00:30Z. Campaign pte-c1 ran 2026-09-24T12:04Z ->
2026-09-25T00:06Z (12 h 02 m), watchdog exit 0, 0 failed cells, 6596 rows.
Frozen at 362f2189b (code eb7c4b40a, PREREG 78243a758). Every number here
is recomputed from the rows by prometheus/ananke/report.py
(c1_report/REPORT.md, c1_report/summary.json); interpretation below is
the seat's and is marked where it goes beyond the preregistered labels.
Post-data annotations to the PREREG (boundary-criterion defects D1-D3) are
in PREREG_PTE_C1.md; no label was changed after data.

## 1. Headline

In a mutable integer substrate with lossy, delayed, superposing packets
and no neural machinery, an ordinary mutation-selection search finds
communication-dependent machinery that is CAUSALLY verified, REPRODUCED
on fresh search seeds, and SIZE-FREE: frozen RELAY laws keep 0.875-0.893
held-out accuracy from N=100-ish up to N=2304 sites, against exactly
0.500 with communication removed. It is rare (A1: 8/352 cells
COMM_DEPENDENT), topology-bound (every RELAY law collapses to 0.500 when
moved to a random graph), and it does not transfer across task families
(0 cross-family TRANSFER_SUPPORT). No integration beyond one sensor
reproduced, and XOR and FLIP produced no signal at all.

The physics has sharp, reproducible gates -- but the SUPPORTED phase
boundaries belong to a known hand-written design, not to evolved
machinery. Evolved transport exists where that design dies.

## 2. The ladder (operator framing, 2026-09-24)

  rung  meaning                          where it stands after C1
  ----  -------------------------------  ----------------------------------
  L1    perturbable                      common: 11-23% of comm-family
                                         A0 cells; set by PROGRAM-SPACE
                                         dials (rules, prog_len, state_dim)
  L2    distal influence                 rare: 0.3-0.7% of cells for a
                                         random program
  L2'   known design viable              RELAY 19/1000; gated by decay,
                                         delay, energy cost (SUPPORTED)
  L3    discoverable / exploitable       RELAY 50/196 evolve cells SIGNAL,
                                         MAJ 19/162, HOLD 97/155,
                                         XOR 0/83, FLIP 0/82 (all waves)
  L3->transport (causal)                 RELAY 4/4 promoted CAUSAL_SUPPORT
  L4    reuse / adaptation               within-family env transfer yes
                                         (RELAY d1/delta4: 0.755); size
                                         transfer yes; cross-family NO;
                                         topology transfer NO; FLIP NULL

Two facts break a naive ladder:
- L2' and L2 are disjoint in RELAY (0 of 7), and L3 appears where L2' is
  0% (a RELAY SIGNAL at loss 0.6 where the design is 0/253; MAJ SIGNALs
  at decay 3 and 6 where it is 0/755). Evolution finds transport outside
  the region a human design needs. A0 plant viability is therefore NOT a
  map of where communication is possible, and must not be used as the
  C2 habitable zone.
- Seeding half of A1 in "living" A0 cells gave no advantage (RELAY 2 vs
  2, MAJ 2 vs 1 SIGNAL): A0's rungs were prior-bound (L1, L2) or
  design-bound (L2').

## 3. Mechanisms found (from the D battery and the post-hoc battery)

  M1 ROUTED RELAY (RELAY, 4 cells, 0.84-0.89). Zero-comm, max-loss and
     shuffled destinations all -> 0.50; shuffled timing barely matters
     (0.73-0.88); payload randomisation partial (0.50-0.70). The law
     depends on WHERE packets go on the lattice, not on when. Survives
     +0.2 loss, +1 latency, +2 jitter, x2.25 size, async 0.7; collapses on
     a random graph. Fresh-seed searches reproduce it in 3 of 4 cells.
  M2 DELAY-LINE MEMORY (HOLD, 1 cell, 0.883; POST-HOC, exploratory).
     Resetting every site's state mid-gap changes nothing (0.88); dropping
     packets, randomising payloads or removing comm -> 0.50. The held bit
     lives in packets in flight, not in any site, although a one-site
     latch solves HOLD. Nobody designed this; the PREREG HOLD rule labels
     it NOT_SUPPORTED because it assumed memory lives in site state.
  M3 SELF-MODIFYING, TIMING-LOCKED MAJ (2 cells, 0.69). Zero-comm -> 0.50
     but packet ablation in the cue->readout window does nothing (0.70);
     in-lifetime adaptation off -> 0.53-0.55 (routing freeze alone: no
     effect, so writable immediates / rule switching carry it); +1
     latency -> 0.49-0.50. PREREG label NOT_SUPPORTED (the rule was
     written for relay-style transport). Candidate, not established.
  M4 INTEGRATION (MAJ, 1 cell, 0.789, lo99 0.742 > 0.70 single-sensor
     ceiling). CAUSAL_SUPPORT, but fresh-seed replicates 0.636 and 0.520:
     integration beyond one sensor did NOT reproduce.
  M5 LOCAL LATCH (HOLD, the trivial solution, most HOLD cells).

## 4. Phase boundaries (PREREG s8; 13 SUPPORTED, 24 CANDIDATE)

  SUPPORTED, physics, known design (RELAY relay-flood viability), both
  bases and fresh seeds:
     decay off -> on          -0.45 / -0.26
     delta 4 -> 8             +0.40 / +0.15
     economy low -> high      -0.45 / -0.22
  SUPPORTED but one phenomenon: HOLD latch dip at decay_shift=1 (counted
  4 times; defects D2 zero-variance and D3 dip) -- the sign-asymmetric
  integer decay predicted in DESIGN s10 (positive memories stall at
  2^k-1, negative ones erase: 0.75 = half at 1.0, half at 0.5).
  SUPPORTED, program-space: random-program emission vs rules (MAJ, FLIP).
  Evolved competence: only CANDIDATE (RELAY acc delta 4 -> 8, +0.18,
  reproduced on fresh seeds, not at the second base).
  Reading: there is no reproducible phase boundary in EVOLVED competence
  yet. The sharp gates found are properties of one design and of the
  program prior.

## 5. Predictions (PREREG s12): 5 HELD, 3 LOST

  P1 HELD  RELAY plant boundary SUPPORTED (delta; also decay, economy)
  P2 LOST  HOLD evolved competence at decay 1 was not NULL (3/9 SIGNAL)
  P3 HELD  zero XOR SIGNAL (0/83 evolve cells)
  P4 HELD  <= 5% of A1 COMM_DEPENDENT (8/352 = 2.3%)
  P5 HELD  zero cross-family transfer
  P6 LOST  one DISTRIBUTED_MEMORY_UNDER_DECAY flag (post-hoc: that cell
           depends on in-lifetime adaptation, 0.50 when off)
  P7 HELD  HOLD champions unchanged at N=1024
  P8 LOST  no ANTI_CORRELATED cell at all (the decay asymmetry shows up
           as a 0.75 dip, not as below-chance behaviour)
  Lost calls are in calibration/LEDGER.md.

## 6. What the failures expose (the seat's reading; roadmap inputs)

  F1 XOR and FLIP: 0 signal in 165 evolve cells. Superposition sums
     packets, so a receiver sees x1+x2, from which XOR needs a
     |sum|-threshold and exact co-arrival; FLIP needs a teacher-conditioned
     sign flip held across trials. Both are two-stage compositions the
     search never assembled at this budget. Opening: port-resolved
     arrival (ANANKE-10), longer programs, multi-episode lineages.
  F2 Topology-bound laws: every RELAY law dies on a random graph. The
     machinery encodes lattice geometry (routing to specific offsets).
     Opening: evolve across mixed topologies to force geometry-free
     transport, or accept geometry as the substrate's "body".
  F3 The PREREG labels missed two of the three most interesting
     mechanisms (M2, M3) because the causal rules encoded the mechanism
     we expected. Opening: mechanism labels from the ablation PATTERN
     (a fingerprint over all controls), not from one expected control.
  F4 The boundary criterion over-fires on categorical dials, zero-variance
     metrics and one-level dips (PREREG annotation D1-D3). Fixed for C2
     before data.
  F5 Wave C's HOLD env variants changed d/delta, which HOLD never reads:
     22 "transfers" were the same condition rerun. They are flagged and
     not counted as transfer.
  F6 A1 hit its budget cap (48/400 censored; 51 s/cell vs 37 preflight);
     promotion by lo99 gave HOLD's four D slots to trivial 1.000 latches
     and left out M2. Opening: promote by comm_delta and by ablation-
     pattern novelty.
  F7 Throughput 11-21M site-updates/s is launch-bound on Windows without
     Triton; a fused kernel (ANANKE-09) or Linux/RunPod with torch.compile
     is the scale path.

## 7. Recommended next steps

  1. Adversarial review of this package (Kairos / Elenchus) before any
     promotion beyond the seat (the independent failure mode).
  2. PTE-C1b (small, preregistered): adjudicate M2 and M3 properly --
     fresh-seed replication, a delay-line fingerprint for M2 (in-flight
     packet count vs held bit), a WIMM/SETRULE split for M3.
  3. PTE-C2 "weather": habitable zone = the physics of the CAUSALLY
     verified RELAY/MAJ cells (not A0 viability, see s2), three separate
     load axes (traffic density, independent processes, informational
     conflict), fixed boundary criterion, ablation-fingerprint labels.
  4. v2 dials motivated by F1/F2: port-resolved arrival, TTL
     auto-forwarding, mixed-topology evolution.
  5. RunPod only for C2's scale leg if a region strengthens with N; C1's
     RELAY laws are already size-free to 2304 locally.
