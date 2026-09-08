# Frontier Practitioner deck -- extension

Prompts 70 and up: fields the original 69 did not contain.
Numbering continues from deck.md so --only works across both.
Rationale for each entry is in build_deck_ext.py::EXTRA.

---

### Prompt 70: Evolving Cellular Automata for Collective Computation

```
FRONTIER PRACTITIONER DOSSIER
Field: Evolving Cellular Automata for Collective Computation

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
Can a genetic algorithm discover a cellular automaton rule whose lattice
performs a global computation that no local rule was told how to do, and
what is the structure that actually does the computing?

Mechanism as I currently understand it:
A one-dimensional binary cellular automaton has a lookup table over
neighbourhoods of radius r, so for r = 3 the rule is a 128-bit string. Every
cell updates synchronously from its own neighbourhood and nothing else;
there is no global operation anywhere in the system. The density
classification task asks the lattice to relax to all ones if the initial
configuration had a majority of ones and to all zeros otherwise, which is a
global property of the initial condition that no cell can see. A genetic
algorithm evolves the rule table against a sample of random initial
conditions scored by whether the lattice reached the correct uniform state
within a step budget. The interesting result is not the fitness. It is that
the successful rules were found, on inspection of their space-time diagrams,
to work by forming regular domains, with the boundaries between domains
acting as travelling particles that carry information across the lattice and
interact when they collide. That particle-and-collision structure is a
description nobody encoded, in a system whose entire specification is a bit
string.

What varies and what is judged:
The candidate is the rule table itself, a bit string of length 2 to the
power of the neighbourhood size, typically 128 bits. What varies is which
bits are set. What is judged is the fraction of random initial conditions
the resulting lattice classifies correctly.

What is measured:
Classification accuracy over a sample of initial conditions, on a scale from
0 to 1, at a stated lattice size, density distribution and step budget.
Separately and more importantly, whether particles and domains can be
identified in the space-time diagrams, and by what method.

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

### Prompt 71: Unsupervised Environment Design

```
FRONTIER PRACTITIONER DOSSIER
Field: Unsupervised Environment Design

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
When an agent and the environments it trains on are optimised together, what
decides which environment to generate next, and does any such rule provably
keep producing environments the agent can still learn from rather than ones
it has already mastered or cannot touch?

Mechanism as I currently understand it:
A generator proposes environment parameters -- a maze layout, a terrain, a
set of physics constants. A student policy is trained on them. Rather than
scoring an environment by difficulty, which collapses onto the impossible,
the generator scores it by REGRET: the gap between what the student achieves
on that environment and what the best achievable policy would achieve.
Environments with high regret are ones the student is failing but could
learn, so the curriculum concentrates there. Regret is not directly
computable, so the methods differ in what they substitute for it -- the gap
between the student's return and the maximum return seen across a
population, or the positive part of the temporal-difference error. The
generator itself may be a learned adversary, or a random sampler whose
outputs are merely CURATED by a replay buffer, and the surprising empirical
result is that curation of random levels often matches or beats a learned
adversary.

What varies and what is judged:
The candidate is an environment: a parameter vector the generator emits.
What varies is the level layout or the physics settings. What is judged is
the estimated regret the student incurs on it, and downstream, whether
training on the curriculum transfers to held-out environments the generator
never produced.

What is measured:
Estimated regret per environment, on the scale of the return. Downstream,
zero-shot transfer performance on a fixed held-out set of human-designed
levels, which is the only number that is not self-referential.

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

### Prompt 72: Reservoir Computing

