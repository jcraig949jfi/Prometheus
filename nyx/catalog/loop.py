"""The catalogue loop (Nyx, 2026-09-12): sources -> candidates -> classified bits, with controls after every commit.

    python -m nyx.catalog.loop status
    python -m nyx.catalog.loop next <source_id> <section_prefix> <n>      # print the next n PENDING entries
    python -m nyx.catalog.loop commit <batch.json>                          # apply a classification batch

A batch is a JSON list of decisions, one per candidate entry:
  {"source": "<source_id>", "entry": "<name>",
   "decision": "BIT" | "INSTANCE_OF" | "NOT_A_BIT" | "DEFER",
   "bit": {<full nyx.bit/0 record>}          # for BIT
   "bit_id": "<existing id>",                 # for INSTANCE_OF (adds the entry as an instance + source)
   "reason": "<one line>"}                     # for NOT_A_BIT / DEFER (a system, a lineage, a field, a duplicate name...)
Grades: a bit made from a list description is T2 unless a source read or a run is cited.
After commit: schema validation, recurrence report, planted controls; a failed control blocks the commit
(the batch is written to nyx/catalog/batches/rejected/ with the failure).
"""
from __future__ import annotations

import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

from nyx.catalog import controls, schema

ROOT = Path("nyx/catalog")


def _sources():
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "sources").glob("*.json")) if "n_entries" in json.loads(p.read_text(encoding="utf-8"))}


def status():
    bits = schema.load_all(ROOT / "bits")
    by_grade = {}
    for b in bits:
        by_grade[b["grade"]] = by_grade.get(b["grade"], 0) + 1
    print(f"bits {len(bits)} by grade {by_grade}")
    for sid, s in _sources().items():
        if "n_entries" not in s:  # a pointer list (e.g. a specimen vault), not a classification source
            print(f"  {sid}: {s.get('kind')} ({len(s.get('entries', []))} entries; {s.get('status')})")
            continue
        pend = sum(1 for e in s["entries"] if e["classification"] == "PENDING")
        done = {}
        for e in s["entries"]:
            done[e["classification"]] = done.get(e["classification"], 0) + 1
        print(f"  {sid}: {s['n_entries']} entries, pending {pend}, {done}")
    rec = schema.recurrences(bits)
    print(f"recurrence groups {len(rec)}")


def next_batch(sid: str, prefix: str, n: int):
    s = _sources()[sid]
    out = []
    for e in s["entries"]:
        if e["classification"] != "PENDING":
            continue
        if prefix and not " / ".join(e["section"]).startswith(prefix):
            continue
        out.append(e)
        if len(out) >= n:
            break
    for e in out:
        print(json.dumps({"entry": e["name"], "desc": e["description"][:200], "section": " / ".join(e["section"])}, ensure_ascii=False))
    print(f"-- {len(out)} entries")


def commit(batch_path: str) -> int:
    batch = json.loads(Path(batch_path).read_text(encoding="utf-8"))
    sources = _sources()
    written, instanced, not_bits, deferred = [], [], [], []
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    for d in batch:
        s = sources[d["source"]]
        # a name can appear in two sections of one list; classify the PENDING one first, then fall back to any
        entry = next((e for e in s["entries"] if e["name"] == d["entry"] and e["classification"] == "PENDING"), None)             or next((e for e in s["entries"] if e["name"] == d["entry"]), None)
        if entry is None:
            print("UNKNOWN ENTRY", d["entry"]); return 2
        if d["decision"] == "BIT":
            b = d["bit"]
            b.setdefault("schema", schema.SCHEMA)
            src_ref = {"ref": f"{s['page']} (revid {s.get('revid')}), entry '{entry['name']}' in section {' / '.join(entry['section'])}: {entry['description'][:160]}", "grade": "T2"}
            b.setdefault("sources", []).append(src_ref)
            b.setdefault("instances", []).append(entry["name"])
            f = schema.validate(b)
            if f:
                print("INVALID BIT", b.get("id"), f); return 2
            sub = ROOT / "bits" / d["source"]
            sub.mkdir(parents=True, exist_ok=True)
            (sub / (b["id"].replace("bit.", "").replace(".", "_") + ".json")).write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            entry["classification"] = "BIT"; entry["bit_id"] = b["id"]; written.append(b["id"])
        elif d["decision"] == "INSTANCE_OF":
            target = next((p for p in (ROOT / "bits").rglob("*.json") if json.loads(p.read_text(encoding="utf-8")).get("id") == d["bit_id"]), None)
            if target is None:
                print("NO SUCH BIT", d["bit_id"]); return 2
            b = json.loads(target.read_text(encoding="utf-8"))
            if entry["name"] not in b["instances"]:
                b["instances"].append(entry["name"])
            b["sources"].append({"ref": f"{s['page']} (revid {s.get('revid')}), entry '{entry['name']}': {entry['description'][:120]}", "grade": "T2"})
            target.write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            entry["classification"] = "INSTANCE_OF"; entry["bit_id"] = d["bit_id"]; instanced.append((entry["name"], d["bit_id"]))
        elif d["decision"] in ("NOT_A_BIT", "DEFER"):
            entry["classification"] = d["decision"]; entry["reason"] = d.get("reason", "")
            (not_bits if d["decision"] == "NOT_A_BIT" else deferred).append(entry["name"])
        else:
            print("BAD DECISION", d); return 2
        entry["classified_at"] = stamp
    for sid, s in sources.items():
        (ROOT / "sources" / f"{sid}.json").write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    out = controls.run(ROOT)
    (ROOT / "batches").mkdir(exist_ok=True)
    dest = ROOT / "batches" / (stamp.replace(":", "") + "_" + Path(batch_path).stem + ".json")
    shutil.copy(batch_path, dest)
    summary = {"stamp": stamp, "batch": str(dest), "bits_written": written, "instances": instanced, "not_bits": not_bits, "deferred": deferred,
               "controls_all_pass": out["all_pass"], "bits_total": out["bits"], "recurrence_groups": out["recurrence_groups"]}
    log = ROOT / "LOOP_LOG.jsonl"
    log.write_text((log.read_text(encoding="utf-8") if log.exists() else "") + json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    if not out["all_pass"]:
        print("CONTROLS FAILED -- inspect before the next batch"); return 1
    return 0


def main(argv):
    if argv[1] == "status":
        status()
    elif argv[1] == "next":
        next_batch(argv[2], argv[3] if len(argv) > 3 else "", int(argv[4]) if len(argv) > 4 else 30)
    elif argv[1] == "commit":
        return commit(argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
