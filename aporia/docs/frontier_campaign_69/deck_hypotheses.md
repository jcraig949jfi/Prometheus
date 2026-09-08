# H0 to H5 evidence deck

Prompts 201 to 212. Two per hypothesis: prior-art audit, then
adversarial review. Verdict on line one in both.

The hypothesis statements are Aporia's RECONSTRUCTION from Archaeon's
feasibility note. No H0-H5 document exists in the repository.

---

### Prompt 201: H1 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H1 -- Failure transport between tasks

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
When a search fails on one task and the failure is recorded as a concrete
counterexample or witness, supplying that stored witness to a later search
on a RELATED task improves the later search, relative to supplying nothing
and relative to supplying a witness drawn at random from an unrelated task.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
Solve fraction on the later task at matched total compute, across three
arms: no transport, random-witness transport, relevance-selected transport.
The random arm is the one that matters, because it separates the value of
the SELECTION from the value of merely having an extra input.

CONTEXT THAT MAY NARROW THE LITERATURE
The setting is automated program synthesis and verification, where a
counterexample is a concrete failing input rather than a gradient or an
embedding, and the transport is between separate sealed runs rather than
within one loop.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 202: H1 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H1 -- Failure transport between tasks

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
When a search fails on one task and the failure is recorded as a concrete
counterexample or witness, supplying that stored witness to a later search
on a RELATED task improves the later search, relative to supplying nothing
and relative to supplying a witness drawn at random from an unrelated task.

THE COMPARISON THEY INTEND
Solve fraction on the later task at matched total compute, across three
arms: no transport, random-witness transport, relevance-selected transport.
The random arm is the one that matters, because it separates the value of
the SELECTION from the value of merely having an extra input.

CONTEXT
The setting is automated program synthesis and verification, where a
counterexample is a concrete failing input rather than a gradient or an
embedding, and the transport is between separate sealed runs rather than
within one loop.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 203: H2 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H2 -- A dynamical system as a reusable component

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
A fixed dynamical system, for instance a cellular automaton driven as a
streaming component with per-step input injection, an explicit reset and a
trained readout, can serve as a reusable computational component, and the
computation it performs is attributable to its own dynamics rather than to
the readout that decodes it.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
Performance of the full system against two controls: the same readout on a
lesioned or frozen substrate, and the same readout on a matched-random
substrate of equal state dimension. Attribution requires the readout class
and its parameter budget to be fixed in advance, because a sufficiently
powerful decoder can manufacture the result.

CONTEXT THAT MAY NARROW THE LITERATURE
The substrate is a discrete cellular automaton rather than a continuous
recurrent network, and the component must be reused across separate sealed
executions rather than trained end to end.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 204: H2 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H2 -- A dynamical system as a reusable component

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
A fixed dynamical system, for instance a cellular automaton driven as a
streaming component with per-step input injection, an explicit reset and a
trained readout, can serve as a reusable computational component, and the
computation it performs is attributable to its own dynamics rather than to
the readout that decodes it.

THE COMPARISON THEY INTEND
Performance of the full system against two controls: the same readout on a
lesioned or frozen substrate, and the same readout on a matched-random
substrate of equal state dimension. Attribution requires the readout class
and its parameter budget to be fixed in advance, because a sufficiently
powerful decoder can manufacture the result.

CONTEXT
The substrate is a discrete cellular automaton rather than a continuous
recurrent network, and the component must be reused across separate sealed
executions rather than trained end to end.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 205: H3 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H3 -- Retention policy determines what is discovered

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
The archive or retention policy of a search materially determines what that
search discovers, such that replaying one identical stream of generated
candidates through several different retention policies yields materially
different retained sets and different downstream discovery.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
Offline replay of a single fixed candidate stream through several policies,
comparing the retained sets and any downstream measure. Because the stream
is held fixed, generator variance is removed and any difference is
attributable to the policy alone.

CONTEXT THAT MAY NARROW THE LITERATURE
The replay is offline and post hoc over a recorded provenance stream, not an
online comparison of separately-run searches, so the usual confound of
different policies exploring different regions does not apply.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 206: H3 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H3 -- Retention policy determines what is discovered

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
The archive or retention policy of a search materially determines what that
search discovers, such that replaying one identical stream of generated
candidates through several different retention policies yields materially
different retained sets and different downstream discovery.

