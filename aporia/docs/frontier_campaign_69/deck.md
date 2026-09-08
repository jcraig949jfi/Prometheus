# Frontier Practitioner deck -- 69 fields

Aporia campaign opened 2026-09-07. Built by build_deck.py from
Herakles MATRIX.json. One prompt per field, fired in waves of three.
Firing order and its rationale live in build_deck.py::ORDER.

---

### Prompt 1: Digital Evolution

```
FRONTIER PRACTITIONER DOSSIER
Field: Digital Evolution

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
Does a particular sequence of machine instructions, run on a small virtual
computer, actually compute a specified logic function of its inputs?

Mechanism as I currently understand it:
An Avidian is a circular sequence of instructions executed by a virtual CPU
with a handful of registers, two stacks, and instruction pointers called
heads. Some instructions do arithmetic and bit operations; others move
heads, allocate memory and divide; a set of no-operation instructions act as
modifiers that change which register the preceding instruction touches,
which is what makes the language robust to point mutation. Input
instructions pull numbers from the environment and output instructions push
a result back. The environment watches the outputs, and when an output
equals a designated logic function of recent inputs, such as NOT of one
input or the EQUALS of two, it credits the organism with a merit multiplier,
which buys more CPU cycles per update, which lets it replicate faster. That
is the entire coupling between computation and fitness. In the 2003
experiment the point was that EQU, which needs five NAND operations to
build, only ever appeared in populations where the simpler intermediate
functions were also rewarded: the stepping stones were required.

What varies and what is judged:
The instruction sequence, the genome. What is judged is the outputs it emits
given the inputs the environment supplies.

What is measured:
For the single-genotype question, whether the target function was performed,
and on how many input cases it was performed correctly. The natural
continuous version is the fraction of input pairs answered correctly,
between zero and one.

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

### Prompt 2: Quality-Diversity (MAP-Elites)

```
FRONTIER PRACTITIONER DOSSIER
Field: Quality-Diversity (MAP-Elites)

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
Instead of hunting for the single best solution, can a search fill in a map
of the best solution of every different kind, and does that map turn out to
be more useful than the single best?

Mechanism as I currently understand it:
Choose a few features that describe what a solution DOES rather than how
good it is, and lay them out as a grid of cells. Evaluate some random
solutions, and file each one in the cell its behaviour falls into. Then
repeat a simple loop: pick an occupant of the grid at random, mutate it,
evaluate the child, work out which cell the child belongs in, and if that
cell is empty or its occupant is worse, the child takes the cell. Because
parents come from all over the grid rather than from the current best, the
search keeps stepping stones that a fitness-only search would throw away.
The output is not one solution but the whole filled grid, reported as
coverage, how many cells are occupied, and as the summed quality of the
occupants.

What varies and what is judged:
An individual solution, judged twice over, once on quality and once on where
its behaviour puts it in the grid. The grid as a whole is the real product.

What is measured:
Coverage, a count or fraction of occupied cells, and the summed fitness of
occupants, both aggregates over the whole run, plus the archive itself as a
structured artifact.

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

### Prompt 3: Open-Ended Evolution

```
FRONTIER PRACTITIONER DOSSIER
Field: Open-Ended Evolution

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
Where does a neural-network-controlled agent end up in a maze after a fixed
number of steps, when nothing in the run tells it where it is supposed to
go?

Mechanism as I currently understand it:
A fixed-topology neural controller with bounded weights reads range-sensor
and heading inputs and drives a simulated robot through a two-dimensional
maze with walls, for a fixed number of timesteps. The behaviour
characterisation is the robot's final coordinate, deliberately ignoring
everything about how it got there. In the full method that endpoint is what
a novelty archive stores and compares; this template isolates only the
evaluation half, the function that turns a genome into a behaviour, which is
the piece that has to be correct before novelty search means anything.

What varies and what is judged:
The controller's weight vector. It is judged only by where the robot stops,
not by whether it reached the goal, which is the whole methodological point.

What is measured:
A two-dimensional endpoint coordinate on a continuous scale, plus steps
consumed and, incidentally, whether the goal was reached.

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

### Prompt 4: Artificial Life (ALife)

```
FRONTIER PRACTITIONER DOSSIER
Field: Artificial Life (ALife)

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
Can a hand-written program, running in a shared block of computer memory,
copy itself successfully? This is the sanity check you run before turning
mutation on and seeing what evolves.

Mechanism as I currently understand it:
Reserve a large block of memory, the soup. Write one ancestor program in a
machine language designed so that most random edits still produce something
that runs: no numeric operands, and addressing by matching templates of no-
operation instructions rather than by absolute address, so the code survives
being moved. The ancestor's body is a loop that measures its own length by
locating its start and end templates, requests a fresh block of memory from
the operating system, copies itself instruction by instruction into that
block, and issues a divide instruction that hands the daughter block its own
instruction pointer and slice of CPU time. A scheduler round-robins CPU time
across all living creatures. A reaper kills creatures when memory fills,
preferring the old and the error-prone. That combination, self-copy plus
finite memory plus a reaper, is what turns replication rate into a selection
pressure. In the full experiment a mutation operator flips bits in the soup
and during copying, and parasites appear that lack a copy loop and execute
their neighbours' instead.

What varies and what is judged:
The ancestor program, a sequence of instructions. What varies is the
instruction sequence and the machine language it is written in.

What is measured:
For the baseline question, a fact: did the ancestor produce at least one
viable daughter, and does the population sustain itself. Scalar proxies are
population count at cycle N, generations elapsed, or fraction of soup
occupied. All are continuous or count-valued and all require the simulation
to have run to completion.

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

### Prompt 5: Novelty Search

```
FRONTIER PRACTITIONER DOSSIER
Field: Novelty Search

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
If a search is rewarded only for doing something no previous attempt has
done, and is never told what the goal is, can it still reach goals that
defeat a search aimed straight at them?

Mechanism as I currently understand it:
Throw the objective away. Describe each individual by what it does, as a
point in a behaviour space. Keep a growing archive of behaviours seen so
far. Score an individual by its average distance to its k nearest neighbours
among the current population and the archive; that number is its novelty,
and it is the only selection pressure. Individuals novel enough get added to
the archive, so the archive densifies the regions already explored and the
pressure automatically moves elsewhere. The claim is that on deceptive
problems, where the gradient of the objective points away from the solution,
divergence reaches the solution while convergence does not, because the
solution is simply one of the behaviours a diverging search eventually
tries.

What varies and what is judged:
An individual, judged not on its own merits at all but on its distance from
everything that came before. Novelty is not a property of the candidate; it
is a property of the candidate together with the archive.

What is measured:
Terminal novelty and archive size, both continuous or count valued, and
separately, and only as a post-hoc check, whether the goal was reached and
after how many evaluations.

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

### Prompt 6: POET / Open-Ended Learning

```
FRONTIER PRACTITIONER DOSSIER
Field: POET / Open-Ended Learning

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
If you let the problems and the problem-solvers improve each other,
generating new challenges from ones already solved and letting solutions
move between challenges, do you end up solving harder problems than you
could by attacking any one of them directly?

Mechanism as I currently understand it:
Keep a population of environment-and-agent pairs. Each environment is
described by parameters, canonically the roughness, gaps and obstacles of a
two-dimensional terrain; each agent is a neural controller optimised on its
own environment by an evolution strategy. Periodically, mutate the
parameters of environments already being solved to produce candidate new
environments, and admit a candidate only if it passes a minimal criterion:
not so easy that current agents already solve it, not so hard that none can
make progress. That criterion is what keeps the frontier moving instead of
exploding. Periodically also attempt TRANSFER: take every agent in the
population, evaluate it on every other environment, and if some other
environment's agent does better than the incumbent, replace the incumbent.
Transfer is the load-bearing part of the argument, because it means a skill
learned on one challenge becomes a stepping stone for a different challenge
that direct optimisation could not reach.

What varies and what is judged:
Both populations at once. Agents are judged by score on environments;
environments are judged by the minimal criterion, which is a judgement about
what the current agents can and cannot do.

What is measured:
The claim the template picks out is a comparison: final score with transfer
enabled against final score for direct optimisation on the same environment.
Both continuous. The open-endedness claim is not a scalar at all and cannot
be made one.

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

### Prompt 7: Coevolution

```
FRONTIER PRACTITIONER DOSSIER
Field: Coevolution

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
Does making the test cases evolve against the solutions, instead of holding
them fixed, keep a search from getting stuck on a local optimum?

Mechanism as I currently understand it:
Two populations are maintained at once. Hosts are candidate solutions, in
Hillis's case sorting networks. Parasites are sets of test cases, in that
case lists to be sorted. Host fitness is how many of the co-located
parasite's cases it handles correctly; parasite fitness is how many it makes
the host fail. Both populations reproduce with variation on a spatial grid,
so a host that is good only against the currently common cases is
immediately punished when the parasites shift. The difficulty of the test
set is therefore a moving function of current host competence, which is what
prevents the search from converging on a static benchmark it has memorised.

What varies and what is judged:
Two candidates at once, and that is the point. The host varies in its
solution structure; the parasite varies in which test cases it presents.
Each is judged only against the other, so neither has an absolute fitness.

What is measured:
Host performance over generations, and in the honest version the quality of
the final host against an independent held-out test set rather than against
the surviving parasites. The scale is a fraction of test cases passed.

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

### Prompt 8: Evolutionary Developmental Systems (Evo-Devo)

```
FRONTIER PRACTITIONER DOSSIER
Field: Evolutionary Developmental Systems (Evo-Devo)

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
When a developmental process turns a genotype into a body plan, are all body
plans equally easy to produce, or does the process itself, before any
selection happens, make some outcomes far more common than others?

Mechanism as I currently understand it:
Build a network of N nodes, each holding an on or off state. Wire each node
to exactly K inputs drawn from the other nodes and give it a Boolean
function of those inputs, in the classical construction by drawing the truth
table at random. Set an initial state, the genotype. Update every node
synchronously according to its function and its inputs' current states.
Because the state space is finite and the update deterministic, the
trajectory must eventually repeat, so it falls into a cyclic attractor. That
attractor is the phenotype. Now the measurement: sample many genotypes,
develop each one, and tabulate how often each attractor comes up. The basin
sizes are wildly unequal, so a few phenotypes absorb most genotypes. That
inequality is developmental bias, and it exists with no selection anywhere
in the procedure. At K equal to 2 the ensemble sits at the critical boundary
between the frozen and chaotic regimes, which is why the template pins K to
2.

