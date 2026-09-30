"""RB-2 BRIDGE PANEL (forensic, not a disposition).

13 families scored under BOTH the old MetaTribunal (engine/meta_tribunal.py,
untouched) and TRIBUNAL_T4 (engine/tribunal_t4.py):
  5 from AMENDMENT 17 catalog A, 4 from the K2 admissible pool, 4 successor-
  world families (2 designed, 2 drawn from the RB-2 V7 census survivors).
For each family: the witness artifact under both instruments (Q3-style), the
exact Q2 (a17.qualify under the panel name), the T4 family profile, and up to 5
near-miss artifacts (the first PRISTINE hits on a size-4 dev set) under both
instruments, with their extensional agreement with the witness.
Writes RB2_BRIDGE_PANEL.json.
"""
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rb2_common as C   # noqa: E402

HERE = C.HERE
A = C.a17
FR = C.FR
E = C.E


def panel():
    cat = json.loads((C.ENG / "A17_CATALOGS_2026-09-26.json").read_text())["A"]["families"]
    byname = {f["name"]: f for f in cat}
    fams = []
    for n in ("hA_add_ah", "hA_sub_az", "hA_fdiv_bf", "hA_gcd_al", "hA_gcd_bf"):
        f = byname[n]
        fams.append({"name": n, "source": "A17 catalog A (%s)" % f["role"],
                     "init": f["init"], "body": f["body"], "final": f["final"]})
    for n, (i, b, fi) in (("kb_mod_onemodaccv", ("0", "(1 % (acc - v))", "(last * acc)")),
                          ("kb_powr_lastdivv", ("0", "pow(acc, (last // v))", "(first * acc)")),
                          ("kb_mul_gcdvacc", ("0", "(1 * math.gcd(abs(v), abs(acc)))", "(last + acc)")),
                          ("kb_gcd_absaccv", ("1", "math.gcd(abs(0), abs((acc + v)))", "(acc + first)"))):
        fams.append({"name": n, "source": "K2 admissible pool", "init": i, "body": b, "final": fi})
    fams.append({"name": "s_alt_sum", "source": "successor (designed): alternating sum",
                 "init": "0", "body": "(v - acc)", "final": "acc"})
    fams.append({"name": "s_product", "source": "successor (designed): product, growth-bounded domain",
                 "init": "1", "body": "(acc * v)", "final": "acc"})
    # two census survivors of the successor world: V7-admissible (widened inits),
    # non-additive, Q2-passing, not extensionally G1, with a T4-qualified solve;
    # the first in draw order for each of two mechanism classes.
    rows = json.loads((HERE / "RB2_CENSUS_ROWS.json").read_text())["rows"]
    g1 = {tuple(json.loads(k)): v for k, v in json.loads((HERE / "RB2_G1EXT.json").read_text()).items()}
    sol = {}
    for line in (HERE / "RB2_SOLVE.jsonl").read_text().splitlines():
        o = json.loads(line)
        sol[tuple(o["prog"])] = o
    for cls in ("NA_GCD", "AFFINE_SCALE_V"):
        for r in rows:
            pr = (r["init_WIDE"], r["body"], r["final"])
            if r["body_class"] == cls and r["profile_WIDE"]["admissible"] and pr in sol and pr in g1                     and g1[pr] is None and (sol[pr]["PRISTINE"].get("qualified_T4", 0) + sol[pr]["L1"].get("qualified_T4", 0)):
                fams.append({"name": "s_census_" + cls.lower(), "source": "successor (RB-2 V7 census survivor, %s)" % cls,
                             "init": pr[0], "body": pr[1], "final": pr[2]})
                break
    return fams


def score_both(prov, name, prog):
    A.M.use_provider(prov)
    C.T4.use_provider(prov)
    art = A.M.artifact_for(name, prog, A.EMITTER)
    old = A.M.MetaTribunal.after_freeze(art, name)
    so = old.score(art)
    t4 = C.T4.TribunalT4.after_freeze(art, name)
    s4 = t4.score(art)
    return {"OLD": dict(so, qualified=old.qualified(so)), "T4": dict(s4, qualified=t4.qualified(s4))}


