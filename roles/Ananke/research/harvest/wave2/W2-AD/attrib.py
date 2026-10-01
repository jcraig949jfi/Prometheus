"""W2-AD single-dial counterfactual attribution of PLANT-STAGE failures (diagnostic only; never an admission input).
For a seeded subsample (<= NMAX) of ceiling survivors whose every screened plant failed, set ONE suspect dial to its
benign level (all else identical, same worlds), rescore every design with the family ruler on 16 fresh pairs,
and record which single removals rescue a pass.  "Rescued by removing X" = X is sufficient to block the screened
plants at that cell (a statement about these plants, Pattern 5: never 'physics-dead').
usage: python attrib.py FAM [NMAX]"""
from w2ad_common import *
import sys
import w2ad_plants as WP
import census as CS

BENIGN = {
    "mut_site": lambda p: p.mut_site > 0 and p.replace(mut_site=0.0),
    "cap": lambda p: p.cap > 0 and p.replace(cap=0),
    "noise": lambda p: p.noise > 0 and p.replace(noise=0),
    "decay_shift": lambda p: p.decay_shift > 0 and p.replace(decay_shift=0),
    "loss": lambda p: p.loss > 0 and p.replace(loss=0.0),
    "async": lambda p: p.update_mode == "async" and p.replace(update_mode="sync", update_period=1),
    "update_period": lambda p: p.update_mode == "sync" and p.update_period > 1 and p.replace(update_period=1),
    "lat_jitter": lambda p: p.lat_jitter > 0 and p.replace(lat_jitter=0),
    "dup": lambda p: p.dup > 0 and p.replace(dup=0.0),
    "sample": lambda p: p.topology != "global" and p.dest_mode == "sample" and p.replace(dest_mode="all"),
}
PAIRS = 16


def score(fam, ph, env, seeds, integ):
    groups = []
    for nm, fn in WP.DESIGNS[fam].items():
        g = fn(ph); groups.append((nm, g, None))
        if fam == "MAJ":
            groups.append((nm + "|DICT", g, CS.dict_off))
    o, _ = multi_eval(ph, env, seeds, groups, inward=(fam == "MAJ"))
    best, anyp = None, False
    for nm in WP.DESIGNS[fam]:
        x = o[nm]
        if fam == "RELAY":
            ok = x["lo99"] > 0.55; v = x["acc"]
        elif fam == "FLIP":
            ok = x["B_lo99"] > 0.75; v = x["B"]
        else:
            dlo = paired(x["pairs"], o[nm + "|DICT"]["pairs"])[1]
            ok = (x["lo99"] > (0.70 if integ else 0.55)) and dlo > 0; v = x["acc"]
        anyp |= bool(ok)
        best = v if best is None else max(best, v)
    return anyp, best


def main(fam, nmax):
    C = {json.loads(l)["cid"]: json.loads(l) for l in (OUT / f"ceil_{fam}.jsonl").read_text().splitlines() if l.strip()}
    P = [json.loads(l) for l in (OUT / f"plant_{fam}.jsonl").read_text().splitlines() if l.strip()]
    fails = [p["cid"] for p in P if not p["plant_pass"]]
    rng = np.random.default_rng(0xA77)
    pick = sorted(rng.choice(len(fails), size=min(nmax, len(fails)), replace=False).tolist())
    path = OUT / f"attrib_{fam}.jsonl"
    have = CS.done_ids(path)
    t_start = time.time()
    with open(path, "a") as fh:
        for j in pick:
            cid = fails[j]
            if cid in have:
                continue
            ck = Clock()
            c = C[cid]; ph0 = Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
            seeds = assays.world_seeds(H_int(NS, 0xA7, CS.FAM_ID[fam], c["i"]), 2 * PAIRS)
            integ = bool(c.get("integration_claimed"))
            base_ok, base_v = score(fam, ph0, env, seeds, integ)
            res = {}
            for k, f in BENIGN.items():
                ph = f(ph0)
                if not ph:
                    continue
                ok, v = score(fam, ph.validate(), env, seeds, integ)
                res[k] = {"rescued": bool(ok), "best": v}
            rec = {"cid": cid, "base_pass16": base_ok, "base_best": base_v, "single": res,
                   "rescuers": [k for k, v in res.items() if v["rescued"]], "compute": ck.done()}
            fh.write(json.dumps(rec, default=float) + "\n"); fh.flush()
            print(cid, base_ok, round(base_v, 3), rec["rescuers"], rec["compute"]["cpu_s"], flush=True)
            if time.time() - t_start > 480:
                print("STOP: wall budget", flush=True); return


if __name__ == "__main__":
    torch.set_num_threads(1)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20)