What varies and what is judged:
The genotype, here the initial state or the wiring; the phenotype is the
attractor it reaches. What is judged is the frequency with which each
phenotype appears.

What is measured:
The frequency of the most common phenotype, a proportion between zero and
one, or equivalently the entropy of the phenotype distribution. Both are
scalars, but both require MANY developmental runs to estimate, which matters
for the routes below.

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

### Prompt 9: Artificial Gene Regulatory Networks

```
FRONTIER PRACTITIONER DOSSIER
Field: Artificial Gene Regulatory Networks

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
If you wire up a network of on-off switches at random and let it update
itself, does it settle into a short repeating cycle or wander for a very
long time, and what decides which?

Mechanism as I currently understand it:
Build N nodes. Give each node K randomly chosen input nodes and a randomly
chosen Boolean function of those K inputs, drawn from the 2 to the power 2
to the K possible functions. Set a random initial state of N bits. Update
every node simultaneously from the current state, repeatedly. Because the
state space is finite and the update is deterministic, the trajectory must
eventually revisit a state, and from then on it repeats. Record the number
of steps before the first revisit, the transient, and the length of the
repeating cycle, the attractor period. Sweeping K reveals a phase
transition: at K equal to 1 the dynamics are frozen, at K equal to 2 they
are critical, and at K of 3 or more they are chaotic with attractor lengths
growing rapidly in N.

What varies and what is judged:
One randomly constructed network together with one initial state. What
varies is the wiring, the function table, the initial state, the node count
and the in-degree. What is judged is the period of the cycle it falls into.

What is measured:
Attractor period, a positive integer, transient length, a non-negative
integer, and whether a cycle was detected within the budget, a boolean.
Period is the natural scalar for the outcome rule.

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

### Prompt 10: Symbolic Regression

```
FRONTIER PRACTITIONER DOSSIER
Field: Symbolic Regression

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
Can an evolving population of mathematical expressions find a formula that
fits a dataset, and does the evolution actually do better than drawing the
same number of random formulas?

Mechanism as I currently understand it:
Represent each candidate as a tree over a declared function set and terminal
set. Evaluate each tree on a set of fitness cases, that is input-output
pairs, and take fitness to be the total error. Select parents in proportion
to fitness, typically by tournament. Produce children by subtree crossover,
which swaps a randomly chosen subtree between two parents, and by mutation,
which replaces a subtree with a fresh random one. Replace the population and
repeat for a number of generations, stopping when a tree's error falls below
a hit criterion. Depth limits bound the trees and are the usual defence
against bloat.

What varies and what is judged:
An expression tree. What varies is the tree's structure and its constants.
What is judged is prediction error on the fitness cases.

What is measured:
Best-of-run error, continuous and non-negative, the generation at which the
hit occurred, and the size of the winning tree. Error is the natural scalar
and is already bounded to 0 to 1 if normalised.

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

### Prompt 11: Equation Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Equation Discovery

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
Given a measured trajectory of a system, can you recover the small handful
of terms that actually govern its motion, out of a large library of terms
that might?

Mechanism as I currently understand it:
Measure the state over time and estimate its time derivative numerically.
Build a library matrix whose columns are candidate functions of the state,
typically polynomials up to some order plus trigonometric terms. The
governing equation is then written as derivative equals library times a
coefficient vector. Solve that overdetermined system by least squares, then
zero every coefficient whose magnitude falls below a sparsity threshold,
then refit least squares on the surviving columns only, and iterate. The
procedure converges to a sparse coefficient vector whose nonzero entries
name the active terms, and that is the discovered equation.

What varies and what is judged:
The coefficient vector over the library, that is the model. What varies is
which library terms survive thresholding. What is judged is the residual
error together with the number of nonzero terms.

What is measured:
Residual error, from 0 upward, and the count of nonzero coefficients, a
small integer. Only one of the two can be the outcome rule's scalar, which
is itself a faithful reflection of the method's real difficulty.

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

### Prompt 12: Genetic Programming

```
FRONTIER PRACTITIONER DOSSIER
Field: Genetic Programming

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
In a randomly generated linear program, what fraction of the instructions
actually affect the output, and how does that fraction depend on how many
registers the program has?

Mechanism as I currently understand it:
A linear genetic program is a straight-line sequence of register
instructions, each writing a destination register from an operation on
source registers. Effective code is found by walking the instruction list
BACKWARD from the end. Start with the output register in a live set. For
each instruction from last to first, if its destination register is
currently live, mark the instruction effective and add its source registers
to the live set; otherwise mark it a structural intron, because nothing it
writes is ever read on any path to the output. The intron fraction that
falls out is a property of the program's structure alone, computed with no
execution and no fitness, and it is the baseline against which selection-
driven bloat is later measured.

What varies and what is judged:
A single randomly drawn program genome, given here directly as a uniform
bitstring of the declared length. What varies is the random draw and the
register count. What is judged is the structural effectiveness of the
decoded instruction sequence.

What is measured:
The fraction of instructions that are effective, continuous from 0 to 1, and
whether at least one effective path to the output register exists, a
boolean. Both are exact, deterministic functions of the seed and the two
axes.

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

### Prompt 13: AI Scientist systems

```
FRONTIER PRACTITIONER DOSSIER
Field: AI Scientist systems

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
Can a language model take a working machine-learning training script, write
a modification to it, and have that modification actually run and reach a
target validation loss?

Mechanism as I currently understand it:
Start from a small working codebase and its known baseline numbers. A
language model brainstorms a research idea against that codebase, checks the
idea against a literature search for prior art, then a coding agent edits
the source files to implement it. The edited code is executed under a fixed
compute budget; if it crashes, the error text is fed back and the agent gets
a bounded number of repair attempts. Numbers that survive are collected into
plots and a write-up, which a second language model then scores. The loop is
generate, edit, execute, observe, repair, report.

What varies and what is judged:
The model-authored code diff, and behind it the idea it encodes. What varies
is which idea is attempted; what is judged is whether the diff executes at
all and what validation loss the modified script reaches.

What is measured:
Two things in the real method, which is already a problem for this bench: a
boolean execution outcome and a continuous validation loss. The literature
also reports a reviewer score on an ordinal scale.

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

### Prompt 14: Causal Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Causal Discovery

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
Given only observational measurements of several variables, and no
experiments, which pairs of variables could possibly be directly connected?
The method rules connections out rather than establishing them.

Mechanism as I currently understand it:
Start with the complete undirected graph, every pair joined. Then delete
edges. For each remaining pair, test whether the two variables are
independent given some set of the others, and test with conditioning sets in
increasing order of size: first the empty set, which is plain marginal
independence, then all single conditioning variables drawn from the
neighbours of either endpoint, then all pairs, and so on up to the allowed
maximum. The moment a conditioning set is found that makes the pair
independent at the chosen significance level, delete that edge and record
the separating set. When no more edges can be removed, the surviving graph
is the skeleton. Orientation is a separate later phase that uses the
recorded separating sets to find colliders and then propagates; this
template stops before that. The whole method rests on assumptions the data
cannot check: causal sufficiency, meaning no unmeasured common causes, plus
faithfulness and the Markov condition.

What varies and what is judged:
The edge set, which starts complete and shrinks. What is judged is which
edges survive.

What is measured:
The template asks for skeleton density, edges retained over edges possible,
continuous between zero and one. Better statistics exist when a ground truth
graph is available: structural Hamming distance to the true skeleton, or
precision and recall over edges. All scalar.

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

### Prompt 15: Bayesian Experimental Design

```
FRONTIER PRACTITIONER DOSSIER
Field: Bayesian Experimental Design

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
Before collecting any data at all, how much would a planned study of a given
size be expected to teach us, and is that enough to be worth doing?

Mechanism as I currently understand it:
Write down what you already believe as a prior distribution over the unknown
parameters, and write down how data would be generated from those parameters
as a likelihood. For a candidate design, such as a sample size or a set of
measurement points, imagine every dataset the design could produce, weighted
by how likely each is under your current beliefs. For each imagined dataset
compute the posterior you would end up with and measure how far it has moved
from the prior, in the Shannon sense. Average that movement over all
imagined datasets. The average is the expected information gain, which is
the design's utility. Under a conjugate normal model this integral is closed
form; otherwise it is estimated by nested Monte Carlo. No data is ever
collected.

What varies and what is judged:
A proposed design, here parameterised by sample size, judged by its expected
utility. Nothing is fitted and nothing is observed.

What is measured:
Expected information gain, a non-negative continuous quantity in nats or
bits, one number per design.

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

### Prompt 16: Optimal Experimental Design

```
FRONTIER PRACTITIONER DOSSIER
Field: Optimal Experimental Design

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
Given that you can only afford a fixed number of measurements, where should
you put them so that the model you intend to fit comes out as sharply
determined as possible?

Mechanism as I currently understand it:
Fix a model, for example a polynomial of a chosen degree, and fix the region
over which measurements may be taken. A design is a specific list of
measurement locations. Build the model matrix whose rows are the model's
basis functions evaluated at those locations, and form the information
matrix as its transpose times itself. The volume of the resulting confidence
ellipsoid for the fitted coefficients shrinks as the determinant of that
matrix grows, so the determinant, usually scaled by the number of parameters
and expressed as an efficiency between zero and one, is the design's score.
Exchange algorithms improve a design by repeatedly swapping one measurement
location for another and keeping the swap if the determinant rises.

What varies and what is judged:
An exact design, that is, a particular set of n measurement locations. It is
judged by the determinant of its information matrix, or equivalently by its
D-efficiency relative to the theoretical continuous optimum.

What is measured:
The determinant of the information matrix, or the D-efficiency in the range
zero to one; a single continuous number per design.

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

### Prompt 17: Active Learning

```
FRONTIER PRACTITIONER DOSSIER
Field: Active Learning

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
If labelling data is expensive, does letting the learner choose which
examples to have labelled beat labelling examples at random, and by how
much?

Mechanism as I currently understand it:
Keep the set of all hypotheses still consistent with the labels seen so far,
the version space. Draw a committee of several hypotheses from it at random.
Show the committee each unlabelled candidate and see how much they disagree
about it. A candidate everyone agrees on teaches nothing, because its label
is already determined; a candidate that splits the committee roughly in half
is worth the most, because whichever way its label falls, about half the
surviving hypotheses are eliminated. Query the label of the most-disagreed-
about candidate, add it, shrink the version space, resample the committee,
and repeat until the budget is gone. The theoretical result is that because
each query carries roughly constant information, generalisation error falls
exponentially in the number of queries rather than polynomially.

What varies and what is judged:
A query, that is, a choice of which point to have labelled. What varies is
the selection policy; what is judged is the error, or here the
identification, achieved per unit of label budget.

What is measured:
Generalisation error as a function of the number of queries spent, a
continuous curve, compared against the same curve for random selection.

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

### Prompt 18: Neural Architecture Search

```
FRONTIER PRACTITIONER DOSSIER
Field: Neural Architecture Search

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
Given a fixed number of tries, does a smarter search strategy find a better
neural network design than simply guessing at random?

