"""prometheus_math.number_theory — number-field and classical NT operations.

Re-exports Techne lib facilities with a cleaner namespace. New researchers
only need to know: `pm.number_theory.<op>(args)`.
"""

# Re-exports from Techne lib (the first-class implementations)
from techne.lib.class_number import (
    class_number,
    class_group,
    regulator_nf,
)
from techne.lib.galois_group import (
    galois_group,
    is_abelian,
    disc_is_square,
)
from techne.lib.hilbert_class_field import (
    hilbert_class_field,
    class_field_tower,
    set_pari_stack_mb,
)
from techne.lib.lll_reduction import (
    lll,
    lll_with_transform,
    shortest_vector_lll,
    lll_gram,
)
from techne.lib.cm_order_data import cm_order_data
from techne.lib.functional_eq_check import functional_eq_check, fe_residual

# Mahler measure / continued fractions / Sturm bound
from techne.lib.mahler_measure import (
    mahler_measure,
    log_mahler_measure,
    is_cyclotomic,
)
from techne.lib.cf_expansion import (
    cf_expand,
    cf_max_digit,
    zaremba_test,
    sturm_bound,
)

__all__ = [
    # class numbers / NF
    "class_number", "class_group", "regulator_nf",
    "galois_group", "is_abelian", "disc_is_square",
    "hilbert_class_field", "class_field_tower", "set_pari_stack_mb",
    "cm_order_data",
    # lattice
    "lll", "lll_with_transform", "shortest_vector_lll", "lll_gram",
    # L-functions
    "functional_eq_check", "fe_residual",
    # polynomials
    "mahler_measure", "log_mahler_measure", "is_cyclotomic",
    "cf_expand", "cf_max_digit", "zaremba_test", "sturm_bound",
]
