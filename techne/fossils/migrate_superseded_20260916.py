"""Direct the `superseded` lineage relation (Nyx, comms #310; Amendment 3 R35 says MKW-1 cannot
count N while it is undirected). 2026-09-16.

Measured before this ran: 17 edges carried `superseded`; by era, 8 pointed older -> newer, 4
newer -> older, 5 to external names; two records (des-reference, tiny-aes-c) carried the edge in
BOTH directions with the same note. The vocabulary said one word and meant two.

New vocabulary (record.LINEAGE_RELATIONS): `superseded_by` (the subject is the one that was
displaced; edge points at the displacer) and `supersedes` (the subject displaced the target).
Every migration below is decided from the edge's own note or the recorded eras, and listed so
it can be disputed edge by edge. `superseded` is refused by record.validate() from now on.

    python -m techne.fossils.migrate_superseded_20260916 [--dry-run]
"""
import argparse
import json
import pathlib

from . import vault

DECISIONS = {
    # (specimen, to) -> new relation
    ("bsd-4.3-distribution-tape-1986", "bsd-tcp-4.3-tahoe-1988"): "superseded_by",
    ("bsd-tcp-4.2-1983", "bsd-tcp-4.3-tahoe-1988"): "superseded_by",
    ("bsd-tcp-4.3-reno-1990", "linux-tcp-congestion"): "superseded_by",
    ("bsd-tcp-4.3-tahoe-1988", "bsd-tcp-4.3-reno-1990"): "superseded_by",
    ("compact-4.2bsd-1983", "ncompress-5.0-lzw-1985"): "superseded_by",
    ("des-reference", "tiny-aes-c"): "superseded_by",
    ("eispack-netlib-1976", "lapack-reference"): "superseded_by",
    ("linpack-netlib-1979", "lapack-reference"): "superseded_by",
    ("leveldb-1.23", "RocksDB (Facebook fork 2012)"): "superseded_by",
    ("md5-rfc1321", "the SHA-2 family"): "superseded_by",
    ("odepack-netlib", "scipy.integrate.odeint / LSODA"): "superseded_by",
    ("spdylay", "HTTP/2 (RFC 7540)"): "superseded_by",
    ("zchaff-2007", "minisat-2.2.0"): "superseded_by",
    ("linux-tcp-congestion", "TCP Reno/NewReno"): "supersedes",        # "CUBIC replaced Reno-family as Linux default"
    ("gzip-1.2.4-1993", "ncompress-5.0-lzw-1985"): "supersedes",       # note: "direction: gzip superseded compress"
    ("minisat-1.14-2006", "zchaff-2007"): "supersedes",                # note: "MiniSat superseded zChaff"
    ("tiny-aes-c", "des-reference"): "supersedes",                     # "AES replaced DES"
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    changed, unmapped = [], []
    for rp in sorted(vault.SPECIMENS.glob("*/record.json")):
        r = json.loads(rp.read_text(encoding="utf-8"))
        touched = False
        for e in r.get("lineage_relations", []):
            if e.get("relation") == "superseded":
                key = (r["specimen_id"], e["to"])
                if key not in DECISIONS:
                    unmapped.append(key)
                    continue
                e["relation"] = DECISIONS[key]
                e["note"] = (e.get("note", "") + " [relation directed 2026-09-16 from 'superseded' (ambiguous) to '%s' by the note/era; migrate_superseded_20260916.py]" % DECISIONS[key]).strip()
                touched = True
                changed.append(key + (DECISIONS[key],))
        if touched and not a.dry_run:
            rp.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for c in changed:
        print("%-34s -> %-34s %s" % c)
    print("changed", len(changed), "unmapped", len(unmapped), unmapped, "(dry run)" if a.dry_run else "")
    return 1 if unmapped else 0


if __name__ == "__main__":
    raise SystemExit(main())
