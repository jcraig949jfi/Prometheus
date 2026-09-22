"""Worker-artifact emission and the hostile meta-tribunal for Tier 3A.

The tribunal is constructed only AFTER a worker artifact is frozen and hashed,
and is unreadable by any improver, pristine or evolved (AMENDMENT 9 s1, s5).
"""
import random
import re
from typing import Dict, List

import basis_v4 as G
import engine as E
import improver as I

# The family provider. Defaults to the Tier-3A catalog; Tier 3B installs its
# own frozen catalog via use_provider(). A provider supplies tasks(), witness()
# and the family spec -- never the tribunal, which stays here and stays hidden.
_P = I


def use_provider(mod):
    global _P
    _P = mod


def program_source(family: str, prog) -> str:
    """Every Tier-3A family carries a trailing query parameter, so `vals`
    always excludes it."""
    _, init, body, final = prog
    sub = lambda s: s.replace("pow(", "_pw(")
    lines = [
        "",
        "def _pw(a, b):",
        "    if b < 0 or b > 32:",
        "        return 0",
        "    return pow(a, b)",
        "def _t3_%s(p):" % family,
        '    nums = [int(x) for x in re.findall(r"-?\\d+", p)]',
        "    vals = nums[:-1]",
        "    first, last = nums[0], nums[-1]",
        "    acc = %s" % sub(init),
        "    for v in vals:",
        "        acc = %s" % sub(body),
        "    return str(%s)" % sub(final),
        'DISCOVERED["%s"] = _t3_%s' % (family, family),
        "",
    ]
    return "\n".join(lines)


def artifact_for(family: str, prog):
    return E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + program_source(family, prog)),
        generation=E.FROZEN_GENERATION)


def counterexamples(family: str, n: int) -> List[Dict]:
    out = []
    for i in range(n):
        rng = random.Random(E.tribunal_entropy("t3a-" + family, 10_000 + i))
        k = rng.choice([2, 3, 80, 150])
        xs = ([rng.randint(2, 30)] * k if i % 3 == 0
              else [rng.randint(2, 30) for _ in range(k)])
        m = rng.choice([1, 2, rng.randint(3, 97)])
        gold = G.run_program(_P.witness(family), xs + [m], True)
        out.append({"family": family,
                    "prompt": ("Family %s over: " % family) + ", ".join(map(str, xs))
                              + " with %d." % m,
                    "gold": str(gold), "key": "ce-t3a-%d" % i})
    return out


class MetaTribunal:
    def __init__(self, family):
        self.family = family

    @classmethod
    def after_freeze(cls, artifact, family):
        if artifact is None:
            raise E.BoundaryViolation("tribunal requested before a frozen artifact")
        if artifact.generation != E.FROZEN_GENERATION:
            raise ValueError("tribunal requires the frozen generation")
        return cls(family)

    def _metamorphic(self, artifact, n=25) -> bool:
        """Oracle-free: every declared body is commutative-associative over the
        sequence, so the answer must be invariant under permutation."""
        r = E.Recipient.fresh(seed=4242)
        r.load(artifact)
        fam = self.family
        for i in range(n):
            rng = random.Random(E.tribunal_entropy("t3a-" + fam, 20_000 + i))
            xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
            m = rng.randint(3, 97)
            perm = xs[1:]
            rng.shuffle(perm)
            perm = [xs[0]] + perm          # `first` is pinned; order else free
            ask = lambda ys: r.answer(("Family %s over: " % fam) + ", ".join(map(str, ys))
                                      + " with %d." % m, fam)
            a, b = ask(xs), ask(perm)
            if a is None or b is None or a != b:
                return False
        return True

    def score(self, artifact, n=150) -> Dict:
        def acc(instances):
            rr = E.Recipient.fresh(seed=4242)
            rr.load(artifact)
            return rr.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"]
        seed = E.tribunal_entropy("t3a-" + self.family, 1)
        return {
            "held_out_extrapolation": acc(_P.tasks(self.family, n, seed,
                                                  G.EXTRAPOLATION_LENGTHS)),
            "stress_length_200": acc(_P.tasks(self.family, 40, seed,
                                             (G.STRESS_LENGTH, G.STRESS_LENGTH))),
            "counterexample_accuracy": acc(counterexamples(self.family, 40)),
            "metamorphic_pass": self._metamorphic(artifact),
        }

    def qualified(self, sc) -> bool:
        return (sc["held_out_extrapolation"] >= 0.99 and sc["stress_length_200"] >= 0.99
                and sc["counterexample_accuracy"] >= 0.99 and sc["metamorphic_pass"])
