"""Cut: pyportfolioopt-1.5.5 (Martin's PyPortfolioOpt; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 24 of the 2026-09-17
NOT_CUT order). Read: efficient_frontier.py min_volatility / _max_return / max_sharpe 186-294; base_optimizer.py _solve_cvxpy_opt_problem
280-318 and the function list; risk_models.py ledoit_wolf 438-470 and the function list; expected_returns.py function list. NOT read:
black_litterman.py, cla.py (the critical line algorithm), hierarchical_portfolio.py, objective_functions.py, discrete_allocation.py,
efficient_semivariance/cvar/cdar. Nothing ran (cvxpy is not installed on M3; the body imports it at module load).
"""
from nyx.atlas.author import Cut

EF = "vault:pyportfolioopt-1.5.5/upstream/tree/pyportfolioopt-1.5.5/pypfopt/efficient_frontier/efficient_frontier.py"
BO = "vault:pyportfolioopt-1.5.5/upstream/tree/pyportfolioopt-1.5.5/pypfopt/base_optimizer.py"
RM = "vault:pyportfolioopt-1.5.5/upstream/tree/pyportfolioopt-1.5.5/pypfopt/risk_models.py"
ER = "vault:pyportfolioopt-1.5.5/upstream/tree/pyportfolioopt-1.5.5/pypfopt/expected_returns.py"
c = Cut("pyportfolioopt-1.5.5", mode="ANCESTRY_AWARE", inspected=["efficient_frontier.py 186-294", "base_optimizer.py 280-318 + function list", "risk_models.py 438-470 + function list", "expected_returns.py function list"],
        evidence=[("SOURCE_READ", EF + ":186-294"), ("SOURCE_READ", BO + ":280-318"), ("SOURCE_READ", RM + ":438-470"), ("SOURCE_READ", ER + ":29-200")],
        note="mean-variance portfolio construction as a thin layer over a convex solver: the mechanisms are the problem transformations (the Sharpe-ratio substitution), the covariance shrinkage estimators, and a guard that refuses to reuse a solved problem with changed objectives")

