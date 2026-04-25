"""Persistent-homology recipe gallery.

End-to-end recipes for topological data analysis using GUDHI.  Each
recipe is a runnable .py file under this package; the shared facade
``api.py`` exposes the helpers used across the gallery.

Recipes:

1.  rip_basic.py                 -- Vietoris-Rips on a 2D point cloud
2.  rip_circle.py                -- VR detects H_1 = 1 of a noisy circle
3.  rip_torus.py                 -- VR Betti numbers (1, 2, 1) of T^2
4.  distance_matrix_to_diagram   -- VR from a precomputed distance matrix
5.  bottleneck_distance          -- bottleneck noisy-vs-ideal circle
6.  wasserstein_distance         -- Wasserstein-2 between diagrams
7.  persistence_image            -- vectorise a diagram for ML
8.  time_series_tda              -- sliding-window PH of a noisy sine
9.  cubical_complex_image        -- sublevel-set PH of an image
10. betti_numbers_recipe         -- Betti numbers from PH directly
"""

from . import api  # noqa: F401

__all__ = ["api"]
