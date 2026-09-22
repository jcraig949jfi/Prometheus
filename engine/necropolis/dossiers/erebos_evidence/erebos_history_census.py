"""erebos_history_census.py -- ONE question:

    What is on the record about how long Erebos ran, which ITER it reached,
    whether the pre-committed ITER-100 kill was ever executed, what the
    "0 permutation-null survivors" number actually measured (N, null,
    p-value), and where the runtime artifacts (234 composed claims, kill
    ledgers, logs, tick counter) are on this host today?

Sources: read-only git log over charon/agents/erebos and the Stygian
composition loaders; the pivot/erebos_* and pivot/sprint1/phase3 docs
(numbers extracted from them are HISTORICAL QUOTES, labelled as such, not
re-measurements); and a filesystem existence check of the gitignored
runtime paths in this worktree, the main worktree (from `git worktree
list`, not hardcoded) and any extra roots passed on argv.

Writes erebos_history_census_result.json next to this file. Pure ASCII.
Repo root is resolved from __file__ (no drive letters).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNTIME_REL = ["charon/agents/erebos/state", "charon/agents/erebos/artifacts",
               "charon/agents/erebos/logs", "charon/agents/stygian/state",
               "charon/agents/pollux/state", "charon/agents/_shared_queues",
               "charon/agents/hecate/artifacts"]


def git(*args: str) -> str:
    cp = subprocess.run(["git"] + list(args), cwd=str(REPO), capture_output=True,
                        text=True, timeout=300)
    return cp.stdout


def log(path: str) -> dict:
    lines = [ln for ln in git("log", "--format=%h|%ad|%s", "--date=short",
                              "--", path).splitlines() if ln]
    dates = [ln.split("|")[1] for ln in lines]
    iters = sorted({int(m) for ln in lines
                    for m in re.findall(r"ITER-?(\d+)", ln.split("|", 2)[2])})
    return {"commits_n": len(lines), "first": min(dates) if dates else None,
            "last": max(dates) if dates else None,
            "iter_numbers_in_subjects": iters,
            "commits_per_day": _per_day(dates)}


def _per_day(dates: list[str]) -> dict:
    d: dict[str, int] = {}
    for x in dates:
        d[x] = d.get(x, 0) + 1
    return dict(sorted(d.items()))


def runtime_presence(roots: list[Path]) -> dict:
    res = {}
    for root in roots:
        row = {}
        for rel in RUNTIME_REL:
            p = root / rel
            if p.exists():
                n = sum(1 for _ in p.rglob("*") if _.is_file())
                row[rel] = {"exists": True, "files_n": n}
            else:
                row[rel] = {"exists": False}
        res[str(root)] = row
    return res


def quote_numbers() -> dict:
    """Historical numbers, quoted from the docs that report them."""
    q: dict = {}
    k = REPO / "pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md"
    if k.exists():
        t = k.read_text(encoding="utf-8", errors="replace")
        q["PHASE3_K_verdict_doc"] = {
            "path": str(k.relative_to(REPO)).replace("\\", "/"),
            "observed_deltas_vs_pair_aware": _grab(t, r"observed deltas vs PAIR-AWARE counter\s*=\s*(\d+)"),
            "observed_deltas_vs_per_plugin": _grab(t, r"observed deltas vs per-plugin counter\s*=\s*(\d+)"),
            "p_value_quoted": _grab(t, r"p\s*=\s*(0\.\d+)"),
            "seven_seed_mean_quoted": _grab(t, r"7-seed mean\s*(0\.\d+)"),
            "n_permutations_quoted": _grab(t, r"N_PERMUTATIONS\s*=\s*(\d+)"),
            "seed_quoted": _grab(t, r"SEED\s*=\s*(\d+)"),
            "verdict_line": _line(t, "**Verdict:**"),
        }
    s = REPO / "charon/CHARON_SESSION_2026-06-03.md"
    if s.exists():
        t = s.read_text(encoding="utf-8", errors="replace")
        q["CHARON_SESSION_2026-06-03"] = {
            "ledger_rows_quoted": _grab(t, r"(\d{3})-row"),
            "lines_with_perm_null": [ln.strip()[:200] for ln in t.splitlines()
                                     if "permutation null" in ln.lower()][:6],
        }
    # pre-committed ITER-100 kill text
    hits = git("grep", "-n", "ITER-100", "--", "pivot", "charon").splitlines()
    q["ITER_100_mentions"] = [h[:220] for h in hits if h][:8]
    q["ITER_100_mentions_n"] = len([h for h in hits if h])
    # max ITER named anywhere in Erebos docs
    doc_iters = set()
    for h in git("grep", "-o", "-h", "-E", "ITER-[0-9]+", "--",
                 "pivot/erebos_*", "pivot/sprint1", "charon/CHARON_SESSION_2026-05-2*.md",
                 "charon/CHARON_SESSION_2026-06-0*.md",
                 "charon/agents/erebos").splitlines():
        m = re.search(r"ITER-(\d+)", h)
        if m:
            doc_iters.add(int(m.group(1)))
    q["max_ITER_named_in_docs_and_code"] = max(doc_iters) if doc_iters else None
    q["ITER_100_or_above_named"] = sorted(i for i in doc_iters if i >= 100)
    # the 234 number and its provenance
    q["claims_234_mentions"] = [h[:200] for h in git(
        "grep", "-n", "234 composed", "--", "pivot", "engine/ledger",
        "charon").splitlines() if h][:6]
    # Sprint-1 kill rule
    v = REPO / "charon/agents/erebos/sprint1/verdict.py"
    if v.exists():
        t = v.read_text(encoding="utf-8", errors="replace")
        q["sprint1_kill_rule_max_fails"] = _grab(t, r"KILL_RULE_MAX_FAILS\s*=\s*(\d+)")
    q["phase3_verdict_docs"] = sorted(p.name for p in
                                     (REPO / "pivot/sprint1/phase3").glob("*.md"))
    q["pivot_erebos_docs_n"] = len(list((REPO / "pivot").glob("erebos_*")))
    return q


def _grab(t: str, pat: str):
    m = re.search(pat, t)
    return m.group(1) if m else None


def _line(t: str, key: str) -> str:
    for ln in t.splitlines():
        if key in ln:
            return ln.strip()[:400]
    return ""


def main() -> int:
    out = {"question": __doc__.strip().splitlines()[0]}
    out["git_log_erebos_dir"] = log("charon/agents/erebos")
    out["git_log_stygian_composition_loaders"] = log(
        "charon/agents/stygian/loaders/composition_*")
    out["git_log_stygian_composition_tests"] = log(
        "charon/agents/stygian/tests/test_composition_*")
    out["git_log_pivot_erebos_docs"] = log("pivot/erebos_*")
    out["git_log_harmonia_costume_parity"] = log(
        "harmonia/primitives/test_baseline_costume_parity.py")
    roots = [REPO]
    wt = git("worktree", "list").splitlines()
    if wt:
        main_wt = Path(wt[0].split()[0])
        if main_wt.resolve() != REPO.resolve():
            roots.append(main_wt)
    for extra in sys.argv[1:]:
        roots.append(Path(extra))
    out["runtime_state_presence"] = runtime_presence(roots)
    out["gitignore_rules"] = [ln.strip() for ln in (
        REPO / "charon/agents/.gitignore").read_text().splitlines()
        if ln.strip() and not ln.startswith("#")]
    out["historical_quotes"] = quote_numbers()
    (HERE / "erebos_history_census_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")
    h = out["historical_quotes"]
    print(json.dumps({
        "erebos_commits": {k: out["git_log_erebos_dir"][k] for k in
                           ("commits_n", "first", "last", "iter_numbers_in_subjects")},
        "loader_commits": {k: out["git_log_stygian_composition_loaders"][k]
                           for k in ("commits_n", "first", "last")},
        "max_ITER_named": h["max_ITER_named_in_docs_and_code"],
        "ITER_100_named": h["ITER_100_or_above_named"],
        "ITER_100_mentions_n": h["ITER_100_mentions_n"],
        "phase3K": h.get("PHASE3_K_verdict_doc"),
        "runtime_present": {r: [k for k, v in row.items() if v["exists"]]
                            for r, row in out["runtime_state_presence"].items()},
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
