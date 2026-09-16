"""LUDUS-03: the previously unrun control halves of the qualification
instruments, with rows.

Run from the repository root:  PYTHONPATH=. python ludus/controls/run_controls.py

Every row records the instrument, the control kind, the injected fixture,
the reading EXPECTED before the run, the reading OBSERVED, and whether the
instrument's behaviour matched. A row where the instrument does NOT detect
an injected defect is reported as MISSED with the same weight as a DETECTED
row; the point of the exercise is the map of what each instrument cannot
see, not a green table.

Control kinds (base role section 2):
  negative   the instrument does not hallucinate signal on a null specimen
  positive   the instrument detects known real structure
  cheat      success or a defect is deliberately injected; does the
             instrument's measurement channel see it
  specimen   a NEW specimen the instrument was not written against: does it
             collapse loudly (acceptable) or silently (a defect)
  regression the instrument reproduces its committed readings

No model calls. Deterministic given the seeds in the instruments.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ludus" / "arena"))

from ludus.controls import fixtures as F                    # noqa: E402

ROWS = []


def row(instrument, kind, fixture, injected, expected, observed, matched, note=""):
    r = {"instrument": instrument, "kind": kind, "fixture": fixture,
         "injected": injected, "expected": expected, "observed": observed,
         "instrument_behaved_as_expected": bool(matched), "note": note}
    ROWS.append(r)
    flag = "ok " if matched else "!! "
    print("  %s[%-9s] %-28s expected=%s observed=%s" % (
        flag, kind, fixture, expected, observed))
    return r


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, timeout=60).stdout.strip()
    except Exception as e:                                       # noqa: BLE001
        return "ERR:%s" % e


# ==========================================================================
# A. depth profile (r0002) and GATE-W1
# ==========================================================================

def controls_depth_profile():
    from ludus.depth_profile import profile
    from ludus.worlds import WORLDS, optimal_actions, reachable_states
    print("\n[A] DEPTH PROFILE / GATE-W1  (gap(k=4) >= 0.20 admits)")

    # regression: the committed 2026-08-26 readings
    committed = json.loads((ROOT / "ludus" / "ledgers" /
                            "cycle001_r0002_depth_profile.json").read_text("utf-8"))
    for name, w in WORLDS.items():
        p = profile(w)
        want = committed["worlds"][name]["gaps"]
        row("depth_profile", "regression", name, "none (own_score hook added)",
            want, p["gaps"], p["gaps"] == want,
            "the hook must not move any existing world's curve")

    # negative: greedy-decidable by construction
    p = profile(F.Ledger())
    row("depth_profile", "negative", "CTRL_LEDGER",
        "optimal set == greedy set at every state",
        {"k=1": 0.0, "k=2": 0.0, "k=3": 0.0, "k=4": 0.0},
        p["gaps"], all(v == 0.0 for v in p["gaps"].values()),
        "eligible=%d sampled=%d survives_depth=%s" % (
            p["eligible_states"], p["sampled"], p["survives_depth"]))

    # positive: deferred payoff invisible to the cutoff eval
    p = profile(F.Orchard())
    row("depth_profile", "positive", "CTRL_ORCHARD",
        "payoff deferred to the terminal state; PLANT optimal, GRAB greedy",
        "gap(4) >= 0.20, curve decreasing in k", p["gaps"],
        p["gap_at_max_depth"] >= 0.20
        and list(p["gaps"].values()) == sorted(p["gaps"].values(), reverse=True),
        "eligible=%d sampled=%d; LIMIT: PLANT-always is a constant policy, so "
        "this proves detection of deferred payoff, not of reasoning" % (
            p["eligible_states"], p["sampled"]))

    # cheat: a world a four-line closed form solves
    for heaps, n in (((3, 4, 5), 10_000), ((3, 4, 5, 6), 250)):
        w = F.Nim345(heaps)
        p = profile(w, n=n)
        sampled = profile(w) if n != 250 else p
        states = [s for s in reachable_states(w) if len(w.legal_actions(s)) >= 2]
        n_pos = [s for s in states if F.bouton_action(s) is not None]
        hits = sum(1 for s in n_pos if F.bouton_action(s) in optimal_actions(w, s))
        bouton_rate = hits / len(n_pos) if n_pos else None
        admitted = p["gap_at_max_depth"] >= 0.20
        row("depth_profile", "cheat", "CTRL_NIM%s" % "".join(map(str, heaps)),
            "normal-play Nim %s; Bouton's 4-line xor rule plays it perfectly"
            % (heaps,),
            "gate ADMITS (gap(4) >= 0.20) although a 4-line rule is optimal",
            {"gaps": p["gaps"], "sampled": p["sampled"],
             "eligible": p["eligible_states"], "admitted": admitted,
             "gaps_at_default_n250": sampled["gaps"],
             "bouton_optimal_rate_on_N_positions": bouton_rate,
             "n_positions": len(n_pos)},
            admitted and bouton_rate == 1.0,
            "MISSED by construction: the gate's cheap-player class is depth-k "
            "search with the world's own eval; it does not contain short "
            "closed-form programs. Charter v3 s2 question 2 needs a second "
            "family. On (3,4,5) the default n=250 sample read gap(4)=0.200, "
            "ON the gate; the exhaustive 517-state reading is what is judged.")

    # specimen: a world with neither a known name nor own_score
    class Bare:
        name = "CTRL_BARE_UNKNOWN"
        _inner = F.Ledger()
        initial_state = _inner.initial_state
        legal_actions = _inner.legal_actions
        apply = _inner.apply
        is_terminal = _inner.is_terminal
        result = _inner.result
    try:
        # no own_score and no matching name: the TITHE branch reads .ta off
        # a PlyState
        profile(Bare())
        obs, loud = "returned a value", False
    except AttributeError as e:
        obs, loud = "AttributeError: %s" % e, True
    row("depth_profile", "specimen", "CTRL_BARE_UNKNOWN",
        "world with no own_score and a name no branch matches",
        "loud failure (exception), never a silent number", obs, loud)


# ==========================================================================
# B. bench verify (rules-fidelity gate)
# ==========================================================================

def controls_bench_verify():
    from ludus.bench import verify as V
    from ludus.bench.compiled import compile_world
    from ludus.bench.worlds import WORLD_BY_NAME
    print("\n[B] BENCH VERIFY  (universal + acyclic + per-world invariants)")

    md = WORLD_BY_NAME["MARTIAN_DICE"]
    cw = compile_world(md)
    base = V.verify(md, cw)
    row("bench_verify", "positive", "MARTIAN_DICE (as committed)", "none",
        "verified_internally=True", base["verified_internally"],
        base["verified_internally"] is True, "n_states=%d" % cw.n_states)

    cw2, s = F.corrupt_pot(cw)
    r = V.verify(md, cw2)
    row("bench_verify", "cheat", "MARTIAN_DICE pot+1 at %s" % (s,),
        "one pot value off by 1", "FAIL via per_world",
        {"verified": r["verified_internally"],
         "per_world_failures": len(r["failures"].get("per_world", []))},
        not r["verified_internally"] and r["failures"].get("per_world"))

    cw3, s, removed = F.corrupt_prob(cw, which="smallest")
    r = V.verify(md, cw3)
    row("bench_verify", "cheat", "MARTIAN_DICE smallest prob*0.5",
        "smallest draw probability of the initial state halved "
        "(mass removed %.3g; tolerance 1e-7)" % removed,
        "NOT detected: injection below the normalisation tolerance",
        {"verified": r["verified_internally"],
         "universal_failures": len(r["failures"].get("universal", []))},
        r["verified_internally"] is True,
        "MISSED by construction: the first injection tried; the perturbation "
        "was smaller than the check's own tolerance, so this row measures the "
        "instrument's floor (1e-7 of mass), not a defect. Eligibility first.")

    cw3, s, removed = F.corrupt_prob(cw, which="largest")
    r = V.verify(md, cw3)
    row("bench_verify", "cheat", "MARTIAN_DICE largest prob*0.5",
        "largest draw probability of the initial state halved "
        "(mass removed %.3g)" % removed,
        "FAIL via universal",
        {"verified": r["verified_internally"],
         "universal_failures": len(r["failures"].get("universal", []))},
        not r["verified_internally"] and r["failures"].get("universal"))

    cw4, s = F.inject_cycle(cw)
    r = V.verify(md, cw4)
    row("bench_verify", "cheat", "MARTIAN_DICE cycle via %s" % (s,),
        "an option of a successor points back at the initial state",
        "FAIL via acyclic",
        {"verified": r["verified_internally"],
         "acyclic_failures": len(r["failures"].get("acyclic", []))},
        not r["verified_internally"] and r["failures"].get("acyclic"))

    # cheat the instrument cannot see: a rule constant no invariant reads
    one_ray = F.martian_dice_one_ray()
    cw5 = compile_world(one_ray)
    r = V.verify(one_ray, cw5)
    row("bench_verify", "cheat", "MARTIAN_DICE one ray face (MD_W ray=1)",
        "the doubled ray face removed from the draw distribution",
        "verified_internally=True (instrument blind to the draw law)",
        {"verified": r["verified_internally"], "n_states": cw5.n_states,
         "n_states_committed": cw.n_states},
        r["verified_internally"] is True,
        "MISSED by construction: VERIFIED means internally consistent, never "
        "faithful (verify.py docstring). Only W3 (LUDUS-01) can see this.")

    # specimen: a world with no per-world invariants
    cw6 = compile_world(WORLD_BY_NAME["LUCKY_NUMBERS"]) \
        if "LUCKY_NUMBERS" in WORLD_BY_NAME else None
    if cw6 is not None:
        r = V.verify(WORLD_BY_NAME["LUCKY_NUMBERS"], cw6)
        row("bench_verify", "specimen", "LUCKY_NUMBERS (no invariants)",
            "a world absent from PER_WORLD",
            "FAIL loudly: NO PER-WORLD INVARIANTS WRITTEN",
            r["failures"].get("per_world"),
            r["failures"].get("per_world") == ["NO PER-WORLD INVARIANTS WRITTEN"],
            "archaeology L-1: loud, not silent; 17 of 21 worlds sit here")


# ==========================================================================
# C. arena verify [7] key-name check  and  D. differential leak audit
# ==========================================================================

def _dealt(world, mine, opp):
    st = world.new_initial_state(None)
    st.apply_action(mine)
    st.apply_action(opp)
    return st


def controls_arena_leaks():
    import audit
    import verify as AV
    import worlds as AW
    print("\n[C/D] ARENA LEAK INSTRUMENTS  ([7] key-name check; differential audit)")

    def keyname_fires(world):
        st = _dealt(world, 0, 2)
        return bool(AV.kuhn_keyname_leak(st.observation(0), st))

    def differential(world):
        leaks = []
        for mine in range(3):
            others = [c for c in range(3) if c != mine]
            a, b = _dealt(world, mine, others[0]), _dealt(world, mine, others[1])
            leaks += audit.probe_pair(a, b, player=0,
                                      label="p0=%s opp %s/%s " % (mine, *others))
        return leaks

    clean = AW.KuhnPoker()
    lk = differential(clean)
    row("arena_keyname_check", "negative", "KUHN_POKER (as committed)", "none",
        "does not fire", keyname_fires(clean), keyname_fires(clean) is False)
    row("arena_differential_audit", "negative", "KUHN_POKER (as committed)",
        "none", "0 leaks", len(lk), len(lk) == 0)

    cases = [
        (F.kuhn_leak_named_key(), "observation key opponent_card", True, True),
        (F.kuhn_leak_innocuous_key(), "observation key tiebreak", False, True),
        (F.kuhn_leak_action_order(), "legal_actions order flips on opp=K", False, True),
        (F.kuhn_leak_public_state(), "public_state carries both cards", False, True),
    ]
    for w, inj, exp_key, exp_diff in cases:
        kf = keyname_fires(w)
        lk = differential(w)
        chans = sorted({l.split(" ", 3)[3].split(":")[0] for l in lk})
        row("arena_keyname_check", "cheat", w.name, inj,
            "fires" if exp_key else "does not fire (key names only)", kf,
            kf == exp_key,
            "" if exp_key else "MISSED by construction: substring matching "
                               "cannot find a leak (standing rule 6)")
        row("arena_differential_audit", "cheat", w.name, inj,
            "fires", {"n_leaks": len(lk), "channels": chans},
            (len(lk) > 0) == exp_diff)


# ==========================================================================

def main():
    print("=" * 78)
    print("LUDUS-03 QUALIFICATION-INSTRUMENT CONTROLS")
    print("=" * 78)
    controls_depth_profile()
    controls_bench_verify()
    controls_arena_leaks()

    per = {}
    for r in ROWS:
        d = per.setdefault(r["instrument"], {"rows": 0, "as_expected": 0,
                                             "missed_by_construction": 0})
        d["rows"] += 1
        d["as_expected"] += int(r["instrument_behaved_as_expected"])
        d["missed_by_construction"] += int(r["note"].startswith("MISSED"))
    out = {
        "artifact": "LUDUS-03 qualification-instrument controls",
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_sha": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "worktree_path": str(ROOT),
        "dirty": bool(_git("status", "--porcelain", "--", "ludus")),
        "reading_guide": "instrument_behaved_as_expected=True on a row whose "
                         "note starts with MISSED means the instrument's "
                         "blind spot was predicted and confirmed, not that "
                         "the instrument passed.",
        "summary": per,
        "rows": ROWS,
    }
    path = ROOT / "ludus" / "controls" / "CONTROLS_2026-09-16.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    n_bad = sum(1 for r in ROWS if not r["instrument_behaved_as_expected"])
    print("\n" + "=" * 78)
    print("%d rows, %d behaved as expected, %d unexpected; wrote %s" % (
        len(ROWS), len(ROWS) - n_bad, n_bad, path))
    print("=" * 78)
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
