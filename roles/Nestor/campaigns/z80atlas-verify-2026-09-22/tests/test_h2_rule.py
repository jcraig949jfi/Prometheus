"""T-H2. The ruled H2 decision rule (operator 2026-09-24), with boundary cases and an
injected defect.

Specimen: SUPPORTS iff B reaches depth >= 5 in >= 8/16 AND C in <= 2/16.
Panel: >= 2 supporting specimens from DIFFERENT strata = PANEL_POSITIVE; exactly one =
ISOLATED_CANDIDATE; several in one stratum = SAME_STRATUM_CANDIDATES (never positive).
Secondary readouts (depth >= 2, >= 3) are reported and never change a verdict.

Injection: a panel rule that counts supporting SPECIMENS instead of distinct STRATA must
be caught by the same-stratum case.

Run:  python tests/test_h2_rule.py      Exit 0 all demonstrated, 1 otherwise.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import hypotheses as H   # noqa: E402


def spec(b_hits, c_hits, a_depth=0, secondary_b=0, n=16, drop_arm=False):
    out = []
    for i in range(n):
        res = {"A_in_situ": {"max_causal_replication_depth": a_depth},
               "B_reimplant_actual": {"max_causal_replication_depth":
                                      5 if i < b_hits else (3 if i < b_hits + secondary_b else 1)},
               "C_reimplant_random": {"max_causal_replication_depth": 5 if i < c_hits else 0}}
        if drop_arm and i == 0:
            del res["C_reimplant_random"]
        out.append({"results": res})
    return out


def panel(entries):
    return {"s%d" % i: {"stratum": st, "bundles": b} for i, (st, b) in enumerate(entries)}


def main():
    ok = True

    def rec(name, got, want):
        nonlocal ok
        ok &= got == want
        print("%-6s %-54s got %-40s want %s" % ("PASS" if got == want else "FAIL", name, got, want))

    rec("B 8/16, C 2/16", H.h2_specimen(spec(8, 2))["verdict"], "SUPPORTS")
    rec("B 7/16, C 0/16", H.h2_specimen(spec(7, 0))["verdict"], "DOES_NOT_SUPPORT")
    rec("B 16/16, C 3/16", H.h2_specimen(spec(16, 3))["verdict"], "DOES_NOT_SUPPORT")
    rec("missing arm in one bundle", H.h2_specimen(spec(16, 0, drop_arm=True))["verdict"], "INCOMPLETE")
    rec("15 seeds only", H.h2_specimen(spec(15, 0, n=15))["verdict"], "INCOMPLETE")
    v = H.h2_specimen(spec(0, 0, secondary_b=16))
    rec("depth >= 3 everywhere is secondary only", v["verdict"], "DOES_NOT_SUPPORT")
    rec("  ...and is reported", v["secondary_readouts_only"]["depth_ge_3"]["B_reimplant_actual"], 16)

    X, Y = ("PAIR_EXECUTION", "WELL_MIXED", "Z8_32"), ("PAIR_EXECUTION", "NICHES_HIGH_MIG", "Z8_64")
    rec("two supporting, different strata", H.h2_panel(panel([(X, spec(9, 0)), (Y, spec(8, 1))]))["verdict"],
        "PANEL_POSITIVE")
    rec("exactly one supporting", H.h2_panel(panel([(X, spec(9, 0)), (Y, spec(2, 0))]))["verdict"],
        "ISOLATED_CANDIDATE")
    same = panel([(X, spec(9, 0)), (X, spec(10, 0)), (Y, spec(0, 0))])
    rec("two supporting, SAME stratum", H.h2_panel(same)["verdict"], "SAME_STRATUM_CANDIDATES")
    rec("none supporting", H.h2_panel(panel([(X, spec(0, 0))]))["verdict"],
        "REPLICATION_EVENTS_WITHOUT_PROPAGATION")

    # injected defect: count specimens, not strata
    src = (pathlib.Path(H.__file__)).read_text()
    target = 'if len(strata) >= C["H2_PANEL_MIN_SPECIMENS"]:'
    assert src.count(target) == 1, "target absent: injection would be VACUOUS"
    ns = {}
    exec(compile(src.replace(target, 'if len(supporting) >= C["H2_PANEL_MIN_SPECIMENS"]:'),
                 "hyp_injected", "exec"), ns)
    got = ns["h2_panel"](same)["verdict"]
    caught = got != "SAME_STRATUM_CANDIDATES"
    ok &= caught
    print("%-6s %-54s injected rule says %s" % ("caught" if caught else "MISSED",
                                                 "specimen-count panel rule", got))
    print("T-H2:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
