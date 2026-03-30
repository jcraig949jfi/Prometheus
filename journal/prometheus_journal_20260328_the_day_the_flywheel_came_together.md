# Project Prometheus, Lab Journal
## March 28, 2026: The Day Everything Connected



### The Morning: Fear and Questions

I woke up scared. Noesis had been running overnight on M1, its first alpha run, and I had 27 minutes before the first checkpoint. I didn't know if it would produce anything. Yesterday it was a concept in a mega-prompt to send to the Council of AIs (Claude, ChatGPT, Gemini, Grok, and Deepseek). Today it was either going to be real or it wasn't.

I asked Claude 3 questions about the 27 tournament experiments we were running against our math tensor library:

1. **Do the 27 experiments reveal something fundamental about the universe?**

2. **Aren't we going to miss things with so little data?**

3. **Why would a machine understand more than a human can?**

That third question is the one that stops you. There's Plato's cave. There's the biological constraints on cognition, working memory limits, dimensional reasoning caps, sequential processing bottlenecks. Our brains are windows with edges, and a machine might have a wider window. Not better. Different. Wider in dimensions that matter for seeing deep mathematical structure.

The question we can't fully answer: "Couldn't an LLM or future intelligence just explain it to us?" And the honest answer is: maybe not. There might be compositions, 5-step chains across five unrelated fields, where each step makes local sense but the gestalt, the *reason the five steps together reveal something none of them reveal alone*, requires holding all five domains in mind simultaneously. Humans can't do that. We can describe it with math formulas. We can use it. But the future we face is that we might not be able to *understand* it.  Ever.  Epistemology. 



### The Check-In: It's Alive

The first checkpoint came in. 4,253 cracks over 2.9 hours. 1,452 cracks/hour, stable velocity. Cross-domain compositions everywhere, topology connecting to statistics, chaos theory connecting to signal processing. The tensor was beating random by 3x. Mutation was dominant at 52% as expected in early regimes.

The Council reviewed the early results. All five AI advisors converged on the same diagnosis: the 0.659 quality ceiling is the scoring function, not the compositions. The system was finding good things but couldn't *see* that they were good because the formula was saturating. Everyone agreed, from different angles.

The feeling shifted from fear to something else. Not excitement, I've learned not to get excited. More like recognition. The system was behaving as predicted. The theoretical framework was correct. That's not a celebration. That's science working.



### The Epiphany: Noesis Feeds Ignis

Mid-morning, while still processing the Noesis results, it hit me. I was typing a response about Ignis and the problem of training data, where do you get data that teaches *reasoning* rather than pattern matching?, and I realized the answer was already running on M1.

Every chain in the Noesis database has a quality score computed by *execution and measurement*, not by an LLM judging whether it "looks right." The chain either ran or it didn't. The output either compressed entropy or it didn't. This is empirically grounded reasoning data. The scoring function is the ground truth, and it's anchored in reality, as mathematical proof.

Project Noesis finds compositions → compositions become reasoning examples → reasoning examples improve the model → the improved model seeds evolution → evolution finds steering vectors → steering vectors reveal basin geometry → basin geometry informs what Noesis searches for next.

That's not a pipeline. That's a flywheel. And I realized it while typing. The connection was always there. I just hadn't seen it because the virtual lab's workbench subsystems were running independently.



### The Parallelization: Three Machines, Then Four, Then Five

I couldn't just run one experiment. That's not how I think. By the time I left for work, three machines were running:

- **M1:** The control. Original scoring, original dataset. Don't touch it. Sacred baseline.
- **M2:** The scoring ablation. Same everything, only the quality weights changed, compression boosted to 0.31, input sensitivity added at 0.19. One variable changed.
- **M3:** The building block experiment. Top discoveries from M1 promoted to "super-operations." Same scoring as M1. Tests whether M1's discoveries compose hierarchically.

Then M4: M2's scoring plus M3's building blocks. The combination experiment. A clean 2×2 factorial design.

