"""W2-42 a3: register-level trace (W2-24 tvm.pair_t, stock z8, checked == common.pair) of the side-0 placement for
F, C3, F+1=61, s1438 top0 (gid1798) and its KO 32 / KO 29, s1505 top0 / top1, on the first 200 N17e panel entries
(donor ZERO ctx, partner bank genome + carried regs; same panel as t2/a2). Per genome: FID keep at side 0; partner
(ctx 1) runs of the LDIR at donor pc 52; partner executions of each JP/JPcc in the donor half and where they land;
the donor-half pc at which partner context first enters; losses by whether the partner ran pc 52."""
import json, sys, pathlib, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
from tvm import C, pair_t  # noqa
from q1_trace import panel, mk  # noqa
import frames  # noqa

F = frames.IMP
G = {"F": F, "C3": mk(F, {43: 0xC3}), "F+1=61": mk(F, {1: 0x61})}
X = json.loads((HERE / "r1_FULL_1438.json").read_text())
g38 = bytes.fromhex(X["gid"][1798])
G["s1438_top0"] = g38
G["s1438_top0_KO32"] = mk(g38, {32: F[32]})
G["s1438_top0_KO29"] = mk(g38, {29: F[29]})
G["F+29=9f+32=d2+33=61+34=78"] = mk(F, {29: 0x9F, 32: 0xD2, 33: 0x61, 34: 0x78})
G["F+32=d2+34=78"] = mk(F, {32: 0xD2, 34: 0x78})
X5 = json.loads((HERE / "r1_BANK_1505.json").read_text())
G["s1505_top0"] = bytes.fromhex(X5["gid"][2675])
G["s1505_top1"] = bytes.fromhex(X5["gid"][2117])
JP = (0xC3, 0xC2, 0xCA, 0xD2, 0xDA)

if __name__ == "__main__":
    r = C.runner_for_spec(C.run_ds.DONOR)
    n = r.L
    PAN = panel()[:200]
    out = {}
    for name, g in G.items():
        st = collections.Counter()
        jumps = collections.Counter()
        entry = collections.Counter()
        for y, cy, _cx, _s in PAN:
            na, nb, ctxs, tr, wl, after0, ld = pair_t(r, g, y, C.ZERO, cy)
            ref = C.pair(r, g, y, C.ZERO, cy, 0.0)
            assert (ref["na"], ref["nb"]) == (na, nb)
            keep = C.FID(g, na) >= 0.9
            p = [t for t in tr if t[0] == 1]
            ran52 = any(t[1] == 52 for t in p)
            fe = next((t[1] for t in p if t[1] < n), None)
            if fe is not None:
                entry["%d-%d" % (fe // 8 * 8, fe // 8 * 8 + 7)] += 1
            for k in range(len(p) - 1):
                pc = p[k][1]
                if pc < n and p[k][2] in JP:
                    jumps["pc%d->%d" % (pc, p[k + 1][1])] += 1
            st["n"] += 1
            st["keep"] += keep
            st["partner_entered"] += fe is not None
            st["partner_ran_pc52"] += ran52
            st["loss_with_pc52"] += (not keep) and ran52
            st["loss_without_pc52"] += (not keep) and not ran52
        out[name] = {"stats": dict(st), "partner_jumps_in_donor_half": jumps.most_common(8),
                     "partner_first_entry_block": sorted(entry.items())}
        print(name, dict(st), jumps.most_common(4), flush=True)
    (HERE / "a3_trace.json").write_text(json.dumps(out, indent=1))
