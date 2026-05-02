"""Prometheus-Math recipe galleries.

Each subpackage is a self-contained set of end-to-end recipes for one
mathematical topic.  Recipes are runnable .py files; they share a thin
``api.py`` facade so each recipe can stay focused on the math.

Galleries:

- persistent_homology  -- Vietoris-Rips, bottleneck, persistence images, ...
"""

from . import persistent_homology  # noqa: F401

__all__ = ["persistent_homology"]