THE COMPARISON THEY INTEND
Offline replay of a single fixed candidate stream through several policies,
comparing the retained sets and any downstream measure. Because the stream
is held fixed, generator variance is removed and any difference is
attributable to the policy alone.

CONTEXT
The replay is offline and post hoc over a recorded provenance stream, not an
online comparison of separately-run searches, so the usual confound of
different policies exploring different regions does not apply.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 207: H4 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H4 -- Generated curricula that transfer

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
A curriculum of automatically generated tasks produces solvers that transfer
to held-out tasks the generator never produced, and does so better than a
matched budget of randomly sampled tasks from the same generator.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
Zero-shot performance on a FIXED held-out set that the generator never saw,
at matched total task budget, against a random-sampling arm. Performance
measured on the curriculum's own generated tasks is self-referential and
settles nothing.

CONTEXT THAT MAY NARROW THE LITERATURE
Tasks are generated by a template family with a validity oracle, and the
solver is transported between separate sealed runs as a frozen artifact
rather than continuing to train.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 208: H4 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H4 -- Generated curricula that transfer

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
A curriculum of automatically generated tasks produces solvers that transfer
to held-out tasks the generator never produced, and does so better than a
matched budget of randomly sampled tasks from the same generator.

THE COMPARISON THEY INTEND
Zero-shot performance on a FIXED held-out set that the generator never saw,
at matched total task budget, against a random-sampling arm. Performance
measured on the curriculum's own generated tasks is self-referential and
settles nothing.

CONTEXT
Tasks are generated by a template family with a validity oracle, and the
solver is transported between separate sealed runs as a frozen artifact
rather than continuing to train.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 209: H5 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H5 -- Learned encodings that earn their keep

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
An encoding learned from earlier data and then FROZEN before the evaluation
tasks improves search relative to a direct encoding at matched evaluation
budget, and the improvement is attributable to the encoding rather than to
the capacity of the decoder that expands it.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
Solve fraction at matched budget against a direct encoding, plus the
decisive control: a SCRAMBLED decoder that preserves the set of reachable
phenotypes AND their frequencies, destroying only the structure of the
mapping. Preserving multiplicities is what makes the control test
representation structure rather than reachability or sampling bias; a
scramble that changes which phenotypes are reachable, or how often each is
drawn, compares two different search problems and settles nothing. If the
advantage survives a multiplicity-preserving scramble it is structure; if it
does not, it was reachability, frequency, compression, or decoder capacity.

CONTEXT THAT MAY NARROW THE LITERATURE
The decoder is frozen before the target tasks and applied at draw time, so
the executor never sees it; the substrate is an elementary cellular
automaton rule table.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 210: H5 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H5 -- Learned encodings that earn their keep

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
An encoding learned from earlier data and then FROZEN before the evaluation
tasks improves search relative to a direct encoding at matched evaluation
budget, and the improvement is attributable to the encoding rather than to
the capacity of the decoder that expands it.

THE COMPARISON THEY INTEND
Solve fraction at matched budget against a direct encoding, plus the
decisive control: a SCRAMBLED decoder that preserves the set of reachable
phenotypes AND their frequencies, destroying only the structure of the
mapping. Preserving multiplicities is what makes the control test
representation structure rather than reachability or sampling bias; a
scramble that changes which phenotypes are reachable, or how often each is
drawn, compares two different search problems and settles nothing. If the
advantage survives a multiplicity-preserving scramble it is structure; if it
does not, it was reachability, frequency, compression, or decoder capacity.

CONTEXT
The decoder is frozen before the target tasks and applied at draw time, so
the executor never sees it; the substrate is an elementary cellular
automaton rule table.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 211: H0 evidence audit

