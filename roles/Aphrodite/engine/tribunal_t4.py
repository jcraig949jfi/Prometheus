"""TRIBUNAL T4 -- order-aware, domain-declared, junk-rejecting successor to the
inherited Tier-3 tribunal (engine/meta_tribunal.MetaTribunal).

NEW MODULE. Written 2026-09-27 by an RB-2 worker under the operator ruling of
2026-09-27 (Aphrodite may design a successor instrument with its own identity).
It does NOT modify or reinterpret meta_tribunal.py: the old tribunal stays the
instrument of record for Campaign 1 and AMENDMENTS <= 17. Nothing here is
adopted until the Aphrodite seat freezes it in a dated AMENDMENT.
Design, measured yields and the provider hook: science/compounding/rb2/
TASK_WORLD_T4_DESIGN.md.

WHAT CHANGES RELATIVE TO MetaTribunal
  1. NO permutation-invariance test. That test is valid only for folds that are
     commutative over the sequence, so it made the tribunal certify exactly
     G1's own span (commutative-monoid folds). T4 keeps NO oracle-free
     metamorphic relation: for the fold artifacts this DSL emits, every
     relation that holds for ALL folds (e.g. prefix-continuation consistency
     fold(xs+[y]) = step(fold(xs), y)) is either vacuous (true of every
     emitted fold by construction) or needs the hidden accumulator state,
     which a black-box answer does not expose. Instead T4 uses the metamorphic
     FOLLOW-UP inputs (reversal, sort, adjacent swap, prefix extension,
     prefix truncation, middle perturbation, duplication) as an ORDER
     BATTERY checked against the witness's gold. Valid for every fold,
     order-sensitive or not.
  2. DECLARED DOMAIN instead of a fixed stress length. The domain of a family
     is: values 2..30, query 1..97, list length 2..L_max, where L_max is the
     largest rung of LADDER on which the witness is TOTAL (no None, no
     ceiling, no pow-guard hit) on a fixed probe set and every lower rung.
     L_max < 20 -> the family is rejected (DOMAIN_TOO_SHORT: it cannot be
     tested for extrapolation beyond 2x the dev length). Extrapolation is
     tested on [20, min(60, L_max)], stress at L_max (= 200 for bounded
     families), counterexamples at {2, 3, min(80, L_max), L_max}. A family
     is never admitted with a None/overflow/guard gold anywhere on its
     batteries (NONE_ON_DOMAIN / GUARD_ON_DOMAIN): overflow artifacts are
     excluded, growth-bounded-by-length multiplicative families are testable.
  3. FAMILY ADMISSIBILITY (junk rejection), from the witness, cached:
       >= K_DISTINCT distinct outputs on 60 dev-distribution inputs, and the
       most common output covers <= MODE_MAX of them (not constant);
       changing a MIDDLE list element changes the answer in >= SENS_MIN of
       probes, and the same for the LAST list element (not input-ignoring,
       not absorbed by a fixed point);
       the answer equals some input value in <= COPY_MAX of probes (not a
       copy/leak of the prompt);
       the accumulator is not absorbed (constant from step 5 on) in
       >= ABSORB_MAX of length-30 probes (no degenerate fixed-point dynamics);
       no pow-guard hit (pow with exponent outside 0..32 silently returns 0 in
       G4; a task whose answer depends on that guard is an overflow artifact).
  4. Family names must be digit-free (ValueError otherwise): the emitted
     artifact parses every integer in the prompt, name included.
  5. Same interface shape as MetaTribunal: after_freeze(artifact, family),
     score(artifact) -> dict, qualified(score) -> bool, use_provider(prov).
     The provider only needs witness(family).
"""
import random
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple

import basis_v4 as G
import engine as E

NAME = "TRIBUNAL_T4_ORDER_AWARE_v1"
LADDER = (20, 25, 30, 40, 60, 80, 100, 150, 200)
BASE_LENGTHS = (2, 3, 4, 5, 6, 7, 8, 9)
EXT_LO, EXT_HI, STRESS_CAP = 20, 60, 200
K_DISTINCT, MODE_MAX, SENS_MIN, COPY_MAX, ABSORB_MAX = 5, 0.5, 0.2, 0.9, 0.9
THRESH = 0.99
CEIL = G.CEIL

