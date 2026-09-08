"""
Build the 69-prompt Frontier Practitioner deck from Herakles' MATRIX.json.

Aporia campaign, opened 2026-09-07 at James's direction.

Purpose, and how it differs from the Herakles deck it draws on:
Herakles mined 69 disciplines into experiment templates SHAPED FOR the
Vivarium/SFE bench, and the shaping is exactly what made them thin -- the
bench has three executors and a single-scalar outcome rule, so every
template was compressed until it fit. This deck asks the opposite question
of the SAME 69 fields, deliberately UNSHAPED by the bench:

    if I wanted to become a practitioner at the frontier of this field in
    2026 and run real experiments in silico, what would I read, install,
    download, reproduce, and build?

The deliverable is depth: primary papers with identifiers, maintained
source code with URLs, datasets and benchmarks with access routes, one
fully specified reproduction recipe, and an honest catalogue of what has
failed.

Deck contract (the dispatcher parser is literal, see
aporia/scripts/gemini_deep_research_dispatch.py::parse_deck):
  - each prompt is "### Prompt N: <title>" at line start
  - the body is the FIRST fenced block after the heading
  - the body must contain no triple backtick

Output-format constraint (doctrine, measured 2026-09-06): Deep Research
rewrites the finished report and replaces square-bracketed spans with
citation markers. Anything bracketed is destroyed. So the prompt forbids
square brackets outright and asks for bare identifiers.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
MATRIX = (REPO / "roles/Herakles/deep_research/2026-09-06_archaeon_template_mining"
                 "/expansion_pass/MATRIX.json")

FENCE = "`" * 3

# ---------------------------------------------------------------------------
# Firing order. Ranked by Aporia, 2026-09-07.
#
# Rank criteria, in order of weight:
#   1. Can unplanned structure appear in this field's substrate at all?
#      (Herakles' own critique: an authored landscape can only return what
#      was authored. The fields where the interesting object is NOT
#      authored go first.)
#   2. Is there mature, installable, actively maintained code, so that a
#      reproduction recipe is a real deliverable and not a wish?
#   3. Mechanism-family leverage -- an early report on a field whose
#      SHARED_MECHANISM covers many of the 69 buys more than a singleton.
# ---------------------------------------------------------------------------
ORDER = [
    # Tier 1 -- emergence-bearing substrates with live tooling
    "digitevol.avida.v0",
    "map.elites.v0",
    "openended.novelty.v0",
    "alife.tierra.v0",
    "novelty.search.v0",
    "poet_paired_coevolution.v0",
    "coevolution.parasites.v0",
    "evodevo.bias.v0",
    "rbn.attractor.v0",
    "symbolic_regression_gp.v0",
    "equation_discovery_sindy.v0",
    "lgp.bloat.v0",
    # Tier 2 -- discovery and design machinery with real code
    "ai_scientist_training.v0",
    "causal_discovery_pc.v0",
    "bayesian_utility.v0",
    "d_optimal_design.v0",
    "query_by_committee.v0",
    "nas_bench_evaluation.v0",
    "maml_few_shot.v0",
    "l2o.meta.optimizer.v0",
    "pbt_hyperparam_schedule.v0",
    "machineevol.neat.v0",
    "illumination.grid.v0",
    "hide_and_seek_autocurriculum.v0",
    # Tier 3 -- intrinsic motivation, information, artificial chemistry
    "curiosity.v0",
    "intrinsic.v0",
    "artificial_curiosity.v0",
    "empowerment.v0",
    "mcc.bipartite.v0",
    "alife.tierra.soup.v0",
    "alchemy.collision.v0",
    "raf.detection.v0",
    "neurodynamics.attractor.evo.v0",
    "agi.mc.aixi.ctw.v0",
    # Tier 4 -- formal methods, synthesis, testing
    "cegis_boolean.v0",
    "program_synthesis_sketch.v0",
    "cegar.abstraction.loop.v0",
    "fm.bounded.model.check.v0",
    "eprover_superposition.v0",
    "lm_guided_proof.v0",
    "mil_predicate_invention.v0",
    "version_space_search.v0",
    "mt.relation.eval.v0",
    "pbt.stateful.walk.v0",
    "sbse.hillclimb.search.v0",
    "l2s.dagger.v0",
    "sciml_pinn_residual.v0",
    # Tier 5 -- discovery-systems history, knowledge, meta-science
    "bacon_equation_discovery.v0",
    "comp_sci_discovery.bacon.v0",
    "am_concept_generation.v0",
    "automated_conjecture_hr.v0",
    "creativity.v0",
    "computational_serendipity.v0",
    "discovery_informatics.v0",
    "knowledge_discovery.v0",
    "cbr_retrieval_cycle.v0",
    "structure_mapping.v0",
    "comp_phil_sci.echo.v0",
    "abduce_set_cover.v0",
    "evo_epistemology.bvsr.v0",
    "universal_darwinism.weasel.v0",
    "science_of_science.v0",
    "simulate_study.v0",
    "adam_yeast_growth.v0",
    "ada_thin_film.v0",
    "algorithm_discovery.v0",
    "evolcomp.fitness.v0",
    "computational_mathematics_walk.v0",
    "falsification_walk.v0",
]


def wrap(text: str, width: int = 76) -> str:
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width))
    return "\n".join(out)


PREAMBLE = """FRONTIER PRACTITIONER DOSSIER
Field: {field}

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
{question}

Mechanism as I currently understand it:
{mechanism}

What varies and what is judged:
{candidate}

What is measured:
{measured}

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
"""


def build() -> str:
    entries = json.loads(MATRIX.read_text(encoding="utf-8"))
    by_id = {e["TEMPLATE_ID"]: e for e in entries}

    missing = [t for t in ORDER if t not in by_id]
    extra = [t for t in by_id if t not in ORDER]
    assert not missing, f"ORDER names templates not in matrix: {missing}"
    assert not extra, f"matrix has templates not in ORDER: {extra}"
    assert len(ORDER) == 69, f"ORDER has {len(ORDER)} entries, expected 69"

    out = [
        "# Frontier Practitioner deck -- 69 fields",
        "",
        "Aporia campaign opened 2026-09-07. Built by build_deck.py from",
        "Herakles MATRIX.json. One prompt per field, fired in waves of three.",
        "Firing order and its rationale live in build_deck.py::ORDER.",
        "",
        "---",
        "",
    ]

    for n, tid in enumerate(ORDER, 1):
        e = by_id[tid]
        body = PREAMBLE.format(
            field=e["FIELD"],
            question=wrap(e["QUESTION"]),
            mechanism=wrap(e["MECHANISM"]),
            candidate=wrap(e["CANDIDATE"]),
            measured=wrap(e["MEASURED"]),
        )
        assert FENCE not in body, f"prompt {n} contains a fence"
        assert "[" not in body and "]" not in body, f"prompt {n} contains a bracket"
        out.append(f"### Prompt {n}: {e['FIELD']}")
        out.append("")
        out.append(FENCE)
        out.append(body.rstrip())
        out.append(FENCE)
        out.append("")

    return "\n".join(out)


if __name__ == "__main__":
    deck = build()
    path = HERE / "deck.md"
    path.write_text(deck, encoding="utf-8")
    print(f"wrote {path} ({len(deck)} chars, {len(ORDER)} prompts)")
