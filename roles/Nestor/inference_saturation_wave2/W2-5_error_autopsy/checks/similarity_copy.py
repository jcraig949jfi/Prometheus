"""Similarity-as-copying check for heredity/replication detectors.

Incidents: 09-19 rehearsal (90% byte identity fired SPONTANEOUS_REPLICATOR 5 times in 3 min
on junk with copy_bytes 0); Z80A-D05 (fidelity read AFTER `_mutate`: the RECOMBINATION splice
made the match in 6,287/6,547 events; 910/1,031 "replicators" were splice artifacts);
P-11 painters (Artemis #793: a program writing a fixed self-matching pattern passes).

The detector under test has the signature
    detector(donor: bytes, before: bytes, after: bytes, donor_wrote: list[bool]) -> bool
where donor_wrote[i] says whether the donor wrote position i of the recipient during the event.

Built-in fixtures (deterministic):
    converged_no_write   recipient already ~95% identical to donor; donor wrote nothing
    splice_no_write      recipient became donor-like by a world variation operator; donor wrote 0
    partial_overwrite    donor wrote 30% of positions; result still >= 0.9 similar
    true_copy            donor wrote every position with its own bytes (must fire)
Verdict FIRES_WITHOUT_WRITING if any no-write / partial fixture fires; UNREACHABLE if the true
copy does not; OK otherwise.
"""
import random
from typing import Callable, Dict, List, Tuple

from . import CheckResult, OK, NOT_VERIFIED

NAME = "similarity_copy"


def fixtures(n: int = 64, seed: int = 0) -> Dict[str, Tuple[bytes, bytes, bytes, List[bool], bool]]:
    rng = random.Random(seed)
    donor = bytes(rng.randrange(256) for _ in range(n))
    # converged population: recipient differs from donor at ~5% of positions, no writes
    conv = bytearray(donor)
    for i in rng.sample(range(n), max(1, n // 20)):
        conv[i] = (conv[i] + 1) % 256
    conv = bytes(conv)
    rand = bytes(rng.randrange(256) for _ in range(n))
    # splice: before is random, after equals donor (world operator), donor wrote nothing
    splice_after = donor
    # partial: donor overwrote 30%, the rest was already donor-like
    part_before = bytearray(donor)
    idx = rng.sample(range(n), int(0.3 * n))
    for i in idx:
        part_before[i] = (part_before[i] + 7) % 256
    part_mask = [i in set(idx) for i in range(n)]
    return {
        # name: (donor, before, after, donor_wrote, must_fire)
        "converged_no_write": (donor, conv, conv, [False] * n, False),
        "splice_no_write": (donor, rand, splice_after, [False] * n, False),
        "partial_overwrite": (donor, bytes(part_before), donor, part_mask, False),
        "true_copy": (donor, rand, donor, [True] * n, True),
    }


def check_similarity_detector(detector: Callable[[bytes, bytes, bytes, List[bool]], bool],
                              n: int = 64, seed: int = 0) -> CheckResult:
    fx = fixtures(n, seed)
    results = {}
    try:
        for name, (d, b, a, w, _) in fx.items():
            results[name] = bool(detector(d, b, a, w))
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "detector raised %s: %s" % (type(e).__name__, e))
    false_fires = [k for k, (_, _, _, _, must) in fx.items() if not must and results[k]]
    misses = [k for k, (_, _, _, _, must) in fx.items() if must and not results[k]]
    details = {"fires": results}
    if false_fires:
        return CheckResult(NAME, "FIRES_WITHOUT_WRITING",
                           "detector credits resemblance the donor did not write: %s" % ", ".join(false_fires),
                           details, [{"fixture": k} for k in false_fires])
    if misses:
        return CheckResult(NAME, "UNREACHABLE", "detector misses a true copy", details)
    return CheckResult(NAME, OK, "detector requires donor-written bytes", details)
