"""Padding-inflation check.

Incidents: X-NONPAIR-FIDELITY's placed-share readout was inflated when span = len (declared
MIXED, overridden to NO_COPYING); X-NEARMISS inherited the placed-share idea (W11/W12); the
CW01 fixed-count damage rulers manufactured "length protects" (count_fixing_damage_rulers);
`_pad` fills hand-written genomes with RNG bytes so any fixed-length similarity sees
padding. A score that depends on what fills the unused tail is measuring the padding.

Method: re-score the same (parent core, child core) pair after padding both to length L with
(a) a CONSTANT fill shared by parent and child (0x00, 0xFF, 0x76 = HALT ...) and
(b) INDEPENDENT random fills. A padding-blind score gives the same value under both regimes.

    score_fn(parent_bytes, child_bytes, core_len) -> float

Verdicts
    PADDING_INFLATED   mean(constant) - mean(random) > tol  (shared padding is being credited)
    PADDING_SENSITIVE  |spread| across fills > tol in either direction (padding moves the score)
    OK                 score invariant to the fill within tol
    NOT_VERIFIED       no padding exists (core >= L) or score_fn raised
"""
import random
from typing import Callable, Sequence

from . import CheckResult, OK, NOT_VERIFIED

NAME = "padding_inflation"
DEFAULT_FILLS = (0x00, 0xFF, 0x76)


def _pad_const(core: bytes, L: int, b: int) -> bytes:
    return bytes(core) + bytes([b]) * (L - len(core))


def _pad_rand(core: bytes, L: int, rng: random.Random) -> bytes:
    return bytes(core) + bytes(rng.randrange(256) for _ in range(L - len(core)))


def check_padding_inflation(score_fn: Callable[[bytes, bytes, int], float], parent_core: bytes,
                            child_core: bytes, L: int, fills: Sequence[int] = DEFAULT_FILLS,
                            n_random: int = 16, seed: int = 0, tol: float = 0.02) -> CheckResult:
    n = max(len(parent_core), len(child_core))
    if n >= L:
        return CheckResult(NAME, NOT_VERIFIED, "core length %d >= L %d: nothing is padded" % (n, L))
    rng = random.Random(seed)
    try:
        const = {f: float(score_fn(_pad_const(parent_core, L, f), _pad_const(child_core, L, f), n))
                 for f in fills}
        rand = [float(score_fn(_pad_rand(parent_core, L, rng), _pad_rand(child_core, L, rng), n))
                for _ in range(n_random)]
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "score_fn raised %s: %s" % (type(e).__name__, e))
    mc = sum(const.values()) / len(const)
    mr = sum(rand) / len(rand)
    allv = list(const.values()) + rand
    spread = max(allv) - min(allv)
    details = {"mean_constant": mc, "mean_random": mr, "by_fill": const, "spread": spread,
               "core_len": n, "L": L, "padded_fraction": (L - n) / L}
    if mc - mr > tol:
        return CheckResult(NAME, "PADDING_INFLATED",
                           "shared constant padding raises the score by %.3f: restrict the ruler to "
                           "the core span or to bytes the actor wrote" % (mc - mr), details)
    if spread > tol:
        return CheckResult(NAME, "PADDING_SENSITIVE",
                           "score moves by %.3f with the padding fill" % spread, details)
    return CheckResult(NAME, OK, "score invariant to padding fill", details)
