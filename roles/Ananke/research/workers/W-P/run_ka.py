"""Known-answer plants through the same pipeline (PLAN s4)."""
import json, sys, time
import numpy as np, torch
import common
from prometheus.ananke import assays, envs
import tt, ana, plants_joint as PJ
torch.set_num_threads(2)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=8)
SEEDS = assays.world_seeds(0x611, 64)
OFFS = [3, 4, 5, 6, 7, 8]
TRIALS = list(range(1, 8))


def fixture(name):
    if name == "max":
        ph = PJ.physics_max(); return ph, PJ.max_plant(ph)
    if name == "mux":
        ph = PJ.physics_mux(); return ph, PJ.mux_plant(ph)
    if name == "latch":
        return PJ.latch_fixture()
    if name == "echo":
        return PJ.echo_fixture()


def run(name, drop=()):
    ph, g = fixture(name)
    comps = {k: v for k, v in tt.coarse_components(ph).items() if k not in drop}
    names = list(comps)
    n = len(names)
    half = [z for z in tt.all_subsets(n) if z[0] == 0]
    site_mask = [tt.is_site(comps[k]) for k in names]
    per_o = {o: [] for o in OFFS}
    for k in TRIALS:
        res, ep = tt.run_table(ph, g, HOLD, SEEDS, k, OFFS, comps, half)
        yA, yB = ep.y[0::2, k], ep.y[1::2, k]
        for o in OFFS:
            per_o[o].append((ana.full_a(res[o], half, n), yA, yB))
    out = {}
    for o in OFFS:
        recs = ana.analyse(per_o[o], names, site_mask)
        out[o] = ana.summarize(recs, names, P=len(SEEDS) // 2, n_boot=500)
    return names, out


if __name__ == "__main__":
    res = {}
    for nm in ("max", "mux", "latch", "echo"):
        ph, g = fixture(nm)
        chk = tt.check_vs_lens(ph, g, HOLD, SEEDS[:32], 3, 5)
        print(nm, "C1 bit-identity vs lens_swap (normal,site,chan,joint):", chk, flush=True)
        names, out = run(nm)
        res[nm] = {"C1": chk, "names": names, "offsets": out}
        for o, s in out.items():
            print(f" {nm} o{o} el={s['eligible']} fS={s['fS']:.2f} fC={s['fC']:.2f} fN={s['fN']:.2f} baseN={s['base_N']} "
                  f"class={s['class']} pol={s.get('polarity')} R={s.get('R_top', '')[:2]} md={s.get('md_top', '')[:1]}", flush=True)
    names, out = run("max", drop=("Msum",))
    res["max_drop_Msum"] = {"names": names, "offsets": out}
    for o, s in out.items():
        print(f" max-dropMsum o{o} el={s['eligible']} fS={s['fS']} fN={s['fN']} baseN={s['base_N']} class={s['class']} md={s.get('md_top', '')[:2]}", flush=True)
    json.dump(res, open(common.HERE / "out/ka_plants.json", "w"), indent=1, default=str)
