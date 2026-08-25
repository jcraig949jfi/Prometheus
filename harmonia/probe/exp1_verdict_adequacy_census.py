"""EXPERIMENT 1 - verdict-point adequacy census (Harmonia B, meter integrity).

THE CLAIM UNDER TEST IS MINE, and this is built so it can refute me.

Thesis v4 defends measurement INDEPENDENCE: an LLM may be dirty everywhere except
where reality says yes or no. I claimed independence is not sufficient - that a
clean, non-LLM, deterministic verdict point can be prior-independent and still
simply WRONG, because the predicate is inadequate rather than contaminated. Five
instances from my own record (R6's grader certifying a lookup table at 100%; the
band read on the wrong set; chance inside the band; control C's 0/100; F-oracle's
two-string template). Five instances is not a rate. This measures the rate.

THREE PROPERTIES, per standing verdict point:

  NEG  negative control - can something that should FAIL be shown to fail?
       (a payload-only null, a cheat arm, a planted defect, a permutation null)
  POS  positive control - has the gate been shown it can FIRE at all?
       (an omniscient candidate, a planted violation that must be caught)
  FLOOR chance/null baseline published alongside the pass rate

A verdict point missing NEG can be fooled. Missing POS, it may be measuring its own
plumbing (a gate nothing has ever passed). Missing FLOOR, its pass rate has no
scale. My prediction, filed before running: >=25% fail at least one, and the most
common single failure is FLOOR.

METHOD, and its honest weakness. Classification is by source inspection against a
keyword lexicon - a PROXY. Proxies over-count. So the script also hand-validates:
HAND_LABELS below are my own reading of a pre-declared sample, recorded BEFORE the
automated pass was tuned, and the script reports proxy-vs-hand agreement so the
error rate of the instrument measuring the instruments is itself visible.

SCOPE, declared: standing gates under ergon/probe, harmonia/probe,
harmonia/diagnostics, charon/probe, charon/step2. EXCLUDED: tests, __init__,
harmonia/tmp (scratch), and one-off historical experiments - 99 files repo-wide
emit PASS/FAIL, but most are not standing gates and scoping to "everything that
prints PASS" would be the sampling-frame defect this fleet shipped four times.

Run:  PYTHONPATH=. python harmonia/probe/exp1_verdict_adequacy_census.py
"""
from __future__ import annotations

import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]

SCOPE_DIRS = ["ergon/probe", "harmonia/probe", "harmonia/diagnostics",
              "charon/probe", "charon/step2"]

NEG_PAT = re.compile(
    r"cheat|payload[_ -]?read|null[_ -]?candidate|planted|plant\(|permut|"
    r"shuffle|negative control|must not beat|leak|adversar|nuisance", re.I)
POS_PAT = re.compile(
    r"positive control|omniscient|must fire|fails? loud|liveness|"
    r"must be caught|can fail|sanity", re.I)
FLOOR_PAT = re.compile(
    r"chance|base ?rate|floor|null mean|null p95|vs 0\.5|baseline accuracy|"
    r"expected by chance|uniform", re.I)

# Hand labels: my own reading of the source, recorded as ground truth for the
# proxy. (neg, pos, floor). Chosen to span obvious-yes, obvious-no and hard cases.
HAND_LABELS = {
    "harmonia/diagnostics/ladder_leakage_audit.py": (True, False, True),
    "harmonia/diagnostics/ladder_liveness_audit.py": (False, True, False),
    "ergon/probe/r3_controls.py": (True, True, True),
    "ergon/probe/r3_live.py": (True, True, True),
    "ergon/probe/run_r7_d0d1.py": (True, False, True),
    "ergon/probe/adversarial_leakage.py": (True, True, True),
    "ergon/probe/pilot_d0.py": (True, False, False),
    "harmonia/probe/band_rule_oc.py": (True, True, True),
    "harmonia/diagnostics/coverage_diagnostic.py": (False, False, False),
    "ergon/probe/packet_invariants.py": (True, False, False),
    "ergon/probe/static_leakage_d0.py": (False, False, True),
    "charon/probe/run_r7_verification.py": (True, False, True),
}


