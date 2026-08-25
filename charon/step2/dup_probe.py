"""Is `record_id` unique in this corpus?

preflight_pass2 looked for 10,421 unresolved parent ids across the deduplicated corpus and found
76,293 matching records -- ~6.6 hits per id, a 732% "resolution rate". Prefix collision is ruled
out (16 hex chars against 555M records gives an expected collision count of ~1e-4), and the regex
cannot match `parent_record_id` because it anchors on a quote immediately before `record_id`.
The remaining explanation is that records are DUPLICATED across batches.

That is not a curiosity. If the same record appears many times, then:
  - row counts overstate distinct claims, including every count in the step 1 census;
  - a random row-level train/test split puts copies of the SAME record on both sides, which is
    textbook leakage and would manufacture exactly the "win on the random holdout" the plan
    predicts -- for a reason that has nothing to do with navigation.

Measured here on the c1 extract (12 GB, 30,031,376 rows) by byte-regex, no JSON parse:
distinct record_ids, the duplication factor, and whether duplicate rows are byte-identical
(a re-emission) or differ (a genuine re-evaluation).

    python charon/step2/dup_probe.py
"""
import collections
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
REC = re.compile(rb'"record_id":"([0-9a-f]+)"')
SHARDS = sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl")))


def main():
    seen = set()
    rows = 0
    for sh in SHARDS:
        with open(sh, "rb") as f:
            for raw in f:
                m = REC.search(raw)
                if m:
                    rows += 1
                    seen.add(int(m.group(1)[:16], 16))
    print(f"c1 rows                {rows:,}")
    print(f"distinct record_ids    {len(seen):,}")
    print(f"duplication factor     {rows/max(len(seen),1):.2f}x")

    # are duplicates byte-identical, or genuine re-evaluations?
    counts = collections.Counter()
    for sh in SHARDS[:6]:
        with open(sh, "rb") as f:
            for raw in f:
                m = REC.search(raw)
                if m:
                    counts[m.group(1)[:16]] += 1
    worst = [k for k, v in counts.most_common(5)]
    print(f"\nmost-repeated record_ids in the first {min(6,len(SHARDS))} shards: "
          f"{[(k.decode(), counts[k]) for k in worst]}")

    payloads = collections.defaultdict(list)
    want = set(worst)
    for sh in SHARDS:
        with open(sh, "rb") as f:
            for raw in f:
                m = REC.search(raw)
                if m and m.group(1)[:16] in want and len(payloads[m.group(1)[:16]]) < 4:
                    payloads[m.group(1)[:16]].append(raw.strip())
    out = {"c1_rows": rows, "distinct_record_ids": len(seen),
           "duplication_factor": round(rows / max(len(seen), 1), 3), "examples": {}}
    for k, v in payloads.items():
        ident = len(set(v)) == 1
        out["examples"][k.decode()] = {"copies_examined": len(v), "byte_identical": ident}
        print(f"\nrecord_id {k.decode()}  copies={len(v)}  byte_identical={ident}")
        if not ident:
            for i, r in enumerate(v[:2]):
                print(f"   [{i}] {r[:300].decode()}")
    (HERE / "dup_probe.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nwrote dup_probe.json")


if __name__ == "__main__":
    main()
