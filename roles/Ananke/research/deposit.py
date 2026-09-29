"""Deposit a delegated worker's report verbatim, with provenance (ARC3 Block M).

Problem: delegated subagents may write scratch files but the harness refuses
their report writes ("subagents return findings as text"). Workers must not
get repository authority (no commits). Solution, the smallest that
preserves provenance, identity and immutability, with principal review:

  worker   puts the report between ===BEGIN REPORT=== / ===END REPORT===
           in its FINAL MESSAGE (handoffs/COMMON_RULES_ARC3.md s1)
  principal saves that final message to a file and runs
      python roles/Ananke/research/deposit.py <worker_id> <message_file> [--source <task/transcript id>]
  deposit  extracts the delimited block byte-for-byte and writes
      workers/<id>/REPORT.md          (the report, verbatim, plus a provenance header)
      workers/<id>/REPORT.provenance.json
           {worker, sha256 of the raw block, sha256 of the full message,
            source, deposited_at_utc, depositor}
           and REFUSES to overwrite an existing REPORT.md (immutable; a
           correction is a new REPORT.v2.md with its own provenance).
  review   the principal commits it; the integration (backlog, synthesis) is
           a separate, reviewed commit.
If the delimiters are missing, the whole message is deposited and flagged
"undelimited".
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BEGIN, END = "===BEGIN REPORT===", "===END REPORT==="


def deposit(worker: str, message: str, source: str = "", depositor: str = "Ananke") -> pathlib.Path:
    d = HERE / "workers" / worker
    d.mkdir(parents=True, exist_ok=True)
    n = 1
    target = d / "REPORT.md"
    while target.exists():
        n += 1
        target = d / f"REPORT.v{n}.md"
    if BEGIN in message and END in message:
        block = message.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")
        mode = "delimited"
    else:
        block, mode = message, "undelimited"
    prov = {"worker": worker, "mode": mode,
            "sha256_report": hashlib.sha256(block.encode("utf-8")).hexdigest(),
            "sha256_message": hashlib.sha256(message.encode("utf-8")).hexdigest(),
            "source": source, "depositor": depositor,
            "deposited_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "file": target.name}
    header = (f"<!-- DEPOSITED VERBATIM by {depositor} for worker {worker}; "
              f"sha256(report)={prov['sha256_report'][:16]}; {mode}; see "
              f"{target.stem}.provenance.json -->\n")
    target.write_text(header + block + "\n", encoding="utf-8", newline="\n")
    (d / f"{target.stem}.provenance.json").write_text(json.dumps(prov, indent=1) + "\n")
    return target


def verify(path: pathlib.Path) -> bool:
    prov = json.loads(path.with_name(path.stem + ".provenance.json").read_text())
    body = path.read_text(encoding="utf-8").split("\n", 1)[1].rstrip("\n")
    return hashlib.sha256(body.encode("utf-8")).hexdigest() == prov["sha256_report"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("worker")
    ap.add_argument("message_file")
    ap.add_argument("--source", default="")
    a = ap.parse_args()
    msg = pathlib.Path(a.message_file).read_text(encoding="utf-8")
    p = deposit(a.worker, msg, a.source)
    print(p, "verified" if verify(p) else "HASH MISMATCH")
