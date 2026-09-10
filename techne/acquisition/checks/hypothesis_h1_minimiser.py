"""Qualify Hypothesis's shrinking as a witness-minimiser for H1 witnesses.

    <env>/python techne/acquisition/checks/hypothesis_h1_minimiser.py --fixture-out <path>

An H1 witness is an input on which two Boolean programs disagree. A minimiser is useful only if
it preserves that property, so the declared contract is one line:

    A SHRUNK WITNESS MUST STILL BE A WITNESS UNDER PROTEUS'S EVALUATOR.

That is a post-condition on the minimiser, checked by `proteus.eval.boolean.truth_table` on
every shrunk result, and it can FAIL -- the negative control feeds the same checker a
non-witness and requires rejection.

WHAT "SMALLER" MEANS IS DECLARED, NOT INHERITED. Hypothesis shrinks toward its own notion of
simplicity, which for a fixed-length tuple of booleans is toward False. That ordering is fine
but it is Hypothesis's, so this check declares the order it cares about -- fewer ones in the
assignment, then lexicographically smaller -- and MEASURES whether the shrunk witness is minimal
under it, rather than assuming that "shrunk" means "minimal for us".

THE HONEST LIMIT, stated before the numbers: on a 3-input domain there are only 8 assignments,
so a minimiser is not needed -- exhaustive enumeration is cheaper and exact, and this check
computes the true minimum that way in order to score Hypothesis against it. The qualification
therefore establishes that shrinking is SOUND here, and explicitly does not establish that it is
USEFUL here. Usefulness would need a domain where enumeration is infeasible, which H1 1.0 is not.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

from hypothesis import HealthCheck, Phase, given, seed, settings
from hypothesis import strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from proteus.eval import boolean as PB   # noqa: E402

N = PB.N_INPUTS
N_CASES = 2 ** N
RUN_SEED = 20260910


def case_bits(k):
    return tuple((k >> (N - 1 - j)) & 1 for j in range(N))


def expr_for_table(table):
    mt = []
    for k, bit in enumerate(table):
        if not bit:
            continue
        lits = [PB.I(j) if b else PB.Not(PB.I(j)) for j, b in enumerate(case_bits(k))]
        t = lits[0]
        for l in lits[1:]:
            t = PB.And(t, l)
        mt.append(t)
    if not mt:
        return PB.C(0)
    out = mt[0]
    for m in mt[1:]:
        out = PB.Or(out, m)
    return out


def is_witness(tf, tg, bits) -> bool:
    """THE POST-CONDITION, evaluated by Proteus's tables and nothing else."""
    k = sum(b << (N - 1 - j) for j, b in enumerate(bits))
    return tf[k] != tg[k]


# Declared order: fewer ones first, then lexicographic. Ours, not Hypothesis's.
def rank(bits):
    return (sum(bits), tuple(bits))


def true_minimum(tf, tg):
    ws = [case_bits(k) for k in range(N_CASES) if tf[k] != tg[k]]
    return min(ws, key=rank) if ws else None


