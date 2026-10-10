"""BEL-RD-72 campaign driver (Bellerophon, 2026-10-10): the BEL-48H driver (roles/Bellerophon/bel48h_2026-10-08/tools/
bel48h_driver.py, unchanged semantics for every existing kind) extended with RD-72 kinds. Instruments from BEL-48H are
imported from that directory; new instruments live beside this file.

Original docstring follows.
BEL-48H campaign driver (Bellerophon, 2026-10-08). Executes a frozen plan (JSON list of specs) with a bounded,
recycled worker pool; resumable (a run with a result line is never re-run; each run is a pure function of its spec);
writes results.jsonl, per-run birth rows (runs/<id>.jsonl.gz, outside git), and STATUS.json (counts, throughput,
worker RSS, free disk and RAM). Launch it DETACHED from a pinned code copy, never from a Claude Code shell:

    setsid nohup python3 bel48h_driver.py --plan plan.json --workdir DIR --workers 6 > DIR/driver.log 2>&1 &

Spec kinds:
  dual      DualWorld (both lineage rulers + FUNC on the same trajectory); geometry v1-vs-written on specimens
  plain     World, end-state hash (the physics-invariance audit pairs)
  lockstep  two configs on one seed stepped together: first tick at which the world RNG / population state differ,
            then both run to the end (the DEF-BEL-009 pairing audit)"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import pathlib
import random
import shutil
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "bel48h_2026-10-08" / "tools"))   # BEL-48H instruments
sys.path.insert(0, str(HERE))                                                 # RD-72 instruments (shadow BEL-48H names if any)
sys.path.insert(0, str(HERE.parents[3]))                          # repository (or pinned copy) root: prometheus/

KEEP = ("extinct", "extinct_tick", "alive_fraction", "final_alive", "endogenous_births", "self_rep_births", "sr_max_depth",
        "sr_alive_end", "sr_distinct_alive", "captures", "null_rewrites", "seed_lineage_share", "seed_causal_share",
        "genetic_lineages_final", "lineages_final", "first_self_replication", "dominant_sr_tape", "ticks_run", "births_by_mechanism")


def _cfg(spec):
    from prometheus.z80atlas.world import Config
    d = dict(spec["cfg"])
    for k in ("init_tapes", "yoke"):
        if k in d:
            d[k] = tuple(d[k])
    return Config(**d)


def _step_once(w) -> bool:
    w.step()
    if not any(o is not None for o in w.cells):
        w.extinct_tick = w.tick; w.extinctions += 1
        w.events.append({"tick": w.tick, "kind": "extinction"})
        return False
    return True


def _finish(w) -> dict:
    """identical to World.run() from the current tick (tested against run() by end-state hash)."""
    alive_flag = any(o is not None for o in w.cells)
    while alive_flag and len(w.ticks_log) < w.cfg.ticks:
        alive_flag = _step_once(w)
    alive = [o for o in w.cells if o is not None]
    w._snapshot(alive, "final")
    return w.summary(alive)


def _pop_hash(w) -> str:
    h = hashlib.sha256()
    for o in w.cells:
        h.update(b"-" if o is None else bytes(o.tape))
    return h.hexdigest()


def _keep(s):
    return {k: s.get(k) for k in KEEP}


def _geom(tape_hex, cfg):
    from prometheus.z80atlas import geometry
    from prometheus.z80atlas.tasks import Task
    if not tape_hex:
        return None
    t = bytes.fromhex(tape_hex); task = Task(cfg.task)
    out = {}
    for rule in ("v1", "written"):
        out[rule] = geometry._eval(t, cfg, task, random.Random(7), rep_rule=rule)["replicates"]
    return out


def run_one(spec):
    try:
        return _run_one(spec)
    except Exception as e:                                          # a crashing run is a VOID line, never a dead pool
        import traceback
        return {"id": spec["id"], "lane": spec.get("lane"), "kind": spec.get("kind"), "void": True,
                "error": "%s: %s" % (type(e).__name__, e), "trace": traceback.format_exc()[-1500:]}


def _run_one(spec):
    t0 = time.time()
    from belinst import DualWorld, end_state_hash
    from prometheus.z80atlas.world import World
    kind = spec["kind"]; out = {k: spec.get(k) for k in ("id", "lane", "cell", "arm", "pair", "seed", "kind")}
    if kind == "dual":
        cfg = _cfg(spec)
        w = DualWorld(cfg, spec["seed"]); s = w.run(); d = w.dual_summary()
        out["summary"] = _keep(s); out["dual"] = d; out["end_hash"] = end_state_hash(w)
        fsr = s.get("first_self_replication") or {}
        out["geom"] = {"first_sr_res_writer": _geom((d["first"].get("sr_res") or {}).get("pre_tape"), cfg),
                       "first_trb_writer": _geom((d["first"].get("trb") or {}).get("pre_tape"), cfg),
                       "dominant_sr": _geom(s.get("dominant_sr_tape"), cfg)}
        if w.rows:
            rd = pathlib.Path(spec["workdir"]) / "runs"; rd.mkdir(parents=True, exist_ok=True)
            with gzip.open(rd / (spec["id"] + ".jsonl.gz"), "wt", encoding="utf-8") as f:
                for r in w.rows:
                    f.write(json.dumps(r, separators=(",", ":")) + "\n")
            out["rows"] = len(w.rows)
    elif kind in ("heredity", "reach"):
        from heredity import HeredityWorld
        from reach import ReachWorld
        cfg = _cfg(spec)
        w = (ReachWorld if kind == "reach" else HeredityWorld)(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["dual"] = w.dual_summary(); out["heredity"] = w.heredity_summary()
        if kind == "reach":
            out["reach"] = w.reach_summary()
        out["end_hash"] = end_state_hash(w)
        if w.h_events:
            rd = pathlib.Path(spec["workdir"]) / "events"; rd.mkdir(parents=True, exist_ok=True)
            with gzip.open(rd / (spec["id"] + ".jsonl.gz"), "wt", encoding="utf-8") as f:
                for e in w.h_events:
                    f.write(json.dumps(e, separators=(",", ":")) + "\n")
            out["events_written"] = len(w.h_events)
    elif kind == "compete":
        from comp import CompWorld, founder_census
        cfg = _cfg(spec)
        w = CompWorld(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["comp"] = w.comp_summary(); out["census"] = founder_census(w)
        out["end_hash"] = end_state_hash(w)
    elif kind == "comp":
        from comp import CompWorld
        cfg = _cfg(spec)
        w = CompWorld(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["summary"]["competence"] = s.get("competence"); out["summary"]["coupling"] = {
            k: v for k, v in (s.get("coupling") or {}).items() if k != "bonus_schedule"}
        out["dual"] = w.dual_summary(); out["heredity"] = w.heredity_summary(); out["comp"] = w.comp_summary()
        out["exposure"] = sum(r.get("alive", 0) for r in w.ticks_log)          # organism-ticks lived (search budget)
        out["end_hash"] = end_state_hash(w)
    elif kind == "scan":
        from prometheus.z80atlas import geometry
        from belinst import Func
        cfg = _cfg(spec); f = Func(cfg)
        rows = []
        for th in spec["tapes"]:
            t = bytes.fromhex(th)
            r = geometry.scan_operators(t, cfg.L, f, ops=("SUB", "MOVE", "INS", "DEL"))
            rows.append({"tape": th, **{op: r[op]["routes"] for op in r}})
        out["scan"] = rows
    elif kind == "harvest":
        from harvest import harvest
        cfg = _cfg(spec)
        out["harvest"] = harvest(cfg, spec["seed"], spec["harvest_tick"], spec.get("n_sample", 20))
    elif kind == "uptake_fate":
        from uptake_fate import UptakeFateWorld
        cfg = _cfg(spec)
        w = UptakeFateWorld(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["origin"] = w.origin_summary(); out["UF"] = dict(w.UF); out["end_hash"] = end_state_hash(w)
    elif kind in ("origin", "origin_block", "origin_block_selfcopy"):
        from origin import OriginWorld
        from uptake_block import UptakeBlockWorld, SelfCopyUptakeBlockWorld
        cfg = _cfg(spec)
        W = {"origin": OriginWorld, "origin_block": UptakeBlockWorld, "origin_block_selfcopy": SelfCopyUptakeBlockWorld}[kind]
        w = W(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["heredity"] = w.heredity_summary(); out["reach"] = w.reach_summary()
        out["origin"] = w.origin_summary(); out["end_hash"] = end_state_hash(w)
        if spec.get("expect_end_hash") is not None:
            out["replay_identical"] = out["end_hash"] == spec["expect_end_hash"]
    elif kind == "plain":
        cfg = _cfg(spec)
        w = World(cfg, spec["seed"]); s = w.run()
        out["summary"] = _keep(s); out["end_hash"] = end_state_hash(w)
    elif kind == "lockstep":
        ca = _cfg({"cfg": spec["cfg"]}); cb = _cfg({"cfg": spec["cfg_b"]})
        a = DualWorld(ca, spec["seed"]); b = DualWorld(cb, spec["seed"])
        out["init_rng_equal"] = a.rng.getstate() == b.rng.getstate()
        out["init_pop_equal_random_slots"] = sum(1 for x, y in zip(a.cells, b.cells) if x is not None and y is not None
                                                 and x.mechanism == "init" and y.mechanism == "init" and x.tape == y.tape)
        rng_div = pop_div = None; alive_a = alive_b = True; t = 0
        while alive_a and alive_b and t < ca.ticks and (rng_div is None or pop_div is None):
            alive_a = _step_once(a); alive_b = _step_once(b); t += 1
            if rng_div is None and a.rng.getstate() != b.rng.getstate():
                rng_div = t
            if pop_div is None and _pop_hash(a) != _pop_hash(b):
                pop_div = t
        out["rng_div_tick"] = rng_div; out["pop_div_tick"] = pop_div
        sa = _finish(a); sb = _finish(b)
        out["a"] = {"summary": _keep(sa), "dual": a.dual_summary()}; out["b"] = {"summary": _keep(sb), "dual": b.dual_summary()}
    if spec.get("expect_end_hash") is not None and "end_hash" in out:
        out["replay_identical"] = out["end_hash"] == spec["expect_end_hash"]
    out["wall_s"] = round(time.time() - t0, 2)
    return out


def _rss_children():
    tot = 0
    me = os.getpid()
    for p in pathlib.Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            st = (p / "stat").read_text().split()
            if int(st[3]) == me:
                for line in (p / "status").read_text().splitlines():
                    if line.startswith("VmRSS:"):
                        tot += int(line.split()[1])
        except Exception:
            pass
    return tot // 1024


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True); ap.add_argument("--workdir", required=True)
    ap.add_argument("--workers", type=int, default=6); ap.add_argument("--recycle", type=int, default=25)
    a = ap.parse_args(argv)
    wd = pathlib.Path(a.workdir); wd.mkdir(parents=True, exist_ok=True)
    plan = json.loads(pathlib.Path(a.plan).read_text())
    plan_sha = hashlib.sha256(pathlib.Path(a.plan).read_bytes()).hexdigest()
    res = wd / "results.jsonl"
    done = set()
    if res.exists():
        with open(res, "rb") as f:
            data = f.read()
        if data and not data.endswith(b"\n"):                      # torn tail from a kill: truncate to the last full line
            data = data[: data.rfind(b"\n") + 1]; res.write_bytes(data)
        for line in data.decode().splitlines():
            done.add(json.loads(line)["id"])
    todo = [dict(p, workdir=str(wd)) for p in plan if p["id"] not in done]
    st = {"plan_sha256": plan_sha, "planned": len(plan), "done_at_start": len(done), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "workers": a.workers, "pid": os.getpid(), "state": "running"}
    t0 = time.time(); n = 0; errors = 0
    with mp.get_context("fork").Pool(a.workers, maxtasksperchild=a.recycle) as pool, open(res, "a") as fo:
        for r in pool.imap_unordered(run_one, todo, chunksize=1):
            fo.write(json.dumps(r, separators=(",", ":")) + "\n"); fo.flush(); n += 1
            errors += bool(r.get("void"))
            if n == 10 and errors == 10:                              # upstream dead (base rule 9): stop loudly, do not burn the plan
                st.update({"state": "ABORTED_ALL_VOID", "voids": errors, "first_error": r.get("error")})
                (wd / "STATUS.json").write_text(json.dumps(st, indent=1)); pool.terminate(); return 2
            if n % 10 == 0 or n == len(todo):
                du = shutil.disk_usage(str(wd))
                mem = dict(l.split(":", 1) for l in pathlib.Path("/proc/meminfo").read_text().splitlines())
                st.update({"done": len(done) + n, "voids": errors, "rate_per_h": round(n / max(1e-9, time.time() - t0) * 3600, 1),
                           "worker_rss_mb": _rss_children(), "mem_available_mb": int(mem["MemAvailable"].split()[0]) // 1024,
                           "disk_free_gb": round(du.free / 1e9, 1), "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                (wd / "STATUS.json").write_text(json.dumps(st, indent=1))
    st.update({"state": "complete" if errors == 0 else "complete_with_voids", "voids": errors, "done": len(done) + n, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "active_s": round(time.time() - t0, 1)})
    (wd / "STATUS.json").write_text(json.dumps(st, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
