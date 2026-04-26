"""Tests for prometheus_math.viz — knot/link diagram rendering.

Project #36 from techne/PROJECT_BACKLOG_1000.md. Per the math-tdd skill,
each operation in the viz module is exercised across the four required
categories:

    * Authority — published crossing numbers from Rolfsen / KnotInfo.
    * Property — invariants that hold across the catalogue
      (single-component knots have num_components == 1, etc.).
    * Edge — invalid name, unknown backend, missing extension.
    * Composition — knot_diagram_data --> save_knot, draw_knot
      output sanity-checked against the data dict.

Skip-with-clear-message when SnapPy is not importable so the gallery
still runs on machines lacking the optional dep.

Run with:
    cd F:/Prometheus && python -m pytest \\
        prometheus_math/tests/test_viz.py -v
"""
from __future__ import annotations

import os
import tempfile
import shutil

import pytest

# Headless-safe matplotlib must come BEFORE any pyplot usage anywhere
# in the import graph (the viz module imports pyplot eagerly).
import matplotlib
matplotlib.use("Agg")

snappy = pytest.importorskip(
    "snappy",
    reason=(
        "SnapPy is not installed; the knot-diagram tests require it. "
        "Install via `pip install snappy`."
    ),
)

from prometheus_math import viz  # noqa: E402


# ---------------------------------------------------------------------------
# Authority-based tests (Rolfsen / KnotInfo crossing numbers)
# ---------------------------------------------------------------------------

def test_authority_crossing_count_4_1():
    """4_1 (figure-eight) has 4 crossings.

    Reference: Rolfsen, "Knots and Links" (1976), knot table; KnotInfo
    entry 4_1 lists ``crossing_number = 4``.
    """
    data = viz.knot_diagram_data("4_1")
    assert len(data["crossings"]) == 4
    assert data["num_components"] == 1


def test_authority_crossing_count_3_1():
    """3_1 (trefoil) has 3 crossings.

    Reference: Rolfsen knot table; KnotInfo entry 3_1.
    """
    data = viz.knot_diagram_data("3_1")
    assert len(data["crossings"]) == 3
    assert data["num_components"] == 1


def test_authority_crossing_count_8_19_non_alternating():
    """8_19 is the famous non-alternating 8-crossing knot.

    Reference: Rolfsen knot table; KnotInfo entry 8_19. 8_19 is the
    smallest non-alternating prime knot.
    """
    data = viz.knot_diagram_data("8_19")
    assert len(data["crossings"]) == 8
    assert data["num_components"] == 1


def test_authority_hopf_link_L2a1():
    """L2a1 (Hopf link) has 2 components and 2 crossings.

    Reference: LinkInfo / Rolfsen catalog. The Hopf link is the
    simplest non-trivial 2-component link.
    """
    data = viz.knot_diagram_data("L2a1")
    assert data["num_components"] == 2
    assert len(data["crossings"]) == 2


# ---------------------------------------------------------------------------
# Property-based tests (invariants over the catalogue)
# ---------------------------------------------------------------------------

# Standard (minimal) crossing numbers from Rolfsen.
_KNOT_CROSSING_TABLE = {
    "3_1": 3,
    "4_1": 4,
    "5_1": 5,
    "5_2": 5,
    "6_1": 6,
    "6_2": 6,
    "6_3": 6,
    "7_2": 7,
}


@pytest.mark.parametrize("name", list(_KNOT_CROSSING_TABLE.keys()))
def test_property_knots_have_one_component(name):
    """Property: every entry in {3_1, 4_1, 5_1, ..., 7_2} is a knot.

    A knot is a single-component link by definition (Rolfsen ch. 1).
    """
    data = viz.knot_diagram_data(name)
    assert data["num_components"] == 1


@pytest.mark.parametrize("name,expected", list(_KNOT_CROSSING_TABLE.items()))
def test_property_crossing_count_matches_catalogue(name, expected):
    """Property: SnapPy PD code crossings == published crossing number.

    For minimal-crossing diagrams of small prime knots this is the
    standard crossing number from the Rolfsen / KnotInfo catalogue.
    """
    data = viz.knot_diagram_data(name)
    assert len(data["crossings"]) == expected


def test_property_determinism_across_repeated_calls():
    """Property: drawing twice with the same backend yields equivalent
    primitive data.

    We compare the data dict (PD code, crossings positions) rather than
    pixels to keep the test renderer-version-independent.
    """
    a = viz.knot_diagram_data("5_2")
    b = viz.knot_diagram_data("5_2")
    assert a["pd_code"] == b["pd_code"]
    assert a["crossings"] == b["crossings"]
    assert a["num_components"] == b["num_components"]
    # Strand layout is also deterministic (same n-gon, same Bezier samples).
    assert a["strands"] == b["strands"]


def test_property_strand_count_proportional_to_crossings():
    """Property: a diagram with n crossings has 2n PD-code edges, hence
    up to 2n strand segments in the layout.

    Holds for any non-trivial prime knot in the catalogue.
    """
    for name, c in _KNOT_CROSSING_TABLE.items():
        data = viz.knot_diagram_data(name)
        # Each edge contributes one strand segment; 2n total.
        assert len(data["strands"]) == 2 * c, (
            f"{name}: expected {2*c} strand segments, got {len(data['strands'])}"
        )


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_invalid_knot_name_raises_valueerror():
    """Edge: a non-catalogued knot name produces ValueError with the
    offending name embedded in the message.
    """
    with pytest.raises(ValueError) as excinfo:
        viz.knot_diagram_data("not_a_real_knot_99")
    assert "not_a_real_knot_99" in str(excinfo.value)


