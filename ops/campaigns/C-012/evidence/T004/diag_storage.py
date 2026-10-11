"""C-012-T004 DIAGNOSTIC (not preregistered; labelled as such): where do the database bytes per accepted epoch go?

R1 measured M6 (database bytes per published epoch) only as a total, because each point's throwaway schemas are
dropped. Tripwire T1 failed at the operating point (s6 of the prereg), and OP-NF2 asks for the precise bottleneck,
so this runs ONE small node point through the FROZEN harness (bench.py, unmodified) and wraps only its drop step to
measure every relation of both schemas first: heap, TOAST and index bytes, and row counts.

    EW_DB_HOST=192.168.1.202 python diag_storage.py --wall-s 60 --out R1/DIAG_STORAGE
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("bench", HERE / "bench.py")
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)

MEASURED = {}


def measure(admin, fs, ms):
    cur = admin.cursor()
    cur.execute("""SELECT n.nspname, c.relname, c.reltuples::bigint, pg_relation_size(c.oid),
                          coalesce(pg_total_relation_size(c.reltoastrelid), 0), pg_indexes_size(c.oid),
                          pg_total_relation_size(c.oid)
                     FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = ANY(%s) AND c.relkind = 'r' ORDER BY pg_total_relation_size(c.oid) DESC""",
                (list((fs, ms)),))
    rows = []
    for nsp, rel, est, heap, toast, idx, total in cur.fetchall():
        cur.execute("SELECT count(*) FROM {}.{}".format(nsp, rel))
        rows.append({"schema": "fabric" if nsp == fs else "moonshot", "table": rel, "rows": cur.fetchone()[0],
                     "heap": heap, "toast": toast, "indexes": idx, "total": total})
    cur.execute("SELECT count(*) FROM {}.publications".format(ms))
    published = cur.fetchone()[0]
    admin.rollback()
    MEASURED.update({"published_rows": published, "relations": rows})


_real_drop = B.drop


def drop_after_measuring(admin, fs, ms):
    measure(admin, fs, ms)
    _real_drop(admin, fs, ms)


B.drop = drop_after_measuring


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall-s", type=float, default=60)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cal = json.loads((HERE / "R1" / "calibration.json").read_text(encoding="utf-8"))["iters_for_D"]
    rec = B.run_point("N", D=1, wpn=1, K=0, wall_s=a.wall_s, iters=cal["1"], run_id="DIAG", out_dir=a.out, smoke=True)
    p = MEASURED["published_rows"] or 1
    rels = MEASURED["relations"]
    total = sum(r["total"] for r in rels)
    for r in rels:
        r["bytes_per_published"] = round(r["total"] / p)
        r["share"] = round(r["total"] / total, 4) if total else None
    doc = {"label": "DIAGNOSTIC (not preregistered)", "point": rec["label"], "published": p, "total_bytes": total,
           "bytes_per_published": round(total / p), "relations": rels,
           "note": "per-relation totals include TOAST and indexes; fixed per-relation overhead (empty pages) is "
                   "included, so per-epoch figures overstate the marginal cost at small P"}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "STORAGE.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("published", p, "total", total, "per epoch", round(total / p))
    for r in rels[:14]:
        print("  {schema:8} {table:22} rows {rows:6} total {total:9} per-epoch {bytes_per_published:7} "
              "(heap {heap}, toast {toast}, idx {indexes})".format(**r))


if __name__ == "__main__":
    sys.exit(main())
