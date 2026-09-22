"""Candidate task families and the M2 fold mechanism grammar.

Nothing here is wired into engine.FAMILIES, the base image, or any existing
artifact until the basis-separation certificate passes and the operator
freezes it.

DESIGN RULE (operator ruling, 2026-09-21): basis capability and mechanism
capability are separated. The arithmetic basis can do the local operations but
cannot express "process an arbitrary-length sequence", so a successful fold is
not decorative scaffolding around an already-complete primitive -- it
contributes a computational resource the substrate did not previously possess.

THE `last` SIDE CHANNEL, closed explicitly. `last` is exposed to the final
step ONLY for families where it is an independently meaningful QUERY
PARAMETER held outside the iterated sequence (list_prod_mod's modulus). For
families whose numbers are all sequence elements (list_sum), F sees `acc`
only, so the last element cannot become an x//x-style shortcut. The
certificate additionally proves that giving a bounded composition access to
`last` does not solve either family without the fold.
"""
import math
import random
from typing import Dict, List, Optional

from engine import PRIMITIVES

BASIS_PRIMITIVES = sorted(PRIMITIVES)

# Lengths the search and certificate may see, and the much longer lengths the
# tribunal uses for extrapolation. The artifact is FIXED SIZE across both.
SEARCH_LENGTHS = (4, 9)
EXTRAPOLATION_LENGTHS = (20, 60)
STRESS_LENGTH = 200

# Families whose final number is a query parameter OUTSIDE the sequence.
QUERY_PARAM_FAMILIES = ("list_prod_mod",)


def _collatz_steps(n: int) -> int:
    s = 0
    while n != 1 and s < 500:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s += 1
    return s


def task(family: str, rng: random.Random, length_range=SEARCH_LENGTHS):
    lo, hi = length_range
    if family == "list_sum":
        xs = [rng.randint(2, 99) for _ in range(rng.randint(lo, hi))]
        return "Add all of: " + ", ".join(map(str, xs)) + ".", str(sum(xs))
    if family == "list_prod_mod":
        xs = [rng.randint(2, 30) for _ in range(rng.randint(lo, hi))]
        m = rng.randint(7, 9973)
        return ("Multiply all of: " + ", ".join(map(str, xs))
                + " then give the remainder mod %d." % m,
                str(math.prod(xs) % m))
    if family == "collatz_steps":
        n = rng.randint(7, 9999)
        return ("Give the number of halve-or-triple-plus-one steps for %d to reach 1." % n,
                str(_collatz_steps(n)))
    raise ValueError(family)


def tasks(family: str, n: int, seed: int, length_range=SEARCH_LENGTHS) -> List[Dict]:
    rng = random.Random((seed, family, length_range).__str__())
    out = []
    for i in range(n):
        p, g = task(family, rng, length_range)
        out.append({"family": family, "prompt": p, "gold": g,
                    "key": "%s-%d-%d" % (family, seed, i)})
    return out


REQUIRED_PROPERTY = {
    "list_sum": "variable-length accumulation",
    "list_prod_mod": "variable-length accumulation + a reusable intermediate "
                     "representation (the running product) consumed by a final "
                     "step that uses the query parameter",
    "collatz_steps": "iteration to convergence with data-dependent branching",
}


# ---------------------------------------------------------------- M2: the fold
def uses_query_param(family: str) -> bool:
    return family in QUERY_PARAM_FAMILIES


