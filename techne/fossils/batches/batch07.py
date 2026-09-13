"""Batch 07 of the fossil harvest (2026-09-13): BREADTH + DEPTH BY COVERAGE -- records.

Chosen from techne/fossils/COVERAGE_MAP_2026-09-13.json: theorem proving, symbolic algebra /
number theory, and bioinformatics sequence alignment were ABSENT domains; this round enters them,
entering bioinformatics via SSW (the scalar global/local DP pair is a later add). Depth in existing areas
(estimation failed-branch, compression decompression-corruption) is added as pressure runs on the
fossils already held (batch07_pressure). Every disposition label is the human record's, cited.
"""
from __future__ import annotations

from .. import record

S = []


def spec(sid, **kw):
    S.append(record.skeleton(sid, **kw))


# ============================ NEW DOMAIN: theorem proving =====================================
spec("eprover-2.6",
    canonical_name="E 2.6 -- a superposition-based theorem prover for first-order logic with equality (Stephan Schulz)",
    aliases=["E prover", "eprover"],
    lineage="Automated theorem proving by SATURATION: the resolution lineage (Robinson 1965) as refined into superposition/paramodulation with term orderings and a given-clause loop -- Otter (McCune 1988) -> E (Schulz 1998-) and Vampire, the engines that win CASC. Distinct execution model from every solver in the vault: it searches a space of DERIVED CLAUSES for the empty clause, proving a conjecture by refuting its negation. First theorem-proving fossil.",
    domain=["theorem-proving", "automated-reasoning", "first-order-logic", "saturation", "search", "symbolic"],
    era="1965 (resolution); 1998- (E); 2.6 = 2022",
    version="github.com/eprover/eprover master as of 2026-09-13 (commit in hashes; 3.x line)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/eprover/eprover", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/eprover/eprover (Schulz)"},
    license={"spdx": "GPL-2.0-or-later", "status": "copyleft", "evidence": "COPYING in the tree"},
    language=["C"], build_system="./configure && make", compiler_or_interpreter="E built from source (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler; the tree bundles its build"],
    entry_points=["eprover --auto --tptp3-format problem.p ; 'Proof found!' / 'No proof found!'"],
    example={"command": "eprover --auto --tptp3-format group.p", "input": "a group-theory conjecture in TPTP (a group where x*x=e for all x is abelian)", "output": "'# Proof found!' + SZS status Theorem (the ORACLE)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Schulz, E - A Brainiac Theorem Prover, AI Communications 2002", "Robinson, A Machine-Oriented Logic Based on the Resolution Principle, JACM 1965"],
    human_capability_summary={"built_to": "decide whether a first-order conjecture follows from axioms, by systematically deriving consequences until it finds a contradiction with the negated goal",
                              "pressure": "the search space of derivable clauses is unbounded; term orderings, literal selection and the given-clause loop keep it tractable on real problems",
                              "success_means": "a conjecture that is a theorem is proved (empty clause derived); a checkable proof object is emitted"},
    known_human_problem_solved="automated first-order theorem proving",
    human_environmental_pressure="unbounded search; combinatorial explosion of derived clauses",
    human_failure_condition="the prover runs forever or exhausts memory on a true theorem it cannot order well (incompleteness of the strategy, not of the calculus)",
    behavioral_entry_point="give it a harder algebra problem (e.g. a ring identity) and watch generated/processed clause counts and time; vary --auto vs a fixed strategy",
    acquisition_tags=["batch07", "new_domain", "theorem_proving", "search", "symbolic", "outside_queue"],
    lineage_relations=[{"relation": "algorithm_from", "to": "Robinson 1965 (resolution); Bachmair-Ganzinger (superposition)", "note": ""},
                       {"relation": "shares_ancestor_with", "to": "cocagne-plain-paxos", "note": "both search, but for a proof vs for agreement -- different problems (Techne records the domain, not equivalence)"}])

