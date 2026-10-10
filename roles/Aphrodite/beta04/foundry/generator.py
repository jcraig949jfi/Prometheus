"""Seeded hierarchical WORLD generator (Beta-04 Experiment 1, foundry lead).

A WORLD is a curriculum of families that share hidden level-1 MECHANISMS:
    f*  Int->Int        p*  Int->Bool        s*  Int->Int->Int (fold step, acc -> v -> acc)
Mechanisms are DRAWN from a seeded PCFG and screened (task-free, outcome-free). No mechanism is named or chosen by
hand. Families are drawn from a pipeline grammar (CONFIG["skeletons"]): a source xs, list stages, a readout, and an
optional post-transform. Function slots are filled by mechanisms, by small base functions, or by the composition
combinators listed in CONFIG. The rung is a property of the drawn structure (classify_rung):
    R0  no mechanism                                               triviality control
    R1  one mechanism, used once, as the only function slot        first-order abstraction
    R2  one distinct mechanism plus extra structure                conditional reuse / two-step composition
        (a base-filled stage, an if-guard, a self-composition, a base fold or a base post-transform)
    R3  two distinct mechanisms. Each also appears alone in R1 families of the same world.
    R4  two distinct mechanisms in a pair that NO R3 family of the world uses, under the SHIFTED input distribution
Truth (mechanisms, promoted-form witnesses, rung composition) goes to a sealed WORLD_TRUTH file. Task JSON follows
contract v0.

Determinism: every random draw comes from random.Random(seed_string). Serialisation is sorted-key JSON, so the same
(config, world seed) gives byte-identical output. tests/test_generator.py checks this.
"""
import hashlib
import json
import random
from typing import Dict, List, Optional, Tuple

import interp_a as A
import tenum

# ---------------------------------------------------------------- CONFIG (freeze candidate; sha printed by `config`)
CONFIG = {
    "version": "b04-foundry-gen-v0.2-e1v2", "readout_len_requires_filter": True,
    "contract": "EXPERIMENT_PLAN.md s1 v0",
    "dist_base": {"len": [2, 8], "val": [-20, 20]},
    "dist_shift": {"len": [9, 16], "val": [-40, 40]},          # R4 TEST + TRIBUNAL only (E1 v2 rule 10 / D4)
    "r4_dev_dist": "dist_base",
    "n_dev": 12, "n_test": 40, "n_tribunal_random": 8,
    "fail_rate_max": 0.05, "fail_rate_samples": 200,
    "degenerate_modal_max": 0.5, "degenerate_min_distinct": 3,
    "mechanisms": {"f": 2, "p": 1, "s": 2},
    "mech_size": {"f": [4, 7], "p": [4, 7], "s": [4, 7]},
    "mech_irreducible_below": 5,        # no base-equivalent body of esize <= 4 (on the probe set)
    "mech_max_draws": 4000,
    "mech_pcfg": {"p_term": [0.0, 0.35, 0.6, 0.85, 1.0],
                  "ops": {"add": 3, "sub": 3, "mul": 3, "div": 1, "mod": 2, "gcd": 1, "pow": 0.5, "neg": 0.5,
                          "if": 1},
                  "var_p": 0.6, "bool_compound_p": 0.2,
                  "literals": [0, 1, 2, 3], "cmp_ops": ["lt", "eq", "gt"], "bool_ops": ["and", "or", "not"]},
    "mech_screen": {"f_min_distinct": 6, "identity_like_max": 0.5, "mag_max": 10 ** 6,
                    "p_true_band": [0.25, 0.75], "s_fold_lists": 40, "s_fold_min_distinct": 20,
                    "s_fold_mag_max": 10 ** 15,
                    "reject_affine_in_acc": True,             # E1 v2 rule 2: s(a,b) = c*a + g(b) on the probe set
                    "r1_regression_screen": True,             # E1 v2 rule 2: the mechanism's R1 families must
                    "regression_attempts_max": 80,            #   survive the REGRESSION rung (screen = reject+redraw)
                    "r1_draws_per_candidate": 12},
    "base_filler_size": {"F1": [2, 3], "P": [3, 5], "F2": [3, 3]},
    "quota": {"R0": 6, "R1_per_mech": 2, "R2": 10, "R3": 12, "R4": 6, "R5": 8},
    "r4_pair_fraction": 0.3,
    "family_max_draws": 200,
    "skeletons": {
        "R0": ["base_stage+readout", "readout_only", "base_stage"],
        "R1": {"f": ["map", "map+red", "post(red)"], "p": ["filter", "filter+red"], "s": ["foldl", "scanl"]},
        "R2": ["extra_base_stage", "guard", "self_compose", "base_fold_readout", "base_post"],
        "R3": {"ff": ["compose", "two_maps", "post_map"], "fp": ["filter_of_map", "map_of_filter", "pred_of_f",
                                                                    "guard_p"],
               "fs": ["fold_of_map", "step_of_f", "scan_of_map", "post_fold"],
               "ps": ["fold_of_filter", "scan_of_filter"], "ss": ["fold_of_scan"], "pp": ["filter_filter"]},
        "R5": {"I": ["base_post", "guard_post"], "L": ["readout", "base_fold", "base_map"],
               "pre": ["pre_struct", "pre_base_f", "pre_base_p"], "pre_prob": 0.4},
    },
    "readouts_int": ["sum", "len", "max", "min", "head", "last"],
    "readouts_after_filter": ["len", "sum"],
}


def config_sha(cfg=None) -> str:
    return hashlib.sha256(json.dumps(cfg or CONFIG, sort_keys=True).encode()).hexdigest()


def _rng(*parts) -> random.Random:
    return random.Random("|".join(str(p) for p in parts))


# ---------------------------------------------------------------- term helpers
def V(n):
    return ("var", n)


def L(k):
    return ("lit", k)


def P(name, *args):
    return ("prim", name, tuple(args))


