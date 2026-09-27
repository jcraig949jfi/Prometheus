# I2 -- Engines that vary substrate physics: unresolved questions

Delegate report for Odysseus, 2026-09-27. Read-only mining of git. Pure ASCII.

Citation shorthand:
- RB = ref origin/aether/research-block-2026-09-27 (tip 3bd6f82b4, unmerged). Read with `git show RB:<path>`.
- PD01 = Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md. PD02 = .../PHYSICS_DESIGN_02_2026-09-26.md.
  PD03 = .../PHYSICS_DESIGN_03_2026-09-27.md (RB only). AUDIT = Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md (RB only).
- CARD = Aether/AETHER_ENGINE_CARD.md (RB only, 7c1724109). REVIEW = Aether/pivot/AETHER_REVIEW_2026-09-27.md (main, ee81c0474).
- C002 = ops/campaigns/C-002/ (RB only). A: = roles/Ananke/. LENS = roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md.
- Line numbers refer to the RB copy for RB files. They refer to the working tree (main) otherwise.
- "INFERRED" marks my reading. "COMPUTED-HERE" marks a stdlib tabulation I ran on committed evidence during this pass (post hoc, descriptive).

-----------------------------------------------------------------------
## Section 1. Territory summary

1. Four engines vary physics instead of organisms: Aether/AGE (local lattice laws), Ananke/PTE (channel physics), Ares (world pressures on a fixed GA substrate) and Bellerophon physics v3 (coupling, peripheral). AC-01 is not substrate physics: it asks whether search over inference frontiers compresses.
2. Aether's central result: under v1 and 8 one-change laws, a one-bit difference stays within about one site. "The substrate lacks propagation" (PD01:32-35, PD01:442-455).
3. The only propagating law, `rcv`, carries activation timing through inert matter, not content: 8% template bytes (PD02:312-325). Without injected perturbation it is horizon-robust to 10,000 ticks at radius 7 (C002/E-005/RESULT.md:100-121).
4. The newest Aether positives exist only in commit messages: `rcv_add` and `rcv_str` passed a preregistered super-additivity test, and `fwd` shows 92% "altered" content. Their data are off-repo or lost (9862cfa9e, fd7ca4fde, 3bd6f82b4).
5. PTE: communication-dependent computation exists but is rare (8/352) and bound to topology (random graph gives 0.500). Its memory bit lives in packets in flight, in a code nobody has decoded (A:pte/c1b/REVIEW_PACKET_PTE_C1b.txt:83-90).
6. Ares: every memory carrier offered works alone. Which one evolution picks tracks parameter basin width, not capability (post hoc). Under attack, lineages built redundancy rather than substituting (ares/ARES_CYCLE2_REPORT.md:60-66, 217-226).
7. Recurring shapes across engines:
   - persistence without propagation;
   - propagation of timing but not of content;
   - a carrier hidden outside the observed state;
   - the physics or parameterisation choosing the mechanism;
   - positives that turn out to be the rule's own definition.
8. Parked:
   - PTE-C2 "weather" and PTE-SI01 (no prereg);
   - Ares cycle 3 arms A/B;
   - Aether's `fwd` write-up, the combination falsifiers, `m4`'s cycle question, and parameter-regime sweeps.

-----------------------------------------------------------------------
## Section 2. Candidate research threads

### T1. Can content (not only activation timing) propagate under a primitive local law without the law encoding the path?
- QUESTION: Is there a local rule under which the VALUE of a difference travels and changes on the way, where the rule does not simply define a message path?
- WHY IT MATTERS: This separates "influence" from "communication". Every Aether positive so far moves who-fired, not what.
- WHAT IS KNOWN:
  - rcv: 269 of 359 secondary differences are the received flag, 75 are energy, 30 (8%) are template bytes and none are opcode (PD02:314-316).
  - REVIEW poses the question itself ("can content propagate under a primitive local law?", REVIEW:564-566).
  - fwd, which relays the received byte, is a declared positive control and "not the sought phenomenon" (PD03:118-125).
- WHAT IS UNKNOWN:
  - Genuine: whether any non-encoding law does it.
  - Missing documentation: PD03 s5 RESULTS is empty (PD03:145-147) although runs happened (9862cfa9e).
- CHEAPEST DISCRIMINATOR: Recover or re-run the E-006 combination units (72 units; CPU, numpy). Then apply `aeth03_content_probe.py` (RB) to split WRITTEN_BOTH / WRITTEN_ONE / PRESERVED / TRANSFORMED.
- LENSES: AGE twin assay with content signature (PD03:18-23). PTE per-carrier resets would be the analogue for packets.
- NEW-LENS SIGNAL: yes. A "content-vs-timing decomposition" of any causal difference is not yet a program-wide instrument.
- RELATED: T2, T3, T13, T17.

### T2. Are the rcv_add / rcv_str "NEW_BEHAVIOUR" verdicts real?
- QUESTION: Do the two combinations that passed preregistered N1/N2 super-additivity survive their own falsifiers? The falsifiers are the content-cause probe and a 10,000-tick horizon run.
- WHY IT MATTERS:
  - This is the only preregistered pass in Aether's physics search. No earlier law passed a JUSTIFY gate (REVIEW:595-597).
  - It bears on REVIEW Q6, which asks whether effects exist only in combination (REVIEW:603-605).
- WHAT IS KNOWN:
  - The commit message 9862cfa9e states the pass and that falsifiers were committed before results.
  - The combinations campaign's 9.2 MB units.tar was fetched, verified and then silently discarded by a 1 MiB cap (fd7ca4fde).
  - The 10,000-tick falsifier results were lost when --resume used the wrong module ($0.04, 3bd6f82b4).
  - The reducer exists (RB:Aether/observatory/aeth03_combinations_reduce.py:15, 92).
- WHAT IS UNKNOWN:
  - Missing documentation: the numbers.
  - Genuine: whether "content" in rcv_add is accumulation counting (add was 83% counting, PD01:436-441), i.e. timing turned into a count.
- CHEAPEST DISCRIMINATOR: Check BUCKKEEP's `<checkout parent>/Prometheus-data/runpod_artifacts` (named in fd7ca4fde) for the re-flown tar. Otherwise re-run the 3 combos plus components at 128^2 on CPU (numpy). In both cases, report WRITTEN_ONE vs WRITTEN_BOTH shares first.
- LENSES: AGE combination reducer; Aether false-friends catalogue ("counting is not change", CARD:171-172).
- NEW-LENS SIGNAL: no. The instrument exists; the evidence path is broken.
- RELATED: T1, T3, T22 (instrumentation).

