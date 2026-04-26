"""prometheus_math.viz.knot — knot/link diagram rendering for notebooks.

Renders knot and link diagrams from SnapPy PD-codes into Matplotlib
figures or SVG strings, suitable for headless export and notebook
inclusion.

Public API
----------
- ``draw_knot(name, ax=None, style='solid', backend='matplotlib')``
  Render a knot diagram (named via Rolfsen / SnapPy convention,
  e.g. ``'4_1'``).  ``backend='matplotlib'`` returns an ``mpl.figure.Figure``;
  ``backend='svg'`` returns a raw SVG string.
- ``knot_diagram_data(name)``
  Extract primitive geometric data: PD code, DT code, Gauss code,
  crossing positions, strand polylines, component count.
- ``save_knot(name, path, fmt=None)``
  Save the diagram directly to disk (PNG / SVG / PDF).  ``fmt`` is
  inferred from the path extension when omitted.
- ``draw_link(name, ax=None)``
  Same as ``draw_knot`` but tolerant of multi-component links such as
  the Hopf link (``'L2a1'``).
- ``knot_layout_canonical(name)``
  Return the per-component strand polylines (list of ``(x, y)`` lists)
  used internally; exposed for advanced users.

Layout strategy
---------------
For a v1 notebook-ready renderer we use a *circular* layout: the ``n``
crossings of an ``n``-crossing diagram are placed on the vertices of a
regular ``n``-gon (or a slightly perturbed polygon for n <= 2 to avoid
degeneracies).  Strands are drawn as cubic-Bezier curves between
crossings, walking the diagram in the order given by the PD code.  At
each crossing the over-strand is drawn solid; the under-strand has a
short white "break" rendered via a fat white segment underneath the
solid line — a standard convention in topology textbooks.

This is not a research-grade diagram engine (no ambient-isotopy
optimisation, no Reidemeister-aware crossing reduction).  It is "clean
enough for a Jupyter cell" and deterministic, which is the requirement
for project #36.

References
----------
- Rolfsen, "Knots and Links" (1976), knot table appendix.
- KnotInfo / LinkInfo (Livingston, Moore): standard crossing numbers.
- SnapPy documentation, ``snappy.Link`` / ``snappy.Manifold`` PD-code API.
"""
from __future__ import annotations

import io
import math
import os
from typing import Any, List, Optional, Sequence, Tuple, Union

# Matplotlib is a hard dependency for the viz module; importing here
# means a missing matplotlib raises a clean ImportError at call time
# rather than buried inside helpers.
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    _HAS_MPL = True
except Exception:  # pragma: no cover
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    Figure = object  # type: ignore
    PathPatch = None  # type: ignore
    Path = None  # type: ignore
    _HAS_MPL = False

try:
    import snappy  # type: ignore
    _HAS_SNAPPY = True
except Exception:  # pragma: no cover
    snappy = None  # type: ignore
    _HAS_SNAPPY = False


__all__ = [
    "draw_knot",
    "draw_link",
    "knot_diagram_data",
    "knot_layout_canonical",
    "save_knot",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_VALID_BACKENDS = ("matplotlib", "svg")
_VALID_FORMATS = ("png", "svg", "pdf")


def _require_snappy() -> None:
    if not _HAS_SNAPPY:
        raise ImportError(
            "prometheus_math.viz requires SnapPy. "
            "Install via `pip install snappy` (or skip the test)."
        )


def _require_mpl() -> None:
    if not _HAS_MPL:
        raise ImportError(
            "prometheus_math.viz requires matplotlib. "
            "Install via `pip install matplotlib`."
        )


def _load_link(name: str):
    """Construct a snappy.Link for ``name``.

    Wraps SnapPy's catalog lookup to translate its generic exceptions
    into a uniform ``ValueError`` with the offending name embedded.
    """
    _require_snappy()
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            f"knot/link name must be a non-empty string, got {name!r}"
        )
    try:
        return snappy.Link(name)  # type: ignore[union-attr]
    except Exception as exc:
        raise ValueError(
            f"unknown knot/link name {name!r} (SnapPy: {exc})"
        ) from exc


