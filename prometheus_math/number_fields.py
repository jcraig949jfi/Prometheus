"""prometheus_math.number_fields — number-field-specific operations.

Splits naturally from `number_theory` to keep the surface focused on
NF-as-object operations (class field theory, CM, etc.).
"""

from techne.lib.class_number import class_number, class_group, regulator_nf
from techne.lib.hilbert_class_field import (
    hilbert_class_field,
    class_field_tower,
    set_pari_stack_mb,
)
from techne.lib.cm_order_data import cm_order_data
from techne.lib.p_class_field_tower import (
    p_hilbert_class_field,
    p_class_field_tower,
    tower_terminates_p,
    p_tower_signature,
)

__all__ = [
    "class_number", "class_group", "regulator_nf",
    "hilbert_class_field", "class_field_tower", "set_pari_stack_mb",
    "cm_order_data",
    "p_hilbert_class_field", "p_class_field_tower",
    "tower_terminates_p", "p_tower_signature",
]