qp = c.organ("portfolio_objectives_as_convex_programs_handed_to_cvxpy_with_a_status_gate", human_name="BaseConvexOptimizer._solve_cvxpy_opt_problem; min_volatility; efficient_risk/return; add_objective/add_constraint", status="ACCEPTED",
    mechanism="weights are a cvxpy Variable; an objective (portfolio variance, negative return, quadratic utility) plus user constraints (sum to one, bounds, sector limits) form a Problem solved by whatever solver cvxpy picks; the result is accepted only if the status is optimal or optimal_inaccurate, else an OptimizationError; weights are rounded to 16 places and signed zeros removed",
    input="expected returns, covariance, bounds, constraints", output="a weight vector", state="the cvxpy Problem object (kept for warm reuse)", update="per solve",
    assumptions=["the objective is convex in the weights (variance is, return is linear); the solver's own status word is trusted (a Techne lesson: 'optimal_inaccurate' is accepted here)"],
    fitness_value_in_ancestor="any convex objective/constraint in a few lines; the solver does the numerics", failure_landscape="by reading: optimal_inaccurate is accepted as success -- the base role's own SCS finding (status anti-correlated with accuracy) applies here directly",
    evidence_ref=BO + ":280-318; " + EF + ":186-224", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the solve helper and the objective methods that call it",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "uncertainty": "POINT"})

sharpe = c.organ("maximum_sharpe_by_the_cornuejols_tutuncu_variable_substitution", human_name="EfficientFrontier.max_sharpe (186-294)", status="ACCEPTED",
    mechanism="the Sharpe ratio (return minus risk-free over volatility) is not convex; substitute w = y/k with k > 0: minimise y' Sigma y subject to (mu - rf)' y = 1 and sum(y) = k, and every existing linear constraint rewritten with its constant side multiplied by k; solve; recover w = y/k; the code warns that added non-linear objectives do not transform",
    input="expected returns, covariance, risk-free rate", output="the tangency portfolio", state="none", update="per solve", assumptions=["at least one asset beats the risk-free rate (checked); constraints are linear (inequalities and equalities are rewritten; anything else raises)"],
    fitness_value_in_ancestor="a quadratic program instead of a non-convex ratio maximisation", failure_landscape="by reading: the constraint rewriting inspects cvxpy's internal argument order (which side is the Constant) -- brittle across cvxpy versions",
    human_prior="Cornuejols & Tutuncu 2006, cited in the docstring", evidence_ref=EF + ":225-294", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="max_sharpe",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

shrink = c.organ("covariance_shrinkage_toward_a_structured_target_with_an_estimated_intensity", human_name="CovarianceShrinkage.ledoit_wolf (constant_variance / single_factor / constant_correlation), shrunk_covariance, oracle_approximating (risk_models.py 356-600)", status="ACCEPTED",
    mechanism="the sample covariance is blended with a target (a scaled identity, a one-factor market model, or a constant-correlation matrix) as (1-delta) S + delta F; delta is either fixed (shrunk_covariance) or estimated from the data by the Ledoit-Wolf formula (sklearn's for constant variance; the library's own for the other two targets) or the oracle-approximating estimator; the result is annualised by the frequency",
    input="a returns matrix", output="a positive-definite covariance estimate", state="none", update="per call", assumptions=["the sample covariance's extreme eigenvalues are estimation noise; pulling toward a low-dimensional target trades bias for variance"],
    fitness_value_in_ancestor="the optimiser is notoriously an error maximiser on the raw sample covariance; shrinkage is the standard cure", failure_landscape="UNKNOWN by run", human_prior="Ledoit & Wolf 2003/2004; the three targets are the paper's",
    evidence_ref=RM + ":356-600", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="class CovarianceShrinkage",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "uncertainty": "POINT"})

psd = c.organ("positive_semidefinite_repair_by_spectral_or_diagonal_fix", human_name="risk_models._is_positive_semidefinite / fix_nonpositive_semidefinite (32-100)", status="ACCEPTED",
    mechanism="check PSD by attempting a Cholesky factorisation (plus a tiny ridge); if it fails, either clip negative eigenvalues to zero and reconstruct (spectral) or add the most negative eigenvalue times identity (diagonal); warn the user; every risk model passes through this before the optimiser",
    input="a symmetric matrix", output="a PSD matrix", state="none", update="per risk-model call", assumptions=["a non-PSD sample matrix is numerical, not structural, so a small repair is honest"],
    fitness_value_in_ancestor="the convex solver requires PSD; without this the solver refuses with an obscure error", failure_landscape="UNKNOWN by run", evidence_ref=RM + ":32-100", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two functions",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

c.reject("expected_returns.py (mean/EMA/CAPM return models), risk_models sample/semi/exp covariances, cov<->corr helpers", reason="BELOW_MEANINGFUL_GRAIN", evidence=ER + "; " + RM + ":101-355", note="estimators that are one formula each; the shrinkage organ is where a mechanism lives")
c.reject("black_litterman.py, cla.py, hierarchical_portfolio.py (HRP), discrete_allocation.py, the semivariance/CVaR/CDaR frontiers, plotting", reason="OTHER", evidence="NOT READ; residue", note="cla.py (Markowitz's critical line algorithm) and HRP (Lopez de Prado) are the two mechanism-bearing modules left unread")
c.reject("'portfolio optimisation' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the estimator (shrinkage), the transformation (Sharpe substitution), the repair (PSD) and the solver call are separable")

c.edge(shrink, psd, "feeds"); c.edge(psd, qp, "feeds"); c.edge(sharpe, qp, "feeds", note="a rewritten problem"); c.edge(qp, sharpe, "feeds", note="y and k back")

c.pressure("an_allocation_over_correlated_assets_must_be_chosen_from_a_noisy_covariance_estimate_without_the_optimiser_amplifying_the_estimation_error",
    condition="N assets, T observations with T not much larger than N; the organism chooses weights to trade expected return against variance; the covariance it sees is a noisy estimate; the score is out-of-sample variance",
    resource_or_constraint="T samples; a convex solve", failure_condition="weights concentrated on the assets whose covariance is most under-estimated (the error-maximisation property)", world_punishes="using the raw sample covariance", world_rewards="shrinkage toward structure; constraints that bound concentration",
    observable_consequence="out-of-sample variance of the minimum-variance portfolio with sample vs shrunk covariance as N/T grows toward 1", vacuity_condition="T >> N (the sample covariance is fine) or uncorrelated assets", trivial_shortcuts="equal weights (the 1/N benchmark, which the literature shows is hard to beat -- a world must include it as a control)",
    cheat_control="an organism given the true covariance must achieve the minimum out-of-sample variance; the raw-sample organism at N/T near 1 must show the blow-up; equal weights must sit between: the world must show all three",
    cost_class="CPU-scale", source_evidence="risk_models.py shrinkage; efficient_frontier.py min_volatility; DeMiguel et al. 2009 (the 1/N result) as the control's rationale", purpose="PURPOSE: mean-variance portfolio construction (Markowitz 1952 as a library)")

c.ancestry("algorithm_from", "Markowitz 1952 (mean-variance); Ledoit & Wolf 2003/2004 (shrinkage); Cornuejols & Tutuncu 2006 (the Sharpe transform)", note="from the docstrings")
c.residue("PARTIALLY_EXPLAINED", ["cla.py and HRP unread", "the body needs cvxpy, absent on M3: NOT an M3-native world candidate as it stands (contradicts my #358 list, which named it from the record; corrected here)", "nothing ran"], note="the optimiser layer's four mechanisms are located")
c.save(state="COARSE")
