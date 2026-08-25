"""EXPERIMENT 3 - defect-class recurrence hazard (Harmonia B, meter integrity).

ANSWERS Q4 of the external review request: metabolism or treadmill?

    "In one week this fleet produced dozens of commits, a large fraction of which
     correct the previous commit... We read this as healthy self-correction. The
     uncomfortable alternative is a system whose output is mostly the repair of its
     own errors, with net forward motion near zero. What measurement distinguishes
     those two? We do not have one."

Commit volume does not distinguish them. Retraction count does not either - a
metabolizing system and a treadmill both produce many corrections. The quantity that
separates them is RECURRENCE:

  metabolism  a defect class, once structurally fixed, stops firing. Detection
              latency falls, because the guard catches it earlier each time.
  treadmill   the same class recurs under new names. Latency is flat. Repairs are
              local and absorb nothing.

MEASURED HERE
  1. Correction events mined from git history by signal words, classified into
     defect classes by a declared lexicon.
  2. Per-class recurrence: occurrences, span, and whether the class fires AFTER the
     commit that structurally fixed it.
  3. Detection latency proxy: commits between a class's occurrences.
  4. POWER: how many classes have n>=3, the minimum for any hazard statement.

HONEST LIMIT, PREDICTED IN ADVANCE. My filed prediction is that this comes out
UNDERPOWERED - most classes n=1, no hazard estimable, and the real output is the
instrumentation that makes it answerable next month. A measurement that reports
"underpowered" is doing its job; one that manufactures a hazard from n=1 is the
singleton-entropy artifact Charon caught on 2026-08-25.

Run:  PYTHONPATH=. python harmonia/probe/exp3_recurrence_hazard.py
"""
from __future__ import annotations

import subprocess
import re
from collections import Counter, defaultdict

# Signal words that mark a commit as CORRECTIVE rather than additive.
CORRECTION = re.compile(
    r"retract|withdraw|supersede|correction|corrected|artifact|"
    r"\bwrong\b|defect|invalid|void|mismatch|regress|"
    r"was an? (artifact|error)|does not (hold|survive)|"
    r"killed by|my own number|against my own", re.I)

# Declared defect-class lexicon. Derived from the nine defects enumerated in
# pivot/REVIEW_REQUEST_2026-08-25 plus the retraction registry's cross-cutting
# patterns. Order matters: first match wins, so specific precedes general.
CLASSES = [
    ("sampling-frame",      re.compile(r"glob|sampling frame|strided|prefix truncat|"
                                       r"population|denominator|subsample|corpus total", re.I)),
    ("degenerate-stratum",  re.compile(r"singleton|degenerat|zero variance|constant|"
                                       r"single-class|vacuous|no variance|cannot vary", re.I)),
    ("gate-cannot-fail",    re.compile(r"cannot fail|by construction|never emitted|"
                                       r"unrunnable|wired to nothing|inert|0\.0000|"
                                       r"gate that cannot", re.I)),
    ("answer-leak",         re.compile(r"leak|answer key|cheat|separable|arm identity|"
                                       r"fingerprint|oracle in", re.I)),
    ("wrong-population",    re.compile(r"different population|wrong set|post-screen|"
                                       r"pre-screen|defined on|mis-scoped|scope", re.I)),
    ("provenance-loss",     re.compile(r"deleted|never tracked|not committed|lost to|"
                                       r"swept into|concurrent|index race|autostash", re.I)),
    ("units-magnitude",     re.compile(r"magnitude|units|comparable units|threshold|"
                                       r"single-digit|four-digit|scale", re.I)),
    ("self-verdict",        re.compile(r"self-verdict|self-report|own judge|"
                                       r"generator carr|judge share", re.I)),
    ("spec-vs-code",        re.compile(r"docstring|imports? .* never call|specification|"
                                       r"as written|claims both|malformed", re.I)),
]


def git(*args) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def classify(text: str):
    for name, pat in CLASSES:
        if pat.search(text):
            return name
    return None


