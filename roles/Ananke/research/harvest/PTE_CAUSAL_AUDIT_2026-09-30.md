# PTE causal audit (inference harvest, 2026-09-30)

Principal synthesis of three independent fresh-context attacks and the principal's own checks:
- harvest/H-IMPL/REPORT.md: implementation audit, 26 findings, 5 patches applied.
- harvest/H-SCI/REPORT.md: interpretation, chain audit and claim audit.
- harvest/H-INST/REPORT.md: instrument gaps and the pte_trace draft.

Principal-verified numbers are marked [V]. Worker-reported numbers are cited by report. Where the
workers disagree, the resolution is stated.

## 0. The five things that change how PTE results should be read
1. **The main comm-dependence control cannot fail. [V]**
   - zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ and 95/95 XOR rows.
   - Cause: mirror partners share every physics draw, and the actuator is never the sensor. With no
     packets, both twins give an identical actuator trajectory.
   - So COMM_DEPENDENT = SIGNAL in the comm families. max_loss and shuffle_dest are the same forced
     control.
   - C1's "causally verified" comm-dependence therefore rests on packet_ablation alone.
2. **Evolved transport is almost entirely ONE hop. [V]**
   - RELAY competent evolve cells: 35 one-hop ring/torus tasks, 4 on global topology, 10 smallworld
     (9 at d = 1), and 1 multi-hop ring (d5 r3).
   - MAJ: 18 of 19 one-hop, 1 global.
   - The dial d is geometric, not a hop count: d <= radius is one hop.
   - "Transport", "relay" and "size-free" findings are statements about one-hop broadcast plus a latch
     at the receiver.
3. **The search fitness pays one-sided codes. [V, code]**
   - f = acc + 0.10 max(sens_act, 0) + 0.02 sens_any (search.py), where sens_act is the mean
     sign((S0_lead - S0_twin) y).
   - A rectified code (S0 in {0, +x}) earns the full bonus at accuracy .75.
   - This is a declared shaping term, not a bug. It is a plausible cause of the observed dominance of
     presence, one-sided and RECTIFIED codes and of integrators where they do not pay. Untested (ANANKE-14).
4. **Most mechanism claims come from ONE physics point** (ring 144, r3, fanout 8, sync period 2, ...),
   descended from one census cell, 86fc0105 (H-SCI F3). That covers the W-I panel, W-L, W-S/W-T,
   4781b0a1 and the M2 echo.
5. **Two C1 labels and one C1 sentence are wrong or uninterpretable** (H-IMPL H1, H2, H5; now in
   C1_ERRATA):
   - MAJ/XOR REACH_BEYOND_HOP is measured from sensor 0 only; a silent program scores 1.0. [patched,
     additive]
   - On global topology the label cannot fire at all.
   - "Frozen RELAY laws ... size-free" rests on ONE law, bbef66a1, which failed fresh-seed
     reproduction.

## 1. Chain audit (boundary by boundary)

