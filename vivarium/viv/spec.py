"""Experiment specification: canonical hashing and strict validation.

Two jobs, both narrow.

HASHING. The hash Vivarium stores must be the hash SFE seals, or the queue and
the ledger are talking about different objects. SFE computes
`content_hash(spec)` = "sha256:" + sha256 over JSON with sorted keys, no
whitespace and ensure_ascii=False (sfe/ids.py). That canonicalization is
reproduced here rather than imported, because Vivarium must run on hosts that
have no engine source; tests/test_spec_hash.py asserts byte-parity with
`sfe.ids.content_hash` wherever the engine IS present, so a drift is a test
failure and not a silent divergence.

VALIDATION. Strict and TOTAL: unknown keys are rejected, missing keys are
rejected, and nothing is ever filled in. A malformed experiment must not
silently mutate into a different experiment, so validation never returns a
repaired spec -- it returns the original or a list of reasons.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SPEC_VERSION = 1

#: Every executor kind Vivarium v0 is willing to run. An unlisted kind is a
#: validation failure, never a best-effort attempt.
KNOWN_KINDS = ("noop_v0", "evaluate_bitstring")

OUTCOMES = ("FALSIFIED", "SURVIVED", "INCONCLUSIVE")
OPS = ("==", "!=", "<", "<=", ">", ">=")

_TOP_LEVEL = {"spec_version", "experiment_kind", "world", "hypothesis",
              "prediction", "work", "outcome_rule", "pew", "notes"}
_REQUIRED = {"spec_version", "experiment_kind", "world", "hypothesis", "work"}


class SpecError(ValueError):
    """A specification Vivarium refuses to execute. Carries every reason."""

    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def spec_hash(spec: Any) -> str:
    """The content address SFE will seal at commit."""
    return "sha256:" + hashlib.sha256(canonical_bytes(spec)).hexdigest()


def _check_world(w: Any, r: list[str]) -> None:
    if not isinstance(w, dict):
        r.append("world must be an object")
        return
    extra = set(w) - {"name", "seed_root"}
    if extra:
        r.append("world has unknown keys: %s" % sorted(extra))
    if not isinstance(w.get("name"), str) or not w.get("name"):
        r.append("world.name must be a non-empty string")
    seed = w.get("seed_root")
    if not isinstance(seed, int) or isinstance(seed, bool):
        r.append("world.seed_root must be an integer")


def _check_work(work: Any, r: list[str]) -> None:
    if not isinstance(work, dict):
        r.append("work must be an object")
        return
    extra = set(work) - {"kind", "payload"}
    if extra:
        r.append("work has unknown keys: %s" % sorted(extra))
    if work.get("kind") not in KNOWN_KINDS:
        r.append("work.kind must be one of %s, got %r"
                 % (list(KNOWN_KINDS), work.get("kind")))
    if not isinstance(work.get("payload"), dict):
        r.append("work.payload must be an object")


def _check_outcome_rule(rule: Any, r: list[str]) -> None:
    """The rule is Archaeon's PRE-REGISTERED decision procedure, evaluated
    mechanically. Vivarium applies it; it does not author or amend it."""
    if not isinstance(rule, dict):
        r.append("outcome_rule must be an object")
        return
    extra = set(rule) - {"field", "op", "value", "if_true", "if_false"}
    if extra:
        r.append("outcome_rule has unknown keys: %s" % sorted(extra))
    if not isinstance(rule.get("field"), str) or not rule.get("field"):
        r.append("outcome_rule.field must be a non-empty string")
    if rule.get("op") not in OPS:
        r.append("outcome_rule.op must be one of %s" % list(OPS))
    if "value" not in rule:
        r.append("outcome_rule.value is required")
    for k in ("if_true", "if_false"):
        if rule.get(k) not in OUTCOMES:
            r.append("outcome_rule.%s must be one of %s" % (k, list(OUTCOMES)))


def _check_pew(pew: Any, r: list[str]) -> None:
    if not isinstance(pew, dict):
        r.append("pew must be an object")
        return
    extra = set(pew) - {"encounter_id", "players", "world_binding_id",
                        "required", "producer"}
    if extra:
        r.append("pew has unknown keys: %s" % sorted(extra))
    if not isinstance(pew.get("encounter_id"), str) or not pew.get("encounter_id"):
        r.append("pew.encounter_id must be a non-empty string "
                 "(Vivarium never mints scientific identity)")
    players = pew.get("players")
    ok_players = (isinstance(players, list) and players
                  and all(isinstance(p, str) and p for p in players))
    if not ok_players:
        r.append("pew.players must be a non-empty list of player ids")
    if "required" in pew and not isinstance(pew["required"], bool):
        r.append("pew.required must be a boolean")
    if "producer" in pew and not isinstance(pew["producer"], dict):
        r.append("pew.producer must be an object")


def validate(spec: Any) -> Any:
    """Return `spec` unchanged, or raise SpecError listing every reason."""
    r: list[str] = []
    if not isinstance(spec, dict):
        raise SpecError(["experiment_spec must be a JSON object"])

    extra = set(spec) - _TOP_LEVEL
    if extra:
        r.append("unknown top-level keys: %s" % sorted(extra))
    missing = _REQUIRED - set(spec)
    if missing:
        r.append("missing required keys: %s" % sorted(missing))

    if spec.get("spec_version") != SPEC_VERSION:
        r.append("spec_version must be %s, got %r"
                 % (SPEC_VERSION, spec.get("spec_version")))
    if not isinstance(spec.get("experiment_kind"), str) or \
            not spec.get("experiment_kind"):
        r.append("experiment_kind must be a non-empty string")
    if not isinstance(spec.get("hypothesis"), str) or not spec.get("hypothesis"):
        r.append("hypothesis must be a non-empty string")

    if "world" in spec:
        _check_world(spec["world"], r)
    if "work" in spec:
        _check_work(spec["work"], r)
    if "prediction" in spec and not isinstance(spec["prediction"], dict):
        r.append("prediction must be an object")
    if "outcome_rule" in spec:
        _check_outcome_rule(spec["outcome_rule"], r)
    if "pew" in spec:
        _check_pew(spec["pew"], r)
    if "notes" in spec and not isinstance(spec["notes"], str):
        r.append("notes must be a string")

    if r:
        raise SpecError(r)
    return spec


def apply_outcome_rule(spec: dict, result: dict) -> tuple:
    """Evaluate the pre-registered rule over the executor's result.

    Returns (outcome, provenance). Absent rule, or a field the result does not
    carry, yields INCONCLUSIVE -- Vivarium does not invent an adjudication and
    does not treat a missing measurement as a negative one.
    """
    rule = spec.get("outcome_rule")
    if rule is None:
        return "INCONCLUSIVE", {"rule": None,
                                "reason": "no_outcome_rule_declared"}
    field = rule["field"]
    if not isinstance(result, dict) or field not in result:
        return "INCONCLUSIVE", {"rule": rule, "reason": "field_absent",
                                "field": field}
    observed, want, op = result[field], rule["value"], rule["op"]
    try:
        if op == "==":
            hit = observed == want
        elif op == "!=":
            hit = observed != want
        elif op == "<":
            hit = observed < want
        elif op == "<=":
            hit = observed <= want
        elif op == ">":
            hit = observed > want
        else:
            hit = observed >= want
    except TypeError as exc:
        return "INCONCLUSIVE", {"rule": rule, "reason": "uncomparable",
                                "detail": str(exc), "observed": observed}
    return (rule["if_true"] if hit else rule["if_false"]), {
        "rule": rule, "observed": observed, "predicate_held": hit}
