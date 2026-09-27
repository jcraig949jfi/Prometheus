"""TH-006 verification pack for BEE births logs (specimen: C-001/E-001/T-001, run r038751).

Stdlib only. Three commands:

  make    build the pack from a T-001 replay output (births_rows + codeprov)
  verify  check a replay output against a committed pack: IDENTITY (the rows
          are the preserved log's rows), CODEPROV (the probe's per-birth
          counts), CLAIM (the published location-vs-material table, recomputed
          here from the rows with this file's own rules)
  attest  check the preserved source log (the .jsonl.gz on M2) against the
          pack's source section, reading nothing but that file

    python th006_pack.py make   --replay OUT.json --rid r038751 --config CFG.json --out PACK.json [--published B6.json]
    python th006_pack.py verify --pack PACK.json --pack-sha256 HEX --replay OUT.json [--published B6.json]
    python th006_pack.py attest --pack PACK.json --source-log r038751.jsonl.gz

The source log's CONTENT is defined as the bytes BEE's traced_replay._one
wrote before gzip: one line per births row, json.dumps(row) + "\\n",
Python's default separators, rows in replay order. Hashing decompressed
content (not the .gz file) makes the hash independent of gzip headers,
and reproducible with `gzip -dc FILE | sha256sum` without this tool.
"""
import argparse
import collections
import gzip
import hashlib
import json
import sys

SCHEMA = "th006.bee_births_verification_pack.v1"
ROWS_PER_CHUNK = 1000
FIELD_NAMES = [
    "tick", "writer_id", "child_id", "mechanism", "fid_writer_now", "fid_target", "material",
    "writes", "copied_from_own", "by_own_code", "changed", "is_sr", "sr_depth", "own_steps",
    "win_steps", "other_steps", "variant", "fid_pre", "is_sr_post", "into_empty",
]
CLAIM_FIELDS = [7, 8, 9, 11]  # writes, copied_from_own, by_own_code, is_sr
CODEPROV_KEYS = ["own_region", "self_copied", "foreign", "elsewhere"]
YES, NO, NI_LOC, NI_MAT = "YES", "NO", "NOT_IDENTIFIABLE", "NI"


# ------------------------------------------------------------------ hashing
def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def row_line(r):
    return json.dumps(list(r)) + "\n"


def content_bytes(rows):
    return "".join(row_line(r) for r in rows).encode("ascii")


def chunk_hashes(rows):
    return [sha256_hex(content_bytes(rows[i:i + ROWS_PER_CHUNK]))
            for i in range(0, len(rows), ROWS_PER_CHUNK)]


def column_hashes(rows):
    nf = len(FIELD_NAMES)
    return [sha256_hex(json.dumps([r[f] if len(r) > f else "<missing>" for r in rows]).encode("ascii"))
            for f in range(nf)]


def codeprov_sha256(cp):
    return sha256_hex(json.dumps(cp, sort_keys=True).encode("ascii"))


def result_sha256(rows, cp):
    """The probe's own result hash (codeprov_replay.py): births rows + codeprov."""
    return sha256_hex(json.dumps({"births_rows": rows, "codeprov": cp}, sort_keys=True).encode())


# ------------------------------------------------------------------ the claim
def by_location(r):
    """BEE's location reading of who governed the writes (archaeon adapters_v02.bee_row autonomy_write)."""
    writes, own, byown = r[7], r[8], r[9]
    if writes <= 0:
        return NI_LOC
    if 2 * byown > writes:
        return YES
    if 2 * (own - byown) > writes:
        return NO
    return NI_LOC


def by_material(r, c):
    """The probe's material reading (archaeon b6_probe_analyze.py)."""
    own_mat = c["own_region"] + c["self_copied"]
    if 2 * own_mat > r[7]:
        return YES
    if 2 * c["foreign"] > r[7]:
        return NO
    return NI_MAT


def compute_claim(rows, cp):
    lvm, agg, sr = collections.Counter(), collections.Counter(), collections.Counter()
    for r, c in zip(rows, cp):
        loc = by_location(r)
        lvm["W_by_location=%s | W_by_material=%s" % (loc, by_material(r, c))] += 1
        if loc == NO:
            for k in CODEPROV_KEYS:
                agg[k] += c[k]
        if r[11]:
            sr["native_SR | " + ("self_copied_writes>0" if c["self_copied"] else "none")] += 1
    return {
        "location_vs_material": dict(sorted(lvm.items())),
        "code_material_of_writes_in_W=NO_births": {k: agg[k] for k in CODEPROV_KEYS},
        "native_SR_births": dict(sorted(sr.items())),
    }


