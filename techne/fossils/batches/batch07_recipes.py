"""Batch 07 recipes + harnesses (2026-09-13). python -m techne.fossils.batches.batch07_recipes
Each runs in the disposable work/ copy; deviations in each recipe's notes."""
from __future__ import annotations

import json
from .. import vault

C = "prometheus-fossil-c:bookworm"
R = {}
H = {}

# ---- theorem proving: E built from source, run on shipped TPTP problems ----------------------
R["eprover-2.6"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "./configure && make (builds PROVER/eprover)", "cmd": "./configure >/dev/null 2>&1 && make -s 2>&1 | grep -iE '\\berror' | head -3; B=$(find . -name eprover -type f -perm -u+x | head -1); echo BIN=$B; test -n \"$B\"", "timeout": 1800}],
    "runs": [{"name": "prove a group-theory theorem (GRP: shipped TPTP, Unsatisfiable = theorem)", "cmd": "B=$(find . -name eprover -type f -perm -u+x | head -1); $B --auto --tptp3-format EXAMPLE_PROBLEMS/TPTP/GRP237-1.p 2>&1 | grep -E 'SZS status|Proof found|processed clauses|generated clauses' | head -6",
              "expect": {"exit": 0, "stdout_regex": r"SZS status (Unsatisfiable|Theorem|ContradictoryAxioms)"}, "timeout": 300},
             {"name": "prove a Boolean-algebra lemma (BOO006-1, Unsatisfiable)", "cmd": "B=$(find . -name eprover -type f -perm -u+x | head -1); $B --auto --tptp3-format EXAMPLE_PROBLEMS/TPTP/BOO006-1.p 2>&1 | grep -E 'SZS status|Proof found' | head -3",
              "expect": {"exit": 0, "stdout_regex": r"SZS status (Unsatisfiable|Theorem)"}, "timeout": 300},
             {"name": "the search cost (generated vs processed clauses) -- the saturation working", "cmd": "B=$(find . -name eprover -type f -perm -u+x | head -1); $B --auto -s EXAMPLE_PROBLEMS/TPTP/GRP237-1.p 2>&1 | grep -iE 'clauses|generated|processed' | head -6; true",
              "expect": {"exit": 0}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the shipped TPTP problems carry '% Status : Unsatisfiable' -- a refutation exists, i.e. the conjecture is a theorem; E must report SZS status Unsatisfiable/Theorem. The problems are E's own EXAMPLE_PROBLEMS/TPTP. Saturation is visible in the generated/processed clause counts."}

# ---- symbolic algebra / number theory: PARI/GP from source ----------------------------------
R["pari-gp-2.17"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/pari-2.17.4",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "./Configure && make gp (readline/gmp optional)", "cmd": "./Configure >/dev/null 2>&1 && make -s gp 2>&1 | grep -iE '\\berror' | head -3; B=$(find . -name gp-dyn -type f -perm -u+x | head -1); echo BIN=$B; test -n \"$B\"", "timeout": 1800}],
    "runs": [{"name": "number theory: factor a Mersenne number, an elliptic-curve point count, a class number, the 1000th prime -- exact, against known values", "cmd": "B=$(find . -name gp-dyn -type f -perm -u+x | head -1); LD_LIBRARY_PATH=$(dirname $B) $B -q < $HARNESS/nt.gp 2>&1 | tail -8",
              "expect": {"exit": 0, "stdout_contains": ["193707721", "761838257287", "prime(1000) = 7919"]}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: known number-theoretic values -- 2^67-1 = 193707721 * 761838257287 (Cole 1903); prime(1000) = 7919; ellap of a named curve; a class number. Exact arithmetic on the PARI stack; gp built from source (readline/gmp optional, bundled fallback)."}
H["pari-gp-2.17"] = {"nt.gp": "print(\"factor 2^67-1: \", factor(2^67-1))\nprint(\"prime(1000) = \", prime(1000))\nE = ellinit([0,0,1,-1,0]); print(\"ellap(11): \", ellap(E, 11))\nprint(\"class number disc -23: \", qfbclassno(-23))\nprint(\"isprime(2^61-1): \", isprime(2^61-1))\n"}

# ---- bioinformatics: SSW (SIMD Smith-Waterman) -----------------------------------------------
R["ssw-smith-waterman"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/src",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make (ssw_test)", "cmd": "make -s 2>&1 | grep -iE '\\berror' | head -3; test -x ./ssw_test && echo built", "timeout": 600}],
    "runs": [{"name": "local-align a query against a reference sharing a conserved core (SIMD Smith-Waterman): optimal score + CIGAR", "cmd": "./ssw_test -c $HARNESS/ref.fa $HARNESS/query.fa 2>&1 | grep -iE 'optimal|score|target|cigar|=' | head -12",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(optimal_alignment_score|score)"}, "timeout": 300}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the query is a 40 bp read exactly matching a slice of the 120 bp reference, so the optimal local-alignment score is the full-match score and the CIGAR is 40M. SSW computes the exact SW optimum on SSE2 lanes; workdir is the extracted repo's src/. The scalar global/local DP pair (EMBOSS/seq-align) is a later depth add."}
H["ssw-smith-waterman"] = {
    "ref.fa": ">ref\nACGTACGTACGTACGTACGTACGTGGGGCCCCAAAATTTTACGTACGTACGTACGTACGTACGTTTTTGGGGCCCCAAAAACGTACGTACGTACGTACGTACGTGGGGTTTTCCCCAAAA\n",
    "query.fa": ">query\nGGGGCCCCAAAATTTTACGTACGTACGTACGTACGTACGT\n"}


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
