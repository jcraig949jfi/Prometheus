"""W2-AD C2 ADMISSION CENSUS (W2-AB next question 1). No search; plants are hand-written and never seeds.

usage: python census.py FAMILY START STOP [stage]      stage in {ceil, plant}
  ceil : draw candidates [START, STOP) of FAMILY, stratum + reachability + joint ceiling -> out/ceil_<FAM>.jsonl
  plant: for ceiling survivors in [START, STOP), score >= 2 plant designs + must-fail ablations on 32 fresh
         pairs -> out/plant_<FAM>.jsonl
Resumable (skips candidate ids already present). Every invocation is kept < 10 min wall by the caller.

Candidate sampler (seeded, declared before any scoring):
  physics levels = campaign.draw_levels(H(SEED, fam_id, i), campaign.DIALS) [C1 A0 dial ranges], then the C2
  genome spec is imposed (PREREG_PTE_C2_DRAFT s2.1): prog_len 16, rules 1, setrule 0, economy off, and the
  per-family register spec below (fixed per family before admission); env levels =
  draw_levels(H(s, 0xE), ENV_DIALS) exactly as C1 A0; invalid physics redrawn with H(s, 1) as C1 does.
"""
from w2ad_common import *
import sys
from prometheus.ananke import campaign
import w2ad_ceil as WC
import w2ad_plants as WP
import attain as AT

SEED = 0xC2AD0001
FAM_ID = {"RELAY": 1, "XOR": 2, "MAJ": 3, "FLIP": 4}
SPEC = {  # C2 genome spec per family (s2.1): >= every screened plant's needs
    "RELAY": dict(prog_len=16, rules=1, setrule=0, state_dim=2, payload_width=1, channels=1),
    "FLIP": dict(prog_len=16, rules=1, setrule=0, state_dim=2, payload_width=1, channels=1),
    "MAJ": dict(prog_len=16, rules=1, setrule=0, state_dim=2, payload_width=2, channels=1),
    "XOR": dict(prog_len=16, rules=1, setrule=0, state_dim=4, payload_width=2, channels=2),
}
CEIL_PAIRS = 64          # ceiling on 64 fresh position pairs (= C2 held design P)
PLANT_PAIRS = 32

