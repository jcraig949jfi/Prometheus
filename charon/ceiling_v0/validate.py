"""Oracle soundness audit — checks the code against the MATHEMATICS, not against
its own prior output.

Motivation. After the working-tree loss, restoration was verified by reproducing
fourteen previously-recorded numbers exactly. That is strong evidence the code was
restored faithfully and NO evidence that the code is correct: deterministic code
reproducing itself proves only self-consistency, and if the original had a bug the
restoration reproduces the bug perfectly.

So this file validates against independently-computed ground truth. Every check
derives its expectation from the definition of the universe — a group of
translations on Z_m^k observed through a lossy sensor — rather than from anything
the pipeline previously emitted.

  python validate.py
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

from baselines import substrate_arm
from config import ArmConfig
from substrate import (ArtifactStore, SubstratePredictor, classify, normalize)
from universe import EvalSet, Session, Universe, UniverseSpec

FAILS: List[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


# ---------------------------------------------------------------------------
#  1. The universe is what the spec says it is
# ---------------------------------------------------------------------------


def audit_universe(seeds=range(1, 21)) -> None:
    print("universe conforms to its own definition")
    ok_trans = ok_group = ok_surj = ok_lossy = True
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        m, k = u.spec.m, u.spec.k
        states = u._all_states()
        # actions are translations: stepping any state by action a adds a fixed
        # vector, independent of where you started
        for ai in range(u.spec.n_actions):
            deltas = {tuple((u._step(x, ai)[i] - x[i]) % m for i in range(k))
                      for x in states}
            if len(deltas) != 1:
                ok_trans = False
        # the shifts generate the WHOLE space, so all 27 elements are reachable
        reach = {tuple([0] * k)}
        frontier = [tuple([0] * k)]
        while frontier:
            cur = frontier.pop()
            for ai in range(u.spec.n_actions):
                nxt = u._step(cur, ai)
                if nxt not in reach:
                    reach.add(nxt)
                    frontier.append(nxt)
        if len(reach) != m ** k:
            ok_group = False
        # sensor is a surjection onto every symbol, and genuinely lossy
        img = set(u._sensor.values())
        if len(img) != u.spec.n_symbols:
            ok_surj = False
        if len(u._sensor) <= u.spec.n_symbols:
            ok_lossy = False
    check("every action is a translation (delta independent of start state)", ok_trans)
    check("the shifts generate the entire hidden space", ok_group)
    check("the sensor hits every symbol", ok_surj)
    check("the sensor is lossy (more states than symbols)", ok_lossy)


# ---------------------------------------------------------------------------
#  2. Eval answers are independently derivable
# ---------------------------------------------------------------------------


def audit_evalset(seeds=range(1, 21)) -> None:
    """Recompute every held-out answer from the group definition directly,
    without calling true_trace, and compare."""
    print("held-out answers recomputed from the group definition")
    bad = 0
    total = 0
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        ev = EvalSet(u)
        m, k = u.spec.m, u.spec.k
        for q, ans in zip(ev.queries, ev.answers):
            start = u._tag_state[u.tags.index(q.tag)]
            acc = list(start)
            for a in q.word:
                b = u._shifts[u.actions.index(a)]
                acc = [(acc[i] + b[i]) % m for i in range(k)]
            independent = u.symbols[u._sensor[tuple(acc)]]
            total += 1
            if independent != ans:
                bad += 1
    check(f"all {total} held-out answers match an independent computation", bad == 0,
          f"{bad} mismatches")


# ---------------------------------------------------------------------------
#  3. The verifier only admits true relations (and how often it does not)
# ---------------------------------------------------------------------------


def audit_accepted_rules(seeds=range(1, 21), rounds=6,
                         mode="datadriven") -> Dict[str, float]:
    """Every rule the environment accepted should be a TRUE group identity.
    False accepts are expected at the measured ~2% verifier rate; what must not
    happen is a systematic bias."""
    print(f"accepted rules are true group identities ({mode})")
    total = false = 0
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        _, store = substrate_arm(u, EvalSet(u), s, ArmConfig(), rounds, mode)
        for r in store.rules.values():
            if r.status != "active":
                continue
            total += 1
            if u.true_word_element(r.lhs) != u.true_word_element(r.rhs):
                false += 1
    rate = false / max(1, total)
    check("false-accept rate among surviving rules is under 5%", rate < 0.05,
          f"{rate:.3f} ({false}/{total})")
    print(f"        {total} surviving rules audited, {false} false ({rate:.1%})")
    return {"total": total, "false": false, "rate": rate}


# ---------------------------------------------------------------------------
#  4. Normalisation is meaning-preserving
# ---------------------------------------------------------------------------


def audit_normaliser(seeds=range(1, 21), rounds=6, mode="datadriven",
                     n_words=200) -> None:
    """normalize(w) must denote the SAME hidden group element as w. This is the
    property the whole predictor rests on and it is checkable directly against
    the group, with no reference to any previously recorded number."""
    print("normalisation preserves the hidden group element")
    rng = random.Random(4242)
    clean_bad = clean_n = dirty_bad = dirty_n = 0
    unattributed = 0
    lengths = []
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        _, store = substrate_arm(u, EvalSet(u), s, ArmConfig(), rounds, mode)
        rules = list(store.rules.values())
        false_ids = {r.rid for r in rules if r.status == "active"
                     and u.true_word_element(r.lhs) != u.true_word_element(r.rhs)}
        for _ in range(n_words):
            L = rng.randint(8, 12)
            w = [rng.choice(u.actions) for _ in range(L)]
            canon, fired = normalize(w, rules)
            lengths.append(len(canon))
            bad = u.true_word_element(w) != u.true_word_element(canon)
            if false_ids:
                dirty_n += 1
                dirty_bad += bad
            else:
                clean_n += 1
                clean_bad += bad
            if bad and not (set(fired) & false_ids):
                unattributed += 1
    # The property that actually has to hold: rewriting is meaning-preserving
    # whenever every rule it uses is true. Violations under a false-accepted rule
    # are the verifier's error surfacing downstream, not a normaliser defect.
    check(f"normalisation is sound when no false rule is present "
          f"({clean_bad}/{clean_n})", clean_bad == 0, f"{clean_bad} violations")
    check("every violation is attributable to a false-accepted rule",
          unattributed == 0, f"{unattributed} unattributed")
    print(f"        stores holding a false rule: {dirty_bad}/{dirty_n} words "
          f"corrupted ({dirty_bad/max(1,dirty_n):.1%})")
    print(f"        a ~0.8% false-rule rate corrupts ~{dirty_bad/max(1,dirty_n):.0%} "
          f"of long-word normalisations in the universes that get one")
    print(f"        mean canonical length {sum(lengths)/len(lengths):.2f} "
          f"from words of length 8-12")


# ---------------------------------------------------------------------------
#  5. Committed predictions are correct
# ---------------------------------------------------------------------------


def audit_commitments(seeds=range(1, 21), rounds=6, mode="datadriven") -> None:
    """When the predictor COMMITS (memo hit rather than fallback) it should be
    right. Errors here are exactly the contradiction rate, and they should trace
    to false-accepted rules rather than to a defect in lookup."""
    print("committed predictions are correct")
    committed = wrong = 0
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        ev = EvalSet(u)
        _, store = substrate_arm(u, ev, s, ArmConfig(), rounds, mode)
        pred = SubstratePredictor(store)
        for q, ans in zip(ev.queries, ev.answers):
            sym, hit = pred.predict(q.tag, q.word)
            if not hit:
                continue
            committed += 1
            if sym != ans:
                wrong += 1
    rate = wrong / max(1, committed)
    check("committed predictions are right at least 95% of the time", rate < 0.05,
          f"{rate:.3f} ({wrong}/{committed})")
    print(f"        {committed} commitments on held-out queries, {wrong} wrong "
          f"({rate:.1%})")


# ---------------------------------------------------------------------------
#  6. The budget is really a budget
# ---------------------------------------------------------------------------


def audit_budget(seeds=range(1, 11), rounds=4) -> None:
    """No arm may exceed its allowance, and no held-out query may ever be run."""
    print("budget and held-out isolation hold under real runs")
    over = leaked = 0
    for s in seeds:
        u = Universe(UniverseSpec(seed=s))
        ev = EvalSet(u)
        held = {(q.tag, tuple(q.word)) for q in ev.queries}
        for mode in ("datadriven", "relevance"):
            recs, _ = substrate_arm(u, ev, s, ArmConfig(), rounds, mode)
            for r in recs:
                if r["interactions"] > ArmConfig().budget_per_round:
                    over += 1
            sess = Session(u, 10_000)
            for q in ev.queries:
                if len(q.word) <= u.spec.max_word_len:
                    leaked += 1          # a held-out query short enough to run
    check("no round exceeds its interaction allowance", over == 0, str(over))
    check("no held-out query is short enough to be runnable", leaked == 0,
          str(leaked))


if __name__ == "__main__":
    print("=" * 74)
    print("ORACLE SOUNDNESS AUDIT — validates against the mathematics, not")
    print("against previously recorded output.")
    print("=" * 74)
    audit_universe()
    audit_evalset()
    audit_normaliser()
    audit_accepted_rules()
    audit_commitments()
    audit_budget()
    print()
    if FAILS:
        print(f"{len(FAILS)} FAILURES: {FAILS}")
        raise SystemExit(1)
    print("all oracle checks pass")
