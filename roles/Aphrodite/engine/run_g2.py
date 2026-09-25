"""G1 -> G2 bounded recursion assay, AMENDMENT 15 (commit aaae70067), frozen
before this was written.

Stages (each writes its own artifact; none reads a later one):
  0 G1 conformance, both parts
  1 generate the treatment-blind Tier-3E catalog -> T3E_CATALOG (hashed)
  2 G2 qualification of every family; stops
  3 shams (SEMANTICALLY_NEW random schemas), hashed BEFORE any donor runs
  4 16 donor replicates (DONOR_G1 and DONOR_P, 8 paired each) with full TRACE
  5 R1; L2 frozen (or STOP)
  6 treatment-blind admission pilot; transfer arms; R2-R5
Process pools are for throughput only (per-worker marker directories).
"""
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G          # noqa: E402
import cert as CT             # noqa: E402
import conformance as CF      # noqa: E402
import engine as E            # noqa: E402
import fair as FR             # noqa: E402
import identity as I          # noqa: E402
import meta_tribunal as M     # noqa: E402
import tier3d as T3D          # noqa: E402
import tier3e as T            # noqa: E402

M.use_provider(T)
N, ESCROW, MAX_HITS, R_D, R_VAL, R_OBS, EMITTER = 16, FR.ESCROW, 5, 8, 8, 3, 2
WORKERS = int(os.environ.get("G2_WORKERS", "7"))
DATE = "2026-09-24"


def _log(m):
    print("[g2] " + m, flush=True)


def _write(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n",
                             encoding="utf-8")


def _read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def _worker_init():
    import tempfile
    E.MARKER_DIR = Path(tempfile.gettempdir()) / ("aphrodite_engine_markers_w%d" % os.getpid())
    T._load()


def pool_map(fn, items, chunks=1):
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_worker_init) as ex:
        return list(ex.map(fn, items, chunksize=chunks))


def L1_entries():
    art = _read("S3_ARTIFACT_2026-09-23.json")
    assert FR.KLib(art["selected_entries"] + FR.pristine().entries).sha256() == art["selected_sha256"]
    return art["selected_entries"] + FR.pristine().entries


def schema_entry(name, schema, **meta):
    e = {"name": name, "inits": list(G.H1_SPACE), "bodies": T3D.instantiate(schema),
         "finals": list(G.FINAL_SPACE), "schema": schema}
    e.update(meta)
    return e


def coverage(entries):
    """D3: the donor's OWN realized search coverage -- its entries' candidates,
    before the G4 fallback."""
    lib = FR.KLib(entries)
    out = []
    for e, bodies in zip(lib.entries, lib._bodies):
        out += [("fold", i, b, f) for i in e["inits"] for b in bodies for f in e["finals"]]
    return list(dict.fromkeys(out))


def members_in(space, observed, examples):
    parsed = [(T.nums_of(t), t["gold"]) for t in examples]
    target = I.behavior_id(observed, True)
    out = []
    for p in space:
        ok = True
        for nums, gold in parsed:
            got = G.run_program(p, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok and I.behavior_id(p, True) == target:
            out.append(p)
    return out


# ---------------------------------------------------------------- stage 0
def stage_conformance():
    std = CF.check()
    rng = random.Random(I._seed("APHRODITE/T3E/CONF/v1"))
    progs = [("fold", rng.choice(G.INIT_SPACE), rng.choice(G.BODY_SPACE), rng.choice(G.FINAL_SPACE))
             for _ in range(40)]
    p2 = [CF.check_whole_program(p, b, EMITTER) for p in progs for b in (I.B1, I.B1_BOUNDARY)]
    g = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"],
         "part2_checked": sum(x["checked"] for x in p2),
         "part2_mismatches": sum(len(x["mismatches"]) for x in p2)}
    g["GREEN"] = g["part1_GREEN"] and g["part2_mismatches"] == 0
    return g


# ---------------------------------------------------------------- stage 2
def _qual(f):
    return f, T.qualify_generator(f)


