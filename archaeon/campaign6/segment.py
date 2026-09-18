"""The SEGMENT loop (Campaign 6 item 2): generations [g0, g1) of one population in one world under
one pressure slice, checkpoint in -> checkpoint out, with T0 sidecar rows, anchors, executor-side
detectors, freeze packets and observations per archived generation. Contract: SEGMENT_CONTRACT.md.

    out = run_segment(spec, checkpoint_in)          # pure function of (spec, checkpoint_in)

Determinism: the same (spec, checkpoint_in) yields byte-identical outputs (self-test). Vivarium
wraps this callable as its segment kind; the engine sees the observations, anchors, freezes and
artifacts it produces, never the rows.

Phase 0 profile: v0 (tape VM) on the WorldSpec worlds. The organism profile, world and pressure
schedule are resolved through small registries so the graph profile (Proteus), Axis W worlds and
Axis P schedules plug in without changing this file.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import evaluate, _tournament, MASK62
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign4 import c4_01 as C1
from archaeon.campaign6 import schemas as S
from archaeon.campaign6.c6base import LANES
from archaeon.campaign6.observatory.fingerprint import rows_v0
from archaeon.campaign6.observatory import detectors as D
from archaeon.campaign6 import substrate as SUB
from archaeon.campaign6.worlds import ComposedWorld, evaluate_world
from archaeon.campaign6.pressure import schedules as P

SCHEMA_SPEC = "archaeon.c6.segment_spec.v1"
SCHEMA_CKPT = "archaeon.c6.checkpoint.v1"
ANCHOR_INTERVAL = 1000                      # R4: never retuned
ANCESTOR_DEPTH = 4                          # freeze members: subject, parent, 4 ancestors, siblings, world, pressure window


def _strip_stamps(obj):
    """Remove wall-clock stamps (preserved_at, at) before digesting: forensic timestamps are kept in the record, never in identity."""
    if isinstance(obj, dict):
        return {k: _strip_stamps(v) for k, v in obj.items() if k not in ("preserved_at", "at")}
    if isinstance(obj, list):
        return [_strip_stamps(v) for v in obj]
    return obj


def _h(obj) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(_strip_stamps(obj), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


# ---------------------------------------------------------------- registries (Phase 0: v0 + WorldSpec + stable pressure)
def resolve_world(world: dict):
    if world["kind"] == "wse.WorldSpec":
        return WorldSpec(**world["knobs"])
    if world["kind"] == "c6.composed.v1":
        return ComposedWorld(world["params"])
    raise ValueError("unknown world kind %r" % world["kind"])


def resolve_profile(profile: str):
    """Returns (evaluate_fn(manifest, episodes, rng_seed) -> ev, descend_fn(parent, seed, mate) -> (child, record), answers_fn(manifest, episodes))."""
    if profile == "v0":
        return (lambda m, eps, rs: evaluate(m, eps, rng_seed=rs, reward_mode="per_ask"), lambda p, s, mate=None: descend(p, s, mate=mate), C1.answers)
    if profile == "graph":
        # Proteus's handover (proteus/graph/handover.py): the same five call shapes, dispatched on the manifest schema
        return (lambda m, eps, rs: SUB.evaluate_any(m, eps, rng_seed=rs, reward_mode="per_ask"), lambda p, s, mate=None: SUB.descend_for(p, s, mate=mate), SUB.answers_any)
    if profile == "repb_fizzle":
        from archaeon.campaign5.repb.evaluate_b import evaluate_b
        from archaeon.campaign5.repb.grammar_b import descend_b
        return (lambda m, eps, rs: evaluate_b(m, eps, rng_seed=rs, reward_mode="per_ask", mode="FIZZLE"), lambda p, s, mate=None: descend_b(p, s, mate=mate),
                lambda m, eps: evaluate_b(m, eps, rng_seed=0, mode="FIZZLE")["_answers"])
    raise ValueError("unknown organism profile %r (the graph profile registers here when Proteus hands it over)" % profile)


def pressure_at(schedule, g: int) -> dict:
    """The active pressure segment at generation g (list form, Phase 0) or the Axis P record's active segment."""
    segs = schedule["segments"] if isinstance(schedule, dict) else schedule
    active = None
    for seg in segs:
        if seg["from_gen"] <= g and (seg.get("to_gen") is None or g < seg["to_gen"]):
            active = seg
    return active or {"kind": "EXOGENOUS_PRESSURE", "label": "stable", "from_gen": 0, "params": {}}


