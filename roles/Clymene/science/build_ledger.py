"""Assemble the disposition ledger from the three measurement runs.

Inputs (all produced by this pass, all committed beside the verdict):
  repo_audit.jsonl         reproducibility + completeness, with 4 controls
  consumption_audit.jsonl  consumption census, with 1 control
  model_audit.jsonl        model provenance + integrity + reproducibility

Buckets are the operator's, applied by the preregistered precedence:
INVALID/STUB/MISRECORDED wins over the four REPRODUCIBLE x CONSUMED cells;
UNKNOWN only where a test could not run.
"""
from __future__ import annotations

import json
import os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
LEDGER_DIR = "D:/Prometheus-worktrees/clymene-base-role/roles/Clymene/ledgers"

# autogen-landing.jpg: the upstream blob at that commit is a Git LFS POINTER
# (131 bytes); the file on disk is the smudged 269 KB image whose sha256 equals
# the pointer's oid (verified by hand, 2026-09-11). The comparator flagged it
# as a content mismatch; it is not one. Preregistration annotation, see the
# ledger's section 6.
LFS_EXONERATED = {("autogen", "autogen-landing.jpg")}


def load(name):
    p = os.path.join(SCRATCH, name)
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def gib(n):
    return round(n / (1024 ** 3), 2)