def lam1(body, v="x"):
    return ("lam", v, body)


def lam2(body, a="a", b="b"):
    return ("lam", a, ("lam", b, body))


def subst_many(t, m: Dict[str, tuple]):
    k = t[0]
    if k == "lit":
        return t
    if k == "var":
        return m.get(t[1], t)
    if k == "lam":
        inner = {kk: vv for kk, vv in m.items() if kk != t[1]}
        return ("lam", t[1], subst_many(t[2], inner))
    if k == "app":
        return ("app", subst_many(t[1], m), tuple(subst_many(a, m) for a in t[2]))
    return ("prim", t[1], tuple(subst_many(a, m) for a in t[2]))


class Mechanism:
    def __init__(self, name, kind, body, stats):
        self.name, self.kind, self.body, self.stats = name, kind, body, stats
        self.vars = ("x",) if kind in ("f", "p") else ("a", "b")
        self.term = lam1(body) if kind in ("f", "p") else lam2(body)

    @property
    def sig(self):
        return ("I",) if self.kind in ("f", "p") else ("I", "I")

    @property
    def ret(self):
        return "B" if self.kind == "p" else "I"

    def promoted(self):
        return A.Promoted(self.name, self.term, self.sig, self.ret)

    def to_json(self):
        return {"name": self.name, "kind": self.kind, "term": A.show(self.term), "body_esize": A.esize(self.body),
                "stats": self.stats}


def expand(t, mechs: Dict[str, Mechanism]):
    """Inline promoted mechanism calls -> a contract-v0 base term (mechanism bodies have no binders)."""
    k = t[0]
    if k in ("lit", "var"):
        return t
    if k == "lam":
        return ("lam", t[1], expand(t[2], mechs))
    if k == "app":
        return ("app", expand(t[1], mechs), tuple(expand(a, mechs) for a in t[2]))
    args = tuple(expand(a, mechs) for a in t[2])
    if t[1] in mechs:
        m = mechs[t[1]]
        return subst_many(m.body, dict(zip(m.vars, args)))
    return ("prim", t[1], args)


# ---------------------------------------------------------------- PCFG for small typed bodies
def gen_int(rng, vars_, depth, pc):
    p_term = pc["p_term"][min(depth, len(pc["p_term"]) - 1)]
    if rng.random() < p_term:
        if rng.random() < pc["var_p"]:
            return V(rng.choice(vars_))
        return L(rng.choice(pc["literals"]))
    ops = sorted(pc["ops"].items())
    op = rng.choices([o for o, _w in ops], weights=[w for _o, w in ops])[0]
    if op == "neg":
        return P("neg", gen_int(rng, vars_, depth + 1, pc))
    if op == "if":
        return P("if", gen_bool(rng, vars_, depth + 1, pc), gen_int(rng, vars_, depth + 1, pc),
                 gen_int(rng, vars_, depth + 1, pc))
    return P(op, gen_int(rng, vars_, depth + 1, pc), gen_int(rng, vars_, depth + 1, pc))


def gen_bool(rng, vars_, depth, pc):
    if rng.random() < pc["bool_compound_p"] and depth < 2:
        op = rng.choice(pc["bool_ops"])
        if op == "not":
            return P("not", gen_bool(rng, vars_, depth + 1, pc))
        return P(op, gen_bool(rng, vars_, depth + 1, pc), gen_bool(rng, vars_, depth + 1, pc))
    return P(rng.choice(pc["cmp_ops"]), gen_int(rng, vars_, depth + 1, pc), gen_int(rng, vars_, depth + 1, pc))


# ---------------------------------------------------------------- probes and irreducibility tables
PROBE_F = list(range(-20, 21))
PROBE_F_WIDE = PROBE_F + [-60, -45, -33, 27, 38, 51, 64, 99]
PROBE_S = [(a, b) for a in (-30, -17, -8, -3, -1, 0, 1, 2, 5, 9, 14, 23, 40)
           for b in (-20, -13, -7, -2, -1, 0, 1, 3, 6, 11, 19)]
_FAILV = "FAIL"


def _ev1(fn, x):
    try:
        return fn({"x": x})
    except (A.Fail, ZeroDivisionError):
        return _FAILV


def _ev2(fn, a, b):
    try:
        return fn({"a": a, "b": b})
    except (A.Fail, ZeroDivisionError):
        return _FAILV


def sig_of(kind, fn):
    if kind in ("f", "p"):
        return tuple(_ev1(fn, x) for x in PROBE_F_WIDE)
    return tuple(_ev2(fn, a, b) for a, b in PROBE_S)


_IRR = {}


def irreducibility_table(kind, max_size):
    """signature -> smallest esize of a base body (no xs) with that signature on the probe set."""
    key = (kind, max_size)
    if key in _IRR:
        return _IRR[key]
    g = tenum.Grammar(with_input=False)
    ctx = ("x",) if kind in ("f", "p") else ("a", "b")
    T = "B" if kind == "p" else "I"
    table = {}
    for n in range(1, max_size + 1):
        for nd in g.get(T, n, ctx):
            s = sig_of(kind, nd.fn)
            if s not in table:
                table[s] = n
    _IRR[key] = table
    return table


def compile_body(body):
    import fastc
    return fastc.compile_term(body)


# ---------------------------------------------------------------- mechanism screening
def affine_in_acc(fn) -> bool:
    """s(a,b) = c*a + g(b) for one constant c, on the probe grid (E1 v2 rule 2)."""
    from fractions import Fraction
    As = sorted({a for a, _b in PROBE_S})
    Bs = sorted({b for _a, b in PROBE_S})
    c = None
    for b in Bs:
        g = _ev2(fn, 0, b)
        if g == _FAILV:
            return False
        for a in As:
            if a == 0:
                continue
            v = _ev2(fn, a, b)
            if v == _FAILV:
                return False
            slope = Fraction(v - g, a)
            if c is None:
                c = slope
            elif slope != c:
                return False
    return True


