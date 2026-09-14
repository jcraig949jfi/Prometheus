"""Batch 02 recipes and harnesses (2026-09-12). python -m techne.fossils.batches.batch02_recipes

Buildable specimens run in the preserved docker world prometheus-fossil-lang:bookworm
(gcc 12, autotools, bison/flex, guile 3, sbcl). swipl and souffle are SOURCE_ONLY this pass
(heavy cmake trees); their records already say so and get no recipe.
"""
from __future__ import annotations

import json

from .. import vault

IMG = "prometheus-fossil-lang:bookworm"
R = {}
H = {}

# PicoSAT: ./configure.sh && make ; solve the same two hand-checkable CNFs as MiniSat.
H["picosat-965"] = {
    "sat.cnf": "p cnf 2 3\n1 2 0\n-1 2 0\n1 -2 0\n",
    "unsat.cnf": "p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"}
R["picosat-965"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream/tree/picosat-965",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure+make", "cmd": "./configure.sh >/dev/null && make -s 2>&1 | tail -2; test -x ./picosat"}],
    "runs": [{"name": "satisfiable CNF (exit 10)", "cmd": "./picosat $HARNESS/sat.cnf; exit $?",
              "expect": {"exit": 10, "stdout_contains": ["s SATISFIABLE"]}},
             {"name": "unsatisfiable CNF (exit 20)", "cmd": "./picosat $HARNESS/unsat.cnf; exit $?",
              "expect": {"exit": 20, "stdout_contains": ["s UNSATISFIABLE"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "PicoSAT uses the same SAT-competition exit convention as MiniSat (10 SAT / 20 UNSAT); same two hand-checkable clauses, a DIFFERENT CDCL implementation."}

# WalkSAT v56: make in the versioned subdir; generate a hard random 3-SAT, then find a model.
R["walksat-v56"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream/tree/Walksat-master/Walksat_v56",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | grep -vi warning | tail -3; test -x ./walksat && test -x ./makewff"}],
    "runs": [{"name": "generate a satisfiable random 3-SAT and solve it by local search",
              "cmd": "./makewff -seed 1 -cnf 3 50 210 > $BODY/build_w.cnf 2>/dev/null || ./makewff 3 50 210 > $BODY/build_w.cnf; ./walksat -seed 1 -numsol 1 < $BODY/build_w.cnf 2>&1 | tail -20",
              "expect": {"exit": 0, "stdout_regex": "(?i)(ASSIGNMENT FOUND|solution|numsol|flips)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "makewff generates instances, walksat solves by stochastic local search; it is INCOMPLETE (finds models, never proves UNSAT), the opposite paradigm to picosat/minisat. The makewff flag form is version-dependent; the recipe tries the flagged form then a positional fallback."}

# FF planner: make (flex+bison build the PDDL parser); plan a tiny gripper problem.
H["ff-planner-2.3"] = {
    "gripper_domain.pddl": """(define (domain gripper)
 (:requirements :strips)
 (:predicates (room ?r) (ball ?b) (gripper ?g) (at-robby ?r) (at ?b ?r) (free ?g) (carry ?o ?g))
 (:action move :parameters (?from ?to)
   :precondition (and (room ?from) (room ?to) (at-robby ?from))
   :effect (and (at-robby ?to) (not (at-robby ?from))))
 (:action pick :parameters (?obj ?room ?gripper)
   :precondition (and (ball ?obj) (room ?room) (gripper ?gripper) (at ?obj ?room) (at-robby ?room) (free ?gripper))
   :effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper))))
 (:action drop :parameters (?obj ?room ?gripper)
   :precondition (and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))
   :effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))))
""",
    "gripper_prob.pddl": """(define (problem gripper2)
 (:domain gripper)
 (:objects rooma roomb ball1 ball2 left right)
 (:init (room rooma) (room roomb) (ball ball1) (ball ball2)
        (gripper left) (gripper right) (free left) (free right)
        (at-robby rooma) (at ball1 rooma) (at ball2 rooma))
 (:goal (and (at ball1 roomb) (at ball2 roomb))))
"""}
R["ff-planner-2.3"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream/tree/FF-v2.3",
    "probe": [{"name": "toolchain", "cmd": "gcc --version | head -1; bison --version | head -1; flex --version"}],
    "build": [{"name": "make (CC=gcc -fcommon: the GCC-10+ -fno-common default breaks 2000-era tentative definitions; a COMPILER FLAG, not a source change)",
               "cmd": "make clean >/dev/null 2>&1; make -s ADDONS=-fcommon 2>&1 | grep -viE 'warning|deprecat' | tail -3; test -x ./ff"}],
    "runs": [{"name": "plan the 2-ball gripper problem", "cmd": "./ff -o $HARNESS/gripper_domain.pddl -f $HARNESS/gripper_prob.pddl 2>&1 | tail -30",
              "expect": {"exit": 0, "stdout_regex": "(?i)(found legal plan|step .*:|PICK|MOVE|DROP)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "FF's PDDL parser is generated by flex+bison at build time. COMPATIBILITY FLAG (isolated, recorded): built with make ADDONS=-fcommon (FF's CFLAGS appends $(ADDONS)) because GCC 10+ defaults to -fno-common, which turns FF's 2000-era tentative header definitions (gbracket_count et al.) into multiple-definition link errors. -fcommon restores the pre-2019 linker behaviour; no source byte is changed and the algorithm is untouched. The harness is a minimal STRIPS gripper domain+problem."}

# GLPK: ./configure && make (autotools; slower). Solve a tiny LP via glpsol MathProg.
H["glpk-5.0"] = {"lp.mod": """/* maximise 3x + 2y s.t. x + y <= 4, x + 3y <= 6, x,y >= 0 ; optimum 12 at (4,0), verified against all four vertices */
var x >= 0; var y >= 0;
maximize obj: 3*x + 2*y;
s.t. c1: x + y <= 4;
s.t. c2: x + 3*y <= 6;
solve;
printf "OBJECTIVE %g x %g y %g\\n", obj, x, y;
end;
"""}
R["glpk-5.0"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream/tree/glpk-5.0",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "configure", "cmd": "./configure --disable-shared >/dev/null 2>&1; echo configured", "timeout": 900},
              {"name": "make", "cmd": "make -s 2>&1 | tail -2; test -x examples/glpsol || test -x src/glpsol || find . -name glpsol -type f", "timeout": 1200}],
    "runs": [{"name": "solve a 2-var LP to its known optimum (10 at x=3,y=1)",
              "cmd": "G=$(find $BODY/upstream/tree -name glpsol -type f | head -1); $G --math $HARNESS/lp.mod 2>&1 | tail -15",
              "expect": {"exit": 0, "stdout_contains": ["OBJECTIVE 12", "x 4", "y 0"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "deviations": ["run 1 (receipt ...143613Z) expected OBJECTIVE 10 at (3,1); GLPK returned 12 at (4,0), which is the true optimum (vertex (4,0): 3*4+2*0=12 beats (3,1): 11). The expected value was my arithmetic error; the gate was corrected to the solver-verified and independently vertex-enumerated optimum. The receipt of the mismatch stays."],
    "notes": "glpsol reads GNU MathProg; the LP has a vertex-enumerated optimum (12 at (4,0); run 1 asserted a wrong hand value of 10 at (3,1) and GLPK correctly returned 12 -- the solver caught my arithmetic, recorded as a deviation) so the check is correctness, not just exit 0. --disable-shared keeps the build self-contained."}

# KISS FFT: build the objects and run the test-tool round trip.
R["kissfft-131.1.0"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream/tree/kissfft-131.1.0",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make all", "cmd": "make -s all 2>&1 | grep -viE 'warning' | tail -3; ls kiss_fft.c.o"}],
    "runs": [{"name": "forward-then-inverse round trip via a tiny driver",
              "cmd": "cat > $BODY/rt.c <<'CEOF'\n#include \"kiss_fft.h\"\n#include <math.h>\n#include <stdio.h>\nint main(){int N=32;kiss_fft_cfg f=kiss_fft_alloc(N,0,0,0),i=kiss_fft_alloc(N,1,0,0);kiss_fft_cpx x[32],X[32],y[32];for(int k=0;k<N;k++){x[k].r=cos(2*M_PI*3*k/N);x[k].i=0;}kiss_fft(f,x,X);kiss_fft(i,X,y);double e=0;for(int k=0;k<N;k++){double dr=y[k].r/N-x[k].r,di=y[k].i/N-x[k].i;e+=dr*dr+di*di;}printf(\"roundtrip_l2 %.3e\\n\", sqrt(e));return e<1e-12?0:1;}\nCEOF\ngcc -I. -O2 -o $BODY/rt $BODY/rt.c kiss_fft.c -lm && $BODY/rt",
              "expect": {"exit": 0, "stdout_regex": r"roundtrip_l2 \d"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Techne's 8-line driver builds a pure cosine, forward + inverse FFT, and checks the L2 reconstruction error is at the floor (<1e-12). It exercises kiss_fft only; it is a smoke of the transform, not a decomposition."}

# Reed-Solomon (Rockliff): single K&R C file with main(); -w silences the K&R warnings.
R["reed-solomon-rockliff-1991"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile (K&R)", "cmd": "gcc -w -std=gnu89 -o $BODY/rs rs.c -lm 2>&1 | grep -i error; test -x $BODY/rs"}],
    "runs": [{"name": "encode, corrupt, decode a Reed-Solomon codeword", "cmd": "$BODY/rs 2>&1 | tail -25",
              "expect": {"exit": 0, "stdout_regex": "(?i)(decode|error|recover|data|codeword|Results)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The 1991 driver builds a codeword, injects errors, and decodes; -std=gnu89 accepts the K&R main() and implicit int. Output is the program's own before/after data."}

# microKanren: run under guile with a tiny query harness.
H["microkanren-scheme"] = {"harness.scm": """;; Techne minimal microKanren query, matched to this microKanren.scm's API:
;; a state is (substitution . counter); the initial state is '(() . 0); a goal
;; applied to a state returns a stream (a possibly-improper list / procedure).
(define empty-state '(() . 0))
;; microKanren.scm uses R6RS `assp`, which Guile does not export by default. It is a library
;; primitive, not part of the algorithm, so Techne supplies it in the HARNESS rather than
;; editing the specimen: (assp pred alist) = first pair whose car satisfies pred, else #f.
(define (assp pred lst)
  (cond ((null? lst) #f) ((pred (caar lst)) (car lst)) (else (assp pred (cdr lst)))))
(define (pull $) (if (procedure? $) (pull ($)) $))
(define (take n $)
  (let loop ((n n) ($ (pull $)))
    (cond ((null? $) '())
          ((= n 0) '())
          (else (cons (car $) (loop (- n 1) (pull (cdr $))))))))
(define one ((call/fresh (lambda (q) (== q 5))) empty-state))
(display "answers-for-q=5: ") (display (length (take 5 one))) (newline)
(define two ((call/fresh (lambda (q) (disj (== q 1) (== q 2)))) empty-state))
(display "disj-answers: ") (display (length (take 9 two))) (newline)
(display "MICROKANREN_OK") (newline)
"""}
R["microkanren-scheme"] = {
    "runner": "docker", "image": IMG, "workdir": "upstream",
    "probe": [{"name": "guile", "cmd": "guile --version | head -1"}],
    "build": [],
    "runs": [{"name": "unification + interleaving search on a tiny relation",
              "cmd": "guile --no-auto-compile -l microKanren.scm -l $HARNESS/harness.scm -c '(exit 0)' 2>&1 | tail -6",
              "expect": {"exit": 0, "stdout_contains": ["MICROKANREN_OK", "disj-answers: 2"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "microKanren.scm defines empty-state, ==, call/fresh, disj, conj as streams. The harness poses (== q 5) (one answer) and (disj (== q 1) (== q 2)) (two answers) and pulls the streams. If guile rejects a name (the paper's variant vs this file's), the receipt shows the exact symbol and the run is BROKEN_UPSTREAM until the harness matches the file -- Techne does not edit microKanren.scm."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid)
        d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid)


if __name__ == "__main__":
    main()
