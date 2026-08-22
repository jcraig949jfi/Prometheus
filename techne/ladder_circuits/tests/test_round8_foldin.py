"""Round-8 external review fold-in — cycle 032. READ-ONLY throughout.

Four items, each of which corrects or extends something I had already published:

1. Merge/split exhaust CLASSIFICATION ERROR against a fixed target, not REPRESENTATION
   ADEQUACY. A third failure mode — within-class loss relative to a later task — is invisible
   to both.
2. `H(P|T)` alone is distribution-dependent; worst-case fragmentation needs its own measure.
3. Infinitely many incomparable observation classes do NOT force "no impossibility result" — a
   uniform adversary constructor kills the family with one schema.
4. R0's advertised "identity congruence" is substantially sympy's normalisation, not the
   circuit's. Audit the preprocessing map before crediting the mechanism.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.partition import (  # noqa: E402
    conditional_entropy, induced_partition, refinement_multiplicity, variation_of_information,
    within_class_loss,
)
from prometheus_math.relative_claim import AGGREGATE, EXISTENTIAL, Domain, probe_monotonicity  # noqa: E402

x, y = sp.symbols("x y")
P = lambda *blocks: tuple(frozenset(b) for b in blocks)


# ---- ITEM 1: merge/split do not exhaust representation adequacy ---------------------------------

def _mult_value(proj, truth, n):
    """Cycle 041: refinement_multiplicity returns a Measurement now. `probe_monotonicity` needs a
    bare number, so the unwrap is explicit and local rather than hidden in the measure."""
    return refinement_multiplicity(proj, truth, n).value


def test_A_PERFECT_PROJECTION_CAN_DESTROY_EVERYTHING_A_LATER_TASK_NEEDS():
    """**Round 8's correction to my cycle-022 duality, on real integers.**

    The primality projection induces exactly the primality partition: no merge, no split,
    VI = 0.0000. Against a LATER target — "what is the smallest factor" — the same projection
    loses 1.9567 bits. Two composites sit in one class; one is 4 and one is 39.

    So merge/split exhaust classification error against a FIXED target. Adequacy is quantified
    over FUTURE targets, which is a different quantifier — and no amount of care about the first
    target detects it.
    """
    ns = list(range(2, 42))
    n = len(ns)
    is_prime = lambda i: sp.isprime(ns[i])
    smallest = lambda i: min(sp.factorint(ns[i]))

    proj = induced_partition(list(range(n)), is_prime)
    target1 = induced_partition(list(range(n)), is_prime)
    target2 = induced_partition(list(range(n)), smallest)

    assert variation_of_information(proj, target1, n) == pytest.approx(0.0)
    assert conditional_entropy(target1, proj, n) == pytest.approx(0.0)   # no merge
    assert conditional_entropy(proj, target1, n) == pytest.approx(0.0)   # no split

    loss = within_class_loss(proj, target2, n)
    assert loss == pytest.approx(1.9567, abs=1e-3)
    assert loss > 0                                                      # invisible to the above


def test_the_merge_split_theorem_is_scoped_to_a_fixed_target():
    """Stated as a test so the scope cannot drift back: the duality is a statement about one
    target, and adequacy needs the target enumerated."""
    ns = list(range(2, 20))
    n = len(ns)
    proj = induced_partition(list(range(n)), lambda i: sp.isprime(ns[i]))
    for target_fn in (lambda i: ns[i] % 2, lambda i: ns[i] % 3, lambda i: min(sp.factorint(ns[i]))):
        target = induced_partition(list(range(n)), target_fn)
        # perfect against primality, yet lossy against each of these
        assert within_class_loss(proj, target, n) > 0


# ---- ITEM 2: average bits vs worst-case fragmentation -------------------------------------------

def test_A_SHATTERED_RARE_CORNER_LOOKS_CHEAP_IN_BITS():
    """Round 8's warning, measured. One truth cell of 10 shattered into singletons costs
    0.3322 bits when the other cell holds 90; comparable shattering in the COMMON cell costs
    0.7851. Same worst-case multiplicity, very different averages."""
    n = 100
    truth = P(range(90), range(90, 100))
    rare_shattered = tuple([frozenset(range(90))] + [frozenset([i]) for i in range(90, 100)])
    common_shattered = tuple([frozenset([i]) for i in range(10)]
                             + [frozenset(range(10, 90)), frozenset(range(90, 100))])

    assert conditional_entropy(rare_shattered, truth, n) == pytest.approx(0.3322, abs=1e-3)
    assert conditional_entropy(common_shattered, truth, n) == pytest.approx(0.7851, abs=1e-3)
    assert refinement_multiplicity(rare_shattered, truth, n).value == 10
    assert refinement_multiplicity(common_shattered, truth, n).value == 11


def test_the_two_measures_are_different_KINDS_under_my_own_2x2():
    """**Convergence between round 8's advice and cycle 031's derivation — and I had to measure
    it twice, because my first chain made both look EXISTENTIAL.**

    Multiplicity is a max-of-counts: monotone up, EXISTENTIAL. Excess bits are normalised:
    growing the domain with elements in an UNSHATTERED truth cell drives them down while
    multiplicity stays fixed, so they move both ways — AGGREGATE.

    "Keep both" is therefore "keep one monotone measure and one normalised one".
    """
    def build(n_a, n_b, shards=4):
        a, b = list(range(n_a)), list(range(n_a, n_a + n_b))
        truth = (frozenset(a), frozenset(b))
        proj = tuple([frozenset(a[i::shards]) for i in range(shards) if a[i::shards]]
                     + [frozenset(b)])
        return proj, truth, n_a + n_b

    excesses, mults = [], []
    for n_b in (4, 20, 80, 300):
        proj, truth, n = build(40, n_b)
        excesses.append(conditional_entropy(proj, truth, n))
        mults.append(refinement_multiplicity(proj, truth, n).value)

    assert excesses == sorted(excesses, reverse=True)      # strictly DOWN on this chain
    assert excesses[0] > 1.8 and excesses[-1] < 0.3
    assert len(set(mults)) == 1                            # multiplicity unmoved

    # and UP on a chain of growing singleton refinements — hence neither direction holds
    chain = [Domain(f"d{k}", tuple(range(m))) for k, m in enumerate((10, 20, 40, 80))]
    up_excess = lambda d: round(conditional_entropy(
        tuple(frozenset([i]) for i in d.members), (frozenset(d.members),), len(d)), 9)
    up_mult = lambda d: _mult_value(
        tuple(frozenset([i]) for i in d.members), (frozenset(d.members),), len(d))
    assert probe_monotonicity(up_excess, chain) == EXISTENTIAL   # this chain only goes up...
    assert probe_monotonicity(up_mult, chain) == EXISTENTIAL
    # ...so the AGGREGATE verdict for excess rests on the decreasing chain above, per HITL #109


# ---- ITEM 3: a uniform adversary beats enumeration ----------------------------------------------

def test_ONE_SCHEMA_KILLS_AN_UNBOUNDED_FAMILY():
    """**Round 8's repair to cycle 022's "prove it per observation class".**

    With infinitely many incomparable classes, enumeration cannot finish — and the fallacy to
    avoid is "we could not enumerate, therefore the family might be sufficient". A parameterised
    constructor closes it: one schema, every width, both policies.
    """
    from techne.ladder_circuits.aliasing import uniform_adversary
    from techne.ladder_circuits.r3_constraint_store import (
        ConstraintStoreCircuit, FixedWidthPipeline,
    )
    from techne.ladder_circuits.sweep import twins_for_policy

    params = [(w, p) for w in range(1, 13) for p in ("fifo", "lifo")]

    def construct(param):
        w, pol = param
        h_t, h_f, q = twins_for_policy(w, pol)
        return h_t + [q], h_f + [q]

    def projection_for(param):
        w, pol = param

        def pi(events):
            pipe = FixedWidthPipeline(width=w, policy=pol)
            pipe.run(list(events)[:-1])
            return tuple(sorted(pipe._state.keys()))
        return pi

    truth = lambda events: ConstraintStoreCircuit().run(list(events))[-1]

    r = uniform_adversary("R3 bounded-state", params, construct, projection_for, truth)
    assert r.schema_survived
    assert r.n_parameters == 24 and len(r.witnesses) == 24


def test_a_uniform_adversary_NEVER_claims_to_prove_family_incapacity():
    """The attribute is hardcoded False so no caller can quietly upgrade the verdict. "The
    constructor works for every parameter" is a UNIVERSAL claim over the parameter space —
    monotone downward — so sampling can refute it and never establish it."""
    from techne.ladder_circuits.aliasing import uniform_adversary

    r = uniform_adversary("toy", [1, 2, 3],
                          construct=lambda p: (p, p + 100),
                          projection_for=lambda p: (lambda v: 0),
                          truth=lambda v: v)
    assert r.schema_survived
    assert r.proves_family_incapacity is False


def test_a_broken_schema_is_reported_as_a_SCHEMA_failure():
    """A parameter where the construction fails is a defect in the adversary, not evidence that
    the family is sound there — the report records it as a failure, and nothing else."""
    from techne.ladder_circuits.aliasing import uniform_adversary

    r = uniform_adversary("toy", [1, 2, 3],
                          construct=lambda p: (p, p),          # identical: truths never differ
                          projection_for=lambda p: (lambda v: 0),
                          truth=lambda v: v)
    assert not r.schema_survived
    assert set(r.failures) == {1, 2, 3}


# ---- ITEM 4: audit the preprocessing map before crediting the circuit ---------------------------

def test_R0s_IDENTITY_CONGRUENCE_IS_MOSTLY_SYMPYS():
    """**Round 8 called this the most interesting cycle-022 finding, and it is worse than I
    reported.** R0 advertises an identity congruence over ASTs. What it implements is
    `pi = srepr o sympy-normalisation`, which is strictly coarser than source identity.

    Seven of eight source-level distinctions are erased before the circuit sees anything:
    commutativity, associativity-with-constant-folding, power collapsing, rational
    normalisation, sqrt evaluation and cancellation. Only the genuine algebraic identity
    `x*(y+1)` vs `x*y+x` survives to be distinguished by the circuit.
    """
    from techne.ladder_circuits.r0_pattern import ast_key

    pairs = [("x+y", "y+x"), ("2*x", "x*2"), ("x**2", "x*x"), ("x/2", "Rational(1,2)*x"),
             ("(x+1)+2", "x+3"), ("sqrt(4)*x", "2*x"), ("x-x", "0")]
    for a, b in pairs:
        assert ast_key(sp.sympify(a)) == ast_key(sp.sympify(b)), (a, b)

    # the one the circuit really does separate
    assert ast_key(sp.sympify("x*(y+1)")) != ast_key(sp.sympify("x*y+x"))


def test_the_preprocessing_audit_rule_as_an_executable_check():
    """The generalised rule: before crediting a circuit with an invariance, check whether its
    PREPROCESSING already delivered it. Two inputs that differ in source and agree after
    normalisation are the circuit's alibi, not its achievement."""
    from techne.ladder_circuits.r0_pattern import ast_key

    def cas_delivered(src_a: str, src_b: str) -> bool:
        return src_a != src_b and ast_key(sp.sympify(src_a)) == ast_key(sp.sympify(src_b))

    assert cas_delivered("x+y", "y+x")
    assert cas_delivered("x-x", "0")
    assert not cas_delivered("x*(y+1)", "x*y+x")
    assert not cas_delivered("x+y", "x+y")          # identical source is not an invariance
