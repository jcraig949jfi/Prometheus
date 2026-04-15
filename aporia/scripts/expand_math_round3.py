"""
Aporia — Third math expansion: MathWorld problems, openproblems.net additions,
and miscellaneous well-known problems not yet in catalog.
"""

import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATH_JSONL = ROOT / "mathematics" / "questions.jsonl"

def load_existing():
    existing = []
    if MATH_JSONL.exists():
        with open(MATH_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))
    return existing

def normalize(t):
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t)

def next_id(existing):
    max_num = 0
    for q in existing:
        m = re.match(r"MATH-(\d+)", q["id"])
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num

def q(counter, subdomain, title, statement, **kw):
    counter[0] += 1
    return {
        "id": f"MATH-{counter[0]:04d}",
        "title": title,
        "domain": "mathematics",
        "subdomain": subdomain,
        "statement": statement,
        "status": kw.get("status", "open"),
        "importance": kw.get("importance", ""),
        "year_posed": kw.get("year_posed", None),
        "posed_by": kw.get("posed_by", ""),
        "sources": kw.get("sources", []),
        "tags": kw.get("tags", []),
        "related_ids": [], "papers": [], "notes": kw.get("notes", ""),
    }

def new_questions(counter):
    qs = []
    def m(sub, title, stmt, **kw):
        qs.append(q(counter, sub, title, stmt, **kw))

    MW = "https://mathworld.wolfram.com/UnsolvedProblems.html"
    OPN = "https://www.openproblems.net/"

    # ── From MathWorld (not yet in catalog) ──────────────────────────
    m("number_theory", "196-algorithm (Lychrel numbers)", "Does the reverse-and-add process starting from 196 ever produce a palindrome?", sources=[MW])
    m("number_theory", "Solitary number problem", "Is 10 a solitary number (is there another integer with the same abundancy index)?", sources=[MW])
    m("number_theory", "Euler-Mascheroni constant irrationality", "Is the Euler-Mascheroni constant gamma irrational?", sources=[MW])
    m("number_theory", "Odd perfect numbers", "Do odd perfect numbers exist?", sources=[MW], notes="Ancient problem, no odd perfect number found")
    m("number_theory", "Cubic number representation", "Can every integer be written as a sum of three cubes?", sources=[MW], notes="Partially resolved for specific values")
    m("applied_mathematics", "Square site percolation threshold", "Determine the exact critical probability for site percolation on the square lattice.", sources=[MW])

    # ── Classic well-known problems not yet in catalog ───────────────
    m("number_theory", "Normality of pi", "Are the digits of pi uniformly distributed in every base?", sources=[OPN])
    m("number_theory", "Normality of e", "Is the base-10 expansion of e normal?", sources=[OPN])
    m("number_theory", "Normality of sqrt(2)", "Is the base-10 expansion of sqrt(2) normal?", sources=[OPN])
    m("number_theory", "e + pi irrationality", "Is e + pi irrational?", sources=[OPN])
    m("number_theory", "e * pi irrationality", "Is e * pi irrational?", sources=[OPN])
    m("number_theory", "Infinitely many perfect numbers", "Are there infinitely many perfect numbers?", sources=[OPN])
    m("number_theory", "Infinitely many Fermat primes", "Are there infinitely many Fermat primes (primes of the form 2^{2^n}+1)?", sources=[OPN])
    m("number_theory", "Infinitely many amicable pairs", "Are there infinitely many amicable number pairs?", sources=[OPN])
    m("number_theory", "Existence of odd weird numbers", "Does an odd weird number exist?", sources=[OPN])
    m("number_theory", "Catalan's conjecture generalization", "Characterize all perfect powers that differ by 1 (beyond Mihailescu's theorem for prime powers).", sources=[OPN])
    m("number_theory", "Benford's law for primes", "Do primes satisfy Benford's law in a suitable asymptotic sense?", sources=[OPN])

    # ── Mirror symmetry and mathematical physics from openproblems.net ──
    m("mathematical_physics", "Mirror symmetry", "Establish the mathematical equivalence between geometrically distinct Calabi-Yau manifolds.", sources=[OPN])
    m("mathematical_physics", "Quantum confinement and mass gap", "Quantitatively understand quark and gluon confinement in QCD.", sources=[OPN], notes="Related to Yang-Mills millennium problem")

    # ── Combinatorics/Ramsey not yet covered ─────────────────────────
    m("ramsey_theory", "Hales-Jewett theorem bounds", "Determine the exact Hales-Jewett numbers HJ(r,k).", sources=["https://en.wikipedia.org/wiki/Hales%E2%80%93Jewett_theorem"])
    m("ramsey_theory", "Graham's number context", "Determine the exact value of N* in the Ramsey-type problem on hypercube colorings.", sources=["https://en.wikipedia.org/wiki/Graham%27s_number"])
    m("combinatorics", "Frankl's conjecture (union-closed)", "In any finite union-closed family of sets, some element belongs to at least half the sets.", sources=["https://en.wikipedia.org/wiki/Union-closed_sets_conjecture"], notes="Also called union-closed sets conjecture")
    m("combinatorics", "Rota's conjecture (matroids)", "Finitely many excluded minors characterize representability over any finite field.", sources=["https://en.wikipedia.org/wiki/Rota%27s_conjecture"])
    m("combinatorics", "Welsh's conjecture", "The number of bases of a matroid is log-concave.", sources=["https://en.wikipedia.org/wiki/Log-concave_sequence"], status="solved", notes="Proved by Adiprasito-Huh-Katz 2018")

    # ── Analysis and PDE ─────────────────────────────────────────────
    m("analysis", "Carleson's theorem extensions", "Does the Fourier series of every L^p function converge almost everywhere for p > 1?", sources=["https://en.wikipedia.org/wiki/Carleson%27s_theorem"], notes="Proved for p>=2 by Carleson, p>1 by Hunt; open for endpoint")
    m("pde", "Regularity of 3D Euler equations", "Do smooth solutions to the incompressible 3D Euler equations develop singularities in finite time?", sources=["https://en.wikipedia.org/wiki/Euler_equations_(fluid_dynamics)"])
    m("functional_analysis", "Kadison-Singer problem", "Every pure state on B(l^2) is uniquely determined by its restriction to a maximal abelian subalgebra.", status="solved", notes="Solved by Marcus-Spielman-Srivastava 2013")

    # ── Knot theory ──────────────────────────────────────────────────
    m("knot_theory", "Unknotting number conjecture", "Is the unknotting number of a knot equal to its 4-genus?", sources=["https://en.wikipedia.org/wiki/Unknotting_number"])
    m("knot_theory", "Slice-ribbon conjecture", "Is every slice knot a ribbon knot?", sources=["https://en.wikipedia.org/wiki/Slice-ribbon_conjecture"])
    m("knot_theory", "Jones polynomial detects unknot", "Does the Jones polynomial distinguish the unknot from all other knots?", sources=["https://en.wikipedia.org/wiki/Jones_polynomial"])
    m("knot_theory", "Vassiliev conjecture", "Do Vassiliev invariants distinguish all knots?", sources=["https://en.wikipedia.org/wiki/Vassiliev_invariant"])
    m("knot_theory", "Volume conjecture", "The colored Jones polynomial determines the hyperbolic volume of the knot complement.", sources=["https://en.wikipedia.org/wiki/Volume_conjecture"])

    # ── Category theory / homotopy theory ────────────────────────────
    m("homotopy_theory", "Homotopy groups of spheres", "Determine the homotopy groups pi_n(S^k) for all n and k.", sources=["https://en.wikipedia.org/wiki/Homotopy_groups_of_spheres"])
    m("homotopy_theory", "Telescope conjecture", "Is the telescope conjecture true in chromatic homotopy theory?", sources=["https://en.wikipedia.org/wiki/Telescope_conjecture"], notes="Disproved for n>=2 by Burklund-Hahn-Levy-Schlank 2023", status="partially_solved")
    m("category_theory", "Homotopy hypothesis", "Are infinity-groupoids equivalent to topological spaces?", sources=["https://en.wikipedia.org/wiki/Homotopy_hypothesis"])

    # ── Operator algebras ────────────────────────────────────────────
    m("operator_algebra", "Kadison's similarity problem", "Is every bounded representation of a C*-algebra similar to a *-representation?", sources=["https://en.wikipedia.org/wiki/Similarity_problem"])
    m("operator_algebra", "Naimark's problem", "If a C*-algebra has only one irreducible representation up to unitary equivalence, is it isomorphic to K(H)?", sources=["https://en.wikipedia.org/wiki/Naimark%27s_problem"])

    # ── Logic ────────────────────────────────────────────────────────
    m("set_theory", "Large cardinal consistency", "Are there models of ZFC with specific large cardinals (measurable, supercompact, etc.)?", sources=["https://en.wikipedia.org/wiki/Large_cardinal"])
    m("set_theory", "Ultimate L", "Does Woodin's Ultimate L conjecture hold, resolving the structure of the set-theoretic universe?", sources=["https://en.wikipedia.org/wiki/Ultimate_L"])
    m("set_theory", "Proper forcing axiom consequences", "What are the complete consequences of PFA for the structure of the continuum?", sources=["https://en.wikipedia.org/wiki/Proper_forcing_axiom"])

    return qs


def main():
    existing = load_existing()
    existing_titles = {normalize(q["title"]) for q in existing}
    start_num = next_id(existing)
    counter = [start_num]

    new = new_questions(counter)

    added = []
    skipped = 0
    for nq in new:
        nt = normalize(nq["title"])
        if nt in existing_titles:
            skipped += 1
            continue
        existing_titles.add(nt)
        added.append(nq)

    all_questions = existing + added

    with open(MATH_JSONL, "w", encoding="utf-8") as f:
        for entry in all_questions:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"  Existing: {len(existing)}")
    print(f"  New candidates: {len(new)}")
    print(f"  Skipped (duplicate): {skipped}")
    print(f"  Added: {len(added)}")
    print(f"  Total: {len(all_questions)}")


if __name__ == "__main__":
    main()
