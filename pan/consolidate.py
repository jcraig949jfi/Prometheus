"""PAN-16: consolidate committed JSON Lines result rows into Parquet + Iceberg.

Source: every .jsonl blob at the catalog SHA (read with git cat-file --batch;
no working tree). Two outputs:

  1. ONE long Iceberg table pan.result_rows -- one row per source line:
       path, top_dir, seat, kind, blob_sha, line_no, record (the JSON text,
       verbatim), n_keys, keys (top-level keys), parse_ok
     Rows that are not valid JSON are KEPT with parse_ok=false (never dropped);
     log-prefixed lines ("TAG ... {json}") parse with parse_mode='prefixed'
     (found: Aether first-light/calibration logs carry a .jsonl extension).
     Partitioned logically by top_dir (one append per batch of files).
  2. A typed Parquet file per source file under <lake>/consolidated/typed/,
     where pyarrow can infer one schema for the whole file; files where it
     cannot are counted, not forced.

ORACLE (independent of the writer): for every file, rows written == the
number of non-empty lines in the source blob, counted separately with
bytes.count(b"\\n") logic; the run fails if any file disagrees.
"""
import datetime as dt
import io
import json
import os
import time

from . import host, lake


def _lines(data):
    for i, ln in enumerate(data.split(b"\n"), 1):
        if ln.strip():
            yield i, ln


def _count_nonempty(data):
    return sum(1 for ln in data.split(b"\n") if ln.strip())


def parse_line(txt):
    """(parse_ok, parse_mode, top_level_keys). 'strict' = the line is JSON; 'prefixed' =
    a log prefix followed by a JSON object ("TAG k=v {...}"); 'none' = neither."""
    obj, ok, mode = None, False, "none"
    try:
        obj = json.loads(txt)
        ok, mode = True, "strict"
    except ValueError:
        j = txt.find("{")
        if j > 0:
            try:
                obj = json.loads(txt[j:])
                ok, mode = True, "prefixed"
            except ValueError:
                obj = None
    keys = list(obj.keys()) if ok and isinstance(obj, dict) else []
    return ok, mode, keys


def run(ext=".jsonl", limit=0, typed=True, out=print, batch_files=200):
    import pyarrow as pa
    import pyarrow.json as pj
    import pyarrow.parquet as pq
    from . import db, iceberg
    from .chunker import BlobReader
    t0 = time.time()
    run_id = "consolidate-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        q = """select path, blob_sha, size_bytes, coalesce(seat,''), top_dir, kind, repo_sha from pan.artifact
               where source='git' and ext=%s order by path"""
        cur.execute(q + (" limit %d" % int(limit) if limit else ""), (ext,))
        files = cur.fetchall()
        sha = files[0][6] if files else None
        cur.execute("insert into pan.run (run_id, kind, host, git_sha, params) values (%s,'consolidate',%s,%s,%s)",
                    (run_id, host(), sha, json.dumps({"ext": ext, "limit": limit, "typed": typed})))
    out("{} {} files to consolidate at {}".format(len(files), ext, (sha or "")[:9]))
    typed_dir = lake() / "consolidated" / "typed"
    typed_dir.mkdir(parents=True, exist_ok=True)
    schema = pa.schema([("path", pa.string()), ("top_dir", pa.string()), ("seat", pa.string()),
                        ("kind", pa.string()), ("blob_sha", pa.string()), ("line_no", pa.int32()),
                        ("record", pa.large_string()), ("n_keys", pa.int16()), ("keys", pa.list_(pa.string())),
                        ("parse_ok", pa.bool_()), ("parse_mode", pa.string())])
    reader = BlobReader()
    counts = dict(files=0, rows=0, bad_json=0, src_bytes=0, typed_ok=0, typed_fail=0, oracle_mismatch=[],
                  missing=0)
    first = True
    try:
        for i in range(0, len(files), batch_files):
            cols = {f.name: [] for f in schema}
            for path, bsha, size, seat, top, kind, _ in files[i:i + batch_files]:
                data = reader.read(bsha)
                if data is None:
                    counts["missing"] += 1
                    continue
                counts["src_bytes"] += len(data)
                expect = _count_nonempty(data)
                n = 0
                for ln_no, ln in _lines(data):
                    txt = ln.decode("utf-8", "replace").replace("\x00", "")
                    ok, mode, keys = parse_line(txt)
                    if mode == "prefixed":
                        counts["prefixed"] = counts.get("prefixed", 0) + 1
                    if not ok:
                        counts["bad_json"] += 1
                    cols["path"].append(path)
                    cols["top_dir"].append(top)
                    cols["seat"].append(seat or None)
                    cols["kind"].append(kind)
                    cols["blob_sha"].append(bsha)
                    cols["line_no"].append(ln_no)
                    cols["record"].append(txt)
                    cols["n_keys"].append(min(len(keys), 32767))
                    cols["keys"].append(keys[:64])
                    cols["parse_ok"].append(ok)
                    cols["parse_mode"].append(mode)
                    n += 1
                if n != expect:
                    counts["oracle_mismatch"].append((path, n, expect))
                counts["files"] += 1
                counts["rows"] += n
                if typed:
                    # temp file + rename: a write that raises after opening the file must not
                    # leave a 0-byte .parquet behind (59 such files on the first full run)
                    dest = typed_dir / (path.replace("/", "__") + ".parquet")
                    tmp = dest.with_suffix(".parquet.tmp")
                    try:
                        t = pj.read_json(io.BytesIO(data))
                        pq.write_table(t, tmp, compression="zstd")
                        os.replace(tmp, dest)
                        counts["typed_ok"] += 1
                    except Exception:
                        counts["typed_fail"] += 1
                        for f in (tmp, dest):
                            try:
                                f.unlink()
                            except OSError:
                                pass
            if cols["path"]:
                tbl = pa.table(cols, schema=schema)
                iceberg.write("result_rows", tbl, mode="overwrite" if first else "append")
                first = False
            out("  {}/{} files, {} rows, {:.0f}s".format(min(i + batch_files, len(files)), len(files),
                                                        counts["rows"], time.time() - t0))
    finally:
        reader.close()
    # independent read-back through Iceberg (not the writer's counter)
    tab = iceberg.catalog().load_table("pan.result_rows")
    snap = tab.current_snapshot()
    counts["iceberg_records"] = int(snap.summary.additional_properties.get("total-records", -1)) if snap else 0
    counts["iceberg_files"] = int(snap.summary.additional_properties.get("total-data-files", -1)) if snap else 0
    counts["iceberg_bytes"] = int(snap.summary.additional_properties.get("total-files-size", -1)) if snap else 0
    counts["seconds"] = round(time.time() - t0, 1)
    ok = not counts["oracle_mismatch"] and counts["iceberg_records"] == counts["rows"]
    with db.cursor() as cur:
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    ("OK" if ok else "FAILED", json.dumps(counts, default=str), run_id))
    out(json.dumps({k: v for k, v in counts.items() if k != "oracle_mismatch"}, default=str))
    if not ok:
        raise SystemExit("ORACLE FAILED: {} mismatched files; iceberg {} vs rows {}".format(
            len(counts["oracle_mismatch"]), counts["iceberg_records"], counts["rows"]))
    return counts
