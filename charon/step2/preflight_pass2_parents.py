"""Step 2 preflight pass 2 — do c1's parent pointers RESOLVE?

The pre-registered experiment needs (S, A, Y) where S is the parent's PRE-decision state. A child
row only carries the post-mutation state, so predicting `mutation_side` from a child's own fields
is leakage, not navigation. The triple therefore exists only if `parent_record_id` resolves to a
record that carries a state.

Stage 1 (cheap, 12 GB): look for the sampled parent ids among c1's own `record_id`s.
Stage 2 (only if stage 1 resolves few): scan the whole deduplicated corpus for those ids and
report which generator actually holds them.

A low resolution rate is not a nuisance -- it is a structural finding about whether the
transition thesis has a substrate in this generator at all, and it is reported as such.

    python charon/step2/preflight_pass2_parents.py
"""
import glob
import gzip
import json
import os
import pathlib
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
REC = re.compile(rb'"record_id":\s*"([0-9a-f]{16})')
GEN = re.compile(rb'"generator_id":\s*"([^"]{1,16})"')
WANT = set()


def stage1():
    want = set(json.loads((HERE / "parent_sample.json").read_text()))
    print(f"stage 1: {len(want)} sampled parent ids vs c1's own record_ids", flush=True)
    found = set()
    for sh in sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl"))):
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                r = d.get("record_id")
                if r in want:
                    found.add(r)
    print(f"stage 1: resolved {len(found)}/{len(want)} "
          f"({100*len(found)/max(len(want),1):.2f}%) inside c1", flush=True)
    return want, found


def scan(path_gz):
    path, gz = path_gz
    hits = Counter()
    try:
        fh = gzip.open(path, "rb") if gz else open(path, "rb", buffering=1 << 22)
        with fh:
            for raw in fh:
                m = REC.search(raw)
                if m and m.group(1).decode() in WANT:
                    g = GEN.search(raw)
                    hits[g.group(1).decode() if g else "?"] += 1
    except Exception as e:
        print("SKIP", path, repr(e), file=sys.stderr, flush=True)
    return hits


def init(want_prefixes):
    global WANT
    WANT = want_prefixes


def main():
    want, found = stage1()
    unresolved = want - found
    out = {"sampled_parent_ids": len(want),
           "resolved_within_c1": len(found),
           "resolved_within_c1_pct": round(100 * len(found) / max(len(want), 1), 2)}

    if len(found) < 0.95 * len(want):
        print(f"\nstage 2: {len(unresolved)} unresolved -> scanning the deduplicated corpus",
              flush=True)
        pref = {r[:16] for r in unresolved}
        gzf = sorted(glob.glob("theseus/corpus/batch-*.jsonl.gz"))
        plain = sorted(glob.glob("theseus/corpus/batch-*.jsonl"))
        dup = {os.path.basename(p)[:-6] for p in plain}
        gzf = [p for p in gzf if os.path.basename(p)[:-9] not in dup]
        files = [(p, True) for p in gzf] + [(p, False) for p in plain]
        files.sort(key=lambda x: -os.path.getsize(x[0]))
        tot = Counter()
        with ProcessPoolExecutor(max_workers=12, initializer=init,
                                 initargs=(pref,)) as ex:
            for h in ex.map(scan, files):
                tot.update(h)
        out["stage2_unresolved_sampled"] = len(unresolved)
        out["stage2_found_by_generator"] = dict(tot.most_common())
        out["stage2_total_found"] = sum(tot.values())
        out["stage2_resolution_pct"] = round(100 * sum(tot.values()) / max(len(unresolved), 1), 2)

    print("\n" + json.dumps(out, indent=2))
    (HERE / "preflight_pass2_parents.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