# ============================ NEW DOMAIN: symbolic algebra / number theory ====================
spec("pari-gp-2.17",
    canonical_name="PARI/GP 2.17.4 -- a computer algebra system specialised for number theory (Henri Cohen et al., Bordeaux)",
    aliases=["PARI", "gp", "pari-gp"],
    lineage="PARI/GP (1985-): a CAS built for fast number theory -- arbitrary-precision integers/reals, factoring, elliptic curves, number fields, modular forms, L-functions -- with its own stack-based interpreter (gp). A distinct symbolic/exact execution model (a computation stack, exact arithmetic, mathematical objects as first-class values) absent from the vault. First computer-algebra fossil.",
    domain=["symbolic", "computer-algebra", "number-theory", "exact-arithmetic", "scientific-computing"],
    era="1985- (PARI); 2.15 = 2022",
    version="PARI/GP 2.17.4 (pari.math.u-bordeaux.fr source)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://pari.math.u-bordeaux.fr/pub/pari/unix/pari-2.17.4.tar.gz", "filename": "pari-2.17.4.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"archive": "pari.math.u-bordeaux.fr/pub/pari/unix", "file": "pari-2.17.4.tar.gz"},
    license={"spdx": "GPL-2.0-or-later", "status": "copyleft", "evidence": "COPYING in the tree"},
    language=["C", "GP (the PARI scripting language)"], build_system="./Configure && make gp", compiler_or_interpreter="gp 2.17 built from source (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler; readline/gmp optional (bundled fallback)"],
    entry_points=["gp -q < script.gp ; factor(), ellinit()+ellap(), qfbclassno(), nextprime()"],
    example={"command": "gp -q < nt.gp", "input": "factor a Mersenne number, count points on an elliptic curve mod p, a class number", "output": "the exact factorisation 2^67-1 = 193707721 * 761838257287, etc. (the ORACLE: known number-theoretic values)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Cohen, A Course in Computational Algebraic Number Theory, Springer 1993", "PARI/GP user's manual"],
    human_capability_summary={"built_to": "compute exact number-theoretic quantities fast -- factorisations, curve orders, class numbers, L-values -- on a purpose-built stack machine",
                              "pressure": "exact arithmetic on huge integers; algorithms whose cost is number-theoretic (factoring is hard); a finite computation stack",
                              "success_means": "the exact mathematical value is returned; known values (LMFDB, tables) match"},
    known_human_problem_solved="computational number theory",
    human_environmental_pressure="exact arithmetic at scale; the hardness of factoring/discrete log; bounded stack memory",
    human_failure_condition="stack overflow on a too-large object, or an intractable factorisation that never returns",
    behavioral_entry_point="factor progressively larger semiprimes and watch the time climb; grow a computation past the default parisize stack",
    acquisition_tags=["batch07", "new_domain", "symbolic", "computer_algebra", "number_theory", "outside_queue"],
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "reed-solomon-rockliff-1991", "note": "finite-field / GF arithmetic underlies both (Techne records the shared machinery domain, not equivalence)"}])

# ============================ NEW DOMAIN: bioinformatics (SIMD Smith-Waterman) =================
spec("ssw-smith-waterman",
    canonical_name="SSW -- a SIMD (SSE2) striped Smith-Waterman implementation in C (Zhao, Lee, Bustamante 2013)",
    aliases=["SSW", "striped Smith-Waterman", "ssw_test"],
    lineage="The Smith-Waterman 1981 recurrence re-expressed for vector hardware: Farrar's striped SIMD layout (2007) as the SSW library (2013), tens of times faster than the scalar DP by computing the score matrix in SSE2 lanes. The architecture-and-era DEPTH partner of EMBOSS's `water`: same algorithm, 32 years and one hardware model apart.",
    domain=["bioinformatics", "sequence-alignment", "SIMD", "biological-computation"],
    era="1981 (SW); 2007 (Farrar striped); SSW 2013",
    version="github.com/mengyao/Complete-Striped-Smith-Waterman-Library master as of 2026-09-13 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library", "commit": "HEAD"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/mengyao/Complete-Striped-Smith-Waterman-Library"},
    license={"spdx": "MIT", "status": "permissive", "evidence": "README/LICENSE"},
    language=["C", "C++"], build_system="make (src/)", compiler_or_interpreter="gcc 12 (docker prometheus-fossil-c:bookworm)",
    dependencies=["a C compiler with SSE2 (x86-64)"],
    entry_points=["src/ssw_test -- align reads against a reference FASTA; the aligned score + CIGAR"],
    example={"command": "make; ./src/ssw_test ref.fa query.fa", "input": "the same conserved-core pair used for EMBOSS water", "output": "the optimal local-alignment score + CIGAR -- the same optimum EMBOSS water reports (the ORACLE: agreement with the 1981 scalar DP)"},
    environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm"},
    upstream_docs=["Zhao, Lee, Bustamante et al., SSW Library: An SIMD Smith-Waterman C/C++ Library, PLoS ONE 2013", "Farrar, Striped Smith-Waterman speeds database searches, Bioinformatics 2007"],
    human_capability_summary={"built_to": "compute the exact Smith-Waterman local-alignment score on vector hardware, an order of magnitude faster than the scalar recurrence",
                              "pressure": "aligning millions of short reads to a genome; the O(mn) DP is too slow scalar; SIMD lanes and striping recover the throughput",
                              "success_means": "the SIMD score equals the exact SW optimum, computed far faster"},
    known_human_problem_solved="fast optimal local alignment at read-mapping scale",
    human_environmental_pressure="throughput: millions of alignments; the quadratic scalar cost",
    human_failure_condition="a saturating 8/16-bit score overflow silently returning a wrong optimum (the known SIMD hazard the library guards with an overflow-and-recompute path)",
    behavioral_entry_point="align a pair with a very high score to probe the 8-bit->16-bit fallback; compare the score with EMBOSS water on the same pair",
    acquisition_tags=["batch07", "new_domain", "bioinformatics", "SIMD", "outside_queue"],
    lineage_relations=[{"relation": "algorithm_from", "to": "Smith-Waterman 1981; Farrar 2007 (striped SIMD)", "note": "first bioinformatics fossil; the global/local DP pair (EMBOSS needle/water or seq-align) is a later add -- its build needs submodules/heavy autotools, deferred honestly"}])


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date",
                      "observability", "nyx_handoff"):
                if old.get(k):
                    rec[k] = old[k]
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-34s %s" % (rec["specimen_id"], "ok" if not probs else probs))
    print(len(S), "records")


if __name__ == "__main__":
    main()
