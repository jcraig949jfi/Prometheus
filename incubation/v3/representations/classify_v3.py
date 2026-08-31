"""classify_v3.py — the preregistered artifact classifier, fixed before any run.

    MACRO              a word of domain primitives (extends an action alphabet)
    OPERATOR           a v2 search program (tuple starting STAGE/SEQ/ROUTE):
                       changes the organization of computation, not state identity
    ACTION_RESTRICTION a single-group lens: same joint problem over a pruned
                       alphabet — the effective decomposition is unchanged, so it
                       does NOT qualify as representational
    REPRESENTATIONAL   a lens with >= 2 groups: it changes the problem decomposition
                       presented to downstream machinery (object boundaries /
                       factorization). When a behavioral record is supplied, at
                       least two subtasks must actually have run (a structural claim
                       unexercised at runtime does not count).

The distinction is structural AND behavioral, executable, and contains no judgment
call at evaluation time.
"""
from __future__ import annotations


def classify(artifact, sub_halts=None):
    if isinstance(artifact, dict) and artifact.get("kind") == "macro":
        return "MACRO"
    if isinstance(artifact, tuple) and artifact and artifact[0] in ("STAGE", "SEQ",
                                                                    "ROUTE"):
        return "OPERATOR"
    groups = artifact["groups"] if isinstance(artifact, dict) else artifact
    if not (isinstance(groups, tuple) and groups
            and all(isinstance(g, tuple) for g in groups)):
        raise ValueError("unclassifiable artifact")
    if len(groups) < 2:
        return "ACTION_RESTRICTION"
    if sub_halts is not None:
        ran = [h for h in sub_halts if h != "noop"]
        if len(ran) < 2:
            return "ACTION_RESTRICTION"
    return "REPRESENTATIONAL"