```
EVIDENCE AUDIT: HAS THIS BEEN TESTED, AND WHAT HAPPENED
Hypothesis under audit: H0 -- Interaction between the mechanisms

WHAT THIS IS

A research programme I am reviewing intends to run an experiment testing the
claim below. Before any of it is built, I want to know whether the question is
already answered, and if so what the answer was. I am not the author of the
claim and I have no stake in it being true.

THE CLAIM, AS STATED TO ME
Mechanisms of the kinds described in H1 to H5 -- transporting failures,
reusing a dynamical component, changing retention policy, generating
curricula, learning an encoding -- interact when combined, so that the
effect of combining two is not simply the sum of their separate effects.

If this claim is confused, ill-posed, or already known to be false, say so.
That is the most useful thing this report can contain.

THE COMPARISON THAT WOULD DECIDE IT, AS STATED TO ME
A factorial design on the solve-fraction scale with independent seeds as the
unit of analysis, testing the interaction term explicitly rather than
comparing a combined arm against a single baseline. An interaction claim
requires the interaction to be estimated, not inferred from two main
effects.

CONTEXT THAT MAY NARROW THE LITERATURE
The mechanisms are combined within one task kind rather than across kinds,
and each factor is on or off rather than tuned.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Begin with exactly one of these words alone on the first line:

    ESTABLISHED
    MIXED
    CONTESTED
    REFUTED
    UNTESTED

ESTABLISHED means the effect has been demonstrated repeatedly WITH the
control described above, by more than one group. MIXED means it holds under
identified conditions and fails under others, and you can name both. CONTESTED
means it is claimed but the controls are disputed. REFUTED means the decisive
test was run and the effect was not there. UNTESTED means nobody has run the
decisive comparison, whatever else has been done nearby.

UNTESTED and REFUTED are valuable answers, not failures of the search. A
programme deciding what to build needs to know which of the five applies. Do
not inflate a nearby result into ESTABLISHED, and do not retreat to UNTESTED
if the work exists under a different name.

PART 2. WHO HAS RUN THE DECISIVE TEST
The specific papers, with authors, year, venue, and an arXiv id written as
arXiv:2401.01234 or a DOI written as DOI 10.1000/xyz. For each: what exactly
they compared, what the control arm was, the sample size and unit of analysis,
the effect they reported, and whether the comparison above was actually made
or only approximated. Be explicit where a paper claims the effect but ran a
weaker comparison.

PART 3. NEAR MISSES AND WHAT THEY LACK
Work that looks like it answers the question and does not. This is where most
of the literature will sit. For each, name the specific thing that is missing:
no matched control, no held-out set, tuned baseline versus untuned comparison,
performance measured on the training distribution, or unit-of-analysis errors
such as treating runs as independent when they share a seed.

PART 4. EFFECT SIZES AND BASE RATES
Where the effect has been measured, how large is it, on what scale, and with
what variance? If several groups measured it, do the numbers agree? State the
range. If reported effects shrink as controls get stricter, say so and give
the sequence, because that pattern is itself the finding.

PART 5. WHAT THE FIELD ARGUES ABOUT
The live methodological disputes bearing on this claim, and who is on each
side. Where a critique was answered, say how. Where it was never answered, say
that.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT
If a competent group wanted to settle this in weeks rather than years, what
exactly would they run? Software, data, parameters, replicate count, compute
cost, and the number to compare against. If no such experiment exists because
the question is not yet sharp enough to test, say that instead and explain
what would have to be pinned down first.

RULES

Separate what you verified from what you inferred. Mark anything unconfirmed
as UNCONFIRMED rather than dropping it. Never invent an identifier; write
IDENTIFIER UNKNOWN.

Do not use square brackets anywhere in the output. Write identifiers bare:
arXiv:2401.01234, DOI 10.1000/xyz, https://github.com/example/repo. Write
ranges as quoted strings such as "16 to 64". No markdown tables, no code
fences. Plain text with the PART headings above, verdict word alone on line
one.
```

### Prompt 212: H0 adversarial review

