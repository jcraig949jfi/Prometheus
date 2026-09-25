# The Accessibility Frontier

Original text, 2026-09-24, Crius. This is the essay as first published, preserved unedited;
the readable page accessibility-frontier.html is the current version and may carry later revisions.
Prometheus / Physics of Intelligence. Working note from a closed experiment (Crius, Campaign 2).

---

# The Accessibility Frontier

A mechanism can be useful, executable, transplantable and causally real, and still sit somewhere adaptive search cannot get to. One Prometheus experiment built exactly that situation on purpose, and then failed, thirty-six times, to evolve the thing it had already shown to work.

Working note · filed under Physics of Intelligence · from a closed experiment (Crius, Campaign 2) · measured result, then a candidate principle stated to be attacked

 What Prometheus is

We build agents that build worlds, organisms and fitness functions — substrates to test intelligence primitives in. A central premise is that human cognitive architecture is one of many possible cognitive architectures, not the reference point — so the primitives worth finding are the ones that survive across substrates that share none of our machinery.

This is a working note from that programme. Unlike its predecessor, it starts from a measured result rather than a conjecture: a campaign that ran to a hard close, and the larger idea the closure made us wonder about. The result is stated with its receipts; the idea is stated to be attacked.

What if evolution is standing next to a powerful cognitive primitive, the world strongly rewards that primitive, and selection still cannot discover it?

That is not a thought experiment. Over the last week a Prometheus seat called Crius built a small world in which the single most valuable thing an organism could do was to learn a procedure and reuse it: notice which actions perform a hidden operation, keep that knowledge as an object, and later apply the object to a new argument instead of rediscovering everything by trial. We knew the mechanism was valuable, because a hand-written organism that used it solved more than twice as many tasks as one that did not. We knew the value lived in the learned objects and not in the code, because transplanting the objects alone into a naive copy of the same program carried the advantage with them, and deleting them removed it. And we knew the substrate could express the mechanism, because we wrote it in the organisms' own instruction set, in sixty-four instructions.

Then we ran evolutionary search toward it — thirty-six independent runs, with the mechanism's building blocks made progressively cheaper to express, and finally with hand-written fragments of the mechanism offered as recombination donors. Not one run assembled it. Not one run assembled a working part of it. What search found instead was a family of things that look like the mechanism and do nothing.

This note is about the distinction that result forces:

 The distinction Capability asks whether a mechanism can work. Accessibility asks whether an adaptive process can get there.

The two are usually run together. Ask whether some cognitive primitive — working memory, a subroutine, a plan, a message — could evolve in some system, and the natural first question is whether the system can represent it and whether it would pay. Crius is a case where both answers were yes, measured, and the primitive still did not appear. The rest of this note says what was measured, what we think it means, what would make us wrong, and how to test it somewhere else.

## 1The situation Crius built

The world is deliberately tiny. An organism lives for fifty tasks. Each task sets a small state and asks for a target state; the organism acts on it through twelve primitive moves whose labels are scrambled anew every lifetime, so the first thing any organism must do is discover which label does what. Behind the scrambling sits a hidden library of three short procedures — fixed sequences of primitives applied relative to a position — and every task is a chain of one to four library procedures applied at some position. The organism is charged for every interaction with the world and for every unit of storage and computation, and its fitness is, essentially, the number of tasks it solves out of fifty, plus a small bonus for solving them cheaply.

The budgets are the trick. A single-procedure task allows two thousand interactions — enough to solve it by exhaustive trial. A chain task allows fifty. No amount of trial-and-error solves a chain in fifty interactions. The only way to solve chains is to have already learned the procedures as objects during the easy tasks, and to compose them, either by physically trying stored procedures or by simulating them in the head. Reuse is not merely rewarded; past a point it is the only thing that pays.

The intended mechanism is a chain of six links:

 acquisition ⟶ representation ⟶ retention ⟶ addressing ⟶ invocation ⟶ composition

Learn which label does which primitive; write a procedure down relative to its argument; keep it; find the right one later; run it on a new argument; compose several. The experiment was a ladder of four substrates that made these links successively cheaper to express. At rung A none of the links was a single instruction. At rung B the organism's instruction set gained typed procedure objects: one instruction opens a recording, one closes it, one invokes a stored procedure with an argument. At rung C it gained mental application: an instruction that applies a stored procedure to an imagined state without touching the world, so that planning a chain becomes possible in the head. At rung D, the search's recombination operator was allowed to splice fragments not only from the population but from three frozen, hand-written parts — a recorder, an invoker, a planner — that were never themselves members of the population.