def test_edge_empty_name_raises_valueerror():
    """Edge: empty / whitespace-only name raises ValueError."""
    with pytest.raises(ValueError):
        viz.knot_diagram_data("")
    with pytest.raises(ValueError):
        viz.knot_diagram_data("   ")


def test_edge_unknown_backend_raises_valueerror():
    """Edge: backend not in {'matplotlib', 'svg'} raises ValueError."""
    with pytest.raises(ValueError) as excinfo:
        viz.draw_knot("4_1", backend="opengl")
    assert "opengl" in str(excinfo.value)


def test_edge_save_path_without_extension_uses_fmt():
    """Edge: a path with no extension infers the file extension from
    the ``fmt`` argument and writes a file accordingly.
    """
    tmpdir = tempfile.mkdtemp(prefix="pm_viz_test_")
    try:
        path_no_ext = os.path.join(tmpdir, "trefoil")
        viz.save_knot("3_1", path_no_ext, fmt="png")
        # save_knot appends the extension; verify that the augmented
        # path exists.
        augmented = path_no_ext + ".png"
        assert os.path.isfile(augmented), (
            f"expected {augmented} to exist; tmpdir contents: "
            f"{os.listdir(tmpdir)}"
        )
        assert os.path.getsize(augmented) > 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_edge_save_path_no_fmt_no_extension_raises():
    """Edge: missing fmt + missing extension -> ValueError."""
    tmpdir = tempfile.mkdtemp(prefix="pm_viz_test_")
    try:
        path = os.path.join(tmpdir, "noext")
        with pytest.raises(ValueError):
            viz.save_knot("3_1", path)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_edge_save_unknown_format_raises():
    """Edge: explicitly passing an unsupported fmt -> ValueError."""
    tmpdir = tempfile.mkdtemp(prefix="pm_viz_test_")
    try:
        path = os.path.join(tmpdir, "out.bmp")
        with pytest.raises(ValueError):
            viz.save_knot("3_1", path, fmt="bmp")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_data_then_save_writes_nonempty_png():
    """Composition: knot_diagram_data --> save_knot --> file on disk.

    Exercises the data-extraction and file-writing chain end-to-end.
    """
    tmpdir = tempfile.mkdtemp(prefix="pm_viz_test_")
    try:
        data = viz.knot_diagram_data("4_1")
        assert len(data["crossings"]) == 4  # sanity from authority test
        out = os.path.join(tmpdir, "fig8.png")
        viz.save_knot("4_1", out)
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 100  # non-trivial PNG
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_composition_data_then_save_svg_string_and_file():
    """Composition: backend='svg' returns a string AND writing to .svg
    on disk produces a valid SVG document.
    """
    s = viz.draw_knot("3_1", backend="svg")
    assert isinstance(s, str)
    assert "<svg" in s.lower()

    tmpdir = tempfile.mkdtemp(prefix="pm_viz_test_")
    try:
        out = os.path.join(tmpdir, "trefoil.svg")
        viz.save_knot("3_1", out)
        with open(out, "r", encoding="utf-8") as fh:
            head = fh.read(2048).lower()
        assert "<svg" in head
        assert os.path.getsize(out) > 100
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_composition_draw_knot_axes_has_strand_artists():
    """Composition: draw_knot output figure has at least as many line
    artists (strand segments) as the diagram has crossings.

    This is a structural sanity check: each crossing contributes two
    strand segments to the layout, so #lines >= #crossings.
    """
    fig = viz.draw_knot("5_2")
    try:
        ax = fig.axes[0]
        # Lines includes both strand polylines and crossing-marker dots.
        # Strand segments are plotted with linestyle != 'None'.
        strand_lines = [
            ln for ln in ax.get_lines()
            if ln.get_linestyle() not in ("None", "none")
        ]
        # Expect 2n strand polylines for an n-crossing knot.
        data = viz.knot_diagram_data("5_2")
        assert len(strand_lines) >= len(data["crossings"]), (
            f"expected >= {len(data['crossings'])} strand lines, "
            f"got {len(strand_lines)}"
        )
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_composition_draw_link_hopf_two_components_render():
    """Composition: draw_link on the Hopf link (L2a1) renders without
    error and the underlying data reports two components.
    """
    data = viz.knot_diagram_data("L2a1")
    assert data["num_components"] == 2

    fig = viz.draw_link("L2a1")
    try:
        # Sanity: figure has at least one axis with content.
        assert len(fig.axes) >= 1
        ax = fig.axes[0]
        assert len(ax.get_lines()) > 0
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_composition_layout_consistent_with_data():
    """Composition: knot_layout_canonical(name) is the same object the
    data dict exposes under ``strands``.
    """
    layout = viz.knot_layout_canonical("4_1")
    data = viz.knot_diagram_data("4_1")
    assert layout == data["strands"]
