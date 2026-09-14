"""Batch 09 recipes + harnesses (2026-09-13). python -m techne.fossils.batches.batch09_recipes
Each runs in the disposable work/ copy; deviations in each recipe's notes."""
from __future__ import annotations

import json
from .. import vault

LANG = "prometheus-fossil-lang:bookworm"
R = {}
H = {}

# ---- avida UNLOCK (charter P1/P5): builds offline from the now-complete body -------------------
# The image already ships cmake/g++/make and libs/apto is preserved IN the body at the commit the
# superproject pins, so this recipe fetches NOTHING from the network -- that is the whole point of
# the P1 repair. AVIDA_DISABLE_BACKTRACE=1 avoids backward-cpp's libbfd probe;
# CMAKE_POLICY_VERSION_MINIMUM=3.5 is needed because the tree's cmake_minimum_required predates
# 2.8.12 and modern CMake refuses it. Neither changes avida's own source.
R["avida"] = {
    "runner": "docker", "image": LANG, "workdir": "upstream/tree",
    "probe": [{"name": "toolchain present without apt", "cmd": "cmake --version | head -1; g++ --version | head -1"},
              {"name": "pinned submodule is IN the body (the P1 repair)",
               "cmd": "echo apto=$(find libs/apto -type f | wc -l) backward_cpp=$(find libs/backward-cpp -type f | wc -l); test $(find libs/apto -type f | wc -l) -gt 50"}],
    "build": [{"name": "cmake + make avida (offline; apto from the preserved body)",
               "cmd": "export AVIDA_DISABLE_BACKTRACE=1; mkdir -p cbuild && cd cbuild && "
                      "cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release .. >/tmp/cmake.log 2>&1 && "
                      "make -j4 avida >/tmp/make.log 2>&1; test -x ./bin/avida && echo BUILT || { tail -20 /tmp/make.log; false; }",
               "timeout": 2400}],
    "runs": [{"name": "evolve a population from the hand-written ancestor for 300 updates (self-replication + descent)",
              "cmd": "W=$(pwd); cp -r avida-core/support/config /tmp/run && cd /tmp/run && "
                     "sed -i 's/^u 100000 Exit/u 300 Exit/' events.cfg && "
                     "$W/cbuild/bin/avida -c avida.cfg > /tmp/run.log 2>&1; "
                     "L=$(grep '^UD:' /tmp/run.log | tail -1); echo \"FINAL $L\"; "
                     "O=$(echo \"$L\" | sed 's/.*Orgs: *//;s/ *$//'); G=$(echo \"$L\" | sed 's/.*Gen: *//;s/ .*//'); "
                     "B=$(grep -v '^#' data/count.dat | tail -1 | awk '{print $4}'); echo \"ORGS=$O GEN=$G BIRTHS=$B\"; "
                     "awk -v o=\"$O\" -v g=\"$G\" -v b=\"$B\" 'BEGIN{print (o>100 && g>5 && b>100) ? \"SELF_REPLICATING_POPULATION=yes\" : \"SELF_REPLICATING_POPULATION=no\"}'",
              "expect": {"exit": 0, "stdout_contains": ["SELF_REPLICATING_POPULATION=yes"]}, "timeout": 1200}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: from ONE hand-written ancestor genome (default-heads.org) the population must "
             "self-replicate and show descent -- >100 organisms, mean generation >5, >100 births by "
             "update 300. Observed 1068 orgs, generation 22.96, 808 births. tasks.dat stays all-zero "
             "at 300 updates (the logic-task rewards need far longer runs); that is recorded, not "
             "interpreted. This fossil SEGFAULTED for an entire batch while libs/apto was an empty "
             "directory in the body; it builds and runs only because the submodule is now preserved "
             "at the superproject's pinned commit. Nothing in avida's source was modernised."}


C = "prometheus-fossil-c:bookworm"

# ---- LINPACK (loser): its own benchmark is its own oracle ------------------------------------
R["linpack-netlib-1979"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "gfortran -std=legacy (the 1979 Fortran compiles unchanged)",
               "cmd": "gfortran -std=legacy -w -O2 -o linpackd linpackd.f 2>&1 | grep -i 'error' | head -3; test -x ./linpackd && echo BUILT", "timeout": 600}],
    "runs": [{"name": "the LINPACK 100x100 benchmark: solve a system whose exact solution is all ones, report residual + MFLOPS",
              "cmd": "./linpackd < /dev/null 2>&1 | grep -A2 -E 'norm. resid|dgefa' | head -12",
              "expect": {"exit": 0, "stdout_regex": r"1\.00000000E\+00\s+1\.00000000E\+00"}, "timeout": 600},
             {"name": "the rate the benchmark reports (the quantity LAPACK was built to improve)",
              "cmd": "./linpackd < /dev/null 2>&1 | grep -E 'mflops|times for|^ *[0-9]+\\.' | head -8; true",
              "expect": {"exit": 0}, "timeout": 600}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the benchmark constructs a system whose exact solution is the all-ones vector and prints x(1) and x(n); both must come back 1.00000000E+00, with a residual at machine epsilon (observed 1.39e-14, machep 2.22e-16). That is LINPACK grading itself. The MFLOPS figure is recorded, not compared -- the LINPACK/LAPACK rate comparison is a separate dataset, and Techne does not rank them here."}

# ---- EISPACK (loser): eigenvalues of a matrix with a closed-form spectrum ---------------------
R["eispack-netlib-1976"] = {
    "runner": "docker", "image": C, "workdir": "upstream",
    "probe": [{"name": "gfortran", "cmd": "gfortran --version | head -1"}],
    "build": [{"name": "gfortran -std=legacy: rs + tred2 + tql2 + harness driver",
               "cmd": "cp $HARNESS/driver.f . && gfortran -std=legacy -w -O2 -o eig driver.f rs.f tred2.f tql2.f tred1.f tqlrat.f pythag.f epslon.f tql1.f 2>&1 | grep -iE 'error|undefined' | head -8; test -x ./eig && echo BUILT", "timeout": 600}],
    "runs": [{"name": "all eigenvalues/vectors of the 3x3 tridiagonal [2,-1;-1,2,-1;-1,2] (exact spectrum 2-sqrt2, 2, 2+sqrt2)",
              "cmd": "./eig 2>&1 | head -12",
              "expect": {"exit": 0, "stdout_contains": ["0.585786", "2.000000", "3.414214"]}, "timeout": 600}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the second-difference matrix has the closed-form spectrum 2-sqrt(2)=0.5857864, 2, 2+sqrt(2)=3.4142136, so EISPACK is graded against exact mathematics rather than another program. rs is called with matz=1 so it routes through tred2+tql2 (the routines preserved here); matz=0 would need tred1/tqlrat, which are not in this body -- recorded, not worked around."}
H["eispack-netlib-1976"] = {"driver.f": """      program eigdrv
      integer nm,n,matz,ierr
      double precision a(3,3),w(3),z(3,3),fv1(3)
      nm = 3
      n = 3
      matz = 1
      a(1,1)= 2.0d0
      a(1,2)=-1.0d0
      a(1,3)= 0.0d0
      a(2,1)=-1.0d0
      a(2,2)= 2.0d0
      a(2,3)=-1.0d0
      a(3,1)= 0.0d0
      a(3,2)=-1.0d0
      a(3,3)= 2.0d0
      call rs(nm,n,a,w,matz,z,fv1,fv1,ierr)
      write(6,10) ierr
   10 format(' ierr = ',i4)
      write(6,20) w(1),w(2),w(3)
   20 format(' eigenvalues: ',3f12.6)
      stop
      end
"""}

# ---- MD5 (loser): the RFC carries the code AND the digests it must produce --------------------
_MD5_STRIP = ("grep -v '\\[Page ' | grep -v '^RFC 1321' | tr -d '\\f' | "
              "awk '{ if ($0 ~ /^[[:space:]]*$/ && cont) next; print; cont = ($0 ~ /\\\\[[:space:]]*$/) }'")
R["md5-rfc1321"] = {
    "runner": "docker", "image": "prometheus-fossil-i386:bookworm", "workdir": "upstream",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "extract the appendix sources from the RFC text, then compile with -DMD=5",
               "cmd": ("sed -n '/^A\\.1 global\\.h/,/^A\\.2 md5\\.h/p' rfc1321.txt | sed '1d;$d' | " + _MD5_STRIP + " > global.h; "
                       "sed -n '/^A\\.2 md5\\.h/,/^A\\.3 md5c\\.c/p' rfc1321.txt | sed '1d;$d' | " + _MD5_STRIP + " > md5.h; "
                       "sed -n '/^A\\.3 md5c\\.c/,/^A\\.4 mddriver\\.c/p' rfc1321.txt | sed '1d;$d' | " + _MD5_STRIP + " > md5c.c; "
                       "sed -n '/^A\\.4 mddriver\\.c/,/^A\\.5 Test suite/p' rfc1321.txt | sed '1d;$d' | " + _MD5_STRIP + " > mddriver.c; "
                       "wc -l global.h md5.h md5c.c mddriver.c; "
                       "gcc -w -DMD=5 -o mddriver md5c.c mddriver.c 2>&1 | head -5; test -x ./mddriver && echo BUILT"),
               "timeout": 600}],
    "runs": [{"name": "the environment assumption the 1992 code depends on: UINT4 is `unsigned long`",
              "cmd": "printf 'int main(){return sizeof(unsigned long);}' > /tmp/z.c; gcc -o /tmp/z /tmp/z.c; /tmp/z; echo \"sizeof_unsigned_long=$?\"",
              "expect": {"exit": 0, "stdout_contains": ["sizeof_unsigned_long=4"]}, "timeout": 120},
             {"name": "run the RFC's own MD5 test suite (-x) and compare with the digests printed in the RFC",
              "cmd": "./mddriver -x 2>&1 | head -12",
              "expect": {"exit": 0, "stdout_contains": ["d41d8cd98f00b204e9800998ecf8427e",
                                                        "0cc175b9c0f1b6a831c399e269772661",
                                                        "900150983cd24fb0d6963f7d28e17f72"]}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "ENVIRONMENT: run in the vault's 32-bit userland, which is the code's ORIGINAL world, not a modernisation. RFC 1321's global.h declares `typedef unsigned long int UINT4`, true on the 32-bit machines of 1992 and FALSE on today's LP64 targets. Built with the modern 64-bit toolchain this same body compiles cleanly, runs, and prints CONFIRMED-WRONG digests (MD5(\"\") came out e4c23762ed2823a27e62a64b95c024e7 instead of d41d8cd98f00b204e9800998ecf8427e) -- a silent numerical failure caused by the environment moving, recorded in ENVIRONMENT_ASSUMPTION_2026-09-13.json. Oracle: RFC 1321 section A.5 prints the digests its own reference code must produce -- MD5(\"\")=d41d8cd9..., MD5(\"a\")=0cc175b9..., MD5(\"abc\")=90015098... The standard, the implementation and the test suite are one artifact; the build extracts the appendix out of the RFC text. NOTE the fossil's point: every one of these vectors still PASSES. What broke in 2004 was collision resistance, which no self-test in the document can detect."}

# ---- DES (loser) --------------------------------------------------------------------------
R["des-reference"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "gcc -O3 des.c run_des.c", "cmd": "gcc -O2 -o run_des des.c run_des.c 2>&1 | grep -i 'error' | head -3; test -x ./run_des && echo BUILT", "timeout": 600}],
    "runs": [{"name": "generate a key, encrypt a known plaintext, decrypt it back (16-round Feistel round trip)",
              "cmd": ("printf 'The quick brown fox jumps over the lazy dog. 1234567890' > /tmp/pt.txt; "
                      "./run_des -g /tmp/k.key >/dev/null 2>&1; "
                      "./run_des -e /tmp/k.key /tmp/pt.txt /tmp/ct.bin >/dev/null 2>&1; "
                      "./run_des -d /tmp/k.key /tmp/ct.bin /tmp/rt.txt >/dev/null 2>&1; "
                      "echo -n 'roundtrip_identical='; cmp -s /tmp/pt.txt /tmp/rt.txt && echo yes || echo no; "
                      "echo -n 'ciphertext_differs='; cmp -s /tmp/pt.txt /tmp/ct.bin && echo no || echo yes; "
                      "echo -n 'key_bytes='; wc -c < /tmp/k.key"),
              "expect": {"exit": 0, "stdout_contains": ["roundtrip_identical=yes", "ciphertext_differs=yes"]},
              "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: a full 16-round Feistel round trip -- the decryption must reproduce the plaintext byte-for-byte while the ciphertext differs from it. This implementation is file-oriented with PKCS5 padding and does NOT expose a raw single-block interface, so a FIPS known-answer vector is not run here; that limitation is recorded rather than papered over. The historical failure of DES was never its round function: it was the 56-bit key, which no round trip can reveal."}

# ---- tiny-AES (winner of the cipher pair) -----------------------------------------------------
R["tiny-aes-c"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "gcc aes.c test.c", "cmd": "gcc -O2 -o aes_test aes.c test.c 2>&1 | grep -i 'error' | head -3; test -x ./aes_test && echo BUILT", "timeout": 600}],
    "runs": [{"name": "the shipped NIST SP 800-38A known-answer vectors (ECB/CBC/CTR, AES-128/192/256)",
              "cmd": "./aes_test 2>&1 | tail -20",
              "expect": {"exit": 0, "stdout_contains": ["3ad77bb40d7a3660a89ecaf32466ef97", "2b7e151628aed2a6abf7158809cf4f3c"]}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: NIST SP 800-38A appendix vectors -- AES-128 key 2b7e151628aed2a6abf7158809cf4f3c over plaintext block 6bc1bee22e409f96e93d7e117393172a gives ciphertext 3ad77bb40d7a3660a89ecaf32466ef97. Kept as the WINNER of the DES/AES pair so the two can be compared on shared vectors later; Techne does not rank them."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid); d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "+harness" if sid in H else "")


if __name__ == "__main__":
    main()
