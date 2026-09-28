"""W-F T-CT-1 carrier census over all C1 SIGNAL cells (PLAN.md frozen).
Usage: python census.py [--device cuda|cpu] [--limit N] [--ids a,b] [--out file]
Appends one JSON line per cell; skips cells already present (resume)."""
import argparse, gzip, json, pathlib, sys, time

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, envs, lens  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

HERE = pathlib.Path(__file__).parent
SEEDS = assays.world_seeds(0x5EA, 64)
ROWS = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def signal_rows():
    out = []
    with gzip.open(ROWS, "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["kind"] == "evolve" and r["result"].get("held", {}).get("lo99", 0) > 0.55:
                out.append(r)
    return out


def cls(t, joint):
    if t["normal"][1] < 0.60:
        return "UNREADABLE"
    s, c = t["site_all"]["verdict"] == "FLIP", t["channel_all"]["verdict"] == "FLIP"
    if s and c:
        return "DUAL"
    if s:
        return "SITE"
    if c:
        return "CHANNEL"
    if joint is not None and joint["verdict"] == "FLIP":
        return "JOINT"
    return "ELSEWHERE"


def one(r, dev):
    ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    tk = c1b.ticks(env)
    mid, late = tk["mid"], tk["late"]
    pre = [t0 - 1 for t0 in tk["t0"] if t0 >= 1]
    names = ["site_all", "channel_all", "channel_content", "channel_count"] + \
            [f"pay{k}" for k in range(ph.payload_width)] + ["w"]
    t = lens.carrier_table(ph, g, env, SEEDS, mid, names=names, device=dev)
    joint = None
    if t["site_all"]["verdict"] != "FLIP" and t["channel_all"]["verdict"] != "FLIP":
        base = lens.run(ph, g, env, SEEDS, device=dev)
        nrm = lens.trial_acc(base, range(env.trials))
        fn = lambda w: lens.swap(w, lens.SITE_ARRAYS + lens.FLIGHT_ARRAYS)
        tr = lens.run(ph, g, env, SEEDS, hooks={x: fn for x in mid}, device=dev)
        p = lens.trial_acc(tr, range(env.trials))
        joint = {"acc": lens.ci(p), "verdict": lens.swap_verdict(nrm, p),
                 "arm_identical": bool(np.array_equal(tr.trace, base.trace))}
    tl = lens.carrier_table(ph, g, env, SEEDS, late, names=["site_all", "channel_all"], device=dev)
    tp = lens.carrier_table(ph, g, env, SEEDS, pre, names=["site_all", "channel_all"], device=dev)
    c = cls(t, joint)
    return {"cell_id": r["cell_id"], "wave": r["wave"], "family": env.family,
            "physics": r["physics"], "env": r["env"], "held": r["result"]["held"],
            "ticks": {"mid": mid, "late": late, "pre": pre},
            "mid": t, "joint": joint, "late": tl, "pre": tp,
            "class": c, "class_late": cls(tl, None) if c != "UNREADABLE" else "UNREADABLE"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    ap.add_argument("--out", default=str(HERE / "out" / "census.jsonl"))
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    out = pathlib.Path(a.out)
    done = set()
    if out.exists():
        done = {json.loads(l)["cell_id"] for l in out.read_text().splitlines() if l.strip()}
    rows = signal_rows()
    if a.ids:
        want = a.ids.split(",")
        rows = [r for r in rows if any(r["cell_id"].startswith(w) for w in want)]
    si, sn = map(int, a.shard.split("/"))
    rows = [r for i, r in enumerate(rows) if i % sn == si]
    todo = [r for r in rows if r["cell_id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"signal={len(rows)} done={len(done)} todo={len(todo)} dev={a.device}", flush=True)
    for i, r in enumerate(todo):
        t0 = time.time()
        try:
            res = one(r, a.device)
        except Exception as e:  # record, do not hide
            res = {"cell_id": r["cell_id"], "family": r["env"]["family"], "error": repr(e)}
        res["wall_s"] = round(time.time() - t0, 2)
        with out.open("a") as f:
            f.write(json.dumps(res) + "\n")
        m = res.get("mid", {})
        print(f"[{i+1}/{len(todo)}] {r['cell_id'][:8]} {res['family']:5s} "
              f"n={m.get('normal', [0,0])[1]:.2f} class={res.get('class', 'ERR')} "
              f"late={res.get('class_late','-')} {res['wall_s']}s", flush=True)
