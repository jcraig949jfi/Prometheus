"""Negative control for report_audit.py. An audit that cannot fail proves nothing.

Each mutation below reinjects a defect that was actually present in revision 1 of
REPORT.html (or a near neighbour of one), and asserts the audit rejects the mutated
report. A mutation that does not apply is itself a failure: it means the string the
test targets has moved and the test has gone vacuous without anyone noticing.

Run:  python test_report_audit.py
Exit: 0 every defect caught, 1 otherwise.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent

# name -> (find, replace). Applied to REPORT.html; each must change the file.
MUTATIONS = {
    # R-01: the defect that made revision 1 state two headline effects backwards.
    "sign_inversion": ('"better_level":"EXPLICIT_FITNESS"',
                       '"better_level":"NONE_IMPLICIT"'),
    # R-02: naming a run that adjudicates WEAK as the admissible instance.
    "wrong_run_identity": ('"run_id":"64dea50f417efb02-s1203-tL-a0"',
                           '"run_id":"1af37ab8c765a7b2-s1099-tL-a0"'),
    # R-02 root cause: sourcing a verdict claim from the preregistered flag stream.
    "verdict_sourced_from_specials": ('"source":"ADJUDICATION.json"',
                                      '"source":"SPECIALS.jsonl"'),
    # R-04: an effect table inherited from a summary rather than the record.
    "stale_axis_count": ('"n_axes_shown": 28', '"n_axes_shown": 24'),
    "stale_pair_total": ('"n_pairs_total": 10741', '"n_pairs_total": 10000'),
    # Counts drifting from the adjudication record.
    "stale_verdict_count": ('"REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION","ADMISSIBLE":1,"WEAK":50',
                            '"REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION","ADMISSIBLE":3,"WEAK":50'),
    "stale_reason_count": ('"why_contains":"seeded instrument","n":117',
                           '"why_contains":"seeded instrument","n":124'),
    "stale_distribution": ('{"key":"depth_1_only","value":911}',
                           '{"key":"depth_1_only","value":120}'),
    # Asserting a capability the substrate does not have.
    "lineage_capability_overclaim": ('{"key":"migration_events_logged","value":false}',
                                     '{"key":"migration_events_logged","value":true}'),
    # An effect value that does not match the record.
    "effect_value_drift": ('"axis_key":"pressure:EXPLICIT_FITNESS->NONE_IMPLICIT","n_pairs":513',
                           '"axis_key":"pressure:EXPLICIT_FITNESS->NONE_IMPLICIT","n_pairs":600'),
}

# R-03: categorical prose the record cannot support. Inserted into an asserted
# paragraph, not into the corrections section, which is allowed to quote retractions.
PROSE_MUTATIONS = {
    "banned_phrase_answerable": (
        "<strong>The reservoir question is not answerable",
        "<strong>This is answerable from per-run lineage records. The reservoir question is not answerable"),
    "banned_phrase_proves": (
        "<strong>Explicit fitness outperformed",
        "<strong>This proves explicit fitness outperformed"),
}


def run_audit(report_path):
    r = subprocess.run([sys.executable, str(HERE / "report_audit.py"),
                        str(HERE / "observatory"), str(report_path)],
                       capture_output=True, text=True)
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    return r.returncode, fails


def main():
    report = HERE / "REPORT.html"
    html = report.read_text(encoding="utf-8")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="reportaudit_"))

    rc, fails = run_audit(report)
    print("%-32s %-8s %s" % ("baseline (unmutated)", "PASS" if rc == 0 else "FAIL",
                             "0 failures" if rc == 0 else fails[0][:80]))
    ok = rc == 0
    if rc != 0:
        print("  baseline must pass before the negative control means anything")

    print()
    print("%-32s %-8s %s" % ("injected defect", "result", "caught by"))
    print("-" * 100)
    for name, (find, repl) in {**MUTATIONS, **PROSE_MUTATIONS}.items():
        if find not in html:
            print("%-32s %-8s %s" % (name, "VACUOUS", "target string absent; test no longer exercises anything"))
            ok = False
            continue
        p = tmp / ("%s.html" % re.sub(r"\W+", "_", name))
        p.write_text(html.replace(find, repl, 1), encoding="utf-8")
        rc, fails = run_audit(p)
        caught = rc != 0 and fails
        if not caught:
            ok = False
        print("%-32s %-8s %s" % (name, "caught" if caught else "MISSED",
                                 fails[0][5:].strip()[:62] if fails else "audit returned PASS"))
    print("-" * 100)
    print("negative control:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
