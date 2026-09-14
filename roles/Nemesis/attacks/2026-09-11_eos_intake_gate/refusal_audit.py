"""EOS-30 second opinion: classify the Eos first-season refusal corpus by CAUSE.

Reproduces every number in SECOND_OPINION_EOS30.md from Eos's own committed
ledger. Reads only; nothing of Eos's is modified.

    python roles/Nemesis/attacks/2026-09-11_eos_intake_gate/refusal_audit.py
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402

LEDGER = REPO / "roles" / "Eos" / "intake" / "ledger_2026-09-11.json"
OUT = HERE / "refusal_audit.json"


def main() -> int:
    assert_not_canonical()
    if not LEDGER.is_file():
        print("ledger not present in this worktree:", LEDGER)
        return 2
    d = json.loads(LEDGER.read_text(encoding="utf-8"))
    vs = d["verdicts"]
    refused = [v for v in vs if v["state"] == "REFUSED"]

    signatures = collections.Counter(
        tuple(sorted(c["name"] for c in v["checks"] if not c["passed"])) for v in refused)

    path_missing = 0
    self_named = 0
    prefixes = collections.Counter()
    for v in refused:
        claim = v.get("claim") or {}
        ref = claim.get("referent", "") or ""
        path = ref.split("#", 1)[0] if "#" in ref else ref
        if path:
            prefixes["/".join(path.split("/")[:2])] += 1
        if "no such file in the repository" in v["reason"]:
            path_missing += 1
            stem = path.rsplit("/", 1)[-1]
            if stem.endswith(".md"):
                stem = stem[:-3]
            # the referent file is NAMED AFTER THE ITEM: the verdict was
            # fixed by the claim constructor, not by the item's content
            if stem and stem in v["item_id"]:
                self_named += 1

    result = {
        "audited": str(LEDGER.relative_to(REPO)).replace(os.sep, "/"),
        "workspace": receipt(),
        "total_verdicts": len(vs),
        "counts": d["counts"],
        "refused": len(refused),
        "refused_missing_referent_file": path_missing,
        "of_those_referent_named_after_the_item": self_named,
        "referent_directory_prefixes": prefixes.most_common(),
        "refusal_signatures": [{"failed_checks": list(k), "n": n}
                               for k, n in signatures.most_common()],
        "research_frontier_exists": (REPO / "research" / "frontier").is_dir(),
        "research_exists": (REPO / "research").is_dir(),
    }
    for k in ("total_verdicts", "refused", "refused_missing_referent_file",
              "of_those_referent_named_after_the_item"):
        print("{:45s} {}".format(k, result[k]))
    print("research/frontier exists:", result["research_frontier_exists"],
          "| research/ exists:", result["research_exists"])
    for row in result["refusal_signatures"]:
        print("  {:60s} {}".format(str(row["failed_checks"]), row["n"]))

    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=2)
        fh.flush()
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