```
ADVERSARIAL REVIEW: WHY THIS WOULD FAIL
Hypothesis under review: H0 -- Interaction between the mechanisms

BEFORE ANYTHING ELSE: THE FIRST LINE OF YOUR OUTPUT MUST BE ONE OF THESE FOUR
WORDS, ALONE ON THE LINE, WITH NO TITLE, NO HEADING AND NO PREAMBLE ABOVE IT:

    FATAL
    SEVERE
    MANAGEABLE
    WEAK

Three previous reports in this series opened with a title and a summary and
omitted the verdict entirely, which cost the machine-readable answer. Write
the word first, then begin the report.

WHAT THIS IS

A research programme intends to test the claim below and believes it is
promising. I want the opposite case, argued as strongly as the evidence
allows. Assume the programme is competent and well resourced; the question is
not whether they can execute, but whether the effect is there to find and
whether they would be able to tell if it were not.

Do not balance this report. I have a separate report seeking supporting
evidence. This one is for the case against, and a report that hedges toward
the middle is less useful to me than one that states the strongest objection
plainly and then says how strong it actually is.

THE CLAIM
Mechanisms of the kinds described in H1 to H5 -- transporting failures,
reusing a dynamical component, changing retention policy, generating
curricula, learning an encoding -- interact when combined, so that the
effect of combining two is not simply the sum of their separate effects.

THE COMPARISON THEY INTEND
A factorial design on the solve-fraction scale with independent seeds as the
unit of analysis, testing the interaction term explicitly rather than
comparing a combined arm against a single baseline. An interaction claim
requires the interaction to be estimated, not inferred from two main
effects.

CONTEXT
The mechanisms are combined within one task kind rather than across kinds,
and each factor is on or off rather than tuned.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    FATAL          a known result or argument makes the effect very unlikely
    SEVERE         serious obstacles that have defeated similar attempts
    MANAGEABLE     real risks, but groups have navigated them
    WEAK           the objections available are not strong

Choose honestly. If the objections are weak, say WEAK; inventing pessimism is
as useless to me as inventing optimism.

PART 2. THE STRONGEST PUBLISHED EVIDENCE AGAINST
Papers that tested something of this shape and found nothing, or found that an
apparent effect was an artefact. Null results, failed replications, and
critiques with identifiers. Negative results are under-published, so also name
cases where an effect quietly disappeared from the literature, where a method
stopped being used, or where a later benchmark revealed an earlier result was
measuring something else.

PART 3. THE CONFOUND THAT MANUFACTURES A FALSE POSITIVE
The most likely way this experiment returns a positive result that is not the
claimed effect. Be concrete and mechanical. Candidates worth checking: the
treatment arm receives more compute or more information than the control; the
baseline is untuned while the treatment is tuned; the unit of analysis is
wrong so precision is overstated; the held-out set is not actually held out;
selection on the outcome; a ceiling or floor that compresses the comparison;
the measure being a monotone function of something trivial. Say which of these
apply HERE and how they would show up.

PART 4. THE CONTROL THAT WOULD KILL IT
Given Part 3, the specific control arm that must be run for a positive result
to mean anything. Say what it costs relative to the main experiment and what
it would look like if the effect were real versus artefactual.

PART 5. WHY SIMILAR PROGRAMMES STOPPED
Where a research line of this shape has been abandoned, why. Distinguish
abandoned because it was refuted, abandoned because it was absorbed into
something else, and abandoned because the field moved on for reasons unrelated
to whether it worked. These have very different implications for someone
starting now.

PART 6. WHAT WOULD HAVE TO BE TRUE
State the conditions under which the claim COULD hold, as sharply as you can,
even if you judge them unlikely. If the effect is real only in a narrow
regime, name the regime. This is the part that tells a programme where to aim
if it proceeds anyway, and it is the one place in this report where a
constructive answer is wanted.

PART 7. HOW A NULL WOULD BE RECOGNISED
If the effect is not there, what would the experiment actually produce? Would
it look like a clean null, or like noise, or like a small positive that
survives to publication? Say what the programme should pre-commit to in order
to be able to recognise a null when it happens.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only: arXiv:2401.01234,
DOI 10.1000/xyz, https://github.com/example/repo. Ranges as quoted strings.
No markdown tables, no code fences. Plain text, PART headings as above,
verdict word alone on line one.
```

### Prompt 213: C1 method audit