| boundary | can the phenomenon reach it? | hidden equivalence / leakage / shortcut | ruler adequacy | NULL from search vs physics? |
|---|---|---|---|---|
| world physics | Yes. Engine = independent oracle, bit-exact (185 tests; GPU conformance re-verified after the harvest patches: 98 passed). | envs.py has NO oracle and drifts from DESIGN s7 without an annotation (balanced targets, MAJ geometry, XOR distance; H-IMPL H20). Fixed deterministic readout ticks let timing coincidences (echo tuned to the gap; delay == delta) solve "memory" and "transport". | n/a | n/a |
| search reachability | Only tails of the seed distribution; champions reproduced 0/4 from their own budget (W-H). | The fitness shaping term (item 0.3) is a selection-side teacher path. B2 seeds are shared across families (H-IMPL H6), so cross-family B2 agreements are not independent. | n/a | UNDECIDABLE for XOR, FLIP and multi-hop: no plant exists for them. "Search cannot reach them" (H6) is untested exactly where it matters (H-SCI). |
| packet generation | Yes. The dominant code is WHO FIRES (presence). | Under superposition presence is also content, so channel_content vs channel_count names the reader's register, not the physical code (W-C, W-I). | Copy counts are not causal weight: the source re-broadcasts 78-79% of copies, and the readout uses first or last only (W-S, W-T, W-V). | -- |
| packet transport | One hop (item 0.2). Multi-hop: 2 marginal cells, no plant. | zero_comm, max_loss and shuffle_dest are forced (0.1). topology->random re-picks the actuator at 3 hops, so its collapse tests "no multi-hop", not "lattice geometry" (H-SCI 1.4). | Only packet_ablation can fail, and it is near-definitional for a relay. | -- |
| receiver semantics | The operator is behaviourally irrelevant at C1 physics (29/32 one-arrival codes; W-J). | Readouts overwrite S0 every wake (M2; 4781b0a1: S0 := IN0_1 - 3; readout Kp[7] = 0 everywhere, W-Y), so the readout samples its last wake window. | S0 == 0 scores .5, and with 0.3 that rewards rectification. Clock parity changes the class (W-R). | -- |
| aggregation | MAJ sensors are all direct neighbours; aggregation is physics superposition plus a threshold. | -- | The INTEGRATION label (lo99 > .70) cannot see noisy aggregation. Majority agreement .77-.84 > best single sensor in all 4 MAJ champions, including the "single-sensor" M3 (H-SCI F5, descriptive). W-V's majority control was lossless, so "not a majority" is WEAKENED. | -- |
| state retention | The tasks never reward cross-trial retention (i.i.d. per-trial targets), so its absence is EXPECTED. | The mirror swap moves the sign of the whole history: an integrator reads like a lag-k store (H-SCI 1.7). | Single-cue twins can separate the two, but the swap verdicts do not use them. | W-L: selective lag-2 0/4 at one budget and physics, with 4 seeds. "Search-limited" is weakly supported. |
| behaviour | HOLD with sensor = actuator is a trivial local latch (81/85 SITE is forced by locality). | The fixed schedule makes a delay line indistinguishable from memory at the trained gap (M2 is at chance for gap >= 12). | -- | -- |
| assay / ruler | -- | lens.verify_reach's "applied" is a batch digest: 85 applied ticks, exactly NOT_REACHED (H-INST). The mirror sum identity is forced (W-M). | FLIP_REL certifies z < -1/2, not completeness. Seed consistency near threshold is 92.7%, with about half from pure threshold noise [V: 11.8 expected vs 22 observed]. The promoted H2 interval is INERT on real data [V: 0/439 group-arms differ from REL3]. H-IMPL H16: swap_rel's sd_floor is on the SE scale while floored as a per-pair SD, so it is ~1/(2 sqrt P) of the plan's intent; and the FC simulator treats K trials per PAIR as independent, whereas real pairs average 2K correlated mirror-world trials. The FC table certifies the simulated model, not the mirror-pair design. | -- |
| scientific conclusion | -- | One physics point, one GA, one author; the independent reviewers never replied (C1b). | Counting by arm, not by independent unit (733 verdicts = 249 groups; 42 transfers = 20 groups). | The syntheses generalise from the ring-144 panel to "PTE" and count forced controls as causal verification. The workers' internal self-correction was strong. |

## 2. Claim verdicts (principal resolution of H-SCI's claim audit; details in H-SCI s2)

| claim | verdict | why (short) |
|---|---|---|
| C1 headline: RELAY comm-dependent, causally verified, reproduced, size-free | WEAKENED. Evolved one-hop relays above chance: SUPPORTED. The "causally verified machinery / lattice-bound / size-free laws" wording: UNSUPPORTED. | forced control (0.1); one hop (0.2); one scaled law, unreproduced (E-H5) |
| "No integration beyond one sensor" | WEAKENED | ruler threshold; F5 majority agreement exceeds single-sensor agreement |
| M3 = transport landing on the readout tick | SUPPORTED | corrected window, latency +/-1 |
| M2 = in-flight echo / tuned delay line | SUPPORTED as an echo; "memory" UNSUPPORTED | gap sweep |
| H6: search, not physics, bounds PTE | WEAKENED | only W-L tests reachability; the biggest NULLs have no plants; fitness shaping is a confound |
| Carriers are trajectories | SUPPORTED, but trivial for one-hop relay + latch | -- |
| No retention regime / SI01 closed | SUPPORTED for the 16 champions; UNSUPPORTED for PTE | the tasks penalise retention |
| Promoted relative swap verdict | SUPPORTED as a statistic on the swap; WEAKENED as a carrier ruler | whole-history mirror swap; FC under modelled nulls; inert H2 floor |
| "84% of CHANCE stay CHANCE" | SUPPORTED as a count; UNSUPPORTED as mechanism evidence | structural causes (normal < .62, o <= 0, identity-broken) |
| 4781b0a1 "joint carrier" (W-P) | WEAKENED (H-CHK C1: PARTIAL) | a count-threshold plant with NO joint logic reproduces JOINT-2 AND/OR, the (inbox, Msum) pair and the o14-15 phase split |
| 4781b0a1 "not a majority" (W-V) | WEAKENED (H-CHK C2: PARTIAL) | the W-V classifier calls a lossy TRUE majority DISTRIBUTED-NONMAJ (D_piv .38-.44 vs 1.00 lossless), so the label is no evidence against a noisy majority |
| First-broadcast jitter rule (W-S), no reach (W-T) | SUPPORTED, scoped to 3 RELAY cells | -- |
| SETRULE compresses (W-H) | SUPPORTED within 5 cells | -- |

