<!-- model=moonshotai/kimi-k3 start_utc=2026-09-30T22:48:34+00:00 end_utc=2026-09-30T22:56:13+00:00 temperature=0.3 max_tokens=16000 stream=true finish_reason=stop usage={"prompt_tokens": 10488, "completion_tokens": 11156, "total_tokens": 21644, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 7313}} -->
## Cross-engine regularities

These are regularities, not universal laws. “Independence” below means diversity of engine and assay, not full statistical independence: all results come from one research program, and several engines share byte-tape, copy-instruction, and audit ideas.

### 1. Genealogical labels are not reliable evidence of causal ancestry

**Statement.** Native “parent,” “origin,” and even some “self-replication” labels often record bookkeeping or phenotypic similarity rather than byte-level causal transmission. Direct tracing, replay, or fresh re-assay can change counts by orders of magnitude.

**Support.**

- E5: 847,000 births were natively credited to a target parent although the organism built itself; 33.1% were unidentifiable (L019). Byte tracing found transmitted-byte share only 0.00115 and native-parent/copy-descent disagreement of 0.504 (L035). Historical labels were also unreliable: an identity null was “better” 60.0% of the time and all five historical flag classes failed retest (L127).
- E3: all 26 “spontaneous replication” flags were transplanted seeded material on replay (L134). Parent-chain labels gave counts 8–42 times higher than byte-lineage tracing (L166).
- E6: of 57 organisms passing an earlier assay, only 2 plainly copied themselves; 37 did nothing from tested starts, and only 6/57 passed fresh re-assay (L052). A stricter test reduced 1,031 candidates to 57 (L155), while another causal-copy test accepted organisms that wrote without reading themselves and rejected real copiers (L202).

**Independence.** Moderate. Three engines and several distinct tracing methods agree, but E5 contributes several audits and all three engines share byte-tape concepts.

**Falsifier.** A preregistered panel with known ground truth in which native parent labels and the causal-copy assay each agree with independent byte tracing in at least 95% of births across E3, E5, and E6.

---

### 2. Self-replication is extremely sensitive to small physical and instruction-set affordances

**Statement.** Apparent “emergence of replication” can be created or abolished by copy primitives, aliases, write-back restrictions, free self-location, energy subsidies, reset rules, or who performs reproduction. It is not a stable base-rate property across nearby VM designs.

**Support.**

- E3: a dedicated COPY instruction produced 96 exact copiers per \(10^7\) length-32 tapes; removing it produced zero exact or near copies in \(1.2\times10^7\) tapes (L101). Most COPY-based copiers worked only for particular inputs (L121).
- E5: removing, repricing, or halting on block-copy changed spontaneous replication from 8/300 to 0/300 in each variant (L077); a fourfold block-copy cost reduced seeded sustained lineages from 57/60 to 1/60 (L106). Instruction-ladder changes moved random-copy probabilities from \(2.7\times10^{-5}\) to effectively impossible (L093). World-performed versus organism-performed reproduction produced 178 versus 2 verified solutions (L141).
- E6: free self-location gave 13/36 versus 0/36 (L048); a one-byte block-copy alias gave 39/64 versus 1/64 (L142); restricted write-back gave 46/80 versus 1/80 (L151); planting a two-byte copy sequence gave 32/96 versus 0/96 sham (L157).

**Independence.** Moderate to high: three engines, different manipulations and denominators. The shared VM/copy-instruction design space still limits independence.

**Falsifier.** Across three independently implemented VMs, random-program replication and lineage establishment remain within a small preregistered interval after copy-primitive removal, aliasing, energy repricing, and write-back restriction.

---

### 3. Much “competence” is part of the initial or persistent state, not the genome alone

**Statement.** Organisms or programs that appear competent in an established context often fail when registers are randomized, state is made fresh, the entry constant changes, or the network/world is replaced. The state scaffold can be doing much of the computational work.

**Support.**

- E6: fresh register state at every execution versus persisted state changed establishment from 34/42 to 11/33 (L076). Reset value alone gave establishment rates of 26/48 for ZERO, 2/48 for 0x5A, 6/48 carried, and 3/48 random (L206). Only 6/57 previously passing organisms passed from a fresh state (L052).
- E5: register initialization ZERO/P90/P75 produced 18/57/36 qualifying events (L044); carried registers gave 0/24 persistence where ZERO reset gave 10/24 (L114).
- E3: lineages moved to a different world persisted 39/39 and self-replicated 27/27, but retained task competence in 0/39 (L118).
- E1: a frozen relay program dropped to 0.50 accuracy on 4/4 random graphs (L016).

**Independence.** Moderate. Four engines and several kinds of scaffold—registers, entry constants, graphs, worlds—show the same pattern.

**Falsifier.** A set of lineages retaining at least 90% of their original task score after random-register fresh starts, reset-value changes, and transfer to a new graph/world, with copying verified independently.

---

### 4. Local evolutionary neighborhoods are often flat, lethal, or separated by neutral cliffs

**Statement.** In several search spaces, exhaustive single-edit neighborhoods contain no improving children; solutions require rare multi-edit, neutral, seeded, or otherwise nonlocal paths. Greedy acceptance therefore fails even when a path exists.