### T3. Why is 92% of fwd's forwarded content "altered"?
- QUESTION: In a law that relays received bytes verbatim, what changes them? Candidates: contest loss, perturbation, several writes merging (payload > arg1 > arg0 > opcode priority), or timing marks misread as content.
- WHY IT MATTERS:
  - If a supplied pure relay is mostly altered, either the metric is blind or the medium transforms messages endogenously.
  - Endogenous transformation would be the first composition seen.
- WHAT IS KNOWN:
  - The E-P2 trigger was preregistered at >25% altered (PD03:132-135).
  - The observed 92% is reported only in the commit message 9862cfa9e and the probe docstring (RB:Aether/observatory/aeth03_content_probe.py:1-8).
  - The relay-chain fixture scores 21 preserved and 0 altered (PD03:22-23).
- WHAT IS UNKNOWN: The classification result, which is missing. Whether "altered" is dominated by WRITTEN_ONE (a timing mark) is genuinely open.
- CHEAPEST DISCRIMINATOR: Run aeth03_content_probe.py on fwd, OFF arm, 1 seed at 128^2 (numpy, minutes).
- LENSES: AGE content signature.
- NEW-LENS SIGNAL: possibly. The "altered" class may need a cause taxonomy (arrival, presence, merge) usable by PTE too.
- RELATED: T1, T2, T17.

### T4. Can an endogenous mechanism replace injected noise as the timing-to-topology converter?
- QUESTION: Perturbation raises rcv's sustained propagation 4.8x by turning activation differences into template differences, which re-aim relays. Can any noise-free law do that conversion?
- WHY IT MATTERS: Without the conversion, propagation stays local forever. With injected noise it grows sub-ballistically. That makes the substrate's "reach" a property of the environment's noise, not of its own dynamics.
- WHAT IS KNOWN:
  - rcv OFF: P_sust 0.047. rcv ON: 0.227 (PD02:197, 213).
  - The mechanism is reasoned, not measured (PD02:327-337).
  - Horizon run: rcv OFF radius 7/7/7 at +500/+2,000/+10,000. rcv ON radius 17/22/39, with 7/32 regions breached (C002/E-005/RESULT.md:100-105, 118-120).
  - rcv_str was designed exactly for this (PD03:88).
- WHAT IS UNKNOWN:
  - Genuine: whether rcv_str's pass is this conversion (T2).
  - The PD02 mechanism for the 4.8x amplification is "reasoned, not measured".
- CHEAPEST DISCRIMINATOR: With the committed ON/OFF assay files, compare the per-field share of generation >=2 differences (arg0/arg1 vs flag/energy). This is partly stdlib (Section 5, D2). The decisive test is an ON arm with perturbation restricted to non-address fields (numpy).
- LENSES: AGE twin assay; PTE loss/latency dials are the channel-noise analogue.
- NEW-LENS SIGNAL: yes. "Noise as a structural amplifier" recurs (T11, PTE loss 0.6 SIGNAL, T18). No engine measures it as its own axis.
- RELATED: T11, T18.

### T5. Is rcv's propagation percolation on a quenched (frozen) map?
- QUESTION: Is rcv reach explained by the connectivity of a frozen relay graph? The graph is inert sites plus fixed arg0 directions. The alternative is any dynamics.
- WHY IT MATTERS: If reach is percolation on a quenched landscape, "propagation" is a static-graph property. It would say nothing about history, which the program cares about.
- WHAT IS KNOWN:
  - The same origin flipped at +0, +200 and +400 ticks gives identical footprints (Jaccard 1.0, 24/24 pairs). About 93% of template bytes are frozen without perturbation (e67dd06bc).
  - Committed file: RB:Aether/AETH-03/evidence/2026-09-27_rcv_paths/rcv_paths_s1.json.
  - A different bit at the same site gives Jaccard 0.72-0.77 (same commit).
  - The relay is a random walk that ends at starved or out-competed sites (reasoned, PD02:327-331).
- WHAT IS UNKNOWN:
  - Genuine: whether the cluster-size distribution of the relay graph predicts P_esc and P_sust.
  - Genuine: whether some regime sits near a percolation threshold. No criticality measurement exists anywhere in this territory (grep found only unrelated agent-tool hits).
- CHEAPEST DISCRIMINATOR: Replay one warmed 128^2 rcv world (numpy). Build the static relay digraph (inert-receipt adjacency via arg0 mod 4). Correlate out-component size with each origin's max radius from committed prop_rcv_*.json.
- LENSES: none fits exactly. A percolation or criticality lens is absent in Prometheus.
- NEW-LENS SIGNAL: yes, strong. "Quenched-landscape vs dynamic propagation" and "distance to percolation threshold" as a sweep axis.
- RELATED: T4, T11.

### T6. Is mutual energy supply the only self-maintaining relation, and could it bound a region?
- QUESTION: Energy-field 2-cycles, where each member feeds the other, are enriched 1.58x over null. Persistently fed sites carry most long-lived edges. Do mutual-supply clusters satisfy rung 1 of the card's assembly ladder: "a bounded region whose state persists because of its own internal interactions"?
- WHY IT MATTERS: Mutual supply is the only candidate in the record for an individual emerging without a predefined organism.
- WHAT IS KNOWN:
  - Sustained inflow cut drops persistence at +128 to 0.39/0.40 of sham (PD01:133-141).
  - Energy 2-cycles are enriched 1.579x vs rewire null. Opcode is 0.003x and arg1 0.002x (PD01:161-165, 195-197).
  - The feeding relation onto a site recurs even though individual energy edges have hazard ~0.80 (PD01:149-153).
  - CARD s3: no rung observed (CARD:60-68).
- WHAT IS UNKNOWN:
  - Genuine: whether supply loops persist through their own interaction or are just uncontested. NATIVE_CIRCUITRY found no persistent edge had a competitor (Aether/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md:393-400).
  - Nobody has lesioned one member of a supply 2-cycle.
- CHEAPEST DISCRIMINATOR: Replay v1 at 256^2 (numpy). Identify energy 2-cycles. Lesion one member's energy for k ticks against a size-matched sham, and measure the partner's survival and whether the loop re-forms.
- LENSES: AGE lesion/sham arms. The Archaeon causal lens is not applicable (no births).
- NEW-LENS SIGNAL: yes. "Self-maintenance by internal flux" as a boundary criterion has no instrument.
- RELATED: T7, T15.

