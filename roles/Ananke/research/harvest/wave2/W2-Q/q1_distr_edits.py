"""Q1: 86 HOLD champions (held lo99 > .60) under schedule edits A (first awake gap distractor silent),
B (count-fixed timing jitter, k=ceil(n/2) of n slots kept at random), C (|dist| ~ U{1..255}, sign kept).
16 pairs, paired against normal in one batched World. Resumable, time-capped (argv[1] wall s)."""
from q_common import *
cap = float(sys.argv[1]) if len(sys.argv) > 1 else 480
ck = Clock(); t0 = time.time()
path = OUT / "q1_distr_edits.json"
done = json.loads(path.read_text()) if path.exists() else {}
cells = [r for r in rows() if r["kind"] == "evolve" and r["env"]["family"] == "HOLD" and r["result"]["held"]["lo99"] > .60]
assert len(cells) == 86

def slots(ph, env, k):
    Pd = env.period(); a = k * Pd + env.cue_len; b = a + env.gap
    return [t for t in range(a, b) if t % ph.update_period == 0] if ph.update_mode == "sync" else list(range(a, b))

def make(ph, env, kind, seed, rec):
    def f(ep):
        sv = ep.schedule.sense_val; B = sv.shape[1]
        g = np.random.default_rng(seed)
        first_sil = np.zeros((B, env.trials), bool)
        for k in range(env.trials):
            sl = slots(ph, env, k)
            if not sl: continue
            if kind == "A":
                sv[sl[0]].zero_(); first_sil[:, k] = True
            elif kind == "B":
                n = len(sl); keep = (n + 1) // 2
                for bb in range(0, B, 2):          # mirror partners share the edit
                    kp = set(g.choice(n, keep, replace=False).tolist())
                    for j, t in enumerate(sl):
                        if j not in kp:
                            sv[t, bb:bb + 2] = 0
                    first_sil[bb:bb + 2, k] = 0 not in kp
            elif kind == "C":
                a0 = k * env.period() + env.cue_len
                seg = sv[a0:a0 + env.gap]           # [gap, B, 1]
                mags = torch.as_tensor(g.integers(1, 256, size=(env.gap, B // 2, 1)), dtype=seg.dtype)
                mags = mags.repeat_interleave(2, dim=1)
                seg.copy_(torch.sign(seg) * mags)
        rec[kind] = first_sil
    return f

for r in cells:
    cid = r["cell_id"][:8]
    if cid in done: continue
    if time.time() - t0 > cap: break
    tc = time.process_time()
    ph, env = spec_of(r); g = genome_of(r)
    S = seeds(H_int(NS, 0x01, int(cid, 16) & 0xFFFF), 32)
    rec = {}
    sd = H_int(NS, 0x0E, int(cid, 16) & 0xFFFF)
    res, _ = run_batched(ph, g, env, S, [("N", None), ("A", make(ph, env, "A", sd, rec)),
                                          ("B", make(ph, env, "B", sd + 1, rec)), ("C", make(ph, env, "C", sd + 2, rec))])
    aN = res["N"][0]; d = {"normal": ci(pairs(aN))}
    for c in "ABC":
        a = res[c][0]
        d[c] = ci(pairs(a)); d[c + "_diff"] = ci(pairs(a) - pairs(aN))
        d[c + "_collapse"] = bool(d[c + "_diff"][2] < 0 and d[c][0] < .60)
    pt = res["B"][1]; fs = rec["B"]
    d["B_first_kept_acc"] = round(float(pt[~fs].mean()), 4) if (~fs).any() else None
    d["B_first_silent_acc"] = round(float(pt[fs].mean()), 4) if fs.any() else None
    d["n_slots"] = len(slots(ph, env, 0))
    d["meta"] = {"rules": ph.rules, "setrule": ph.setrule, "topology": ph.topology, "mode": ph.update_mode,
                 "P": ph.update_period, "gap": env.gap, "N": ph.n_sites, "held": r["result"]["held"]["acc"],
                 "parent": r["parent"]}
    d["cpu_s"] = round(time.process_time() - tc, 2)
    done[cid] = d
    path.write_text(json.dumps(done, indent=1))
print(len(done), "of", len(cells), ck.done(), flush=True)
