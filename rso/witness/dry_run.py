"""End-to-end DRY RUN of the witness machinery (C-010-T013). Plumbing only: two TINY subject runs (P=4, G=1) stand
in for the registered ones, a temp ledger and contract, a fixture keeper store. It prints STRUCTURE only (bundles,
refusals, custody, which gates were evaluated, binding of every receipt); outcome values of these stand-in
subjects are not printed and mean nothing. Usage: python -B -m rso.witness.dry_run [--keep DIR]"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile

from rso.binding import binding as B
from rso.slice001 import evidence as EV
from rso.slice001 import ledger as L
from rso.witness import evaluate as EVW
from rso.witness import make_configs as MC
from rso.witness import run_witness as RW


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run(root):
    s4, s15 = os.path.join(root, "S4"), os.path.join(root, "S15")
    RW.run_subject("W4", "present", {}, 4, 1, 2, 101, s4)
    RW.run_subject("W15", "present", {}, 4, 1, 2, 102, s15)
    cfgdir = os.path.join(root, "configs")
    summary = MC.build(s4, s15, cfgdir)
    contract = os.path.join(root, "contract.json")
    json.dump({"caps": {"top_level_validation_launches": 10, "cpu_minutes": 600, "new_artifact_mb": 2000}}, open(contract, "w"))
    led = L.Ledger.from_contract(os.path.join(root, "ledger.jsonl"), contract)
    bundles = []
    for label in ("CONTROLS", "S4", "S15"):
        out = os.path.join(root, "bundle_" + label)
        res = RW.launch(os.path.join(cfgdir, summary["configs"][label]), led, out, code_commit="0" * 40)
        bundles.append(out)
        print("launch", label, res["status"], res["nodes"], "nodes")
    reg = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    first = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for b in bundles:
        for kind, f in (("EVIDENCE_MANIFEST", "MANIFEST.json"), ("RUN_INVENTORY", "inventory.json")):
            rows.append({"row_id": len(rows) + 1, "record_kind": kind, "blob_sha256": _sha(os.path.join(b, f)),
                         "registered_at_utc": reg, "registrar": "dry-run fixture", "repo_path": f, "commit_sha": "0" * 40})
    store = EV.FixtureStore(rows)
    for b in bundles:
        man = json.load(open(os.path.join(b, "MANIFEST.json")))
        inv = json.load(open(os.path.join(b, "inventory.json")))["rows"]
        bad = []
        for n in man["nodes"]:
            data = open(os.path.join(b, n["receipt_file"]), "rb").read()
            why = B.binding_reasons(n["node_id"], n["run_id"], data, inv[:-1], man["launch_run_id"])
            if why:
                bad.append((n["node_id"], why))
        print("binding", os.path.basename(b), "nodes", len(man["nodes"]), "unbound", bad)
    subjects = {"S4": json.load(open(os.path.join(s4, "subject_record.json")))["genome_sha256"],
                "S15": json.load(open(os.path.join(s15, "subject_record.json")))["genome_sha256"]}
    res = EVW.evaluate(bundles, store, first, subjects, "S4", seed_lists=json.load(open(os.path.join(cfgdir, "SEED_LISTS.json")))["seeds"])
    shape = {}
    for k, v in res.items():
        if isinstance(v, dict):
            shape[k] = sorted(v.keys())
        elif isinstance(v, list):
            shape[k] = "list[%d]" % len(v)
        else:
            shape[k] = type(v).__name__
    print("evaluate keys", json.dumps(shape, sort_keys=True)[:1500])
    for b in res.get("bundles", []):
        print("bundle", b.get("bundle"), "refused", b.get("refused"), "custody", (b.get("custody") or {}).get("status"))
    for name in ("S4", "S15"):
        sub = (res.get("subjects") or {}).get(name) or {}
        print("subject", name, "gates evaluated", sorted(k for k in sub if k.startswith("P-")), "has class", "class" in sub,
              "why" if sub.get("class") == "UNQUALIFIED" else "", sub.get("why") if sub.get("class") == "UNQUALIFIED" else "")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep")
    a = ap.parse_args(argv)
    root = a.keep or tempfile.mkdtemp(prefix="witness-dry-")
    try:
        run(root)
    finally:
        if not a.keep:
            shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