def screen_mechanism(kind, body, cfg, existing_sigs) -> Tuple[Optional[str], dict]:
    sc = cfg["mech_screen"]
    lo, hi = cfg["mech_size"][kind]
    es = A.esize(body)
    if not (lo <= es <= hi):
        return "SIZE", {}
    vs = A.free_vars(body)
    need = {"x"} if kind in ("f", "p") else {"a", "b"}
    if not need <= vs:
        return "UNUSED_ARGUMENT", {}
    fn = compile_body(body)
    sig = sig_of(kind, fn)
    st = {"esize": es}
    if kind in ("f", "p"):
        base = [_ev1(fn, x) for x in PROBE_F]
        if any(v == _FAILV for v in base):
            return "FAIL_PRONE", st
        if kind == "f":
            if len(set(base)) == 1:
                return "CONSTANT", st
            if sum(1 for x, v in zip(PROBE_F, base) if v == x) / len(PROBE_F) >= sc["identity_like_max"]:
                return "IDENTITY_LIKE", st
            if len(set(base)) < sc["f_min_distinct"]:
                return "LOW_DIVERSITY", st
            if max(abs(v) for v in base) > sc["mag_max"]:
                return "MAGNITUDE", st
            st["distinct"] = len(set(base))
        else:
            tf = sum(1 for v in base if v) / len(base)
            st["true_frac"] = round(tf, 3)
            if not (sc["p_true_band"][0] <= tf <= sc["p_true_band"][1]):
                return "PRED_BALANCE", st
    else:
        vals = [_ev2(fn, a, b) for a, b in PROBE_S]
        if any(v == _FAILV for v in vals):
            return "FAIL_PRONE", st
        if len(set(vals)) == 1:
            return "CONSTANT", st
        if all(v == a for (a, _b), v in zip(PROBE_S, vals)) or all(v == b for (_a, b), v in zip(PROBE_S, vals)):
            return "PROJECTION", st
        if sum(1 for (a, b), v in zip(PROBE_S, vals) if v in (a, b)) / len(vals) >= sc["identity_like_max"]:
            return "IDENTITY_LIKE", st
        if sc.get("reject_affine_in_acc") and affine_in_acc(fn):
            return "AFFINE_IN_ACC", st
        # fold stability on base-distribution lists
        r = _rng("fold-probe", A.show(body))
        outs = []
        for i in range(sc["s_fold_lists"]):
            xs = sample_list(r, cfg["dist_base"])
            for init in (0, 1):
                acc = init
                try:
                    for v in xs:
                        acc = fn({"a": acc, "b": v})
                        if abs(acc) > sc["s_fold_mag_max"]:
                            raise A.Fail
                except (A.Fail, ZeroDivisionError):
                    return "FOLD_UNSTABLE", st
                outs.append(acc)
        st["fold_distinct"] = len(set(outs))
        if len(set(outs)) < sc["s_fold_min_distinct"]:
            return "FOLD_LOW_DIVERSITY", st
    tab = irreducibility_table(kind, cfg["mech_irreducible_below"] - 1)
    if sig in tab:
        st["min_equiv_esize"] = tab[sig]
        return "REDUCIBLE", st
    st["min_equiv_esize"] = ">%d" % (cfg["mech_irreducible_below"] - 1)
    if sig in existing_sigs:
        return "DUPLICATE_MECHANISM", st
    return None, st


def draw_mechanisms(world_seed, cfg) -> Tuple[List[Mechanism], dict]:
    mechs, sigs, rej = [], set(), {}
    draws = {}
    for kind in ("f", "p", "s"):
        for i in range(cfg["mechanisms"][kind]):
            rng = _rng("mech", world_seed, kind, i)
            vars_ = ("x",) if kind in ("f", "p") else ("a", "b")
            for d in range(cfg["mech_max_draws"]):
                body = gen_bool(rng, vars_, 0, cfg["mech_pcfg"]) if kind == "p" else \
                    gen_int(rng, vars_, 0, cfg["mech_pcfg"])
                why, st = screen_mechanism(kind, body, cfg, sigs)
                if why is None:
                    m = Mechanism("%s%d" % (kind, i), kind, body, dict(st, draws=d + 1))
                    mechs.append(m)
                    sigs.add(sig_of(kind, compile_body(body)))
                    break
                rej[why] = rej.get(why, 0) + 1
            else:
                raise RuntimeError("no mechanism of kind %s within %d draws" % (kind, cfg["mech_max_draws"]))
            draws["%s%d" % (kind, i)] = d + 1
    return mechs, {"rejections": dict(sorted(rej.items())), "draws": draws}


# ---------------------------------------------------------------- base fillers (small, non-mechanism functions)
def draw_base_filler(rng, kind, cfg):
    lo, hi = cfg["base_filler_size"][{"f": "F1", "p": "P", "s": "F2"}[kind]]
    vars_ = ("x",) if kind in ("f", "p") else ("a", "b")
    pc = dict(cfg["mech_pcfg"], p_term=[0.0, 0.7, 1.0])
    for _ in range(500):
        body = gen_bool(rng, vars_, 1, pc) if kind == "p" else gen_int(rng, vars_, 0, pc)
        if not (lo <= A.esize(body) <= hi) or not (set(vars_) <= A.free_vars(body)):
            continue
        fn = compile_body(body)
        if kind in ("f", "p"):
            vals = [_ev1(fn, x) for x in PROBE_F]
            if _FAILV in vals or len(set(vals)) == 1:
                continue
            if kind == "f" and all(v == x for x, v in zip(PROBE_F, vals)):
                continue
            if kind == "p" and not (0.15 <= sum(1 for v in vals if v) / len(vals) <= 0.85):
                continue
        else:
            vals = [_ev2(fn, a, b) for a, b in PROBE_S]
            if _FAILV in vals or len(set(vals)) == 1:
                continue
        return body
    raise RuntimeError("no base filler")