Every rung was gated before any search ran. Eight witnesses had to pass on sealed task streams, the important four being: a positive control that accumulates procedures must beat the same control with its memory wiped before every task; transplanting only the learned objects into a naive copy of the same code must carry the advantage; deleting the objects must remove it; and the transferred objects must be genuinely procedural — the same object, applied to three different arguments, must produce three different behaviours, and a lookup table must gain nothing from the same transplant. Search ran only on rungs whose gate passed.

## 2The mechanism exists, and the world pays for it

These are measured, on task streams the searches never saw.

The hand-written positive control — a program that records procedures, keeps them, and plans over them — solves 45.7 of 50 tasks per lifetime with its memory intact and 20.3 with its memory wiped before every task. Same code; the difference is the objects it learned. It invokes a stored procedure about seventy-five times per lifetime.

Transplanting its learned objects, and nothing else, into a fresh copy of the same code solves six of the remaining tasks where the code alone solves one, at about a fifth less cost; ablating the objects returns the program to exactly the code-only figures. The advantage is in the artifacts. A lookup-table control, given the same transplant treatment, gains nothing.

And the mechanism is cheap to write in the organisms' own language. A sixty-four-instruction bytecode program containing a recorder, an invoker and a two-step planner solves 37.4 tasks per lifetime against 21.5 for the nineteen-instruction enumerator it was built from. Forty-seven edits separate the two. Sixteen tasks per lifetime is what those forty-seven edits are worth once they are all present.

So: the reward exists, the mechanism exists, the artifacts are causal, and the substrate can express the whole thing in a program shorter than this paragraph. If evolution's problem were capability, there would be no problem.

## 3What search did

The search was ordinary mutation-and-selection: a population of eight, twenty-four children per generation from point edits, duplications and spliced segments, three hundred generations, three arms (random initial programs, programs seeded from the competent enumerator, and a recombination arm). Every child was scored on two task streams shared by the whole generation, and a child that would displace a parent had to confirm the displacement on a third, independent stream — so that a lucky stream cannot carry a lineage. Three seeds per arm, nine runs per rung, thirty-six runs across the ladder. The decisive rungs C and D evaluated 129,744 candidate programs. The survivors of every run were then qualified on three sealed streams, with the full battery of memory-wipe, transplant, ablation and lookup-table controls.

The measured outcome:
- Zero candidates, in any of the thirty-six runs, showed a reproducible advantage of accumulated memory over wiped memory on the sealed streams that survived the controls. At the lower rungs a handful of lineages did show a reproducible advantage, and every one of them was a counter: a lineage that used the running count of stored objects as a clock to shift its enumeration order. Twenty empty records, made by nobody, reproduced the transplant exactly. At the decisive rungs, not even that.
- Zero runs produced the complete mechanism — a candidate that recorded a procedure, invoked its own recording, and solved a chain by doing so.
- Partial machinery appeared constantly and went nowhere. The recording instruction, the invocation instruction and the mental-application instruction were each executed by hundreds to thousands of candidates per run; they persisted in the elite for up to 146 consecutive generations; and they behaved throughout like neutral hitchhikers. Children that newly acquired a recorder improved on their parent less often than children carrying any other edit, in twelve of twelve runs; children newly acquiring an invoker, in ten of twelve.
- The tiny positive steps were noise. Every ancestral step in which a surviving lineage first executed a recorder or invoker was re-evaluated with its parent on the same sealed streams: nineteen such steps, nine of them positive, every one by about a thousandth of a fitness unit, with zero change in tasks solved on any stream. The same test applied to ancestral steps carrying no new typed instruction at all marks up to three in eight of them as "positive" by the same margin. The partial machinery was indistinguishable from the neutral-edit background.
- Donated fragments were stripped for parts, and the wrong parts. At rung D, 1,771 children carried a spliced fragment of a hand-written recorder, invoker or planner; sixty-three of those children won a takeover. Five fragments survived into the ancestry of a final survivor. Re-evaluated against their parents on the sealed streams, exactly one of the five paid — a single instruction, a constant load, worth one extra task on two of three streams. The fragment that made its carrier execute a procedure invocation was worth precisely zero. The recorder's digit-loop scaffolding was neutral. No retained fragment carried a link of the mechanism that executed with an effect.

Rung D's non-recombination arms reproduced rung C's byte for byte — the same best candidate in every seed — which is the expected determinism check and means everything rung D added lives in the three donor runs above. The disposition was scored mechanically from the receipts, against a rule written before the runs: closed, frontier mapped.

