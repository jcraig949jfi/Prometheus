"""A second reader's one-line changes to gate logic in harness v2 (none of them among the author's 55).
Each is applied to its own copy under scratch; the 59 unit tests are run on the copy."""
import os, pathlib, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "harness"
OUT = HERE / "mut"
ENV = dict(os.environ, RSO_COUNTERFEIT=r"F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit",
           PYTHONDONTWRITEBYTECODE="1")
M = [
 ("F01 G2: design-run lower bound at 50% confidence, not 99%", "stats.py", "DESIGN_CONFIDENCE = 0.99 ", "DESIGN_CONFIDENCE = 0.50 "),
 ("F02 G7.report: zero-hit bound at 50% confidence, not 95%", "stats.py", "def zero_hit_upper(n, conf=0.95):", "def zero_hit_upper(n, conf=0.50):"),
 ("F03 G8: WITHIN shown at level 0.5", "stats.py", "    above = tail_ge(n, k, max(center - margin, 0.0)) <= alpha / 2 ", "    above = tail_ge(n, k, max(center - margin, 0.0)) <= 0.5 "),
 ("F04 G2: design rate used as point estimate, not lower bound", "stats.py", "max(lower_bound(design_hits, design_n), 1e-12)", "max(design_hits / design_n, 1e-12)"),
 ("F05 G1.cell: a table that counts fewer units than seeds registered is accepted", "registration.py", 'if seeds and table["n"] != len(seeds):', 'if seeds and table["n"] > len(seeds):'),
 ("F06 G1.cell: negative exposure counts accepted", "registration.py", 'exposure["tuning_evaluations"] >= 0):', 'exposure["tuning_evaluations"] >= -99):'),
 ("F07 G1.receipt: a run on a subset of the registered seeds is accepted", "registration.py", 'or sorted(receipt["seeds"]) != sorted(cell["registered_seeds"]):', 'or set(receipt["seeds"]) - set(cell["registered_seeds"]):'),
 ("F08 G1.cell: attainability floor 0.99 -> 0.97", "registration.py", "        if p < floor:", "        if p < floor - 0.02:"),
 ("F09 G6.reset: only one earlier cue is tried", "torture.py", "            for earlier in (0, 1):", "            for earlier in (0,):"),
 ("F10 G8: equivalence at alpha 1e-3, not 1e-6", "torture.py", "stats.equivalence(scores[name], n, 0.5, margin, alpha)", "stats.equivalence(scores[name], n, 0.5, margin, alpha * 1000)"),
 ("F11 G9: a conjunct HOLDS at 20 of 24, not 22", "audits.py", "N, HOLDS_AT, FAILS_AT = 24, 22, 12", "N, HOLDS_AT, FAILS_AT = 24, 20, 12"),
 ("F12 G9: a conjunct FAILS at 16 of 24, not 12", "audits.py", "N, HOLDS_AT, FAILS_AT = 24, 22, 12", "N, HOLDS_AT, FAILS_AT = 24, 22, 16"),
 ("F13 G10.setting: a horizon of zero later families accepted", "audits.py", "and not isinstance(v, bool) and v >= 1):", "and not isinstance(v, bool) and v >= 0):"),
 ("F14 G10.setting: only '' and 'tbd' are placeholders", "audits.py", 'PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")', 'PLACEHOLDERS = ("", "tbd")'),
 ("F15 G10.setting: a threshold of zero accepted", "audits.py", "and not isinstance(v, bool) and v > 0):", "and not isinstance(v, bool) and v > -1):"),
 ("F16 G9.clauses: 'the others hold' weakened to 'the others do not fail'", "audits.py", "all(table[d][cell] >= HOLDS_AT for d in names if d != c)", "all(table[d][cell] > FAILS_AT for d in names if d != c)"),
 ("F17 G10.ruler: a ruler with no known positive is accepted", "audits.py", '    if not seen["POSITIVE"]:', "    if False:"),
 ("F18 G12: an ORIGIN claim needs no class bound", "claims.py", '"ORIGIN": ("cold_start", "class_bound"),', '"ORIGIN": ("cold_start",),'),
 ("F19 G12: an ECONOMY claim needs no extra facet", "claims.py", '"ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '"ECONOMY": (),'),
 ("F20 G12: L3 needs nothing beyond L2", "claims.py", 'L3 = ("reproduced",)', "L3 = ()"),
 ("F21 G12: L4 needs nothing beyond L3", "claims.py", 'L4 = ("predicted",)', "L4 = ()"),
 ("F22 G11: any selection_data other than 'confirmation' accepted", "claims.py", 'if record["selection_data"] != "discovery":', 'if record["selection_data"] == "confirmation":'),
 ("F23 G12: a LAW claim needs no registered prediction", "claims.py", '"LAW": ("prediction_registered",),', '"LAW": (),'),
 ("F24 G7.calibration: level 0.002 -> 0.00002", "search.py", "CAL_ALPHA = 0.002 ", "CAL_ALPHA = 0.00002 "),
 ("F25 G7.report: a null with one hit is accepted", "search.py", "        if total:", "        if total > 1:"),
 ("F26 G7.report: a repair claim from a cold start is accepted", "search.py", '        if law != "REPAIR":', "        if False:"),
 ("F27 G0: UNQUALIFIED ranked below INDETERMINATE", "verdict.py", "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}", "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 1, INDETERMINATE: 2, PASS: 0}"),
 ("F28 G3: impostors judged on the first block only", "rulers.py", "        for i, block in enumerate([seeds] + list(blocks)):", "        for i, block in enumerate([seeds]):"),
 ("F29 G5: a shared ruler is judged on the first known physics only", "rulers.py", "        out = judge(known)", "        out = judge(known[:1])"),
 ("F30 G11: identical panels accepted", "claims.py", '    if d["panel_sha256"] == c["panel_sha256"]:', "    if False:"),
 ("F31 G12.promote: a claim of unknown kind is treated as EFFECT", "claims.py", "    need = list(L1) + list(KIND[claim[\"kind\"]])", "    need = list(L1) + list(KIND.get(claim[\"kind\"], ()))"),
 ("F32 G4.entry: an inverted impostor is not refused", "rulers.py", '    if on_impostor == "INVERTED":', '    if False:'),
]

def one(job):
    i, (name, fname, old, new) = job
    d = OUT / ("m%02d" % i)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*.json", "mutation_probe.py"))
    if fname:
        p = d / "rso_harness" / fname
        s = p.read_text(encoding="ascii")
        if s.count(old) != 1:
            return name, "PATTERN_NOT_FOUND(%d)" % s.count(old), ""
        p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True, env=ENV)
    tail = (r.stderr.strip().splitlines() or [""])[-1]
    fails = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
    return name, ("noticed" if r.returncode != 0 else "SURVIVES"), tail + ((" | " + "; ".join(fails[:3])) if fails else "")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    base = one((0, ("unchanged copy", None, None, None)))
    print(base)
    with ThreadPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(one, list(enumerate(M, 1))))
    for n, s, t in res:
        print("%-22s %s   [%s]" % (s, n, t[:150]))
    sv = [n for n, s, _ in res if s == "SURVIVES"]
    print("changes %d, noticed %d, survived %d, pattern not found %d" % (
        len(res), sum(1 for _, s, _ in res if s == "noticed"), len(sv), sum(1 for _, s, _ in res if s.startswith("PATTERN"))))
    shutil.rmtree(OUT, ignore_errors=True)
