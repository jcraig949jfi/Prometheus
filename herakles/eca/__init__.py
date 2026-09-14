"""eca_rule_eval_v1: elementary radius-1 cellular automata. H5 alpha.

Separate from `herakles.evca` by design. See `core` for the pinned
conventions. Nothing here decodes a genome: the design places the decoder
producer-side and this evaluator consumes only a resolved rule number.
"""
from . import core  # noqa: F401
from .core import (  # noqa: F401
    EcaError, RADIUS, WIDTH, TABLE_BITS, N_RULES,
    require_rule, require_lattice, require_steps,
    rule_table, table_to_rule, neighbourhood_index, step, evolve,
    all_configurations, behaviour, behaviour_digest, equivalence_classes,
    derive_constant_zero, derive_constant_one, derive_identity,
    derive_shift_left, derive_shift_right, derive_xor_neighbours,
    HAND_DERIVED,
    make_ics, density, adjacent_pairs, block_output_correct,
    block_output_score, uniform_at_T_correct, uniform_at_T_score,
    planted_block_configuration,
)
