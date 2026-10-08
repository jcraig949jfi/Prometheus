"""W9-H -- hierarchical (second-level) task ecology for Beta-03 E4. TASK SIDE ONLY.

No treatment is run here and no existing engine file is modified. This module is the GENERATOR: a seeded,
pre-registerable hierarchical grammar that turns a world seed into (a) a pool of level-1 MECHANISMS (one-hole body
schemas S(H)), (b) a pool of level-2 COMPOSITIONS S_b o S_a := S_b[H := S_a[H]], and (c) a family stream
(lineage-style recurrence) mixing level-0 background (W8-shaped PCFG bodies), level-1 families S_a[H := e] and
level-2 families S_b[H := S_a[H := e]], with fillers e from the base grammar (W8's E1: atom or op(atom, atom)).

Nothing in the grammar names a motif. Mechanism operators and atoms are uniform draws; the only structure imposed
is a STRATUM QUOTA (ADD/MUL/DIV/GCD/MIX + one ANY slot) so that non-additive mechanisms are present in measurable
numbers. Stratum sizes are reported; nothing here is a claim about natural frequency.

Outputs (python w9h_grammar.py gen <seeds> [out]):
  W9H_SUPPLIES.json  {"W9H:<seed>": {"families": [[name, init, body, final], ...], "stats": {...}}}  (W8 shape)
  W9H_TRUTH.json     generator ground truth (mechanisms, compositions, per-family level/mechanism/filler).
                     SEALED for analysis + certification only: a treatment must never read it.
"""
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
os.environ.setdefault("A18_FASTCOST", "1")
os.environ.setdefault("A18_TAG", "W9H")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # roles/Aphrodite
ENG = ROOT / "engine"
for p in (ENG / "v2b", ENG, ENG / "accel", ROOT / "science" / "compounding" / "rb1"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import a18  # noqa: E402
from a18 import G, T3D, I, FR  # noqa: E402
import engine as E  # noqa: E402

# ------------------------------------------------------------------ FROZEN-CANDIDATE CONFIG
# Everything that changes the generated world lives here; its sha256 is recorded in every output. The coordinator
# freezes a specific CONFIG (by sha) before any treatment run.
CONFIG = {
    "version": "W9H-v1",
    "kind": "W9H",
    "ops": sorted(E.PRIMITIVES),                         # all 7 base primitives, uniform
    "atoms": list(G.BODY_ATOMS),                         # acc v first last 0 1, uniform
    "mech_shapes": {"W1": 0.2, "W2": 0.45, "W2S": 0.35},  # op(x,H) | op1(x, op2(y,H)) | op1(op2(x,y), H)
    "mech_quota": ["ADD", "MUL", "DIV", "GCD", "MIX", "ANY"],   # K1 = 6 mechanisms per seed, one per slot
    "K2": 3,                                             # level-2 compositions per seed (ordered pairs b != a)
    "level_quota": {"L0": 10, "L1": 20, "L2": 18},       # generator-admitted families per seed and level (pilot)
    "source_proposal_cap": 400,                          # a mechanism/composition is retired after this many draws
    "filler": "W8.e1: p=.5 atom else op(atom, atom)",
    "mech_screen": {"min_accumulating_share": 0.2, "min_distinct_vecs": 8, "max_identity_share": 0.5,
                    "min_w5_instantiations": 8, "no_redundant_node": True, "no_constant_subterm": True,
                    "min_feasible_of_24": 3},
    "comp_screen": {"min_accumulating_share": 0.2, "min_distinct_vecs": 8, "max_identity_share": 0.5,
                    "min_feasible_of_24": 3},
    "max_proposals": 20000,
    "init_space": "H1_SPACE", "final_space": "FINAL_SPACE containing acc",
}
COMM = ("add", "mul", "gcd")
NONADD = {"mul": "MUL", "fdiv": "DIV", "mod": "DIV", "gcd": "GCD", "powr": "POW"}
_LET = "abcdefghijklmnopqrstuvwxyz"


def config_sha(cfg=None):
    return hashlib.sha256(json.dumps(cfg or CONFIG, sort_keys=True).encode()).hexdigest()


def log(m):
    print("[W9H %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def init():
    a18.worker_init()
    a18.use_world("W5")
    T3D.in_space_body("(acc + v)")


# ------------------------------------------------------------------ base grammar (W8-identical E1/E2/E3)
def _tmpl(op):
    return E.PRIMITIVES[op][1]


def e1(rng, ops=None, atoms=None):
    ops, atoms = ops or CONFIG["ops"], atoms or CONFIG["atoms"]
    if rng.random() < 0.5:
        return rng.choice(atoms)
    return _tmpl(rng.choice(ops)).format(rng.choice(atoms), rng.choice(atoms))


def pcfg(rng):
    """W8's W5-shaped PCFG (level-0 background)."""
    ops, atoms = CONFIG["ops"], CONFIG["atoms"]

    def e2():
        return _tmpl(rng.choice(ops)).format(e1(rng), e1(rng))
    if rng.random() < 0.95:
        return _tmpl(rng.choice(ops)).format(rng.choice(atoms), e2())
    return e2()


def _orient(rng, op, a, b):
    """op with operands (a, b) in a uniformly random order."""
    return _tmpl(op).format(a, b) if rng.random() < 0.5 else _tmpl(op).format(b, a)


# ------------------------------------------------------------------ level-1 mechanisms
def render(t):
    if t[0] == "H":
        return "{H}"
    if t[0] == "atom":
        return t[1]
    return _tmpl(t[0]).format(render(t[1][0]), render(t[1][1]))


def _node(rng, op, a, b):
    """op with operands (a, b) in a uniformly random order."""
    return (op, [a, b]) if rng.random() < 0.5 else (op, [b, a])


def draw_mechanism(rng):
    """Returns (tree, shape, stratum). Shapes: W1 op(x,H); W2 op1(x, op2(y,H)); W2S op1(op2(x,y), H); every
    operator and atom uniform, every argument order uniform."""
    ops, atoms = CONFIG["ops"], CONFIG["atoms"]
    shapes = sorted(CONFIG["mech_shapes"])
    shape = rng.choices(shapes, weights=[CONFIG["mech_shapes"][x] for x in shapes])[0]
    at = lambda: ("atom", rng.choice(atoms))  # noqa: E731
    if shape == "W1":
        o = [rng.choice(ops)]
        t = _node(rng, o[0], at(), ("H",))
    elif shape == "W2":
        o = [rng.choice(ops), rng.choice(ops)]
        t = _node(rng, o[0], at(), _node(rng, o[1], at(), ("H",)))
    else:
        o = [rng.choice(ops), rng.choice(ops)]
        t = _node(rng, o[0], _node(rng, o[1], at(), at()), ("H",))
    return t, shape, stratum_of(o)


def _paths(t, p=()):
    yield p, t
    if t[0] not in ("H", "atom"):
        for i, c in enumerate(t[1]):
            yield from _paths(c, p + (i,))


def _put(t, p, y):
    if not p:
        return y
    kids = list(t[1])
    kids[p[0]] = _put(kids[p[0]], p[1:], y)
    return (t[0], kids)


def _has_hole(t):
    return t[0] == "H" or (t[0] != "atom" and any(_has_hole(c) for c in t[1]))


def _abs_sig(sg):
    """Signature up to sign: a node that only takes abs / negates (gcd(x, 0), (0 - x)) counts as redundant."""
    return tuple(tuple(abs(x) if isinstance(x, int) else x for x in vv) for vv in sg)


def degeneracy(t):
    """Semantic degeneracy of a mechanism tree (outcome-free): a REDUNDANT operator node (replacing it by one of its
    children leaves the 12-filler signature unchanged, e.g. (1 * v), pow(x, 1)), or a CONSTANT hole-free subterm
    (e.g. (first - first), (0 // v)). Returns a reason or None."""
    import ruler_v2 as R
    sg = _abs_sig(signature(render(t)))
    for p, n in _paths(t):
        if n[0] in ("H", "atom"):
            continue
        for c in n[1]:
            if _abs_sig(signature(render(_put(t, p, c)))) == sg:
                return "REDUNDANT_NODE"
        if not _has_hole(n) and len(set(R.vec(render(n)))) == 1:
            return "CONSTANT_SUBTERM"
    return None


def stratum_of(ops):
    cls = {NONADD[o] for o in ops if o in NONADD}
    if not cls:
        return "ADD"
    return cls.pop() if len(cls) == 1 else "MIX"


def schema_ops(s):
    t = I.parse(s.replace("{H}", "v"))
    out = []

    def walk(x):
        if x[1]:
            out.append(x[0])
            for c in x[1]:
                walk(c)
    walk(t)
    return out


def struct_key(src):
    return I.term_str(I.normalise(I.parse(src)))


def fill(schema, f):
    return schema.replace("{H}", f)


def compose(outer, inner):
    """S_b o S_a := S_b[H := S_a[H]] -- a one-hole schema of dependency depth 2."""
    return outer.replace("{H}", inner)


_PROBE = None


def probe_fillers():
    """A fixed 12-filler probe (seed-independent) for schema behaviour signatures."""
    global _PROBE
    if _PROBE is None:
        r = random.Random(I._seed("APHRODITE/W9H/PROBE/v1"))
        _PROBE = sorted(r.sample(FR.LEVEL1, 12))
    return _PROBE


def signature(schema):
    import ruler_v2 as R
    return tuple(R.vec(fill(schema, f)) for f in probe_fillers())


def screen_schema(schema, scr, need_w5=0):
    """Task-free, outcome-free schema screen over ALL LEVEL1 fillers. Returns (ok, record)."""
    import ruler_v2 as R
    inst = [fill(schema, f) for f in FR.LEVEL1]
    acc = [b for b in inst if R.accumulating(b)]
    vecs = {R.vec(b) for b in acc}
    ident = sum(1 for f in FR.LEVEL1 if R.vec(fill(schema, f)) == R.vec(f)) / len(FR.LEVEL1)
    w5 = len(T3D.instantiate(schema)) if need_w5 else None
    rec = {"acc_share": round(len(acc) / len(inst), 3), "distinct_vecs": len(vecs), "identity_share": round(ident, 3),
           "w5_inst": w5}
    ok = (rec["acc_share"] >= scr["min_accumulating_share"] and rec["distinct_vecs"] >= scr["min_distinct_vecs"]
          and ident <= scr["max_identity_share"] and (not need_w5 or w5 >= need_w5))
    if ok:
        rec["feasible_of_24"] = feasible(schema)
        ok = rec["feasible_of_24"] >= scr["min_feasible_of_24"]
    return ok, rec


_FEAS = None


def feasible(schema):
    """How many of 24 fixed LEVEL1 fillers give a family-admissible body (accumulating + T4 task-side profile
    admissible with init 0 and final acc). Task-side only; no search is run."""
    import ruler_v2 as R
    import tribunal_t4 as T4
    global _FEAS
    if _FEAS is None:
        _FEAS = sorted(random.Random(I._seed("APHRODITE/W9H/FEAS/v1")).sample(FR.LEVEL1, 24))
    n = 0
    for f in _FEAS:
        b = fill(schema, f)
        if R.accumulating(b) and T4.family_profile(("fold", "0", b, "acc"))["admissible"]:
            n += 1
    return n


def mechanisms_for(rng):
    mechs, sigs, keys, tries = [], set(), set(), 0
    for slot in CONFIG["mech_quota"]:
        while True:
            tries += 1
            if tries > 20000:
                raise RuntimeError("mechanism quota unfillable")
            t, shape, st = draw_mechanism(rng)
            if slot != "ANY" and st != slot:
                continue
            s = render(t)
            k = s
            if k in keys or degeneracy(t):
                continue
            ok, rec = screen_schema(s, CONFIG["mech_screen"], CONFIG["mech_screen"]["min_w5_instantiations"])
            if not ok:
                continue
            sg = signature(s)
            if sg in sigs:
                continue
            keys.add(k)
            sigs.add(sg)
            mechs.append({"id": "M%d" % len(mechs), "schema": s, "shape": shape, "stratum": st, "slot": slot,
                          "ops": schema_ops(s), "screen": rec})
            break
    return mechs, tries


def compositions_for(rng, mechs):
    """K2 ordered pairs (outer b, inner a), b != a, uniform without replacement, each passing the schema screen and
    IRREDUCIBLE: its probe signature differs from every level-1 mechanism of the seed (it is not secretly one of
    them)."""
    msig = {signature(m["schema"]) for m in mechs}
    pairs = [(b, a) for b in range(len(mechs)) for a in range(len(mechs)) if b != a]
    rng.shuffle(pairs)
    comps, sigs = [], set()
    for b, a in pairs:
        if len(comps) >= CONFIG["K2"]:
            break
        s = compose(mechs[b]["schema"], mechs[a]["schema"])
        ok, rec = screen_schema(s, CONFIG["comp_screen"])
        sg = signature(s)
        if not ok or sg in msig or sg in sigs:
            continue
        sigs.add(sg)
        inst = [fill(s, f) for f in FR.LEVEL1]
        rec["w5_share"] = round(sum(T3D.in_space_body(x) is not None for x in inst) / len(inst), 3)
        comps.append({"id": "C%d" % len(comps), "outer": mechs[b]["id"], "inner": mechs[a]["id"], "schema": s,
                      "strata": [mechs[b]["stratum"], mechs[a]["stratum"]], "screen": rec})
    return comps


# ------------------------------------------------------------------ family stream
def fam_name(seed, j):
    x = seed * 1000 + j
    s = ""
    for _ in range(5):
        s += _LET[x % 26]
        x //= 26
    return "y" + s


def canon(body):
    """W5 canonical string when the body is in W5 (as W8 does), else the raw expansion."""
    b = T3D.in_space_body(body)
    return (b, True) if b is not None else (body, False)


def supply(seed, quota=None):
    """One world seed -> (W8-shaped supply, sealed truth). The stream: at every proposal a level is drawn with weight
    = its remaining quota; within a level the SOURCE (mechanism / composition) is drawn uniformly among the
    least-filled live sources (recurrence is balanced, not favoured); a source is retired after
    source_proposal_cap draws. Each family: fresh filler e (W8 E1), init ~ H1, final ~ acc-finals; then the W8
    generator-level screens (accumulating, T4 task-side profile) and behaviour-level de-duplication."""
    import ruler_v2 as R
    import tribunal_t4 as T4
    quota = dict(quota or CONFIG["level_quota"])
    rng = random.Random(I._seed("APHRODITE/W9H/%s/SUPPLY/%d" % (CONFIG["version"], seed)))
    t0 = time.time()
    mechs, mtries = mechanisms_for(rng)
    comps = compositions_for(rng, mechs)
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    levels = sorted(quota)
    pools = {"L1": mechs, "L2": comps}
    filled = {x["id"]: 0 for x in mechs + comps}
    tried = {x["id"]: 0 for x in mechs + comps}
    left = {k: quota[k] for k in levels}
    if not comps:
        left["L2"] = 0
    fams, meta, seen_b, seen_bid, used_fill = [], {}, set(), set(), {}
    st = {"proposals": 0, "by_level": {k: {"proposals": 0, "rej_dup": 0, "rej_accum": 0, "rej_t4profile": 0,
                                           "rej_l1_not_w5": 0, "rej_l0_not_w5": 0, "admitted": 0} for k in levels}}
    while sum(left.values()) > 0 and st["proposals"] < CONFIG["max_proposals"]:
        lv = rng.choices(levels, weights=[left[k] for k in levels])[0]
        rec = {"level": lv}
        if lv != "L0":
            live = [x for x in pools[lv] if tried[x["id"]] < CONFIG["source_proposal_cap"]]
            if not live:
                left[lv] = 0
                continue
            lo = min(filled[x["id"]] for x in live)
            src = rng.choice([x for x in live if filled[x["id"]] == lo])
            tried[src["id"]] += 1
        st["proposals"] += 1
        s_l = st["by_level"][lv]
        s_l["proposals"] += 1
        if lv == "L0":
            b, inw5 = canon(pcfg(rng))
            if not inw5:
                s_l["rej_l0_not_w5"] += 1
                continue
        else:
            e = e1(rng)
            if e in used_fill.setdefault(src["id"], set()):
                s_l["rej_dup"] += 1
                continue
            b, inw5 = canon(fill(src["schema"], e))
            if lv == "L1" and not inw5:          # level-1 families must be representable by the base engine
                s_l["rej_l1_not_w5"] += 1
                continue
            rec.update({"src": src["id"], "filler": e, "in_W5": inw5})
        if b in seen_b:
            s_l["rej_dup"] += 1
            continue
        if not R.accumulating(b):
            s_l["rej_accum"] += 1
            continue
        p = ("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals))
        if not T4.family_profile(p)["admissible"]:
            s_l["rej_t4profile"] += 1
            continue
        bid = I.behavior_id(p, True)
        if bid in seen_bid:
            s_l["rej_dup"] += 1
            continue
        if lv != "L0":
            used_fill[src["id"]].add(e)
            filled[src["id"]] += 1
        seen_b.add(b)
        seen_bid.add(bid)
        s_l["admitted"] += 1
        left[lv] -= 1
        name = fam_name(seed, len(fams))
        fams.append([name, p[1], p[2], p[3]])
        meta[name] = rec
    st.update({"admitted": len(fams), "mech_tries": mtries, "seconds": round(time.time() - t0, 1),
               "per_source": filled, "source_draws": tried, "n_mechanisms": len(mechs),
               "n_compositions": len(comps), "config_sha": config_sha()})
    truth = {"mechanisms": mechs, "compositions": comps, "families": meta, "config_sha": config_sha()}
    return {"families": fams, "stats": st}, truth


def _gen_job(seed):
    init()
    sup, truth = supply(seed)
    return seed, sup, truth


def cmd_gen(seeds, out_dir):
    from concurrent.futures import ProcessPoolExecutor
    out_dir.mkdir(parents=True, exist_ok=True)
    sp, tp = out_dir / "W9H_SUPPLIES.json", out_dir / "W9H_TRUTH.json"
    sups = json.loads(sp.read_text()) if sp.exists() else {}
    truths = json.loads(tp.read_text()) if tp.exists() else {}
    todo = [s for s in seeds if "W9H:%d" % s not in sups]
    with ProcessPoolExecutor(int(os.environ.get("W9H_NPROC", "2")), initializer=init) as ex:
        for seed, sup, truth in ex.map(_gen_job, todo):
            sups["W9H:%d" % seed], truths["W9H:%d" % seed] = sup, truth
            sp.write_text(json.dumps(sups, sort_keys=True))
            tp.write_text(json.dumps(truths, sort_keys=True, indent=1))
            log("W9H:%d %s" % (seed, {k: sup["stats"][k] for k in ("proposals", "admitted", "seconds")}))
    return sups, truths


def parse_seeds(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        cmd_gen(parse_seeds(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "pilot")
    elif sys.argv[1] == "config":
        print(json.dumps({"config": CONFIG, "sha256": config_sha()}, indent=1))
