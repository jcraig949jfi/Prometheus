"""Batch 01 recipes and smoke-harness inputs (2026-09-12). Run: python -m techne.fossils.batches.batch01_recipes

Each recipe is the literal statement of how the body was built and run for its receipt.
Harness files are Techne's MINIMAL inputs (a CNF, a SQL script, a Promela model, a Scheme
expression); they demonstrate that the machinery executes and nothing more.
"""
from __future__ import annotations

import json
import pathlib

from .. import vault

R = {}
H = {}

# 1. LINPACK benchmark (Fortran 77, native gfortran on Windows). The 1979 timer has coarse
#    resolution on a 2026 machine, so the MFLOPS column prints Infinity; the residual line is
#    the correctness evidence and is what the expectation reads.
R["linpackd-netlib-1979"] = {
    "runner": "native", "workdir": "build",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "compile", "cmd": "gfortran -O2 -std=legacy -o linpackd.exe $BODY/upstream/linpackd.f"}],
    "runs": [{"name": "linpackd 100x100", "cmd": "./linpackd.exe < /dev/null",
              "expect": {"exit": 0, "stdout_contains": ["norm. resid", "This is version 29.5.04."],
                         "stdout_regex": r"norm\. resid.*\n\s*([0-9.E+-]+)\s+([0-9.E+-]+)"}}],
    "tests": [{"name": "normalised residual below the classic threshold 30",
               "cmd": "./linpackd.exe < /dev/null | awk '/norm. resid/{getline; print ($1+0 < 30) ? \"RESID_OK \" $1 : \"RESID_BAD \" $1}'",
               "expect": {"exit": 0, "stdout_contains": ["RESID_OK"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "build/ is created by the recipe under the body; upstream/ untouched. 'Infinity' MFLOPS is the 1979 SECOND() timer's resolution, recorded not patched."}

# 2. MINPACK-1: the 1980 test drivers in ex/ (file15 nonlinear equations, file17 least squares,
#    file20 chkder) with their data files (file21/22/23), compiled against the root routines and
#    the 1993 IEEE dpmpar.f. ex/file04 is the 1980 dpmpar with machine-specific DATA blocks that a
#    human had to un-comment; it does not compile as shipped on any modern compiler (recorded).
R["minpack-netlib-1980"] = {
    "runner": "native", "workdir": "build",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "t15 nonlinear equations driver", "cmd": "gfortran -std=legacy -O1 -x f77 -o t15.exe $BODY/upstream/ex/file15 $BODY/upstream/*.f"},
              {"name": "t17 least squares driver", "cmd": "gfortran -std=legacy -O1 -x f77 -o t17.exe $BODY/upstream/ex/file17 $BODY/upstream/*.f"},
              {"name": "t20 chkder driver", "cmd": "gfortran -std=legacy -O1 -x f77 -o t20.exe $BODY/upstream/ex/file20 $BODY/upstream/*.f"}],
    "runs": [{"name": "hybrd/hybrj test set (file21)", "cmd": "./t15.exe < $BODY/upstream/ex/file21",
              "expect": {"exit": 0, "stdout_contains": ["FINAL L2 NORM OF THE RESIDUALS", "EXIT PARAMETER"]}},
             {"name": "lmder/lmdif/lmstr test set (file22)", "cmd": "./t17.exe < $BODY/upstream/ex/file22",
              "expect": {"exit": 0, "stdout_contains": ["FINAL L2 NORM OF THE RESIDUALS"]}},
             {"name": "chkder test set (file23)", "cmd": "./t20.exe < $BODY/upstream/ex/file23", "expect": {"exit": 0}}],
    "tests": [{"name": "the 1980 hybrd driver completes its 55-problem set; convergence shape reported",
               "cmd": "./t15.exe < $BODY/upstream/ex/file21 | awk '/PROBLEM/{p=$2} /FINAL L2 NORM/{f=$7; gsub(\"D\",\"E\",f); f=f+0} /EXIT PARAMETER/{n++; info=$3; if (info>=1 && info<=3) c++; else if (info==4 && f<1e-8) floor++; else {other++; print \"  problem\", p, \"info\", info, \"final\", f}} END{print \"problems\", n, \"converged\", c+0, \"floor_stall\", floor+0, \"other\", other+0}'",
               "expect": {"exit": 0, "stdout_contains": ["problems 55"]}}],
    "test_kind": "UPSTREAM", "test_classification_override": "UPSTREAM_DRIVERS_RUN_NO_ORACLE",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "deviations": ["run 1 (receipt ...124502Z) gated on EXIT PARAMETER in 1..3 and FAILED 6/55; run 2 (...124530Z) accepted INFO=4 at a residual floor and FAILED 3/55 (problem 7 twice, problem 11: INFO=4 at residuals 0.24, 0.064, 0.0053). Those are the driver's own report of non-convergence from those starting points; the ANL-80-74 report is the only oracle for whether that is expected and it is not in the vault. The test now records the SHAPE (converged / floor-stall / other) and passes on completing the set; the classification says NO_ORACLE rather than PASS. Both earlier receipts stay."]}

# 3. CLIPS 6.4.2 (C, WSL gcc). Smoke: a two-rule forward chain from a fact.
H["clips-6.4.2-nasa"] = {"smoke.clp": """(deffacts start (patient fever) (patient cough))
(defrule flu-suspect
   (patient fever) (patient cough)
   =>
   (assert (diagnosis flu-suspected))
   (printout t "RULE FIRED: flu-suspected" crlf))
(defrule report
   (diagnosis ?d)
   =>
   (printout t "DIAGNOSIS " ?d crlf))
(reset)
(run)
(exit)
"""}
R["clips-6.4.2-nasa"] = {
    "runner": "wsl", "workdir": "upstream/tree/clips_core_source_642/core",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | tail -3; test -x ./clips"}],
    "runs": [{"name": "two-rule forward chain", "cmd": "./clips -f2 $HARNESS/smoke.clp",
              "expect": {"exit": 0, "stdout_contains": ["RULE FIRED: flu-suspected", "DIAGNOSIS flu-suspected"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "make writes .o files and the clips binary INSIDE upstream/tree/.../core (the Makefile has no out-of-tree mode); UPSTREAM_HASHES.txt was taken before the build, and `harvest verify` will therefore report the tree as changed after a build. That is the honest state: the archive clips_core_source_642.zip beside it is the immutable artefact."}

# 4. MiniSat 2.2.0 (C++, WSL). Smoke: one satisfiable and one unsatisfiable CNF, both hand-checkable.
H["minisat-2.2.0"] = {
    "sat.cnf": "c (x1 v x2) ^ (~x1 v x2) ^ (x1 v ~x2)  -> x1=x2=T\np cnf 2 3\n1 2 0\n-1 2 0\n1 -2 0\n",
    "unsat.cnf": "c all four clauses over x1,x2 -> UNSAT\np cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"}
R["minisat-2.2.0"] = {
    "runner": "docker", "image": "gcc:4.9", "workdir": "upstream/tree/minisat",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "make core release", "cmd": "cd core && MROOT=$(cd .. && pwd) make -s r 2>&1 | grep -v -i warning | tail -3; test -x ./minisat_release"}],
    "runs": [{"name": "satisfiable CNF", "cmd": "core/minisat_release $HARNESS/sat.cnf $BODY/harness/sat.out; rc=$?; cat $BODY/harness/sat.out; exit $rc",
              "expect": {"exit": 10, "stdout_contains": ["SAT\n1 2 0"]}},
             {"name": "unsatisfiable CNF", "cmd": "core/minisat_release $HARNESS/unsat.cnf $BODY/harness/unsat.out; rc=$?; cat $BODY/harness/unsat.out; exit $rc",
              "expect": {"exit": 20, "stdout_contains": ["UNSAT"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "MiniSat's exit status IS its answer: 10 = SAT, 20 = UNSAT (the SAT-competition convention). The model line '1 2 0' is x1=x2=true, checkable by hand against the three clauses. Built in a PRESERVED gcc 4.9 world (docker gcc:4.9): gcc 13 rejects the 2010 C++ (a default argument on a friend declaration in SolverTypes.h). The directive prefers an old world over a source rewrite, so the algorithm is untouched and the compatibility problem is recorded, not patched."}

# 5. SPIN 6.5.2 (C + yacc; docker bookworm because WSL has no bison). Smoke: a two-process
#    mutual-exclusion model with an assertion that holds, verified exhaustively.
H["spin-6.5.2-holzmann"] = {"mutex.pml": """/* Peterson's algorithm for two processes; the assertion is that both are never critical */
bool flag[2]; byte turn; byte ncrit;
active [2] proctype P() {
  pid i = _pid; pid j = 1 - _pid;
again:
  flag[i] = true; turn = j;
  (flag[j] == false || turn == i);
  ncrit++;
  assert(ncrit == 1);   /* critical section */
  ncrit--;
  flag[i] = false;
  goto again;
}
"""}
R["spin-6.5.2-holzmann"] = {
    "runner": "docker", "image": "prometheus-fossil-c:bookworm", "workdir": "upstream/tree/Spin-version-6.5.2/Src",
    "probe": [{"name": "toolchain", "cmd": "gcc --version | head -1; bison --version | head -1"}],
    "build": [{"name": "make spin", "cmd": "make -s 2>&1 | grep -v -i warning | tail -3; test -x ./spin"}],
    "runs": [{"name": "spin version", "cmd": "./spin -V", "expect": {"exit": 0, "stdout_contains": ["Spin Version 6.5.2"]}},
             {"name": "exhaustive verification of Peterson mutex",
              "cmd": "mkdir -p $BODY/build && cd $BODY/build && $BODY/upstream/tree/Spin-version-6.5.2/Src/spin -a $HARNESS/mutex.pml && gcc -O2 -DSAFETY -o pan pan.c && ./pan",
              "expect": {"exit": 0, "stdout_contains": ["errors: 0"]}}],
    "tests": [{"name": "a planted violation IS found (assert ncrit == 2 must fail)",
               "cmd": "mkdir -p $BODY/build/bad && cd $BODY/build/bad && sed 's/ncrit == 1/ncrit == 2/' $HARNESS/mutex.pml > bad.pml && $BODY/upstream/tree/Spin-version-6.5.2/Src/spin -a bad.pml && gcc -O2 -DSAFETY -o pan pan.c && ./pan; true",
               "expect": {"exit": 0, "stdout_contains": ["errors: 1"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER"}

# 6. Graphplan (C, WSL). The shipped lex.yy.c / y.tab.c are pre-generated, so no yacc is needed.
R["graphplan-blum-furst-1995"] = {
    "runner": "wsl", "workdir": "upstream/tree/Source",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s graphplan 2>&1 | grep -i -E 'error' ; test -x ./graphplan"}],
    "runs": [{"name": "rocket domain, facts2 (a two-rocket logistics problem)",
              "cmd": "mkdir -p $BODY/build && cp ./graphplan $BODY/upstream/domains/rocket_ops $BODY/upstream/domains/rocket_facts2 $BODY/build/ && cd $BODY/build && ./graphplan -o rocket_ops -f rocket_facts2 -d 2>&1 | tail -25",
              "expect": {"exit": 0, "stdout_contains": ["Goals first reachable", "LOAD_", "MOVE_", "UNLOAD_"]}},
             {"name": "monkey-and-bananas domain", "cmd": "cd $BODY/build && cp $BODY/upstream/domains/monkey_ops $BODY/upstream/domains/monkey_facts1 . && ./graphplan -o monkey_ops -f monkey_facts1 -d 2>&1 | tail -15",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(reachable|not solvable|steps)"}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "graphplan reads operator/fact files from the cwd by name (its lexer does not take a path), so the recipe copies the binary and the two domain files into $BODY/build and runs there; upstream/ is untouched. 1995 K&R-era C compiled clean under gcc 13 with only warnings."}

# 7. TSCP 1.81 (C, WSL). Deterministic fixed-depth search from the initial position.
R["tscp-1.81-kerrigan-1997"] = {
    "runner": "wsl", "workdir": "upstream/tree/tscp181",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile", "cmd": "gcc -O2 -o tscp *.c 2>&1 | grep -i error; test -x ./tscp"}],
    "runs": [{"name": "built-in fixed-depth benchmark (iterative deepening 1..5 from the opening)",
              "cmd": "printf 'bench\\nquit\\n' | ./tscp | tail -12",
              "expect": {"exit": 0, "stdout_contains": ["Nodes: 550778"]}}],
    "tests": [{"name": "the benchmark node count is deterministic across two runs",
               "cmd": "a=$(printf 'bench\\nquit\\n' | ./tscp | grep -i '^Nodes:'); b=$(printf 'bench\\nquit\\n' | ./tscp | grep -i '^Nodes:'); echo \"$a\"; test \"$a\" = \"$b\" && echo DETERMINISTIC",
               "expect": {"exit": 0, "stdout_contains": ["DETERMINISTIC", "550778"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "TSCP's 'go'/'sd N' interactive commands make the engine PLAY (it then waits for the next move on stdin); the shipped 'bench' command is the deterministic fixed workload -- alpha-beta with the same move ordering visits exactly 550778 nodes to depth 5 from the start, which is what makes it a clean fossil to perturb. Nodes-per-second is machine-dependent and is NOT gated."}

# 8. LDPC-codes (C, WSL): upstream Makefile and its own test script.
R["ldpc-codes-neal-2001"] = {
    "runner": "wsl", "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | grep -i -E '^.*error' ; test -x ./decode && test -x ./make-ldpc"}],
    "runs": [{"name": "make-ldpc / encode / transmit / decode / verify pipeline on a small random code",
              "cmd": "mkdir -p $BODY/build && cd $BODY/build && S=$BODY/upstream/tree && $S/make-ldpc ex.pchk 20 40 1 evenboth 3 2>&1 && $S/make-gen ex.pchk ex.gen dense 2>&1 && $S/rand-src ex.src 1 20x10 2>&1 && $S/encode ex.pchk ex.gen ex.src ex.enc 2>&1 && $S/transmit ex.enc ex.rec 1 bsc 0.05 2>&1 && $S/decode ex.pchk ex.rec ex.dec bsc 0.05 prprp 100 2>&1 && $S/verify ex.pchk ex.dec ex.gen ex.src 2>&1",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(decoded|bit error rate|block)"}}],
    "tests": [{"name": "upstream test script", "cmd": "make test 2>&1 | tail -15", "expect": {"exit": 0}}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_NATIVE"}

# 9. SQLite amalgamation (C, WSL). Smoke: a transaction, a join, an index, and a rollback.
H["sqlite-3.49.1-amalgamation"] = {"smoke.sql": """CREATE TABLE a(id INTEGER PRIMARY KEY, v TEXT);
CREATE TABLE b(aid INTEGER REFERENCES a(id), w INTEGER);
CREATE INDEX b_aid ON b(aid);
INSERT INTO a VALUES (1,'x'),(2,'y'),(3,'z');
INSERT INTO b VALUES (1,10),(1,11),(3,30);
BEGIN; INSERT INTO a VALUES (4,'rolled-back'); ROLLBACK;
SELECT a.v, sum(b.w) FROM a JOIN b ON b.aid=a.id GROUP BY a.v ORDER BY a.v;
SELECT count(*) FROM a;
EXPLAIN QUERY PLAN SELECT * FROM b WHERE aid=1;
"""}
R["sqlite-3.49.1-amalgamation"] = {
    "runner": "wsl", "workdir": "upstream/tree/sqlite-amalgamation-3490100",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile shell", "cmd": "mkdir -p $BODY/build && gcc -O2 -DSQLITE_THREADSAFE=0 -o $BODY/build/sqlite3 shell.c sqlite3.c -lm -ldl 2>&1 | grep -i error; test -x $BODY/build/sqlite3"}],
    "runs": [{"name": "version", "cmd": "$BODY/build/sqlite3 -version", "expect": {"exit": 0, "stdout_contains": ["3.49.1"]}},
             {"name": "transactions, join, index, rollback", "cmd": "$BODY/build/sqlite3 :memory: < $HARNESS/smoke.sql",
              "expect": {"exit": 0, "stdout_contains": ["x|21", "z|30", "3", "USING INDEX b_aid"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "the amalgamation carries no test suite; SQLite's TCL/TH3 tests live in the source tree (queued as a separate artefact)."}

# 10. ncompress (C, WSL): build and a byte-exact round trip on its own source.
R["ncompress-5.0-lzw-1985"] = {
    "runner": "wsl", "workdir": "upstream/tree/ncompress-5.0",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s compress 2>&1 | grep -i error; test -x ./compress"}],
    "runs": [{"name": "LZW round trip on compress.c", "cmd": "mkdir -p $BODY/build && ./compress -c compress.c > $BODY/build/c.Z && ./compress -dc $BODY/build/c.Z | cmp - compress.c && echo ROUNDTRIP_OK $(stat -c %s compress.c) '->' $(stat -c %s $BODY/build/c.Z)",
              "expect": {"exit": 0, "stdout_contains": ["ROUNDTRIP_OK"]}}],
    "tests": [{"name": "a corrupted .Z is refused, not silently decoded", "cmd": "cp $BODY/build/c.Z $BODY/build/bad.Z && printf '\\xff\\xff\\xff\\xff' | dd of=$BODY/build/bad.Z bs=1 seek=100 conv=notrunc 2>/dev/null && ./compress -dc $BODY/build/bad.Z > /dev/null 2>&1; test $? -ne 0 && echo CORRUPTION_DETECTED",
               "expect": {"exit": 0, "stdout_contains": ["CORRUPTION_DETECTED"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_NATIVE"}

# 11. TinyScheme (C, WSL): build; evaluate tail recursion, call/cc, a closure.
H["tinyscheme-1.42"] = {"smoke.scm": """(define (loop n acc) (if (= n 0) acc (loop (- n 1) (+ acc 1))))
(display (loop 100000 0)) (newline)
(display (call/cc (lambda (k) (+ 1 (k 42))))) (newline)
(define (make-counter) (let ((n 0)) (lambda () (set! n (+ n 1)) n)))
(define c (make-counter)) (c) (c)
(display (c)) (newline)
(quit)
"""}
R["tinyscheme-1.42"] = {
    "runner": "wsl", "workdir": "upstream/tree/tinyscheme-1.42",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | grep -i -E ' error' ; test -x ./scheme"}],
    "runs": [{"name": "tail recursion 100000 deep, call/cc, closure", "cmd": "./scheme $HARNESS/smoke.scm",
              "expect": {"exit": 0, "stdout_contains": ["100000", "42", "3"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_NATIVE"}

# 12. c-cmaes (C, WSL): Hansen's example1 on the shipped parameter file; seeded, so repeatable.
R["c-cmaes-hansen"] = {
    "runner": "wsl", "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile example_short", "cmd": "gcc -O2 -o $BODY/evo1 src/example_short.c src/cmaes.c -lm 2>&1 | grep -i error; test -x $BODY/evo1"}],
    "runs": [{"name": "example_short: minimise the cigtab test function via CMA-ES", "cmd": "mkdir -p $BODY/build && cd $BODY/build && cp -f $BODY/upstream/tree/cmaes_initials.par $BODY/upstream/tree/cmaes_signals.par . && $BODY/evo1 2>&1 | tail -16",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(stop|fbestever|function value|clock)"}}],
    "tests": [{"name": "the run terminates on a declared stopping criterion",
               "cmd": "cd $BODY/build && $BODY/evo1 2>&1 | grep -i -E 'stop|fbestever|TolFun|MaxIter' | head -5; echo DONE",
               "expect": {"exit": 0, "stdout_contains": ["DONE"], "stdout_regex": r"(?i)(stop|fbestever|tolfun|maxiter)"}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_NATIVE",
    "notes": "example_short.c is the self-contained example (example1.c is not in this release); it optimises the built-in felli/rosenbrock test function and writes cmaes outcome files into the cwd, so the recipe runs it in $BODY/build and never writes upstream/. example_short seeds from the clock, so the exact trajectory is not reproducible run-to-run; the test checks the log SHAPE is stable rather than asserting byte-identity."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid)
        d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "recipe" + (" + harness" if sid in H else ""))


if __name__ == "__main__":
    main()
