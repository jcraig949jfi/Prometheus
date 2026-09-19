"""Admission (directive s19): a machine-checkable predicate over an IMPLEMENTATION. No approver.

admit_world(kind, registry, ...) -> AdmissionResult
    1 conformance   the object satisfies the World Protocol and the episode loop runs (reset/observe/step shapes)
    2 replay        two runs from equal seeds give equal trace hashes (BIT) -- or the component declares SEMANTIC
                    with a tolerance and agrees within it (Phase 1: BIT only; SEMANTIC recorded INDETERMINATE)
    3 reference     if the row names a reference of the same family and both exist: trace agreement on the probe seeds
                    (a component IS its family's reference when reference_of is set: agreement is with itself, trivially)
    4 controls      the cheat arm changes the trace (the measurement channel sees the mechanics); a world that
                    ignores _cheat_skip_dynamics is not necessarily wrong, but then it must not claim ext.cost.v1
                    dynamics -- recorded, not failed, unless the row declares the cheat mechanism
    5 performance   steps/s on this host at a small batch, dated, with python version (a receipt, never a gate)
    6 provenance    row has provenance.author, license, route; native_deps listed (may be empty)
    7 capabilities  every declared capability is well formed; declared ext.* that the object cannot demonstrate
                    (events(), snapshot()) are failures
    8 registry      the row exists

Outcome: ADMITTED (all checks pass) or UNAVAILABLE (any check fails); the registry row's state is updated
in-process and the result is returned as data for the caller to write as a receipt. A failed admission
never affects any other component.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from prometheus.toolbox import capabilities as C
from prometheus.toolbox.contracts import World, ActionSpace


@dataclass
class AdmissionResult:
    kind: str
    state: str                       # ADMITTED | UNAVAILABLE
    checks: Dict[str, dict] = field(default_factory=dict)
    failed: List[str] = field(default_factory=list)
    when_utc: str = ""

    def as_dict(self) -> dict:
        return {"kind": self.kind, "state": self.state, "checks": self.checks, "failed": self.failed, "when_utc": self.when_utc}


def _episode(world, seed: int, horizon: int, actions_fn) -> str:
    world.reset(seed)
    done = False; t = 0
    while not done and t < horizon:
        acts = {pid: actions_fn(pid, world.observe(pid), world.legal_actions(pid)) for pid in range(world.n_players)}
        done = world.step(acts)
        if "ext.events.v1" in world.capabilities:
            world.events()
        t += 1
    return world.trace_hash()


def _accepts(factory, params: dict) -> bool:
    """Does the factory construct with these params? (The world's own refusal is the only source of truth.)"""
    try:
        factory(**params); return True
    except Exception:
        return False


def _det_actions(pid: int, obs: List[int], legal: ActionSpace) -> List[int]:
    return [(sum(obs) + pid + i) % legal.range for i in range(legal.width)]


def admit_world(kind: str, registry, params: dict | None = None, seeds=(1, 2, 3), horizon: int = 32) -> AdmissionResult:
    params = dict(params or {})
    res = AdmissionResult(kind, "UNAVAILABLE", when_utc=datetime.now(timezone.utc).isoformat())
    checks = res.checks
    # 8 registry
    if not registry.has(kind):
        res.failed.append("registry"); checks["registry"] = {"ok": False}; return res
    row = registry.get(kind)
    if row.state == "UNAVAILABLE" and str(row.admission.get("failed", "")).startswith("import"):     # C92b: same rule as every other slot
        checks["registry"] = {"ok": False, "note": "absent machinery", "reason": row.admission.get("failed")}
        res.failed.append("registry"); return res                                  # the row keeps its import reason for the next asker
    checks["registry"] = {"ok": True}
    # 6 provenance
    prov_ok = bool(row.provenance.get("author")) and row.license != "UNSPECIFIED" and row.route in ("write", "wrap", "bind", "chop")
    checks["provenance"] = {"ok": prov_ok, "author": row.provenance.get("author"), "license": row.license, "route": row.route, "native_deps": list(row.native_deps)}
    if not prov_ok:
        res.failed.append("provenance")
    # 7 capabilities well formed
    bad = [c for c in row.capabilities if not C.well_formed(c)]
    checks["capabilities"] = {"ok": not bad, "malformed": bad, "declared": sorted(row.capabilities)}
    if bad:
        res.failed.append("capabilities")
    # 1 conformance
    try:
        w = row.factory(**params)
        conf = isinstance(w, World) and isinstance(w.legal_actions(0) if hasattr(w, "legal_actions") else None, ActionSpace) or False
        if not conf:
            w.reset(seeds[0]); conf = isinstance(w.legal_actions(0), ActionSpace)
        h = _episode(w, seeds[0], horizon, _det_actions)
        conf = conf and isinstance(h, str) and len(h) >= 16
        checks["conformance"] = {"ok": bool(conf), "protocol": isinstance(w, World)}
        if not conf:
            res.failed.append("conformance")
    except Exception as exc:                                    # noqa: BLE001
        checks["conformance"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}
        res.failed.append("conformance"); return res
    # 7b declared extensions must be demonstrable
    ext_fail = []
    if "ext.events.v1" in row.capabilities:
        w.reset(seeds[0]); w.step({pid: [1] * w.legal_actions(pid).width for pid in range(w.n_players)})
        ev = w.events()
        if not isinstance(ev, list) or (ev and (len(ev[0]) != 5 or not all(isinstance(x, int) for x in ev[0]))):
            ext_fail.append("ext.events.v1")
    if "ext.snapshot.v1" in row.capabilities:
        w.reset(seeds[0]); snap = w.snapshot(); w.step({pid: [1] * w.legal_actions(pid).width for pid in range(w.n_players)})
        w.restore(snap); o1 = w.observe(0); w.reset(seeds[0]); o2 = w.observe(0)
        if not isinstance(snap, (bytes, bytearray)) or o1 != o2:
            ext_fail.append("ext.snapshot.v1")
    checks["extensions"] = {"ok": not ext_fail, "undemonstrable": ext_fail}
    if ext_fail:
        res.failed.append("extensions")
    # 2 replay
    rc = getattr(w, "replay_class", "NONDETERMINISTIC")
    if rc in ("BIT", "SEMANTIC"):
        w1 = row.factory(**params); w2 = row.factory(**params)
        eq = all(_episode(w1, s, horizon, _det_actions) == _episode(w2, s, horizon, _det_actions) for s in seeds)
        checks["replay"] = {"ok": eq, "class": rc, "seeds": list(seeds), "quantum": w.manifest().get("quantum") if rc == "SEMANTIC" else None}
        if rc == "SEMANTIC" and w.manifest().get("quantum") is None:
            eq = False; checks["replay"]["note"] = "SEMANTIC without a declared quantum"
        if not eq:
            res.failed.append("replay")
    else:
        checks["replay"] = {"ok": True, "class": rc, "note": "non-BIT replay is recorded, not checked, in Phase 1"}
    # 3 reference agreement
    if row.reference_of:
        checks["reference"] = {"ok": True, "is_reference": True, "family": row.reference_of}
    else:
        fam = row.implements or kind.rsplit(".", 1)[0]          # C70: a row names the family it implements; the kind string is only a fallback
        refs = [r for r in registry.rows("world") if r.get("reference_of") == fam]
        if refs:
            # C70b: the probe must have POWER -- on at least one probe world the reference's trace must depend on the
            # actions, or agreement proves nothing (found: world_seed 0 overwrote every action target within the tick,
            # so a wrong action multiplier agreed with the reference on every seed)
            variants = [dict(params)] + [dict(params, world_seed=ws) for ws in (11, 23, 47) if _accepts(row.factory, dict(params, world_seed=ws))]
            zero = lambda pid, obs, legal: [0] * legal.width
            power = any(_episode(registry.make(refs[0]["kind"], **v), s, horizon, _det_actions) != _episode(registry.make(refs[0]["kind"], **v), s, horizon, zero)
                        for v in variants for s in seeds)
            agree = all(_episode(registry.make(refs[0]["kind"], **v), s, horizon, _det_actions) == _episode(row.factory(**v), s, horizon, _det_actions)
                        for v in variants for s in seeds)
            checks["reference"] = {"ok": agree and power, "reference": refs[0]["kind"], "probe_variants": len(variants), "probe_has_power": power}
            if not power:
                checks["reference"]["note"] = "the reference is action-blind on every probe: agreement is not evidence"
            if not (agree and power):
                res.failed.append("reference")
        else:
            checks["reference"] = {"ok": True, "note": "no reference registered for family %s; this component stands alone" % fam}
    # 4 controls: the cheat mechanism, if the world accepts it, must change the trace
    try:
        wc = row.factory(**dict(params, _cheat_skip_dynamics=True))
        h_c = _episode(wc, seeds[0], horizon, _det_actions); h_p = _episode(row.factory(**params), seeds[0], horizon, _det_actions)
        checks["controls"] = {"ok": h_c != h_p, "cheat": "world_params._cheat_skip_dynamics", "trace_changed": h_c != h_p}
        if h_c == h_p:
            res.failed.append("controls")
    except (TypeError, ValueError):
        checks["controls"] = {"ok": True, "cheat": None, "note": "world has no kernel cheat parameter; a control generator must ship with it before it is used in an experiment with control.cheat.v1"}
    # 5 performance receipt
    w = row.factory(**params); t0 = time.perf_counter(); ticks = 0
    for s in seeds:
        w.reset(s); done = False
        while not done and ticks < 5000:
            done = w.step({pid: _det_actions(pid, w.observe(pid), w.legal_actions(pid)) for pid in range(w.n_players)}); ticks += 1
            if "ext.events.v1" in w.capabilities:
                w.events()
    dt = time.perf_counter() - t0
    import sys
    checks["performance"] = {"ok": True, "ticks": ticks, "wall_s": round(dt, 6), "steps_per_s": round(ticks / dt, 1) if dt > 0 else None, "python": sys.version.split()[0]}
    res.state = "ADMITTED" if not res.failed else "UNAVAILABLE"
    row.state = res.state; row.admission = res.as_dict()
    return res


# ================================================================================================ all slots (C28)
def _common(kind: str, registry) -> "AdmissionResult":
    res = AdmissionResult(kind, "UNAVAILABLE", when_utc=datetime.now(timezone.utc).isoformat())
    if not registry.has(kind):
        res.failed.append("registry"); res.checks["registry"] = {"ok": False}; return res
    row = registry.get(kind)
    if row.state == "UNAVAILABLE" and str(row.admission.get("failed", "")).startswith("import"):
        res.checks["registry"] = {"ok": False, "note": "absent machinery", "reason": row.admission.get("failed")}
        res.failed.append("registry"); return res
    res.checks["registry"] = {"ok": True}
    prov_ok = bool(row.provenance.get("author")) and row.license != "UNSPECIFIED" and row.route in ("write", "wrap", "bind", "chop")
    res.checks["provenance"] = {"ok": prov_ok, "author": row.provenance.get("author"), "license": row.license, "route": row.route}
    if not prov_ok:
        res.failed.append("provenance")
    bad = [c for c in row.capabilities if not C.well_formed(c)]
    res.checks["capabilities"] = {"ok": not bad, "malformed": bad, "declared": sorted(row.capabilities)}
    if bad:
        res.failed.append("capabilities")
    return res


def _finish(res: "AdmissionResult", registry) -> "AdmissionResult":
    res.state = "ADMITTED" if not res.failed else "UNAVAILABLE"
    if registry.has(res.kind):
        row = registry.get(res.kind); row.state = res.state; row.admission = res.as_dict()
    return res


def _serialisable(obj) -> bool:
    import json
    try:
        json.dumps(obj); return True
    except (TypeError, ValueError):
        return False


def _det_spec(i: int):
    from prometheus.toolbox.ref.players import random_statemachine
    return random_statemachine(100 + i)


def _synthetic_run(registry, observers: list, seed: int = 3, horizon: int = 12, n_players: int = 2) -> dict:
    from prometheus.toolbox.backends.local import run_episode
    w = registry.make("world.integer.v1", world_seed=5, n_players=n_players, start_charge=20)
    sub = registry.make("substrate.flat.v1")
    inst = {i: sub.instantiate(_det_spec(i), i) for i in range(n_players)}
    return run_episode(w, inst, observers, seed, horizon)


def admit_observer(kind: str, registry) -> "AdmissionResult":
    res = _common(kind, registry)
    if res.failed:
        return _finish(res, registry)
    row = registry.get(kind)
    try:
        from prometheus.toolbox.contracts import Observer
        obs = [row.factory(), row.factory()]
        conf = all(isinstance(o, Observer) for o in obs)
        _synthetic_run(registry, [obs[0]]); _synthetic_run(registry, [obs[1]])
        m0, m1 = obs[0].measure(), obs[1].measure()
        res.checks["conformance"] = {"ok": conf}
        if not conf:
            res.failed.append("conformance")
        ser = _serialisable(m0) and _serialisable(obs[0].describe()) and _serialisable(obs[0].manifest())
        res.checks["serialisable"] = {"ok": ser}
        if not ser:
            res.failed.append("serialisable")
        det = ser and m0 == m1 and obs[0].describe() == obs[1].describe()
        res.checks["determinism"] = {"ok": det, "note": "two identical synthetic runs must measure identically"}
        if not det:
            res.failed.append("determinism")
        if getattr(obs[0], "series", False):
            se = obs[0].series_episode()
            ok = isinstance(se, list) and all(isinstance(r, list) and all(isinstance(x, int) for x in r) for r in se)
            res.checks["series"] = {"ok": ok, "records": len(se)}
            if not ok:
                res.failed.append("series")
    except Exception as exc:                                    # noqa: BLE001
        res.checks["conformance"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}; res.failed.append("conformance")
    return _finish(res, registry)


def admit_substrate(kind: str, registry) -> "AdmissionResult":
    res = _common(kind, registry)
    if res.failed:
        return _finish(res, registry)
    row = registry.get(kind)
    try:
        from prometheus.toolbox.contracts import Substrate, PlayerInstance, ActionSpace, PlayerSpec
        from prometheus.toolbox.ref import players as P
        sub = row.factory()
        res.checks["conformance"] = {"ok": isinstance(sub, Substrate)}
        if not isinstance(sub, Substrate):
            res.failed.append("conformance")
        makers = {"statemachine.v1": lambda: P.random_statemachine(7), "statemachine.v2": lambda: P.random_statemachine_v2(7), "statemachine.v3": lambda: P.random_statemachine_v3(7), "constant.v1": lambda: P.constant_player([1, 2]),
                  "rewrite.v1": lambda: P.random_rewrite_system(7), "proteus.tape.v0": (lambda: P.random_proteus_player(17)) if P.proteus_available() else None}
        bad_reps = []
        for rep in sorted(sub.representations):
            mk = makers.get(rep)
            if mk is None:
                bad_reps.append(rep); continue                  # claims a representation nobody can make: not demonstrable
            inst = sub.instantiate(mk(), 1)
            a = inst.act([1, 2, 3, 4, 5], ActionSpace(2, 8)); snap = inst.snapshot(); inst.restore(snap)
            if not (isinstance(inst, PlayerInstance) and len(a) == 2 and _serialisable(inst.cost())):
                bad_reps.append(rep)
        res.checks["representations"] = {"ok": not bad_reps, "undemonstrable": bad_reps, "declared": sorted(sub.representations)}
        if bad_reps:
            res.failed.append("representations")
        try:
            sub.instantiate(PlayerSpec("statemachine.v1", P.random_statemachine(1).payload, {}, frozenset({"ext.nobody.grants.v1"})), 0)
            res.checks["refuses_unmet_requires"] = {"ok": False}; res.failed.append("refuses_unmet_requires")
        except Exception:
            res.checks["refuses_unmet_requires"] = {"ok": True}
        acc = sub.accounting()
        res.checks["accounting"] = {"ok": isinstance(acc, dict) and all(isinstance(v, int) for v in acc.values()), "keys": sorted(acc)}
        if not res.checks["accounting"]["ok"]:
            res.failed.append("accounting")
    except Exception as exc:                                    # noqa: BLE001
        res.checks["conformance"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}; res.failed.append("conformance")
    return _finish(res, registry)


def admit_control(kind: str, registry) -> "AdmissionResult":
    res = _common(kind, registry)
    if res.failed:
        return _finish(res, registry)
    row = registry.get(kind)
    try:
        from prometheus.toolbox.contracts import Control
        from prometheus.toolbox.ir import Experiment, ref
        ctrl = row.factory()
        res.checks["conformance"] = {"ok": isinstance(ctrl, Control)}
        if not isinstance(ctrl, Control):
            res.failed.append("conformance")
        e = Experiment(family="admit", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[_det_spec(0).manifest()],
                       budget={"episodes": 1, "horizon": 4})
        arm = ctrl.arm(e, 1)
        ok = isinstance(arm, Experiment) and arm.validate() == [] and _serialisable(arm.to_dict())
        res.checks["arm"] = {"ok": ok, "defects": arm.validate() if isinstance(arm, Experiment) else "not an Experiment"}
        if not ok:
            res.failed.append("arm")
        fake = {"status": "COMPLETED", "trace_hashes": ["a"], "series": {}, "science": {"observations": {}, "objective": {"value": 0}}, "accounting": {"params": 1}, "provenance": {}, "replay_class": "BIT"}
        out = ctrl.expectation(fake, dict(fake))
        ok2 = isinstance(out, dict) and out.get("outcome") in ("MET", "NOT_MET", "INDETERMINATE") and _serialisable(out)
        res.checks["expectation"] = {"ok": ok2, "outcome": out.get("outcome") if isinstance(out, dict) else None}
        if not ok2:
            res.failed.append("expectation")
    except Exception as exc:                                    # noqa: BLE001
        res.checks["conformance"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}; res.failed.append("conformance")
    return _finish(res, registry)


def admit_simple(kind: str, registry) -> "AdmissionResult":
    """representation / objective / transform / selector: constructible, manifest serialisable, slot-specific smoke."""
    res = _common(kind, registry)
    if res.failed:
        return _finish(res, registry)
    row = registry.get(kind)
    try:
        if row.slot == "representation":
            spec = row.factory(3) if kind != "constant.v1" else row.factory([1, 2])
            ok = _serialisable(spec.manifest()) and spec.representation == kind
            res.checks["spec"] = {"ok": ok}
            if not ok:
                res.failed.append("spec")
        elif row.slot == "objective":
            obj = row.factory(); out = obj.evaluate({"science": {"observations": {}}, "accounting": {}, "series": {}})
            ok = isinstance(out, dict) and "value" in out and "components" in out and _serialisable(out) and _serialisable(obj.manifest())
            res.checks["evaluate"] = {"ok": ok}
            if not ok:
                res.failed.append("evaluate")
        elif row.slot == "transform":
            t = row.factory(); ok = isinstance(t.accepts, frozenset) and _serialisable(t.manifest())
            if "player.statemachine.v1" in t.accepts:
                out = t.apply(_det_spec(0), 9); ok = ok and out.representation == "statemachine.v1" and _serialisable(out.manifest())
            res.checks["apply"] = {"ok": ok}
            if not ok:
                res.failed.append("apply")
        elif row.slot == "selector":
            sel = row.factory(); props = sel.propose([], 1, 3)
            ok = len(props) == 3 and all(_serialisable(p.manifest()) for p in props) and _serialisable(sel.manifest())
            res.checks["propose"] = {"ok": ok}
            if not ok:
                res.failed.append("propose")
        else:
            res.checks["slot"] = {"ok": True, "note": "no behavioural check for slot %s yet" % row.slot}
    except Exception as exc:                                    # noqa: BLE001
        res.checks["conformance"] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}; res.failed.append("conformance")
    return _finish(res, registry)


def admit(kind: str, registry) -> "AdmissionResult":
    if not registry.has(kind):
        return _finish(_common(kind, registry), registry)
    slot = registry.get(kind).slot
    if slot == "world":
        return admit_world(kind, registry)
    if slot == "observer":
        return admit_observer(kind, registry)
    if slot == "substrate":
        return admit_substrate(kind, registry)
    if slot == "control":
        return admit_control(kind, registry)
    return admit_simple(kind, registry)


def admit_all(registry) -> Dict[str, "AdmissionResult"]:
    return {row["kind"]: admit(row["kind"], registry) for row in registry.rows()}
