<!-- model=deepseek-ai/deepseek-v4.1-flash start_utc=2026-09-30T22:48:34+00:00 end_utc=2026-09-30T22:56:23+00:00 temperature=0.3 max_tokens=16000 stream=true finish_reason=stop usage={"prompt_tokens": 10454, "completion_tokens": 11094, "total_tokens": 21548, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 8948}} -->
Below I treat a “regularity” as a cross-engine pattern, not a claim about the original authors’ intent. I cite line numbers as evidence.

## 1. Self-replication is gated by explicit copy machinery, but can be reacquired by relocation, aliases, or seeding
**Statement:** Sustained self-replication usually requires a copy/block-copy instruction or equivalent machinery. Removing, halting, or heavily taxing it collapses replication; however, replication can reappear via a copy instruction at a new position, a 1-byte alias, or seeded/planted copy sequences.  
**Support:** E5: L077, L078, L093, L106, L201; E3: L101, L120, L121, L171; E6: L142, L157, L202.  
**Independence:** E5 and E6 share byte-tape/copy ideas, so not fully independent; E3’s VM/COPY-instruction results are more independent.  
**Falsifier:** An engine where deleting all copy instructions still yields sustained self-replication at rates comparable to copy-enabled controls.

## 2. Register/state initialization and persistence strongly determine lineage establishment and competence
**Statement:** Zero/fresh register state often promotes establishment and deep lineages; carried, random, or non-zero state often suppresses them. Removing state persistence can collapse performance.  
**Support:** E6: L068, L076, L098, L114, L206, L211; E5: L044, L114; E11: L027, L105, L111; E1: L129.  
**Independence:** E6/E5 share register/tape ideas; E11 and E1 add different task/state regimes.  
**Falsifier:** An engine where random or carried state yields equal or higher deep-lineage establishment than zero/fresh state.

## 3. Energy/reward contingency controls competence and extinction
**Statement:** Paying energy contingent on correct computation or real copying promotes competence and survival; yoked, uncoupled, or non-limiting energy payments often fail or erase differences.  
**Support:** E5: L107, L165, L201, L026, L209; E6: L048, L057, L085; E11: L013, L086.  
**Independence:** E5/E6 share physics/energy ideas; E11’s rank-tax/price results are more independent.  
**Falsifier:** An engine where yoked payment produces the same competence as contingent payment.

## 4. Topology and locality matter for extinction, exploration, and relay behavior
**Statement:** Well-mixed vs local/niche/graph topologies change extinction and exploration; moving a frozen lattice relay to a random graph destroys accuracy; spatial starvation and locality constraints alter propagation.  
**Support:** E5: L003, L150; E3: L192; E1: L016, L039, L062, L104; E8: L020, L031, L047, L144, L168, L215.  
**Independence:** E1/E8 are different physics; E5/E3 add population/topology effects.  
**Falsifier:** An engine where topology manipulation has no effect on extinction, exploration, or relay accuracy.

## 5. Search landscapes are highly neutral/lethal; single edits rarely improve, and greedy hill-climbers fail
**Statement:** Most single edits are neutral or lethal; improvements are rare or absent. Neutral intermediates are often required for later function, and greedy rules that reject neutral steps miss paths.  
**Support:** E4: L007, L009, L021, L043, L072, L090, L108, L113, L199; E11: L070, L063, L013, L086; E5: L095.  
**Independence:** E4/E11 share program-edit ideas; E5 adds mutation-supply evidence.  
**Falsifier:** An engine where greedy single-edit hill climbing reliably finds improvements without neutral intermediates.

## 6. Native ancestry/parent labels are unreliable; byte-level tracing is needed
**Statement:** Parent labels often disagree with actual copy descent, can credit self-assembly or location, and inflate lineage counts. Byte-level or causal-copy tracing gives different, often much lower, ancestry estimates.  
**Support:** E5: L019, L035; E6: L014, L143, L153, L155, L176, L196, L202; E3: L079, L166, L073.  
**Independence:** E5/E6 share byte-tape ancestry ideas; E3’s grafting/label comparisons are more independent.  
**Falsifier:** An engine where native parent labels match byte-level copy descent above 95% with no misattribution.

