#!/usr/bin/env python3
"""Prepare assessor runs for a sealed evaluation set.

This is measurement scaffolding, not an epoch runner. It assembles one frozen
ASSESSOR prompt per claim under a given condition, copies the PUBLIC claim
package next to it, and creates an empty run directory for the submission.

It never touches `sealed/`. The sealed record is read only by `score.py`, after
submissions exist.

  python prepare.py --set ../heldout/A0_EVAL --condition A
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--set", required=True)
    p.add_argument("--condition", default="A", choices=list("ABCD"))
    args = p.parse_args()

    src = Path(args.set).resolve()
    set_name = src.name
    out = HERE / set_name
    if out.exists():
        shutil.rmtree(out)
    (out / "prompts").mkdir(parents=True)
    (out / "runs").mkdir(parents=True)

    index = []
    for claim_path in sorted((src / "public").glob("*.json")):
        claim = json.loads(claim_path.read_text(encoding="utf-8"))
        cid = claim["claim_id"]
        run_dir = out / "runs" / cid
        run_dir.mkdir()
        local_claim = run_dir / "claim.json"
        shutil.copyfile(claim_path, local_claim)

        vars_path = run_dir / "_vars.json"
        vars_path.write_text(json.dumps({
            "RUN_ID": f"A0-{cid}",
            "CONDITION": args.condition,
            "CLAIM_ID": cid,
            "CLAIM_PATH": str(local_claim).replace("\\", "/"),
            "PROBLEM_PATH": claim["problem_id"],
            "SUBMISSION_DIR": str(run_dir).replace("\\", "/"),
        }, indent=2) + "\n", encoding="utf-8")

        prompt_path = out / "prompts" / f"{cid}.md"
        r = subprocess.run(
            [sys.executable, str(ARENA / "prompts" / "assemble.py"), "assemble",
             "--role", "ASSESSOR", "--condition", args.condition,
             "--vars", str(vars_path), "--out", str(prompt_path)],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr, file=sys.stderr)
            return 1
        manifest = json.loads(r.stdout)

        # append the claim itself so the seat has one file to read
        with prompt_path.open("a", encoding="utf-8") as fh:
            fh.write("\n\n---\n\n## The claim under assessment\n\n")
            fh.write("```json\n")
            fh.write(json.dumps(claim, indent=2))
            fh.write("\n```\n")

        index.append({
            "claim_id": cid,
            "prompt": str(prompt_path).replace("\\", "/"),
            "run_dir": str(run_dir).replace("\\", "/"),
            "submission": str(run_dir / "disposition.json").replace("\\", "/"),
            "invariant_sha256": manifest["invariant_sha256"],
            "context_sha256": manifest["context_sha256"],
        })

    inv = {i["invariant_sha256"] for i in index}
    ctx = {i["context_sha256"] for i in index}
    idx = {
        "set_name": set_name,
        "condition": args.condition,
        "count": len(index),
        "invariant_sha256": sorted(inv),
        "context_sha256": sorted(ctx),
        "parity_ok": len(inv) == 1 and len(ctx) == 1,
        "runs": index,
    }
    (out / "INDEX.json").write_text(json.dumps(idx, indent=2) + "\n",
                                    encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in idx.items() if k != "runs"}, indent=2))
    return 0 if idx["parity_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
