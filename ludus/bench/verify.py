"""Rules-fidelity gate. Runs BEFORE any circuit is allowed to touch a world.

The discipline this enforces: **world implementation and strategic interpretation
stay separate.** First establish that the simulator reproduces the rules. Only
then let a circuit hypothesis near it. Otherwise a bug in the transition function
and a discovery about strategy arrive in the same number, and there is no way to
tell them apart afterwards.

Everything here is a rules-conformance property. Not one of these checks knows
what a good move is, and none of them may ever be relaxed because a circuit would
score better if it were.

Two tiers:

  UNIVERSAL   properties any world in this bench must satisfy whatever its rules:
              probabilities normalise, the state graph is acyclic and finite,
              banking is well defined, death is reachable-or-declared-absent.
  PER-WORLD   invariants specific to the world's stated rules, written from the
              rules text and checkable without reference to strategy.

A world that fails is marked UNVERIFIED in the atlas and its circuit rows are
suppressed. It is not deleted: a world whose simulator disagrees with its own
rules is a finding about the implementation, and the failure is the record of it.

WHAT THIS GATE CANNOT DO, stated so a VERIFIED stamp is never over-read. It checks
the simulator against **the rules as this seat wrote them down**. It cannot check
those rules against the actual published game, because it has no access to one.
So VERIFIED means *internally consistent*, never *faithful*. A world can pass
every check here and still model a game nobody plays -- if Martian Dice has one
ray face rather than two, every invariant below still holds and every conclusion
drawn from the world is still wrong.

Fidelity to the real game is a separate gate with a different instrument: the
operator, via `ludus/bench/RULES_AUDIT.md`. The two must not be conflated, and a
VERIFIED world whose audit is outstanding is reported as
`verified_internally=True, rules_audited=False`.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ==========================================================================
# Universal properties
# ==========================================================================

def check_universal(cw, tol: float = 1e-9) -> list:
    """Properties every bench world must satisfy regardless of its rules."""
    fails = []
    n_death, n_dec = 0, 0
    for s, rows in cw.trans.items():
        if cw.forced[s]:
            if rows:
                fails.append(f"{s!r}: forced_end state has outgoing draws")
            continue
        if not rows:
            fails.append(f"{s!r}: non-terminal state has no draws")
            continue
        tot = sum(p for p, _ in rows)
        if abs(tot - 1.0) > 1e-7:
            fails.append(f"{s!r}: draw probabilities sum to {tot!r}, not 1")
        for p, opts in rows:
            if p < -tol:
                fails.append(f"{s!r}: negative probability {p}")
            if not opts:
                n_death += 1
            elif len(opts) > 1:
                n_dec += 1
            for s2 in opts:
                if s2 not in cw.pot:
                    fails.append(f"{s!r}: option {s2!r} was never compiled")
    if cw.initial not in cw.pot:
        fails.append("initial state absent from the compiled table")
    return fails


def check_acyclic(cw) -> list:
    """A cyclic episode graph makes backward induction meaningless, and the
    solver's memo guard would silently return the zero it seeded instead of
    diverging. That is a wrong answer that looks like an answer."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {}
    fails = []
    stack = [(cw.initial, iter([o for _, opts in cw.trans.get(cw.initial, ())
                                for o in opts]))]
    colour[cw.initial] = GREY
    while stack:
        node, it = stack[-1]
        advanced = False
        for nxt in it:
            c = colour.get(nxt, WHITE)
            if c == GREY:
                fails.append(f"cycle detected through {nxt!r}")
                return fails
            if c == WHITE:
                colour[nxt] = GREY
                stack.append((nxt, iter([o for _, opts in cw.trans.get(nxt, ())
                                         for o in opts])))
                advanced = True
                break
        if not advanced:
            colour[node] = BLACK
            stack.pop()
    return fails


# ==========================================================================
# Per-world invariants, written from the rules text only
# ==========================================================================

def check_flip7(cw) -> list:
    from ludus.bench.worlds import F7_COUNTS
    fails = []
    for s in cw.pot:
        if len(s) != len(set(s)):
            fails.append(f"{s!r}: a rank is held twice; a duplicate must bust")
        expect = sum(s) + (15 if len(s) >= 7 else 0)
        if abs(cw.pot[s] - expect) > 1e-9:
            fails.append(f"{s!r}: pot {cw.pot[s]} != sum+bonus {expect}")
        if len(s) > 7:
            fails.append(f"{s!r}: more than 7 ranks held; the round must have ended")
        for r in s:
            if r not in F7_COUNTS:
                fails.append(f"{s!r}: rank {r} is not in the deck")
    return fails


def check_incan(cw) -> list:
    from ludus.bench.worlds import IG_TOTAL, IG_TREASURES
    fails = []
    base = sorted(IG_TREASURES)
    for s in cw.pot:
        rem, mask = s
        if sorted(rem) != sorted(x for x in base if _multiset_ok(rem, base)):
            pass                                   # checked below by containment
        if not _is_submultiset(rem, base):
            fails.append(f"{s!r}: remaining treasures are not a sub-multiset of the deck")
        if abs(cw.pot[s] - (IG_TOTAL - sum(rem))) > 1e-9:
            fails.append(f"{s!r}: pot != total minus remaining")
        if mask < 0 or mask > 31:
            fails.append(f"{s!r}: hazard mask out of range")
    return fails


