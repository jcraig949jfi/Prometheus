"""C-018-T030 RED rows: every decision line of the evaluator / completeness wrapper / non-ancestor rule has a behavioural test
that turns RED on its mutant (C-016-T041 lesson 3: a hash guard is not a behavioural pin; the suite has no freeze-hash test,
so every kill below is behavioural). Each edit is applied IN PLACE, the suite runs in a fresh `python -B` subprocess (caches
purged), the source is restored byte for byte and its sha256 re-checked. Baseline first, unedited.

    python -m rso.aether.red.run_red rso/aether/red/red_rows.jsonl

v1.1.0 (C-018-T041): rows 0-20 are the C-018-T030 rows (three retargeted to the v1.1.0 lines that replaced theirs: 12 p2,
14 need, 19 the N choice); rows 21+ pin the repair round; rows 47-50 pin s10.6 (per-unit tree replay); then Pallas's challenge/edits.json E1-E5 are applied VERBATIM
(`old` -> `new`, in the file named there). Edits are matched line-ending agnostically (Pallas S2: on a CRLF checkout four
T030 rows were EDIT_NOT_UNIQUE): a newline in an edit is rewritten to the file's own line ending before matching.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

from rso.registry.registry import ROOT

SUITE = [sys.executable, "-B", "-m", "unittest", "rso.aether.tests.test_adapter"]
EDITS = [
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.7, 0.2, 3"),
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.3, 3"),
    ("evaluate.py", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 3", "REMOVED_MIN, NONANC_MAX, TARGETS_MIN = 0.8, 0.2, 2"),
    ("evaluate.py", "MARGIN, NULL_MAX = 0.05, 0.03", "MARGIN, NULL_MAX = 0.07, 0.03"),
    ("evaluate.py", "    if t0_sites(a) != [O]:\n", "    if len(t0_sites(a)) > 7:\n"),
    ("evaluate.py", "vac = N is None or imp[N] < 0", "vac = N is None"),
    ("evaluate.py", "tg = [s for s in targets if imp[s] >= 0]", "tg = list(targets)"),
    ("evaluate.py", "return bool((d <= ft[idx]).all())", "return bool((d <= ft[idx] + 10).all())"),
    ("evaluate.py", "    if set(tree[\"site\"]) != obs:\n", "    if False:\n"),
    ("evaluate.py", "    if B != meta[\"B\"]:\n", "    if False:\n"),
    ("evaluate.py", "return B, A.choose_nonancestor(tree, B, meta[\"origin\"], meta[\"n\"]), sorted(TR.descendants(tree, B))",
     "return B, meta[\"N\"], sorted(TR.descendants(tree, B))"),
    ("evaluate.py", "return [] if meta.get(\"arrays_sha256\") == A.arrays_sha256(a) else", "return [] if True else"),
    ("evaluate.py", "p2 = L[\"confirmed_r2\"] >= need(L[\"evaluable\"])", "p2 = L[\"confirmed_r2\"] >= 3"),
    ("evaluate.py", "if L[\"null_excess\"] is None or abs(L[\"null_excess\"]) >= NULL_MAX:", "if L[\"null_excess\"] is None:"),
    ("evaluate.py", "return max(3, math.ceil(0.1 * n_evaluable))", "return max(2, math.ceil(0.1 * n_evaluable))"),
    ("evaluate.py", "[:, 1:min(band, 6)] - 0.125)", "[:, 1:6] - 0.125)"),
    ("confirm.py", "(pinned_design_sha256 is not None and design[\"manifest_sha256\"] != pinned_design_sha256)", "False"),
    ("confirm.py", "presented, sources=sources, native_digest=M.digest)", "presented, sources=sources, native_digest=None)"),
    ("adapter.py", "if g >= 1 and s != B", "if g >= -1 and s != B"),
    ("adapter.py", "return ok[0][2] if ok else None", "return ok[-1][2] if ok else None"),
    ("adapter.py", "                    nx[f][y, x] = nc[f][y, x]\n", "                    pass\n"),
    # ---- v1.1.0 (C-018-T041) repair-round pins, rows 21+
    ("adapter.py", "if lo <= c[1] and (hi is None or c[1] < hi)", "if (hi is None or c[1] < hi)"),                 # B8
    ("adapter.py", "if lo <= c[1] and (hi is None or c[1] < hi)", "if lo <= c[1] and (hi is None or c[1] <= hi)"),  # B4
    ("adapter.py", "if lo <= c[1] and (hi is None or c[1] < hi)", "if lo <= c[1]"),                                # B4
    ("evaluate.py", "    elif out[\"removed_B\"] < REMOVED_MIN:\n", "    elif out[\"removed_B\"] < REMOVED_MIN and not vac:\n"),
    ("evaluate.py", "    bad += tree_invariants(tree, meta[\"n\"])\n", "    bad += []\n"),                           # B1
    ("evaluate.py", "bad[\"parent not 4-adjacent\"] += dy + dx != 1", "bad[\"parent not 4-adjacent\"] += 0"),
    ("evaluate.py", "bad[\"parent not earlier\"] += not ft[p] < ft[s]", "bad[\"parent not earlier\"] += 0"),
    ("evaluate.py", "bad[\"gen != parent gen + 1\"] += gen[s] != gen[p] + 1", "bad[\"gen != parent gen + 1\"] += 0"),
    ("evaluate.py", "        if p not in par:\n", "        if False:\n"),
    ("evaluate.py", "not (f[meta[\"origin\"]] == 0 and f[site] < 0)", "not (f[site] < 0)"),
    ("evaluate.py", "not (f[meta[\"origin\"]] == 0 and f[site] < 0)", "not (f[meta[\"origin\"]] == 0)"),
    ("evaluate.py", "EVALUABLE_MIN = 8 ", "EVALUABLE_MIN = 7 "),                                                   # B2
    ("evaluate.py", "    if L[\"evaluable\"] < EVALUABLE_MIN:\n", "    if False:\n"),
    ("evaluate.py", "    need_ = need(evaluable(rows))\n", "    need_ = need(len(rows))\n"),
    ("evaluate.py", "p2 = L[\"confirmed_r2\"] >= need(L[\"evaluable\"])", "p2 = L[\"confirmed_r2\"] >= need(L[\"n_units\"])"),
    ("evaluate.py", "acc[r[\"seed\"]] for r in conf", "acc[r[\"seed\"]] for r in rows"),                          # B3
    ("evaluate.py", "\"after_300\": sum(1 for t in ticks if t > 300)", "\"after_300\": sum(1 for t in ticks if t > 200)"),  # B7
    ("evaluate.py", "and r[\"ftick_N\"] < r[\"ftick_B\"]", "and r[\"ftick_N\"] <= r[\"ftick_B\"]"),
    ("evaluate.py", "\"%s [evaluable %d of %d units;", "\"%s [%d of %d units;"),
    ("confirm.py", "    bad = (freeze_check or freeze.mismatches)()", "    bad = []"),                              # B6
    ("confirm.py", "    if len(set(shas)) != len(shas):", "    if False:"),                                          # B5
    ("confirm.py", "            why = snapshot_problem(law, row[\"seed\"], meta, arrays, snapshot)", "            why = None"),
    ("confirm.py", "and A.P.digest(s) == meta[\"aether\"][\"warm_digest\"])", ")"),
    ("confirm.py", "            if meta.get(\"seed\") != row[\"seed\"] or meta.get(\"law\") != law:", "            if False:"),
    ("confirm.py", "                elif any(m2.get(f) != meta.get(f) for f in REPLAY_META):", "                elif False:"),  # B1
    ("confirm.py", "    if problems:                                       # P1", "    if False:                                       # P1"),
    # ---- s10.6 (Argus[harry1-d48cbcfd]): every unit's Aether tree replayed, rows 47+
    ("confirm.py", "            why = tree_problem(law, row[\"seed\"], meta, tree_replay)", "            why = None"),
    ("confirm.py", "if not (u[\"tree\"] == meta[\"tree\"] and ", "if not ("),
    ("confirm.py", " and u[\"origin\"] == meta[\"origin\"]\n", "\n"),
    ("confirm.py", "            and u[\"warm_digest\"] == meta[\"aether\"][\"warm_digest\"]):", "            ):"),
]
PALLAS_EDITS = os.path.join(ROOT, "rso", "aether", "challenge", "edits.json")    # applied verbatim after EDITS


def purge():
    for d in ("rso/aether/__pycache__", "rso/aether/tests/__pycache__", "rso/aether/demand/__pycache__"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)


def suite():
    purge()
    p = subprocess.run(SUITE, cwd=ROOT, capture_output=True, text=True, timeout=600)
    tail = (p.stderr or p.stdout).strip().splitlines()
    return p.returncode, tail[-1] if tail else ""


def _adapt(src, text):
    """Rewrite a newline in an edit to the file's own line ending (CRLF checkouts; Pallas S2)."""
    return text.replace("\n", "\r\n") if "\r\n" in src else text


