"""Step 2: where does register fragility come from?
(a) Reproduce s10 (own context, own entry, HALT partner, 30 random register files + flags per genome, same seeds).
(b) Failure anatomy under those 30 random contexts (taint interpreter, validated in s1): did the child copy op
    (same pc as under FRESH) execute at all (else PATH), and if so were src / dst / count what FRESH gave?
(c) Split randomization: randomize ONLY the registers/flags that the child copy's operands inherit (data taint),
    keep the rest FRESH; and the converse (randomize everything EXCEPT them). If operand inheritance is the
    mechanism, (c1) ~ all-random and (c2) ~ FRESH.
(d) Inherited operand counts per side, and the 'free-zero' reading: is the inherited operand the one whose
    required value is FRESH-reachable (0 or 0 +- a few through INC/DEC)?"""
import json, pathlib, random, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
sys.path.insert(0, str(HERE))
from _env import A, ROWS                      # noqa: E402
from s10_side0_register_dependence import trial   # noqa: E402
from s1_operand_taint import SEL, own_run, child_copy   # noqa: E402
from _taint import REGSET                     # noqa: E402

IDX = {"B": 0, "C": 1, "D": 2, "E": 3, "H": 4, "L": 5, "A": 7}


def randsets(key):
    rr = random.Random("W2-16-regs-" + key)        # identical to s10
    return [([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2)) for _ in range(30)]


def mix(rs, keep_fresh=(), only=None):
    regs, fz, fc = list(rs[0]), rs[1], rs[2]
    names = set(IDX) | {"fz", "fc"}
    rnd = names - set(keep_fresh) if only is None else set(only)
    regs = [regs[i] if any(IDX.get(n) == i for n in rnd) else 0 for i in range(8)]
    return regs, (fz if "fz" in rnd else 0), (fc if "fc" in rnd else 0)


def fisher_2x2(a, b, c, d):
    from math import comb
    n = a + b + c + d; r1 = a + b; c1 = a + c
    def p(x): return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
    p0 = p(a)
    return sum(p(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if p(x) <= p0 * (1 + 1e-9))


if __name__ == "__main__":
    out = {"per_genome": {}, "summary": {}}
    for s in (0, 1):
        agg = collections.Counter()
        for r in SEL[s]:
            G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
            f = own_run(G, s); cp, _ = child_copy(f, s)
            if cp is None:
                continue
            data_inh = sorted((set(cp["t_src"]) | set(cp["t_dst"]) | set(cp["t_cnt"])) & REGSET)
            ctrl_inh = sorted(set(cp["ctrl"]) & REGSET)
            sets = randsets(r["key"])
            rec = collections.Counter()
            for rs in sets:
                good_all = trial(z, P, G, s, rs)
                rec["all_random_good"] += good_all
                rec["opd_only_random_good"] += trial(z, P, G, s, mix(rs, only=data_inh))
                rec["non_opd_random_good"] += trial(z, P, G, s, mix(rs, keep_fresh=data_inh))
                rec["opd_and_ctrl_fresh_good"] += trial(z, P, G, s, mix(rs, keep_fresh=set(data_inh) | set(ctrl_inh)))
                # anatomy (taint interpreter, same context)
                t = own_run(G, s, rs)
                same = [c for c in t["copies"] if c["pc"] == cp["pc"]]
                if t["good"]:
                    cls = "GOOD"
                elif not same:
                    cls = "PATH(no copy at FRESH pc)"
                else:
                    c0 = same[0]
                    bad = []
                    if c0["src"] != cp["src"]: bad.append("src")
                    if c0["dst"] != cp["dst"]: bad.append("dst")
                    if c0["n"] < min(cp["n"], 64): bad.append("count")
                    cls = "OPERAND(" + "+".join(bad) + ")" if bad else "COLLATERAL(operands ok)"
                rec["anat:" + cls] += 1
            rec = dict(rec)
            rec.update({"data_inherited": data_inh, "ctrl_inherited": ctrl_inh})
            out["per_genome"][r["key"]] = rec
            for k, v in rec.items():
                if isinstance(v, int):
                    agg[k] += v
            agg["genomes"] += 1
            agg["trials"] += 30
        out["summary"]["side%d" % s] = dict(sorted(agg.items()))
        print(s, out["summary"]["side%d" % s])
    # operand inheritance contrast (from s1)
    s1 = json.loads((HERE / "s1_operand_taint.json").read_text())
    con = {}
    for s in (0, 1):
        recs = [v for v in s1["side%d" % s].values() if v.get("op")]
        con["side%d" % s] = {
            "n": len(recs),
            "dst_inherited": sum(v["dst_from"].startswith("INH") for v in recs),
            "src_inherited": sum(v["src_from"].startswith("INH") for v in recs),
            "cnt_inherited": sum(v["cnt_from"].startswith("INH") for v in recs),
            "addr_operand_inherited_any": sum(v["dst_from"].startswith("INH") or v["src_from"].startswith("INH") for v in recs),
            "both_addr_from_code_or_ctx": sum(not v["dst_from"].startswith("INH") and not v["src_from"].startswith("INH") for v in recs),
            "all_three_not_inherited": sum(not any(v[o + "_from"].startswith("INH") for o in ("src", "dst", "cnt")) for v in recs),
        }
    a, b = con["side1"]["dst_inherited"], con["side1"]["n"] - con["side1"]["dst_inherited"]
    c, d = con["side0"]["dst_inherited"], con["side0"]["n"] - con["side0"]["dst_inherited"]
    con["fisher_dst_inherited"] = fisher_2x2(a, b, c, d)
    a, b = con["side1"]["both_addr_from_code_or_ctx"], con["side1"]["n"] - con["side1"]["both_addr_from_code_or_ctx"]
    c, d = con["side0"]["both_addr_from_code_or_ctx"], con["side0"]["n"] - con["side0"]["both_addr_from_code_or_ctx"]
    con["fisher_both_addr_set"] = fisher_2x2(a, b, c, d)
    # free-zero reading: per address operand, value class vs inherited
    fz = collections.Counter()
    for s in (0, 1):
        for v in s1["side%d" % s].values():
            if not v.get("op"):
                continue
            for o in ("src", "dst"):
                val = v[o]
                near0 = min(val, 128 - val) <= 4
                fz[("side%d" % s, o, "near0" if near0 else "far", "INH" if v[o + "_from"].startswith("INH") else "SET")] += 1
    con["free_zero_table"] = {"|".join(k): n for k, n in sorted(fz.items())}
    out["operand_contrast"] = con
    print(json.dumps(con, indent=1))
    (HERE / "s2_fragility_decomposition.json").write_text(json.dumps(out, indent=1))
