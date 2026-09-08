"""
Re-fire deck: the ten SUBSTITUTED Tier 5 fields, asked the question directly.

WHY THIS EXISTS. The preregistration in PREREGISTRATION_recipe_hatch.md
resolved INDETERMINATE at k=1, s=10. Ten Tier 5 dossiers gave a complete
reproduction recipe for a system OTHER than the one the prompt anchored on --
BACON became PySR on Feynman, AM became IMO-AG-30, HR and Weasel both became
FunSearch, ECHO became IMEC, structure-mapping became a 2025 language-model
stress test. None of them said the anchored system was irreproducible. They
just changed the subject.

That leaves the interesting question unasked. A substitution is consistent
with two very different states of the world:

    the historical system genuinely cannot be reproduced, and the report
    silently routed around it; or
    it CAN be reproduced, and the report preferred a more recent, more
    citable result.

These have opposite consequences for the corpus, and the original prompt
cannot separate them because it asked for "the single most reproducible and
informative experiment in this field", which a substitution answers
truthfully.

So this deck asks the narrow question instead, one field at a time, and makes
declining the FIRST-CLASS answer rather than an escape hatch at the end. It
also blocks the substitution move explicitly, which the original did not.

Numbered from 101 so the original dossiers at 48 to 61 are never overwritten
and the two answers can be compared side by side.

    python aporia/docs/frontier_campaign_69/build_deck_refire.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_deck import wrap, FENCE  # noqa: E402

# (number, original_prompt_number, field, the system that was anchored on,
#  what the original substituted instead)
REFIRES = [
    (101, 48, "Automated Scientific Discovery",
     "the BACON family of discovery programs, and the general claim that a "
     "program can rediscover physical laws from tabulated data",
     "PySR on the Feynman symbolic-regression benchmark"),
    (102, 49, "Computational Models of Scientific Discovery",
     "BACON, Langley's discovery program from the 1970s and 1980s, together "
     "with its successors in the same programme such as GLAUBER, STAHL and "
     "DALTON",
     "PySR on the Feynman benchmark with dimensional-analysis constraints"),
    (103, 50, "Machine Discovery",
     "AM, Lenat's Automated Mathematician, and its successor EURISKO",
     "the symbolic baseline on the IMO-AG-30 geometry benchmark"),
    (104, 51, "Automated Conjecture Generation",
     "HR, Colton's automated theory formation system, and the earlier "
     "Graffiti conjecture-making program",
     "FunSearch on the cap set problem"),
    (105, 52, "Computational Creativity",
     "the evaluation frameworks the field built for itself, such as Colton's "
     "creative tripod and Ritchie's criteria, applied to a generative system",
     "CMA-MAE on the Rastrigin function via pyribs, which is a "
     "quality-diversity benchmark rather than a creativity evaluation"),
    (106, 56, "Case-Based Reasoning",
     "the classical CBR cycle of retrieve, reuse, revise and retain, as "
     "implemented in systems such as CHEF, PROTOS or the jCOLIBRI framework",
     "Legal-BERT holding retrieval on CaseHOLD, which is dense retrieval "
     "rather than case-based reasoning"),
    (107, 57, "Analogical Reasoning",
     "the Structure-Mapping Engine of Falkenhainer, Forbus and Gentner, and "
     "the structure-mapping theory it implements",
     "a 2025 perceptual-uncertainty stress test of large reasoning models on "
     "I-RAVEN-X"),
    (108, 58, "Computational Philosophy of Science",
     "ECHO, Thagard's connectionist model of explanatory coherence, and the "
     "theory of explanatory coherence it implements",
     "IMEC, a later Bayesian successor, rather than ECHO itself"),
    (109, 59, "Abductive Reasoning",
     "parsimonious covering theory as set out by Reggia, Nau and Wang, and "
     "the diagnostic set-covering systems built on it",
     "the copct library for robotic intention recognition"),
    (110, 61, "Universal Darwinism",
     "the Weasel program from Dawkins, and the broader class of cumulative "
     "selection demonstrations it belongs to",
     "FunSearch on the cap set problem"),
]

TEMPLATE = """REPRODUCIBILITY AUDIT OF A SPECIFIC HISTORICAL SYSTEM
Field: {field}

WHAT I AM ASKING, AND IT IS NARROW

This is not a survey and not a field overview. I want one question answered
about one specific system, in as much concrete detail as the evidence
supports, and I want a plain NO if the answer is no.

The system:
{system}

The question: can that system, or a faithful reimplementation of it, be run
today by a competent programmer with ordinary resources, and reproduced
against a published result?

WHY I AM ASKING AGAIN

I asked about this field before, in an open-ended way, and the answer I got
back was a well-specified reproduction recipe for something else entirely:

{substituted}

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
"""


def build() -> str:
    out = [
        "# Re-fire deck -- the ten SUBSTITUTED Tier 5 fields",
        "",
        "Prompts 101 to 110. Rationale in build_deck_refire.py.",
        "Numbered from 101 so originals at 48 to 61 are never overwritten.",
        "",
        "---",
        "",
    ]
    for n, orig, field, system, substituted in REFIRES:
        body = TEMPLATE.format(
            field=field,
            system=wrap(system),
            substituted=wrap(substituted),
        )
        assert FENCE not in body, f"prompt {n} contains a fence"
        assert "[" not in body and "]" not in body, f"prompt {n} has a bracket"
        out += [f"### Prompt {n}: {field} reproducibility audit",
                "", FENCE, body.rstrip(), FENCE, ""]
    return "\n".join(out)


if __name__ == "__main__":
    deck = build()
    path = HERE / "deck_refire.md"
    path.write_text(deck, encoding="utf-8")
    print(f"wrote {path} ({len(deck)} chars, {len(REFIRES)} prompts)")
