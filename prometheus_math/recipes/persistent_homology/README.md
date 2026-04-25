# Persistent-Homology Recipe Gallery

End-to-end recipes for topological data analysis using GUDHI.  Each recipe
is a self-contained Python file: import or `python <recipe>.py` and you
get a real persistent-homology result, no further setup required.

## Backend

Primary: [GUDHI](https://gudhi.inria.fr) (`pip install gudhi`).
The recipes share a thin facade in `api.py`; install GUDHI and every
recipe runs.

## Recipes

| #  | File                              | Topic                                                          | Run command                                                |
|----|-----------------------------------|----------------------------------------------------------------|------------------------------------------------------------|
| 1  | `rip_basic.py`                    | Vietoris-Rips on a 200-point 2D random cloud                   | `python rip_basic.py`                                      |
| 2  | `rip_circle.py`                   | VR detects H_1 = 1 of a noisy unit circle                      | `python rip_circle.py`                                     |
| 3  | `rip_torus.py`                    | VR Betti numbers of T^2 (1, 2, 1)                              | `python rip_torus.py`                                      |
| 4  | `distance_matrix_to_diagram.py`   | Rips persistence directly from a precomputed distance matrix   | `python distance_matrix_to_diagram.py`                     |
| 5  | `bottleneck_distance.py`          | Bottleneck distance: noisy circle vs ideal circle              | `python bottleneck_distance.py`                            |
| 6  | `wasserstein_distance.py`         | Wasserstein-2 distance between persistence diagrams            | `python wasserstein_distance.py`                           |
| 7  | `persistence_image.py`            | Vectorise a diagram into a persistence image (ML-ready)        | `python persistence_image.py`                              |
| 8  | `time_series_tda.py`              | Sliding-window PH of a noisy sine -- topological periodicity   | `python time_series_tda.py`                                |
| 9  | `cubical_complex_image.py`        | Sublevel-set PH of a 2D image -- counts dark blobs             | `python cubical_complex_image.py`                          |
| 10 | `betti_numbers_recipe.py`         | Betti numbers extracted from persistence diagrams              | `python betti_numbers_recipe.py`                           |

## Shared facade

`api.py` exposes the helpers used across the gallery so each recipe stays
short:

| Helper                                | Description                                                              |
|---------------------------------------|--------------------------------------------------------------------------|
| `rips_persistence(points, ...)`       | Vietoris-Rips persistence on a (N, d) array of points                    |
| `persistence_diagram_from_distmat(D)` | VR persistence directly on a distance matrix                             |
| `bottleneck_distance(a, b, dim)`      | Bottleneck (L_inf) distance between diagrams                             |
| `wasserstein_distance(a, b, p, dim)`  | p-Wasserstein distance between diagrams (Hera backend)                   |
| `persistence_image(diag, ...)`        | 2D persistence image vectorisation (Adams et al. 2017)                   |
| `betti_numbers_from_diagram(diag)`    | Betti numbers as the count of infinite-persistence bars per dimension    |
| `sliding_window_embed(ts, dim, tau)`  | Takens-style sliding-window embedding of a 1D time series                |
| `cubical_persistence(image_2d)`       | Sublevel-set PH of a 2D scalar field                                     |

## Tests

`tests/test_persistent_homology.py` covers all four math-tdd categories
(authority / property / edge / composition) plus a smoke test for every
recipe.

```
cd F:/Prometheus
python -m pytest prometheus_math/recipes/persistent_homology/tests/test_persistent_homology.py
```

## References

- Edelsbrunner & Harer, *Computational Topology* (AMS 2010).
- Carlsson, "Topology and Data", Bull. AMS 46 (2009).
- Cohen-Steiner, Edelsbrunner & Harer, "Stability of persistence diagrams",
  Discrete Comput. Geom. 37 (2007).
- Cohen-Steiner, Edelsbrunner, Harer & Mileyko, "Lipschitz functions have
  L_p-stable persistence", FoCM 10 (2010).
- Adams et al., "Persistence Images", JMLR 18 (2017).
- Perea & Harer, "Sliding Windows and Persistence", FoCM 15 (2015).
- de Silva & Ghrist, "Coverage in sensor networks via persistent homology",
  AGT 7 (2007).