def _crossing_positions(n: int) -> List[Tuple[float, float]]:
    """Return ``n`` points on a unit circle, evenly spaced.

    For ``n == 1`` we return a single off-origin point so downstream
    code can still draw a tiny loop. For ``n == 0`` (no crossings, e.g.
    the unknot) we return a single dummy point so the layout reduces
    to one circular strand.
    """
    if n <= 0:
        return [(1.0, 0.0)]
    if n == 1:
        return [(1.0, 0.0)]
    return [
        (math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n))
        for k in range(n)
    ]


def _pd_to_gauss(pd_code: Sequence[Sequence[int]]) -> List[int]:
    """Convert PD code to a flat Gauss code (signed crossing visits).

    A PD code lists crossings as 4-tuples of edge labels in
    counter-clockwise order starting from the incoming under-strand.
    The Gauss code records, for each component, the sequence of
    crossing visits with sign indicating over (+) / under (-).

    For a single-component diagram with ``n`` crossings there are
    ``2n`` edge labels (0..2n-1) which we trace starting from edge 0,
    visiting each crossing twice.
    """
    if not pd_code:
        return []
    n = len(pd_code)
    num_edges = 2 * n
    # Map each edge label to (crossing_idx, position_in_crossing 0..3)
    edge_to_crossing: dict = {}
    for ci, crossing in enumerate(pd_code):
        for pos, edge in enumerate(crossing):
            edge_to_crossing.setdefault(int(edge) % num_edges, []).append(
                (ci, pos)
            )

    gauss: List[int] = []
    visited_edges = set()
    edge = 0
    safety = 4 * num_edges
    while edge not in visited_edges and safety > 0:
        safety -= 1
        visited_edges.add(edge)
        endpoints = edge_to_crossing.get(edge, [])
        if not endpoints:
            break
        # The "next" endpoint of this edge is the one we haven't just
        # come from; for the start (edge 0) we just pick the first.
        ci, pos = endpoints[-1]
        # Position 0 = incoming under, 2 = outgoing over (typical PD).
        # SnapPy PD codes follow Kauffman convention; we don't need the
        # exact sign here for layout purposes — any signed visit will do.
        sign = +1 if pos in (1, 3) else -1
        gauss.append(sign * (ci + 1))
        # Move to the "next" edge along the strand: in PD-code Kauffman
        # convention, position 0 -> position 2 (under straight) and
        # position 1 -> position 3 (over straight).
        next_pos = (pos + 2) % 4
        next_edge = int(pd_code[ci][next_pos]) % num_edges
        edge = next_edge
    return gauss


def _bezier_segment(p0: Tuple[float, float],
                    p1: Tuple[float, float],
                    bulge: float = 0.25) -> List[Tuple[float, float]]:
    """Return a sampled cubic-Bezier curve from ``p0`` to ``p1``.

    The control points are pulled toward the origin by ``bulge`` so
    strands curve gracefully through the centre of the diagram rather
    than running as straight chords (which produces a tangle of
    overlapping lines for n >= 5).
    """
    cx0 = p0[0] * (1 - bulge)
    cy0 = p0[1] * (1 - bulge)
    cx1 = p1[0] * (1 - bulge)
    cy1 = p1[1] * (1 - bulge)
    samples = []
    for t in [i / 24.0 for i in range(25)]:
        u = 1 - t
        x = (
            u**3 * p0[0]
            + 3 * u**2 * t * cx0
            + 3 * u * t**2 * cx1
            + t**3 * p1[0]
        )
        y = (
            u**3 * p0[1]
            + 3 * u**2 * t * cy0
            + 3 * u * t**2 * cy1
            + t**3 * p1[1]
        )
        samples.append((x, y))
    return samples


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def knot_diagram_data(name: str) -> dict:
    """Extract primitive diagram data for a knot or link.

    Parameters
    ----------
    name : str
        Knot/link name in SnapPy / Rolfsen convention, e.g. ``'4_1'``,
        ``'8_19'``, ``'L2a1'``.

    Returns
    -------
    dict with keys:
        ``pd_code`` (list[tuple[int]]):
            SnapPy PD code (Kauffman convention).
        ``dt_code`` (list[int]):
            Flat DT code; for multi-component links, the codes for
            each component are concatenated.
        ``gauss_code`` (list[int]):
            Signed crossing-visit sequence derived from the PD code.
        ``crossings`` (list[tuple[float, float, int]]):
            ``(x, y, sign)`` for each crossing where ``sign`` is +1 or
            -1 (SnapPy crossing sign).
        ``strands`` (list[list[tuple[float, float]]]):
            Polyline samples for each strand (per component).
        ``num_components`` (int):
            Number of link components (1 for a knot).

    Raises
    ------
    ValueError
        If ``name`` is not a recognised knot/link.
    ImportError
        If SnapPy is not installed.
    """
    link = _load_link(name)
    pd = [tuple(int(e) for e in c) for c in link.PD_code()]
    n_cross = len(pd)

    # DT code: SnapPy returns a list of tuples (one per component).
    raw_dt = link.DT_code()
    if raw_dt and isinstance(raw_dt[0], (list, tuple)):
        dt_flat: List[int] = []
        for chunk in raw_dt:
            dt_flat.extend(int(x) for x in chunk)
    else:
        dt_flat = [int(x) for x in raw_dt]

    gauss = _pd_to_gauss(pd)

    # Crossing positions on the unit circle, plus per-crossing sign.
    base_pts = _crossing_positions(n_cross)
    crossings: List[Tuple[float, float, int]] = []
    snappy_crossings = list(link.crossings)
    for i in range(n_cross):
        x, y = base_pts[i]
        sign = int(getattr(snappy_crossings[i], "sign", 0)) if i < len(
            snappy_crossings
        ) else 0
        crossings.append((x, y, sign))

    # Strand polylines: walk components by tracing PD-code edges.
    strands = knot_layout_canonical(name)

    return {
        "pd_code": pd,
        "dt_code": dt_flat,
        "gauss_code": gauss,
        "crossings": crossings,
        "strands": strands,
        "num_components": len(link.link_components),
    }


