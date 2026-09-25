"""File the defects the independent replication lane exposed.

Four of these are in code I wrote or froze, and one is in my own brief. They were
found by an executor that had never seen the code, which is the argument for the
lane existing at all.

Appends rather than rewriting, so the 44 committed entries cannot churn.
"""
from __future__ import annotations

import json
import pathlib
import re
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
LEDGER = BASE / "DEFECTS.jsonl"

NEW = [
 {"severity": "high", "category": "instrument",
  "title": "selfcheck_e05.py is self-invalidating: S9 asserts a subtree it writes into",
  "evidence": "selfcheck_e05.py writes SELFCHECK.json INTO the campaign subtree whose cleanliness "
              "S9 asserts, and reads `git status --porcelain -- <subtree>` at startup. First run on a "
              "clean tree passes 9/9 and EXECUTE ADMISSIBLE: YES; that very write makes the SECOND run "
              "fail S9 and report ADMISSIBLE: NO. The receipt also embeds commit_sha and branch, so on "
              "any branch but the canonical one its content necessarily differs. An independent "
              "executor who runs it twice sees a red gate that is an artifact of the checker. Found by "
              "the replication lane (P2), not by me.",
  "proposed_fix": "Write the receipt OUTSIDE the verified subtree, or exclude the receipt path from the "
                  "S9 status query. Not a verdict criterion, so fixing it does not touch the frozen "
                  "contract; the recorded 9/9 on a clean tree stands. Fix before e06 uses this pattern."},

 {"severity": "medium", "category": "provenance",
  "title": "default PM_TAG/PM_LANE stamps an independent executor's rows as the canonical A lane",
  "evidence": "execute_e05.py __main__ does os.environ.setdefault('PM_TAG','m1-cw01a001') and "
              "setdefault('PM_LANE','A'). An independent executor following only the committed "
              "artifacts, who does not know to override these, produces durable rows and a git commit "
              "stamped as the CANONICAL A lane. Provenance silently collides. The replication lane set "
              "them explicitly and its commits correctly read R[m1-cw01replica], but only because it "
              "was told to. Found by the replication lane (P3).",
  "proposed_fix": "Require PM_TAG rather than defaulting it, or derive the lane from the attempt_id. "
                  "OPEN BY DESIGN for e05: execute_e05.py is frozen under contract c80b5bfd and editing "
                  "it would void attempt cw01-e05-a01."},

 {"severity": "medium", "category": "portability",
  "title": "experiment directory cannot be relocated: REPO derived from hardcoded directory depth",
  "evidence": "execute_e05.py derives REPO as HERE.parents[1].parents[3], hardcoding the layout "
              "roles/<Seat>/campaigns/<id>/experiments/<exp>. git archive-ing the experiment subtree "
              "alone to a different depth breaks the import of primordial.fabric. The replication "
              "lane's selfcheck worked only because git archive reconstructs that exact layout. This "
              "bears directly on the campaign's portability mandate (M1/M2/Podman/cloud): the "
              "experiment is reproducible in place, but not relocatable. Found by the replication "
              "lane (P5).",
  "proposed_fix": "Locate the repo root by walking up for a .git marker rather than counting parents. "
                  "OPEN BY DESIGN for e05 (frozen driver); fix in the shared lib before e06."},

 {"severity": "low", "category": "instrument",
  "title": "rows filename and exp_id hardcoded to a01 regardless of PM_TAG or lane",
  "evidence": "execute_e05.py __main__ always writes rows/cw01-e05-a01.jsonl with exp id "
              "CW01-E05-A01, whatever the tag or lane. Two lanes sharing one worktree would collide on "
              "that path. Harmless across separate worktrees, which is how it was actually run. Found "
              "by the replication lane (P6).",
  "proposed_fix": "Derive the rows filename from PM_TAG or attempt_id. OPEN BY DESIGN for e05 "
                  "(frozen driver)."},

 {"severity": "low", "category": "documentation", "status_override": "FIXED",
  "title": "REPLICA_BRIEF.md presented a01-specific BEST/WORST as global facts",
  "evidence": "The brief's 'frozen object' block states BEST [0,2,4] and WORST [4,5,7] without "
              "qualification, but one_replicate calls enumerate_sets with each replicate's OWN "
              "attempt_id, so those sets hold for a01 only. r02-r04 selected [1,2,6]/[0,1,4], "
              "[0,4,5]/[3,6,7], [0,3,7]/[0,2,6]; r05-r12 likewise differ. This is correct behaviour - "
              "attempt-stable latent facts mean independent replicates are independent worlds - but "
              "the brief read as though the sets were properties of the experiment. The replication "
              "lane flagged the ambiguity in my own document.",
  "proposed_fix": "Brief corrected to mark BEST/WORST as binding for attempt cw01-e05-a01 only."},
]


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    n = max(int(m.group(1)) for m in
            (re.match(r"CW01-D(\d+)", str(d.get("id", ""))) for d in entries) if m)
    existing_titles = {d.get("title") for d in entries}

    added = []
    with LEDGER.open("a", encoding="utf-8") as fh:
        for spec in NEW:
            if spec["title"] in existing_titles:
                continue
            n += 1
            rec = {"id": "CW01-D%03d" % n, "ts": now, "campaign_id": "cw01-2026-09-17",
                   "experiment_id": "cw01-e05", "phase": "CLOSE_SCIENCE (independent replication)",
                   "severity": spec["severity"], "category": spec["category"],
                   "status": spec.get("status_override", "OPEN"),
                   "title": spec["title"], "evidence": spec["evidence"],
                   "proposed_fix": spec["proposed_fix"],
                   "found_by": "independent replication lane, branch nestor/e05-replica-2026-09-18"}
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")   # CW01-D050
            added.append(rec["id"])

    after = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    print("added: %s" % (added or "none (already filed)"))
    print("ledger entries: %d | unique ids: %d" % (len(after), len({d["id"] for d in after})))
    print("OPEN: %d | FIXED: %d" % (sum(1 for d in after if d.get("status") == "OPEN"),
                                    sum(1 for d in after if d.get("status") == "FIXED")))
    print("found_by replication lane: %d" % sum(1 for d in after if d.get("found_by")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
