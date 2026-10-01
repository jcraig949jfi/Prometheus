"""A2: 613162a3 (MAJ global). (i) shuffle_dest vs normal, fresh M=256 paired.
(ii) is the whole-network twin divergence chaos? Perturb S0 / S3 at one
non-sensor site by +1 and by the twin cue; measure spread and magnitude.
(iii) lag agreement and decay-floor residue."""
from w2e_common import *
ck = Clock()
r = row("613162a3", "evolve"); ph, env = spec_of(r); g = genome_of(r)
out = {"decompiled": decompile(ph, g[0])}
S = seeds(H_int(NS, 0xA2), 256)
acc_n, tr_n, ep, _ = run(ph, g, env, S)
acc_s, _, _, _ = run(ph, g, env, S, ctrl=Controls(shuffle_dest=True))
pn, ps = pairs(acc_n), pairs(acc_s)
d = ps - pn
out["normal"] = ci(pn); out["shuffle_dest"] = ci(ps)
out["paired_diff"] = {"mean": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(len(d))), "ci": ci(d)}
out["lag_agreement"] = lag_agreement(ep, tr_n)
# recorded D-row: normal .688 / shuffle .720 on 32 pairs -> recompute z
adj = [x for x in rows() if x["kind"] == "adjudicate" and x["parent"] and x["parent"].startswith("613162a3")][0]
c = adj["result"]["controls"]; dd = np.array(c["shuffle_dest"]["pair"]) - np.array(c["normal"]["pair"])
out["recorded_D_paired"] = {"mean": float(dd.mean()), "se": float(dd.std(ddof=1) / np.sqrt(len(dd)))}

# (ii) perturbation spread, non-mirrored worlds, 32 worlds
M = 32
S2 = seeds(H_int(NS, 0xA2B), M)
ep2 = envs.build(ph, env, S2)
Pd = env.period(); t0 = 2 * Pd
def pert_run(kind):
    gg = np.repeat(g[None], M, 0)
    wa = World(ph, gg, S2, device="cpu", schedule=ep2.schedule)
    sch = ep2.schedule
    if kind == "cue":
        sv = sch.sense_val.clone(); sv[t0:t0 + env.cue_len] = -sv[t0:t0 + env.cue_len]
        sch = type(sch)(sch.sense_idx, sv, sch.read_idx)
    wb = World(ph, gg, S2, device="cpu", schedule=sch)
    sens = ep2.schedule.sense_idx.numpy(); ro = ep2.schedule.read_idx[:, 0].numpy()
    rng_ = np.random.default_rng(7)
    site = np.array([rng_.choice(np.setdiff1d(np.arange(ph.n_sites), np.r_[sens[b], ro[b]])) for b in range(M)])
    frac, mag_s0, mag_nonsens = [], [], []
    for t in range(env.T()):
        if t == t0 and kind in ("S0+1", "S3+1", "S0+256", "S3+256"):
            reg = 0 if kind.startswith("S0") else 3
            amt = 1 if kind.endswith("+1") else 256
            wb.S[np.arange(M), site, reg] += amt
        wa.step(); wb.step()
        div = (wa.S != wb.S).any(-1)
        frac.append(div.float().mean().item())
        diff0 = (wa.S[..., 0] - wb.S[..., 0]).abs().float()
        mask = torch.ones_like(diff0, dtype=torch.bool)
        for b in range(M):
            mask[b, sens[b]] = False
        mag_nonsens.append(float(diff0[mask].mean()))
    frac = np.array(frac)
    nxt = t0 + Pd + env.delta
    return {"div_frac_at_ro": float(frac[t0 + env.delta]), "div_frac_next_ro": float(frac[nxt]),
            "div_frac_end": float(frac[-1]),
            "mean_abs_dS0_nonsensor_at_ro": mag_nonsens[t0 + env.delta],
            "mean_abs_dS0_nonsensor_next_ro": mag_nonsens[nxt], "mean_abs_dS0_nonsensor_end": mag_nonsens[-1]}
out["perturb"] = {k: pert_run(k) for k in ["cue", "S0+1", "S3+1", "S0+256", "S3+256"]}
out["clock"] = ck.done()
save("a2_613162a3.json", out); print(json.dumps(out, indent=1))
