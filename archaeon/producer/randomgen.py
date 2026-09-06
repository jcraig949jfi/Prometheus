"""The fallback: a boring, valid, executable experiment.

When no weak signal fires, Archaeon still proposes. That is the charter's only
reading of an absence of signal, and it is what keeps the loop sustaining
experimentation rather than stalling.

This generator is deliberately dumb. It is NOT the coverage-biased exploration
policy in ``archaeon/explore.py`` -- that one reads the fossil record and is a
policy with scientific content. This one draws uniformly from a small declared
parameter space and is the **RANDOM control**, kept as a named policy exactly
as the operator required. Nothing here consults the corpus.

Reproducibility: every draw is seeded from ``(lane, utc_day, nonce)`` and the
seed is recorded, so a proposal can be re-derived from its own provenance
rather than re-guessed.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any, Dict, Optional

from .contract import ALLOWED_LENGTHS

POLICY = "random.v0"

#: The declared parameter space. Small and enumerable on purpose: at this
#: milestone the point is a valid experiment, not coverage of a large space.
SEED_ROOT_RANGE = (100_000, 999_999)


def derive_seed(lane: str, day: str, nonce: str = "") -> int:
    blob = "|".join(["archaeon.random.v0", lane, day, nonce]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")


def draw(lane: str, day: str, nonce: str = "") -> Dict[str, Any]:
    """One draw from the declared space. Pure; no I/O, no corpus.

    Returns the parameters AND the seed that produced them, so the choice is
    reconstructable from the recorded provenance alone.
    """
    seed = derive_seed(lane, day, nonce)
    rng = random.Random(seed)
    length = rng.choice(list(ALLOWED_LENGTHS))
    seed_root = rng.randint(*SEED_ROOT_RANGE)
    bits = "".join(rng.choice("01") for _ in range(length))
    return {
        "policy": POLICY,
        "seed": seed,
        "seed_inputs": {"lane": lane, "day": day, "nonce": nonce},
        "space": {"lengths": list(ALLOWED_LENGTHS),
                  "seed_root_range": list(SEED_ROOT_RANGE),
                  "bits": "uniform over {0,1}^length"},
        "params": {"length": length, "seed_root": seed_root, "bits": bits},
    }


def draw_unused(lane: str, day: str, used_hashes, spec_builder,
                max_attempts: int = 16) -> Optional[Dict[str, Any]]:
    """Draw until the built spec's hash is one this lane has not used.

    Guards against re-proposing a byte-identical spec by accident. Gives up
    after ``max_attempts`` and returns None rather than looping: a generator
    that cannot find an unused draw is reporting something real about the
    space, and tick() records that instead of spinning.
    """
    for i in range(max_attempts):
        d = draw(lane, day, nonce=str(i))
        spec = spec_builder(d["params"])
        h = spec_builder.spec_hash(spec) if hasattr(spec_builder, "spec_hash") \
            else None
        d["attempt"] = i
        d["spec"] = spec
        if h is None or h not in used_hashes:
            d["spec_hash"] = h
            return d
    return None
