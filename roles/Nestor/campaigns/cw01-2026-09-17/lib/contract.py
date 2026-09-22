"""Verdict contracts as first-class objects: what counts as evidence, frozen.

WHY THIS EXISTS

e05 logged seven measurement/specification defects during QUALIFY. Individually
they look like ordinary bugs. Collectively they are one failure: THE CRITERION
ITSELF BECAME AN EXPERIMENTAL OBJECT, seven times, while I was looking at the
evidence it was supposed to judge.

  - superadditivity defined on a ratio contaminated by a shared cost floor
  - an intervention applied to the mixture but not to its own baseline
  - raw superadditivity compared ACROSS composition laws, which overlap invalidates
  - an invented `gap_conj > abs(gap_disj)` magnitude threshold with no basis in the
    hypothesis, which reported FAIL on the predicted dissociation
  - a hand-picked "complementary" set that was 30% worse than a random subset
  - a carry PRICE that was monotone at every swept value, so carrying could never
    be contested
  - a zero-variance world that silently disabled the noise-floor gate

The runtime guards (learnability.assert_live, learnability.assert_controlled,
infometrics.effect_clears_null) catch violations DURING a comparison. None of them
can catch a conductor who changes the definition of the comparison between one
measurement and the next, because each individual measurement looks clean.

A verdict contract is the missing object. It states, before any experimental
genome is evaluated, what the statistic is, how it is normalised, what the control
is, how the null is constructed, what clears it, and how sets are selected. It is
canonicalised and hashed. The driver refuses to run unless its contract matches the
committed one, and records the hash into every result.

FREEZE RULE: once the first organism is evaluated under an attempt_id, no metric,
normalisation, control, threshold, set-selection rule, budget, null, or verdict
criterion may change under that attempt_id. A defect discovered mid-EXECUTE voids
the affected verdict and opens a NEW attempt_id. Criteria are never repaired in
place while evidence accumulates.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

# Fields excluded from the hash: descriptive only, never decision-bearing.
_NON_BINDING = {"_doc", "_note", "_rationale", "notes", "description"}


class ContractViolation(AssertionError):
    """Raised when a driver's contract does not match the committed one."""


class FrozenContractEdit(AssertionError):
    """Raised on an attempt to mutate a contract after freezing."""


def canonical(obj):
    """Deterministic serialisation: sorted keys, no whitespace drift.

    Non-binding descriptive keys are stripped so that improving a comment does not
    invalidate a hash, while any change to a decision-bearing field does.
    """
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in sorted(o.items()) if k not in _NON_BINDING}
        if isinstance(o, (list, tuple)):
            return [strip(v) for v in o]
        if isinstance(o, float):
            return round(o, 10)
        return o
    return json.dumps(strip(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def contract_hash(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


REQUIRED_FIELDS = (
    "experiment_id", "attempt_id", "world_schema_version",
    "statistic_name", "statistic_formula", "normalisation",
    "intervention_control_relationship", "null_construction",
    "effect_clearing_rule", "set_selection_procedure", "disposition_rules",
)


class VerdictContract:
    """An immutable statement of what counts as evidence."""

    def __init__(self, spec):
        missing = [f for f in REQUIRED_FIELDS if f not in spec]
        if missing:
            raise ContractViolation("contract is missing required fields: %s" % missing)
        self._spec = json.loads(json.dumps(spec))     # defensive copy
        self._frozen = False

    # --- construction -----------------------------------------------------
    @classmethod
    def load(cls, path):
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        spec = data.get("contract", data)
        c = cls(spec)
        stored = data.get("contract_sha256")
        if stored is not None and stored != c.hash:
            raise ContractViolation(
                "committed contract hash %s does not match its own body %s" % (stored, c.hash))
        return c

    def save(self, path):
        pathlib.Path(path).write_text(
            json.dumps({"contract": self._spec, "contract_sha256": self.hash,
                        "_freeze_rule": "no criterion may change under this attempt_id once the first "
                                        "organism is evaluated; a defect voids the verdict and opens a "
                                        "new attempt_id"},
                       indent=1),
            encoding="utf-8")
        return self.hash

    # --- identity ---------------------------------------------------------
    @property
    def hash(self):
        return contract_hash(self._spec)

    @property
    def spec(self):
        return json.loads(json.dumps(self._spec))

    def get(self, key, default=None):
        return self._spec.get(key, default)

    # --- freezing ---------------------------------------------------------
    def freeze(self):
        self._frozen = True
        return self

    def set(self, key, value):
        if self._frozen:
            raise FrozenContractEdit(
                "contract is frozen; '%s' cannot change under attempt_id %s. Open a new attempt_id."
                % (key, self._spec.get("attempt_id")))
        self._spec[key] = value
        return self

    # --- enforcement ------------------------------------------------------
    def require_matches(self, committed_path):
        """Refuse to proceed unless this contract equals the committed one."""
        other = VerdictContract.load(committed_path)
        if other.hash != self.hash:
            diffs = _diff(other.spec, self.spec)
            raise ContractViolation(
                "driver contract %s does not match committed %s; differing fields: %s"
                % (self.hash[:12], other.hash[:12], diffs))
        return self

    def stamp(self, result):
        """Record the contract identity into an experimental result."""
        result["verdict_contract_sha256"] = self.hash
        result["verdict_contract_attempt_id"] = self._spec.get("attempt_id")
        result["verdict_contract_statistic"] = self._spec.get("statistic_name")
        return result


def _diff(a, b, prefix=""):
    out = []
    for k in sorted(set(a) | set(b)):
        pa, pb = a.get(k), b.get(k)
        if isinstance(pa, dict) and isinstance(pb, dict):
            out += _diff(pa, pb, prefix + k + ".")
        elif pa != pb:
            out.append(prefix + k)
    return out
