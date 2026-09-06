"""Build and validate an experiment spec against Vivarium's spec v2.

One builder, one validator, and the validator is **Vivarium's own**. Archaeon
does not keep a second copy of the rules: a private reimplementation would
drift, and the first symptom would be a spec that passes here and is rejected
at the seam -- or worse, passes both while meaning different things.

The spec carries EXACTLY the execution inputs. Everything about why Archaeon
chose this experiment rides in ``source_evidence``, a queue column.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

from .contract import KIND, SPEC_VERSION, ensure_viv_importable


class SpecInvalid(Exception):
    """The built spec does not satisfy Vivarium's contract."""


def build(params: Dict[str, Any], *,
          pew_required: bool = True) -> Dict[str, Any]:
    """An `evaluate_bitstring` spec, complete and explicit.

    Every top-level key Vivarium requires is present. `prediction`,
    `outcome_rule` and `pew` may be null in the contract but are all supplied
    here: an absent value that means something must be written explicitly, and
    a run that produces no PEW fossil is invisible to the next tick, which
    would break the loop this milestone exists to close.
    """
    bits = params["bits"]
    length = int(params["length"])
    seed_root = int(params["seed_root"])
    if len(bits) != length:
        raise SpecInvalid(
            "bits is {} characters but length is {}; the hidden target is "
            "derived from length, so a mismatch is two different experiments"
            .format(len(bits), length))

    return {
        "spec_version": SPEC_VERSION,
        # No world.name: Vivarium derives it from spec_hash (their F2). An
        # author-supplied name inside the hash is a channel, and S14 already
        # burned a result on trusting one.
        "world": {"seed_root": seed_root},
        "hypothesis": ("the supplied candidate does not solve the "
                       "seed-{} length-{} onemax landscape"
                       .format(seed_root, length)),
        "prediction": {"solved": False,
                       "basis": ("{} independent bit positions; the target is "
                                 "derived from the seed and the length"
                                 .format(length))},
        "work": {"kind": KIND, "payload": {"bits": bits, "length": length}},
        # if_indeterminate is required and is the REQUESTER's branch to
        # declare: Vivarium must never author the indeterminate outcome.
        "outcome_rule": {"field": "solved", "op": "==", "value": False,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE"},
        # Vivarium never mints scientific identity, so the encounter id is
        # Archaeon's to supply. Derived from the PARAMETERS, never from
        # spec_hash: the block is inside the spec, so hashing the spec to name
        # a field of the spec is circular. `players` is [] and explicit --
        # this execution declares no player, which is different from having
        # forgotten to say.
        "pew": {"required": bool(pew_required),
                "encounter_id": encounter_id(params),
                "players": []},
    }


def encounter_id(params: Dict[str, Any]) -> str:
    """Deterministic encounter identity for a player-less probe.

    Same parameters -> same id, so a re-derivation of the same experiment is
    recognisable rather than looking like a new encounter.
    """
    blob = json.dumps({"kind": KIND,
                       "bits": params["bits"],
                       "length": int(params["length"]),
                       "seed_root": int(params["seed_root"])},
                      sort_keys=True, separators=(",", ":"))
    return "ENC-archaeon-" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def spec_hash(spec: Dict[str, Any]) -> str:
    """Canonical hash. Delegates to Vivarium's when importable.

    Their hash is the one the queue's CHECK constraint and the engine's seal
    are compared against, so theirs is authoritative; the local form is a
    byte-identical fallback for offline use and is asserted equal by a test.
    """
    ensure_viv_importable()
    try:
        from viv import spec as vspec
        return vspec.spec_hash(spec)
    except Exception:                              # pragma: no cover
        blob = json.dumps(spec, sort_keys=True, separators=(",", ":"),
                          default=str)
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def validate(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Validate with VIVARIUM'S validator. Raises SpecInvalid on failure."""
    ensure_viv_importable()
    try:
        from viv import spec as vspec
    except Exception as exc:
        raise SpecInvalid(
            "vivarium's validator is unavailable ({}); Archaeon will not "
            "substitute a private copy of the rules, because the first "
            "symptom of drift is a spec that passes here and is rejected at "
            "the seam".format(exc))
    try:
        return vspec.validate(spec)
    except Exception as exc:
        raise SpecInvalid(str(exc))


def build_validated(params: Dict[str, Any], **kw) -> Dict[str, Any]:
    spec = build(params, **kw)
    validate(spec)
    return spec
