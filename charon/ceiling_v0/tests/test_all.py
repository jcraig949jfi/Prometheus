"""Guard tests. RESTORED 2026-08-22 (see RECOVERY.md).

Covers the deterministic half: determinism, scoring, budget, eval sealing,
artifact hygiene, verifier soundness, the solvable ceiling, wrong-artifact
removal, whole-pipeline reproducibility, and a frozen reference for every arm so
a future restoration can be checked the way this one was.

Leakage and ladder tests will return with prompts.py and arms.py; their absence
is recorded in the iteration log rather than silently skipped.

Run:  python tests/test_all.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baselines import (DataDrivenProposer, RelevanceProposer, SignatureAutomaton,
                       random_arm, state_merge_arm, substrate_arm)
from config import ArmConfig
from metrics import assay, l1_count_distance, suffix_overlap
from policy import probe_stream
from substrate import (ArtifactStore, SubstratePredictor, classify,
                       detect_surprise, harvest, normalize, submit_rule,
                       test_rule)
from universe import (BudgetExhausted, EvalSet, InteractionForbidden,
                      SealedSession, Session, Universe, UniverseSpec)

FAILS = []

# Substring ban list for leakage. Deliberately blunt: over-strict beats
# under-strict for a leakage guard. It once flagged "re-STATE", and the wording
# was changed rather than the guard weakened.
BANNED = [
    "state", "group", "modul", "matrix", "vector", "commut", " order",
    "parity", "symmetr", "invariant", "cyclic", "lattice", "algebra",
    "abelian", "translat", "shift", "latent", "coordinate", "dimension",
    "arithmetic", "addition", "modulo", "offset", "permut", "isomorph",
    "monoid", "semigroup", "linear", "affine", "mod ", "z_",
]


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        FAILS.append(name)


def mk(seed=1):
    return Universe(UniverseSpec(seed=seed))


def test_determinism():
    print("determinism")
    a, b, c = mk(7), mk(7), mk(8)
    check("same seed -> same shifts", a._shifts == b._shifts)
    check("same seed -> same sensor", a._sensor == b._sensor)
    check("same seed -> same entry points", a._tag_state == b._tag_state)
    check("different seed -> different laws",
          a._shifts != c._shifts or a._sensor != c._sensor)
    w = ["A1", "A3", "A0", "A2"]
    check("traces reproduce", a.true_trace("K2", w) == b.true_trace("K2", w))
    ea, eb = EvalSet(a), EvalSet(b)
    check("eval sets reproduce",
          [q.word for q in ea.queries] == [q.word for q in eb.queries]
          and ea.answers == eb.answers)
    check("generator covers the full hidden space",
          len(set(a._sensor.values())) == a.spec.n_symbols)


def test_sealing():
    print("eval sealing")
    uni = mk(4)
    ev = EvalSet(uni)
    check("held-out words exceed the probe cap",
          all(len(q.word) > uni.spec.max_word_len for q in ev.queries))
    check("prompt-facing length range matches the eval set",
          (ev.len_lo, ev.len_hi) ==
          (min(len(q.word) for q in ev.queries),
           max(len(q.word) for q in ev.queries)))
    try:
        SealedSession().run("K0", ["A0"])
        check("sealed session refuses interaction", False)
    except InteractionForbidden:
        check("sealed session refuses interaction", True)


def test_budget_and_scoring():
    print("budget and scoring")
    uni = mk(5)
    s = Session(uni, 3)
    for _ in range(3):
        s.run("K0", ["A0"])
    try:
        s.run("K0", ["A0"])
        check("budget is hard", False)
    except BudgetExhausted:
        check("budget is hard", True)
    check("over-long probes refused", not s.try_run("K0", ["A0"] * 99)[0])
    check("unknown tokens refused", not Session(uni, 2).try_run("K0", ["A99"])[0])

    ev = EvalSet(uni)
    check("perfect predictions score 1.0", ev.score(ev.answers)[0] == 1.0)
    check("wrong predictions score 0.0", ev.score(["zzz"] * len(ev))[0] == 0.0)
    sym, mj = ev.majority_baseline()
    check("majority baseline is sane", 0.2 <= mj <= 0.6, f"{mj:.2f}")


def test_artifacts():
    print("artifact isolation and hygiene")
    check("non-decreasing rules refused", classify(["A0"], ["A1", "A2"]) is None)
    check("equal-length lex rules accepted",
          classify(["A1", "A0"], ["A0", "A1"]) == "order")
    check("reducing rules accepted", classify(["A0", "A0"], []) == "reduce")
    check("empty lhs refused", classify([], []) is None)

    s = ArtifactStore()
    r = s.add_rule(["A0", "A0"], ["A1"], "reduce", "llm", 1)
    s.remember("K0", ["A1"], "q2", [r.rid])
    check("store round-trips", ArtifactStore.from_json(s.to_json()).to_json()
          == s.to_json())
    c = s.clone()
    c.rules[r.rid].status = "rejected"
    check("clone is independent", s.rules[r.rid].status == "active")

    s.demote(r.rid)
    check("demotion purges dependent memo", len(s.memo) == 0)
    s.remember("K1", ["A0"], "q1", [], src="c4_fact_wrong")
    check("memo records what caused the observation to be paid for",
          s.memo["K1|A0"]["src"] == "c4_fact_wrong")

    adv = ArtifactStore()
    adv.add_rule(["A0", "A1"], ["A1", "A0"], "order", "x", 1)
    adv.add_rule(["A1", "A0"], ["A0", "A1"], "order", "x", 1)
    out, _ = normalize(["A0", "A1"] * 8, list(adv.rules.values()))
    check("normalisation terminates under adversarial rules", isinstance(out, list))

    oid = s.define_op(["A0", "A1"], 1)
    check("op provenance resolves to primitives",
          s.expand([oid, "A2"]) == ["A0", "A1", "A2"])
    try:
        s.expand(["OP_999"])
        check("unknown op rejected", False)
    except ValueError:
        check("unknown op rejected", True)


def test_ignorance_vs_error():
    print("ignorance instrumented separately from error")
    uni = mk(9)
    store = ArtifactStore()
    rng = random.Random(0)
    sess = Session(uni, 400)
    stream = probe_stream(uni, rng)
    for _ in range(60):
        tag, w = next(stream)
        detect_surprise(store, tag, w, uni.true_final_symbol(tag, w))
        sess.run(tag, w)
        harvest(store, sess.log[-1])
    c = store.counters
    check("every probe is classified",
          c["probes_seen"] == c["probes_ignorant"] + c["probes_committed"])
    check("the store commits on some probes", c["probes_committed"] > 0)
    check("a verification-gated store is never wrong, only ignorant",
          c["probes_wrong"] == 0,
          f"{c['probes_wrong']} contradictions in {c['probes_committed']}")


def test_verifier():
    print("verifier soundness (the environment is the only judge)")
    tp = tt = fp = ft = 0
    for seed in range(6):
        uni = mk(100 + seed)
        rng = random.Random(seed)
        sess = Session(uni, 100_000)
        for _ in range(60):
            la = rng.randint(1, 3)
            lb = rng.randint(0, la - 1) if la > 1 else 0
            lhs = [rng.choice(uni.actions) for _ in range(la)]
            rhs = [rng.choice(uni.actions) for _ in range(lb)]
            if classify(lhs, rhs) is None:
                continue
            truly = uni.true_word_element(lhs) == uni.true_word_element(rhs)
            v, _ = test_rule(sess, lhs, rhs, rng, n_contexts=3)
            if v is None:
                continue
            if truly:
                tt += 1
                tp += int(v)
            else:
                ft += 1
                fp += int(v)
    fa = fp / max(1, ft)
    check("every true equivalence passes", tp == tt, f"{tp}/{tt}")
    check("false-accept rate under 5%", fa < 0.05, f"{fa:.3f}")
    print(f"        measured false-accept rate {fa:.3f} over {ft} false claims")


def test_solvable_ceiling():
    print("environment ceiling (is there anything to find?)")
    uni = mk(11)
    ev = EvalSet(uni)
    store = ArtifactStore()
    words = [[]]
    frontier = [[]]
    for _ in range(3):
        frontier = [w + [a] for w in frontier for a in uni.actions]
        words += frontier
    canon = {}
    for w in sorted(words, key=lambda w: (len(w), w)):
        canon.setdefault(uni.true_word_element(tuple(w)), w)
    for w in words:
        tgt = canon[uni.true_word_element(tuple(w))]
        k = classify(w, tgt)
        if w != tgt and k:
            store.add_rule(w, tgt, k, "oracle", 0)
    sess = Session(uni, 5000)
    stream = probe_stream(uni, random.Random(1))
    for _ in range(400):
        tag, w = next(stream)
        sess.run(tag, w)
        harvest(store, sess.log[-1])
    preds, cov = SubstratePredictor(store).predict_all(ev.queries)
    acc, _ = ev.score(preds)
    print(f"        oracle-rule substrate acc={acc:.2f} coverage={cov:.2f} "
          f"rules={len(store.active_rules())}")
    check("a good rule set really does solve held-out queries", acc >= 0.85,
          f"acc={acc:.2f}")


def test_wrong_artifacts_die():
    print("planted falsehoods are removed by environmental re-testing")
    uni = mk(21)
    recs, _ = substrate_arm(uni, EvalSet(uni), 21, ArmConfig(), 4,
                            "datadriven", inject_wrong=6)
    alive = recs[-1]["n_injected_alive"]
    print(f"        injected 6; still alive after 4 rounds: {alive}")
    check("selection removes planted falsehoods", alive <= 2, str(alive))


def test_pipeline_determinism():
    print("whole-pipeline reproducibility")
    uni, ev = mk(31), EvalSet(mk(31))
    a, sa = substrate_arm(uni, ev, 31, ArmConfig(), 3, "datadriven")
    b, sb = substrate_arm(uni, ev, 31, ArmConfig(), 3, "datadriven")
    check("identical records on a re-run", json.dumps(a) == json.dumps(b))
    check("identical artifact store on a re-run", sa.to_json() == sb.to_json())
    c, _ = substrate_arm(mk(32), EvalSet(mk(32)), 32, ArmConfig(), 3, "datadriven")
    check("a different universe gives different records",
          json.dumps(a) != json.dumps(c))


def test_cross_process_stability():
    """Set iteration over string tuples is hash-order dependent, which silently
    made P3b vary run to run. Any arm whose output depends on set order is not
    reproducible even at a fixed seed, so the property is asserted directly."""
    print("cross-process determinism (hash-order hazards)")
    import subprocess, sys as _s
    code = ("import sys; sys.path.insert(0,'.');"
            "from baselines import substrate_arm, state_merge_arm;"
            "from config import ArmConfig;"
            "from universe import Universe, UniverseSpec, EvalSet;"
            "u=Universe(UniverseSpec(seed=3)); e=EvalSet(u);"
            "a=substrate_arm(u,e,3,ArmConfig(),3,'relevance')[0][-1]['acc_post'];"
            "b=state_merge_arm(u,e,3,100,3)[-1]['acc_post'];"
            "print(f'{a:.6f},{b:.6f}')")
    outs = set()
    for seedenv in ("0", "1", "2"):
        r = subprocess.run([_s.executable, "-c", code], capture_output=True,
                           text=True, env={"PYTHONHASHSEED": seedenv, "PATH": ""},
                           cwd=str(Path(__file__).resolve().parents[1]))
        outs.add(r.stdout.strip())
    check("arms give identical results under different hash seeds",
          len(outs) == 1, str(outs))


def test_model_pipeline_offline():
    """The model pipeline must be proven working WITHOUT a lane, because a lane
    window is the scarce resource and iteration 5 lost one to a crash on an
    untested code path."""
    print("model pipeline, offline")
    import prompts as pr
    from arms import LLMArm, parse_claims, parse_answers, parse_runs
    from reasoner import ScriptedModel, extract_json
    uni = mk(41)
    ev = EvalSet(uni)
    reply = json.dumps({
        "runs": [{"tag": "K0", "seq": "A1 A2"}, {"tag": "K9", "seq": "A1"}],
        "claims": [{"lhs": "A1 A1", "rhs": "A2"}, {"lhs": "A1", "rhs": "A2 A3"}],
        "note": "n" * 4000})
    obj = extract_json(reply)
    check("json extracted", obj is not None and "claims" in obj)
    check("invalid run dropped, valid kept",
          parse_runs(obj, uni, None, 5) == [("K0", ["A1", "A2"])])
    cl = parse_claims(obj, uni, ArtifactStore(), 5)
    check("non-decreasing claim rejected at the parser",
          len(cl) == 1 and cl[0][0] == ["A1", "A1"])
    check("answers fall back when missing",
          parse_answers({"answers": {"0": "q1"}}, uni.symbols, [0, 1], "q0")
          == ["q1", "q0"])

    for cond in ("C0", "C1", "C1N", "C3", "C4"):
        a = LLMArm("P2", uni, ev, ScriptedModel([reply] * 20), ArmConfig(), 41,
                   condition=cond)
        sess = Session(uni, 60)
        for _ in range(12):
            t, w = next(a.stream)
            sess.run(t, w)
            a.absorb(sess.log[-1])
        text = pr.explore_user("P2", uni, sess.remaining, 1, 4, 12,
                               a.persistent_block(), cond,
                               a.candidates() if cond == "C3" else ())
        check(f"{cond} renders and absorbs", isinstance(text, str) and len(text) > 100)
        low = text.lower()
        bad = [w for w in BANNED if w in low]
        check(f"{cond} prompt is leakage-clean", not bad, str(bad))
    check("C4 withholds the hint",
          "interchangeably" not in pr.system_prompt(uni, hint=False))
    check("C0-C3 keep the hint", "interchangeably" in pr.system_prompt(uni))
    check("prompt length range matches the eval set",
          f"length {ev.len_lo} to {ev.len_hi}" in pr.system_prompt(
              uni, ev.len_lo, ev.len_hi))


def test_frozen_references():
    """The check that made the 2026-08-22 restoration trustworthy, kept as a
    permanent guard so any future restoration can be verified the same way.
    P3b's reference is 0.475, the value it takes once its cross-process
    nondeterminism is fixed. Every pre-loss P3b figure (0.467, 0.471, 0.483) and
    the first restored one (0.476) were samples from a hash-order-dependent
    distribution, not measurements of different code."""
    print("frozen arm references (20 universes, 6 rounds)")
    seeds, R = range(1, 21), 6
    got = {}
    for mode in ("random", "datadriven", "relevance"):
        v = []
        for s in seeds:
            u = mk(s)
            recs, _ = substrate_arm(u, EvalSet(u), s, ArmConfig(), R, mode)
            v.append(recs[-1]["acc_post"])
        got[mode] = sum(v) / len(v)
    b = [state_merge_arm(mk(s), EvalSet(mk(s)), s, 100, R)[-1]["acc_post"]
         for s in seeds]
    got["P3b"] = sum(b) / len(b)
    ra = [random_arm(mk(s), EvalSet(mk(s)), s) for s in seeds]
    got["chance"] = sum(r["acc_random"] for r in ra) / len(ra)
    got["majority"] = sum(r["acc_majority"] for r in ra) / len(ra)

    ref = {"chance": 0.239, "majority": 0.330, "random": 0.259,
           "datadriven": 0.364, "relevance": 0.647, "P3b": 0.475}
    for k, want in ref.items():
        d = abs(got[k] - want)
        check(f"{k} reproduces {want:.3f}", d < 0.0005,
              f"got {got[k]:.4f}")


if __name__ == "__main__":
    test_determinism()
    test_sealing()
    test_budget_and_scoring()
    test_artifacts()
    test_ignorance_vs_error()
    test_verifier()
    test_solvable_ceiling()
    test_wrong_artifacts_die()
    test_pipeline_determinism()
    test_model_pipeline_offline()
    test_cross_process_stability()
    test_frozen_references()
    print()
    if FAILS:
        print(f"{len(FAILS)} FAILURES: {FAILS}")
        sys.exit(1)
    print("all guards pass")
