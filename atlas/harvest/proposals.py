"""Source adapter: Atlas's own experiment PROPOSALS (roles/Atlas/proposals/
<date>_<topic>/EXPERIMENTS.jsonl). Indexed as campaign program
'atlas.proposal', experiments of kind 'proposal', atlas_class PLANNED, with
TRANSPLANT_OF edges to the Prometheus findings each one transplants. Nothing
here ran; the kind and the program say so on every row, so 'what ran' queries
exclude them by filtering kind <> 'proposal'.
"""
from __future__ import annotations

import json
from pathlib import Path

from atlas import db
from atlas.harvest import common as C

VERSION = "proposals/1"
ROOT = Path(__file__).resolve().parents[2] / "roles" / "Atlas" / "proposals"


def run(args) -> dict:
    b = C.Batch("proposals", VERSION, "Atlas")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT experiment_key FROM atlas.experiment")
            exps = {r[0] for r in cur.fetchall()}
            cur.execute("SELECT idea_key FROM atlas.idea")
            ideas = {r[0] for r in cur.fetchall()}
            cur.execute("SELECT campaign_key FROM atlas.campaign")
            camps = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()
    for f in sorted(ROOT.glob("*/EXPERIMENTS.jsonl")):
        topic = f.parent.name
        ck = C.campaign_key("atlas.proposal", topic)
        rel = f.relative_to(ROOT.parents[2]).as_posix()
        uri = b.other_source("git:" + rel, "git_blob", "GIT_REMOTE", path=rel, repo=C.REPO_NAME)
        b.campaign(campaign_key=ck, program="atlas.proposal", native_id=topic, driver_seat="Atlas",
                   title="Atlas proposals " + topic, reported_status="PROPOSED")
        b.link(uri, "campaign", ck, "definition")
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            r = json.loads(line)
            ek = C.experiment_key(ck, r["id"])
            b.experiment(experiment_key=ek, campaign_key=ck, native_id=r["id"], kind="proposal",
                         title=r.get("title"), question=r.get("question"), driver_seat="Atlas",
                         reported_disposition=r.get("status", "PROPOSED"), atlas_class="PLANNED",
                         atlas_class_confidence="HIGH", atlas_class_method="proposal file status",
                         validity_state="UNKNOWN", result_summary=None,
                         extract={"substrates": r.get("substrates"), "suggested_owner": r.get("suggested_owner"),
                                  "controls": r.get("controls"), "claim_ceiling": r.get("claim_ceiling")})
            b.link(uri, "experiment", ek, "definition")
            for p in r.get("parents") or []:
                ptype = "experiment" if p in exps else "idea" if p in ideas else "campaign" if p in camps else "ecosystem"
                b.edge(("experiment", ek), (ptype, p), "TRANSPLANT_OF", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT", basis="DECLARED", confidence="HIGH",
                       detail=C.trunc(r.get("parent_finding_verbatim"), 800), uri=uri, locator="line {}".format(i))
            for s in r.get("substrates") or []:
                b.edge(("experiment", ek), ("ecosystem", s), "ANALOGUE_OF", "SCIENTIFIC", reason="UNKNOWN",
                       basis="ATLAS_DERIVED", confidence="MEDIUM", detail="proposed substrate", uri=uri,
                       locator="line {}".format(i))
    with db.harvest("proposals", VERSION, source_ref="roles/Atlas/proposals") as h:
        return b.flush(h)
