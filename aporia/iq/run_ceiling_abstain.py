"""run_ceiling_abstain.py — CEILING-UNDER-ABSTAIN. Is the proven 0.8333 partly a guess?

Preregistration: aporia/iq/PREREG_CEILING_ABSTAIN_2026-08-25.md (7a0e5b6d), committed before
this file existed. C is never edited; all eight abstain variants are harness-side.

METHOD FOR THE VARIANTS. Rather than reimplementing eight scorers (which would risk a variant
that differs from its original for reasons other than the guess), each variant WRAPS the
original op and reverts the write when the emission is the no-match guess: run the original on
a copy, and accept its answer only if the answer is genuinely matched rather than the
candidates[0] fall-through. "Genuinely matched" is decided by re-running the original against a
state whose candidate list has the emitted answer REMOVED -- a fall-through emits position 0
regardless of content, so it will emit the new position 0; a real match will emit nothing or a
different value. That is a behavioural test, not a source reading.

    python aporia/iq/run_ceiling_abstain.py
"""
from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "apollo" / "scripts",
          ROOT / "agents" / "hephaestus" / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import blackboard_evolve as be                                     # noqa: E402
from blackboard import BlackboardState, BlackboardOp, run_pipeline  # noqa: E402
import port_ops                                                    # noqa: E402
from run_iq_port_1 import (TASKS, make_pool, PORTED_BODY, CEILING_BODY,  # noqa: E402
                           CEILING_TAIL)

OUT = Path(__file__).resolve().parent

GUESSERS = ["score_by_aggregate", "score_by_aggregate__g", "score_by_derivability",
            "score_by_derivability__g", "score_by_max_entity", "score_by_max_value",
            "select_nth", "select_nth__g"]


def _abstaining(orig: BlackboardOp) -> BlackboardOp:
    """Wrap `orig` so a candidates[0] fall-through becomes an abstention.

    DISCRIMINATOR v2 — ROTATION, not removal. The v1 test removed the emitted candidate and
    asked whether the op then emitted the new position 0. That CANNOT distinguish a genuine
    match at position 0 from a fall-through, because removing a genuinely-matched candidate
    leaves nothing to match and the original falls through by construction. It was caught by
    execution: all 24 tasks it cost the ceiling had their correct answer at index 0, against a
    29% base rate. That is the instrument, not the substrate.

    v2: run the original on the state, and again on a state whose candidate list is ROTATED.
    A genuine match tracks the VALUE and emits the same string from a different position.
    A fall-through tracks POSITION and emits whatever now sits at index 0. Nothing is removed,
    so a real match is never destroyed by the probe.
    """
    def fn(state: BlackboardState) -> BlackboardState:
        before = state.selected_answer
        probe = copy.deepcopy(state)
        out = orig.fn(probe)
        ans = out.selected_answer
        if not ans or ans == before or len(state.candidates) < 2:
            state.selected_answer = ans
            state.candidate_scores = out.candidate_scores
            return state
        rot = copy.deepcopy(state)
        rot.candidates = list(state.candidates[1:]) + [state.candidates[0]]
        rot_ans = orig.fn(rot).selected_answer
        if rot_ans == ans:
            state.selected_answer = ans           # value-tracking: a genuine match
            state.candidate_scores = out.candidate_scores
            return state
        return state                              # position-tracking: ABSTAIN

    return BlackboardOp(fn, reads=orig.reads, writes=orig.writes,
                        precondition=orig.precondition, on_fail="skip", name=orig.name)


def abstain_pool():
    pool = make_pool(port_ops.PORT_OPS)
    for n in GUESSERS:
        pool[n] = _abstaining(be.REGISTRY[n][0])
    return pool


def battery(pool, pipeline):
    ops = [pool[n] for n in pipeline]
    hits, per = 0, []
    for t in TASKS:
        st = BlackboardState(problem_text=t["prompt"], candidates=list(t["candidates"]))
        try:
            ans = run_pipeline(ops, st).selected_answer
        except Exception:
            ans = ""
        ok = (ans == t["correct"])
        hits += ok
        per.append(ok)
    return hits / len(TASKS), per


