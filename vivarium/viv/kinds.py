"""The execution-kind registry: what each kind of experiment REQUIRES.

One entry per executor kind. An entry declares the EXACT set of parameters the
kind consumes -- not a minimum, an exact set. Validation requires all of them
and rejects any extra, and no executor is permitted a default for any of them.

WHY EXACT AND WHY NO DEFAULTS. `evaluate_bitstring` derived its hidden target
from sha256("target:{seed_root}:{length}"), and `length` defaulted to 24. A
spec that omitted it was accepted and then silently run against a
Vivarium-chosen landscape -- Vivarium supplying a scientific parameter, which
is the one thing this seat exists not to do. A missing parameter is now a
REJECTED SPECIFICATION. An absent value that means something (no controls, no
prediction) must be written explicitly, because "absent" and "empty" are
different experiments and only one of them was requested.

IMPLEMENTED vs EXTERNAL. `implemented=False` declares a kind whose contract is
known but whose executor does not live here. Such a row is admissible -- the
queue is a REGISTER, and a candidate registered before selection need not be
runnable today -- but executing it fails terminally with
EXECUTOR_NOT_IMPLEMENTED rather than silently doing something else.

OWNERSHIP. `owner` names the seat that owns an entry's content. Vivarium owns
the shape of this file and the two kinds it can execute; it does not own the
scientific meaning of another seat's parameters. An entry marked PROVISIONAL
was transcribed by Vivarium from what that seat's code actually emits, and is
theirs to confirm or correct.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet


@dataclass(frozen=True)
class Kind:
    kind: str
    #: The EXACT parameter names work.payload must carry. Not a minimum.
    params: FrozenSet[str]
    #: False = contract known, executor absent. Admissible, not runnable.
    implemented: bool
    owner: str
    note: str = ""
    provisional: bool = False

    def check(self, payload: dict) -> list:
        """Reasons this payload does not satisfy the contract. Empty = ok."""
        if not isinstance(payload, dict):
            return ["work.payload must be an object"]
        got = set(payload)
        reasons = []
        missing = sorted(self.params - got)
        if missing:
            reasons.append(
                "work.payload for kind %r is missing %s; every parameter that "
                "can change the result must be explicit (no executor default "
                "exists or is permitted)" % (self.kind, missing))
        extra = sorted(got - self.params)
        if extra:
            reasons.append(
                "work.payload for kind %r carries unknown parameter(s) %s; "
                "the contract is exact, and an unread parameter in a hashed "
                "spec is a channel, not a comment" % (self.kind, extra))
        return reasons


REGISTRY: Dict[str, Kind] = {}


def register(k: Kind) -> Kind:
    REGISTRY[k.kind] = k
    return k


# --------------------------------------------------------------- Vivarium's
register(Kind(
    kind="noop_v0",
    params=frozenset(),
    implemented=True,
    owner="vivarium",
    note="Exercises the whole queue -> SFE -> PEW loop with no science in it. "
         "Takes no parameters at all, so there is nothing it could default."))

register(Kind(
    kind="evaluate_bitstring",
    params=frozenset({"bits", "length"}),
    implemented=True,
    owner="vivarium",
    note="Delegates to the engine's own reference executor. `length` is a "
         "scientific parameter: the hidden target is derived from "
         "sha256('target:<seed_root>:<length>'), so two lengths are two "
         "landscapes. It used to default to 24."))


# --------------------------------------------------------------- Archaeon's
register(Kind(
    kind="archaeon.probe.v0",
    params=frozenset({"procedure", "probe_kind", "replicates", "worlds",
                      "players", "target", "hold_fixed", "controls"}),
    implemented=False,
    owner="archaeon",
    provisional=True,
    note="PROVISIONAL. Transcribed by Vivarium from archaeon/propose.py "
         "build_spec(); Archaeon owns this entry and should confirm or "
         "correct it. `controls` is REQUIRED and must be [] when there are "
         "none: a probe with no controls and a probe whose controls were "
         "forgotten are different experiments, and only an explicit empty "
         "list says which one was requested. No executor lives here, so a "
         "row of this kind registers and fails visibly if executed."))


def get(kind: str):
    return REGISTRY.get(kind)


def known() -> list:
    return sorted(REGISTRY)


def implemented() -> list:
    return sorted(k for k, v in REGISTRY.items() if v.implemented)
