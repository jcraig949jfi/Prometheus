"""RNG-pairing check.

Incident: C9-D24 (with C9-D17). In the frozen world, arm B ACTUAL_GENOME consumed 0 RNG
draws for organism 0 while arm A (in situ) and arm C RANDOM_MATCHED drew L bytes from the
same RNG. So C == A for every seed, and B's whole stream was shifted by L draws ("B and C
share the same background population" was false). The k-founder subclass inherits the same
shift via `_pad`.

The check runs a caller-supplied, cheap setup function for each arm and seed and compares
the observables that the design claims are SHARED (the background), and optionally the
observables that must DIFFER (the treatment).

    setup(arm, seed) -> {"background": <comparable>, "treatment": <comparable>,
                         "draws": <int, optional>}

Verdicts
    UNPAIRED         some seed has a background that differs between arms that claim pairing
    SAME_SIMULATION  two arms that must differ have identical treatment AND background
    OK               backgrounds identical per seed across arms; treatments differ
    NOT_VERIFIED     setup raised, or fewer than 2 arms / 1 seed
:class:`CountingRandom` is a drop-in ``random.Random`` that counts draws, so a design can
report per-arm draw counts at the end of setup (a cheap, generic leading indicator).
"""
import random
from typing import Callable, Iterable, Mapping, Sequence

from . import CheckResult, OK, NOT_VERIFIED

NAME = "rng_pairing"


class CountingRandom(random.Random):
    """random.Random that counts calls to random()/getrandbits() (all draws go through them)."""

    def __init__(self, seed=None):
        self.draws = 0
        super().__init__(seed)

    def random(self):
        self.draws += 1
        return super().random()

    def getrandbits(self, k):
        self.draws += 1
        return super().getrandbits(k)


def check_rng_pairing(setup: Callable[[str, int], Mapping], arms: Sequence[str], seeds: Iterable[int],
                      must_differ: bool = True) -> CheckResult:
    arms = list(arms)
    seeds = list(seeds)
    if len(arms) < 2 or not seeds:
        return CheckResult(NAME, NOT_VERIFIED, "need >= 2 arms and >= 1 seed")
    out = {}
    try:
        for a in arms:
            for s in seeds:
                out[(a, s)] = setup(a, s)
    except Exception as e:  # noqa: BLE001 - an unrunnable setup is NOT_VERIFIED, never a pass
        return CheckResult(NAME, NOT_VERIFIED, "setup raised %s: %s" % (type(e).__name__, e))

    unpaired, same_sim = [], []
    draws = {a: sorted({out[(a, s)].get("draws") for s in seeds} - {None}) for a in arms}
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            bad = [s for s in seeds if out[(a, s)]["background"] != out[(b, s)]["background"]]
            if bad:
                unpaired.append({"arms": (a, b), "seeds_differing": len(bad), "of": len(seeds),
                                 "first_seed": bad[0], "draws": (draws[a], draws[b])})
            if must_differ:
                same = [s for s in seeds
                        if out[(a, s)]["background"] == out[(b, s)]["background"]
                        and out[(a, s)].get("treatment") == out[(b, s)].get("treatment")]
                if len(same) == len(seeds):
                    same_sim.append({"arms": (a, b), "seeds": len(seeds)})
    if unpaired:
        return CheckResult(NAME, "UNPAIRED",
                           "background differs between arms on the same seed: any per-seed / "
                           "'same background' reasoning is invalid; use unpaired tests or fix the stream",
                           {"draws": draws, "same_simulation": same_sim}, unpaired)
    if same_sim:
        return CheckResult(NAME, "SAME_SIMULATION",
                           "two arms are the same simulation for every seed: one null, not two",
                           {"draws": draws}, same_sim)
    return CheckResult(NAME, OK, "backgrounds paired per seed; treatments differ", {"draws": draws})
