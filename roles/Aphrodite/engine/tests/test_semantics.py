"""Regression fixtures for the semantic-identity layer (AMENDMENT 10 s1).

These verify the GENERAL layer. They do not define it: no rule in semantics.py
names any expression appearing here. The Tier-3A equivalences are included
because mistaking them for distinct mechanisms is what invalidated that run's
control.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import semantics as S  # noqa: E402

TIER3A_EQUIVALENCES = [
    ("(acc + v)", "(v + acc)"),
    ("(acc * math.gcd(abs(v), abs(v)))", "(acc * v)"),
    ("math.gcd(abs(v), abs(math.gcd(abs(acc), abs(acc))))", "math.gcd(abs(acc), abs(v))"),
    ("math.gcd(abs(acc), abs((v + acc)))", "math.gcd(abs(acc), abs(v))"),
    ("(acc + math.gcd(abs(v), abs(v)))", "(acc + v)"),
]


def test_tier3a_equivalences_are_recognised():
    """The exact identities that broke Tier 3A's sham."""
    for a, b in TIER3A_EQUIVALENCES:
        assert S.equivalent(a, b), "%s !~ %s" % (a, b)


def test_the_number_theoretic_identity_needs_the_denotational_signature():
    """gcd(acc, v + acc) == gcd(acc, v) is true arithmetic, not a rewrite rule.
    The canonical AST forms differ; the signatures must still agree."""
    a, b = "math.gcd(abs(acc), abs((v + acc)))", "math.gcd(abs(acc), abs(v))"
    assert S.canonical_form(a) != S.canonical_form(b)
    assert S.equivalent(a, b)


def test_genuinely_different_mechanisms_stay_apart():
    for a, b in [("(acc + v)", "(acc * v)"),
                 ("(acc + v)", "(acc - v)"),
                 ("math.gcd(abs(acc), abs(v))", "(acc + v)"),
                 ("(acc + (v * v))", "(acc + v)"),
                 ("(acc + (v % last))", "(acc + v)"),
                 ("(acc + (v // last))", "(acc + (v % last))")]:
        assert not S.equivalent(a, b), "%s wrongly collapsed with %s" % (a, b)


def test_commutative_ordering_is_canonical():
    for a, b in [("(acc + v)", "(v + acc)"), ("(acc * v)", "(v * acc)"),
                 ("math.gcd(abs(acc), abs(v))", "math.gcd(abs(v), abs(acc))")]:
        assert S.canonical_form(a) == S.canonical_form(b)


def test_algebraic_identities_are_general():
    """Rules stated over variables, verified on variables the Tier-3A donor
    never produced."""
    assert S.canonical_form("(first + 0)") == "first"
    assert S.canonical_form("(last * 1)") == "last"
    assert S.canonical_form("(first * 0)") == "0"
    assert S.canonical_form("math.gcd(abs(last), abs(last))") == "last"
    assert S.canonical_form("(first - first)") == "0"
    assert S.canonical_form("(last // last)") == "1"


def test_partial_functions_are_distinguished_by_where_they_are_undefined():
    """A signature records None where an expression errors, so two programs
    that agree where both are defined are NOT merged."""
    assert not S.equivalent("(acc // v)", "(acc // last)")


def test_index_picks_a_stable_representative():
    idx = S.SemanticIndex()
    for src in ["(v + acc)", "(acc + v)", "(acc + math.gcd(abs(v), abs(v)))"]:
        idx.add(src)
    assert len(idx.classes()) == 1
    rep = idx.representative(S.signature("(acc + v)"))
    assert S.equivalent(rep, "(acc + v)")
    assert rep in ("(acc + v)", "(v + acc)")