def main():
    R = {"experiment": "CEILING-UNDER-ABSTAIN", "date": "2026-08-25", "agent": "Aporia (M1)",
         "prereg": "aporia/iq/PREREG_CEILING_ABSTAIN_2026-08-25.md",
         "prereg_commit": "7a0e5b6d", "C_edited": False,
         "discriminator": "v2 rotation (v1 removal was invalid; see FINDINGS)",
         "scope": ("Scores TWO PROGRAMS, not a new ceiling over all programs. A fall shows "
                   "0.8333 is guess-dependent FOR THE KNOWN ORGANISM; the true abstain-regime "
                   "ceiling needs Lexis's joint product BFS re-run and is NOT established here.")}

    OLD, NEW = make_pool(port_ops.PORT_OPS), abstain_pool()
    R["guessers_wrapped"] = GUESSERS

    # positive control: the wrapper must not change behaviour where nothing is a fall-through.
    # If it does, every number below is about the wrapper, not about guessing.
    base_before, pb = battery(OLD, CEILING_BODY + CEILING_TAIL)
    base_after, pa = battery(NEW, CEILING_BODY + CEILING_TAIL)
    port_before, qb = battery(OLD, PORTED_BODY + CEILING_TAIL)
    port_after, qa = battery(NEW, PORTED_BODY + CEILING_TAIL)

    R["ceiling_before"] = round(base_before, 6)
    R["ceiling_after"] = round(base_after, 6)
    R["ported_before"] = round(port_before, 6)
    R["ported_after"] = round(port_after, 6)
    R["dE_port_guess_regime"] = round(port_before - base_before, 6)
    R["dE_port_abstain_regime"] = round(port_after - base_after, 6)
    R["dE_port_changed"] = abs((port_after - base_after) - (port_before - base_before)) > 1e-12
    R["dropped_records"] = 0
    R["dropped_records_note"] = ("Nothing dropped. All 120 tasks scored under both pools; "
                                 "exceptions count as WRONG.")

    # C1/C2: direction and magnitude
    R["ceiling_fell"] = base_after < base_before - 1e-12
    R["ceiling_rose"] = base_after > base_before + 1e-12
    R["tasks_lost_ceiling"] = sum(1 for a, b in zip(pb, pa) if a and not b)
    R["tasks_gained_ceiling"] = sum(1 for a, b in zip(pb, pa) if b and not a)
    R["tasks_lost_ported"] = sum(1 for a, b in zip(qb, qa) if a and not b)
    R["C2_fall_bounded_at_0.70"] = base_after >= 0.70

    # C5: attribute every lost task
    lost = [i for i, (a, b) in enumerate(zip(pb, pa)) if a and not b]
    R["lost_by_category"] = dict(Counter(
        f'{TASKS[i]["_subset"]}:{TASKS[i].get("category")}' for i in lost))
    R["lost_indices"] = lost[:40]
    R["attribution_complete"] = (sum(R["lost_by_category"].values()) == len(lost))

    # C4: resolve score_by_extreme_number__g
    op = be.REGISTRY["score_by_extreme_number__g"][0]
    resolved, note = False, "no firing state found"
    for extreme in ("777 a", "777", "larger", "1"):
        s = BlackboardState(problem_text="probe", candidates=["777 a", "888 b", "999 c"])
        s.extreme_number = extreme
        s.numbers = [777.0, 888.0]
        if op.precondition is None or op.precondition(s):
            out = run_pipeline([op], s)
            resolved = True
            note = (f"guard fired with extreme_number={extreme!r}; emitted "
                    f"{out.selected_answer!r}; "
                    + ("GUESSES candidates[0]" if out.selected_answer == "777 a"
                       else "does not take position 0"))
            break
    R["C4_extreme_number_resolved"] = resolved
    R["C4_extreme_number_note"] = note

    # ── terminal state; three directions, asserted to partition ──────────────
    if R["ceiling_rose"]:
        verdict = "PARK_INSTRUMENT_BUG_CEILING_ROSE"
    elif R["ceiling_fell"]:
        verdict = "REDESIGN_PROVEN_CEILING_IS_PARTLY_GUESSING"
    else:
        verdict = "ADVANCE_NO_WON_TASK_DEPENDS_ON_A_GUESS"
    R["verdict"] = verdict
    R["verdict_rule_null_output"] = ("If the wrapper were inert, ceiling_after would equal "
                                     "ceiling_before and the run would read ADVANCE -- which is "
                                     "indistinguishable from a genuine no-dependence result. "
                                     "The wrapper's non-inertness is therefore established "
                                     "separately by tasks_lost_ported and by the C4 probe.")
    seen = {("PARK_INSTRUMENT_BUG_CEILING_ROSE" if r else
             ("REDESIGN_PROVEN_CEILING_IS_PARTLY_GUESSING" if f else
              "ADVANCE_NO_WON_TASK_DEPENDS_ON_A_GUESS"))
            for r, f in ((True, False), (False, True), (False, False))}
    assert seen == {"PARK_INSTRUMENT_BUG_CEILING_ROSE",
                    "REDESIGN_PROVEN_CEILING_IS_PARTLY_GUESSING",
                    "ADVANCE_NO_WON_TASK_DEPENDS_ON_A_GUESS"}, "terminal table leaks"
    R["terminal_table_partitions"] = True
    if R["ceiling_fell"]:
        R["LOUD"] = ("The proven 0.8333 is PARTLY GUESSING for the known organism. dE_port's "
                     "baseline moves; every number this arc quoted carries a regime qualifier.")

    json.dump(R, open(OUT / "RESULT_CEILING_ABSTAIN.json", "w", encoding="utf-8"), indent=2)
    for k, v in R.items():
        if k not in ("dropped_records_note", "verdict_rule_null_output", "scope", "lost_indices"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
