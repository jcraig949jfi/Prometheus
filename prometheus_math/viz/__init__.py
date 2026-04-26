"""prometheus_math.viz — visualization helpers for math research.

Subpackages
-----------
- :mod:`prometheus_math.viz.knot` — Rolfsen / SnapPy-driven knot and
  link diagrams (project #36).
- :mod:`prometheus_math.viz.lfunctions` — L-function zero plots,
  critical-strip heat-maps, and zero-spacing statistics (project #37).
- :mod:`prometheus_math.viz.dashboard` — capability-matrix dashboard
  rendering :func:`prometheus_math.registry.installed` as HTML / PNG
  (project #50).

Everything in those submodules is also re-exported from
``prometheus_math.viz`` directly so existing call sites keep working
after the wave-7 refactor:

    from prometheus_math.viz import draw_knot     # still works
    pm.viz.draw_knot('4_1')                       # still works
    pm.viz.plot_zeros('Riemann', n_zeros=10)      # new in project #37
    pm.viz.dashboard()                            # new in project #50
"""
from __future__ import annotations

# Knot/link diagrams (project #36).
from .knot import (  # noqa: F401
    draw_knot,
    draw_link,
    knot_diagram_data,
    knot_layout_canonical,
    save_knot,
)

# L-function zeros plots (project #37).
from .lfunctions import (  # noqa: F401
    compare_zero_statistics,
    get_zeros,
    plot_critical_strip,
    plot_zero_spacings,
    plot_zeros,
    save_zeros_plot,
)

# Capability dashboard (project #50).
# Import the submodule first so the attribute access
# ``prometheus_math.viz.dashboard`` resolves to the module, not the
# function we re-export below.  After the ``from .dashboard import
# dashboard`` line, the function takes priority — we restore the
# submodule via the explicit alias ``dashboard_module``.
from . import dashboard as dashboard_module  # noqa: F401
from .dashboard import (  # noqa: F401
    capability_matrix,
    dashboard,
    render_html,
    render_png,
    save_dashboard,
    serve_dashboard,
    stop_dashboard,
)

__all__ = [
    # knot.py
    "draw_knot",
    "draw_link",
    "knot_diagram_data",
    "knot_layout_canonical",
    "save_knot",
    # lfunctions.py
    "compare_zero_statistics",
    "get_zeros",
    "plot_critical_strip",
    "plot_zero_spacings",
    "plot_zeros",
    "save_zeros_plot",
    # dashboard.py
    "capability_matrix",
    "dashboard",
    "render_html",
    "render_png",
    "save_dashboard",
    "serve_dashboard",
    "stop_dashboard",
]