```
FRONTIER PRACTITIONER DOSSIER
Field: Reservoir Computing

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
Can a fixed, randomly wired dynamical system do the computational work, so
that only a linear readout has to be trained, and what property of the
system decides whether it can?

Mechanism as I currently understand it:
A reservoir is a large recurrent network whose internal weights are
generated at random and then NEVER TRAINED. The input is injected into it
and the reservoir's state evolves; the high-dimensional trajectory of that
state is recorded. The only thing fitted is a linear map from reservoir
states to the desired output, obtained in closed form by ridge regression,
so there is no backpropagation through time and no gradient anywhere. The
reservoir works because it projects the input history into a space where the
task becomes linearly separable, and it does this only if its dynamics sit
near the boundary between order and chaos -- controlled in practice by the
spectral radius of the random weight matrix. The same argument has been made
for physical substrates: buckets of water, photonic systems, memristor
arrays and random Boolean networks have all been used as reservoirs, on the
claim that the computation is a property of the dynamics rather than of any
designed circuit.

What varies and what is judged:
The candidate is the readout weights, which are the only trained object,
though what is really under test is the reservoir: its size, spectral
radius, input scaling and connection density. What is judged is prediction
error on a held-out continuation of a time series.

What is measured:
Normalised root-mean-square error on a held-out horizon, or the valid-
prediction time before the forecast diverges from a chaotic target, measured
in Lyapunov times so it is comparable across systems.

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

### Prompt 73: Unsupervised Skill Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Unsupervised Skill Discovery

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
Without any reward, can an agent discover a set of distinct, reusable
behaviours, and is the number it finds limited by the algorithm or by the
objective itself?

Mechanism as I currently understand it:
The agent learns a policy conditioned on a latent skill variable z drawn
from a fixed distribution. Training maximises the mutual information between
z and the states the policy visits, which is estimated with a learned
discriminator that tries to predict which z produced an observed state. The
policy is rewarded for reaching states that make the discriminator
confident, so different z values are pushed toward visiting distinguishable
regions. No task reward is used at any point. The standing objection is that
mutual information is maximised as soon as the skills are merely
DISTINGUISHABLE, which a set of policies that each stand still in a slightly
different spot achieves perfectly, so the objective does not by itself
demand that skills be far apart, dynamic, or useful. Later methods add an
explicit distance or Lipschitz constraint to force coverage rather than mere
separability.

What varies and what is judged:
The candidate is a skill, meaning the policy obtained by conditioning on one
value of the latent z. What varies is z. What is judged is how
distinguishable the resulting state visitation is from that of the other
skills.

What is measured:
The discriminator's log-probability of the correct skill, which is a lower
bound on the mutual information in nats. Separately, state coverage of the
reachable space, and downstream task return when the discovered skills are
frozen and used as primitives.

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

### Prompt 74: Emergent Self-Replication in Artificial Systems

```
FRONTIER PRACTITIONER DOSSIER
Field: Emergent Self-Replication in Artificial Systems

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
Can a self-replicating program arise from a soup that was never given one,
and how would you tell an actual replicator from a pattern that merely
persists?

Mechanism as I currently understand it:
A population of random instruction sequences is placed in a shared memory
and executed, usually with no fitness function and no selection imposed from
outside. Nothing rewards replication. If a sequence happens to copy itself,
its copies are also executed, so the copying is its own reward and the
population composition shifts on its own. The historical systems seeded a
hand-written ancestor and studied what evolution did to it afterwards, which
assumes away the harder question. The interesting modern claim is that
replicators arise SPONTANEOUSLY from random initial conditions in
sufficiently expressive instruction sets, given long enough, and that the
transition shows up as a sharp change in a measurable quantity such as the
entropy of the instruction distribution or the length of the longest
repeated substring in memory. The measurement problem is real: persistence,
parasitism on another sequence's copy loop, and genuine autonomous self-
copying all look similar from outside.

What varies and what is judged:
The candidate is a sequence of instructions occupying a region of shared
memory. Nothing is selected by an external scorer; what varies is what the
soup happens to contain after execution. What is judged is whether a
sequence causes copies of itself to appear.

What is measured:
The time to first replicator, in executed instructions, which is a count
with no upper bound and may be censored if none appears. Alongside it a
continuous order parameter such as the entropy of the instruction
distribution over time, whose drop is the claimed signature of the
transition.

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

### Prompt 75: Lenia and Continuous Cellular Automata

