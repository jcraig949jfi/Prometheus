# D2 harvest -- origin of replication / heredity / lineage family (Artemis Block A)
- Domain: D2, replication origin, heredity, lineage and attribution across the three Z80 builds (Archaeon SFE line, BEE = Bellerophon z80atlas, NPE = Nestor) plus the cross-engine causal lens.
- Paths covered (main @ d7ec26d37, 2026-09-27): roles/Nestor (FINDINGS.md, STATUS.md, EXPERIMENT_GRAPH.jsonl, campaigns/{z80atlas-*, c9x-explore, cw01 (skim)}), roles/Bellerophon (forensics_2026-09-23, coupling_2026-09-24, atlas_bee, WORLDS_KERNEL_DESIGN v0.2 s13), archaeon/{z80atlas (pivot, postcampaign, census), envgate, envgate2, lineage, rie, causal_lens, frontier (DECISIONS, CHARTER)}, ops/campaigns/C-001/E-001,E-002 RESULT.md, ops/threads TH-001..006 (context only).
- Seat branches read (unmerged): origin/archaeon/deep-block-2026-09-27 @ 72923db05 (Blocks A-D, F, G + operator directive), origin/nestor/s1-forensics-2026-09-23 @ d63b76a5f (NPE W1 donor discovery), origin/bellerophon/multiday-campaign-2026-09-26 @ ee7a7d954 (multi-day prereg; RUNNING, results not in Git). Other branches listed were checked and have 0 commits ahead of main.
- Paths NOT covered: primordial/ beyond README and packet headers (engineering / swarm plumbing; no replication-heredity questions found), prometheus/toolbox beyond README and kernel falsifier list, prometheus/atlas_bee code, roles/Nestor/sidequests/graphworld (skimmed filenames only), roles/*/journal, raw JSON/JSONL result files, evidence held only on M2 disk.
- Method: read-only. git log/show/diff --stat, grep, sed, python3 read-only one-liners over EXPERIMENT_GRAPH.jsonl. No tests, engines or repo scripts run. Each candidate re-checked against later commits on main and the three live seat branches.
- Exclusions: TH-001..TH-006 were not re-harvested verbatim. Where a candidate extends one of them, that is noted under "related". Ordinary ops chores are excluded.
- Counts: 52 candidates. By kind: open-question 17, anomaly 7, defect-ambiguity 6, prior-art-gap 6, unfollowed-recommendation 6, parked-experiment 4, contradiction 3, directive-idea 3.
- Operator concern (three Z80 builds converging) is addressed head-on by H-D2-01, -02, -06, -07 and -08.
- Branch-state caveat: Archaeon's deep block names TH-007..TH-011 but never created those files. origin/aether/research-block-2026-09-27 has meanwhile created an unrelated ops/threads/TH-007.md (Aether). The IDs collide (see Cross-domain pointers).
- Line numbers refer to the file at the cited sha. For branch files, the sha is the branch tip.

### H-D2-01 Are the three Z80 "independent" builds actually independent?
- source: archaeon/frontier/DECISIONS.md:223 @ c7610ea19 (2026-09-19), seat Archaeon; quote: "Built archaeon/z80atlas/ ... as Archaeon's build of the NESTOR 72-hour directive". Also ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md:50 @ 72923db05 (2026-09-27, unmerged): "Three independently written worlds, three independent teams ... three make it a design law."
- kind: contradiction
- question: All three engines were built on 2026-09-19 (98b2149a7 BEE, c7610ea19 Archaeon, aa5833488 NPE) from one operator directive, by agents of one model family. How much of the cross-engine "recurrence" in Block D reflects shared design priors, and how much reflects properties of copy-selected byte worlds? Examples of possible shared priors: an LDIR-class block copy, a neighbour window, first-ruler designs, and harness transplant/migration channels.
- why it might matter: The Block D synthesis rests its strongest claims ("what Prometheus can say only because three engines looked") on independence. A common cause would turn "design law" into "shared design habit", and the North Star needs to know which it is.
- later evidence: none found. Block D s4 concedes "recurrences across three designs, not a controlled comparison" (line 96), but nobody has audited the directive-to-design lineage or run a deliberately dissimilar fourth substrate.
- lenses: Archaeon z80atlas/ENVGATE, BEE z80atlas, NPE, causal lens; would need a non-Z80 substrate (Aether, PTE, Ensorain)
- related: H-D2-02, H-D2-03, H-D2-04, H-D2-06, H-D2-11; TH-001

### H-D2-02 Is every Z80 heredity result a designer-supplied block-copy result?
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:78 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "replication is reachable ONLY through LDIR plus the neutral undefined-byte slide; removing either abolishes it."
- kind: open-question
- question: The pieces: BEE (LDIR off -> 0/300), NPE (C-CORE conserves OP_SELF + LDIR; C-DENSE-COPY gates acquisition on block-copy encodings), and Archaeon ("Copying requires the COPY primitive in this bench", Z80ATLAS_RULINGS_FOLLOWUP_REVIEW:227). Every engine's heredity depends on a single-instruction block-copy primitive that the designers supplied. Can heredity arise, or be sustained, from byte-loop copiers (LDI / LD (T),A loops, 12 of 361 BEE historical origins) when no block-copy primitive exists?
- why it might matter: The North Star is to supply primitives and let mechanisms grow. If the only heredity observed is one opcode's semantics, then the program has studied that opcode rather than the emergence of replication. This candidate also bounds the "three engines converge" claim.
- later evidence: none found. The NPE W1 SELF-free copier still uses LDIR/LDDR (W1_REPORT:77 on origin/nestor/s1-forensics).
- lenses: BEE P8 ablation knobs, NPE dense-encoding lane, Archaeon census
- related: H-D2-01, H-D2-08, H-D2-36

### H-D2-03 Harness channels credited as organism copying: can a ruler be forced to rule them out?
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:9 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Can every reproduction ruler be required to enumerate all channels that move material (harness, migration, splice, transplant) and show zero credit leak?"
- kind: directive-idea
- question: The deep block proposed this as TH-008 but never opened it. Can the v0.3 contract validator be required to show, using synthetic leak fixtures (migration copy, splice, transplant), that every material-moving channel names an explicit non-organism carrier?
- why it might matter: The same error occurred independently in all three engines (Z80xAtlas transplants, BEE POLLINATION P1, NPE splice Z80A-D05). A general guard would protect every future substrate.
- later evidence: none found. schema_v03.py has J21/J22 for referents but no carrier-enumeration rule.
- lenses: causal lens v0.3 validator, all engines
- related: H-D2-01, H-D2-22

### H-D2-04 Cargo erodes while copy machinery is conserved: a law of copy-selected byte worlds?
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md:56 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Replicative machinery is conserved while cargo erodes, unless something explicitly pays for the cargo."
- kind: directive-idea
- question: Proposed TH-007, never opened. Is conserved copy core plus eroding cargo general, and what is the minimal coupling that preserves cargo? The cheapest first step is to measure, from preserved material ids, the per-position founder-material share of Archaeon's block-13 dominant glin. Archaeon is so far only "inferred".
- why it might matter: This determines whether any computation can hitchhike on replication without a designed payment channel. That bears directly on the "reasoning mechanisms co-evolve with representations" goal.
- later evidence: BEE coupling campaign (COUPLING_CAMPAIGN_REPORT.md @ 6a0b9813e) shows v3 copy-resource coupling maintains cargo in 6/6 tasks. The multi-day campaign (RUNNING) tests protection. The Archaeon measurement has not been done.
- lenses: NPE C-CORE/z8taint, BEE coupling v3, Archaeon lineage material ids
- related: H-D2-23, H-D2-17, H-D2-49

### H-D2-05 Reproduction vs mere copying: which births transmit the capacity to reproduce?
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/G_PRIOR_ART.md (Griesemer row) and F_FRONTIER.md:10 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Which recorded 'reproductions' transmit the CAPACITY to reproduce, not just material?"
- kind: prior-art-gap
- question: Proposed TH-009, never opened. For each recorded birth, is the child itself copier-capable? Compare mechanisms (Archaeon SELF_COPY / HOST_EXECUTION / ORIGINATION; BEE copy events; NPE P-11 pair births).
- why it might matter: Under Griesemer's reproducer criterion, many counted "reproductions" are copying, which would deflate every reproduction and lineage count in the record. NPE X-STALL already shows P-11 certifies "a causal rebuild of the victim half, not a fertile child".
- later evidence: partial. NPE X-STERILE finds children 75-80% fertile at birth (FINDINGS.md:314). No per-event capacity field exists in any engine.
- lenses: all three engines, causal lens (would need a capacity field)
- related: H-D2-38, H-D2-22

### H-D2-06 Is acquisition the hard barrier or not? The synthesis contradicts the NPE W1 window
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md:67 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Acquisition, establishment and maintenance are different barriers, and the hard one is not acquisition." Versus roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:53 @ d63b76a5f (2026-09-26, unmerged): "Donor acquisition is the gate in plain physics (~1%)."
- kind: contradiction
- question: Which barrier dominates, and is the answer a property of each substrate or of what each ruler calls "acquisition"? Candidate readings: BEE access 1-5% per run, Archaeon copier prior 9.6e-6 per tape, NPE donor acquisition 1/96 in plain physics.
- why it might matter: Allocation depends on it. Searching for origins and searching for maintenance are different programs.
- later evidence: the W1 report was written a day before Block D, but Block D does not cite it (it cites W1_NPE_LENS, which is different). Unreconciled.
- lenses: NPE W1 funnel, BEE G1/G2, Archaeon census/ENVGATE
- related: H-D2-07, H-D2-08

### H-D2-07 Origins by lottery (Archaeon) vs origins by construction (BEE)
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:60 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "no initial random tape and no mutated initial tape became the first self-replicator in any run. The first self-replicator is built by another organism's writes." Versus archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:233 (Archaeon): "DOES NOT: ... Measure copiers arising by mutation during a world's life, or ones that need an occupied neighbour."
- kind: contradiction
- question: Archaeon explains its one survivor as an initial-founder lottery (lambda 6.86). BEE finds 160/160 origins built by other organisms' copying. Is Archaeon's lottery reading an artifact of a census that only scores isolated random tapes? Would a BEE-style genealogy of Archaeon's surviving copiers show construction too?
- why it might matter: It decides whether origin is a rare draw (so scale the inflow) or an ecological construction process (so study scaffolding). These are different North-Star search strategies.
- later evidence: none found. RIE-01, which would record ORIGINATION glins at scale, is parked (H-D2-30).
- lenses: Archaeon census + lineage core, BEE first_self_replication genealogy
- related: H-D2-06, H-D2-25, H-D2-30, H-D2-47

### H-D2-08 Encoding accessibility as a substrate-neutral coordinate of replication origin
- source: roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:91 @ d63b76a5f (2026-09-26, unmerged), seat Nestor; quote: "A primitive's DISCOVERABILITY is set by its encoding length and alignment, not only by whether it exists. That is a candidate accessibility coordinate for other substrates."
- kind: directive-idea
- question: Does encoding length/alignment of the copy primitive predict the copier prior across engines? Data points: Archaeon vmcopy32 ~1e-5 vs its z80 variant >= 2.7e6 tapes per copier (RULINGS_FOLLOWUP:245), BEE LDIR + undefined-byte NOP slide, NPE 6-byte chain vs 1-byte aliases (C-DENSE 13/40 vs 0/40; C-DENSE-COPY 39/64 vs 1/64).
- why it might matter: A quantitative accessibility coordinate would let designers set the origin rate on purpose, and would test whether the three engines agree once encoding is controlled for.
- later evidence: none found across engines. Within NPE it is confirmed twice.
- lenses: NPE, Archaeon census (vmcopy32 vs z80), BEE P8
- related: H-D2-02, H-D2-06, H-D2-35

### H-D2-09 Hidden effective-mutation channels far above nominal rates
- source: roles/Nestor/FINDINGS.md:318 @ 345e0ceef (2026-09-26), seat Nestor; quote: "This tape-write EROSION is a ~5%/byte/epoch mutation, ~25x the nominal rate."
- kind: prior-art-gap
- question: Do BEE (shared window [L,2L)) and Archaeon (neighbour-window writes, overwrites) also have write-back channels whose effective mutation rate is far above the declared rate? Is heredity loss in each engine explained by an Eigen error-threshold calculation on the effective rate?
- why it might matter: X-ERROR-THRESHOLD found "no dose effect" on the NOMINAL rate. An error-threshold analysis on the effective rate is standard theory that has not been applied here, and it could unify the stall and erosion findings.
- later evidence: C-ATOMIC C1 confirms erosion in one NPE cell. No cross-engine audit exists.
- lenses: NPE pair tape, BEE window, Archaeon lineage core
- related: H-D2-10, H-D2-37

### H-D2-10 Heredity failing in carried execution state rather than in bytes
- source: roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:93 @ d63b76a5f (2026-09-26, unmerged), seat Nestor; quote: "Heredity can fail in CARRIED EXECUTION STATE while the genome is fine."
- kind: open-question
- question: The finding: self-poisoning register state (18/18 stalled donors; C-STATELESS-FFA6 0.33 -> 0.81). Do BEE or Archaeon organisms carry state across executions, and are competence assays in those engines run from a fresh state that hides this failure?
- why it might matter: Every "fresh-state" competence ruler (BEE verify_exact, Archaeon census, NPE P-11 draws) may overstate in-world competence. This is also a non-genetic inheritance channel that the lineage contract cannot represent.
- later evidence: none found outside NPE.
- lenses: NPE, BEE VM, Archaeon VM, causal lens (no state-carrier field)
- related: H-D2-34, H-D2-09

### H-D2-11 Do three axes (CARRIER, RELATION, CONTRAST) plus aggregation suffice? A predictive test
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/B_B1_B6_B8.md:73 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Predictive test (cheapest): take a native field from an engine not yet examined (e.g. Aether or Ensorain). Assign its coordinates BEFORE use, and see whether the misreadings it would cause are predicted."
- kind: open-question
- question: Does the three-axis error taxonomy predict misreadings in an engine it was not fitted on?
- why it might matter: It would turn the false-friends ledger from a post-hoc classification into a falsifiable theory of attribution error, reusable by every engine that joins.
- later evidence: none found.
- lenses: causal lens, FALSE_FRIENDS, Aether, Ensorain
- related: H-D2-12, H-D2-13

### H-D2-12 Is role-splitting bounded, or will each substrate recurse a new referent?
- source: archaeon/causal_lens/V02_REGRESSION_REPORT.md:184 @ 949b9ba4d (2026-09-26), seat Archaeon; quote: "Role-splitting is not yet shown to be bounded: B6 is its first recursion."
- kind: open-question
- question: B4 split material into whose vs where. B6 re-applied that split to the code that governs writes. Will the next substrate force a third recursion (for example, the referent of the state or context the code runs in; compare H-D2-10)?
- why it might matter: If the split is unbounded, a portable lineage contract may not exist, and the lens would need a generative referent rule instead of a fixed list.
- later evidence: Block B (unmerged) reduces B2/B4/B6 to one CARRIER axis. That is a classification and is not tested predictively.
- lenses: causal lens schema v0.3
- related: H-D2-11, H-D2-10

### H-D2-13 Dependence does not chain: do lens errors cluster where it was chained?
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:12 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Do lens errors cluster where a counterfactual-dependence result was chained like a production (flow) result (Hall)?"
- kind: prior-art-gap
- question: Proposed TH-011, never opened. Classify FF-1..FF-34 and the Block B error table by "chained dependence?".
- why it might matter: It is cheap archival work. A positive result would give a method rule for any lineage depth claim built from P-11 or sham-arm dependence tests.
- later evidence: none found.
- lenses: FALSE_FRIENDS, P-11, Archaeon sham arms
- related: H-D2-11, H-D2-22

### H-D2-14 A continuity convention for recombinants: per-unit ancestry (ARG) instead of a singular parent
- source: ops/campaigns/C-001/E-002/RESULT.md:60 @ 0a5c0895d (2026-09-27), seat Artemis-worker/Archaeon; quote: "Architecture continuity under recombination has no usable criterion in PTE ... Whether C-OP' holds in any second substrate."
- kind: prior-art-gap
- question: Block A (unmerged, A_E002_REVIEW:69) lists as unresolved "A continuity convention that practitioners would accept". Block G says the ancestral recombination graph literature keeps per-locus trees rather than recovering a singular parent. Should the lineage contract adopt graded per-unit FLOW/DIFFERENCE shares with a declared convention, and does that behave in Archaeon (RECOMBINATION births) and NPE splice cells?
- why it might matter: Every lineage-depth and establishment count in a recombining world depends on this aggregation choice.
- later evidence: C-OP' was attacked and narrowed in Block A (E1b/E4/E5 counter-cases). It is not adopted and not tested outside PTE.
- lenses: causal lens, PTE, Archaeon, NPE
- related: H-D2-15, H-D2-16; TH-001 (B1)

### H-D2-15 What is the null for a privileged (asymmetric) recombination operator?
- source: ops/campaigns/C-001/E-002/RESULT.md:61 @ 0a5c0895d (2026-09-27), seat Archaeon/C-001; quote: "F2, privileged operators with thin margins. No case appears in Git ... The full distributions are on M2."
- kind: open-question
- question: How should a singular-lineage label be decided when the operator itself favours one parent (Block A E3b: 14/16 is typical under a 90%-a operator)?
- why it might matter: Real operators in NPE (donor/victim) and Archaeon (executor/occupant) are asymmetric, so the unbiased null does not apply to them.
- later evidence: none found. The data sit on M2 (TH-006 locality).
- lenses: causal lens, NPE, Archaeon
- related: H-D2-14; TH-006

### H-D2-16 A non-saturating architecture criterion; the B7 guard is still not in the contract
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/C_B7.md:34 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Any behavioural ARCH criterion must carry a declared non-saturation guard".
- kind: unfollowed-recommendation
- question: Can an architecture or identity criterion be defined that neither saturates at the fitness ceiling nor tracks fitness? The recorded guard (Frontier I-2) is absent from archaeon/causal_lens/schema_v03.py, which has 0 occurrences of "saturat". The OBSERVATORY ask for a PTE non-saturating probe set (OBSERVATORY_DESIGN.md:80) is also unmet.
- why it might matter: Ceiling ties are common (PTE 8 champions, NPE 1,062 genomes, Archaeon 95 tapes). Without the guard, identity claims imported across engines repeat the v0.2 3/48 misreading.
- later evidence: none found.
- lenses: causal lens, PTE, NPE, Archaeon census
- related: H-D2-14, H-D2-20

### H-D2-17 "Inert for attribution" is not "inert for evolution" (GP introns)
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/G_PRIOR_ART.md:29 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "Our 'neutral / inert' units (E-002 identical positions; NPE drift regions) may be doing protective work".
- kind: prior-art-gap
- question: Do the non-core bytes that turn over in NPE runaways (all positions except 23-24 and 52-53), or BEE's undefined-byte slide, protect the copy core from crossover, erosion or overwrite? Test: fix those bytes to constants versus leave them free, and measure runaway or persistence.
- why it might matter: It would refine the reading of C-CORE and cargo erosion. BEE's NOP slide is already known to be necessary for origin (P8), which hints that "junk" is functional.
- later evidence: none found.
- lenses: NPE C-CORE cell, BEE P8
- related: H-D2-04, H-D2-23

### H-D2-18 Reuse hereditary stratigraphy / phylotrack instead of inventing lineage tracking
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/G_PRIOR_ART.md:15 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "ALREADY SOLVED ENGINEERING. For tracking, Prometheus should reuse this rather than invent."
- kind: prior-art-gap
- question: Can hereditary stratigraphy (Moreno, Dolson, Ofria) provide the per-birth ancestry that BEE and NPE currently lack? That is the gap behind "establishment NI" and the 33% of UNRESOLVED BEE births. What does it cost per birth?
- why it might matter: It is instrumentation that could remove the M2-only full-replay dependence (TH-006) and make establishment identifiable in two engines.
- later evidence: none found.
- lenses: BEE, NPE, causal lens
- related: H-D2-20, H-D2-21; TH-006

### H-D2-19 Host-conditioned assay: READY on main, NOT_READY on the unmerged deep block
- source: archaeon/causal_lens/HOST_CONDITIONED_ASSAY_READINESS.md:80 @ 949b9ba4d (2026-09-26), seat Archaeon; quote: "READY_WITH_ENGINE_SPECIFIC_LIMITS". Versus ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:18 @ 72923db05: "Status recommendation: NOT_READY until the NPE arm is restated on P-11-causal events".
- kind: defect-ambiguity
- question: Main's TH-001 and TH-003 still describe "NPE host-conditioned reproduction 16/34". Block D point 5 withdraws that as a reproduction claim (6/34 pass P-11). Which record governs? And is the Archaeon-only arm (by material), which is unaffected, worth running alone?
- why it might matter: A fresh reader of main would schedule an assay on a withdrawn premise. The Archaeon arm alone could test host-mediated reproduction by intervention.
- later evidence: deep-block branch unmerged as of 2026-09-27. TH-003 not yet revised on main.
- lenses: causal lens, NPE P-11, Archaeon lineage
- related: TH-003, TH-004, H-D2-29

### H-D2-20 Observatory ASK fields never adopted; the multi-day BEE campaign launched without them
- source: archaeon/causal_lens/OBSERVATORY_DESIGN.md:68 @ 949b9ba4d (2026-09-26), seat Archaeon; quote: "Proposed ASK fields. Nothing here changes another seat's engine without coordination." (BEE `replaced`, per-birth write counts by code MATERIAL; NPE pre-rename oid; PTE GA parents). First asked in PORTABILITY01_REPORT.md:177.
- kind: unfollowed-recommendation
- question: Should the B6 WHAT-referent counters have been in the 4,160-run, 20k-tick multi-day campaign? It is BEE's largest evidence body, and without them every WHAT claim about it will again need an M2-local full replay. Can they be added as pure observers to future runs?
- why it might matter: Code-material provenance for the biggest BEE run is being lost now. TH-002/TH-005-style questions about it will be NOT_IDENTIFIABLE.
- later evidence: prometheus/z80atlas/world.py was last touched at c9bed96de (coupling prereg), and the multiday branch adds no such fields (diff --stat). Not adopted.
- lenses: BEE multi-day, causal lens
- related: TH-002, TH-005, TH-006, H-D2-18, H-D2-50

### H-D2-21 Establishment is defined three ways and is unidentifiable in two engines
- source: archaeon/causal_lens/FALSE_FRIENDS.md:32 @ 949b9ba4d (2026-09-26), seat Archaeon; quote: "FF-24 | establishment | ... Archaeon: an HU alive 3 x max_age after its root is gone ...; NPE: founder-count dose effects; BEE: undefined (nearest: SUSTAINED = sr_max_depth >= 3)". Also PORTABILITY01_REPORT.md:164: "establishment is not identifiable from BEE or NPE records".
- kind: open-question
- question: What cross-engine establishment measure could be computed natively in all three? The candidates are persistence after the root is gone, depth, and runaway, and they are not equivalent. Do the engines' establishment findings (ENVGATE blocking, BEE SUSTAINED 39%, NPE C-STATELESS "establishment") agree once one measure is used?
- why it might matter: "Establishment is the hard barrier" (H-D2-06) cannot be compared across engines while each uses a different object.
- later evidence: none found.
- lenses: causal lens, all engines
- related: H-D2-06, H-D2-18, H-D2-22

### H-D2-22 Chain-depth endpoints are capped by per-edge certification break rates
- source: roles/Nestor/FINDINGS.md:383 @ 345e0ceef (2026-09-26), seat Nestor; quote: "A per-edge break rate p caps an unbroken certified chain from a fixed root at ~1/p generations, which is exactly the observed founder causal depth (5-22)."
- kind: defect-ambiguity
- question: Does the same ceiling apply to BEE sr_max_depth / SUSTAINED depth >= 3 and to Archaeon genetic depth >= 10? That is, do they measure certification luck rather than heredity? Which births break certification in each engine (Nestor's "open instrument question", FINDINGS.md:353)?
- why it might matter: Depth thresholds are primary endpoints in all three engines (NPE C-RUNAWAY depth >= 20, Archaeon establishment rule, BEE SUSTAINED). A shared artifact would bias every cross-engine depth comparison.
- later evidence: partially answered for NPE (mostly C2 + C4 failures on partial copies; FINDINGS.md:383). Not examined for BEE or Archaeon.
- lenses: NPE P-11, BEE adjudication, Archaeon lineage core
- related: H-D2-05, H-D2-21, H-D2-13

### H-D2-23 C-CORE vs purifying selection: a non-circular test of what is inherited
- source: roles/Nestor/FINDINGS.md:376 @ 345e0ceef (2026-09-26), seat Nestor; quote: "C-CORE is exactly what PURIFYING SELECTION on a functional core plus drift elsewhere predicts; it is not evidence for any stronger account, and calling SELF/LDIR 'relevant' because they survived would be circular."
- kind: open-question
- question: Measure per-position mutational fitness effects independently, for example single-byte knockouts in isolation, before looking at conservation. Then predict which positions are conserved. Does anything beyond purifying selection (for example, a Selective-Irreversibility-type ratchet) predict conservation that fitness effects do not?
- why it might matter: It turns a descriptive confirmed finding into a discriminating one, and it is the only route by which the NPE chain could bear on the SI program without the retrofit that was withdrawn.
- later evidence: none found. The SI framing was withdrawn by operator directive 2026-09-26 (FINDINGS.md:389).
- lenses: NPE 7ae3 cell, z8taint
- related: H-D2-04, H-D2-17; Cross-domain SI pointer

### H-D2-24 BEE out-of-position own-copying: 847,000 births where provenance and resemblance disagree
- source: archaeon/causal_lens/V02_REGRESSION_REPORT.md:124 @ 949b9ba4d (2026-09-26), seat Archaeon; quote: "D1 BEE resemblance vs provenance (FF-27, 847k) | provenance says writer | REMAINS_REAL_DISAGREEMENT (not rotations; architecture NI)". Also line 135: "AN7 BEE frame-shifted copying ... REMAINS (not frame shifts; architecture NI)".
- kind: anomaly
- question: In these births the writer copies >= L/2 of its own bytes but out of position, and they are neither rotations nor frame shifts. What copying mechanism is this? Is it a distinct heritable architecture?
- why it might matter: It is a large, unexplained reproduction class in BEE, and positional-fidelity heredity rulers systematically misattribute it.
- later evidence: none found.
- lenses: BEE traced replay, causal lens
- related: H-D2-25; TH-002

### H-D2-25 Context-dependent copiers that copy nothing in isolation
- source: roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md:110 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "context-dependent copiers that write nothing when run alone 57 (16%)".
- kind: anomaly
- question: 16% of BEE origin tapes copy only in a population context. Archaeon's census, by design, cannot see copiers "that need an occupied neighbour". What fraction of replication in each engine is context-dependent? Are these scaffolded reproducers in Godfrey-Smith's sense?
- why it might matter: Isolated-tape rulers (Archaeon census, NPE fresh-state P-11, BEE isolation assays) would undercount exactly the scaffolded class that Block D point 4 highlights.
- later evidence: none found.
- lenses: BEE, Archaeon census, NPE X-DD-NOCOPY-CONTEXT
- related: H-D2-07, H-D2-10, H-D2-24

### H-D2-26 The five BAND0 establishments: what carries establishment when the window is closed?
- source: archaeon/envgate2/VERDICT_2026-09-26.md:60 @ c5ba19571 (2026-09-26), seat Archaeon; quote: "both came in at 5, about 7x the prediction. Something outside the frozen window model carries establishment when the window is closed."
- kind: anomaly
- question: Which copiers or mechanisms established in the all-blocked arm? Were they non-128-gated copiers, host-mediated, or ORIGINATION glins?
- why it might matter: This is the direct residue of a failed mechanistic model. Explaining it could reveal the actual environmental dependence of establishment.
- later evidence: kept as a fossil, explicitly "NOT allocation targets" (ENVGATE_CLOSURE:20). TH-001 lists it without a child thread. Rows exist in RESULTS.json per_block.
- lenses: Archaeon ENVGATE-02 preserved rows, lineage core, census ruler
- related: H-D2-27; TH-001

### H-D2-27 Blocks 11/13/14: establishment concentrates in the slowest worlds
- source: archaeon/envgate2/VERDICT_2026-09-26.md:63 @ c5ba19571 (2026-09-26), seat Archaeon; quote: "Establishment in the non-U arms concentrates in blocks 11, 13 and 14, which were also the slowest blocks by wall time (5.9, 3.3 and 5.9 h against a median of 1.0 h)."
- kind: anomaly
- question: Is wall time a proxy for a different ecological regime (more executions, larger live population, a takeover) that permits establishment independently of the input window?
- why it might matter: It could be a hidden block-level covariate in both ENVGATE assays. Cheap to test from the preserved block files.
- later evidence: none found. Deep-block commit message mentions a "block-13 probe" (archaeon/causal_lens/deep_block/block13_probe.py, unmerged) aimed at TH-007/TH-009, not at this heterogeneity.
- lenses: Archaeon ENVGATE-02 block files (M2-local)
- related: H-D2-26

### H-D2-28 From copier founders to survivors: a conversion model, not lambda
- source: archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:263 @ 863d34a55 (2026-09-23), seat Archaeon; quote: "Q1 Is lambda (worlds containing a copier founder) the right quantity to compare with 1 survivor, given that gating makes most copier founders fire rarely ... A tighter model would predict survivors, not copier-worlds." Also ENVGATE01_REVIEW:320 Q3 (branching process R0 = 60 x k/256 too simple).
- kind: open-question
- question: What is the copier-founder to established-lineage conversion probability as a function of gating, occupancy, overwrites and host amplification? It is currently estimated from 1 event (~1/7).
- why it might matter: Inflow sizing and any "lottery-consistent" claim rest on it. It also connects origin rates to establishment across engines.
- later evidence: none. RIE-01 tier 1 (unbiased event rates arrivals -> copier -> first reproduction -> establishment) was designed to measure this and is parked.
- lenses: Archaeon census, RIE-01
- related: H-D2-30, H-D2-07, H-D2-21

### H-D2-29 Host-mediated reproduction: a confound of chamber designs, or the phenomenon to study?
- source: archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:323 @ 2b3661444 (2026-09-24), seat Archaeon; quote: "Q4 Does host-mediated reproduction make chamber designs unsuitable for the next ecology, or is it the phenomenon to study?"
- kind: open-question
- question: The reviewer question was never answered in a ruling. Ruling R2 kept host-mediated reproduction as a mechanism, but no experiment has made it the object of study. Should it become one, by intervention on the host (Archaeon arm of the host-conditioned assay)?
- why it might matter: Block D point 4 (origins scaffolded) and prior art (Tierra parasites, Godfrey-Smith) make host dependence central. Archaeon's material attribution (72% vs 28%) is the novel contribution according to Block G.
- later evidence: TH-001 lists "host-conditioned assay ... not preregistered". Deep block recommends NOT_READY for the NPE arm only.
- lenses: Archaeon lineage, host-conditioned assay
- related: H-D2-19, H-D2-30

### H-D2-30 RIE-01 (dependency liberation / acquisition map) is staged and never launched
- source: archaeon/rie/world.py:7 @ 87f51c5ee (2026-09-24), seat Archaeon; quote: "liberation    founder EXACT_GATED -> dominant descendant with a strictly larger exact-input set (or ungated); or early hosted -> later self". Status: ENVGATE_CLOSURE_2026-09-26.md: "RIE-01 | correctly NOT launched ... It stays staged and unfrozen".
- kind: parked-experiment
- question: In a random-inflow ecology, do lineages evolve out of environmental gating or host dependence (liberation), or into it (acquisition)? What are the unbiased transition rates?
- why it might matter: This is the only built instrument in the domain aimed at how dependence structures evolve, which is closest to "mechanisms co-evolve under pressure". It was gated on a model (the window) that failed, not on its own merit.
- later evidence: none. Its precondition (the ENVGATE-02 Phase-C gate) failed. PORTABILITY-01 s16 bars ENVGATE-03, not RIE.
- lenses: Archaeon rie/, lineage core, census ruler
- related: H-D2-28, H-D2-29, H-D2-07

### H-D2-31 Genetic re-audit of the ENVGATE-01 worlds was never run
- source: archaeon/envgate2/VERDICT_2026-09-26.md:69 @ c5ba19571 (2026-09-26), seat Archaeon; quote: "The genetic audit of the ENVGATE-01 worlds and RIE-01 are NOT started."
- kind: unfollowed-recommendation
- question: Under genetic identity (glin), what do ENVGATE-01's 475 established lineages (parent-chain counted) reduce to, per arm? Does the ENVGATE-01 blocking effect hold at the magnitude claimed?
- why it might matter: ENVGATE-02 showed parent-chain counts inflate by 8-42x. ENVGATE-01's adjudicated record still rests on parent-chain lineages for some numbers.
- later evidence: archaeon/lineage/audit_envgate01.py exists (tool present). No audit result committed.
- lenses: Archaeon lineage core, ENVGATE-01 evidence archive (M2)
- related: H-D2-26

### H-D2-32 Why does 7ae3 establishment not respond to stateless execution when ffa6 does?
- source: roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:97 @ d63b76a5f (2026-09-26, unmerged), seat Nestor; quote: "Resolve the 7ae3 / ffa6 split. Why does register persistence limit establishment in ffa6 (SLOTTED, NICHES_HIGH_MIG) and not confirmably in 7ae3 (Z8_64, WELL_MIXED)?"
- kind: open-question
- question: As stated. Mutate one cell axis at a time (representation, then structure) under STATELESS vs DENSE.
- why it might matter: It localizes which world property makes carried state heritable-poisonous. That is the first mechanistic handle on establishment in NPE.
- later evidence: none. W1 window closed 2026-09-26. C-STATELESS on both cells was NOT_CONFIRMED (p = 0.012).
- lenses: NPE
- related: H-D2-10, H-D2-39

### H-D2-33 Remove the scaffolds: does evolution find dense encodings or state-robust copiers on its own?
- source: roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:100 @ d63b76a5f (2026-09-26, unmerged), seat Nestor; quote: "Remove the scaffolds. Ask whether evolution finds state-robust copiers or dense-like encodings on its own".
- kind: open-question
- question: Every confirmed NPE spontaneous-heredity result depends on experimenter-relieved barriers (in-place search, free self-location, energy inheritance, 1-byte aliases, atomic write-back, stateless execution). Can any be removed in favour of an evolvable mechanism, for example a mutation operator that creates short encodings?
- why it might matter: This is the North-Star crux: grow rather than hand-design. At present heredity appears only in a world where the designer has removed each barrier.
- later evidence: none found.
- lenses: NPE; parallels BEE P8 and Archaeon census
- related: H-D2-02, H-D2-08, H-D2-35

### H-D2-34 The spontaneous SELF-free pair-tape copier class (n = 1)
- source: roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md:77 @ d63b76a5f (2026-09-26, unmerged), seat Nestor; quote: "A SELF-free pair-tape copier arose spontaneously. It uses LDIR/LDDR with register values produced by incidental arithmetic on the fixed tape layout, not self-location. Hypothesis, n = 1 specimen."
- kind: open-question
- question: Characterise the class across the 49 + 39 donor runs. Is incidental self-location via fixed layout the typical spontaneous route? Does it make C-CORE's "OP_SELF is conserved" a property of the implanted specimen only?
- why it might matter: If the spontaneous route bypasses OP_SELF, the confirmed core and the "self-location is the gate" finding (E-6) are specimen-bound.
- later evidence: none. L1 ruler (SELF+LDIR) already corrected as "7ae3's route, not the spontaneous route".
- lenses: NPE
- related: H-D2-23, H-D2-33

### H-D2-35 Energy inheritance matters for seeded depth but not for spontaneous depth: why?
- source: roles/Nestor/FINDINGS.md:255 @ 345e0ceef (2026-09-26), seat Nestor; quote: "The exploratory claim that energy inheritance matters for depth in SPONTANEOUS replicators did NOT confirm (depth >= 2: 3 vs 3); E-7 (seeded copier) is unaffected."
- kind: anomaly
- question: Seeded copiers hit a newborn-starvation wall that energy inheritance relieves (20/40 vs 4/40), yet spontaneous replicators under dense encodings do not respond. Do spontaneous replicators differ in cost structure (shorter programs, cheaper copies), or is the test underpowered?
- why it might matter: It bears on whether barriers found with implants transfer to spontaneous origins, which is a general methodological worry for seeded-lineage research (BEE B0 also recommends seeded study).
- later evidence: none found.
- lenses: NPE
- related: H-D2-33, H-D2-45

### H-D2-36 Can descendants acquire copy competence their founder lacks?
- source: roles/Nestor/FINDINGS.md:357 @ 345e0ceef (2026-09-26), seat Nestor; quote: "C-SWAP-ACQUIRE NOT CONFIRMED (frozen at 82b6caeb3): 9/240 vs 0/240 founder-descended runaways, p = 0.0018; the rule needed 10 vs 0."
- kind: open-question
- question: X-ACQUIRE puts 9-15% of runaway populations on genomes that copy where the founder cannot. Is descendant acquisition of competence real, given that the confirm missed the bar by one run and anc-descent is not content inheritance?
- why it might matter: Evolution improving the replicator is the minimal "machinery evolves" event. This is the closest the record has come to it.
- later evidence: none. X-CONTENT caveat (FINDINGS.md:362) says founder material is a 13-25% minority, so "descended" is lineage, not content.
- lenses: NPE, z8taint
- related: H-D2-37, H-D2-05

### H-D2-37 Lineage descent vs content inheritance: what should count as a descendant?
- source: roles/Nestor/FINDINGS.md:362 @ 345e0ceef (2026-09-26), seat Nestor; quote: "Every 'founder-descended' statement above ... is lineage descent, not content inheritance."
- kind: defect-ambiguity
- question: When a lineage label passes through overwrites and only the copy core survives, is "descent" the right unit for heredity claims in any engine? Should cross-engine claims require a material share threshold (IBD at informative sites)?
- why it might matter: Runaway, critical-mass and swap claims in NPE and establishment in Archaeon all use label-based descent in part.
- later evidence: Block B (unmerged) maps this onto the RELATION axis (FLOW vs DIFFERENCE). No endpoint rule adopted.
- lenses: NPE anc/z8taint, Archaeon glin, causal lens
- related: H-D2-14, H-D2-36

### H-D2-38 Competence is a genome x cell property: which cell factors?
- source: roles/Nestor/FINDINGS.md:334 @ 345e0ceef (2026-09-26), seat Nestor; quote: "competence is a property of genome x cell, not of the genome."
- kind: open-question
- question: 7ae3's genome copies from a fresh state at 0.955 only in 7ae3 and ffa6, which differ only in representation and structure, and at 0.0 in ten other cells. Which cell factors (pressure, reproduction physics, niche) disable a competent copier?
- why it might matter: Heredity that is portable across environments versus heredity bound to its niche is a basic question about whether any replicator can be a general primitive.
- later evidence: none. X-DONOR-SWAP was exploratory only (WEAK_SIGNAL). The planned "localize which cell factors block" branch (STATUS) was not run.
- lenses: NPE
- related: H-D2-32, H-D2-39

### H-D2-39 Why does 7ae3 copy only from tape side 1?
- source: roles/Nestor/STATUS.md:53 @ 345e0ceef (2026-09-26), seat Nestor; quote: "open question worth a child: 7ae3 copies only from tape side 1 (runs second) - why, and does side asymmetry matter in the world?"
- kind: open-question
- question: As stated.
- why it might matter: Execution-order asymmetry on the pair tape may be a hidden structural cause of which organism becomes donor. That would bear on WHO/WHAT attribution in NPE and on TH-004 (donor writes not necessary).
- later evidence: none found (no graph node on main or on origin/nestor/s1-forensics).
- lenses: NPE pair tape
- related: H-D2-38; TH-004

### H-D2-40 Reservoir / easy-niche stepping stones for heredity remain untested
- source: roles/Nestor/FINDINGS.md:277 @ 345e0ceef (2026-09-26), seat Nestor; quote: "H3 -- NOT_DEMONSTRATED (R3 material certificates 1/1/0 of 64): crossings are frequent in one cell but made of hard-niche material; the easy niche does not raise them." Also FINDINGS.md:214: "C9-D11 | H3 certificate walks non-causal pair edges in RECOMBINATION cells (NOT repaired; operator decision)".
- kind: parked-experiment
- question: Do refugia or easy niches act as stepping stones for lineages crossing hard environments once lineage records log migration (P-1 repaired) and certificates follow material? Does the unrepaired C9-D11 contaminate the H3 null?
- why it might matter: Spatial stepping stones are a standard open-endedness mechanism. The predecessor question (A-5) was unanswerable and the successor carries a known unrepaired defect.
- later evidence: none after C9.
- lenses: NPE niches/reservoir
- related: H-D2-22

### H-D2-41 The endogenous-accessibility assay (H4) needs redesign and is withheld
- source: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/S4_CANDIDATE.md:21 @ 459d465a4 (2026-09-24), seat Nestor; quote: "H4 endogenous | 4 blocks x 16 pairs x 2 | 4 x 16 x 2, NOT enlarged | 128 | the S1-B autopsy shows the assay needs redesign first". Also EXPERIMENT_GRAPH C9-H4 status WITHHELD; FINDINGS C9-D07: "H4 endogenous arm cannot reproduce, so H4 cannot test accessibility".
- kind: parked-experiment
- question: Is a task solution more accessible when reproduction is endogenous than when it is external, in a design where the endogenous arm actually reproduces?
- why it might matter: BEE G3 answered the reverse causally (EXTERNAL 178 vs 2), but only for BEE physics. NPE never got a valid test, so the cross-engine reading is one-sided.
- later evidence: BEE GROUNDING G3 (3efdacf7e) and the coupling campaign reframed the question. No NPE redesign found.
- lenses: NPE, BEE
- related: H-D2-49

### H-D2-42 Why do unselected BEE origins mostly die, and fresh worlds go 95-100% extinct?
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:172 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "New uncertainties: why unselected origins mostly die (competition vs overwriting vs hostile random neighbours)".
- kind: open-question
- question: As stated. Also: why do only WELL_MIXED topologies survive (73% extinct vs 95-100%)?
- why it might matter: This is the BEE establishment barrier (39.4% sustained). It is the direct BEE analogue of the NPE establishment and Archaeon ENVGATE questions and the natural cross-engine comparison point.
- later evidence: none. The coupling and multi-day campaigns moved to seeded founders (B0) and did not address fresh-origin mortality.
- lenses: BEE
- related: H-D2-06, H-D2-21, H-D2-44

### H-D2-43 Do replication "ramps" have selectable intermediates?
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:147 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "incremental construction (ramp) | ... 52% with a partial copier in line; mostly 1 decisive byte | PROVISIONAL (a short ramp + small step; selectable advantage of intermediates not tested)".
- kind: open-question
- question: Do partial copiers (>= 25% window) leave more descendants than non-copiers, so that selection builds replicators incrementally rather than by one lucky byte?
- why it might matter: Incremental selectable paths versus cliffs is the origin-of-life question in miniature, and it decides whether pressure can grow replicators.
- later evidence: none found.
- lenses: BEE
- related: H-D2-07, H-D2-44

### H-D2-44 Knockout validity: NOPing the copy opcode is not a knockout
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:107 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "NOPing the copy byte is not a knockout in this chemistry" (ablated arm still self-replicates in 126/345, 124 via a copy instruction at a new position).
- kind: defect-ambiguity
- question: Are knockouts used elsewhere also rescued by a nearby re-creation of the primitive? Cases: NPE C-CORE position claims, the Archaeon copier-founded exclusion, and BEE's own G4 "nopped" mechanism effect. What is the right ablation (remove the setup, per B4)?
- why it might matter: Causal mechanism claims in all three engines use single-site ablations, and a shallow, wide replication basin makes them unreliable.
- later evidence: the recommendation is recorded in NEXT_CAMPAIGN_RECOMMENDATION B4. No cross-engine audit found.
- lenses: BEE, NPE, Archaeon
- related: H-D2-17, H-D2-23, H-D2-43

### H-D2-45 Reproduction-computation antagonism: general, or a BEE copier artifact?
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:97 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "the effect that exists has the opposite meaning (reproduction-computation ANTAGONISM). Underpowered (n = 11)."
- kind: anomaly
- question: The grafted LDIR routine destroys the task witness, and 85% of "beneficial" mutations break the copier. Is antagonism between copy machinery and computation general across engines, or specific to whole-window LDIR copiers?
- why it might matter: If it is general, every co-evolution design needs explicit modularity or payment. That is the premise of the multi-day Q2 (protection).
- later evidence: the coupling campaign shows payment maintains competence. E2 conflict repair was 4/60 vs 0/60 (ns). Multi-day Q3 is testing repair (RUNNING, results pending).
- lenses: BEE, NPE (C-CORE cargo turnover), Archaeon
- related: H-D2-04, H-D2-47

### H-D2-46 Paid computation executed from partner code: the coupling reward credits WHO, not WHAT
- source: roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md:81 @ 6a0b9813e (2026-09-25), seat Bellerophon; quote: "Correct outputs by organisms whose own tape is not competent (partner-code execution in the SHARED window, lucky partial solvers): 1-6% of paid correct outputs in most lanes, 14.6% in Lane F, 25% in Lane J".
- kind: defect-ambiguity
- question: The copy resource pays the executing organism (WHO) for computation that may be governed by a partner's code (WHAT), which is B6 inside the fitness function. Does a material-referent payment rule change what the multi-day campaign selects for? And do partner-code executors become a parasite class (NEXT_MULTIDAY Q4)?
- why it might matter: Selection is aimed at the referent the reward reads. A WHO reward can favour window-placement parasites over computers.
- later evidence: Q4 (ecology) was dropped from MULTIDAY_PREREG (only Q1-Q3 on origin/bellerophon/multiday-campaign-2026-09-26). Not tested.
- lenses: BEE coupling v3 / multi-day, causal lens B6
- related: H-D2-20, H-D2-47; TH-002

### H-D2-47 Is YOKED a fair no-contingency control? Per-capita matching
- source: roles/Bellerophon/coupling_2026-09-24/REVIEW_PACKET_COUPLING_2026-09-25.md:171 @ 98a28dd39 (2026-09-25), seat Bellerophon; quote: "Is YOKED a fair no-contingency control, given it matches total supply per tick but spreads it evenly? Would a per-capita-matched yoke change P2/P4?"
- kind: unfollowed-recommendation
- question: As stated.
- why it might matter: The contingency interpretation, "computation causes reproduction", rests on YOKED. The multi-day campaign reuses the same yoke for all acquisition claims.
- later evidence: MULTIDAY_PREREG line 52 keeps the per-tick total yoke. No per-capita arm.
- lenses: BEE coupling / multi-day
- related: H-D2-46, H-D2-48

### H-D2-48 Multi-day outcomes pending: ladder acquisition, protection, repair
- source: roles/Bellerophon/coupling_2026-09-24/NEXT_MULTIDAY_CAMPAIGN.md:10 @ 6a0b9813e (2026-09-25), seat Bellerophon; quote: "Evolution of machinery that preserves, improves or reorganizes computation BECAUSE computation now finances reproduction." Also REVIEW_PACKET:173: "ECHO is output = input. Is 29 vs 6 of 150 acquisition of 'computation' or of a trivial I/O idiom".
- kind: parked-experiment
- question: Q1 (ECHO->INC->COND_ONE acquisition), Q2 (damage-exposed robustness, replacing the ceiling-bound r_cc, F6/F7), Q3 (repair > 4/60). Whatever the verdict, is the reviewer's "trivial idiom" objection answered by the INC rung?
- why it might matter: It is the single largest running test of "computation-driven machinery evolution" in the program.
- later evidence: launched 2026-09-26T16:40Z (ee7a7d954), blind until md_analysis.py runs. No results in Git as of 2026-09-27.
- lenses: BEE multi-day
- related: H-D2-45, H-D2-46, H-D2-47, H-D2-49

### H-D2-49 Superlinear per-run cost at long horizons: what grows?
- source: roles/Bellerophon/multiday_2026-09-26/receipts/SCALE_PROBE_2026-09-26.json @ ee7a7d954 (2026-09-26, unmerged), seat Bellerophon; quote: "ticks": 500 ... "wall_s": 58.8 ... "ticks": 5000 ... "wall_s": 3048.9, "peak_rss_mb": 597 (commit 41f73bc0e: "superlinear").
- kind: anomaly
- question: Runtime grows about 52x for 10x ticks and memory about 14x. Is this bookkeeping (event logs, lineage records) or a biological signal (populations executing longer programs, copy-length or bloat growth)?
- why it might matter: If it is biological, it is an unmeasured evolutionary trend (bloat or complexity growth) in the long-horizon runs. If it is bookkeeping, it bounds feasible horizons.
- later evidence: none found. A 2.8x measurement-only speedup (515a675ae) addresses cost, not cause.
- lenses: BEE multi-day, profile_probe.py
- related: H-D2-17, H-D2-48

### H-D2-50 Implicit-pressure BEE results: the task never touched the dynamics
- source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:54 @ 3efdacf7e (2026-09-23), seat Bellerophon; quote: "the task score never changes who lives, dies or reproduces -- the task is causally INERT in these worlds."
- kind: defect-ambiguity
- question: Which earlier BEE, Atlas-feed or NPE-comparison claims were drawn from IMPLICIT-pressure cells and so carry no task causation? Does the NPE pressure axis (A-2: EXPLICIT_FITNESS vs NONE_IMPLICIT, +0.30) have the same inertness?
- why it might matter: Any "task independence of replication" or task-effect claim from these cells is NOT_ADJUDICABLE. They may still be cited in the evidence wiki or the Atlas.
- later evidence: the grounding report marks the BEE instance NOT_ADJUDICABLE. No sweep of downstream citations or of NPE found.
- lenses: BEE, NPE, Atlas
- related: H-D2-41

### H-D2-51 atlas_bee a6b: does BEE resolve the e07 memory-damage question?
- source: roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md:194 @ 933ee9f02 (2026-09-19), seat Bellerophon; quote: "Next (a descendant, not a repair): a6b, selecting memory-load-bearing organisms before the weather arms, would test whether BEE RESOLVES e07".
- kind: unfollowed-recommendation
- question: As stated. Also: can BEE's differential role (interrogating findings rather than voting on them) be used systematically on the NPE heredity findings, for example transplanting C-ATOMIC or C-DENSE-COPY into BEE?
- why it might matter: It is the program's only built cross-ecosystem transplant harness, and it has been idle since 2026-09-19.
- later evidence: none found (no a6b commit on any branch).
- lenses: BEE atlas_bee harness, Atlas
- related: H-D2-01

### H-D2-52 BEE-wide location-vs-material divergence rate on a random sample
- source: ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:11 @ 72923db05 (2026-09-27, unmerged), seat Archaeon; quote: "run the T-001 recipe on a RANDOM sample of 20 BEE runs on ubu nodes (about 30 CPU-min); report the location/material divergence rate with a CI."
- kind: unfollowed-recommendation
- question: Proposed TH-010, never opened. B6 rests on 2 BEE runs "chosen for being rich in 'decoupled' births" (V02_REGRESSION_REPORT.md:186). What is the population-wide rate? This narrows TH-002 to its cheapest discriminating step and adds a sampling-design requirement that TH-002 lacks.
- why it might matter: It separates a selected-specimen curiosity from a systematic bias in BEE's SR counts.
- later evidence: none. Coordination with Bellerophon is required (TH-002 constraint).
- lenses: BEE, causal lens T-001 recipe, ubu nodes
- related: TH-002, TH-005, TH-006, H-D2-20

## Cross-domain pointers
- Ops/thread IDs: ops/threads/TH-007.md on origin/aether/research-block-2026-09-27 (Aether) collides with Archaeon's proposed TH-007..TH-011 in ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md (origin/archaeon/deep-block-2026-09-27). Needs an ID allocator ruling.
- Selective Irreversibility: roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md plus the Nestor withdrawal at roles/Nestor/FINDINGS.md:389. SI relevance of C-CORE / X-CORE-TIME is left "for the operator to adjudicate separately".
- Cue-reading obstruction is the price of reading, not the ordering (C9-H1R, COST_INTERACTION_ONLY): roles/Nestor/FINDINGS.md (E-9). This is a task/representation question, not heredity.
- Seeded moat and shallow CONST tasks (375 epoch-0 crossings): archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:267 (Q2-Q4, allocation/support design).
- Ratchet ordering ambiguity (simultaneous vs sequential gains): roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e02/RESULT.json ("unresolved_ambiguity").
- Neutral-marker hitchhiking bounds gene-order resolution (fixation ~gen 26 vs drift ~96, deferred): roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e06/DISPOSITION.json; DEFECTS CW01-D027.
- TAPE vs TREE compactness: TREE's only advantage may be dynamic (subtree crossover): roles/Nestor/campaigns/cw01-2026-09-17/DEFECTS.jsonl CW01-D055. This is a representation-domain question.
- Kernel falsifiers F3/F4/U1-U3 (per-episode observation series for experience-to-competence not in receipts): roles/Bellerophon/WORLDS_KERNEL_DESIGN_v0.2.md:263.
- Atlas ADAPTATION concept (TRANSPLANT_OF edge; adaptation table proposal): roles/Bellerophon/atlas_bee/ATLAS_EXTENSION_PROPOSAL.md:16 (Atlas schema domain).
- Cosmos C3 holdout D delivered on an unmerged branch: origin/nestor/c3-holdout-d-2026-09-25, roles/Nestor/C3_HOLDOUT_D_REPORT.md (Cosmos domain).
- Aether propagation physics (minimal local law for causal influence), relevant to H-D2-11 as the "unexamined engine": origin/aether/research-block-2026-09-27 ops/threads/TH-007.md.
- Evidence locality (M2-only BEE traces, ENVGATE block files, NPE replays) recurs in H-D2-15, -20, -27, -31: ops/threads/TH-006.md.
