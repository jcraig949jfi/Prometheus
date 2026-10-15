"""C-019-T020 post-confirmation replay audit (separate from, and never modifying, C-018's frozen confirmation).

  python -B -m rso.aether.audit.replay_audit run [--limit N]     replay every unit not yet replayed; one JSON per unit
  python -B -m rso.aether.audit.replay_audit aggregate           tables + law-level dispositions -> TABLES.json

Reads committed evidence (rso/aether/runs/CONFIRM) read-only; writes ONLY under rso/aether/audit/ (replay/*.json committed;
replay_arrays/*.npz are local scratch, not committed). A unit with a replay record is skipped, so a restart resumes.
Inputs per unit are its committed meta (law, seed, n, warm, H); the call is adapter.native_unit, the same one
`confirm analyse` uses for its sample (confirm.py:214). No new seeds: every (law, seed) is one already in the committed shards."""
import json
import os
import sys
import time

import numpy as np

from rso.aether import adapter as A, confirm as C, evaluate as E

HERE = os.path.dirname(os.path.abspath(__file__))
REPLAY_DIR = os.path.join(HERE, "replay")
ARR_DIR = os.path.join(HERE, "replay_arrays")
# already fully replayed (arrays_sha256 + tree/B/N/origin): the six preregistered samples (analyse_full.out full_replay_verified=6)
# and the integrator's RX 8201 (C-018-T050)
ALREADY = {("RX", 8192), ("RX", 8204), ("RX", 8216), ("RX", 8228), ("V1", 8192), ("V1", 8200), ("RX", 8201)}
META_FIELDS = ("tree", "B", "N", "origin", "B_tick")


def units():
    out = []
    for sh in C.load_presented(C.RUNS):
        for row in sh["rows"]:
            out.append((sh["id"], row["law"], row["seed"], row))
    return out


def rec_path(law, seed):
    return os.path.join(REPLAY_DIR, "%s_%s.json" % (law, seed))


def clamp_cmp(old, new, key):
    a, b = old[key], new[key]
    return {"equal": bool(a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b)),
            "n_diff_sites": int((a != b).sum()) if a.shape == b.shape else None}


def one(sid, law, seed, row):
    meta, arrays = A.load_unit(os.path.join(C.RUNS, sid, "native_%s_%s" % (law, seed)))
    t0 = time.process_time()
    w0 = time.time()
    m2, a2 = A.native_unit(law, seed, meta["n"], meta["warm"], meta["H"])
    cpu, wall = time.process_time() - t0, time.time() - w0
    new_sha = A.arrays_sha256(a2)
    rec = {"schema": "prometheus.rso.aether.audit.unit.v1", "shard": sid, "law": law, "seed": seed,
           "inputs": {"n": meta["n"], "warm": meta["warm"], "H": meta["H"]},
           "committed_arrays_sha256": meta["arrays_sha256"], "replayed_arrays_sha256": new_sha,
           "arrays_match": new_sha == meta["arrays_sha256"],
           "committed_meta_sha256": row["meta_sha256"], "replayed_meta_sha256": None,
           "clamp_arrays": {k: clamp_cmp(arrays, a2, k) for k in ("ftick_cutB", "ftick_cutN")},
           "all_arrays": {k: bool(arrays[k].shape == a2[k].shape and np.array_equal(arrays[k], a2[k])) for k in sorted(arrays)},
           "meta_fields": {f: m2.get(f) == meta.get(f) for f in META_FIELDS},
           "warm_digest_match": m2["aether"]["warm_digest"] == meta["aether"]["warm_digest"],
           "cpu_s": round(cpu, 1), "wall_s": round(wall, 1)}
    m2["arrays_sha256"] = new_sha
    rec["replayed_meta_sha256"] = C.M.digest(m2)
    rec["meta_digest_match"] = rec["replayed_meta_sha256"] == row["meta_sha256"]
    rec["match"] = bool(rec["arrays_match"] and all(rec["all_arrays"].values()) and all(rec["meta_fields"].values())
                        and rec["warm_digest_match"] and all(v["equal"] for v in rec["clamp_arrays"].values()) and rec["meta_digest_match"])
    np.savez_compressed(os.path.join(ARR_DIR, "%s_%s.npz" % (law, seed)), **a2)
    with open(os.path.join(ARR_DIR, "%s_%s.meta.json" % (law, seed)), "w", encoding="utf-8") as f:
        json.dump(m2, f, sort_keys=True)
    return rec


