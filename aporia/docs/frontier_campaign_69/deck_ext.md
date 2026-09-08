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