Mechanism as I currently understand it:
Training neural networks to compare architectures is prohibitively
expensive, so the benchmark pre-computes the answer once. A constrained
space of small architectures is enumerated exhaustively, each one is trained
several times to fixed epoch budgets, and the resulting accuracies and
training times are stored in a table. After that, evaluating an architecture
is a table lookup, so a search algorithm can be run thousands of times and
its variability measured honestly. The search itself is the object of study.
Random search draws architectures uniformly. Regularized evolution keeps a
fixed-size population, repeatedly samples a small tournament, mutates the
best member of the tournament, adds the child, and removes the OLDEST member
rather than the worst, which is the regularization: it prevents a lucky
early architecture from dominating forever and keeps the population turning
over. Both algorithms are charged the same query budget, and the comparison
is between best-found accuracy at equal budget, over many independent
repetitions.

What varies and what is judged:
An architecture, an encoded cell graph. What is judged is the best accuracy
the search found within its budget, not any single architecture.

What is measured:
Best validation accuracy found within budget, continuous, and properly the
regret against the table's known global optimum, since the optimum is known
by exhaustive enumeration.

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

### Prompt 19: Meta-Learning

```
FRONTIER PRACTITIONER DOSSIER
Field: Meta-Learning

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
Can a model's starting parameters be trained in such a way that a handful of
gradient steps on a brand new task is enough to do that task well?

Mechanism as I currently understand it:
Two nested loops. In the inner loop, a task is sampled, a few labelled
examples from it are used to take a small number of gradient steps from the
current initialisation, producing task specific parameters, and the loss of
those parameters is measured on held out examples of the same task. In the
outer loop, that post adaptation loss is differentiated with respect to the
original initialisation, which involves a second derivative term or a first
order approximation of it, and the initialisation is updated. Repeat over
many batches of tasks. At meta test time an unseen task is sampled, the same
few inner steps are taken from the learned initialisation, and accuracy is
reported. The point is that nothing about the model architecture is special;
only the initialisation is meta-learned, which is where the model-agnostic
name comes from.

What varies and what is judged:
The initialisation, judged by post adaptation performance on tasks it has
never seen.

What is measured:
Post adaptation accuracy or mean squared error on held out query sets,
continuous, averaged over many test tasks and reported with a confidence
interval because the variance across tasks is large.

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

### Prompt 20: Learning-to-Optimize

```
FRONTIER PRACTITIONER DOSSIER
Field: Learning-to-Optimize

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
Instead of writing an optimisation algorithm by hand, can you train one, and
if you can, does it still work on problems unlike the ones it was trained
on?

Mechanism as I currently understand it:
There are two nested loops. The inner loop optimises an ordinary function:
at each step the current parameters produce a loss and a gradient. Instead
of applying a hand-written update such as gradient descent, the gradient is
fed into a small recurrent network which outputs the update, and the same
network is applied independently to every coordinate so it can scale to any
dimension. The outer loop trains that network. It unrolls the inner loop for
a fixed number of steps, sums the inner losses along the trajectory to form
a meta-loss, and backpropagates through the unrolled trajectory into the
network's weights, treating the incoming gradient as a constant input to
avoid second derivatives. The smallest characteristic instance trains on
random ten-dimensional quadratic objectives and then tests on fresh ones.

What varies and what is judged:
The update rule itself. What varies is the learned optimiser's weights; what
is judged is the loss it drives its optimisee to within a fixed number of
steps.

What is measured:
Final or summed inner loss after a fixed step count, continuous, compared
against hand-written baselines such as SGD, momentum, RMSprop and Adam on
the same problems.

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

### Prompt 21: Population-Based Training

```
FRONTIER PRACTITIONER DOSSIER
Field: Population-Based Training

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
Instead of choosing one learning rate and living with it, can a group of
models being trained side by side discover, on the fly, a whole SCHEDULE of
settings that changes as training proceeds?

Mechanism as I currently understand it:
Train a population of models in parallel, each with its own hyperparameters.
Every fixed number of steps, evaluate all of them. In the exploit step, a
poorly performing worker abandons its own run and copies both the weights
and the hyperparameters of a well-performing worker. In the explore step it
then perturbs the copied hyperparameters. Training resumes from the copied
weights, not from scratch, which is what makes the method cheap and what
makes its product a schedule: following one surviving worker's ancestry
backwards yields a sequence of hyperparameter values indexed by training
step, and that sequence typically beats any constant setting. Total compute
is the same as running the population independently.

What varies and what is judged:
A worker, that is, the pair of a weight vector and a hyperparameter vector.
It is judged by its validation performance at each checkpoint, and a poor
judgement causes it to be overwritten rather than merely down-weighted.

What is measured:
Best validation metric against step or wall-clock budget, continuous, and
the discovered schedule, which is a time series rather than a number.

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

### Prompt 22: Machine Evolution

```
FRONTIER PRACTITIONER DOSSIER
Field: Machine Evolution

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
How well does the simplest possible neural network controller, with almost
no structure in it, perform on a control task? This is the starting line
against which everything a structure-growing evolutionary method later adds
has to be compared.

Mechanism as I currently understand it:
A network is described by two gene lists, one of nodes and one of
connections, with each connection gene carrying a source, a target, a
weight, an enable flag and a historical marking. To evaluate one network,
build it from the genes, then run an episode: at each timestep read the
task's state variables into the input nodes, propagate activations through
the network, read the output nodes, apply that as the control signal, and
step the task's dynamics forward. Continue until the task fails or the time
limit is reached. Fitness is a function of the episode, typically how long
the system was kept within bounds. The wider method around this evaluation
is where NEAT lives: start every network minimal and fully connected input
to output with no hidden nodes, mutate weights and occasionally add a node
or a connection, use the historical markings to align genomes so that
crossover between different topologies is meaningful, and protect new
structure inside species so that a mutation that adds a node is not killed
before it has time to be optimised. This template deliberately runs only the
evaluation and none of the method.

What varies and what is judged:
One network genome. What varies is its topology and its connection weights;
what is judged is the episode it produces.

What is measured:
Episode length before failure, or a normalised version of it, a continuous
scalar. In the non-Markovian variants it is averaged over several starting
states, which already requires aggregation.

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

### Prompt 23: Illumination Algorithms

```
FRONTIER PRACTITIONER DOSSIER
Field: Illumination Algorithms

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
Instead of asking what is the single best solution, can a search return a
whole map showing the best solution of every distinct kind, and how much of
that map can it actually fill?

Mechanism as I currently understand it:
Choose a small number of descriptive features that characterise how a
solution behaves rather than how well it scores, and cut that behaviour
space into a grid of bins. Keep an archive holding at most one solution per
bin, the best found so far for that bin. Repeat: draw a solution at random
from the archive, mutate it, evaluate it to get both a performance score and
a behaviour descriptor, find the bin the descriptor falls in, and place the
new solution there if the bin is empty or if it beats the incumbent. The
output is the entire archive, summarised as coverage, the fraction of bins
filled, and as a quality-diversity score summing performance over filled
bins. Because elites in one bin are the parents of solutions in other bins,
an archive acts as a set of stepping stones and can reach places that direct
optimisation cannot.

What varies and what is judged:
A genome. It is judged on two channels at once, a scalar performance and a
behaviour descriptor vector, and the second channel decides where it is
allowed to compete.

What is measured:
Coverage, the fraction of bins filled, between zero and one; the quality-
diversity score; and the maximum performance found. Coverage is the one the
outcome rule would use.

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

### Prompt 24: Autocurricula

```
FRONTIER PRACTITIONER DOSSIER
Field: Autocurricula

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
When two teams of agents compete in a physical world with no designed task,
do they generate their own escalating sequence of challenges, and do
genuinely new strategies appear that nobody put in?

Mechanism as I currently understand it:
Two teams, hiders and seekers, are placed in a physics sandbox containing
movable boxes and ramps. The only reward is the hide-and-seek outcome. Both
teams are trained by self-play reinforcement learning against each other.
Because each team's improvement raises the difficulty facing the other, the
task never stabilises, and training passes through a sequence of discrete
strategy regimes: seekers chase, hiders build shelters, seekers use ramps to
get in, hiders lock the ramps away, and so on. The curriculum is generated
by the competition rather than by a designer, which is what makes it an
autocurriculum.

What varies and what is judged:
Two team policies, each judged only against the current version of the
other. What varies is the learned behaviour on each side.

What is measured:
The number and timing of distinct strategy regimes over training, and per-
regime team performance. Regime count is a small integer, but identifying a
regime boundary is a change-point judgement over a long time series.

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

### Prompt 25: Curiosity-Driven Exploration

```
FRONTIER PRACTITIONER DOSSIER
Field: Curiosity-Driven Exploration

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
In an environment too large to count visits to individual states, can a
learned density model stand in for a visit counter well enough to tell an
agent which parts of the world it has not really seen?

Mechanism as I currently understand it:
A sequential density model is fit online over observed states. For a state
just seen, the model gives a probability before the update and a probability
after being trained on that one observation. The increase, called the
prediction gain, is large for a state the model finds surprising and small
for one it already expects. From those two probabilities a pseudo-count is
derived algebraically, and it behaves like an empirical visit count while
being defined for states never visited. An exploration bonus proportional to
one over the square root of the pseudo-count is added to the reward, and the
agent's policy then pursues that bonus, which is what drives it into
unvisited regions.

What varies and what is judged:
The agent's policy, judged by where it goes. What varies is the density
model class and the bonus scale, and downstream of those, the states the
agent chooses to visit.

What is measured:
State coverage and extrinsic return over training, plus the agreement
between pseudo-counts and true counts where true counts happen to be known.
Coverage is a count, return is unbounded, agreement is a ratio.

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

### Prompt 26: Intrinsic Motivation

```
FRONTIER PRACTITIONER DOSSIER
Field: Intrinsic Motivation

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
If a learning agent is given no goal at all, and instead simply chooses
whatever activity it is currently getting better at fastest, will it teach
itself a sensible sequence of skills, starting easy and moving to hard
entirely on its own?

