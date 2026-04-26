"""prometheus_math.numerics_special — special-function namespace.

Aggregates the per-family modules from backlog cluster #55-#58.
"""
from __future__ import annotations

from ..numerics_special_hurwitz import (  # noqa: F401
    hurwitz_zeta,
    hurwitz_zeta_derivative,
    dirichlet_l,
    polygamma,
    euler_maclaurin_zeta,
)

from ..numerics_special_dilogarithm import (  # noqa: F401
    dilogarithm,
    polylogarithm,
    bloch_wigner_dilog,
    dilog_inversion,
    dilog_reflection,
    clausen,
)

from ..numerics_special_q_pochhammer import (  # noqa: F401
    q_pochhammer,
    euler_function,
    dedekind_eta,
    q_factorial,
    q_binomial,
    jacobi_triple_product,
    pentagonal_number_partial_sum,
)

from ..numerics_special_theta import (  # noqa: F401
    jacobi_theta,
    jacobi_theta_derivative,
    theta_null_value,
    riemann_theta,
    lattice_theta_series,
    jacobi_triple_to_theta,
    theta_modular_transformation,
)

__all__ = [
    "hurwitz_zeta",
    "hurwitz_zeta_derivative",
    "dirichlet_l",
    "polygamma",
    "euler_maclaurin_zeta",
    "dilogarithm",
    "polylogarithm",
    "bloch_wigner_dilog",
    "dilog_inversion",
    "dilog_reflection",
    "clausen",
    "q_pochhammer",
    "euler_function",
    "dedekind_eta",
    "q_factorial",
    "q_binomial",
    "jacobi_triple_product",
    "pentagonal_number_partial_sum",
    "jacobi_theta",
    "jacobi_theta_derivative",
    "theta_null_value",
    "riemann_theta",
    "lattice_theta_series",
    "jacobi_triple_to_theta",
    "theta_modular_transformation",
]
