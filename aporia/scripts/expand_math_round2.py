"""
Aporia — Second math expansion: graph theory + more number theory + misc.
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

    WIKI = "https://en.wikipedia.org/wiki/"

    # ── Graph Theory (from Wikipedia category) ───────────────────────
    m("graph_theory", "Albertson conjecture", "If the chromatic number of a graph is at least r, it contains K_r as a minor with crossing number at most cr(K_r).", sources=[WIKI+"Albertson_conjecture"])
    m("graph_theory", "Babai's problem", "Is every group the automorphism group of some graph?", sources=[WIKI+"Babai%27s_problem"])
    m("graph_theory", "Barnette's conjecture", "Every 3-connected bipartite cubic planar graph is Hamiltonian.", sources=[WIKI+"Barnette%27s_conjecture"])
    m("spectral_graph_theory", "Brouwer's conjecture", "The sum of the k largest Laplacian eigenvalues is at most the number of edges plus k(k+1)/2.", sources=[WIKI+"Brouwer%27s_conjecture"])
    m("graph_theory", "Conway's 99-graph problem", "Does there exist a graph on 99 vertices that is strongly regular with parameters (99,14,1,2)?", sources=[WIKI+"Conway%27s_99-graph_problem"])
    m("graph_theory", "Cycle double cover conjecture", "Every bridgeless graph has a cycle double cover.", sources=[WIKI+"Cycle_double_cover"])
    m("graph_theory", "Earth-Moon problem", "What is the chromatic number of graphs embeddable on two spheres joined by tubes?", sources=[WIKI+"Earth%E2%80%93Moon_problem"])
    m("graph_theory", "GNRS conjecture", "Every minor-free graph embeds into L1 with constant distortion.", sources=[WIKI+"GNRS_conjecture"])
    m("graph_theory", "Grünbaum-Nash-Williams conjecture", "Every connected graph has a spanning tree with min(Delta, ceil((n-1)/3)) leaves.", sources=[WIKI+"Gr%C3%BCnbaum%E2%80%93Nash-Williams_conjecture"])
    m("graph_theory", "Gyárfás-Sumner conjecture", "For every tree T, the class of T-free graphs is chi-bounded.", sources=[WIKI+"Gy%C3%A1rf%C3%A1s%E2%80%93Sumner_conjecture"])
    m("graph_theory", "Hadwiger-Nelson problem", "What is the chromatic number of the plane (unit-distance graph on R^2)?", sources=[WIKI+"Hadwiger%E2%80%93Nelson_problem"], notes="Known to be 5,6, or 7")
    m("graph_theory", "Harborth's conjecture", "Every planar graph has a straight-line embedding with all edge lengths integers.", sources=[WIKI+"Harborth%27s_conjecture"])
    m("graph_theory", "Imbalance conjecture", "For every tournament on n vertices, the sum of vertex imbalances is at most n(n-1)(n-3)/4.", sources=[WIKI+"Imbalance_conjecture"])
    m("graph_theory", "Kotzig's conjecture", "There is no finite basis for well-covered graphs.", sources=[WIKI+"Kotzig%27s_conjecture"])
    m("graph_theory", "Lovász-Woodall conjecture", "The edge connectivity of a graph equals its edge toughness.", sources=[WIKI+"Lov%C3%A1sz%E2%80%93Woodall_conjecture"])
    m("graph_theory", "New digraph reconstruction conjecture", "Every directed graph on n >= 6 vertices is reconstructible from its vertex-deleted subdigraphs.", sources=[WIKI+"New_digraph_reconstruction_conjecture"])
    m("graph_theory", "Oberwolfach problem", "Is there a 2-factorization of K_n into copies of a given 2-factor for all odd n?", sources=[WIKI+"Oberwolfach_problem"])
    m("graph_theory", "Second neighborhood conjecture (Seymour)", "Every oriented graph has a vertex whose second neighborhood is at least as large as its first.", sources=[WIKI+"Second_neighborhood_problem"])
    m("graph_theory", "Sumner's conjecture", "Every tournament on 2n-2 vertices contains every oriented tree on n vertices.", sources=[WIKI+"Sumner%27s_conjecture"])
    m("graph_theory", "Szymanski's conjecture", "Every permutation of hypercube vertices can be routed along edge-disjoint paths.", sources=[WIKI+"Szymanski%27s_conjecture"])
    m("graph_theory", "Turán's brick factory problem", "The crossing number of K_{m,n} equals floor(m/2)*floor((m-1)/2)*floor(n/2)*floor((n-1)/2).", sources=[WIKI+"Tur%C3%A1n%27s_brick_factory_problem"])
    m("graph_theory", "Unfriendly partition conjecture", "Every countable graph has an unfriendly partition (each vertex has at least as many neighbors across as on its side).", sources=[WIKI+"Unfriendly_partition"])
    m("graph_theory", "Zarankiewicz problem", "Determine the maximum edges in a bipartite graph avoiding K_{s,t} as subgraph.", sources=[WIKI+"Zarankiewicz_problem"])

    # ── More number theory ───────────────────────────────────────────
    m("number_theory", "Suslin's problem", "Is every complete dense linear order without endpoints satisfying CCC isomorphic to the reals?", sources=[WIKI+"Suslin%27s_problem"])
    m("number_theory", "Kummer-Vandiver conjecture", "The p-part of class number of cyclotomic fields Q(zeta_p) is trivial for regular primes.", sources=[WIKI+"Kummer%E2%80%93Vandiver_conjecture"])
    m("analytic_number_theory", "Hardy-Littlewood first conjecture", "The prime k-tuples conjecture predicting when patterns of primes repeat infinitely.", sources=[WIKI+"First_Hardy%E2%80%93Littlewood_conjecture"])
    m("number_theory", "Lander-Parkin-Selfridge conjecture", "Counterexamples to Euler's sum of powers conjecture require at least as many terms on the right as the power.", sources=[WIKI+"Lander,_Parkin,_and_Selfridge_conjecture"])
    m("number_theory", "Giuga conjecture", "p is prime iff sum of k^{p-1} for k=1..p-1 is -1 mod p.", sources=[WIKI+"Giuga_number"])
    m("number_theory", "Brocard's problem", "The only solutions to n! + 1 = m^2 are n = 4, 5, 7.", sources=[WIKI+"Brocard%27s_problem"])
    m("number_theory", "Erdős-Kac theorem extensions", "Extend the Gaussian distribution of prime factors to other arithmetic functions.", sources=[WIKI+"Erd%C5%91s%E2%80%93Kac_theorem"])
    m("number_theory", "Wall-Sun-Sun prime conjecture", "Are there infinitely many Wall-Sun-Sun primes?", sources=[WIKI+"Wall%E2%80%93Sun%E2%80%93Sun_prime"])
    m("number_theory", "Wieferich prime conjecture", "Are there infinitely many Wieferich primes?", sources=[WIKI+"Wieferich_prime"])
    m("number_theory", "Mersenne prime conjecture", "Are there infinitely many Mersenne primes?", sources=[WIKI+"Mersenne_prime"])
    m("number_theory", "Sophie Germain prime conjecture", "Are there infinitely many Sophie Germain primes?", sources=[WIKI+"Sophie_Germain_prime"])
    m("number_theory", "Safe prime conjecture", "Are there infinitely many safe primes?", sources=[WIKI+"Safe_and_Sophie_Germain_primes"])

    # ── More algebra/topology ────────────────────────────────────────
    m("topology", "Andrews-Curtis conjecture (topology)", "Every balanced presentation of the trivial group can be reduced via Andrews-Curtis moves.", sources=[WIKI+"Andrews%E2%80%93Curtis_conjecture"])
    m("topology", "Zeeman conjecture", "If K is a contractible 2-complex, then K x I is collapsible.", sources=[WIKI+"Zeeman_conjecture"])
    m("algebra", "Dixmier conjecture", "Every endomorphism of the Weyl algebra A_n is an automorphism.", sources=[WIKI+"Dixmier_conjecture"])
    m("algebraic_geometry", "Fujita conjecture", "For ample line bundle L on n-dim variety, K + (n+1)L is basepoint-free and K + (n+2)L is very ample.", sources=[WIKI+"Fujita_conjecture"])

    # ── Logic/Foundations ────────────────────────────────────────────
    m("model_theory", "Vaught's conjecture", "A countable first-order theory has either countably many or continuum-many models.", sources=[WIKI+"Vaught%27s_conjecture"])
    m("computability", "Collatz conjecture undecidability", "Is the generalized Collatz problem algorithmically undecidable?", sources=[WIKI+"Collatz_conjecture"])

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
