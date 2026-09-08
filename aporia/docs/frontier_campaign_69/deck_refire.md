# Re-fire deck -- the ten SUBSTITUTED Tier 5 fields

Prompts 101 to 110. Rationale in build_deck_refire.py.
Numbered from 101 so originals at 48 to 61 are never overwritten.

---

### Prompt 101: Automated Scientific Discovery reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Automated Scientific Discovery

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
the BACON family of discovery programs, and the general claim that a program
can rediscover physical laws from tabulated data

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

PySR on the Feynman symbolic-regression benchmark

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 102: Computational Models of Scientific Discovery reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Computational Models of Scientific Discovery

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
BACON, Langley's discovery program from the 1970s and 1980s, together with
its successors in the same programme such as GLAUBER, STAHL and DALTON

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

PySR on the Feynman benchmark with dimensional-analysis constraints

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 103: Machine Discovery reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Machine Discovery

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
AM, Lenat's Automated Mathematician, and its successor EURISKO

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

the symbolic baseline on the IMO-AG-30 geometry benchmark

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 104: Automated Conjecture Generation reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Automated Conjecture Generation

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
HR, Colton's automated theory formation system, and the earlier Graffiti
conjecture-making program

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

FunSearch on the cap set problem

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 105: Computational Creativity reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Computational Creativity

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
the evaluation frameworks the field built for itself, such as Colton's
creative tripod and Ritchie's criteria, applied to a generative system

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

CMA-MAE on the Rastrigin function via pyribs, which is a quality-diversity
benchmark rather than a creativity evaluation

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 106: Case-Based Reasoning reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Case-Based Reasoning

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
the classical CBR cycle of retrieve, reuse, revise and retain, as
implemented in systems such as CHEF, PROTOS or the jCOLIBRI framework

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

Legal-BERT holding retrieval on CaseHOLD, which is dense retrieval rather
than case-based reasoning

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 107: Analogical Reasoning reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Analogical Reasoning

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
the Structure-Mapping Engine of Falkenhainer, Forbus and Gentner, and the
structure-mapping theory it implements

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

a 2025 perceptual-uncertainty stress test of large reasoning models on
I-RAVEN-X

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 108: Computational Philosophy of Science reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Computational Philosophy of Science

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
ECHO, Thagard's connectionist model of explanatory coherence, and the theory
of explanatory coherence it implements

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

IMEC, a later Bayesian successor, rather than ECHO itself

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 109: Abductive Reasoning reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Abductive Reasoning

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
parsimonious covering theory as set out by Reggia, Nau and Wang, and the
diagnostic set-covering systems built on it

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

the copct library for robotic intention recognition

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```

### Prompt 110: Universal Darwinism reproducibility audit

```
REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: Universal Darwinism

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
the Weasel program from Dawkins, and the broader class of cumulative
selection demonstrations it belongs to

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

FunSearch on the cap set problem

That may have been the right call. If the original system genuinely cannot be
reproduced, routing me to a live modern proxy is helpful. But the report never
said the original was irreproducible, so I cannot tell whether it was a
judgement or a preference, and the difference matters to me. This prompt asks
the question the previous one did not.

THE ANSWER I NEED, IN SIX PARTS

PART 1. VERDICT, IN THE FIRST LINE
Begin with exactly one of these words on its own line, and nothing else on
that line:

    REPRODUCIBLE
    REPRODUCIBLE_WITH_EFFORT
    NOT_REPRODUCIBLE
    UNCERTAIN

REPRODUCIBLE means source or a faithful reimplementation exists, runs on
current hardware, and a published number exists to check against.
REPRODUCIBLE_WITH_EFFORT means it could be rebuilt from the published
description in a bounded amount of work, and you should say how much.
NOT_REPRODUCIBLE means it cannot, and you should say precisely what is
missing. UNCERTAIN means you could not establish it either way, which is a
legitimate answer and better than a guess.

A verdict of NOT_REPRODUCIBLE is a genuinely useful answer to me. Do not
avoid it. Do not soften it into a recipe for something else.

PART 2. THE ARTEFACT TRAIL
What actually survives of this system. Original source code, and where it is
now, with a bare URL if one exists. Later reimplementations, by whom, in what
language, and whether they claim faithfulness or merely inspiration. Archived
copies, museum collections, university FTP remnants, code appendices in
theses. If the source is lost, say so and say when it was last known to
exist. Mark anything you could not confirm as UNCONFIRMED rather than
dropping it.

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The specific claim in the original publications that a reproduction would
have to match: the number of laws rediscovered, the concepts generated, the
conjectures produced, the accuracy achieved. Give the exact figure and the
citation with an arXiv id or a DOI. If the original papers report no number a
reproduction could be checked against, say that plainly, because that alone
makes the system irreproducible in the sense I care about, whatever survives
of the code.

PART 4. WHAT WOULD BREAK A REPRODUCTION
Dependencies on vanished hardware or languages, Lisp machine primitives,
interactive human input during the run, hand-tuned parameters never
published, datasets never released, or evaluation done by the authors'
judgement rather than by a rule. Be specific about which of these apply here.

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
Many systems of this era were challenged after publication, sometimes
decisively. Who criticised this one, on what grounds, and how did the
challenge resolve. Where a re-examination found that a published result
depended on hand-holding, on the representation chosen, or on the authors'
own interpretation, say so directly and cite it. This part is as important to
me as the verdict.

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Only now, and only if PART 1 was NOT_REPRODUCIBLE or UNCERTAIN, name the
closest live substitute, and say explicitly what it does NOT capture about
the original. If PART 1 was either REPRODUCIBLE verdict, give the
reproduction recipe instead: exact software, parameters, replicate count,
compute cost, and the number from PART 3 to compare against.

RULES

Answer about the named system. Do not substitute a modern system in PARTS 1
through 5; PART 6 is the only place a substitute belongs, and only after a
negative verdict.

Do not invent repository URLs, arXiv numbers, DOIs or version numbers. If you
do not know an identifier, write IDENTIFIER UNKNOWN. If you cannot confirm a
claim, write UNCONFIRMED beside it.

Do not use square brackets anywhere in the output, for any purpose. Write
identifiers bare: arXiv:2401.01234, DOI 10.1000/xyz,
https://github.com/example/repo. Never wrap anything in square brackets and
never use markdown link syntax. Write ranges as quoted strings such as
"1976 to 1984".

Plain text. No markdown tables, no code fences. Use the six PART headings
above, with the verdict word alone on the first line.
```
