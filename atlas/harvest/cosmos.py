"""Source adapter: Cosmos's committed Atlas export (roles/Cosmos/campaigns/atlas_export_c0 on a git ref).

Cosmos wrote the export already in Atlas's shape (atlas_fact.jsonl and
atlas_edge.jsonl per store) plus a MANIFEST.json carrying the sha256 of every
exported file and of the runtime ledgers left on M2. This adapter:

- verifies each exported file's sha256 and row count against the MANIFEST
  BEFORE ingesting anything. One mismatch refuses the whole pass (fail closed);
- maps one store to one experiment and one attempt. The runtime ran on M2
  (Cosmos #562, DECLARED). The runtime ledgers (cwe.sqlite, receipts.jsonl)
  are EXPECTED:M2 pointers carrying the MANIFEST sha256;
- groups experiments into campaigns by the store name's c<N> prefix (INFERRED,
  and labelled so on each campaign);
- keeps every exported fact per store. Cosmos's fact_key is a world-level key
  that recurs across stores, sometimes with a different value (the same world
  measured again under another purpose/code), so the store file is part of
  each fact's identity. The native `method` (it carries purpose=) is kept in
  value_json;
- keeps edges with Cosmos's own relation words (migration 012 adds them to
  the vocabulary). An edge that recurs across stores is one edge.

Semantics Cosmos stated for this export (#562): every row is a COMPLETED
observation. INVALID attempts (C0 run 1, C1 run 1, the pinned C0b replay) have
NO rows by construction. A confirmed counterexample and an unconfirmed attack
row look alike here, because the confirmation stays in each store's
adversary.json on M2.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Dict, List, Tuple

from atlas import db, gitsrc
from atlas.harvest import common as C

VERSION = "cosmos/1"
ENGINE = "cosmos"
PROGRAM = "cosmos"
RUN_HOST = "M2"
EXPORT = "roles/Cosmos/campaigns/atlas_export_c0"
FILES = (("atlas_fact.jsonl", "fact_jsonl_sha256", "facts"), ("atlas_edge.jsonl", "edge_jsonl_sha256", "edges"))
LEDGERS = (("cwe.sqlite", "sqlite_sha256"), ("receipts.jsonl", "receipts_sha256"))


class ManifestMismatch(RuntimeError):
    pass


def verify(manifest: dict, read) -> Dict[Tuple[str, str], bytes]:
    """read(store, filename) -> bytes or None. Returns the verified bytes per
    (store, file), or raises ManifestMismatch listing EVERY problem found."""
    out, bad = {}, []
    for store, m in sorted((manifest.get("stores") or {}).items()):
        for fname, hkey, nkey in FILES:
            data = read(store, fname)
            if data is None:
                bad.append("{}/{}: missing".format(store, fname))
                continue
            got = hashlib.sha256(data).hexdigest()
            if got != m.get(hkey):
                bad.append("{}/{}: sha256 {} != MANIFEST {}".format(store, fname, got[:16], str(m.get(hkey))[:16]))
                continue
            rows = sum(1 for x in data.splitlines() if x.strip())
            if m.get(nkey) is not None and rows != m[nkey]:
                bad.append("{}/{}: {} rows != MANIFEST {}".format(store, fname, rows, m[nkey]))
                continue
            out[(store, fname)] = data
    if not manifest.get("stores"):
        bad.append("MANIFEST lists no stores")
    if bad:
        raise ManifestMismatch("; ".join(bad))
    return out


def campaign_of(store: str) -> str:
    m = re.match(r"(c\d+)", store)
    return m.group(1) if m else "unassigned"


def _purpose(method: str) -> str:
    m = re.search(r"purpose=(\S+)", method or "")
    return m.group(1) if m else None


def run(args) -> dict:
    ref = args.ref
    files = {p: (s, z) for p, s, z in gitsrc.ls_tree(ref, EXPORT)}
    newest, oldest, _touch = gitsrc.path_commits(ref, EXPORT)
    mpath = EXPORT + "/MANIFEST.json"
    if mpath not in files:
        raise ManifestMismatch("no MANIFEST.json under {} at {}".format(EXPORT, ref))
    b = C.Batch("cosmos", VERSION, "Cosmos")
    with gitsrc.CatFile() as cat:
        manifest = cat.json(files[mpath][0])

        def read(store, fname):
            p = "{}/{}/{}".format(EXPORT, store, fname)
            return cat.read(files[p][0]) if p in files else None
        data = verify(manifest, read)          # nothing below runs unless every file verified

    def src(path, text=None, obj=None):
        s, z = files[path]
        return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), text=text, obj=obj)

    muri = src(mpath, obj=manifest)
    closed = manifest.get("closed_at")
    for store, m in sorted(manifest["stores"].items()):
        cnat = campaign_of(store)
        ck = C.campaign_key(PROGRAM, cnat)
        b.campaign(campaign_key=ck, program=PROGRAM, native_id=cnat, engine_id=ENGINE, driver_seat="Cosmos",
                   title="Cosmos {} (from the atlas_export_c0 export)".format(cnat.upper()),
                   extract={"grouping": "INFERRED from the store name prefix c<N>", "closed_at": closed})
        ek = C.experiment_key(ck, store)
        facts = [json.loads(x) for x in data[(store, "atlas_fact.jsonl")].decode("utf-8").splitlines() if x.strip()]
        edges = [json.loads(x) for x in data[(store, "atlas_edge.jsonl")].decode("utf-8").splitlines() if x.strip()]
        purposes: Dict[str, int] = {}
        for f in facts:
            p = _purpose(f.get("method")) or "?"
            purposes[p] = purposes.get(p, 0) + 1
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id=store, kind="experiment",
                     title="Cosmos store {}".format(store), driver_seat="Cosmos", atlas_class="UNKNOWN",
                     atlas_class_confidence="LOW",
                     atlas_class_method="export carries per-world verdicts, no store-level disposition",
                     validity_state="VALID",
                     extract={"runtime_dir": m.get("runtime_dir"), "facts": m.get("facts"), "edges": m.get("edges"),
                              "purposes": purposes, "closed_at": closed},
                     inferred={"validity": "Cosmos #562: every exported row is a completed observation; INVALID "
                                           "attempts are excluded from the export, not labelled"})
        rdir = (m.get("runtime_dir") or "").replace("\\", "/")
        anat = rdir.rsplit("/", 1)[-1] or store
        ak = C.attempt_key(ek, anat)
        b.attempt(attempt_key=ak, experiment_key=ek, native_id=anat, attempt_no=1, of_record=True,
                  reported_status="COMPLETED", validity_state="VALID", host_id=RUN_HOST,
                  host_basis="DECLARED by Cosmos (#562, REPLY_TO_ATLAS_558.md): C0 host = M2 / SPECTREX5, every store",
                  operator_seat="Cosmos", worktree_path=rdir or None)
        b.link(muri, "experiment", ek, "manifest")
        for ledger, hkey in LEDGERS:
            lp = "{}/store/{}".format(rdir, ledger)
            lu = b.other_source("hostfile://{}/{}".format(RUN_HOST, lp), "file", "EXPECTED:" + RUN_HOST,
                                host_id=RUN_HOST, path=lp, file_sha256=m.get(hkey), present=None)
            b.link(lu, "attempt", ak, "runtime_ledger")
        furi = src("{}/{}/atlas_fact.jsonl".format(EXPORT, store), text=data[(store, "atlas_fact.jsonl")].decode("utf-8"))
        euri = src("{}/{}/atlas_edge.jsonl".format(EXPORT, store), text=data[(store, "atlas_edge.jsonl")].decode("utf-8"))
        b.t["source"][furi]["file_sha256"] = m["fact_jsonl_sha256"]
        b.t["source"][euri]["file_sha256"] = m["edge_jsonl_sha256"]
        b.link(furi, "experiment", ek, "export_facts")
        b.link(euri, "experiment", ek, "export_edges")
        for f in facts:
            _fact(b, f, furi)
        for e in edges:
            b.edge((e["src_type"], e["src_key"]), (e["dst_type"], e["dst_key"]), e["relation"], e["lineage_kind"],
                   reason=e.get("reason") or "UNKNOWN", basis=e.get("basis") or "DECLARED",
                   confidence=e.get("confidence") or "MEDIUM", detail=e.get("detail"), uri=euri)
        b.fact("RAN", "telemetry_availability", "experiment", ek, "cosmos.export_rows",
               {"facts": len(facts), "edges": len(edges), "purposes": purposes}, furi, "", author="ATLAS_DERIVED")
    with db.harvest("cosmos", VERSION, source_ref="{}:{} (MANIFEST-verified)".format(ref, EXPORT)) as h:
        return b.flush(h)


def _fact(b: C.Batch, f: dict, uri: str) -> None:
    """One exported row -> one Atlas fact, identity (subject, kind, name, store file, Cosmos fact_key)."""
    vj = f.get("value_json")
    native = {"native_method": f.get("method"), "purpose": _purpose(f.get("method"))}
    band = (f["band_low"], f["band_high"]) if f.get("band_low") is not None and f.get("band_high") is not None else None
    value = f.get("value_num") if f.get("value_num") is not None else f.get("value_text")
    b.fact(f["layer"], f["kind"], f["subject_type"], f["subject_key"], f["name"], value, uri, f["fact_key"],
           author=f.get("author") or "Cosmos", status=f.get("status") or "REPORTED", band=band)
    fk = C.h16(f["subject_type"], f["subject_key"], f["kind"], f["name"], uri, f["fact_key"])
    row = b.facts[fk]
    row["value_text"] = C.trunc(f.get("value_text"))
    row["value_num"] = f.get("value_num")
    payload = {**native, "value": vj} if vj is not None else native
    s = json.dumps(payload, sort_keys=True, default=str)
    row["value_json"] = payload if len(s) <= C.MAX_JSON else {**native, "value": "<{} chars; see source>".format(len(s))}