def main(out):
    rows = []
    rc, tail = suite()
    rows.append({"edit": "BASELINE (unedited)", "returncode": rc, "result": "GREEN" if rc == 0 else "BROKEN", "tail": tail})
    if rc != 0:
        raise SystemExit("baseline not green: %s" % tail)
    with open(PALLAS_EDITS, encoding="utf-8") as fh:
        pallas = [(k, e["file"], e["old"], e["new"]) for k, e in sorted(json.load(fh).items())]
    for i, f, old, new in [(i, f, o, n) for i, (f, o, n) in enumerate(EDITS)] + pallas:
        path = os.path.join(ROOT, "rso", "aether", f)
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        src = raw.decode("utf-8")
        old, new = _adapt(src, old), _adapt(src, new)
        if src.count(old) != 1:
            rows.append({"edit": i, "file": f, "result": "EDIT_NOT_UNIQUE", "count": src.count(old)})
            continue
        try:
            open(path, "wb").write(src.replace(old, new).encode("utf-8"))
            rc, tail = suite()
        finally:
            open(path, "wb").write(raw)
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
        rows.append({"edit": i, "file": f, "old": old.strip(), "new": new.strip(), "returncode": rc,
                     "result": "KILLED" if rc != 0 else "SURVIVED", "tail": tail})
        print(i, f, rows[-1]["result"], tail, file=sys.stderr, flush=True)
    purge()
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    killed = sum(1 for r in rows if r.get("result") == "KILLED")
    total = len(EDITS) + len(pallas)
    print("killed %d / %d" % (killed, total))
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