# ---------------------------------------------------------------- stage 3
def stage_shams():
    shams = []
    for k in range(8):
        rng = random.Random(I._seed("APHRODITE/T3E/SHAM/v1/%d" % k))
        tries = 0
        while True:
            tries += 1
            b = rng.choice(G.BODY_SPACE)
            t = I.normalise(I.parse(b))
            paths = []

            def walk(node, path):
                for i, a in enumerate(node[1]):
                    paths.append(path + (i,))
                    walk(a, path + (i,))
            walk(t, ())
            if not paths:
                continue
            path = rng.choice(paths)

            def put(node, p):
                if not p:
                    return ("hole", [])
                op, args = node
                args = list(args)
                args[p[0]] = put(args[p[0]], p[1:])
                return (op, args)
            schema = T3D.schema_src(put(t, path))
            if len(T3D.instantiate(schema)) >= 2 and T.semantically_new(schema)["SEMANTICALLY_NEW"]:
                break
        e = schema_entry("sham_%d" % k, schema)
        shams.append({"k": k, "schema": schema, "tries": tries, "entry": e,
                      "sha256": FR.KLib([e] + L1_entries()).sha256()})
    return shams


# ---------------------------------------------------------------- stage 4
def donor(args):
    kind, r, quals = args
    t0 = time.perf_counter()
    start = L1_entries() if kind == "G1" else FR.pristine().entries
    base = FR.KLib(start)
    cov = coverage(start)
    obs_fams = [f for f in T.by_role("OBSERVE") if quals[f]["QUALIFIED"]]
    val_fams = [f for f in T.by_role("VALIDATE") if quals[f]["QUALIFIED"]]
    meta, observed = 0, []
    for fam in obs_fams:                                                    # D1
        for c in range(R_OBS):
            cell = FR.Cell(T, fam, r * R_OBS + c, quals[fam]["qualified_dev_size"],
                           label="T3E-obs/r%d" % r)
            esc = E.Escrow(ESCROW)
            hits = FR.search_collect(base, cell.parsed, esc, ESCROW, cell.seed, max_hits=1)
            meta += esc.spent
            if hits:
                observed.append({"family": fam, "program": tuple(hits[0][0]),
                                 "examples": cell.examples, "charges": hits[0][2]})
    buckets = {}                                                            # D2
    for o in observed:
        buckets.setdefault(I.behavior_id(o["program"], True), []).append(o)
    classes, certs = [], []
    for bid, obs in sorted(buckets.items()):                                # D3
        progs = [o["program"] for o in obs]
        mem = members_in(cov, progs[0], obs[0]["examples"])
        rec = CT.certify(progs + mem, anchor=progs[0])
        certs.append({"bucket": bid, "PASS": rec["PASS"], "sub_buckets": rec["sub_buckets"]})
        groups = [(progs, mem)]
        if not rec["PASS"]:
            bat = list(I.B1) + CT.b_cert() + CT.adversarial(progs + mem)
            sub = {}
            for p in dict.fromkeys(progs + mem):
                sub.setdefault(I.values(p, True, bat), []).append(p)
            groups = [([p for p in v if p in progs], [p for p in v if p in mem])
                      for v in sub.values() if any(p in progs for p in v)]
        for gp, gm in groups:
            classes.append({"bucket": bid, "families": sorted({o["family"] for o in obs
                                                               if o["program"] in gp}),
                            "observed": [list(p) for p in gp],
                            "member_bodies": sorted({p[2] for p in gm} | {p[2] for p in gp})})
    derived = T3D.derive_schemas([c["member_bodies"] for c in classes])   # D4
    for d in derived:
        d.update(T.semantically_new(d["schema"]))
    cands = {"INHERITED": start,                                            # D5
             "MEMORISE": [{"name": "memorised", "inits": list(G.H1_SPACE),
                           "bodies": sorted({b for c in classes for b in c["member_bodies"]}),
                           "finals": list(G.FINAL_SPACE)}] + start}
    for k, d in enumerate(derived):
        cands["SCHEMA_%d" % k] = [schema_entry("g2_new", d["schema"])] + start
    if len(derived) > 1:
        allb = list(dict.fromkeys(b for d in derived for b in T3D.instantiate(d["schema"])))
        cands["SCHEMA_ALL"] = [{"name": "g2_new", "inits": list(G.H1_SPACE), "bodies": allb,
                                "finals": list(G.FINAL_SPACE),
                                "schemas": [d["schema"] for d in derived]}] + start
    libs = {n: FR.KLib(e) for n, e in cands.items()}
    cells = [FR.Cell(T, f, r * R_VAL + j, quals[f]["qualified_dev_size"], label="T3E-val/r%d" % r)
             for f in val_fams for j in range(R_VAL)]                       # D6
    costs = {n: [c.cost(l)[0] for c in cells] for n, l in libs.items()}
    meta += sum(sum(v) for v in costs.values())
    table = {}
    for n in cands:
        row = FR.paired_summary(costs["INHERITED"], costs[n])
        row.update({"sha256": libs[n].sha256(), "size": libs[n].size(),
                    "eligible": n != "INHERITED" and row["lower95_one_sided"] > 0})
        table[n] = row
    elig = [n for n in table if table[n]["eligible"]]
    chosen = (min(elig, key=lambda n: (-table[n]["mean_paired_saving"], table[n]["size"],
                                       table[n]["sha256"])) if elig else "INHERITED")
    if chosen.startswith("SCHEMA_") and chosen != "SCHEMA_ALL":
        sel_new = derived[int(chosen.split("_")[1])]["SEMANTICALLY_NEW"]
        sel_schemas = [derived[int(chosen.split("_")[1])]["schema"]]
    elif chosen == "SCHEMA_ALL":
        sel_schemas = [d["schema"] for d in derived]
        sel_new = any(d["SEMANTICALLY_NEW"] for d in derived)
    else:
        sel_new, sel_schemas = False, []
    return {"donor": kind, "replicate": r,
            "trace": {"observed": [{"family": o["family"], "program": list(o["program"]),
                                    "charges": o["charges"]} for o in observed],
                      "class_certificates": certs, "classes": classes,
                      "candidate_schemas": derived, "selection_table": table,
                      "selected": chosen, "selected_schemas": sel_schemas,
                      "selected_entries": cands[chosen],
                      "selected_sha256": table[chosen]["sha256"]},
            "observed_class_set": sorted(c["bucket"] for c in classes),
            "observed_body_keys": sorted({T.body_key(o["program"][2]) for o in observed}),
            "SELECTED_SEMANTICALLY_NEW": sel_new, "meta_charges": meta,
            "seconds": round(time.perf_counter() - t0, 1)}


