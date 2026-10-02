"""Round 3: my own plants against check_hardening.py (third version), run with --no-pins.

Base: plants/base (a copy of the package with the placeholders replaced and PINS filled, so that its
baseline passes; check_review.py in the copy reads git objects through HARDENING_GIT_ROOT).
Each plant gets its own copy. Usage:  python -B p31_plants.py chosen | random
"""
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
SCR = pathlib.Path(r"C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify5")
BASE = SCR / "plants" / "base"
REL = pathlib.Path("docs/phase3/hardening/FABLE-5.1")
D1 = "01_SYNTHESIS_TWO_REVIEWS_AND_HARDENING_v0.2.md"
D2 = "02_HARDENING_DESIGN_v0.2_FABLE.md"
D3 = "03_TEST_HARNESS_SPEC_FABLE.md"
RM, HR, AR = "00_README.md", "harness/README.md", "attack/README.md"
TEXTS = (D1, D2, D3, RM, HR, AR)
ENV = dict(os.environ, HARDENING_GIT_ROOT="F:/Prometheus-worktrees/dionysus-base-role",
           RSO_COUNTERFEIT="F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit")

# (kind, what, file, old, new). Each old must occur exactly once.
CHOSEN = [
    # ---------------- digits (and counts written as words)
    ("digit", "D1 s3: B's cell 'days 31 to 55' -> 45 (second occurrence, in prose)", D1,
     "one cell in days 31 to 55. I deferred", "one cell in days 31 to 45. I deferred"),
    ("digit", "D1 s2: zero-hit bound 0.05 -> 0.50", D1, "1 - 0.05^(1/n)", "1 - 0.50^(1/n)"),
    ("digit", "D1 s3: B stores seven facets -> six", D1, "B stores seven independent", "B stores six independent"),
    ("digit", "D1 s5: run 3 factor 2 -> 3", D1, "no content reset, factor 2)", "no content reset, factor 3)"),
    ("digit", "D1 s9: Gate 15 carries EIGHT builds -> FIVE", D1, "GATE 15 CARRIES EIGHT BUILDS", "GATE 15 CARRIES FIVE BUILDS"),
    ("digit", "D2 s5: six families per life -> eight", D2, "six families per life", "eight families per life"),
    ("digit", "D2 s5: 256 re-indexings -> 128", D2, "trying\nits 256 re-indexings", "trying\nits 128 re-indexings"),
    ("digit", "D2 s15: second author scores tests with 30 changes -> 3", D2, "tests with at least 30 one-line changes",
     "tests with at least 3 one-line changes"),
    ("digit", "D3 s5: fixture rule of 22 -> 20", D3, "24 units and a rule of 22", "24 units and a rule of 20"),
    ("digit", "D3 s5: calibration level 0.002 -> 0.02", D3, "at level\n  0.002, both ways", "at level\n  0.02, both ways"),
    ("digit", "D3 s8: hard-wired formula 16.00 -> 6.00", D3, "one hard-wired formula scores 16.00",
     "one hard-wired formula scores 6.00"),
    ("digit", "AR: first checker fire test 11 of 33 -> 31 of 33", AR, "it reported 11 of 33 planted errors caught",
     "it reported 31 of 33 planted errors caught"),
    # ---------------- words
    ("word", "D1 s1 table: A and B swapped on the boundary row", D1,
     "    boundary       fix it for 90 days            vary it: a 2x2 of",
     "    boundary       vary it for 90 days           fix it: a 2x2 of "),
    ("word", "D1 headline: my repair shown INCOMPLETE -> COMPLETE", D1, "WAS SHOWN INCOMPLETE BY A RUN", "WAS SHOWN COMPLETE BY A RUN"),
    ("word", "D1 s2: evidence mark for B changed from ARGUED to RUN", D1, "RUN (A); ARGUED (B)", "RUN (A); RUN (B)   "),
    ("word", "D1 s3 point 12: 'Nothing that runs tests it' -> 'A gate that runs tests it'", D1,
     "no scalar. Nothing that runs tests it.", "no scalar. A gate that runs tests it."),
    ("word", "D1 s5: 'No positive for the strong claim has been built' -> 'One positive'", D1,
     "No positive for the strong\nclaim has been built", "One positive for the strong\nclaim has been built"),
    ("word", "D1 s6 table: 'from' of resets/observers B -> A", D1, "whole runs compared, with margins by   B",
     "whole runs compared, with margins by   A"),
    ("word", "D1 s8: 'These are not omissions by C' -> 'These are omissions by C'", D1, "These are not omissions by C.",
     "These are omissions by C."),
    ("word", "D2 s3 table: the strong claim FAIL -> PASS at all three settings", D2,
     "    the strong claim                       FAIL at all three settings",
     "    the strong claim                       PASS at all three settings"),
    ("word", "D2 s5: 'this certificate is not a ruler for reuse' -> 'is a ruler'", D2,
     "this certificate is not a ruler for reuse.", "this certificate is a ruler for reuse."),
    ("word", "D2 s12: 'The first five are B's' -> C's (attribution)", D2, "RULES. The first five are B's;", "RULES. The first five are C's;"),
    ("word", "D3 s7: 'They return a part of what that reader found' -> 'all'", D3, "They return a part of what that reader found.",
     "They return all of what that reader found."),
    ("word", "RM: 'simulated and not registered' -> 'simulated and registered'", RM, "simulated and not registered. Document 3 marks each.",
     "simulated and registered. Document 3 marks each."),
    ("word", "HR: 'It qualifies no science' -> 'It qualifies the science'", HR, "It qualifies no science.", "It qualifies the science."),
    ("word", "AR: 'All three readers are of my own model family' -> 'of other model families'", AR,
     "All three readers are of my own model family.", "All three readers are of other model families."),
]


