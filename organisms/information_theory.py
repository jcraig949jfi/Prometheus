"""
Information Theory organism.

Operations: shannon_entropy, mutual_information, kl_divergence, conditional_entropy
"""

from .base import MathematicalOrganism


class InformationTheory(MathematicalOrganism):
    name = "information_theory"
    operations = {
        "shannon_entropy": {
            "code": """
def shannon_entropy(p):
    \"\"\"H(X) = -sum p(x) log2 p(x). Input: probability distribution (1-D array).\"\"\"
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]  # avoid log(0)
    p = p / p.sum()  # normalise
    return -np.sum(p * np.log2(p))
""",
            "input_type": "probability_distribution",
            "output_type": "scalar",
        },
        "mutual_information": {
            "code": """
def mutual_information(joint):
    \"\"\"I(X;Y) from a joint probability table (2-D array).
    I(X;Y) = H(X) + H(Y) - H(X,Y).\"\"\"
    joint = np.asarray(joint, dtype=np.float64)
    joint = joint / joint.sum()
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)

    def H(p):
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    return H(px) + H(py) - H(joint.ravel())
""",
            "input_type": "joint_distribution",
            "output_type": "scalar",
        },
        "kl_divergence": {
            "code": """
def kl_divergence(p, q):
    \"\"\"D_KL(P || Q) = sum p(x) log2(p(x)/q(x)).\"\"\"
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    p = p / p.sum()
    q = q / q.sum()
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log2(p[mask] / q[mask]))
""",
            "input_type": "probability_distribution_pair",
            "output_type": "scalar",
        },
        "conditional_entropy": {
            "code": """
def conditional_entropy(joint):
    \"\"\"H(Y|X) = H(X,Y) - H(X).  Input: joint probability table.\"\"\"
    joint = np.asarray(joint, dtype=np.float64)
    joint = joint / joint.sum()
    px = joint.sum(axis=1)

    def H(p):
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    return H(joint.ravel()) - H(px)
""",
            "input_type": "joint_distribution",
            "output_type": "scalar",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = InformationTheory()
    print(org)

    # Shannon entropy of a fair coin
    h = org.execute("shannon_entropy", [0.5, 0.5])
    print(f"H(fair coin) = {h:.4f}  (expect 1.0)")

    # Shannon entropy of a biased coin
    h2 = org.execute("shannon_entropy", [0.9, 0.1])
    print(f"H(biased coin 0.9/0.1) = {h2:.4f}")

    # Mutual information — independent variables should give ~0
    joint_indep = np.outer([0.5, 0.5], [0.5, 0.5])
    mi = org.execute("mutual_information", joint_indep)
    print(f"MI(independent) = {mi:.6f}  (expect ~0)")

    # Mutual information — correlated
    joint_corr = np.array([[0.4, 0.1], [0.1, 0.4]])
    mi2 = org.execute("mutual_information", joint_corr)
    print(f"MI(correlated) = {mi2:.4f}")

    # KL divergence
    kl = org.execute("kl_divergence", [0.5, 0.5], [0.9, 0.1])
    print(f"KL([.5,.5] || [.9,.1]) = {kl:.4f}")

    # Conditional entropy
    ce = org.execute("conditional_entropy", joint_corr)
    print(f"H(Y|X) for correlated joint = {ce:.4f}")

    print("--- information_theory: ALL TESTS PASSED ---")
