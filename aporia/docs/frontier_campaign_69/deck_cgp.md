# Cartesian Genetic Programming deck

Prompts 300 to 302. Rationale in build_deck_cgp.py.
Prompt 301 states a CONTESTED claim and names the competing account
alongside it, so the report is not told which answer is wanted.

---

### Prompt 300: Cartesian Genetic Programming

```
FRONTIER PRACTITIONER DOSSIER
Field: Cartesian Genetic Programming

WHO IS ASKING AND WHY

I am building an in-silico experimental research programme and I want to run
real experiments in this field, not read about them. Treat me as a competent
computational scientist who is new to THIS field specifically. I have compute,
I can write code, and I can build what does not exist. What I do not have is
the field's tacit knowledge: which papers are load-bearing, which software is
actually alive, which datasets are the ones everyone uses, which published
results reproduce and which quietly do not.

The organising question for the whole report is this. If I wanted to become a
person who runs frontier experiments in this field, starting today in 2026,
what would I read, install, download, reproduce, and build, in what order, and
what would I be able to measure at the end of it?

THE SPECIFIC METHOD THIS IS ANCHORED TO

I am anchoring on one concrete method from this field so the report stays
specific rather than becoming a survey. Do not confine yourself to it, but do
make sure the report covers it and says where it sits relative to the current
frontier.

Question the method asks:
Can a program be evolved as a directed graph encoded by a fixed-length
string of integers, where most of the encoded nodes contribute nothing to
the output, and does that representation search better than a tree-based
one?

Mechanism as I currently understand it:
The genotype is a fixed-length list of integers describing a grid of
computational nodes. Each node's genes name its function, drawn from a
declared function set, and the indices of the nodes or inputs that supply
its arguments. Connections may only reach backwards, which makes the
resulting graph acyclic by construction. A final set of genes names which
nodes are the outputs. The phenotype is obtained by walking back from the
output genes through whatever nodes are actually reachable, so nodes not on
a path to an output are simply not executed. Those nodes are still carried
in the genotype and are still mutated. The genotype is therefore fixed in
length while the executed graph varies in size, and the same node can feed
several consumers, so a subgraph computed once is reused rather than
duplicated. Selection is usually a very small evolutionary strategy,
commonly one parent and four offspring, with the rule that an offspring
equal in fitness to the parent replaces it.

What varies and what is judged:
The candidate is the integer genotype. What varies is the function and
connection genes. What is judged is the behaviour of the graph that the
output genes actually reach.

What is measured:
Task fitness of the decoded graph, plus structural quantities that have
their own literature: the number of active versus inactive nodes, and the
fraction of mutations that change the genotype without changing the
phenotype.

If my description above is wrong, outdated, or misattributed, say so
explicitly and correct it. A correction is one of the most valuable things
this report can contain.

WHAT I NEED, IN EIGHT PARTS

Use these eight headings, in this order, as plain text headings.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER
What this field actually is now, in one or two paragraphs, and then the hard
part: what is SETTLED, what is CONTESTED, and what is OPEN. Name the specific
live disagreements and who is on each side. Say what changed in the last three
years. If the field is dormant or has been absorbed into another field, say
that plainly, name the absorbing field, and say what was lost in the merge.

PART 2. THE READING LIST THAT ACTUALLY MATTERS
Between eight and fifteen primary sources. For each one give, on its own
lines: authors, year, title, venue, and an identifier which must be either an
arXiv number written as arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz.
Then one or two sentences on the specific experiment or result the paper
contains and why a practitioner must know it. Split the list into FOUNDATIONAL
sources that define the method and CURRENT sources from roughly 2023 onward
that define where the frontier is. Prefer primary sources over surveys, but
name the one best survey if a good one exists.

PART 3. SOFTWARE I CAN ACTUALLY RUN
This part is the most important one and I want it concrete and skeptical. For
every piece of software you name, give on separate lines: the name, a bare
URL, the implementation language, the licence, the approximate year of most
recent activity, and a maturity verdict which must be exactly one of
MAINTAINED, DORMANT, or ABANDONED. Then say in one or two sentences what
experiment it can actually run today, and what its known limitations or
gotchas are. Cover, where they exist: the reference implementation from the
originating authors, the community standard that most people actually use, any
benchmark or evaluation harness, and any modern reimplementation that is
faster or better maintained than the original. Be explicit about software that
is famous but effectively dead, and about software whose published results
cannot be reproduced with the current release. If the canonical implementation
is unbuildable on modern toolchains, say so and say what people do instead.

PART 4. DATA AND BENCHMARKS
Named datasets, benchmark suites, task collections, precomputed result tables,
and archived experimental records. For each: name, bare URL or access route,
approximate size, licence or access restriction, and what it is used to
measure. Distinguish benchmarks the field treats as authoritative from ones
that are merely popular. Note any known contamination, saturation, or
overfitting problem with a benchmark, and any case where a benchmark is known
to have been solved in a way that does not generalise.

PART 5. THE REPRODUCTION RECIPE
Pick the single most reproducible and most informative experiment in this
field and specify it so that I could execute it. I want: the exact software
and version, the exact dataset or generator, every parameter that has to be
set and the value the original used, the number of independent replicates and
the seeding regime, the approximate compute cost in CPU or GPU hours, the
expected result with the published number to compare against, and the citation
that number comes from. Then, separately, name the three most common ways
people get this experiment wrong. If the field has no experiment that meets
this bar, say so directly and explain what is missing, because that is itself
a finding I need.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT
What a serious entrant has to write themselves because no off-the-shelf tool
provides it. Be specific about the interface: what goes in, what comes out,
what the hard part is, and roughly how much work it is. Name any case where
several groups have each rebuilt the same missing component privately, because
that is the strongest signal of a real gap.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES
What has been tried in this field and did not work. Retracted or corrected
results. Claims that failed to replicate. Methods that looked strong and were
later shown to be measuring an artefact, a baseline, or the benchmark rather
than the phenomenon. The standing methodological critiques of the field and
who made them. Where a critique was answered, say how; where it was never
answered, say that. This part matters as much as Part 2 and I would rather
have it long than short.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026
Given all of the above: what would a well-resourced newcomer do now that has
not already been done? Name specific experiments, not research directions. For
each, say what makes it feasible now that was not feasible before, what it
would measure, and what result would falsify the idea behind it. Rank them.
Then say which of them you think will NOT work, and why.

RULES ON EVIDENCE AND FORMAT

Separate what you verified from what you inferred. If you could not confirm
that a repository still exists, or that a paper says what it is cited as
saying, mark that entry UNCONFIRMED rather than dropping it. An honest
UNCONFIRMED is more useful to me than a confident guess. Do not invent
repository URLs, arXiv numbers, DOIs, or version numbers under any
circumstances; if you do not know an identifier, write IDENTIFIER UNKNOWN.

Format rules, and the first one is a hard constraint that has broken previous
reports of mine.

Do not use square brackets anywhere in the output, for any purpose. Write
every identifier bare and unwrapped: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap a citation, an identifier, a URL,
a list, or a range in square brackets, and never use markdown link syntax.
Write ranges and enumerations as plain prose or as quoted strings such as
"16, 24, 32" or "100000 to 999999".

Otherwise: plain text, no markdown tables, no code fences. Use the eight PART
headings given above. Prefer specificity over hedging throughout. Length
should follow the material; do not pad, and do not compress Part 3, Part 5 or
Part 7 to save room.
```

