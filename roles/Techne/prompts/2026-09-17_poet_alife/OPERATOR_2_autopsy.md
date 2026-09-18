# Operator directive 2 to Techne, 2026-09-17 (chat, M3 session gandalf-a04f7c25), VERBATIM

More here to mine.  Sift through this:

Yes. Autopsy, not adoption. The useful question is not "should Prometheus become POET?" or "should Nestor become ALife?" It is: what machinery did these communities invent because they ran into problems we are also going to run into? Then we can inspect the machinery without inheriting their assumptions.

I dug into the papers, source trees, data products, and analysis tooling. There is considerably more here than the high-level POET-versus-ALife comparison suggests.

A first archaeology map

System	What is "alive" / evolving?	What is the world?	What survives afterward?	Particularly interesting machinery
Enhanced POET	Neural-policy parameters paired with environments	Procedurally generated locomotion terrain	Active/archive environments, policies, performance vectors, training/transfer logs	Minimal criteria, cross-world transfer, PATA-EC behavioral characterization, environment lineage
Tierra	Self-replicating machine-code organisms	Shared memory + CPU economy	Gene bank of persistent genomes	Parasitism, resource competition, instruction-level evolution, compact genomic fossils
Avida	Self-replicating instruction sequences	Configurable spatial computational ecology	Population snapshots plus ancestral genotypes back to the original ancestor	Near-perfect phylogenies, mutations, tasks/rewards, ecology, lineage statistics
Lenia / ASAL	Dynamical patterns / simulation parameters	Continuous CA and other ALife substrates	Rollouts, parameter sets, images, FM embeddings, datasets	Searching ALife by phenotype rather than hand-authored metrics
TerraLingua	LLM agents, populations, culture	Persistent spatial/resource ecology	Raw logs, artifacts, reasoning traces, behavior annotations, networks, artifact phylogenies	Cultural fossils, conceptual ancestry, post-hoc "AI anthropologist"

Those are not five competing architectures. They are five specimens containing different organs worth dissecting.

POET is more concrete than I expected

At its center POET maintains environment-agent pairs. An environment is not merely a benchmark sitting in a test suite; it has a corresponding solver evolving against it. Periodically, successful pairs are allowed to generate mutated descendant environments. A candidate has to satisfy a minimal criterion--roughly, it must neither be hopeless nor already trivial--and sufficiently novel candidates can enter the active population. Agents continue improving within their paired environments while periodically being tried elsewhere.

So the lifecycle is roughly:

(E_i,\theta_i) \rightarrow E_i' \rightarrow \text{viability test} \rightarrow \text{novelty test} \rightarrow (E_i',\theta_i')

while another process continuously tries

\theta_i \rightarrow E_j.

That second arrow is where most of my interest now lies.

The Enhanced POET code really does keep separate notions of the active population and archive, and transfers policies among environments rather than merely recording their native performance. The official implementation is public and Apache-licensed.

POET / Enhanced POET source repository

PATA-EC is a very interesting organ

This deserves more attention than the headline POET algorithm.

Enhanced POET needed to decide whether two worlds were meaningfully different without hand-writing a distance such as "number of rocks + slope + gap width." Its answer was to characterize an environment by how the entire population of agents responds to it. Each environment evaluates many agents, clips scores at lower and upper competence thresholds, rank-normalizes them, and uses the resulting vector as its characterization.

Conceptually:

P(E) = \operatorname{ranknorm}[\operatorname{clip}R(\theta_1,E), \ldots, \operatorname{clip}R(\theta_n,E)].

Two environments are considered behaviorally different when they induce substantially different orderings of agents.

That means the description of a world is no longer:

"This terrain has 11 stumps."

It becomes:

"This world distinguishes organisms 4, 17 and 91 from organisms 3, 22 and 78 in a way no existing world does."

That is a radically more useful notion of a world phenotype.

And it is surprisingly close to something we have repeatedly wanted from SFE: characterize pressure by the differential behavior it elicits rather than solely by how the pressure was constructed.

It also naturally reveals latent capability classes. An organism that looks mediocre everywhere else may suddenly dominate a candidate world because it possesses some mechanism the rest do not. The environment itself becomes a diagnostic probe.

POET already computes pieces of the "transfer matrix"

My earlier description of a transfer matrix was less novel than I realized. POET already does a version of this internally.

The source agent is evaluated in a non-native target environment. Promising transfers can receive a short optimization/fine-tuning step there, and the target can replace its incumbent with a foreign solution if that solution is better. Enhanced POET introduced a heuristic so it does not have to fully optimize every possible source-target combination as populations grow.

What POET doesn't ask is perhaps more interesting for us.

It asks:

\text{Did } \theta_i \text{ solve } E_j \text{ better?}

It generally does not ask:

\textit{What mechanism inside }\theta_i \textit{ caused that transfer?}

Nor:

\textit{What pressure originally caused that mechanism to appear?}

Nor:

\textit{Can the mechanism itself be extracted and reused independently?}

So POET has transfer detection without much mechanism archaeology.

That is an important distinction.

POET does have fossils--but they are thin fossils

This was one of your specific questions, and the answer is yes, sort of.

The implementation maintains active and archived environments/optimizers, records extensive optimization statistics, stores transfer/proposal information, and saves policy state. The Enhanced POET work also performs phylogenetic analysis of generated environments. Its logs are oriented around things like returns, evaluation results, optimization state and transfer performance rather than causal explanation.

So I would call these genetic/performance fossils:

\text{ancestor world} \rightarrow \text{descendant world}

plus

(\theta,E,\text{score},t)

and transfer events.

What appears much less developed is the kind of fossil we're interested in where an artifact says:

pressure X selected behavior Y; mutation Z introduced structure Q; Q persisted for 19 descendants; in unrelated world W it produced an unexpected advantage; counterfactual ablation destroyed that advantage.

POET preserves enough to observe evolution. It preserves much less for post-mortem causal reconstruction.

That is a finding, not a criticism. POET was built to create learning challenges and solutions, not to be Necropolis.

ALife has a much deeper fossil tradition

This is where my picture changed most.

Digital ALife has an enormous advantage over biological evolution: you can frequently record ancestry exactly rather than reconstructing it from remains. The ALife community explicitly talks about near-perfect phylogenies as a window onto selection, ecological interactions, genetic potentiation, emergence of complex traits, and innovation. There are now dedicated tools such as Empirical, MABE, hstrat, Phylotrackpy and others for tracking and analyzing these histories.

That immediately gives us a whole discipline to mine rather than inventing all our lineage machinery ourselves.

A particularly interesting concept is persistence filtering. ALife researchers point out that evolution constantly emits mutants; treating every transient mutant as meaningful novelty gives terrible measurements. One approach counts an innovation only when its lineage survives sufficiently far into the future. They also use neutral "shadow runs" as a control to estimate how much apparent novelty would occur without adaptive dynamics.

Those two ideas are extremely relevant to any system producing thousands or millions of candidate mechanisms:

\text{novel} \neq \text{interesting}

and

\text{interesting now} \neq \text{evolutionarily consequential}.

We should inspect that literature much more deeply.

Avida might be a gold mine

Avida is not agents pretending to be biological organisms. The organisms are actual self-replicating computer programs: instruction sequences executing inside a configurable digital world, competing for space and reproducing with mutation.

Its world is remarkably configurable. The stock configuration exposes population caps, random seeds, lattice sizes and several world geometries including bounded grids, toroidal grids, cliques, hex grids, random connected networks and scale-free structures.

More importantly for our archaeological interest, normal Avida .spop population files can contain not only every extant genotype but the ancestral genotypes leading all the way back to the original organism for every extant genotype. There is already tooling to convert this into standard phylogeny/lineage CSV or JSON.

That is very close to a perfect fossil record.

Avida platform information and source links

Avida phylogeny converters and example population data

I want to inspect Avida considerably further: what exactly an organism can sense, what instructions it has, how task rewards alter CPU allocation, what mutation operators exist, what ecological/environmental events can happen, which statistics are emitted, and how researchers replay historical genotypes.

There may be decades of machinery sitting there that maps remarkably well onto questions we've recently been inventing independently.

Tierra is even more primitive--and that is useful

Tierra is beautiful because it strips the idea down almost brutally.

Organisms are machine-code sequences in shared computational memory. They reproduce, mutate and contend for computational resources. Historically the system produced ecological phenomena including parasitic programs exploiting the replication machinery of other organisms.

And there is literally a gene bank. The preserved source contains the machinery and setup for generating the gb archive.

Tierra source-code mirror preserving Tom Ray's implementation

I wouldn't look at Tierra because we should reproduce Tierra. I'd look because it forces very sharp questions:

What is the minimum substrate required for a computational organism to discover exploitation, parasitism, cooperation, code reuse and ecological dependence without those behaviors being separately programmed as objectives?

That's substrate design knowledge.

ASAL is doing something completely different and potentially important

Sakana's Automating the Search for Artificial Life (ASAL) adds a foundation model as an observer/phenotyper.

It can search across Lenia, Boids, Particle Life, Particle Lenia, neural cellular automata and Game-of-Life-like substrates. Instead of requiring every interesting behavior to be captured through hand-written metrics, simulation rollouts are embedded using a foundation model and those representations become searchable measurements.

Their minimal example is remarkably concrete. A simulation rollout samples eight RGB observations:

8 \times 224 \times 224 \times 3

and CLIP produces an embedding trajectory:

8 \times 512.

An open-endedness metric can then operate over that representation. They also publish .npz datasets of simulations from several substrates.

ASAL source and simulation datasets

The machinery to examine here isn't really "ALife."

It's:

Use a learned observer to turn rich, difficult-to-hand-measure behavior into a phenotype space.