# A90 at C2's held design (P = 64), power .9 (W2-B attain.min_true_to_cross)
def K_scored(env):
    return env.trials - (env.trials // env.block if env.family == "FLIP" else 0)

def thresholds(fam, env):
    K = K_scored(env)
    a90 = lambda thr: AT.min_true_to_cross(thr, 64, K, "lo_gt", 0.9)
    t = {"SIGNAL": a90(0.55) + 0.05}
    if fam == "MAJ":
        t["INTEGRATION"] = max(0.80, a90(0.70) + 0.05)
    if fam == "FLIP":
        t["B"] = max(0.90, a90(0.75) + 0.05)
    if fam == "XOR":
        t["XOR_SYM"] = max(0.85, a90(0.55) + 0.05)
    return t


def candidate(fam, i):
    s = H_int(SEED, FAM_ID[fam], i)
    tries = 0
    while True:
        lv = campaign.draw_levels(s, campaign.DIALS)
        lv = dict(lv)
        lv["economy"] = "off"
        for k, v in SPEC[fam].items():
            lv[k] = v
        try:
            ph = campaign.physics_from_levels(lv, topo_seed=H_int(s, 0x7090))
            break
        except AssertionError:
            s = H_int(s, 1); tries += 1
    ev = campaign.draw_levels(H_int(s, 0xE), campaign.ENV_DIALS)
    env = campaign.env_from_levels(fam, ev)
    cid = f"{fam}-{i:04d}-{ph.digest()[:8]}"
    return dict(cid=cid, i=i, family=fam, levels=lv, env_levels=ev, physics=ph.to_dict(), env=env.to_dict(),
                redraws=tries)


def done_ids(path):
    if not path.exists():
        return set()
    return {json.loads(l)["cid"] for l in path.read_text().splitlines() if l.strip()}


def stage_ceil(fam, a, b):
    path = OUT / f"ceil_{fam}.jsonl"
    have = done_ids(path)
    t_start = time.time()
    with open(path, "a") as fh:
        for i in range(a, b):
            c = candidate(fam, i)
            if c["cid"] in have:
                continue
            ck = Clock()
            ph = Physics.from_dict(c["physics"]); env = envs.EnvSpec(**c["env"])
            seeds = assays.world_seeds(H_int(NS, 0xCE, FAM_ID[fam], i), 2 * CEIL_PAIRS)
            r = WC.joint_ceiling(ph, env, seeds)
            th = thresholds(fam, env)
            h = r["hops"]
            c.update(r)
            c["thresholds"] = th
            c["reach_ok"] = h["impossible_pairs"] == 0
            if fam == "RELAY":
                c["stratum_ok"] = h["min_hops"] >= 2
                c["ceil_ok"] = r["ceiling"] >= th["SIGNAL"]
            elif fam == "MAJ":
                c["stratum_ok"] = True       # operational rule: all sensors within reach by delta (enforced by ceilings)
                c["hop1_all"] = h["max_hops"] <= 1
                c["integration_claimed"] = bool(r["ceiling"] >= th["INTEGRATION"] and r["q"] >= 0.7)
                c["ceil_ok"] = r["ceiling"] >= th["SIGNAL"]
            elif fam == "FLIP":
                c["stratum_ok"] = True
                c["ceil_ok"] = r["ceiling"] >= th["B"]
            elif fam == "XOR":
                c["stratum_ok"] = True
                c["ceil_ok"] = r["ceiling"] >= th["XOR_SYM"]
            c["survivor"] = bool(c["stratum_ok"] and c["reach_ok"] and c["ceil_ok"])
            c["compute"] = ck.done()
            fh.write(json.dumps(c, default=float) + "\n"); fh.flush()
            print(c["cid"], round(c["ceiling"], 3), c["binding"], c["survivor"], c["compute"]["cpu_s"], flush=True)
            if time.time() - t_start > 480:
                print("STOP: wall budget", flush=True); return


def teacher_off(sv, ep):
    Pd = ep.meta["env"]["delta"] + 1 + ep.meta["env"]["cue_len"] + ep.meta["env"]["iti"]
    sv[Pd:, :, 1] = 0                     # FLIP teacher only on trial 0


def dict_off(sv, ep):
    sv[:, :, 1:] = 0                      # MAJ DICT: only sensor 0 receives its cue


def stage_plant(fam, a, b):
    src = [json.loads(l) for l in (OUT / f"ceil_{fam}.jsonl").read_text().splitlines() if l.strip()]
    src = [c for c in src if c["survivor"] and a <= c["i"] < b]
    path = OUT / f"plant_{fam}.jsonl"
    have = done_ids(path)
    t_start = time.time()
    with open(path, "a") as fh:
        for c in src:
            if c["cid"] in have:
                continue
            ck = Clock()
            ph = Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
            seeds = assays.world_seeds(H_int(NS, 0x9A, FAM_ID[fam], c["i"]), 2 * PLANT_PAIRS)
            groups = []
            for nm, fn in WP.DESIGNS[fam].items():
                g = fn(ph)
                groups.append((nm, g, None))
                if fam == "FLIP":
                    groups.append((nm + "|teacher_off", g, teacher_off))
                if fam == "MAJ":
                    groups.append((nm + "|DICT", g, dict_off))
            o, ep = multi_eval(ph, env, seeds, groups, inward=(fam == "MAJ"))
            res = {}
            th = c["thresholds"]
            for nm in WP.DESIGNS[fam]:
                x = o[nm]
                d = {"acc": x["acc"], "lo99": x["lo99"], "hi99": x["hi99"]}
                if fam == "RELAY":
                    d["pass"] = bool(x["lo99"] > 0.55)
                    d["ruler"] = "SIGNAL(relay forced: min_hops>=2)"
                elif fam == "FLIP":
                    t = o[nm + "|teacher_off"]
                    d.update(B=x["B"], B_lo99=x["B_lo99"], chg=x["chg"], same=x["same"],
                             teacher_off=t["acc"], teacher_off_lo99=t["lo99"])
                    d["mustfail_ok"] = bool(t["lo99"] < 0.55)
                    d["pass"] = bool(x["B_lo99"] > 0.75 and d["mustfail_ok"])
                    d["ruler"] = "B lo99>.75 + teacher_off not SIGNAL"
                elif fam == "MAJ":
                    t = o[nm + "|DICT"]
                    dm, dlo, dhi = paired(x["pairs"], t["pairs"])
                    d.update(DICT=t["acc"], DICT_lo99=t["lo99"], diff=dm, diff_lo99=dlo)
                    win = dlo > 0
                    if c.get("integration_claimed"):
                        d["pass"] = bool(x["lo99"] > 0.70 and win)
                        d["ruler"] = "INTEGRATION lo99>.70 + paired win over DICT"
                    else:
                        d["pass"] = bool(x["lo99"] > 0.55 and win)
                        d["ruler"] = "SIGNAL + paired win over DICT"
                    d["dict_le_70"] = bool(t["acc"] <= 0.70)
                d["above_ceiling"] = bool(x["lo99"] > c["ceiling"])   # stop condition (s2.2)
                res[nm] = d
            rec = {"cid": c["cid"], "i": c["i"], "ceiling": c["ceiling"], "plants": res,
                   "plant_pass": any(v["pass"] for v in res.values()),
                   "n_designs": len(res), "compute": ck.done()}
            fh.write(json.dumps(rec, default=float) + "\n"); fh.flush()
            print(c["cid"], {k: (round(v["acc"], 3), v["pass"]) for k, v in res.items()}, rec["compute"]["cpu_s"], flush=True)
            if time.time() - t_start > 480:
                print("STOP: wall budget", flush=True); return


if __name__ == "__main__":
    fam, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    stage = sys.argv[4] if len(sys.argv) > 4 else "ceil"
    if len(sys.argv) > 5:
        torch.set_num_threads(int(sys.argv[5]))
    (stage_ceil if stage == "ceil" else stage_plant)(fam, a, b)
