"""Donor Foundry disposition audit -- what Prometheus ACTUALLY possesses, measured today.

    python -m techne.scripts.donor_disposition --out techne/acquisition/DONOR_DISPOSITION_<date>.json --txt <path>

The Gen-0 handoff (techne/TECHNE_GEN0_DONOR_HANDOFF.txt, 2026-08-31) listed five wrapped donors
and one held contestant, and named the ugly condition in its blocker B5: capability surfaces
with ZERO callers. This script re-measures every donor Techne has ever been responsible for
against TODAY'S tree and installed interpreter, so the four-word ladder can be answered from
evidence rather than recall:

    PRESENT      the distribution is installed here (importlib.metadata) and imports
    WRAPPED      a Techne adapter / wrapper module exists and its tests exist
    CONTROLLED   a receipt or test with a positive/cheat/parity control exists (path quoted)
    CONSUMED     a tracked .py outside techne/ (and outside tests) imports the donor OR the wrapper

Labels are then assigned by rule from those measurements plus the recorded blockers; the rule
is printed with the table. "Installed" is never allowed to become "consumed" by implication:
`consumers_direct` and `consumers_via_wrapper` are separate columns, because the Gen-0 adapter
contract (native_selection_relation on every artifact) was the provenance route, and whether
consumers used it or bypassed it is the finding.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- the donors
# dist: PyPI distribution name (None for a non-pip donor); module: import name;
# wrapper: Techne module(s) that wrap it; direct_pattern: regex for a direct import;
# controls: receipts/tests that carry a real control (quoted, verified to exist by the script);
# blockers: recorded, with owner; origin: which Techne mission acquired it.
DONORS = [
    dict(name="tensorly", dist="tensorly", module="tensorly", upstream="github.com/tensorly/tensorly", license="BSD-3 (modified)",
         origin="Gen-0 2026-08-31", wrapper=["techne/lib/donors/tensorly_adapter.py", "prometheus_math/symbolic_tensor_decomp.py"],
         controls=["techne/donor_tensor_parity_2026-08-31.json", "prometheus_math/tests/test_tensor_decomposition.py", "techne/tests/test_donor_adapters.py"],
         blockers=[], notes="TT parity 5/5 vs quimb with ground truth by construction (NATIVE_EARNS_DISTINCT_ROLE)"),
    dict(name="pyribs", dist="ribs", module="ribs", upstream="github.com/icaros-usc/pyribs", license="MIT",
         origin="Gen-0 2026-08-31; H3 adapter 2026-09-10", wrapper=["techne/lib/donors/pyribs_adapter.py", "techne/h3_retention/adapter.py", "techne/h3_retention/archaeon_seam.py"],
         controls=["techne/acquisition/receipts/adapter_qualification-pyribs-20260911T065018Z.json", "techne/tests/test_h3_retention.py", "techne/tests/test_donor_adapters.py"],
         blockers=[], notes="H3 GridArchive adapter retains the IDENTICAL set to Archaeon's independent behavioral policy on cs-c3-2 (150 rows, 12 sealed queries); CVT and SlidingBoundaries archives NOT qualified (TECHNE-03/04 open)"),
    dict(name="discopy", dist="discopy", module="discopy", upstream="github.com/discopy/discopy", license="BSD-3",
         origin="Gen-0 2026-08-31", wrapper=["techne/lib/donors/retired/discopy_adapter.py"],
         controls=["techne/tests/test_donor_adapters.py"], blockers=[],
         notes="compose + tensor_eval only; Gen-0 B5 said: no consumer within a generation or two = arsenal weight"),
    dict(name="egglog", dist="egglog", module="egglog", upstream="github.com/egraphs-good/egglog-python", license="MIT",
         origin="pre-Gen-0 install, reconciled 2026-08-31", wrapper=["techne/lib/donors/egglog_adapter.py", "techne/loop/egglog_saturation_demo.py"],
         controls=["techne/tests/test_donor_adapters.py"], blockers=["B2 Family A vs Family B (Lexis) -- see notes"],
         notes="only Python-reachable member of the UW PLSE e-graph family; Ergon's gen0/family_b_probe.py (2026-08-31) recorded FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER on the RM genotype question"),
    dict(name="cvc5", dist="cvc5", module="cvc5", upstream="github.com/cvc5/cvc5", license="BSD-3",
         origin="Gen-0 2026-08-31", wrapper=["techne/lib/donors/retired/cvc5_adapter.py"],
         controls=["techne/donor_smt_comparison_2026-08-31.json", "techne/tests/test_donor_adapters.py"],
         blockers=["B3 teardown segfault worked around by ordering, not enforced by a test"],
         notes="REDUNDANT_AT_GEN0: 6/6 QF_LIA agreement with z3; z3 has since been qualified as H1's oracle (2048/2048) and has 6 direct consumers"),
    dict(name="stitch", dist="stitch_core", module="stitch_core", upstream="github.com/mlb2251/stitch (core) + mlb2251/stitch_bindings (wheel)", license="core MIT @0ef5ec7f1709; bindings UNRESOLVED @v0.1.29",
         origin="held 2026-08-31; acquired 2026-09-09/10 (H0-H5 lane)", wrapper=["techne/acquisition/checks/stitch_first_check.py", "techne/acquisition/exports"],
         controls=["techne/acquisition/receipts/adapter_qualification-stitch_rust_core-20260911T074111Z.json", "techne/acquisition/receipts/paper_reproduction-stitch_rust_core-20260910T161201Z.json"],
         blockers=["D-17 v1 amendment (operator): bindings dev-only on licence; core MIT export route", "TECHNE-43: section-1 declaration + 8 boundary fixtures (Vivarium contract v1.1: a scientific kind may NOT call an external executable at 1.0)"],
         notes="on the only held-out-legal corpus (PHASE1_3) stitch returns 0 abstractions and Archaeon's own extractor also returns 0; on ALL_17 every abstraction has arity 0; installed in the ISOLATED tool env (TECHNE_TOOL_CACHE), not the default interpreter"),
    dict(name="z3", dist="z3-solver", module="z3", upstream="github.com/Z3Prover/z3", license="MIT",
         origin="pre-existing; qualified 2026-09-10", wrapper=["techne/acquisition/checks/z3_h1_oracle.py", "harmonia/experiments/z3_backend.py"],
         controls=["techne/acquisition/receipts/adapter_qualification-z3-20260910T222642Z.json"],
         blockers=["TECHNE-22 UNKNOWN-by-incompleteness never elicited on this build"],
         notes="exhaustive parity 2048/2048 vs proteus.eval.boolean.truth_table, 32,640 pairs, every witness independently validated"),
    dict(name="hypothesis", dist="hypothesis", module="hypothesis", upstream="github.com/HypothesisWorks/hypothesis", license="MPL-2.0",
         origin="pre-existing; qualified 2026-09-11", wrapper=["techne/acquisition/checks/hypothesis_program_minimiser.py", "techne/ladder_circuits/adversarial_registry.py"],
         controls=["techne/acquisition/receipts/adapter_qualification-hypothesis-20260911T065703Z.json"],
         blockers=[], notes="SOUND 45/45, NOT MINIMAL 24/45 (max excess 4 nodes); usefulness over enumeration not established"),
    dict(name="cvxpy+CLARABEL+SCS", dist="cvxpy", module="cvxpy", upstream="github.com/cvxpy/cvxpy; oxfordcontrol/Clarabel.rs; cvxgrp/scs", license="Apache-2.0 all three",
         origin="pre-existing; gap fixture 2026-09-10/11", wrapper=["prometheus_math/optimization_sdp.py", "techne/scripts/capability_gap_fixture.py"],
         controls=["techne/tests/test_capability_gap_fixture.py", "techne/acquisition/GAP_FIXTURE_SDP.json"],
         blockers=["TECHNE-46 no accuracy requirement declared (Harmonia/Aporia)"],
         notes="every arm correctness-scored (TECHNE-45); SCS default tolerance is silently wrong at cond >= 1e4, eps=1e-9 fixes it"),
    dict(name="dreamcoder", dist=None, module=None, upstream="github.com/ellisk42/ec", license="only notice is AngularJS MIT text (TECHNE-16 UNRESOLVED)",
         origin="H0-H5 lane 2026-09-09", wrapper=["techne/acquisition/checks/dreamcoder_smoke.py"],
         controls=["techne/acquisition/receipts/first_useful_check-dreamcoder-20260910T222933Z.json"],
         blockers=["TECHNE-15 build in WSL2 (docker + opam 4.06.1); 14 of 38 requirement pins have a wheel here", "TECHNE-16 licence"],
         notes="Nyx delivered a DreamCoder-shaped organ independently (memory note 2026-09-11); Techne's receipt is the obstruction record, not a build"),
    dict(name="POET", dist=None, module=None, upstream="github.com/uber-research/poet", license="Apache-2.0",
         origin="H0-H5 lane", wrapper=[], controls=[], blockers=["TECHNE-17 PARKED to 2026-12-11: H4 1.1 reference arm by design (Harmonia ruling)"],
         notes="the acquisition command's REFUSAL is the artifact until H4 1.0 closes; supply-chain rule: PyPI 'poet' is an unrelated package"),
    dict(name="SDPA-GMP", dist=None, module=None, upstream="sdpa.sourceforge.net (SDPA-GMP)", license="GPL",
         origin="TECHNE-39 (unbuilt)", wrapper=[], controls=[], blockers=["TECHNE-39 L: no consumer has declared a certificate requirement (report_95 / report_166 are the certificate-shaped candidates, not queued)"],
         notes="the only route to a verifiable certificate beyond double precision; not a purchase"),
    dict(name="MOSEK", dist=None, module=None, upstream="mosek.com", license="commercial ($4,300 perpetual)",
         origin="REQ-029 roadmap row", wrapper=[], controls=["techne/acquisition/GAP_FIXTURE_SDP.json"], blockers=[],
         notes="STRUCK 2026-09-11: no roadmap SDP at 1e10 (Harmonia), the 1e10 instance was Techne's own defect (ELEN-TECHNE-38), and the free path handles every regime tested"),
]


def _run(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONPATH=str(REPO)))
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError as exc:
        return -2, "", str(exc)


def installed_version(dist):
    if not dist:
        return None
    try:
        from importlib.metadata import version
        return version(dist)
    except Exception:                                                   # noqa: BLE001
        return None


def import_status(module):
    if not module:
        return {"status": "N/A"}
    t0 = time.perf_counter()
    rc, out, err = _run([sys.executable, "-c", "import importlib,sys; importlib.import_module(sys.argv[1])", module], timeout=180)
    return {"status": "IMPORTS" if rc == 0 else "FAILS", "seconds": round(time.perf_counter() - t0, 1),
            **({"error": (err.splitlines() or ["?"])[-1][:200]} if rc else {})}


def git_grep(pattern, globs=("*.py",)):
    rc, out, _ = _run(["git", "grep", "-l", "-P", "-e", pattern, "--", *globs])
    return [l.replace("\\", "/") for l in out.splitlines() if l]


def consumers(donor):
    res = {"direct": [], "via_wrapper": []}
    if donor["module"]:
        pat = r"^\s*(from\s+%s(\.|\s)|import\s+%s\b)" % (re.escape(donor["module"]), re.escape(donor["module"]))
        res["direct"] = sorted(f for f in git_grep(pat)
                               if not f.startswith("techne/") and "/tests/" not in f and not f.rsplit("/", 1)[-1].startswith("test_"))
    for w in donor["wrapper"]:
        if not w.endswith(".py"):
            continue
        mod = w[:-3].replace("/", ".")
        base = mod.rsplit(".", 1)[-1]
        parent = mod.rsplit(".", 1)[0]
        # full module path, or `from <parent> import <base>`; never a bare basename, which
        # would count every unrelated adapter.py in the tree as a consumer of this one
        pat = r"(from\s+%s\s+import|import\s+%s\b|from\s+%s\s+import\s+[^\n]*\b%s\b)" % (
            re.escape(mod), re.escape(mod), re.escape(parent), re.escape(base))
        hits = [f for f in git_grep(pat) if f != w and not f.startswith("techne/") and "/tests/" not in f
                and not f.rsplit("/", 1)[-1].startswith("test_")]
        res["via_wrapper"] += [{"wrapper": w, "consumer": f} for f in sorted(hits)]
    return res


def git_last(path):
    rc, out, _ = _run(["git", "log", "-1", "--format=%h %cs", "--", path])
    return out if rc == 0 and out else None


def classify(row):
    labels = []
    present = row["installed_version"] is not None and row["import"]["status"] == "IMPORTS"
    if row["dist"] is None and not row["wrapper_present"]:
        labels.append("CANDIDATE" if not row["blockers"] else "BLOCKED")
    if row["dist"] is None and row["wrapper_present"] and not present:
        labels.append("CANDIDATE")
    if present:
        labels += ["ACQUIRED", "IMPORT-TESTED"]
    if row["wrapper_present"]:
        labels.append("WRAPPED")
    if row["controls_present"]:
        labels.append("CONTROLLED")
    if row["consumers"]["direct"] or row["consumers"]["via_wrapper"]:
        labels.append("CONSUMED")
    if row["blockers"]:
        labels.append("BLOCKED")
    if row["name"] == "cvc5":
        labels += ["SUPERSEDED (by z3, qualified 2026-09-10)", "ADAPTER RETIRED 2026-09-12 (TECHNE-51)"]
    if row["name"] == "discopy":
        labels += ["ADAPTER RETIRED 2026-09-12 (TECHNE-51); donor stays a CANDIDATE"]
    if row["name"] == "MOSEK":
        labels = ["REJECTED (struck 2026-09-11)"]
    if row["name"] == "POET":
        labels = ["CANDIDATE", "PARKED to 2026-12-11"]
    if row["name"] == "SDPA-GMP":
        labels = ["CANDIDATE (no consumer has declared the requirement)"]
    if row["name"] == "dreamcoder":
        labels = ["CANDIDATE", "BLOCKED (TECHNE-15 build, TECHNE-16 licence)"]
    if row["name"] == "stitch" and not present:
        # installed in the isolated tool env, not the default interpreter: say so, do not
        # let a default-interpreter import failure read as ABSENT.
        labels = [l for l in labels if l not in ("CANDIDATE",)]
        labels = ["ACQUIRED (isolated env; see stitch lock + installation receipts)", "IMPORT-TESTED (isolated env)"] + labels
    return labels


def build():
    rows = []
    for d in DONORS:
        row = dict(d)
        row["installed_version"] = installed_version(d["dist"])
        row["import"] = import_status(d["module"])
        row["wrapper_present"] = [w for w in d["wrapper"] if (REPO / w).exists()]
        row["wrapper_missing"] = [w for w in d["wrapper"] if not (REPO / w).exists()]
        row["controls_present"] = [c for c in d["controls"] if (REPO / c).exists()]
        row["controls_missing"] = [c for c in d["controls"] if not (REPO / c).exists()]
        row["consumers"] = consumers(d)
        row["wrapper_git_last"] = {w: git_last(w) for w in row["wrapper_present"]}
        row["labels"] = classify(row)
        rows.append(row)
        print("%-20s v=%-9s import=%-8s wrap=%d ctrl=%d direct=%d via=%d  %s" % (
            d["name"], row["installed_version"], row["import"]["status"], len(row["wrapper_present"]),
            len(row["controls_present"]), len(row["consumers"]["direct"]), len(row["consumers"]["via_wrapper"]),
            ", ".join(row["labels"])), flush=True)
    rc, head, _ = _run(["git", "rev-parse", "HEAD"])
    adapters_outside = [f for f in git_grep(r"techne\.lib\.donors|from\s+techne\.lib\s+import\s+donors") if not f.startswith("techne/")]
    return {"schema": "techne.donor_disposition/1", "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head": head, "interpreter": sys.version.split()[0], "executable": sys.executable,
            "label_rule": ("ACQUIRED+IMPORT-TESTED iff the distribution is installed in THIS interpreter and imports in a "
                           "fresh process; WRAPPED iff a listed wrapper file exists; CONTROLLED iff a listed control "
                           "artefact exists on the tree; CONSUMED iff a tracked non-test .py outside techne/ imports the "
                           "donor or a wrapper; BLOCKED iff a blocker is recorded. Hand overrides are named in classify()."),
            "gen0_adapter_contract_consumers_outside_techne": adapters_outside,
            "rows": rows}


def render(doc):
    o = ["DONOR DISPOSITION -- built %s at %s, interpreter %s" % (doc["built_at"], doc["head"][:9], doc["interpreter"]), ""]
    o.append("%-20s %-10s %-8s %-4s %-4s %-6s %-4s labels" % ("donor", "installed", "import", "wrap", "ctrl", "direct", "via"))
    o.append("-" * 110)
    for r in doc["rows"]:
        o.append("%-20s %-10s %-8s %-4d %-4d %-6d %-4d %s" % (
            r["name"], r["installed_version"] or "-", r["import"]["status"], len(r["wrapper_present"]),
            len(r["controls_present"]), len(r["consumers"]["direct"]), len(r["consumers"]["via_wrapper"]), ", ".join(r["labels"])))
    o.append("")
    o.append("Gen-0 adapter contract (techne.lib.donors) importers outside techne/: %s" % (
        doc["gen0_adapter_contract_consumers_outside_techne"] or "NONE"))
    o.append("")
    for r in doc["rows"]:
        o.append("=" * 110)
        o.append("%s   upstream %s   licence %s" % (r["name"], r["upstream"], r["license"]))
        o.append("  origin      %s" % r["origin"])
        o.append("  installed   %s   import %s%s" % (r["installed_version"], r["import"]["status"],
                                                      ("  -- " + r["import"]["error"]) if r["import"].get("error") else ""))
        o.append("  wrappers    %s" % (", ".join("%s (%s)" % (w, r["wrapper_git_last"].get(w)) for w in r["wrapper_present"]) or "NONE"))
        if r["wrapper_missing"]:
            o.append("  MISSING     %s" % ", ".join(r["wrapper_missing"]))
        o.append("  controls    %s" % (", ".join(r["controls_present"]) or "NONE"))
        if r["controls_missing"]:
            o.append("  ctrl MISSING %s" % ", ".join(r["controls_missing"]))
        o.append("  direct use  %s" % (", ".join(r["consumers"]["direct"]) or "NONE outside techne/"))
        o.append("  via wrapper %s" % (", ".join("%s <- %s" % (v["consumer"], v["wrapper"]) for v in r["consumers"]["via_wrapper"]) or "NONE outside techne/"))
        o.append("  blockers    %s" % ("; ".join(r["blockers"]) or "none"))
        o.append("  notes       %s" % r["notes"])
        o.append("  labels      %s" % ", ".join(r["labels"]))
    return "\n".join(o) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="techne/acquisition/DONOR_DISPOSITION.json")
    ap.add_argument("--txt", default=None)
    a = ap.parse_args(argv)
    doc = build()
    pathlib.Path(a.out).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    txt = render(doc)
    if a.txt:
        pathlib.Path(a.txt).write_text(txt, encoding="utf-8", newline="\n")
    print(txt.split("\n\n")[0])
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
