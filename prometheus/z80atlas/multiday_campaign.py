"""Multi-day campaign driver (Bellerophon, 2026-09-26): does coupled earning carry computing copiers UP a task ladder,
protect their computation, and make repair common over long horizons?

Authorised by the operator rulings of 2026-09-26 (roles/Bellerophon/multiday_2026-09-26/prompts/) after the coupling
campaign's frozen readiness rule returned READY_FOR_MULTIDAY. Physics v3 is unchanged (coupling.py); this module only
plans, schedules and measures. Scope (NEXT_MULTIDAY_CAMPAIGN.md): acquisition + protection + repair; it does not
re-measure maintenance of seeded code.

Lanes (all coupled physics v3, K16 and K40 as separate arms, seed pairs share a seed across arms):
  LADDER1  founders = the 4 ECHO acquirers the coupling campaign verified CAUSAL_COUPLED; the world PAYS FOR INC.
           Question: does ON coupling produce de novo INC-competent self-replicators above control rates?
  LADDER2  founders = the 3 INC-competent E2 repairs verified CAUSAL_COUPLED; the world PAYS FOR COND_ONE.
  COPIER   pure copiers (SEEDED_REPLICATOR, no task code); the world pays for ECHO (the coupling campaign's only
           acquisition result, re-tested at a long horizon).
  REPAIR   REP + BAD (a copier whose sweep wrecks its own INC code); pays for INC (the coupling campaign's P6,
           underpowered at 500 ticks).
Arms: ON, OFF, SHUFFLED, YOKED (matched ON bonus schedule, split evenly) -- REPAIR: ON, OFF, YOKED.

Measurement additions (never fed back into a world):
  checkpoints  at fixed ticks: alive, competent (configured task), competent self-replicators, the dominant competent
               SR tape, previous-rung competence of the living (ladders), the dominant SR tape, and robustness
               (robustness.py) of both dominant tapes -- joint for the competent one, copy-only for the SR one.
  events       World.events is bounded in memory to exactly the records runner.run_spec would have written
               (first 400 + the next 200 non-copy) -- long runs otherwise hold millions of copy events.
Scheduling (identical mechanics to coupling_campaign Amendment 1): continuous submission, YOKED released when its ON
partner's result exists, worker recycling, active-runtime caps, torn-tail repair, atomic STATUS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import pathlib
import time
from typing import Dict, List, Optional

from prometheus.z80atlas import coupling_campaign as CC

SEED_BASE = 12_000_000_000_000        # disjoint: coupling 11e12.., grounding 9e12.., pilots 7e12..7.9e12
PILOT_SHIFT = -4_300_000_000_000      # --pilot seeds land in 7.7e12.. (off-plan)
TICKS = 10_000                        # frozen horizon (20x the coupling campaign); --pilot may override
CELLS, BUDGET = CC.CELLS, CC.BUDGET
CHECKPOINT_FRACS = (0.05, 0.1, 0.25, 0.5, 0.75, 1.0)
ROBUST_N = 128
TOTAL_CAP_H = 60.0                    # active runtime
RECYCLE_TASKS = 2                     # long runs: recycle workers often (RSS bound)
LANE_PRIORITY = {"LADDER1": 0, "COPIER": 1, "REPAIR": 2, "LADDER2": 3}
N_SEEDS = {"LADDER1": 80, "COPIER": 60, "REPAIR": 80, "LADDER2": 60}
PREV_RUNG = {"LADDER1": "ECHO", "LADDER2": "INC"}


def checkpoints(ticks: int) -> List[int]:
    return sorted({max(0, min(ticks - 1, int(round(f * ticks)) - 1)) for f in CHECKPOINT_FRACS})


# ---- plan ---------------------------------------------------------------------------------------------------------
def plan(inputs: Dict, ticks: int = TICKS) -> List[Dict]:
    fnd = inputs["founders"]
    P: List[Dict] = []
    lanes: Dict[str, int] = {}

    def add(lane, block, cell, arm, k, kname, vec, tapes, depends=None, founder=None):
        ln = lanes.setdefault(lane, len(lanes))
        seed = SEED_BASE + ln * 10 ** 9 + block * 10 ** 5 + k
        o = dict(CC.V3, **CC.K[kname]); o["coupling"] = arm
        P.append({"lane": lane, "block": block, "cell": cell, "arm": arm, "K": kname, "k": k, "pair": "%s|%d|%d" % (lane, block, k),
                  "vec": dict(CC.COMMON, **vec), "config_overrides": o, "init_tapes": list(tapes), "seed": seed, "depends": depends,
                  "ticks": ticks, "founder": founder, "priority": LANE_PRIORITY[lane], "id": None})
        return P[-1]

    def arms(lane, block, cellbase, k, kname, vec, tapes, arm_set, founder=None):
        on = add(lane, block, cellbase + "_ON", "ON", k, kname, vec, tapes, founder=founder)
        for a in arm_set:
            if a != "ON":
                add(lane, block, cellbase + "_" + a, a, k, kname, vec, tapes, depends=on if a == "YOKED" else None, founder=founder)
        return on

    FULL = ("ON", "OFF", "SHUFFLED", "YOKED")
    for bi, kn in enumerate(("K16", "K40")):
        for k in range(N_SEEDS["LADDER1"]):
            f = fnd["ECHO"][k % len(fnd["ECHO"])]
            arms("LADDER1", bi, "LADDER1_%s" % kn, k, kn, {"task": "INC"}, [f["tape"]], FULL, founder=f["id"])
        for k in range(N_SEEDS["LADDER2"]):
            f = fnd["INC"][k % len(fnd["INC"])]
            arms("LADDER2", bi, "LADDER2_%s" % kn, k, kn, {"task": "COND_ONE"}, [f["tape"]], FULL, founder=f["id"])
        for k in range(N_SEEDS["COPIER"]):
            arms("COPIER", bi, "COPIER_%s" % kn, k, kn, {"task": "ECHO", "init": "SEEDED_REPLICATOR"}, [], FULL)
        for k in range(N_SEEDS["REPAIR"]):
            seed = SEED_BASE + 10 ** 9 * 99 + bi * 10 ** 5 + k        # fixture construction only (task_k); not a run seed
            F = CC.fixtures("INC", seed)
            arms("REPAIR", bi, "REPAIR_%s" % kn, k, kn, {"task": "INC"}, [F["REP"], F["BAD"]], ("ON", "OFF", "YOKED"))
    for i, p in enumerate(P):
        p["id"] = "m%06d" % i
    for p in P:
        if p["depends"] is not None:
            p["depends"] = p["depends"]["id"]
    return P


def plan_hash(P: List[Dict]) -> str:
    return hashlib.sha256(json.dumps(P, sort_keys=True).encode()).hexdigest()


# ---- one run ----------------------------------------------------------------------------------------------------------
class _BoundedEvents(list):
    """Keeps exactly what runner.run_spec writes: the first 400 events of any kind, then up to 200 non-copy events."""
    def append(self, e):                                     # noqa: D401
        n_extra = getattr(self, "_extra", 0)
        if len(self) < 400:
            super().append(e)
        elif e.get("kind") != "copy" and n_extra < 200:
            super().append(e); self._extra = n_extra + 1


def _dominant(alive, pred) -> Optional[bytes]:
    cnt: Dict[bytes, int] = {}
    for o in alive:
        if pred(o):
            b = bytes(o.tape); cnt[b] = cnt.get(b, 0) + 1
    return max(sorted(cnt), key=cnt.get) if cnt else None


def _checkpoint(w, cfg, lane: str, seed: int) -> Dict:
    from prometheus.z80atlas.robustness import robustness
    from prometheus.z80atlas.tasks import Task, verify_exact
    alive = [o for o in w.cells if o is not None]
    comp = {o.id: w.competence.of(bytes(o.tape))[0] for o in alive}
    sr = {o.id: w.sr_depth.get(o.id, 0) > 0 for o in alive}
    dc = _dominant(alive, lambda o: comp[o.id] and sr[o.id])
    ds = _dominant(alive, lambda o: sr[o.id])
    rec = {"tick": w.tick, "alive": len(alive), "competent": sum(comp.values()), "competent_sr": sum(1 for o in alive if comp[o.id] and sr[o.id]),
           "sr_alive": sum(sr.values()), "dom_comp_sr": dc.hex() if dc else None, "dom_sr": ds.hex() if ds else None}
    if lane in PREV_RUNG:
        prev = Task(PREV_RUNG[lane]); cache: Dict[bytes, bool] = {}
        n = 0
        for o in alive:
            b = bytes(o.tape)
            if b not in cache:
                cache[b] = verify_exact(b, w.L, prev, cfg.read_gate, cfg.budget, cfg.layout, cfg.allow_copyall)
            n += cache[b]
        rec["prev_rung_competent"] = n
    task = w.configured_task()
    rec["robust_comp"] = robustness(dc, cfg, task, n=ROBUST_N, seed=seed % 2 ** 31) if dc else None
    rec["robust_sr_copy"] = robustness(ds, cfg, task, n=ROBUST_N, seed=seed % 2 ** 31, copy_only=True) if ds else None
    return rec


def _run(p: Dict) -> Dict:
    from prometheus.z80atlas import grammar as G
    from prometheus.z80atlas import adjudication as A
    from prometheus.z80atlas.world import World, ENDOGENOUS
    t0 = time.time()
    head = {k: p[k] for k in ("id", "lane", "cell", "arm", "K", "k", "pair", "seed", "founder")}
    try:
        vec = p["vec"]; ticks = int(p["ticks"])
        cfg = G.to_config(vec, ticks, CELLS, BUDGET, tuple(p["init_tapes"]))
        over = dict(p["config_overrides"])
        if over.get("coupling") == "YOKED":
            over["yoke"] = tuple(p.get("yoke") or ())
        for k, v in over.items():
            if k not in cfg.__dataclass_fields__:
                raise KeyError("config_overrides: %r is not a Config field" % k)
            setattr(cfg, k, v)
        w = World(cfg, p["seed"])
        w.events = _BoundedEvents(w.events)
        cps = set(checkpoints(ticks)); cp_recs = []
        for _ in range(cfg.ticks):                                           # == World.run, plus checkpoints
            t_now = w.tick
            w.step()
            if t_now in cps:
                cp_recs.append(_checkpoint(w, cfg, p["lane"], p["seed"]))
            if not any(o is not None for o in w.cells):
                w.extinct_tick = w.tick; w.extinctions += 1
                w.events.append({"tick": w.tick, "kind": "extinction"})
                break
        alive = [o for o in w.cells if o is not None]
        w._snapshot(alive, "final")
        s = w.summary(alive)
        assert not (vec["reproduction"] in ENDOGENOUS and s["external_births"] > 0), "external reproduction leaked into an ENDOGENOUS treatment"
    except Exception as e:                                                   # a VOID: recorded, never silently dropped
        return dict(head, void=repr(e)[:500])
    comp = s.get("competence") or {}
    dom = comp.get("dominant_competent_sr_tape")
    coup = dict(s.get("coupling") or {})
    sched = coup.pop("bonus_schedule", None)
    out = dict(head)
    out.update({"wall_s": round(time.time() - t0, 1), "ticks": ticks, "extinct": s["extinct"], "extinct_tick": s.get("extinct_tick"),
                "final_alive": s["final_alive"], "endogenous_births": s["endogenous_births"], "self_rep_births": s["self_rep_births"],
                "sr_max_depth": s["sr_max_depth"], "sr_alive_end": s["sr_alive_end"], "coupling": coup, "competence": comp,
                "dominant_sr_tape": s.get("dominant_sr_tape"),
                "dominant_competent_arch": A.arch_descriptor(bytes.fromhex(dom), cfg) if dom else None,
                "fixture_tapes": p["init_tapes"], "checkpoints": cp_recs, "snapshots_top": [
                    {"tick": x["tick"], "alive": x["alive"], "unique": x["unique"], "tapes": x["tapes"][:3]} for x in w.snapshots[::20]]})
    if p["arm"] == "ON":
        out["bonus_schedule"] = sched
    return out


# ---- execution (coupling_campaign Amendment-1 mechanics, with this module's _run) -------------------------------------
def execute(P: List[Dict], wd: pathlib.Path, workers: int, deadline: float, st_: Dict, st_path: pathlib.Path) -> str:
    res_path = wd / "results.jsonl"
    CC.repair_tail(res_path, st_)
    done: Dict[str, Dict] = CC.load_results(wd)
    pending = sorted((p for p in P if p["id"] not in done), key=lambda p: (p["priority"], p["id"]))
    stopped = "complete"; inflight = {}
    import queue as _q
    q: "_q.Queue" = _q.Queue()
    by_id = {p["id"]: p for p in P}
    with mp.Pool(workers, maxtasksperchild=RECYCLE_TASKS) as pool, res_path.open("a", encoding="utf-8", newline=chr(10)) as fh:
        while pending or inflight:
            if time.time() < deadline:
                i = 0
                while i < len(pending) and len(inflight) < workers + 2:
                    p = pending[i]
                    dep = p.get("depends")
                    if dep and dep not in done:
                        if dep not in inflight and not any(x["id"] == dep for x in pending):
                            p["yoke"] = []; p["yoke_partner_void"] = True
                        else:
                            i += 1; continue
                    elif dep:
                        d = done[dep]
                        if d.get("void") or not d.get("bonus_schedule"):
                            p["yoke"] = []; p["yoke_partner_void"] = True
                        else:
                            p["yoke"] = d["bonus_schedule"]
                    inflight[p["id"]] = pool.apply_async(_run, (p,), callback=q.put,
                                                         error_callback=lambda e, pid=p["id"]: q.put({"id": pid, "void": "pool: " + repr(e)[:400]}))
                    pending.pop(i)
            elif pending:
                stopped = "active_cap"; pending = []
            if not inflight:
                if pending:
                    raise RuntimeError("dependency deadlock")
                break
            try:
                out = q.get(timeout=CC.HEARTBEAT_S)
            except _q.Empty:
                CC._beat(st_, st_path); continue
            if out["id"] in inflight:
                src = by_id.get(out["id"], {})
                for k in ("lane", "cell", "arm", "K", "k", "pair", "seed", "founder"):
                    out.setdefault(k, src.get(k))
                if src.get("yoke_partner_void"):
                    out["yoke_partner_void"] = True
                fh.write(json.dumps(out, sort_keys=True, default=str) + chr(10)); fh.flush()
                done[out["id"]] = out; inflight.pop(out["id"])
                st_["last_write_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); st_["done"] = len(done)
                CC._beat(st_, st_path)
    st_["done"] = len(done); CC._beat(st_, st_path, force=True)
    return stopped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir"); ap.add_argument("--inputs", required=True); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--plan-only", action="store_true"); ap.add_argument("--status", action="store_true")
    ap.add_argument("--pilot", type=int, default=0, help="OFF-PLAN pilot: a stratified subset of N pairs, seeds shifted to 7.7e12..")
    ap.add_argument("--ticks", type=int, default=None, help="pilot only: override the horizon")
    ap.add_argument("--cap-h", type=float, default=None, help="pilot only: active-runtime cap in hours")
    a = ap.parse_args(argv)
    inputs = json.loads(pathlib.Path(a.inputs).read_text(encoding="utf-8"))
    if (a.ticks or a.cap_h) and not a.pilot:
        raise SystemExit("--ticks/--cap-h are pilot-only")
    P = plan(inputs, a.ticks or TICKS); h = plan_hash(P)
    if a.pilot:
        pairs = sorted({p["pair"] for p in P}); keep = set()
        by_lane: Dict[str, List[str]] = {}
        for pr in pairs:
            by_lane.setdefault(pr.split("|")[0], []).append(pr)
        per = max(1, a.pilot // max(1, len(by_lane)))
        for ln, prs in by_lane.items():
            keep |= set(prs[:: max(1, len(prs) // per)][:per])
        P = [dict(p, seed=p["seed"] + PILOT_SHIFT) for p in P if p["pair"] in keep]
        h = "PILOT-" + plan_hash(P)
    if a.plan_only:
        by: Dict[str, int] = {}
        for p in P:
            by[p["lane"]] = by.get(p["lane"], 0) + 1
        print(json.dumps({"plan_sha256": h, "runs": len(P), "by_lane": by, "ticks": P[0]["ticks"] if P else None}, indent=1)); return 0
    wd = pathlib.Path(a.workdir); wd.mkdir(parents=True, exist_ok=True)
    st_path = wd / "STATUS.json"
    st_ = json.loads(st_path.read_text(encoding="utf-8")) if st_path.exists() else {}
    if a.status:
        print(json.dumps(dict(st_, done=len(CC.load_results(wd))), indent=1)); return 0
    if st_.get("stopped"):
        raise SystemExit("campaign already stopped")
    if st_.get("plan_sha256") and st_["plan_sha256"] != h:
        raise SystemExit("plan hash changed since the campaign started: refusing")
    st_.setdefault("plan_sha256", h); st_.setdefault("time_rule", "active_runtime_v1"); st_.setdefault("active_segments", [])
    st_.setdefault("starts", []).append(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    st_.setdefault("workers_by_start", []).append([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), a.workers, RECYCLE_TASKS])
    segs = st_["active_segments"]
    if segs and segs[-1][1] is None:
        segs[-1][1] = max(segs[-1][0], st_.get("heartbeat_ts") or segs[-1][0]); segs[-1].append("closed at last heartbeat after an interruption")
    now = time.time(); used = CC.active_used(st_)
    segs.append([now, None, "segment %d" % (len(segs) + 1)])
    cap_h = a.cap_h if a.cap_h else TOTAL_CAP_H
    deadline = now + cap_h * 3600 - used
    CC._beat(st_, st_path, force=True)
    st_["stopped_reason"] = execute(P, wd, a.workers, deadline, st_, st_path)
    st_["stopped_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); st_["stopped"] = True
    st_["active_segments"][-1][1] = time.time(); st_["active_elapsed_s"] = round(CC.active_used(st_), 1)
    CC.save_status(st_, st_path)
    print(json.dumps({"stopped": True, "reason": st_["stopped_reason"], "done": st_["done"]}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