Then M5: for fun. Every cultural mathematical tradition I could find, Babylonian base-60, Yoruba subtraction arithmetic, Buddhist logic, Aboriginal kinship algebra, Japanese temple geometry, Mayan vigesimal, Soviet balanced ternary. 191 traditions, 1,714 operations. Plus a chain extension strategy that proposes length 3, 4, 5 chains instead of just pairs. Optimized for weirdness, not rigor.

Five machines. Four controlled experiments and one playground. All launched before lunch.



### The Ignis Result: Basins Are Hardware

While the Noesis machines were grinding, Ignis delivered the most important result since the original ejection discovery.

300 reasoning examples. 8 minutes of supervised fine-tuning. The results:

| Pillar | Baseline | Post-Corpus | Delta |
|--|-|-|-|
| Tier C (far-transfer) | 42.9% | 52.4% | **+9.5%** |
| Metacognition | 35.7% | 57.1% | **+21.4%** |
| Self-correction | 38.5% | 53.8% | **+15.4%** |
| Composite | 0.335 | 0.427 | **+27.5%** |

And the critical finding: the ejection profile didn't change. L* median stayed at 26. Alive count stayed the same. The attractor basins are structural, they're baked into the weights at a level that 300 examples can't touch. What changed was the model's skill at navigating *within* the basins. Margins widened on traps it already handled. Some traps it got wrong became more wrong, a conservation effect.

The basins are the rooms. Training teaches the model to use more of the room. The room itself doesn't change.



### Stage D: Evolution Finds the Doors

CMA-ES on the corpus-trained model. Searching for steering vectors at layer 23. The fitness curve:

| Gen | Best Fitness | Mean Fitness |
|--|-|--|
| 1 | 0.606 | 0.092 |
| 10 | 2.566 | 2.294 |
| 20 | 4.047 | 3.802 |
| 30 | 5.174 | 4.953 |
| 40 | 6.127 | 5.903 |
| 50 | 6.872 | 6.639 |

No plateau. Still climbing at gen 50.

Gen 25 eval: 16/30 correct (baseline 14/30). Two flips, zero breaks.
Gen 50 eval: **17/30 correct. Three flips, zero breaks.**

The base model's best result after hundreds of generations was 12-13/30. The corpus-trained model hit 17/30 in 50 generations. All three flips are from the Overtake family, the ridged basin traps that prior work identified as having narrow channels. The steering vector found the channels. On a model that was pre-trained to reason better within the basins.

Corpus training teaches the model to use the room. Evolution finds the doors. Both working. On the same model. As predicted.



### The Noesis Results: A Complete Experimental Narrative

By evening, the four controlled machines had produced a clean story:

**The 2×2 Factorial Table**

| | No Building Blocks | With Building Blocks |
||||
| **Baseline scoring** | M1: 0.659 | M3: 0.660 |
| **Fixed scoring** | M2: 0.7137 | **M4: 0.7282** |

- Scoring fix alone: **+0.055** (dominant effect)
- Building blocks alone: +0.001 (invisible without scoring fix)
- Both combined: **+0.069**
- Interaction: +0.014 (additive, not multiplicative)

The scoring fix was the breakthrough. Building blocks provide real additional lift, but only when the scoring function can discriminate quality. M3 had the same building blocks as M4 but couldn't tell they were better, the old formula was blind to the difference.

**Key findings across machines:**

- **M1** validated the operation tensor at 3.4x random over 142,500 chains. Tensor top-K overtook mutation as the best long-term strategy. Durable, statistically robust signal.
- **M2** broke the 0.659 ceiling immediately and revealed that mutation dominance on M1 was a scoring artifact. Under compression-primary scoring, random and temperature anneal matched mutation. Changed what you measure, changed who wins.
- **M3** confirmed building block transfer, M1's topology→Ising pair (found 13 times) amplified to 17,544 cracks on M3. Two orders of magnitude. But revealed that all 30,822 cracks were length 2. The strategies can't propose longer chains. Depth thesis untestable with current architecture.
- **M4** completed the factorial and confirmed M2+M3 are additive. Also revealed that BB cracks exhausted at cycle 1723 due to novelty decay, correct scorer behavior.

