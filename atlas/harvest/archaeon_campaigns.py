"""Source adapter: Archaeon campaigns driven through the SFE
(archaeon/campaign{N}/ on a git ref, default origin/main).

Identity: campaign = directory campaignN (NOT the RECEIPT.campaign field,
which says 'cmp2' for all of cmp3 and parts of cmp5 -- runner reuse; the
PEW ingestion contract rule T1 makes the same call). Experiment = a
subdirectory holding PREREG/RECEIPT/REHEARSAL files. Attempt = entries of
ATTEMPTS.json (C2+) or RECEIPT_attempt1.json + RECEIPT.json (C1).
Segment = receipt steps (idem:*). Engine records (exp_/obs_ ids) become
ledger:// pointers, not copies.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Dict, Optional

from atlas import classify, db, gitsrc
from atlas.harvest import common as C

VERSION = "archaeon_campaigns/3"
PROGRAM = "archaeon.campaign"
ROLE_BY_NAME = [
    (r"^PREREG\.json$", "prereg"), (r"^PREREG\.md$", "prereg"), (r"^DESIGN\.md$", "design"),
    (r"^READOUT\.md$", "readout"), (r"^RECORD(\.generated)?\.md$", "record"), (r"^RECEIPT.*\.json$", "receipt"),
    (r"^ATTEMPTS\.json$", "registry"), (r"^addendum\.json$", "report"), (r"^rows.*\.json$", "rows"),
    (r"^CAMPAIGN_REPORT\.md$", "report"), (r"^LEDGER\.jsonl$", "ledger"), (r"^DECISIONS\.md$", "decision"),
    (r"^JOURNAL\.md$", "journal"), (r"^FUNNEL\.json$", "registry"), (r"^PLAN\.md$", "design"),
    (r"^DISPOSITION.*", "report"), (r"^SUPERSESSION.*\.md$", "report"), (r"\.py$", "code"),
    (r"^(REACHABILITY|CORRIDOR)\.jsonl$", "rows"), (r"^REHEARSAL.*\.json$", "receipt"),
    (r"^CALIBRATION.*\.json$", "telemetry"), (r"\.json(\.gz)?$", "telemetry"), (r"\.md$", "report"),
]
EXP_FILES = {"PREREG.json", "RECEIPT.json", "ATTEMPTS.json"}
DECISION_LINE = re.compile(r"^(D\d+-\d{3})\s*\|\s*([^|]*)\|\s*(.*)$")


def role_for(name: str) -> str:
    for pat, role in ROLE_BY_NAME:
        if re.search(pat, name):
            return role
    return "other"


def run(args) -> dict:
    ref = args.ref
    sha = gitsrc.resolve(ref)
    files = gitsrc.ls_tree(ref, "archaeon")
    newest, oldest, touching = gitsrc.path_commits(ref, "archaeon")
    b = C.Batch("archaeon_campaigns", VERSION, "Archaeon")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            b.local_shas = C.local_commits(cur)
    finally:
        conn.close()

    by_camp: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for path, blob, size in files:
        m = re.match(r"archaeon/(campaign\d+)/(.*)$", path)
        if m:
            parts = m.group(2).split("/")
            by_camp[m.group(1)][parts[0] if len(parts) > 1 else ""].append((path, blob, size))

    native_to_key: Dict[str, str] = {}
    with gitsrc.CatFile() as cat:
        def src(path, blob, size, parse=True):
            obj = text = None
            if parse and (path.endswith(".json") or path.endswith(".jsonl")) and size < 20_000_000:
                if path.endswith(".json"):
                    obj = cat.json(blob)
                else:
                    text = cat.text(blob)
            return b.git_source(ref, path, blob, size, newest.get(path), oldest.get(path), obj=obj, text=text), obj, text

        pending_parents = []
        for camp, groups in sorted(by_camp.items()):
            n = re.sub(r"\D", "", camp)
            native = "cmp" + n
            ckey = C.campaign_key(PROGRAM, native)
            b.campaign(campaign_key=ckey, program=PROGRAM, native_id=native, engine_id="sfe",
                       driver_seat="Archaeon", title="Archaeon campaign {}".format(n))
            # campaign-level files and non-experiment subdirectories
            for sub, flist in groups.items():
                is_exp = sub and (any(p.rsplit("/", 1)[-1] in EXP_FILES for p, _, _ in flist)
                                  or re.match(r"^(C\d-|SFE-|G\d-)", sub))
                if is_exp:
                    continue
                for path, blob, size in flist:
                    name = path.rsplit("/", 1)[-1]
                    uri, obj, text = src(path, blob, size, parse=not path.endswith(".py"))
                    role = role_for(name)
                    b.link(uri, "campaign", ckey, role)
                    if name == "LEDGER.jsonl" and text:
                        for i, row in enumerate(_jsonl(text), 1):
                            _ledger_defect(b, ckey, uri, i, row)
                    if name == "DECISIONS.md":
                        _decisions(b, ckey, cat.text(blob) or "", uri, native_to_key)
                    if name.startswith("SUPERSESSION") and name.endswith(".md"):
                        pending_parents.append(("supersession", ckey, cat.text(blob) or "", uri))
                    if isinstance(obj, dict) and name.startswith("CAMPAIGN") and "seed" in obj:
                        b.campaign(campaign_key=ckey, seed=str(obj.get("seed")))
            for sub, flist in sorted(groups.items()):
                if not sub or not (any(p.rsplit("/", 1)[-1] in EXP_FILES for p, _, _ in flist)
                                   or re.match(r"^(C\d-|SFE-|G\d-)", sub)):
                    continue
                ekey = C.experiment_key(ckey, sub)
                native_to_key.setdefault(sub, ekey)
                _experiment(b, cat, ref, ckey, ekey, sub, flist, src, touching, pending_parents)
        # declared parents resolve after every campaign is known
        for kind, ekey, payload, uri in pending_parents:
            if kind == "parents":
                parents, detail = payload
                for p in parents:
                    pkey = native_to_key.get(p) or C.experiment_key(PROGRAM + "/?", p)
                    b.edge(("experiment", ekey), ("experiment", pkey), "DESCENDANT_OF", "SCIENTIFIC",
                           reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH",
                           detail=detail, uri=uri, locator="parents")
            elif kind == "supersession":
                _supersession(b, payload, uri, native_to_key)

    with db.harvest("archaeon_campaigns", VERSION, source_ref=ref, source_sha=sha) as h:
        return b.flush(h)


def _jsonl(text):
    import json
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                v = json.loads(line)
                if isinstance(v, dict):
                    yield v
            except ValueError:
                pass


def _experiment(b, cat, ref, ckey, ekey, sub, flist, src, touching, pending):
    docs: Dict[str, Any] = {}
    uris: Dict[str, str] = {}
    attempt_files = defaultdict(list)
    for path, blob, size in flist:
        rel = path.split("/", 3)[3]
        name = rel.rsplit("/", 1)[-1]
        m = re.match(r"attempts/(a\d+)/", rel)
        big = size > 20_000_000 or name.endswith(".gz")
        uri, obj, _text = src(path, blob, size, parse=not big and not name.endswith(".py"))
        if m:
            attempt_files[m.group(1)].append((name, uri, obj))
            continue
        b.link(uri, "experiment", ekey, role_for(name))
        docs[name] = obj
        uris[name] = uri
        b.commits("experiment", ekey, touching.get(path, []))
    prereg = docs.get("PREREG.json") if isinstance(docs.get("PREREG.json"), dict) else {}
    receipt = docs.get("RECEIPT.json") if isinstance(docs.get("RECEIPT.json"), dict) else {}
    attempts = docs.get("ATTEMPTS.json") if isinstance(docs.get("ATTEMPTS.json"), dict) else {}
    dc = receipt.get("disposition_candidate") if isinstance(receipt.get("disposition_candidate"), dict) else {}
    disp = dc.get("disposition") or receipt.get("disposition") or receipt.get("verdict")
    worlds = sorted((receipt.get("worlds") or {}).keys()) if isinstance(receipt.get("worlds"), dict) else []
    rec = _record_disposition(cat, flist)
    cls_basis = disp
    if not disp and rec:  # campaign 1 receipts carry no disposition; RECORD.md does (verbatim)
        disp = rec["word"]
        cls_basis = rec["science"] or rec["word"]
    slot = re.search(r"(\d+)$", sub)
    kind = "rehearsal" if "REH" in sub or sub.startswith("G6") else "experiment"
    budget = prereg.get("budget")
    b.experiment(
        experiment_key=ekey, campaign_key=ckey, engine_id="sfe", native_id=sub,
        slot=int(slot.group(1)) if slot and kind == "experiment" else None, kind=kind,
        title=C.trunc(prereg.get("title") or (rec or {}).get("title"), 500), question=C.trunc(prereg.get("question")),
        purpose=receipt.get("purpose"), driver_seat="Archaeon",
        world_family=", ".join(worlds) or None, search_family=None,
        seeds=[str(receipt["campaign_seed"])] if receipt.get("campaign_seed") else [],
        budget_summary=C.trunc(_short(budget), 500) if budget else None,
        reported_disposition=disp, reported_conclusion=C.trunc(dc.get("reason") or (rec or {}).get("text"), 1000),
        atlas_class=(classify.science_class(rec["science"])[0] if rec and cls_basis is rec.get("science") and rec["science"]
                     else classify.status_class(cls_basis)),
        atlas_class_confidence=(classify.science_class(rec["science"])[1] if rec and cls_basis is rec.get("science") and rec["science"]
                                else ("HIGH" if dc.get("disposition") else "MEDIUM")
                                if cls_basis and classify.status_class(cls_basis) != "UNKNOWN" else "LOW"),
        atlas_class_method="status_class/1 on " + ("receipt disposition" if dc.get("disposition") or receipt.get("disposition")
                                                   else "science_class/1 on RECORD.md DISPOSITION 'Science:' clause" if rec else "reported disposition"),
        validity_state=C.validity_from(disp, " ".join(map(str, receipt.get("errors") or []))[:2000] if receipt.get("errors") else None),
        prereg_digest=prereg.get("prereg_digest") or receipt.get("prereg_digest"),
        design_digest=prereg.get("design_digest"),
        result_summary=C.trunc(dc.get("claim_ceiling"), 500),
        extract={k: prereg[k] for k in ("ancestry", "claim_ceiling", "typed_failure_conditions") if k in prereg},
    )
    if receipt.get("campaign") and receipt.get("campaign") != "cmp" + re.sub(r"\D", "", ckey.split("/")[-1]):
        b.fact("RAN", "parameter", "experiment", ekey, "receipt.campaign_field_disagrees_with_path",
               receipt.get("campaign"), uris.get("RECEIPT.json"), "campaign", status="CONTRADICTORY", author="ATLAS_DERIVED")
    # facts: definition (prereg), what ran, what was observed, what was concluded
    pu = uris.get("PREREG.json")
    for key, kind_ in (("question", "open_question"), ("arms", "comparison_group"), ("decl", "comparison_group"),
                       ("positive_control", "control"), ("assay_capability_requirement", "control"),
                       ("falsification_condition", "condition"), ("kill_condition", "condition"),
                       ("replacement_condition", "condition"), ("primary_observable", "measurement"),
                       ("crn_policy", "parameter"), ("budget", "budget"), ("claim_ceiling", "condition"),
                       ("typed_failure_conditions", "condition"), ("machine_changes_exercised", "representation_descriptor"),
                       ("expected_machine_telemetry", "telemetry_availability"), ("parent_evidence", "mechanism_claim"),
                       ("reachability_estimate", "prediction"), ("predictions", "prediction"), ("why_this_slot", "campaign_decision")):
        if key in prereg:
            for name, val in C.flatten(prereg[key], "prereg." + key, depth=2, limit=30):
                b.fact("OBSERVED" if kind_ not in ("parameter", "budget") else "RAN", kind_, "experiment", ekey,
                       name, val, pu, name)
    if prereg.get("parents"):
        pending.append(("parents", ekey, (prereg["parents"],
                        "ancestry: {}; parent_evidence: {}".format(prereg.get("ancestry"), C.trunc(prereg.get("parent_evidence"), 600))), pu))
    ru = uris.get("RECEIPT.json")
    if receipt:
        for name, val in C.flatten(dc.get("evidence") or {}, "evidence", depth=2, limit=40):
            b.fact("OBSERVED", "measurement", "experiment", ekey, name, val, ru, "disposition_candidate." + name)
        for name, val in C.flatten(dc.get("battery") or {}, "battery", depth=1):
            b.fact("OBSERVED", "control", "experiment", ekey, name, val, ru, "disposition_candidate." + name)
        for name, val in C.flatten(receipt.get("summary") or {}, "summary", depth=3, limit=60):
            b.fact("OBSERVED", "metric_summary", "experiment", ekey, name, val, ru, name)
        for name, val in C.flatten(receipt.get("effects") or {}, "effects", depth=2, limit=40):
            b.fact("OBSERVED", "measurement", "experiment", ekey, name, val, ru, name)
        for name, val in C.flatten(receipt.get("typed_states") or {}, "typed_states", depth=1, limit=20):
            b.fact("OBSERVED", "anomaly", "experiment", ekey, name, val, ru, name)
        if receipt.get("errors"):
            b.fact("RAN", "failure_mode", "experiment", ekey, "receipt.errors", receipt["errors"], ru, "errors")
        b.conclusion("experiment", ekey, disp, "{} | claim ceiling: {}".format(dc.get("reason"), dc.get("claim_ceiling"))
                     if dc else None, ru, "disposition_candidate", stated_at=receipt.get("finished_at"))
        for d in receipt.get("decisions") or []:
            b.fact("CONCLUDED", "campaign_decision", "experiment", ekey, "decision", d, ru, "decisions")
    if rec and "RECORD.md" in uris:  # the record's own DISPOSITION paragraph, verbatim, with its line
        b.conclusion("experiment", ekey, rec["word"], rec["text"], uris["RECORD.md"], "line {}".format(rec["line"]))
    if "READOUT.md" in uris:  # the human readout is a conclusion held by pointer
        b.conclusion("experiment", ekey, None, "[READOUT.md] see source", uris["READOUT.md"], "READOUT.md")
    ad = docs.get("addendum.json")
    if isinstance(ad, dict):
        for k, v in ad.items():
            if isinstance(v, str):
                b.conclusion("experiment", ekey, None, v, uris["addendum.json"], k)
    # attempts
    _attempts(b, ekey, sub, receipt, attempts, attempt_files, uris, docs)


def _short(v) -> str:
    import json
    return json.dumps(v, sort_keys=True, default=str)


def _attempts(b, ekey, sub, receipt, attempts, attempt_files, uris, docs):
    entries = {}
    if isinstance(attempts.get("attempts"), dict):
        for k, a in attempts["attempts"].items():
            entries["a{:02d}".format(int(k))] = a
        of_record = attempts.get("of_record")
    else:
        of_record = None
    if not entries:  # campaign 1 shape: RECEIPT_attempt1.json (preserved) + RECEIPT.json (of record)
        if "RECEIPT_attempt1.json" in docs:
            entries["attempt1"] = {"receipt": docs["RECEIPT_attempt1.json"], "_uri": uris["RECEIPT_attempt1.json"]}
        if receipt:
            entries["record"] = {"receipt": receipt, "_uri": uris.get("RECEIPT.json"), "_of_record": True}
    prev = None
    for native in sorted(entries, key=lambda x: (x != "attempt1", x)):
        a = entries[native]
        akey = C.attempt_key(ekey, native)
        files = attempt_files.get(native, [])
        rec = a.get("receipt")
        rec_uri = a.get("_uri")
        for name, uri, obj in files:
            b.link(uri, "attempt", akey, role_for(name))
            if name == "RECEIPT.json" and isinstance(obj, dict):
                rec, rec_uri = obj, uri
        if rec is None and a.get("_of_record") is None and of_record is not None and native == "a{:02d}".format(int(of_record)):
            rec, rec_uri = receipt, uris.get("RECEIPT.json")
        rec = rec if isinstance(rec, dict) else {}
        eng = rec.get("engine") if isinstance(rec.get("engine"), dict) else {}
        ws = rec.get("workspace") if isinstance(rec.get("workspace"), dict) else {}
        host, basis = classify.host_from_text(ws.get("worktree_path"))
        ei = eng.get("engine_instance_id") or (rec.get("engine_version") or {}).get("engine_instance_id")
        if ei:
            eh, ebasis = classify.host_from_text(eng.get("base_url"))
            b.engine_instance(engine_instance_key=ei, engine_id="sfe", native_id=ei, host_id=eh,
                              schema_version=str(eng.get("schema_version") or (rec.get("engine_version") or {}).get("schema_version") or "") or None,
                              source_hash=eng.get("engine_source_hash"),
                              commit_sha=(rec.get("engine_version") or {}).get("source_commit"),
                              endpoint=eng.get("base_url"), first_seen_at=eng.get("pinned_at"),
                              last_seen_at=rec.get("finished_at"),
                              basis="receipt engine.base_url ({})".format(ebasis) if ebasis else "receipt",
                              extract={"runtime": (rec.get("engine_version") or {}).get("runtime"),
                                       "api": (rec.get("engine_version") or {}).get("api"),
                                       "pinned_by": eng.get("pinned_by")})
        t = rec.get("timings") if isinstance(rec.get("timings"), dict) else {}
        is_record = bool(a.get("_of_record")) or (of_record is not None and native == "a{:02d}".format(int(of_record)))
        errs = rec.get("errors") or []
        b.attempt(attempt_key=akey, experiment_key=ekey, native_id=native,
                  attempt_no=int(re.sub(r"\D", "", native)) if re.search(r"\d", native) else None,
                  of_record=is_record, reported_status=a.get("disposition_candidate") or
                  ((rec.get("disposition_candidate") or {}).get("disposition") if isinstance(rec.get("disposition_candidate"), dict) else None),
                  validity_state="SUPERSEDED" if (of_record is not None and not is_record) or native == "attempt1"
                  else C.validity_from(" ".join(map(str, errs))[:2000] if errs else None),
                  started_at=a.get("started_at") or rec.get("started_at"),
                  finished_at=a.get("finished_at") or rec.get("finished_at"),
                  duration_s=t.get("total_s"), host_id=host, host_basis=("runner worktree " + basis) if basis else None,
                  operator_seat="Archaeon", engine_instance_key=ei, branch=ws.get("branch"),
                  commit_sha=ws.get("base_sha"), code_digest=rec.get("runtime_hash"),
                  config_digest=rec.get("prereg_digest"), dirty=ws.get("dirty"), worktree_path=ws.get("worktree_path"),
                  budget={"purpose": a.get("purpose") or rec.get("purpose"), "engine_path": a.get("engine_path"),
                          "replayed_steps": a.get("replayed_steps"), "errors": len(errs) if isinstance(errs, list) else errs},
                  result_summary=C.trunc(((rec.get("disposition_candidate") or {}).get("reason")
                                          if isinstance(rec.get("disposition_candidate"), dict) else None), 500))
        if rec_uri:
            for name, val in C.flatten(t, "timings", depth=1):
                b.fact("RAN", "timing", "attempt", akey, name, val, rec_uri, name, unit="s")
            for sk, sv in (rec.get("steps") or {}).items():
                if isinstance(sv, dict):
                    b.segment(segment_key=C.segment_key(akey, sk), attempt_key=akey, native_id=sk, kind="step",
                              reported_status=str(sv.get("status") or sv.get("outcome") or "") or None,
                              extract={k: v for k, v in sv.items() if isinstance(v, (str, int, float, bool)) and len(str(v)) < 200})
            for fk, fv in (rec.get("records") or {}).items():
                if isinstance(fv, dict) and ei:
                    for idk in ("exp_id", "obs_id"):
                        if fv.get(idk):
                            u = b.other_source("ledger://{}/{}".format(ei, fv[idk]), "engine_ledger",
                                               "EXPECTED:{}".format(classify.host_from_text(eng.get("base_url"))[0] or "?"),
                                               engine_ledger_id=fv[idk], record_key=fk)
                            b.link(u, "attempt", akey, "engine_record")
        if prev is not None:
            rf = a.get("resumed_from")
            if rf is not None:
                b.edge(("attempt", akey), ("attempt", C.attempt_key(ekey, "a{:02d}".format(int(rf)))), "RESUMED_FROM",
                       "EXECUTION", reason="CONTINUATION", basis="DECLARED", confidence="HIGH",
                       detail="ATTEMPTS.json resumed_from={}".format(rf), uri=uris.get("ATTEMPTS.json"))
            else:
                b.edge(("attempt", akey), ("attempt", prev), "RERUN_OF", "EXECUTION", reason="UNKNOWN",
                       basis="INFERRED", confidence="MEDIUM",
                       detail="attempt order within {}; prior purpose={}, this purpose={}".format(
                           sub, (entries.get(prev.split("#")[-1]) or {}).get("purpose"), a.get("purpose")),
                       uri=uris.get("ATTEMPTS.json") or rec_uri)
        prev = akey


def _ledger_defect(b, ckey, uri, line, row):
    did = row.get("id")
    if not did:
        return
    dkey = "{}/{}".format(ckey, did)
    b.defect(defect_key=dkey, native_id=did, engine_id="sfe", campaign_key=ckey, category=row.get("category"),
             severity=row.get("severity"), title=C.trunc(row.get("symptom") or row.get("title"), 1000),
             reported_status="OPEN" if not row.get("resolved") else "RESOLVED", reported_at=row.get("recorded_at"),
             extract={k: row.get(k) for k in ("evidence", "proposed_fix", "proposed_telemetry", "recurrence",
                                             "blocks_future_runs", "workaround") if row.get(k) not in (None, "", [])})
    b.link(uri, "defect", dkey, "ledger")
    exp = row.get("experiment")
    if exp:
        b.edge(("experiment", C.experiment_key(ckey, exp)), ("defect", dkey), "AFFECTED_BY", "PROVENANCE",
               basis="DECLARED", confidence="HIGH", uri=uri, locator="line {}".format(line))


def _decisions(b, ckey, text, uri, native_to_key):
    for i, line in enumerate(text.splitlines(), 1):
        m = DECISION_LINE.match(line.strip())
        if m:
            did, when, title = m.group(1), m.group(2).strip(), m.group(3).strip()
            b.fact("CONCLUDED", "campaign_decision", "campaign", ckey, did, title, uri, "line {}".format(i),
                   stated_at=None)
            for x in re.findall(r"\bC\d-(?:SFE-)?\d{2}\b|\bSFE-\d{2}\b", title):
                b.fact("CONCLUDED", "campaign_decision", "experiment", C.experiment_key(ckey, x), did, title, uri,
                       "line {}".format(i))


def _supersession(b, text, uri, native_to_key):
    m1 = re.search(r"WHAT IS SUPERSEDED\.(.{0,400})", text, re.S)
    m2 = re.search(r"BY WHAT\.(.{0,300})", text, re.S)
    if not (m1 and m2):
        return
    old = re.findall(r"\bC\d-\d{2}\b", m1.group(1))
    new = re.findall(r"\bC\d-\d{2}\b", m2.group(1))
    if not old or not new:
        return
    ok, nk = native_to_key.get(old[0]), native_to_key.get(new[0])
    if not ok or not nk:
        return
    b.edge(("experiment", nk), ("experiment", ok), "SUPERSEDES", "SCIENTIFIC", reason="UNKNOWN", basis="DECLARED",
           confidence="HIGH", detail=C.trunc(" ".join(m1.group(1).split()), 600), uri=uri)
    b.conclusion("experiment", ok, "SUPERSEDED_INTERPRETATION", " ".join(m1.group(1).split()), uri, "WHAT IS SUPERSEDED",
                 status="SUPERSEDED_INTERPRETATION")


def _record_disposition(cat, flist):
    """The 'DISPOSITION: <WORD> ...' paragraph that closes a directive-IV
    RECORD.md (up to the next blank line), with its line number. The
    'Science:' clause, when present, is the scientific reading; the word
    before it (COMPLETE, INCONCLUSIVE, ...) is the execution/assay state."""
    blob = next((b for p, b, _z in flist if p.endswith("/RECORD.md") and "/attempts/" not in p), None)
    text = cat.text(blob) if blob else None
    if not text:
        return None
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else None
    for i, line in enumerate(lines):
        m = re.match(r"^DISPOSITION:\s*([A-Z_]+)", line)
        if m:
            para = []
            for j in range(i, len(lines)):
                if not lines[j].strip():
                    break
                para.append(lines[j].strip())
            full = " ".join(para)
            sci = re.search(r"Science:\s*(.*)", full)
            return {"word": m.group(1), "text": full, "line": i + 1, "title": title,
                    "science": sci.group(1)[:400] if sci else None}
    return None
