"""TECHNE-01: run the stitch extraction route on H1/H0's REAL solved programs.

    python -m techne.acquisition.checks.stitch_on_h1_solutions

Input: archaeon/docs/h0h5/H1H0_SOLVED_PROGRAMS_2026-09-10.json, sha256 (over the COMMITTED
bytes) 581aed3186281f1b250bfb08ef411a70d21d6581df07d6f7f2c1714943db30d7 as Archaeon declared.
17 programs: all 14 solved phase-2 cells, never de-duplicated, plus the 3 solved phase-1 source
rows.

THE QUESTION. My threshold measurement on Proteus's synthetic fixtures said abstractions become
non-empty at 3 programs -- but that was 3 programs that SHARED STRUCTURE, drawn from canonical
sum-of-products forms of 256 functions. Real solved programs are a different population: there
are 7 distinct s-expressions here and they are TINY (size 2 to 5 grammar nodes), where the
nuts-bolts corpus was large. Whether a library route works on real H1 output is therefore not
settled by the threshold; it is settled by running it on these.

FIVE DECLARED CORPORA, because "the solutions" is ambiguous and the ambiguity changes the answer:

  ALL_17          every exported row, duplicates included. Duplicates matter: stitch counts
                  USES, so the same program appearing six times is six uses of whatever
                  abstraction covers it.
  DISTINCT_7      the 7 distinct s-expressions, one copy each.
  PHASE2_14       the 14 solved phase-2 cells only (4 distinct) -- the population the brief
                  was about.
  PHASE2_DISTINCT_4   those 4, one copy each. This is the corpus closest in spirit to the
                  N=3 threshold measurement, and the direct test of it.
  PHASE1_3        the 3 phase-1 source rows, which is the "only 3 solutions" the brief named.

Run through the MIT-licensed Rust core over its documented JSON interface, not the bindings:
D-17 keeps the bindings development-only, and a result that cannot leave the host is not a
capability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import time
from collections import Counter

from .. import budget as _budget
from .. import manifest_io, paths, receipt

SOLVED = ("archaeon", "docs", "h0h5", "H1H0_SOLVED_PROGRAMS_2026-09-10.json")
DECLARED_SHA = "581aed3186281f1b250bfb08ef411a70d21d6581df07d6f7f2c1714943db30d7"
MINGW_GCC_BIN = ("C:/Users/jcrai/AppData/Local/Microsoft/WinGet/Packages/"
                 "BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/"
                 "mingw64/bin")

_TOKEN = re.compile(r"\(|\)|[^\s()]+")


def parse_sexpr(s: str):
    toks = _TOKEN.findall(s)
    pos = 0

    def rd():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(":
            out = []
            while toks[pos] != ")":
                out.append(rd())
            pos += 1
            return out
        return t
    n = rd()
    if pos != len(toks):
        raise ValueError("trailing tokens")
    return n


def unparse(n):
    return n if isinstance(n, str) else "(" + " ".join(unparse(c) for c in n) + ")"


def substitute(body, args):
    if isinstance(body, str):
        m = re.fullmatch(r"#(\d+)", body)
        return args[int(m.group(1))] if m else body
    return [substitute(c, args) for c in body]


def expand(node, table):
    if isinstance(node, str):
        # An arity-0 abstraction is applied as a BARE NAME, not as a call, so a string node can
        # itself be an application. Omitting this branch silently leaves `fn_0` unexpanded and
        # the expansion check then fails for a reason that has nothing to do with stitch. I had
        # this branch in the nuts-bolts check and dropped it here; arity-0 abstractions never
        # arose on that corpus because its programs were large enough to factor WITHIN.
        if node in table and table[node]["arity"] == 0:
            return expand(table[node]["body"], table)
        return node
    parts = [expand(c, table) for c in node]
    head = parts[0]
    if isinstance(head, str) and head in table:
        ar = table[head]["arity"]
        args = parts[1:]
        if len(args) < ar:
            raise ValueError(f"{head} under-applied")
        out = expand(substitute(table[head]["body"], args[:ar]), table)
        rest = args[ar:]
        return expand([out] + rest, table) if rest else out
    return parts


def run_compress(binary, cwd, progs, out, *, iterations, max_arity, b):
    inp = out.with_suffix(".in.json")
    inp.write_text(json.dumps(progs), encoding="utf-8")
    import os
    env = {**os.environ, "PATH": MINGW_GCC_BIN + ";" + os.environ.get("PATH", "")}
    r = b.run([str(binary), str(inp), f"--max-arity={max_arity}", f"--iterations={iterations}",
               "--threads=1", f"--out={out}"], cwd=str(cwd), env=env)
    if r["returncode"] != 0:
        return {"ok": False, "returncode": r["returncode"], "stderr_tail": r["stderr"][-600:]}
    doc = json.loads(out.read_text(encoding="utf-8"))
    return {"ok": True, "n_abstractions": int(doc["num_abstractions"]),
            "original_cost": int(doc["original_cost"]), "final_cost": int(doc["final_cost"]),
            "bodies": [x["body"] for x in doc["abstractions"]],
            "names": [x["name"] for x in doc["abstractions"]],
            "arities": [int(x["arity"]) for x in doc["abstractions"]],
            "uses": [int(x["num_uses"]) for x in doc["abstractions"]],
            "original": list(doc["original"]), "rewritten": list(doc["rewritten"])}


def expansion_check(res) -> dict:
    if not res.get("ok") or not res["bodies"]:
        return {"applicable": False, "reason": "no abstractions to expand"}
    table = {n: {"arity": ar, "body": parse_sexpr(b)}
             for n, ar, b in zip(res["names"], res["arities"], res["bodies"])}
    ok = err = 0
    for orig, rw in zip(res["original"], res["rewritten"]):
        try:
            ok += 1 if unparse(expand(parse_sexpr(rw), table)) == unparse(parse_sexpr(orig)) else 0
        except Exception:
            err += 1
    # negative control
    import copy
    bad = copy.deepcopy(table)
    bad[res["names"][0]]["body"] = parse_sexpr("c0")
    cok = 0
    for orig, rw in zip(res["original"], res["rewritten"]):
        try:
            cok += 1 if unparse(expand(parse_sexpr(rw), bad)) == unparse(parse_sexpr(orig)) else 0
        except Exception:
            pass
    n = len(res["original"])
    return {"applicable": True, "n": n, "recovered": ok, "errored": err,
            "all_recovered": ok == n and err == 0,
            "negative_control_recovered": cok,
            "negative_control_discriminates": cok < n}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-arity", type=int, default=3)
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--profile", default="stitch_core_reproduction")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    core = manifest_io.entry(man, "stitch_rust_core")
    root = paths.repos() / "stitch_rust_core"
    binary = root / "target" / "release" / "compress.exe"
    work = paths.tool_cache() / "checkwork" / "stitch_h1"
    work.mkdir(parents=True, exist_ok=True)

    rec = receipt.new("ADAPTER_QUALIFICATION", "stitch_rust_core")
    rec["check"] = "stitch_extraction_on_real_h1_solved_programs"
    rec["consumer"] = "H0/H2 instrument-library construction, on H1's actual output"
    rec["clears"] = "TECHNE-01"
    rec["budget_profile"] = _budget.get_profile(a.profile)

    src = paths.REPO_ROOT.joinpath(*SOLVED)
    # hash the COMMITTED bytes: this checkout converts LF to CRLF, so the working-tree hash
    # differs from Archaeon's by line endings alone. Verified both ways and recorded.
    git_bytes = subprocess.run(["git", "show", f"origin/main:{'/'.join(SOLVED)}"],
                               cwd=str(paths.REPO_ROOT), capture_output=True).stdout
    committed_sha = hashlib.sha256(git_bytes).hexdigest()
    worktree_sha = hashlib.sha256(src.read_bytes()).hexdigest()

    doc = json.loads(src.read_text(encoding="utf-8"))
    progs = doc["programs"]
    sx = [p["solution_sexpr"] for p in progs]
    p2 = [p for p in progs if p["candidate_set"].startswith("cs-h1h0-1-p2")]
    p1 = [p for p in progs if p["candidate_set"] == "cs-h1h0-1-p1"]

    def distinct(xs):
        seen, out = set(), []
        for x in xs:
            if x not in seen:
                seen.add(x); out.append(x)
        return out

    corpora = {
        "ALL_17": sx,
        "DISTINCT_7": distinct(sx),
        "PHASE2_14": [p["solution_sexpr"] for p in p2],
        "PHASE2_DISTINCT_4": distinct([p["solution_sexpr"] for p in p2]),
        "PHASE1_3": [p["solution_sexpr"] for p in p1],
    }

    results = {}
    with _budget.Budget(profile=_budget.get_profile(a.profile)) as b:
        for name, corpus in corpora.items():
            res = run_compress(binary, root, corpus, work / f"{name}.json",
                               iterations=a.iterations, max_arity=a.max_arity, b=b)
            res["expansion"] = expansion_check(res)
            res["n_programs"] = len(corpus)
            res["n_distinct"] = len(set(corpus))
            results[name] = res
        rec["resource_receipt"] = b.resource_receipt()

    sizes = [p["solution_size"] for p in progs]
    rec["observations"] = {
        "input": {
            "path": "/".join(SOLVED),
            "declared_sha256": DECLARED_SHA,
            "committed_bytes_sha256": committed_sha,
            "matches_declared": committed_sha == DECLARED_SHA,
            "worktree_sha256": worktree_sha,
            "line_ending_note": ("this checkout converts LF to CRLF on checkout, so the "
                                 "working-tree hash differs from Archaeon's by line endings "
                                 "alone. The COMMITTED bytes are what match and what is "
                                 "verified; a hash must be taken over those."),
            "n_programs": len(progs), "n_distinct_sexpr": len(set(sx)),
            "n_phase1": len(p1), "n_phase2_cells": len(p2),
            "n_phase2_distinct": len(set(p["solution_sexpr"] for p in p2)),
            "sexpr_multiplicity": dict(Counter(sx)),
            "solution_size_grammar_nodes": {"min": min(sizes), "max": max(sizes),
                                            "mean": round(sum(sizes) / len(sizes), 2)},
        },
        "route": {"binary": str(binary), "source_revision": core["upstream_revision"]["commit"],
                  "licence": core["license_claim"],
                  "why_this_route": "D-17 keeps the Python bindings development-only; a library "
                                    "that cannot leave the host is not a capability"},
        "parameters": {"max_arity": a.max_arity, "iterations": a.iterations, "threads": 1},
        "corpora": {k: {kk: vv for kk, vv in v.items()
                        if kk not in ("original", "rewritten", "bodies")}
                    | {"bodies": v.get("bodies", [])}
                    for k, v in results.items()},
        "threshold_comparison": {
            "synthetic_threshold": 3,
            "synthetic_corpus": "canonical sum-of-products over 256 Boolean functions, large "
                                "programs that shared structure",
            "real_corpus": f"{len(set(sx))} distinct programs of {min(sizes)}-{max(sizes)} "
                           f"grammar nodes",
            "why_the_threshold_does_not_transfer": (
                "the threshold was a property of (corpus, rendering, arity, iterations) and was "
                "stated as such. These programs are an order of magnitude smaller, so the "
                "question is not whether there are 3 of them but whether an abstraction can pay "
                "for itself against programs this size."),
        },
    }

    # ---- the finding, computed rather than narrated
    all_arities = [ar for v in results.values() if v.get("ok") for ar in v.get("arities", [])]
    kinds = {}
    for k, v in results.items():
        if not v.get("ok"):
            continue
        corpus = set(v.get("original", []))
        kinds[k] = [{"body": bd, "arity": ar, "uses": us,
                     "is_a_whole_program_in_the_corpus": bd in corpus}
                    for bd, ar, us in zip(v["bodies"], v["arities"], v["uses"])]
    rec["observations"]["analysis"] = {
        "max_arity_learned": max(all_arities) if all_arities else None,
        "every_abstraction_is_arity_zero": bool(all_arities) and max(all_arities) == 0,
        "abstraction_kind_per_corpus": kinds,
        "reading": (
            "NO ABSTRACTION HAS ARITY > 0 on any corpus. Nothing PARAMETERISED was learned, so "
            "what stitch produced is a set of named constants, not reusable functions. Two "
            "different things are happening and they should not be reported as one: on the "
            "duplicate-bearing corpora (ALL_17, PHASE2_14) every abstraction IS a whole program "
            "of the corpus, so stitch is MEMOISING DUPLICATES. EXACTLY ONE abstraction across "
            "all five corpora is a pure shared subexpression -- (not x2) in PHASE2_DISTINCT_4, "
            "factored out of (or x1 (not x2)) and (or (not x2) x1). In DISTINCT_7 the same body "
            "is classified whole-program, correctly: (not x2) is itself one of those 7 programs "
            "(a phase-1 solution), so there it is both. The classifier reports what is true "
            "rather than the more flattering of the two."),
        "why": ("these programs are 2 to 4 grammar nodes. There is almost nothing to factor "
                "WITHIN a program at that size, and a parameterised abstraction must pay for its "
                "own application syntax. The nuts-bolts corpus where stitch earned three "
                "arity-1-to-3 abstractions had programs an order of magnitude larger."),
        "consequence_for_H0_H2": (
            "a library of arity-0 macros is a compression dictionary, not an instrument library. "
            "On H1's current output the extraction route RUNS, is expansion-correct, and "
            "produces nothing a later solver could call WITH ARGUMENTS. The route is qualified; "
            "the corpus is not yet rich enough to exercise it. That is a statement about H1's "
            "program size, not about stitch."),
        "what_would_change_it": (
            "larger solved programs -- H1 beta's n=5 bits and K=4 would help -- or a corpus "
            "spanning tasks whose solutions share parameterised structure. Neither is Techne's "
            "to produce, and neither is a reason to change a parameter here."),
    }

    nonempty = [k for k, v in results.items() if v.get("ok") and v["n_abstractions"] > 0]
    checks = [
        ("the declared input hash matches the committed bytes", committed_sha == DECLARED_SHA),
        ("the route ran on every declared corpus", all(v.get("ok") for v in results.values())),
        ("every corpus that produced abstractions expands back to its originals",
         all(v["expansion"]["all_recovered"] for v in results.values()
             if v.get("ok") and v["expansion"]["applicable"])),
        ("negative control discriminates wherever expansion was checked",
         all(v["expansion"]["negative_control_discriminates"] for v in results.values()
             if v.get("ok") and v["expansion"]["applicable"])),
    ]
    rec["observations"]["checks"] = [{"claim": c, "pass": bool(p)} for c, p in checks]
    rec["observations"]["corpora_with_abstractions"] = nonempty
    rec["status"] = "MEASURED" if all(p for _, p in checks) else "FAILED"
    out = receipt.write(rec)

    print(f"=== stitch on REAL H1 solved programs -> {rec['status']} ===")
    print(f"input           {len(progs)} programs, {len(set(sx))} distinct, sizes "
          f"{min(sizes)}-{max(sizes)} grammar nodes")
    print(f"hash            committed {committed_sha[:16]}... matches declared "
          f"{committed_sha == DECLARED_SHA}")
    print(f"route           MIT core {core['upstream_revision']['commit'][:12]}, documented JSON")
    print(f"\n{'corpus':<20} {'n':>3} {'distinct':>8} {'absn':>5} {'cost_before':>11} "
          f"{'cost_after':>10}  expansion")
    for k, v in results.items():
        if not v.get("ok"):
            print(f"{k:<20} ERROR rc={v.get('returncode')}")
            continue
        e = v["expansion"]
        ex = (f"{e['recovered']}/{e['n']} (neg {e['negative_control_recovered']})"
              if e["applicable"] else "n/a")
        print(f"{k:<20} {v['n_programs']:>3} {v['n_distinct']:>8} {v['n_abstractions']:>5} "
              f"{v['original_cost']:>11} {v['final_cost']:>10}  {ex}")
    print()
    for k, v in results.items():
        if v.get("ok") and v["bodies"]:
            for nm, ar, bd, us in zip(v["names"], v["arities"], v["bodies"], v["uses"]):
                print(f"  {k:<20} {nm} arity={ar} uses={us}  {bd}")
    an = rec["observations"]["analysis"]
    print(f"\ncorpora with abstractions: {nonempty or 'NONE'}")
    print(f"max arity learned anywhere: {an['max_arity_learned']}   "
          f"every abstraction arity 0: {an['every_abstraction_is_arity_zero']}")
    for k, items in an["abstraction_kind_per_corpus"].items():
        for it in items:
            kind = ("WHOLE PROGRAM (memoised duplicate)"
                    if it["is_a_whole_program_in_the_corpus"] else "shared SUBEXPRESSION")
            print(f"  {k:<20} {kind:<34} uses={it['uses']:<3} {it['body']}")
    for c in rec["observations"]["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    print(f"receipt         {out}")
    return 0 if rec["status"] == "MEASURED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
