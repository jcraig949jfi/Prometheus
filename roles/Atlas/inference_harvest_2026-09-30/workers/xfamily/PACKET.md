# Observation packet

These are results from about 12 artificial-life, artificial-physics and learning
simulation engines built by one research program, coded E1..E12.
Each numbered line is one observation: the engine code, what was varied or
measured (in plain words), and the numeric outcome.
Lines are in random order; they are not grouped by engine or by date.
Numbers are as recorded; "vs" separates arms of one comparison.
Some engines share instruction-set ideas (e.g. byte tapes, copy instructions).
Several lines report a measurement procedure being changed and what then changed.
No interpretation by the original experimenters is included.
Treat each line as a raw observation, not as a conclusion.

L001 [E8] Cycle membership 0.37x of both null models; per-field association: opcode .003x, arg1 .002x, energy 1.58x.
L002 [E5] Repaired physics, 12,130 runs: organisms copying themselves with their own code from random start, pooled 55/2,400 = 2.3%.
L003 [E5] Well-mixed vs local / niche / graph topologies: extinction 73% vs 95-100%.
L004 [E7] Repeated adversary rounds re-fired identical deterministic attacks in 3 of 4 rounds.
L005 [E7] A simple rule 'next-step reliability above chance' scored balanced accuracy .910 vs .500 for the design's target test on 48 rows; second certificate agrees with the first 47/48; the target test registers on 60/60 continuous rows.
L006 [E2] Table predictor restricted to 10 newest features: baseline accuracy 1.000 / .995 / .547 / .998 / .518 across five worlds.
L007 [E4] Two-key task W2_K2: 0 full solutions in 24 + 54 runs; plateau elites store one value (6/12 store the first PUT, 4/12 the last PUT); 0/480 greedy paths reach 0.9.
L008 [E12] Re-reading 16-byte / 36-byte claims with top-1 instead of top-16 readout: 1.121 / 1.283.
L009 [E4] Flat vs graph program encoding, two-key probe, 4,267 / 4,881 children: useful 0 vs 0; destroyed .70 vs .36; neutral .27 vs .64; greedy 3-step walks reaching the target 0/100.
L010 [E1] Reading the sign of packet payload component 1 instead of component 0: decodes the output at 1.00 (component 0 gave 0.44); swapping component 1 between trials flips the output.
L011 [E4] Graph program profile triggers detectors ~100x less often than the default profile.
L012 [E3] Blocking input window 120..135 across 24 blocks: lineage establishment 24 -> 5; restoring input 128 / 128..131 / 125..128 gave 5 / 3 / 2 (no recovery).
L013 [E11] Rank-tax arms: competent lineages 2 / 1 / 2 / 3 per arm (frozen minimum 6); scalar burden control 1.725 vs tax 0.834 vs tax+amplifier 0.512.
L014 [E6] An organism keeps its id while its bytes are replaced: id-to-genome identity 0.97 after 1 epoch, 0.00 by epoch 600.
L015 [E6] 64 fresh seeds: 27 deep lineages; 17/27 conserve the 4 core bytes; position 23 conserved 27/27, position 52 23/27, all others <= 13/27.
L016 [E1] Frozen relay program moved from its lattice to a random graph: accuracy 0.50 in 4/4 graphs.
L017 [E4] Dose surface (57,536 rows, 126 programs): loss rises +.145 per doubling of k vs +.024 per doubling of number of sites; at k=8, 1 site .66 vs 8 sites .77; operand edits .36 vs delete/opcode/move edits .72-.75.
L018 [E7] Mined phase-boundary rule, sealed holdout worlds D/E/F: balanced accuracy .983 / .972 / .930; second rule on F .955.
L019 [E5] 845 runs, 28,964,089 births: 847,000 births where the native label credits the target as parent though the organism built itself; 33.1% not identifiable; of 28,163 births executed at a foreign location, 27,083 are own material and 21 foreign.
L020 [E8] Graph-rewriting artificial chemistry, 512^2 x 2 seeds: source starvation accounts for 89% of edge hazard; sustained cut of feeder edges vs sham at +128 ticks 0.39 / 0.40; long-edge persistence 0.39x sham.
L021 [E4] Transferring fragments of prior search material, under common random numbers at n >= 10: effects +0.009 and +0.002; shuffled-fragment controls beat intact fragments.
L022 [E6] Answer gated on consuming a cue, with a VM cost for reading vs a free cue: competence 0.200 -> 0.000 with cost; 0.197 vs 0.197 free (interaction +0.20).
L023 [E10] Development runs: a key-lookup learner ~0 AC on never-seen cells; the positive control passes in 8/29 testable strata.
L024 [E9] Admission of one world per program per round: 76% of 243 mechanisms never tested; mechanisms stated as a world rule admitted 0/10.
L025 [E8] Pairwise rule combinations: fire-once+combine sustained share .172, fire-once+steering .109, fire-once+conditional .016; positive control that should preserve copied content preserved content in only 3.1% of origins (clean fixture 21/21).
L026 [E5] When base energy income is never limiting, 5 of 6 task cells run identically, run for run.
L027 [E11] State persistence set to none: score .72 -> .03.
L028 [E1] Relay task, evolved programs: held-out accuracy .837-.883 with packets vs .50 with packet exchange disabled; at N=2,304 nodes .882.
L029 [E9] Validation rule for the novelty detector was passed by a lookup-table baseline (AUC .844 / .852); lawful-vs-noise discrimination AUC .98.
L030 [E3] Random populations at the parameters of the best world: self-sustaining replicator appeared in 0/80 runs, 95% CI [0, 0.0451]; 6 positive controls passed.
L031 [E8] 92.3% of sites unchanged over 64 ticks; edge recurrence after lesion 0 up to +500 ticks (<= 0.5% in 3 seeds).
L032 [E1] Majority-task program: dropping packets only on the readout tick -> 0.511/0.500; adding +1 tick latency -> 0.493/0.500; removing 1 tick latency -> 0.741/0.715 (dropping packets over a window that excluded the readout tick gave 0.697/0.686).
L033 [E2] One fused sensor built from two individually uninformative inputs: gain +0.075 (z 5.6); on fresh seeds +0.101 / +0.109.
L034 [E4] Replacing fixed-count damage with independent per-instruction damage at fraction f (Bernoulli): 4 of 7 earlier damage effects disappear (e.g. 'longer programs are protected'), 2 shrink, operand-vs-opcode difference remains (-.19 over 124 pairs); fixed-count and contiguous variants reproduce the vanished effects.
L035 [E5] Byte-level ancestry of one run (32,827 births, 2,878,487 written loci): share of transmitted bytes 0.00115 [0.00098, 0.00134]; the native parent label disagrees with copy-descent 0.504 [0.456, 0.552], n 395; own-index agreement 0.962.
L036 [E2] 32 worlds, 27-op sensor genomes over linear/tree/table predictors: 2,368 sensors evolved, 44 admitted at z >= 4.
L037 [E4] Walks that convert invalid-instruction traps to no-ops: length grows +1.80 vs +0.30 for other walks; proposals balanced for length grow length more (+2.35).
L038 [E7] Six planted test systems x 5 seeds for a decodability/causal-swap certificate: v2 failed (one incoherent seed; one passes on a 4-decimal tie); v3 passed on fresh seeds 6-10; full-state swap effect .000 for the passive system vs 1.000 for functional ones.
L039 [E1] One frozen relay program run at network sizes N=400 / 1,024 / 2,304: accuracy .875 / .893 / .882.
L040 [E2] Worlds whose target is XOR/parity of delayed inputs, each input individually uninformative, equal budget 6,000 evaluations: cells solved by arm V0 3, DENR 2, DE 1 of 10; parity-3 and one other world unsolved by all arms.
L041 [E6] Evolved genome vs random implant placed in foreign cells: 9/240 vs 0/240 deep lineages (p .0018).
L042 [E10] Planted low-rank positive controls: held-out R^2 .007 (learner could not build it); with latent order + 10 sweeps, efficiency 8.63 vs low-rank baseline 2.03 at size 192; structure identification .20 / .15.
L043 [E4] Alternative representation, 96 cells: 0 held-out gains; one arm 0/24 improved; the elite was still the starting parent after 36,000 evaluations.
L044 [E5] Register initialisation ZERO vs P90 vs P75, 30 transplanted founders, 300 runs: qualifying lineage events 18 / 57 / 36; 93/200 vs 18/100, p 6.6e-7; founder-content test passed 0/93; founder content share ~0.01 by tick 500 in every arm; longest common substring median 2 vs random null 1.
L045 [E10] Exact-record budget B = 216 / 864 / 1,728 / full: accuracy on never-seen cells .2 / 1.2 / 2.0 / 2.6 AC.
L046 [E10] Bounded window assay (11 regimes x 8 worlds): no window meets >= 6/8 in any regime; stratified bound stale .124 (> .10 bar); loss from missing data .36-.95 AC; held-out reference passes 83/88.
L047 [E8] Horizon test to 10,000 ticks: radius grows in 16/19 (fire-once+combine) and 8/19 (fire-once+steering); 6/32 origins set a new max generation after tick 2,000 (bar 10%).
L048 [E6] Non-pair physics with an implanted copier: free self-location 13/36 vs 0/36 (p 1.6e-10); giving children half the parent's energy at birth 20/40 vs 4/40 (p 7.2e-5).
L049 [E4] Changing trap handling to NOP or HALT on the degenerate programs: improving and cross-task-gain children = 0 in 839 children per rule.
L050 [E12] 16-byte 4-bit compressed controller: progress above floor 1.591 [1.139, 1.827] over 32 runs / 4 RNG families; leave-one-family-out 4/4 but one family's CI low .9964; 3/32 runs below floor, all in one family.
L051 [E7] McNemar test on class-imbalanced strata (share .6): power .20-.40 for good candidates; sign-flip test on balanced accuracy .99+ at n 160.
L052 [E6] Of the 57 passing organisms: 2 copy themselves, 1 copies context-dependently, 17 write a fixed pattern regardless of their own bytes, 37 do nothing from any start state tested; re-assay from fresh state: 6/57 pass.
L053 [E2] After the switch, 62/92 new sensors were formed by fusing sensors from different lineages; 63/92 reused a part that previously served a different function.
L054 [E4] Opcode edits are 2.3x more lethal than operand edits under both damage procedures.
L055 [E4] Mate-splice recombination: children 8 points less viable, no new behaviours.
L056 [E1] Packet-passing integer-tensor world; 16-op programs evolved by GA (population 96 x 36 generations), 6,596 rows over 12 h: cells whose accuracy depended on packet exchange = 8/352.
L057 [E6] Non-pair physics, 1-byte aliases for allocate/copy/birth instructions: replication 13/40 vs 0/40 (p 3.8e-5); removing free self-location 15 -> 1; removing search 15 -> 6; extra energy for depth 3 vs 3.
L058 [E6] Removing the zero reset abruptly vs gradually after establishment: persistence difference 0.00 (12/12 persist); robust share .22 -> .94 (abrupt), .24 -> .93 (gradual), .15 -> .10 (control that keeps the reset).
L059 [E7] Power simulation of a design gate: a predictor that only knows the world family passes the first gate in 200/200 simulations (uplift .201); a family-dependence clause alone rejects a true universal law with probability ~.40.
L060 [E7] Recoding one register with a repetition code: 43/300 verdicts flip; rule with mechanism-level coordinates balanced accuracy .961 (wrong hazard .866).
L061 [E7] Null distribution of an early fragment test contained expressions equivalent to the reference: q99 = 1.000; gate unpassable for size >= 5.
L062 [E1] Relay program with packets disabled, maximum packet loss, or shuffled destinations: accuracy 0.50-0.52; with only packet timing shuffled: 0.73-0.88.
L063 [E11] Organism limited to one 3-bit nudge per tick: single-op ceiling 142.5-159.0 vs abstain floor 159.0; 0/64 competent; 3-op chains overfit the 8 training cases.
L064 [E2] Error/disagreement residual under a perturbation: error .261 -> .140 and disagreement .492 -> .735 while accuracy stayed flat.
L065 [E8] Move-instead-of-copy variant: 98.9% of differences stay at generation 1; 41% of divergences die.
L066 [E6] Lineage members at epoch 100: 177/192 no longer copy from a fresh state (187/192 with mutation off); children copy at birth in 75-80%; 57% of interactions change the genome by ~5.5 bytes, ~5% per byte per epoch, ~25x the nominal mutation rate.
L067 [E3] The founder of the largest takeover (3,419,189 births) was already an exact self-copier at depth 0.
L068 [E6] Entry state ZERO vs 0x5A: survival share 0.867 vs 0.111; deep lineages 23/48 vs 3/48; exact copies 4/63 and 38/340; post-copy losses in child material .51/.63.
L069 [E3] 94% of neutral mutations landed on bytes that were never executed.
L070 [E11] Tape-genome task worlds, exhaustive single-edit census (12,880 edits per genome): 0 edits improve; a 4-instruction XOR solution exists but every prefix scores 0.0; seeding one solution among 95 genomes fixes 10/12 runs.
L071 [E2] Share of living sensors carrying any building block of the new law before the switch: .115 (lexicase arm) > .075 (reserve arm) > .055 (strict arm); carrying all blocks <= 0.0006 mean, max .007.
L072 [E4] Graph encoding, 50 walks x 300 steps: a 5-edit duplicate-then-diverge path exists with 4 neutral steps (score 3/6) then 6/6; the greedy acceptance rule never accepts a neutral child.
L073 [E3] Same replay: share of the aligned founder genome 0.90 at epoch 14,000 -> 0.09 at 17,500-19,900 while median exact self-copy fidelity stays 0.83; non-copier children 72% dead on arrival, 0 alive at 20,000.
L074 [E5] 4,160 runs, 47.1 h: task ladder 1 climbed 58/320 vs 0/1/0 in three controls; copier lane 36/240 vs 4/2/2; ladder 2 0/240 in every arm.
L075 [E10] Windows N/12..N/2: competence passes 0-25 of 88; contamination .26-.39; stratified statistic recovery .76.
L076 [E6] Fresh register state at every execution vs persisted state: establishment 34/42 vs 11/33 (p 3e-5) in one cell; both cells 23/29 vs 11/24 (p .012).
L077 [E5] Block-copy instruction removed / cost x4 / made to halt: spontaneous self-replication 8/300 -> 0/300 in each variant.
L078 [E5] Replacing every copy instruction with NOP in 345 historical self-replicating origins: 126 (36.5%) still self-replicate, 124/126 via a copy instruction at a new position.
L079 [E3] Replay to epoch 20,000 (655,307 births): grafting a copier's executed path plus data (mean 21/32 loci) into another tape transfers copying at 0.89, vs 0.057 for a size-matched random graft and 0.028 for the knockout-necessary loci alone.
L080 [E10] Keeping exact old records with a regime gate vs discarding: change on stale split -1.153 (all records obsolete) .. +0.856 (none obsolete); on generalisation split -0.137 .. -0.005.
L081 [E10] Exact-oracle pilot: for the Even process no finite window reaches the Bayes loss, interior optimum k=6 (excess .060); key-value task with 64 / 256 / 1,024 table slots excess 1.512 / .728 / .040.
L082 [E8] Exact twin assay (1,280 pairs), one-bit difference: only the fire-once-when-written variant sustains propagation, 6/128 origins, generation 12, radius 11; baseline reaches generation 56 but radius 3.
L083 [E2] Count-mod-3 world: sensor gain +0.675 (replicated); delayed-XOR world stuck at gain 0.029-0.037 for 40 generations.
L084 [E5] Initial population audit: 103/160 organisms born by copying; 57 initial writers, 26 unmodified.
L085 [E6] Founder dose k = 1, 2, 4, 8, 64 seeds each: s(k) = 1 - (1 - p)^k with p = .13 fits (superadditivity LRT p .42); 4 founders vs 1: 41/80 vs 5/80.
L086 [E11] Price on genome length: genomes shrink 44 -> 5-6 instructions at unchanged reward.
L087 [E8] Relay writes replace instead of add in the combine combination: 22/128 -> 10/128 (additive null 5/128), lower in all 4 seeds.
L088 [E1] Mixed clock-phase programs: which of two per-trial behaviours occurs was predicted at 1.00 in 4 units by one latency-jitter draw on the source's first broadcast (found post hoc, replicated on a fresh namespace); the same predictor failed on 3 other programs (e.g. 22/22 misses).
L089 [E3] Worlds seeded with a hand-written task solution: 98.2% crossed the task threshold, 77.3% of those at epoch 0; random-initialisation worlds crossed in 45.8%, mostly at late epochs.
L090 [E4] 1,568 eligible single-edit children of one parent: 0 improved, 61.7% neutral, 4.7% deleterious, 33.6% lethal; rule-of-3 upper bound on improvement .0019.
L091 [E1] Same search on an XOR task: 0/83 cells packet-dependent; on a FLIP task 0/82.
L092 [E6] Random implant vs the evolved genome in the same cell: 0/80 vs 46/80 (p 1.3e-18); 100% of the final population carries the founder marker.
L093 [E5] Instruction-set ladder L0-L3t: probability a random program self-copies 2.7e-5 -> 1.4e-5 -> 5.1e-9 -> impossible within 256 steps; generic write only 2.1e-10; no reset pointer 1.7e-14.
L094 [E3] An earlier window-blocking test's significance came from a single takeover world and host-labelled non-independent lineages; block-level p = 0.5.
L095 [E5] Mutation supply medium / low / very low: rate of reaching self-replication 8 / 3 / 4 of 300; evolutionary activity 60 -> 48 -> 11 of 60.
L096 [E9] World generator v1: 12 of 29 built worlds untestable; control-first v2: 0 of 8 untestable.
L097 [E10] Learner not told the state count: 14/14 predictions on a 4-world ladder; 2/6 held-out random machines refuted at T=4,000.
L098 [E6] Lineages founded by donors that need zero-initialised registers: 8 lineages in 144 runs became able to construct from random registers (7 in one cell); at the first donor 1/94 runs had this ability.
L099 [E6] Non-pair physics with mutation only at birth: 907/907 runs had zero births of variants.
L100 [E12] CPU vs GPU at batch size 1: CPU faster 125-666x; a reported 34 ms GPU cost was a cold transfer vs warm copy 5.13 ms.
L101 [E3] Uniform random byte tapes run in isolation: VM with a dedicated COPY instruction gives 96 exact self-copiers per 1e7 tapes (length 32) and 9 (length 64); VM without a copy instruction gives 0 exact and 0 near copies in 1.2e7.
L102 [E5] Six experiments from other engines rebuilt natively here: 1 inverted, 2 changed, 2 absent, 1 preserved.
L103 [E11] Scattered Bernoulli(f) damage qualified first: 25,200 draws, chi2 p .49; one selection effect 6/6 -> 0/6 under it.
L104 [E1] Memory-task program: flushing packets in flight mid-gap 0.883 -> 0.497; flushing 1 tick before readout 0.853; resetting node state or inbox: no change.
L105 [E11] Damage experiment gate: primary damage effect attainable only at fraction f >= .44; evolved organisms never use state (intact .37-.43 vs a hand accumulator .74).
L106 [E5] Block-copy cost x4 on a seeded copier: sustained lineages 57/60 -> 1/60.
L107 [E5] Energy paid contingent on correct computation vs yoked payment of the same total: extinction 1 vs 67 of 150; competence .77 vs 0.
L108 [E4] Neutral walks: share of children gaining function on a different task .016 -> .043 along the walk.
L109 [E9] Lawful-but-unfamiliar systems shown to a language model (100 systems): unfamiliar systems learned .88 vs known 1.00; 0/32 unfamiliar called noise; 19/30 incompressible nulls called a rule; detector pair accuracy .767 (bar .80).
L110 [E9] Adversarial unfamiliar systems under a linear change of coordinates: learned 2/8.
L111 [E11] Overwriting the register that correlates with the regime changes 0% of answers.
L112 [E1] Disabling the programs' rule-switch instruction from the start: accuracy 0.52 and emissions fall 4x; disabling it only after trial 0: no change.
L113 [E4] 57 parent programs, all single edits (5,472) and a second set (2,280): children better than parent 0/5,472 and 0/2,280; loss .52 -> .99 as edit radius grows 1 -> 16.
L114 [E5] Registers carried across executions: founder lineages that need zero-initialised registers persist 0/24; p=.9 reset 5/12; ZERO reset 10/24.
L115 [E9] Novelty detector run on 32 mechanically generated unfamiliar rules: 28 familiar, 4 composite, 0 unfamiliar (Wilson upper .107); funnel 243 mechanisms -> 58 admitted -> 38 read -> 6 with signal -> 0 survived.
L116 [E10] Tensor-world learning-rule search, 38,000 proposals: 181 admitted, 9 flagged; a tuned batch matrix-completion baseline beats all 9 (e.g. 2.578 vs 4.856).
L117 [E8] Cutting the coupling between aim and energy in the steering combination: 15/128 -> 4/128.
L118 [E3] Seeded lineages moved to a different world, environment and physics: persisted 39/39, still self-replicated 27/27, retained task competence 0/39.
L119 [E5] World-performed copying variant v1 vs v2: extinction 0/150 vs 148/150.
L120 [E3] 27,140 of 27,141 random-initialisation worlds went extinct; the 1 survivor is a self-copier that copies exactly only at input value 121.
L121 [E3] Of the exact self-copiers in the COPY-instruction VM, 0.9896 copy only for particular input values (94 of 96 for one single input).
L122 [E5] Removing the scalar objective: copy summary statistics change in 99/100 paired runs, number of self-replication origins 1 vs 1.
L123 [E6] Perturbing single parent bytes and tracking 2 generations: donor sets pass 23/32, 83/100, 8/8; 19 test-passing genomes fail (11 at generation 2).
L124 [E9] One world's hypothesised effect implemented at strength r=0.2 was not detected; at r=0.65: LLE -0.919, ARI 1.0, matched a known analogue.
L125 [E9] Executable worlds generated from language-model concept triples, 37 probed with treatment/control/null-twin/cheat controls and >= 5 seeds: 5 showed signal; 0 of 5 survived an independent replication attack; 15 parked.
L126 [E4] Narrow decode with explicit FAIL/FIZZLE outcomes vs total modulo decode: recoveries 229 vs losses 154 (replicated); opcode faults recover 209 vs 15, register faults lost 142 vs 25; 0 held-out gains in 96 cells; final populations carry faults in .46-.80 of members.
L127 [E5] Forensics of 63,247 earlier runs: an identity null scored 'better' 60.0% of the time vs 1.3% for the control; all 5 historical flag classes failed re-test.
L128 [E1] Raising the energy-economy parameter from low to high on the hand relay design: viability change -0.45 / -0.22.
L129 [E1] Registers initialised to 0 at tick 0: in 27/42 cells the program's first action switches to rule 0.
L130 [E9] Same systems in prose vs tuple form: unfamiliar comprehension .91 -> .78; known .99 -> .99.
L131 [E6] Random pair-tape populations: a donor able to construct from fresh state appeared in 1/96 runs; it lacked the self-reference instruction.
L132 [E12] Metered communication channel: learners converged to silence in 3 separate rounds; 13/13 planted cheats caught.
L133 [E8] Combine-instead-of-replace writes: frozen fraction .927 -> .696; retained 0.998.
L134 [E3] Combinatorial search, 101,003 runs over 31,522 parameter families: 'spontaneous replication' flag fired in 26 runs; on replay all 26 were transplanted seeded material; after repair 0.
L135 [E9] Prompt-arm comparison, 8 units x 5 arms: fraction of generated mechanisms judged familiar T .088, P .140, S .775, O .838, G .850; triple vs pair 5/8; unfamiliar 0 in every arm.
L136 [E6] A robustness gain in one lineage: knock-in of the candidate change 0/5, revert 0/8, cross-graft 0/12; 49-54 of 64 bytes had changed.
L137 [E8] Snapshot comparison against a 250-tick-old state inflated per-field change by +128%; corrected ~25.5% of events state-changing, ~42% perturbation share.
L138 [E12] Screen of 74 cells: 1 survived; 232 new worlds: 1 more survived (replication never run); 4 pending became impossible to survive.
L139 [E4] Importing programs from another population: permuted incompetent imports take over 11-12/12 runs, competent imports 12/12, no import 0/12; takeover within 2-8 generations.
L140 [E6] Recombination splice off vs on: lineages exceeding copy depth 20 in 7/150 vs 0/150 (p .0073); maximum depth 549 vs 13.
L141 [E5] Verified task solutions reached under world-performed reproduction only: 178 vs organism-performed reproduction only: 2.
L142 [E6] 1-byte alias for the block-copy instruction: donor acquisition 39/64 vs 1/64 (p 1e-14); block-copy encodings were present in 87/96 plain runs.
L143 [E6] Byte-origin tags in those 8 lineages: share of bytes from outside the lineage median 0.020, max 0.107; mutation-origin share 18-56% in 6/8.
L144 [E8] Horizon 500 -> 10,000 ticks: max radius with fire-once off 2 (baseline), 5 (combine), 7; fire-once on 39; 0 locality violations.
L145 [E1] Majority program, per-sensor tagged swaps: outputs o2-o8 show effect 0.00 even though 80-95% of mirrored pairs carry different traffic; outputs o12-o14 each sensor contributes share .17-.27.
L146 [E4] Deleting k instructions scattered vs contiguous at the same k: loss .564 / .761 / .878 vs .463 / .652 / .795 across three fractions.
L147 [E8] Fresh seeds 4-7, 128 origins: fire-once+combine 22/128 (5/6/6/5 per seed), fire-once+steering 15/128 (3/2/5/5, two seeds below the per-seed floor); components alone: fire-once 4, combine 1, steering 0.
L148 [E4] Block vs distributed damage: loss .569 vs .630.
L149 [E4] Population size N = 50/100/200/400 at 60,000 evaluations: median first->last score from .167->.354 to .396->.375; every N reaches max .479-.562, above the best starting parent (.382).
L150 [E5] A promotion score >= 2 was reached by 69% of runs and steered allocation to one topology (9,655 runs).
L151 [E6] Write-back restricted so a tape half changes only through an accepted copy: deep lineages 46/80 vs 1/80 (p 4e-17) in one cell; 1/120 vs 0/120 over 15 other specimens.
L152 [E9] Same 5 systems, comprehension metric: language model .512 vs an affine baseline .487.
L153 [E6] Founder-byte share in descendants: median 0.134 (own cell), 0.253 (foreign); ancestry marker share ~1.0; in 17/19 populations no organism has >= 50% founder bytes.
L154 [E4] A balanced instruction encoding with more viable variation was 9x slower to reach targets.
L155 [E6] Re-assay of the 1,031 with a 3-draw causal-copy test: 57 pass (48 literal); 69/7,919 events causal; maximum depth 2; the recombination splice produced 6,287/6,547 of the byte matches.
L156 [E6] Hamming-1 matched run pairs (10,741): explicit vs implicit selection +0.3036 (513 pairs); pair-tape vs external reproduction -0.1197.
L157 [E6] Planting a 2-byte copy sequence once per initial genome: 32/96 vs sham 0/96 vs plain 0/96 vs dense instruction set 49/96; moved back to the stock VM, 372/372 acquirers lose competence (0.927 -> 0.000); share of organisms holding the planted sequence .76 -> .16.
L158 [E3] Knocking bytes out with 0x00 misses essential no-op loci: 5-7 essential loci found vs 14-17 with random-value or full-substitution scans.
L159 [E8] Edges live 3.1x shorter than a null that had no energy term; observed P(run >= 64) .0695 / .0726; hazard .128.
L160 [E10] Earlier search round: the only surviving specimen was a single running mean.
L161 [E10] In that probe, 87-89% of the 'never seen' test cells were cells from earlier episodes.
L162 [E1] Hand-written programs vs best evolved: latch task .999 vs .755; second task 1.000 vs .590; rule-switching beat the best fixed-rule program in 0/5 cells.
L163 [E7] Adversarial attack on 9 mined rules: 7 rejected.
L164 [E11] Admission gate refused 5/5 deliberately broken fixtures.
L165 [E5] 11,657 runs, payment-coupled physics: 40/40 positive-control pairs; 149 vs 0; seeded copier with repeated-output task K40 29/150 vs 6/150; random initialisation 0/3,200.
L166 [E3] Unblocked vs blocked input window: 12 blocks higher, 2 lower, p = .0065; counts from parent-chain labels were 8x-42x the counts from byte-lineage tracing.
L167 [E8] Hysteresis and conditional variants: more static (sticky .97; frozen .961); price-change variant: graph overlap .86 at lag 100 vs .36.
L168 [E8] Partial ring starvation in the fire-once variant: crossing 0/128 when inert sites starved vs 13/128 when writing sites starved vs sham 17/128.
L169 [E7] Follow-up campaign: a fixed rule with no fitted parameters reproduces 104/120 classes and 12/12 substitutions; mined rule vs fixed rule 6:1 on disagreements (p .125); out-of-sample confident stratum 42 = 42; coordinate rank correlation with effect .875; generating family recoverable .77 (chance .33).
L170 [E2] 0/8 negative-control worlds produced a spurious gain; a sensor exploiting a timing leak reached z 54.9 and was rejected by the leak check.
L171 [E3] Near-copiers: 12/63 (19%), and 5/22 near-copier founders, become exact self-copiers after ONE copy step (shift plus 0x00 fill), with no mutation.
L172 [E7] First intervention engine assumed a single flip point: 0/12; retest treating the boundary as a band: 12/12.
L173 [E4] Shared-state persistence on vs reset each generation: median first->last scores identical in all 12 worlds shown (e.g. .067 -> .069 both).
L174 [E7] Active sampler vs random sampling: .790 vs .788; cost-line sampler .767 vs random .946.
L175 [E2] 64 random matched sensors already solved 3 of 6 designated hard worlds (probabilities .227, .109, .141), leaving 3 valid worlds where the frozen rule required >= 4.
L176 [E6] Independent byte tracer vs reference tracer: agreement 1.0 on all gated fields; flip-test coverage self 159/496 = .321, other 48/168 = .286; 29 distinct births (<30 required).
L177 [E2] Selection arms strict / lexicase / reserve (14 of 48 slots kept for currently useless sensors) at equal budget: no arm advantage; the reserve arm produced the only assembly built from parts that were useless before they were needed.
L178 [E11] Answer-before-read strategy favoured in both matched pair sets.
L179 [E4] Delay task ladder: 11/12 seeds generalise to held-out delays 8 and 16 at 1.0 vs direct search 0/6 and 1/6; 5/12 already had the variation at the start.
L180 [E2] Unannounced law switch at generation 20 of 50 (36 runs, 72 cells): 2/72 cells adapted (+0.496 and +0.337).
L181 [E7] Interventions moving the rule's inputs changed outcome in the predicted direction 12/12, 10/12, 11/12.
L182 [E1] A fitted two-hop fixed-delay model predicted 46/46 unseen accuracy curves (median MAE .02).
L183 [E3] A recombination-matched control removed recombination by construction (0/1,829 controls kept it): recombination rate all runs .2534 vs .0454; restricted to exploration draws .1308 vs .1192.
L184 [E12] Graft transfer between worlds: graft - scratch +.738 (p .046); graft - sham -.662; sham - scratch +1.400.
L185 [E12] Charge-index bug in 29/36 worlds; after repair, an affine learner detects 73/130 regime switches.
L186 [E10] ~19,300 learner lives over competence dials: one coupling replicated (F 11.39, p 3.9e-5); with correct vs random tensor mode order the coupling is +0.87 vs +0.19 NLMSE.
L187 [E7] Location-aware selection matrix: 6 of 7 arms survive without it; gain between two campaigns mostly attributable to seed.
L188 [E10] Strict drift gate on 48 fresh worlds: stale records admitted .0003 vs .299 for the soft gate; multi-regime .0002 vs .698; verifies 4% of valid old records; forfeits +.60 AC in stationary worlds.
L189 [E11] Retention raw values .359 vs .181 (the ratio statistic reversed sign).
L190 [E8] Mutation numerator set to 0: template change -41% at +1 tick, -94.5% at +500; energy-change shift 0.000000.
L191 [E8] Five one-rule-change variants (combine, hysteresis, price change, conditional, steering), 128^2 x 2 seeds: 4 rejected; combine unresolved with 83% of its change being counting; all six: footprint 0.5-1.5 sites per origin, reach 1-2 over 500 ticks.
L192 [E3] A niche topology showed exploration advantage .0171 vs .0002-.0013 for other topologies; its sampler was coupled to migration and reservoir settings.
L193 [E2] A negative-arm test was passed by 0/20 simulated random ecologies.
L194 [E7] Intervention gate without a chance floor: a constant predictor f_hi = 2 scored magnitude 10/12 (bar 8); precision .155 vs best constant .83.
L195 [E1] Emission cost added (income 2, emit cost 1, cap 64) vs no cost, 3 seeds each: packet-using champions 3/3 vs 1/3; share of firing-style codes 1.0 in both arms.
L196 [E6] Pair-tape physics, 23,471 runs: 1,031 events where one organism wrote >= 25% of another's tape half; chain depth 1 in 911.
L197 [E7] A baseline predictor with no fitted parameters built from the world's own scoring formula matched the mined rule: McNemar p .688 (D), .688 (E), .125 (F); second rule vs baseline on F p .227.
L198 [E1] Checking whether an intervention actually reached its target, 21 fixtures (10 broken, 11 valid), 16 checks: best single check J .70 with 0 false alarms; smallest check set covering all fixtures = 3.
L199 [E4] 100 generations of selection on 188 drifted lineages: loss under mutation .42 -> .13 while genome length grew 19 -> 62; improving children 10 -> 0; removing unexecuted code changed loss only .435 -> .409.
L200 [E1] n-back reward (n=0,1,2), 10 searches: 4/8 pass the bar lo99 > .60; all 4 passing programs have a flat response over lags (.60-.65); programs selective for lag 2: 0/4 searches; a hand-written lag-2 program scores 1.000; the n=0 control also evolves the flat profile.
L201 [E5] Self-replication label in the payment arm: 108/109 acquisitions were real self-copiers; in controls 6/9 carried the label without copying.
L202 [E6] Causal-copy test on a 17-specimen panel with known answers: accepts all 4 organisms that write without reading their own bytes (scores 0.90-1.00) and rejects 4 real copiers.
L203 [E1] Synchronous update period 2: output mixture splits by clock phase (fraction .73 on even vs .12 on odd ticks).
L204 [E1] Forbidding a rule switch at the readout site: accuracy .500 exactly; the same restriction at a random site: 0 change.
L205 [E3] Establishments outside the unblocked arm occurred in the slowest compute blocks (5.9 / 3.3 / 5.9 h vs median 1.0 h); 3 of 5 were the same arrivals across arms.
L206 [E6] Reset value ZERO vs constant 0x5A vs carried vs random: establishment 26/48 vs 2/48 vs 6/48 vs 3/48 (p 2.4e-8).
L207 [E1] Re-evaluating evolved programs under 4 receiver operators (sum, saturating, collision, arbitration): 29/32 unchanged; one sum-dependent count code .801 -> .500 under every other operator; collision operator lowers dense codes .717 -> .539.
L208 [E7] Rule fragments from rejected and surviving rules: 11 of 15 re-express the no-fitted-parameter baseline formula, including every top-scoring fragment; fragments of firmly rejected rules do not.
L209 [E5] Paying partial solvers that answer a conditional ~half the time: the conditional was acquired in 0/960 runs.
L210 [E1] Material-provenance tracker built on another engine, applied here: majority-of-mask continuity matched behaviour in 3/48 cases.
L211 [E6] In-place mutation off: wins 6 -> 8/64 (p .39); register reset only on genome change .38 -> .43.
L212 [E12] Graph worlds, 28 cells: a zero-byte policy that always abstains beats every held-out baseline (e.g. 107.75 vs 98.76).
L213 [E1] Decay parameter 0 vs > 0: hand-designed relay viable in 19/245 settings at 0, 0/755 otherwise; evolved majority programs used packets at decay 3 and 6.
L214 [E1] Re-running 733 'no effect' component-swap verdicts at 512 worlds instead of 64: 615 unchanged, 90 became output flips; under a relative decision rule 170 flips; of 42 low-accuracy transfers 19 complete, 18 partial, 5 ambiguous.
L215 [E8] Adjacency generation equals causal generation in 100% (baseline), 99% (combine), 96.5% (move / fire-once off), 84% (fire-once on) of 27,000 flips; a bytes-only predicate gives 32 locality violations vs 0.
L216 [E5] Replication attempt under 6 transforms, 750 runs: dominance event 1/50 vs 0/50 for ZERO; the RANDOM positive arm 0/50 with 42/50 extinct.
L217 [E2] The V0 arm was later found to keep an unlogged 14-slot reserve; its surviving sensors had noise-level best-case wins in the trace.
L218 [E4] Evaluation-order arms: spike rate per 100 generations A .17/2.83/5.67 vs B 1.67/3.00/3.33 (within-arm spread larger than between-arm).
