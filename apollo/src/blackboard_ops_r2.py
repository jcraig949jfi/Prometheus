"""blackboard_ops_r2.py — R2-tier inference transformers.

Decomposition of hephaestus `tier_specialists/r2_chain_tracker.py` (a
monolithic answer-producer: `evaluate(prompt, candidates) -> scores`) into
the Branch C typed-transformer shape, per the 2026-05-29 forge handoff
(`apollo/pivot/apollo_forge_handoff_2026-05-29.md`, §4).

The point of the handoff's one-experiment falsification: Apollo's blackboard
substrate is tier-monocultured at R0-R1 (parse / extract / reduce / select).
Sequencing extractors never manufactures a higher-tier reasoning *operation*,
which mechanically explains the decorative-composition / flat-ceiling result.
This module adds the missing R2 operation.

Three ops; the MIDDLE one is the R2 atom the substrate lacked:

    parse_rules            R1 parse      problem_text -> rules, facts
    forward_chain          R2 OPERATION  rules, facts -> derived_facts   <-- keystone
    score_by_derivability  terminal      derived_facts, candidates -> answer

`forward_chain` performs an inference closure (modus ponens + modus tollens
to fixpoint), not extraction. Its load-bearing test is unambiguous: zero
`derived_facts` before the scorer reads it and accuracy collapses, because
the correct answer is only reachable by multi-hop derivation.

The grammar parse_rules accepts (single-token atoms, lowercased):
    "If <a> then <b>"   -> rule  a -> b
    "<a> is true"       -> fact  a
    "<a> is false"      -> fact  "not a"
Question clauses (multi-word, e.g. "Which of the following can be derived?")
do not match the single-token atom patterns and are ignored.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blackboard import blackboard_op, BlackboardState


_RULE_RE = re.compile(r"\bif\s+(\w+)\s+then\s+(\w+)", re.IGNORECASE)
_FACT_TRUE_RE = re.compile(r"^(\w+)\s+is\s+true$", re.IGNORECASE)
_FACT_FALSE_RE = re.compile(r"^(\w+)\s+is\s+false$", re.IGNORECASE)


# ── parse_rules (R1) ──────────────────────────────────────────────────


@blackboard_op(
    reads=["problem_text"],
    writes=["rules", "facts"],
    name="parse_rules",
)
def parse_rules(state: BlackboardState) -> BlackboardState:
    """Parse If-then rules and asserted facts into typed slots.

    Writes BOTH rules and facts — they are distinct typed representations
    (a rule base vs an assertion set), not redundant views of one source.
    parse_rules is an R1 parse; the R2 work happens in forward_chain.
    """
    rules: dict[str, list[str]] = {}
    facts: set[str] = set()
    # Split on sentence boundaries; the question clause is split off here.
    for raw in re.split(r"[.?!]", state.problem_text):
        clause = raw.strip()
        if not clause:
            continue
        mr = _RULE_RE.search(clause)
        if mr:
            premise = mr.group(1).lower()
            conclusion = mr.group(2).lower()
            rules.setdefault(premise, []).append(conclusion)
            continue
        mf = _FACT_FALSE_RE.match(clause)
        if mf:
            facts.add("not " + mf.group(1).lower())
            continue
        mt = _FACT_TRUE_RE.match(clause)
        if mt:
            facts.add(mt.group(1).lower())
            continue
    state.rules = rules
    state.facts = facts
    return state


# ── forward_chain (R2 — the keystone) ─────────────────────────────────


@blackboard_op(
    reads=["rules", "facts"],
    writes=["derived_facts"],
    precondition=lambda s: bool(s.rules) or bool(s.facts),
    name="forward_chain",
)
def forward_chain(state: BlackboardState) -> BlackboardState:
    """Fixpoint inference closure over the rule base. THE R2 OPERATION.

    Not extraction — this manufactures facts that appear nowhere in the
    surface text. Two inference patterns, applied to fixpoint:
      - modus ponens:  a in derived, rule a->b  =>  add b
      - modus tollens: "not b" in derived, rule a->b  =>  add "not a"

    The closure is the load-bearing intermediate: corrupt it before the
    scorer reads it and the answer is wrong, because the correct candidate
    is only reachable through multi-hop derivation, never stated directly.
    """
    derived = set(state.facts)
    rules = state.rules or {}
    changed = True
    while changed:
        changed = False
        for premise, conclusions in rules.items():
            # modus ponens
            if premise in derived:
                for c in conclusions:
                    if c not in derived:
                        derived.add(c)
                        changed = True
            # modus tollens
            for c in conclusions:
                if ("not " + c) in derived and ("not " + premise) not in derived:
                    derived.add("not " + premise)
                    changed = True
    state.derived_facts = derived
    return state


# ── score_by_derivability (terminal scorer) ───────────────────────────


@blackboard_op(
    reads=["derived_facts", "candidates"],
    writes=["candidate_scores", "selected_answer"],
    name="score_by_derivability",
)
def score_by_derivability(state: BlackboardState) -> BlackboardState:
    """Score each candidate by membership in the forward-chain closure.

    Reads derived_facts (the load-bearing R2 intermediate). A candidate
    is an atom token; it scores 1.0 iff it (or its negation form) is in
    the closure. Corrupt derived_facts and scoring is blind — the
    dependency the gauntlet tests.
    """
    if not state.candidates:
        return state
    derived = state.derived_facts or set()
    scores = []
    for c in state.candidates:
        atom = c.strip().lower()
        scores.append(1.0 if (atom in derived or ("not " + atom) in derived) else 0.0)
    state.candidate_scores = scores
    idx = max(range(len(scores)), key=lambda i: scores[i])
    state.selected_answer = state.candidates[idx]
    return state


# ── relations_from_facts (R2→R1 TYPE BRIDGE) ──────────────────────────
# Added 2026-06-10 after R2 Run 1 (pivot/r2_run1_findings_2026-06-10.md): the
# substrate could NOT wire forward_chain into op_build_ordering because
# derived_facts (set[str]) and relations (list[tuple]) share no slot — R2
# output was a dead-end except for the terminal scorer. This is the minimal
# typed adapter that makes cross-tier composition (R2 inference -> R1 ordering)
# EXPRESSIBLE for the first time.


@blackboard_op(
    reads=["derived_facts"],
    writes=["relations"],
    precondition=lambda s: bool(s.derived_facts),
    name="relations_from_facts",
)
def relations_from_facts(state: BlackboardState) -> BlackboardState:
    """Project comparison atoms from the forward-chain closure into typed
    relations. An atom of the form '<a>_gt_<b>' (a greater-than b) becomes the
    ordered pair (a, b) that op_build_ordering consumes.

    Single canonical output (relations). The bridge is load-bearing in a
    cross-tier composition: zero derived_facts and no relations are produced,
    so the downstream ordering collapses. Negations and non-comparison atoms
    are ignored — only the comparison projection crosses the bridge.
    """
    rels = []
    for fact in (state.derived_facts or set()):
        if fact.startswith("not ") or "_gt_" not in fact:
            continue
        a, _, b = fact.partition("_gt_")
        if a and b and "_gt_" not in b:
            rels.append((a, b))
    rels.sort()  # determinism (derived_facts is an unordered set)
    state.relations = rels
    return state


# ── Registry (additive; transformer/scorer roles for blackboard_evolve) ─


OP_REGISTRY_R2 = {
    "parse_rules": parse_rules,            # transformer
    "forward_chain": forward_chain,        # transformer (R2 keystone)
    "relations_from_facts": relations_from_facts,  # transformer (R2->R1 bridge)
    "score_by_derivability": score_by_derivability,  # scorer (terminal)
}
