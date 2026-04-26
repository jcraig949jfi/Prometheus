"""prometheus_math.elliptic_curves — elliptic curves over Q.

The full BSD audit chain plus structural invariants.
"""

from techne.lib.regulator import regulator, mordell_weil, height
from techne.lib.conductor import conductor, global_reduction, bad_primes
from techne.lib.root_number import (
    root_number,
    local_root_number,
    parity_consistent,
)
from techne.lib.analytic_sha import analytic_sha, sha_an_rounded
from techne.lib.selmer_rank import selmer_2_rank, selmer_2_data
from techne.lib.faltings_height import faltings_height, faltings_data


_PADIC_L_SURVEY_PATH = "techne/whitepapers/padic_l_survey.md"
_PADIC_L_PHASE2_MESSAGE = (
    "padic_l_function is a Phase-1 stub. The literature survey covering "
    "Pollack, Stevens, Greenberg, and Pollack-Stevens algorithms is "
    "available at techne/whitepapers/padic_l_survey.md. Phase-2 (ordinary "
    "EC at good primes via Pollack-Stevens overconvergent symbols) is the "
    "next implementation milestone for project #38; expected completion "
    "in a 7-day sprint following Phase 1. Phase 3 will add the "
    "supersingular case via Pollack plus/minus splitting (5 days). "
    "Phase 4 will cross-check against LMFDB ec_padic (4 days)."
)


def padic_l_function(ainvs, p, T_precision=10, M_precision=20, prec="auto"):
    """p-adic L-function L_p(E, T) of an elliptic curve E over Q at prime p.

    **STATUS: Phase-1 stub.** The full algorithm design is documented in
    ``techne/whitepapers/padic_l_survey.md`` (project #38, phase 1). This
    callable enforces input validation but raises NotImplementedError
    pending the Phase-2 implementation.

    The Phase-2 implementation will compute L_p(E, T) modulo T^{T_precision}
    to p-adic precision p^{M_precision} via the Pollack-Stevens
    overconvergent modular-symbol algorithm (ordinary case). Phase 3 adds
    the Pollack plus/minus splitting for supersingular reduction. Phase 4
    cross-checks against the LMFDB ``ec_padic`` table.

    Parameters
    ----------
    ainvs : list[int]
        Weierstrass invariants ``[a1, a2, a3, a4, a6]`` defining E over Q.
    p : int
        A rational prime of good reduction for E.
    T_precision : int, default 10
        Truncation order in the Iwasawa variable T (returned series is
        modulo ``T^{T_precision}``).
    M_precision : int, default 20
        Target p-adic precision of each coefficient (in units of p-adic
        digits).
    prec : str, default 'auto'
        One of ``'ordinary'``, ``'supersingular'``, ``'auto'``. ``'auto'``
        dispatches based on ``a_p(E) mod p``.

    Returns
    -------
    dict
        See ``techne/whitepapers/padic_l_survey.md`` Appendix B for the
        return-shape contract.

    Raises
    ------
    ValueError
        If ``ainvs`` is not a length-5 list of integers, or ``p`` is not a
        prime >= 2, or ``T_precision`` is negative.
    NotImplementedError
        Always (in Phase 1). The exception message points to the survey
        whitepaper at ``techne/whitepapers/padic_l_survey.md``.

    See Also
    --------
    techne/whitepapers/padic_l_survey.md : full algorithm design.
    """
    # --- Input validation: these run BEFORE the NotImplementedError so
    # that callers can rely on the stub to surface bad arguments early.
    if not isinstance(ainvs, (list, tuple)) or len(ainvs) != 5:
        raise ValueError(
            f"ainvs must be a length-5 list of integers [a1,a2,a3,a4,a6]; "
            f"got {ainvs!r}"
        )
    if not all(isinstance(a, int) for a in ainvs):
        raise ValueError(
            f"ainvs entries must be integers; got {ainvs!r}"
        )
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a rational prime >= 2; got {p!r}")
    # Trial-division primality check (fast for reasonable p).
    if p > 2 and (p % 2 == 0 or any(p % q == 0 for q in range(3, int(p**0.5) + 1, 2))):
        raise ValueError(f"p = {p} is not prime")
    if not isinstance(T_precision, int) or T_precision < 0:
        raise ValueError(
            f"T_precision must be a non-negative integer; got {T_precision!r}"
        )
    if not isinstance(M_precision, int) or M_precision < 1:
        raise ValueError(
            f"M_precision must be a positive integer; got {M_precision!r}"
        )
    if prec not in ("ordinary", "supersingular", "auto"):
        raise ValueError(
            f"prec must be one of 'ordinary', 'supersingular', 'auto'; "
            f"got {prec!r}"
        )

    raise NotImplementedError(_PADIC_L_PHASE2_MESSAGE)


__all__ = [
    "regulator", "mordell_weil", "height",
    "conductor", "global_reduction", "bad_primes",
    "root_number", "local_root_number", "parity_consistent",
    "analytic_sha", "sha_an_rounded",
    "selmer_2_rank", "selmer_2_data",
    "faltings_height", "faltings_data",
    "padic_l_function",
]