# ---------------------------------------------------------------- inputs
def sample_list(rng, dist):
    n = rng.randint(dist["len"][0], dist["len"][1])
    return [rng.randint(dist["val"][0], dist["val"][1]) for _ in range(n)]


# ---------------------------------------------------------------- family skeletons
class Fam:
    """A drawn family in PROMOTED form, plus its bookkeeping."""

    def __init__(self, term, out, uses, extra, skeleton, dist_key):
        self.term, self.out, self.uses, self.extra, self.skeleton, self.dist_key = \
            term, out, uses, extra, skeleton, dist_key


def mech_filler(m: Mechanism):
    if m.kind == "f":
        return lam1(P(m.name, V("x")))
    if m.kind == "p":
        return lam1(P(m.name, V("x")))
    return lam2(P(m.name, V("a"), V("b")))


def base_filler(rng, kind, cfg):
    body = draw_base_filler(rng, kind, cfg)
    return lam1(body) if kind in ("f", "p") else lam2(body)


def stage(kind, filler, src, rng):
    if kind == "f":
        return P("map", filler, src)
    if kind == "p":
        return P("filter", filler, src)
    return P("scanl", filler, L(rng.choice([0, 1])), src)


def apply_fun_body(filler, arg):
    """filler (lam x BODY) applied to an Int expression -> BODY[x:=arg] (promoted form)."""
    return subst_many(filler[2], {filler[1]: arg})


def struct_stage(rng):
    c = rng.choice(["rev", "take", "drop"])
    if c == "rev":
        return lambda src: P("rev", src)
    k = rng.choice([1, 2, 3])
    return lambda src: P(c, L(k), src)


def readout(rng, src, choices):
    """A list readout. `len` is offered only if the list term contains a filter: otherwise its length is a function
    of len(xs) alone, so the readout would not depend on any mechanism (defect found pre-pilot on a dummy seed)."""
    if "(filter " not in A.show(src):
        choices = [c for c in choices if c != "len"]
    r = rng.choice(choices)
    return P(r, src), r


def sample_R0(rng, cfg):
    sk = rng.choice(cfg["skeletons"]["R0"])
    if sk == "readout_only":
        src = V("xs")
        if rng.random() < 0.5:
            src = struct_stage(rng)(src)
        t, _r = readout(rng, src, cfg["readouts_int"])
        return Fam(t, "I", [], 0, "R0:" + sk, "dist_base")
    kind = rng.choice(["f", "p"])
    s = stage(kind, base_filler(rng, kind, cfg), V("xs"), rng)
    if sk == "base_stage":
        return Fam(s, "L", [], 0, "R0:" + sk, "dist_base")
    t, _r = readout(rng, s, cfg["readouts_after_filter"] if kind == "p" else cfg["readouts_int"])
    return Fam(t, "I", [], 0, "R0:" + sk, "dist_base")


def r1_term(rng, m: Mechanism, cfg):
    sk = rng.choice(cfg["skeletons"]["R1"][m.kind])
    xs = V("xs")
    if sk == "map":
        return P("map", mech_filler(m), xs), "L", sk
    if sk == "map+red":
        return readout(rng, P("map", mech_filler(m), xs), cfg["readouts_int"])[0], "I", sk
    if sk == "post(red)":
        r, _ = readout(rng, xs, cfg["readouts_int"])
        return P(m.name, r), "I", sk
    if sk == "filter":
        return P("filter", mech_filler(m), xs), "L", sk
    if sk == "filter+red":
        return readout(rng, P("filter", mech_filler(m), xs), cfg["readouts_after_filter"])[0], "I", sk
    if sk == "foldl":
        return P("foldl", mech_filler(m), L(rng.choice([0, 1])), xs), "I", sk
    if sk == "scanl":
        return P("scanl", mech_filler(m), L(rng.choice([0, 1])), xs), "L", sk
    raise ValueError(sk)


def sample_R1(rng, m, cfg):
    t, out, sk = r1_term(rng, m, cfg)
    return Fam(t, out, [m.name], 0, "R1:%s:%s" % (m.kind, sk), "dist_base")


