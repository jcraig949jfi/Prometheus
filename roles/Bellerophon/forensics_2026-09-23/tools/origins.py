"""Phase 2B / 3.1: independent origins of self-replication in the historical campaign.

Unit: the RUN (one fresh random population). A non-intervention RANDOM-init endogenous run in which traced replay
found >= 1 SELF_REPLICATION birth contributes exactly ONE origin (its first self-replicating writer, pre-execution
tape). Descendants and later within-run 'origins' are never counted. Rate: origins / all RANDOM-init endogenous
non-intervention runs, combining the trigger set (fully traced) with the untriggered set (traced random sample).
Mechanism clusters (clustering assumption stated): an origin tape is executed alone; its mechanism key is
  (copy opcode, source offset S0 and target T0 of the first window write, the sorted multiset of DEFINED opcodes
   executed at own-tape PCs below the copy instruction)
Two origins with the same key use the same copy route; the number of distinct keys is the number of mechanistically
distinct routes (an upper bound on independence of MECHANISM; every run is independent in ORIGIN).
Also writes receipts/grounding_inputs.json (historical_origins for the HIST lane: one tape per origin run, deduped).
    python origins.py"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

WORKTREE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, WORKTREE)
from prometheus.z80atlas import vm  # noqa: E402
from prometheus.z80atlas.world import Config  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def mech_key(tape_hex, rep):
    cfg = Config(representation=rep)
    L = cfg.L
    t = bytes.fromhex(tape_hex)[:L]
    mem = bytearray(256); mem[:L] = t; mem[vm.IN_BASE] = 42
    tr = vm.execute(mem, L, 0, 256, [42], allow_copyall=cfg.allow_copyall, trace_pcs=True)
    prov = tr.win_prov
    if 0 not in prov:
        return ("NO_WINDOW_WRITE_IN_ISOLATION",)
    src0, pc0, op0 = prov[0]
    first_pc = min(pc for (_, pc, _) in prov.values())
    setup = sorted(t[p] for p in (tr.pcs or ()) if p < min(first_pc, L) and t[p] in vm.DEFINED and t[p] != vm.NOP)
    return (vm.MNEMONIC.get(op0, hex(op0)), src0, tuple(vm.MNEMONIC.get(o, hex(o)) for o in setup))


def main() -> None:
    R = Ld.runs()
    pool_runs = [r for r in R if r["vec"]["init"] == "RANDOM" and r["vec"]["reproduction"] in Ld.ENDOGENOUS]
    ints = {r["id"] for r in pool_runs if (Ld.run_file(r["id"], "config.json").get("init_tapes"))}
    base = [r for r in pool_runs if r["id"] not in ints]
    trig = {r["id"] for r in base if r["triggers"].get("spontaneous_replication")}
    N = len(base); N_trig = len(trig); N_non = N - N_trig
    T = {r["run"]: r for r in json.loads((Ld.OUT / "TRACED_spontaneous.json").read_text(encoding="utf-8"))["rows"]}
    B = [r for r in json.loads((Ld.OUT / "TRACED_baseline.json").read_text(encoding="utf-8"))["rows"] if not r["intervention"]]
    trig_sr = [T[i] for i in trig if T[i]["self_rep"] > 0]
    base_sr = [r for r in B if r["self_rep"] > 0]
    p_non = len(base_sr) / len(B)
    est = (len(trig_sr) + p_non * N_non) / N
    # CI: trigger part is a census; the untriggered part is a sample -> propagate its binomial variance
    se = math.sqrt(p_non * (1 - p_non) / len(B)) * N_non / N
    out = {"definition": __doc__, "pool_random_endogenous_nonintervention_runs": N, "trigger_runs": N_trig, "untriggered_runs": N_non,
           "trigger_runs_with_SR": len(trig_sr), "trigger_false_positive_runs": N_trig - len(trig_sr),
           "untriggered_sample": len(B), "untriggered_sample_with_SR": len(base_sr), "untriggered_SR_rate": round(p_non, 4),
           "untriggered_SR_rate_wilson": wilson(len(base_sr), len(B)),
           "origin_rate_per_run_est": round(est, 4), "origin_rate_ci95": [round(est - 1.96 * se, 4), round(est + 1.96 * se, 4)],
           "estimated_origins_total": round(len(trig_sr) + p_non * N_non, 1)}
    # sustained / active among origins (trigger census + sample, reported separately: they are different populations)
    for name, rows in (("trigger_census", trig_sr), ("untriggered_sample", base_sr)):
        n = len(rows)
        out[name] = {"origins": n, "sustained_d3": sum(r["sustained_lineage"] for r in rows), "sustained_d3_ci": wilson(sum(r["sustained_lineage"] for r in rows), n),
                     "sr_alive_at_end": sum(1 for r in rows if r["alive_end_sr_born"] > 0), "evolutionarily_active": sum(r["evolutionarily_active"] for r in rows),
                     "first_sr_tick_median": sorted(r["first_self_rep"]["tick"] for r in rows)[n // 2] if n else None,
                     "first_sr_at_tick0": sum(1 for r in rows if r["first_self_rep"]["tick"] == 0),
                     "by_reproduction": dict(collections.Counter(r["vec"]["reproduction"] for r in rows)),
                     "by_representation": dict(collections.Counter(r["vec"]["representation"] for r in rows))}
    # mechanism clusters over every origin we hold a tape for
    keys = collections.Counter(); ex = {}; hist = []; seen = set()
    for r in trig_sr + base_sr:
        o = (r.get("origins") or [None])[0]
        if not o:
            continue
        k = mech_key(o["tape"], r["vec"]["representation"])
        keys[k] += 1; ex.setdefault(k, (r["run"], o["tape"]))
        if o["tape"] not in seen:
            seen.add(o["tape"]); hist.append({"run": r["run"], "representation": r["vec"]["representation"], "reproduction": r["vec"]["reproduction"],
                                               "tick": o["tick"], "tape": o["tape"]})
    coarse = collections.Counter(tuple(k[:2]) for k in keys.elements())
    out["mechanism"] = {"origins_with_tape": sum(keys.values()), "distinct_fine_keys": len(keys), "distinct_coarse_routes(copy_op,S0)": len(coarse),
                        "coarse": {"/".join(map(str, k)): v for k, v in coarse.most_common()},
                        "top_fine": [{"key": [str(x) for x in k], "n": n, "example_run": ex[k][0], "example_tape": ex[k][1]} for k, n in keys.most_common(15)],
                        "singletons": sum(1 for n in keys.values() if n == 1)}
    p = Ld.write("ORIGINS.json", out)
    inp = {"built_by": "tools/origins.py", "historical_origins": sorted(hist, key=lambda h: h["run"])}
    q = Ld.write("grounding_inputs.json", inp)
    print(p, q, len(hist))
    print(json.dumps({k: v for k, v in out.items() if k not in ("definition", "mechanism")}, indent=1))
    print(json.dumps({k: v for k, v in out["mechanism"].items() if k != "top_fine"}, indent=1))
    for t in out["mechanism"]["top_fine"][:8]:
        print(t["n"], t["key"])


if __name__ == "__main__":
    main()