Mechanism as I currently understand it:
The agent acts, and after each action tries to predict what its sensors will
read next. It keeps the prediction errors. It carves its sensorimotor space
into regions, splitting a region in two whenever the data inside become
heterogeneous enough that two child regions predict better than the parent.
For each region it keeps a recent history of prediction error and computes
LEARNING PROGRESS, the rate at which that error is falling, which is a
derivative over time and not the error itself. It then chooses its next
action mostly from whichever region has the highest learning progress, with
some random exploration mixed in. The consequence is a self-organised
curriculum: a region already mastered has near-zero error and therefore
near-zero progress, so the agent leaves it; a region that is pure noise has
high error but also near-zero progress, because the error never falls, so
the agent leaves that too. Using progress rather than error is precisely
what stops the agent being captured by unpredictable noise.

What varies and what is judged:
The agent's behaviour policy, which changes continuously. What is judged is
the sequence of activities the agent chose, not any single action.

What is measured:
In the real work, the time-ordered sequence of which region the agent
selected, compared against the regions' true difficulty. Scalar reductions
exist but are lossy: rank correlation between selection time and difficulty,
or fraction of a run spent in the unlearnable region.

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

### Prompt 27: Artificial Curiosity

```
FRONTIER PRACTITIONER DOSSIER
Field: Artificial Curiosity

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
If an agent is rewarded for surprising itself, does it seek out the parts of
its world it does not yet understand, and does it lose interest once it has
learned them?

Mechanism as I currently understand it:
Two networks share a world. A model network watches the current state and
the action taken and tries to predict the next state; it is trained to
reduce its own prediction error. A controller network chooses actions and is
rewarded by exactly that prediction error, so it is trained to increase it.
The two are in direct opposition. The consequence is a moving target: a
region that is initially surprising pulls the controller toward it, the
model learns that region, the error falls, and the controller leaves. That
departure is boredom, and it falls out of the arithmetic rather than being
programmed. The known failure is a region whose unpredictability is
irreducible, such as pure noise, where the model can never reduce error and
the controller never leaves.

What varies and what is judged:
The controller, judged by where in the world it spends its time and whether
that allocation tracks the model's residual error.

What is measured:
Prediction error over time, on a continuous scale, and the controller's
occupancy over regions, as a distribution. The claim lives in the coupling
between the two, not in either one alone.

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

### Prompt 28: Empowerment

```
FRONTIER PRACTITIONER DOSSIER
Field: Empowerment

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
Can an agent decide what to do using nothing but a measure of how much
control it has over its own future, with no goal given to it from outside?

Mechanism as I currently understand it:
Treat the agent's actuators as the input to a communication channel and the
future state of the world as its output. Fix a state and a horizon of h
steps. Consider every action sequence of length h. Each sequence induces a
distribution over the state h steps later. The channel capacity of that
mapping, the maximum over distributions on action sequences of the mutual
information between the sequence and the resulting state, is the empowerment
of the state, measured in bits. It is computed by an iterative algorithm of
the Blahut-Arimoto family. High empowerment means many distinguishable
futures are reachable. An agent with no goal can then simply climb the
empowerment landscape, and in many worlds this reproduces sensible behaviour
such as staying near the centre of a room or keeping a pole balanced.

What varies and what is judged:
A state of the world, judged by how many distinguishable futures the agent
can steer itself into from there.

What is measured:
A single non-negative real number of bits per state, bounded above by the
horizon times the actuator bits. In practice a landscape of that number over
many states.

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

### Prompt 29: Minimal-Criterion Coevolution

```
FRONTIER PRACTITIONER DOSSIER
Field: Minimal-Criterion Coevolution

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
Can two coupled populations keep generating new problems and new solutions
indefinitely when the only rule for staying alive is solve at least one and
be solved by at least one, with nothing ever ranked as better than anything
else?

Mechanism as I currently understand it:
Two populations reproduce with mutation, solvers and environments. A child
solver survives if it satisfies its minimal criterion, solving at least one
environment currently in the environment population. A child environment
survives if at least one solver in the current solver population solves it.
Nothing is scored and nothing is ranked. Because an environment must remain
solvable to persist and a solver must have something to solve, the two
populations drag each other along a moving frontier of just-reachable
difficulty, and structural complexity accumulates without any objective ever
being specified. The coupling is the algorithm; remove either half and it
collapses to random drift.

What varies and what is judged:
Two candidates, symmetrically. A solver is judged by whether any environment
yields to it; an environment is judged by whether any solver cracks it.
Neither receives a score, only a binary existential verdict.

What is measured:
Population sizes over generations as integers, the number of surviving
solver-environment pairs, and structural statistics of the environments that
persist. The primary reading is whether both counts stay positive over a
long horizon.

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

### Prompt 30: ALife-Inspired AI

```
FRONTIER PRACTITIONER DOSSIER
Field: ALife-Inspired AI

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
If you put one hand-written self-copying program into a block of computer
memory and let copying make occasional mistakes, does an ecology appear on
its own, including creatures that live off other creatures?

Mechanism as I currently understand it:
A region of virtual memory, the soup, is seeded with a single ancestor
written in a purpose-built machine code, roughly eighty instructions long,
whose whole job is to measure itself, allocate space and copy itself into
it. A scheduler gives each running creature slices of CPU time. Errors are
injected in two places, as background bit flips in the soup and as mistakes
during copying. When memory fills, a reaper queue kills the oldest and the
most error-prone creatures to make room. Nothing selects for anything in
particular: the only currencies are memory space and CPU time, so whatever
copies itself faster in the space available takes over. What is observed is
that shorter creatures appear which have lost the copy loop and instead
execute a neighbour's copy code, that is, parasites; then hosts that resist
them; then hyper-parasites; then creatures that cheat cooperative
arrangements.

What varies and what is judged:
A creature, that is, a contiguous block of executable instructions with its
own instruction pointer. What varies is its length and its exact instruction
sequence. It is judged by nothing external: it is judged by whether copies
of it are still in memory later.

What is measured:
A time series rather than a scalar: the histogram of creature lengths over
time, the number of distinct genotypes, the lineage tree, and the appearance
time of the first creature that cannot replicate in isolation, which is the
operational definition of a parasite.

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

### Prompt 31: Artificial Chemistry

```
FRONTIER PRACTITIONER DOSSIER
Field: Artificial Chemistry

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
When two elementary lambda-calculus combinators are applied to one another,
does the resulting expression settle into a stable final form within a
bounded number of rewriting steps, or does it keep rewriting forever?

Mechanism as I currently understand it:
In Fontana's algorithmic chemistry, molecules are lambda terms and a
chemical reaction is a collision. Pick two terms A and B from a reactor,
form the application of A to B, then beta-reduce that application under a
fixed reduction strategy, counting steps. If a normal form is reached before
the step ceiling, the normal form is the product and it is injected back
into the reactor, displacing a randomly chosen term. If the ceiling is hit
first, the collision is declared elastic and nothing is produced. Iterating
collisions over a well-stirred population is what eventually yields self-
maintaining organizations; the single collision is the atomic event
underneath all of that.

What varies and what is judged:
The ordered pair of combinators, left operand and right operand, drawn from
I, K and S, together with the reduction budget. What is judged is whether
that specific application halts and what term it halts on.

What is measured:
A halting boolean, an integer count of reduction steps consumed, and a term-
valued product. Steps are on a bounded integer scale; the product is
symbolic and not a number at all.

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

### Prompt 32: Autocatalytic Sets

```
FRONTIER PRACTITIONER DOSSIER
Field: Autocatalytic Sets

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
In a randomly generated soup of molecules and reactions, at what level of
catalytic connectivity does a self-sustaining, self-catalysing subnetwork
first appear, and how does that level change as the soup gets bigger?

Mechanism as I currently understand it:
Build a binary polymer model. Molecules are bit strings up to max_length;
reactions are ligation, joining two molecules, and cleavage, splitting one.
The shortest molecules form a food set assumed to be freely available. Each
molecule-reaction pair is independently made catalytic with probability
catalysis_prob. Then run the RAF algorithm, which is a prune to a fixed
point: repeatedly delete any reaction that is not catalysed by a molecule
currently in the set, or whose reactants cannot be built from the food set
using only the remaining reactions, and iterate until nothing more can be
deleted. Whatever remains, if anything, is reflexively autocatalytic and
food-generated. The field's headline result is that the catalysis
probability needed for a RAF to appear grows only slowly with system size
rather than exponentially.

What varies and what is judged:
The whole reaction network. What is judged is a SUBSET of it, the maximal
RAF, and it is found by deletion to a fixed point rather than by any search
over candidates.

What is measured:
RAF present or absent as a boolean, and RAF size as an integer or as a
fraction of the network. Swept over catalysis_prob it produces a
percolation-like curve with a threshold, and the threshold's location is the
actual result.

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

### Prompt 33: Darwinian Neurodynamics

```
FRONTIER PRACTITIONER DOSSIER
Field: Darwinian Neurodynamics

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
Can a population of small brain-like networks actually run Darwinian
evolution, with copying, variation and inheritance, and does doing so find
solutions faster than merely trying variants at random?

Mechanism as I currently understand it:
A population of attractor networks of the Hopfield kind. Each network stores
patterns as attractors, and those patterns are candidate solutions. A
network is relaxed from a noisy starting state and settles into a pattern,
which is a variant. The variants produced across the population are scored
against a fitness function, the best are selected, and the selected patterns
are then used to retrain the networks by a Hebbian rule, which installs them
as new attractors. That retraining step is the heredity channel: the
offspring network inherits the parents' attractor landscape rather than a
copied string. Iterate over generations. The decisive comparison is against
a purely selectionist control, which keeps selection but severs the heredity
channel, and against random search.

What varies and what is judged:
At the lower level a binary pattern generated by relaxation; at the upper
level the network itself, judged by the fitness of the patterns it
generates.

What is measured:
Best and mean fitness over generations, and time to reach the target. The
reported quantity is a difference between arms over a trajectory, not a
point, which matters for how it can be adjudicated.

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

### Prompt 34: Artificial General Intelligence (AGI)

```
FRONTIER PRACTITIONER DOSSIER
Field: Artificial General Intelligence (AGI)

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
Can an agent that knows nothing about the rules of its environment learn to
act well in it, purely by compressing its own past stream of actions and
observations and then simulating possible futures from that compressed
model?

