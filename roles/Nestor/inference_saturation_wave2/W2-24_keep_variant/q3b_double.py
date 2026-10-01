"""Q3 supplement: per-side keep/conv of the double mutant 43->C3+44->AC on the N17e panel, and the traced jump
behaviour (JP 22AC at pos 43 -> absolute 44): who takes it, from which side. Also the ZERO-context placement
traces of F@0 vs 5C@1 and F@0 vs C3+AC@1 (who runs whose LDIR)."""
import json, collections
from q1_trace import panel, mk, HERE
from tvm import C, pair_t
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
D = mk(F, {43: 0xC3, 44: 0xAC})
pan = panel()
out = {}
for s in (0, 1):
    c = collections.Counter()
    for y, cy, cx, side in pan:
        if side != s:
            continue
        ga, gb, sa, sb = (D, y, C.ZERO, cy) if s == 0 else (y, D, cy, C.ZERO)
        na, nb, ctxs, tr, wl, a0, ld = pair_t(r, ga, gb, sa, sb)
        nx, ny = (na, nb) if s == 0 else (nb, na)
        c["N"] += 1; c["keep"] += C.FID(D, nx) >= 0.9; c["conv"] += C.FID(D, ny) >= 0.9
        pt = 1 - s
        p = [t[1] for t in tr if t[0] == pt]
        d = [t[1] for t in tr if t[0] == s]
        c["partner_takes_JP_at_donor43"] += any(p[k] == s * 64 + 43 and p[k + 1] == 44 for k in range(len(p) - 1))
        c["partner_runs_donor_LDIR52"] += any(l[0] == pt and l[1] == s * 64 + 52 for l in ld)
        c["donor_takes_JP_into_partner_half"] += s == 1 and any(d[k] == 107 and d[k + 1] == 44 for k in range(len(d) - 1))
    out["C3+AC_side%d" % s] = dict(c)
G = {"F": F, "5C": mk(F, {49: 0x5C}), "C3": mk(F, {43: 0xC3}), "C3+AC": D}
for a, b in (("F", "5C"), ("F", "C3+AC"), ("C3", "F"), ("C3", "C3+AC"), ("F", "C3")):
    na, nb, ctxs, tr, wl, a0, ld = pair_t(r, G[a], G[b])
    out["%s@0 vs %s@1" % (a, b)] = {"ldirs(who,pc,src,dst,n)": [l[:5] for l in ld],
                                    "after_side0_run": ["same" if a0[0] == G[a] else "changed", "same" if a0[1] == G[b] else "changed"],
                                    "ctx0_visits_side1_pcs": sorted({t[1] for t in tr if t[0] == 0 and t[1] >= 64})[:6],
                                    "ctx1_visits_side0_pcs": sorted({t[1] for t in tr if t[0] == 1 and t[1] < 64})[:6]}
(HERE / "q3b_double.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
