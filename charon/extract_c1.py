"""Charon plan step 2, preparation — exact extraction of the c1 population.

WHY THIS RUNS BEFORE THE EXPERIMENT. The plan pre-registers the step 2 population as
"c1 x equal_mod_2, both file windows, full scan: 411,580 rows / 222,715 parent states". The
step 1 census measured c1 at 30,031,376 rows EXACT (every line of 370.9 GB), and c1's `relation`
field is near-uniform over four values {equal_mod_2, divides, abs_diff_le_3, equal}, which puts
equal_mod_2 near 7.8M rows -- about 19x the pre-registered figure. One "full scan" claim on this
corpus (generator_census.py v1) has already been shown to be a 5% prefix. The population a
pre-registered experiment runs on is not something to inherit unverified, so it is recounted here
exactly, every line, before any estimator is written.

Extracts ALL FOUR relations, not just equal_mod_2. The scan is IO-bound, so the other three
relations are free at extraction time, and they are the held-out-relation control -- the control
that retracted the h4 ranking positive when it turned out to be memorisation of 14 constants. Not
having them would mean paying for a second 370.9 GB scan later. The pre-registered experiment
still runs on equal_mod_2 alone; the rest are the transfer test, kept separate.

DEDUPLICATION. Two batch ids exist byte-identically in BOTH file populations
(batch-...e62af7, batch-...5b165c). The .gz copies are dropped so their rows are not counted twice.

Emits the (state, action, outcome, link) tuple only:
  state   catalog_a/b, invariant_a/b, object_a/b, value_a/b, relation
  action  mutation_side          <- chosen BEFORE the outcome
  outcome holds                  <- terminus; never an input to any estimator
  link    record_id, parent_record_id

    python charon/extract_c1.py
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

C1 = re.compile(rb'"generator_id":\s*"c1"')
REL = re.compile(rb'"relation":\s*"([a-z0-9_]{1,24})"')
OUTDIR = pathlib.Path(__file__).resolve().parent / "step2" / "shards"
KEEP = ("catalog_a", "catalog_b", "invariant_a", "invariant_b", "object_a", "object_b",
        "value_a", "value_b", "relation", "mutation_side", "holds", "parent_record_id")


def one_file(arg):
    idx, path, gz = arg
    rows = 0                       # c1 rows seen
    rel = Counter()                # c1 rows per relation (EXACT)
    kept = 0
    out = OUTDIR / f"c1-{idx:04d}.jsonl"
    try:
        fh = gzip.open(path, "rb") if gz else open(path, "rb", buffering=1 << 22)
        with fh, open(out, "w", encoding="utf-8") as w:
            for raw in fh:
                if not C1.search(raw):
                    continue
                rows += 1
                m = REL.search(raw)
                rel[m.group(1).decode() if m else "?"] += 1
                try:
                    d = json.loads(raw)
                except Exception:
                    continue
                pl = d.get("claim_payload")
                if not isinstance(pl, dict):
                    continue
                r = {k: pl.get(k) for k in KEEP}
                r["record_id"] = d.get("record_id")
                r["verdict"] = d.get("verdict")
                w.write(json.dumps(r, separators=(",", ":")) + "\n")
                kept += 1
    except Exception as e:
        print("SKIP", path, repr(e), file=sys.stderr, flush=True)
    if rows == 0:
        try:
            out.unlink()
        except OSError:
            pass
    print(f"  {os.path.basename(path)} c1={rows:,} kept={kept:,}", flush=True)
    return rows, rel, kept


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    gzf = sorted(glob.glob("theseus/corpus/batch-*.jsonl.gz"))
    plain = sorted(glob.glob("theseus/corpus/batch-*.jsonl"))
    dup = {os.path.basename(p)[:-6] for p in plain}
    dropped = [p for p in gzf if os.path.basename(p)[:-9] in dup]
    gzf = [p for p in gzf if os.path.basename(p)[:-9] not in dup]
    print(f"dropped {len(dropped)} duplicate .gz copies: "
          f"{[os.path.basename(p) for p in dropped]}", flush=True)
    files = [(p, True) for p in gzf] + [(p, False) for p in plain]
    files.sort(key=lambda x: -os.path.getsize(x[0]))
    args = [(i, p, g) for i, (p, g) in enumerate(files)]
    gb = sum(os.path.getsize(p) for p, _ in files) / 1e9
    print(f"extract c1: {len(files)} files, {gb:.1f} GB (deduplicated)", flush=True)

    tot, rel, kept = 0, Counter(), 0
    with ProcessPoolExecutor(max_workers=12) as ex:
        for r, rc, k in ex.map(one_file, args):
            tot += r
            rel.update(rc)
            kept += k

    summary = {
        "scope": f"{len(files)} files, {round(gb,1)} GB, duplicate .gz copies dropped",
        "c1_rows_EXACT": tot,
        "c1_rows_by_relation_EXACT": dict(rel.most_common()),
        "rows_emitted": kept,
        "preregistered_claim": "c1 x equal_mod_2 = 411,580 rows / 222,715 parent states",
        "measured_equal_mod_2": rel.get("equal_mod_2", 0),
        "ratio_measured_over_preregistered": round(rel.get("equal_mod_2", 0) / 411_580, 2),
    }
    print("\n" + json.dumps(summary, indent=2))
    (OUTDIR.parent / "c1_extract_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print("\nshards in", OUTDIR)


if __name__ == "__main__":
    main()
