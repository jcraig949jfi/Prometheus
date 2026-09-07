"""WP-0e: the kind-generic spec builder.

The first builder (``specbuild.build``) was hard-wired to ``evaluate_bitstring``
and authored the outcome rule itself. That meant a template on any other kind
could be drawn and could never be built, which Herakles's pass surfaced as
"7 runnable, 0 buildable". This module builds a spec for ANY implemented kind
from three declared things and nothing else:

    the kind's parameter contract   (Vivarium's registry: exact names)
    the drawn parameters            (from the template's nested space)
    the template's declared science (outcome_rule; repeat for stateful kinds;
                                     hypothesis / prediction text)

Rules it enforces BEFORE anything is queued (the order's 0e-b/0e-c):

* the kind must be registered, implemented and ACTIVE;
* every kind parameter must be present -- nothing is defaulted, ever;
* no extra payload parameter is accepted;
* scalar types are checked against a declared per-kind type map;
* cross-axis constraints are checked (``len(bits) == length``);
* the outcome rule's field must exist in the kind's declared result and be a
  scalar; a vector field needs a declared reduction, which no kind offers yet;
* ``repeat`` is required when the kind is stateful and must satisfy Vivarium's
  own validator (spec v3); ``persist`` is refused for a stateless kind;
* the finished spec is validated by VIVARIUM'S validator, never a copy.

Legacy compatibility (0e-d): a ``bitstring.uniform.v0`` draw with no
template-declared rule produces a spec byte-identical to the old builder, so
every hash already published stays re-derivable.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Tuple

from . import specbuild
from .contract import ensure_viv_importable
from .specbuild import SpecInvalid

#: Declared result fields per kind, from the executors' return dicts
#: (SOURCES.md §C.3). Vivarium's WP-0f `result_schema` supersedes this map
#: when present on the Kind; until then this is Archaeon's declared copy and
#: a test asserts it against the executor source.
RESULT_FIELDS: Dict[str, Dict[str, type]] = {
    "evaluate_bitstring": {"bits": str, "score": float, "solved": bool,
                           "length": int},
    "random_walk_v0": {"position": float, "start_position": float,
                       "displacement": float, "steps": int,
                       "step_scale": float, "seed": int},
    "noop_v0": {"executed": bool},
}

#: Scalar parameter types per kind. `bool` is never accepted for a number.
PARAM_TYPES: Dict[str, Dict[str, Tuple[type, ...]]] = {
    "evaluate_bitstring": {"bits": (str,), "length": (int,)},
    "random_walk_v0": {"steps": (int,), "step_scale": (int, float)},
    "noop_v0": {},
}

RULE_KEYS = ("field", "op", "value", "if_true", "if_false", "if_indeterminate")
RULE_OPS = ("==", "!=", "<", "<=", ">", ">=")
RULE_BRANCHES = ("FALSIFIED", "SURVIVED", "INCONCLUSIVE")


def _kind(name: str):
    ensure_viv_importable()
    from viv import kinds as vk
    k = vk.get(name)
    if k is None:
        raise SpecInvalid("kind {!r} is not registered".format(name))
    if not k.implemented:
        raise SpecInvalid("kind {!r} has no executor".format(name))
    if getattr(k, "status", "ACTIVE") != "ACTIVE":
        raise SpecInvalid("kind {!r} is {}".format(name, k.status))
    return k


def result_fields(kind_name: str) -> Dict[str, type]:
    """Vivarium's declared result schema when it exists (WP-0f), else the
    local declared copy."""
    k = _kind(kind_name)
    rs = getattr(k, "result_schema", None)
    if rs:
        return dict(rs)
    if kind_name not in RESULT_FIELDS:
        raise SpecInvalid("no declared result schema for kind {!r}; Vivarium's "
                          "WP-0f result_schema or a local declaration is "
                          "required before a rule can reference a field"
                          .format(kind_name))
    return RESULT_FIELDS[kind_name]


def _check_payload(kind_name: str, k, params: Dict[str, Any]) -> Dict[str, Any]:
    want = set(k.params)
    have = {p for p in params if p != "seed_root"}
    missing = sorted(want - have)
    extra = sorted(have - want)
    if missing:
        raise SpecInvalid("kind {!r} requires {} and the draw did not supply "
                          "{}; nothing is defaulted".format(kind_name,
                                                             sorted(want), missing))
    if extra:
        raise SpecInvalid("kind {!r} does not accept {}".format(kind_name, extra))
    types = PARAM_TYPES.get(kind_name, {})
    payload = {}
    for p in sorted(want):
        v = params[p]
        if v is None:
            raise SpecInvalid("parameter {!r} is null: a destroyed value must be "
                              "supplied at admission, never guessed".format(p))
        if p in types:
            if isinstance(v, bool) or not isinstance(v, types[p]):
                raise SpecInvalid("parameter {!r} must be {} not {}"
                                  .format(p, "/".join(t.__name__ for t in types[p]),
                                          type(v).__name__))
        payload[p] = v
    # cross-axis constraints (C-6 / F-3): declared per kind, checked here
    if kind_name == "evaluate_bitstring":
        if set(payload["bits"]) - {"0", "1"}:
            raise SpecInvalid("bits must be a binary string")
        if len(payload["bits"]) != payload["length"]:
            raise SpecInvalid(
                "bits is {} characters but length is {}; the hidden target is "
                "derived from length, so a mismatch is two different experiments"
                .format(len(payload["bits"]), payload["length"]))
    return payload


def _check_rule(kind_name: str, rule: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(rule, dict) or set(rule) - set(RULE_KEYS + ("aggregate",)):
        raise SpecInvalid("outcome_rule keys must be {}".format(list(RULE_KEYS)))
    for key in RULE_KEYS:
        if key not in rule:
            raise SpecInvalid("outcome_rule is missing {!r}; the branch taken "
                              "when the rule cannot be evaluated is the "
                              "requester's declaration".format(key))
    if rule["op"] not in RULE_OPS:
        raise SpecInvalid("outcome_rule.op must be one of {}".format(RULE_OPS))
    for b in ("if_true", "if_false", "if_indeterminate"):
        if rule[b] not in RULE_BRANCHES:
            raise SpecInvalid("outcome_rule.{} must be one of {}".format(b, RULE_BRANCHES))
    fields = result_fields(kind_name)
    f = rule["field"]
    if f not in fields:
        raise SpecInvalid("outcome_rule.field {!r} is not a declared result "
                          "field of {!r} ({})".format(f, kind_name, sorted(fields)))
    ftype = fields[f]
    if ftype in (list, tuple, dict):
        raise SpecInvalid("outcome_rule.field {!r} is vector-valued; a vector "
                          "needs a declared reduction and no kind offers one "
                          "yet".format(f))
    v = rule["value"]
    if ftype is bool:
        if not isinstance(v, bool):
            raise SpecInvalid("outcome_rule.value for boolean field {!r} must "
                              "be a boolean".format(f))
    elif ftype in (int, float):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise SpecInvalid("outcome_rule.value for numeric field {!r} must "
                              "be a number".format(f))
    elif ftype is str and not isinstance(v, str):
        raise SpecInvalid("outcome_rule.value for string field {!r} must be a "
                          "string".format(f))
    out = {k: rule[k] for k in RULE_KEYS}
    if "aggregate" in rule:
        # Only meaningful (and only accepted by the validator) once Vivarium's
        # E16 lands. We pass it through when the local validator knows it.
        ensure_viv_importable()
        from viv import spec as vspec
        if hasattr(vspec, "AGGREGATES"):
            out["aggregate"] = rule["aggregate"]
        else:
            raise SpecInvalid("outcome_rule.aggregate is declared but this "
                              "Vivarium has no within-run aggregation (E16); "
                              "refusing rather than silently dropping it")
    return out


def encounter_id(kind_name: str, payload: Dict[str, Any], seed_root: int) -> str:
    if kind_name == "evaluate_bitstring":
        # byte-for-byte the legacy derivation, so old encounters stay recognisable
        return specbuild.encounter_id(dict(payload, seed_root=seed_root))
    blob = json.dumps({"kind": kind_name, "payload": payload,
                       "seed_root": int(seed_root)},
                      sort_keys=True, separators=(",", ":"), default=str)
    return "ENC-archaeon-" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def build_from_template(template: Dict[str, Any], params: Dict[str, Any], *,
                        pew_required: bool = True) -> Dict[str, Any]:
    """A complete, explicit spec for the template's kind from drawn params."""
    kind_name = template["kind"]
    k = _kind(kind_name)
    if "seed_root" not in params or params["seed_root"] is None:
        raise SpecInvalid("world.seed_root is required and was not drawn; a "
                          "template must declare it (constant, int_range, "
                          "choices or from_region)")
    sr = params["seed_root"]
    if isinstance(sr, bool) or not isinstance(sr, int):
        raise SpecInvalid("seed_root must be an integer")
    payload = _check_payload(kind_name, k, params)

    rule = template.get("outcome_rule")
    stateful = bool(getattr(k, "stateful", False))
    repeat = template.get("repeat")

    # Legacy path: the frozen baseline and every bitstring template without a
    # declared rule keep the old builder's exact spec (and therefore hash).
    if kind_name == "evaluate_bitstring" and rule is None and repeat is None:
        return specbuild.build(dict(payload, seed_root=sr),
                               pew_required=pew_required)

    if rule is None:
        raise SpecInvalid("template {!r} on kind {!r} declares no outcome_rule; "
                          "the rule is the requester's science and is never "
                          "authored by the builder".format(
                              template.get("template_id"), kind_name))
    rule = _check_rule(kind_name, rule)

    if stateful and repeat is None:
        raise SpecInvalid("kind {!r} is stateful; the template must declare "
                          "`repeat` (count, order, seed_derivation, state, "
                          "budget) so state policy is explicit".format(kind_name))
    if repeat is not None and repeat.get("state") == "persist" and not stateful:
        raise SpecInvalid("repeat.state=persist on a stateless kind would be a "
                          "declared choice quietly not happening")

    hyp = template.get("hypothesis") or (
        "template {} on kind {} with payload {}".format(
            template.get("template_id"), kind_name,
            json.dumps(payload, sort_keys=True, default=str)))
    pred = template.get("prediction")
    if pred is None:
        pred = {"basis": "declared by template {}".format(template.get("template_id")),
                "outcome_rule_field": rule["field"]}

    spec: Dict[str, Any] = {
        "spec_version": 3 if repeat is not None else specbuild.SPEC_VERSION,
        "world": {"seed_root": sr},
        "hypothesis": hyp,
        "prediction": pred,
        "work": {"kind": kind_name, "payload": payload},
        "outcome_rule": rule,
        "pew": {"required": bool(pew_required),
                "encounter_id": encounter_id(kind_name, payload, sr),
                "players": []},
    }
    if repeat is not None:
        spec["repeat"] = dict(repeat)
    return spec


def build_validated(template: Dict[str, Any], params: Dict[str, Any],
                    **kw) -> Dict[str, Any]:
    spec = build_from_template(template, params, **kw)
    specbuild.validate(spec)
    return spec
