"""Forensic replay harness for the frozen 72-hour record (S1-A replays, S1-B, S1-C).

A replay re-executes one frozen run - same cell, seed, tier, invaders, physics - on
`substrate/`, a verbatim copy of the predecessor modules with observation hooks added
(git diff shows additions only, plus z8's write path gaining an unexecuted-by-default
provenance branch). The hooks never read or advance the world's RNG.

EVERY REPLAY IS CHECKED AGAINST ITS FROZEN SUMMARY. The replay's `summary` must equal
the frozen RESULT.json `summary` field for field. A mismatch marks the replay
REPLAY_MISMATCH and its telemetry is not used: telemetry from a run that is not the
original run would describe something else.

These replays are a NEW FORENSIC ASSAY. They are not retroactive 72-hour evidence and
nothing here writes under the frozen observatory.

Modes
  funnel  per-organism sequential replication funnel (S1-A)
  h4      per-epoch population / births / deaths-by-cause / validation / held (S1-B)
  p11     P-11 randomized-victim reassay of every predecessor pair-tape event (S1-C)
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import os
import pathlib
import sys
import time
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
SUB = HERE / "substrate"
VERIFY = HERE.parent / "z80atlas-verify-2026-09-22"
FROZEN = pathlib.Path(os.environ.get(
    "Z80A_FROZEN_OBS",
    r"F:/Prometheus-worktrees/nestor-sidequest-graphworld/roles/Nestor/campaigns/"
    r"z80atlas-2026-09-19/observatory"))

sys.path.insert(0, str(SUB))
import world      # noqa: E402  (substrate copy)
import z8         # noqa: E402  (substrate copy)
import grammar as G   # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


constants = _load("constants", VERIFY / "constants.py")
p11 = _load("p11", VERIFY / "p11.py")

FUNNEL = ("self_location_executed", "alloc_attempted", "alloc_succeeded", "target_writes",
          "birth_attempted", "birth_accepted", "fidelity_ge_090", "offspring_evidence_child")


def depth(edges):
    """Longest chain of child -> parent edges; edges is a dict child -> parent."""
    best, memo = 0, {}
    for node in edges:
        chain, cur = [], node
        while cur in edges and cur not in memo and cur not in chain:
            chain.append(cur)
            cur = edges[cur]
        base = memo.get(cur, 0)
        for k in reversed(chain):
            base += 1
            memo[k] = base
        best = max(best, memo.get(node, 0))
    return best, memo


class FX:
    """The observer. One per replay; all state is private to it."""

    def __init__(self, mode, cell):
        self.mode = mode
        self.p11 = mode == "p11"
        self.ct = Counter()
        self.none_sl = cell["self_location"] == "NONE"
        self.stage = {}
        self.marg = defaultdict(set)
        self.hi_child_parent = {}
        self.deaths = Counter()
        self.epoch_deaths = Counter()
        self.series = []
        self.t0 = time.time()
        self.events = []
        self.pred_edges = {}
        self.p11_edges = {}
        self.p11_lit_edges = {}

    # ------------------------------------------------------------ funnel
    def _st(self, oid):
        return self.stage.get(oid, 1 if self.none_sl else 0)

    def _adv(self, oid, need, to):
        s = self._st(oid)
        if s >= need and s < to:
            self.stage[oid] = to

    def attach(self, w, ctx, o):
        if self.mode == "p11":
            return
        oid = o.oid

        def ev(code, _w=w, _oid=oid):
            if code == "L":
                self.ct["self_location_exec"] += 1
                self.marg["self_location_executed"].add(_oid)
                self._adv(_oid, 0, 1)
            elif code == "l":
                self.ct["self_location_disabled_hit"] += 1
            elif code == "W":
                self.ct["window_writes"] += 1
                self.marg["target_writes"].add(_oid)
                self._adv(_oid, 3, 4)
            elif code == "B":
                self.ct["birth_calls"] += 1
                if _w.pending.get(_oid) is None:
                    self.ct["birth_calls_no_pending"] += 1
                self.marg["birth_attempted"].add(_oid)
                self._adv(_oid, 4, 5)
        ctx.ev = ev

    def alloc_attempt(self, w, o):
        self.ct["alloc_attempts"] += 1
        self.marg["alloc_attempted"].add(o.oid)
        self._adv(o.oid, 1, 2)

    def alloc_ok(self, w, o, slot):
        self.ct["alloc_ok"] += 1
        self.marg["alloc_succeeded"].add(o.oid)
        self._adv(o.oid, 2, 3)

    def birth_ok(self, w, o, child, fid, wrote, is_repl, partial):
        self.ct["births_ok"] += 1
        self.ct["births_ok_split" if partial else "births_ok_birth"] += 1
        if wrote > 0:
            self.ct["births_wrote_any"] += 1
        self.marg["birth_accepted"].add(o.oid)
        self._adv(o.oid, 5, 6)
        if fid >= 0.90:
            self.ct["births_fid_ge_090"] += 1
            self.marg["fidelity_ge_090"].add(o.oid)
            self._adv(o.oid, 6, 7)
            self.hi_child_parent[child.oid] = o.oid
        if is_repl:
            self.ct["births_evidence_backed"] += 1
            par = self.hi_child_parent.get(o.oid)
            if par is not None:
                self.ct["offspring_evidence_births"] += 1
                self.marg["offspring_evidence_child"].add(par)
                self._adv(par, 7, 8)
        if self.mode == "h4":
            self.ct["epoch_births_endo"] += 1

    def death(self, w, o, why):
        self.deaths[why] += 1
        self.epoch_deaths[why] += 1

    def end_epoch(self, w):
        if self.mode != "h4":
            return
        alive = [o for o in w.orgs if o.alive]
        every = w.t["val_every"]
        self.series.append({
            "e": w.epoch, "pop": len(alive),
            "births_endo_cum": w.ct["births_endogenous"], "births_ext_cum": w.ct["births_external"],
            "deaths": dict(self.epoch_deaths), "validated": (w.epoch % every == 0) and not w.spec.neutral,
            "held_max_alive": round(max((o.held for o in alive), default=0.0), 4),
            "comp_max_alive": round(max((o.comp for o in alive), default=0.0), 4),
            "first_cross_epoch": (w.first_cross or {}).get("epoch"),
            "ops_cum": w.ct["ops"], "mutate_calls_cum": self.ct["mutate_calls"],
            "uniq": len({w._genome(o) for o in alive}),
            "env": ([(e["transform"], e["read_order"]) for e in w.env_pop] if w.env_pop else None),
            "wall_s": round(time.time() - self.t0, 3)})
        self.epoch_deaths = Counter()

    # ------------------------------------------------------------ P-11
    def pair_event(self, w, *, i, a, b, victim, st0, ga, gb, final_half, prov, lit, n,
                   tape_len, fid_other, fid_self, donor_wrote, child_oid, parent_oid):
        vs = 0 if victim is a else 1
        seed = (w.seed, G.cell_id(w.cell), w.epoch, i, vs)
        kw = dict(n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=st0[0], st_b=st0[1],
                  budget=w.t["slice"], ops_mask=w._ops_mask(), cmr=w.copy_mut, victim_side=vs,
                  seed=seed)
        res = p11.assay(z8, **kw)
        v0 = 0 if vs == 0 else n
        diag = p11.ordinary_diagnostics(z8, final_half=bytes(final_half),
                                        prov_half=prov[v0:v0 + n], lit_half=lit[v0:v0 + n], **kw)
        # literal reading (last write at all) of criterion 4, reported beside the primary
        lit_pass = sum(1 for d in res["draws"]
                       if d["C2"] and d["C5"] and d["n_directed"]
                       and d["donor_last_wrote_share"] >= constants.C["P11_AUTHORSHIP"])
        rec = {"epoch": w.epoch, "pair": i, "victim_side": vs, "child": child_oid,
               "parent": parent_oid, "fid_other": round(fid_other, 4),
               "fid_self": round(fid_self, 4), "donor_wrote": donor_wrote, "n": n,
               "p11": res["pass"], "draws_passed": res["draws_passed"],
               "C2": res["C2_majority"], "C4": res["C4_majority"], "C5": res["C5_majority"],
               "p11_literal": lit_pass >= constants.C["P11_MAJORITY"],
               "draws": [{k: d[k] for k in ("fid_init", "fid_final", "n_directed",
                                             "donor_authored_share", "donor_last_wrote_share",
                                             "fid_donor_disabled")} for d in res["draws"]],
               **diag}
        if res["pass"] or res["draws_passed"]:
            # the donor's pre-interaction genome: what H2 arm B would implant
            rec["donor_genome"] = bytes(gb if vs == 0 else ga).hex()
        self.events.append(rec)
        self.pred_edges[child_oid] = parent_oid
        if res["pass"]:
            self.p11_edges[child_oid] = parent_oid
        if rec["p11_literal"]:
            self.p11_lit_edges[child_oid] = parent_oid


def frozen_record(run_id):
    fam = run_id.split("-")[0]
    d = FROZEN / "runs" / fam / run_id
    return (json.loads((d / "CONFIG.json").read_text()),
            json.loads((d / "RESULT.json").read_text())["summary"])


def _norm(x):
    return json.loads(json.dumps(x, default=str))


def replay(run_id, mode, cell=None, seed=None, tier=None, invaders=0, check=True):
    """Replay one run. For a frozen run only run_id is needed; a NEW forensic run (for
    example an exactly matched control that the frozen record never ran) passes cell,
    seed and tier and is marked check=False because there is nothing frozen to match."""
    frozen_s = None
    if cell is None:
        cfg, frozen_s = frozen_record(run_id)
        job = cfg["job"]
        cell, seed, tier, invaders = job["cell"], job["seed"], job["tier"], job.get("invaders", 0)
    t0 = time.time()
    r = world.Runner(cell, seed, tier=tier, invaders=invaders)
    fx = FX(mode, cell)
    r.fx = fx
    s = r.run()
    wall = round(time.time() - t0, 2)
    status = "NEW_RUN_UNCHECKED"
    diffs = []
    if check and frozen_s is not None:
        ns = _norm(s)
        diffs = sorted(k for k in set(ns) | set(frozen_s) if ns.get(k) != frozen_s.get(k))
        status = "REPLAY_MATCH" if not diffs else "REPLAY_MISMATCH"
    out = {"run_id": run_id, "mode": mode, "status": status, "mismatch_fields": diffs,
           "cell": cell, "seed": seed, "tier": tier, "invaders": invaders, "wall_s": wall,
           "summary_key": {k: s.get(k) for k in ("births_endogenous", "births_external",
                                                  "replication_events", "alloc_calls",
                                                  "alloc_fails", "pop_final", "held_max",
                                                  "epochs_run", "ops", "deaths", "extinct")},
           "ct": dict(fx.ct), "deaths_by_cause": dict(fx.deaths),
           "organisms_total": r.next_oid}
    if mode == "funnel":
        seq = []
        for k in range(1, 9):
            seq.append(sum(1 for oid in range(r.next_oid) if fx._st(oid) >= k))
        out["funnel_sequential"] = dict(zip(FUNNEL, seq))
        out["funnel_marginal"] = {k: len(fx.marg[k]) for k in FUNNEL}
        if fx.none_sl:
            out["funnel_marginal"]["self_location_executed"] = None
        out["max_stage"] = max((fx._st(oid) for oid in range(r.next_oid)), default=0)
    if mode == "h4":
        out["series"] = fx.series
        out["first_cross"] = s.get("first_cross")
        out["extinct_epoch"] = next((x["e"] for x in fx.series if x["pop"] == 0), None)
    if mode == "p11":
        dp, _ = depth(fx.pred_edges)
        d11, _ = depth(fx.p11_edges)
        dl, _ = depth(fx.p11_lit_edges)
        ev = fx.events
        out["p11"] = {
            "n_pred_events": len(ev), "n_p11_events": sum(e["p11"] for e in ev),
            "n_p11_literal_events": sum(e["p11_literal"] for e in ev),
            "fail_C2": sum(1 for e in ev if not e["C2"]),
            "fail_C4": sum(1 for e in ev if not e["C4"]),
            "fail_C5": sum(1 for e in ev if not e["C5"]),
            "max_pred_depth": dp, "max_p11_depth": d11, "max_p11_literal_depth": dl,
            "first_event": ev[0] if ev else None,
            "first_p11_event": next((e for e in ev if e["p11"]), None)}
        out["events_gz"] = True
        out["_events"] = ev
    return out


def _worker(args):
    run_id, mode, outdir = args
    try:
        res = replay(run_id, mode)
    except Exception as e:                                     # noqa: BLE001
        import traceback
        res = {"run_id": run_id, "mode": mode, "status": "ERROR",
               "error": "%s: %s" % (type(e).__name__, e), "tb": traceback.format_exc()[-1500:]}
    ev = res.pop("_events", None)
    if ev is not None:
        with gzip.open(pathlib.Path(outdir) / (run_id + ".events.jsonl.gz"), "wt") as fh:
            for e in ev:
                fh.write(json.dumps(e) + "\n")
    (pathlib.Path(outdir) / (run_id + ".json")).write_text(json.dumps(res, default=str))
    return run_id, res.get("status"), res.get("wall_s")


def run_many(run_ids, mode, outdir, workers=12):
    """Replay many runs in a process pool; resumable (skips runs already written)."""
    import multiprocessing as mp
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    todo = [r for r in run_ids if not (outdir / (r + ".json")).exists()]
    print("todo", len(todo), "of", len(run_ids), flush=True)
    done = 0
    with mp.Pool(workers) as pool:
        for rid, st, wall in pool.imap_unordered(_worker, [(r, mode, str(outdir)) for r in todo]):
            done += 1
            print("%5d/%d %s %s %ss" % (done, len(todo), rid, st, wall), flush=True)


if __name__ == "__main__":
    mode, listfile, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    ids = [l.strip() for l in open(listfile) if l.strip()]
    run_many(ids, mode, outdir, workers)
