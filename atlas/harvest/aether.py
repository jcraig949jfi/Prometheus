"""Source adapter: Aether (GPU-native artificial physics), V2-B flights and the C-002 experiments.

Sources on a git ref:
    roles/Aether/WORK_STATE.json      experiments[] = {id, status, verdict, report}: the seat's own index
    Aether/V2B/<ID>/                  PREREGISTRATION.md, RESULT.md, RULES.json, production/*.json,
                                      production/REDUCTION.json, attempts/*.json (TEST-*)
    ops/campaigns/C-002/E-NNN/        RESULT.md (+ prereg) of the C-002 experiments

Mapping (native ids only):
- experiment native id = the directory name (TEST-2, OFFER01, E-012). V2B
  experiments sit in campaign aether/V2B; E-NNN experiments sit in the
  workgraph campaign workgraph/C-002, so they join the workgraph harvester's
  campaign row (WORK_STATE campaigns[] maps C-002 = AETH-03).
- the verdict is WORK_STATE experiments[].verdict when present (verbatim),
  else the first `Preregistered disposition:` / `Scientific disposition:` /
  `Verdict:` heading of RESULT.md. Class: a token ending in _SUPPORTED or
  REPLICATED -> POSITIVE, _WEAK -> WEAK_POSITIVE, NO_GAIN / NOT_SUPPORTED ->
  NEGATIVE, PARTIAL -> INCONCLUSIVE; compound verdicts (with ';' or '/')
  keep confidence LOW; any other token stays UNKNOWN.
- attempts: one per production unit file production/<unit>.json (schema
  aether.*.unit.v1) and one per attempts/<unit>__A-NNN__<mode>-<HOST>.json.
  Host: the attempt filename names it; else the PREREGISTRATION header
  (`SPECTREX5, ...`) matched against the registry, labelled.
- RULES.json -> RAN condition facts; REDUCTION.json decision -> OBSERVED.
- Aether/runpod receipts are NOT read yet (a known gap, reported).
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from atlas import classify, db, gitsrc
from atlas.harvest import common as C

VERSION = "aether/1"
ENGINE = "aether"
V2B = "Aether/V2B"
C002 = "ops/campaigns/C-002"
WS = "roles/Aether/WORK_STATE.json"
FREEZE = re.compile(r"(?:frozen at|Freeze|freeze commit|Preregistration frozen at)\s+([0-9a-f]{7,40})", re.I)
DISP = re.compile(r"^#+\s*(?:Preregistered disposition|Scientific disposition|Verdict)\s*:\s*(.+)$", re.M | re.I)
ATT = re.compile(r"^(?P<unit>.+?)__(?P<att>A-\d+)__(?P<mode>[a-z]+)-(?P<host>[A-Za-z0-9-]+)\.json$")


def verdict_class(v: Optional[str]):
    if not v:
        return "UNKNOWN", "LOW"
    conf = "LOW" if re.search(r"[;/]", v) else "MEDIUM"
    head = re.split(r"[\s(;/]", v.strip(), 1)[0].upper()
    if re.search(r"NO_GAIN$|NOT_SUPPORTED$", head):
        return "NEGATIVE", conf
    if re.search(r"_SUPPORTED$|^REPLICATED$|REPLICATED$", head) or " REPLICATED" in v.upper():
        return "POSITIVE", conf
    if head.endswith("_WEAK"):
        return "WEAK_POSITIVE", conf
    if head == "PARTIAL":
        return "INCONCLUSIVE", conf
    return "UNKNOWN", "LOW"


def run(args) -> dict:
    ref = args.ref
    files: Dict[str, tuple] = {}
    newest, oldest = {}, {}
    for root in (V2B, C002, WS):
        for p, s, z in gitsrc.ls_tree(ref, root):
            files[p] = (s, z)
        n, o, _t = gitsrc.path_commits(ref, root)
        newest.update(n)
        oldest.update(o)
    b = C.Batch("aether", VERSION, "Aether")
    ck_v2b = C.campaign_key("aether", "V2B")
    b.campaign(campaign_key=ck_v2b, program="aether", native_id="V2B", engine_id=ENGINE, driver_seat="Aether",
               title="Aether V2-B (operator directive 2026-10-04, roles/Aether/prompts/2026-10-04_v2b_directive/)",
               extract={"grouping": "directory Aether/V2B"})
    ck_c002 = C.campaign_key("workgraph", "C-002")

    def src(path, obj=None, text=None):
        s, z = files[path]
        return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), obj=obj, text=text)

    dirs: Dict[str, tuple] = {}            # native id -> (campaign key, dir path)
    for p in files:
        m = re.match(r"^Aether/V2B/([^/]+)/RESULT\.md$", p)
        if m:
            dirs[m.group(1)] = (ck_v2b, "{}/{}".format(V2B, m.group(1)))
        m = re.match(r"^ops/campaigns/C-002/(E-\d+)/RESULT\.md$", p)
        if m:
            dirs[m.group(1)] = (ck_c002, "{}/{}".format(C002, m.group(1)))
    with gitsrc.CatFile() as cat:
        ws_v: Dict[str, dict] = {}
        ws_uri = None
        if WS in files:
            ws = cat.json(files[WS][0]) or {}
            ws_uri = src(WS, obj=ws)
            for e in ws.get("experiments") or []:
                if e.get("id"):
                    ws_v[e["id"]] = e
        for nat, (ck, d) in sorted(dirs.items()):
            ek = C.experiment_key(ck, nat)
            res_p = d + "/RESULT.md"
            res = cat.text(files[res_p][0]) or ""
            ru = src(res_p, text=res)
            pre_p = next((p for p in (d + "/PREREGISTRATION.md", d + "/PREREG.md") if p in files), None)
            pre = cat.text(files[pre_p][0]) if pre_p else None
            pu = src(pre_p, text=pre) if pre_p else None
            head = res.split("\n", 6)
            fm = FREEZE.search("\n".join(head[:6]))
            w = ws_v.get(nat)
            dm = DISP.search(res)
            verdict = (w or {}).get("verdict") or (dm.group(1).strip() if dm else None)
            vsrc = ws_uri if w and w.get("verdict") else ru
            cls, conf = verdict_class(verdict)
            host_txt = (pre or "").split("\n", 6)[:6]
            hid, hbasis = classify.host_from_text("\n".join(host_txt))
            b.experiment(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id=nat, driver_seat="Aether",
                         kind="aether.flight", title=head[0].lstrip("# ").strip()[:300],
                         reported_disposition=C.trunc(verdict, 300), atlas_class=cls, atlas_class_confidence=conf,
                         atlas_class_method="aether/1 verdict-token map", validity_state="UNKNOWN",
                         prereg_digest=fm.group(1) if fm else None,
                         extract={"dir": d, "work_state": w} if w else {"dir": d})
            b.link(ru, "experiment", ek, "result")
            if pu:
                b.link(pu, "experiment", ek, "prereg")
            if verdict:
                b.conclusion("experiment", ek, C.trunc(verdict, 300), _section(res, dm.start()) if dm else None, vsrc,
                             "experiments[{}]".format(nat) if vsrc == ws_uri else "RESULT.md disposition")
            rules_p = d + "/RULES.json"
            if rules_p in files:
                rules = cat.json(files[rules_p][0])
                uu = src(rules_p, obj=rules)
                b.link(uu, "experiment", ek, "rules")
                for k, v in C.flatten(rules, depth=2, limit=60):
                    b.fact("RAN", "condition", "experiment", ek, "aether.rules." + k, v, uu, k)
            red_p = d + "/production/REDUCTION.json"
            if red_p in files:
                red = cat.json(files[red_p][0]) or {}
                uu = src(red_p, obj=red)
                b.link(uu, "experiment", ek, "reduction")
                for k, v in C.flatten(red.get("decision") or {}, depth=3, limit=100):
                    b.fact("OBSERVED", "metric_summary", "experiment", ek, "aether.decision." + k, v, uu, "decision." + k)
                for k, v in C.flatten(red.get("gates") or {}, depth=2, limit=40):
                    b.fact("OBSERVED", "control", "experiment", ek, "aether.gates." + k, v, uu, "gates." + k)
            n = 0
            for p in sorted(files):
                if p.startswith(d + "/production/") and p.endswith(".json") and \
                        not re.search(r"/(REDUCTION|plan)\.json$", p):
                    unit = p.rsplit("/", 1)[-1][:-5]
                    obj = cat.json(files[p][0])
                    if not isinstance(obj, dict) or not str(obj.get("schema", "")).endswith(".unit.v1"):
                        continue
                    n += 1
                    _attempt(b, ek, unit, "A-001", obj, src(p, obj=obj), hid, ("PREREGISTRATION header: " + hbasis) if hbasis else
                             "no host in the PREREGISTRATION header or the unit file")
                m = re.match(re.escape(d) + r"/attempts/([^/]+)$", p)
                if m and ATT.match(m.group(1)):
                    a = ATT.match(m.group(1))
                    obj = cat.json(files[p][0])
                    mode = a.group("mode")
                    h2 = None if mode == "runpod" else _host_id(a.group("host"))
                    basis = ("RunPod cloud pod (attempt filename mode=runpod, receipt {}); not a fleet host".format(
                        a.group("host")) if mode == "runpod" else
                        "attempt filename names host {} (mode {})".format(a.group("host"), mode))
                    n += 1
                    _attempt(b, ek, a.group("unit"), a.group("att"), obj if isinstance(obj, dict) else {},
                             src(p, obj=obj), h2, basis)
            b.fact("RAN", "telemetry_availability", "experiment", ek, "aether.units_indexed", n, ru, "",
                   author="ATLAS_DERIVED")
    with db.harvest("aether", VERSION, source_ref="{}:{},{},{}".format(ref, V2B, C002, WS)) as h:
        return b.flush(h)


def _host_id(name: str) -> Optional[str]:
    for m in db.registry()["hosts"]:
        if name.lower() in [a.lower() for a in m["aliases"]] or (m.get("hostname") or "").lower() == name.lower():
            return m["host_id"]
    return None


def _attempt(b, ek, unit, att, obj, uri, hid, hbasis):
    ak = C.attempt_key(ek, "{}/{}".format(unit, att))
    b.attempt(attempt_key=ak, experiment_key=ek, native_id="{}/{}".format(unit, att),
              attempt_no=int(att.split("-")[1]), of_record=True, reported_status=None if obj.get("status", obj.get("rc")) is None else str(obj.get("status", obj.get("rc"))),
              validity_state="UNKNOWN", host_id=hid, host_basis=hbasis, operator_seat="Aether",
              duration_s=obj.get("wall_seconds"),
              extract={k: obj.get(k) for k in ("schema", "runner", "backend", "law", "arm", "variant", "seed_index",
                                               "semantics_id", "gpu") if obj.get(k) is not None})
    b.link(uri, "attempt", ak, "unit")
    for k in ("seed_index", "law", "arm", "variant", "n", "ticks"):
        if obj.get(k) is not None:
            b.fact("RAN", "parameter", "attempt", ak, "aether." + k, obj[k], uri, k)
    for k in ("p1_class", "final_digest", "result_sha256"):
        if obj.get(k) is not None:
            b.fact("OBSERVED", "measurement", "attempt", ak, "aether." + k, obj[k], uri, k)


def _section(text: str, start: int) -> str:
    nxt = re.search(r"^#+\s", text[start + 1:], re.M)
    return C.trunc(text[start:start + 1 + nxt.start()] if nxt else text[start:], 2000)
