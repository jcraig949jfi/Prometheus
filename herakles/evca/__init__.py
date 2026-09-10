"""EvCA density classification as a pure, wrappable library (WP-C1).

Importing this package evaluates constants only: no execution, no file I/O,
no global RNG. See `core` for the pinned conventions, each of which is
enforced in code and covered by a test.

Intended consumer: Vivarium, wrapping this as the executor kind
`ca_density_v0`. The wrapper should stay thin and blind; every convention
that can change a result is fixed here and stated, so the wrapper does not
have to re-derive any of them.
"""
from .core import (  # noqa: F401
    EvcaError,
    RADIUS, WIDTH, TABLE_BITS, TABLE_HEX, WITNESS_LIMIT,
    require_radius, require_lattice, require_steps, require_density,
    require_table,
    decode_table, encode_table,
    neighbourhood_index, step, evolve, fixes_uniform_states,
    make_ics, majority_target,
    classify, mask_digest,
    reverse_bits, reflect_table, complement_table,
    reflect_states, complement_states,
    normalise_trajectory, trajectory_digest, selected_trajectory,
    majority_rule_table, gkl_rule_table,
    cellwise_majority_match, random_table,
)
from .genomes import GENOMES, NAMES, SPECIMEN_JSON, rule_hex  # noqa: F401

__all__ = [
    "EvcaError",
    "RADIUS", "WIDTH", "TABLE_BITS", "TABLE_HEX", "WITNESS_LIMIT",
    "require_radius", "require_lattice", "require_steps", "require_density",
    "require_table",
    "decode_table", "encode_table",
    "neighbourhood_index", "step", "evolve", "fixes_uniform_states",
    "make_ics", "majority_target",
    "classify", "mask_digest",
    "reverse_bits", "reflect_table", "complement_table",
    "reflect_states", "complement_states",
    "normalise_trajectory", "trajectory_digest", "selected_trajectory",
    "majority_rule_table", "gkl_rule_table",
    "cellwise_majority_match", "random_table",
    "GENOMES", "NAMES", "SPECIMEN_JSON", "rule_hex",
]
