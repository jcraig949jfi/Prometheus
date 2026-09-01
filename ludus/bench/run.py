"""Build the circuit x world transfer matrix and write the atlas.

This is the bench's standing product. It grows monotonically: a new world is
scored against every registered circuit, a new circuit against every registered
world, and nothing is ever recomputed by hand. A kill is a cell in this matrix,
not the end of a cycle.

Reported per world:

  * exact optimal EV, and the state count that made it exact;
  * a per-world FITTED pot threshold, swept — the strongest cheap baseline, and
    the thing a transferable circuit has to beat to have shown anything;
  * every circuit's EV retention on its own axis, holding the other axis at
    exact optimal so the axes do not contaminate each other;
  * the AXIS DECOMPOSITION: what share of the gap between cheap play and optimal
    play lives on SELECT versus on STOP. Cycle 002 showed that number can be 86/0
    in a world whose genre label names only the STOP axis.
"""
from __future__ import annotations

import json
import pathlib
import time
from datetime import datetime, timezone

from ludus.bench.circuits import (REGISTRY, SELECT_CIRCUITS, STOP_CIRCUITS,
                                  optimal_select, optimal_stop, select_greedy_pot,
                                  select_one_ply, stop_myopic, stop_never,
                                  stop_threshold)
from ludus.bench.compiled import compile_world, evaluate, solve
from ludus.bench.worlds import ALL_WORLDS

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"


