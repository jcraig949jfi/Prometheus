"""Coverage map of the fossil bed (batch 06+ standing tool). MECHANICAL and transparent: counts over
the tracked records, several overlapping views, and a sparsity signal that is a plain rule -- never a
learned classifier, never a judgement of what the machinery means. Its only purpose is to show where
the vault is thin so the next harvest digs there (charter: "classify only enough to dig better").

    python -m techne.fossils.coverage            human-readable
    python -m techne.fossils.coverage --json [--out F]   the coverage artifact

Views: domain, decade, language, execution-model (runner+image), runnability, failure/disposition,
ancestry-relation. A fossil appears in every cell it belongs to (no forced hierarchy). Unknown is a
legal cell; guessing is not (only recorded fields are read).
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import time

from . import catalog, vault


def _decade(era: str) -> str:
    m = re.search(r"(1[89]\d\d|20\d\d)", era or "")
    return m.group(1)[:3] + "0s" if m else "unknown"


def _disposed(r) -> bool:
    """A fossil counts as carrying a failed/superseded disposition when either the explicit P7
    state says so, or the older acquisition tags do. Mechanical; no inference from age."""
    st = (r.get("historical_disposition") or {}).get("state", "UNKNOWN")
    if st not in ("ACTIVE", "UNKNOWN", None, ""):
        return True
    return bool(r.get("known_historical_disposition"))


def build() -> dict:
    rows = catalog.enumerate_fossils()
    n = len(rows)
    runnable = lambda r: str(r["run_status"]).startswith("RUNNABLE")

    def tally(keyfn):
        cells = collections.defaultdict(lambda: {"specimens": 0, "runnable": 0, "oracle_backed": 0,
                                                 "failed_or_superseded": 0, "eras": set(), "languages": set()})
        for r in rows:
            for k in keyfn(r):
                c = cells[k]
                c["specimens"] += 1
                c["runnable"] += runnable(r)
                c["oracle_backed"] += (r.get("oracle_backed") == "yes")
                c["failed_or_superseded"] += _disposed(r)
                c["eras"].add(_decade(r.get("era", "")))
                for l in (r.get("language") or []):
                    c["languages"].add(l.split(" (")[0].strip())
        out = {}
        for k, c in cells.items():
            out[k] = {"specimens": c["specimens"], "runnable": c["runnable"], "oracle_backed": c["oracle_backed"],
                      "failed_or_superseded": c["failed_or_superseded"], "era_diversity": len(c["eras"]),
                      "language_diversity": len(c["languages"])}
        return dict(sorted(out.items(), key=lambda kv: -kv[1]["specimens"]))

    views = {
        "domain": tally(lambda r: r.get("domain") or ["(none)"]),
        "decade": tally(lambda r: [_decade(r.get("era", ""))]),
        "language": tally(lambda r: [l.split(" (")[0].strip() for l in (r.get("language") or ["(none)"])]),
        "execution_model": tally(lambda r: [((r_env := None) or _exec_model(r))]),
        "runnability": tally(lambda r: [r.get("run_status") or "(none)"]),
        "disposition": tally(lambda r: ([ (r.get("historical_disposition") or {}).get("state") ]
                                        if _disposed(r) else ["(none recorded)"])),
        "failure_reason": tally(lambda r: ((r.get("historical_disposition") or {}).get("failure_reasons")
                                           or ["(none recorded)"])),
        "ancestry_relation": tally(lambda r: [e.get("relation", "?") for e in (r.get("ancestry") or [])] or ["(none)"]),
    }

    # transparent sparsity signal per DOMAIN cell: a point for each thin condition it meets.
    sparse = []
    for dom, c in views["domain"].items():
        if dom == "(none)":
            continue
        score = ((c["specimens"] <= 2) + (c["era_diversity"] <= 1) + (c["language_diversity"] <= 1)
                 + (c["runnable"] == 0) + (c["failed_or_superseded"] == 0))
        sparse.append({"domain": dom, "sparsity": score, **c})
    sparse.sort(key=lambda d: (-d["sparsity"], d["specimens"]))

    return {"schema": "techne.fossil.coverage/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_specimens": n, "runnable": sum(1 for r in rows if runnable(r)),
            "oracle_backed": sum(1 for r in rows if r.get("oracle_backed") == "yes"),
            "with_failed_or_superseded_disposition": sum(1 for r in rows if _disposed(r)),
            "sparsity_rule": "per domain: +1 for each of {<=2 specimens, <=1 decade, <=1 language, 0 runnable, 0 failed/superseded}; higher = thinner. Mechanical, not a judgement of value.",
            "views": views, "sparsest_domains": sparse[:20],
            "note": "coverage of the source corpus only; NOT behavioral organs, equivalence, or a taxonomy of cognition (those are Nyx's). A fossil is counted in every cell it belongs to."}


def _exec_model(r: dict) -> str:
    # execution model proxy from the recorded run world; unknown stays unknown.
    rc = r.get("run_status", "")
    if rc == "RUNNABLE_EMULATED":
        return "emulated (HDL/VM)"
    if rc == "RUNNABLE_HISTORICAL_TOOLCHAIN":
        return "historical-toolchain"
    if rc == "SOURCE_ONLY":
        return "source-only (not executed)"
    if rc == "RUNNABLE_NATIVE":
        return "native"
    if rc == "RUNNABLE_CONTAINER":
        return "container"
    return "other/" + (rc or "unknown")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    c = build()
    if a.json or a.out:
        t = json.dumps(c, indent=1)
        if a.out:
            pathlib.Path(a.out).write_text(t + "\n", encoding="utf-8", newline="\n")
            print("coverage", a.out, c["total_specimens"], "specimens")
        else:
            print(t)
    else:
        print("total %d  runnable %d  oracle-backed %d  with-disposition %d\n" % (
            c["total_specimens"], c["runnable"], c["oracle_backed"], c["with_failed_or_superseded_disposition"]))
        for view, cells in c["views"].items():
            print("== %s (%d cells)" % (view, len(cells)))
            for k, cc in list(cells.items())[:12]:
                print("   %-28s n=%-3d run=%-3d oracle=%-3d disp=%-2d eras=%d langs=%d" % (
                    k[:28], cc["specimens"], cc["runnable"], cc["oracle_backed"],
                    cc["failed_or_superseded"], cc["era_diversity"], cc["language_diversity"]))
        print("\n== sparsest domains (mechanical)")
        for d in c["sparsest_domains"][:15]:
            print("   %-26s sparsity=%d n=%d run=%d disp=%d eras=%d langs=%d" % (
                d["domain"][:26], d["sparsity"], d["specimens"], d["runnable"],
                d["failed_or_superseded"], d["era_diversity"], d["language_diversity"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
