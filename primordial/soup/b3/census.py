"""B3 op census: which primitive ops do B1 and B2 actually execute? Rows, not the list.

Part 1 (B1): trace wforge Encounter.step at BYTECODE level (sys.settrace with opcode
events) and tally every executed BINARY_OP by operator, COMPARE_OP, and subscript
store/load, per world. The action tensor and seeds match the B1 oracle.

Part 2 (B2): the same opcode census on the plain-Python GraphWorld reference, plus a
timing wrapper around every python-graphblas entry point used by run_gb and around
the numpy conversions, grouped as kernel / conversion / construction.

usage: python -m primordial.soup.b3.census --worlds 60 --specs 20 --out-dir primordial/ledger/rows/B
"""
from __future__ import annotations

import argparse
import dis
import json
import pathlib
import sys
import time
from collections import Counter

NB_OPS = {i: name for i, (name, _sym) in enumerate(dis._nb_ops)} if hasattr(dis, "_nb_ops") else {}


class OpTracer:
    """Counts executed opcodes inside functions whose code object is in `codes`."""

    def __init__(self, codes):
        self.codes = set(codes)
        self.ops = Counter()

    def _local(self, frame, event, arg):
        if event == "opcode":
            code = frame.f_code.co_code
            i = frame.f_lasti
            op = code[i]
            name = dis.opname[op]
            if name == "BINARY_OP":
                self.ops["BINARY_OP:" + NB_OPS.get(code[i + 1], str(code[i + 1]))] += 1
            elif name in ("COMPARE_OP", "CONTAINS_OP", "IS_OP", "UNARY_NOT", "UNARY_NEGATIVE", "UNARY_INVERT",
                          "BINARY_SUBSCR", "STORE_SUBSCR", "CALL", "FOR_ITER", "POP_JUMP_IF_FALSE",
                          "POP_JUMP_IF_TRUE", "BUILD_LIST", "LIST_APPEND"):
                self.ops[name] += 1
        return self._local

    def _global(self, frame, event, arg):
        if event == "call" and frame.f_code in self.codes:
            frame.f_trace_opcodes = True
            return self._local
        return None

    def __enter__(self):
        sys.settrace(self._global)
        return self

    def __exit__(self, *exc):
        sys.settrace(None)


def _untraced_helper(x: int) -> int:
    """Outside the traced scope: its ops must NOT be counted (scope cheat)."""
    for _ in range(50):
        x = x * 3 % 97
    return x


def _calib_target(n: int) -> int:
    """Executes exactly n multiplies and n additions of its own, then calls an untraced helper."""
    acc = 1
    for i in range(n):
        acc = acc * 5
        acc = acc + i
    return _untraced_helper(acc)


def calibration() -> list[dict]:
    """Positive control: the tracer counts a known op budget exactly. Scope cheat: ops in a
    helper outside the traced code set are invisible (would inflate the census if not).

    ORDER MATTERS: n=1000 runs FIRST, in the fresh process, before any warm-up. A first
    run with n=0 hid a cold-start under-count (observed 2026-09-14: the first traced world
    lost ~23% of its opcode events in-process; the repeat was complete)."""
    rows = []
    for n in (1000, 0, 1, 7, 1000):
        tr = OpTracer([_calib_target.__code__])
        with tr:
            _calib_target(n)
        mul = tr.ops.get("BINARY_OP:NB_MULTIPLY", 0)
        add = tr.ops.get("BINARY_OP:NB_ADD", 0)
        rem = tr.ops.get("BINARY_OP:NB_REMAINDER", 0)
        rows.append({"part": "calibration", "order": len(rows), "n": n, "expected_mul": n, "counted_mul": mul,
                     "expected_add": n, "counted_add": add, "helper_mod_counted": rem,
                     "exact": mul == n and add == n, "scope_leak": rem > 0})
    # scope cheat run: tracing BOTH codes must see the helper's 50 multiplies and 50 mods
    tr = OpTracer([_calib_target.__code__, _untraced_helper.__code__])
    with tr:
        _calib_target(7)
    rows.append({"part": "calibration_cheat", "n": 7, "traced_helper_too": True,
                 "counted_mul": tr.ops.get("BINARY_OP:NB_MULTIPLY", 0), "expected_mul": 7 + 50,
                 "counted_mod": tr.ops.get("BINARY_OP:NB_REMAINDER", 0), "expected_mod": 50})
    return rows