Mechanism as I currently understand it:
The agent runs a closed loop with an environment. At each cycle it emits an
action symbol and receives an observation and a reward symbol. The whole
history of that stream is fed to a Context Tree Weighting model, which is a
Bayesian mixture over all variable order Markov predictors up to a fixed
context depth, so the agent does not have to choose a model order. To pick
the next action it runs a Monte Carlo tree search, rho-UCT, in which the
rollouts are sampled from the CTW mixture itself rather than from a known
simulator, out to a finite horizon. It executes the best action, observes
what happens, updates the mixture, and repeats for thousands of cycles.
Performance is read as average reward per cycle rising over experience, on
toy partially observable domains such as a biased coin flip, tiger, a small
grid world, tic tac toe and Kuhn poker.

What varies and what is judged:
The agent itself, more precisely its policy at a given amount of accumulated
experience. What is judged is the reward it collects. What varies between
agents is the context tree depth, the search horizon and the simulation
budget per move.

What is measured:
Average reward per cycle, continuous, usually rescaled so that the random
policy is 0 and the optimal policy is 1. Secondary numbers are model size
and time per decision.

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

### Prompt 35: Counterexample-Guided Inductive Synthesis

```
FRONTIER PRACTITIONER DOSSIER
Field: Counterexample-Guided Inductive Synthesis

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
Can a synthesis loop that repeatedly proposes a program and gets back one
concrete failing input find a correct program before it runs out of
attempts, and how does that depend on how big the space of programs is?

Mechanism as I currently understand it:
The programmer writes a sketch, a program with holes. The synthesizer solves
an inductive query: find hole values that make the program correct on the
current finite set of concrete example inputs. That candidate goes to a
verifier, typically a SAT or SMT solver, which checks it against the full
specification over all inputs. If verification fails the verifier returns a
concrete counterexample input, which is added to the example set, and the
loop repeats with a strictly harder inductive query. The loop ends when
verification succeeds or the iteration budget is exhausted. The essential
property is that each failure permanently narrows the next proposal, so the
example set is a monotone accumulation of hardness.

What varies and what is judged:
The completed program, that is the vector of hole values. It is judged by a
verifier that returns a verdict and a witness, not by a graded score.

What is measured:
Solved or not solved as a boolean, iterations consumed as an integer, and
the size and composition of the accumulated counterexample set.

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

### Prompt 36: Program Synthesis

```
FRONTIER PRACTITIONER DOSSIER
Field: Program Synthesis

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
If a programmer writes a program with holes in it plus a statement of what
the program should do, can a solver fill in the holes so that the result is
correct, and how much work does that take?

Mechanism as I currently understand it:
Sketching. The programmer writes a partial program in which unknown
constants or expressions are left as holes, and supplies a specification,
often a slow reference implementation. The sketch and the spec are compiled
into a constraint over the hole values, bounded in input size and loop
unrolling so the constraint is finite. Then counterexample guided inductive
synthesis runs a loop: a SAT or SMT solver proposes hole values that work on
the current finite set of test inputs; a verifier searches for an input on
which the candidate and the spec disagree; if it finds one, that
counterexample is added to the set and the loop repeats; if it cannot, the
completed program is returned. The iteration cap bounds that loop, and
sketch size measures how much was left unspecified.

What varies and what is judged:
The hole assignment, that is, the completed program. It is judged by whether
it satisfies the bounded specification.

What is measured:
A solved or unsolved boolean, plus iterations consumed and wall clock time.
The boolean is the verdict and the time is the continuous statistic; they
are different quantities and the template should not conflate them.

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

### Prompt 37: Counterexample-Guided Verification

```
FRONTIER PRACTITIONER DOSSIER
Field: Counterexample-Guided Verification

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
Can you prove a property about a system too big to check directly, by
checking a deliberately blurred version of it and sharpening the blur only
where the blur lies to you?

Mechanism as I currently understand it:
Build a coarse abstraction of the system that keeps every real behaviour and
also admits some fake ones, so it over-approximates. Ask a model checker
whether the property holds on the abstraction. If yes, it holds on the real
system too and you are done. If no, the checker hands back a counterexample
trace. Replay that trace on the concrete system. If it reproduces, the bug
is real and you are done. If it does not, it was an artifact of the
blurring, and the trace tells you WHICH distinction the abstraction
discarded; you add that distinction back, refine, and loop. The loop
terminates because each refinement strictly splits the abstract state space.

What varies and what is judged:
The abstraction. What varies is which distinctions it keeps; what is judged
is whether it is precise enough to settle the property.

What is measured:
In the real method, a three-way outcome, property proven, real bug found, or
refine again, together with the number of refinement rounds and the final
abstraction size.

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

### Prompt 38: Formal Methods

```
FRONTIER PRACTITIONER DOSSIER
Field: Formal Methods

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
Within a fixed number of steps, can a system reach a state that violates its
safety property, and if it can, what exactly is the sequence of steps that
gets there?

Mechanism as I currently understand it:
Take an initial-state predicate, a transition relation and a safety
property. Unroll the transition relation k times into a single propositional
formula whose satisfying assignments are exactly the length-k executions
that end in a violating state. Hand that formula to a SAT solver. A
satisfying assignment decodes into a concrete counterexample trace.
Unsatisfiable means no violation exists at any length up to k, which is a
genuine proof but only within the bound; nothing is claimed at step k plus
one unless a separate k-induction check also succeeds. The method's whole
selling point is that it replaces a fixed-point computation over the state
space with a single, exhaustive, bounded query.

What varies and what is judged:
The candidate is a trace, a length-k execution, and it is found or shown not
to exist by the solver rather than proposed by the experimenter. What the
experimenter chooses is the model and the bound.

What is measured:
Satisfiable or unsatisfiable as a boolean, solver time, formula size, and on
satisfiable, the length and content of the counterexample trace.

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

### Prompt 39: Automated Theorem Proving

```
FRONTIER PRACTITIONER DOSSIER
Field: Automated Theorem Proving

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
Can a first-order theorem prover derive a contradiction from a set of
clauses within a fixed budget of generated clauses, and does changing the
heuristic that picks what to work on next change whether it gets there?

Mechanism as I currently understand it:
Negate the conjecture and clausify everything into a flat set of clauses.
Then saturate: repeatedly select one clause from the unprocessed set, which
is the given-clause choice and is exactly where the heuristic lives, compute
all superposition, resolution and paramodulation inferences between it and
the already-processed set, simplify and subsume the results, and put the
survivors back into the unprocessed set. Stop when the empty clause appears,
which is a refutation and hence a proof, or when the clause or time budget
is exhausted, which proves nothing. Every inference rule is sound, so the
heuristic can only change cost, never correctness, and that is why the field
measures heuristics by budget consumption.

What varies and what is judged:
The search strategy and its clause-selection heuristic. What varies across
runs is the order in which the same sound inference rules are applied, not
the logic and not the problem.

What is measured:
Refuted or not as a boolean, clauses generated and processed as integers,
and wall time. The primary scale is a bounded integer count, and comparisons
are only meaningful at a fixed budget.

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

### Prompt 40: Proof Search

```
FRONTIER PRACTITIONER DOSSIER
Field: Proof Search

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
Can a language model trained on mathematical proofs suggest the next step
well enough that a machine, checking every suggestion against a strict
logical kernel, closes proofs it could not close by guessing?

Mechanism as I currently understand it:
A formal proof assistant holds a goal and a library of previously proved
statements, and can check whether a proposed step is legal. A transformer,
trained on a corpus of formal proofs, is shown an open goal and samples
candidate next steps. A best-first search keeps a frontier of open goals,
repeatedly picks the most promising one according to a learned value
estimate, samples proposals for it, submits each to the kernel, discards the
illegal ones and adds the resulting subgoals to the frontier. The search
stops when the goal is closed or when a fixed number of node expansions is
spent. Sampling temperature controls how varied the proposals are. The
kernel is never trusted to the model: nothing the model says is accepted
without a check, which is why a wrong model wastes budget but cannot produce
a wrong proof.

What varies and what is judged:
A proof attempt, that is, the tree of tactic applications built during the
search. It is judged on one thing, whether the kernel accepts a complete
proof within the expansion budget.

What is measured:
Closed or not closed, a binary fact, plus the number of expansions consumed
and the length of the resulting proof, both integers.

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

### Prompt 41: Inductive Logic Programming

```
FRONTIER PRACTITIONER DOSSIER
Field: Inductive Logic Programming

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
From a handful of examples and some background facts, can a system write a
logic program that explains them, and can it invent the intermediate
concepts it needs but was never given?

Mechanism as I currently understand it:
Meta-interpretive learning runs a Prolog meta-interpreter that tries to
prove the positive examples. When it cannot prove a goal from the background
knowledge directly, it applies a metarule, which is a higher-order clause
template with variables standing for predicate names, such as the chain rule
saying P of A and B holds if Q of A and C and R of C and B hold. Proving the
goal then requires binding those predicate variables, and the bindings that
succeed are recorded as the induced clauses. If no existing predicate can be
bound, a fresh predicate symbol is drawn from the signature, and that is
predicate invention. The whole search is run under iterative deepening on
the number of clauses, so the first hypothesis found is minimal in clause
count, and negative examples must not be provable.

What varies and what is judged:
A hypothesis, that is a set of logic clauses possibly including invented
predicates. What varies is which metarules are available and how many
clauses are permitted. What is judged is whether the hypothesis entails all
positive and no negative examples.

What is measured:
Whether a consistent hypothesis was found within the clause bound, the
clause count of the hypothesis found, the number of predicates invented, and
the search time. Clause count is a small integer and is the natural scalar.

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

### Prompt 42: Inductive Reasoning

```
FRONTIER PRACTITIONER DOSSIER
Field: Inductive Reasoning

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
As you show a learner labelled examples one at a time, how fast does the set
of rules still consistent with everything it has seen shrink toward a single
answer?

Mechanism as I currently understand it:
Fix a language of hypotheses in advance, classically conjunctions over
attributes where each attribute is either pinned to a value, or a wildcard
matching anything, or the empty symbol matching nothing. The version space
is the set of hypotheses consistent with every example seen so far.
Candidate Elimination represents that set implicitly by only its two
boundaries: S, the most specific consistent hypotheses, and G, the most
general. On a POSITIVE example, drop any member of G that fails to cover it,
and minimally generalise each member of S until it covers it. On a NEGATIVE
example, drop any member of S that covers it, and minimally specialise each
member of G until it no longer does. The version space is everything lying
between the two boundaries in the generality ordering, so its size can be
huge while S and G stay small. Learning is complete when S and G coincide on
a single hypothesis. The method is exact and non-statistical: it never
scores a hypothesis, it only eliminates the inconsistent, and one
contradictory example collapses the space to empty.

What varies and what is judged:
The whole surviving hypothesis set, not any single hypothesis. What varies
is which examples arrive and in what order.

