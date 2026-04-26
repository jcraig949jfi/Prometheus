"""prometheus_math.topology — knot, link, 3-manifold operations.

Hyperbolic geometry, knot Floer homology, Alexander polynomial, shape
fields. TDA helpers (gudhi/ripser/persim) re-exported as pass-through.
"""

from techne.lib.hyperbolic_volume import (
    hyperbolic_volume,
    hyperbolic_volume_hp,
    is_hyperbolic,
    volume_conjecture_ratio,
)
from techne.lib.knot_shape_field import (
    knot_shape_field,
    knot_shape_field_batch,
    polredabs,
)
from techne.lib.alexander_polynomial import (
    alexander_polynomial,
    alexander_coeffs,
)

__all__ = [
    "hyperbolic_volume", "hyperbolic_volume_hp", "is_hyperbolic",
    "volume_conjecture_ratio",
    "knot_shape_field", "knot_shape_field_batch", "polredabs",
    "alexander_polynomial", "alexander_coeffs",
]