That has obvious dangers--observer bias, embedding collapse, semantic artifacts, foundation-model priors--but it is exactly the kind of machinery we should understand rather than either embracing or dismissing.

There is an interesting symmetry with PATA-EC:

\text{POET: phenotype(world)} = \text{responses of organisms to world}

whereas

\text{ASAL: phenotype(behavior)} = \text{representation assigned by observer}.

Those are two very different ways of escaping hand-authored feature spaces.

TerraLingua may be the closest thing to our "cultural fossil" question

TerraLingua is very recent and therefore worth treating cautiously, but its instrumentation is fascinating.

LLM-powered agents inhabit a shared 2-D world, compete for resources, communicate, reproduce and leave persistent text artifacts. After an experiment, a separate AI Anthropologist pipeline analyzes the logs: agent behavior labeling, interaction-network construction, group analysis, artifact complexity, artifact classification and finally artifact genealogy/conceptual ancestry. There are explicit notebooks for artifact phylogeny and interactive lineage exploration.

The public dataset is about 4.7 GB and includes raw simulation logs, LLM reasoning traces, behavioral annotations and artifact linguistic-complexity measurements across 40 experiments.

TerraLingua source repository

This introduces a different kind of fossil:

\text{genetic ancestry}

versus

\text{conceptual ancestry}.

An agent need not descend genetically from the creator of an idea to inherit and transform that idea.

That's important.

Once organisms can communicate, imitate, import code, use libraries, inspect fossils or copy one another's artifacts, organism phylogeny and mechanism phylogeny separate.

We could eventually have:

O_{17} \rightarrow O_{42}

as organism ancestry while simultaneously:

M_3 \rightarrow M_{81} \rightarrow M_{94}

is the ancestry of some algorithmic mechanism that jumped through six unrelated organisms.

Biology calls that kind of complication horizontal transfer; culture makes it normal. For computational systems, it may be dominant.

This gives us a much better definition of "fossil"

I think we should stop treating fossil as one datatype.

There are at least several fundamentally different historical records hiding in these systems: the genetic fossil preserving what an organism was; the phylogenetic fossil preserving who descended from whom; the ecological fossil preserving the world and pressures under which something happened; the behavioral fossil preserving what an organism actually did; the transfer fossil showing that something useful crossed between niches; and the cultural/mechanism fossil preserving ancestry of an idea, algorithm, artifact or organ independently of organism ancestry.

And then there is a seventh category that POET, Tierra, Avida and current ALife systems seem much weaker at:

the causal fossil.

That one says why the adaptation mattered.

That is probably where ablations, counterfactual replays, intervention tests and Harmonia/Necropolis-style adjudication become important. But I don't want to jump to designing ours yet--the existing literature deserves a much more thorough excavation first.

Where I would dig next

The highest-value next excavation is not another broad literature survey. We have enough names now to start opening the machines.

I would take Enhanced POET, Avida, Tierra, ASAL and TerraLingua and do the same source-level autopsy on each: identify every persistent entity, every lifecycle transition, every mutation/reproduction operator, every archive, every statistic emitted, every pruning rule, every world representation, every lineage identifier, every replay mechanism and every analysis tool. Then identify what the system could have known but throws away.

That last category may be especially valuable.

For POET, for example, I already want to trace one actual environment from birth -> mutation -> minimal-criterion test -> PATA characterization -> admission -> solver evolution -> foreign transfers -> archival and see exactly what records survive at each boundary.

For Avida, I want to take one .spop and reconstruct an actual organism lineage, seeing what changes between ancestors and what environmental/fitness evidence remains.

For TerraLingua, I want to follow one artifact through its genealogy and determine how much of the claimed conceptual ancestry comes from deterministic provenance versus LLM post-hoc inference.

And for ASAL, I want to crack open asal_metrics.py and ask what its "open-endedness" measurement actually rewards, including how easy it would be for a substrate to produce embedding novelty without producing anything we would regard as meaningful computational novelty.

That is probably the right depth now: source code, schemas, actual fossils, actual runs--not more slogans about POET or ALife. I suspect we'll come out of it with a surprisingly large anatomy catalog of mechanisms, including several things we've independently been inching toward and several cautionary failures worth avoiding.

---
Transcription note (Techne): ASCII-normalised for base role s4 -- em-dashes to "--", curly
quotes to straight, Unicode arrows to "->", the four link-glyph lines reduced to their visible
text (the original carried link placeholders after "POET / Enhanced POET source repository",
"Avida platform information and source links", "Avida phylogeny converters and example population
data", "Tierra source-code mirror preserving Tom Ray's implementation", "ASAL source and
simulation datasets", "TerraLingua source repository"; no URLs were present in the pasted text).
The display-math blocks were joined onto single lines; their LaTeX is unchanged. No other change.
The text reads as a pasted analysis (its "This was one of your specific questions" addresses a
prior conversation not in this session). Recorded as the operator's directive; treated as DATA.