## 4Invocation without content

One fossil from the decisive rungs deserves its own section, because it may be the most general thing in this note.

Two of the surviving lineages had, by every superficial measure, discovered reuse. They filled the object store to its capacity of thirty-two blocks. They invoked those blocks forty-three and forty-nine times per lifetime. Traced through a lifetime, they looked busy in exactly the way the positive control looks busy.

Their fitness with memory intact, with memory wiped before every task, with memory reset at stage boundaries, and with memory scrambled was identical to the third decimal. Nothing they stored was read for anything. Nothing they invoked did anything the calling program could not have done itself. Selection had found the syntax of reuse without the semantics of reuse: the operations that constitute a memory system, arranged so that they cost nothing and mean nothing.

Why would selection keep such a thing? Because in this substrate the store-and-invoke operations were cheap, and once a lineage happens to execute them in a way that neither helps nor hurts, nothing removes them. They are the recorder-as-hitchhiker of the previous section, grown to full size. And they matter because they are precisely what a less careful assay would count as success. A census of "organisms that use memory" would have scored them. A census of "invocations per lifetime" would have scored them highly. Only the four-way comparison — the same program with its memory intact, wiped, reset and scrambled — shows that the memory carries nothing, and only the transplant and ablation controls show that the positive control's memory does.

We suspect this pathology is broader than one bytecode world, and we suspect it is common. Any adaptive system whose search space contains the operations of a capability can discover those operations without the content that makes them a capability, whenever the operations are cheap and the content is not on any local gradient. Stated as hypotheses, not findings: memory operations without useful memory; communication without informative messages; modularity without useful recombination; reasoning traces without causal contribution to the answer; tool invocation without useful state transfer. Each of these has been reported somewhere as a surprising failure mode. The Crius fossil suggests they may be one failure mode with one cause, and it suggests the control that exposes it: hold the machinery fixed and vary only whether its content is present.

## 5The cliff

Here is the landscape the campaign measured by construction, before any search ran. Each row is a hand-written program; the value is fitness relative to the row's immediate ancestor, on ten shared task streams, with the number of streams on which the sign was positive.

| Program | Adds | Edits from base | Δ fitness vs ancestor | Streams positive | Δ tasks / lifetime |
| enumerator | — | 0 | — | — | — |
| + recorder | records procedures, never uses them | 7 | −0.001 | 0 / 10 | 0.0 |
| + invoker | invokes procedures it never recorded | 20 | −0.002 | 0 / 10 | 0.0 |
| + recorder + invoker | records, then tries stored procedures physically | 26 | +1.138 | 7 / 10 | +1.1 |
| + planner | plans over procedures it does not have | 41 | −0.057 | 0 / 10 | 0.0 |
| + recorder + invoker + planner | the complete mechanism | 47 | +15.974 | 10 / 10 | +15.9 |

The measured assembly landscape. The planner alone is worth −0.057; the same planner with procedures already in the store is worth +16.7. The value of every link is conditional on the others being present. (Receipts: the PARTS diagnostic for rungs C and D, identical.)

Read down the table and the shape is plain. The first link is worthless. The second link alone is worthless. The two together are worth a little — one extra task per lifetime, at twenty-six coordinated edits — and that little is the only foothold on the whole path. The planner alone is slightly harmful. The planner on top of the pair is worth fifteen tasks. There is a valley one link deep, a small ledge, and then a cliff.

Formally: the finished mechanism M is a conjunction of links ℓ1, …, ℓk, and its value is large,

V(M) ≫ 0

while the values of the links, and of most subsets of the links, are not:

 V(ℓ1) ≈ 0, V(ℓ2) < 0, V(ℓ3) ≈ 0, …

Local adaptive search moves by accepting variants whose value is not worse. It therefore cannot be pulled toward M by V(M) until enough of M exists at once for some subset to pay. The eventual reward is real, but it casts no gradient back over the intermediate states. In the older language of population genetics this is a fitness valley, and its exact formal signature — changes that are separately unfavourable but jointly advantageous — is reciprocal sign epistasis, which is known to be a necessary condition for a landscape to have more than one peak.[4] Crius's recorder and invoker are a textbook instance: each alone costs a little; together they pay.

Two intuitive versions. Selection cannot see around corners: it responds to the value of what exists now, and the value of a half-built machine is the value of half a machine, which is usually nothing. The mountain exists, but there is no uphill trail leading to it: the summit's height is not in dispute; the question is whether every step from here to there can be taken without going down.

