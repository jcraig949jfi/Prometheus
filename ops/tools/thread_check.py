"""Pre-merge checks for ops thread identity (Artemis's proposal roles/Artemis/challenge/identity/IDENTITY.md, adopted by Archaeon
2026-09-28 for its own threads). stdlib only. Exit 1 on any failure.

  C1  no two thread files on this tree claim the same main alias (TH-nnn), and no two share a canonical id
  C2  every `id:` re-derives from its `id-rule:` (sha256(rule)[:12]); a genesis rule's commit must exist in the repo
  C3  every lifecycle edge target (duplicate-of, merged-into, merged-from, split-into, split-from, superseded-by, rediscovers) is a
      known canonical id
Threads without an `id:` header are listed as UNMIGRATED (a warning, not a failure: migration is each owner's call).
    python ops/tools/thread_check.py [THREADS_DIR]
"""
import glob
import hashlib
import os
import re
import subprocess
import sys

EDGES = ("duplicate-of", "merged-into", "merged-from", "split-into", "split-from", "superseded-by", "rediscovers")


def parse(path):
    h = {"path": path, "edges": []}
    for line in open(path, encoding="utf-8").read().splitlines()[:40]:
        m = re.match(r"^(id|id-rule|aliases):\s*(.+)$", line)
        if m: h[m.group(1)] = m.group(2).strip()
        m = re.match(r"^(%s):\s*(.+)$" % "|".join(EDGES), line)
        if m: h["edges"] += re.findall(r"thr-[0-9a-f]{12}", m.group(2))
    base = os.path.basename(path)[:-3]
    h["alias"] = h["aliases"].split()[0] if "aliases" in h else (base if base.startswith("TH-") else None)
    return h


def main(d):
    heads = [parse(p) for p in sorted(glob.glob(os.path.join(d, "*.md")))]
    fail = []; warn = []
    seen_alias, seen_id = {}, {}
    for h in heads:
        if h["alias"]:
            if h["alias"] in seen_alias: fail.append("C1 alias %s claimed by %s and %s" % (h["alias"], seen_alias[h["alias"]], h["path"]))
            seen_alias[h["alias"]] = h["path"]
        if "id" not in h: warn.append("UNMIGRATED %s" % h["path"]); continue
        if h["id"] in seen_id: fail.append("C1 id %s in %s and %s" % (h["id"], seen_id[h["id"]], h["path"]))
        seen_id[h["id"]] = h["path"]
        rule = h.get("id-rule", "")
        if "thr-" + hashlib.sha256(rule.encode()).hexdigest()[:12] != h["id"]: fail.append("C2 %s: id does not re-derive from id-rule" % h["path"])
        if rule.startswith("genesis|"):
            sha = rule.split("|")[1]
            if subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], capture_output=True).returncode:
                fail.append("C2 %s: genesis commit %s not in this repo" % (h["path"], sha[:10]))
    for h in heads:
        for t in h["edges"]:
            if t not in seen_id: fail.append("C3 %s: edge target %s unknown" % (h["path"], t))
    for x in warn: print(x)
    for x in fail: print(x)
    print("threads=%d migrated=%d failures=%d" % (len(heads), len(seen_id), len(fail)))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "ops/threads"))
