"""Nestor's INDEPENDENT raw comparison of the G2 fresh set (C9 s5(d)): my frozen v2 output (c6aa5569...) vs the reference
output (9fd3bc44...). RAW equality, no canonicalization. Classes: unwritten / written_self / written_other /
written_perf_none (performer entity vs store_by), and MUTATION (mutated loci, set M) as its own class. Gate: >= 0.995 per
class per gated field (label, addr, ctrl, exec, written, store_by, performer); ctrl_slice is reported (secondary).
Declared diagnostics (Archaeon #859; they cannot rescue the gate): non-mutated loci only; MUTATION content
(flag, side, pos, old_label)."""
import gzip, json, sys
from collections import defaultdict

GATED = ("label", "addr", "ctrl", "exec", "written", "store_by", "performer")


def cls_of(r):
    if r.get("mutated"):
        return "MUTATION"
    if not r["written"]:
        return "unwritten"
    p = r.get("performer")
    pe = p[1] if p and p[0] == "E" else None
    return "written_perf_none" if pe is None else ("written_self" if pe == r["store_by"] else "written_other")


def main(mine_p, ref_p):
    mine = {json.loads(l)["k"]: json.loads(l) for l in open(mine_p, encoding="utf-8")}
    ref = {json.loads(l)["k"]: json.loads(l) for l in gzip.open(ref_p, "rt", encoding="utf-8")}
    assert sorted(mine) == sorted(ref), "record sets differ"
    agree = defaultdict(lambda: [0, 0])
    diag = defaultdict(lambda: [0, 0])
    examples = []
    for k in sorted(mine):
        a, b = mine[k], ref[k]
        st = a["set"]
        for half in ("a", "b"):
            for ra, rb in zip(a["loci"][half], b["loci"][half]):
                c_mine, c_ref = cls_of(ra), cls_of(rb)
                c = c_ref                                          # class key = the reference's (as in C9 s3)
                if c_mine != c_ref:
                    agree[(st, c, "class_key")][1] += 1
                else:
                    agree[(st, c, "class_key")][0] += 1; agree[(st, c, "class_key")][1] += 1
                fields = GATED + ("ctrl_slice",)
                for f in fields:
                    if c == "unwritten" and f not in ("label", "addr", "written"):
                        continue
                    if c == "MUTATION" and f not in ("label", "addr", "written"):
                        continue
                    eq = ra.get(f) == rb.get(f)
                    agree[(st, c, f)][0] += eq; agree[(st, c, f)][1] += 1
                    if not eq and len(examples) < 12 and f != "ctrl_slice":
                        examples.append({"k": k, "set": st, "half": half, "j": ra["j"], "class": c, "field": f,
                                         "mine": ra.get(f), "ref": rb.get(f)})
                if c == "MUTATION":
                    ma, mb = ra.get("mutation") or {}, rb["label"]
                    same = (ra.get("mutated") == rb.get("mutated") and ma.get("side") == mb[1] and ma.get("pos") == mb[3]
                            and ma.get("old_label") == mb[4])
                    diag[(st, "MUTATION_content(flag,side,pos,old_label)")][0] += same
                    diag[(st, "MUTATION_content(flag,side,pos,old_label)")][1] += 1
    table = {"%s|%s|%s" % key: [v[0], v[1], round(v[0] / v[1], 4) if v[1] else None] for key, v in sorted(agree.items())}
    gate = {}
    for (st, c, f), (x, n) in agree.items():
        if f in GATED and n:
            gate.setdefault(st, []).append((x / n, "%s|%s" % (c, f)))
    verdict = {st: ("PASS" if min(v)[0] >= 0.995 else "FAIL (min %.4f at %s)" % min(v)) for st, v in gate.items()}
    out = {"table": table, "verdict_raw": verdict,
           "diagnostics": {"%s|%s" % k: v for k, v in diag.items()}, "first_discrepancies": examples}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
