"""W2-14 l1: the ingredient ladder. One config = (rule, STRUCT, PARTNER, CTX, MUT); seeds: BASE 9_998_000+s (X-TICKET's),
ATOMIC 12_000_000+s (C-ATOMIC's), s = 0..n-1; horizon 300. Appends one JSON line per run to ladder.jsonl.
python -B l1_ladder.py RULE STRUCT PARTNER CTX MUT n [s0]"""
import json, pickle, sys, time
import multiprocessing as mp
import ffield as F

BANKS = None


def job(a):
    global BANKS
    rule, struct, partner, ctx, mut, s = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    seed = (9_998_000 if rule == "BASE" else 12_000_000) + s
    res = F.run(rule, seed, struct, partner, ctx, mut == "ON", T=300, bank=BANKS.get(rule), pool=BANKS["POOL"], traj=True)
    res["s"] = s
    res["cpu_s"] = round(time.process_time() - t0, 2)
    return res


if __name__ == "__main__":
    rule, struct, partner, ctx, mut, n = sys.argv[1:7]
    s0 = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    jobs = [(rule, struct, partner, ctx, mut, s) for s in range(s0, s0 + int(n))]
    with mp.Pool(8) as pool, open(F.HERE / "ladder.jsonl", "a") as fh:
        for res in pool.imap_unordered(job, jobs):
            fh.write(json.dumps(res) + "\n"); fh.flush()
            print(res["s"], res["stop"], res["epochs"], "B", res["B"], "Ball", res["Ball"], "maxA", res["maxA"], "dF", res["depth_f"], res["cpu_s"], flush=True)
