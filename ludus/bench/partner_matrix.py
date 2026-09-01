"""Cycle 004 — the partner matrix E_ijk, and an exact variance decomposition of it.

Preregistration: `roles/Ludus/CYCLE_004_PREREG_basis_audit.md`, written first.
Fossil of the failure that prompted it: `ludus/fossils/FOSSIL_r0003_2026-08-27.json`.

    E_ijk = EV(axis A uses circuit r_i, axis B uses partner r_j, in world W_k)
            / EV(exact optimal play in W_k)

The question is not whether any circuit scores well. It is what a circuit's score
is a property OF. If `E_ijk` decomposes into a stable per-circuit term, the flat
rXXXX catalog is the right representation. If the circuit x partner interaction
dominates the circuit main effect, the useful object is the PAIR and the catalog
is the wrong shape.

Because every world is solved exactly, `E_ijk` has no measurement error and the
decomposition below is arithmetic over a complete factorial, not a fit. There is
no residual standing in for noise: whatever lands in the three-way term is real
higher-order structure.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import statistics
import time
from datetime import datetime, timezone

from ludus.bench.circuits import (REGISTRY, SELECT_CIRCUITS, STOP_CIRCUITS,
                                  optimal_select, optimal_stop)
from ludus.bench.compiled import compile_world, evaluate, solve

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"


# ==========================================================================
# The design
# ==========================================================================

def factorial_worlds():
    """A complete 2x2x2x2 FOUNDRY factorial, plus the real worlds with both axes.

    The FOUNDRY block is the diagnostic instrument: gate and decoy move
    independently while the STOP structure -- pot dynamics, death probability,
    horizon -- is bit-for-bit identical across all sixteen. If a STOP circuit's
    measured value moves across that block, its value was never a property of the
    STOP interface alone.
    """
    from ludus.bench.worlds2 import Foundry
    out = []
    for gate in (0, 1):
        for decoy in (0, 1):
            for k in (2, 3):
                for cap in (2, 4):
                    out.append(Foundry(gate=gate, decoy=bool(decoy),
                                       arity=k, capacity=cap))
    return out


def real_worlds():
    from ludus.bench.worlds import BATCH1
    from ludus.bench.worlds2 import Coloretto, LuckyNumbers
    keep = {"MARTIAN_DICE", "CANT_STOP"}
    return [w for w in BATCH1 if w.name in keep] + [LuckyNumbers(), Coloretto()]


# ==========================================================================
# Measurement
# ==========================================================================

def cell_values(world, include_optimal=True) -> dict:
    """Every admissible (stop circuit, select circuit) pairing in one world."""
    cw = compile_world(world)
    ev_star, V, W = solve(cw)
    if ev_star <= 0:
        return {"world": world.name, "degenerate": "optimal EV is zero"}
    live = any(len(o) > 1 for rows in cw.trans.values() for _, o in rows)
    stops = list(STOP_CIRCUITS)
    sels = list(SELECT_CIRCUITS)
    if include_optimal:
        stops = stops + [optimal_stop(V, W)]
        sels = sels + [optimal_select(V, W)]
    cells = {}
    for si in stops:
        for sj in sels:
            cells[f"{si.rid}|{sj.rid}"] = round(evaluate(cw, sj, si) / ev_star, 6)
    return {"world": world.name, "optimal_ev": round(ev_star, 6),
            "n_states": cw.n_states, "select_axis_live": live, "cells": cells}


# ==========================================================================
# Exact variance decomposition over a complete factorial
# ==========================================================================

def decompose(E: dict, circuits, partners, worlds) -> dict:
    """Classical ANOVA sums of squares. Complete design required; exact."""
    vals = [E[(i, j, k)] for i in circuits for j in partners for k in worlds]
    n = len(vals)
    g = sum(vals) / n

    def mean(sel):
        xs = [E[key] for key in E if sel(key)]
        return sum(xs) / len(xs)

    a = {i: mean(lambda key, i=i: key[0] == i) - g for i in circuits}
    b = {j: mean(lambda key, j=j: key[1] == j) - g for j in partners}
    c = {k: mean(lambda key, k=k: key[2] == k) - g for k in worlds}
    ab = {(i, j): mean(lambda key, i=i, j=j: key[0] == i and key[1] == j)
          - a[i] - b[j] - g for i in circuits for j in partners}
    ac = {(i, k): mean(lambda key, i=i, k=k: key[0] == i and key[2] == k)
          - a[i] - c[k] - g for i in circuits for k in worlds}
    bc = {(j, k): mean(lambda key, j=j, k=k: key[1] == j and key[2] == k)
          - b[j] - c[k] - g for j in partners for k in worlds}

    ss = {"circuit": len(partners) * len(worlds) * sum(v * v for v in a.values()),
          "partner": len(circuits) * len(worlds) * sum(v * v for v in b.values()),
          "world": len(circuits) * len(partners) * sum(v * v for v in c.values()),
          "circuit x partner": len(worlds) * sum(v * v for v in ab.values()),
          "circuit x world": len(partners) * sum(v * v for v in ac.values()),
          "partner x world": len(circuits) * sum(v * v for v in bc.values())}
    total = sum((v - g) ** 2 for v in vals)
    ss["circuit x partner x world"] = max(0.0, total - sum(ss.values()))

    share = {k: (v / total if total > 1e-15 else 0.0) for k, v in ss.items()}
    own = (ss["circuit"] + ss["circuit x partner"] + ss["circuit x world"]
           + ss["circuit x partner x world"])
    s_circuit = ss["circuit"] / own if own > 1e-15 else 0.0
    return {"grand_mean": round(g, 6), "total_ss": round(total, 6),
            "variance_share": {k: round(v, 4) for k, v in share.items()},
            "S_circuit": round(s_circuit, 4),
            "S_circuit_meaning": "share of a circuit's OWN variance that is "
                                 "marginal rather than conditional on partner/world",
            "main_effects_circuit": {i: round(v, 4) for i, v in a.items()},
            "main_effects_partner": {j: round(v, 4) for j, v in b.items()}}


def kendall_tau(x, y) -> float:
    n = len(x)
    if n < 2:
        return 1.0
    conc = disc = 0
    for p, q in itertools.combinations(range(n), 2):
        s = (x[p] - x[q]) * (y[p] - y[q])
        if s > 0:
            conc += 1
        elif s < 0:
            disc += 1
    tot = conc + disc
    return (conc - disc) / tot if tot else 1.0


def rank_stability(E, circuits, partners, worlds) -> dict:
    """Does the circuit ORDERING survive a change of partner?

    A stable marginal effect implies a stable ranking. Ranking is the property a
    practitioner would actually rely on -- 'use r_i rather than r_i2' -- so it is
    reported beside the variance share rather than derived from it.
    """
    taus = []
    per_world = {}
    for k in worlds:
        tk = []
        for j1, j2 in itertools.combinations(partners, 2):
            v1 = [E[(i, j1, k)] for i in circuits]
            v2 = [E[(i, j2, k)] for i in circuits]
            tk.append(kendall_tau(v1, v2))
        if tk:
            per_world[k] = round(sum(tk) / len(tk), 4)
            taus.extend(tk)
    return {"mean_tau_across_partner_pairs": round(sum(taus) / len(taus), 4) if taus else None,
            "per_world": per_world,
            "min_world": min(per_world, key=per_world.get) if per_world else None}


def leave_one_out(E, circuits, partners, worlds) -> dict:
    """Leave-one-partner-out and leave-one-world-out prospective checks.

    Characterise each circuit by its mean effect over all but one partner (or
    world), then predict the held-out cell. The error is what the representation
    could NOT predict somewhere it was not constructed. A circuit only
    interpretable after seeing every partner has no prospective value.
    """
    def loo(dim):
        errs = []
        held = partners if dim == "partner" else worlds
        for h in held:
            rest = [x for x in held if x != h]
            for i in circuits:
                if dim == "partner":
                    train = [E[(i, j, k)] for j in rest for k in worlds]
                    test = [E[(i, h, k)] for k in worlds]
                else:
                    train = [E[(i, j, k)] for j in partners for k in rest]
                    test = [E[(i, j, h)] for j in partners]
                pred = sum(train) / len(train)
                errs.extend(abs(pred - t) for t in test)
        return {"mean_abs_error": round(sum(errs) / len(errs), 4),
                "max_abs_error": round(max(errs), 4),
                "n": len(errs)}
    return {"leave_one_partner_out": loo("partner"),
            "leave_one_world_out": loo("world")}


def invariance(E, circuits, partners, wmeta) -> dict:
    """Which world properties can change without moving a circuit's value?

    This is the cycle's positive target. FOUNDRY supplies the irrelevance by
    construction: worlds identical except in one named property. A circuit with
    an empty invariance set has no earned scope statement, whatever its mean.
    """
    out = {}
    for i in circuits:
        rec = {}
        for prop in ("gate", "decoy", "arity", "capacity"):
            deltas = []
            for j in partners:
                groups = {}
                for k, meta in wmeta.items():
                    if (i, j, k) not in E:
                        continue
                    key = tuple(v for p, v in meta.items() if p != prop)
                    groups.setdefault(key, []).append(E[(i, j, k)])
                for vals in groups.values():
                    if len(vals) > 1:
                        deltas.append(max(vals) - min(vals))
            if deltas:
                rec[prop] = {"max_abs_delta": round(max(deltas), 4),
                             "invariant": bool(max(deltas) < 0.01)}
        out[i] = rec
    return out


def identifiability(E, circuits, partners, worlds) -> dict:
    """Do two behaviourally DISTINCT circuits produce identical signatures?

    If so, the measurements cannot separate the mechanisms they are claimed to
    represent, and every claim resting on them is unidentified regardless of how
    good the numbers look.
    """
    sigs = {i: tuple(round(E[(i, j, k)], 6) for j in partners for k in worlds)
            for i in circuits}
    collisions = []
    for i1, i2 in itertools.combinations(circuits, 2):
        if sigs[i1] == sigs[i2]:
            collisions.append([i1, i2])
    return {"identical_signature_pairs": collisions,
            "n_distinct_signatures": len(set(sigs.values())),
            "n_circuits": len(circuits),
            "identified": len(collisions) == 0}


# ==========================================================================

def main() -> None:
    t0 = time.time()
    ATLAS.mkdir(parents=True, exist_ok=True)
    fw = factorial_worlds()
    rw = real_worlds()
    wmeta = {w.name: {"gate": int(w.gate), "decoy": int(w.decoy),
                      "arity": w.arity, "capacity": w.capacity} for w in fw}

    out = {"artifact": "cycle 004 partner matrix E_ijk",
           "prereg": "roles/Ludus/CYCLE_004_PREREG_basis_audit.md",
           "fossil": "ludus/fossils/FOSSIL_r0003_2026-08-27.json",
           "no_model_calls": True, "exact": True,
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "worlds": {}}
    path = ATLAS / "cycle004_partner_matrix.json"

    for w in fw + rw:
        r = cell_values(w)
        out["worlds"][w.name] = r
        path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"  {w.name:46s} cells={len(r.get('cells', {})):3d} "
              f"({time.time()-t0:6.1f}s)", flush=True)

    # Analysis over the FOUNDRY factorial only: it is the sole COMPLETE design,
    # and a decomposition over an incomplete one would silently attribute
    # missing cells to interaction.
    fnames = [w.name for w in fw]
    circuits = [f.rid for f in STOP_CIRCUITS]
    partners = [f.rid for f in SELECT_CIRCUITS]
    E = {}
    ok = True
    for i in circuits:
        for j in partners:
            for k in fnames:
                c = out["worlds"][k].get("cells", {})
                if f"{i}|{j}" not in c:
                    ok = False
                else:
                    E[(i, j, k)] = c[f"{i}|{j}"]
    out["design_complete"] = ok
    if ok:
        out["decomposition_STOP_axis"] = decompose(E, circuits, partners, fnames)
        out["rank_stability"] = rank_stability(E, circuits, partners, fnames)
        out["leave_one_out"] = leave_one_out(E, circuits, partners, fnames)
        out["invariance"] = invariance(E, circuits, partners, wmeta)
        out["identifiability"] = identifiability(E, circuits, partners, fnames)
    out["wall_seconds"] = round(time.time() - t0, 1)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    import threading
    for _mb in (256, 128, 64, 32):
        try:
            threading.stack_size(_mb * 1024 * 1024)
            break
        except Exception:
            continue
    th = threading.Thread(target=main)
    th.start()
    th.join()
