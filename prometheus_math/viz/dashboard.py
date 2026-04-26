"""prometheus_math.viz.dashboard — capability-matrix dashboard (project #50).

Renders ``pm.registry.installed()`` as a live capability grid in three
surfaces:

1. ``render_html(matrix=None)`` — self-contained HTML page (CSS embedded)
   suitable for opening in a browser or saving to disk.
2. ``render_png(matrix=None, ax=None)`` — matplotlib heat-map figure for
   reports / notebooks.
3. ``dashboard(format='jupyter')`` — IPython display object for inline
   notebook rendering.

The HTML page has client-side filter / sort buttons (vanilla JS, no
external dependencies). The PNG path uses the Agg backend so it is
headless-safe.

A tiny optional :func:`serve_dashboard` spins up
``http.server.BaseHTTPRequestHandler`` in a background thread; tests
should pair it with :func:`stop_dashboard` to terminate cleanly.

Example
-------
>>> from prometheus_math import viz
>>> html = viz.dashboard(format='html')
>>> viz.save_dashboard("/tmp/cap.html")
"""
from __future__ import annotations

import datetime as _dt
import html as _html
import http.server as _http_server
import io as _io
import socket as _socket
import threading as _threading
from html.parser import HTMLParser as _HTMLParser
from typing import Any, Callable, Optional

# Kept lazy so test environments without matplotlib still load the
# module (the html surface is matplotlib-free).
_VALID_FORMATS = ("html", "png", "jupyter")

_TITLE = "Prometheus Math — Capability Dashboard"


# ---------------------------------------------------------------------------
# Registry adapter
# ---------------------------------------------------------------------------

# Allow tests to monkeypatch this without poking the real registry.
_registry_provider: Optional[Callable[[], dict]] = None


def _get_installed() -> dict:
    if _registry_provider is not None:
        return _registry_provider()
    from prometheus_math import registry as _registry
    return _registry.installed()


def _set_registry_provider(fn: Optional[Callable[[], dict]]) -> None:
    """Test hook: override the registry source. Pass ``None`` to reset."""
    global _registry_provider
    _registry_provider = fn


def capability_matrix(filter_kind: Optional[str] = None,
                      sort_by: str = "category") -> dict:
    """Return a structured snapshot of the capability registry.

    Parameters
    ----------
    filter_kind:
        If given, restrict to entries with ``entry['kind'] == filter_kind``.
        An unknown kind yields an empty entries list (consistent with
        "no matches").
    sort_by:
        One of ``'category'``, ``'name'``, ``'available'``.  Sorting is
        stable; ``'available'`` puts available backends first then sorts
        within each bucket by name.

    Returns
    -------
    dict
        ``{'categories': [...], 'kinds': [...],
        'entries': [{'name', 'kind', 'category', 'available', 'version',
        'description', 'error'}, ...],
        'summary': {'total': int, 'available': int, 'unavailable': int,
        'kinds': {kind: count}}}``.
    """
    raw = _get_installed()
    entries: list[dict[str, Any]] = []
    for name, info in raw.items():
        entry = {
            "name": name,
            "kind": info.get("kind", "unknown"),
            "category": info.get("category", "unknown"),
            "available": bool(info.get("available", False)),
            "version": info.get("version"),
            "description": info.get("description", ""),
            "error": info.get("error"),
        }
        if filter_kind is None or entry["kind"] == filter_kind:
            entries.append(entry)

    if sort_by == "name":
        entries.sort(key=lambda e: e["name"].lower())
    elif sort_by == "available":
        entries.sort(key=lambda e: (not e["available"], e["name"].lower()))
    elif sort_by == "category":
        entries.sort(key=lambda e: (e["category"], e["name"].lower()))
    else:
        raise ValueError(
            f"sort_by must be one of 'category', 'name', 'available'; "
            f"got {sort_by!r}"
        )

    categories = sorted({e["category"] for e in entries})
    kinds = sorted({e["kind"] for e in entries})
    kind_counts: dict[str, int] = {}
    for e in entries:
        kind_counts[e["kind"]] = kind_counts.get(e["kind"], 0) + 1

    n_total = len(entries)
    n_avail = sum(1 for e in entries if e["available"])
    return {
        "categories": categories,
        "kinds": kinds,
        "entries": entries,
        "summary": {
            "total": n_total,
            "available": n_avail,
            "unavailable": n_total - n_avail,
            "kinds": kind_counts,
        },
    }


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_CSS = """
*{box-sizing:border-box;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;}
body{background:#0d1117;color:#c9d1d9;margin:0;padding:24px;}
h1{font-size:22px;margin:0 0 4px 0;color:#58a6ff;}
.meta{font-size:12px;color:#8b949e;margin-bottom:16px;}
.summary{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;}
.summary .card{background:#161b22;border:1px solid #30363d;padding:12px 16px;border-radius:6px;}
.summary .card .num{font-size:24px;font-weight:600;color:#58a6ff;}
.summary .card .lbl{font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;}
.controls{margin:16px 0;display:flex;gap:8px;flex-wrap:wrap;}
.controls button{background:#21262d;color:#c9d1d9;border:1px solid #30363d;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:12px;}
.controls button.active{background:#1f6feb;border-color:#1f6feb;color:#fff;}
.controls button:hover{background:#30363d;}
table{width:100%;border-collapse:collapse;background:#0d1117;}
th{text-align:left;padding:10px 12px;background:#161b22;border-bottom:2px solid #30363d;font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:#8b949e;cursor:pointer;}
td{padding:10px 12px;border-bottom:1px solid #21262d;font-size:13px;}
tr:hover td{background:#161b22;}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.dot.green{background:#3fb950;box-shadow:0 0 6px #3fb950aa;}
.dot.red{background:#f85149;}
.dot.gray{background:#6e7681;}
.kind{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;text-transform:uppercase;letter-spacing:.5px;}
.kind.python{background:#1f6feb33;color:#58a6ff;}
.kind.binary{background:#a371f733;color:#a371f7;}
.kind.service{background:#3fb95033;color:#3fb950;}
.kind.data{background:#d29922aa;color:#fff;}
.kind.unknown{background:#6e768133;color:#8b949e;}
.version{font-family:Menlo,Consolas,monospace;font-size:11px;color:#8b949e;}
.error{color:#f85149;font-size:11px;font-style:italic;}
.empty{padding:48px;text-align:center;color:#8b949e;}
"""