def fold_source(family: str, init: str, e_body: str, f_body: str) -> str:
    """Emit the fold as module source. `last`/`vals` split is fixed by the
    family's declared shape, not chosen by the search."""
    trailing = uses_query_param(family)
    return (
        "\ndef _fold_%s(p):\n"
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


def fold_space(family: str):
    """The declared fold grammar: INIT x E(acc, v) x F(...).

    F sees `last` ONLY for query-parameter families -- the side channel is
    closed by construction for the others.
    """
    atoms = ["acc", "v"]
    bodies = list(atoms)
    for _n, (_f, tmpl) in sorted(PRIMITIVES.items()):
        for a in atoms:
            for b in atoms:
                bodies.append(tmpl.format(a, b))
    finals = ["acc"]
    if uses_query_param(family):
        for _n, (_f, tmpl) in sorted(PRIMITIVES.items()):
            finals.append(tmpl.format("acc", "last"))
    return ["0", "1"], bodies, finals


_OPS = {name: fn for name, (fn, _t) in PRIMITIVES.items()}


def _compile(expr: str):
    return compile(expr, "<fold>", "eval")


def fold_eval(init_c, body_c, final_c, nums: List[int], trailing: bool) -> Optional[int]:
    """Execute a fold candidate directly. Semantically identical to the emitted
    module source, but without rebuilding an artifact per candidate."""
    vals = nums[:-1] if trailing else nums
    last = nums[-1]
    def _pw(a, b):
        if b < 0 or b > 32:      # the declared bound on `powr`, enforced BEFORE
            return 0             # the operation rather than after it
        return pow(a, b)

    g = {"__builtins__": {}, "math": math, "pow": _pw, "abs": abs}
    try:
        acc = eval(init_c, g, {})
        for v in vals:
            acc = eval(body_c, g, {"acc": acc, "v": v, "last": last})
            if acc is None or abs(acc) > 10 ** 40:
                return None
        out = eval(final_c, g, {"acc": acc, "last": last})
        if out is None or abs(out) > 10 ** 40:
            return None
        return out
    except Exception:      # noqa: BLE001 -- a bad candidate is simply wrong
        return None


def search_fold(family: str, examples: List[Dict], escrow, cap: int) -> Optional[Dict]:
    """Enumerate the declared fold space against DEVELOPMENT instances only."""
    import re as _re
    inits, bodies, finals = fold_space(family)
    trailing = uses_query_param(family)
    parsed = [([int(v) for v in _re.findall(r"-?\d+", t["prompt"])], t["gold"])
              for t in examples]
    for init in inits:
        ic = _compile(init)
        for e_body in bodies:
            bc = _compile(e_body)
            for f_body in finals:
                if escrow.remaining() <= 0 or escrow.spent >= cap:
                    return None
                escrow.charge(1)
                fc = _compile(f_body)
                ok = True
                for nums, gold in parsed:
                    got = fold_eval(ic, bc, fc, nums, trailing)
                    # A candidate whose value escapes the declared ceiling is
                    # not a solution: the sandbox cannot even stringify it.
                    if got is None or abs(got) > 10 ** 40 or str(got) != gold:
                        ok = False
                        break
                if ok:
                    return {"init": init, "body": e_body, "final": f_body,
                            "trailing": trailing,
                            "source": fold_source(family, init, e_body, f_body),
                            "charges": escrow.spent}
    return None


def fold_surrogates(family: str, mech: Dict) -> List[tuple]:
    """Simpler causal surrogates (INVARIANT 1): constants, identity/passthrough,
    single primitive over the first two inputs, and SINGLE-ITERATION control
    flow -- the surrogate that specifically tests whether variable-length
    accumulation is doing the work."""
    trailing = "True" if uses_query_param(family) else "False"
    out = []
    for c in ("0", "1"):
        out.append(("const_acc_%s" % c, fold_source(family, mech["init"], c, mech["final"])))
    out.append(("identity_first",
                "\ndef _fold_%s(p):\n"
                "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
                "    return str(nums[0])\n"
                "DISCOVERED[\"%s\"] = _fold_%s\n" % (family, family, family)))
    for name, (_f, tmpl) in sorted(PRIMITIVES.items()):
        out.append(("expr_%s(n0,n1)" % name,
                    "\ndef _fold_%s(p):\n"
                    "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
                    "    return str(%s)\n"
                    "DISCOVERED[\"%s\"] = _fold_%s\n"
                    % (family, tmpl.format("nums[0]", "nums[1]"), family, family)))
        out.append(("expr_%s(n0,last)" % name,
                    "\ndef _fold_%s(p):\n"
                    "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
                    "    return str(%s)\n"
                    "DISCOVERED[\"%s\"] = _fold_%s\n"
                    % (family, tmpl.format("nums[0]", "nums[-1]"), family, family)))
    out.append(("single_iteration",
                "\ndef _fold_%s(p):\n"
                "    nums = [int(v) for v in re.findall(r\"-?\\d+\", p)]\n"
                "    vals = nums[:-1] if %s else nums\n"
                "    last = nums[-1]\n"
                "    acc = %s\n"
                "    for v in vals[:1]:\n"
                "        acc = %s\n"
                "    return str(%s)\n"
                "DISCOVERED[\"%s\"] = _fold_%s\n"
                % (family, trailing, mech["init"], mech["body"], mech["final"],
                   family, family)))
    return out
