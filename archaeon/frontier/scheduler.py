"""The Python scheduler (operator directive s3): discovers experiment specs in the registry, checks
capabilities, executes every runnable spec, skips locally blocked ones, resumes interrupted runs from
their last checkpoint, writes structured receipts first, branches on results, advances the queue.
No conversational decision anywhere on the path.

    python -m archaeon.frontier.scheduler --run [--wall-hours 6] [--max-items N]
    python -m archaeon.frontier.scheduler --self-test
    python -m archaeon.frontier.scheduler --status

Global halt only via integrity.IntegrityHalt (assertions), written to GLOBAL_HALT.json with the invariant,
the receipt and the invalidated evidence; the scheduler refuses to start while that file exists.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign6 import segment as SG                                 # noqa: E402
from archaeon.campaign6 import substrate as SUB                              # noqa: E402
from archaeon.campaign6.worlds import sample_world                           # noqa: E402
from archaeon.campaign6.pressure import schedules as P                       # noqa: E402
from archaeon.frontier import capabilities as CAP                            # noqa: E402
from archaeon.frontier import integrity as INT                               # noqa: E402
from archaeon.frontier import specs as SP                                    # noqa: E402
from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402
from archaeon.frontier.allocation import RULES                               # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
HALT = HERE / "GLOBAL_HALT.json"
SUPPRESSIONS = HERE / "suppressions"


def frozen_table() -> Tuple[dict, dict]:
    frozen = json.loads((REPO / "archaeon/campaign6/observatory/DETECTORS_FROZEN_candidate.json").read_text(encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2,
                "environmental_modification": 0, "niche_divergence": 0.5, "regime_persistence": 1 / 16})
    return thr, frozen


def load_suppressions() -> List[dict]:
    out = []
    for p in sorted(SUPPRESSIONS.glob("*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        src = REPO / s["source"]
        s["_active"] = False
        if src.exists():
            v = json.loads(src.read_text(encoding="utf-8"))
            s["_active"] = v.get(s["condition"]["field"]) == s["condition"]["equals"]
            s["_source_state"] = {k: v.get(k) for k in ("verdict", "falsifier_status", "neighbourhood_exhausted")}
        out.append(s)
    return out


def suppressed(spec: dict, sups: List[dict]) -> Optional[dict]:
    eid = spec["experiment_id"]; fam = spec["family_id"]
    for s in sups:
        if not s["_active"]:
            continue
        if eid in s["covers_experiments"] or eid.split("/")[0] in s["covers_experiments"] or fam in s["covers_families"]:
            return s
    return None


# ---------------------------------------------------------------- spec -> segment kwargs + population (pure code)
def resolve(spec: dict, thr: dict, frozen: dict) -> Tuple[dict, List[dict]]:
    w = spec["world"]
    if w["kind"] == "c6.composed.sample":
        rec = sample_world(w["seed"], bin_target=w.get("bin"))
        world = {"kind": "c6.composed.v1", "params": rec["params"]}
    else:
        world = w
    pr = spec["params"]; sc = spec["schedule"]; gens = pr["generations"]
    sched = {"stable": lambda: P.stable(gens), "labeled": lambda: P.labeled(sc["seed"], gens), "unlabeled": lambda: P.unlabeled(sc["seed"], gens)}[sc["kind"]]()
    pop = spec["organism"]["population"]; N = pop["N"]
    if pop["source"] == "c4_parents":
        parents = C1.parents_from_population()
        from proteus.foundry.prng import SplitMix64, seed_from
        rng = SplitMix64(seed_from("frontier.pop", pop["seed"]))
        init = [parents[rng.randbelow(len(parents))]["parent"] for _ in range(N)]
    else:
        init = SUB.gen0_any(spec["organism"]["profile"], N, pop["seed"])
    kw = dict(run_id=spec["experiment_id"].replace("/", "_"), provenance=spec["provenance"], world=world, profile=spec["organism"]["profile"], schedule=sched, N=N, E=pr["E"],
              archive=pr["archive"], thresholds=thr, spread=frozen["spread"], seed=spec["seed"], freeze_policy=pr["freeze_policy"], log_scores=spec["telemetry"].get("log_scores", False),
              world_options=pr.get("world_options") or {}, nominate=pr.get("nominate") or {})
    return kw, init


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(HERE)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def run_dir(spec: dict) -> Path:
    return RUNS / spec["family_id"].split(".")[0] / spec["experiment_id"].replace("/", "_")


def execute(spec: dict, thr: dict, frozen: dict, caps: Dict[str, bool]) -> dict:
    """Run one spec to completion (resuming from the last chunk on disk); write RECEIPT.json first and update it per chunk."""
    d = run_dir(spec); d.mkdir(parents=True, exist_ok=True)
    receipt_path = d / "RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {"schema": "archaeon.frontier.receipt.v1", "experiment_id": spec["experiment_id"], "spec": spec, "capabilities": caps,
                                                                                                    "status": "STARTED", "chunks": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "integrity": []}
    receipt_path.write_text(json.dumps(receipt, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    kw, init = resolve(spec, thr, frozen)
    pr = spec["params"]; chunk = pr["chunk"]; gens = pr["generations"]
    n_chunks = max(1, (gens + chunk - 1) // chunk)
    done = {c["chunk"] for c in receipt["chunks"] if c.get("status") == "DONE"}
    # resume: load the last finished chunk's checkpoint_out
    ck = None
    if done:
        last = max(done)
        with gzip.open(d / ("chunk_%03d.json.gz" % last), "rt", encoding="utf-8") as f:
            ck = json.load(f)["out"]["checkpoint_out"]
        start = last + 1
    else:
        spec0 = SG.make_spec(g0=0, g1=min(chunk, gens), **kw); ck = SG.initial_checkpoint(spec0, init); start = 0
    chunks_loaded = []
    total = sum(c["evaluations"] for c in receipt["chunks"] if c.get("status") == "DONE")
    for c in range(start, n_chunks):
        g0, g1 = c * chunk, min(gens, (c + 1) * chunk)
        seg = SG.make_spec(g0=g0, g1=g1, **kw)
        INT.check_provenance(spec, seg)
        out = SG.run_segment(seg, ck)
        INT.check_evidence_writes(out)
        if c == 0 and spec["checkpoint"].get("replay_required") == "A":
            out2 = SG.run_segment(seg, ck); INT.check_replay_A(seg["spec_hash"], out["out_digest"], out2["out_digest"], c)
            receipt["integrity"].append({"chunk": c, "replay_A": "SAME"})
        path = d / ("chunk_%03d.json.gz" % c)
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump({"spec": seg, "checkpoint_in_digest": ck["digest"], "out": out}, f, default=str)
        chunks_loaded.append({"out": out, "checkpoint_in_digest": ck["digest"]})
        INT.check_checkpoint_ancestry(chunks_loaded)
        meas = {}
        if spec["params"].get("measurements"):
            from archaeon.frontier.design import measurement as MEAS
            m_all = MEAS.measure(out, frozen["spread"]); meas = {k: v for k, v in m_all.items() if k in spec["params"]["measurements"]}
            meas["authority"] = "NONE"                                # CALIBRATION_EPOCH-002 rulers: discovery instruments; never branching/priority/freeze/selection
        rec = {"chunk": c, "g0": g0, "g1": g1, "status": "DONE", "spec_hash": seg["spec_hash"], "out_digest": out["out_digest"], "checkpoint_out": out["checkpoint_out"]["digest"], "measurements": meas,
               "evaluations": out["evaluations"], "events": len(out["events"]), "freezes": len(out["freezes"]), "anchors": len(out["anchors"]), "wall_s": out["wall_s"],
               "fired": _count(out, "fired"), "unable": _count(out, "unable"), "path": _rel(path)}
        receipt["chunks"].append(rec); total += out["evaluations"]; ck = out["checkpoint_out"]
        receipt["status"] = "RUNNING"; receipt["evaluations"] = total
        receipt_path.write_text(json.dumps(receipt, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
        if total >= spec["budget"]["evaluations"]:
            break
    receipt["status"] = "DONE"; receipt["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    receipt_path.write_text(json.dumps(receipt, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    return receipt


def _count(out: dict, key: str) -> dict:
    c: Dict[str, int] = {}
    for e in out["events"]:
        for d in e[key]:
            c[d] = c.get(d, 0) + 1
    return c


# ---------------------------------------------------------------- branching (code, from the receipt)
ADMITTED = ("unexpected_transfer", "lineage_discontinuity", "behavioral_novelty", "environmental_modification", "niche_divergence", "regime_persistence")


def descendants(spec: dict, receipt: dict) -> List[Tuple[dict, str, str]]:
    """(spec, why, pool). Controls come only from a run that is not itself a control or descendant (depth 0), go to AUDIT;
    persistence (x4 horizon) only when an ADMITTED ruler fired, goes to EXPLOITATION; adjacent bins only from a depth-0
    composed-world run with classifier failure, EXPLORATION. Runaway chains of controls-of-controls are thereby impossible."""
    fired: Dict[str, int] = {}
    for c in receipt["chunks"]:
        for d, n in c["fired"].items():
            fired[d] = fired.get(d, 0) + n
    depth = spec["experiment_id"].count("/") - spec["family_id"].count("/")
    if depth > 0:
        return []
    # Scientific authority is Archaeon's (DF-013): the scheduler proposes ONLY the two evidence controls, and only when an
    # admitted ruler fired; every other descendant is authored under archaeon/frontier/design/.
    out = []
    adm = {d: n for d, n in fired.items() if d in ADMITTED}
    if adm:
        for ctl in spec["controls"]:
            if ctl["kind"] in ("seed", "initialization") and ctl["spec_delta"]:
                out.append((SP.apply_delta(spec, ctl["spec_delta"]), "control:" + ctl["kind"], "AUDIT"))
    return out


# ---------------------------------------------------------------- the loop
PURSUE = HERE / "pursue.json"          # Archaeon-authored: {"lineages": {lid: multiplier}, "families": {family_id: multiplier}, "note": ...}


def pursue_table() -> dict:
    try:
        return json.loads(PURSUE.read_text(encoding="utf-8")) if PURSUE.exists() else {}
    except Exception:                                                # noqa: BLE001
        return {}


def _mult(entry) -> float:
    """A multiplier applies only while LIVE and within its evaluation expiry; a bare number (legacy) is treated as expired."""
    if not isinstance(entry, dict):
        return 1.0
    if entry.get("state") != "LIVE" or entry.get("spent_evaluations", 0) >= entry.get("expires_evaluations", 0):
        return 1.0
    return float(entry.get("multiplier", 1.0))


def charge_pursuit(lineage_id: str, family: str, evaluations: int) -> None:
    """Charge a finished run to the multipliers that steered it; expire them when spent; record it."""
    if not PURSUE.exists():
        return
    pt = json.loads(PURSUE.read_text(encoding="utf-8")); changed = False
    for key, table in (("lineages", lineage_id), ("families", family)):
        e = pt.get(key, {}).get(table)
        if isinstance(e, dict) and e.get("state") == "LIVE":
            e["spent_evaluations"] = e.get("spent_evaluations", 0) + evaluations; changed = True
            if e["spent_evaluations"] >= e.get("expires_evaluations", 0):
                e["state"] = "EXPIRED"; e["expired_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                pt.setdefault("history", []).append({"expired": table, "at": e["expired_at"], "spent": e["spent_evaluations"]})
    if changed:
        PURSUE.write_text(json.dumps(pt, indent=1) + "\n", encoding="utf-8", newline="\n")


def choose_pool(q: Queues, shares: Dict[str, float], spent: Dict[str, int]) -> Optional[str]:
    tot = max(1, sum(spent.values())); best, gap = None, -1.0
    for pool in ("EXPLORATION", "EXPLOITATION", "AUDIT", "REVISIT"):
        if not q.pending(pool):
            continue
        share = shares.get("AUDIT" if pool == "REVISIT" else pool, 0.0)
        g = share - spent.get(pool, 0) / tot
        if g > gap:
            best, gap = pool, g
    return best


def spec_of(reg: Registry, item: dict) -> Optional[dict]:
    rec = reg.get(item["lineage_id"])
    for t in rec["transformations"]:
        if t["id"] == item["transformation_id"]:
            return t.get("spec")
    return None


ENFORCEMENT_FILE = "SUPPRESSION_ENFORCEMENT.json"


def _canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), default=str)


class Enforcement:
    """OPERATIONAL ACCOUNTING of suppression enforcement per queued item -- NOT observations (instrumentation repair 2026-09-26).

    Defect repaired: step() wrote one full BLOCKED_BY_SUPPRESSION event on EVERY retry of a blocked item. With one pending item the
    loop re-popped it each tick, so EVENTS.jsonl got 299,991 identical rows for ONE decision (PROTEUS-46 on C4-cliff.T1). That
    historical file is NOT touched.

    Rule now: a scientific event is written only on an enforcement-STATE TRANSITION of an item (lineage_id, transformation):
      * BLOCKED_BY_SUPPRESSION when the item becomes blocked, or when its tuple (suppression, canonical source_state) changes;
      * SUPPRESSION_LIFTED when a previously blocked item is next found unblocked.
    Retries under an unchanged tuple only update this file: retries, first_blocked_at, last_blocked_at. It lives beside EVENTS.jsonl
    as <registry>/SUPPRESSION_ENFORCEMENT.json and carries an explicit `accounting_only` flag. Closed episodes are kept in
    `closed` (reason SUPERSEDED | LIFTED)."""

    def __init__(self, root: Path):
        self.path = Path(root) / ENFORCEMENT_FILE
        if self.path.exists():
            self.d = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.d = {"schema": "archaeon.frontier.suppression_enforcement.v1", "accounting_only": True,
                      "note": "operational retry accounting; NOT scientific observations; scientific transitions are the events in EVENTS.jsonl",
                      "open": {}, "closed": []}

    @staticmethod
    def key(lid: str, tid: str) -> str:
        return lid + "|" + tid

    def _save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.d, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n"); os.replace(tmp, self.path)

    def blocked(self, lid: str, tid: str, suppression: str, source_state, now: str) -> bool:
        """Record one blocked retry. True = an enforcement-state transition (the caller writes the scientific event)."""
        k = self.key(lid, tid); canon = _canon(source_state); cur = self.d["open"].get(k)
        if cur is not None and cur["suppression"] == suppression and cur["source_state_canonical"] == canon:
            cur["retries"] += 1; cur["last_blocked_at"] = now; self._save(); return False
        if cur is not None:
            self.d["closed"].append(dict(cur, closed_at=now, reason="SUPERSEDED"))
        self.d["open"][k] = {"lineage_id": lid, "transformation": tid, "suppression": suppression, "source_state_canonical": canon,
                             "first_blocked_at": now, "last_blocked_at": now, "retries": 1}
        self._save(); return True

    def unblocked(self, lid: str, tid: str, now: str) -> Optional[dict]:
        """The item passed the suppression check. Returns the closed episode if it had been blocked (a transition), else None."""
        cur = self.d["open"].pop(self.key(lid, tid), None)
        if cur is None: return None
        rec = dict(cur, closed_at=now, reason="LIFTED"); self.d["closed"].append(rec); self._save(); return rec

    def get(self, lid: str, tid: str) -> Optional[dict]:
        return self.d["open"].get(self.key(lid, tid))


_ENF: Dict[str, Enforcement] = {}


def enforcement(reg: Registry) -> Enforcement:
    k = str(Path(reg.root).resolve())
    if k not in _ENF: _ENF[k] = Enforcement(reg.root)
    return _ENF[k]


def step(reg: Registry, q: Queues, shares, spent, thr, frozen, caps, sups) -> dict:
    pool = choose_pool(q, shares, spent)
    if pool is None:
        return {"status": "IDLE"}
    # pursuit steering: within the pool, Archaeon's multipliers reorder the pending items (data, not prose)
    pt = pursue_table()
    if pt:
        pend = q.pending(pool)
        def _w(it):
            m = _mult(pt.get("lineages", {}).get(it["lineage_id"])) * _mult(pt.get("families", {}).get(it["transformation_id"].split("/")[0].split(".")[0]))
            return -(it["priority"] * m)
        pend.sort(key=_w)
        if pend:
            q.set_state(pool, pend[0]["item_id"], "CLAIMED"); item = q.items[pool][pend[0]["item_id"]]
        else:
            return {"status": "IDLE"}
    else:
        item = q.pop(pool)
    lid = item["lineage_id"]; tid = item["transformation_id"]
    spec = spec_of(reg, item)
    if spec is None:
        q.set_state(pool, item["item_id"], "DROPPED", note="no spec"); reg.event(lid, "DROPPED", {"transformation": tid, "reason": "no executable spec"})
        return {"status": "DROPPED", "lineage": lid, "transformation": tid}
    try:
        spec = SP.validate_spec(spec)
    except SP.SpecError as e:
        q.set_state(pool, item["item_id"], "DROPPED", note="invalid spec: %s" % e); reg.event(lid, "INVALID_SPEC", {"transformation": tid, "error": str(e)})
        return {"status": "INVALID_SPEC", "lineage": lid, "transformation": tid, "error": str(e)}
    miss = CAP.missing(spec["required_capabilities"], caps)
    if miss:
        q.set_state(pool, item["item_id"], "PENDING", note="BLOCKED_MISSING_CAPABILITY " + ",".join(miss))
        it = dict(q.items[pool][item["item_id"]]); it["priority"] -= 1.0; q._append(pool, it)
        reg.event(lid, "BLOCKED_MISSING_CAPABILITY", {"transformation": tid, "missing": miss})
        return {"status": "BLOCKED_MISSING_CAPABILITY", "lineage": lid, "transformation": tid, "missing": miss}
    sup = suppressed(spec, sups)
    if sup:
        q.set_state(pool, item["item_id"], "PENDING", note="BLOCKED_BY_SUPPRESSION " + sup["suppression_id"])
        it = dict(q.items[pool][item["item_id"]]); it["priority"] -= 1.0; q._append(pool, it)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); enf = enforcement(reg)
        transition = enf.blocked(lid, tid, sup["suppression_id"], sup.get("_source_state"), now)
        if transition:                                                    # one scientific event per enforcement-state transition
            reg.event(lid, "BLOCKED_BY_SUPPRESSION", {"transformation": tid, "suppression": sup["suppression_id"], "source_state": sup.get("_source_state"),
                                                      "enforcement": "STATE_TRANSITION"})
        return {"status": "BLOCKED_BY_SUPPRESSION", "lineage": lid, "transformation": tid, "suppression": sup["suppression_id"],
                "event_written": transition, "retries": enf.get(lid, tid)["retries"]}
    lifted = enforcement(reg).unblocked(lid, tid, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    if lifted is not None:
        reg.event(lid, "SUPPRESSION_LIFTED", {"transformation": tid, "suppression": lifted["suppression"],
                                              "source_state": json.loads(lifted["source_state_canonical"]), "enforcement": "STATE_TRANSITION"})
    before = sum(1 for _ in open(reg.events_path, encoding="utf-8"))
    receipt = execute(spec, thr, frozen, caps)
    INT.check_registry_write(reg.events_path, before)
    reg.record_run(lid, tid, {"receipt": _rel(run_dir(spec) / "RECEIPT.json"), "chunks": [c["out_digest"] for c in receipt["chunks"]]},
                   status="RUN", evaluations=receipt["evaluations"])
    fired = {}
    for c in receipt["chunks"]:
        for d, n in c["fired"].items():
            fired[d] = fired.get(d, 0) + n
    reg.observe(lid, "%s: %d chunks, %d evaluations, firings %s" % (tid, len(receipt["chunks"]), receipt["evaluations"], fired), ref={"receipt": receipt["chunks"][-1]["path"] if receipt["chunks"] else None})
    new = []
    seen = {t["id"] for t in reg.get(lid)["transformations"]}
    for dspec, why, dpool in descendants(spec, receipt):
        did = dspec["experiment_id"]
        if did in seen:
            continue
        seen.add(did)
        new.append({"id": did, "dims": [why], "from": tid, "to": why, "budget_evaluations": dspec["budget"]["evaluations"], "status": "PENDING", "trigger": why, "spec": dspec, "pool": dpool})
    if new:
        reg.add_transformations(lid, new)
        for t in new:
            q.push(t["pool"], lineage_id=lid, transformation_id=t["id"], priority=item["priority"] - 0.1, lane=t["spec"]["provenance"]["lane"] if t["trigger"].startswith("control") else "EVOLUTION_GENERATED",
                   budget_evaluations=t["budget_evaluations"], note="branch: " + t["trigger"])
    q.set_state(pool, item["item_id"], "DONE"); spent[pool] = spent.get(pool, 0) + receipt["evaluations"]
    charge_pursuit(lid, spec["family_id"].split(".")[0], receipt["evaluations"])
    run_due_readouts(reg)
    return {"status": "RAN", "pool": pool, "lineage": lid, "transformation": tid, "evaluations": receipt["evaluations"], "chunks": len(receipt["chunks"]), "fired": fired, "descendants": [t["id"] for t in new]}


READOUTS = HERE / "design" / "readouts.json"     # [{"id", "module", "lineage", "condition": {"family", "done_min"}, "state": "PENDING"|"DONE", ...}]


def run_due_readouts(reg: Registry) -> None:
    """A readout is a durable object: when its condition holds (N receipts DONE in the family) the scheduler runs the module and
    writes the result into the lineage as an OBSERVATION with the file reference. Whoever is alive later finds it in state."""
    if not READOUTS.exists():
        return
    rs = json.loads(READOUTS.read_text(encoding="utf-8")); changed = False
    for r in rs:
        if r.get("state") != "PENDING":
            continue
        fam = r["condition"]["family"]; done = 0; prefixes = r["condition"].get("ids_prefix")
        for rp in (RUNS / fam.split(".")[0]).glob("*/RECEIPT.json") if (RUNS / fam.split(".")[0]).exists() else []:
            try:
                rc_ = json.loads(rp.read_text(encoding="utf-8"))
                if rc_.get("status") == "DONE" and (not prefixes or any(rc_["experiment_id"].split("/")[1].startswith(p) for p in prefixes)):
                    done += 1
            except Exception:                                        # noqa: BLE001
                pass
        if done >= r["condition"]["done_min"]:
            import importlib, io, contextlib
            mod = importlib.import_module("archaeon.frontier.design." + r["module"])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod.main()
            out = buf.getvalue()
            path = out.strip().splitlines()[-1].replace("written ", "") if "written" in out else None
            reg.observe(r["lineage"], "readout %s ran (condition: %d/%d %s receipts DONE); result file %s" % (r["module"], done, r["condition"]["done_min"], fam, path), ref={"readout": path, "module": r["module"]})
            r["state"] = "DONE"; r["ran_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); r["result"] = path; r["rc"] = rc; changed = True
    if changed:
        READOUTS.write_text(json.dumps(rs, indent=1) + "\n", encoding="utf-8", newline="\n")


def run(wall_hours: float, max_items: int, reg=None, q=None) -> int:
    if HALT.exists():
        print("REFUSED: GLOBAL_HALT.json exists; resolve the named invariant first", flush=True); return 3
    reg = reg or Registry(); q = q or Queues()
    thr, frozen = frozen_table(); caps = CAP.present(); sups = load_suppressions()
    shares = dict(RULES["initial"]); spent: Dict[str, int] = {}
    recovered = 0
    for pool in q.items:
        for it in list(q.items[pool].values()):
            if it["state"] == "CLAIMED":
                q.set_state(pool, it["item_id"], "PENDING", note="recovered at start"); recovered += 1
    print(json.dumps({"scheduler": "start", "capabilities": {k: v for k, v in caps.items() if not k.endswith(".error")}, "suppressions": [(s["suppression_id"], s["_active"]) for s in sups], "recovered": recovered}), flush=True)
    t0 = time.time(); n = 0
    while n < max_items and time.time() - t0 < wall_hours * 3600:
        try:
            r = step(reg, q, shares, spent, thr, frozen, caps, sups)
        except INT.IntegrityHalt as h:
            HALT.write_text(json.dumps({"invariant": h.invariant, "receipt": h.receipt, "invalidated": h.invalidated, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
            print(json.dumps({"status": "GLOBAL_HALT", "invariant": h.invariant, "receipt": h.receipt, "invalidated": h.invalidated}, default=str), flush=True); return 4
        except Exception:                                                # noqa: BLE001  a local failure: record, drop the item, continue
            print(json.dumps({"status": "LOCAL_ERROR", "traceback": traceback.format_exc()[-1500:]}), flush=True)
            n += 1; continue
        r["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); print(json.dumps(r, default=str), flush=True)
        if r["status"] == "IDLE":
            break
        n += 1
    print(json.dumps({"scheduler": "stop", "items": n, "registry": reg.summary(), "queues": q.status(), "spent": spent, "wall_s": round(time.time() - t0, 1)}, indent=1), flush=True)
    return 0


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="frontier_sched_"))
    global RUNS
    RUNS = tmp / "runs"
    reg = Registry(tmp / "registry"); q = Queues(tmp / "queues")
    spec = SP.make_spec(family_id="B-scatter", experiment_id="B-scatter.selftest", world={"kind": "c6.composed.sample", "seed": 10000, "bin": 3}, profile="v0",
                        population={"source": "c4_parents", "seed": 1, "N": 16}, E=4, generations=20, chunk=10, schedule={"kind": "unlabeled", "seed": 10000}, seed=10000,
                        budget_evaluations=320, lane="PROCEDURAL", generator="frontier.scatter")
    gspec = SP.make_spec(family_id="G-test", experiment_id="G-test.selftest", world={"kind": "wse.WorldSpec", "knobs": C1.ENVS["W0"].knobs()}, profile="graph",
                         population={"source": "foundry", "seed": 1, "N": 16}, E=4, generations=10, chunk=10, schedule={"kind": "stable", "seed": 0}, seed=7, budget_evaluations=160, lane="LLM_PROPOSED", generator="t")
    lid = reg.create(originating_observation={"key": "B-scatter", "summary": "self-test"}, mode="BREADTH", title="st",
                     transformations=[{"id": "B-scatter.selftest", "dims": ["random_seed"], "from": "-", "to": "-", "budget_evaluations": 320, "status": "PENDING", "spec": spec},
                                      {"id": "G-test.selftest", "dims": ["organism_profile"], "from": "v0", "to": "graph", "budget_evaluations": 160, "status": "PENDING", "spec": gspec},
                                      {"id": "C4-cliff.T1", "dims": ["organism_profile"], "from": "v0", "to": "graph", "budget_evaluations": 160, "status": "PENDING", "spec": dict(gspec, experiment_id="C4-cliff.T1")}])
    q.push("EXPLORATION", lineage_id=lid, transformation_id="B-scatter.selftest", priority=1.0, lane="PROCEDURAL", budget_evaluations=320)
    q.push("EXPLOITATION", lineage_id=lid, transformation_id="G-test.selftest", priority=1.0, lane="LLM_PROPOSED", budget_evaluations=160)
    q.push("EXPLOITATION", lineage_id=lid, transformation_id="C4-cliff.T1", priority=0.9, lane="LLM_PROPOSED", budget_evaluations=160)
    thr, frozen = frozen_table(); caps = CAP.present(); sups = load_suppressions(); spent = {}
    results = [step(reg, q, RULES["initial"], spent, thr, frozen, caps, sups) for _ in range(5)]
    st = [r["status"] for r in results]
    # resume: mark the first receipt's last chunk as not done and re-execute -> only the missing chunk runs
    rec = reg.get(lid); first = [t for t in rec["transformations"] if t["id"] == "B-scatter.selftest"][0]
    rp = run_dir(first["spec"]) / "RECEIPT.json"; r0 = json.loads(rp.read_text(encoding="utf-8"))
    r0["chunks"] = r0["chunks"][:1]; rp.write_text(json.dumps(r0), encoding="utf-8")
    r1 = execute(SP.validate_spec(first["spec"]), thr, frozen, caps)
    rep = {"statuses": st, "graph_ran": "RAN" in st and any(r.get("transformation") == "G-test.selftest" and r["status"] == "RAN" for r in results),
           "suppressed": any(r["status"] == "BLOCKED_BY_SUPPRESSION" and r.get("transformation") == "C4-cliff.T1" for r in results),
           "resume_chunks": [c["chunk"] for c in r1["chunks"]], "resume_status": r1["status"], "descendants": sum(len(r.get("descendants", [])) for r in results),
           "receipt_integrity": r1["integrity"], "tmp": str(tmp)}
    print(json.dumps(rep, indent=1, default=str))
    ok = rep["graph_ran"] and rep["suppressed"] and rep["resume_status"] == "DONE" and rep["resume_chunks"] == [0, 1]
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--status", action="store_true")
    ap.add_argument("--wall-hours", type=float, default=6.0); ap.add_argument("--max-items", type=int, default=100000)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.status:
        reg = Registry(); q = Queues(); print(json.dumps({"registry": reg.summary(), "queues": q.status(), "halt": HALT.exists(), "capabilities": CAP.present()}, indent=1)); return 0
    if a.run:
        return run(a.wall_hours, a.max_items)
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
