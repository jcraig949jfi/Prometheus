# ATLAS_ONTOLOGY_GAPS_VNEXT -- an attack on Atlas's own primitive inventory

Atlas[m1-a5680f90], inference harvest of 2026-09-30 (operator directive, verbatim at
roles/Atlas/prompts/2026-09-30_inference_harvest/01_OPERATOR_DIRECTIVE_verbatim.md, sha256 b2b7ad26).
Everything in this file is ATLAS_DERIVED unless a row is tagged RAN, OBSERVED or CONCLUDED. The
evidence rows come from seven read-only digests of the record (listed in INFERENCE_HARVEST_HANDOFF.md s3).
Every pointer is path@sha or comms #id, as the digests give it. Atlas has no authority over any seat.
This file proposes changes to ATLAS'S OWN vocabulary only.

The inventory under attack is roles/Atlas/theory/PRIMITIVES.jsonl @f8df65681: 20 primitives, 15 with an
axis rule, and 5 UNMEASURED.

---------------------------------------------------------------------------------------------------------
## 0. The finding that comes first: Atlas's combination table is null by construction

OBSERVED (live index, SELECT only, 2026-09-30; digest atlas_index_and_history s6):
- Every experiment-level `primitive_use` row carries the evidence text "inherited from <engine> via campaign".
- The 90 POSITIVE/WEAK_POSITIVE experiments and the 90 NEGATIVE/NULL/FAILED experiments carry the SAME three
  primitive tuples (69/17/4 vs 66/20/4). Every pair count is within +/-3 between the two groups.
- The 1,242 Vivarium experiments have no primitive_use rows.
- The 5 UNMEASURED primitives have zero rows anywhere.
- atlas_class POSITIVE counts infrastructure PASSes together with science: 649 of the 723 POSITIVE rows are
  Vivarium "completed" queue jobs.

ATLAS_DERIVED consequence: "combination X precedes success" CANNOT be answered from the index today. A
"combination" is currently an engine label. The 2026-09-24 soup table (89 TESTED / 85 UNEXPLORED / 16
SUGGESTED) measures co-presence in catalogues, not co-occurrence in experiments that moved. Every
ROADMAP statement built on it is a statement about which engines exist. This is Atlas's own defect, and it
is the reason this file ends with an experiment-level INTERVENTION MATRIX (s7) built by hand from the
digests. That matrix is the seed for tagging primitives per experiment (ATLAS-39 redefined in s8).

---------------------------------------------------------------------------------------------------------
## 1. The five UNMEASURED primitives: instrumentation gaps, not science gaps

The inventory says each of the five is UNMEASURED because "no indexed source records" it. The record says
otherwise. For four of the five, seats have already RUN interventions on the primitive. Atlas simply has
no rule to read those interventions from experiment designs.

