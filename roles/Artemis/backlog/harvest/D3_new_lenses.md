# D3 harvest -- the new-lens engines (Aether, Cosmos, Ensorain, Ananke, Aphrodite, Odysseus, Ares, Crius)
Domain: D3 new-lens engines founded 2026-09-17..26. Harvester: Artemis delegate, 2026-09-27, read-only, base d7ec26d37 (origin/main).
Paths covered: Aether/** + roles/Aether (main) and origin/aether/research-block-2026-09-27 (C-002, TH-007, PD03, assay audit, engine card); prometheus/cosmos + roles/Cosmos (C0 packet, D-seal packet, C3 design, P1/P2 gate); ensorain/** + roles/Ensorain (E0-E2, D1-D3 dials, WTP-01..03, LM01 prereg review, STEWARD_RULINGS); roles/Ananke (C1 report, C1b packet, SI01 directive, TODO); roles/Aphrodite (main) + origin/aphrodite/a16-campaign-2026-09-26 (A17 report); odysseus/ + roles/Odysseus; ares/ + roles/Ares; crius/ + roles/Crius + docs/essays accessibility-frontier; roles/Atlas-M2 (skimmed).
Paths NOT covered: Aether/runpod platform internals and AETH-01 RunPod cleanup reviews (ASTRA_CLOSURE_REVIEW_02, INDEPENDENT_CLOSURE_REVIEW_04: ops, not science); Cosmos withheld C3 branch (local to M2, unpublished, by design unreadable); origin/nestor/c3-holdout-d (sealed D; deliberately not opened); ensorain run rows/jsonl; prometheus/ananke code; Aphrodite engine amendments 3-14 in detail; Odysseus th006 (ops, TH-006); Crius C0/C1 packets beyond STATUS; Ares cycle 0/1 packets beyond the cycle-2 report.
Method: read status/review packets/verdicts/"questions for the reviewer"; grep for open/unresolved/deferred/untested/INDETERMINATE; diffed seat branches against origin/main; checked later commits (git log per path, branch tips) for answers; no code or tests executed.
Counts: 68 candidates. By kind: open-question 24, parked-experiment 11, anomaly 8, unfollowed-recommendation 6, defect-ambiguity 6, future-work 5, contradiction 4, directive-idea 3, prior-art-gap 1.
Engines: Aether 20, Cosmos 10, Ensorain 10, Ananke 9, Aphrodite 5, Ares 4, Crius 4, Odysseus 1, cross-engine synthesis 5 (H-D3-64..68).
Answered/advanced later: H-D3-03 (answered: generation is a lower bound), H-D3-05 (answered: horizon-robust), H-D3-06 (advanced: Block D ran), H-D3-50 (advanced: A17 ran E1).
Most live right now: H-D3-01/02 (rcv_add, rcv_str, fwd results exist only in a commit message on an unmerged branch), H-D3-21 (Cosmos foreign holdout D sealed but not spent), H-D3-31 (LM01 frozen, not launched).
Existing Threads overlapping: TH-007 (Aether propagation; origin/aether/research-block only) covers H-D3-01..09 in part; TH-001 (causal identity/heredity) touches H-D3-15/64.

---

### H-D3-01 rcv_add / rcv_str passed the "new causal behaviour" gate (N1/N2); falsifiers are pending
- source: commit 9862cfa9e message (2026-09-27), branch origin/aether/research-block-2026-09-27, seat Aether; quote: "Block D's preregistered test called rcv_add and rcv_str NEW_BEHAVIOUR (N1 and N2, super-additive over their components). Before believing it: the content-cause probe (E-P2, triggered by fwd's 92% 'altered' share) and a 10,000-tick horizon run, both committed before their results."
- kind: anomaly
- question: Do two-mechanism combinations (receipt relay + accumulation; receipt relay + energy-steered aim) really produce super-additive propagation or content propagation that neither parent law shows, or is it the same artefact behind fwd's "altered" content?
- why it might matter: This would be the first positive in Aether after 9 single-change laws, and the first evidence for the North Star's "interactions between primitives create new causal behaviour". If it survives, it justifies the first GPU scale-up. If it fails, that bounds the combination search.
- later evidence: none found. The PD03 s5 RESULTS section is still empty at the branch tip. The d_horizon unit set and aeth03_content_probe.py are committed (9862cfa9e) but have no results. Not merged to main.
- lenses: Aether propagation twin assay, content signature, aeth03_combinations_reduce.py, RunPod aether_units
- related: H-D3-02, H-D3-06, H-D3-64

### H-D3-02 fwd, a pure forwarding control, shows 92% "altered" content
- source: Aether/observatory/aeth03_content_probe.py:1-12 @ 9862cfa9e (2026-09-27), branch aether/research-block, seat Aether; quote: "if more than 25% of fwd's content differences at generation >= 2 are "altered", classify the altered events by cause. They were (92%)."
- kind: anomaly
- question: Why does a law whose only content operation is verbatim forwarding produce mostly altered (not preserved) content differences? Is it an instrument artefact (XOR signature versus overwrite timing), or does the substrate transform content on its own (collisions, perturbation, arbitration)?
- why it might matter: PD03 predicted that pure forwarding would give mostly preserved content (E-P2). A 92% miss either invalidates the content-signature metric that the combination positives depend on, or it is the first sign of endogenous content transformation.
- later evidence: none found. The probe is committed without results.
- lenses: Aether content signature, relay-chain fixture
- related: H-D3-01, H-D3-04

### H-D3-03 Is the assay's "generation" really causal depth? (Q1)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:585 @ ee81c0474 (2026-09-27), seat Aether; quote: "Q1. Is the exact-generation argument actually sound? It rests on strict locality and an identical noise stream."
- kind: open-question
- question: Can a site differ without a differing neighbour, and is a differing neighbour always a cause?
- why it might matter: Every Aether propagation verdict rests on this assay.
- later evidence: ANSWERED. Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md:18 @ d8b47a199 (branch) says the "exact shortest causal chain" claim "does NOT hold". Generation is a lower bound, and it matches counterfactual depth in only 84% of rcv-ON events. Verdicts are unchanged. The residue is joint causation, "assigned conservatively" (AETHER_ENGINE_CARD.md:115 @ 7c1724109). That residue is still open and could matter once combinations make joint causes common.
- lenses: Aether assay audit (lightcone, hidden, parents)
- related: H-D3-01

### H-D3-04 Is "activation timing propagates" a finding, or rcv's definition restated? (Q2)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:591 @ ee81c0474 (2026-09-27), seat Aether; quote: "Q2. Is "activation timing propagates" a finding, or is it simply the definition of rcv restated? If the latter, rcv should be recorded as KILLED under "the rule directly encodes the communication it produces""
- kind: open-question
- question: Program-wide form: how do we tell an emergent phenomenon from a rule that directly encodes it?
- why it might matter: The same failure appears in Ananke (RELAY boundaries "gate a hand design") and Cosmos (the recovered law equals the task economics). The program has no general "encoded-by-construction" test.
- later evidence: E-004 (ops/campaigns/C-002/E-004/EXPERIMENT.md:4, branch) was opened to decide rcv's status. No RESULT.md exists.
- lenses: Aether twin assay; the question applies to every engine
- related: H-D3-26, H-D3-42, H-D3-67

### H-D3-05 Does a 128^2, 500-tick window bias propagation verdicts toward "local"? (Q4)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:598 @ ee81c0474, seat Aether; quote: "Q4. Is 128^2 x 400-500 ticks a fair test of propagation, or does it bias toward "local" for any process slower than ~1 site per 50 ticks?"
- kind: open-question
- question: as stated.
- why it might matter: A slow process would be invisible to every ladder.
- later evidence: ANSWERED for v1, add and rcv. ops/campaigns/C-002/E-005/RESULT.md (branch, e67dd06bc) says "locality conclusions are horizon-robust to 10,000 ticks". The residue is that add OFF was the "one slow process seen" (radius 3 -> 5 between +5,000 and +10,000; RESULT.md:26). It is below every bar and has not been followed up.
- lenses: aeth03_longhorizon
- related: H-D3-07

### H-D3-06 Does the one-change-per-law rule hide the only interesting region? (Q6)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:603 @ ee81c0474, seat Aether; quote: "Q6. The one-change-per-arm rule forbids combinations until each part is understood. Could that rule itself hide the only interesting region (effects that exist only in combination)?"
- kind: open-question
- question: as stated. General form: what is the right protocol for moving from causal attribution to combinatorial search?
- why it might matter: This sets how every engine escalates from single mechanisms. Ares found mechanism substitution only under exclusion arms, and Crius found value only in the complete assembly.
- later evidence: ADVANCED. PD03 Block D (39b7f7e85) ran 3 combinations, and 2 passed the gate (see H-D3-01). The general protocol question stays open.
- lenses: Aether; Ares carrier-exclusion arms; Crius rungs
- related: H-D3-01, H-D3-64

### H-D3-07 Perturbation is the only engine of unbounded spread
- source: ops/campaigns/C-002/E-005/RESULT.md:28 @ e67dd06bc (2026-09-27), branch aether/research-block, seat Aether; quote: "rcv ON keeps growing, sub-ballistically (radius 22 at +1,000, 37 at +5,000; 7 of 32 regions reach 28 sites by +10,000) while the share of origins still differing falls to 0.40."
- kind: anomaly
- question: The injected noise channel (Mu) turns timing differences into topology differences (4.8x amplification). What would an endogenous converter look like? Is noise-driven spread science, or contamination by an exogenous driver?
- why it might matter: In an ecology frame, perturbation is variation. This is the substrate telling us that variation, not physics, carries influence. That bears on where selection pressure must act.
- later evidence: rcv_str was designed as an endogenous substitute (PD03 s2.2). Its result is pending (H-D3-01).
- lenses: Aether twin assay, perturbation ON/OFF arms
- related: H-D3-01, H-D3-64

### H-D3-08 Were the kill/justify thresholds strict enough, or so strict that nothing could pass? (Q3)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:595 @ ee81c0474, seat Aether; quote: "Q3. Were the kill/justify thresholds strict enough, or so strict that nothing could pass? No law has passed a justify gate in two rounds. Is that the physics, or the bar?"
- kind: open-question
- question: as stated.
- why it might matter: If the bar can never be met, the negatives carry no information. The same problem recurs in other engines (see H-D3-67).
- later evidence: Two combinations passed N1/N2 in Block D (commit message 9862cfa9e), so the bar is at least reachable. No calibration of the bar against a planted positive propagator was found, apart from the fwd control.
- lenses: Aether reducers
- related: H-D3-67

### H-D3-09 rcv's weak propagation has never been tested outside one parameter regime
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:541 @ ee81c0474, seat Aether; quote: "b. rcv replication across parameter regimes (write cost, replenishment, perturbation rate) -- the obvious fan-out campaign; many CPU units."
- kind: parked-experiment
- question: Does rcv's propagation (sustained 0.047 OFF) survive or strengthen when write cost, replenishment and perturbation rate vary?
- why it might matter: "Nothing was tuned, and nothing was varied either" (line 473). The single regime could sit near a phase boundary or far from one.
- later evidence: none found. PD03 s4 explicitly excluded parameter sweeps.
- lenses: Aether, RunPod aether_units
- related: H-D3-05

### H-D3-10 m4's original question was never asked: do arg1 cycles persist once the K2 channel is removed?
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:543 @ ee81c0474, seat Aether; quote: "c. m4's original question, never asked: without the K2 channel, do arg1-mediated cycles persist?"
- kind: unfollowed-recommendation
- question: as stated.
- why it might matter: It would test whether the perturbation re-aim mechanism (H3-X) is the whole explanation for the arg1 cycle deficit.
- later evidence: none found. m4 was killed on locality only.
- lenses: Aether AETH-02 cycle instrument
- related: H-D3-11

### H-D3-11 Why do cycle members lose their out-edge more often than off-cycle writers? (H3-P3)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:233 @ ee81c0474, seat Aether; quote: "P3 FALSIFIED: at a fixed written field, cycle members keep their out-edge LESS often than off-cycle writers (by 0.07-0.29 per tick). Cause NOT established."
- kind: anomaly
- question: as stated.
- why it might matter: It is a small unexplained anomaly in the one substrate whose law is fully known. It is a cheap test of whether the mechanism inventory is complete.
- later evidence: none found. The PD03 mechanism inventory does not address it.
- lenses: Aether aeth02_closure
- related: H-D3-10

### H-D3-12 The D-15 accessibility transplant was never built
- source: Aether/AETHER_DECISIONS.md:93 @ abe63ef42 (2026-09-20 decision), seat Aether (operator); quote: "The first accessibility transplant reproduces a stated SCIENTIFIC PROPERTY ... useful conditional computation remains inaccessible because of representation topology."
- kind: directive-idea
- question: Can Aether reproduce, from scratch in its own physics, a system where information and selection pressure are present, a viable conditional form exists behind a zero-evaluation valley, and a seeded witness is strongly selectable?
- why it might matter: This is the same scientific property as the Crius accessibility frontier and the Ares basin-width result. It was committed as Aether's first science on 09-20, and then the seat pivoted to persistence and propagation.
- later evidence: none found. No AETH document after 09-20 implements it. K8 ("bounded path/assembly witness with transplants") is still deferred (H-D3-13).
- lenses: Aether; Crius accessibility rulers; Ares basin width
- related: H-D3-13, H-D3-58, H-D3-60, H-D3-64

### H-D3-13 K7/K8 gates are still deferred; they are preconditions for using AETH-01 as evidence
- source: Aether/AETH-01/KILL_GATES_01.md:315 @ abe63ef42 (2026-09-22), seat Aether; quote: "- **K8** (bounded path/assembly witness with transplants) -- requires a running simulator to search a bounded reconfiguration path; cannot be hand-derived."
- kind: parked-experiment
- question: Does a bounded reconfiguration path from the incumbent to a viable assembly exist in aeth01.v1, and do trace and oracle agree (K7)?
- why it might matter: KILL_GATES says K4/K5 tails, K7 and K8 "are preconditions for using AETH-01 as scientific evidence". AETH-02/03 science has proceeded without them.
- later evidence: none found. A simulator now exists, so K8 is buildable.
- lenses: Aether CPU oracle, GPU trace
- related: H-D3-12

### H-D3-14 Assay blind spots: distributed, informational or reconfigurable circuitry
- source: Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md:282-285 @ 0e63a3d52 (2026-09-25), seat Aether; quote: "They cannot see a structure that is spatially distributed, informational rather than resource-routing, uncontested in normal operation, stateful without being self-repairing, or dynamically reconfigurable"
- kind: future-work
- question: What assay could detect those five classes of structure? Is Aether's "no circuitry" reading an instrument limit?
- why it might matter: Aether's negatives are bounded by what the observatory can see. The engine card (7c1724109:119) still lists this as "ambiguous or open".
- later evidence: none found. The twin assay covers causal influence but not these structure classes.
- lenses: Aether observatory
- related: H-D3-15

### H-D3-15 Does the observer smuggle in a heredity ontology?
- source: Aether/AETH-01/ASTRA_REVIEW_01.md:209 @ b751992f8 (2026-09-20), seat Aether (external Astra review); quote: "The observer smuggles in a template-copy/Mu/parent-preserving heredity ontology more strongly than the bare absence of organism IDs removes one."
- kind: open-question
- question: How much of what Aether's observatory reports is imposed by its template-copy/heredity vocabulary rather than by the physics?
- why it might matter: It bears directly on TH-001 (causal identity/heredity across substrates) and on any claim of organism-free emergence.
- later evidence: A terminology linter and refactor exist (TERMINOLOGY_REFACTOR_RECEIPT). No ontology-neutral re-analysis was found.
- lenses: Aether observatory; TH-001
- related: H-D3-14, H-D3-16

### H-D3-16 How can recursive construction and mutual constructors be operationalised?
- source: Aether/AETHER_OPEN_QUESTIONS.md:134 @ abe63ef42 (2026-09-22), seat Aether; quote: "13. How RECURSIVE_CONSTRUCTION, mutual constructors (A builds B, B builds A), and partial copying completed by environmental dynamics get operationalized as detectable, testable predicates -- not yet designed."
- kind: open-question
- question: as stated.
- why it might matter: It is the detection predicate the program needs for "grown, not designed" replication in any substrate (BEE/NPE overlap).
- later evidence: none found.
- lenses: Aether; BEE/NPE replication instruments (TH-001..004)
- related: H-D3-15

### H-D3-17 Is the arbitration hash a hidden economic law once resources are at stake?
- source: Aether/AETH-01/ASTRA_REVIEW_PACKET.md:94 @ 5e41c1d67 (2026-09-20), seat Aether; quote: "Whether AETH-00's arbitration law is statistically neutral enough that its known non-neutrality caveat does not become a hidden "economic law" once real resource stakes are attached"
- kind: defect-ambiguity
- question: as stated. It is flagged there as a "required pre-campaign check".
- why it might matter: The physics has contest-driven energy transfer. A biased arbiter would be an unmodelled selective force.
- later evidence: none found. No neutrality test was located in AETH-02/03.
- lenses: Aether arbitration (SplitMix64)
- related: H-D3-18

### H-D3-18 Expressivity ceiling: no movement primitive, one active opcode, no conditional
- source: Aether/AETH-01/ASTRA_REVIEW_PACKET.md:104,117 @ 5e41c1d67, seat Aether; quote: "Whether excluding literal movement (D-AETH01-07) will eventually force an R6 dead end that can only be resolved by adding a movement primitive as a new semantics_id."
- kind: open-question
- question: Which affordances (movement, conditional, sensing) are the minimal additions? And the ASTRA counter-warning (ASTRA_REVIEW_01.md:215): energy thresholds already provide conditionals, so do not add a familiar ISA.
- why it might matter: This is where the North-Star "primitives we supply" question becomes concrete. mov (conservation) and cnd were tried in the ladders; movement as transport was not.
- later evidence: PARTLY ADVANCED. mov was killed (local; 41% of differences die) and cnd was killed (ladder 1). No non-conservative movement primitive has been tried.
- lenses: Aether physics ladders
- related: H-D3-17, H-D3-12

### H-D3-19 Aether excludes selection, and the engine card lists that as a bad fit. Should selection be added?
- source: Aether/AETHER_ENGINE_CARD.md:90 @ 7c1724109 (2026-09-27), branch aether/research-block, seat Aether; quote: "- **Anything about selection or ensembles of assemblies.** There is no inheritance of anything but bytes and no selection of anything"
- kind: open-question
- question: Is Aether's propagation null a property of selection-free physics? Would a minimal selection or ecological filter (Ananke evolved RELAY in its physics) produce content propagation that the law alone does not?
- why it might matter: The North Star is co-evolution under selection. The one new-lens engine with no selection is also the one with no propagation.
- later evidence: none found. The TH-007 constraint forbids steering on propagation.
- lenses: Aether; Ananke PTE
- related: H-D3-65

### H-D3-20 Stop the Aether science and keep only the benchmark, or keep both? (Q7/Q9)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:606,612 @ ee81c0474, seat Aether; quote: "Q7. Is Aether a good queue/campaign test bed precisely BECAUSE its science is open, or would a closed benchmark with known answers be a stronger test of the machinery?"
- kind: open-question
- question: as stated. Its lean is option (1) with a guard: if fwd plus one more ladder give no content propagation, switch to option (2), a fixed benchmark.
- why it might matter: The guard's trigger condition may now have been met or averted (H-D3-01/02). Someone should apply the pre-stated rule.
- later evidence: the Block J frontier synthesis is requested by the directive; not found at the branch tip.
- lenses: Aether; campaign model C-002
- related: H-D3-01

### H-D3-21 Foreign holdout D is sealed but unspent: does a Cosmos law transfer to a world it did not author?
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:182 @ af2af37f4 (2026-09-23), seat Cosmos; quote: "Stop condition worth stating: if C3's sealed-by-another-seat substrate is predicted no better than 5-NN transfer, the transfer seen here was an artifact of shared authorship"
- kind: parked-experiment
- question: Once D is spent, does the C3 functional-memory law predict a Nestor-authored world better than 5-NN?
- why it might matter: This is the program's only test that breaks the one-author ceiling on cross-world invariants. The outcome decides whether Cosmos is a law finder or only an auditing tool.
- later evidence: D was sealed by Nestor (#599). REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt:32 says "ONE GATE IS OPEN". The seal commit a56ef7787 is still NOT an ancestor of origin/main (checked 2026-09-27). D has not been run.
- lenses: Cosmos CWE, holdout broker, P1/P2 certificate
- related: H-D3-22, H-D3-24

### H-D3-22 Coordinates declared by the author may smuggle in the answer (Q4)
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:196 @ af2af37f4, seat Cosmos; quote: "Q4 Coordinates are declared by the substrate author. Is there any defence against a well-meaning author declaring coordinates that smuggle the answer (every family "knows" C, N, K, G)?"
- kind: open-question
- question: as stated. The planned defence is a Harmonia coordinate audit (C3 design D2).
- why it might matter: Every cross-world law is expressed in declared coordinates. If the coordinates carry the law, invariance is manufactured.
- later evidence: the Harmonia audit is still not invoked (D-seal packet s0: "Harmonia has not been invoked").
- lenses: Cosmos miner, Harmonia
- related: H-D3-21, H-D3-23

### H-D3-23 What would a non-circular qualification target look like? (Q1)
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:189 @ af2af37f4, seat Cosmos; quote: "Q1 Is "qualification" meaningful when the recovered law equals the task economics the author built in? What would a non-circular qualification target look like at this cost?"
- kind: open-question
- question: as stated.
- why it might matter: The mined law agreed with the hand-derived economics on 97.5% of worlds. Instruments that re-find planted economics cannot yet be trusted to find unplanted invariants.
- later evidence: C3 moved to P1/P2 (memory), which is not an economics restatement. No independent answer to the general question.
- lenses: Cosmos; applies to every engine with planted controls
- related: H-D3-04, H-D3-22

### H-D3-24 Selection and active sampling are not shown to help law discovery (V3)
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:28 @ af2af37f4, seat Cosmos; quote: "V3 SEARCH METHOD: UNRESOLVED. Active sampler ties random; cost lines lose to random (.767 vs .946, matched budget)"
- kind: open-question
- question: Is there any regime where adaptive or active experimentation beats random sampling for recovering cross-world laws? Or is random sampling the right default?
- why it might matter: The North Star assumes that selection pressure and search add value. This is a clean case where they did not, and "location-aware selection is not shown necessary".
- later evidence: C3 retired sampler development ("random sampling only", 03_c3_design s1). The question is parked, not answered.
- lenses: Cosmos sampler, eta2, c2x attribution matrix
- related: H-D3-66

### H-D3-25 Law A's unique errors are gross misses on growing and dying clones
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:32 @ af2af37f4, seat Cosmos; quote: "Observation (not a conclusion): on F, A's unique errors include gross misses on growing/dying clones; B's all sit near the phase boundary."
- kind: anomaly
- question: Do population-dynamics regimes (growing or dying clones) violate law A's coordinates in a structured way, pointing to a missing coordinate?
- why it might matter: B over A was not established (p = 1.0), but the error SHAPES differ. A structured failure is evidence of a missing variable.
- later evidence: none found (F is spent, so this needs a new sealed world).
- lenses: Cosmos adversary, location gate
- related: H-D3-22

### H-D3-26 P1/P2 certificate: a 0.08 false-INDETERMINATE rate and a low-power generic probe
- source: roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md:100 @ 940b486f2 (2026-09-24), seat Cosmos; quote: "CALIBRATION FACT for users of the certificate: the INDETERMINATE band admits a truly history-free system with probability ~0.08 per certification"
- kind: defect-ambiguity
- question: P1 now leans on the system's OWN readout probe, because the generic probe was low-power (line 70). Does that make the certificate blind to memory that the readout does not use (Ananke M2-like, in-flight memory)? Is 49 permutations enough?
- why it might matter: Cosmos P1/P2, Ensorain LM01 and Ananke SI01 all certify "history kept and causally used". This is the most formal of the three certificates.
- later evidence: none found beyond the v3 gate PASS.
- lenses: Cosmos C3 certificate
- related: H-D3-66, H-D3-39

### H-D3-27 P3 "when does retention pay" was deferred
- source: roles/Cosmos/design/03_c3_design_draft_2026-09-23.md:36 @ e8f6d0ad1 (2026-09-23), seat Cosmos; quote: "P3 ADVANTAGE (a pressure law): under which conditions retention pays. DEFERRED until P1 and P2 are measured and certified across substrates"
- kind: parked-experiment
- question: as stated.
- why it might matter: This is the pressure law the ecology needs: which environments select for memory. Ensorain's dials (timescale x representation) and Ares's W-worlds are partial answers made with no shared instrument.
- later evidence: none found.
- lenses: Cosmos; Ensorain dials; Ares pressure catalog
- related: H-D3-37, H-D3-66

### H-D3-28 Stigmergic memory: where is the boundary between system and world?
- source: roles/Cosmos/design/03_c3_design_draft_2026-09-23.md:57 @ e8f6d0ad1, seat Cosmos; quote: "declare what "the system" vs "the world" is (for C that boundary IS the question and is declared by the author, then attacked)."
- kind: open-question
- question: When memory lives in the environment (family C), how is causal state attributed? How is the "attack" on an author-declared boundary performed?
- why it might matter: It links to Ananke M2 (memory in packets in flight, not in site state) and to Aether's partial machinery held in the environment.
- later evidence: results are withheld on the Cosmos C3 branch, so this cannot be checked.
- lenses: Cosmos C3 family C
- related: H-D3-39, H-D3-66

### H-D3-29 Operator directive: "Cosmos should search for the dials, not predefine them" -- never routed
- source: roles/Ensorain/prompts/2026-09-24_dials_of_intelligence/01_OPERATOR_DIALS_verbatim.md:50 @ 0180ab244 (2026-09-24), operator via seat Ensorain; quote: "That suggests something very Promethean for Cosmos: do not predefine the important dials. Search for them."
- kind: directive-idea
- question: Can a Cosmos-style chamber discover which parameters (dials) govern competence across worlds, instead of sweeping author-chosen dials?
- why it might matter: It is the North-Star-shaped version of Ensorain's dial sweeps. The only replicated dial coupling (timescale x representation) was found by hand-chosen grids.
- later evidence: none found. No Cosmos file mentions dials. The Ensorain README notes that routing is the operator's call.
- lenses: Cosmos miner; Ensorain dials
- related: H-D3-37

### H-D3-30 Was holdout D built independently of Cosmos's hypothesis? (D-seal Q3/Q5)
- source: roles/Cosmos/campaigns/REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt:188 @ 4a6a5df52 (2026-09-26), seat Cosmos; quote: "Q5  What evidence would convince you D was NOT unconsciously built to agree with a Cosmos-shaped hypothesis, given Nestor read the public P1/P2 definitions?"
- kind: defect-ambiguity
- question: What holdout-independence protocol (commit-reveal, blind contract) is sufficient when the holdout author reads the certificate definitions?
- why it might matter: Foreign holdouts are the program's generalisation instrument. Q1 (line 178) notes the honor-based protection that the operator rejected in the other direction.
- later evidence: none found.
- lenses: Cosmos holdout broker; evidence provenance
- related: H-D3-21

### H-D3-31 WTP-LM01 is frozen but not launched: does exact retention match bounded coarse-graining?
- source: ensorain/LM01_PREREG_REVIEW_2026-09-26.md:12 @ 222ed8082 (2026-09-26), seat Ensorain; quote: "under honestly accounted bounded resources, can a system that keeps its admitted history EXACTLY reach the held-out / fresh-field competence of systems that keep a bounded coarse-grained representation?"
- kind: parked-experiment
- question: as stated.
- why it might matter: This is the direct test of the compression premise behind "representations/compressions co-evolve". The design is complete (1,968 worlds, ~9 h).
- later evidence: none found. No launch prompt exists under roles/Ensorain/prompts. Last commit 222ed8082.
- lenses: Ensorain LM01 reservoir curve
- related: H-D3-32, H-D3-33, H-D3-66

### H-D3-32 Is selectivity causally required? (untested in LM01 by design)
- source: ensorain/LM01_PREREG_REVIEW_2026-09-26.md:28 @ 222ed8082, seat Ensorain; quote: "- WHETHER SELECTIVITY IS CAUSALLY REQUIRED REMAINS UNTESTED in LM01 (ruling item 5)."
- kind: open-question
- question: as stated. The intervention arm was deferred (D11, "decided by construction").
- why it might matter: This is the core of the Selective-Irreversibility hypothesis. Ananke SI01 was designed to attack it and has also not run.
- later evidence: none found. STEWARD_RULINGS.md:92 caps any intervention reading at "needed for the rest of THIS life".
- lenses: Ensorain LM01; Ananke SI01
- related: H-D3-45, H-D3-66

### H-D3-33 Self-signal eviction rules lose to random eviction
- source: ensorain/LM01_PREREG_REVIEW_2026-09-26.md:102 @ 222ed8082, seat Ensorain; quote: "NOTE: both declared self-signal eviction rules LOSE to random there; they keep noisy records. That is recorded as a dev finding, not repaired."
- kind: anomaly
- question: Why does residual-driven ("what surprises me") eviction keep noisy records and do worse than random? Is surprise a bad retention signal in noisy worlds?
- why it might matter: Endogenous forgetting rules are a North-Star primitive. A principled result here ("surprise retains noise") would shape the memory primitives supplied to every engine.
- later evidence: none found.
- lenses: Ensorain LM01 eviction arms
- related: H-D3-32

### H-D3-34 WTP-04 "beyond completion" (N6 null, cross-field transfer, class-agnostic admission) was never authorised
- source: ensorain/ENSORAIN_WTP03_REPORT.md:143 @ a65d27ced (2026-09-25), seat Ensorain; quote: "W2 **ADMISSION PRE-SELECTS THE PHENOMENON.**" (W1 at line 135, "TRANSFERS IS NEAR-TAUTOLOGICAL for field models.")
- kind: unfollowed-recommendation
- question: With admission on class-agnostic information demand, a same-class batch-completion null (N6) and transfer to a different field, does any learned substrate do something that completion physics cannot?
- why it might matter: The collider's positives are all "known completion physics". Without these fixes it can only confirm what it admits.
- later evidence: SUPERSEDED in direction by WTP-LM01 (STATUS: "WTP-LM01 supersedes WTP-04"). The instrument fixes W1-W4 were never applied, and STATUS open question 1 (the DEEPEN adjudication) has no recorded ruling.
- lenses: Ensorain WTP collider
- related: H-D3-35, H-D3-67

### H-D3-35 The learning-time / lifetime ratio decides whether a world is inhabitable
- source: ensorain/ENSORAIN_WTP03_REPORT.md:166 @ a65d27ced, seat Ensorain; quote: "- **The binding constraint is in-life learning speed, not information.**"
- kind: future-work
- question: Is the ratio of learning time to lifetime a universal control parameter for whether adaptive machinery pays? Can it be searched directly?
- why it might matter: Ares found that recurrence wins "on SPEED, not capability". Both engines point to learning speed relative to lifetime as the selective axis.
- later evidence: none found. The item stays in STATUS as a WTP-04 fix (d).
- lenses: Ensorain WTP; Ares
- related: H-D3-57, H-D3-37

### H-D3-36 Weird physics destroys learnability
- source: ensorain/ENSORAIN_WTP03_REPORT.md:171 @ a65d27ced, seat Ensorain; quote: "- **Weird physics generally destroys learnability.** 3 of 181 admitted worlds are "wild"; transform chains, credit corruption and graph-cell maps almost always make the stream uninformative."
- kind: contradiction
- question: The mandate to search weird worlds and the requirement that relationships matter "pull hard against each other". Is there a class of non-standard physics that stays learnable? What property separates it?
- why it might matter: The North Star wants novel representations. If novelty and learnability are anti-correlated in world grammars, then how environments are generated needs its own theory.
- later evidence: none found.
- lenses: Ensorain world grammar; Aether (novel physics with no learnability measure)
- related: H-D3-19

### H-D3-37 One replicated dial coupling (timescale x representation); capacity x replay is under-powered
- source: ensorain/DIALS_SYNTHESIS.md:27,34 @ 818882180 (2026-09-24), seat Ensorain; quote: "One candidate is alive but under-powered: CAPACITY x REPLAY (replay is costly only under capacity pressure; neutral with slack)"
- kind: parked-experiment
- question: Does the capacity x replay coupling (r .92, p .065) replicate with adequate power? Does timescale separation x representation correctness generalise beyond TT worlds?
- why it might matter: It is the only organism-intrinsic dial interaction the program has replicated.
- later evidence: none found. Dial work stopped at round 4.
- lenses: Ensorain dials
- related: H-D3-29, H-D3-27

### H-D3-38 Structure discovery fails: evolved memories do not identify the world's structure
- source: ensorain/E2_VERDICT.md:26 @ 553a05d2e (2026-09-23), seat Ensorain; quote: "G_ID (SD correct-structure rate; gate >= 0.70 per structured family, >= 0.50 NONE; sets A / B):"
- kind: open-question
- question: TT 0.20/0.15, CP 0.27/0.38: why can't the structure-discovery arm recover the generating tensor structure when a correctly ordered TT is known to win (E1.5)? The operator named it "the open problem" (E1P5_VERDICT.md:13).
- why it might matter: It is the representation-selection problem, the co-evolution half of the North Star, in its cleanest form.
- later evidence: none found. E1/E1.5/E2 are PARKED intact.
- lenses: Ensorain E2
- related: H-D3-49

### H-D3-39 LM01 cannot say anything about a computation-inclusive version of the law
- source: ensorain/LM01_PREREG_REVIEW_2026-09-26.md:155 @ 222ed8082, seat Ensorain; quote: "- a computation-inclusive version of the law (an L-R win says nothing either way about it)."
- kind: future-work
- question: If exact retention wins only by recomputing a transient fit at readout (L-R), how should compute be charged so that "lossless" and "compressed" are compared honestly? The secondary arm is also optimizer-confounded (line 126).
- why it might matter: Without compute accounting, the memory-vs-compression question is under-determined.
- later evidence: none found.
- lenses: Ensorain LM01 accounting
- related: H-D3-31

### H-D3-40 E0/E1 closed INDETERMINATE (controls); the substantive question was never answered
- source: ensorain/E1P5_VERDICT.md:13 @ 984804b44 (2026-09-23), seat Ensorain (operator ruling); quote: "world; the open problem is structure discovery (E2). E1 and E1.5 are PARKED intact."
- kind: parked-experiment
- question: Do tensor-network memories give a compression-headroom advantage when the correct order must be learned? (E0 and E1 were both INDETERMINATE on controls.)
- why it might matter: It is the founding question of the Ensorain lens and is still open behind control failures.
- later evidence: E2 failed (H-D3-38), and the lens moved to WTP/LM01.
- lenses: Ensorain E0-E2
- related: H-D3-38

### H-D3-41 What carries M2's in-flight bit, if not the signed payload?
- source: roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt:171 @ cc98596dd (2026-09-26), seat Ananke; quote: "- M2's code is unknown: in flight, but not the signed payload sum. Timing, count or destination pattern are untested candidates."
- kind: open-question
- question: as stated.
- why it might matter: An evolved system stores a bit in the communication medium (packets in flight), not in state. That is a non-designed memory locus. It reproduced 3/3 under fresh seeds.
- later evidence: none found.
- lenses: Ananke PTE assay switches; Cosmos P1 (full causal state must include in-flight packets)
- related: H-D3-28, H-D3-66

### H-D3-42 M3's SETRULE dependence: configuration or memory?
- source: roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt:173 @ cc98596dd, seat Ananke; quote: "- M3's SETRULE role is inferred as configuration (the readout rule is constantly 0). Which sites switch, and when, is not measured."
- kind: open-question
- question: as stated.
- why it might matter: It separates self-modification used as memory from self-modification used as one-time wiring. That distinction matters for any claim of evolved self-modification.
- later evidence: none found.
- lenses: Ananke C1b
- related: H-D3-41

### H-D3-43 Absolute thresholds make C1b labels unattainable near 0.6
- source: roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt:155 @ cc98596dd, seat Ananke; quote: "- Absolute thresholds make "kills" automatic, and T unattainable, for champions near 0.6. This is a prereg limitation, reported, not repaired."
- kind: defect-ambiguity
- question: With M3 fingerprints visible descriptively but labels mechanically blocked, what is M3's true reproduction status?
- why it might matter: It is a case of the prereg, not the physics, deciding the verdict (see H-D3-67).
- later evidence: none found.
- lenses: Ananke C1b reducer
- related: H-D3-67, H-D3-08

### H-D3-44 XOR/FLIP: 0 signal in 165 cells; two-stage composition is never assembled
- source: roles/Ananke/pte/C1_REPORT.md:119 @ e35fb9704 (2026-09-24), seat Ananke; quote: "F1 XOR and FLIP: 0 signal in 165 evolve cells. Superposition sums packets, so a receiver sees x1+x2, from which XOR needs a |sum|-threshold and exact co-arrival"
- kind: parked-experiment
- question: With port-resolved arrival, longer programs or multi-episode lineages, can the search assemble two-stage compositions? Or is this another accessibility frontier?
- why it might matter: It is the same shape as Crius's frontier and Aether's "nothing composes". Composition is the universal gap.
- later evidence: none found. v2 dials (C1_REPORT.md:158) have not been built.
- lenses: Ananke PTE; Crius
- related: H-D3-64, H-D3-60

### H-D3-45 PTE-SI01: do distinctions stop being recoverable when they stop mattering?
- source: roles/Ananke/prompts/2026-09-25_pte_si01_directive/01_STEWARD_DIRECTIVE_verbatim.md:149 @ 69302a66e (2026-09-25), seat Ananke (steward Aporia); quote: "When a bounded communication-based system repeatedly solves changing tasks, do distinctions cease to remain accessible specifically when they cease to matter for future prediction/control?"
- kind: directive-idea
- question: as stated, using R/E/N (relevant, expired, never-relevant) distinction classes.
- why it might matter: It is the most direct falsification test of the Selective-Irreversibility candidate law. The expired-vs-nuisance design is a novel control.
- later evidence: none found. C1b ran first, as required, but there is no PREREG_PTE_SI01 in roles/Ananke/pte. The steward-management channel was frozen by the operator on 2026-09-26 (Ensorain STATUS #732/#733), so SI01's governance path is unclear.
- lenses: Ananke PTE; Ensorain LM01; Cosmos P1/P2
- related: H-D3-32, H-D3-66

### H-D3-46 PTE-C1 was never independently reviewed
- source: roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt:164 @ cc98596dd, seat Ananke; quote: "Science: NONE yet. Kairos #564 and Elenchus #565 never replied (advisory now). Same author throughout."
- kind: defect-ambiguity
- question: Does C1's RELAY COMM_DEPENDENT + CAUSAL_SUPPORT verdict survive independent adversarial review?
- why it might matter: C1 is the seat's headline positive, and the operator HOLD was placed pending exactly this review.
- later evidence: none found. The review was downgraded to advisory.
- lenses: Ananke PTE; review process
- related: H-D3-47

### H-D3-47 RELAY laws are topology-bound; no cross-family transfer
- source: roles/Ananke/pte/C1_REPORT.md:125 @ e35fb9704, seat Ananke; quote: "F2 Topology-bound laws: every RELAY law dies on a random graph. The machinery encodes lattice geometry (routing to specific offsets)."
- kind: open-question
- question: Would evolving across mixed topologies produce geometry-free transport, or is geometry the substrate's "body"?
- why it might matter: It is the transfer and generality question for evolved communication. It parallels Ares's "transplantability refuted twice".
- later evidence: none found.
- lenses: Ananke PTE topology
- related: H-D3-68

### H-D3-48 PTE-C2 "weather" (load axes on the causally verified habitable zone) is not preregistered
- source: roles/Ananke/pte/C1_REPORT.md:154 @ e35fb9704, seat Ananke; quote: "3. PTE-C2 "weather": habitable zone = the physics of the CAUSALLY verified RELAY/MAJ cells (not A0 viability, see s2), three separate load axes"
- kind: unfollowed-recommendation
- question: How do evolved communication mechanisms degrade under traffic density, independent processes and informational conflict?
- why it might matter: It maps the robustness of evolved communication. The item is still open in roles/Ananke/TODO.md:10 (ANANKE-26).
- later evidence: none found.
- lenses: Ananke PTE
- related: H-D3-49

### H-D3-49 Labels built from expected controls missed the interesting mechanisms
- source: roles/Ananke/pte/C1_REPORT.md:129 @ e35fb9704, seat Ananke; quote: "F3 The PREREG labels missed two of the three most interesting mechanisms (M2, M3) because the causal rules encoded the mechanism we expected. Opening: mechanism labels from the ablation PATTERN"
- kind: future-work
- question: Can mechanism labels be built as unsupervised ablation fingerprints (a pattern over all controls) instead of expected-mechanism rules, and be shared across engines?
- why it might matter: It is a falsification-instrument principle. Ensorain W2 (admission pre-selects) and the Aether forced-by-law intervention are the same failure. A shared fingerprint instrument would serve every engine.
- later evidence: C1b introduced per-carrier batteries. No general fingerprint labeller was found.
- lenses: Ananke; all engines' ablation suites
- related: H-D3-67, H-D3-34

### H-D3-50 G1 -> G2 recursion: the one valid test hit a task supply that could show G1 nothing new
- source: roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:96 @ 4f937e88f (2026-09-26), branch origin/aphrodite/a16-campaign-2026-09-26, seat Aphrodite; quote: "The E1 negative is conditional on this G4 task distribution, in which the only reliably qualifiable families are additive/subtractive folds -- exactly G1's home ground"
- kind: open-question
- question: Does an inherited abstraction help derive a semantically NEW abstraction when the task supply contains families it does not already explain?
- why it might matter: It is the program's only operational test of bounded recursive self-improvement (improver-of-improvers). BRSI = NO so far is a supply artefact, not a verdict.
- later evidence: A17 (4f937e88f, unmerged branch): E1 = NO (valid), E2 UNTESTABLE. Earlier, AMENDMENT 15 and the A16 first execution were UNTESTABLE. No A18.
- lenses: Aphrodite engine, foundry
- related: H-D3-51, H-D3-64

### H-D3-51 Non-additive task families (mul, mod, powr) cannot be qualified
- source: roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:79 @ 4f937e88f, branch aphrodite/a16-campaign, seat Aphrodite; quote: "FINDING (task space, not apparatus): the frozen G4 per-stratum sampler is dominated by degenerate draws."
- kind: anomaly
- question: Why do mul/mod/powr strata accept 0/32 draws in both catalogs (Q3 hostile-tribunal rejects 233 of 416)? Is it degenerate witnesses, or a real property of the G4 task space?
- why it might matter: Task and environment supply is the binding constraint on testing recursion (the report says "the binding constraint is now family SUPPLY"). The environment half of the ecology is under-built.
- later evidence: none found. The proposed fix (a sampler excluding degenerate witnesses) needs a new prereg.
- lenses: Aphrodite foundry Q2/Q3
- related: H-D3-50, H-D3-36

### H-D3-52 Whole-program identity (S1) is what makes endogenous abstraction possible
- source: roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:56 @ 4f937e88f, branch aphrodite/a16-campaign, seat Aphrodite; quote: "S1_NECESSITY = SUPPORTED  (WHOLE recovered 3/3, BODY_ONLY 0/3)"
- kind: open-question
- question: Does the finding that abstraction recovery needs whole-program behavioural identity (not body-only anti-unification) generalise beyond this DSL? Is behavioural-identity certification the primitive other engines lack?
- why it might matter: It is a representation-level design rule for how compressions are discovered. It supersedes the 09-24 INCONCLUSIVE.
- later evidence: this result is itself the later evidence (the earlier A16 E4 was INCONCLUSIVE). Unmerged to main.
- lenses: Aphrodite cert.py, identity.py
- related: H-D3-53

### H-D3-53 Search leverage without recursion: G1 donors search about 40% cheaper but derive nothing new
- source: roles/Aphrodite/pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md:81 @ 4f937e88f, branch aphrodite/a16-campaign, seat Aphrodite; quote: "Search leverage of G1 remains visible and is NOT a recursion claim: G1 donor meta-charges 8.57M-9.22M vs PRISTINE 14.51M-15.00M"
- kind: open-question
- question: Transferable search leverage (Tier 3B 47x, 3C 345x) is repeatedly YES while recursion is NO. Is leverage a precursor of recursion, or a different capability? What experiment would link them?
- why it might matter: It separates "improves search" from "improves the improver", the core RSI distinction.
- later evidence: none found.
- lenses: Aphrodite tiers 3A-3C, S4
- related: H-D3-50

### H-D3-54 Tier 3A causal inference was left INCONCLUSIVE_CONTROL_INVALID
- source: roles/Aphrodite/STATUS.md:29 @ 9490f3f34 (2026-09-25), seat Aphrodite; quote: "Tier 3A also: PRIMARY_CAUSAL_INFERENCE = INCONCLUSIVE_CONTROL_INVALID"
- kind: defect-ambiguity
- question: What was Tier 3A's primary causal inference, and was it ever re-run with a valid control?
- why it might matter: An invalid control leaves a causal question open, not closed.
- later evidence: none found (AMENDMENT_10 records it; no re-run located).
- lenses: Aphrodite Tier 3A
- related: H-D3-53

### H-D3-55 Odysseus: what should the first scientific payload of the distributed brain be?
- source: odysseus/pivot/ODYSSEUS_BRAIN_V0_REVIEW_2026-09-26.md:189 @ 37051a342 (2026-09-26), seat Odysseus; quote: "Q4 Is a spiking placeholder misleading, given the operator also named vectors, tensors and nets? Should the first real payload be a sharded tensor graph instead?"
- kind: parked-experiment
- question: What reasoning-signal experiment justifies a sharded, replayable, forkable substrate? (Line 164 lists "usefulness for finding weak reasoning signals (no consumer yet)".) Q1 asks whether bit-identical replay would block float/GPU consumers.
- why it might matter: Replay and fork microtests are a novel falsification instrument (counterfactual forks at any tick), but there is no scientific consumer. The operator parked the lane for more design (626d8c396).
- later evidence: FROZEN by the operator on 2026-09-27 ("It feels like more deign is needed by me").
- lenses: Odysseus brain; Aether twin assay (a similar counterfactual-fork idea)
- related: H-D3-66

### H-D3-56 Direct test of the basin-width explanation on evolved genomes
- source: ares/ARES_CYCLE2_REPORT.md:209 @ 3f68be2b9 (2026-09-25), seat Ares; quote: "1. DIRECT TEST OF THE BASIN EXPLANATION, on evolved genomes rather than hand-wired ones: re-parameterise keep so its viable region is wide"
- kind: parked-experiment
- question: If keep is given a wide, unbounded viable region, does evolution then select keep over recurrence?
- why it might matter: The basin-width claim is post-hoc and measured on hand-wired carriers. This is its falsifier.
- later evidence: none found. The seat is PARKED with CONTINUE_RECOMMENDED and has no operator ruling on record.
- lenses: Ares substrate/GA
- related: H-D3-57, H-D3-64

### H-D3-57 Basin width as a predictor of which primitive evolution selects
- source: ares/ARES_CYCLE2_REPORT.md:217 @ 3f68be2b9, seat Ares; quote: "2. BASIN WIDTH AS A PREDICTOR ACROSS PRIMITIVES: measure the viable region of every primitive the substrate offers and test whether basin width, not expressiveness or reachability, predicts which one evolution selects."
- kind: unfollowed-recommendation
- question: as stated. If true, it is "a design rule for any substrate in the program".
- why it might matter: It speaks directly to how primitives are supplied: evolution takes the wide basin, not the higher peak.
- later evidence: none found.
- lenses: Ares; applies to Aether and Aphrodite primitive sets
- related: H-D3-56, H-D3-64, H-D3-35

### H-D3-58 Redundancy under attack: selected, or a by-product?
- source: ares/ARES_CYCLE2_REPORT.md:222 @ 3f68be2b9, seat Ares; quote: "3. WHY REDUNDANCY UNDER ATTACK: W15 produced dual-carrier lineages (recurrence load-bearing 8/10 AND plasticity 7/10, recurrent edges up 4.5x) rather than substitution."
- kind: unfollowed-recommendation
- question: as stated. The seat calls it "the only result here that pointed somewhere nobody predicted".
- why it might matter: Degeneracy and redundancy under adversarial pressure is a robustness mechanism with a direct link to evolvability theory.
- later evidence: none found.
- lenses: Ares W15
- related: H-D3-56

### H-D3-59 Parked Ares items: novelty-search arm, pressure combinations, ancestry reconstruction
- source: roles/Ares/BACKLOG_H0H5.md:33 @ 8ba05b2c8 (2026-09-21), seat Ares; quote: "ARES-19 | Add a novelty-biased search arm and re-run the two most informative worlds to test whether the finding depends on the optimizer"
- kind: parked-experiment
- question: Do Ares's findings (substitution, basin width) depend on the GA optimizer? Do combined pressures (ARES-15/16, lines 29-30) create mechanisms that single pressures do not? Did mechanisms arrive in one mutation or accrete (ARES-27, line 41)?
- why it might matter: Optimizer dependence is the standard confound for any "evolution prefers X" claim. Ancestry reconstruction is the instrument Crius used to find its frontier.
- later evidence: none found. The backlog records "PARKED: ARES-15..20, 24, 26, 27".
- lenses: Ares search, fossils
- related: H-D3-56, H-D3-62

### H-D3-60 The controlled pair: same mechanism, same payoff, different assembly geometry
- source: docs/essays/2026-09-24-accessibility-frontier.md:200 @ 391395aac (2026-09-24), seat Crius; quote: "The controlled pair Same destination. Same payoff. Different assembly geometry."
- kind: unfollowed-recommendation
- question: Does changing only the construction landscape (independent part utility, niches, coupled recombination, developmental staging, local credit) radically change the probability of discovering a primitive?
- why it might matter: It is a sharp, cross-engine test of the "assembly-geometry principle". It maps onto Aether D-15, Ares basin width and Aphrodite task supply. The essay: "None of these has been tested anywhere" (line 222).
- later evidence: none found. The Crius lane is CLOSED, and the essay says it does not reopen it.
- lenses: Crius substrate; any GA engine
- related: H-D3-12, H-D3-57, H-D3-64

### H-D3-61 Is the Crius frontier a representation artefact? (the neutral-network objection)
- source: docs/essays/2026-09-24-accessibility-frontier.md:188 @ 391395aac, seat Crius; quote: "It may only be a bad representation. Typed procedural reuse may be inaccessible in Crius's bytecode because Crius encoded it badly"
- kind: prior-art-gap
- question: Would a genotype-phenotype map with percolating neutral networks (Greenbury et al. 2022; Wagner 2008) make the same mechanism reachable?
- why it might matter: If yes, representation design, not capability or reward, controls accessibility. That is the co-evolving-representation half of the North Star.
- later evidence: none found.
- lenses: Crius; representation engines
- related: H-D3-60, H-D3-62

### H-D3-62 Accessibility rulers (foothold density, flat-valley length, accessibility ratio) are unvalidated
- source: docs/essays/2026-09-24-accessibility-frontier.md:146 @ 391395aac, seat Crius; quote: "These are attempts to make accessibility measurable; they are rulers to attack, not results."
- kind: future-work
- question: Can foothold density, flat-valley length and the proposed rho = V/(V + d_flat*c) be measured in other engines and shown to predict discovery?
- why it might matter: A portable accessibility instrument would measure the "hidden axis" (the useful gradient a substrate exposes) across all substrates.
- later evidence: none found.
- lenses: Crius; Ares ancestry; Aphrodite foundry
- related: H-D3-60, H-D3-59

### H-D3-63 "Invocation without content": the fossil that selection settles into
- source: crius/CRIUS_C2_TERMINAL_REVIEW.md:144 @ 7069c0ce6 (2026-09-23), seat Crius; quote: "Two qualified tops invoke blocks with zero effect ("invocation without"
- kind: anomaly
- question: Why does selection keep full block-stores invoked dozens of times per lifetime with zero effect? Is content-free scaffolding a general attractor at the foot of an accessibility cliff? Does it appear in other engines (Aether frozen residue, Aphrodite degenerate witnesses)?
- why it might matter: A recognisable fossil signature would be a cheap detector for "stuck below a frontier" in any evolving system.
- later evidence: none found.
- lenses: Crius; fossils in Ares
- related: H-D3-60, H-D3-51

### H-D3-64 CROSS-ENGINE: the construction landscape decides discovery (Crius, Ares, Aether D-15, Aphrodite, Ananke)
- source: ares/ARES_CYCLE2_REPORT.md:26 @ 3f68be2b9 (2026-09-23), seat Ares; quote: "ceiling; recurrence works across a wide, flat, open-ended region where more is never worse." With docs/essays/2026-09-24-accessibility-frontier.md:134 (Crius) and Aether/AETHER_DECISIONS.md:93 (D-15).
- kind: contradiction
- question: Five engines give compatible but differently framed findings. Crius: reachable parts pay nothing (flat valley). Ares: evolution picks the wide basin over the higher peak. Aether D-15: a conditional form behind a zero-evaluation valley. Ananke: XOR/FLIP are never assembled. Aphrodite: only additive families can be supplied. Is there one law (the hidden axis: gradient exposed toward incomplete machinery) that predicts all five? Or do basin width (the parameter landscape) and assembly geometry (the structural landscape) conflict?
- why it might matter: It is the most North-Star-central open question in D3. It concerns what makes grown mechanisms reachable, and it is testable with instruments that already exist.
- later evidence: none found. No Thread links these seats.
- lenses: Crius, Ares, Aether, Ananke, Aphrodite
- related: H-D3-12, H-D3-44, H-D3-50, H-D3-56, H-D3-57, H-D3-60

### H-D3-65 CROSS-ENGINE: propagation without selection (Aether) vs evolved relay (Ananke)
- source: Aether/pivot/AETHER_REVIEW_2026-09-27.md:467 @ ee81c0474, seat Aether; quote: "- That no local law can propagate content. Nine laws and one parameter regime is a small corner." With roles/Ananke/pte/C1_REPORT.md (RELAY COMM_DEPENDENT, "gate a hand design").
- kind: contradiction
- question: Ananke evolves routed relay under selection on a hand-designed transport physics, while Aether's selection-free byte physics shows almost no propagation. Is content transport something selection builds on minimal physics, something physics must supply, or does Ananke's success rest on its hand-designed packets (the "encoded by construction" risk)?
- why it might matter: It decides whether primitive physics or selection should carry communication in the ecology design.
- later evidence: none found.
- lenses: Aether, Ananke
- related: H-D3-19, H-D3-04

### H-D3-66 CROSS-ENGINE: three memory certificates with no common instrument (Cosmos P1/P2, Ensorain LM01, Ananke SI01)
- source: roles/Cosmos/design/03_c3_design_draft_2026-09-23.md:36 @ e8f6d0ad1, seat Cosmos; quote: "P3 ADVANTAGE (a pressure law): under which conditions retention pays." With ensorain/lm01/STEWARD_RULINGS.md:92 and roles/Ananke/prompts/2026-09-25_pte_si01_directive/01_STEWARD_DIRECTIVE_verbatim.md:149.
- kind: contradiction
- question: Cosmos (persistence + causal utility by state interchange), Ensorain (exact vs coarse retention, a selectivity intervention) and Ananke (relevant/expired/nuisance recoverability) each define "memory that matters" differently. Do they agree on shared specimens, for example Ananke M2's in-flight bit, an Ensorain reservoir, or a Cosmos planted system? Would the Cosmos certificate, run on Ananke M2 as a foreign substrate, classify it FUNCTIONAL?
- why it might matter: The Selective-Irreversibility law is being tested in three places with incommensurable instruments. A cross-certification would give the program one memory ruler.
- later evidence: none found. The SI01 directive forbids copying Cosmos's withheld law (line 601), but not using the public P1/P2 certificate.
- lenses: Cosmos C3, Ensorain LM01, Ananke PTE
- related: H-D3-26, H-D3-32, H-D3-41, H-D3-45

### H-D3-67 CROSS-ENGINE: verdicts decided by the bar, not the physics (threshold provenance)
- source: roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt:192 @ af2af37f4, seat Cosmos; quote: "Q2 The location gate killed laws with 2-4% contradiction rates. Is a 0.10 log2 location tolerance scientifically motivated or arbitrary?"
- kind: open-question
- question: Aether Q3 (no law passed the bar), Ananke C1b (absolute thresholds block labels), Cosmos Q2 (an arbitrary tolerance) and Ensorain E0/E1 (INDETERMINATE on controls) all raise the same issue. Should the program adopt one standard, "tolerances from replicate uncertainty, preregistered as rules not numbers" (Cosmos C3 s1), with planted positives calibrating each bar?
- why it might matter: Falsification instruments are a North-Star deliverable. Unprincipled thresholds turn negatives into non-information.
- later evidence: PARTIAL. Cosmos C3 adopted uncertainty-derived tolerances (03_c3_design s1). Ensorain LM01 added per-stratum positive controls (E6). Aether and Ananke have not.
- lenses: all reducers/gates
- related: H-D3-08, H-D3-43, H-D3-49

### H-D3-68 CROSS-ENGINE: when do transplants and transfers succeed?
- source: ares/ARES_CYCLE2_REPORT.md:240 @ 3f68be2b9, seat Ares; quote: "Transplantability is refuted twice, now with the instrument that could have detected it."
- kind: open-question
- question: Transplant and transfer fail in Ares (refuted twice), Ananke (no cross-family transfer, topology-bound), Crius (donor fragments drop typed links) and Ensorain (transfer tautological, W1). They succeed in Aphrodite (S4 abstraction transplant into 5 unseen-body families) and Crius (a complete-mechanism artifact transplant). Is the discriminant completeness (whole mechanism vs fragment), the level (abstraction vs weights/code), or certification of behavioural identity?
- why it might matter: Heritable transfer of learned structure is how an ecology accumulates. Knowing the discriminant tells us which representations are "portable" units of selection.
- later evidence: none found.
- lenses: Ares, Ananke, Crius, Ensorain, Aphrodite
- related: H-D3-47, H-D3-52, H-D3-34

## Cross-domain pointers
- RunPod platform correctness and billing reconciliation (Aether Q8; receipts reconciled to provider billing in c1cc6e3b9 on origin/aether/research-block): Aether/RUNPOD_ENGINEERING_04_2026-09-27.md (branch). Ops/infra domain.
- Campaign/task-queue work model lessons (known-answer lane E-007, "when the Task structure was and was not useful"): ops/campaigns/C-002/CAMPAIGN.md (branch aether/research-block). Ops/program domain.
- Evidence portability and verification locality (Odysseus TH-006 slice, N2-N5 recorded, attestation pending): roles/Odysseus/th006/REPORT.md; ops/threads/TH-006.md.
- Steward governance: steward-by-comms frozen 2026-09-26, and whether SI01 and LM01 need a steward go: roles/Ensorain/STATUS.md:9; roles/Ananke/prompts/2026-09-25_pte_si01_directive/. Program-governance domain.
- Cosmos withheld-branch ancestor-of-main gate (Q2 "ritual or real?"): roles/Cosmos/campaigns/REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt:180. Provenance/process domain.
- Seat comms deafness (Ares sent 7 messages with 0 replies; Kairos/Elenchus never answered Ananke): roles/Ares/STATUS.md; roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt:164. Comms/ops domain.
- Atlas index: 60 facts UNRESOLVED/CONTRADICTORY and 603 experiments classed UNKNOWN (Archaeon campaign ids cmp2/cmp3/cmp4 collide): roles/Atlas-M2/reports/REPORT_2026-09-19_M2.txt:20-23. Atlas/indexing domain.
- Aphrodite Campaign 1 frozen and unrun, blocked on contracts from Archaeon/Harmonia/Vivarium and benchmark receipts from Nestor: roles/Aphrodite/STATUS.md:33. Belongs to the BEE/NPE/Archaeon substrate domain.
- The Selective Irreversibility companion essay (linked from the Crius essay) is the theoretical source for H-D3-32/45/66: docs/essays (Aporia). Theory/essays domain.
- Archaeon base-role test failing on Nyx manifest drift (reported by Cosmos and Aether): roles/Cosmos/STATUS.md. Test-infrastructure domain.