# ---------------------------------------------------------------- spec / checkpoint
def make_spec(*, run_id: str, provenance: dict, world: dict, profile: str, schedule: List[dict], g0: int, g1: int, N: int, E: int,
              archive: dict, thresholds: dict, spread: dict, seed: int, probe_worlds: Optional[List[dict]] = None, planted: Optional[List[dict]] = None,
              log_scores: bool = False, freeze_policy: str = "c6_all_full", admitted: Optional[List[str]] = None) -> dict:
    """freeze_policy: 'c6_all_full' (Campaign 6 G6-0: every firing gets the full package) or 'tiered' (Deep Frontier s9 until
    Harmonia's policy: EVENT_RECORD always; PARTIAL when only 10/11 or unvalidated rulers fire; FULL on an admitted detector,
    corroboration by two rulers, persistence >= 3 archived generations, or the audit draw 1 in 50). `admitted` lists the
    detector names Harmonia has admitted (default: transfer, disagreement, classifier_failure per the packet, until she rules)."""
    assert provenance["lane"] in LANES
    spec = {"schema": SCHEMA_SPEC, "run_id": run_id, "provenance": provenance, "world": world, "profile": profile, "schedule": schedule,
            "g0": g0, "g1": g1, "N": N, "E": E, "archive": archive, "thresholds": thresholds, "spread": spread, "seed": seed,
            "probe_worlds": probe_worlds or [], "planted": planted or [], "anchor_interval": ANCHOR_INTERVAL, "log_scores": log_scores,
            "freeze_policy": freeze_policy, "admitted": admitted or ["unexpected_transfer", "detector_disagreement", "classifier_failure"]}
    spec["spec_hash"] = _h({k: v for k, v in spec.items() if k != "spec_hash"})
    return spec


def initial_checkpoint(spec: dict, init_manifests: List[dict]) -> dict:
    pop = []
    for m in init_manifests:
        org = SUB.organism_record_for(dict(m), None, 0); org["origins"] = ["start"]; pop.append(org)
    rng = SplitMix64(seed_from("c6.segment", spec["run_id"], spec["seed"]))
    ck = {"schema": SCHEMA_CKPT, "run_id": spec["run_id"], "generation": spec["g0"], "eval_ordinal": 0, "rng_state": rng.state,
          "population": pop, "records": {}, "lineage_pairs": {}, "library": [], "prev_anchor_hash": None, "history": {}}
    ck["digest"] = _h({k: v for k, v in ck.items() if k != "digest"})
    return ck


def archived(g: int, archive: dict, firings: set) -> bool:
    """Archive policy: every generation to `dense_until`, then powers of two, plus +-`neighbourhood` around a firing."""
    if g <= archive.get("dense_until", 64):
        return True
    if g & (g - 1) == 0:
        return True
    nb = archive.get("neighbourhood", 16)
    return any(abs(g - f) <= nb for f in firings)