def fit_threshold(cw, opt_sel, optimal_ev):
    """Sweep the pot threshold and keep the best. Fitted per world by design."""
    best = (None, -1.0)
    pots = sorted({round(v, 4) for v in cw.pot.values() if v > 0})
    if not pots:
        return None, 0.0
    # Grid size scales DOWN with the state count. Fitting this baseline costs one
    # full DP pass per grid point, so a fixed 40-point sweep is cheap on Flip 7
    # (4k states) and dominates the entire run on Can't Stop (69k states x 126
    # draws). The baseline only has to be strong, not resolved to four decimals.
    k = 40 if cw.n_states <= 20_000 else (16 if cw.n_states <= 100_000 else 8)
    grid = pots if len(pots) <= k else [pots[i] for i in
                                        range(0, len(pots), max(1, len(pots) // k))]
    grid = grid[:k]
    for T in grid:
        ev = evaluate(cw, opt_sel, stop_threshold(T, f"r0006[T={T}]"))
        if ev > best[1]:
            best = (T, ev)
    return best[0], best[1] / optimal_ev if optimal_ev else 0.0


def run_world(world) -> dict:
    t0 = time.time()
    cw = compile_world(world)
    ev_star, V, W = solve(cw)
    opt_sel, opt_stop = optimal_select(V, W), optimal_stop(V, W)

    has_select = any(len(o) > 1 for rows in cw.trans.values() for _, o in rows)
    entry = {
        "world": world.name, "genre": world.genre, "surface": world.surface,
        "rules_state": world.rules_state,
        "declared_interfaces": list(world.interfaces),
        "select_axis_is_live": has_select,
        "n_states": cw.n_states, "optimal_ev": round(ev_star, 6),
        "compile_and_solve_seconds": round(time.time() - t0, 1),
        "stop_axis": {}, "select_axis": {},
    }

    # STOP axis, measured against a PAIRING ENVELOPE rather than one partner.
    #
    # The earlier version held SELECT at exact optimal, on the reasoning that an
    # optimal partner cannot contaminate the axis under test. That reasoning is
    # wrong and it silently produced a whole column of zeros. An optimal selector
    # maximises LONG-RUN value and will happily take options with no immediate
    # gain; r0003 reads immediate gain, so it banks instantly and scores 0.0000 in
    # a world where the same circuit scores 1.0000 beside a greedy partner
    # (FOUNDRY[gate=1,k=3,cap=4]: 0.0000 vs 1.0000).
    #
    # This is the same mismatch already documented on `optimal_stop` -- a
    # component optimised against a different partner is not a clean control --
    # committed a second time on the opposite axis. So no axis is ever measured
    # against a single partner again: every circuit is scored against several and
    # the envelope is reported, because the SPREAD is itself the finding.
    for fn in STOP_CIRCUITS:
        pairings = {"optimal_select": evaluate(cw, opt_sel, fn),
                    "greedy_select": evaluate(cw, select_greedy_pot, fn),
                    "one_ply_select": evaluate(cw, select_one_ply, fn)}
        best = max(pairings.values())
        entry["stop_axis"][fn.rid] = {
            "ev": round(best, 6), "retention": round(best / ev_star, 4),
            "retention_by_partner": {k: round(v / ev_star, 4)
                                     for k, v in pairings.items()},
            "partner_spread": round((max(pairings.values()) -
                                     min(pairings.values())) / ev_star, 4),
            "transferable": REGISTRY[fn.rid]["transferable"]}
    T, ret = fit_threshold(cw, opt_sel, ev_star)
    entry["stop_axis"]["r0006-fitted"] = {
        "ev": round(ret * ev_star, 6), "retention": round(ret, 4),
        "fitted_T": T, "transferable": False,
        "note": "swept per world; the bar a transferable circuit must clear"}

    # SELECT axis: hold STOP at the transferable circuit r0003, not at optimal.
    # Optimal-stop is optimal GIVEN optimal continuation and is mismatched when
    # bolted onto a cheap select; pairing with r0003 measures the select circuit
    # against a partner it will actually be deployed with.
    if has_select:
        for fn in SELECT_CIRCUITS:
            pairings = {"myopic_stop": evaluate(cw, fn, stop_myopic),
                        "never_stop": evaluate(cw, fn, stop_never),
                        "optimal_stop": evaluate(cw, fn, opt_stop)}
            best = max(pairings.values())
            entry["select_axis"][fn.rid] = {
                "ev": round(best, 6), "retention": round(best / ev_star, 4),
                "retention_by_partner": {k: round(v / ev_star, 4)
                                         for k, v in pairings.items()},
                "partner_spread": round((max(pairings.values()) -
                                         min(pairings.values())) / ev_star, 4),
                "transferable": REGISTRY[fn.rid]["transferable"]}
        ev_opt_sel = evaluate(cw, opt_sel, stop_myopic)
        entry["select_axis"]["OPTIMAL"] = {
            "ev": round(ev_opt_sel, 6), "retention": round(ev_opt_sel / ev_star, 4),
            "transferable": False}

        # Axis decomposition, from the all-cheap corner.
        best_cheap_sel = max((f for f in SELECT_CIRCUITS
                              if REGISTRY[f.rid]["transferable"]),
                             key=lambda f: entry["select_axis"][f.rid]["retention"])
        base = evaluate(cw, best_cheap_sel, stop_myopic)
        up_stop = evaluate(cw, best_cheap_sel, opt_stop)
        up_sel = evaluate(cw, opt_sel, stop_myopic)
        entry["axis_decomposition"] = {
            "cheap_pair": f"{best_cheap_sel.rid}+r0003",
            "cheap_pair_retention": round(base / ev_star, 4),
            "recovered_by_upgrading_SELECT_only": round((up_sel - base) / ev_star, 4),
            "recovered_by_upgrading_STOP_only": round((up_stop - base) / ev_star, 4),
            "total_residual": round((ev_star - base) / ev_star, 4)}
    else:
        entry["axis_decomposition"] = {
            "note": "no SELECT axis: every draw admits at most one option. "
                    "This is a property of the world, recorded, not a gap."}
    entry["wall_seconds"] = round(time.time() - t0, 1)
    return entry


def main() -> None:
    """`python -m ludus.bench.run [WORLD ...]` — omit names to rebuild everything.

    Named worlds are MERGED into the existing matrix rather than replacing it, so
    a single expensive world can be recomputed without discarding the rest.
    """
    import sys
    want = set(a.strip().upper() for a in sys.argv[1:] if a.strip())
    ATLAS.mkdir(parents=True, exist_ok=True)
    p = ATLAS / "transfer_matrix.json"
    out = {"artifact": "LUDUS transfer matrix + atlas",
           "no_model_calls": True,
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "circuits": {k: {"axis": v["axis"], "doc": v["doc"],
                            "transferable": v["transferable"]}
                        for k, v in REGISTRY.items()},
           "worlds": {}}
    if want and p.exists():
        prev = json.loads(p.read_text(encoding="utf-8"))
        out["worlds"] = prev.get("worlds", {})
        out["merged_from"] = prev.get("ts_utc")
    todo = [w for w in ALL_WORLDS if not want or w.name.upper() in want]
    for w in todo:
        print(f"\n=== {w.name} ===", flush=True)
        try:
            e = run_world(w)
        except Exception as exc:                      # noqa: BLE001
            # A world that cannot be solved is a RECORDED FACT about that world,
            # not a reason to lose the whole run. It gets a row like any other.
            out["worlds"][w.name] = {"world": w.name, "genre": w.genre,
                                     "failed": f"{type(exc).__name__}: {exc}"[:300]}
            print(f"  FAILED {type(exc).__name__}: {str(exc)[:160]}", flush=True)
            p.write_text(json.dumps(out, indent=2), encoding="utf-8")
            continue
        out["worlds"][w.name] = e
        p.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"  states={e['n_states']}  optimal_EV={e['optimal_ev']:.4f}  "
              f"({e['wall_seconds']}s)")
        print("  STOP axis (SELECT held at optimal):")
        for rid, v in sorted(e["stop_axis"].items(),
                             key=lambda kv: -kv[1]["retention"]):
            tag = "" if v.get("transferable") else "   [not transferable]"
            print(f"    {rid:16s} retention={v['retention']:.4f}{tag}")
        if e["select_axis"]:
            print("  SELECT axis (STOP held at r0003):")
            for rid, v in sorted(e["select_axis"].items(),
                                 key=lambda kv: -kv[1]["retention"]):
                tag = "" if v.get("transferable") else "   [not transferable]"
                print(f"    {rid:16s} retention={v['retention']:.4f}{tag}")
            d = e["axis_decomposition"]
            print(f"  axis decomposition from {d['cheap_pair']} "
                  f"(retention {d['cheap_pair_retention']:.4f}):")
            print(f"    SELECT upgrade recovers {d['recovered_by_upgrading_SELECT_only']:+.4f}")
            print(f"    STOP   upgrade recovers {d['recovered_by_upgrading_STOP_only']:+.4f}")
            print(f"    total residual          {d['total_residual']:+.4f}")

    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {p}")


def _run_with_big_stack(fn):
    """Run on a thread with a large stack.

    The solver and the policy evaluator recurse over the state graph, and Can't
    Stop's turns are long enough to blow CPython's default C stack. Raising
    `sys.setrecursionlimit` alone does NOT help: it lifts the interpreter's own
    guard while leaving the real stack unchanged, so the process dies with no
    traceback at all. The first build of this matrix died exactly that way and
    lost Can't Stop silently -- and because the run was piped through `tail`,
    the shell reported `tail`'s exit code 0 and the crash looked like success.
    Hence both fixes: a big stack, and an atlas written after every world.
    """
    import threading
    # Windows caps thread stack size; fall back down the ladder until one takes.
    for mb in (256, 128, 64, 32, 16):
        try:
            threading.stack_size(mb * 1024 * 1024)
            break
        except (ValueError, RuntimeError):
            continue
    box = {}
    th = threading.Thread(target=lambda: box.update(r=fn()))
    th.start()
    th.join()
    return box.get("r")


if __name__ == "__main__":
    _run_with_big_stack(main)
