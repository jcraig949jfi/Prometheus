"""
Aporia — Integrate open problems from arXiv survey papers.
Sources:
  - Comparative Prime Number Theory Problem List (arXiv:2407.03530) — 23 problems
  - UP24 (arXiv:2504.04845) — 18 problems in potential theory/discrete geometry
"""

import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load_jsonl(path):
    qs = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line: qs.append(json.loads(line))
    return qs

def normalize(t):
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t)

def next_id(existing, code):
    max_num = 0
    for q in existing:
        m = re.match(rf"{code}-(\d+)", q["id"])
        if m: max_num = max(max_num, int(m.group(1)))
    return max_num

def q(qid, domain, subdomain, title, statement, **kw):
    return {
        "id": qid, "title": title, "domain": domain,
        "subdomain": subdomain, "statement": statement,
        "status": kw.get("status", "open"),
        "importance": kw.get("importance", ""),
        "year_posed": kw.get("year_posed", None),
        "posed_by": kw.get("posed_by", ""),
        "sources": kw.get("sources", []),
        "tags": kw.get("tags", []),
        "related_ids": [], "papers": [], "notes": kw.get("notes", ""),
    }

def add_to_domain(domain, code, new_entries):
    path = ROOT / domain / "questions.jsonl"
    existing = load_jsonl(path)
    titles = {normalize(e["title"]) for e in existing}
    counter = next_id(existing, code)

    added = 0
    for sub, title, stmt, kw in new_entries:
        if normalize(title) in titles:
            continue
        counter += 1
        existing.append(q(f"{code}-{counter:04d}", domain, sub, title, stmt, **kw))
        titles.add(normalize(title))
        added += 1

    with open(path, "w", encoding="utf-8") as f:
        for e in existing:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"  {domain}: +{added} -> {len(existing)} total")

def main():
    CPNT = "https://arxiv.org/abs/2407.03530"
    UP24 = "https://arxiv.org/abs/2504.04845"

    # ── Comparative Prime Number Theory ──────────────────────────────
    add_to_domain("mathematics", "MATH", [
        ("analytic_number_theory", "CPNT 1: Irrationality of zeta zero ordinates", "Prove that the Riemann zeta function has at least one zero with irrational imaginary part.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 2: Irrationality of first zeta zero", "Show that gamma_1 ≈ 14.135 (the first nontrivial zero's ordinate) is irrational.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 3: Zeta derivative at zeros", "Obtain upper bounds for 1/|zeta'(rho)| as rho ranges over nontrivial zeros.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 4: Discrete moments of zeta derivative", "Compute upper bounds for sum of 1/|zeta'(rho)|^{2k} assuming SZ and GUE.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 6: Zero multiplicity bounds", "Improve unconditional upper bounds for multiplicities of nontrivial zeta zeros.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 7: First sign change of prime races", "Obtain upper bounds for the first sign change of pi(x;q,a) - pi(x;q,b) in terms of q.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 8: Mertens' theorem for number fields", "Localize the first negative value of Delta_K(x) for specific number fields.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 10: Linear independence in function fields", "Show that failure of linear independence of L-function zeros always has geometric explanation.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 11: Primes from quadratic forms", "Compare prime-counting functions for distinct quadratic forms with identical discriminants.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 13: Prime race ties have density zero", "Prove unconditionally that ties in prime races have logarithmic density 0.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 15: Explicit Mertens sum bounds", "Find explicit version of M(x) << x exp(-C(log x)^{3/5}(log log x)^{-1/5}).", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
        ("analytic_number_theory", "CPNT 17: Sign changes of psi(x)-x", "Improve lower bounds for sign changes of the prime-counting error term.", {"sources": [CPNT], "tags": ["cpnt"], "year_posed": 2024}),
    ])

    # ── UP24: Potential Theory and Discrete Geometry ─────────────────
    add_to_domain("mathematics", "MATH", [
        ("potential_theory", "UP24 1: Equilibrium support on spheres", "Characterize equilibrium measures for Riesz energy with s in (d-3, d) on d-spheres.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("potential_theory", "UP24 2: Dimension reduction of equilibrium measures", "When is the support of the equilibrium measure on a manifold full-dimensional vs lower-dimensional?", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("frame_theory", "UP24 10: P-frame energy minimizers", "For p > 2 and p not an even integer, are all p-frame energy minimizers discrete measures?", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("discrete_geometry", "UP24 12: Phase transitions on the torus", "Determine phase transition points between different maximizers on the flat torus.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("numerical_analysis", "UP24 14: Integration weights for random points", "Quantify point quality via positivity of integration weights for random point processes.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("approximation_theory", "UP24 15: Snake polynomial expansion", "Find classes of majorants whose associated snake polynomials have non-negative Chebyshev expansion.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("discrete_geometry", "UP24 17: Chromatic numbers of sphere configurations", "Find kissing configurations that improve upper bounds for chromatic number of spheres.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
        ("matrix_theory", "UP24 18: Explicit approximately Hadamard matrices", "Find explicit constructions of approximately Hadamard matrices with small condition ratio.", {"sources": [UP24], "tags": ["up24"], "year_posed": 2024}),
    ])


if __name__ == "__main__":
    main()