_P = None


def use_provider(mod):
    """Install the family provider (anything with witness(family))."""
    global _P
    _P = mod


# ---------------------------------------------------------------- instrumented evaluator
# Same semantics as basis_v4.run_program (same globals, same guarded pow, same
# CEIL, exceptions -> None); additionally counts pow-guard hits.
_GUARD = [0]


def _pw(a, b):
    if b < 0 or b > 32:
        _GUARD[0] += 1
        return 0
    return pow(a, b)


_GT = dict(G._G)
_GT["pow"] = _pw
_FN: Dict[str, object] = {}


def _fn(expr):
    f = _FN.get(expr)
    if f is None:
        f = eval("lambda acc, v, first, last: (%s)" % expr, _GT)   # noqa: S307
        if len(_FN) > 200_000:
            _FN.clear()
        _FN[expr] = f
    return f


def run(prog, xs: List[int], m: int, trace: Optional[list] = None) -> Tuple[Optional[int], int]:
    """(answer or None, pow-guard hits) of a fold program on list xs + query m."""
    _GUARD[0] = 0
    nums = list(xs) + [m]
    vals, first, last = nums[:-1], nums[0], nums[-1]
    try:
        if prog[0] == "expr":
            out = _fn(prog[1])(0, 0, first, last)
        else:
            _, init, body, final = prog
            bf = _fn(body)
            acc = _fn(init)(0, 0, first, last)
            for v in vals:
                acc = bf(acc, v, first, last)
                if acc is None or abs(acc) > CEIL:
                    return None, _GUARD[0]
                if trace is not None:
                    trace.append(acc)
            out = _fn(final)(acc, vals[-1] if vals else 0, first, last)
        if out is None or abs(out) > CEIL:
            return None, _GUARD[0]
        return out, _GUARD[0]
    except Exception:      # noqa: BLE001
        return None, _GUARD[0]


# ---------------------------------------------------------------- family profile
def _rand_list(rng, L):
    return [rng.randint(2, 30) for _ in range(L)]


def _extremes(L):
    return [[2] * L, [30] * L, [2 if i % 2 == 0 else 30 for i in range(L)],
            [30 if i % 2 == 0 else 2 for i in range(L)],
            [2 + (i % 29) for i in range(L)], [30 - (i % 29) for i in range(L)]]


_PROFILE: Dict[tuple, Dict] = {}


