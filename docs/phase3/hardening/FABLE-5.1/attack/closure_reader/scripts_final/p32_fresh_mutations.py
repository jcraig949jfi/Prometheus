"""Round 3: fresh one-line changes to the gates of the THIRD version. Do its 103 tests notice?

Written after reading the gate code and the first half of the test file (to line 470), and before
running any of them. None is among the 167 changes of mutation_probe.py.
"""
import os
import pathlib
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "mirror" / "root" / "docs" / "phase3" / "hardening" / "FABLE-5.1" / "harness"
OUT = HERE / "mut2"
ENV = dict(os.environ, RSO_COUNTERFEIT=r"F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit")

M = [
    ("W01 G3: the impostor blocks may repeat the first block of seeds (only the further blocks are compared)", "rulers.py",
     "    every = [s for block in [seeds] + list(blocks) for s in block]",
     "    every = [s for block in list(blocks) for s in block]"),
    ("W02 G5: a physics with no known answer counts toward the three a shared ruler needs", "rulers.py",
     "        if len(known) < MIN_PHYSICS:", "        if len(table) < MIN_PHYSICS:"),
    ("W03 G6.restart: the first step after the cut is not compared", "torture.py",
     '            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],',
     '            if (whole["answer"], whole["trace"][at + 2:], whole["final"]) != (cut["answer"], cut["trace"][at + 2:],'),
    ("W04 G8: the clock table sees two bits of the clock, not three", "torture.py",
     '"CLOCK": (probe[1] & 7,)', '"CLOCK": (probe[1] & 3,)'),
    ("W05 G7.report: a stated bound above 1 is accepted", "search.py",
     "        elif not zero_hit_upper(n) - 5e-5 <= bound <= 1:", "        elif not zero_hit_upper(n) - 5e-5 <= bound:"),
    ("W06 G7.calibration: the panel loses its fifth cell (VALLEY, strict, cold)", "search.py",
     '         ("ASCENT", "STRICT", "COLD", 0), ("VALLEY", "STRICT", "COLD", 0))',
     '         ("ASCENT", "STRICT", "COLD", 0))'),
    ("W07 G10.setting: placeholders are refused in lower case only", "audits.py",
     "        if v is None or (isinstance(v, str) and v.strip().lower() in PLACEHOLDERS):",
     "        if v is None or (isinstance(v, str) and v.strip() in PLACEHOLDERS):"),
    ("W08 G10.setting: a power above 1 is accepted", "audits.py", "0.99 <= v <= 1.0", "0.99 <= v"),
    ("W09 G10.setting: true and false count as numbers", "audits.py",
     "    return isinstance(v, (int, float)) and not isinstance(v, bool)", "    return isinstance(v, (int, float))"),
    ("W10 G10.contrast: a field written down in one cell only is not compared", "audits.py",
     "    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))",
     "    differ = sorted(k for k in set(a) & set(b) if a.get(k) != b.get(k))"),
    ("W11 G9.arms: two arms with one series are allowed; three are not", "audits.py",
     "    merged = [g for g in groups if len(g) > 1]", "    merged = [g for g in groups if len(g) > 2]"),
    ("W12 G12.render: the setting hash depends on the order the choices were typed in", "claims.py",
     '    return hashlib.sha256(json.dumps(setting, sort_keys=True).encode("ascii")).hexdigest()',
     '    return hashlib.sha256(json.dumps(setting, sort_keys=False).encode("ascii")).hexdigest()'),
    ("W13 G2: a bound of exactly 0 or 1 is accepted", "stats.py",
     "    if not (is_count(n) and n > 0 and 0 < p0 < 1 and 0 < alpha < 1 and 0 < p_positive <= 1):",
     "    if not (is_count(n) and n > 0 and 0 <= p0 <= 1 and 0 < alpha < 1 and 0 < p_positive <= 1):"),
    ("W14 G8: the upper side of the equivalence test is run at alpha, not alpha/2", "stats.py",
     "    below = tail_le(n, k, min(center + margin, 1.0)) <= alpha / 2 ",
     "    below = tail_le(n, k, min(center + margin, 1.0)) <= alpha "),
    ("W16 interchange: 'carried somewhere that was not moved' is reported as NEGATIVE", "rulers.py",
     '            ("INVERTED", "EXCLUDES"): "NOT_MOVED", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}.get((a, b), "NEGATIVE")',
     '            ("INVERTED", "EXCLUDES"): "NEGATIVE", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}.get((a, b), "NEGATIVE")'),
    ("W18 ladder: the control arm is ignored when the two arms are read together", "ladder.py",
     '    if control["answer"] == "CARRIED":', "    if False:"),
    ("W19 G12: level() never reports L4", "claims.py", "    for lv in (1, 2, 3, 4):", "    for lv in (1, 2, 3):"),
    ("W20 ladder: the Hoeffding margin with n in place of 2n", "ladder.py",
     "    threshold = H16 + N * sqrt(log(1 / alpha) / (2 * n))", "    threshold = H16 + N * sqrt(log(1 / alpha) / n)"),
    ("W21 G3: an empty panel is not refused", "rulers.py",
     "    if not panel or any(pos is None or imp is None for pos, imp in panel.values()):",
     "    if any(pos is None or imp is None for pos, imp in panel.values()):"),
    ("W22 G10.setting: the wrong-history choice is no longer one of the nine", "audits.py",
     'SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "wrong_history", "effect_threshold",',
     'SETTING = ("cost", "later_families", "content_reset", "sham", "family_A", "effect_threshold",'),
    ("W23 G7.report: the founders are compared as sets, so a founder may be reported twice", "search.py",
     '        if list(p["seeds"]) != list(registered_seeds):', '        if set(p["seeds"]) != set(registered_seeds):'),
    ("W24 G11: a discovery and a confirmation may share their panel if their seeds differ", "claims.py",
     '    if d["panel_sha256"] == c["panel_sha256"]:',
     '    if d["panel_sha256"] == c["panel_sha256"] and set(d["seeds"]) & set(c["seeds"]):'),
    ("W26 G9.clauses: a clause is isolated if the others hold in 21 of 24", "audits.py",
     "        table[c][cell] <= FAILS_AT and all(table[d][cell] >= HOLDS_AT for d in names if d != c) for cell in cell_names))",
     "        table[c][cell] <= FAILS_AT and all(table[d][cell] >= HOLDS_AT - 1 for d in names if d != c) for cell in cell_names))"),
    ("W28 G4.entry: the impostor is judged on the first 48 seeds", "rulers.py",
     "    on_positive, on_impostor = exclusion_ruler(pair[0], seeds), exclusion_ruler(pair[1], seeds)",
     "    on_positive, on_impostor = exclusion_ruler(pair[0], seeds), exclusion_ruler(pair[1], seeds[:48])"),
    ("W27 G6.reset: the earlier episode is run on the same seed as the later one", "torture.py",
     "                episode(w, org, seed, earlier)", "                episode(w, org, seed + 1, earlier)"),
    ("W29 G1.cell: the highest count of a verdict table is not checked", "registration.py",
     "    for count in range(n + 1):\n        got = [o for lo, hi, o in rule if lo <= count <= hi]",
     "    for count in range(n):\n        got = [o for lo, hi, o in rule if lo <= count <= hi]"),
]


def one(job):
    i, (name, fname, old, new) = job
    d = OUT / ("w%02d" % i)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*.json", "mutation_probe.py"))
    p = d / "rso_harness" / fname
    s = p.read_text(encoding="ascii")
    if s.count(old) != 1:
        return name, "PATTERN x%d" % s.count(old), ""
    p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True, env=ENV)
    tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
    return name, "noticed" if r.returncode != 0 else "SURVIVES", tail[:30]


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(one, list(enumerate(M, 1))))
    for name, res, tail in results:
        print("%-10s %-22s %s" % (res, tail, name))
    surv = [n for n, r, _ in results if r == "SURVIVES"]
    bad = [n for n, r, _ in results if r.startswith("PATTERN")]
    print("\n%d changes; %d noticed; %d SURVIVE; %d pattern problems" % (
        len(results), sum(1 for _, r, _ in results if r == "noticed"), len(surv), len(bad)))
    for n in surv:
        print("   -", n)
