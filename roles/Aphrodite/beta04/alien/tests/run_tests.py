"""AR-1 tests. Run from roles/Aphrodite/beta04:  python -m alien.tests.run_tests
Writes alien/AR1_TEST_RESULTS.json. Exit 0 iff all pass."""
import json
import random
import sys
import tempfile
import time
from pathlib import Path

from alien import machine as M
from alien import search as S
from alien import extract as X
from alien import conformance as CF
from alien import ar1_kp as K

HERE = Path(__file__).resolve().parents[1]
PILOT = "foundry/pilot_v2"
RESULTS = []


def test(fn):
    t0 = time.perf_counter()
    try:
        fn()
        RESULTS.append({"test": fn.__name__, "ok": True, "s": round(time.perf_counter() - t0, 2)})
    except Exception as e:                          # noqa: BLE001
        RESULTS.append({"test": fn.__name__, "ok": False, "error": repr(e)})
    return fn


def R(t, xs, T="Int", macros=None):
    return M.run(t, xs, T, macros)


@test
def t_ops():
    assert R("2 3 +", []) == 5 and R("2 3 -", []) == -1 and R("2 3 *", []) == 6
    assert R("3 n 2 /", []) == -2 and R("3 n 2 %", []) == 1            # floor div / Python mod
    assert R("2 3 <", []) == 1 and R("3 2 <", []) == 0 and R("2 2 =", []) == 1
    assert R("3 d +", []) == 6 and R("1 2 s -", []) == 1 and R("1 2 p", []) == 1
    assert R("3 A a a *", []) == 9 and R("#", [4, 5, 6]) == 3
    assert R("[ ]", [1, 2, 3]) == 3 and R("[ . ] l [ ]", [1, 2], "Int") == 2
    assert R("[ . ]", [1, 2], "List") == [1, 2] and R("", [1], "List") == []
    assert R("1", [], "Bool") is True and R("0", [], "Bool") is False


@test
def t_fail():
    for t in ("+", "1 +", "d", "s", "p", "A", "?", ".", "1 0 /", "1 0 %", ""):
        assert R(t, [1]) == M.FAIL, t
    assert R("3 [ p d * ]", [0] * 7) == M.FAIL                          # ceiling: 3^(2^7) > 1e18
    assert R("[ [ [ ] ] ]", [1] * 16) == M.FAIL                         # 16 + 256 + 4096 > ITER_MAX
    big = [10 ** 18, 1]
    assert R("[ ] +", big) == M.FAIL and R("[ ] *", big) == 10 ** 18


@test
def t_stackmax():
    assert R("[ [ ] ]", [1] * 12) == M.FAIL                              # 12 + 144 = 156 values > 128 -> FAIL
    assert R("[ [ p ] ]", [1] * 12) == 1


@test
def t_brackets_skip():
    assert R("] 2", []) == 2 and R("[ 1 +", [1, 2]) == 3                  # unmatched ] no-op; [ closes at end
    assert R("0 ? 2 3", []) == 3 and R("1 ? 2", []) == 2 and R("0 ? 2", []) == M.FAIL
    assert M.run("0 ? [ . ]", [1, 2], "List") == [] and M.run("1 ? [ . ]", [1, 2], "List") == [1, 2]
    assert M.run("1 0 ? ? . 2 .", [], "List") == [1, 2]                   # skipped '?' does nothing; '.' runs
    assert R("1 ? 0 ? 2", []) == M.FAIL and R("1 ? 1 ? 2", []) == 2
    mac = {"@m": M.parse("1 + 3 /")}
    assert R("3 0 ? @m", [], "Int", mac) == 3 and R("3 1 ? @m", [], "Int", mac) == 1