### T7. Why do cycle members persist less than non-members in the same field?
- QUESTION: At fixed field, cycle members' one-tick out-edge persistence is lower than non-members': arg0 0.587 vs 0.755, opcode 0.34 vs 0.63, energy 0.919 vs 0.987. Cycle membership costs 0.07-0.29 per tick.
- WHY IT MATTERS: It is the one H3 sub-prediction that failed with no cause established. It bears on whether closed loops are penalised by the physics, which would be anti-structure.
- WHAT IS KNOWN: H3-P3 was FALSIFIED. The candidate cause ("a 2-cycle member's out-edge needs its own writer to stay put") is untested and not claimed (PD01:203-210).
- WHAT IS UNKNOWN: The cause. This is a genuine gap.
- CHEAPEST DISCRIMINATOR: The existing closure instrument (Aether/observatory/aeth02_closure.py) with a conditional split on whether the member's own writer changed that tick (numpy, 256^2).
- LENSES: AGE.
- NEW-LENS SIGNAL: no.
- RELATED: T6, T8.

### T8. Without the K2 perturbation channel, do arg1-mediated cycles persist? (m4's original question, never asked)
- QUESTION: The one H3 mechanism that runs through perturbation (every single-bit flip of arg1 changes arg1 mod 5): does removing it let cyclic structure persist?
- WHY IT MATTERS: It tests whether perturbation's address-scrambling is what destroys structure. That is a physics-design rule for any substrate with addressed writes.
- WHAT IS KNOWN:
  - H3-X: arg1 cycle edges retain 0.40 with perturbation off vs 0.095 on (PD01:191-194).
  - m4 was assayed only for propagation, and "its original question ... was not asked here and remains open" (PD02:344-347).
  - REVIEW lists it as candidate science c (REVIEW:543-544).
- WHAT IS UNKNOWN: The result. Nothing blocks it; it has simply not been run.
- CHEAPEST DISCRIMINATOR: Run the H3 closure battery under m4 at 256^2 (numpy, CPU).
- LENSES: AGE.
- NEW-LENS SIGNAL: no.
- RELATED: T7, T4.

### T9. Is there a regime (write cost, replenishment, perturbation rate) where propagation changes character?
- QUESTION: Every Aether propagation number comes from one parameter regime (B-balanced, Mu 0.1). Does rcv's weak reach turn into sustained reach, or into saturation, as a dial moves? Is there a transition?
- WHY IT MATTERS: With one regime, "the substrate lacks propagation" is a point estimate. A phase boundary would be the first criticality evidence in the territory.
- WHAT IS KNOWN:
  - "Nothing was tuned, and nothing was varied either" (REVIEW:471-472).
  - FIRST_LIGHT H5 says the perturbation axis was untested (Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md:384-390).
  - REVIEW candidate b names this fan-out (REVIEW:541-542).
  - The PTE analogue exists: RELAY plant viability is 19/245 at decay 0 and 0/755 otherwise, "an AND of gates" (A:pte/c1_a0/A0_FINDINGS.md:44-50).
- WHAT IS UNKNOWN: The result is a genuine gap. My grep of RB for follow-ups found none.
- CHEAPEST DISCRIMINATOR: A 1-D sweep of Mu in {0, .025, .05, .1, .2, .4} on rcv, 128^2, 2 seeds, 32 origins (numpy; about 70 s per 4-origin slice on a pod core, C002/E-007/TASKS.md:149).
- LENSES: AGE twin assay. The PTE A0 census style (dial tree) could be borrowed.
- NEW-LENS SIGNAL: yes. A shared "habitability or phase map" format across AGE and PTE.
- RELATED: T4, T5, T10, T18.

### T10. Does contest-destroyed energy put every world on a clock, and is there a density above which no inflow sustains it?
- QUESTION: v1 loses energy even at zero cost, because losers' transfers are destroyed. Does the loss rate scale with contest density, giving a maximum sustainable activity?
- WHY IT MATTERS: It is a thermodynamic-style ceiling on how much "computation" a substrate can host. It would be the analogue of an energy budget limiting structure.
- WHAT IS KNOWN:
  - Regime C_free_compute loses 3.04% of energy in 5,000 ticks (FIRST_LIGHT_01:188-194).
  - The mechanism is documented (FIRST_LIGHT_01:300-313; Aether/AETH-01/ECONOMICS.md:18).
  - H6 proposes the measurement (FIRST_LIGHT_01:392-398).
  - Gini rises in all regimes: B goes 0.364 -> 0.588 (FIRST_LIGHT_01:196-200).
- WHAT IS UNKNOWN: The loss-rate vs density curve. No follow-up was found in RB.
- CHEAPEST DISCRIMINATOR: A CPU scout at 128^2, sweeping initial WRITE density and logging the contest-loss energy per tick (numpy).
- LENSES: AGE energy accounting (closed identity, CARD:112).
- NEW-LENS SIGNAL: weak. An energy-dissipation-per-interaction observable across engines (PTE has economy dials; A:pte/C1_REPORT.md:89-91).
- RELATED: T6, T9.

### T11. Is "no law passed" a property of the physics or of the bar?
- QUESTION: Two rounds and 9+ laws produced no JUSTIFY pass until the unverified combos. Were the thresholds calibrated against a law known to propagate?
- WHY IT MATTERS: Negative science is only informative if a positive could have passed.
- WHAT IS KNOWN:
  - REVIEW Q3 asks this (REVIEW:595-597).
  - The relay-chain positive control is a fixture, not a soup law (PD02:126-128).
  - fwd was introduced as the first soup-level positive control with E-P1 ">= 2x rcv and >= 0.05" (PD03:127-131). Its result is not in git.
- WHAT IS UNKNOWN: fwd's E-P1 outcome (missing documentation).
- CHEAPEST DISCRIMINATOR: Report fwd E-P1 from recovered data, or re-run fwd OFF at 128^2 (numpy).
- LENSES: AGE. CWE's planted-truth recovery (LENS:128-129) is the model.
- NEW-LENS SIGNAL: no. It is borrowable from CWE.
- RELATED: T2, T3.

### T12. Is joint causation's near-absence the signature of "no composition"?
- QUESTION: Across 2,793 audited events, only 2 needed two differing parents jointly; differences are caused one parent at a time. Is a substrate able to compute if joint causation is about 0?
- WHY IT MATTERS:
  - Composition (two inputs needed together) is the minimal ingredient of non-trivial computation.
  - A per-law joint-causation rate is a candidate universal observable.
- WHAT IS KNOWN:
  - AUDIT:117-119 (joint 2/2,793). AUDIT:98-104 per law: rcv ON has 2 joint events out of 1,254.
  - PTE's XOR/FLIP null is attributed to superposition plus an unassembled two-stage composition (A:pte/C1_REPORT.md:119-124).
- WHAT IS UNKNOWN:
  - Genuine: whether any law (add, rcv_add) raises joint causation.
  - Genuine: whether PTE's summed arrivals structurally prevent it.
