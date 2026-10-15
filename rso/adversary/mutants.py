"""The kit has teeth: single-line mutants of rso/completeness/verify.py (registry entry mutation-runner, rso.slice001.mutation)
run against the Z80 attack suite (rso.adversary.tests.test_mutants.SuiteZ80Attacks). Every mutant must be KILLED, i.e. the
kit would have flagged that regression. Nothing is written to verify.py: the runner edits source text in memory.

    python -m rso.adversary mutants [rows.jsonl]       exit 0 iff every mutant is killed (rows file must not exist yet)
"""
import os

from rso.registry.registry import ROOT
from rso.slice001 import mutation

EDITS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mutant_edits.json")
SUITE = ["rso.adversary.tests.test_mutants.SuiteZ80Attacks"]


def run_mutants(rows_path, require_committed=True, timeout_s=240):
    return mutation.run(EDITS_PATH, ROOT, SUITE, rows_path, timeout_s=timeout_s, require_committed=require_committed)
