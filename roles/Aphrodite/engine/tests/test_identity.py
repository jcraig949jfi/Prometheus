"""Unit tests for the S1 identity layer (AMENDMENT 12). The full gate is
s1_gate.py; these pin the individual properties so a regression is local."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import identity as I  # noqa: E402
import s1_fixtures as F  # noqa: E402

TIER3C_WITNESS = ("fold", "0", "(acc + (v * v))", "(acc + first)")
TIER3C_OBSERVED = ("fold", "0", "(acc - (v * v))", "(first - acc)")


def test_compensating_pair_collapses_in_behavior_not_in_structure():
    """The collapse must come from the denotation, not from a rewrite rule."""
    a, b = I.identify(TIER3C_WITNESS), I.identify(TIER3C_OBSERVED)
    assert a["behavior_id"] == b["behavior_id"]
    assert a["structure_id"] != b["structure_id"]
    assert a["source_id"] != b["source_id"]
    assert a["source"] != b["source"] and a["structure"] != b["structure"]


def test_negation_conjugate_is_exact_for_every_witness():
    for w in F.catalog_witnesses():
        p = w["program"]
        assert I.same_behavior(p, F.negation_conjugate(p), w["trailing"]), w["family"]


def test_unsafe_rewrites_are_not_admitted():
    t = lambda s: I.term_str(I.normalise(I.parse(s)))
    assert t("(v // v)") == "fdiv(v, v)"                  # fails at v = 0
    assert t("(v % v)") == "mod(v, v)"
    assert t("math.gcd(abs(v), abs(v))") == "gcd(v, v)"   # it is |v|, not v
    assert t("(0 * (first // last))") == "mul(0, fdiv(first, last))"
    assert t("abs(acc)") == "abs(acc)"


def test_safe_rewrites_apply():
    t = lambda s: I.term_str(I.normalise(I.parse(s)))
    assert t("(v + acc)") == t("(acc + v)")
    assert t("((acc + 0) * 1)") == "acc"
    assert t("(first - first)") == "0"
    assert t("(0 * (first + last))") == "0"
    assert t("pow(acc, 1)") == "acc"
    assert t("(v // 1)") == "v"


def test_near_neighbours_have_real_witnesses_and_stay_apart():
    for nn in F.NEAR_NEIGHBOURS:
        tr = nn["trailing"]
        assert I.G.run_program(nn["a"], nn["witness"], tr) != \
            I.G.run_program(nn["b"], nn["witness"], tr), nn["name"]
        assert not I.same_behavior(nn["a"], nn["b"], tr), nn["name"]


def test_failure_is_part_of_behavior():
    a = ("fold", "0", "(acc + v)", "acc")
    b = ("fold", "0", "(acc + (v + (0 * (last // (v - first)))))", "acc")
    assert not I.same_behavior(a, b)


def test_batteries_lie_in_the_declared_domain():
    assert all(I.in_task_domain(x) for x in I.B1)
    assert all(I.in_task_domain(x) for x in I.b2())


def test_internal_overflow_on_valid_input_is_behavior():
    a = ("fold", "1", "(acc * v)", "(0 * acc)")
    assert not I.same_behavior(a, ("expr", "0"))


def test_battery_is_frozen():
    assert I.B1 == I.build_b1()
    assert I.B1_SHA == I._sha(I.build_b1())


def test_structural_program_round_trips():
    p = ("fold", "(1 * 1)", "(v + (acc + 0))", "math.gcd(abs(last), abs(acc))")
    sp = I.structural_program(p)
    assert I.same_behavior(p, sp)
    assert I.structural_form(sp) == I.structural_form(p)
