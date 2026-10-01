"""Q1b: is the C (|dist| ~ U{1..255}) collapse magnitude-threshold fairness (distractors near the cue
amplitude 256) or tuning to the trained amplitude 64? Conditions on the SAME seeds as q1:
N, Clow |d|~U{1..64} (never above trained amp), Cmid U{1..128} (never above cue/2), Chi U{129..255}.
Cells: the 14 C-collapse cells, the 3 strobe cells, 0a3f6b87, + 10 random others (seeded)."""
from q_common import *
ck = Clock()
q1 = json.loads((OUT / "q1_distr_edits.json").read_text())
coll = [k for k, v in q1.items() if v["C_collapse"]]
fixed = coll + ["2c300c47", "0c18ce5e", "41fcb232", "0a3f6b87"]
rest = sorted(k for k in q1 if k not in fixed)
pick = list(np.random.default_rng(0x5751).choice(rest, 10, replace=False))
cells = list(dict.fromkeys(fixed + pick))
path = OUT / "q1b_mag_ranges.json"
done = json.loads(path.read_text()) if path.exists() else {}
def mag(env, lo, hi, seed):
    def f(ep):
        sv = ep.schedule.sense_val; B = sv.shape[1]; g = np.random.default_rng(seed)
        for k in range(env.trials):
            a0 = k * env.period() + env.cue_len; seg = sv[a0:a0 + env.gap]
            m = torch.as_tensor(g.integers(lo, hi + 1, size=(env.gap, B // 2, 1)), dtype=seg.dtype).repeat_interleave(2, 1)
            seg.copy_(torch.sign(seg) * m)
    return f
t0 = time.time()
for cid in cells:
    if cid in done: continue
    if time.time() - t0 > 500: break
    r = row(cid); ph, env = spec_of(r); g = genome_of(r)
    S = seeds(H_int(NS, 0x01, int(cid, 16) & 0xFFFF), 32)
    sd = H_int(NS, 0x1B, int(cid, 16) & 0xFFFF)
    res, _ = run_batched(ph, g, env, S, [("N", None), ("Clow", mag(env, 1, 64, sd)), ("Cmid", mag(env, 1, 128, sd + 1)),
                                          ("Chi", mag(env, 129, 255, sd + 2))])
    pN = pairs(res["N"][0]); d = {"normal": ci(pN), "pairs_N": pN.tolist(), "in_C_collapse": cid in coll}
    for c in ("Clow", "Cmid", "Chi"):
        p = pairs(res[c][0]); d[c] = ci(p); d[c + "_diff"] = ci(p - pN)
        d[c + "_collapse"] = bool(d[c + "_diff"][2] < 0 and d[c][0] < .60)
    done[cid] = d; path.write_text(json.dumps(done, indent=1))
    print(cid, d["normal"][0], {c: (d[c][0], d[c + "_diff"][2] < 0) for c in ("Clow", "Cmid", "Chi")}, flush=True)
print(len(done), "of", len(cells), ck.done())
