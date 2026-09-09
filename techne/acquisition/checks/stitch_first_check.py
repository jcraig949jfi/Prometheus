"""Stitch first useful check + the frozen upstream reproduction. Runs INSIDE the isolated env.

    <env>/python techne/acquisition/checks/stitch_first_check.py \
        --fixture <path to nuts-bolts.json> --manifest <path> --out <result json>

Two separate things happen here and the output keeps them separate:

  A) PAPER_REPRODUCTION  -- the four metrics frozen in
     techne/acquisition/reproduction/stitch_nuts_bolts.manifest.json, which was committed
     BEFORE this script ran. The expected values and tolerances are READ from that file;
     this script does not define them and cannot relax them.

  B) FIRST_USEFUL_CHECK  -- semantics-preserving expansion of the learned abstractions,
     verified by an expander written here that shares no code with stitch. The design's
     rule is "For Stitch, demonstrate semantics-preserving expansion before measuring later
     solving", and a library whose abstractions do not inline back to the original programs
     is not a library, it is a lossy encoding.

The expansion test is the strongest form available without an evaluator for the graphics
DSL: inline every abstraction application with its arguments substituted for the #k holes,
and require the result to be TOKEN-IDENTICAL to the original program. Syntactic identity
after inlining implies semantic identity under any interpretation of the primitives, which
is a stronger statement than agreeing on one evaluator -- and it needs no evaluator for a
DSL this seat has no semantics for.

NEGATIVE CONTROL: the same expander is run against a DELIBERATELY CORRUPTED abstraction
body. It must fail to recover the originals. An expander that cannot fail proves nothing
when it succeeds.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time

import stitch_core as sc


# ------------------------------------------------------------------ independent s-expr tools
# No stitch_core is used below this line until the reproduction section. This is the
# independent evaluator the design asks for.
_TOKEN = re.compile(r"\(|\)|[^\s()]+")


def tokenize(s: str) -> list[str]:
    return _TOKEN.findall(s)


def parse_sexpr(s: str):
    toks = tokenize(s)
    pos = 0

    def rd():
        nonlocal pos
        if pos >= len(toks):
            raise ValueError("unexpected end of input")
        t = toks[pos]
        pos += 1
        if t == "(":
            out = []
            while pos < len(toks) and toks[pos] != ")":
                out.append(rd())
            if pos >= len(toks):
                raise ValueError("unbalanced parentheses")
            pos += 1
            return out
        if t == ")":
            raise ValueError("unexpected )")
        return t

    node = rd()
    if pos != len(toks):
        raise ValueError(f"trailing tokens after expression: {toks[pos:]}")
    return node


def unparse(node) -> str:
    if isinstance(node, str):
        return node
    return "(" + " ".join(unparse(c) for c in node) + ")"


def normalize(s: str) -> str:
    """Whitespace-only normalisation, via the token stream. Does NOT reassociate, reorder
    or simplify anything -- two programs that normalise equal are the same tree."""
    return unparse(parse_sexpr(s))


def substitute(body, args: list):
    """Replace #0..#n with the argument subtrees. Holes are leaves, so this is a plain
    structural substitution with no capture to worry about."""
    if isinstance(body, str):
        m = re.fullmatch(r"#(\d+)", body)
        if m:
            i = int(m.group(1))
            if i >= len(args):
                raise ValueError(f"hole #{i} has no argument (got {len(args)})")
            return args[i]
        return body
    return [substitute(c, args) for c in body]


def expand(node, table: dict[str, dict]):
    """Inline every abstraction application, innermost first, until no abstraction name
    remains. `table` maps name -> {"arity": int, "body": parsed body}."""
    if isinstance(node, str):
        if node in table and table[node]["arity"] == 0:
            return expand(table[node]["body"], table)
        return node
    parts = [expand(c, table) for c in node]
    head = parts[0]
    if isinstance(head, str) and head in table:
        ar = table[head]["arity"]
        args = parts[1:]
        if len(args) < ar:
            # partial application: left as-is and reported, not silently mangled
            raise ValueError(f"{head} applied to {len(args)} args, arity {ar}")
        inlined = substitute(table[head]["body"], args[:ar])
        rest = args[ar:]
        out = expand(inlined, table)
        if rest:
            out = expand([out] + rest, table)
        return out
    return parts


def build_table(abstractions) -> dict[str, dict]:
    return {a.name: {"arity": int(a.arity), "body": parse_sexpr(a.body)}
            for a in abstractions}


def expansion_recovers_originals(originals: list[str], rewritten: list[str],
                                 table: dict[str, dict]) -> dict:
    ok, bad, errors = 0, [], []
    for i, (orig, rw) in enumerate(zip(originals, rewritten)):
        try:
            got = unparse(expand(parse_sexpr(rw), table))
            want = normalize(orig)
            if got == want:
                ok += 1
            else:
                bad.append({"index": i, "rewritten": rw[:200],
                            "expanded": got[:200], "original": want[:200]})
        except Exception as exc:
            errors.append({"index": i, "error": f"{type(exc).__name__}: {exc}",
                           "rewritten": rw[:200]})
    return {"n": len(originals), "n_recovered": ok, "n_mismatched": len(bad),
            "n_errored": len(errors), "all_recovered": ok == len(originals),
            "mismatches": bad[:5], "errors": errors[:5]}


# ------------------------------------------------------------------ reproduction
def run_compress(programs: list[str], invocation: dict) -> dict:
    t0 = time.perf_counter()
    res = sc.compress(programs, iterations=3, max_arity=3, threads=1, silent=True)
    dt = time.perf_counter() - t0
    j = res.json
    return {
        "seconds": round(dt, 3),
        "n_abstractions": int(j["num_abstractions"]),
        "original_cost": int(j["original_cost"]),
        "final_cost": int(j["final_cost"]),
        "compression_ratio": float(j["compression_ratio"]),
        "abstraction_names": [a.name for a in res.abstractions],
        "abstraction_arities": [int(a.arity) for a in res.abstractions],
        "abstraction_bodies": [a.body for a in res.abstractions],
        "rewritten": list(res.rewritten),
        "_abstractions": res.abstractions,
        "backend_args": j["args"],
    }


def score_metric(m: dict, observed) -> dict:
    exp = m["expected"]
    tol = m.get("tolerated_deviation")
    out = {"metric_id": m["metric_id"], "metric": m["metric"], "expected": exp,
           "observed": observed, "tolerated_deviation": tol,
           "verdict_grade": m.get("verdict_grade"),
           "expected_provenance": m.get("expected_provenance")}
    if isinstance(exp, list):
        obs_n = [normalize(x) for x in observed]
        exp_n = [normalize(x) for x in exp]
        out["observed_normalized"] = obs_n
        out["match"] = sorted(obs_n) == sorted(exp_n)
        out["only_in_observed"] = [x for x in obs_n if x not in exp_n]
        out["only_in_expected"] = [x for x in exp_n if x not in obs_n]
    elif isinstance(exp, (int, float)) and isinstance(observed, (int, float)):
        dev = abs(observed - exp)
        out["deviation"] = dev
        out["match"] = dev <= (tol if isinstance(tol, (int, float)) else 0)
    else:
        out["match"] = observed == exp
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--library-out", required=True,
                    help="declarative typed library export path")
    a = ap.parse_args()

    man = json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
    programs = json.loads(pathlib.Path(a.fixture).read_text(encoding="utf-8"))

    run1 = run_compress(programs, man["invocation"])
    run2 = run_compress(programs, man["invocation"])

    determinism = {
        "claim": "compress() exposes no seed; with threads=1 the identical invocation must "
                 "return the identical result, or no reproduction verdict is possible",
        "n_abstractions_equal": run1["n_abstractions"] == run2["n_abstractions"],
        "bodies_equal": run1["abstraction_bodies"] == run2["abstraction_bodies"],
        "original_cost_equal": run1["original_cost"] == run2["original_cost"],
        "final_cost_equal": run1["final_cost"] == run2["final_cost"],
        "rewritten_equal": run1["rewritten"] == run2["rewritten"],
    }
    determinism["deterministic"] = all(v for k, v in determinism.items() if k != "claim")

    observed_by_id = {
        "M1_N_ABSTRACTIONS": run1["n_abstractions"],
        "M2_ABSTRACTION_BODIES": run1["abstraction_bodies"],
        "M3_COST_BEFORE": run1["original_cost"],
        "M4_COST_AFTER": run1["final_cost"],
    }
    scored = [score_metric(m, observed_by_id[m["metric_id"]]) for m in man["metrics"]]

    first_hand = [s for s in scored if s["verdict_grade"] is None]
    second_hand = [s for s in scored if s["verdict_grade"] == "SECOND_HAND_EXPECTED_VALUE"]

    if not determinism["deterministic"]:
        status = "BLOCKED_NONDETERMINISTIC"
    elif all(s["match"] for s in scored):
        status = "REPRODUCED"
    elif all(s["match"] for s in first_hand) and not all(s["match"] for s in second_hand):
        status = "FIRST_HAND_METRICS_REPRODUCED_SECOND_HAND_COSTS_FAILED"
    else:
        status = "FAILED_OUTSIDE_TOLERANCE"

    # ---------------- B) semantics-preserving expansion, independent expander
    table = build_table(run1["_abstractions"])
    expansion = expansion_recovers_originals(programs, run1["rewritten"], table)

    # negative control: corrupt one body and require the expander to NOTICE
    import copy
    corrupt = copy.deepcopy(table)
    victim = run1["abstraction_names"][0]
    corrupt[victim]["body"] = parse_sexpr("(M 1 0 0 0)")
    corrupt_res = expansion_recovers_originals(programs, run1["rewritten"], corrupt)

    # cross-check: rewrite() on the originals must agree with compress()'s own rewritten
    rw = sc.rewrite(programs, run1["_abstractions"])
    rewrite_agrees = list(rw.rewritten) == run1["rewritten"]

    # ---------------- declarative typed export, no pickles
    library = {
        "schema": "techne.acquisition.stitch_library/1",
        "provenance": {
            "producer": "stitch_core==0.1.29 (isolated env h0h5_tools)",
            "invocation": man["invocation"]["call"],
            "input_fixture_sha256": man["data"][0]["sha256"],
            "reproduction_manifest": man["id"],
        },
        "export_rule": "DECLARATIVE ONLY. Abstraction bodies are exported as s-expression "
                       "TEXT plus a parsed typed AST. No stitch object, no Rust handle and "
                       "no pickle crosses this boundary, so nothing here can execute on "
                       "import and an admitted interpreter can validate it independently.",
        "abstractions": [
            {"name": n, "arity": ar, "body_sexpr": b, "body_ast": parse_sexpr(b),
             "holes": sorted({int(m) for m in re.findall(r"#(\d+)", b)}),
             "calls_earlier_abstractions": sorted(
                 {x for x in re.findall(r"fn_\d+", b)}),
             }
            for n, ar, b in zip(run1["abstraction_names"], run1["abstraction_arities"],
                                run1["abstraction_bodies"])
        ],
        "semantics_preserving_expansion_verified": expansion["all_recovered"],
        "verification_method": "every rewritten program inlined by an expander written "
                               "outside stitch and required to be token-identical to the "
                               "original; negative control corrupts a body and must fail",
        "NOT_QUALIFIED": "This library is a PROPOSAL. Mechanical evaluation decided it is "
                         "expansion-correct. Whether it is USEFUL is decided by a held-out "
                         "controlled experiment that has not been run.",
        "licensing": "the producing distribution declares NO license in any distributed "
                     "artifact; see techne/acquisition/LICENSE_EVIDENCE.json. This export "
                     "contains abstractions learned FROM the Wong et al. 2022 corpus, not "
                     "stitch code, but the blocker is recorded here so a consumer sees it.",
    }
    pathlib.Path(a.library_out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.library_out).write_text(json.dumps(library, indent=2) + "\n",
                                           encoding="utf-8")

    checks = [
        {"case": "DETERMINISM_UNDER_IDENTICAL_INVOCATION", **determinism,
         "pass": determinism["deterministic"]},
        {"case": "SEMANTICS_PRESERVING_EXPANSION", **expansion,
         "pass": expansion["all_recovered"]},
        {"case": "NEGATIVE_CONTROL_CORRUPTED_BODY_IS_CAUGHT",
         "corrupted_abstraction": victim,
         "n_recovered_with_corrupt_body": corrupt_res["n_recovered"],
         "n_total": corrupt_res["n"],
         "pass": not corrupt_res["all_recovered"],
         "why": "If the expander still recovered every original after a body was replaced "
                "by (M 1 0 0 0), it would not be reading the body at all and the positive "
                "result above would be vacuous."},
        {"case": "REWRITE_AGREES_WITH_COMPRESS",
         "claim": "rewrite(originals, abstractions) reproduces compress()'s own rewritten "
                  "programs exactly",
         "agrees": rewrite_agrees, "pass": rewrite_agrees},
    ]

    out = {
        "check": "stitch_first_useful_check_and_reproduction",
        "tool": "stitch_core",
        "stitch_core_version": "0.1.29",
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "reproduction": {
            "manifest_id": man["id"],
            "manifest_status_before_run": man["status"],
            "comparison_variant": man["comparison_variant"],
            "metrics": [{k: v for k, v in s.items() if k != "observed_normalized"}
                        for s in scored],
            "first_hand_all_match": all(s["match"] for s in first_hand),
            "second_hand_all_match": all(s["match"] for s in second_hand),
            "determinism": determinism,
            "status": status,
            "wall_seconds_run1": run1["seconds"],
            "wall_seconds_run2": run2["seconds"],
            "backend_args": run1["backend_args"],
        },
        "first_useful_check": {
            "cases": checks,
            "n_passed": sum(1 for c in checks if c["pass"]),
            "n_total": len(checks),
            "all_passed": all(c["pass"] for c in checks),
        },
        "library_export": a.library_out,
        "stage_separation": {
            "INSTALLATION": "done in a separate receipt",
            "PAPER_REPRODUCTION": status,
            "FIRST_USEFUL_CHECK": "PASSED" if all(c["pass"] for c in checks) else "FAILED",
            "ADAPTER_QUALIFICATION": "NOT ATTEMPTED -- no Prometheus consumer calls this yet",
            "LOCAL_SCIENTIFIC_BENEFIT": "NOT ATTEMPTED -- nothing here shows an experiment "
                                        "got a better answer",
        },
    }
    print(json.dumps(out))
    return 0 if out["first_useful_check"]["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