def run_checker(folder, *flags):
    r = subprocess.run([sys.executable, "-B", str(folder / "check_hardening.py"), "--no-fire", "--no-manifests"] + list(flags),
                       capture_output=True, text=True, env=ENV)
    failed = [line[5:110] for line in r.stdout.splitlines() if line.startswith("FAIL")]
    return r.returncode, failed


def mirror(tag):
    root = SCR / "plants" / tag
    if root.exists():
        shutil.rmtree(root)
    shutil.copytree(BASE, root, ignore=shutil.ignore_patterns("__pycache__"))
    return root / REL


def one_chosen(job):
    i, (kind, what, name, old, new) = job
    folder = mirror("c%02d" % i)
    path = folder / name
    s = path.read_text(encoding="ascii")
    if s.count(old) != 1:
        return kind, what, "PATTERN x%d" % s.count(old), []
    path.write_bytes(s.replace(old, new).encode("ascii"))
    rc, failed = run_checker(folder, "--no-pins")
    return kind, what, "caught" if rc else "MISSED", failed


# ---------------------------------------------------------------- mechanical plants
NUMBER = re.compile(r"(?<![A-Za-z0-9.\-/_^(])\d[\d,]*(?:\.\d+)?(?![A-Za-z0-9\-/_]|\.\d)")
VERDICT = re.compile(r"\b(PASS|FAIL|FAILS|BLOCKED|UNQUALIFIED|INDETERMINATE)\b")
SWAP = {"PASS": "FAIL", "FAIL": "PASS", "FAILS": "PASSES", "BLOCKED": "PASS", "UNQUALIFIED": "PASS", "INDETERMINATE": "PASS"}


def candidates():
    """Every standalone number, every ' not ', and every verdict word of the six files, with its position."""
    out = {"digit": [], "negation": [], "verdict": []}
    for name in TEXTS:
        s = (BASE / REL / name).read_text(encoding="ascii")
        offset = 0
        for line in s.split("\n"):
            skip = line.startswith("    python ") or line.startswith("    cd ") or set(line) <= set("-= ") or "sha256" in line
            if not skip:
                for m in NUMBER.finditer(line):
                    if re.match(r"^\s*\d+\.\s", line) and m.start() == len(line) - len(line.lstrip()):
                        continue                                   # list or section numbering
                    out["digit"].append((name, offset + m.start(), m.group(0)))
                for m in re.finditer(r" not ", line):
                    out["negation"].append((name, offset + m.start(), " not "))
                for m in VERDICT.finditer(line):
                    out["verdict"].append((name, offset + m.start(), m.group(0)))
            offset += len(line) + 1
    return out


def altered(kind, token):
    if kind == "digit":
        i = next(k for k, ch in enumerate(token) if ch.isdigit())
        d = int(token[i])
        new = (d + 3) % 10
        if new == 0 and i == 0 and len(token) > 1 and token[1].isdigit():
            new = 7
        if new == d:
            new = (d + 1) % 10
        return token[:i] + str(new) + token[i + 1:]
    if kind == "negation":
        return " "
    return SWAP[token]


def one_random(job):
    i, (kind, name, pos, token) = job
    folder = mirror("r%03d" % i)
    path = folder / name
    s = path.read_text(encoding="ascii")
    assert s[pos:pos + len(token)] == token
    new = altered(kind, token)
    line_start = s.rfind("\n", 0, pos) + 1
    line_end = s.find("\n", pos)
    line = s[line_start:line_end]
    t = s[:pos] + new + s[pos + len(token):]
    path.write_bytes(t.encode("ascii"))
    rc, failed = run_checker(folder, "--no-pins")
    what = "%s:%d  %r -> %r  in: %s" % (name[:14], s.count("\n", 0, pos) + 1, token, new, line.strip()[:70])
    return kind, what, "caught" if rc else "MISSED", failed


def main():
    mode = sys.argv[1]
    rc, failed = run_checker(BASE / REL, "--no-pins")
    print("baseline without pins: rc %d %s" % (rc, failed))
    if rc:
        return 1
    if mode == "chosen":
        jobs = list(enumerate(CHOSEN))
        if len(sys.argv) > 2:
            jobs = [j for j in jobs if j[0] in [int(x) for x in sys.argv[2:]]]
        fn = one_chosen
    else:
        rng = random.Random(20261002)
        cand = candidates()
        print("candidates:", {k: len(v) for k, v in cand.items()})
        picks = []
        for kind, n in (("digit", 40), ("negation", 20), ("verdict", 20)):
            picks += [(kind,) + c for c in rng.sample(cand[kind], n)]
        jobs = list(enumerate(picks))
        fn = one_random
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fn, jobs))
    by = {}
    for kind, what, res, failed in rows:
        print("%-8s %-9s %s%s" % (res, kind, what, ("   [" + failed[0][:70] + "]") if failed else ""))
        k = by.setdefault(kind, [0, 0, 0])
        k[0] += 1
        k[1] += res == "caught"
        k[2] += bool(failed) and failed[0].startswith("form ")
    for kind, (n, c, f) in sorted(by.items()):
        print("   %-9s %2d planted, %2d caught without the pins (%d of them by the form check)" % (kind, n, c, f))
    print("total %d planted, %d caught without the pins" % (len(rows), sum(1 for r in rows if r[2] == "caught")))
    (SCR / ("out_plants_%s.json" % mode)).write_text(json.dumps(
        [{"kind": k, "plant": w, "result": r, "failed": f} for k, w, r, f in rows], indent=1), encoding="ascii")
    return 0


if __name__ == "__main__":
    sys.exit(main())