def family_profile(witness) -> Dict:
    """Task-side admissibility of a family, from its witness alone. Cached."""
    key = tuple(witness)
    got = _PROFILE.get(key)
    if got is not None:
        return got
    rng = random.Random("APHRODITE/T4/PROFILE/v1/" + repr(key))
    reasons, guard = [], 0

    def total_on(L, nrand):
        nonlocal guard
        probes = [(xs, m) for xs in _extremes(L) for m in (1, 2, 3, 41, 97)]
        probes += [(_rand_list(rng, L), rng.randint(1, 97)) for _ in range(nrand)]
        for xs, m in probes:
            out, g = run(witness, xs, m)
            guard += g
            if out is None or g:
                return False
        return True

    base_ok = all(total_on(L, 6) for L in BASE_LENGTHS)
    l_max = None
    if base_ok:
        for L in LADDER:
            if not total_on(L, 16):
                break
            l_max = L
    if not base_ok:
        reasons.append("NONE_OR_GUARD_ON_DEV_LENGTHS")
    elif l_max is None:
        reasons.append("DOMAIN_TOO_SHORT")
    # non-degeneracy on the dev distribution (lengths 4..9, query 3..97)
    outs, copies, mid_ch, last_ch = [], 0, 0, 0
    for _ in range(60):
        xs = _rand_list(rng, rng.randint(5, 9))
        m = rng.randint(3, 97)
        o, g = run(witness, xs, m)
        guard += g
        outs.append(o)
        copies += o is not None and (o in xs or o == m)
        i = len(xs) // 2
        ys = list(xs)
        ys[i] = rng.choice([u for u in range(2, 31) if u != xs[i]])
        mid_ch += run(witness, ys, m)[0] != o
        zs = list(xs)
        zs[-1] = rng.choice([u for u in range(2, 31) if u != xs[-1]])
        last_ch += run(witness, zs, m)[0] != o
    cnt = Counter(outs)
    distinct = len([o for o in cnt if o is not None])
    mode_share = cnt.most_common(1)[0][1] / len(outs)
    mid_s, last_s, copy_s = mid_ch / 60, last_ch / 60, copies / 60
    # absorbing (fixed-point) dynamics on length-30 (or l_max) inputs
    absorbed, n_abs = 0, 0
    La = min(30, l_max or 30)
    for _ in range(30):
        tr = []
        out, g = run(witness, _rand_list(rng, La), rng.randint(3, 97), trace=tr)
        if len(tr) > 6:
            n_abs += 1
            absorbed += len(set(tr[5:])) == 1
    absorb_s = absorbed / n_abs if n_abs else 0.0
    if None in cnt:
        reasons.append("NONE_ON_DEV_DISTRIBUTION")
    if distinct < K_DISTINCT or mode_share > MODE_MAX:
        reasons.append("CONSTANT_OR_NEAR_CONSTANT")
    if mid_s < SENS_MIN:
        reasons.append("MIDDLE_INSENSITIVE")
    if last_s < SENS_MIN:
        reasons.append("LAST_INSENSITIVE")
    if copy_s > COPY_MAX:
        reasons.append("COPIES_INPUT")
    if absorb_s >= ABSORB_MAX:
        reasons.append("FIXED_POINT_DYNAMICS")
    if guard:
        reasons.append("POW_GUARD_HIT")
    prof = {"L_max": l_max, "base_ok": base_ok, "distinct": distinct,
            "mode_share": round(mode_share, 3), "middle_sensitivity": round(mid_s, 3),
            "last_sensitivity": round(last_s, 3), "copy_share": round(copy_s, 3),
            "absorbed_share": round(absorb_s, 3), "pow_guard_hits": guard,
            "reasons": sorted(set(reasons)), "admissible": not reasons}
    _PROFILE[key] = prof
    return prof


# ---------------------------------------------------------------- batteries
def _prompt(family, xs, m):
    return ("Family %s over: " % family) + ", ".join(map(str, xs)) + " with %d." % m


def _follow_ups(rng, xs):
    """Metamorphic FOLLOW-UP inputs (gold from the witness, never assumed equal)."""
    out = [list(reversed(xs)), sorted(xs), sorted(xs, reverse=True)]
    i = rng.randrange(1, len(xs) - 1)
    sw = list(xs)
    sw[i], sw[i + 1] = sw[i + 1], sw[i]
    out.append(sw)
    out.append(list(xs) + [rng.randint(2, 30)])
    out.append(list(xs[:-1]))
    mp = list(xs)
    j = len(xs) // 2
    mp[j] = 2 + (mp[j] - 1) % 29
    out.append(mp)
    out.append(list(xs[:j]) + [xs[j]] + list(xs[j:]))
    return out


_BAT: Dict[tuple, Dict[str, List[Dict]]] = {}


