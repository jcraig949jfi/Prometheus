"""prometheus_math.viz._common — shared viz helpers.

Tiny utilities reused by ``viz.knot`` and ``viz.lfunctions``:

- :func:`_setup_matplotlib` — Agg-safe matplotlib initialisation for
  headless contexts (CI, batch render scripts).
- :func:`_resolve_path` — derive an output path + format pair from a
  user-supplied ``(path, fmt)`` argument.

These helpers are intentionally private (single-leading-underscore)
because they are implementation details, not part of the user API.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

_VALID_FORMATS = ("png", "svg", "pdf")


def _setup_matplotlib(backend: str = "matplotlib") -> None:
    """Ensure matplotlib is importable and using a non-interactive backend.

    Parameters
    ----------
    backend : str
        Logical backend name as passed to viz functions.  Accepted:
        ``'matplotlib'`` (default), ``'svg'``.  Both map onto the
        non-interactive ``'Agg'`` matplotlib backend so we never try to
        open a GUI window.

    Raises
    ------
    ImportError
        If matplotlib is not installed at all.
    ValueError
        If ``backend`` is not one of the supported logical backends.
    """
    if backend not in ("matplotlib", "svg"):
        raise ValueError(
            f"unknown backend {backend!r}; expected 'matplotlib' or 'svg'"
        )
    try:
        import matplotlib  # noqa: F401
    except Exception as exc:  # pragma: no cover - matplotlib is required
        raise ImportError(
            "prometheus_math.viz requires matplotlib. "
            "Install via `pip install matplotlib`."
        ) from exc
    # Only force Agg if no interactive backend has been chosen by the
    # caller.  This keeps notebook usage (inline backend) intact while
    # making CI / save_* paths safe.
    import matplotlib as _mpl
    current = _mpl.get_backend().lower()
    if current in ("agg", "module://matplotlib_inline.backend_inline"):
        return
    # Interactive backends are fine; explicit override only happens when
    # the caller selects 'svg' (we still need pyplot, but Agg is OK).
    if backend == "svg" and current not in ("agg",):
        try:
            _mpl.use("Agg", force=False)
        except Exception:  # pragma: no cover
            pass


def _resolve_path(path: Union[str, os.PathLike],
                  fmt: Optional[str] = None) -> Tuple[Path, str]:
    """Normalise a save path / format pair.

    Parameters
    ----------
    path : str or os.PathLike
        Filesystem path. May or may not have an extension.
    fmt : str, optional
        Explicit output format (one of ``png``, ``svg``, ``pdf``).
        If ``None``, the extension is read from ``path``.

    Returns
    -------
    (Path, str)
        Tuple of the resolved Path (with extension always present) and
        the chosen format string.

    Raises
    ------
    ValueError
        If neither ``fmt`` nor an extension on ``path`` provides a
        recognisable format, or if the format is not in
        ``{'png', 'svg', 'pdf'}``.
    """
    p = Path(os.fspath(path))
    ext_clean = p.suffix.lstrip(".").lower()

    if fmt is None:
        if ext_clean in _VALID_FORMATS:
            fmt = ext_clean
        else:
            raise ValueError(
                f"cannot infer format from path {str(p)!r}; "
                f"pass fmt explicitly (one of {_VALID_FORMATS})"
            )
    fmt = fmt.lower()
    if fmt not in _VALID_FORMATS:
        raise ValueError(
            f"unknown fmt {fmt!r}; expected one of {_VALID_FORMATS}"
        )

    # If path lacked an extension, append the chosen format.
    if not ext_clean:
        p = p.with_suffix(f".{fmt}")
    return p, fmt
