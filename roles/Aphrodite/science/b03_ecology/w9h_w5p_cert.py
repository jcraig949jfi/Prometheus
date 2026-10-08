"""D5: W9-H certification re-run with W5P's ACTUAL promotion machinery (engine/w5p, @1e169a577).

My expansion-based certification (w9h_admit.certify_family) built PROMOTED entries by substituting EVERY LEVEL1 filler
into S_x o S_a with no shape limit. W5P instead promotes S_a to P_a = Promoted.from_schema(S_a) and builds an entry for
the promoted-form schema S_x[H := P_a({H})] with promote.instantiate (fillers = LEVEL1 + P(atom); bodies containing P
must satisfy g5p_admissible: depth <= 3 counting P as one node and every binary node has an atom child). The entry
construction below is donor.schema_entry's three lines restated (donor.py imports gtc/b02, which would re-label a18).

Per T4-qualified L2 pilot family (W9H:0-2) this walks the TRANSFER cells (2 x cap 1M; same cells and qualifier as
w9h_admit) for:
  W5P_PROMOTED_A      [S_x o P_a for every seed mechanism x] + FLAT + PRISTINE
  W5P_PROMOTED_ORACLE [S_b o P_a] + FLAT + PRISTINE
PRISTINE and FLAT are unchanged (re-used from W9H_CERTIFY.jsonl). Static coverage (is the witness body, up to
normalisation, among the entry's expanded bodies?) is recorded for both W5P and the expansion libraries.
Usage: python w9h_w5p_cert.py <pilot_dir> [workers]
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w9h_admit as A  # noqa: E402
from a18 import FR, G, I  # noqa: E402

sys.path.insert(0, str(HERE.parents[1] / "engine"))
from w5p import promote as WP  # noqa: E402

LIBS = ("W5P_PROMOTED_A", "W5P_PROMOTED_ORACLE")


def skey(b):
    return I.term_str(I.normalise(I.parse(b)))


def w5p_entry(name, schema, reg):
    """= w5p.donor.schema_entry(name, schema, reg) (restated)."""
    e = {"name": name, "inits": list(G.H1_SPACE), "bodies": WP.instantiate(schema, reg),
         "finals": list(G.FINAL_SPACE), "schema": schema}
    if WP.has_promoted(schema):
        e["schema_expansion"] = WP.expand(schema, reg)
        e["promoted"] = WP.lineage_records(reg, sorted(set(WP.prims_in(WP.parse(schema)))))
    return e


def w5p_libraries(truth, comp):
    mechs = {m["id"]: m for m in truth["mechanisms"]}
    reg = {}
    pa = WP.register(reg, WP.Promoted.from_schema(mechs[comp["inner"]]["schema"], reg, "W9H-oracle", "oracle"))
    app = "%s({H})" % pa.id
    flat = A.flat_entries(truth["mechanisms"])
    pr = FR.pristine().entries
    comps = sorted({m["schema"].replace("{H}", app) for m in truth["mechanisms"]},
                   key=lambda s: A._hkey(WP.expand(s, reg)))
    prom = [w5p_entry("promoted_%d" % i, s, reg) for i, s in enumerate(comps)]
    orac = w5p_entry("promoted_oracle", mechs[comp["outer"]]["schema"].replace("{H}", app), reg)
    return {"W5P_PROMOTED_A": prom + flat + pr, "W5P_PROMOTED_ORACLE": [orac] + flat + pr}, pa, prom, orac


def job(args):
    A.init_worker()
    row, truth, old = args
    t0 = time.time()
    name = row["name"]
    meta = truth["families"][name]
    comp = {c["id"]: c for c in truth["compositions"]}[meta["src"]]
    prov = A.a17.Prov({name: (row["body"], row["final"], row["init"])})
    A.a17.M.use_provider(prov)
    libs, pa, prom, orac = w5p_libraries(truth, comp)
    wk = skey(row["body"])
    mechs = {m["id"]: m for m in truth["mechanisms"]}
    exp_prom = {skey(b) for m in truth["mechanisms"] for b in A.expand(A.W.compose(m["schema"], mechs[comp["inner"]]["schema"]))}
    static = {"witness_in_W5P_PROMOTED_A": any(wk in {skey(b) for b in e["bodies"]} for e in prom),
              "witness_in_W5P_ORACLE": wk in {skey(b) for b in orac["bodies"]},
              "witness_in_EXPANSION_PROMOTED_A": wk in exp_prom,
              "w5p_promoted_bodies": sum(len(e["bodies"]) for e in prom), "w5p_oracle_bodies": len(orac["bodies"]),
              "expansion_promoted_bodies": sum(len(A.expand(A.W.compose(m["schema"], mechs[comp["inner"]]["schema"])))
                                               for m in truth["mechanisms"])}
    _dev, tx = A.cells_for(prov, name, row["Q2_size"])
    walks = {k: [A.walk_cell(FR.KLib(libs[k]), c, A.CAP, prov, name) for c in tx] for k in LIBS}
    s = {k: sum(not x["censored"] for x in v) for k, v in walks.items()}
    os_ = old["summary"]
    pr0 = os_["PRISTINE"]["tx_reached"] == 0
    return {"name": name, "seed": row["source"], "src": meta["src"], "P_a": pa.id, "P_a_schema": pa.schema,
            "static": static, "walks": walks, "tx_reached": s,
            "verdict_w5p": bool(s["W5P_PROMOTED_A"] >= 1 and pr0),
            "verdict_w5p_oracle": bool(s["W5P_PROMOTED_ORACLE"] >= 1 and pr0),
            "verdict_expansion": old["CERTIFIED"], "verdict_expansion_oracle": old["CERTIFIED_ORACLE"],
            "expansion_tx_reached": {k: os_[k]["tx_reached"] for k in ("PROMOTED_A", "PROMOTED_ORACLE")},
            "expansion_tx_charges": os_["PROMOTED_A"]["tx_charges"],
            "seconds": round(time.time() - t0, 1)}


def main(pdir, workers=2):
    from collections import Counter
    truths = json.loads((pdir / "W9H_TRUTH.json").read_text())
    rows = {r["name"]: r for r in A.rdl(pdir / "W9H_FOUNDRY.jsonl")}
    certs = [c for c in A.rdl(pdir / "W9H_CERTIFY.jsonl") if c["level"] == "L2"]
    out_p = pdir / "W9H_W5P_CERT.jsonl"
    done = {r["name"] for r in A.rdl(out_p)}
    jobs = [(rows[c["name"]], truths[c["seed"]], c) for c in certs if c["name"] not in done]
    t0 = time.time()
    with open(out_p, "a", encoding="utf-8") as fh, ProcessPoolExecutor(workers, initializer=A.init_worker) as ex:
        for r in ex.map(job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            A.log("w5p-cert %s w5p=%s exp=%s %s (%ss)" % (r["name"], r["verdict_w5p"], r["verdict_expansion"],
                                                         r["tx_reached"], r["seconds"]))
    res = A.rdl(out_p)
    adm = A.admit(list(rows.values()), truths)
    summ = {"families": len(res), "cpu_s": round(sum(r["seconds"] for r in res), 1), "wall_s": round(time.time() - t0)}
    for grp, sel in (("all_T4q_L2", lambda r: True), ("admitted_L2", lambda r: adm[r["name"]]["admitted"])):
        rr = [r for r in res if sel(r)]
        summ[grp] = {"n": len(rr),
                     "agree": sum(r["verdict_w5p"] == r["verdict_expansion"] for r in rr),
                     "agree_oracle": sum(r["verdict_w5p_oracle"] == r["verdict_expansion_oracle"] for r in rr),
                     "certified_expansion": sum(bool(r["verdict_expansion"]) for r in rr),
                     "certified_w5p": sum(r["verdict_w5p"] for r in rr),
                     "certified_w5p_oracle": sum(r["verdict_w5p_oracle"] for r in rr),
                     "mismatch": [[r["name"], r["src"], r["verdict_expansion"], r["verdict_w5p"],
                                   r["static"]["witness_in_W5P_PROMOTED_A"]] for r in rr
                                  if r["verdict_w5p"] != r["verdict_expansion"]],
                     "witness_static_w5p": sum(r["static"]["witness_in_W5P_PROMOTED_A"] for r in rr),
                     "witness_static_expansion": sum(r["static"]["witness_in_EXPANSION_PROMOTED_A"] for r in rr),
                     "tx_cells_w5p": sum(r["tx_reached"]["W5P_PROMOTED_A"] for r in rr),
                     "tx_cells_w5p_oracle": sum(r["tx_reached"]["W5P_PROMOTED_ORACLE"] for r in rr),
                     "by_composition": {"%s/%s" % k: v for k, v in Counter(
                         (r["seed"], r["src"], r["verdict_expansion"], r["verdict_w5p"]) for r in rr).items()}
                     if False else dict(Counter("%s/%s exp=%s w5p=%s" % (r["seed"], r["src"], r["verdict_expansion"],
                                                                         r["verdict_w5p"]) for r in rr))}
    (pdir / "W9H_W5P_CERT_SUMMARY.json").write_text(json.dumps(summ, indent=1, sort_keys=True))
    print(json.dumps(summ, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 2)
