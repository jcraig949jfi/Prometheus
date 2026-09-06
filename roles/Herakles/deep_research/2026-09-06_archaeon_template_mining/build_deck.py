"""Build the Archaeon template-mining deck.

One prompt per discipline cluster. Every prompt carries the SAME bench
description and the SAME output contract; only the field list changes. That is
deliberate: the answers have to be comparable across fields, and the bench
description is the part most likely to be got wrong if written 14 times.

The bench facts below are taken from source, not from recall:
  vivarium/viv/kinds.py          the three implemented executor kinds
  vivarium/tests/conftest.py     the spec v3 shape, outcome_rule, repeat
  archaeon/docs/ROADMAP.md:94    the template JSON schema

    python build_deck.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CLUSTERS = [
    ("Evolutionary substrates",
     ["Artificial Life (ALife)", "Open-Ended Evolution",
      "Evolutionary Computation", "Digital Evolution", "Machine Evolution"]),
    ("Diversity and illumination",
     ["Quality-Diversity (MAP-Elites)", "Novelty Search",
      "Illumination Algorithms", "Coevolution",
      "Minimal-Criterion Coevolution"]),
    ("Generative and developmental representations",
     ["Genetic Programming", "Artificial Chemistry", "Autocatalytic Sets",
      "Artificial Gene Regulatory Networks",
      "Evolutionary Developmental Systems (Evo-Devo)"]),
    ("Open-ended learning and architecture search",
     ["POET / Open-Ended Learning", "Autocurricula",
      "Population-Based Training", "Neural Architecture Search",
      "Meta-Learning"]),
    ("Intrinsic drives and creativity",
     ["Intrinsic Motivation", "Curiosity-Driven Exploration",
      "Artificial Curiosity", "Empowerment", "Computational Creativity"]),
    ("Automated discovery systems",
     ["Automated Scientific Discovery", "Machine Discovery",
      "AI Scientist systems", "Robot Scientists",
      "Automated Experimentation"]),
    ("Experimental design and falsification",
     ["Active Learning", "Optimal Experimental Design",
      "Bayesian Experimental Design", "Falsification-Based Search",
      "Meta-Science"]),
    ("Synthesis and logic",
     ["Program Synthesis",
      "Counterexample-Guided Inductive Synthesis (CEGIS)",
      "Inductive Logic Programming", "Automated Theorem Proving",
      "Proof Search"]),
    ("Testing and verification",
     ["Property-Based Testing", "Metamorphic Testing",
      "Counterexample-Guided Verification", "Formal Methods",
      "Search-Based Software Engineering"]),
    ("Model and law discovery",
     ["Symbolic Regression", "Equation Discovery", "Causal Discovery",
      "Scientific Machine Learning", "Computational Mathematics"]),
    ("Reasoning modes",
     ["Abductive Reasoning", "Inductive Reasoning", "Analogical Reasoning",
      "Case-Based Reasoning", "Automated Conjecture Generation"]),
    ("Knowledge discovery and serendipity",
     ["Knowledge Discovery", "Discovery Informatics",
      "Computational Serendipity", "Science of Science",
      "Algorithm Discovery"]),
    ("Learning to search, and machine minds",
     ["Learning-to-Search", "Learning-to-Optimize",
      "Artificial General Intelligence (AGI)", "ALife-Inspired AI",
      "Darwinian Neurodynamics"]),
    ("Evolutionary epistemology",
     ["Universal Darwinism", "Evolutionary Epistemology",
      "Computational Philosophy of Science",
      "Computational Models of Scientific Discovery"]),
]

BENCH = """
THE BENCH, EXACTLY AS IT IS TODAY

This section is ground truth taken from the bench's source code on 2026-09-06.
Do not assume any capability that is not listed here. Proposing an experiment
the bench cannot run is not a failure -- it is half the deliverable -- but it
must be LABELLED as such rather than assumed to work.

