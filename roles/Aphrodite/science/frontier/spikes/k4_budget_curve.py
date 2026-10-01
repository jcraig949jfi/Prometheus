"""SPIKE K4 -- is G1's advantage budget-relative (reordering) or absolute?
For G1-mechanism families that PRISTINE failed within the frozen escrow (K2
'L1_only'), rerun PRISTINE with a 40M-candidate escrow on 2 cells each and
record the charge of the first dev-consistent hit; compare to L1's charge.
Forensic labels 'K4-...'. Hits are dev-consistent only (no tribunal)."""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
os.environ["A17_FASTEVAL"] = "1"
import a17, engine as E, fair as FR  # noqa: E401,E402
HERE = Path(__file__).resolve().parent
CAP = 40_000_000

def job(args):
    a17.worker_init()
    k, r, i = args
    name = "kb_" + "abcdefghijklmnopqrstuvwxyz"[k % 26] + "abcdefghijklmnopqrstuvwxyz"[k // 26]
    prov = a17.Prov({name: (r["body"], r["final"], r["init"])})
    out = {"body": r["body"], "final": r["final"], "init": r["init"], "cell": i}
    for arm, ents, cap in (("PRISTINE", FR.pristine().entries, CAP), ("L1", a17.L1_entries(), a17.ESCROW)):
        c = FR.Cell(prov, name, i, r["Q2_size"], label="K4")
        esc = E.Escrow(cap)
        h = FR.search_collect(FR.KLib(ents), c.parsed, esc, cap, c.seed, max_hits=1)
        out[arm] = {"charge": h[0][2] if h else None, "coord": h[0][1] if h else None}
    return out

if __name__ == "__main__":
    rows = json.loads((HERE / "K2_ADMISSIBLE_SOLVABILITY.json").read_text())["rows"]
    tgt = [r for r in rows if r["g1_body"] and r["Q2_size"] and r["L1"]["solved"] > 0 and r["PRISTINE"]["solved"] == 0][:10]
    jobs = [(k, r, i) for k, r in enumerate(tgt) for i in range(2)]
    with ProcessPoolExecutor(8, initializer=a17.worker_init) as ex:
        res = list(ex.map(job, jobs, chunksize=1))
    for x in res:
        print(x["body"], "|", x["final"], "| P", x["PRISTINE"], "| L1", x["L1"])
    solved = [x for x in res if x["PRISTINE"]["charge"]]
    print("PRISTINE solved at 40M:", len(solved), "/", len(res))
    if solved:
        ratios = sorted(x["PRISTINE"]["charge"] / x["L1"]["charge"] for x in solved if x["L1"]["charge"])
        print("P/L1 charge ratios:", [round(v) for v in ratios])
    Path(__file__).with_name("K4_BUDGET_CURVE.json").write_text(json.dumps(res, indent=1))
