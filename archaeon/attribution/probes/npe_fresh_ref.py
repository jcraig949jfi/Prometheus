"""Frozen reference on the G2 FRESH set (C9 s5(d)). Writes per-locus output in Nestor's export shape. Set M loci are taken AFTER
write-back (rng = random.Random(wb_seed), mut_rate from the record); a MUTATION label is exported as ["M", [side, k, pos], old_label] (C10 s3(a), SPEC_ISSUES E3).
    python -m archaeon.attribution.probes.npe_fresh_ref PRE.jsonl OUT.jsonl.gz
"""
import gzip
import json
import random
import sys

from archaeon.attribution.probes.npe_fixture_validate import load_ref

R = load_ref()
RI = {r: i for i, r in enumerate(R.REGN)}


def b(l):
    k = l[0]
    if k == "ENTITY": return "E|%s|%d" % (l[1], l[2])
    if k == "PREG": return "P|%s|%s" % (l[1], RI.get(l[2], l[2]))
    if k == "CONTEXT": return "X|%s" % l[1]
    return "|".join(map(str, l))


def lab(l):
    if l is None: return None
    k = l[0]
    if k == "ENTITY": return ["E", l[1], l[2], l[3] if len(l) > 3 else l[1]]
    if k == "CONST": return ["K", l[1]]
    if k == "CONTEXT": return ["X", l[1]]
    if k == "PREG": return ["P", l[1], RI.get(l[2], l[2])]
    if k == "COMPUTED": return ["C", sorted(b(x) for x in l[1])]
    if k == "COMPUTED_FROM": return ["F", lab(l[1])]
    if k == "MUTATION": return ["M", [l[1][0], l[1][1], l[1][2]], lab(l[2])]      # C10: ["M", [side, k, pos], old_label]
    return [k, repr(l[1:])]


def main(pre_path, outp):
    out = gzip.open(outp, "wt", newline="\n")
    for line in open(pre_path):
        rec = json.loads(line); p = rec["pre"]
        rng = random.Random(rec["wb_seed"]) if rec["set"] == "M" else None
        kw = {"rng": rng, "mut_rate": rec["mut_rate"]} if rng else {}
        r = R.trace_interaction(bytes.fromhex(p["ga"]), bytes.fromhex(p["gb"]), (p["regs_a"],) + tuple(p["flags_a"]),
                                (p["regs_b"],) + tuple(p["flags_b"]), budget=p["budget"], ops_mask=p["ops_mask"], **kw)
        loci = {}
        for h, side in enumerate("ab"):
            L = []
            for j in range(R.N):
                y = r["loci"][h * R.N + j]
                x = {"j": j, "label": lab(y["label"]), "written": y["written"], "mutated": y["mutated"],
                     "addr": sorted(b(q) for q in y["addr_deps"])}
                if y["written"]:
                    x.update({"store_by": y["store_by"], "performer": lab(y["performer"]), "ctrl": sorted(b(q) for q in y["ctrl_deps"]),
                              "ctrl_slice": sorted(b(q) for q in y["ctrl_deps_slice"]), "exec": sorted(b(q) for q in y["exec_deps"])})
                L.append(x)
            loci[side] = L
        out.write(json.dumps({"k": rec["k"], "set": rec["set"], "loci": loci}, sort_keys=True) + "\n")
    out.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