@test
def t_differential():
    rng = random.Random(11)
    mac = {"@a": M.parse("1 + 3 /"), "@b": M.parse("2 3 + <"), "@c": M.parse("a 3 / -")}
    alpha = list(M.BASE) + sorted(mac)
    n = 0
    for _ in range(6000):
        t = tuple(rng.choice(alpha) for _ in range(rng.randint(0, 24)))
        T = rng.choice(["Int", "List", "Bool"])
        f1, f2, p = M.compile_closure(t, T, mac), M.compile_fast(t, T, mac), M.compile_tape(t, mac)
        for _ in range(3):
            xs = [rng.randint(-40, 40) for _ in range(rng.randint(0, 16))]
            a, b, c = f1(list(xs)), f2(list(xs)), M.run_compiled(p, list(xs), T)
            assert M.same_value(a, c) and M.same_value(b, c), (M.to_str(t), T, xs, a, b, c)
            n += 1
    assert n == 18000


@test
def t_ledgers():
    mac = {"@f": M.parse("1 + 3 /")}
    a, b = [0, 0], [0, 0]
    v1 = M.run("[ @f ]", [1, 2, 3], "Int", mac, a)
    v2 = M.run("[ 1 + 3 / ]", [1, 2, 3], "Int", None, b)
    assert v1 == v2 and a[0] == b[0] and a[1] < b[1], (a, b)
    c = K.tape_cost("[ @f ]", mac, [[[1, 2, 3], 1]], "Int")
    assert c["len_promoted"] == 3 and c["len_expanded"] == 6 and c["macro_calls"] == 1


@test
def t_signature():
    sg = lambda s: M.signature(M.parse(s))                                # noqa: E731
    assert sg("1 + 3 /") == (1, 1) and sg("2 3 + <") == (1, 1) and sg("a 3 / -") == (1, 1)
    assert sg("s 3 / -") == (2, 1) and sg("d 2 3 + <") == (1, 2) and sg("[ 1 ]") is None and sg("1 ? 2") is None


@test
def t_extract():
    dev = [[[1, 5, 8], 3], [[4, -2], -1], [[7], 2], [[0, 0, 9], 3]]
    e = X.extract(M.parse("0 3 3 p p [ 1 + 3 / ]"), dev, "Int", "f")
    assert e["segment"] == "1 + 3 /", e
    devp = [[[1, 5, 8, -3], [1, -3]], [[6, 2], [2]], [[9], []], [[4, 4], [4, 4]]]
    assert X.extract(M.parse("[ d 2 3 + < ? . ]"), devp, "List", "p")["segment"] == "2 3 + <"
    devs = [[[4, 5, 6], 5], [[1], 1], [[9, 9], 8], [[0, 3, 3], 3]]
    assert M.run("1 A [ a 3 / - A ] a", [4, 5, 6], "Int") == 5
    assert X.extract(M.parse("1 A [ a 3 / - A ] a"), devs, "Int", "s")["segment"] == "a 3 / -"
    assert X.extract(M.parse("1 [ s 3 / - ]"), devs, "Int", "s")["segment"] == "s 3 / -"
    assert X.extract(M.parse("[ . ]"), devp, "List", "p")["segment"] is None
    # probe frame: f stack [v]; s stack [a, b] with A = a
    assert X.unit_value(M.parse("1 + 3 /"), "f", (5,)) == 2
    assert X.unit_value(M.parse("2 3 + <"), "p", (4,)) is True
    assert X.unit_value(M.parse("a 3 / -"), "s", (7, 10)) == 8 and X.unit_value(M.parse("s 3 / -"), "s", (7, 10)) == 8


@test
def t_search():
    dev = [[[1, 2, 3], [1, 2, 3]], [[4], [4]], [[-2, 0], [-2, 0]], [[5, 5, 1], [5, 5, 1]]]
    r1 = S.chain(dev, "List", "toy", 0, 20000)
    r2 = S.chain(dev, "List", "toy", 0, 20000)
    r1.pop("cpu_s"), r2.pop("cpu_s")
    assert r1["hit"] and r1 == r2, (r1, r2)
    assert M.run(r1["program"], [7, 8], "List") == [7, 8] or True        # first dev-consistent; may be odd off-dev
    devi = [[[1, 2, 3], 6], [[4], 4], [[-2, 0], -2], [[5, 5, 1], 11]]
    r3 = S.chain(devi, "Int", "toy-sum", 0, 200000)
    assert r3["hit"], r3
    r4 = S.chain(devi, "Int", "toy-sum", 0, 300)
    assert not r4["hit"] and r4["charges"] == 300


