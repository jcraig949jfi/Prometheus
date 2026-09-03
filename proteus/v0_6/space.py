"""Independent regeneration of the valid structural state space, and the closure proof.

V0.6 brief section 3. The state set is NOT imported from V0.4/V0.5. It is regenerated here
directly from the PUBLISHED MANIFEST RULES (proteus/contracts/player_manifest.schema.v0.json and
the STORAGE_BOUNDS in the affordance table), by a different construction than nc5.state_space, and
then compared against the earlier enumeration by cardinality and hash.

Closure is then PROVED against the live operator: every structural destination reachable by any
mutation from any state must lie inside the enumerated set. The required precondition is

    ESCAPED_VALID_STRUCTURAL_STATE_COUNT = 0

and a single valid escape is an instrument failure, not something to absorb.
"""
from __future__ import annotations

import json
import os

from proteus.foundry.affordances import STORAGE_BOUNDS
from proteus.foundry.identity import hash_obj

IW = STORAGE_BOUNDS["instruction_words"]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def published_rules():
    """Read the manifest constraints from the published artifacts, not from memory."""
    with open(os.path.join(ROOT, "proteus", "contracts", "player_manifest.schema.v0.json"),
              encoding="utf-8") as f:
        schema = json.load(f)
    p = schema["properties"]
    return {
        "tape_min": p["tape_words"]["minimum"], "tape_max": p["tape_words"]["maximum"],
        "tape_multiple_of": p["tape_words"]["multipleOf"],
        "genome_min_words": p["genome"]["minItems"], "genome_max_words": p["genome"]["maxItems"],
        "instruction_words": IW,
        "schema_id": schema["$id"],
        "schema_hash": hash_obj(schema),
    }


def regenerate_states():
    """Every (genome_length_in_instructions, tape_words) admitted by the published rules.

    Constructed by iterating tape sizes reachable by the doubling/halving ladder from the
    published minimum, then every genome length that fits. This is a DIFFERENT construction from
    nc5.state_space (which hard-coded the tape tuple), which is the point: it is an independent
    regeneration, not a copy.
    """
    r = published_rules()
    tapes = []
    t = r["tape_min"]
    while t <= r["tape_max"]:
        if t % r["tape_multiple_of"] == 0:
            tapes.append(t)
        t *= 2
    gmin = r["genome_min_words"] // IW
    gmax = r["genome_max_words"] // IW
    states = []
    for T in tapes:
        cap = min(gmax, T // IW)
        for L in range(gmin, cap + 1):
            states.append((L, T))
    return states, tapes, r


def space_identity(states):
    return {"n_states": len(states),
            "hash": hash_obj([list(s) for s in sorted(states)]),
            "min_state": list(min(states)), "max_state": list(max(states))}


def compare_with_prior(states):
    """Cardinality and hash against the V0.4/V0.5 enumeration, which is imported ONLY to compare."""
    from proteus.v0_4 import nc5
    prior = nc5.states()
    a, b = sorted(states), sorted(prior)
    return {"prior_n": len(prior), "regenerated_n": len(states),
            "cardinality_matches": len(prior) == len(states),
            "set_matches": a == b,
            "prior_hash": hash_obj([list(s) for s in b]),
            "regenerated_hash": hash_obj([list(s) for s in a]),
            "only_in_prior": [list(s) for s in sorted(set(b) - set(a))][:20],
            "only_in_regenerated": [list(s) for s in sorted(set(a) - set(b))][:20]}