```
FRONTIER PRACTITIONER DOSSIER
Field: Lenia and Continuous Cellular Automata

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
In a continuous cellular automaton, do coherent self-maintaining patterns
exist as a matter of the update rule, and can they be searched for rather
than designed?

Mechanism as I currently understand it:
Lenia generalises Conway's Life along every axis at once: the state of a
cell is a real number rather than a bit, the neighbourhood is a smooth
radial kernel rather than eight cells, and time advances in small continuous
increments rather than discrete ticks. The update convolves the grid with
the kernel, passes the result through a smooth growth function, and adds a
fraction of it back to the current state. Because every operation is
differentiable, the whole system can be run inside an automatic
differentiation framework on a GPU. What makes it interesting is what
appears in it: localised, coherent, self-maintaining patterns that move,
rotate and sometimes interact, which persist because the rule sustains them
and were not put there. They are found by searching the space of kernel and
growth parameters, and the search is the experiment.

What varies and what is judged:
The candidate is a parameter vector: the kernel shape, the growth function's
mean and width, and the initial pattern. What varies is those parameters.
What is judged is whether the resulting pattern stays bounded and coherent
rather than dying out or filling the grid.

What is measured:
A survival or persistence measure over a fixed number of steps, plus
continuous descriptors such as the mass of the pattern, its centre of mass
displacement, and whether the mass stays within a bounded region, all on
real scales.

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

### Prompt 76: Neural Cellular Automata and Differentiable Morphogenesis

```
FRONTIER PRACTITIONER DOSSIER
Field: Neural Cellular Automata and Differentiable Morphogenesis

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
If every cell runs the same small learned rule and sees only its neighbours,
can a target global structure be grown reliably, and does the rule that
grows it also repair it when it is damaged?

Mechanism as I currently understand it:
Each cell holds a vector of channels, some of which are visible as colour
and the rest hidden. The update rule is a small neural network, identical in
every cell, that reads a fixed perception of the cell's neighbourhood --
typically the cell state together with Sobel gradients of the surrounding
field -- and outputs an increment to the cell's own state. The same rule is
applied for many steps and the resulting image is compared to a target; the
loss is backpropagated through all those steps to train the shared rule. Two
details do the real work. Updates are applied stochastically per cell, so
the rule cannot depend on global synchrony. And a pool of partially grown
states is sampled from during training, with some samples deliberately
damaged, which is what produces regeneration rather than a rule that only
works from the exact seed.

What varies and what is judged:
The candidate is the shared update rule, meaning the weights of the small
network every cell runs. What varies is those weights, trained by gradient
descent rather than searched. What is judged is how close the grown pattern
is to the target, and whether it recovers after damage.

What is measured:
Pixel-wise loss against the target after a stated number of steps, on a
continuous scale. Separately, and more informative, the loss after a region
of the grown pattern is deleted and the rule is left to run, which measures
regeneration rather than growth.

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

### Prompt 77: World Models and Learned Simulators

```
FRONTIER PRACTITIONER DOSSIER
Field: World Models and Learned Simulators

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
If an agent learns a model of its environment and then trains entirely
inside that model, when does what it learned survive contact with the real
environment, and how far into an imagined rollout can you go before the
model's errors dominate?

Mechanism as I currently understand it:
The system learns two things from logged experience. An encoder compresses
each observation into a low-dimensional latent, and a recurrent dynamics
model predicts the next latent and the reward from the current latent and
action. Once trained, the dynamics model can be rolled forward without
touching the environment at all, so a policy can be optimised on imagined
trajectories, millions of them, at no environment cost. The failure mode is
compounding error: each predicted step is slightly wrong, the error feeds
into the next prediction, and a policy optimised on long rollouts learns to
exploit places where the model is wrong rather than places where the
environment rewards it. So the rollout horizon is a bounded resource, and
the methods differ mainly in how they detect or penalise leaving the region
the model was trained on.

What varies and what is judged:
The candidate is the policy, optimised inside the learned model. What varies
is its parameters. What is judged is its return when it is finally executed
in the real environment rather than the imagined one.

What is measured:
Real-environment return after training in imagination, on the task's own
reward scale. Alongside it the model's prediction error as a function of
rollout length, which determines the usable horizon and is the number that
transfers between tasks.

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

### Prompt 78: Indirect and Generative Encodings

```
FRONTIER PRACTITIONER DOSSIER
Field: Indirect and Generative Encodings

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
When a small genome is decoded into a much larger structure by a generative
process rather than listed directly, does the regularity that decoding
imposes actually help search, and can that be separated from the advantage
of simply having fewer parameters?

