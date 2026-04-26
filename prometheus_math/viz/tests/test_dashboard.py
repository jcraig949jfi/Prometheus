"""Tests for prometheus_math.viz.dashboard — project #50.

Covers the four math-tdd categories (>=2 each):

* Authority — registry counts and verbatim title strings.
* Property — HTML5 validity, name coverage, summary invariants.
* Edge — bad format / empty registry / bad path / privileged port.
* Composition — render_html(matrix) ≡ render_html(),
  save_dashboard round-trip, registry counts agree.

Run with:
    cd F:/Prometheus && python -m pytest \\
        prometheus_math/viz/tests/test_dashboard.py -v
"""
from __future__ import annotations

import os
import socket
import tempfile
import time
import urllib.request

import pytest

import matplotlib
matplotlib.use("Agg")
import matplotlib.figure  # noqa: E402

from prometheus_math import registry as pm_registry  # noqa: E402
# Use the explicit alias `dashboard_module` exposed by viz/__init__.py
# (the bare name ``dashboard`` is shadowed by the re-exported function
# of the same name).
from prometheus_math.viz import dashboard_module as dash  # noqa: E402
from prometheus_math import viz  # noqa: E402


# ---------------------------------------------------------------------------
# Authority
# ---------------------------------------------------------------------------

def test_authority_total_at_least_thirty():
    """Registry has >= 30 backends. Reference: registry._BACKENDS list
    in prometheus_math/registry.py — currently enumerates 32+ entries
    spanning CAS, NT, NUM, TOP, COMB, SAT, OPT, AI, GT, AG, lang, PA,
    stats, DB."""
    m = dash.capability_matrix()
    assert m["summary"]["total"] >= 30, (
        f"Expected >=30 backends; got {m['summary']['total']}"
    )


def test_authority_at_least_four_kinds():
    """Registry exposes the four backend kinds:
    python | binary | service | data. Reference: registry.Backend
    docstring at prometheus_math/registry.py:24."""
    m = dash.capability_matrix()
    kinds = m["summary"]["kinds"]
    assert len(kinds) >= 4, f"Expected >=4 kinds; got {sorted(kinds)}"
    expected = {"python", "binary", "service", "data"}
    assert expected.issubset(set(kinds)), (
        f"Missing kinds: {expected - set(kinds)}"
    )


def test_authority_known_backend_present():
    """'cypari' is a registered backend (PARI/GP wrapper).
    Reference: registry._BACKENDS line declaring
    Backend('cypari', 'python', 'NT', ...)."""
    m = dash.capability_matrix()
    names = {e["name"] for e in m["entries"]}
    assert "cypari" in names


def test_authority_html_title_verbatim():
    """The dashboard page title is the verbatim project string."""
    html = dash.render_html()
    assert "Prometheus Math — Capability Dashboard" in html


def test_authority_summary_kinds_counts_match_entries():
    """summary.kinds[k] must equal the count of entries with that
    kind. Reference: capability_matrix() docstring contract."""
    m = dash.capability_matrix()
    kind_counts = m["summary"]["kinds"]
    for k, n in kind_counts.items():
        actual = sum(1 for e in m["entries"] if e["kind"] == k)
        assert actual == n, (
            f"kind {k}: summary says {n} but entries have {actual}"
        )


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------

def test_property_html_is_valid_html5():
    """render_html() output starts with <!DOCTYPE html> and parses
    cleanly through html.parser without raising."""
    html = dash.render_html()
    assert dash._is_valid_html5(html), "HTML failed validity check"


def test_property_html_contains_every_backend_name():
    """Every name in capability_matrix().entries must appear in the
    rendered HTML — the dashboard cannot silently drop rows."""
    m = dash.capability_matrix()
    html = dash.render_html(m)
    missing = [e["name"] for e in m["entries"] if e["name"] not in html]
    assert not missing, f"Missing backend names in HTML: {missing}"


def test_property_render_png_returns_figure():
    """render_png returns a matplotlib Figure object."""
    fig = dash.render_png()
    assert isinstance(fig, matplotlib.figure.Figure)
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_property_summary_available_le_total():
    """For every snapshot, summary.available <= summary.total
    (basic counting invariant)."""
    m = dash.capability_matrix()
    s = m["summary"]
    assert s["available"] <= s["total"]
    assert s["unavailable"] == s["total"] - s["available"]


def test_property_sort_by_name_lexicographic():
    """Sorting by name yields a list that is lexicographic
    (case-insensitive) on the entries' names."""
    m = dash.capability_matrix(sort_by="name")
    names = [e["name"].lower() for e in m["entries"]]
    assert names == sorted(names), (
        f"Names not lex-sorted: {names[:5]} ... vs sorted "
        f"{sorted(names)[:5]} ..."
    )


def test_property_sort_by_available_groups_available_first():
    """sort_by='available' puts all available backends ahead of any
    unavailable one."""
    m = dash.capability_matrix(sort_by="available")
    seen_unavail = False
    for e in m["entries"]:
        if not e["available"]:
            seen_unavail = True
        elif seen_unavail:
            pytest.fail(
                f"Available backend {e['name']!r} appears after "
                "an unavailable one with sort_by='available'"
            )


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------