# ---------------------------------------------------------------- the loop
def run_segment(spec: dict, ck: dict) -> dict:
    t_start = time.time()
    world = resolve_world(spec["world"]); eval_fn, descend_fn, answers_fn = resolve_profile(spec["profile"])
    regime = REGIMES["E0"]
    rng = SplitMix64(0); rng.state = ck["rng_state"]
    pop: List[dict] = [dict(o) for o in ck["population"]]
    records: Dict[str, dict] = dict(ck["records"])
    pairs_prev: Dict[str, Any] = dict(ck["lineage_pairs"])            # organism_id -> (t0, ext) of the previous generation (parents)
    history: Dict[str, dict] = dict(ck["history"])                     # organism_id -> {manifest, pair, parent_id, generation} for freezes (bounded)
    library: List[Any] = list(ck["library"])
    eval_ord = ck["eval_ordinal"]
    N, E = spec["N"], spec["E"]
    rows: List[dict] = []; anchors: List[dict] = []; observations: List[dict] = []; events: List[dict] = []; freezes: List[dict] = []
    pressure_history: List[dict] = []; firings: set = set(); lineage_delta: List[dict] = []
    prev_anchor = ck["prev_anchor_hash"]; seg_rows: List[dict] = []; score_log: List[dict] = []
    thresholds, spread = spec["thresholds"], spec["spread"]
    planted = {p["generation"]: p for p in spec.get("planted", [])}
    persist_count: Dict[str, int] = dict(ck.get("persist_count", {}))

    def anchor(reason: str):
        nonlocal prev_anchor, seg_rows
        if not seg_rows:
            return
        a = {"schema": "sfe.t0_anchor.v1", "segment_hash": _h(seg_rows), "n": len(seg_rows), "first_lt": seg_rows[0]["t0"]["lt"], "last_lt": seg_rows[-1]["t0"]["lt"],
             "first_eval": seg_rows[0]["t0"]["eval"], "last_eval": seg_rows[-1]["t0"]["eval"], "sidecar_ref": "run/%s/t0/%d" % (spec["run_id"], len(anchors)),
             "row_schema": "proteus.behavior_fingerprint.v1+archaeon.c6.world_ext.v1", "row_bytes_max": 1024, "producer": "archaeon.segment", "prev_segment_hash": prev_anchor, "reason": reason}
        anchors.append(a); prev_anchor = a["segment_hash"]; seg_rows = []

    for g in range(spec["g0"], spec["g1"]):
        pr = pressure_at(spec["schedule"], g)
        if not pressure_history or pressure_history[-1]["label"] != pr["label"]:
            pressure_history.append({"generation": g, "kind": pr["kind"], "label": pr["label"], "params": pr.get("params", {})})
        # planted event (Phase 0 fixtures of my own; the blind ones are Harmonia's and arrive as ordinary population members)
        planted_now: set = set()
        if g in planted and planted[g]["kind"] == "inject_child_of":
            pid_ = planted[g]["parent_id"]
            org = SUB.organism_record_for(json.loads(json.dumps(planted[g]["manifest"])), pid_, g); org["origins"] = ["planted_child"]
            records[org["organism_id"]] = {"organism_id": org["organism_id"], "parent_ids": [pid_], "generation": g, "operators": [{"operator": planted[g].get("operator", "planted_edit")}]}
            pop[planted[g].get("index", 0)] = org; planted_now.add(org["organism_id"])
        if g in planted and planted[g]["kind"] == "inject_foreign":
            victim = pop[planted[g].get("index", 0)]
            org = SUB.organism_record_for(json.loads(json.dumps(planted[g]["manifest"])), victim["lineage_id"], g); org["origins"] = ["planted_foreign"]
            records[org["organism_id"]] = {"organism_id": org["organism_id"], "parent_ids": [victim["organism_id"]], "generation": g, "operators": [{"operator": "planted_foreign"}]}
            pop[planted[g].get("index", 0)] = org; planted_now.add(org["organism_id"])
        if g in planted and planted[g]["kind"] == "inject_randomized":
            prng = SplitMix64(seed_from("c6.plant", spec["run_id"], g)); victim = pop[planted[g].get("index", 0)]
            m = json.loads(json.dumps(victim["manifest"])); m["genome"] = [prng.next_u32() for _ in m["genome"]]
            org = SUB.organism_record_for(m, victim["lineage_id"], g); org["origins"] = list(victim.get("origins", [])) + ["planted"]
            records[org["organism_id"]] = {"organism_id": org["organism_id"], "parent_ids": [victim["organism_id"]], "generation": g, "operators": [{"operator": "planted_randomize"}]}
            pop[planted[g].get("index", 0)] = org; planted_now.add(org["organism_id"])
        composed = isinstance(world, ComposedWorld)
        reward_scale = 1.0; exo_events: List[dict] = []
        if composed:
            if isinstance(spec["schedule"], dict):
                params_g, exo_events = P.apply(spec["schedule"], spec["world"]["params"], g)
                reward_scale = params_g.pop("reward_scale", 1.0); params_g.pop("redistribution_seed", None); params_g.pop("migration", None)
            else:
                params_g = spec["world"]["params"]
            world_g = ComposedWorld(params_g)
            shared: Optional[dict] = {} if "coupling" in world_g.features else None
            eps = None; asks = None
        else:
            eps = episodes_for(world, spec["seed"], "train", g * 100003 + spec["seed"], E)
            asks = [e.n_asks() for e in eps]
        for e_ in exo_events:
            pressure_history.append({"generation": g, "kind": e_["kind"], "label": e_["label"], "params": {"target": e_["target"], "before": e_["before"], "after": e_["after"]}})
        rs = seed_from("wse.eval", spec["seed"], g, spec["run_id"])
        scored = []; pairs_now: Dict[str, Any] = {}; subjects: Dict[str, D.Subject] = {}
        endo = {"pool_depletion": 0.0, "signals": 0, "objects_changed": 0}
        for org in pop:
            if composed:
                pools_before = list(shared["pools"]) if (shared is not None and "pools" in shared) else None
                ev = evaluate_world(org["manifest"], world_g, spec["seed"] * 1000003 + g, E, rng_seed=rs, shared=shared)
                a = ev["_answers"]; asks = ev["_asks_per_episode"]
                if pools_before is not None and shared.get("pools"):
                    endo["pool_depletion"] += max(0.0, sum(pools_before) - sum(shared["pools"]))
                endo["signals"] += ev["world"]["signals"]; endo["objects_changed"] += ev["world"]["objects_changed"]
                if reward_scale != 1.0:
                    ev["reward"] = min(1.0, ev["reward"] * reward_scale)
            else:
                ev = eval_fn(org["manifest"], eps, rs); a = answers_fn(org["manifest"], eps)
            pid = records.get(org["organism_id"], {}).get("parent_ids", [None])[0]
            wf = ev["world"]["env_dependencies"] if composed else [world.name]
            t0, ext = SUB.rows_any(org["manifest"], org["organism_id"], pid, eval_ord, g, ev, a, world_features=wf, asks_per_episode=asks)
            if composed:
                ext.update({"action_hist": ev["world"]["action_hist"], "resources_touched": ev["world"]["resources_touched"], "survival": ev["world"]["survival"],
                            "objects_changed": ev["world"]["objects_changed"]})
            eval_ord += 1
            row = {"t0": t0, "ext": ext}; rows.append(row); seg_rows.append(row)
            if len(seg_rows) >= spec["anchor_interval"]:
                anchor("interval")
            f = regime.fitness(ev["reward"], ev["meter"], E)
            scored.append((f, org, ev)); pairs_now[org["organism_id"]] = (t0, ext)
            parent_subject = None
            if pid and pid in history:
                hp = history[pid]; parent_subject = D.Subject(pid, hp["manifest"], hp["pair"], None, hp["generation"])
            subjects[org["organism_id"]] = D.Subject(org["organism_id"], org["manifest"], (t0, ext), parent_subject, g, meta={"reward": ev["reward_per_ask"] if not composed else ev["reward"]})
        scored.sort(key=lambda z: -z[0])
        if composed and shared is not None and (endo["pool_depletion"] > 0 or endo["signals"] or endo["objects_changed"]):
            pressure_history.append({"generation": g, "kind": "ENDOGENOUS_PRESSURE", "label": "population_effect", "params": {k: round(v, 4) if isinstance(v, float) else v for k, v in endo.items()}})
        # ---- executor-side detectors on every child of this generation
        pop_subjects = list(subjects.values())
        ws = {"persistent": composed and ("objects" in world_g.features or "coupling" in world_g.features), "resources": world_g.R if composed else 1,
              "persisted_reads": (lambda s: s.pair[1].get("objects_changed", 0))} if composed else None
        ctx = D.Context(thresholds, spread, library=library, population=pop_subjects, world_state=ws,
                        regime_events=[e_["generation"] for e_ in pressure_history if e_["kind"] == "EXOGENOUS_PRESSURE" and e_["label"] != "stable"],
                        ancestors=lambda s, depth: _ancestors(s, history, records, depth),
                        siblings=lambda s: [x for x in pop_subjects if x.parent is not None and s.parent is not None and x.parent.organism_id == s.parent.organism_id and x is not s],
                        home_reward=lambda s: s.meta.get("reward"))
        gen_fired: List[dict] = []
        event_records: List[dict] = []
        for s in pop_subjects:
            vs = D.run_all(s, ctx)
            if spec.get("log_scores"):
                score_log.append({"generation": g, "organism_id": s.organism_id, "planted_now": s.organism_id in planted_now,
                                  "origins": next((o.get("origins") for o in pop if o["organism_id"] == s.organism_id), None),
                                  **{v["detector"]: (v["outcome"], v["score"]) for v in vs if v["detector"] in ("behavioral_novelty", "lineage_discontinuity", "structural_reuse")}})
            if any(v["outcome"] == "FIRE" for v in vs):
                ev_rec = S.event(spec["run_id"], s.organism_id, g, vs, "T1")
                events.append(ev_rec); gen_fired.append(ev_rec); firings.add(g)
                if spec.get("freeze_policy", "c6_all_full") == "tiered":
                    tier = _tier(ev_rec, spec, s, g, persist_count, rows)
                    ev_rec["tier_decision"] = tier
                    if tier == "FULL":
                        freezes.append(_freeze(ev_rec, s, history, records, pop, world, pressure_history, rows, spec))
                    elif tier == "PARTIAL":
                        fz = _freeze(ev_rec, s, history, records, pop, world, pressure_history, rows, spec)
                        fz = {k: v for k, v in fz.items() if k not in ("siblings", "ancestors")}; fz["scope"] = "PARTIAL_BY_POLICY"; fz["missing"] = fz.get("missing", []) + [{"member": "SIBLINGS+ANCESTORS", "owner": "policy", "reason": "tiered freeze policy: PARTIAL tier", "at": fz["preserved_at"]}]
                        freezes.append(fz)
                    # EVENT_RECORD is the event itself plus the archived neighbourhood rows: always kept
                else:
                    freezes.append(_freeze(ev_rec, s, history, records, pop, world, pressure_history, rows, spec))
        if gen_fired:
            anchor("escalation")
        # ---- observation per archived generation
        if archived(g, spec["archive"], firings) or g == spec["g1"] - 1:
            rewards = sorted(z[2]["reward_per_ask"] for z in scored)
            observations.append({"generation": g, "n_evals": len(scored), "reward_min": rewards[0], "reward_median": rewards[len(rewards) // 2], "reward_max": rewards[-1],
                                 "fingerprint_set_digest": _h(sorted(p[0]["digest"] for p in pairs_now.values())), "population_digest": _h(sorted(o["organism_id"] for o in pop)),
                                 "detectors_fired": [e["fired"] for e in gen_fired], "elite": scored[0][1]["organism_id"], "pressure": pr["label"]})
        # ---- history (bounded to what freezes need) and library (elite of archived generations)
        for org in pop:
            history[org["organism_id"]] = {"manifest": org["manifest"], "pair": pairs_now[org["organism_id"]], "parent_id": records.get(org["organism_id"], {}).get("parent_ids", [None])[0], "generation": g}
        if archived(g, spec["archive"], firings):
            library.append(pairs_now[scored[0][1]["organism_id"]])
        # ---- reproduce after EVERY evaluated generation (the checkpoint carries the next, unevaluated population;
        #      a segment boundary must not skip it -- the self-test's continuity check caught exactly that)
        if True:
            new_pop = [z[1] for z in scored[:4]]
            while len(new_pop) < N:
                parent = _tournament(scored, rng, 4); mate = _tournament(scored, rng, 4)
                child, rec = descend_fn(parent, rng.next_u64() & MASK62, mate=mate if mate is not parent else None)
                origins = list(parent.get("origins", ["gen0"]))
                if mate is not parent:
                    for t in mate.get("origins", ["gen0"]):
                        if t not in origins:
                            origins.append(t)
                child["origins"] = origins
                if child["organism_id"] != parent["organism_id"] and child["organism_id"] not in records:
                    records[child["organism_id"]] = rec; lineage_delta.append({"child": child["organism_id"], "parent_ids": rec["parent_ids"], "generation": g + 1, "operators": [o["operator"] for o in rec["operators"]]})
                new_pop.append(child)
            pop = new_pop
        pairs_prev = pairs_now
    anchor("segment_close")
    # prune history to the last ANCESTOR_DEPTH+2 generations' worth of ids reachable from the population (bounded checkpoint)
    keep = set()
    for org in pop:
        oid = org["organism_id"]
        for _ in range(ANCESTOR_DEPTH + 2):
            if oid in history:
                keep.add(oid); oid = history[oid]["parent_id"]
            if not oid:
                break
    history = {k: v for k, v in history.items() if k in keep}
    ck_out = {"schema": SCHEMA_CKPT, "run_id": spec["run_id"], "generation": spec["g1"], "eval_ordinal": eval_ord, "rng_state": rng.state, "population": pop,
              "records": {k: v for k, v in records.items() if k in keep or k in {o["organism_id"] for o in pop}}, "lineage_pairs": {k: pairs_prev[k] for k in pairs_prev},
              "library": library[-256:], "prev_anchor_hash": prev_anchor, "history": history, "persist_count": {k: v for k, v in persist_count.items() if k in keep or v >= 2}}
    ck_out["digest"] = _h({k: v for k, v in ck_out.items() if k != "digest"})
    out = {"schema": "archaeon.c6.segment_out.v1", "spec_hash": spec["spec_hash"], "checkpoint_in": ck["digest"], "checkpoint_out": ck_out, "rows": rows, "anchors": anchors,
           "observations": observations, "events": events, "freezes": freezes, "pressure_history": pressure_history, "lineage_delta": lineage_delta,
           "evaluations": eval_ord - ck["eval_ordinal"], "wall_s": round(time.time() - t_start, 1), "score_log": score_log}
    out["out_digest"] = _h({k: v for k, v in out.items() if k not in ("wall_s", "out_digest", "score_log")})
    return out


def _tier(ev_rec: dict, spec: dict, s: D.Subject, g: int, persist_count: Dict[str, int], rows: List[dict]) -> str:
    """Deep Frontier s9 tiers. Persistence is counted per lineage (parent chain) across generations; the audit draw is seeded."""
    fired = set(ev_rec["fired"]); admitted = set(spec.get("admitted", []))
    core = fired - {"detector_disagreement", "classifier_failure"}
    key = s.parent.organism_id if s.parent else s.organism_id
    persist_count[key] = persist_count.get(key, 0) + 1
    draw = SplitMix64(seed_from("c6.audit_draw", spec["run_id"], g, s.organism_id)).randbelow(50) == 0
    if (core & admitted) or len(core) >= 2 or persist_count[key] >= 3 or draw:
        return "FULL"
    if core or fired:
        return "PARTIAL"
    return "EVENT_RECORD"


def _ancestors(s: D.Subject, history: dict, records: dict, depth: int) -> List[D.Subject]:
    out = []; oid = s.parent.organism_id if s.parent else None
    while oid and oid in history and len(out) < depth:
        h = history[oid]; out.append(D.Subject(oid, h["manifest"], h["pair"], None, h["generation"])); oid = h["parent_id"]
    return out


def _freeze(ev_rec: dict, s: D.Subject, history: dict, records: dict, pop: List[dict], world: WorldSpec, pressure_history: List[dict], rows: List[dict], spec: dict) -> dict:
    """Escalation steps 1-9 as one record, BEFORE any interpretation: subject, parent, ancestors, siblings, world, pressure window, mutation chain, T1 window, replay packet.
    Missing members make the freeze PARTIAL_FREEZE with (member, owner, reason, timestamp) -- never silent (R2)."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    missing = []
    parent = s.parent
    if parent is None:
        pid = records.get(s.organism_id, {}).get("parent_ids", [None])[0]
        missing.append({"member": "PARENT", "owner": "archaeon.segment", "reason": "parent not in checkpoint history (%s)" % (pid[:12] if pid else "no parent id"), "at": ts})
    ancestors = _ancestors(s, history, records, ANCESTOR_DEPTH)
    if len(ancestors) < ANCESTOR_DEPTH and parent is not None:
        missing.append({"member": "ANCESTOR", "owner": "archaeon.segment", "reason": "only %d of %d ancestors within the checkpoint horizon" % (len(ancestors), ANCESTOR_DEPTH), "at": ts})
    sibs = [o for o in pop if records.get(o["organism_id"], {}).get("parent_ids", [None])[0] == (parent.organism_id if parent else None) and o["organism_id"] != s.organism_id] if parent else []
    chain = []; oid = s.organism_id
    for _ in range(ANCESTOR_DEPTH + 1):
        r = records.get(oid)
        if not r:
            break
        chain.append({"child": oid, "parent_ids": r["parent_ids"], "operators": [o.get("operator") for o in r.get("operators", [])]}); oid = r["parent_ids"][0] if r["parent_ids"] else None
        if not oid:
            break
    lineage_ids = {s.organism_id} | {a.organism_id for a in ancestors} | ({parent.organism_id} if parent else set())
    t1 = [r for r in rows if r["t0"]["organism_id"] in lineage_ids][-64:]
    scope = "COMPLETE" if not missing else "PARTIAL_FREEZE"
    fz = {"schema": "sfe.freeze.v1", "event_id": ev_rec["event_id"], "detector_ids": ev_rec["fired"], "scope": scope, "missing": missing,
          "subject": {"organism_id": s.organism_id, "manifest": s.manifest, "generation": s.generation},
          "parent": {"organism_id": parent.organism_id, "manifest": parent.manifest} if parent else None,
          "ancestors": [{"organism_id": a.organism_id, "manifest": a.manifest, "generation": a.generation} for a in ancestors],
          "siblings": [{"organism_id": o["organism_id"], "manifest": o["manifest"]} for o in sibs][:16],
          "world": {"kind": spec["world"]["kind"], "knobs": world.knobs(), "world_id": world.world_id(), "seed": spec["seed"],
                    "complexity_bin": world.complexity_bin() if hasattr(world, "complexity_bin") else 0},
          "pressure_window": pressure_history[-4:], "mutation_chain": chain, "t1_window_n": len(t1), "t1_window_digest": _h(t1),
          "replay_packet": {"spec_hash": spec["spec_hash"], "generation": s.generation, "run_id": spec["run_id"], "changed": {}},
          "preserved_at": ts, "interpretation": None}
    fz["freeze_digest"] = _h({k: v for k, v in fz.items() if k not in ("freeze_digest",)})
    return fz


# ---------------------------------------------------------------- self-test
def self_test(procs: int = 1) -> int:
    from archaeon.campaign6.observatory.fingerprint import spread_from
    frozen = json.load(open(__file__.replace("segment.py", "observatory/DETECTORS_FROZEN_candidate.json"), encoding="utf-8"))
    thr = {k: v["threshold"] for k, v in frozen["thresholds"].items() if v.get("threshold") is not None}
    thr.update({"lineage_discontinuity.struct_max": 0.25, "unexplained_gain.struct_max": 0.25, "unexpected_transfer.floor": 3 / 16, "structural_reuse": 2})
    parents = C1.parents_from_population()
    init = [p["parent"] for p in parents[:16]]
    prov = S.provenance("PROCEDURAL", "segment.self_test", "0.1", 1, {"world": "W0"})
    world = {"kind": "wse.WorldSpec", "knobs": C1.ENVS["W0"].knobs()}
    base = dict(run_id=prov["run_id"], provenance=prov, world=world, profile="v0", schedule=[{"from_gen": 0, "kind": "EXOGENOUS_PRESSURE", "label": "stable", "params": {}}],
                N=16, E=8, archive={"dense_until": 8, "neighbourhood": 4}, thresholds=thr, spread=frozen["spread"], seed=1)
    spec20 = make_spec(g0=0, g1=20, **base); ck0 = initial_checkpoint(spec20, init)
    a = run_segment(spec20, ck0); b = run_segment(spec20, ck0)
    det = a["out_digest"] == b["out_digest"]
    # continuity: [0,10) + [10,20) == [0,20) on population digest and eval count
    s1 = make_spec(g0=0, g1=10, **base); s2 = make_spec(g0=10, g1=20, **base)
    o1 = run_segment(s1, initial_checkpoint(s1, init)); o2 = run_segment(s2, o1["checkpoint_out"])
    cont = (_h(sorted(o["organism_id"] for o in o2["checkpoint_out"]["population"])) == _h(sorted(o["organism_id"] for o in a["checkpoint_out"]["population"]))
            and o1["evaluations"] + o2["evaluations"] == a["evaluations"] and o2["checkpoint_out"]["rng_state"] == a["checkpoint_out"]["rng_state"])
    # anchors cover every evaluation, chain intact
    cov = sum(x["n"] for x in a["anchors"]) == a["evaluations"] and all(a["anchors"][i]["prev_segment_hash"] == a["anchors"][i - 1]["segment_hash"] for i in range(1, len(a["anchors"])))
    # planted event travels: inject at gen 5 -> a firing -> a freeze with the subject; a PARTIAL_FREEZE appears when ancestry is short
    specp = make_spec(g0=0, g1=12, planted=[{"generation": 5, "kind": "inject_randomized", "index": 0}], **base)
    p = run_segment(specp, initial_checkpoint(specp, init))
    planted_hits = [e for e in p["events"] if e["organism_id"] in {fz["subject"]["organism_id"] for fz in p["freezes"]} and "planted" in str(next((r for r in p["lineage_delta"] if r["child"] == e["organism_id"]), {})) or e["generation"] == 5]
    fired_gens = sorted({e["generation"] for e in p["events"]})
    scopes = {fz["scope"] for fz in p["freezes"]}
    no_reward_in_rows = all("reward" not in json.dumps(r).lower() for r in a["rows"][:50])
    rep = {"deterministic": det, "continuity": cont, "anchors_cover_all_evals": cov, "anchors": len(a["anchors"]), "evaluations": a["evaluations"], "events_plain_run": len(a["events"]),
           "events_planted_run": len(p["events"]), "planted_gen5_fired": 5 in fired_gens, "fired_gens": fired_gens[:10], "freeze_scopes": sorted(scopes),
           "observations": len(a["observations"]), "no_reward_in_rows": no_reward_in_rows, "interpretation_all_none": all(fz["interpretation"] is None for fz in p["freezes"]),
           "wall_s": a["wall_s"]}
    print(json.dumps(rep, indent=1))
    return 0 if (det and cont and cov and rep["planted_gen5_fired"] and no_reward_in_rows and rep["interpretation_all_none"]) else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
