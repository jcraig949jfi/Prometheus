"""Grammar G4, the slice-4 family catalog, and the two search coordinates.

Frozen by AMENDMENT_8_2026-09-22.md (commit 026ccc847) before this was built.

G4 contains the structural constructors needed to synthesise a fold FROM
FIRST PRINCIPLES. The ORGAN arm additionally carries the frozen macro
5488abb9f6354f02..., whose holes are NARROWER than G4's fold shape. Both arms
can ultimately express exactly the same set of programs; only the order and
shape of the search differ.
"""
import math
import random
import re
from typing import Dict, List, Optional, Tuple

import engine as E

GRAMMAR_VERSION_4 = "g4-imperative-v1"
ORGAN_SHA256 = "5488abb9f6354f02eb210909e180b17db644f3e3a2675d70f3a140f2e6acf79a"

SEARCH_LENGTHS = (4, 9)
EXTRAPOLATION_LENGTHS = (20, 60)
STRESS_LENGTH = 200

CATALOG = ["gcd_times_first", "prod_minus_first", "sum_minus_first",
           "sum_plus_last", "sumsq_minus_first"]
QUERY_PARAM = ("sum_plus_last",)

# ---------------------------------------------------------------- expressions
INIT_ATOMS = ["0", "1", "first", "last"]
BODY_ATOMS = ["acc", "v", "first", "last", "0", "1"]
FINAL_ATOMS = ["acc", "first", "last", "0", "1"]


def _exprs(atoms, depth):
    out = list(atoms)
    if depth >= 1:
        for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
            for a in atoms:
                for b in atoms:
                    out.append(tmpl.format(a, b))
    if depth >= 2:
        level1 = list(out)
        for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
            for a in atoms:
                for b in level1:
                    if b not in atoms:
                        out.append(tmpl.format(a, b))
    return out


INIT_SPACE = _exprs(INIT_ATOMS, 1)
BODY_SPACE = _exprs(BODY_ATOMS, 2)
FINAL_SPACE = _exprs(FINAL_ATOMS, 1)

# the organ's declared hole grammars -- NARROWER by construction
H1_SPACE = ["0", "1"]
H2_SPACE = _exprs(["acc", "v"], 2)
H3_SPACE = ["acc"] + [tmpl.format("acc", "last")
                      for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())]


def space_sizes():
    return {
        "G4_INIT": len(INIT_SPACE), "G4_BODY": len(BODY_SPACE),
        "G4_FINAL": len(FINAL_SPACE),
        "G4_fold_shape_total": len(INIT_SPACE) * len(BODY_SPACE) * len(FINAL_SPACE),
        "G4_expr_shape_total": len(FINAL_SPACE),
        "ORGAN_H1": len(H1_SPACE), "ORGAN_H2": len(H2_SPACE), "ORGAN_H3": len(H3_SPACE),
        "ORGAN_macro_total": len(H1_SPACE) * len(H2_SPACE) * len(H3_SPACE) * len(FINAL_SPACE),
    }


# ---------------------------------------------------------------- tasks
def uses_query_param(family): return family in QUERY_PARAM


def task(family, rng, length_range=SEARCH_LENGTHS):
    lo, hi = length_range
    k = rng.randint(lo, hi)
    if family == "gcd_times_first":
        f = rng.choice([1, 2, 3, 6, 12])
        xs = [f * rng.randint(1, 30) for _ in range(k)]
        return ("Give the gcd of all of: " + ", ".join(map(str, xs))
                + " multiplied by the first.", str(math.gcd(*xs) * xs[0]))
    if family == "prod_minus_first":
        xs = [rng.randint(2, 9) for _ in range(k)]
        return ("Multiply all of: " + ", ".join(map(str, xs))
                + " then subtract the first.", str(math.prod(xs) - xs[0]))
    if family == "sum_minus_first":
        xs = [rng.randint(2, 99) for _ in range(k)]
        return ("Add all of: " + ", ".join(map(str, xs)) + " then subtract the first.",
                str(sum(xs) - xs[0]))
    if family == "sum_plus_last":
        xs = [rng.randint(2, 99) for _ in range(k)]
        m = rng.randint(7, 999)
        return ("Add all of: " + ", ".join(map(str, xs)) + " then add %d." % m,
                str(sum(xs) + m))
    if family == "sumsq_minus_first":
        xs = [rng.randint(2, 40) for _ in range(k)]
        return ("Add the squares of: " + ", ".join(map(str, xs)) + " then subtract the first.",
                str(sum(x * x for x in xs) - xs[0]))
    raise ValueError(family)


def tasks(family, n, seed, length_range=SEARCH_LENGTHS) -> List[Dict]:
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": "%s-%d-%d" % (family, seed, i)})
    return out