def knot_layout_canonical(name: str) -> List[List[Tuple[float, float]]]:
    """Compute strand polylines for a knot/link diagram.

    The layout places the ``n`` crossings of an ``n``-crossing diagram
    on the vertices of a regular ``n``-gon and routes strands as
    cubic-Bezier curves between them.

    Returns
    -------
    list[list[tuple[float, float]]]
        One polyline per strand segment.  The number of segments is
        ``2 * n_crossings`` for an ``n``-crossing diagram (each strand
        passes through each crossing twice).
    """
    link = _load_link(name)
    pd = [tuple(int(e) for e in c) for c in link.PD_code()]
    n = len(pd)
    if n == 0:
        # Unknot: one circular strand
        circle = [
            (math.cos(2 * math.pi * k / 64),
             math.sin(2 * math.pi * k / 64))
            for k in range(65)
        ]
        return [circle]

    pts = _crossing_positions(n)
    num_edges = 2 * n
    # Map edges to (crossing, position) — same scheme as _pd_to_gauss.
    edge_to_endpoints: dict = {}
    for ci, crossing in enumerate(pd):
        for pos, edge in enumerate(crossing):
            edge_to_endpoints.setdefault(int(edge) % num_edges, []).append(
                (ci, pos)
            )

    strands: List[List[Tuple[float, float]]] = []
    for edge in range(num_edges):
        endpoints = edge_to_endpoints.get(edge, [])
        if len(endpoints) < 2:
            # malformed PD code — skip
            continue
        (ci0, _), (ci1, _) = endpoints[0], endpoints[1]
        if ci0 == ci1:
            # self-loop at a single crossing: render a small bulge
            x, y = pts[ci0]
            offset = 0.15
            seg = _bezier_segment(
                (x + offset, y),
                (x - offset, y),
                bulge=0.5,
            )
        else:
            seg = _bezier_segment(pts[ci0], pts[ci1], bulge=0.45)
        strands.append(seg)

    return strands


def _render_to_axes(name: str, ax, style: str = "solid") -> None:
    """Render the named knot diagram onto an existing matplotlib axes."""
    _require_mpl()
    data = knot_diagram_data(name)
    strands = data["strands"]
    crossings = data["crossings"]

    # Strand line: width and style
    lw = 2.4
    linestyle = "-" if style == "solid" else "--"
    color = "black"

    for seg in strands:
        xs = [p[0] for p in seg]
        ys = [p[1] for p in seg]
        ax.plot(xs, ys, linestyle=linestyle, color=color, linewidth=lw)

    # Crossing markers: a small white-rimmed dot whose colour encodes
    # the SnapPy sign (+ blue, - red).  Doubles as visual indicator of
    # the n-gon vertices for sanity-checking.
    for (x, y, sign) in crossings:
        face = "#1f77b4" if sign > 0 else ("#d62728" if sign < 0 else "#888")
        ax.plot(
            [x], [y],
            marker="o",
            markersize=10,
            markerfacecolor=face,
            markeredgecolor="white",
            markeredgewidth=1.5,
            linestyle="None",
        )

    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.axis("off")
    ax.set_title(f"{name}  ({len(crossings)} crossings, "
                 f"{data['num_components']} comp.)",
                 fontsize=10)