def batteries(family: str, witness, l_max: Optional[int], n: int = 150) -> Dict[str, List[Dict]]:
    key = (family, tuple(witness), l_max, n)
    got = _BAT.get(key)
    if got is not None:
        return got
    L = l_max or EXT_LO
    ehi = max(EXT_LO, min(EXT_HI, L))

    def mk(xs, m, tag, i):
        out, g = run(witness, xs, m)
        return {"family": family, "prompt": _prompt(family, xs, m),
                "gold": str(out), "key": "t4-%s-%d" % (tag, i), "_guard": g}

    bat = {"ext": [], "stress": [], "ce": [], "order": []}
    rng = random.Random(E.tribunal_entropy("t4-" + family, 1))
    for i in range(n):
        bat["ext"].append(mk(_rand_list(rng, rng.randint(EXT_LO, ehi)), rng.randint(3, 97), "ext", i))
    for i in range(40):
        bat["stress"].append(mk(_rand_list(rng, L), rng.randint(3, 97), "st", i))
    for i in range(40):
        r = random.Random(E.tribunal_entropy("t4-" + family, 10_000 + i))
        k = r.choice([2, 3, min(80, L), L])
        xs = [r.randint(2, 30)] * k if i % 3 == 0 else _rand_list(r, k)
        bat["ce"].append(mk(xs, r.choice([1, 2, r.randint(3, 97)]), "ce", i))
    for i in range(30):
        r = random.Random(E.tribunal_entropy("t4-" + family, 20_000 + i))
        xs = _rand_list(r, r.randint(5, min(30, L - 1)))
        m = r.randint(3, 97)
        for j, ys in enumerate(_follow_ups(r, xs)):
            bat["order"].append(mk(ys, m, "ord%d" % j, i))
    _BAT[key] = bat
    return bat


# ---------------------------------------------------------------- the tribunal
class TribunalT4:
    NAME = NAME

    def __init__(self, family):
        if re.search(r"\d", family):
            # the emitted artifact parses EVERY integer in the prompt, including
            # digits in "Family <name> over:", so such a name silently changes
            # the input list (the old tribunal has the same latent hazard).
            raise ValueError("T4: family names must be digit-free: %r" % family)
        self.family = family
        self.witness = _P.witness(family)
        self.profile = family_profile(self.witness)

    @classmethod
    def after_freeze(cls, artifact, family):
        if artifact is None:
            raise E.BoundaryViolation("tribunal requested before a frozen artifact")
        if artifact.generation != E.FROZEN_GENERATION:
            raise ValueError("tribunal requires the frozen generation")
        return cls(family)

    def score(self, artifact, n=150) -> Dict:
        bat = batteries(self.family, self.witness, self.profile["L_max"], n)
        reasons = list(self.profile["reasons"])
        allt = [t for v in bat.values() for t in v]
        if any(t["gold"] == "None" for t in allt):
            reasons.append("NONE_ON_DOMAIN")
        if any(t["_guard"] for t in allt):
            reasons.append("GUARD_ON_DOMAIN")

        def acc(instances):
            rr = E.Recipient.fresh(seed=4242)
            rr.load(artifact)
            inst = [{k: v for k, v in t.items() if k != "_guard"} for t in instances]
            return rr.run_tasks(inst, E.Escrow(10 ** 7))["accuracy"]

        return {
            "tribunal": NAME,
            "held_out_extrapolation": acc(bat["ext"]),
            "stress_at_domain_max": acc(bat["stress"]),
            "counterexample_accuracy": acc(bat["ce"]),
            "order_battery_accuracy": acc(bat["order"]),
            "domain_L_max": self.profile["L_max"],
            "family_admissible": not reasons,
            "family_reasons": sorted(set(reasons)),
        }

    def qualified(self, sc) -> bool:
        return (sc["family_admissible"] and sc["held_out_extrapolation"] >= THRESH
                and sc["stress_at_domain_max"] >= THRESH
                and sc["counterexample_accuracy"] >= THRESH
                and sc["order_battery_accuracy"] >= THRESH)


