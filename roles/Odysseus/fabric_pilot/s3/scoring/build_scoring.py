"""S3 s5 blind quality scoring: build the sanitised, relabelled bundles and the scorer prompts.

    EW_DB_HOST=192.168.1.202 python3 build_scoring.py <scratch_dir>

- S3 set: the 10 research packages' REPORT.md (Fabric artifacts, thr-s3).
- Control set: 10 of Artemis's 36 self-test reports (roles/Artemis/selftest/runs/R-xx/REPORT.md), drawn with
  random.Random(20260929).
- Sanitising (identical for both sets): redact run/task/attempt ids, package/run labels, host and worker names,
  seat names, the words self-test/S3/Fabric/package, and header lines that name a task or attempt.
- Labels X001..X020 are assigned by a seeded shuffle. The KEY (label -> source) goes to <scratch_dir> only. Its
  sha256 is written to KEY_SHA256.txt here (commit-reveal); the key is published after scoring.
- Deviation from S3_PROTOCOL s5 (recorded): scorers get REPORT.md only (control reports have no claims.json;
  including it would unblind the set).
- Scorer batches: role A = labels in sorted order, split into 4 x 5; role B = a seeded shuffle, split into 4 x 5.
"""
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))
from fabric import store as S  # noqa: E402

REDACT = [
    r"^.*\b(tsk|att)-[0-9a-f]{6,}.*$",
    r"\b(tsk|att|lse)-[0-9a-f]{6,}\b", r"\bR-\d{2}\b", r"\bQ\d{1,2}\b", r"\bIP\d\b", r"\bX\d{3}\b",
    r"\bworker\.[A-Za-z0-9_.-]+", r"\bubu00\d\b", r"\bSKULLPORT\b|\bSPECTREX5\b|\bBUCKKEEP\b",
    r"\b(Artemis|Odysseus|Nestor|Harmonia|Cosmos|Aporia|Archaeon|Aether|Ensorain|Bellerophon|Aphrodite|Ananke|Cyclops)\b",
    r"\bself-?test\b", r"\bS3\b", r"\b[Ff]abric\b", r"\bPACKAGE\.md\b", r"\bpackage\b", r"\bclaims\.json\b",
    r"roles/[A-Za-z]+/selftest/[^\s)`]*", r"/home/jcraig/[^\s)`]*",
]
RX = [re.compile(p, re.I | re.M) for p in REDACT]


def sanitise(t: str) -> str:
    for rx in RX:
        t = rx.sub("[redacted]", t)
    return t


def main():
    scratch = Path(sys.argv[1]); scratch.mkdir(parents=True, exist_ok=True)
    c = S.connect()
    items = []
    for t in S.list_tasks(c, thread_id="thr-s3", limit=50):
        k = S.get_task(c, t["task_id"])
        if not re.match(r"S3 Q\d+$", k["title"]):
            continue
        rep = [x for x in k["artifacts"] if x["name"].endswith("REPORT.md")][-1]
        items.append({"source": "S3", "id": k["title"], "task": k["task_id"],
                      "text": S.artifact_content(c, rep["artifact_id"])["content"].decode("utf-8", "replace")})
    runs = sorted(p.name for p in (REPO / "roles/Artemis/selftest/runs").iterdir() if (p / "REPORT.md").is_file())
    for r in random.Random(20260929).sample(runs, 10):
        items.append({"source": "CONTROL", "id": r, "task": None,
                      "text": (REPO / "roles/Artemis/selftest/runs" / r / "REPORT.md").read_text("utf-8", "replace")})
    assert len(items) == 20, len(items)
    order = list(range(20)); random.Random(424242).shuffle(order)
    key = {}
    for n, i in enumerate(order, 1):
        lab = "X%03d" % n
        items[i]["label"] = lab
        key[lab] = {"source": items[i]["source"], "id": items[i]["id"], "task": items[i]["task"]}
    kb = json.dumps(key, indent=1, sort_keys=True).encode()
    (scratch / "S3_SCORING_KEY.json").write_bytes(kb)
    (HERE / "KEY_SHA256.txt").write_text(hashlib.sha256(kb).hexdigest() + "  S3_SCORING_KEY.json (revealed after scoring)\n")
    by = {it["label"]: sanitise(it["text"]) for it in items}
    labels = sorted(by)
    shuf = labels[:]; random.Random(20260930).shuffle(shuf)
    batches = {"A%d" % (j + 1): labels[j * 5:(j + 1) * 5] for j in range(4)}
    batches.update({"B%d" % (j + 1): shuf[j * 5:(j + 1) * 5] for j in range(4)})
    rubric = (HERE / "RUBRIC.md").read_text()
    for b, labs in batches.items():
        body = rubric + "\n\n---------------- THE REPORTS ----------------\n"
        for lab in labs:
            body += "\n\n======== REPORT %s ========\n\n%s\n" % (lab, by[lab])
        (HERE / ("prompt_%s.md" % b)).write_text(body)
    (HERE / "BATCHES.json").write_text(json.dumps(batches, indent=1) + "\n")
    print(json.dumps({"items": 20, "s3": sum(1 for v in key.values() if v["source"] == "S3"), "batches": batches}))


if __name__ == "__main__":
    main()