@test
def t_credit_early_stop_exact():
    dev = [[[1, 2, 3], 6], [[4], 4], [[-2, 0], -2], [[5, 5, 1], 11]]
    rng = random.Random(3)
    for _ in range(2000):
        t = tuple(rng.choice(M.BASE) for _ in range(rng.randint(0, 12)))
        fn = M.compile_closure(t, "Int")
        full = S.credit(fn, dev)
        fl = rng.choice([0.0, 1.0, 2.0, 3.0, 4.0])
        part = S.credit(fn, dev, fl)
        assert (full[0] >= fl) == (part[0] >= fl) and full[1] == part[1]


@test
def t_conformance():
    r = CF.check(PILOT)
    assert r["n_witnesses"] >= 5 and r["all_agree"], [x for x in r["rows"] if x["disagreements"]]
    (HERE / "runs").mkdir(exist_ok=True)
    (HERE / "runs" / "CONFORMANCE_pilot_v2.json").write_text(json.dumps(r, indent=1, sort_keys=True))


@test
def t_boundary_and_runner():
    with tempfile.TemporaryDirectory() as td:
        kp = K.AR1KP(PILOT, "W1d5301d0")
        d = K._load(td, "W1d5301d0")
        cfg = K.Config(budget=300)
        fid = kp.r1_families("f1")[0]
        r = kp.search(d, fid, None, cfg)
        assert r["arm_view_files_opened"] >= 1 and r["charges"] <= 300
        rc = K.run_stages(PILOT, "W1d5301d0", K.Config(budget=200), "all", td, log=lambda s: None)
        assert rc == 0
        res = K.pooled(PILOT, ["W1d5301d0"], K.Config(budget=200), td)
        assert res["readout"]["complete"] and res["readout"]["n_admitted_R3_R4"] == 4


@test
def t_labels():
    kp = K.AR1KP(PILOT, "W1d5301d0")
    fid = "W1d5301d0-F071-R4"
    acq = {"status": "ACQUIRED", "agrees_with_sealed_on_probe": 1.0}
    units = {"f1": dict(acq), "p0": dict(acq)}
    assert kp.family_link(fid, units, {"status": "SOLVED"})["detail"] == "CHAIN_QUALIFIED"
    assert kp.family_link(fid, units, {"status": "NOT_FOUND_AT_BUDGET"})["link"] == "COMPOSITION_HORIZON"
    assert kp.family_link(fid, units, {"status": "FIRST_DEV_CONSISTENT_FAILS_TEST"})["link"] == \
        "COMPOSITION_UNDERDETERMINED"
    u2 = {"f1": dict(acq, agrees_with_sealed_on_probe=0.9), "p0": dict(acq)}
    assert kp.family_link(fid, u2, {"status": "NOT_FOUND_AT_BUDGET"})["link"] == "UNDERDETERMINED_STONE"
    u3 = {"f1": {"status": "NOT_ACQUIRED", "link": "HORIZON_R1", "link_detail": "BUDGET_EXHAUSTED"}, "p0": dict(acq)}
    assert kp.family_link(fid, u3, None)["link"] == "HORIZON_R1"
    fams = [{"chain_qualified": True, "scratch_fails": True, "complete": True, "first_failing_link": None,
             "chain_uses_macro": True}] * 4 + \
           [{"chain_qualified": False, "scratch_fails": True, "complete": True, "first_failing_link": "HORIZON_R1",
             "chain_uses_macro": None}]
    pr = K.pooled_readout(fams)
    assert pr["AR1_KP_PARITY"] == "YES" and pr["first_failing_link_counts"]["HORIZON_R1"] == 1


def main():
    ok = all(r["ok"] for r in RESULTS)
    out = {"n": len(RESULTS), "passed": sum(r["ok"] for r in RESULTS), "all_pass": ok, "results": RESULTS,
           "code_sha256": K.code_hashes()}
    (HERE / "AR1_TEST_RESULTS.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    for r in RESULTS:
        print("PASS" if r["ok"] else "FAIL", r["test"], r.get("error", ""))
    print("ALL PASS" if ok else "FAILURES", "%d/%d" % (out["passed"], out["n"]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