def _is_submultiset(a, b) -> bool:
    import collections
    ca, cb = collections.Counter(a), collections.Counter(b)
    return all(ca[k] <= cb[k] for k in ca)


def _multiset_ok(a, b):
    return True


def check_martian(cw) -> list:
    from ludus.bench.worlds import MD_DICE
    fails = []
    for s in cw.pot:
        tanks, rays, h, c, ch = s
        if sum(s) > MD_DICE:
            fails.append(f"{s!r}: more than {MD_DICE} dice set aside")
        if any(x < 0 for x in s):
            fails.append(f"{s!r}: negative die count")
        expect = 0.0 if rays < tanks else float(h + c + ch + (3 if h and c and ch else 0))
        if abs(cw.pot[s] - expect) > 1e-9:
            fails.append(f"{s!r}: pot {cw.pot[s]} != rules score {expect}")
    # a claimed symbol always has a non-zero count, which is what collapses the
    # claim mask into the counts; if that ever fails the state is not Markov
    for s, rows in cw.trans.items():
        for _, opts in rows:
            for s2 in opts:
                if sum(1 for i in range(1, 5) if s2[i] > 0) < sum(
                        1 for i in range(1, 5) if s[i] > 0):
                    fails.append(f"{s!r}->{s2!r}: a claimed symbol lost its count")
    return fails


def check_cantstop(cw) -> list:
    from ludus.bench.worlds import CS_HEIGHTS, CS_RUNNERS
    fails = []
    for s in cw.pot:
        if len(s) > CS_RUNNERS:
            fails.append(f"{s!r}: more than {CS_RUNNERS} runners")
        cols = [c for c, _ in s]
        if len(cols) != len(set(cols)):
            fails.append(f"{s!r}: two runners on one column")
        for col, st in s:
            if col not in CS_HEIGHTS:
                fails.append(f"{s!r}: column {col} does not exist")
            elif st > CS_HEIGHTS[col]:
                fails.append(f"{s!r}: column {col} advanced past its height")
            elif st < 1:
                fails.append(f"{s!r}: a placed runner has no progress")
        expect = sum(st / CS_HEIGHTS[c] for c, st in s if c in CS_HEIGHTS)
        if abs(cw.pot[s] - expect) > 1e-9:
            fails.append(f"{s!r}: pot != summed column fractions")
    # every advance moves exactly one or two steps: the rules allow at most two
    for s, rows in cw.trans.items():
        for _, opts in rows:
            for s2 in opts:
                d = sum(dict(s2).values()) - sum(dict(s).values())
                if d not in (1, 2):
                    fails.append(f"{s!r}->{s2!r}: advanced {d} steps, not 1 or 2")
    return fails


PER_WORLD = {"FLIP7": check_flip7, "INCAN_GOLD": check_incan,
             "MARTIAN_DICE": check_martian, "CANT_STOP": check_cantstop}


# ==========================================================================

def verify(world, cw) -> dict:
    fails = {"universal": check_universal(cw), "acyclic": check_acyclic(cw)}
    fn = PER_WORLD.get(world.name)
    fails["per_world"] = fn(cw) if fn else ["NO PER-WORLD INVARIANTS WRITTEN"]
    total = sum(len(v) for v in fails.values())
    return {"world": world.name,
            "verified_internally": total == 0,
            "rules_audited": False,
            "verified_meaning": "simulator matches the rules AS WRITTEN BY THE "
                                "SEAT; it does NOT establish those rules match "
                                "the published game - see RULES_AUDIT.md",
            "n_failures": total,
            "failures": {k: v[:8] for k, v in fails.items() if v},
            "n_states": cw.n_states, "ts_utc": _now(),
            "note": "rules fidelity only; nothing here knows what a good move is"}


def main() -> None:
    from ludus.bench.compiled import compile_world
    from ludus.bench.worlds import ALL_WORLDS
    ATLAS.mkdir(parents=True, exist_ok=True)
    out = {"artifact": "rules-fidelity gate", "ts_utc": _now(), "worlds": {}}
    for w in ALL_WORLDS:
        cw = compile_world(w)
        r = verify(w, cw)
        out["worlds"][w.name] = r
        flag = ("VERIFIED-INTERNALLY (rules unaudited)" if r["verified_internally"]
                else f"FAILED ({r['n_failures']})")
        print(f"{w.name:14s} {flag}")
        for k, v in r.get("failures", {}).items():
            for line in v[:4]:
                print(f"    [{k}] {line}")
    (ATLAS / "rules_fidelity.json").write_text(json.dumps(out, indent=2),
                                               encoding="utf-8")
    print(f"\nwrote {ATLAS / 'rules_fidelity.json'}")


if __name__ == "__main__":
    main()