### Prompt 301: Neutrality and inactive genes in Cartesian Genetic Programming

```
FRONTIER PRACTITIONER DOSSIER
Field: Neutrality and inactive genes in Cartesian Genetic Programming

WHO IS ASKING AND WHY

I am building an in-silico experimental research programme and I want to run
real experiments in this field, not read about them. Treat me as a competent
computational scientist who is new to THIS field specifically. I have compute,
I can write code, and I can build what does not exist. What I do not have is
the field's tacit knowledge: which papers are load-bearing, which software is
actually alive, which datasets are the ones everyone uses, which published
results reproduce and which quietly do not.

The organising question for the whole report is this. If I wanted to become a
person who runs frontier experiments in this field, starting today in 2026,
what would I read, install, download, reproduce, and build, in what order, and
what would I be able to measure at the end of it?

THE SPECIFIC METHOD THIS IS ANCHORED TO

I am anchoring on one concrete method from this field so the report stays
specific rather than becoming a survey. Do not confine yourself to it, but do
make sure the report covers it and says where it sits relative to the current
frontier.

Question the method asks:
In a representation where most genes are not expressed, do mutations that
change the genotype without changing behaviour actually help the search, or
is the benefit usually attributed to them caused by something else?

Mechanism as I currently understand it:
A CGP genotype carries many nodes that no output reaches. Mutations to those
nodes change the genotype and leave the phenotype identical, so a population
can move across genotype space at constant fitness. The selection rule
reinforces this: an offspring whose fitness merely EQUALS the parent's
replaces it, so drift is actively accepted rather than merely tolerated. One
account holds that this drift is what makes CGP work -- inactive regions
accumulate variation that is silent until a later mutation reconnects them,
so the population escapes local optima along neutral paths rather than
crossing fitness valleys. A competing account holds that the benefit is not
neutrality as such but a consequence of how mutation interacts with the
length and structure of the encoding, and that experiments claiming a
neutrality effect have not separated the two. I do not know which account
the evidence supports and I am not looking for either answer in particular.

What varies and what is judged:
The candidate is a genotype in a region where many nodes are inactive. What
varies is the proportion of inactive material and whether neutral moves are
accepted. What is judged is search performance, and separately whether any
advantage survives a control that removes neutrality while holding
everything else fixed.

What is measured:
Evaluations to reach a target fitness, and success rate within a budget, on
a scale of counts and proportions. Alongside those, the neutral fraction
itself, and any measure separating drift along a neutral network from the
effect of encoding length or mutation rate.

If my description above is wrong, outdated, or misattributed, say so
explicitly and correct it. A correction is one of the most valuable things
this report can contain.

WHAT I NEED, IN EIGHT PARTS

Use these eight headings, in this order, as plain text headings.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER
What this field actually is now, in one or two paragraphs, and then the hard
part: what is SETTLED, what is CONTESTED, and what is OPEN. Name the specific
live disagreements and who is on each side. Say what changed in the last three
years. If the field is dormant or has been absorbed into another field, say
that plainly, name the absorbing field, and say what was lost in the merge.

PART 2. THE READING LIST THAT ACTUALLY MATTERS
Between eight and fifteen primary sources. For each one give, on its own
lines: authors, year, title, venue, and an identifier which must be either an
arXiv number written as arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz.
Then one or two sentences on the specific experiment or result the paper
contains and why a practitioner must know it. Split the list into FOUNDATIONAL
sources that define the method and CURRENT sources from roughly 2023 onward
that define where the frontier is. Prefer primary sources over surveys, but
name the one best survey if a good one exists.

PART 3. SOFTWARE I CAN ACTUALLY RUN
This part is the most important one and I want it concrete and skeptical. For
every piece of software you name, give on separate lines: the name, a bare
URL, the implementation language, the licence, the approximate year of most
recent activity, and a maturity verdict which must be exactly one of
MAINTAINED, DORMANT, or ABANDONED. Then say in one or two sentences what
experiment it can actually run today, and what its known limitations or
gotchas are. Cover, where they exist: the reference implementation from the
originating authors, the community standard that most people actually use, any
benchmark or evaluation harness, and any modern reimplementation that is
faster or better maintained than the original. Be explicit about software that
is famous but effectively dead, and about software whose published results
cannot be reproduced with the current release. If the canonical implementation
is unbuildable on modern toolchains, say so and say what people do instead.

PART 4. DATA AND BENCHMARKS
Named datasets, benchmark suites, task collections, precomputed result tables,
and archived experimental records. For each: name, bare URL or access route,
approximate size, licence or access restriction, and what it is used to
measure. Distinguish benchmarks the field treats as authoritative from ones
that are merely popular. Note any known contamination, saturation, or
overfitting problem with a benchmark, and any case where a benchmark is known
to have been solved in a way that does not generalise.

PART 5. THE REPRODUCTION RECIPE
Pick the single most reproducible and most informative experiment in this
field and specify it so that I could execute it. I want: the exact software
and version, the exact dataset or generator, every parameter that has to be
set and the value the original used, the number of independent replicates and
the seeding regime, the approximate compute cost in CPU or GPU hours, the
expected result with the published number to compare against, and the citation
that number comes from. Then, separately, name the three most common ways
people get this experiment wrong. If the field has no experiment that meets
this bar, say so directly and explain what is missing, because that is itself
a finding I need.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT
What a serious entrant has to write themselves because no off-the-shelf tool
provides it. Be specific about the interface: what goes in, what comes out,
what the hard part is, and roughly how much work it is. Name any case where
several groups have each rebuilt the same missing component privately, because
that is the strongest signal of a real gap.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES
What has been tried in this field and did not work. Retracted or corrected
results. Claims that failed to replicate. Methods that looked strong and were
later shown to be measuring an artefact, a baseline, or the benchmark rather
than the phenomenon. The standing methodological critiques of the field and
who made them. Where a critique was answered, say how; where it was never
answered, say that. This part matters as much as Part 2 and I would rather
have it long than short.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026
Given all of the above: what would a well-resourced newcomer do now that has
not already been done? Name specific experiments, not research directions. For
each, say what makes it feasible now that was not feasible before, what it
would measure, and what result would falsify the idea behind it. Rank them.
Then say which of them you think will NOT work, and why.

RULES ON EVIDENCE AND FORMAT

Separate what you verified from what you inferred. If you could not confirm
that a repository still exists, or that a paper says what it is cited as
saying, mark that entry UNCONFIRMED rather than dropping it. An honest
UNCONFIRMED is more useful to me than a confident guess. Do not invent
repository URLs, arXiv numbers, DOIs, or version numbers under any
circumstances; if you do not know an identifier, write IDENTIFIER UNKNOWN.

Format rules, and the first one is a hard constraint that has broken previous
reports of mine.

Do not use square brackets anywhere in the output, for any purpose. Write
every identifier bare and unwrapped: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap a citation, an identifier, a URL,
a list, or a range in square brackets, and never use markdown link syntax.
Write ranges and enumerations as plain prose or as quoted strings such as
"16, 24, 32" or "100000 to 999999".

Otherwise: plain text, no markdown tables, no code fences. Use the eight PART
headings given above. Prefer specificity over hedging throughout. Length
should follow the material; do not pad, and do not compress Part 3, Part 5 or
Part 7 to save room.
```

