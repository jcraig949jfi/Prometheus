"""W2-V common: CPU only, 2 threads, batched strict-genome evaluation (no overrides, no search)."""
import os, sys, pathlib, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["HP_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
HP = HERE.parents[1] / "H-PLANT"
sys.path.insert(0, str(HP))
import hp_common as hc  # noqa: E402  (asserts no CUDA)
import numpy as np  # noqa: E402
import torch  # noqa: E402
assert not torch.cuda.is_available()
torch.set_num_threads(2)
assert torch.get_num_threads() <= 2
from prometheus.ananke import envs, plants, assays  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
V_NS = 0x57325653    # "W2VS" fresh scoring namespace (W2-V)
V_DEV = 0x57325644   # "W2VD" design/enumeration namespace (W2-V)
ROWS = ["48256f59", "1974a9cf", "333d6b2b", "e2fd1e07", "4222a5f7", "84cf905d"]


def row(c8):
    for r in hc.rows():
        if r["cell_id"].startswith(c8):
            return r
    raise KeyError(c8)


def row_phys(c8):
    r = row(c8)
    return Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])


def asm(ph, lines, rules_variants=None):
    """lines -> genome [G, L, 5] at the row's OWN prog_len (assert fits). rules_variants: list of line lists
    (one per rule) for G>1 heterogeneous programs; default broadcasts one program to all rules."""
    if rules_variants is None:
        body = plants.assemble(ph, lines)  # asserts len <= prog_len
        return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
    assert len(rules_variants) == ph.rules
    return np.stack([plants.assemble(ph, v) for v in rules_variants])


def veval(ph, genomes, env, seeds, sched_fn=None):
    """Batched eval: genomes [P, G, L, 5]; mirror pairs share physics seeds (c1b/assays semantics). -> acc [P, M]"""
    genomes = np.asarray(genomes)
    P, M = genomes.shape[0], len(seeds)
    assert M % 2 == 0
    ws = [seeds[m - (m % 2)] for _ in range(P) for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    sch = ep.schedule
    sch = type(sch)(sch.sense_idx.repeat(P, 1), sch.sense_val.repeat(1, P, 1), sch.read_idx.repeat(P, 1))
    g = np.repeat(genomes, M, axis=0)
    w = World(ph, g, ws, device="cpu", schedule=sch)
    w.run(env.T(), graph=False)
    trace = w.trace.cpu().numpy()
    epP = envs.Episode(sch, np.tile(ep.ro_tick, (P, 1)), np.tile(ep.ro_slot, (P, 1)),
                       np.tile(ep.y, (P, 1)), np.tile(ep.scored, (P, 1)), ep.meta)
    acc = envs.score(epP, trace).reshape(P, M)
    stats = {k: v.cpu().numpy().reshape(P, M).sum(1) for k, v in w.stats.items()}
    return acc, stats


def summarize(acc_row):
    pairs = np.asarray(acc_row).reshape(-1, 2).mean(-1)
    m, lo, hi = assays.pair_ci(pairs)
    return {"acc": round(float(m), 4), "lo99": round(float(lo), 4), "hi99": round(float(hi), 4), "pairs": len(pairs)}


def zero_s2(ep):
    ep.schedule.sense_val[:, :, 1] = 0


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p


class Clock:
    def __init__(self):
        self.t0 = time.process_time()

    def cpu(self):
        return round(time.process_time() - self.t0, 1)
