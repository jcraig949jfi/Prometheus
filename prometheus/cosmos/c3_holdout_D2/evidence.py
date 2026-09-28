"""Holdout D2 evidence bundle for adjudication (Harmonia), built on M1 after the result seal.

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.evidence --run RUN_DIR --out DIR [--revealed DIR] [--ref origin/main]

Refused unless protocol.check_gates(..., "RESULT_SEAL") passes, the run's receipt chain verifies and ends at the
sealed chain head, and RESULT.json hashes to the sealed result hash. So no bundle (and no result) can leave M1
before the results are sealed.

The bundle (DIR, outside every git repository) holds:
- the committed protocol records, the manifest and the ciphertext, read from the reference branch;
- receipts.jsonl and RESULT.json, copied;
- GATES.json: the gate status, with the commit of every record, showing the enforced order;
- RECEIPTS_VERIFY.json;
- REVEAL_VERIFY.json, only with --revealed (a directory produced by custody.py reveal): verify_reveal on the
  published plaintext/salt/key, including the redraw from the nonce;
- INDEX.json: sha256 of every file in the bundle.
The prediction package is inside the run directory (package/), already hash-bound by the receipts.
"""
from __future__ import annotations

import os

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 evidence: set COSMOS_BROKER=1 (broker only)")

import argparse
import json
import shutil
import sys
from pathlib import Path

from prometheus.cosmos.c3_holdout_D2 import protocol, sealbox

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[2]


class EvidenceRefusal(Exception):
    pass


def _inside_git(p: Path) -> bool:
    p = Path(p).resolve()
    return any((q / ".git").exists() for q in [p] + list(p.parents))


def build(run_dir, out_dir, revealed_dir=None, repo=DEFAULT_REPO, ref=protocol.DEFAULT_REF, host=None,
          allowlist=None, pins=None, verify_loaded=True) -> dict:
    from prometheus.cosmos.c3_holdout_D2 import runner, verify_reveal
    run_dir, out = Path(run_dir), Path(out_dir)
    if _inside_git(out):
        raise EvidenceRefusal("bundle directory is inside a git repository")
    if out.exists() and any(out.iterdir()):
        raise EvidenceRefusal("bundle directory is not empty")
    g = protocol.check_gates(repo, "RESULT_SEAL", ref=ref, host=host, pins=pins, verify_loaded=verify_loaded,
                             allowlist=protocol.DEFAULT_ALLOWLIST if allowlist is None else allowlist)
    ok, recs, why = runner.verify_receipts(run_dir / "receipts.jsonl")
    if not ok or not recs or recs[-1]["kind"] != "close" or recs[-1]["hash"] != g["chain_head"]:
        raise EvidenceRefusal("receipts do not verify or do not end at the sealed chain head (%s)" % why)
    if sealbox.sha256_file(run_dir / "RESULT.json") != g["result_sha256"]:
        raise EvidenceRefusal("RESULT.json does not match the sealed result hash")
    out.mkdir(parents=True, exist_ok=True)
    (out / "protocol").mkdir()
    for name in [n for n in protocol._proto_tree(repo, ref)]:            # every record, incl. every audit version
        (out / "protocol" / name).write_bytes(protocol._show(repo, ref, protocol.PROTO_REL + "/" + name))
    for name in ("MANIFEST_D2.json", "hidden_D2.enc"):
        (out / name).write_bytes(protocol._show(repo, ref, protocol.PKG_REL + "/" + name))
    shutil.copy2(run_dir / "receipts.jsonl", out / "receipts.jsonl")
    shutil.copy2(run_dir / "RESULT.json", out / "RESULT.json")
    (out / "GATES.json").write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "RECEIPTS_VERIFY.json").write_text(json.dumps({"ok": ok, "reason": why, "n_records": len(recs),
                                                          "head": recs[-1]["hash"]}, indent=1) + "\n", encoding="utf-8")
    if revealed_dir is not None:
        rd = Path(revealed_dir)
        chk = verify_reveal.verify((rd / "hidden_D2.plain.json").read_bytes(),
                                   sealbox.read_hex_file(rd / "hidden_D2.salt.hex", 32),
                                   sealbox.read_hex_file(rd / "hidden_D2.key.hex", sealbox.KEY_BYTES),
                                   json.loads((out / "MANIFEST_D2.json").read_text(encoding="utf-8")),
                                   (out / "hidden_D2.enc").read_bytes(), redraw=True)
        (out / "REVEAL_VERIFY.json").write_text(json.dumps(chk, indent=1) + "\n", encoding="utf-8")
    index = {str(p.relative_to(out)).replace("\\", "/"): sealbox.sha256_file(p)
             for p in sorted(out.rglob("*")) if p.is_file()}
    (out / "INDEX.json").write_text(json.dumps(index, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return {"bundle": str(out), "n_files": len(index) + 1, "chain_head": g["chain_head"],
            "revealed": revealed_dir is not None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="holdout D2 evidence bundle (Harmonia)")
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--revealed")
    ap.add_argument("--ref", default=protocol.DEFAULT_REF)
    a = ap.parse_args(argv)
    try:
        r = build(a.run, a.out, a.revealed, ref=a.ref)
    except (protocol.GateRefusal, EvidenceRefusal) as e:
        print(json.dumps({"refused": True, "reason": "%s: %s" % (type(e).__name__, e)}))
        return 3
    print(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
