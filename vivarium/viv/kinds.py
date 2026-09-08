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

from .result_schema import Field as R
from .result_schema import (describe as describe_result,
                             reduction_supported, validate_result)


#: Lifecycle of a kind. RETIRED is not deletion: rows and fossils that named a
#: retired kind stay readable and keep their meaning, and the entry stays here
#: so an archaeologist reading a 2026-09 fossil can still learn what
#: `archaeon.probe.v0` meant. What RETIRED forbids is a NEW admission.
ACTIVE = "ACTIVE"
RETIRED = "RETIRED"


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
    #: ACTIVE | RETIRED. A retired kind is refused at ADMISSION and keeps its
    #: historical meaning for everything already recorded.
    status: str = ACTIVE
    #: Does the executor carry state between repeats? A spec may only declare
    #: repeat.state="persist" for a stateful kind -- otherwise "persist" would
    #: be a silent no-op: a declared scientific choice quietly not happening.
    stateful: bool = False
    #: Why it was retired, and what replaced it. Never blank when RETIRED.
    retired_note: str = ""
    retired_at: str = ""
    #: WP-0f. What the executor RETURNS: field -> result_schema.Field. Empty
    #: for a kind whose executor does not live here -- an external owner
    #: declares its own result, and guessing one would be a contract Vivarium
    #: is not entitled to write.
    result_schema: Dict[str, R] = field(default_factory=dict)

    @property
    def retired(self) -> bool:
        return self.status == RETIRED

    @property
    def declares_result(self) -> bool:
        return bool(self.result_schema)

    def check_result(self, result, *, truncation=None) -> dict:
        """Validate an executor's OUTPUT. Raises ResultSchemaError."""
        return validate_result(self.kind, self.result_schema, result,
                               truncation=truncation)

    def supports_reduction(self, field_name: str, reduction: str):
        """May an outcome rule reduce this output field this way?"""
        return reduction_supported(self.result_schema, field_name, reduction)

    def result_lines(self) -> list:
        return describe_result(self.result_schema)

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
         "Takes no parameters at all, so there is nothing it could default.",
    result_schema={
        "executed": R("boolean", note="always true; the loop ran"),
    }))

register(Kind(
    kind="evaluate_bitstring",
    params=frozenset({"bits", "length"}),
    implemented=True,
    owner="vivarium",
    note="Delegates to the engine's own reference executor. `length` is a "
         "scientific parameter: the hidden target is derived from "
         "sha256('target:<seed_root>:<length>'), so two lengths are two "
         "landscapes. It used to default to 24.",
    result_schema={
        "bits": R("string", note="the candidate as scored"),
        "score": R("number", finite=True,
                   note="fraction of positions matching the hidden target"),
        "solved": R("boolean", note="score >= 1.0"),
        "length": R("integer", note="the landscape length actually used"),
    }))


# --------------------------------------------------------------- Archaeon's
register(Kind(
    kind="archaeon.probe.v0",
    params=frozenset({"procedure", "probe_kind", "replicates", "worlds",
                      "players", "target", "hold_fixed", "controls"}),
    implemented=False,
    owner="archaeon",
    provisional=True,
    status=RETIRED,
    retired_at="2026-09-06",
    note="HISTORICAL MEANING, PRESERVED. A region-targeted re-interrogation of "
         "the sfe.candidate_score.v0 chart. `probe_kind` named the operation "
         "from Archaeon's fixed detector->probe table (RESAMPLE_REGION, "
         "REPLICATE_AT_COORDINATE, INTERPOLATE_BETWEEN, CROSS_REPLICATE, "
         "REPEAT_OUTLIER_CELL, BISECT_BOUNDARY); `target` gave the coordinate "
         "in both normalized and raw form; `worlds`/`players` the region; "
         "`hold_fixed` what the probe held constant; `replicates` how many "
         "times; `controls` the nearby conditions, [] meaning explicitly none. "
         "Any queue row or fossil naming this kind still means exactly that, "
         "and this entry exists so it stays readable.",
    retired_note="RETIRED 2026-09-06 by operator direction. No executor was "
         "ever written for it and none can be written faithfully: the "
         "sfe.candidate_score.v0 worlds it targets were scored by a harness "
         "Vivarium does not have -- candidate 6926509 scores 0.42289 in the "
         "corpus and 0.33333 under the engine's 24-bit reference executor, and "
         "0.42289 is not a multiple of 1/24 -- so any substitution would "
         "fabricate an execution that was not the one requested. Archaeon's "
         "producer already routes around it with a declared random.v0 draw "
         "over evaluate_bitstring. Its re-execution half is now served by "
         "`repeat` (spec v3); its region-targeting half is an SFE substrate "
         "request, not an executor kind. RETIRED refuses NEW admissions only."))


