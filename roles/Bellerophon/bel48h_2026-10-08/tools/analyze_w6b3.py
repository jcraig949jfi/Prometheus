"""BEL-48H W6 block 3 analysis (rules: prereg s12; committed before the runs).   python3 analyze_w6b3.py RESULTS OUT"""
import json, sys, pathlib
from collections import Counter
from analyze_w2 import wilson
from analyze_w4 import cls_repair


def out_from_child(tape_hex, cfg_like=None):
    """ENTANGLED_FLOW test: executed alone (input 77), is the first OUT_A executed from the CHILD copy in the window
    ([L,2L)) rather than from the organism's own tape ([0,L))?  Returns (out_in_child, out_in_self)."""
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas import vm
    t = bytes.fromhex(tape_hex); L = 64
    mem = bytearray(256); mem[:L] = t[:L]; mem[vm.IN_BASE] = 77
    tr = vm.execute(mem, L, 0, 256, [77], trace_pcs=True)
    pcs = tr.pcs or set()
    in_child = any(L <= p < 2 * L and mem[p] == vm.OUT_A for p in pcs)
    in_self = any(p < L and t[p] == vm.OUT_A for p in pcs)
    return in_child, in_self


def budget_class(tape_hex, shared):
    """BUDGET_COUPLED: a shared critical byte whose NOP knockout kills competence at the world's budget (256) but NOT at
    budget 512 -- reproduction and computation compete for one execution budget. OTHER_SHARED: a shared byte whose
    knockout kills competence at both budgets (e.g. an opcode knockout that exposes its operand as an instruction).
    Returns 'BUDGET_COUPLED' | 'OTHER_SHARED' | 'SEPARATED' (no shared byte)."""
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas.tasks import Task, verify_exact
    t = bytes.fromhex(tape_hex)
    if not shared:
        return "SEPARATED"
    def comp(x, budget):
        return bool(verify_exact(x, 64, Task("ECHO"), "ABR", budget, "SHARED", False))
    kinds = set()
    for p in shared:
        u = bytearray(t); u[p] = 0
        kinds.add("BUDGET_COUPLED" if (not comp(bytes(u), 256) and comp(bytes(u), 512)) else "OTHER_SHARED")
    return "BUDGET_COUPLED" if "BUDGET_COUPLED" in kinds else "OTHER_SHARED"


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    out = {"n": len(R) + len(voids), "voids": len(voids)}
    end = lambda r: r["comp"]["comp_func_alive"] > 0 and r["comp"].get("dominant")
    k1 = [r for r in R if r["lane"] == "K1" and end(r)]
    shared = sum(1 for r in k1 if r["comp"]["dominant"]["shared"])
    flow = [out_from_child(r["comp"]["dominant"]["tape"])[0] for r in k1]
    bc = Counter(budget_class(r["comp"]["dominant"]["tape"], r["comp"]["dominant"]["shared"]) for r in k1)
    out["K1"] = {"runs": sum(1 for r in R if r["lane"] == "K1"), "competent_machines": len(k1), "shared": shared,
                 "out_executed_in_child_copy": sum(flow), "budget_classes": dict(bc)}
    out["E-P1"] = {"shared": [shared, len(k1)], "wilson": wilson(shared, len(k1)), "holds": bool(k1) and shared / len(k1) >= 0.5}
    bcn = bc.get("BUDGET_COUPLED", 0)
    out["E-P2"] = {"budget_coupled": [bcn, len(k1)], "wilson": wilson(bcn, len(k1)), "holds": bool(k1) and bcn / len(k1) >= 0.35}
    k2 = [r for r in R if r["lane"] == "K2" and end(r)]
    cl = Counter(cls_repair(r["comp"]["dominant"]) for r in k2)
    out["K2"] = {"runs": sum(1 for r in R if r["lane"] == "K2"), "repaired_machines": len(k2), "classes": dict(cl)}
    out["E-P3"] = {"modal": cl.most_common(1)[0][0] if cl else None, "holds": bool(cl) and cl.most_common(1)[0][0] == "SINGLE_LINEAGE_BAD"}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