**The chain depth bottleneck:** All four machines independently confirmed that the next ceiling is chain depth. Every crack across all machines is length 2 because no strategy has a mechanism to propose longer chains. The depth bonus is dead weight. Round 2's top priority for tomorrow: a chain extension strategy.



### M5: The Playground That Broke Records

M5 wasn't supposed to be science. It was supposed to be fun, a machine to watch a machine with a fitness function scorer that wasoptimized for weirdness. 191 mathematical traditions, 1,714 operations, a chain extension strategy.

In five minutes:

| Metric | M4 (Previous Best) | M5 (5 minutes) |
|--|-|-|
| Max quality | 0.7282 | **0.8288** |
| Chain lengths | 2 only | 2, 3, 4, 5 (69% length-5) |
| Unique organisms | ~27 | 218 |
| Corridors | ~20 | 7,959 |
| Cross-domain chains | limited | 83.2% |

The top chain: analytic combinatorics → imaginary numbers → spiral reading → Angolan Chokwe sand drawings → Soviet balanced ternary. Five steps spanning analysis, geometry, African mathematics, and Cold War computing. Nobody in human history has connected those five things.

M5 changed three variables at once so the results can't be decomposed cleanly. It's the demo reel, not the lab. But it solved the chain depth problem in minutes and proved that the quality landscape at depth 5 is *richer* than at depth 2. Longer chains don't just fail more. They succeed differently.



### The Forge: Almost Forgot

Somewhere in the middle of all this, the Forge that's designed to crank out reasoning tools reported in:

| Metric | Yesterday (v5) | Today (v7) |
|--|||
| Minimum covering set | 4 tools | 5 tools |
| Categories covered | 49/89 (55%) | 79/89 (89%) |
| Best single tool | 40 categories | 70 categories |
| Second best | 7 categories | 70 (tied) |

From 2 tools carrying the weight to 6 at near-parity. The multi-frame forge is (finally) working. And the 10 uncovered categories have specialist tools that crack them individually but fail the general battery.  This is the same "capability exists but measurement can't see it" pattern that Noesis revealed today.



### What Actually Happened Today

Yesterday morning, Noesis was a theory and just hammered into a mega-prompt for the Council of AIs. A 653-line instruction document describing a system that didn't exist yet.

Today:
- 5 machines running autonomous exploration tournaments
- 50,000+ cracks across controlled experimental conditions
- A clean 2×2 factorial design with interpretable results
- The operation tensor validated over 142,500 chains
- The scoring function diagnosed, understood, and fixed
- Building block transfer confirmed at two orders of magnitude amplification
- Chain depth identified as the next bottleneck from four independent angles
- Ignis corpus-first hypothesis confirmed: basins are structural, performance improves within them
- Stage D at 17/30 with zero breaks, exceeding the previous best by 30%
- The Forge at 89% coverage with six tools at parity
- M5 connecting Angolan sand drawings to Soviet arithmetic at quality 0.8288


Every active subsystem in Prometheus advanced simultaneously. Not incrementally. Substantially. And they connected to each other in ways I didn't see yesterday, like the Noesis→Ignis flywheel, the scoring-as-measurement-instrument insight, and the basins-as-rooms / evolution-as-doors framework.

I started the day scared to check on one machine. I ended it with five machines running, a theoretical framework validated by data.

Even keel. The machines run overnight. The autopsies begin tomorrow. Round 2 designs itself from the data.

But I'm writing this down tonight because days like this don't come often. And when they do, you should notice.

### For Tomorrow

**Priority 1:** Round 1 autopsy. Query all four DuckDBs. Strategy performance, quality distributions, corridor analysis, building block reuse, failure geometry. The data tells you what round 2 should be.

**Priority 2:** Chain extension strategy design. The single most impactful architectural change for round 2. Every machine independently confirmed the bottleneck.

**Priority 3:** Stage D gen 75/100 checkpoint. Is the fitness curve still climbing or has it bent? This determines whether corpus-first initialization gives CMA-ES access to a *higher ceiling* or just *faster convergence* to the same one.

