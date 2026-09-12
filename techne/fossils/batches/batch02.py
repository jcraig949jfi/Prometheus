"""Batch 02 of the computational fossil harvest (2026-09-12): records.

    python -m techne.fossils.batches.batch02

Lineages chosen to be UNLIKE batch 01: a second SAT lineage (PicoSAT) and a stochastic-local-
search SAT (WalkSAT) beside batch 01's CDCL MiniSat; a heuristic-search STRIPS planner (FF)
beside Graphplan's planning-graph; an LP/MIP simplex+interior ecosystem (GLPK); a Forth
(concatenative, stack) and a relational-logic microKanren (Scheme) beside batch 01's
TinyScheme; a Reed-Solomon coder (algebraic block code) beside batch 01's LDPC
(sparse-graph); a small FFT; a Datalog engine and a Prolog/WAM system (source-pinned; heavy
builds). Nothing chosen for fame; several are one file. Nyx chops.
"""
from __future__ import annotations

from .. import record

S = []

S.append(record.skeleton("picosat-965",
    canonical_name="PicoSAT 965 -- Armin Biere",
    aliases=["picosat"],
    lineage="PicoSAT (2007-, JKU Linz, Armin Biere): compact CDCL SAT solver with aggressive clause learning, phase saving and a trace/proof mode; a distinct CDCL lineage from MiniSat and the ancestor of PrecoSAT/Lingeling",
    domain=["sat", "logic", "search", "constraint-solving", "proof-trace"], era="2007 (965 rel. 2014)",
    version="965 from fmv.jku.at (the author's site)",
    source_origin={"artifacts": [{"kind": "url", "url": "http://fmv.jku.at/picosat/picosat-965.tar.gz", "filename": "picosat-965.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"site": "fmv.jku.at/picosat", "release": "965"},
    license={"spdx": "MIT", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C"], build_system="./configure.sh && make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./picosat <cnf>"],
    example={"command": "./picosat sat.cnf", "input": "DIMACS CNF", "output": "s SATISFIABLE + v model, or s UNSATISFIABLE"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Biere, PicoSAT Essentials, JSAT 2008", "fmv.jku.at/picosat"],
    human_capability_summary={"built_to": "decide propositional satisfiability and emit a model or an UNSAT proof trace, in a small self-contained solver",
                              "pressure": "the same industrial CNF pressure as MiniSat, plus a demand for checkable UNSAT proofs (the trace mode)",
                              "success_means": "correct SAT/UNSAT, models that satisfy the clauses, and a replayable resolution proof on UNSAT"},
    known_human_problem_solved="propositional satisfiability with proof tracing"))

S.append(record.skeleton("walksat-v56",
    canonical_name="WalkSAT -- Kautz and Selman (stochastic local search for SAT)",
    aliases=["walksat", "WalkSAT", "GSAT/WalkSAT"],
    lineage="GSAT (1992) -> WalkSAT (1994, Selman, Kautz, Cohen): STOCHASTIC LOCAL SEARCH for SAT -- flip the variable that minimises broken clauses, with a random-walk escape; an incomplete solver that finds models fast but never proves UNSAT. The opposite paradigm to CDCL (MiniSat/PicoSAT).",
    domain=["sat", "stochastic-local-search", "search", "optimization"], era="1994 (this repo the maintained C source)",
    version="Kautz's Walksat repository default branch as of 2026-09-12 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "url", "url": "https://gitlab.com/HenryKautz/Walksat/-/archive/master/Walksat-master.tar.gz", "filename": "Walksat-master.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"repo": "gitlab.com/HenryKautz/Walksat"},
    license={"spdx": "custom academic (Kautz/Selman; see the source header)", "status": "read header before redistribution", "evidence": "source header"},
    language=["C"], build_system="make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./walksat < cnf", "./makewff (instance generator)"],
    example={"command": "./walksat -seed 1 < sat.cnf", "input": "DIMACS CNF on stdin", "output": "ASSIGNMENT FOUND / no solution found, with flip statistics"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Selman, Kautz, Cohen, Local Search Strategies for Satisfiability Testing, 1994", "gitlab.com/HenryKautz/Walksat"],
    human_capability_summary={"built_to": "find a satisfying assignment for a hard SAT instance quickly by hill-climbing on the count of unsatisfied clauses with random restarts and walks",
                              "pressure": "instances where systematic search is too slow but a model exists; the trade of completeness for speed",
                              "success_means": "an assignment satisfying all clauses within a flip budget; it cannot report UNSAT"},
    known_human_problem_solved="fast (incomplete) satisfiability by local search"))

S.append(record.skeleton("ff-planner-2.3",
    canonical_name="FF (Fast-Forward) planner v2.3 -- Joerg Hoffmann",
    aliases=["FF", "Fast-Forward", "Metric-FF ancestor"],
    lineage="FF (2000, Hoffmann & Nebel): forward heuristic-search STRIPS/ADL planner -- the relaxed-plan (ignore-delete-lists) heuristic guiding enforced hill-climbing, then best-first; won AIPS-2000 and reset classical planning after Graphplan",
    domain=["planning", "search", "heuristic-search", "strips", "symbolic-ai"], era="2000 (v2.3)",
    version="FF-v2.3 from the author's Saarland page",
    source_origin={"artifacts": [{"kind": "url", "url": "https://fai.cs.uni-saarland.de/hoffmann/ff/FF-v2.3.tgz", "filename": "FF-v2.3.tgz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"site": "fai.cs.uni-saarland.de/hoffmann/ff", "release": "v2.3"},
    license={"spdx": "GPL-2.0-or-later (FF's COPYRIGHT)", "status": "copyleft", "evidence": "source header"},
    language=["C", "flex", "bison"], build_system="make (needs flex + bison for the PDDL parser)", compiler_or_interpreter="gcc 12 + flex + bison (docker bookworm)",
    dependencies=["flex", "bison"], entry_points=["./ff -o <domain.pddl> -f <facts.pddl>"],
    example={"command": "./ff -o gripper_domain.pddl -f gripper_prob.pddl", "input": "PDDL domain + problem", "output": "a step-by-step plan and the relaxed-plan heuristic trace"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Hoffmann, Nebel, The FF Planning System, JAIR 14 (2001)", "fai.cs.uni-saarland.de/hoffmann/ff.html"],
    human_capability_summary={"built_to": "find a plan from initial state to goal in STRIPS/ADL by heuristic forward search, using the relaxed (delete-free) plan length as the guiding heuristic",
                              "pressure": "the huge branching of forward search; the relaxed-plan heuristic makes it tractable where blind or Graphplan-style search stalls",
                              "success_means": "a valid plan found fast on the AIPS/IPC benchmark domains (gripper, logistics, blocksworld)"},
    known_human_problem_solved="classical planning by relaxed-plan heuristic forward search"))

S.append(record.skeleton("glpk-5.0",
    canonical_name="GLPK 5.0 (GNU Linear Programming Kit) -- Andrew Makhorin",
    aliases=["glpk", "glpsol"],
    lineage="GLPK (2000-, Makhorin): revised primal/dual SIMPLEX and a primal-dual INTERIOR-POINT method for LP, plus branch-and-cut MIP and the GNU MathProg modelling language; a complete free LP/MIP solver ecosystem",
    domain=["optimization", "linear-programming", "integer-programming", "simplex", "interior-point", "branch-and-bound"], era="2000 (5.0 rel. 2020)",
    version="5.0 from ftp.gnu.org",
    source_origin={"artifacts": [{"kind": "url", "url": "https://ftp.gnu.org/gnu/glpk/glpk-5.0.tar.gz", "filename": "glpk-5.0.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"archive": "ftp.gnu.org/gnu/glpk", "release": "5.0"},
    license={"spdx": "GPL-3.0-or-later", "status": "copyleft", "evidence": "COPYING in tarball"},
    language=["C"], build_system="./configure && make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=[], entry_points=["./glpsol --lp <model> --output <sol>", "libglpk C API"],
    example={"command": "glpsol --math model.mod (a MathProg LP/MIP)", "input": "a MathProg or CPLEX-LP model", "output": "the optimal objective and variable values"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["GLPK Reference Manual", "gnu.org/software/glpk"],
    human_capability_summary={"built_to": "solve linear programs (simplex or interior-point) and mixed-integer programs (branch-and-cut) to proven optimality, from a modelling-language description",
                              "pressure": "large sparse LPs where the choice of pivot rule / interior path decides speed, and MIPs where branching and cutting decide tractability",
                              "success_means": "the certified optimal (or optimal-integer) solution, or a proof of infeasibility/unboundedness"},
    known_human_problem_solved="linear and mixed-integer optimisation to optimality"))

S.append(record.skeleton("kissfft-131.1.0",
    canonical_name="KISS FFT 131.1.0 -- Mark Borgerding",
    aliases=["kissfft", "kiss_fft"],
    lineage="KISS FFT (2003-, Borgerding): a mixed-radix Cooley-Tukey FFT small enough to read in one sitting; the 'keep it simple' counterpoint to FFTW's code generation",
    domain=["scientific-computing", "signal-processing", "fft", "numerical"], era="2003 (131.1.0 rel. 2021)",
    version="131.1.0 git tag, github.com/mborgerding/kissfft",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/mborgerding/kissfft/archive/refs/tags/131.1.0.tar.gz", "filename": "kissfft-131.1.0.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"repo": "github.com/mborgerding/kissfft", "tag": "131.1.0"},
    license={"spdx": "BSD-3-Clause", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C"], build_system="make", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=["libm"], entry_points=["kiss_fft() / kiss_fftr() C API; test/ programs"],
    example={"command": "make testall (builds and runs the fwd/inverse round-trip tests)", "input": "generated signals", "output": "round-trip error below tolerance"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["github.com/mborgerding/kissfft README", "Cooley & Tukey 1965"],
    human_capability_summary={"built_to": "compute the discrete Fourier transform (and inverse) for arbitrary sizes via mixed-radix Cooley-Tukey, in minimal readable C",
                              "pressure": "the O(N^2) cost of the naive DFT; the demand for a small dependency-free FFT where FFTW is overkill",
                              "success_means": "forward-then-inverse reconstructs the input within floating-point tolerance; agreement with a reference DFT"},
    known_human_problem_solved="the fast Fourier transform, minimally"))

S.append(record.skeleton("reed-solomon-rockliff-1991",
    canonical_name="Reed-Solomon encoder/decoder -- Simon Rockliff (1989/1991)",
    aliases=["rs.c", "Rockliff Reed-Solomon", "eccpage rs"],
    lineage="Rockliff RS (1989-1991, University of Adelaide): a textbook Reed-Solomon coder over GF(2^m) -- generate the field, build the generator polynomial, systematic encode, and Berlekamp-Massey + Forney erasure/error decode; the widely-copied reference on eccpage.com",
    domain=["error-correcting-codes", "coding-theory", "galois-field", "algebraic-codes"], era="1989-1991",
    version="eccpage.com/rs.c as served 2026-09-12 (single file, self-dated 26 June 1991)",
    source_origin={"artifacts": [{"kind": "url", "url": "http://www.eccpage.com/rs.c", "filename": "rs.c", "extract": False}]},
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    source_identity={"site": "eccpage.com", "author": "Simon Rockliff", "dated": "1989-09-21 / 1991-06-26 in the header"},
    license={"spdx": "public (Rockliff: 'This program may be freely modified and/or given to whoever wants it')", "status": "the header grants free use", "evidence": "rs.c header lines"},
    language=["C (K&R)"], build_system="cc rs.c", compiler_or_interpreter="gcc 12 (docker bookworm)",
    dependencies=["libm"], entry_points=["main() in rs.c: generate_gf, encode_rs, then inject errors and decode"],
    example={"command": "gcc -w -o rs rs.c -lm && ./rs", "input": "none (the driver builds a codeword, corrupts it, and decodes)", "output": "the recovered data, showing errors corrected"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["eccpage.com", "Reed & Solomon 1960; Berlekamp 1968; Massey 1969"],
    human_capability_summary={"built_to": "encode data with Reed-Solomon redundancy and recover it after a bounded number of symbol errors and erasures, over a Galois field",
                              "pressure": "burst errors on storage and transmission channels (CDs, DVB, deep space) where up to t symbol errors must be corrected exactly",
                              "success_means": "the decoded message equals the original whenever the error count is within the code's correction bound t"},
    known_human_problem_solved="algebraic block error correction (Reed-Solomon)"))

S.append(record.skeleton("microkanren-scheme",
    canonical_name="microKanren -- Hemann and Friedman (relational/logic programming kernel)",
    aliases=["microKanren", "uKanren"],
    lineage="microKanren (2013, Hemann & Friedman): a ~40-line relational programming kernel -- unification, fresh logic variables, interleaving (complete) search via streams; the minimal core underneath miniKanren and, by descent, a functional cousin of Prolog's resolution",
    domain=["logic-programming", "relational-programming", "unification", "search", "languages"], era="2013",
    version="jasonhemann/microKanren microKanren.scm as served 2026-09-12",
    source_origin={"artifacts": [{"kind": "url", "url": "https://raw.githubusercontent.com/jasonhemann/microKanren/master/microKanren.scm", "filename": "microKanren.scm", "extract": False}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"repo": "github.com/jasonhemann/microKanren", "file": "microKanren.scm"},
    license={"spdx": "MIT", "status": "permissive", "evidence": "the repository LICENSE (recorded separately if fetched)"},
    language=["Scheme"], build_system="none (interpreted by guile)", compiler_or_interpreter="GNU Guile 3.0 (docker bookworm)",
    dependencies=[], entry_points=["the relational operators ==, call/fresh, disj, conj; a Techne harness runs a tiny query"],
    example={"command": "guile -l microKanren.scm harness.scm", "input": "a relational query (Techne's minimal harness)", "output": "the stream of substitutions satisfying the relation"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Hemann & Friedman, microKanren: A Minimal Functional Core for Relational Programming, Scheme Workshop 2013"],
    human_capability_summary={"built_to": "run relations (not functions) -- pose a goal with logic variables and get the complete stream of variable bindings that make it hold, by unification and interleaving search",
                              "pressure": "the need for a tiny, auditable core capturing logic programming's essence without Prolog's machinery; completeness of search (no infinite left-branch starvation)",
                              "success_means": "every and only the correct substitutions are enumerated, fairly, for a relation"},
    known_human_problem_solved="relational logic programming in a minimal functional core"))

S.append(record.skeleton("swipl-9.2.9",
    canonical_name="SWI-Prolog 9.2.9 -- Jan Wielemaker",
    aliases=["swipl", "SWI-Prolog"],
    lineage="SWI-Prolog (1987-, Wielemaker): a full ISO Prolog with a WAM-style virtual machine, garbage collection, constraint (CLP) libraries, tabling and modules; the most widely used free Prolog and a living WAM lineage (Warren 1983)",
    domain=["logic-programming", "prolog", "wam", "unification", "resolution", "languages"], era="1987 (9.2.9 rel. 2024)",
    version="git tag V9.2.9, github.com/SWI-Prolog/swipl-devel",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/SWI-Prolog/swipl-devel/archive/refs/tags/V9.2.9.tar.gz", "filename": "swipl-9.2.9.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"repo": "github.com/SWI-Prolog/swipl-devel", "tag": "V9.2.9"},
    license={"spdx": "BSD-2-Clause (core; some components differ)", "status": "permissive core", "evidence": "LICENSE in tarball"},
    language=["C", "Prolog"], build_system="cmake (many submodules)", compiler_or_interpreter="gcc + cmake (heavy; NOT built this pass)",
    dependencies=["cmake", "libgmp", "libreadline", "many optional packages"], entry_points=["swipl (REPL); swipl -g goal -t halt script.pl"],
    example={"command": "swipl -g \"append(X,[c],[a,b,c]), write(X), nl\" -t halt", "input": "Prolog goals/clauses", "output": "unified bindings"},
    environment={"runner": "none this pass -- SOURCE pinned; build is a heavy cmake tree deferred to a later pass or on demand"},
    upstream_docs=["swi-prolog.org", "Warren, An Abstract Prolog Instruction Set, SRI 1983 (the WAM)"],
    human_capability_summary={"built_to": "execute logic programs -- resolution (SLD) over Horn clauses with unification and backtracking -- as a practical, full-featured programming system",
                              "pressure": "the WAM exists because naive resolution is too slow; GC, indexing and tabling exist because real Prolog programs exhaust memory and loop",
                              "success_means": "goals succeed with correct bindings, deterministically where possible, on real programs"},
    known_human_problem_solved="logic programming (Prolog / resolution) at production scale",
    versions_preserved=[{"note": "GNU Prolog and a bare WAM implementation queued as lighter, buildable WAM-lineage companions"}]))

S.append(record.skeleton("souffle-2.4.1",
    canonical_name="Souffle 2.4.1 -- a Datalog engine that compiles to C++",
    aliases=["souffle", "Soufflé"],
    lineage="Souffle (2016-, Oracle Labs / Sydney): a high-performance Datalog -- bottom-up semi-naive evaluation with a specialised data-structure back end, compiled to parallel C++; the modern engine behind large-scale static program analyses",
    domain=["databases", "datalog", "logic", "deductive-database", "static-analysis", "fixpoint"], era="2016 (2.4.1 rel. 2023)",
    version="git tag 2.4.1, github.com/souffle-lang/souffle",
    source_origin={"artifacts": [{"kind": "url", "url": "https://github.com/souffle-lang/souffle/archive/refs/tags/2.4.1.tar.gz", "filename": "souffle-2.4.1.tar.gz"}]},
    source_type="ORIGINAL_AUTHORITATIVE_RELEASE",
    source_identity={"repo": "github.com/souffle-lang/souffle", "tag": "2.4.1"},
    license={"spdx": "UPL-1.0 (Universal Permissive License)", "status": "permissive", "evidence": "LICENSE in tarball"},
    language=["C++", "yacc/flex"], build_system="cmake (needs bison, flex, libffi, mcpp; heavy)", compiler_or_interpreter="g++ + cmake (heavy; NOT built this pass)",
    dependencies=["cmake", "bison", "flex", "libffi", "mcpp", "sqlite3", "zlib"], entry_points=["souffle -c prog.dl (compile) / souffle prog.dl (interpret)"],
    example={"command": "souffle transitive_closure.dl -F facts -D out", "input": "a .dl Datalog program + fact directory", "output": "the computed relations as .csv"},
    environment={"runner": "none this pass -- SOURCE pinned; heavy cmake build deferred"},
    upstream_docs=["souffle-lang.github.io", "Jordan, Scholz, Subotic, Souffle: On Synthesis of Program Analyzers, CAV 2016"],
    human_capability_summary={"built_to": "evaluate Datalog -- compute the least fixpoint of a set of recursive Horn rules over relations -- fast enough for whole-program static analysis of millions of tuples",
                              "pressure": "the semi-naive fixpoint must not recompute derived tuples, and the join/index choices decide whether a real analysis finishes in seconds or hours",
                              "success_means": "the exact least model of the rules over the input facts, computed at C++ speed"},
    known_human_problem_solved="deductive (Datalog) fixpoint computation over relations"))


def main():
    from .. import record as R
    import json, pathlib
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date"):
                if old.get(k):
                    rec[k] = old[k]
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-30s %s" % (rec["specimen_id"], "ok" if not probs else probs))


if __name__ == "__main__":
    main()
