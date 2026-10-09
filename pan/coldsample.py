"""Measure what converting the cold April JSON Lines to Parquet would buy, without
converting (or touching) the 128.8 GB: one file converted in full with a line-count
oracle, and random-offset block samples of the largest files (never a prefix: the head
of a file can differ from its body). Read-only toward the sources; output Parquet goes
to <lake>/cold_sample/ and can be deleted.

python -m pan.coldsample FULL_FILE [SAMPLED_FILE ...]
"""
import io
import json
import os
import random
import sys
import time


FORMS = {}


def _convert(data, dest):
    """Typed Parquet when one schema can be inferred; otherwise the lossless fallback
    (one column of verbatim JSON text per line), as in PAN-16. The form used is recorded."""
    import pyarrow as pa
    import pyarrow.json as pj
    import pyarrow.parquet as pq
    try:
        if os.environ.get("PAN_COLD_FORCE_STRING"):
            raise pa.ArrowInvalid("record_string form requested")
        t = pj.read_json(io.BytesIO(data), read_options=pj.ReadOptions(block_size=64 << 20))
        FORMS[dest] = "typed"
    except pa.ArrowInvalid:
        t = pa.table({"record": pa.array([ln.decode("utf-8", "replace") for ln in data.split(b"\n") if ln.strip()],
                                         pa.large_string())})
        FORMS[dest] = "record_string"
    pq.write_table(t, dest, compression="zstd")
    return t.num_rows, t.num_columns


def full(path, outdir):
    t0 = time.time()
    data = open(path, "rb").read()
    lines = sum(1 for ln in data.split(b"\n") if ln.strip())
    dest = os.path.join(outdir, os.path.basename(path) + ".parquet")
    rows, cols = _convert(data, dest)
    return dict(file=path, mode="full", src_bytes=len(data), parquet_bytes=os.path.getsize(dest),
                ratio=round(len(data) / os.path.getsize(dest), 2), rows=rows, columns=cols,
                oracle_lines=lines, oracle_ok=(rows == lines), form=FORMS.get(dest),
                seconds=round(time.time() - t0, 1))


def sampled(path, outdir, blocks=10, block_bytes=16 << 20, seed=20261009):
    size = os.path.getsize(path)
    rng = random.Random(seed)
    offs = sorted(rng.randrange(0, max(1, size - 2 * block_bytes)) for _ in range(blocks))
    src, pq_bytes, rows, cols, t0, forms = 0, 0, 0, set(), time.time(), set()
    with open(path, "rb") as f:
        for i, off in enumerate(offs):
            f.seek(off)
            raw = f.read(block_bytes)
            a, b = raw.find(b"\n"), raw.rfind(b"\n")
            chunk = raw[a + 1:b + 1]              # whole lines only
            dest = os.path.join(outdir, "{}.block{:02d}.parquet".format(os.path.basename(path), i))
            n, c = _convert(chunk, dest)
            forms = forms | {FORMS.get(dest)}
            src += len(chunk)
            pq_bytes += os.path.getsize(dest)
            rows += n
            cols.add(c)
    return dict(file=path, mode="sampled", file_bytes=size, blocks=blocks, sampled_bytes=src,
                sampled_parquet_bytes=pq_bytes, ratio=round(src / pq_bytes, 2), rows_sampled=rows,
                column_counts=sorted(cols), forms=sorted(f for f in forms if f), projected_parquet_gb=round(size / (src / pq_bytes) / 1e9, 2),
                seconds=round(time.time() - t0, 1))


def main():
    from . import lake
    outdir = str(lake() / "cold_sample")
    os.makedirs(outdir, exist_ok=True)
    res = [full(sys.argv[1], outdir)] + [sampled(p, outdir) for p in sys.argv[2:]]
    for r in res:
        print(json.dumps(r))
    return res


if __name__ == "__main__":
    main()