def sample_R2(rng, m: Mechanism, cfg):
    """One distinct mechanism + one extra structural element."""
    sk = rng.choice(cfg["skeletons"]["R2"])
    xs = V("xs")
    if sk == "self_compose":
        if m.kind == "f":
            fil = lam1(P(m.name, P(m.name, V("x"))))
            t = P("map", fil, xs)
            if rng.random() < 0.5:
                t = readout(rng, t, cfg["readouts_int"])[0]
                return Fam(t, "I", [m.name, m.name], 1, "R2:f:self_compose+red", "dist_base")
            return Fam(t, "L", [m.name, m.name], 1, "R2:f:self_compose", "dist_base")
        if m.kind == "p":                               # p used on both a list and a shifted copy
            fil = lam1(P("and", P(m.name, V("x")), P(m.name, P("add", V("x"), L(1)))))
            return Fam(P("filter", fil, xs), "L", [m.name, m.name], 1, "R2:p:self_compose", "dist_base")
        t = P("foldl", mech_filler(m), L(0), P("scanl", mech_filler(m), L(0), xs))
        return Fam(t, "I", [m.name, m.name], 1, "R2:s:self_compose", "dist_base")
    if sk == "guard":
        bp = base_filler(rng, "p", cfg)
        if m.kind == "f":
            other = V("x") if rng.random() < 0.5 else apply_fun_body(base_filler(rng, "f", cfg), V("x"))
            fil = lam1(P("if", apply_fun_body(bp, V("x")), P(m.name, V("x")), other))
            return Fam(P("map", fil, xs), "L", [m.name], 1, "R2:f:guard", "dist_base")
        if m.kind == "p":
            fil = lam1(P(rng.choice(["and", "or"]), P(m.name, V("x")), apply_fun_body(bp, V("x"))))
            t = P("filter", fil, xs)
            if rng.random() < 0.5:
                t = readout(rng, t, cfg["readouts_after_filter"])[0]
                return Fam(t, "I", [m.name], 1, "R2:p:guard+red", "dist_base")
            return Fam(t, "L", [m.name], 1, "R2:p:guard", "dist_base")
        fil = lam2(P("if", apply_fun_body(bp, V("b")), P(m.name, V("a"), V("b")), V("a")))
        return Fam(P("foldl", fil, L(rng.choice([0, 1])), xs), "I", [m.name], 1, "R2:s:guard", "dist_base")
    if sk == "extra_base_stage":
        bk = rng.choice(["f", "p", "struct"])
        if bk == "struct":
            pre = struct_stage(rng)
        else:
            bf = base_filler(rng, bk, cfg)
            pre = (lambda src, bk=bk, bf=bf: stage(bk, bf, src, rng))
        if m.kind in ("f", "p"):
            mstage = (lambda src: stage(m.kind, mech_filler(m), src, rng))
            order = rng.random() < 0.5
            t = mstage(pre(xs)) if order else pre(mstage(xs))
            if rng.random() < 0.5:
                t = readout(rng, t, cfg["readouts_after_filter"] if (m.kind == "p" or bk == "p")
                            else cfg["readouts_int"])[0]
                return Fam(t, "I", [m.name], 1, "R2:%s:extra_%s+red" % (m.kind, bk), "dist_base")
            return Fam(t, "L", [m.name], 1, "R2:%s:extra_%s" % (m.kind, bk), "dist_base")
        t = P("foldl", mech_filler(m), L(rng.choice([0, 1])), pre(xs))
        return Fam(t, "I", [m.name], 1, "R2:s:extra_%s" % bk, "dist_base")
    if sk == "base_fold_readout":
        bs = base_filler(rng, "s", cfg)
        if m.kind == "s":
            t = P("foldl", bs, L(rng.choice([0, 1])), P("scanl", mech_filler(m), L(rng.choice([0, 1])), xs))
        else:
            t = P("foldl", bs, L(rng.choice([0, 1])), stage(m.kind, mech_filler(m), xs, rng))
        return Fam(t, "I", [m.name], 1, "R2:%s:base_fold" % m.kind, "dist_base")
    if sk == "base_post":
        bf = base_filler(rng, "f", cfg)
        if m.kind == "f":
            inner = readout(rng, P("map", mech_filler(m), xs), cfg["readouts_int"])[0]
        elif m.kind == "p":
            inner = readout(rng, P("filter", mech_filler(m), xs), cfg["readouts_after_filter"])[0]
        else:
            inner = P("foldl", mech_filler(m), L(rng.choice([0, 1])), xs)
        return Fam(apply_fun_body(bf, inner), "I", [m.name], 1, "R2:%s:base_post" % m.kind, "dist_base")
    raise ValueError(sk)


def pair_key(m1, m2):
    return "+".join(sorted([m1.name, m2.name]))


def sample_R3(rng, m1: Mechanism, m2: Mechanism, cfg, dist_key="dist_base", tag="R3"):
    """Two distinct mechanisms combined by a combinator for their kind pair."""
    a, b = sorted([m1, m2], key=lambda m: "fps".index(m.kind))
    kp = a.kind + b.kind
    sk = rng.choice(cfg["skeletons"]["R3"][kp])
    xs = V("xs")
    uses = [a.name, b.name]
    name = "%s:%s:%s" % (tag, kp, sk)
    red_i = cfg["readouts_int"]

    def maybe_red(t, choices):
        if rng.random() < 0.5:
            return Fam(readout(rng, t, choices)[0], "I", uses, 0, name + "+red", dist_key)
        return Fam(t, "L", uses, 0, name, dist_key)

    if kp == "ff":
        a, b = (m1, m2) if rng.random() < 0.5 else (m2, m1)       # order of composition
        if sk == "compose":
            return maybe_red(P("map", lam1(P(a.name, P(b.name, V("x")))), xs), red_i)
        if sk == "two_maps":
            return maybe_red(P("map", mech_filler(a), P("map", mech_filler(b), xs)), red_i)
        if sk == "post_map":
            return Fam(P(a.name, readout(rng, P("map", mech_filler(b), xs), red_i)[0]), "I", uses, 0, name,
                       dist_key)
    if kp == "fp":
        f, p = a, b
        if sk == "filter_of_map":
            return maybe_red(P("filter", mech_filler(p), P("map", mech_filler(f), xs)), cfg["readouts_after_filter"])
        if sk == "map_of_filter":
            return maybe_red(P("map", mech_filler(f), P("filter", mech_filler(p), xs)), cfg["readouts_after_filter"])
        if sk == "pred_of_f":
            return maybe_red(P("filter", lam1(P(p.name, P(f.name, V("x")))), xs), cfg["readouts_after_filter"])
        if sk == "guard_p":
            return maybe_red(P("map", lam1(P("if", P(p.name, V("x")), P(f.name, V("x")), V("x"))), xs), red_i)
    if kp == "fs":
        f, s = a, b
        c = L(rng.choice([0, 1]))
        if sk == "fold_of_map":
            return Fam(P("foldl", mech_filler(s), c, P("map", mech_filler(f), xs)), "I", uses, 0, name, dist_key)
        if sk == "step_of_f":
            return Fam(P("foldl", lam2(P(s.name, V("a"), P(f.name, V("b")))), c, xs), "I", uses, 0, name, dist_key)
        if sk == "scan_of_map":
            return Fam(P("scanl", mech_filler(s), c, P("map", mech_filler(f), xs)), "L", uses, 0, name, dist_key)
        if sk == "post_fold":
            return Fam(P(f.name, P("foldl", mech_filler(s), c, xs)), "I", uses, 0, name, dist_key)
    if kp == "ps":
        p, s = a, b
        c = L(rng.choice([0, 1]))
        if sk == "fold_of_filter":
            return Fam(P("foldl", mech_filler(s), c, P("filter", mech_filler(p), xs)), "I", uses, 0, name, dist_key)
        if sk == "scan_of_filter":
            return Fam(P("scanl", mech_filler(s), c, P("filter", mech_filler(p), xs)), "L", uses, 0, name, dist_key)
    if kp == "ss":
        a, b = (m1, m2) if rng.random() < 0.5 else (m2, m1)
        return Fam(P("foldl", mech_filler(a), L(rng.choice([0, 1])),
                     P("scanl", mech_filler(b), L(rng.choice([0, 1])), xs)), "I", uses, 0, name, dist_key)
    if kp == "pp":
        return maybe_red(P("filter", mech_filler(a), P("filter", mech_filler(b), xs)), cfg["readouts_after_filter"])
    raise ValueError((kp, sk))


