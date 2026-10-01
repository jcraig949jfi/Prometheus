"""W2-J common: imports H-PLANT machinery (read-only), CPU only, 2 threads."""
import os, sys, pathlib, json
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("HP_THREADS", "2")
os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
HP = HERE.parents[1] / "H-PLANT"
sys.path.insert(0, str(HP))
import hp_common as hc  # noqa: E402  (asserts no CUDA, sets threads)
import torch  # noqa: E402
assert not torch.cuda.is_available()
assert torch.get_num_threads() <= 2
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
WJ_NS = 0x57324A53   # "W2JS" fresh scoring namespace (W2-J)
WJ_DEV = 0x57324A44  # "W2JD" design namespace


def lc():
    return {o["cell"]: o for o in json.load(open(HP / "out/lc_census.json"))["rows"]}


def xor_evolve():
    return [r for r in hc.rows() if r["env"]["family"] == "XOR" and r["kind"] == "evolve"]


def held(r):
    h = r["result"].get("held") or {}
    return h if isinstance(h, dict) else {}


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
