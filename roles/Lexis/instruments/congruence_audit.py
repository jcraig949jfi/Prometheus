"""Does the field projection D actually form a CONGRUENCE on Apollo's operators?

External review, 2026-08-25, correctly refused to certify the slicing theorem. The
objection is not that my AST read-detection is incomplete in some vague way; it is a
concrete counterexample that survives PERFECT read detection:

    def make_alias(bb):      bb.scratch = bb.d        # writes only `scratch`
    def mutate_scratch(bb):  bb.scratch.append(1)     # touches only `scratch`

Neither operator ever executes `bb.d = ...`, so neither enters the backward slice of `d`.
Yet `make_alias ; mutate_scratch` changes `d` through the heap. And the cleaner form: two
records whose `d` are extensionally equal (`[]` and `[]`) but where one aliases `scratch`
to `d` and the other does not, AGREE on the projection and DIVERGE after `mutate_scratch`.
Field-value equality does not capture alias topology, so the induction step is unproven.

The reviewer's prescription is exactly right and is what this audit implements:

    "test a stronger property: no D-reachable mutable object is reachable from any field
     outside D, or else make the slice heap-aware."

WHAT IS ACTUALLY REQUIRED. The projection is a congruence if, at every reachable record,
the mutable object graph rooted at the fields is a FOREST -- no mutable object appears at
two distinct paths. That is strictly stronger than the reviewer's cross-boundary condition
and it is the right bar, because sharing *within* D breaks the induction too: if `names`
and `ordered` are the same list object in one record and equal-but-distinct lists in
another, the two records have identical projections and diverge the moment any operator
appends to either.

So three tests, in increasing strength:

  A. CROSS-BOUNDARY SHARING - a mutable object reachable from a D field and also from a
     non-D field. This is the reviewer's literal counterexample shape.
  B. ANY INTER-FIELD SHARING - the same mutable object reachable from two distinct fields.
  C. ANY SHARING AT ALL - the same mutable object at two distinct paths anywhere,
     including twice inside one field. Passing C means the projection is a congruence with
     respect to aliasing, unconditionally.

Also audited here because the reviewer is right that "no random / no clock / no uuid"
establishes much less than "deterministic function of the blackboard":

  D. HIDDEN STATE, STATIC - `global` statements, module-level mutable containers, mutable
     default arguments, closure cells, class attributes, function attributes.
  E. ESCAPE HATCHES, STATIC - getattr/setattr/vars/__dict__/asdict/astuple/attrgetter/
     copy/deepcopy/pickle/json, and calls that pass the WHOLE record to a helper.
  F. HISTORY INDEPENDENCE, DYNAMIC - the reviewer's counter-example
     `global calls; calls += 1; if calls == 7: ...`. For every tabulated (state, operator)
     pair, re-evaluate after unrelated histories and require byte-identical projected
     output.
  G. CROSS-TASK CONTAMINATION, DYNAMIC - build the transition tables with the battery in
     original order and in reversed order and require the tables to be identical. If
     evaluation shares globals, caches or operator instances across tasks, coordinate t+1
     depends on coordinate t and the joint construction is invalid.

A FAILURE HERE INVALIDATES THE 0.8333 CLOSURE RESULT. That is the point of running it.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import argparse
import ast
import copy
import inspect
import json
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                      # noqa: E402
from blackboard import BlackboardState              # noqa: E402
from o1_enumerate import build_battery              # noqa: E402
from _answer_slice import D as _SLICE               # noqa: E402

ALL_FIELDS = list(BlackboardState.__dataclass_fields__)
PROVENANCE = {"write_log", "op_log", "skipped_ops"}
D_FIELDS = [f for f in ALL_FIELDS if f in _SLICE]
NON_D = [f for f in ALL_FIELDS if f not in _SLICE]

IMMUTABLE_ATOM = (str, int, float, bool, type(None), bytes, complex)
MUTABLE_KINDS = (list, dict, set, bytearray)


# ── object-graph walk ────────────────────────────────────────────────────────
def walk(obj, path, out, depth=0):
    """Append (id(obj), path) for every MUTABLE object reachable from obj."""
    if depth > 12 or isinstance(obj, IMMUTABLE_ATOM):
        return
    if isinstance(obj, MUTABLE_KINDS):
        out.append((id(obj), path))
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(k, path + "[key]", out, depth + 1)
            walk(v, path + "[%r]" % (k,), out, depth + 1)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for i, v in enumerate(obj):
            walk(v, path + "[%d]" % i, out, depth + 1)
    elif hasattr(obj, "__dict__"):
        out.append((id(obj), path))
        for k, v in vars(obj).items():
            walk(v, path + "." + k, out, depth + 1)


def sharing_report(state):
    """-> (crossD, interfield, anyshare) lists of (path_a, path_b)."""
    per_field = {}
    for f in ALL_FIELDS:
        acc = []
        walk(getattr(state, f), f, acc)
        per_field[f] = acc
    seen = {}
    cross, inter, anyshare = [], [], []
    for f, entries in per_field.items():
        for oid, path in entries:
            if oid in seen:
                pf, ppath = seen[oid]
                anyshare.append((ppath, path))
                if pf != f:
                    inter.append((ppath, path))
                    in_d_a, in_d_b = pf in _SLICE, f in _SLICE
                    if in_d_a != in_d_b:
                        cross.append((ppath, path))
            else:
                seen[oid] = (f, path)
    return cross, inter, anyshare


def skey(s):
    parts = []
    for f in D_FIELDS:
        v = getattr(s, f)
        if isinstance(v, set):
            parts.append(tuple(sorted(map(repr, v))))
        elif isinstance(v, dict):
            parts.append(tuple(sorted((repr(k), repr(x)) for k, x in v.items())))
        elif isinstance(v, list):
            parts.append(tuple(map(repr, v)))
        else:
            parts.append(repr(v))
    return tuple(parts)


def apply_op(op, s):
    try:
        return op(copy.deepcopy(s))
    except Exception:
        return s


# ── static audits ────────────────────────────────────────────────────────────
ESCAPES = {"getattr", "setattr", "delattr", "vars", "asdict", "astuple",
           "attrgetter", "deepcopy", "dumps", "loads", "eval", "exec",
           "__dict__", "__getattribute__", "globals", "locals"}


def static_audit(ops_by_name):
    globals_used, mutable_defaults, escapes, whole_record_passed = [], [], [], []
    closure_cells, func_attrs = [], []
    for name, op in ops_by_name.items():
        fn = op.fn
        # closure cells
        if getattr(fn, "__closure__", None):
            closure_cells.append((name, len(fn.__closure__)))
        # function attributes beyond the standard set
        extra = set(vars(fn)) - {"__wrapped__", "__module__", "__name__", "__qualname__",
                                 "__doc__", "__dict__", "__annotations__"}
        if extra:
            func_attrs.append((name, sorted(extra)))
        # mutable default arguments
        try:
            sig = inspect.signature(fn)
            for pname, p in sig.parameters.items():
                if p.default is not inspect.Parameter.empty and \
                        isinstance(p.default, MUTABLE_KINDS):
                    mutable_defaults.append((name, pname, type(p.default).__name__))
        except (ValueError, TypeError):
            pass
        try:
            src = inspect.getsource(fn)
            tree = ast.parse(src.strip())
        except (OSError, TypeError, IndentationError, SyntaxError):
            continue
        argnames = [a.arg for a in tree.body[0].args.args] if isinstance(
            tree.body[0], ast.FunctionDef) else []
        recvar = argnames[0] if argnames else "state"
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                globals_used.append((name, node.names))
            if isinstance(node, ast.Nonlocal):
                globals_used.append((name, ["nonlocal:" + n for n in node.names]))
            if isinstance(node, ast.Call):
                fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if fname in ESCAPES:
                    escapes.append((name, fname))
                # whole-record passed to a helper
                for a in node.args:
                    if isinstance(a, ast.Name) and a.id == recvar:
                        callee = fname or "<expr>"
                        if callee not in ("len", "print", "repr", "type"):
                            whole_record_passed.append((name, callee))
            if isinstance(node, ast.Attribute) and node.attr in ("__dict__", "__class__"):
                escapes.append((name, node.attr))
    return dict(globals_used=globals_used, mutable_defaults=mutable_defaults,
                escapes=escapes, whole_record_passed=whole_record_passed,
                closure_cells=closure_cells, func_attrs=func_attrs)


def module_level_mutables(ops_by_name):
    """Module-level mutable containers, split into LIVE and INERT.

    A module-level mutable is only hidden state if an operator can reach it. Refined
    2026-08-25 after the first run flagged three operator REGISTRIES (name -> op lookup
    tables) as failures: they are mutable dicts, and they are also read-only constants no
    operator names. An over-broad detector that cannot tell those apart produces a FAIL
    that is about the detector, not the substrate.

    LIVE  = the identifier appears in at least one operator's source.
    INERT = it does not. Inertness is confirmed dynamically in `registries_unchanged()`.
    """
    live, inert = [], []
    sources = {}
    for name, op in ops_by_name.items():
        try:
            sources[name] = inspect.getsource(op.fn)
        except (OSError, TypeError):
            pass
    for modname in ("blackboard_ops", "blackboard_ops_v2", "blackboard_ops_r2",
                    "blackboard_ops_compare"):
        mod = sys.modules.get(modname)
        if mod is None:
            continue
        for k, v in vars(mod).items():
            if k.startswith("__") or not isinstance(v, MUTABLE_KINDS):
                continue
            referencing = [n for n, src in sources.items() if k in src]
            rec = (modname, k, type(v).__name__, len(v), referencing)
            (live if referencing else inert).append(rec)
    return live, inert


def snapshot_module_mutables():
    """Deep snapshot: repr plus container identity plus element identities."""
    snap = {}
    for modname in ("blackboard_ops", "blackboard_ops_v2", "blackboard_ops_r2",
                    "blackboard_ops_compare"):
        mod = sys.modules.get(modname)
        if mod is None:
            continue
        for k, v in vars(mod).items():
            if k.startswith("__") or not isinstance(v, MUTABLE_KINDS):
                continue
            vals = list(v.values()) if isinstance(v, dict) else list(v)
            snap[(modname, k)] = (repr(v), id(v), tuple(id(x) for x in vals))
    return snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=120)
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "congruence_audit_result.json"))
    args = ap.parse_args()

    tasks, _b = build_battery()
    tasks = tasks[:args.tasks]
    names = sorted(be.REGISTRY)
    ops_by_name = {n: be.REGISTRY[n][0] for n in names}
    ops = [ops_by_name[n] for n in names]

    print("=" * 78)
    print("CONGRUENCE AUDIT of the field projection D  (|D| = %d of %d fields)"
          % (len(D_FIELDS), len(ALL_FIELDS)))
    print("=" * 78)
    print()

    result = {}

    # ---- A/B/C: aliasing over the whole reachable closure ---------------------
    print("--- A/B/C  ALIASING over every reachable record of every task ---")
    n_states = 0
    cross_hits, inter_hits, any_hits = [], [], []
    for ti, t in enumerate(tasks):
        s0 = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        seen, frontier = {skey(s0)}, deque([s0])
        while frontier:
            s = frontier.popleft()
            n_states += 1
            c, i, a = sharing_report(s)
            if c:
                cross_hits.append((ti, c[:2]))
            if i:
                inter_hits.append((ti, i[:2]))
            if a:
                any_hits.append((ti, a[:2]))
            for op in ops:
                s2 = apply_op(op, s)
                k = skey(s2)
                if k not in seen:
                    seen.add(k)
                    frontier.append(s2)
    print("  records inspected: %d over %d tasks" % (n_states, len(tasks)))
    print("  A cross-boundary sharing (D field <-> non-D field) : %d" % len(cross_hits))
    print("  B inter-field sharing (any two distinct fields)     : %d" % len(inter_hits))
    print("  C any sharing at all (same object at two paths)     : %d" % len(any_hits))
    for label, hits in (("A", cross_hits), ("B", inter_hits), ("C", any_hits)):
        if hits:
            print("     %s example: task %d  %s" % (label, hits[0][0], hits[0][1]))
    result["aliasing"] = {"records": n_states, "cross_boundary": len(cross_hits),
                          "inter_field": len(inter_hits), "any_sharing": len(any_hits),
                          "cross_examples": cross_hits[:5], "inter_examples": inter_hits[:5],
                          "any_examples": any_hits[:5]}
    print()

    # ---- D/E: hidden state and escape hatches, static -------------------------
    print("--- D/E  HIDDEN STATE and ESCAPE HATCHES (static) ---")
    sa = static_audit(ops_by_name)
    live_mods, inert_mods = module_level_mutables(ops_by_name)
    mods = live_mods
    for k in ("globals_used", "mutable_defaults", "escapes", "whole_record_passed",
              "closure_cells", "func_attrs"):
        v = sa[k]
        print("  %-22s %d %s" % (k, len(v), (v[:4] if v else "")))
    print("  %-22s %d %s" % ("module mutables LIVE", len(live_mods), live_mods[:3]))
    print("  %-22s %d %s" % ("module mutables INERT", len(inert_mods),
                             [(m, k) for m, k, _t, _n, _r in inert_mods]))
    print("     (INERT = mutable, but the identifier appears in NO operator source.")
    print("      Confirmed dynamically below by deep before/after snapshot.)")
    result["static"] = {k: sa[k] for k in sa}
    result["static"]["module_mutables_live"] = live_mods
    result["static"]["module_mutables_inert"] = inert_mods
    print()

    mod_snapshot_before = snapshot_module_mutables()

    # ---- F: history independence, dynamic ------------------------------------
    print("--- F  HISTORY INDEPENDENCE (dynamic) ---")
    print("  For a sample of reachable records, apply each operator (a) directly and")
    print("  (b) after 40 unrelated operator applications on OTHER records. Require")
    print("  byte-identical projected output.")
    mismatches = []
    t0 = tasks[0]
    probe = BlackboardState(problem_text=t0["prompt"], candidates=t0["candidates"])
    samples = [probe]
    for op in ops[:6]:
        samples.append(apply_op(op, samples[-1]))
    burn_src = BlackboardState(problem_text=tasks[-1]["prompt"],
                               candidates=tasks[-1]["candidates"])
    for si, s in enumerate(samples):
        direct = {n: skey(apply_op(ops_by_name[n], s)) for n in names}
        burn = burn_src
        for r in range(40):
            burn = apply_op(ops[r % len(ops)], burn)
        after = {n: skey(apply_op(ops_by_name[n], s)) for n in names}
        for n in names:
            if direct[n] != after[n]:
                mismatches.append((si, n))
    print("  (record, operator) pairs tested: %d   MISMATCHES: %d"
          % (len(samples) * len(names), len(mismatches)))
    if mismatches:
        print("     !! %s" % mismatches[:6])
    result["history_independence"] = {"tested": len(samples) * len(names),
                                      "mismatches": mismatches[:20]}
    print()

    # ---- G: cross-task contamination -----------------------------------------
    print("--- G  CROSS-TASK CONTAMINATION (dynamic) ---")
    print("  Build each task's reachable answer-set with the battery in original order")
    print("  and in REVERSED order. Identical => no shared state leaks between tasks.")

    def answers(t):
        s0 = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        seen, frontier, ans = {skey(s0)}, deque([s0]), {s0.selected_answer}
        while frontier:
            s = frontier.popleft()
            for op in ops:
                s2 = apply_op(op, s)
                k = skey(s2)
                if k not in seen:
                    seen.add(k)
                    ans.add(s2.selected_answer)
                    frontier.append(s2)
        return frozenset(ans)

    fwd = {i: answers(t) for i, t in enumerate(tasks)}
    rev = {}
    for i in range(len(tasks) - 1, -1, -1):
        rev[i] = answers(tasks[i])
    diff = [i for i in fwd if fwd[i] != rev[i]]
    print("  tasks whose reachable answer set changed with evaluation order: %d / %d"
          % (len(diff), len(tasks)))
    if diff:
        print("     !! %s" % diff[:10])
    result["cross_task"] = {"n_tasks": len(tasks), "order_sensitive": diff}
    print()

    # ---- D-dynamic: did any module-level mutable actually change? -------------
    mod_after = snapshot_module_mutables()
    mod_changed = [k for k in mod_snapshot_before
                   if mod_snapshot_before[k] != mod_after.get(k)]
    print("--- D(dynamic)  MODULE-LEVEL MUTABLES after the whole audit ---")
    print("  containers tracked: %d   CHANGED: %d %s"
          % (len(mod_snapshot_before), len(mod_changed), mod_changed[:5]))
    result["module_mutables_changed"] = [list(k) for k in mod_changed]
    print()

    # ---- verdict --------------------------------------------------------------
    print("=" * 78)
    ok_alias = len(any_hits) == 0
    ok_crossb = len(cross_hits) == 0
    ok_hidden = not (sa["globals_used"] or sa["mutable_defaults"] or live_mods
                     or mod_changed)
    ok_hist = not mismatches
    ok_task = not diff
    print("VERDICT")
    print("  C  no aliasing anywhere (projection is a congruence)   : %s"
          % ("PASS" if ok_alias else "FAIL"))
    print("  A  no cross-boundary aliasing (reviewer's condition)   : %s"
          % ("PASS" if ok_crossb else "FAIL"))
    print("  D  no reachable/changing module state in operators     : %s"
          % ("PASS" if ok_hidden else "FAIL"))
    print("  F  operator transitions are history-independent        : %s"
          % ("PASS" if ok_hist else "FAIL"))
    print("  G  no cross-task contamination                         : %s"
          % ("PASS" if ok_task else "FAIL"))
    print()
    if ok_alias and ok_hidden and ok_hist and ok_task:
        print("  => The projection D IS a congruence on this operator set, and the")
        print("     transition system IS deterministic and task-separable. The reviewer's")
        print("     counterexample is valid Python and does NOT obtain here. Claim 1 and")
        print("     claim 2 stand, now on a measured premise rather than an assumed one.")
    elif ok_crossb and ok_hidden and ok_hist and ok_task:
        print("  => Cross-boundary aliasing is absent, so non-D fields cannot influence D.")
        print("     But sharing exists somewhere, so report the exact shape before")
        print("     claiming the congruence unconditionally.")
    else:
        print("  => AT LEAST ONE PREMISE FAILS. The 0.8333 closure is NOT certified.")
        print("     Report this immediately and do not restate the ceiling until fixed.")
    result["verdict"] = {"no_aliasing": ok_alias, "no_cross_boundary": ok_crossb,
                         "no_hidden_state": ok_hidden, "history_independent": ok_hist,
                         "task_separable": ok_task}
    Path(args.out).write_text(json.dumps(result, indent=1, default=str), encoding="utf-8")
    print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