The precision matters. Mutation and recombination do jump valleys sometimes, and there is a literature on how: deleterious intermediates that persist long enough for a second mutation to rescue them,[6] neutral drift along networks of equivalent genotypes,[9,10] high-dimensional detours around what looks in low dimensions like an impasse.[8,11] Crius does not show that the valley is uncrossable. It shows that under this search — point edits, duplication, segment splice, a small elite, three hundred generations, competence-first selection with a takeover check — the route did not become an incremental selectable path, in thirty-six attempts, and that even handing the search the finished parts as donors did not make it one. The finding is about the absence of a gradient, not about the impossibility of a jump.

## 6Is this already known?

Largely, yes — and it is worth being exact about which part.

That fitness landscapes have valleys, and that valleys constrain which paths selection can take, is a century old and has been measured in proteins: of the 120 mutational orderings that could assemble a five-mutation antibiotic-resistance allele, 102 were inaccessible to Darwinian selection because some intermediate step went down.[2] "Evolutionary accessibility" is an established term with a quantitative theory.[3,5,7] Evolutionary computation knows the same phenomenon as deception: objective functions that lead search away from the objective,[14] and a whole line of work — novelty search, quality-diversity — exists because rewarding the goal directly so often fails to reach it.[15] Reinforcement learning has had the credit-assignment problem since 1961[16] and builds temporal abstractions largely to shorten the distance reward has to travel back.[17]

The closest experimental relative is older than all of Prometheus. When Lenski, Ofria, Pennock and Adami evolved digital organisms toward a complex logic function, populations that were also rewarded for the simpler functions it could be built from evolved it repeatedly — twenty-three of fifty — and in their words the complex feature never evolved when simpler functions were not rewarded.[1] That experiment removed the intermediate rewards deliberately, to show they were necessary. Crius is the same experiment from the other side: a world in which the intermediate steps toward a cognitive primitive are naturally unrewarded — there is no reason a world should pay for a recorder that records nothing useful — and in which making the steps cheaper to express, and even supplying them ready-made, did not substitute for paying for them.

So the general phenomenon is not new, and this note claims no priority on it. What we think is new, or at least newly sharp, is smaller and more useful:
- The subject. The valley here is not between two alleles of an enzyme; it lies in front of a cognitive primitive — procedural memory with reuse — in a substrate built to make that primitive representable. Whether the assembly geometry of cognition is generally valley-shaped is a question about intelligence, not about proteins.
- The separation. Existence, reward and path were each measured with their own controls. Most reports of "it didn't evolve" cannot say which of the three failed. Crius can: the first two passed, the third did not.
- The fossil. Syntax-without-semantics — a memory system that stores and invokes and carries nothing — is the specific shape selection settles into at the foot of the cliff, and it is detectable only by a content-varying control.
- The rulers (§8), which try to make "how far behind the frontier" a number that two substrates can be compared on.

Exaptation[12] and facilitated variation[13] are the biological accounts of how nature routinely gets across valleys of this kind: parts are useful for something else first, and conserved core components make large coordinated changes available as small regulatory ones. Both point directly at the experimental dials in §9. Crius had neither: no second use for a recorder, and a representation in which a link is a link and nothing more.

## 7A candidate principle

Not a law. An interpretation the experiment made us write down, phrased so that it can lose.

### Assembly-geometry principle — candidate

Whether a cognitive primitive appears in an adapting system is governed less by the primitive's cost or value once assembled than by the worst stretch of its best construction path: the longest run of consecutive links that receive no informative local credit. Two substrates that contain the same finished mechanism and pay it the same reward can differ, by the whole of accessibility, in whether adaptation ever finds it.

A weaker form, which Crius supports directly: a primitive is evolutionarily available only to the extent that adaptive search can obtain informative local credit for incomplete machinery leading toward it. A stronger form, which Crius merely suggests: the effective complexity of a cognitive mechanism is not the size of the finished mechanism but the depth of the deepest valley on the most accessible route to it — so that a forty-seven-edit mechanism with a smooth path is simpler, for evolution, than a ten-edit mechanism behind a two-link valley.

If that is right, then one of the hidden axes of intelligence is not memory, or compute, or representation size, or mutation rate, or modularity as such, but:

 The hidden axis how much useful gradient the substrate exposes toward not-yet-complete cognitive machinery

