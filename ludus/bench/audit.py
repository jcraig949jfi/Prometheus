"""Circuit audits: reskin invariance, collisions, negative transfer.

Three checks a circuit must survive before it means anything, all mechanical.

1. RESKIN INVARIANCE. Rename the entities, scramble the presentation order,
   preserve the mechanics exactly, and re-measure. A circuit whose retention
   moves was reading the surface, not the structure. The bench's architecture
   *claims* immunity here — circuits see only a compiled table, never a game —
   but a claim of immunity is not a measurement of it, and there is one channel
   the architecture does not close: **argmax tie-breaking**. `max(opts, key=...)`
   returns the first element among equals, so option ENUMERATION ORDER leaks into
   every circuit that ever faces a tie. AMA's fingerprint audit found the same
   defect from the other direction, where resolving ties to the first step
   smuggled a positional prior into a text measurement.

2. COLLISIONS. If two circuits make near-identical decisions in every world, the
   bench is carrying two names for one thing and its "two independent circuits
   both survived" is one circuit counted twice. The fix is not to delete one; it
   is to go looking for a world that separates them, and to say so out loud until
   one is found.

3. NEGATIVE TRANSFER. A circuit that helps in world A and *hurts* in world B is
   structure, not noise. It says the two worlds differ along an axis the circuit
   is sensitive to, which is a lead. Retention is therefore recorded against the
   null circuit as a SIGNED quantity, and sign flips across worlds are surfaced
   rather than averaged away.
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
from datetime import datetime, timezone

from ludus.bench.circuits import (REGISTRY, SELECT_CIRCUITS, STOP_CIRCUITS,
                                  optimal_select, optimal_stop, select_null,
                                  stop_myopic)
from ludus.bench.compiled import Compiled, compile_world, evaluate, solve

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ==========================================================================
# 1. Adversarial reskin
# ==========================================================================

def reskin(cw: Compiled, seed: int = 20260826) -> Compiled:
    """Mechanics-preserving, surface-destroying transformation.

    Every state is renamed to an opaque integer, and the option lists within each
    draw are shuffled. Nothing about the probability structure, the pots, or the
    reachability graph changes. Any circuit reading structure is unaffected by
    construction; any circuit reading presentation moves.
    """
    rng = random.Random(seed)
    names = list(cw.pot)
    rng.shuffle(names)
    rename = {s: i for i, s in enumerate(names)}
    out = Compiled(cw.name + "@reskin", cw.genre, "RESKINNED: entities renamed, "
                   "option order scrambled, mechanics preserved",
                   cw.interfaces, rename[cw.initial])
    out.pot = {rename[s]: v for s, v in cw.pot.items()}
    out.forced = {rename[s]: v for s, v in cw.forced.items()}
    for s, rows in cw.trans.items():
        new_rows = []
        for p, opts in rows:
            o = [rename[x] for x in opts]
            rng.shuffle(o)
            new_rows.append((p, tuple(o)))
        rng.shuffle(new_rows)
        out.trans[rename[s]] = tuple(new_rows)
    out.cons = {(rename[a], rename[b]): v for (a, b), v in cw.cons.items()}
    out.n_states = cw.n_states
    return out


def reskin_audit(cw: Compiled, seeds=(1, 2, 3)) -> dict:
    """Measure every circuit on the world and on reskins of it."""
    ev0, V0, W0 = solve(cw)
    base_sel = optimal_select(V0, W0)
    rows = {}

    for fn in STOP_CIRCUITS:
        native = evaluate(cw, base_sel, fn) / ev0 if ev0 else 0.0
        drifts = []
        for sd in seeds:
            rk = reskin(cw, seed=sd)
            evr, Vr, Wr = solve(rk)
            r = evaluate(rk, optimal_select(Vr, Wr), fn) / evr if evr else 0.0
            drifts.append(round(r - native, 6))
        rows[fn.rid] = {"axis": "STOP", "native_retention": round(native, 6),
                        "reskin_drift": drifts,
                        "max_abs_drift": round(max(abs(d) for d in drifts), 6)}

    has_select = any(len(o) > 1 for r in cw.trans.values() for _, o in r)
    if has_select:
        for fn in SELECT_CIRCUITS:
            native = evaluate(cw, fn, stop_myopic) / ev0 if ev0 else 0.0
            drifts = []
            for sd in seeds:
                rk = reskin(cw, seed=sd)
                evr, _, _ = solve(rk)
                r = evaluate(rk, fn, stop_myopic) / evr if evr else 0.0
                drifts.append(round(r - native, 6))
            rows[fn.rid] = {"axis": "SELECT", "native_retention": round(native, 6),
                            "reskin_drift": drifts,
                            "max_abs_drift": round(max(abs(d) for d in drifts), 6)}
    return rows


# ==========================================================================
# 2. Collisions
# ==========================================================================

def visitation(cw, select, stop, cutoff: float = 1e-12) -> dict:
    """Probability mass reaching each decision state under a reference policy."""
    mass = collections.defaultdict(float)
    front = {cw.initial: 1.0}
    while front:
        nxt = collections.defaultdict(float)
        for s, m in front.items():
            if m <= cutoff or cw.forced[s]:
                continue
            mass[s] += m
            if stop(cw, s, select):
                continue
            for p, opts in cw.trans.get(s, ()):
                if not opts:
                    continue
                nxt[select(cw, s, opts)] += m * p
        front = nxt
    return dict(mass)


def collision_audit(cw) -> dict:
    """Pairwise decision agreement, weighted by where competent play actually goes.

    Uniform weighting over reachable states is the wrong measure and the bench
    learned that the expensive way: in cycle 002 it disagreed with the
    visitation-weighted number by a factor of 78.
    """
    ev0, V0, W0 = solve(cw)
    opt_sel = optimal_select(V0, W0)
    mass = visitation(cw, opt_sel, stop_myopic)
    tot = sum(mass.values()) or 1.0
    out = {}

    stops = [f for f in STOP_CIRCUITS if REGISTRY[f.rid]["transferable"]]
    for i, a in enumerate(stops):
        for b in stops[i + 1:]:
            agree = sum(m for s, m in mass.items()
                        if a(cw, s, opt_sel) == b(cw, s, opt_sel))
            out[f"{a.rid}~{b.rid}"] = {"axis": "STOP",
                                       "weighted_agreement": round(agree / tot, 4)}

    has_select = any(len(o) > 1 for r in cw.trans.values() for _, o in r)
    if has_select:
        sels = [f for f in SELECT_CIRCUITS if REGISTRY[f.rid]["transferable"]]
        pts = [(s, m) for s, m in mass.items() if any(len(o) > 1 for _, o in
                                                      cw.trans.get(s, ()))]
        tot2 = sum(m for _, m in pts) or 1.0
        for i, a in enumerate(sels):
            for b in sels[i + 1:]:
                agree = 0.0
                for s, m in pts:
                    same = all(a(cw, s, o) == b(cw, s, o)
                               for _, o in cw.trans.get(s, ()) if len(o) > 1)
                    if same:
                        agree += m
                out[f"{a.rid}~{b.rid}"] = {"axis": "SELECT",
                                           "weighted_agreement": round(agree / tot2, 4)}
    return out


# ==========================================================================
# 3. Negative transfer, signed against the null circuit
# ==========================================================================

def negative_transfer(cw) -> dict:
    ev0, V0, W0 = solve(cw)
    opt_sel = optimal_select(V0, W0)
    out = {}
    has_select = any(len(o) > 1 for r in cw.trans.values() for _, o in r)
    if has_select:
        null_ev = evaluate(cw, select_null, stop_myopic)
        for fn in SELECT_CIRCUITS:
            if fn.rid == "r0013":
                continue
            ev = evaluate(cw, fn, stop_myopic)
            out[fn.rid] = {"axis": "SELECT",
                           "vs_null_circuit": round((ev - null_ev) / ev0, 6),
                           "helps": ev > null_ev}
    # STOP has no null circuit; the floor is the better of the two trivial rules.
    floor = max(evaluate(cw, opt_sel, f) for f in STOP_CIRCUITS
                if not REGISTRY[f.rid]["transferable"])
    for fn in STOP_CIRCUITS:
        if not REGISTRY[fn.rid]["transferable"]:
            continue
        ev = evaluate(cw, opt_sel, fn)
        out[fn.rid] = {"axis": "STOP",
                       "vs_trivial_floor": round((ev - floor) / ev0, 6),
                       "helps": ev > floor}
    return out


# ==========================================================================

def main() -> None:
    from ludus.bench.worlds import ALL_WORLDS
    ATLAS.mkdir(parents=True, exist_ok=True)
    out = {"artifact": "circuit audits", "ts_utc": _now(), "worlds": {}}
    for w in ALL_WORLDS:
        print(f"\n=== {w.name} ===", flush=True)
        try:
            cw = compile_world(w)
            e = {"reskin": reskin_audit(cw), "collisions": collision_audit(cw),
                 "negative_transfer": negative_transfer(cw)}
        except Exception as exc:                       # noqa: BLE001
            e = {"failed": f"{type(exc).__name__}: {exc}"[:300]}
            print(f"  FAILED {type(exc).__name__}: {str(exc)[:140]}")
        out["worlds"][w.name] = e
        (ATLAS / "circuit_audits.json").write_text(json.dumps(out, indent=2),
                                                   encoding="utf-8")
        if "failed" in e:
            continue
        print("  reskin drift (nonzero = the circuit reads presentation):")
        for rid, v in sorted(e["reskin"].items(),
                             key=lambda kv: -kv[1]["max_abs_drift"]):
            flag = "  <-- SURFACE-DEPENDENT" if v["max_abs_drift"] > 1e-9 else ""
            print(f"    {rid:10s} {v['axis']:6s} native={v['native_retention']:.4f} "
                  f"max|drift|={v['max_abs_drift']:.6f}{flag}")
        coll = [(k, v) for k, v in e["collisions"].items()
                if v["weighted_agreement"] >= 0.99]
        if coll:
            print("  COLLISIONS (>=0.99 weighted agreement):")
            for k, v in coll:
                print(f"    {k}  {v['weighted_agreement']:.4f}  -> needs a "
                      f"separating world")
        neg = [(k, v) for k, v in e["negative_transfer"].items() if not v["helps"]]
        if neg:
            print("  NEGATIVE / NO transfer vs the floor:")
            for k, v in neg:
                d = v.get("vs_null_circuit", v.get("vs_trivial_floor"))
                print(f"    {k:10s} {d:+.6f}")
    print(f"\nwrote {ATLAS / 'circuit_audits.json'}")


if __name__ == "__main__":
    main()
