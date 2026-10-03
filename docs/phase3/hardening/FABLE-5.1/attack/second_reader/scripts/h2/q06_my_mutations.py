"""A second mutation probe, by someone who did not write the tests: one change per copy; do the 59 tests notice?"""
import os, pathlib, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "harness"
OUT = HERE / "mut"
ENV = dict(os.environ, RSO_COUNTERFEIT=r"F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit")

M = [
    ("V01 G9.arms: one series only if equal in 23 of 24 (was 22)", "audits.py",
     "def coincident(reps, arms, same_at=HOLDS_AT):", "def coincident(reps, arms, same_at=HOLDS_AT + 1):"),
    ("V02 G9.clauses: GOOD_MAX 3.5 -> 4.5 in the run-2 clauses", "audits.py",
     "GOOD_MAX, BAD_MIN = 3.5, 6.0", "GOOD_MAX, BAD_MIN = 4.5, 6.0"),
    ("V03 G9.clauses: slack 2*dev+4 -> 2*dev+8 in the sham and rescue clauses", "audits.py",
     '    slack = 2 * o["dev_B"] + 4', '    slack = 2 * o["dev_B"] + 8'),
    ("V04 G9.clauses: lesion_hurts 2*lesion >= naive -> 3*lesion >= naive", "audits.py",
     '"NESTING.lesion_hurts": 2 * o["lesion_B"] >= o["naive_B"],', '"NESTING.lesion_hurts": 3 * o["lesion_B"] >= o["naive_B"],'),
    ("V05 G9.clauses: a clause counts as able to fail if some cell leaves it undecided (13..21)", "audits.py",
     "    cannot_fail = sorted(c for c in names if min(table[c].values()) > FAILS_AT)",
     "    cannot_fail = sorted(c for c in names if min(table[c].values()) >= HOLDS_AT)"),
    ("V06 G9.clauses: a clause counts as able to hold if some cell leaves it undecided", "audits.py",
     "    cannot_hold = sorted(c for c in names if max(table[c].values()) < HOLDS_AT)",
     "    cannot_hold = sorted(c for c in names if max(table[c].values()) <= FAILS_AT)"),
    ("V07 G9.clauses: isolation needs the other clauses only not to fail", "audits.py",
     "all(table[d][cell] >= HOLDS_AT for d in names if d != c)", "all(table[d][cell] > FAILS_AT for d in names if d != c)"),
    ("V08 G9.sham: a sham clause counts as able to fail if some cell leaves it undecided", "audits.py",
     "    if min(clause_row.values()) > FAILS_AT:", "    if min(clause_row.values()) >= HOLDS_AT:"),
    ("V09 G9.sham: neutral in 12 of 24 replicates is enough (was 22)", "audits.py",
     "    if near >= HOLDS_AT:", "    if near >= FAILS_AT:"),
    ("V10 G10.setting: five placeholders no longer refused (n/a, na, none, unknown, ?)", "audits.py",
     'PLACEHOLDERS = ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?")',
     'PLACEHOLDERS = ("", "tbd", "todo", "not computed")'),
    ("V11 G10.setting: a horizon of zero later families accepted", "audits.py",
     "isinstance(v, int) and not isinstance(v, bool) and v >= 1):", "isinstance(v, int) and not isinstance(v, bool) and v >= 0):"),
    ("V12 G10.setting: the effect threshold is not type-checked", "audits.py",
     '        elif k == "effect_threshold" and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):',
     "        elif False:"),
    ("V13 G10.contrast: one further difference besides the named variable is allowed", "audits.py",
     "    if differ == [named]:", "    if named in differ and len(differ) <= 2:"),
    ("V14 G10.ruler: a mixed v0.1 verdict counts as NEGATIVE", "audits.py",
     '.get(tuple(sorted(answers)), "MIXED")', '.get(tuple(sorted(answers)), "NEGATIVE")'),
    ("V15 G10.ruler: a ruler with no known positive is accepted", "audits.py",
     '    if not seen["POSITIVE"]:', "    if False:"),
    ("V16 G10.ruler: members run only at another setting are ignored", "audits.py",
     "    if elsewhere:", "    if False:"),
    ("V17 G10.ruler: WITHIN_SELECTION_BOUND is read as POSITIVE", "audits.py",
     'return "POSITIVE" if data["verdicts"][key] == "CONSTRUCTED" else "NEGATIVE"',
     'return "POSITIVE" if data["verdicts"][key] in ("CONSTRUCTED", "WITHIN_SELECTION_BOUND") else "NEGATIVE"'),
    ("V18 G10.ruler: an unreadable receipt is UNQUALIFIED, not BLOCKED", "audits.py",
     'found.append(Result(member, BLOCKED, "no readable verdict for %s in %s" % (source[2], source[0])))',
     'found.append(Result(member, UNQUALIFIED, "no readable verdict for %s in %s" % (source[2], source[0])))'),
    ("V19 G11.custody: only the literal word confirmation fails the selection check", "claims.py",
     '    if record["selection_data"] != "discovery":', '    if record["selection_data"] == "confirmation":'),
    ("V20 G11.custody: one generator fails whatever the claim says", "claims.py",
     '    if record["claim"] == "NEW_FAMILY" and d["generator_sha256"] == c["generator_sha256"]:',
     '    if d["generator_sha256"] == c["generator_sha256"]:'),
    ("V21 G11.custody: the generator check is dropped", "claims.py",
     '    if record["claim"] == "NEW_FAMILY" and d["generator_sha256"] == c["generator_sha256"]:',
     "    if False:"),
    ("V22 G11.custody: the discovery side needs no seeds, panel or generator", "claims.py",
     "    if any(not side.get(k) for side in (d, c) for k in part):", "    if any(not side.get(k) for side in (c,) for k in part):"),
    ("V23 G11.custody: booleans count as counts", "claims.py",
     "    return isinstance(v, int) and not isinstance(v, bool) and v >= 0", "    return isinstance(v, int) and v >= 0"),
    ("V24 G12: L4 needs nothing more than L3", "claims.py", 'L4 = ("predicted",)', "L4 = ()"),
    ("V25 G12: L3 needs nothing more than L2 (control: expected to be noticed)", "claims.py", 'L3 = ("reproduced",)', "L3 = ()"),
    ("V26 G12: an ORIGIN claim needs no cold start and no class bound", "claims.py",
     '    "ORIGIN": ("cold_start", "class_bound"),', '    "ORIGIN": (),'),
    ("V27 G12: an ECONOMY claim needs no lifecycle cost and no frozen comparators", "claims.py",
     '    "ECONOMY": ("lifecycle_cost", "frozen_comparators"),', '    "ECONOMY": (),'),
    ("V28 G12: a LAW claim needs no registered prediction", "claims.py",
     '    "LAW": ("prediction_registered",),', '    "LAW": (),'),
    ("V29 G12: a TRANSFER claim needs no new family", "claims.py", '    "TRANSFER": ("new_family",),', '    "TRANSFER": (),'),
    ("V30 G12: a MECHANISM claim needs no intervention (control: expected to be noticed)", "claims.py",
     '    "MECHANISM": ("intervention",),', '    "MECHANISM": (),'),
    ("V31 G12.render: a claim with no setting hash is rendered", "claims.py",
     '    if setting_hash(setting) != claim["setting_sha256"]:', '    if claim.get("setting_sha256") and setting_hash(setting) != claim["setting_sha256"]:'),
    ("V32 G12: a facet may be any object with a verdict attribute missing -> absent facets pass", "claims.py",
     '        return Result(name, BLOCKED, "absent")', '        return Result(name, UNQUALIFIED, "absent")'),
    ("V33 verdict: INDETERMINATE outranks UNQUALIFIED (control: expected to be noticed)", "verdict.py",
     "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 2, INDETERMINATE: 1, PASS: 0}",
     "_RANK = {FAIL: 4, BLOCKED: 3, UNQUALIFIED: 1, INDETERMINATE: 2, PASS: 0}"),
    ("V34 GM: a mutant rejected with the wrong verdict is not reported (control: expected to be noticed)", "meta.py",
     "                      if r.verdict not in (PASS, exp)]", "                      if False]"),
    ("V35 G9.sham: a faster sham counts as neutral (control: expected to be noticed)", "audits.py",
     'abs(o["sham_B"] - o["dev_B"]) <= max(margin * o["dev_B"], slack)', 'o["sham_B"] - o["dev_B"] <= max(margin * o["dev_B"], slack)'),
    ("V36 G10.setting: power may be an integer", "audits.py",
     '        elif k == "power" and not (isinstance(v, float) and 0.99 <= v <= 1.0):',
     '        elif k == "power" and not (isinstance(v, (int, float)) and 0.99 <= v <= 1.0):'),
]


def one(job):
    i, (name, fname, old, new) = job
    d = OUT / ("m%02d" % i)
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns("__pycache__", "RECEIPT_*.json", "mutation_probe.py"))
    p = d / "rso_harness" / fname
    s = p.read_text(encoding="ascii")
    if old and s.count(old) != 1:
        return name, "PATTERN_NOT_FOUND(%d)" % s.count(old)
    if old:
        p.write_text(s.replace(old, new), encoding="ascii", newline="\n")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover"], cwd=str(d), capture_output=True, text=True, env=ENV)
    tail = (r.stderr.strip().splitlines() or [""])[-1]
    return name, ("noticed" if r.returncode != 0 else "SURVIVES") + "  [" + tail[:40] + "]"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(one((0, ("unchanged copy", "audits.py", "", ""))))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(one, list(enumerate(M, 1))))
    for n, s in results:
        print("%-40s %s" % (s, n))
    surv = [n for n, s in results if s.startswith("SURVIVES")]
    print("changes %d, noticed %d, survive %d, pattern not found %d" % (
        len(results), sum(1 for _, s in results if s.startswith("noticed")), len(surv),
        sum(1 for _, s in results if s.startswith("PATTERN"))))
    shutil.rmtree(OUT, ignore_errors=True)