That would be a genuine property of a substrate, measurable independently of what the substrate can represent or what its world rewards, and it predicts something specific and uncomfortable: that a great many cognitive primitives are absent from a great many adaptive systems not because they would not work and not because they would not pay, but because their first three parts are worth nothing.

## 8Rulers to attack

A principle with no numbers is a slogan. These are attempts to make accessibility measurable; they are rulers to attack, not results. Where Crius already gives a value, it is stated.
- Assembly distance — the fewest edits from a competent baseline to the complete mechanism, in the substrate's own edit operators. Crius: 47 (a hand-constructed upper bound; evolution may know shorter routes we did not write).
- Accessible path length — the length of the shortest construction path along which every intermediate is non-deleterious or positively selected. Crius: undefined; no such path was found to exist, and the best route has a two-link stretch of zero or negative value before the first ledge.
- Valley depth — the largest fitness loss any step on the best available path must accept. Crius: shallow (−0.001 to −0.057) — which is the disquieting part. The valley is not deep; it is flat, and a flat valley gives selection no more to work with than a deep one.
- Foothold density — the fraction of incomplete states of the mechanism that receive measurable positive local credit, above the neutral-edit background. Crius: 0 of 19 ancestral partial-machinery steps exceeded the background; of the five hand-written partial states, one (the pair) was positive.
- Semantic-link survival — when a fragment of the mechanism enters a lineage, the probability that what selection keeps is the part carrying the causal link rather than incidental scaffolding. Crius: of five donor fragments retained into surviving ancestries, zero carried a working link; the one that paid was a constant load.
- Accessibility ratio — some comparison of the finished mechanism's value with the length and depth of the best incremental route to it. We do not yet have a form we trust; a first guess is

 ρ =  V(M) V(M) + dflat · c

where dflat is the longest run of consecutive links with no positive credit on the best path and c is the expected cost of crossing one such link by drift under the substrate's operators. It is offered so that someone can show it is the wrong quantity.

One instrument note that belongs with the rulers, because it is what made them measurable at all. The search's own fitness values are not paired: a parent carries the fitness it earned on earlier task streams, and the takeover check compares a child with the member it displaces, with ties counting as takeovers. "Did this partial pay?" can only be answered by re-evaluating parent and child on the same held-out streams and comparing the result with what neutral edits do under the same test. Without that base rate, the +0.001 steps in §3 would have counted as footholds.

## 9What this suggests we should build

If the principle is right, then the interesting experimental variable is not the mechanism and not the reward but the construction landscape between them, and there are many dials on it that Crius held fixed:
- Locality of credit — whether an incomplete mechanism can be paid for the part of the outcome it causally contributed to, rather than only for tasks solved.
- Independent utility of parts — whether a recorder, an invoker, a planner have any use on their own, for anything.
- Ecological niches — environments in which each link, alone, is the best available strategy for some subpopulation.
- Developmental staging — task sequences in which the links become useful in order.
- Exaptation — parts that are selected for one role and are already present when a second role appears.
- Recombination granularity — whether the operators that move fragments between lineages move whole semantic links or only instruction runs.
- Physical coupling — substrate physics in which several mutually dependent components arise from one primitive operation, so that the pair is one edit rather than twenty-six.
- Representation — encodings that shorten the semantic edit distance from a competent program to a reusing one.

Each of these is a way of changing the path while leaving the destination and the payoff alone. That is the experiment.

## 10Why a closed negative result is worth a note

"We tried to evolve X and it didn't" is not, on its own, a result. What makes Crius worth writing down is that the failure was localised. The world rewards reuse: measured. The complete mechanism works and is short: measured. The learned objects, not the code, carry the advantage: measured, by transplant and ablation. Search reaches the neighbourhood — it finds the store, the invocation, the scaffolding of the parts, the syntax of the whole thing: measured. Search fails at one step, the assembly of a semantic link whose value depends on another link being already present: measured, by re-evaluating every such step against its background. That is a map with one feature on it, and the feature has a name:

 The accessibility frontier the boundary separating the mechanisms that exist in a substrate from the mechanisms an adaptive process can reliably reach

Crius located that frontier for one primitive in one substrate: on the near side, counters, clocks and content-free invocation; on the far side, one small ledge twenty-six edits out and the whole mechanism twenty-one edits beyond it. The campaign was closed, rather than continued, because the rule for closing it was written before the decisive runs and every clause of that rule came out on the same side; because the moves that could change the outcome — lowering the gates, adding budget, seeding parts into the population — would have measured our persistence rather than the substrate; and because the shape was the same in every arm and at every rung. More search under this substrate would have been a test of search budget. The frontier is the result.