def classify_rung(fam: Fam, r1_mechs: set, r3_pairs: set) -> str:
    """Derived rung label from structure (checked against the target rung)."""
    if getattr(fam, "reuses", None):
        return "R5"
    distinct = sorted(set(fam.uses))
    if not distinct:
        return "R0"
    if len(distinct) == 1:
        if len(fam.uses) == 1 and fam.extra == 0:
            return "R1"
        return "R2"
    if fam.dist_key == "dist_shift":
        return "R4"
    return "R3"


# ---------------------------------------------------------------- R5: combination reuse (E1 v2 rule 8)
def sample_R5(rng, src_fam: "Fam", src_id: str, cfg):
    """Reuse an R3 combination (the source family's whole promoted term) in a NEW context: either a new input stage
    (pre) or a new outer context (post). The combination itself is unchanged."""
    sk = cfg["skeletons"]["R5"]
    T = src_fam.term
    xs = V("xs")
    if rng.random() < sk["pre_prob"]:
        ctx = rng.choice(sk["pre"])
        if ctx == "pre_struct":
            pre = struct_stage(rng)(xs)
        elif ctx == "pre_base_f":
            pre = P("map", base_filler(rng, "f", cfg), xs)
        else:
            pre = P("filter", base_filler(rng, "p", cfg), xs)
        t, out = subst_many(T, {"xs": pre}), src_fam.out
    elif src_fam.out == "I":
        ctx = rng.choice(sk["I"])
        if ctx == "base_post":
            t = apply_fun_body(base_filler(rng, "f", cfg), T)
        else:
            bp = base_filler(rng, "p", cfg)
            bf = base_filler(rng, "f", cfg)
            t = P("if", apply_fun_body(bp, T), T, apply_fun_body(bf, T))
        out = "I"
    else:
        ctx = rng.choice(sk["L"])
        if ctx == "readout":
            t, out = readout(rng, T, cfg["readouts_int"])[0], "I"
        elif ctx == "base_fold":
            t, out = P("foldl", base_filler(rng, "s", cfg), L(rng.choice([0, 1])), T), "I"
        else:
            t, out = P("map", base_filler(rng, "f", cfg), T), "L"
    f = Fam(t, out, list(src_fam.uses), 1, "R5:%s:%s" % (ctx, src_fam.skeleton.split(":", 1)[1]), "dist_base")
    f.reuses = src_id
    return f


# ---------------------------------------------------------------- family materialisation (inputs, screens)
def _key(xs):
    return tuple(xs)


def materialise(fam: Fam, mechs, cfg, world_seed, fkey, rung):
    """Run screens and draw dev / test / tribunal. Returns (record, reject_class|None).
    fkey: a string that, with the (secret) world seed, seeds every draw of this family.
    D4 (E1 v2 rule 10): R4 dev comes from cfg["r4_dev_dist"]; test and tribunal from the family's dist_key."""
    base = expand(fam.term, mechs)
    A.typecheck(base)
    test_dist = cfg[fam.dist_key]
    dev_dist = cfg[cfg["r4_dev_dist"]] if rung == "R4" else test_dist
    rec = {"witness": A.show(base), "witness_promoted": A.show(fam.term), "witness_esize": A.esize(base),
           "witness_size": A.size(base), "promoted_esize": A.esize(fam.term), "output_type": fam.out,
           "skeleton": fam.skeleton, "mechanisms_used": sorted(set(fam.uses)), "uses": list(fam.uses),
           "rung": rung, "dist_key": fam.dist_key,
           "dev_dist_key": cfg["r4_dev_dist"] if rung == "R4" else fam.dist_key, "fkey": fkey}
    if getattr(fam, "reuses", None):
        rec["reuses"] = fam.reuses
    rates = []
    for dk, dist in sorted({rec["dev_dist_key"]: dev_dist, fam.dist_key: test_dist}.items()):
        r = _rng("failprobe", world_seed, fkey, dk)
        fails = sum(1 for _ in range(cfg["fail_rate_samples"]) if A.run(base, sample_list(r, dist)) == A.FAIL)
        rates.append(fails / cfg["fail_rate_samples"])
    rec["fail_rate"] = max(rates)
    if rec["fail_rate"] > cfg["fail_rate_max"]:
        return rec, "FAIL_PRONE"
    seeds = {sp: "%s|%s|%s" % (world_seed, fkey, sp) for sp in ("dev", "test", "trib")}

    def draw(split, n, exclude, dist):
        rr = random.Random(seeds[split])
        out, seen = [], set(exclude)
        guard = 0
        while len(out) < n:
            guard += 1
            if guard > 50 * n + 1000:
                return None
            xs = sample_list(rr, dist)
            if _key(xs) in seen:
                continue
            y = A.run(base, xs)
            if y == A.FAIL:
                continue
            seen.add(_key(xs))
            out.append([xs, y])
        return out

    dev = draw("dev", cfg["n_dev"], set(), dev_dist)
    test = draw("test", cfg["n_test"], {_key(x) for x, _ in dev or []}, test_dist) if dev else None
    if dev is None or test is None:
        return rec, "FAIL_PRONE"
    rec["dev"], rec["test"] = dev, test
    rr = random.Random(seeds["trib"])
    lo, hi = test_dist["val"]
    lmax = test_dist["len"][1]
    extras = [sample_list(rr, test_dist) for _ in range(cfg["n_tribunal_random"])]
    extras += [[], [rr.randint(lo, hi)], [rr.randint(lo, hi)], [lo], [hi]]
    extras += [[hi] * lmax, [lo] * lmax, [hi if i % 2 else lo for i in range(lmax)], [0] * lmax]
    rec["tribunal"] = [[xs, A.run(base, xs)] for xs in extras]
    outs = [json.dumps(y) for _x, y in dev + test]
    modal = max(outs.count(o) for o in set(outs)) / len(outs)
    rec["modal_frac"] = round(modal, 3)
    rec["distinct_outputs"] = len(set(outs))
    if fam.out == "L":
        ident = sum(1 for x, y in dev + test if y == x) / len(outs)
        empty = sum(1 for _x, y in dev + test if y == []) / len(outs)
        rec["identity_frac"], rec["empty_frac"] = round(ident, 3), round(empty, 3)
        if ident > cfg["degenerate_modal_max"] or empty > cfg["degenerate_modal_max"]:
            return rec, "DEGENERATE"
    if modal > cfg["degenerate_modal_max"] or len(set(outs)) < cfg["degenerate_min_distinct"]:
        return rec, "DEGENERATE"
    return rec, None


