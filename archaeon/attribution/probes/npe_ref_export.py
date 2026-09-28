"""Reference per-locus OUTPUT (data only) for the burned first G2 set, Nestor's export shape; base labels in Nestor's string form."""
import ast, json, gzip, sys
from archaeon.attribution.probes.npe_fixture_validate import load_ref, ARC
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
    return [k, repr(l[1:])]
out = gzip.open(sys.argv[1], "wt", newline="\n")
for line in open(ARC + "/npe_fixture_validation/nestor_v2_FUZZ_AGREEMENT_nestor.jsonl"):
    rec = json.loads(line); pre = ast.literal_eval(rec["pre"]) if isinstance(rec["pre"], str) else rec["pre"]
    r = R.trace_interaction(bytes.fromhex(pre["ga"]), bytes.fromhex(pre["gb"]), (pre["regs_a"],) + tuple(pre["flags_a"]),
                            (pre["regs_b"],) + tuple(pre["flags_b"]), budget=pre["budget"], ops_mask=pre["ops_mask"])
    loci = {}
    for h, side in enumerate("ab"):
        L = []
        for j in range(R.N):
            y = r["loci"][h * R.N + j]
            x = {"j": j, "label": lab(y["label"]), "written": y["written"], "addr": sorted(b(q) for q in y["addr_deps"])}
            if y["written"]:
                x.update({"store_by": y["store_by"], "performer": lab(y["performer"]), "ctrl": sorted(b(q) for q in y["ctrl_deps"]),
                          "ctrl_slice": sorted(b(q) for q in y["ctrl_deps_slice"]), "exec": sorted(b(q) for q in y["exec_deps"])})
            L.append(x)
        loci[side] = L
    out.write(json.dumps({"k": rec["k"], "loci": loci}, sort_keys=True) + "\n")
out.close()