- CHEAPEST DISCRIMINATOR: Run `aeth03_assay_audit.py parents` on add, rcv_add and fwd (numpy). Compare the joint share. Mark INFERRED that this is a composition proxy.
- LENSES: AGE counterfactual parent audit.
- NEW-LENS SIGNAL: yes, strong. "Joint-causation rate" as a composition meter, portable to PTE (packets as parents) and to Z80 engines (CARD:180-183 proposes porting the twin).
- RELATED: T1, T19.

### T13. What is the complete causal state? Hidden carriers break twin assays in two engines.
- QUESTION: Each engine's twin assay compares a subset of state. How much propagation and memory lives in the uncompared remainder?
- WHY IT MATTERS: Both engines' "local / not beyond one hop" verdicts may be artefacts of predicate scope. Any claim about "where information is" depends on it.
- WHAT IS KNOWN:
  - Aether: a flag-only twin produced visible differences in 20/20 trials. A bytes-only predicate records 32 locality violations; the full predicate records 0 (AUDIT:35-38). The structural fix is World.extra (AUDIT:130-132).
  - PTE: the twin assay tracks only S (prometheus/ananke/assays.py:233-285, per the Ananke sub-report). 3 of 4 causal RELAY cells show beyond_hop 0.0 while being COMM_DEPENDENT (A:pte/c1_report/REPORT.md, wave D twin lines). The link is INFERRED: in-flight carriage is invisible.
  - PTE M2's carrier IS in-flight packets (flush mid-gap gives 0.497) (A:pte/c1b/REVIEW_PACKET_PTE_C1b.txt:85).
- WHAT IS UNKNOWN: How PTE's twin verdicts change with packets in the predicate. This is genuine, but the evidence to compute it is not stored.
- CHEAPEST DISCRIMINATOR: Stdlib, from A:pte/c1_rows/cells.jsonl.gz: cross-tab `twin.beyond_hop` against `held.comm_delta` over evolve rows (Section 5, D4). The decisive test extends PTE's twin predicate to the packet queue (torch/numpy).
- LENSES: AGE assay audit (state-scope attack). The PTE per-carrier resets.
- NEW-LENS SIGNAL: yes. A "predicate-completeness audit" as a mandatory step for any twin or light-cone instrument.
- RELATED: T1, T16, T17.

### T14. Locality vs horizon vs area: are slow processes missed at 128^2-256^2?
- QUESTION: OFF-arm locality holds to 10,000 ticks at 256^2. Does it hold at 4096^2 over 10^5 ticks, and below the 64-site resolution FIRST_LIGHT recorded?
- WHY IT MATTERS: It bounds the claim "lacks propagation".
- WHAT IS KNOWN:
  - E-005 is CLOSED as horizon-robust (C002/E-005/RESULT.md:107-110).
  - add OFF shows the only late movement: one origin went from radius 3 to 5 between +5,000 and +10,000 (RESULT.md:116-117).
  - FIRST_LIGHT kept only 64x64 block maps. Structure under 64 sites is unrecoverable except by replay (FIRST_LIGHT_01:236-243, 371-377).
  - FIRST_LIGHT B_balanced was right-censored at 5,000 ticks (FIRST_LIGHT_01:352-360). NATIVE_CIRCUITRY later ran 2048^2 x 50,000 (NATIVE_CIRCUITRY_01:31-37).
