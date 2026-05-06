"""sigma_kernel.exclusion_certificates — concrete certificate registrations.

Each submodule here registers one or more :class:`ExclusionCertificate`
instances against :data:`sigma_kernel.exclusion_certificate.DEFAULT_REGISTRY`
at **import time**. Mirrors the P0 ``sigma_kernel.coordinate_charts``
package layout.

Importing this package side-effects: every shipped certificate submodule
is imported, which registers the certificates. This is the registration
entry point for substrate-shipped exclusion certificates.

Currently shipped:
- ``lehmer_deg14`` — the deg14 ±5 palindromic Lehmer brute-force
  exclusion certificate (substrate v2.3 §6.3 prototype). Earned
  ``strength = COMPLETE`` via Path A/B/C/D triangulation.

Note: importing the lehmer_deg14 submodule depends on the Lehmer chart
being registered first (so the certificate's ``coordinate_chart_id``
validates). The submodule imports the chart package directly to ensure
import order is correct regardless of consumer load path.
"""
from __future__ import annotations

# Import each submodule so its register_certificate(...) side-effects execute.
from . import lehmer_deg14  # noqa: F401

__all__ = ["lehmer_deg14"]