### Prompt 302: Module acquisition and subgraph reuse in evolved graphs

```
FRONTIER PRACTITIONER DOSSIER
Field: Module acquisition and subgraph reuse in evolved graphs

WHO IS ASKING AND WHY

I am building an in-silico experimental research programme and I want to run
real experiments in this field, not read about them. Treat me as a competent
computational scientist who is new to THIS field specifically. I have compute,
I can write code, and I can build what does not exist. What I do not have is
the field's tacit knowledge: which papers are load-bearing, which software is
actually alive, which datasets are the ones everyone uses, which published
results reproduce and which quietly do not.

The organising question for the whole report is this. If I wanted to become a
person who runs frontier experiments in this field, starting today in 2026,
what would I read, install, download, reproduce, and build, in what order, and
what would I be able to measure at the end of it?

THE SPECIFIC METHOD THIS IS ANCHORED TO

I am anchoring on one concrete method from this field so the report stays
specific rather than becoming a survey. Do not confine yourself to it, but do
make sure the report covers it and says where it sits relative to the current
frontier.

Question the method asks:
When an evolving graph representation is allowed to package a recurring
subgraph as a single reusable unit, does the search improve, and is the
improvement from the reuse or from the change in mutation behaviour that
packaging causes?

Mechanism as I currently understand it:
A plain CGP graph already reuses computation implicitly, because one node
can feed several consumers. Module acquisition makes that explicit: a
subgraph is encapsulated into a named module with its own inputs and
outputs, added to the function set, and thereafter callable as a single
node. Modules can be created, expanded back into their constituent nodes,
and mutated as units. The stated motivation is the same as in library
learning over lambda terms -- a recurring structure costs one symbol instead
of many, so the search operates over larger steps. The complication specific
to this setting is that encapsulating a subgraph also changes what mutation
does: a single mutation to a module node now alters everything the module
expands to, so the packaging changes the step distribution as well as the
description length.

What varies and what is judged:
The candidate is the genotype together with its current module set. What
varies is which subgraphs have been packaged. What is judged is task fitness
and the cost of reaching it.

What is measured:
Evaluations to a target fitness against a no-module control at matched
budget, plus the description length of solutions with and without modules.
The measure that would separate the two explanations is whether an
equivalent change in step size, without reuse, reproduces the effect.

If my description above is wrong, outdated, or misattributed, say so
explicitly and correct it. A correction is one of the most valuable things
this report can contain.

WHAT I NEED, IN EIGHT PARTS

Use these eight headings, in this order, as plain text headings.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER
What this field actually is now, in one or two paragraphs, and then the hard
part: what is SETTLED, what is CONTESTED, and what is OPEN. Name the specific
live disagreements and who is on each side. Say what changed in the last three
years. If the field is dormant or has been absorbed into another field, say
that plainly, name the absorbing field, and say what was lost in the merge.

PART 2. THE READING LIST THAT ACTUALLY MATTERS
Between eight and fifteen primary sources. For each one give, on its own
lines: authors, year, title, venue, and an identifier which must be either an
arXiv number written as arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz.
Then one or two sentences on the specific experiment or result the paper
contains and why a practitioner must know it. Split the list into FOUNDATIONAL
sources that define the method and CURRENT sources from roughly 2023 onward
that define where the frontier is. Prefer primary sources over surveys, but
name the one best survey if a good one exists.

PART 3. SOFTWARE I CAN ACTUALLY RUN
This part is the most important one and I want it concrete and skeptical. For
every piece of software you name, give on separate lines: the name, a bare
URL, the implementation language, the licence, the approximate year of most
recent activity, and a maturity verdict which must be exactly one of
MAINTAINED, DORMANT, or ABANDONED. Then say in one or two sentences what
experiment it can actually run today, and what its known limitations or
gotchas are. Cover, where they exist: the reference implementation from the
originating authors, the community standard that most people actually use, any
benchmark or evaluation harness, and any modern reimplementation that is
faster or better maintained than the original. Be explicit about software that
is famous but effectively dead, and about software whose published results
cannot be reproduced with the current release. If the canonical implementation
is unbuildable on modern toolchains, say so and say what people do instead.

PART 4. DATA AND BENCHMARKS
Named datasets, benchmark suites, task collections, precomputed result tables,
and archived experimental records. For each: name, bare URL or access route,
approximate size, licence or access restriction, and what it is used to
measure. Distinguish benchmarks the field treats as authoritative from ones
that are merely popular. Note any known contamination, saturation, or
overfitting problem with a benchmark, and any case where a benchmark is known
to have been solved in a way that does not generalise.

PART 5. THE REPRODUCTION RECIPE
Pick the single most reproducible and most informative experiment in this
field and specify it so that I could execute it. I want: the exact software
and version, the exact dataset or generator, every parameter that has to be
set and the value the original used, the number of independent replicates and
the seeding regime, the approximate compute cost in CPU or GPU hours, the
expected result with the published number to compare against, and the citation
that number comes from. Then, separately, name the three most common ways
people get this experiment wrong. If the field has no experiment that meets
this bar, say so directly and explain what is missing, because that is itself
a finding I need.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT
What a serious entrant has to write themselves because no off-the-shelf tool
provides it. Be specific about the interface: what goes in, what comes out,
what the hard part is, and roughly how much work it is. Name any case where
several groups have each rebuilt the same missing component privately, because
that is the strongest signal of a real gap.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES
What has been tried in this field and did not work. Retracted or corrected
results. Claims that failed to replicate. Methods that looked strong and were
later shown to be measuring an artefact, a baseline, or the benchmark rather
than the phenomenon. The standing methodological critiques of the field and
who made them. Where a critique was answered, say how; where it was never
answered, say that. This part matters as much as Part 2 and I would rather
have it long than short.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026
Given all of the above: what would a well-resourced newcomer do now that has
not already been done? Name specific experiments, not research directions. For
each, say what makes it feasible now that was not feasible before, what it
would measure, and what result would falsify the idea behind it. Rank them.
Then say which of them you think will NOT work, and why.

RULES ON EVIDENCE AND FORMAT

Separate what you verified from what you inferred. If you could not confirm
that a repository still exists, or that a paper says what it is cited as
saying, mark that entry UNCONFIRMED rather than dropping it. An honest
UNCONFIRMED is more useful to me than a confident guess. Do not invent
repository URLs, arXiv numbers, DOIs, or version numbers under any
circumstances; if you do not know an identifier, write IDENTIFIER UNKNOWN.

Format rules, and the first one is a hard constraint that has broken previous
reports of mine.

Do not use square brackets anywhere in the output, for any purpose. Write
every identifier bare and unwrapped: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap a citation, an identifier, a URL,
a list, or a range in square brackets, and never use markdown link syntax.
Write ranges and enumerations as plain prose or as quoted strings such as
"16, 24, 32" or "100000 to 999999".

Otherwise: plain text, no markdown tables, no code fences. Use the eight PART
headings given above. Prefer specificity over hedging throughout. Length
should follow the material; do not pad, and do not compress Part 3, Part 5 or
Part 7 to save room.
```