## 7. Self-replication and task competence dissociate
**Statement:** Lineages can retain self-replication after moving to new worlds/physics while losing task competence; copying and task computation are often separate capabilities.  
**Support:** E3: L118, L067, L073, L120, L121; E5: L074, L141, L165; E6: L052, L066, L092, L098.  
**Independence:** E3, E5, and E6 are different engines, though some share tape/copy motifs.  
**Falsifier:** An engine where moved self-replicators retain task competence as often as they retain replication.

## 8. Measurement/readout/damage/lineage-tracing procedure often flips or shrinks effects
**Statement:** Changing readout, damage model, packet handling, snapshot comparison, or lineage tracing often changes conclusions: effects vanish, reverse, or become artifacts.  
**Support:** E1: L010, L032, L104, L145, L203, L207, L214; E4: L017, L034, L054, L126, L146, L148; E8: L001, L137, L190, L215; E10: L046, L075, L080, L188; E12: L008, L100, L185.  
**Independence:** Broad across many engines and procedures.  
**Falsifier:** An effect that remains invariant across all reasonable readout, damage, and tracing procedures.

## 9. Novelty/lawfulness detection and unfamiliar-system learning are unreliable
**Statement:** Detectors often call nulls lawful, miss unfamiliar lawful systems, or are matched by simple baselines. Language-model comprehension of unfamiliar systems is lower than known systems, and adversarial coordinate changes break learning.  
**Support:** E9: L024, L029, L096, L109, L110, L115, L125, L130, L135, L152; E10: L116, L160, L161; E12: L212, L217; E2: L170, L175, L193.  
**Independence:** E9/E10/E12/E2 are different engines and tasks.  
**Falsifier:** A detector that identifies unfamiliar lawful systems above the stated bar and rejects incompressible nulls.

## 10. Positive/negative controls and hidden implementation details often explain apparent successes
**Statement:** Many apparent discoveries disappear after repair, independent replication, or proper controls. Hidden reserves, charge-index bugs, unlogged slots, and mislabeled seeds explain some positive results.  
**Support:** E10: L023, L042, L116, L160, L161; E12: L138, L185, L217; E2: L170, L175, L193, L217; E5: L127; E3: L030, L094, L134, L166, L205.  
**Independence:** Broad across engines, though some are shared infrastructure bugs.  
**Falsifier:** A claimed effect that survives repair, independent replication, and all relevant controls.

## 11. Recombination/splicing creates long-range byte matches and can increase copy depth, but usually reduces viability or adds no new function
**Statement:** Splicing/recombination can produce long-range byte matches and deeper copy chains, but often lowers viability and does not reliably create new behaviors.  
**Support:** E4: L055; E6: L140, L155; E3: L183, L079.  
**Independence:** E4/E6/E3 are different engines, though E6/E3 share tape ancestry ideas.  
**Falsifier:** An engine where recombination reliably produces viable novel functions.

## 12. Instruction-set/encoding details strongly determine evolvability
**Statement:** Copy aliases, NOP/trap handling, balanced encodings, and decode rules change replication acquisition, viability, and search speed.  
**Support:** E5: L077, L078, L093; E6: L142, L157; E3: L101, L158, L171; E4: L037, L049, L154.  
**Independence:** E5/E6 share copy/tape ideas; E3/E4 add different VM/encoding evidence.  
**Falsifier:** An engine where changing copy aliases, trap handling, or encoding has no effect on replication or evolvability.

## Three things this corpus seems unable to tell us

1. **Whether any mechanism is generally necessary or only an artifact of a particular instruction set.** Many engines share byte tapes, copy instructions, register resets, and damage models, so cross-engine agreement may reflect shared implementation rather than a universal principle.

2. **Absolute rates of spontaneous self-replication, task competence, or open-ended evolution.** Measurement procedures, parent labels, hidden reserves, and positive controls differ so much that the corpus cannot give a common-scale rate for “how often life/task-solving appears.”

3. **Whether long-horizon outcomes would persist beyond the tested horizons.** Most runs are short or only spot-checked at 10,000–20,000 ticks; the corpus cannot tell whether reported lineages, laws, or competencies would survive much longer or under different energy/topology/instruction-set combinations.