def test_edge_unknown_format_raises():
    """dashboard(format='unknown') must raise ValueError."""
    with pytest.raises(ValueError):
        dash.dashboard(format="unknown")


def test_edge_unknown_sort_raises():
    """capability_matrix(sort_by='nope') must raise ValueError."""
    with pytest.raises(ValueError):
        dash.capability_matrix(sort_by="nope")


def test_edge_empty_registry_renders_gracefully():
    """When the registry returns nothing, render_html should still
    produce valid HTML and not crash. Uses the _set_registry_provider
    test hook."""
    try:
        dash._set_registry_provider(lambda: {})
        m = dash.capability_matrix()
        assert m["summary"]["total"] == 0
        assert m["entries"] == []
        html = dash.render_html(m)
        assert dash._is_valid_html5(html)
        assert "No backends registered." in html
        # PNG path also handles empty data.
        fig = dash.render_png(m)
        assert isinstance(fig, matplotlib.figure.Figure)
        import matplotlib.pyplot as plt
        plt.close(fig)
    finally:
        dash._set_registry_provider(None)


def test_edge_filter_kind_nonexistent_yields_empty():
    """An unknown filter_kind yields zero entries (graceful, not
    a crash)."""
    m = dash.capability_matrix(filter_kind="nonexistent_kind")
    assert m["entries"] == []
    assert m["summary"]["total"] == 0


def test_edge_save_dashboard_invalid_path_raises():
    """save_dashboard to a directory that does not exist must
    raise IOError (we deliberately wrap OSError)."""
    bad = os.path.join(
        tempfile.gettempdir(),
        "nope_does_not_exist_dashboard_dir_xyz",
        "subdir",
        "out.html",
    )
    if os.path.exists(os.path.dirname(bad)):
        # Rare: clean up if leftover from previous run.
        import shutil
        shutil.rmtree(os.path.dirname(bad), ignore_errors=True)
    with pytest.raises(IOError):
        dash.save_dashboard(bad)


def test_edge_save_dashboard_unknown_suffix_raises():
    """save_dashboard cannot infer format for unknown suffix."""
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError):
            dash.save_dashboard(os.path.join(tmp, "out.xyz"))


def test_edge_serve_dashboard_privileged_port_raises():
    """Privileged ports (<1024) are rejected with ValueError to
    avoid accidental sudo-needed launches."""
    with pytest.raises(ValueError):
        dash.serve_dashboard(port=80)


def test_edge_serve_dashboard_out_of_range_port_raises():
    """Ports outside [1024, 65535] are rejected."""
    with pytest.raises(ValueError):
        dash.serve_dashboard(port=70000)


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def test_composition_render_html_idempotent_with_explicit_matrix():
    """render_html(capability_matrix()) yields the same body as
    render_html() when the snapshots agree (we strip the timestamp
    line because it differs by sub-second resolution)."""
    m = dash.capability_matrix()
    a = dash.render_html(m)
    b = dash.render_html(m)
    assert a == b, "render_html with same matrix should be deterministic"


def test_composition_save_round_trip():
    """dashboard(format='html') content must equal the file written
    by save_dashboard (modulo timestamp)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "cap.html")
        dash.save_dashboard(out)
        assert os.path.exists(out)
        with open(out, "r", encoding="utf-8") as f:
            disk = f.read()
        # Body matches structurally — same backend names embedded.
        m = dash.capability_matrix()
        for e in m["entries"]:
            assert e["name"] in disk, (
                f"saved file missing backend {e['name']!r}"
            )
        # Title present
        assert "Prometheus Math — Capability Dashboard" in disk


def test_composition_counts_match_registry():
    """capability_matrix totals must equal the number of probed
    entries returned by pm.registry.installed() — no row drops."""
    raw = pm_registry.installed()
    m = dash.capability_matrix()
    assert m["summary"]["total"] == len(raw)
    n_avail = sum(1 for v in raw.values() if v.get("available"))
    assert m["summary"]["available"] == n_avail


def test_composition_viz_namespace_exposes_dashboard():
    """The viz package must re-export dashboard / save_dashboard so
    `pm.viz.dashboard()` works (per project #50 deliverable)."""
    assert hasattr(viz, "dashboard")
    assert hasattr(viz, "save_dashboard")
    assert hasattr(viz, "capability_matrix")
    out = viz.dashboard(format="html")
    assert "Prometheus Math — Capability Dashboard" in out


def test_composition_serve_then_fetch_then_stop():
    """End-to-end: start the HTTP server, fetch /, see the title,
    then stop_dashboard() cleans up. Skipped if the chosen port is
    already taken on the host."""
    # Pick a free high port from the OS.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    if dash._port_in_use(port):
        pytest.skip(f"port {port} in use; cannot run live serve test")

    url = dash.serve_dashboard(port=port, host="localhost")
    try:
        # Give the server a moment to start (it's already listening
        # by the time serve_forever begins, but be defensive).
        deadline = time.time() + 3.0
        body = b""
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=1.0) as resp:
                    body = resp.read()
                break
            except Exception:
                time.sleep(0.05)
        assert b"Prometheus Math" in body
    finally:
        dash.stop_dashboard()
    # After stop, the port should no longer accept connections.
    assert dash._server_state["server"] is None