What is measured:
The size of the version space after m examples, a positive integer that
falls monotonically, and convergence when it reaches one. Log of the size is
the better scale, since it falls roughly linearly with informative examples.

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

### Prompt 43: Metamorphic Testing

```
FRONTIER PRACTITIONER DOSSIER
Field: Metamorphic Testing

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
How do you test a program when nobody knows what the right answer is, and
you therefore have nothing to compare its output against?

Mechanism as I currently understand it:
Give up on knowing the correct output and instead state a relation that must
hold between the outputs of two related runs. Pick an input, run the
program, then transform the input in a way whose effect on the output is
known by construction, run the program again, and check the relation.
Classic examples are that the sine of an angle equals the sine of its
supplement, or that adding a constant to every element of a dataset must
shift the reported mean by exactly that constant, or that shuffling the
input rows of a classifier's training set should leave a deterministic
classifier's output unchanged. The relation is asserted between two
executions; neither execution is ever independently checked. When the
relation is violated, the pair of inputs is a failing witness with no
ambiguity about whether a bug exists.

What varies and what is judged:
The pair of inputs, an original and its transform. What is being judged is
not the pair but the PROGRAM, through its consistency across the pair. This
inversion is the method's distinguishing feature.

What is measured:
Whether the relation held, a binary fact, and usually also the magnitude of
the violation, which is continuous and is what tells you whether you have
found a rounding artefact or a real defect.

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

### Prompt 44: Property-Based Testing

```
FRONTIER PRACTITIONER DOSSIER
Field: Property-Based Testing

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
Does a stated invariant survive a randomly generated sequence of state-
changing operations, and when it does not, what is the smallest sequence
that breaks it?

Mechanism as I currently understand it:
The tester writes a property, a universally quantified claim about the
system. A generator produces random inputs from a declared distribution. The
property is checked on each. In the stateful form, the generator produces a
random SEQUENCE of commands, a model of the system is stepped alongside the
real system, and postconditions are checked after each command rather than
only at the end. When a counterexample is found, shrinking repeatedly re-
runs the property on systematically smaller inputs, keeping any that still
fail, until a minimal failing case remains, and it is that minimal case, not
the original random one, that is reported.

What varies and what is judged:
The generated input, here the sequence of walk increments determined by the
derived seed. What varies is the seed and the sequence length. What is
judged is whether the invariant holds on the resulting state.

What is measured:
displacement and position, both continuous and unbounded, compared against
an invariant bound. The bench also returns start_position, steps and
step_scale, so the invariant can be stated in terms of the declared inputs.

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

### Prompt 45: Search-Based Software Engineering

```
FRONTIER PRACTITIONER DOSSIER
Field: Search-Based Software Engineering

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
If you can write down what makes one version of a piece of software better
than another as a single number, can a dumb local search find a good version
for you?

Mechanism as I currently understand it:
Reformulate a software engineering problem as optimisation. Encode the
artefact as a string, for example one bit per test case included in a suite,
or per module assigned to a cluster, or per requirement selected for a
release. Define a fitness function from measurable properties such as
coverage achieved, coupling reduced or cost incurred. Start from some
candidate. Repeatedly evaluate the neighbours reachable by a single small
change, typically all single-position flips; move to the best improving
neighbour; stop when no neighbour improves, which certifies a local optimum;
restart from a new starting point and repeat until the evaluation budget is
exhausted. The method's real content is that the fitness function encodes a
genuine engineering objective, and the search is deliberately
unsophisticated.

What varies and what is judged:
A bitstring encoding of a software artefact, judged by the fitness function.
What varies is the bits, and, across restarts, the starting point.

What is measured:
Best fitness found, continuous, and the evaluations consumed, an integer;
across restarts, also the number of distinct local optima certified.

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

### Prompt 46: Learning-to-Search

```
FRONTIER PRACTITIONER DOSSIER
Field: Learning-to-Search

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
Can a policy learn to copy an expert well enough that it stays on the
expert's path even when it is the one driving, rather than only when the
expert has been driving all along?

Mechanism as I currently understand it:
DAgger. Round one rolls out the expert, collects state and expert-action
pairs, and trains a policy on them. Round i rolls out a mixture policy that
takes the expert's action with probability beta and the learner's otherwise,
so the states visited are the ones the LEARNER induces. At every visited
state the expert is queried for the action it would have taken, and those
labels are appended to an aggregated dataset that is never discarded. The
policy is retrained on the whole aggregate, and beta decays toward zero.
Training on the learner's own state distribution is the entire trick: it
converts imitation into a no-regret online learning problem and removes the
error that otherwise compounds quadratically in the horizon.

What varies and what is judged:
The policy. It is judged by its loss against the expert's action, measured
on the states the policy itself visits rather than on the expert's states.

What is measured:
Per-step disagreement with the oracle or test loss, a continuous non-
negative quantity, and crucially its scaling with the horizon, which is
where the linear-versus-quadratic claim lives.

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

### Prompt 47: Scientific Machine Learning

```
FRONTIER PRACTITIONER DOSSIER
Field: Scientific Machine Learning

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
Can a neural network be made to solve a differential equation by being
penalised for violating the equation itself, rather than by being shown
examples of the solution?

Mechanism as I currently understand it:
The unknown solution is represented directly by a neural network taking the
space and time coordinates as inputs. Points are sampled across the domain,
called collocation points. At each one the residual of the governing
equation is computed by differentiating the network's output with respect to
its own inputs using automatic differentiation, so the derivatives in the
equation are exact rather than discretised. The training loss is the mean
squared residual over the collocation points plus a mean squared error term
on the initial and boundary conditions. The network is trained by gradient
descent, usually Adam followed by a quasi-Newton refinement. At the end the
residual is reported, and where a reference solution exists so is the
relative error against it. No solution data is needed in the interior of the
domain, which is the whole selling point.

What varies and what is judged:
The trained network, that is, its weights, judged by the residual it
achieves and by its distance from the true solution.

What is measured:
Mean squared residual, continuous and near zero, and relative error against
a reference solution, also continuous. These are two different numbers with
very different meanings and the difference between them is the entire
subject.

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

### Prompt 48: Automated Scientific Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Automated Scientific Discovery

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
Can a small set of general heuristics, applied to a table of measurements,
rediscover the empirical law that generated them, without being told the
form of the law in advance?

Mechanism as I currently understand it:
BACON reads a table of observed variables. It applies a handful of data-
driven heuristics, one at a time. If a quantity is constant, record it as a
law. If two quantities increase together, define a new theoretical term
equal to their ratio. If one increases as the other decreases, define their
product. Each new term becomes a column in the table, and the heuristics run
again on the enlarged table. The recursion halts when some derived term
comes out constant within tolerance, and that constant term is the
discovered law. This is how BACON reaches expressions of the same shape as
the ideal gas law and Kepler's third law from raw tables.

What varies and what is judged:
A derived theoretical term, that is a composed expression over the observed
variables. What varies is which composition the heuristics build. What is
judged is whether that term is constant across the rows within tolerance.

What is measured:
Whether a law was found within the depth budget, the depth at which it was
found, and the residual variation of the discovered constant. The natural
scalar is the residual, from 0 upward.

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

### Prompt 49: Computational Models of Scientific Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Computational Models of Scientific Discovery

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
Can a small set of mechanical rules, given nothing but a table of numbers,
rediscover a quantitative law of nature such as the relation between a
planet's distance from the sun and the time it takes to orbit?

Mechanism as I currently understand it:
The system holds a table of observations with one column per measured
variable and applies a very small set of data-driven heuristics in a loop.
If a term is constant across the rows within tolerance, record it as a law
and stop. If two terms increase together, define a new column that is their
ratio. If one increases as the other decreases, define a new column that is
their product. Then look again at the enlarged table for a constant term.
Applied to distance D and period P, the recursion builds D over P, then that
over P again, then a ratio of those, and arrives at D cubed over P squared
being constant, which is Kepler's third law. Later versions add symmetry and
common-divisor heuristics and intrinsic properties, and handle several
independent variables by holding all but one fixed and sweeping. The
essential point is that this is a search over DERIVED TERMS, not a fit of a
pre-chosen functional form.

What varies and what is judged:
A derived term, an expression built from the measured columns. What is
judged is whether that term is constant across rows.

What is measured:
Whether a constant term was found; the coefficient of variation of the best
term, a continuous non-negative number; and the number of search steps taken
to reach it, a count.

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

### Prompt 50: Machine Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Machine Discovery

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
Can a program that starts from a handful of elementary set theory ideas and
a bag of rules of thumb invent new mathematical concepts that a
mathematician would call interesting?

Mechanism as I currently understand it:
AM holds each concept as a frame with slots, a definition, known examples,
generalisations, specialisations and a numeric worth. It also holds an
agenda of pending tasks, each task being something like fill in examples of
this concept, generalise it, specialise it, or look for a regularity among
its examples. The agenda is sorted by an interestingness score computed from
heuristic rules. The loop is: pop the top task, run it, which usually means
executing or rewriting a Lisp definition, create whatever new concepts
result, assign them a worth, and push the tasks they suggest back onto the
agenda. Run until the step budget is spent. Famously the loop reached the
notion of a number with unusually few divisors, that is, primes, and then
unique factorisation, from set theoretic starting material. The output is
not one number, it is the trace of concepts created and their worth.

What varies and what is judged:
A generated concept, that is, a Lisp frame carrying an executable
definition. What varies is which concepts get created and what worth the
heuristics award them.

What is measured:
The count of concepts generated whose worth exceeds a threshold, on a
bounded numeric scale, plus a discrete rediscovery checklist, did it reach
primes, did it reach unique factorisation. The second of those is the number
anyone actually cares about and it is not continuous.

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

### Prompt 51: Automated Conjecture Generation

```
FRONTIER PRACTITIONER DOSSIER
Field: Automated Conjecture Generation

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
Starting from a small set of given concepts and a finite pile of example
objects, how many non-trivial conjectures does an automated concept-
inventing loop actually produce within a fixed search budget, and does
narrowing the set of ways it is allowed to build new concepts change that
yield?

Mechanism as I currently understand it:
HR begins with core concepts and concrete example data, for example the
integers up to some bound or a set of small finite groups. Production rules
such as exists, match, negate, size, split and compose take existing
concepts and manufacture new concept definitions. Every new concept is
evaluated empirically by computing its extension, the set of example objects
that satisfy it. Regularities among extensions are then read off as
conjectures: two concepts with identical extensions give an equivalence
conjecture, one extension contained in another gives an implication, an
empty extension gives a non-existence conjecture. Concepts are scored by
interestingness measures and the best are fed back to the production rules,
so the theory is an archive that grows and reshapes what gets built next.

