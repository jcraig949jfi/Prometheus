"""The reader's own one-line logic changes against the SECOND version of the harness. Do the 59 tests notice?"""
import os
import pathlib
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "mirror" / "root" / "docs" / "phase3" / "hardening" / "FABLE-5.1" / "harness"
OUT = HERE / "mut"
ENV = dict(os.environ, RSO_COUNTERFEIT=r"F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit")

M = [
    # ---- stats.py
    ("V01 classify: a score AT the lower critical count is no longer INVERTED", "stats.py",
     "        if low is not None and successes <= low:", "        if low is not None and successes < low:"),
    ("V02 equivalence: WITHIN needs only one of the two one-sided tests", "stats.py",
     '    return "WITHIN" if above and below else "UNDECIDED"', '    return "WITHIN" if above or below else "UNDECIDED"'),
    ("V03 calibration test at alpha, not alpha/2 per side", "stats.py",
     "    return tail_ge(n, k, p) > alpha / 2 and tail_le(n, k, p) > alpha / 2",
     "    return tail_ge(n, k, p) > alpha and tail_le(n, k, p) > alpha"),
    ("V04 design rates used at a 90% lower bound, not 99%", "stats.py", "DESIGN_CONFIDENCE = 0.99 ", "DESIGN_CONFIDENCE = 0.90 "),
    # ---- registration.py
    ("V05 G1.cell: a rate given as True/False is accepted", "registration.py",
     'if outcome not in table["outcomes"] or isinstance(rate, bool) or not isinstance(rate, (int, float)) \\',
     'if outcome not in table["outcomes"] or not isinstance(rate, (int, float)) \\'),
    ("V06 G1.cell: a negative count of tuning evaluations is accepted", "registration.py",
     'and not isinstance(exposure["tuning_evaluations"], bool) and exposure["tuning_evaluations"] >= 0):',
     'and not isinstance(exposure["tuning_evaluations"], bool)):'),
    ("V07 G1.receipt: a receipt need not carry the time it ran", "registration.py",
     'missing = [k for k in ("source_sha256", "seeds", "ran_at") if receipt.get(k) in (None, "", [])]',
     'missing = [k for k in ("source_sha256", "seeds") if receipt.get(k) in (None, "", [])]'),
    ("V08 G1.cell: attainability is not computed when two known answers are given as one pair of equal outcomes "
     "(the yes-and-no requirement dropped to one)", "registration.py",
     "    if not isinstance(known_answers, dict) or len(known_answers) < 2:",
     "    if not isinstance(known_answers, dict) or len(known_answers) < 1:"),
    # ---- rulers.py
    ("V09 G4.entry: the preflight is not run", "rulers.py", "    if pre.verdict != PASS:", "    if False:"),
    ("V10 G5: a ruler declared valid nowhere is not blocked", "rulers.py", "    if not declared:", "    if False:"),
    ("V11 interchange: the state is moved at step 5, not 3", "rulers.py",
     "def _interchange(make, seeds, grab, put, at=3):", "def _interchange(make, seeds, grab, put, at=5):"),
    ("V12 G3: impostors are judged on the first further block only", "rulers.py",
     "        for i, block in enumerate([seeds] + list(blocks)):", "        for i, block in enumerate([seeds] + list(blocks)[:1]):"),
    ("V13 G5: a shared ruler is judged on the first three physics of the panel", "rulers.py",
     "        out = judge(known)", "        out = judge(known[:3])"),
    ("V14 G4.entry: an impostor that beats the bound is INDETERMINATE, not FAIL", "rulers.py",
     '        found.append(Result("impostor", FAIL, "the impostor beats the exact bound: it is no impostor, or the world leaks"))',
     '        found.append(Result("impostor", INDETERMINATE, "the impostor beats the exact bound"))'),
    # ---- torture.py
    ("V15 G6.observer: only the first seed is checked", "torture.py",
     '    for seed in seeds:\n        off = World().episode(make(), seed)', '    for seed in seeds[:1]:\n        off = World().episode(make(), seed)'),
    ("V16 G6.reset: only the first seed is checked", "torture.py",
     "    for seed in seeds:\n        for cue in (None, 0, 1):", "    for seed in seeds[:1]:\n        for cue in (None, 0, 1):"),
    ("V17 G6.restart: only the first seed is checked", "torture.py",
     "    for seed in seeds:\n        whole = World().episode(make(), seed)", "    for seed in seeds[:1]:\n        whole = World().episode(make(), seed)"),
    ("V18 G6.reset: the mark left on the environment is not compared", "torture.py",
     'return r["answer"], r["trace"], r["final"][0], r["final"][1]', 'return r["answer"], r["trace"], r["final"][0]'),
    ("V19 G6.restart: the last cut point is not tried", "torture.py",
     '        for at in range(len(whole["trace"]) - 1):', '        for at in range(len(whole["trace"]) - 2):'),
    ("V20 G8.demand: alpha 1e-6 -> 1e-3", "torture.py",
     "def demand_closure(seeds, train_seeds, baselines=None, alpha=1e-6, margin=MARGIN, **world):",
     "def demand_closure(seeds, train_seeds, baselines=None, alpha=1e-3, margin=MARGIN, **world):"),
    ("V21 G8.demand: an UNDECIDED baseline does not stop a PASS", "torture.py", "    if open_:", "    if False:"),
    # ---- search.py
    ("V22 G7.report: a report with missing fields is not blocked", "search.py", "    if missing:", "    if False:"),
    ("V23 G7.report: a policy with no founders at all is accepted", "search.py",
     'if len(set(p["seeds"])) != len(p["seeds"]) or not p["seeds"]:', 'if len(set(p["seeds"])) != len(p["seeds"]):'),
    ("V24 G7.report: the positive control need only reach 0.5", "search.py", "        if control < 0.99:", "        if control < 0.5:"),
    ("V25 G7.report: a repair claim needs no repair start", "search.py", '        if law != "REPAIR":', "        if False:"),
    ("V26 G7.report: the bound is held to the LARGEST founder count among the policies", "search.py",
     '        n = min(len(p["seeds"]) for p in report["policies"].values()) or 1',
     '        n = max(len(p["seeds"]) for p in report["policies"].values()) or 1'),
    ("V27 G7.report: an unknown claim passes", "search.py",
     '        return Result(gate, BLOCKED, "unknown claim %r" % (claim,))', '        return Result(gate, PASS, "unknown claim %r" % (claim,))'),
    ("V28 G7.report: an unregistered landscape is not blocked", "search.py",
     '    if unknown or report["landscape"] not in LANDSCAPES:', "    if unknown:"),
    # ---- audits.py
    ("V29 G9.clauses: a clause true in exactly 12 of 24 somewhere counts as unable to fail", "audits.py",
     "    cannot_fail = sorted(c for c in names if min(table[c].values()) > FAILS_AT)",
     "    cannot_fail = sorted(c for c in names if min(table[c].values()) >= FAILS_AT)"),
    ("V30 G10.setting: the amortization horizon need not be a count", "audits.py",
     '        elif k == "amortization_horizon" and not (isinstance(v, int) and not isinstance(v, bool) and v >= 1):',
     '        elif False:'),
    ("V31 G10.setting: the effect threshold need not be a number", "audits.py",
     '        elif k == "effect_threshold" and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):',
     '        elif False:'),
    ("V32 G10.ruler: a ruler with no known positive is accepted", "audits.py", '    if not seen["POSITIVE"]:', "    if False:"),
    ("V33 G10.setting: 'n/a' and 'unknown' count as registered", "audits.py",
     'PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")', 'PLACEHOLDERS = ("", "tbd")'),
    ("V34 G9.sham: a sham clause that fails nowhere is not UNQUALIFIED unless it holds in every replicate of every cell",
     "audits.py", "    if min(clause_row.values()) > FAILS_AT:", "    if min(clause_row.values()) >= N:"),
    # ---- claims.py
    ("V35 G11: a confirmation from the same generator is refused whatever the claim", "claims.py",
     '    if record["claim"] == "NEW_FAMILY" and d["generator_sha256"] == c["generator_sha256"]:',
     '    if d["generator_sha256"] == c["generator_sha256"]:'),
    ("V36 G12: a level may be skipped (L3 without L2)", "claims.py",
     "            best = lv\n        else:\n            break", "            best = lv\n        else:\n            continue"),
    ("V37 G12: an ORIGIN claim needs no cold start and no class bound", "claims.py",
     '    "ORIGIN": ("cold_start", "class_bound"),', '    "ORIGIN": (),'),
    ("V38 G12: a TRANSFER claim needs no new family", "claims.py", '    "TRANSFER": ("new_family",),', '    "TRANSFER": (),'),
    ("V39 G12: L1 no longer needs the resources facet", "claims.py",
     'L1 = ("registration", "power", "detection", "demand", "independence", "exposure", "resources")',
     'L1 = ("registration", "power", "detection", "demand", "independence", "exposure")'),
    ("V40 G12: L2 no longer needs an attack round", "claims.py",
     'L2 = ("exact_null", "attack_round", "custody", "second_implementation")',
     'L2 = ("exact_null", "custody", "second_implementation")'),
    ("V41 G12: an ECONOMY claim needs no frozen comparators", "claims.py",
     '    "ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '    "ECONOMY": ("lifecycle_cost",),'),
    ("V42 G11: a boolean counts as a clock reading or a count", "claims.py",
     "    return isinstance(v, int) and not isinstance(v, bool) and v >= 0", "    return isinstance(v, int) and v >= 0"),
    # ---- verdict.py, ladder.py
    ("V43 combine: nothing checked is PASS, not BLOCKED", "verdict.py",
     '        return Result(gate, BLOCKED, "no results to combine")', '        return Result(gate, PASS, "no results to combine")'),
    ("V44 ladder: the certificate's alpha 1e-6 -> 1e-2", "ladder.py",
     "def certificate(per_life, alpha=1e-6):", "def certificate(per_life, alpha=1e-2):"),
]


def one(job):
    i, (name, fname, old, new) = job
    d = OUT / ("v%02d" % i)
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
    print("\n%d changes; %d noticed; %d SURVIVE; %d pattern problems" % (len(results), sum(1 for _, r, _ in results if r == "noticed"), len(surv), len(bad)))
    for n in surv:
        print("   -", n)