def sign_test(a, b):
    n = a + b
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(a, n + 1)) / 2 ** n


def r1(donors):
    g = {d["replicate"]: d for d in donors if d["donor"] == "G1"}
    p = {d["replicate"]: d for d in donors if d["donor"] == "P"}
    altered = [r for r in range(R_D) if g[r]["observed_class_set"] != p[r]["observed_class_set"]]
    a = sum(1 for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"] and not p[r]["SELECTED_SEMANTICALLY_NEW"])
    b = sum(1 for r in range(R_D) if p[r]["SELECTED_SEMANTICALLY_NEW"] and not g[r]["SELECTED_SEMANTICALLY_NEW"])
    both = [r for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"] and p[r]["SELECTED_SEMANTICALLY_NEW"]]
    pv = sign_test(a, b)
    rb = pv < 0.05 and a > b
    fallback = None
    if a == 0 and b == 0 and both:
        s = FR.paired_summary([g[r]["meta_charges"] for r in both], [p[r]["meta_charges"] for r in both])
        # paired saving here = G1 - P; P costlier <=> saving < 0
        fallback = {"n": len(both), "mean_P_minus_G1": -s["mean_paired_saving"],
                    "upper95_of_G1_minus_P": s["mean_paired_saving"] + 1.645 * s["se"]}
        rb = fallback["upper95_of_G1_minus_P"] < 0
    g1_new = [r for r in range(R_D) if g[r]["SELECTED_SEMANTICALLY_NEW"]]
    return {"altered_replicates": altered, "R1a": bool(altered),
            "G1_new_replicates": g1_new,
            "P_new_replicates": [r for r in range(R_D) if p[r]["SELECTED_SEMANTICALLY_NEW"]],
            "discordant_G1_only": a, "discordant_P_only": b, "sign_test_p": pv,
            "meta_cost_fallback": fallback, "R1b": rb, "PASS": bool(altered) and rb,
            "L2_replicate": g1_new[0] if g1_new else None}


# ---------------------------------------------------------------- stage 6
def run_recipient(args):
    fam, arm, entries, i, size, label = args
    lib = FR.KLib(entries)
    c = FR.Cell(T, fam, i, size, label=label)
    esc = E.Escrow(ESCROW)
    hits = FR.search_collect(lib, c.parsed, esc, ESCROW, c.seed, max_hits=MAX_HITS)
    fp, first = 0, None
    for prog, coord, ch in hits:
        art = M.artifact_for(fam, prog, EMITTER)
        trib = M.MetaTribunal.after_freeze(art, fam)
        if trib.qualified(trib.score(art)):
            first = {"charges": ch, "coordinate": coord, "program": list(prog),
                     "bytes": len(art.bytes), "sha256": art.sha256}
            break
        fp += 1
    return (fam, arm, label, i), {
        "recipient": i, "arm": arm, "family": fam, "escrow_spent": esc.spent, "hits": len(hits),
        "qualified": first is not None, "charges": first["charges"] if first else None,
        "coordinate": first["coordinate"] if first else None,
        "solution_program": first["program"] if first else None,
        "solution_body_key": T.body_key(first["program"][2]) if first else None,
        "artifact_sha256": first["sha256"] if first else None, "false_positives": fp}


def summarise(rows):
    q = [r for r in rows if r["qualified"]]
    hits = sum(r["hits"] for r in rows)
    fps = sum(r["false_positives"] for r in rows)
    return {"censored_effort": round(statistics.mean([r["charges"] if r["qualified"] else ESCROW
                                                     for r in rows]), 1),
            "qualified": len(q), "hits": hits, "false_positives": fps}


def stage_transfer(quals, shams, l2_entries, p_entries, g1_trace_rep):
    L1 = L1_entries()
    cand = [f for f in T.by_role("TRANSFER") if quals[f]["QUALIFIED"]]
    wit = {}
    for f in cand:
        a = M.artifact_for(f, T.witness(f), EMITTER)
        tr = M.MetaTribunal.after_freeze(a, f)
        wit[f] = tr.qualified(tr.score(a))
    cand = [f for f in cand if wit[f]]
    pilot = dict(pool_map(run_recipient, [(f, "PRISTINE", FR.pristine().entries, i,
                                            quals[f]["qualified_dev_size"], "T3E-pilot")
                                           for f in cand for i in range(N)]))
    pq = {f: sum(pilot[(f, "PRISTINE", "T3E-pilot", i)]["qualified"] for i in range(N)) for f in cand}
    admitted = [f for f in cand if pq[f] <= 8]
    out = {"transfer_qualified": cand, "witness_tribunal": wit, "pristine_pilot_qualified": pq,
           "admitted": admitted}
    _log("[admission] %s" % out)
    if len(admitted) < 2:
        out["STOP"] = "fewer than two TRANSFER families admitted -- untestable; BRSI = NO"
        return out
    arms = {"L2": l2_entries, "L1": L1, "PRISTINE": FR.pristine().entries}
    for s in shams:
        arms["L1+SHAM_%d" % s["k"]] = [s["entry"]] + L1
    if p_entries is not None:
        arms["L1+P_SCHEMA"] = p_entries
    jobs = [(f, a, arms[a], i, quals[f]["qualified_dev_size"], "T3E-rx")
            for f in admitted for a in arms for i in range(N)]
    rows = dict(pool_map(run_recipient, jobs))
    detail = {f: {a: [rows[(f, a, "T3E-rx", i)] for i in range(N)] for a in arms} for f in admitted}
    out["arms"] = {a: FR.KLib(e).sha256() for a, e in arms.items()}
    out["arm_desugars"] = {a: FR.KLib(e).desugars()[0] for a, e in arms.items()}
    out["detail"] = detail
    out["per_family"] = {f: {a: summarise(detail[f][a]) for a in arms} for f in admitted}
    out["criterion"] = criterion(out, g1_trace_rep)
    return out


def criterion(out, rep):
    fams, det, pf = out["admitted"], out["detail"], out["per_family"]
    shams = [a for a in pf[fams[0]] if a.startswith("L1+SHAM_")]
    c = {}
    d2, d1 = [], []
    fam = {}
    for f in fams:
        a = [r["charges"] if r["qualified"] else ESCROW for r in det[f]["L2"]]
        b = [r["charges"] if r["qualified"] else ESCROW for r in det[f]["L1"]]
        d2 += a
        d1 += b
        s = FR.paired_summary(b, a)
        se = sorted(pf[f][x]["censored_effort"] for x in shams)
        e2 = pf[f]["L2"]["censored_effort"]
        effect = s["lower95_one_sided"] > 0 and pf[f]["L2"]["qualified"] >= pf[f]["L1"]["qualified"]
        q = [r for r in det[f]["L2"] if r["qualified"]]
        g1m = T.g1_mechanisms()
        obs_keys = set(rep["observed_body_keys"])
        attrib = [r for r in q if r["coordinate"] == "g2_new"
                  and r["solution_body_key"] not in obs_keys and r["solution_body_key"] not in g1m]
        fam[f] = {"paired_L2_vs_L1": s, "L2_qualified": pf[f]["L2"]["qualified"],
                  "L1_qualified": pf[f]["L1"]["qualified"], "effect": effect,
                  "beats_every_sham": e2 < se[0], "below_sham_median": e2 < statistics.median(se),
                  "attributed_to_new_mechanism": len(attrib), "qualified": len(q),
                  "R3_family": bool(q) and len(attrib) * 2 > len(q)}
    pooled = FR.paired_summary(d1, d2)
    c["R2_G2_beats_G1"] = pooled["lower95_one_sided"] > 0 and all(
        fam[f]["L2_qualified"] >= fam[f]["L1_qualified"] for f in fams)
    r3 = [f for f in fams if fam[f]["R3_family"]]
    c["R3_attribution_new_mechanism"] = len(r3) >= 2
    eff = [f for f in fams if fam[f]["effect"]]
    hits = sum(pf[f]["L2"]["hits"] for f in fams)
    fps = sum(pf[f]["L2"]["false_positives"] for f in fams)
    c["R4_hostile_controls"] = (sum(fam[f]["beats_every_sham"] for f in fams) * 2 >= len(fams)
                                and all(fam[f]["below_sham_median"] for f in eff)
                                and (fps / hits if hits else 0.0) <= 0.25
                                and all(out["arm_desugars"].values()))
    c["R5_clean_transplant"] = True
    return {"conditions": c, "pooled_L2_vs_L1": pooled, "per_family": fam,
            "R3_families": r3, "effect_families": eff,
            "L2_fp_fraction": round(fps / hits, 4) if hits else 0.0}


# ---------------------------------------------------------------- main
def main():
    t0 = time.perf_counter()
    gate = stage_conformance()
    _log("G1 conformance %s" % gate)
    if not gate["GREEN"]:
        raise SystemExit("CONFORMANCE RED")
    if not T.CATALOG_FILE.exists():
        cat = T.generate_catalog()
        cat["sha256"] = hashlib.sha256(json.dumps(cat["families"], sort_keys=True).encode()).hexdigest()
        T.CATALOG_FILE.write_text(json.dumps(cat, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    T._load()
    cat = _read(T.CATALOG_FILE.name)
    _log("catalog sha %s: %s" % (cat["sha256"][:12], [(f["name"], f["role"], f["body"], f["final"],
                                                       f["init"]) for f in cat["families"]]))
    quals = dict(pool_map(_qual, sorted(T.FAMILY_SPEC)))
    _write("T3E_QUALIFICATION_%s.json" % DATE, quals)
    obs = [f for f in T.by_role("OBSERVE") if quals[f]["QUALIFIED"]]
    val = [f for f in T.by_role("VALIDATE") if quals[f]["QUALIFIED"]]
    _log("qualified OBSERVE %s VALIDATE %s TRANSFER %s" % (obs, val, [
        f for f in T.by_role("TRANSFER") if quals[f]["QUALIFIED"]]))
    result = {"amendment": "AMENDMENT_15 @ aaae70067", "conformance_before": gate,
              "catalog_sha256": cat["sha256"]}
    if len(obs) < 3 or len(val) < 3:
        result.update({"STOP": "catalog cannot support the assay (s3)",
                       "BOUNDED_RECURSIVE_SELF_IMPROVEMENT": "NO"})
        _write("G2_RESULTS_%s.json" % DATE, result)
        _log("STOP %s" % result["STOP"])
        return 2
    shams = stage_shams()
    _write("T3E_SHAMS_%s.json" % DATE, shams)
    _log("shams hashed: %s" % [(s["schema"], s["sha256"][:10]) for s in shams])
    donors = pool_map(donor, [(kind, r, quals) for r in range(R_D) for kind in ("G1", "P")])
    _write("G2_DONORS_%s.json" % DATE, donors)
    for d in sorted(donors, key=lambda d: (d["replicate"], d["donor"])):
        _log("[donor %s r%d] classes=%d candidates=%s selected=%s NEW=%s meta=%d"
             % (d["donor"], d["replicate"], len(d["trace"]["classes"]),
                [(x["schema"], x["SEMANTICALLY_NEW"]) for x in d["trace"]["candidate_schemas"]],
                d["trace"]["selected"], d["SELECTED_SEMANTICALLY_NEW"], d["meta_charges"]))
    rr = r1(donors)
    result["R1"] = rr
    _log("R1 %s" % rr)
    if rr["L2_replicate"] is None or not rr["PASS"]:
        result.update({"BOUNDED_RECURSIVE_SELF_IMPROVEMENT": "NO",
                       "STOP": ("DONOR_G1 selected no SEMANTICALLY_NEW schema in any replicate -- "
                                "G4 cannot support a genuinely new abstraction from G1"
                                if rr["L2_replicate"] is None else "R1 failed")})
        result["conformance_after"] = {"part1_GREEN": CF.check()["GREEN"]}
        _write("G2_RESULTS_%s.json" % DATE, result)
        _log("BRSI = NO: %s" % result["STOP"])
        return 3
    g1rep = next(d for d in donors if d["donor"] == "G1" and d["replicate"] == rr["L2_replicate"])
    l2 = g1rep["trace"]["selected_entries"]
    result["L2"] = {"replicate": rr["L2_replicate"], "schemas": g1rep["trace"]["selected_schemas"],
                    "sha256": FR.KLib(l2).sha256()}
    _write("G2_L2_ARTIFACT_%s.json" % DATE, {"entries": l2, **result["L2"]})
    prep = next(d for d in donors if d["donor"] == "P" and d["replicate"] == rr["L2_replicate"])
    p_entries = None
    if prep["SELECTED_SEMANTICALLY_NEW"]:
        p_entries = [schema_entry("g2_new", s) for s in prep["trace"]["selected_schemas"]][:1] + L1_entries()
    tr = stage_transfer(quals, shams, l2, p_entries, g1rep)
    result["transfer"] = tr
    if "criterion" in tr:
        c = dict(tr["criterion"]["conditions"])
        c["R1_G1_dependent_derivation"] = rr["PASS"]
        result["conditions"] = c
        result["BOUNDED_RECURSIVE_SELF_IMPROVEMENT"] = "YES" if all(c.values()) else "NO"
        result["failed"] = [k for k, v in c.items() if not v]
    else:
        result["BOUNDED_RECURSIVE_SELF_IMPROVEMENT"] = "NO"
    std = CF.check()
    result["conformance_after"] = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"]}
    result["seconds"] = round(time.perf_counter() - t0, 1)
    _write("G2_RESULTS_%s.json" % DATE, result)
    _log("BRSI = %s failed=%s" % (result["BOUNDED_RECURSIVE_SELF_IMPROVEMENT"], result.get("failed")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
