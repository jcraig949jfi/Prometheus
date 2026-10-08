"""g12 unit tests (Beta-03 E2). Run: python -m pytest roles/Aphrodite/engine/v2b/tests/test_g12.py -q
Slow tests (-m slow) run real donors on EXPOSED Beta-02 seed 26 and compare with beta02/runs/E12/E12_DONORS.jsonl."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths  # noqa: E402,F401
import pytest  # noqa: E402

import g12  # noqa: E402
from a18 import G  # noqa: E402

H1, FIN = list(G.H1_SPACE), list(G.FINAL_SPACE)
START = [{"name": "organ_fold", "inits": H1, "bodies": list(G.H2_SPACE), "finals": FIN}]


def row(rb, dl, saving=0, sha="0", ok=True, ref=False):
    return g12.score_row(rb, dl, ok, saving, sha, ref)


# ---------------------------------------------------------------- the rule on synthetic tables
def test_picks_max_S():
    t = {"INHERITED": row([0, 0], 0, ref=True), "A": row([1, 1], 1, sha="a"), "B": row([2, 1], 1, sha="b"),
         "C": row([3, 2], 2, sha="c")}
    # S: A 0.75, B 0.75, C 1.5
    assert g12.choose(t) == "C"
    assert t["C"]["S"] == 1.5 and t["A"]["eligible"] and t["B"]["eligible"]


def test_min_over_folds_not_total():
    t = {"INHERITED": row([0, 0], 0, ref=True), "ONE_FOLD": row([6, 0], 1, saving=10 ** 9, sha="a"),
         "BOTH": row([1, 1], 1, sha="b")}
    assert not t["ONE_FOLD"]["eligible"] and g12.choose(t) == "BOTH"


def test_ties_saving_then_sha():
    t = {"INHERITED": row([0, 0], 0, ref=True), "A": row([2, 2], 1, saving=5, sha="ff"),
         "B": row([2, 2], 1, saving=9, sha="ee"), "C": row([2, 2], 1, saving=9, sha="dd")}
    assert g12.choose(t) == "C"           # S tie -> saving tie (9) -> min sha
    t["B"]["saving"] = 10
    assert g12.choose(t) == "B"


def test_all_ineligible_returns_inherited():
    t = {"INHERITED": row([5, 5], 0, ref=True), "A": row([0, 3], 1), "B": row([1, 1], 4),   # S = 0 -> not > 0
         "C": row([2, 2], 1, ok=False)}                                                        # tribunal failure
    assert [t[k]["eligible"] for k in "ABC"] == [False, False, False]
    assert g12.choose(t) == "INHERITED"
    assert g12.choose({"INHERITED": row([0, 0], 0, ref=True)}) == "INHERITED"


def test_inherited_never_eligible():
    assert not row([9, 9], 0, ref=True)["eligible"]


def test_name_freedom_renaming_keys_keeps_choice():
    rng = random.Random(3)
    for _ in range(200):
        t = {"INHERITED": row([0, 0], 0, ref=True)}
        for k in range(rng.randint(1, 8)):
            t["X%d" % k] = row([rng.randint(0, 4), rng.randint(0, 4)], rng.randint(0, 9), rng.randint(-5, 5),
                               "%08x" % rng.getrandbits(32))
        c = g12.choose(t)
        names = [n for n in t if n != "INHERITED"]
        new = ["MEMORISE", "SCHEMA_ALL"] + ["SCHEMA_%d" % i for i in range(len(names))]
        rng.shuffle(new)
        ren = dict(zip(names, new))
        t2 = {ren.get(n, n): v for n, v in t.items()}
        c2 = g12.choose(t2)
        assert (c == "INHERITED" and c2 == "INHERITED") or ren[c] == c2


def test_arm_choice_equals_separate_runs():
    """Joint table: each arm's choice == choose() on that arm's own candidate set."""
    rng = random.Random(11)
    for _ in range(300):
        t = {"INHERITED": row([0, 0], 0, ref=True)}
        for n in ["SCHEMA_0", "SCHEMA_1", "MEMORISE"] + list(g12.PLANTS):
            if rng.random() < 0.8:
                t[n] = row([rng.randint(0, 3), rng.randint(0, 3)], rng.randint(1, 6), rng.randint(0, 9),
                           "%04x" % rng.getrandbits(16))
        for arm, plants in g12.ARMS.items():
            own = {n: v for n, v in t.items() if not n.startswith("PLANT_") or n in plants}
            assert g12.arm_choice(t, arm) == g12.choose(own)
        assert not g12.arm_choice(t, "g12").startswith("PLANT_")


# ---------------------------------------------------------------- description length
def test_description_length():
    sch = {"name": "g2_new", "inits": H1, "bodies": ["(acc + v)", "(acc + 1)", "(acc + first)"], "finals": FIN,
           "schema": "(acc + {H})"}
    allc = dict(sch, schemas=["(acc + {H})", "({H} + v)"])
    allc.pop("schema")
    memo = {"name": "memorised", "inits": H1, "bodies": ["(acc + v)", "(acc * v)", "(acc - 1)", "v"], "finals": FIN}
    plant = [{"name": "m0", "inits": ["0"], "bodies": ["(acc + v)"], "finals": ["acc"]},
             {"name": "m1", "inits": ["1"], "bodies": ["(acc * v)"], "finals": ["acc"]}]
    assert g12.description_length(START, START) == 0
    assert g12.description_length([sch] + START, START) == 1
    assert g12.description_length([allc] + START, START) == 2
    assert g12.description_length([memo] + START, START) == 4
    assert g12.description_length(plant + START, START) == 6
    assert g12.description_length([dict(memo, bodies=[])] + START, START) == 0
    assert g12.description_length([], START) == 0                    # dropping entries costs nothing
    # a 4-body memorised entry needs one more reached family per fold than a schema to tie (E4 s3)
    a = row([1, 1], g12.description_length([sch] + START, START))
    b = row([2, 2], g12.description_length([memo] + START, START))
    assert a["S"] == 0.75 and b["S"] == 1.0 and row([1, 1], 4)["S"] == 0


# ---------------------------------------------------------------- folds
def test_folds_seeded_disjoint_halves():
    fams = ["f%02d" % i for i in range(12)]
    a = g12.folds(fams, 25)
    assert a == g12.folds(list(reversed(fams)), 25)
    assert len(a[0]) == len(a[1]) == 6 and not set(a[0]) & set(a[1]) and set(a[0]) | set(a[1]) == set(fams)
    assert any(g12.folds(fams, s) != a for s in range(26, 40))


# ---------------------------------------------------------------- traps
def test_root_split_and_near_miss():
    assert g12.root_split("(acc + {H})") == ("add", "acc", "{H}")
    assert g12.root_split("({H} * v)") == ("mul", "{H}", "v")
    assert g12.root_split("math.gcd(abs(acc), abs({H}))") == ("gcd", "acc", "{H}")
    assert g12.root_split("pow({H}, 2)") == ("powr", "{H}", "2")
    assert g12.root_split("((acc + v) - {H})") == ("sub", "(acc + v)", "{H}")
    assert g12.root_split("acc") is None
    der = [{"schema": "(acc + {H})", "n_pairs": 3}, {"schema": "({H} + v)", "n_pairs": 1}]
    w, meta = g12.near_miss(der, 25)
    src = meta["source"]
    assert src == "(acc + {H})" and w and w != src and g12.root_split(w)[1:] == ("acc", "{H}")
    assert g12.near_miss(der, 25) == (w, meta)                    # deterministic
    assert w not in [d["schema"] for d in der] and w in meta["alternatives"]
    assert g12.near_miss([], 25) == (None, "no_derived_schema")
    import tier3d as T3D
    import instruments as INS
    assert len(T3D.instantiate(w)) >= 2 and not INS.equal_extensional(w, src)


def test_near_miss_prefers_dev_consistent_alternative():
    """Attractiveness = number of validation cells with a dev-consistent program (no tribunal, no transfer)."""
    import a17
    der = [{"schema": "(acc + {H})", "n_pairs": 3}]
    # dev examples generated by the witness fold (0, (acc * v), acc): only multiplicative alternatives fit them
    prov = a17.Prov({"fam": ("(acc * v)", "acc", "1")})
    import fair as FR
    cells = [FR.Cell(prov, "fam", r, 6, label="G12-TEST") for r in range(3)]
    w, meta = g12.near_miss(der, 25, cells)
    assert meta["dev_consistent_cells"] == max(meta["alternatives"].values())
    assert meta["dev_consistent_cells"] >= 1 and w == "(acc * {H})"


def test_memo_plant_is_verbatim():
    cls = [{"observed": [["fold", "0", "(acc + v)", "acc"], ["fold", "0", "(acc + v)", "acc"]]},
           {"observed": [["expr", "first"], ["fold", "1", "(acc * v)", "last"]]}]
    p = g12.memo_plant(cls)
    assert [(e["inits"], e["bodies"], e["finals"]) for e in p] == [(["0"], ["(acc + v)"], ["acc"]),
                                                                    (["1"], ["(acc * v)"], ["last"])]


# ---------------------------------------------------------------- per-cell reach rule
class _C:
    def __init__(self, f, r):
        self.family, self.r = f, r


def _w(ch, cens):
    return {"charge": ch, "censored": cens, "program": None if cens else ["fold", "0", "v", "acc"]}


def test_reach_is_per_cell_against_inherited():
    cells = [_C("a", 0), _C("a", 1), _C("b", 0), _C("b", 1), _C("c", 0)]
    cap = 100
    W = {"INHERITED": [_w(cap, True), _w(10, False), _w(5, False), _w(cap, True), _w(cap, True)],
         "X": [_w(50, False), _w(cap, True), _w(4, False), _w(cap, True), _w(cap, True)],     # a reached (cell 0)
         "Y": [_w(cap, True), _w(3, False), _w(3, False), _w(cap, True), _w(7, False)]}       # only c reached
    cands = {k: START for k in W}
    t = g12.table_from_walks(W, cands, START, cells, [["a", "b"], ["c"]], {k: k for k in W}, cap)
    assert t["X"]["reached_families"] == ["a"] and t["X"]["reach_by_fold"] == [1, 0]
    assert t["Y"]["reached_families"] == ["c"] and t["Y"]["reach_by_fold"] == [0, 1]
    assert t["X"]["saving"] == (cap - 50) + (10 - cap) + (5 - 4) and t["INHERITED"]["saving"] == 0


def test_rescore_at_full_cap_reproduces_table():
    rng = random.Random(5)
    ids = [["f%d" % (i // 4), i % 4] for i in range(48)]
    fams = sorted({f for f, _ in ids})
    fs = g12.folds(fams, 30)
    walks, table = {}, {}
    for n in ["INHERITED", "A", "B", "C"]:
        walks[n] = [[rng.choice([g12.SEL_CAP, rng.randint(1, g12.SEL_CAP)]), False, None] for _ in ids]
        for w in walks[n]:
            w[1] = w[0] == g12.SEL_CAP
    cells = [_C(f, r) for f, r in ids]
    W = {n: [{"charge": c, "censored": z, "program": None} for c, z, _ in v] for n, v in walks.items()}
    t = g12.table_from_walks(W, {n: START for n in W}, START, cells, fs, {n: n for n in W})
    rec = {"g12": {"params": g12.params(), "cell_ids": ids, "folds": fs, "walks": walks,
                   "table": {n: dict(v) for n, v in t.items()}}}
    tab, arms = g12.rescore(rec)
    for n in t:
        assert tab[n]["reach_by_fold"] == t[n]["reach_by_fold"] and tab[n]["saving"] == t[n]["saving"]
    assert arms["g12"] == g12.choose(t)


# ---------------------------------------------------------------- real donors (slow; exposed Beta-02 seed 26)
E12 = g12.paths.ROOT / "beta02" / "runs" / "E12" / "E12_DONORS.jsonl"
KEYS = ("selected", "selected_schema", "selected_origin", "selected_entries", "n_observed", "n_derived", "classes")


def _e12(seed, tag):
    for x in E12.read_text(encoding="utf-8").splitlines():
        r = json.loads(x)
        if r["seed"] == seed and r["tag"] == tag:
            return r
    raise KeyError((seed, tag))


@pytest.mark.slow
def test_reset_and_continuity_in_one_worker():
    """One worker, in order: g12 (plants) -> b02 g10_O4 -> g12-off g0_O4 -> b02 g11_O4. Seed 26 (exposed).
    After a g12 job the b02 g10 and the unpatched donor must reproduce the Beta-02 E12 rows exactly."""
    import b02
    from concurrent.futures import ProcessPoolExecutor
    P = b02.rj(b02.SUP / "PLAN_E.json")
    s, fams, pn = 26, P["plan"]["26"]["O4"], P["panel"]
    jobs = [("g12", ("g12_O4", "g12", "O4", s, fams, pn, None)),
            ("b02", ("g10_O4", "g10", "O4", s, fams, pn, None)),
            ("g12", ("g0_O4", "off", "O4", s, fams, pn, None)),
            ("b02", ("g11_O4", "g11", "O4", s, fams, pn, None))]
    with ProcessPoolExecutor(max_workers=1, initializer=b02.T.init_worker) as ex:
        out = list(ex.map(g12.run_job, jobs))
    assert "g12" in out[0] and out[0]["g12"]["n_walks"] > 0
    for r, tag in zip(out[1:], ("g10_O4", "g0_O4", "g11_O4")):
        ref = _e12(s, tag)
        assert all(r[k] == ref[k] for k in KEYS), (tag, [k for k in KEYS if r[k] != ref[k]])


@pytest.mark.slow
def test_fast_prefix_equals_full_walks_on_real_cells():
    """walk_table with FAST_PREFIX == full first_qualified walks (exposed seed 26 VALIDATE families, cap 100k)."""
    import a17
    import a18
    import b02
    import fair as FR
    b02.T.init_worker()
    P = b02.rj(b02.SUP / "PLAN_E.json")
    fams = [f for f in P["plan"]["26"]["O10"] if f["role"] == "VALIDATE"][:3]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fams}
    prov = a17.Prov(specs)
    cells = [FR.Cell(prov, f["name"], 26 * 4 + j, f["Q2_size"], label="%s-LIN26-val/r26" % a18.TAG)
             for f in fams for j in range(2)]
    start = FR.pristine().entries
    cands = {"INHERITED": start}
    for k, s in enumerate(["(acc + {H})", "({H} + v)", "({H} * v)", g12.gtc.OFF_SCHEMA]):
        cands["S%d" % k] = [a17.schema_entry("g2_new", s)] + start
    cands["M"] = [{"name": "m", "inits": ["0"], "bodies": ["(acc + v)"], "finals": ["acc"]}] + start
    out = {}
    for fast in (True, False):
        g12.FAST_PREFIX = fast
        out[fast], _ = g12.walk_table(cands, cells, prov, g12.SEL_CAP, start)
    g12.FAST_PREFIX = True
    for n in cands:
        for a, b in zip(out[True][n], out[False][n]):
            assert a["censored"] == b["censored"], n
            if not a["censored"]:
                assert (a["charge"], a["program"]) == (b["charge"], b["program"]), n
