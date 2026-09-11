"""
Cartesian Genetic Programming deck -- prompts 300 to 302.

WHY. CGP appears in the 109-dossier corpus only in passing, in three dossiers
(12 Genetic Programming, 66 Algorithm Discovery, 78 Indirect Encodings), always
as a tool some other method uses and never as the subject. No Miller citation
appears anywhere. That is a gap, and it is a badly placed one, because CGP sits
directly on three things this programme is actively arguing about:

  - a fixed-length integer genotype decoding to a variable-size GRAPH
    phenotype, which is the H5 question in a different substrate
  - large numbers of INACTIVE genes, and a long-standing claim that the
    resulting neutral drift is what makes the search work -- which is dossier
    84's neutrality axis and dossier 12's finding that structural introns
    provide neutral evolutionary pathways
  - reusable subgraphs and module acquisition, which is library learning
    (dossier 80) in a graph representation rather than a lambda calculus

Three prompts, all on the proven eight-part frontier template:

  300  CGP as a field: tooling, reproduction, negative results
  301  the neutrality claim specifically, stated NEUTRALLY as contested
  302  module acquisition and reuse, i.e. compression co-evolving with search

Prompt 301 is the one to write carefully. The claim that inactive genes and
neutral drift are causally responsible for CGP's performance is CONTESTED in
the literature, and the anchor must not assert it. It is stated as a claim
under adjudication, with the competing explanation named alongside it, so the
report is not told which answer is wanted.

    python aporia/docs/frontier_campaign_69/build_deck_cgp.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_deck import PREAMBLE, wrap, FENCE  # noqa: E402

ENTRIES = [
    (
        300,
        "Cartesian Genetic Programming",
        "Can a program be evolved as a directed graph encoded by a "
        "fixed-length string of integers, where most of the encoded nodes "
        "contribute nothing to the output, and does that representation "
        "search better than a tree-based one?",
        "The genotype is a fixed-length list of integers describing a grid of "
        "computational nodes. Each node's genes name its function, drawn from "
        "a declared function set, and the indices of the nodes or inputs that "
        "supply its arguments. Connections may only reach backwards, which "
        "makes the resulting graph acyclic by construction. A final set of "
        "genes names which nodes are the outputs. The phenotype is obtained "
        "by walking back from the output genes through whatever nodes are "
        "actually reachable, so nodes not on a path to an output are simply "
        "not executed. Those nodes are still carried in the genotype and are "
        "still mutated. The genotype is therefore fixed in length while the "
        "executed graph varies in size, and the same node can feed several "
        "consumers, so a subgraph computed once is reused rather than "
        "duplicated. Selection is usually a very small evolutionary "
        "strategy, commonly one parent and four offspring, with the rule "
        "that an offspring equal in fitness to the parent replaces it.",
        "The candidate is the integer genotype. What varies is the function "
        "and connection genes. What is judged is the behaviour of the graph "
        "that the output genes actually reach.",
        "Task fitness of the decoded graph, plus structural quantities that "
        "have their own literature: the number of active versus inactive "
        "nodes, and the fraction of mutations that change the genotype "
        "without changing the phenotype.",
    ),
    (
        301,
        "Neutrality and inactive genes in Cartesian Genetic Programming",
        "In a representation where most genes are not expressed, do mutations "
        "that change the genotype without changing behaviour actually help "
        "the search, or is the benefit usually attributed to them caused by "
        "something else?",
        "A CGP genotype carries many nodes that no output reaches. Mutations "
        "to those nodes change the genotype and leave the phenotype "
        "identical, so a population can move across genotype space at "
        "constant fitness. The selection rule reinforces this: an offspring "
        "whose fitness merely EQUALS the parent's replaces it, so drift is "
        "actively accepted rather than merely tolerated. One account holds "
        "that this drift is what makes CGP work -- inactive regions "
        "accumulate variation that is silent until a later mutation "
        "reconnects them, so the population escapes local optima along "
        "neutral paths rather than crossing fitness valleys. A competing "
        "account holds that the benefit is not neutrality as such but a "
        "consequence of how mutation interacts with the length and structure "
        "of the encoding, and that experiments claiming a neutrality effect "
        "have not separated the two. I do not know which account the "
        "evidence supports and I am not looking for either answer in "
        "particular.",
        "The candidate is a genotype in a region where many nodes are "
        "inactive. What varies is the proportion of inactive material and "
        "whether neutral moves are accepted. What is judged is search "
        "performance, and separately whether any advantage survives a "
        "control that removes neutrality while holding everything else "
        "fixed.",
        "Evaluations to reach a target fitness, and success rate within a "
        "budget, on a scale of counts and proportions. Alongside those, the "
        "neutral fraction itself, and any measure separating drift along a "
        "neutral network from the effect of encoding length or mutation "
        "rate.",
    ),
    (
        302,
        "Module acquisition and subgraph reuse in evolved graphs",
        "When an evolving graph representation is allowed to package a "
        "recurring subgraph as a single reusable unit, does the search "
        "improve, and is the improvement from the reuse or from the change "
        "in mutation behaviour that packaging causes?",
        "A plain CGP graph already reuses computation implicitly, because "
        "one node can feed several consumers. Module acquisition makes that "
        "explicit: a subgraph is encapsulated into a named module with its "
        "own inputs and outputs, added to the function set, and thereafter "
        "callable as a single node. Modules can be created, expanded back "
        "into their constituent nodes, and mutated as units. The stated "
        "motivation is the same as in library learning over lambda terms -- "
        "a recurring structure costs one symbol instead of many, so the "
        "search operates over larger steps. The complication specific to "
        "this setting is that encapsulating a subgraph also changes what "
        "mutation does: a single mutation to a module node now alters "
        "everything the module expands to, so the packaging changes the "
        "step distribution as well as the description length.",
        "The candidate is the genotype together with its current module set. "
        "What varies is which subgraphs have been packaged. What is judged "
        "is task fitness and the cost of reaching it.",
        "Evaluations to a target fitness against a no-module control at "
        "matched budget, plus the description length of solutions with and "
        "without modules. The measure that would separate the two "
        "explanations is whether an equivalent change in step size, without "
        "reuse, reproduces the effect.",
    ),
]


def build() -> str:
    out = [
        "# Cartesian Genetic Programming deck",
        "",
        "Prompts 300 to 302. Rationale in build_deck_cgp.py.",
        "Prompt 301 states a CONTESTED claim and names the competing account",
        "alongside it, so the report is not told which answer is wanted.",
        "",
        "---",
        "",
    ]
    for n, field, question, mechanism, candidate, measured in ENTRIES:
        body = PREAMBLE.format(
            field=field,
            question=wrap(question),
            mechanism=wrap(mechanism),
            candidate=wrap(candidate),
            measured=wrap(measured),
        )
        assert FENCE not in body, f"prompt {n} has a fence"
        assert "[" not in body and "]" not in body, f"prompt {n} has a bracket"
        out += [f"### Prompt {n}: {field}", "", FENCE, body.rstrip(), FENCE, ""]
    return "\n".join(out)


if __name__ == "__main__":
    deck = build()
    p = HERE / "deck_cgp.md"
    p.write_text(deck, encoding="utf-8")
    print(f"wrote {p} ({len(deck)} chars, {len(ENTRIES)} prompts, 300..302)")