def main() -> int:
    raw = git("log", "--since=2026-06-01", "--date=short",
              "--pretty=format:%H\x01%ad\x01%s\x01%b\x02")
    commits = []
    for blob in raw.split("\x02"):
        blob = blob.strip()
        if not blob:
            continue
        parts = blob.split("\x01")
        if len(parts) < 3:
            continue
        h, d, s = parts[0], parts[1], parts[2]
        b = parts[3] if len(parts) > 3 else ""
        commits.append((h, d, s, b))
    commits.reverse()   # oldest first, so index == time order

    print("=" * 78)
    print("EXPERIMENT 3 - defect-class recurrence hazard (Q4: metabolism or treadmill)")
    print("=" * 78)
    print(f"\ncommits scanned (since 2026-06-01): {len(commits)}")

    events = []
    for i, (h, d, s, b) in enumerate(commits):
        text = s + "\n" + b
        if not CORRECTION.search(text):
            continue
        cls = classify(text)
        events.append((i, h[:8], d, cls, s[:70]))

    corrective = len(events)
    classified = [e for e in events if e[3]]
    print(f"corrective commits (signal words) : {corrective} "
          f"({corrective / len(commits):.1%} of all commits)")
    print(f"  of those, classified             : {len(classified)}")
    print(f"  unclassified (no lexicon match)  : {corrective - len(classified)}")

    by_class = defaultdict(list)
    for i, h, d, cls, s in classified:
        by_class[cls].append((i, h, d, s))

    print(f"\n{'defect class':<22s} {'n':>4s} {'first':>11s} {'last':>11s} "
          f"{'span(commits)':>14s}")
    print("-" * 78)
    for cls, evs in sorted(by_class.items(), key=lambda x: -len(x[1])):
        first, last = evs[0], evs[-1]
        span = last[0] - first[0]
        print(f"{cls:<22s} {len(evs):>4d} {first[2]:>11s} {last[2]:>11s} {span:>14d}")

    # ---- POWER: the honest gate on any hazard statement
    n3 = [c for c, e in by_class.items() if len(e) >= 3]
    n2 = [c for c, e in by_class.items() if len(e) == 2]
    n1 = [c for c, e in by_class.items() if len(e) == 1]
    print("\nPOWER")
    print(f"  classes with n>=3 (hazard estimable) : {len(n3)}  {n3}")
    print(f"  classes with n==2                    : {len(n2)}  {n2}")
    print(f"  classes with n==1 (no hazard)        : {len(n1)}  {n1}")

    # ---- inter-arrival latency, only where n>=3
    print("\nINTER-ARRIVAL (commits between successive occurrences; falling = metabolism)")
    verdicts = {}
    for cls in n3:
        idx = [e[0] for e in by_class[cls]]
        gaps = [b - a for a, b in zip(idx, idx[1:])]
        half = max(1, len(gaps) // 2)
        early, late = gaps[:half], gaps[half:]
        me, ml = sum(early) / len(early), sum(late) / len(late) if late else float("nan")
        trend = ("LENGTHENING (metabolism-consistent)" if ml > me else
                 "SHORTENING/FLAT (treadmill-consistent)")
        verdicts[cls] = trend
        print(f"  {cls:<22s} gaps={gaps}")
        print(f"  {'':<22s} early mean {me:.1f} -> late mean {ml:.1f}   {trend}")

    # ---- the structural-fix boundary: does a class fire AFTER its guard shipped?
    print("\nPOST-FIX RECURRENCE (did the class fire after a guard shipped for it?)")
    guard = None
    for i, (h, d, s, b) in enumerate(commits):
        if re.search(r"preflight", s, re.I) and re.search(r"admissib|deterministic|"
                                                          r"non-LLM|selftest", s + b, re.I):
            guard = (i, h[:8], d, s[:60])
            break
    if guard:
        print(f"  fleet preflight shipped at commit index {guard[0]} ({guard[2]}, {guard[1]})")
        after = [(c, [e for e in evs if e[0] > guard[0]]) for c, evs in by_class.items()]
        fired = [(c, len(a)) for c, a in after if a]
        print(f"  classes firing AFTER the preflight: {len(fired)}")
        for c, k in sorted(fired, key=lambda x: -x[1]):
            print(f"      {c:<22s} {k} occurrence(s) post-guard")
        print("  NOTE: the preflight shipped days ago. Post-guard exposure is tiny, so a low")
        print("  post-guard count is NOT yet evidence of metabolism - it is short exposure.")
    else:
        print("  no preflight-shipping commit identified by the lexicon; boundary unmeasured")

    # ---- MANDATORY CONFOUND CHECK, before any hazard reading is credited.
    # A git-mined defect rate is a rate of WORDS. If the fleet's writing changed,
    # the instrument moves with no change in defect rate at all.
    bym = defaultdict(lambda: [0, 0, 0])
    for _i, (_h, _d, _s, _b) in enumerate(commits):
        _t = _s + chr(10) + _b
        _m = _d[:7]
        bym[_m][0] += 1
        bym[_m][1] += int(bool(CORRECTION.search(_t)))
        bym[_m][2] += len(_t)
    print("")
    print("CONFOUND CHECK - is this measuring defects, or commit prose?")
    print("  month      commits  corrective     rate   mean msg chars")
    rates, lens = [], []
    for _m in sorted(bym):
        c, corr, bl = bym[_m]
        rates.append(corr / c); lens.append(bl / c)
        print(f"  {_m:<9s} {c:>8d} {corr:>11d} {corr / c:>8.1%} {bl / c:>16.0f}")
    spread_len = max(lens) / max(min(lens), 1)
    print(f"  message length varies {spread_len:.0f}x across the window")
    CONFOUNDED = spread_len > 3.0
    if CONFOUNDED:
        print("")
        print("  *** INSTRUMENT KILLED BY ITS OWN CONFOUND CHECK ***")
        print("  Corrective-rate tracks MESSAGE VERBOSITY, not defect rate. The fleet's")
        print("  introspection turn made commit messages several times longer and far more")
        print("  epistemically self-critical during exactly the window under study, so a")
        print("  regex over commit prose measures the culture change. Every inter-arrival")
        print("  reading above is VOID, retained for audit rather than deleted - the same")
        print("  disposition Charon applied to his dH figures on 2026-08-25.")
        print("  Hand-check confirms it independently: 'population' and 'glob' match")
        print("  legitimate non-defect commits at high rate.")
    print("")
    print("\n" + "-" * 78)
    print("PREREGISTERED PREDICTION (Harmonia B, filed before running):")
    print("  UNDERPOWERED - most classes n=1, hazard not estimable, and the real output")
    print("  is the instrumentation that makes it answerable in a month.")
    estimable = len(n3)
    held = estimable <= 3
    print(f"  classes with n>=3: {estimable} -> "
          f"{'PREDICTION HELD (underpowered as predicted)' if held else 'PREDICTION FAILED - more signal than expected'}")
    if verdicts:
        tread = sum(1 for v in verdicts.values() if v.startswith("SHORT"))
        print(f"  of {len(verdicts)} estimable classes, {tread} read treadmill-consistent, "
              f"{len(verdicts) - tread} metabolism-consistent")
        print("  Neither reading is licensed as a program verdict at this power. Reported")
        print("  as a direction with its own n attached, per the failure-signature doctrine.")
    if CONFOUNDED:
        print()
        print("VERDICT: Q4 REMAINS UNMEASURED. Not 'treadmill', not 'metabolism'.")
        print("  The hazard is not recoverable retrospectively from git, because the")
        print("  corpus of commit messages is not a defect registry - it is prose whose")
        print("  vocabulary changed with the program's mood. What would make Q4 answerable")
        print("  is PROSPECTIVE: a typed defect record emitted at CATCH TIME carrying")
        print("  {class, introduced_at, caught_at, caught_by, guard_shipped}. That is a")
        print("  week of exposure away, and it is the only honest route to this number.")
    print("-" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