_JS = """
(function(){
  function rerender(){
    var k=document.querySelector('.controls .kind-btn.active');
    var s=document.querySelector('.controls .sort-btn.active');
    var kind=k?k.dataset.kind:'';
    var sort=s?s.dataset.sort:'category';
    var rows=Array.from(document.querySelectorAll('#cap-table tbody tr'));
    rows.forEach(function(r){
      var rk=r.dataset.kind;
      r.style.display=(kind===''||rk===kind)?'':'none';
    });
    var tbody=document.querySelector('#cap-table tbody');
    var visible=rows.filter(function(r){return r.style.display!=='none';});
    visible.sort(function(a,b){
      if(sort==='name')return a.dataset.name.localeCompare(b.dataset.name);
      if(sort==='available'){
        var av=a.dataset.available==='true'?0:1, bv=b.dataset.available==='true'?0:1;
        return av-bv||a.dataset.name.localeCompare(b.dataset.name);
      }
      return a.dataset.category.localeCompare(b.dataset.category)||a.dataset.name.localeCompare(b.dataset.name);
    });
    visible.forEach(function(r){tbody.appendChild(r);});
  }
  document.querySelectorAll('.controls button').forEach(function(b){
    b.addEventListener('click',function(){
      var grp=b.classList.contains('kind-btn')?'kind-btn':'sort-btn';
      document.querySelectorAll('.controls .'+grp).forEach(function(o){o.classList.remove('active');});
      b.classList.add('active');
      rerender();
    });
  });
})();
"""