# ---------------------------------------------------------------- evaluation
_G = {"__builtins__": {}, "math": math, "abs": abs}


def _pw(a, b):
    if b < 0 or b > 32:
        return 0
    return pow(a, b)


_G["pow"] = _pw
CEIL = 10 ** 40


_CODE_CACHE = {}


CODE_CACHE_LIMIT = 200_000


def _code(expr: str):
    """Compile each expression string ONCE, with a BOUNDED cache.

    DEFECT FOUND 2026-09-22: the original cache was unbounded. The G4 fallback
    enumerates millions of distinct expression strings, so the cache grew
    without limit -- 1.65 GB and climbing, with the attendant dict and GC cost
    dominating the run. Semantics, candidate order and charge accounting are
    unchanged; only the cache is capped."""
    c = _CODE_CACHE.get(expr)
    if c is None:
        if len(_CODE_CACHE) >= CODE_CACHE_LIMIT:
            _CODE_CACHE.clear()
        c = compile(expr, "<g4>", "eval")
        _CODE_CACHE[expr] = c
    return c


def run_program(prog: Tuple, nums: List[int], trailing: bool):
    """prog = ('fold', init, body, final) or ('expr', final)."""
    vals = nums[:-1] if trailing else nums
    first, last = nums[0], nums[-1]
    env = {"first": first, "last": last, "acc": 0, "v": 0}
    try:
        if prog[0] == "expr":
            out = eval(_code(prog[1]), _G, env)
        else:
            _, init, body, final = prog
            bcode = _code(body)
            acc = eval(_code(init), _G, env)
            for v in vals:
                env["acc"], env["v"] = acc, v
                acc = eval(bcode, _G, env)
                if acc is None or abs(acc) > CEIL:
                    return None
            env["acc"] = acc
            out = eval(_code(final), _G, env)
        if out is None or abs(out) > CEIL:
            return None
        return out
    except Exception:      # noqa: BLE001
        return None


def program_source(family: str, prog: Tuple) -> str:
    trailing = uses_query_param(family)
    head = ("\ndef _pw(a, b):\n    if b < 0 or b > 32:\n        return 0\n"
            "    return pow(a, b)\n"
            "def _p4_%s(p):\n"
            "    nums = [int(x) for x in re.findall(r\"-?\\d+\", p)]\n"
            "    vals = nums[:-1] if %s else nums\n"
            "    first, last = nums[0], nums[-1]\n" % (family, trailing))
    if prog[0] == "expr":
        body = "    acc = 0\n    return str(%s)\n" % prog[1].replace("pow(", "_pw(")
    else:
        _, init, bexpr, final = prog
        body = ("    acc = %s\n    for v in vals:\n        acc = %s\n    return str(%s)\n"
                % (init.replace("pow(", "_pw("), bexpr.replace("pow(", "_pw("),
                   final.replace("pow(", "_pw(")))
    return head + body + ("DISCOVERED[\"%s\"] = _p4_%s\n" % (family, family))


# ---------------------------------------------------------------- coordinates
def macro_expand(h1: str, h2: str, h3: str, outer_final: str) -> Tuple:
    """The organ macro, EXPANDED into a plain G4 program. This is the function
    the expressivity certificate uses to prove ORGAN's set is inside G4's."""
    inner = h3                       # acc, or prim(acc, last)
    if outer_final == "acc":
        final = inner
    else:
        final = outer_final.replace("acc", "(%s)" % inner) if inner != "acc" else outer_final
    return ("fold", h1, h2, final)


def organ_candidates(rng: Optional[random.Random] = None):
    """The ORGAN coordinate: macro instantiations composed with a G4 FINAL."""
    h1s, h2s, h3s, fs = list(H1_SPACE), list(H2_SPACE), list(H3_SPACE), list(FINAL_SPACE)
    if rng:
        for lst in (h1s, h2s, h3s, fs):
            rng.shuffle(lst)
    for h1 in h1s:
        for h2 in h2s:
            for h3 in h3s:
                for f in fs:
                    yield macro_expand(h1, h2, h3, f), ("macro", h1, h2, h3, f)


def sham_macro_expand(h1: str, h2: str, h3: str, outer_final: str) -> Tuple:
    """SHAM: the declared mechanical rewrite of the organ -- the BODY hole's
    second argument v is rewritten to acc, so the loop ignores the sequence."""
    return macro_expand(h1, re.sub(r"\bv\b", "acc", h2), h3, outer_final)


def sham_candidates(rng: Optional[random.Random] = None):
    for prog, tag in organ_candidates(rng):
        _, h1, h2, h3, f = tag
        yield sham_macro_expand(h1, h2, h3, f), ("sham", h1, h2, h3, f)


