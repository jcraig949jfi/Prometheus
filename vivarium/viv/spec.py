"""The sealed execution specification: canonical hashing and strict validation.

    THE SEALED SPEC CONTAINS EXACTLY THE EXECUTION INPUTS.
    PROVENANCE LIVES OUTSIDE THE HASH.

That is the whole contract, and everything here enforces one half of it.

WHY. spec_hash is the substrate's grouping surface (Harmonia S13/T-B), and S14
found it is "a fixed point against an adversary who VARIES the spec, but not
against one who makes every spec identical". So anything hashed that does not
change what is executed is a channel by which the selecting policy leaks into
the sealed scientific record and splits the derived universe along the arm
boundary -- which would make "policy C beat policy A" unattributable to
selection. Conversely anything unhashed that DOES change execution is a hidden
difference between arms. Both directions are fatal; both are closed here.

REMOVED IN v2, having been measured to change spec_hash without changing what
is executed:
    notes             free text, read by nothing
    experiment_kind   free text, read by nothing
    world.name        author-supplied metadata. S14 burned a result on
                      trusting one. Vivarium now DERIVES the world name from
                      spec_hash (see world_name()), so it cannot be a channel.

EXPLICIT NULL, NEVER OMISSION. `prediction`, `outcome_rule` and `pew` must be
present, with an explicit null when they do not apply. An omitted prediction
and a declared absence of one are different experiments; only one of them was
requested, and the sealed spec should say which.

HASHING. SFE computes content_hash(spec) = "sha256:" + sha256 over JSON with
sorted keys, no whitespace, ensure_ascii=False (sfe/ids.py). That is
reproduced here rather than imported, because Vivarium must run on hosts with
no engine source; tests/test_spec.py asserts byte-parity wherever the engine IS
present, so drift is a test failure and not a silent divergence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from . import kinds as _kinds

SPEC_VERSION = 3
#: v2 stays ADMISSIBLE and keeps its meaning: it had no repeat concept, so a v2
#: spec is exactly one observation. That is v2's DEFINITION, not a default
#: Vivarium is choosing now. New specs must be v3.
LEGACY_SPEC_VERSIONS = (2,)
ACCEPTED_SPEC_VERSIONS = (2, 3)

OUTCOMES = ("FALSIFIED", "SURVIVED", "INCONCLUSIVE")
OPS = ("==", "!=", "<", "<=", ">", ">=")

#: Closed. Every key is an execution input; adding one is a decision about
#: what the sealed record means, not a convenience.
_TOP_LEVEL = {"spec_version", "world", "hypothesis", "prediction", "work",
              "outcome_rule", "pew", "repeat"}

#: Present on every v3 spec. `prediction`/`outcome_rule`/`pew` may be null but
#: may not be missing. `repeat` may NOT be null: one observation is
#: `{"count": 1, ...}` stated outright, because "I did not think about
#: repetition" and "I chose exactly one" are different experiments.
_REQUIRED_V3 = set(_TOP_LEVEL)
_REQUIRED_V2 = _REQUIRED_V3 - {"repeat"}

# ---------------------------------------------------------------- repeat ---
#: How the per-repeat seed is derived from (world.seed_root, index). CLOSED,
#: and never defaulted: Archaeon's own note is that reusing one seed across
#: repeats gives zero within-world variance and a unit that looks eligible
#: while carrying no information. Vivarium will not pick for them.
SEED_DERIVATIONS = ("sha256_index", "linear_index", "constant")

#: Only one order exists today, and it is stated rather than assumed: the
#: lag-1 features read a trajectory, so which observation is "next" is an
#: execution input.
REPEAT_ORDERS = ("sequential",)

#: Whether executor state survives between repeats. "persist" is only legal
#: for a kind that HAS state; otherwise the declaration would be a silent
#: no-op.
REPEAT_STATES = ("reset", "persist")

_REPEAT_KEYS = {"count", "order", "seed_derivation", "state", "budget"}
_BUDGET_KEYS = {"max_seconds", "max_observations"}

#: Fields that are provenance or design and must NEVER appear in a spec. Named
#: explicitly so the failure says WHY rather than only "unknown key". Mirrors
#: archaeon/vivqueue.py FORBIDDEN_SPEC_KEYS -- the same rule, enforced on both
#: sides of the seam.
_BANISHED = {
    "notes": "free text that nothing executes",
    "experiment_kind": "free text that nothing executes",
    "family_id": "comparison identity -- a queue column",
    "family": "comparison identity -- a queue column",
    "arm_id": "arm identity -- a queue column",
    "arm": "arm identity -- a queue column",
    "candidate_set_id": "candidate-set membership -- a queue column",
    "replication_of": "a design relation -- a queue column",
    "request_key": "request identity -- a queue column",
    "policy": "the selecting policy -- provenance, never hashed",
    "created_by": "provenance -- a queue column",
    "source_reason": "provenance -- a queue column",
    "source_evidence": "provenance -- a queue column",
    "spec_hash": "the hash may not be inside the object it hashes",
}


class SpecError(ValueError):
    """A specification Vivarium refuses to execute. Carries every reason."""

    def __init__(self, reasons: list):
        self.reasons = list(reasons)
        super().__init__("; ".join(self.reasons))


# --------------------------------------------------------------------------
# Hashing and derived execution identity
# --------------------------------------------------------------------------

def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def spec_hash(spec: Any) -> str:
    """The content address SFE will seal at commit."""
    return "sha256:" + hashlib.sha256(canonical_bytes(spec)).hexdigest()


def world_name(sealed_hash: str) -> str:
    """The SFE world name, DERIVED from execution identity.

    Author-supplied world names were an unhashed-looking policy channel and a
    trap for archaeology (S14). Deriving the name means two arms of one
    comparison running byte-identical specs produce byte-identical world names,
    so the name discriminates nothing an archaeologist should not already be
    reading off spec_hash.
    """
    if not sealed_hash.startswith("sha256:"):
        raise ValueError("expected a sha256: content hash")
    return "viv-" + sealed_hash[7:23]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def _check_world(w: Any, r: list) -> None:
    if not isinstance(w, dict):
        r.append("world must be an object")
        return
    extra = set(w) - {"seed_root"}
    if extra:
        if "name" in extra:
            r.append("world.name is not permitted: it is author-supplied "
                     "metadata inside the sealed hash, and Vivarium derives "
                     "the world name from spec_hash instead")
        other = sorted(extra - {"name"})
        if other:
            r.append("world has unknown keys: %s" % other)
    if "seed_root" not in w:
        r.append("world.seed_root is required and has no default")
    else:
        seed = w["seed_root"]
        if not isinstance(seed, int) or isinstance(seed, bool):
            r.append("world.seed_root must be an integer")


def _check_work(work: Any, r: list) -> None:
    if not isinstance(work, dict):
        r.append("work must be an object")
        return
    extra = set(work) - {"kind", "payload"}
    if extra:
        r.append("work has unknown keys: %s" % sorted(extra))
    kind_name = work.get("kind")
    if not isinstance(kind_name, str) or not kind_name:
        r.append("work.kind must be a non-empty string")
        return
    kind = _kinds.get(kind_name)
    if kind is None:
        r.append("work.kind %r is not a registered execution kind; admissible "
                 "kinds are %s. An unregistered kind has no parameter "
                 "contract, so nothing could check it was fully specified."
                 % (kind_name, _kinds.admissible()))
        return
    if kind.retired:
        # RETIRED refuses NEW admissions. Rows and fossils already naming it
        # keep their meaning; that is the point of retiring rather than
        # deleting the entry.
        r.append("work.kind %r is RETIRED (%s) and may not be named by a new "
                 "specification. %s Admissible kinds: %s"
                 % (kind_name, kind.retired_at, kind.retired_note,
                    _kinds.admissible()))
        return
    if "payload" not in work:
        r.append("work.payload is required (use {} for a kind that takes no "
                 "parameters)")
        return
    r.extend(kind.check(work["payload"]))


def _check_outcome_rule(rule: Any, r: list) -> None:
    """The requester's PRE-REGISTERED decision procedure.

    Vivarium evaluates it; it does not author, amend or complete it. That is
    why if_indeterminate is required: the branch taken when the rule cannot be
    evaluated is a scientific choice, and it was previously Vivarium's.
    """
    if not isinstance(rule, dict):
        r.append("outcome_rule must be an object or null")
        return
    allowed = {"field", "op", "value", "if_true", "if_false", "if_indeterminate"}
    extra = set(rule) - allowed
    if extra:
        r.append("outcome_rule has unknown keys: %s" % sorted(extra))
    if not isinstance(rule.get("field"), str) or not rule.get("field"):
        r.append("outcome_rule.field must be a non-empty string")
    if rule.get("op") not in OPS:
        r.append("outcome_rule.op must be one of %s" % list(OPS))
    if "value" not in rule:
        r.append("outcome_rule.value is required")
    for k in ("if_true", "if_false", "if_indeterminate"):
        if k not in rule:
            r.append("outcome_rule.%s is required and has no default; the "
                     "branch taken when the rule cannot be evaluated is the "
                     "requester's declaration, not Vivarium's" % k)
        elif rule[k] not in OUTCOMES:
            r.append("outcome_rule.%s must be one of %s" % (k, list(OUTCOMES)))


def _check_repeat(rep: Any, kind, r: list) -> None:
    """The four declared axes of a repeat: how many, in what order, how the
    seed moves, whether state survives, and what it is allowed to cost."""
    if not isinstance(rep, dict):
        r.append("repeat must be an object (use {\"count\": 1, ...} for a "
                 "single observation; it may not be null)")
        return
    extra = sorted(set(rep) - _REPEAT_KEYS)
    if extra:
        r.append("repeat has unknown keys: %s" % extra)
    missing = sorted(_REPEAT_KEYS - set(rep))
    if missing:
        r.append("repeat is missing %s; every axis of a repeat is an execution "
                 "input and none has a default" % missing)

    count = rep.get("count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        r.append("repeat.count must be an integer >= 1")
    if rep.get("order") not in REPEAT_ORDERS:
        r.append("repeat.order must be one of %s" % list(REPEAT_ORDERS))
    if rep.get("seed_derivation") not in SEED_DERIVATIONS:
        r.append("repeat.seed_derivation must be one of %s"
                 % list(SEED_DERIVATIONS))
    state = rep.get("state")
    if state not in REPEAT_STATES:
        r.append("repeat.state must be one of %s" % list(REPEAT_STATES))
    elif state == "persist" and kind is not None and not kind.stateful:
        r.append("repeat.state='persist' is not legal for kind %r, which is "
                 "stateless: nothing would carry between repeats and the "
                 "declaration would be a silent no-op" % kind.kind)

    budget = rep.get("budget")
    if not isinstance(budget, dict):
        r.append("repeat.budget must be an object")
        return
    bextra = sorted(set(budget) - _BUDGET_KEYS)
    if bextra:
        r.append("repeat.budget has unknown keys: %s" % bextra)
    bmissing = sorted(_BUDGET_KEYS - set(budget))
    if bmissing:
        r.append("repeat.budget is missing %s" % bmissing)
    secs = budget.get("max_seconds")
    if not isinstance(secs, (int, float)) or isinstance(secs, bool) or secs <= 0:
        r.append("repeat.budget.max_seconds must be a positive number")
    obs = budget.get("max_observations")
    if not isinstance(obs, int) or isinstance(obs, bool) or obs < 1:
        r.append("repeat.budget.max_observations must be an integer >= 1")
    elif isinstance(count, int) and not isinstance(count, bool) and count > obs:
        r.append("repeat.count (%s) exceeds repeat.budget.max_observations "
                 "(%s); the budget is a bound on what may run, so this request "
                 "could never complete" % (count, obs))


def _check_pew(pew: Any, r: list) -> None:
    if not isinstance(pew, dict):
        r.append("pew must be an object or null")
        return
    extra = set(pew) - {"encounter_id", "players", "world_binding_id",
                        "required", "producer"}
    if extra:
        r.append("pew has unknown keys: %s" % sorted(extra))
    if not isinstance(pew.get("encounter_id"), str) or not pew.get("encounter_id"):
        r.append("pew.encounter_id must be a non-empty string "
                 "(Vivarium never mints scientific identity)")
    players = pew.get("players")
    ok = (isinstance(players, list)
          and all(isinstance(p, str) and p for p in players))
    if not ok:
        r.append("pew.players must be a list of player ids (use [] for an "
                 "execution with no declared player)")
    if "required" in pew and not isinstance(pew["required"], bool):
        r.append("pew.required must be a boolean")
    if "producer" in pew and not isinstance(pew["producer"], dict):
        r.append("pew.producer must be an object")


def validate(spec: Any) -> Any:
    """Return `spec` UNCHANGED, or raise SpecError listing every reason.

    Never repairs, never defaults, never normalises: a normalised spec is a
    different experiment with the same name.
    """
    r: list = []
    if not isinstance(spec, dict):
        raise SpecError(["experiment_spec must be a JSON object"])

    for key, why in _BANISHED.items():
        if key in spec:
            r.append("%r is not permitted in the sealed spec (%s). It changes "
                     "spec_hash without changing what is executed, which "
                     "splits the derived universe along the policy boundary."
                     % (key, why))
    extra = sorted(set(spec) - _TOP_LEVEL - set(_BANISHED))
    if extra:
        r.append("unknown top-level keys: %s" % extra)
    required = (_REQUIRED_V2 if spec.get("spec_version") in LEGACY_SPEC_VERSIONS
                else _REQUIRED_V3)
    missing = sorted(required - set(spec))
    if missing:
        r.append("missing required keys: %s (declare an explicit null where "
                 "one does not apply; an omitted field and a declared absence "
                 "are different experiments)" % missing)
    if spec.get("spec_version") in LEGACY_SPEC_VERSIONS and "repeat" in spec:
        r.append("spec_version %s predates `repeat` and means exactly one "
                 "observation; a v2 spec carrying a repeat block is ambiguous. "
                 "Declare spec_version %s."
                 % (spec.get("spec_version"), SPEC_VERSION))

    version = spec.get("spec_version")
    if version not in ACCEPTED_SPEC_VERSIONS:
        r.append("spec_version must be one of %s (new specs should be %s), "
                 "got %r" % (list(ACCEPTED_SPEC_VERSIONS), SPEC_VERSION,
                             version))
    if not isinstance(spec.get("hypothesis"), str) or not spec.get("hypothesis"):
        r.append("hypothesis must be a non-empty string")

    if "world" in spec:
        _check_world(spec["world"], r)
    if "work" in spec:
        _check_work(spec["work"], r)
    if "repeat" in spec:
        _check_repeat(spec["repeat"],
                      _kinds.get((spec.get("work") or {}).get("kind")), r)
    if spec.get("prediction") is not None and \
            not isinstance(spec.get("prediction"), dict):
        r.append("prediction must be an object or null")
    if spec.get("outcome_rule") is not None:
        _check_outcome_rule(spec["outcome_rule"], r)
    if spec.get("pew") is not None:
        _check_pew(spec["pew"], r)

    # An implemented kind WILL be executed, so it must be execution-ready: an
    # experiment SFE can record needs an outcome, and Vivarium will not author
    # one. A non-implemented kind is registrable without being runnable.
    work = spec.get("work")
    if isinstance(work, dict):
        kind = _kinds.get(work.get("kind"))
        if kind is not None and kind.implemented and \
                spec.get("outcome_rule") is None:
            r.append("outcome_rule is required for executable kind %r: SFE "
                     "records an outcome for every observation, and Vivarium "
                     "does not author one" % kind.kind)

    if r:
        raise SpecError(r)
    return spec


def repeat_plan(spec: dict) -> dict:
    """The declared repeat, resolved into the exact per-index seeds.

    A v2 spec resolves to one repeat with the world seed, because that is what
    v2 MEANT -- not a default chosen here.

    `degenerate_by_construction` is arithmetic, not a judgement: with a
    constant seed derivation, a stateless kind and count > 1, every repeat is
    provably the same computation, so the within-world variance is zero before
    anything runs. Vivarium records that and executes the request as written.
    """
    seed_root = spec["world"]["seed_root"]
    rep = spec.get("repeat")
    if rep is None:
        return {"count": 1, "order": "sequential",
                "seed_derivation": "legacy_v2_world_seed", "state": "reset",
                "budget": None, "seeds": [seed_root],
                "degenerate_by_construction": False,
                "note": "spec_version 2: one observation, the world seed"}
    how = rep["seed_derivation"]
    seeds = []
    for i in range(rep["count"]):
        if how == "constant":
            seeds.append(seed_root)
        elif how == "linear_index":
            seeds.append(seed_root + i)
        else:                                    # sha256_index
            digest = hashlib.sha256(("%d:%d" % (seed_root, i)).encode()).digest()
            seeds.append(int.from_bytes(digest[:8], "big"))
    kind = _kinds.get((spec.get("work") or {}).get("kind"))
    degenerate = (how == "constant" and rep["count"] > 1
                  and rep["state"] == "reset"
                  and not (kind.stateful if kind else False))
    return {**{k: rep[k] for k in ("count", "order", "seed_derivation",
                                   "state", "budget")},
            "seeds": seeds,
            "degenerate_by_construction": degenerate,
            "note": ("every repeat is the same computation: constant seed, "
                     "stateless kind, state=reset. Within-world variance is "
                     "zero by construction." if degenerate else "")}


def is_executable(spec: dict) -> bool:
    kind = _kinds.get((spec.get("work") or {}).get("kind"))
    return bool(kind and kind.implemented)


# --------------------------------------------------------------------------
# The pre-registered decision procedure
# --------------------------------------------------------------------------

def apply_outcome_rule(spec: dict, result: dict) -> tuple:
    """Evaluate the requester's rule over the executor's result.

    Returns (outcome, provenance). Every branch, INCLUDING the one taken when
    the rule cannot be evaluated, comes from the spec. Vivarium chooses
    nothing here; if it cannot evaluate the rule it says so and takes the
    branch the requester declared for exactly that case.
    """
    rule = spec.get("outcome_rule")
    if rule is None:
        raise SpecError(["apply_outcome_rule called on a spec with no "
                         "outcome_rule; this is unreachable for an executable "
                         "kind and must never be silently defaulted"])
    field = rule["field"]
    indeterminate = rule["if_indeterminate"]
    if not isinstance(result, dict) or field not in result:
        return indeterminate, {"rule": rule, "branch": "if_indeterminate",
                               "reason": "field_absent", "field": field}
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
        return indeterminate, {"rule": rule, "branch": "if_indeterminate",
                               "reason": "uncomparable", "detail": str(exc),
                               "observed": observed}
    return (rule["if_true"] if hit else rule["if_false"]), {
        "rule": rule, "branch": "if_true" if hit else "if_false",
        "observed": observed, "predicate_held": hit}