# ------------------------------------------------- primitives for `repeat`
register(Kind(
    kind="random_walk_v0",
    params=frozenset({"steps", "step_scale"}),
    implemented=True,
    owner="vivarium",
    stateful=True,
    note="A bench primitive, not a scientific claim. A deterministic 1-D walk: "
         "`steps` increments drawn from the repeat's derived seed, each scaled "
         "by `step_scale`. It exists because repeat.state has no observable "
         "meaning without a kind that HAS state -- under `reset` the repeats "
         "are independent draws, under `persist` they are one trajectory, and "
         "that difference is exactly what within-world serial autocorrelation "
         "reads. Available to templates; ADMITTING a template that uses it is "
         "the operator's act, never mine.",
    result_schema={
        "position": R("number", finite=True, note="position after this repeat"),
        "start_position": R("number", finite=True,
                            note="position this repeat began from; equals the "
                                 "previous position under state=persist"),
        "displacement": R("number", finite=True,
                          note="position - start_position"),
        "steps": R("integer", note="steps taken, echoing the declared param"),
        "step_scale": R("number", finite=True),
        "seed": R("integer", note="the REPEAT's derived seed, not the world's"),
    }))


# ------------------------------------------------- Herakles's, wrapped (C1)
register(Kind(
    kind="ca_density_v0",
    params=frozenset({"rule_hex", "radius", "n_cells", "steps", "n_ic",
                      "ic_density_set", "success_criterion"}),
    implemented=True,
    owner="herakles (library) / vivarium (wrapper)",
    stateful=False,
    note="A thin wrapper around herakles/evca (WP-C1). Vivarium owns the kind "
         "contract; Herakles owns the semantics -- the rule encoding, the "
         "neighbourhood bit order, the periodic boundary and the r=3-only "
         "refusal all come from core.py and none is decided here. The lattice "
         "state lives inside ONE execution, so nothing carries between "
         "repeats and stateful is False. `success_criterion` (at_T | stable) "
         "chooses which mask `accuracy` is scored under; BOTH are always "
         "reported, along with the two per-rule fixed-point facts that decide "
         "whether they can differ at all. `ic_density_set` is ordered, null "
         "meaning the unbiased ensemble; n_ic is ICs PER density.",
    result_schema={
        "accuracy": R("number", finite=True,
                      note="scored under the declared success_criterion"),
        "misclassified_ic": R("vector", element="integer",
                              bounds=(0, 64), reductions=("any", "count"),
                              note="IC indices, global across density blocks, "
                                   "ascending, bounded"),
        "spacetime_digest": R("string",
                              note="one declared space-time diagram: ic_index "
                                   "0 of the first block"),
        "success_criterion": R("string", note="echoed, so a reader cannot "
                                             "mistake which question was "
                                             "answered"),
        "accuracy_at_T": R("number", finite=True),
        "accuracy_stable": R("number", finite=True),
        "n_incorrect_at_T": R("integer"),
        "n_incorrect_stable": R("integer"),
        "mask_digest_at_T": R("string"),
        "mask_digest_stable": R("string"),
        "all_zeros_fixed": R("boolean", note="table entry 0"),
        "all_ones_fixed": R("boolean", note="table entry 127"),
        "criteria_agree": R("boolean",
                            note="whether at_T and stable selected the same "
                                 "ICs on this run"),
        "n_ic_total": R("integer", note="n_ic * len(ic_density_set)"),
        "n_cells": R("integer"),
        "steps": R("integer"),
        "witness_truncated": R("boolean"),
    }))


def get(kind: str):
    return REGISTRY.get(kind)


def known() -> list:
    return sorted(REGISTRY)


def implemented() -> list:
    return sorted(k for k, v in REGISTRY.items() if v.implemented)


def admissible() -> list:
    """Kinds a NEW row may name. Excludes retired ones."""
    return sorted(k for k, v in REGISTRY.items() if not v.retired)


def retired() -> list:
    return sorted(k for k, v in REGISTRY.items() if v.retired)