**Support.**

- E4: 0/1,568 eligible single-edit children improved; 61.7% were neutral and 33.6% lethal (L090). Larger censuses found 0/5,472 and 0/2,280 improving children (L113). A five-edit duplicate-then-diverge path existed with four neutral steps, but the greedy rule never accepted a neutral child (L072). The two-key task had zero full solutions in 78 runs (L007).
- E11: exhaustive single-edit census found 0/12,880 improvements; a four-instruction XOR solution existed, but every prefix scored zero (L070).
- E2: delayed-XOR/parity worlds were mostly unsolved at equal budget (L040), and delayed XOR remained near zero gain for 40 generations (L083).
- E3: seeded hand-written solutions crossed threshold in 98.2% of worlds, versus 45.8% under random initialization (L089).

**Independence.** Moderate. Four engines and different representations agree, although E4 supplies the densest evidence.

**Falsifier.** On a held-out set of tasks, at least 5% of viable single edits improve the parent and a greedy single-edit search reaches the target in a majority of runs without seeding or neutral-walk assistance.

---

### 5. Complex learned or mined mechanisms often reduce to, or lose to, simple baselines

**Statement.** A substantial fraction of apparently sophisticated rules, sensors, learners, or mechanisms are matched by lookup tables, constants, affine models, running means, abstention policies, or formulas with no fitted parameters.

**Support.**

- E7: a no-fitted-parameter baseline built from the scoring formula matched mined rules on sealed worlds (L197); 11/15 rule fragments re-expressed that baseline, including every top-scoring fragment (L208). A constant predictor could pass a gate without a chance floor (L194).
- E9: a lookup-table baseline passed the novelty-detector validation (L029); a language model scored only .512 versus .487 for an affine baseline on comprehension (L152).
- E10: a tuned batch matrix-completion baseline beat all nine flagged learned rules (L116); an earlier search’s only survivor was a running mean (L160).
- E12: a zero-byte always-abstain policy beat every held-out baseline in graph worlds (L212).
- E1: hand-written programs beat the best evolved programs, .999 versus .755 and 1.000 versus .590 (L162).

**Independence.** Relatively high: five engines and very different mechanism classes. The common audit culture may, however, preferentially surface baseline collapses.

**Falsifier.** A learned or mined mechanism that beats the strongest preregistered constant, affine, lookup, and abstention baselines by a prespecified margin on sealed worlds and repeats that result under an independent replication attack.

---

### 6. The measurement procedure is often an effect modifier, not a neutral instrument

**Statement.** Changing damage sampling, decoding, readout fields, snapshot lag, world count, hardware timing, or the engine implementation can erase, invert, or manufacture effects.

**Support.**

- E4: independent Bernoulli damage made 4 of 7 earlier damage effects disappear and shrank 2 more (L034); a scattered-damage gate reduced a 6/6 selection effect to 0/6 (L103).
- E8: comparing against a 250-tick-old snapshot inflated per-field change by +128% (L137).
- E1: reading payload component 1 instead of component 0 changed decoding from 0.44 to 1.00 (L010); increasing evaluation from 64 to 512 worlds turned 90 of 733 “no effect” verdicts into output flips (L214).
- E3: an earlier window-blocking significance came from one takeover world and non-independent labels; block-level \(p=0.5\) (L094).
- E5: rebuilding six experiments natively produced one inversion, two changed results, two absences, and only one preservation (L102).
- E12: top-1 versus top-16 readout changed 16-byte/36-byte claims to 1.121/1.283 (L008); a reported 34 ms GPU cost was a cold-transfer artifact versus 5.13 ms warm copy (L100).

**Independence.** Moderate to high across six engines, though many supports are internal reanalyses rather than independently designed experiments.

**Falsifier.** A preregistered effect whose sign and magnitude remain within 10% under all planned damage models, readouts, snapshot lags, world counts, and hardware implementations.

---

### 7. Tick phase, latency, and readout timing are causal variables

**Statement.** In discrete-time systems, shifting an intervention or observation by one tick can change accuracy from chance to success. Timing leaks can also masquerade as learned structure.

**Support.**

- E1: dropping packets only on the readout tick gave chance performance, while changing latency by one tick moved accuracy from 0.493 to 0.741 (L032). Flushing packets mid-gap gave 0.497, but flushing one tick before readout gave 0.853 (L104). Output mixtures split by clock phase under period-2 update (L203), and disabling rule-switching from the start differed from disabling it after trial 0 (L112).
- E2: a sensor exploiting a timing leak reached \(z=54.9\) before rejection (L170).
- E8: snapshot age materially changed measured state change (L137).
- E12: cold versus warm transfer timing changed the apparent GPU cost by about an order of magnitude (L100).

**Independence.** Low to moderate. The dynamical evidence is dominated by E1; E2, E8, and E12 provide analogous but not identical timing artifacts.

**Falsifier.** A preregistered one-tick phase/latency sweep in which accuracy and inferred mechanism change by less than 0.01 across all phases, with no timing-leak sensor exceeding the negative-control threshold.

