"""TOOL_HYPERBOLIC_VOLUME — Hyperbolic volume of a knot/link complement.

For a hyperbolic 3-manifold M = S^3 \\ K, the hyperbolic volume vol(M) is a
topological invariant (Mostow rigidity). Non-hyperbolic knots (torus knots,
satellite knots without hyperbolic pieces) return 0.

Wraps SnapPy (Culler-Dunfield-Weeks). Authority for all published volumes.

Interface:
    hyperbolic_volume(knot) -> float
    hyperbolic_volume_hp(knot, digits=60) -> str           # arbitrary precision
    is_hyperbolic(knot, tol=1e-6) -> bool
    volume_conjecture_ratio(knot, N=100) -> float | None   # helper

Forged: 2026-04-21 | Tier: 1 (Python/SnapPy) | REQ-003
Tested against: knotinfo.math.indiana.edu tables — 4_1, 5_2, 6_1, K11n34.
"""
import snappy


def _load_manifold(knot):
    """Accept a knot name, PD code, SnapPy Manifold, or SnapPy Link."""
    if isinstance(knot, snappy.Manifold):
        return knot
    if isinstance(knot, snappy.Link):
        return knot.exterior()
    if isinstance(knot, str):
        if not knot.strip():
            raise ValueError("hyperbolic_volume: empty knot identifier")
        return snappy.Manifold(knot)
    if isinstance(knot, list):
        if not knot:
            raise ValueError("hyperbolic_volume: empty PD code")
        return snappy.Link(knot).exterior()
    raise TypeError(f"Unsupported knot input: {type(knot).__name__}")


def hyperbolic_volume(knot) -> float:
    """Compute the hyperbolic volume of the knot/link complement.

    Parameters
    ----------
    knot : str | list | snappy.Manifold | snappy.Link
        Knot name ('4_1', 'K11n34'), PD code (list of 4-tuples),
        or an existing SnapPy object.

    Returns
    -------
    float
        Volume in hyperbolic 3-space. Returns 0.0 for non-hyperbolic knots
        (torus knots, connect sums, etc). Use `is_hyperbolic` to distinguish
        a true zero from a numerically tiny volume.
    """
    M = _load_manifold(knot)
    return float(M.volume())


def hyperbolic_volume_hp(knot, digits: int = 60) -> str:
    """Return the volume as a high-precision decimal string.

    SnapPy's high_precision engine uses arbitrary precision arithmetic
    (via snap). Useful for precision arithmetic / relation-finding (PSLQ).
    """
    M = _load_manifold(knot)
    v = M.high_precision().volume()
    s = str(v)
    # Truncate to requested digits (decimal places)
    if '.' in s:
        intpart, frac = s.split('.')
        frac = frac[:digits]
        return f"{intpart}.{frac}"
    return s


def is_hyperbolic(knot, tol: float = 1e-6) -> bool:
    """Test whether the knot complement admits a complete hyperbolic structure.

    Returns False for torus knots (volume exactly 0), connect sums, and
    satellite knots without hyperbolic JSJ pieces.
    """
    M = _load_manifold(knot)
    return float(M.volume()) > tol


def volume_conjecture_ratio(knot, N: int = 100) -> float:
    """Return (2*pi/N) * log|J_N(K; exp(2*pi*i/N))| / vol(K).

    The Kashaev-Murakami volume conjecture asserts this ratio -> 1 as N -> inf.
    Requires SnapPy's `colored_jones` method; may be unavailable for high-crossing
    knots. Returns None if the colored Jones evaluation fails.

    NOTE: This is a diagnostic helper, not a proof — convergence is slow.
    """
    import cmath
    import math
    M = _load_manifold(knot)
    v = float(M.volume())
    if v < 1e-9:
        return None
    link = getattr(M, 'link', lambda: None)()
    if link is None:
        return None
    try:
        cj = link.colored_jones_polynomial(N)
    except Exception:
        return None
    q = cmath.exp(2j * math.pi / N)
    val = complex(cj.subs(q=q))
    if val == 0:
        return None
    return float((2 * math.pi / N) * math.log(abs(val)) / v)


if __name__ == "__main__":
    cases = [
        ('4_1',     2.0298832128),  # figure-eight
        ('5_2',     2.8281220883),
        ('6_1',     3.1639632194),
        ('K11n34',  11.2191177244),  # Kinoshita-Terasaka (first mutant pair)
    ]
    print("hyperbolic_volume smoke test")
    print("-" * 54)
    for name, expected in cases:
        v = hyperbolic_volume(name)
        ok = abs(v - expected) < 1e-6
        print(f"  {name:10s}  computed={v:.10f}  expected={expected:.10f}  {'OK' if ok else 'FAIL'}")

    print(f"\n  3_1 (trefoil, non-hyperbolic): vol={hyperbolic_volume('3_1')}, "
          f"is_hyperbolic={is_hyperbolic('3_1')}")

    # PD code path
    fig8_pd = [[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]]
    print(f"  4_1 via PD code:  vol={hyperbolic_volume(fig8_pd):.10f}")

    # High precision
    print(f"\n  4_1 (60 digits):  {hyperbolic_volume_hp('4_1', digits=60)}")