```
METHOD AUDIT: WOULD THE RESULT MEAN ANYTHING
Question under audit: C1 -- Sealing an adaptive experiment

WHAT THIS IS

A research programme is designing a series of experiments. Before the science
is run, I want the methodology examined, because my concern is not that these
experiments fail -- a failure is a result -- but that they return a POSITIVE
that cannot be interpreted, which costs far more.

I am reviewing this design and did not write it. Tell me where it is wrong.

THE PROPOSAL AS STATED TO ME
In several of these experiments the next action depends on the previous
result: a synthesis loop refines on its own counterexamples, a curriculum
chooses the next task from the solver's performance. The proposal is to seal
the ALGORITHM, its initial inputs, seeds, budgets and stopping conditions
before execution, and let it adapt inside its executor while recording every
decision -- rather than freezing each future decision in advance.

WHAT I NEED ESTABLISHED
Whether an adaptive procedure sealed only at the policy level retains the
inferential guarantees that a fully pre-specified design has: controlled
error rates, an interpretable stopping rule, and immunity to the analyst's
choices. Fields that run adaptive designs under regulatory scrutiny have
confronted exactly this and have both machinery and cautionary tales.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    SOLVED         the field has established machinery for this and it works
    PARTIAL        machinery exists but with known gaps, and you can name them
    CONTESTED      practitioners disagree about the right approach
    UNSOLVED       there is no accepted answer and everyone improvises

PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO
Which disciplines have confronted this seriously, and what they settled on.
Give the specific machinery by name, with identifiers as arXiv:2401.01234 or
DOI 10.1000/xyz. Where fields disagree, say which does what and why they
diverged. Prefer fields that had to get this right under external scrutiny
over fields that adopted a convention by habit.

PART 3. THE FAILURE CASES, WITH RECEIPTS
Documented cases where getting this wrong invalidated a published result, or
where a correction changed a conclusion. Name them. This is the part I care
most about, because a programme is far more likely to adopt a convention that
sounds reasonable than to check whether it survives contact with the specific
failure it is meant to prevent.

PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN
Read the proposal as stated and identify what it does not handle. Be specific
and mechanical. If the proposal is sound as far as it goes, say so and name
the boundary beyond which it stops being sound.

PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE
The smallest set of rules a programme could adopt that would make its results
interpretable, ranked by how much each buys. Distinguish what is necessary
from what is merely best practice, because a programme that adopts twenty
rules will follow twelve.

PART 6. TOOLS AND CHECKS
Software, packages, or published checklists that implement any of this, with
bare URLs and a maturity note. If there are none and everyone hand-rolls it,
say that, because that is itself worth knowing.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only. Ranges as quoted
strings. No markdown tables, no code fences. Plain text, PART headings as
above, verdict word alone on line one.
```

### Prompt 214: C2 method audit

```
METHOD AUDIT: WOULD THE RESULT MEAN ANYTHING
Question under audit: C2 -- Charging the whole experiment

WHAT THIS IS

A research programme is designing a series of experiments. Before the science
is run, I want the methodology examined, because my concern is not that these
experiments fail -- a failure is a result -- but that they return a POSITIVE
that cannot be interpreted, which costs far more.

I am reviewing this design and did not write it. Tell me where it is wrong.

THE PROPOSAL AS STATED TO ME
Arms of these experiments differ structurally, not just in one parameter.
One arm may pay for retrieval over a store of prior failures, another for
training a decoder or a readout, another for oracle calls inside an inner
loop. The proposal is to charge every one of those costs to the arm that
incurs them and report a full cost vector before any comparison, rather than
equalising an outer wall clock or a count of outer iterations.

WHAT I NEED ESTABLISHED
How comparisons between structurally different methods are made fair in
practice, and what goes wrong when they are not. Whether cost-matched
comparison actually changes published conclusions, and by how much, in
fields that have re-run their own literature under matched budgets.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    SOLVED         the field has established machinery for this and it works
    PARTIAL        machinery exists but with known gaps, and you can name them
    CONTESTED      practitioners disagree about the right approach
    UNSOLVED       there is no accepted answer and everyone improvises

PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO
Which disciplines have confronted this seriously, and what they settled on.
Give the specific machinery by name, with identifiers as arXiv:2401.01234 or
DOI 10.1000/xyz. Where fields disagree, say which does what and why they
diverged. Prefer fields that had to get this right under external scrutiny
over fields that adopted a convention by habit.

PART 3. THE FAILURE CASES, WITH RECEIPTS
Documented cases where getting this wrong invalidated a published result, or
where a correction changed a conclusion. Name them. This is the part I care
most about, because a programme is far more likely to adopt a convention that
sounds reasonable than to check whether it survives contact with the specific
failure it is meant to prevent.

PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN
Read the proposal as stated and identify what it does not handle. Be specific
and mechanical. If the proposal is sound as far as it goes, say so and name
the boundary beyond which it stops being sound.

PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE
The smallest set of rules a programme could adopt that would make its results
interpretable, ranked by how much each buys. Distinguish what is necessary
from what is merely best practice, because a programme that adopts twenty
rules will follow twelve.

PART 6. TOOLS AND CHECKS
Software, packages, or published checklists that implement any of this, with
bare URLs and a maturity note. If there are none and everyone hand-rolls it,
say that, because that is itself worth knowing.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only. Ranges as quoted
strings. No markdown tables, no code fences. Plain text, PART headings as
above, verdict word alone on line one.
```