# ---------------------------------------------------------------- self-test
def _selftest():
    import os
    import sys
    import tempfile
    from pathlib import Path
    E.MARKER_DIR = Path(tempfile.gettempdir()) / ("aphrodite_t4_selftest_%d" % os.getpid())
    import meta_tribunal as M          # read-only: artifact emission + the old instrument

    class P:
        def __init__(self, specs):
            self.S = specs

        def witness(self, f):
            b, fi, i = self.S[f]
            return ("fold", i, b, fi)

        def tasks(self, f, n, seed, lr=G.SEARCH_LENGTHS):
            rng = random.Random((seed, f, lr).__str__())
            out = []
            for i in range(n):
                xs = _rand_list(rng, rng.randint(*lr))
                m = rng.randint(3, 97)
                out.append({"family": f, "prompt": _prompt(f, xs, m),
                            "gold": str(G.run_program(self.witness(f), xs + [m], True)),
                            "key": "%s-%d" % (f, i)})
            return out

    specs = {"alt": ("(v - acc)", "acc", "0"),            # alternating sum: order-sensitive
             "prod": ("(acc * v)", "acc", "1"),           # growth-bounded by length
             "horner_mod": ("(v + (acc * first))", "(acc % last)", "0"),  # Horner at x=first
             "const": ("(acc * v)", "acc", "0"),          # always 0
             "ignore": ("(v + (acc * 0))", "acc", "0"),   # = last list element
             "blowup": ("pow(acc, v)", "acc", "(1 + 1)"),  # overflows at once
             "guard": ("(acc + pow(v, last))", "acc", "0"),  # pow exponent > 32 -> guard
             "add": ("(acc + v)", "acc", "0")}
    prov = P(specs)
    use_provider(prov)
    M.use_provider(prov)
    checks = {}
    # 0. evaluator equivalence with basis_v4.run_program
    rng = random.Random(0)
    eq = True
    for f in specs:
        w = prov.witness(f)
        for _ in range(40):
            xs = _rand_list(rng, rng.randint(2, 40))
            m = rng.randint(1, 97)
            eq &= run(w, xs, m)[0] == G.run_program(w, xs + [m], True)
    checks["evaluator_equals_run_program"] = eq

    def both(fam, prog):
        art = M.artifact_for(fam, prog, 2)
        t4 = TribunalT4.after_freeze(art, fam)
        s4 = t4.score(art)
        old = M.MetaTribunal.after_freeze(art, fam)
        so = old.score(art)
        return t4.qualified(s4), s4, old.qualified(so), so

    q4, s4, qo, so = both("alt", prov.witness("alt"))
    checks["alt_witness_T4_qualified"] = q4
    checks["alt_witness_OLD_rejected_by_permutation"] = (not qo) and not so["metamorphic_pass"]
    # a commutative decoy (sum with sign by parity is order-sensitive; plain sum is not)
    q4d, s4d, _, _ = both("alt", ("fold", "0", "(acc + v)", "acc"))
    checks["alt_decoy_T4_rejected"] = not q4d
    q4, s4, qo, so = both("prod", prov.witness("prod"))
    checks["prod_T4_qualified_L_max_25"] = q4 and s4["domain_L_max"] == 25
    checks["prod_OLD_rejected_by_stress"] = (not qo) and so["stress_length_200"] < 0.99
    q4, s4, _, _ = both("horner_mod", prov.witness("horner_mod"))
    checks["horner_mod_T4_verdict_recorded"] = isinstance(q4, bool)
    for junk, reason in (("const", "CONSTANT_OR_NEAR_CONSTANT"), ("ignore", "MIDDLE_INSENSITIVE"),
                         ("blowup", "NONE_OR_GUARD_ON_DEV_LENGTHS"), ("guard", "POW_GUARD_HIT")):
        q4, s4, _, _ = both(junk, prov.witness(junk))
        checks["%s_T4_rejected_%s" % (junk, reason)] = (not q4) and reason in s4["family_reasons"]
    q4, s4, qo, _ = both("add", prov.witness("add"))
    checks["add_both_qualified"] = q4 and qo
    try:
        TribunalT4.after_freeze(None, "add")
        checks["boundary_none_artifact_raises"] = False
    except E.BoundaryViolation:
        checks["boundary_none_artifact_raises"] = True
    try:
        TribunalT4("alt2")
        checks["digit_family_name_rejected"] = False
    except ValueError:
        checks["digit_family_name_rejected"] = True
    p1 = family_profile(prov.witness("alt"))
    _PROFILE.clear()
    checks["profile_deterministic"] = family_profile(prov.witness("alt")) == p1
    for k, v in checks.items():
        print("%-46s %s" % (k, "PASS" if v else "FAIL"))
    ok = all(checks.values())
    print("T4 SELF-TEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