What varies and what is judged:
The invented concept, that is a definition assembled by applying a
production rule to concepts already in the theory. It is judged twice, first
empirically by its extension over the object set and second by
interestingness heuristics that decide whether it re-enters the generator.

What is measured:
A count of emitted conjectures, a non-negative integer, ideally broken down
by conjecture class. Secondarily the size and shape of the concept tree.

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

### Prompt 52: Computational Creativity

```
FRONTIER PRACTITIONER DOSSIER
Field: Computational Creativity

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
Can a search driven only by how different a behaviour is from everything
already seen keep producing new behaviours indefinitely, with no goal and no
fitness function telling it what counts as better?

Mechanism as I currently understand it:
Each individual is run in a domain and reduced to a behaviour
characterisation, a low-dimensional vector such as a final position. Its
novelty is the mean distance to its k nearest neighbours among the current
population together with an archive of previously encountered behaviours.
Selection is on novelty alone. Individuals that are sufficiently novel are
inserted into the archive, which makes that region of behaviour space less
rewarding for everything that comes after, so the search is continuously
pushed outward. The archive is the mechanism: without it the search forgets
and cycles.

What varies and what is judged:
An individual, that is a genome mapped to a controller. It is judged only by
the distance of its behaviour from stored behaviours, and crucially the
comparison is on behaviour, not genome, so two very different genomes with
the same behaviour are interchangeable.

What is measured:
Novelty score, a continuous non-negative distance, along with archive growth
rate and behaviour-space coverage over time.

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

### Prompt 53: Computational Serendipity

```
FRONTIER PRACTITIONER DOSSIER
Field: Computational Serendipity

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
How often does an aimless, undirected process stumble into something a
standing criterion would call valuable?

Mechanism as I currently understand it:
The account this template draws on breaks a serendipitous discovery into
four parts. A prepared mind holds standing interests and evaluation
criteria. A serendipity trigger occurs, and it is unsought, accidental and
independent of what the agent was doing. A bridge is then constructed by the
agent, connecting the trigger to something it cares about. A result follows,
and the result must have value. The account grades an episode along three
dimensions: chance, how unlikely and unsought the trigger was; sagacity, how
much insight the bridge took; and value, how good the result is. Only the
combination is serendipity.

What varies and what is judged:
A trajectory of an unguided stochastic process. What varies is where the
wander goes; what is judged is whether it reaches a state a preset criterion
calls valuable.

What is measured:
The signed final position and the displacement from the start, both
continuous, compared once against a threshold.

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

### Prompt 54: Discovery Informatics

```
FRONTIER PRACTITIONER DOSSIER
Field: Discovery Informatics

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
Given a candidate bridging term that connects two unrelated bodies of
literature, can a statistical model predict from a few cheap features
whether that bridge is a real, relevant connection rather than noise?

Mechanism as I currently understand it:
In an Arrowsmith style two node search, two literatures are retrieved and
the terms they share are extracted. There are typically hundreds or
thousands of them and almost all are worthless, so the practical problem is
ranking. Torvik and Smalheiser computed, for each shared term, a set of
cheap features, how often it appears in each literature, how many distinct
literatures it occurs in, its indexing category, how cohesive its usage is,
and fitted a logistic regression of those features against expert relevance
judgements. The fitted model returns a probability of relevance, the terms
are sorted by it, and a human curator reads only the top of the list. The
method is ordinary supervised ranking; what makes it a discovery method is
what the features are computed over.

What varies and what is judged:
One shared bridging term, represented as a feature vector, judged by its
predicted relevance.

What is measured:
In the real method, a predicted probability in 0 to 1, evaluated in
aggregate by area under the curve or precision at k. In the template,
evaluate_bitstring's score, which is the fraction of bits agreeing with a
hash derived target.

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

### Prompt 55: Knowledge Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Knowledge Discovery

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
Do two bodies of medical literature that never cite each other nonetheless
share intermediate terms, and can those shared terms point to a real
connection that nobody had noticed?

Mechanism as I currently understand it:
Swanson's ABC model. Choose literature A, for instance Raynaud's syndrome,
and literature C, for instance dietary fish oil, which have essentially no
articles and no citations in common. Extract terms from the titles of each.
Intersect them. A term B appearing in both, such as blood viscosity or
platelet aggregation, indicates that A to B and B to C are separately known
while A to C has never been stated, so A to C becomes a candidate implicit
connection. A human then reads the ranked bridging terms and judges which
are plausible. The Arrowsmith system automates the retrieval and
intersection; the judgement stays human. Swanson's fish oil and Raynaud's
proposal, and later his magnesium and migraine proposal, were both
subsequently supported by clinical work.

What varies and what is judged:
The pair of literatures. What is judged is the set of bridging terms between
them, and whether there are more or better of them than two arbitrary
disjoint literatures would share by chance.

What is measured:
The number of shared bridging terms and their ranking scores, and, in a well
run version, the significance of that count against a null of randomly
paired disjoint literatures. Counts and continuous scores.

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

### Prompt 56: Case-Based Reasoning

```
FRONTIER PRACTITIONER DOSSIER
Field: Case-Based Reasoning

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
When a new problem arrives, can a memory of past cases return the genuinely
most similar past case, and does the choice of similarity measure change
which case comes back?

Mechanism as I currently understand it:
Case-based reasoning runs a four step cycle, retrieve, reuse, revise,
retain. This template isolates the first step. A case base holds N past
cases, each described by a vector of D features together with the solution
that was used. A new problem arrives described in the same features. A
similarity function scores every stored case against the query, either as
plain geometric closeness, Euclidean or cosine, or with domain knowledge
weighting some features more heavily than others. The cases are ranked and
the top one is returned with its similarity score. In the full cycle that
case's solution would then be adapted, tested and stored back, but none of
that happens here.

What varies and what is judged:
The query case. What is judged is the retrieval, that is, the similarity
score of the top ranked case, and in a stricter design whether the retrieved
case's solution was in fact the right one.

What is measured:
Top one similarity, continuous on 0 to 1. Optionally retrieval accuracy
against a labelled correct neighbour, which is a different and much more
meaningful number.

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

### Prompt 57: Analogical Reasoning

```
FRONTIER PRACTITIONER DOSSIER
Field: Analogical Reasoning

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
Given two described situations, how good is the best correspondence between
them that can be built purely from matching relational structure rather than
matching surface features, and does insisting on deep, interconnected
structure change the answer?

Mechanism as I currently understand it:
The Structure-Mapping Engine works in stages. First it proposes local match
hypotheses between base and target items whose predicates are identical,
together with the argument matches those force. Second it merges locally
consistent hypotheses into structurally consistent kernels, obeying one-to-
one correspondence and parallel connectivity, which means matching a
relation requires matching its arguments. Third it merges kernels into a
small number of maximal global interpretations and scores each with a
structural evaluation that propagates evidence downward from relations to
their arguments, so that a deep interconnected system of relations outweighs
a large number of shallow attribute matches; that weighting is the
systematicity principle. Fourth it projects unmatched base structure across
the mapping into the target as candidate inferences, which is what makes
analogy generative rather than merely comparative.

What varies and what is judged:
The mapping, that is a set of correspondences between base and target items.
It is judged by a structural evaluation score and constrained by one-to-one
and parallel connectivity, so most syntactically possible mappings are never
scored at all.

What is measured:
The structural evaluation score of the best interpretation, a continuous but
unnormalised quantity, plus the number of correspondences and the candidate
inferences. The scale is the problem: the score is not comparable across
descriptions of different sizes.

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

### Prompt 58: Computational Philosophy of Science

```
FRONTIER PRACTITIONER DOSSIER
Field: Computational Philosophy of Science

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
When two scientific theories compete over the same body of evidence, can the
choice between them be reproduced by a simple mechanical process that only
balances which theory explains more and contradicts less?

Mechanism as I currently understand it:
Every proposition, whether hypothesis or evidence, becomes a unit in a
network. If one hypothesis, possibly together with others, explains a
proposition, symmetric excitatory links are created among all of them, with
the weight divided among co-hypotheses so that explaining something with
fewer assumptions pays better. If two propositions contradict, an inhibitory
link is created. Evidence units also receive an excitatory link from a
special always-on data unit, which is how observation gets its privileged
pull. Activation is then updated in parallel over many cycles by a standard
connectionist rule until activations stop changing. Units settling positive
are accepted, units settling negative are rejected. The whole thing is
parallel constraint satisfaction with no search and no explicit inference
rules.

What varies and what is judged:
A hypothesis unit. What varies is its final activation, and what is judged
is whether it is accepted, which depends on the whole network rather than on
the unit alone.

What is measured:
A settled activation per unit, continuous and bounded between minus one and
one, plus whether the network settled at all within the cycle budget.

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

### Prompt 59: Abductive Reasoning

```
FRONTIER PRACTITIONER DOSSIER
Field: Abductive Reasoning

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
Given a set of observed symptoms, can a system pick the smallest set of
underlying causes that accounts for all of them, and how small can that
explanation get before it stops covering everything?

Mechanism as I currently understand it:
Parsimonious covering theory sets up a two-layer causal network. One layer
is disorders, the other is manifestations, and a stored relation says which
manifestations each disorder can produce. A case presents a set of observed
manifestations. The solver then searches the powerset of disorders for
subsets whose combined manifestation sets cover every observation, and among
those covers it prefers the ones of minimum cardinality or the ones that are
irredundant, meaning no member can be dropped without losing coverage. The
output is a cover, or a set of competing covers, plus its size.

What varies and what is judged:
A candidate explanation, which is a subset of the disorder set. What varies
is which disorders are in the subset and how many there are. What is judged
is whether the subset covers all observed manifestations and how large the
subset is.

What is measured:
The cardinality of the returned cover, an integer bounded below by 1 and
above by the hypothesis space size, plus a boolean saying whether the cover
is complete. On the bench only one of those two can be adjudicated.

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

### Prompt 60: Evolutionary Epistemology

```
FRONTIER PRACTITIONER DOSSIER
Field: Evolutionary Epistemology

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
Can new knowledge be produced by a process that generates its guesses
blindly, with no foresight about which will work, provided that the
successful guesses are kept and built on?

Mechanism as I currently understand it:
The claim being tested is that all genuine increases in knowledge require
three things and only those three: variation that is blind, meaning
uncorrelated with which variant will turn out to succeed; a selection step
that culls variants against a criterion the variant-generator cannot see;
and retention, so that surviving variants become the starting point for the
next round of variation rather than being discarded. Foresight, if it
exists, is then explained as the compressed residue of earlier rounds of the
same process, not as an extra ingredient. Operationally the model is run by
perturbing a current best guess, testing it, keeping the perturbation only
if the test improved, and repeating under a fixed budget; the comparison of
interest is against the same process with retention switched off.

