"""prometheus_math.combinatorics — graphs, polytopes, integer matrices.

Currently:
- Smith normal form / abelian-group structure (Techne)
- Tropical (Baker-Norine) rank on graphs (Techne)
- Singularity classification of generating functions (Techne)
- networkx graph helpers (passthrough — researchers can use networkx directly)
"""

from techne.lib.smith_normal_form import (
    smith_normal_form,
    invariant_factors,
    abelian_group_structure,
)
from techne.lib.tropical_rank import (
    tropical_rank,
    tropical_rank_graph,
    is_winnable,
)
from techne.lib.singularity_classifier import (
    classify_singularity,
    estimate_radius,
)
from prometheus_math.combinatorics_partitions import (
    partitions_of,
    num_partitions,
    conjugate,
    hook_length,
    hook_length_array,
    num_standard_young_tableaux,
    num_ssyt,
    all_standard_young_tableaux,
    all_semi_standard_young_tableaux,
    rsk,
    inverse_rsk,
    schur_polynomial,
    bulgey,
)
from prometheus_math.combinatorics_posets import (
    Poset,
    chain_poset,
    antichain_poset,
    boolean_lattice,
    divisor_poset,
    product_poset,
    dual_poset,
)

__all__ = [
    "smith_normal_form", "invariant_factors", "abelian_group_structure",
    "tropical_rank", "tropical_rank_graph", "is_winnable",
    "classify_singularity", "estimate_radius",
    # Young tableaux / partitions:
    "partitions_of", "num_partitions",
    "conjugate", "hook_length", "hook_length_array",
    "num_standard_young_tableaux", "num_ssyt",
    "all_standard_young_tableaux", "all_semi_standard_young_tableaux",
    "rsk", "inverse_rsk", "schur_polynomial", "bulgey",
    # Posets:
    "Poset",
    "chain_poset", "antichain_poset", "boolean_lattice",
    "divisor_poset", "product_poset", "dual_poset",
]
