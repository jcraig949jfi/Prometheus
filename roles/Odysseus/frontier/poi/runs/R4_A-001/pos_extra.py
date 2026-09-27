"""Amendment A1: POS-F (forced clean clobber removal), POS-P (power curve), POS-E (erosion)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4lib as L
eps = L.episodes(); exp = L.expected_vector(eps)
def sc(m): return L.score(L.answers(m, eps), exp)
two = L.manifest_of(L.summit_genome(2)); r0 = sc(two)
g = two["genome"]; assert g[13*4:13*4+4] == [3, 9, 0, 0]
one = dict(two); one["genome"] = g[:52] + g[56:]
out = {"r0": r0, "forced_step_reward": sc(one)}
def probe_depth(m, tag, s, P=4):
    imp = app = 0
    for op in L.OPS:
        for j in range(P):
            c, _ = L.one_edit(m, L.SplitMix64(L.seed_from("r4a001.posf", tag, s, op, j)), name=op)
            if c is None: continue
            app += 1; imp += sc(c) > r0 + L.BAND + L.EPS
    return app, imp
F = {"L1": [], "L2": []}
for s in range(32):
    F["L1"].append(probe_depth(two, "d0", s)); F["L2"].append(probe_depth(one, "d1", s))
out["POS_F"] = {k: {"seeds": len(v), "seeds_with_find": sum(1 for a, i in v if i), "applied": sum(a for a, _ in v), "improved": sum(i for _, i in v)} for k, v in F.items()}
out["POS_F"]["PASS"] = out["POS_F"]["L2"]["seeds_with_find"] >= 1 and out["POS_F"]["L2"]["seeds_with_find"] > out["POS_F"]["L1"]["seeds_with_find"]
p = out["POS_F"]["L2"]["improved"] / out["POS_F"]["L2"]["applied"]
out["POS_P"] = {"rate_used": p, "detect_prob_by_applied_probes": {n: round(1 - (1 - p) ** n, 3) for n in (45, 90, 180, 270, 540, 1000)}}
# POS-E erosion
rng = L.SplitMix64(L.seed_from("r4a001.pose"))
acc = fix1 = fix2 = 0
def has_clobber_positions(m):
    gg = m["genome"]; return [i for i in range(0, len(gg), 4) if gg[i] % 25 == 3 and gg[i+1] % m["n_regs"] == 9 and gg[i+2] == 0]
for _ in range(3000):
    c, _r = L.one_edit(two, rng)
    if c is None or abs(sc(c) - r0) > L.BAND + L.EPS: continue
    acc += 1
    pos = has_clobber_positions(c)
    # delete all clobber-pattern instructions: does the summit come back?
    gg = [w for k, w in enumerate(c["genome"]) if (k - k % 4) not in pos]
    m2 = dict(c); m2["genome"] = gg
    try:
        ok = sc(m2) >= 0.9
    except Exception:
        ok = False
    if ok and len(pos) == 1: fix1 += 1
    if ok: fix2 += 1
out["POS_E"] = {"accepted_neutral": acc, "one_deletion_from_summit": fix1, "summit_restorable_by_deleting_clobbers": fix2,
                "share_path_intact": round(fix2 / acc, 4), "share_one_edit_from_summit": round(fix1 / acc, 4)}
json.dump(out, open(os.path.join(L.HERE, "pos_extra.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