What varies and what is judged:
A candidate idea, encoded as a bitstring. What varies is its bits and what
is judged is its score against a criterion the generator has no access to.

What is measured:
Best score reached at a fixed evaluation budget, continuous between zero and
one, or equivalently the number of evaluations to first reach the target.

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

### Prompt 61: Universal Darwinism

```
FRONTIER PRACTITIONER DOSSIER
Field: Universal Darwinism

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
Is the difference between something being astronomically improbable and
being easy just the difference between guessing it all at once and building
it up in small steps that are each kept?

Mechanism as I currently understand it:
Fix a target string. Start from a random string of the same length. Each
generation, make a number of copies of the current string, mutate each copy
at some per-position rate, score every copy by how many positions match the
target, and keep the single best copy as the parent of the next generation.
Repeat. The comparison the demonstration exists to make is against single-
step selection, where the whole string is redrawn at random each time and
nothing is retained: single-step selection needs on the order of the size of
the whole space, while cumulative selection needs on the order of tens of
generations. The gap between the two numbers, not the absolute time, is the
entire result.

What varies and what is judged:
A string. What varies is its positions; it is judged by the count of
positions matching the target.

What is measured:
Generations to reach the target, an integer, or best match fraction at a
fixed budget, continuous between zero and one.

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

### Prompt 62: Science of Science

```
FRONTIER PRACTITIONER DOSSIER
Field: Science of Science

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
Why are citations so unequally distributed, with a few papers collecting
enormous numbers and most collecting almost none? Can a simple growth rule,
with no notion of quality, reproduce that inequality on its own?

Mechanism as I currently understand it:
Grow a graph one node at a time. Each arriving node attaches a fixed number
of edges to nodes already present, choosing each target with probability
proportional to how many edges that target already has, usually plus a small
constant so that a node with none can still be chosen. That is the entire
rule, and it is enough: because attachment probability rises with current
degree, early and lucky nodes accumulate advantage, and the degree
distribution develops a heavy tail. Richer variants in this literature
multiply the degree term by a per-node fitness, so that quality and
accumulated advantage compete, and add an ageing term so that old papers
stop attracting citations, which together reproduce the observed pattern in
which most papers peak and decline while a few remain live for decades. The
measurement at the end is a structural statistic over the finished graph.

What varies and what is judged:
The graph. What is judged is a summary statistic of its shape, not any
individual node.

What is measured:
A structural statistic of the final graph: Gini coefficient of the degree
distribution, share of edges held by the top one percent, maximum degree
over node count, or a fitted power-law exponent. All scalar, but they differ
enormously in how safely they can be gated on.

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

### Prompt 63: Meta-Science

```
FRONTIER PRACTITIONER DOSSIER
Field: Meta-Science

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
If you know how well-powered a field's studies are, how often it looks for
effects that are not there, and how much fiddling goes on, what fraction of
its published positive findings are actually true?

Mechanism as I currently understand it:
Model a field with four numbers. Pre-study odds say how many of the
relationships researchers examine are genuinely real. Power says how often a
real relationship is detected. The significance level says how often a non-
existent relationship is nonetheless declared significant. A bias term says
what fraction of results that should have been null get converted into
positives by flexible analysis, selective reporting or outright error.
Simulate one study by drawing whether the relationship is real, then drawing
whether it is declared significant under the appropriate rate, then applying
the bias conversion. Aggregate over many studies and the positive predictive
value, the fraction of declared positives that are true, falls out. The
headline consequence is that with low power, low pre-study odds, and modest
bias, that fraction drops below one half.

What varies and what is judged:
A single simulated study, judged only on whether its declared positive is
true.

What is measured:
For one study, a boolean. For the field, a ratio, the positive predictive
value, which is the quantity the theory is actually about.

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

### Prompt 64: Robot Scientists

```
FRONTIER PRACTITIONER DOSSIER
Field: Robot Scientists

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
If you delete one gene from a yeast strain and then add one nutrient back
into its food, does the yeast grow again? The answer is meant to hint at
what the deleted gene was doing.

Mechanism as I currently understand it:
Take a yeast strain in which exactly one open reading frame has been
deleted. Grow it in a chemically defined medium that lacks the nutrient of
interest, and in parallel in the same medium with that one nutrient added
back. Incubate, and read optical density of the culture over time as the
growth readout. A strain that fails to grow without the supplement and grows
with it is auxotrophic for that nutrient, which places the deleted gene
somewhere upstream in the pathway that makes it. In the real Robot Scientist
loop this assay is not the whole method: a logical model of the metabolic
pathway proposes which gene-enzyme pairing would predict which growth
outcome, the machine picks the assay that best discriminates among live
hypotheses, the robot physically runs it, and the outcome kills the
hypotheses it contradicts. The growth assay is the single measurement at the
bottom of that loop.

What varies and what is judged:
The knocked-out strain. What varies is which single gene is absent and which
single nutrient is present.

What is measured:
Final or maximum optical density, a continuous positive real, in practice
compared against a no-growth control. Richer versions read the whole growth
curve and extract lag time and doubling rate.

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

### Prompt 65: Automated Experimentation

```
FRONTIER PRACTITIONER DOSSIER
Field: Automated Experimentation

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
Which combination of dopant concentration and annealing time gives a thin
film the highest charge-carrier mobility, and can a machine find it by
choosing its own next experiment rather than following a human's plan?

Mechanism as I currently understand it:
A robot runs a closed loop. Each iteration mixes an ink from a hole-
transport material, a dopant and an additive at a chosen ratio; spin coats
it onto a substrate; anneals it on a hotplate for a chosen time; photographs
the film; takes an optical spectrum; and measures a current-voltage curve. A
pseudomobility is computed from the conductivity and the film thickness. A
model-based optimiser fits a surrogate to every measurement made so far and
picks the next ratio and time. The loop repeats until the budget of physical
experiments is spent.

What varies and what is judged:
A processing recipe, that is, one point in a two-dimensional continuous
space of dopant ratio and annealing time. It is judged by the measured
pseudomobility of the film it produces.

What is measured:
Pseudomobility, a positive continuous quantity, one value per film, plus the
count of physical experiments consumed, an integer.

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

### Prompt 66: Algorithm Discovery

```
FRONTIER PRACTITIONER DOSSIER
Field: Algorithm Discovery

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
Can a search over encoded sequences of computational primitives find a
genome that behaves like a target algorithm, rather than merely resembling
it bit for bit?

Mechanism as I currently understand it:
In the PADO line of work, a genome is decoded into an executable program, in
that case a graph or tree of primitive operations with indexed memory. The
program is then run on a set of input signals, its outputs are read, and
fitness is the quality of those outputs on the classification task. Multiple
such programs are orchestrated, each contributing a confidence, and the
ensemble decides. The essential step is that the genome is INTERPRETED
before it is judged; nothing is scored on its syntax.

What varies and what is judged:
The bitstring genome. What varies across specs is which bitstring is
submitted and, through length, which landscape it faces. What is being
judged, on this bench, is the fraction of positions matching a hidden target
string.

What is measured:
score, continuous from 0 to 1, equal to the count of matching positions
divided by the target length, plus solved, a boolean true only at score 1.0.

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

### Prompt 67: Evolutionary Computation

```
FRONTIER PRACTITIONER DOSSIER
Field: Evolutionary Computation

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
How good is one particular binary individual on a hidden fitness landscape,
and how does that change as the genome gets longer?

Mechanism as I currently understand it:
In a genetic algorithm the inner loop is fitness evaluation. An individual
is a bitstring, it is handed to an objective function, and a scalar comes
back. Selection then keeps the better scoring individuals, crossover
recombines pairs of them, mutation flips occasional bits, and the next
generation is evaluated. Holland's framework explains why this works in
terms of schemata, short building blocks of bits whose above average fitness
is compounded across generations. This template runs only the evaluation
step: one uniformly drawn bitstring is scored against a hidden target
derived from the seed and the length.

What varies and what is judged:
A single bitstring genome, sampled uniformly at random.

What is measured:
Score, continuous on 0 to 1, equal to the fraction of matching bits, plus a
solved flag that fires only at exactly 1.0.

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

### Prompt 68: Computational Mathematics

```
FRONTIER PRACTITIONER DOSSIER
Field: Computational Mathematics

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
Over a fixed number of steps, how far does an unbiased one dimensional
random walk wander, and does the accumulated displacement stay inside the
bounds that theory predicts?

Mechanism as I currently understand it:
Start at the origin. Repeat a fixed number of times: draw a value uniformly
from minus one to plus one, multiply by the step scale, add it to the
current position. Report the final position and the displacement from the
start. Because each increment is independent with mean zero and variance
equal to the square of the step scale divided by three, the displacement
after n steps is asymptotically normal with mean zero and standard deviation
equal to the step scale times the square root of n over three. The
characteristic prediction of the model is not any single endpoint but that
the spread grows as the square root of the number of steps, which is the
diffusive scaling law.

What varies and what is judged:
The realised trajectory, judged by its endpoint. Nothing is being optimised.

What is measured:
Position and displacement, continuous and unbounded, in units of the step
scale. The executor also returns start position, steps and step scale, so
the fossil is self describing.

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

### Prompt 69: Falsification-Based Search

```
FRONTIER PRACTITIONER DOSSIER
Field: Falsification-Based Search

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
If you cannot prove a system safe, can you at least hunt hard for an input
that makes it unsafe, and how much hunting does it take to find one?

Mechanism as I currently understand it:
A safety requirement is written in a temporal logic over signals, for
example that a value never leaves a band for the whole run. That formula is
given a real-valued robustness rather than a yes or no: positive means
satisfied with room to spare, near zero means marginal, negative means
violated, and the magnitude says by how much. Falsification then becomes
minimisation. A stochastic optimiser, Monte Carlo sampling or simulated
annealing or cross-entropy, proposes input signals and parameters, simulates
the system, computes robustness, and steers toward lower robustness. The
first negative value is a counterexample and the search stops. No negative
value within budget proves nothing at all; the search is deliberately
incomplete.

What varies and what is judged:
A trajectory, and behind it the input signal that produced it. What varies
is the sampled input; what is judged is the robustness of the resulting
trace against the property.

What is measured:
In the real method, a continuous robustness value per trace and, over a
campaign, the number of simulations to first falsification. On this bench,
only the terminal position and displacement.

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