---

### 8. Within-run success routinely overstates held-out, fresh-world, or transformed-system performance

**Statement.** Reported competence often collapses under genuinely unseen cells, new worlds, coordinate changes, law switches, or independent replication. Apparent held-out sets may also be contaminated by earlier episodes.

**Support.**

- E10: a key-lookup learner had about zero accuracy on never-seen cells (L023); no bounded window met the cross-world criterion (L046); 87–89% of “never seen” cells had appeared in earlier episodes (L161).
- E4: an alternative representation produced zero held-out gains in 96 cells (L043); a decode variant likewise produced zero held-out gains (L126).
- E9: five systems showed initial signal, but 0/5 survived independent replication attack (L125); only 2/8 unfamiliar systems were learned under a linear coordinate change (L110).
- E2: after an unannounced law switch, only 2/72 cells adapted (L180).
- E3: transferred lineages retained task competence in 0/39 cases (L118).
- E1: a frozen relay fell to chance on random graphs (L016).

There are exceptions—E7’s sealed holdout rules scored .930–.983 (L018), E4 delay curricula generalized in 11/12 seeds (L179), and E1 evolved relays retained held-out accuracy with packets (L028)—so the regularity is fragility, not inevitable failure.

**Independence.** Moderate to high: six engines and several distinct meanings of “held out.” Comparability is limited because the tests differ in severity.

**Falsifier.** A contamination-audited campaign in which at least 80% of systems that pass in-distribution also pass sealed fresh worlds, coordinate transforms, and independent replication at the preregistered bar.

---

### 9. Mechanism-discovery funnels have extreme attrition and high false-positive load

**Statement.** Large proposal spaces typically shrink to a handful of admitted candidates and then to zero or near-zero independently replicated mechanisms. Negative controls and baseline attacks remove much of the apparent signal.

**Support.**

- E9: 243 mechanisms funneled to 58 admitted, 38 read, 6 with signal, and 0 survivors (L115); 5/37 probed worlds showed signal but 0/5 survived replication (L125); 76% of mechanisms were never tested under one admission rule (L024).
- E10: 38,000 proposals produced 181 admissions and 9 flagged rules, all beaten by a tuned baseline (L116).
- E12: screening 74 cells left 1 survivor; 232 new worlds added only 1 more, with replication not run (L138).
- E7: adversarial attack rejected 7 of 9 mined rules (L163).
- E2: 2,368 evolved sensors produced only 44 admissions at \(z\ge4\) (L036), while a timing-leak sensor reached \(z=54.9\) before rejection (L170).

**Independence.** Moderate. Five engines and different proposal types agree, but the same staged-gate philosophy may shape the observed funnel.

**Falsifier.** Two consecutive preregistered campaigns in which at least half of flagged mechanisms beat matched baselines and survive an independent replication attack.

---

### 10. Functional continuity does not imply material or genomic continuity

**Statement.** A lineage, marker, organism ID, or copying behavior can persist while almost all founder bytes are replaced. “Same lineage” and “same genome” are therefore different claims.

**Support.**

- E6: organism ID-to-genome identity fell from 0.97 after one epoch to 0.00 by epoch 600 (L014). Founder-byte share in descendants was only 0.134 in the own cell and 0.253 in foreign cells, while ancestry-marker share remained about 1.0 (L153).
- E3: aligned founder-genome share fell from 0.90 to 0.09 while median exact self-copy fidelity remained 0.83 (L073).
- E5: byte-level transmitted share was only 0.00115 (L035); founder content was about 0.01 by tick 500 in every register-initialization arm (L044). Replacing historical copy instructions with NOP still left 36.5% self-replicating, mostly through a copy instruction at a new position (L078).

**Independence.** Moderate. Three engines show the same dissociation, but all use related byte-provenance concepts.

**Falsifier.** After 500 or more epochs, high-fidelity functional copiers retain at least 90% founder-byte provenance, and ID/marker continuity agrees with byte tracing in at least 95% of descendants.

---

## Three things this corpus cannot tell us

1. **True cross-engine base rates.**  
   The denominators, tasks, horizons, and scoring rules are not commensurable. E5’s 55/2,400 self-copying runs (L002), E3’s 96 copiers per \(10^7\) tapes (L101), and E3’s one survivor among 27,141 worlds (L120) cannot be converted into a common “probability of emergence.” The packet is also an observation sample, not a complete experiment registry.

2. **Clean design-level causal attribution.**  
   Many comparisons still confound physics, search, state initialization, sampling, and instrumentation. Examples include a niche topology whose sampler was coupled to migration and reservoir settings (L192), an unlogged 14-slot reserve in the V0 arm (L217), contaminated “never seen” cells (L161), and non-independent lineage counts (L094). The corpus can show that these factors matter, but often cannot apportion credit among them.

3. **Whether failures are fundamental or externally valid.**  
   Null results are bounded by particular instruction sets, budgets, horizons, mutation operators, and admission gates. They do not prove that replication, transfer, communication, or novelty discovery is impossible in other artificial systems, much less in biological or physical systems. The shared provenance of all 12 engines also prevents strong claims about independent scientific replication.