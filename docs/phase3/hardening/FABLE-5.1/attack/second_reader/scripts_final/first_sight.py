"""FIRST-SIGHT probe of harness v3. Written 2026-10-02 after reading ONLY harness/rso_harness/*.py of version three
(and my own earlier sets F01-F32 and V01-V36, to avoid copying them). tests/test_harness.py and mutation_probe.py of
version three had NOT been opened when this list was written. One change per copy; the unit tests are run on the copy."""
import json
import os
import pathlib
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "harness"
OUT = HERE / "mut"
ENV = dict(os.environ, RSO_COUNTERFEIT="F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit",
           PYTHONDONTWRITEBYTECODE="1")
CRLF_OLD = '    return hashlib.sha256(source.replace(b"\\r\\n", b"\\n")).hexdigest()'
M = [
    # ---- stats.py
    ("S01 stats.upper_bound: the upper end of a design rate at its median, not at 99%", "stats.py",
     "        if tail_le(n, k, mid) < 1 - conf:", "        if tail_le(n, k, mid) < 1 - conf / 2:"),
    ("S02 stats.is_count: a float counts as a count", "stats.py",
     "    return isinstance(v, int) and not isinstance(v, bool) and v >= 0",
     "    return isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0"),
    ("S03 G2: the negative's probability is taken up to the weak positive's critical count even where that is a yes",
     "stats.py",
     "    said_no = 0.0 if no is None else tail_le(n, min(no, k - 1), p0)",
     "    said_no = 0.0 if no is None else tail_le(n, no, p0)"),
    ("S04 G2: power computed one count below the critical count", "stats.py",
     "    power = tail_ge(n, k, p_positive)", "    power = tail_ge(n, k - 1, p_positive)"),
    ("S05 equivalence: the upper margin is not tested", "stats.py",
     "tail_le(n, k, min(center + margin, 1.0))", "tail_le(n, k, 1.0)"),
    ("S06 consistent: each side at alpha, not alpha/2", "stats.py",
     "    return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2",
     "    return tail_ge(n, k, p) > alpha and tail_le(n, k, p) > alpha"),
    ("S07 G2: more design hits than design runs accepted", "stats.py",
     "    if not (is_count(design_n) and design_n > 0 and is_count(design_hits) and design_hits <= design_n):",
     "    if not (is_count(design_n) and design_n > 0 and is_count(design_hits)):"),
    # ---- registration.py
    ("G01 G1.cell: attainability taken at the lower end of the design interval only", "registration.py",
     "                for rate in (stats.lower_bound(h, n), stats.upper_bound(h, n)))",
     "                for rate in (stats.lower_bound(h, n),))"),
    ("G02 G1.cell: more design hits than design units accepted", "registration.py",
     "or not is_count(n) or n == 0 or h > n:", "or not is_count(n) or n == 0:"),
    ("G03 G1.cell: the registration clock is not type-checked", "registration.py",
     '    if cell.get("registered_at") is not None and not is_count(cell["registered_at"]):', "    if False:"),
    ("G04 G1.cell: an empty list or dict counts as a registered field", "registration.py",
     '    missing = [k for k in REQUIRED if cell.get(k) in (None, "", [], {})]',
     '    missing = [k for k in REQUIRED if cell.get(k) in (None, "")]'),
    ("G05 G1.receipt: a receipt need not list its seeds to be checked", "registration.py",
     '    missing = [k for k in ("source_sha256", "seeds", "ran_at") if receipt.get(k) in (None, "", [])]',
     '    missing = [k for k in ("source_sha256", "ran_at") if receipt.get(k) in (None, "", [])]'),
    ("G06 G1.receipt: line endings are not normalised before hashing", "registration.py",
     CRLF_OLD, "    return hashlib.sha256(source).hexdigest()"),
    # ---- verdict.py
    ("V01 G0: UNQUALIFIED outranks BLOCKED", "verdict.py",
     "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}",
     "_RANK = {FAIL: 4, BLOCKED: 2, UNQUALIFIED: 3, INDETERMINATE: 1, PASS: 0}"),
    ("V02 G0: nothing to combine is a PASS", "verdict.py",
     '        return Result(gate, BLOCKED, "no results to combine")',
     '        return Result(gate, PASS, "no results to combine")'),
    ("V03 G0: a sixth verdict is accepted", "verdict.py", "        if verdict not in ALL:", "        if False:"),
    # ---- rulers.py
    ("U01 G3: the registered threshold at 48 is dropped", "rulers.py",
     'EDGES = {51: "POSITIVE", 50: "UNDECIDED", 48: "UNDECIDED", 47: "NEGATIVE", 14: "NEGATIVE", 13: "INVERTED"}',
     'EDGES = {51: "POSITIVE", 50: "UNDECIDED", 47: "NEGATIVE", 14: "NEGATIVE", 13: "INVERTED"}'),
    ("U02 interchange: the state is moved at step 5, not step 3", "rulers.py",
     "def _interchange(make, seeds, grab, put, at=3):", "def _interchange(make, seeds, grab, put, at=5):"),
    ("U03 interchange: an undecided count is called NEGATIVE", "rulers.py",
     '        return "UNDECIDED"', '        return "NEGATIVE"'),
    ("U04 interchange: crossed-inverted with same-follows is called NEGATIVE, not NOT_MOVED", "rulers.py",
     '("INVERTED", "EXCLUDES"): "NOT_MOVED", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}',
     '("INVERTED", "EXCLUDES"): "NEGATIVE", ("EXCLUDES", "INVERTED"): "NOT_MOVED"}'),
    # ---- torture.py
    ("T01 G6.reset: the mark left on the environment is not compared", "torture.py",
     '        return r["answer"], r["trace"], r["final"][0], r["final"][1]',
     '        return r["answer"], r["trace"], r["final"][0]'),
    ("T02 G6.restart: the step right after the cut is not compared", "torture.py",
     '            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],',
     '            if (whole["answer"], whole["trace"][at + 2:], whole["final"]) != (cut["answer"], cut["trace"][at + 2:],'),
    ("T03 G6.restart: no cut after the first step", "torture.py",
     '        for at in range(len(whole["trace"])):', '        for at in range(1, len(whole["trace"])):'),
    ("T04 G6.observer: only the first six seeds are run", "torture.py",
     "        return [w.episode(make(), seed, observer=observer) for seed in seeds]",
     "        return [w.episode(make(), seed, observer=observer) for seed in seeds[:6]]"),
    # ---- search.py
    ("R01 G7.report: founders compared as a set (order and repeats ignored)", "search.py",
     '            if list(p["seeds"]) != list(registered_seeds):', '            if set(p["seeds"]) != set(registered_seeds):'),
    ("R02 G7.report: fewer hits reported than the search had is accepted", "search.py",
     '            if replayed != p["hits"]:', '            if replayed < p["hits"]:'),
    ("R03 G7.report: positive control needed at 0.85, not 0.99", "search.py",
     "                if control < 0.99:", "                if control < 0.85:"),
    ("R04 G7.report: a bound up to 0.005 below what the founders warrant is accepted", "search.py",
     "        elif not zero_hit_upper(n) - 5e-5 <= bound <= 1:", "        elif not zero_hit_upper(n) - 5e-3 <= bound <= 1:"),
    ("R05 G7.calibration: the needle repair cell is dropped from the panel", "search.py",
     'CELLS = (("NEEDLE", "NEUTRAL", "COLD", 0), ("NEEDLE", "NEUTRAL", "REPAIR", 1), ("VALLEY", "NEUTRAL", "REPAIR", 1),',
     'CELLS = (("NEEDLE", "NEUTRAL", "COLD", 0), ("VALLEY", "NEUTRAL", "REPAIR", 1),'),
    ("R06 G7.report: one policy that crosses neutral steps is enough for a null", "search.py",
     '        if len(report["policies"]) < 2 or "CROSSES_NEUTRAL_STEPS" not in kinds:',
     '        if "CROSSES_NEUTRAL_STEPS" not in kinds:'),
    # ---- audits.py
    ("A01 G9.arms: with fewer than 22 replicates no two arms are ever one series", "audits.py",
     ">= min(same_at, len(reps)):", ">= same_at:"),
    ("A02 G9.arms: two arms with one series are tolerated; three are not", "audits.py",
     "    merged = [g for g in groups if len(g) > 1]", "    merged = [g for g in groups if len(g) > 2]"),
    ("A03 G9.clauses: run 3 audited at factor 3, not its registered 2", "audits.py",
     "def clauses_run3(o, factor=2):", "def clauses_run3(o, factor=3):"),
    ("A04 G10.setting: placeholders are matched case-sensitively", "audits.py",
     "v.strip().lower() in PLACEHOLDERS", "v.strip() in PLACEHOLDERS"),
    ("A05 G10.setting: power has no upper limit", "audits.py",
     "(_number(v) and 0.99 <= v <= 1.0)", "(_number(v) and 0.99 <= v)"),
    ("A06 G10.setting: the horizon need not be a whole number", "audits.py",
     "(_number(v) and v == int(v) and v >= 1)", "(_number(v) and v >= 1)"),
    ("A07 G10.contrast: a field written in one cell only is not a difference", "audits.py",
     "    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))",
     "    differ = sorted(k for k in set(a) & set(b) if a.get(k) != b.get(k))"),
    ("A08 G10.ruler: a cell verdict other than PASS or FAIL is read as NEGATIVE", "audits.py",
     '            return {"PASS": "POSITIVE", "FAIL": "NEGATIVE"}[data["cells"][key]["verdict"]]',
     '            return {"PASS": "POSITIVE", "FAIL": "NEGATIVE"}.get(data["cells"][key]["verdict"], "NEGATIVE")'),
    ("A09 G10.ruler: RULER_NOT_APPLICABLE is no longer a guard", "audits.py",
     'GUARDS = ("INHERITED_OR_LEAK", "RULER_NOT_APPLICABLE")', 'GUARDS = ("INHERITED_OR_LEAK",)'),
    ("A10 G10.ruler: a member run here and also elsewhere is reported as not run here", "audits.py",
     "    elsewhere = sorted({r[0] for r in runs if claim in r[3] and r[1] != setting} - {r[0] for r in here})",
     "    elsewhere = sorted({r[0] for r in runs if claim in r[3] and r[1] != setting})"),
    # ---- claims.py
    ("C01 G11: the opening clock is not type-checked", "claims.py",
     '            and is_count(record["rule_fixed_at"]) and is_count(record["confirmation_opened_at"])):',
     '            and is_count(record["rule_fixed_at"])):'),
    ("C02 G11: a side needs no generator hash", "claims.py",
     '    part = ("seeds", "panel_sha256", "generator_sha256")', '    part = ("seeds", "panel_sha256")'),
    ("C03 G12.render: the setting hash depends on key order", "claims.py",
     "json.dumps(setting, sort_keys=True)", "json.dumps(setting, sort_keys=False)"),
    ("C04 G11: an empty string counts as a custody field", "claims.py",
     '    missing = [k for k in CUSTODY_FIELDS if record.get(k) in (None, "")]',
     "    missing = [k for k in CUSTODY_FIELDS if record.get(k) is None]"),
    # ---- ladder.py
    ("L01 ladder: certificate at alpha 0.01, not 1e-6", "ladder.py",
     "def certificate(per_life, alpha=1e-6):", "def certificate(per_life, alpha=1e-2):"),
    ("L02 ladder: the control is ignored when the ninth pair is CARRIED", "ladder.py",
     '    if control["answer"] == "CARRIED":', '    if control["answer"] == "CARRIED" and full["answer"] != "CARRIED":'),
    ("L03 ladder: in the control the ninth pair too comes from the other key", "ladder.py",
     "            bases, moves = other if (control and (j, k) != UNSEEN) else own",
     "            bases, moves = other if control else own"),
    # ---- retain1.py
    ("W01 score: a fresh world for every seed", "retain1.py",
     "(w.episode(make(), s)))", "(World(**world).episode(make(), s)))"),
    ("W02 world: the final state does not hold the mark", "retain1.py",
     '                "final": (org.native(), self.mark, self.draws, self.episodes)}',
     '                "final": (org.native(), None, self.draws, self.episodes)}'),
    ("W03 world: the trajectory does not hold the value delivered", "retain1.py",
     "            trace.append((obs.kind, obs.value, obs.clock, obs.mark, after_step, org.native()))",
     "            trace.append((obs.kind, None, obs.clock, obs.mark, after_step, org.native()))"),
    # ---- meta.py
    ("M01 GM: a mutant that passes is not an escape", "meta.py",
     "        escapes = [name for name, r, _ in mutant_results if r.verdict == PASS]",
     "        escapes = [name for name, r, _ in mutant_results if r.verdict == PASS and False]"),
    ("M02 GM: a sound case refused as BLOCKED, UNQUALIFIED or INDETERMINATE is no false accusation", "meta.py",
     "        false_alarms = [r.reason or r.verdict for r in clean_results if r.verdict != PASS]",
     "        false_alarms = [r.reason or r.verdict for r in clean_results if r.verdict == FAIL]"),
    ("M03 GM: the missing-field mutant tries the first eight fields only", "meta.py",
     "    open_ = [f for f in fields if check(make(**{f: None})).verdict != BLOCKED]",
     "    open_ = [f for f in fields[:8] if check(make(**{f: None})).verdict != BLOCKED]"),
    ("M04 GM: the kind-facet mutant tries the first three kinds only", "meta.py",
     '    open_ = ["%s.%s" % (k, f) for k, fs in sorted(KIND_FACETS.items()) for f in fs',
     '    open_ = ["%s.%s" % (k, f) for k, fs in sorted(KIND_FACETS.items())[:3] for f in fs'),
]