def census_b1(worlds: int) -> list[dict]:
    from primordial.soup.b1.common import Encounter, action_tensor, episode_seeds, make_world
    from wforge.world import XS64
    # step itself plus the xorshift stream it calls (stoch kicks); observe() is not a tick op
    codes = [Encounter.step.__code__, XS64.next.__code__, XS64.below.__code__]
    rows = []
    for g in range(worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(4, base=7000 + g)
        acts = action_tensor(mech, 4, seed=g)
        tr = OpTracer(codes)
        ticks = 0
        for e in range(4):
            enc = Encounter(mech, wid, int(seeds[e]))
            done, t = False, 0
            with tr:
                while not done:
                    done = enc.step([[int(x) for x in acts[t, e, s]] for s in range(mech.n_slots)])
                    t += 1
            ticks += t
        rows.append({"part": "B1", "world_seed": g, "ticks": ticks, "n_regs": mech.n_regs,
                     "lin_ops": len(mech.lin_ops), "stoch": mech.stoch_rate, "delay": mech.delay,
                     "n_slots": mech.n_slots, "ops": dict(tr.ops)})
    return rows


def census_b2_ref(specs: int) -> list[dict]:
    from primordial.soup.b2.graphworld import run_ref, step_cell
    from primordial.soup.b2.oracle import specs as mk
    codes = [run_ref.__code__, step_cell.__code__]
    rows = []
    for j, s in enumerate(mk(specs)):
        tr = OpTracer(codes)
        with tr:
            run_ref(s)
        rows.append({"part": "B2ref", "spec": j, "entities": s.n, "ticks": s.ticks, "ops": dict(tr.ops)})
    return rows


# python-graphblas is lazy: mxm / mxv / ewise_* / reduce_* only BUILD an expression; the
# SuiteSparse kernel runs when the expression is materialised (.new) or assigned (<<).
# So: "kernel" = expression .new + container dup(mask) + << assignment; "build" = the
# expression constructors; "convert" = to_coo / from_coo (the numpy <-> GraphBLAS boundary).
BUILD = ("mxm", "mxv", "ewise_add", "ewise_mult", "reduce_rowwise")


def _owner(cls, name):
    for c in cls.__mro__:
        if name in c.__dict__:
            return c
    return None


def census_b2_gb(L_list) -> list[dict]:
    import graphblas.core.matrix as cm
    import graphblas.core.vector as cv
    from graphblas import Matrix, Vector
    from primordial.soup.b2.graphworld import Spec, run_gb

    wall = Counter()
    calls = Counter()
    originals = []            # (owner class, attr name, original __dict__ entry)
    seen = set()
    depth = [0]               # only the OUTERMOST wrapped call is timed: no double counting

    def make_timed(fn, key):
        def timed(*a, **k):
            if depth[0]:
                return fn(*a, **k)
            depth[0] += 1
            t0 = time.perf_counter()
            try:
                return fn(*a, **k)
            finally:
                depth[0] -= 1
                wall[key] += time.perf_counter() - t0
                calls[key] += 1
        return timed

    def wrap(cls, name, group):
        owner = _owner(cls, name)
        if owner is None or (owner, name) in seen:
            return
        seen.add((owner, name))
        raw = owner.__dict__[name]
        key = f"{group}:{name}"
        if isinstance(raw, classmethod):
            new = classmethod(make_timed(raw.__func__, key))
        elif isinstance(raw, staticmethod):
            new = staticmethod(make_timed(raw.__func__, key))
        else:
            new = make_timed(raw, key)
        originals.append((owner, name, raw))
        setattr(owner, name, new)

    # the per-tick trajectory line (sorted "id,cell" string over every live entity + sha256)
    # is paid by EVERY form including ref; time it as its own group
    import primordial.soup.b2.graphworld as gw
    orig_line = gw._line
    gw._line = make_timed(orig_line, "trace:_line")
    originals.append((gw, "_line", orig_line))

    expr_classes = [getattr(m, n) for m in (cm, cv) for n in dir(m)
                    if n.endswith("Expression") and isinstance(getattr(m, n), type)]
    for ec in expr_classes:
        wrap(ec, "new", "kernel")
    for cls in (Matrix, Vector):
        wrap(cls, "dup", "kernel")
        wrap(cls, "__lshift__", "kernel")
        for nm in BUILD:
            wrap(cls, nm, "build")
        wrap(cls, "to_coo", "convert")
        wrap(cls, "from_coo", "convert")

    rows = []
    try:
        for L in L_list:
            e = max(8, (L * L) // 8)
            s = Spec(L=L, n_pred=e // 8, n_prey=3 * e // 8, n_food=e // 2, ticks=16, seed=L)
            wall.clear()
            calls.clear()
            t0 = time.perf_counter()
            run_gb(s)
            total = time.perf_counter() - t0
            groups = Counter()
            for k, v in wall.items():
                groups[k.split(":")[0]] += v
            rows.append({"part": "B2gb", "L": L, "entities": s.n, "ticks": s.ticks, "wall_total_s": total,
                         "wall_by_group_s": dict(groups),
                         "wall_share": {g: v / total for g, v in groups.items()},
                         "unaccounted_share": 1 - sum(groups.values()) / total,
                         "calls": dict(calls), "wall_by_call_s": dict(wall)})
    finally:
        for owner, name, orig in originals:
            if orig is None:
                try:
                    delattr(owner, name)
                except AttributeError:
                    pass
            else:
                setattr(owner, name, orig)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=60)
    ap.add_argument("--specs", type=int, default=20)
    ap.add_argument("--L", default="16,32,64,128,256")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out_dir)
    cal = calibration()
    print("calibration:", json.dumps(cal))
    with open(out / "B3-census-calibration.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in cal:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    # warm-up (discarded) so the counted pass is not the cold first pass, then an
    # in-process repeatability control: the census over the same worlds twice must agree
    census_b1(2)
    b1 = census_b1(a.worlds)
    b1_again = census_b1(a.worlds)
    rep = [{"part": "repeatability", "world_seed": x["world_seed"], "equal": x["ops"] == y["ops"],
            "ops_total_first": sum(x["ops"].values()), "ops_total_second": sum(y["ops"].values())}
           for x, y in zip(b1, b1_again)]
    with open(out / "B3-census-repeatability.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in rep:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print("repeatability: worlds equal", sum(r["equal"] for r in rep), "/", len(rep))
    b2r = census_b2_ref(a.specs)
    b2g = census_b2_gb([int(x) for x in a.L.split(",")])
    for name, rows in (("B3-census-b1.jsonl", b1), ("B3-census-b2ref.jsonl", b2r), ("B3-census-b2gb.jsonl", b2g)):
        with open(out / name, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
    tot = Counter()
    for r in b1:
        tot.update(r["ops"])
    arith = {k: v for k, v in tot.items() if k.startswith("BINARY_OP:")}
    s_ar = sum(arith.values())
    print("B1 executed arithmetic ops:", json.dumps(dict(sorted(arith.items(), key=lambda kv: -kv[1]))))
    print("B1 distinct arithmetic operators:", len(arith), " total:", s_ar)
    for r in b2g:
        print(f"B2gb L={r['L']} n={r['entities']} shares:",
              {k: round(v, 3) for k, v in r["wall_share"].items()}, "unaccounted", round(r["unaccounted_share"], 3))


if __name__ == "__main__":
    main()