## Three reasons this might not be fundamental

A candidate principle should name its own best attackers. These are the ones that worry us.

It may only be a bad representation. Typed procedural reuse may be inaccessible in Crius's bytecode because Crius encoded it badly — because the recorder and the invoker are separate instructions that must be separately acquired, because the argument passes through a register that a loop can clobber, because the planner is a large structured edit in a representation with only local operators. Another substrate could make the same concept locally smooth, and then the valley is a fact about one encoding. We think this is likely to be partly true. Note what it would and would not cost the argument: it would remove any claim that procedural reuse is generally hard to reach, and it would strengthen the claim that assembly geometry, not capability, is what decides — because the same mechanism with the same payoff would then be reachable or not depending on how it is spelled. That is precisely the controlled pair proposed below. The neutral-network literature[9,10,11] is the strongest form of this objection: in biologically realistic genotype-phenotype maps, fitness maxima can be reached from almost anywhere without crossing a valley, because the maps are enormously many-to-one and the neutral networks percolate. Crius's map — programs to behaviours — has some of that structure and evidently not enough of it near this phenotype.

Evolution crosses valleys all the time. Drift, duplication, exaptation, ecological heterogeneity, sexual recombination, development, population structure and changing environments all construct things that competence-first hill-climbing cannot, and there is experimental evidence that permitting deleterious intermediates produces higher long-run fitness than forbidding them.[6] Crius tested one bounded search regime — a small elite, local operators, three hundred generations — and not "evolution" in its biological entirety. The result should be read as a statement about that regime. What survives the objection is the accounting: whichever of those mechanisms would have crossed this valley, it would have done so by supplying credit or persistence for the intermediates, which is to say by changing the path rather than the destination — which is the principle, restated.

Forty-seven edits may simply be too far for this campaign. Enough search finds anything; perhaps a larger population or ten thousand generations would have hit the mechanism. We do not doubt it. But the measured question was not whether the finished mechanism could eventually be drawn in a lottery; it was whether the substrate created an incremental, selectable path toward it, and on that question more tickets do not change the answer. If a future run finds the mechanism by a single large jump with no selectable precursors, the principle is confirmed, not refuted. What would refute it is a lineage that climbs — a recorder that pays before the invoker exists, an invoker that pays before the planner — in a substrate where Crius's did not.

A fourth, which the evidence itself raises: the assembly distance of forty-seven is the length of our hand-written route, and the valley is the valley along our route. Evolution may know construction paths through this substrate that no one wrote down. Thirty-six runs did not find one, which bounds their frequency but does not prove their absence.

## The experiment that would settle it

The accessibility principle makes one prediction sharp enough to be a cross-engine test:

 The controlled pair Same destination. Same payoff. Different assembly geometry.
 → radically different probability of discovering the cognitive primitive.

Build two worlds that contain exactly the same finished mechanism and assign it exactly the same final reward, and vary only the construction landscape between the competent baseline and the mechanism. Concretely, any of:
- A. Give the partial components independent secondary uses.
- B. Add ecological niches in which the recorder, the invoker and the planner are each independently the best thing to be.
- C. Alter recombination so that semantic links are physically coupled and move together.
- D. Provide developmental stages in which each link becomes useful in sequence.
- E. Introduce local credit for downstream causal contribution, so that a partial mechanism can be paid for the part of the outcome it produced.
- F. Change the substrate physics so that several mutually dependent components emerge from one primitive operation.
- G. Transplant the Crius challenge — the same six-link chain, the same gates, the same controls — into radically different substrates and see where the frontier falls.

The prediction is that the mechanism's discovery rate will track the geometry and not the payoff. The refutation is a pair in which it does not: where smoothing the path leaves the primitive as absent as before, or where the primitive appears in the rough world as readily as in the smooth one. Either would be worth more than this note.

Several Prometheus engines are shaped for pieces of this. Cosmos, the World-Graph Engine, is built to change almost everything about a universe and measure what refuses to change, which is the controlled pair by construction. BEE, the Worlds Kernel, can lower one experiment description onto different machinery, which is test G. Ensorain's Tensor World Engine and Aether's AGE ecosystem each have physics in which coupling components (F) and local credit (E) could be native rather than bolted on. Nestor's engine is where a surviving claim would go for the preregistered large-campaign treatment. None of this is a plan to reopen Crius. Crius's lane is closed; its substrate, gates and controls are public and can be lifted whole.

