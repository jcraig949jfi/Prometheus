"""Ranked preservation-debt queue for the network-dependent recipes (batch 10 P7).

The charter forbids repairing all of them in one batch and asks instead for a RANKING by
scientific/forensic value and preservation risk, answering for each external dependency:

    CAN THIS EXACT BODY BE RECONSTRUCTED WITHOUT TRUSTING MOVING HEAD?

For these fossils the BODY is pinned and verified; what is not pinned is the WORLD the oracle runs
in. P5 showed that is not a bookkeeping distinction: the same preserved bytes give a different
answer when the environment moves, silently and with exit 0.

    python -m techne.fossils.preservation_queue [--out F]

The score is a plain additive rule, printed with the artifact. It is a dig-order, not a judgement.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import time

from . import catalog, record, vault

NUMERICAL = ("numpy", "scipy", "matplotlib", "pandas", "sympy", "statsmodels")


def assess(sid: str, cat_row: dict) -> dict:
    rp = vault.specimen_dir(sid) / "recipe.json"
    txt = rp.read_text(encoding="utf-8", errors="ignore") if rp.exists() else ""
    pip = re.findall(r"pip3?\s+install[^\"']{0,160}", txt)
    apt = bool(re.search(r"apt-get\s+(?:-\S+\s+)*install", txt))
    version_pinned = bool(re.search(r"==\s*\d", " ".join(pip)))
    numerical = sorted({n for n in NUMERICAL if re.search(r"\b%s\b" % n, " ".join(pip))})

    rec = record.load(sid)
    hd = rec.get("historical_disposition") or {}
    disposed = hd.get("state") not in ("ACTIVE", "UNKNOWN", None, "")

    risk, why_risk = 0, []
    if pip and not version_pinned:
        risk += 3; why_risk.append("pip install with NO version pin (PyPI is a moving target)")
    if numerical:
        risk += 2; why_risk.append("floating NUMERICAL dependency (%s): P5 showed a moving world can "
                                   "change an answer silently" % ",".join(numerical))
    if apt:
        risk += 1; why_risk.append("apt-get install from a moving distro index")
    if pip and version_pinned:
        risk += 1; why_risk.append("pip pinned by version but not by hash")

    value, why_value = 0, []
    if cat_row.get("oracle_backed") == "yes":
        value += 2; why_value.append("oracle-backed: its evidence DEPENDS on the run reproducing")
    if disposed:
        value += 2; why_value.append("carries an evidence-backed historical disposition (%s)" % hd.get("state"))
    if cat_row.get("intervention_ready") == "yes":
        value += 1; why_value.append("intervention-ready (downstream perturbation target)")
    doms = cat_row.get("domain") or []
    if any(d in ("estimation", "control", "inference") for d in doms):
        value += 1; why_value.append("in a behaviourally-exercised area (estimation/control/inference)")

    return {"specimen_id": sid, "risk": risk, "value": value, "priority": risk + value,
            "pip": bool(pip), "version_pinned": version_pinned, "apt": apt,
            "floating_numerical": numerical, "oracle_backed": cat_row.get("oracle_backed"),
            "disposition": hd.get("state", "UNKNOWN"),
            "reconstructible_without_moving_head": bool(version_pinned and not numerical) if pip else (not apt),
            "why_risk": why_risk, "why_value": why_value}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    census = json.loads((pathlib.Path("techne/fossils/PRESERVATION_CENSUS_2026-09-13.json"))
                        .read_text(encoding="utf-8"))
    net = [r["specimen_id"] for r in census["rows"] if r.get("recipe_status") == "NETWORK_DEPENDENT"]
    cat = {r["fossil_id"]: r for r in catalog.enumerate_fossils()}
    rows = sorted((assess(s, cat.get(s, {})) for s in net),
                  key=lambda r: (-r["priority"], -r["risk"], r["specimen_id"]))

    doc = {"schema": "techne.fossil.preservation_queue/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "question": "CAN THIS EXACT BODY BE RECONSTRUCTED WITHOUT TRUSTING MOVING HEAD?",
           "n_network_dependent": len(rows),
           "reconstructible_without_moving_head": sum(1 for r in rows if r["reconstructible_without_moving_head"]),
           "rule": {"risk": "+3 unpinned pip, +2 floating numerical dep, +1 apt index, +1 pip pinned by "
                            "version but not hash",
                    "value": "+2 oracle-backed, +2 evidence-backed disposition, +1 intervention-ready, "
                             "+1 estimation/control/inference",
                    "priority": "risk + value; ties broken by risk then id"},
           "note": "For these fossils the BODY is pinned and verifies; the WORLD is not. That is the same "
                   "failure class P5 demonstrated, not a bookkeeping nicety. This is a dig-order, not a "
                   "judgement of the software.",
           "rows": rows}
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("network-dependent: %d   reconstructible without trusting a moving head: %d"
          % (len(rows), doc["reconstructible_without_moving_head"]))
    print("%-34s %4s %5s %5s  %s" % ("specimen", "pri", "risk", "value", "floating numerical"))
    for r in rows:
        print("%-34s %4d %5d %5d  %s" % (r["specimen_id"], r["priority"], r["risk"], r["value"],
                                         ",".join(r["floating_numerical"]) or "-"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
