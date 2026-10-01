"""W2-49 audit of W2-45's tier-2 (frozen-inferred) negatives: replay the FULL frozen-early runs with B >= 7
(the ones most able to fire EW-1/EW-1b) with trajectory. python -B p2_tier2_audit.py -> runs_tier2_audit.jsonl"""
import json, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p1_replay import job, KEYS

if __name__ == "__main__":
    full = [json.loads(l) for l in open(HERE.parent / "W2-29_residue" / "runs_FULL.jsonl")]
    gen = {json.loads(l)["s"] for l in open(HERE.parent / "W2-29_residue" / "genomes_FULL.jsonl")}
    ref = {r["s"]: r for r in full}
    seeds = sorted(r["s"] for r in full if r["s"] not in gen and r["stop"] == "frozen" and r["epochs"] - 101 <= 9
                   and r["B"] >= 7)
    print("n seeds", len(seeds), "est cpu_s", sum(ref[s]["cpu_s"] for s in seeds), flush=True)
    t0 = time.time(); cpu = 0.0; bad = 0
    with mp.Pool(5) as p, open(HERE / "runs_tier2_audit.jsonl", "w") as fh:
        for res in p.imap_unordered(job, seeds, chunksize=1):
            res["bitexact_mismatch"] = [k for k in KEYS if res[k] != ref[res["s"]][k]]
            bad += bool(res["bitexact_mismatch"]); cpu += res["cpu_s"]
            fh.write(json.dumps(res) + "\n")
    print("DONE n", len(seeds), "mismatching runs", bad, "cpu_s %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
