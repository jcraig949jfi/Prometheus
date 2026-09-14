"""Nyx 2026-09-11: switches and negative controls for the hypothesis shrinker (PREREG s3).
Run with Techne's isolated env from the repo root:
  <tool_cache>/envs/h0h5_tools/Scripts/python nyx/specimens/hypothesis_shrinker/ablations/n1_controls.py
Writes RECEIPT_N1_<date>.json beside itself. Order: negatives first (K4), then standalone (P-a),
then engine-level switches, then the consumer's worst case (P-b). Every block records what was
PREDICTED in PREREG and what was OBSERVED; nothing is asserted, the receipt is the evidence.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import io
import json
import os
import random
import sys
import time
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

import hypothesis  # noqa: E402
from hypothesis import Phase, find, settings, HealthCheck, Verbosity  # noqa: E402
from hypothesis import strategies as st  # noqa: E402
from hypothesis.errors import NoSuchExample, Unsatisfiable  # noqa: E402
from hypothesis.internal.conjecture.junkdrawer import find_integer  # noqa: E402
from hypothesis.internal.conjecture.shrinking import Collection, Integer, Ordering  # noqa: E402

REC: dict = {"date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
             "hypothesis_version": hypothesis.__version__, "python": sys.executable,
             "shrinker_sha256": hashlib.sha256((Path(hypothesis.__file__).parent / "internal/conjecture/shrinker.py").read_bytes()).hexdigest(),
             "blocks": []}


def block(name, predicted, fn):
    calls = {"n": 0}
    t0 = time.perf_counter()
    try:
        observed = fn(calls)
        err = None
    except Exception as e:  # noqa: BLE001
        observed, err = None, f"{type(e).__name__}: {e}"[:300]
    REC["blocks"].append({"name": name, "predicted": predicted, "observed": observed, "error": err,
                          "predicate_calls": calls["n"], "seconds": round(time.perf_counter() - t0, 3)})


def counting(pred, calls):
    def f(*a):
        calls["n"] += 1
        return pred(*a)
    return f


# ---------------- negatives first (K4), standalone organs (c07, c03, c01)
block("N-a_standalone_always_false_returns_initial", "Integer.shrink(1000, always False) == 1000; Collection likewise unchanged",
      lambda c: {"integer": Integer.shrink(1000, counting(lambda n: False, c)),
                 "collection": list(Collection.shrink((5, 7, 9), counting(lambda s: False, c), ElementShrinker=Integer, min_size=0))})
block("N-b_standalone_local_minimum_plant", "P3: predicate true only at n>=1000 or n==5; Integer stops at 1000 (5 unreachable by its moves)",
      lambda c: Integer.shrink(1000, counting(lambda n: n >= 1000 or n == 5, c)))
block("N-b2_standalone_reachable_control", "same shape but a reachable target: true at n>=1000 or n==0 -> 0 (short_circuit tries 0 first)",
      lambda c: Integer.shrink(1000, counting(lambda n: n >= 1000 or n == 0, c)))
block("N-e_find_integer_nonmonotone", "returns 3 (local boundary), NOT 5+: the organ does not promise the global boundary",
      lambda c: find_integer(counting(lambda k: k <= 3 or k in (5, 6), c)))
# ---------------- positives standalone (P-a): first independent-of-engine behaviour
block("P-a1_Integer_positive", "Integer.shrink(1000, n > 42) == 43 with O(log) predicate calls",
      lambda c: Integer.shrink(1000, counting(lambda n: n > 42, c)))
block("P-a2_Ordering_positive", "Ordering.shrink([3,1,2], always True) == (1,2,3)",
      lambda c: list(Ordering.shrink([3, 1, 2], counting(lambda s: True, c))))
block("P-a3_Collection_positive", "Collection.shrink((5,7,9,7,1), contains 7) == [7]",
      lambda c: list(Collection.shrink((5, 7, 9, 7, 1), counting(lambda s: 7 in s, c), ElementShrinker=Integer, min_size=0)))
block("P-a4_find_integer_positive", "find_integer(k <= 37) == 37 in far fewer than 37 calls",
      lambda c: find_integer(counting(lambda k: k <= 37, c)))
def _pa5(c):
    # cheat control for c01: every ADOPTED value must be strictly smaller than the previous one.
    # (The first run of this block had a malformed check whose 'true' was vacuous; recorded in CUTS.md.)
    accepted = []

    def pred(n):
        ok = n > 42
        if ok:
            accepted.append(n)  # the shrinker only calls the predicate on candidates it would adopt
        return ok
    result = Integer.shrink(1000, counting(pred, c))
    strictly_decreasing = all(b < a for a, b in zip(accepted, accepted[1:]))
    return {"result": result, "accepted_sequence": accepted, "strictly_decreasing": strictly_decreasing}


block("P-a5_Integer_cheat_control_order_strict", "every adopted value strictly smaller than the last (c01: adoption is a strict decrease under the order)", _pa5)

# ---------------- engine-level switches (Phase.shrink on/off), K6 null configuration
BASE = settings(database=None, deadline=None, suppress_health_check=list(HealthCheck), max_examples=500)


def _first_found_and_result(phases, seed):
    first = {"x": None}

    def cond(x):
        ok = x >= 1000
        if ok and first["x"] is None:
            first["x"] = x
        return ok
    r = find(st.integers(), cond, settings=settings(BASE, phases=phases), random=random.Random(seed))
    return {"first_satisfying_seen": first["x"], "returned": r}


block("S-b_engine_shrink_on", "find(integers, x >= 1000) == 1000",
      lambda c: _first_found_and_result([Phase.generate, Phase.shrink], 1))
block("N-c_engine_null_config_shrink_off", "K6: with Phase.shrink EXCLUDED the returned example equals the FIRST satisfying example seen; if it is smaller, something reduced it outside the shrinker",
      lambda c: _first_found_and_result([Phase.generate], 1))
block("N-d_engine_nonmonotone_two_seeds", "find(integers(0,10**6), x % 7 == 3 and x > 100) for seeds 1 and 2: equal results (101 is the minimum; predicted reached by both)",
      lambda c: [find(st.integers(0, 10 ** 6), lambda x: x % 7 == 3 and x > 100, settings=settings(BASE, phases=[Phase.generate, Phase.shrink]), random=random.Random(s)) for s in (1, 2)])
block("S-a_engine_derandomize_vs_seed", "derandomize=True gives the same final example as a seeded run (the shrunk result does not depend on the path)",
      lambda c: {"derandomized": find(st.integers(), lambda x: x >= 1000, settings=settings(BASE, derandomize=True)),
                 "seeded": find(st.integers(), lambda x: x >= 1000, settings=settings(BASE), random=random.Random(7))})
block("N-f_engine_local_minimum_plant", "P3 at engine level: find(integers, x >= 1000 or x == 5) -> does the full pass set reach 5? Standalone Integer could not; the engine has minimize_individual_choices + try_trivial_spans (index-0) -- prediction: reaches 5 only if a pass proposes it directly; expected 1000",
      lambda c: find(st.integers(), lambda x: x >= 1000 or x == 5, settings=settings(BASE), random=random.Random(3)))
block("N-g_engine_structural_nested_not", "pass_to_descendant positive: a recursive one_of strategy; predicate 'contains at least one Not' -- minimal is Not(leaf); prediction: reached",
      lambda c: (lambda tree: find(tree, lambda t: str(t).count("Not") >= 1, settings=settings(BASE), random=random.Random(5)))(
          st.recursive(st.sampled_from(["x0", "x1"]), lambda ch: st.one_of(ch.map(lambda a: ("Not", a)), st.tuples(ch, ch).map(lambda p: ("And",) + p)), max_leaves=6)))

# ---------------- consumer worst case (P-b): Proteus target 7 with the shrink profiling report captured
def _proteus_target7(c):
    # Techne's check realises an integer target as a canonical sum-of-products EXPRESSION
    # (techne/acquisition/checks/hypothesis_program_minimiser.py::target_expr); reuse it verbatim.
    sys.path.insert(0, str(ROOT / "techne" / "acquisition" / "checks"))
    from hypothesis_program_minimiser import target_expr  # noqa: E402
    from proteus.eval.hypothesis_strategy import solving_programs
    from proteus.eval.shrink import size_key, canonical, minimal_by_enumeration, still_solves
    tgt = target_expr(7)
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        try:
            prog = find(solving_programs(tgt), lambda p: still_solves(p, tgt),
                        settings=settings(BASE, verbosity=Verbosity.debug, max_examples=300, derandomize=True,
                                          phases=[Phase.generate, Phase.shrink]))
            found = {"program": canonical(prog), "size_key": list(size_key(prog))}
        except (NoSuchExample, Unsatisfiable) as e:
            found = {"error": type(e).__name__}
    log = buf.getvalue()
    useful = [ln.strip() for ln in log.splitlines() if ln.strip().startswith("*") or "Shrinking made a total" in ln]
    gt = minimal_by_enumeration(tgt)
    return {"found": found, "ground_truth": {"program": gt["canonical"], "size_key": list(gt["size_key"])} if gt else None,
            "pass_report_lines": useful[:20], "log_bytes": len(log)}


block("P-b_proteus_target7_with_pass_profile", "Techne saw size 9 vs ground truth 5 for target 7; prediction P6: the result is not minimal and the profile shows which passes fired (structural passes vs value passes)", _proteus_target7)

out = HERE / f"RECEIPT_N1_{_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')}.json"
out.write_text(json.dumps(REC, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
print(json.dumps(REC, indent=1, ensure_ascii=False, default=str))
