"""`eca_rule_eval_v1` -- a thin wrapper around Herakles's radius-1 library.

The library is `herakles/eca/` and it owns every convention: the neighbourhood
bit order, the periodic ring, the rule numbering, and the definition of
TERMINAL BEHAVIOUR (the lattice after exactly `steps` updates, over every one
of the 2^n_cells initial configurations -- not the trajectory). Nothing here
decides any of that, and where the library refuses, this refuses with it.

WHAT THIS KIND MEASURES, AND WHY THAT AND NOT A SCORE. The library's own
observable is `behaviour(rule, n_cells, steps)`: the complete terminal
behaviour on the declared scope. Two rules with identical output there are
behaviourally indistinguishable and, in the library's own words, "must not be
counted as two tasks". So the wrapper reports that observable's digest and the
equivalence class it falls in, because those are what the library computes and
what `class_map_fixture.json` is keyed to.

IT DOES NOT SCORE THE RULE AGAINST A TARGET. A scoring rule would need a target
and a metric, and neither is in the library or in any spec Herakles has handed
over -- `assay_alpha.json` names the kind and pins the scope, but it is an
assay RESULT, not a payload/result contract. Inventing the missing half here
would be Vivarium deciding what H5 measures, which is the one thing this seat
exists not to do. The gap is named in the report and in the kind's note; adding
a scored variant later is a NEW kind name, never a flag on this one.

THE FIXTURE IS THE ANCHOR. `class_map_fixture.json` declares 224 classes over
256 rules at n_cells=7, steps=8, and the tests assert this wrapper reproduces
its class assignment exactly -- including the two degenerate groups Herakles
names (240 with 15/180/210, and 170 with 85/154/166).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

#: The scope the class-map fixture was computed over. A payload that names a
#: different one is legal and is simply not comparable with the fixture, which
#: the result says out loud rather than leaving to be assumed.
FIXTURE_SCOPE = {"n_cells": 7, "steps": 8}


class EcaUnavailable(RuntimeError):
    """herakles.eca is not importable on this host."""


def _eca():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    try:
        from herakles.eca import core                        # noqa: PLC0415
    except Exception as exc:                                 # noqa: BLE001
        raise EcaUnavailable(
            "eca_rule_eval_v1 needs Herakles's radius-1 library "
            "(herakles/eca/core.py). Refusing to reimplement its rule "
            "numbering or its terminal-behaviour definition: %s" % exc) from exc
    return core


def _fixture():
    path = REPO / "herakles" / "eca" / "class_map_fixture.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run(payload: dict, *, seed: int) -> dict:
    """Evaluate one elementary CA rule on the declared scope.

    `seed` is accepted and DELIBERATELY UNUSED: the scope is every initial
    configuration, exhaustively, so there is nothing to sample and a seed could
    not change the answer. Reporting that explicitly is better than accepting a
    parameter that silently does nothing.
    """
    core = _eca()
    rule = payload["rule_number"]
    n_cells = payload["n_cells"]
    steps = payload["steps"]

    core.require_rule(rule)          # 0..255; the library's refusal
    core.require_lattice(n_cells)
    core.require_steps(steps)

    n_configs = 1 << n_cells
    digest = core.behaviour_digest(rule, n_cells, steps)

    # The class, computed over the SAME scope this payload declared. Recomputed
    # rather than looked up, so a payload on a scope the fixture never covered
    # still gets a real answer instead of a wrong one.
    classes = core.equivalence_classes(n_cells, steps)
    members = sorted(classes.get(digest, [rule]))

    fixture = _fixture()
    fixture_agrees = None
    fixture_class_members = None
    if fixture is not None:
        scope = fixture.get("scope") or {}
        on_fixture_scope = (scope.get("n_cells") == n_cells
                            and scope.get("steps") == steps)
        if on_fixture_scope:
            by_rule = fixture.get("rule_to_class") or {}
            cid = by_rule.get(str(rule), by_rule.get(rule))
            same = [int(r) for r, c in by_rule.items() if c == cid]
            fixture_class_members = sorted(same)
            fixture_agrees = fixture_class_members == members

    return {
        "rule_number": int(rule),
        "behaviour_digest": digest,
        "equivalence_class_members": members,
        "equivalence_class_size": len(members),
        "is_class_representative": members[0] == int(rule),
        "n_cells": int(n_cells),
        "steps": int(steps),
        "n_initial_configurations": int(n_configs),
        "on_fixture_scope": bool(fixture_agrees is not None),
        "fixture_class_agrees": fixture_agrees,
        "fixture_class_members": fixture_class_members,
        "radius": int(core.RADIUS),
        "scored_against_a_target": False,
        "executor": "eca_rule_eval_v1",
        "reproducibility": "BIT_DETERMINISTIC",
    }
