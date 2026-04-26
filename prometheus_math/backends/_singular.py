"""Singular subprocess gateway.

Singular (https://www.singular.uni-kl.de/) is the dominant open-source
computer algebra system for polynomial rings, Groebner bases,
factorization over algebraic extensions, primary decomposition, and
free resolutions. It ships with SageMath, runs natively on Linux/Mac,
and on Windows runs via Cygwin or WSL2.

This module provides a *gated* subprocess wrapper:

- ``is_installed()`` returns True iff the Singular executable is
  reachable on this machine. It probes ``shutil.which("Singular")``
  first, then a small set of common install locations (Cygwin, WSL2,
  SageMath bundle).
- ``run_session(commands)`` executes a Singular script over stdin and
  returns captured stdout. Raises ``RuntimeError`` if Singular is
  missing, errors out, or times out.
- ``execute(command)`` is a single-statement convenience wrapper.
- ``parse_polynomial(s)`` translates Singular's univariate polynomial
  syntax into a list of integer coefficients.

The wrapper is deliberately stateless: every call spawns a fresh
Singular process. This is slower than a long-lived REPL session but
much more robust under failure, which is what we want for a research
toolkit where individual queries are coarse-grained.

Forged: 2026-04-22 | Backend: singular | Category: AG
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from functools import lru_cache
from typing import Optional

# ---------------------------------------------------------------------------
# Install-location candidates
# ---------------------------------------------------------------------------
#
# Order: PATH first (handles the common case across all platforms), then
# fall back to a curated list of well-known install paths. The list is
# intentionally small — exotic installs should put Singular on PATH.

_CYGWIN_CANDIDATES = (
    r"C:\cygwin64\bin\Singular.exe",
    r"C:\cygwin64\bin\Singular",
    r"C:\cygwin\bin\Singular.exe",
    r"C:\cygwin\bin\Singular",
)

_SAGE_CANDIDATES_WIN = (
    # SageMath on Windows historically ships under Program Files.
    r"C:\Program Files\SageMath\local\bin\Singular.exe",
    r"C:\Program Files\SageMath\runtime\opt\sagemath\local\bin\Singular",
)

_UNIX_CANDIDATES = (
    "/usr/bin/Singular",
    "/usr/local/bin/Singular",
    "/opt/Singular/bin/Singular",
    "/opt/sagemath/local/bin/Singular",
)

# WSL2: Windows users often have Singular reachable as
#   wsl.exe Singular -q
# We don't enumerate paths inside WSL — instead, if `wsl.exe` is on
# PATH and `wsl.exe which Singular` returns a path, we treat WSL as
# the gateway. That probe is performed in `_probe_wsl()` below.


def _probe_wsl() -> Optional[str]:
    """If WSL is present and Singular is on PATH inside WSL, return the
    sentinel string ``"wsl"``. Returns None otherwise.

    The sentinel signals to ``run_session`` that commands must be sent
    via ``wsl.exe -- Singular -q`` instead of a direct invocation.
    """
    if shutil.which("wsl") is None and shutil.which("wsl.exe") is None:
        return None
    try:
        out = subprocess.run(
            ["wsl", "--", "which", "Singular"],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode == 0 and out.stdout.strip():
        return "wsl"
    return None


@lru_cache(maxsize=1)
def singular_path() -> Optional[str]:
    """Resolve the Singular executable path.

    Returns the absolute path to the binary, or the sentinel "wsl" when
    the only available Singular is inside WSL2, or None if Singular is
    not reachable on this machine.

    Cached: the first call probes the filesystem; subsequent calls are
    free. Call ``singular_path.cache_clear()`` if Singular is installed
    after the process started.
    """
    # 1. Direct lookup on PATH (works on Linux, macOS, native Windows
    #    if Cygwin's bin dir is on PATH, and inside Sage shells).
    direct = shutil.which("Singular")
    if direct:
        return direct

    # 2. Common install locations — Windows + Cygwin
    for cand in _CYGWIN_CANDIDATES + _SAGE_CANDIDATES_WIN + _UNIX_CANDIDATES:
        if os.path.isfile(cand):
            return cand

    # 3. WSL gateway (Windows only)
    if os.name == "nt":
        wsl = _probe_wsl()
        if wsl is not None:
            return wsl

    return None


def is_installed() -> bool:
    """True iff Singular is reachable.

    Uses ``singular_path()``. Returns False if no executable can be
    found and WSL is unavailable.
    """
    return singular_path() is not None


# ---------------------------------------------------------------------------
# Session execution
# ---------------------------------------------------------------------------

_INSTALL_HINT = (
    "Singular not installed. Install via https://www.singular.uni-kl.de/ "
    "or as a SageMath component, then ensure 'Singular' is on PATH or in "
    r"C:\cygwin64\bin\."
)


def _build_argv(path: str) -> list[str]:
    """Construct the argv to spawn Singular with banner suppressed."""
    if path == "wsl":
        return ["wsl", "--", "Singular", "-q"]
    return [path, "-q"]


def run_session(commands: str, timeout: float = 30) -> str:
    """Execute a Singular script over stdin and return stdout.

    Parameters
    ----------
    commands:
        Singular source. Should end with ``quit;`` to terminate the
        interpreter cleanly. If absent, ``quit;`` is appended.
    timeout:
        Wall-clock seconds before the subprocess is killed. Default 30s.

    Raises
    ------
    RuntimeError
        If Singular is not installed, exits non-zero, or times out.
    """
    path = singular_path()
    if path is None:
        raise RuntimeError(_INSTALL_HINT)

    script = commands if commands.rstrip().endswith("quit;") else commands.rstrip() + "\nquit;\n"
    argv = _build_argv(path)
    try:
        proc = subprocess.run(
            argv,
            input=script,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Singular timed out after {timeout}s")
    except FileNotFoundError as e:
        raise RuntimeError(f"Singular launch failed: {e}")

    if proc.returncode != 0:
        # Singular sometimes returns non-zero on warnings; surface stderr.
        raise RuntimeError(
            f"Singular exited {proc.returncode}: "
            f"{(proc.stderr or proc.stdout or '').strip()[:500]}"
        )
    # Singular prints "// ** ..." warnings to stderr and to stdout. We
    # strip them on the consumer side, not here, because some operations
    # encode useful information in those lines.
    return proc.stdout


def execute(command: str, timeout: float = 30) -> str:
    """Run a single Singular statement and return stdout.

    Convenience wrapper around ``run_session`` for one-liners. The
    command should not include a trailing ``quit;`` — it is appended
    automatically.
    """
    cmd = command.strip()
    if not cmd.endswith(";"):
        cmd += ";"
    return run_session(cmd, timeout=timeout)


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

# Singular's polynomial pretty-printer emits forms like
#   2x2+3x-5
#   x3-x2+1
# i.e. exponents are juxtaposed without `**` or `^`. Coefficients can be
# negative and may include rationals (e.g. `1/2`).

_TERM_RE = re.compile(
    r"""
    (?P<sign>[+-]?)
    \s*
    (?P<coef>\d+(?:/\d+)?)?
    \s*
    (?P<var>[A-Za-z_]\w*)?
    (?P<exp>\d+)?
    """,
    re.VERBOSE,
)


def parse_polynomial(s: str) -> Optional[list[int]]:
    """Parse a Singular univariate polynomial output into integer coeffs.

    Returns coefficients in *descending* degree order (so ``2x^2+3x-5``
    parses as ``[2, 3, -5]``). Returns None on parse failure rather
    than raising — callers can then choose to re-route through sympy
    or report up.

    Limitations
    -----------
    - Only univariate polynomials with integer coefficients are
      handled by the fast path. For rationals or multivariate output
      the caller should fall back to ``sympy.sympify``.
    - Whitespace and ``*`` between coef and variable are tolerated;
      ``^`` for exponents is also accepted.
    """
    if not isinstance(s, str):
        return None
    text = s.strip()
    if not text:
        return None

    # Normalise common variants: drop '*', convert '^' to nothing
    # (since Singular pretty-printing uses juxtaposition).
    text = text.replace(" ", "").replace("*", "")
    text = re.sub(r"\^", "", text)

    # Split into signed terms while preserving the leading sign.
    # We add a leading '+' so the regex captures the first term too.
    if not text.startswith(("+", "-")):
        text = "+" + text

    coeffs: dict[int, int] = {}
    pos = 0
    n = len(text)
    while pos < n:
        # Each term: [+-]<coef?><var?><exp?>
        # Variable name: letter optionally followed by letters/underscores
        # (digits are reserved for the exponent in Singular's output).
        m = re.match(r"([+-])(\d+)?([A-Za-z_][A-Za-z_]*)?(\d+)?", text[pos:])
        if not m or m.end() == 0:
            return None
        sign_s, coef_s, var_s, exp_s = m.group(1), m.group(2), m.group(3), m.group(4)

        # Empty match guard
        if coef_s is None and var_s is None:
            return None

        try:
            coef = int(coef_s) if coef_s is not None else 1
        except ValueError:
            # rational? bail out
            return None
        if sign_s == "-":
            coef = -coef

        if var_s is None:
            degree = 0
        elif exp_s is None:
            degree = 1
        else:
            try:
                degree = int(exp_s)
            except ValueError:
                return None

        coeffs[degree] = coeffs.get(degree, 0) + coef
        pos += m.end()

    if not coeffs:
        return None

    max_deg = max(coeffs)
    return [coeffs.get(d, 0) for d in range(max_deg, -1, -1)]


# ---------------------------------------------------------------------------
# Output cleanup
# ---------------------------------------------------------------------------

def strip_singular_chatter(out: str) -> str:
    """Drop Singular's status chatter ("// ...") from stdout.

    Useful when the caller cares only about polynomial/result lines.
    """
    keep = []
    for line in out.splitlines():
        if line.startswith("//"):
            continue
        if not line.strip():
            continue
        keep.append(line.rstrip())
    return "\n".join(keep)


__all__ = [
    "is_installed",
    "singular_path",
    "run_session",
    "execute",
    "parse_polynomial",
    "strip_singular_chatter",
]