def render_html(matrix: Optional[dict] = None) -> str:
    """Render the capability matrix as a self-contained HTML page.

    Parameters
    ----------
    matrix:
        Optional precomputed :func:`capability_matrix` result.  If
        ``None``, a fresh snapshot is taken.

    Returns
    -------
    str
        UTF-8 HTML5 string (no external CSS / JS).
    """
    if matrix is None:
        matrix = capability_matrix()

    ts = _dt.datetime.now().isoformat(timespec="seconds")
    summary = matrix["summary"]
    entries = matrix["entries"]
    kinds_present = sorted(matrix["kinds"]) if matrix["kinds"] else []

    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en"><head>')
    parts.append('<meta charset="utf-8">')
    parts.append(f"<title>{_html.escape(_TITLE)}</title>")
    parts.append(f"<style>{_CSS}</style>")
    parts.append("</head><body>")
    parts.append(f"<h1>{_html.escape(_TITLE)}</h1>")
    parts.append(
        f'<div class="meta">Last refresh: {_html.escape(ts)} '
        f'&middot; Source: <code>pm.registry.installed()</code></div>'
    )

    # Summary cards
    parts.append('<div class="summary">')
    parts.append(
        f'<div class="card"><div class="num">{summary["total"]}</div>'
        '<div class="lbl">Backends</div></div>'
    )
    parts.append(
        f'<div class="card"><div class="num">{summary["available"]}</div>'
        '<div class="lbl">Available</div></div>'
    )
    parts.append(
        f'<div class="card"><div class="num">{summary["unavailable"]}</div>'
        '<div class="lbl">Unavailable</div></div>'
    )
    for k, n in sorted(summary["kinds"].items()):
        parts.append(
            f'<div class="card"><div class="num">{n}</div>'
            f'<div class="lbl">{_html.escape(k)}</div></div>'
        )
    parts.append("</div>")

    # Filter / sort controls
    parts.append('<div class="controls">')
    parts.append(
        '<button class="kind-btn active" data-kind="">All</button>'
    )
    for k in kinds_present:
        parts.append(
            f'<button class="kind-btn" data-kind="{_html.escape(k)}">'
            f'{_html.escape(k)}</button>'
        )
    parts.append('<span style="flex:1"></span>')
    parts.append(
        '<button class="sort-btn active" data-sort="category">'
        'Sort: category</button>'
    )
    parts.append(
        '<button class="sort-btn" data-sort="name">Sort: name</button>'
    )
    parts.append(
        '<button class="sort-btn" data-sort="available">'
        'Sort: available</button>'
    )
    parts.append("</div>")

    # Table
    if not entries:
        parts.append('<div class="empty">No backends registered.</div>')
    else:
        parts.append('<table id="cap-table"><thead><tr>')
        for col in ("Name", "Kind", "Category", "Status", "Version", "Notes"):
            parts.append(f"<th>{col}</th>")
        parts.append("</tr></thead><tbody>")
        for e in entries:
            avail = e["available"]
            dot = "green" if avail else (
                "gray" if e.get("error") is None else "red"
            )
            status_text = "available" if avail else "unavailable"
            kind_class = e["kind"] if e["kind"] in (
                "python", "binary", "service", "data"
            ) else "unknown"
            ver = e.get("version") or ""
            err = e.get("error") or e.get("description") or ""
            parts.append(
                "<tr "
                f'data-name="{_html.escape(e["name"])}" '
                f'data-kind="{_html.escape(e["kind"])}" '
                f'data-category="{_html.escape(e["category"])}" '
                f'data-available="{"true" if avail else "false"}">'
                f'<td><strong>{_html.escape(e["name"])}</strong></td>'
                f'<td><span class="kind {kind_class}">'
                f'{_html.escape(e["kind"])}</span></td>'
                f'<td>{_html.escape(e["category"])}</td>'
                f'<td><span class="dot {dot}"></span>{status_text}</td>'
                f'<td class="version">{_html.escape(str(ver))}</td>'
                f'<td class="error" '
                f'style="color:{"#f85149" if e.get("error") else "#8b949e"};'
                f'font-style:{"italic" if e.get("error") else "normal"}">'
                f'{_html.escape(str(err))}</td>'
                "</tr>"
            )
        parts.append("</tbody></table>")

    parts.append(f"<script>{_JS}</script>")
    parts.append("</body></html>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# PNG / matplotlib rendering
# ---------------------------------------------------------------------------

def render_png(matrix: Optional[dict] = None, ax=None):
    """Render the capability matrix as a matplotlib heat-map figure.

    Parameters
    ----------
    matrix:
        Optional precomputed :func:`capability_matrix` result.
    ax:
        Optional matplotlib axis to draw into.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import matplotlib  # noqa: F401
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy as np

    if matrix is None:
        matrix = capability_matrix(sort_by="available")

    entries = matrix["entries"]
    n = len(entries)

    if ax is None:
        fig_h = max(2.0, 0.28 * max(n, 1) + 1.5)
        fig, ax = plt.subplots(figsize=(8, fig_h))
    else:
        fig = ax.figure

    if n == 0:
        ax.text(0.5, 0.5, "No backends registered.",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        ax.set_title(_TITLE)
        return fig

    # 2 = available, 1 = unavailable-with-error, 0 = unavailable-unknown
    grid = np.zeros((n, 1), dtype=int)
    labels: list[str] = []
    for i, e in enumerate(entries):
        if e["available"]:
            grid[i, 0] = 2
        elif e.get("error"):
            grid[i, 0] = 1
        else:
            grid[i, 0] = 0
        labels.append(f"{e['name']} [{e['kind']}]")

    cmap = ListedColormap(["#6e7681", "#f85149", "#3fb950"])
    ax.imshow(grid, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xticks([0])
    ax.set_xticklabels(["status"])
    ax.set_title(
        f"{_TITLE}  "
        f"({matrix['summary']['available']}/{matrix['summary']['total']} "
        f"available)"
    )
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Top-level entrypoint
# ---------------------------------------------------------------------------

def dashboard(format: str = "html",
              filter_kind: Optional[str] = None,
              sort_by: str = "category"):
    """Render the live capability dashboard.

    Parameters
    ----------
    format:
        ``'html'`` returns an HTML5 string; ``'png'`` returns a
        matplotlib Figure; ``'jupyter'`` returns an
        ``IPython.display.HTML`` object (or the raw string with a
        ``_repr_html_`` shim if IPython is not installed).
    filter_kind:
        Restrict to one of ``'python'``, ``'binary'``, ``'service'``,
        ``'data'``.
    sort_by:
        ``'category'`` (default), ``'name'``, or ``'available'``.
    """
    if format not in _VALID_FORMATS:
        raise ValueError(
            f"format must be one of {_VALID_FORMATS}; got {format!r}"
        )
    matrix = capability_matrix(filter_kind=filter_kind, sort_by=sort_by)
    if format == "html":
        return render_html(matrix)
    if format == "png":
        return render_png(matrix)
    # 'jupyter'
    html_str = render_html(matrix)
    try:
        from IPython.display import HTML  # type: ignore
        return HTML(html_str)
    except Exception:
        class _HTMLShim:
            def __init__(self, s: str):
                self._s = s

            def _repr_html_(self) -> str:
                return self._s

            def __str__(self) -> str:
                return self._s

        return _HTMLShim(html_str)


def save_dashboard(path: str, format: Optional[str] = None) -> None:
    """Compute and save the dashboard in one call.

    The output format is inferred from ``path``'s suffix unless
    ``format`` is given.  Supported suffixes: ``.html``, ``.htm``,
    ``.png``.
    """
    if format is None:
        lower = path.lower()
        if lower.endswith(".html") or lower.endswith(".htm"):
            format = "html"
        elif lower.endswith(".png"):
            format = "png"
        else:
            raise ValueError(
                f"Cannot infer format from path {path!r}; pass format= "
                "explicitly."
            )
    if format not in ("html", "png"):
        raise ValueError(
            f"save_dashboard format must be 'html' or 'png'; got "
            f"{format!r}"
        )
    matrix = capability_matrix()
    if format == "html":
        html_str = render_html(matrix)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_str)
        except OSError as e:
            raise IOError(f"Cannot write dashboard to {path!r}: {e}") from e
    else:  # png
        fig = render_png(matrix)
        try:
            fig.savefig(path, dpi=120, bbox_inches="tight")
        except (OSError, ValueError) as e:
            raise IOError(f"Cannot write dashboard to {path!r}: {e}") from e
        finally:
            import matplotlib.pyplot as plt
            plt.close(fig)


# ---------------------------------------------------------------------------
# Optional HTTP server (background thread)
# ---------------------------------------------------------------------------

_server_state: dict[str, Any] = {"server": None, "thread": None}


class _DashboardHandler(_http_server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003 - silence stdout
        return

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html", "/dashboard"):
            html_str = render_html()
            payload = html_str.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"not found")


def serve_dashboard(port: int = 8765, host: str = "localhost") -> str:
    """Start a tiny HTTP server in a background thread.

    Returns the URL the dashboard is reachable at. The server is
    non-blocking; call :func:`stop_dashboard` to terminate.

    Privileged ports (< 1024) are rejected with ``ValueError`` to avoid
    accidental sudo-needed launches.
    """
    if port < 1024:
        raise ValueError(
            f"port {port} is privileged (< 1024); pick a high port"
        )
    if not (1024 <= port <= 65535):
        raise ValueError(
            f"port must be in [1024, 65535]; got {port}"
        )
    if _server_state["server"] is not None:
        raise RuntimeError(
            "dashboard server already running; call stop_dashboard() first"
        )

    try:
        server = _http_server.ThreadingHTTPServer(
            (host, port), _DashboardHandler
        )
    except OSError as e:
        raise OSError(
            f"cannot bind dashboard to {host}:{port}: {e}"
        ) from e

    thread = _threading.Thread(
        target=server.serve_forever, name="prometheus-dashboard",
        daemon=True,
    )
    thread.start()
    _server_state["server"] = server
    _server_state["thread"] = thread
    return f"http://{host}:{port}/"


def stop_dashboard() -> None:
    """Terminate any running serve_dashboard() thread cleanly."""
    server = _server_state.get("server")
    thread = _server_state.get("thread")
    if server is not None:
        try:
            server.shutdown()
            server.server_close()
        finally:
            _server_state["server"] = None
    if thread is not None:
        thread.join(timeout=2.0)
        _server_state["thread"] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_html5(html_str: str) -> bool:
    """Cheap HTML5 validity check using the stdlib HTML parser."""
    if not html_str.lstrip().lower().startswith("<!doctype html"):
        return False
    parser = _HTMLParser()
    try:
        parser.feed(html_str)
        parser.close()
    except Exception:
        return False
    return True


def _port_in_use(port: int, host: str = "localhost") -> bool:
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    s.settimeout(0.2)
    try:
        return s.connect_ex((host, port)) == 0
    finally:
        s.close()


__all__ = [
    "capability_matrix",
    "dashboard",
    "render_html",
    "render_png",
    "save_dashboard",
    "serve_dashboard",
    "stop_dashboard",
]