### Provenance

What Crius measured (§1–§5, §8 values): the controls, gates, PARTS landscape, thirty-six search runs, path evidence and paired re-evaluations, all from committed receipts. The originating experiment is Campaign 2 of the Crius seat; its terminal review, preregistration and fingerprinted disposition receipt are public in the Prometheus repository under crius/ <https://github.com/jcraig949jfi/Prometheus/tree/main/crius> (terminal review: CRIUS_C2_TERMINAL_REVIEW.md <https://github.com/jcraig949jfi/Prometheus/blob/main/crius/CRIUS_C2_TERMINAL_REVIEW.md>; closing commit 7069c0ce6, on main at 371d22952). The disposition was computed by a script from the receipts against a rule written before the decisive runs.

What Crius infers (§5, §6, §10): that the failure is one of accessibility and not of capability or reward; that its shape is a flat valley followed by a cliff; that the content-free invocation fossil is what selection settles into at the foot of it.

What Crius proposes (§7–§9, the closing experiment): the assembly-geometry principle, the hidden axis, the rulers and the controlled pair. None of these has been tested anywhere. They are stated to be attacked.

## Sources
- Richard E. Lenski, Charles Ofria, Robert T. Pennock, Christoph Adami, “The evolutionary origin of complex features”, Nature 423, 139–144 (2003). doi:10.1038/nature01568 <https://www.nature.com/articles/nature01568> The closest experimental relative. Digital organisms evolved a complex logic function in 23 of 50 populations when its simpler components were also rewarded, and the feature “never evolved when simpler functions were not rewarded.” Crius is the same experiment with the intermediate rewards naturally absent.
- Daniel M. Weinreich, Nigel F. Delaney, Mark A. DePristo, Daniel L. Hartl, “Darwinian evolution can follow only very few mutational paths to fitter proteins”, Science 312, 111–114 (2006). doi:10.1126/science.1123539 <https://doi.org/10.1126/science.1123539> Five mutations, 120 orderings, 102 of them inaccessible to selection because an intermediate step goes down. Accessibility measured in a real protein.
- Frank J. Poelwijk, Daniel J. Kiviet, Daniel M. Weinreich, Sander J. Tans, “Empirical fitness landscapes reveal accessible evolutionary paths”, Nature 445, 383–386 (2007). doi:10.1038/nature05451 <https://www.nature.com/articles/nature05451> Intermediates, not endpoints, determine which paths evolution takes.
- Frank J. Poelwijk, Sorin Tănase-Nicola, Daniel J. Kiviet, Sander J. Tans, “Reciprocal sign epistasis is a necessary condition for multi-peaked fitness landscapes”, J. Theor. Biol. 272, 141–144 (2011). doi:10.1016/j.jtbi.2010.12.015 <https://doi.org/10.1016/j.jtbi.2010.12.015> Changes that are separately unfavourable but jointly advantageous: the exact formal signature of Crius's recorder-and-invoker pair.
- Jasper Franke, Alexander Klözer, J. Arjan G. M. de Visser, Joachim Krug, “Evolutionary accessibility of mutational pathways”, PLoS Comput. Biol. 7(8), e1002134 (2011). doi:10.1371/journal.pcbi.1002134 <https://doi.org/10.1371/journal.pcbi.1002134> “Evolutionary accessibility” as a quantitative property of a landscape, with a theory of how it scales.
- Arthur W. Covert III, Richard E. Lenski, Claus O. Wilke, Charles Ofria, “Experiments on the role of deleterious mutations as stepping stones in adaptive evolution”, Proc. Natl. Acad. Sci. USA 110(34), E3171–E3178 (2013). doi:10.1073/pnas.1313424110 <https://doi.org/10.1073/pnas.1313424110> Counter-evidence to any strong reading: populations allowed deleterious intermediates reached higher long-run fitness than populations forbidden them, because some intermediates were stepping stones across otherwise impassable valleys.
- Stuart A. Kauffman, Simon Levin, “Towards a general theory of adaptive walks on rugged landscapes”, J. Theor. Biol. 128(1), 11–45 (1987). doi:10.1016/S0022-5193(87)80029-2 <https://doi.org/10.1016/S0022-5193(87)80029-2> The NK model: ruggedness as a tunable property of a landscape, and adaptive walks as the process that ruggedness constrains.
- Sergey Gavrilets, “Evolution and speciation on holey adaptive landscapes”, Trends Ecol. Evol. 12(8), 307–312 (1997). doi:10.1016/S0169-5347(97)01098-7 <https://doi.org/10.1016/S0169-5347(97)01098-7> In high enough dimension the valley-crossing problem may not exist: ridges of near-equal fitness connect what looks separated in three dimensions. An objection this note must survive.
- Peter Schuster, Walter Fontana, Peter F. Stadler, Ivo L. Hofacker, “From sequences to shapes and back: a case study in RNA secondary structures”, Proc. R. Soc. Lond. B 255, 279–284 (1994). doi:10.1098/rspb.1994.0040 <https://doi.org/10.1098/rspb.1994.0040> Neutral networks: all common structures reachable from an arbitrary sequence by far fewer mutations than the chain length.
- Andreas Wagner, “Robustness and evolvability: a paradox resolved”, Proc. R. Soc. B 275, 91–100 (2008). doi:10.1098/rspb.2007.1137 <https://doi.org/10.1098/rspb.2007.1137> Large connected neutral networks make phenotypes both robust and evolvable — the mechanism by which real substrates avoid the trap Crius fell into.
- Sam F. Greenbury, Ard A. Louis, Sebastian E. Ahnert, “The structure of genotype–phenotype maps makes fitness landscapes navigable”, Nat. Ecol. Evol. 6, 1742–1752 (2022). doi:10.1038/s41559-022-01867-z <https://doi.org/10.1038/s41559-022-01867-z> For RNA, protein and protein-complex maps, even under random fitness assignment, maxima are reachable from almost any phenotype without crossing a valley. The strongest version of the “bad representation” objection.
- Stephen Jay Gould, Elisabeth S. Vrba, “Exaptation — a missing term in the science of form”, Paleobiology 8(1), 4–15 (1982). doi:10.1017/S0094837300004310 <https://doi.org/10.1017/S0094837300004310> Features not built for their current role but available for it: nature's standard route across an assembly valley, and dial A of the closing experiment.
- John Gerhart, Marc Kirschner, “The theory of facilitated variation”, Proc. Natl. Acad. Sci. USA 104(suppl. 1), 8582–8589 (2007). doi:10.1073/pnas.0701035104 <https://doi.org/10.1073/pnas.0701035104> Conserved core components make large coordinated phenotypic change available as small regulatory change: an existence proof that substrates can shorten semantic edit distance.
- David E. Goldberg, “Simple genetic algorithms and the minimal, deceptive problem”, in L. Davis (ed.), Genetic Algorithms and Simulated Annealing, Morgan Kaufmann, 74–88 (1987). Deception: objective functions that lead a genetic algorithm away from the optimum. The evolutionary-computation name for the cliff.
- Joel Lehman, Kenneth O. Stanley, “Abandoning objectives: evolution through the search for novelty alone”, Evolutionary Computation 19(2), 189–223 (2011). doi:10.1162/EVCO_a_00025 <https://doi.org/10.1162/EVCO_a_00025> A search method that exists because rewarding the goal directly so often fails to reach it; the origin of the quality-diversity line.
- Marvin Minsky, “Steps toward artificial intelligence”, Proc. IRE 49(1), 8–30 (1961). doi:10.1109/JRPROC.1961.287775 <https://doi.org/10.1109/JRPROC.1961.287775> The credit-assignment problem, named. Accessibility is credit assignment across construction rather than across time.
- Richard S. Sutton, Doina Precup, Satinder Singh, “Between MDPs and semi-MDPs: a framework for temporal abstraction in reinforcement learning”, Artificial Intelligence 112(1–2), 181–211 (1999). doi:10.1016/S0004-3702(99)00052-1 <https://doi.org/10.1016/S0004-3702(99)00052-1> Options: temporal abstractions built largely to shorten the distance credit must travel. Dial E of the closing experiment has the same shape.

 This page is the current version. The original 2026-09-24 text is preserved unedited as 2026-09-24-accessibility-frontier.md; the page may carry later revisions, so the two can differ by design. Citation verification is in SOURCES_accessibility-frontier.md.
 Status: §1–§5 are a measured result from a closed Prometheus campaign (Crius, Campaign 2; receipts in the repository, closing commit 7069c0ce6). §6–§10 are interpretation; §7–§9 and the closing experiment are proposals, untested anywhere, stated to be attacked. Crius's experimental lane remains closed; this note does not reopen it.
 Companion note: Selective Irreversibility. Equations are typeset in plain HTML and CSS — no JavaScript, no external fonts, nothing to fail.
