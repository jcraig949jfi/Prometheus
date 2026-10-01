"""W2-49 replay: W2-29 FULL seeds (unknown EW-1/EW-1b alarm status + 1303) with per-epoch trajectory.
Identical call to W2-29 p1_run.job for partner FULL. python -B p1_replay.py CAP_CPU_MIN -> runs_replay.jsonl"""
import json, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w49

KEYS = ["rule", "seed", "struct", "partner", "ctx", "mut", "epochs", "stop", "B", "Ball", "maxA", "A_end", "N_end",
        "depth_f", "depth_world", "calls", "Bxk", "kin", "n_genomes"]


def job(s):
    t0 = time.process_time()
    res, G, gf, tr = w49.run3("BASE", 9_998_000 + s, "FIELD", "FULL", stop="xk163", rec=True)
    res["s"] = s
    res["n_genomes"] = len(G)
    res["cpu_s"] = round(time.process_time() - t0, 2)
    res["traj"] = tr
    res["genomes"] = [[g.hex(), e[0], e[1], e[2]] for g, e in G.items()] if res["B"] >= 27 else None
    return res


if __name__ == "__main__":
    cap = float(sys.argv[1]) * 60
    seeds = json.load(open(HERE / "unknown_sets.json"))["primary"]
    ref = {}
    for l in open(HERE.parent / "W2-29_residue" / "runs_FULL.jsonl"):
        d = json.loads(l); ref[d["s"]] = d
    # longest first so the pool drains evenly
    seeds = sorted(seeds, key=lambda s: -ref[s]["cpu_s"])
    t0 = time.time(); cpu = 0.0; n = 0; bad = 0
    with mp.Pool(5) as p, open(HERE / "runs_replay.jsonl", "w") as fh:
        for res in p.imap_unordered(job, seeds, chunksize=1):
            mism = [k for k in KEYS if res[k] != ref[res["s"]][k]]
            res["bitexact_mismatch"] = mism
            bad += bool(mism); cpu += res["cpu_s"]; n += 1
            fh.write(json.dumps(res) + "\n"); fh.flush()
            if cpu > cap:
                print("CAP exceeded", cpu, flush=True); p.terminate(); break
    print("DONE n", n, "mismatching runs", bad, "cpu_s %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