- WHAT IS UNKNOWN: Genuine: whether the add slow creep continues.
- CHEAPEST DISCRIMINATOR: Stdlib: per-origin radius-vs-horizon trajectories for add OFF from C002/E-005/attempts/*.json (Section 5, D3). Extending add OFF to 50,000 ticks needs numpy.
- LENSES: AGE long-horizon instrument.
- NEW-LENS SIGNAL: no.
- RELATED: T9.

### T15. What minimal physics would produce a bounded individual? Aether's three-rung ladder is unoccupied.
- QUESTION: What is the smallest law change under which a region persists by internal interaction, influences outside it, and is reproduced elsewhere by dynamics (not by a copy rule)?
- WHY IT MATTERS: This is the emergence-of-individuals question the program cares most about. Aether is the only engine where it is asked without a predefined organism.
- WHAT IS KNOWN:
  - None of the 3 rungs has been observed (CARD:60-68).
  - "Mutual constructors / RECURSIVE_CONSTRUCTION ... not yet designed" as detectable predicates (Aether/AETHER_OPEN_QUESTIONS.md:134-137).
  - FIRST_LIGHT: 0 detectors existed to run, and "zero means not measured" (FIRST_LIGHT_01:219-231).
  - PD01 rejected "pull semantics" as a new ontology, deferred (PD01:464-466).
- WHAT IS UNKNOWN:
  - Genuine.
  - Missing instrumentation: no rung-1 detector is implemented.
- CHEAPEST DISCRIMINATOR: Implement a rung-1 test as T6's lesion on supply clusters. That is the only candidate structure with a known self-feeding mechanism.
- LENSES: none fit. The Archaeon causal lens needs births. AGE has no region-level predicate.
- NEW-LENS SIGNAL: yes. A "region self-maintenance under lesion vs matched null" instrument.
- RELATED: T6, T7.

### T16. What code carries PTE's in-flight memory bit (M2)?
- QUESTION: Flushing packets mid-gap kills M2's held bit (0.497), yet the signed payload sum in flight does not predict it (0.44, perm p 0.998). What property of the traffic encodes the bit?
- WHY IT MATTERS: It is the clearest case in the program of memory held in transit (memory as propagation), and its code is unknown.
- WHAT IS KNOWN:
  - The M2 arms: normal 0.883, reset w 0.817, flush 1 tick pre-readout 0.853, readout-tick census 0.50 (A:pte/c1b/REVIEW_PACKET_PTE_C1b.txt:83-90).
  - The label is IN_FLIGHT_PLUS_JOINT_UNRESOLVED (same file:90).
  - Timing, count and destination are named as untested candidates (same file:171-172, per the sub-report).
- WHAT IS UNKNOWN: The code. This is genuine.
- CHEAPEST DISCRIMINATOR: Replay the M2 champion 4ab2ba01 (torch or numpy oracle). Log the packet count per destination and the latency class at mid-gap, then fit single-feature predictors with a permutation null.
- LENSES: PTE per-carrier resets. The AGE content signature is the analogue.
- NEW-LENS SIGNAL: yes. A "code decoder for a carrier" (which features of a carrier predict the stored bit) is absent program-wide.
- RELATED: T13, T17.

### T17. Where does M2's bit go in the last tick before readout?
- QUESTION: A flush mid-gap destroys the bit (0.497), but a flush 1 tick before readout barely hurts (0.853). The readout-tick census reads 0.50. Which carrier holds the bit at t-1?
- WHY IT MATTERS: It is a carrier hand-off, from in-flight to something else, that nobody has named. A hand-off between propagation and storage is a physics-of-memory primitive.
- WHAT IS KNOWN: The numbers above (REVIEW_PACKET_PTE_C1b.txt:85-86). The C1 errata show that the ablation window must include the readout tick (A:pte/C1_ERRATA.md:6-14).
- WHAT IS UNKNOWN: Genuine, and unexplained in the packet (the sub-report flags this as INFERRED).
- CHEAPEST DISCRIMINATOR: Per-carrier resets (S, inbox, w, Kp, En, r) applied at t-1 only, from the C1b harness (torch/numpy).
- LENSES: PTE.
- NEW-LENS SIGNAL: no.
- RELATED: T16, T13.

### T18. Is geometry the substrate's "body"? RELAY laws die on a random graph.
- QUESTION: Every routed-relay law collapses to 0.500 on a random graph. Can geometry-free transport evolve under mixed-topology training, or is lattice geometry a required ingredient?
- WHY IT MATTERS: It tests whether communication-dependent computation needs spatial locality as a resource. That links directly to Aether's locality findings.
- WHAT IS KNOWN: Frozen RELAY laws score 0.875/0.893/0.882 at N=400/1024/2304, but 0.500 on a random graph, and cross-family transfer is 0 (A:pte/C1_REPORT.md:125-128; LENS:208-210). F2 states the fork: evolve across mixed topologies, or accept geometry (A:pte/C1_REPORT.md:125-128).
- WHAT IS UNKNOWN: Genuine.
- CHEAPEST DISCRIMINATOR: Stdlib: tabulate the evolve rows in cells.jsonl.gz by topology x SIGNAL (Section 5, D5). The decisive test is a mixed-topology evolve arm (GPU/torch).
- LENSES: PTE. AGE lattice twin (always lattice).
- NEW-LENS SIGNAL: weak.
- RELATED: T9, T19.

### T19. Influence vs function: why is distal influence 20-35x rarer than perturbability in PTE, and 1 hop in Aether?
- QUESTION: PTE A0 finds L1 perturbability in 11-23% of cells but L2 distal influence in 0.3-0.7%. Is this the same phenomenon as Aether's "a write changes the neighbour's behaviour only if it lands in its own arguments"?
- WHY IT MATTERS: The "reactivity vs functional transport" gap appears independently in two engines. It may be a general law of local substrates, or two different artefacts.
- WHAT IS KNOWN:
  - PTE: A:pte/c1_a0/A0_FINDINGS.md:11-22. A0 cannot separate "physics cannot carry" from "random programs rarely relay" (same file:23-28).
  - Aether: PD01:442-450 ("v1's causal influence is one hop").
  - Aether also has the absorbing case: of 128 origins, 63 v1 flips were INERT (PD02:194).
- WHAT IS UNKNOWN: Whether a common cause exists. INFERRED: both are "receivers re-emit their own content, not what they received".
- CHEAPEST DISCRIMINATOR: Stdlib: from the Aether assay JSONs, INERT/DIRECT/SECONDARY by flipped field (Section 5, D1). From PTE rows, L1 vs L2 by family. The goal is to see whether the influence gap concentrates in address-like fields.
- LENSES: AGE twin; PTE L-ladder.
- NEW-LENS SIGNAL: yes. A cross-engine "reactivity-to-transport ratio" observable.
- RELATED: T1, T12, T18.

### T20. XOR/FLIP null in PTE: substrate capacity or search budget?
- QUESTION: PTE has GT, SEL, MAX, XOR and MOD opcodes, yet 0 of 165 evolve cells solved XOR or FLIP. Is superposition (summed arrivals, no source identity) a physical barrier, or is the two-stage composition just unfound?
- WHY IT MATTERS:
  - It decides whether "communication-dependent computation" is limited to linear aggregates under superposing channels.
  - LENS:203-204 states PTE is unsuitable for non-linear computation. The sub-report flags this as a contradiction with DESIGN.md:176-189.
- WHAT IS KNOWN: A:pte/C1_REPORT.md:119-124 (F1). ANANKE-10 port-resolved arrival is parked (A:BACKLOG_H0H5.md, per sub-report :47).
- WHAT IS UNKNOWN: Genuine.
- CHEAPEST DISCRIMINATOR: A hand-built positive control. Write an XOR program with port-resolved arrival disabled, and check whether the physics can express it at all. That is a capacity test and needs no search (CPU oracle, numpy).
- LENSES: PTE. The AGE joint-causation audit (T12) would read it directly.
- NEW-LENS SIGNAL: yes. The "expressibility certificate vs discoverability" split is recurrent (see T23).
- RELATED: T12, T23.

### T21. PTE-C2 "weather": does load (traffic density, concurrent cues, conflict) break or create communication-dependent computation?
- QUESTION: As designed in the backlog: three separate load axes, targeting rung L5.
- WHY IT MATTERS: Channel contention is the communication-physics analogue of Aether's contest loss (T10). It is untested.
- WHAT IS KNOWN:
  - Backlog item ANANKE-26 (A:BACKLOG_H0H5.md:63).
  - No prereg exists. Prerequisites: an amended boundary rule, ablation-fingerprint labels, an env no-op guard, and a habitable zone taken from causally verified cells, NOT A0 viability (A:pte/C1_REPORT.md:153-157; A:RESUME.md s4).
  - Proposed $10 RunPod ceiling pending operator Q3 (A:RESUME.md s5).
- WHAT IS UNKNOWN: Everything; it has not been run.
- CHEAPEST DISCRIMINATOR: Write the prereg first. The known habitable cells (RELAY bbef66a1, M2 4ab2ba01) are the substrate. Start with a single density axis on CPU oracle at small N.
- LENSES: PTE.
- NEW-LENS SIGNAL: no.
- RELATED: T10, T22.

### T22. PTE-SI01: do distinctions stop being accessible exactly when they stop mattering?
- QUESTION: With repeated HOLD, distinction classes R (relevant), E (expired) and N (nuisance), no reset, and the complete causal state including packets in flight: is expired information merged or still accessible?
- WHY IT MATTERS: It is a test of selective forgetting as a physical property. It is to be read beside Ensorain LM01 (ensorain/lm01/STEWARD_RULINGS.md:94, per sub-report).
- WHAT IS KNOWN:
  - The directive text is at A:prompts/2026-09-25_pte_si01_directive/01_STEWARD_DIRECTIVE_verbatim.md:127-280.
  - Ananke's objections O1-O4 are at A:prompts/2026-09-25_pte_si01_directive/02_REPLY_TO_STEWARDS.md. O1: relevance is confounded with recency. O4: E's utility is zero by definition.
  - Gates reverted to the operator (roles/Aporia/journal/2026-09-26.md:205-213).
- WHAT IS UNKNOWN: Everything. No prereg exists.
- CHEAPEST DISCRIMINATOR: The O1 fixture (crossed interleaved streams plus a FIFO fixture) is a zero-evolution check. It asks whether recency alone predicts accessibility.
- LENSES: PTE. The WTP/LM01 arm.
- NEW-LENS SIGNAL: yes. "Accessibility vs utility across the complete causal state" is a new observable.
- RELATED: T13, T16.

### T23. Does parameterisation basin width, not capability, decide which carrier or mechanism a substrate yields?
- QUESTION: In Ares, all three memory carriers are individually sufficient. Recurrence wins on basin width (viable in 14/23 of its sweep, saturating) over keep, which has a higher peak (33.75 vs 24.56) but is viable in only 3/25. Is basin width a general predictor across substrates?
- WHY IT MATTERS: If it holds, "what evolution finds" reports the substrate's parameter geometry, not the problem's demands. That is a design rule for every engine.
- WHAT IS KNOWN:
  - ares/ARES_CYCLE2_REPORT.md:15-23, 91-99, 136-140, 160-167. The explanation is post hoc and measured on hand-wired organisms (:164-167).
  - Parallel: PTE's HOLD search on RELAY physics produced a delay line, and "the physics, not the search, chose the carrier" (A:calibration/LEDGER.md, 2026-09-26 C1b-P5 row, per the sub-report).
- WHAT IS UNKNOWN: Genuine.
  - Ares parks Arm A (decouple the leak, v = keep*v + f; predict keep load-bearing >= 5/10) and Arm B (re-parameterise keep as 1-exp(-r)) (roles/Ares/TODO.md:60-68).
  - Q4, a test on another seat's substrate, is operator-only.
- CHEAPEST DISCRIMINATOR: Ares Arm B. The same function under a different parameterisation should flip carrier preference if basin width is causal (numpy, CPU; about 10 lineages).
- LENSES: Ares present/absent/shuffled plus forbid-arms.
- NEW-LENS SIGNAL: yes. A "basin-width census of primitives" for AGE laws and PTE opcodes.
- RELATED: T20, T24.

### T24. Why does attack produce redundancy rather than substitution?
- QUESTION: Under W15 (reset events), lineages kept recurrence load-bearing in 8/10, made plasticity load-bearing in 7/10, and raised median recurrent edges from 2.0 to 9.0. Is redundancy selected, or a by-product of a harder task?
- WHY IT MATTERS: Robustness by redundant carriers is a candidate "physics of persistence" rule. Ares calls it "the only result here that pointed somewhere nobody predicted".
- WHAT IS KNOWN: ares/ARES_CYCLE2_REPORT.md:62-66, 222-226.
- WHAT IS UNKNOWN: Genuine.
- CHEAPEST DISCRIMINATOR: Stdlib: from ares/runs/sweep_c2/*.json logs, check whether struct_div and behav_div trajectories diverge for W15 vs W4 before redundancy appears (Section 5, D6).
- LENSES: Ares dissection/graft.
- NEW-LENS SIGNAL: weak.
- RELATED: T23.

### T25. Does a supplied pressure or rule register as a "discovery"? The author-plants-the-law shape in substrate engines.
- QUESTION: Aether rcv (its relay is its definition), CWE law A (97.5% agreement with the task economics), AC-01 v2 (an exact closed-form S_7 orbit quotient) and the PTE plant boundaries ("properties of the hand design") all turned headline positives into rediscovery. Can a substrate engine be designed so its positives cannot be restatements of its rules?
- WHY IT MATTERS: It is a precondition for any claim of capability that "was not explicitly installed".
- WHAT IS KNOWN:
  - PD02:356-365.
  - REVIEW Q2 ("is activation timing simply the definition of rcv restated?", REVIEW:591-594).
  - LENS:136-138 (CWE).
  - alien_circuitry/AC01D_V2_RECEIPT.md:5-20 (per sub-report).
  - A:pte/C1_REPORT.md:85-101 (13 SUPPORTED boundaries are hand-design properties, per sub-report).
- WHAT IS UNKNOWN: Whether a formal "encodes-its-own-positive" test exists. None was found.
- CHEAPEST DISCRIMINATOR: For each AGE law, compute the effect with the rule's defining primitive ablated only where it fires on the difference path. PD02 s4.2's partial-ring is the template (PD02:282-300).
- LENSES: CWE sealed holdouts; AGE partial interventions.
- NEW-LENS SIGNAL: yes. A "rule-restatement test".
- RELATED: T1, T11.

### T26. Why does evolution find transport outside the region a human design needs, in PTE?
- QUESTION: L3 SIGNALs appear where designed plant viability is 0%: a RELAY SIGNAL at loss 0.6, where the design scores 0/253, and MAJ at decay 3 and 6, where it scores 0/755. What do the evolved programs exploit?
- WHY IT MATTERS: "Evolved capability exceeds designed habitability" is direct evidence of capability not installed.
- WHAT IS KNOWN: A:pte/C1_REPORT.md:50-55 (L2 and L2' disjoint, 0 of 7). Seeding in "living" A0 cells gave no advantage (A:pte/C1_REPORT.md:56-58).
- WHAT IS UNKNOWN: The mechanism of those out-of-zone champions. This is genuine.
- CHEAPEST DISCRIMINATOR: Stdlib: pull the champion genomes and held metrics for those cells from cells.jsonl.gz. Diff their opcode usage against in-zone RELAY champions (Section 5, D5).
- LENSES: PTE.
- NEW-LENS SIGNAL: weak.
- RELATED: T18, T20.

-----------------------------------------------------------------------
## Section 3. Anomalies and reversals

| # | What | Evidence | Failure shape |
|---|---|---|---|
| 1 | AETH-02 "edges live 3.1x shorter than independence" | PD01:94-114 | Null model missing a physical term (source starvation, 89% of hazard) |
| 2 | H2-P2 conditioned null under-predicted the long cohort 6-7x | PD01:115-119 | Over-correction, opposite sign. Residual = neighbour energy supply (0.39x sham) |
| 3 | Opcode change rate +128% | calibration LEDGER 2026-09-24 row (RB:roles/Aether/calibration/LEDGER.md) | Stale comparator (prev refreshed every 250 ticks). An identity mistaken for a validation check |
| 4 | "State-changing enrichment on cycles 1.97x" | PD01:215-221 | Simpson's paradox via the enriched energy field |
| 5 | H3-P2 predicted wrong fields; arg1 most suppressed (0.002x) | PD01:174-178; LEDGER 2026-09-26 | Prediction ignored the perturbation phase (K2 mod-5 property) |
| 6 | H3-P3: cycle members persist less | PD01:203-210 | Unexplained; open |
| 7 | Full-ring starvation "falsifier" 0/128 vs 17/128 | PD02:266-280; LEDGER | Intervention forced by the law's semantics, a check rather than a test (second occurrence after the clamp firewall) |
| 8 | "Generation = exact shortest causal chain" | AUDIT:17-25 | Withdrawn. Adjacency is a lower bound (84% exact for rcv ON). One-directional error |
| 9 | Bytes-only twin predicate | AUDIT:35-38 | Hidden carried state produced 32 false locality violations |
| 10 | v1 reaches generation 56 at radius 3 | PD02:246-252 | Generation depth without reach (re-entry flicker). "Generation is not reach" |
| 11 | rcv footprints identical across +0/+200/+400 | e67dd06bc; rcv_paths_s1.json | Propagation on a quenched map, not history |
| 12 | add's endogenous change: 83% counting | PD01:434-441 | Rule restated as a gain (counting is not change) |
| 13 | mov: 41% of differences die | PD02:219-222 | Conservation erases the difference it moves |
| 14 | rcv_add / rcv_str NEW_BEHAVIOUR; fwd 92% altered | 9862cfa9e | Unverified. Evidence discarded (fd7ca4fde: receipt PASS, science gone). 10k falsifier lost (3bd6f82b4) |
| 15 | Zero-cost regime leaks 3% of energy | FIRST_LIGHT_01:188-194, 300-313 | Documented sink (contest loss) newly quantified. Every world on a clock |
| 16 | Regime A dies full of writers | FIRST_LIGHT_01:340-342 | Universal insolvency with the ensemble intact. DEAD_CERTIFIED definition lacked this case |
| 17 | PTE C1 ablation window missed the readout tick | A:pte/C1_ERRATA.md:6-14 | Perturbation window excluded the causal moment. Null vacuous by construction |
| 18 | PTE frozen routing vacuous under dest_mode "all" | A:pte/C1_ERRATA.md:15-19 | Ablated a variable never read |
| 19 | PTE M3 "self-modifying timing memory" | REVIEW_PACKET_PTE_C1b.txt:194-199 (per sub-report) | Reversed to transport landing on the readout tick (memory to propagation) |
| 20 | PTE M2 bit not predicted by signed sum (0.44) | REVIEW_PACKET_PTE_C1b.txt:89 | Carrier known, code unknown |
| 21 | PTE M2 flush asymmetry (0.497 mid-gap vs 0.853 at t-1) | REVIEW_PACKET_PTE_C1b.txt:85-86 | Unexplained hand-off |
| 22 | PTE twin beyond_hop 0.0 in COMM_DEPENDENT cells | A:pte/c1_report/REPORT.md wave D (per sub-report) | Predicate scope blind to in-flight carriage (INFERRED) |
| 23 | PTE exact env balance let "copy last teacher" score 0.346 | A:calibration/LEDGER.md row 1 (per sub-report) | Environment construction leaked an exploitable anti-correlation |
| 24 | PTE M4 integration 0.789 did not reproduce (0.636, 0.520) | A:pte/C1_REPORT.md:80-82 (per sub-report) | Single-specimen positive |
| 25 | Ares "plasticity 0/10" became 4/10 | ares/ARES_CYCLE2_REPORT.md:171-188 | Coarse ablation plus lineage sampling. About 0.6% probability; not fully explained |
| 26 | Ares "10 seeds" = 7 independent | ares/ARES_CYCLE1_REPORT.md:29-37 (per sub-report) | Seed namespace collision |
| 27 | Ares gate C flipped by a best-of-9 swap statistic | ares/ARES_CYCLE2_REPORT.md:72-86 (per sub-report) | Selection-on-max statistic. gates.txt still prints OPEN |
| 28 | Ares held-out selection bias (shuffled controls 4.22/13.47) | ARES_CYCLE2_REPORT.md:192-202 (per sub-report) | Champion chosen on the evaluation set |
| 29 | Ares c2_recur_unstable (jitter on recurrent edges) fastest arm | ARES_CYCLE2_REPORT.md:147-151 (per sub-report) | Noise helping search. Unexplained |
| 30 | AC-01 C5 (0.91) was an approximation of an exact S_7 orbit table (0.998) | alien_circuitry/AC01D_V2_RECEIPT.md:5-20 (per sub-report) | Learned model rediscovered known symmetry |
| 31 | AC-01 datalog universe: 0 traps | alien_circuitry/DATALOG_FAILURE.md:17-55 (per sub-report) | Monotone physics cannot trap. Theorem: needs irreversible AND non-monotone actions |

-----------------------------------------------------------------------
## Section 4. Recurring shapes (with evidence)

S1. PERSISTENCE WITHOUT PROPAGATION.
- Aether v1: 1.2% of edges persist 50,000 ticks (NATIVE_CIRCUITRY_01:388-390), yet influence is one hop (PD01:442-450).
- A lesioned persistent edge is never repaired or replaced (AETH-02_CLOSE:51-77).
- Persistence here is the absence of opposition (NATIVE_CIRCUITRY_01:393-400).

S2. PROPAGATION WITHOUT CONTENT (timing, not value).
- Aether rcv: 92% who-fired/energy, 8% content (PD02:312-325).
- PTE M3: timing memory reversed to transport arriving on the readout tick (C1b packet, per sub-report).
- PTE M2: carrier known, content code not the payload sum (0.44).
- INFERRED common form: the channel carries "that something happened", not "what".

S3. THE CARRIER HIDES OUTSIDE THE OBSERVED STATE.
- Aether flag-only twins: 32 false violations under a bytes-only predicate (AUDIT:37).
- PTE: in-flight packets hold M2's bit, while its twin assay compares only S (T13).
- PTE C1 memory ablation reset only S (C1_ERRATA:20-22, per sub-report).
- The Ares cycle-1 ablation could not separate keep from recurrence (CYCLE2:181-183).

S4. THE ENVIRONMENT OR NOISE DOES THE WORK.
- Perturbation supplies ~42% of template change immediately and ~95% cumulatively (AETH-02_CLOSE:297-298).
- Perturbation amplifies rcv 4.8x and is the only source of horizon growth (E-005).
- Energy inflow from neighbours powers long edges (PD01:126-148).
- PTE environments leaked a solvable anti-correlation (T-row 23).
- Ares c2_recur_unstable: jitter was the fastest arm.

S5. THE PHYSICS OR PARAMETERISATION CHOOSES THE MECHANISM, NOT THE TASK.
- Ares basin width (CYCLE2:217-221). PTE "the physics, not the search, chose the carrier" (LEDGER, per sub-report).
- Aether: the direction/field decode (arg0 mod 4, arg1 mod 5) decides which flips are inert.
- COMPUTED-HERE (Section 5, D1): arg0 flips were INERT in 19/28 origins in every law.
- INFERRED: bits the mod-4 decode ignores are invisible to the physics.

S6. THE POSITIVE IS THE RULE RESTATED.
- rcv relay (PD02:356-365); add counting (PD01:436-441); CWE law A 97.5% (LENS:136); AC-01 exact quotient; PTE 13 SUPPORTED boundaries are hand-design properties.

S7. THE INTERVENTION IS FORCED BY THE SEMANTICS.
- The Aether full-ring starvation and the clamp firewall (LEDGER).
- PTE: the ablation window that could only yield NOT_SUPPORTED, and frozen routing on an unread variable (C1_ERRATA).

S8. THE EVIDENCE PATH, NOT THE SCIENCE, FAILS.
- Aether: combination data discarded after a verified PASS; 10k falsifier lost; PD03 results empty; STATUS stale.
- PTE: STATUS stale; 0 Atlas experiments (LENS:216-217).
- Ares: 7 messages, 0 replies (STATUS:33-35, per sub-report).
- New shape, not in the brief: "receipt PASS / science gone".

S9. ONE-PARENT CAUSATION (new shape).
- Joint causation in Aether is 2/2,793 (AUDIT:117-119).
- PTE cannot assemble XOR under superposition (F1).
- INFERRED: substrates where each difference has a single sufficient cause do not compose.

S10. DESIGNED HABITABILITY != EVOLVED POSSIBILITY (new shape).
- PTE L3 found outside the designed plant zone (C1_REPORT:50-55).
- Ares: evolution routed around the designated carrier (CYCLE2:160-162).

S11. GENERATION OR ACTIVITY IS NOT REACH (false friend).
- v1 generation 56 at radius 3; rcv OFF generation 8 -> 13 with radius fixed at 7 (E-005 RESULT:114-115).

Independent agreement across engines:
- Aether and PTE both find influence far rarer than local perturbability (T19).
- Both find the carrier outside the obvious state (S3).
- Ares and PTE both find several carriers sufficient, with selection decided by physics or parameterisation (S5).

Contradictions:
- LENS:203-204 ("PTE: non-linear computation null") vs DESIGN.md opcode set and the seat's own "search never assembled it" (C1_REPORT:119-124). This is a capacity-vs-search conflation.
- Aether CARD s11 says a registry lists the host as M2, "which is wrong" (CARD:161-163). C_engines records BUCKKEEP (C_engines.md:69).
- PTE DESIGN.md:256-258 says "EXACTLY balanced", superseded by i.i.d. plus mirror pairs (per sub-report).

-----------------------------------------------------------------------
## Section 5. Cheap discriminators (4-core, 7 GB, stdlib Python, git only)

STDLIB, FROM GIT ALONE:

- D1 (RUN IN THIS PASS; COMPUTED-HERE).
  - Method: for each law and arm, tabulate propagation class by flipped field from RB:Aether/AETH-03/evidence/2026-09-26_propagation/prop_<law>_n128_s{0..3}.json (arms[arm][i].summary.{field,class,max_radius}). Script: `git show` + json. Runs in under 10 s.
  - arg0 flips are INERT in 19/28 origins in every law. INFERRED: the high bits are ignored by the mod-4 decode.
  - Energy flips are INERT in 25/27 for v1 OFF.
  - In rcv OFF, arg1 flips give the most escapes (8/24 reach radius >= 3). In rcv ON, arg1 gives 14/24 SUSTAINED. For payload the counts are 4/26 escapes OFF and 6/26 sustained ON.
  - Small n. Descriptive only. It suggests address-field (arg1) differences are the main propagating seed under perturbation (T4, T19).
- D2. The same files, horizons[tick].differing_pairs_by_field: compare the OFF vs ON per-field composition of differences at +400 for rcv. This checks the PD02 "timing -> topology" mechanism (T4).
- D3. RB:ops/campaigns/C-002/E-005/attempts/T-007..T-014*.json (8 files, ~1,150 lines each): per-origin radius and generation at each horizon. Fit a growth law (radius vs t) for rcv ON (sub-ballistic exponent) and for add OFF's slow creep (T14).
- D4. roles/Ananke/pte/c1_rows/cells.jsonl.gz (2.94 MB, 6,596 rows; gzip + json): cross-tab twin.beyond_hop and twin.reach against held.comm_delta and SIGNAL labels over evolve rows. It tests whether twin locality predicts communication dependence (T13).
- D5. The same file: SIGNAL by topology and family, and the champions of out-of-zone L3 cells (loss 0.6, decay 3/6) vs in-zone ones (opcode histograms) (T18, T26).
- D6. ares/runs/sweep_c2/*.json (396 files, 33 MB): struct_div / behav_div / mutation_survival trajectories for W15 vs W4. Also the cycle-1 vs cycle-2 plasticity discrepancy with the cycle-2 dissect files (T24, row 25).
- D7. RB:Aether/AETH-03/evidence/2026-09-27_assay_audit/: per-law joint vs single-parent event counts, plus the events where min-generation neighbour is not sufficient, by field (T12).

NEEDS NUMPY (CPU minutes; Aether units are about 70 s per 4-origin slice on a pod core, 381 s on a contended laptop, C002/E-007/TASKS.md:149):
- T2/T3/T11: re-run fwd, rcv_add and rcv_str plus components at 128^2 with aeth03_content_probe.py. Highest information per CPU-minute in the territory.
- T5: static relay-graph percolation vs per-origin reach.
- T6/T15: supply-loop lesion.
- T7, T8: closure battery variants.
- T9: Mu sweep on rcv.
- T10: loss rate vs density.
- T12: parent audit on add, rcv_add and fwd.

NEEDS TORCH/GPU OR SEAT HARNESS:
- T16/T17: PTE M2 replay with per-carrier resets at t-1 and a traffic-feature decoder. The oracle imports numpy (prometheus/ananke/oracle.py:102, per sub-report); CUDA is optional for small N.
- T18: mixed-topology evolve.
- T21/T22: prereg first.

NEEDS ANOTHER HOST'S DISK (no compute):
- T2: the combinations units.tar is on BUCKKEEP under Prometheus-data/runpod_artifacts, if it survived the v4 re-flight (fd7ca4fde, 76e226c90). Recovering it would decide T2, T3 and T11 at zero compute.