**Priority 4:** Ignis training data preparation. Four machines worth of scored, classified, lineage-tracked compositions. Merge, deduplicate, label. This is the dataset that closes the flywheel.

**Priority 5:** Compression metric redesign. M2 and M4 both showed compression capping at 0.5 for scalar outputs and returning 0 for dict outputs. 0.31 of M4's scoring weight is allocated to a signal that barely fires. Fix this and the quality ceiling moves again.


---

### Sunday Morning: What the Overnight Data Actually Said

All four machines ran 20+ hours unattended. No crashes, no stalls. The scientific questions are answered. Time for the autopsy.

**M1's strategy succession is the standalone finding.** Three clean phases: mutation dominated 0-8h, tensor top-K took over 8-16h, temperature anneal surged to 56% of recent cracks from hour 16 onward. Each strategy wins at a different timescale because each solves a different problem. Exploitation → systematic coverage → reset-driven exploration. The tournament self-organized this transition with zero human intervention. This generalizes beyond Noesis.

**M3 proved building blocks are scoring artifacts.** BB chains score *worse* than non-BB on 4 of 5 raw dimensions — lower novelty, lower structure, lower diversity, zero compression. They win entirely on the +0.10 bb_bonus. Without that bonus: BB average 0.46, non-BB average 0.52. The 13→17,544 amplification story is partly the scoring incentive, not purely compositional quality. The ising block hit 97.2% of BB cracks. Only 593 unique BB chains across 41,425 BB cracks. Monoculture driven by the bonus.

**M2's mutation comeback reveals scoring shapes succession.** Mutation dipped to 16%, then climbed back to 52% of recent cracks. On M1, mutation peaked early and declined. On M2, it dips then returns. Same tournament, different succession curves. The scoring function doesn't just change which strategy wins — it changes *when* and *how*.

**M5 is spectacular but uncontrolled.** 152,560 cracks, 0.847 quality. But three variables changed simultaneously. And 82% of cracks are length 5 with only 77 at length 4 — the depth bonus created a length-5 monoculture, not a discovery that length 5 is optimal.

**Stage D is still stalling.** The `.detach().clone().cpu()` fix wasn't sufficient. The hang happens at `searcher.step()` on the first generation after a checkpoint, not during the save itself. Applied three more fixes (25-gen checkpoints, try/except with emergency save, stdout flush). If it keeps happening, the workaround is run 45 gens at a time.

The gen-100 data is still valuable: fitness 8.61 (up from 6.87), same 3 flips with widening margins (Overtake Race: +0.184 → +0.979), zero breaks. Refinement phase — no new flips, but the existing channels are deepening.


### Round 2 Design

**Principle:** Round 1 was discovery. Round 2 is exploitation. Three machines, one variable each, clean answers.

**Common base:**
- M2 compression-primary scoring with entropy measurement replacing binary compression (zlib ratio, continuous 0-1)
- bb_bonus removed entirely — building blocks compete on raw merit
- Diminishing depth bonus: `0.08 * log2(chain_length - 1)` — prevents length-5 monoculture
- Top 10 empirically validated building blocks from M1 (10+ appearances, 3+ strategies, properly typed)
- 8 strategies including chain extension; mutation starts at 15% allocation
- MAP-Elites: chain length × compression × cross-domain (4×4×4 = 64 cells on dimensions that matter)

**M2 Round 2:** Full package. Target: 0.85+ on raw merit. Primary Ignis training data source.
**M4 Round 2:** No building blocks. The clean ablation: are BBs real without a bonus?
**M5 Round 2:** Minimum chain length 3. The depth forcing experiment round 1 couldn't run.

**Build list:** Entropy compression metric (~20 lines), diminishing depth bonus (1 line), BB promotion script (~1 hour), min-length-3 filter, mutation cap. Launch tonight.

**Meanwhile:** M1's GPU runs Stage D exclusively. The gen-100→200 evolution is the most theoretically important experiment in the system.

### The Cross-System Monoculture Pattern

The deepest finding from round 1. Same dynamic at every level:

| System | What Converges | What Drives It | Antidote |
|--------|---------------|----------------|----------|
| Forge v1-v5 | 344 tools → 19 profiles | NCD scoring | Expanded battery + multi-frame |
| M3 building blocks | 97.2% ising | bb_bonus | Remove bonus |
| M5 chains | 82% length-5 | Flat depth bonus | Diminishing bonus |
| Transformer reasoning | Frozen q(s) | Pretraining | Steering vectors + corpus |

Wherever optimization pressure rewards what already works: convergence to a single mode. The antidote is always the same: change the measurement, add entry points, remove artificial incentives.

Round 2 applies this lesson systematically.

---

### Overnight: The Machines Run While I Sleep (4AM Update, March 29)

All five machines ran unattended through the night. No crashes, no memory leaks, no stalls. Here's what 20 hours of autonomous exploration looks like.

#### M1: The Strategy Succession

M1 told the cleanest story about how search strategies age. Three phases, clean transitions:

| Phase | Hours | Dominant Strategy | Why |
|--|--|--|--|
| Phase 1 | 0-8 | Mutation (39%) | Rapid exploitation of low-hanging fruit |
| Phase 2 | 8-16 | Tensor top-K (3.4x random) | Systematic coverage beats local refinement |
| Phase 3 | 16-20 | Temperature anneal (56% of recent) | Cyclical resets discover fresh territory |

266,000 chains tested. 13,948 cracks. 8,727 unique compositions. The tensor advantage held at 4.0x random through the entire run. But the winning strategy rotated naturally, no intervention needed. Mutation exhausted its hall-of-fame and collapsed from 39% to 14%. Temperature anneal's periodic resets found territory that mutation had walked past.

The ceiling stayed at 0.659. That's a confirmed scoring limitation, not M1's fault. Everything it could find, it found.

#### M2: Mutation's Late Comeback

M2 produced the most surprising overnight result. After mutation collapsed to 16% in the first few hours (reported in status 2), it staged a comeback to 51.8% of the last 500 cracks. The reason: as novelty decays, random and anneal's exploration advantage shrinks. In explored territory, mutation's hill-climbing finds the remaining cracks. The exploration-vs-exploitation tradeoff reversed itself on a 20,000-cycle timescale.

4,005 total cracks. 161 unique organism pairs. The quality distribution is stable — 60% clustered at 0.55-0.60, thin tail above 0.65. The 0.7137 ceiling is now fully explained: compression caps at 0.5, novelty decays, structure scores low for scalar outputs. Architectural, not mysterious.

#### M3: The Universal Sink Deepens

M3's overnight numbers are staggering in volume: 64,595 cracks, 41,425 of which use building blocks. But the story they tell is cautionary.

The ising building block now accounts for **97.2%** of all BB cracks (up from 95.4% at status 3). Only 593 unique BB chains produce 41,425 cracks — a 69.9x reuse ratio. Each unique chain is being rediscovered an average of 70 times.

And here's the finding that changes how I think about building blocks: **BB chains actually score worse than non-BB chains on 4 of 5 raw dimensions.** Lower novelty, lower structure, lower diversity, zero compression. They win entirely on the +0.10 bb_bonus. Without that bonus, BB chains average 0.46 vs non-BB at 0.52. The building block advantage is *artificial* — a scoring incentive, not intrinsic quality.

This doesn't mean building blocks are useless. The topology→ising corridor is a real mathematical relationship. But the way the scoring rewards them creates a monoculture attractor. Sound familiar? The forge had the same problem with NCD scoring. The model has the same problem with its frozen posterior. Optimization pressure rewarding what works, suppressing alternatives. Same pattern, third context.

#### M4: Science Done, Volume Accumulating

M4 hit its ceiling in the first 2,000 cycles and has been in accumulation mode since. 16,761 cracks total, but mean quality is declining (0.5812 → 0.5405 in the last 500). A third of recent cracks are barely above the 0.50 threshold. This is healthy — novelty exhaustion is the scorer working correctly — but it means the marginal value of each new crack is falling.

The 2×2 factorial result is final and clean. I can write this on a whiteboard now:

