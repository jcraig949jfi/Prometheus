"""
AETH-01 -- property-based tests (Hypothesis) over the repaired
transition law (`oracle_aeth01.py`), plus "instrument" tests that
reconcile the trace against the transition itself -- a first, partial
step toward REQUIREMENTS.md's independent event-ledger cross-check
(full K7 audit is deferred; these tests establish that the trace's
OWN reported amounts are internally consistent with the accounting
identity and with the committed grid, on every generated case, not
just the 6 K1 hand cases).

"Small" worlds: H, W in [1, 4] (AETH-00's own precedent, test_properties.py).
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle_aeth01 as ok1

MAX_DIM = 4

_cell_strategy = st.one_of(
    st.tuples(
        st.just(ok1.WRITE_OPCODE),
        st.integers(0, 255),
        st.integers(0, 255),
        st.integers(0, 255),
        st.integers(0, 255),
    ),
    st.tuples(
        st.integers(0, 255).filter(lambda o: o != ok1.WRITE_OPCODE),
        st.integers(0, 4),
        st.integers(0, 4),
        st.integers(0, 4),
        st.integers(0, 255),
    ),
)


@st.composite
def worlds(draw, max_dim=MAX_DIM):
    H = draw(st.integers(min_value=1, max_value=max_dim))
    W = draw(st.integers(min_value=1, max_value=max_dim))
    seed = draw(st.integers(min_value=0, max_value=(1 << 64) - 1))
    tick = draw(st.integers(min_value=0, max_value=(1 << 64) - 2))
    write_cost = draw(st.integers(min_value=0, max_value=255))
    maintenance_cost = draw(st.integers(min_value=0, max_value=255))
    replenish_numer = draw(st.sampled_from([0, 1, 1 << 16, 1 << 31, 1 << 32]))
    replenish_amount = draw(st.integers(min_value=0, max_value=255))
    mut_numer = draw(st.sampled_from([0, 1, 1 << 16, 1 << 31, 1 << 32]))
    grid = draw(st.lists(st.lists(_cell_strategy, min_size=W, max_size=W), min_size=H, max_size=H))
    return ok1.Aeth01World(
        H, W, seed, write_cost, maintenance_cost, replenish_numer,
        replenish_amount, mut_numer, tick=tick, grid=grid,
    )


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_accounting_identity_holds_exactly(world):
    """The single, non-double-counting identity (PHYSICS_SPEC_DRAFT.md
    S01 repair) must hold with ZERO tolerance, reconstructed purely
    from the trace's own reported amounts -- an instrument test, not
    only a physics test: it fails if the TRACE misreports an amount
    even if the grid happens to be correct."""
    trace = []
    nxt = world.step(trace=trace)
    total_before = sum(cell[ok1.ENERGY] for row in world.grid for cell in row)
    total_after = sum(cell[ok1.ENERGY] for row in nxt.grid for cell in row)
    X = sum(row[2] for row in trace if row[0] == "energy_debited")
    C = sum(row[2] for row in trace if row[0] == "energy_credited")
    D = sum(row[2] for row in trace if row[0] == "energy_decayed")
    R = sum(row[2] for row in trace if row[0] == "energy_replenished")
    # X here already includes BOTH the WRITE_COST debit and any
    # transfer-attempt debit (both are logged as "energy_debited" rows
    # per the oracle), i.e. X_identity + A_identity combined.
    assert total_after == total_before - X + C - D + R


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_energy_field_always_in_uint8_range(world):
    nxt = world.step()
    for row in nxt.grid:
        for cell in row:
            assert 0 <= cell[ok1.ENERGY] <= 255


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_only_winner_targeted_template_fields_may_differ(world):
    proposals = ok1.decode_and_emit(world.grid, world.H, world.W, world.write_cost)
    contests = ok1.group_contests(proposals)
    ok1.assert_no_duplicate_sources(contests)
    winners = ok1.arbitrate(world.seed, world.tick, contests)
    nxt = world.step()
    winner_targets = set(winners.keys())
    for r in range(world.H):
        for c in range(world.W):
            for f in ok1.TEMPLATE_FIELDS:
                if nxt.grid[r][c][f] != world.grid[r][c][f]:
                    assert ((r, c), f) in winner_targets


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_mutation_never_touches_energy_field(world):
    trace = []
    world.step(trace=trace)
    for row in trace:
        if row[0] == "mutation_applied":
            _kind, _target, field, _bit = row
            assert field != ok1.ENERGY


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_starved_cell_emits_nothing_and_pays_no_cost(world):
    trace = []
    nxt = world.step(trace=trace)
    starved_cells = {row[1] for row in trace if row[0] == "cell_starved"}
    emitted_sources = {row[1] for row in trace if row[0] == "proposal_emitted"}
    assert starved_cells.isdisjoint(emitted_sources)
    for (r, c) in starved_cells:
        # A starved cell's own energy is untouched by execution/transfer
        # debits (it never emitted), though it may still change via
        # maintenance/replenishment or an incoming credit as a TARGET.
        debited = any(
            row[0] == "energy_debited" and row[1] == (r, c) for row in trace
        )
        assert not debited


@settings(max_examples=200, deadline=None)
@given(world=worlds())
def test_property_replay_determinism(world):
    clone = ok1.Aeth01World(
        world.H, world.W, world.seed, world.write_cost, world.maintenance_cost,
        world.replenish_numer, world.replenish_amount, world.mut_numer,
        tick=world.tick, grid=world.grid,
    )
    assert world.step().to_bytes() == clone.step().to_bytes()
