"""
Extension deck: fields the 69 did not contain.

The source matrix has 69 entries because Herakles mined 69 disciplines. That
is a property of his mining run, not a census of the space. This file adds
prompts for fields the campaign itself showed to be missing, numbered from 70
so that prompt numbers stay stable and `--only` keeps working across both
decks.

Each entry here must justify its own existence. "It would be interesting" is
not a reason; the reason has to be a gap the corpus demonstrated.

    python aporia/docs/frontier_campaign_69/build_deck_ext.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_deck import PREAMBLE, wrap, FENCE  # noqa: E402

# ---------------------------------------------------------------------------
# Each entry: (number, field, why_it_is_here, question, mechanism, candidate,
#              measured)
# ---------------------------------------------------------------------------
EXTRA = [
    (
        70,
        "Evolving Cellular Automata for Collective Computation",
        # WHY. Flagged twice during the campaign and never covered by the 69.
        # Herakles' own critique of the Archaeon roadmap argues this substrate
        # should run FIRST, on the grounds that it is the only place in the
        # plan where the interesting object is not authored by the programme:
        # "the structure that solves the task is not in the table; it is in
        # what the lattice does over time. Nobody put it there."
        # herakles/specimens/spec-evca-density/ is the only spatial stateful
        # substrate in the repository and it is already recovered and verified.
        "Can a genetic algorithm discover a cellular automaton rule whose "
        "lattice performs a global computation that no local rule was told "
        "how to do, and what is the structure that actually does the "
        "computing?",
        "A one-dimensional binary cellular automaton has a lookup table over "
        "neighbourhoods of radius r, so for r = 3 the rule is a 128-bit "
        "string. Every cell updates synchronously from its own neighbourhood "
        "and nothing else; there is no global operation anywhere in the "
        "system. The density classification task asks the lattice to relax to "
        "all ones if the initial configuration had a majority of ones and to "
        "all zeros otherwise, which is a global property of the initial "
        "condition that no cell can see. A genetic algorithm evolves the rule "
        "table against a sample of random initial conditions scored by "
        "whether the lattice reached the correct uniform state within a step "
        "budget. The interesting result is not the fitness. It is that the "
        "successful rules were found, on inspection of their space-time "
        "diagrams, to work by forming regular domains, with the boundaries "
        "between domains acting as travelling particles that carry "
        "information across the lattice and interact when they collide. That "
        "particle-and-collision structure is a description nobody encoded, in "
        "a system whose entire specification is a bit string.",
        "The candidate is the rule table itself, a bit string of length 2 to "
        "the power of the neighbourhood size, typically 128 bits. What varies "
        "is which bits are set. What is judged is the fraction of random "
        "initial conditions the resulting lattice classifies correctly.",
        "Classification accuracy over a sample of initial conditions, on a "
        "scale from 0 to 1, at a stated lattice size, density distribution and "
        "step budget. Separately and more importantly, whether particles and "
        "domains can be identified in the space-time diagrams, and by what "
        "method.",
    ),
]


def build() -> str:
    out = [
        "# Frontier Practitioner deck -- extension",
        "",
        "Prompts 70 and up: fields the original 69 did not contain.",
        "Numbering continues from deck.md so --only works across both.",
        "Rationale for each entry is in build_deck_ext.py::EXTRA.",
        "",
        "---",
        "",
    ]
    # The rationale for each entry is a COMMENT above it, not a tuple field,
    # so the tuple is exactly (number, field, question, mechanism, candidate,
    # measured). Indexing it as though `why` were an element shifted every
    # field by one and raised IndexError on the last.
    for n, field, question, mechanism, candidate, measured in EXTRA:
        body = PREAMBLE.format(
            field=field,
            question=wrap(question),
            mechanism=wrap(mechanism),
            candidate=wrap(candidate),
            measured=wrap(measured),
        )
        assert FENCE not in body, f"prompt {n} contains a fence"
        assert "[" not in body and "]" not in body, f"prompt {n} has a bracket"
        out += [f"### Prompt {n}: {field}", "", FENCE, body.rstrip(), FENCE, ""]
    return "\n".join(out)


if __name__ == "__main__":
    deck = build()
    path = HERE / "deck_ext.md"
    path.write_text(deck, encoding="utf-8")
    print(f"wrote {path} ({len(deck)} chars, {len(EXTRA)} prompts)")
