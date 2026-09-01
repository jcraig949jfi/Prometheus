"""G7 — re-measure the slice on an INDEPENDENTLY-AUTHORED battery (Charon's E9, 42 tasks).

Backlog item 0 of `roles/Lexis/ROLE.md` §6, inserted 2026-08-27 ahead of everything else.
Every accuracy number in ROLE.md §4a was measured over T_home, the 120-task battery from
`o1_enumerate.build_battery()`. Apollo's E9 showed T_home is co-adapted with its own parsers
(Charon's blind 42-task battery: 2/42 correct, 40 abstentions). This instrument re-runs the
slice's three measurements over T_charon instead, under the SAME clean-routing pool and the
SAME 24-permutation standard, so the two populations can be compared like for like.

  1. the exact joint ceiling of the clean pool C (product BFS, exhausted or reported capped)
  2. the dE / dS split of the tasks the production organism fails
  3. the bundle arms: C, C+compute, C+readout, C+compute+readout  (dE, dS, dROBUST)

THE BATTERY SEAM. Charon's file is the identical {prompt, candidates, correct, category}
schema build_battery() returns. It is loaded here, on the Lexis side; nothing in apollo/ is
imported differently and nothing there is written. The E9 file is read verbatim.

POSITIVE CONTROLS, both mandatory, both fatal on mismatch:
  P1  the known 0.8333 organism scores 0.8333 on T_home   -> the substrate loaded correctly
  P2  the known organism scores 2/42 with 40 abstentions on T_charon -> the battery adapter
      is faithful to E9 (E9_RESULT.json; abstain sentinel is the empty string "", not None,
      per apollo/scripts/e9_score.py)

PRE-COMMITTED READINGS, fixed in notes/E9_INGESTION_2026-08-27.md §7 BEFORE this file
existed, copied here verbatim so the instrument prints its own verdict:

  R1  the pair buys 0 on Charon's all_but_n  -> the +5/+5/+5 dE is AUTHORSHIP-BOUND; the G5
      ledger's only positive is retracted to home-battery-only; the interface-pair claim
      drops from measured to hypothesised. Reported as the headline.
  R2  the pair buys > 0                       -> the interface-pair claim survives its first
      population change and becomes the strongest object in the slice.
  R3  the ceiling over T_charon sits at or near floor with mass abstention -> confirms the
      deficit is the surface layer; quantifies how much of the 16.67% dE was authorship;
      decides E9's own open question (parser failure vs capability failure) from this side.

"Near floor" for R3 is fixed here, before the run, as: exact ceiling <= 11/42 (the chance
floor 0.25 is 10.5/42; Charon's measured trivial-heuristic floors are 0.2599 / 0.2560).
Note the clean pool contains no unconditional scorer, so a ceiling of k/42 means k tasks
whose correct answer some program actually ROUTES to, not k lucky positional hits.

DIRECTIONALITY (ROLE.md G7). This is a population change, not a null. It removes the
co-adaptation advantage but is a different distribution, so it is NOT monotone. Surviving it
is a generalisation result, not the same kind of evidence as surviving a permutation null.

Read-only with respect to apollo/. Writes only notes/g7_charon_result.json (never the
home-battery result files).
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                        # noqa: E402
from blackboard import BlackboardState, run_pipeline  # noqa: E402
from o1_enumerate import build_battery, KNOWN_0833    # noqa: E402
from _answer_slice import D as _SLICE                 # noqa: E402
from candidate_primitives import CANDIDATES           # noqa: E402
from bundle_test import evaluate, skey, table         # noqa: E402

CHARON = ROOT / "roles" / "Charon" / "apollo_e9" / "charon_battery_E9.json"
E9_RESULT = APOLLO / "cycles" / "campaign_20260825" / "E9_RESULT.json"
FLOOR_TASKS = 11          # pre-committed "near floor" line: ceiling <= 11/42


def load_charon():
    tasks = json.loads(CHARON.read_text(encoding="utf-8"))
    for t in tasks:
        assert set(t) >= {"prompt", "candidates", "correct", "category"}, t
        assert t["correct"] in t["candidates"], t
    cats = collections.Counter(t["category"] for t in tasks)
    bounds, off = [], 0
    for c in sorted(cats):
        n = cats[c]
        bounds.append((c, off, off + n))
        off += n
    # regroup so the bounds are contiguous, keeping Charon's within-category order
    ordered = [t for c in sorted(cats) for t in tasks if t["category"] == c]
    return ordered, bounds


def organism_run(tasks):
    ops = [be.REGISTRY[n][0] for n in KNOWN_0833]
    rows = []
    for t in tasks:
        s = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        try:
            ans = run_pipeline(ops, s).selected_answer
        except Exception as e:                       # noqa: BLE001
            ans = "<exception:%s>" % type(e).__name__
        abst = ans in ("", None)
        rows.append({"correct": (ans == t["correct"]), "abstained": abst,
                     "guessed_wrong": (not abst and ans != t["correct"]), "answer": ans})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=2_000_000)
    ap.add_argument("--rcap", type=int, default=300000)
    ap.add_argument("--compute", default="lexis_op_subtract")
    ap.add_argument("--readout", default="lexis_score_by_value_match__g")
    ap.add_argument("--out", default=str(HERE.parent / "notes" / "g7_charon_result.json"))
    args = ap.parse_args()

    home, home_bounds = build_battery()
    charon, bounds = load_charon()
    print("T_home   : %d tasks   T_charon : %d tasks in %d categories"
          % (len(home), len(charon), len(bounds)))

    # ---- P1 -------------------------------------------------------------------------
    h = organism_run(home)
    p1 = sum(r["correct"] for r in h) / len(h)
    print("P1  known organism on T_home   = %.4f (expect 0.8333) -> %s"
          % (p1, "MATCH" if abs(p1 - 0.8333) < 1e-3 else "MISMATCH"))
    if abs(p1 - 0.8333) >= 1e-3:
        return 2

    # ---- P2 -------------------------------------------------------------------------
    c = organism_run(charon)
    n_ok = sum(r["correct"] for r in c)
    n_ab = sum(r["abstained"] for r in c)
    n_gw = sum(r["guessed_wrong"] for r in c)
    exp_ok, exp_ab = 2, 40
    if E9_RESULT.exists():
        try:
            e9 = json.loads(E9_RESULT.read_text(encoding="utf-8"))
            pc = e9.get("per_category", {})
            if pc:      # E9_RESULT.json keeps counts per category, not top-level
                exp_ok = sum(v["correct"] for v in pc.values())
                exp_ab = sum(v["abstained"] for v in pc.values())
        except Exception:                            # noqa: BLE001
            pass
    p2 = (n_ok == exp_ok and n_ab == exp_ab)
    print("P2  known organism on T_charon = %d/%d correct, %d abstained, %d guessed wrong"
          " (E9: %d correct, %d abstained) -> %s"
          % (n_ok, len(c), n_ab, n_gw, exp_ok, exp_ab, "MATCH" if p2 else "MISMATCH"))
    if not p2:
        print("    the battery adapter does not reproduce E9. Aborting.")
        return 2
    print()

    # ---- clean pool C, exactly as bundle_test.py defines it --------------------------
    base_names = [n for n in sorted(be.REGISTRY)
                  if (be.role_of(n) == "transformer" or n in be.GUARDED_SCORERS)
                  and set(be.REGISTRY[n][0].writes) & set(_SLICE)]
    base_ops = [be.REGISTRY[n][0] for n in base_names]
    C = CANDIDATES[args.compute]
    R = CANDIDATES[args.readout]
    print("clean pool C: %d operators; compute=%s readout=%s"
          % (len(base_ops), args.compute, args.readout))
    print()

    # ---- 1 + 3: the four arms (reach = dE ledger, ceiling = dS ledger, robust) --------
    arms = [("baseline C", ()), ("C + compute", (C,)),
            ("C + readout", (R,)), ("C + compute + readout", (C, R))]
    out, t0 = {}, time.time()
    for label, extra in arms:
        r = evaluate(label, extra, base_ops, charon, args.cap, args.rcap)
        out[label] = {k: v for k, v in r.items() if k != "reach"}
        out[label]["reach_tasks"] = [i for i, b in enumerate(r["reach"]) if b]
        print("  %-24s ops=%-3d  reachable=%3d  ceiling=%3d/%d %-11s  robust=%3d %s (%.0fs)"
              % (label, r["n_ops"], r["reach_n"], r["ceiling"], len(charon),
                 "(exhausted)" if r["exhausted"] else "(CAPPED)", r["robust_n"],
                 ("unres %d" % len(r["robust_unresolved"])) if r["robust_unresolved"] else "",
                 time.time() - t0))
    b = out["baseline C"]
    for label, _ in arms[1:]:
        a = out[label]
        a["dE"] = a["reach_n"] - b["reach_n"]
        a["dS"] = a["ceiling"] - b["ceiling"]
        a["dROBUST"] = a["robust_n"] - b["robust_n"]
    print()

    # ---- 2: dE / dS split under baseline C, and per category --------------------------
    reach_b = set(b["reach_tasks"])
    solved = [i for i, r in enumerate(c) if r["correct"]]
    dS = [i for i, r in enumerate(c) if not r["correct"] and i in reach_b]
    dE = [i for i, r in enumerate(c) if not r["correct"] and i not in reach_b]
    n = len(charon)
    print("=" * 76)
    print("DECOMPOSITION OF T_charon (%d tasks) under the production 0.833 organism" % n)
    print("=" * 76)
    print("  solved by the organism                       %3d / %d  = %.4f" % (len(solved), n, len(solved) / n))
    print("  UNREACHED, correct answer NOT in closure     %3d / %d  = %.4f   <- dE-bound"
          % (len(dE), n, len(dE) / n))
    print("  UNREACHED, correct answer IS in closure      %3d / %d  = %.4f   <- dS-bound"
          % (len(dS), n, len(dS) / n))
    print()
    per_cat = {}
    pair_reach = set(out["C + compute + readout"]["reach_tasks"])
    pair_rob = set(out["C + compute + readout"]["robust"])
    base_rob = set(b["robust"])
    print("  %-22s %6s %5s %5s %5s | %8s %8s | %10s %10s" % (
        "category", "solved", "abst", "dS", "dE", "C_reach", "C_rob", "pair_reach", "pair_rob"))
    for name, a0, a1 in bounds:
        idx = range(a0, a1)
        row = {
            "n": a1 - a0,
            "solved": sum(1 for i in idx if i in solved),
            "abstained": sum(1 for i in idx if c[i]["abstained"]),
            "dS": sum(1 for i in idx if i in dS),
            "dE": sum(1 for i in idx if i in dE),
            "C_reach": sum(1 for i in idx if i in reach_b),
            "C_robust": sum(1 for i in idx if i in base_rob),
            "pair_reach": sum(1 for i in idx if i in pair_reach),
            "pair_robust": sum(1 for i in idx if i in pair_rob),
        }
        per_cat[name] = row
        print("  %-22s %6d %5d %5d %5d | %8d %8d | %10d %10d" % (
            name, row["solved"], row["abstained"], row["dS"], row["dE"],
            row["C_reach"], row["C_robust"], row["pair_reach"], row["pair_robust"]))
    print()

    # ---- 2b: RECOGNITION -- which operators fire on the INITIAL state at all -----------
    # A task whose per-task closure under C has size 1 is one where no operator in the
    # clean pool changes the initial state: the surface layer did not recognise it. This
    # separates "unrecognised" from "recognised but inexpressible" without touching Apollo.
    recog = []
    for i, t in enumerate(charon):
        s0 = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        k0 = skey(s0)
        fired = []
        for nm, op in zip(base_names, base_ops):
            try:
                s2 = op(copy.deepcopy(s0))
            except Exception:                        # noqa: BLE001
                s2 = s0
            if skey(s2) != k0:
                fired.append(nm)
        d, _ = table(t["prompt"], t["candidates"], t["correct"], base_ops)
        recog.append({"idx": i, "category": t["category"], "closure_size": len(d),
                      "fired_at_s0": fired})
    unrec = [r["idx"] for r in recog if r["closure_size"] == 1]
    numonly = [r["idx"] for r in recog if r["fired_at_s0"] == ["parse_numbers"]]
    fire_count = collections.Counter(nm for r in recog for nm in r["fired_at_s0"])
    print("RECOGNITION over T_charon under C (initial state only)")
    print("  unrecognised (closure size 1, no operator fires)    %2d / %d" % (len(unrec), n))
    print("  number-extraction only (parse_numbers is all that fires) %2d / %d" % (len(numonly), n))
    print("  operators that fire on ANY Charon initial state: %s" % dict(sorted(fire_count.items())))
    never = [nm for nm in base_names if be.role_of(nm) == "transformer" and nm not in fire_count]
    print("  transformers that fire on NO Charon initial state: %s" % never)
    print()

    # ---- 2c: the pair's trace on Charon's all_but_n, so the rows ship with the verdict --
    abn_trace = []
    for i, t in enumerate(charon):
        if t["category"] != "all_but_n":
            continue
        s = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        for op in base_ops:
            try:
                s = op(s)
            except Exception:                        # noqa: BLE001
                pass
        nums = list(s.numbers)
        for op in (C, R):
            try:
                s = op(s)
            except Exception:                        # noqa: BLE001
                pass
        abn_trace.append({"idx": i, "numbers": nums, "max_value": s.max_value,
                          "selected": s.selected_answer, "correct": t["correct"],
                          "ok": s.selected_answer == t["correct"],
                          "wrong_guess": bool(s.selected_answer) and s.selected_answer != t["correct"],
                          "prompt": t["prompt"]})
    print("PAIR TRACE on Charon's all_but_n (parse_numbers -> subtract -> value-match)")
    for r in abn_trace:
        print("  task %2d numbers=%-14s max_value=%-6s sel=%-5r correct=%-5r %s"
              % (r["idx"], r["numbers"], r["max_value"], r["selected"], r["correct"],
                 "OK" if r["ok"] else ("WRONG GUESS" if r["wrong_guess"] else "abstain")))
    n_wrong = sum(r["wrong_guess"] for r in abn_trace)
    if n_wrong:
        print("  NOTE: the pair converts %d abstention(s) into WRONG guesses. Inspect the"
              " prompts: these ask for the complement." % n_wrong)
    print()

    # ---- verdicts against the pre-committed readings ---------------------------------
    pair = out["C + compute + readout"]
    abn = per_cat.get("all_but_n", {})
    pair_abn_gain = abn.get("pair_reach", 0) - abn.get("C_reach", 0)
    pair_abn_rob_gain = abn.get("pair_robust", 0) - abn.get("C_robust", 0)
    print("=" * 76)
    print("PRE-COMMITTED READINGS (E9_INGESTION_2026-08-27.md §7)")
    print("=" * 76)
    print("  pair arm over all of T_charon : dE=%+d  dS=%+d  dROBUST=%+d"
          % (pair["dE"], pair["dS"], pair["dROBUST"]))
    print("  pair arm on Charon's all_but_n: reach %+d  robust %+d  (of %d)"
          % (pair_abn_gain, pair_abn_rob_gain, abn.get("n", 0)))
    if pair_abn_gain == 0 and pair["dE"] == 0:
        r12 = ("R1 FIRES. The pair buys NOTHING on Charon's battery. The +5/+5/+5 is "
               "AUTHORSHIP-BOUND; the G5 ledger's only positive is retracted to "
               "home-battery-only; the interface-pair claim is HYPOTHESISED, not measured.")
    elif pair_abn_gain > 0 or pair["dE"] > 0:
        r12 = ("R2 FIRES. The pair moves the closure on an independently-authored battery "
               "(%+d overall, %+d on all_but_n). The interface-pair claim survives its "
               "first population change." % (pair["dE"], pair_abn_gain))
        if pair["dROBUST"] == 0:
            r12 += (" BUT dROBUST = 0: nothing gained survives all 24 permutations, so "
                    "the gain is a positional fallback, not an answer. Report as such.")
    else:
        r12 = "NEITHER R1 NOR R2 as written (pair dE=%d, all_but_n %+d). Report raw." % (
            pair["dE"], pair_abn_gain)
    print("  " + r12)
    ceil = b["ceiling"]
    if ceil <= FLOOR_TASKS:
        r3 = ("R3 FIRES. Exact clean-pool ceiling over T_charon = %d/%d = %.4f (line %d/42; "
              "chance 10.5/42); organism abstained on %d/%d; %d/%d tasks unrecognised by every "
              "operator and %d/%d reach only number extraction. The deficit is the SURFACE "
              "layer. Under a change of author the dE-bound fraction goes from 16.67%% (home) "
              "to %.2f%%: the home battery's 83.33%% solved was authorship-bound."
              % (ceil, n, ceil / n, FLOOR_TASKS, n_ab, n, len(unrec), n, len(numonly), n,
                 100.0 * len(dE) / n))
    else:
        r3 = ("R3 does NOT fire. Exact clean-pool ceiling over T_charon = %d/%d = %.4f is "
              "ABOVE the pre-committed line %d/42, although the organism abstained on %d/%d. "
              "Apollo's vocabulary expresses more of Charon's battery than production routing "
              "reaches: that part is dS, not surface." % (ceil, n, ceil / n, FLOOR_TASKS, n_ab, n))
    print("  " + r3)
    if not b["exhausted"]:
        print("  NOTE: baseline joint BFS was CAPPED; the ceiling is a LOWER bound.")
    print()

    Path(args.out).write_text(json.dumps({
        "battery": str(CHARON.relative_to(ROOT)), "n_tasks": n,
        "category_bounds": bounds,
        "P1_home_known_organism_acc": p1,
        "P2_charon_known_organism": {"correct": n_ok, "abstained": n_ab,
                                     "guessed_wrong": n_gw, "e9_expected": [exp_ok, exp_ab]},
        "organism_rows": c,
        "clean_pool": base_names,
        "arms": out,
        "solved": solved, "dS_bound": dS, "dE_bound": dE,
        "per_category": per_cat,
        "recognition": recog, "unrecognised": unrec, "number_only": numonly,
        "transformers_never_firing": never,
        "all_but_n_pair_trace": abn_trace,
        "floor_line_tasks": FLOOR_TASKS,
        "readings": {"R1R2": r12, "R3": r3},
    }, indent=1), encoding="utf-8")
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
