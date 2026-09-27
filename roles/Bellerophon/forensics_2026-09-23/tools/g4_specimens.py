"""G4 (GROUNDING_PREREG.md s3): does beneficial-neighbourhood density follow the reproductive mechanism?

Specimens (unit = specimen = one independent origin):
  (i)  HIST  -- the 10 historical REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY runs with the largest PAIRED gain
               (receipts/GEOM_AUDIT_flagged.json): their top tape, their configured task and representation
  (ii) GRND  -- the first 30 grounding G1 'ENDOGENOUS_COPY/Z80_64' runs (by run id) whose dominant SR tape self-copies
Interventions per specimen X (paired beneficial density on the specimen's configured task, ATOMIC ruler):
  intact           BD(X)
  nopped           BD(X with every LDI/LDIR/COPYALL byte -> NOP)
  graft_routine    routine = X[0 : copy_pc+1]; onto 10 foreign genomes (5 = task witness after the routine + random
                   padding, 5 = random tapes), seeded per specimen
  graft_control    the same foreign genomes with a same-length RANDOM graft in place of the routine
Effects: mech_effect = BD(X) - BD(nopped); transplant_effect = mean BD(graft_routine) - mean BD(graft_control).
Also recorded: whether the grafted genomes self-copy (did the transplant transfer reproduction at all).
    python g4_specimens.py --grounding <workdir> --workers 12   -> receipts/G4_SPECIMENS.json"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

WORKTREE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _witness(task_kind: str, k: int, offset: int) -> bytes:
    """the task witness assembled for `offset` (absolute jumps relocated -- forensics H1)"""
    from prometheus.z80atlas import vm
    w = {"CONST": lambda: vm.witness_const(k), "ECHO": vm.witness_echo, "INC": vm.witness_inc, "COND_ONE": vm.witness_cond_one,
         "COND_MULTI": vm.witness_cond_multi, "SUM2": vm.witness_sum2}[task_kind]()
    return vm.relocate(w, offset)


def _one(sp):
    if WORKTREE not in sys.path:
        sys.path.insert(0, WORKTREE)
    from prometheus.z80atlas.world import Config
    from prometheus.z80atlas.tasks import Task
    from prometheus.z80atlas import geometry as Gm, adjudication as A
    cfg = Config(representation=sp["rep"], task=sp["task"], scoring="ATOMIC", read_gate=sp.get("read_gate", "ABR"))
    L = cfg.L; task = Task(sp["task"], k=sp.get("k", 42))
    X = bytes.fromhex(sp["tape"])[:L]; X = X + bytes(L - len(X))
    bd = lambda t: Gm.scan_paired(t, cfg, task, seed=4040)["beneficial_density"]
    d = A.repro_descriptor(X, cfg, task)
    nopped = bytes(0 if b in (0x14, 0x15, 0x16) else b for b in X)
    row = {"id": sp["id"], "source": sp["source"], "task": sp["task"], "rep": sp["rep"], "descriptor": d,
           "bd_intact": bd(X), "bd_nopped": bd(nopped), "nopped_self_copy": A.repro_descriptor(nopped, cfg, task)["self_copy"]}
    row["mech_effect"] = round(row["bd_intact"] - row["bd_nopped"], 4)
    cp = d.get("copy_pc")
    if not d["self_copy"] or cp is None or cp >= L - 4:
        row["graft"] = "NOT_GRAFTABLE (no own-code copy routine inside the tape)"
        return row
    routine = X[:cp + 1]
    import hashlib
    rng = random.Random(int(hashlib.sha256(sp["id"].encode()).hexdigest()[:12], 16))   # stable across processes (str hash() is salted)
    foreign = []
    for i in range(10):
        pad = bytes(rng.randrange(256) for _ in range(L))
        if i < 5:
            w = _witness(sp["task"], task.k, len(routine))
            foreign.append((routine + w + pad)[:L])
            ctrl = bytes(rng.randrange(256) for _ in range(len(routine)))
            foreign.append(("CTRL", (ctrl + w + pad)[:L]))
        else:
            foreign.append((routine + pad[len(routine):])[:L])
            ctrl = bytes(rng.randrange(256) for _ in range(len(routine)))
            foreign.append(("CTRL", (ctrl + pad[len(routine):])[:L]))
    g_r = [t for t in foreign if not isinstance(t, tuple)]; g_c = [t[1] for t in foreign if isinstance(t, tuple)]
    row["bd_graft_routine"] = [bd(t) for t in g_r]; row["bd_graft_control"] = [bd(t) for t in g_c]
    row["graft_routine_self_copy"] = sum(A.repro_descriptor(t, cfg, task)["self_copy"] for t in g_r)
    row["transplant_effect"] = round(st.mean(row["bd_graft_routine"]) - st.mean(row["bd_graft_control"]), 4)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grounding", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    specs = []
    ga = json.loads((Ld.OUT / "GEOM_AUDIT_flagged.json").read_text(encoding="utf-8"))["rows"]
    for r in sorted((r for r in ga if r["status"] == "OK"), key=lambda r: -r["paired_gain"])[:10]:
        s = Ld.run_file(r["run"], "summary.json")
        specs.append({"id": "HIST:" + r["run"], "source": "historical_flagged", "tape": s["top"][0]["tape"], "task": r["vec"]["task"],
                      "k": r["task"]["k"], "rep": r["vec"]["representation"], "read_gate": r["vec"]["read_gate"]})
    res = [json.loads(l) for l in open(os.path.join(a.grounding, "results.jsonl"), encoding="utf-8") if l.strip()]
    g1 = sorted((r for r in res if r["lane"] == "G1" and r["cell"] == "ENDOGENOUS_COPY/Z80_64" and (r.get("dominant_sr_descriptor") or {}).get("self_copy")),
                key=lambda r: r["id"])[:30]
    for r in g1:
        specs.append({"id": "GRND:" + r["id"], "source": "grounding_G1", "tape": r["dominant_sr_tape"], "task": "INC", "k": 42, "rep": "Z80_64"})
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_one, specs, chunksize=1)
    me = [r["mech_effect"] for r in rows]
    te = [r["transplant_effect"] for r in rows if "transplant_effect" in r]
    rng = random.Random(7)
    def boot(xs):
        if not xs:
            return None
        bs = sorted(st.mean(rng.choice(xs) for _ in xs) for _ in range(2000))
        return [round(bs[50], 4), round(bs[1949], 4)]
    out = {"definition": __doc__, "n_specimens": len(rows), "n_graftable": len(te),
           "mech_effect": {"median_abs": round(st.median(abs(x) for x in me), 4), "mean": round(st.mean(me), 4), "ci95_boot": boot(me)},
           "transplant_effect": {"mean": round(st.mean(te), 4) if te else None, "ci95_boot": boot(te)}, "rows": rows}
    p = Ld.write("G4_SPECIMENS.json", out)
    print(p, json.dumps({k: v for k, v in out.items() if k not in ("rows", "definition")}))


if __name__ == "__main__":
    main()
