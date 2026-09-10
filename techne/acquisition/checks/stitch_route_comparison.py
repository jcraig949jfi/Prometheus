"""Rust core vs Python bindings, on ONE pinned input. Same claim, two routes.

    python -m techne.acquisition.checks.stitch_route_comparison

The point is not to reproduce the published numbers again -- the Python route already did that
on 2026-09-09. It is to establish that the MIT-licensed Rust core, driven through its
DOCUMENTED JSON interface, gives the same answer as the bindings whose licence is unresolved.
If it does, H0/H2 has a library route that is not blocked on D-17.

THE INPUT IS PINNED BY HASH, not by path, and it is deliberately the file the PYTHON route
consumed: `nuts-bolts.json` sha256 4e8ea309..., from mlb2251/stitch@350804b7, recorded in
MANIFEST.json with expected_sha256 and VERIFIED at acquisition. The core's own tree ships a
copy at its pinned revision 0ef5ec7 with a DIFFERENT sha256 (1c734247...) and identical
content -- same 250 programs, same order, formatting only. Letting each route use its own
in-tree copy would put a dataset difference inside a route comparison, so one file is used for
both and this is which.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

from .. import budget as _budget
from .. import manifest_io, paths, receipt

MINGW_GCC_BIN = ("C:/Users/jcrai/AppData/Local/Microsoft/WinGet/Packages/"
                 "BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/"
                 "mingw64/bin")

# The Python route's result, as recorded in its own receipt on 2026-09-09.
PYTHON_ROUTE = {
    "source": "techne/acquisition/reproduction/stitch_nuts_bolts.manifest.json + the "
              "FIRST_USEFUL_CHECK receipt of 2026-09-09",
    "n_abstractions": 3,
    "original_cost": 1919558,
    "final_cost": 316890,
    "bodies": [
        "(T (repeat (T l (M 1 0 -0.5 (/ 0.5 (tan (/ pi #1))))) #1 (M 1 (/ (* 2 pi) #1) 0 0)) (M #0 0 0 0))",
        "(repeat (T (T #2 (M 0.5 0 0 0)) (M 1 0 (* #1 (cos (/ pi 4))) (* #1 (sin (/ pi 4))))) #0 (M 1 (/ (* 2 pi) #0) 0 0))",
        "(T (T c (M 2 0 0 0)) (M #0 0 0 0))",
    ],
}


# --- the independent expander, reused verbatim in spirit from the bindings check -----------
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
    node = rd()
    if pos != len(toks):
        raise ValueError("trailing tokens")
    return node


def unparse(n):
    return n if isinstance(n, str) else "(" + " ".join(unparse(c) for c in n) + ")"


def substitute(body, args):
    if isinstance(body, str):
        m = re.fullmatch(r"#(\d+)", body)
        return args[int(m.group(1))] if m else body
    return [substitute(c, args) for c in body]


def expand(node, table):
    if isinstance(node, str):
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="stitch_core_reproduction")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    core = manifest_io.entry(man, "stitch_rust_core")
    stitch = manifest_io.entry(man, "stitch")
    root = paths.repos() / "stitch_rust_core"
    binary = root / "target" / "release" / "compress.exe"
    fixture = paths.tool_cache() / "fixtures" / "stitch" / "nuts-bolts.json"
    workdir = paths.tool_cache() / "checkwork" / "stitch_rust"
    workdir.mkdir(parents=True, exist_ok=True)
    out_json = workdir / "out.json"

    rec = receipt.new("PAPER_REPRODUCTION", "stitch_rust_core")
    rec["check"] = "rust_core_vs_python_bindings_on_one_pinned_input"
    rec["budget_profile"] = _budget.get_profile(a.profile)

    if not binary.exists():
        rec["status"] = "BLOCKED_BINARY_NOT_BUILT"
        rec["unrun_or_blocked"].append(f"{binary} does not exist")
        print(receipt.write(rec)); return 3

    # the pinned input, verified by hash before anything runs
    expected = next(f["expected_sha256"] for f in stitch["fixtures"]
                    if f["id"] == "nuts_bolts_cogsci")
    got = hashlib.sha256(fixture.read_bytes()).hexdigest()
    intree = root / "data" / "cogsci" / "nuts-bolts.json"
    intree_sha = hashlib.sha256(intree.read_bytes()).hexdigest() if intree.exists() else None

    with _budget.Budget(profile=_budget.get_profile(a.profile)) as b:
        # network is FORBIDDEN under this profile; assert the run needs none
        argv_run = [str(binary), str(fixture), "--max-arity=3", "--iterations=3",
                    "--threads=1", f"--out={out_json}"]
        env_path = MINGW_GCC_BIN + ";" + __import__("os").environ.get("PATH", "")
        t0 = time.perf_counter()
        r = b.run(argv_run, cwd=str(root), env={**__import__("os").environ, "PATH": env_path})
        wall = time.perf_counter() - t0
        rec["resource_receipt"] = b.resource_receipt()
    receipt.record_command(rec, r)

    doc = json.loads(out_json.read_text(encoding="utf-8"))
    rust = {
        "n_abstractions": int(doc["num_abstractions"]),
        "original_cost": int(doc["original_cost"]),
        "final_cost": int(doc["final_cost"]),
        "bodies": [x["body"] for x in doc["abstractions"]],
        "names": [x["name"] for x in doc["abstractions"]],
        "arities": [int(x["arity"]) for x in doc["abstractions"]],
        "n_rewritten": len(doc["rewritten"]),
        "wall_seconds": round(wall, 3),
    }

    norm = lambda s: unparse(parse_sexpr(s))
    metrics = [
        {"metric": "n_abstractions", "python": PYTHON_ROUTE["n_abstractions"],
         "rust": rust["n_abstractions"],
         "agree": PYTHON_ROUTE["n_abstractions"] == rust["n_abstractions"]},
        {"metric": "original_cost", "python": PYTHON_ROUTE["original_cost"],
         "rust": rust["original_cost"],
         "agree": PYTHON_ROUTE["original_cost"] == rust["original_cost"]},
        {"metric": "final_cost", "python": PYTHON_ROUTE["final_cost"],
         "rust": rust["final_cost"],
         "agree": PYTHON_ROUTE["final_cost"] == rust["final_cost"]},
        {"metric": "abstraction_bodies (whitespace-normalised, as a set)",
         "python": PYTHON_ROUTE["bodies"], "rust": rust["bodies"],
         "agree": sorted(map(norm, PYTHON_ROUTE["bodies"])) == sorted(map(norm, rust["bodies"]))},
    ]

    # semantics-preserving expansion of the RUST route's own output, by our expander
    table = {x["name"]: {"arity": int(x["arity"]), "body": parse_sexpr(x["body"])}
             for x in doc["abstractions"]}
    ok = bad = 0
    for orig, rw in zip(doc["original"], doc["rewritten"]):
        try:
            ok += 1 if unparse(expand(parse_sexpr(rw), table)) == norm(orig) else 0
        except Exception:
            bad += 1
    expansion = {"n": len(doc["rewritten"]), "recovered": ok, "errored": bad,
                 "all_recovered": ok == len(doc["rewritten"]) and bad == 0}

    # negative control, so the expansion result is not vacuous
    import copy
    corrupt = copy.deepcopy(table)
    corrupt[rust["names"][0]]["body"] = parse_sexpr("(M 1 0 0 0)")
    cok = 0
    for orig, rw in zip(doc["original"], doc["rewritten"]):
        try:
            cok += 1 if unparse(expand(parse_sexpr(rw), corrupt)) == norm(orig) else 0
        except Exception:
            pass

    checks = [
        ("the pinned input is byte-identical to the one the Python route consumed",
         got == expected),
        ("all four metrics agree between the two routes", all(m["agree"] for m in metrics)),
        ("the Rust route's own output expands back to the originals",
         expansion["all_recovered"]),
        ("negative control: a corrupted body breaks the expansion",
         cok < expansion["n"]),
        ("the run needed no network under a network-FORBIDDEN profile", r["returncode"] == 0),
    ]

    rec["observations"] = {
        "input_pinned": {
            "path": str(fixture), "sha256": got, "expected_sha256": expected,
            "verified": got == expected,
            "provenance": "mlb2251/stitch@350804b7, recorded in MANIFEST.json fixtures",
            "why_this_one": ("it is the file the Python route consumed, so the comparison holds "
                             "the input BYTE-identical rather than merely content-identical"),
            "core_in_tree_copy_at_0ef5ec7": {
                "sha256": intree_sha, "used": False,
                "note": "different bytes, identical content (same 250 programs, same order); "
                        "NOT used, because a route comparison must not contain a dataset "
                        "difference"},
        },
        "rust_route": {**rust, "binary": str(binary),
                       "source_revision": core["upstream_revision"]["commit"],
                       "licence": core["license_claim"],
                       "invocation": " ".join(argv_run)},
        "python_route": PYTHON_ROUTE,
        "metrics": metrics,
        "expansion": expansion,
        "negative_control_recovered": cok,
        "checks": [{"claim": c, "pass": bool(p)} for c, p in checks],
    }
    rec["status"] = "ROUTES_AGREE" if all(p for _, p in checks) else "ROUTES_DISAGREE"
    rec["consequence"] = (
        "H0/H2 can construct its instrument library through the MIT-licensed Rust core over a "
        "documented JSON interface, with the same result the unlicensed Python bindings give. "
        "That does NOT clear D-17 -- the bindings' licence is still unresolved and nothing "
        "derived through THEM may leave the host -- it means D-17 no longer gates the "
        "capability."
        if rec["status"] == "ROUTES_AGREE" else
        "the two routes disagree; the Rust route is not a drop-in substitute and the "
        "difference must be characterised before either is used")
    out = receipt.write(rec)

    print(f"=== stitch route comparison -> {rec['status']} ===")
    print(f"input           {fixture.name} sha256 {got[:16]}... verified={got == expected}")
    print(f"                core in-tree copy {str(intree_sha)[:16]}... NOT used (identical content)")
    print(f"rust binary     {binary.name} from {core['upstream_revision']['commit'][:12]} (MIT)")
    for m in metrics:
        pv = m["python"] if not isinstance(m["python"], list) else f"{len(m['python'])} bodies"
        rv = m["rust"] if not isinstance(m["rust"], list) else f"{len(m['rust'])} bodies"
        print(f"  {'AGREE' if m['agree'] else 'DIFFER':<7} {m['metric']:<48} py={pv} rust={rv}")
    print(f"expansion       {expansion['recovered']}/{expansion['n']} recovered; "
          f"negative control {cok}/{expansion['n']}")
    print(f"wall            {rust['wall_seconds']}s")
    for c in rec["observations"]["checks"]:
        print(f"  {'PASS' if c['pass'] else 'FAIL':<5} {c['claim']}")
    print(f"receipt         {out}")
    return 0 if rec["status"] == "ROUTES_AGREE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