def run(limit=None):
    os.makedirs(REPLAY_DIR, exist_ok=True)
    os.makedirs(ARR_DIR, exist_ok=True)
    todo = [u for u in units() if (u[1], u[2]) not in ALREADY and not os.path.exists(rec_path(u[1], u[2]))]
    print("units total %d, to replay %d" % (len(units()), len(todo)), flush=True)
    for i, (sid, law, seed, row) in enumerate(todo[:limit]):
        rec = one(sid, law, seed, row)
        tmp = rec_path(law, seed) + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, rec_path(law, seed))
        print("%s %s %s match=%s cpu=%.1fs" % (time.strftime("%H:%M:%S"), law, seed, rec["match"], rec["cpu_s"]), flush=True)
    return 0


def aggregate():
    """Per-unit match table; classes recomputed from the REPLAYED arrays with the frozen evaluator (rso.aether.evaluate, read-only);
    RX / V1 law dispositions recomputed from replayed evidence, printed beside the committed ones. The 7 already-replayed units are
    taken from the committed arrays (their replay digests already equalled the committed ones)."""
    recs, rowsC, rowsR, featsC, featsR = [], {}, {}, {}, {}
    with open(os.path.join(C.HERE, "qual", "QUALIFICATION.json"), encoding="utf-8") as f:
        qualified = json.load(f)["qualified"]
    for sid, law, seed, row in units():
        meta, arrays = A.load_unit(os.path.join(C.RUNS, sid, "native_%s_%s" % (law, seed)))
        rc = E.evaluate_unit(meta, arrays)
        rec = {"shard": sid, "law": law, "seed": seed, "committed_class": rc["cls"], "committed_arrays_sha256": meta["arrays_sha256"]}
        if (law, seed) in ALREADY:
            rec.update(status="PRIOR_FULL_REPLAY", replayed_class=rc["cls"], replayed_arrays_sha256=meta["arrays_sha256"], match=True,
                       source="C-018 analyse_full.out (6 samples) / C-018-T050 integrator (RX 8201)")
            ra = arrays
            rr = rc
            m2 = meta
        else:
            r = json.load(open(rec_path(law, seed), encoding="utf-8"))
            m2 = json.load(open(os.path.join(ARR_DIR, "%s_%s.meta.json" % (law, seed)), encoding="utf-8"))
            ra = {k: v for k, v in np.load(os.path.join(ARR_DIR, "%s_%s.npz" % (law, seed))).items()}
            rr = E.evaluate_unit(m2, ra)
            rec.update(status="REPLAYED_THIS_AUDIT", replayed_class=rr["cls"], replayed_arrays_sha256=r["replayed_arrays_sha256"],
                       match=r["match"], class_changed=rr["cls"] != rc["cls"], cpu_s=r["cpu_s"],
                       clamp_equal={k: v["equal"] for k, v in r["clamp_arrays"].items()})
        recs.append(rec)
        rowsC.setdefault(law, []).append((rc, (seed, arrays["H"], arrays["D"])))
        rowsR.setdefault(law, []).append((rr, (seed, ra["H"], ra["D"])))
    laws = {}
    for law in rowsC:
        out = {}
        for tag, rows in (("committed", rowsC[law]), ("replayed_post_confirmation", rowsR[law])):
            rs, fs = [x[0] for x in rows], [x[1] for x in rows]
            L = E.law_summary(rs, E.decode(fs), E.decode(fs, null=True))
            d = E.disposition({"completeness": "COMPLETE", "records_ok": True, "qualified": qualified, "law": L})
            out[tag] = {"classes": L["classes"], "evaluable": L["evaluable"], "confirmed_r2": L["confirmed_r2"], "reach_band": L["reach_band"],
                        "content_excess_cond": L["content_excess_cond"], "null_excess": L["null_excess"],
                        "pooled_agreement": L["pooled_agreement"], "disposition": d, "label": E.label(d, L)}
        laws[law] = out
    n_rep = [r for r in recs if r["status"] == "REPLAYED_THIS_AUDIT"]
    tab = {"schema": "prometheus.rso.aether.audit.tables.v1", "units": recs, "laws": laws,
           "summary": {"units": len(recs), "replayed_this_audit": len(n_rep), "prior_replays": len(recs) - len(n_rep),
                       "match": sum(1 for r in n_rep if r["match"]), "mismatch": sum(1 for r in n_rep if not r["match"]),
                       "class_changed": sum(1 for r in n_rep if r["class_changed"]),
                       "cpu_s_total": round(sum(r.get("cpu_s", 0) for r in n_rep), 1)}}
    with open(os.path.join(HERE, "TABLES.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(tab, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(tab["summary"]))
    for law, o in laws.items():
        print(law, "committed:", o["committed"]["label"], "| replayed:", o["replayed_post_confirmation"]["label"])
    return 0


def main(argv):
    if argv and argv[0] == "run":
        lim = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None
        return run(lim)
    if argv and argv[0] == "aggregate":
        return aggregate()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
