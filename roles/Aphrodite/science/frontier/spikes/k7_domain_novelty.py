"""SPIKE K7 -- ruler/domain mismatch. For each K2 pool family flagged non-G1
by the mechanism key (grid includes negative acc), is the WITNESS PROGRAM
extensionally equal, on 150 random task-domain inputs (values 2-30, lengths
2-60, query 1-97), to some program in G1's coverage (derived_0 entries)?"""
import json, random, sys, os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG)); sys.path.insert(0, str(ENG / "accel"))
import fasteval as FE, a17, basis_v4 as G  # noqa: E401,E402
HERE = Path(__file__).resolve().parent

def job(r):
    rng = random.Random(r["body"] + r["final"] + r["init"])
    ins = [[rng.randint(2, 30) for _ in range(rng.randint(2, 60))] + [rng.randint(1, 97)] for _ in range(150)]
    w = ("fold", r["init"], r["body"], r["final"])
    tv = [FE.run_program(w, x, True) for x in ins]
    g1 = [e for e in a17.L1_entries() if e["name"] == "derived_0"][0]
    for i in g1["inits"]:
        for b in g1["bodies"]:
            for f in g1["finals"]:
                p = ("fold", i, b, f)
                if all(FE.run_program(p, x, True) == t for x, t in zip(ins, tv)):
                    return dict(r, g1_equivalent=list(p))
    return dict(r, g1_equivalent=None)

if __name__ == "__main__":
    rows = json.loads((HERE / "K2_ADMISSIBLE_SOLVABILITY.json").read_text())["rows"]
    ng = [r for r in rows if not r["g1_body"] and r["Q2_size"] is not None and r["PRISTINE"]["solved"] + r["L1"]["solved"] > 0]
    with ProcessPoolExecutor(8) as ex:
        out = list(ex.map(job, ng))
    eq = [r for r in out if r["g1_equivalent"]]
    print("non-G1-by-key, qualified, solvable:", len(out), "| extensionally G1 on task domain:", len(eq))
    for r in out:
        print("  %-5s %-42s %-34s -> %s" % (r["op"], r["body"], r["final"], r["g1_equivalent"]))
    Path(__file__).with_name("K7_DOMAIN_NOVELTY.json").write_text(json.dumps(out, indent=1))
