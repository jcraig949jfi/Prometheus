"""The frozen third-family catalog (AMENDMENT 7 section B) and its tribunal.

The catalog was frozen in the amendment at commit abad582c9, before the organ
was extracted and before any transplant performance existed. Selection is
lexicographic over family name and takes no account of how any arm performs.
"""
import math
import random
import re
from typing import Dict, List

import basis_v2 as B
import engine as E

CATALOG = ["list_alt_sum", "list_gcd", "list_max", "list_prod", "list_sum_mod"]

# Families whose final number is a query parameter OUTSIDE the sequence.
QUERY_PARAM = ("list_sum_mod",)

SEARCH_LENGTHS = B.SEARCH_LENGTHS               # 4..9
EXTRAPOLATION_LENGTHS = B.EXTRAPOLATION_LENGTHS  # 20..60
STRESS_LENGTH = B.STRESS_LENGTH                  # 200


def uses_query_param(family: str) -> bool:
    return family in QUERY_PARAM


def task(family: str, rng: random.Random, length_range=SEARCH_LENGTHS):
    lo, hi = length_range
    k = rng.randint(lo, hi)
    if family == "list_alt_sum":
        xs = [rng.randint(2, 99) for _ in range(k)]
        g = sum(x if i % 2 == 0 else -x for i, x in enumerate(xs))
        return "Alternately add and subtract: " + ", ".join(map(str, xs)) + ".", str(g)
    if family == "list_gcd":
        f = rng.choice([1, 2, 3, 4, 6, 12])
        xs = [f * rng.randint(1, 40) for _ in range(k)]
        return "Give the gcd of all of: " + ", ".join(map(str, xs)) + ".", str(math.gcd(*xs))
    if family == "list_max":
        xs = [rng.randint(2, 999) for _ in range(k)]
        return "Give the largest of: " + ", ".join(map(str, xs)) + ".", str(max(xs))
    if family == "list_prod":
        xs = [rng.randint(2, 12) for _ in range(k)]
        return "Multiply all of: " + ", ".join(map(str, xs)) + ".", str(math.prod(xs))
    if family == "list_sum_mod":
        xs = [rng.randint(2, 99) for _ in range(k)]
        m = rng.randint(7, 9973)
        return ("Add all of: " + ", ".join(map(str, xs))
                + " then give the remainder mod %d." % m, str(sum(xs) % m))
    raise ValueError(family)


def tasks(family: str, n: int, seed: int, length_range=SEARCH_LENGTHS) -> List[Dict]:
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": "%s-%d-%d" % (family, seed, i)})
    return out


# ---------------------------------------------------------------- the organ
def organ_space(family: str):
    """The declared hole grammars: INIT x E x F. The skeleton is FROZEN."""
    atoms = ["acc", "v"]
    e_bodies = list(atoms)
    for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
        for a in atoms:
            for b in atoms:
                e_bodies.append(tmpl.format(a, b))
    finals = ["acc"]
    if uses_query_param(family):
        for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
            finals.append(tmpl.format("acc", "last"))
    return ["0", "1"], e_bodies, finals


def organ_source(family: str, init: str, e_body: str, f_body: str) -> str:
    trailing = uses_query_param(family)
    return (
        "\n" + B.POW_GUARD +
        "def _fold_%s(p):\n"
        "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
        "    vals = nums[:-1] if %s else nums\n"
        "    last = nums[-1]\n"
        "    acc = %s\n"
        "    for v in vals:\n"
        "        acc = %s\n"
        "    return str(%s)\n"
        "DISCOVERED[\"%s\"] = _fold_%s\n"
        % (family, "True" if trailing else "False", init,
           e_body.replace("pow(", "_pw("), f_body.replace("pow(", "_pw("),
           family, family))


