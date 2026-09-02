"""V1-C prospective gap slates (charter s10-s11, prereg section C).

Generates three 5-cell slates on mechanism x substrate_class from the current
snapshot: marginal-top, uniform-random (seed 7), frequency-weighted random
(seed 8). All 15 are registered as MISSING_CELL hypotheses with method
'v1c_sealed' so downstream agents cannot preferentially pick the marginal
ones; the true slate mapping is written to derived/ (gitignored) and only its
sha256 is committed. Cells whose method was already exposed by the V0-era
registrations are excluded from every slate (blinding burned).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import compiler, db, store  # noqa: E402


def main():
    conn = db.connect()
    snap = compiler.compile(conn, "evidence_v1", {})
    con = compiler.contract(conn, snap["snapshot_id"],
                            ["agent", "evidence_type", "outcome"],
                            ["mechanism", "substrate_class"])
    observed = {(c["cell"]["mechanism"], c["cell"]["substrate_class"]): c["value"]
                for c in con["cells"]}
    mech_tot, sub_tot = {}, {}
    for (m, s), v in observed.items():
        mech_tot[m] = mech_tot.get(m, 0) + v
        sub_tot[s] = sub_tot.get(s, 0) + v

    with db.dict_cur(conn) as cur:
        cur.execute("SELECT coords FROM ew.hypotheses WHERE kind='MISSING_CELL' "
                    "AND method <> 'v1c_sealed'")
        burned = {(json.loads(r["coords"]) if isinstance(r["coords"], str)
                   else r["coords"]) and
                  (r["coords"]["mechanism"] if isinstance(r["coords"], dict)
                   else json.loads(r["coords"])["mechanism"],
                  (r["coords"]["substrate_class"] if isinstance(r["coords"], dict)
                   else json.loads(r["coords"])["substrate_class"]))
                  for r in cur.fetchall() if r["coords"]}

    unobs = [(m, s) for m in mech_tot for s in sub_tot
             if (m, s) not in observed and (m, s) not in burned]
    weights = {c: mech_tot[c[0]] * sub_tot[c[1]] for c in unobs}

    marginal = sorted(unobs, key=lambda c: -weights[c])[:5]
    rest = [c for c in unobs if c not in marginal]
    rng7 = np.random.default_rng(7)
    uniform = [rest[i] for i in rng7.choice(len(rest), 5, replace=False)]
    rest2 = [c for c in rest if c not in uniform]
    w = np.array([weights[c] for c in rest2], dtype=float)
    rng8 = np.random.default_rng(8)
    freqw = [rest2[i] for i in rng8.choice(len(rest2), 5, replace=False,
                                           p=w / w.sum())]

    sealed, public = [], []
    for method, slate in (("marginal", marginal), ("uniform_random", uniform),
                          ("freq_weighted_random", freqw)):
        for m, s in slate:
            coords = {"mechanism": m, "substrate_class": s}
            hid = store.record_hypothesis(
                conn, "MISSING_CELL",
                f"V1-C prospective gap candidate: mechanism={m} on "
                f"substrate_class={s} has no evidence row despite both terms "
                f"being observed elsewhere",
                "v1c_sealed", "Mnemosyne", "M1", view_name="evidence_v1",
                coords=coords, score=float(weights[(m, s)]),
                basis={"snapshot": snap["snapshot_id"],
                       "mechanism_marginal": mech_tot[m],
                       "substrate_marginal": sub_tot[s]})
            sealed.append({"hypothesis_id": hid, "true_method": method,
                           "coords": coords, "weight": weights[(m, s)]})
            public.append({"hypothesis_id": hid, "coords": coords,
                           "score": weights[(m, s)]})

    sealed_path = HERE / "derived" / "v1c_sealed_methods.json"
    sealed_blob = json.dumps(sealed, indent=1, sort_keys=True)
    sealed_path.write_text(sealed_blob, encoding="utf-8")
    out = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "snapshot_id": snap["snapshot_id"],
        "view": "mechanism x substrate_class (evidence_v1)",
        "n_unobserved_cells_eligible": len(unobs),
        "n_burned_cells_excluded": len(burned),
        "slate_size_per_method": 5,
        "methods_sealed_until_adjudication": ["marginal", "uniform_random",
                                              "freq_weighted_random"],
        "sealed_mapping_sha256": hashlib.sha256(sealed_blob.encode()).hexdigest(),
        "slate_public": public,
        "adjudication": "PENDING_PROSPECTIVE (60-day window per prereg C)",
    }
    (HERE / "benchmarks" / "gap_prospective_v1.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "slate_public"},
                     indent=1))
    print("slate cells:", len(public))
    conn.close()


if __name__ == "__main__":
    main()