Mechanism as I currently understand it:
A direct encoding stores one gene per element of the phenotype, so a
million-connection network needs a million genes. An indirect encoding
instead stores a small program or function that is queried to produce the
phenotype. In the compositional pattern producing network approach the
genome is a small network of mathematical primitives, sine and gaussian and
absolute value among them, and the phenotype is produced by querying it at
each coordinate of a geometric layout, so symmetry, repetition, and
repetition with variation fall out of the primitives used rather than having
to be discovered independently at every location. The claim is that this
bias matches the regularity of real problems and therefore helps. The
confound is that indirect encodings also have far fewer parameters, so any
advantage must be separated from ordinary dimensionality reduction, and the
standard test is a task whose regularity can be destroyed while its
difficulty is held fixed.

What varies and what is judged:
The candidate is the compact genome, meaning the small generating network.
What varies is its topology and weights. What is judged is the performance
of the large phenotype it decodes into.

What is measured:
Task performance of the decoded phenotype on the task's own scale, measured
against a direct encoding at matched evaluation budget. The decisive
comparison is the same task with its regularity scrambled, where the
indirect encoding's advantage should vanish if it is exploiting regularity
rather than compression.

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

### Prompt 79: Morphological Computation and Embodied Intelligence

```
FRONTIER PRACTITIONER DOSSIER
Field: Morphological Computation and Embodied Intelligence

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
How much of a behaviour is produced by the controller and how much by the
body, and is there a way to measure that split which does not simply relabel
one as the other?

Mechanism as I currently understand it:
The claim is that the physical structure of a body, the compliance of a
limb, the damping of a joint, the shape of a foot, performs part of the
control problem, so that a much simpler controller suffices than the same
task would need with a rigid body. The classic demonstrations are passive
dynamic walkers, which walk down a shallow slope with no actuation and no
controller at all, and compliant grippers that conform to an object without
sensing its shape. In simulation the study is usually done by co-optimising
the morphology and the controller together and comparing against a fixed
morphology with the controller optimised alone. The hard part is
attribution. A body that makes a task easy and a controller that solves it
are not separable by inspection, and the measures proposed for the split,
information-theoretic quantities computed over sensor and motor channels,
depend on where the boundary between agent and environment is drawn, which
is a modelling choice rather than a fact about the system.

What varies and what is judged:
The candidate is a body and controller pair, where both may vary. What is
judged is task performance, and separately how much the controller has to do
to achieve it.

What is measured:
Task performance on its own scale, alongside a controller complexity measure
such as the number of parameters or the information rate between sensors and
actuators in bits per step. The comparison that carries the claim is
performance at matched controller complexity across morphologies.

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

### Prompt 80: Library Learning and Program Induction

```
FRONTIER PRACTITIONER DOSSIER
Field: Library Learning and Program Induction

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
When a system invents a new primitive and adds it to its library, is that
primitive a genuine new generator or just a name for a composition it could
already express, and does anyone test which?

Mechanism as I currently understand it:
The system alternates two phases. In the wake phase it searches for programs
solving a batch of tasks, using its current library of primitives and a
learned neural policy that proposes which primitives to try. In the sleep
phase it examines the solutions it found, extracts subexpressions that recur
across them, and promotes those subexpressions to named primitives in the
library, so the next wake phase searches a space where those patterns cost
one symbol instead of many. Compression is the promotion criterion: a
candidate abstraction earns its place if adding it shortens the description
length of the solution corpus. Later systems replace the expensive search
over candidate abstractions with an exact method over e-graphs, or use a
language model to propose and name them. The step that is never separately
audited is whether a promoted primitive extends what the library can express
at all, or merely shortens something already reachable.

