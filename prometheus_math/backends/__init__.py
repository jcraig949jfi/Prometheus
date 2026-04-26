"""prometheus_math.backends — thin adapters around external mathematical tools.

Each backend module wraps a single tool (Python library or native binary)
behind a uniform shape. Categorical modules (e.g. algebraic_geometry,
number_theory) import these adapters and dispatch to whichever is
available.

Backends should fail gracefully when the underlying tool is not present:
expose `is_installed()` plus operations that raise informative
ValueError when called without the dependency.
"""
