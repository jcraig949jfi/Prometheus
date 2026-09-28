"""Cross-engine attribution assay (directive item 13): the SAME attribution-v0 schema over bounded preserved samples from three
engines. Adapters read native fields and record NOT_IDENTIFIABLE where an engine did not persist something. Nothing is re-simulated.

Samples (all preserved evidence on M2; inputs are sha256-fingerprinted in the output):
  BEE       T-001 (r038751) and T-002 (r016299) FULL replays with Bellerophon's traced VM + code provenance (E-001).
            Row layout = traced_replay.py _register_offspring: 0 tick, 1 writer id, 2 child id, 3 mechanism, 4 fid to writer now,
            5 fid to replaced target, 6 native `material` label (writer|target, BY RESEMBLANCE), 7 bytes written, 8 copied from the
            writer's own region, 9 of those by own-region code, 10 bytes changed, 11 is_sr, 12 sr_depth, 13-15 own/window/other
            steps, 16 variant, 17 fid_pre, 18 is_sr_post, 19 into_empty.
  NPE       T-003 observation-only replays: 34 preserved births with per-directed-byte WHO|WHERE|WHAT and native P-11 flags.
  Archaeon  ENVGATE-01 block 13 events from PORTABILITY-01 A4 (the 53,185 watched births, native taint counts).

Capability is NOT per-event in any of the three samples:
- BEE: a child counts as demonstrably capable IN SITU when it later writes an is_sr birth as the writer (world-scaffolded, so
  never "autonomous"). A child that is never seen doing so may have died first: "no observed SR" is an upper bound on incapacity.
- NPE: P-11 is a test of the EVENT's dependence, not of the child's capability; it is recorded as dependence.
- Archaeon: per-event capability comes from the block-13 probes (deep block; TH-013), reported beside the table.
    python -m archaeon.attribution.assay OUT_DIR
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter

from archaeon.attribution import schema as S, classify as K
from archaeon.attribution.schema import seg

EV = os.environ.get("PROM_EVIDENCE", "C:/Prometheus-data/evidence")
INPUTS = {"BEE_r038751": EV + "/ops_pilot_2026-09-27/T-001_A-002/out.json", "BEE_r016299": EV + "/ops_pilot_2026-09-27/T-002_A-001/out.json",
          "NPE_T003": EV + "/ops_pilot_2026-09-27/T-003_A-001/out.json", "ARCH_block13": EV + "/portability01_2026-09-26/archaeon/A4_block13_events.json"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def _contrast(n): return {"baseline": "shares of the child's %d loci; donors by material channel" % n, "kind": "reference_entity"}


# ------------------------------------------------------------------ BEE
def bee_records(d, L=64):
    rows, cp = d["births_rows"], d["codeprov"]
    sr_writers = {r[1] for r in rows if r[11]}                           # ids that later wrote an is_sr birth
    any_writers = {r[1] for r in rows}
    out = []
    for r, c in zip(rows, cp):
        w, child, nw, own = "bee:%d" % r[1], "bee:%d" % r[2], r[7], r[8]
        retained = 0 if r[19] else L - nw
        occ = "bee:occupant_of_slot_before_%d" % r[2]
        segs = []; p = 0
        if own: segs.append(seg(p, p + own, entity=w, via="replay_taint")); p += own
        if retained: segs.append(seg(p, p + retained, entity=occ, via="by_construction")); p += retained
        if L - p: segs.append(seg(p, L, "unknown"))
        n_code = sum(c.values())
        what = S.NI if not n_code else {"via": "replay_taint", "writer_material": (c["own_region"] + c["self_copied"]) / n_code,
                                        "occupant_material": c["foreign"] / n_code, "unclassified": c["elsewhere"] / n_code}
        caps = []
        if r[2] in sr_writers:
            caps.append({"capability": "approximate_self_copy", "result": True, "method": "replayed", "ruler": "BEE is_sr (traced_replay)",
                         "conditions": {"neighbour": "in_situ_partner", "scaffold": "BEE world (%s)" % r[3]}})
        rec = S.record("bee:%s:%d" % (d["rid"], r[2]), "BEE", child, source="%s births_rows" % d["rid"],
                       native={"mechanism": r[3], "material_label": r[6], "is_sr": r[11], "fid_writer": r[4], "fid_target": r[5],
                               "later_writer": r[2] in any_writers, "later_sr": r[2] in sr_writers, "donor_capabilities": {w: bool(r[11])}},
                       carrier={"performers": [{"kind": "organism_code", "id": w, "role": "performer"}],
                                "exec_where": {"own": r[13], "window": r[14], "other": r[15]}, "exec_what": what},
                       production={"process": "executed_write", "evidence": "traced VM write log"},
                       material={"unit": "byte", "n_units": L, "resolution": "counts", "segments": segs},
                       state={"resemblance": [{"reference": w, "ibs": r[4], "units": "byte"}] +
                              ([{"reference": occ, "ibs": r[5], "units": "byte"}] if r[5] is not None else [])},
                       capability=caps, contrast=_contrast(L))
        out.append(rec)
    return out


# ------------------------------------------------------------------ NPE
def npe_records(d):
    out = []
    for run in d["results"]:
        for b in run["births"]:
            ww = b["who_where_what"]; D = max(1, b["D"]); n = b["n"]
            def s(pred): return sum(v for k, v in ww.items() if pred(*k.split("|")))
            don = s(lambda w_, l, m: (l == "donor_half" and m == "original") or m == "changed_by_donor")
            vic = s(lambda w_, l, m: (l == "victim_half" and m == "original") or m == "changed_by_victim")
            vctx = s(lambda w_, l, m: w_ == "victim_ctx")
            segs = []; p = 0
            for ent, k in (("npe:donor", don), ("npe:victim", vic)):
                if k: segs.append(seg(p, p + k, entity=ent, via="replay_taint")); p += k
            if n - p: segs.append(seg(p, n, "unknown"))
            perf = [{"kind": "organism_code", "id": "npe:donor", "role": "performer"}]
            if vctx: perf.append({"kind": "neighbour_organism", "id": "npe:victim", "role": "performer"})
            dep = [{"target": "carrier", "intervention": "P-11 %s" % k, "outcome": "the overwrite recurs", "contrast": "native P-11 arm",
                    "result": "persists" if b.get("native_" + k) else "ceases"} for k in ("C2", "C4", "C5") if ("native_" + k) in b]
            out.append(S.record("npe:%s:%s" % (run["name"], b["child"]), "NPE", "npe:child", source="T-003 %s" % run["name"],
                                native={"causal": b.get("native_causal"), "donor_authored_share": b.get("native_donor_authored_share"),
                                        "D": b["D"], "vctx_share": vctx / D, "donor_capabilities": {}},
                                carrier={"performers": perf, "exec_where": S.NI, "exec_what": {"via": "replay_taint", "donor": don / D, "victim": vic / D}},
                                production={"process": "executed_write", "evidence": "z8taint write log"},
                                material={"unit": "byte", "n_units": n, "resolution": "counts", "segments": segs},
                                dependence=dep, contrast=_contrast(n)))
    return out


# ------------------------------------------------------------------ Archaeon
def arch_records(d, G=32):
    out = []
    for e in d["watched"]:
        nE, nN = e["copied_exec"], e["copied_nbr"]; ex = "arch:oid%d" % e["executor_oid"]; nb = "arch:occupant@cell%d" % e["child_cell"]
        segs = []; p = 0
        for ent, k in ((ex, nE), (nb, nN)):
            if k: segs.append(seg(p, p + k, entity=ent, via="taint")); p += k
        if e["computed"]: segs.append(seg(p, p + e["computed"], "new_computed")); p += e["computed"]
        if G - p: segs.append(seg(p, G, "new_unspecified"))
        kind = "organism_code" if nE >= nN else "host_organism"
        out.append(S.record("arch:b13:%d" % len(out), "Archaeon", "arch:child@cell%d" % e["child_cell"], source="A4 block 13 watched",
                            native={"mechanism": e.get("mechanism"), "template": e["template"], "executed_material": e["executed_material"],
                                    "executor_glin": e["executor_glin"], "donor_capabilities": {}},
                            carrier={"performers": [{"kind": kind, "id": ex, "role": "performer"}], "exec_where": S.NI,
                                     "exec_what": {"via": "taint", "executed_material": e["executed_material"], "counts": e["exec_counts"]}},
                            production={"process": "executed_write", "evidence": "taint VM"},
                            material={"unit": "byte", "n_units": G, "resolution": "counts", "segments": segs}, contrast=_contrast(G)))
    return out


# ------------------------------------------------------------------ questions
def unk(r):
    m = r["material"]; return sum(x["loci"][1] - x["loci"][0] for x in m["segments"] if x["source_kind"] == "unknown") / m["n_units"]


def questions(recs, engine):
    n = len(recs); bad = sum(1 for r in recs if S.check(r))
    def frac(pred): return round(sum(1 for r in recs if pred(r)) / n, 4) if n else None
    def top(r):
        d = S.donors(r); return max(d, key=d.get) if d else None
    q = {"engine": engine, "n": n, "invalid_records": bad,
         "producer_ne_any_donor": frac(S.producer_ne_donor),
         "majority_donor_not_producer": frac(lambda r: top(r) is not None and top(r) not in S.producer_ids(r)),
         "no_material_donor": frac(lambda r: not S.donors(r)),
         "singular_parent_lossy": frac(lambda r: not S.singular_loss(r)["lossless"]),
         "unidentified_material_ge_0.1": frac(lambda r: unk(r) >= 0.1),
         "singular_lossy_by_identified_structure": frac(lambda r: (lambda l: l["other_donor_share"] >= 0.1 or l["producer_ne_donor"]
                                                                   or l["new_share"] >= 0.1)(S.singular_loss(r))),
         "mean_unidentified_share": round(sum(unk(r) for r in recs) / n, 4) if n else None,
         "no_singular_material_parent": frac(lambda r: S.singular_parent(r) is None),
         "two_plus_donors": frac(lambda r: len(S.donors(r)) >= 2),
         "classes": dict(Counter(K.production_class(r) for r in recs).most_common(8))}
    return q


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    fp = {k: sha(p) for k, p in INPUTS.items()}
    res = {"inputs": INPUTS, "input_sha256": fp, "engines": {}}
    for key in ("BEE_r038751", "BEE_r016299"):
        d = json.load(open(INPUTS[key])); recs = bee_records(d)
        q = questions(recs, key)
        lab_wrong = [r for r in recs if S.donors(r) and r["native"]["material_label"] == "writer"
                     and max(S.donors(r), key=S.donors(r).get) != r["carrier"]["performers"][0]["id"]]
        lab_t_wrong = [r for r in recs if S.donors(r) and r["native"]["material_label"] == "target"
                       and max(S.donors(r), key=S.donors(r).get) == r["carrier"]["performers"][0]["id"]]
        q["native_material_label_contradicts_IBD_majority"] = round((len(lab_wrong) + len(lab_t_wrong)) / len(recs), 4)
        q["native_label_writer_but_IBD_majority_not_writer"] = len(lab_wrong)
        q["native_label_target_but_IBD_majority_writer"] = len(lab_t_wrong)
        maj_w = [r for r in recs if S.donors(r).get(r["carrier"]["performers"][0]["id"], 0) >= 0.5]
        q["writer_majority_children"] = len(maj_w)
        q["of_which_later_sr"] = sum(1 for r in maj_w if r["native"]["later_sr"])
        q["of_which_never_seen_writing"] = sum(1 for r in maj_w if not r["native"]["later_writer"])
        seen = [r for r in maj_w if r["native"]["later_writer"]]
        q["later_sr_among_those_seen_writing"] = round(sum(1 for r in seen if r["native"]["later_sr"]) / len(seen), 4) if seen else None
        q["is_sr_births"] = sum(1 for r in recs if r["native"]["is_sr"])
        q["mechanisms"] = dict(Counter(r["native"]["mechanism"] for r in recs))
        wh = [r["carrier"]["exec_what"] for r in recs if isinstance(r["carrier"]["exec_what"], dict)]
        q["births_with_code_provenance"] = len(wh)
        q["code_run_mostly_occupant_material"] = sum(1 for x in wh if x["occupant_material"] > 0.5)
        res["engines"][key] = q
    d = json.load(open(INPUTS["NPE_T003"])); recs = npe_records(d); q = questions(recs, "NPE_T003")
    q["p11_causal"] = sum(1 for r in recs if r["native"]["causal"])
    q["victim_context_wrote_some"] = sum(1 for r in recs if r["native"]["vctx_share"] > 0)
    q["native_donor_authored_vs_replay_donor_material"] = [(r["native"]["donor_authored_share"], r["carrier"]["exec_what"]["donor"]) for r in recs][:34]
    res["engines"]["NPE_T003"] = q
    d = json.load(open(INPUTS["ARCH_block13"])); recs = arch_records(d); q = questions(recs, "ARCH_block13")
    q["executor_is_not_majority_donor"] = sum(1 for r in recs if r["carrier"]["performers"][0]["kind"] == "host_organism")
    q["mechanisms"] = dict(Counter(r["native"]["mechanism"] for r in recs))
    q["executed_material"] = dict(Counter(r["native"]["executed_material"] for r in recs))
    res["engines"]["ARCH_block13"] = q
    res["result_sha256"] = hashlib.sha256(json.dumps(res["engines"], sort_keys=True).encode()).hexdigest()
    json.dump(res, open(os.path.join(out_dir, "ASSAY.json"), "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("native_donor_authored_vs_replay_donor_material",)} for k, v in res["engines"].items()}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