What varies and what is judged:
The candidate is an abstraction proposed for promotion into the library: a
subexpression recurring across solved tasks. What varies is which
subexpression. What is judged is the compression it buys over the solution
corpus, and downstream, whether tasks unsolved before become solvable after.

What is measured:
Description length of the solution corpus before and after promotion, in
symbols, and the solve rate on held-out tasks at a fixed search budget. The
measure that is NOT standard, and the one this report should hunt for, is a
leave-one-out test: remove one library primitive, enumerate the closure of
what remains more deeply, and report what fraction of the lost behaviours
never comes back.

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

### Prompt 81: Swarm Intelligence and Stigmergy

```
FRONTIER PRACTITIONER DOSSIER
Field: Swarm Intelligence and Stigmergy

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
Can a colony of agents that share no plan and no global view solve a problem
by modifying their shared environment, and is the resulting behaviour better
explained by the agents or by the trace they leave?

Mechanism as I currently understand it:
Each agent follows a simple local rule and deposits a signal into the
environment -- a pheromone on a graph edge, a marker on a grid -- which
decays over time and biases the choices of agents that arrive later. No
agent holds the solution and none communicates directly with another. In ant
colony optimisation, agents walk a graph choosing edges with probability
weighted by deposited pheromone and by a local heuristic, then reinforce the
edges of the better tours they found; evaporation is what stops early
accidents from locking the colony in. The mechanism of interest is
stigmergy: the coordination is carried entirely by modifications to the
shared medium, so the environment is doing the remembering. Particle swarm
optimisation is the continuous relative, where each particle is pulled
toward its own best position and the swarm's best, and the standing critique
is that its behaviour is dominated by the parameters controlling those two
pulls rather than by anything swarm-like.

What varies and what is judged:
The candidate is a solution constructed by one agent's walk, for instance a
tour of a graph. What varies is the path taken, which is sampled from the
pheromone field rather than chosen by any optimiser. What is judged is the
cost of that solution, which then feeds back as deposit.

What is measured:
Best and mean solution cost against a known optimum, on the problem's own
scale, as a function of evaluations. Separately, a measure of the pheromone
field itself, such as its entropy over time, which is what distinguishes a
colony that is converging from one that has stagnated.

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

### Prompt 82: Self-Organised Criticality and the Edge of Chaos

```
FRONTIER PRACTITIONER DOSSIER
Field: Self-Organised Criticality and the Edge of Chaos

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
Do systems that compute well actually sit at a critical point between order
and chaos, and is that a measured property or a story told after the fact?

Mechanism as I currently understand it:
A system is tuned by one parameter -- the fraction of ones in a cellular
automaton rule table, the spectral radius of a reservoir, the mean
connectivity of a random Boolean network -- and its dynamics change
character as that parameter is swept. At low values perturbations die out
and the system freezes; at high values they spread and the system is
chaotic; between them is a narrow region where a perturbation neither dies
nor explodes. The claim, made repeatedly since the late 1980s, is that this
region is where systems can store, transmit and combine information, and
therefore where computation is possible. It is measured by order parameters
such as the Lyapunov exponent, the size distribution of avalanches, or the
divergence rate of two initially close configurations. The history matters
as much as the claim: the original demonstration linking a specific rule-
table statistic to computational capability was challenged on the grounds
that the correlation reflected the genetic algorithm's search bias rather
than a property of the rule space, and that dispute is the most instructive
thing in the field.

What varies and what is judged:
The candidate is a system instance at a given setting of the control
parameter: one rule table, one reservoir, one network. What varies is the
control parameter. What is judged is a dynamical order parameter, and
separately whether the system can perform a computational task.

What is measured:
A dynamical order parameter on a continuous scale -- Lyapunov exponent,
avalanche size exponent, or normalised Hamming distance growth between
perturbed and unperturbed runs -- paired with task performance measured
independently, so that the correlation between them is the result rather
than the assumption.

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
