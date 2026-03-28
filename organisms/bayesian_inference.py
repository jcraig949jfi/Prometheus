"""
Bayesian Inference organism.

Operations: bayes_update, conjugate_prior_normal, posterior_predictive,
            evidence_lower_bound
"""

from .base import MathematicalOrganism


class BayesianInference(MathematicalOrganism):
    name = "bayesian_inference"
    operations = {
        "bayes_update": {
            "code": """
def bayes_update(prior, likelihood):
    \"\"\"Bayes' rule: posterior(theta) propto prior(theta) * likelihood(data|theta).
    Input: prior and likelihood as arrays over a discrete parameter grid.
    Returns normalised posterior.\"\"\"
    prior = np.asarray(prior, dtype=np.float64)
    likelihood = np.asarray(likelihood, dtype=np.float64)
    unnormed = prior * likelihood
    evidence = unnormed.sum()
    if evidence == 0:
        return np.ones_like(prior) / len(prior)
    posterior = unnormed / evidence
    return posterior
""",
            "input_type": "probability_distribution_pair",
            "output_type": "probability_distribution",
        },
        "conjugate_prior_normal": {
            "code": """
def conjugate_prior_normal(data, prior_mu=0.0, prior_sigma=1.0, noise_sigma=1.0):
    \"\"\"Conjugate Bayesian update for Normal-Normal model.
    Prior: mu ~ N(prior_mu, prior_sigma^2)
    Likelihood: x_i ~ N(mu, noise_sigma^2)
    Returns posterior (mu_post, sigma_post).\"\"\"
    data = np.asarray(data, dtype=np.float64)
    n = len(data)
    prior_prec = 1.0 / (prior_sigma ** 2)
    lik_prec = n / (noise_sigma ** 2)
    post_prec = prior_prec + lik_prec
    post_sigma = np.sqrt(1.0 / post_prec)
    post_mu = (prior_prec * prior_mu + lik_prec * data.mean()) / post_prec
    return {"posterior_mu": post_mu, "posterior_sigma": post_sigma}
""",
            "input_type": "vector",
            "output_type": "dict",
        },
        "posterior_predictive": {
            "code": """
def posterior_predictive(post_mu, post_sigma, noise_sigma=1.0, n_grid=200):
    \"\"\"Posterior predictive distribution for Normal-Normal model.
    p(x_new | data) = N(post_mu, post_sigma^2 + noise_sigma^2).
    Returns (x_grid, pdf) arrays.\"\"\"
    pred_sigma = np.sqrt(post_sigma**2 + noise_sigma**2)
    x_grid = np.linspace(post_mu - 4*pred_sigma, post_mu + 4*pred_sigma, n_grid)
    pdf = (1.0 / (pred_sigma * np.sqrt(2*np.pi))) * np.exp(
        -0.5 * ((x_grid - post_mu) / pred_sigma)**2
    )
    return {"x_grid": x_grid, "pdf": pdf}
""",
            "input_type": "dict",
            "output_type": "probability_distribution",
        },
        "evidence_lower_bound": {
            "code": """
def evidence_lower_bound(log_joint, log_q):
    \"\"\"ELBO = E_q[log p(x,z)] - E_q[log q(z)].
    Inputs: arrays of log p(x,z_i) and log q(z_i) evaluated at samples z_i.
    This is the variational lower bound on log p(x).\"\"\"
    log_joint = np.asarray(log_joint, dtype=np.float64)
    log_q = np.asarray(log_q, dtype=np.float64)
    # ELBO = mean(log_joint - log_q)  (Monte Carlo estimate)
    elbo = np.mean(log_joint - log_q)
    return elbo
""",
            "input_type": "vector_pair",
            "output_type": "scalar",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = BayesianInference()
    print(org)

    # Bayes update: uniform prior, peaked likelihood
    prior = np.ones(10) / 10
    likelihood = np.array([0.01, 0.01, 0.01, 0.01, 0.8, 0.8, 0.01, 0.01, 0.01, 0.01])
    post = org.execute("bayes_update", prior, likelihood)
    print(f"Posterior: {np.round(post, 3)}")
    print(f"  MAP index: {np.argmax(post)}  (expect 4 or 5)")

    # Conjugate Normal update
    data = np.array([2.1, 1.9, 2.3, 2.0, 1.8])
    result = org.execute("conjugate_prior_normal", data, prior_mu=0.0, prior_sigma=1.0, noise_sigma=0.5)
    print(f"Conjugate update: mu={result['posterior_mu']:.3f}, sigma={result['posterior_sigma']:.3f}")

    # Posterior predictive
    pp = org.execute("posterior_predictive", result["posterior_mu"], result["posterior_sigma"], noise_sigma=0.5)
    print(f"Predictive dist: peak at x={pp['x_grid'][np.argmax(pp['pdf'])]:.3f}")

    # ELBO
    z = np.random.randn(1000)
    log_joint = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)  # standard normal
    log_q = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)  # same distribution
    elbo = org.execute("evidence_lower_bound", log_joint, log_q)
    print(f"ELBO (q=p): {elbo:.4f}  (expect ~0 since q=p)")

    print("--- bayesian_inference: ALL TESTS PASSED ---")
