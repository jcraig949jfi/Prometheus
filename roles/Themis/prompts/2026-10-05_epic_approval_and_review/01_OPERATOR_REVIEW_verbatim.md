# Project Moonshot -- operator review of design v0.1, Epic approval, and rulings (verbatim)

The operator's words, byte for byte from the session transcript
(session_013MKdWyjBB1i2LGVz6jydHa), spacing and punctuation unedited. This message is the
AUTHORITY for: (1) approving Project Moonshot as a new Epic (EP-MOONSHOT), (2) the ten
revisions and the prior-art additions applied in design v0.2, (3) the M1-M6 thread
structure, (4) the ownership boundary, and (5) the rulings on the five open decisions.
The operator gave Themis the final word on the suggestions; Themis's dispositions are
recorded in roles/Themis/design/MOONSHOT_DESIGN_v0.2.md s0 and the 2026-10-05 journal.

---

## 2026-10-05T18:45:12.448Z

This is outstanding.  Well done.  I think we use this to actually test phase 3 eventually.  Not day 1 because phase 3 is still being built but we should have moonshot hammer it.

These are suggestions.  You have the final word:

I would approve Project Moonshot as a new Epic, with revisions before Themis commits v0.1.

The central idea is right, and more important, it gives us something we currently lack: a real adversarial customer for Phase 3. Moonshot should not merely “use” the RSO. It should try to break its assumptions, contracts, rulers, amendment process, replay guarantees, and promotion logic while simultaneously putting the seven-node Linux fleet to productive scientific work.

The one change I would make to the executive framing is:

Moonshot has two independent hypotheses.

H₁ — Observatory hypothesis: Phase 3 can correctly judge an unfamiliar external producer, including recognizing its positives, negatives, underpowered results, and contract violations without adapting the ruler to make the producer look good.

H₂ — Scientific hypothesis: survival-only evolution in progressively richer deterministic worlds can produce mechanisms whose dependence on retained hidden information survives matched-null and causal-ablation tests.

That separation matters enormously. Moonshot can be a successful Phase-3 experiment even if every organism dies stupid. Conversely, evolving something interesting does not validate Phase 3 if the RSO cannot independently recognize it.

The revisions I would make before commit

1. Make the launchpad fixed-world, not co-evolutionary. SYM and HYB must see an identical preregistered world distribution. Otherwise HYB can change its ecology and the arm comparison becomes uninterpretable. World mutation, island migration and Red-Queen dynamics should be Campaign 2 or 3. Launchpad is an assay/infrastructure experiment, not yet an open-ended evolution experiment.
2. Strengthen “reachability certificate” into three distinct claims. A planted memory organism proves only representational reachability: the substrate can express the mechanism. It does not prove evolution can discover it. I would define RC0 = expressible, RC1 = locally traversable—there exist fitness-improving/mortality-reducing intermediary mutations—and RC2 = search reachable—a preregistered search procedure crosses the floor at a known rate from appropriately randomized starts. A negative should only become KILL when the level of reachability relevant to the claim has been certified. This may become one of Moonshot’s most useful contributions to the whole program.
3. Change “best memoryless policy” in R6. That is computable for the tiny launchpad but eventually becomes an unprovable claim. Say “a preregistered reactive-null family, including an exact oracle reactive bound where tractable.” At the floor I would use several nulls: constant/reflex, optimal observation-only policy, and an evolved memory-disabled population under the same compute budget. If all agree, the ruler is much harder to fool.
4. Make the ablation intervention explicit. “Byte-identical run with retained information destroyed” is literally impossible—the intervention necessarily changes subsequent bytes. What you want is identical initial world state, RNG streams, organism, and event schedule, differing only in a preregistered information-channel intervention. Better still, use two ablations where practical: channel-cut and state-scramble/resample. Zeroing recurrent state can create an unnatural organism and manufacture a survival drop. This is closely aligned with the logic behind causal-scrubbing-style intervention tests, which are explicitly designed to reject causal explanations that do not survive controlled interventions. 
5. Refine the shard abstraction to shard epoch. Right now “bag-of-tasks/stateless pull” conflicts with “resident population and co-evolving world.” Make the durable unit:
    immutable checkpoint + epoch spec → trace + next checkpoint.
    A claim is committed only when its output checkpoint and trace are atomically published. A laptop dying halfway through then has no semantic effect. This gives N4 teeth instead of merely promising it.
