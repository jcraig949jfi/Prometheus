"""Seeded scientific contract fixtures, not a general heredity detector.

The oracle and GPU-shaped implementation remain independent; these builders
only share their input corpus. No transition-law or production code lives here.
"""

from math import inf

from reference import oracle_aeth01 as oracle

CLAIM_TIERS = (
    "STRUCTURAL_RESEMBLANCE",
    "CAUSAL_VALUE_CONSTRUCTION",
    "CONSTRUCTED_CAPACITY",
    "RECURSIVE_CONSTRUCTION",
    "HEREDITY_VARIATION",
)

CONTROL = (0, 5, 5, 5, 0)
EMPTY = (0, 0, 0, 0, 0)


def _world(grid, seed):
    return oracle.Aeth01World(len(grid), len(grid[0]), seed, 1, 0, 0, 0, 0, grid=grid)


def set_field(world, cell, field, value):
    """Explicit intervention on a fresh fixture or replay-fork state."""
    r, c = cell
    values = list(world.grid[r][c])
    values[field] = value
    world.grid[r][c] = tuple(values)


def relay_world(a_active=True):
    return _world([[
        (1 if a_active else 2, 1, 3, 77, 10),
        (1, 1, 3, 0, 10), EMPTY, CONTROL,
    ]], 21)


def activation_world(a_active=True):
    return _world([[
        (1 if a_active else 2, 1, 0, 1, 10),
        (0, 1, 3, 99, 10), EMPTY, CONTROL,
    ]], 23)


def distributed_world(a_opcode_active=True, a_arg0_active=True):
    # Two DISTINCT constructors act in the SAME tick, on different fields.
    # B's arg1=PAYLOAD, payload=77, and energy=10 are initialized scaffold.
    return _world([
        [CONTROL, (1 if a_opcode_active else 2, 2, 0, 1, 10), EMPTY],
        [(1 if a_arg0_active else 2, 1, 1, 1, 10), (0, 2, 3, 77, 10), EMPTY],
        [EMPTY, EMPTY, EMPTY],
    ], 31)


def recursive_activation_world(a_active=True, b_active=False, c_active=False):
    # B and C have fully preconfigured routing, field selection and payload.
    return _world([[
        (1 if a_active else 2, 1, 0, 1, 10),
        (1 if b_active else 0, 1, 0, 1, 10),
        (1 if c_active else 0, 1, 3, 99, 10), EMPTY, CONTROL,
    ]], 37)


def k3_intervention_cases():
    """Shared CPU/GPU inputs; expected scientific effects are tested separately."""
    for active in (True, False):
        yield f"relay A={active}", relay_world(active)
        yield f"activation A={active}", activation_world(active)
        yield f"recursive activation A={active}", recursive_activation_world(active)
    for opcode_active in (True, False):
        for routing_active in (True, False):
            yield (f"distributed opcode={opcode_active} routing={routing_active}",
                   distributed_world(opcode_active, routing_active))
    for name, builder, sources, control in (
        ("relay", relay_world, ((0, 0),), (0, 3)),
        ("activation", activation_world, ((0, 0),), (0, 3)),
        ("distributed", distributed_world, ((0, 1), (1, 0)), (0, 0)),
        ("recursive activation", recursive_activation_world, ((0, 0), (0, 1)), (0, 4)),
    ):
        for source in sources:
            world = builder()
            # SOUTH sends B to an inert target, avoiding a feedback path
            # into A_opcode that a NORTH-routing perturbation would create.
            value = oracle.SOUTH if builder is distributed_world and source == (1, 0) else 0
            set_field(world, source, oracle.PAYLOAD, value)
            yield f"{name} content intervention {source}", world
        world = builder()
        set_field(world, control, oracle.PAYLOAD, 29)
        yield f"{name} inert-control intervention", world
        for payload in (17, 29):
            world = builder()
            r, c = control
            world.grid[r][c] = (1, 0, 3, payload, 10)
            yield f"{name} active-control payload={payload}", world
    yield "recursive activation B rescue", recursive_activation_world(False, b_active=True)
    yield "recursive activation C rescue", recursive_activation_world(False, c_active=True)
    world = recursive_activation_world()
    set_field(world, (0, 1), oracle.ARG1, oracle.PAYLOAD)
    yield "recursive activation replaced by payload relay", world
    world = distributed_world()
    set_field(world, (1, 0), oracle.PAYLOAD, 5)
    yield "distributed neutral routing-byte intervention", world
    for field, value in ((oracle.ARG1, 2), (oracle.PAYLOAD, 55), (oracle.ENERGY, 0)):
        world = distributed_world()
        set_field(world, (1, 1), field, value)
        yield f"distributed initialized-scaffold field={field}", world


def isolated_pulse_budget(energy, write_cost, maintenance_cost):
    """Emission count for a persistent template writer, no inflow/transfers.

    Maintenance is paid AFTER emission and floors at zero. Zero write cost
    means energy never prevents emission, even after maintenance drains it.
    `inf` denotes no energy-limited stopping time, not uint64 tick overflow.
    """
    for value in (energy, write_cost, maintenance_cost):
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError("energy and costs must be uint8 integers")
    if write_cost == 0:
        return inf
    if energy < write_cost:
        return 0
    return 1 + (energy - write_cost) // (write_cost + maintenance_cost)