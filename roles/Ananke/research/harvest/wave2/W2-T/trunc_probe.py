"""W2-T: what kills the TRUNCATED champions? Reuses W2-O g12_diag.diag (read-only import; writes only to W2-T/out)."""
import os, sys, json, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["PTE_MUT_THREADS"] = "1"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-O"))
import g12_diag as GD  # noqa: E402
t = json.load(open(HERE / "out/table_t.json"))["rows"]
cells = [x["cell"] for x in t if x["class"] == "TRUNCATED"]
with open(HERE / "out/trunc_probe.jsonl", "w") as f:
    for c in cells:
        o = GD.diag(c)
        print(json.dumps(o), flush=True)
        f.write(json.dumps(o) + "\n")