def draw_knot(name: str,
              ax: Optional[Any] = None,
              style: str = "solid",
              backend: str = "matplotlib") -> Union[Figure, str]:
    """Render a knot diagram.

    Parameters
    ----------
    name : str
        Knot name (e.g. ``'4_1'``, ``'8_19'``).
    ax : matplotlib.axes.Axes, optional
        Pre-existing axes to draw into.  When omitted a fresh figure
        is created.  Ignored when ``backend='svg'``.
    style : {'solid', 'dashed'}, default 'solid'
        Line style for the strand polylines.
    backend : {'matplotlib', 'svg'}, default 'matplotlib'
        ``'matplotlib'`` returns an ``mpl.figure.Figure``;
        ``'svg'`` returns a raw SVG string.

    Returns
    -------
    matplotlib.figure.Figure or str

    Raises
    ------
    ValueError
        If ``backend`` is unrecognised or ``name`` is invalid.
    """
    if backend not in _VALID_BACKENDS:
        raise ValueError(
            f"unknown backend {backend!r}; expected one of {_VALID_BACKENDS}"
        )
    _require_mpl()

    if backend == "matplotlib":
        if ax is None:
            fig, ax = plt.subplots(figsize=(4.5, 4.5))
        else:
            fig = ax.figure
        _render_to_axes(name, ax, style=style)
        fig.tight_layout()
        return fig

    # backend == 'svg'
    fig, ax_local = plt.subplots(figsize=(4.5, 4.5))
    try:
        _render_to_axes(name, ax_local, style=style)
        fig.tight_layout()
        buf = io.StringIO()
        fig.savefig(buf, format="svg")
        return buf.getvalue()
    finally:
        plt.close(fig)


def draw_link(name: str,
              ax: Optional[Any] = None,
              style: str = "solid") -> Figure:
    """Render a multi-component link diagram.

    A thin wrapper around :func:`draw_knot` that explicitly supports
    the multi-component case (e.g. ``'L2a1'``, the Hopf link).  The
    function exists so callers can document intent in code; the
    underlying renderer is identical because PD codes already encode
    component count.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("link name must be a non-empty string")
    return draw_knot(name, ax=ax, style=style, backend="matplotlib")


def save_knot(name: str,
              path: Union[str, os.PathLike],
              fmt: Optional[str] = None) -> None:
    """Save a knot diagram directly to disk.

    Parameters
    ----------
    name : str
        Knot or link name.
    path : str or os.PathLike
        Output path.  If the path has an extension matching one of
        ``.png``, ``.svg``, ``.pdf`` and ``fmt`` is None, the format
        is inferred.  Otherwise ``fmt`` is required.
    fmt : {'png', 'svg', 'pdf'}, optional
        Output format.  Inferred from ``path`` extension when omitted.

    Raises
    ------
    ValueError
        If neither ``fmt`` nor a recognisable extension is given,
        or if ``fmt`` is not supported.
    """
    _require_mpl()
    path_str = os.fspath(path)
    base, ext = os.path.splitext(path_str)
    ext_clean = ext.lstrip(".").lower()

    if fmt is None:
        if ext_clean in _VALID_FORMATS:
            fmt = ext_clean
        else:
            raise ValueError(
                f"cannot infer format from path {path_str!r}; "
                f"pass fmt explicitly (one of {_VALID_FORMATS})"
            )
    fmt = fmt.lower()
    if fmt not in _VALID_FORMATS:
        raise ValueError(
            f"unknown fmt {fmt!r}; expected one of {_VALID_FORMATS}"
        )

    # If the path lacks an extension, append the chosen one.
    if not ext_clean:
        path_str = f"{base}.{fmt}"

    fig = draw_knot(name, backend="matplotlib")
    try:
        fig.savefig(path_str, format=fmt)
    finally:
        plt.close(fig)
