"""Step 2 build — extract the PRE-DECISION parent states for c1 x equal_mod_2.

The pre-registered triple is (S, A, Y) with S = the PARENT's state, because the action
`mutation_side` is chosen AT the parent and every child row stores only the post-mutation state.
Predicting the action from a child's own fields would largely be detecting which object changed --
leakage, not navigation. So the parent states have to be fetched.

Stage A  collect the distinct parent_record_ids of the 7,062,044 c1 x equal_mod_2 rows
         (preflight_pass1 measured 3,060,875 of them, 100% coverage, none missing).
Stage B  scan the deduplicated corpus for records whose record_id is one of those, and emit
         their state. Membership is a sorted uint64 array + searchsorted so each of the 12
         workers carries ~24 MB rather than a 200 MB Python set.

Parents are themselves content-addressed and duplicated (dup_probe: 2.99x in c1), so the output
is deduplicated by record_id on load, not here.

    python charon/step2/extract_parents.py
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

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
REL = "equal_mod_2"
IDS = HERE / "parent_ids.npy"
OUTDIR = HERE / "parent_shards"
REC = re.compile(rb'"record_id":\s*"([0-9a-f]{16})')
GEN = re.compile(rb'"generator_id":\s*"([^"]{1,16})"')
KEEP = ("catalog_a", "catalog_b", "invariant_a", "invariant_b", "object_a", "object_b",
        "value_a", "value_b", "relation", "mutation_side", "holds", "parent_record_id")
_KEYS = None


def stage_a():
    if IDS.exists():
        a = np.load(IDS)
        print(f"stage A: reusing {IDS.name}, {len(a):,} distinct parent ids", flush=True)
        return a
    pid_re = re.compile(rb'"parent_record_id":"([0-9a-f]{16})')
    rel_re = re.compile(rb'"relation":"([a-z0-9_]{1,24})"')
    seen = set()
    for sh in sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl"))):
        with open(sh, "rb") as f:
            for raw in f:
                r = rel_re.search(raw)
                if not r or r.group(1) != REL.encode():
                    continue
                m = pid_re.search(raw)
                if m:
                    seen.add(int(m.group(1), 16))
    a = np.fromiter(seen, dtype=np.uint64, count=len(seen))
    a.sort()
    np.save(IDS, a)
    print(f"stage A: {len(a):,} distinct parent ids -> {IDS.name}", flush=True)
    return a


def init(path):
    global _KEYS
    _KEYS = np.load(path)


def scan(arg):
    idx, path, gz = arg
    hits = 0
    gens = Counter()
    out = OUTDIR / f"p-{idx:04d}.jsonl"
    try:
        fh = gzip.open(path, "rb") if gz else open(path, "rb", buffering=1 << 22)
        with fh, open(out, "w", encoding="utf-8") as w:
            for raw in fh:
                m = REC.search(raw)
                if not m:
                    continue
                v = np.uint64(int(m.group(1), 16))
                i = np.searchsorted(_KEYS, v)
                if i >= len(_KEYS) or _KEYS[i] != v:
                    continue
                try:
                    d = json.loads(raw)
                except Exception:
                    continue
                pl = d.get("claim_payload")
                if not isinstance(pl, dict):
                    pl = {}
                r = {k: pl.get(k) for k in KEEP}
                r["record_id"] = d.get("record_id")
                r["generator_id"] = d.get("generator_id")
                r["verdict"] = d.get("verdict")
                w.write(json.dumps(r, separators=(",", ":")) + "\n")
                hits += 1
                gens[str(d.get("generator_id"))] += 1
    except Exception as e:
        print("SKIP", path, repr(e), file=sys.stderr, flush=True)
    if hits == 0:
        try:
            out.unlink()
        except OSError:
            pass
    print(f"  {os.path.basename(path)} parents={hits:,}", flush=True)
    return hits, gens


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    keys = stage_a()

    gzf = sorted(glob.glob("theseus/corpus/batch-*.jsonl.gz"))
    plain = sorted(glob.glob("theseus/corpus/batch-*.jsonl"))
    dup = {os.path.basename(p)[:-6] for p in plain}
    gzf = [p for p in gzf if os.path.basename(p)[:-9] not in dup]
    files = [(p, True) for p in gzf] + [(p, False) for p in plain]
    files.sort(key=lambda x: -os.path.getsize(x[0]))
    args = [(i, p, g) for i, (p, g) in enumerate(files)]
    print(f"stage B: {len(files)} files, "
          f"{sum(os.path.getsize(p) for p,_ in files)/1e9:.1f} GB", flush=True)

    tot, gens = 0, Counter()
    with ProcessPoolExecutor(max_workers=12, initializer=init, initargs=(str(IDS),)) as ex:
        for h, g in ex.map(scan, args):
            tot += h
            gens.update(g)

    summary = {
        "distinct_parent_ids_wanted": int(len(keys)),
        "parent_records_emitted": tot,
        "emitted_over_wanted": round(tot / max(len(keys), 1), 3),
        "note": "emitted > wanted is expected: parents are content-addressed and duplicated "
                "across batches (dup_probe: 2.99x in c1). Deduplicate by record_id on load.",
        "by_generator": dict(gens.most_common()),
    }
    print("\n" + json.dumps(summary, indent=2))
    (HERE / "parent_extract_summary.json").write_text(json.dumps(summary, indent=2),
                                                      encoding="utf-8")


if __name__ == "__main__":
    main()