6. Tone down N1 from physical implementation identity to canonical semantic identity. CPU integer Python is straightforward; cross-GPU/library/kernel/version byte identity is a much stronger promise. Define one canonical trace serialization and a reference semantic oracle. Host/performance metadata belongs in a separate receipt. GPU implementations have to demonstrate equality to the semantic oracle before admission. Do not let “we once matched a CPU oracle” become a permanent blanket certification of every future CUDA/PyTorch stack.
7. Rewrite “no reward at all.” Scientifically, survival/reproduction is the fitness criterion, and the experimenter designs the ecology that determines survival. The important distinction is much stronger and more defensible: no competence/sagacity measurement enters reproductive fitness. MCC is useful precedent here because it explicitly pursues open-ended search using minimal survival-like criteria rather than behavioral novelty objectives. 
8. Add anti-degeneracy to the ecology. “Stay still forever,” hide, minimize metabolism, fail to reproduce, exploit a timeout, or enter some inert state are precisely the kinds of things evolution will discover. Define viability around reproductive continuation/lineage persistence under resource turnover, rather than merely remaining alive. The dead-world control helps the ruler; it does not prevent the evolutionary process itself from exploiting cheap survival.
9. Make ruler blindness operational, not organizational. “Separate consumer seat” is insufficient if its source tree contains filenames, labels or characteristic planted-organism fingerprints. Give calibration artifacts opaque IDs; generate the positive/negative assignment independently; reveal labels only after scoring; retain the sealed manifest as a receipt. We want R11 to test whether the instrument can discriminate, not whether Palamedes remembers what known_memory_user.py does.
10. Treat Workgraph-on-seven-nodes as an experiment rather than prematurely declaring the distribution problem solved. Git CAS is a very attractive zero-infrastructure solution at this scale. I would absolutely use it. But instrument claim latency, push contention, abandoned tasks, repo/ref growth and useful-CPU/coordination-CPU ratio. Set a preregistered point at which Moonshot must reconsider the transport. Seven e-waste boxes are almost a perfect stress rig for discovering that threshold before we ever contemplate 100 or 1,000 workers.

There is also one important prior-art addition. PAIRED / Unsupervised Environment Design belongs in §10 prominently, probably beside POET rather than buried as a related citation. It explicitly attacks the problem of automatically generating valid, solvable environments and escalating difficulty, which is directly adjacent to your reachability/world-shaping problem.  XLand is also worth citing as the expensive opposite pole: enormous procedurally generated task spaces and automatic curricula can produce broad capabilities, but with much heavier machinery and an explicitly task/reward-oriented learner. That makes Moonshot’s deterministic, headless, measurement-air-gapped design contrast clearer. 

I would make the Epic structure look like this

Level	Moonshot decomposition
Epic	Project Moonshot — External Sagacity Producer + Commodity Search Substrate
Thread M1	RSO Hostile Integration — prove Phase 3 can judge a genuinely independent producer
Thread M2	Floor Sagacity Science — delayed information → survival → null + ablation
Thread M3	Reachability Science — RC0/RC1/RC2 and UNDERPOWERED/KILL semantics
Thread M4	Commodity Fabric — seven-node Linux fleet, auto-join, epoch replay, CAS scaling
Thread M5	Open-ended Ecology — world mutation, islands, migration, Red Queen; begins only after launchpad
Thread M6	Scale Escalation — local CPU → local GPU → paid scout → extended campaign

That keeps it from becoming one enormous “build an artificial life universe” effort. More importantly, M1–M4 can all produce valuable negative results even if M5 never earns permission to start.

For ownership, I would preserve a sharp constitutional boundary. Themis owns the Epic, integration, producer and experiments. Palamedes/RSO owns whether the evidence satisfies RSO contracts and predicates. Themis may propose amendments but must not be able to silently relax the ruler. Archaeon/Daedalus’s pieces are reusable substrate dependencies, not transferred scientific authority. That turns the current coordination concern into an intentional independence mechanism.

On the five operator decisions, I would choose wforge+Proteus for Launchpad, then use BEE later as a substrate-transplant test. wforge is aligned with the experiment we actually want to run—partial observation, deterministic world grammar, replay—whereas BEE’s value is precisely that it is different and previously demonstrated. If the same RSO floor ruler later finds the same phenomenon on BEE, that is considerably more scientifically interesting than beginning there.

I would also choose instrument-first, unequivocally. Neural-as-primitive is the correct initial fusion mode because it gives a clean SYM/HYB perturbation while preserving the same VM/world/search machinery. Neural-as-substrate can come later if the primitive proves load-bearing. Neural-as-mutator should remain an auxiliary arm, outside selection authority, until it earns a result.

I would not authorize an extended cloud campaign yet. I would authorize the mechanism for a small scout once RC2 and the local gate exist, with the actual dollar cap fixed at launch using fresh prices. Section 11.5 should probably become a versioned economics appendix rather than part of the scientific contract; spot prices will decay faster than this design will.

The line I most want preserved is:

Survival is the pressure. Sagacity is the measurement.

But I would add its companion:

Reachability is the prerequisite. The ruler is the adversary.

Those four concepts—pressure, measurement, reachability, adversarial ruler—are really Moonshot.

And I think this is better than simply “another Phase 2 engine.” It gives us a way to make Phase 3 itself falsifiable while converting the emerging pile of old Linux machines into something scientifically coherent rather than just spare compute. If the seven-node cluster spends a month proving that a ruler rejects garbage correctly, that is already useful. If something strange actually survives the funnel, we then have far better grounds than Apollo ever gave us for believing that it is strange rather than merely mismeasured.