def scratch_candidates(rng: Optional[random.Random] = None):
    """The G4 coordinate: no macro. The recipient must assemble the fold."""
    fs = list(FINAL_SPACE)
    inits, bodies = list(INIT_SPACE), list(BODY_SPACE)
    if rng:
        for lst in (fs, inits, bodies):
            rng.shuffle(lst)
    for f in fs:                                   # SHAPE_EXPR first (smaller)
        yield ("expr", f), ("expr", f)
    for i in inits:
        for b in bodies:
            for f in fs:
                yield ("fold", i, b, f), ("fold", i, b, f)


def search(candidates, examples, escrow, cap):
    """Charge one unit per candidate evaluated. Returns (prog, tag, charges)."""
    parsed = [([int(x) for x in re.findall(r"-?\d+", t["prompt"])], t["gold"],
               uses_query_param(t["family"])) for t in examples]
    for prog, tag in candidates:
        if escrow.remaining() <= 0 or escrow.spent >= cap:
            return None
        escrow.charge(1)
        ok = True
        for nums, gold, trailing in parsed:
            got = run_program(prog, nums, trailing)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            return prog, tag, escrow.spent
    return None


def rediscovered_fold(prog: Tuple) -> bool:
    """M8: did the arm independently produce fold-equivalent structure -- a
    loop whose body consumes v and threads acc?"""
    if prog[0] != "fold":
        return False
    body = prog[2]
    return bool(re.search(r"\bv\b", body)) and bool(re.search(r"\bacc\b", body))


# ---------------------------------------------------------------- tribunal
def _counterexamples(family, n):
    out = []
    for i in range(n):
        rng = random.Random(E.tribunal_entropy("v4-" + family, 10_000 + i))
        p, g = task(family, rng, (2, 120))
        out.append({"family": family, "prompt": p, "gold": g, "key": "ce4-%d" % i})
    return out


class Tribunal4:
    def __init__(self, family): self.family = family

    @classmethod
    def after_freeze(cls, artifact, family):
        if artifact is None:
            raise E.BoundaryViolation("tribunal requested before a frozen artifact")
        return cls(family)

    def _metamorphic(self, artifact, n=25):
        r = E.Recipient.fresh(seed=4242)
        r.load(artifact)
        fam = self.family
        for i in range(n):
            rng = random.Random(E.tribunal_entropy("v4-" + fam, 20_000 + i))
            xs = [rng.randint(2, 30) for _ in range(rng.randint(5, 30))]
            perm = [xs[0]] + sorted(xs[1:])     # first element pinned
            pa, _ = task(fam, random.Random(0))  # shape only
            def ask(ys):
                p = pa.split(":")[0] + ": " + ", ".join(map(str, ys)) + pa.split(".", 1)[-1] \
                    if False else None
                return None
            # permutation invariance of the non-first elements, evaluated by
            # rebuilding the prompt through the family's own generator shape
            def build(ys):
                if fam == "sum_minus_first":
                    return ("Add all of: " + ", ".join(map(str, ys)) + " then subtract the first.")
                if fam == "sumsq_minus_first":
                    return ("Add the squares of: " + ", ".join(map(str, ys))
                            + " then subtract the first.")
                if fam == "prod_minus_first":
                    return ("Multiply all of: " + ", ".join(map(str, ys))
                            + " then subtract the first.")
                if fam == "gcd_times_first":
                    return ("Give the gcd of all of: " + ", ".join(map(str, ys))
                            + " multiplied by the first.")
                return ("Add all of: " + ", ".join(map(str, ys)) + " then add 5.")
            a, b = r.answer(build(xs), fam), r.answer(build(perm), fam)
            if a is None or b is None or a != b:
                return False
        return True

    def score(self, artifact, n=200):
        def acc(instances):
            r = E.Recipient.fresh(seed=4242)
            r.load(artifact)
            return r.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"]
        seed = E.tribunal_entropy("v4-" + self.family, 1)
        return {
            "held_out_extrapolation": acc(tasks(self.family, n, seed, EXTRAPOLATION_LENGTHS)),
            "stress_length_200": acc(tasks(self.family, 50, seed,
                                           (STRESS_LENGTH, STRESS_LENGTH))),
            "counterexample_accuracy": acc(_counterexamples(self.family, 50)),
            "metamorphic_pass": self._metamorphic(artifact),
        }

    def qualified(self, sc):
        return (sc["held_out_extrapolation"] >= 0.99 and sc["stress_length_200"] >= 0.99
                and sc["counterexample_accuracy"] >= 0.99 and sc["metamorphic_pass"])
