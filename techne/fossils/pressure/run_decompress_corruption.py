"""Batch 07 depth (compression): decompression-corruption behaviour of the preserved codecs.
The charter's example -- "ten compression fossils, zero decompressor failure behaviour" -- so this
records what each decompressor DOES when its stream is corrupted: clean error, partial output,
silent wrong output, or crash. Techne records raw behaviour; it does not rank recovery.

    python run_decompress_corruption.py -> DECOMPRESS_CORRUPTION_<date>.json

For each codec: compress a known text; then for each corruption (flip a byte at 10%/50%/90% of
the stream, and truncate to 50%), decompress and record exit code, bytes produced, and whether the
output equals the original.  Drives the vault's docker C world.

Note: the C build image has no python3, so the workload text, the byte-flip and the truncation are
done with pure coreutils (seq/sed, dd/od, head) inside the container.
"""
import json, pathlib, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"

SCRIPT = r'''
set -e
# workload: 3000 numbered lines (~155 KB), coreutils only (no python in the C image)
seq 1 3000 | sed 's/$/: the quick brown fox jumps over the lazy dog/' > /tmp/orig
build_gzip(){ cp -r /vault/gzip-1.2.4-1993/upstream/tree/gzip-1.2.4 /tmp/g && (cd /tmp/g && ./configure >/dev/null 2>&1 && make -s CFLAGS='-O1 -fcommon -std=gnu89 -w' >/dev/null 2>&1); echo /tmp/g/gzip; }
build_bzip2(){ cp -r /vault/bzip2-1.0.8/upstream/tree/bzip2-1.0.8 /tmp/b && (cd /tmp/b && make -s bzip2 >/dev/null 2>&1); echo /tmp/b/bzip2; }
build_ncomp(){ cp -r /vault/ncompress-5.0-lzw-1985/upstream/tree/ncompress-5.0 /tmp/n && (cd /tmp/n && (make -s compress >/dev/null 2>&1 || make -s >/dev/null 2>&1)); find /tmp/n -maxdepth 1 -name compress -type f | head -1; }
GZ=$(build_gzip); BZ=$(build_bzip2); NC=$(build_ncomp)
set +e
# compress once per codec
$GZ -c -9 < /tmp/orig > /tmp/s.gz 2>/dev/null
$BZ -c -9 < /tmp/orig > /tmp/s.bz2 2>/dev/null
$NC -c   < /tmp/orig > /tmp/s.Z 2>/dev/null
flipbyte(){ # infile pct outfile -> copy, then XOR-0xFF one byte at pct% of the file
  cp "$1" "$3"
  sz=$(stat -c%s "$3"); off=$(( sz * $2 / 100 )); [ "$off" -ge "$sz" ] && off=$(( sz - 1 )); [ "$off" -lt 0 ] && off=0
  b=$(dd if="$3" bs=1 skip="$off" count=1 2>/dev/null | od -An -tu1 | tr -d ' ')
  nb=$(( ${b:-0} ^ 255 ))
  printf "$(printf '\\%03o' "$nb")" | dd of="$3" bs=1 seek="$off" count=1 conv=notrunc 2>/dev/null
}
trunc_half(){ sz=$(stat -c%s "$1"); head -c $(( sz / 2 )) "$1" > "$2"; }
emit(){ # codec case infile decompressor
  cp "$3" /tmp/in
  "$4" -dc < /tmp/in > /tmp/out 2>/tmp/err; rc=$?
  by=$(stat -c%s /tmp/out 2>/dev/null || echo 0)
  same=$(cmp -s /tmp/out /tmp/orig && echo yes || echo no)
  err=$(head -c 120 /tmp/err | tr '\n\t' '  ')
  printf '%s|%s|%s|%s|%s|%s\n' "$1" "$2" "$rc" "$by" "$same" "$err"
}
for spec in "gzip-1.2.4 s.gz $GZ" "bzip2-1.0.8 s.bz2 $BZ" "ncompress-5.0 s.Z $NC"; do
  set -- $spec; codec=$1; f=/tmp/$2; D=$3
  emit "$codec" "clean" "$f" "$D"
  for pct in 10 50 90; do flipbyte "$f" "$pct" /tmp/c; emit "$codec" "flip@${pct}%" /tmp/c "$D"; done
  trunc_half "$f" /tmp/t; emit "$codec" "truncate@50%" /tmp/t "$D"
done
'''


def main():
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro prometheus-fossil-c:bookworm bash -lc %s" % (VAULT, _q(SCRIPT))],
        capture_output=True, text=True, timeout=1800).stdout
    rows = []
    for line in out.splitlines():
        p = line.split("|")
        if len(p) == 6 and "-" in p[0]:
            rows.append({"codec": p[0], "case": p[1], "exit_code": int(p[2]), "bytes_out": int(p[3]),
                         "output_equals_original": p[4] == "yes", "stderr_head": p[5].strip()})
    doc = {"schema": "techne.fossil.decompress_corruption/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "method": "compress ~155 KB of text, then flip one byte (XOR 0xFF) at 10/50/90% or truncate to 50%, and decompress; record exit code, bytes produced, whether output == original, stderr head. Workload/corruption via coreutils (no python in the C image).",
           "note": "raw decompressor failure behaviour; NOT a recovery ranking. A clean case must reproduce the original; corrupted cases show each codec's error/partial/silent-wrong/crash response.",
           "codecs": ["gzip-1.2.4", "bzip2-1.0.8", "ncompress-5.0"], "rows": rows}
    op = HERE / ("DECOMPRESS_CORRUPTION_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print("%-14s %-14s exit=%-3d bytes=%-7d same=%-3s %s" % (r["codec"], r["case"], r["exit_code"], r["bytes_out"], "yes" if r["output_equals_original"] else "no", r["stderr_head"][:50]))
    print("wrote", op, len(rows), "rows")


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