def _norm_table(t):
    return {k: dict(sorted(v.items())) for k, v in t.items() if k in (
        "location_vs_material", "code_material_of_writes_in_W=NO_births", "native_SR_births")}


# ------------------------------------------------------------------ make
def load_replay(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d, [list(r) for r in d["births_rows"]], d["codeprov"]


def make_pack(replay_path, rid, L, recipe=None, published=None, source_path=None):
    d, rows, cp = load_replay(replay_path)
    if len(rows) != len(cp):
        raise ValueError("rows and codeprov differ in length")
    content = content_bytes(rows)
    return {
        "schema": SCHEMA,
        "specimen": {"thread": "TH-006", "campaign": "C-001", "experiment": "E-001", "task": "T-001", "rid": rid},
        "source": {
            "what": "BEE preserved traced births log (one run)",
            "path_on_M2": source_path,
            "written_by": "traced_replay._one (Bellerophon forensics tools)",
            "content_definition": "gzip-decompressed bytes; one line per row: json.dumps(row) + '\\n', default separators, replay order",
            "row_count": len(rows),
            "fields": FIELD_NAMES,
            "content_bytes": len(content),
            "content_sha256": sha256_hex(content),
            "gz_file_sha256": None,
        },
        "chunks": {"rows_per_chunk": ROWS_PER_CHUNK, "sha256": chunk_hashes(rows)},
        "columns": {"sha256": column_hashes(rows)},
        "claim": {
            "fields_used": CLAIM_FIELDS,
            "codeprov_keys_used": CODEPROV_KEYS,
            "L": L,
            "rules": {
                "W_by_location": "writes=f7, own=f8, byown=f9: writes<=0 -> NOT_IDENTIFIABLE; 2*byown>writes -> YES; "
                                 "2*(own-byown)>writes -> NO; else NOT_IDENTIFIABLE",
                "W_by_material": "own_mat=own_region+self_copied: 2*own_mat>f7 -> YES; 2*foreign>f7 -> NO; else NI",
                "aggregate": "sum codeprov over births with W_by_location=NO",
                "native_SR": "births with f11 != 0, split by self_copied > 0",
            },
            "table": compute_claim(rows, cp),
            "published": published,
        },
        "replay": {
            "result_sha256": result_sha256(rows, cp),
            "codeprov_sha256": codeprov_sha256(cp),
            "recipe": recipe,
        },
        "derivation": {
            "derived_from": "a replay output, NOT the preserved source log",
            "why": "the preserved log exists only on M2; this pack predicts its content hash from a replay that M2 "
                   "found row-identical to it (E-001 T-001 A-002 receipt). The prediction is checked by `attest` on M2.",
            "attestation": {"status": "PENDING", "by": None, "gz_file_sha256": None},
        },
    }


def dump_pack(pack):
    return json.dumps(pack, indent=1, sort_keys=True) + "\n"


# ------------------------------------------------------------------ compare helpers
def _diff_fields(pack, rows):
    got = column_hashes(rows)
    return [f for f, (a, b) in enumerate(zip(pack["columns"]["sha256"], got)) if a != b]


def _first_bad_chunk(pack, rows):
    want, got = pack["chunks"]["sha256"], chunk_hashes(rows)
    for i in range(max(len(want), len(got))):
        if i >= len(want) or i >= len(got) or want[i] != got[i]:
            return i
    return None


# ------------------------------------------------------------------ verify
def verify(pack_path, replay_path, expected_pack_sha256=None, published_path=None):
    out = {"pack": {}, "identity": {}, "codeprov": {}, "claim": {}}
    psha = file_sha256(pack_path)
    with open(pack_path, encoding="utf-8") as f:
        pack = json.load(f)
    ok = pack.get("schema") == SCHEMA and (expected_pack_sha256 is None or psha == expected_pack_sha256)
    out["pack"] = {"status": "PASS" if ok else "FAIL", "sha256": psha, "expected": expected_pack_sha256}

    d, rows, cp = load_replay(replay_path)
    src = pack["source"]
    content = content_bytes(rows)
    changed = _diff_fields(pack, rows)
    ident = {
        "row_count": len(rows), "expected_row_count": src["row_count"],
        "content_sha256": sha256_hex(content), "expected_content_sha256": src["content_sha256"],
        "first_bad_chunk": _first_bad_chunk(pack, rows),
        "fields_changed": changed,
        "claim_fields_changed": [f for f in changed if f in CLAIM_FIELDS],
        "result_sha256_match": result_sha256(rows, cp) == pack["replay"]["result_sha256"],
    }
    ident["status"] = "PASS" if (len(rows) == src["row_count"] and ident["content_sha256"] == src["content_sha256"]) else "FAIL"
    out["identity"] = ident

    cps = codeprov_sha256(cp)
    out["codeprov"] = {"status": "PASS" if (cps == pack["replay"]["codeprov_sha256"] and len(cp) == len(rows)) else "FAIL",
                       "sha256": cps, "expected": pack["replay"]["codeprov_sha256"]}

    table = compute_claim(rows, cp)
    claim_ok = _norm_table(table) == _norm_table(pack["claim"]["table"])
    claim = {"recomputed": table, "matches_pack": claim_ok}
    if published_path:
        with open(published_path, encoding="utf-8") as f:
            pub = json.load(f)
        claim["matches_published"] = _norm_table(table) == _norm_table(pub)
        claim_ok = claim_ok and claim["matches_published"]
    claim["status"] = "PASS" if claim_ok else "FAIL"
    out["claim"] = claim

    out["verdict"] = "PASS" if all(out[k]["status"] == "PASS" for k in ("pack", "identity", "codeprov", "claim")) else "FAIL"
    return out


# ------------------------------------------------------------------ attest (runs where the source log lives)
def attest(pack_path, source_log_path):
    with open(pack_path, encoding="utf-8") as f:
        pack = json.load(f)
    with gzip.open(source_log_path, "rb") as f:
        content = f.read()
    rows = [json.loads(line) for line in content.decode("ascii").splitlines() if line.strip()]
    src = pack["source"]
    same = sha256_hex(content) == src["content_sha256"] and len(rows) == src["row_count"]
    return {
        "status": "MATCH" if same else "MISMATCH",
        "source_log": source_log_path,
        "source_gz_sha256": file_sha256(source_log_path),
        "content_sha256": sha256_hex(content), "expected_content_sha256": src["content_sha256"],
        "content_bytes": len(content),
        "row_count": len(rows), "expected_row_count": src["row_count"],
        "first_bad_chunk": None if same else _first_bad_chunk(pack, rows),
        "fields_changed": [] if same else _diff_fields(pack, rows),
        "reserialises_identically": content_bytes(rows) == content,
    }


# ------------------------------------------------------------------ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(prog="th006_pack")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--replay", required=True)
    m.add_argument("--rid", required=True)
    m.add_argument("--config", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--published")
    m.add_argument("--source-path")
    m.add_argument("--recipe-json", help="JSON file describing how the replay was produced")
    v = sub.add_parser("verify")
    v.add_argument("--pack", required=True)
    v.add_argument("--pack-sha256", required=True)
    v.add_argument("--replay", required=True)
    v.add_argument("--published")
    a = sub.add_parser("attest")
    a.add_argument("--pack", required=True)
    a.add_argument("--source-log", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "make":
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)
        L = 32 if "32" in str(cfg["config"].get("representation")) else 64  # b6_probe_analyze.py's rule
        recipe = None
        if args.recipe_json:
            with open(args.recipe_json, encoding="utf-8") as f:
                recipe = json.load(f)
        published = None
        if args.published:
            published = {"path": args.published, "sha256": file_sha256(args.published)}
        pack = make_pack(args.replay, args.rid, L, recipe=recipe, published=published,
                         source_path=args.source_path)
        if args.published:
            with open(args.published, encoding="utf-8") as f:
                pub = json.load(f)
            if _norm_table(pack["claim"]["table"]) != _norm_table(pub):
                print("REFUSED: the replay does not reproduce the published table", file=sys.stderr)
                return 1
        with open(args.out, "w", encoding="ascii", newline="\n") as f:
            f.write(dump_pack(pack))
        print(json.dumps({"pack": args.out, "sha256": file_sha256(args.out),
                          "content_sha256": pack["source"]["content_sha256"]}))
        return 0
    if args.cmd == "verify":
        r = verify(args.pack, args.replay, args.pack_sha256, args.published)
        slim = {k: ({kk: vv for kk, vv in r[k].items() if kk != "recomputed"} if isinstance(r[k], dict) else r[k]) for k in r}
        print(json.dumps(slim, indent=1, sort_keys=True))
        return 0 if r["verdict"] == "PASS" else 1
    if args.cmd == "attest":
        r = attest(args.pack, args.source_log)
        print(json.dumps(r, indent=1, sort_keys=True))
        return 0 if r["status"] == "MATCH" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
