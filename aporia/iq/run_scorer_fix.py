"""run_scorer_fix.py — SCORER-FIX. Remove the candidates[0] guess; re-read the frozen corpus.

Preregistration: aporia/iq/PREREG_SCORERFIX_2026-08-25.md, committed BEFORE this file existed.
Predictions S1-S4 and the terminal table are fixed there.

C IS NOT EDITED. blackboard_evolve.REGISTRY is the byte-frozen baseline every dE in this arc is
defined against. The fix is a variant op built here and substituted at measurement time, so the
whole rung is reversible by not passing the variant.

    python aporia/iq/run_scorer_fix.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import blackboard_evolve as be                                    # noqa: E402
from blackboard import BlackboardState, BlackboardOp, run_pipeline  # noqa: E402
import port_ops                                                   # noqa: E402
from port_ops import _mutant                                      # noqa: E402
from run_iq_port_1 import (TASKS, make_pool, PORTED_BODY, CEILING_BODY,  # noqa: E402
                           CEILING_TAIL, cat_acc)
import transfer1_generator as G                                   # noqa: E402
from run_transfer_1 import score, by_key, ALL_MUTANTS             # noqa: E402

OUT = Path(__file__).resolve().parent
_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _abstain_aggregate(state: BlackboardState) -> BlackboardState:
    """score_by_aggregate with the guess removed.

    Identical to apollo/src/blackboard_ops_v2.py:score_by_aggregate EXCEPT that when no
    candidate matches max_value it writes NOTHING -- selected_answer is left untouched, which
    is what every other guarded scorer's on_fail='skip' path already does. The original emits
    candidates[0], which is a 1-in-4 guess on a 4-candidate task.
    """
    if not state.candidates or state.max_value is None:
        return state
    scores, best, best_i = [], -1.0, None
    for i, c in enumerate(state.candidates):
        m = _NUM.search(c)
        s = 1.0 if (m and abs(float(m.group(0)) - state.max_value) < 1e-6) else 0.0
        scores.append(s)
        if s > best:
            best, best_i = s, i
    if best <= 0.0:
        return state                      # ABSTAIN. This is the whole intervention.
    state.candidate_scores = scores
    state.selected_answer = state.candidates[best_i]
    return state


def fixed_pool(extra=None):
    """C u {abstain variant} u optional extras. C itself is never mutated."""
    base = be.REGISTRY["score_by_aggregate"][0]
    guard = be.REGISTRY["score_by_aggregate__g"][0]
    pool = make_pool(port_ops.PORT_OPS)
    pool["score_by_aggregate"] = BlackboardOp(
        _abstain_aggregate, reads=base.reads, writes=base.writes,
        precondition=base.precondition, on_fail="skip", name="score_by_aggregate")
    pool["score_by_aggregate__g"] = BlackboardOp(
        _abstain_aggregate, reads=guard.reads, writes=guard.writes,
        precondition=guard.precondition, on_fail="skip", name="score_by_aggregate__g")
    if extra:
        pool.update(extra)
    return pool


def audit_scorers():
    """S4. For each scorer: construct a state where it fires and NOTHING matches, and record
    whether it emits an answer anyway. Executed, not read off the source."""
    out = {}
    for name in sorted(be.SCORERS):
        op = be.REGISTRY[name][0]
        st = BlackboardState(problem_text="probe", candidates=["777 a", "888 b", "999 c"])
        # populate every slot a scorer might key on, with values matching no candidate
        st.max_value = 1.0
        st.ordered = ["zzz"]
        st.question_target = "first"
        st.facts = {"p"}
        st.derived_facts = {"q"}
        st.counts = {"k": {"count": 1}}
        st.comparison = True
        st.extreme_number = "1"
        st.max_entity = "zzz"
        st.numbers = [1.0]
        try:
            res = run_pipeline([op], st)
            ans = res.selected_answer
        except Exception as e:
            ans = f"<EXC {type(e).__name__}>"
        out[name] = {"emitted": ans,
                     "guessed_first_candidate": (ans == "777 a"),
                     "abstained": (ans == "")}
    return out


def main():
    R = {"experiment": "SCORER-FIX", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_SCORERFIX_2026-08-25.md",
         "C_edited": False,
         "note": "C = blackboard_evolve.REGISTRY untouched; the fix is a harness-side variant."}

    train, test, xsets = G.build()
    R["corpus_sha256"] = G.corpus_hash(train, test, xsets)
    R["corpus_matches_transfer1"] = (R["corpus_sha256"].startswith("e2e6898d"))
    nd = [t for t in train + test if t["stratum"] == "NONDEGENERATE"]
    deg = [t for t in train + test if t["stratum"] == "DEGENERATE"]
    R["nondegenerate_n"], R["degenerate_n"] = len(nd), len(deg)
    R["dropped_records"] = 0
    R["dropped_records_note"] = ("Nothing dropped. Every task scored under both pools; "
                                 "pipeline exceptions count as WRONG.")

    PIPE = PORTED_BODY + CEILING_TAIL
    OLD = make_pool(port_ops.PORT_OPS)
    NEW = fixed_pool()

    # ── S1: mutants on NONDEGENERATE, before and after ───────────────────────
    mut = {}
    for name, op in ALL_MUTANTS.items():
        po = make_pool({"parse_all_but_n": port_ops.parse_all_but_n, "op_all_but_n": op})
        pn = fixed_pool({"parse_all_but_n": port_ops.parse_all_but_n, "op_all_but_n": op})
        ko, no_, _ = score(nd, po, PIPE)
        kn, _, _ = score(nd, pn, PIPE)
        mut[name] = {"before": round(ko / no_, 4), "after": round(kn / no_, 4)}
    R["mutants_nondegenerate"] = mut
    worst_after = max(v["after"] for v in mut.values())
    R["worst_mutant_after"] = worst_after
    R["S1_all_mutants_at_or_below_0.02"] = (worst_after <= 0.02)

    # ── S2: the port, per surface, before and after ──────────────────────────
    def per_surface(pool, tasks):
        _, _, per = score(tasks, pool, PIPE)
        return by_key(tasks, per, "surface")
    R["port_by_surface_before"] = per_surface(OLD, train + test)
    R["port_by_surface_after"] = per_surface(NEW, train + test)
    moved = {k: (R["port_by_surface_before"][k]["acc"], R["port_by_surface_after"][k]["acc"])
             for k in R["port_by_surface_before"]
             if abs(R["port_by_surface_before"][k]["acc"]
                    - R["port_by_surface_after"][k]["acc"]) > 0.01}
    R["port_surfaces_moved"] = moved
    R["S2_port_unchanged"] = (len(moved) == 0)
    ko, n_nd, _ = score(nd, OLD, PIPE)
    kn, _, _ = score(nd, NEW, PIPE)
    R["port_nondegenerate_before"] = round(ko / n_nd, 4)
    R["port_nondegenerate_after"] = round(kn / n_nd, 4)

    # ── S3: the 120-task battery, before and after. LOUD if it moves. ────────
    def battery(pool, pipeline):
        hits, per = 0, []
        for t in TASKS:
            st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
            try:
                ans = run_pipeline([pool[n] for n in pipeline], st).selected_answer
            except Exception:
                ans = ""
            ok = (ans == t["correct"])
            hits += ok
            per.append(ok)
        return hits / len(TASKS), per

    base_old, _ = battery(OLD, CEILING_BODY + CEILING_TAIL)
    base_new, _ = battery(NEW, CEILING_BODY + CEILING_TAIL)
    port_old, pold = battery(OLD, PIPE)
    port_new, pnew = battery(NEW, PIPE)
    R["battery_baseline_before"], R["battery_baseline_after"] = round(base_old, 6), round(base_new, 6)
    R["battery_ported_before"], R["battery_ported_after"] = round(port_old, 6), round(port_new, 6)
    R["battery_moved"] = (abs(base_old - base_new) > 1e-12 or abs(port_old - port_new) > 1e-12)
    R["S3_battery_unchanged"] = not R["battery_moved"]
    R["delta_E_port_after_fix"] = round(port_new - base_new, 6)
    if R["battery_moved"]:
        R["LOUD"] = ("THE 120-TASK BATTERY MOVED under the fix. Every prior rung in this arc "
                     "quoted the pre-fix numbers.")

    # ── S4: audit every scorer ───────────────────────────────────────────────
    aud = audit_scorers()
    R["scorer_audit"] = aud
    guessers = sorted(k for k, v in aud.items() if v["guessed_first_candidate"])
    R["scorers_that_guess_first_candidate"] = guessers
    R["S4_other_guessers_found"] = len([g for g in guessers if "aggregate" not in g]) > 0

    # ── terminal state, asserted to partition over S1 x S2 ───────────────────
    s1, s2 = R["S1_all_mutants_at_or_below_0.02"], R["S2_port_unchanged"]
    R["verdict"] = ("PARK_ABSTAIN_DOES_NOT_REMOVE_FLOOR" if not s1
                    else ("REDESIGN_PORT_WAS_RIDING_THE_GUESS" if not s2 else "ADVANCE"))
    R["verdict_rule_null_output"] = ("If the corpus regenerated differently, corpus_sha256 would "
                                     "not start e2e6898d and the before/after would be "
                                     "incomparable; that is reported, never silently passed.")
    seen = {("PARK_ABSTAIN_DOES_NOT_REMOVE_FLOOR" if not a else
             ("REDESIGN_PORT_WAS_RIDING_THE_GUESS" if not b else "ADVANCE"))
            for a in (True, False) for b in (True, False)}
    assert seen == {"PARK_ABSTAIN_DOES_NOT_REMOVE_FLOOR",
                    "REDESIGN_PORT_WAS_RIDING_THE_GUESS", "ADVANCE"}, "terminal table leaks"
    R["terminal_table_partitions"] = True

    json.dump(R, open(OUT / "RESULT_SCORER_FIX.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        if k not in ("dropped_records_note", "verdict_rule_null_output", "note"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
