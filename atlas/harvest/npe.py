"""Source adapter: the Nestor Primordial Engine (NPE).

Reads a git ref that holds primordial/ and the CW01 campaign. On
2026-09-19 that ref is the M1-LOCAL branch
nestor/sidequest-graphworld-2026-09-14 (origin/main has no primordial/);
sources from commits not on any remote ref are recorded GIT_LOCAL:M1.

Two programs:
  nestor.graphworld  rounds r1..r8 -- receipts primordial/ledger/<Lane>.jsonl
                     (one receipt = one attempt of exp_id; supersedes /
                     rerun_of / parent_* are declared edges)
  nestor.cw01        CW01 -- CAMPAIGN_STATE.json experiments e01..e10 and
                     their attempts; the revisit/perturb/stasis loop:
                     TRAJECTORIES (ideas), PERTURBATIONS (experiments;
                     append-only, amend records merged in order), STATE
                     (stasis facts), EVIDENCE (observations), DEFECTS.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict

from atlas import classify, db, gitsrc
from atlas.harvest import common as C

VERSION = "npe/5"
DEFAULT_REF = "nestor/sidequest-graphworld-2026-09-14"
GW = "nestor.graphworld"
CW = "nestor.cw01"
CWDIR = "roles/Nestor/campaigns/cw01-2026-09-17"
TYPE_REASON = [("transplant", "CROSS_SUBSTRATE_TRANSPLANT"), ("stasis-escape", "STASIS_ESCAPE"),
               ("replication", "REPLICATION"), ("pressure", "PRESSURE_DEFORMATION"),
               ("deformation", "PARAMETER_DEFORMATION"), ("one-axis", "PARAMETER_DEFORMATION"),
               ("parameterized", "PARAMETER_DEFORMATION"), ("break", "CONTROL_REPAIR"),
               ("reanalysis", "MORE_TELEMETRY"), ("cross", "CROSS_SUBSTRATE_TRANSPLANT")]
AXIS_REASON = {"world_geometry": "WORLD_DEFORMATION", "representation": "REPRESENTATION_CHANGE",
               "mutation_geometry": "PARAMETER_DEFORMATION", "search_dynamics": "PARAMETER_DEFORMATION",
               "search_depth": "PARAMETER_DEFORMATION", "damage_rescue": "PARAMETER_DEFORMATION"}
SFE_ID = re.compile(r"\bC[1-6]-(?:SFE-)?\d{2}\b")


def _npe_refs(explicit=None):
    """Nestor works on many branches and moves between them (sidequest-graphworld,
    s1-forensics, arch4-loop ...). Reading one hardcoded ref silently goes stale,
    so discover every nestor ref that carries the CW01 campaign or the primordial
    ledger and read them oldest-first, newest last (upserts merge; newest wins)."""
    if explicit:
        return [explicit]
    cands = []
    for name, sha, date in gitsrc.refs(("refs/remotes/origin", "refs/heads")):
        short = name.replace("refs/remotes/", "").replace("refs/heads/", "")
        if "nestor" not in short.lower():
            continue
        has = gitsrc.git("ls-tree", "--name-only", sha, "--", CWDIR, "primordial/ledger", check=False).strip()
        if has:
            cands.append((date, short))
    cands.sort()
    seen, out = set(), []
    for _date, short in cands:
        if short not in seen:
            seen.add(short)
            out.append(short)
    return out[-4:] if out else [DEFAULT_REF]


def run(args) -> dict:
    refs = _npe_refs(args.npe_ref if getattr(args, "npe_ref", None) else None)
    counts = {}
    for ref in refs:
        counts = _run_one(ref)
        counts["refs_read"] = len(refs)
    return counts


def _run_one(ref) -> dict:
    sha = gitsrc.resolve(ref)
    if not sha:
        raise RuntimeError("NPE ref {} not visible on this host (it is M1-local); nothing inferred as absent".format(ref))
    b = C.Batch("npe", VERSION, "Nestor")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            b.local_shas = C.local_commits(cur)
            cur.execute("SELECT native_id, experiment_key FROM atlas.experiment WHERE campaign_key LIKE 'archaeon.campaign/%'")
            sfe = dict(cur.fetchall())
    finally:
        conn.close()
    with gitsrc.CatFile() as cat:
        _rounds(b, cat, ref)
        _cw01(b, cat, ref, sfe)
    with db.harvest("npe", VERSION, source_ref=ref, source_sha=sha,
                    notes="host-local ref" if ref.startswith("nestor/") else None) as h:
        return b.flush(h)


# ---------------------------------------------------------------- rounds

def _round_of(exp_id: str) -> str:
    """'<Lane>-R<n>-...' names round n for n in 1..8 (the rounds that ran).
    R16 in G-R16-* is a regime label, not a round (NPE survey 2026-09-19):
    such ids go to 'unassigned' rather than a fabricated round."""
    m = re.match(r"^[A-Z]\d*-R(\d+)-", exp_id)
    if m:
        return "r" + m.group(1) if 1 <= int(m.group(1)) <= 8 else "unassigned"
    return "r1"


def _rounds(b, cat, ref):
    files = gitsrc.ls_tree(ref, "primordial/ledger")
    files += gitsrc.ls_tree(ref, "roles/Nestor/sidequests/graphworld/epochs")
    newest, oldest, touching = gitsrc.path_commits(ref, "primordial/ledger")
    n2, o2, _ = gitsrc.path_commits(ref, "roles/Nestor/sidequests/graphworld/epochs")
    newest.update(n2)
    oldest.update(o2)
    blobs = {p: (s, z) for p, s, z in files}
    rows_by_exp = {}
    for p in blobs:
        m = re.match(r"primordial/ledger/rows/([A-Z])/(.+?)\.jsonl$", p)
        if m:
            rows_by_exp[m.group(2)] = p
    for p, (s, z) in blobs.items():
        m = re.match(r"roles/Nestor/sidequests/graphworld/epochs/ROUND_(r\d+)\.json$", p)
        if m:
            ck = C.campaign_key(GW, m.group(1))
            b.campaign(campaign_key=ck, program=GW, native_id=m.group(1), engine_id="npe", driver_seat="Nestor",
                       title="Nestor GraphWorld round {}".format(m.group(1)))
            b.link(b.git_source(ref, p, s, z, newest.get(p), oldest.get(p), obj=cat.json(s)), "campaign", ck, "report")
    for p, (s, z) in sorted(blobs.items()):
        m = re.match(r"primordial/ledger/([A-Z])\.jsonl$", p)
        if not m:
            continue
        lane = m.group(1)
        text = cat.text(s) or ""
        by_exp = defaultdict(list)
        for i, line in enumerate(text.splitlines(), 1):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and r.get("exp_id"):
                by_exp[r["exp_id"]].append((i, r))
        for exp_id, recs in by_exp.items():
            rnd = _round_of(exp_id)
            ck = C.campaign_key(GW, rnd)
            b.campaign(campaign_key=ck, program=GW, native_id=rnd, engine_id="npe", driver_seat="Nestor",
                       title="Nestor GraphWorld round {}".format(rnd))
            ek = C.experiment_key(ck, exp_id)
            last = recs[-1][1]
            status = last.get("status")
            b.experiment(experiment_key=ek, campaign_key=ck, engine_id="npe", native_id=exp_id, kind="experiment",
                         title=C.trunc(exp_id, 300), question=C.trunc(last.get("claim")), driver_seat="Nestor",
                         purpose=last.get("experiment_class"), reported_disposition=C.trunc(str(status), 300) if status else None,
                         atlas_class=classify.status_class(status),
                         atlas_class_confidence="MEDIUM" if status else "LOW",
                         atlas_class_method="status_class/1 on last receipt status",
                         validity_state=C.validity_from(status),
                         seeds=[str(x) for x in (last.get("families") or [])][:20] if isinstance(last.get("families"), list) else [],
                         extract={"lane": lane, "evidence_class": last.get("evidence_class"),
                                  "campaign_stage": last.get("campaign_stage"), "predicate_id": last.get("predicate_id")},
                         inferred={"campaign": "round from exp_id pattern '<Lane>-R<n>-'; ids without R are round 1"}
                         if rnd == "r1" else {"campaign": "R-number outside 1..8 is a regime label; round not stated"}
                         if rnd == "unassigned" else {})
            if exp_id in rows_by_exp:
                rp = rows_by_exp[exp_id]
                rs, rz = blobs[rp]
                b.link(b.git_source(ref, rp, rs, rz, newest.get(rp), oldest.get(rp)), "experiment", ek, "rows")
            for n, (line, r) in enumerate(recs, 1):
                native = "r{:02d}".format(n) + ("-" + str(r.get("job_id")) if r.get("job_id") else "")
                ak = C.attempt_key(ek, native)
                u = b.git_source(ref, p, s, z, newest.get(p), oldest.get(p), record_key="{}@{}".format(exp_id, line),
                                 line=(line, line))
                b.link(u, "attempt", ak, "receipt")
                eng = r.get("engineering") if isinstance(r.get("engineering"), dict) else {}
                host = classify.host_from_tag(r.get("tag"))
                basis = "instance tag {}".format(r.get("tag")) if host else None
                if not host and isinstance(eng.get("host"), str):
                    host = "M1" if re.search(r"\bM1\b|SKULLPORT", eng["host"]) else None
                    basis = "engineering.host text" if host else None
                b.attempt(attempt_key=ak, experiment_key=ek, native_id=native, attempt_no=n, of_record=(n == len(recs)),
                          reported_status=C.trunc(str(r.get("status")), 300) if r.get("status") else None,
                          validity_state="SUPERSEDED" if n < len(recs) else C.validity_from(r.get("status")),
                          finished_at=r.get("ts"), host_id=host, host_basis=basis, instance_tag=r.get("tag"),
                          operator_seat="Nestor", commit_sha=r.get("git"),
                          engine_instance_key=_npe_instance(b, host, r.get("git"), r.get("ts")),
                          budget={k: r.get(k) for k in ("runs_total", "rng_family_count", "runs_per_family",
                                                        "n_per_family") if r.get(k) is not None},
                          result_summary=C.trunc(json.dumps(r.get("science"), default=str), 500) if r.get("science") else None)
                if n > 1:
                    b.edge(("attempt", ak), ("attempt", C.attempt_key(ek, _native(recs, n - 1))), "RERUN_OF", "EXECUTION",
                           reason="UNKNOWN", basis="INFERRED", confidence="MEDIUM",
                           detail="second receipt for the same exp_id in {}".format(p), uri=u)
                for key, kind in (("claim", "prediction"), ("controls", "control"), ("science", "measurement"),
                                  ("engineering", "measurement"), ("oracles", "control"), ("envelope", "parameter"),
                                  ("refutes", "mechanism_claim"), ("residue", "failure_mode"), ("sample_rule", "parameter")):
                    if r.get(key) is not None:
                        layer = "RAN" if kind == "parameter" else "CONCLUDED" if key == "refutes" else "OBSERVED"
                        for name, val in C.flatten(r[key], key, depth=2, limit=40):
                            b.fact(layer, kind, "attempt", ak, name, val, u, name, stated_at=r.get("ts"))
                b.conclusion("attempt", ak, C.trunc(str(r.get("status")), 300) if r.get("status") else None,
                             C.trunc(json.dumps(r.get("refutes"), default=str)) if r.get("refutes") else None, u,
                             "status", stated_at=r.get("ts"))
                for fld, rel, reason in (("supersedes", "SUPERSEDES", "UNKNOWN"), ("rerun_of", "RERUN_OF", "UNKNOWN"),
                                         ("parent_receipt", "DESCENDANT_OF", "DECLARED_PARENT"),
                                         ("parent_anomaly", "DESCENDANT_OF", "DECLARED_PARENT"),
                                         ("parent_ids", "DESCENDANT_OF", "DECLARED_PARENT")):
                    v = r.get(fld)
                    for tgt in (v if isinstance(v, list) else [v] if v else []):
                        tgt = str(tgt)
                        tk = C.experiment_key(C.campaign_key(GW, _round_of(tgt)), tgt)
                        b.edge(("experiment", ek), ("experiment", tk), rel,
                               "EXECUTION" if rel == "RERUN_OF" else "SCIENTIFIC", reason=reason, basis="DECLARED",
                               confidence="HIGH", detail="{}={}".format(fld, C.trunc(tgt, 200)), uri=u, locator=fld)


def _native(recs, n):
    r = recs[n - 1][1]
    return "r{:02d}".format(n) + ("-" + str(r.get("job_id")) if r.get("job_id") else "")


def _npe_instance(b, host, git, ts):
    """The NPE mints no instance id: '<engine>@<host>:<code sha12>' is Atlas's
    synthetic key (basis recorded)."""
    if not git:
        return None
    k = "npe@{}:{}".format(host or "?", str(git)[:12])
    b.engine_instance(engine_instance_key=k, engine_id="npe", host_id=host, commit_sha=str(git),
                      first_seen_at=ts, last_seen_at=ts,
                      basis="ATLAS_DERIVED synthetic key from receipt git sha + host (the NPE mints no instance id)")
    return k


# ---------------------------------------------------------------- CW01

def _cw01(b, cat, ref, sfe):
    files = gitsrc.ls_tree(ref, CWDIR)
    newest, oldest, touching = gitsrc.path_commits(ref, CWDIR)
    blobs = {p: (s, z) for p, s, z in files}

    def src(path, obj=None, text=None, record=None, line=None):
        s, z = blobs[path]
        return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), obj=obj, text=text,
                            record_key=record, line=line)

    state = cat.json(blobs[CWDIR + "/CAMPAIGN_STATE.json"][0]) or {}
    cid = state.get("campaign_id") or "cw01-2026-09-17"
    ck = C.campaign_key(CW, cid)
    su = src(CWDIR + "/CAMPAIGN_STATE.json", obj=state)
    b.campaign(campaign_key=ck, program=CW, native_id=cid, engine_id="npe", driver_seat="Nestor",
               title="Nestor CW01 campaign", summary=C.trunc(json.dumps(state.get("campaign_totals"), default=str), 1500),
               extract={"phase_model": state.get("phase_model"), "campaign_order": state.get("campaign_order")})
    b.link(su, "campaign", ck, "state")
    for p in blobs:
        rel = p[len(CWDIR) + 1:]
        if "/" not in rel or rel.startswith("loop/"):
            if p.endswith(".py"):
                continue
            name = rel.rsplit("/", 1)[-1]
            role = ("report" if name.endswith(".md") else "registry" if name.endswith(".jsonl") else "state")
            b.link(src(p), "campaign", ck, role)
    mp = CWDIR + "/MACHINE_PROFILE.json"
    if mp in blobs:
        prof = cat.json(blobs[mp][0]) or {}
        hn = (prof.get("provenance_only") or {}).get("hostname")
        hid = next((m["host_id"] for m in db.registry()["hosts"] if (m.get("hostname") or "") == hn), None)
        if hid:
            b.fact("RAN", "telemetry_availability", "campaign", ck, "machine_profile.capabilities",
                   prof.get("capabilities"), src(mp, obj=prof), "capabilities")
    # e01..e10
    for e in state.get("experiments") or []:
        eid = e.get("id")
        if not eid:
            continue
        ek = C.experiment_key(ck, eid)
        edir = "{}/experiments/{}/".format(CWDIR, eid)
        world = _json_in(cat, blobs, edir + "WORLD.json")
        result = _json_in(cat, blobs, edir + "RESULT.json")
        disp = e.get("disposition") or e.get("status")
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id="npe", native_id=eid, kind="experiment",
                     slot=int(re.sub(r"\D", "", eid)[-2:]) if re.search(r"\d", eid) else None,
                     title=C.trunc(e.get("title"), 500), driver_seat="Nestor",
                     world_family=C.trunc(str(world.get("world_family")), 300) if world.get("world_family") else None,
                     organism_family=C.trunc(json.dumps(world.get("genome"), default=str), 300) if world.get("genome") else None,
                     reported_disposition=disp, reported_conclusion=C.trunc(result.get("disposition_reason"), 1500),
                     atlas_class=classify.status_class(result.get("disposition") or disp),
                     atlas_class_confidence="MEDIUM", atlas_class_method="status_class/1 on RESULT/state disposition",
                     validity_state=C.validity_from(disp, result.get("disposition")),
                     result_summary=C.trunc(json.dumps(e.get("headline"), default=str), 800) if e.get("headline") else None)
        for p in [p for p in blobs if p.startswith(edir)]:
            if p.endswith(".py"):
                continue
            name = p.rsplit("/", 1)[-1]
            role = {"PREREGISTRATION.md": "prereg", "WORLD.json": "world", "VERDICT_CONTRACT.json": "contract",
                    "RESULT.json": "result", "PACKAGE.md": "package", "MECHANISM_OF_NULL.md": "readout"}.get(
                name, "rows" if "/rows/" in p else "report" if name.endswith(".md") else "telemetry")
            b.link(src(p), "experiment", ek, role)
            b.commits("experiment", ek, touching.get(p, []))
        su_e = src(CWDIR + "/CAMPAIGN_STATE.json", record=eid)
        b.link(su_e, "experiment", ek, "state")
        for name, val in C.flatten(e.get("headline") or {}, "headline", depth=2, limit=40):
            b.fact("OBSERVED", "measurement", "experiment", ek, name, val, su_e, "experiments[{}].{}".format(eid, name))
        for lim in e.get("limitations") or []:
            b.fact("CONCLUDED", "open_question", "experiment", ek, "limitation", lim, su_e, "limitations")
        if world:
            wu = src(edir + "WORLD.json", obj=world)
            for key, kind in (("world_family", "world_descriptor"), ("genome", "representation_descriptor"),
                              ("population", "population_descriptor"), ("arms", "comparison_group"),
                              ("measurements", "measurement"), ("info_model", "world_descriptor"),
                              ("interventions_post_hoc", "followup_proposal"), ("amendments", "campaign_decision")):
                if key in world:
                    for name, val in C.flatten(world[key], "world." + key, depth=1, limit=20):
                        b.fact("OBSERVED", kind, "experiment", ek, name, val, wu, name)
        if result:
            ru = src(edir + "RESULT.json", obj=result)
            for name, val in C.flatten(result.get("summary") or {}, "summary", depth=2, limit=50):
                b.fact("OBSERVED", "metric_summary", "experiment", ek, name, val, ru, name)
            for name, val in C.flatten(result.get("tests") or {}, "tests", depth=2, limit=40):
                b.fact("OBSERVED", "measurement", "experiment", ek, name, val, ru, name)
            b.conclusion("experiment", ek, result.get("disposition"), result.get("disposition_reason"), ru, "disposition")
        prev = None
        for a in e.get("attempts") or []:
            anat = a.get("attempt_id") or "a?"
            ak = C.attempt_key(ek, anat)
            b.attempt(attempt_key=ak, experiment_key=ek, native_id=anat,
                      attempt_no=int(re.search(r"a(\d+)$", anat).group(1)) if re.search(r"a(\d+)$", anat) else None,
                      reported_status=a.get("disposition"), validity_state=C.validity_from(a.get("disposition")),
                      started_at=_local(a.get("started_local")), finished_at=_local(a.get("ended_local")),
                      duration_s=(a.get("wall_minutes") or 0) * 60 or None, host_id="M1",
                      host_basis="CW01 MACHINE_PROFILE.json hostname SKULLPORT (campaign-level)", operator_seat="Nestor",
                      commit_sha=a.get("rows_commit"), budget={"rows": a.get("rows"), "phase": a.get("phase")})
            b.link(su_e, "attempt", ak, "state")
            if prev:
                b.edge(("attempt", ak), ("attempt", prev), "RERUN_OF", "EXECUTION", basis="INFERRED",
                       confidence="MEDIUM", detail="attempt order in CAMPAIGN_STATE", uri=su_e)
            prev = ak
        if e.get("replication"):
            b.fact("OBSERVED", "measurement", "experiment", ek, "replication", e["replication"], su_e, "replication")
    _loop(b, cat, blobs, src, ck, sfe)


def _loop(b, cat, blobs, src, ck, sfe):
    L = CWDIR + "/loop/"
    # trajectories -> ideas
    tpath = L + "TRAJECTORIES.jsonl"
    traj = {}
    for i, row in enumerate(_jsonl(cat.text(blobs[tpath][0]) if tpath in blobs else ""), 1):
        traj[row["trajectory_id"]] = (i, row)
    for tid, (i, row) in traj.items():
        ik = "{}/{}".format(CW, tid)
        u = src(tpath, record=tid, line=(i, i))
        b.idea(idea_key=ik, native_id=tid, kind=row.get("kind") or "trajectory", engine_id="npe", campaign_key=ck,
               title=C.trunc(row.get("derived_operationalization") or row.get("originating_question_verbatim"), 500),
               question=C.trunc(row.get("originating_question_verbatim")),
               world_family=C.trunc(_s(row.get("world_substrate")), 300), organism_family=C.trunc(_s(row.get("representation")), 300),
               pressure_family=C.trunc(_s(row.get("pressure")), 300), search_family=C.trunc(_s(row.get("search_process")), 300),
               ruler=C.trunc(_s(row.get("ruler")), 300), reported_status=_s(row.get("stasis_state")),
               origin_text=C.trunc(_s(row.get("origin")), 1500),
               extract={"age": row.get("age"), "scope": row.get("scope"), "anti_gravity": row.get("anti_gravity")})
        b.link(u, "idea", ik, "registry")
        for key, kind, layer in (("result", "mechanism_claim", "CONCLUDED"), ("failure_surface", "failure_mode", "OBSERVED"),
                                 ("anomalies", "anomaly", "OBSERVED"), ("unrun_interventions", "followup_proposal", "CONCLUDED"),
                                 ("translation_loss", "open_question", "CONCLUDED"), ("assumptions_at_time", "open_question", "CONCLUDED"),
                                 ("later_changes_relevant", "campaign_decision", "CONCLUDED"), ("fossils", "telemetry_availability", "OBSERVED"),
                                 ("compute_budget", "budget", "RAN"), ("stasis_state", "stasis_status", "OBSERVED"),
                                 ("stasis_reason", "stasis_status", "OBSERVED"), ("marginal_information_history", "measurement", "OBSERVED")):
            if row.get(key) not in (None, "", []):
                for name, val in C.flatten(row[key], key, depth=1, limit=25):
                    b.fact(layer, kind, "idea", ik, name, val, u, name, stated_at=row.get("recorded"))
        if row.get("result"):
            b.conclusion("idea", ik, _s(row.get("stasis_state")), _s(row.get("result")), u, "result",
                         stated_at=row.get("recorded"))
        if row.get("parent"):
            b.edge(("idea", ik), ("idea", "{}/{}".format(CW, row["parent"])), "DESCENDANT_OF", "SCIENTIFIC",
                   reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH", uri=u, locator="parent")
        origin = _s(row.get("origin"))
        for eid in re.findall(r"\bcw01-e\d{2}\b", origin):
            b.edge(("idea", ik), ("experiment", C.experiment_key(ck, eid)), "ORIGINATES_FROM", "SCIENTIFIC",
                   reason="CONTINUATION", basis="DECLARED", confidence="HIGH", detail=C.trunc(origin, 500), uri=u, locator="origin")
        if "archaeon/campaign" in origin or SFE_ID.search(origin):
            for x in SFE_ID.findall(origin):
                if x in sfe:
                    b.edge(("idea", ik), ("experiment", sfe[x]), "ORIGINATES_FROM", "SCIENTIFIC",
                           reason="CROSS_SUBSTRATE_TRANSPLANT", basis="DECLARED", confidence="HIGH",
                           detail=C.trunc(origin, 500), uri=u, locator="origin")
            for n in re.findall(r"archaeon/campaign(\d)", origin):
                b.edge(("idea", ik), ("campaign", "archaeon.campaign/cmp" + n), "ORIGINATES_FROM", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT", basis="DECLARED", confidence="HIGH",
                       detail=C.trunc(origin, 500), uri=u, locator="origin")
    # perturbations -> experiments (append-only: base record, then amend records merged in order)
    ppath = L + "PERTURBATIONS.jsonl"
    pert, pline = {}, {}
    for i, row in enumerate(_jsonl(cat.text(blobs[ppath][0]) if ppath in blobs else ""), 1):
        pid = row.get("id")
        if not pid:
            continue
        base = pert.setdefault(pid, {})
        base.update({k: v for k, v in row.items() if k != "amend"})
        pline.setdefault(pid, []).append(i)
    for pid, row in pert.items():
        ek = C.experiment_key(ck, pid)
        u = src(ppath, record=pid, line=(pline[pid][0], pline[pid][-1]))
        res_path = (row.get("result") or "").replace("\\", "/")
        rp = CWDIR + "/" + res_path if res_path else None
        result = _json_in(cat, blobs, rp) if rp else {}
        pre = _json_in(cat, blobs, rp.rsplit("/", 1)[0] + "/PREREG.json") if rp else {}
        disp = result.get("disposition") or result.get("verdict") or result.get("status")
        typ = row.get("type") or ""
        reason = next((r for k, r in TYPE_REASON if k in typ), "UNKNOWN")
        axis = str(row.get("axis") or "")
        reason = AXIS_REASON.get(axis.split(" ")[0], reason) if axis else reason
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id="npe", native_id=pid, kind="perturbation",
                     title=C.trunc(row.get("delta"), 500), question=C.trunc(row.get("attacks")), purpose=typ or None,
                     driver_seat="Nestor", budget_summary="cost_minutes={}".format(row.get("cost_minutes")),
                     reported_disposition=C.trunc(_s(disp), 300) if disp else ("EXECUTED" if row.get("executed_in") else "PROPOSED"),
                     atlas_class=classify.status_class(disp) if disp else ("UNKNOWN" if row.get("executed_in") else "PLANNED"),
                     atlas_class_confidence="MEDIUM" if disp else "LOW",
                     atlas_class_method="status_class/1 on P-RESULT disposition",
                     validity_state=C.validity_from(_s(disp)) if disp else "UNKNOWN",
                     extract={"family": row.get("family"), "type": typ, "axis": row.get("axis"), "batch": row.get("batch"),
                              "anti_gravity": row.get("anti_gravity"), "serendipity": row.get("serendipity"),
                              "nonredundant": row.get("nonredundant")})
        b.link(u, "experiment", ek, "definition")
        for key, kind in (("delta", "parameter"), ("unchanged", "parameter"), ("attacks", "open_question"),
                          ("why_now", "campaign_decision"), ("scores", "campaign_decision"), ("deformation", "parameter"),
                          ("escapes_stasis", "stasis_status"), ("cost_minutes", "budget")):
            if row.get(key) not in (None, "", []):
                for name, val in C.flatten(row[key], "perturbation." + key, depth=1, limit=20):
                    b.fact("RAN" if kind in ("parameter", "budget") else "CONCLUDED" if kind == "campaign_decision"
                           else "OBSERVED", kind, "experiment", ek, name, val, u, name, stated_at=row.get("recorded"))
        if row.get("parent"):
            b.edge(("experiment", ek), ("idea", "{}/{}".format(CW, row["parent"])), "TESTS", "SCIENTIFIC",
                   reason=reason, basis="DECLARED", confidence="HIGH",
                   detail="type={}; axis={}; delta: {}".format(typ, row.get("axis"), C.trunc(row.get("delta"), 400)),
                   uri=u, locator="parent")
        for cp in row.get("co_parents") or []:
            b.edge(("experiment", ek), ("idea", "{}/{}".format(CW, cp)), "CO_PARENT", "SCIENTIFIC", reason=reason,
                   basis="DECLARED", confidence="HIGH", uri=u, locator="co_parents")
        if row.get("superseded_by"):
            # the field is prose that names the superseding work: another perturbation or an SFE experiment
            sb = _s(row["superseded_by"])
            sups = [sfe[x] for x in SFE_ID.findall(sb) if x in sfe] + \
                   [C.experiment_key(ck, x) for x in re.findall(r"\bP-[A-F]\d{2}\b", sb) if x != pid]
            for sk in sups:
                b.edge(("experiment", sk), ("experiment", ek), "SUPERSEDES", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT" if sk.startswith("archaeon.") else "UNKNOWN",
                       basis="DECLARED", confidence="HIGH", detail=C.trunc(sb, 500), uri=u, locator="superseded_by")
            if not sups:
                b.fact("CONCLUDED", "campaign_decision", "experiment", ek, "superseded_by", sb, u, "superseded_by",
                       status="UNRESOLVED")
        for c in (row.get("continuation") if isinstance(row.get("continuation"), list) else [row.get("continuation")] if row.get("continuation") else []):
            c = _s(c)
            targets = [sfe[x] for x in SFE_ID.findall(c) if x in sfe] + \
                      [C.experiment_key(ck, x) for x in re.findall(r"\bP-[A-F]\d{2}\b", c) if x != pid]
            for tk in targets:
                b.edge(("experiment", ek), ("experiment", tk), "CONTINUATION_OF", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT" if tk.startswith("archaeon.") else "CONTINUATION",
                       basis="DECLARED", confidence="HIGH", detail=C.trunc(c, 500), uri=u, locator="continuation")
        if row.get("executed_in"):
            ak = C.attempt_key(ek, row["executed_in"])
            b.attempt(attempt_key=ak, experiment_key=ek, native_id=row["executed_in"], attempt_no=1, of_record=True,
                      reported_status=C.trunc(_s(disp), 300) if disp else "EXECUTED", host_id="M1",
                      host_basis="CW01 loop runs on M1 (MACHINE_PROFILE SKULLPORT; run logs in the M1 worktree)",
                      operator_seat="Nestor", finished_at=_local(row.get("recorded")),
                      validity_state=C.validity_from(_s(disp)) if disp else "UNKNOWN")
            b.link(u, "attempt", ak, "registry")
            if rp and rp in blobs:
                ru = src(rp, obj=result)
                b.link(ru, "attempt", ak, "result")
                b.link(ru, "experiment", ek, "result")
                for name, val in C.flatten({k: v for k, v in result.items() if k not in ("rows",)}, "result", depth=2, limit=60):
                    b.fact("OBSERVED", "measurement", "experiment", ek, name, val, ru, name)
                b.conclusion("experiment", ek, _s(disp) if disp else None,
                             _s(result.get("disposition_reason") or result.get("reading") or result.get("summary")) or None,
                             ru, "disposition")
            if pre and rp:
                pp = rp.rsplit("/", 1)[0] + "/PREREG.json"
                pu = src(pp, obj=pre)
                b.link(pu, "experiment", ek, "prereg")
                for name, val in C.flatten(pre, "prereg", depth=1, limit=30):
                    b.fact("OBSERVED", "prediction" if "predict" in name else "condition" if re.search(r"kill|falsif|gate", name)
                           else "parameter", "experiment", ek, name, val, pu, name)
    # stasis history, evidence, defects
    spath = L + "STATE.jsonl"
    for i, row in enumerate(_jsonl(cat.text(blobs[spath][0]) if spath in blobs else ""), 1):
        ik = "{}/{}".format(CW, row.get("trajectory_id"))
        u = src(spath, record="{}@{}".format(row.get("trajectory_id"), i), line=(i, i))
        b.fact("OBSERVED", "stasis_status", "idea", ik, "state@{}".format(row.get("ts")),
               "{}: {}".format(row.get("state"), row.get("reason")), u, str(i), stated_at=_local(row.get("ts")))
    epath = L + "EVIDENCE.jsonl"
    for i, row in enumerate(_jsonl(cat.text(blobs[epath][0]) if epath in blobs else ""), 1):
        pid, tid = row.get("perturbation_id"), row.get("trajectory_id")
        u = src(epath, record="{}x{}@{}".format(tid, pid, i), line=(i, i))
        ik = "{}/{}".format(CW, tid)
        # perturbation_id is a P- id, an SFE experiment id (evidence from Archaeon's campaigns), a bare
        # campaign ('C5'), or a loop step ('RECONCILE-3', 'operator-directive-...'): resolve, never mint a key
        if pid and not re.fullmatch(r"P-[A-F]\d{2}", pid):
            target = sfe.get(pid) if pid in sfe else None
            camp = "archaeon.campaign/cmp" + pid[1] if re.fullmatch(r"C\d", pid) else None
            b.fact("OBSERVED", "measurement", "idea", ik, "evidence.{}".format(pid), row.get("summary"), u, str(i),
                   stated_at=_local(row.get("ts")))
            if target or camp:
                b.edge(("experiment", target) if target else ("campaign", camp), ("idea", ik), "TESTS", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT", basis="DECLARED", confidence="HIGH",
                       detail=C.trunc(row.get("summary"), 600), uri=u, locator=str(i))
            continue
        if pid:
            ek = C.experiment_key(ck, pid)
            b.fact("OBSERVED", "measurement", "experiment", ek, "evidence.{}".format(tid), row.get("summary"), u, str(i),
                   stated_at=_local(row.get("ts")))
            b.fact("OBSERVED", "measurement", "experiment", ek, "evidence.material_change.{}".format(tid),
                   row.get("material_change"), u, str(i))
            b.edge(("experiment", ek), ("idea", "{}/{}".format(CW, tid)), "TESTS", "SCIENTIFIC", basis="DECLARED",
                   confidence="HIGH", detail=C.trunc(row.get("summary"), 600), uri=u, locator=str(i))
    dpath = CWDIR + "/DEFECTS.jsonl"
    for i, row in enumerate(_jsonl(cat.text(blobs[dpath][0]) if dpath in blobs else ""), 1):
        did = row.get("id")
        if not did:
            continue
        dk = "{}/{}".format(CW, did)
        u = src(dpath, record=did, line=(i, i))
        b.defect(defect_key=dk, native_id=did, engine_id="npe", campaign_key=ck, category=row.get("category"),
                 severity=row.get("severity"), phase=row.get("phase"), title=C.trunc(row.get("title"), 1000),
                 reported_status=row.get("status"), reported_at=_local(row.get("ts")),
                 extract={k: row.get(k) for k in ("defect_class", "found_by", "proposed_fix", "fix_evidence",
                                                 "_significance", "_pattern", "_meta_lesson") if row.get(k)})
        b.link(u, "defect", dk, "ledger")
        eid = row.get("experiment_id") or ""
        targets = []
        if re.fullmatch(r"cw01-e\d{2}", eid):
            targets.append(C.experiment_key(ck, eid))
        targets += [C.experiment_key(ck, x) for x in re.findall(r"\bP-[A-F]\d{2}\b", row.get("title") or "")]
        for tk in targets:
            b.edge(("experiment", tk), ("defect", dk), "AFFECTED_BY", "PROVENANCE",
                   basis="DECLARED" if tk.endswith(eid) else "INFERRED",
                   confidence="HIGH" if tk.endswith(eid) else "MEDIUM", uri=u,
                   detail=None if tk.endswith(eid) else "perturbation id named in the defect title")
        if not targets:
            b.edge(("campaign", ck), ("defect", dk), "AFFECTED_BY", "PROVENANCE", basis="DECLARED",
                   confidence="MEDIUM", detail="experiment_id={}".format(eid), uri=u)


def _json_in(cat, blobs, path):
    if path and path in blobs:
        v = cat.json(blobs[path][0])
        return v if isinstance(v, dict) else {}
    return {}


def _jsonl(text):
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            try:
                v = json.loads(line)
                if isinstance(v, dict):
                    yield v
            except ValueError:
                pass


def _s(v) -> str:
    if v is None:
        return ""
    return v if isinstance(v, str) else json.dumps(v, default=str)


def _local(s):
    """'2026-09-17 16:54:06' (M1 local time, America/New_York) -> ISO with offset."""
    if not s or not isinstance(s, str):
        return None
    if re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", s.strip()):
        return s.strip().replace(" ", "T") + "-04:00"
    return s