def one(job):
    i, (name, fname, old, new) = job
    d = OUT / ("m%02d" % i)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns("__pycache__"))
    if fname:
        p = d / "rso_harness" / fname
        s = p.read_text(encoding="ascii")
        if s.count(old) != 1:
            shutil.rmtree(d, ignore_errors=True)
            return name, "PATTERN_NOT_FOUND(%d)" % s.count(old), ""
        p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True,
                       env=ENV)
    lines = r.stderr.strip().splitlines()
    tail = lines[-1] if lines else ""
    ran = next((ln for ln in lines if ln.startswith("Ran ")), "")
    fails = [ln.split(" ")[1] for ln in lines if ln.startswith(("FAIL:", "ERROR:"))]
    shutil.rmtree(d, ignore_errors=True)
    return name, ("noticed" if r.returncode != 0 else "SURVIVES"), "%s | %s | %s" % (ran, tail, ", ".join(fails[:4]))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    base = one((0, ("unchanged copy", None, None, None)))
    print(base)
    if base[1] != "SURVIVES":
        sys.exit("the unchanged copy does not pass its own tests")
    with ThreadPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(one, list(enumerate(M, 1))))
    for n, s, t in res:
        print("%-22s %s   [%s]" % (s, n, t[:170]))
    sv = [n for n, s, _ in res if s == "SURVIVES"]
    print("changes %d, noticed %d, unnoticed %d, pattern not found %d" % (
        len(res), sum(1 for _, s, _ in res if s == "noticed"), len(sv), sum(1 for _, s, _ in res if s.startswith("PATTERN"))))
    (HERE / "first_sight_result.json").write_text(
        json.dumps([{"change": n, "result": s, "detail": t} for n, s, t in res], indent=1), encoding="ascii")
    shutil.rmtree(OUT, ignore_errors=True)