| primitive | Atlas's reason (PRIMITIVES.jsonl) | interventions that already exist in the record (RAN/OBSERVED, pointer) | verdict |
|---|---|---|---|
| write_authority | "write permissions live in substrate specs and code" | NPE ATOMIC write-back (a tape half changes only by an accepted copy): runaway 1/80 -> 46/80 (C-ATOMIC C1, roles/Nestor/FINDINGS.md:328-334 @19ef51610). Aether `add` (combine instead of replace): frozen fraction .927 -> .696 (Aether/AETH-03/PHYSICS_DESIGN_01 s6 @43202cf7b). PTE freeze_rule -> 0.52; forbidding the switch at the readout site -> .500 exactly (roles/Ananke/research/workers/W-H). SFE import takeover: incompetent imports take over 12/12, like competent ones (archaeon/campaign3/CAMPAIGN_REPORT s0 @cb9135104). BEE "own code" measured as WHO / WHERE / WHAT, with 27,083 of 28,163 location-foreign births made of own material (comms #741) | **INSTRUMENTATION GAP.** Measurable from arm definitions today. It is also the most consequential unmeasured primitive: it moved outcomes in four substrates |
| temporal_gating | "a property of the interpreter" | NPE mutation gated behind birth: 907/907 zero-variation births (FINDINGS E-1). C9 answer gate: competence 0.200 -> 0.000 only when reading the cue costs (C9-H1R I = +0.20). PTE latency +1 kills M3 (0.493), latency -1 improves it (0.741); clock phase splits S/C/N blends (C1b s4; W-R). Aether rcv, where a written site fires once, is the only single law with multi-generation propagation, 6/128 (PHYSICS_DESIGN_02) | **INSTRUMENTATION GAP.** Readable from arms: gate on/off, latency and phase shifts |
| reproductive_closure | "requires an ablation ... that no indexed experiment reports" | BEE EXTERNAL-only 178 vs ENDOGENOUS-only 2 verified task pairs (GROUNDING s6 @2159c2e06). BEE world-made copies (POLLINATION v1 vs v2: extinction 0/150 vs 148/150). Archaeon host-mediated reproduction ("amplification, not origination", ENVGATE-01 R2). Parasites: 0/120 isolated capability vs 117/120 in the self-performed class (REVIEW_7_ADJ, BRANCH:archaeon/attribution-arc-2026-09-28@9c8cfed55). NPE: the environment supplies self-location, since 280/280 SELF-free copiers are tape-anchored (SYNTHESIS P2 s4 @948b3a45f) | **INSTRUMENTATION GAP, with a ready quantitative proxy:** the ratio of relational to isolated capability of a birth (E-003 ERRATA X4: 0.124 of all births are relationally but not isolatedly capable) |
| partial_heredity | "no indexed source records offspring-parent similarity as a continuous quantity" | Artemis CVT-R: transmission of parental variation over 2 generations; 19 P-11-certified genomes fail (comms #891). NPE X-CONTENT: founder byte share 0.134-0.253 under full "lineage descent" (FINDINGS:368-372). E-003 Q8c 0.00115 transmission defect rate. BEE `material` label disagrees with copy-descent in 0.504 of births | **INSTRUMENTATION GAP.** Three continuous measures now exist (CVT-R recurrence, byte-share, Q8c). The record also shows a NEW phenotype the definition does not name: **construction without transmissible variation** (the 19 CVT-R failures; the 17 "painters") |
| error_correction | "needs a measured fidelity and a channel baseline" | NPE: only 6-11% of certified copies are exact; tape-write erosion runs ~5%/byte/epoch, ~25x the nominal rate (X-STALL, FINDINGS:316-327; A3S s3). BEE r_cc 0.9987, at ceiling (COUPLING s1). Archaeon C5 FIZZLE: skipping a faulted opcode recovers 209 vs 15 (campaign5 s3.4). No engine has shown EVOLVED error correction | **PARTLY a science gap.** Fidelity and a channel baseline now exist (NPE erosion is a channel measurement). EVOLVED repair has never been observed, and no experiment was designed to see it. Designed recovery (FIZZLE) exists only as world physics |

**Operator-relevant bottom line:** four of the five "unmeasured" primitives are not unmeasured science.
They are unmeasured BY ATLAS, because its detection rules read catalogue axes instead of experiment arms.
The fifth (error correction) is half-measured: fidelity yes, evolved repair never.

---------------------------------------------------------------------------------------------------------
## 2. Aliases: primitives that are the same thing, or that hide the same thing

| alias set | evidence of identity | proposal |
|---|---|---|
| self_location ~ environment-supplied addressing ~ reset/initialization | NPE: 95.7% of competent donors are SELF-free offset-64 copiers that work only at tape offset 0; the zero reset plus the tape position IS the self-location (P2S s4). Archaeon vmcopy: 0.9896 of exact copiers are gated to ONE input byte, around the hardcoded neighbour base 128 (census RESULTS @c5067fac6; Artemis R-26 via #874, a worker claim). Establishment rescue is ZERO-specific: 26/48 vs CONST 2/48 vs RANDOM 3/48 (C-ZERO-SPECIFIC) | Split self_location into (a) **self_location_internal**, meaning computed by the organism (NPE: only 2/332 true locators), and (b) **addressing_supplied**, meaning a constant, offset or reset the world provides. Nearly every "self-location" in the record is (b) |
| copy_mechanism ~ "a copy op exists in the ISA" ~ "somebody copies" | The definition joins "executed by the organism OR by the runner". Those two are opposite on reproductive closure. BEE LDIR off: spontaneous SR 8/300 -> 0/300. Archaeon z80 (no COPY op) 0 copiers in 1.2e7 random tapes vs vmcopy 96/1e7. BEE world-made copies drove the old topology effect | Split into **copy_affordance** (a primitive op exists, with its encoding length), **copy_executor** (organism / host / world / runner) and **copy_material_source** (whose bytes). The same experiment can score differently on each |
| memory_persistence ~ local_state ~ "in-flight/channel state" | PTE M2 stores the bit in packets in transit: flushing in-flight packets mid-gap -> 0.497, while S and inbox resets have no effect (C1b s4). Seat's words: "it schedules, it does not store". Archaeon FF-20: "causally load-bearing, non-material state" | Add **channel_state** (state held only in transit) as distinct from local_state and broadcast_state |
| selection_pressure ~ admission ~ payment | The 751 experiment rows are inherited. The record separates in-world differential reproduction (BEE contingent payment vs YOKED: extinction 1 vs 67 of 150), experimenter admission gates (Hecate admission 24%; C5 world screen 9/25) and fleet promotion (sigma_kernel.PROMOTE never re-runs the battery, Harmonia stall map s2) | Split into **in_world_selection**, **payment_coupling** (computation -> reproduction resource) and **admission** (experimenter/gate). Admission belongs on the ruler side (s5), not in the substrate |

---------------------------------------------------------------------------------------------------------
## 3. Too broad

- **local_state (751 experiment rows):** conflates execution registers (which the zero reset controls),
  genome bytes, and write-once "scars" (PTE W-E/W-G: frozen signed writes that are read as interference).
  Registers behave like environment on reset worlds and like heredity-breaking load on carried worlds
  (BEE CARRIED 0/24; NPE fresh-state 0.33 -> 0.81). Split: execution_state vs structural_state vs scar.
- **memory_persistence:** conflates retention (Ensorain exact records help RECALL +0.86 and are neutral on
  novel cells, |dAC| <= .02), integration (PTE W-L: every "retention" champion is an integrator, and so is
  the n=0 control), and presence without use (see s4 "use"). The record shows these move independently.
- **environment_generation:** used for the NPE graphworld and for catalogued ecosystems. It does not
  separate worlds made by a generator from worlds made by the experimenter, and Hecate shows that
  generator reachability is the binding constraint (12/29 built worlds untestable at Pass 3 v1).

---------------------------------------------------------------------------------------------------------
## 4. Important mechanisms with no primitive

Ranked by how many independent substrates show an outcome moving under them (independence per s6).

| # | missing primitive / dimension | definition (proposed) | substrates where it moved an outcome (OBSERVED) |
|---|---|---|---|
| M1 | **initialization_regime** | what state the world hands a new executor or organism (zero, constant, random, carried) | NPE C-ZERO-SPECIFIC (26/48 vs 2/48 vs 3/48 vs carried 6/48); BEE carried registers kill zero-dependent founders (0/24 vs ZERO 10/24, REPL PREREG s3 D2); PTE SETRULE bootstrap to rule 0 because registers are 0 at tick 0, in 27/42 cells (W-B), which the seat calls "a PHYSICS ARTIFACT"; graphworld "sham beats scratch" +1.400 and scale-only +2.10 (GW/P7:127, replay_r8) |
| M2 | **encoding_accessibility** | encoded length / frame alignment of an operation, separately from whether the op exists | NPE 1-byte copy alias: 1/64 -> 39/64 (C-DENSE-COPY); non-pair 0/40 -> 13/40 (C-DENSE); Odysseus: ~2.4 decades per copy-loop byte (BEE; EXPEDITION s4); Aphrodite "accessible vs representable"; Hecate prose vs tuple presentation: alien T2 .91 -> .78 while known stays .99 |
| M3 | **use_coupling** (decodable != used) | whether information present in state is consumed by the readout | CW01 cycle 8: the regime word sits in a register that predicts the regime at 1.0 and is NEVER used; PTE W-I/W-V: 80-95% of pairs carry mirror-different traffic that swapping does not affect; Cosmos L5 "distance is not information"; Aether "activation timing, not content" |
| M4 | **executor_referent** (WHO / WHERE / WHAT) | which of executor, code location and code material an ownership claim refers to | BEE pc < L = WHERE; material = WHAT; 27,083/28,163 (#741). Archaeon's parent-chain labels inflate lineages 8-42x over genetic identity (envgate2 VERDICT) |
| M5 | **search_tie_policy** | whether the search accepts neutral moves, and its step horizon | PROTEUS-46 greedy 3-step walk (cannot accept neutral ties) vs Artemis D002-03q 5-edit neutral path; C5 "flat elite" vs Deep Frontier equal-compute climbs at every N (.479-.562 vs .382); PTE plants beat champions (.999 vs .755) |
| M6 | **variation_operator_geometry** | whether variation is count-fixed or fraction-fixed, and whether it acts before measurement | CW01: count-fixed rulers manufactured 4 of 7 damage claims; the mutation operator is itself count-fixed (length grows by acceptance, not proposal: P-C03 +1.80 vs +0.30); NPE Z80A-D05: fidelity was read after the splice, manufacturing 910/1,031 |
| M7 | **scaffold_status** (supplied / internalized / withdrawn) | a process coordinate, not a primitive: which supplied support the lineage has taken over | NPE C-A3-INTERNALIZE 8/144 (register init; material 8/8 X-MAT); placement internalized 2/332; BEE REPL-01 event signature only under a partial scaffold, and transient; Odysseus: "all three [Z80 cases] are a lineage INTERNALISING something the world supplied" |
| M8 | **horizon** | how long the assay runs relative to the process timescale | Aether rcv_str reach 8 -> 19 between 400 and 10,000 ticks (E-008); FR-081: 0/181 WTP-03 worlds have lifetime <= 600, so the learning-time/lifetime ratio is unobservable |

---------------------------------------------------------------------------------------------------------
## 5. Dimensions missing ENTIRELY: the ruler side

Atlas's ontology describes substrates. The record says the dominant cause of reversals is the RULER
(proposition P-measurement-before-mechanism is Atlas's only STRONG one). Atlas records no ruler properties
per experiment. Proposed experiment-level fields, each with the failure it would have caught:

| field | meaning | failure it would have caught (examples) |
|---|---|---|
| ruler_can_return_opposite | shown to return the opposite outcome on a same-substrate positive/negative | K3 founder snapshot (0/93, could not reach SURVIVES); Tyche H1 (3 valid worlds < 4 needed); Hecate detector (0 UNFAMILIAR calibration items); Artemis R-11: 37/94 absence-reading gates never shown to fire |
| zero_parameter_baseline | the result vs a zero-parameter restatement of the target or label | Cosmos C0 laws tie the definition rung (McNemar p .125-.688); C3 zero rule 104/120; Ensorain N6 tuned completion beats all 9 WTP-03 flags; Hecate: 5/5 reduced to known mechanisms |
| ruler_id (shared) | a stable identity of the instrument, so independence is counted per ruler | P-11 underlies all NPE "competent" claims; BEE SR/material labels underlie Bellerophon, Archaeon E-003 and FR-091; the CLIP OE score underlies ASAL, Nyx and Techne |
| author_family | the model family that wrote hypothesis, code, ruler and review | "These two hypotheses are currently observationally identical ... It cannot be closed at one author" (Harmonia REVIEW_20260812 s3) |
| measured_before_or_after_variation | whether the observation precedes the variation operator | Z80A-D05 splice |
| frozen_vs_adjudicated verdict | a frozen analysis verdict vs the final adjudication | ENVGATE-01 frozen CAUSALLY_SUPPORTED -> operator PARTIALLY_SUPPORTED; E-003 VALIDATED -> ALTERED |

---------------------------------------------------------------------------------------------------------
## 6. Presumed-independent primitives that are causally entangled

| pair | entanglement (evidence) |
|---|---|
| self_location x local_state (initialization) | In NPE, "self-location" is the zero register state plus tape position. Withdrawing the reset destroys placement but not register init (C-A3-INTERNALIZE; A3S s5-s6) |
| copy_mechanism x write_authority | Pair-tape heredity is killed by write-back of both halves, ~25x erosion; restricting write authority (ATOMIC) restores it (C-ATOMIC C1). In this substrate you cannot test copying without fixing who may write |
| selection_pressure x resource_coupling | BEE's YOKED control (same total bonus, non-contingent) separates them: extinction 1 vs 67/150, competence .77 vs 0. The only clean disentanglement in the record |
| copy_mechanism x self_location | C-ABLATE: removing free self-location cuts replication 15 -> 1 (p 6.1e-5) |
| communication_topology x temporal_gating | PTE RELAY is topology-bound (random graph -> 0.50 in 4/4) but timing-tolerant (shuffled timing .73-.88) |
| competition x write_authority | "Import takeover is mechanics": whoever writes into the population takes it, competent or not (C3-SFE-10) |
| memory_persistence x horizon | Ensorain: after a world change, data availability, not memory policy, is the binding loss (.36-.95 AC); no fixed window works (LM02) |

---------------------------------------------------------------------------------------------------------
## 7. Seed of an experiment-level INTERVENTION MATRIX (the only honest combination table Atlas can offer)

Rows are primitive interventions that were actually RUN; columns are substrates. Each cell is OBSERVED
outcome movement with a pointer in the digests. The "shared ruler" column marks where the cells are not
independent. Directions: up = the phenomenon appears or grows under the intervention; down = it disappears.

| intervention | NPE (Z80 pair-tape) | BEE (Z80 soup) | Archaeon z80atlas / Proteus VM | PTE | Aether | other | shared ruler? |
|---|---|---|---|---|---|---|---|
| supply / densify a copy op | up: 1/64 -> 39/64; 0/40 -> 13/40 | down when removed: 8/300 -> 0/300 | z80 0 vs vmcopy 96/1e7 | -- | -- | -- | NO (P-11 vs SR label vs census); SAME ISA family |
| zero vs carried initialization | ZERO 26/48 vs carried 6/48 | carried 0/24 vs ZERO 10/24 | -- | registers 0 at t=0 -> SETRULE bootstrap 27/42 | -- | GW sham +1.40 over scratch | NO; the NPE/BEE ISA is shared |
| restrict write authority | ATOMIC 1/80 -> 46/80 | own-code WHO/WHERE/WHAT split | import takeover 12/12 regardless of competence | freeze_rule -> .52 | add vs replace: frozen .927 -> .696 | -- | NO |
| gate an operation in time | mutation at birth only -> 0 variation; cue-cost gate I = +.20 | -- | -- | latency +1 kills, -1 improves | rcv fire-once -> the only propagating law | -- | NO |
| remove a zero-parameter restatement (baseline rung) | -- | -- | CMP1 transfer died under CRN | -- | rcv "is a CALIBRATION LAW" | Cosmos laws tie the rung; Ensorain N6 beats 9/9; Hecate 5/5 reduced | NO (different attacks, one style) |
| extend the horizon | long runs: founders decided in ~12 epochs | multi-day 20k ticks | Deep Frontier equal compute: every N climbs | -- | reach 8 -> 19 at 10k ticks | -- | NO |
| accept neutral moves in search | neutral walk ~ soup rate (pilot ratio 1.75, p .20; WP-9 never run) | -- | PROTEUS-46 greedy blind; D002-03q 5-edit neutral path | plants beat champions | -- | Tyche 2/72 adaptations | NO |

ATLAS_DERIVED reading: every row has at least two substrates where the SAME primitive intervention moved an
outcome, and in most rows the rulers differ. These are the combination-level facts the index could not
produce. They should replace the co-presence soup as the input to any future roadmap. (Any roadmap run
needs operator authority; this file proposes none.)

---------------------------------------------------------------------------------------------------------
## 8. vNext proposals for Atlas's OWN ontology (Atlas-internal; nothing here instructs a seat)

1. Redefine ATLAS-39: instead of "detection rules for 5 primitives" from catalogue axes, tag PRIMITIVE
   INTERVENTIONS per experiment ARM (s7 schema: primitive, direction, substrate, ruler_id, outcome delta,
   pointer). Seed it with the s7 matrix (about 30 cells).
2. Add the primitives M1-M4 (initialization_regime, encoding_accessibility, use_coupling,
   executor_referent). Add the process coordinates M5-M8 as experiment fields, not substrate primitives.
3. Split copy_mechanism, self_location, selection_pressure and local_state as in s2-s3. Keep the old ids as
   parents so earlier rows stay readable. Migrations only: add, never rename (migration 003 rule).
4. Add the ruler-side fields (s5) to atlas.experiment. Nothing counts as "independent evidence" in
   proposition confidence unless the rows differ in ruler_id AND substrate lineage.
5. Retire the co-presence soup (atlas.combination) as an input to scoring. Keep it only as a catalogue view.
6. Record atlas_class for science and for infrastructure separately (649/723 POSITIVE are queue completions).

Falsifier for this whole file: if experiment-level tagging (proposal 1) of about 100 experiments finds the
same primitive-combination distribution in moved and unmoved experiments, the missing-primitive claims in s4
lose their support, because none of M1-M4 would then separate outcomes.