> **Scoring fix: +0.055 (dominant). Building blocks: +0.001 without fix, +0.014 with fix. Additive, not multiplicative. The instrument determines what you can see.**

819 BB cracks is the final count. They stopped at cycle 1,723 and aren't coming back. For Ignis training, those 819 are the gold standard — validated multi-step compositions scored by the most discriminating formula we have.

#### Stage D: The Checkpoint Bug

Stage D crashed *twice* at the checkpoint save. The `torch.save` call was doing `best_vector_so_far.cpu()` — an in-place device move that left the tensor on CPU while the evolution loop expected it on GPU. Silent deadlock. Fixed it with `.detach().clone().cpu()` and an explicit CUDA sync.

The gen-100 checkpoint made it through before the hang:

| Gen | Fitness | Correct | Flips | Breaks |
|--|--|--|--|--|
| 50 | 6.872 | 17/30 | 3 | 0 |
| 100 | 8.609 | 17/30 | 3 | 0 |

Same 3 flips (Overtake Race, 2nd, Last) but with widening margins. Overtake Race went from +0.184 at gen 25 to +0.979 at gen 100. The vector isn't just finding the channel — it's centering itself in it. More room, less fragile.

No new flips between gen 50 and 100. The fitness is climbing (margins widening on existing flips) but no new traps are crossing. CMA-ES may be entering the refinement phase. Gen 125-150 will tell us if there's a fourth flip or if 17/30 is the ceiling for this layer/epsilon combo.

The resumed run is active with the bug fix. It should clear gen 150 and 200 without hanging.

#### What 20 Hours of Data Changes

When you run experiments overnight, you get to see things that a 4-hour session can't show you:

**Strategy succession is real.** The best strategy at hour 2 is not the best at hour 20. M1 showed mutation → tensor → temperature anneal. M2 showed random → anneal → mutation comeback. These aren't random fluctuations. They're phase transitions in the search landscape as regions get explored and exhausted. Designing for one strategy is wrong. You need a portfolio.

**Quality decay is universal.** All four machines show mean quality declining over time as novelty drains. This is correct behavior — the scorer should get harder as the pool of unseen compositions shrinks. But it means the *first few hours* of any run produce disproportionate value. Future runs should prioritize diversity of configuration over length of run.

**The monoculture pattern is fractal.** It appeared in the forge (NCD scoring → behavioral convergence), in M3 (ising BB → 97% dominance), and in the model itself (frozen posterior → reasoning suppression). Same dynamic, three scales. Wherever an optimization pressure rewards what already works, you get convergence to a single mode. The antidote is always the same: expand the measurement, add entry points, change the scoring.

**Building blocks are scaffolding, not substance.** M3 and M4 proved that BB chains win because of the bonus, not because of intrinsic quality. The topology→ising pair is real mathematics, but the scoring inflates it. When we design round 2, building blocks should be treated as seeding mechanisms (kickstart exploration in known-good regions) not as quality signals (the bonus should go away once enough data exists to judge them on merit).


### Updated Priorities for March 29

1. **Stage D gen 150-200.** Bug is fixed, run is active. This determines whether 17/30 is the ceiling or whether more flips are coming. Highest-value GPU hour in the system.

2. **Round 1 autopsy.** All four machines will finish by tonight. Query the DuckDBs. The overnight data revealed strategy succession, quality decay curves, and the BB scoring artifact — all of which inform round 2 design.

3. **Chain extension strategy.** M5 proved length-5 chains hit 0.8288. The controlled machines proved length-2 caps at ~0.73. The gap is architecture, not search. Design and implement for round 2.

4. **Compression metric redesign.** M3 proved BB chains get zero compression because they output dicts. M2 proved compression caps at 0.5 for scalar outputs. 31% of scoring weight allocated to a near-dead signal. Replace binary scalar/not-scalar with actual entropy measurement.

5. **BB bonus sunset plan.** M3's 97.2% ising dominance is a monoculture driven by the +0.10 bonus. In round 2, either remove the bonus and let BBs compete on merit, or decay it over time (high bonus initially to seed exploration, declining as data accumulates).