def behaviour_key(base, cfg):
    r = _rng("dup-probe")
    vals = []
    for _ in range(24):
        vals.append(json.dumps(A.run(base, sample_list(r, cfg["dist_base"]))))
    return "|".join(vals)


def seed_sha256(world_seed) -> str:
    return hashlib.sha256(str(world_seed).encode()).hexdigest()


# ---------------------------------------------------------------- mechanisms + their R1 families (rule 2 screen)
def draw_mechanisms_with_r1(seed, cfg, beh_seen):
    """Draw each mechanism slot. A candidate that passes the task-free screens gets its R1 families drawn at once;
    the candidate is rejected (and redrawn) if it cannot supply R1_per_mech generation-OK R1 families, or if the
    REGRESSION rung solves any of them (E1 v2 rule 2). Returns (mechanisms, r1 records by mechanism, stats)."""
    import regress
    sc = cfg["mech_screen"]
    mechs, sigs, rej, draws, r1_by, unfilled, reg_rejects = [], set(), {}, {}, {}, [], []
    for kind in ("f", "p", "s"):
        for i in range(cfg["mechanisms"][kind]):
            name = "%s%d" % (kind, i)
            rng = _rng("mech", seed, kind, i)
            vars_ = ("x",) if kind in ("f", "p") else ("a", "b")
            attempts, filled = 0, False
            for d in range(cfg["mech_max_draws"]):
                body = gen_bool(rng, vars_, 0, cfg["mech_pcfg"]) if kind == "p" else \
                    gen_int(rng, vars_, 0, cfg["mech_pcfg"])
                why, st = screen_mechanism(kind, body, cfg, sigs)
                if why is not None:
                    rej[why] = rej.get(why, 0) + 1
                    continue
                attempts += 1
                m = Mechanism(name, kind, body, dict(st, draws=d + 1, regression_attempts=attempts))
                rr = _rng("R1", seed, name, d)
                recs, local, ok, nd = [], {}, 0, 0
                while ok < cfg["quota"]["R1_per_mech"] and nd < sc["r1_draws_per_candidate"]:
                    nd += 1
                    fam = sample_R1(rr, m, cfg)
                    fkey = "R1|%s|%d|%d" % (name, d, nd)
                    rec, why2 = materialise(fam, {name: m}, cfg, seed, fkey, "R1")
                    if why2 is None:
                        bk = behaviour_key(expand(fam.term, {name: m}), cfg) + "|" + fam.dist_key
                        if bk in beh_seen or bk in local:
                            why2 = "DUPLICATE"
                        else:
                            local[bk] = fkey
                    rec["gen_class"] = why2 or "OK"
                    recs.append(rec)
                    ok += why2 is None
                verdict = None
                if ok < cfg["quota"]["R1_per_mech"]:
                    verdict = "R1_SUPPLY"
                elif sc.get("r1_regression_screen"):
                    for rec in recs:
                        if rec["gen_class"] != "OK":
                            continue
                        rv = regress.run(rec["dev"], rec["test"], cfg)
                        rec["gen_regression"] = {"solved": rv["solved"], "solved_by": rv["solved_by"],
                                                 "best_selected_test_acc": rv["best_selected_test_acc"]}
                        if rv["solved"]:
                            verdict = "R1_REGRESSION"
                            reg_rejects.append({"slot": name, "term": A.show(m.term), "family": rec["witness"],
                                                "solved_by": rv["solved_by"],
                                                "model": rv["classes"][rv["solved_by"]]["model"]})
                            break
                if verdict is not None:
                    rej[verdict] = rej.get(verdict, 0) + 1
                    if attempts >= sc["regression_attempts_max"]:
                        break
                    continue
                mechs.append(m)
                sigs.add(sig_of(kind, compile_body(body)))
                r1_by[name] = recs
                beh_seen.update(local)
                filled = True
                draws[name] = d + 1
                break
            if not filled:
                unfilled.append(name)
    stats = {"rejections": dict(sorted(rej.items())), "draws": draws, "unfilled_slots": unfilled,
             "regression_rejects": reg_rejects}
    return mechs, r1_by, stats


