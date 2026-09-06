"""CHAOS: a template mutation operator that PROPOSES and never admits.

The operator's charter for random science: RNG, a sprinkle of chaos, human
input, LLM input, prior research. This is the sprinkle. It takes admitted
templates and writes perturbed copies into the inbox as PROPOSED, with
``origin.source = "CHAOS"`` and the parent ids recorded. A human decides
whether any of them enters the menu.

Three operators, all on the declared parameter space and nothing else --
chaos does not invent kinds, because a kind is an executor and executors are
Vivarium's:

    WIDEN     extend a numeric range or a choice list outward
    NARROW    the reverse: focus a space
    CROSS     take the world space from one parent and the payload space from
              another, when both share a kind

Every mutation is seeded and the seed is recorded, so a proposed template can
be regenerated from its parent(s) and seed. Chaos is reproducible chaos.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any, Dict, List, Optional
from pathlib import Path

from . import templates as T

OPERATORS = ("WIDEN", "NARROW", "CROSS")


def _seed(parent_ids: List[str], nonce: str) -> int:
    blob = "|".join(["archaeon.chaos.v0"] + sorted(parent_ids) + [nonce]).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")


def _widen(space: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for section, params in space.items():
        out[section] = {}
        for k, spec in params.items():
            s = dict(spec)
            if "int_range" in s:
                lo, hi = s["int_range"]
                span = max(hi - lo, 1)
                s["int_range"] = [int(lo - rng.randint(0, span // 2)),
                                  int(hi + rng.randint(0, span // 2))]
            elif "choices" in s and all(isinstance(c, int) for c in s["choices"]):
                cs = sorted(s["choices"])
                step = cs[-1] - cs[-2] if len(cs) > 1 else max(cs[-1] // 2, 1)
                s["choices"] = cs + [cs[-1] + step]
            out[section][k] = s
    return out


def _narrow(space: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for section, params in space.items():
        out[section] = {}
        for k, spec in params.items():
            s = dict(spec)
            if "int_range" in s:
                lo, hi = s["int_range"]
                span = max(hi - lo, 2)
                cut = rng.randint(0, span // 4)
                s["int_range"] = [int(lo + cut), int(hi - cut)]
            elif "choices" in s and len(s["choices"]) > 1:
                cs = list(s["choices"])
                cs.pop(rng.randrange(len(cs)))
                s["choices"] = cs
            out[section][k] = s
    return out


def mutate(parents: List[Dict[str, Any]], operator: str, *,
           nonce: str = "", directory: Optional[Path] = None) -> Path:
    """Write one PROPOSED template into the inbox. Returns its path."""
    if operator not in OPERATORS:
        raise ValueError("unknown chaos operator {!r}".format(operator))
    if not parents:
        raise ValueError("chaos needs at least one parent")
    pids = [p["template_id"] for p in parents]
    seed = _seed(pids, nonce)
    rng = random.Random(seed)

    if operator == "CROSS":
        if len(parents) < 2:
            raise ValueError("CROSS needs two parents")
        a, b = parents[0], parents[1]
        if a["kind"] != b["kind"]:
            raise ValueError("CROSS parents must share a kind; a kind is an "
                             "executor and chaos does not invent executors")
        space = {"world": a["param_space"].get("world", {}),
                 "payload": b["param_space"].get("payload", {})}
        kind = a["kind"]
    else:
        p = parents[0]
        space = (_widen if operator == "WIDEN" else _narrow)(p["param_space"], rng)
        kind = p["kind"]

    tid = "{}.chaos-{}-{}".format(pids[0].split(".")[0], operator.lower(),
                                   hashlib.sha256(str(seed).encode()).hexdigest()[:8])
    t = {"template_id": tid, "kind": kind, "param_space": space,
         "origin": {"source": "CHAOS", "proposed_by": "archaeon.chaos.v0",
                    "parents": pids, "operator": operator, "seed": seed,
                    "nonce": nonce},
         "rationale": ("Mechanical {} of {} under seed {}. Proposed, not "
                       "admitted; whether it enters the menu is a human "
                       "decision.".format(operator, pids, seed))}
    return T.propose(t, directory=directory)
