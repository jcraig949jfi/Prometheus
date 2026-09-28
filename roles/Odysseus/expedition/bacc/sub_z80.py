"""bacc substrate S2: BEE Z80-like VM (prometheus/z80atlas/vm.py), 64-byte tapes, task COND_ONE.

    python3 sub_z80.py [--smoke]      -> z80_result.json
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)
import bacc  # noqa: E402
from prometheus.z80atlas import vm, tasks  # noqa: E402

L = 64
BUDGET = 256
TASK = tasks.Task("COND_ONE")
PANEL = [p[0] for p in tasks.panel(TASK)]
EXP = [TASK.expected([x])[0] for x in PANEL]
ALL = list(range(256))


def run1(tape, x, pcs=False):
    mem = bytearray(256)
    mem[:L] = tape
    mem[vm.IN_BASE] = x
    return vm.execute(mem, L, 0, BUDGET, [x], trace_pcs=pcs)


def behaviour_on(tape, xs):
    out = []
    for x in xs:
        tr = run1(tape, x)
        out.append(tr.outputs[0] if tr.outputs else -1)
    return tuple(out)


def evaluate(tape):
    b = behaviour_on(tape, PANEL)
    return b, sum(1 for o, e in zip(b, EXP) if o == e) / len(EXP)


def mutate(tape, rng, j):
    i = rng.randrange(L)
    v = rng.randrange(255)
    v = v if v < tape[i] else v + 1
    return tape[:i] + bytes([v]) + tape[i + 1:]


def gkey(t):
    return bytes(t)


def neutral(s, s0):
    return abs(s - s0) < 1e-12


def improving(s, s0):
    return s > s0 + 1e-12


def sample(rng):
    return bytes(rng.randrange(256) for _ in range(L))


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


_EXEC = {}


def executed(tape):
    if tape not in _EXEC:
        s = set()
        for x in PANEL:
            s |= run1(tape, x, pcs=True).pcs
        if len(_EXEC) > 4096:
            _EXEC.clear()
        _EXEC[tape] = s
    return _EXEC[tape]


def extra(cur, child, b, s):
    i = next(k for k in range(L) if cur[k] != child[k])
    row = {"site_executed": i in executed(cur)}
    if abs(s - 0.5) < 1e-12:
        row["full"] = hash(behaviour_on(child, ALL))
    return row


SPEC = bacc.Spec("z80_cond_one", mutate, evaluate, gkey, neutral, improving, sample, hamming, extra)


def parents():
    out = []
    for kind, wit in (("echo", vm.witness_echo()), ("inc", vm.witness_inc())):
        for i in range(4):
            r = bacc.rng_for("z80.parent", kind, i)
            fill = bytes(r.randrange(256) for _ in range(L - len(wit)))
            out.append(("%s%d" % (kind, i), wit + fill))
    return out


def main():
    smoke = "--smoke" in sys.argv
    W, D, m, NN = (1, 3, 8, 50) if smoke else (2, 20, 32, 2000)
    ps = parents()
    if smoke:
        ps = ps[:2]
    t0 = time.time()
    walkers, null = bacc.run_all(SPEC, ps, W, D, m, procs=4, null_n=NN)
    t_run = time.time() - t0
    per, summ = bacc.analyse(SPEC, walkers, null, D)
    # mechanism: non-coding sites; cryptic variation on all 256 inputs
    by = defaultdict(list)
    for wk in walkers:
        by[wk["pid"]].append(wk)
    pmap = dict(ps)
    for pid, ws in by.items():
        neut = [p for wk in ws for p in wk["probes"] if p["neutral"]]
        dom = [p for p in neut if p["b"] == ws[0]["b0"]]
        per[pid]["neutral_share_site_not_executed"] = (sum(1 for p in neut if not p["site_executed"]) / len(neut)) if neut else None
        allp = [p for wk in ws for p in wk["probes"]]
        per[pid]["all_probe_share_site_not_executed"] = sum(1 for p in allp if not p["site_executed"]) / len(allp)
        full0 = hash(behaviour_on(pmap[pid], ALL))
        per[pid]["cryptic_distinct_full256_among_panel_identical"] = len({p["full"] for p in dom})
        per[pid]["cryptic_share_panel_identical_but_full256_differs"] = (sum(1 for p in dom if p["full"] != full0) / len(dom)) if dom else None
        per[pid]["B_full256_neutral"] = len({p["full"] for p in neut})
    for k in ("neutral_share_site_not_executed", "cryptic_share_panel_identical_but_full256_differs", "B_full256_neutral",
              "cryptic_distinct_full256_among_panel_identical"):
        summ["median_" + k] = bacc.median([p[k] for p in per.values()])
    nm = bacc.null_metrics(null)
    nm["share_scoring_0.5"] = sum(1 for r in null if abs(r["s"] - 0.5) < 1e-12) / len(null)
    nm["share_improving_over_0.5"] = sum(1 for r in null if r["s"] > 0.5 + 1e-12) / len(null)
    nm["share_no_output"] = sum(1 for r in null if all(o == -1 for o in r["b"])) / len(null)
    out = {"substrate": "Z80 BEE vm, 64-byte tape, COND_ONE panel", "EXPLORATORY": True,
           "design": {"W": W, "D": D, "m": m, "null_n": NN, "parents": [p for p, _ in ps]},
           "wall_s": round(time.time() - t0, 1), "walk_wall_s": round(t_run, 1),
           "summary": summ, "null": nm, "per_parent": per}
    with open(os.path.join(HERE, "z80_result%s.json" % ("_smoke" if smoke else "")), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: summ[k] for k in ("median_B_over_G", "median_DOM", "BEHAVIOURAL_POVERTY",
                                            "pooled_neutral_genotypes", "pooled_neutral_behaviours")}), out["wall_s"])


if __name__ == "__main__":
    main()
