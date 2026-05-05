"""Hand-crafted candidate library for Tink 2 — AST-based (Tier B).

Candidates are tuples (E_A_ast, E_B_ast). Each AST is a tagged-tuple
expression over the synthetic-BSD atoms.

For each candidate the runner derives:
  - n_tokens (via ast_utils.token_count)
  - atoms_used (via ast_utils.atoms_used)
  - SymPy form (via ast_utils.to_sympy) for CAS Layer C
  - executable evaluation (via ast_utils.evaluate)
  - trace evaluation (via ast_utils.evaluate_with_trace) for η_trace

Candidate classes:

  F043_family       — rearrangements of BSD identity; basis_projection ≈ 1
  mixed             — one side in basis, one off-basis
  off_basis         — both sides off-basis
  stress_cas        — cases where CAS Layer C should differ from Layer B
"""

from __future__ import annotations


def _atom(name): return ("atom", name)
def _const(v): return ("const", v)
def _add(a, b): return ("op", "add", a, b)
def _sub(a, b): return ("op", "sub", a, b)
def _scalar_mul(k, a): return ("op", "scalar_mul", k, a)
def _pow(a, k): return ("op", "pow", a, k)
def _exp(a): return ("op", "exp", a)
def _log(a): return ("op", "log", a)


# ---------- candidate library ---------------------------------------------

CANDIDATES = [
    # ----- F043 family -----------------------------------------------------
    {
        "name": "F043_literal",
        "description": "corr(log Sha, log Ω + log ∏c_p)",
        "class": "F043_family",
        "E_A": _atom("log_sha"),
        "E_B": _add(_atom("log_omega"), _atom("log_prod_cp")),
    },
    {
        "name": "F043_solve_L",
        "description": "corr(log L, log Ω + log ∏c_p + log Sha)",
        "class": "F043_family",
        "E_A": _atom("log_L"),
        "E_B": _add(_add(_atom("log_omega"), _atom("log_prod_cp")), _atom("log_sha")),
    },
    {
        "name": "F043_three_term",
        "description": "corr(log Sha, log L − log Ω)",
        "class": "F043_family",
        "E_A": _atom("log_sha"),
        "E_B": _sub(_atom("log_L"), _atom("log_omega")),
    },
    {
        "name": "F043_full_BSD",
        "description": "corr(log Ω + log ∏c_p + log Sha − 2 log Tor, log L)",
        "class": "F043_family",
        "E_A": _sub(
            _add(_add(_atom("log_omega"), _atom("log_prod_cp")), _atom("log_sha")),
            _scalar_mul(2.0, _atom("log_tor")),
        ),
        "E_B": _atom("log_L"),
    },
    {
        "name": "F043_solved_for_Sha",
        "description": "corr(log Sha + 2 log Tor, log L − log Ω − log ∏c_p)",
        "class": "F043_family",
        "E_A": _add(_atom("log_sha"), _scalar_mul(2.0, _atom("log_tor"))),
        "E_B": _sub(_sub(_atom("log_L"), _atom("log_omega")), _atom("log_prod_cp")),
    },

    # ----- mixed (one side in basis, one off-basis) -----------------------
    {
        "name": "mixed_Sha_j",
        "description": "corr(log Sha, log j)",
        "class": "mixed",
        "E_A": _atom("log_sha"),
        "E_B": _atom("log_j"),
    },
    {
        "name": "mixed_L_disc",
        "description": "corr(log L, log Δ)",
        "class": "mixed",
        "E_A": _atom("log_L"),
        "E_B": _atom("log_disc"),
    },

    # ----- genuinely off-basis --------------------------------------------
    {
        "name": "offbasis_j_disc",
        "description": "corr(log j, log Δ)",
        "class": "off_basis",
        "E_A": _atom("log_j"),
        "E_B": _atom("log_disc"),
    },
    {
        "name": "offbasis_jsq_disc",
        "description": "corr((log j)^2, log Δ)",
        "class": "off_basis",
        "E_A": _pow(_atom("log_j"), 2),
        "E_B": _atom("log_disc"),
    },
    {
        "name": "offbasis_j_jPlusDisc",
        "description": "corr(log j, log j + log Δ)",
        "class": "off_basis",
        "E_A": _atom("log_j"),
        "E_B": _add(_atom("log_j"), _atom("log_disc")),
    },
    {
        "name": "mixed_bag",
        "description": "corr(log Ω + log j, log Δ + log Sha)",
        "class": "mixed",
        "E_A": _add(_atom("log_omega"), _atom("log_j")),
        "E_B": _add(_atom("log_disc"), _atom("log_sha")),
    },
    {
        "name": "offbasis_j_L",
        "description": "corr(log j, log L)",
        "class": "mixed",
        "E_A": _atom("log_j"),
        "E_B": _atom("log_L"),
    },

    # ----- stress-test candidates (Tier B addition) -----------------------
    # exp(log_X) ≡ |X| numerically. Layer B linear regression of |X|
    # against the log-basis gets R² < 1 because exp is nonlinear in
    # log_X. CAS Layer C with `linear_in_basis` only ALSO doesn't catch
    # this (exp(log_X) is not a polynomial in log_X). This is an honest
    # demonstration that BOTH layers have the same blind spot for
    # transcendental compositions. v3+ would need richer CAS rules
    # (e.g., a `bijective_invertible` substitution table).
    {
        "name": "stress_exp_logSha",
        "description": "corr(exp(log Sha), exp(log Ω))  [exp/log composition]",
        "class": "stress_cas",
        "E_A": _exp(_atom("log_sha")),
        "E_B": _exp(_atom("log_omega")),
    },
    # Linear combination that uses ONLY basis atoms but is dressed in
    # nested AST form that linear regression catches trivially. CAS
    # should also catch this via expand+poly. Both layers agree.
    {
        "name": "stress_nested_basis",
        "description": "corr(((log Sha + log Ω) − log Ω) + log ∏c_p, log L)",
        "class": "stress_cas",
        "E_A": _add(
            _sub(
                _add(_atom("log_sha"), _atom("log_omega")),
                _atom("log_omega"),
            ),
            _atom("log_prod_cp"),
        ),
        "E_B": _atom("log_L"),
    },
    # Polynomial in basis atoms (degree 2): for our cheap-path CAS
    # this still counts as "in basis" via `polynomial_in_basis_atoms`,
    # because all atoms used ARE basis atoms even though the form is
    # quadratic. Layer B linear regression would NOT catch this fully
    # (R² < 1 because of nonlinearity). The two layers disagree.
    {
        "name": "stress_quadratic_basis",
        "description": "corr((log Sha)^2, log Ω)",
        "class": "stress_cas",
        "E_A": _pow(_atom("log_sha"), 2),
        "E_B": _atom("log_omega"),
    },
]
