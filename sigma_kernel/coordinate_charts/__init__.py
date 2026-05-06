"""sigma_kernel.coordinate_charts — concrete chart registrations.

Each submodule here registers one or more :class:`CoordinateChart`
instances against :data:`sigma_kernel.coordinate_chart.DEFAULT_REGISTRY`
at **import time**. Downstream consumers can either import the chart
directly (e.g. ``from sigma_kernel.coordinate_charts.lehmer import
LEHMER_DEG14_PM5_PALINDROMIC``) or look it up by chart_id
(``get_chart("lehmer:deg14:pm5:palindromic")``).

Importing this package side-effects: every shipped chart submodule is
imported, which registers the charts. This is the registration entry
point for the substrate.

Currently shipped:
- ``lehmer`` — degree-14, ±5 coefficient bound, palindromic Lehmer
  subspace. Aporia priority; Ergon W3.2 unblocked when this lands.

Not yet shipped (need cross-pillar coordination, sync point T11):
- ``a149`` (Charon)
- ``obstruction_shape`` (Charon)
"""
from __future__ import annotations

# Import each submodule so its register_chart(...) side-effects execute
from . import lehmer  # noqa: F401

__all__ = ["lehmer"]