def ext_equal(p, q, n=300):
    rng = random.Random("bridge-ext")
    for _ in range(n):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(2, 60))]
        m = rng.randint(1, 97)
        if C.FE.run_program(p, xs + [m], True) != C.FE.run_program(q, xs + [m], True):
            return False
    return True


def job(f):
    name = f["name"]
    prov = A.Prov({name: (f["body"], f["final"], f["init"])})
    w = ("fold", f["init"], f["body"], f["final"])
    out = dict(f)
    out["Q2_size"] = A.qualify(prov, name, "RB2-BRIDGE")
    out["body_class"] = C.body_class(f["body"])
    out["T4_profile"] = C.T4.family_profile(w)
    out["witness"] = score_both(prov, name, w)
    cell = FR.Cell(prov, name, 0, 4, label="RB2-BRIDGE-NEARMISS")
    esc = E.Escrow(A.ESCROW)
    hits = FR.search_collect(FR.pristine(), cell.parsed, esc, A.ESCROW, cell.seed, max_hits=5)
    out["near_misses"] = []
    for prog, coord, ch in hits:
        s = score_both(prov, name, prog)
        out["near_misses"].append({"program": list(prog), "charges": ch,
                                   "extensionally_equal_to_witness": ext_equal(prog, w),
                                   "OLD_qualified": s["OLD"]["qualified"], "T4_qualified": s["T4"]["qualified"],
                                   "OLD": s["OLD"], "T4": s["T4"]})
    o, t = out["witness"]["OLD"]["qualified"], out["witness"]["T4"]["qualified"]
    why = []
    if o != t:
        if not o:
            why += ["OLD fails: " + ", ".join(k for k in ("held_out_extrapolation", "stress_length_200",
                                                         "counterexample_accuracy")
                                             if out["witness"]["OLD"][k] < 0.99)]
            if not out["witness"]["OLD"]["metamorphic_pass"]:
                why.append("OLD fails permutation invariance")
        if not t:
            why.append("T4 rejects family: %s" % out["witness"]["T4"]["family_reasons"])
    out["disagreement"] = o != t
    out["disagreement_mechanics"] = why
    out["near_miss_disagreements"] = sum(nm["OLD_qualified"] != nm["T4_qualified"] for nm in out["near_misses"])
    out["wrong_artifact_admitted"] = {
        "OLD": sum(nm["OLD_qualified"] and not nm["extensionally_equal_to_witness"] for nm in out["near_misses"]),
        "T4": sum(nm["T4_qualified"] and not nm["extensionally_equal_to_witness"] for nm in out["near_misses"])}
    return out


if __name__ == "__main__":
    fams = panel()
    with ProcessPoolExecutor(C.WORKERS, initializer=C.worker_init) as ex:
        rows = list(ex.map(job, fams, chunksize=1))
    summ = [{"name": r["name"], "source": r["source"], "prog": [r["init"], r["body"], r["final"]],
             "body_class": r["body_class"], "Q2": r["Q2_size"],
             "OLD_q3": r["witness"]["OLD"]["qualified"], "T4_q3": r["witness"]["T4"]["qualified"],
             "OLD_components": {k: r["witness"]["OLD"][k] for k in ("held_out_extrapolation", "stress_length_200",
                                                                    "counterexample_accuracy", "metamorphic_pass")},
             "T4_components": {k: r["witness"]["T4"][k] for k in ("held_out_extrapolation", "stress_at_domain_max",
                                                                  "counterexample_accuracy", "order_battery_accuracy",
                                                                  "domain_L_max", "family_reasons")},
             "disagreement": r["disagreement"], "mechanics": r["disagreement_mechanics"],
             "near_misses": len(r["near_misses"]), "near_miss_disagreements": r["near_miss_disagreements"],
             "wrong_artifact_admitted": r["wrong_artifact_admitted"]} for r in rows]
    (HERE / "RB2_BRIDGE_PANEL.json").write_text(json.dumps({"forensic": "not a disposition", "summary": summ,
                                                            "detail": rows}, indent=1))
    for s in summ:
        print("%-26s OLD=%-5s T4=%-5s Q2=%-4s %s | %s | nm=%d nmdis=%d wrong=%s" % (
            s["name"], s["OLD_q3"], s["T4_q3"], s["Q2"], s["OLD_components"], s["T4_components"],
            s["near_misses"], s["near_miss_disagreements"], s["wrong_artifact_admitted"]))