# ---------------------------------------------------------------- world
def build_world(world_seed, cfg=None):
    """world_seed: a string (E1 v2: a 128-bit secret hex string). It is NEVER stored in the world; only its sha256."""
    cfg = cfg or CONFIG
    seed = str(world_seed)
    ssha = seed_sha256(seed)
    wid = "W" + ssha[:8]
    sha = config_sha(cfg)
    beh_seen = {}
    mechs_l, r1_by, mstats = draw_mechanisms_with_r1(seed, cfg, beh_seen)
    mechs = {m.name: m for m in mechs_l}
    families = []
    r3_fams = []

    def push(rec):
        rec["index"] = len(families)
        rec["family_id"] = "%s-F%03d-%s" % (wid, rec["index"], rec["rung"])
        families.append(rec)
        return rec

    def add(fam: Fam, target, fkey):
        rung = classify_rung(fam, set(), set())
        assert rung == target, (rung, target, fam.skeleton)
        rec, why = materialise(fam, mechs, cfg, seed, fkey, target)
        if why is None:
            bk = behaviour_key(expand(fam.term, mechs), cfg) + "|" + fam.dist_key
            if bk in beh_seen:
                why = "DUPLICATE"
                rec["duplicate_of_fkey"] = beh_seen[bk]
            else:
                beh_seen[bk] = fkey
        rec["gen_class"] = why or "OK"
        push(rec)
        if why is None and target == "R3":
            r3_fams.append((rec["family_id"], fam))
        return why is None

    def fill(target, quota, sampler):
        got, draws = 0, 0
        while got < quota and draws < cfg["family_max_draws"]:
            draws += 1
            fam = sampler(draws)
            if fam is None:
                break
            if add(fam, target, "%s|%d" % (target, draws)):
                got += 1
        return {"quota": quota, "ok": got, "draws": draws}

    fill_stats = {}
    rng0 = _rng("R0", seed)
    fill_stats["R0"] = fill("R0", cfg["quota"]["R0"], lambda d: sample_R0(rng0, cfg))
    fill_stats["R1"] = {}
    for m in mechs_l:
        for rec in r1_by[m.name]:
            push(rec)
        fill_stats["R1"][m.name] = {"ok": sum(1 for r in r1_by[m.name] if r["gen_class"] == "OK"),
                                    "draws": len(r1_by[m.name])}
    if mechs_l:
        rng2 = _rng("R2", seed)
        fill_stats["R2"] = fill("R2", cfg["quota"]["R2"],
                                lambda d: sample_R2(rng2, mechs_l[(d - 1) % len(mechs_l)], cfg))
    pairs = [(mechs_l[i], mechs_l[j]) for i in range(len(mechs_l)) for j in range(i + 1, len(mechs_l))]
    rp = _rng("pairs", seed)
    rp.shuffle(pairs)
    if len(pairs) >= 2:
        n4 = max(1, int(round(cfg["r4_pair_fraction"] * len(pairs))))
        r4_pairs, r3_pairs = pairs[:n4], pairs[n4:]
    else:
        r4_pairs, r3_pairs = [], pairs
    if r3_pairs:
        rng3 = _rng("R3", seed)
        fill_stats["R3"] = fill("R3", cfg["quota"]["R3"],
                                lambda d: sample_R3(rng3, *r3_pairs[(d - 1) % len(r3_pairs)], cfg))
    if r4_pairs:
        rng4 = _rng("R4", seed)
        fill_stats["R4"] = fill("R4", cfg["quota"]["R4"],
                                lambda d: sample_R3(rng4, *r4_pairs[(d - 1) % len(r4_pairs)], cfg,
                                                    dist_key="dist_shift", tag="R4"))
    if r3_fams:
        rng5 = _rng("R5", seed)
        fill_stats["R5"] = fill("R5", cfg["quota"]["R5"],
                                lambda d: (lambda src: sample_R5(rng5, src[1], src[0], cfg))(rng5.choice(r3_fams)))
    world = {
        "world_id": wid, "world_seed_sha256": ssha, "config_sha": sha,
        "mechanisms": [m.to_json() for m in mechs_l], "mechanism_screen": mstats,
        "r3_pairs": sorted(pair_key(a, b) for a, b in r3_pairs),
        "r4_pairs": sorted(pair_key(a, b) for a, b in r4_pairs),
        "fill": fill_stats, "families": families,
    }
    return world


def yoke_seed(world_seed) -> str:
    """Sibling seed for the YOKED world: derived from the secret seed, itself secret."""
    return hashlib.sha256(("yoke|%s" % world_seed).encode()).hexdigest()[:32]


def build_yoked(world, sibling):
    """YOKED world (E1 v2 rule 9 / D10): the SAME R3-R5 target families as `world`, but every R0-R2 stepping stone
    comes from the sibling world (independently drawn mechanisms, the same generator and quotas). Stepping stones
    are therefore matched in kind and number but carry no information about the targets' mechanisms."""
    fams = [dict(r, yoked_source="sibling") for r in sibling["families"] if r["rung"] in ("R0", "R1", "R2")]
    fams += [dict(r, yoked_source="target") for r in world["families"] if r["rung"] in ("R3", "R4", "R5")]
    return {"world_id": world["world_id"] + "-YOKED", "target_world": world["world_id"],
            "sibling_world": sibling["world_id"], "sibling_seed_sha256": sibling["world_seed_sha256"],
            "sibling_mechanisms": sibling["mechanisms"], "families": fams,
            "counts": {r: sum(1 for f in fams if f["rung"] == r and f["gen_class"] == "OK")
                       for r in ("R0", "R1", "R2", "R3", "R4", "R5")}}


def world_bytes(world) -> bytes:
    return json.dumps(world, sort_keys=True, separators=(",", ":")).encode()


def mechanisms_of(world) -> Dict[str, Mechanism]:
    out = {}
    for mj in world["mechanisms"]:
        t = A.parse(mj["term"])
        body = t[2] if mj["kind"] in ("f", "p") else t[2][2]
        out[mj["name"]] = Mechanism(mj["name"], mj["kind"], body, mj["stats"])
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        print(json.dumps(CONFIG, sort_keys=True, indent=1))
        print("config_sha256", config_sha())