## 3. Code defects (H-IMPL; principal disposition)
- APPLIED (neutral, regression-tested; full CPU suite 229 passed, GPU conformance 98 passed):
  - H1 twin reach nearest-sensor keys (additive);
  - H3 past-schedule overwrite;
  - H4 wave-D resume determinism;
  - H13 vacuous handoff clause;
  - H18 Controls.label.
- ERRATA (C1 frozen; recorded in C1_ERRATA): E-H1, E-H2, E-H5, E-H2b.
- REPORT ONLY, no change needed now (future C2 driver): H6 seed reuse across families; H7 recorded vs
  actual dest_mode (951 of 1589 global rows) and inert transects; H8-H12, H14-H17, H19-H26.
- OPEN (instrument):
  - H16 swap_rel's sd_floor units and the FC model's pair structure. Needs a plan-first re-check before
    swap_rel is used to certify carriers at small P.
  - Low urgency on current data, because H2 = REL3 on all real arrays [V].

## 4. What the record can still claim, in one paragraph
Evolution under this GA reliably finds ONE-HOP broadcast relays with a latch at the receiver, at one
physics point. Their per-trial carrier behaviour is set by packet latency jitter and the update clock
phase. MAJ champions read several sensors through physics superposition plus a threshold, noisily. No
evolved champion retains across trials, which the tasks do not reward. The temporal "memory" found (M2)
is a delay line tuned to the fixed gap. Composition (XOR, FLIP) and multi-hop relay are NULL, and it is
UNDETERMINED whether search or physics limits them, because no plant has been built at any physics.
The instruments built over arcs 2-3 (swap census, relative certificates, truth tables, phase
stratification, provenance and difference tracing) are the durable value. Several of their early
readings were corrected by later workers, which the record shows honestly.

## ADDENDUM: H-CHK decisive checks (plan 7e156c12b frozen first; known-answer gate PASS; principal re-ran tests 4/4 and verified the readings)
- C1 PARTIAL (by .0004). A noisy count-threshold plant (readout "+" iff >= 3 payload-1 copies in its last
  wake window; no joint logic) reproduces W-P's signature: JOINT-2 AND/OR share 1.00, the (inbox, Msum)
  pair at o14-15, and the champion's o14/o15 clock-phase split (o14 q1 E .50 vs champion .49). Under
  W-V's frozen classifier it reads DISTRIBUTED-NONMAJ in 9/9 strata, median D_piv .3004 against the frozen
  bar < .3.
  -> "Joint carrier" as a distinct architecture is not supported by the truth tables: a threshold on a
     noisy sum produces them.
- C2 PARTIAL. W-V's majority plant at the champion's loss .1 and fanout-8 sampling reads DISTRIBUTED-NONMAJ,
  D_piv .38-.44 (lossless 1.00).
  -> The DISTRIBUTED-NONMAJ label is not evidence against a noisy majority.
- UNEXPLAINED (do not normalize away): the champion's D_piv (.10-.12) is LOWER than both plants' (.30,
  .38-.44). Loss plus a count threshold does not fully account for 4781b0a1. Candidates: rectification
  strength, the longer effective latency (the champion's readout-bound traffic only acts from o10), or
  sensor-to-sensor relaying.
- C3 NOT CONFIRMED, and the proposed discriminator is itself refuted. A single-cue-twin S swap gives z = -1
  for integrators too (-1.00 [-1,-1]), because the twins receive identical input after the swap tick. So an
  S swap puts world A exactly on B's trajectory, whatever the mechanism. The lag weight shows up in the
  twin-difference RATE (.23-.54, falling with trial index), not in z.
  -> The integrator/store question needs a statistic not normalised by the twin effect: a lag profile, or
     the twin-difference rate.