def main():
    ra = load("repo_audit.jsonl")
    ca = load("consumption_audit.jsonl")
    ma = load("model_audit.jsonl")
    wp = {r["dir"]: r for r in load("weights_probe.jsonl")
          if r["kind"] == "weights_probe"}
    wpc = [r for r in load("weights_probe.jsonl") if r["kind"] == "control"]

    repos = {r["name"]: r for r in ra if r["kind"] == "repo"}
    rcons = {r["name"]: r for r in ca if r["kind"] == "repo_consumption"}
    mcons = {r["dir"]: r for r in ca if r["kind"] == "model_consumption"}
    models = {r["dir"]: r for r in ma if r["kind"] == "model"}
    controls = ([r for r in ra if r["kind"] == "control"]
                + [r for r in ca if r["kind"] == "control"]
                + [r for r in ma if r["kind"] == "control"] + wpc)

    rows = []
    for name in sorted(repos, key=lambda n: repos[n]["i"]):
        r = repos[name]
        c = rcons.get(name, {})
        comp = r.get("completeness") or {}
        mismatch = comp.get("content_mismatch", 0)
        for rn, fn in LFS_EXONERATED:
            if rn == name and mismatch:
                mismatch -= 1
        repro = bool(r.get("reproducible"))
        consumed = bool(c.get("CONSUMED"))
        bucket = ("REPRODUCIBLE + CONSUMED" if repro and consumed else
                  "REPRODUCIBLE + UNCONSUMED" if repro else
                  "IRREPRODUCIBLE + CONSUMED" if consumed else
                  "IRREPRODUCIBLE + UNCONSUMED")
        rows.append({
            "kind": "repo", "name": name, "bucket": bucket,
            "reproducible": repro, "consumed": consumed,
            "upstream_files": comp.get("comparable_entries"),
            "files_on_disk": comp.get("local_files"),
            "completeness": comp.get("match_fraction"),
            "content_mismatch_after_lfs": mismatch,
            "extra_on_disk": comp.get("extra_on_disk"),
            "import_refs_in_live_code": c.get("import_ref_code"),
            "import_resolves_to_vault": c.get("IDENTITY_RESOLVES_TO_VAULT"),
            "path_refs_in_live_code": c.get("path_ref_code"),
            "registry_commit": r.get("registry_commit"),
            "url": r.get("url"),
            "note": c.get("note", ""),
        })

    mrows = []
    for d in sorted(models):
        m = models[d]
        c = mcons.get(d, {})
        stub = not m.get("PAYLOAD_PRESENT") or m.get("registry_status") == "download_failed"
        w = wp.get(d, {})
        # A model is REPRODUCIBLE only if its WEIGHTS resolve at the recorded
        # revision. The first probe HEADed one sidecar-covered file, which on a
        # gated repo is a public README returning 200 -- green for the wrong
        # reason. This can only move a row toward IRREPRODUCIBLE, never away.
        repro = m.get("REPRODUCIBLE")
        if w.get("weights_obtainable") is False:
            repro = False
        elif w.get("weights_obtainable") is True and repro is None:
            repro = None
        consumed = bool(c.get("CONSUMED"))
        if stub:
            bucket = "INVALID / STUB / MISRECORDED"
        elif repro is None:
            bucket = "UNKNOWN"
        else:
            bucket = (("REPRODUCIBLE" if repro else "IRREPRODUCIBLE") + " + "
                      + ("CONSUMED" if consumed else "UNCONSUMED"))
        mrows.append({
            "kind": "model", "dir": d, "hf_id": m.get("hf_id"), "bucket": bucket,
            "payload_present": m.get("PAYLOAD_PRESENT"),
            "bytes_on_disk": m.get("bytes_on_disk"),
            "gib": gib(m.get("bytes_on_disk") or 0),
            "integrity_ok": m.get("integrity_ok"), "integrity_checked": m.get("integrity_checked"),
            "integrity_failed": m.get("integrity_failed"),
            "integrity_verified": m.get("INTEGRITY_VERIFIED"),
            "recorded_revision": m.get("recorded_revision"),
            "provenance_complete": m.get("PROVENANCE_COMPLETE"),
            "registry_records_revision": False,
            "reproducible": repro, "repro_note": m.get("repro_note"),
            "weights_obtainable": w.get("weights_obtainable"),
            "weights_probe_status": w.get("status"),
            "weights_probe_note": w.get("note", ""),
            "repro_http_status": m.get("repro_http_status"),
            "consumed_path": c.get("CONSUMED_PATH"),
            "id_referenced_in_code": c.get("ID_REFERENCED_IN_CODE"),
            "id_code_sample": c.get("hf_id_ref_code_sample", []) + c.get("short_ref_code_sample", []),
            "also_in_hf_cache": m.get("ALSO_IN_HF_CACHE"),
            "registry_status": m.get("registry_status"),
            "registry_row_present": m.get("registry_row_present"),
        })

    os.makedirs(LEDGER_DIR, exist_ok=True)
    out = os.path.join(LEDGER_DIR, "VAULT_DISPOSITION_ROWS_2026-09-11.jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"kind": "meta", "generated_by": "roles/Clymene",
                             "preregistration": "roles/Clymene/PREREGISTRATION_2026-09-11_vault_audit.md",
                             "scope": "the vault as it exists on M2 (SPECTREX5); M1 unmeasured from here",
                             "repo_rows": len(rows), "model_rows": len(mrows),
                             "controls": len(controls)}) + "\n")
        for c in controls:
            fh.write(json.dumps(c) + "\n")
        for r in rows + mrows:
            fh.write(json.dumps(r) + "\n")

    # ---- console summary the write-up is built from
    print("CONTROLS:")
    for c in controls:
        print("  %-28s PASS=%s" % (c["control"], c.get("PASS")))
    print()
    from collections import Counter
    print("REPO BUCKETS:", dict(Counter(r["bucket"] for r in rows)))
    print("MODEL BUCKETS:", dict(Counter(r["bucket"] for r in mrows)))
    print()
    tot_up = sum(r["upstream_files"] or 0 for r in rows)
    tot_disk = sum(r["files_on_disk"] or 0 for r in rows)
    print("repo files upstream=%d on_disk=%d completeness=%.4f" %
          (tot_up, tot_disk, tot_disk / tot_up))
    print("repo content mismatches after LFS exoneration:",
          sum(r["content_mismatch_after_lfs"] for r in rows))
    print("repos consumed:", sum(1 for r in rows if r["consumed"]), "of", len(rows))
    print()
    payload = [m for m in mrows if m["payload_present"]]
    stubs = [m for m in mrows if not m["payload_present"]]
    print("models with payload:", len(payload), " stubs:", len(stubs))
    print("model bytes total  : %.2f GiB" % gib(sum(m["bytes_on_disk"] or 0 for m in mrows)))
    print("integrity verified :", sum(1 for m in payload if m["integrity_verified"]), "of", len(payload))
    print("provenance complete:", sum(1 for m in payload if m["provenance_complete"]), "of", len(payload))
    print("reproducible       :", sum(1 for m in payload if m["reproducible"]), "of", len(payload))
    print("weights obtainable :", sum(1 for m in mrows if m["weights_obtainable"]), "of", len(mrows))
    gated = [m for m in mrows if m["weights_obtainable"] is False]
    print("GATED              :", [(m["dir"], m["gib"]) for m in gated])
    keep = [m for m in mrows if m["payload_present"] and not m["reproducible"]]
    drop = [m for m in mrows if m["payload_present"] and m["reproducible"]]
    print("MUST PRESERVE (intact + not re-obtainable): %s  %.2f GiB"
          % ([m["dir"] for m in keep], sum(m["gib"] for m in keep)))
    print("DELETION-ELIGIBLE models (reproducible + unconsumed): %d  %.2f GiB"
          % (len(drop), sum(m["gib"] for m in drop)))
    print("consumed by path   :", sum(1 for m in mrows if m["consumed_path"]))
    print("id referenced      :", sum(1 for m in mrows if m["id_referenced_in_code"]))
    print("also in hf cache   :", sum(1 for m in mrows if m["also_in_hf_cache"]))
    print()
    for m in mrows:
        print("  %-44s %-30s %7.2f GiB int=%s/%s repro=%s idref=%s" % (
            m["dir"][:44], m["bucket"], m["gib"], m["integrity_ok"], m["integrity_checked"],
            m["reproducible"], m["id_referenced_in_code"]))
    print()
    print("wrote", out)


if __name__ == "__main__":
    main()