The bench executes sealed experiment specifications. A specification is exactly
the execution inputs and nothing else: no title, no notes, no free commentary.
Its fields are:

  spec_version   3
  world          an object carrying a single integer seed_root
  hypothesis     a sentence of prose, recorded, not interpreted
  prediction     optional, may be explicitly null
  work           an object with a kind name and a payload object
  outcome_rule   see below
  repeat         see below
  pew            optional linkage to a separate encounter subsystem

THE THREE EXECUTOR KINDS THAT EXIST. There are exactly three. Each declares the
EXACT set of payload parameters it consumes. Not a minimum -- an exact set.
A payload missing a parameter is a rejected specification, and a payload with
an extra parameter is also rejected. No executor is permitted a default for any
parameter, because a default means the bench would be silently choosing a
scientific value on the experimenter's behalf.

  noop_v0
      payload parameters: none at all
      Exercises the whole loop with no science in it.

  evaluate_bitstring
      payload parameters: bits, length
      Scores a bitstring against a hidden target. The target is derived by
      hashing the seed_root together with the length, so two different lengths
      are two different landscapes, not one landscape at two scales.

  random_walk_v0
      payload parameters: steps, step_scale
      A deterministic one-dimensional walk. Increments are drawn from the
      repeat's derived seed and scaled. This kind is STATEFUL: it is the only
      kind that carries state between repeats.

A fourth kind for region-targeted re-interrogation was retired on 2026-09-06
and cannot be admitted again.

THE OUTCOME RULE IS A SINGLE SCALAR COMPARISON. This is the tightest limit on
the bench and you should treat it as such. A rule names one field of the
result, one comparison operator, and one value, and maps the three possible
answers onto the verdicts SURVIVED, FALSIFIED and INCONCLUSIVE. There is no
conjunction, no disjunction, no expression over two fields, no aggregation
across repeats, and no ordering or trend test. Any experiment whose conclusion
requires comparing two arms, fitting a curve, or aggregating a distribution
cannot express its own verdict on this bench today.

REPEAT SEMANTICS. A repeat block declares a count, an order (sequential), a
seed derivation (each repeat's seed is derived by hashing the root with the
index), a state discipline, and a budget in seconds and observations. State is
either reset, meaning each repeat starts clean, or persist, meaning the
executor carries state forward. Persist may only be declared for a kind that is
actually stateful, so today only the walk can use it.

ONE WORLD PER SPECIFICATION. The world is a single seed root. There is no
declared notion of a population, a generation, an archive, a niche grid, a
tournament, an opponent, or a second world to compare against.

WHAT THE BENCH RECORDS. Every run leaves a durable record with its inputs, its
seeds, and its verdict. Records are the unit that later analysis reads.
"""

CONTRACT = """
WHAT YOU MUST RETURN, AND IN WHAT FORM

Return TEMPLATES AND EXPANSION REQUESTS. Do not return an essay. Do not return
a literature review. Prose that is not inside one of the two blocks below is
wasted output. A short paragraph of framing at the very top is acceptable and
nothing else is.

For EACH of the fields listed above, answer the same two questions.

QUESTION ONE. What is the SMALLEST experiment this field would run on this
bench today? Smallest means: the least elaborate thing a working researcher in
that field would recognise as a real instance of their method, not a toy
gesture at it. Prefer an experiment that is characteristic of the field's
actual practice over one that merely fits the bench comfortably.

Express the answer as one template object, emitted exactly like this, with the
opening and closing markers on their own lines:

BEGIN_TEMPLATE
{
  "template_id": "<lowercase dotted identifier, ending in .v0>",
  "kind": "<executor kind name>",
  "param_space": {"<param>": {"choices": [..]},
                  "<param>": {"int_range": [lo, hi]}},
  "origin": {"source": "LITERATURE",
             "field": "<the field name from the list above>",
             "reference": "<the specific method, system or paper this comes from>",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "<one paragraph: what this measures, why this field would run it, and what a SURVIVED verdict would and would not license>"
}
END_TEMPLATE

Rules for the template object, all of which matter:

- The param_space keys must be EXACTLY the payload parameters of the kind you
  named. For evaluate_bitstring that is bits and length. For random_walk_v0
  that is steps and step_scale. For noop_v0 it is the empty object. If you
  propose a NEW kind, declare its exact parameter set and nothing beyond it.
- If the experiment can run on one of the three existing kinds, USE that kind.
  A template that fits the bench as it stands is more valuable than one that
  does not, because it can be drawn from immediately once admitted.
- If the field's smallest honest experiment CANNOT be expressed by the three
  existing kinds, then name a new kind anyway, in the same dotted style, and
  declare its exact parameters. Such a template is automatically an expansion
  request and that is a legitimate and expected outcome. Do not distort the
  field's method to squeeze it into the bitstring or the walk.
- The rationale must state what a SURVIVED verdict would NOT license. Be
  concrete about the inference the verdict does not support.

QUESTION TWO. What is the SMALLEST thing the bench lacks in order to run that
field's characteristic experiments? Smallest means one capability, stated so
precisely that an engineer could build it without asking a follow-up question.
Not "richer worlds". Not "better analysis".

Emit it exactly like this:

BEGIN_EXPANSION
FIELD: <the field name>
LACKS: <one sentence naming the single missing capability>
WHY: <two or three sentences: what experiment it unblocks and why no
      workaround on the current bench is faithful to the method>
SMALLEST_FORM: <the minimum version that would be useful, concretely: the
      parameters it would take and the field it would add to a result>
BLOCKS: <which of the fields in this prompt are blocked by this same gap>
EVIDENCE: <the specific published method or system that establishes this is
      how the field actually works, not how it might work>
END_EXPANSION

If two fields in this cluster are blocked by the SAME missing capability, emit
the expansion once and name both fields in BLOCKS. Do not pad the count.

EVIDENCE STANDARD. Ground every template in a method that has actually been
published and run, and name it in the reference field. Where you are inferring
what a field would do rather than reporting what it has done, say so inside the
rationale. Do not invent citations. A template whose reference you are unsure
of should say so plainly rather than name a plausible-looking source.

THE MOST USEFUL ANSWER is one where the smallest experiment is genuinely small
and genuinely characteristic, and where the missing capability is genuinely
one thing. Resist the urge to propose a grand experiment. The bench runs a
bitstring, a walk, and a noop. Meet it where it is.
"""


def main():
    out = ["# Deep Research Deck -- Archaeon template mining",
           "",
           "**Fired by:** Herakles, 2026-09-06",
           "**Purpose:** ROADMAP Challenge 2 delegation -- literature mining",
           "into PROPOSED templates for `archaeon/templates/inbox/`.",
           "**Prompts:** %d clusters covering the full discipline list."
           % len(CLUSTERS),
           "**Generated by:** `build_deck.py` in this directory.",
           ""]
    for i, (name, fields) in enumerate(CLUSTERS, start=1):
        body = []
        body.append("You are mining one cluster of research disciplines for "
                    "concrete, runnable experiment templates for a working "
                    "computational research bench. This is a design task "
                    "grounded in literature, not a literature survey.")
        body.append("")
        body.append("THE FIELDS IN THIS CLUSTER (%s):" % name)
        body.append("")
        for f in fields:
            body.append("  - " + f)
        body.append("")
        body.append(BENCH.strip())
        body.append("")
        body.append(CONTRACT.strip())
        body.append("")
        body.append("Work through the fields in the order listed. One "
                    "template per field, and as many expansion blocks as "
                    "there are genuinely distinct missing capabilities, "
                    "which may be fewer than the number of fields.")
        out.append("### Prompt %d: %s" % (i, name))
        out.append("")
        out.append("```")
        out.append("\n".join(body))
        out.append("```")
        out.append("")
    path = os.path.join(HERE, "deck.md")
    io.open(path, "w", encoding="utf-8", newline="").write("\n".join(out))
    print("wrote %s (%d prompts)" % (path, len(CLUSTERS)))
    print("fields covered: %d" % sum(len(f) for _, f in CLUSTERS))


if __name__ == "__main__":
    main()
