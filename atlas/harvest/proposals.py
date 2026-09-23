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

VERSION = "proposals/2"
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
            # two record shapes: the 2026-09-19 cross-ecosystem set and the 2026-09-21
            # prior-art queue (the operator's fuller format). Map both onto the same columns.
            question = r.get("question") or r.get("scientific_question")
            substrates = r.get("substrates") or r.get("donors") or []
            parents = r.get("parents") or []
            ek = C.experiment_key(ck, r["id"])
            b.experiment(experiment_key=ek, campaign_key=ck, native_id=r["id"], kind="proposal",
                         title=r.get("title"), question=question, driver_seat="Atlas",
                         reported_disposition=r.get("status", "PROPOSED"), atlas_class="PLANNED",
                         atlas_class_confidence="HIGH", atlas_class_method="proposal file status",
                         validity_state="UNKNOWN", result_summary=None,
                         extract={k: r.get(k) for k in (
                             "substrates", "donors", "suggested_owner", "controls", "claim_ceiling", "group",
                             "claim_under_test", "why_prometheus", "target_engine", "primary_endpoint", "falsifier",
                             "causal_test", "assumption_cost", "donor_code", "implementation_gap", "compute_class",
                             "engineering_class", "information_gain", "promotion_gate", "stopping_rule",
                             "prereg_required", "anticheat", "telemetry", "expected_failure_modes") if r.get(k) is not None})
            b.link(uri, "experiment", ek, "definition")
            for p in parents:
                ptype = "experiment" if p in exps else "idea" if p in ideas else "campaign" if p in camps else "ecosystem"
                b.edge(("experiment", ek), (ptype, p), "TRANSPLANT_OF", "SCIENTIFIC",
                       reason="CROSS_SUBSTRATE_TRANSPLANT", basis="DECLARED", confidence="HIGH",
                       detail=C.trunc(r.get("parent_finding_verbatim"), 800), uri=uri, locator="line {}".format(i))
            for dep in r.get("dependencies") or []:
                b.edge(("experiment", ek), ("experiment", C.experiment_key(ck, dep)), "DEPENDS_ON", "PROVENANCE",
                       reason="UNKNOWN", basis="DECLARED", confidence="HIGH", detail="ladder ordering", uri=uri,
                       locator="line {}".format(i))
            for s in substrates:
                b.edge(("experiment", ek), ("ecosystem", s), "ANALOGUE_OF", "SCIENTIFIC", reason="UNKNOWN",
                       basis="ATLAS_DERIVED", confidence="MEDIUM", detail="proposed substrate", uri=uri,
                       locator="line {}".format(i))
    with db.harvest("proposals", VERSION, source_ref="roles/Atlas/proposals") as h:
        return b.flush(h)