def shrink_one(tf, tg, db_dir: pathlib.Path):
    """Let Hypothesis find and shrink a witness, then hand the result to Proteus."""
    found = {}

    @settings(database=DirectoryBasedExampleDatabase(str(db_dir)), max_examples=500,
              deadline=None, suppress_health_check=[HealthCheck.too_slow],
              phases=[Phase.generate, Phase.shrink])
    @seed(RUN_SEED)
    @given(st.tuples(*[st.booleans() for _ in range(N)]))
    def prop(bits):
        b = tuple(int(x) for x in bits)
        # the property under test: "these two programs agree here". Its falsification IS a
        # witness, which is why shrinking a failure shrinks a witness.
        assert not is_witness(tf, tg, b), f"witness {b}"

    try:
        prop()
        return None
    except AssertionError as exc:
        msg = str(exc)
        raw = msg.split("witness", 1)[1].strip().split("\n")[0]
        found["bits"] = tuple(int(c) for c in raw if c in "01")
        return found["bits"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-out", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--n-pairs", type=int, default=40)
    a = ap.parse_args(argv)

    work = pathlib.Path(a.work)
    work.mkdir(parents=True, exist_ok=True)

    tables = [tuple((f >> (N_CASES - 1 - k)) & 1 for k in range(N_CASES))
              for f in range(2 ** N_CASES)]
    # a declared, seeded, reproducible selection of distinct pairs: every (f, f+1) plus a
    # stride. Chosen by rule so the sample is not picked after seeing which ones shrink well.
    pairs = [(f, (f + 1) % 256) for f in range(0, 256, 256 // (a.n_pairs // 2))]
    pairs += [(f, (f + 37) % 256) for f in range(0, 256, 256 // (a.n_pairs // 2))]
    pairs = [(f, g) for f, g in pairs if tables[f] != tables[g]]

    rows, post_failures, not_minimal = [], [], []
    for i, (f, g) in enumerate(pairs):
        tf, tg = tables[f], tables[g]
        shrunk = shrink_one(tf, tg, work / f"scope_{i}" / "examples")
        truth = true_minimum(tf, tg)
        ok = shrunk is not None and is_witness(tf, tg, shrunk)
        minimal = shrunk is not None and rank(shrunk) == rank(truth)
        if not ok:
            post_failures.append({"f": f, "g": g, "shrunk": shrunk})
        if ok and not minimal:
            not_minimal.append({"f": f, "g": g, "shrunk": list(shrunk),
                                "true_minimum": list(truth),
                                "shrunk_rank": rank(shrunk), "true_rank": rank(truth)})
        rows.append({"f": f, "g": g, "shrunk": list(shrunk) if shrunk else None,
                     "still_a_witness_under_proteus": ok,
                     "true_minimum": list(truth) if truth else None,
                     "minimal_under_our_declared_order": minimal,
                     "n_witnesses_in_domain": sum(1 for k in range(N_CASES) if tf[k] != tg[k])})

    # NEGATIVE CONTROL: the post-condition checker must reject a non-witness.
    f0, g0 = pairs[0]
    tf, tg = tables[f0], tables[g0]
    non = next((case_bits(k) for k in range(N_CASES) if tf[k] == tg[k]), None)
    neg = {"pair": [f0, g0], "non_witness": list(non) if non else None,
           "checker_rejects_it": (non is not None and not is_witness(tf, tg, non))}

    checks = [
        (f"every shrunk witness over {len(rows)} pairs is STILL A WITNESS under Proteus",
         not post_failures),
        ("a witness was found for every pair that has one",
         all(r["shrunk"] is not None for r in rows)),
        ("negative control: the post-condition checker rejects a non-witness",
         neg["checker_rejects_it"]),
        ("MEASURED, not assumed: whether the shrunk witness is minimal under OUR declared order",
         True),   # reported below either way; this is a measurement, not a gate
    ]

    fixture = {
        "schema": "techne.h1.hypothesis_minimiser_fixture/1",
        "declared_contract": "a shrunk witness must still be a witness under "
                             "proteus.eval.boolean.truth_table",
        "declared_order": "fewer ones in the assignment, then lexicographic -- OURS, not "
                          "Hypothesis's. Hypothesis shrinks toward its own notion of "
                          "simplicity; this check measures agreement rather than assuming it.",
        "tool": {"distribution": "hypothesis", "version": __import__("hypothesis").__version__,
                 "env": "isolated venv h0h5_tools",
                 "reproducibility": f"explicit @seed({RUN_SEED}); derandomize is NOT used "
                                    f"because it would disable the scoped example database"},
        "oracle": {"module": "proteus.eval.boolean", "function": "truth_table",
                   "interface_version": PB.INTERFACE_VERSION},
        "domain": {"n_inputs": N, "n_cases": N_CASES,
                   "pair_selection": "declared by rule: (f, f+1) and (f, f+37) on a fixed "
                                     "stride, so the sample is not chosen after seeing which "
                                     "pairs shrink well"},
        "rows": rows,
        "post_condition_failures": post_failures,
        "shrunk_but_not_minimal_under_our_order": not_minimal,
        "n_pairs": len(rows),
        "n_minimal": sum(1 for r in rows if r["minimal_under_our_declared_order"]),
        "negative_control": neg,
        "checks": [{"claim": c, "pass": bool(p)} for c, p in checks],
        "all_passed": all(p for _, p in checks),
        "HONEST_LIMIT": (
            "SOUND here, not USEFUL here. On 3 inputs there are 8 assignments, so exhaustive "
            "enumeration finds the true minimum exactly and more cheaply than shrinking -- this "
            "check uses that enumeration as the yardstick. The qualification establishes that "
            "Hypothesis's shrinking preserves the witness property under Proteus's evaluator. "
            "It does NOT establish that a minimiser earns its place in H1 1.0, and it cannot: "
            "that needs a domain where enumeration is infeasible."),
        "what_this_does_NOT_establish": [
            "that shrinking is minimal under Hypothesis's own ordering -- that is Hypothesis's "
            "business, and a different claim from ours",
            "usefulness at H1 1.0's scale; see HONEST_LIMIT",
            "anything about shrinking structured H1 programs rather than assignments",
        ],
    }
    pathlib.Path(a.fixture_out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.fixture_out).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    try:
        from techne.acquisition import receipt as _R
        rec = _R.new("ADAPTER_QUALIFICATION", "hypothesis", tool="hypothesis")
        rec["check"] = "hypothesis_shrinking_as_an_h1_witness_minimiser"
        rec["consumer"] = "H1 witness minimisation (Proteus's Boolean substrate)"
        rec["fixture"] = a.fixture_out
        rec["observations"] = fixture
        rec["status"] = "QUALIFIED_SOUND_USEFULNESS_NOT_ESTABLISHED" if fixture["all_passed"] \
            else "FAILED"
        rec["unrun_or_blocked"] = [fixture["HONEST_LIMIT"]]
        print("receipt", _R.write(rec))
    except Exception as exc:
        print(f"receipt NOT written: {type(exc).__name__}: {exc}")

    print(f"pairs {len(rows)} | post-condition failures {len(post_failures)} | "
          f"minimal under our order {fixture['n_minimal']}/{len(rows)}")
    for c in fixture["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    if not_minimal:
        print(f"  NOT MINIMAL on {len(not_minimal)} pairs, e.g. {not_minimal[0]}")
    return 0 if fixture["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