def search_organ_holes(family: str, examples: List[Dict], escrow, cap: int):
    """The ORGAN arm: the skeleton is frozen, only the declared holes are
    searched. Returns (mechanism, charges_at_discovery) or None."""
    inits, bodies, finals = organ_space(family)
    trailing = uses_query_param(family)
    parsed = [([int(v) for v in re.findall(r"-?\d+", t["prompt"])], t["gold"])
              for t in examples]
    for init in inits:
        ic = B._compile(init)
        for e_body in bodies:
            bc = B._compile(e_body)
            for f_body in finals:
                if escrow.remaining() <= 0 or escrow.spent >= cap:
                    return None
                escrow.charge(1)
                fc = B._compile(f_body)
                ok = True
                for nums, gold in parsed:
                    got = B.fold_eval(ic, bc, fc, nums, trailing)
                    if got is None or str(got) != gold:
                        ok = False
                        break
                if ok:
                    return ({"init": init, "body": e_body, "final": f_body,
                             "source": organ_source(family, init, e_body, f_body)},
                            escrow.spent)
    return None


# ---------------------------------------------------------------- tribunal
def _counterexamples(family: str, n: int) -> List[Dict]:
    out = []
    for i in range(n):
        rng = random.Random(E.tribunal_entropy("v3-" + family, 10_000 + i))
        if family == "list_gcd":
            mode = i % 4
            if mode == 0:                                  # all identical
                x = rng.randint(2, 500)
                xs = [x] * rng.randint(3, 40)
            elif mode == 1:                                # a 1 forces gcd 1
                xs = [rng.randint(2, 99) for _ in range(rng.randint(3, 40))] + [1]
            elif mode == 2:                                # large common factor
                f = rng.choice([48, 60, 120])
                xs = [f * rng.randint(1, 20) for _ in range(rng.randint(3, 40))]
            else:                                          # long, coprime-ish
                xs = [rng.choice([7, 11, 13, 17, 19, 23]) for _ in range(120)]
            out.append({"family": family,
                        "prompt": "Give the gcd of all of: " + ", ".join(map(str, xs)) + ".",
                        "gold": str(math.gcd(*xs)), "key": "ce3-%d" % i})
        else:
            rng2 = random.Random(E.tribunal_entropy("v3-" + family, 30_000 + i))
            p, g = task(family, rng2, (2, 120))
            out.append({"family": family, "prompt": p, "gold": g, "key": "ce3-%d" % i})
    return out


class Tribunal3:
    """Independently seeded, constructed only after the recipient artifact is
    frozen and hashed. Never shown to any search."""

    def __init__(self, frozen_hash: str, family: str):
        self.frozen_hash, self.family = frozen_hash, family

    @classmethod
    def after_freeze(cls, artifact, family):
        if artifact is None:
            raise E.BoundaryViolation("tribunal requested before a frozen artifact")
        return cls(artifact.sha256, family)

    def _metamorphic(self, artifact, n: int = 30) -> bool:
        r = E.Recipient.fresh(seed=4242)
        r.load(artifact)
        fam = self.family
        for i in range(n):
            rng = random.Random(E.tribunal_entropy("v3-" + fam, 20_000 + i))
            xs = [rng.randint(2, 60) * rng.choice([1, 2, 6]) for _ in range(rng.randint(5, 40))]
            perm = xs[:]
            rng.shuffle(perm)
            k = rng.randint(2, 60)
            if fam == "list_gcd":
                f = lambda ys: r.answer("Give the gcd of all of: "
                                        + ", ".join(map(str, ys)) + ".", fam)
                a, b, c = f(xs), f(perm), f(xs + [k])
                if a is None or b is None or c is None:
                    return False
                try:
                    if a != b or int(c) != math.gcd(int(a), k):
                        return False
                except ValueError:
                    return False
            else:
                return True     # only the selected family needs relations here
        return True

    def score(self, artifact, n: int = 200) -> Dict:
        def acc(instances):
            r = E.Recipient.fresh(seed=4242)
            r.load(artifact)
            return r.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"]
        seed = E.tribunal_entropy("v3-" + self.family, 1)
        return {
            "held_out_extrapolation": acc(tasks(self.family, n, seed,
                                                EXTRAPOLATION_LENGTHS)),
            "stress_length_200": acc(tasks(self.family, 60, seed,
                                           (STRESS_LENGTH, STRESS_LENGTH))),
            "counterexample_accuracy": acc(_counterexamples(self.family, 60)),
            "metamorphic_pass": self._metamorphic(artifact),
        }

    def qualified(self, artifact) -> bool:
        s = self.score(artifact)
        return (s["held_out_extrapolation"] >= 0.99 and s["stress_length_200"] >= 0.99
                and s["counterexample_accuracy"] >= 0.99 and s["metamorphic_pass"])
