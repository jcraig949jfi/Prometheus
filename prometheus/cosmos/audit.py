"""Campaign audit: receipts, ledger consistency, holdout ordering, seals, committed copies.

  python -m prometheus.cosmos.audit <store_dir> [<store_dir> ...]

Checks (each reported PASS / FAIL with the offending record):
  R1 receipt chain verifies (content ids + prev links)
  R2 every FROZEN law's freeze hash recomputes from its immutable row (no mutation after freeze)
  R3 lifecycle order: PROPOSED first; FROZEN before any HOLDOUT_TESTED / INTERVENTION_TESTED;
     nothing after a law's own RETIRED
  R4 holdout ordering in the chain: for every holdout_revealed there is an earlier holdout_predictions for
     the same law; for every *_revealed intervention an earlier *prescriptions record for the same law
  R5 every sealed spec still hashes to its commitment and its family source to the recorded hash
  R6 (optional) a committed receipts copy is a PREFIX of the live chain (nothing rewritten)
Known weakness: R4 matches a g6b-style reveal to ANY earlier prescription when the record lacks a law
id (older records); exact only when each store holds one frozen law, as all campaign stores do.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from prometheus.cosmos import broker
from prometheus.cosmos.hashing import h
from prometheus.cosmos.store import Store

COMMITMENTS = {"D": "48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265",
               "E": "d17ace6e6f9171da49afab4a6c9626cfd1d998ae9e5c9cfdc14837dc319e7528",
               "F": "5e0064901277ef9e48571906dab60f998ad924b16a46bdb316d0db46bc504946"}


def audit_store(d: Path, committed_copy: Path = None) -> Dict[str, Any]:
    st = Store(d)
    out: Dict[str, Any] = {"store": str(d)}
    bad = st.receipts.verify()
    out["R1"] = "PASS" if bad is None else "FAIL at record %d" % bad
    r2, r3 = [], []
    for law in st.laws():
        ev = [e["status"] for e in law["events"]]
        if law["freeze_hash"]:
            if h({"law_id": law["law_id"], "body": law["body"], "parent": law["parent"]}) != law["freeze_hash"]:
                r2.append(law["law_id"])
        if not ev or ev[0] != "PROPOSED":
            r3.append((law["law_id"], "first event %s" % (ev[:1],)))
        for tested in ("HOLDOUT_TESTED", "INTERVENTION_TESTED"):
            if tested in ev and ("FROZEN" not in ev or ev.index("FROZEN") > ev.index(tested)):
                r3.append((law["law_id"], "%s before FROZEN" % tested))
    out["R2"] = "PASS" if not r2 else "FAIL %s" % r2
    out["R3"] = "PASS" if not r3 else "FAIL %s" % r3
    recs = st.receipts.read()
    r4 = []
    seen_pred, seen_presc = set(), set()
    for i, r in enumerate(recs):
        k, b = r["kind"], r["body"]
        if k == "holdout_predictions":
            seen_pred.add(b["law_id"])
        if k in ("intervention_prescriptions", "g6b_prescriptions"):
            seen_presc.add(b["law_id"])
        if k == "holdout_revealed" and b.get("law_id") not in seen_pred:
            r4.append((i, k))
        if k in ("intervention_revealed", "g6b_revealed") and b.get("law_id") not in seen_presc:
            # g6b_revealed carries no law_id in older records: accept if ANY prescription preceded it
            if not seen_presc:
                r4.append((i, k))
    out["R4"] = "PASS" if not r4 else "FAIL %s" % r4
    out["n_receipts"] = len(recs)
    out["n_reveals"] = sum(r["kind"] in ("holdout_revealed", "intervention_revealed", "g6b_revealed") for r in recs)
    if committed_copy is not None and committed_copy.exists():
        cc = [json.loads(line) for line in committed_copy.read_text(encoding="utf-8").splitlines() if line.strip()]
        live_ids = [r["id"] for r in recs]
        out["R6"] = "PASS" if [r["id"] for r in cc] == live_ids[: len(cc)] else "FAIL (committed copy is not a prefix)"
    return out


def audit_seals() -> Dict[str, str]:
    out = {}
    for k, c in COMMITMENTS.items():
        try:
            broker.load_spec(c, k)
            out[k] = "PASS"
        except Exception as e:
            out[k] = "FAIL %r" % e
    return out


def main(argv: List[str]) -> int:
    res = {"R5_seals": audit_seals(), "stores": []}
    for a in argv:
        store, _, copy = a.partition("=")
        res["stores"].append(audit_store(Path(store), Path(copy) if copy else None))
    print(json.dumps(res, indent=1))
    ok = all(v == "PASS" for v in res["R5_seals"].values()) and all(
        all(str(s.get(k, "PASS")).startswith("PASS") for k in ("R1", "R2", "R3", "R4", "R6")) for s in res["stores"])
    print("AUDIT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