### Prompt 215: C3 method audit

```
METHOD AUDIT: WOULD THE RESULT MEAN ANYTHING
Question under audit: C3 -- What counts as one independent observation

WHAT THIS IS

A research programme is designing a series of experiments. Before the science
is run, I want the methodology examined, because my concern is not that these
experiments fail -- a failure is a result -- but that they return a POSITIVE
that cannot be interpreted, which costs far more.

I am reviewing this design and did not write it. Tell me where it is wrong.

THE PROPOSAL AS STATED TO ME
These experiments produce generations within a run, episodes within a
curriculum, repeats within a sealed specification, and separately seeded
runs. The proposal is to treat separately seeded runs as the independent
unit and to treat generations and episodes as within-unit structure, with
cross-run transfer conclusions placed in separately identified analyses.

WHAT I NEED ESTABLISHED
How often the unit of analysis is got wrong in search and learning
experiments, what the consequences are for reported precision, and which
conventions the relevant fields have actually converged on. Whether a
correct treatment changes conclusions that were drawn under an incorrect
one.

WHAT I NEED

PART 1. VERDICT, ON THE FIRST LINE
Exactly one of these words alone on the first line:

    SOLVED         the field has established machinery for this and it works
    PARTIAL        machinery exists but with known gaps, and you can name them
    CONTESTED      practitioners disagree about the right approach
    UNSOLVED       there is no accepted answer and everyone improvises

PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO
Which disciplines have confronted this seriously, and what they settled on.
Give the specific machinery by name, with identifiers as arXiv:2401.01234 or
DOI 10.1000/xyz. Where fields disagree, say which does what and why they
diverged. Prefer fields that had to get this right under external scrutiny
over fields that adopted a convention by habit.

PART 3. THE FAILURE CASES, WITH RECEIPTS
Documented cases where getting this wrong invalidated a published result, or
where a correction changed a conclusion. Name them. This is the part I care
most about, because a programme is far more likely to adopt a convention that
sounds reasonable than to check whether it survives contact with the specific
failure it is meant to prevent.

PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN
Read the proposal as stated and identify what it does not handle. Be specific
and mechanical. If the proposal is sound as far as it goes, say so and name
the boundary beyond which it stops being sound.

PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE
The smallest set of rules a programme could adopt that would make its results
interpretable, ranked by how much each buys. Distinguish what is necessary
from what is merely best practice, because a programme that adopts twenty
rules will follow twelve.

PART 6. TOOLS AND CHECKS
Software, packages, or published checklists that implement any of this, with
bare URLs and a maturity note. If there are none and everyone hand-rolls it,
say that, because that is itself worth knowing.

RULES

Separate verified from inferred; mark uncertain items UNCONFIRMED; never
invent an identifier, write IDENTIFIER UNKNOWN.

Do not use square brackets anywhere. Bare identifiers only. Ranges as quoted
strings. No markdown tables, no code fences. Plain text, PART headings as
above, verdict word alone on line one.
```