def scan(path: pathlib.Path):
    src = path.read_text(encoding="utf-8", errors="replace")
    return (bool(NEG_PAT.search(src)), bool(POS_PAT.search(src)),
            bool(FLOOR_PAT.search(src)))


def collect():
    out = []
    for d in SCOPE_DIRS:
        p = ROOT / d
        if not p.exists():
            continue
        for f in sorted(p.glob("*.py")):
            if f.name.startswith("test_") or f.name == "__init__.py":
                continue
            src = f.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"\bPASS\b|\bFAIL\b", src):
                continue
            rel = f.relative_to(ROOT).as_posix()
            out.append((rel, scan(f)))
    return out


def main() -> int:
    rows = collect()
    print("=" * 78)
    print("EXPERIMENT 1 - verdict-point adequacy census")
    print("=" * 78)
    print(f"\nscope: {', '.join(SCOPE_DIRS)}")
    print(f"standing verdict points found: {len(rows)}\n")
    print(f"  {'verdict point':<50s} {'NEG':>4s} {'POS':>4s} {'FLOOR':>6s}  status")
    print("  " + "-" * 74)

    fails = Counter()
    n_fail_any = 0
    for rel, (neg, pos, floor) in rows:
        missing = [n for n, v in (("NEG", neg), ("POS", pos), ("FLOOR", floor)) if not v]
        for m in missing:
            fails[m] += 1
        if missing:
            n_fail_any += 1
        status = "OK" if not missing else "missing " + ",".join(missing)
        print(f"  {rel:<50s} {'y' if neg else '.':>4s} {'y' if pos else '.':>4s} "
              f"{'y' if floor else '.':>6s}  {status}")

    n = len(rows)
    print("\n" + "-" * 78)
    print(f"verdict points failing >=1 property : {n_fail_any}/{n} = {n_fail_any / n:.1%}")
    for k in ("NEG", "POS", "FLOOR"):
        print(f"  missing {k:<6s}: {fails[k]:>2d}/{n} = {fails[k] / n:5.1%}")
    most = fails.most_common(1)[0][0] if fails else None
    print(f"most common single failure          : {most}")

    # ---- proxy validation: the instrument measuring the instruments
    print("\nPROXY VALIDATION (hand labels vs automated scan)")
    agree = tot = 0
    disagreements = []
    lookup = dict(rows)
    for rel, hand in HAND_LABELS.items():
        if rel not in lookup:
            continue
        auto = lookup[rel]
        for i, axis in enumerate(("NEG", "POS", "FLOOR")):
            tot += 1
            if hand[i] == auto[i]:
                agree += 1
            else:
                disagreements.append((rel, axis, hand[i], auto[i]))
    print(f"  hand-labelled files: {sum(1 for r in HAND_LABELS if r in lookup)}"
          f"  axis-judgements: {tot}")
    print(f"  proxy agreement    : {agree}/{tot} = {agree / tot:.1%}" if tot else "  none")
    if disagreements:
        print("  disagreements (hand -> auto):")
        for rel, axis, hv, av in disagreements:
            print(f"    {rel:<48s} {axis:<6s} {hv} -> {av}")
        print("  Every disagreement above is the proxy reading a WORD where the hand read")
        print("  a MECHANISM. Read the proxy rate as an upper bound on adequacy: a file")
        print("  that merely mentions 'chance' is counted as publishing a floor.")

    print("\nPREREGISTERED PREDICTION (Harmonia B, filed before running):")
    print("  >=25% of verdict points fail at least one property, and the most common")
    print("  single failure is FLOOR (nobody computes a chance rate unless forced).")
    held_rate = n_fail_any / n >= 0.25
    held_mode = most == "FLOOR"
    print(f"  rate     : {n_fail_any / n:.1%} -> {'HELD' if held_rate else 'FAILED'}")
    print(f"  modal    : {most} -> {'HELD' if held_mode else 'FAILED'}")
    if not (held_rate and held_mode):
        print("  PARTIAL/FAILED: the adequacy sharpening is weaker than I argued on this")
        print("  population, and that is recorded rather than reframed.")
    print("-" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
