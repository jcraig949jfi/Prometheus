#!/usr/bin/env python3
"""Prepare metered assessor runs for a navigation set.

Assembles one prompt per claim, opens a metered session for each, and creates
the run directory. Never touches `sealed/` — that is read only by `score_nav.py`
after submissions exist.

  python prepare_nav.py --set ../heldout/NAV_PILOT --budget 120
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
CLI = ARENA / "verifier" / "meter_cli.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True)
    ap.add_argument("--budget", type=int, default=120)
    ap.add_argument("--condition", default="A")
    args = ap.parse_args()

    src = Path(args.set).resolve()
    name = src.name
    out = HERE / f"{name}_RUN"
    if out.exists():
        shutil.rmtree(out)
    (out / "prompts").mkdir(parents=True)
    (out / "runs").mkdir(parents=True)
    # keep prior sessions: the v0.2 run's ledgers are evidence and are read by
    # its report. Only this set's sessions are reset.

    role = (ARENA / "prompts" / "ROLE_ASSESSOR_NAV.md").read_text(encoding="utf-8")
    common = (ARENA / "prompts" / "00_COMMON_PREAMBLE.md").read_text(encoding="utf-8")
    budget_cfg = json.loads(
        (ARENA / "prompts" / "budget.json").read_text(encoding="utf-8"))

    index = []
    for cp in sorted((src / "public").glob("*.json")):
        claim = json.loads(cp.read_text(encoding="utf-8"))
        cid = claim["claim_id"]
        run_dir = out / "runs" / cid
        run_dir.mkdir()
        shutil.copyfile(cp, run_dir / "claim.json")
        sid = f"A0{name}-{cid}"

        r = subprocess.run(
            [sys.executable, str(CLI), "open", "--claim", cid, "--seat", sid,
             "--budget", str(args.budget), "--set", str(src)],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr, file=sys.stderr)
            return 1

        text = common
        for k, v in {"BUDGET_TOKENS": budget_cfg["BUDGET_TOKENS"],
                     "BUDGET_WALL_SECONDS": budget_cfg["BUDGET_WALL_SECONDS"],
                     "BUDGET_VERIFIER_CALLS": args.budget,
                     "BUDGET_SEARCH_SIZE": args.budget}.items():
            text = text.replace("{{" + k + "}}", str(v))
        body = role
        for k, v in {"RUN_ID": f"A0NAV-{cid}", "CONDITION": args.condition,
                     "CLAIM_ID": cid, "SESSION_ID": sid,
                     "CLAIM_PATH": str(run_dir / "claim.json").replace("\\", "/"),
                     "SUBMISSION_DIR": str(run_dir).replace("\\", "/"),
                     "METER_CLI": str(CLI).replace("\\", "/")}.items():
            body = body.replace("{{" + k + "}}", str(v))

        prompt = (text + "\n\n---\n\n" + body + "\n\n---\n\n"
                  "## The claim under assessment\n\n```json\n"
                  + json.dumps(claim, indent=2) + "\n```\n")
        pp = out / "prompts" / f"{cid}.md"
        pp.write_text(prompt, encoding="utf-8", newline="\n")
        index.append({"claim_id": cid, "prompt": str(pp).replace("\\", "/"),
                      "run_dir": str(run_dir).replace("\\", "/"),
                      "session": sid,
                      "submission": str(run_dir / "disposition.json").replace("\\", "/")})

    idx = {"set_name": name, "condition": args.condition, "budget": args.budget,
           "count": len(index), "runs": index}
    (out / "INDEX.json").write_text(json.dumps(idx, indent=2) + "\n",
                                    encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in idx.items() if k != "runs"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
