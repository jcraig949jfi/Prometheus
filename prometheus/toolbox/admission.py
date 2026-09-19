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
    if rc == "BIT":
        w1 = row.factory(**params); w2 = row.factory(**params)
        eq = all(_episode(w1, s, horizon, _det_actions) == _episode(w2, s, horizon, _det_actions) for s in seeds)
        checks["replay"] = {"ok": eq, "class": "BIT", "seeds": list(seeds)}
        if not eq:
            res.failed.append("replay")
    else:
        checks["replay"] = {"ok": True, "class": rc, "note": "non-BIT replay is recorded, not checked, in Phase 1"}
    # 3 reference agreement
    if row.reference_of:
        checks["reference"] = {"ok": True, "is_reference": True, "family": row.reference_of}
    else:
        fam = kind.rsplit(".", 1)[0]
        refs = [r for r in registry.rows("world") if r.get("reference_of") == fam]
        if refs:
            wr = registry.make(refs[0]["kind"], **params); wc = row.factory(**params)
            agree = all(_episode(wr, s, horizon, _det_actions) == _episode(wc, s, horizon, _det_actions) for s in seeds)
            checks["reference"] = {"ok": agree, "reference": refs[0]["kind"]}
            if not agree:
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
