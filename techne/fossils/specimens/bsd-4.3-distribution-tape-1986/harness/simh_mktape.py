"""Build a SIMH .tap image from distribution tape files (batch 06, TECHNE-69).

    python3 simh_mktape.py OUT.tap FILE:BLOCKSIZE [FILE:BLOCKSIZE ...]

Each FILE becomes one tape file of fixed-length records of BLOCKSIZE bytes (the last record padded
with zeros, as the 4BSD `dd`-written tapes were), followed by a tape mark; the image ends with a
double tape mark. SIMH's E11 .tap format: each record is <u32 length> <data> <u32 length>; a tape
mark is a single u32 0. Gzipped inputs are decompressed on the fly. Nothing here alters a
distribution file: the image is a container, and its sha256 is written to stdout.
"""
import gzip, hashlib, struct, sys


def records(path, bs):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rb") as f:
        while True:
            chunk = f.read(bs)
            if not chunk:
                return
            if len(chunk) < bs:
                chunk = chunk + b"\0" * (bs - len(chunk))
            yield chunk


def main(argv):
    out = argv[1]
    h = hashlib.sha256()
    with open(out, "wb") as o:
        def w(b):
            o.write(b); h.update(b)
        for spec in argv[2:]:
            path, bs = spec.rsplit(":", 1); bs = int(bs); n = 0
            for rec in records(path, bs):
                hdr = struct.pack("<I", len(rec)); w(hdr); w(rec); w(hdr); n += 1
            w(struct.pack("<I", 0))
            print("%s: %d records of %d bytes" % (path, n, bs))
        w(struct.pack("<I", 0))
    print("tap sha256", h.hexdigest())


if __name__ == "__main__":
    main(sys.argv)
